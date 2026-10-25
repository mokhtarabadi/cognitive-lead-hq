# Task 345: Planner planning cockpit — day/week/month views, charts, deadlines

**File:** `tasks/completed/0345-planner-planning-cockpit.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Estimate:** 4h
**Sprint:** S26-W43
**Milestone:** M01
**Depends on:** 344

## Goal

Turn the dashboard from a status board into a planning cockpit: one data endpoint that buckets work by day, week and month, three switchable views, two small charts (load and capacity), a deadline rail with overdue/today/soon alerts, and a shareable deep link per task — so the Manager can plan a week from any starting day and see what was done versus what is left, and an external collaborator can open exactly one task.

## Manager's Notes

- "داشبورد و نمودار خیلی دوست دارم" — charts must be real, not decorative; inline SVG, design tokens only, no library.
- "برنامه کل هفته از اول یا وسط هفته تا اخر هفته" — the week view is Monday–Sunday and must work mid-week (past days shown as done/elapsed, not hidden).
- "برنامه روزانه … چی کار کردیم و چی مونده" — day view separates done (completed lane with a deadline or closed marker) from open work.
- "ماهانه هم" — month view buckets by ISO week inside the month.
- "ددلاین … هشدار" — overdue, today, and next three days must be visible without opening the timeline.
- Deep link: `?task=<id>` opens the modal on load; every task modal gets a Copy link action.
- No CDN, no build step; Bootstrap 5.3 vendored stays.

## Local TODOs

- [x] Add `GET /api/plan` in `mcp-planner-server/server.py`: `{project_root, window, generated_at, days[], weeks[], totals, alerts}` computed from `_load_all_tasks`, reusing `_relative_root`, `_auth_from_request`, `AuthState.project_allowed` and the `_api_status` fallback root
- [x] Day bucket: `{date, jalali, open, in_progress, done, estimate_hours, tasks[]}`; week bucket adds `capacity_hours` and `remaining_hours`; month bucket groups ISO weeks
- [x] Alerts: `overdue`, `today`, `soon` (next 3 days) with task briefs
- [x] Dashboard: view switcher (Day / Week / Month) persisted in `localStorage`, three panels rendered from `/api/plan`
- [x] Charts: 14-day load bars and weekly estimate-vs-capacity bar as inline SVG using `--gd-*` tokens
- [x] Deadline rail: counts plus the next five due tasks, each opening its modal
- [x] Deep link `?task=<id>` opens the modal on load; Copy link button in the modal header writes the URL
- [x] Tests for `/api/plan` (shape, buckets, alerts, 401, 400 relative root) in `tests/test_planner_server.py`

## Acceptance Criteria

- [x] `GET /api/plan?window=day|week|month` returns 200 with `days`, `weeks`, `totals`, `alerts`; unknown window → 400; relative `project_root` → 400; no session with auth on → 401
- [x] Day view lists open work and done work separately and shows estimate totals
- [x] Week view covers Monday–Sunday of the current week and works mid-week
- [x] Month view groups the current month by ISO week
- [x] Both charts render from `/api/plan` with inline SVG and no external script
- [x] Overdue and next-three-day deadlines appear in a rail without opening the timeline
- [x] `?task=<id>` opens that task's modal, and the modal can copy its link
- [x] Full planner suite passes with exit code 0

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/test_planner_server.py -q`
- **Expected result:** existing 100 tests plus the new `/api/plan` tests pass
- **Actual result:** `105 passed, 2 warnings in 51.52s`; live board `/api/plan` returns 200 for day/week/month with `totals {open:1, in_progress:1, estimate_hours:6.0, capacity_hours:20.0}` and empty alerts
- **Exit code:** 0

## Definition of Done

- [ ] `lint_task_file` passes
- [ ] `CHANGELOG.md` updated
- [ ] `mcp-planner-server/README.md` documents `/api/plan`; `DECISIONS.md` records the bucket contract
- [ ] Deployed to `~/.config/opencode/mcp-planner-server/` and verified live

## Risk & Rollback

- **Risk:** completion history does not exist in the task files, so "done" is derived from the `completed` lane plus deadlines, not from a real closed timestamp — the UI must say so.
- **Risk:** month buckets drift across ISO week boundaries; pinned by tests.
- **Rollback:** remove the route and the three panels; the status board keeps working.

## Execution Log & Reasoning

Night mode, created by the Hands on the Manager's order (2026-10-24). Autopilot: implement, test, deploy, QA, review, self-approve closure.

**Design decisions:** (D1) buckets are computed from the task files at request time — no new store, `tasks/` stays the single source of truth; (D2) "done" is derived from the completed lane plus a deadline inside the bucket because task files carry no closed timestamp, and the UI states this; (D3) undated open work is attributed to the current bucket so the cockpit is never empty on a project whose tasks omit deadlines; (D4) charts are inline SVG built from `--gd-*` tokens, keeping the zero-dependency rule; (D5) the deep link is `?task=<id>` opened client-side, so a collaborator can share one task without a new route.

**Verification:** `105 passed` (five new tests: bucket shape per window, overdue/soon alerts, HTTP 401/400 contract, relative root 400, empty project), both inline scripts parse, live board 200 on all three windows. Deployed `server.py` and `static/index.html` to `~/.config/opencode/mcp-planner-server/` and restarted `mcp-planner`.

**QA fix loop 1 (REJECTED → fixed):** QA found three real defects. F1/F2: week and month buckets copied the Monday row instead of summing the range, so work dated Tuesday–Sunday vanished from the capacity bar and month totals. Fixed by building real day rows for the whole range (7 days / every day of the month) and deriving `weeks` by grouping those rows per ISO week. F3: the day panel rendered one combined list; it now splits "To do" and "Done" with counts. Two regression tests pin the week sum and mid-month inclusion; suite is 107 passed.

**QA fix loop 2 (REJECTED → fixed):** the new day/week branches compared the global `window` object instead of `data.window`, so both fell through to the month template. Corrected on both branches; inline script re-parsed, page redeployed, `mcp-planner` active.

**Review postfix (five items, applied):** README plan-API contract, `DECISIONS.md` ADR-008, CHANGELOG count corrected to 107, a Done-semantics note under the plan totals, and `escapeHtml` on `estimate_hours`. Reviewer then approved.

**Closure (night mode):** the Manager delegated closure approval for the night ("هر کدوم رسید به مرحله approve for closure خودت از طرف من approve کن"). Approved on his behalf and recorded here: QA_PASSED (third pass) + Code Reviewer APPROVED + the five postfix items applied.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `736a1cb08417f53f5eb3566e5910b677c312aa7b`
<!-- END_GIT_DIFF -->
