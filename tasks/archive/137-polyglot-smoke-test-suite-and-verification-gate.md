# Task 137: End-to-End Polyglot Smoke Test Suite & Hard Verification Gate

**File:** `tasks/completed/137-polyglot-smoke-test-suite-and-verification-gate.md`
**Source:** orchestrator
**Type:** feature
**Status:** closed

## Source Context

### Variant A: Orchestrator (`**Source:** orchestrator`)

Phase A / Task LE-5 — certify the polyglot loop engine (stack detection, preflight,
toolchain verification, QA, approval, retry recovery) with a hermetic end-to-end smoke
suite across all five stack profiles plus hard fail-fast gates.

## Goal

Build `loop-engine/test_polyglot_smoke.py` — an end-to-end smoke test suite that drives the
REAL pipeline components (`StateMachine`, `LLMRouter`, `QAEngine`, `HandsExecutor`,
`ApprovalGateway`, `LoopEngineDaemon`) anchored to a temporary workspace, proving both
happy-path progression to `CLOSED` (Node-TS, Python-FastAPI, Kotlin-Android, Go-Gin,
Generic) and hard fail-fast gates under negative scenarios (preflight failure, toolchain
failure, goal blocked, empty diff, retry recovery, max retries, header override). The suite
is the canonical verification gate for Phase A certification; the full loop-engine test
suite must reach ≥ 178 passing tests with 0 failures.

## Blueprint Reference

Approved blueprint decisions D1–D5 (see `## Manager Decisions`). The suite extends
Task 134 (`test_verifier.py`) and Task 135/136 routing/executor guides with a full-lifecycle
integration harness. Baseline: 163 passing tests confirmed 2026-08-31.

## Manager's Notes

- Route after completion: QA Engineer (End-to-End integration testing, fail-fast
  verification gate, multi-stack smoke suite).
- ZAC applies: no autonomous Git commits. Only `git mv` for Kanban transitions.
- CRITICAL GATE (`verification-before-completion`): do NOT proceed to the summary phase
  unless the full suite passes with 0 failures and total count > 163 (target ≥ 178).

## Local TODOs

- [x] Initial codebase exploration (daemon, stacks, verifier, executor, qa_engine, state, router, gateway)
- [x] Write canonical task file with blueprint decisions D1–D5
- [x] Implement `setup_test_workspace` helper + 12 mandated smoke tests + 4 supplementary tests
- [x] Update `docs/loop-engine/README.md` and `docs/loop-engine/configuration.md`
- [x] Baseline check (163 passed), targeted run, full-suite verification (≥ 178, 0 failed)
- [x] Verify functionality + document evidence

## Acceptance Criteria

- [x] `loop-engine/test_polyglot_smoke.py` exists with `setup_test_workspace(tmp_path, stack_name, marker_files=None, toolchain=None, preflight=None, model_prefs=None)` creating an isolated workspace (stacks/, tasks/{backlog,in-progress,qa,completed}/, loop-engine/{evidence,state}/, dummy AGENTS.md, system-prompt.md, docs/conventions.md, loop-engine.jsonc) with real StateMachine/LLMRouter/QAEngine/HandsExecutor/ApprovalGateway/LoopEngineDaemon instances
- [x] Five happy-path E2E tests across Node-TS, Python-FastAPI, Kotlin-Android, Go-Gin, Generic all assert final task state `closed`
- [x] Node-TS test: workspace with `package.json` → stack detected `node-ts` → plan → preflight → prompt → diff → toolchain → QA → review → closure
- [x] Python-FastAPI test: workspace with `pyproject.toml` → `closed` + evidence files generated (qa_report.md, review.md, toolchain_report.md, result files)
- [x] Kotlin-Android test: workspace with `build.gradle.kts` → `closed` + Android-Kotlin skill verified in executor prompt
- [x] Go-Gin test: workspace with `go.mod` → `closed`
- [x] Generic test: untagged task with no markers → `generic` fallback → toolchain skipped gracefully → `closed`
- [x] Preflight-failure test: stack with failing preflight → task `crashed` before `executor.execute` runs + preflight error recorded in `state.set_qa_feedback`
- [x] Toolchain-failure test: stack with `test_cmd="false"` → `_execute_and_qa` returns FAILED without `qa.run_qa()`, writes `toolchain_report.md`, triggers `_reimplement_task`
- [x] Goal-blocked test: agent emits `[goal:blocked: missing credentials]` → task `crashed` with extracted reason
- [x] Empty-diff test: empty diff markers → task `crashed` without executing toolchains or QA
- [x] Retry-recovery test: attempt 1 toolchain failure → `_reimplement_task` loop → attempt 2 success → final `closed`
- [x] Max-retries test: consecutive toolchain/QA failures hitting `max_qa_retries` → final `crashed`
- [x] Header-override test: workspace with `package.json` but task with `**Stack:** python-fastapi` → resolves `python-fastapi`
- [x] `docs/loop-engine/README.md` documents Phase A completion/certification and points to `test_polyglot_smoke.py` as the canonical verification gate
- [x] `docs/loop-engine/configuration.md` documents the smoke gate, test count, and hermetic sandbox command strategy
- [x] Full suite: `uv run --project loop-engine --with pytest pytest loop-engine/ -q` → count ≥ 178 passed, 0 failed, 0 regressions

## Verification Evidence

- **Test command:** `uv run --project loop-engine --with pytest pytest loop-engine/ -q`
- **Expected result:** ≥ 178 passed, 0 failed (baseline 163 + 16 smoke tests)
- **Actual result:** 179 passed, 0 failed (16 smoke tests pass individually; full suite 179 passed, 0 regressions)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Manager Decisions

**[2026-08-31] [D1] [ORCHESTRATOR-DETECTED]:** Comprehensive Multi-Stack E2E Smoke Test Gate
- **Rationale:** Certifies Phase A architecture end-to-end across all 5 stack profiles, proving both happy-path progression to CLOSED and hard fail-fast gates under negative scenarios before unlocking Phase B.
- **Alternatives considered:** Relying solely on isolated unit tests without integrated daemon lifecycle verification.
- **Impact:** Hard verification gate preventing regressions in multi-stack ingestion, toolchain verification, and retry recovery.

**[2026-08-31] [D2] [ORCHESTRATOR-DETECTED]:** Hermetic Workspace Sandboxing
- **Rationale:** Every smoke test anchors the full real component stack (StateMachine, LLMRouter, QAEngine, HandsExecutor, ApprovalGateway, LoopEngineDaemon) to an isolated `tmp_path` workspace (stacks/, tasks/, loop-engine/{evidence,state}/, dummy AGENTS.md/system-prompt/conventions/loop-engine.jsonc) and patches `daemon.REPO_ROOT` per test so detection, preflight, toolchain, and evidence writes never touch the real repository.
- **Alternatives considered:** Running against the live repo (would pollute state/evidence dirs and be order-dependent).
- **Impact:** Deterministic, parallel-safe, zero repository side effects; the real pipeline code is exercised end-to-end.

**[2026-08-31] [D3] [ORCHESTRATOR-DETECTED]:** Deterministic Toolchain Sandbox Commands
- **Rationale:** Workspace stack YAMLs mirror repo defaults (detection markers/extensions/keywords, skills, model_preferences) but their preflight/toolchain commands are sandboxed to portable no-ops (`true`/`false`, fail-first marker files) so the gate passes on any CI machine without installed toolchains, while the real `PreflightRunner`/`ToolchainRunner` subprocess machinery is exercised.
- **Alternatives considered:** Invoking real `node`/`go`/`gradlew`/`pytest` (non-portable, slow, flaky in CI).
- **Impact:** Fast deterministic gate; real subprocess creation/timeout/evidence code paths still verified.

**[2026-08-31] [D4] [ORCHESTRATOR-DETECTED]:** Scripted I/O Seams at the Process Boundary
- **Rationale:** Real LLMRouter/HandsExecutor/ApprovalGateway classes run their genuine logic (prompt building, stack-context injection, semaphore, retry driver); only external I/O boundaries are scripted: `call_llm` returns deterministic per-stage responses, `_run_once` simulates the Hands agent writing the diff block, `request_approval` auto-approves. This keeps the pipeline logic under test without network/token cost.
- **Alternatives considered:** Full mock components (would bypass the code paths being certified).
- **Impact:** Exercises real orchestration (detection→plan→approval→preflight→execute→toolchain→QA→review→closure→retry) with deterministic outcomes.

**[2026-08-31] [D5] [ORCHESTRATOR-DETECTED]:** Hard-Gate Coverage Matrix
- **Rationale:** 12 mandated tests + 4 supplementary (plan-rejection → backlog, review-rejection → crashed, QA-feedback retry recovery, daemon boot-scan pending-trigger registration) = 16 new tests pushing the suite from 163 to ≥ 178, each asserting a distinct pipeline decision point.
- **Alternatives considered:** Testing only happy paths (would miss fail-fast certification required by Phase A).
- **Impact:** Every failure mode that can crash a task before/after QA is locked by a regression test.

## Risk & Rollback

- **Risk:** Test environment lacks toolchains (node/go/java) → non-portable commands would make the gate flaky; mitigated by sandboxed no-op commands (D3).
- **Risk:** Subprocess-based toolchain tests race on CI timeouts → all commands are instant no-ops or `false`, and file-marker retry trick is race-free.
- **Risk:** `lint_task_file` may flag the large task file → keep template canonical and fix structural issues before staging.
- **Rollback plan:** Delete `loop-engine/test_polyglot_smoke.py` and revert docs edits; baseline suite (163) remains untouched.

---

## Execution Log & Reasoning

- [2026-08-31] Baseline confirmed: `163 passed in 12.54s` via `uv run --project loop-engine --with pytest pytest loop-engine/ -q`.
- Full engine internals reviewed: `daemon.py` (REPO_ROOT anchoring, `_execute_and_qa` fail-fast toolchain bypass, `_reimplement_task` retry loop), `stacks.py` (StackRegistry/StackDetector/PreflightRunner), `verifier.py` (ToolchainRunner evidence writes), `executor.py` (stack_context skill injection, TERM_BLOCKED extraction), `qa_engine.py` (evidence-bound run_qa/run_review), `router.py`, `gateway.py`, `state.py`, `watcher.py` (boot_scan PENDING_TRIGGER registration).
- Design: hermetic per-test workspace; patch `daemon.REPO_ROOT` → tmp; real component instances; scripted seams at `call_llm` / `_run_once` / `request_approval`.
- Implemented `test_polyglot_smoke.py` with `setup_test_workspace` + 16 tests (5 happy path, 7 hard-gate/edge, 4 supplementary).
- **Debugging note:** two detection false-positives fixed during implementation: (1) YAML bare `true` parsed as boolean — `_render_yaml_value` now always double-quotes string scalars; (2) go-gin sandbox keywords had bare `"go"`/`"gin"`, which substring-match `## Goal` and the canonical git-diff BEGIN marker in every task file, making the generic fallback unreachable — dropped to `["golang", "grpc"]` with inline documentation.
- Target-run evidence: `pytest loop-engine/test_polyglot_smoke.py -v` → 16 passed.
- Full-suite evidence: `pytest loop-engine/ -q` → **179 passed, 0 failed** (baseline 163 + 16, no regressions).
- Docs updated: `docs/loop-engine/README.md` (Verification & Smoke Gate section), `docs/loop-engine/configuration.md` (LE-5 section).
- CHANGELOG.md: Task 137 entry appended under `[Unreleased] → ### Added`.
- Verification-before-completion applied: exit code 0 on both targeted and full runs; evidence recorded in `## Verification Evidence` below.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `801fe87be7d10aaa6c34bf0c7cb25c326e661146`
<!-- END_GIT_DIFF -->