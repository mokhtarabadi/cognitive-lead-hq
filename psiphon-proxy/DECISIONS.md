# Architecture decisions — psiphon-proxy

## [2026-11-20] ADR-001: Psiphon is an optional backend, not a replacement for WARP

- **Context:** the operator first asked to replace WARP with Psiphon, then removed all proxies after a false blowsh startup failure, then restored Psiphon after the blowsh source was fixed, and finally required both WARP and Psiphon to exist as properly Dockerized, optional backends.
- **Decision:** keep a repo-owned `psiphon-proxy/` build context based on the previously verified recipe: `ubuntu:22.04`, `psiphon-tunnel-core` fetched at build time, baked config with `EgressRegion=US`, HTTP `8082`, SOCKS `1081`, internal-only on a bridge network. Both proxies are opt-in via blowsh's `PROXY_*` variables; no proxy is the default.
- **Alternatives considered:** (a) make Psiphon mandatory — rejected, the operator wants a user choice; (b) mount the host Psiphon config — rejected, it is unreadable and couples blowsh to another stack; (c) download the binary at container start — rejected in favor of a real image with the binary baked in.
- **Consequences:** the exit IP is shared and rotating and the region is a preference. The container must remain unpublished. Switching backends means recreating blowsh with different `PROXY_HOST`/`PROXY_PORT`; no data migration.
- **Rollback:** remove the image and container and recreate blowsh with another proxy mode.
