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
**Factual Git Diff:** Stored in Commit Hash: `d069568fb6c6650af63db0931ea30740b5c3e1d1`
<!-- END_GIT_DIFF -->
