# Task 304: Cache correctness for Brain bridge

**File:** `tasks/archive/304-cache-correctness-for-brain-bridge.md`
**Source:** manager
**Type:** feature
**Status:** superseded
**Superseded-By:** `305-brain-anti-hallucination-harness`
**Superseded-At:** `2026-10-06`
**Risk-Tier:** T1 standard
**Supersedes:** none
**Meta:** false

## Goal

Make the Brain context cache provably correct with explicit eviction and collision tests, defaulting to safe-off until proven.

## Manager's Notes

Brainstorm C5 must-task from self-judgment task 299: correctness wins over cache speed because stale context directly causes hallucinations.

## Scope

In scope:
- `mcp-brain-bridge/server.py` cache-split hashing, static prefix cache, eviction paths
- Collision plus staleness tests across prompt and env change, safe-off default

Out of scope:
- XML gate, attach signaling, session contract (separate tasks)
- External repos untouched
- No git add/commit/push by Hands (ZAC holds)
- docs/history, tasks/archive, CHANGELOG history lines immutable

## Local TODOs

- [ ] Inventory cache paths with grep evidence
- [ ] Implement explicit eviction plus collision tests
- [ ] Run verification gates

## Acceptance Criteria

- [ ] AC1: eviction rules explicit and tested
- [ ] AC2: collision and staleness tests pass
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

- **Risk:** safe-off default raises latency and token spend
- **Rollback plan:** worktree diff revert before staging

---

> **Superseded:** This task was bundled into META task `305-brain-anti-hallucination-harness` and archived on 2026-10-06. See `tasks/backlog/305-brain-anti-hallucination-harness.md` (or its Kanban successor) for the unified execution. History preserved via `git log --follow -- tasks/archive/304-cache-correctness-for-brain-bridge.md`.

## Execution Log & Reasoning

- Origin: brainstorm C5 from task 299 self-judgment report.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
