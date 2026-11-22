# Architecture decisions — psiphon-proxy

## [2026-11-20] ADR-001: Psiphon is an optional backend, not a replacement for WARP

- **Context:** the operator first asked to replace WARP with Psiphon, then removed all proxies after a false blowsh startup failure, then restored Psiphon after the blowsh source was fixed, and finally required both WARP and Psiphon to exist as properly Dockerized, optional backends.
- **Decision:** keep a repo-owned `psiphon-proxy/` build context based on the previously verified recipe: `ubuntu:22.04`, `psiphon-tunnel-core` fetched at build time, baked config with `EgressRegion=US`, HTTP `8082`, SOCKS `1081`, internal-only on a bridge network. Both proxies are opt-in via blowsh's `PROXY_*` variables; no proxy is the default.
- **Alternatives considered:** (a) make Psiphon mandatory — rejected, the operator wants a user choice; (b) mount the host Psiphon config — rejected, it is unreadable and couples blowsh to another stack; (c) download the binary at container start — rejected in favor of a real image with the binary baked in.
- **Consequences:** the exit IP is shared and rotating and the region is a preference. The container must remain unpublished. Switching backends means recreating blowsh with different `PROXY_HOST`/`PROXY_PORT`; no data migration.
- **Rollback:** remove the image and container and recreate blowsh with another proxy mode.

## [2026-11-22] ADR-002: EgressRegion switched from US to DE

- **Context:** the operator wanted a German exit IP for blowsh. The repo had no reference to a "GB node"; the operator clarified the intent as `EgressRegion=DE`, skipping GB. `EgressRegion` is a preference, not a guarantee, so the actual exit had to be traced.
- **Decision:** set `EgressRegion: "DE"` in `psiphon.config`, retag the image `psiphon-proxy:de`, and recreate blowsh on `warp-net` with `PROXY_TYPE=http`, `PROXY_HOST=psiphon-socks`, `PROXY_PORT=8082`, `PROXY_BYPASS=localhost,127.0.0.1`. All prior blowsh environment variables were preserved.
- **Alternatives considered:** (a) keep US — rejected, operator wants a DE IP; (b) GB — explicitly skipped by the operator; (c) WARP/direct — rejected, neither gives a controllable DE exit.
- **Consequences:** the exit IP is shared and rotating and the country is a preference; a live Cloudflare trace is required after any change. Verified on 2026-11-22: `ip=172.105.78.25`, `loc=DE`, `colo=FRA`, `warp=off` from both the proxy container and blowsh's own `fetch_web`.
- **Rollback:** restore `EgressRegion=US`, rebuild `psiphon-proxy:us`, recreate `psiphon-socks`, and recreate blowsh with the same `PROXY_*` variables.
