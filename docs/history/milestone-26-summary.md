# Milestone 26 Summary

**Date:** 2026-11-24
**Tasks Compacted:** 16
**Release:** v9.96.0

## Source Distribution

| Source       | Count |
| ------------ | ----- |
| orchestrator | 1     |
| manager      | 15    |

## Architectural Changes

- Moved blowsh egress through Dockerized WARP and Psiphon proxies, then restored both as optional backends with direct egress as the default (Tasks 406, 407).
- Repaired the OpenChamber service after reboot and reconciled its auth and bind documentation with the live install (Tasks 408, 410).
- Hardened the planner dashboard across projects: absolute `project_root`, HTTP 500 on failure, real finished-today counts, UTC anchors, canonical milestones, month proration, escaped estimates, and focus-trapped dialogs (Task 409).
- Refreshed stale global-install memory records and added the DeepSeek chat-completions hardening for usage details, reasoning budgets, and terminal 429 handling (Tasks 411, 412).
- Hardened zen-proxy with allowlist pruning, keyless refresh, health checks, and documentation (Task 413).
- Delivered comprehensive prompt and workflow hardening: manual/automatic topology reconciliation, approval literals, ZAC consolidation, Context Map, parallel discovery, direct-input plan gate, and generated prompt sync (Task 417).
- Made context MCP tool outputs agent-facing, removed copy/paste instructions, and added multi-project brain root handling with sprint/planner stages (Tasks 418, 419).
- Stabilized the HQ suite: 988 passing assertions, auth-isolation fixes, shared-path race elimination, and no tests weakened (Task 420).
- Canonicalized user-facing responses with one Manager-Facing Concision Contract across prompt and agents (Task 421).
- Made stage-prompt regeneration mandatory every release, added runtime stale-stage fallback and a byte-freshness gate, and repaired the handoff test (Task 422).
- Split the versioning skill into a portable core plus optional harness profile, added mandatory omitted-output recovery, and introduced the `brain-orchestration` skill (Task 423).
- Made Brain raw output immutable before triage, added truthful diagnostics and a deterministic Hands helper, and enforced non-executable partial XML (Task 424).

## Files Modified

| File                                              | Change                                                                                          |
| ------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `mcp-brain-bridge/server.py`                      | Raw-before-triage persistence, additive diagnostics, stage fallback, chat-completions hardening |
| `mcp-brain-bridge/parse_brain_output.py`          | New deterministic artifact parser/helper                                                        |
| `agents/cognitive-executor.md`                    | Recovery gate, raw-output contract, and concise response rule                                   |
| `agents/cognitive-discovery.md`                   | Concise response rule                                                                           |
| `prompts/fragments/*`                             | Portable release guidance, output recovery, Brain skill registry, version 9.96.0                |
| `skill-templates/versioning-and-release/SKILL.md` | Portable core plus optional harness profile                                                     |
| `skill-templates/brain-orchestration/SKILL.md`    | New Brain platform skill template                                                               |
| `system-prompt.md` + `build/stage-prompts/*`      | Regenerated and freshness-checked at 9.96.0                                                     |
| `CHANGELOG.md`                                    | v9.96.0 release entries                                                                         |
| `tests/*`                                         | Portability, recovery, Brain-skill, prompt-sync, and stage-freshness coverage                   |
| `docs/*`, `scripts/*`                             | Brain output contract, release invariants, deploy and freshness docs                            |
| `tasks/completed/*`                               | 16 tasks archived to `tasks/archive/`                                                           |

## Criteria Met

| Task | Acceptance Criteria                                         | Status |
| ---- | ----------------------------------------------------------- | ------ |
| 406  | Docker WARP egress documented and verified                  | ✅ Met |
| 407  | Optional WARP/Psiphon proxies documented and verified       | ✅ Met |
| 408  | OpenChamber service path repaired and verified              | ✅ Met |
| 409  | Planner hardening across all five projects                  | ✅ Met |
| 410  | OpenChamber docs freshness checked against upstream         | ✅ Met |
| 411  | Stale global-install memory records refreshed               | ✅ Met |
| 412  | DeepSeek chat-completions hardening verified                | ✅ Met |
| 413  | zen-proxy hardening and documentation verified              | ✅ Met |
| 417  | Prompt/workflow hardening complete with sync gates          | ✅ Met |
| 418  | Agent-facing context tool outputs pinned                    | ✅ Met |
| 419  | Multi-project brain root and stage routing verified         | ✅ Met |
| 420  | HQ suite stabilized with 988 passed assertions              | ✅ Met |
| 421  | Concise response contract mirrored in both agents           | ✅ Met |
| 422  | Stage regeneration and freshness gate enforced              | ✅ Met |
| 423  | Portable release skill, recovery gate, Brain skill verified | ✅ Met |
| 424  | Raw-first persistence and deterministic recovery verified   | ✅ Met |

## Individual Task Summaries

### Task 406: Run Cloudflare WARP in Docker as blowsh proxy, document the setup

- **Type:** infrastructure + documentation
- **Source:** manager
- **Reasoning:** Added a Dockerized WARP egress option for blowsh and documented the setup and verification path.

### Task 407: Optional WARP and Psiphon Docker proxies for blowsh

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Restored WARP and Psiphon as optional Dockerized backends while keeping direct egress as the default.

### Task 408: Fix OpenChamber service CLI path after reboot

- **Type:** bug
- **Source:** manager
- **Reasoning:** Corrected the service entry point to the upgraded CLI path and verified the service stays active.

### Task 409: Planner MCP dashboard hardening across all projects

- **Type:** bug
- **Source:** manager
- **Reasoning:** Hardened planner APIs, milestone handling, auth, and dashboard behavior across projects.

### Task 410: OpenChamber docs freshness check against upstream

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Added docs freshness checks and corrected environment/bind guidance.

### Task 411: Refresh stale global-install memory records

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Refreshed stale global-install memory records and regenerated the memory index.

### Task 412: DeepSeek Chat Completions Hardening

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Hardened chat-completions usage, reasoning, budget, and terminal error handling.

### Task 413: zen-proxy hardening — allowlist prune, keyless refresh, health, docs

- **Type:** improvement
- **Source:** orchestrator
- **Reasoning:** Hardened zen-proxy health, allowlists, refresh behavior, and documentation.

### Task 417: Comprehensive prompt and workflow hardening across fragments, agents, and brain context

- **Type:** feature
- **Source:** manager
- **Reasoning:** Reconciled manual/automatic topology, consolidated approval and ZAC rules, added Context Map, and regenerated the prompt.

### Task 418: Agent-facing context MCP tool outputs

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Made context tool output agent-facing and removed copy/paste instructions.

### Task 419: Multi-project brain root handling

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Documented and implemented multi-project brain root handling and stage routing.

### Task 420: Stabilize and simplify the HQ test suite

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Fixed stale fixtures, auth isolation, and shared-path races while preserving the test floor.

### Task 421: Concise User-Facing Responses Across Agents and System Prompt

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Added one canonical Manager-Facing Concision Contract and removed competing length budgets.

### Task 422: Regenerate Stage Prompts Every Release and Repair Handoff Test

- **Type:** bug
- **Source:** manager
- **Reasoning:** Made stage regeneration mandatory, added freshness gating, and repaired the handoff test.

### Task 423: Portable Release Skill, Omitted-Output Recovery, and Brain Orchestration Skill

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Split portable release rules from harness profile, added omitted-output recovery, and registered Brain orchestration.

### Task 424: Raw-First Brain Output with Deterministic Hands Recovery

- **Type:** bug
- **Source:** manager
- **Reasoning:** Preserved raw provider output before triage, added truthful diagnostics and a deterministic helper, and kept malformed XML non-executable.

## Archived Tasks

All 16 source task files from `tasks/completed/` were moved to `tasks/archive/` as part of this release. History remains reachable with `git log --oneline --follow -- tasks/archive/<file>`.
