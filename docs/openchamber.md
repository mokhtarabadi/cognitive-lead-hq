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

## 10. Server Browser — agent-driven web browsing (2026-10-28 runbook)

The `openchamber_web` `browser.*` tools (open, snapshot, click, type, capture…)
let an agent see and drive web pages — but only when a **browser provider**
exists. A page open in a plain web-browser tab **cannot** be driven
(`drivable:false`; snapshot fails with "No OpenChamber client connected").
Two providers exist: the **desktop app**, or the **server-browser extension**
below. Without one, the agent can only describe pages, never open them.

Extension: `openchamber-server-browser`
(`https://github.com/JosueGalRe/openchamber-server-browser`, experimental,
requires OpenChamber ≥ 2.0.1). It runs its own Chrome on the OpenChamber host;
you watch the same page in the **Server Browser** panel.

### 10.1 Install

```bash
# folder install (URL install from extension settings works too)
git clone https://github.com/JosueGalRe/openchamber-server-browser.git ~/Develop/openchamber-server-browser
```

1. OpenChamber → Settings → Extensions → add the folder (or the GitHub URL).
2. Review and **approve its service permission** (the service launches Chrome).
3. Settings → General → OpenChamber Tools → **Browser provider = Server Browser**.
4. Restart the extension after any config change.

### 10.2 Chrome — use headless-shell, NOT apt chromium

The extension needs Chrome/Chromium ≥ 109 on the OpenChamber host and sends
**no `--no-sandbox` flag** itself. Ubuntu trap: `apt install chromium`
installs a 50 KB stub that pulls the **snap** stack (snapd + core + gnome
snaps, 1 GB+ and still downloading). On a server/VPS use
`chrome-headless-shell` from Chrome-for-Testing instead (~127 MB zip,
12 small system libs, no snap):

```bash
VER=$(python3 -c "import urllib.request,json; print(json.load(urllib.request.urlopen('https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json'))['channels']['Stable']['version'])")
python3 -c "import urllib.request; urllib.request.urlretrieve('https://storage.googleapis.com/chrome-for-testing-public/$VER/linux64/chrome-headless-shell-linux64.zip', '/tmp/chs.zip')"
sudo rm -rf /opt/chrome-headless-shell && sudo mkdir -p /opt \
  && sudo unzip -q -o /tmp/chs.zip -d /opt \
  && sudo mv /opt/chrome-headless-shell-linux64 /opt/chrome-headless-shell
ldd /opt/chrome-headless-shell/chrome-headless-shell | grep "not found"   # missing libs, if any
sudo apt-get install -y --no-install-recommends \
  libnspr4 libnss3 libatk1.0-0 libatk-bridge2.0-0 libatspi2.0-0 libgbm1 \
  libasound2t64 libxcomposite1 libxdamage1 libxfixes3 libxrandr2
/opt/chrome-headless-shell/chrome-headless-shell --version   # expect 156.x+
```

Containers/rootless hosts additionally need `--no-sandbox` (without it Chrome
dies with `SIGTRAP` on startup). The extension has no extra-flags option, so
point `chromePath` at a wrapper script:

```sh
#!/bin/sh
exec /opt/chrome-headless-shell/chrome-headless-shell --no-sandbox "$@"
```

```bash
chmod +x ~/chrome-wrapper.sh
```

### 10.3 Extension config (`config.json` next to the install)

```json
{
  "allowedOrigins": ["http://127.0.0.1:3000", "http://localhost:3000"],
  "chromePath": "/home/mohammad/chrome-wrapper.sh",
  "discoverDevServers": false
}
```

- `allowedOrigins`: loopback dev servers are **blocked by default** — list
  every exact origin (scheme + host + port) the browsed pages need.
- `chromePath`: full Chrome **or** the wrapper above.
- `discoverDevServers`: leave `false` unless you accept any page reaching
  every live loopback listener. Restart the extension after editing.

### 10.4 Daily use

- Agent: `browser.open` (returns a real `tabId`, `settled:true`), then
  `browser.snapshot` / `click` / `type` / `capture`, always naming the `tabId`.
- Human: open **Server Browser** from the panel rail → pick the tab → watch
  the same page. Taking panel control pauses agent actions; release it to
  hand the page back.
- First action in a chat starts that chat's browser scope (isolated cookies/
  storage, 5-min idle expiry). Captures land in
  `<project>/.openchamber/screenshots/`.

### 10.5 Troubleshooting (all 2026-10-28, live)

| Symptom | Cause → fix |
| --- | --- |
| `drivable:false`, "No OpenChamber client connected" | No provider → install this extension (or use the desktop app). |
| "Chrome or Chromium was not found" | Set `chromePath` in `config.json`, restart extension. |
| "Chrome exited during startup (SIGTRAP)" | Sandbox blocked → wrapper script with `--no-sandbox` (§10.2). |
| `502` / blocked page on `127.0.0.1:PORT` | Dev server down, or origin missing from `allowedOrigins`. |
| `apt chromium` eating the VPS | It's the snap stub → remove per §10.6, install headless-shell (§10.2). |

### 10.6 Removing the snap stack (if §10.2's trap already bit)

Order matters: kill seed processes → `snap remove` each snap (needs snapd
**running**) → purge debs → delete dirs. Never `rm -rf /snap` first
(squashfs mounts are read-only; unmount happens through `snap remove`/purge):

```bash
sudo snap list                                   # what is registered (may be empty)
for s in $(sudo snap list 2>/dev/null | awk 'NR>1{print $1}'); do sudo snap remove --purge $s; done
sudo dpkg --remove --force-remove-reinstreq chromium-browser   # the stub re-runs `snap install` via configure — remove, don't configure
sudo apt purge -y snapd
sudo rm -rf /snap /var/snap /var/lib/snapd /root/snap ~/snap /var/cache/snapd
sudo apt autoremove -y
```

Two traps we hit live: (1) `pkill -f '<pattern>'` matches your **own**
command line when the rest of the one-liner contains the target words —
split kills into their own call with bracket patterns (`[s]nap …`). (2) A
half-installed stub re-triggers `snap install` on `dpkg --configure -a`,
so configure-then-purge loops forever; remove the stub first.

### 10.7 Verification

- [ ] `browser.open` returns a real `tabId` (not `browser:…:agent:…` display-only).
- [ ] `browser.snapshot` lists the tab; `browser.capture` writes
      `.openchamber/screenshots/*.png`.
- [ ] Server Browser panel shows the same page the agent opened.
