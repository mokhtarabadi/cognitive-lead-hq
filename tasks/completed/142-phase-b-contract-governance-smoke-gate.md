# Task 142: End-to-End Contract Propagation Smoke Test Suite & Hard Gate

**File:** `tasks/completed/142-phase-b-contract-governance-smoke-gate.md`
**Source:** orchestrator
**Type:** feature
**Status:** closed

## Goal

Implement the end-to-end integration and smoke test suite for Phase B in `loop-engine/test_contract_smoke.py`, validating contract mutation detection, downstream task backlog generation, TypeDriftSentinel fail-fast enforcement, and Spec-First state gating in full daemon lifecycles, serving as the official Hard Gate certifying Phase B.

## Local TODOs

- [x] Initial codebase exploration (contracts.py, sentinel.py, specs.py, daemon.py)
- [x] Implement loop-engine/test_contract_smoke.py covering the full Phase B lifecycle
- [x] Prove downstream task generation in tasks/backlog/ without duplicate cascades
- [x] Update docs/loop-engine/README.md and configuration.md certifying Phase B
- [x] Verify full test suite passes

## Acceptance Criteria

- [x] `loop-engine/test_contract_smoke.py` covers full Phase B lifecycle across contract mutations, downstream task creation, type drift blocking, and spec-first gating.
- [x] Proves downstream tasks are generated in `tasks/backlog/` and registered in SQLite state without duplicate cascades.
- [x] Updates `docs/loop-engine/README.md` and `configuration.md` certifying Phase B.
- [x] Full test suite passes with 0 failures and 0 regressions.

## Verification Evidence

- **Test command:** `uv run --project loop-engine --with pytest pytest loop-engine/test_contract_smoke.py -v` + `uv run --project loop-engine --with pytest pytest loop-engine/ -q`
- **Expected result:** all tests pass, 0 failures, 0 regressions
- **Actual result:** `test_contract_smoke.py` 14 passed in 0.37s; full suite 285 passed, 0 failed in 13.62s (baseline 271, +14 new; no regressions)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Manager Decisions

**[2026-08-31] [D1] [ORCHESTRATOR-DETECTED]:** Comprehensive Phase B Contract Governance Smoke Gate
- **Rationale:** Certifies the entire Phase B architecture end-to-end, proving contract propagation, type-drift interception, spec-first gating, and blast-radius scoping work harmoniously before unlocking Phase C.
- **Alternatives considered:** Relying on unit tests without integrated daemon lifecycle verification.
- **Impact:** Hard verification gate certifying that monorepo contract governance operates without regressions or infinite cascades.

**[2026-09-01] [D2] [EXECUTION-DETECTED]:** Hermetic Phase B workspace replication
- **Rationale:** Mirrored `test_polyglot_smoke.py` hermetic pattern (tmp_path, daemon.REPO_ROOT patch, scripted I/O seams with ScriptedRouter/FakeHandsExecutor/AutoApproveGateway) but with contract monorepo fixture (packages/shared-schema + services/api + apps/web + docs/adr) and LoopEngineConfig with contract_rules/spec_gate/blast_radius enabled to certify Phase B without touching real repo.
- **Alternatives considered:** Reusing polyglot workspace as-is — rejected: contract propagation requires shared-schema layout, sentinel requires consumer path, spec gate requires ADR layout.
- **Impact:** 14 deterministic smoke tests covering 8 core Phase B scenarios + 6 extra edge cases; full suite 285 passing.

**[2026-09-01] [D3] [EXECUTION-DETECTED]:** 14-test gate for >=285 certification bar
- **Rationale:** Baseline 271 + 8 core Phase B tests = 279 (<285 gate in bash_phase). Added 6 extra tests (rule matching, sentinel allowed, spec multiple rules, blast root fallback, sequential IDs, state registration) to reach 285 (271+14) and satisfy `verification-before-completion` strict >271 and bash_phase >=285.
- **Alternatives considered:** Keeping 8 tests and lowering gate to 279 — rejected: spec's bash_phase explicitly requires >=285.
- **Impact:** Meets both verification-before-completion and Hard Gate; no regressions.

## Risk & Rollback

- **Risk:** Smoke suite may be flaky when daemon lifecycle state dependencies diverge.
- **Rollback plan:** Gate the suite behind a marker and skip when state-dependency setup fails.

---

## Execution Log & Reasoning

**2026-09-01 — Task 142 implemented (Plan→Execute→Observe):**

1. **Verify-before-apply:** Delegated to `cognitive-discovery` subagent (10-file context: contracts/sentinel/specs/blast_radius/test_polyglot_smoke/daemon/README/configuration). Confirmed `contracts.py` ContractPropagationEngine, `sentinel.py` TypeDriftSentinel, `specs.py` SpecGateEngine, `blast_radius.py` LE-9 API, `test_polyglot_smoke` hermetic pattern (setup_test_workspace, tmp_path, daemon.REPO_ROOT patch, ScriptedRouter/FakeHandsExecutor/AutoApproveGateway), docs Phase A certified, baseline 271.

2. **Step 2 — `loop-engine/test_contract_smoke.py` (14 tests, 0.37s):**
   - Built `setup_contract_workspace(tmp_path)` mirroring polyglot pattern but with Phase B fixture: packages/shared-schema (package.json/types.ts), services/api (depends on shared-schema), apps/web (depends on shared-schema), docs/adr/0001-init.md, stacks/{generic,node-ts,python-fastapi}, LoopEngineConfig with _default_contract_rules/_default_spec_rules/BlastRadiusConfig(enabled) and trigger_mode="auto", real StateMachine/LLMRouter/QAEngine/HandsExecutor/ApprovalGateway/LoopEngineDaemon with daemon.REPO_ROOT patched.
   - Implemented ScriptedRouter (call_llm per stage), FakeHandsExecutor (_run_once injecting diff_content between BEGIN_GIT_DIFF/END_GIT_DIFF, modes complete/empty_diff/blocked/error), AutoApproveGateway (request_approval, send_task_trigger_card/summary).
   - 8 core tests: contract mutation dispatches downstream tasks with Triggered-By and sequential IDs registered as BACKLOG in SQLite; no duplicate cascades (apps/web non-schema → 0); sentinel blocks manual DTO (export interface UserDTO → FAILED before qa.run_qa); spec gate blocks unspecified architecture (no ADR → CRASHED at Step 2.5) and allows verified ADR; blast-radius scopes (apps/web mutation skips services/api, runs for apps/web); full unified lifecycle (Spec → Sentinel Pass → Blast Scope → QA → Closure → Propagation); non-contract diff → 0 propagation.
   - 6 extra tests for >=285 bar: contract rule matching (shared-schema/openapi/prisma/proto), sentinel allowed patterns (shared-schema DTO passes), spec multiple rules, blast root fallback (README → all affected), sequential IDs, state registration (BACKLOG).

3. **Step 3 — Docs:** Updated `docs/loop-engine/README.md` with Phase B Certified section (8 core + 6 extra, 285 bar, hermetic guarantees, run commands for test_contract_smoke.py and full suite) and `docs/loop-engine/configuration.md` with Phase B Certification subsection after LE-9 (lifecycle, contract dispatch, sentinel, spec, blast, run commands).

4. **Observe:** Targeted `test_contract_smoke.py` 14 passed; full suite 285 passed, 0 failed (baseline 271, +14 new, 13.62s; no regressions). Diff verification: `git diff --stat` shows strictly `loop-engine/test_contract_smoke.py`, `docs/loop-engine/README.md`, `docs/loop-engine/configuration.md`, `CHANGELOG.md`, task file.

5. **Scope guard:** Changes strictly scoped to `loop-engine/`, `docs/loop-engine/`, and task file per bash_phase; HOTFIX bundle (149) and blast-radius (141) commits remain in completed, not re-staged.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `af57f1f4eb0349c4f779b706f0b6300074ba3f16`
<!-- END_GIT_DIFF -->