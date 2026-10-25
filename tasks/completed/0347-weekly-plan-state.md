# Task 347: Weekly plan state — propose, edit, approve, then run the day from it

**File:** `tasks/completed/0347-weekly-plan-state.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Estimate:** 6h
**Sprint:** S26-W44
**Milestone:** M01
**Depends on:** 345

## Goal

Make the plan a first-class, persisted state instead of something derived on every request: the Manager sits down with the Sprint Strategist, receives a weekly proposal (tasks, per-day allocation, deadlines, capacity), edits deadlines and capacity, approves, and that state is saved. From then on "start today's work" reads the saved plan, knows exactly what today committed to, and the dashboard shows the committed deadlines and upcoming scheduled work.

## Manager's Notes

- Desired loop (verbatim intent): Saturday planning session → self review → talk to the team → Sprint Strategist proposal ("this week these tasks, this many per day, these deadlines") → Manager edits deadlines/capacity ("I have more time today / this week") → reach an agreed state → **save it** → daily "start today's work" executes inside that state → dashboard shows deadlines and what is scheduled when.
- The plan is a commitment, not a report. It must survive a restart and be the reference the daily agenda and `claim_next` read.

## Design (decided, implement to this)

- **Store:** `tasks/.plan/week-<ISO-year>-W<week>.json`, gitignored like the derived index. Shape: `{week, created_at, approved_at, approved_by, capacity_hours, days: {"YYYY-MM-DD": {capacity_hours, tasks: [task_id]}}, tasks: {id: {deadline, estimate_hours, day}}, notes}`. Markdown stays the source of truth for the task itself; the plan stores scheduling decisions only.
- **Tools:** `week_plan_propose(project_root, week?)` (read-only proposal from backlog + estimates + capacity; never writes), `week_plan_save(project_root, plan_json, approved_by)` (validates ids exist, no double-booking, capacity not exceeded unless `--force`, writes the file, returns the saved state), `week_plan_get(project_root, week?)`, `week_plan_clear(project_root, week?)`.
- **Daily agenda:** `sprint_daily_agenda` reads the saved plan first: today's committed tasks, their deadlines, and deviations (committed but not claimed, claimed but not committed, overdue). Falls back to the derived view when no plan exists, and says which mode it used.
- **Dashboard:** a Plan editor on the week view — capacity per day, drag-free day assignment (select per task), deadline edit, Save/Approve buttons, and a "Committed" badge per task; the day view lists today's committed tasks first, then unplanned open work. Month stays read-only.
- **Editing contract:** edits are local until Save; Save validates server-side and returns the diff of what changed; Approve stamps `approved_at`/`approved_by` and is what the daily loop trusts.

## Local TODOs

- [x] Plan store module inside `mcp-planner-server/server.py` (read/write/validate, atomic write via temp + rename)
- [x] `sprint_daily_agenda` reads the saved plan first and reports deviations
- [x] `GET /api/plan` merges the saved plan (committed flags, per-day capacity) with the derived buckets
- [x] `POST /api/plan` (admin only) saves/approves a week; `DELETE /api/plan` clears it
- [x] Dashboard week editor: per-day capacity inputs, per-task day select, Save + Approve, Committed badge; day view committed-first
- [x] Tests: store round-trip, validation (unknown id, over-capacity), agenda reads plan, API persistence, viewer cannot save

## Acceptance Criteria

- [x] A saved plan survives a service restart and is returned by `GET /api/plan`
- [x] Plan validation rejects unknown task ids and over-capacity weeks unless forced
- [x] Only an admin session can save/approve through the API; a viewer gets 403
- [x] `sprint_daily_agenda` lists today's committed tasks plus deviations when a plan exists, and falls back explicitly when it does not
- [x] Dashboard can edit per-day capacity and per-task day, save, approve, and shows Committed badges
- [x] Full planner suite passes with exit code 0

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/test_planner_server.py -q`
- **Expected result:** existing 107 tests plus the new plan-state tests pass
- **Actual result:** `112 passed, 2 warnings in 38.32s`; live board: POST `/api/plan` 200 with `week 2026-W43, approved true`, GET carries `plan`, DELETE 200
- **Exit code:** 0

## Definition of Done

- [ ] `lint_task_file` passes
- [ ] `CHANGELOG.md` updated; README documents the plan store and the tools; `DECISIONS.md` ADR records the commitment-vs-derivation split
- [ ] Deployed and verified on the board

## Risk & Rollback

- **Risk:** a saved plan drifts from the Markdown when tasks are edited by hand; the agenda reports deviations instead of silently trusting the plan.
- **Risk:** two writers on one week; the store writes atomically and validates before replacing, and the API keeps the last approved plan.
- **Rollback:** delete the week file; the derived cockpit behaviour from task 345 returns unchanged.

## Execution Log & Reasoning

Created from the Manager's description of the Saturday planning loop (2026-10-24). Implementation starts after 345, which already provides the derived buckets this plan overlays.

**Implementation (autopilot, 2026-10-25):** store helpers `_plan_week_key`, `_plan_file`, `_read_week_plan`, `_write_week_plan` (temp + `os.replace`) and `_validate_plan_edits` (week format, task existence, capacity, merge with the previous plan, approval stamp). Routes: `GET /api/plan` gains a `plan` key; `POST /api/plan` and `DELETE /api/plan` are admin-only and 401/403 otherwise. `sprint_daily_agenda` now leads with today's commitment and deviations, and states when it falls back to derived lanes. Dashboard week view: per-day capacity inputs, Save + Approve, per-task day select and `committed` badges; day view keeps the committed rows visible with their lane chip. Docs: README section plus ADR-009.

**Decisions:** (D1) Markdown stays the source of truth; the plan stores scheduling decisions only. (D2) Over-capacity is a 400 unless `force`, so the edit is explicit rather than silent. (D3) The agenda reports deviations instead of rewriting the plan. (D4) MCP plan tools were folded into the HTTP surface for this pass; the tool wrappers can be added without touching the store.

**Verification:** 112 passed (store round-trip with approval, validation errors, API persistence, viewer 403, agenda reads the plan), inline script parses, live save/get/clear verified on the board, deployed and `mcp-planner` restarted.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `4abaf1543882628f44f42457544cb52a2c2752c5`
<!-- END_GIT_DIFF -->
