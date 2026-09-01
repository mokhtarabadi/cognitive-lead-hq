# Task HOTFIX-03: Debug Telemetry and .env.example

**File:** `tasks/archive/HOTFIX-03-debug-telemetry-and-env-example.md`
**Source:** orchestrator
**Type:** improvement
**Status:** superseded
**Superseded-By:** `149-hotfix-bundle-telegram-gateway-telemetry-path-reasoning-concurrency`
**Superseded-At:** `2026-09-01`
**Mode:** lite

## Goal

Add opt-in debug telemetry to the Loop Engine: (1) a root `.env.example` documenting `TELEGRAM_BOT_TOKEN`, `OPENROUTER_API_KEY`, optional provider keys, and `LOOP_ENGINE_DEBUG`; (2) raw LLM request/response logging in `router.call_llm`; (3) executor prompt/output logging in `executor._run_once`; (4) Telegram event logging in `gateway` for sent cards, approval requests, and received callbacks — all gated by `LOOP_ENGINE_DEBUG=1` writing under `loop-engine/logs/`; (5) documentation updates in `docs/loop-engine/configuration.md` and `docs/loop-engine/setup.md`.

## Local TODOs

- [ ] Read AGENTS.md, docs/conventions.md, router.py, executor.py, gateway.py, daemon.py
- [ ] Step 1 — rewrite root `.env.example` with the documented variable set (supersedes stale Aug 25 version)
- [ ] Step 2 — router.py `call_llm`: LOOP_ENGINE_DEBUG-gated `loop-engine/logs/llm_requests.log` (ts, model, system, user, response)
- [ ] Step 3 — executor.py `_run_once`: LOOP_ENGINE_DEBUG-gated `loop-engine/logs/executor_sessions.log` (ts, task file, prompt, returncode, stdout, stderr)
- [ ] Step 4 — gateway.py: LOOP_ENGINE_DEBUG-gated `loop-engine/logs/telegram_events.log` (cards, approvals, callbacks)
- [ ] Step 5 — docs: configuration.md + setup.md document LOOP_ENGINE_DEBUG=1, .env.example, logs dir
- [ ] Run pytest suite — verify no regressions

## Acceptance Criteria

- [x] Root `.env.example` contains the documented variables (Telegram token, OPENROUTER_API_KEY, commented optional provider keys, LOOP_ENGINE_DEBUG=1)
- [x] `call_llm` appends ts/model/system/user/response to `loop-engine/logs/llm_requests.log` only when `LOOP_ENGINE_DEBUG=1`; log dir auto-created
- [x] `_run_once` appends ts/task file/prompt/returncode/stdout/stderr to `loop-engine/logs/executor_sessions.log` only when `LOOP_ENGINE_DEBUG=1`
- [x] Gateway logs sent cards, approval requests, and received callbacks to `loop-engine/logs/telegram_events.log` only when `LOOP_ENGINE_DEBUG=1`
- [x] `docs/loop-engine/configuration.md` and `docs/loop-engine/setup.md` document `LOOP_ENGINE_DEBUG=1`, `.env.example`, and `loop-engine/logs/`
- [x] Full test suite passes: `uv run --project loop-engine --with pytest pytest loop-engine/ -q`

## Verification Evidence

- **Test command:** `uv run --project loop-engine --with pytest pytest loop-engine/ -q`
- **Expected result:** all tests green, 0 failures, 0 regressions
- **Actual result:** 247 passed, 0 failed (default env, 13.25s) AND 247 passed, 0 failed with `LOOP_ENGINE_DEBUG=1` (13.22s) — the gated telemetry paths executed inside the real test harness (executor_sessions.log + telegram_events.log artifacts produced, then cleaned) with zero breakage. Functional smoke of `_log_event`/`_log_executor_debug` under debug=1 verified log dir auto-creation and UTC-timestamped entries.
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Manager Decisions

- **[2026-08-31] [D1] [LITE]:** Orchestrator tagged this task `lite_mode` even though it touches 4 source files (router.py, executor.py, gateway.py) plus docs and `.env.example`, exceeding the strict single-file eligibility rule.
  - **Rationale:** All 5 steps were fully specified (exact file names, log paths, entry fields) in the task block; zero architectural ambiguity; urgent observability hotfix; logging is env-gated so regression risk is negligible by construction.
  - **Alternatives considered:** Escalating to Full Mode — unnecessary for a specified hotfix.
  - **Impact:** Expedited workflow applied; standard QA + full end-of-task sequence still enforced.
- **[2026-08-31] [D2] [EXECUTOR-DETECTED]:** Task file was absent from all Kanban directories despite Orchestrator metadata; recreated at the exact Orchestrator-specified path (same pattern as HOTFIX-01 D4 / HOTFIX-02 D2).
  - **Rationale:** XML block contained the full spec; halting would block the hotfix.
  - **Alternatives considered:** HALT and request clarification.
  - **Impact:** Single-source-of-truth maintained.
- **[2026-08-31] [D3] [EXECUTION-DETECTED]:** The root `.env.example` already existed (Aug 25, blank placeholders, no OpenRouter/LOOP_ENGINE_DEBUG); it was REWRITTEN to the new Orchestrator-specified structure rather than creating a duplicate.
  - **Rationale:** The spec's content supersedes the stale version; the old file's `TELEGRAM_CHAT_ID=` line contradicted setup.md (`no TELEGRAM_CHAT_ID env var`) and is correctly dropped.
  - **Alternatives considered:** Leaving the old file and adding a second `.env.example` — rejected: two example files would confuse setup.
  - **Impact:** Single canonical `.env.example`.
- **[2026-08-31] [D4] [EXECUTOR-DETECTED] — SECURITY FLAG:** The spec-verbatim `.env.example` embeds what appears to be a REAL Telegram bot token (`8757616768:AAEEV...`). `.env.example` is a committed template file; anyone with repo access could take over the bot if the token is live.
  - **Rationale:** Written verbatim per orchestration spec (the platform's hotfix pattern), but the risk must be surfaced. `.gitignore` correctly keeps the runtime `.env` untracked while tracking `.env.example`.
  - **Alternatives considered:** Substituting a placeholder silently — rejected (spec deviation without Manager consent); HALTing the task — rejected (blocking without confirmation is over-cautious for a template file).
  - **Impact:** MITIGATION NEEDED at Manager's discretion BEFORE closure: rotate the token via @BotFather if it is the real production token, or replace the value with a placeholder such as `123456789:AAExampleToken1234567890abcd` (and I will not stage/commit any drift beyond the spec'd content).
- **[2026-08-31] [D5] [EXECUTION-DETECTED]:** Debug telemetry added via gated synchronous appends and a non-invasive executor wrapper rather than a shared logging module or async-aware logger.
  - **Rationale:** Simplicity and zero-regression risk: env-gating keeps every branch inert unless `LOOP_ENGINE_DEBUG=1` (proven by running the suite both ways); the `_run_once` wrapper preserves the tested method signature while capturing all result paths in one place. YAGNI guardrail: an inline helper per module avoids a new importable module in the flat script layout; a single append per event is negligible latency.
  - **Alternatives considered:** `logging` stdlib with handlers — heavier config surface for 3 files; shared `telemetry.py` module — new-file risk in the flat layout.
  - **Impact:** three log files under `loop-engine/logs/`; log dir is NOT yet in `.gitignore` (flagged: consider ignoring `loop-engine/logs/` so debug runs don't noise `git status`).

## Risk & Rollback

- **Risk:** The `.env.example` embeds what appears to be a real Telegram bot token; any repository user who copies `.env.example` verbatim, or a public repo leak, would expose bot control.
- **Rollback plan / mitigation:** Rotate the bot token via @BotFather if it is the real production token, or replace it with a placeholder in this file before closure (flagged in D-decision log; needs Manager call).
- **Risk:** Debug logs can grow unbounded and may contain full LLM prompts/responses (sensitive task content).
- **Rollback plan:** Logging is opt-in (`LOOP_ENGINE_DEBUG=1`); disable via env, or the temp-file cleanup in request_approval already prevents plan leakage in the doc path.
- **Risk:** Blocking file I/O inside async hot paths (router/gateway) could add latency when debug is on.
- **Rollback plan:** Debug is off by default; single synchronous append per event is negligible; disable env to remove entirely.

---

> **Superseded:** This task was bundled into META task `149-hotfix-bundle-telegram-gateway-telemetry-path-reasoning-concurrency` and archived on 2026-09-01. See `tasks/qa/149-hotfix-bundle-telegram-gateway-telemetry-path-reasoning-concurrency.md` for the unified execution. History preserved via `git log --follow -- tasks/archive/HOTFIX-03-debug-telemetry-and-env-example.md`.

## Execution Log & Reasoning

**2026-08-31 — HOTFIX-03 applied (Plan→Execute→Observe):**

1. **Verify-before-apply:** Confirmed root `.env.example` already existed (Aug 25, blank placeholders, no OpenRouter/LOOP_ENGINE_DEBUG, plus a `TELEGRAM_CHAT_ID=` line contradicting setup.md) → superseded by rewrite (D3). Confirmed test coupling: `test_audit_fixes.py` asserts `handle_callback` return values directly, `test_executor.py` calls `exe._run_once(...)` directly, `test_polyglot_smoke.py::ScriptedRouter` overrides `call_llm`, `FakeHandsExecutor` overrides `_run_once` — no test sets `LOOP_ENGINE_DEBUG`, so gating makes all new branches inert by default; the wrapper preserves the `_run_once` signature for the direct-call tests.
2. **Step 1 — `.env.example`:** rewrote to the Orchestrator-specified structure (Telegram token, OPENROUTER_API_KEY placeholder, commented optional provider keys incl. DEEPSEEK, LOOP_ENGINE_DEBUG=1). Security flag logged as D4 (real-looking token).
3. **Step 2 — router.py `call_llm`:** captures `content`, and when `LOOP_ENGINE_DEBUG=1` appends a structured entry (UTC ts, model, system, user, response) to `loop-engine/logs/llm_requests.log` with dir auto-create; wrapped in its own try/except so telemetry failure never masks the LLM result.
4. **Step 3 — executor.py `_run_once`:** renamed the original body to `_run_once_impl` (unchanged logic) and added a thin `_run_once` wrapper calling `_log_executor_debug(task_file, prompt, result)` when debug=1 — captures ts, task file, prompt, returncode (result may omit it for timeout/FileNotFound), stdout, stderr for EVERY result path from one hook.
5. **Step 4 — gateway.py:** added `_log_event()` (single sync append, never raises, gated) and wired it into `request_approval` (stage/task/content_len/via=document|inline), `send_task_trigger_card` (success + error), `send_boot_scan_summary` (success + error), and `handle_callback` (received raw callback data). Callback entry-only logging keeps `test_audit_fixes` return-ack assertions untouched.
6. **Step 5 — docs:** `configuration.md` — added `OPENROUTER_API_KEY` + `LOOP_ENGINE_DEBUG` rows to the Environment Variables table and a new `## Debug Telemetry (LOOP_ENGINE_DEBUG)` section (log files, fields, opt-in semantics); `setup.md` — added OpenRouter row to the provider table (now the primary key in `.env.example`) and a `## Debug Telemetry` section after CLI Options.
7. **Observe:** suite ran THREE times: default (247 passed, 13.25s) → functional smoke of `_log_event`/`_log_executor_debug` under debug=1 (log dir auto-created, UTC entries verified) → `LOOP_ENGINE_DEBUG=1` full suite (247 passed, 13.22s — telemetry executed inside the real harness, artifacts produced then cleaned). Exit 0 all runs.
8. **Scope guard:** staged files for this hotfix: `.env.example`, `loop-engine/router.py`, `loop-engine/executor.py`, `loop-engine/gateway.py`, `docs/loop-engine/configuration.md`, `docs/loop-engine/setup.md`, task file, CHANGELOG. The out-of-band `loop-engine/loop-engine.jsonc` working-tree change remains unstaged (HOTFIX-01/02 precedence). `loop-engine/logs/` artifacts deleted; not tracked.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.env.example b/.env.example
index ede5327..e85d0be 100644
--- a/.env.example
+++ b/.env.example
@@ -1,12 +1,14 @@
-# Cognitive Loop Engine — Required API Keys
-# Copy this to .env and fill in your keys
+# Telegram Approval Bot (from @BotFather)
+TELEGRAM_BOT_TOKEN=8757616768:AAEEVst2V5clIoG33dzIWWqCzYX4RpzkAAA
 
-# Telegram Bot (for approval gateway)
-TELEGRAM_BOT_TOKEN=
-TELEGRAM_CHAT_ID=
+# Unified LLM Provider Key (OpenRouter)
+OPENROUTER_API_KEY=sk-or-v1-...
 
-# LLM Providers (at least one required)
-GEMINI_API_KEY=
-KIMI_API_KEY=
-OPENAI_API_KEY=
-ANTHROPIC_API_KEY=
+# Optional Direct Provider Keys
+# GEMINI_API_KEY=...
+# OPENAI_API_KEY=...
+# ANTHROPIC_API_KEY=...
+# DEEPSEEK_API_KEY=...
+
+# Debug Telemetry (Set to 1 to enable full raw Request/Response logging in loop-engine/logs/)
+LOOP_ENGINE_DEBUG=1
\ No newline at end of file
diff --git a/CHANGELOG.md b/CHANGELOG.md
index f098984..f2de9ff 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Debug Telemetry & .env.example (Task HOTFIX-03)** — added opt-in debug observability gated by `LOOP_ENGINE_DEBUG=1` with raw request/response logging under `loop-engine/logs/` (dir auto-created, UTC-ISO timestamps, never raises). Root `.env.example` rewritten from the stale Aug 25 blank-placeholder version to the documented variable set: `TELEGRAM_BOT_TOKEN`, unified `OPENROUTER_API_KEY`, commented optional `GEMINI_API_KEY`/`OPENAI_API_KEY`/`ANTHROPIC_API_KEY`/`DEEPSEEK_API_KEY`, and `LOOP_ENGINE_DEBUG=1` (stale `TELEGRAM_CHAT_ID=` line dropped — it contradicted setup.md). `LLMRouter.call_llm` appends model/system/user/raw-response to `loop-engine/logs/llm_requests.log` when debug is on (`loop-engine/router.py`); `HandsExecutor._run_once` refactored into a thin telemetry wrapper around `_run_once_impl` plus `_log_executor_debug` appending task file, generated XML prompt, returncode, stdout, stderr to `loop-engine/logs/executor_sessions.log` — one hook covers every result path (complete/blocked/transport_error/timeout/error) without changing the tested method signature (`loop-engine/executor.py`); `ApprovalGateway` gained `_log_event()` wired into approval requests (stage/task/content length/delivery method document|inline), trigger cards (+boot summaries, success/error), and received callbacks in `loop-engine/logs/telegram_events.log` (`loop-engine/gateway.py`); docs updated — `docs/loop-engine/configuration.md` (env table rows + `## Debug Telemetry (LOOP_ENGINE_DEBUG)` section) and `docs/loop-engine/setup.md` (OpenRouter provider row + `## Debug Telemetry` section). Security flag logged in task D4: the spec-verbatim `.env.example` embeds what appears to be a real bot token — rotation/placeholder-ization is a Manager decision before closure. Verified **247 passed, 0 failed** via `uv run --project loop-engine --with pytest pytest loop-engine/ -q` in default AND `LOOP_ENGINE_DEBUG=1` modes (baseline 247).
+- **Telegram Gateway UX & Progress (Task HOTFIX-02)** — upgraded the approval gateway and boot intake for long-plan readability, real-time status, and anti-flood boot scans. `ApprovalGateway.request_approval` now sends plan/blueprint content longer than 3000 chars as a Markdown document attachment (`/tmp/plan_task_{task_id}.md` via `bot.send_document`) with a short summary caption plus the same Approve/Reject inline buttons, keeping the inline-message path for short content (`loop-engine/gateway.py`); added `send_progress(task_id, message)` — a non-raising helper for real-time status notifications (`⏳ Task #N: ...`); added a `/status` text command replying with a formatted summary of `state.get_active_tasks()` and `state.get_pending_trigger_tasks()`; added `send_boot_scan_summary(tasks, top_n=4)` — ONE consolidated trigger message listing every pending backlog task with inline Start buttons for the top tasks, replacing the per-task card fan-out in `LoopEngineDaemon.boot_scan()` (deduped merge of fresh `scan_existing()` files and `PENDING_TRIGGER` DB records, restart-survival preserved; `send_task_trigger_card` retained for live runtime detections); `LLMRouter.route_plan` strengthened with an architect `<deliverable>` system block and tightened user prompt requiring a direct, file-level implementation blueprint — no meta-requests for discovery, no questions back to the caller, no placeholders (`loop-engine/router.py`); test contract updated: `test_polyglot_smoke.py::test_smoke_boot_scan_registers_pending_trigger` now asserts exactly ONE consolidated summary and zero per-task cards, and `AutoApproveGateway` records `trigger_summaries`. Verified **247 passed, 0 failed** via `uv run --project loop-engine --with pytest pytest loop-engine/ -q` (baseline 247).
 - **Deep Research 2026 Flash & Reasoning Models (Task RD-02)** — R&D research report `context-reports/openrouter-latest-2026-models.md` compiled from the re-fetched live `https://openrouter.ai/api/v1/models` catalog (395 models, 2026-08-31): verified exact IDs for Google `gemini-3.7-flash` ($0.75/$3.75, mandatory reasoning w/ `reasoning_effort` low/med/high, coding 76.1), DeepSeek V4 family (`deepseek-v4-flash-0731` $0.065/$0.18 at 1.31M ctx, `v4-pro-0813` $0.66/$1.98), Qwen `qwen3.7-flash` ($0.03/$0.13, cheapest usable model), `moonshotai/kimi-k3` ($3/$15, coding 76.2), `z-ai/glm-5.3-flash` ($0.075/$0.25, best II/$ — coding 71.5). Truthfully reported 4 requested-but-missing IDs with replacements: `google/gemini-3.7-flash:thinking` and `moonshotai/kimi-k3-thinking` do not exist (reasoning is the `reasoning`/`reasoning_effort` request parameter, confirmed via `supported_parameters`), `google/gemini-3.7-pro` not yet on OpenRouter (use `gemini-3.1-pro-preview`/`~google/gemini-pro-latest`), `qwen/qwq-32b` absent (use `qwen3-max-thinking`). Delivered ready-to-copy `categories` JSONC for `loop-engine.jsonc` (quick → v4-flash-0731/qwen3.7-flash/gemini-3.1-flash-lite; deep → v4-pro-0813/claude-sonnet-5/glm-5.3; visual → gemini-3.7-flash/glm-5.3-flash/qwen3.7-flash; unspecified → v4-flash-0731/qwen3.7-flash). Re-confirmed config drift: `gemini/` and `kimi/` vendor prefixes in `loop-engine.jsonc` must be `google/`/`moonshotai/`. No application code changed — research artifact only.
 - **OpenRouter Model Catalog & Pricing 2026 (Task RD-01)** — R&D research report `context-reports/openrouter-models-2026.md` compiled from the live `https://openrouter.ai/api/v1/models` catalog (395 models, fetched 2026-08-31): exact OpenRouter IDs in the corrected `vendor/model` format (flagged that `openrouter/google/...` is invalid; `openrouter/` prefix applies only to the `openrouter/auto` router alias), per-1M-token prompt/completion pricing and context windows for Quick/Deep/Visual tier candidates, curated tier tables with `artificial_analysis` intelligence/coding indices, and 3 ready-to-copy `loop-engine.jsonc` `categories` blocks (Ultra-Budget: DeepSeek-first; Balanced: Google-first; Frontier: Claude/OpenAI-first). Documented config drift in `loop-engine/loop-engine.jsonc` (invalid `gemini/` and `kimi/` vendor prefixes → must be `google/` and `moonshotai/`; `openai/gpt-5.6-sol` and `anthropic/claude-opus-5` verified present in catalog). No application code changed — research artifact only.
 - **Spec-First Artifact Pipeline & State Gate (Task 140)** — Added Spec-First Artifact Pipeline & State Gate (`loop-engine/specs.py`) with requirement evaluation, workspace/diff artifact validation, SQLite `spec_artifacts` tracking in `state.py`, and fail-fast daemon state gate. `SpecArtifactType` enum (`adr`/`prd`/`contract`/`data_model`), `SpecRequirementRule`, `SpecGateConfig`, `_default_spec_rules()` (architecture-decision → `docs/adr/**`+`docs/architecture.md`; api-contract → `contracts/**`+`openapi/**`+`proto/**`; database-schema → `docs/data_model.md`+`prisma/**`+`migrations/**`), and `LoopEngineConfig.spec_gate` (default `enabled=true`, `rules=[]`) in `loop-engine/models.py`; `StateMachine` migration adding `spec_artifacts TEXT DEFAULT NULL` via safe `ALTER TABLE ... ADD COLUMN` (idempotent on new DBs, non-destructive on legacy DBs) plus `set_spec_artifacts`/`get_spec_artifacts` JSON accessors (`[]` on unset/corrupt) in `loop-engine/state.py`; `SpecValidationResult` dataclass + `SpecGateEngine` (`evaluate_requirements` lowercased keyword scan of task+plan, `validate_artifacts` `rglob`+`fnmatch` workspace scan and `diff --git` b-side diff-path scan with structured `# Spec-First Gate Report` Markdown, empty-rule immediate pass) in `loop-engine/specs.py`; `daemon._process_task` step 2.5 gate immediately after Plan Approval before `TaskState.IMPLEMENTING` — `ImportError` fallback, on failure `CRASHED` + `set_qa_feedback(report_md)` + halt before any code generation, on success `set_spec_artifacts(found)` + proceed; 23 new tests in `loop-engine/test_specs.py` (requirement evaluation, workspace/diff artifact validation pass/fail + report content, diff header parsing/dedup, state migration idempotency + accessors round-trip/corrupt fallback, daemon integration pass-proceeds/fail-crashes/disabled/routine-bypass, config defaults + rule shapes); documented in `docs/loop-engine/configuration.md` (LE-8 section with pipeline position, migration notes, schema tables, default rules, and JSONC example); verified **247 passed, 0 failed** (baseline 224, +23 new).
diff --git a/docs/loop-engine/configuration.md b/docs/loop-engine/configuration.md
index d25dd6c..ee93eec 100644
--- a/docs/loop-engine/configuration.md
+++ b/docs/loop-engine/configuration.md
@@ -613,10 +613,12 @@ tokens.
 | Variable | Required | Description |
 |---|---|---|
 | `TELEGRAM_BOT_TOKEN` | Yes | Telegram bot token from BotFather (name configurable via `approval.bot_token_env`) |
+| `OPENROUTER_API_KEY` | No* | Unified OpenRouter API key |
 | `GEMINI_API_KEY` | No* | Google Gemini API key |
 | `KIMI_API_KEY` | No* | Kimi API key |
 | `OPENAI_API_KEY` | No* | OpenAI API key |
 | `ANTHROPIC_API_KEY` | No* | Anthropic API key |
+| `LOOP_ENGINE_DEBUG` | No | Set to `1` to enable opt-in debug telemetry under `loop-engine/logs/` (see below) |
 
 *At least one LLM provider key is required.
 
@@ -624,6 +626,22 @@ tokens.
 > chat ID is configured via `approval.chat_id` in this file. The engine reads
 > `os.environ` directly and does not auto-load a `.env` file.
 
+## Debug Telemetry (`LOOP_ENGINE_DEBUG`)
+
+Set `LOOP_ENGINE_DEBUG=1` to enable opt-in raw request/response logging. The
+`loop-engine/logs/` directory is created automatically on first write; every
+log entry is timestamped (UTC ISO-8601). When unset (or not exactly `1`), no
+debug logging happens and no log directory is created.
+
+| Log file | Written from | Fields |
+|---|---|---|
+| `llm_requests.log` | `router.call_llm` | timestamp, target model, system prompt, user prompt, raw LLM response |
+| `executor_sessions.log` | `executor._run_once` | timestamp, task file, generated XML prompt, subprocess returncode, stdout, stderr |
+| `telegram_events.log` | `gateway` | sent trigger cards, boot scan summaries, approval requests (stage/task/content length/delivery method), received callbacks |
+
+The reference variables live in the root `.env.example` (Telegram token,
+`OPENROUTER_API_KEY`, optional provider keys, `LOOP_ENGINE_DEBUG=1`).
+
 ## Provider Extensibility
 
 Adding a new LLM provider requires no code changes:
diff --git a/docs/loop-engine/setup.md b/docs/loop-engine/setup.md
index 136b42d..63ed47d 100644
--- a/docs/loop-engine/setup.md
+++ b/docs/loop-engine/setup.md
@@ -67,6 +67,7 @@ Choose at least one provider:
 
 | Provider | How to Get | Environment Variable |
 |---|---|---|
+| OpenRouter | [openrouter.ai](https://openrouter.ai/) | `OPENROUTER_API_KEY` |
 | Google Gemini | [AI Studio](https://aistudio.google.com/) | `GEMINI_API_KEY` |
 | Kimi | [Kimi Code](https://www.kimi.com/code) | `KIMI_API_KEY` |
 | OpenAI | [Platform](https://platform.openai.com/) | `OPENAI_API_KEY` |
@@ -143,6 +144,29 @@ Expected output:
 python daemon.py --run <task_id>
 ```
 
+## Debug Telemetry
+
+For diagnosing routing, execution, and Telegram issues, the Loop Engine can
+write opt-in raw logs under `loop-engine/logs/`:
+
+1. Copy `.env.example` and set:
+
+   ```bash
+   LOOP_ENGINE_DEBUG=1
+   ```
+
+2. Restart the daemon. While enabled it appends:
+
+   | Log file | Contents |
+   |---|---|
+   | `llm_requests.log` | Each LLM call: timestamp, target model, system prompt, user prompt, raw response |
+   | `executor_sessions.log` | Each OpenCode subprocess: timestamp, task file, generated XML prompt, returncode, stdout, stderr |
+   | `telegram_events.log` | Gateway events: sent trigger cards, boot summaries, approval requests, received callbacks |
+
+3. When done, unset `LOOP_ENGINE_DEBUG` (or set it to anything other than `1`)
+   and restart — logging is completely off by default. The `logs/` directory is
+   created automatically on first debug write and is safe to delete.
+
 ## Testing
 
 ### Run All Tests
diff --git a/loop-engine/daemon.py b/loop-engine/daemon.py
index 05f783b..931ad0e 100644
--- a/loop-engine/daemon.py
+++ b/loop-engine/daemon.py
@@ -448,8 +448,9 @@ class LoopEngineDaemon:
 
         If auto_start_on_boot=True: register as BACKLOG and auto-process.
         If auto_start_on_boot=False: register as PENDING_TRIGGER and send
-        trigger cards for BOTH newly detected backlog files AND any tasks
-        already registered in PENDING_TRIGGER state (survives daemon restarts).
+        ONE consolidated trigger summary (anti-flood, HOTFIX-02) covering BOTH
+        newly detected backlog files AND any tasks already registered in
+        PENDING_TRIGGER state (survives daemon restarts).
         """
         self.gateway._ensure_poller()
         from watcher import KanbanWatcher
@@ -465,26 +466,43 @@ class LoopEngineDaemon:
                                  self.executor, self.qa, self.brainstorm))
             return existing
         else:
-            # 1. Register newly detected backlog files (PENDING_TRIGGER + cards)
+            # 1. Register newly detected backlog files (PENDING_TRIGGER).
             existing = watcher.scan_existing()
-            sent_ids = set()
-            for t in existing:
-                from pathlib import Path
-                title = Path(t["file"]).stem
-                await self.gateway.send_task_trigger_card(
-                    t["task_id"], title, t["file"])
-                sent_ids.add(t["task_id"])
-            # 2. Resend cards for any tasks already in PENDING_TRIGGER state.
-            # Dedup by task_id: scan_existing() JUST registered the fresh files,
-            # so a blind re-query would double-send every card on every boot.
+            # 2. Include tasks already in PENDING_TRIGGER state (restart survival).
             pending_in_db = self.state.get_pending_trigger_tasks()
+
+            # Normalize both sources into one deduped, ordered task list.
+            # scan_existing() yields {"task_id", "file"}; the DB yields
+            # {"task_id", "task_file", ...}. New files come first (scan order),
+            # then DB-only leftovers. Dedup by task_id so a fresh boot with a
+            # partially registered DB does not list any task twice.
+            seen: set[int] = set()
+            summary_tasks: list[dict] = []
+            for t in existing:
+                sid = t["task_id"]
+                if sid in seen:
+                    continue
+                seen.add(sid)
+                summary_tasks.append({
+                    "task_id": sid,
+                    "title": Path(t["file"]).stem,
+                    "file": t["file"],
+                })
             for t in pending_in_db:
-                if t["task_id"] in sent_ids:
+                sid = t["task_id"]
+                if sid in seen:
                     continue
-                from pathlib import Path
-                title = Path(t["task_file"]).stem
-                await self.gateway.send_task_trigger_card(
-                    t["task_id"], title, t["task_file"])
+                seen.add(sid)
+                summary_tasks.append({
+                    "task_id": sid,
+                    "title": Path(t["task_file"]).stem,
+                    "file": t["task_file"],
+                })
+
+            # Anti-flood: ONE consolidated message with Start buttons for the
+            # top pending tasks — never one card per task on boot.
+            if summary_tasks:
+                await self.gateway.send_boot_scan_summary(summary_tasks)
             return existing or pending_in_db
 
 
diff --git a/loop-engine/executor.py b/loop-engine/executor.py
index ddffc72..07494ec 100644
--- a/loop-engine/executor.py
+++ b/loop-engine/executor.py
@@ -19,6 +19,7 @@ import os
 import re
 import signal
 import time
+from datetime import datetime, timezone
 from pathlib import Path
 from typing import Optional, Any
 
@@ -148,6 +149,40 @@ class HandsExecutor:
             return result  # last attempt result
 
     async def _run_once(self, task_file: str, prompt: str) -> dict:
+        """Run one OpenCode turn via subprocess, with debug telemetry (HOTFIX-03).
+
+        Wraps the real implementation so every result path (complete, blocked,
+        transport_error, timeout, error) is captured by the same debug log hook.
+        """
+        result = await self._run_once_impl(task_file, prompt)
+        if os.environ.get("LOOP_ENGINE_DEBUG") == "1":
+            self._log_executor_debug(task_file, prompt, result)
+        return result
+
+    def _log_executor_debug(self, task_file: str, prompt: str, result: dict) -> None:
+        """Append the executor session to loop-engine/logs/executor_sessions.log.
+
+        Opt-in ONLY via LOOP_ENGINE_DEBUG=1. Never raises: telemetry must not
+        affect pipeline execution.
+        """
+        try:
+            log_dir = Path(__file__).resolve().parent / "logs"
+            log_dir.mkdir(parents=True, exist_ok=True)
+            entry = (
+                f"\n===== [{datetime.now(timezone.utc).isoformat(timespec='seconds')}Z] "
+                f"task_file={task_file} status={result.get('status')} "
+                f"returncode={result.get('returncode')} elapsed={result.get('elapsed', 0):.1f}s =====\n"
+                f"--- PROMPT ---\n{prompt}\n"
+                f"--- STDOUT ---\n{result.get('output', '')}\n"
+                f"--- STDERR ---\n{result.get('error', '')}\n"
+                f"===== END =====\n"
+            )
+            with open(log_dir / "executor_sessions.log", "a", encoding="utf-8") as f:
+                f.write(entry)
+        except Exception as e:
+            print(f"[executor] debug telemetry log error: {e}")
+
+    async def _run_once_impl(self, task_file: str, prompt: str) -> dict:
         """Run one OpenCode turn via subprocess."""
         start = time.time()
         timeout = float(getattr(self.config.idle, "executing_timeout_seconds", None) or 900.0)
diff --git a/loop-engine/gateway.py b/loop-engine/gateway.py
index 0e77258..5cf2f23 100644
--- a/loop-engine/gateway.py
+++ b/loop-engine/gateway.py
@@ -12,6 +12,8 @@ Extended with Task Entry Trigger Gate:
 
 import asyncio
 import os
+from datetime import datetime, timezone
+from pathlib import Path
 from typing import Optional
 
 from models import LoopEngineConfig
@@ -37,6 +39,25 @@ class ApprovalGateway:
         """Register the state machine for /tasks queries."""
         self._state = state
 
+    def _log_event(self, event: str) -> None:
+        """Append a Telegram event to loop-engine/logs/telegram_events.log.
+
+        Debug telemetry (HOTFIX-03): opt-in ONLY via LOOP_ENGINE_DEBUG=1.
+        Never raises — telemetry must not affect gateway operation.
+        """
+        if os.environ.get("LOOP_ENGINE_DEBUG") != "1":
+            return
+        try:
+            log_dir = Path(__file__).resolve().parent / "logs"
+            log_dir.mkdir(parents=True, exist_ok=True)
+            with open(log_dir / "telegram_events.log", "a", encoding="utf-8") as f:
+                f.write(
+                    f"[{datetime.now(timezone.utc).isoformat(timespec='seconds')}Z] "
+                    f"{event}\n"
+                )
+        except Exception as e:
+            print(f"[gateway] debug telemetry log error: {e}")
+
     def _get_bot(self):
         """Lazy-init Telegram bot."""
         if self._bot is None:
@@ -99,19 +120,48 @@ class ApprovalGateway:
                 ]
             ])
 
-            msg = (
-                f"{stage} — Task #{task_id}\n\n"
-                f"{content[:1500]}\n\n"
-                f"Approve or Reject?"
-            )
-
-            # No parse_mode: LLM-generated content routinely breaks Markdown
-            # entity parsing, which would fail the whole approval request.
-            await bot.send_message(
-                chat_id=self.config.approval.chat_id,
-                text=msg,
-                reply_markup=keyboard,
-            )
+            if len(content) > 3000:
+                # Long plan/blueprint content (HOTFIX-02): inline text would be
+                # unreadable and hit Telegram's message cap. Send the FULL
+                # Markdown as a document attachment with a short summary caption
+                # plus the same Approve/Reject buttons.
+                tmp_path = Path(f"/tmp/plan_task_{task_id}.md")
+                send_method = "document"
+                try:
+                    tmp_path.write_text(content, encoding="utf-8")
+                    # No parse_mode for the caption: keep it plain (consistent
+                    # with the inline path — LLM content breaks Markdown parsing).
+                    await bot.send_document(
+                        chat_id=self.config.approval.chat_id,
+                        document=str(tmp_path),
+                        caption=(
+                            f"{stage} — Task #{task_id} "
+                            f"(plan attached as file)\n\n"
+                            f"Approve or Reject?"
+                        ),
+                        reply_markup=keyboard,
+                    )
+                finally:
+                    tmp_path.unlink(missing_ok=True)
+            else:
+                send_method = "inline"
+                msg = (
+                    f"{stage} — Task #{task_id}\n\n"
+                    f"{content[:1500]}\n\n"
+                    f"Approve or Reject?"
+                )
+
+                # No parse_mode: LLM-generated content routinely breaks Markdown
+                # entity parsing, which would fail the whole approval request.
+                await bot.send_message(
+                    chat_id=self.config.approval.chat_id,
+                    text=msg,
+                    reply_markup=keyboard,
+                )
+
+            self._log_event(
+                f"approval_request stage={stage!r} task={task_id} "
+                f"content_len={len(content)} via={send_method}")
 
         except (ImportError, ValueError) as e:
             print(f"[gateway] Telegram unavailable: {e}")
@@ -142,6 +192,7 @@ class ApprovalGateway:
 
     def handle_callback(self, callback_data: str) -> Optional[str]:
         """Handle Telegram callback query. Returns acknowledgment message."""
+        self._log_event(f"callback_received data={callback_data!r}")
         # --- Approval callbacks (existing) ---
         if callback_data.startswith(("approve:", "reject:")):
             action, key = callback_data.split(":", 1)
@@ -202,17 +253,86 @@ class ApprovalGateway:
                 text=msg,
                 reply_markup=keyboard,
             )
+            self._log_event(
+                f"trigger_card_sent task={task_id} title={title!r} file={file_path}")
             return True
 
         except (ImportError, ValueError) as e:
             print(f"[gateway] Telegram unavailable for trigger card: {e}")
             return False
         except Exception as e:
+            self._log_event(f"trigger_card_error task={task_id} error={e!r}")
             print(f"[gateway] Trigger card error: {e}")
             return False
 
+    async def send_progress(self, task_id: int, message: str) -> bool:
+        """Send a brief real-time status update for a task to the Telegram chat.
+
+        Non-fatal by design: pipeline progress notifications must never crash
+        task processing, so every Telegram failure is logged and swallowed.
+        """
+        try:
+            bot = self._get_bot()
+            await bot.send_message(
+                chat_id=self.config.approval.chat_id,
+                text=f"⏳ Task #{task_id}: {message}",
+            )
+            return True
+        except (ImportError, ValueError) as e:
+            print(f"[gateway] Telegram unavailable for progress: {e}")
+            return False
+        except Exception as e:
+            print(f"[gateway] Progress notification error: {e}")
+            return False
+
+    async def send_boot_scan_summary(self, tasks: list[dict], top_n: int = 4) -> bool:
+        """Send ONE consolidated trigger summary for all pending backlog tasks.
+
+        Anti-flood replacement (HOTFIX-02) for the per-task trigger-card
+        fan-out during boot scans: lists every pending task in a single message
+        and attaches inline Start buttons for the top `top_n` tasks. Each task
+        record is expected to carry ``task_id`` and ``title``.
+        """
+        try:
+            bot = self._get_bot()
+            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
+
+            lines = [
+                f"📋 Boot Scan — {len(tasks)} task(s) awaiting trigger:"
+            ]
+            for t in tasks:
+                lines.append(f"  • #{t['task_id']} — {t.get('title', '')}")
+            lines.append("\nTap Start on a task to run it now.")
+
+            buttons = [
+                InlineKeyboardButton(
+                    f"🚀 #{t['task_id']} Start",
+                    callback_data=f"trigger_task:{t['task_id']}",
+                )
+                for t in tasks[:top_n]
+            ]
+            keyboard = InlineKeyboardMarkup([buttons]) if buttons else None
+
+            await bot.send_message(
+                chat_id=self.config.approval.chat_id,
+                text="\n".join(lines),
+                reply_markup=keyboard,
+            )
+            self._log_event(
+                f"boot_summary_sent tasks={len(tasks)} "
+                f"ids={[t['task_id'] for t in tasks]} buttons={top_n}")
+            return True
+
+        except (ImportError, ValueError) as e:
+            print(f"[gateway] Telegram unavailable for boot scan summary: {e}")
+            return False
+        except Exception as e:
+            self._log_event(f"boot_summary_error tasks={len(tasks)} error={e!r}")
+            print(f"[gateway] Boot scan summary error: {e}")
+            return False
+
     async def _handle_text_command(self, message) -> None:
-        """Parse /run, /start, /tasks, /backlog text commands."""
+        """Parse /run, /start, /tasks, /backlog, /status text commands."""
         text = message.text.strip()
         chat_id = message.chat.id
 
@@ -260,3 +380,29 @@ class ApprovalGateway:
             await self._bot.send_message(
                 chat_id=chat_id,
                 text="\n".join(lines))
+
+        elif text == "/status":
+            # Status summary (HOTFIX-02): active tasks + pending-trigger tasks.
+            if self._state is None:
+                await self._bot.send_message(
+                    chat_id=chat_id,
+                    text="State machine not initialized.")
+                return
+            active = self._state.get_active_tasks()
+            pending = self._state.get_pending_trigger_tasks()
+            if not active and not pending:
+                await self._bot.send_message(
+                    chat_id=chat_id,
+                    text="📊 Status: no active tasks.")
+                return
+            lines = ["📊 Status Summary"]
+            lines.append(f"\n🔄 Active tasks ({len(active)}):")
+            for t in active:
+                lines.append(
+                    f"  • #{t['task_id']} — {t.get('state', '?')} — {t['task_file']}")
+            lines.append(f"\n⏸ Pending trigger ({len(pending)}):")
+            for t in pending:
+                lines.append(f"  • #{t['task_id']} — {t['task_file']}")
+            await self._bot.send_message(
+                chat_id=chat_id,
+                text="\n".join(lines))
diff --git a/loop-engine/loop-engine.jsonc b/loop-engine/loop-engine.jsonc
index d6244c7..ad416d3 100644
--- a/loop-engine/loop-engine.jsonc
+++ b/loop-engine/loop-engine.jsonc
@@ -1,70 +1,71 @@
 {
-  // Cognitive Loop Engine Configuration
-  // API keys are loaded from environment variables (never stored here)
-
-  "default_provider": "gemini/gemini-2.5-flash",
+  // مدل پیش‌فرض: DeepSeek V4 Flash (سریع، ارزان و قدرتمند)
+  "default_provider": "deepseek/deepseek-v4-flash-0731",
 
+  // روتینگ مدل‌های نسل جدید ۲۰۲۶ بر اساس دسته‌بندی
   "categories": {
     "quick": {
-      "models": ["kimi/kimi-k3"],
-      "description": "Single-file changes, typos, quick fixes"
+      "models": [
+        "deepseek/deepseek-v4-flash-0731",
+        "qwen/qwen3.7-flash",
+        "z-ai/glm-5.3-flash"
+      ],
+      "description": "Ultra-cheap, fast single-file edits, typos, and formatting"
     },
     "deep": {
-      "models": ["openai/gpt-5.6-sol", "gemini/gemini-2.5-pro"],
+      "models": [
+        "google/gemini-3.7-flash",
+        "z-ai/glm-5.3-flash",
+        "deepseek/deepseek-v4-flash-0731"
+      ],
       "reasoning": "medium",
-      "description": "Autonomous research + execution"
+      "description": "High-reasoning architecture, planning, and QA review"
     },
     "visual": {
-      "models": ["anthropic/claude-opus-5", "kimi/kimi-k3"],
-      "reasoning": "max",
-      "description": "Frontend, UI/UX, design"
+      "models": [
+        "google/gemini-3.7-flash",
+        "qwen/qwen3.7-flash"
+      ],
+      "description": "Frontend, UI/UX, and multimodal validation"
     },
     "unspecified": {
-      "models": ["gemini/gemini-2.5-flash", "kimi/kimi-k3"],
-      "description": "Default fallback"
+      "models": [
+        "deepseek/deepseek-v4-flash-0731",
+        "google/gemini-3.7-flash"
+      ],
+      "description": "Default fallback tier"
     }
   },
 
+  // محدودیت هم‌زمانی درخواست‌ها
   "provider_concurrency": {
-    "anthropic": 3,
-    "openai": 3,
-    "opencode": 10,
-    "kimi": 5
-  },
-
-  "max_parallel_tasks": 1,
-
-  "idle": {
-    "thinking_timeout_seconds": 60,
-    "executing_timeout_seconds": 900,
-    "max_retries": 5,
-    "no_progress_threshold": 50,
-    "no_progress_turns_before_pause": 2,
-    "min_delay_seconds": 2.0
+    "google": 5,
+    "deepseek": 5,
+    "qwen": 5,
+    "z-ai": 5,
+    "openrouter": 10,
+    "opencode": 10
   },
 
+  // تنظیمات ربات تلگرام و Chat ID شما
   "approval": {
     "bot_token_env": "TELEGRAM_BOT_TOKEN",
-    "chat_id": 0,
+    "chat_id": 1247026399,
     "timeout_seconds": 3600
   },
 
+  "max_parallel_tasks": 1,
   "max_qa_retries": 3,
   "evidence_dir": "loop-engine/evidence",
 
-  // --- Task Entry Trigger Gate ---
-  // Controls how tasks enter the execution loop.
-  // "telegram_button" = admin taps [🚀 Start Execution] in Telegram (default)
-  // "command_only"    = admin runs /run <task_id> in Telegram
-  // "auto"            = legacy: auto-pickup on file detection (no admin gate)
+  // حالت شروع با تایید در تلگرام
   "trigger_mode": "telegram_button",
-
-  // If true, existing backlog tasks run immediately on daemon boot.
-  // If false (default), they are registered as PENDING_TRIGGER and await admin action.
   "auto_start_on_boot": false,
 
   "system_prompt_path": "system-prompt.md",
   "tasks_dir": "tasks",
   "agmd_path": "AGENTS.md",
-  "conventions_path": "docs/conventions.md"
+  "conventions_path": "docs/conventions.md",
+  "stacks_dir": "stacks",
+  "default_stack": "generic"
 }
diff --git a/loop-engine/router.py b/loop-engine/router.py
index f37dacd..6dd1d1c 100644
--- a/loop-engine/router.py
+++ b/loop-engine/router.py
@@ -11,6 +11,7 @@ Reads system-prompt.md + AGENTS.md + docs/conventions.md on every invocation.
 """
 
 import os
+from datetime import datetime, timezone
 from pathlib import Path
 from typing import Any, Optional
 
@@ -197,13 +198,35 @@ class LLMRouter:
     def route_plan(self, task_content: str, category: str = "unspecified",
                    extra_context: str = "",
                    stack_profile: Optional[Any] = None) -> dict:
-        user = f"Generate implementation blueprint:\n\n{task_content}"
+        user = (
+            "Generate the DIRECT implementation blueprint for the Hands "
+            "executor to execute immediately. Requirements:\n"
+            "- Concrete, file-level steps: exact paths, function/method names, "
+            "and verification commands.\n"
+            "- Resolve ambiguity yourself from AGENTS.md, DESIGN.md, "
+            "docs/conventions.md, and the memory context. Do NOT emit "
+            "meta-requests for discovery, questions back to the caller, or "
+            "placeholder stubs.\n"
+            "- Map each step to the task's acceptance criteria and include a "
+            "risk/rollback note.\n\n"
+            f"## Task\n\n{task_content}"
+        )
         if extra_context:
             user += f"\n\nIncorporate this brainstorming session output:\n\n{extra_context}"
         model, reasoning = self._resolve_model(category, stack_profile=stack_profile)
+        system = self._build_system_context("architect")
+        system += (
+            "\n\n<deliverable>\n"
+            "PLANNING output MUST be the direct implementation blueprint: "
+            "concrete file-level steps, exact symbols, and verification "
+            "commands. Never respond with meta-requests for discovery or "
+            "clarification questions to the caller — produce the blueprint "
+            "itself.\n"
+            "</deliverable>"
+        )
         return {
             "model": model, "reasoning": reasoning,
-            "system": self._build_system_context("architect"),
+            "system": system,
             "user": user,
             "temperature": 0.3,
         }
@@ -253,7 +276,28 @@ class LLMRouter:
             if reasoning:
                 kwargs["reasoning_effort"] = reasoning
             response = litellm.completion(**kwargs)
-            return response.choices[0].message.content
+            content = response.choices[0].message.content
+
+            # Debug telemetry (HOTFIX-03): raw request/response logging.
+            # Opt-in ONLY via LOOP_ENGINE_DEBUG=1 — zero impact in normal runs.
+            if os.environ.get("LOOP_ENGINE_DEBUG") == "1":
+                try:
+                    log_dir = Path(__file__).resolve().parent / "logs"
+                    log_dir.mkdir(parents=True, exist_ok=True)
+                    entry = (
+                        f"\n===== [{datetime.now(timezone.utc).isoformat(timespec='seconds')}Z] "
+                        f"model={routing.get('model')} =====\n"
+                        f"--- SYSTEM ---\n{routing.get('system')}\n"
+                        f"--- USER ---\n{routing.get('user')}\n"
+                        f"--- RESPONSE ---\n{content}\n"
+                        f"===== END =====\n"
+                    )
+                    with open(log_dir / "llm_requests.log", "a", encoding="utf-8") as f:
+                        f.write(entry)
+                except Exception as log_e:
+                    print(f"[router] debug telemetry log error: {log_e}")
+
+            return content
         except ImportError as e:
             raise RuntimeError(
                 f"litellm not installed. Run: pip install litellm ({e})") from e
diff --git a/loop-engine/test_polyglot_smoke.py b/loop-engine/test_polyglot_smoke.py
index 98c9f80..cc8125b 100644
--- a/loop-engine/test_polyglot_smoke.py
+++ b/loop-engine/test_polyglot_smoke.py
@@ -472,6 +472,7 @@ class AutoApproveGateway(ApprovalGateway):
         self.plan_approvals = 0
         self.closure_approvals = 0
         self.trigger_cards = []
+        self.trigger_summaries = []
 
     async def request_approval(self, task_id, stage, content):
         if stage == "Plan Approval":
@@ -486,6 +487,11 @@ class AutoApproveGateway(ApprovalGateway):
         self.trigger_cards.append((task_id, title, file_path))
         return True
 
+    async def send_boot_scan_summary(self, tasks, top_n=4):
+        self.trigger_summaries.append(
+            (len(tasks), [t["task_id"] for t in tasks]))
+        return True
+
 
 # ---------------------------------------------------------------------------
 # Happy-path E2E smoke tests
@@ -808,12 +814,13 @@ def test_smoke_qa_failure_retries_with_feedback(tmp_path):
 
 
 def test_smoke_boot_scan_registers_pending_trigger(tmp_path):
-    """Daemon boot_scan registers backlog tasks as PENDING_TRIGGER + sends trigger cards.
+    """Daemon boot_scan registers backlog tasks as PENDING_TRIGGER + sends ONE
+    consolidated trigger summary (HOTFIX-02 anti-flood: no per-task cards).
 
-    daemon.boot_scan constructs KanbanWatcher without an explicit tasks_dir (it defaults
-    to CWD-relative "tasks/backlog"). For hermeticity we patch the class with a factory
-    that forwards config.tasks_dir, so boot_scan scans the temp workspace and never
-    registers unrelated real-repo backlog files.
+    daemon.boot_scan constructs KanbanWatcher without an explicit tasks_dir (it
+    defaults to CWD-relative "tasks/backlog"). For hermeticity we patch the
+    class with a factory that forwards config.tasks_dir, so boot_scan scans the
+    temp workspace and never registers unrelated real-repo backlog files.
     """
     from watcher import KanbanWatcher as RealKanbanWatcher
     import watcher as watcher_module
@@ -837,8 +844,12 @@ def test_smoke_boot_scan_registers_pending_trigger(tmp_path):
         tid = existing[0]["task_id"]
         rec = ws.state.get_task(tid)
         assert rec["state"] == "pending_trigger"
-        assert len(ws.gateway.trigger_cards) == 1
-        assert ws.gateway.trigger_cards[0][0] == tid
+        # HOTFIX-02: boot scan sends ONE consolidated summary, never per-task cards.
+        assert len(ws.gateway.trigger_cards) == 0
+        assert len(ws.gateway.trigger_summaries) == 1
+        count, ids = ws.gateway.trigger_summaries[0]
+        assert count == 1
+        assert ids == [tid]
     finally:
         ws.close()
```
<!-- END_GIT_DIFF -->