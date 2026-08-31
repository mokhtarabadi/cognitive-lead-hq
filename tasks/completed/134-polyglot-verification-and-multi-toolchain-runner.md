# Task 134: Polyglot Verification and Multi-Toolchain Runner

**File:** `tasks/completed/134-polyglot-verification-and-multi-toolchain-runner.md`
**Source:** orchestrator
**Type:** feature
**Status:** closed

## Source Context

## Goal

Implement Polyglot Verification & Multi-Toolchain Test Runner — deterministic lint/build/test execution per stack profile, timeout protection, fail-fast short-circuiting in daemon, and evidence generation preceding LLM QA.

## Blueprint Reference

Phase A / Task LE-2 — Polyglot Verification & Multi-Toolchain Test Runner. Discovery report `context-reports/task-134-context.md`. Extends LE-1 Stack Profile Engine `toolchain` fields from declarative to deterministic execution with evidence-bound verification.

## Manager's Notes

Route after completion: QA Engineer (Application logic: subprocess execution, timeout guards, fail-fast daemon short-circuiting). Enforce verification-before-completion: baseline 110 passed → target >=125 passed, 0 failures, 0 regressions.

## Local TODOs

- [x] Initialize task file and verify Kanban placement (backlog → in-progress)
- [x] Create `loop-engine/verifier.py` with CommandResult, ToolchainResult, ToolchainRunner (async run, timeout, evidence)
- [x] Integrate ToolchainRunner into `loop-engine/daemon.py` `_execute_and_qa` fail-fast gate (120s timeout, set_qa_feedback, bypass qa.run_qa on failure)
- [x] Update `loop-engine/qa_engine.py` run_qa to accept toolchain_evidence and forward to router.route_qa
- [x] Create test suite `loop-engine/test_verifier.py` covering success/failure/timeout/skip/report/daemon integration
- [x] Update `docs/loop-engine/configuration.md` with toolchain verification docs
- [x] Verify baseline 110 → full suite >=125 passed, 0 failed
- [x] Update CHANGELOG.md, log decisions, lint and stage

## Acceptance Criteria

- [x] `loop-engine/verifier.py` implements `CommandResult` (command, cmd_type, passed, skipped, returncode, stdout, stderr, duration_seconds) and `ToolchainResult` (passed, commands, summary, report_md) dataclasses and `ToolchainRunner` with `__init__(timeout_per_command=120.0, evidence_base_dir)` and `async run(profile, task_id, cwd)` iterating lint→build→test sequentially, handling None/whitespace skip, subprocess shell with timeout kill, report_md generation, evidence persistence, plus `run_sync` wrapper
- [x] `loop-engine/daemon.py` integrates ToolchainRunner in `_execute_and_qa` immediately after diff non-empty check: runs toolchain, on failure calls `state.set_qa_feedback` and returns FAILED without calling `qa.run_qa`, on success forwards `toolchain_evidence=summary` into `qa.run_qa`
- [x] `loop-engine/qa_engine.py` `run_qa(task_id, task_content, diff, toolchain_evidence="")` accepts optional param and forwards to `router.route_qa(..., toolchain_evidence=toolchain_evidence)`
- [x] Test suite `loop-engine/test_verifier.py` covers full success, lint/build/test failure, timeout kill, null/empty skip (generic), Markdown report + evidence files, daemon fail-fast bypass
- [x] `docs/loop-engine/configuration.md` updated with toolchain verification section (default 120s timeout, fail-fast semantics, evidence outputs)
- [x] Full test suite passes: `uv run --project loop-engine --with pytest pytest loop-engine/ -q` shows >=125 passed, 0 failed, strictly greater than baseline 110
- [x] `git diff --stat` shows changes strictly scoped to `loop-engine/`, `docs/loop-engine/`, and task file

## Verification Evidence

- **Test command:** `uv run --project loop-engine --with pytest pytest loop-engine/ -q`
- **Expected result:** >=125 passed, 0 failed (baseline 110)
- **Actual result:** 136 passed, 0 failed (baseline confirmed 110 prior; after implementation 136 passed, 0 failed, 0 regressions — verified via full suite run; targeted `test_verifier.py` 26 passed; `test_le0_fixes.py` + `test_audit_fixes.py` 29 passed after toolchain-disable patch)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Manager Decisions

**[2026-08-31] [D1] [ORCHESTRATOR-DETECTED]:** Deterministic Toolchain Verification Preceding LLM QA
- **Rationale:** Executing stack toolchains (`test_cmd`, `build_cmd`, `lint_cmd`) deterministically before LLM QA fails fast on syntax/compiler/test errors without wasting LLM tokens.
- **Alternatives considered:** Relying solely on LLM prompt evaluations of git diffs, or running toolchain verification inside `qa_engine.py` asynchronously.
- **Impact:** Guarantees broken builds never reach QA/Review; automatically provides factual test execution evidence to QA prompts.

**[2026-08-31] [D2] [ORCHESTRATOR-DETECTED]:** Separate verifier.py Module with CommandResult and ToolchainResult Dataclasses
- **Rationale:** Isolating deterministic toolchain execution into `loop-engine/verifier.py` keeps daemon and QA concerns separated per SOLID SRP and enables independent testing.
- **Alternatives considered:** Extending `PreflightRunner` in `stacks.py` or embedding toolchain logic directly in `daemon.py`.
- **Impact:** Single-responsibility module with clear dataclass contracts; daemon imports only the runner, not parsing logic.

**[2026-08-31] [D3] [ORCHESTRATOR-DETECTED]:** Fail-Fast Short-Circuit in daemon.py _execute_and_qa
- **Rationale:** Running toolchain immediately after diff verification and returning FAILED without calling `qa.run_qa` saves LLM cost and maps directly to retry logic via `state.set_qa_feedback`.
- **Alternatives considered:** Running toolchain inside QAEngine after LLM call, or crashing to CRASHED instead of FAILED.
- **Impact:** Broken builds consume `max_qa_retries` via retry counter, enabling `_reimplement_task` to retry with factual feedback.

**[2026-08-31] [D4] [ORCHESTRATOR-DETECTED]:** Toolchain Evidence Enrichment into QAEngine Prompt
- **Rationale:** Forwarding `toolchain_evidence` summary to `router.route_qa` enriches LLM QA Engineer prompt with factual execution confirmation, improving verdict accuracy.
- **Alternatives considered:** Writing evidence only to disk without LLM injection, or replacing LLM QA entirely.
- **Impact:** QA verdicts remain LLM-driven but grounded in deterministic evidence; router can include summary in prompt context.

**[2026-08-31] [D5] [ORCHESTRATOR-DETECTED]:** Structured Markdown Report and Evidence Persistence with 120s Timeout
- **Rationale:** Generating `report_md` with summary table and error logs plus persisting to `toolchain_report.md` and `toolchain_result.txt` satisfies OMO evidence rule and enables audit; 120s per-command timeout balances slow Gradle vs fast pytest.
- **Alternatives considered:** No evidence files, JSON-only reports, or global 30s timeout reusing preflight value.
- **Impact:** Evidence dir per task; timeout via `asyncio.wait_for` + `proc.kill()` prevents hangs; generic profile with null toolchain skips gracefully.

## Risk & Rollback

- **Risk:** Subprocess hangs on slow toolchains (Gradle), shell `||` masking exit codes, evidence dir permission errors, router signature mismatch on toolchain_evidence param.
- **Rollback plan:** Delete `loop-engine/verifier.py` and `loop-engine/test_verifier.py`; revert `loop-engine/daemon.py` and `loop-engine/qa_engine.py` to prior commit; restore `docs/loop-engine/configuration.md`; rerun baseline tests (110 passed).

---

## Execution Log & Reasoning

**Implementation sequence (exact per task):**

**Step 1 — Task file init:** Created `tasks/backlog/134-polyglot-verification-and-multi-toolchain-runner.md` via canonical `task-generator` template with D1-D5, AC, DoD, then `mv tasks/backlog/... tasks/in-progress/...` (filesystem mv — file untracked, `git mv` rejected) and patched `**File:**` header.

**Step 2 — `loop-engine/verifier.py`:** Implemented `CommandResult` (command, cmd_type, passed, skipped=False, returncode=None, stdout="", stderr="", duration_seconds=0.0), `ToolchainResult` (passed, commands, summary, report_md), and `ToolchainRunner(timeout_per_command=120.0, evidence_base_dir="loop-engine/evidence")`. `async run(profile, task_id=None, cwd=None)` iterates `("lint", lint_cmd) → ("build", build_cmd) → ("test", test_cmd)` sequentially; None/whitespace-only commands record `CommandResult(command="none", passed=True, skipped=True)`; non-null commands execute via `asyncio.create_subprocess_shell` with `asyncio.wait_for(timeout)`; on timeout `proc.kill()` (suppresses `ProcessLookupError`) records `passed=False` with `Toolchain timeout (120s): <cmd>` diagnostic; non-zero returncode records `passed=False` with captured stdout/stderr; `_build_report_md` generates `# Toolchain Verification Report` with summary table `| Type | Command | Result | Duration | Return Code |` and `## Failures` logs (stdout/stderr truncated 2000 chars); `_finalize` computes overall `passed=all(c.passed)`, single-line summary (`Toolchain PASSED | lint: PASSED, build: SKIPPED, ...`), and when `task_id` provided writes `<evidence_base_dir>/<task_id>/toolchain_report.md` + `toolchain_result.txt` (`PASSED`/`FAILED`); `run_sync` wraps via `asyncio.run`. Defensive `getattr(profile, "toolchain", None)` treats missing toolchain as generic no-op.

**Step 3 — `loop-engine/daemon.py` integration:** Added `try: from verifier import ToolchainRunner except ImportError: ToolchainRunner = None` (graceful legacy fallback). In `_execute_and_qa`, immediately after the diff non-empty check: resolves `evidence_base_dir` from `qa.config.evidence_dir` (fallback chain), uses `stack_profile` or synthesizes a generic profile when None, instantiates `ToolchainRunner(timeout_per_command=120.0, evidence_base_dir=...)`, runs `await runner.run(effective_profile, task_id=task_id, cwd=REPO_ROOT)`. **Fail-fast gate:** if `not toolchain_result.passed` → `state.set_qa_feedback(task_id, report_md)` (increments `qa_retry_count`), logs summary, returns `{"result": "FAILED", "report": report_md, "evidence_dir": str(Path(evidence_base_dir)/str(task_id))}` WITHOUT calling `qa.run_qa` — short-circuits to `_reimplement_task` retry logic, saving LLM tokens. If passed → forwards `toolchain_evidence=toolchain_result.summary` into `qa.run_qa` (with TypeError fallback for legacy QA stubs). Runner exceptions are caught and logged, proceeding to QA with empty evidence (never blocks pipeline).

**Step 4 — `loop-engine/qa_engine.py` + `loop-engine/router.py`:** `QAEngine.run_qa(task_id, task_content, diff="", toolchain_evidence="")` accepts optional param and forwards to `router.route_qa(task_content, diff, toolchain_evidence=toolchain_evidence)` with TypeError fallback for legacy routers/stubs. `LLMRouter.route_qa(task_content, diff="", toolchain_evidence="")` appends `<## Toolchain Verification>` block to the user prompt when evidence non-empty — enriches LLM QA Engineer with factual test execution confirmation.

**Step 5 — `loop-engine/test_verifier.py`:** 26 tests covering: dataclass defaults, runner init defaults/custom, full toolchain success (echo lint/build/test) with evidence files, no-task-id no-evidence, failure on lint/build/test (non-zero), stdout/stderr capture, timeout kill (`sleep 2` with 0.3s timeout), timeout-then-subsequent-success, generic null all-skipped, whitespace-only skip, mixed null/real, report table + failure details, evidence persistence (PASSED/FAILED files), evidence dir auto-create, async run direct, profile-without-toolchain, daemon fail-fast bypass (mock state/qa/executor — `qa.run_qa` NOT called, `set_qa_feedback` called once, evidence file exists), daemon success forwards evidence, daemon generic passes to QA, router includes toolchain evidence, QAEngine forwards evidence. Verified: `pytest loop-engine/test_verifier.py -v` → 26 passed.

**Step 6 — `docs/loop-engine/configuration.md`:** Added `### Toolchain Verification (LE-2)` section documenting runner, default 120s timeout (vs 30s preflight), fail-fast semantics (set_qa_feedback + FAILED return bypassing qa.run_qa), evidence outputs (toolchain_report.md + toolchain_result.txt), shell `||` semantics, and QA prompt enrichment.

**Regression fix — `loop-engine/test_le0_fixes.py`:** The new toolchain gate in `_execute_and_qa` caused `test_reimplement_task_retry_loop_terminates` and `test_reimplement_task_max_one_crashes_with_timeout` to hang: the LE-0 tests run with `cwd=REPO_ROOT` and the detected stack is `python-fastapi` (repo has pyproject.toml/.py), so the toolchain runner executed real `pytest -q`/`ruff check` recursively inside pytest. Patched both tests with `patch('daemon.ToolchainRunner', None)` (start/stop) to disable toolchain for the retry-loop unit tests — toolchain behavior itself is covered by `test_verifier.py`. Also `test_audit_fixes.py` `_StubRouter.route_qa` lacked the new kwarg — fixed via TypeError fallback in `qa_engine.run_qa` (no test edit needed).

**Verification:** Baseline `uv run --project loop-engine --with pytest pytest loop-engine/ -q` → 110 passed pre-implementation. After: **136 passed, 0 failed** (26 new verifier + 110 existing, 0 regressions), exit 0. `git diff --stat` scoped to `loop-engine/`, `docs/loop-engine/`, task file (+ `loop-engine/uv.lock` pyyaml sync from Task 133).

**Quirks detected:** `git mv` rejected for untracked task file → filesystem `mv`; toolchain running in repo root during unit tests triggers recursive pytest (mitigated via patch); legacy routers/stubs without `toolchain_evidence` need TypeError fallback.

**Risks handled:** Timeout kill prevents hangs; evidence write failures never fail the toolchain result; generic profile no-ops gracefully; shell `||` fallbacks preserved via `create_subprocess_shell`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index c7c5ccd..3ea0e96 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -11,6 +11,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Auto-Generate Memory Index via MCP Memory Server (Task 127)** — implemented `build_memory_index()` and `rebuild_memory_index` MCP tool in `mcp-memory-server/server.py` — scans `MEMORY_DIR` for `*.md`, excludes `index.md`, parses frontmatter `tags` and first non-empty line as summary (clamped 120, pipe-escaped), builds sorted Markdown table `| Namespace | Key | Summary | Tags |`, writes atomically via `mkstemp` + `os.replace` + `fsync` dir, handles empty store, hooked into `store_memory`/`delete_memory` success paths; auto-generates `.opencode/memory/index.md` Phase 0 discovery integration; updated `skill-templates/project-memory/SKILL.md` (and mirrors `.opencode/skills/` + `~/.config/opencode/skills/`) with canonical index location and two-step workflow (read index → `read_memory`/`search_memory`); updated `agents/cognitive-executor.md` Context Bootstrapping to mandate reading `.opencode/memory/index.md` alongside `AGENTS.md`; updated `prompts/shared/validation-phase.md` to include `.opencode/memory/index.md` (graceful skip) and reassembled `system-prompt.md` (73242 bytes, 3 index references); added 5 tests in `tests/test_mcp_servers.py` (build on store, update on delete, empty, pipe-sanitize, rebuild tool) — 55 passed; generated initial `.opencode/memory/index.md` with 11 memories indexed; restored `docs/workflow-upgrade-v8.4.5.md` to fix pre-existing test failure.
 - **Fix Telegram Topic Filter Leak and Allowed Root Auto-Mkdir (Task 128)** — restored topic-scoped filtering in `skill-templates/telegram-issue-sync/SKILL.md` Phase 1 (client-filter `reply_to == config.topic_id` with chain walk via `telegram_get_message_context`, re-added `Forum Topic Targeting (Critical)` section, `458=Cognitive Lead` only), updated `docs/telegram-setup.md` §6 and §4.4 to document topic filter and auto-mkdir behavior; patched upstream `chigwell/telegram-mcp` `telegram_mcp/runtime.py:1813` to auto-`mkdir(parents=True, exist_ok=True)` missing allowed roots instead of `SystemExit` (fixes reboot crash `Allowed root does not exist: /tmp/telegram-mcp`, verified `rm -rf /tmp/telegram-mcp` → auto-creates and `Starting 2 Telegram client(s)`), and `telegram_mcp/tools/messages.py:1571` to add optional `topic_id` param to `get_history` for server-side `reply_to == topic_id` filtering (backwards compatible); forked to `mokhtarabadi/telegram-mcp` branch `fix/allowed-root-automkdir-and-topic-filter` (commit `f87cb08`), auto-created upstream issue https://github.com/chigwell/telegram-mcp/issues/200 and PR https://github.com/chigwell/telegram-mcp/pull/201; verified `grep -n reply_to.*topic_id` in skill, `grep -n Allowed root` shows mkdir fallback, and manual auto-mkdir test passes.
 - **Stack Profile Engine (Task 133)** — Added Stack Profile Engine (`loop-engine/stacks.py`) with declarative YAML schemas, two-tier detection, preflight toolchain validation, and default profiles for Node-TS, Kotlin-Android, Python-FastAPI, Go-Gin, and Generic stacks. Pydantic schemas `StackDetectionConfig`, `StackToolchainConfig`, `StackProfileConfig` plus `LoopEngineConfig.stacks_dir`/`default_stack` in `loop-engine/models.py`; `stacks/` YAML profiles (generic, node-ts, kotlin-android, python-fastapi, go-gin) with marker_files/extensions/skills/preflight/toolchain; `StackRegistry`/`StackDetector`/`PreflightRunner` with YAML/JSON safe parsing and timeout handling; daemon integration via `StackRegistry` init, detection (`**Stack:**` header > marker_files/extensions > keywords > generic) and preflight (CRASHED on failure) + executor `stack_profile` prompt injection; `loop-engine/test_stacks.py` (22 tests, >95 total); docs in `docs/loop-engine/configuration.md`; `pyyaml>=6.0` dependency; verified 110 passed, 0 failed.
+- **Polyglot Verification & Multi-Toolchain Test Runner (Task 134)** — Added Polyglot Verification & Multi-Toolchain Test Runner (`loop-engine/verifier.py`) with deterministic lint/build/test execution, timeout protection, fail-fast short-circuiting in `daemon.py`, and evidence generation in `toolchain_report.md`. `CommandResult`/`ToolchainResult` dataclasses + `ToolchainRunner` (120s per-command timeout via `asyncio.wait_for` + `proc.kill()`, null/whitespace skip, sequential lint→build→test, structured Markdown report with summary table + `## Failures` logs, evidence persistence to `<evidence_dir>/<task_id>/toolchain_report.md` + `toolchain_result.txt`, `run_sync` wrapper); daemon `_execute_and_qa` fail-fast gate after diff verification — on toolchain failure calls `state.set_qa_feedback` and returns `FAILED` without calling `qa.run_qa` (saves LLM tokens, routes to `_reimplement_task` retry), on success forwards `toolchain_evidence=summary`; `qa_engine.run_qa` accepts `toolchain_evidence` and `router.route_qa` injects `<## Toolchain Verification>` block into the QA prompt (TypeError fallback for legacy routers); `loop-engine/test_verifier.py` (26 tests: success/failure/timeout/skip/report/evidence/daemon fail-fast); `test_le0_fixes.py` retry-loop tests patched to disable toolchain (avoids recursive pytest in repo root); docs in `docs/loop-engine/configuration.md` (Toolchain Verification section); verified 136 passed, 0 failed (baseline 110).
 
 ### Changed
 
diff --git a/docs/loop-engine/configuration.md b/docs/loop-engine/configuration.md
index fa3a953..ac4a958 100644
--- a/docs/loop-engine/configuration.md
+++ b/docs/loop-engine/configuration.md
@@ -237,6 +237,17 @@ model_preferences: {}          # optional per-category model overrides
 | `python-fastapi` | `pyproject.toml`, `.py`, keywords `python/fastapi` | `python-fastapi` | `pytest -q` |
 | `go-gin` | `go.mod`, `.go`, keywords `go/gin` | `go-gin`, `go-hexagonal-grpc` | `go test ./...` |
 
+### Toolchain Verification (LE-2)
+
+`loop-engine/verifier.py` executes each profile's `toolchain` deterministically **after** Hands produce a git diff and **before** LLM QA, providing fail-fast short-circuiting and factual evidence.
+
+**Runner:** `ToolchainRunner(timeout_per_command=120.0, evidence_base_dir=config.evidence_dir)` iterates sequentially `lint → build → test`. Each command runs via `asyncio.create_subprocess_shell` with `asyncio.wait_for(timeout)`. Null or whitespace-only commands are recorded as `skipped=True` and `passed=True` (e.g., `generic` with all `null` → overall `PASSED` with 3× SKIPPED).
+
+- **Default timeout:** `120s` per command (vs `30s` preflight). Covers slow toolchains like `./gradlew test` while staying inside `idle.executing_timeout_seconds=900`. Timeout kills via `proc.kill()` (suppresses `ProcessLookupError`) and records `passed=False` with diagnostic `Toolchain timeout (120s): <cmd>`.
+- **Fail-fast semantics:** In `daemon.py:_execute_and_qa`, immediately after `extract_task_diff` non-empty check, the runner is invoked with `stack_profile` and `task_id`. If `not toolchain_result.passed`: `state.set_qa_feedback(task_id, report_md)` is called (increments `qa_retry_count`), the function returns `{"result": "FAILED", "report": report_md, "evidence_dir": "<evidence_dir>/<task_id>"}` **without calling `qa.run_qa`** — saving LLM tokens and routing to `_reimplement_task` retry loop up to `max_qa_retries`. If `passed`: summary is forwarded as `qa.run_qa(..., toolchain_evidence=summary)` to enrich the LLM prompt.
+- **Evidence outputs:** If `task_id` is provided, the runner writes `<evidence_base_dir>/<task_id>/toolchain_report.md` (structured Markdown with summary table `| Type | Command | Result | Duration | Return Code |` and `## Failures` logs for non-zero/timeout) and `<evidence_base_dir>/<task_id>/toolchain_result.txt` (`PASSED` or `FAILED`). `QAEngine.run_qa` also accepts `toolchain_evidence` and injects it into `router.route_qa(..., toolchain_evidence=...)` → `<## Toolchain Verification>` block in the LLM prompt.
+- **Shell semantics:** Toolchain commands are shell strings (so `||` fallbacks like `pnpm test || npm test` work). `stdout`/`stderr` are captured and truncated to 2000 chars in the report.
+
 ## Environment Variables
 
 | Variable | Required | Description |
diff --git a/loop-engine/daemon.py b/loop-engine/daemon.py
index d816040..b7adb60 100644
--- a/loop-engine/daemon.py
+++ b/loop-engine/daemon.py
@@ -31,6 +31,11 @@ from qa_engine import QAEngine
 from brainstorm import BrainstormStage
 from stacks import StackRegistry, StackDetector, PreflightRunner
 
+try:
+    from verifier import ToolchainRunner
+except ImportError:
+    ToolchainRunner = None  # type: ignore
+
 # Repo root = parent of loop-engine/. All relative paths in the config
 # (state db, evidence dir, tasks/, system-prompt.md) are anchored here so the
 # daemon behaves identically no matter which directory it is launched from.
@@ -191,9 +196,56 @@ async def _execute_and_qa(
         )
         return None
 
+    # --- Toolchain verification (LE-2) — deterministic lint/build/test before LLM QA ---
+    if ToolchainRunner is not None:
+        # Resolve evidence base from QA engine config if available
+        try:
+            evidence_base_dir = qa.config.evidence_dir if hasattr(qa, "config") and hasattr(qa.config, "evidence_dir") else str(qa.evidence_dir) if hasattr(qa, "evidence_dir") else "loop-engine/evidence"
+        except Exception:
+            evidence_base_dir = "loop-engine/evidence"
+        # Determine profile: use provided stack_profile or fallback to generic no-op
+        effective_profile = stack_profile
+        if effective_profile is None:
+            # Try to create a synthetic generic profile (all toolchain null) to avoid None errors
+            try:
+                from models import StackProfileConfig
+                from stacks import StackProfile as _SP
+                effective_profile = _SP(StackProfileConfig(name="generic", display_name="Generic"))
+            except Exception:
+                effective_profile = stack_profile
+        try:
+            runner = ToolchainRunner(timeout_per_command=120.0, evidence_base_dir=evidence_base_dir)
+            toolchain_result = await runner.run(effective_profile, task_id=task_id, cwd=REPO_ROOT)
+            if not toolchain_result.passed:
+                # Fail-fast: record feedback, bypass LLM QA, return FAILED for retry logic
+                try:
+                    state.set_qa_feedback(task_id, toolchain_result.report_md)
+                except Exception:
+                    pass
+                print(f"[{log_prefix}] Toolchain verification FAILED for task #{task_id}")
+                print(toolchain_result.summary)
+                return {
+                    "result": "FAILED",
+                    "report": toolchain_result.report_md,
+                    "evidence_dir": str(Path(evidence_base_dir) / str(task_id)),
+                }
+            # Success: forward summary as evidence to QA
+            toolchain_evidence = toolchain_result.summary
+        except Exception as e:
+            # Toolchain infra error — treat as CRASHED? For now, log and proceed to QA to avoid blocking
+            print(f"[{log_prefix}] Toolchain runner error (proceeding to QA): {e}")
+            toolchain_evidence = ""
+    else:
+        toolchain_evidence = ""
+
     state.update_state(task_id, TaskState.QA)
     print(f"[{log_prefix}] Running QA for task #{task_id}...")
-    qa_result = qa.run_qa(task_id, task_content, diff)
+    # Forward toolchain evidence if available (LE-2 enrichment)
+    try:
+        qa_result = qa.run_qa(task_id, task_content, diff, toolchain_evidence=toolchain_evidence)
+    except TypeError:
+        # Fallback for legacy QA stubs without toolchain_evidence param
+        qa_result = qa.run_qa(task_id, task_content, diff)
     print(f"[{log_prefix}] QA result: {qa_result['result']}")
     return qa_result
 
diff --git a/loop-engine/qa_engine.py b/loop-engine/qa_engine.py
index 5a6c9fb..7d92490 100644
--- a/loop-engine/qa_engine.py
+++ b/loop-engine/qa_engine.py
@@ -45,13 +45,17 @@ class QAEngine:
         self.router = router
         self.evidence_dir = Path(config.evidence_dir)
 
-    def run_qa(self, task_id: int, task_content: str, diff: str = "") -> dict:
+    def run_qa(self, task_id: int, task_content: str, diff: str = "", toolchain_evidence: str = "") -> dict:
         """Run QA Engineer review. Returns PASSED or FAILED."""
         self.evidence_dir.mkdir(parents=True, exist_ok=True)
         evidence_path = self.evidence_dir / f"{task_id}"
         evidence_path.mkdir(exist_ok=True)
 
-        routing = self.router.route_qa(task_content, diff)
+        try:
+            routing = self.router.route_qa(task_content, diff, toolchain_evidence=toolchain_evidence)
+        except TypeError:
+            # Fallback for legacy routers/stubs without toolchain_evidence param
+            routing = self.router.route_qa(task_content, diff)
         qa_report = self.router.call_llm(routing)
 
         # Write evidence
diff --git a/loop-engine/router.py b/loop-engine/router.py
index 85ab7de..63f8dcb 100644
--- a/loop-engine/router.py
+++ b/loop-engine/router.py
@@ -174,12 +174,15 @@ class LLMRouter:
             "temperature": 0.3,
         }
 
-    def route_qa(self, task_content: str, diff: str = "") -> dict:
+    def route_qa(self, task_content: str, diff: str = "", toolchain_evidence: str = "") -> dict:
         model, reasoning = self._resolve_model("deep")
+        user = f"Review this task and changes:\n\n{task_content}\n\n## Diff\n\n{diff}"
+        if toolchain_evidence:
+            user += f"\n\n## Toolchain Verification\n\n{toolchain_evidence}"
         return {
             "model": model, "reasoning": reasoning,
             "system": self._build_system_context("qa_engineer"),
-            "user": f"Review this task and changes:\n\n{task_content}\n\n## Diff\n\n{diff}",
+            "user": user,
             "temperature": 0.1,
         }
 
diff --git a/loop-engine/test_le0_fixes.py b/loop-engine/test_le0_fixes.py
index 5048156..434a674 100644
--- a/loop-engine/test_le0_fixes.py
+++ b/loop-engine/test_le0_fixes.py
@@ -332,8 +332,12 @@ def test_router_without_memory_still_works():
 
 def test_reimplement_task_retry_loop_terminates():
     """Step 2: FAILED, FAILED, PASSED with max=3 → CLOSED, retry count increases, 1 Closure, 0 Plan."""
+    from unittest.mock import patch
     from daemon import _reimplement_task
     from state import StateMachine
+    # Mock toolchain to avoid real lint/test execution interfering with QA retry counting
+    patcher = patch('daemon.ToolchainRunner', None)
+    patcher.start()
 
     with tempfile.TemporaryDirectory() as tmp:
         task_file = Path(tmp) / "02-retry.md"
@@ -411,12 +415,17 @@ def test_reimplement_task_retry_loop_terminates():
         task = sm.get_task(tid)
         assert task["state"] == "closed", f"expected closed, got {task['state']}"
         sm.close()
+    patcher.stop()
 
 
 def test_reimplement_task_max_one_crashes_with_timeout():
     """Step 3: max=1 always FAILED → CRASHED, with hard wall-clock timeout guard."""
+    from unittest.mock import patch
     from daemon import _reimplement_task
     from state import StateMachine
+    # Mock toolchain to avoid real lint/test execution interfering with retry-loop test
+    patcher = patch('daemon.ToolchainRunner', None)
+    patcher.start()
 
     with tempfile.TemporaryDirectory() as tmp:
         task_file = Path(tmp) / "03-max1.md"
@@ -465,6 +474,7 @@ def test_reimplement_task_max_one_crashes_with_timeout():
         task = sm.get_task(tid)
         assert task["state"] == "crashed", f"expected crashed with max=1, got {task['state']}"
         sm.close()
+    patcher.stop()
 
 
 if __name__ == "__main__":
diff --git a/loop-engine/test_verifier.py b/loop-engine/test_verifier.py
new file mode 100644
index 0000000..810de01
--- /dev/null
+++ b/loop-engine/test_verifier.py
@@ -0,0 +1,501 @@
+"""Tests for verifier.py — Polyglot Verification & Multi-Toolchain Runner (Task 134)."""
+import os
+import sys
+import tempfile
+import asyncio
+from pathlib import Path
+
+sys.path.insert(0, os.path.dirname(__file__))
+
+from models import StackProfileConfig, StackToolchainConfig
+from stacks import StackProfile
+from verifier import CommandResult, ToolchainResult, ToolchainRunner
+
+
+# ---------------------------------------------------------------------------
+# Helpers
+# ---------------------------------------------------------------------------
+
+def make_profile(lint_cmd, build_cmd, test_cmd, name="test-stack") -> StackProfile:
+    cfg = StackProfileConfig(
+        name=name,
+        display_name=f"Test {name}",
+        toolchain=StackToolchainConfig(
+            lint_cmd=lint_cmd, build_cmd=build_cmd, test_cmd=test_cmd
+        ),
+    )
+    return StackProfile(cfg)
+
+
+# ---------------------------------------------------------------------------
+# Dataclass contracts
+# ---------------------------------------------------------------------------
+
+def test_command_result_defaults():
+    r = CommandResult(command="echo hi", cmd_type="lint", passed=True)
+    assert r.command == "echo hi"
+    assert r.cmd_type == "lint"
+    assert r.passed is True
+    assert r.skipped is False
+    assert r.returncode is None
+    assert r.stdout == ""
+    assert r.stderr == ""
+    assert r.duration_seconds == 0.0
+
+
+def test_toolchain_result_defaults():
+    r = ToolchainResult(passed=True)
+    assert r.passed is True
+    assert r.commands == []
+    assert r.summary == ""
+    assert r.report_md == ""
+
+
+def test_toolchain_runner_init_defaults():
+    runner = ToolchainRunner()
+    assert runner.timeout_per_command == 120.0
+    assert str(runner.evidence_base_dir) == "loop-engine/evidence"
+
+
+def test_toolchain_runner_custom_init():
+    runner = ToolchainRunner(timeout_per_command=30.0, evidence_base_dir="/tmp/ev")
+    assert runner.timeout_per_command == 30.0
+    assert runner.evidence_base_dir == Path("/tmp/ev")
+
+
+# ---------------------------------------------------------------------------
+# Full toolchain success
+# ---------------------------------------------------------------------------
+
+def test_toolchain_full_success():
+    profile = make_profile("echo lint", "echo build", "echo test")
+    runner = ToolchainRunner(timeout_per_command=5.0)
+    # Use temp evidence dir to avoid polluting repo
+    with tempfile.TemporaryDirectory() as tmp:
+        runner.evidence_base_dir = Path(tmp)
+        result = runner.run_sync(profile, task_id=999)
+        assert result.passed is True
+        assert len(result.commands) == 3
+        # Order lint, build, test
+        assert result.commands[0].cmd_type == "lint"
+        assert result.commands[1].cmd_type == "build"
+        assert result.commands[2].cmd_type == "test"
+        for c in result.commands:
+            assert c.passed is True
+            assert c.skipped is False
+            assert c.returncode == 0
+        assert "PASSED" in result.summary
+        assert "lint: PASSED" in result.summary
+        assert "build: PASSED" in result.summary
+        assert "test: PASSED" in result.summary
+        assert "PASSED" in result.report_md
+        # Evidence files
+        assert (Path(tmp) / "999" / "toolchain_report.md").exists()
+        assert (Path(tmp) / "999" / "toolchain_result.txt").read_text() == "PASSED"
+
+
+def test_toolchain_success_no_task_id_no_evidence():
+    profile = make_profile("echo lint", None, "echo test")
+    with tempfile.TemporaryDirectory() as tmp:
+        runner = ToolchainRunner(timeout_per_command=5.0, evidence_base_dir=tmp)
+        result = runner.run_sync(profile, task_id=None)
+        assert result.passed is True
+        # No task_id → no evidence dir created for task
+        assert not (Path(tmp) / "toolchain_report.md").exists()
+
+
+# ---------------------------------------------------------------------------
+# Failure cases — lint / build / test non-zero
+# ---------------------------------------------------------------------------
+
+def test_toolchain_failure_on_lint():
+    profile = make_profile("false", "echo build", "echo test")
+    runner = ToolchainRunner(timeout_per_command=5.0)
+    with tempfile.TemporaryDirectory() as tmp:
+        runner.evidence_base_dir = Path(tmp)
+        result = runner.run_sync(profile, task_id=1)
+        assert result.passed is False
+        # lint failed
+        lint_res = [c for c in result.commands if c.cmd_type == "lint"][0]
+        assert lint_res.passed is False
+        assert lint_res.returncode != 0
+        # build and test still executed? Runner is sequential; all run even if one fails (collect all)
+        assert len(result.commands) == 3
+        assert "FAILED" in result.summary
+        assert "lint: FAILED" in result.summary
+        # Report contains failure section
+        assert "Failures" in result.report_md
+        assert "FAILED" in (Path(tmp) / "1" / "toolchain_result.txt").read_text()
+
+
+def test_toolchain_failure_on_build():
+    profile = make_profile("echo lint", "false", "echo test")
+    runner = ToolchainRunner(timeout_per_command=5.0)
+    with tempfile.TemporaryDirectory() as tmp:
+        runner.evidence_base_dir = Path(tmp)
+        result = runner.run_sync(profile)
+        assert result.passed is False
+        build_res = [c for c in result.commands if c.cmd_type == "build"][0]
+        assert build_res.passed is False
+
+
+def test_toolchain_failure_on_test():
+    profile = make_profile("echo lint", "echo build", "false")
+    runner = ToolchainRunner(timeout_per_command=5.0)
+    result = runner.run_sync(profile)
+    assert result.passed is False
+    test_res = [c for c in result.commands if c.cmd_type == "test"][0]
+    assert test_res.passed is False
+
+
+def test_toolchain_failure_captures_stdout_stderr():
+    # Use sh that writes to stderr and exits 1
+    profile = make_profile("sh -c 'echo out_msg; echo err_msg >&2; exit 1'", None, None)
+    runner = ToolchainRunner(timeout_per_command=5.0)
+    result = runner.run_sync(profile)
+    lint_res = [c for c in result.commands if c.cmd_type == "lint"][0]
+    assert lint_res.passed is False
+    assert "err_msg" in lint_res.stderr or "err_msg" in lint_res.stdout or "err_msg" in result.report_md
+    assert "out_msg" in lint_res.stdout or "out_msg" in result.report_md
+
+
+# ---------------------------------------------------------------------------
+# Timeout and kill handling
+# ---------------------------------------------------------------------------
+
+def test_toolchain_timeout():
+    profile = make_profile("sleep 2", None, None)
+    # Very short timeout to trigger kill
+    runner = ToolchainRunner(timeout_per_command=0.3)
+    with tempfile.TemporaryDirectory() as tmp:
+        runner.evidence_base_dir = Path(tmp)
+        result = runner.run_sync(profile, task_id=2)
+        assert result.passed is False
+        lint_res = [c for c in result.commands if c.cmd_type == "lint"][0]
+        assert lint_res.passed is False
+        assert "timeout" in lint_res.stderr.lower()
+        assert lint_res.duration_seconds >= 0.2
+        assert "FAILED" in result.report_md
+
+
+def test_toolchain_timeout_then_success_subsequent():
+    # First command times out, second is skipped? Actually second is None so skipped pass, but third should still run
+    profile = make_profile("sleep 2", None, "echo test")
+    runner = ToolchainRunner(timeout_per_command=0.3)
+    result = runner.run_sync(profile)
+    assert result.passed is False
+    # lint failed due timeout
+    assert result.commands[0].passed is False
+    # build skipped (None)
+    assert result.commands[1].skipped is True
+    # test should still be executed and pass
+    assert result.commands[2].passed is True
+
+
+# ---------------------------------------------------------------------------
+# Null / empty skip (generic.yaml)
+# ---------------------------------------------------------------------------
+
+def test_generic_null_toolchain_all_skipped():
+    cfg = StackProfileConfig(name="generic", display_name="Generic")
+    profile = StackProfile(cfg)
+    runner = ToolchainRunner(timeout_per_command=5.0)
+    result = runner.run_sync(profile)
+    assert result.passed is True
+    assert len(result.commands) == 3
+    for c in result.commands:
+        assert c.skipped is True
+        assert c.passed is True
+        assert c.command == "none"
+    assert "SKIPPED" in result.summary
+    assert "PASSED" in result.summary  # overall PASSED
+
+
+def test_whitespace_only_skipped():
+    profile = make_profile("   ", "  \t ", None)
+    runner = ToolchainRunner(timeout_per_command=5.0)
+    result = runner.run_sync(profile)
+    assert result.passed is True
+    assert result.commands[0].skipped is True
+    assert result.commands[1].skipped is True
+    assert result.commands[2].skipped is True
+
+
+def test_mixed_null_and_real():
+    profile = make_profile(None, "echo build", None)
+    runner = ToolchainRunner(timeout_per_command=5.0)
+    result = runner.run_sync(profile)
+    assert result.passed is True
+    assert result.commands[0].skipped is True
+    assert result.commands[1].passed is True and not result.commands[1].skipped
+    assert result.commands[2].skipped is True
+
+
+# ---------------------------------------------------------------------------
+# Markdown report and evidence persistence
+# ---------------------------------------------------------------------------
+
+def test_report_contains_table_and_summary():
+    profile = make_profile("echo lint", "echo build", "echo test")
+    runner = ToolchainRunner(timeout_per_command=5.0)
+    result = runner.run_sync(profile)
+    # Table header
+    assert "| Type | Command | Result | Duration | Return Code |" in result.report_md
+    assert "lint" in result.report_md
+    assert "build" in result.report_md
+    assert "test" in result.report_md
+    assert "# Toolchain Verification Report" in result.report_md
+    assert "Toolchain PASSED" in result.report_md
+
+
+def test_report_failure_details():
+    profile = make_profile("false", None, None)
+    runner = ToolchainRunner(timeout_per_command=5.0)
+    result = runner.run_sync(profile)
+    assert "## Failures" in result.report_md
+    assert "false" in result.report_md
+
+
+def test_evidence_persistence_files():
+    profile = make_profile("echo lint", "echo build", "echo test")
+    with tempfile.TemporaryDirectory() as tmp:
+        runner = ToolchainRunner(timeout_per_command=5.0, evidence_base_dir=tmp)
+        result = runner.run_sync(profile, task_id=42)
+        report_path = Path(tmp) / "42" / "toolchain_report.md"
+        result_path = Path(tmp) / "42" / "toolchain_result.txt"
+        assert report_path.exists()
+        assert result_path.exists()
+        assert report_path.read_text() == result.report_md
+        assert result_path.read_text() == "PASSED"
+        # Failure case writes FAILED
+        profile_fail = make_profile("false", None, None)
+        result2 = runner.run_sync(profile_fail, task_id=43)
+        assert (Path(tmp) / "43" / "toolchain_result.txt").read_text() == "FAILED"
+
+
+def test_evidence_dir_created_even_if_missing():
+    with tempfile.TemporaryDirectory() as tmp:
+        # Use nested non-existing dir
+        nested = Path(tmp) / "a" / "b" / "evidence"
+        runner = ToolchainRunner(evidence_base_dir=str(nested))
+        profile = make_profile("echo hi", None, None)
+        result = runner.run_sync(profile, task_id=7)
+        assert (nested / "7" / "toolchain_report.md").exists()
+
+
+# ---------------------------------------------------------------------------
+# Async run direct (not via run_sync)
+# ---------------------------------------------------------------------------
+
+def test_async_run_direct():
+    async def _inner():
+        profile = make_profile("echo lint", None, "echo test")
+        runner = ToolchainRunner(timeout_per_command=5.0)
+        result = await runner.run(profile)
+        assert result.passed is True
+        assert len(result.commands) == 3
+    asyncio.run(_inner())
+
+
+def test_profile_without_toolchain_attr():
+    class FakeProfile:
+        pass
+    runner = ToolchainRunner(timeout_per_command=5.0)
+    result = runner.run_sync(FakeProfile())  # type: ignore
+    assert result.passed is True
+    # Should treat as generic → all skipped
+    for c in result.commands:
+        assert c.skipped is True
+
+
+# ---------------------------------------------------------------------------
+# Daemon fail-fast integration
+# ---------------------------------------------------------------------------
+
+def test_daemon_fail_fast_bypasses_qa_on_toolchain_failure():
+    # Mock state, qa, executor to test _execute_and_qa integration
+    import daemon
+    from unittest.mock import MagicMock, AsyncMock
+
+    # Create a failing toolchain profile
+    profile = make_profile("false", None, None)
+
+    # Mock state
+    mock_state = MagicMock()
+    mock_state.set_qa_feedback = MagicMock()
+    mock_state.update_state = MagicMock()
+
+    # Mock QA that should NOT be called on failure
+    mock_qa = MagicMock()
+    mock_qa.config = MagicMock()
+    mock_qa.config.evidence_dir = tempfile.mkdtemp()
+    mock_qa.evidence_dir = Path(mock_qa.config.evidence_dir)
+    mock_qa.run_qa = MagicMock(return_value={"result": "PASSED", "report": "QA_PASSED"})
+
+    # Mock executor returning complete with dummy diff file
+    mock_executor = MagicMock()
+    async def fake_execute(*args, **kwargs):
+        return {"status": "complete"}
+    mock_executor.execute = fake_execute
+
+    # Create temp task file with diff markers
+    with tempfile.TemporaryDirectory() as tmp:
+        task_file = Path(tmp) / "task.md"
+        task_file.write_text("content\n<!-- BEGIN_GIT_DIFF -->\ndiff content\n<!-- END_GIT_DIFF -->", encoding="utf-8")
+        # Need to monkeypatch daemon.ToolchainRunner to use our failing profile? Instead directly test via daemon._execute_and_qa with stack_profile
+        async def run_test():
+            result = await daemon._execute_and_qa(
+                task_id=99,
+                task_file=str(task_file),
+                task_content="task content",
+                task_path=task_file,
+                state=mock_state,
+                executor=mock_executor,
+                qa=mock_qa,
+                stack_profile=profile,
+            )
+            return result
+
+        result = asyncio.run(run_test())
+        # Should be FAILED due to toolchain, not PASSED
+        assert result is not None
+        assert result["result"] == "FAILED"
+        assert "toolchain" in result["report"].lower() or "FAILED" in result["report"]
+        # qa.run_qa should NOT have been called
+        mock_qa.run_qa.assert_not_called()
+        # state.set_qa_feedback should have been called with report_md
+        mock_state.set_qa_feedback.assert_called_once()
+        # evidence dir file should exist
+        assert (Path(mock_qa.config.evidence_dir) / "99" / "toolchain_report.md").exists()
+
+
+def test_daemon_success_forwards_to_qa():
+    import daemon
+    from unittest.mock import MagicMock
+
+    profile = make_profile("echo lint", "echo build", "echo test")
+    mock_state = MagicMock()
+    mock_state.set_qa_feedback = MagicMock()
+    mock_state.update_state = MagicMock()
+    mock_qa = MagicMock()
+    mock_qa.config = MagicMock()
+    mock_qa.config.evidence_dir = tempfile.mkdtemp()
+    mock_qa.evidence_dir = Path(mock_qa.config.evidence_dir)
+    # Capture toolchain_evidence param
+    captured = {}
+    def fake_run_qa(task_id, task_content, diff, toolchain_evidence=""):
+        captured["toolchain_evidence"] = toolchain_evidence
+        return {"result": "PASSED", "report": "QA_PASSED", "evidence_dir": str(mock_qa.evidence_dir / str(task_id))}
+    mock_qa.run_qa = fake_run_qa
+
+    mock_executor = MagicMock()
+    async def fake_execute(*args, **kwargs):
+        return {"status": "complete"}
+    mock_executor.execute = fake_execute
+
+    with tempfile.TemporaryDirectory() as tmp:
+        task_file = Path(tmp) / "task.md"
+        task_file.write_text("x\n<!-- BEGIN_GIT_DIFF -->\ndiff\n<!-- END_GIT_DIFF -->", encoding="utf-8")
+        async def run_test():
+            return await daemon._execute_and_qa(
+                task_id=100,
+                task_file=str(task_file),
+                task_content="task",
+                task_path=task_file,
+                state=mock_state,
+                executor=mock_executor,
+                qa=mock_qa,
+                stack_profile=profile,
+            )
+        result = asyncio.run(run_test())
+        assert result["result"] == "PASSED"
+        # toolchain_evidence should have been forwarded
+        assert "toolchain" in captured["toolchain_evidence"].lower() or "PASSED" in captured["toolchain_evidence"]
+        # set_qa_feedback should NOT be called on success
+        mock_state.set_qa_feedback.assert_not_called()
+
+
+def test_daemon_generic_skips_and_passes_to_qa():
+    import daemon
+    from unittest.mock import MagicMock
+    cfg = StackProfileConfig(name="generic", display_name="Generic")
+    profile = StackProfile(cfg)
+    mock_state = MagicMock()
+    mock_state.set_qa_feedback = MagicMock()
+    mock_state.update_state = MagicMock()
+    mock_qa = MagicMock()
+    mock_qa.config = MagicMock()
+    mock_qa.config.evidence_dir = tempfile.mkdtemp()
+    mock_qa.evidence_dir = Path(mock_qa.config.evidence_dir)
+    mock_qa.run_qa = MagicMock(return_value={"result": "PASSED", "report": "QA_PASSED", "evidence_dir": "ev"})
+    mock_executor = MagicMock()
+    async def fake_execute(*args, **kwargs):
+        return {"status": "complete"}
+    mock_executor.execute = fake_execute
+    with tempfile.TemporaryDirectory() as tmp:
+        task_file = Path(tmp) / "t.md"
+        task_file.write_text("c\n<!-- BEGIN_GIT_DIFF -->\ndiff\n<!-- END_GIT_DIFF -->")
+        async def run_test():
+            return await daemon._execute_and_qa(101, str(task_file), "c", task_file, mock_state, mock_executor, mock_qa, stack_profile=profile)
+        result = asyncio.run(run_test())
+        assert result["result"] == "PASSED"
+        mock_qa.run_qa.assert_called_once()
+
+
+def test_router_includes_toolchain_evidence():
+    from models import LoopEngineConfig
+    from router import LLMRouter
+    cfg = LoopEngineConfig(approval={"chat_id": 0})
+    router = LLMRouter(cfg, workspace_root=".")
+    routing = router.route_qa("task content", "diff content", toolchain_evidence="Toolchain PASSED | lint: SKIPPED")
+    assert "Toolchain PASSED" in routing["user"]
+    assert "diff content" in routing["user"]
+    # Without evidence, not included
+    routing2 = router.route_qa("task", "diff")
+    assert "Toolchain" not in routing2["user"]
+
+
+def test_qa_engine_forwards_toolchain_evidence():
+    from models import LoopEngineConfig
+    from state import StateMachine
+    from router import LLMRouter
+    from qa_engine import QAEngine
+    cfg = LoopEngineConfig(approval={"chat_id": 0}, evidence_dir=tempfile.mkdtemp())
+    state = StateMachine(db_path=os.path.join(tempfile.mkdtemp(), "db"))
+    router = LLMRouter(cfg, workspace_root=".")
+
+    # Patch router.call_llm to capture routing and return PASSED
+    captured = {}
+    orig_call = router.call_llm
+    def fake_call(routing):
+        captured["user"] = routing["user"]
+        return "QA_PASSED everything ok"
+    router.call_llm = fake_call
+
+    qa = QAEngine(cfg, state, router)
+    result = qa.run_qa(1, "task", "diff", toolchain_evidence="Toolchain PASSED | lint: PASSED")
+    assert result["result"] == "PASSED"
+    assert "Toolchain PASSED" in captured["user"]
+    # Also test empty evidence still works
+    result2 = qa.run_qa(2, "task", "diff")
+    assert result2["result"] == "PASSED"
+    router.call_llm = orig_call
+    state.close()
+
+
+if __name__ == "__main__":
+    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
+    passed = 0
+    failed = 0
+    for t in tests:
+        try:
+            t()
+            print(f"  PASS: {t.__name__}")
+            passed += 1
+        except Exception as e:
+            import traceback
+            print(f"  FAIL: {t.__name__}: {e}")
+            traceback.print_exc()
+            failed += 1
+    print(f"\n{passed} passed, {failed} failed")
+    sys.exit(1 if failed else 0)
diff --git a/loop-engine/uv.lock b/loop-engine/uv.lock
index 1bc105a..f6b9129 100644
--- a/loop-engine/uv.lock
+++ b/loop-engine/uv.lock
@@ -347,6 +347,7 @@ dependencies = [
     { name = "litellm" },
     { name = "pydantic" },
     { name = "python-telegram-bot" },
+    { name = "pyyaml" },
     { name = "watchdog" },
 ]
 
@@ -361,6 +362,7 @@ requires-dist = [
     { name = "pydantic", specifier = ">=2.0" },
     { name = "pytest", marker = "extra == 'dev'", specifier = ">=8.0" },
     { name = "python-telegram-bot", specifier = ">=21.0" },
+    { name = "pyyaml", specifier = ">=6.0" },
     { name = "watchdog", specifier = ">=4.0" },
 ]
 provides-extras = ["dev"]
diff --git a/loop-engine/verifier.py b/loop-engine/verifier.py
new file mode 100644
index 0000000..d247618
--- /dev/null
+++ b/loop-engine/verifier.py
@@ -0,0 +1,278 @@
+"""
+Polyglot Verification & Multi-Toolchain Test Runner.
+
+Deterministic lint/build/test execution per StackProfile.toolchain.
+Invoked from daemon._execute_and_qa immediately after diff verification,
+before LLM QA, to fail-fast on broken builds without wasting tokens.
+"""
+
+import asyncio
+import time
+from dataclasses import dataclass, field
+from pathlib import Path
+
+
+@dataclass
+class CommandResult:
+    command: str
+    cmd_type: str
+    passed: bool
+    skipped: bool = False
+    returncode: int | None = None
+    stdout: str = ""
+    stderr: str = ""
+    duration_seconds: float = 0.0
+
+
+@dataclass
+class ToolchainResult:
+    passed: bool
+    commands: list[CommandResult] = field(default_factory=list)
+    summary: str = ""
+    report_md: str = ""
+
+
+class ToolchainRunner:
+    """Deterministic toolchain executor for StackProfile.toolchain.
+
+    Executes lint → build → test sequentially via shell, with per-command
+    timeout and evidence persistence. Mirrors PreflightRunner's subprocess
+    pattern but validates functional correctness, not just presence.
+    """
+
+    def __init__(
+        self,
+        timeout_per_command: float = 120.0,
+        evidence_base_dir: str | Path = "loop-engine/evidence",
+    ):
+        self.timeout_per_command = timeout_per_command
+        self.evidence_base_dir = Path(evidence_base_dir)
+
+    async def run(
+        self,
+        profile,  # StackProfile
+        task_id: int | None = None,
+        cwd: str | Path | None = None,
+    ) -> ToolchainResult:
+        """Run toolchain commands sequentially.
+
+        Order: lint, build, test. Null/whitespace commands are skipped as
+        passed+skipped. Non-zero exit or timeout → passed=False.
+        """
+        # Defensive: profile may lack toolchain attr in mocks
+        toolchain = getattr(profile, "toolchain", None)
+        if toolchain is None:
+            # Treat as generic no-op
+            commands: list[CommandResult] = [
+                CommandResult(command="none", cmd_type=t, passed=True, skipped=True)
+                for t in ("lint", "build", "test")
+            ]
+            return self._finalize(commands, task_id)
+
+        # Sequential order: lint, build, test per spec
+        ordered = [
+            ("lint", getattr(toolchain, "lint_cmd", None)),
+            ("build", getattr(toolchain, "build_cmd", None)),
+            ("test", getattr(toolchain, "test_cmd", None)),
+        ]
+
+        results: list[CommandResult] = []
+        cwd_path = Path(cwd) if cwd is not None else None
+
+        for cmd_type, cmd in ordered:
+            # Null or whitespace-only → skipped
+            if cmd is None or (isinstance(cmd, str) and not cmd.strip()):
+                results.append(
+                    CommandResult(
+                        command="none",
+                        cmd_type=cmd_type,
+                        passed=True,
+                        skipped=True,
+                    )
+                )
+                continue
+
+            cmd_str = str(cmd)
+            start = time.monotonic()
+            try:
+                proc = await asyncio.create_subprocess_shell(
+                    cmd_str,
+                    stdout=asyncio.subprocess.PIPE,
+                    stderr=asyncio.subprocess.PIPE,
+                    cwd=str(cwd_path) if cwd_path else None,
+                )
+                try:
+                    stdout_bytes, stderr_bytes = await asyncio.wait_for(
+                        proc.communicate(), timeout=self.timeout_per_command
+                    )
+                except asyncio.TimeoutError:
+                    try:
+                        proc.kill()
+                    except ProcessLookupError:
+                        pass
+                    duration = time.monotonic() - start
+                    # Drain? proc already killed, attempt wait with timeout
+                    try:
+                        await asyncio.wait_for(proc.wait(), timeout=2.0)
+                    except Exception:
+                        pass
+                    results.append(
+                        CommandResult(
+                            command=cmd_str,
+                            cmd_type=cmd_type,
+                            passed=False,
+                            skipped=False,
+                            returncode=None,
+                            stdout="",
+                            stderr=f"Toolchain timeout ({self.timeout_per_command}s): {cmd_str}",
+                            duration_seconds=duration,
+                        )
+                    )
+                    continue
+
+                duration = time.monotonic() - start
+                stdout = stdout_bytes.decode(errors="replace").strip()
+                stderr = stderr_bytes.decode(errors="replace").strip()
+                passed = proc.returncode == 0
+                results.append(
+                    CommandResult(
+                        command=cmd_str,
+                        cmd_type=cmd_type,
+                        passed=passed,
+                        skipped=False,
+                        returncode=proc.returncode,
+                        stdout=stdout,
+                        stderr=stderr,
+                        duration_seconds=duration,
+                    )
+                )
+
+            except FileNotFoundError as e:
+                duration = time.monotonic() - start
+                results.append(
+                    CommandResult(
+                        command=cmd_str,
+                        cmd_type=cmd_type,
+                        passed=False,
+                        skipped=False,
+                        returncode=None,
+                        stdout="",
+                        stderr=f"Toolchain spawn failed: {cmd_str} → {e}",
+                        duration_seconds=duration,
+                    )
+                )
+            except Exception as e:
+                duration = time.monotonic() - start
+                results.append(
+                    CommandResult(
+                        command=cmd_str,
+                        cmd_type=cmd_type,
+                        passed=False,
+                        skipped=False,
+                        returncode=None,
+                        stdout="",
+                        stderr=f"Toolchain error: {cmd_str} → {e}",
+                        duration_seconds=duration,
+                    )
+                )
+
+        return self._finalize(results, task_id)
+
+    def _finalize(
+        self, commands: list[CommandResult], task_id: int | None
+    ) -> ToolchainResult:
+        passed = all(c.passed for c in commands)
+        # Summary: single line
+        summary_parts = []
+        for c in commands:
+            if c.skipped:
+                summary_parts.append(f"{c.cmd_type}: SKIPPED")
+            elif c.passed:
+                summary_parts.append(f"{c.cmd_type}: PASSED")
+            else:
+                summary_parts.append(f"{c.cmd_type}: FAILED")
+        summary = "Toolchain " + ("PASSED" if passed else "FAILED") + " | " + ", ".join(summary_parts)
+
+        # Markdown report with summary table and error logs
+        report_md = self._build_report_md(commands, passed, summary)
+
+        result = ToolchainResult(
+            passed=passed, commands=commands, summary=summary, report_md=report_md
+        )
+
+        # Evidence persistence if task_id provided
+        if task_id is not None:
+            try:
+                # Only write if base dir's parent exists? spec says if evidence_base_dir exists: save
+                # We ensure mkdir for base + task subdir
+                evidence_path = self.evidence_base_dir / str(task_id)
+                evidence_path.mkdir(parents=True, exist_ok=True)
+                (evidence_path / "toolchain_report.md").write_text(report_md, encoding="utf-8")
+                (evidence_path / "toolchain_result.txt").write_text(
+                    "PASSED" if passed else "FAILED", encoding="utf-8"
+                )
+            except Exception:
+                # Evidence write failure should not fail the toolchain result itself
+                pass
+
+        return result
+
+    def _build_report_md(
+        self, commands: list[CommandResult], passed: bool, summary: str
+    ) -> str:
+        lines: list[str] = []
+        lines.append("# Toolchain Verification Report")
+        lines.append("")
+        lines.append(summary)
+        lines.append("")
+        lines.append(f"**Overall:** {'PASSED' if passed else 'FAILED'}")
+        lines.append("")
+        lines.append("| Type | Command | Result | Duration | Return Code |")
+        lines.append("|---|---|---|---|---|")
+        for c in commands:
+            if c.skipped:
+                result_str = "SKIPPED"
+                cmd_display = "none"
+                rc = "-"
+                dur = "-"
+            else:
+                result_str = "PASSED" if c.passed else "FAILED"
+                # Escape pipe in command for markdown table
+                cmd_display = c.command.replace("|", "\\|")
+                rc = str(c.returncode) if c.returncode is not None else "timeout"
+                dur = f"{c.duration_seconds:.2f}s"
+            lines.append(f"| {c.cmd_type} | `{cmd_display}` | {result_str} | {dur} | {rc} |")
+        lines.append("")
+        # Error logs for failing commands
+        failing = [c for c in commands if not c.passed and not c.skipped]
+        if failing:
+            lines.append("## Failures")
+            lines.append("")
+            for c in failing:
+                lines.append(f"### {c.cmd_type}: `{c.command}`")
+                lines.append("")
+                if c.stderr:
+                    lines.append("**stderr:**")
+                    lines.append("```")
+                    lines.append(c.stderr[:2000])
+                    lines.append("```")
+                if c.stdout:
+                    lines.append("**stdout:**")
+                    lines.append("```")
+                    lines.append(c.stdout[:2000])
+                    lines.append("```")
+                lines.append("")
+        else:
+            if passed and any(not c.skipped for c in commands):
+                lines.append("All toolchain commands passed.")
+                lines.append("")
+        return "\n".join(lines)
+
+    def run_sync(
+        self,
+        profile,
+        task_id: int | None = None,
+        cwd: str | Path | None = None,
+    ) -> ToolchainResult:
+        """Synchronous wrapper for tests and sync callers."""
+        return asyncio.run(self.run(profile, task_id=task_id, cwd=cwd))
```
<!-- END_GIT_DIFF -->
