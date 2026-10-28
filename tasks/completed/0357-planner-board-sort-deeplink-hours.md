# Task 0357: Planner board — numeric sort, deep-link fix, daily/weekly hours chart

**File:** `tasks/qa/0357-planner-board-sort-deeplink-hours.md`
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
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 8a81ac7..69ef142 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Planner board numeric sort, hardened deep links, measured-hours chart (Task 0357):** lane files sorted lexically while filenames mix widths, so `0356` rendered before `283`. One numeric sort key (leading filename integer, lexical fallback) now orders lanes, milestone groups, plan buckets and alert rails lowest-number-first. The `?task=` modal fired on page load with no project root and no session, dying as "Error 401"; it now waits for the first successful status, carries `project_root`, and retries once automatically after login. `fetchStatus` read `resp.json()` unguarded, so an edge HTML login page served with 200 crashed the status line with a raw `Unexpected token '<'` dump; it now sniffs non-JSON bodies and names the cause. New read-only `GET /api/hours` aggregates `elapsed_seconds` by finish date into 14 daily plus 8 weekly rows (measured-only, unstamped tasks skipped), rendered as an SVG block reusing the plan-chart pattern. Verified: 3 new tests (mixed-width lane/milestone sort, hours math), planner suite 122 green, inline JS syntax clean. Docs: planner README route table + ordering note, ADR-012.
+
 - **Runtime-neutral sweep: Claude-centric wording and phantom tool names removed (Task 0356):** a four-way read-only sweep found one skill (`doc-coauthoring`, 22 Claude hits plus `create_file`/`str_replace`/Artifacts/connectors/`claude.ai` reader testing), four phantom tool names in prompt fragments (`nodejs-express`, `@explore`/`@general`, `view_file`/`apply_patch`), one wrong delegation noun in the executor (`task` tool), four vendor-first lines in setup docs, and one vendor-trio comment plus a non-catalog `["question"]` docstring example in the Brain Bridge. All remapped to OpenCode-native tools (`write`/`edit`, `subagent`/`cognitive-discovery`, `node-hexagonal-api`, native `read`, `default.question`); the shipped prompt was rebuilt (`9.67.0` → `9.68.0`) and verified phantom-free. Two new regression tests (shipped-prompt catalog names, doc-coauthoring runtime neutrality) prove teeth against the prior text. 31 other skills verified clean; history archives untouched; generic Maven/report `artifact` usage untouched.
 
 - **Graph coverage honesty, round-trippable IDs and inline signatures (Task 0355):** a smoke test found the lite graph indexing 345 of 587 files silently, and the missing set included the newest task files because docs were ordered `(depth, path)` and cut at 300. The graph now orders task docs lane-first and newest-id-first, defaults to 600 files / 600 docs / 12000 nodes, accepts `include`/`exclude` globs plus `max_files`/`max_docs`/`max_nodes` overrides, and stores coverage metadata (scanned, indexed, caps, truncation flags, indexed source list) in the graph envelope. `graph_stats` and `query_graph` print a coverage line, including `truncated: …` ("absence here is not proof of absence") and a `STALE` verdict naming the first source modified after the build. `explain_node` and `shortest_path` resolve the `sym:path#name`, `sec:path#slug` and `file:path` IDs the graph prints. Seed ranking weights symbols above files above sections with an exact-label bonus; `god_nodes` uses confidence-weighted degree, qualifies each label with its file and drops generic identifiers. `extract_signatures` accepts a directory (`.gitignore`-aware, 200-file cap), returns the signature text inline alongside the report path (capped by `max_chars`), and reports Markdown/HTML as unsupported instead of an empty success. `get_directory_tree` and `create_tree_report` expose `max_depth` (default 3) and `max_entries`. The `code-search` skill (repo template plus global copy) is rewritten around the graph-first flow with a tool-choice table and the real tool contracts. On this repo the rebuild indexes 49/49 code files and 522/522 docs in 3.3s (7,582 nodes, 11,720 edges); seven new tests cover recency, coverage reporting, ID round-trip, ranking, staleness, inline/directory signatures and the depth bound.
diff --git a/mcp-planner-server/DECISIONS.md b/mcp-planner-server/DECISIONS.md
index 17311b3..36a2a3e 100644
--- a/mcp-planner-server/DECISIONS.md
+++ b/mcp-planner-server/DECISIONS.md
@@ -180,3 +180,10 @@ not initialized`.
 - **Decision:** three ISO-8601 UTC stamps written by the transitions themselves: `Started` in `claim_next`, `Submitted` in `qa_transition`, `Finished` in `commit_and_clean_task`. All are write-once — the first start is the measured work — and `_task_brief` derives `elapsed_seconds` and `qa_wait_seconds`, `null` when a stamp is missing so the UI never shows a fake zero. `sprint_stats` keeps estimates and adds a separate measured line, and `_check_planner_metadata` rejects a non-UTC stamp or a finish before the start.
 - **Consequences:** the duration is measured, not guessed, and the estimate stays visible next to it so drift is obvious. The stamps live in the task header, so they travel with the file through every lane move and need no sidecar. A handwriting of the fields is impossible to corrupt silently: the lint fails.
 - **Rollback:** remove the three stamps, the brief fields and the lint checks; estimates-only behaviour returns and the extra lines are inert.
+
+## [2026-10-28] ADR-012: Numeric lane order, hardened deep links, measured-hours endpoint
+
+- **Context:** three board defects shared one root theme — the UI trusted transport details it never verified. Lane files sorted lexically while filenames mix widths, so `0356` rendered before `283`. The `?task=` modal fired on page load with no `project_root` and no session, dying as "Error 401" with no recovery; and `fetchStatus` called `resp.json()` unguarded, so an edge HTML login page served with 200 for `/api/*` crashed the status line with a raw `Unexpected token '<'` dump. Measured time existed per task but had no daily/weekly view.
+- **Decision:** one numeric sort key (leading filename integer, lexical fallback) applied to lanes, milestone groups, plan buckets and alert rails; the deep-link modal waits for the first successful status, carries `project_root`, and retries once automatically after login on 401; `fetchStatus` sniffs non-JSON bodies and names the edge-login/ingress cause instead of dumping the token; new read-only `GET /api/hours` aggregates `elapsed_seconds` by finish date into 14 daily plus 8 weekly rows (measured-only, unstamped tasks skipped), rendered as an SVG block reusing the plan-chart pattern.
+- **Consequences:** board order is numeric everywhere; deep links survive a cold open; the status line diagnoses instead of dumping. Hours are derived per request like the plan buckets — no second store.
+- **Rollback:** revert `server.py` + `static/index.html`; the board returns to lexical order, immediate modal, and no hours block.
diff --git a/mcp-planner-server/README.md b/mcp-planner-server/README.md
index 9dc804d..324a7ca 100644
--- a/mcp-planner-server/README.md
+++ b/mcp-planner-server/README.md
@@ -30,6 +30,7 @@ dashboard on loopback port 8108.
 | `GET /static/*`                                           | Dashboard assets (same `static/` directory).                                                                                                                                                              |
 | `GET /api/status[?project_root=<abs path>]`               | JSON status contract the dashboard renders.                                                                                                                                                               |
 | `GET /api/task?id=<id>` or `?path=tasks/<lane>/<file>.md` | One task file as `{id, path, lane, title, markdown}` for the dashboard modal. `id` wins when both are sent. 400 no param, 401 no session, 403 outside grants or unsafe path, 404 unknown, 500 unexpected. |
+| `GET /api/hours[?project_root=<abs path>]` | Measured hours from task stamps: per-day rows for the last 14 days plus per-week rows for the last 8 ISO weeks (`{date/week, measured_hours, done}`). Measured-only: tasks without `Finished` + `elapsed_seconds` never count. Same 401/403 contract as `/api/status`. |
 | `POST /api/login`                                         | `{"username","password"}` → `{token, username, role, allowed_projects}` + `HttpOnly` cookie.                                                                                                              |
 | `POST /api/logout`                                        | Invalidates the session and clears the cookie.                                                                                                                                                            |
 | `GET /api/me`                                             | Current user, or 401 when signed out (200 + `note: "auth disabled"` in open mode).                                                                                                                        |
@@ -40,7 +41,10 @@ dashboard on loopback port 8108.
 (`today` = `done`/`target`/`open`, mirroring `sprint_check_daily_quota`), the
 selectable project roots (`projects`), and the root actually reported on
 (`project_root`). Lane values are lists, never counts — the dashboard calls
-`.map()` on them.
+`.map()` on them. Every rendered list (lanes, milestone groups, plan buckets,
+alert rails) is ordered lowest task number first by the leading filename
+integer, so mixed widths (`283-*.md` vs `0356-*.md`) still sort numerically;
+names without a numeric prefix sort last, lexically.
 
 Project resolution order: the `project_root` query parameter, then
 `PLANNER_PROJECT_ROOT`, then the nearest ancestor of the working directory
diff --git a/mcp-planner-server/server.py b/mcp-planner-server/server.py
index d9b0c02..9d0cc80 100644
--- a/mcp-planner-server/server.py
+++ b/mcp-planner-server/server.py
@@ -315,6 +315,23 @@ def _parse_task_file(path: Path) -> dict:
     return record
 
 
+def _task_sort_key(name: str) -> tuple:
+    """Sort key ordering tasks lowest-number-first regardless of name width.
+
+    Filenames mix widths (``283-x.md`` vs ``0356-y.md``), so a plain lexical
+    sort puts "0356" before "283". The leading integer decides; names without
+    a numeric prefix sort after numbered ones, lexically.
+    """
+    text = name or ""
+    match = re.match(r"(\d+)", text.strip())
+    if match:
+        try:
+            return (0, int(match.group(1)), text)
+        except ValueError:  # noqa: BLE001 - fall through to lexical
+            pass
+    return (1, text)
+
+
 def _load_all_tasks(workspace_root: Path) -> list[dict]:
     """Load every task file across all Kanban lanes.
 
@@ -330,7 +347,7 @@ def _load_all_tasks(workspace_root: Path) -> list[dict]:
         lane_dir = tasks_dir / lane
         if not lane_dir.is_dir():
             continue
-        for f in sorted(lane_dir.glob("*.md")):
+        for f in sorted(lane_dir.glob("*.md"), key=lambda p: _task_sort_key(p.name)):
             rec = _parse_task_file(f)
             rec["lane"] = lane
             all_tasks.append(rec)
@@ -1878,6 +1895,91 @@ def _api_task(
         return {"error": "internal error"}
 
 
+def _api_hours(
+    project_root: Optional[str] = None,
+    auth: Optional[AuthState] = None,
+) -> dict:
+    """Return measured hours per day and per week as JSON (GET /api/hours).
+
+    Measured-only semantics, mirroring :func:`_task_brief`: a task counts
+    only when it carries both ``finished_at`` and ``elapsed_seconds``;
+    unstamped tasks are skipped (never zero), so backfilled history cannot
+    fabricate hours. Attribution is by finish date (UTC).
+
+    Error contract mirrors :func:`_api_status`: ``unauthenticated`` and
+    ``forbidden`` dicts, mapped to 401/403 by the route.
+
+    Args:
+        project_root: Optional absolute root from ``?project_root=``.
+        auth: Optional session view; ``None`` means open local mode.
+
+    Returns:
+        ``{"days": [...14 x {date, measured_hours, done}],
+        "weeks": [...8 x {week, start, end, measured_hours, done}]}``.
+    """
+    if auth is not None and not auth.authenticated:
+        return {"error": "unauthenticated"}
+
+    workspace_root = _resolve_dashboard_root(project_root)
+    if auth is not None and not auth.project_allowed(workspace_root):
+        if project_root and project_root.strip():
+            return {"error": "forbidden"}
+        fallback = _first_allowed_root(auth)
+        if fallback is None:
+            return {"error": "forbidden"}
+        workspace_root = fallback
+
+    try:
+        today = date.today()
+        day_keys = [
+            (today - timedelta(days=offset)).isoformat() for offset in range(14)
+        ]
+        week_starts: list[date] = []
+        monday = today - timedelta(days=today.weekday())
+        for index in range(8):
+            week_starts.append(monday - timedelta(days=7 * index))
+        days: dict[str, dict] = {
+            key: {"date": key, "measured_hours": 0.0, "done": 0} for key in day_keys
+        }
+        weeks: dict[str, dict] = {
+            start.isoformat(): {
+                "week": start.isoformat(),
+                "start": start.isoformat(),
+                "end": (start + timedelta(days=6)).isoformat(),
+                "measured_hours": 0.0,
+                "done": 0,
+            }
+            for start in week_starts
+        }
+        for task in _load_all_tasks(workspace_root):
+            brief = _task_brief(task)
+            elapsed = brief.get("elapsed_seconds")
+            finished = _parse_utc(task.get("finished_at"))
+            if elapsed is None or finished is None or elapsed < 0:
+                continue
+            hours = round(elapsed / 3600.0, 2)
+            day_key = finished.date().isoformat()
+            if day_key in days:
+                days[day_key]["measured_hours"] = round(
+                    days[day_key]["measured_hours"] + hours, 2
+                )
+                days[day_key]["done"] += 1
+            week_key = (
+                finished.date() - timedelta(days=finished.date().weekday())
+            ).isoformat()
+            if week_key in weeks:
+                weeks[week_key]["measured_hours"] = round(
+                    weeks[week_key]["measured_hours"] + hours, 2
+                )
+                weeks[week_key]["done"] += 1
+        return {
+            "days": [days[key] for key in sorted(days)],
+            "weeks": [weeks[start.isoformat()] for start in sorted(week_starts)],
+        }
+    except Exception:  # noqa: BLE001 - surface as 500, never a 200 envelope
+        return {"error": "internal error"}
+
+
 _PLAN_WINDOWS = ("day", "week", "month")
 
 
@@ -2125,6 +2227,13 @@ def _plan_payload(
         else:
             anchor_bucket["open"] += 1
 
+    # Numeric task order everywhere: buckets and alert rails inherit load
+    # order, which mixes lanes, so sort each rendered list explicitly.
+    for bucket in buckets.values():
+        bucket["tasks"].sort(key=lambda b: _task_sort_key(b.get("name") or ""))
+    for key in alerts:
+        alerts[key].sort(key=lambda b: _task_sort_key(b.get("name") or ""))
+
     weeks: list[dict] = []
     if window in ("week", "month"):
         grouped: dict[str, list[dict]] = {}
@@ -2241,6 +2350,8 @@ def _api_status(
             if task.get("deadline"):
                 deadlines.append(brief)
 
+        for items in milestone_tree.values():
+            items.sort(key=lambda b: _task_sort_key(b.get("name") or ""))
         deadlines.sort(key=lambda t: t.get("deadline") or "")
         open_work = len(lanes["in-progress"]) + len(lanes["qa"])
 
@@ -2338,6 +2449,23 @@ def build_app():
             return JSONResponse(payload, status_code=500)
         return JSONResponse(payload)
 
+    async def api_hours(request):
+        root = request.query_params.get("project_root")
+        if _relative_root(root):
+            return JSONResponse(
+                {"error": "project_root must be absolute"}, status_code=400
+            )
+        auth = _auth_from_request(request)
+        payload = _api_hours(root, auth)
+        error = payload.get("error")
+        if error == "unauthenticated":
+            return JSONResponse(payload, status_code=401)
+        if error == "forbidden":
+            return JSONResponse(payload, status_code=403)
+        if error == "internal error":
+            return JSONResponse(payload, status_code=500)
+        return JSONResponse(payload)
+
     async def api_plan(request):
         root = request.query_params.get("project_root")
         if _relative_root(root):
@@ -2523,6 +2651,7 @@ def build_app():
         Route("/", dashboard),
         Route("/api/status", api_status),
         Route("/api/task", api_task),
+        Route("/api/hours", api_hours),
         Route("/api/plan", api_plan, methods=["GET"]),
         Route("/api/plan", api_plan_save, methods=["POST"]),
         Route("/api/plan", api_plan_clear, methods=["DELETE"]),
diff --git a/mcp-planner-server/static/index.html b/mcp-planner-server/static/index.html
index 4aa3209..d2c6c27 100644
--- a/mcp-planner-server/static/index.html
+++ b/mcp-planner-server/static/index.html
@@ -91,8 +91,10 @@
             <span class="small text-muted mono" id="plan-totals"></span>
           </div>
           <div id="plan-view"></div>
-          <div class="small text-muted mt-2">Done means a completed task carrying a deadline in this range; the task files store no closed timestamp.</div>
+          <div class="small text-muted mt-2">Done means a completed task carrying a deadline in this range. Measured hours come from task time stamps (<span class="mono">Started</span> → <span class="mono">Finished</span>); unstamped tasks never count.</div>
           <div id="plan-chart" class="mt-3"></div>
+          <div class="label mt-3 mb-1">Measured hours</div>
+          <div id="hours-chart"><div class="small text-muted">Loading…</div></div>
         </div></div>
       </div>
       <div class="col-12 col-lg-4">
@@ -207,6 +209,7 @@
     planTitle: document.getElementById('plan-title'),
     planTotals: document.getElementById('plan-totals'),
     planChart: document.getElementById('plan-chart'),
+    hoursChart: document.getElementById('hours-chart'),
     deadlineRail: document.getElementById('deadline-rail'),
     taskModal: document.getElementById('task-modal'),
     taskModalTitle: document.getElementById('task-modal-title'),
@@ -222,6 +225,13 @@
   let planCommitted = {};
   let mineOnly = false;
   let currentUser = '';
+  // Deep link (?task=<id>) waits for the first successful status: only then
+  // are the project root and the auth state known, so the modal fetch can
+  // carry ?project_root= instead of failing into a dead 401 box.
+  let pendingDeepTask = null;
+  try { pendingDeepTask = new URLSearchParams(window.location.search).get('task'); } catch (e) { pendingDeepTask = null; }
+  // Task id to reopen automatically right after a successful login.
+  let pendingTaskModalId = '';
 
   const JALALI_MONTHS = ['Farvardin', 'Ordibehesht', 'Khordad', 'Tir', 'Mordad', 'Shahrivar', 'Mehr', 'Aban', 'Azar', 'Dey', 'Bahman', 'Esfand'];
 
@@ -259,10 +269,26 @@
         return;
       }
       if (!resp.ok) throw new Error('HTTP ' + resp.status);
-      const data = await resp.json();
+      // Defensive parse: the edge occasionally serves its HTML login page
+      // with 200 for /api/* when the session lapses. resp.json() would throw
+      // "Unexpected token '<'" — diagnose instead of dumping the token.
+      const text = await resp.text();
+      let data;
+      try {
+        data = JSON.parse(text);
+      } catch (e) {
+        throw new Error(/^\s*</.test(text)
+          ? 'board served a page instead of data (edge login expired or /api/* misrouted)'
+          : 'board served invalid data');
+      }
       render(data);
       elements.statusChip.className = 'badge text-bg-success';
       elements.statusText.textContent = 'Server reachable';
+      if (pendingDeepTask) {
+        const deepId = pendingDeepTask;
+        pendingDeepTask = null;
+        openTaskModal(deepId);
+      }
     } catch (err) {
       elements.statusChip.className = 'badge text-bg-danger';
       elements.statusText.textContent = 'Server unreachable: ' + err.message;
@@ -516,6 +542,15 @@
     elements.taskModalClose.focus();
     fetch('/api/task?' + params.toString(), { cache: 'no-cache' })
       .then(async function (resp) {
+        if (resp.status === 401) {
+          // Not signed in (typical for a fresh ?task= link): show login and
+          // reopen this task automatically after a successful sign-in.
+          pendingTaskModalId = id || '';
+          showLoginModal();
+          elements.taskModalMeta.textContent = 'Sign in required';
+          elements.taskModalBody.innerHTML = '<p class="text-muted small">Sign in, then the task opens automatically.</p>';
+          return;
+        }
         const payload = await resp.json().catch(function () { return {}; });
         if (!resp.ok) {
           elements.taskModalMeta.textContent = 'Error ' + resp.status;
@@ -640,6 +675,49 @@
       '<div class="d-flex justify-content-between small text-muted mt-1"><span>' + trend[0].date.slice(5) + '</span><span>open / in progress / done</span><span>' + trend[trend.length - 1].date.slice(5) + '</span></div>';
   }
 
+  function hoursUrl() {
+    const params = new URLSearchParams();
+    if (currentProject) params.set('project_root', currentProject);
+    const query = params.toString();
+    return '/api/hours' + (query ? '?' + query : '');
+  }
+
+  async function fetchHours() {
+    if (!elements.hoursChart) return;
+    try {
+      const resp = await fetch(hoursUrl(), { cache: 'no-cache' });
+      if (!resp.ok) throw new Error('HTTP ' + resp.status);
+      renderHours(await resp.json());
+    } catch (err) {
+      elements.hoursChart.innerHTML = '<div class="small text-muted">Hours unavailable.</div>';
+    }
+  }
+
+  function renderHours(data) {
+    const days = data.days || [];
+    const weeks = data.weeks || [];
+    if (!days.length && !weeks.length) {
+      elements.hoursChart.innerHTML = '<div class="small text-muted">No measured hours yet.</div>';
+      return;
+    }
+    const max = Math.max(0.5, ...days.map(function (d) { return d.measured_hours || 0; }));
+    const width = 100 / Math.max(1, days.length);
+    const bars = days.map(function (d, i) {
+      const h = Math.round(((d.measured_hours || 0) / max) * 46);
+      if (h <= 0) return '';
+      const x = i * width;
+      return '<rect x="' + x + '" y="' + (50 - h) + '" width="' + (width * 0.62) + '" height="' + h + '" fill="var(--gd-accent)"><title>' +
+        d.date.slice(5) + ': ' + d.measured_hours + 'h · ' + d.done + ' done</title></rect>';
+    }).join('');
+    const weekLine = weeks.filter(function (w) { return (w.done || 0) > 0; }).map(function (w) {
+      return '<span class="mono">' + w.start.slice(5) + '→' + w.end.slice(5) + ' ' + w.measured_hours + 'h</span>';
+    }).join(' · ') || '<span class="text-muted">no finished tasks in range</span>';
+    elements.hoursChart.innerHTML = '<svg viewBox="0 0 100 54" width="100%" height="64" role="img" aria-label="Measured hours, last 14 days">' +
+      '<line x1="0" y1="50" x2="100" y2="50" stroke="var(--gd-border)" stroke-width="0.4"></line>' + bars + '</svg>' +
+      '<div class="d-flex justify-content-between small text-muted mt-1"><span>' + (days.length ? days[0].date.slice(5) : '') + '</span><span>measured h/day</span><span>' + (days.length ? days[days.length - 1].date.slice(5) : '') + '</span></div>' +
+      '<div class="small mt-1"><span class="text-muted">Weeks: </span>' + weekLine + '</div>';
+  }
+
   function renderDeadlineRail(alerts) {
     const groups = [['Overdue', alerts.overdue || [], 'var(--gd-danger)'], ['Today', alerts.today || [], 'var(--gd-warning)'], ['Next 3 days', alerts.soon || [], 'var(--gd-info)']];
     const total = groups.reduce(function (sum, g) { return sum + g[1].length; }, 0);
@@ -810,7 +888,14 @@
         hideLoginModal();
         showUserBadge(data.username, data.role);
         currentProject = '';
-        fetchStatus();
+        fetchStatus().then(function () {
+          if (pendingTaskModalId) {
+            const retryId = pendingTaskModalId;
+            pendingTaskModalId = '';
+            openTaskModal(retryId);
+          }
+        });
+        fetchHours();
       } else if (data.note === 'auth disabled') {
         hideLoginModal();
         fetchStatus();
@@ -848,13 +933,13 @@
 
   fetchStatus();
   fetchPlan();
+  fetchHours();
   setInterval(fetchStatus, 30000);
   setInterval(fetchPlan, 60000);
+  setInterval(fetchHours, 60000);
   document.querySelectorAll('[data-window]').forEach(function (b) {
     b.className = 'btn btn-sm ' + (b.dataset.window === planWindow ? 'btn-primary' : 'btn-outline-secondary');
   });
-  const initialTask = new URLSearchParams(window.location.search).get('task');
-  if (initialTask) openTaskModal(initialTask);
 })();
 </script>
 <script src="/static/vendor/bootstrap.bundle.min.js"></script>
diff --git a/tests/test_planner_server.py b/tests/test_planner_server.py
index 07fe217..41877ca 100644
--- a/tests/test_planner_server.py
+++ b/tests/test_planner_server.py
@@ -513,6 +513,123 @@ def test_api_status_explicit_project_root_wins_over_env(tmp_path, monkeypatch):
     assert payload["project_root"] == str(tmp_path.resolve())
 
 
+def _write_mixed_width_task(tmp_path, lane, filename, title, **headers):
+    """Write a task file with an exact filename (mixed widths allowed)."""
+    lane_dir = tmp_path / "tasks" / lane
+    lane_dir.mkdir(parents=True, exist_ok=True)
+    lines = [
+        f"# Task {title}",
+        "",
+        f"**File:** `tasks/{lane}/{filename}`",
+        "**Source:** manager",
+        "**Type:** feature",
+        "**Status:** open",
+    ]
+    for key, value in headers.items():
+        lines.append(f"**{key}:** {value}")
+    lines += [
+        "",
+        "## Goal",
+        "",
+        "Fixture.",
+        "",
+        "## Local TODOs",
+        "",
+        "- [x] Done",
+        "",
+        "## Acceptance Criteria",
+        "",
+        "- [x] Done",
+        "",
+        "## Verification Evidence",
+        "",
+        "Done.",
+        "",
+        "## Risk & Rollback",
+        "",
+        "None.",
+        "",
+        "## Execution Log & Reasoning",
+        "",
+        "Done.",
+        "",
+        "## Factual Git Diff",
+        "",
+        "<!-- BEGIN_GIT_DIFF -->",
+        "<!-- END_GIT_DIFF -->",
+        "",
+    ]
+    (lane_dir / filename).write_text("\n".join(lines), encoding="utf-8")
+
+
+def test_lane_lists_sort_numerically_despite_mixed_widths(tmp_path):
+    """Lexical glob order puts 0356 before 283; the board must not."""
+    _write_mixed_width_task(tmp_path, "backlog", "0356-new.md", "New task")
+    _write_mixed_width_task(tmp_path, "backlog", "283-old.md", "Old task")
+    payload = planner._api_status(str(tmp_path))
+    ids = [b["id"] for b in payload["lanes"]["backlog"]]
+    assert ids == ["283", "0356"], ids
+
+
+def test_milestone_tree_sorts_numerically(tmp_path):
+    _write_mixed_width_task(
+        tmp_path, "backlog", "0356-new.md", "New task", Milestone="M1"
+    )
+    _write_mixed_width_task(
+        tmp_path, "backlog", "283-old.md", "Old task", Milestone="M1"
+    )
+    payload = planner._api_status(str(tmp_path))
+    ids = [b["id"] for b in payload["milestone_tree"]["M1"]]
+    assert ids == ["283", "0356"], ids
+
+
+def test_api_hours_aggregates_measured_only(tmp_path):
+    """Finished+stamped tasks count by finish date; unstamped never count."""
+    from datetime import date, timedelta
+
+    today = date.today()
+    three_days_ago = today - timedelta(days=3)
+    stamp = lambda d, h, m: f"{d.isoformat()}T{h:02d}:{m:02d}:00Z"
+    _write_mixed_width_task(
+        tmp_path,
+        "completed",
+        "283-old.md",
+        "Old done",
+        Started=stamp(today, 10, 0),
+        Finished=stamp(today, 12, 30),
+    )
+    _write_mixed_width_task(
+        tmp_path,
+        "completed",
+        "0356-new.md",
+        "New done",
+        Started=stamp(today, 14, 0),
+        Finished=stamp(today, 15, 0),
+    )
+    _write_mixed_width_task(
+        tmp_path,
+        "completed",
+        "100-earlier.md",
+        "Earlier done",
+        Started=stamp(three_days_ago, 9, 0),
+        Finished=stamp(three_days_ago, 10, 0),
+    )
+    _write_mixed_width_task(tmp_path, "completed", "101-unstamped.md", "No stamps")
+    payload = planner._api_hours(str(tmp_path))
+    assert "error" not in payload
+    by_date = {d["date"]: d for d in payload["days"]}
+    assert by_date[today.isoformat()]["measured_hours"] == 3.5
+    assert by_date[today.isoformat()]["done"] == 2
+    assert by_date[three_days_ago.isoformat()]["measured_hours"] == 1.0
+    assert by_date[three_days_ago.isoformat()]["done"] == 1
+    assert sum(d["done"] for d in payload["days"]) == 3
+    current_week = today - timedelta(days=today.weekday())
+    by_week = {w["week"]: w for w in payload["weeks"]}
+    assert by_week[current_week.isoformat()]["done"] >= 2
+    assert len(payload["days"]) == 14
+    assert len(payload["weeks"]) == 8
+
+
 def test_resolve_dashboard_root_uses_env(tmp_path, monkeypatch):
     (tmp_path / "tasks").mkdir(parents=True, exist_ok=True)
     monkeypatch.setenv("PLANNER_PROJECT_ROOT", str(tmp_path))
```
<!-- END_GIT_DIFF -->
