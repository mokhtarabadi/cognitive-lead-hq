# Slice: mcp-planner-server

## Duties

Planner MCP singleton: a capacity-aware, QA-gated planning layer over `tasks/`
Markdown. Reads task files as the single source of truth, enforces dependency,
WIP, milestone, deadline, and QA-budget queue gates, and exposes a local
dashboard on loopback port 8108.

## Files

- `server.py` — MCP daemon entrypoint exposing `brain_turn`-style planning tools
  (`plan_propose`, `plan_materialize`, `claim_next`, `qa_budget`,
  `milestone_status`, `plan_status`, `sprint_daily_agenda`,
  `sprint_check_daily_quota`, `sprint_lock`) plus an embedded HTTP route
  serving the static dashboard on `GET /` and `GET /api/status`.
- `static/index.html` — standalone dark-mode dashboard (no build step).
- `pyproject.toml` / `uv.lock` — runtime deps and lockfile.
- `README.md` / `DECISIONS.md` — Living Folder Docs for this slice.

## HTTP surface (loopback 8108)

| Route | Purpose |
| ----- | ------- |
| `GET /` | Standalone dark-mode dashboard (no build step). |
| `GET /api/status[?project_root=<abs path>]` | JSON status contract the dashboard renders. |
| `POST /mcp` | MCP Streamable HTTP endpoint (tools). |

`/api/status` returns per-lane **task lists** (`lanes`), the milestone tree
(`milestone_tree`), upcoming deadlines (`deadlines`), the pacing figures
(`today` = `done`/`target`/`open`, mirroring `sprint_check_daily_quota`), the
selectable project roots (`projects`), and the root actually reported on
(`project_root`). Lane values are lists, never counts — the dashboard calls
`.map()` on them.

Project resolution order: the `project_root` query parameter, then
`PLANNER_PROJECT_ROOT`, then the nearest ancestor of the working directory
holding `tasks/`, then the working directory. `PLANNER_PROJECTS`
(pathsep-separated absolute paths) adds entries to the dashboard switcher;
`PLANNER_DAILY_TARGET` overrides the daily batch size (default 3).

## Key Risks & Invariants

- `tasks/` Markdown is the canonical source of truth; the planner is a derived
  index (`tasks/.plan/index.json`, gitignored) regenerated per turn.
- Autopilot QA budget: max 1 unresolved QA/review task (general WIP ceiling 3).
- No external integrations in v1 (GitHub/Telegram/Asana/Plane deferred).
- Zero-Autonomous-Commit: agents never `git commit`/`git push`; staging goes
  through `custom_context_stage_and_inject_diff`.
