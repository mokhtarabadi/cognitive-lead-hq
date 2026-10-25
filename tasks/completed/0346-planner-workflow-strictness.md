# Task 346: Planner workflow strictness — ownership, nudges, overdue pressure

**File:** `tasks/completed/0346-planner-workflow-strictness.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Estimate:** 2h
**Sprint:** S26-W43
**Milestone:** M01
**Depends on:** 345

## Goal

Make the planner actually push work forward: an optional `**Owner:**` field parsed and shown (so joint work has a name on it), a "Mine" filter, an agenda that nudges the admin when nothing is claimed while the backlog is non-empty, explicit overdue warnings in `claim_next` and in the agenda, and a documented rule that a bypassed `git mv` is a workflow violation.

## Manager's Notes

- "همه هم سخت گیر باشن روی planner و sprint strategist اگه ادمین یادش رفت هی بهش یاداوری بشه" — the reminder must come from the tool output, not from the dashboard only.
- Ownership is additive: old task files without the field keep working and show "unassigned".
- Nudges must never block a legitimate claim; they are loud warnings, not gates — except unmet dependencies and the WIP/QA ceilings, which already block.

## Local TODOs

- [x] `_parse_task_file` reads `**Owner:**`; `_task_brief` carries `owner`
- [x] `GET /api/plan` and the day view exclude/include by owner; dashboard adds a "Mine" toggle using the signed-in username
- [x] `sprint_daily_agenda`: when nothing is in progress and QA is empty while backlog is non-empty, append a `NUDGE` block naming the top backlog task; list overdue deadlines with counts
- [x] `claim_next`: append an `OVERDUE` warning line listing up to three overdue task ids (never blocking)
- [x] Document the ownership field and the bypass rule in `tasks/README.md` and `mcp-planner-server/README.md`

## Acceptance Criteria

- [x] Briefs carry `owner` (null when absent) and the dashboard shows it on every card
- [x] "Mine" filter narrows lanes to the signed-in username without a server round-trip
- [x] `sprint_daily_agenda` emits a NUDGE when the day is empty and the backlog is not
- [x] `claim_next` reports OVERDUE tasks without refusing the claim
- [x] Task-file docs describe `**Owner:**` and forbid hand-moving files around the planner
- [x] Full planner suite passes with exit code 0

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/test_planner_server.py -q`
- **Expected result:** all tests pass, including new owner and nudge tests
- **Actual result:** `115 passed, 2 warnings in 38.71s` (three new: owner parse/brief, agenda NUDGE, claim_next OVERDUE)
- **Exit code:** 0

## Definition of Done

- [x] `lint_task_file` passes
- [x] `CHANGELOG.md` updated

## Risk & Rollback

- **Risk:** a nudge on every empty day becomes noise; mitigated by emitting it only when the backlog is non-empty.
- **Rollback:** drop the NUDGE/OVERDUE lines and the owner field; filtering disappears, nothing else breaks.

## Execution Log & Reasoning

Night mode, created after 345. Autopilot with self-approved closure.

**Implementation:** `_parse_task_file` reads `**Owner:**` (additive; older files stay valid) and `_task_brief` exposes it, so the dashboard renders an owner badge and the new **Mine only** toggle filters lanes client-side by the signed-in username. `sprint_daily_agenda` adds `NUDGE` when nothing is claimed while the backlog is non-empty, plus `OVERDUE` ids; `claim_next` appends the same overdue warning to a successful claim and never blocks on it. README documents the field and the bypass rule. Deployed to the global install and `mcp-planner` restarted; 115 planner tests pass (three new).

**Decision:** the nudge is a warning, not a gate — dependency, WIP, and QA ceilings remain the only blockers, so a legitimate claim is never refused for style reasons.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `6dfcac7df1f1af8769787cf6a72ce8cb3198f1b0`
<!-- END_GIT_DIFF -->
