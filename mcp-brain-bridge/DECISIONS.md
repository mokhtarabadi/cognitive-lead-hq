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
