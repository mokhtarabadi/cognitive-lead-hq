# Task 348: Auto-register projects that use the planner MCP

**File:** `tasks/qa/0348-planner-project-registry.md`
**Source:** manager
**Type:** feature
**Status:** in-progress
**Estimate:** 2h
**Sprint:** S26-W44
**Milestone:** M03

## Goal

Any project whose session calls a planner MCP tool is remembered automatically, so the dashboard's project switcher lists it without editing `PLANNER_PROJECTS` by hand.

## Design

- New registry file `~/.config/opencode/planner-projects.json` (override `PLANNER_PROJECTS_REGISTRY`), shape `{"projects": ["/abs/path", ...]}` capped at the 50 most recent, written atomically.
- `_project_tool` records the resolved `project_root` after every successful tool call; failures never surface to the caller.
- `_discover_projects` merges registry entries with `PLANNER_PROJECTS` and the current root, de-duplicates, and keeps only directories that exist and hold `tasks/`; when a session is present, grants still filter the list.
- Dashboard needs no change: it renders `projects`.

## Local TODOs

- [x] Registry helpers (`_registry_path`, `_read_projects_registry`, `_register_project`) with env override, 50-entry cap, atomic write
- [x] Record the resolved root from `_project_tool` (kwargs or first positional arg), swallowing failures
- [x] Merge registry entries into `_discover_projects` before the exists/`tasks/`/grant filters
- [x] Four tests: record + dedupe, cap, registered project listed, dead path dropped

## Acceptance Criteria

- [x] Calling a planner tool from a project adds that absolute path to the registry once (idempotent)
- [x] `GET /api/status` lists a registered project without `PLANNER_PROJECTS`
- [x] Non-existent paths and paths without `tasks/` are filtered out
- [x] A viewer still sees only granted projects despite registration
- [x] Registry writes are atomic and capped at 50 entries
- [x] Full planner suite passes with exit code 0

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/test_planner_server.py -q`
- **Expected result:** 115 existing tests plus the new registry tests pass
- **Actual result:** `119 passed, 2 warnings in 41.43s` (four new registry tests)
- **Exit code:** 0

## Definition of Done

- [x] `lint_task_file` passes; `CHANGELOG.md` updated; README documents the registry
- [x] Deployed to `~/.config/opencode/mcp-planner-server/` and `mcp-planner` restarted

## Risk & Rollback

- **Risk:** a tool call with a wrong `project_root` pollutes the list; mitigated by the `tasks/` + existence filter and the 50-entry cap.
- **Rollback:** delete the registry file; discovery falls back to `PLANNER_PROJECTS` + current root.

## Execution Log & Reasoning

Autopilot task created from the Manager's question about automatic project discovery (2026-10-25).

**Implementation:** `_register_project` writes the resolved root into `~/.config/opencode/planner-projects.json` (env override, newest first, cap 50, temp + `os.replace`, all failures swallowed); `_project_tool` records the root from kwargs or the first positional arg after every call; `_discover_projects` merges the registry with `PLANNER_PROJECTS` and the current root before the exists/`tasks/`/grant filters. Verified: 119 tests pass, deployed and `mcp-planner` restarted.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 61e37f9..d05655c 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -55,6 +55,8 @@ _(nothing yet)_
 
 ### Changed
 
+- **Planner auto-registers the projects that use it (Task 348):** every tool call carrying an explicit `project_root` now records that path in `~/.config/opencode/planner-projects.json` (`PLANNER_PROJECTS_REGISTRY` override), newest first, capped at 50, written via temp + `os.replace`, and never failing the tool call. `_discover_projects` merges the registry with `PLANNER_PROJECTS` and the current root before applying the existing exists/`tasks/`/grant filters, so a project shows up in the dashboard switcher after its first planner call instead of requiring an env edit. Verified: 119 planner tests pass (four new: record + dedupe, 50-entry cap, registered project appears, dead path dropped), `py_compile` clean.
+
 - **Login form is now a real form, so password managers fill both fields (lite change):** the sign-in overlay had two loose inputs, `autocomplete="off"` on the username, no `name` attributes and a `type="button"` submit, so Chrome injected the last typed username ("admin") while Google Password Manager only filled the password. It is now a `<form method="post" action="#">` with `name="username"` / `autocomplete="username"` and `name="password"` / `autocomplete="current-password"`, a real submit button, and a submit handler that prevents navigation and calls the existing login. Enter submits once and the manager recognises the credential pair. Verified: inline script parses, deployed, live page serves both attributes. Lite justification: single static file, no auth logic touched, reversible by reverting the markup.
 
 - **Public board hardening and a real Jalali library (META 344 audit):** an authorized audit of `https://board.surfshield.org/` produced four fixes. The dashboard's Jalali conversion was a hand-copied algorithm with wrong leap-year behaviour and the timeline rendered Gregorian numbers only under a "Gregorian + Jalali" heading; `jalaali-js` 1.2.6 is now vendored (`static/vendor/jalaali.min.js`, MIT, 2.9KB) and the timeline shows the Jalali day as primary, the Gregorian day beneath, the month name at each Jalali month start, and a full tooltip. The session cookie now carries `Secure` when the request arrives over HTTPS (`X-Forwarded-Proto` aware, since the daemon sits behind a tunnel), a relative `?project_root=` is rejected with `400 {"error":"project_root must be absolute"}` instead of silently resolving against the daemon cwd, and a `_SecurityHeaders` middleware adds `X-Content-Type-Options: nosniff`, `Referrer-Policy: same-origin`, `X-Frame-Options: DENY` plus HSTS on HTTPS. Verified live on the board (Secure cookie, all four headers, 400 on the relative root, 200 on the vendored script) and by 100 passing planner tests, three of them new. `/mcp` still answers `421` remotely instead of the documented `404`; no cloudflared config exists on this host, so that ingress fix is Cloudflare-side.
diff --git a/mcp-planner-server/README.md b/mcp-planner-server/README.md
index ce9da70..4bc726b 100644
--- a/mcp-planner-server/README.md
+++ b/mcp-planner-server/README.md
@@ -163,6 +163,16 @@ truth for each task; the plan only records scheduling decisions.
   deviations (claimed but uncommitted, saved but unapproved); with no plan it
   says it is using the derived lanes.
 
+### Project registry
+
+Every planner tool call with an explicit `project_root` records that path in
+`~/.config/opencode/planner-projects.json` (`PLANNER_PROJECTS_REGISTRY`
+overrides), newest first, capped at 50, written atomically. `_discover_projects`
+merges the registry with `PLANNER_PROJECTS` and the current root, then keeps only
+paths that exist and hold `tasks/`, applying session grants as before. So a
+project appears in the dashboard switcher after its first planner call, without
+editing the environment.
+
 ### Ownership and pressure signals
 
 A task file may carry `**Owner:** <username>`; briefs expose it and the
diff --git a/mcp-planner-server/server.py b/mcp-planner-server/server.py
index 1fe45ae..818a8a2 100644
--- a/mcp-planner-server/server.py
+++ b/mcp-planner-server/server.py
@@ -81,6 +81,52 @@ _ROOT_FALLBACK_WARNING = (
 )
 
 
+_PROJECTS_REGISTRY_ENV = "PLANNER_PROJECTS_REGISTRY"
+_PROJECTS_REGISTRY_LIMIT = 50
+
+
+def _registry_path() -> Path:
+    """Machine-local registry of projects that have used the planner."""
+    override = os.environ.get(_PROJECTS_REGISTRY_ENV, "").strip()
+    if override:
+        return Path(override).expanduser()
+    return Path.home() / ".config" / "opencode" / "planner-projects.json"
+
+
+def _read_projects_registry() -> list[str]:
+    """Registered roots, newest first; unreadable files behave as empty."""
+    try:
+        data = json.loads(_registry_path().read_text(encoding="utf-8"))
+    except (OSError, ValueError):
+        return []
+    projects = data.get("projects") if isinstance(data, dict) else None
+    return [str(p) for p in projects] if isinstance(projects, list) else []
+
+
+def _register_project(project_root: Path) -> None:
+    """Record a root that just used a planner tool (best-effort, atomic).
+
+    Never raises: a registry failure must not fail the tool call the user
+    asked for. Keeps the newest entry first and caps the list.
+    """
+    try:
+        root = str(Path(project_root).resolve())
+        current = _read_projects_registry()
+        if current and current[0] == root:
+            return
+        entries = [root] + [p for p in current if p != root]
+        path = _registry_path()
+        path.parent.mkdir(parents=True, exist_ok=True)
+        tmp = path.with_suffix(".json.tmp")
+        tmp.write_text(
+            json.dumps({"projects": entries[:_PROJECTS_REGISTRY_LIMIT]}, indent=2),
+            encoding="utf-8",
+        )
+        os.replace(tmp, path)
+    except OSError:
+        return
+
+
 def _project_tool(fn):
     """Register an MCP tool that surfaces root-fallback client-visibly."""
 
@@ -88,6 +134,11 @@ def _project_tool(fn):
     def wrapper(*args, **kwargs):
         _FALLBACK_FIRED.set(False)
         out = fn(*args, **kwargs)
+        requested = kwargs.get("project_root")
+        if requested is None and args and isinstance(args[0], str):
+            requested = args[0]
+        if requested and str(requested).strip():
+            _register_project(Path(str(requested)).expanduser())
         if not _FALLBACK_FIRED.get():
             return out
         if isinstance(out, str):
@@ -1377,6 +1428,13 @@ def _discover_projects(current: Path, auth: Optional[AuthState] = None) -> list[
         if not chunk:
             continue
         roots.append(Path(chunk).expanduser().resolve())
+    # Projects that have used a planner tool are remembered automatically, so a
+    # session never has to edit PLANNER_PROJECTS by hand.
+    for entry in _read_projects_registry():
+        try:
+            roots.append(Path(entry).expanduser().resolve())
+        except OSError:
+            continue
 
     seen: set[Path] = set()
     projects: list[dict] = []
diff --git a/tests/test_planner_server.py b/tests/test_planner_server.py
index 5422637..4500960 100644
--- a/tests/test_planner_server.py
+++ b/tests/test_planner_server.py
@@ -1106,6 +1106,46 @@ def test_claim_next_reports_overdue(tmp_path):
     assert "OVERDUE" in result and "063" in result
 
 
+def test_project_registry_records_and_dedupes(tmp_path, monkeypatch):
+    reg = tmp_path / "reg.json"
+    monkeypatch.setenv("PLANNER_PROJECTS_REGISTRY", str(reg))
+    target = tmp_path / "proj"
+    (target / "tasks").mkdir(parents=True)
+    planner._register_project(target)
+    planner._register_project(target)
+    assert planner._read_projects_registry() == [str(target.resolve())]
+
+
+def test_project_registry_is_capped(tmp_path, monkeypatch):
+    reg = tmp_path / "reg.json"
+    monkeypatch.setenv("PLANNER_PROJECTS_REGISTRY", str(reg))
+    for i in range(55):
+        planner._register_project(tmp_path / f"p{i}")
+    assert len(planner._read_projects_registry()) == 50
+
+
+def test_discover_projects_includes_registered(tmp_path, monkeypatch):
+    reg = tmp_path / "reg.json"
+    monkeypatch.setenv("PLANNER_PROJECTS_REGISTRY", str(reg))
+    monkeypatch.delenv("PLANNER_PROJECTS", raising=False)
+    project = tmp_path / "registered"
+    (project / "tasks").mkdir(parents=True)
+    planner._register_project(project)
+    names = [p["path"] for p in planner._discover_projects(tmp_path)]
+    assert str(project.resolve()) in names
+
+
+def test_discover_projects_drops_dead_registered_paths(tmp_path, monkeypatch):
+    reg = tmp_path / "reg.json"
+    monkeypatch.setenv("PLANNER_PROJECTS_REGISTRY", str(reg))
+    monkeypatch.delenv("PLANNER_PROJECTS", raising=False)
+    dead = tmp_path / "no-tasks"
+    dead.mkdir()
+    planner._register_project(dead)
+    names = [p["path"] for p in planner._discover_projects(tmp_path)]
+    assert str(dead.resolve()) not in names
+
+
 def test_api_plan_http_contract(auth_client):
     assert auth_client.get("/api/plan").status_code == 401
     auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
```
<!-- END_GIT_DIFF -->
