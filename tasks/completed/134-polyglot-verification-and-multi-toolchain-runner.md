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
**Factual Git Diff:** Stored in Commit Hash: `b4d89f4f49e93ecfd202f080b2cbd10613459285`
<!-- END_GIT_DIFF -->
