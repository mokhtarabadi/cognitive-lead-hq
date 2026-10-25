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
**Factual Git Diff:** Stored in Commit Hash: `372df07ae1dedc5d3e71e1b1fa291f1e1c9e6589`
<!-- END_GIT_DIFF -->
