# Milestone 10 Summary

**Date:** 2026-08-11
**Tasks Compacted:** 13

## Source Distribution

| Source       | Count |
| ------------ | ----- |
| manager      | 10    |
| orchestrator | 1     |
| telegram     | 1     |
| research     | 1     |

## Architectural Changes

Milestone 10 covers three waves of work following the v8.3.0 release:

1. **Cognitive Executor Agent platform (Tasks 82–84):** Created and globally installed the `cognitive-executor` primary agent plus the read-only `cognitive-discovery` subagent, with ZAC (zero autonomous commits) hard-enforced at the permission layer (`git add`/`git commit`/`git push` → deny). Full bash autonomy (`"*": "allow"`) with only `rm -rf` → ask and git denies retained. Added the Skill Auto-Loading Matrix, Direct Input (Ad-Hoc) Validation Protocol, Context Bootstrapping & Memory Protocol, and Subagent Delegation sections to the executor prompt. Released as **v8.3.0**.

2. **MCP server hardening wave (Tasks 85, 90, 91, 92):** Added the `create_tree_report` MCP tool (`.gitignore`-aware tree persistence twin of `get_directory_tree`), fixed path traversal + TOCTOU race conditions in both report-producing tools (UUID-suffix filenames), replaced blind `git add -A .` staging with explicit `modified_files` path scoping (F5 fix — the exact line that re-swept foreign task files 86/87/88 into Task 89's closure commit), and scoped `lint_all_tasks` to exclude `tasks/archive/` by default (`include_archive` flag), turning the health gate from 388 issues of noise into "11 active files, 0 issues".

3. **Governance & workflow sync wave (Tasks 86–89, 93–94):** Vendored the MIT `opencode-shell-strategy` instructions with an explicit ZAC Overrides section; created the full-workflow audit record (Task 87, findings F1–F8); activated Telegram as a persistent task-input source ("Cognitive Hq" topic, `telegram-sync.json` state file); fixed the task-generator template lint contract (F2 — lint sections now unconditional outside the variant switch) and added the Absent-File Policy (F1 — SKIP gracefully, DO NOT HALT/HALLUCINATE); installed the mandatory `tasks/qa/` lifecycle transition in the executor agent and audit skill (F7d); synced `audit-agents` with the F7 standards so AGENTS.md → executor agent → audit skill all enforce identical git-mv-exception + qa-transition semantics.

Versions released during this milestone window: 8.3.0 → 8.4.0 → 8.4.1 → 8.4.2 → 8.4.3.

## Files Modified

| File                                                     | Change                                                                                                                                             |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `agents/cognitive-executor.md`                           | New primary agent (permission layer ZAC, bash autonomy, protocol body); QA transition rule added (F7d)                                             |
| `agents/cognitive-discovery.md`                          | New read-only subagent for custom_context MCP-based context compilation                                                                            |
| `~/.config/opencode/agents/` (global)                    | Executor + discovery agent deployments synced                                                                                                      |
| `~/.config/opencode/opencode.jsonc`                      | `default_agent: cognitive-executor`                                                                                                                |
| `opencode.json` (repo)                                   | `instructions` for shell strategy; `default_agent` key (F7b)                                                                                       |
| `LLM.txt`                                                | Section 6.5 agent install, shell-strategy copy step, `instructions` in global config template                                                      |
| `mcp-context-server/server.py`                           | `create_tree_report` tool; `modified_files` staging contract (F5); UUID-suffix in `read_source_files` (F4); path traversal guard                   |
| `mcp-lint-server/server.py`                              | `lint_all_tasks(include_archive=False)` scoping (F3)                                                                                               |
| `tests/test_mcp_servers.py`                              | 6+ new regression tests (tree report, traversal, None input, collision, F5 staging)                                                                |
| `system-prompt.md`                                       | v8.4.0–8.4.3: tree-report step in discovery templates, Absent-File Policy in 3 validation phases, `modified_files` contract, `@scout` → `@general` |
| `AGENTS.md`                                              | Absent-File Policy, `git mv` Kanban exception (F7c), `modified_files` in end-of-task sequence                                                      |
| `skill-templates/task-generator/SKILL.md`                | Lint sections moved outside variant switch (F2)                                                                                                    |
| `skill-templates/audit-agents/SKILL.md`                  | MCP report generation criteria, `modified_files` audit criterion, F7 sync (git mv + qa transition)                                                 |
| `skill-templates/code-search/SKILL.md`                   | Tree report step 1.5                                                                                                                               |
| `docs/opencode-shell-strategy.md`                        | Vendored MIT shell strategy + ZAC Overrides                                                                                                        |
| `~/.config/opencode/opencode-shell-strategy.md` (global) | Vendored copy                                                                                                                                      |
| `README.md`                                              | Custom agents section, tree report docs, V8 label + tree sync (F7a)                                                                                |
| `telegram-sync.json`                                     | New Telegram sync state (chat -1003993323129, topic 425)                                                                                           |
| `CHANGELOG.md`                                           | 8.3.0, Unreleased→Added/Changed/Fixed entries for all tasks                                                                                        |
| `docs/history/milestone-10-summary.md`                   | This file                                                                                                                                          |

**Note:** `git mv` of task files between `tasks/backlog/` → `tasks/in-progress/` → `tasks/qa/` → `tasks/completed/` occurred throughout; see the task files for their individual closure commit hashes.

## Criteria Met

| Task | Acceptance Criteria                                                                                                                       | Status                                             |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| 82   | Global executor + discovery agents with ZAC deny rules; `default_agent` configured; LLM.txt bootstrap step                                | ✅ Met                                             |
| 83   | Bash `"*": "allow"` with `rm -rf` ask and git add/commit/push deny; global sync; all 5 appended protocol sections                         | ✅ Met                                             |
| 84   | `<system_version>8.3.0`; CHANGELOG 8.3.0 header; release commit (`ee5e9d7`); tag/release pending Manager                                  | ✅ Met (partial: tag/GH release Manager-owned)     |
| 85   | `create_tree_report` tool with `.gitignore` awareness, collision-free naming, path traversal + None input guards; 14 tests pass           | ✅ Met                                             |
| 86   | Vendored shell strategy with MIT attribution; reconciliation documented; `instructions` wired in repo + global + LLM.txt                  | ✅ Met                                             |
| 87   | Single documentation task file; every finding (F1–F8) with What/Where/Evidence/Impact/Fix; no implementation                              | ✅ Met                                             |
| 88   | Task file with `Source: telegram` + verbatim Persian message; `telegram-sync.json` with chat/topic/state; topic-name discrepancy surfaced | ✅ Met                                             |
| 89   | 4 lint sections unconditional in task-generator template; Absent-File Policy in AGENTS.md + 3 validation phases; v8.4.1                   | ✅ Met                                             |
| 90   | `modified_files` path-scoped staging; no `git add -A` in server.py; v8.4.2; 14 tests pass                                                 | ✅ Met                                             |
| 91   | UUID suffix in `read_source_files`; `@scout` gone; v8.4.3; 14 tests pass                                                                  | ✅ Met                                             |
| 92   | 6 zombie tasks archived; `lint_all_tasks` excludes archive by default; backlog = 3 files                                                  | ✅ Met                                             |
| 93   | README V8 label + tree; `default_agent` in repo config; AGENTS.md git mv exception; executor qa transition                                | ✅ Met                                             |
| 94   | audit-agents F7 sync: git mv exception + qa transition in Mode 1 + criteria; global byte-identical                                        | ✅ Met (grep counts superset: 3/4 vs expected 2/2) |

## Individual Task Summaries

### Task 82: Implement Cognitive Executor Agent

- **Type:** feature
- **Source:** manager
- **Reasoning:** Created global `cognitive-executor` (primary, `mode: primary`, `temperature: 0.1`, ZAC denies at the permission layer — `git add*`/`git commit*`/`git push*` → deny, bash catch-all `"*": "ask"`) and `cognitive-discovery` (read-only subagent, edit/bash deny). Added `"default_agent": "cognitive-executor"` to `~/.config/opencode/opencode.jsonc`, LLM.txt Section 6.5 global-install bootstrap, README section. Kernels: permission-layer enforcement beats prompt compliance (prior ZAC violations in tasks 16/78 were prompt-level); enforcement is structural, not prose.

### Task 83: Update Cognitive Executor Bash Autonomy

- **Type:** improvement
- **Source:** orchestrator
- **Reasoning:** Replaced granular bash allowlist with `"*": "allow"` catch-all while preserving ZAC denies and `rm -rf` → ask (last-matching-rule-wins: denies listed after the catch-all). Five follow-up iterations appended: Task Lifecycle & Kanban State Enforcement, Skill Auto-Loading Matrix, Direct Input Validation Protocol, Context Bootstrapping & Memory Protocol, Subagent Delegation — plus a duplicate `DO SAVE` line fix. Makes the executor deterministic against Orchestrator omissions.

### Task 84: Release v8.3.0 - Cognitive Executor Agents

- **Type:** feature
- **Source:** manager
- **Reasoning:** Cut release v8.3.0 (MINOR — new agent features): `<system_version>` 8.2.0 → 8.3.0, `[Unreleased]` → `## [8.3.0] - 2026-08-08` with Added + Changed entries, commit via MCP lifecycle (`ee5e9d7` release + `51663cd` close). Tag `v8.3.0` + `gh release create` remain Manager-owned (ZAC denies them for the agent) — the intended division of power: agent cannot forge history, human owns the remote.

### Task 85: Add Tree Report MCP Tool

- **Type:** feature
- **Source:** manager
- **Reasoning:** Added `create_tree_report(target_path=".")` to `mcp-context-server/server.py` — persistence twin of `get_directory_tree` reusing `GitIgnoreFilter` + `generate_tree`; shared `_ensure_context_reports_ignored()` safeguard; UUID-suffix naming. QA iterations closed 3 adversarial findings: path traversal (resolve + `relative_to` workspace check), TOCTOU (UUID by construction, no exists()/open() race), None input coercion. Synced 8+ doc artifacts + bumped 8.3.0 → 8.4.0.

### Task 86: Vendor OpenCode Shell Strategy Instructions

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Vendored MIT `shell_strategy.md` → `docs/opencode-shell-strategy.md` with attribution header + `## Cognitive Lead AI HQ Overrides` section (upstream presents `git commit -m` as GOOD — reconciled: ZAC bans it here; all commit/add/push exclusively via MCP tools). Wired `instructions` into repo `opencode.json`, global config, and LLM.txt (copy step + Step-7 template). Local > remote keeps the platform self-contained/offline.

### Task 87: Workflow Audit Findings — Documentation

- **Type:** research
- **Source:** manager
- **Reasoning:** Canonical documentation-only record of the 2026-08-10 full-workflow audit. Findings F1–F8: F1 unsatisfiable first-read mandate (absent files), F2 template/lint contract mismatch, F3 lint archive noise wall, F4 TOCTOU in `read_source_files`, F5 cross-session contamination via `git add -A`, F6 dead `@scout` ref, F7 doc drift (README/opencode.json/AGENTS.md/executor), F8 future CI zombie gate. Empirical gates: pytest 14 passed, `lint_all_tasks` 388 issues/87 files. Live evidence: parallel session created task 86 mid-audit (F5 proof).

### Task 88: Enable Telegram Task Input Source — Cognitive Hq Topic Sync Setup

- **Type:** feature
- **Source:** telegram
- **Reasoning:** Wired the `telegram-issue-sync` workflow to the "Cognitive Hq" topic (id 425, chat `-1003993323129`) and created `telegram-sync.json` (last_processed_message_id 426, processed_ids [425,426], sync_registry mapping 426 → this task). Preserved the Manager's Persian message verbatim. Surfaces the "Cognitive Edge" vs actual "Cognitive Hq" topic-name discrepancy as a grounding decision — never silently correct user intent; state file binds to the objectively retrieved topic id.

### Task 89: Fix Template Lint Contract and Add Absent-File Policy

- **Type:** bug
- **Source:** manager
- **Reasoning:** F2 fix: moved the 4 lint-required sections outside the source-variant switch in `skill-templates/task-generator/SKILL.md` (DRY — one copy, always emitted, guarded by an anti-regression marker comment); global copy byte-identical. F1 fix: Absent-File Policy (SKIP gracefully — DO NOT HALT, DO NOT HALLUCINATE) added to AGENTS.md + all 3 `<validation_phase>` blocks; bumped 8.4.0 → 8.4.1 PATCH; stored `project/absent-file-policy` memory.

### Task 90: Fix MCP Staging and ZAC Sync

- **Type:** security
- **Source:** manager
- **Reasoning:** F5 fix: `stage_and_inject_diff` gained `modified_files` list — stages ONLY declared files + task file (no `git add -A .` + reset loop). `commit_and_clean_task` stages ONLY the task file (the exact `git add -A tasks/` line that re-swept 86/87/88 into Task 89's closure commit). Trust model inverted: git-wide staging trusted the environment; path-scoped staging trusts the executor's self-reporting, which the Brain's review loop verifies. Default `= []` keeps trivial tasks functional; empty diff table is visible failure, not silent contamination. Bumped 8.4.1 → 8.4.2.

### Task 91: Fix TOCTOU and Dead Scout Ref

- **Type:** bug
- **Source:** manager
- **Reasoning:** F4 fix: `read_source_files` report filenames gained the UUID-suffix pattern (`context_report_<timestamp>_<uuid8>.md`) — closing the half-applied fix from Task 85 (same-second overwrite was equally real for context reports). F6 fix: dead `@scout` subagent reference in the implementation template `<context_phase>` (never registered — only `cognitive-discovery`/`explore`/`general` exist) replaced with `@general`. Bumped 8.4.2 → 8.4.3; global system-prompt re-synced.

### Task 92: Archive Zombies and Scope Lint

- **Type:** chore
- **Source:** manager
- **Reasoning:** F3 fix in two parts: (1) archived 6 zombie tasks (10, 11, 12, 13, 25, 30 — completed but never closed, verified via Execution Logs + merged changes) via `git mv`; (2) `lint_all_tasks(include_archive=False)` scoped to active dirs only — the archive is a historical record, not a health signal; the gate became "11 active files, 0 issues" vs the old 388-noise wall. Zombie root cause: tasks predating the enforced closure loop (Task 26/45). Flagged (no bump instructed): MCP server change without system-prompt version bump.

### Task 93: Fix Document Drift and Inconsistencies

- **Type:** docs
- **Source:** manager
- **Reasoning:** All four F7 findings: F7a README structure tree + V8 label sync; F7b `"default_agent": "cognitive-executor"` added to repo `opencode.json` (documented deviation — Orchestrator said `"agent"`, authoritative vendored config docs + working global config use `default_agent`; `"agent"` would be a no-op and not close F7b); F7c `git mv` Kanban exception in AGENTS.md guardrail; F7d mandatory `tasks/qa/` transition in the executor agent (first live application: task 93 itself transited qa/). Known lint false positive: naive fence counter mis-toggles on diff-content ``` lines — flagged for a fence-aware follow-up.

### Task 94: Sync Audit-Agents with F7 Standards

- **Type:** chore
- **Source:** manager
- **Reasoning:** Propagated the F7 standards (git mv exception + qa transition) into `skill-templates/audit-agents/SKILL.md` Mode 1 template + both criteria lists (top summary + Mode 2, via replaceAll to keep identical bullets in sync). Grep counts are supersets (3/4 vs expected 2/2) by deliberate consistency extension — the required targets are all updated. With this task, AGENTS.md → executor agent → audit skill enforce IDENTICAL semantics, closing the "rules in one place only" drift pattern (F7). Global copy byte-identical.
