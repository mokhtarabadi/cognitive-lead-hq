# Zen Proxy (Enhanced Python Edition)

## What it is

`zen-bridge/proxy.py` is a minimal, professional, dependency-free proxy written
in pure Python (stdlib). It lets paid OpenCode Go models be used from anywhere,
especially the Brain, with no caller-side session or header setup.

- No Python dependencies, no venv, no uv; stdlib only.
- No free models. Paid Go models only (caller supplies `model`).
- Caller sends just `{ model, messages }` — no session id, no project, no headers.
- API key comes from outside: caller `Authorization` header, or `BRAIN_API_KEY`
  in the MCP server environment. No key is stored in project files.
- All endpoints: responses API, chat completions, model list, discovery, and
  HTTP CONNECT (works as a normal local HTTP proxy).

## Install

Python 3.9+ is required. Check: `python3 --version`. No packages to install.

```bash
mkdir -p ~/.config/opencode/zen-bridge
cp zen-bridge/proxy.py ~/.config/opencode/zen-bridge/
chmod +x ~/.config/opencode/zen-bridge/proxy.py
```

## Systemd user service

`~/.config/systemd/user/zen-bridge.service`:

```ini
[Unit]
Description=Zen Proxy (Enhanced Python)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
EnvironmentFile=%h/.config/opencode/.env
ExecStart=/usr/bin/python3 %h/.config/opencode/zen-bridge/proxy.py
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now zen-bridge.service
systemctl --user status zen-bridge.service
journalctl --user -u zen-bridge -f
```

## Configuration (environment)

| Variable                      | Default                      | Purpose                                    |
| ----------------------------- | ---------------------------- | ------------------------------------------ |
| `OPENCODE_BASE`               | `https://opencode.ai`        | upstream base                              |
| `OPENCODE_MODELS_HOST`        | `https://models.opencode.ai` | model discovery                            |
| `OPENCODE_PROJECT_ID`         | `global`                     | `x-opencode-project`                       |
| `OPENCODE_CLIENT`             | `cli`                        | `x-opencode-client`                        |
| `OPENCODE_CHANNEL`            | `latest`                     | `x-opencode-channel`                       |
| `OPENCODE_VERSION`            | `2.3.2`                      | `x-opencode-version`                       |
| `OPENCODE_NAME`               | `cli`                        | User-Agent suffix                          |
| `PORT`                        | `8081`                       | listen port                                |
| `UPSTREAM_TIMEOUT_SEC`        | `900`                        | upstream timeout (legacy alias)            |
| `ZEN_BRIDGE_UPSTREAM_TIMEOUT` | `900`                        | upstream timeout (wins over the alias)     |
| `ZEN_BRIDGE_MAX_BODY_BYTES`   | `33554432`                   | request body cap                           |
| `ZEN_BRIDGE_HTTPS_PROXY`      | unset                        | upstream proxy for gateway traffic         |
| `ZEN_BRIDGE_NO_PROXY`         | loopback                     | hosts never proxied; loopback always added |
| `BRAIN_API_KEY`               | optional                     | fallback key injected into MCP server env  |

The API key is **not** in this repository. The caller sends
`Authorization: Bearer <key>`, or the MCP server supplies `BRAIN_API_KEY` in
its environment. `.env.example` documents this; no live key is checked in.

## Identity

All OpenCode-v2 reverse-engineered headers (`x-opencode-client`,
`x-opencode-project`, `x-opencode-session`, `x-opencode-session-id`,
`x-session-affinity`, `X-Session-Id`, `x-session-id`, `x-opencode-channel`,
`x-opencode-version`, `x-opencode-request*`, `User-Agent`, `b3`,
`traceparent`) are generated **once at process start** and cached for the
process lifetime. Each restart generates fresh values.

## Endpoints

| Caller path                                      | Upstream                      | Purpose           |
| ------------------------------------------------ | ----------------------------- | ----------------- |
| `GET /health`                                    | local                         | status + identity |
| `POST /v1/chat/completions`, `/chat/completions` | `/zen/go/v1/chat/completions` | paid Go chat      |
| `POST /v1/responses`, `/responses`               | `/zen/go/v1/responses`        | responses API     |
| `GET /v1/models`, `/models`                      | `/zen/go/v1/models`           | model list        |
| `GET /api.json`, `/experimental/v2.0/api.json`   | models host                   | discovery         |
| `ANY /zen/*`, `/inference/*`, `/*`               | real upstream                 | passthrough       |
| `CONNECT host:port`                              | allowlisted hosts only        | HTTP proxy tunnel |

## Using from the Brain

In the MCP server environment (not in this project):

```bash
BRAIN_API_BASE=http://127.0.0.1:8081/v1
BRAIN_MODEL=muse-spark-1.3-contributor
BRAIN_MODEL_LOW=muse-spark-1.3-contributor
BRAIN_MODEL_HIGH=muse-spark-1.3-contributor
BRAIN_REASONING_EFFORT=high
BRAIN_API_KEY=<key supplied externally>
```

## Verification log (2026-11-27)

- `GET /health` → 200 (`status ok`, `connect true`)
- `GET /v1/models` → 200
- `POST /v1/chat/completions` (`muse-spark-1.3-contributor`) → 200
- `POST /v1/responses` (`muse-spark-1.3-contributor`) → 200
- HTTP CONNECT tunnel via `curl -x http://127.0.0.1:8081` → 200
- `brain_turn` on `muse-spark-1.3-contributor` → completed
- CONNECT allowlist: only `opencode.ai`, `models.opencode.ai` on ports 443/80
- Request body cap: `ZEN_BRIDGE_MAX_BODY_BYTES` (default 32 MiB), oversized → 413

## Verification log (2026-11-27, final)

- Python-only: no JS/Bun source remains; `ls -l zen-bridge/proxy.py` -> success; no references in docs.
- `.env.example`: no live `100.74.8.111` IP; `BRAIN_API_BASE` commented example present.
- `python3 -m py_compile zen-bridge/proxy.py` -> exit 0.
- `curl -s http://127.0.0.1:8081/health` -> 200 `status ok`.
- `curl -s -o /dev/null -w %{http_code} http://127.0.0.1:8081/v1/models` -> 200.
- `curl -X CONNECT ... Host:example.com` -> 403.
