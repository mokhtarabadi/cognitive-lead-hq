# Architectural Decisions: mcp-planner-server

## [2026-10-23] ADR-001: Initial Slice Baseline

- **Context:** Baseline documentation initialized via init-folder-docs.
- **Decision:** Adopting Living Folder Docs standard for this component.
- **Consequences:** All future structural or contract changes must be recorded here.
- **Rollback:** N/A (baseline adoption).

## [2026-10-23] ADR-002: Planner MCP is a derived index over `tasks/` Markdown

- **Context:** The Manager wants a planning layer (capacity, QA gates, milestones,
  dependencies) without introducing a competing task store that could diverge
  from the canonical `tasks/` Kanban files.
- **Decision:** `tasks/` Markdown remains the single source of truth. The planner
  builds a derived, gitignored index (`tasks/.plan/index.json`) regenerated on
  every turn. External platforms (GitHub Projects, Plane, Asana) are deferred to
  v2/v3 because they risk a second source of truth and unverified lifecycle fit.
- **Consequences:** Planner tools (`claim_next`, `plan_materialize`, …) mutate
  `tasks/` Markdown only through validated transitions that pass `lint_task_file`.
- **Rollback:** Disable the server and return to the existing Kanban workflow;
  task files remain readable Markdown throughout.

## [2026-10-24] ADR-003: MCP transport is mounted via `streamable_http_app()` with an explicit lifespan

- **Context:** The combined Starlette app has to serve the dashboard at `/` and
the MCP endpoint on the same loopback port. The first implementation called
`FastMCP.http_app()`, which does not exist in the installed `mcp` 1.30 SDK, and
mounted the returned app at `/mcp` — which would also have double-prefixed the
endpoint, since the transport app already routes itself at
`settings.streamable_http_path` (`/mcp`).
- **Decision:** Build the transport app with `mcp.streamable_http_app()`, mount it
at the root, and enter `mcp_app.router.lifespan_context(mcp_app)` from the parent
app's lifespan. Starlette runs only the parent lifespan and never a `Mount`-ed
sub-app's, so without the explicit enter the session manager task group stays
uninitialised and every request to `/mcp` fails with `RuntimeError: Task group is
not initialized`.
- **Consequences:** Dashboard routes (`/`, `/api/status`) and the MCP endpoint
(`/mcp`) coexist on one loopback listener. A future SDK change to the transport
entrypoint or to `streamable_http_path` must be re-verified against
`tests/test_planner_server.py::test_build_app_serves_dashboard_and_mcp_routes` and
a live `initialize` probe.
- **Rollback:** Run `uvicorn` directly on `mcp.streamable_http_app()` and drop the
dashboard routes; the planning tools keep working unchanged.

## [2026-10-24] ADR-004: `/api/status` ships task lists, not counts

- **Context:** The dashboard renders each lane by mapping over its items and
builds the milestone tree and timeline from the same payload. The first contract
returned a scalar count per lane and no `milestone_tree`/`deadlines`, so
`items.map` threw inside `render()`, the exception was swallowed by the fetch
catch block, and the board blanked while the UI reported "Server unreachable".
A hard-coded `Path.cwd()` root also made the dashboard report an empty board
under systemd, whose WorkingDirectory is the install directory.
- **Decision:** `/api/status` returns JSON-serialisable task briefs per lane, a
`milestone_tree` keyed by `**Milestone:**`, a sorted `deadlines` list, the
`today` pacing triple (`done`/`target`/`open`, derived from the same rule as
`sprint_check_daily_quota`), and a `projects` list for the switcher. The root is
resolved from the `project_root` query parameter → `PLANNER_PROJECT_ROOT` →
nearest ancestor holding `tasks/` → cwd.
- **Consequences:** The contract is pinned by
`tests/test_planner_server.py::test_api_status_lanes_are_task_lists` and friends;
any change to lane shape breaks a test rather than silently blanking the UI.
`PLANNER_PROJECTS` is the only way to offer several roots in the switcher.
- **Rollback:** Revert the `/api/status` handler and the dashboard `render()`
together — they share one contract and must never be changed independently.

## [2026-10-24] ADR-005: Optional cookie-session auth with per-user project scoping

- **Context:** The dashboard is useful from a phone, so the Manager wants it
reachable through a Cloudflare Tunnel. Loopback-only access was the sole control
until now, which stops working the moment the port leaves the host. At the same
time the local OpenCode clients call `/mcp` with no credentials and must keep
working untouched.
- **Decision:** Auth is opt-in through `~/.config/opencode/planner-users.json`
(`PLANNER_USERS_CONFIG` override). A missing, unreadable, non-object, or
`auth_enabled: false` file — or one with no users — keeps the server in open
local mode with no 401s and no filtering. When enabled: PBKDF2-HMAC-SHA256
(600k iterations, 16-byte `secrets` salt, `hmac.compare_digest`) with stdlib
only; opaque in-memory session tokens in an `HttpOnly` `SameSite=Lax`
`planner_session` cookie (7-day TTL, dropped on restart); `/api/status` answers
401 unauthenticated, filters `projects` to `allowed_projects` (`"*"` = all) and
403s an explicit `project_root` outside them; `/mcp` requires an **admin**
session while viewers stay read-only. A viewer with no explicit root falls back
to their first allowed project rather than being denied.
- **Consequences:** One server serves both audiences: local tooling stays
credential-free in open mode, remote browsers sign in. Restart is required after
a user edit because the config is read when the app is built. A restart also
signs everyone out — acceptable, and it means no long-lived signing secret lives
on disk. `/mcp` over the tunnel is blocked at ingress (`http_status:404`), so
tool execution never depends on the guard alone. Pinned by the auth tests plus
the CLI test that hashes through the server's own verifier.
- **Rollback:** Delete `planner-users.json` or run `manage_users.py disable`;
the server returns to open local mode with no code change. Full code rollback is
`server.py` + `static/index.html` + `manage_users.py` reverted together.
- **Superseded in part:** the `/mcp` admin-session requirement only — see
ADR-006 below. Session auth, scoping, and the CLI remain as decided here.

## [2026-10-24] ADR-006: `/mcp` is auth-free on loopback; the edge is the gate

- **Context:** With auth enabled, the `/mcp` guard returned 401 to every
  credential-free caller, and OpenCode's local clients connect with no cookie.
  The transport therefore broke whenever the Manager turned authentication on
  for the dashboard — the two requirements collided inside one process.
  The `/mcp` route is already unreachable from outside: the Cloudflare Tunnel
  ingress answers `http_status: 404` for `^/mcp(/.*)?$` before the catch-all
  rule, so no remote request ever reaches the process.
- **Decision:** `_guarded_mcp_app` passes every request straight to the MCP
  transport, in open mode and with auth enabled alike. No `SESSION_COOKIE`
  check, no admin-role check, no 401/403 from that path. `/`, `/static/*`,
  `/api/login`, `/api/logout`, `/api/me`, and `/api/status` keep their session
  checks unchanged — the dashboard is still authenticated.
- **Consequences:** Local MCP clients work in both auth modes, which removes the
  old "set `auth_enabled: false` or lose your tools" coupling. Tool execution
  now trusts the bind (127.0.0.1) plus the tunnel ingress instead of an
  in-process guard, so **the ingress rule is load-bearing for security**: adding
  a catch-all tunnel rule before the `/mcp` 404, or rebinding the port off
  loopback, exposes unauthenticated tool execution. The ingress ordering and
  the external `curl …/mcp` → 404 probe in `docs/services.md` are the checks
  that hold this. Pinned by
  `tests/test_planner_server.py::test_mcp_open_without_session_when_auth_enabled`
  and `::test_api_status_stays_guarded_while_mcp_is_open`.
- **Rollback:** Restore the cookie/role checks in `_guarded_mcp_app` and the
  three guard tests; no config or dashboard change is involved.
