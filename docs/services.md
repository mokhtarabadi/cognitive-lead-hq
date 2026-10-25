# MCP Singleton Services

One supervised instance of each MCP server, shared across all sessions and projects.

## Port map (127.0.0.1 only)

| Server    | Port | Unit / job                |
| --------- | ---- | ------------------------- |
| lint      | 8101 | mcp-lint                  |
| context   | 8102 | mcp-context               |
| memory    | 8103 | mcp-memory                |
| decisions | 8104 | mcp-decision              |
| brain     | 8105 | mcp-brain                 |
| telegram  | 8106 | mcp-telegram              |
| blowsh    | 8107 | blowsh-singleton (Docker) |
| planner   | 8108 | mcp-planner               |
| zen-proxy | 8081 | zen-proxy (not MCP — the Brain's provider hop) |

`planner` is the capacity-aware, QA-gated planning layer over `tasks/`
Markdown. It serves the MCP Streamable HTTP endpoint at `/mcp` and a
standalone dashboard at `/` (plus `/api/status`) on the same loopback
port. It reads the project given by `PLANNER_PROJECT_ROOT`, falling back
to the nearest ancestor of its working directory that holds `tasks/`.
`PLANNER_PROJECTS` (pathsep-separated absolute paths) feeds the
dashboard's project switcher. It needs no credentials. `schedule_tasks`
is the only writer for the `**Estimate:**`, `**Deadline:**` and
`**Depends on:**` header lines the planner reads, and `lint_task_file`
rejects a malformed value so the two cannot drift.

Planner authentication is **optional and off by default**: with no
`~/.config/opencode/planner-users.json` (or `"auth_enabled": false`) the
server stays in open local mode, byte-identical to the pre-auth
behaviour. With auth on, `POST /api/login` issues an `HttpOnly`
`planner_session` cookie, `/api/status` is 401 until sign-in and 403
outside the caller's `allowed_projects`. `/mcp` is deliberately auth-free on
loopback (the tunnel answers 404 for it), so local MCP clients connect with
no credentials even when auth is on. Users are managed with the stdlib CLI
(no venv needed):

```bash
python3 ~/.config/opencode/mcp-planner-server/manage_users.py \
  add --username admin --role admin --projects "*"
python3 ~/.config/opencode/mcp-planner-server/manage_users.py \
  add --username friend --role viewer --projects /home/me/Develop/Projects/shared
python3 ~/.config/opencode/mcp-planner-server/manage_users.py list
systemctl --user restart mcp-planner     # config is read at startup
```

Passwords are PBKDF2-HMAC-SHA256 (600k iterations, per-user salt); the
file is written `chmod 600`. `PLANNER_USERS_CONFIG` overrides the path,
and `enable` / `disable` flip `auth_enabled` without touching users.

### Exposing the planner through a Cloudflare Tunnel

The tunnel is the only supported way to reach the dashboard from outside
the host. Keep the unit bound to loopback and let `cloudflared` make the
outbound connection — never rebind to `0.0.0.0`.

```bash
cloudflared tunnel login
cloudflared tunnel create planner
cloudflared tunnel route dns planner planner.example.com
```

`~/.cloudflared/config.yml` — the `/mcp` ingress rule is a deliberate
`404` so tool execution never leaves the host, even for an admin cookie:

```yaml
tunnel: planner
credentials-file: /home/me/.cloudflared/<tunnel-uuid>.json

ingress:
  # Tool execution stays loopback-only. This rule must come first.
  - hostname: planner.example.com
    path: ^/mcp(/.*)?$
    service: http_status:404
  # Dashboard + JSON API (login, status, me) through the tunnel.
  - hostname: planner.example.com
    service: http://127.0.0.1:8108
  - service: http_status:404
```

```bash
sudo cloudflared service install        # or: cloudflared tunnel run planner
```

Rules that make the exposure safe:

1. `path: ^/mcp(/.*)?$` → `http_status:404` is ordered **before** the
   catch-all hostname rule; Cloudflare matches ingress top-down, so a
   later rule can never re-open `/mcp`.
2. Enable auth (`manage_users.py add ...`) before starting the tunnel.
   Without it the dashboard is open to anyone who finds the hostname.
3. `allowed_projects` is the second gate: a viewer only ever sees the
   project roots listed for them, and any other `?project_root=` is 403.
4. The tunnel exposes HTTPS only; the `planner_session` cookie is
   `HttpOnly` + `SameSite=Lax`, so keep the hostname HTTPS-only in
   Cloudflare (no plain-HTTP origin rule).
5. Verify from outside: `curl -s -o /dev/null -w '%{http_code}\n'
   https://planner.example.com/mcp` must print `404`, while `/` prints
   `200` and shows the login modal.

`zen-proxy` is listed here because it is provisioned and supervised the same
way, but it speaks the OpenAI Responses/Chat API rather than MCP. Its unit
reads the same global `.env`; it needs no API key of its own (the caller's
`Authorization` header passes through). See `docs/zen-proxy.md`.

## Security (accepted risk)

Loopback HTTP carries no authentication: any local process can call any
singleton (QA finding F1). The control is the bind itself — every server
listens on 127.0.0.1 only (verified via `ss -tlnp`, test T4), so only code
already running on this machine can reach them. Do not rebind to
0.0.0.0 or expose these ports beyond the host. (Inside the blowsh
container `MCP_HOST=0.0.0.0` is required, but the published port stays
`-p 127.0.0.1:8107:8107`.)

The planner is the one exception when it is tunneled: it ships optional
cookie-session auth with per-user project scoping, so an operator can
expose the dashboard through `cloudflared` while `/mcp` stays
loopback-only (see the planner section above). Every other singleton
stays loopback-only with no auth at all.

## Credentials (`.env`) — how the servers read keys

The Python servers (`context`, `memory`, `lint`, `decision`, `brain`) load
`.env` themselves at import via `mcp_common.env.load_env_files`. Search
order, **first file holding a key wins**:

1. `<server-dir>/.env`
2. `<server-dir>/../.env`
3. `<cwd>/.env`

Real process environment always wins over the file; an empty value counts
as **unset** (so a blank `{env:}` injection never shadows a real file
value).

Consequence for the global singleton install (`<server-dir>` =
`~/.config/opencode/mcp-*/`): the effective file is
**`~/.config/opencode/.env`** (`<server-dir>/../.env`). For servers run
straight from the repo, that is the repo-root `.env`. Telegram is
third-party and reads its own `.env` in its install dir.

Therefore the unit files need **no** `EnvironmentFile=` for `BRAIN_*` /
`DECISION_*` / `TELEGRAM_*`; just keep the keys in the right `.env`:

```bash
# global install: seed once, keep chmod 600
install -m 600 /path/to/repo/.env ~/.config/opencode/.env
# or start from the template:
# install -m 600 /path/to/repo/.env.example ~/.config/opencode/.env   # then edit keys
```

After changing any key, restart the affected unit
(`systemctl --user restart mcp-brain mcp-decision mcp-telegram`).

> Note: this is separate from OpenCode's own `{env:VAR}` forwarding for a
> managed/daemon server — that concerns variables you want the OpenCode
> process itself to see. The MCP servers above do not need it.

## How it works

Each HQ Python server (lint, context, memory, decision, brain, planner) reads
`MCP_TRANSPORT` from the environment. Default is `streamable-http`
(singleton default: all callers consume these servers as remote http
singletons, so an unset variable must not silently drop into stdio while
the unit reports active; explicit `MCP_TRANSPORT=stdio` still works for
local debugging). Telegram is third-party and honors `stdio | http | sse`
(`http` in its unit files) plus `MCP_HOST` / `MCP_PORT` (defaults
`127.0.0.1:8106`) plus `TELEGRAM_ALLOW_SERVER_ROOTS_FALLBACK=1` (falls back
to CLI roots when the client never answers `roots/list`, else `upload_file`
is disabled).

OpenCode connects via
`type: "remote"` entries in the global `opencode.json`:

```json
{
  "mcp": {
    "lint": {
      "type": "remote",
      "url": "http://127.0.0.1:8101/mcp",
      "enabled": true,
      "timeout": 15000
    }
  }
}
```

> **project_root isolation (Task 279 F6/V1):** every tool on the HQ
> servers takes an optional `project_root`. When it is omitted the call
> is scoped to the singleton server's own directory and the result now
> carries a client-visible `WARNING [project-isolation]` line (plus the
> existing stderr warning). Pass an absolute `project_root` on every
> call.

> **Brain tool surface:** `mcp-brain` exposes `brain_turn` as its singular
> automation tool — the only path for planning, QA, and review turns.
> File inspection uses the caller's native tools (`read`, `grep`, `glob`);
> the former server-side file helpers were removed.

## Linux (systemd user units)

Unit files live in `services/`. Install:

```bash
mkdir -p ~/.config/systemd/user
cp services/mcp-*.service ~/.config/systemd/user/
systemctl --user daemon-reload
for s in lint context memory decision brain telegram planner; do
  systemctl --user enable --now mcp-$s
done
```

All units use `%h` for the home directory and `Restart=always`, so they
survive reboots and crashes.

## macOS (launchd)

> **Untested on macOS — no Mac host was available in this pass.**

Ready-made templates live in `services/launchd/` (substitute your home
path for `{HOME}`); the inline template below shows the shape
(`~/Library/LaunchAgents/mcp-<name>.plist`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>mcp-lint</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string><string>-lc</string>
    <string>MCP_TRANSPORT=streamable-http exec ~/.config/opencode/mcp-lint-server/.venv/bin/python ~/.config/opencode/mcp-lint-server/server.py</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
</dict>
</plist>
```

Load with `launchctl load ~/Library/LaunchAgents/mcp-<name>.plist`.
Repeat for the remaining ports (8102-8106 and 8108) with the matching
server directory. Credentials
are self-loaded by each server from `~/.config/opencode/.env`
(`<server-dir>/../.env`) — no `EnvironmentVariables` entry is needed for
`BRAIN_*`/`DECISION_*` (see the Credentials section above).

## Windows

A Task Scheduler XML template is vendored at
`services/windows/mcp-singleton-template.xml` (> **untested on Windows —
no Windows host was available in this pass**; import with
`schtasks /create /xml`, replacing `{HOME}`, `{NAME}`, `{PORT}`).
GUI/NSSM alternative (also untested on Windows):

- **Task Scheduler:** one task per server, trigger "At log on", action:
  `<server-dir>\.venv\Scripts\python.exe <server-dir>\server.py`
  with environment variable `MCP_TRANSPORT=streamable-http`.
- **NSSM alternative:** `nssm install mcp-lint <python> <server.py>`,
  then set `MCP_TRANSPORT` under the Environment tab. NSSM gives
  `Restart=always` equivalent behavior.

Credentials (`BRAIN_*`/`DECISION_*`/`TELEGRAM_*`) are self-loaded by each
server from `%USERPROFILE%\.config\opencode\.env`
(`<server-dir>/../.env`); you do not need to set them in the task/service
environment (see the Credentials section above).

## Verification

```bash
opencode mcp list            # every configured server connected
ps aux | grep mcp- | grep -v grep   # exactly one process per server
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8108/   # planner dashboard: 200
```

Open a second session and repeat: process count must not grow.

## Rollback

Restore the global config backup (`~/.config/opencode/opencode.json.bak-*`),
stop the units (`systemctl --user stop mcp-*`), and restart the client.
Sessions return to per-session stdio servers.
