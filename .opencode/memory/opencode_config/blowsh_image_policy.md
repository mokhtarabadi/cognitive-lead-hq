---
tags: [blowsh, docker, images, opencode, proxy]
---

# Blowsh image and proxy policy — two optional backends (supersedes direct-only rule)

Supersedes: opencode_config/blowsh_image_policy (2026-11-20 direct-egress rule). Manager ruling 2026-11-20: blowsh normally uses the auto-built remote `ghcr.io/mokhtarabadi/blowsh-mcp:latest` and never a pinned tag. Two proxy backends are supported and both are OPTIONAL, selected by the operator through `PROXY_*` env vars on blowsh-singleton: WARP via `warp-proxy/` (`warp-socks:9091`) and Psiphon via `psiphon-proxy/` (`psiphon-socks:8082`, EgressRegion US). Direct mode (`PROXY_TYPE=none`) is the default when no proxy is chosen. Neither proxy is mandatory. Both containers must stay unpublished on a bridge shared with blowsh; keep `PROXY_BYPASS=localhost,127.0.0.1`.

Current live state: Psiphon mode is enabled on the fixed blowsh image, verified with a US exit IP. The current guide is `docs/blowsh-proxy-options.md`; the retired single-proxy wording in `docs/blowsh-warp-proxy.md` was replaced by the WARP option guide. The fix for the old 800 ms health probe is `BROWSH_HEALTH_PROBE_TIMEOUT_MS` in blowsh-mcp task 269. Do not delete the locally built fixed image until the remote `:latest` is confirmed to contain that fix.
