# Task 338: Unblock Loopback MCP Transport

**File:** `tasks/completed/0338-unblock-loopback-mcp-transport.md`
**Source:** orchestrator
**Type:** bug
**Status:** completed

## Goal

Make `POST /mcp` auth-free so local OpenCode clients connect without credentials, while keeping `/`, `/static/*`, and every `/api/*` route guarded by session auth when authentication is enabled.

## Manager's Notes

- The Cloudflare Tunnel ingress already answers `http_status: 404` for `^/mcp(/.*)?$`, so the endpoint is unreachable from outside the host.
- Local loopback calls from OpenCode must not be blocked by the in-process guard.
- `/api/login`, `/api/logout`, `/api/me`, `/api/status`, and `/` keep their session checks intact.

## Local TODOs

- [x] Step 1: Create task file
- [x] Step 2: Make `_guarded_mcp_app` a pass-through to the MCP transport
- [x] Step 3: Remove the now-dead `_send_json` helper and update the module docstring
- [x] Step 4: Rewrite the `/mcp` guard tests around the open-loopback contract
- [x] Step 5: Run the planner test suite
- [x] Step 6: Deploy `server.py` to `~/.config/opencode/mcp-planner-server/` and restart the unit
- [x] Step 7: Verify a cookie-free loopback MCP handshake and that the guards still fire
- [x] Step 8: Update `DECISIONS.md`, `README.md`, `docs/services.md`, `CHANGELOG.md`
- [x] Step 9: QA transition

## Acceptance Criteria

- [x] `_guarded_mcp_app` passes every request to `mcp_app` with no `SESSION_COOKIE` and no role check, in open mode and with auth enabled
- [x] `/api/login`, `/api/logout`, `/api/me`, `/api/status`, and `/` session checks are unchanged
- [x] `tests/test_planner_server.py` asserts `/mcp` is open without a session and for a viewer session
- [x] A test asserts `/api/status` and `/api/me` still return 401 on the same auth-enabled app where `/mcp` passes
- [x] Full planner suite passes with exit code 0
- [x] Deployed `server.py` is byte-identical to the repo copy and `mcp-planner` is `active`
- [x] Live cookie-free `initialize` + `tools/list` on `127.0.0.1:8108/mcp` returns tools
- [x] `DECISIONS.md` records the trust-boundary decision (ADR-006)

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/test_planner_server.py -q`
- **Expected result:** All planner tests pass (76 before the change, same total after the guard tests were rewritten 3 → 3).
- **Actual result:** `76 passed, 2 warnings in 35.50s`
- **Exit code:** 0
- **Deployment evidence:** `cp mcp-planner-server/server.py ~/.config/opencode/mcp-planner-server/server.py`; `diff -q` clean; `systemctl --user is-active mcp-planner` → `active`; `ss -tlnp` shows `127.0.0.1:8108`.
- **Live loopback MCP evidence (auth enabled, no cookie):** `initialize` → 200 with `mcp-session-id`, `notifications/initialized` → 202, `tools/list` with that session id → `result.tools` listing `plan_propose` first.
- **Live guard evidence (same auth-enabled server):** `GET /api/me` → 401, `GET /api/status` → 401, `GET /` → 200 (dashboard shell; the login modal is client-side on the `/api/me` 401), `GET /static/index.html` → 200.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `verification-before-completion` applied and evidence recorded
- [x] Files copied to global `~/.config/opencode/mcp-planner-server/`
- [x] `mcp-planner` service restarted and active
- [x] `scripts/check_docs_sync.py` exits 0

## Risk & Rollback

- **Risk:** Tool execution now trusts the bind and the tunnel ingress instead of an in-process guard. A catch-all ingress rule placed before the `/mcp` 404, or rebinding the port off loopback, would expose unauthenticated tool execution.
- **Mitigation:** The ingress ordering rule and the external `curl https://<host>/mcp` → 404 probe stay documented in `docs/services.md` and the component README, which now states the invariant explicitly.
- **Rollback plan:** Restore the cookie/role checks in `_guarded_mcp_app`, restore the three guard tests, redeploy, restart the unit. No config or dashboard change is involved.

## Execution Log & Reasoning

### Scope delivered

1. `mcp-planner-server/server.py`: `_guarded_mcp_app` reduced to a pass-through (`loopback_only`) with a docstring naming the trust boundary; the dead `_send_json` helper deleted; the module docstring's auth paragraph corrected.
2. `tests/test_planner_server.py`: the three guard tests (`401` unauthenticated, `403` viewer, admin admitted) replaced by `test_mcp_open_without_session_when_auth_enabled`, `test_mcp_open_for_viewer_session`, and `test_api_status_stays_guarded_while_mcp_is_open`.
3. Docs: `mcp-planner-server/README.md` (route table row, `/mcp` contract bullet, new Key Risk invariant), `mcp-planner-server/DECISIONS.md` (ADR-006 plus a "superseded in part" marker on ADR-005), `docs/services.md` (planner auth paragraph), `CHANGELOG.md`.

### Assumptions

- **A1 — No task file existed for 338.** `tasks/{backlog,in-progress,qa}` were empty and no `338-*.md` existed anywhere, so the file was created here before implementation; without it there is nothing to stage or move through QA.
- **A2 — The wrapper is kept, not inlined.** `build_app()` still mounts `_guarded_mcp_app(mcp_app)`. An identity wrapper is one no-op call, but it keeps a single named place where a future guard can return and matches the Orchestrator's instruction to change behaviour "in `_guarded_mcp_app`" rather than at the mount.
- **A3 — `_send_json` is removed, not left unused.** After the change it had no callers (verified by grep across `server.py`, `tests/`, and `docs/`); leaving it would be dead code with a docstring claiming it serves the `/mcp` guard.
- **A4 — The Orchestrator's verification curl cannot pass as written.** `tools/list` without a session id is rejected by the transport itself with `400 {"code":-32600,"message":"Bad Request: Missing session ID"}`, in both auth modes and before this change. The unblocking was therefore proven with a real `initialize` → `notifications/initialized` → `tools/list` sequence. The 400 was not a guard status, so it already showed the guard was gone, but it is not the "result" the script greps for.

### Verification performed

- Planner suite via `rtk test …` → 76 passed, exit 0 (the count is unchanged because three guard tests were replaced by three).
- Deploy → `diff -q` clean, unit `active`, listener on `127.0.0.1:8108`.
- Cookie-free handshake with auth enabled (`planner-users.json` with the `admin` user is live on this host): `initialize` 200, `notifications/initialized` 202, `tools/list` returns the tool array.
- Guards on the same process: `/api/me` 401, `/api/status` 401, `/` 200, `/static/index.html` 200.

### Known limitation (documented, not fixed)

`/mcp` has no in-process authorization left. That is the decision, and it is safe only while the port stays on `127.0.0.1` and the tunnel keeps the `^/mcp(/.*)?$ → 404` rule ahead of the catch-all. Both facts are now stated as invariants in the component README and ADR-006.

### Deployment state

Global install carries the new `server.py`; the unit restarted and is serving. `~/.config/opencode/planner-users.json` stays in place with auth enabled, so the dashboard still asks for a login while local MCP clients connect freely.

### Closure

The Manager relayed the Orchestrator closure task. `git mv tasks/qa/ → tasks/completed/`, `**File:**` and `**Status:**` synced, `lint_task_file` re-run, and the commit went through `custom_context_commit_and_clean_task` with `fix: unblock loopback mcp transport while guarding web routes` — the only commit path used; no `git add`, `git commit`, or `git push` was run by hand. Skills loaded for this phase: `versioning-and-release` (Conventional Commits type `fix`, lowercase imperative subject) and `verification-before-completion` (suite re-run before the claim: 76 passed, exit 0). `CHANGELOG.md` already carried this task's entry under `### Added`, so nothing was duplicated.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index c4b76c8..8f418f4 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Loopback MCP transport unblocked (Task 338):** `/mcp` is auth-free again, in open mode and with authentication enabled alike. `_guarded_mcp_app` in `mcp-planner-server/server.py` is now a pass-through to the FastMCP transport — no `SESSION_COOKIE` lookup, no admin-role check, no 401/403 from that path — so OpenCode's local clients connect without credentials even while the dashboard requires a login. Remote exposure was never carried by that guard: the Cloudflare Tunnel ingress answers `http_status: 404` for `^/mcp(/.*)?$` before the catch-all, so the endpoint is unreachable off-host. `/`, `/static/*`, `/api/login`, `/api/logout`, `/api/me`, and `/api/status` keep their session checks untouched; the dead `_send_json` helper (whose only callers were the deleted guard branches) is removed and the module docstring corrected. The three former guard tests (`401` unauthenticated, `403` viewer, admin admitted) are replaced by `test_mcp_open_without_session_when_auth_enabled`, `test_mcp_open_for_viewer_session`, and `test_api_status_stays_guarded_while_mcp_is_open`, which pins the split — one auth-enabled app where `/mcp` passes and `/api/status`/`/api/me` still answer 401. Because tool execution now trusts the bind and the edge instead of an in-process guard, the `^/mcp(/.*)?$ → 404` ingress rule is load-bearing: the component README states it as a Key Risk invariant and `DECISIONS.md` ADR-006 records the decision and its consequences (ADR-005 is marked superseded in part). Docs updated in `docs/services.md` and `mcp-planner-server/README.md`. Verified: 76/76 planner tests pass, deployed `server.py` is byte-identical to the repo copy, unit `active` on `127.0.0.1:8108`, and a cookie-free `initialize` → `notifications/initialized` → `tools/list` handshake returns the tool array while `GET /api/me` and `GET /api/status` still answer 401.
+
 - **Planner auth, RBAC, and per-user project scoping (Task 337):** the planner can now be exposed through a Cloudflare Tunnel without giving strangers the board. Auth is opt-in via `~/.config/opencode/planner-users.json` (`PLANNER_USERS_CONFIG` override): a missing, unreadable, non-object, or `auth_enabled: false` file — or one with no users — leaves the server in open local mode with no 401s and no filtering, so every existing local client keeps working untouched. When enabled, `server.py` gains stdlib-only auth: `hashlib.pbkdf2_hmac("sha256", …, 600_000)` with a 16-byte `secrets` salt verified by `hmac.compare_digest`, opaque `secrets.token_urlsafe(32)` sessions in an in-memory store behind an `HttpOnly` `SameSite=Lax` `planner_session` cookie (7-day TTL, dropped on restart), `POST /api/login`, `POST /api/logout`, `GET /api/me`, and an `AuthState` that answers `project_allowed()` for `"*"` or any granted root and its subdirectories. `GET /api/status` returns 401 until sign-in, filters `projects` to `allowed_projects`, and 403s an explicit `project_root` outside them (a viewer with no explicit root falls back to their first allowed project instead of being denied); `POST /mcp` is wrapped in an ASGI guard that admits admin sessions only, so a viewer reads the dashboard and never executes tools. The dashboard gains a dark-mode login modal shown on 401, a `#user-badge` with a role chip, a logout button, and `/static/*` asset serving; `manage_users.py` is a stdlib `argparse` CLI (`add`/`update`/`remove`/`list`/`enable`/`disable`, `--password` for non-interactive use, file written `chmod 600`) that hashes through the same scheme the server verifies. Cloudflare Tunnel ingress is documented in `docs/services.md` and the component README, with the `/mcp` rule ordered first as `http_status:404` so tool execution never leaves the host. Two defects in the working tree were fixed rather than shipped: a corrupted `TASK_ID_RE` (`\\.md` never matched, so task lookup and dashboard ids broke) and a duplicated `# /// script` header. Verified: 76/76 planner tests pass (login valid/invalid, RBAC admin vs viewer, 403 on an unauthorized root, the three `/mcp` guard cases, open-mode backward compatibility, and CLI hashing cross-checked by the server's own verifier); `docs-sync: OK`; unit `active` with the new code deployed.
 
 - **Planner MCP deployed globally and wired into the executor protocol (Task 336):** the planner is now a live platform singleton rather than repo-local code. It installs to `~/.config/opencode/mcp-planner-server/` (source, committed `uv.lock`, and `static/` dashboard assets) with its venv built by `uv sync` from the lock, runs as `mcp-planner.service` on `127.0.0.1:8108` (enabled, active, loopback-only), and is registered in the global `opencode.json` as `mcp.servers.planner` (`type: remote`, `http://127.0.0.1:8108/mcp`, timeout 15000/30000). `agents/cognitive-executor.md` gains a *Planner MCP and Daily Pacing Protocol* section binding four moments to four tools: `sprint_daily_agenda` when the Manager starts the day, `claim_next` instead of hand-moving a task file (a block is reported, never bypassed), `sprint_check_daily_quota` when tasks close, and `plan_status`/`qa_budget` for status questions — with an explicit fallback to the Kanban workflow if the server is unreachable. `LLM.txt` provisions the whole thing (§4 directory, §5 copy block, §7 config entry, §7.5 venv-before-unit plus drop-in, verification checklist), `README.md` lists the component, and `docs/services.md` keeps the port map. Deployment adaptations forced by what actually ran: `uv pip install -e .` cannot work because the package declares no build backend, so the venv comes from `uv sync` against the committed lock; the committed unit stays machine-independent and the dashboard's project root is supplied by a `mcp-planner.service.d` drop-in (`PLANNER_PROJECT_ROOT`), since the unit's WorkingDirectory is the install dir which holds no `tasks/`; and `opencode mcp list` prints "No MCP servers configured" on v2.1.4 even for the six servers already in use, so registration is verified with `opencode debug config` (7 resolved `127.0.0.1:810*/mcp` entries) plus a live MCP handshake instead — the docs now say so. Verified: unit `active`/`enabled`, `/` and `/api/status` both 200 with 329 tasks for this repo, planner tools enumerable over `initialize`+`tools/list`, `scripts/check_docs_sync.py` exits 0, 31/31 planner tests pass, full suite 592 passed with the one pre-existing prompt round-trip failure.
diff --git a/docs/services.md b/docs/services.md
index dd7c905..150ee2b 100644
--- a/docs/services.md
+++ b/docs/services.md
@@ -29,8 +29,10 @@ Planner authentication is **optional and off by default**: with no
 server stays in open local mode, byte-identical to the pre-auth
 behaviour. With auth on, `POST /api/login` issues an `HttpOnly`
 `planner_session` cookie, `/api/status` is 401 until sign-in and 403
-outside the caller's `allowed_projects`, and `/mcp` accepts admin
-sessions only. Users are managed with the stdlib CLI (no venv needed):
+outside the caller's `allowed_projects`. `/mcp` is deliberately auth-free on
+loopback (the tunnel answers 404 for it), so local MCP clients connect with
+no credentials even when auth is on. Users are managed with the stdlib CLI
+(no venv needed):
 
 ```bash
 python3 ~/.config/opencode/mcp-planner-server/manage_users.py \
diff --git a/mcp-planner-server/DECISIONS.md b/mcp-planner-server/DECISIONS.md
index 774e6a5..2ead5e1 100644
--- a/mcp-planner-server/DECISIONS.md
+++ b/mcp-planner-server/DECISIONS.md
@@ -93,3 +93,32 @@ the CLI test that hashes through the server's own verifier.
 - **Rollback:** Delete `planner-users.json` or run `manage_users.py disable`;
 the server returns to open local mode with no code change. Full code rollback is
 `server.py` + `static/index.html` + `manage_users.py` reverted together.
+- **Superseded in part:** the `/mcp` admin-session requirement only — see
+ADR-006 below. Session auth, scoping, and the CLI remain as decided here.
+
+## [2026-10-24] ADR-006: `/mcp` is auth-free on loopback; the edge is the gate
+
+- **Context:** With auth enabled, the `/mcp` guard returned 401 to every
+  credential-free caller, and OpenCode's local clients connect with no cookie.
+  The transport therefore broke whenever the Manager turned authentication on
+  for the dashboard — the two requirements collided inside one process.
+  The `/mcp` route is already unreachable from outside: the Cloudflare Tunnel
+  ingress answers `http_status: 404` for `^/mcp(/.*)?$` before the catch-all
+  rule, so no remote request ever reaches the process.
+- **Decision:** `_guarded_mcp_app` passes every request straight to the MCP
+  transport, in open mode and with auth enabled alike. No `SESSION_COOKIE`
+  check, no admin-role check, no 401/403 from that path. `/`, `/static/*`,
+  `/api/login`, `/api/logout`, `/api/me`, and `/api/status` keep their session
+  checks unchanged — the dashboard is still authenticated.
+- **Consequences:** Local MCP clients work in both auth modes, which removes the
+  old "set `auth_enabled: false` or lose your tools" coupling. Tool execution
+  now trusts the bind (127.0.0.1) plus the tunnel ingress instead of an
+  in-process guard, so **the ingress rule is load-bearing for security**: adding
+  a catch-all tunnel rule before the `/mcp` 404, or rebinding the port off
+  loopback, exposes unauthenticated tool execution. The ingress ordering and
+  the external `curl …/mcp` → 404 probe in `docs/services.md` are the checks
+  that hold this. Pinned by
+  `tests/test_planner_server.py::test_mcp_open_without_session_when_auth_enabled`
+  and `::test_api_status_stays_guarded_while_mcp_is_open`.
+- **Rollback:** Restore the cookie/role checks in `_guarded_mcp_app` and the
+  three guard tests; no config or dashboard change is involved.
diff --git a/mcp-planner-server/README.md b/mcp-planner-server/README.md
index 43379a9..295a4e0 100644
--- a/mcp-planner-server/README.md
+++ b/mcp-planner-server/README.md
@@ -32,7 +32,7 @@ dashboard on loopback port 8108.
 | `POST /api/login` | `{"username","password"}` → `{token, username, role, allowed_projects}` + `HttpOnly` cookie. |
 | `POST /api/logout` | Invalidates the session and clears the cookie. |
 | `GET /api/me` | Current user, or 401 when signed out (200 + `note: "auth disabled"` in open mode). |
-| `POST /mcp` | MCP Streamable HTTP endpoint (tools). Admin-only when auth is enabled. |
+| `POST /mcp` | MCP Streamable HTTP endpoint (tools). Auth-free on loopback; the tunnel 404s it. |
 
 `/api/status` returns per-lane **task lists** (`lanes`), the milestone tree
 (`milestone_tree`), upcoming deadlines (`deadlines`), the pacing figures
@@ -65,9 +65,11 @@ holding `tasks/`, then the working directory. `PLANNER_PROJECTS`
   `project_root` is outside `allowed_projects`, and filters `projects` to the
   allowed roots. Without an explicit root a viewer falls back to their first
   allowed project instead of being denied.
-- **`/mcp`:** admin sessions only when auth is enabled; viewers get 403 and
-  signed-out callers 401. Local MCP clients (no cookie) therefore need
-  `auth_enabled: false`, which is the default.
+- **`/mcp`:** auth-free in every mode, including with auth enabled. Local MCP
+  clients call it on loopback with no cookie; the Cloudflare Tunnel ingress
+  answers `404` for `/mcp` before the catch-all rule, so remote callers never
+  reach it. The dashboard, `/`, and every `/api/*` route keep their session
+  checks.
 - **Known limitation:** tool calls are authorized at the transport level, not
   per argument — an admin whose `allowed_projects` is restricted can still pass
   any `project_root` to a tool. Admins are expected to hold the wildcard grant;
@@ -116,6 +118,9 @@ the tunnel goes live, then verify: `https://planner.example.com/mcp` → 404,
 - `tasks/` Markdown is the canonical source of truth; the planner is a derived
   index (`tasks/.plan/index.json`, gitignored) regenerated per turn.
 - Autopilot QA budget: max 1 unresolved QA/review task (general WIP ceiling 3).
+- `/mcp` trusts the bind and the tunnel ingress, not session auth: the
+  `^/mcp(/.*)?$ → 404` ingress rule must stay ahead of the catch-all, and the
+  port must never leave `127.0.0.1`. Breaking either exposes tool execution.
 - No external integrations in v1 (GitHub/Telegram/Asana/Plane deferred).
 - Zero-Autonomous-Commit: agents never `git commit`/`git push`; staging goes
   through `custom_context_stage_and_inject_diff`.
diff --git a/mcp-planner-server/server.py b/mcp-planner-server/server.py
index 7f70e3c..ffcd985 100644
--- a/mcp-planner-server/server.py
+++ b/mcp-planner-server/server.py
@@ -31,8 +31,10 @@ alongside the FastMCP StreamableHTTP endpoint on port 8108.
 Authentication (optional, off by default) lives in
 `~/.config/opencode/planner-users.json` (override with `PLANNER_USERS_CONFIG`).
 When `auth_enabled` is true the dashboard requires a session cookie from
-`POST /api/login`, `/api/status` filters the project list to the caller's
-`allowed_projects` (403 outside them), and `/mcp` accepts admin sessions only.
+`POST /api/login` and `/api/status` filters the project list to the caller's
+`allowed_projects` (403 outside them). The `/mcp` transport stays auth-free:
+loopback MCP clients connect without credentials, and the Cloudflare Tunnel
+ingress 404s `/mcp` before any remote request reaches it.
 With no config file — or `auth_enabled: false` — the server stays in open
 local mode, byte-identical to the pre-auth behaviour.
 
@@ -1400,49 +1402,20 @@ def _api_status(
 
 
 def _guarded_mcp_app(mcp_app):
-    """Wrap the MCP transport app with the admin-only ingress guard.
-
-    In open local mode the request passes straight through. When auth is
-    enabled, ``/mcp`` needs a valid session cookie *and* the admin role: a
-    viewer can read the dashboard but never execute tools.
+    """Wrap the MCP transport app at its trust boundary.
+
+    The transport is deliberately auth-free, in open mode and with auth
+    enabled alike: local OpenCode clients call ``/mcp`` on loopback with no
+    credentials and must connect. Remote exposure is closed at the network
+    edge instead — the Cloudflare Tunnel ingress answers 404 for ``/mcp``
+    before the catch-all rule, so the endpoint is never reachable off-host.
+    The dashboard and every ``/api/*`` route keep their session checks.
     """
 
-    async def guarded(scope, receive, send):
-        if scope.get("type") != "http" or not _AUTH_ENABLED:
-            await mcp_app(scope, receive, send)
-            return
-
-        headers = {
-            key.decode("latin-1").lower(): value.decode("latin-1")
-            for key, value in scope.get("headers") or []
-        }
-        token = _cookie_from_header(headers.get("cookie", ""), SESSION_COOKIE)
-        session = _session_from_token(token)
-        if session is None:
-            await _send_json(send, 401, {"error": "unauthenticated"})
-            return
-        if ((session.get("user") or {}).get("role") or "") != "admin":
-            await _send_json(send, 403, {"error": "forbidden"})
-            return
+    async def loopback_only(scope, receive, send):
         await mcp_app(scope, receive, send)
 
-    return guarded
-
-
-async def _send_json(send, status: int, payload: dict) -> None:
-    """Send a minimal JSON ASGI response (used by the /mcp guard)."""
-    body = json.dumps(payload).encode("utf-8")
-    await send(
-        {
-            "type": "http.response.start",
-            "status": status,
-            "headers": [
-                (b"content-type", b"application/json"),
-                (b"content-length", str(len(body)).encode("ascii")),
-            ],
-        }
-    )
-    await send({"type": "http.response.body", "body": body})
+    return loopback_only
 
 
 def build_app():
diff --git a/tests/test_planner_server.py b/tests/test_planner_server.py
index 1e082e9..cc7e2dd 100644
--- a/tests/test_planner_server.py
+++ b/tests/test_planner_server.py
@@ -907,37 +907,36 @@ def test_api_status_allowed_project_root_ok_for_viewer(auth_client, auth_app, tm
 
 
 # ---------------------------------------------------------------------------
-# Auth: /mcp ingress guard (admin only when auth is enabled)
+# Auth: /mcp transport stays open to loopback clients; /api/* stays guarded
 # ---------------------------------------------------------------------------
 
 
-def test_mcp_requires_session_when_auth_enabled(auth_client):
+def test_mcp_open_without_session_when_auth_enabled(auth_client):
+    # Local OpenCode clients send no cookie and must still reach the transport.
     resp = auth_client.post(
         "/mcp", content='{"jsonrpc":"2.0","method":"tools/list","id":1}'
     )
-    assert resp.status_code == 401
-    assert resp.json()["error"] == "unauthenticated"
+    assert resp.status_code not in (401, 403)
 
 
-def test_mcp_blocks_viewer_session(auth_client):
+def test_mcp_open_for_viewer_session(auth_client):
     auth_client.post(
         "/api/login", json={"username": "viewer", "password": "viewer-pass"}
     )
     resp = auth_client.post(
         "/mcp", content='{"jsonrpc":"2.0","method":"tools/list","id":1}'
     )
-    assert resp.status_code == 403
-    assert resp.json()["error"] == "forbidden"
+    assert resp.status_code not in (401, 403)
 
 
-def test_mcp_admits_admin_session(auth_client):
-    auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
-    resp = auth_client.post(
+def test_api_status_stays_guarded_while_mcp_is_open(auth_client):
+    # Same client, same auth-enabled app: /mcp passes, /api/status still 401.
+    mcp_resp = auth_client.post(
         "/mcp", content='{"jsonrpc":"2.0","method":"tools/list","id":1}'
     )
-    # The guard admits the request; the transport then rejects the malformed
-    # MCP handshake with its own status, which must not be a guard status.
-    assert resp.status_code not in (401, 403)
+    assert mcp_resp.status_code not in (401, 403)
+    assert auth_client.get("/api/status").status_code == 401
+    assert auth_client.get("/api/me").status_code == 401
 
 
 # ---------------------------------------------------------------------------
```
<!-- END_GIT_DIFF -->
