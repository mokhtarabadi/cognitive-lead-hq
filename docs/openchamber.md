# OpenChamber (web workspace for OpenCode)

> OpenChamber is the visual workspace that runs **on top of OpenCode**. Install
> OpenCode first, then OpenChamber. OpenChamber starts and manages its own
> OpenCode server — you do **not** run a separate `opencode serve` unit.
>
> Docs: https://docs.openchamber.dev — OpenCode V2 docs: https://opencode.ai/v2/docs/

## 1. Versions

| Component | Version | Update command | Source of truth |
| --- | --- | --- | --- |
| OpenCode | 2.0.21 | `curl -fsSL https://opencode.ai/v2/install \| bash` (V2) | `opencode --version`; latest via `https://opencode.ai/update/api/latest/cli/npm` |
| OpenChamber | 2.1.0 | `openchamber update` | `openchamber --version`; latest via `npm view @openchamber/web version` |

OpenChamber and OpenCode update **separately**. OpenChamber offers OpenCode
updates in its UI and restarts the server afterward; you can also run the V2
installer directly and let OpenChamber reconnect.

## 2. Install

```bash
# 1. OpenCode first
curl -fsSL https://opencode.ai/v2/install | bash
opencode --version            # expect 2.x

# 2. OpenChamber (Node >= 22)
npm install -g @openchamber/web
openchamber --version         # expect 2.x
```

## 3. Run

OpenChamber starts and manages its own OpenCode server (managed mode). This is
the supported default — no external server, no `OPENCODE_SKIP_START`, no extra
systemd unit.

```bash
openchamber --ui-password "$(cat ~/.secrets/openchamber-ui-password)"
# prints the URL (default http://127.0.0.1:3000)
```

Set the UI password from a `chmod 600` file so it never appears in `ps`:

```bash
mkdir -p ~/.secrets
printf '%s' 'be-creative-here' > ~/.secrets/openchamber-ui-password
chmod 600 ~/.secrets/openchamber-ui-password
```

### Server discovery order (from the docs)

1. reuse a server it already started
2. connect to an external one if configured (`OPENCODE_HOST` + `OPENCODE_SKIP_START=true`)
3. auto-detect a server on the default port `4096`
4. otherwise start and manage its own

In managed mode you rely on step 4; nothing else is required.

## 4. Start at boot (the supported way)

Use OpenChamber's own startup integration — it writes the systemd user unit,
snapshots the environment (PATH, tokens), and remembers `--port`, `--host`,
`--ui-password`, and `--api-only`. Do **not** hand-author a custom unit.

```bash
export OPENCHAMBER_UI_PASSWORD="$(cat ~/.secrets/openchamber-ui-password)"
openchamber startup enable --port 3005 --host 127.0.0.1
openchamber startup status                 # startup enabled + service active
sudo loginctl enable-linger mohammad       # start at boot without login
```

Notes:

- `openchamber startup enable` snapshots the current environment into the
  service (provider tokens, `PATH`, SSH agent). Use `--no-env-snapshot` for a
  minimal environment.
- Re-run `startup enable` after changing env vars or the UI password — it
  rewrites `~/.config/openchamber/startup.env`.
- Manage it with `openchamber startup {status,enable,disable}`; inspect with
  `systemctl --user status openchamber`.
- Uninstall: `openchamber startup disable` (stops + removes the service).

## 5. Daily commands

```bash
openchamber status                      # running runtimes
openchamber restart                     # restart server
openchamber stop                        # stop server
openchamber update                      # update OpenChamber
openchamber logs                        # tail logs (wrap in `timeout` if following)
openchamber startup status              # boot integration state
openchamber connect-url --qr            # pairing link for another device
```

## 6. Remote access (optional)

OpenChamber can be reached from other devices through a tunnel. Choose one:

```bash
openchamber tunnel start --port 3005    # ngrok-backed
openchamber tunnel stop  --port 3005
```

Or put it behind a reverse proxy / Cloudflare Tunnel yourself. When binding
beyond localhost, keep a strong UI password and prefer `--api-only` for
headless clients:

```bash
openchamber startup enable --port 3005 --api-only --host 0.0.0.0
```

Locally reach it at `http://127.0.0.1:3005`; generate pairing links with
`openchamber connect-url --port 3005 --server <public-url> --qr`. Links are
single-use and expire.

## 7. Environment variables (the ones that matter here)

| Var | Purpose |
| --- | --- |
| `OPENCHAMBER_HOST` | Bind address for the web server (`0.0.0.0` for other machines). |
| `OPENCHAMBER_UI_PASSWORD` | Browser UI password. |
| `OPENCHAMBER_API_ONLY` | Headless mode (`true`/`1`) — API routes only. |
| `OPENCHAMBER_DATA_DIR` | Data dir (default `~/.config/openchamber`). |
| `OPENCODE_BINARY` | Path to the `opencode` binary OpenChamber runs. |
| `OPENCODE_HOST` / `OPENCODE_PORT` / `OPENCODE_SKIP_START` | External-server mode only. Not used here. |

Full list: https://docs.openchamber.dev/environment/

## 8. Troubleshooting

| Symptom | Check |
| --- | --- |
| UI does not load | `openchamber status`; open the URL it prints; confirm the port is listening (`ss -tlnp \| grep <port>`). |
| "OpenChamber requires OpenCode 2.0.20 or newer" | Update OpenCode: `curl -fsSL https://opencode.ai/v2/install \| bash`, then restart OpenChamber. |
| "OpenCode is restarting" never clears | OpenChamber pauses requests while the managed server starts; if stuck, `openchamber restart` and check `openchamber logs`. |
| Not starting at boot | `openchamber startup status`; re-run `openchamber startup enable`; verify `loginctl show-user <user> \| grep Linger` → `yes`. |
| Sessions visible but tools missing | Reconnect/restart; MCP servers must be reachable on their loopback ports (`docs/services.md`). |

## 9. Relationship to the MCP servers

OpenChamber serves the OpenCode server; OpenCode loads MCP servers from
`~/.config/opencode/opencode.json` (`mcp.servers`). Installing those servers is
covered in `LLM.txt` §5–§7 and `docs/services.md`. OpenChamber itself needs no
MCP configuration.
