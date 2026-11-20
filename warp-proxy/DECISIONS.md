# Architecture decisions — warp-proxy

## [2026-11-20] ADR-001: WARP stays as an optional backend

- **Context:** WARP was the original blowsh egress, was briefly retired when the real cause of blowsh startup failures turned out to be a source-level 800 ms health probe, and is now required again as one of two optional proxy backends.
- **Decision:** provide a repo-owned `warp-proxy/` build context that wraps the pinned upstream image and bakes `NET_PORT=9091`. WARP is opt-in through blowsh's `PROXY_*` variables and is never mandatory. No proxy remains the default, Psiphon is the alternative.
- **Alternatives considered:** (a) keep using the bare upstream image with a remembered `-e NET_PORT=9091` — rejected because the setting is undocumented and easy to lose; (b) build WARP from source in this repo — rejected as unnecessary maintenance; (c) remove WARP entirely — rejected, the operator requires both options.
- **Consequences:** switching to WARP means recreating blowsh with `PROXY_HOST=warp-socks` and `PROXY_PORT=9091`. A WARP exit IP is shared and may be blocked by some sites.
- **Rollback:** remove the image and container and recreate blowsh with another proxy mode.
