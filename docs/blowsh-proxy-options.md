# blowsh egress options

blowsh supports direct egress and an optional HTTP proxy. Neither is tied to a
named container backend any more: the proxy is selected purely by environment
variables, so any proxy you operate can sit in front of it without a source
change.

| Mode   | Default | Proxy container          | Blowsh variables                                            | Exit     |
| ------ | ------- | ------------------------ | ----------------------------------------------------------- | -------- |
| Direct | yes     | none                     | `PROXY_TYPE=none`                                           | host IP  |
| HTTP   | opt-in  | your own proxy, any name | `PROXY_TYPE=http`, `PROXY_HOST=<host>`, `PROXY_PORT=<port>` | proxy IP |

The source fix that added `BROWSH_HEALTH_PROBE_TIMEOUT_MS` is present in the
current blowsh image. Do not run a blowsh image older than that fix with a
proxy: the old 800 ms health probe made every startup fail regardless of the
proxy.

## Shared requirements

- If your proxy runs in a container, that container must share a Docker network
  with blowsh. This host's firewall drops container-to-host proxy traffic, so a
  container cannot reach a proxy listening on the host.
- Publish no host ports for the proxy; it is reachable only from its network.
- Keep `PROXY_BYPASS=localhost,127.0.0.1` in every mode so the Browsh control
  channel on `127.0.0.1:4333` stays local.
- Use `PROXY_TYPE=http`, not SOCKS, because blowsh's Node-side axios has no
  SOCKS agent. Firefox receives the matching `network.proxy.*` preferences in
  the profile's `user.js`.
- Verify the exit with a Cloudflare trace through the chosen proxy before
  trusting it. Shared proxy IP pools can be blocked by some sites.

## Deploy a mode

Direct (default):

```bash
docker rm -f blowsh-singleton 2>/dev/null || true
docker run -d --name blowsh-singleton --restart unless-stopped \
  -p 127.0.0.1:8107:8107 \
  -v browsh-profile:/data/browsh-profile \
  -e MCP_TRANSPORT=http -e MCP_HOST=0.0.0.0 -e MCP_PORT=8107 \
  -e BROWSH_PROFILE_DIR=/data/browsh-profile \
  -e PROXY_TYPE=none -e PROXY_BYPASS=localhost,127.0.0.1 \
  ghcr.io/mokhtarabadi/blowsh-mcp:latest
```

Through a proxy you operate (replace host and port with yours):

```bash
docker run -d --name blowsh-singleton --restart unless-stopped \
  --network <your-proxy-network> \
  -p 127.0.0.1:8107:8107 \
  -v browsh-profile:/data/browsh-profile \
  -e MCP_TRANSPORT=http -e MCP_HOST=0.0.0.0 -e MCP_PORT=8107 \
  -e BROWSH_PROFILE_DIR=/data/browsh-profile \
  -e PROXY_TYPE=http -e PROXY_HOST=<proxy-host> -e PROXY_PORT=<proxy-port> \
  -e PROXY_BYPASS=localhost,127.0.0.1 \
  ghcr.io/mokhtarabadi/blowsh-mcp:latest
```

Keep the rest of the budgets (`BROWSH_*`, `SEARCH_DEADLINE_MS`) from
`docs/blowsh-direct-egress.md` unchanged; they are independent of egress.

## Switching or rollback

Stop and remove the blowsh container and recreate it with the other mode's
`PROXY_*` variables. There is no data migration and no profile reset.

## Verification (any mode)

```bash
curl -sS http://127.0.0.1:8107/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"fetch_web","arguments":{"url":"https://www.cloudflare.com/cdn-cgi/trace","type":"plain"}}}'
```

The returned text must show the exit you expect: the host IP for direct mode,
the proxy IP for a proxied run. Confirm the actual country yourself; this
project no longer bakes one.
