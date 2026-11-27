# Slice: zen-bridge

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

## Failure contract

Every failure answers with a parseable JSON error, never with a dropped
socket. This matters because the Brain Bridge reads the body to decide
whether to retry or to give up.

| Case                                       | Status              | Error type                |
| ------------------------------------------ | ------------------- | ------------------------- |
| upstream did not answer inside the timeout | 504                 | `GatewayTimeout`          |
| upstream unreachable (egress, TLS, DNS)    | 502                 | `BadGatewayError`         |
| request body over the cap                  | 413                 | `PayloadTooLarge`         |
| malformed or short request body            | 400                 | `BadRequest`              |
| model owned by another mount               | 404                 | `ModelNotServedHere`      |
| path matches no configured mount           | 404                 | `UnknownRoute`            |
| stream ended without its terminal event    | 200 + in-band event | `UpstreamStreamTruncated` |

The last row is the one that cannot use a status: the status line is
already on the wire, so the failure is reported inside the stream itself.

## Observability

One structured line per request goes to stdout (the systemd journal):

```
ts=2026-11-13T12:41:55Z req_id=c8134dcb method=POST path=/go/resp/responses \
  status=404 outcome=model_not_served model=big-pickle duration_ms=0 \
  session=-(client) bytes=0
```

`session=…(injected)` means the proxy minted the session, `(client)` means
the caller supplied it. The `Authorization` value, the request body and
the response body are never written to the log.

## Routes (loopback `127.0.0.1:8081`)

| Mount       | Upstream                | Serves                            |
| ----------- | ----------------------- | --------------------------------- |
| `/zen/chat` | `opencode.ai/zen/v1`    | free chat models                  |
| `/zen/resp` | `opencode.ai/zen/v1`    | free Responses models             |
| `/go/chat`  | `opencode.ai/zen/go/v1` | Go subscription, chat completions |
| `/go/resp`  | `opencode.ai/zen/go/v1` | Go subscription, Responses API    |

`GET /health` answers `{"status":"ok","mounts":{...},"dormant":[...],"degraded":bool}` and is the liveness probe.

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
- Tests: `tests/test_zen_bridge.py` is not present yet; bridge behaviour is
  covered indirectly by the Brain suites. Creating the slice-local suite is
  open follow-up work.

## Configuration

| Variable                      | Default               | Meaning                                                             |
| ----------------------------- | --------------------- | ------------------------------------------------------------------- |
| `ZEN_BRIDGE_UPSTREAM_TIMEOUT` | `900`                 | upstream socket timeout, seconds; also the silence wall of a stream |
| `UPSTREAM_TIMEOUT_SEC`        | `900`                 | legacy alias, ignored when `ZEN_BRIDGE_UPSTREAM_TIMEOUT` is set     |
| `ZEN_BRIDGE_MAX_BODY_BYTES`   | `33554432`            | hard cap on an inbound request body                                 |
| `ZEN_BRIDGE_HTTPS_PROXY`      | unset                 | upstream proxy for gateway traffic (first in precedence)            |
| `ZEN_BRIDGE_HTTP_PROXY`       | unset                 | proxy for plain-HTTP routes                                         |
| `ZEN_BRIDGE_NO_PROXY`         | loopback              | hosts that must never be proxied; loopback is always appended       |
| `PORT`                        | `8081`                | loopback listen port                                                |
| `OPENCODE_BASE`               | `https://opencode.ai` | gateway root                                                        |

## Two-hop routing

The Brain calls this bridge over loopback (`BRAIN_API_BASE=http://127.0.0.1:8081/v1`)
with no proxy in between; the bridge then reaches the OpenCode gateway through
the `ZEN_BRIDGE_*` proxy values. Proxy precedence is `ZEN_BRIDGE_HTTPS_PROXY`,
`ZEN_BRIDGE_HTTP_PROXY`, then the standard lowercase names, then the uppercase
names. `127.0.0.1`, `localhost`, and `::1` are always excluded from proxying, so
the loopback leg can never be tunnelled.

A malformed value stops the process with a readable message and exit code
2 instead of starting with a substituted default.

## Key Risks & Invariants

- **Loopback only.** Never bind a public interface; the gateway credentials
  pass through this hop.
- **Allowlists gate both `GET /models` and `POST`.** A model posted to the
  wrong mount gets `404 ModelNotServedHere` naming the correct route instead
  of an opaque upstream 400.
- **Timeout ordering.** `ZEN_BRIDGE_UPSTREAM_TIMEOUT` (900s) must sit at or
  below the caller's read timeout (`BRAIN_HTTP_READ_TIMEOUT`, 960s) and the MCP
  client execution timeout (1500000ms). The Brain does not retry, so no outer
  deadline sits above them. A hidden 300s here is what silently killed long
  reasoning turns before 2026-10-22.
- **Never truncate a replayed item id** in a caller; that rule lives in the
  bridge, but it exists because of this gateway's strict input validation.
- **A stream must prove its own completion.** A relay that ends without the
  terminal event reports `UpstreamStreamTruncated` instead of passing a cut
  turn off as a short answer.
- **Never log a credential.** The journal line carries the request id, the
  model and the timing; the `Authorization` value stays in the header.
- The bridge ships no audit mode and no drain knob; only the documented
  `ZEN_BRIDGE_*` settings exist. Never add a second, undocumented switch.
