# zen-proxy — loopback gateway sidecar

The sidecar that lets an OpenAI-compatible client talk to the OpenCode
Zen/Go gateways. Source: `zen-proxy/proxy.py` (stdlib only). Unit:
`services/zen-proxy.service`. Installed globally at
`~/.config/opencode/zen-proxy/`.

## Why it exists

The gateways are stricter than a generic OpenAI client:

1. **Session header required.** Requests without `x-opencode-session` are
   rejected. The proxy mints one when the caller supplies none.
2. **User-agent gate.** Cloudflare in front of `opencode.ai` answers HTTP
   1010 to bare SDK agents. The proxy sends a browser UA unless a genuine
   `opencode/...` client is talking, in which case it forwards the client's
   own UA untouched.
3. **Model lists merge by id.** An OpenAI-compatible client that mounts both
   API styles in one connection shows models that cannot work on that style.
   Each mount filters `GET /models` to the ids that actually work there.
4. **Effort shape differs.** Clients send chat-style `reasoning_effort`;
   the `/responses` endpoints accept only `reasoning: {effort}`. The proxy
   rewrites one into the other so `high`/`xhigh`/`max` reach the model.

Historically the consumer was Open-WebUI (retired 2026-09-19). The live
consumer is the Brain Bridge: `BRAIN_API_BASE=http://127.0.0.1:8081/go/resp`.

## Routes

| Mount | Upstream | Serves |
| --- | --- | --- |
| `/zen/chat` | `opencode.ai/zen/v1` | free chat models |
| `/zen/resp` | `opencode.ai/zen/v1` | free Responses models |
| `/go/chat` | `opencode.ai/zen/go/v1` | Go subscription, chat completions |
| `/go/resp` | `opencode.ai/zen/go/v1` | Go subscription, Responses API |

`GET /health` → `{"status":"ok"}`.

Both `GET /models` and `POST` are gated by the mount allowlist. A model
posted to the wrong mount returns `404 ModelNotServedHere` naming the correct
mount, or `no known route` when no mount serves it.

## Verified allowlists (2026-10-22)

- `/go/resp` — 13: `muse-spark-1.2/1.3-contributor`, `gpt-5.6-luna`,
  `gpt-6-luna`, `grok-4.6`, `grok-4.7`, `glm-5.3`, `glm-5.3-flash`,
  `kimi-k3`, `qwen3.8-max`, `mimo-v2.6-pro`, `deepseek-v4-pro`,
  `deepseek-v4.1-flash`.
  Every Go chat model probed on 2026-10-21 also answered on `/responses`;
  the earlier "only six Responses models" reading came from the docs table,
  not from the gateway.
- `/go/chat` — the Go chat set. The served count tracks upstream and drifts
  (36 upstream ids, 23 allowlisted present at the last check); re-probe
  before trusting a number.
- `/zen/chat`, `/zen/resp` — free models only. Free-tier generation is
  blocked server-side for non-OpenCode callers (see the A3 gate finding in
  the `code-server` history); the mount exists for list parity.

## Configuration

Read from the single global `~/.config/opencode/.env` via the unit's
`EnvironmentFile`.

| Variable | Default | Meaning |
| --- | --- | --- |
| `ZEN_SESSION_ID` | zero UUID | Fallback session header when the caller sends none |
| `ZEN_PROXY_UPSTREAM_TIMEOUT` | `900` | Upstream socket timeout, seconds |
| `ZEN_PROXY_AUDIT` | `0` | `1` writes prompts + responses to `~/.local/share/zen-proxy/audit-logs/` |

No API key of its own: the caller's `Authorization` header passes through.

### Timeout ordering (binding)

```
zen-proxy upstream timeout  ≤  caller overall deadline  ≤  MCP client execution
       900s (default)             900s (brain default)        1200s
```

A hidden 300s here is what killed long reasoning turns before 2026-10-22: a
deep `gpt-6-luna` turn spends 14-19K reasoning tokens, i.e. five to ten
minutes, so the proxy dropped the socket with no response, the bridge saw
`RemoteProtocolError`, retried, and reported
`provider overall deadline hit (500.0s)`.

## Install (global)

```bash
# from a clone of this repo
mkdir -p ~/.config/opencode/zen-proxy
cp zen-proxy/{proxy.py,pyproject.toml,README.md,DECISIONS.md} ~/.config/opencode/zen-proxy/
chmod +x ~/.config/opencode/zen-proxy/proxy.py
cd ~/.config/opencode/zen-proxy && uv venv .venv     # no deps to install
cp services/zen-proxy.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now zen-proxy.service
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8081/health   # 200
```

The venv is built by `uv` but the unit launches the venv interpreter
directly, matching every other slice: a running service must not depend on
`uv` being on PATH.

## Verification

```bash
systemctl --user is-active zen-proxy
for r in go/resp go/chat zen/chat zen/resp; do
  curl -s "http://127.0.0.1:8081/$r/models" | jq '.data | length'
done
# wrong-mount post must be 404 with a hint, not an upstream 400
curl -s -X POST http://127.0.0.1:8081/go/resp/responses \
  -H 'Content-Type: application/json' \
  -d '{"model":"hy3","input":[{"role":"user","content":"x"}]}' | jq .error.type
# a real Responses turn through the proxy
curl -s -X POST http://127.0.0.1:8081/go/resp/responses \
  -H "Authorization: Bearer $BRAIN_API_KEY" -H 'Content-Type: application/json' \
  -d '{"model":"glm-5.3","input":[{"role":"user","content":"reply: ok"}],"max_output_tokens":64}' | jq -r .status
```

## Failure modes

| Symptom | Cause | Fix |
| --- | --- | --- |
| `502 BadGatewayError` | egress proxy node failed TLS | retry; check the mihomo pool if enabled |
| `404 ModelNotServedHere` | model posted to the wrong mount | use the mount named in the message |
| `Server disconnected without sending a response` | upstream slower than `ZEN_PROXY_UPSTREAM_TIMEOUT` | raise the timeout, or lower the caller's reasoning effort |
| `/models` count dropped | upstream list drift | re-probe upstream and refresh the allowlist |
