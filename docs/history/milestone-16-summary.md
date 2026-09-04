# Milestone 16 Summary

**Date:** 2026-09-04
**Tasks Compacted:** 31
**Version:** 9.10.0 (MINOR, pending release Task 162)

## Source Distribution

| Source       | Count |
| ------------ | ----- |
| orchestrator | 13    |
| telegram     | 6     |
| manager      | 12    |

## Architectural Changes

Milestone 16 spans infra hardening (125-132), loop-engine polyglot + governance Phases A/B (133-142), hotfix resilience (HOTFIX-01, 149), prompt/tooling purification (151-156), and release automation (157-161).

- **Infra/Memory (125-128):** Removed opentmux/agent-tmux globals (keep system tmux); migrated goal plugin to `@prevalentware/opencode-goal-plugin` (opencode.json + tui.json parity); auto-generated `.opencode/memory/index.md` via mcp-memory-server integrated into executor + system prompt; fixed telegram-issue-sync `topic_id` leak (client reply_to filter) + telegram-mcp allowed-root auto-mkdir.
- **Task lifecycle hardening (130-132):** Replaced inline task-ID discovery with `task-generator` skill single source of truth; mandated AC/DoD box-checking at implementation time + closing-tag normalization (Prettier); verified/fixed loop-engine critical bugs LE-0.1–LE-0.4 with CONFIRMED/REFUTED gates.
- **Loop-engine polyglot (133-137):** Stack Profile Engine (YAML profiles, two-tier detection, preflight toolchain validation); Polyglot Verification + Multi-Toolchain Runner (deterministic lint/build/test, timeout, fail-fast, evidence pre-QA); Stack-Aware LLM Router (3-tier model hierarchy, stack propagation); Executor stack context + goal-plugin termination tokens + process-group isolation + semaphore; polyglot smoke suite driving real StateMachine/Router/QA/Executor/Gateway/Daemon.
- **Governance Phases A/B (138-142):** Contract Propagation Dispatcher LE-6 (contract globs → downstream backlog, sequential IDs, BACKLOG state); No-Manual-DTO Mandate + TypeDriftSentinel LE-7 (fragment 20, consumer DTO fail-fast); Spec-First Pipeline + State Gate LE-8 (ADR/PRD/Contract/DataModel verification); Blast-Radius Analyzer (package discovery, reverse-dep graph, affected matrix, verifier scoping); Phase B contract smoke suite (14 tests, full daemon lifecycle certification).
- **Resilience (HOTFIX-01, 149/HOTFIX-02-06):** SQLite `check_same_thread=False` + boot-scan PENDING_TRIGGER re-trigger + poller-before-boot; gateway `_send_with_retry` backoff + InvalidToken fail-fast + SQLite dead_letter_queue; telemetry content_len; path `resolve_actual_task_path` Kanban search; reasoning_content fallback + None-body placeholder; in-flight task locks + instant callback ack + poller containment + max_tokens 8192.
- **Prompt/tooling purification (151-156):** Removed decision-logging pipeline (fragment 17, task sections) to kill rationalization; added self-improvement protocol fragment (21, /reflect); fixed audit-agents scope leak (HQ-only rules stay in AGENTS.md, template stays project-agnostic); atomic `custom_context_qa_transition` MCP tool; pure-MCP bundling (retired `scripts/bundle-tasks.py`, `scripts/qa-transition.py`, promoted helpers to module level); coach prompt alignment + 10 user-prompts quad-fence standardization + README pure-MCP overhaul.
- **Release automation (157-159):** v9.8.0 push-script generator + global upgrade hardening (drift audit → copy → re-verify → smoke); v9.9.0 deprecated-section purge (Manager/Admin Decision remnants), 1-click fences, README SEO overhaul, backlog orphan purge; v9.9.0 publication + global sync (system-prompt 9.9.0 byte-identical, tui.json + goal plugin parity).
- **Stabilization + readiness (160-161):** Stale suite repair (bundle helpers import retarget, splitter TOP_LEVEL_TAGS drift); production-readiness META (143-148): multi-project routing, gateway resilience, metrics/Sentry, ReleaseEngine SemVer, Docker/Compose/systemd deployment, vertical-slice hermetic certification (309 passed).

## Files Modified

| File                         | Change                                                                                                                                                                     |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| loop-engine/*.py             | Stack profiles, toolchain runner, router, executor, contracts, sentinel, spec gate, blast_radius, gateway resilience, metrics, release engine, daemon locks/path/telemetry |
| loop-engine/test_*.py        | Polyglot smoke, contract smoke, blast, multi-project, resilience, metrics, release, vertical-slice suites                                                                  |
| prompts/fragments/*          | Removed 17-decision-logging, added 21-self-improvement, 20-no-manual-DTO, 09-QA-transition, 10-Lite retarget, audit purge rules                                            |
| system-prompt.md             | Reassembled to 9.9.0 (75689 bytes), byte-identical to fragments                                                                                                            |
| mcp-context-server/server.py | bundle_tasks pure helpers (module-level), qa_transition tool                                                                                                               |
| mcp-memory-server/server.py  | Memory index auto-generation + build_memory_index                                                                                                                          |
| mcp-lint-server/server.py    | lint_task_file, lint_markdown, lint_system_prompt_sync                                                                                                                     |
| skill-templates/*            | audit-agents purge rule, bundle-tasks/task-generator pure-MCP, telegram-issue-sync topic filter                                                                            |
| agents/*                     | cognitive-executor/disco memory-index + stack context                                                                                                                      |
| docs/loop-engine/*           | configuration, deployment, README Phase B                                                                                                                                  |
| deploy/*                     | Dockerfile, docker-compose.yml, systemd service, healthcheck.py                                                                                                            |
| user-prompts/*               | Quad-fence wrappers, coach persona upgrades                                                                                                                                |
| README.md                    | Pure-MCP rewrite, SEO header, milestone table                                                                                                                              |
| .opencode/memory/index.md    | Auto-generated index (derived state)                                                                                                                                       |

## Criteria Met

| Task      | Acceptance Criteria                                                     | Status |
| --------- | ----------------------------------------------------------------------- | ------ |
| 125       | opentmux removed, tmux kept, docs clean                                 | ✅ Met |
| 126       | prevalentware plugin in opencode.json + tui.json, docs/memories updated | ✅ Met |
| 127       | index auto-generated + executor integration                             | ✅ Met |
| 128       | topic filter + auto-mkdir, no cross-topic leak                          | ✅ Met |
| 129       | decision detection into task files                                      | ✅ Met |
| 130       | generator skill mandate, no hallucinated IDs                            | ✅ Met |
| 131       | AC/DoD checked at impl, tags normalized                                 | ✅ Met |
| 132       | CONFIRMED bugs patched with verdicts                                    | ✅ Met |
| 133       | stack profiles + detection + preflight                                  | ✅ Met |
| 134       | polyglot runner + evidence pre-QA                                       | ✅ Met |
| 135       | 3-tier router + stack propagation                                       | ✅ Met |
| 136       | structured prompts + tokens + isolation + semaphore                     | ✅ Met |
| 137       | smoke suite happy + failure paths                                       | ✅ Met |
| 138       | contract rules → downstream backlog                                     | ✅ Met |
| 139       | DTO ban + sentinel fail-fast                                            | ✅ Met |
| 140       | spec gate blocks unspecified arch                                       | ✅ Met |
| 141       | blast matrix + verifier scoping                                         | ✅ Met |
| 142       | Phase B 14-test certification                                           | ✅ Met |
| 149       | 5 hotfixes one diff, one QA gate                                        | ✅ Met |
| 151       | decision pipeline verified/fixed                                        | ✅ Met |
| 152       | self-improve trigger + suggestions                                      | ✅ Met |
| 153       | audit scopes to caller project only                                     | ✅ Met |
| 154       | atomic qa_transition tool                                               | ✅ Met |
| 155       | pure MCP, scripts retired                                               | ✅ Met |
| 156       | coach alignment + prompts standardized                                  | ✅ Met |
| 157       | v9.8.0 push script + global sync                                        | ✅ Met |
| 158       | decision remnants purged, audit hardened                                | ✅ Met |
| 159       | v9.9.0 published + global synced                                        | ✅ Met |
| 160       | 55 passed, servers verified                                             | ✅ Met |
| 161       | 309 passed, healthcheck dry-run 0                                       | ✅ Met |
| HOTFIX-01 | thread-safe SQLite + boot re-trigger                                    | ✅ Met |

## Individual Task Summaries

### Task 125: Remove opentmux and opencode-agent-tmux — Keep tmux

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Strip npm globals + docs/config references to opentmux/agent-tmux; verify system tmux intact.

### Task 126: Migrate Goal Plugin to @prevalentware/opencode-goal-plugin

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Migrate opencode.json + tui.json + docs + memories + loop-engine refs from willytop8 to prevalentware v0.1.39; verify plugin parity.

### Task 127: Auto-Generate Memory Index via MCP Memory Server and Integrate into Agents

- **Type:** improvement
- **Source:** telegram
- **Reasoning:** MCP server rebuilds `.opencode/memory/index.md` atomically after every mutation; executor + prompt read index first, selective fetch.

### Task 128: Fix Telegram Topic Filter Leak and Allowed Root Auto-Mkdir

- **Type:** bug
- **Source:** manager
- **Reasoning:** HQ skill client-side reply_to filtering; upstream auto-mkdir allowed roots + topic_id on get_history; fork tracks chigwell + patches.

### Task 129: Orchestrator-Driven Manager Decision Detection for Coach Review

- **Type:** improvement
- **Source:** telegram
- **Reasoning:** Orchestrator/executor detect goals/decisions from context into task files for weekly/monthly coach handoff.

### Task 130: Fix Task ID Discovery Hallucination

- **Type:** bug
- **Source:** orchestrator
- **Reasoning:** Removed truncated inline discovery; task-generator skill is single source of truth for NEXT_ID.

### Task 131: Prevent Recurring Task-File Review Findings

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Harden lifecycle: AC/DoD boxes checked at implementation summary_phase, closing-tag normalization in build pipeline.

### Task 132: Loop Engine Critical Bug Verification and Fix

- **Type:** bug
- **Source:** orchestrator
- **Reasoning:** LE-0.1 plan-threading, LE-0.2 clean diff for QA, LE-0.3 scoped fix loop, LE-0.4 router memory gap — CONFIRMED/REFUTED before patch.

### Task 133: Stack Profile Engine and Schema

- **Type:** feature
- **Source:** orchestrator
- **Reasoning:** YAML stack profiles, explicit-header → markers/extensions → keywords → generic detection, preflight validation, daemon integration.

### Task 134: Polyglot Verification and Multi-Toolchain Runner

- **Type:** feature
- **Source:** orchestrator
- **Reasoning:** Deterministic per-stack lint/build/test, timeouts, fail-fast in daemon, evidence before LLM QA.

### Task 135: Stack-Aware LLM Router & Provider Model Mapping

- **Type:** feature
- **Source:** orchestrator
- **Reasoning:** 3-tier hierarchy (stack-preferred → category → default), stack propagation through plan/QA/review, model_preferences population.

### Task 136: OpenCode Executor Stack Context Injection & Goal Plugin Guardrails

- **Type:** feature
- **Source:** orchestrator
- **Reasoning:** Structured prompt building, termination token extraction, process-group isolation, concurrency semaphore, expanded executor tests.

### Task 137: End-to-End Polyglot Smoke Test Suite & Hard Verification Gate

- **Type:** feature
- **Source:** orchestrator
- **Reasoning:** test_polyglot_smoke.py drives real pipeline components in temp workspace, happy-path to CLOSED + failure containment.

### Task 138: Contract Propagation & Downstream Task Dispatcher

- **Type:** feature
- **Source:** orchestrator
- **Reasoning:** LE-6 contracts.py extracts diff paths, matches contract globs, dispatches downstream backlog tasks with Triggered-By + sequential IDs.

### Task 139: No-Manual-DTO Mandate & Type Drift Sentinel

- **Type:** feature
- **Source:** orchestrator
- **Reasoning:** Fragment 20 bans hand DTOs when contract governs; sentinel.py fails fast on consumer drift (drift-ignore escape hatch).

### Task 140: Spec-First Artifact Pipeline & State Gate

- **Type:** feature
- **Source:** orchestrator
- **Reasoning:** LE-8 requires ADR/PRD/Contract/DataModel for arch/API/schema changes; state gate blocks unspecified work.

### Task 141: Monorepo Blast-Radius Analyzer & Affected Path Matrix

- **Type:** feature
- **Source:** orchestrator
- **Reasoning:** blast_radius.py longest-prefix ownership, reverse-dep closure, affected matrix, toolchain skip scoping.

### Task 142: End-to-End Contract Propagation Smoke Test Suite & Hard Gate

- **Type:** feature
- **Source:** orchestrator
- **Reasoning:** test_contract_smoke.py 14 tests certify propagation, sentinel block, spec gate, blast scoping in full daemon lifecycles.

### Task 149: Hotfix Bundle — Telegram Gateway, Telemetry, Path Resolution, Reasoning Guard & Concurrency

- **Type:** feature
- **Source:** manager
- **Reasoning:** META bundling HOTFIX-02–06: gateway retry, telemetry content_len, Kanban path resolution, reasoning fallbacks, concurrency locks — one diff, one QA gate.

### Task 151: Audit Manager Decision Logging Accuracy

- **Type:** improvement
- **Source:** telegram
- **Reasoning:** Verified decision storage gaps; fixed detection pipeline (later superseded by Task 151 removal in 9.4.0 — history preserved).

### Task 152: Self-Improvement System-Prompt & Workflow Retrofit

- **Type:** improvement
- **Source:** telegram
- **Reasoning:** Added fragment 21 self-improvement protocol (/reflect) synthesizing session friction into backlog upgrades.

### Task 153: Fix audit-agents Skill Scope Leak Across Projects

- **Type:** bug
- **Source:** telegram
- **Reasoning:** Audit now scopes to caller project; HQ-only fragment system + executor stays in AGENTS.md, template stays agnostic.

### Task 154: Atomic QA Transition & Staging Tooling

- **Type:** improvement
- **Source:** manager
- **Reasoning:** custom_context_qa_transition MCP tool unifies git mv + File header sync + diff injection atomically.

### Task 155: Pure MCP Tooling & Script Removal

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Inlined bundling engine into mcp-context-server, retired scripts/bundle-tasks.py + qa-transition.py, pure-MCP protocols.

### Task 156: Coach Prompt Alignment, User Prompts Refactor & Manual Mode Optimizations

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Retargeted coach audit off Manager Decisions, standardized 10 user-prompts wrappers, README pure-MCP rewrite, manual-mode 6-step.

### Task 157: Release v9.8.0 — Global Upgrade and Push Script

- **Type:** feature
- **Source:** manager
- **Reasoning:** Bumped 9.7.0→9.8.0, reassembled 75689-byte prompt, push-script generator, global drift audit/copy/re-verify/smoke, release-workflow memory mandate.

### Task 158: Purge Deprecated Manager Decision and Harden Audit Agent

- **Type:** bug
- **Source:** telegram
- **Reasoning:** Purged Manager/Admin Decision remnants, added deprecated-section purge rule, README SEO overhaul, backlog orphan purge, synced audit-agents globally.

### Task 159: Release v9.9.0 publication and global install upgrade

- **Type:** feature
- **Source:** manager
- **Reasoning:** Published v9.9.0 (push script manual step), zero bump release, global install synced byte-identical + plugin parity verified.

### Task 160: Fix stale test suite (bundle-test import + splitter round-trip)

- **Type:** bug
- **Source:** manager
- **Reasoning:** Promoted bundle helpers to module level, retargeted tests from retired script, fixed splitter TOP_LEVEL_TAGS; 55 passed. system-prompt.md version unchanged.

### Task 161: production-readiness-bundle

- **Type:** feature
- **Source:** manager
- **Reasoning:** META 143–148: multi-project routing, gateway resilience, metrics/Sentry, ReleaseEngine, Docker/Compose/systemd, vertical-slice certification; 309 passed, healthcheck dry-run 0.

### Task HOTFIX-01: SQLite Thread-Affinity & Boot-Scan Pending Re-Trigger Fix

- **Type:** improvement
- **Source:** orchestrator
- **Reasoning:** check_same_thread=False for watchdog threads, boot_scan re-sends PENDING_TRIGGER cards across restarts, poller starts before boot cards.
