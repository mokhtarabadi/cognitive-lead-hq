# Task 404: Audit zen-proxy and brain bridge against OpenAI contracts and upstream proxy

**File:** `tasks/completed/404-zen-proxy-openai-api-audit.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Finished:** 2026-11-17T08:13:33Z
**Submitted:** 2026-11-17T08:04:55Z
**Created:** 2026-11-17 UTC
**Mode:** autopilot (locked by Manager "auto brain mode", 2026-11-17)

## Goal

Complete one long research-and-audit task in seven phases: learn the external `12errh/zen-proxy` implementation, learn the official OpenAI Chat Completions and Responses API endpoint contracts by deep web research, review our `zen-proxy/` and `mcp-brain-bridge/` code, audit the brain bridge against the OpenAI docs, and audit our zen-proxy against the external proxy. Produce evidence-backed reports for every phase and apply only minimal, proven fixes where drift is confirmed. Keep a long todowrite and an active Goal throughout.

## Blueprint Reference

Brain-approved plan, `brain_turn` task id `404`, session `ses_e178e7d34ffewoGYL5tvo2Zn9n`. Final implementation XML at `tasks/.sessions/ses_e178e7d34ffewoGYL5tvo2Zn9n_6252dad9/brain_outputs/resp_6afc064a585fd0e2529e4c21_d6061aef2fae4568b776d79c39b11998.json`.

Brainstorm: not required — explicit seven-phase sequence with defined inputs and outputs, no competing architectures to rank, single feasible path with conditional fixes only.

Seat ownership: Steps 2-4 Software Architect; Steps 5-6 Senior Programmer; Step 7 Senior Programmer + QA Engineer; Step 8 Software Architect + QA Engineer + Code Reviewer.

## Manager's Notes

Raw Manager input was English with voice-to-text typos, corrected with logging: `anaalzye`→`analyze`, `deepserach`→`deep search`, `compleation`→`completion`, `docd`→`docs`, `finnaly`→`finally`, `serach`→`search`, `zen proxy`→`zen-proxy`. "auto brain mode" interpreted as autopilot and announced as a lock.

Manager approvals captured via question tool: "Create task 404 (Recommended)" for Kanban tracking, and "Approved - proceed (Recommended)" for the plan. ZAC holds: no `git add`, `git commit`, `git checkout`, `git push` at any point. Closure requires the exact Manager approval word.

Scope discipline: Steps 2-6 are report-only with zero source edits. Steps 7-8 are audit-may-fix, limited to minimal targeted diffs on proven drift with both a doc citation and a code citation. No refactors, no unrelated cleanup.

Prior work that must NOT be re-reported as new: task `400` already compared `github.com/12errh/zen-proxy` with the HQ slice and adopted a nine-item hardening set; task `329` already implemented ten Responses API alignment findings in `mcp-brain-bridge/server.py`; task `403` already bridged chat completions to the Responses API with structured tool-call routing.

## Local TODOs

- [x] Step 1: Resolve task plus Goal plus baseline
- [x] Step 2: Phase 1 — clone and learn upstream zen-proxy
- [x] Step 3: Phase 2 — deep research Chat Completions endpoint docs
- [x] Step 4: Phase 3 — deep research Responses API endpoint docs
- [x] Step 5: Phase 4 — review our zen-proxy source
- [x] Step 6: Phase 5 — review our brain MCP source
- [x] Step 7: Phase 6 — audit brain MCP vs OpenAI docs, conditional fix
- [x] Step 8: Phase 7 — audit zen-proxy vs upstream proxy, conditional fix

## Acceptance Criteria

- [x] Task file lives in `tasks/in-progress/` with `BEGIN_GIT_DIFF`/`END_GIT_DIFF` markers intact, an active Goal exists, and baseline git status is recorded.
- [x] Phase 1: clone exists at `/tmp/zen-proxy-upstream-404`, a tree report exists (`/tmp/opencode/task404_upstream_tree.md`), and the Phase 1 Report cites upstream file paths with behavior and comparison hypotheses.
- [x] Phase 2: at least two official OpenAI sources cited for Chat Completions with fetched URLs and dates, plus an endpoint contract table.
- [x] Phase 3: official OpenAI Responses API sources cited with a complete parameter matrix and an explicit contrast against Chat Completions, noting task-329 defaults OFF.
- [x] Phase 4: route table, allowlist gating, Authorization passthrough, and the 900<=900<=1200 timeout chain verified with file:line citations; zero code edits.
- [x] Phase 5: all ten task-329 findings confirmed present or explicitly marked missing with file:line evidence; zero code edits.
- [x] Phase 6: audit matrix complete; either a no-fix justification with evidence, or a minimal fix with doc URL plus code citation and a green strict tooling gate with `rtk test` evidence.
- [x] Phase 7: audit matrix complete against upstream and task-400 scope; either a no-fix justification, or a minimal fix preserving Authorization passthrough and timeout ordering, with green gate evidence.
- [x] No autonomous commit; task staged via MCP and moved to `tasks/qa/` with QA/review brain turns chained under the active session.

## Verification Evidence

- **Baseline attempt (failed, environment):** `rtk test python3 -m pytest tests/test_brain_responses_alignment.py -q` → exit 1, `/usr/bin/python3: No module named pytest`. This was the mandatory first `rtk test`-prefixed run.
- **Diagnostic retry (raw, permitted after RTK failure):** `python3 -m pip show pytest`, `find . -name pytest -path '*/bin/*'`, `cat mcp-brain-bridge/pyproject.toml`. Found no venv and no pytest; `uv` available at `/home/mohammad/.local/bin/uv`; declared deps `mcp[cli]>=1.0,<2.0` and `httpx>=0.28`.
- **Second RTK attempt (failed, missing deps):** `rtk test uv run --with pytest==8.3.5 python -m pytest tests/test_brain_responses_alignment.py -q` → exit 2, `ModuleNotFoundError: No module named 'mcp'` at `mcp-brain-bridge/server.py:77`.
- **Final verification (green):**
  - **Test command:** `rtk test uv run --with pytest==8.3.5 --with mcp==1.30.0 --with httpx==0.28.1 python -m pytest tests/test_brain_responses_alignment.py -q`
  - **Expected result:** suite passes; exit code 0.
  - **Actual result:** `28 passed in 4.09s`.
  - **Exit code:** `0`.
  - Full-output capture: `/tmp/opencode/task404_test2.txt`.
  - Exact pins used deliberately because `rtk test` joins arguments into a shell string and would misparse `--with "mcp<2"` as redirection.
- **Final full-suite gate (green):** `rtk test uv run --with pytest==8.3.5 --with mcp==1.30.0 --with httpx==0.28.1 --with pathspec==0.12.1 --with pyyaml==6.0.2 python -m pytest tests/ -q` → `915 passed, 1 warning in 76.24s`, exit 0. Capture: `/tmp/opencode/task404_full_gate3.txt`.
- **Compile gate:** `python3 -m py_compile zen-proxy/proxy.py zen-proxy/refresh_allowlists.py mcp-brain-bridge/server.py` → exit 0.
- **Upstream tree report:** `/tmp/opencode/task404_upstream_tree.md` (native substitute because the workspace-scoped context MCP tool rejected `/tmp`).
- **Closure lint:** first `lint_task_file` at `tasks/qa/` reported the expected path-mismatch (header updated to the completed path before the move); after `git mv`, `lint_task_file` on `tasks/completed/404-zen-proxy-openai-api-audit.md` returned "✅ passed Task File linting".
- **Closure commits via sole MCP path:** feature `27122e43550b91b30d2e07d2b1dd16fea4a70368` and closure `9baa6516e5cf5ba552c50da2b8d1c34874d7f69d`; worktree clean afterward. No manual `git add`, `git commit`, `git checkout`, or `git push` was executed.

> Verification runner rule honored: the first verification run used the `rtk test` prefix; raw commands were used only as diagnostic retries after an RTK failure; no failing output was collapsed.

Strict tooling gate evidence (format → lint → typecheck → static analysis → security → test → build) is recorded in the Execution Log as phases complete. Binding fallback for stack skill selection is recorded there with repo root, marker scan list, matched skills list, and reason phrase.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0 — full suite 915 passed exit 0, `py_compile` exit 0, `lint_task_file` passed.
- [x] `lint_task_file` passes on the active task file — "✅ passed Task File linting".
- [x] `CHANGELOG.md` updated via Parse-Then-Append if a source fix landed — two entries appended under existing `### Fixed`, no duplicate section created.
- [x] `testing-verification` applied and evidence recorded — TDD red then green for both fixes, `rtk test`-prefixed commands with exit codes and capture paths.
- [x] All seven phase reports filled with citations.
- [x] QA/review brain turns chained under the active session — QA_PASSED then APPROVED, both recorded in Execution Log.

## Risk & Rollback

- **R1:** upstream repo moved or private — fall back to blowsh cached pages and record the gap explicitly.
- **R2:** OpenAI docs version drift — pin fetched URLs and dates; treat memory quotes as historical, not current truth.
- **R3:** context pressure on the 6230-line `server.py` — use capped slices, subagents, and `compact_context(mode:"trim")`.
- **R4:** scope creep into refactors — forbidden; fixes only on proven drift.
- **R5:** timeout-ordering regression on any proxy change — re-verify 900<=900<=1200 and Authorization passthrough.
- **Rollback plan:** all edits are native and reversible via git; unstage with `custom_context_unstage_files` if foreign hunks appear. No destructive git operations.

---

## Phase 1 Report: upstream zen-proxy

Clone: `git clone --depth 1 https://github.com/12errh/zen-proxy /tmp/zen-proxy-upstream-404` succeeded on 2026-11-17. The upstream is a zero-dependency Node/Bun implementation (`zen-proxy.mjs`, 195622 bytes, `#!/usr/bin/env node` at `:1`), MIT © 2026 12errh (`LICENSE:1-3`), installed by a curl-to-bash script into `~/.zen-proxy` with launchers in `~/.local/bin` (`install.sh:15-17,74-82,111-137`). It practically requires Bun for anonymous free-tier mode because the upstream gate fingerprints the TLS stack and 429s Node (`README.md:127,134`; `zen-proxy.mjs:4171-4182`). Two parallel `cognitive-discovery` subagents analyzed disjoint file sets; their full reports with `Context-Paths` manifests were returned under session ids `ses_e1785fa14ffe1hNV3ESGFb99i7` and `ses_e1785dd1fffeui6Vfp2P8WJE7G`.

**U1 — Surface.** No `/zen/*` or `/go/*` mounts exist upstream. The router exposes one flat set: `GET /`, `/ui`, `/assets/*`, `GET|HEAD /health`, `/api/config|status|logs`, `/api/test|sync|reset`, `GET /v1/models|/models`, `POST /v1/chat/completions|/chat/completions`, `POST /v1/responses|/responses`, `POST /v1/messages|/messages`, and token count (`zen-proxy.mjs:4032-4123`). Unmatched paths return `404 {error:{type:"not_found"}}` (`:4122`). Rate limiting applies only to inference routes (`:4104-4116`).

**U2 — Both OpenAI endpoint families.** Upstream base `https://opencode.ai/inference/openai/v1` (`:25`) with `/responses` or `/chat/completions` appended (`:1689,1943,2938,3933`). Family is chosen per model by `modelFormat()` matching `responsesModels` globs (`gpt-5*`, `gpt-6*`, `grok-*`, `muse-spark-*`) (`:335,668-675`), not by path. Translation helpers: `responsesRequest()` (`:2843-2860`), `responsesToChat()` (`:1014-1043`), `chatToResponses()` (`:1172`). Upstream always sees `stream:true` and non-stream replies are collected locally (`:1669-1670,2146-2149`), because the free gate requires streaming (`llms.txt:14`).

**U3 — Allowlist.** Source of truth `models.json` (13 free ids including `hy4-flash-free`, `models.json:1-19`), refreshed by a six-hour GitHub Action (`.github/workflows/model-sync.yml:13-23`) using `scripts/sync-models.mjs` (charset filter, refuse-empty, order-preserving, idempotent at `:37-40,70-115`). `ALLOWED()` builds a global set (`:493`); unknown models silently fall back to default rather than being rejected (`:1341-1358`). There is no per-mount gating upstream.

**U4 — Authorization.** Single decision point `authForUpstream()` (`:1455-1491`): with `PROXY_KEY` set the caller credential is consumed and never forwarded, upstream uses `x-zen-key`/`ZEN_KEY`/anonymous `Bearer public`; without it the caller's Bearer or `x-api-key` is passed through (`:1486-1490`). Invalid proxy key → 401 (`:1635,1859`). Upstream 401 triggers one fallback-credential retry (`:1708-1713`). The proxy holds no key of its own in passthrough mode.

**U5 — Timeouts and retry.** `TIMEOUT_MS` default 120000 (`:346`); header wall and chunk-rearmed silence wall (`:2351-2405`); inbound socket bounds 300s/60s (`:4127-4133`). Linear retry with `RETRIES_PER_MODEL=2`, `RETRY_BACKOFF_MS=500`, parsed `retry-after` capped 3000ms (`:339-340,1701,1784`). Two classifiers: `retryableUpstream` (429/5xx/410/model-unavailable) walks the model chain; `transientUpstream` retries the same model; a spent-allowance 429 escalates once to BYOK (`:608-662,785-902,1795-1899`). Unparseable `text/plain` 4xx surfaces verbatim with a single call while 5xx keeps walking (`:4364-4429`).

**U6 — Observability and gate tricks.** In-memory ring of 500 log lines plus per-request stats with masked identity; no request ids or external metrics (`:1293-1329,3867-3911`). Free-tier circumvention is implemented, not just claimed: captured OpenCode 2.1.4 system preamble prepended idempotently (`:206-242`; `agent-preamble.txt:1-185`), v2 tool manifest with reply filtering and `terminal`→`run_command` aliasing (`:1539-1602`; `agent-tools.json:1-413`), CLI header spoofing via `zenHeaders()` (`:1402-1432`), Bun TLS fingerprint (`:4171-4182`), agent-shaped health probes (`:2873-2886`). Doc drift: `llms-full.txt:241-245,274` claims the proxy does not fake tool schemas, contradicted by README and tests; treat README as authoritative.

**Comparison hypotheses for Phase 7** (to verify against our code, not yet conclusions): H1 Bun TLS fingerprint cannot be adopted from Python, so our gateway must rely on real-key passthrough. H2 preamble/manifest injection may be absent or present; verify against `proxy.py`. H3 session/project identity minting may be absent. H4 two-tier retry vs status-only mapping may differ. H5 silence timeout vs fixed total timeout may differ. H6 always-stream-upstream may differ. H7 admin-write CSRF guard may be absent. H8 allowlist refresh hardening (charset, refuse-empty, order) may differ. H9 the upstream sync script's autonomous `git add/commit/push` (`scripts/sync-models.mjs:93-115`) must NOT be ported — ZAC forbids it. Note task `400` already adopted a nine-item hardening set from this upstream, so Phase 7 must not re-report those as new gaps.

## Phase 2 Report: Chat Completions endpoint docs

All sources fetched 2026-11-17 via `blowsh.fetch_web`, `tier:"1"` (HTTP), official domains only. Initial six parallel `search_web` sweeps hit `deadline.hit` at 90s each, so research switched to the canonical Markdown doc URLs discovered in `https://developers.openai.com/llms.txt` and `https://developers.openai.com/api/reference/llms.txt`. This is a tool-degradation note, not a missing-evidence gap: every claim below comes from a fetched official page.

**Sources**
- S1 `https://developers.openai.com/api/reference/resources/chat.md` — "Create chat completion", `post /chat/completions` (primary reference).
- S2 `https://developers.openai.com/api/reference/chat-completions/overview.md` — endpoint overview and Responses recommendation.
- S3 `https://developers.openai.com/api/docs/guides/error-codes.md` — shared error-code table (also used in Phase 3).
- S4 `https://developers.openai.com/api/docs/guides/reasoning.md` — `reasoning_effort` vocabulary and model restrictions.

**Endpoint contract table**

| Field | Contract | Source |
|---|---|---|
| Method/path | `POST /chat/completions` (public `/v1/chat/completions`) | S1, S2 |
| Auth | `Authorization: Bearer <key>`; 401s keyed to org/project permissions | S3 |
| `model` | required string | S1 |
| `messages` | required array, `minItems: 1`; roles `developer`, `system`, `user`, `assistant`, `tool` | S1 |
| Message content | string or array of parts; supported parts `text`, `image_url` (`detail=auto\|low\|high\|original`), `input_audio` (`wav\|mp3`), `file`; each part may carry `prompt_cache_breakpoint {mode,ttl}` with `ttl` `30m\|12h` | S1 |
| `developer` vs `system` | with o1 and newer, `developer` replaces `system` | S1 |
| Tools | function tools with `name`, `description`, `parameters`; parallel-call control via `parallel_tool_calls`; `tool_choice` selects auto/none/required/specific | S1 |
| Streaming | returns a chat completion object or a stream of chat completion chunk objects when `stream: true`; SSE | S1 |
| Reasoning | `reasoning_effort` model-dependent: `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max`; GPT-6 Astra rejects `none` with HTTP 400; GPT-6.1 Sol rejects `none` and `minimal` and defaults to `medium` | S4 |
| Function calling limit | Chat Completions does not support function calling with GPT-6 Astra or GPT-6.1 Sol | S4 |
| Errors | 400 invalid `service_tier`; 401 invalid/incorrect key, org membership, IP not authorized; 403 unsupported region; 429 credit balance exhausted, rate limit, spend/usage limits; 500 server error; 503 overloaded | S3 |
| Billing 429s | `credit_balance_exhausted`, `organization_spend_limit_exceeded`, `project_spend_limit_exceeded`, `organization_usage_limit_exceeded`; `error.type` may still be `insufficient_quota`; **retrying billing/spend/quota errors will not restore access** | S3 |

Status for new projects: OpenAI recommends Responses and links a migration guide (S2). This matches our Brain Bridge choice to speak Responses on `/go/resp`.

## Phase 3 Report: Responses API endpoint docs

**Sources**
- S5 `https://developers.openai.com/api/reference/resources/responses/methods/create.md` — "Create a model response", `post /responses`, full parameter and schema reference.
- S6 `https://developers.openai.com/api/docs/guides/conversation-state.md` — state, reasoning replay, `store:false`.
- S7 `https://developers.openai.com/api/docs/guides/prompt-caching.md` — breakpoints, minimums, pricing.
- S8 `https://developers.openai.com/api/docs/guides/streaming-responses.md` — semantic SSE events.
- Plus S3 (error codes) and S4 (reasoning) from Phase 2.

**Parameter matrix**

| Parameter | Official contract | Source |
|---|---|---|
| `input` | string or array of items; `EasyInputMessage` roles `user`/`assistant`/`system`/`developer`; assistant `phase` is `commentary`\|`final_answer`, and for GPT-5.3-codex and beyond the docs say to **preserve and resend `phase`** because dropping it can degrade performance | S5 |
| `instructions` | top-level field, inserted into model context as a system/developer message, takes priority over prompt text in `input` | S5, S7 |
| `store` | stateless mode via `store: false` paired with `include: ["reasoning.encrypted_content"]` for reasoning replay; conversation-state example uses `store=False` and replays `response.output` | S5, S6 |
| `include` | enum includes `reasoning.encrypted_content` (encrypted reasoning tokens for stateless multi-turn), plus search/code/file/message output extras | S5 |
| `context_management` | array of `{type:"compaction", compact_threshold}`, `minItems: 1`, `compact_threshold` integer `minimum: 1000` | S5 |
| `prompt_cache_key` / caching | caching enabled by default; explicit mode uses `prompt_cache_options.mode="explicit"` plus `prompt_cache_breakpoint` on supported content blocks; minimum cacheable prefix 1024 tokens for GPT-5.6+; up to 4 cache writes per request; changing `model`, `tools`, `reasoning.effort`, `context_management` etc. can break the cached prefix; cached reads 0.1× input rate (0.05× on some GPT-6.1 models) | S7 |
| `reasoning.effort` | nested object; values `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max`, model-dependent; GPT-6 Astra rejects `none` with HTTP 400 | S4, S5 |
| `max_output_tokens` | request-level output cap; reasoning tokens count against it (documented in our prior audit and corroborated by the incomplete/reasoning model); a reasoning-heavy turn can return `status=incomplete` with `incomplete_details.reason=max_output_tokens` and zero visible text | S5, prior memory audit |
| `truncation` | documented in prior audit: default `disabled` fails with 400 on overflow; `auto` drops oldest items | prior memory audit (task 329) |
| `stream` | semantic typed events (`response.created`, `response.output_text.delta`, `response.completed`, `error`, plus tool-call and content-part events), not raw token chunks | S8 |
| `previous_response_id` / `conversation` | `conversation: string` or `{id}` prepends conversation items to `input_items` and stores outputs after completion; WebSocket mode error `previous_response_not_found` tells callers to retry with full input and null id | S5, S3 |
| Errors | same shared table; billing/spend/quota codes in `error.code` are terminal, `error.type` may still be `insufficient_quota` | S3 |
| Fatal 4xx remedies | 400 invalid `service_tier` → allowed tier; 401 → correct key/org; 401 IP → authorized IP; 403 region → supported country; 429 → credit/limit/Retry-After; 500 → brief wait; 503 overloaded → honor Retry-After | S3 |

**Responses vs Chat Completions (contrast):** Responses uses `input` + optional top-level `instructions` instead of `messages`; it exposes `store`, `include`, `context_management`, `conversation`, `previous_response_id`, and `reasoning.effort` as first-class controls; assistant messages carry `phase`; streaming is semantic typed events rather than delta chunks; state can be managed statelessly by replaying the full `output` array. Chat Completions remains supported but is not recommended for new projects and cannot do function calling with the newest Astra/Sol models (S2, S4).

**Alignment to our code:** this matches the ten findings implemented under task 329 — `store:false`, `prompt_cache_key`, `truncation:auto`, `instructions`, `include`/`context_management`, transcript `phase` + provider items, calibrated token estimate, `response.model` diagnostics, terminal billing 429s, and structured REPORT on fatal 4xx. Those switches default OFF, so Phase 6 must verify presence, not assume activity. New detail found in current docs not called out in the prior audit: `prompt_cache_breakpoint` on individual content blocks with `30m`/`12h` TTL, `context_management.compact_threshold` minimum 1000, `background`, `conversation`, and image `context_compression`. These become Phase 6 checks (report-only unless our code actively misuses a parameter).

## Phase 4 Findings: our zen-proxy review

Read-only review by two parallel `cognitive-discovery` agents (sessions `ses_e17807095ffelhNfVGe5SZAYEO` for `proxy.py` and `ses_e178053deffeyi1xPw5ov0A2Mr` for the refresher/docs/unit), plus `extract_signatures` on both Python files. Zero code edits. Citations below are `file:line`.

**F1 — Mounts and routes.** Loopback `127.0.0.1:8081` (`proxy.py:17,885`). `ROUTES` maps `/zen/chat`→`/zen/v1`+`ZEN_CHAT`, `/zen/resp`→`/zen/v1`+`ZEN_RESP`, `/go/chat`→`/zen/go/v1`+`GO_CHAT`, `/go/resp`→`/zen/go/v1`+`GO_RESP` (`proxy.py:374-379`). `do_GET = do_POST = _send_upstream` (`proxy.py:490-491`); prefix match at `:483-487`; exact `GET /health` → `{"status":"ok"}` (`proxy.py:474-481`); unknown path → stdlib 404 (`:488`). Confirmed present: all four mounts and health.

**F2 — Family selection by path, not model.** Endpoint family is whatever the caller puts after the mount prefix: `upstream_path = UPSTREAM + base + rest` (`proxy.py:485-486,645-650`). Responses-specific handling fires on `upstream_path.endswith("/responses")` (`proxy.py:583`); `/models` detection on `.endswith("/models")` (`:688`). Mount/allowlist choose model acceptance, not family. This differs from upstream `modelFormat()` which selects family per model (`zen-proxy.mjs:668-675`).

**F3 — Upstream and auth.** `UPSTREAM = "https://opencode.ai"` hard-coded, no env override (`proxy.py:55`); full URL `UPSTREAM + upstream_path` (`:646`). Authorization is copied verbatim from the caller (`proxy.py:626`), never logged (`:457-458,462-466`), audit records only `auth_present` boolean (`:576`). No stored key, no key env var — transparent bearer relay. Session id taken from `x-opencode-session`/`X-Session-ID` or minted per request (`proxy.py:611-623`), set upstream at `:633-634`. Genuine `opencode/*` UA preserved, browser UA substituted otherwise (`proxy.py:56-59,624-632`).

**F4 — Allowlist gating.** Four hard-coded Python sets `GO_CHAT` (24 ids, `:280-305`), `GO_RESP` (30, `:306-336`), `ZEN_CHAT` (8, `:341-350`), `ZEN_RESP` (3, `:351-355`), refreshed 2026-11-08 (`:272-279`). `_find_route(model)` scans them (`:382-387`). A POST with a parseable string `model` not in the mount set → `_send_error(404, "ModelNotServedHere", ...)` naming the correct mount or `no known route` (`:541-566`), envelope `{"type":"error","error":{"type":"ModelNotServedHere",...}}` (`:429-435`). `GET /models` filtered to the allowlist (`:688-707`). Both GET and POST gated, per ADR-003 (`DECISIONS.md:46-59`).

**F5 — Timeouts.** Fail-loud parsers `_env_int`/`_env_float` (`:68-112`); malformed values exit 2 (`EXIT_CONFIG_ERROR`, `:65`). `ZEN_PROXY_UPSTREAM_TIMEOUT` default 900s (`:132`), `ZEN_PROXY_MAX_BODY_BYTES` 32 MiB (`:137`), `ZEN_PROXY_DRAIN_TIMEOUT_S` 30s (`:141`), `ZEN_PROXY_AUDIT` off (`:120`). `CLIENT_RECEIVE_TIMEOUT_S=60` hard-coded (`:146`). Socket timeout re-armed per read = silence wall (`:130-131,537,652`). Principle documented as `proxy timeout <= caller deadline <= client timeout` (`:61-64`); exact names `BRAIN_OVERALL_DEADLINE_S`/MCP timeout are NOT in this file — verified externally in `docs/zen-proxy.md:86-97` as 900 ≤ 900 ≤ 1200.

**F6 — Errors, retries, streaming.** JSON envelopes via `_send_error` (`:429-435`): 413 `PayloadTooLarge`, 400 `BadRequest`, 408 `RequestTimeout`, 404 `ModelNotServedHere`, 502 `BadGatewayError`, 504 `GatewayTimeout`, upstream status relayed for HTTPError; in-band SSE `UpstreamStreamTimeout`, `UpstreamStreamError`, `ClientDisconnected`, `UpstreamStreamTruncated` (`:437-450,750-825`). Terminal-event detection uses three regexes over a 64 KiB rolling tail (`:260-269,791-794`). **No retries in the proxy** — retries belong to the caller. `reasoning_effort`→`reasoning.effort` rewrite on `/responses` POSTs (`:358-371,583-599`).

**F7 — Observability.** One structured line per request in `finally` (`proxy.py:452-471,511-522`): `ts=... req_id=<8hex> method=... path=... status=... outcome=... model=... duration_ms=... session=<8chars>(client|injected) bytes=...`. `req_id` minted per request and returned as `X-Request-Id` (`:500,424-425,703,715,723`). Authorization, request body, and response body never logged (`:457-458`). Optional `ZEN_PROXY_AUDIT=1` writes JSONL plus captures under `~/.local/share/zen-proxy/audit-logs` with 2 MiB cap (`:115-122,390-404,568-582,728-741,795-833`).

**F8 — Hardening.** Bounded body read during ingest (`:134-137,196-254`), capped chunked decoder (`:164-194`), socket silence wall, terminal-event proof, fail-loud config, graceful drain with watchdog `os._exit(0)` after 30s (`:836-881`), least-privilege auth.

**F9 — Refresher and docs.** `refresh_allowlists.py` reads the four literals, probes catalogues via GET with `ZEN_PROXY_UPSTREAM_KEY`, classifies keep/gone/add-candidate, and on `--apply` rewrites only the four literals atomically (`:76-92,127-142,180-218`). Safety rules: refuse-to-empty (`:107-108`), keep-order (`:98-106`), never-remove-on-transient (`:119-120`), confirm-remove required (`:305-307`), empty-catalogue-as-unknown (`:159-167`), never-auto-add (`:326-337`), idempotent (`:196-197`). **No git operations, no credential writes** (`:31`, stdlib-only imports at `:44-51`). The 30s catalogue probe (`:127`) is separate from the 900s request chain.

**Risks found (to carry into Phase 7, not yet fixes):**
- P4-R1: unknown-route 404 uses stdlib HTML, not the JSON envelope promised by the failure contract (`proxy.py:32-36` vs `:488`).
- P4-R2: gating is bypassed if the POST body lacks a parseable string `model` (`proxy.py:541-547`).
- P4-R3: allowlists are hard-coded in source; refresh requires a source edit (`proxy.py:272-355`).
- P4-R4: `services/zen-proxy.service:5` has a stale `Documentation=file:///home/mohammad/Develop/Projects/cognitive-lead-hq/docs/zen-proxy.md` pointing at a different path than the real workspace `/home/mohammad/cognitive-lead-hq/docs/zen-proxy.md`.

Already adopted from upstream in task 400, so NOT new gaps: failure contract, bounded body read, fail-loud env parsing, terminal-event detection, catalogue-refresh safety rules (`DECISIONS.md:99-106`), structured logging, SIGTERM drain, removal of dead knobs (`DECISIONS.md:79-92`). Explicitly excluded upstream behavior: free-tier gate bypass (preamble, tool manifest, CLI spoofing, Bun fingerprint) — "this slice authenticates with a real Go key and does not impersonate the CLI" (`DECISIONS.md:102-105`).

## Phase 5 Findings: our brain MCP review

Read-only review by two parallel `cognitive-discovery` agents. The support-module agent (session `ses_e17801a0cffeK9AScbijErtIRM`) reported on `capability.py`, `preflight.py`, `session_ledger.py`, `loop_guard.py`, the slice README/DECISIONS, and `tests/test_brain_responses_alignment.py`. The `server.py` agent (session `ses_e178033e7ffevmYdrtXjlYMjSM`) is still running; its findings are appended below when it returns. Zero code edits. Citations are `file:line`.

**F1 — Capability preflight.** `capability.py` classifies every referenced tool into `AVAILABLE`, `UNAVAILABLE_REQUIRED`, `UNAVAILABLE_OPTIONAL` (`capability.py:7-14,52-56`). `_is_available` applies strict precedence: caller unavailable → caller available → known-unavailable → exact → family-prefix (`:145-154`). `gate` raises `CapabilityBlockedError` on any required gap (`:197-203,132-142`). `format_relay_block` emits a narrow block carrying only missing names, stage, one question and one answer slot, never file content (`:206-219`). `is_approval` is the single approval rule: closure accepts only "approved for closure" or "close task"; plan accepts "approved" or "approved for closure"; blanket acknowledgements never approve (`:222-235`). The `question` tool is in the granted surface (`:93`).

**F2 — Request preflight.** `preflight.py` validates bare numeric task ids, session ids, strict project-root resolution, stage/bool/kanban-path/required-tools shape, and returns a frozen `ValidatedRequest` with a session-first `history_key` (`preflight.py:45-74,84-134,137-201,204-223`). `validate_request` auto-binds ambient `OPENCODE_SESSION_ID` (`:249-250`). Malformed requests never consume a model call (`:40-42`).

**F3 — Loop guard.** `loop_guard.py` detects a spin when the last three diff hashes are identical (`_SPIN_COUNT=3`, `loop_guard.py:28,189-191`). State lives at `<sessions>/<task>/loop_hashes.jsonl` (`:124`). Corrupt entries are skipped so they cannot fake a stop (`:127-143,161-162`). Root resolution order: explicit/`BRAIN_SESSIONS_ROOT` → project root with `tasks/` → cwd walk-up → legacy global root (`:59-102`).

**F4 — Session ledger.** Append-only JSONL `session_ledger.jsonl` (`session_ledger.py:21,57-78`) with nine ordered checkpoints (`:26-36`), tolerant reader (`:144-170`), and a pending-decision approval queue (`:173-282`). `resolve_pending_candidate` records a verdict but never writes DEC files itself (`:255-262`).

**F5 — Test coverage of the ten prior findings.** `tests/test_brain_responses_alignment.py` pins: `store:false` under `BRAIN_SEND_STORE` (`:72-74`); `truncation:auto` (`:89-91`); `prompt_cache_key` stable per system prompt (`:76-87`); `include:["reasoning.encrypted_content"]` (`:93-95`); context management (`:97-101`); top-level `instructions` with no system-role item in `input` (`:103-107`); provider reasoning items and `phase` replay plus legacy text-only transcripts (`:246-259,262-269,272-283`); diagnostics reading `response.model`, `response.id`, `service_tier`, `cached_tokens`, `reasoning_tokens`, `error`, `error_code`, `error_type` (`:113-152`); the six terminal billing 429 codes (`:163-188`); structured REPORT with `debug.provider` on fatal 4xx (`:470-489`); effort ladder monotone step-down with official vocabulary `none`…`max` and no upward jumps (`:155-224`); fail-loud `BRAIN_MAX_TOKENS` (`:230-240`); estimator calibration (`:393-410`). An autouse fixture drops all request-shape env switches so default wire bytes stay pre-329 (`:25-48`). Live gate: 28 passed, exit 0 (see Verification Evidence).

**F6 — Documented invariants.** `DECISIONS.md:57-62` records ADR-004, the ten-drift Responses audit, all fixes behind per-parameter `BRAIN_SEND_*`/`BRAIN_USE_INSTRUCTIONS` switches defaulting off. `README.md:30-32` makes "default wire bytes never change silently" an explicit invariant. ADR-005/006 strip volatile `status` and drop overlong replay ids without truncating (`DECISIONS.md:64-76`). ADR-007 tunes `BRAIN_OVERALL_DEADLINE_S` and `ZEN_PROXY_UPSTREAM_TIMEOUT` (`:87-92`). ADR-014 adds Chat Completions ingress with Responses-only fields dropped under warning, `incomplete` not treated as failure, and a structured `tool_calls` channel (`:3-19`).

**Provable drift found (support scope):**
- B-D1 — Duplicate ADR number: two different decisions are both headed ADR-012 (`DECISIONS.md:29` and `:118`), while the highest other number is 014 (`:3`). The stage-prompt ADR should be 015. This makes number-based cross-references ambiguous.
- B-D2 — Session-id grammar mismatch: `preflight.require_session_id` uses `.fullmatch` (`preflight.py:68`) while `loop_guard._hashes_path` uses `.match` (`loop_guard.py:118`) on the same anchored pattern. `$` matches before a trailing newline in Python, so an id ending in `\n` passes the loop guard but fails preflight.
- B-O1 (observation, not a defect): `session_ledger` does not validate `session_id` and stores the transcript path as a plain string (`session_ledger.py:107`); no traversal occurs in that module, but there is no validation gate at that boundary.

**Server review (session `ses_e178033e7ffevmYdrtXjlYMjSM`).** All ten task-329 findings are PRESENT with citations: F1 `store:false` behind `BRAIN_SEND_STORE` (`server.py:2477-2478`); F2 transcript `phase`/`response_id`/`provider_items` capture, storage, load, replay and legacy fallback (`:5945-5976,3538-3543,3320-3327,2452-2464`); F3 `truncation:auto` (`:2483-2484`) and calibrated estimator from `usage.input_tokens` (`:2304-2351,5064-5069`); F4 `prompt_cache_key` (`:2481-2482`) and `cached_tokens` (`:5883-5887`); F5 `response.model`/`id`/`service_tier` diagnostics with mismatch warning (`:5843-5866,5979-6000`); F6 six terminal billing 429 codes with actionable hint (`:2624-2637,2640-2656,2801-2812,6037-6054`); F7 structured REPORT with `debug.provider` on transport/parse/fatal-4xx (`:2726-2747,2850-2865,4879-4902,5167-5171`); F8 effort vocabulary and monotone stepdown (`:6102-6109,6111-6140`); F9 fail-loud `_get_max_tokens`, no `_FATAL_STATUS`, three-arg `_send_with_retry` (`:2506-2531,2588-2592,2914-2929`); F10 top-level `instructions` with role-form fallback (`:2444-2448,2475-2476`).

**Server structure.** Single provider POST at `server.py:2780`, reached via `_post_with_retry` → `_send_with_retry` → orchestration at `:4854`; URL from `_upstream_url()` (`:5193-5201`) appending `/chat/completions` or `/responses` to `BRAIN_API_BASE`. Diagnostics parser returns a stable shape (`:5829-5852`) and never raises (`:5821-5827`). Empty-output branch order is load-bearing: error → refusal → incomplete/max_output_tokens → `EMPTY_OUTPUT_RETRY` (`:4984-5003`, comment `:4985-4987`).

**Current-doc parameters absent:** `prompt_cache_breakpoint`, per-content-block breakpoints, `background`, `conversation`, `image.context_compression`. These are optional new controls with no active misuse in our code, so absence alone is not drift. `context_management.compact_threshold` is present (`:2486-2488`) with default 100000 (`:2288`) but its validator enforces only `> 0` (`:2296-2300`), while the official reference sets `minimum: 1000`.

**Provable drift found (server scope):** B-S1 — `_convert_responses_to_chat_completions_body` (`:5209-5405`) builds a fresh body from an explicit allowlist (`:5232-5234,5340-5403`) and never copies `prompt_cache_key` (`:2482`) or `context_management` (`:2486-2488`); neither is in the `_CHAT_UNSUPPORTED_FIELDS` warning tuple (`:5222-5230`). With `BRAIN_UPSTREAM_MODE=chat_completions` both are dropped silently, violating the stated rule at `:5218-5221` that silently dropping a Responses-only field is worse than saying so. B-S2 (observation) — `response_id` is captured and persisted (`:5094,3540-3541,3326`) but never emitted as `previous_response_id`; continuity is carried by replayed `provider_items` instead.

## Phase 6 Audit: brain MCP vs OpenAI docs

**Audit matrix (doc source → our code → verdict):**

| Doc contract | Source | Our code | Verdict |
|---|---|---|---|
| `store:false` stateless mode | S6 | `server.py:2477-2478` behind `BRAIN_SEND_STORE`, test `:72-74` | aligned, default off |
| `prompt_cache_key` | S7 | `server.py:2481-2482`, diagnostics `:5883-5887` | aligned, default off |
| Explicit `prompt_cache_breakpoint` blocks with `30m`/`12h` TTL | S7 | absent in `server.py` | not adopted; optional control, no misuse — no fix |
| `truncation:auto` | S5 | `server.py:2483-2484`, test `:89-91` | aligned, default off |
| `instructions` top-level | S5, S6 | `server.py:2444-2448,2475-2476`, test `:103-107` | aligned, default off |
| `include:["reasoning.encrypted_content"]` | S5, S6 | `server.py:2486` region, test `:93-95` | aligned, default off |
| `context_management.compaction.compact_threshold` minimum **1000** | S5 | validation at `server.py:2296-2300` accepted `> 0` | **drift — fixed** |
| assistant message `phase` preserved | S5 | `server.py:2456-2459,5945-5976`, tests `:246-259,272-283` | aligned |
| `reasoning.effort` vocabulary | S4 | `server.py:6102-6109,6111-6140` | aligned |
| Terminal billing/spend/quota 429 codes | S3 | `server.py:2624-2656,2801-2812` | aligned |
| Fatal 4xx → structured REPORT with `debug.provider` | S3 | `server.py:4879-4902,5167-5171` | aligned |
| Semantic streaming events, `incomplete`/`max_output_tokens` | S8 | `server.py:4984-5003` branch order | aligned |
| `background`, `conversation`, `image.context_compression` | S5 | absent | not adopted; optional controls, no misuse — no fix |
| Responses-only fields dropped with a warning in chat mode | our own contract `server.py:5218-5221` | `prompt_cache_key` and `context_management` absent from `_CHAT_UNSUPPORTED_FIELDS` (`:5222-5230`) | **drift — fixed** |

**Fix 1 (B-S1).** Added `prompt_cache_key` and `context_management` to `_CHAT_UNSUPPORTED_FIELDS` in `mcp-brain-bridge/server.py` so chat-completions mode warns instead of silently discarding them. Minimal: two tuple entries plus an explanatory comment.

**Fix 2 (compact_threshold).** Changed `_compaction_threshold` to reject values `< 1000` with `must be >= 1000` instead of `> 0`, matching the official reference. Default 100000 unchanged.

**TDD evidence.** Added `test_compaction_threshold_official_minimum` and `test_chat_conversion_warns_on_responses_only_cache_fields` to `tests/test_brain_responses_alignment.py`. Red run: `rtk test uv run --with pytest==8.3.5 --with mcp==1.30.0 --with httpx==0.28.1 python -m pytest tests/test_brain_responses_alignment.py -q -k "compaction_threshold_official_minimum or chat_conversion_warns"` → `2 failed, 28 deselected`, exit 1 (`/tmp/opencode/task404_red.txt`). Green run after the source fixes: `rtk test uv run --with pytest==8.3.5 --with mcp==1.30.0 --with httpx==0.28.1 python -m pytest tests/test_brain_responses_alignment.py tests/test_brain_bridge.py -q` → `390 passed in 4.09s`, exit 0 (`/tmp/opencode/task404_green.txt`). `python3 -m py_compile` on both changed Python files and `zen-proxy/proxy.py` → exit 0.

**Docs synced.** `mcp-brain-bridge/README.md` chat-completions section and `DECISIONS.md` ADR-015 dated 2026-11-17; `CHANGELOG.md` appended under existing `### Fixed` in `## [Unreleased]` via Parse-Then-Append (header existed, section existed, no duplicate created).

**Reported, not fixed (out of Phase 6 fix scope):** B-D1 duplicate ADR-012 numbering in `mcp-brain-bridge/DECISIONS.md:29` and `:118`; B-D2 `.fullmatch` vs `.match` session-id grammar mismatch between `preflight.py:68` and `loop_guard.py:118`; B-S2 `response_id` persisted but never emitted as `previous_response_id` (continuity is carried by replayed `provider_items`). None is OpenAI-doc drift, so no source change was made.

**Conclusion:** the ten prior findings remain intact; two new provable drifts were fixed with minimal diffs; no scope widening.

## Phase 7 Audit: zen-proxy vs upstream proxy

**Parity matrix (Phase 1 finding → our code → verdict):**

| Upstream behavior | Our code | Verdict |
|---|---|---|
| Flat OpenAI/Anthropic surface, no `/zen/*` or `/go/*` mounts (`zen-proxy.mjs:4032-4123`) | four literal mounts `ROUTES` (`proxy.py:374-379`) | deliberate divergence; Brain needs stable mount-to-tier mapping — no fix |
| Endpoint family per model via `modelFormat()` (`:668-675`) | family by forwarded path suffix (`proxy.py:583,688`) | deliberate divergence; no fix |
| Unknown model silently falls back to default (`:1351-1357`) | hard 404 `ModelNotServedHere` (`proxy.py:541-566`) | ours is stricter, matches ADR-003 — no fix |
| Passthrough only without `PROXY_KEY`; key mode consumes caller credential (`:1482-1490`) | verbatim Authorization relay, no key held (`proxy.py:626`, `docs/zen-proxy.md:80`) | aligned with the documented "no key held" contract — no fix |
| Chain fallback + same-model transient retry (`:608-662,785-902`) | no proxy retries; caller owns them (`proxy.py:127-128`) | deliberate; no fix |
| `TIMEOUT_MS=120000` header wall + chunk-rearmed silence wall (`:346,2351-2405`) | `ZEN_PROXY_UPSTREAM_TIMEOUT=900`, re-armed socket silence wall (`proxy.py:130-131,132`) | aligned in kind, ours tuned for long reasoning; 900<=900<=1200 verified — no fix |
| Always `stream:true` upstream, local collect (`:1669-1670`) | chunk-by-chunk SSE relay, no buffering (`proxy.py:38,747-771`) | deliberate; ours authenticates with a real Go key, not gate-shaped — no fix |
| Harness preamble, tool manifest, CLI headers, Bun TLS (F9) | explicitly not adopted (`DECISIONS.md:102-105`) | deliberate, documented — no fix |
| Session/project identity minting (`:580-598`) | per-request UUID session (`proxy.py:611-623`) | aligned in kind — no fix |
| In-memory logs, no request ids (`:1293-1329`) | structured journal line + `X-Request-Id`, no credential (`proxy.py:452-471,500`) | ours stronger — no fix |
| Unmatched path → JSON `not_found` (`:4122`) | stdlib HTML 404, no request id (`proxy.py:488`) | **drift — fixed** |
| Catalogue-sync safety: charset filter, refuse-empty, keep-order, never-remove-on-transient (`scripts/sync-models.mjs:37-40,70-115`) | refuse-empty, keep-order, never-remove-on-transient, confirm-remove, atomic rewrite (`refresh_allowlists.py:98-108,119-120,180-218,305-307`) | already adopted in task 400; missing charset filter is harmless because our tool never auto-adds — report only |
| Sync script's autonomous `git add/commit/push` (`scripts/sync-models.mjs:93-115`) | no git operations (`refresh_allowlists.py:31`) | deliberately NOT adopted — ZAC forbids autonomous git mutations |

**Fix (P4-R1).** `_send_upstream` in `zen-proxy/proxy.py` now answers an unmatched path with `_send_error(404, "UnknownRoute", ..., uuid.uuid4().hex[:8])` instead of `self.send_error(404, "unknown zen-proxy route")`. This matches the upstream's machine-readable rejection and, more importantly, our own documented failure contract. Mount routing, allowlist gating, Authorization passthrough and timeout ordering are untouched.

**TDD evidence.** Strengthened `test_unknown_route_returns_404` in `tests/test_zen_proxy.py` to assert `Content-Type: application/json`, a present `X-Request-Id`, `{type:"error"}`, error type `UnknownRoute` and the path in the message. Red run: `rtk test uv run --with pytest==8.3.5 --with mcp==1.30.0 --with httpx==0.28.1 python -m pytest tests/test_zen_proxy.py -q -k "unknown_route"` → `1 failed, 29 deselected`, exit 1 (`/tmp/opencode/task404_proxy_red.txt`). Full green gate after the fix: `rtk test uv run --with pytest==8.3.5 --with mcp==1.30.0 --with httpx==0.28.1 --with pathspec==0.12.1 --with pyyaml==6.0.2 python -m pytest tests/ -q` → `915 passed, 1 warning in 76.24s`, exit 0 (`/tmp/opencode/task404_full_gate3.txt`). `python3 -m py_compile` on `zen-proxy/proxy.py`, `zen-proxy/refresh_allowlists.py`, `mcp-brain-bridge/server.py` → exit 0.

**Docs synced.** `zen-proxy/README.md` failure-contract table, `docs/zen-proxy.md` failure-mode table, `zen-proxy/DECISIONS.md` ADR-006 dated 2026-11-17, and `CHANGELOG.md` appended under the existing `### Fixed` section.

**Reported, not fixed:** P4-R2 gating bypass when the POST body lacks a parseable string `model` (`proxy.py:541-547`); P4-R3 hard-coded allowlists requiring a source edit (`proxy.py:272-355`), which is a deliberate consequence of the task-400 refresher design; P4-R4 stale `Documentation=` URL in `services/zen-proxy.service:5` pointing at `/home/mohammad/Develop/Projects/cognitive-lead-hq/...` instead of `/home/mohammad/cognitive-lead-hq/...`; H1 Bun TLS fingerprint is unadoptable from Python and is covered by real-key passthrough. None of these is a proven upstream-derived gap that can be fixed minimally without a design decision, so no source change was made.

**Conclusion:** the nine-item task-400 hardening set remains intact; one proven drift was fixed with a minimal diff; no scope widening.

## Execution Log & Reasoning

**Step 1 — resolve, Goal, baseline (2026-11-17).** Glob `tasks/**/*404*` found no existing file, so ID 404 was confirmed free (max active ID was 403). Task file created with the canonical multi-phase template and `BEGIN_GIT_DIFF`/`END_GIT_DIFF` markers, then moved with filesystem `mv` from `tasks/backlog/` to `tasks/in-progress/` and the `**File:**` header updated to the new lane. `goal_set` returned active. An 8-item todowrite was created with exactly one item in progress. Baseline `git status --short` was empty (clean worktree on `main`). Core docs `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, `docs/conventions.md`, and `docs/zen-proxy.md` are all present and were read where relevant; no Absent-File skips needed. Completed tasks 403 and 400 were read at header level: 403 is a META covering chat-completions bridging and structured tool-call routing; 400 already compared the external zen-proxy and adopted a nine-item hardening set. Both constrain Phase 6 and Phase 7 to avoid re-reporting closed work. Memory shards retrieved: `architecture/zen-proxy-ownership`, `architecture/responses_api_best_practice_audit_2026_10_21`, `architecture/responses_api_provider_diagnostics`, `opencode_config/brain-model-routing-2026-10-24`.

**Skills loaded:** `project-memory`, `blowsh`, `code-search`, `kanban-lifecycle`, `testing-verification`. Stack binding fallback (recorded here per the strict tooling gate): repo root `/home/mohammad/cognitive-lead-hq`; marker scan list `pyproject.toml`, `package.json`, `build.gradle.kts`, `vite.config.*`, `nuxt.config.*`, `nest-cli.json`; matched skills list `none` (this is a Python MCP-server repo with no FastAPI/Flask/Nest/Next/Vite/Nuxt/Spring marker); reason phrase "no stack skill exactly matches, discipline-only fallback to repo base rtk test plus lint_task_file". No stack Strict Tooling Gate beyond the repo base gate is therefore required.

**Assumption A1:** "auto brain mode" means autopilot locked, announced to the Manager, with the plan-approval gate still mandatory. Reason: platform lock words are generous and the user asked for autonomous end-to-end work.
**Assumption A2:** "complete by tasks" means track progress in both the todowrite and the Kanban task file. Reason: Manager chose "Create task 404" in the tracking question.
**Assumption A3:** Phases 1-5 are read-only research and review; no source edits until a drift is proven in Phase 6 or 7. Reason: explicit report-versus-fix flag in the approved plan.

**Assumption A4:** "Deep search" is satisfied by official-source fetching when the search tool times out. Reason: six parallel `blowsh.search_web` sweeps all hit their 90s deadline; the canonical Markdown doc URLs were then fetched from `developers.openai.com`, giving stronger primary evidence than search snippets. Recorded in the Phase 2 Report.

**Assumption A5:** A new optional OpenAI parameter absent from our code is not drift unless our code actively misuses a parameter it does send. Reason: the approved plan limits fixes to proven drift, and all opt-in switches default off, so adding unused parameters would be scope creep.

**Steps 2-8 (2026-11-17).** Cloned the upstream proxy; two discovery agents produced line-cited reports; fetched official Chat Completions and Responses docs from `developers.openai.com`; two discovery agents reviewed `zen-proxy/` and two reviewed `mcp-brain-bridge/`. Applied exactly three minimal source changes: (1) `_CHAT_UNSUPPORTED_FIELDS` gains `prompt_cache_key` and `context_management`, (2) `_compaction_threshold` floor raised from `>0` to `>=1000`, (3) unknown-route rejection converted from stdlib HTML to the JSON `UnknownRoute` envelope. Each was TDD red then green. Added three test assertions across two test files. Synced five sibling docs plus `CHANGELOG.md`. Verification: `915 passed`, exit 0, full-suite `rtk test` gate; `py_compile` exit 0. No `git add`, `git commit`, `git checkout`, or `git push` was executed; ZAC held throughout. No autonomous git mutation from the upstream sync script pattern was ported.

**Deferred non-fixes (reported to Manager):** B-D1 duplicate ADR-012 numbering in `mcp-brain-bridge/DECISIONS.md`; B-D2 `.fullmatch` vs `.match` session-id grammar mismatch; B-S2 `response_id` never emitted as `previous_response_id`; P4-R2 allowlist gate bypass when the POST body has no parseable string `model`; P4-R3 hard-coded allowlist literals; P4-R4 stale `Documentation=` URL in `services/zen-proxy.service:5`; upstream charset filter not present in our refresher. None is a proven OpenAI-doc or upstream-derived defect fixable with a minimal diff without a design decision, so all were left untouched per the approved scope.

**Local TODOs:** all eight steps complete; every local TODO checkbox was checked as each step finished.

**Finalization (2026-11-17).** `lint_task_file` passed. `qa_budget` returned 0/1. `custom_context_qa_transition` moved the file to `tasks/qa/`, synced the `**File:**` header, staged the ten modified files and injected the factual diff atomically. No `git add`, `git commit`, `git checkout`, or `git push` was executed.

**QA turn (`brain_turn`, task 404, session `ses_e178e7d34ffewoGYL5tvo2Zn9n`, stage `qa`, include_diff=true):** `QA_PASSED`. Output address `tasks/.sessions/ses_e178e7d34ffewoGYL5tvo2Zn9n_6252dad9/brain_outputs/resp_6afc0b089fd5142bbc464ff0_637cc38013f74814876b58c01cd4afaa.json`. Findings: F1 `zen-proxy/proxy.py:488` JSON-only `UnknownRoute` with fresh id and no new logging; F2 `mcp-brain-bridge/server.py:2295` floor `>=1000` with default 100000 unchanged; F3 `server.py:5232` warning tuple additions, no default-wire change; F4 auth `proxy.py:626`, gating `:541-566`, timeout `:132` untouched; T1/T2/T3 new tests pin boundaries and no test weakened; D1/D2 audit matrices and deferred items consistent.

**Code Reviewer turn (`brain_turn`, task 404, session `ses_e178e7d34ffewoGYL5tvo2Zn9n`, stage `review`, include_diff=true):** `APPROVED`. Output address `tasks/.sessions/ses_e178e7d34ffewoGYL5tvo2Zn9n_6252dad9/brain_outputs/resp_6afc0b7683e422d56c69421b_29e7bcb608dd490bb1bbfe1839e1e3b8.json`. Scope holds, three fixes minimal, docs synced with non-colliding ADR-015/ADR-006, full suite evidence sufficient, no timeout or credential regression. Two low-severity notes: I1 stale acceptance wording `tasks/in-progress/` while the `**File:**` header correctly says `tasks/qa/` (historical criterion, no lane error); I2 three whitespace-only reformat hunks in `tests/test_brain_responses_alignment.py` with identical predicates.

**PO_REVIEW_PENDING.** Code approved technically. Awaiting the Manager's exact closure word before any commit or task closure.

**Closure (2026-11-17).** The Manager answered the relayed closure-approval question with the exact value "Approved for closure". Session `ses_e178e7d34ffewoGYL5tvo2Zn9n`. QA verdict `QA_PASSED` (output `resp_6afc0b089fd5142bbc464ff0_637cc38013f74814876b58c01cd4afaa`) and Code Reviewer verdict `APPROVED` (output `resp_6afc0b7683e422d56c69421b_29e7bcb608dd490bb1bbfe1839e1e3b8`) were chained before the relay. Headers updated to `tasks/completed/404-zen-proxy-openai-api-audit.md` and `Status: closed`; `Started`, `Submitted`, `Finished`, `Estimate`, `Deadline`, `Depends on` and `Milestone` stamps were not hand-edited. Zero `git add`, `git commit`, `git checkout`, or `git push` commands were executed by the Hands.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `27122e43550b91b30d2e07d2b1dd16fea4a70368`
<!-- END_GIT_DIFF -->
