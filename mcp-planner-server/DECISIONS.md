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
