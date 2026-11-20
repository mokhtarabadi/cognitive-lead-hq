# blowsh with Psiphon proxy (optional)

Psiphon is one of two optional egress backends. See `docs/blowsh-proxy-options.md` for the comparison; direct and WARP are the alternatives.

## Deploy

```bash
docker network create warp-net 2>/dev/null || true
docker build -t psiphon-proxy:us psiphon-proxy/
docker run -d --name psiphon-socks --restart unless-stopped --network warp-net psiphon-proxy:us
```

Build context: `psiphon-proxy/Dockerfile` builds `ubuntu:22.04` with `psiphon-tunnel-core` baked in from the official binaries repository. The config is baked with `EgressRegion=US`, HTTP `8082`, and SOCKS5 `1081`. Publish no host ports; the container is reachable only from its bridge.

## Connect blowsh

```bash
docker stop blowsh-singleton 2>/dev/null || true
docker rm blowsh-singleton 2>/dev/null || true
docker run -d --name blowsh-singleton --restart unless-stopped --network warp-net \
  -p 127.0.0.1:8107:8107 \
  -v browsh-profile:/data/browsh-profile \
  -e MCP_TRANSPORT=http -e MCP_HOST=0.0.0.0 -e MCP_PORT=8107 \
  -e BROWSH_STARTUP_TIMEOUT_MS=120000 \
  -e BROWSH_QUEUE_TIMEOUT_MS=600000 \
  -e BROWSH_REQUEST_TIMEOUT_MS=180000 \
  -e SEARCH_DEADLINE_MS=900000 \
  -e BROWSH_CRASH_WINDOW_MS=60000 \
  -e BROWSH_CRASH_THRESHOLD=3 \
  -e BROWSH_CRASH_COOLDOWN_MS=30000 \
  -e BROWSH_PROFILE_DIR=/data/browsh-profile \
  -e BROWSH_COLS=160 -e BROWSH_ROWS=60 \
  -e PROXY_TYPE=http -e PROXY_HOST=psiphon-socks -e PROXY_PORT=8082 \
  -e PROXY_BYPASS=localhost,127.0.0.1 \
  ghcr.io/mokhtarabadi/blowsh-mcp:latest
```

HTTP mode uses port `8082` because blowsh's Node-side axios has no SOCKS agent. The loopback bypass protects the Browsh control channel.

## Verify

```bash
docker run --rm --network warp-net --entrypoint sh psiphon-proxy:us \
  -c 'curl -x http://psiphon-socks:8082 -fsSL https://cloudflare.com/cdn-cgi/trace'
```

Expect `loc=US` and `warp=off`, with an `ip=` line. `EgressRegion` is a preference, not a guarantee, so always check. Then call `fetch_web` on the trace URL and confirm the same IP and country, which proves the browser itself uses the proxy.

Live proof on 2026-11-20 with the fixed blowsh image: `ip=104.131.189.185`, `loc=US`, `warp=off`, and `fetch_web` rendered `example.com` in about 10 s.

## Rollback

Recreate blowsh with a different mode's variables. See `docs/blowsh-proxy-options.md`.
