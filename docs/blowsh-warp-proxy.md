# blowsh with Cloudflare WARP proxy (optional)

WARP is one of two optional egress backends. See `docs/blowsh-proxy-options.md` for the comparison; direct and Psiphon are the alternatives.

## Deploy

```bash
docker network create warp-net 2>/dev/null || true
docker build -t warp-proxy:local warp-proxy/
docker run -d --name warp-socks --restart unless-stopped --network warp-net warp-proxy:local
```

Build context: `warp-proxy/Dockerfile` wraps the pinned upstream image and bakes `NET_PORT=9091`. The container serves HTTP and SOCKS5 on `9091`, publishes no host ports, and must share a bridge with blowsh because this host's firewall blocks container-to-host proxy traffic.

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
  -e PROXY_TYPE=http -e PROXY_HOST=warp-socks -e PROXY_PORT=9091 \
  -e PROXY_BYPASS=localhost,127.0.0.1 \
  ghcr.io/mokhtarabadi/blowsh-mcp:latest
```

HTTP mode is required because blowsh's Node-side axios has no SOCKS agent. The loopback bypass protects the Browsh control channel.

## Verify

Trace through the proxy from another container on `warp-net`; a working exit shows `warp=on`. Then call `fetch_web` and confirm a real render with `isError:false`. A blowsh image older than the `BROWSH_HEALTH_PROBE_TIMEOUT_MS` fix will fail to start behind any proxy.

## Rollback

Recreate blowsh with a different mode's variables. See `docs/blowsh-proxy-options.md`.
