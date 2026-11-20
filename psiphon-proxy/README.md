# psiphon-proxy — optional Psiphon egress for blowsh

Docker build context for the Psiphon proxy option. It is one of two optional egress backends. The other is `warp-proxy/`; blowsh also works with no proxy at all.

## Build and run

```bash
docker build -t psiphon-proxy:us psiphon-proxy/
docker network create warp-net 2>/dev/null || true
docker run -d --name psiphon-socks --restart unless-stopped --network warp-net \
  psiphon-proxy:us
```

The container serves HTTP on `8082` and SOCKS5 on `1081`. Publish no host ports. Only containers on the same bridge should reach it.

## Use with blowsh

Recreate `blowsh-singleton` on `warp-net` with:

```
-e PROXY_TYPE=http -e PROXY_HOST=psiphon-socks -e PROXY_PORT=8082 \
-e PROXY_BYPASS=localhost,127.0.0.1
```

The HTTP port is required because blowsh's Node-side axios has no SOCKS agent. Keep the loopback bypass so the Browsh control channel on `127.0.0.1:4333` stays local.

## Verify

```bash
docker run --rm --network warp-net --entrypoint sh psiphon-proxy:us \
  -c 'curl -x http://psiphon-socks:8082 -fsSL https://cloudflare.com/cdn-cgi/trace'
```

Look for `loc=US` and `warp=off`. `EgressRegion` is a preference, not a guarantee; always verify the exit before trusting it.

See `docs/blowsh-proxy-options.md` for the full comparison and rollback.
