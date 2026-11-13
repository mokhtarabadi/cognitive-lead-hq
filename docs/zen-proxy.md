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

## Verified allowlists (2026-11-08)

- `/go/resp` — 29: `muse-spark-1.2-contributor`, `muse-spark-1.3-contributor`, `gpt-5.6-luna`,
  `gpt-6-luna`, `grok-4.7`, `glm-5.2`, `glm-5.3`, `glm-5.3-flash`,
  `kimi-k2.7-code`, `kimi-k3`, `kimi-k3.1-pro`, `qwen3.7-plus`,
  `qwen3.8-flash`, `qwen3.8-max`, `mimo-v2.6-flash`, `mimo-v2.6-pro`,
  `beam-free`, `deepseek-v4-pro`, `deepseek-v4.1-flash`, `gemini-4-argon`,
  `minimax-m3`, `minimax-m3.1-flash`, `step-5-preview`, `longcat-2.0`,
  `hy3`, `hy4`, `hy4-preview`, `iceman-contributor-free`,
  `crouton-alpha-free`. (`muse-spark-1.2/1.3-contributor` counts as 2 ids; total 29.)
  Every Go model listed above also answered on `/go/resp/responses`
  (verified against live upstream 2026-11-08); the three-tuple test
  `crouton-alpha-free` on `/go/resp` and `/go/chat` both returned 200 while
  the same id on `/zen/v1` returned 429 `FreeUsageLimitError` (free quota
  exhausted for this account). **Do not move `crouton-alpha-free` back to
  only the Zen mount** — it is a Go model id; placing it only on Zen makes it
  unreachable and the wrong-mount hint points the wrong way.
- `/go/chat` — the Go chat set (24 ids). The served count tracks upstream;
  re-probe before trusting a number.
- `/zen/chat`, `/zen/resp` — free models only. Free-tier generation is
  blocked server-side for non-OpenCode callers (see the A3 gate finding in
  the `code-server` history); the mount exists for list parity. The same
  `crouton-alpha-free` id exists on Zen too, but there it is the *free*
  instance and shares the exhausted free quota — prefer `/go/resp`.

## Configuration

Read from the single global `~/.config/opencode/.env` via the unit's
`EnvironmentFile`.

| Variable | Default | Meaning |
| --- | --- | --- |
| `ZEN_PROXY_UPSTREAM_TIMEOUT` | `900` | Upstream socket timeout, seconds; also the silence wall of a stream. Upper bound: it must stay at or below the caller's overall deadline (`BRAIN_OVERALL_DEADLINE_S`, also `900`) and below the MCP client execution timeout (`1200000` ms). Raising it above `900` without raising the caller's deadline only moves the failure from a `504` here to a caller-side timeout. |
| `ZEN_PROXY_MAX_BODY_BYTES` | `33554432` | Hard cap on an inbound request body |
| `ZEN_PROXY_DRAIN_TIMEOUT_S` | `30` | How long a `SIGTERM` waits for in-flight requests |
| `ZEN_PROXY_AUDIT` | `0` | `1` writes prompts + responses to `~/.local/share/zen-proxy/audit-logs/` |

No API key of its own: the caller's `Authorization` header passes through.
The session id is minted per request when the caller sends none; there is no
`ZEN_SESSION_ID` knob (it was read but never used — see ADR-005). A malformed
value stops the unit with a readable message and exit code 2 instead of
starting with a substituted default.

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
# the slice's own suite (offline, fake upstream, no quota spent)
uv run --with pytest pytest tests/test_zen_proxy.py -q
# one structured journal line per request
journalctl --user -u zen-proxy -n 5 --no-pager
```

## Failure modes

| Symptom | Cause | Fix |
| --- | --- | --- |
| `502 BadGatewayError` | egress proxy node failed TLS | retry; check the mihomo pool if enabled |
| `504 GatewayTimeout` | upstream did not answer inside `ZEN_PROXY_UPSTREAM_TIMEOUT` | raise the timeout within the ordering bound, or lower the caller's reasoning effort |
| `413 PayloadTooLarge` | request body over `ZEN_PROXY_MAX_BODY_BYTES` | raise the cap or send a smaller body |
| `400 BadRequest` | malformed or short request body | fix the client framing |
| `404 ModelNotServedHere` | model posted to the wrong mount | use the mount named in the message |
| `UpstreamStreamTruncated` in the stream | upstream ended without its terminal event | retry the turn; the relay refused to pass a cut turn off as a complete one |
| `Server disconnected without sending a response` | pre-2026-11-13 behaviour; the timeout escaped the handler | fixed in ADR-005 — a timeout now answers 504 |
| `/models` count dropped | upstream list drift | run `zen-proxy/refresh_allowlists.py` and apply the reported removals |
