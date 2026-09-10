# Milestone 17 Summary

**Date:** 2026-09-10
**Tasks Compacted:** 15
**Version:** 9.13.0

## Source Distribution

| Source       | Count |
| ------------ | ----- |
| orchestrator | 0     |
| telegram     | 2     |
| manager      | 13    |

## Architectural Changes

Milestone 17 spans release + plugin installs (162-164), OpenChamber multi-device (165-166), persona/decision automation build (167-168), workspace hardening META (171-172), docs follow-up (173), persona expansion + automation pause (174-176), and audit/hardening + prompt optimization (177-178).

- **Release + plugins (162-164):** Archived 31 completed tasks into milestone-16, released v9.10.0 via Parse-Then-Append with push script, drift-audited and re-synced global install + Telegram fork (162); integrated `@tarquinen/opencode-dcp` mirroring the goal-plugin pattern across repo + global configs and LLM.txt (163); installed `@nano-step/opencode-worktree-plugin` globally via `owt-setup` with `.gitignore` guards + docs, deliberately NOT in plugin arrays (docs-only repo has no node_modules).
- **OpenChamber (165-166):** Researched OpenChamber v1.22.2, installed globally via npm on alternate port 3005 (3000 taken by Next.js), Tailscale-only bind with UI password in `~/.secrets`, disabled goal + worktree plugins (DCP-only), Cloudflare Tunnel deferred; added optional-install LLM.txt guide with ask-user-first gate plus auto-start and pairing runbook.
- **Automation build (167-168):** Retired the full `loop-engine/` daemon (48 files) + `deploy/`, replaced with `mcp-persona-server/` (Dual Dispatch, session transcripts, Telegram approval gates) and 4 slash commands; added `mcp-decision-server/` (redaction, decision repo schema, review-gated profile evolution) with `manager-decision` skill template and executor integration.
- **Hardening META (171-172):** Bundled post-sprint fixes (DECISION_TEMPERATURE, BOM handling, docstring drift guards) with MCP workspace cleanup (shared `mcp-common`, per-server pyprojects + uv.lock, split PERSONA/DECISION models, approval notes); sync task re-staged 3 files whose fixes missed the closure commit.
- **Pause + audit (174-178):** Added 5 missing persona commands and removed the `brainstorm-swarm` skill wrapper (scheme survives in fragment 12), then paused the whole automation (executor sections commented, 9 commands archived, both MCP servers unwired repo + global) back to manual workflow; hardened `mcp-context-server` (traversal rejection, depth/entry/file caps, banned dirs, report metrics), added `blowsh` skill, archived stale loop-engine docs, and stubbed the brainstorming protocol + scoped clarity style while bumping system-prompt 9.10.0 → 9.13.0.

## Files Modified

| File                                                   | Change                                                                                                        |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| docs/history/milestone-16-summary.md                   | New 31-task archive (162)                                                                                     |
| CHANGELOG.md                                           | 9.10.0 release + Unreleased entries for 163-178                                                               |
| opencode.json + tui.json (repo + global)               | DCP added (163), dcp-only after goal removal (165), persona/decisions added (167-168) then removed (176)      |
| LLM.txt                                                | DCP docs, owt section, OpenChamber optional guide, plugin install verification (163-166, 173)                  |
| mcp-persona-server/                                    | New persona dispatch server + session/telegram modules + fixes (167, 171, 174)                                 |
| mcp-decision-server/                                   | New decision learning server + redactor (168)                                                                 |
| mcp-context-server/server.py                           | Workspace confinement + runaway caps + report metrics (177)                                                   |
| mcp-common/ + per-server pyproject/uv.lock             | Locked workspace with shared loader (171)                                                                     |
| .opencode/commands/                                    | 9 persona commands created (167, 174), then archived (175)                                                    |
| agents/cognitive-executor.md + cognitive-discovery.md  | Persona/decision loops, manual workflow default, clarity style (167-168, 174-175, 178)                        |
| prompts/fragments/* + system-prompt.md                 | Skills registry, brainstorm stub, clarity constraints, 9.10.0 → 9.13.0 (174, 177-178)                          |
| skill-templates/                                       | manager-decision added (168), brainstorm-swarm removed/restored inert (174-175), blowsh added (177)            |
| docs/openchamber-tailscale.md                          | New Tailscale pairing + ops runbook (165)                                                                     |
| archive/automation-paused-2026-09-09/                  | Archived commands, loop-engine docs, RESTORE.md with verbatim JSON blocks (175-177)                            |
| .env.example                                           | PERSONA_*/DECISION_* vars added then PAUSED-commented (167-168, 176)                                          |
| packages/cognitive-lead-decisions/                     | Decision repo schema + validate/compile scripts (168)                                                         |
| README.md + .gitignore                                 | Plugin blocks, paused banner, blowsh row; worktree + cache guards (164, 166, 173, 177)                         |
| scripts/smoke_test_live.py                             | Added (171) then removed as inapplicable while servers paused (177)                                           |

## Criteria Met

| Task | Acceptance Criteria                                                        | Status |
| ---- | -------------------------------------------------------------------------- | ------ |
| 162  | Milestone-16 archived, 9.10.0 released, global + fork synced               | ✅ Met |
| 163  | DCP in all 4 plugin arrays, docs + global install verified                 | ✅ Met |
| 164  | owt installed globally, project guards + docs, tests green                 | ✅ Met |
| 165  | OpenChamber on 3005 via Tailscale, dcp-only configs, runbook written       | ✅ Met |
| 166  | LLM.txt optional OpenChamber guide + checklist, Tailscale-only verified    | ✅ Met |
| 167  | Loop-engine removed, persona MCP spec + Telegram approval gate defined     | ✅ Met |
| 168  | Decision schema + invocation contract + gated evolution loop               | ✅ Met |
| 171  | META 169+170 bundled: split models, approval notes, locked workspace       | ✅ Met |
| 172  | Stranded fixes re-staged, headers synced, suite green                      | ✅ Met |
| 173  | Plugin install + cache-verify docs in LLM.txt and README                   | ✅ Met |
| 174  | 5 persona commands added, brainstorm skill removed, prompt 9.10.0 in sync  | ✅ Met |
| 175  | Executor automation commented, 9 commands archived, manual default active  | ✅ Met |
| 176  | Both MCP servers unwired repo + global, restore record complete            | ✅ Met |
| 177  | Audit cleanup, server hardening, blowsh skill, prompt 9.12.0 in sync      | ✅ Met |
| 178  | Brainstorm stub + scoped clarity style, prompt 9.13.0 in sync             | ✅ Met |

## Individual Task Summaries

### Task 162: Archive Release Global Upgrade

- **Type:** feature
- **Source:** manager
- **Reasoning:** Archived 31 completed tasks to milestone-16, released v9.10.0 with push script, re-synced global install + Telegram fork; all suites green (55 + 309 + 446 passed).

### Task 163: Integrate DCP Dynamic Context Pruning Like Goal Plugin

- **Type:** feature
- **Source:** manager
- **Reasoning:** Mirrored goal-plugin pattern for DCP across project + global configs with LLM.txt docs; official installer used globally, upstream-slowdown caveat documented.

### Task 164: owt Worktree Plugin Integration (Project + Global)

- **Type:** feature
- **Source:** manager
- **Reasoning:** Chose `@nano-step/owt` over OCX-only/fork alternatives; gatekeeper deviation kept it out of plugin arrays (no node_modules in docs-only repo), global file-based install covers all sessions.

### Task 165: OpenChamber Install + Multi-Device (Android/PC) + Internet Exposure via Cloudflare

- **Type:** feature
- **Source:** manager
- **Reasoning:** Installed OpenChamber 1.22.2 globally on port 3005 Tailscale-only with UI password; goal/worktree plugins disabled; Cloudflare Tunnel deferred per Manager directive.

### Task 166: Update LLM.txt with optional OpenChamber install guide

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Added ask-first optional install section with Tailscale bind + auto-start + pairing steps; consolidated prior hardening docs in the same diff, no secrets staged.

### Task 167: Replace Loop-Engine With Persona Skill-MCP Slash Commands

- **Type:** improvement
- **Source:** telegram
- **Reasoning:** Decommissioned 48-file loop-engine daemon; built `mcp-persona-server` with Dual Dispatch + Telegram gates and slash commands; QA rounds fixed dispatch precision, gate scoping, and lineage dedupe (87 passed).

### Task 168: Manager-Decision Skill With Separate Learning Repo

- **Type:** feature
- **Source:** telegram
- **Reasoning:** Built decision repo schema with verbatim quotes + redaction, `mcp-decision-server` with 5 tools, skill template, and review-gated profile evolution (101 passed with persona suite).

### Task 171: post-sprint-workspace-bundle

- **Type:** feature
- **Source:** manager
- **Reasoning:** META bundling post-sprint fixes (temperature env, BOM, drift guards) with MCP workspace lockdown (mcp-common, uv.lock, split models, approval notes); survived QA_REJECTED + reviewer FAIL triage with evidence (120 passed).

### Task 172: Sync Stranded Post-Closure Fixes

- **Type:** bug
- **Source:** manager
- **Reasoning:** Staging-only sync: re-staged 3 files whose working-tree fixes missed the Task 171 closure commit; no code changes, suite green on exact tree.

### Task 173: Plugin Install Docs Follow-Up

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Documented the referenced-but-never-installed plugin outage (install commands + cache verification + restart) in LLM.txt and README; QA scope-creep nit fixed.

### Task 174: Add missing persona slash commands and remove brainstorm-swarm skill

- **Type:** feature
- **Source:** manager
- **Reasoning:** Added 5 missing persona commands, removed skill wrapper (swarm scheme survives in fragment 12), rebuilt prompt to 9.10.0; manager-ordered extension fixed persona persistence, context lane, gate bottlenecks, and lineage fallback (138 passed).

### Task 175: Disable automation in Cognitive Executor agent, archive automation commands, restore manual workflow

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Paused immature automation via HTML comments + `git mv` of 9 commands to archive with RESTORE.md; zero deletions, manual workflow restored as active default.

### Task 176: Disable persona + decision MCP servers (repo + global), document rollback/restore record

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Removed both MCP blocks + permission lines from repo and global configs (JSON has no comments), preserved verbatim blocks in task log + RESTORE.md; 5 remaining servers verified connected.

### Task 177: Comprehensive audit cleanup, MCP server hardening, and blowsh skill integration

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Archived stale loop-engine docs, hardened context server against wedging bugs with regression tests, added blowsh skill, overhauled README; paused state preserved throughout (145 passed).

### Task 178: Prompt optimization — brainstorm stub + clarity style

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Stubbed 53-line brainstorming protocol to 6-line hybrid trigger (~350 tokens saved) and added final-response-only clarity constraints; prompt reassembled byte-identical at 9.13.0.
