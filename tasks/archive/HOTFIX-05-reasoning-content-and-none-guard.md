# Task HOTFIX-05: Reasoning Content and None Guard

**File:** `tasks/archive/HOTFIX-05-reasoning-content-and-none-guard.md`
**Source:** orchestrator
**Type:** improvement
**Status:** superseded
**Superseded-By:** `149-hotfix-bundle-telegram-gateway-telemetry-path-reasoning-concurrency`
**Superseded-At:** `2026-09-01`
**Mode:** lite

## Goal

Harden the LLM response path and the approval gateway against two failure modes: (1) thinking/reasoning models that return reasoning tokens instead of a plain `content` field in `router.call_llm` — extract content with a fallback chain (`content` → `reasoning_content`/`reasoning` → stringified message) and strip; (2) `None`/empty approval bodies passed to `gateway.request_approval` — coerce to a defensible string and use it consistently throughout (including the `len(content_str) > 3000` document branch).

## Local TODOs

- [ ] Read AGENTS.md, docs/conventions.md, router.py, gateway.py
- [ ] Step 1 — router.py `call_llm`: safe content extraction with reasoning fallback + `.strip()`
- [ ] Step 2 — gateway.py `request_approval`: `content_str` None-guard at method head; use `content_str` everywhere
- [ ] Run pytest suite — verify no regressions

## Acceptance Criteria

- [x] `call_llm` extracts `msg.content`, falls back to `reasoning_content`/`reasoning`, then `str(msg)`, and returns `.strip()` — never raises on a missing content field
- [x] `request_approval` coerces `None`/blank content to a descriptive placeholder at the method head and uses `content_str` for the `>3000` document branch, inline truncation, temp file write, and the telemetry log entry
- [x] Full test suite passes: `uv run --project loop-engine --with pytest pytest loop-engine/ -q`

## Verification Evidence

- **Test command:** `uv run --project loop-engine --with pytest pytest loop-engine/ -q`
- **Expected result:** all tests green, 0 failures, 0 regressions
- **Actual result:** 247 passed, 0 failed in 13.26s. Functional harness verified all extraction branches (plain content strip, `content=None` → `reasoning_content`, `reasoning` attr, empty message → non-empty `str(msg)` without crash) and the gateway None-body guard (inline message rendered `[Plan Approval for Task #7] (No text body provided)`, no TypeError).
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Manager Decisions

- **[2026-08-31] [D1] [LITE]:** Orchestrator tagged this task `lite_mode` (2 source files + task recreation).
  - **Rationale:** Both steps fully specified with exact code; both are localized hardening edits with zero architectural ambiguity.
  - **Alternatives considered:** Escalating to Full Mode — unnecessary for a specified hotfix.
  - **Impact:** Expedited workflow applied; standard QA + full end-of-task sequence still enforced.
- **[2026-08-31] [D2] [EXECUTOR-DETECTED]:** Task file was absent from all Kanban directories despite Orchestrator metadata; recreated at the exact Orchestrator-specified path (same pattern as HOTFIX-01..04).
  - **Rationale:** XML block contained the full spec; halting would block the hotfix.
  - **Alternatives considered:** HALT and request clarification.
  - **Impact:** Single-source-of-truth maintained.
- **[2026-08-31] [D3] [EXECUTION-DETECTED]:** The HOTFIX-03 debug-telemetry block in `call_llm` logs `content` — with the new fallback extraction, the log now records the RESOLVED content (reasoning fallback applied), which is the intended observability surface.
  - **Rationale:** The variable was already named `content` and remains set; no change needed to the logging block.
  - **Alternatives considered:** Logging the raw message too — rejected: YAGNI, and raw reasoning tokens bloat the log.
  - **Impact:** Debug logs reflect what actually flows downstream.
- **[2026-08-31] [D4] [EXECUTION-DETECTED]:** `content_str` placeholder (spec) uses the STAGE+task, not the raw content — this also means the HOTFIX-02 `>3000` document branch can never be hit for empty bodies (placeholder is short), so a `None` body always goes inline. Confirmed intended.
  - **Rationale:** A placeholder body as a document would be absurd; inline with explanatory text is correct UX.
  - **Alternatives considered:** Forcing document delivery for empty bodies — rejected.
  - **Impact:** None-body approvals render inline with the placeholder caption.

## Risk & Rollback

- **Risk:** Fallback to `str(msg)` for empty content could surface a Python object repr as a "plan" and get approved.
- **Rollback plan:** Revert the fallback chain to the original `content` access; the reasoning fallback is additive (only when content is empty/None).
- **Risk:** `content_str` substitution could miss a `content` reference and change behavior inconsistently.
- **Rollback plan:** Full-suite run + targeted functional check of both branches (None guard, document path) — revert if any drift.
- **Risk:** `.strip()` on content could alter whitespace-sensitive plans.
- **Rollback plan:** Strip is trailing-only safe; trivial revert if a consumer depends on raw leading/trailing whitespace.

---

> **Superseded:** This task was bundled into META task `149-hotfix-bundle-telegram-gateway-telemetry-path-reasoning-concurrency` and archived on 2026-09-01. See `tasks/qa/149-hotfix-bundle-telegram-gateway-telemetry-path-reasoning-concurrency.md` for the unified execution. History preserved via `git log --follow -- tasks/archive/HOTFIX-05-reasoning-content-and-none-guard.md`.

## Execution Log & Reasoning

**2026-08-31 — HOTFIX-05 applied (Plan→Execute→Observe):**

1. **Verify-before-apply:** Confirmed no test couples to the raw `response.choices[0].message.content` expression (test_router calls `_build_system_context`/route helpers; the polygon smoke suite overrides `call_llm` in `ScriptedRouter`; `test_polyglot_smoke.AutoApproveGateway` overrides `request_approval`; test_le0_fixes uses stubs). The gateway guard only changes the body string, not the blocking/event flow.
2. **Step 1 — router.py:** replaced `content = response.choices[0].message.content` with the spec's extraction: `msg = response.choices[0].message`; `content = getattr(msg, "content", None) or ""`; fallback to `reasoning_content` then `reasoning` (both via getattr, stringified); last-resort `str(msg)`; final `.strip()`. The HOTFIX-03 telemetry block logs the resolved `content` (D3).
3. **Step 2 — gateway.py:** added the `content_str` None-guard at the method head (placeholder `[{stage} for Task #{task_id}] (No text body provided)`); substituted `content_str` for every body reference — `len(content_str) > 3000` document branch, temp-file write, inline `content_str[:1500]`, and the `_log_event` `content_len`. Signature keeps the original `content: str` parameter name.
4. **Observe:** functional harness — plain-content strip PASS, `content=None`+`reasoning_content` PASS, `reasoning` attr PASS, empty message → non-empty `str(msg)` without crash PASS, gateway `request_approval(7, "Plan Approval", None)` rendered the placeholder inline with NO TypeError PASS. Full suite **247 passed, 0 failed** (13.26s).
5. **Scope guard:** files changed: `loop-engine/router.py`, `loop-engine/gateway.py`, task file, CHANGELOG. Out-of-band files untouched; prior hotfix staged artifacts still in the index under the accumulated-staging model.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.env.example b/.env.example
index ede5327..8dbdefb 100644
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
index f098984..e8786ee 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Reasoning Content & None Guard (Task HOTFIX-05)** — hardened the LLM response path and approval gateway. `LLMRouter.call_llm` now extracts content safely from thinking/reasoning models: `content = getattr(msg, "content", None) or ""`, fallback to `reasoning_content` then `reasoning` (stringified), last-resort `str(msg)`, and returns `.strip()` — never raises on a missing content field (`loop-engine/router.py`; the HOTFIX-03 telemetry block logs the resolved content). `ApprovalGateway.request_approval` coerces `None`/blank bodies at the method head into a descriptive placeholder (`[{stage} for Task #{task_id}] (No text body provided)`) and uses the resulting `content_str` consistently across the `len() > 3000` document branch, temp-file write, inline truncation, and the telemetry `content_len` entry — no `NoneType` can reach `len()`/format paths (`loop-engine/gateway.py`). Verified with a functional harness (plain-content strip, reasoning_content fallback, reasoning-attr fallback, str(msg) last resort, None-body inline placeholder without TypeError) plus the full suite: **247 passed, 0 failed** via `uv run --project loop-engine --with pytest pytest loop-engine/ -q` (baseline 247).
+- **Dynamic Task Path Resolution (Task HOTFIX-04)** — added `resolve_actual_task_path(task_file, repo_root)` to `loop-engine/daemon.py`: returns the recorded path unchanged when it still exists on disk, otherwise searches all standard Kanban folders (`in-progress` → `qa` → `backlog` → `completed`) for the same filename and returns the resolved absolute path plus repo-relative path, falling back to the recorded path when not found anywhere. Integrated at the start of `LoopEngineDaemon.trigger_task` (replaces the direct `Path(task_file)` existence check; best-effort `UPDATE tasks SET task_file=... WHERE task_id=...` re-syncs the state DB when the file moved across Kanban directories, then launches processing with the resolved path) and `process_task` (resolves + re-syncs best-effort, forwards the resolved path into `_process_task`), plus `_process_task` itself resolves at its head for defense-in-depth so the fresh content read always targets the real on-disk file. Semantics verified with a functional harness (identity, moved-found across all folders, missing, search order, identity-wins-over-duplicates); dead local `from pathlib import Path` import in `trigger_task` removed. Verified **247 passed, 0 failed** via `uv run --project loop-engine --with pytest pytest loop-engine/ -q` (baseline 247).
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
diff --git a/loop-engine/blast_radius.py b/loop-engine/blast_radius.py
new file mode 100644
index 0000000..2413d92
--- /dev/null
+++ b/loop-engine/blast_radius.py
@@ -0,0 +1,556 @@
+"""
+Monorepo Blast-Radius Analyzer & Affected Path Matrix (LE-9 / Task 141).
+
+Deterministic, side-effect-free analysis of task diffs against monorepo
+workspaces: given the list of files modified by a task, discover the packages
+under ``workspace_root``, map their local dependency edges, and compute the
+exact affected dependency matrix — the directly modified packages PLUS every
+package that (transitively) depends on them.
+
+The matrix feeds the toolchain verification gate (``ToolchainRunner`` in
+``verifier.py``) so lint/build/test is skipped for *completely unaffected*
+workspaces and strictly scoped to impacted modules. The analyzer is
+deliberately conservative: when it cannot PROVE a workspace is unaffected
+(non-monorepo layout, unreadable manifests, root-owned files), it reports it
+as affected so verification always runs. False-negative skips of actually
+affected modules are the failure mode this guard rails against (see the
+Risk & Rollback section of Task 141).
+
+Design notes:
+- Package discovery is manifest-driven (``os.walk`` with noise-dir pruning)
+  plus root ``package.json`` ``workspaces`` globs (npm/yarn/pnpm-style).
+- Dependency edges come from explicit local references (``workspace:*``,
+  ``file:../x``, relative paths, Go ``replace ... => ../x``, uv ``sources``
+  path map) and from plain references to another discovered package's name.
+- Manifest parsers are implemented for package.json / pyproject.toml / go.mod;
+  other manifests (Cargo.toml, composer.json, gradle, pom.xml) act as package
+  boundaries only and contribute no dependency edges.
+- Diff-path parsing replicates the tiny ``_DIFF_HEADER_RE`` helper from
+  ``specs.py``/``contracts.py`` (established in-repo pattern, no cross-module
+  imports so this stays dependency-light).
+"""
+
+from __future__ import annotations
+
+import json
+import os
+import re
+import tomllib
+from pathlib import Path
+
+from models import BlastRadiusMatrix, PackageDependency, PackageInfo
+
+# Matches `diff --git a/<old> b/<new>` header lines — the b-side path is the
+# post-change relative path we care about (mirrors specs.py / contracts.py).
+_DIFF_HEADER_RE = re.compile(r"^diff --git a/(.+?) b/(.+?)\n", re.MULTILINE)
+
+# Pseudo-manifest sentinel for workspace-glob packages that have no real
+# manifest file (e.g. a workspaces glob pointing at an empty dir).
+_PSEUDO_MANIFEST = "<workspaces glob>"
+
+# Directories that never contain a package boundary (pruned during discovery).
+_EXCLUDED_DIR_NAMES = {
+    ".git", ".idea", ".vscode", ".venv", ".opencode", ".pytest_cache",
+    "__pycache__", "node_modules", "venv", "dist", "build", "target",
+    "coverage", "htmlcov", "state", "evidence", ".tox", ".mypy_cache",
+    ".ruff_cache",
+}
+
+# Manifest precedence when a directory contains several (pick the winner).
+_MANIFEST_PRECEDENCE = (
+    "package.json",
+    "pyproject.toml",
+    "go.mod",
+    "Cargo.toml",
+    "composer.json",
+    "build.gradle.kts",
+    "build.gradle",
+    "pom.xml",
+)
+
+_GO_MODULE_RE = re.compile(r"^\s*module\s+(\S+)", re.MULTILINE)
+_GO_SINGLE_REQUIRE_RE = re.compile(r"^\s*require\s+(\S+)")
+_GO_REPLACE_RE = re.compile(r"^\s*replace\s+(\S+)(?:\s+\S+)?\s*=>\s*(\S+)")
+_PY_REQUIREMENT_NAME_RE = re.compile(r"^([A-Za-z0-9_.-]+)")
+
+
+def extract_modified_paths(diff_text: str) -> list[str]:
+    """Return deduplicated relative paths of files touched by a git diff.
+
+    Parses ``diff --git a/x b/y`` headers (b-side path) and preserves
+    first occurrence order. Empty/malformed diffs yield ``[]``.
+    """
+    paths: list[str] = []
+    seen: set[str] = set()
+    for match in _DIFF_HEADER_RE.finditer(diff_text or ""):
+        path = match.group(2)
+        if path not in seen:
+            seen.add(path)
+            paths.append(path)
+    return paths
+
+
+# ---------------------------------------------------------------------------
+# Package discovery
+# ---------------------------------------------------------------------------
+
+
+def discover_packages(workspace_root: str | Path) -> list[PackageInfo]:
+    """Discover monorepo packages under ``workspace_root``.
+
+    Scans for manifest files (package.json, pyproject.toml, go.mod,
+    Cargo.toml, composer.json, gradle/pom markers) while pruning noise
+    directories, then additionally resolves root ``package.json``
+    ``workspaces`` globs (npm/yarn/pnpm) so un-manifested workspace dirs
+    are still tracked. Returns a deterministic path-sorted list (root
+    package ``"."`` first when the root itself carries a manifest).
+    """
+    root = Path(workspace_root)
+    packages: dict[str, PackageInfo] = {}
+    if not root.exists():
+        return []
+
+    # 1. Manifest-file discovery (top-down walk with in-place pruning)
+    for dirpath, dirnames, filenames in os.walk(root):
+        dirnames[:] = sorted(
+            d for d in dirnames
+            if d not in _EXCLUDED_DIR_NAMES and not d.startswith(".")
+        )
+        manifest = _first_manifest(filenames)
+        if manifest is None:
+            continue
+        dirpath_p = Path(dirpath)
+        rel = dirpath_p.relative_to(root).as_posix()
+        name = _manifest_name(manifest, dirpath_p / manifest, rel)
+        packages[rel] = PackageInfo(name=name, path=rel, manifest=manifest)
+
+    # 2. Root package.json workspaces globs (additional package dirs)
+    root_pkg = root / "package.json"
+    if root_pkg.is_file():
+        try:
+            data = json.loads(root_pkg.read_text(encoding="utf-8"))
+        except Exception:
+            data = {}
+        workspaces = data.get("workspaces") or []
+        if isinstance(workspaces, list):
+            for pattern in workspaces:
+                if not isinstance(pattern, str):
+                    continue
+                for match in sorted(root.glob(pattern)):
+                    if not match.is_dir():
+                        continue
+                    rel = match.relative_to(root).as_posix()
+                    if rel not in packages:
+                        packages[rel] = PackageInfo(
+                            name=_dir_fallback_name(rel),
+                            path=rel,
+                            manifest=_PSEUDO_MANIFEST,
+                        )
+
+    return [packages[path] for path in sorted(packages, key=_package_sort_key)]
+
+
+def find_owning_package(
+    file_rel: str, packages: list[PackageInfo]
+) -> PackageInfo | None:
+    """Return the deepest package whose directory prefixes ``file_rel``.
+
+    The root package (``path == "."``) is the last-resort owner for any
+    file not under a deeper package. Returns ``None`` only when the
+    workspace has no root package and no deeper package owns the file.
+    """
+    best = None
+    best_parts = -1
+    for pkg in packages:
+        if pkg.path == ".":
+            continue
+        if file_rel == pkg.path or file_rel.startswith(pkg.path + "/"):
+            parts = pkg.path.count("/")
+            if parts > best_parts:
+                best = pkg
+                best_parts = parts
+    if best is not None:
+        return best
+    for pkg in packages:
+        if pkg.path == ".":
+            return pkg
+    return None
+
+
+# ---------------------------------------------------------------------------
+# Dependency graph
+# ---------------------------------------------------------------------------
+
+
+def build_dependency_map(
+    packages: list[PackageInfo], workspace_root: str | Path
+) -> list[PackageDependency]:
+    """Build local dependency edges for every discovered package.
+
+    Edges are local-only: a package depends on another package when its
+    manifest references it via an explicit path (``workspace:*``,
+    ``file:../x``, relative path, Go ``replace``, uv ``sources``) or by
+    name matching a discovered package. Deterministic sorted lists.
+    """
+    root = Path(workspace_root)
+    by_name: dict[str, PackageInfo] = {p.name: p for p in packages}
+    abs_by_path: dict[Path, PackageInfo] = {}
+    for p in packages:
+        try:
+            abs_by_path[(root / p.path).resolve()] = p
+        except OSError:
+            continue
+
+    result: list[PackageDependency] = []
+    for pkg in packages:
+        edges: set[str] = set()
+        if pkg.manifest != _PSEUDO_MANIFEST:
+            manifest_path = root.joinpath(pkg.path, pkg.manifest)
+            if manifest_path.is_file():
+                if pkg.manifest == "package.json":
+                    edges |= _node_deps(
+                        manifest_path, abs_by_path, by_name
+                    )
+                elif pkg.manifest == "pyproject.toml":
+                    edges |= _python_deps(
+                        manifest_path, abs_by_path, by_name
+                    )
+                elif pkg.manifest == "go.mod":
+                    edges |= _go_deps(
+                        manifest_path, abs_by_path, by_name
+                    )
+        result.append(
+            PackageDependency(
+                package=pkg.name, path=pkg.path, depends_on=sorted(edges)
+            )
+        )
+    return result
+
+
+# ---------------------------------------------------------------------------
+# Public API — the acceptance-criteria entry point
+# ---------------------------------------------------------------------------
+
+
+def calculate_affected_paths(
+    modified_files: list[str], workspace_root: str | Path
+) -> BlastRadiusMatrix:
+    """Compute the affected dependency matrix for a set of modified files.
+
+    Mapping: every modified file is owned by the deepest discovered
+    package whose directory is a prefix of the file path (files outside
+    every package become ``root_owned_files``). The affected set is the
+    direct owners PLUS the transitive closure of packages that depend on
+    them. Unaffected packages are the discovered packages outside that
+    closure. Output lists are deterministically sorted.
+    """
+    root = Path(workspace_root)
+    normalized = sorted(set(_normalize_file(f) for f in (modified_files or [])))
+    normalized = [f for f in normalized if f]
+
+    packages = discover_packages(root)
+    dep_map = build_dependency_map(packages, root)
+    deps_by_pkg: dict[str, set[str]] = {
+        d.package: set(d.depends_on) for d in dep_map
+    }
+
+    affected: set[str] = set()
+    root_owned: list[str] = []
+    for f in normalized:
+        owner = find_owning_package(f, packages)
+        if owner is None:
+            root_owned.append(f)
+        else:
+            affected.add(owner.name)
+
+    # Transitive closure over reverse edges: any package that
+    # (transitively) depends on an affected package is itself affected.
+    if affected:
+        changed = True
+        while changed:
+            changed = False
+            for pkg_name, deps in deps_by_pkg.items():
+                if pkg_name not in affected and deps & affected:
+                    affected.add(pkg_name)
+                    changed = True
+
+    affected_names = sorted(affected)
+    affected_objs = [p for p in packages if p.name in affected_names]
+    affected_paths = sorted(p.path for p in affected_objs)
+    unaffected = sorted(p.name for p in packages if p.name not in affected_names)
+
+    return BlastRadiusMatrix(
+        modified_files=normalized,
+        packages=packages,
+        dependency_map=dep_map,
+        affected_packages=affected_names,
+        affected_paths=affected_paths,
+        unaffected_packages=unaffected,
+        root_owned_files=root_owned,
+    )
+
+
+# ---------------------------------------------------------------------------
+# Manifest parsers
+# ---------------------------------------------------------------------------
+
+
+def _node_deps(
+    manifest_path: Path,
+    abs_by_path: dict[Path, PackageInfo],
+    by_name: dict[str, PackageInfo],
+) -> set[str]:
+    """Parse package.json dependency sections into local edges."""
+    try:
+        data = json.loads(manifest_path.read_text(encoding="utf-8"))
+    except Exception:
+        return set()
+    edges: set[str] = set()
+    sections = (
+        "dependencies",
+        "devDependencies",
+        "peerDependencies",
+        "optionalDependencies",
+    )
+    for section in sections:
+        deps = data.get(section) or {}
+        if not isinstance(deps, dict):
+            continue
+        for dep_name, raw_spec in deps.items():
+            spec = str(raw_spec or "")
+            if spec.startswith("workspace:"):
+                if dep_name in by_name:
+                    edges.add(dep_name)
+                continue
+            local = _resolve_local_reference(
+                spec, manifest_path.parent, abs_by_path
+            )
+            if local is not None:
+                edges.add(local)
+                continue
+            if dep_name in by_name:
+                edges.add(dep_name)
+    return edges
+
+
+def _python_deps(
+    manifest_path: Path,
+    abs_by_path: dict[Path, PackageInfo],
+    by_name: dict[str, PackageInfo],
+) -> set[str]:
+    """Parse pyproject.toml project/optional dependencies and uv sources."""
+    try:
+        data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
+    except Exception:
+        return set()
+    edges: set[str] = set()
+    project = data.get("project") or {}
+
+    deps = project.get("dependencies") or []
+    if isinstance(deps, list):
+        for spec in deps:
+            _maybe_py_name_edge(spec, by_name, edges)
+
+    optional = project.get("optional-dependencies") or {}
+    if isinstance(optional, dict):
+        for specs in optional.values():
+            if isinstance(specs, list):
+                for spec in specs:
+                    _maybe_py_name_edge(spec, by_name, edges)
+
+    # uv source map: {pkg: {"path": "../x"}} — explicit local references
+    uv_sources = ((data.get("tool") or {}).get("uv") or {}).get("sources") or {}
+    if isinstance(uv_sources, dict):
+        for dep_name, source in uv_sources.items():
+            if isinstance(source, dict) and isinstance(source.get("path"), str):
+                local = _resolve_local_reference(
+                    source["path"], manifest_path.parent, abs_by_path
+                )
+                if local is not None:
+                    edges.add(local)
+                elif dep_name in by_name:
+                    edges.add(dep_name)
+    return edges
+
+
+def _maybe_py_name_edge(
+    spec: str, by_name: dict[str, PackageInfo], edges: set[str]
+) -> None:
+    """Add a name edge when a requirement spec names a discovered package."""
+    if not isinstance(spec, str):
+        return
+    match = _PY_REQUIREMENT_NAME_RE.match(spec.strip())
+    if match and match.group(1) in by_name:
+        edges.add(match.group(1))
+
+
+def _go_deps(
+    manifest_path: Path,
+    abs_by_path: dict[Path, PackageInfo],
+    by_name: dict[str, PackageInfo],
+) -> set[str]:
+    """Parse go.mod requires (name refs) and replaces (local path refs)."""
+    try:
+        text = manifest_path.read_text(encoding="utf-8")
+    except Exception:
+        return set()
+    edges: set[str] = set()
+    in_require_block = False
+    in_replace_block = False
+    base_dir = manifest_path.parent
+    for raw in text.splitlines():
+        line = raw.strip()
+        if not line or line.startswith("//"):
+            continue
+        if line == "require (":
+            in_require_block = True
+            continue
+        if line == ")" and in_require_block:
+            in_require_block = False
+            continue
+        if line == "replace (":
+            in_replace_block = True
+            continue
+        if line == ")" and in_replace_block:
+            in_replace_block = False
+            continue
+        if in_require_block:
+            parts = line.split()
+            if parts and parts[0] in by_name:
+                edges.add(parts[0])
+            continue
+        if in_replace_block:
+            match = re.match(r"^(\S+)(?:\s+\S+)?\s*=>\s*(\S+)", line)
+            if match:
+                _maybe_go_replace_edge(
+                    match.group(2), base_dir, abs_by_path, edges
+                )
+            continue
+        if line.startswith("replace"):
+            repl = _GO_REPLACE_RE.match(line)
+            if repl:
+                _maybe_go_replace_edge(
+                    repl.group(2), base_dir, abs_by_path, edges
+                )
+            continue
+        single = _GO_SINGLE_REQUIRE_RE.match(line)
+        if single:
+            token = single.group(1)
+            if token in by_name:
+                edges.add(token)
+    return edges
+
+
+def _maybe_go_replace_edge(
+    target: str,
+    base_dir: Path,
+    abs_by_path: dict[Path, PackageInfo],
+    edges: set[str],
+) -> None:
+    """Resolve a replace target path into a local dependency edge."""
+    local = _resolve_local_reference(target, base_dir, abs_by_path)
+    if local is not None:
+        edges.add(local)
+
+
+# ---------------------------------------------------------------------------
+# Reference resolution
+# ---------------------------------------------------------------------------
+
+
+def _resolve_local_reference(
+    spec: str, base_dir: Path, abs_by_path: dict[Path, PackageInfo]
+) -> str | None:
+    """Resolve an explicit local dependency reference to a package name.
+
+    Handles ``file:../x``, ``file:../x#fragment``, relative paths and
+    absolute paths. Returns the referenced package's name when the target
+    resolves to a discovered package directory, else ``None``.
+    """
+    if spec.startswith("workspace:"):
+        return None  # name-based; handled by callers
+    target: str | None = None
+    if spec.startswith("file:"):
+        target = spec[5:]
+    elif spec.startswith(".") or spec.startswith("/") or spec.startswith(os.sep):
+        target = spec
+    if target is None:
+        return None
+    target = target.split("#")[0].split("?")[0]
+    if not target:
+        return None
+    try:
+        resolved = (base_dir / target).resolve()
+    except OSError:
+        return None
+    info = abs_by_path.get(resolved)
+    return info.name if info is not None else None
+
+
+# ---------------------------------------------------------------------------
+# Manifest name / helpers
+# ---------------------------------------------------------------------------
+
+
+def _first_manifest(filenames: list[str]) -> str | None:
+    """Return the winning manifest filename by precedence, or None."""
+    names = set(filenames)
+    for manifest in _MANIFEST_PRECEDENCE:
+        if manifest in names:
+            return manifest
+    return None
+
+
+def _manifest_name(manifest: str, manifest_path: Path, rel: str) -> str:
+    """Extract the canonical package name from a manifest, else rel path."""
+    if manifest in ("package.json", "composer.json"):
+        try:
+            data = json.loads(manifest_path.read_text(encoding="utf-8"))
+            name = data.get("name") if isinstance(data, dict) else None
+            if isinstance(name, str) and name:
+                return name
+        except Exception:
+            pass
+    elif manifest == "pyproject.toml":
+        try:
+            data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
+            name = (data.get("project") or {}).get("name") if isinstance(data, dict) else None
+            if isinstance(name, str) and name:
+                return name
+        except Exception:
+            pass
+    elif manifest == "go.mod":
+        try:
+            text = manifest_path.read_text(encoding="utf-8")
+            match = _GO_MODULE_RE.search(text)
+            if match:
+                return match.group(1)
+        except Exception:
+            pass
+    elif manifest == "Cargo.toml":
+        try:
+            data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
+            name = (data.get("package") or {}).get("name") if isinstance(data, dict) else None
+            if isinstance(name, str) and name:
+                return name
+        except Exception:
+            pass
+    return rel
+
+
+def _dir_fallback_name(rel: str) -> str:
+    """Name for a manifestless workspace dir: its last path segment."""
+    return rel.rsplit("/", 1)[-1] or rel
+
+
+def _normalize_file(path) -> str:
+    """Normalize a modified-file path to a posix relative string."""
+    s = str(path).replace("\\", "/")
+    while s.startswith("./"):
+        s = s[2:]
+    return s
+
+
+def _package_sort_key(p: PackageInfo) -> tuple[int, str]:
+    """Sort root package ('.') first, then by path for determinism."""
+    return (0 if p.path == "." else 1, p.path)
\ No newline at end of file
diff --git a/loop-engine/daemon.py b/loop-engine/daemon.py
index 05f783b..9304dd2 100644
--- a/loop-engine/daemon.py
+++ b/loop-engine/daemon.py
@@ -119,6 +119,24 @@ EXEC_OK = "complete"
 EXEC_BLOCKED = "blocked"
 
 
+def resolve_actual_task_path(task_file: str, repo_root: Path) -> tuple[Path, str]:
+    """Dynamically find a task file across all Kanban folders if it was moved."""
+    p = Path(task_file)
+    if not p.is_absolute():
+        p = repo_root / task_file
+    if p.exists():
+        return p, task_file
+
+    # If not found at recorded path, search across all standard Kanban directories
+    filename = Path(task_file).name
+    for folder in ("in-progress", "qa", "backlog", "completed"):
+        candidate = repo_root / "tasks" / folder / filename
+        if candidate.exists():
+            rel_path = str(candidate.relative_to(repo_root))
+            return candidate, rel_path
+    return p, task_file
+
+
 def extract_task_diff(task_file: Path) -> str | None:
     """Extract ONLY the content between <!-- BEGIN_GIT_DIFF --> and <!-- END_GIT_DIFF -->.
 
@@ -386,8 +404,21 @@ async def process_task(task_id: int, task_file: str, config: LoopEngineConfig,
     """Full pipeline for one task."""
     print(f"\n[pipeline] Processing task #{task_id}: {task_file}")
 
+    # Dynamic path resolution (HOTFIX-04): the task may have moved across
+    # Kanban folders since registration. Re-sync the state DB best-effort and
+    # process from the actual on-disk path.
+    actual_path, actual_rel_path = resolve_actual_task_path(task_file, REPO_ROOT)
+    resolved_task_file = task_file
+    if actual_path.exists() and actual_rel_path != task_file:
+        try:
+            state.conn.execute("UPDATE tasks SET task_file = ? WHERE task_id = ?", (actual_rel_path, task_id))
+            state.conn.commit()
+        except Exception:
+            pass
+        resolved_task_file = actual_rel_path
+
     try:
-        await _process_task(task_id, task_file, config, state, router,
+        await _process_task(task_id, resolved_task_file, config, state, router,
                             gateway, executor, qa, brainstorm)
     except Exception as e:
         state.update_state(task_id, TaskState.CRASHED)
@@ -425,14 +456,23 @@ class LoopEngineDaemon:
 
         task_file = task_record["task_file"]
 
-        # Fresh read from disk
-        from pathlib import Path
-        task_path = Path(task_file)
+        # Fresh read from disk with dynamic path resolution (HOTFIX-04): the
+        # task may have been moved across Kanban folders after registration.
+        task_path, actual_rel_path = resolve_actual_task_path(task_file, REPO_ROOT)
         if not task_path.exists():
             print(f"[daemon] Task file not found: {task_file}")
             self.state.update_state(task_id, TaskState.CRASHED)
             return
 
+        # Sync state DB if the file was moved across Kanban folders
+        if actual_rel_path != task_file:
+            try:
+                self.state.conn.execute("UPDATE tasks SET task_file = ? WHERE task_id = ?", (actual_rel_path, task_id))
+                self.state.conn.commit()
+            except Exception:
+                pass
+            task_file = actual_rel_path
+
         # Transition PENDING_TRIGGER -> PLANNING
         self.state.update_state(task_id, TaskState.PLANNING)
         print(f"[daemon] Task #{task_id} triggered, transitioning to PLANNING...")
@@ -448,8 +488,9 @@ class LoopEngineDaemon:
 
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
@@ -465,26 +506,43 @@ class LoopEngineDaemon:
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
 
 
@@ -493,7 +551,11 @@ async def _process_task(task_id: int, task_file: str, config: LoopEngineConfig,
                         gateway: ApprovalGateway, executor: HandsExecutor,
                         qa: QAEngine, brainstorm: BrainstormStage):
     """Inner pipeline — exceptions propagate to process_task's guard."""
-    task_path = Path(task_file)
+    # Dynamic path resolution (HOTFIX-04): resolve the actual on-disk path so
+    # the fresh read below never fails on a stale recorded path after a Kanban
+    # move. Callers (process_task / trigger_task) already re-synced the DB.
+    task_file_path, _ = resolve_actual_task_path(task_file, REPO_ROOT)
+    task_path = task_file_path
     task_content = task_path.read_text(encoding="utf-8")
 
     # Stack detection (LE-1) — detect once at the start so planning, QA, and
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
index 0e77258..e36f8e6 100644
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
@@ -86,6 +107,11 @@ class ApprovalGateway:
 
     async def request_approval(self, task_id: int, stage: str, content: str) -> bool:
         """Send approval request with inline keyboard. Blocks until response."""
+        # Defensive string guard (HOTFIX-05): LLM/other callers may pass None or
+        # blank content — never let a NoneType reach len()/format paths.
+        content_str = str(content) if content is not None else ""
+        if not content_str.strip():
+            content_str = f"[{stage} for Task #{task_id}] (No text body provided)"
         key = f"{task_id}:{stage}"
 
         try:
@@ -99,19 +125,48 @@ class ApprovalGateway:
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
+            if len(content_str) > 3000:
+                # Long plan/blueprint content (HOTFIX-02): inline text would be
+                # unreadable and hit Telegram's message cap. Send the FULL
+                # Markdown as a document attachment with a short summary caption
+                # plus the same Approve/Reject buttons.
+                tmp_path = Path(f"/tmp/plan_task_{task_id}.md")
+                send_method = "document"
+                try:
+                    tmp_path.write_text(content_str, encoding="utf-8")
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
+                    f"{content_str[:1500]}\n\n"
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
+                f"content_len={len(content_str)} via={send_method}")
 
         except (ImportError, ValueError) as e:
             print(f"[gateway] Telegram unavailable: {e}")
@@ -142,6 +197,7 @@ class ApprovalGateway:
 
     def handle_callback(self, callback_data: str) -> Optional[str]:
         """Handle Telegram callback query. Returns acknowledgment message."""
+        self._log_event(f"callback_received data={callback_data!r}")
         # --- Approval callbacks (existing) ---
         if callback_data.startswith(("approve:", "reject:")):
             action, key = callback_data.split(":", 1)
@@ -202,17 +258,86 @@ class ApprovalGateway:
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
 
@@ -260,3 +385,29 @@ class ApprovalGateway:
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
index d6244c7..26f22f1 100644
--- a/loop-engine/loop-engine.jsonc
+++ b/loop-engine/loop-engine.jsonc
@@ -1,70 +1,71 @@
 {
-  // Cognitive Loop Engine Configuration
-  // API keys are loaded from environment variables (never stored here)
-
-  "default_provider": "gemini/gemini-2.5-flash",
+  // مدل پیش‌فرض: DeepSeek V4 Flash (سریع، ارزان و قدرتمند)
+  "default_provider": "openrouter/deepseek/deepseek-v4-flash-0731",
 
+  // روتینگ مدل‌های نسل جدید ۲۰۲۶ از درگاه OpenRouter
   "categories": {
     "quick": {
-      "models": ["kimi/kimi-k3"],
-      "description": "Single-file changes, typos, quick fixes"
+      "models": [
+        "openrouter/deepseek/deepseek-v4-flash-0731",
+        "openrouter/qwen/qwen3.7-flash",
+        "openrouter/z-ai/glm-5.3-flash"
+      ],
+      "description": "Ultra-cheap, fast single-file edits, typos, and formatting"
     },
     "deep": {
-      "models": ["openai/gpt-5.6-sol", "gemini/gemini-2.5-pro"],
+      "models": [
+        "openrouter/google/gemini-3.7-flash",
+        "openrouter/z-ai/glm-5.3-flash",
+        "openrouter/deepseek/deepseek-v4-flash-0731"
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
+        "openrouter/google/gemini-3.7-flash",
+        "openrouter/qwen/qwen3.7-flash"
+      ],
+      "description": "Frontend, UI/UX, and multimodal validation"
     },
     "unspecified": {
-      "models": ["gemini/gemini-2.5-flash", "kimi/kimi-k3"],
-      "description": "Default fallback"
+      "models": [
+        "openrouter/deepseek/deepseek-v4-flash-0731",
+        "openrouter/google/gemini-3.7-flash"
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
+    "openrouter": 10,
+    "google": 5,
+    "deepseek": 5,
+    "qwen": 5,
+    "z-ai": 5,
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
diff --git a/loop-engine/models.py b/loop-engine/models.py
index 384b40e..8be25c8 100644
--- a/loop-engine/models.py
+++ b/loop-engine/models.py
@@ -307,3 +307,48 @@ class LoopEngineConfig(BaseModel):
         default_factory=SpecGateConfig,
         description="Spec-first artifact governance: fail-fast gate requiring spec artifacts before implementation",
     )
+
+
+# --- Blast-Radius Analyzer (LE-9 / Task 141) ---
+
+
+class PackageInfo(BaseModel):
+    """A discovered monorepo package/workspace.
+
+    ``path`` is the package directory relative to the workspace root (posix,
+    ``"."`` for the root package itself when the root carries a manifest).
+    """
+
+    name: str = Field(..., description="Package name from its manifest, or the relative path when unnamed")
+    path: str = Field(..., description="Package directory relative to workspace root (posix), '.' for the root package")
+    manifest: str = Field(..., description="Manifest filename that defined the package, e.g. 'package.json'")
+
+
+class PackageDependency(BaseModel):
+    """One discovered package plus the local packages it depends on (LE-9)."""
+
+    package: str = Field(..., description="Name of the depending package")
+    path: str = Field(..., description="Relative directory of the depending package (posix)")
+    depends_on: list[str] = Field(
+        default_factory=list,
+        description="Names of local packages this package depends on (workspace/file/name references)",
+    )
+
+
+class BlastRadiusMatrix(BaseModel):
+    """Result of ``calculate_affected_paths`` — the affected dependency matrix.
+
+    ``affected_packages``/``affected_paths`` include the directly modified
+    packages PLUS every package that transitively depends on them (reverse
+    dependency closure). ``unaffected_packages`` are the discovered packages
+    with no path to any modified file. ``root_owned_files`` are modified files
+    that belong to no discovered package (repo-root configs, docs, etc.).
+    """
+
+    modified_files: list[str] = Field(default_factory=list, description="Normalized modified file paths analyzed")
+    packages: list[PackageInfo] = Field(default_factory=list, description="All discovered monorepo packages")
+    dependency_map: list[PackageDependency] = Field(default_factory=list, description="Local dependency edges per package")
+    affected_packages: list[str] = Field(default_factory=list, description="Names of directly/transitively affected packages")
+    affected_paths: list[str] = Field(default_factory=list, description="Relative directories of affected packages (posix)")
+    unaffected_packages: list[str] = Field(default_factory=list, description="Names of discovered packages NOT affected")
+    root_owned_files: list[str] = Field(default_factory=list, description="Modified files not owned by any package")
diff --git a/loop-engine/router.py b/loop-engine/router.py
index f37dacd..f453711 100644
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
@@ -253,7 +276,37 @@ class LLMRouter:
             if reasoning:
                 kwargs["reasoning_effort"] = reasoning
             response = litellm.completion(**kwargs)
-            return response.choices[0].message.content
+            msg = response.choices[0].message
+            # Extract content or fallback to reasoning_content for thinking models
+            content = getattr(msg, "content", None) or ""
+            if not content:
+                reasoning = getattr(msg, "reasoning_content", None) or getattr(msg, "reasoning", None)
+                if reasoning:
+                    content = str(reasoning)
+                else:
+                    content = str(msg)
+            content = content.strip()
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
 
diff --git a/loop-engine/verifier.py b/loop-engine/verifier.py
index bc41da4..dc11774 100644
--- a/loop-engine/verifier.py
+++ b/loop-engine/verifier.py
@@ -12,6 +12,11 @@ from dataclasses import dataclass, field
 from pathlib import Path
 
 from sentinel import TypeDriftSentinel
+from blast_radius import (
+    calculate_affected_paths,
+    extract_modified_paths,
+    find_owning_package,
+)
 
 
 @dataclass
@@ -46,9 +51,20 @@ class ToolchainRunner:
         self,
         timeout_per_command: float = 120.0,
         evidence_base_dir: str | Path = "loop-engine/evidence",
+        workspace_root: str | Path | None = None,
+        skip_unaffected: bool = True,
     ):
         self.timeout_per_command = timeout_per_command
         self.evidence_base_dir = Path(evidence_base_dir)
+        # Blast-radius scoping (LE-9 / Task 141): workspace_root defaults to
+        # the repo root (parent of loop-engine/). skip_unaffected is the
+        # rollback flag — set False to always run full toolchain verification.
+        self.workspace_root = (
+            Path(workspace_root)
+            if workspace_root is not None
+            else Path(__file__).resolve().parent.parent
+        )
+        self.skip_unaffected = skip_unaffected
 
     async def run(
         self,
@@ -87,6 +103,24 @@ class ToolchainRunner:
                 # daemon's toolchain-infra-error tolerance). Log to the result.
                 print(f"[verifier] Type Drift Sentinel error (proceeding): {e}")
 
+        # --- Blast-Radius Workspace Scoping (LE-9 / Task 141) ---
+        # When the task diff touches only a subset of monorepo workspaces, a
+        # completely unaffected workspace skips its lint/build/test (all
+        # commands reported SKIPPED, result passes). The analyzer is
+        # deliberately conservative: it only skips when it can PROVE the
+        # verified workspace is unaffected, so affected modules are never
+        # silently missed (Task 141 Risk & Rollback).
+        if self.skip_unaffected and diff_text and str(diff_text).strip():
+            blast_note = self._blast_radius_note(diff_text, cwd)
+            if blast_note:
+                skipped_commands: list[CommandResult] = [
+                    CommandResult(command="none", cmd_type=t, passed=True, skipped=True)
+                    for t in ("lint", "build", "test")
+                ]
+                return self._finalize(
+                    skipped_commands, task_id, blast_radius_note=blast_note
+                )
+
         # Defensive: profile may lack toolchain attr in mocks
         toolchain = getattr(profile, "toolchain", None)
         if toolchain is None:
@@ -207,7 +241,10 @@ class ToolchainRunner:
         return self._finalize(results, task_id)
 
     def _finalize(
-        self, commands: list[CommandResult], task_id: int | None
+        self,
+        commands: list[CommandResult],
+        task_id: int | None,
+        blast_radius_note: str = "",
     ) -> ToolchainResult:
         passed = all(c.passed for c in commands)
         # Summary: single line
@@ -220,9 +257,11 @@ class ToolchainRunner:
             else:
                 summary_parts.append(f"{c.cmd_type}: FAILED")
         summary = "Toolchain " + ("PASSED" if passed else "FAILED") + " | " + ", ".join(summary_parts)
+        if blast_radius_note:
+            summary += f" | {blast_radius_note}"
 
         # Markdown report with summary table and error logs
-        report_md = self._build_report_md(commands, passed, summary)
+        report_md = self._build_report_md(commands, passed, summary, blast_radius_note)
 
         result = ToolchainResult(
             passed=passed, commands=commands, summary=summary, report_md=report_md
@@ -246,13 +285,20 @@ class ToolchainRunner:
         return result
 
     def _build_report_md(
-        self, commands: list[CommandResult], passed: bool, summary: str
+        self,
+        commands: list[CommandResult],
+        passed: bool,
+        summary: str,
+        blast_radius_note: str = "",
     ) -> str:
         lines: list[str] = []
         lines.append("# Toolchain Verification Report")
         lines.append("")
         lines.append(summary)
         lines.append("")
+        if blast_radius_note:
+            lines.append(f"**Blast-radius scoping:** {blast_radius_note}")
+            lines.append("")
         lines.append(f"**Overall:** {'PASSED' if passed else 'FAILED'}")
         lines.append("")
         lines.append("| Type | Command | Result | Duration | Return Code |")
@@ -296,6 +342,61 @@ class ToolchainRunner:
                 lines.append("")
         return "\n".join(lines)
 
+    def is_workspace_affected(
+        self, diff_text: str, cwd: str | Path | None = None
+    ) -> bool:
+        """True when verification must run for the workspace at ``cwd``.
+
+        Returns False only when blast-radius analysis PROVES the workspace
+        (a discovered monorepo package, or the root package) is completely
+        unaffected by the diff. Conservative bias: any uncertainty — no cwd,
+        a non-monorepo layout, root-owned files, or a cwd outside the
+        package graph — returns True so the toolchain always runs.
+        """
+        return self._blast_radius_note(diff_text, cwd) == ""
+
+    def _blast_radius_note(self, diff_text: str, cwd: str | Path | None) -> str:
+        """Return a skip note when ``cwd`` is provably unaffected, else "".
+
+        The empty string means "run verification". A non-empty note is a
+        human-readable explanation appended to the summary/report so skipped
+        workspaces are observable in QA evidence.
+        """
+        if not cwd:
+            return ""
+        try:
+            cwd_path = Path(cwd).resolve()
+        except OSError:
+            return ""
+        try:
+            root = Path(self.workspace_root).resolve()
+        except OSError:
+            return ""
+        modified = extract_modified_paths(str(diff_text))
+        if not modified:
+            return ""
+        try:
+            matrix = calculate_affected_paths(modified, root)
+        except OSError:
+            return ""  # analyzer failure must never skip
+        if not matrix.packages:
+            return ""  # not a proven monorepo → conservative full verification
+        if matrix.root_owned_files:
+            return ""  # change outside the package graph → conservative
+        try:
+            cwd_rel = cwd_path.relative_to(root).as_posix()
+        except ValueError:
+            return ""  # cwd outside the workspace root → cannot scope
+        owner = find_owning_package(cwd_rel, matrix.packages)
+        if owner is None:
+            return ""  # cwd not inside any discovered package → conservative
+        if owner.name in matrix.affected_packages:
+            return ""
+        return (
+            f"Blast-radius scoping: workspace `{owner.name}` ({owner.path}) "
+            f"is unaffected by this diff — skipping unrelated toolchain verification"
+        )
+
     def run_sync(
         self,
         profile,
```
<!-- END_GIT_DIFF -->