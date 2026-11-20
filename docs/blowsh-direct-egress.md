# blowsh direct egress (default mode)

Direct egress is the default mode. It needs no proxy container and no `PROXY_*` variables beyond `PROXY_TYPE=none`. WARP and Psiphon remain available as opt-in alternatives; see `docs/blowsh-proxy-options.md`.

## Deploy

```bash
docker run -d --name blowsh-singleton --restart unless-stopped \
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
  -e PROXY_TYPE=none \
  ghcr.io/mokhtarabadi/blowsh-mcp:latest
```

## Why an older image failed with any proxy

The old blowsh source had a hardcoded 800 ms axios timeout on the Browsh control-channel health probe. Browsh's `/` endpoint re-renders its welcome page and takes about 0.9–2 s here, so every probe timed out while the endpoint answered HTTP 200. The failure reproduced with the proxy fully off, proving the proxy was not the cause. The fix adds `BROWSH_HEALTH_PROBE_TIMEOUT_MS` (default 5000 ms, clamped 1000–60000) and stops a pure probe timeout from quarantining a healthy profile. Use an image that contains this fix for any proxy mode.

## Verify

A real `fetch_web` on `https://example.com` must return page text with `isError:false`. A Cloudflare trace through `fetch_web` shows the VPS IP with `warp=off`.

## Rollback

Recreate blowsh with either proxy mode's variables. See `docs/blowsh-proxy-options.md`.
