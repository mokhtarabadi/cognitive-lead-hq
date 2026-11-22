---
tags: [blowsh, docker, images, opencode, proxy]
---

# Blowsh image and proxy policy — two optional backends (supersedes direct-only rule)

Supersedes: opencode_config/blowsh_image_policy (2026-11-20 direct-egress rule). Manager ruling 2026-11-20: blowsh normally uses the auto-built remote `ghcr.io/mokhtarabadi/blowsh-mcp:latest` and never a pinned tag. Two proxy backends are supported and both are OPTIONAL, selected by the operator through `PROXY_*` env vars on blowsh-singleton: WARP via `warp-proxy/` (`warp-socks:9091`) and Psiphon via `psiphon-proxy/` (`psiphon-socks:8082`, EgressRegion DE as of 2026-11-22). Direct mode (`PROXY_TYPE=none`) is the default when no proxy is chosen. Neither proxy is mandatory. Both containers must stay unpublished on a bridge shared with blowsh; keep `PROXY_BYPASS=localhost,127.0.0.1`.

Current live state (verified 2026-11-22): Psiphon mode is enabled on the remote `:latest` blowsh image with `EgressRegion=DE`. Baked config is in `psiphon-proxy/psiphon.config`; the image tag `psiphon-proxy:de` records the region preference. Live verification returned `ip=172.105.78.25`, `loc=DE`, `colo=FRA`, `warp=off` from both the proxy container trace and blowsh's own `fetch_web`, and BrowserLeaks showed the DE flag for the primary IP. The previous US exit (`ip=104.131.189.185`, `loc=US`) was superseded on 2026-11-22 at the operator's request (the ambiguous "GB node" wording was clarified as EgressRegion DE). The current guide is `docs/blowsh-proxy-options.md`; the retired single-proxy wording in `docs/blowsh-warp-proxy.md` was replaced by the WARP option guide. The fix for the old 800 ms health probe is `BROWSH_HEALTH_PROBE_TIMEOUT_MS` in blowsh-mcp task 269. Do not delete the locally built fixed image until the remote `:latest` is confirmed to contain that fix.

Supersedes: opencode_config/blowsh_image_policy (2026-11-20 revision: EgressRegion US, US exit IP — stale as of 2026-11-22).