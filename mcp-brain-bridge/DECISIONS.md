# Architectural Decisions: mcp-brain-bridge

## [2026-10-06] ADR-001: Initial Slice Baseline

- **Context:** Baseline documentation initialized via init-folder-docs.
- **Decision:** Adopting Living Folder Docs standard for this component.
- **Consequences:** All future structural or contract changes must be recorded here.
- **Rollback:** N/A (baseline adoption).

## [2026-10-12] ADR-002: Dual-mode XML extraction (bare + fenced fallback)

- **Context:** Manual copy-paste mode needs forced ```xml fences; automatic MCP mode needs bare XML. The strict fence reject forced a wasted re-emit turn.
- **Decision:** Bare unfenced blocks extract first; explicit ```xml fences extract second; other fences stay documentation-only; bare unclosed tails still strict-reject.
- **Consequences:** Both modes extract without re-emit; fence-fallback tests pin extraction.
- **Rollback:** Revert extract_xml_blocks fallback hunk and fence tests to strict-reject form.

## [2026-10-12] ADR-003: Pre-send token budget guard

- **Context:** A 943718-token output reservation plus ~106K input tokens exceeded the 1048576-token provider window as a hard 400 with no retry.
- **Decision:** Estimate input as chars divided by four, add live reserved output, compare against window minus margin; trim oldest history, then diffs and context, then bundle; persistent over-budget returns a BRAIN_BUDGET_OVER REPORT hint and skips the provider.
- **Consequences:** Oversize turns fail gracefully with numbers; 128K and 256K caps with xhigh keep working inside the window.
- **Rollback:** Revert the guard hunk plus hint helper plus eight tests.

## [2026-10-21] ADR-004: Responses API best-practice alignment

- **Context:** The 2026-10-21 audit found ten drifts from current official Responses practice in the single provider call site: no `store`, dropped reasoning items and `phase`, no `truncation`, no cache key, unread response `model`, retried billing 429s, raw-exception fatal 4xx, an effort ladder that could raise effort, silent token-cap fallback, and a role-form system prompt.
- **Decision:** Fix all ten behind per-parameter env switches defaulting to off (all six new wire parameters probed HTTP 200 against the live gateway first); validate effort against the official vocabulary; parse `error.code`/`error.type` with terminal billing codes; read `response.model`/`cached_tokens` into diagnostics; replay reasoning items and `phase` from version-tolerant transcripts; return structured REPORTs on fatal transport errors; fail loud on malformed numeric config.
- **Consequences:** Default wire bytes are unchanged until operators opt in; diagnostics expose model substitution and cache hits; transcripts stay backward compatible.
- **Rollback:** One-function revert of the request builder plus switch-off; diagnostics parser is pure and separately testable.

## [2026-10-22] ADR-005: Strip volatile `status` from replayed provider items

- **Context:** After switching `BRAIN_MODEL` to `gpt-6-luna`, every turn with replayed history failed 400 with `Unknown parameter: 'input[N].status'`. Upstream attaches `status` (e.g. `"completed"`) to reasoning output items; the bridge stored and replayed them verbatim (ADR-004/F2). `muse-spark-1.3-contributor` silently accepts the key, so this only surfaced on the stricter Luna endpoint.
- **Decision:** Sanitize replayed `provider_items` at send time (`_sanitize_replay_item` drops the `status` key, keeps `id`/`type`/`encrypted_content`/`summary`/`content` intact). Send-time, not capture-time, so transcripts already on disk are fixed without migration; capture stays verbatim for audit. Proven live: a real provider-issued reasoning blob replayed with `status` attached now returns `completed` instead of 400.
- **Consequences:** Strict providers accept history replays; lenient ones are unaffected (key was ignored anyway). Two regression tests pin the strip and the byte-identical fast path.
- **Rollback:** Revert the sanitizer call in `_build_request_body` plus the two tests; old transcripts keep working (they replayed verbatim before).

## [2026-10-22] ADR-006: Drop replayed items with over-long ids

- **Context:** After ADR-005, `gpt-6-luna` turns with history failed a new way: `Invalid 'input[N].id': string too long` (length 67, cap 64). The platform itself mints reasoning ids longer than its own input cap (`rs_` + 64 hex); Muse ignores it, Luna 400s. An OpenAI community thread ("input item ID exceeds 64 characters", Oct 2026) confirms the platform generates over-limit ids and that the supported recovery is to not replay the offending item.
- **Decision:** `_sanitize_replay_item` returns None for items whose string `id` exceeds 64 chars; the send loop skips them. The skip diagnostic records only the id length and the cap — never the id, type, or any other item field. Never truncate: the id is bound to `encrypted_content` and editing it breaks decryption. Dropping only loses encrypted-context continuity for that turn.
- **Consequences:** Strict providers accept history replays regardless of id length. The skip applies on the send path for every provider (lenient ones simply never needed it — they ignored the over-long id instead of 400ing). Three regression tests pin the drop, the at-cap pass-through, and the redacted diagnostic. The skip diagnostic records only the id length and the cap, never item fields.
- **Rollback:** Revert the length check plus the two tests; old transcripts keep working on lenient models.

## [2026-10-24] ADR-008: Fenced XML extraction rescues nested code fences

- **Context:** In manual mode the Hands tells the Brain "xml-fenced blocks expected" and the Brain complies: it wraps a `hands_implementation_task` in ` ```xml `. That body legitimately contains fenced code samples of its own (` ```python ` inside `<execution_phase>`). `_XML_FENCE_RE` cannot nest, so the body was closed at the first inner fence, `_extract_unclosed_tail` saw the truncated opener, and the turn was rejected as `XML_STRICT_REJECT_FENCE_FALLBACK`. The bridge then replaced the answer with the reject header plus the first 2000 chars, withholding the remaining ~25k chars, and the Hands had to re-prompt for a full re-emit — one wasted turn and ~10k output tokens per occurrence. Reproduced offline: a fenced block with one inner ` ```python ` yields zero blocks.
- **Decision:** Extraction walks line-anchored ` ```xml ` openers in document order (`_XML_FENCE_OPEN_RE`, anchored and info-string-checked so ````quad```` and non-xml fences stay out). For each opener it first tries the existing non-nesting fence body; when that body holds no complete allowlisted block, it scans forward from the opener — bounded by the next opener — for the block's closing tag. The rescue only runs where the old code raised, and a genuinely truncated block still finds nothing and still raises `XML_STRICT_REJECT_FENCE_FALLBACK`.
- **Consequences:** Nested fences no longer cost a turn, and multi-fence answers stay ordered and bounded per opener. The strict gate keeps its guarantee: input is still never repaired — an incomplete block is rejected, not closed. Trade-off: inside a fence whose body was truncated, a later allowlisted block before the next opener would also be extracted, which is acceptable because that path previously produced no output at all. Pinned by `test_extract_xml_fenced_hands_block_with_inner_code_fences`, `test_extract_rescued_fences_stay_ordered_and_bounded`, and `test_extract_truncated_xml_fence_still_rejects`.
- **Follow-up (same day), the mirror-image defect:** the bare-block scan ran on `_strip_fences` output, whose non-nesting strip mis-slices the same nested body. The leftover fragment reads as bare prose, so an operator-shaped literal parked in a documentation sample (`sample = "<hotfix>not real</hotfix>"` inside a ` ```python ` block) was returned as a live instruction while the real block was dropped — a false positive, worse than the false negative above. The bare scan now runs on `_mask_fenced_code`, a line-accurate CommonMark-style mask (opener with info string through the next bare run of the same character and length). `_strip_fences` is still called for its diagnostics only. Pinned by `test_extract_ignores_operator_tag_in_nested_fence_sample`.
- **Fence recognition is now line based, not regex:** `_xml_fence_segments` walks lines and closes a fence only on a bare run of the same character at least as long as the opener. That makes a four-backtick ````xml fence work as the canonical wrapper for a body carrying three-backtick samples, so the safe shape the prompts now recommend is actually extracted, and a three-backtick body that closes early is repaired by the rescue scan. The rescue and the fence-body pass both use `_extract_complete_blocks`, which anchors openers at line starts so a literal inside a code sample cannot win. Supersedes the old `test_extract_quad_xml_fence_stays_ignored` pin (quad fences with the `xml` info string now extract; a quad fence without it stays documentation).
- **Rollback:** Restore the single `_XML_FENCE_RE.finditer` loop in `extract_xml_blocks` and drop the three tests; fenced answers with inner code fences go back to costing a re-emit.

## [2026-10-22] ADR-007: Provider deadline tunable above the proxy hop

- **Context:** Big `xhigh`/`max` turns died as `provider overall deadline hit (500.0s) ... RemoteProtocolError: Server disconnected without sending a response`. Three stacked ceilings existed; the tightest won: zen-proxy `urlopen(timeout=300)`, bridge `_OVERALL_DEADLINE_S = 500`, httpx read timeout 600, MCP client 600s. A deep `gpt-6-luna` turn spends 14-19K reasoning tokens, i.e. 5-10 minutes.
- **Decision:** `_OVERALL_DEADLINE_S` becomes `BRAIN_OVERALL_DEADLINE_S` (default 900s, fail-loud on malformed), and the proxy hop becomes `ZEN_PROXY_UPSTREAM_TIMEOUT` (default 900s). Ordering contract: httpx read ≤ bridge overall ≤ MCP client execution, with the proxy at or below the bridge overall so its disconnects surface as retryable rather than as a deadline.
- **Consequences:** Long reasoning turns complete; a truly hung provider now surfaces later (bounded by the client timeout). The existing test that forced the deadline was updated to patch the new default constant.
- **Rollback:** Unset both env vars to restore code defaults, or set them to 500/300 explicitly for the old behavior.

## [2026-10-27] ADR-009: Server Prose Stays Runtime-Neutral

- **Context:** A code comment named a vendor trio as the transcript-persistence pattern, and the `brain_turn` docstring used `["question"]` as its `required_tools` example although no `tools.question` Code Mode path exists.
- **Decision:** The comment names OpenCode and other agentic clients; the example names `default.question`, the session tool that actually gates the turn.
- **Consequences:** Server prose no longer teaches tool names the catalog cannot resolve. Comment-only change; no wire behavior touched.
- **Rollback:** Restore the two lines from git history.
