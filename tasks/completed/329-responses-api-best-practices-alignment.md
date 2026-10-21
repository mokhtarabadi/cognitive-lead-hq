# Task 329: Responses API Best-Practice Alignment (Brain Bridge)

**File:** `tasks/qa/329-responses-api-best-practices-alignment.md`
**Source:** manager
**Type:** improvement
**Status:** open

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
```diff
diff --git a/.env.example b/.env.example
index e5f0f91..7925a8a 100644
--- a/.env.example
+++ b/.env.example
@@ -15,11 +15,46 @@ BRAIN_API_KEY=sk-...
 # Brain Bridge (mcp-brain-bridge) — model + prompt source for `brain_turn`.
 # Brain model (Responses-API id). Blank = built-in default
 # (gpt-6-astra).
-#BRAIN_MODEL=gpt-6-astra
+#
+# RECOMMENDED MODES (verified 2026-10-21 against the live Go gateway
+# through zen-proxy 127.0.0.1:8081/go/resp; all below accept
+# reasoning.effort on /responses):
+#
+#   Default (balanced, current production setting):
+#     BRAIN_MODEL=gpt-6-luna
+#     BRAIN_MODEL_LOW=muse-spark-1.3-contributor
+#     BRAIN_MODEL_HIGH=gpt-6-luna
+#     BRAIN_REASONING_EFFORT=xhigh
+#   Max quality (hard planning/review only; ~10x fewer requests/month):
+#     BRAIN_MODEL_HIGH=gpt-6-luna with effort max
+#     (keep LOW on muse-spark-1.3-contributor so implement/qa/closure
+#     stay on the cheap 226k-requests/month tier).
+#   Economy (everything cheap; weaker planning, fine for routine turns):
+#     BRAIN_MODEL=muse-spark-1.3-contributor
+#     BRAIN_MODEL_LOW=muse-spark-1.3-contributor
+#     BRAIN_MODEL_HIGH=muse-spark-1.3-contributor
+#     BRAIN_REASONING_EFFORT=xhigh
+#
+# Per-model notes (all on the /go/resp route):
+# - gpt-6-luna: strongest reasoning (#24) on /go/resp, 1.05M ctx,
+#   verified xhigh+max OK. 30-day log retention, no training.
+#   Quota is the binding constraint: ~21k requests/month on Go $10.
+# - muse-spark-1.3-contributor: TB-2.1 88.8 / DeepSWE 75.4, 1M ctx,
+#   ~226k requests/month. CONTRIBUTOR tier: prompts train future Meta
+#   models and are region-restricted — do not point it at private code
+#   you would not share.
+# - glm-5.3 (#8 agentic, TB-2.1 88.2) and kimi-k3 (#10 agentic) are
+#   stronger planners but live on /go/chat only — unreachable for the
+#   brain until the proxy gains a chat-route client. Do NOT set them
+#   here; /responses is the only shape the bridge speaks.
+# - grok-4.7: forbidden for the brain — 500K window while
+#   BRAIN_CONTEXT_WINDOW_TOKENS assumes ~1M; the guard would let
+#   oversized prompts through and the server rejects them.
+#BRAIN_MODEL=gpt-6-luna
 # Reasoning effort sent as `reasoning.effort` (default medium, the Luna
 # model's own default). xhigh/max can claim roughly 95% of the token cap
 # on reasoning and starve the visible answer.
-#BRAIN_REASONING_EFFORT=medium
+#BRAIN_REASONING_EFFORT=xhigh
 # System prompt override (absolute path). Blank = global install copy
 # (~/.config/opencode/system-prompt.md).
 #BRAIN_SYSTEM_PROMPT=
@@ -38,6 +73,20 @@ BRAIN_API_KEY=sk-...
 # Malformed or non-positive values fail loud.
 #BRAIN_HTTP_READ_TIMEOUT=600
 
+# Responses request-shape opt-ins (Task 329; all default OFF, all probed
+# HTTP 200 against the live gateway 2026-10-21). Set to 1/true/yes/on to
+# enable. Default wire bytes stay identical to the pre-329 shape.
+#BRAIN_SEND_STORE=0
+#BRAIN_SEND_INCLUDE_ENCRYPTED=0
+#BRAIN_SEND_CACHE_KEY=0
+#BRAIN_SEND_TRUNCATION=0
+#BRAIN_SEND_CONTEXT_MANAGEMENT=0
+#BRAIN_USE_INSTRUCTIONS=0
+# Estimator/token overrides. Blank = calibrated from observed
+# usage.input_tokens, else 4.0. Malformed values fail loud.
+#BRAIN_CHARS_PER_TOKEN=
+#BRAIN_COMPACTION_THRESHOLD=100000
+
 # Risk-aware routing (mcp-brain-bridge) — ON by default. Hard stages use the
 # high model, light stages use the low one; an explicit `risk_tier` on
 # `brain_turn(..., risk_tier=...)` overrides the stage-derived tier
@@ -47,8 +96,9 @@ BRAIN_API_KEY=sk-...
 # Both model ids below are also the built-in code defaults.
 # Set the switch to a falsy value to disable routing (single-model behavior).
 #BRAIN_RISK_ROUTING_ENABLED=true
-#BRAIN_MODEL_LOW=deepseek/deepseek-v4.1-flash
-#BRAIN_MODEL_HIGH=openai/gpt-5.6-luna
+# Tier models (production default 2026-10-21 — verified on /go/resp):
+#BRAIN_MODEL_LOW=muse-spark-1.3-contributor
+#BRAIN_MODEL_HIGH=gpt-6-luna
 # Stage->tier overrides: comma-separated `stage:Tier` pairs merged onto the
 # built-in default (unusable pairs are ignored).
 #BRAIN_STAGE_TIERS=plan:T2,review:T2,implement:T0,qa:T0,closure:T0
diff --git a/.opencode/memory/architecture/responses_api_best_practice_audit_2026_10_21.md b/.opencode/memory/architecture/responses_api_best_practice_audit_2026_10_21.md
index 6abf8ae..a0348e3 100644
--- a/.opencode/memory/architecture/responses_api_best_practice_audit_2026_10_21.md
+++ b/.opencode/memory/architecture/responses_api_best_practice_audit_2026_10_21.md
@@ -44,4 +44,18 @@ D2 continuity and context: F2 F3 F10 — transcript format change (output items
 D3 record only: no behavior change; correct the CHANGELOG claims; keep this memory shard.
 
 ## Gateway probe checklist (prerequisite for any scope)
-One small request per parameter: store:false, prompt_cache_key, truncation:auto, include:[reasoning.encrypted_content], instructions, context_management. Record which are accepted, whether the response echoes model and service_tier, and whether usage.input_tokens_details.cached_tokens is populated.
\ No newline at end of file
+One small request per parameter: store:false, prompt_cache_key, truncation:auto, include:[reasoning.encrypted_content], instructions, context_management. Record which are accepted, whether the response echoes model and service_tier, and whether usage.input_tokens_details.cached_tokens is populated.
+
+## Implementation outcome (2026-10-21, task 329 — supersedes the scopes above)
+
+All ten findings implemented in `mcp-brain-bridge/server.py`; all six new wire parameters probed HTTP 200 against the live gateway (`/go/resp/responses`) before wiring. Switches default OFF, so default wire bytes are unchanged until operators opt in.
+
+- F1 `store:false` + F4 `prompt_cache_key` + F3 `truncation:auto` + F10 `instructions` + `include`/`context_management`: one `_build_request_body` builder behind `BRAIN_SEND_STORE`, `BRAIN_SEND_INCLUDE_ENCRYPTED`, `BRAIN_SEND_CACHE_KEY`, `BRAIN_SEND_TRUNCATION`, `BRAIN_SEND_CONTEXT_MANAGEMENT`, `BRAIN_USE_INSTRUCTIONS`.
+- F2: assistant transcript records carry `phase`, `response_id`, `provider_items` (non-message output items replayed verbatim); old text-only transcripts replay exactly as before (key presence is the version).
+- F3: estimator calibrated from observed `usage.input_tokens` (`BRAIN_CHARS_PER_TOKEN` override, fail loud).
+- F5: diagnostics read `response.model`/`response.id`/`service_tier`/`cached_tokens`; mismatch with the requested model warns on stderr.
+- F6: `error.code`/`error.type` parsed; six billing/spend/quota 429 codes terminal with an actionable hint.
+- F7: transport/parse/fatal-4xx failures return a structured REPORT with `debug.provider` instead of raising.
+- F8: effort validated against `none/minimal/low/medium/high/xhigh/max`; ladder `max→xhigh→high→medium→low→minimal→minimal`, unknown values keep current effort (never raise).
+- F9: `_get_max_tokens` fails loud; `_FATAL_STATUS` deleted; `_send_with_learning` renamed to `_send_with_retry`; stale `__pycache__` removed; CHANGELOG Task 298 entry already states the stateless path, so no history rewrite was needed.
+- Full suite: 554 passed, 1 pre-existing failure (`test_system_prompt_split_assemble_round_trip`, proven on HEAD); 23 new tests in `tests/test_brain_responses_alignment.py`.
\ No newline at end of file
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 12be832..c78e848 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Responses API best-practice alignment implemented (Task 329, D1 + D2):** all ten 2026-10-21 audit findings are now code in `mcp-brain-bridge/server.py`, with every new wire parameter probed HTTP 200 against the live gateway (`127.0.0.1:8081/go/resp/responses`) before wiring and shipped behind env switches defaulting to off, so default wire bytes are unchanged until operators opt in. Request shape: one `_build_request_body` builder owns `model`/`input`/`reasoning`/`max_output_tokens` plus opt-in `store: false` (`BRAIN_SEND_STORE`), `include: ["reasoning.encrypted_content"]` (`BRAIN_SEND_INCLUDE_ENCRYPTED`), stable `prompt_cache_key` from the system-prompt hash (`BRAIN_SEND_CACHE_KEY`), `truncation: "auto"` (`BRAIN_SEND_TRUNCATION`), `context_management` compaction (`BRAIN_SEND_CONTEXT_MANAGEMENT` + `BRAIN_COMPACTION_THRESHOLD`), and top-level `instructions` (`BRAIN_USE_INSTRUCTIONS`). Continuity: assistant transcript records carry `phase`, `response_id`, and `provider_items` (non-message output items replayed verbatim); old text-only transcripts replay exactly as before. Estimator calibrated from observed `usage.input_tokens` (`BRAIN_CHARS_PER_TOKEN` override, fail loud). Diagnostics now read `response.model`/`response.id`/`service_tier`/`cached_tokens` plus `error.code`/`error.type`, with a stderr warning on model substitution; six billing/spend/quota 429 codes are terminal with an actionable hint; fatal transport/parse/4xx failures return a structured REPORT with `debug.provider` instead of raising; effort validated against the official vocabulary with a never-raise ladder (`max→xhigh→high→medium→low→minimal→minimal`); `_get_max_tokens` fails loud, `_FATAL_STATUS` deleted, `_send_with_learning` renamed to `_send_with_retry`, stale bytecode removed (the Task 298 CHANGELOG entry already states the stateless path, so no history rewrite). Docs: `docs/brain-bridge.md` request-shape/diagnostics section plus ten new env rows, `.env.example` switch block, `mcp-brain-bridge` README invariant + ADR-004. 23 new tests in `tests/test_brain_responses_alignment.py`; full suite 554 passed with the one pre-existing failure; `debug.provider` always carries the new keys including on fatal turns.
+
 - **Responses API best-practice audit recorded for later implementation (Task 329, no code change):** a research pass against the current official OpenAI Responses API material — the create reference and the conversation-state, reasoning, text, prompt-caching, error-codes, your-data and streaming guides on `developers.openai.com`, the Cookbook "per-run spending controller" sample, and the `openai-python` 2.54.0 `ResponseCreateParams` (generated from the OpenAPI spec) — audited against `mcp-brain-bridge/server.py`, the repository's only provider call site. Ten findings are recorded in `tasks/backlog/329-responses-api-best-practices-alignment.md` with the official quote, the code citation, the impact and the proposed fix: F1 `store` never sent (responses stored provider-side by default while the system prompt, task file and diffs are sent); F2 reasoning items and assistant `phase` dropped on every turn, against the official "preserve every item in the response's `output` array"; F3 no `truncation` (the default `disabled` fails with a 400) and no `context_management` compaction behind a `chars // 4` estimate against a 1M-token window; F4 `prompt_cache_key` never sent although a cache-split descriptor is computed and deliberately kept off the wire, and `cached_tokens` never read; F5 the response `model` never read, so a silent model substitution is invisible; F6 every 429 retried and `error.code` never parsed, against the official "retrying billing, spend, or quota errors won't restore API access"; F7 a fatal 4xx escaping `brain_turn` as a raw exception instead of a REPORT with `debug.provider`; F8 the reasoning-effort ladder omitting `minimal` with an unknown-value fallback that raises effort, and no validation against the official vocabulary; F9 configuration hygiene (silent `BRAIN_MAX_TOKENS` fallback, dead `_FATAL_STATUS`, vestigial `_send_with_learning`, stale bytecode, and a CHANGELOG claim about a correction path the code no longer contains); F10 the system prompt as a `role: "system"` item instead of the top-level `instructions` field. The same record is saved to project memory (`architecture/responses_api_best_practice_audit_2026_10_21`), together with a verified-correct table and three implementation scopes (D1 request-shape and observability, D2 transcript continuity and context, D3 record only). Audit caveat recorded in the task: the live peer is a local gateway on `127.0.0.1:8081`, not `api.openai.com`, and it was not probed, so every parameter claim is "documented by OpenAI" rather than "verified live" — a gateway probe is a prerequisite for any scope.
 - **Telegram message formatting contract (Task 328):** the Manager's contract document — proven empirically against the live Telegram MCP on 2026-10-21 — is stored as `docs/telegram-message-formatting.md` (executive summary, length findings with the 4096-char cap and the opaque `GEN-ERR-184`, parse-mode findings where HTML is fully preserved but Markdown strips ` ``` ` fences and leaves `*bold*` literal, the U+200C ZWNJ read-path loss, the missing `topic_id` on `send_message`, read-path notes, safe patterns, reproduction probes, the upstream defect list, and a binding authoring-rules table). The new `telegram-message-format` skill carries the nine rules, four message templates, the pre-send checklist, and the upstream defect table, and is registered in the agent skills registry; `telegram-issue-sync` loads it in Phase 0 and sends its confirmation as an HTML block anchored to the source message, with no emoji, no fences, no ZWNJ, and a ~3800-char budget; `telegram-message-export` formats its caption and states the topic rule for delivery; the executor skill auto-loading matrix binds any Telegram MCP send, reply, edit, or caption to the skill, so direct MCP use is covered too; `docs/telegram-setup.md` gains the skill row and a §6.1 contract summary; the contract is saved to project memory (index rebuilt, 27 shards) and the three skills are synced byte-identically to the global install; three contract tests added (skill terms, both Telegram skills referencing it, document presence). Bumped `<system_version>` 9.63.0 → 9.64.0 with byte-identical re-assemble.
 - **Plugin lane contract for Brain and Hands (Task 327):** the goal, todolist, and smart-compact lanes become executable steps instead of trailing prose. Lane G (goal) restores the missing `goal_set` create trigger and states the full lifecycle with the evidence gate and the busy-lease retry; Lane T (todolist) mirrors ANY Brain-produced plan with 2 or more steps, including the combined conditional phase, and states the replace-whole-list semantics, the 100-item and 500-char caps, the durable session storage, and the automatic re-injection; Lane C (smart-compact) adds the task-boundary trigger (previous task finished, new task in the same session) and states the async effect plus the `omitted-NNNN` retrieval rule. (Round 2 superseded the in-prompt lanes: the prompt is now plugin-blind and the executor owns every lane — see the separation entries below.)
diff --git a/docs/brain-bridge.md b/docs/brain-bridge.md
index dfce527..604e9f5 100644
--- a/docs/brain-bridge.md
+++ b/docs/brain-bridge.md
@@ -132,6 +132,14 @@ repo-root `.env`). Real process env wins; blank counts as unset. See
 | `BRAIN_MODEL_WINDOW_CHARS` | `200000` — utilization monitor only, never a send cap |
 | `BRAIN_CONTEXT_WINDOW_TOKENS` | `1048576` — provider window for the pre-send guard; blank/unset = default |
 | `BRAIN_BUDGET_MARGIN_TOKENS` | `8192` — safety margin for the pre-send guard; blank/unset = default |
+| `BRAIN_SEND_STORE` | off — when on, sends `store: false` (F1; probed OK on the live gateway 2026-10-21) |
+| `BRAIN_SEND_INCLUDE_ENCRYPTED` | off — when on, sends `include: ["reasoning.encrypted_content"]` (F1/F2; probed OK) |
+| `BRAIN_SEND_CACHE_KEY` | off — when on, sends a stable `prompt_cache_key` derived from the system-prompt hash (F4; probed OK) |
+| `BRAIN_SEND_TRUNCATION` | off — when on, sends `truncation: "auto"` (F3; probed OK) |
+| `BRAIN_SEND_CONTEXT_MANAGEMENT` | off — when on, sends `context_management: [{type: compaction, compact_threshold}]` (F3; probed OK, record-only) |
+| `BRAIN_USE_INSTRUCTIONS` | off — when on, the system prompt moves to top-level `instructions` instead of a `role: system` input item (F10; probed OK) |
+| `BRAIN_CHARS_PER_TOKEN` | unset — explicit chars-per-token override for the pre-send estimate; otherwise calibrated from observed `usage.input_tokens`, else `4.0` (F3) |
+| `BRAIN_COMPACTION_THRESHOLD` | `100000` — token threshold for `context_management` compaction (F3) |
 
 `BRAIN_INPUT_BUDGET` defaults to 1,000,000 chars (~217k input tokens at
 the measured ~4.6 chars/token) — room for full context and diff reports
@@ -187,6 +195,37 @@ always empty:
 A capability-blocked turn returns the same field set (with `status:
 "REPORT"`), so callers never face two incompatible schemas.
 
+## Request shape and provider diagnostics
+
+The base request body is `model`, `input`, `reasoning.effort`,
+`max_output_tokens` (plus `temperature` when explicitly set, which still
+deletes `reasoning`). Every newer Responses parameter is opt-in behind
+the `BRAIN_SEND_*` / `BRAIN_USE_INSTRUCTIONS` switches above, each
+defaulting to off so default wire bytes are unchanged. All six were
+probed `HTTP 200` against the live gateway (`127.0.0.1:8081/go/resp`)
+on 2026-10-21 before being wired.
+
+Reasoning continuity: assistant transcript records now carry `phase`,
+`response_id`, and `provider_items` (non-message output items such as
+reasoning blocks with encrypted content); the next turn replays them
+after their message item. Old text-only transcripts replay exactly as
+before. Reasoning effort is validated against the official vocabulary
+(`none/minimal/low/medium/high/xhigh/max`); the truncation-recovery
+ladder runs `max→xhigh→high→medium→low→minimal→minimal` and never
+raises effort. A malformed `BRAIN_MAX_TOKENS` fails loud.
+
+`debug.provider` on every turn now carries `response_model`,
+`response_id`, `service_tier`, `usage.input_tokens_details.cached_tokens`,
+and `error_code` / `error_type` alongside the previous fields, plus
+`requested_model` for the substitution check (mismatch warns on
+stderr, never fails). Billing/spend/quota 429 codes
+(`credit_balance_exhausted`, `organization_spend_limit_exceeded`,
+`project_spend_limit_exceeded`, `organization_usage_limit_exceeded`,
+`insufficient_quota`, `billing_hard_limit_exceeded`) are terminal with
+an actionable hint and are not retried. A fatal 4xx or transport
+failure returns a structured `REPORT` carrying `debug.provider`
+instead of raising a raw exception.
+
 ## Routing
 
 Risk-aware model routing is ON by default. The effective tier comes from
diff --git a/mcp-brain-bridge/DECISIONS.md b/mcp-brain-bridge/DECISIONS.md
index 892d5f0..68a0d80 100644
--- a/mcp-brain-bridge/DECISIONS.md
+++ b/mcp-brain-bridge/DECISIONS.md
@@ -20,3 +20,10 @@
 - **Decision:** Estimate input as chars divided by four, add live reserved output, compare against window minus margin; trim oldest history, then diffs and context, then bundle; persistent over-budget returns a BRAIN_BUDGET_OVER REPORT hint and skips the provider.
 - **Consequences:** Oversize turns fail gracefully with numbers; 128K and 256K caps with xhigh keep working inside the window.
 - **Rollback:** Revert the guard hunk plus hint helper plus eight tests.
+
+## [2026-10-21] ADR-004: Responses API best-practice alignment
+
+- **Context:** The 2026-10-21 audit found ten drifts from current official Responses practice in the single provider call site: no `store`, dropped reasoning items and `phase`, no `truncation`, no cache key, unread response `model`, retried billing 429s, raw-exception fatal 4xx, an effort ladder that could raise effort, silent token-cap fallback, and a role-form system prompt.
+- **Decision:** Fix all ten behind per-parameter env switches defaulting to off (all six new wire parameters probed HTTP 200 against the live gateway first); validate effort against the official vocabulary; parse `error.code`/`error.type` with terminal billing codes; read `response.model`/`cached_tokens` into diagnostics; replay reasoning items and `phase` from version-tolerant transcripts; return structured REPORTs on fatal transport errors; fail loud on malformed numeric config.
+- **Consequences:** Default wire bytes are unchanged until operators opt in; diagnostics expose model substitution and cache hits; transcripts stay backward compatible.
+- **Rollback:** One-function revert of the request builder plus switch-off; diagnostics parser is pure and separately testable.
diff --git a/mcp-brain-bridge/README.md b/mcp-brain-bridge/README.md
index d4749bd..c20fcee 100644
--- a/mcp-brain-bridge/README.md
+++ b/mcp-brain-bridge/README.md
@@ -19,3 +19,6 @@ Brain Bridge MCP daemon: single-tool (`brain_turn`) automation path for planning
 - Single-tool invariant: no second tool or slash-command path may bypass `brain_turn`.
 - Helpers (`capability`, `loop_guard`, `preflight`) stay stdlib-only and importable without MCP runtime so tests stay offline.
 - Session ledger is append-only; never rewrite history lines.
+- Request-shape evolution stays opt-in: every new Responses parameter
+  ships behind a `BRAIN_SEND_*` / `BRAIN_USE_INSTRUCTIONS` switch
+  defaulting to off, so default wire bytes never change silently.
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 432e138..ca2e0b5 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -1372,6 +1372,200 @@ def build_prompt_cache_split(
     }
 
 
+def _env_flag(name: str) -> bool:
+    """Read a boolean env switch (Task 329: request-shape opt-ins).
+
+    Truthy values are ``1``/``true``/``yes``/``on`` (case-insensitive);
+    everything else — including blank/unset — is off. Every new
+    Responses parameter ships behind one of these switches defaulting
+    to off, so wire bytes stay identical to the pre-329 shape until
+    the operator opts in.
+    """
+    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}
+
+
+def _prompt_cache_key(system_prompt: str) -> str:
+    """Stable prompt-cache key from the static system prefix (Task 329 F4).
+
+    The system prompt is byte-identical across turns, which is the ideal
+    cache prefix. The key carries only a hash — never prompt text.
+    """
+    digest = hashlib.sha256(system_prompt.encode("utf-8")).hexdigest()[:32]
+    return "brain-" + digest
+
+
+def _compaction_threshold() -> int:
+    """Compaction token threshold for ``context_management`` (Task 329 F3).
+
+    Override via ``BRAIN_COMPACTION_THRESHOLD`` (default 100000).
+    Malformed or non-positive values fail loud.
+    """
+    raw = os.environ.get("BRAIN_COMPACTION_THRESHOLD", "100000").strip() or "100000"
+    try:
+        val = int(raw)
+    except ValueError:
+        raise ValueError(
+            f"BRAIN_COMPACTION_THRESHOLD={raw!r} is not an integer; "
+            "set a positive integer or leave it blank"
+        )
+    if val <= 0:
+        raise ValueError(
+            f"BRAIN_COMPACTION_THRESHOLD={raw!r} must be > 0; "
+            "set a positive integer or leave it blank"
+        )
+    return val
+
+
+#: Fallback chars-per-token before any provider measurement (Task 329 F3).
+_CHARS_PER_TOKEN_DEFAULT = 4.0
+#: Calibrated ratio from observed usage (module-global, updated per turn).
+_calibrated_chars_per_token: Optional[float] = None
+
+
+def _chars_per_token() -> float:
+    """Chars-per-token ratio for the pre-send estimate (Task 329 F3).
+
+    Explicit ``BRAIN_CHARS_PER_TOKEN`` wins (fail loud on malformed);
+    otherwise the calibrated ratio from observed usage; otherwise 4.0.
+    """
+    raw = os.environ.get("BRAIN_CHARS_PER_TOKEN", "").strip()
+    if raw:
+        try:
+            val = float(raw)
+        except ValueError:
+            raise ValueError(
+                f"BRAIN_CHARS_PER_TOKEN={raw!r} is not a number; "
+                "set a positive number or leave it blank"
+            )
+        if val <= 0:
+            raise ValueError(
+                f"BRAIN_CHARS_PER_TOKEN={raw!r} must be > 0; "
+                "set a positive number or leave it blank"
+            )
+        return val
+    if _calibrated_chars_per_token is not None:
+        return _calibrated_chars_per_token
+    return _CHARS_PER_TOKEN_DEFAULT
+
+
+def _note_observed_ratio(chars: int, input_tokens: int) -> None:
+    """Calibrate the estimator from one observed turn (Task 329 F3).
+
+    Pure bookkeeping: a plausible observation (ratio inside [1, 8])
+    replaces the ratio; garbage (non-positive inputs, absurd ratios)
+    is ignored so a corrupt usage payload can never corrupt the guard.
+    """
+    global _calibrated_chars_per_token
+    try:
+        if chars <= 0 or input_tokens <= 0:
+            return
+        ratio = chars / input_tokens
+    except (TypeError, ZeroDivisionError):
+        return
+    if 1.0 <= ratio <= 8.0:
+        _calibrated_chars_per_token = ratio
+
+
+def _build_request_body(
+    system_prompt: str,
+    history: Optional[list],
+    effective_prompt: str,
+    *,
+    model: Optional[str] = None,
+    effort: Optional[str] = None,
+    max_tokens: Optional[int] = None,
+) -> dict[str, Any]:
+    """Assemble the Responses request body (Task 329 request-shape work).
+
+    The base shape is the pre-329 contract — ``model``, ``input``,
+    ``reasoning.effort``, ``max_output_tokens`` — plus ``temperature``
+    when explicitly set (which still deletes ``reasoning``). Every new
+    Responses parameter is opt-in behind an env switch defaulting to
+    off, so the default wire bytes are byte-identical to before:
+
+    - ``BRAIN_SEND_STORE`` → ``store: false`` (F1)
+    - ``BRAIN_SEND_INCLUDE_ENCRYPTED`` → ``include:
+      ["reasoning.encrypted_content"]`` (F1/F2)
+    - ``BRAIN_SEND_CACHE_KEY`` → ``prompt_cache_key`` from the system
+      prefix hash (F4)
+    - ``BRAIN_SEND_TRUNCATION`` → ``truncation: "auto"`` (F3)
+    - ``BRAIN_SEND_CONTEXT_MANAGEMENT`` → compaction entry (F3,
+      record-only unless probed)
+    - ``BRAIN_USE_INSTRUCTIONS`` → system prompt moves to top-level
+      ``instructions`` instead of a ``role: system`` input item (F10)
+
+    History items may carry ``phase`` (assistant only — replayed on the
+    item per the official guidance) and ``provider_items`` (non-message
+    output items such as reasoning blocks with encrypted content,
+    replayed verbatim after their turn — F2). Old text-only transcripts
+    carry neither key and replay exactly as before.
+    """
+    if model is None:
+        model = _get_brain_model()
+    if effort is None:
+        effort = _get_reasoning_effort()
+    if max_tokens is None:
+        max_tokens = _get_max_tokens()
+    use_instructions = _env_flag("BRAIN_USE_INSTRUCTIONS")
+    if use_instructions:
+        chat: list[dict[str, Any]] = []
+    else:
+        chat = [{"role": "system", "content": system_prompt}]
+    for turn in history or []:
+        if not isinstance(turn, dict):
+            continue
+        item: dict[str, Any] = {
+            "role": turn.get("role", "user"),
+            "content": turn.get("content", ""),
+        }
+        phase = turn.get("phase")
+        if item["role"] == "assistant" and isinstance(phase, str) and phase:
+            item["phase"] = phase
+        chat.append(item)
+        for extra in turn.get("provider_items") or []:
+            if isinstance(extra, dict):
+                chat.append(extra)
+    chat.append({"role": "user", "content": effective_prompt})
+    body: dict[str, Any] = {
+        "model": model,
+        "input": chat,
+        # Responses API shape: effort nests under reasoning (flat
+        # reasoning_effort is rejected by strict providers, e.g.
+        # OpenAI/OpenRouter 400 unsupported_parameter).
+        "reasoning": {"effort": effort},
+        "max_output_tokens": max_tokens,
+    }
+    if use_instructions:
+        body["instructions"] = system_prompt
+    if _env_flag("BRAIN_SEND_STORE"):
+        body["store"] = False
+    if _env_flag("BRAIN_SEND_INCLUDE_ENCRYPTED"):
+        body["include"] = ["reasoning.encrypted_content"]
+    if _env_flag("BRAIN_SEND_CACHE_KEY"):
+        body["prompt_cache_key"] = _prompt_cache_key(system_prompt)
+    if _env_flag("BRAIN_SEND_TRUNCATION"):
+        body["truncation"] = "auto"
+    if _env_flag("BRAIN_SEND_CONTEXT_MANAGEMENT"):
+        body["context_management"] = [
+            {"type": "compaction", "compact_threshold": _compaction_threshold()}
+        ]
+    # Blank-means-unset: only send temperature when explicitly set. A
+    # non-blank temperature conflicts with reasoning effort on Responses
+    # models, so drop the reasoning key when temperature is present.
+    _temp_raw = os.environ.get("BRAIN_TEMPERATURE", "")
+    if _temp_raw.strip():
+        try:
+            body["temperature"] = float(_temp_raw.strip())
+        except ValueError:
+            raise ValueError(
+                f"BRAIN_TEMPERATURE={_temp_raw.strip()!r} is not a number; "
+                "set a numeric value or leave it blank"
+            )
+        else:
+            del body["reasoning"]
+    return body
+
+
 def _get_max_tokens() -> int:
     """Cap for Brain turns; override via ``BRAIN_MAX_TOKENS``.
 
@@ -1379,11 +1573,25 @@ def _get_max_tokens() -> int:
     output and count against this cap on most providers, so a smaller cap
     lets high-effort reasoning starve the visible answer (blank or
     truncated replies while the reasoning tokens are still charged).
+
+    Fail-loud (Task 329 F9): a non-numeric or non-positive value raises
+    instead of silently falling back — a quiet 32768 would change the
+    output budget and the reasoning-budget warning threshold.
     """
+    raw = os.environ.get("BRAIN_MAX_TOKENS", "32768").strip() or "32768"
     try:
-        return int(os.environ.get("BRAIN_MAX_TOKENS", "32768").strip() or "32768")
+        val = int(raw)
     except ValueError:
-        return 32768
+        raise ValueError(
+            f"BRAIN_MAX_TOKENS={raw!r} is not an integer; "
+            "set a positive integer or leave it blank"
+        )
+    if val <= 0:
+        raise ValueError(
+            f"BRAIN_MAX_TOKENS={raw!r} must be > 0; "
+            "set a positive integer or leave it blank"
+        )
+    return val
 
 
 # Pre-send token budget guard: values are operator-tunable via env
@@ -1395,12 +1603,14 @@ _BUDGET_SAFETY_MARGIN_DEFAULT = 8192
 
 
 def _estimate_input_tokens_from_chars(budget_chars: int) -> int:
-    """Estimate input tokens from character count for pre-send budget check. Why this exists: provider bills tokens while bridge only sees chars, so chars divided by four gives a conservative fast estimate matching existing lines 3030 and 3056. Args budget_chars total chars of system plus effective plus history plus diffs plus context plus bundle. Returns integer token estimate. Edge: zero or negative input returns zero, never negative."""
+    """Estimate input tokens from character count for pre-send budget check. Why this exists: provider bills tokens while bridge only sees chars, so the calibrated ratio gives a fast estimate matching existing lines 3030 and 3056. Args budget_chars total chars of system plus effective plus history plus diffs plus context plus bundle. Returns integer token estimate. Edge: zero or negative input returns zero, never negative."""
     # Guard trivial input first so downstream math never sees negative totals.
     if budget_chars <= 0:
         return 0
-    # Integer division matches existing estimate behavior exactly.
-    return budget_chars // 4
+    # Calibrated ratio (Task 329 F3): explicit BRAIN_CHARS_PER_TOKEN,
+    # else measured from observed usage, else 4.0 — identical to the old
+    # integer division when uncalibrated.
+    return int(budget_chars / _chars_per_token())
 
 
 def _pre_send_budget_fits(
@@ -1440,13 +1650,70 @@ _RETRYABLE_STATUS = {429, 500, 502, 503, 504}
 
 # Fatal client errors: never retried — the request itself is wrong
 # (bad auth, bad route, bad payload). Other 4xx fail fast the same way.
-_FATAL_STATUS = {400, 401, 403, 404, 422}
+# NOTE (Task 329 F9): the old ``_FATAL_STATUS`` constant listed
+# {400, 401, 403, 404, 422} but was never referenced — the branch below
+# is range-based, so the constant was deleted rather than kept in sync.
 
 # Overall deadline (seconds) for the whole retry sequence. Sleeps are
 # capped by the remaining budget; hitting the deadline fast-fails instead
 # of sleeping past it.
 _OVERALL_DEADLINE_S = 500.0
 
+#: Billing/spend/quota 429 codes that must NEVER be retried (Task 329
+#: F6, per the official error-codes guide): "Retrying billing, spend, or
+#: quota errors won't restore API access." These fail terminal with an
+#: actionable hint instead of burning three attempts plus backoff.
+_TERMINAL_429_CODES = frozenset(
+    {
+        "credit_balance_exhausted",
+        "organization_spend_limit_exceeded",
+        "project_spend_limit_exceeded",
+        "organization_usage_limit_exceeded",
+        "insufficient_quota",
+        "billing_hard_limit_exceeded",
+    }
+)
+
+
+def _terminal_429_code(status: Any, data: Any) -> Optional[str]:
+    """Return the terminal billing/spend/quota code, or None (pure).
+
+    Only 429 responses are examined; anything else returns None so the
+    existing retry/fatal branches keep their behavior. Unknown 429 codes
+    and unparseable bodies return None — current retry behavior is the
+    safe default against false-terminal classification.
+    """
+    if status != 429:
+        return None
+    if isinstance(data, dict):
+        error = data.get("error")
+        if isinstance(error, dict):
+            code = error.get("code")
+            if isinstance(code, str) and code.strip().lower() in _TERMINAL_429_CODES:
+                return code.strip().lower()
+    return None
+
+
+def _error_code_from_body(text: Any) -> Optional[str]:
+    """Best-effort ``error.code`` extraction from a response body (pure).
+
+    Never raises: non-JSON or misshapen bodies yield None.
+    """
+    try:
+        if not isinstance(text, str) or not text.strip():
+            return None
+        data = json.loads(text)
+    except (ValueError, TypeError):
+        return None
+    if isinstance(data, dict):
+        error = data.get("error")
+        if isinstance(error, dict):
+            code = error.get("code")
+            if isinstance(code, str) and code.strip():
+                return code.strip()
+    return None
+
+
 # Empty-output contract (Task 232): a REPORT with blank output is a
 # transport/model flake, never a verdict. The bridge MUST NOT return it
 # silently — it substitutes the EMPTY_OUTPUT_RETRY hint so the caller
@@ -1494,15 +1761,29 @@ def _retry_after_s(resp: Any) -> float:
     return min(val, 120.0)
 
 
-def _transport_fail(message: str, attempts: int) -> RuntimeError:
+def _transport_fail(
+    message: str,
+    attempts: int,
+    *,
+    provider_status: Optional[int] = None,
+    provider_code: Optional[str] = None,
+    provider_type: Optional[str] = None,
+) -> RuntimeError:
     """Build a transport RuntimeError carrying its attempt count.
 
     WS3 seam (GitHub issue 17): the learning send path accounts
     attempts across the failed round and the corrected retry.
     Message text is unchanged — existing message matches keep passing.
+
+    Task 329 F6/F7: the provider status/code/type ride along as
+    attributes so the caller can build a structured REPORT instead of
+    re-parsing the message text. Attributes default to None.
     """
     err = RuntimeError(message)
     err.transport_attempts = attempts  # type: ignore[attr-defined]
+    err.provider_status = provider_status  # type: ignore[attr-defined]
+    err.provider_code = provider_code  # type: ignore[attr-defined]
+    err.provider_type = provider_type  # type: ignore[attr-defined]
     return err
 
 
@@ -1544,17 +1825,43 @@ def _post_with_retry(client: Any, url: str, payload: dict[str, Any]) -> tuple[An
             if resp.status_code < 400:
                 return resp, attempts
             last_status, last_snippet = resp.status_code, resp.text[:500]
+            if resp.status_code == 429:
+                # Terminal billing/spend/quota codes (Task 329 F6): the
+                # official guide says retrying these cannot restore
+                # access, so fail at once with an actionable hint. The
+                # body parse is best-effort — an unparseable body keeps
+                # the current retry behavior.
+                try:
+                    _terminal_data = json.loads(resp.text) if resp.text else None
+                except (ValueError, TypeError):
+                    _terminal_data = None
+                _terminal_code = _terminal_429_code(resp.status_code, _terminal_data)
+                if _terminal_code is not None:
+                    raise _transport_fail(
+                        f"provider billing/quota error 429 "
+                        f"({_terminal_code}, no retry) at "
+                        f"{url.rsplit('/', 1)[-1]}: {last_snippet}. "
+                        "Add credits or raise the organization/project "
+                        "spend or usage limit before sending another request.",
+                        attempts,
+                        provider_status=resp.status_code,
+                        provider_code=_terminal_code,
+                    )
             if resp.status_code not in _RETRYABLE_STATUS:
                 if 400 <= resp.status_code < 500:
                     raise _transport_fail(
                         f"fatal provider error {resp.status_code} (no retry) at "
                         f"{url.rsplit('/', 1)[-1]}: {last_snippet}",
                         attempts,
+                        provider_status=resp.status_code,
+                        provider_code=_error_code_from_body(resp.text),
                     )
                 raise _transport_fail(
                     f"provider error {resp.status_code} at "
                     f"{url.rsplit('/', 1)[-1]}: {last_snippet}",
                     attempts,
+                    provider_status=resp.status_code,
+                    provider_code=_error_code_from_body(resp.text),
                 )
             if resp.status_code == 429:
                 retry_after = _retry_after_s(resp)
@@ -1641,21 +1948,18 @@ def _make_client() -> Any:
     )
 
 
-def _send_with_learning(
+def _send_with_retry(
     make_client: Any,
     url: str,
     body: dict[str, Any],
-    *,
-    task_key: Optional[str] = None,
-    task_id: Optional[str] = None,
-    session_id: Optional[str] = None,
-    project_root: Optional[str] = None,
 ) -> tuple[Any, int]:
     """POST with stateless retry (429/5xx + timeouts via _post_with_retry).
 
     No correction memory and no escalation: 4xx fails fast inside
-    ``_post_with_retry`` and propagates to the caller. Extra keyword
-    arguments stay accepted so existing callers pass unchanged.
+    ``_post_with_retry`` and propagates to the caller. Renamed from
+    ``_send_with_learning`` (Task 329 F9) — the old name promised a
+    learning seam whose kwargs (task_key/task_id/session_id/project_root)
+    the body never used.
     """
     with make_client() as client:
         resp, attempts = _post_with_retry(client, url, body)
@@ -1929,6 +2233,14 @@ _META_KEYS = (
     "models",
     "truncated_total",
     "compacted_count",
+    # Task 329 F2 continuity: assistant phase, provider response id, and
+    # replayable non-message output items (reasoning blocks with
+    # encrypted content). Old records lack these keys and replay exactly
+    # as before — the transcript format is backward compatible by key
+    # presence, no version flag needed.
+    "phase",
+    "response_id",
+    "provider_items",
 )
 
 
@@ -2115,12 +2427,21 @@ def append_turn(
     prompt_hash: Optional[str] = None,
     truncated: int = 0,
     project_root: Optional[str] = None,
+    phase: Optional[str] = None,
+    response_id: Optional[str] = None,
+    provider_items: Optional[list] = None,
 ) -> None:
     """Append one turn to the task transcript (creates dirs as needed).
 
     Traceability keys ride on every record; unset stays None/0 so
     older callers keep working unchanged. Writes always go to the
-    per-project path, never to the legacy global dir."""
+    per-project path, never to the legacy global dir.
+
+    Task 329 F2: assistant records may carry ``phase`` (commentary vs
+    final answer, replayed on the item per the official guidance),
+    ``response_id``, and ``provider_items`` (non-message output items
+    such as reasoning blocks, replayed verbatim after their turn).
+    """
     path = _write_transcript_path(task_id, project_root)
     path.parent.mkdir(parents=True, exist_ok=True)
     record: dict[str, Any] = {
@@ -2130,6 +2451,12 @@ def append_turn(
         "prompt_hash": prompt_hash,
         "truncated": truncated,
     }
+    if isinstance(phase, str) and phase:
+        record["phase"] = phase
+    if isinstance(response_id, str) and response_id:
+        record["response_id"] = response_id
+    if isinstance(provider_items, list) and provider_items:
+        record["provider_items"] = provider_items
     with path.open("a", encoding="utf-8") as fh:
         fcntl.flock(fh, fcntl.LOCK_EX)
         try:
@@ -3189,32 +3516,7 @@ def brain_turn(
             f"(budget_chars={budget_chars} est_tokens~{budget_chars // 4})",
             file=sys.stderr,
         )
-    chat: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
-    chat.extend({"role": t["role"], "content": t["content"]} for t in history)
-    chat.append({"role": "user", "content": effective_prompt})
-    body: dict[str, Any] = {
-        "model": model,
-        "input": chat,
-        # Responses API shape: effort nests under reasoning (flat
-        # reasoning_effort is rejected by strict providers, e.g.
-        # OpenAI/OpenRouter 400 unsupported_parameter).
-        "reasoning": {"effort": _get_reasoning_effort()},
-        "max_output_tokens": _get_max_tokens(),
-    }
-    # Blank-means-unset: only send temperature when explicitly set. A
-    # non-blank temperature conflicts with reasoning effort on Responses
-    # models, so drop the reasoning key when temperature is present.
-    _temp_raw = os.environ.get("BRAIN_TEMPERATURE", "")
-    if _temp_raw.strip():
-        try:
-            body["temperature"] = float(_temp_raw.strip())
-        except ValueError:
-            raise ValueError(
-                f"BRAIN_TEMPERATURE={_temp_raw.strip()!r} is not a number; "
-                "set a numeric value or leave it blank"
-            )
-        else:
-            del body["reasoning"]
+    body = _build_request_body(system_prompt, history, effective_prompt, model=model)
     if "reasoning" in body:
         # Guard the risky default (Task 259): reasoning tokens count
         # against max_output_tokens, so high/xhigh effort with a small cap
@@ -3235,7 +3537,11 @@ def brain_turn(
     # the fragment is discarded and pass 1 re-issues the whole turn once
     # server-side with stepped-down reasoning effort. Structured output
     # must never stitch a fragment — the whole call is retried with more
-    # visible-answer headroom instead.
+    # visible-answer headroom instead. resp_data stays None on paths that
+    # never reach the provider (budget-over) or that fail before parsing
+    # (structured fatal) — the continuity capture below treats None as
+    # empty, never a crash.
+    resp_data: Any = None
     for _transport_pass in (0, 1):
         if _budget_over_hint_text is not None:
             # Pre-send budget guard tripped: skip the provider entirely and
@@ -3256,17 +3562,38 @@ def brain_turn(
             session_id=session_id,
             project_root=project_root,
         )
-        resp, attempts = _send_with_learning(
-            _make_client,
-            _responses_url(),
-            body,
-            task_key=history_key,
-            task_id=task_id,
-            session_id=session_id,
-            project_root=project_root,
-        )
-        _total_attempts += attempts
-        resp_data = _resp_json(resp)
+        try:
+            resp, attempts = _send_with_retry(
+                _make_client,
+                _responses_url(),
+                body,
+            )
+            _total_attempts += attempts
+            resp_data = _resp_json(resp)
+        except RuntimeError as exc:
+            # Structured fatal (Task 329 F7): a transport failure, a
+            # malformed body, or a fatal 4xx must surface as a REPORT
+            # carrying debug.provider — never as a raw tool exception.
+            # Genuine bugs still raise: only RuntimeError from the send
+            # path converts; anything else propagates untouched.
+            _total_attempts += int(getattr(exc, "transport_attempts", 0) or 0)
+            _fatal_code = getattr(exc, "provider_code", None)
+            if not isinstance(_fatal_code, str):
+                _fatal_code = None
+            _fatal_status = getattr(exc, "provider_status", None)
+            diag = parse_responses_diagnostics(
+                {"error": {"message": str(exc), "code": _fatal_code}}
+            )
+            if isinstance(_fatal_status, int):
+                diag["provider_status_code"] = _fatal_status
+            diag["requested_model"] = model
+            _log_provider_diagnostics(diag)
+            output = _provider_error_hint(
+                diag["error"] or str(exc), diag.get("error_code")
+            )
+            xml_blocks = []
+            _raw_text_present = False
+            break
         output = parse_responses_text(resp_data)
         # Eligibility is judged on the RAW model text: the triage below
         # rewrites blank output into hint text, and a rewritten hint must
@@ -3332,14 +3659,18 @@ def brain_turn(
                 )
                 xml_blocks = []
         diag = parse_responses_diagnostics(resp_data)
+        diag["requested_model"] = model
         _log_provider_diagnostics(diag)
+        _note = _model_substitution_note(diag, model)
+        if _note is not None:
+            print(f"brain-bridge: {_note}", file=sys.stderr)
         if not xml_blocks and not output.strip():
             # Empty-output triage (Task 259): classify the provider diagnosis
             # BEFORE falling back to the flake hint. Order is load-bearing:
             # top-level error -> refusal -> output-budget exhaustion -> flake.
             state = _task_state_note(history_key, project_root)
             if diag["error"]:
-                output = _provider_error_hint(diag["error"])
+                output = _provider_error_hint(diag["error"], diag.get("error_code"))
             elif diag["refusal"]:
                 output = _provider_refusal_hint(diag["refusal"])
             elif (
@@ -3406,6 +3737,19 @@ def brain_turn(
         )
         xml_blocks = []
     fence_drops = list(_last_fence_drops)
+    # Continuity capture (Task 329 F2/F3): replayable provider items
+    # plus estimator calibration from this turn's observed usage. The
+    # fatal-error path leaves resp_data None, which yields empty
+    # continuity and skips calibration — never a crash.
+    _replay_phase, _replay_response_id, _replay_items = _replayable_provider_items(
+        resp_data
+    )
+    if isinstance(resp_data, dict):
+        _seen_usage = resp_data.get("usage")
+        if isinstance(_seen_usage, dict):
+            _seen_input = _as_int(_seen_usage.get("input_tokens"))
+            if _seen_input is not None:
+                _note_observed_ratio(budget_chars, _seen_input)
     if history_key:
         prompt_hash = hashlib.sha256(effective_prompt.encode("utf-8")).hexdigest()
         # Store the compact form: attachment markers, not attachment
@@ -3429,6 +3773,9 @@ def brain_turn(
             prompt_hash=prompt_hash,
             truncated=truncated_count,
             project_root=project_root,
+            phase=_replay_phase,
+            response_id=_replay_response_id,
+            provider_items=_replay_items,
         )
     result: dict[str, Any] = {
         "status": "XML_EXTRACTED" if xml_blocks else "REPORT",
@@ -3475,11 +3822,23 @@ def _get_reasoning_effort() -> str:
     ``xhigh`` (and ``max``) allocate roughly 95% of ``max_output_tokens`` to
     reasoning, so a modest cap leaves almost nothing for the visible answer
     while the reasoning tokens are still billed.
+
+    Validated against the official Responses vocabulary (Task 329 F8):
+    none/minimal/low/medium/high/xhigh/max. Anything else raises instead
+    of reaching the provider as a 400.
     """
     val = os.environ.get("BRAIN_REASONING_EFFORT", "medium").strip() or "medium"
     if not re.fullmatch(r"[\w.-]{1,64}", val):
         raise ValueError(f"bad reasoning effort: {val!r}")
-    return val
+    if val.lower() not in _EFFORT_VOCABULARY:
+        raise ValueError(
+            f"BRAIN_REASONING_EFFORT={val!r} is not a Responses effort; "
+            f"expected one of {sorted(_EFFORT_VOCABULARY)}"
+        )
+    # Normalized to lower (Task 329 QA F4): the provider vocabulary is
+    # lowercase, and a preserved `LOW`/`XHigh` would ship an invalid
+    # effort string after passing validation.
+    return val.lower()
 
 
 def _task_state_note(task_id: Optional[str], project_root: Optional[str] = None) -> str:
@@ -3614,14 +3973,38 @@ def parse_responses_diagnostics(data: Any) -> dict:
             "input_tokens": None,
             "output_tokens": None,
             "reasoning_tokens": None,
+            "cached_tokens": None,
             "total_tokens": None,
         },
         "error": None,
+        "error_code": None,
+        "error_type": None,
         "refusal": None,
+        # Response identity (Task 329 F5): echoed by the provider, read
+        # so a silent model substitution by a routing gateway is visible.
+        # provider_status_code is set only on the fatal-transport path
+        # (Task 329 QA F5): the HTTP status that produced the structured
+        # REPORT, so debug.provider never hides it as status=None.
+        "response_model": None,
+        "response_id": None,
+        "service_tier": None,
+        "provider_status_code": None,
     }
     if not isinstance(data, dict):
         return diag
 
+    response_model = data.get("model")
+    if isinstance(response_model, str) and response_model:
+        diag["response_model"] = response_model
+
+    response_id = data.get("id")
+    if isinstance(response_id, str) and response_id:
+        diag["response_id"] = response_id
+
+    service_tier = data.get("service_tier")
+    if isinstance(service_tier, str) and service_tier:
+        diag["service_tier"] = service_tier
+
     status = data.get("status")
     if isinstance(status, str) and status:
         diag["status"] = status
@@ -3637,6 +4020,11 @@ def parse_responses_diagnostics(data: Any) -> dict:
         diag["usage"]["input_tokens"] = _as_int(usage.get("input_tokens"))
         diag["usage"]["output_tokens"] = _as_int(usage.get("output_tokens"))
         diag["usage"]["total_tokens"] = _as_int(usage.get("total_tokens"))
+        in_details = usage.get("input_tokens_details")
+        if isinstance(in_details, dict):
+            # Prompt-cache visibility (Task 329 F4): a populated value
+            # proves the cache key is working; None means unreported.
+            diag["usage"]["cached_tokens"] = _as_int(in_details.get("cached_tokens"))
         details = usage.get("output_tokens_details")
         if isinstance(details, dict):
             diag["usage"]["reasoning_tokens"] = _as_int(details.get("reasoning_tokens"))
@@ -3655,6 +4043,15 @@ def parse_responses_diagnostics(data: Any) -> dict:
                 diag["error"] = json.dumps(error, ensure_ascii=False)
             except (TypeError, ValueError):
                 diag["error"] = str(error)
+        # Machine-readable billing/spend/quota classification (Task 329
+        # F6): the detail lives in error.code, not in error.type or the
+        # message text.
+        code = error.get("code")
+        if isinstance(code, str) and code.strip():
+            diag["error_code"] = code.strip()
+        err_type = error.get("type")
+        if isinstance(err_type, str) and err_type.strip():
+            diag["error_type"] = err_type.strip()
     elif error is not None and not isinstance(error, list):
         diag["error"] = str(error)
 
@@ -3685,6 +4082,64 @@ def parse_responses_diagnostics(data: Any) -> dict:
     return diag
 
 
+def _replayable_provider_items(resp_data: Any) -> tuple[Any, Any, list]:
+    """Extract continuity items from a Responses payload (Task 329 F2).
+
+    Pure (no I/O): returns ``(phase, response_id, provider_items)``.
+    ``phase`` comes from the first assistant message item that carries
+    one (commentary vs final answer); ``response_id`` is the provider
+    response id; ``provider_items`` are the non-message output items
+    (reasoning blocks with encrypted content) replayed verbatim after
+    their turn. Message items are NOT replayed — their text already
+    rides the transcript content rows, and replaying both would
+    duplicate them. Anything malformed yields ``(None, None, [])``.
+    """
+    if not isinstance(resp_data, dict):
+        return None, None, []
+    response_id = resp_data.get("id")
+    if not isinstance(response_id, str) or not response_id:
+        response_id = None
+    phase: Any = None
+    items: list = []
+    output = resp_data.get("output")
+    if isinstance(output, list):
+        for entry in output:
+            if not isinstance(entry, dict):
+                continue
+            if entry.get("type") == "message":
+                if phase is None:
+                    maybe_phase = entry.get("phase")
+                    if isinstance(maybe_phase, str) and maybe_phase:
+                        phase = maybe_phase
+                continue
+            items.append(entry)
+    return phase, response_id, items
+
+
+def _model_substitution_note(diag: dict, requested: str) -> Optional[str]:
+    """Warn when the provider served a different model than requested.
+
+    Pure (no I/O): returns the warning text or None. The bridge points
+    at a routing gateway that may fall back or downgrade tiers, so a
+    silent substitution would invalidate the tier routing that chose
+    the requested id. A mismatch warns — it never fails the turn.
+    """
+    response_model = diag.get("response_model")
+    if (
+        isinstance(response_model, str)
+        and response_model
+        and isinstance(requested, str)
+        and requested
+        and response_model != requested
+    ):
+        return (
+            f"model substitution: requested {requested!r} but provider "
+            f"served {response_model!r} — tier routing assumed the "
+            "requested id"
+        )
+    return None
+
+
 def _log_provider_diagnostics(diag: dict) -> None:
     """Emit one compact diagnostics line to stderr on every turn (AC1).
 
@@ -3708,19 +4163,35 @@ def _log_provider_diagnostics(diag: dict) -> None:
         f"output_tokens={out_tokens} "
         f"reasoning_tokens={reasoning_tokens} "
         f"visible_tokens={visible_tokens} "
+        f"cached_tokens={usage.get('cached_tokens')} "
         f"total_tokens={usage.get('total_tokens')} "
-        f"error={diag.get('error')!r} refusal={diag.get('refusal')!r}",
+        f"model={diag.get('response_model')} "
+        f"tier={diag.get('service_tier')} "
+        f"http_status={diag.get('provider_status_code')} "
+        f"error={diag.get('error')!r} error_code={diag.get('error_code')!r} "
+        f"refusal={diag.get('refusal')!r}",
         file=sys.stderr,
     )
 
 
-def _provider_error_hint(error: str) -> str:
-    """Surface a top-level provider error verbatim (Task 259, terminal)."""
-    return (
+def _provider_error_hint(error: str, code: Optional[str] = None) -> str:
+    """Surface a top-level provider error verbatim (Task 259, terminal).
+
+    Task 329 F6: a terminal billing/spend/quota code appends the
+    actionable remedy — retrying those can never restore access.
+    """
+    hint = (
         f"{PROVIDER_ERROR}: the provider returned an error "
         "(terminal for this turn, never a verdict):\n"
         f"{error}"
     )
+    if isinstance(code, str) and code.strip().lower() in _TERMINAL_429_CODES:
+        hint += (
+            "\nThis is a billing, spend, or quota error: do NOT retry — "
+            "add credits or raise the organization/project spend or usage "
+            "limit before sending another request."
+        )
+    return hint
 
 
 def _provider_refusal_hint(refusal: str) -> str:
@@ -3768,29 +4239,45 @@ def _output_budget_hint(
 #: callers and regression tests match this exact string.
 TRUNCATION_UNRECOVERABLE = "TRUNCATION_UNRECOVERABLE"
 
+#: Official Responses reasoning-effort vocabulary (Task 329 F8).
+#: Model-dependent subset applies per model; the bridge accepts the full
+#: vocabulary and lets the provider reject per-model unsupported values
+#: (surfaced as a structured REPORT via the fatal-error path, never a
+#: raw exception).
+_EFFORT_VOCABULARY = frozenset(
+    {"none", "minimal", "low", "medium", "high", "xhigh", "max"}
+)
+
 #: One-notch reasoning-effort step-down for truncation recovery (Task
 #: 291). Lower effort frees visible-answer share inside the same
 #: ``max_output_tokens`` cap — the only headroom source once the cap
-#: already sits at the model ceiling. Unknown/non-string values fail
-#: safe to ``medium``; ``low`` is the floor (a second step down from
-#: ``low`` would change nothing, so the caller treats equality as
-#: no-recovery).
+#: already sits at the model ceiling. Unknown/non-string values keep
+#: the current effort (``low`` when there is none to keep): the floor
+#: guard treats equality as no-recovery, so an unknown value can never
+#: RAISE effort the way the old ``medium`` fallback did (Task 329 F8).
 _EFFORT_STEPDOWN = {
     "max": "xhigh",
     "xhigh": "high",
     "high": "medium",
     "medium": "low",
-    "low": "low",
+    "low": "minimal",
+    "minimal": "minimal",
 }
 
 
 def _step_down_effort(effort: object) -> str:
-    """Return one notch below ``effort`` (pure, offline)."""
+    """Return one notch below ``effort`` (pure, offline).
+
+    A value already in the ladder maps down it; an unknown string keeps
+    itself (recovery is then a no-op via the floor guard); a missing or
+    non-string value falls to ``low``.
+    """
     if isinstance(effort, str) and effort.strip():
         key = effort.strip().lower()
         if key in _EFFORT_STEPDOWN:
             return _EFFORT_STEPDOWN[key]
-    return "medium"
+        return effort
+    return "low"
 
 
 def _truncation_exhausted_hint(
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index 2548cb8..6fa859f 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -1912,10 +1912,13 @@ def test_step_down_effort_map():
     assert bridge._step_down_effort("medium") == "low"
     assert bridge._step_down_effort("max") == "xhigh"
     assert bridge._step_down_effort("XHIGH") == "high"
-    assert bridge._step_down_effort("low") == "low"
-    assert bridge._step_down_effort("turbo") == "medium"
-    assert bridge._step_down_effort("") == "medium"
-    assert bridge._step_down_effort(None) == "medium"
+    assert bridge._step_down_effort("low") == "minimal"
+    assert bridge._step_down_effort("minimal") == "minimal"
+    # Unknown values keep the current effort (floor guard => no recovery),
+    # never jump up. Missing values fall to low.
+    assert bridge._step_down_effort("turbo") == "turbo"
+    assert bridge._step_down_effort("") == "low"
+    assert bridge._step_down_effort(None) == "low"
 
 
 def test_truncation_exhausted_hint_is_terminal():
@@ -1983,7 +1986,7 @@ def test_brain_turn_no_recovery_at_effort_floor(tmp_path, monkeypatch):
     script = [
         _FakeResp(200, "cut", _incomplete_payload(_TRUNCATED_IMPLEMENT)),
     ]
-    result = _run_recovery_turn(monkeypatch, tmp_path, script, holder, effort="low")
+    result = _run_recovery_turn(monkeypatch, tmp_path, script, holder, effort="minimal")
     assert result["status"] == "REPORT"
     assert bridge.TRUNCATION_UNRECOVERABLE in result["output"]
     assert "partial plan text" not in result["output"]
@@ -2031,23 +2034,38 @@ def test_brain_turn_complete_xml_with_incomplete_status_no_recovery(
     assert len(holder["bodies"]) == 1
 
 
-def test_brain_turn_uppercase_low_floor_no_second_call(tmp_path, monkeypatch):
+def test_brain_turn_uppercase_minimal_floor_no_second_call(tmp_path, monkeypatch):
     holder = {}
     script = [
         _FakeResp(200, "cut", _incomplete_payload(_TRUNCATED_IMPLEMENT)),
     ]
-    result = _run_recovery_turn(monkeypatch, tmp_path, script, holder, effort="LOW")
+    result = _run_recovery_turn(monkeypatch, tmp_path, script, holder, effort="MINIMAL")
     assert result["status"] == "REPORT"
     assert bridge.TRUNCATION_UNRECOVERABLE in result["output"]
     assert len(holder["bodies"]) == 1
 
 
+def test_brain_turn_low_steps_down_to_minimal(tmp_path, monkeypatch):
+    """Low is no longer the floor (Task 329 F8): low recovers once at
+    minimal, then the floor guard stops a third call."""
+    holder = {}
+    script = [
+        _FakeResp(200, "cut1", _incomplete_payload(_TRUNCATED_IMPLEMENT)),
+        _FakeResp(200, "cut2", _incomplete_payload("more partial prose")),
+    ]
+    result = _run_recovery_turn(monkeypatch, tmp_path, script, holder, effort="low")
+    assert result["status"] == "REPORT"
+    assert bridge.TRUNCATION_UNRECOVERABLE in result["output"]
+    assert len(holder["bodies"]) == 2
+    assert holder["bodies"][1]["reasoning"]["effort"] == "minimal"
+
+
 def test_brain_turn_prose_only_floor_truncation_is_terminal(tmp_path, monkeypatch):
     holder = {}
     script = [
         _FakeResp(200, "cut", _incomplete_payload("plain prose, cut mid-way")),
     ]
-    result = _run_recovery_turn(monkeypatch, tmp_path, script, holder, effort="low")
+    result = _run_recovery_turn(monkeypatch, tmp_path, script, holder, effort="minimal")
     assert result["status"] == "REPORT"
     assert bridge.TRUNCATION_UNRECOVERABLE in result["output"]
     assert len(holder["bodies"]) == 1
@@ -2481,6 +2499,7 @@ def test_parse_responses_diagnostics_full_payload():
         "input_tokens": 100,
         "output_tokens": 16384,
         "reasoning_tokens": 16384,
+        "cached_tokens": None,
         "total_tokens": 16484,
     }
     assert diag["error"] is None
@@ -2490,11 +2509,24 @@ def test_parse_responses_diagnostics_full_payload():
 def test_parse_responses_diagnostics_tolerates_malformed():
     for bad in ({}, {"output": None}, {"usage": "nope"}, {"error": {}}, []):
         diag = bridge.parse_responses_diagnostics(bad)
-        assert set(diag) == {"status", "incomplete_reason", "usage", "error", "refusal"}
+        assert set(diag) == {
+            "status",
+            "incomplete_reason",
+            "usage",
+            "error",
+            "error_code",
+            "error_type",
+            "refusal",
+            "response_model",
+            "response_id",
+            "service_tier",
+            "provider_status_code",
+        }
         assert set(diag["usage"]) == {
             "input_tokens",
             "output_tokens",
             "reasoning_tokens",
+            "cached_tokens",
             "total_tokens",
         }
     assert bridge.parse_responses_diagnostics(None)["status"] is None
@@ -2643,7 +2675,14 @@ def test_brain_turn_debug_provider_on_success(tmp_path, monkeypatch):
         "incomplete_reason",
         "usage",
         "error",
+        "error_code",
+        "error_type",
         "refusal",
+        "response_model",
+        "response_id",
+        "service_tier",
+        "provider_status_code",
+        "requested_model",
     }
 
 
@@ -2674,7 +2713,19 @@ def test_parse_responses_diagnostics_scalar_content_does_not_raise():
         diag = bridge.parse_responses_diagnostics(
             {"output": [{"type": "message", "content": bad_content}]}
         )
-        assert set(diag) == {"status", "incomplete_reason", "usage", "error", "refusal"}
+        assert set(diag) == {
+            "status",
+            "incomplete_reason",
+            "usage",
+            "error",
+            "error_code",
+            "error_type",
+            "refusal",
+            "response_model",
+            "response_id",
+            "service_tier",
+            "provider_status_code",
+        }
         assert diag["refusal"] is None
 
 
@@ -2694,6 +2745,7 @@ def test_parse_responses_diagnostics_non_finite_usage_is_none():
         "input_tokens": None,
         "output_tokens": None,
         "reasoning_tokens": None,
+        "cached_tokens": None,
         "total_tokens": None,
     }
 
diff --git a/tests/test_brain_responses_alignment.py b/tests/test_brain_responses_alignment.py
new file mode 100644
index 0000000..52ee793
--- /dev/null
+++ b/tests/test_brain_responses_alignment.py
@@ -0,0 +1,385 @@
+# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
+"""Responses-API alignment tests (Task 329).
+
+Offline only: covers the request-body builder behind env switches, the
+extended diagnostics parser (response model, cached tokens, error
+codes), the billing-terminal 429 classifier, the corrected effort
+ladder, fail-loud token cap, versioned transcript replay with phase,
+estimator calibration, and the fatal-4xx-as-REPORT path. The live LLM
+path (httpx POST) is never touched: provider calls are faked.
+"""
+
+import os
+import sys
+import types as _types
+from pathlib import Path
+
+import pytest
+
+BRIDGE_DIR = Path(__file__).parent.parent / "mcp-brain-bridge"
+sys.path.insert(0, str(BRIDGE_DIR))
+
+import server as bridge
+
+
+@pytest.fixture(autouse=True)
+def _clean_responses_env(monkeypatch):
+    """Hermetic defaults for every alignment test: drop ambient session
+    binding and every request-shape switch so the default wire bytes
+    stay identical to the pre-329 shape unless a test opts in."""
+    monkeypatch.delenv("OPENCODE_SESSION_ID", raising=False)
+    for var in (
+        "BRAIN_SEND_STORE",
+        "BRAIN_SEND_INCLUDE_ENCRYPTED",
+        "BRAIN_SEND_CACHE_KEY",
+        "BRAIN_SEND_TRUNCATION",
+        "BRAIN_SEND_CONTEXT_MANAGEMENT",
+        "BRAIN_USE_INSTRUCTIONS",
+        "BRAIN_CHARS_PER_TOKEN",
+        "BRAIN_COMPACTION_THRESHOLD",
+        "BRAIN_TEMPERATURE",
+    ):
+        monkeypatch.delenv(var, raising=False)
+    monkeypatch.setenv("BRAIN_REASONING_EFFORT", "medium")
+    monkeypatch.setenv("BRAIN_MAX_TOKENS", "32768")
+    # Reset the calibrated estimator so tests never inherit each other.
+    bridge._calibrated_chars_per_token = None  # type: ignore[attr-defined]
+    yield
+    bridge._calibrated_chars_per_token = None  # type: ignore[attr-defined]
+
+
+def _history():
+    return [
+        {"role": "user", "content": "first question"},
+        {"role": "assistant", "content": "first answer"},
+    ]
+
+
+# --- Request-body builder (F1/F3/F4/F10) ---------------------------------
+
+
+def test_body_builder_default_shape_unchanged():
+    """With every switch off, wire bytes are identical to pre-329 shape."""
+    body = bridge._build_request_body("sys", _history(), "do it")
+    assert set(body) == {"model", "input", "reasoning", "max_output_tokens"}
+    assert body["input"][0] == {"role": "system", "content": "sys"}
+    assert body["input"][-1] == {"role": "user", "content": "do it"}
+    assert body["reasoning"] == {"effort": "medium"}
+
+
+def test_body_builder_flags_matrix(monkeypatch):
+    """Each opt-in switch adds exactly its documented key, nothing else."""
+    monkeypatch.setenv("BRAIN_SEND_STORE", "1")
+    body = bridge._build_request_body("sys", _history(), "do it")
+    assert body["store"] is False
+
+    monkeypatch.setenv("BRAIN_SEND_CACHE_KEY", "yes")
+    body = bridge._build_request_body("sys", _history(), "do it")
+    assert isinstance(body["prompt_cache_key"], str)
+    assert body["prompt_cache_key"].startswith("brain-")
+    key2 = bridge._build_request_body("sys", _history(), "different prompt")[
+        "prompt_cache_key"
+    ]
+    assert body["prompt_cache_key"] == key2, "key must be stable per system prompt"
+    key3 = bridge._build_request_body("other-sys", _history(), "do it")[
+        "prompt_cache_key"
+    ]
+    assert key3 != body["prompt_cache_key"], "key must vary with system prompt"
+
+    monkeypatch.setenv("BRAIN_SEND_TRUNCATION", "true")
+    body = bridge._build_request_body("sys", _history(), "do it")
+    assert body["truncation"] == "auto"
+
+    monkeypatch.setenv("BRAIN_SEND_INCLUDE_ENCRYPTED", "on")
+    body = bridge._build_request_body("sys", _history(), "do it")
+    assert body["include"] == ["reasoning.encrypted_content"]
+
+    monkeypatch.setenv("BRAIN_SEND_CONTEXT_MANAGEMENT", "1")
+    body = bridge._build_request_body("sys", _history(), "do it")
+    assert body["context_management"] == [
+        {"type": "compaction", "compact_threshold": 100000}
+    ]
+
+    monkeypatch.setenv("BRAIN_USE_INSTRUCTIONS", "1")
+    body = bridge._build_request_body("sys", _history(), "do it")
+    assert body["instructions"] == "sys"
+    assert all(t.get("role") != "system" for t in body["input"])
+    assert body["input"][-1] == {"role": "user", "content": "do it"}
+
+
+# --- Diagnostics parser (F4/F5/F6) ----------------------------------------
+
+
+def test_diagnostics_reads_model_and_cached_tokens_and_error_codes():
+    data = {
+        "id": "resp_123",
+        "model": "muse-spark-1.3-contributor",
+        "service_tier": "default",
+        "status": "completed",
+        "usage": {
+            "input_tokens": 10,
+            "output_tokens": 5,
+            "total_tokens": 15,
+            "input_tokens_details": {"cached_tokens": 4},
+            "output_tokens_details": {"reasoning_tokens": 2},
+        },
+        "error": {
+            "message": "quota hit",
+            "code": "insufficient_quota",
+            "type": "insufficient_quota",
+        },
+        "output": [],
+    }
+    diag = bridge.parse_responses_diagnostics(data)
+    assert diag["response_model"] == "muse-spark-1.3-contributor"
+    assert diag["response_id"] == "resp_123"
+    assert diag["service_tier"] == "default"
+    assert diag["usage"]["cached_tokens"] == 4
+    assert diag["usage"]["reasoning_tokens"] == 2
+    assert diag["error"] == "quota hit"
+    assert diag["error_code"] == "insufficient_quota"
+    assert diag["error_type"] == "insufficient_quota"
+
+
+def test_diagnostics_new_keys_default_to_none():
+    diag = bridge.parse_responses_diagnostics({"status": "completed"})
+    assert diag["response_model"] is None
+    assert diag["response_id"] is None
+    assert diag["service_tier"] is None
+    assert diag["provider_status_code"] is None
+    assert diag["usage"]["cached_tokens"] is None
+    assert diag["error_code"] is None
+    assert diag["error_type"] is None
+
+
+def test_effort_validation_normalizes_case(monkeypatch):
+    monkeypatch.setenv("BRAIN_REASONING_EFFORT", "XHigh")
+    assert bridge._get_reasoning_effort() == "xhigh"
+
+
+# --- Terminal 429 classifier (F6) ------------------------------------------
+
+
+@pytest.mark.parametrize(
+    "code",
+    [
+        "credit_balance_exhausted",
+        "organization_spend_limit_exceeded",
+        "project_spend_limit_exceeded",
+        "organization_usage_limit_exceeded",
+        "insufficient_quota",
+        "billing_hard_limit_exceeded",
+    ],
+)
+def test_terminal_429_codes_are_terminal(code):
+    assert bridge._terminal_429_code(429, {"error": {"code": code}}) == code
+
+
+def test_non_terminal_429_returns_none():
+    assert (
+        bridge._terminal_429_code(429, {"error": {"code": "rate_limit_exceeded"}})
+        is None
+    )
+    assert bridge._terminal_429_code(429, {"error": {"message": "slow down"}}) is None
+    assert bridge._terminal_429_code(429, "slow down") is None
+    assert (
+        bridge._terminal_429_code(500, {"error": {"code": "insufficient_quota"}})
+        is None
+    )
+
+
+# --- Effort vocabulary and ladder (F8) --------------------------------------
+
+
+def test_effort_ladder_includes_minimal_and_never_raises():
+    assert bridge._step_down_effort("max") == "xhigh"
+    assert bridge._step_down_effort("xhigh") == "high"
+    assert bridge._step_down_effort("high") == "medium"
+    assert bridge._step_down_effort("medium") == "low"
+    assert bridge._step_down_effort("low") == "minimal"
+    assert bridge._step_down_effort("minimal") == "minimal"
+    # Unknown values keep the current effort (floor guard => no recovery),
+    # never jump up to medium.
+    assert bridge._step_down_effort("turbo") == "turbo"
+    assert bridge._step_down_effort("none") == "none"
+
+
+def test_effort_ladder_bad_types_fall_to_low():
+    assert bridge._step_down_effort("") == "low"
+    assert bridge._step_down_effort(None) == "low"
+
+
+def test_effort_validation_accepts_official_vocabulary(monkeypatch):
+    for effort in ("none", "minimal", "low", "medium", "high", "xhigh", "max"):
+        monkeypatch.setenv("BRAIN_REASONING_EFFORT", effort)
+        assert bridge._get_reasoning_effort() == effort
+
+
+def test_effort_validation_rejects_garbage(monkeypatch):
+    import pytest as _pt
+
+    for bad in ("bad effort!!", "x" * 65, "MEDIUM!!"):
+        monkeypatch.setenv("BRAIN_REASONING_EFFORT", bad)
+        with _pt.raises(ValueError):
+            bridge._get_reasoning_effort()
+
+
+# --- Token cap fails loud (F9) -----------------------------------------------
+
+
+def test_get_max_tokens_fail_loud(monkeypatch):
+    import pytest as _pt
+
+    monkeypatch.setenv("BRAIN_MAX_TOKENS", "not-a-number")
+    with _pt.raises(ValueError, match="BRAIN_MAX_TOKENS"):
+        bridge._get_max_tokens()
+    monkeypatch.setenv("BRAIN_MAX_TOKENS", "-5")
+    with _pt.raises(ValueError, match="BRAIN_MAX_TOKENS"):
+        bridge._get_max_tokens()
+    monkeypatch.setenv("BRAIN_MAX_TOKENS", "16384")
+    assert bridge._get_max_tokens() == 16384
+
+
+# --- Transcript replay with phase and reasoning items (F2) --------------------
+
+
+def test_parse_turns_keeps_provider_items_and_phase():
+    raw = (
+        '{"role": "user", "content": "q"}\n'
+        '{"role": "assistant", "content": "a", "phase": "final_answer", '
+        '"response_id": "resp_1", "provider_items": '
+        '[{"id": "rs_1", "type": "reasoning", "encrypted_content": "e30="}]}\n'
+    )
+    turns, skipped = bridge._parse_turns(raw)
+    assert skipped == 0
+    assert turns[1]["phase"] == "final_answer"
+    assert turns[1]["response_id"] == "resp_1"
+    assert turns[1]["provider_items"] == [
+        {"id": "rs_1", "type": "reasoning", "encrypted_content": "e30="}
+    ]
+
+
+def test_old_transcript_replays_exactly_as_today():
+    raw = '{"role": "user", "content": "q"}\n{"role": "assistant", "content": "a"}\n'
+    turns, _ = bridge._parse_turns(raw)
+    assert "provider_items" not in turns[1]
+    assert "phase" not in turns[1]
+    body = bridge._build_request_body("sys", turns, "next")
+    assert body["input"][1] == {"role": "user", "content": "q"}
+    assert body["input"][2] == {"role": "assistant", "content": "a"}
+
+
+def test_new_transcript_replays_reasoning_items_and_phase():
+    raw = (
+        '{"role": "user", "content": "q"}\n'
+        '{"role": "assistant", "content": "a", "phase": "final_answer", '
+        '"provider_items": [{"id": "rs_1", "type": "reasoning"}]}\n'
+    )
+    turns, _ = bridge._parse_turns(raw)
+    body = bridge._build_request_body("sys", turns, "next")
+    assistant = body["input"][2]
+    assert assistant["content"] == "a"
+    assert assistant["phase"] == "final_answer"
+    assert {"id": "rs_1", "type": "reasoning"} in body["input"][3:]
+
+
+# --- Estimator calibration (F3) -----------------------------------------------
+
+
+def test_estimator_calibration_from_observed_usage():
+    assert bridge._estimate_input_tokens_from_chars(4000) == 1000
+    bridge._note_observed_ratio(4600, 1000)
+    assert bridge._estimate_input_tokens_from_chars(4600) == 1000
+    # Garbage observations never corrupt the estimator.
+    bridge._note_observed_ratio(0, 0)
+    bridge._note_observed_ratio(-10, 5)
+    assert bridge._estimate_input_tokens_from_chars(4600) == 1000
+
+
+def test_chars_per_token_env_override_fail_loud(monkeypatch):
+    import pytest as _pt
+
+    monkeypatch.setenv("BRAIN_CHARS_PER_TOKEN", "junk")
+    with _pt.raises(ValueError, match="BRAIN_CHARS_PER_TOKEN"):
+        bridge._estimate_input_tokens_from_chars(100)
+    monkeypatch.setenv("BRAIN_CHARS_PER_TOKEN", "2")
+    assert bridge._estimate_input_tokens_from_chars(100) == 50
+
+
+# --- Fatal 4xx as structured REPORT (F7) ---------------------------------------
+
+
+class _FakeResp:
+    def __init__(self, status_code=200, text="", payload=None):
+        self.status_code = status_code
+        self.text = text
+        self._payload = payload
+        self.headers = {"content-type": "application/json"}
+
+    def json(self):
+        if isinstance(self._payload, Exception):
+            raise self._payload
+        return self._payload
+
+
+class _FakeClient:
+    def __init__(self, script):
+        self._script = list(script)
+        self.last_body = None
+
+    def __enter__(self):
+        return self
+
+    def __exit__(self, *a):
+        return False
+
+    def post(self, url, json=None, headers=None, **kwargs):
+        self.last_body = json
+        item = self._script.pop(0) if len(self._script) > 1 else self._script[0]
+        if isinstance(item, Exception):
+            raise item
+        return item
+
+
+def _mk_sys_prompt(tmp_path, monkeypatch, text="sys"):
+    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
+    prompt_file = tmp_path / ".config" / "opencode" / "sys.md"
+    prompt_file.parent.mkdir(parents=True, exist_ok=True)
+    prompt_file.write_text(text, encoding="utf-8")
+    monkeypatch.setenv("BRAIN_SYSTEM_PROMPT", str(prompt_file))
+
+
+def _stub_client(monkeypatch, script):
+    stub = _types.ModuleType("httpx")
+    stub.Client = lambda *a, **k: _FakeClient(script)
+    stub.TimeoutException = type("TimeoutException", (Exception,), {})
+    stub.TransportError = type("TransportError", (Exception,), {})
+
+    class _Timeout:
+        def __init__(self, *a, **k):
+            self.args, self.kwargs = a, k
+
+    stub.Timeout = _Timeout
+    monkeypatch.setitem(sys.modules, "httpx", stub)
+
+
+def test_fatal_4xx_returns_report_with_provider_diagnostics(tmp_path, monkeypatch):
+    """A 400 with an error code must surface as a REPORT carrying
+    debug.provider — never as a raw tool exception (F7)."""
+    import time as _time
+
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _mk_sys_prompt(tmp_path, monkeypatch)
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
+    monkeypatch.setattr(_time, "sleep", lambda s: None)
+    body_text = '{"error": {"message": "quota hit", "code": "insufficient_quota"}}'
+    _stub_client(monkeypatch, [_FakeResp(400, body_text, None)])
+    target = (
+        bridge.brain_turn.fn if hasattr(bridge.brain_turn, "fn") else bridge.brain_turn
+    )
+    result = target("q", task_id="329")
+    assert result["status"] == "REPORT"
+    assert bridge.PROVIDER_ERROR in result["output"]
+    assert "insufficient_quota" in result["output"]
+    assert result["debug"]["provider"]["error_code"] == "insufficient_quota"
+    assert result["debug"]["provider"]["provider_status_code"] == 400
diff --git a/tests/test_session_lifecycle.py b/tests/test_session_lifecycle.py
index 2b23dbf..c8223fe 100644
--- a/tests/test_session_lifecycle.py
+++ b/tests/test_session_lifecycle.py
@@ -420,7 +420,9 @@ def test_brain_turn_emits_ordered_checkpoints(tmp_path, monkeypatch):
     ]
 
 
-def test_brain_turn_unsupported_param_fails_fast(tmp_path, monkeypatch):
+def test_brain_turn_unsupported_param_returns_report(tmp_path, monkeypatch):
+    """A 400 unsupported_parameter surfaces as a structured REPORT with
+    debug.provider (Task 329 F7) — never as a raw tool exception."""
     proj = _turn_env(tmp_path, monkeypatch)
     monkeypatch.setenv("BRAIN_TEMPERATURE", "0.7")
     bodies: list = []
@@ -428,5 +430,15 @@ def test_brain_turn_unsupported_param_fails_fast(tmp_path, monkeypatch):
     _stub_client(monkeypatch, script, bodies)
     call = bridge.brain_turn
     target = call.fn if hasattr(call, "fn") else call
-    with pytest.raises(RuntimeError, match="fatal provider error 400"):
-        target("q", task_id="999", project_root=str(proj))
+    result = target("q", task_id="999", project_root=str(proj))
+    assert result["status"] == "REPORT"
+    assert bridge.PROVIDER_ERROR in result["output"]
+    assert "temperature" in result["output"]
+    assert result["debug"]["provider"]["error_code"] == "unsupported_parameter"
+    # The failed turn still records the transport checkpoint, just never
+    # reaches response_parsed.
+    names = [
+        e.get("checkpoint") for e in _ledger_events(proj) if e["event"] == "checkpoint"
+    ]
+    assert "transport_started" in names
+    assert "response_parsed" not in names
```
<!-- END_GIT_DIFF -->
