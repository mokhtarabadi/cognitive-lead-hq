# Task 0357: Planner board — numeric sort, deep-link fix, daily/weekly hours chart

**File:** `tasks/in-progress/0357-planner-board-sort-deeplink-hours.md`
**Source:** manager
**Type:** feature
**Status:** open

## Goal

Three small planner-board UI fixes in one task: (A) sort every rendered task list by task number ascending; (B) make `?task=<id>` deep links work reliably on the public board (no cryptic auth/HTML errors); (C) add a daily + weekly measured-hours chart built from the task time stamps.

## Manager's Notes

> روی planner mcp دوتا تغییر ریز ui میخوام. تسک‌ها توی kanban بر اساس شماره از کم به زیاد sort بشه کلا همه جا sort بشه. وقتی با لینک باز میکنم مثلا `?task=283` گاها خطا میده auth یا بخش بالا این رو میزنه "Server unreachable: Unexpected token '<'…" ولی اگه تسک مشخص نکرده باشم کار میکنه. میخوام یه جایی یه آماری چارتی از ساعات روزانه و هفتگی هم باشه که داخل تسک‌ها حساب میشه.

## Findings (grounded)

- F1: `mcp-planner-server/server.py:333` sorts lane files lexically (`sorted(glob)`). Filenames mix widths (`283-*.md` vs `0356-*.md`), so lexical order is not numeric order. Same risk in milestone tree, plan buckets, deadline rail.
- F2: `static/index.html:856-857` calls `openTaskModal(id)` immediately on load with no `project_root`, before the first `fetchStatus` resolves (so `currentProject` is unset) and before login. On the authed public board the modal fetch can 401 while the board itself is still loading. `fetchStatus` (`index.html:246-270`) calls `resp.json()` directly: if the edge ever serves the dashboard HTML for `/api/*`, the board shows the cryptic `Unexpected token '<', "<!DOCTYPE"…` instead of a diagnosis.
- F3: Per-task measured data already exists (`_task_brief`, `server.py:1703`: `elapsed_seconds`, `started_at/submitted_at/finished_at`, `estimate_hours`). No daily/weekly aggregation or chart exists yet; `renderPlanChart` (`index.html:622`) is the reusable SVG pattern.

## Local TODOs

- [x] A: numeric sort by task id in lanes, milestone tree, plan buckets, deadline rail
- [x] B: defer deep-link modal until first successful status; pass project_root; login-then-retry; non-JSON API response diagnosis
- [x] C: server daily/weekly measured-hours aggregation + SVG chart block
- [x] Verify functionality

## Acceptance Criteria

- [x] A: every task list on the board (lanes, milestones, plan day/week views, deadline rail) renders lowest task number first, regardless of filename width
- [x] B: opening `?task=283` on the public board either opens the task (logging in first when needed and retrying after login) or shows a human-readable reason; the status line never shows a raw `Unexpected token` dump
- [x] C: the board shows measured hours per day (last 14 days) and per week, derived from task stamps, as a chart next to the existing plan chart
- [x] Full suite green; no other board behavior changed

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/test_planner_server.py -q
- **Expected result:** lane order numeric with mixed-width fixtures; milestone order numeric; hours math measured-only; JS syntax valid
- **Actual result:** `122 passed` (3 new: mixed-width lane sort, milestone sort, hours aggregation); inline JS `node --check` clean; `server.py` AST clean
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** sorting by int id changes order for lanes with unparseable names; mitigated by falling back to name order when no numeric prefix exists.
- **Risk:** tunnel ingress serving HTML for `/api/*` is infra, not code; the client fix diagnoses it instead of masking it — Manager checks ingress rule order (`/api/*` before catch-all).
- **Rollback:** revert `server.py` + `static/index.html`; the board returns to current behavior.

---

## Execution Log & Reasoning

**Diagnosis (joint, Hands + Brain):** the `Unexpected token '<'` crash is the edge serving an HTML login/challenge page with HTTP 200 for `/api/*` when the Access session lapses, while `fetchStatus` calls `resp.json()` unguarded. Live probes without a session return correct 401s on `/api/status`, `/api/me` and `/api/task?id=283`, proving the app never emits HTML on API routes — so the HTML must come from the edge, and the intermittence matches session-valid (JSON 401, handled) vs session-lapsed (HTML 200, crash). Brain confirmed the diagnosis in the same planning turn.

**A (sort):** new `_task_sort_key` (`server.py`, leading filename integer, lexical fallback for unparseable names) applied at the single choke point `_load_all_tasks` per-lane glob, plus explicit sorts for milestone groups, plan buckets and alert rails (these inherit mixed-lane load order). Deadlines stay date-ordered by design.

**B (deep link):** `?task=` no longer fires on page load. The id waits in `pendingDeepTask` until the first successful status (project root + auth known), then opens with `project_root`. A 401 in the modal shows login and retries once automatically after sign-in (`pendingTaskModalId`). `fetchStatus` reads text first and names the cause ("board served a page instead of data") instead of dumping the token. Infra note kept in the task: tunnel ingress must keep `/api/*` ahead of catch-all — code diagnoses, it cannot route.

**C (hours):** new read-only `GET /api/hours` aggregating `elapsed_seconds` by UTC finish date (14 daily + 8 weekly rows, measured-only, unstamped skipped), same 401/403 contract as status; dashboard block reuses the `renderPlanChart` SVG pattern; the stale "no closed timestamp" note corrected to describe stamp semantics.

**Assumption A1:** attribution by finish date (a task's hours land on the day it closed); weekly buckets are ISO Monday–Sunday. Reason: finish is the only measured day boundary the stamps support.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
