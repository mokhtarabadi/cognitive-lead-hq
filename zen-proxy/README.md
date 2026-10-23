# Slice: zen-proxy

## Duties

Loopback sidecar between OpenAI-compatible clients and the OpenCode Zen/Go
gateways. It exists because those gateways are stricter than a generic
client:

1. They require an `x-opencode-session` header; the proxy mints one when the
   caller does not supply it.
2. Cloudflare in front of `opencode.ai` blocks bare SDK user-agents; the
   proxy sends a browser UA unless a real `opencode/...` client is talking.
3. Clients merge model lists across connections by id, so each mount path
   filters `/models` to the ids that actually work on that API style.
4. Chat-style `reasoning_effort` is rewritten into the Responses-API shape
   `reasoning: {effort}` so `high`/`xhigh`/`max` reach the model.

## Routes (loopback `127.0.0.1:8081`)

| Mount | Upstream | Serves |
| --- | --- | --- |
| `/zen/chat` | `opencode.ai/zen/v1` | free chat models |
| `/zen/resp` | `opencode.ai/zen/v1` | free Responses models |
| `/go/chat` | `opencode.ai/zen/go/v1` | Go subscription, chat completions |
| `/go/resp` | `opencode.ai/zen/go/v1` | Go subscription, Responses API |

`GET /health` answers `{"status":"ok"}` and is the liveness probe.

## Consumers

- **Brain Bridge (primary).** `BRAIN_API_BASE=http://127.0.0.1:8081/go/resp`
  — every `brain_turn` goes through this slice.
- Historical: Open-WebUI, retired and archived 2026-09-19. The proxy stayed
  because the Brain still needs the header minting, the route filters, and
  the effort rewrite.

## Files

- `proxy.py` — the whole server (`BaseHTTPRequestHandler` + `ThreadingHTTPServer`, stdlib only).
- `pyproject.toml` — no runtime dependencies; exists so the venv is built by `uv`.
- `README.md` / `DECISIONS.md` — this slice's docs and ADRs.

## Key Risks & Invariants

- **Loopback only.** Never bind a public interface; the gateway credentials
  pass through this hop.
- **Allowlists gate both `GET /models` and `POST`.** A model posted to the
  wrong mount gets `404 ModelNotServedHere` naming the correct route instead
  of an opaque upstream 400.
- **Timeout ordering.** `ZEN_PROXY_UPSTREAM_TIMEOUT` (default 900s) must sit
  at or below the caller's own deadline (`BRAIN_OVERALL_DEADLINE_S`, also
  900) and below the MCP client's execution timeout. A hidden 300s here is
  what silently killed long reasoning turns before 2026-10-22.
- **Never truncate a replayed item id** in a caller; that rule lives in the
  bridge, but it exists because of this gateway's strict input validation.
- Audit mode (`ZEN_PROXY_AUDIT=1`) writes prompts to local disk. Leave it off
  outside active debugging.
