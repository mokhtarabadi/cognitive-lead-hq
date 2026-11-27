---
tags: [blowsh, docker, images, opencode, proxy]
---

# Blowsh image and proxy policy — direct by default, any HTTP proxy by env (supersedes two-backend rule)

Supersedes: opencode_config/blowsh_image_policy (2026-11-20 two-backend rule). Manager ruling 2026-11-27: the `warp-proxy/` and `psiphon-proxy/` build contexts are removed from this repo along with every reference to them. blowsh keeps proxy support but reads it from plain environment variables only.

Policy: blowsh uses the auto-built remote `ghcr.io/mokhtarabadi/blowsh-mcp:latest` and never a pinned tag. Direct egress is the default (`PROXY_TYPE=none`). Any opt-in proxy is supplied by the operator through `PROXY_TYPE=http`, `PROXY_HOST`, `PROXY_PORT`, and `PROXY_BYPASS=localhost,127.0.0.1`; the proxy must share a Docker network with blowsh, publish no host ports, and must be HTTP (blowsh's Node-side axios has no SOCKS agent). This repo no longer builds or owns a proxy image.

Guide: `docs/blowsh-proxy-options.md` (current), `docs/blowsh-direct-egress.md` (default mode). The health-probe fix `BROWSH_HEALTH_PROBE_TIMEOUT_MS` from blowsh-mcp task 269 remains required in any image used with a proxy.
