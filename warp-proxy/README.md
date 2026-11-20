# warp-proxy — optional Cloudflare WARP egress for blowsh

Docker build context for the WARP proxy option. It is one of two optional egress backends. The other is `psiphon-proxy/`; blowsh also works with no proxy at all.

The Dockerfile pins the previously verified upstream image `ghcr.io/mon-ius/docker-warp-socks:v8` and bakes `NET_PORT=9091`, which the upstream image does not default. This is a wrapper, not a from-scratch WARP build.

## Build and run

```bash
docker build -t warp-proxy:local warp-proxy/
docker network create warp-net 2>/dev/null || true
docker run -d --name warp-socks --restart unless-stopped --network warp-net \
  warp-proxy:local
```

The container serves HTTP and SOCKS5 on `9091`. Publish no host ports. Container-to-host proxying is blocked by this host's firewall, so the proxy must share a bridge with blowsh.

## Use with blowsh

Recreate `blowsh-singleton` on `warp-net` with:

```
-e PROXY_TYPE=http -e PROXY_HOST=warp-socks -e PROXY_PORT=9091 \
-e PROXY_BYPASS=localhost,127.0.0.1
```

HTTP mode is required because blowsh's Node-side axios has no SOCKS agent. Keep the loopback bypass so the Browsh control channel stays local.

## Verify

Run a Cloudflare trace through `http://warp-socks:9091` from another container on `warp-net`. A working exit shows `warp=on`. Then confirm a real `fetch_web` render succeeds.

See `docs/blowsh-proxy-options.md` for the full comparison and rollback.
