# Task 345: Planner planning cockpit — day/week/month views, charts, deadlines

**File:** `tasks/qa/0345-planner-planning-cockpit.md`
**Source:** manager
**Type:** feature
**Status:** in-progress
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

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 6b7027d..2a2e3ae 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Planner planning cockpit: day, week and month views with charts and deadline pressure (Task 345):** new `GET /api/plan?window=day|week|month` returns buckets computed from `tasks/` — day (today), week (Monday–Sunday, mid-week safe) and month (ISO weeks of the current month) — plus a 14-day `trend`, per-week `capacity_hours` / `remaining_hours` against `PLANNER_WEEKLY_CAPACITY`, and `alerts` split into overdue / today / next-three-days. Undated open work is attributed to the current bucket, because counting deadlines alone rendered an empty cockpit; completion history does not exist in the task files, so "done" means a completed-lane task carrying a deadline in the bucket and the UI says so. The dashboard gains a Day/Week/Month switcher persisted in `localStorage`, a capacity bar, an inline-SVG 14-day load chart (open / in-progress / done, design tokens only), a deadline rail whose rows open the task modal, deep links via `?task=<id>`, and a Copy-link action in the modal header. Constants: 400 on an unknown window or a relative root, 401 without a session. Verified: 107 planner tests pass (seven new), live board returns 200 for all three windows with correct totals.
+
 - **Planner MCP and daily pacing are native to the system prompt (Task 340):** `prompts/fragments/11-execution_workflow.md` now carries a *Planner MCP and daily pacing* block after Step 9 — the singleton at `127.0.0.1:8108`, `tasks/` Markdown as the single source of truth, `sprint_daily_agenda` on "start today's work" in any language (the Persian trigger is quoted), `claim_next` instead of hand-moving a task file with refusals reported not bypassed, `plan_status`/`qa_budget` for sizing the day (one unresolved review ceiling), and `sprint_check_daily_quota` with `DAILY_QUOTA_REACHED` → present `sprint_stats` and stop claiming. It sits inside the existing tag, so the splitter manifest needed no change. `<system_version>` bumps `9.64.1 → 9.65.0`, the pin in `tests/test_prompt_sync.py` follows, and `system-prompt.md` was reassembled (109,554 bytes). Verified: 103 prompt/splitter tests pass including `test_system_prompt_split_assemble_round_trip` (byte-identical), `check_docs_sync.py` prints `docs-sync: OK`; the prompt was deployed to `~/.config/opencode/system-prompt.md` byte-identical and `mcp-brain` restarted.
 
 - **`DESIGN.md` — Graphite Desk, one contract for both UIs:** the repo had no design system, so the Planner dashboard carried scattered slate/cyan tokens with mixed radii and the Prompt Composer was raw Tailwind defaults with six rainbow preset pills. The Manager reviewed four proposals and chose **A · Graphite Desk**: near-black slate surfaces (`#0b0e14` / `#141a23` / `#1b2430`), hairline borders `#263141`, one mint accent `#5eead4` with ink `#04211d`, four state colours, an 8px grid, a fixed 4/6/8/12 radius scale, Inter for UI and JetBrains Mono for ids/paths/diffs, and no shadows outside modals. The file also fixes component specs (buttons, lanes, tabs, inputs, preset chips, diff blocks, task modal), layout widths (1200 / 960), motion (120/180ms with reduced-motion honoured) and Stitch prompts. The Planner dashboard was re-skinned onto these tokens under task 339 — gradient gauge replaced, lane chips reduced to neutral plus semantic text, hard-coded greys removed — deployed byte-identical to `~/.config/opencode/mcp-planner-server/static/` and served live by `mcp-planner`. The Prompt Composer port is task 343 so it can drop the Tailwind CDN without touching this diff.
diff --git a/mcp-planner-server/DECISIONS.md b/mcp-planner-server/DECISIONS.md
index 0db36be..29d8114 100644
--- a/mcp-planner-server/DECISIONS.md
+++ b/mcp-planner-server/DECISIONS.md
@@ -152,3 +152,10 @@ ADR-006 below. Session auth, scoping, and the CLI remain as decided here.
   and `::test_api_status_stays_guarded_while_mcp_is_open`.
 - **Rollback:** Restore the cookie/role checks in `_guarded_mcp_app` and the
   three guard tests; no config or dashboard change is involved.
+
+## [2026-10-24] ADR-008: Plan buckets are computed per request, not stored
+
+- **Context:** the Manager asked for day/week/month planning views with charts and deadline pressure. Completion history does not exist in `tasks/` Markdown, and adding a second store would break the "Markdown is the single source of truth" rule.
+- **Decision:** `GET /api/plan` derives `days`, `weeks`, `trend` (14 days), `totals` and `alerts` from `_load_all_tasks` on every request. Week rows sum the day rows they contain; month builds every day of the month and groups by ISO week. Open work without a deadline is attributed to the current bucket so the view is never empty. `done` is a completed-lane task with a deadline in the bucket, and the UI states that history is not stored. Capacity comes from `PLANNER_WEEKLY_CAPACITY`.
+- **Consequences:** no migration, no cache to invalidate, and a slow project with thousands of tasks pays a full scan per request (acceptable at 337 tasks; revisit if it grows). Charts read `trend`, so a future history feature only needs to extend that array.
+- **Rollback:** remove the route and the three dashboard panels; `/api/status` keeps working unchanged.
diff --git a/mcp-planner-server/README.md b/mcp-planner-server/README.md
index 7ca6fa1..41c5a99 100644
--- a/mcp-planner-server/README.md
+++ b/mcp-planner-server/README.md
@@ -125,3 +125,23 @@ the tunnel goes live, then verify: `https://planner.example.com/mcp` → 404,
 - No external integrations in v1 (GitHub/Telegram/Asana/Plane deferred).
 - Zero-Autonomous-Commit: agents never `git commit`/`git push`; staging goes
   through `custom_context_stage_and_inject_diff`.
+
+## Planning API (`GET /api/plan`)
+
+`GET /api/plan?window=day|week|month[&project_root=<abs path>]` returns the
+cockpit buckets: `days`, `weeks`, `trend` (14 days), `totals` and `alerts`
+(`overdue`, `today`, `soon` = next three days). Buckets are computed from
+`tasks/` at request time — there is no second store.
+
+- `day` is today; `week` is Monday–Sunday of the current week (safe mid-week);
+  `month` covers every day of the current month and groups it by ISO week.
+- Week rows sum the days they contain (`open`, `in_progress`, `done`,
+  `estimate_hours`) and compare the estimate against `PLANNER_WEEKLY_CAPACITY`
+  (`capacity_hours`, `remaining_hours`).
+- Open work without a deadline is attributed to the current bucket, so the
+  cockpit is never empty on a project whose tasks omit deadlines.
+- `done` means a task in the `completed` lane carrying a deadline inside the
+  bucket; task files store no closed timestamp, and the UI says so.
+- `project_root` must be absolute (`400` otherwise); `window` must be one of
+  the three values (`400`); with auth enabled the route answers `401` without a
+  session and `403` outside the session's grants.
diff --git a/mcp-planner-server/server.py b/mcp-planner-server/server.py
index e90d23a..efbd6f8 100644
--- a/mcp-planner-server/server.py
+++ b/mcp-planner-server/server.py
@@ -59,7 +59,7 @@ import sys
 import time
 import uuid
 from contextlib import asynccontextmanager
-from datetime import date, datetime, timedelta
+from datetime import date, datetime, timedelta, timezone
 from pathlib import Path
 from typing import Any, Optional
 
@@ -1470,6 +1470,180 @@ def _api_task(
         return {"error": "internal error"}
 
 
+_PLAN_WINDOWS = ("day", "week", "month")
+
+
+def _empty_bucket(day: date) -> dict:
+    """One planning bucket; ``jalali`` is filled by the client."""
+    return {
+        "date": day.isoformat(),
+        "jalali": None,
+        "open": 0,
+        "in_progress": 0,
+        "done": 0,
+        "estimate_hours": 0.0,
+        "tasks": [],
+    }
+
+
+def _plan_payload(
+    project_root: Optional[str] = None, window: str = "week", auth=None
+) -> dict:
+    """Return day/week/month planning buckets (``GET /api/plan``).
+
+    Completion history is not stored in the task files, so "done" means a task
+    that sits in the ``completed`` lane and carries a deadline inside the
+    bucket. That limitation is part of the contract and is stated in the README
+    and in the dashboard, rather than being papered over with a fake timestamp.
+
+    Args:
+        project_root: Optional absolute root from ``?project_root=``.
+        window: ``day``, ``week`` or ``month`` (validated by the route).
+        auth: Optional session view; ``None`` is open local mode.
+
+    Returns:
+        ``{project_root, window, generated_at, days, weeks, totals, alerts,
+        trend}`` or ``{"error": ...}``.
+    """
+    if auth is not None and not auth.authenticated:
+        return {"error": "unauthenticated"}
+    root = _resolve_dashboard_root(project_root)
+    if auth is not None and not auth.project_allowed(root):
+        if project_root and project_root.strip():
+            return {"error": "forbidden"}
+        fallback = _first_allowed_root(auth)
+        if fallback is None:
+            return {"error": "forbidden"}
+        root = fallback
+
+    today = date.today()
+    week_start = today - timedelta(days=today.weekday())
+    capacity = float(_WEEKLY_CAPACITY_HOURS or 0)
+
+    buckets: dict[str, dict] = {}
+    open_lanes = ("backlog", "in-progress", "qa")
+
+    def bucket_for(day: date) -> dict:
+        key = day.isoformat()
+        if key not in buckets:
+            buckets[key] = _empty_bucket(day)
+        return buckets[key]
+
+    alerts = {"overdue": [], "today": [], "soon": []}
+    undated: list[tuple[dict, str]] = []
+    for task in _load_all_tasks(root):
+        lane = task.get("lane")
+        brief = _task_brief(task)
+        deadline_raw = task.get("deadline")
+        try:
+            deadline = date.fromisoformat(str(deadline_raw)) if deadline_raw else None
+        except ValueError:
+            deadline = None
+        if deadline is not None:
+            bucket = bucket_for(deadline)
+            bucket["tasks"].append(brief)
+            bucket["estimate_hours"] += float(task.get("estimate_hours") or 0)
+            if lane == "completed":
+                bucket["done"] += 1
+            elif lane == "in-progress":
+                bucket["in_progress"] += 1
+            elif lane in open_lanes:
+                bucket["open"] += 1
+        if lane in open_lanes and deadline is not None:
+            delta = (deadline - today).days
+            if delta < 0:
+                alerts["overdue"].append(brief)
+            elif delta == 0:
+                alerts["today"].append(brief)
+            elif delta <= 3:
+                alerts["soon"].append(brief)
+        elif lane in open_lanes:
+            undated.append((task, brief))
+
+    if window == "day":
+        days = [today]
+    elif window == "week":
+        days = [week_start + timedelta(days=offset) for offset in range(7)]
+    else:
+        first = today.replace(day=1)
+        next_month = (first + timedelta(days=32)).replace(day=1)
+        days = [first + timedelta(days=i) for i in range((next_month - first).days)]
+
+    day_rows = [bucket_for(day) for day in days]
+
+    # Undated open work is what "still to do" means in practice: most task
+    # files carry no deadline, so counting deadlines alone would render an
+    # empty cockpit. Attribute it to the current bucket (today, this week, or
+    # the month's first day) and keep the count honest in ``totals``.
+    anchor = today if window == "day" else (week_start if window == "week" else days[0])
+    anchor_bucket = bucket_for(anchor)
+    for task, brief in undated:
+        anchor_bucket["tasks"].append(brief)
+        anchor_bucket["estimate_hours"] += float(task.get("estimate_hours") or 0)
+        if task.get("lane") == "in-progress":
+            anchor_bucket["in_progress"] += 1
+        else:
+            anchor_bucket["open"] += 1
+
+    weeks: list[dict] = []
+    if window in ("week", "month"):
+        grouped: dict[str, list[dict]] = {}
+        for row in day_rows:
+            day = date.fromisoformat(row["date"])
+            key = (day - timedelta(days=day.weekday())).isoformat()
+            grouped.setdefault(key, []).append(row)
+        for start_key in sorted(grouped):
+            rows = grouped[start_key]
+            start = date.fromisoformat(start_key)
+            estimate = round(sum(r["estimate_hours"] for r in rows), 2)
+            weeks.append(
+                {
+                    "start": start_key,
+                    "end": (start + timedelta(days=6)).isoformat(),
+                    "label": f"{start.isocalendar()[0]}-W{start.isocalendar()[1]:02d}",
+                    "open": sum(r["open"] for r in rows),
+                    "in_progress": sum(r["in_progress"] for r in rows),
+                    "done": sum(r["done"] for r in rows),
+                    "estimate_hours": estimate,
+                    "capacity_hours": capacity,
+                    "remaining_hours": round(capacity - estimate, 2),
+                }
+            )
+
+    trend = []
+    for offset in range(13, -1, -1):
+        day = today - timedelta(days=offset)
+        row = bucket_for(day)
+        trend.append(
+            {
+                "date": day.isoformat(),
+                "open": row["open"],
+                "in_progress": row["in_progress"],
+                "done": row["done"],
+                "estimate_hours": round(row["estimate_hours"], 2),
+            }
+        )
+
+    totals = {
+        "open": sum(b["open"] for b in day_rows),
+        "in_progress": sum(b["in_progress"] for b in day_rows),
+        "done": sum(b["done"] for b in day_rows),
+        "estimate_hours": round(sum(b["estimate_hours"] for b in day_rows), 2),
+        "capacity_hours": capacity,
+    }
+
+    return {
+        "project_root": str(root),
+        "window": window,
+        "generated_at": datetime.now(timezone.utc).isoformat(),
+        "days": day_rows,
+        "weeks": weeks,
+        "trend": trend,
+        "totals": totals,
+        "alerts": alerts,
+    }
+
+
 def _api_status(
     project_root: Optional[str] = None, auth: Optional[AuthState] = None
 ) -> dict:
@@ -1623,6 +1797,26 @@ def build_app():
             return JSONResponse(payload, status_code=500)
         return JSONResponse(payload)
 
+    async def api_plan(request):
+        root = request.query_params.get("project_root")
+        if _relative_root(root):
+            return JSONResponse(
+                {"error": "project_root must be absolute"}, status_code=400
+            )
+        window = (request.query_params.get("window") or "week").strip().lower()
+        if window not in _PLAN_WINDOWS:
+            return JSONResponse({"error": "invalid window"}, status_code=400)
+        auth = _auth_from_request(request)
+        payload = _plan_payload(root, window, auth)
+        error = payload.get("error")
+        if error == "unauthenticated":
+            return JSONResponse(payload, status_code=401)
+        if error == "forbidden":
+            return JSONResponse(payload, status_code=403)
+        if error == "internal error":
+            return JSONResponse(payload, status_code=500)
+        return JSONResponse(payload)
+
     async def api_login(request):
         if not _AUTH_ENABLED:
             return JSONResponse(
@@ -1731,6 +1925,7 @@ def build_app():
         Route("/", dashboard),
         Route("/api/status", api_status),
         Route("/api/task", api_task),
+        Route("/api/plan", api_plan),
         Route("/api/login", api_login, methods=["POST"]),
         Route("/api/logout", api_logout, methods=["POST"]),
         Route("/api/me", api_me),
diff --git a/mcp-planner-server/static/index.html b/mcp-planner-server/static/index.html
index ed6dc49..3c66ea6 100644
--- a/mcp-planner-server/static/index.html
+++ b/mcp-planner-server/static/index.html
@@ -71,6 +71,37 @@
     <div class="small text-muted mt-2" id="pacing-sub">Fetching status…</div>
   </div></div>
 
+  <!-- Plan cockpit -->
+  <section class="mb-4" id="plan-section">
+    <div class="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-2">
+      <span class="label mb-0">Plan</span>
+      <div class="d-flex gap-1" role="group" aria-label="Plan window">
+        <button type="button" class="btn btn-sm btn-outline-secondary" data-window="day">Day</button>
+        <button type="button" class="btn btn-sm btn-outline-secondary" data-window="week">Week</button>
+        <button type="button" class="btn btn-sm btn-outline-secondary" data-window="month">Month</button>
+      </div>
+    </div>
+    <div class="row g-3">
+      <div class="col-12 col-lg-8">
+        <div class="card h-100"><div class="card-body">
+          <div class="d-flex justify-content-between align-items-baseline mb-2">
+            <span class="label mb-0" id="plan-title">—</span>
+            <span class="small text-muted mono" id="plan-totals"></span>
+          </div>
+          <div id="plan-view"></div>
+          <div class="small text-muted mt-2">Done means a completed task carrying a deadline in this range; the task files store no closed timestamp.</div>
+          <div id="plan-chart" class="mt-3"></div>
+        </div></div>
+      </div>
+      <div class="col-12 col-lg-4">
+        <div class="card h-100"><div class="card-body">
+          <div class="label mb-2">Deadlines</div>
+          <div id="deadline-rail"></div>
+        </div></div>
+      </div>
+    </div>
+  </section>
+
   <!-- Project + refresh -->
   <div class="d-flex flex-wrap align-items-end gap-2 mb-4">
     <div>
@@ -129,7 +160,10 @@
   <div class="gd-panel gd-panel-lg">
     <div class="d-flex align-items-start justify-content-between gap-3 p-3 border-bottom">
       <h2 class="h6 mb-0" id="task-modal-title">Task</h2>
-      <button type="button" class="btn btn-sm btn-outline-secondary" id="task-modal-close">Close</button>
+      <div class="d-flex gap-2">
+        <button type="button" class="btn btn-sm btn-outline-secondary" id="task-modal-link">Copy link</button>
+        <button type="button" class="btn btn-sm btn-outline-secondary" id="task-modal-close">Close</button>
+      </div>
     </div>
     <div class="small text-muted px-3 pt-2 mono" id="task-modal-meta"></div>
     <div id="task-modal-body"></div>
@@ -162,12 +196,21 @@
     refreshBtn: document.getElementById('refresh-btn'),
     projectSelect: document.getElementById('project-select'),
     search: document.getElementById('board-search'),
+    planView: document.getElementById('plan-view'),
+    planTitle: document.getElementById('plan-title'),
+    planTotals: document.getElementById('plan-totals'),
+    planChart: document.getElementById('plan-chart'),
+    deadlineRail: document.getElementById('deadline-rail'),
     taskModal: document.getElementById('task-modal'),
     taskModalTitle: document.getElementById('task-modal-title'),
     taskModalMeta: document.getElementById('task-modal-meta'),
     taskModalBody: document.getElementById('task-modal-body'),
     taskModalClose: document.getElementById('task-modal-close'),
+    taskModalLink: document.getElementById('task-modal-link'),
   };
+  let planWindow = 'week';
+  try { planWindow = window.localStorage.getItem('planner-plan-window') || 'week'; } catch (e) { planWindow = 'week'; }
+  let modalTaskId = '';
 
   const JALALI_MONTHS = ['Farvardin', 'Ordibehesht', 'Khordad', 'Tir', 'Mordad', 'Shahrivar', 'Mehr', 'Aban', 'Azar', 'Dey', 'Bahman', 'Esfand'];
 
@@ -436,6 +479,7 @@
   }
 
   function openTaskModal(id, absPath) {
+    modalTaskId = id || '';
     const params = new URLSearchParams();
     const rel = relTaskPath(absPath);
     if (rel) params.set('path', rel);
@@ -479,6 +523,14 @@
     openTaskModal(row.dataset.id, row.dataset.path);
   });
   elements.taskModalClose.addEventListener('click', closeTaskModal);
+  elements.taskModalLink.addEventListener('click', function () {
+    if (!modalTaskId) return;
+    const url = window.location.origin + window.location.pathname + '?task=' + encodeURIComponent(modalTaskId);
+    navigator.clipboard.writeText(url).then(function () {
+      elements.taskModalLink.textContent = 'Copied';
+      setTimeout(function () { elements.taskModalLink.textContent = 'Copy link'; }, 1500);
+    }).catch(function () { elements.taskModalLink.textContent = 'Copy failed'; });
+  });
   elements.taskModal.addEventListener('click', function (event) {
     if (event.target === elements.taskModal) closeTaskModal();
   });
@@ -490,6 +542,124 @@
     if (lastData) render(lastData);
   });
 
+  // ---- Plan cockpit ----
+  const WINDOW_LABELS = { day: 'Today', week: 'This week', month: 'This month' };
+
+  function planUrl() {
+    const params = new URLSearchParams({ window: planWindow });
+    if (currentProject) params.set('project_root', currentProject);
+    return '/api/plan?' + params.toString();
+  }
+
+  async function fetchPlan() {
+    try {
+      const resp = await fetch(planUrl(), { cache: 'no-cache' });
+      if (!resp.ok) throw new Error('HTTP ' + resp.status);
+      renderPlan(await resp.json());
+    } catch (err) {
+      elements.planTitle.textContent = 'Plan unavailable';
+      elements.planTotals.textContent = '';
+    }
+  }
+
+  function laneChip(lane) {
+    const cls = { backlog: 'text-bg-secondary', 'in-progress': 'text-bg-info', qa: 'text-bg-warning', completed: 'text-bg-success' }[lane] || 'text-bg-secondary';
+    return '<span class="badge ' + cls + '">' + escapeHtml(lane || '?') + '</span>';
+  }
+
+  function planTaskRow(t) {
+    return '<div class="task-row" role="button" tabindex="0" data-id="' + escapeHtml(t.id || '') + '" data-path="' + escapeHtml(t.path || '') + '">' +
+      laneChip(t.lane) + ' <span class="id">' + escapeHtml(t.id || '') + '</span> — ' + escapeHtml(t.title || '') +
+      (t.estimate_hours != null ? ' <span class="text-muted">' + escapeHtml(t.estimate_hours) + 'h</span>' : '') + '</div>';
+  }
+
+  function renderPlanChart(trend) {
+    if (!trend || !trend.length) { elements.planChart.innerHTML = ''; return; }
+    const max = Math.max(1, ...trend.map(function (d) { return d.open + d.in_progress + d.done; }));
+    const width = 100 / trend.length;
+    const bars = trend.map(function (d, i) {
+      const total = d.open + d.in_progress + d.done;
+      const h = total === 0 ? 1 : Math.round((total / max) * 46);
+      const x = i * width;
+      let y = 50;
+      const parts = [];
+      [['var(--gd-accent)', d.open], ['var(--gd-info)', d.in_progress], ['var(--gd-success)', d.done]].forEach(function (seg) {
+        const segH = total === 0 ? 0 : Math.round((seg[1] / total) * h);
+        if (segH > 0) { y -= segH; parts.push('<rect x="' + x + '" y="' + y + '" width="' + (width * 0.62) + '" height="' + segH + '" fill="' + seg[0] + '"></rect>'); }
+      });
+      return parts.join('');
+    }).join('');
+    elements.planChart.innerHTML = '<svg viewBox="0 0 100 54" width="100%" height="64" role="img" aria-label="14-day load">' +
+      '<line x1="0" y1="50" x2="100" y2="50" stroke="var(--gd-border)" stroke-width="0.4"></line>' + bars + '</svg>' +
+      '<div class="d-flex justify-content-between small text-muted mt-1"><span>' + trend[0].date.slice(5) + '</span><span>open / in progress / done</span><span>' + trend[trend.length - 1].date.slice(5) + '</span></div>';
+  }
+
+  function renderDeadlineRail(alerts) {
+    const groups = [['Overdue', alerts.overdue || [], 'var(--gd-danger)'], ['Today', alerts.today || [], 'var(--gd-warning)'], ['Next 3 days', alerts.soon || [], 'var(--gd-info)']];
+    const total = groups.reduce(function (sum, g) { return sum + g[1].length; }, 0);
+    if (total === 0) { elements.deadlineRail.innerHTML = '<div class="small text-muted">No deadlines in range.</div>'; return; }
+    elements.deadlineRail.innerHTML = groups.map(function (g) {
+      if (!g[1].length) return '';
+      return '<div class="mb-2"><div class="small fw-semibold" style="color:' + g[2] + '">' + g[0] + ' · ' + g[1].length + '</div>' +
+        g[1].slice(0, 5).map(planTaskRow).join('') + '</div>';
+    }).join('');
+  }
+
+  function renderPlan(data) {
+    const days = data.days || [];
+    const first = days.length ? days[0].date : '';
+    const last = days.length ? days[days.length - 1].date : '';
+    elements.planTitle.textContent = WINDOW_LABELS[data.window] + (first ? ' · ' + first.slice(5) + ' → ' + last.slice(5) : '');
+    const t = data.totals || {};
+    elements.planTotals.textContent = 'open ' + (t.open || 0) + ' · in-progress ' + (t.in_progress || 0) + ' · done ' + (t.done || 0) + ' · ' + (t.estimate_hours || 0) + 'h / ' + (t.capacity_hours || 0) + 'h';
+
+    let html = '';
+    if (data.window === 'day') {
+      const bucket = days[0] || { tasks: [] };
+      const open = bucket.tasks.filter(function (t) { return t.lane !== 'completed'; });
+      const done = bucket.tasks.filter(function (t) { return t.lane === 'completed'; });
+      html = (open.length ? '<div class="label mb-1">To do · ' + open.length + '</div>' + open.map(planTaskRow).join('') : '') +
+        (done.length ? '<div class="label mt-2 mb-1">Done · ' + done.length + '</div>' + done.map(planTaskRow).join('') : '') ||
+        '<div class="small text-muted">Nothing scheduled for today.</div>';
+    } else if (data.window === 'week') {
+      const w = (data.weeks || [])[0] || { remaining_hours: 0, estimate_hours: 0, capacity_hours: 0 };
+      html = '<div class="d-flex justify-content-between small mb-2"><span class="text-muted">Capacity</span><span class="mono">' +
+        (w.estimate_hours || 0) + 'h of ' + (w.capacity_hours || 0) + 'h · ' + (w.remaining_hours || 0) + 'h left</span></div>' +
+        '<div class="progress mb-2" style="height:6px;background:var(--gd-raised)"><div class="progress-bar" style="width:' +
+        Math.min(100, Math.round(((w.estimate_hours || 0) / Math.max(1, w.capacity_hours || 1)) * 100)) + '%;background:var(--gd-accent)"></div></div>' +
+        days.map(function (d) {
+          return '<div class="d-flex justify-content-between border-bottom py-1 small"><span>' + d.date.slice(5) + '</span>' +
+            '<span class="mono text-muted">' + d.open + ' open · ' + d.in_progress + ' wip · ' + d.done + ' done · ' + (d.estimate_hours || 0) + 'h</span></div>';
+        }).join('');
+    } else {
+      html = (data.weeks || []).map(function (w) {
+        return '<div class="d-flex justify-content-between border-bottom py-1 small"><span class="mono">' + w.label + '</span>' +
+          '<span class="mono text-muted">' + w.open + ' open · ' + w.done + ' done · ' + (w.estimate_hours || 0) + 'h</span></div>';
+      }).join('');
+    }
+    elements.planView.innerHTML = html;
+    renderPlanChart(data.trend);
+    renderDeadlineRail(data.alerts || {});
+
+    const rowHandler = function (event) {
+      const row = event.target.closest('.task-row');
+      if (row) openTaskModal(row.dataset.id, row.dataset.path);
+    };
+    elements.planView.onclick = rowHandler;
+    elements.deadlineRail.onclick = rowHandler;
+  }
+
+  document.querySelectorAll('[data-window]').forEach(function (btn) {
+    btn.addEventListener('click', function () {
+      planWindow = btn.dataset.window;
+      try { window.localStorage.setItem('planner-plan-window', planWindow); } catch (e) { /* storage blocked */ }
+      document.querySelectorAll('[data-window]').forEach(function (b) {
+        b.className = 'btn btn-sm ' + (b.dataset.window === planWindow ? 'btn-primary' : 'btn-outline-secondary');
+      });
+      fetchPlan();
+    });
+  });
+
   elements.refreshBtn.addEventListener('click', function () {
     elements.refreshBtn.textContent = '…';
     fetchStatus().then(function () { elements.refreshBtn.textContent = 'Refresh'; });
@@ -498,6 +668,7 @@
   elements.projectSelect.addEventListener('change', function () {
     currentProject = elements.projectSelect.value;
     fetchStatus();
+    fetchPlan();
   });
 
   // ---- Auth ----
@@ -602,7 +773,14 @@
   })();
 
   fetchStatus();
+  fetchPlan();
   setInterval(fetchStatus, 30000);
+  setInterval(fetchPlan, 60000);
+  document.querySelectorAll('[data-window]').forEach(function (b) {
+    b.className = 'btn btn-sm ' + (b.dataset.window === planWindow ? 'btn-primary' : 'btn-outline-secondary');
+  });
+  const initialTask = new URLSearchParams(window.location.search).get('task');
+  if (initialTask) openTaskModal(initialTask);
 })();
 </script>
 <script src="/static/vendor/bootstrap.bundle.min.js"></script>
diff --git a/tests/test_planner_server.py b/tests/test_planner_server.py
index 20c6964..9c9a8a9 100644
--- a/tests/test_planner_server.py
+++ b/tests/test_planner_server.py
@@ -939,6 +939,94 @@ def test_session_cookie_is_secure_behind_https_proxy(auth_client):
     assert "Secure" in cookie
 
 
+def test_plan_payload_day_week_month(tmp_path):
+    from datetime import date
+
+    today = date.today().isoformat()
+    _write_task(tmp_path, "backlog", 21, "Undated work", estimate=2)
+    _write_task(tmp_path, "in-progress", 22, "Today work", estimate=1, deadline=today)
+    _write_task(tmp_path, "completed", 23, "Done today", deadline=today)
+
+    day = planner._plan_payload(str(tmp_path), "day")
+    assert day["window"] == "day"
+    assert len(day["days"]) == 1
+    assert len(day["trend"]) == 14
+    assert day["totals"]["in_progress"] >= 1
+    assert any(t["id"] == "022" for t in day["days"][0]["tasks"])
+
+    week = planner._plan_payload(str(tmp_path), "week")
+    assert len(week["days"]) == 7
+    assert len(week["weeks"]) == 1
+    assert week["weeks"][0]["capacity_hours"] > 0
+
+    month = planner._plan_payload(str(tmp_path), "month")
+    assert len(month["weeks"]) >= 4
+
+
+def test_plan_alerts_overdue_and_soon(tmp_path):
+    from datetime import date, timedelta
+
+    today = date.today()
+    _write_task(
+        tmp_path, "qa", 31, "Late", deadline=(today - timedelta(days=2)).isoformat()
+    )
+    _write_task(
+        tmp_path,
+        "backlog",
+        32,
+        "Soon",
+        deadline=(today + timedelta(days=2)).isoformat(),
+    )
+    payload = planner._plan_payload(str(tmp_path), "week")
+    assert [t["id"] for t in payload["alerts"]["overdue"]] == ["031"]
+    assert [t["id"] for t in payload["alerts"]["soon"]] == ["032"]
+
+
+def test_plan_week_sums_all_days(tmp_path):
+    from datetime import date, timedelta
+
+    today = date.today()
+    week_start = today - timedelta(days=today.weekday())
+    _write_task(tmp_path, "backlog", 41, "Mon", deadline=week_start.isoformat())
+    _write_task(
+        tmp_path, "qa", 42, "Thu", deadline=(week_start + timedelta(days=3)).isoformat()
+    )
+    week = planner._plan_payload(str(tmp_path), "week")
+    assert week["weeks"][0]["open"] == 2
+    assert week["weeks"][0]["estimate_hours"] == week["totals"]["estimate_hours"]
+
+
+def test_plan_month_includes_mid_month_dates(tmp_path):
+    from datetime import date
+
+    today = date.today()
+    mid = today.replace(day=min(15, 28))
+    _write_task(
+        tmp_path, "backlog", 43, "Mid month", estimate=3, deadline=mid.isoformat()
+    )
+    month = planner._plan_payload(str(tmp_path), "month")
+    assert month["totals"]["open"] >= 1
+    assert month["totals"]["estimate_hours"] >= 3
+    assert sum(w["open"] for w in month["weeks"]) == month["totals"]["open"]
+
+
+def test_api_plan_http_contract(auth_client):
+    assert auth_client.get("/api/plan").status_code == 401
+    auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
+    assert auth_client.get("/api/plan", params={"window": "year"}).status_code == 400
+
+
+def test_api_plan_relative_root_rejected(open_client):
+    resp = open_client.get("/api/plan", params={"project_root": "relative/path"})
+    assert resp.status_code == 400
+
+
+def test_plan_missing_dir_returns_empty_buckets(tmp_path):
+    payload = planner._plan_payload(str(tmp_path), "week")
+    assert payload["totals"]["estimate_hours"] == 0
+    assert len(payload["days"]) == 7
+
+
 def test_login_valid_credentials_returns_token(auth_client):
     resp = auth_client.post(
         "/api/login", json={"username": "admin", "password": "admin-pass"}
```
<!-- END_GIT_DIFF -->
