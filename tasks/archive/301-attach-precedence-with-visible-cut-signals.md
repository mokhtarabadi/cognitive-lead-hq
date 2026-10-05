# Task 301: Attach precedence with visible cut signals

**File:** `tasks/backlog/301-attach-precedence-with-visible-cut-signals.md`
**Source:** manager
**Type:** feature
**Status:** open
**Risk-Tier:** T1 standard
**Supersedes:** none
**Meta:** false

## Goal

Give every Brain context attach a defined precedence order with visible cut signals at per-file and total caps so no truncation ever happens silently.

## Manager's Notes

Brainstorm C2 must-task from self-judgment task 299: truncation is the worst option for large context and Hands must always see inline versus file versus chunked plus what was cut.

## Scope

In scope:
- `mcp-brain-bridge/server.py` attach builders, per-file 60k and total 200k caps, history bound markers
- Boundary tests at cap minus 1, cap, cap plus 1 plus total overflow

Out of scope:
- XML gate, session contract, parity matrix (separate tasks)
- External repos untouched
- No git add/commit/push by Hands (ZAC holds)
- docs/history, tasks/archive, CHANGELOG history lines immutable

## Local TODOs

- [ ] Inventory attach paths and caps with grep evidence
- [ ] Implement precedence plus cut signals plus bound markers
- [ ] Add boundary tests and run verification gates

## Acceptance Criteria

- [ ] AC1: every cut emits a visible signal naming what was cut
- [ ] AC2: precedence order documented and tested at boundaries
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

- **Risk:** larger prompts from signals increase token spend
- **Rollback plan:** worktree diff revert before staging

---

## Execution Log & Reasoning

- Origin: brainstorm C2 from task 299 self-judgment report.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
