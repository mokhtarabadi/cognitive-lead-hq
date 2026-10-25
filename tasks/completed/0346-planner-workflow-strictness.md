# Task 346: Planner workflow strictness — ownership, nudges, overdue pressure

**File:** `tasks/qa/0346-planner-workflow-strictness.md`
**Source:** manager
**Type:** feature
**Status:** in-progress
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
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 5301f80..51d71d4 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Ownership, Mine filter and pressure signals (Task 346):** task files may carry `**Owner:**`; `_parse_task_file` reads it and `_task_brief` exposes `owner`, so the dashboard shows an owner badge and a **Mine only** toggle filters lanes to the signed-in username in the browser. `sprint_daily_agenda` emits `NUDGE` when nothing is claimed while the backlog is non-empty and lists `OVERDUE` ids, and `claim_next` appends the same overdue warning (never blocking). README documents the field and states that hand-moving files around `claim_next` bypasses the gates. Verified: 115 planner tests (three new: owner parse/brief, agenda nudge, claim_next overdue), suite exit 0.
+
 - **Weekly plan state: propose, edit, approve, then run the day from it (Task 347):** the plan is now a saved commitment instead of a per-request derivation. `tasks/.plan/week-YYYY-Www.json` holds `deadline_edits`, `capacity_by_day`, notes and the approval stamp; writes are atomic (temp + rename) and validated (unknown task ids, non-object maps, over-capacity unless `force`). `GET /api/plan` returns the saved plan alongside the buckets, `POST /api/plan` saves or approves (admin-only, 401/403 otherwise), `DELETE /api/plan` clears the week. `sprint_daily_agenda` reads the plan first and leads with today's committed tasks plus deviations (claimed but uncommitted, saved but unapproved), falling back explicitly when no plan exists. Dashboard week view gained per-day capacity inputs, a Save and an Approve action, a per-task day assignment select, and `committed` badges; the day view lists committed work first. Verified: 112 planner tests pass (five new: store round-trip with approval, validation errors, API persistence in open mode, viewer 403, agenda reads the plan), and the live board returned 200 for save → `plan` present in GET → clear.
 
 - **Planner planning cockpit: day, week and month views with charts and deadline pressure (Task 345):** new `GET /api/plan?window=day|week|month` returns buckets computed from `tasks/` — day (today), week (Monday–Sunday, mid-week safe) and month (ISO weeks of the current month) — plus a 14-day `trend`, per-week `capacity_hours` / `remaining_hours` against `PLANNER_WEEKLY_CAPACITY`, and `alerts` split into overdue / today / next-three-days. Undated open work is attributed to the current bucket, because counting deadlines alone rendered an empty cockpit; completion history does not exist in the task files, so "done" means a completed-lane task carrying a deadline in the bucket and the UI says so. The dashboard gains a Day/Week/Month switcher persisted in `localStorage`, a capacity bar, an inline-SVG 14-day load chart (open / in-progress / done, design tokens only), a deadline rail whose rows open the task modal, deep links via `?task=<id>`, and a Copy-link action in the modal header. Constants: 400 on an unknown window or a relative root, 401 without a session. Verified: 107 planner tests pass (seven new), live board returns 200 for all three windows with correct totals.
diff --git a/mcp-planner-server/README.md b/mcp-planner-server/README.md
index 32343cf..ce9da70 100644
--- a/mcp-planner-server/README.md
+++ b/mcp-planner-server/README.md
@@ -162,3 +162,13 @@ truth for each task; the plan only records scheduling decisions.
 - `sprint_daily_agenda` reads the plan first: today's committed tasks, then
   deviations (claimed but uncommitted, saved but unapproved); with no plan it
   says it is using the derived lanes.
+
+### Ownership and pressure signals
+
+A task file may carry `**Owner:** <username>`; briefs expose it and the
+dashboard renders it as a badge, with a **Mine only** toggle that filters lanes
+to the signed-in username (client-side, no round-trip). `sprint_daily_agenda`
+now emits `NUDGE` when nothing is claimed while the backlog is non-empty, and
+`OVERDUE` with the oldest ids; `claim_next` appends the same `OVERDUE` warning
+to a successful claim without ever blocking it. Hand-moving a task file around
+`claim_next` bypasses all of these gates and is a workflow violation.
diff --git a/mcp-planner-server/server.py b/mcp-planner-server/server.py
index 3a9b066..1fe45ae 100644
--- a/mcp-planner-server/server.py
+++ b/mcp-planner-server/server.py
@@ -183,6 +183,8 @@ def _parse_task_file(path: Path) -> dict:
             record["type"] = val
         elif key == "status":
             record["status"] = val
+        elif key == "owner":
+            record["owner"] = val
         elif key == "estimate":
             em = re.match(r"(\d+(?:\.\d+)?)\s*h", val, re.IGNORECASE)
             if em:
@@ -626,9 +628,26 @@ def claim_next(project_root: str, task_id: str) -> str:
     except OSError:
         pass  # Header update is best-effort; the move itself succeeded.
 
+    overdue = []
+    for candidate in _load_all_tasks(workspace_root):
+        if candidate.get("lane") not in ("backlog", "in-progress", "qa"):
+            continue
+        raw = candidate.get("deadline")
+        if not raw:
+            continue
+        try:
+            if date.fromisoformat(str(raw)) < date.today():
+                overdue.append(str(_task_brief(candidate).get("id")))
+        except ValueError:
+            continue
+    warning = (
+        f" ⚠️ OVERDUE: {', '.join(overdue[:3])}" + (" …" if len(overdue) > 3 else "")
+        if overdue
+        else ""
+    )
     return (
         f"✅ claim_next succeeded: task {task_id} ('{task.get('title')}') "
-        f"moved to tasks/in-progress/. Status: in-progress."
+        f"moved to tasks/in-progress/. Status: in-progress.{warning}"
     )
 
 
@@ -953,7 +972,28 @@ def sprint_daily_agenda(project_root: Optional[str] = None) -> str:
             lines.append(f"- {t['name']} — {t.get('title') or 'untitled'}")
         lines.append("")
     if not in_progress and not qa_pending:
-        lines.append("- Nothing in progress or awaiting QA. Ready to claim next task.")
+        backlog = [t for t in tasks if t.get("lane") == "backlog"]
+        if backlog:
+            lines.append(
+                f"- NUDGE: nothing is claimed and {len(backlog)} task(s) wait in backlog. "
+                f"Top: {backlog[0]['name']} — {backlog[0].get('title') or 'untitled'}."
+            )
+        overdue_ids = []
+        for task in tasks:
+            raw = task.get("deadline")
+            if not raw or task.get("lane") not in ("backlog", "in-progress", "qa"):
+                continue
+            try:
+                if date.fromisoformat(str(raw)) < date.today():
+                    overdue_ids.append(str(_task_brief(task).get("id")))
+            except ValueError:
+                continue
+        if overdue_ids:
+            lines.append(f"- OVERDUE: {', '.join(overdue_ids[:5])}")
+        if not backlog and not overdue_ids:
+            lines.append(
+                "- Nothing in progress or awaiting QA. Ready to claim next task."
+            )
     return "\n".join(lines)
 
 
@@ -1386,6 +1426,7 @@ def _task_brief(task: dict) -> dict:
         "lane": task.get("lane"),
         "status": task.get("status") or "open",
         "estimate_hours": task.get("estimate_hours"),
+        "owner": task.get("owner"),
         "deadline": task.get("deadline"),
         "milestone": task.get("milestone"),
     }
diff --git a/mcp-planner-server/static/index.html b/mcp-planner-server/static/index.html
index 1838517..4eb474a 100644
--- a/mcp-planner-server/static/index.html
+++ b/mcp-planner-server/static/index.html
@@ -119,6 +119,7 @@
       <span class="label mb-0">Kanban lanes</span>
     </div>
     <input type="search" id="board-search" class="form-control form-control-sm mb-3" placeholder="Filter tasks by ID or title…" autocomplete="off" aria-label="Filter tasks">
+    <div class="d-flex justify-content-end mb-2"><button type="button" class="btn btn-sm btn-outline-secondary" id="mine-toggle" aria-pressed="false">Mine only</button></div>
     <div class="row g-3" id="lanes-grid"></div>
   </section>
 
@@ -215,6 +216,8 @@
   let modalTaskId = '';
   let planDays = [];
   let planCommitted = {};
+  let mineOnly = false;
+  let currentUser = '';
 
   const JALALI_MONTHS = ['Farvardin', 'Ordibehesht', 'Khordad', 'Tir', 'Mordad', 'Shahrivar', 'Mehr', 'Aban', 'Azar', 'Dey', 'Bahman', 'Esfand'];
 
@@ -310,7 +313,8 @@
     const needle = query.trim().toLowerCase();
     laneOrder.forEach(function (lane) {
       const all = lanes[lane] || [];
-      const items = needle ? all.filter(function (t) { return taskMatches(t, needle); }) : all;
+      const scoped = mineOnly && currentUser ? all.filter(function (t) { return t.owner === currentUser; }) : all;
+      const items = needle ? scoped.filter(function (t) { return taskMatches(t, needle); }) : scoped;
       const isArchive = lane === 'archive';
       const collapsed = isArchive && !archiveOpen;
       const chipClass = { backlog: 'text-bg-secondary', 'in-progress': 'text-bg-info', qa: 'text-bg-warning', completed: 'text-bg-success', archive: 'text-bg-secondary' }[lane];
@@ -321,6 +325,7 @@
         : items.map(function (t) {
           return '<div class="task-row" role="button" tabindex="0" data-id="' + escapeHtml(t.id || t.name || '') + '" data-path="' + escapeHtml(t.path || '') + '">' +
             '<span class="id">' + escapeHtml(t.id || t.name || 'task') + '</span> — ' + escapeHtml(t.title || 'untitled') +
+            (t.owner ? ' <span class="badge text-bg-secondary">' + escapeHtml(t.owner) + '</span>' : '') +
             (t.estimate_hours != null ? ' <span class="text-muted">' + t.estimate_hours + 'h</span>' : '') +
             '</div>';
         }).join('');
@@ -546,6 +551,16 @@
     if (lastData) render(lastData);
   });
 
+  const mineToggle = document.getElementById('mine-toggle');
+  if (mineToggle) {
+    mineToggle.addEventListener('click', function () {
+      mineOnly = !mineOnly;
+      mineToggle.setAttribute('aria-pressed', mineOnly ? 'true' : 'false');
+      mineToggle.className = 'btn btn-sm ' + (mineOnly ? 'btn-primary' : 'btn-outline-secondary');
+      if (lastData) render(lastData);
+    });
+  }
+
   // ---- Plan cockpit ----
   const WINDOW_LABELS = { day: 'Today', week: 'This week', month: 'This month' };
 
@@ -739,6 +754,7 @@
   function hideLoginModal() { auth.modal.classList.add('hidden'); }
 
   function showUserBadge(username, role) {
+    currentUser = username || '';
     auth.userBadge.classList.remove('d-none');
     auth.userBadge.classList.add('d-flex');
     auth.logoutBtn.classList.remove('d-none');
diff --git a/tests/test_planner_server.py b/tests/test_planner_server.py
index dde497e..5422637 100644
--- a/tests/test_planner_server.py
+++ b/tests/test_planner_server.py
@@ -1078,6 +1078,34 @@ def test_sprint_daily_agenda_reads_saved_plan(tmp_path, monkeypatch):
     assert "054" in agenda
 
 
+def test_owner_field_parsed_and_briefed(tmp_path):
+    _write_task(tmp_path, "backlog", 61, "Owned work")
+    path = next((tmp_path / "tasks" / "backlog").glob("061-*.md"))
+    path.write_text(
+        path.read_text().replace(
+            "**Status:** open", "**Status:** open\n**Owner:** ehsan"
+        ),
+        encoding="utf-8",
+    )
+    brief = planner._task_brief(planner._parse_task_file(path))
+    assert brief["owner"] == "ehsan"
+
+
+def test_agenda_nudges_when_backlog_waiting(tmp_path, monkeypatch):
+    monkeypatch.setenv("PLANNER_PROJECT_ROOT", str(tmp_path))
+    _write_task(tmp_path, "backlog", 62, "Waiting")
+    agenda = planner.sprint_daily_agenda(str(tmp_path))
+    assert "NUDGE" in agenda
+
+
+def test_claim_next_reports_overdue(tmp_path):
+    _write_task(tmp_path, "backlog", 63, "Late", deadline="2020-01-01")
+    _write_task(tmp_path, "backlog", 64, "Next")
+    result = planner.claim_next(str(tmp_path), "64")
+    assert "claim_next succeeded" in result
+    assert "OVERDUE" in result and "063" in result
+
+
 def test_api_plan_http_contract(auth_client):
     assert auth_client.get("/api/plan").status_code == 401
     auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
```
<!-- END_GIT_DIFF -->
