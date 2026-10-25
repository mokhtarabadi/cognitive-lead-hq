# Task 329: Responses API Best-Practice Alignment (Brain Bridge)

**File:** `tasks/completed/329-responses-api-best-practices-alignment.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Source Context

### Variant C: Manager (`**Source:** manager`)

## Goal

Align the Brain Bridge provider client with current official OpenAI Responses API practice, closing the ten findings of the 2026-10-21 audit without changing the Brain/Hands protocol contract.

## Manager's Notes

- The Manager asked for a research + audit pass against the official OpenAI Responses API documentation and samples, and for every finding to be recorded now so the implementation could happen later.
- SUPERSEDED 2026-10-21: the Manager ordered full-automatic implementation ("now full automatic complete 329 task base on what you learned"). This task is now the implementation task; the record above is its specification.
- The audit found no correctness bug in the current call path. Every finding is either a drift from current official practice, a robustness gap, or a cost/visibility gap.

## Audit Scope & Sources

**Official sources consulted (2026-10-21):**

| Source | URL |
| ------ | --- |
| Responses create reference (body parameters) | `https://developers.openai.com/api/reference/resources/responses/methods/create.md` |
| Conversation state guide | `https://developers.openai.com/api/docs/guides/conversation-state` |
| Reasoning guide (effort, `context`, `phase`, incomplete handling) | `https://developers.openai.com/api/docs/guides/reasoning` |
| Text inputs and outputs guide (`instructions` vs roles) | `https://developers.openai.com/api/docs/guides/text` |
| Prompt caching guide | `https://developers.openai.com/api/docs/guides/prompt-caching` |
| Error codes guide | `https://developers.openai.com/api/docs/guides/error-codes` |
| Your data guide (storage, ZDR) | `https://developers.openai.com/api/docs/guides/your-data` |
| Streaming guide | `https://developers.openai.com/api/docs/guides/streaming-responses` |
| Cookbook: per-run spending controller | `https://developers.openai.com/cookbook/articles/per_run_spending_controller_responses_api` |
| Cookbook index | `https://developers.openai.com/cookbook/llms.txt` |
| `openai-python` SDK 2.54.0 (vendored in `mcp-brain-bridge/.venv`) | `ResponseCreateParams` is generated from the OpenAPI spec, so it is the authoritative parameter list |

**Code audited:** `mcp-brain-bridge/server.py` (3878 lines) plus `capability.py`, `session_ledger.py`, `loop_guard.py`, `preflight.py` (stdlib only, no provider calls). A repo-wide sweep found exactly **one** provider call site — `mcp-brain-bridge/server.py:1536`. No other server, script, or tool in this repository calls a model.

**Live configuration at audit time (from the gitignored `.env`):**

```
BRAIN_API_BASE=http://127.0.0.1:8081/go/resp   # local gateway, loopback http
BRAIN_MODEL=muse-spark-1.3-contributor         # same id for LOW and HIGH tiers
BRAIN_REASONING_EFFORT=xhigh
BRAIN_MAX_TOKENS=131072
BRAIN_CONTEXT_WINDOW_TOKENS=1048576
```

**Audit caveat (binding for the implementation):** the peer is a local gateway on `127.0.0.1:8081`, not `api.openai.com`. The OpenAI docs are the reference contract, but every change below needs a probe against that gateway first, or it can fail with an unsupported-parameter 400. The gateway was **not** called during this audit.

## Findings

### F1 — `store` is never sent, so responses are stored provider-side by default

- **Official:** "Responses are stored by default. Chat completions are stored by default for new accounts. To disable storage when using either API, set `store: false`." (migrate-to-responses). SDK: `store` — "Whether to store the generated model response for later retrieval via API." Zero Data Retention "changes some endpoint behavior: the `store` parameter for `/v1/responses` and `v1/chat/completions` will always be treated as `false`".
- **Our code:** the request body is built at `mcp-brain-bridge/server.py:3195-3203` and contains only `model`, `input`, `reasoning`, `max_output_tokens` (plus `temperature` when explicitly set). `store` never appears.
- **Impact:** every Brain turn — system prompt, task file, diffs, repo context — is retained by the provider for later retrieval. The default retention window for application state is 30 days.
- **Proposed fix:** send `store: false`. If reasoning continuity is wanted later, pair it with `include: ["reasoning.encrypted_content"]`, which the create reference documents as the stateless path: "Includes an encrypted version of reasoning tokens in reasoning item outputs. This enables reasoning items to be used in multi-turn conversations when using the Responses API statelessly (like when the `store` parameter is set to `false`...)".
- **Risk:** behavioral change at the provider. Must be confirmed with the Manager (retention of proprietary repo content) and probed against the gateway.

### F2 — Reasoning items and assistant `phase` are dropped on every turn

- **Official:** "For stateless reasoning-model requests, preserve every item in the response's `output` array. The Responses API returns encrypted reasoning items by default. Replaying the complete output keeps reasoning items and assistant `phase` values intact." On the message item: `phase` — "For models like `gpt-5.3-codex` and beyond, when sending follow-up requests, preserve and resend `phase` on all assistant messages — dropping it can degrade performance." And the conversation-state guide: "When troubleshooting cases where GPT-5.5 treats an intermediate update as the final answer, verify your integration preserves the assistant message `phase` field correctly."
- **Our code:** `server.py:3192-3194` rebuilds the payload as `{"role", "content"}` pairs with string content; the transcript parser keeps only `user`/`assistant` roles (`server.py:1956-1961`); the session transcript stores text (`append_turn`, `server.py:3415-3432`).
- **Impact:** (a) reasoning continuity is lost every turn, so reasoning models re-derive context and spend reasoning tokens again; (b) an assistant message that carried `phase: commentary` or `phase: final_answer` loses it, which is the documented cause for a model treating an intermediate update as the final answer — directly relevant to a protocol where the Brain must emit XML blocks.
- **Proposed fix:** persist the provider's `output[]` items (or at minimum the reasoning items plus `phase`) in the session transcript and replay them as input items. Requires a transcript-format change and a `store: false` + `include` decision from F1.

### F3 — No `truncation`, no `context_management`, and the overflow guard is a `chars // 4` estimate

- **Official:** `truncation` — "`auto`: If the input to this Response exceeds the model's context window size, the model will truncate the response to fit the context window by dropping items from the beginning of the conversation." / "`disabled` (default): If the input size will exceed the context window size for a model, the request will fail with a 400 error." `create.md` also documents `context_management` — "Context management configuration for this request", `type: "compaction"`, `compact_threshold` (token threshold at which compaction should be triggered).
- **Our code:** the pre-send guard estimates tokens as `chars // 4` (`server.py:1397-1403`) against a declared window of 1,048,576 tokens (`server.py:1393`, `BRAIN_CONTEXT_WINDOW_TOKENS`), then trims oldest history, then drops diffs, then drops the bundle, and finally skips the provider entirely (`server.py:3091-3146`, `3239-3252`). `truncation` is never sent, so the provider default `disabled` applies — an overflow that the estimate missed is a hard 400.
- **Impact:** the estimate is a heuristic on a 1M-token window; a 25% error is 250k tokens of real overflow. The API now offers two mechanisms the code does not use: server-side truncation and server-side compaction.
- **Proposed fix:** send `truncation: "auto"`; consider `context_management` compaction for long Brain sessions; and calibrate the chars-to-tokens ratio from data we already receive — `usage.input_tokens` comes back on every turn, so the estimate can be measured instead of guessed. The official Cookbook uses the token-count endpoint (`client.responses.input_tokens.count`) for exactly this; the gateway may not expose it, so the measured-ratio route is the fallback.

### F4 — `prompt_cache_key` is never sent although a cache-split descriptor is computed and deliberately kept off the wire

- **Official:** SDK `prompt_cache_key` — "Used by OpenAI to cache responses for similar requests to optimize your cache hit rates. Replaces the `user` field." The SDK also exposes `prompt_cache_options` ("Supported for `gpt-5.6` and later models… You can add explicit breakpoints to content blocks with `prompt_cache_breakpoint`. Each request can write up to four breakpoints.").
- **Our code:** `build_prompt_cache_split` (`server.py:1334-1372`) computes a split descriptor, and `server.py:3155-3156` states it is sidecar-only: "the split descriptor never touches wire bytes — effective_prompt, chat payload, and prompt_hash stay identical."
- **Impact:** the system prompt is large and byte-identical across turns, which is the ideal prompt-cache prefix, and we never ask for it. Separately, `usage.input_tokens_details.cached_tokens` is never read, so the hit rate is invisible — the cache cannot be verified even if the gateway caches on its own.
- **Proposed fix:** send a stable `prompt_cache_key` derived from the prompt hash that already exists, and surface `usage.input_tokens_details.cached_tokens` in the diagnostics block so the effect is measurable.

### F5 — The response's `model` is never read, so a silent model substitution is invisible

- **Official:** Cookbook, per-run spending controller: "Use a fixed model ID that the API returns unchanged in `response.model`", and the sample raises `UncertainCharge` when `response.model != rates.model` (and likewise for `service_tier`). The create reference documents `service_tier` as: "When the `service_tier` parameter is set, the response body will include the `service_tier` value based on the processing mode actually used to serve the request. This response value may be different from the value set in the parameter."
- **Our code:** the diagnostics parser reads only `status`, `incomplete_details.reason`, `usage`, top-level `error`, and `output` (`server.py:3625-3661`). `data.get("model")` and `data.get("id")` are never read from a provider payload (the only `model` read at `server.py:1986` is a transcript record, not the provider response).
- **Impact:** this bridge points at a routing gateway. If the gateway answers with a different model than requested — a fallback, a tier downgrade, an alias resolving elsewhere — nothing in the turn records it. The tier routing (`BRAIN_MODEL_LOW` / `_HIGH`, `server.py:1129-1254`) is built on the assumption that the requested id is the served id.
- **Proposed fix:** read `response.model` into `debug.provider` and compare it with the requested model; treat a mismatch as a visible warning (or a hard failure, depending on the Manager's decision).

### F6 — Every 429 is retried, and `error.code` is never parsed

- **Official:** error-codes guide — 429 `credit_balance_exhausted` ("Your organization has no prepaid credits remaining"), `organization_spend_limit_exceeded`, `project_spend_limit_exceeded`, `organization_usage_limit_exceeded`, and "Retrying billing, spend, or quota errors won't restore API access. Update the relevant credits or limits before sending another request." Billing detail is in `error.code`, not only `error.type`.
- **Our code:** `_RETRYABLE_STATUS = {429, 500, 502, 503, 504}` (`server.py:1439`) retries 429 unconditionally; the diagnostics parser reads `error` as string or `error.message` only (`server.py:3644-3659`) and never `error.code` or `error.type`.
- **Impact:** a spend-limit or credit-exhaustion 429 is retried three times with backoff (up to the 500 s overall deadline) before failing, and the final hint does not say "add credits" or "raise the limit" — the failure mode the official guide warns about.
- **Proposed fix:** parse `error.code` / `error.type`; classify billing, spend, and quota codes as terminal (no retry) with a specific hint, per the official guide.

### F7 — A fatal 4xx escapes `brain_turn` as a raw exception instead of a structured REPORT

- **Official:** the error table gives each fatal status a distinct remedy — 400 invalid `service_tier`, 401 invalid authentication / incorrect key / not an organization member / IP not authorized, 403 country not supported, 404, 422.
- **Our code:** `server.py:1548-1553` raises a `RuntimeError` for any 4xx; `brain_turn` (`server.py:2669-3460`) has no try/except around the transport call, so the exception propagates out of the MCP tool. The 500-char body snippet does reach the caller, so the failure is diagnosable, but it bypasses the bridge's own contract of a `REPORT` plus `debug.provider` (the shape mandated by the provider-diagnostics memory rule).
- **Impact:** the Hands sees a tool exception instead of a structured verdict with provider diagnostics, and the per-task provider-diagnostics rule ("MUST parse and log the provider diagnostics on every turn") is not satisfied for fatal 4xx turns.
- **Proposed fix:** catch the transport failure inside the turn and return a REPORT carrying `debug.provider` plus the provider error, keeping the exception path for genuine bugs.

### F8 — The reasoning-effort ladder omits `minimal`, the unknown-value fallback raises effort, and the vocabulary is not validated

- **Official:** supported values are "model-dependent and can include `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, and `max`"; "GPT-6 Astra does not support `none` reasoning effort. Setting `reasoning.effort` (Responses) or `reasoning_effort` (Chat Completions) to `none` returns HTTP 400. GPT-6.1 Sol does not support `none` or `minimal` and defaults to `medium`." SDK `ReasoningEffort` = `none | minimal | low | medium | high | xhigh | max`.
- **Our code:** `_get_reasoning_effort` validates only a character class (`server.py:3479-3482`, regex `[\w.-]{1,64}`), so any well-formed word reaches the provider. The step-down ladder is `{"max": "xhigh", "xhigh": "high", "high": "medium", "medium": "low", "low": "low"}` (`server.py:3778-3784`) and the fallback for an unknown value is `"medium"` (`server.py:3787-3793`).
- **Impact:** with `BRAIN_REASONING_EFFORT=minimal`, a truncation recovery raises effort to `medium` — the opposite of its purpose, and it spends more of the same `max_output_tokens` on reasoning. `none` and `minimal` are absent from the ladder entirely, and an unsupported effort value is a 400 that currently escapes as an uncaught exception (F7).
- **Proposed fix:** validate against the official vocabulary (per-model where known), add `minimal` to the ladder, and make the unknown-value fallback step down to `low` or keep the current effort rather than jumping to `medium`.

### F9 — Configuration hygiene: silent fallback, dead constant, vestigial function, stale bytecode, and a CHANGELOG claim the code no longer supports

- **Our code and the official baseline:**
  - `_get_max_tokens` (`server.py:1383-1386`) silently falls back to `32768` on a non-numeric `BRAIN_MAX_TOKENS` and passes a negative value through, while every other env reader in the file fails loud (`BRAIN_HTTP_READ_TIMEOUT`, `BRAIN_REASONING_EFFORT`). A malformed value silently changes the output budget and the reasoning-budget warning threshold.
  - `_FATAL_STATUS = {400, 401, 403, 404, 422}` (`server.py:1443`) is defined and never referenced; the 4xx branch is range-based (`server.py:1548`).
  - `_send_with_learning` (`server.py:1644-1662`) keeps a name and four keyword arguments (`task_key`, `task_id`, `session_id`, `project_root`) that its body never uses; its own docstring says "No correction memory and no escalation". There is **no** `unsupported_parameter` correction path in the code — the only mention of that string is a comment at `server.py:3198-3200`. The CHANGELOG entry for the transport-learning bundle still describes a "correction memory keyed by task_id persisted as ledger events", which no longer exists in the tree.
  - `mcp-brain-bridge/__pycache__/` holds stale bytecode for eight deleted modules (`transport.py`, `transport_learning.py`, `diagnostics.py`, `history.py`, `saga.py`, `golden_replay.py`, `authority_retrieval.py`, `eval_harness.py`) with no `.py` source.
- **Impact:** no runtime defect, but the code, the CHANGELOG, and the memory narrative disagree, which makes future audits harder and hides that a previously shipped feature (unsupported-parameter self-correction) is gone.
- **Proposed fix:** fail loud on a malformed `BRAIN_MAX_TOKENS`; delete `_FATAL_STATUS`; rename or delete `_send_with_learning`; remove the stale `__pycache__`; correct the CHANGELOG wording.

### F10 — The system prompt is a `role: "system"` item instead of the top-level `instructions` field

- **Official:** `instructions` — "A system (or developer) message inserted into the model's context." The text guide: "The `instructions` parameter gives the model high-level instructions on how it should behave while generating a response… Any instructions provided this way will take priority over a prompt in the `input` parameter." The create reference states that instructions given with the `developer` or `system` role take precedence over `user` role instructions.
- **Our code:** `server.py:3192` builds `chat = [{"role": "system", "content": system_prompt}]` and appends it to the same `input` array as the turn messages.
- **Impact:** functionally valid, but the canonical Responses shape is `instructions`, and it sits higher in the instruction hierarchy than a role inside `input`. Low risk to change; gateway-dependent.
- **Proposed fix:** move the system prompt to the top-level `instructions` field, keeping the role form as a fallback if the gateway rejects it.

## Verified As Correct (no action)

| Behavior | Code | Official baseline |
| -------- | ---- | ----------------- |
| Walks all of `output[]`, both `type == "message"` → `content[]` → `type == "output_text"` and bare `output_text` | `server.py:3850-3869` | "The `output` array often has more than one item in it! … It is not safe to assume that the model's text output is present at `output[0].content[0].text`." |
| Triage order: provider `error` → `refusal` → `status=incomplete` / `reason=max_output_tokens` → generic flake, and the budget case is explicitly not a flake | `server.py:3336-3355`, `3735-3760` | "If the generated tokens reach the context window limit or the `max_output_tokens` value you've set, you'll receive a response with a `status` of `incomplete` and `incomplete_details` with `reason` set to `max_output_tokens`." |
| `reasoning.effort` nested under `reasoning`, never flat | `server.py:3198-3203` | The Responses shape is `reasoning: {effort}`; the flat form is rejected by strict providers. |
| `temperature` and `reasoning` are mutually exclusive — setting one deletes the other | `server.py:3204-3217` | Reasoning models reject sampling overrides alongside reasoning effort. |
| `Retry-After` honored (capped at 120 s), exponential backoff with jitter, 500 s overall deadline, 4xx fail fast, network errors retried | `server.py:1509-1577` | 429 guidance: "follow the `Retry-After` header when it's present"; 503: "Follow the `Retry-After` header when it's present, then retry your request." |
| Provider diagnostics parsed and logged on every turn, parsers pure and non-raising | `server.py:3601-3714` | The repo's own provider-diagnostics memory rule (Task 259). |
| API key never enters error strings; https enforced except loopback; empty key fails closed | `server.py:1424-1430`, `1598-1614`, `1515-1516` | Standard key-safety practice. |
| Pre-send budget guard, transcript bounding (40 turns, compaction at 30 messages / 200 KB, 1 M char ceiling) | `server.py:3091-3146`, `1915-1921` | No official requirement; sound engineering, kept. |

## Proposed Implementation Scopes

Sequencing matters: each scope is independently shippable, and the gateway probe in front of it is mandatory.

- **D1 — Safe alignment, no protocol change (F1, F4, F5, F6, F8, F9).** Request-shape and observability work: `store: false`, `prompt_cache_key`, `cached_tokens` in diagnostics, `response.model` verification, `error.code` parsing with terminal billing/spend codes, effort-vocabulary validation plus a corrected step-down ladder, and the configuration hygiene fixes. Every item is unit-testable offline; the only live dependency is the gateway probe.
- **D2 — Continuity and context (F2, F3, F10).** Transcript format change to carry provider output items (reasoning items and `phase`), `truncation: "auto"`, measured or endpoint-based token counting, and moving the system prompt to `instructions`. Larger surface: it touches the session ledger, the transcript format, and the request body, so it needs its own design pass before implementation.
- **D3 — Record only (no behavior change).** Keep this audit as the sole artifact, correct the CHANGELOG claims (F9), and store the findings in project memory so future sessions see them.

**Gateway probe checklist (run before any scope):** one small request against `http://127.0.0.1:8081/go/resp` per parameter — `store: false`, `prompt_cache_key`, `truncation: "auto"`, `include: ["reasoning.encrypted_content"]`, `instructions`, `context_management` — and read back which ones the gateway accepts, whether the response echoes `model` and `service_tier`, and whether `usage.input_tokens_details.cached_tokens` is populated. The gateway was not called during the audit, so every parameter claim above is "documented by OpenAI", not "verified against the live peer".

## Local TODOs

- [x] Gateway probe: record which Responses parameters the local gateway accepts and what it echoes back
- [x] D1 — F1 `store: false`; F4 `prompt_cache_key` plus `cached_tokens` in diagnostics; F5 `response.model` verification; F6 `error.code` parsing with terminal billing/spend codes; F8 effort vocabulary validation and corrected step-down ladder; F9 configuration hygiene and CHANGELOG correction
- [x] D2 — design pass, then implementation: F2 output-item replay with `phase` preserved; F3 `truncation: "auto"` and token-count calibration; F10 `instructions` field
- [x] D3 — project-memory shard for the audit (done at task creation, refresh if the findings change)
- [x] Unit tests for every changed parser, ladder, and request-body builder
- [x] Update `docs/brain-bridge.md` with the new request shape, env vars, and diagnostics fields
- [x] Verify the full suite stays green and re-run the provider-diagnostics memory rule against the new code

## Acceptance Criteria

- [x] Every one of the ten findings is either implemented or explicitly deferred with a recorded reason, in this task file
- [x] The request body matches the official Responses shape for every parameter it sends, and every new parameter is confirmed against the gateway
- [x] Provider diagnostics expose `response.model` and `usage.input_tokens_details.cached_tokens`
- [x] Billing, spend, and quota 429 codes are terminal with an actionable hint and are not retried
- [x] Reasoning-effort values are validated against the official vocabulary, and the step-down ladder never raises effort
- [x] A malformed `BRAIN_MAX_TOKENS` fails loud, and the dead constant, the vestigial function, and the stale bytecode are removed
- [x] The CHANGELOG corrects the record going forward: the Task 298 entry already states the stateless send path (`_send_with_learning` is a stateless retry with no correction memory) and this task's entry documents the rename to `_send_with_retry`; the older META 257 entry is preserved verbatim as history per the append-only convention
- [x] `docs/brain-bridge.md` documents the final request shape, env vars, and diagnostics fields
- [x] The test suite passes with no new failure, and the provider-diagnostics memory rule is satisfied for every turn including fatal 4xx

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-context-server --with pytest --with pyyaml python -m pytest tests/ -q
- **Expected result:** 555 passed; the only failure is the pre-existing `test_system_prompt_split_assemble_round_trip` (proven on unmodified HEAD: identical 85 missing `<night_mode>` lines)
- **Actual result:** 555 passed, 1 failed (`test_system_prompt_split_assemble_round_trip` only); new file `tests/test_brain_responses_alignment.py` 24 passed; all 7 tests updated for the new contracts pass
- **Exit code:** 1 (solely the pre-existing failure; every test touching this task's code exits 0)

> QA round 2 (hotfix): QA_REJECTED the first pass on 5 findings (DoD exit-0 over-claim, AC7 history wording, task number in a docs heading, effort case not normalized, fatal diag dropping the HTTP status). All five fixed: exit-0 box honestly unchecked with the recorded reason, AC7 reworded to history-preserved with forward correction, heading stripped of the number, effort normalized to lower, `provider_status_code` carried into `debug.provider` and the log line. Re-running QA below.

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0 — NOT satisfied as written: the suite exits 1 solely on the pre-existing `test_system_prompt_split_assemble_round_trip` (proven identical on unmodified HEAD, out of scope for this task). All 554 other tests pass, including every test touching this task's code. Kept unchecked deliberately; see the box-checking note below.
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> Box-checking note: the suite exits 1 solely on the pre-existing `test_system_prompt_split_assemble_round_trip` (proven identical on unmodified HEAD — the splitter drops `<night_mode>`, unrelated to this task); the exit-0 box above stays honestly unchecked for that reason. `lint_task_file` on this task file passes clean.

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** the peer is a local gateway, not OpenAI, so a parameter that the official docs list may be rejected by the gateway — and conversely a gateway quirk may make an official "fix" wrong here. Every parameter change therefore needs a probe first, and the probe results belong in this task file next to the finding. The second risk is scope: D2 changes the transcript format, which the session ledger and the transcript reader both depend on.
- **Rollback plan:** the request body is built in one place (`server.py:3195-3217`), so a body-shape change is a one-function revert; the diagnostics parser is pure and separately testable; the transcript format change in D2 must be versioned, so an unreadable transcript must fall back to the current text-only replay rather than failing the turn. Keep `store: false` and the effort-vocabulary validation behind their own env switches until the gateway probe confirms them, so each can be turned off without a code revert.

---

## Execution Log & Reasoning

**Gateway probe results (2026-10-21, recorded before any body change):** peer is `http://127.0.0.1:8081/go/resp/responses` (the `/responses` suffix is required — the bare base returns 404). All six rows returned HTTP 200, so every documented parameter is accepted and NO env switch needs to stay off for gateway reasons:

| Row | Param | Result |
| --- | ----- | ------ |
| P1 | `store: false` | 200 `completed`, model echoed `muse-spark-1.3-contributor` |
| P2 | `prompt_cache_key` | 200 `completed`; `usage.input_tokens_details.cached_tokens` present (0 on first-seen prefix) |
| P3 | `truncation: "auto"` | 200 accepted |
| P4 | `store: false` + `include: ["reasoning.encrypted_content"]` | 200 `completed` |
| P5 | top-level `instructions` (system prompt moved out of `input`) | 200 `completed`, instruction obeyed (input was `Go.`, answer `PROBE-OK`) |
| P6 | `context_management: [{type: compaction, compact_threshold}]` | 200 accepted |
| Echo | baseline + all rows | `response.model` echoed correctly, `service_tier` is `null` (gateway does not report a tier), reasoning items carry `encrypted_content` BY DEFAULT even without `include`, no `phase` fields on this model (replay code must tolerate absent `phase`) |

Switches still ship default-off per the rollback plan (behavior change is opt-in until the Manager enables it), but none are blocked by the gateway.

### Closure (2026-10-21)

Manager approval quote: "Approved for closure". File moved `tasks/qa/` → `tasks/completed/`, status set to closed, header synced. Committed via `custom_context_commit_and_clean_task` only.

### Autopilot QA + Review (2026-10-21, same session)

- **QA round 1: QA_REJECTED** on 5 findings (DoD exit-0 over-claim, AC7 history wording, task number in a docs heading, effort case not normalized, fatal diag dropping the HTTP status). All fair.
- **Hotfix:** exit-0 box honestly unchecked with the recorded pre-existing-failure reason; AC7 reworded to history-preserved with forward correction; heading stripped of the number; effort normalized to lower (`XHigh`→`xhigh` pinned); `provider_status_code` carried into `debug.provider` + log line `http_status` (400 pinned). Suite: 555 passed / 1 pre-existing.
- **QA round 2: QA_PASSED** — all five findings fixed, boxes honest, no scope widening.
- **Review: APPROVED (PO_REVIEW_PENDING)** — technical approval; 3 non-blocking nits (pre-existing `.env.example` model-mode block riding along per A2; task number in env comments/test docstring/memory prose — allowed homes; `_step_down_effort` returning original-cased unknown value — validated path never hits it). File stays in `tasks/qa/`; closure needs the exact phrase "Approved for closure" or "Close task".

### What this task is

**UPDATE 2026-10-21 — Manager ordered full-automatic implementation ("now full automatic complete 329 task base on what you learned").** The "record, not an implementation" note above is superseded for this task: Hands now implements all ten findings (D1 + D2), probes the gateway first, and runs the full pipeline through QA/review to closure.

**Autopilot LOCKED for this task** (Manager order 2026-10-21, "full automatic complete 329"). From that word the mode is LOCKED: Hands chains discovery, probe, Brain plan, plan approval, implementation, QA, review, stage, and qa-move directly, pausing only for hard blockers, the plan-approval gate, Relay questions, and the closure approval gate. The lock breaks only on "manual", "stop", or a new direct order.

A record, not an implementation. The Manager asked for the audit to be saved so the work can be done later. Every finding from the 2026-10-21 research pass is captured above with the official quote, the code citation, the impact, the proposed fix, and the gateway caveat. The ten findings are F1 through F10; nothing from the audit is dropped.

### What was implemented (2026-10-21, same session)

All in `mcp-brain-bridge/server.py` unless noted; every new wire parameter behind an env switch defaulting to off.

- **F1/F3/F4/F10 — one `_build_request_body` builder** replaces the inline body: base shape unchanged (`model`/`input`/`reasoning`/`max_output_tokens` + `temperature` handling moved in verbatim); opt-ins `BRAIN_SEND_STORE`, `BRAIN_SEND_INCLUDE_ENCRYPTED`, `BRAIN_SEND_CACHE_KEY` (stable `brain-<sha256>` from the system prompt), `BRAIN_SEND_TRUNCATION`, `BRAIN_SEND_CONTEXT_MANAGEMENT` (+`BRAIN_COMPACTION_THRESHOLD`), `BRAIN_USE_INSTRUCTIONS`.
- **F2 — continuity:** `append_turn` accepts `phase`/`response_id`/`provider_items`; `_parse_turns` carries them via `_META_KEYS`; the builder replays `provider_items` after their turn and `phase` on the assistant item; `_replayable_provider_items` extracts them (message text is not duplicated); fatal/budget paths yield empty continuity, never a crash. Old transcripts replay exactly as before.
- **F3 — estimator:** `_chars_per_token` (explicit `BRAIN_CHARS_PER_TOKEN` override, else calibrated ratio, else 4.0) + `_note_observed_ratio` updated from every successful turn's `usage.input_tokens`; `_estimate_input_tokens_from_chars` uses it (identical output when uncalibrated).
- **F5 — diagnostics** read `response_model`/`response_id`/`service_tier`/`cached_tokens`; `_model_substitution_note` warns on stderr on mismatch; `requested_model` recorded in `debug.provider`.
- **F6 — terminal 429s:** `_TERMINAL_429_CODES` + `_terminal_429_code` + `_error_code_from_body`; a terminal 429 raises at once with an add-credits/raise-limits hint; unknown codes keep current retry.
- **F7 — structured fatal:** the send+parse block in `brain_turn` catches `RuntimeError` and returns a REPORT with `debug.provider` (error + code); genuine non-RuntimeError bugs still propagate. `_transport_fail` carries `provider_status`/`provider_code`/`provider_type`.
- **F8 — effort:** `_EFFORT_VOCABULARY` validation; ladder extended with `minimal`, unknown strings keep current effort, missing values fall to `low`.
- **F9 — hygiene:** `_get_max_tokens` fails loud on malformed/negative; `_FATAL_STATUS` deleted; `_send_with_learning` renamed to `_send_with_retry` (caller updated); `mcp-brain-bridge/__pycache__` removed. CHANGELOG: the Task 298 entry already states the stateless path, so no history rewrite — recorded here instead.
- **Tests:** `tests/test_brain_responses_alignment.py` (23 tests: body matrix, diagnostics, terminal classifier, ladder, fail-loud, transcript replay, calibration, fatal-4xx REPORT); updated 5 pinned tests in `test_brain_bridge.py` (ladder, two diag key sets, debug provider set, usage set) and 1 in `test_session_lifecycle.py` (fatal 4xx now REPORT).
- **Deviations from the XML (recorded, none behavior-changing):** transcript versioning by key presence instead of a `v` flag (old records lack the keys and replay identically — same guarantee, less surface); one extra passing test added (`test_brain_turn_low_steps_down_to_minimal`) to pin the new ladder rung.
- **Stack skill skip:** root=. markers=[mcp-brain-bridge/pyproject.toml, server.py imports httpx stdlib only, no framework markers] matched=[] reason=no stack blueprint matches raw httpx provider client, stdlib discipline only.

### Assumptions

- **A1** — The Manager's "full automatic complete 329" supersedes the task's own "record, not an implementation" note: the audit section stays as the specification, and this log records the build. One-line reason: an explicit newer Manager order overrides stale task prose.
- **A2** — `.env.example` already carried uncommitted model-mode docs from earlier work; the new switch block was appended in the same file and stages with this task. One-line reason: the switch block belongs to this task's contract and the file is the canonical env reference.

### Decisions recorded with the findings

- **The official docs are the reference, the gateway is the peer.** OpenAI's parameter list and semantics are the yardstick, but the live endpoint is a local router, so the audit states what is documented and what is unverified separately, and makes the probe a prerequisite rather than an assumption.
- **Findings are recorded with their impact, not just their existence.** A gap that costs tokens (F4), leaks repo content (F1), or degrades model behavior (F2) has to survive until someone implements it, so each one carries the official sentence that proves it and the line number that shows our behavior.
- **The verified-correct table is part of the record.** An audit that only lists gaps invites a later implementer to "fix" behavior that already matches the official guidance, so the correct behaviors are pinned with their citations.
- **Scopes are separated by blast radius.** D1 is request-shape and observability work that is unit-testable offline; D2 changes the transcript format and the conversation model and deserves its own design pass; D3 is record-only. The Manager can pick a scope without inheriting the others.
- **No code was touched.** This task is the deliverable; the implementation lands in a follow-up task that starts from this file.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `c3c54e37e2658e2e8f6261a371ea09fac880e23f`
<!-- END_GIT_DIFF -->
