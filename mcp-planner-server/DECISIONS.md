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

## [2026-10-24] ADR-007: `GET /api/task` is a guarded, lane-confined read

- **Context:** The dashboard needs to open a task's full Markdown (todos,
  acceptance criteria, `## Factual Git Diff`) in a modal, and `/api/status`
  ships only briefs. A naive `?path=` reader would turn the loopback dashboard
  into an arbitrary-file reader; the slice has no containment helper today
  (`_explicit_project_root` never consults `allowed_projects`, and
  `_resolve_dashboard_root` resolves any absolute `?project_root=`).
- **Decision:** `/api/task` accepts `?id=` (resolved through `_find_task_by_id`
  over `_load_all_tasks`, int-normalized) or `?path=tasks/<lane>/<file>.md`
  (resolved through the new `_safe_task_path`). `id` wins when both arrive.
  The path form accepts exactly three segments, a lane from `TASK_LANES`, a
  `.md` suffix, no `..`/`.`/backslash/drive-colon/absolute prefix, and the
  resolved candidate must remain inside the project root. Authorization reuses
  `AuthState.project_allowed` and the `_api_status` fallback to the first
  allowed root. Status mapping is explicit: 400 missing param, 401 no session,
  403 outside grants **and** unsafe path (never 404, so the route is not an
  existence oracle), 404 unknown id/missing file, 500 unexpected — the
  `_api_status` blanket `except → 200 {"error": …}` is deliberately not copied.
- **Consequences:** The modal can deep-link by id or path and the route remains
  a read-only view of `tasks/` Markdown. `GET /` stays unauthenticated by
  design (ADR-005 changed the data routes only); this route gates like
  `/api/status`. Traversal attempts are logged as 403 by the client, which
  cannot distinguish "outside your grants" from "not a task path". Pinned by
  the `/api/task` tests in `tests/test_planner_server.py` (route presence, by id,
  by path, 400, 401, 403 cross-project, 403 traversal).
- **Rollback:** Remove the route from `build_app`, drop `_api_task` and
  `_safe_task_path`, and remove the route from the route-existence test; the
  dashboard falls back to the brief-only lanes.

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

## [2026-10-24] ADR-008: Plan buckets are computed per request, not stored

- **Context:** the Manager asked for day/week/month planning views with charts and deadline pressure. Completion history does not exist in `tasks/` Markdown, and adding a second store would break the "Markdown is the single source of truth" rule.
- **Decision:** `GET /api/plan` derives `days`, `weeks`, `trend` (14 days), `totals` and `alerts` from `_load_all_tasks` on every request. Week rows sum the day rows they contain; month builds every day of the month and groups by ISO week. Open work without a deadline is attributed to the current bucket so the view is never empty. `done` is a completed-lane task with a deadline in the bucket, and the UI states that history is not stored. Capacity comes from `PLANNER_WEEKLY_CAPACITY`.
- **Consequences:** no migration, no cache to invalidate, and a slow project with thousands of tasks pays a full scan per request (acceptable at 337 tasks; revisit if it grows). Charts read `trend`, so a future history feature only needs to extend that array.
- **Rollback:** remove the route and the three dashboard panels; `/api/status` keeps working unchanged.
