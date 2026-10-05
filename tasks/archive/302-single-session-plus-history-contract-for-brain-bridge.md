# Task 302: Single session plus history contract for Brain bridge

**File:** `tasks/archive/302-single-session-plus-history-contract-for-brain-bridge.md`
**Source:** manager
**Type:** feature
**Status:** superseded
**Superseded-By:** `305-brain-anti-hallucination-harness`
**Superseded-At:** `2026-10-06`
**Risk-Tier:** T1 standard
**Supersedes:** none
**Meta:** false

## Goal

Reduce Brain session binding to one source of truth with a documented history contract so a task id without session id can never silently split threads.

## Manager's Notes

Brainstorm C3 must-task from self-judgment task 299: session roots plus session ledger plus fed-context save and load currently form three sources of truth.

## Scope

In scope:
- `mcp-brain-bridge/server.py` session resolvers, `session_ledger.py`, `loop_guard.py` resolvers, 40-message bound with markers
- Contract spec plus negative tests for bare task id, ambient bind, explicit bind

Out of scope:
- XML gate, attach signaling, parity matrix (separate tasks)
- External repos untouched
- No git add/commit/push by Hands (ZAC holds)
- docs/history, tasks/archive, CHANGELOG history lines immutable

## Local TODOs

- [ ] Inventory bind sources with grep evidence
- [ ] Implement single contract with bound markers
- [ ] Add negative tests and run verification gates

## Acceptance Criteria

- [ ] AC1: one documented bind source with no triple truth
- [ ] AC2: history bound cuts carry markers
- [ ] AC3: full suite passes with evidence recorded

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pathspec pytest tests/ -q
- **Expected result:** pass exit 0
- **Actual result:** pending
- **Exit code:** pending

## Definition of Done

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** bind change splits existing threads if miswired
- **Rollback plan:** worktree diff revert before staging

---

> **Superseded:** This task was bundled into META task `305-brain-anti-hallucination-harness` and archived on 2026-10-06. See `tasks/backlog/305-brain-anti-hallucination-harness.md` (or its Kanban successor) for the unified execution. History preserved via `git log --follow -- tasks/archive/302-single-session-plus-history-contract-for-brain-bridge.md`.

## Execution Log & Reasoning

- Origin: brainstorm C3 from task 299 self-judgment report.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
