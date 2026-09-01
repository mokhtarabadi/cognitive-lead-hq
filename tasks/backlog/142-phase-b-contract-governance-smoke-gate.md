# Task 142: End-to-End Contract Propagation Smoke Test Suite & Hard Gate

**File:** `tasks/backlog/142-phase-b-contract-governance-smoke-gate.md`
**Source:** orchestrator
**Type:** feature
**Status:** open

## Goal

Implement the end-to-end integration and smoke test suite for Phase B in `loop-engine/test_contract_smoke.py`, validating contract mutation detection, downstream task backlog generation, TypeDriftSentinel fail-fast enforcement, and Spec-First state gating in full daemon lifecycles, serving as the official Hard Gate certifying Phase B.

## Local TODOs

- [ ] Initial codebase exploration (contracts.py, sentinel.py, specs.py, daemon.py)
- [ ] Implement loop-engine/test_contract_smoke.py covering the full Phase B lifecycle
- [ ] Prove downstream task generation in tasks/backlog/ without duplicate cascades
- [ ] Update docs/loop-engine/README.md and configuration.md certifying Phase B
- [ ] Verify full test suite passes

## Acceptance Criteria

- [ ] `loop-engine/test_contract_smoke.py` covers full Phase B lifecycle across contract mutations, downstream task creation, type drift blocking, and spec-first gating.
- [ ] Proves downstream tasks are generated in `tasks/backlog/` and registered in SQLite state without duplicate cascades.
- [ ] Updates `docs/loop-engine/README.md` and `configuration.md` certifying Phase B.
- [ ] Full test suite passes with 0 failures and 0 regressions.

## Verification Evidence

- **Test command:** `python -m pytest loop-engine/ -q`
- **Expected result:** all tests pass, 0 failures, 0 regressions
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Manager Decisions

_(Log non-trivial architectural, design, or strategic decisions here using the format from `<decision_logging_mandate>`: `**[YYYY-MM-DD] [DECISION_ID] [SOURCE]:** <summary>`.)_

## Risk & Rollback

- **Risk:** Smoke suite may be flaky when daemon lifecycle state dependencies diverge.
- **Rollback plan:** Gate the suite behind a marker and skip when state-dependency setup fails.

---

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->