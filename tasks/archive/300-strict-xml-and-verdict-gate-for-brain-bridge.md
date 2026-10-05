# Task 300: Strict XML and verdict gate for Brain bridge

**File:** `tasks/backlog/300-strict-xml-and-verdict-gate-for-brain-bridge.md`
**Source:** manager
**Type:** feature
**Status:** open
**Risk-Tier:** T1 standard
**Supersedes:** none
**Meta:** false

## Goal

Make the Brain bridge reject unmarked XML repair so hallucinated plans or closures can never pass as valid. Fallback accept stays only on explicitly marked repair.

## Manager's Notes

Brainstorm C1 must-task from self-judgment task 299: strictness wins because the top goal is the strongest anti-hallucination harness, not fewer halts.

## Scope

In scope:
- `mcp-brain-bridge/server.py` XML extractor, fence repair, semantic validators, plan-verdict and closure validators
- Explicit reject codes plus negative tests for malformed, unclosed, nested, and repaired XML

Out of scope:
- Hub decomposition, attach signaling, session contract (separate tasks)
- External repos untouched
- No git add/commit/push by Hands (ZAC holds)
- docs/history, tasks/archive, CHANGELOG history lines immutable

## Local TODOs

- [ ] Inventory XML repair paths with grep evidence
- [ ] Implement strict gate with reject codes
- [ ] Add negative tests and run verification gates

## Acceptance Criteria

- [ ] AC1: unmarked repair is rejected with explicit codes
- [ ] AC2: marked repair path still works with tests
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

- **Risk:** stricter gate halts more Hands turns needing re-emit
- **Rollback plan:** worktree diff revert before staging

---

## Execution Log & Reasoning

- Origin: brainstorm C1 from task 299 self-judgment report.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
