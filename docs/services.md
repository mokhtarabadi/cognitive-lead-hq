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

## Security (accepted risk)

Loopback HTTP carries no authentication: any local process can call any
singleton (QA finding F1). The control is the bind itself — every server
listens on 127.0.0.1 only (verified via `ss -tlnp`, test T4), so only code
already running on this machine can reach them. Do not rebind to
0.0.0.0 or expose these ports beyond the host. (Inside the blowsh
container `MCP_HOST=0.0.0.0` is required, but the published port stays
`-p 127.0.0.1:8107:8107`.)

## How it works

Each HQ Python server (lint, context, memory, decision, brain) reads
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

## Linux (systemd user units)

Unit files live in `services/`. Install:

```bash
mkdir -p ~/.config/systemd/user
cp services/mcp-*.service ~/.config/systemd/user/
systemctl --user daemon-reload
for s in lint context memory decision brain telegram; do
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
Repeat for ports 8102-8106 with the matching server directory.

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

## Verification

```bash
opencode mcp list            # 7/7 connected
ps aux | grep mcp- | grep -v grep   # exactly one process per server
```

Open a second session and repeat: process count must not grow.

## Rollback

Restore the global config backup (`~/.config/opencode/opencode.json.bak-*`),
stop the units (`systemctl --user stop mcp-*`), and restart the client.
Sessions return to per-session stdio servers.
