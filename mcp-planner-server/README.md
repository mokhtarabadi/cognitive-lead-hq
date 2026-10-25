# Slice: mcp-planner-server

## Duties

Planner MCP singleton: a capacity-aware, QA-gated planning layer over `tasks/`
Markdown. Reads task files as the single source of truth, enforces dependency,
WIP, milestone, deadline, and QA-budget queue gates, and exposes a local
dashboard on loopback port 8108.

## Files

- `server.py` — MCP daemon entrypoint exposing `brain_turn`-style planning tools
  (`plan_propose`, `plan_materialize`, `schedule_tasks`, `claim_next`, `qa_budget`,
  `milestone_status`, `plan_status`, `sprint_daily_agenda`,
  `sprint_check_daily_quota`, `sprint_lock`) plus an embedded HTTP route
  serving the static dashboard on `GET /` and `GET /api/status`, the auth
  routes, and the admin-guarded MCP endpoint.
- `manage_users.py` — stdlib-only user CLI (`add`, `update`, `remove`,
  `list`, `enable`, `disable`) writing `~/.config/opencode/planner-users.json`.
- `static/index.html` — standalone dark-mode dashboard (no build step),
  including the login modal and the user badge.
- `pyproject.toml` / `uv.lock` — runtime deps and lockfile.
- `README.md` / `DECISIONS.md` — Living Folder Docs for this slice.

## HTTP surface (loopback 8108)

| Route                                                     | Purpose                                                                                                                                                                                                   |
| --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET /`                                                   | Standalone dark-mode dashboard (no build step).                                                                                                                                                           |
| `GET /static/*`                                           | Dashboard assets (same `static/` directory).                                                                                                                                                              |
| `GET /api/status[?project_root=<abs path>]`               | JSON status contract the dashboard renders.                                                                                                                                                               |
| `GET /api/task?id=<id>` or `?path=tasks/<lane>/<file>.md` | One task file as `{id, path, lane, title, markdown}` for the dashboard modal. `id` wins when both are sent. 400 no param, 401 no session, 403 outside grants or unsafe path, 404 unknown, 500 unexpected. |
| `POST /api/login`                                         | `{"username","password"}` → `{token, username, role, allowed_projects}` + `HttpOnly` cookie.                                                                                                              |
| `POST /api/logout`                                        | Invalidates the session and clears the cookie.                                                                                                                                                            |
| `GET /api/me`                                             | Current user, or 401 when signed out (200 + `note: "auth disabled"` in open mode).                                                                                                                        |
| `POST /mcp`                                               | MCP Streamable HTTP endpoint (tools). Auth-free on loopback; the tunnel 404s it.                                                                                                                          |

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

## Authentication and RBAC (optional, off by default)

- **Config:** `~/.config/opencode/planner-users.json`, overridable with
  `PLANNER_USERS_CONFIG`. Shape: `{"auth_enabled": bool, "users": [{"username",
"role": "admin"|"viewer", "password_salt", "password_hash",
"allowed_projects": ["*"] | ["/abs/path", ...]}]}`.
- **Open mode:** no file, unreadable file, invalid JSON, `auth_enabled: false`,
  or an empty `users` list ⇒ every request behaves exactly as before
  (no 401, no filtering). This is the backward-compatibility contract.
- **Hashing:** `hashlib.pbkdf2_hmac("sha256", …, 600_000)` with a 16-byte
  `secrets` salt, verified with `hmac.compare_digest`. No third-party crypto.
- **Sessions:** `secrets.token_urlsafe(32)` held in memory, `HttpOnly` +
  `SameSite=Lax` cookie `planner_session`, 7-day TTL. A restart drops every
  session by design (re-login is cheap; no server-side secret to leak).
- **Scoping:** `/api/status` returns 401 until sign-in, 403 when an explicit
  `project_root` is outside `allowed_projects`, and filters `projects` to the
  allowed roots. Without an explicit root a viewer falls back to their first
  allowed project instead of being denied.
- **`/mcp`:** auth-free in every mode, including with auth enabled. Local MCP
  clients call it on loopback with no cookie; the Cloudflare Tunnel ingress
  answers `404` for `/mcp` before the catch-all rule, so remote callers never
  reach it. The dashboard, `/`, and every `/api/*` route keep their session
  checks.
- **Known limitation:** tool calls are authorized at the transport level, not
  per argument — an admin whose `allowed_projects` is restricted can still pass
  any `project_root` to a tool. Admins are expected to hold the wildcard grant;
  use a viewer account for read-only scoped access.

Manage users (stdlib CLI, no venv):

```bash
python3 manage_users.py add --username admin --role admin --projects "*"
python3 manage_users.py add --username friend --role viewer --projects /path/to/shared-project
python3 manage_users.py list
python3 manage_users.py update --username friend --add-project /another/project
python3 manage_users.py disable        # back to open local mode
```

Config is read when the app is built, so `systemctl --user restart mcp-planner`
after any user change.

## Cloudflare Tunnel (external dashboard access)

Keep the unit on `127.0.0.1` and let `cloudflared` dial out. The ingress
config must block `/mcp` **before** the catch-all rule so tool execution never
leaves the host:

```yaml
# ~/.cloudflared/config.yml
tunnel: planner
credentials-file: /home/me/.cloudflared/<tunnel-uuid>.json

ingress:
  - hostname: planner.example.com
    path: ^/mcp(/.*)?$
    service: http_status:404
  - hostname: planner.example.com
    service: http://127.0.0.1:8108
  - service: http_status:404
```

`cloudflared tunnel create planner` → `cloudflared tunnel route dns planner
planner.example.com` → `sudo cloudflared service install`. Enable auth before
the tunnel goes live, then verify: `https://planner.example.com/mcp` → 404,
`/` → 200 with the login modal. Full walkthrough in `docs/services.md`.

## Key Risks & Invariants

- `tasks/` Markdown is the canonical source of truth; the planner is a derived
  index (`tasks/.plan/index.json`, gitignored) regenerated per turn.
- Autopilot QA budget: max 1 unresolved QA/review task (general WIP ceiling 3).
- `/mcp` trusts the bind and the tunnel ingress, not session auth: the
  `^/mcp(/.*)?$ → 404` ingress rule must stay ahead of the catch-all, and the
  port must never leave `127.0.0.1`. Breaking either exposes tool execution.
- No external integrations in v1 (GitHub/Telegram/Asana/Plane deferred).
- Zero-Autonomous-Commit: agents never `git commit`/`git push`; staging goes
  through `custom_context_stage_and_inject_diff`.

## Planning API (`GET /api/plan`)

`GET /api/plan?window=day|week|month[&project_root=<abs path>]` returns the
cockpit buckets: `days`, `weeks`, `trend` (14 days), `totals` and `alerts`
(`overdue`, `today`, `soon` = next three days). Buckets are computed from
`tasks/` at request time — there is no second store.

- `day` is today; `week` is Monday–Sunday of the current week (safe mid-week);
  `month` covers every day of the current month and groups it by ISO week.
- Week rows sum the days they contain (`open`, `in_progress`, `done`,
  `estimate_hours`) and compare the estimate against `PLANNER_WEEKLY_CAPACITY`
  (`capacity_hours`, `remaining_hours`).
- Open work without a deadline is attributed to the current bucket, so the
  cockpit is never empty on a project whose tasks omit deadlines.
- `done` means a task in the `completed` lane carrying a deadline inside the
  bucket; task files store no closed timestamp, and the UI says so.
- `project_root` must be absolute (`400` otherwise); `window` must be one of
  the three values (`400`); with auth enabled the route answers `401` without a
  session and `403` outside the session's grants.

## Weekly plan state (`tasks/.plan/week-YYYY-Www.json`)

The week plan is the Manager's commitment, not a derived report. It stores
`deadline_edits` (task id → `YYYY-MM-DD`), `capacity_by_day` (date → hours),
optional notes, and `approved_at` / `approved_by`. Markdown stays the source of
truth for each task; the plan only records scheduling decisions.

- `GET /api/plan` returns the saved plan next to the buckets.
- `POST /api/plan` accepts `{week?, deadline_edits?, capacity_by_day?, approved?,
force?}`; admin session required when auth is on (401 without a session, 403
  for non-admins). Unknown ids, malformed maps, and over-capacity assignments
  are rejected with 400 unless `force` is set.
- `DELETE /api/plan?week=...` clears the week.
- `sprint_daily_agenda` reads the plan first: today's committed tasks, then
  deviations (claimed but uncommitted, saved but unapproved); with no plan it
  says it is using the derived lanes.

### Project registry

Every planner tool call with an explicit `project_root` records that path in
`~/.config/opencode/planner-projects.json` (`PLANNER_PROJECTS_REGISTRY`
overrides), newest first, capped at 50, written atomically. `_discover_projects`
merges the registry with `PLANNER_PROJECTS` and the current root, then keeps only
paths that exist and hold `tasks/`, applying session grants as before. So a
project appears in the dashboard switcher after its first planner call, without
editing the environment.

### Ownership and pressure signals

A task file may carry `**Owner:** <username>`; briefs expose it and the
dashboard renders it as a badge, with a **Mine only** toggle that filters lanes
to the signed-in username (client-side, no round-trip). `sprint_daily_agenda`
now emits `NUDGE` when nothing is claimed while the backlog is non-empty, and
`OVERDUE` with the oldest ids; `claim_next` appends the same `OVERDUE` warning
to a successful claim without ever blocking it. Hand-moving a task file around
`claim_next` bypasses all of these gates and is a workflow violation.

### Scheduling metadata (`schedule_tasks`)

The Planner reads `**Estimate:**`, `**Deadline:**` and `**Depends on:**` from
the task header, and Markdown stays the only source of truth. `schedule_tasks`
is the single writer for those three lines:

```
schedule_tasks(project_root, "336:3h:2026-10-25, 339:3h:2026-10-27:338")
```

Each entry is `id:estimate:deadline[:deps]`; `-` leaves a value untouched.
The tool resolves the id in the active lanes only, replaces an existing value
or inserts the line directly after `**Status:**` (final order Estimate,
Deadline, Depends on), leaves the rest of the file byte-identical, and writes
atomically. It is idempotent, and the call is **all-or-nothing**: one malformed
entry rejects the whole batch so a partially applied schedule cannot exist.
Rejections are explicit — unknown or archived id, duplicate id in one call,
estimate that is not `Nh`/`N.Nh`, deadline that is not `YYYY-MM-DD`, dependencies
that are not ids. The lint rule `_check_planner_metadata` enforces the same
formats, so an agent cannot invent one and have the task silently drop out of
capacity and the timeline.

### Measured time (`Started`, `Submitted`, `Finished`)

Estimates are a plan; these three stamps are the measurement. They are written
by the lane transitions themselves, never by hand:

| Stamp            | Written by              | When                                               |
| ---------------- | ----------------------- | -------------------------------------------------- |
| `**Started:**`   | `claim_next`            | the file enters `tasks/in-progress/`               |
| `**Submitted:**` | `qa_transition`         | the file enters `tasks/qa/`                        |
| `**Finished:**`  | `commit_and_clean_task` | closure, after the file sits in `tasks/completed/` |

Each is ISO-8601 UTC with a `Z` suffix and is **write-once**: a re-claim or a
re-stage never rewrites the original start, because the first one is the work
being measured. `_task_brief` turns them into `elapsed_seconds` (finished −
started) and `qa_wait_seconds` (submitted − started), both `null` rather than
`0` when a stamp is missing, so the panel can tell "not measured" from
"instant". `sprint_stats` keeps the estimate arithmetic and adds a separate
`Completed measured` line. `_check_planner_metadata` rejects a stamp that is not
UTC or a `Finished` earlier than its `Started`.
