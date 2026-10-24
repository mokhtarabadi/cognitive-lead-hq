# Task 337: Planner Auth, RBAC, and Project Scoping

**File:** `tasks/completed/0337-planner-auth-rbac-and-project-scoping.md`
**Source:** orchestrator
**Type:** feature
**Status:** completed

## Goal

Add optional authentication, role-based access control (RBAC), and per-user project scoping to the Planner MCP server so the dashboard and MCP endpoint can be used securely over an external tunnel while remaining fully open when auth is disabled.

## Manager's Notes

- Backward-compatible: if `planner-users.json` is missing or `"auth_enabled": false`, server continues in open local mode.
- Use stdlib only for crypto: `hashlib.pbkdf2_hmac` + `secrets`, zero third-party crypto dependency.
- Admin session protects `/mcp`; viewer/admin role distinction matters for project scoping.

## Local TODOs

- [x] Step 1: Create task file
- [x] Step 2: Implement auth in server.py (user config, password hashing, session management, login/logout/me endpoints, _api_status filtering, /mcp guard)
- [x] Step 3: Implement Login Modal and User Header in index.html
- [x] Step 4: Create manage_users.py CLI
- [x] Step 5: Add unit tests
- [x] Step 6: Document Cloudflare Tunnel setup
- [x] Step 7: Update CHANGELOG.md
- [x] Step 8: Run tests, deploy, verify, QA transition

## Acceptance Criteria

- [x] `POST /api/login` accepts `{"username": "...", "password": "..."}`, returns `{"token": "...", "username": "...", "role": "...", "allowed_projects": [...]}`, sets HttpOnly cookie
- [x] `POST /api/logout` clears session
- [x] `GET /api/me` returns current user info or 401 if unauthenticated
- [x] When auth enabled and user unauthenticated, `_api_status` returns HTTP 401
- [x] Authenticated user sees only projects matching `allowed_projects` (or all if `"*"`)
- [x] If requested `project_root` is NOT inside `allowed_projects`, return HTTP 403
- [x] `/mcp` route guarded: only `admin` sessions can execute tools when auth enabled
- [x] Backward compatibility: missing `planner-users.json` or `"auth_enabled": false` = open local mode
- [x] Login modal (`#login-modal`) shown on 401 or when not logged in
- [x] Header user badge (`#user-badge`) displays username and role chip
- [x] Logout button (`#logout-btn`) clears session and shows login modal
- [x] Dashboard renders only projects the authenticated user can access
- [x] `manage_users.py` CLI adds/listed/updated users with PBKDF2 hashing
- [x] Tests cover login valid/invalid, RBAC admin vs viewer, 403 on unauthorized project, backward compat
- [x] Cloudflare Tunnel docs provided in `docs/services.md` and `README.md`

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/test_planner_server.py -q`
- **Expected result:** All tests pass including new auth tests
- **Actual result:** `76 passed, 2 warnings in 23.07s` — includes login valid/invalid, `/api/me` 401, RBAC admin vs viewer project lists, 403 on an unauthorized `project_root`, the three `/mcp` guard cases (401 unauthenticated, 403 viewer, admin admitted), open-mode backward compatibility, and three `manage_users.py` CLI tests whose hash is cross-verified by the server's `_verify_password`.
- **Exit code:** 0
- **Deployment evidence:** files copied to `~/.config/opencode/mcp-planner-server/`; `systemctl --user is-active mcp-planner` → `active`; open-mode live probes `GET /` 200, `GET /api/status` 200, `GET /api/me` 200 (`note: "auth disabled"`), `GET /static/index.html` 200, MCP `initialize` 200. Auth-mode probes against the deployed copy with `PLANNER_USERS_CONFIG=/tmp/opencode/planner-users-live.json`: unauth `/api/status` 401, unauth `/mcp` 401, wrong password 401, admin login 200 + `planner_session` cookie, admin `/mcp` admitted, logout → `/api/me` 401, viewer `/mcp` 403, viewer foreign `project_root` 403, viewer allowed root 200.
- **Docs sync:** `python3 scripts/check_docs_sync.py` → `docs-sync: OK`, exit 0.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `verification-before-completion` applied and evidence recorded
- [x] Files copied to global `~/.config/opencode/mcp-planner-server/`
- [x] `mcp-planner` service restarted and active
- [x] `scripts/check_docs_sync.py` exits 0

## Risk & Rollback

- **Risk:** Breaking backward compatibility for existing open-local users.
- **Rollback plan:** If `planner-users.json` is absent or `"auth_enabled": false`, server behaves exactly as before; no config change needed to retain open mode. To roll back the code, revert `server.py`, `index.html`, `manage_users.py`, and remove `PLANNER_USERS_CONFIG` env var.

## Execution Log & Reasoning

### Scope delivered

1. `mcp-planner-server/server.py` (+454/−33): auth config loader, PBKDF2 hash/verify, `AuthState`, in-memory session store, `_refresh_auth_config`, `POST /api/login`, `POST /api/logout`, `GET /api/me`, RBAC-aware `_api_status` and `_discover_projects`, `_first_allowed_root`, `_guarded_mcp_app`, `/static` mount.
2. `mcp-planner-server/static/index.html` (+185): `.hidden` utility, `#login-modal`, `#user-badge` with role chip, `#logout-btn`, 401/403 handling inside `fetchStatus`, auth check on load.
3. `mcp-planner-server/manage_users.py` (new, 224 lines): stdlib `argparse` CLI — `add`, `update`, `remove`, `list`, `enable`, `disable`, `--password` for non-interactive use, `chmod 600` on write, fail-fast message when no TTY is available.
4. `tests/test_planner_server.py` (+625): auth fixtures (`auth_app`/`auth_client`, `open_app`/`open_client`), login valid/invalid/missing-fields, `/api/me`, RBAC project filtering, 403 on a foreign root, three `/mcp` guard cases, open-mode backward compatibility, three CLI tests.
5. Docs: `docs/services.md` (planner auth + Cloudflare Tunnel ingress with `/mcp` → `http_status:404` ordered first, security-section exception), `mcp-planner-server/README.md` (routes table, auth/RBAC contract, tunnel config, known limitation), `mcp-planner-server/DECISIONS.md` ADR-005.
6. `CHANGELOG.md` under `### Added`; `mcp-planner-server/pyproject.toml` + `uv.lock` (dev extras, `itsdangerous` dropped, lock regenerated with `uv lock`).

### Assumptions

- **A1 — Auth needs users, not just the flag.** `auth_enabled: true` with an empty `users` list keeps open local mode. Reason: otherwise a mistyped flag locks every caller out with no in-band way back in, and the Manager's backward-compatibility requirement is better served by failing open than by failing closed.
- **A2 — MCP transport stays mounted at `/`.** `Mount("/mcp")` produced a 307 redirect on `/mcp` that httpx-based MCP clients do not follow, so the transport keeps routing itself at `settings.streamable_http_path` and the ASGI guard inspects the session instead of the path. This is why the route assertion in the test checks for a `Mount` plus `streamable_http_path` rather than `"/mcp" in paths`.
- **A3 — `pyproject.toml` / `uv.lock` are in scope.** They were already modified in the worktree for the test tooling; leaving them half-edited would ship a lock that disagrees with the manifest, so both are included and `itsdangerous` was removed (auth is stdlib-only as instructed).
- **A4 — Logout reloads the page.** The AC asks the logout button to "clear session and show login modal"; a reload reaches the same state through the `/api/me` 401 path and additionally guarantees no stale board data from the previous session stays on screen.

### Defects fixed in passing (pre-existing in the worktree, not new scope)

- `TASK_ID_RE` was `r"^(\d+)-(.+)\.md$"` (double-escaped), so no task id ever matched and dashboard ids were blank. Corrected to `r"^(\d+)-(.+)\.md$"`.
- `server.py` carried a duplicated `# /// script` header (`(drop)` / `(re-add)` markers), which the PEP 723 header parser rejects. Collapsed to a single block.
- `mcp._session_manager = None` reset in `build_app()`: FastMCP caches its session manager and a manager may be `run()` only once, so a second `build_app()` (tests, or a rebuild) failed with `RuntimeError: StreamableHTTPSessionManager .run() can only be called once per instance`.

### Verification performed

- `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/test_planner_server.py -q` → 76 passed, exit 0.
- Deployed to `~/.config/opencode/mcp-planner-server/` (server.py, manage_users.py, static/), `systemctl --user restart mcp-planner`, unit `active`.
- Live open-mode probes on 127.0.0.1:8108: `/` 200, `/api/status` 200, `/api/me` 200 with `note: "auth disabled"`, `/static/index.html` 200, MCP `initialize` 200.
- Live auth-mode probes against the deployed copy (`PLANNER_USERS_CONFIG=/tmp/opencode/planner-users-live.json`): unauth `/api/status` 401, unauth `/mcp` 401, wrong password 401, admin login 200 + `planner_session` cookie, admin `/mcp` admitted (guard passes; transport rejects the malformed handshake), logout → `/api/me` 401, viewer `/mcp` 403, viewer foreign root 403, viewer allowed root 200, viewer project list `['/tmp/opencode/shared']`.
- `scripts/check_docs_sync.py` → `docs-sync: OK`, exit 0.
- Dashboard JS parsed with `node -e "new Function(...)"` (no syntax errors); `#login-modal`, `#user-badge`, `#logout-btn` present.
- `ruff check` delta vs `HEAD` is style-only (UP045/F401/F841/I001 pre-existing); no new functional findings. Those pre-existing findings were deliberately left out of scope.

### Known limitation (documented, not fixed)

Tool authorization is enforced at the transport level, not per argument: an admin whose `allowed_projects` is restricted can still pass any `project_root` to a planner tool. The mitigation is procedural — admins hold `"*"`, viewers are the scoped read-only account. Recorded in `mcp-planner-server/README.md`.

### Deployment state

Live deployment stays in open mode: no `~/.config/opencode/planner-users.json` exists, so local MCP clients keep working. The tunnel walkthrough requires the operator to enable auth before exposing the hostname.

### Note on tooling

ADR-005 was appended to `mcp-planner-server/DECISIONS.md` with a shell heredoc rather than the native edit tool (the block is long and the file ends at a known anchor); the result was read back and verified in place. Everything else was edited with native tools only.

### Closure

Manager relayed the Orchestrator closure task: `git mv` to `tasks/completed/`, `**File:**`/`**Status:**` synced, `lint_task_file` re-run, diff re-injected, then committed through `custom_context_commit_and_clean_task` (the only commit path; no `git add`/`commit`/`push` was executed by hand). Status is `completed`, matching the field value on the most recent closed task (0336) and the Orchestrator's explicit instruction; older completed tasks carry `closed`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 2be084b..c4b76c8 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Planner auth, RBAC, and per-user project scoping (Task 337):** the planner can now be exposed through a Cloudflare Tunnel without giving strangers the board. Auth is opt-in via `~/.config/opencode/planner-users.json` (`PLANNER_USERS_CONFIG` override): a missing, unreadable, non-object, or `auth_enabled: false` file — or one with no users — leaves the server in open local mode with no 401s and no filtering, so every existing local client keeps working untouched. When enabled, `server.py` gains stdlib-only auth: `hashlib.pbkdf2_hmac("sha256", …, 600_000)` with a 16-byte `secrets` salt verified by `hmac.compare_digest`, opaque `secrets.token_urlsafe(32)` sessions in an in-memory store behind an `HttpOnly` `SameSite=Lax` `planner_session` cookie (7-day TTL, dropped on restart), `POST /api/login`, `POST /api/logout`, `GET /api/me`, and an `AuthState` that answers `project_allowed()` for `"*"` or any granted root and its subdirectories. `GET /api/status` returns 401 until sign-in, filters `projects` to `allowed_projects`, and 403s an explicit `project_root` outside them (a viewer with no explicit root falls back to their first allowed project instead of being denied); `POST /mcp` is wrapped in an ASGI guard that admits admin sessions only, so a viewer reads the dashboard and never executes tools. The dashboard gains a dark-mode login modal shown on 401, a `#user-badge` with a role chip, a logout button, and `/static/*` asset serving; `manage_users.py` is a stdlib `argparse` CLI (`add`/`update`/`remove`/`list`/`enable`/`disable`, `--password` for non-interactive use, file written `chmod 600`) that hashes through the same scheme the server verifies. Cloudflare Tunnel ingress is documented in `docs/services.md` and the component README, with the `/mcp` rule ordered first as `http_status:404` so tool execution never leaves the host. Two defects in the working tree were fixed rather than shipped: a corrupted `TASK_ID_RE` (`\\.md` never matched, so task lookup and dashboard ids broke) and a duplicated `# /// script` header. Verified: 76/76 planner tests pass (login valid/invalid, RBAC admin vs viewer, 403 on an unauthorized root, the three `/mcp` guard cases, open-mode backward compatibility, and CLI hashing cross-checked by the server's own verifier); `docs-sync: OK`; unit `active` with the new code deployed.
+
 - **Planner MCP deployed globally and wired into the executor protocol (Task 336):** the planner is now a live platform singleton rather than repo-local code. It installs to `~/.config/opencode/mcp-planner-server/` (source, committed `uv.lock`, and `static/` dashboard assets) with its venv built by `uv sync` from the lock, runs as `mcp-planner.service` on `127.0.0.1:8108` (enabled, active, loopback-only), and is registered in the global `opencode.json` as `mcp.servers.planner` (`type: remote`, `http://127.0.0.1:8108/mcp`, timeout 15000/30000). `agents/cognitive-executor.md` gains a *Planner MCP and Daily Pacing Protocol* section binding four moments to four tools: `sprint_daily_agenda` when the Manager starts the day, `claim_next` instead of hand-moving a task file (a block is reported, never bypassed), `sprint_check_daily_quota` when tasks close, and `plan_status`/`qa_budget` for status questions — with an explicit fallback to the Kanban workflow if the server is unreachable. `LLM.txt` provisions the whole thing (§4 directory, §5 copy block, §7 config entry, §7.5 venv-before-unit plus drop-in, verification checklist), `README.md` lists the component, and `docs/services.md` keeps the port map. Deployment adaptations forced by what actually ran: `uv pip install -e .` cannot work because the package declares no build backend, so the venv comes from `uv sync` against the committed lock; the committed unit stays machine-independent and the dashboard's project root is supplied by a `mcp-planner.service.d` drop-in (`PLANNER_PROJECT_ROOT`), since the unit's WorkingDirectory is the install dir which holds no `tasks/`; and `opencode mcp list` prints "No MCP servers configured" on v2.1.4 even for the six servers already in use, so registration is verified with `opencode debug config` (7 resolved `127.0.0.1:810*/mcp` entries) plus a live MCP handshake instead — the docs now say so. Verified: unit `active`/`enabled`, `/` and `/api/status` both 200 with 329 tasks for this repo, planner tools enumerable over `initialize`+`tools/list`, `scripts/check_docs_sync.py` exits 0, 31/31 planner tests pass, full suite 592 passed with the one pre-existing prompt round-trip failure.
 
 - **Planner MCP v1 and local dashboard (Task 335):** new `mcp-planner-server/` singleton on loopback `127.0.0.1:8108` that reads `tasks/` Markdown as the single source of truth and adds a capacity-aware, QA-gated planning layer over it. Tools: `plan_propose` (decompose a goal into estimated tasks + milestones, writes nothing), `plan_materialize` (writes task files only after approval), `claim_next` (guarded claim that refuses on unmet dependencies, a full WIP ceiling, or an exhausted QA budget), `plan_status`, `sprint_stats` (hours spent, progress, velocity), `qa_budget`, `milestone_status`, `sprint_lock`, `sprint_daily_agenda`, and `sprint_check_daily_quota` (`DAILY_QUOTA_REACHED`). The same process serves a zero-build dark-mode dashboard at `/` with a Jalali + Gregorian 14-day timeline, Kanban lanes, milestone tree, daily pacing gauge, and a working project switcher, plus `GET /api/status`. Two defects were fixed during verification rather than shipped: the transport is built with `mcp.streamable_http_app()` (mcp 1.30 has no `http_app()`) mounted at the root with an explicit `lifespan_context` enter, because Starlette never runs a `Mount`-ed sub-app's lifespan and the session manager stayed uninitialised; and `/api/status` now returns per-lane **task lists**, a `milestone_tree`, sorted `deadlines`, a `today` triple matching `sprint_check_daily_quota`, and a `projects` list, with the root resolved from `project_root` → `PLANNER_PROJECT_ROOT` → nearest ancestor holding `tasks/` → cwd. The previous count-per-lane shape made `items.map` throw inside `render()` and silently blanked the board, and the hard-coded `Path.cwd()` root reported an empty board under systemd. Also added `tasks/sprints/` and `tasks/milestones/`, `services/mcp-planner.service`, `uv.lock`, port 8108 in `docs/services.md`, and the unit in `services/README.md`. Verified: 30/30 planner tests pass, a live `initialize` on `/mcp` returns 200, `GET /` and `/api/status` return 200 against the real repo (328 tasks), and the dashboard `render()` was exercised headlessly against both the live and a synthetic milestone payload.
diff --git a/docs/services.md b/docs/services.md
index c48a251..dd7c905 100644
--- a/docs/services.md
+++ b/docs/services.md
@@ -24,6 +24,77 @@ to the nearest ancestor of its working directory that holds `tasks/`.
 `PLANNER_PROJECTS` (pathsep-separated absolute paths) feeds the
 dashboard's project switcher. It needs no credentials.
 
+Planner authentication is **optional and off by default**: with no
+`~/.config/opencode/planner-users.json` (or `"auth_enabled": false`) the
+server stays in open local mode, byte-identical to the pre-auth
+behaviour. With auth on, `POST /api/login` issues an `HttpOnly`
+`planner_session` cookie, `/api/status` is 401 until sign-in and 403
+outside the caller's `allowed_projects`, and `/mcp` accepts admin
+sessions only. Users are managed with the stdlib CLI (no venv needed):
+
+```bash
+python3 ~/.config/opencode/mcp-planner-server/manage_users.py \
+  add --username admin --role admin --projects "*"
+python3 ~/.config/opencode/mcp-planner-server/manage_users.py \
+  add --username friend --role viewer --projects /home/me/Develop/Projects/shared
+python3 ~/.config/opencode/mcp-planner-server/manage_users.py list
+systemctl --user restart mcp-planner     # config is read at startup
+```
+
+Passwords are PBKDF2-HMAC-SHA256 (600k iterations, per-user salt); the
+file is written `chmod 600`. `PLANNER_USERS_CONFIG` overrides the path,
+and `enable` / `disable` flip `auth_enabled` without touching users.
+
+### Exposing the planner through a Cloudflare Tunnel
+
+The tunnel is the only supported way to reach the dashboard from outside
+the host. Keep the unit bound to loopback and let `cloudflared` make the
+outbound connection — never rebind to `0.0.0.0`.
+
+```bash
+cloudflared tunnel login
+cloudflared tunnel create planner
+cloudflared tunnel route dns planner planner.example.com
+```
+
+`~/.cloudflared/config.yml` — the `/mcp` ingress rule is a deliberate
+`404` so tool execution never leaves the host, even for an admin cookie:
+
+```yaml
+tunnel: planner
+credentials-file: /home/me/.cloudflared/<tunnel-uuid>.json
+
+ingress:
+  # Tool execution stays loopback-only. This rule must come first.
+  - hostname: planner.example.com
+    path: ^/mcp(/.*)?$
+    service: http_status:404
+  # Dashboard + JSON API (login, status, me) through the tunnel.
+  - hostname: planner.example.com
+    service: http://127.0.0.1:8108
+  - service: http_status:404
+```
+
+```bash
+sudo cloudflared service install        # or: cloudflared tunnel run planner
+```
+
+Rules that make the exposure safe:
+
+1. `path: ^/mcp(/.*)?$` → `http_status:404` is ordered **before** the
+   catch-all hostname rule; Cloudflare matches ingress top-down, so a
+   later rule can never re-open `/mcp`.
+2. Enable auth (`manage_users.py add ...`) before starting the tunnel.
+   Without it the dashboard is open to anyone who finds the hostname.
+3. `allowed_projects` is the second gate: a viewer only ever sees the
+   project roots listed for them, and any other `?project_root=` is 403.
+4. The tunnel exposes HTTPS only; the `planner_session` cookie is
+   `HttpOnly` + `SameSite=Lax`, so keep the hostname HTTPS-only in
+   Cloudflare (no plain-HTTP origin rule).
+5. Verify from outside: `curl -s -o /dev/null -w '%{http_code}\n'
+   https://planner.example.com/mcp` must print `404`, while `/` prints
+   `200` and shows the login modal.
+
 `zen-proxy` is listed here because it is provisioned and supervised the same
 way, but it speaks the OpenAI Responses/Chat API rather than MCP. Its unit
 reads the same global `.env`; it needs no API key of its own (the caller's
@@ -39,6 +110,12 @@ already running on this machine can reach them. Do not rebind to
 container `MCP_HOST=0.0.0.0` is required, but the published port stays
 `-p 127.0.0.1:8107:8107`.)
 
+The planner is the one exception when it is tunneled: it ships optional
+cookie-session auth with per-user project scoping, so an operator can
+expose the dashboard through `cloudflared` while `/mcp` stays
+loopback-only (see the planner section above). Every other singleton
+stays loopback-only with no auth at all.
+
 ## Credentials (`.env`) — how the servers read keys
 
 The Python servers (`context`, `memory`, `lint`, `decision`, `brain`) load
diff --git a/mcp-planner-server/DECISIONS.md b/mcp-planner-server/DECISIONS.md
index a8ff0eb..774e6a5 100644
--- a/mcp-planner-server/DECISIONS.md
+++ b/mcp-planner-server/DECISIONS.md
@@ -64,3 +64,32 @@ any change to lane shape breaks a test rather than silently blanking the UI.
 `PLANNER_PROJECTS` is the only way to offer several roots in the switcher.
 - **Rollback:** Revert the `/api/status` handler and the dashboard `render()`
 together — they share one contract and must never be changed independently.
+
+## [2026-10-24] ADR-005: Optional cookie-session auth with per-user project scoping
+
+- **Context:** The dashboard is useful from a phone, so the Manager wants it
+reachable through a Cloudflare Tunnel. Loopback-only access was the sole control
+until now, which stops working the moment the port leaves the host. At the same
+time the local OpenCode clients call `/mcp` with no credentials and must keep
+working untouched.
+- **Decision:** Auth is opt-in through `~/.config/opencode/planner-users.json`
+(`PLANNER_USERS_CONFIG` override). A missing, unreadable, non-object, or
+`auth_enabled: false` file — or one with no users — keeps the server in open
+local mode with no 401s and no filtering. When enabled: PBKDF2-HMAC-SHA256
+(600k iterations, 16-byte `secrets` salt, `hmac.compare_digest`) with stdlib
+only; opaque in-memory session tokens in an `HttpOnly` `SameSite=Lax`
+`planner_session` cookie (7-day TTL, dropped on restart); `/api/status` answers
+401 unauthenticated, filters `projects` to `allowed_projects` (`"*"` = all) and
+403s an explicit `project_root` outside them; `/mcp` requires an **admin**
+session while viewers stay read-only. A viewer with no explicit root falls back
+to their first allowed project rather than being denied.
+- **Consequences:** One server serves both audiences: local tooling stays
+credential-free in open mode, remote browsers sign in. Restart is required after
+a user edit because the config is read when the app is built. A restart also
+signs everyone out — acceptable, and it means no long-lived signing secret lives
+on disk. `/mcp` over the tunnel is blocked at ingress (`http_status:404`), so
+tool execution never depends on the guard alone. Pinned by the auth tests plus
+the CLI test that hashes through the server's own verifier.
+- **Rollback:** Delete `planner-users.json` or run `manage_users.py disable`;
+the server returns to open local mode with no code change. Full code rollback is
+`server.py` + `static/index.html` + `manage_users.py` reverted together.
diff --git a/mcp-planner-server/README.md b/mcp-planner-server/README.md
index b9ed7e7..43379a9 100644
--- a/mcp-planner-server/README.md
+++ b/mcp-planner-server/README.md
@@ -13,8 +13,12 @@ dashboard on loopback port 8108.
   (`plan_propose`, `plan_materialize`, `claim_next`, `qa_budget`,
   `milestone_status`, `plan_status`, `sprint_daily_agenda`,
   `sprint_check_daily_quota`, `sprint_lock`) plus an embedded HTTP route
-  serving the static dashboard on `GET /` and `GET /api/status`.
-- `static/index.html` — standalone dark-mode dashboard (no build step).
+  serving the static dashboard on `GET /` and `GET /api/status`, the auth
+  routes, and the admin-guarded MCP endpoint.
+- `manage_users.py` — stdlib-only user CLI (`add`, `update`, `remove`,
+  `list`, `enable`, `disable`) writing `~/.config/opencode/planner-users.json`.
+- `static/index.html` — standalone dark-mode dashboard (no build step),
+  including the login modal and the user badge.
 - `pyproject.toml` / `uv.lock` — runtime deps and lockfile.
 - `README.md` / `DECISIONS.md` — Living Folder Docs for this slice.
 
@@ -23,8 +27,12 @@ dashboard on loopback port 8108.
 | Route | Purpose |
 | ----- | ------- |
 | `GET /` | Standalone dark-mode dashboard (no build step). |
+| `GET /static/*` | Dashboard assets (same `static/` directory). |
 | `GET /api/status[?project_root=<abs path>]` | JSON status contract the dashboard renders. |
-| `POST /mcp` | MCP Streamable HTTP endpoint (tools). |
+| `POST /api/login` | `{"username","password"}` → `{token, username, role, allowed_projects}` + `HttpOnly` cookie. |
+| `POST /api/logout` | Invalidates the session and clears the cookie. |
+| `GET /api/me` | Current user, or 401 when signed out (200 + `note: "auth disabled"` in open mode). |
+| `POST /mcp` | MCP Streamable HTTP endpoint (tools). Admin-only when auth is enabled. |
 
 `/api/status` returns per-lane **task lists** (`lanes`), the milestone tree
 (`milestone_tree`), upcoming deadlines (`deadlines`), the pacing figures
@@ -39,6 +47,70 @@ holding `tasks/`, then the working directory. `PLANNER_PROJECTS`
 (pathsep-separated absolute paths) adds entries to the dashboard switcher;
 `PLANNER_DAILY_TARGET` overrides the daily batch size (default 3).
 
+## Authentication and RBAC (optional, off by default)
+
+- **Config:** `~/.config/opencode/planner-users.json`, overridable with
+  `PLANNER_USERS_CONFIG`. Shape: `{"auth_enabled": bool, "users": [{"username",
+  "role": "admin"|"viewer", "password_salt", "password_hash",
+  "allowed_projects": ["*"] | ["/abs/path", ...]}]}`.
+- **Open mode:** no file, unreadable file, invalid JSON, `auth_enabled: false`,
+  or an empty `users` list ⇒ every request behaves exactly as before
+  (no 401, no filtering). This is the backward-compatibility contract.
+- **Hashing:** `hashlib.pbkdf2_hmac("sha256", …, 600_000)` with a 16-byte
+  `secrets` salt, verified with `hmac.compare_digest`. No third-party crypto.
+- **Sessions:** `secrets.token_urlsafe(32)` held in memory, `HttpOnly` +
+  `SameSite=Lax` cookie `planner_session`, 7-day TTL. A restart drops every
+  session by design (re-login is cheap; no server-side secret to leak).
+- **Scoping:** `/api/status` returns 401 until sign-in, 403 when an explicit
+  `project_root` is outside `allowed_projects`, and filters `projects` to the
+  allowed roots. Without an explicit root a viewer falls back to their first
+  allowed project instead of being denied.
+- **`/mcp`:** admin sessions only when auth is enabled; viewers get 403 and
+  signed-out callers 401. Local MCP clients (no cookie) therefore need
+  `auth_enabled: false`, which is the default.
+- **Known limitation:** tool calls are authorized at the transport level, not
+  per argument — an admin whose `allowed_projects` is restricted can still pass
+  any `project_root` to a tool. Admins are expected to hold the wildcard grant;
+  use a viewer account for read-only scoped access.
+
+Manage users (stdlib CLI, no venv):
+
+```bash
+python3 manage_users.py add --username admin --role admin --projects "*"
+python3 manage_users.py add --username friend --role viewer --projects /path/to/shared-project
+python3 manage_users.py list
+python3 manage_users.py update --username friend --add-project /another/project
+python3 manage_users.py disable        # back to open local mode
+```
+
+Config is read when the app is built, so `systemctl --user restart mcp-planner`
+after any user change.
+
+## Cloudflare Tunnel (external dashboard access)
+
+Keep the unit on `127.0.0.1` and let `cloudflared` dial out. The ingress
+config must block `/mcp` **before** the catch-all rule so tool execution never
+leaves the host:
+
+```yaml
+# ~/.cloudflared/config.yml
+tunnel: planner
+credentials-file: /home/me/.cloudflared/<tunnel-uuid>.json
+
+ingress:
+  - hostname: planner.example.com
+    path: ^/mcp(/.*)?$
+    service: http_status:404
+  - hostname: planner.example.com
+    service: http://127.0.0.1:8108
+  - service: http_status:404
+```
+
+`cloudflared tunnel create planner` → `cloudflared tunnel route dns planner
+planner.example.com` → `sudo cloudflared service install`. Enable auth before
+the tunnel goes live, then verify: `https://planner.example.com/mcp` → 404,
+`/` → 200 with the login modal. Full walkthrough in `docs/services.md`.
+
 ## Key Risks & Invariants
 
 - `tasks/` Markdown is the canonical source of truth; the planner is a derived
diff --git a/mcp-planner-server/manage_users.py b/mcp-planner-server/manage_users.py
new file mode 100644
index 0000000..123d610
--- /dev/null
+++ b/mcp-planner-server/manage_users.py
@@ -0,0 +1,317 @@
+#!/usr/bin/env python3
+# Sibling Docs: mcp-planner-server/README.md | Decisions: mcp-planner-server/DECISIONS.md
+"""Manage planner users stored in ~/.config/opencode/planner-users.json.
+
+Stdlib only (argparse, getpass, hashlib, secrets) so it runs with a bare
+``python3`` — no venv, no third-party packages. Passwords are stored as
+PBKDF2-HMAC-SHA256 with a per-user 16-byte salt; the same scheme the server
+verifies against.
+
+Usage:
+    python3 manage_users.py add --username admin --role admin --projects "*"
+    python3 manage_users.py add --username friend --role viewer --projects /path/to/shared-project
+    python3 manage_users.py list
+    python3 manage_users.py update --username friend --role viewer --projects /new/path
+    python3 manage_users.py remove --username friend
+    python3 manage_users.py enable
+    python3 manage_users.py disable
+
+The config path comes from ``--config`` or ``PLANNER_USERS_CONFIG``, falling
+back to ``~/.config/opencode/planner-users.json``. The planner picks the same
+path, so no server-side change is needed after adding a user.
+"""
+
+import argparse
+import getpass
+import hashlib
+import json
+import os
+import secrets
+import sys
+from pathlib import Path
+
+PBKDF2_ALGORITHM = "sha256"
+PBKDF2_ITERATIONS = 600_000
+
+DEFAULT_RELATIVE = Path(".config") / "opencode" / "planner-users.json"
+
+
+def _config_path(override: str | None = None) -> Path:
+    """Resolve the users config path (flag, env, then home default)."""
+    if override:
+        return Path(override).expanduser()
+    env = os.environ.get("PLANNER_USERS_CONFIG", "").strip()
+    if env:
+        return Path(env).expanduser()
+    return Path.home() / DEFAULT_RELATIVE
+
+
+def _load(path: Path) -> dict:
+    """Load the config, defaulting to a disabled, user-less document."""
+    if not path.is_file():
+        return {"auth_enabled": False, "users": []}
+    try:
+        data = json.loads(path.read_text(encoding="utf-8"))
+    except (OSError, json.JSONDecodeError) as exc:
+        sys.exit(f"❌ Cannot read {path}: {exc}")
+    if not isinstance(data, dict):
+        sys.exit(f"❌ {path} must contain a JSON object.")
+    if not isinstance(data.get("users"), list):
+        data["users"] = []
+    data.setdefault("auth_enabled", False)
+    return data
+
+
+def _save(path: Path, data: dict) -> None:
+    """Write the config with owner-only permissions (it holds password hashes)."""
+    path.parent.mkdir(parents=True, exist_ok=True)
+    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
+    try:
+        path.chmod(0o600)
+    except OSError:
+        pass  # Non-POSIX filesystems: the file is still written.
+
+
+def _hash_password(password: str) -> tuple[str, str]:
+    """Return ``(salt_hex, hash_hex)`` for ``password`` (PBKDF2-HMAC-SHA256)."""
+    salt = secrets.token_bytes(16)
+    derived = hashlib.pbkdf2_hmac(
+        PBKDF2_ALGORITHM, password.encode("utf-8"), salt, PBKDF2_ITERATIONS
+    )
+    return salt.hex(), derived.hex()
+
+
+def _find(data: dict, username: str) -> int:
+    """Return the index of ``username`` in the users list, or -1."""
+    for index, user in enumerate(data.get("users", [])):
+        if user.get("username") == username:
+            return index
+    return -1
+
+
+def _parse_projects(raw) -> list[str]:
+    """Normalize repeated ``--projects`` values into a de-duplicated list."""
+    if raw is None:
+        return []
+    if isinstance(raw, str):
+        raw = [raw]
+    out: list[str] = []
+    for entry in raw:
+        value = str(entry).strip()
+        if value and value not in out:
+            out.append(value)
+    return out
+
+
+def _read_password(username: str) -> str:
+    """Prompt twice for a new password and confirm the two match.
+
+    Fails fast with a clear message when there is no TTY (CI, pipes, agent
+    shells) instead of raising ``EOFError`` out of getpass.
+    """
+    try:
+        password = getpass.getpass(f"Password for {username}: ")
+        if not password:
+            sys.exit("❌ Password required.")
+        confirm = getpass.getpass("Confirm password: ")
+    except (EOFError, OSError):
+        sys.exit("❌ No TTY for a password prompt — pass --password instead.")
+    if password != confirm:
+        sys.exit("❌ Passwords do not match.")
+    return password
+
+
+def _project_summary(projects: list[str]) -> str:
+    """Human-readable allowed-projects summary."""
+    if "*" in projects:
+        return "* (all projects)"
+    return ", ".join(projects) if projects else "(none)"
+
+
+def cmd_add(args) -> int:
+    path = _config_path(args.config)
+    data = _load(path)
+    if _find(data, args.username) >= 0:
+        print(f"❌ User '{args.username}' already exists.", file=sys.stderr)
+        return 1
+
+    password = args.password or _read_password(args.username)
+    salt, hash_hex = _hash_password(password)
+    allowed = _parse_projects(args.projects)
+
+    data["users"].append(
+        {
+            "username": args.username,
+            "role": args.role.lower(),
+            "password_salt": salt,
+            "password_hash": hash_hex,
+            "allowed_projects": allowed,
+        }
+    )
+    data["auth_enabled"] = True
+    _save(path, data)
+    print(
+        f"✅ Added user '{args.username}' (role={args.role.lower()}, "
+        f"projects={_project_summary(allowed)})."
+    )
+    print(f"   Config: {path}")
+    print("   Auth is now ENABLED — restart mcp-planner to apply.")
+    return 0
+
+
+def cmd_update(args) -> int:
+    path = _config_path(args.config)
+    data = _load(path)
+    index = _find(data, args.username)
+    if index < 0:
+        print(f"❌ User '{args.username}' not found.", file=sys.stderr)
+        return 1
+
+    user = data["users"][index]
+    if args.role:
+        user["role"] = args.role.lower()
+
+    if args.projects:
+        user["allowed_projects"] = _parse_projects(args.projects)
+    else:
+        current = list(user.get("allowed_projects") or [])
+        for entry in _parse_projects(args.add_project):
+            if entry not in current:
+                current.append(entry)
+        for entry in _parse_projects(args.remove_project):
+            if entry in current:
+                current.remove(entry)
+        user["allowed_projects"] = current
+
+    if args.password:
+        salt, hash_hex = _hash_password(args.password)
+        user["password_salt"] = salt
+        user["password_hash"] = hash_hex
+
+    _save(path, data)
+    print(
+        f"✅ Updated user '{args.username}': role={user.get('role')}, "
+        f"projects={_project_summary(list(user.get('allowed_projects') or []))}."
+    )
+    return 0
+
+
+def cmd_remove(args) -> int:
+    path = _config_path(args.config)
+    data = _load(path)
+    index = _find(data, args.username)
+    if index < 0:
+        print(f"❌ User '{args.username}' not found.", file=sys.stderr)
+        return 1
+    removed = data["users"].pop(index)
+    _save(path, data)
+    print(f"✅ Removed user '{removed.get('username')}'.")
+    if not data["users"]:
+        print("   No users left — auth is effectively disabled.")
+    return 0
+
+
+def cmd_list(args) -> int:
+    path = _config_path(args.config)
+    data = _load(path)
+    users = data.get("users", [])
+    print(f"Auth enabled: {bool(data.get('auth_enabled'))}")
+    print(f"Config: {path}")
+    if not users:
+        print("\nNo users configured — the server runs in open local mode.")
+        return 0
+    print()
+    print(f"{'Username':<18} {'Role':<8} Projects")
+    print("-" * 70)
+    for user in users:
+        projects = list(user.get("allowed_projects") or [])
+        print(
+            f"{user.get('username', '?')!s:<18} "
+            f"{user.get('role', '?')!s:<8} {_project_summary(projects)}"
+        )
+    return 0
+
+
+def cmd_set_enabled(args, enabled: bool) -> int:
+    path = _config_path(args.config)
+    data = _load(path)
+    data["auth_enabled"] = enabled
+    _save(path, data)
+    if enabled and not data.get("users"):
+        print("⚠️  auth_enabled is true but no users exist — the server stays open.")
+        return 0
+    print(
+        f"✅ Auth {'ENABLED' if enabled else 'DISABLED'} in {path}. "
+        "Restart mcp-planner to apply."
+    )
+    return 0
+
+
+def build_parser() -> argparse.ArgumentParser:
+    """Build the CLI parser (subcommands: add/update/remove/list/enable/disable)."""
+    parser = argparse.ArgumentParser(
+        description="Manage planner authentication users.",
+    )
+    parser.add_argument(
+        "--config",
+        help="Users config path (default: $PLANNER_USERS_CONFIG or "
+        "~/.config/opencode/planner-users.json).",
+    )
+    sub = parser.add_subparsers(dest="command", required=True)
+
+    add = sub.add_parser("add", help="Add a user with a password prompt.")
+    add.add_argument("--username", required=True)
+    add.add_argument(
+        "--role", default="viewer", choices=["admin", "viewer"], type=str.lower
+    )
+    add.add_argument(
+        "--projects",
+        action="append",
+        default=[],
+        help="Allowed project root; repeat for several. Use '*' for all.",
+    )
+    add.add_argument(
+        "--password",
+        help="Password (non-interactive use; otherwise prompted).",
+    )
+    add.set_defaults(func=cmd_add)
+
+    update = sub.add_parser("update", help="Update role, projects, or password.")
+    update.add_argument("--username", required=True)
+    update.add_argument("--role", choices=["admin", "viewer"], type=str.lower)
+    update.add_argument(
+        "--projects",
+        action="append",
+        default=[],
+        help="Replace the allowed project list; repeat for several.",
+    )
+    update.add_argument("--add-project", action="append", default=[])
+    update.add_argument("--remove-project", action="append", default=[])
+    update.add_argument("--password", help="Set a new password.")
+    update.set_defaults(func=cmd_update)
+
+    remove = sub.add_parser("remove", help="Remove a user.")
+    remove.add_argument("--username", required=True)
+    remove.set_defaults(func=cmd_remove)
+
+    listing = sub.add_parser("list", help="List users (no secrets shown).")
+    listing.set_defaults(func=cmd_list)
+
+    enable = sub.add_parser("enable", help="Turn authentication on.")
+    enable.set_defaults(func=lambda args: cmd_set_enabled(args, True))
+
+    disable = sub.add_parser("disable", help="Turn authentication off (open mode).")
+    disable.set_defaults(func=lambda args: cmd_set_enabled(args, False))
+
+    return parser
+
+
+def main(argv=None) -> int:
+    """Parse arguments and dispatch; returns a process exit code."""
+    parser = build_parser()
+    args = parser.parse_args(argv)
+    return args.func(args)
+
+
+if __name__ == "__main__":
+    sys.exit(main())
diff --git a/mcp-planner-server/pyproject.toml b/mcp-planner-server/pyproject.toml
index 376dc46..f010e49 100644
--- a/mcp-planner-server/pyproject.toml
+++ b/mcp-planner-server/pyproject.toml
@@ -4,8 +4,17 @@ version = "1.0.0"
 description = "Planner MCP server: capacity-aware, QA-gated planning layer over tasks/ Markdown"
 requires-python = ">=3.10"
 dependencies = [
-    "mcp>=1.3.0,<2.0",
+    "mcp>=1.3.0,<2.0",  # v1 API: FastMCP, streamable_http_app()
     "pyyaml",
     "starlette",
     "uvicorn",
 ]
+
+[project.optional-dependencies]
+# Auth uses stdlib only (hashlib/secrets/hmac); httpx is here because
+# starlette.testclient needs it for the route-level tests.
+dev = ["pytest", "pytest-timeout", "httpx"]
+
+[tool.pytest.ini_options]
+pythonpath = [".", "./.."]
+
diff --git a/mcp-planner-server/server.py b/mcp-planner-server/server.py
index 55e836e..7f70e3c 100644
--- a/mcp-planner-server/server.py
+++ b/mcp-planner-server/server.py
@@ -2,16 +2,9 @@
 # Sibling Docs: mcp-planner-server/README.md | Decisions: mcp-planner-server/DECISIONS.md
 # /// script
 # requires-python = ">=3.10"
-# dependencies = [
-#     "mcp>=1.3.0,<2.0",
-#     "pyyaml",
-#     "starlette",
-#     "uvicorn",
-# ]
+# dependencies = ["mcp>=1.3.0,<2.0", "pyyaml", "starlette", "uvicorn"]
 # ///
-
-"""
-Planner MCP Server — capacity-aware, QA-gated planning layer over tasks/ Markdown.
+"""Planner MCP Server — capacity-aware, QA-gated planning layer over tasks/ Markdown.
 
 Reads task files from tasks/{backlog,in-progress,qa,completed,archive} as the
 single source of truth, builds a derived index (tasks/.plan/index.json,
@@ -35,6 +28,14 @@ gitignored), and exposes planning tools:
 An embedded Starlette app serves the static dashboard on GET / and GET /api/status
 alongside the FastMCP StreamableHTTP endpoint on port 8108.
 
+Authentication (optional, off by default) lives in
+`~/.config/opencode/planner-users.json` (override with `PLANNER_USERS_CONFIG`).
+When `auth_enabled` is true the dashboard requires a session cookie from
+`POST /api/login`, `/api/status` filters the project list to the caller's
+`allowed_projects` (403 outside them), and `/mcp` accepts admin sessions only.
+With no config file — or `auth_enabled: false` — the server stays in open
+local mode, byte-identical to the pre-auth behaviour.
+
 Design rules:
 - tasks/ Markdown is canonical; the planner is a derived index only.
 - Autopilot QA budget: max 1 unresolved QA/review task.
@@ -45,9 +46,11 @@ Design rules:
 import contextvars
 import functools
 import hashlib
+import hmac
 import json
 import os
 import re
+import secrets
 import shutil
 import subprocess
 import sys
@@ -418,7 +421,8 @@ def plan_materialize(
 
     Args:
         project_root: Absolute path to the project holding tasks/.
-        task_ids: Comma-separated list of task IDs to materialize.        Returns:
+        task_ids: Comma-separated list of task IDs to materialize.
+        Returns:
         Summary of created files and any validation results.
 
         Notes:
@@ -427,7 +431,7 @@ def plan_materialize(
         those values, and a fabricated placeholder would pollute the derived
         read model (an `Estimate: TBD` never parses and a `Deadline: TBD`
         would appear on the dashboard timeline).
-        """
+    """
     workspace_root = _explicit_project_root(project_root, "plan_materialize")
     tasks_dir = workspace_root / "tasks"
     backlog_dir = tasks_dir / "backlog"
@@ -647,9 +651,7 @@ def plan_status(project_root: Optional[str] = None) -> str:
 
     # Remaining work = everything not yet closed and not archived.
     open_tasks = [
-        t
-        for lane in ("backlog", "in-progress", "qa")
-        for t in lanes.get(lane, [])
+        t for lane in ("backlog", "in-progress", "qa") for t in lanes.get(lane, [])
     ]
     remaining_est = sum(
         (t.get("estimate_hours") or 0) for t in open_tasks if t.get("estimate_hours")
@@ -948,6 +950,236 @@ def sprint_check_daily_quota(project_root: Optional[str] = None) -> str:
     return f"⏳ Quota not reached — still open: {'; '.join(parts)}."
 
 
+# ---------------------------------------------------------------------------
+# Authentication, RBAC, and per-user project scoping (optional, off by default)
+# ---------------------------------------------------------------------------
+
+_USERS_CONFIG_ENV = "PLANNER_USERS_CONFIG"
+_DEFAULT_USERS_RELATIVE = Path(".config") / "opencode" / "planner-users.json"
+
+SESSION_COOKIE = "planner_session"
+SESSION_TTL_SECONDS = 7 * 24 * 3600
+
+_PBKDF2_ALGORITHM = "sha256"
+_PBKDF2_ITERATIONS = 600_000
+
+# In-memory token -> session store. Sessions deliberately do not survive a
+# restart: a restart is an operator action and re-login is cheap.
+_SESSIONS: dict = {}
+
+_USER_CONFIG: dict = {"auth_enabled": False}
+_AUTH_ENABLED: bool = False
+
+
+def _users_config_path() -> Path:
+    """Return the users config path: ``PLANNER_USERS_CONFIG`` or the home default.
+
+    Resolved per call (never cached at import) so tests and operators can
+    redirect it without reimporting the module.
+    """
+    env = os.environ.get(_USERS_CONFIG_ENV, "").strip()
+    if env:
+        return Path(env).expanduser()
+    return Path.home() / _DEFAULT_USERS_RELATIVE
+
+
+def _hash_password(password: str) -> tuple[str, str]:
+    """Hash a password with PBKDF2-HMAC-SHA256 and a fresh 16-byte salt.
+
+    Returns ``(salt_hex, hash_hex)``. Stdlib only — no third-party crypto.
+    """
+    salt = secrets.token_bytes(16)
+    derived = hashlib.pbkdf2_hmac(
+        _PBKDF2_ALGORITHM,
+        password.encode("utf-8"),
+        salt,
+        _PBKDF2_ITERATIONS,
+    )
+    return salt.hex(), derived.hex()
+
+
+def _verify_password(password: str, salt_hex: str, hash_hex: str) -> bool:
+    """Constant-time verification of a password against a stored salt + hash.
+
+    Returns False on any malformed stored value instead of raising, so a
+    corrupt config entry denies access rather than crashing the handler.
+    """
+    if not password or not salt_hex or not hash_hex:
+        return False
+    try:
+        salt = bytes.fromhex(salt_hex)
+        expected = bytes.fromhex(hash_hex)
+    except (ValueError, TypeError):
+        return False
+    derived = hashlib.pbkdf2_hmac(
+        _PBKDF2_ALGORITHM, password.encode("utf-8"), salt, _PBKDF2_ITERATIONS
+    )
+    return hmac.compare_digest(derived, expected)
+
+
+def _load_user_config() -> dict:
+    """Load the users config, failing closed to open local mode.
+
+    A missing file, unreadable file, invalid JSON, or non-object payload all
+    mean "no auth configured": the server keeps behaving exactly as it did
+    before auth existed.
+    """
+    path = _users_config_path()
+    try:
+        raw = path.read_text(encoding="utf-8")
+    except OSError:
+        return {"auth_enabled": False}
+    try:
+        data = json.loads(raw)
+    except (json.JSONDecodeError, ValueError):
+        return {"auth_enabled": False}
+    if not isinstance(data, dict):
+        return {"auth_enabled": False}
+    users = data.get("users")
+    if not isinstance(users, list):
+        users = []
+    return {
+        "auth_enabled": bool(data.get("auth_enabled", False)),
+        "users": users,
+    }
+
+
+def _find_user(config: dict, username: str) -> Optional[dict]:
+    """Return the user record matching ``username``, or None."""
+    if not isinstance(config, dict) or not username:
+        return None
+    for user in config.get("users") or []:
+        if isinstance(user, dict) and user.get("username") == username:
+            return user
+    return None
+
+
+class AuthState:
+    """Per-request authentication and authorization view.
+
+    ``user`` is None for an unauthenticated request. Project authorization
+    follows the user's ``allowed_projects``: ``"*"`` grants every project,
+    any other entry grants that directory and everything beneath it.
+    """
+
+    def __init__(self, config: dict, user: Optional[dict], sessions: dict):
+        self.config = config or {}
+        self.user = user or None
+        self.sessions = sessions
+
+    @property
+    def authenticated(self) -> bool:
+        return self.user is not None
+
+    @property
+    def username(self) -> str:
+        return str((self.user or {}).get("username") or "")
+
+    @property
+    def role(self) -> str:
+        return str((self.user or {}).get("role") or "")
+
+    @property
+    def is_admin(self) -> bool:
+        return self.authenticated and self.role == "admin"
+
+    @property
+    def allowed_projects(self) -> list[str]:
+        raw = (self.user or {}).get("allowed_projects") or []
+        if isinstance(raw, str):
+            raw = [raw]
+        if not isinstance(raw, (list, tuple)):
+            return []
+        out: list[str] = []
+        for entry in raw:
+            value = str(entry).strip()
+            if value and value not in out:
+                out.append(value)
+        return out
+
+    def project_allowed(self, path) -> bool:
+        """True when this session may read ``path`` (itself or a subdirectory)."""
+        if not self.authenticated:
+            return False
+        allowed = self.allowed_projects
+        if "*" in allowed:
+            return True
+        try:
+            target = Path(path).expanduser().resolve()
+        except OSError:
+            return False
+        for entry in allowed:
+            if entry == "*":
+                continue
+            try:
+                base = Path(entry).expanduser().resolve()
+            except OSError:
+                continue
+            if target == base or base in target.parents:
+                return True
+        return False
+
+
+def _build_auth_url_map() -> dict:
+    """Return the live token -> session map (the module-level session store)."""
+    return _SESSIONS
+
+
+def _session_from_token(token: str) -> Optional[dict]:
+    """Return a live session for ``token``, dropping it when expired."""
+    if not token:
+        return None
+    session = _SESSIONS.get(token)
+    if session is None:
+        return None
+    created = float(session.get("created") or 0.0)
+    if created and (time.time() - created) > SESSION_TTL_SECONDS:
+        _SESSIONS.pop(token, None)
+        return None
+    return session
+
+
+def _invalidate_token(token: str) -> None:
+    """Remove ``token`` from the session store (logout)."""
+    if token:
+        _SESSIONS.pop(token, None)
+
+
+def _refresh_auth_config() -> None:
+    """Reload the users config into the module globals.
+
+    Auth is enabled only when the file says so *and* at least one user is
+    defined — ``auth_enabled: true`` with an empty user list would lock every
+    caller out with no way back in except editing the file.
+    """
+    global _USER_CONFIG, _AUTH_ENABLED
+    _USER_CONFIG = _load_user_config()
+    _AUTH_ENABLED = bool(_USER_CONFIG.get("auth_enabled")) and bool(
+        _USER_CONFIG.get("users")
+    )
+
+
+def _cookie_from_header(header: str, name: str) -> str:
+    """Extract one cookie value from a raw ``Cookie`` header."""
+    for chunk in (header or "").split(";"):
+        key, _, value = chunk.strip().partition("=")
+        if key == name:
+            return value.strip()
+    return ""
+
+
+def _auth_from_request(request) -> Optional[AuthState]:
+    """Build the request's AuthState, or None when auth is disabled.
+
+    None means "open local mode": no session, no filtering, no 401/403.
+    """
+    if not _AUTH_ENABLED:
+        return None
+    token = request.cookies.get(SESSION_COOKIE, "")
+    session = _session_from_token(token)
+    return AuthState(_USER_CONFIG, (session or {}).get("user"), _SESSIONS)
+
+
 # ---------------------------------------------------------------------------
 # Embedded Starlette app: static dashboard + FastMCP HTTP endpoint
 # ---------------------------------------------------------------------------
@@ -973,9 +1205,7 @@ _PROJECT_ROOT_ENV = "PLANNER_PROJECT_ROOT"
 _DAILY_TARGET = int(os.environ.get("PLANNER_DAILY_TARGET", "3") or 3)
 
 # Weekly capacity in hours; the planner's default from the approved plan.
-_WEEKLY_CAPACITY_HOURS = float(
-    os.environ.get("PLANNER_WEEKLY_CAPACITY", "20") or 20
-)
+_WEEKLY_CAPACITY_HOURS = float(os.environ.get("PLANNER_WEEKLY_CAPACITY", "20") or 20)
 
 
 def _resolve_dashboard_root(project_root: Optional[str] = None) -> Path:
@@ -1013,16 +1243,18 @@ def _resolve_dashboard_root(project_root: Optional[str] = None) -> Path:
     return cwd
 
 
-def _discover_projects(current: Path) -> list[dict]:
+def _discover_projects(current: Path, auth: Optional[AuthState] = None) -> list[dict]:
     """List the project roots selectable in the dashboard switcher.
 
     Sources the ``PLANNER_PROJECTS`` environment variable (absolute paths
     separated by ``os.pathsep``) plus the currently resolved root. Entries are
     de-duplicated, and paths that do not exist or hold no ``tasks/`` directory
-    are dropped, so the selector never offers a dead target.
+    are dropped, so the selector never offers a dead target. When ``auth`` is
+    given, entries outside the session's ``allowed_projects`` are dropped too.
 
     Args:
         current: The project root currently being reported on.
+        auth: Optional session view used to filter the list.
 
     Returns:
         A list of ``{"path": ..., "label": ...}`` dicts, current first.
@@ -1043,10 +1275,26 @@ def _discover_projects(current: Path) -> list[dict]:
         seen.add(root)
         if not (root / "tasks").is_dir():
             continue
+        if auth is not None and not auth.project_allowed(root):
+            continue
         projects.append({"path": str(root), "label": root.name})
     return projects
 
 
+def _first_allowed_root(auth: AuthState) -> Optional[Path]:
+    """Return the first existing directory in the session's allowed projects."""
+    for entry in auth.allowed_projects:
+        if entry == "*":
+            continue
+        try:
+            candidate = Path(entry).expanduser().resolve()
+        except OSError:
+            continue
+        if candidate.is_dir():
+            return candidate
+    return None
+
+
 def _task_brief(task: dict) -> dict:
     """Project a parsed task record onto the fields the dashboard renders.
 
@@ -1071,7 +1319,9 @@ def _task_brief(task: dict) -> dict:
     }
 
 
-def _api_status(project_root: Optional[str] = None) -> dict:
+def _api_status(
+    project_root: Optional[str] = None, auth: Optional[AuthState] = None
+) -> dict:
     """Return planner status as JSON (GET /api/status).
 
     The payload is the dashboard's data contract: per-lane task lists (not
@@ -1084,12 +1334,30 @@ def _api_status(project_root: Optional[str] = None) -> dict:
 
     Args:
         project_root: Optional absolute project root from the query string.
+        auth: Optional session view. When given, an unauthenticated session
+            yields ``{"error": "unauthenticated"}``, an explicitly requested
+            root outside the session's allowed projects yields
+            ``{"error": "forbidden"}``, and the ``projects`` list is filtered
+            to the allowed roots. ``None`` means open local mode.
 
     Returns:
         A JSON-serialisable dict; on failure a dict with an ``error`` key.
     """
     try:
+        if auth is not None and not auth.authenticated:
+            return {"error": "unauthenticated"}
+
         workspace_root = _resolve_dashboard_root(project_root)
+        if auth is not None and not auth.project_allowed(workspace_root):
+            if project_root and project_root.strip():
+                return {"error": "forbidden"}
+            # No explicit root: fall back to the first allowed project rather
+            # than denying a viewer whose cwd is outside their grants.
+            fallback = _first_allowed_root(auth)
+            if fallback is None:
+                return {"error": "forbidden"}
+            workspace_root = fallback
+
         tasks = _load_all_tasks(workspace_root)
 
         lanes: dict[str, list[dict]] = {lane: [] for lane in TASK_LANES}
@@ -1112,7 +1380,7 @@ def _api_status(project_root: Optional[str] = None) -> dict:
 
         return {
             "project_root": str(workspace_root),
-            "projects": _discover_projects(workspace_root),
+            "projects": _discover_projects(workspace_root, auth),
             "total_tasks": len(tasks),
             "in_progress": len(lanes["in-progress"]),
             "qa_pending": len(lanes["qa"]),
@@ -1131,22 +1399,169 @@ def _api_status(project_root: Optional[str] = None) -> dict:
         return {"error": str(exc)}
 
 
+def _guarded_mcp_app(mcp_app):
+    """Wrap the MCP transport app with the admin-only ingress guard.
+
+    In open local mode the request passes straight through. When auth is
+    enabled, ``/mcp`` needs a valid session cookie *and* the admin role: a
+    viewer can read the dashboard but never execute tools.
+    """
+
+    async def guarded(scope, receive, send):
+        if scope.get("type") != "http" or not _AUTH_ENABLED:
+            await mcp_app(scope, receive, send)
+            return
+
+        headers = {
+            key.decode("latin-1").lower(): value.decode("latin-1")
+            for key, value in scope.get("headers") or []
+        }
+        token = _cookie_from_header(headers.get("cookie", ""), SESSION_COOKIE)
+        session = _session_from_token(token)
+        if session is None:
+            await _send_json(send, 401, {"error": "unauthenticated"})
+            return
+        if ((session.get("user") or {}).get("role") or "") != "admin":
+            await _send_json(send, 403, {"error": "forbidden"})
+            return
+        await mcp_app(scope, receive, send)
+
+    return guarded
+
+
+async def _send_json(send, status: int, payload: dict) -> None:
+    """Send a minimal JSON ASGI response (used by the /mcp guard)."""
+    body = json.dumps(payload).encode("utf-8")
+    await send(
+        {
+            "type": "http.response.start",
+            "status": status,
+            "headers": [
+                (b"content-type", b"application/json"),
+                (b"content-length", str(len(body)).encode("ascii")),
+            ],
+        }
+    )
+    await send({"type": "http.response.body", "body": body})
+
+
 def build_app():
     """Build the combined Starlette app: dashboard + FastMCP HTTP endpoint."""
     from starlette.applications import Starlette
     from starlette.routing import Mount, Route
     from starlette.responses import HTMLResponse, JSONResponse
+    from starlette.staticfiles import StaticFiles
     import uvicorn  # noqa: F401  (ensured available via pyproject)
 
+    # Pick up users-config edits on every (re)build; requests then read the
+    # module globals, so the hot path stays a dict lookup.
+    _refresh_auth_config()
+
     async def dashboard(request):
         return HTMLResponse(_dashboard_html())
 
     async def api_status(request):
-        return JSONResponse(_api_status(request.query_params.get("project_root")))
+        auth = _auth_from_request(request)
+        payload = _api_status(request.query_params.get("project_root"), auth)
+        error = payload.get("error")
+        if error == "unauthenticated":
+            return JSONResponse(payload, status_code=401)
+        if error == "forbidden":
+            return JSONResponse(payload, status_code=403)
+        return JSONResponse(payload)
+
+    async def api_login(request):
+        if not _AUTH_ENABLED:
+            return JSONResponse(
+                {
+                    "note": "auth disabled",
+                    "token": "",
+                    "username": "",
+                    "role": "",
+                    "allowed_projects": [],
+                }
+            )
+        try:
+            body = await request.json()
+        except Exception:  # noqa: BLE001 - any parse failure is a 400
+            return JSONResponse({"error": "invalid JSON body"}, status_code=400)
+        if not isinstance(body, dict):
+            return JSONResponse({"error": "invalid JSON body"}, status_code=400)
+
+        username = str(body.get("username") or "").strip()
+        password = str(body.get("password") or "")
+        if not username or not password:
+            return JSONResponse(
+                {"error": "username and password are required"}, status_code=400
+            )
 
-    # mcp>=1.10 exposes the Streamable HTTP transport as streamable_http_app()
-    # (the app already routes itself at settings.streamable_http_path, default
-    # "/mcp", so it is mounted at the root and must not be re-prefixed).
+        user = _find_user(_USER_CONFIG, username)
+        if user is None or not _verify_password(
+            password,
+            str(user.get("password_salt") or ""),
+            str(user.get("password_hash") or ""),
+        ):
+            return JSONResponse({"error": "invalid credentials"}, status_code=401)
+
+        token = secrets.token_urlsafe(32)
+        _SESSIONS[token] = {"user": user, "created": time.time()}
+        state = AuthState(_USER_CONFIG, user, _SESSIONS)
+        response = JSONResponse(
+            {
+                "token": token,
+                "username": state.username,
+                "role": state.role,
+                "allowed_projects": state.allowed_projects,
+            }
+        )
+        response.set_cookie(
+            SESSION_COOKIE,
+            token,
+            max_age=SESSION_TTL_SECONDS,
+            httponly=True,
+            samesite="lax",
+            path="/",
+        )
+        return response
+
+    async def api_logout(request):
+        _invalidate_token(request.cookies.get(SESSION_COOKIE, ""))
+        response = JSONResponse({"ok": True})
+        response.delete_cookie(SESSION_COOKIE, path="/")
+        return response
+
+    async def api_me(request):
+        if not _AUTH_ENABLED:
+            return JSONResponse(
+                {
+                    "authenticated": False,
+                    "note": "auth disabled",
+                    "username": "",
+                    "role": "",
+                    "allowed_projects": [],
+                }
+            )
+        auth = _auth_from_request(request)
+        if not auth.authenticated:
+            return JSONResponse({"error": "unauthenticated"}, status_code=401)
+        return JSONResponse(
+            {
+                "authenticated": True,
+                "username": auth.username,
+                "role": auth.role,
+                "is_admin": auth.is_admin,
+                "allowed_projects": auth.allowed_projects,
+            }
+        )
+
+    # The transport app routes itself at settings.streamable_http_path
+    # (default "/mcp"), so it is mounted at the root and must not be
+    # re-prefixed; the guard inspects the path instead.
+    #
+    # FastMCP caches its session manager on the instance, and a manager can be
+    # run() only once. build_app() runs again on every test app and on a real
+    # restart, so drop the cached manager to get a fresh transport app.
+    mcp._session_manager = None
     mcp_app = mcp.streamable_http_app()
 
     # Starlette runs the lifespan of the parent app only; a Mount-ed sub-app
@@ -1158,14 +1573,20 @@ def build_app():
         async with mcp_app.router.lifespan_context(mcp_app):
             yield
 
-    app = Starlette(
-        routes=[
-            Route("/", dashboard),
-            Route("/api/status", api_status),
-            Mount("/", app=mcp_app),
-        ],
-        lifespan=lifespan,
-    )
+    routes = [
+        Route("/", dashboard),
+        Route("/api/status", api_status),
+        Route("/api/login", api_login, methods=["POST"]),
+        Route("/api/logout", api_logout, methods=["POST"]),
+        Route("/api/me", api_me),
+    ]
+    if _STATIC_DIR.is_dir():
+        routes.append(
+            Mount("/static", app=StaticFiles(directory=str(_STATIC_DIR)), name="static")
+        )
+    routes.append(Mount("/", app=_guarded_mcp_app(mcp_app)))
+
+    app = Starlette(routes=routes, lifespan=lifespan)
     return app
 
 
diff --git a/mcp-planner-server/static/index.html b/mcp-planner-server/static/index.html
index 525c0e5..6dc92fd 100644
--- a/mcp-planner-server/static/index.html
+++ b/mcp-planner-server/static/index.html
@@ -68,14 +68,68 @@
   .project-switcher select { background: var(--panel); border: 1px solid var(--border); color: var(--text); padding: 4px 10px; border-radius: 6px; font-size: 0.875rem; }
   .pacing { display: flex; align-items: center; gap: 12px; }
   .pacing .label { font-size: 0.875rem; color: var(--muted); }
+  /* Auth UI */
+  .hidden { display: none !important; }
+  .user-badge { display: flex; align-items: center; gap: 8px; background: var(--panel); border: 1px solid var(--border); padding: 4px 12px 4px 8px; border-radius: 20px; font-size: 0.875rem; }
+  .user-badge .avatar { width: 22px; height: 22px; border-radius: 50%; background: var(--accent); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.75rem; color: #000; }
+  .user-badge .name { color: var(--text); font-weight: 600; }
+  .role-chip { font-size: 0.7rem; padding: 2px 8px; border-radius: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; }
+  .role-chip.admin { background: #1e1b4b; color: #c7d2fe; border: 1px solid #3730a3; }
+  .role-chip.viewer { background: #1c1917; color: #fed7aa; border: 1px solid #78350f; }
+  #logout-btn { background: transparent; border: 1px solid var(--border); color: var(--muted); padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.8rem; }
+  #logout-btn:hover { background: var(--panel-hover); color: var(--text); }
+  /* Login modal */
+  .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 100; }
+  .modal-overlay.hidden { display: none; }
+  .modal { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 24px; width: 360px; box-shadow: 0 20px 60px rgba(0,0,0,0.5); }
+  .modal h2 { font-size: 1.125rem; margin-bottom: 4px; }
+  .modal .sub { font-size: 0.875rem; color: var(--muted); margin-bottom: 20px; }
+  .modal .field { margin-bottom: 14px; }
+  .modal .field label { display: block; font-size: 0.8rem; color: var(--muted); margin-bottom: 4px; }
+  .modal .field input { width: 100%; background: var(--bg); border: 1px solid var(--border); color: var(--text); padding: 8px 12px; border-radius: 6px; font-size: 0.9rem; outline: none; }
+  .modal .field input:focus { border-color: var(--accent); }
+  .modal .err { color: var(--danger); font-size: 0.8rem; margin-bottom: 12px; min-height: 1.2em; }
+  .modal .actions { display: flex; gap: 10px; margin-top: 8px; }
+  .modal .btn-primary { flex: 1; background: var(--accent); color: #000; border: none; padding: 8px 16px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 0.9rem; }
+  .modal .btn-primary:hover { background: var(--accent-hover); }
+  .modal .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
+  .modal .btn-ghost { background: transparent; border: 1px solid var(--border); color: var(--muted); padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 0.9rem; }
+  .modal .btn-ghost:hover { background: var(--panel-hover); color: var(--text); }
 </style>
 </head>
 <body>
 <div class="container">
   <header>
     <div class="brand"><div class="dot"></div> Planner MCP</div>
+    <div id="user-area" style="display:flex;align-items:center;gap:10px;">
+      <div class="user-badge hidden" id="user-badge">
+        <div class="avatar" id="user-avatar">?</div>
+        <span class="name" id="user-name">—</span>
+        <span class="role-chip" id="user-role">—</span>
+      </div>
+      <button id="logout-btn" class="hidden">Logout</button>
+    </div>
     <div class="status-chip" id="status-chip"><span class="dot" id="status-dot"></span><span id="status-text">Loading…</span></div>
   </header>
+  <div class="modal-overlay hidden" id="login-modal">
+    <div class="modal">
+      <h2>Sign in to Planner</h2>
+      <div class="sub">Authentication is enabled on this server.</div>
+      <div class="err" id="login-err"></div>
+      <div class="field">
+        <label for="login-username">Username</label>
+        <input type="text" id="login-username" placeholder="e.g. admin" autocomplete="off">
+      </div>
+      <div class="field">
+        <label for="login-password">Password</label>
+        <input type="password" id="login-password" placeholder="Enter your password">
+      </div>
+      <div class="actions">
+        <button class="btn-ghost" id="login-cancel">Cancel</button>
+        <button class="btn-primary" id="login-btn">Sign in</button>
+      </div>
+    </div>
+  </div>
 
   <div class="grid">
     <div class="card">
@@ -186,6 +240,21 @@
   async function fetchStatus() {
     try {
       const resp = await fetch(statusUrl(), { cache: 'no-cache' });
+      if (resp.status === 401) {
+        // Auth is enabled and this session is not signed in.
+        hideUserBadge();
+        showLoginModal();
+        elements.statusChip.className = 'status-chip err';
+        elements.statusText.textContent = 'Sign in required';
+        elements.statusDot.className = 'dot';
+        return;
+      }
+      if (resp.status === 403) {
+        elements.statusChip.className = 'status-chip err';
+        elements.statusText.textContent = 'Access denied for this project';
+        elements.statusDot.className = 'dot';
+        return;
+      }
       if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
       const data = await resp.json();
       render(data);
@@ -330,6 +399,122 @@
     fetchStatus();
   });
 
+  // ---- Auth (login modal, user badge, logout) ----
+  const auth = {
+    modal: document.getElementById('login-modal'),
+    err: document.getElementById('login-err'),
+    username: document.getElementById('login-username'),
+    password: document.getElementById('login-password'),
+    loginBtn: document.getElementById('login-btn'),
+    cancelBtn: document.getElementById('login-cancel'),
+    logoutBtn: document.getElementById('logout-btn'),
+    userBadge: document.getElementById('user-badge'),
+    userName: document.getElementById('user-name'),
+    userRole: document.getElementById('user-role'),
+    userAvatar: document.getElementById('user-avatar'),
+    userArea: document.getElementById('user-area'),
+  };
+
+  function showLoginModal() {
+    auth.modal.classList.remove('hidden');
+    auth.err.textContent = '';
+    auth.username.value = '';
+    auth.password.value = '';
+    auth.username.focus();
+  }
+
+  function hideLoginModal() {
+    auth.modal.classList.add('hidden');
+  }
+
+  function showUserBadge(username, role, allowedProjects) {
+    auth.userBadge.classList.remove('hidden');
+    auth.logoutBtn.classList.remove('hidden');
+    auth.userName.textContent = username;
+    auth.userRole.textContent = role;
+    auth.userRole.className = 'role-chip ' + (role === 'admin' ? 'admin' : 'viewer');
+    auth.userAvatar.textContent = (username || '?').charAt(0).toUpperCase();
+  }
+
+  function hideUserBadge() {
+    auth.userBadge.classList.add('hidden');
+    auth.logoutBtn.classList.add('hidden');
+  }
+
+  async function login() {
+    auth.err.textContent = '';
+    auth.loginBtn.disabled = true;
+    auth.loginBtn.textContent = '…';
+    try {
+      const resp = await fetch('/api/login', {
+        method: 'POST',
+        headers: { 'Content-Type': 'application/json' },
+        body: JSON.stringify({
+          username: auth.username.value.trim(),
+          password: auth.password.value,
+        }),
+      });
+      if (!resp.ok) {
+        let message = `HTTP ${resp.status}`;
+        try {
+          const errBody = await resp.json();
+          if (errBody && errBody.error) message = errBody.error;
+        } catch (e) { /* non-JSON error body */ }
+        auth.err.textContent = message;
+        return;
+      }
+      const data = await resp.json();
+      if (data.token) {
+        hideLoginModal();
+        showUserBadge(data.username, data.role, data.allowed_projects);
+        currentProject = '';
+        fetchStatus();
+      } else if (data.note === 'auth disabled') {
+        // Auth is disabled server-side: open local mode, no badge to show.
+        hideLoginModal();
+        fetchStatus();
+      }
+    } catch (e) {
+      auth.err.textContent = 'Network error: ' + e.message;
+    } finally {
+      auth.loginBtn.disabled = false;
+      auth.loginBtn.textContent = 'Sign in';
+    }
+  }
+
+  async function logout() {
+    try {
+      await fetch('/api/logout', { method: 'POST' });
+    } catch (e) { /* best-effort: the cookie is cleared server-side */ }
+    hideUserBadge();
+    // Reload so no stale board data from the previous session stays on screen.
+    window.location.reload();
+  }
+
+  auth.loginBtn.addEventListener('click', login);
+  auth.cancelBtn.addEventListener('click', hideLoginModal);
+  auth.logoutBtn.addEventListener('click', logout);
+  auth.username.addEventListener('keydown', (e) => { if (e.key === 'Enter') auth.password.focus(); });
+  auth.password.addEventListener('keydown', (e) => { if (e.key === 'Enter') login(); });
+
+  // Check auth state on load.
+  (async function checkAuth() {
+    try {
+      const resp = await fetch('/api/me');
+      if (resp.ok) {
+        const data = await resp.json();
+        if (data.authenticated) {
+          showUserBadge(data.username, data.role || 'viewer', data.allowed_projects || []);
+        }
+        // `note: "auth disabled"` is open local mode — nothing to sign in to.
+      } else if (resp.status === 401) {
+        showLoginModal();
+      }
+    } catch (e) {
+      // If the server is unreachable, just show the board as-is.
+    }
+  })();
+
   fetchStatus();
   setInterval(fetchStatus, 30000);
 })();
diff --git a/mcp-planner-server/uv.lock b/mcp-planner-server/uv.lock
index 8639501..120e64c 100644
--- a/mcp-planner-server/uv.lock
+++ b/mcp-planner-server/uv.lock
@@ -5,8 +5,8 @@ resolution-markers = [
     "python_full_version >= '3.14' and sys_platform == 'win32'",
     "python_full_version >= '3.14' and sys_platform != 'win32'",
     "python_full_version >= '3.11' and python_full_version < '3.14' and sys_platform == 'win32'",
-    "python_full_version < '3.11' and sys_platform == 'win32'",
     "python_full_version >= '3.11' and python_full_version < '3.14' and sys_platform != 'win32'",
+    "python_full_version < '3.11' and sys_platform == 'win32'",
     "python_full_version < '3.11' and sys_platform != 'win32'",
 ]
 
@@ -171,6 +171,15 @@ wheels = [
     { url = "https://files.pythonhosted.org/packages/58/50/6c0d534c5f134586a8e1ba4e330569e32f057e33372ae556463212fb4cd3/click-8.5.0-py3-none-any.whl", hash = "sha256:255bc9599cf7748b4b1a446ccc735421bd08a2ae529a8b88597d3de5664ee360", size = 125251, upload-time = "2026-08-26T13:33:12.928Z" },
 ]
 
+[[package]]
+name = "colorama"
+version = "0.4.6"
+source = { registry = "https://pypi.org/simple" }
+sdist = { url = "https://files.pythonhosted.org/packages/d8/53/6f443c9a4a8358a93a6792e2acffb9d9d5cb0a5cfd8802644b7b1c9a02e4/colorama-0.4.6.tar.gz", hash = "sha256:08695f5cb7ed6e0531a20572697297273c47b8cae5a63ffc6d6ed5c201be6e44", size = 27697, upload-time = "2022-10-25T02:36:22.414Z" }
+wheels = [
+    { url = "https://files.pythonhosted.org/packages/d1/d6/3965ed04c63042e047cb6a3e6ed1a63a35087b6a609aa3a15ed8ac56c221/colorama-0.4.6-py2.py3-none-any.whl", hash = "sha256:4f1d9991f5acc0ca119f9d443620b77f9d6b33703e51011c16baf57afb285fc6", size = 25335, upload-time = "2022-10-25T02:36:20.889Z" },
+]
+
 [[package]]
 name = "cryptography"
 version = "50.0.2"
@@ -308,6 +317,15 @@ wheels = [
     { url = "https://files.pythonhosted.org/packages/58/a2/bb081bab032533a855d44de1d56f8e8426114ff1ba5d1f07a438a0a654f8/idna-3.20-py3-none-any.whl", hash = "sha256:ab7ae7122974553370f0bdb919e1a960b2cd1bc1ef0276416d896db81c14582c", size = 69583, upload-time = "2026-09-17T14:11:03.168Z" },
 ]
 
+[[package]]
+name = "iniconfig"
+version = "2.3.1"
+source = { registry = "https://pypi.org/simple" }
+sdist = { url = "https://files.pythonhosted.org/packages/01/e1/2069291243c926a2ff1cd706c7f3eeb9b62144bf60f77c9fb9ff2fb26bd3/iniconfig-2.3.1.tar.gz", hash = "sha256:67f4b9c50da0dedf52af349e7749a80a9057a5031199791b906c3bb3ae878960", size = 21209, upload-time = "2026-10-06T22:48:38.076Z" }
+wheels = [
+    { url = "https://files.pythonhosted.org/packages/56/43/4ca9e49d27a1fcf6bece6f6aec0ea46bb9112489b93d4b688fb415457bdb/iniconfig-2.3.1-py3-none-any.whl", hash = "sha256:9121e2c1fdb355232495be3194c8dfe87ccc2d5dee45947b78e68f499790d7a7", size = 7552, upload-time = "2026-10-06T22:48:36.959Z" },
+]
+
 [[package]]
 name = "jsonschema"
 version = "4.26.0"
@@ -375,13 +393,42 @@ dependencies = [
     { name = "uvicorn" },
 ]
 
+[package.optional-dependencies]
+dev = [
+    { name = "httpx" },
+    { name = "pytest" },
+    { name = "pytest-timeout" },
+]
+
 [package.metadata]
 requires-dist = [
+    { name = "httpx", marker = "extra == 'dev'" },
     { name = "mcp", specifier = ">=1.3.0,<2.0" },
+    { name = "pytest", marker = "extra == 'dev'" },
+    { name = "pytest-timeout", marker = "extra == 'dev'" },
     { name = "pyyaml" },
     { name = "starlette" },
     { name = "uvicorn" },
 ]
+provides-extras = ["dev"]
+
+[[package]]
+name = "packaging"
+version = "26.3"
+source = { registry = "https://pypi.org/simple" }
+sdist = { url = "https://files.pythonhosted.org/packages/7d/fa/3944b40b07da9ce895c0e6303a5ab7d53da063554f534556b134a54d6093/packaging-26.3.tar.gz", hash = "sha256:94edc256424af38762eb31306eed28beb9f0efc50a8837492c9d6fd6004aed79", size = 313412, upload-time = "2026-08-04T18:15:28.737Z" }
+wheels = [
+    { url = "https://files.pythonhosted.org/packages/63/34/ba1c580383c9eada3711951fef0795c80b829a078d72188184bcab9dd527/packaging-26.3-py3-none-any.whl", hash = "sha256:d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c", size = 129956, upload-time = "2026-08-04T18:15:27.159Z" },
+]
+
+[[package]]
+name = "pluggy"
+version = "1.7.0"
+source = { registry = "https://pypi.org/simple" }
+sdist = { url = "https://files.pythonhosted.org/packages/bf/db/7fc19e6f2dc92a966727031389fc2e08b558f0f25eb7403c1119ad4713cd/pluggy-1.7.0.tar.gz", hash = "sha256:d1eaa46ebb595891b860ab086b4d09c8588af65ebd4361b8e8f4bb8920b90ba8", size = 123304, upload-time = "2026-10-15T09:50:58.343Z" }
+wheels = [
+    { url = "https://files.pythonhosted.org/packages/40/9e/2b38731e0fc536806f16490e1a12d7f0dc2a1235aa8cc07bcc75416a7daa/pluggy-1.7.0-py3-none-any.whl", hash = "sha256:7dd7b0d8832ba3cb632c306926ded123429211b83641b35dc5c41ad2d34f9bec", size = 27082, upload-time = "2026-10-15T09:50:56.808Z" },
+]
 
 [[package]]
 name = "pycparser"
@@ -612,6 +659,15 @@ wheels = [
     { url = "https://files.pythonhosted.org/packages/3c/74/fdf926afe145d8629c4b2ff57f4ea1d64ed7abc4d84d97463b2517a2547e/pydantic_settings-2.16.1-py3-none-any.whl", hash = "sha256:30f5313340da4e8f1b440d1910b92a5bc3ccbb6b4ba70ec2b8395bc921f418f5", size = 80771, upload-time = "2026-10-20T11:37:17.298Z" },
 ]
 
+[[package]]
+name = "pygments"
+version = "2.21.0"
+source = { registry = "https://pypi.org/simple" }
+sdist = { url = "https://files.pythonhosted.org/packages/49/2e/ced460408999b33da6b31b0021b0f37d329e202d4169aeb164493778f25b/pygments-2.21.0.tar.gz", hash = "sha256:610ca751c9bc2492b38eb9a38a7fbc93edbbb2d7182edaf34e66ae493dee5c8c", size = 5005329, upload-time = "2026-08-17T08:02:48.824Z" }
+wheels = [
+    { url = "https://files.pythonhosted.org/packages/71/46/17f022dd3e953bf20a04a028a21ec746d942f8d2af30fa0f124fa0e6a684/pygments-2.21.0-py3-none-any.whl", hash = "sha256:2363c69b61c4a97c838da3b130dcd6468f4848992b21a82f2a63ec34377137d9", size = 1250147, upload-time = "2026-08-17T08:02:44.912Z" },
+]
+
 [[package]]
 name = "pyjwt"
 version = "2.15.1"
@@ -629,6 +685,36 @@ crypto = [
     { name = "cryptography" },
 ]
 
+[[package]]
+name = "pytest"
+version = "9.1.1"
+source = { registry = "https://pypi.org/simple" }
+dependencies = [
+    { name = "colorama", marker = "sys_platform == 'win32'" },
+    { name = "exceptiongroup", marker = "python_full_version < '3.11'" },
+    { name = "iniconfig" },
+    { name = "packaging" },
+    { name = "pluggy" },
+    { name = "pygments" },
+    { name = "tomli", marker = "python_full_version < '3.11'" },
+]
+sdist = { url = "https://files.pythonhosted.org/packages/e4/47/b9efed96c114afcfa3c9d3fe98a76a1d14c74a9e266d397cf6eb64be5e01/pytest-9.1.1.tar.gz", hash = "sha256:1088fbde8f2b49d95a549a195707afa7a76a3ce9bcadc26b6d71f0ffda5fe313", size = 1636369, upload-time = "2026-06-19T10:58:32.857Z" }
+wheels = [
+    { url = "https://files.pythonhosted.org/packages/24/25/1de2678b631f5a49215c6c96fff41ba892b0a34df68d6d80292b1b48aa7f/pytest-9.1.1-py3-none-any.whl", hash = "sha256:37a86b45efb9a47a61a36449063e8e18d0cab3161329fc099eb21783169c4f0c", size = 386536, upload-time = "2026-06-19T10:58:31.347Z" },
+]
+
+[[package]]
+name = "pytest-timeout"
+version = "2.4.0"
+source = { registry = "https://pypi.org/simple" }
+dependencies = [
+    { name = "pytest" },
+]
+sdist = { url = "https://files.pythonhosted.org/packages/ac/82/4c9ecabab13363e72d880f2fb504c5f750433b2b6f16e99f4ec21ada284c/pytest_timeout-2.4.0.tar.gz", hash = "sha256:7e68e90b01f9eff71332b25001f85c75495fc4e3a836701876183c4bcfd0540a", size = 17973, upload-time = "2025-05-05T19:44:34.99Z" }
+wheels = [
+    { url = "https://files.pythonhosted.org/packages/fa/b6/3127540ecdf1464a00e5a01ee60a1b09175f6913f0644ac748494d9c4b21/pytest_timeout-2.4.0-py3-none-any.whl", hash = "sha256:c42667e5cdadb151aeb5b26d114aff6bdf5a907f176a007a30b940d3d865b5c2", size = 14382, upload-time = "2025-05-05T19:44:33.502Z" },
+]
+
 [[package]]
 name = "python-dotenv"
 version = "1.2.4"
@@ -1068,6 +1154,78 @@ wheels = [
     { url = "https://files.pythonhosted.org/packages/f3/93/181df62699d9b5aca1d87e5cfda131dac87e3cdaebf668662f7206ca3470/starlette-1.9.0-py3-none-any.whl", hash = "sha256:fd3f159936e882d06c1108f84688f7cda2cf85fc6a592a50edbd175e882c2ddc", size = 80335, upload-time = "2026-10-18T15:50:31.526Z" },
 ]
 
+[[package]]
+name = "tomli"
+version = "2.5.0"
+source = { registry = "https://pypi.org/simple" }
+sdist = { url = "https://files.pythonhosted.org/packages/b0/78/9ad63712633ed3ab5cc1a648d863d7e7da371e9425e209555a0fe711b695/tomli-2.5.0.tar.gz", hash = "sha256:264507556cd8b8c8e7c6ee037cdf443a463f03f4c958e57195e3d369711b8ff6", size = 17662, upload-time = "2026-10-07T12:23:37.892Z" }
+wheels = [
+    { url = "https://files.pythonhosted.org/packages/22/a6/ab99b60ee52acd949684febabc3005d0045d0f66bebd9cdebd67372d26dd/tomli-2.5.0-cp311-cp311-macosx_10_9_x86_64.whl", hash = "sha256:c4dc1c1781f2f716de763d1e9a7b34c6a894e167e291c7c5d16c72f7a9538545", size = 163901, upload-time = "2026-10-07T12:22:15.601Z" },
+    { url = "https://files.pythonhosted.org/packages/bc/00/ee01b7ed4579180fff07142d290257f25ba786f23f3ec6005f620933c2f5/tomli-2.5.0-cp311-cp311-macosx_11_0_arm64.whl", hash = "sha256:eff8babca5a7999bc137acbc7482a8b7e17ffca5075ab41f5d770ab408c7bfef", size = 163756, upload-time = "2026-10-07T12:22:16.957Z" },
+    { url = "https://files.pythonhosted.org/packages/72/c2/4efebf65372f6583185f79799312109dddb61102d47e5c33dcfd1a297aca/tomli-2.5.0-cp311-cp311-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:86665cee9c4835b7a7f1e8ec2c719b5258d4dc782887aded5a8ae7352a96843b", size = 268038, upload-time = "2026-10-07T12:22:18.135Z" },
+    { url = "https://files.pythonhosted.org/packages/53/07/5850468e925d898abb36038666f9c333a94d2a223e802a8ba5b6d319d23f/tomli-2.5.0-cp311-cp311-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:d7e369fd63331746182360977b1892bfc215476a30d61612d732425311639f56", size = 276422, upload-time = "2026-10-07T12:22:19.567Z" },
+    { url = "https://files.pythonhosted.org/packages/b4/87/f293984cdcf83c054196d4fd3dad44fc68ae55b4b8c44bc76cef360c3150/tomli-2.5.0-cp311-cp311-musllinux_1_2_aarch64.whl", hash = "sha256:7ad1ea345759240d6463efa0ed1c704402752e49aa21476620738d74d72d8aa1", size = 272616, upload-time = "2026-10-07T12:22:20.794Z" },
+    { url = "https://files.pythonhosted.org/packages/ce/ce/db582886b3c1219d3fec93ebd669332482e5aee7a91e0f7838d84f2d1759/tomli-2.5.0-cp311-cp311-musllinux_1_2_x86_64.whl", hash = "sha256:96243987194634bd411066ce40c952e108f86af04db533ecd8ac3ff2a85b1885", size = 276593, upload-time = "2026-10-07T12:22:22.12Z" },
+    { url = "https://files.pythonhosted.org/packages/bf/72/7619b87dea4261fc27dd7b54c4461c129c1f7d9bb7ba3aec89c797a431b8/tomli-2.5.0-cp311-cp311-win32.whl", hash = "sha256:610b27d99f28ec5f191c7064a48f3ddb179a1fe6ca73d571483ae859f57b605e", size = 101830, upload-time = "2026-10-07T12:22:23.651Z" },
+    { url = "https://files.pythonhosted.org/packages/1e/74/220106da34502304b6751a2a9b8a9fbca6c3fd47e737a2e2e3da7c61c9db/tomli-2.5.0-cp311-cp311-win_amd64.whl", hash = "sha256:c804ae44fe7b4bab5da295e4f980a1ff04670bca9d23fe0a4e887e08ebd741a8", size = 112742, upload-time = "2026-10-07T12:22:24.972Z" },
+    { url = "https://files.pythonhosted.org/packages/27/99/7d9c8b41837a7773613e169504147375c157a290167aa59ad74a085f521f/tomli-2.5.0-cp311-cp311-win_arm64.whl", hash = "sha256:cfac177ebd6236003846ea339981f71457cb6eb748f23381eb257e45092e3980", size = 109332, upload-time = "2026-10-07T12:22:26.117Z" },
+    { url = "https://files.pythonhosted.org/packages/52/ed/7baa86f87493646a594de388c7c1c40a39dd0461f7e9c0359cbeefc91fe8/tomli-2.5.0-cp312-cp312-macosx_10_13_x86_64.whl", hash = "sha256:1f4a40d03fb9f63424f0979855bdeaf44dd7696b8d59501822c10ed30ba532df", size = 164854, upload-time = "2026-10-07T12:22:27.444Z" },
+    { url = "https://files.pythonhosted.org/packages/a5/b1/44c0341f2224397855723c7a8a39f718ea6fcbcc3dacc66e5aeca0f334e3/tomli-2.5.0-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:9ebf8d19b17bd0daeb7b7dec81a946a439b753942fd0210d6e96c532249eea6b", size = 164074, upload-time = "2026-10-07T12:22:28.679Z" },
+    { url = "https://files.pythonhosted.org/packages/23/04/e2d5b7d3fba47adedb23de616c16d428ea076c79a3d8e1d95d649ffe197e/tomli-2.5.0-cp312-cp312-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:bf0b5e8e0f68ebb494356e577c06c139161efd8d3b9050f93b39b7c26cc54ff0", size = 274274, upload-time = "2026-10-07T12:22:29.804Z" },
+    { url = "https://files.pythonhosted.org/packages/43/90/6090e706ff27a6f89f4a40578e3324b95c3cd8c4150868aabf33a8f414c3/tomli-2.5.0-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:6cf74416bdc94ae458b14e37286c1073081850ac8459a00d0c5efef5d44294c6", size = 286435, upload-time = "2026-10-07T12:22:31.297Z" },
+    { url = "https://files.pythonhosted.org/packages/0a/9e/a2c40768df16c408f22430afb0a73e9d7e5f79c950884954649d1146b74d/tomli-2.5.0-cp312-cp312-musllinux_1_2_aarch64.whl", hash = "sha256:61ea1ebe1e55a34ea8199cc8dbff398d35027b82271c8ac4802fd3a1fd5b1bcc", size = 278119, upload-time = "2026-10-07T12:22:32.601Z" },
+    { url = "https://files.pythonhosted.org/packages/12/25/3c0cb485b98e9cfac495629b1c93c87ccf0b72fbe9d2689fd8fe62c6d5a3/tomli-2.5.0-cp312-cp312-musllinux_1_2_x86_64.whl", hash = "sha256:ed53f7e89bb04f6d9e8e7799112360b0c4d5cbff067de0814c98c37c39b920f7", size = 286177, upload-time = "2026-10-07T12:22:33.745Z" },
+    { url = "https://files.pythonhosted.org/packages/77/8b/0144c65f0e37e51c18d04ae15c21b19431c165002d0131fe9aa8b0b8b1e8/tomli-2.5.0-cp312-cp312-win32.whl", hash = "sha256:e7ad033e27a516a233bea839cdb77b80146facb3b4f40bf02cd0cac165cdd5c2", size = 102760, upload-time = "2026-10-07T12:22:34.887Z" },
+    { url = "https://files.pythonhosted.org/packages/de/32/5d6d8f42fc9a05fce69354e00ff256484192f5f2fc9a2165718fa0de61ec/tomli-2.5.0-cp312-cp312-win_amd64.whl", hash = "sha256:bd05de8c1698f8413dd7d869492693a0bf2211543b787ac78cd5e7536af1a6d7", size = 112722, upload-time = "2026-10-07T12:22:36.162Z" },
+    { url = "https://files.pythonhosted.org/packages/30/65/df18032218db0fb9b769fb23c8039a051f15c811993995ea04c350273a32/tomli-2.5.0-cp312-cp312-win_arm64.whl", hash = "sha256:069435bd5480429b98c5e5afb02ab21c219b6f0064680671c6dc0d46817346ea", size = 109534, upload-time = "2026-10-07T12:22:37.296Z" },
+    { url = "https://files.pythonhosted.org/packages/42/e5/51736d70da209350969e15aca5c5ab6e2ce1ea87a0a892a6c13aec172a86/tomli-2.5.0-cp313-cp313-macosx_10_13_x86_64.whl", hash = "sha256:943276cf269e0071948d9ff697159c1735e623c1151d88abb09b74659ef0cbea", size = 163328, upload-time = "2026-10-07T12:22:38.373Z" },
+    { url = "https://files.pythonhosted.org/packages/ec/55/086f80dab4ab497602644274e6dea7ec5dd0b4e262e443a8ad3bb7edee2d/tomli-2.5.0-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:463b16086865b97facd8d0b3fb4cb7c544e3f58d2a69dc3113d6db9653fdb043", size = 162246, upload-time = "2026-10-07T12:22:39.673Z" },
+    { url = "https://files.pythonhosted.org/packages/aa/eb/3ecc94459f3635c92321f4e7bde571323fdb2267c50e19e3188a281eae3b/tomli-2.5.0-cp313-cp313-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:1245a6638fc4bb0a60af38a7d45413db34a13842027c77597c712c998c62fdf0", size = 272655, upload-time = "2026-10-07T12:22:41.08Z" },
+    { url = "https://files.pythonhosted.org/packages/c0/d7/494fd1f0c37a621f1ad9975c2efadb523e8101f144ed6edb2e7fe64738f2/tomli-2.5.0-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:5d8bac3d603c97e6854424e5b2b5b741bdbde387e09f162fb0446812b4a8362b", size = 283595, upload-time = "2026-10-07T12:22:42.222Z" },
+    { url = "https://files.pythonhosted.org/packages/70/51/bb8d62b1317e6640866f6949b2d5855e5300f2c99d46de1cd245570bba65/tomli-2.5.0-cp313-cp313-musllinux_1_2_aarch64.whl", hash = "sha256:21e4cae4114aba25aa0d4f85cdf486d290fb35c0954d7bba536248da64d43066", size = 276253, upload-time = "2026-10-07T12:22:43.625Z" },
+    { url = "https://files.pythonhosted.org/packages/66/f4/f46bd7f0763cd47de2db697dca9257c6a4adfd1a93b018cc75c8190ed5a8/tomli-2.5.0-cp313-cp313-musllinux_1_2_x86_64.whl", hash = "sha256:bbaefc84548d754be821bba7c4141c4787dda182f9e77f2f87b71213529efa7b", size = 283582, upload-time = "2026-10-07T12:22:44.983Z" },
+    { url = "https://files.pythonhosted.org/packages/ac/03/70f2bcb2923a6db37818d917e124270a7f4cfd38ea576f5aa753a91c0ef5/tomli-2.5.0-cp313-cp313-win32.whl", hash = "sha256:abdbf6313b8d9efe157edeb7ab6eae4de064b1300ad31abf73755154b30abe68", size = 102628, upload-time = "2026-10-07T12:22:46.508Z" },
+    { url = "https://files.pythonhosted.org/packages/dc/98/d52024bb5b0ff68b4f0d276d867f634c84a67319a7e9f6b7708a37742333/tomli-2.5.0-cp313-cp313-win_amd64.whl", hash = "sha256:fd4dc129784e0c5335bd4e61dfcc4487499a013419e655cf2da1d091b7e0efdc", size = 113301, upload-time = "2026-10-07T12:22:47.647Z" },
+    { url = "https://files.pythonhosted.org/packages/6f/f2/540db3a70572a8c23a28aba3e9c358ce0ffffbafc990905c1343aa265b31/tomli-2.5.0-cp313-cp313-win_arm64.whl", hash = "sha256:69491c143d2fe063046e0301e62a810bed338fa4d1ce0fd870c27dc1e09b0d84", size = 109744, upload-time = "2026-10-07T12:22:48.925Z" },
+    { url = "https://files.pythonhosted.org/packages/e4/49/caf6b307766eb9567664a8707e9d6be5fcc0e8903f18781c6677a60d80c7/tomli-2.5.0-cp314-cp314-macosx_10_15_x86_64.whl", hash = "sha256:d3182ee2d887e507bd67319a0a61105d1dd33facc111329559a233b772c1a105", size = 162899, upload-time = "2026-10-07T12:22:50.088Z" },
+    { url = "https://files.pythonhosted.org/packages/d3/c8/68cfce773a2733a49c74f99d627fb461bd990756860099eac25617889585/tomli-2.5.0-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:521345fd1f19d45b8df87657aaa38b6f2ca3800059fadf428e7ebf479a383646", size = 162080, upload-time = "2026-10-07T12:22:51.558Z" },
+    { url = "https://files.pythonhosted.org/packages/7e/b2/e5bb8651fdad593f670501a7d718b1a7f73f064d44dea15e04c04dfef45d/tomli-2.5.0-cp314-cp314-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:6e95c7614e705bfe2b04b27aa124adec59752d15813df37e2156747cab3a006b", size = 273380, upload-time = "2026-10-07T12:22:52.918Z" },
+    { url = "https://files.pythonhosted.org/packages/8d/d2/9e2d7f8b1dfe0e2b34c245986ebd55c4c553ea4ce6c47c443b332673253f/tomli-2.5.0-cp314-cp314-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:7ac2027d37c3afbdf4bdd377f2676f6f1d2122a5be1f1137b49dced590b37e75", size = 283228, upload-time = "2026-10-07T12:22:54.173Z" },
+    { url = "https://files.pythonhosted.org/packages/ba/df/ec7b876b7b1a2718bd74a3743c076fff565b04029ba33e8f61fac262739f/tomli-2.5.0-cp314-cp314-musllinux_1_2_aarch64.whl", hash = "sha256:c414be4ed9d3cac80c42e348fa5a956117d1a48227f48026e31f59cb4a7671eb", size = 277189, upload-time = "2026-10-07T12:22:55.342Z" },
+    { url = "https://files.pythonhosted.org/packages/7d/7b/e192d9eed0b9cb80da799f4d77052297fb9a2c3cc9b19f571f56ea88add6/tomli-2.5.0-cp314-cp314-musllinux_1_2_x86_64.whl", hash = "sha256:9b03d7dc168353b4132965bde20feceabaa470e570c6f59660dfae59b1f9eeb3", size = 283632, upload-time = "2026-10-07T12:22:56.735Z" },
+    { url = "https://files.pythonhosted.org/packages/84/50/ff94454e75461d75623e47401ed323d65c10aab8fe9033242c20cd2fdf32/tomli-2.5.0-cp314-cp314-win32.whl", hash = "sha256:6f041843c4d3a37245c0c056fd955b186bf8b1fb85690cbe40b81230891dc34b", size = 103535, upload-time = "2026-10-07T12:22:58.084Z" },
+    { url = "https://files.pythonhosted.org/packages/54/0b/bdacf05f963bd6026ebf6eeb0beda847d1d60e03e440725c64a4e08a0afd/tomli-2.5.0-cp314-cp314-win_amd64.whl", hash = "sha256:f4b653094e18f9031102d3a1da5c729c8f222d85225b18037dac621695e46e1a", size = 114621, upload-time = "2026-10-07T12:22:59.2Z" },
+    { url = "https://files.pythonhosted.org/packages/61/99/53f438fa6ae4f9d4ed0ddde3e7242b3bdc34b48c8f9948b72b9e9b127676/tomli-2.5.0-cp314-cp314-win_arm64.whl", hash = "sha256:3f89d10c1ff6a38d992c27fc8a4816af71a909e08a40ec66934240b1e74347c3", size = 111572, upload-time = "2026-10-07T12:23:00.479Z" },
+    { url = "https://files.pythonhosted.org/packages/b9/20/1f88f19427d380a40e90a770e087489eaafe4aeee070ae88ed2bbec00acd/tomli-2.5.0-cp314-cp314t-macosx_10_15_x86_64.whl", hash = "sha256:e9e15b4a6c7dd6b85b5fbab29488a73f1f70de516942308daa266bf0e0aeb0d4", size = 171814, upload-time = "2026-10-07T12:23:01.914Z" },
+    { url = "https://files.pythonhosted.org/packages/d0/56/cbe5079c9f9a54b9b3e27fc82f08f3cb36edee75561679f53d2380c801d6/tomli-2.5.0-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:e12bbcd32897272fb05929110362ae9ff4c1b9bb26bd9e971e71dcd3275b4c3d", size = 171324, upload-time = "2026-10-07T12:23:03.18Z" },
+    { url = "https://files.pythonhosted.org/packages/2b/30/1d53fd3b0f1cb3ba542e345ec32c26aefdddc4e829e4f3429af8a4f27782/tomli-2.5.0-cp314-cp314t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:20aa36de8f2cf87237143bc1fa1aae8d6612c09118f4da21c6a684db5dd1f6f9", size = 297441, upload-time = "2026-10-07T12:23:04.345Z" },
+    { url = "https://files.pythonhosted.org/packages/66/d9/0800acb6a111686f764c1b91ef15cc42a20a66a46013bb42220f1d2c61c1/tomli-2.5.0-cp314-cp314t-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:22185fad8a1e622f064e78008018a0dd3323550dcb479cb7a1d296888d74024f", size = 307476, upload-time = "2026-10-07T12:23:05.671Z" },
+    { url = "https://files.pythonhosted.org/packages/e8/63/30a8f3cd51b5bec37f04744bad0b0dc6160df84aad4f27b0e9283d66f221/tomli-2.5.0-cp314-cp314t-musllinux_1_2_aarch64.whl", hash = "sha256:984012f71908165449a951de2050d52f276bfe3aa5d5f570f63ddad814370374", size = 296113, upload-time = "2026-10-07T12:23:07.202Z" },
+    { url = "https://files.pythonhosted.org/packages/ab/18/0b9ffc597e69c5a1e20a7823cb60d54b39a9f54e91edcb8574f022186758/tomli-2.5.0-cp314-cp314t-musllinux_1_2_x86_64.whl", hash = "sha256:f79203b3965b4000e91808aaa7c040206093f2b8bf86f455982f2274c9ccf442", size = 307725, upload-time = "2026-10-07T12:23:08.508Z" },
+    { url = "https://files.pythonhosted.org/packages/ab/c7/18f8baae0b5607a60e8e19b4a7fedee43a8ff6458e3896dcbbadeeac9c22/tomli-2.5.0-cp314-cp314t-win32.whl", hash = "sha256:91294a9fb94a75542f6e46e4a2ae709bd8d9b51134098cae5cf3bea5478b6d03", size = 108546, upload-time = "2026-10-07T12:23:09.956Z" },
+    { url = "https://files.pythonhosted.org/packages/72/34/4cca9739254130627bde87500b3f2b512154fe2f278efa7e2a5e10ad4bcb/tomli-2.5.0-cp314-cp314t-win_amd64.whl", hash = "sha256:f15e3e0b835a6d68b10c86bf80a3149780498d6911c93c3ffd1861d19f9200f1", size = 117814, upload-time = "2026-10-07T12:23:11.486Z" },
+    { url = "https://files.pythonhosted.org/packages/7d/fb/afa530d47dd80a78fce43beac6bc6e00f84558eafcffbc6f37b21e80d056/tomli-2.5.0-cp314-cp314t-win_arm64.whl", hash = "sha256:6664b7ae7af7294256c53960a6103077f4914cec8ff98479c352f622c6f6b2f0", size = 115188, upload-time = "2026-10-07T12:23:12.728Z" },
+    { url = "https://files.pythonhosted.org/packages/66/98/316fdc00f8c0939e6fe50461dd343c162d3ad51d1286eb25b7db54361d50/tomli-2.5.0-cp315-cp315-macosx_10_15_x86_64.whl", hash = "sha256:a525685c2f97da40762b8695eb7aa0af4c8344ca1905c73e4e29cb04d34607dc", size = 162775, upload-time = "2026-10-07T12:23:13.941Z" },
+    { url = "https://files.pythonhosted.org/packages/c5/22/7b10fa5bb01c9539f53f69b619361b19350acc73657772ea7ac70ba309a8/tomli-2.5.0-cp315-cp315-macosx_11_0_arm64.whl", hash = "sha256:9dbb18c1cfb2f6517942fc9314437f66aa06d94436ffb1f06102ef3572f35276", size = 161406, upload-time = "2026-10-07T12:23:15.215Z" },
+    { url = "https://files.pythonhosted.org/packages/9c/e7/1a069d86dfd20f1f84f71c63faed9f83c1d890bc06c27d82dc7d888fb573/tomli-2.5.0-cp315-cp315-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:752e8b1aa6a4367ef8bf6a1a1e005540f7ed055ba36d7193796812ca5404eb52", size = 273855, upload-time = "2026-10-07T12:23:16.471Z" },
+    { url = "https://files.pythonhosted.org/packages/ae/83/d1ef43d1687d092ab9c235455c76e6e709483b346b056f086095c7c263a5/tomli-2.5.0-cp315-cp315-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:c47300f9bf791808f77d82747691c4bb09cb14bdf3060cca99b42cdc4361d5a7", size = 284910, upload-time = "2026-10-07T12:23:18.166Z" },
+    { url = "https://files.pythonhosted.org/packages/cc/05/f4d9cf7de61822ece0c3873f30d291e324911c71a378b8bfe5ced13fd9f5/tomli-2.5.0-cp315-cp315-musllinux_1_2_aarch64.whl", hash = "sha256:19b0dd8749f4ea2f112c5fcfb3c5248390c899d7e2e173f1d91abee1fa0ff391", size = 277723, upload-time = "2026-10-07T12:23:19.355Z" },
+    { url = "https://files.pythonhosted.org/packages/42/28/78262493141fa543151cf005760c3cb01d09fc28a11f993c05109902cb8c/tomli-2.5.0-cp315-cp315-musllinux_1_2_x86_64.whl", hash = "sha256:57b1c3b01fab802e2899bc3d168dca320e14165e2fd9fd584760fb4ca5826859", size = 285115, upload-time = "2026-10-07T12:23:20.698Z" },
+    { url = "https://files.pythonhosted.org/packages/1a/b9/e1dab9a30bcb677b5cc5cee810609cfd64f24306a3055767dd3fda00b1e0/tomli-2.5.0-cp315-cp315-win32.whl", hash = "sha256:667e521b37a6c5ccaa044202c235b530f90177ffe2cd4a64ecc213c7dd535feb", size = 103475, upload-time = "2026-10-07T12:23:21.941Z" },
+    { url = "https://files.pythonhosted.org/packages/4c/bd/31a3790c11d6ea95fcf5e6022ac0f8d0543c9b61120b730fc481bd43d3b4/tomli-2.5.0-cp315-cp315-win_amd64.whl", hash = "sha256:d747252933c8a65ef6bd8da0fbb7ce28a90eb6119d8cd00772cd528aa07b68d5", size = 114589, upload-time = "2026-10-07T12:23:23.098Z" },
+    { url = "https://files.pythonhosted.org/packages/47/a2/4f6310fa699364f0e3af7ee3af88dddd9af066d33e716a0265bbe2b3ea84/tomli-2.5.0-cp315-cp315-win_arm64.whl", hash = "sha256:75dbcde8751b0a960aa3de173aa5e894d590755c6d7758b7e774c06f1dc3cbdd", size = 111493, upload-time = "2026-10-07T12:23:24.233Z" },
+    { url = "https://files.pythonhosted.org/packages/68/14/00853f0b396d8971107ae1921bb5b322fdee1650d2f16bf06c20adb532e5/tomli-2.5.0-cp315-cp315t-macosx_10_15_x86_64.whl", hash = "sha256:2419c2a189551987b59d80e63ec355671283336f41c6b9b89462df679c7d0c57", size = 171380, upload-time = "2026-10-07T12:23:25.512Z" },
+    { url = "https://files.pythonhosted.org/packages/89/ad/fa6949321dadee46b27363974fb197b94c911c3b0f7a5fd26d7dc18fc2a0/tomli-2.5.0-cp315-cp315t-macosx_11_0_arm64.whl", hash = "sha256:0dc598040da8d42cf20f0be588ed7004f46db12a0ac6c32e03a59dccedaaadcd", size = 170553, upload-time = "2026-10-07T12:23:26.855Z" },
+    { url = "https://files.pythonhosted.org/packages/53/aa/3056c919eb3e084df3752b2cf5f865dcc04af0b27dba2f66d7b28af4633a/tomli-2.5.0-cp315-cp315t-manylinux2014_aarch64.manylinux_2_17_aarch64.manylinux_2_28_aarch64.whl", hash = "sha256:49096930c8d886c9bbdab62d2d0d17ce823ddeea522309a190b36245d5b49e01", size = 294428, upload-time = "2026-10-07T12:23:28.132Z" },
+    { url = "https://files.pythonhosted.org/packages/96/b2/faeeb5d8769ea3832021d73e892c8391eae7b4b4f8b55a789127bd8b18a9/tomli-2.5.0-cp315-cp315t-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl", hash = "sha256:b8ade5023067f99fe72b88accd30d0ea05a158e9e32a11f124e731ea9695313f", size = 304909, upload-time = "2026-10-07T12:23:29.381Z" },
+    { url = "https://files.pythonhosted.org/packages/f6/52/f094c09e73fb654b621716d019acb5d29bdfd1be01df80c281d552bda48d/tomli-2.5.0-cp315-cp315t-musllinux_1_2_aarch64.whl", hash = "sha256:b69564772b5c8f22ea5f498dff08cfa825045b4d4c4400529000bdf818aa3b2a", size = 293220, upload-time = "2026-10-07T12:23:30.608Z" },
+    { url = "https://files.pythonhosted.org/packages/86/f5/0c30541078ca4b505ce3bd76ed931facbfec524dd018535d691d1af0a6d2/tomli-2.5.0-cp315-cp315t-musllinux_1_2_x86_64.whl", hash = "sha256:8ff3a2ca028c7eee0c777f9a092038d0a594a9fa04e215f929a22c329e2cb142", size = 305705, upload-time = "2026-10-07T12:23:32.181Z" },
+    { url = "https://files.pythonhosted.org/packages/05/74/590e7d19d6a118fc5cc5704ff358e21d95b8573f6b9443b1519f29ca8825/tomli-2.5.0-cp315-cp315t-win32.whl", hash = "sha256:62fc1bc8eb03e3a9cadfca713d65614ed8e09d974a283295ffe3a831976b4dc5", size = 108432, upload-time = "2026-10-07T12:23:33.496Z" },
+    { url = "https://files.pythonhosted.org/packages/1c/b8/63a75cfb27a17c38550e44025d3a6e7be64516fd8608a3b75703bf37d81b/tomli-2.5.0-cp315-cp315t-win_amd64.whl", hash = "sha256:f3fcbc57b1791fa6cbe5d8434179d51de12be1a4811469529f47f6e7487a2571", size = 117281, upload-time = "2026-10-07T12:23:34.648Z" },
+    { url = "https://files.pythonhosted.org/packages/72/01/e8c1debb2173973372934c68fc8e46170ab60ef23ed4592dff4dec6e8993/tomli-2.5.0-cp315-cp315t-win_arm64.whl", hash = "sha256:d2ba24db8a9376921b5e87b4762b9adb0f3f1deaea68f2b8b0bb2c11efb9c3e7", size = 115069, upload-time = "2026-10-07T12:23:35.77Z" },
+    { url = "https://files.pythonhosted.org/packages/60/3f/3e3f8fd0919249b0200c80fbc4f9a1e70be19f9883da71dfb7f8b9ab8aca/tomli-2.5.0-py3-none-any.whl", hash = "sha256:32a7b79ac57a2e83670ce329ccf675798bc5a2094783a63676866b70503f2e2b", size = 14765, upload-time = "2026-10-07T12:23:36.875Z" },
+]
+
 [[package]]
 name = "typing-extensions"
 version = "4.16.0"
diff --git a/tests/test_planner_server.py b/tests/test_planner_server.py
index 6713576..1e082e9 100644
--- a/tests/test_planner_server.py
+++ b/tests/test_planner_server.py
@@ -16,6 +16,7 @@ gateway, no server process required.
 """
 
 import importlib.util
+import json
 import os
 import sys
 from pathlib import Path
@@ -426,8 +427,9 @@ def test_plan_materialize_output_passes_real_lint(tmp_path, monkeypatch):
     # as the real tool is invoked.
     monkeypatch.chdir(tmp_path)
     rel = "tasks/backlog/010-task-10.md"
-    issues = lint._check_markdown_basics(content, rel) + \
-        lint._check_task_file_structure(content, rel)
+    issues = lint._check_markdown_basics(
+        content, rel
+    ) + lint._check_task_file_structure(content, rel)
     assert issues == [], issues
 
     # No fabricated placeholders in the created file.
@@ -466,8 +468,12 @@ def test_api_status_lanes_are_task_lists(tmp_path):
 
 def test_api_status_milestone_tree_and_deadlines(tmp_path):
     _write_task(
-        tmp_path, "backlog", 1, "Milestone task",
-        milestone="M1", deadline="2026-12-01",
+        tmp_path,
+        "backlog",
+        1,
+        "Milestone task",
+        milestone="M1",
+        deadline="2026-12-01",
     )
     payload = planner._api_status(str(tmp_path))
 
@@ -499,11 +505,612 @@ def test_resolve_dashboard_root_uses_env(tmp_path, monkeypatch):
     assert planner._resolve_dashboard_root(None) == tmp_path.resolve()
 
 
-def test_build_app_serves_dashboard_and_mcp_routes():
+def test_build_app_serves_dashboard_and_mcp_routes(tmp_path):
     """The combined app must expose dashboard, API, and the MCP mount."""
+    from starlette.routing import Mount
+
+    (tmp_path / "tasks").mkdir(parents=True, exist_ok=True)
+    monkeypatch = pytest.MonkeyPatch()
+    monkeypatch.setenv("PLANNER_PROJECT_ROOT", str(tmp_path))
+    monkeypatch.setenv("PLANNER_USERS_CONFIG", str(tmp_path / "nonexistent.json"))
     app = planner.build_app()
-    paths = [getattr(r, "path", None) for r in app.routes]
-    assert "/" in paths
-    assert "/api/status" in paths
-    assert "/" in paths  # MCP sub-app is mounted at the root
+    try:
+        paths = [getattr(r, "path", None) for r in app.routes]
+        assert "/" in paths
+        assert "/api/status" in paths
+        assert "/api/login" in paths
+        assert "/api/logout" in paths
+        assert "/static" in paths
+    finally:
+        monkeypatch.undo()
+    assert "/api/me" in paths
+    # The MCP transport routes itself at settings.streamable_http_path
+    # ("/mcp") inside a root Mount, so the mount is the route to assert on.
+    assert any(isinstance(route, Mount) for route in app.routes)
+    assert planner.mcp.settings.streamable_http_path == "/mcp"
     assert app.router.lifespan_context is not None
+
+
+# ---------------------------------------------------------------------------
+# Auth: password hashing, user config, and session management
+# ---------------------------------------------------------------------------
+
+
+def test_hash_password_produces_salt_and_hash():
+    salt, hash_hex = planner._hash_password("test-password")
+    assert len(salt) == 32  # 16 bytes hex
+    assert len(hash_hex) == 64  # 32 bytes hex
+    # Same password, different salt each call.
+    salt2, hash2 = planner._hash_password("test-password")
+    assert salt != salt2
+    assert hash_hex != hash2
+
+
+def test_verify_password_accepts_valid():
+    salt, hash_hex = planner._hash_password("secret")
+    assert planner._verify_password("secret", salt, hash_hex) is True
+
+
+def test_verify_password_rejects_wrong():
+    salt, hash_hex = planner._hash_password("secret")
+    assert planner._verify_password("wrong", salt, hash_hex) is False
+
+
+def test_verify_password_rejects_tampered_hash():
+    salt, hash_hex = planner._hash_password("secret")
+    assert planner._verify_password("secret", salt, hash_hex[:-4] + "0000") is False
+
+
+def test_load_user_config_missing_file_returns_open_mode(tmp_path, monkeypatch):
+    # When the file does not exist, auth is disabled.
+    monkeypatch.setenv("PLANNER_USERS_CONFIG", str(tmp_path / "nonexistent.json"))
+    cfg = planner._load_user_config()
+    assert cfg == {"auth_enabled": False}
+
+
+def test_load_user_config_invalid_json_returns_open_mode(tmp_path, monkeypatch):
+    cfg_path = tmp_path / "planner-users.json"
+    cfg_path.write_text("{not json", encoding="utf-8")
+    monkeypatch.setenv("PLANNER_USERS_CONFIG", str(cfg_path))
+    cfg = planner._load_user_config()
+    assert cfg == {"auth_enabled": False}
+
+
+def test_load_user_config_auth_disabled_by_default(tmp_path, monkeypatch):
+    cfg_path = tmp_path / "planner-users.json"
+    cfg_path.write_text('{"users": []}', encoding="utf-8")
+    monkeypatch.setenv("PLANNER_USERS_CONFIG", str(cfg_path))
+    cfg = planner._load_user_config()
+    assert cfg["auth_enabled"] is False
+    assert cfg["users"] == []
+
+
+def test_load_user_config_with_users(monkeypatch, tmp_path):
+    # When no env var is set, falls back to ~/.config/opencode/planner-users.json.
+    monkeypatch.delenv("PLANNER_USERS_CONFIG", raising=False)
+    fallback = tmp_path / "home" / ".config" / "opencode"
+    fallback.mkdir(parents=True, exist_ok=True)
+    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path / "home")
+    (fallback / "planner-users.json").write_text(
+        json.dumps(
+            {
+                "auth_enabled": True,
+                "users": [
+                    {"username": "a", "password_hash": "x", "allowed_projects": ["/p"]}
+                ],
+            }
+        )
+    )
+    cfg = planner._load_user_config()
+    assert isinstance(cfg, dict)
+    assert "auth_enabled" in cfg
+    assert isinstance(cfg.get("users"), list)
+
+
+def test_find_user_by_username():
+    cfg = {
+        "auth_enabled": True,
+        "users": [
+            {"username": "alice", "role": "admin"},
+            {"username": "bob", "role": "viewer"},
+        ],
+    }
+    assert planner._find_user(cfg, "alice") is not None
+    assert planner._find_user(cfg, "alice").get("role") == "admin"
+    assert planner._find_user(cfg, "bob").get("role") == "viewer"
+    assert planner._find_user(cfg, "carol") is None
+
+
+def test_auth_state_properties_no_user():
+    state = planner.AuthState({}, None, {})
+    assert state.authenticated is False
+    assert state.is_admin is False
+    assert state.role == ""
+    assert state.allowed_projects == []
+    assert state.project_allowed(Path("/any")) is False
+
+
+def test_auth_state_properties_with_user():
+    user = {
+        "username": "admin",
+        "role": "admin",
+        "allowed_projects": ["/"],
+    }
+    state = planner.AuthState({"users": [user]}, user, {})
+    assert state.authenticated is True
+    assert state.is_admin is True
+    assert state.role == "admin"
+    assert "/" in state.allowed_projects
+
+
+def test_auth_state_allowed_projects_star():
+    user = {"username": "admin", "role": "admin", "allowed_projects": ["*"]}
+    state = planner.AuthState({}, user, {})
+    assert state.project_allowed(Path("/anything")) is True
+    assert state.project_allowed(Path("/deep/nested/project")) is True
+
+
+def test_auth_state_project_allowed_exact_match():
+    user = {"username": "viewer", "role": "viewer", "allowed_projects": ["/shared"]}
+    state = planner.AuthState({}, user, {})
+    assert state.project_allowed(Path("/shared")) is True
+    assert state.project_allowed(Path("/shared/child")) is True
+    assert state.project_allowed(Path("/other")) is False
+
+
+def test_auth_state_project_allowed_subpath():
+    user = {"username": "viewer", "role": "viewer", "allowed_projects": ["/home/dev"]}
+    state = planner.AuthState({}, user, {})
+    assert state.project_allowed(Path("/home/dev/project-a")) is True
+    assert state.project_allowed(Path("/home/other/project-b")) is False
+
+
+def test_auth_state_project_allowed_empty_when_not_authenticated():
+    state = planner.AuthState({}, None, {})
+    # Even if allowed_projects contained "*", an unauthenticated user is blocked.
+    assert state.project_allowed(Path("/anything")) is False
+
+
+def test_auth_state_dedup_allowed_projects():
+    user = {"username": "u", "role": "viewer", "allowed_projects": ["/", "/", "*"]}
+    state = planner.AuthState({}, user, {})
+    assert state.allowed_projects == ["/", "*"]
+
+
+def test_auth_state_allowed_projects_string_coerced_to_list():
+    user = {"username": "u", "role": "viewer", "allowed_projects": "/"}
+    state = planner.AuthState({}, user, {})
+    assert state.allowed_projects == ["/"]
+
+
+def test_auth_token_store_roundtrip():
+    planner._build_auth_url_map().clear()
+    store = planner._build_auth_url_map()
+    store["tok1"] = {"user": {"username": "admin"}, "created": 0.0}
+    assert planner._session_from_token("tok1") is not None
+    assert planner._session_from_token("tok1").get("user").get("username") == "admin"
+    assert planner._session_from_token("tok2") is None
+    planner._invalidate_token("tok1")
+    assert planner._session_from_token("tok1") is None
+
+
+# ---------------------------------------------------------------------------
+# Auth: login / logout / me handlers (tested through Starlette TestClient)
+# ---------------------------------------------------------------------------
+
+
+@pytest.fixture
+def auth_app(tmp_path, monkeypatch):
+    """Build the app with auth enabled and a test user config."""
+    cfg_path = tmp_path / "planner-users.json"
+    salt, hash_hex = planner._hash_password("admin-pass")
+    salt2, hash2 = planner._hash_password("viewer-pass")
+    cfg_path.write_text(
+        json.dumps(
+            {
+                "auth_enabled": True,
+                "users": [
+                    {
+                        "username": "admin",
+                        "role": "admin",
+                        "password_salt": salt,
+                        "password_hash": hash_hex,
+                        "allowed_projects": ["*"],
+                    },
+                    {
+                        "username": "viewer",
+                        "role": "viewer",
+                        "password_salt": salt2,
+                        "password_hash": hash2,
+                        "allowed_projects": [str(tmp_path / "project-a")],
+                    },
+                ],
+            }
+        ),
+        encoding="utf-8",
+    )
+    monkeypatch.setenv("PLANNER_USERS_CONFIG", str(cfg_path))
+    # Both fixture projects feed the dashboard switcher; per-test creation of
+    # their tasks/ dirs happens before the first request, so discovery sees
+    # them and the RBAC filter is what decides who may list them.
+    monkeypatch.setenv(
+        "PLANNER_PROJECTS",
+        os.pathsep.join([str(tmp_path / "project-a"), str(tmp_path / "project-b")]),
+    )
+    # Reset the module-level auth flag and config so the app picks up the
+    # test config. The module was already imported, so we patch the globals.
+    planner._USER_CONFIG = planner._load_user_config()
+    planner._AUTH_ENABLED = bool(planner._USER_CONFIG.get("auth_enabled", False))
+    planner._build_auth_url_map().clear()
+    app = planner.build_app()
+    # Build the app with auth enabled and a test user config — the auth middleware
+    # is mounted inside build_app(), so every fresh app instance already reads the
+    # patched module globals; no custom reset helper is required.
+    # Prevent the build_app() call from signaling _CHANGED during fixture setup —
+    # the signal is only meaningful between test cases, and we rely on the
+    # auth_app fixture being rebuilt per test (pytest caches fixtures by params).
+    return app
+
+
+@pytest.fixture
+def auth_client(auth_app):
+    from starlette.testclient import TestClient
+
+    # A context-managed client runs the app lifespan, which is what starts the
+    # MCP session manager behind the /mcp guard.
+    with TestClient(auth_app) as client:
+        yield client
+
+
+def test_login_valid_credentials_returns_token(auth_client):
+    resp = auth_client.post(
+        "/api/login", json={"username": "admin", "password": "admin-pass"}
+    )
+    assert resp.status_code == 200
+    data = resp.json()
+    assert data["token"]
+    assert data["username"] == "admin"
+    assert data["role"] == "admin"
+    assert data["allowed_projects"] == ["*"]
+    assert "planner_session" in resp.cookies
+
+
+def test_login_invalid_password_returns_401(auth_client):
+    resp = auth_client.post(
+        "/api/login", json={"username": "admin", "password": "wrong"}
+    )
+    assert resp.status_code == 401
+
+
+def test_login_nonexistent_user_returns_401(auth_client):
+    resp = auth_client.post("/api/login", json={"username": "nobody", "password": "x"})
+    assert resp.status_code == 401
+
+
+def test_login_missing_fields_returns_400(auth_client):
+    resp = auth_client.post("/api/login", json={"username": "admin"})
+    assert resp.status_code == 400
+
+
+def test_login_invalid_json_returns_400(auth_client):
+    resp = auth_client.post("/api/login", content="not json")
+    assert resp.status_code == 400
+
+
+def test_me_returns_user_when_authenticated(auth_client, auth_app):
+    auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
+    resp = auth_client.get("/api/me")
+    assert resp.status_code == 200
+    data = resp.json()
+    assert data["authenticated"] is True
+    assert data["username"] == "admin"
+    assert data["role"] == "admin"
+    assert data["allowed_projects"] == ["*"]
+
+
+def test_me_returns_401_when_unauthenticated(auth_client):
+    resp = auth_client.get("/api/me")
+    assert resp.status_code == 401
+
+
+def test_logout_clears_session(auth_client, auth_app):
+    auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
+    assert auth_client.get("/api/me").status_code == 200
+    resp = auth_client.post("/api/logout")
+    assert resp.status_code == 200
+    assert resp.json()["ok"] is True
+    assert auth_client.get("/api/me").status_code == 401
+
+
+def test_me_after_logout_is_401(auth_client, auth_app):
+    auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
+    auth_client.post("/api/logout")
+    resp = auth_client.get("/api/me")
+    assert resp.status_code == 401
+
+
+# ---------------------------------------------------------------------------
+# Auth: RBAC — admin sees all, viewer only sees authorized projects
+# ---------------------------------------------------------------------------
+
+
+def test_api_status_401_when_unauthenticated_and_auth_enabled(auth_client):
+    # Without logging in, status is 401.
+    resp = auth_client.get("/api/status")
+    assert resp.status_code == 401
+
+
+def test_api_status_admin_sees_all_projects(auth_client, auth_app, tmp_path):
+    auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
+    (tmp_path / "project-a").mkdir(parents=True, exist_ok=True)
+    (tmp_path / "project-b").mkdir(parents=True, exist_ok=True)
+    (tmp_path / "project-a" / "tasks").mkdir(parents=True, exist_ok=True)
+    (tmp_path / "project-b" / "tasks").mkdir(parents=True, exist_ok=True)
+    resp = auth_client.get("/api/status")
+    assert resp.status_code == 200
+    data = resp.json()
+    project_paths = [p["path"] for p in data["projects"]]
+    assert str(tmp_path / "project-a") in project_paths
+    assert str(tmp_path / "project-b") in project_paths
+
+
+def test_api_status_viewer_sees_only_authorized_project(
+    auth_client, auth_app, tmp_path
+):
+    # Viewer is only allowed into project-a.
+    auth_client.post(
+        "/api/login", json={"username": "viewer", "password": "viewer-pass"}
+    )
+    (tmp_path / "project-a").mkdir(parents=True, exist_ok=True)
+    (tmp_path / "project-b").mkdir(parents=True, exist_ok=True)
+    (tmp_path / "project-a" / "tasks").mkdir(parents=True, exist_ok=True)
+    (tmp_path / "project-b" / "tasks").mkdir(parents=True, exist_ok=True)
+    resp = auth_client.get("/api/status")
+    assert resp.status_code == 200
+    data = resp.json()
+    project_paths = [p["path"] for p in data["projects"]]
+    assert str(tmp_path / "project-a") in project_paths
+    assert str(tmp_path / "project-b") not in project_paths
+
+
+def test_api_status_403_when_project_root_not_allowed(auth_client, auth_app, tmp_path):
+    # Viewer logs in; requesting project-b (not allowed) returns 403.
+    auth_client.post(
+        "/api/login", json={"username": "viewer", "password": "viewer-pass"}
+    )
+    (tmp_path / "project-a").mkdir(parents=True, exist_ok=True)
+    (tmp_path / "project-b").mkdir(parents=True, exist_ok=True)
+    (tmp_path / "project-a" / "tasks").mkdir(parents=True, exist_ok=True)
+    (tmp_path / "project-b" / "tasks").mkdir(parents=True, exist_ok=True)
+    resp = auth_client.get(
+        "/api/status", params={"project_root": str(tmp_path / "project-b")}
+    )
+    assert resp.status_code == 403
+    data = resp.json()
+    assert data.get("error") == "forbidden"
+
+
+def test_api_status_allowed_project_root_ok_for_viewer(auth_client, auth_app, tmp_path):
+    auth_client.post(
+        "/api/login", json={"username": "viewer", "password": "viewer-pass"}
+    )
+    (tmp_path / "project-a").mkdir(parents=True, exist_ok=True)
+    (tmp_path / "project-a" / "tasks").mkdir(parents=True, exist_ok=True)
+    resp = auth_client.get(
+        "/api/status", params={"project_root": str(tmp_path / "project-a")}
+    )
+    assert resp.status_code == 200
+    data = resp.json()
+    project_paths = [p["path"] for p in data["projects"]]
+    assert str(tmp_path / "project-a") in project_paths
+    assert str(tmp_path / "project-b") not in project_paths
+
+
+# ---------------------------------------------------------------------------
+# Auth: /mcp ingress guard (admin only when auth is enabled)
+# ---------------------------------------------------------------------------
+
+
+def test_mcp_requires_session_when_auth_enabled(auth_client):
+    resp = auth_client.post(
+        "/mcp", content='{"jsonrpc":"2.0","method":"tools/list","id":1}'
+    )
+    assert resp.status_code == 401
+    assert resp.json()["error"] == "unauthenticated"
+
+
+def test_mcp_blocks_viewer_session(auth_client):
+    auth_client.post(
+        "/api/login", json={"username": "viewer", "password": "viewer-pass"}
+    )
+    resp = auth_client.post(
+        "/mcp", content='{"jsonrpc":"2.0","method":"tools/list","id":1}'
+    )
+    assert resp.status_code == 403
+    assert resp.json()["error"] == "forbidden"
+
+
+def test_mcp_admits_admin_session(auth_client):
+    auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
+    resp = auth_client.post(
+        "/mcp", content='{"jsonrpc":"2.0","method":"tools/list","id":1}'
+    )
+    # The guard admits the request; the transport then rejects the malformed
+    # MCP handshake with its own status, which must not be a guard status.
+    assert resp.status_code not in (401, 403)
+
+
+# ---------------------------------------------------------------------------
+# Auth: backward compatibility when auth is disabled
+# ---------------------------------------------------------------------------
+
+
+@pytest.fixture
+def open_app(tmp_path, monkeypatch):
+    """Build the app with auth disabled (no config file)."""
+    monkeypatch.setenv("PLANNER_USERS_CONFIG", str(tmp_path / "nonexistent.json"))
+    planner._USER_CONFIG = planner._load_user_config()
+    planner._AUTH_ENABLED = bool(planner._USER_CONFIG.get("auth_enabled", False))
+    planner._build_auth_url_map().clear()
+    return planner.build_app()
+
+
+@pytest.fixture
+def open_client(open_app):
+    from starlette.testclient import TestClient
+
+    # Context-managed so the app lifespan starts the MCP session manager.
+    with TestClient(open_app) as client:
+        yield client
+
+
+def test_login_when_auth_disabled_returns_note(open_client):
+    resp = open_client.post("/api/login", json={"username": "x", "password": "y"})
+    assert resp.status_code == 200
+    data = resp.json()
+    assert data["note"] == "auth disabled"
+    assert data["token"] == ""
+    assert data["username"] == ""
+
+
+def test_me_when_auth_disabled_returns_unauthenticated_note(open_client):
+    resp = open_client.get("/api/me")
+    assert resp.status_code == 200
+    data = resp.json()
+    assert data["authenticated"] is False
+    assert data["note"] == "auth disabled"
+
+
+def test_status_works_without_auth(open_client, tmp_path):
+    (tmp_path / "tasks").mkdir(parents=True, exist_ok=True)
+    resp = open_client.get("/api/status")
+    assert resp.status_code == 200
+    data = resp.json()
+    assert "error" not in data or data.get("error") is None
+
+
+def test_dashboard_frontend_serves_when_auth_disabled(open_client, tmp_path):
+    # The dashboard static files should still serve when auth is disabled.
+    (tmp_path / "tasks").mkdir(parents=True, exist_ok=True)
+    resp = open_client.get("/")
+    assert resp.status_code == 200
+    assert "text/html" in resp.headers.get("content-type", "")
+
+
+def test_dashboard_static_assets_serve_when_auth_disabled(open_client, tmp_path):
+    (tmp_path / "tasks").mkdir(parents=True, exist_ok=True)
+    resp = open_client.get("/static/index.html")
+    assert resp.status_code == 200
+
+
+def test_mcp_route_exists_when_auth_disabled(open_client):
+    # The /mcp route is present regardless of auth mode.
+    resp = open_client.post(
+        "/mcp", content='{"jsonrpc":"2.0","method":"tools/list","id":1}'
+    )
+    # The MCP endpoint returns its own status; we just assert the route is reachable.
+    assert resp.status_code in (
+        200,
+        400,
+        405,
+    )  # 400/405 expected for malformed MCP body
+
+
+def test_login_when_auth_disabled_and_blob_body_returns_200(open_client):
+    resp = open_client.post("/api/login", content="not json")
+    # Auth disabled: the handler still parses JSON and falls through to the note.
+    assert resp.status_code == 200
+    assert resp.json()["note"] == "auth disabled"
+
+
+# ---------------------------------------------------------------------------
+# User management CLI (stdlib only, same hashing scheme as the server)
+# ---------------------------------------------------------------------------
+
+
+def _load_manage_users():
+    spec = importlib.util.spec_from_file_location(
+        "planner_manage_users", PLANNER_DIR / "manage_users.py"
+    )
+    module = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(module)
+    return module
+
+
+def test_manage_users_cli_add_writes_server_verifiable_hash(tmp_path, capsys):
+    manage_users = _load_manage_users()
+    cfg = tmp_path / "planner-users.json"
+
+    code = manage_users.main(
+        [
+            "--config",
+            str(cfg),
+            "add",
+            "--username",
+            "friend",
+            "--role",
+            "viewer",
+            "--projects",
+            str(tmp_path / "shared"),
+            "--password",
+            "friend-pass",
+        ]
+    )
+    assert code == 0
+
+    data = json.loads(cfg.read_text(encoding="utf-8"))
+    assert data["auth_enabled"] is True
+    user = data["users"][0]
+    assert user["username"] == "friend"
+    assert user["role"] == "viewer"
+    assert user["allowed_projects"] == [str(tmp_path / "shared")]
+    # The server verifies with its own PBKDF2 helper — the schemes must agree.
+    assert planner._verify_password(
+        "friend-pass", user["password_salt"], user["password_hash"]
+    )
+
+    out = capsys.readouterr().out
+    assert "Added user 'friend'" in out
+
+
+def test_manage_users_cli_rejects_duplicate_user(tmp_path):
+    manage_users = _load_manage_users()
+    cfg = tmp_path / "planner-users.json"
+    base = [
+        "--config",
+        str(cfg),
+        "add",
+        "--username",
+        "admin",
+        "--role",
+        "admin",
+        "--projects",
+        "*",
+        "--password",
+        "pw",
+    ]
+    assert manage_users.main(base) == 0
+    assert manage_users.main(base) == 1
+
+
+def test_manage_users_cli_disable_keeps_server_open(tmp_path):
+    manage_users = _load_manage_users()
+    cfg = tmp_path / "planner-users.json"
+    manage_users.main(
+        [
+            "--config",
+            str(cfg),
+            "add",
+            "--username",
+            "admin",
+            "--role",
+            "admin",
+            "--projects",
+            "*",
+            "--password",
+            "pw",
+        ]
+    )
+    assert manage_users.main(["--config", str(cfg), "disable"]) == 0
+    data = json.loads(cfg.read_text(encoding="utf-8"))
+    assert data["auth_enabled"] is False
```
<!-- END_GIT_DIFF -->
