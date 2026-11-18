# blowsh with a Docker-side Cloudflare WARP proxy

This guide gives the blowsh MCP server a clean outbound IP by running a Cloudflare WARP proxy container on the same Docker network. It was verified on 2026-11-18 with `ghcr.io/mon-ius/docker-warp-socks:v8` and `blowsh-mcp:latest`.

## Why this pattern

On this VPS the host firewall drops every container-to-host TCP connection. A bridge container cannot reach a proxy listening on the host, whether that proxy is on `7890`, `8118`, `3005` or `8081`. Container-to-container traffic on a Docker bridge does not traverse the host INPUT chain, so a proxy container on the same network is reachable. This was verified with a live `BRIDGE_OK` response between two containers.

The WARP exit IP is shared Cloudflare infrastructure, not a dedicated residential IP. It is cleaner than the VPS IP but some sites still block it. Keep the no-proxy setup as the rollback path.

## Prerequisites

- Docker with permission to create networks and containers.
- `blowsh-mcp:latest` built from `/home/mohammad/blowsh-mcp` at the current HEAD.
- The `browsh-profile` named volume. It preserves Firefox profile state across container recreation.

## Deploy the WARP proxy

Create a dedicated network so container names resolve through Docker DNS:

```bash
docker network create warp-net
```

Run the proxy. This image needs no privileged mode and no `NET_ADMIN`:

```bash
docker run -d --name warp-socks --restart unless-stopped --network warp-net \
  -e NET_PORT=9091 \
  ghcr.io/mon-ius/docker-warp-socks:v8
```

The container registers with Cloudflare automatically and serves both HTTP and SOCKS5 on port `9091`. It keeps private-network traffic local, which protects the Browsh localhost control channel.

## Verify the WARP exit

Run this from another container on `warp-net`, not from the host:

```bash
docker run --rm --network warp-net --entrypoint sh ghcr.io/mon-ius/docker-warp-socks:v8 \
  -c 'curl -x http://warp-socks:9091 -fsSL https://cloudflare.com/cdn-cgi/trace'
```

The result must contain `warp=on` and an `ip=` line. In the verified run the IP was `104.28.211.187` with `loc=FR`. Record the IP you get; it will differ on another day.

## Connect blowsh

Recreate the singleton on the same network. Environment variables are fixed at container creation, so `docker container update` cannot add them. Preserve the name, port binding, volume, restart policy, transport, and the existing `BROWSH_*` timeouts:

```bash
docker stop blowsh-singleton && docker rm blowsh-singleton

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
  blowsh-mcp:latest
```

Use `PROXY_TYPE=http`, not `socks5`. blowsh's Firefox is fully SOCKS5-capable, but the Node-side axios calls have no SOCKS agent in this image. The HTTP mode covers both paths. Never remove `localhost,127.0.0.1` from `PROXY_BYPASS`: the Browsh control channel listens on `127.0.0.1:4333`.

## Verify blowsh

Health and readiness:

```bash
curl -sS http://127.0.0.1:8107/health
docker exec blowsh-singleton cat /data/browsh-profile/.config/browsh/firefox_profile/user.js
```

The generated `user.js` must show `network.proxy.type 1`, host `warp-socks`, port `9091`, and `no_proxies_on` containing `localhost, 127.0.0.1`. The file is written on first render in HTTP mode, so trigger one fetch before judging it:

```bash
curl -sS http://127.0.0.1:8107/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"fetch_web","arguments":{"url":"https://example.com","type":"markdown"}}}'
```

Confirm the clean exit through blowsh itself:

```bash
docker exec blowsh-singleton curl -sS -x http://warp-socks:9091 \
  https://cloudflare.com/cdn-cgi/trace | grep -E '^(ip|warp)='
```

A successful browser render of `https://example.com` plus `warp=on` in the trace is the full acceptance test.

## Rollback

```bash
docker stop blowsh-singleton && docker rm blowsh-singleton
docker run -d --name blowsh-singleton --restart unless-stopped \
  -p 127.0.0.1:8107:8107 \
  -v browsh-profile:/data/browsh-profile \
  -e MCP_TRANSPORT=http -e MCP_HOST=0.0.0.0 -e MCP_PORT=8107 \
  -e BROWSH_PROFILE_DIR=/data/browsh-profile \
  -e PROXY_TYPE=none blowsh-mcp:latest
docker rm -f warp-socks
```

The server rewrites `user.js` to `network.proxy.type 0` on the next boot. Removing the WARP container leaves the network in place for a future retry.

## Troubleshooting

- **`warp=off`** — registration failed. Check `docker logs warp-socks`. Recreate the container to register again.
- **Blowsh renders time out** — check that both containers are on `warp-net` and that `docker exec blowsh-singleton getent hosts warp-socks` resolves.
- **Local pages break** — `PROXY_BYPASS` lost its loopback entries. Restore `localhost,127.0.0.1`.
- **Host proxy tried instead** — not supported here; the host firewall blocks container-to-host traffic. Keep the proxy inside Docker.

## References

- `ghcr.io/mon-ius/docker-warp-socks:v8` — <https://github.com/Mon-ius/Docker-Warp-Socks>
- Host firewall finding and container-to-container verification are recorded in the active task file and its verification evidence.
