# Milestone 10 Summary

**Date:** 2026-11-27
**Tasks Compacted:** 2
**Release:** v9.97.0

## Source Distribution

| Source  | Count |
| ------- | ----- |
| manager | 2     |

## Architectural Changes

- **Brain transport migrated to LiteLLM:** `mcp-brain-bridge/server.py` now sends through `litellm.responses(model="openai/<id>", api_base=BRAIN_API_BASE)` with `num_retries=0`. The hand-written `httpx` transport, retry ladder, terminal-429 classifier, and overall deadline are deleted; a failed turn returns a `PROVIDER_ERROR` report and retrying is the caller's decision. 44 per-turn stderr sites are gated behind `BRAIN_DEBUG` (default off).
- **zen-proxy renamed to zen-bridge:** the slice, systemd unit, docs, memory records, and env keys moved to the new name (`ZEN_BRIDGE_*`). The bridge resolves its upstream proxy from `ZEN_BRIDGE_HTTPS_PROXY`/`ZEN_BRIDGE_HTTP_PROXY` with standard-name fallback and forces loopback out of the tunnel; the Brain side mirrors a `BRAIN_*` proxy onto the standard names only when unset. `warp-proxy/` and `psiphon-proxy/` plus every live reference were removed; blowsh egress is now env-only.
- **Environment cleanup:** `.env.example` rebuilt from a project-wide scan; `BRAIN_UPSTREAM_MODE`, `BRAIN_OVERALL_DEADLINE_S`, and every `ZEN_PROXY_*` key were retired; ADR-009 and ADR-015 record the removals and the transport change.
- **Stage prompt roster settled:** each stage ships one lead persona block plus the full seven-seat roster and a new `auto_load` Layer 3 adoption rule. The earlier all-seven-blocks variant was reverted because multiple full personas conflict and burn context every turn. All eight artifacts were regenerated and the stale installed copies were re-synced.
- **Tests retargeted:** 940 passing, with new guards for provider-base resolution, loopback no-proxy forcing, the `BRAIN_DEBUG` switch, and seven-seat roster presence.
- **Global install:** `zen-bridge.service` + `~/.config/opencode/zen-bridge/` replaced the retired unit and directory; brain venv rebuilt with LiteLLM; every singleton runs; global `.env` points at `100.74.8.111:7890` with `muse-spark-1.3-contributor` at `xhigh` for every stage and `BRAIN_DEBUG=0`.
- **Release 9.97.0:** `<system_version>` bumped, `[Unreleased]` emptied, all three entries moved under the dated header, `assemble_system_prompt.py --check` exit 0.

## Files Modified

| File                                     | Change                                                |
| ---------------------------------------- | ----------------------------------------------------- |
| mcp-brain-bridge/server.py               | LiteLLM transport, proxy env mirror, no-retry policy  |
| mcp-brain-bridge/pyproject.toml          | litellm dependency; httpx direct dep dropped          |
| mcp-brain-bridge/README.md               | transport, timeout, stage sections rewritten          |
| mcp-brain-bridge/DECISIONS.md            | ADR-015 supersedes ADR-004/014                        |
| zen-bridge/proxy.py                      | renamed + env-aware upstream proxy and no-proxy guard |
| services/zen-bridge.service              | renamed unit and exec path                            |
| docs/brain-bridge.md                     | LiteLLM transport, proxy/env ladder, retired keys     |
| docs/zen-bridge.md                       | real files, config table, two-hop routing             |
| docs/blowsh-proxy-options.md             | direct default plus any HTTP proxy                    |
| .env.example                             | rebuilt from project-wide scan                        |
| prompts/stage-manifest.json              | lead rosters + Layer 3 adoption rule                  |
| prompts/fragments/06-personas-catalog.md | Layer 3 roster-adoption rule                          |
| prompts/fragments/DECISIONS.md           | ADR for the seat design                               |
| system-prompt.md                         | 9.97.0, regenerated                                   |
| tests/test_brain_bridge.py               | retargeted to the LiteLLM seam                        |
| tests/test_stage_prompts.py              | lead-roster and Layer 3 assertions                    |
| tests/litellm_double.py                  | shared offline LiteLLM double                         |
| CHANGELOG.md                             | [9.97.0] header with all entries                      |

## Criteria Met

| Task | Acceptance Criteria                                                                                                       | Status |
| ---- | ------------------------------------------------------------------------------------------------------------------------- | ------ |
| 425  | pure-Python zen-proxy with CONNECT, identity, endpoints, global install                                                   | ✅ Met |
| 432  | Brain on LiteLLM, zen-bridge rename, proxy removal, env/test/docs cleanup, retry policy removed, seven-seat prompt design | ✅ Met |

## Individual Task Summaries

### Task 425: Enhanced Python zen-proxy

- **Type:** improvement
- **Source:** manager
- **Reasoning:** full rewrite to a pure-Bun transparent proxy with OpenCode-v2 identity, all endpoints including model list, CONNECT allowlist, body cap, global install and systemd restart, then verified end to end.

### Task 432: brain-litellm-zen-bridge-cleanup

- **Type:** feature
- **Source:** manager
- **Reasoning:** migrated the Brain transport to LiteLLM, renamed zen-proxy to zen-bridge with env-driven two-hop proxy routing, removed warp-proxy and psiphon-proxy, rebuilt `.env.example`, retargeted the test suite to the new seam, settled the stage prompt roster on one lead persona plus a Layer 3 adoption rule, and cut release 9.97.0. Full suite 940 passed; `assemble_system_prompt.py --check` exit 0.
