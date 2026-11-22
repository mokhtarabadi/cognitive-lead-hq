# Architectural Decisions: docs

## [2026-10-06] ADR-001: Initial Slice Baseline

- **Context:** Baseline documentation initialized via init-folder-docs.
- **Decision:** Adopting Living Folder Docs standard for this component.
- **Consequences:** All future structural or contract changes must be recorded here.
- **Rollback:** N/A (baseline adoption).

## [2026-10-21] ADR-002: Telegram Message Formatting Contract Lives in `docs/`

- **Context:** The Telegram MCP's real formatting behavior (HTML preserved, Markdown fences consumed, 4096-char limit, lost ZWNJ, no `topic_id` on `send_message`) was proven empirically on 2026-10-21 and handed over as a document. It had no home in the repo, so every agent that sends a Telegram message re-derives it or ignores it.
- **Decision:** The contract is stored verbatim as `docs/telegram-message-formatting.md` (server-side facts plus a binding authoring-rules table). The agent-facing rulebook is a skill, `skill-templates/telegram-message-format/SKILL.md`, so the Hands can load it on demand; the doc stays the reference the skill points at.
- **Consequences:** Every Telegram send from a skill or a direct MCP call must load the skill and obey the 9 authoring rules. The two Telegram skills and the Hands skill matrix now name it explicitly.
- **Rollback:** Delete the skill and the doc, and remove the registry line, the skill-matrix row, and the skill references from the two Telegram skills.

## [2026-10-27] ADR-003: Setup Docs Stay Runtime-Neutral

- **Context:** `docs/telegram-setup.md` labeled callback mode "for Claude Code", listed only external MCP clients, and gave a `claude mcp add` command; `docs/brain-bridge.md` presented one vendor trio as the industry pattern. Operating docs must describe this platform first.
- **Decision:** Callback mode is labeled for agentic clients; client lists name OpenCode first with others as compatible examples; the vendor trio became "OpenCode and other agentic clients".
- **Consequences:** Setup docs no longer route the reader to another runtime. External-client interop facts are kept, not deleted.
- **Rollback:** Restore the prior wording from git history.

## [2026-10-28] ADR-004: Server Browser Runbook Lives in `docs/openchamber.md`

- **Context:** Enabling agent-driven browsing took a full debug session (display-only tabs, missing Chrome, snap-stub trap, sandbox SIGTRAP, squashfs leftovers, self-matching `pkill`). None of it was written down, so the next installer would repeat every step.
- **Decision:** The complete runbook is `docs/openchamber.md` §10 (install, headless-shell over apt-chromium, `--no-sandbox` wrapper, `config.json`, daily use, troubleshooting, snap removal); `LLM.txt` carries a §7.10 pointer plus a verification-checklist line.
- **Consequences:** Future browser setups follow one doc instead of rediscovery.
- **Rollback:** Delete §10, §7.10, and the checklist line.

## [2026-11-18] ADR-005: WARP proxy lives inside Docker, not on the host

- **Context:** The host proxy on port 7890 is unreachable from every bridge container because the host firewall drops container-to-host connections on all tested ports. A live container-to-container test on the same bridge returned `BRIDGE_OK`. The VPS IP is not clean enough for the web research workload, so a clean exit is required.
- **Decision:** Run `ghcr.io/mon-ius/docker-warp-socks:v8` on a dedicated `warp-net` bridge and connect blowsh with `PROXY_TYPE=http` to `warp-socks:9091`. HTTP mode is required because the Node-side axios has no SOCKS agent. Loopback stays in `PROXY_BYPASS` to protect the Browsh control channel. The full procedure is `docs/blowsh-warp-proxy.md`.
- **Consequences:** Browser renders and axios egress both use the Cloudflare WARP exit IP. The shared WARP IP may still be blocked by some sites, and the no-proxy setup remains the documented rollback.
- **Rollback:** Recreate blowsh with `PROXY_TYPE=none`, remove `warp-socks`, and delete the guide.

## [2026-11-20] ADR-006: Direct egress replaces WARP and Psiphon

- **Context:** The operator asked to move blowsh off WARP to a Psiphon Docker proxy with a US exit. During deployment every `fetch_web` failed with `FetchError: Browsh did not start in HTTP mode within timeout`. Live measurement showed Browsh's control endpoint answering HTTP 200 in 0.9–2 s while the manager's hardcoded 800 ms health probe timed out every time. Raising `BROWSH_STARTUP_TIMEOUT_MS` to 300 s did not help, and the same failure reproduced with proxying fully off. The proxy was incidental; the defect was in the blowsh source.
- **Decision:** Fix the source in `blowsh-mcp` (`BROWSH_HEALTH_PROBE_TIMEOUT_MS`, default 5000 ms; no profile quarantine on a pure probe timeout) and retire both proxy containers. `blowsh-singleton` runs with `PROXY_TYPE=none` on the default bridge using the locally built fixed image. `docs/blowsh-direct-egress.md` is the current guide; `docs/blowsh-warp-proxy.md` is retired history.
- **Consequences:** A real `fetch_web` render succeeds in about 10 s with no proxy. Exit traffic now uses the VPS IP, which may be blocked by some sites; the proxy knobs remain available if a clean exit is needed again. The deployed image is local until the source fix is pushed to the GitHub image repo and the remote `:latest` picks it up.
- **Rollback:** Recreate blowsh with `PROXY_TYPE=http` and a proxy endpoint; the previous procedure stays in git history and in the retired guide.

## [2026-11-20] ADR-007: Two optional proxy backends replace the one-way retirement

- **Context:** after the blowsh health-probe source fix, direct egress was made the default and both proxy containers were removed. The operator then restored Psiphon for a live render and finally required both proxy types to exist as properly Dockerized, optional backends that the user may enable for blowsh.
- **Decision:** keep two repo-owned build contexts. `warp-proxy/` wraps the pinned upstream image and bakes `NET_PORT=9091`; `psiphon-proxy/` builds `ubuntu:22.04` with `psiphon-tunnel-core` and a baked `EgressRegion=US` config. Neither proxy is mandatory. `docs/blowsh-proxy-options.md` is the comparison; each mode has its own deployment guide; direct remains the default. Blowsh selects a backend only through `PROXY_*` variables.
- **Alternatives considered:** (a) mandatory Psiphon — rejected, the operator wants a choice; (b) keep only WARP — rejected, both types are required; (c) keep only direct — rejected, some sites block the VPS IP; (d) share one Dockerfile for both backends — rejected, the binaries and configs are unrelated.
- **Consequences:** switching modes means recreating blowsh with different `PROXY_HOST`/`PROXY_PORT`; no data migration or profile reset. Both proxies must stay unpublished on a bridge. The live deployment currently uses Psiphon with the fixed blowsh image.

## [2026-11-22] ADR-008: Psiphon EgressRegion switched to DE for blowsh

- **Context:** the operator asked for a German exit IP for blowsh and clarified the earlier ambiguous "GB node" wording as `EgressRegion=DE`, skipping GB. The baked config used `EgressRegion=US`. `EgressRegion` is a preference, not a guarantee, so the exit had to be traced live.
- **Decision:** set `EgressRegion: "DE"` in `psiphon-proxy/psiphon.config`, build `psiphon-proxy:de`, run `psiphon-socks` on the `warp-net` bridge, and recreate `blowsh-singleton` with all prior environment preserved plus `PROXY_TYPE=http`, `PROXY_HOST=psiphon-socks`, `PROXY_PORT=8082`, `PROXY_BYPASS=localhost,127.0.0.1`.
- **Alternatives considered:** (a) keep US — rejected, a DE IP was requested; (b) GB — explicitly skipped; (c) WARP or direct — rejected, neither offers a controllable country exit.
- **Consequences:** the shared, rotating exit country remains a preference and must be re-traced after any change. Verified 2026-11-22: `ip=172.105.78.25`, `loc=DE`, `colo=FRA`, `warp=off` from both the proxy container and blowsh's own `fetch_web`. The sibling `psiphon-proxy/ADR-002` records the build-context decision.
- **Rollback:** restore `EgressRegion=US`, rebuild `psiphon-proxy:us`, recreate the proxy and blowsh with the same `PROXY_*` variables.
- **Rollback:** remove either build context and its container and recreate blowsh in direct mode.
