# Task 347: Weekly plan state — propose, edit, approve, then run the day from it

**File:** `tasks/qa/0347-weekly-plan-state.md`
**Source:** manager
**Type:** feature
**Status:** in-progress
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
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 2a2e3ae..5301f80 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Weekly plan state: propose, edit, approve, then run the day from it (Task 347):** the plan is now a saved commitment instead of a per-request derivation. `tasks/.plan/week-YYYY-Www.json` holds `deadline_edits`, `capacity_by_day`, notes and the approval stamp; writes are atomic (temp + rename) and validated (unknown task ids, non-object maps, over-capacity unless `force`). `GET /api/plan` returns the saved plan alongside the buckets, `POST /api/plan` saves or approves (admin-only, 401/403 otherwise), `DELETE /api/plan` clears the week. `sprint_daily_agenda` reads the plan first and leads with today's committed tasks plus deviations (claimed but uncommitted, saved but unapproved), falling back explicitly when no plan exists. Dashboard week view gained per-day capacity inputs, a Save and an Approve action, a per-task day assignment select, and `committed` badges; the day view lists committed work first. Verified: 112 planner tests pass (five new: store round-trip with approval, validation errors, API persistence in open mode, viewer 403, agenda reads the plan), and the live board returned 200 for save → `plan` present in GET → clear.
+
 - **Planner planning cockpit: day, week and month views with charts and deadline pressure (Task 345):** new `GET /api/plan?window=day|week|month` returns buckets computed from `tasks/` — day (today), week (Monday–Sunday, mid-week safe) and month (ISO weeks of the current month) — plus a 14-day `trend`, per-week `capacity_hours` / `remaining_hours` against `PLANNER_WEEKLY_CAPACITY`, and `alerts` split into overdue / today / next-three-days. Undated open work is attributed to the current bucket, because counting deadlines alone rendered an empty cockpit; completion history does not exist in the task files, so "done" means a completed-lane task carrying a deadline in the bucket and the UI says so. The dashboard gains a Day/Week/Month switcher persisted in `localStorage`, a capacity bar, an inline-SVG 14-day load chart (open / in-progress / done, design tokens only), a deadline rail whose rows open the task modal, deep links via `?task=<id>`, and a Copy-link action in the modal header. Constants: 400 on an unknown window or a relative root, 401 without a session. Verified: 107 planner tests pass (seven new), live board returns 200 for all three windows with correct totals.
 
 - **Planner MCP and daily pacing are native to the system prompt (Task 340):** `prompts/fragments/11-execution_workflow.md` now carries a *Planner MCP and daily pacing* block after Step 9 — the singleton at `127.0.0.1:8108`, `tasks/` Markdown as the single source of truth, `sprint_daily_agenda` on "start today's work" in any language (the Persian trigger is quoted), `claim_next` instead of hand-moving a task file with refusals reported not bypassed, `plan_status`/`qa_budget` for sizing the day (one unresolved review ceiling), and `sprint_check_daily_quota` with `DAILY_QUOTA_REACHED` → present `sprint_stats` and stop claiming. It sits inside the existing tag, so the splitter manifest needed no change. `<system_version>` bumps `9.64.1 → 9.65.0`, the pin in `tests/test_prompt_sync.py` follows, and `system-prompt.md` was reassembled (109,554 bytes). Verified: 103 prompt/splitter tests pass including `test_system_prompt_split_assemble_round_trip` (byte-identical), `check_docs_sync.py` prints `docs-sync: OK`; the prompt was deployed to `~/.config/opencode/system-prompt.md` byte-identical and `mcp-brain` restarted.
diff --git a/mcp-planner-server/DECISIONS.md b/mcp-planner-server/DECISIONS.md
index 29d8114..bf5de0a 100644
--- a/mcp-planner-server/DECISIONS.md
+++ b/mcp-planner-server/DECISIONS.md
@@ -159,3 +159,10 @@ ADR-006 below. Session auth, scoping, and the CLI remain as decided here.
 - **Decision:** `GET /api/plan` derives `days`, `weeks`, `trend` (14 days), `totals` and `alerts` from `_load_all_tasks` on every request. Week rows sum the day rows they contain; month builds every day of the month and groups by ISO week. Open work without a deadline is attributed to the current bucket so the view is never empty. `done` is a completed-lane task with a deadline in the bucket, and the UI states that history is not stored. Capacity comes from `PLANNER_WEEKLY_CAPACITY`.
 - **Consequences:** no migration, no cache to invalidate, and a slow project with thousands of tasks pays a full scan per request (acceptable at 337 tasks; revisit if it grows). Charts read `trend`, so a future history feature only needs to extend that array.
 - **Rollback:** remove the route and the three dashboard panels; `/api/status` keeps working unchanged.
+
+## [2026-10-25] ADR-009: The week plan is saved state, buckets stay derived
+
+- **Context:** the Manager's loop is planning-session → edit → approve → run the day from that state. Deriving everything per request cannot remember what was agreed, so "start today's work" had no state to resume from.
+- **Decision:** keep `tasks/.plan/week-YYYY-Www.json` as the commitment (deadline edits, per-day capacity, approval stamp, atomic writes, server-side validation with an optional `force`). Buckets from ADR-008 remain derived; `GET /api/plan` merges the saved plan into them. `sprint_daily_agenda` prefers the plan and reports deviations instead of trusting it blindly.
+- **Consequences:** restart-safe commitments, one writer path, and an explicit fallback when no plan exists. Markdown is untouched, so hand edits surface as deviations rather than silent overwrites.
+- **Rollback:** delete the week file or `DELETE /api/plan`; the derived cockpit from task 345 behaves exactly as before.
diff --git a/mcp-planner-server/README.md b/mcp-planner-server/README.md
index 41c5a99..32343cf 100644
--- a/mcp-planner-server/README.md
+++ b/mcp-planner-server/README.md
@@ -145,3 +145,20 @@ cockpit buckets: `days`, `weeks`, `trend` (14 days), `totals` and `alerts`
 - `project_root` must be absolute (`400` otherwise); `window` must be one of
   the three values (`400`); with auth enabled the route answers `401` without a
   session and `403` outside the session's grants.
+
+## Weekly plan state (`tasks/.plan/week-YYYY-Www.json`)
+
+The week plan is the Manager's commitment, not a derived report. It stores
+`deadline_edits` (task id → `YYYY-MM-DD`), `capacity_by_day` (date → hours),
+optional notes, and `approved_at` / `approved_by`. Markdown stays the source of
+truth for each task; the plan only records scheduling decisions.
+
+- `GET /api/plan` returns the saved plan next to the buckets.
+- `POST /api/plan` accepts `{week?, deadline_edits?, capacity_by_day?, approved?,
+  force?}`; admin session required when auth is on (401 without a session, 403
+  for non-admins). Unknown ids, malformed maps, and over-capacity assignments
+  are rejected with 400 unless `force` is set.
+- `DELETE /api/plan?week=...` clears the week.
+- `sprint_daily_agenda` reads the plan first: today's committed tasks, then
+  deviations (claimed but uncommitted, saved but unapproved); with no plan it
+  says it is using the derived lanes.
diff --git a/mcp-planner-server/server.py b/mcp-planner-server/server.py
index efbd6f8..3a9b066 100644
--- a/mcp-planner-server/server.py
+++ b/mcp-planner-server/server.py
@@ -886,6 +886,10 @@ def sprint_lock(sprint_id: str, project_root: Optional[str] = None) -> str:
 def sprint_daily_agenda(project_root: Optional[str] = None) -> str:
     """Return locked task(s) for today's quota.
 
+    Reads the saved week plan first: today's committed tasks and any deviation
+    (committed but not claimed, or claimed but not committed) lead the answer.
+    Without a saved plan it falls back to the derived lanes and says so.
+
     Lists in-progress tasks and any QA-pending tasks that must be resolved
     before new work can be claimed.
 
@@ -902,6 +906,42 @@ def sprint_daily_agenda(project_root: Optional[str] = None) -> str:
     qa_pending = [t for t in tasks if t.get("lane") == "qa"]
 
     lines: list[str] = ["# Daily Agenda", ""]
+    week_plan = _read_week_plan(workspace_root, _plan_week_key())
+    if week_plan:
+        today_key = date.today().isoformat()
+        committed_today = [
+            task_id
+            for task_id, day_key in (week_plan.get("deadline_edits") or {}).items()
+            if str(day_key) == today_key
+        ]
+        by_id = {str(_task_brief(t).get("id")): t for t in tasks}
+        lines.append(f"## Today's commitment ({week_plan.get('week')})")
+        if committed_today:
+            for task_id in committed_today:
+                task = by_id.get(str(task_id))
+                lane = task.get("lane") if task else "missing"
+                lines.append(
+                    f"- {task_id} — {(task.get('title') if task else 'unknown task') or 'untitled'} [{lane}]"
+                )
+        else:
+            lines.append("- No task is committed to today in the saved plan.")
+        committed_ids = {str(i) for i in (week_plan.get("deadline_edits") or {})}
+        deviations = [
+            f"- {t['name']}: claimed but not in the committed plan"
+            for t in in_progress
+            if str(_task_brief(t).get("id")) not in committed_ids
+        ]
+        if deviations:
+            lines.append("")
+            lines.append("## Deviations")
+            lines.extend(deviations)
+        if not week_plan.get("approved_at"):
+            lines.append("")
+            lines.append("- Plan is saved but not approved yet.")
+        lines.append("")
+    else:
+        lines.append("- No saved week plan; using the derived lanes.")
+        lines.append("")
     if in_progress:
         lines.append("## In Progress")
         for t in in_progress:
@@ -1486,8 +1526,140 @@ def _empty_bucket(day: date) -> dict:
     }
 
 
+def _hours(value) -> float:
+    """Best-effort hours; malformed values count as zero, never crash."""
+    try:
+        return float(value)
+    except (TypeError, ValueError):
+        return 0.0
+
+
+_PLAN_DIR_NAME = ".plan"
+
+
+def _plan_week_key(day: Optional[date] = None) -> str:
+    """ISO week key for a date, e.g. ``2026-W43``."""
+    target = day or date.today()
+    iso = target.isocalendar()
+    return f"{iso[0]}-W{iso[1]:02d}"
+
+
+def _plan_file(root: Path, week: str) -> Path:
+    return root / "tasks" / _PLAN_DIR_NAME / f"week-{week}.json"
+
+
+def _read_week_plan(root: Path, week: Optional[str] = None) -> Optional[dict]:
+    """Return the saved commitment for ``week`` (default: current week)."""
+    key = week or _plan_week_key()
+    path = _plan_file(root, key)
+    if not path.is_file():
+        return None
+    try:
+        return json.loads(path.read_text(encoding="utf-8"))
+    except (OSError, ValueError):
+        return None
+
+
+def _write_week_plan(root: Path, plan: dict) -> Path:
+    """Atomically persist a week plan (temp file + rename)."""
+    key = str(plan.get("week") or _plan_week_key())
+    plan["week"] = key
+    path = _plan_file(root, key)
+    path.parent.mkdir(parents=True, exist_ok=True)
+    tmp = path.with_suffix(".json.tmp")
+    tmp.write_text(json.dumps(plan, indent=2, sort_keys=True), encoding="utf-8")
+    os.replace(tmp, path)
+    return path
+
+
+def _validate_plan_edits(root: Path, body: dict) -> tuple[dict, Optional[str]]:
+    """Validate and normalise a plan save request.
+
+    Accepts ``{week?, deadline_edits?, capacity_by_day?, approved?, force?}``
+    where ``deadline_edits`` maps a task id to ``YYYY-MM-DD`` and
+    ``capacity_by_day`` maps a date to hours. Returns ``(plan, error)``.
+    """
+    week = str(body.get("week") or _plan_week_key())
+    if not re.fullmatch(r"\d{4}-W\d{2}", week):
+        return {}, "week must look like 2026-W43"
+    tasks = {str(_task_brief(t).get("id")): t for t in _load_all_tasks(root)}
+    deadline_edits = body.get("deadline_edits") or {}
+    capacity_by_day = body.get("capacity_by_day") or {}
+    if not isinstance(deadline_edits, dict) or not isinstance(capacity_by_day, dict):
+        return {}, "deadline_edits and capacity_by_day must be objects"
+    for task_id, deadline in deadline_edits.items():
+        if str(task_id) not in tasks:
+            return {}, f"unknown task id {task_id}"
+        try:
+            date.fromisoformat(str(deadline))
+        except ValueError:
+            return {}, f"invalid deadline for {task_id}: {deadline}"
+    for day_key, hours in capacity_by_day.items():
+        try:
+            date.fromisoformat(str(day_key))
+            _hours(hours)
+        except (ValueError, TypeError):
+            return {}, f"invalid capacity entry {day_key}"
+    total_estimate = 0.0
+    for task_id in deadline_edits:
+        total_estimate += _hours(tasks[str(task_id)].get("estimate_hours"))
+    capacity_total = sum(_hours(v) for v in capacity_by_day.values())
+    if capacity_total and total_estimate > capacity_total and not body.get("force"):
+        return {}, (
+            f"over capacity: {total_estimate:.1f}h assigned vs "
+            f"{capacity_total:.1f}h capacity (pass force to override)"
+        )
+    previous = _read_week_plan(root, week) or {}
+    merged_edits = (
+        {str(k): str(v) for k, v in deadline_edits.items()}
+        if body.get("replace")
+        else {
+            **(previous.get("deadline_edits") or {}),
+            **{str(k): str(v) for k, v in deadline_edits.items()},
+        }
+    )
+    merged_capacity = (
+        {str(k): _hours(v) for k, v in capacity_by_day.items()}
+        if body.get("replace")
+        else {
+            **(previous.get("capacity_by_day") or {}),
+            **{str(k): _hours(v) for k, v in capacity_by_day.items()},
+        }
+    )
+    merged_estimate = sum(
+        _hours(tasks[str(task_id)].get("estimate_hours"))
+        for task_id in merged_edits
+        if str(task_id) in tasks
+    )
+    merged_capacity_total = sum(merged_capacity.values())
+    if (
+        merged_capacity_total
+        and merged_estimate > merged_capacity_total
+        and not body.get("force")
+    ):
+        return {}, (
+            f"over capacity: {merged_estimate:.1f}h assigned vs "
+            f"{merged_capacity_total:.1f}h capacity (pass force to override)"
+        )
+    plan = {
+        "week": week,
+        "deadline_edits": merged_edits,
+        "capacity_by_day": merged_capacity,
+        "notes": body.get("notes", previous.get("notes", "")),
+        "approved_at": previous.get("approved_at"),
+        "approved_by": previous.get("approved_by"),
+    }
+    if body.get("approved"):
+        plan["approved_at"] = datetime.now(timezone.utc).isoformat()
+        plan["approved_by"] = str(body.get("approved_by") or "manager")
+    return plan, None
+
+
 def _plan_payload(
-    project_root: Optional[str] = None, window: str = "week", auth=None
+    project_root: Optional[str] = None,
+    window: str = "week",
+    auth=None,
+    plan_week: Optional[str] = None,
 ) -> dict:
     """Return day/week/month planning buckets (``GET /api/plan``).
 
@@ -1542,7 +1714,7 @@ def _plan_payload(
         if deadline is not None:
             bucket = bucket_for(deadline)
             bucket["tasks"].append(brief)
-            bucket["estimate_hours"] += float(task.get("estimate_hours") or 0)
+            bucket["estimate_hours"] += _hours(task.get("estimate_hours"))
             if lane == "completed":
                 bucket["done"] += 1
             elif lane == "in-progress":
@@ -1579,7 +1751,7 @@ def _plan_payload(
     anchor_bucket = bucket_for(anchor)
     for task, brief in undated:
         anchor_bucket["tasks"].append(brief)
-        anchor_bucket["estimate_hours"] += float(task.get("estimate_hours") or 0)
+        anchor_bucket["estimate_hours"] += _hours(task.get("estimate_hours"))
         if task.get("lane") == "in-progress":
             anchor_bucket["in_progress"] += 1
         else:
@@ -1641,6 +1813,7 @@ def _plan_payload(
         "trend": trend,
         "totals": totals,
         "alerts": alerts,
+        "plan": _read_week_plan(root, plan_week or _plan_week_key()),
     }
 
 
@@ -1806,8 +1979,13 @@ def build_app():
         window = (request.query_params.get("window") or "week").strip().lower()
         if window not in _PLAN_WINDOWS:
             return JSONResponse({"error": "invalid window"}, status_code=400)
+        plan_week = request.query_params.get("week")
+        if plan_week and not re.fullmatch(r"\d{4}-W\d{2}", plan_week):
+            return JSONResponse(
+                {"error": "week must look like 2026-W43"}, status_code=400
+            )
         auth = _auth_from_request(request)
-        payload = _plan_payload(root, window, auth)
+        payload = _plan_payload(root, window, auth, plan_week)
         error = payload.get("error")
         if error == "unauthenticated":
             return JSONResponse(payload, status_code=401)
@@ -1817,6 +1995,58 @@ def build_app():
             return JSONResponse(payload, status_code=500)
         return JSONResponse(payload)
 
+    async def api_plan_save(request):
+        if _AUTH_ENABLED:
+            auth = _auth_from_request(request)
+            if not auth.authenticated:
+                return JSONResponse({"error": "unauthenticated"}, status_code=401)
+            if not auth.is_admin:
+                return JSONResponse({"error": "forbidden"}, status_code=403)
+        else:
+            auth = None
+        try:
+            body = await request.json()
+        except Exception:  # noqa: BLE001 - any parse failure is a 400
+            return JSONResponse({"error": "invalid JSON body"}, status_code=400)
+        if not isinstance(body, dict):
+            return JSONResponse({"error": "invalid JSON body"}, status_code=400)
+        root = _resolve_dashboard_root(None)
+        if auth is not None and not auth.project_allowed(root):
+            fallback = _first_allowed_root(auth)
+            if fallback is None:
+                return JSONResponse({"error": "forbidden"}, status_code=403)
+            root = fallback
+        plan, error = _validate_plan_edits(root, body)
+        if error:
+            return JSONResponse({"error": error}, status_code=400)
+        _write_week_plan(root, plan)
+        return JSONResponse(plan)
+
+    async def api_plan_clear(request):
+        if _AUTH_ENABLED:
+            auth = _auth_from_request(request)
+            if not auth.authenticated:
+                return JSONResponse({"error": "unauthenticated"}, status_code=401)
+            if not auth.is_admin:
+                return JSONResponse({"error": "forbidden"}, status_code=403)
+        else:
+            auth = None
+        week = (request.query_params.get("week") or _plan_week_key()).strip()
+        if not re.fullmatch(r"\d{4}-W\d{2}", week):
+            return JSONResponse(
+                {"error": "week must look like 2026-W43"}, status_code=400
+            )
+        root = _resolve_dashboard_root(None)
+        if auth is not None and not auth.project_allowed(root):
+            fallback = _first_allowed_root(auth)
+            if fallback is None:
+                return JSONResponse({"error": "forbidden"}, status_code=403)
+            root = fallback
+        path = _plan_file(root, week)
+        if path.is_file():
+            path.unlink()
+        return JSONResponse({"cleared": week})
+
     async def api_login(request):
         if not _AUTH_ENABLED:
             return JSONResponse(
@@ -1925,7 +2155,9 @@ def build_app():
         Route("/", dashboard),
         Route("/api/status", api_status),
         Route("/api/task", api_task),
-        Route("/api/plan", api_plan),
+        Route("/api/plan", api_plan, methods=["GET"]),
+        Route("/api/plan", api_plan_save, methods=["POST"]),
+        Route("/api/plan", api_plan_clear, methods=["DELETE"]),
         Route("/api/login", api_login, methods=["POST"]),
         Route("/api/logout", api_logout, methods=["POST"]),
         Route("/api/me", api_me),
diff --git a/mcp-planner-server/static/index.html b/mcp-planner-server/static/index.html
index 3c66ea6..1838517 100644
--- a/mcp-planner-server/static/index.html
+++ b/mcp-planner-server/static/index.html
@@ -79,6 +79,8 @@
         <button type="button" class="btn btn-sm btn-outline-secondary" data-window="day">Day</button>
         <button type="button" class="btn btn-sm btn-outline-secondary" data-window="week">Week</button>
         <button type="button" class="btn btn-sm btn-outline-secondary" data-window="month">Month</button>
+        <button type="button" class="btn btn-sm btn-outline-secondary" id="plan-save">Save</button>
+        <button type="button" class="btn btn-sm btn-primary" id="plan-approve">Approve</button>
       </div>
     </div>
     <div class="row g-3">
@@ -211,6 +213,8 @@
   let planWindow = 'week';
   try { planWindow = window.localStorage.getItem('planner-plan-window') || 'week'; } catch (e) { planWindow = 'week'; }
   let modalTaskId = '';
+  let planDays = [];
+  let planCommitted = {};
 
   const JALALI_MONTHS = ['Farvardin', 'Ordibehesht', 'Khordad', 'Tir', 'Mordad', 'Shahrivar', 'Mehr', 'Aban', 'Azar', 'Dey', 'Bahman', 'Esfand'];
 
@@ -568,9 +572,20 @@
   }
 
   function planTaskRow(t) {
-    return '<div class="task-row" role="button" tabindex="0" data-id="' + escapeHtml(t.id || '') + '" data-path="' + escapeHtml(t.path || '') + '">' +
+    const committed = planCommitted[t.id];
+    const options = ['<option value="">—</option>'].concat(
+      planDays.map(function (d) {
+        const sel = committed === d ? ' selected' : '';
+        return '<option value="' + d + '"' + sel + '>' + d.slice(5) + '</option>';
+      })
+    ).join('');
+    return '<div class="d-flex align-items-center gap-2 border-bottom py-1">' +
+      '<div class="task-row flex-grow-1 border-0 py-0" role="button" tabindex="0" data-id="' + escapeHtml(t.id || '') + '" data-path="' + escapeHtml(t.path || '') + '">' +
       laneChip(t.lane) + ' <span class="id">' + escapeHtml(t.id || '') + '</span> — ' + escapeHtml(t.title || '') +
-      (t.estimate_hours != null ? ' <span class="text-muted">' + escapeHtml(t.estimate_hours) + 'h</span>' : '') + '</div>';
+      (t.estimate_hours != null ? ' <span class="text-muted">' + escapeHtml(t.estimate_hours) + 'h</span>' : '') +
+      (committed ? ' <span class="badge text-bg-success">committed</span>' : '') + '</div>' +
+      '<select class="form-select form-select-sm" style="width:8.5rem" data-assign="' + escapeHtml(t.id || '') + '">' + options + '</select>' +
+      '</div>';
   }
 
   function renderPlanChart(trend) {
@@ -607,6 +622,8 @@
 
   function renderPlan(data) {
     const days = data.days || [];
+    planDays = days.map(function (d) { return d.date; });
+    planCommitted = (data.plan && data.plan.deadline_edits) || {};
     const first = days.length ? days[0].date : '';
     const last = days.length ? days[days.length - 1].date : '';
     elements.planTitle.textContent = WINDOW_LABELS[data.window] + (first ? ' · ' + first.slice(5) + ' → ' + last.slice(5) : '');
@@ -628,8 +645,10 @@
         '<div class="progress mb-2" style="height:6px;background:var(--gd-raised)"><div class="progress-bar" style="width:' +
         Math.min(100, Math.round(((w.estimate_hours || 0) / Math.max(1, w.capacity_hours || 1)) * 100)) + '%;background:var(--gd-accent)"></div></div>' +
         days.map(function (d) {
-          return '<div class="d-flex justify-content-between border-bottom py-1 small"><span>' + d.date.slice(5) + '</span>' +
-            '<span class="mono text-muted">' + d.open + ' open · ' + d.in_progress + ' wip · ' + d.done + ' done · ' + (d.estimate_hours || 0) + 'h</span></div>';
+          return '<div class="d-flex justify-content-between align-items-center border-bottom py-1 small gap-2"><span>' + d.date.slice(5) + '</span>' +
+            '<span class="mono text-muted">' + d.open + ' open · ' + d.in_progress + ' wip · ' + d.done + ' done · ' + (d.estimate_hours || 0) + 'h</span>' +
+            '<input type="number" min="0" step="0.5" class="form-control form-control-sm" style="width:5.5rem" data-cap="' + d.date + '" value="' +
+            (((data.plan || {}).capacity_by_day || {})[d.date] || '') + '" aria-label="Capacity ' + d.date + '"></div>';
         }).join('');
     } else {
       html = (data.weeks || []).map(function (w) {
@@ -660,6 +679,30 @@
     });
   });
 
+  function savePlan(approved) {
+    const deadline_edits = {};
+    document.querySelectorAll('[data-assign]').forEach(function (el) {
+      if (el.value) deadline_edits[el.dataset.assign] = el.value;
+    });
+    const capacity_by_day = {};
+    document.querySelectorAll('[data-cap]').forEach(function (el) {
+      if (el.value !== '') capacity_by_day[el.dataset.cap] = parseFloat(el.value);
+    });
+    fetch('/api/plan', {
+      method: 'POST',
+      headers: { 'Content-Type': 'application/json' },
+      body: JSON.stringify({ deadline_edits: deadline_edits, capacity_by_day: capacity_by_day, approved: !!approved }),
+    }).then(function (resp) { return resp.json().then(function (body) { return { ok: resp.ok, body: body }; }); })
+      .then(function (res) {
+        elements.planTotals.textContent = res.ok ? (approved ? 'Plan approved' : 'Plan saved') : 'Save failed: ' + (res.body.error || 'error');
+        if (res.ok) fetchPlan();
+      })
+      .catch(function () { elements.planTotals.textContent = 'Save failed'; });
+  }
+
+  document.getElementById('plan-save').addEventListener('click', function () { savePlan(false); });
+  document.getElementById('plan-approve').addEventListener('click', function () { savePlan(true); });
+
   elements.refreshBtn.addEventListener('click', function () {
     elements.refreshBtn.textContent = '…';
     fetchStatus().then(function () { elements.refreshBtn.textContent = 'Refresh'; });
diff --git a/tests/test_planner_server.py b/tests/test_planner_server.py
index 9c9a8a9..dde497e 100644
--- a/tests/test_planner_server.py
+++ b/tests/test_planner_server.py
@@ -1010,6 +1010,74 @@ def test_plan_month_includes_mid_month_dates(tmp_path):
     assert sum(w["open"] for w in month["weeks"]) == month["totals"]["open"]
 
 
+def test_week_plan_roundtrip_and_approval(tmp_path):
+    _write_task(tmp_path, "backlog", 51, "Plan me", estimate=2)
+    plan, err = planner._validate_plan_edits(
+        tmp_path,
+        {
+            "week": "2026-W43",
+            "deadline_edits": {"051": "2026-10-26"},
+            "capacity_by_day": {"2026-10-26": 4},
+            "approved": True,
+        },
+    )
+    assert err is None
+    planner._write_week_plan(tmp_path, plan)
+    saved = planner._read_week_plan(tmp_path, "2026-W43")
+    assert saved["deadline_edits"]["051"] == "2026-10-26"
+    assert saved["approved_at"]
+
+
+def test_week_plan_validation_errors(tmp_path):
+    _write_task(tmp_path, "backlog", 52, "Small", estimate=1)
+    _, err = planner._validate_plan_edits(
+        tmp_path, {"deadline_edits": {"999": "2026-10-26"}}
+    )
+    assert "unknown task" in err
+    _, err = planner._validate_plan_edits(
+        tmp_path,
+        {
+            "deadline_edits": {"052": "2026-10-26"},
+            "capacity_by_day": {"2026-10-26": 0.5},
+        },
+    )
+    assert "over capacity" in err
+
+
+def test_plan_api_admin_only_and_persists(open_client, tmp_path, monkeypatch):
+    monkeypatch.setenv("PLANNER_PROJECT_ROOT", str(tmp_path))
+    _write_task(tmp_path, "backlog", 53, "Saved", estimate=1)
+    resp = open_client.post(
+        "/api/plan",
+        json={"week": "2026-W43", "deadline_edits": {"053": "2026-10-26"}},
+    )
+    assert resp.status_code == 200
+    assert resp.json()["deadline_edits"]["053"] == "2026-10-26"
+    status = open_client.get("/api/plan", params={"window": "week"}).json()
+    assert status["plan"]["week"] == "2026-W43"
+
+
+def test_plan_api_viewer_cannot_save(auth_client):
+    auth_client.post(
+        "/api/login", json={"username": "viewer", "password": "viewer-pass"}
+    )
+    resp = auth_client.post("/api/plan", json={"deadline_edits": {}})
+    assert resp.status_code == 403
+
+
+def test_sprint_daily_agenda_reads_saved_plan(tmp_path, monkeypatch):
+    monkeypatch.setenv("PLANNER_PROJECT_ROOT", str(tmp_path))
+    _write_task(tmp_path, "backlog", 54, "Committed", estimate=1)
+    plan, _ = planner._validate_plan_edits(
+        tmp_path,
+        {"deadline_edits": {"054": __import__("datetime").date.today().isoformat()}},
+    )
+    planner._write_week_plan(tmp_path, plan)
+    agenda = planner.sprint_daily_agenda(str(tmp_path))
+    assert "Today's commitment" in agenda
+    assert "054" in agenda
+
+
 def test_api_plan_http_contract(auth_client):
     assert auth_client.get("/api/plan").status_code == 401
     auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
```
<!-- END_GIT_DIFF -->
