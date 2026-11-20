# blowsh egress options

blowsh supports three egress modes. None is mandatory. Choose one when you recreate `blowsh-singleton`; the proxy is selected purely by environment variables, so switching modes needs no source change.

| Mode | Default | Container | Blowsh variables | Exit |
| --- | --- | --- | --- | --- |
| Direct | yes | none | `PROXY_TYPE=none` | VPS IP |
| WARP | opt-in | `warp-socks` on `warp-net` | `PROXY_TYPE=http`, `PROXY_HOST=warp-socks`, `PROXY_PORT=9091` | Cloudflare WARP |
| Psiphon | opt-in | `psiphon-socks` on `warp-net` | `PROXY_TYPE=http`, `PROXY_HOST=psiphon-socks`, `PROXY_PORT=8082` | Psiphon, `EgressRegion=US` |

The source fix that added `BROWSH_HEALTH_PROBE_TIMEOUT_MS` is present in the current blowsh image. After that fix, Psiphon mode was verified live with a US browser-side trace and a successful `fetch_web` render, and direct mode was verified earlier with a successful render. The WARP build context is current and the WARP image builds, but WARP has not been re-traced live since the fix; record a fresh `warp=on` trace when enabling it. Do not use a blowsh image older than the fix with a proxy: the old 800 ms health probe made every startup fail regardless of the proxy.

## Shared requirements

- Proxy containers live inside Docker on the same bridge as blowsh. This host's firewall drops container-to-host proxy traffic, so a container cannot use a proxy running on the host.
- Publish no host ports for either proxy. Both are reachable only from their bridge.
- Keep `PROXY_BYPASS=localhost,127.0.0.1` in every mode so the Browsh control channel on `127.0.0.1:4333` stays local.
- Use `PROXY_TYPE=http`, not SOCKS, because blowsh's Node-side axios has no SOCKS agent. Firefox receives the matching `network.proxy.*` preferences in the profile's `user.js`.
- Verify the exit with a Cloudflare trace through the chosen proxy before trusting it. Both proxy IP pools are shared and can be blocked by some sites.

## Deploy one mode

Create the bridge once:

```bash
docker network create warp-net 2>/dev/null || true
```

Build and start the chosen proxy:

```bash
# WARP
docker build -t warp-proxy:local warp-proxy/
docker run -d --name warp-socks --restart unless-stopped --network warp-net warp-proxy:local

# Psiphon
docker build -t psiphon-proxy:us psiphon-proxy/
docker run -d --name psiphon-socks --restart unless-stopped --network warp-net psiphon-proxy:us
```

Then recreate blowsh with the matching variables. Full commands live in `docs/blowsh-warp-proxy.md`, `docs/blowsh-psiphon-proxy.md`, and `docs/blowsh-direct-egress.md`.

## Switching or rollback

Stop and remove the current blowsh container and recreate it with the other mode's `PROXY_*` variables. The unused proxy container can stay stopped or be removed; it has no shared state with blowsh. There is no data migration and no profile reset.

## Verification (any proxy mode)

```bash
curl -sS http://127.0.0.1:8107/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"fetch_web","arguments":{"url":"https://www.cloudflare.com/cdn-cgi/trace","type":"plain"}}}'
```

The returned text must show the exit expected for the chosen mode: `warp=on` for WARP, `loc=US` and `warp=off` for Psiphon, and the VPS IP for direct.
