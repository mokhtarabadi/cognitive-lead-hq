# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- **Workflow governance improvements (Task 97)** — `task-generator` SKILL.md now includes a **Duplicate ID Check** (`find ... | sort | uniq -d`) plus a **`## Definition of Done`** block (Build/Test/Lint exit 0, `lint_task_file` passes, CHANGELOG Parse-Then-Append, verification-before-completion evidence) in both single-phase and multi-phase templates; the lint MCP server gained a **path-drift guard** (`_check_task_file_structure` now flags `**File:**` headers that mismatch the actual file path, with a new fail-first `test_lint_task_file_path_mismatch`); `system-prompt.md` (v8.4.4) gained a **non-blocking distribution/growth signal** in the Orchestrator workflow (reminder + 2-3 suggestions when the last 5 closed tasks have no business/marketing/growth/analytics classification; auto-creation FORBIDDEN); and `telegram-issue-sync` SKILL.md now mandates mirroring `task-generator` exactly (same ID discovery, duplicate-title/ID/collision checks, canonical template, and Definition of Done).

- **Partial Freebuff Support documentation (Task 96)** — New `docs/freebuff-support.md` documenting the 2026-08-12 port of Cognitive Lead AI HQ components to the Freebuff runtime (vendor: manicode, formerly Codebuff-based): what Freebuff is, its extension points (`.agents/mcp.json`, `.agents/skills/<name>/SKILL.md`, `.agents/*.ts` custom `AgentDefinition` agents) as discovered via binary analysis, the full port record (3 MCP servers + 29 skills + 2 custom agent `.ts` ports under `~/.agents/`), verification commands, the partial-support matrix, and the free-tier limitation (`HTTP 403 free_mode_invalid_agent_model`). `README.md` gained a "Partial Freebuff Support (Experimental)" section with the port matrix and link to the docs; `LLM.txt` gained an optional Step 7.5 that installs the MCP servers + 29 skills globally under `~/.agents/`. The primary runtime and `system-prompt.md` are **unchanged** — OpenCode remains the task-generation target; Freebuff support is intentionally partial and documented as such. Verified: `lint_task_file` ✅, `lint_markdown` ✅, prettier ✅, grep gates ✅.

## [8.4.3] - 2026-08-11

### Added

- **Tree Report MCP Tool (8.4.0)** — New `create_tree_report` tool on the `custom_context` server: saves a `.gitignore`-aware directory tree of any path (default: the entire project) as `context-reports/tree_report_<timestamp>_<uuid>.md`, mirroring the `context_report_<timestamp>.md` naming convention (with a UUID suffix to guarantee collision-free naming). Trigger phrase: "create a tree of the project". Wired into the discovery/combined task templates in `system-prompt.md` (version bumped 8.3.0 → 8.4.0, MINOR), the `code-search` skill, the `cognitive-executor` and `cognitive-discovery` agents, `README.md`, and the `AGENTS.md` context-reports guardrail. The `audit-agents` skill gained an **MCP Report Generation** audit criterion (top summary + Mode 2 lists) and the matching guardrail pair in its Mode 1 `AGENTS.md` template; deployed global skill copies (`code-search`, `audit-agents`) synced from `skill-templates/`. Regression tests added for explicit-path, default-target, invalid-path, `.gitignore` filtering, same-second collision, path-traversal rejection, and `None` input handling.

### Changed

- **Milestone 10 archive and release v8.4.3** — All 13 completed tasks (82–94) compacted into `docs/history/milestone-10-summary.md` and moved to `tasks/archive/` via `git mv`; the accumulated unreleased work since v8.3.0 (cognitive executor agents and discovery subagent, tree report MCP tool, F1–F7 workflow fixes, shell-strategy vendoring, Telegram task input source, archive-scoped linting, mandatory `tasks/qa/` transition) is released as **v8.4.3**. `[Unreleased]` consolidated under this header; `<system_version>` stays 8.4.3 (already bumped by Task 91).
- **External directory permission: `/tmp` allowed for agents** — `external_directory` set to `{"*": "ask", "/tmp/**": "allow"}` (last-match-wins; only `/tmp/**` auto-approved, everything else still prompts) in `agents/cognitive-executor.md`, `agents/cognitive-discovery.md`, project `opencode.json`, global `~/.config/opencode/opencode.json`, and the `LLM.txt` Step-7 global config template. Shape verified against the authoritative `https://opencode.ai/config.json` schema (`PermissionRuleConfig` = action enum or `{pattern → action}` object).
- **Archived 6 completed zombie tasks (10, 11, 12, 13, 25, 30) from backlog to archive (F3)** — fully completed work items that were never closed (all Local TODOs checked, Execution Logs written, changes confirmed merged in the codebase) now live in `tasks/archive/`; `tasks/backlog/` reduced to the 3 active items (86, 87, 88).
- **`lint_all_tasks` now excludes the `tasks/archive/` directory by default to reduce noise (F3)** — the whole-repo health gate previously reported 388 issues across 87 files (mostly historical-format archived tasks), which agents learned to ignore. New optional `include_archive=True` flag restores explicit historical linting.
- **Synced `audit-agents` skill with F7 standards: AGENTS.md template and audit criteria now enforce the `git mv` Kanban exception and the mandatory `tasks/qa/` transition** — Mode 1's Git Guardrail and End-Of-Task Sequence (step 3 = stage_and_inject_diff → `git mv` to `tasks/qa/` → notify) mirror the live executor protocol from Task 93; the Target Audit Criteria (both the top summary and Mode 2 lists) carry matching `git mv` exception and QA-transition wording; global copy at `~/.config/opencode/skills/audit-agents/` re-synced byte-identical.
- **Vendored MIT-licensed `opencode-shell-strategy.md` into `docs/`; wired into repo, global, and LLM.txt configs** — the upstream non-interactive shell policy (JRedeker/opencode-shell-strategy) is now a local `instructions` file with a MIT attribution header and a **Cognitive Lead AI HQ Overrides** section that reconciles the Git reference table with ZAC: `git add`/`git commit`/`git push` remain banned regardless of non-interactive flags (MCP tools only), `git mv` limited to Kanban moves. Wired via `instructions` key in repo `opencode.json`, global `~/.config/opencode/opencode.json` (absolute path), and the `LLM.txt` Step-7 template + a new copy step and checklist item.

### Fixed

- **MCP `read_source_files` now uses UUID suffix for context reports to prevent same-second TOCTOU overwrites (F4)** — `context_report_<timestamp>_<uuid8>.md` replaces `context_report_<timestamp>.md`, mirroring the `create_tree_report` pattern from Task 85 that was never ported back.
- **Removed dead `@scout` subagent reference from system-prompt implementation template; replaced with `@general` (F6)** — no `scout` agent exists in the platform (only `cognitive-discovery`, `explore`, `general`); the dead reference could error or be silently substituted. System prompt version bumped 8.4.2 → 8.4.3 (PATCH).
- **Security hardening of `create_tree_report` (QA iteration)** — (1) Path traversal prevention: `target_path` is resolved against the workspace root and rejected with `"Error: Path traversal detected. target_path must be within the project workspace."` when it escapes the project. (2) TOCTOU race condition: the `while report_file.exists():` numeric-suffix check loop was replaced with a UUID suffix (`uuid4().hex[:8]`) so filenames are unique by construction. (3) `None`/invalid `target_path` types now degrade gracefully to the whole-project default instead of raising `TypeError`. Regression tests: `test_create_tree_report_rejects_path_traversal`, `test_create_tree_report_handles_none_input`. Filename pattern documented in README, system-prompt templates, agents, and the code-search skill updated to `tree_report_<timestamp>_<uuid>.md`.
- **Resolved F7 document drift: README tree updated with missing directories (agents, mcp-lint-server, mcp-memory-server, tests) and V8 label. Added `default_agent: cognitive-executor` to repo `opencode.json`. Clarified `git mv` exception in `AGENTS.md` (Kanban moves only). Enforced `tasks/qa/` transition in `cognitive-executor.md`** — README's stale "V7 Multi-Agent System Prompt" label corrected to V8 and the structure tree now lists the custom agents directory, both additional MCP servers, and the test suite; the repo config now carries the same `default_agent` that the working global config uses (the CHANGELOG 8.3.0 claim that F7b flagged as unfulfilled is now true; the key is `default_agent` per the vendored opencode config docs — not `agent`); the AGENTS.md guardrail now states the autonomous `git mv` exception for Kanban file moves; the cognitive-executor agent now MUST move completed implementations to `tasks/qa/` before the summary message, making the previously-dead QA state a real lifecycle transition.
- **Task 88 closure: removed stale Cando reference from memory workflow and ensured telegram-sync.json is tracked** — cleaned up `.opencode/memory/workflows/telegram-file-delivery.md` by deleting the obsolete Cando topic entry; confirmed `telegram-sync.json` is not gitignored and staged it for tracking; moved task 88 to `tasks/completed/` and updated status to closed.

## [8.4.2] - 2026-08-10

### Fixed

- **MCP `stage_and_inject_diff` now requires explicit `modified_files` list (F5 Fix - prevents cross-session contamination)** — blind `git add -A .` staging (plus the sensitive-file reset loop) replaced with explicit path scoping: only the files OpenCode lists plus the active task file are staged. `commit_and_clean_task` stages only the active task file (`git add -- <task_file>` instead of `git add -A tasks/`), closing the proven contamination hole that swept tasks 86/87/88 into Task 89's closure commit. System prompt and AGENTS.md updated to enforce ZAC compliance: all 3 task templates' summary-phase instructions (implementation + combined; discovery does not stage) now carry the `modified_files` contract with a CRITICAL REMINDER, and `audit-agents` gained an Explicit Staging Contract audit criterion. System prompt version bumped 8.4.1 → 8.4.2 (PATCH).

## [8.4.1] - 2026-08-10

### Fixed

- **Task-generator template now includes all lint-required sections (Local TODOs, Acceptance Criteria, Verification Evidence, Risk & Rollback) unconditionally for all source variants (F2)** — the 4 sections were moved OUT of the polymorphic variant switch (previously only Variant C carried them, so orchestrator- and telegram-sourced tasks failed `lint_task_file` at creation). A marker comment now guards the unconditional block: `<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->`. Global copy `~/.config/opencode/skills/task-generator/SKILL.md` re-synced from `skill-templates/` (byte-identical).
- **Added absent-file policy to AGENTS.md and all 3 validation phases in system-prompt.md — agents now gracefully skip missing core docs instead of halting or hallucinating (F1)** — `DESIGN.md`, `docs/architecture.md`, and `docs/data_model.md` are referenced as mandatory first-reads but do not exist in this repository; the new policy instructs agents to SKIP absent referenced files with an explicit internal note (DO NOT HALT, DO NOT HALLUCINATE). System prompt version bumped 8.4.0 → 8.4.1 (PATCH).

## [8.3.0] - 2026-08-08

### Added

- Implemented global `cognitive-executor` and `cognitive-discovery` OpenCode agents to hard-enforce ZAC and workflow protocols at the permission layer.

### Changed

- **Cognitive Executor Agent Hardened (8.3.0)** — The `cognitive-executor` primary agent now carries the full execution protocol as its permanent system prompt: bash full-autonomy with ZAC denies (`git add`/`git commit`/`git push` → `deny`) and `rm -rf` guard, Task Lifecycle & Kanban State Enforcement (self-correcting `backlog → in-progress` and closure moves), Skill Auto-Loading Matrix (14 stack/workflow mappings), Direct Input (Ad-Hoc) Validation Protocol, Context Bootstrapping & Memory Protocol, and Subagent Delegation for Context Discovery via `cognitive-discovery`. `LLM.txt` bootstrap extended with Section 6.5 (global agent install) and `default_agent` in the Section 7 config JSON; `README.md` documents the custom agents. `opencode.json` and `opencode.jsonc` set `default_agent: cognitive-executor`. System prompt version bumped to 8.3.0 (MINOR).

## [8.2.0] - 2026-08-06

### Added

- **Sprint Strategist Persona (8.1.2)** — New persona that acts as the strategic sprint gatekeeper. Evaluates every backlog task against the 9-question decision framework, operating principles, and documented cognitive biases. Has explicit authority to challenge the Manager's excitement-driven overcommitment and output a MoSCoW-ranked sprint plan with WIP limits. Wires the Founder OS rules into active sprint planning enforcement.

### Changed

- **Founder OS System-Level Rules Added (V8.1.1, Code Review iteration)** — Incorporated the Code Reviewer's Request-Changes feedback: added `<growth_model>` (Manager evolves through Solo Builder → Founder → Product Leader → Engineering Leader → CEO → Executive; coaching style must evolve with the stage), `<ai_objective>` (the AI maximizes the Manager's long-term company success — not agreement, code quality, or conversation quality), `<operating_principles>` (leverage over effort, systems over heroics, recurring revenue over one-time wins, optimization before exploration, evidence over intuition, reusable infrastructure, compounding assets, people over individual output), `<delegation_strategy>` (the default solution is never "the Manager writes more code" — improve systems/AI/workflows/delegation/documentation/hiring first), and `<challenge_policy>` (explicitly challenge excitement-driven decisions; recommend delay, evidence collection, or experiments; honest disagreement is encouraged). Added question 9 to `<decision_framework>`: "Does this create a compounding advantage? If not, the work is probably not worth doing." `<leadership_and_language_protocol>` item 0 now also references `<ai_objective>` and `<operating_principles>`. System prompt version bumped to 8.1.1 (PATCH).
- **Manager Prompt Refactored into a Founder Operating System (V8.1.0)** — Replaced the minimal `<manager_profile>` in `system-prompt.md` with a structured 13-section identity layer: `<identity>`, `<current_role>`, `<long_term_mission>`, `<entrepreneurial_history>`, `<technical_context>`, `<leadership_objectives>`, `<behavioral_patterns>`, `<cognitive_biases>`, `<decision_framework>`, `<product_philosophy>`, `<company_vision>`, `<ai_collaboration_philosophy>`, and `<coaching_preferences>`. The Manager is now modeled as an AI-native Founder (15+ years self-taught engineering, earliest unofficial Persian Telegram client, million-user products, both commercial success and financial failures) whose objective is building an AI-first software company — programming is one tool, not his identity. `<leadership_and_language_protocol>` upgraded: added Step 0 Founder-First Coaching Mode (evaluate every request against mission, decision framework, and company vision) and Step 4 Bias Defense (actively weigh the documented cognitive biases against the decision framework and surface conflicts), while preserving the existing Vocabulary & Keyword Assistant, English Language Corrections (`Coach's Note` with Persian phonetics), and Ruthless Soft-Skills Feedback (now judging founder skills: delegation, clarity of vision, team motivation). `<role>` and `<initialization>` now propagate the founder mission to every persona. README.md Manager Profile section and LLM.txt Section 9 synced. System prompt version bumped to 8.1.0 (MINOR).
- **Milestone 9 archive** — Compacted Tasks 80–81 into `docs/history/milestone-9-summary.md` and moved completed task files to `tasks/archive/`. System prompt version bumped to 8.2.0.

## [8.0.2] - 2026-08-04

### Changed

- **Commit Lifecycle Rule (ZAC) in system-prompt `<constraints>`** — Added a `<commit_lifecycle_rule>` bullet to the top-level `<constraints>` section documenting the two commit-producing MCP tools (`stage_and_inject_diff` for development-time, `commit_and_clean_task` for closure-time), their distinct lifecycle semantics, the two-commit flow (feature + closure), and ZAC enforcement. Previously the ZAC intent was only visible in `<bash_phase>` implementation templates, allowing LLM agents to invoke `commit_and_clean_task` during implementation (Zen Router incident, Task 13). System prompt version bumped to 8.0.1 (PATCH).
- **Milestone 8 archive** — Compacted Tasks 69, 77–79 into `docs/history/milestone-8-summary.md` and moved completed task files to `tasks/archive/`. System prompt version bumped to 8.0.2.

### Fixed

- **Orphaned commit hash bug in `commit_and_clean_task`** — The tool captured the commit hash _before_ `git commit --amend`, so the hash stored in the task file pointed to a commit that became unreachable after the amend replaced it. Reworked the tool to a two-commit flow: the feature commit hash is captured and stored in the task file, then the cleaned task file is committed as a separate `chore: close task N` closure commit. The stored hash is now permanently reachable from HEAD, `git show <hash>` returns the real code diff, and no amend/orphaned commits are produced. The idempotency guard matches the exact cleaned-block structure (regex), so a raw injected diff that merely mentions "Stored in Commit Hash" (e.g. this very changelog entry or the guard's own source line) cannot false-positive and block a legitimate closure. Regression tests: `test_commit_and_clean_task_stores_reachable_hash`, `test_commit_and_clean_task_guard_no_false_positive_on_diff_mention`.
- **`stage_and_inject_diff` crash when an ignored `context-reports/` directory exists** — the tool staged with `git add . :!...` negative pathspecs, which makes git exit 1 with "paths are ignored" whenever an excluded path actually exists on disk (the accumulated `context-reports/` reports), blocking every closure until deleted. Replaced with plain `git add -A .` (gitignore-respected) plus defense-in-depth `git reset -q -- <pattern>` for the sensitive/ignored paths. Regression test: `test_stage_and_inject_diff_with_ignored_context_reports`.

## [8.0.0] - 2026-08-04

### Added

- **P1 Quality Improvements (V8.0.0 Phase 5)** — Added `tests/test_mcp_servers.py` for basic MCP server import and logic validation. Enhanced `mcp-memory-server` with YAML frontmatter support (`pyyaml`) for metadata tracking and improved `search_memory` with tag filtering and ranking. Created `docs/system-prompt-modularization.md` design document for V9.0.0 planning. Documented tree-sitter regex fallback for Swift, Ruby, PHP, and C# in `code-search` skill. System prompt version bumped to 7.5.0.
- **New Lint MCP Server & Skill (V8.0.0 Phase 3)** — Created `mcp-lint-server/server.py` providing `lint_markdown`, `lint_task_file`, and `lint_all_tasks` tools for structural validation. Registered server in `opencode.json` and `LLM.txt` global configs. Created `task-lint` skill template. Added `task-lint` to `<agent_skills_registry>` in `system-prompt.md`. System prompt version bumped to 7.4.0.

### Changed

- **Milestone 7 archive** — Compacted tasks 70–76 into `docs/history/milestone-7-summary.md` and moved completed task files to `tasks/archive/`. System prompt version bumped to 8.0.0.
- **Task Template Ecosystem Enforcement (V8.0.0 Phase 4 Revised)** — Enforced new task template sections across the entire ecosystem. Updated `mcp-lint-server` to mandate `## Acceptance Criteria`, `## Verification Evidence`, and `## Risk & Rollback`. Instructed `telegram-issue-sync` to populate acceptance criteria from message intent. Enhanced `archive-tasks` milestone summaries to extract and report criteria met. Added `CRITICAL RULE 6 (Evidence Capture)` to `<bash_phase>` in `system-prompt.md` to force verification evidence logging before summary. System prompt version bumped to 7.4.2.
- **Task Template Enhancement & Lint Integration (V8.0.0 Phase 4)** — Enhanced `task-generator` skill template with mandatory `## Acceptance Criteria`, `## Verification Evidence`, and `## Risk & Rollback` sections for both unified and multi-phase task files. Integrated `lint_task_file` MCP tool into the `<summary_phase>` of both `<opencode_implementation_task_template>` and `<opencode_combined_task_template>` to enforce structural validation before diff injection. System prompt version bumped to 7.4.1.
- **Input Processing Pipeline Enhancement (V8.0.0 Phase 1)** — Enhanced `<user_input_processing>` in `system-prompt.md` with mandatory Input Validation Gate (Step 0.5), enriched Intent Expansion, and Prompt Refactor Gate (Step 5.5). Enhanced `prompt-refactor` skill with Step 0 validation and typo correction. Updated `AGENTS.md` guardrail to enforce Input Validation Pipeline. Created `user-prompts/input-validation-test.md`. System prompt version bumped to 7.3.0.

### Fixed

- **Fixed search_memory tag-only query edge case** — When querying with only `tag:xxx` (no additional search terms), the function now correctly returns all files matching the tag filter instead of returning zero results. Previously, the fallback content matching would search for the literal string "tag:xxx" in file content, which would never match.
- **P0 Consistency & Safety Fixes (V8.0.0 Phase 2)** — Resolved AGENTS.md documentation-only contradiction by adding explicit exceptions for MCP servers and tooling. Hardened `stage_and_inject_diff` to exclude sensitive files (`.env`, `.pem`, etc.) from blind `git add .`. Hardened `commit_and_clean_task` with empty-staged checks and push-history amend warnings. Fixed version sync rules in `versioning-and-release` skill. Resolved `DESIGN.md` path conflict (root vs `.stitch/`). Converted `archive-tasks` to use `git mv` for history preservation. Secured memory deletion by changing `delete_memory` permission to `ask` in `opencode.json` and `LLM.txt`, and adding a Safety Gate to the `project-memory` skill.
- **MCP servers crash on startup with MCP SDK 2.0** — Pinned `mcp[cli]>=1.0,<2.0` in the `# /// script` dependency headers of `mcp-context-server/server.py` and `mcp-memory-server/server.py`. PyPI's latest `mcp` (2.0.0) removed `mcp.server.fastmcp`, causing `ModuleNotFoundError` on boot and disabling both `custom_context` and `project_memory` tools.

## [7.2.2] - 2026-08-02

### Added

- **MIT License** — Added `LICENSE` file to project root. The repository previously had a README badge pointing to `LICENSE` but no actual file existed. MIT chosen as the best fit for a documentation-only, community-driven open-source framework repository.

## [7.2.1] - 2026-08-01

### Changed

- **Milestone 6 archive** — Compacted tasks 66–68 into `docs/history/milestone-6-summary.md` and moved completed task files to `tasks/archive/`. System prompt version bumped to 7.2.1.
- **OpenCode Config Enhancement:** Added `timeout: 15000` to MCP server configurations in `LLM.txt`, `README.md`, and `opencode.json` to prevent cold-boot timeouts with Python `uv` servers.
- **UX Fix:** `LLM.txt` now preserves `system-prompt.md` to `~/.config/opencode/` before cleaning up the temporary clone directory.

## [7.2.0] - 2026-08-01

### Added

- Unified canonical task file template with polymorphic `## Source Context` section supporting three provenances: `orchestrator`, `telegram`, `manager`.
- Mandatory `## Goal` and `## Local TODOs` sections for all task files regardless of source.
- `Source:` metadata field in task file header for provenance tracking.
- `Source Distribution` table in `archive-tasks` milestone summaries.

### Changed

- `task-generator` skill template updated to unified canonical format with `# Task [NN]: [Title]` title convention.
- `telegram-issue-sync` Phase 3 Step 6 now references the unified template instead of defining an inline template.
- `archive-tasks` skill now extracts and reports `Source:` metadata per task.
- "Architectural Blueprint Reference" renamed to "Blueprint Reference" in the orchestrator source context block.

## [7.1.1] - 2026-08-01

### Changed

- **README V7 consistency polish** — repository tree now labels `system-prompt.md` as the V7 Multi-Agent System Prompt, adds a `## Key V7 Changes` section (brainstorming protocol, universal datetime rules, SOLID mandate, leadership & language protocol, expanded skills registry), and completes the `skill-templates/` tree with all 28 skill directories (grouped General & Workflow / Stack-Specific Blueprints, alphabetical within each group — including previously missing `audit-agents/`).
- **`<execution_workflow>` renumbered** — workflow list now runs `1.`–`9.` instead of `0.`–`8.`. Discovery & Onboarding is step 1, explicitly labeled `(Phase 0)` to preserve the `<initialization>` anchor. Sub-steps re-parented: `1.5` Task Number Pre-Assignment Validation, `2.5` Deep Research Loop, `2.7` Combined Discovery+Plan Workflow. Internal "Loop back to step 3" reference corrected to step 4. Opening and closing `<execution_workflow>` tags moved to their own lines.
- **System prompt version bumped to 7.1.1** — PATCH increment per SemVer (formatting and documentation sync).

### Fixed

- **task-generator Collision Check renumbered** — step `2.5` moved to `3.5` so numbering ascends (Collision Check sits between Name and Generate File steps).
- **README skill-templates tree grouping labels** — `# General & Workflow` and `# Stack-Specific Blueprints` comment lines removed from the tree and replaced with standalone `**General & Workflow:**` / `**Stack-Specific Blueprints:**` lines before each group's first entry, keeping all 28 skill directories unchanged.
- **Memory auto-deletion policy reconciled** — `project-memory` Supersession Detection now scopes auto-`delete_memory` to store-time supersession within the same namespace/key topic only, aligning with `archive-tasks` Memory Validation's "NEVER auto-delete without Manager confirmation".

## [7.1.0] - 2026-08-01

### Added

- **Combined Discovery+Plan workflow template** (`<opencode_combined_task>`) — reducing Manager round-trips from 6 to 3.
- **Topic Shift Detection protocol** in `<user_input_processing>` for proactive context-switch notices.
- **Multi-phase task file support** in task-generator skill (single file with inline phase sections).
- **Memory Validation step** in archive-tasks skill for detecting stale/superseded memories.
- **Supersession Detection heuristic** in project-memory skill.
- **Pre-Commit Verification Gate** for DevOps/infrastructure tasks in bash_phase.

### Changed

- **Task number assignment** now requires mandatory pre-assignment validation via OpenCode ID discovery script.
- **CHANGELOG update step** now uses Parse-Then-Append Protocol to prevent duplicate section headers.
- **Senior Programmer persona** now enforces single-file multi-phase tasks instead of separate subtask files.

### Fixed

- **Task file numbering collision** (e.g., Task 608 assigned twice) by adding collision check to task-generator.
- **CHANGELOG duplicate `### Changed` headers** (Tasks 606, 610) by enforcing parse-before-append.

## [7.0.1] - 2026-07-25

### Changed

- **Milestone 5 archive** — Compacted task 65 into `docs/history/milestone-5-summary.md` and moved completed task file to `tasks/archive/`.

## [7.0.0] — 2026-07-25

### Changed

- **Platform-Agnostic Rebrand:** Removed all hardcoded references to "Google AI Studio" and "Gemini" from active project files. The workflow is now entirely vendor-neutral, relying on "Orchestrator" terminology. Covers system-prompt.md, README.md, AGENTS.md, skill-templates/, and user-prompts/.
- System prompt version bumped to 7.0.0.

## [6.12.0] — 2026-07-23

### Added

- **audit-agents conventions.md governance** — The `audit-agents` skill now auto-generates and audits `docs/conventions.md` with Universal DateTime Standard and SOLID Programming Guidelines. Mode 1 (Phase 0) generates conventions.md alongside AGENTS.md. Mode 2 audits and patches conventions.md if missing or incomplete. Agent Audit Summary expanded with conventions.md compliance status.

### Changed

- **Milestone 4 archive** — Compacted tasks 56–64 into `docs/history/milestone-4-summary.md` and moved completed task files to `tasks/archive/`.
- **System prompt upgraded to V6.12.0** — `<system_version>` bumped from 6.11.0 to 6.12.0.

## [6.11.0] — 2026-07-23

### Added

- **SOLID Programming Mandate** (`<solid_programming_mandate>`) — New block in `system-prompt.md` codifying the 5 SOLID principles (SRP, OCP, LSP, ISP, DIP) plus Pragmatic Guardrails (No-Zero-Abstraction Dogma, 3-Implementation Rule, YAGNI, Occam's Razor) to prevent over-engineering while enforcing strict architecture.
- **Universal DateTime Rules** (`<universal_datetime_rules>`) — New block in `system-prompt.md` enforcing: UTC at rest, ISO-8601 with Offset / Epoch ms at API boundaries, SOLID Clock Injection (banning unmockable clock calls), Dual-Representation for future calendar events, and `TZ=UTC` infrastructure enforcement.
- **`docs/conventions.md` DateTime & SOLID sections** — Dedicated documentation of the Universal DateTime Standard and SOLID Programming Guidelines for quick reference.
- **12 Skill Template DateTime Governance** — Injected stack-specific datetime rules into all skill templates covering Spring Boot, Python FastAPI, Flask, NestJS Prisma, Go Gin, Go Hexagonal gRPC, React Vite, Next.js, React Native Expo, Vue Nuxt, Android Kotlin, and iOS SwiftUI.

### Changed

- **System prompt upgraded to V6.11.0** — `<system_version>` bumped from 6.9.1 to 6.11.0.

## [6.10.0] — 2026-07-21

### Added

- **Global Auto-Setup (`LLM.txt`)** — Rewrote `LLM.txt` to install OpenCode configuration globally (`~/.config/opencode/`) instead of project-locally. Now handles: uv prerequisite check with user-confirmed installation, copy of both MCP server scripts (context + memory) to global directories, and global `opencode.json` with **absolute paths** for reliable MCP server execution from any working directory.
- **Global Skills Deployment** — `LLM.txt` Step 5 now copies `skill-templates/*` to `~/.config/opencode/skills/` for system-wide skill availability.

### Fixed

- **README Quick Install** — Fixed the one-click setup prompt to explicitly reference `LLM.txt` so users know exactly what to tell their AI agent.

## [6.9.1] — 2026-07-21

### Added

- **Deterministic Tool Orchestration (Anti-Lazy Rule)** — Added to `<constraints>` in `system-prompt.md`. Forces singular, deterministic MCP tool commands without "OR" fallback options, preventing LLM agents from bypassing tools.
- **Isolated Closure Mandate** — Added to execution workflow step 8. Forbids bundling `git mv` to completed with unrelated documentation tasks.

### Fixed

- **XML closing tag indentation** — Fixed leading whitespace on 5 closing XML tags (`</manager_profile>`, `</leadership_and_language_protocol>`, `</agent_skills_registry>`, `</user_input_processing>`, `</agentic_reasoning>`).
- **Code Reviewer strict tool enforcement** — Added "without alternative options" wording to force deterministic MCP tool execution.

## [6.9.0] — 2026-07-21

### Added

- **Discovery-First Mandate** — Injected into Software Architect and UI/UX Designer personas. Agents are strictly forbidden from generating architectural blueprints or roadmaps without first running a `code-search` discovery task to read factual codebase context.
- **PO Approval Gate** — Execution workflow updated from 7 to 8 steps. Code Reviewer now hands technical approvals to PO_REVIEW_PENDING. Agents are forbidden from moving tasks to `completed/` or running the commit MCP tool without explicit Manager keywords (e.g., "Approved for closure").
- **Environmental Checklist** — Injected into UI/UX Designer persona. Enforces checking offline states, latency, Dark/Light modes, and a11y rather than exclusively designing for the 'Happy Path'.
- **Anti-Hack / Clean Architecture Mandate** — Injected into Senior Programmer persona. Strictly forbids fragile fixes (e.g., arbitrary `setTimeout` race-condition masks) and demands structural refactors over dirty hacks.

## [6.8.0] — 2026-07-21

### Added

- **CRITICAL RULE 4 (File Staging)** — Added to `<bash_phase>` of `<opencode_implementation_task_template>` in `system-prompt.md`. Forces the Orchestrator to explicitly include `git mv tasks/backlog/XX-task.md tasks/in-progress/XX-task.md` as the first bash command when the active task resides in `tasks/backlog/`. This resolves a deadlock where Zero-Autonomous-Commit prevented task file promotion when the Orchestrator forgot to write the command.

## [6.7.1] — 2026-07-19

### Changed

- **Multi-Agent Brainstorming Enhancement** — Added explicit `<tradeoffs>` and `<conflict_resolution>` blocks to the XML schema in both `system-prompt.md` and `user-prompts/multi-agent-brainstorming.md`. This forces an iterative debate layer where personas explicitly "hash out" compromises, producing a solution magnitudes superior to siloed outputs.

## [6.7.0] — 2026-07-19

### Added

- **Manager Profile (`<manager_profile>`)** — Added a dedicated block in `system-prompt.md` defining the Manager's background (Mohammad, self-taught, Linux/Android expert, transitioning from solo dev to Product Owner). This allows the AI to tailor its technical assumptions and communication style perfectly to the user's history.
- **Leadership & Language Coaching (`<leadership_and_language_protocol>`)** — Transformed the Orchestrator into an Executive Coach and English Tutor.
  - **Vocabulary Assistance:** Personas will explicitly teach industry keywords if the Manager forgets them.
  - **English Corrections:** Appends a non-disruptive `> 💡 **Coach's Note:**` correcting grammar and teaching pronunciation using Persian phonetic characters (e.g., /مَنِیجِر/).
  - **Sprint Retrospectives:** When a sprint is closed or feedback is requested, personas break character to ruthlessly critique the Manager's tone, phrasing, and empathy from the perspective of a simulated human team member.
- **Setup Integration** — Added instructions in `README.md` and `LLM.txt` so new users know to customize this profile for themselves.

## [6.6.0] — 2026-07-17

### Added

- **Multi-Agent Brainstorming Protocol** (`system-prompt.md`) — new `<brainstorming_protocol>` section defining Phase 1.5, six expert personas (system_architect, security_engineer, product_manager, business_strategist, legal_advisor, critical_thinker), and the exact XML-tagged output schema for session reports.
- **Standalone brainstorming user prompt** (`user-prompts/multi-agent-brainstorming.md`) — reusable XML-tagged prompt template for running the simulated 6-persona expert swarm in any chat environment (AI Studio, ChatGPT, Claude, Gemini). Includes role, system context, agentic reasoning, constraints, and output format blocks.
- **`brainstorm-swarm` skill definition** — added to `<agent_skills_registry>` in system-prompt.md under Global Workflow Skills.
- **Brainstorming trigger rule** — new Step 3 in `<user_input_processing>`: if the Manager requests brainstorming or the input exhibits cross-disciplinary ambiguity, halt and trigger Phase 1.5 instead of blind execution.

### Changed

- **System prompt upgraded to V6.6.0** — `<system_version>` already at 6.6.0. `brainstorm-swarm` added to `<agent_skills_registry>`. `<user_input_processing>` expanded with brainstorming trigger. New `<brainstorming_protocol>` section added.
- **AGENTS.md guardrails** — added directive: trigger Multi-Agent Brainstorming Loop when Manager requests brainstorming or cross-disciplinary ambiguity is detected. Interpret `<brainstorming_session>` results as non-functional guidelines.

## [6.5.1] — 2026-07-17

### Fixed

- **Skill name standardization** — Aligned YAML `name:` fields across all 27 `skill-templates/*/SKILL.md` files to match folder names exactly. Removed architecture-prefixed names (`backend-architecture-*`, `frontend-architecture-*`, `mobile-architecture-*`) and `stitch::extract-design-md` in favor of clean short names matching each folder.
- **System prompt consistency** — Added missing `archive-tasks` and `migrate-kanban` to the skills registry. Aligned all 27 skill descriptions in `<agent_skills_registry>` verbatim with their YAML `description:` counterparts.

### Changed

- **Milestone 3 archive** — Compacted tasks 49–55 into `docs/history/milestone-3-summary.md` and moved completed task files to `tasks/archive/`.

## [6.5.0] — 2026-07-16

### Added

- **Perplexity Deep Research 3-Step Framework** (`user-prompts/perplexity-deep-research.md`) — reusable user prompt template encoding a Broad → Refined → Precise search pyramid for Perplexity. Forces 9 targeted `search_web` calls in three rounds before synthesizing a final answer with citations.
- **`perplexity-research` Agent Skill** (`skill-templates/perplexity-research/SKILL.md`) — companion skill teaching OpenCode when to HALT and trigger the human-in-the-loop deep research cycle. Covers post-2025 dependencies, undocumented API errors, and complex OS/hardware bugs.
- **Deep Research Loop workflow step** — new Step 1.5 in `<execution_workflow>` inserted between Input Processing and Plan & Review. The Orchestrator now checks whether post-2025 external research is required before proceeding to implementation planning.

### Changed

- **System prompt upgraded to V6.5.0** — `<system_version>` bumped. `perplexity-research` added to `<agent_skills_registry>` under Global Workflow Skills. Execution workflow expanded with Step 1.5 Deep Research Loop.

### Changed

- **`perplexity-research` skill UX refactored** — skill now embeds the full 3-Step Framework prompt inline, so the Manager can copy the entire Perplexity session prompt with one click instead of opening `user-prompts/perplexity-deep-research.md` separately. The standalone user prompt file is preserved for manual use-cases.

## [6.4.1] — 2026-07-16

### Changed

- **README.md** — Cleaned up the Future Architectural Roadmap by removing completed tasks (V6.0.0 Kanban, V6.1.0 QA Persona, V6.2.0 Prompt Refactoring, V6.4.0 Memory Management) and renumbering remaining items.

## [6.4.0] — 2026-07-16

### Added

- **Project Memory MCP Server** (`mcp-memory-server/server.py`) — new FastMCP server providing persistent, project-scoped memory via atomic-write markdown files under `.opencode/memory/`. Five tools: `store_memory` (with atomic writes using tempfile + os.replace), `read_memory`, `search_memory` (full-text across namespaces), `list_namespaces`, and `delete_memory` (for pruning obsolete constraints).
- **`project-memory` Agent Skill** (`skill-templates/project-memory/SKILL.md`) — companion skill teaching OpenCode when to proactively store Manager constraints and when to retrieve them during the Context Phase.
- **`opencode.json` registration** — `project_memory` MCP server registered alongside `custom_context`, with explicit permissions for `store_memory`, `read_memory`, `search_memory`, and `list_namespaces`.
- **System prompt integration** — `project-memory` added to `<agent_skills_registry>` under Global Workflow Skills. Software Architect and Senior Programmer personas updated to proactively save Manager constraints via the `project-memory` skill.

### Changed

- **System prompt upgraded to V6.4.0** — `<system_version>` bumped.
- **`audit-agents` skill** — Target Audit Criteria (Mode 1 and Mode 2) and AGENTS.md Template updated with Context Bootstrapping rule: agents must call `search_memory`/`list_namespaces` at task start.
- **README.md** — Roadmap item #7 (Memory Management) struck through and marked implemented in V6.4.0.

## [6.3.0] — 2026-07-16

### Added

- **Intelligent Cold-Start & Vertical Slicing Protocol** — new `code-search` skill section (`### Vertical Slicing Strategy`) instructing OpenCode to target specific feature modules instead of scanning the whole repo, and to always bundle Core SOP files (`AGENTS.md`, `DESIGN.md`, `docs/*.md`) in the context report.
- **`user-prompts/cold-start-context.md`** — reusable dual-language (English/Farsi) prompt for the Manager to trigger local cold-start context generation directly in OpenCode, bypassing AI Studio for the discovery phase.
- **Phase 0 cold-start routing** — `<execution_workflow>` updated: for EXISTING projects with an empty context window, the Orchestrator instantly outputs a discovery task to fetch the directory tree, extract vertical slice signatures, and read all Core SOP files.

### Changed

- **System prompt upgraded to V6.3.0** — `<system_version>` bumped. `<opencode_discovery_task_template>` execution phase updated to mandate fetching AGENTS.md, DESIGN.md, and docs/*.md as absolute source-of-truth, with explicit Vertical Slice Extraction instructions added between core file reading and compilation.
- **README.md** — directory tree updated to include `cold-start-context.md` in `user-prompts/`.

## [6.2.0] — 2026-07-16

### Added

- **Omni-Channel Bilingual Prompt Pipeline** — bilingual (Farsi-to-English) translation and expansion layer embedded across AI Studio, OpenCode, and Telegram syncs.
- **Bilingual Translation guardrail** — new guardrail in `AGENTS.md` and `audit-agents` skill (template + audit criteria) forbidding execution of raw non-English prompts before `prompt-refactor` processing.

### Changed

- **System prompt upgraded to V6.2.0** — `<system_version>` bumped. `<user_input_processing>` block replaced with 4-step Automated Refactoring Pipeline: Bilingual Translation → Intent Expansion → Clarification → Seamless Routing.
- **`prompt-refactor` skill** — Workflow Execution Step 1 updated to Bilingual Translation & Analysis: raw Farsi or informal English is seamlessly translated into technical English before structuring.
- **`telegram-issue-sync` skill** — Phase 3 Step 3 now explicitly documented as the omni-channel filter, passing `RAW_TEXT` (which may be Farsi) through `prompt-refactor` for translation and architectural expansion.
- **README.md** — Roadmap item #5 struck through and marked implemented in V6.2.0.

## [6.1.0] — 2026-07-16

### Fixed

- **Kanban `git mv` duplicate file bug** — `commit_and_clean_task` MCP tool hardened: `git add <single_file>` replaced with `git add -A tasks/` to catch deletions caused by standard `mv` fallbacks when Kanban directories are empty.
- **Missing `mkdir -p` in completion instructions** — Code Reviewer persona and workflow Step 7 updated to explicitly mandate `mkdir -p tasks/completed/` before `git mv`, preventing failures when the target directory doesn't exist.

### Added

- **QA Engineer persona** — new `<persona name="QA Engineer">` block in `system-prompt.md` inserted between Project Planner and Code Reviewer. Adopts a strictly adversarial mindset: reads the factual Git Diff, looks for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Outputs QA_PASSED or QA_REJECTED with vulnerabilities and missing tests report.
- **7-step execution workflow** — `<execution_workflow>` expanded from 6 to 7 steps with a new Step 4 (Adversarial QA) between implementation and team review. Fix loop now involves both Programmer and QA if either rejects.

### Changed

- **System prompt upgraded to V6.1.0** — `<system_version>` bumped. QA Engineer persona added. Execution workflow updated with adversarial QA step.
- **Summary phase handover instructions** — `<summary_phase>` in `<opencode_implementation_task_template>` now differentiates between logic tasks (instructing Manager to send to QA Engineer) and documentation/CSS tasks (sending directly to Code Reviewer), preventing human workflow errors.
- **README.md** — How to Operate section updated with QA Loop description. Roadmap item #8 struck through and marked implemented in V6.1.0.

## [6.0.0] — 2026-07-16

### Added

- **Kanban lifecycle architecture** — flat `tasks/` directory replaced by state-based folders: `tasks/backlog/`, `tasks/in-progress/`, `tasks/qa/`, `tasks/completed/`, `tasks/archive/`. Task files are physically moved through the pipeline as work progresses.
- **`commit_and_clean_task` MCP tool** — new tool on the custom context server (`mcp-context-server/server.py`). Commits staged changes, captures the commit hash, replaces the raw git diff in the task file with the hash reference to save space, and amends the commit to include the cleaned file.
- **`migrate-kanban` skill** — `skill-templates/migrate-kanban/SKILL.md` for automated migration of existing flat `tasks/` files into the Kanban structure by reading `Status:` metadata. Uses `git mv` to preserve history.
- **`archive-tasks` skill** — `skill-templates/archive-tasks/SKILL.md` for milestone compaction. Scans completed tasks, generates dense `docs/history/milestone-X-summary.md` summaries, and moves files to `tasks/archive/`.

### Changed

- **System prompt upgraded to V6.0.0** — `<system_version>` bumped. Project Planner persona now manages state-based Kanban directories. Code Reviewer APPROVED action now generates tasks that move files through the pipeline and uses `custom_context_commit_and_clean_task`. Execution workflow updated with `backlog → in-progress → qa → completed` transitions. Implementation task template summary path updated to `tasks/in-progress/`.
- **`task-generator` skill** — directory references changed from `tasks/` to `tasks/backlog/`. Task ID calculation now uses `find` across all Kanban subdirectories instead of `ls`.
- **`telegram-issue-sync` skill** — `NEXT_ID` bash command updated to use `find tasks/ -type f -name "*.md"`. File creation paths changed to `tasks/backlog/`.
- **`audit-agents` skill** — Core File Locations and Audit Criteria updated to list the 5 Kanban directories (`tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`). AGENTS.md template updated accordingly.
- **README.md** — directory tree updated to show Kanban structure and new skills. Item 9 in Future Architectural Roadmap marked as implemented in V6.0.0. New "Key V6 Changes" section added.
- **README roadmap** — Added Memory Management (Smart Note-Taking MCP & Skill) as item #7 in the Future Architectural Roadmap, describing a local `memory-mcp` server and `project-memory` agent skill for persistent context retention.
- **README roadmap** — Added Adversarial QA Persona as item #8 and Lifecycle Task Architecture (Kanban & Archiving) as item #9 to the Future Architectural Roadmap, describing a dedicated `[QA Engineer]` persona with adversarial testing instructions and a state-based Kanban folder workflow with archiving compaction.

## [5.19.0] — 2026-07-15

### Added

- **OpenCode docs mirror** — All 36 documentation pages from opencode.ai/docs fetched into `docs/opencode/` as clean Markdown files for offline reference.
- **`LLM.txt`** — AI agent auto-configuration manual at project root. Contains platform-specific OpenCode setup instructions (macOS/Linux via Bash, Windows via PowerShell), the exact `opencode.json` payload for the custom_context MCP server, skill installation commands, and a ready-to-use "Agent Prompt" for self-configuration.
- **`docs/conventions.md`** — Centralized documentation for syntax rules and automation conventions (e.g., `--body-file` pattern for gh commands).
- **Strict Grounding constraint** — Added to `<constraints>` block in `system-prompt.md`. Enforces that the assistant relies only on provided context, treating external knowledge as unsupported.
- **CRITICAL RULE 3 (Output Truncation)** — Added to `<opencode_implementation_task_template>` instructing OpenCode to pipe massive test output through `grep`/`tail` to avoid 50KB truncation.

### Changed

- **Rebranded repository to `cognitive-lead-hq`** — updated GitHub description, topics, and renamed repo. Restructured README.md with flat-square shields.io badges, improved hierarchy, Quick Start section. Preserved all Agent Skills tables and MCP configuration sections.
- **Enforced `--body-file` pattern for all `gh issue create` commands** — replaced inline `--body` in `skill-templates/telegram-issue-sync/SKILL.md`, `tasks/22-refactor-telegram-skill-templates.md`, `tasks/11-enforce-project-skill-loading.md`, and `tasks/06-implement-telegram-issue-sync-skill.md` with heredoc `--body-file` pattern using single-quoted `'EOF'` delimiter.
- **README.md** — Updated Quick Start to reference `LLM.txt` as the canonical auto-setup source.
- **System prompt upgraded to V5.19.0** — `<system_version>` bumped. `<agentic_reasoning>` rewritten with Google's official 10-step nested reasoning framework with numbered sub-points, explicit tool-preference rules, and intelligent retry logic. Updated `<opencode_implementation_task_template>` with subagent delegation (`@scout`, `@general` alongside `@explore`) and `apply_patch` path marker syntax.

## [5.18.0] — 2026-07-13

### Added

- **Dependency Tracing Protocol:** Injected into `code-search` skill — forces deep, recursive import/DI tracing via `extract_signatures` and multi-layer source reading for complete, unbroken context reports.
- **`verification-before-completion` skill:** New agent skill enforcing the "Iron Law" — no completion claims without fresh test/lint evidence. Mandatory Gate Function before `<summary_phase>`.
- **Hardened AI Studio XML templates:** Discovery template now requires Dependency Tracing Protocol adherence; implementation template `<bash_phase>` rewritten to invoke `verification-before-completion` skill with strict 3-attempt limit and explicit exit-code-0 gate.
- **Enforced Micro-Task Checklists:** Implementation template `<execution_phase>` now mandates `- [ ]` checklist with stateful step tracking — OpenCode must physically check off each step after completing it.
- **Explicit Skill Orchestration Routing:** Senior Programmer persona now required to specify exactly WHICH skills to load, WHY and HOW for each, and break implementation into a strict numbered checklist.
- **`verification-before-completion` added to Agent Skills Registry:** Listed as a Global Workflow Skill for mandatory test/lint gate enforcement.
- **Restored Critical Bash & Context Guardrails:** Re-added native tool instructions (`read`, `glob`, `@explore`, MCP) to `<context_phase>` and restored CRITICAL RULE 1 (non-interactive flags) and CRITICAL RULE 2 (Git command ban via MCP) to `<bash_phase>`, merged safely with the new Gate Function.

- **NestJS Prisma Vertical Skill Template:** Created `skill-templates/nestjs-prisma-vertical/SKILL.md` enforcing NestJS decorators, Vertical Slice Architecture, Prisma ORM, strict TypeScript, and class-validator DTOs for zero-hallucination backend development.

### Changed

- **Tree-sitter AST upgrade for `extract_signatures` MCP tool:** Replaced the regex-based signature extractor in `mcp-context-server/server.py` with a multi-language tree-sitter AST parser. Supports Python, JavaScript, TypeScript, Go, Java, Rust, and Kotlin with accurate function/class/interface/method signature extraction. Falls back to the existing regex when no grammar is available for a given language. Added 7 new tree-sitter dependencies to the inline script metadata.

- **Bulk Prettier Format:** Ran `npx prettier --write "**/*.md"` across all 46 markdown files to enforce consistent formatting — blank-line spacing, list indentation, code-fence normalization, and trailing newlines.
- **Android Kotlin Template Overhaul:** `skill-templates/android-kotlin/SKILL.md` completely rewritten with strict XML ban, Hilt DI mandate, compile-time safe DB (SQLDelight/Room), and enhanced null-safety rules.
- **React Native Expo Template Overhaul:** `skill-templates/react-native-expo/SKILL.md` rewritten with Expo Managed Workflow enforcement, ban on native folder edits, mandatory NativeWind, and strict TypeScript requirement.
- **README.md:** Updated Stack-Specific Blueprints table to reflect removed and added templates; strengthened Android Kotlin and React Native Expo descriptions with zero-hallucination rules.

### Removed

- **`skill-templates/nodejs-express/`:** Deleted — unstructured Express patterns cause AI hallucinations. Superseded by opinionated frameworks (NestJS).
- **`skill-templates/android-java-xml/`:** Deleted — XML layout files cause severe UI hallucinations. Superseded by 100% Jetpack Compose Android Kotlin template.

## [5.17.0] — 2026-07-04

### Added

- **Max-Efficiency AI Skill Templates:** Completely rewrote the Node.js Express, Python FastAPI, and Android Kotlin skill templates to enforce "The 4 Pillars of AI-Native Code" (Strict Static Typing, Declarative UI, Low Boilerplate, Extreme Modularity) derived from LLM behavioral analysis.
- **Node.js Template Upgrade:** Migrated from plain JavaScript to strict TypeScript with Zod validation to eliminate AI hallucinations.
- **FastAPI Template Upgrade:** Enforced strict Pydantic V2 schemas and mandatory type-hinting.
- **Android Template Upgrade:** Explicitly banned XML layouts to conserve token limits and mandated 100% modular Jetpack Compose.
- **Universal AI-Native Framework Upgrades:** Injected strict `AI Context & Token Optimization` constraint blocks into all 11 stack skill templates. This ensures OpenCode always utilizes hallucination-resistant patterns (e.g., Strict TypeScript, Zod, MapStruct, Feature-Sliced Design, Server Actions) regardless of the chosen framework.
- **Restored Structural Guardrails:** Fully restored the `Project Structure`, `Naming Conventions`, and `Testing Strategies` sections to the Node.js, FastAPI, and Android Kotlin templates, correcting an over-optimization from Task 27 and returning the repository to full SOP compliance.

## [5.1.0] — Prompt Optimization & Input Processing

### Added

- **`<user_input_processing>` block:** Integrated a robust pre-processing phase to clean up informal, raw text from the Manager. The AI is now strictly instructed to HALT and ask clarifying questions if the request is ambiguous, eliminating blind guessing.
- **Agentic Workflow alignment:** Overhauled the `<agentic_reasoning>` block to perfectly match Google's official 9-point system instruction template (Logical dependencies, Risk assessment, Abductive reasoning, Outcome evaluation, Information availability, Precision & Grounding, Completeness, Persistence, Inhibit response).
- **Strict Grounding Rules:** Added constraints to treat the provided context as the absolute limit of truth, preventing hallucination.

### Changed

- **Execution Workflow:** Inserted "Input Processing & Clarification" as Step 1 in the execution pipeline.

## [5.0.0] — V5 Decentralized Task Architecture

### Added

- **`tasks/` directory** — decentralized, numbered task files replace global `STATE.md` and `TODO.md`. Each task file tracks its own TODOs, final status, technical changes, and architectural reasoning.
- **`skill-templates/task-generator/SKILL.md`** — new skill for automatically generating structured task files based on Manager instructions, with halt-and-handover protocol.
- **`skill-templates/audit-agents/SKILL.md`** — new skill for auditing `AGENTS.md` to enforce task update workflows, UI/UX checks, and legacy global state removal.
- **Phase 0 UI/UX traversal rule** — Project Planner now instructs OpenCode to perform deep source code traversal resulting in a comprehensive `DESIGN.md`.

### Changed

- **Project Planner persona** in `system-prompt.md` — duty and behavior rewritten to manage decentralized task files in `tasks/` as the single source of truth, dropping `STATE.md` and `TODO.md` references.
- **`AGENTS.md`** — documentation sync rules updated to reference `tasks/` active task file and `DESIGN.md`; removed `STATE.md` and `TODO.md` from sync requirements.
- **`.opencode/skills/sop-maintenance/SKILL.md`** — added documentation sync rules for task files and `DESIGN.md`.
- **`<opencode_implementation_task_template>`** — context phase now reads active task file instead of `STATE.md`; documentation phase updates active task file instead of `STATE.md`/`TODO.md`.
- **Runtime model identifier** — `Gemini 3.5 Flash` renamed to `Gemini` throughout `system-prompt.md`.

### Removed

- **`STATE.md`** — replaced by decentralized task files in `tasks/`.
- **`TODO.md`** — replaced by per-task local TODOs in task files.

## [4.0.0] — V4 Multi-Agent Skills Update

### Added

- Integrated Google's official **Agentic Reasoning System Instruction** for superior logic, risk assessment, and abductive reasoning.
- Added `opencode.json` auto-configuration to Phase 0 for enforcing formatters and tool permissions.
- Created native OpenCode skill at `.opencode/skills/sop-maintenance/SKILL.md` for repository maintenance rules.

### Changed

- Shifted from monolithic `AGENTS.md` to OpenCode's native **Agent Skills** (`SKILL.md`) framework for progressive disclosure and optimized context usage.
- Upgraded `<opencode_task>` to leverage OpenCode's native tools (`lsp`, `@explore`, `websearch`) instead of relying solely on bash commands.
- Restructured the repository: migrated `stacks/` to `skill-templates/` and converted the repo's own rules into `.opencode/skills/sop-maintenance/SKILL.md`.
- Updated `system-prompt.md` to V4 with expanded personas, enhanced Agentic Reasoning, and the full `<opencode_protocol>` XML structure.

### Removed

- Removed monolithic `AGENTS.md` file (replaced by `.opencode/skills/sop-maintenance/SKILL.md`).
- Removed `stacks/` directory (migrated to `skill-templates/`).

## [4.1.0] — V4.1 Production-Ready Refinements

### Added

- **MCP server support** across all personas and `<opencode_protocol>` for external API/database context.
- **`STATE.md` management** — Project Planner persona now owns `STATE.md` as the single source of truth for architecture, features, and bugs.
- **Storybook-friendly component isolation** requirement in UI/UX Designer persona.
- **Bug fix documentation rule** — complex fixes generate dedicated `SKILL.md` files.
- **DevOps/Infrastructure** duty added to Software Architect persona.
- **CRITICAL RULE 2** in `<bash_phase>` — test suite and type-checker must pass before summary.

### Changed

- **SOP Import Rule** simplified — always instruct Manager to copy `SKILL.md` templates from external SOP repo.
- **Phase 0** now generates/updates `STATE.md` alongside `opencode.json` and Agent Skills.
- **Context phase** now requires reading `STATE.md` first.
- **Documentation phase** now updates `STATE.md` alongside `TODO.md` and `SKILL.md`.
- **Architect behavior** — now rephrases fragmented requests for confirmation before proceeding.

## [4.2.0] — Custom Context MCP Integration

### Added

- **Custom Context MCP** server (`mcp-context-server/server.py`) using FastMCP for `.gitignore`-aware file reading and directory tree exploration.
- **`code-search` Agent Skill** at `.opencode/skills/code-search/SKILL.md` documenting the custom context codebase exploration workflow.
- **MCP Setup Rule** in Phase 0 of `system-prompt.md` — AI now checks for MCP servers and assists with `mcp-context-server` setup.
- **`STATE.md`** — new single source of truth for repository architecture, integrations, and known items.
- **README.md** section on Custom Code Context MCP with setup instructions.

## [4.6.0] — V4.6 Dual-Task Protocol

### Added

- **Dual-Task Protocol** (`<opencode_discovery_task>` and `<opencode_implementation_task>`) in the system prompt to strictly separate context gathering from code execution.
- `docs/opencode-schema.json` to ensure strict type-safety and validation for OpenCode configurations.

### Changed

- Streamlined `AGENTS.md` into a concise Project Context Hub (<150 lines) with a strict guardrail against reading `context-reports/` directly.
- Re-wrote the `code-search` skill to enforce the `read_source_files` MCP handover workflow, stopping OpenCode from polluting its own context window.

## [5.3.0] — V5.3 Ultimate Factual Diff Architecture

### Added

- **`stage_and_inject_diff` MCP tool** — new MCP tool on the custom context server that stages all Git changes, extracts the factual `git diff --staged`, and injects it into the active task file's `<!-- BEGIN_GIT_DIFF -->` block.
- **`extract_signatures` MCP tool** — new MCP tool that extracts structural signatures (classes, functions, methods, interfaces) from source files using regex, enabling context-bloat prevention during codebase exploration.
- **Workspace Security constraint** — OpenCode is strictly forbidden from executing terminal commands that modify files outside the current project workspace. Destructive commands must only target known auto-generated directories.
- **3-attempt bash failure limit** — CRITICAL RULE 2 now permits a maximum of 3 consecutive repair attempts before halting and outputting a `<failure_report>`.
- **Core File Locations anchor** in `AGENTS.md` — explicitly lists exact paths for `AGENTS.md`, `DESIGN.md`, `tasks/`, and `.opencode/skills/`.
- **Mandatory End-Of-Task Sequence** in `AGENTS.md` — mandates a 3-step completion process: write reasoning, call `stage_and_inject_diff`, notify Manager.

### Changed

- **`AGENTS.md`** — appended Core File Locations and Mandatory End-Of-Task Sequence blocks.
- **Code-review audit criteria** — audit-agents SKILL.md now checks for Core File Locations and Mandatory End-Of-Task Sequence.
- **Task template** — task-generator SKILL.md now uses `OpenCode Execution Log & Reasoning` and `Factual Git Diff` sections with MCP injection markers.
- **Code-search workflow** — code-search SKILL.md now includes an `extract_signatures` step before full file reads to prevent context bloat.
- **`summary_phase`** in `system-prompt.md` — replaced with exact `stage_and_inject_diff` finalization sequence.
- **`documentation_phase`** in `system-prompt.md` — streamlined to manual logging in task file under `OpenCode Execution Log & Reasoning`.
- **Code Reviewer persona** — now reviews based strictly on the "Factual Git Diff" block inside the task file, with iteration instructions for rejections.

## [5.16.0] — 2026-07-03

### Added

- **Strict Approval Gate & Inline Review Pattern:** Formalized the requirement that the AI Studio Orchestrator must receive explicit Manager approval before generating OpenCode implementation tasks.
- **Markdown Review Convention:** Documented the `> 📝 **MANAGER REVIEW:**` blockquote syntax in both `system-prompt.md` and `README.md` to establish a standard method for Managers to leave inline feedback on architectural blueprints.

## [5.15.0] — 2026-07-02

### Added

- **Mandatory Structural Validation Phase:** Injected a new `<validation_phase>` as the very first phase in both the `<opencode_discovery_task>` and `<opencode_implementation_task>` templates. Every generated instruction now starts with reading `AGENTS.md`, then reading every referenced configuration file (`DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, `docs/conventions.md`), cross-checking the Orchestrator's instructions against project rules, and halting with a `⚠️ RULE VIOLATION WARNING` if a violation is found — before any context gathering or execution begins.

### Changed

- **`system-prompt.md`** — `<system_version>` bumped from `5.14.0` to `5.15.0`. Both task templates restructured with `<validation_phase>` as the structural first phase.

## [5.14.0] — 2026-07-02

### Added

- **Agentic Self-Correction Loop (Gatekeeper Protocol):** Empowered OpenCode to act as a strict gatekeeper. OpenCode now cross-checks tasks against `AGENTS.md` and `DESIGN.md`, halting execution and issuing a `⚠️ RULE VIOLATION WARNING` if the AI Studio Orchestrator hallucinates or breaks architectural rules.
- Updated `audit-agents` skill to enforce the Gatekeeper Protocol on all newly scaffolded projects.

## [5.13.2] — 2026-06-30

### Changed

- **`skill-templates/telegram-issue-sync/SKILL.md`** — Replaced LLM-driven JSON state mutation with a deterministic Python updater script. Removed verbose Telegram MCP behavioral documentation. Consolidated from 5 to 4 phases.
- **`skill-templates/telegram-message-export/SKILL.md`** — Simplified message export workflow. Removed multi-input resolution section. Stripped verbose per-message formatting. Consolidated from 5 to 4 phases.

## [5.13.1] — 2026-06-30

### Changed

- **`README.md`** — Updated repository tree to feature `go-hexagonal-grpc` and `prompt-refactor` as prominent entries; appended 2 new strategic items to the Future Architectural Roadmap (Automated Prompt Refactoring Pipeline and Hexagonal Architecture Expansion).

## [5.13.0] — 2026-07-01

### Added

- **`skill-templates/go-hexagonal-grpc/SKILL.md`:** New Agent Skill template for Go Hexagonal Architecture (Ports & Adapters) with gRPC, Uber Fx compile-time DI, Redis caching, and PostgreSQL (pgx/ent). Designed for ultra-low-latency backends like the Caller ID system.
- **`skill-templates/prompt-refactor/SKILL.md`:** New meta-cognitive Agent Skill template for refactoring basic human prompts into elite, XML-tagged, agent-optimized system instructions with `<role>`, `<system_context>`, `<agentic_reasoning>`, `<constraints>`, and `<output_format>` blocks.
- **`<core_workflow_skills>` registry** — injected directly into `system-prompt.md` to grant the AI Studio Orchestrator proactive awareness of available workflow tools (like `debug-instrumentation` and `versioning-and-release`).
- **Comprehensive Agent Skills Library tables** — added to `README.md` detailing both general workflow skills (10 skills) and stack-specific blueprints (13 stacks).

### Changed

- **`skill-templates/android-kotlin/SKILL.md`:** Upgraded from MVVM to strict MVI (Model-View-Intent) with Unidirectional Data Flow. ParsePlatform references replaced with gRPC/Ktor. Offline-First Room caching mandated. Added a complete Kotlin MVI contract example with sealed Intents and reducer-style ViewModel.
- **Updated `SKILL LOADING` instructions** in task templates to explicitly instruct the Orchestrator to route core workflow skills based on task requirements, consulting the new `<core_workflow_skills>` registry.

## [5.12.0] — 2026-06-29

### Added

- **Zero-Autonomous-Commit (ZAC) Workflow:** Enforced strict separation of code staging from committing. OpenCode is now forbidden from running `git add`, `git commit`, or `git stash` during implementation (CRITICAL RULE 3). Staging is handled exclusively by the `custom_context_stage_and_inject_diff` MCP tool.
- **Reviewer-Driven Commit Cycle:** Code Reviewer persona now generates commit tasks on `APPROVED` status and fix-loop implementation tasks on `REJECTED_NEEDS_FIXES` status, completing the review loop.
- **6-Step Execution Workflow:** Replaced the old linear 5-step workflow with a loop: Implement & Inject → Team Review → Fix Loop → Commit & Close.
- **Audit-Agents ZAC Propagation:** Updated `skill-templates/audit-agents/SKILL.md` to enforce the Zero-Autonomous-Commit (ZAC) workflow in newly scaffolded or audited projects — ZAC criterion added to both Target Audit Criteria blocks, Git guardrails added to the AGENTS.md template, and End-Of-Task Sequence updated.
- **Cognitive Language Rule:** Enforced English-only cognitive reasoning and execution logging across both AI Studio (reasoning_log, blueprints, task generation) and OpenCode (execution logs). Appended future architectural TODOs to README.md.
- **`skill-templates/debug-instrumentation/SKILL.md`:** new Agent Skill template for diagnosing complex bugs, deadlocks, race conditions, and silent failures via strategic logging and tracing.
- **`skill-templates/audit-agents/SKILL.md`:** Added Complex Debugging audit criteria referencing the new debug-instrumentation skill to both Target Audit Criteria blocks and the AGENTS.md template guardrails.

### Changed

- **`system-prompt.md`** — `<system_version>` bumped to 5.10.0. Code Reviewer behavior updated. CRITICAL RULE 1 in bash phase no longer lists `git commit` as a non-interactive example. CRITICAL RULE 3 added forbidding Git commands. `<execution_workflow>` rewritten with implement/inject, review, fix-loop, and commit steps.
- **`AGENTS.md`** — Added Git guardrail under Actionable Guardrails. Mandatory End-Of-Task Sequence step 3 updated to forbid `git commit` commands.
- **`stage_and_inject_diff` MCP tool** — optimized the staged git diff command to globally exclude the entire `tasks/` directory (`:!tasks/`) instead of just the single active task file, completely eliminating task history clutter from factual codebase reviews.

## [5.9.0] — 2026-06-21

### Added

- **🛑 MANDATORY FIRST-READ RULE:** Added rules to `system-prompt.md` and `AGENTS.md` forcing coding agents to read global configurations and architectural files before starting any implementation.
- **Parallel Subagent Guidelines:** Declared OpenCode's ability to run up to 4 concurrent subagent tasks during Phase 0 discovery.
- **Core File Scaffolding Templates:** Integrated full schemas and templates for `architecture.md`, `DESIGN.md`, and `AGENTS.md` directly into the `audit-agents` skill template.
- **AI-Driven Project Initialization Standards:** Standardized templates for Android Kotlin, Spring Boot, Node.js, Nuxt, and Next.js in `skill-templates/`.
- **Task 15:** Added the active task file tracking this major system prompt and scaffolding upgrade.

## [5.7.1] — 2026-06-17

### Changed

- **`system-prompt.md`** — `<system_version>` bumped to 5.7.1. `documentation_phase` text changed from discretionary `"Update CHANGELOG.md if necessary"` to mandatory `"You MUST update CHANGELOG.md with a new entry following the project's versioning rules."`
- **`AGENTS.md`** — Mandatory End-Of-Task sequence expanded from 3 steps to 4 steps. New Step 1: "Update Changelog" — agents must now insert a formal CHANGELOG.md entry before writing their summary.
- **`skill-templates/audit-agents/SKILL.md`** — AGENTS.md Template and Target Audit Criteria updated to reflect the new 4-step mandatory completion process.

## [5.8.0] — 2026-06-17

### Added

- **`skill-templates/telegram-message-export/SKILL.md`** — new Agent Skill template for exporting Telegram messages (text, images, voice notes) into a numbered folder and packing them into a ZIP archive. Supports three input methods: message ID range, message link, and text search.

## [5.7.0] — 2026-06-16

### Added

- **Skill Loading Rules section** in `AGENTS.md` — two new mandatory rules: 1) Load `task-generator` skill before creating new task files. 2) Scan and load relevant project tech-stack skills before task implementation.
- **Two new audit criteria** in `audit-agents/SKILL.md` — audits now verify that `AGENTS.md` contains both Task-Generator Skill Loading and Project Skill Loading rules.
- **`task-generator` mention** in both discovery and implementation task template `SKILL LOADING` blocks in `system-prompt.md` — OpenCode now loads the task-generator skill when task creation is involved.
- **Phase 0 Generation Mode** in `audit-agents/SKILL.md` — skill now has a full AGENTS.md template and workflow for generating the file from scratch on new projects.

### Changed

- **`system-prompt.md`** — `<constraints>` Mandatory Project Skill Loading clarified to cover both tech-stack skills (e.g., `android-kotlin`, `spring-boot`) and workflow skills (e.g., `task-generator`). All `SKILL LOADING` blocks now reference `task-generator` alongside tech-stack examples. Phase 0 workflow and Project Planner persona updated to instruct OpenCode to load the `audit-agents` skill for AGENTS.md generation.
- **Simplified skill loading instructions** in `AGENTS.md`, `system-prompt.md`, and `audit-agents/SKILL.md` — removed redundant "scan `.opencode/skills/`..." path instructions since OpenCode auto-discovers skills natively. Now just says "load every available skill matching..."
- `<system_version>` bumped from 5.6.0 to 5.7.0.

## [5.4.1] — 2026-06-13

### Changed

- **Project Planner persona** in `system-prompt.md` — added explicit instruction to load the `task-generator` skill when creating new task files, ensuring the template includes the correct `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers for MCP diff injection.

## [5.6.0] — 2026-06-14

### Added

- **Mandatory Project Skill Loading constraint** in `system-prompt.md` — OpenCode must now discover and load all relevant local Agent Skills (e.g., bootstrap, spring-boot, android-kotlin, vue-nuxt) during every task's context phase. Skills are optional per project but if they exist, they MUST be loaded.
- **`SKILL LOADING` instruction** in both the discovery task template and implementation task template `<context_phase>` blocks — ensures framework-specific rules are enforced before exploration and code generation.

### Changed

- `<system_version>` bumped from 5.4.1 to 5.6.0.

## [5.5.0] — 2026-06-08

### Added

- **`user-prompts/` directory** — new folder structure for storing reusable copy-paste prompt templates for the Manager.
- **`user-prompts/session-compactor.md`** — first reusable user prompt template for executing semantic context compaction and cold-start session restoration.
- **Task 08** — local task file tracking the user-prompts directory and compactor implementation.

## [5.4.0] — 2026-06-08

### Added

- **`skill-templates/versioning-and-release/SKILL.md`** — new global Agent Skill template for standardizing Semantic Versioning (SemVer), Keep a Changelog formats, Conventional Commits, and Safe Push Protocols.
- **Task 07** — local task file tracking the release-standards skill implementation.
- **`skill-templates/telegram-issue-sync/SKILL.md`** — new global, optional Agent Skill template for syncing Telegram group topics with local tasks and GitHub issues, featuring advanced non-tagged discussion thread crawling.
- **Task 06** — local task file tracking the synchronization skill implementation.
- **Mandatory Code Documentation constraint** in `system-prompt.md` — OpenCode is now required to write docstrings on all public functions/classes, inline comments on non-obvious logic, and README/header comments for new modules. Enforced via both `<constraints>` and the `<opencode_implementation_task_template>` execution phase.
- **`system_version` tag** added to `system-prompt.md` at version 5.2.0 for tracking system prompt iterations.
- **`skill-templates/doc-coauthoring/SKILL.md`** — Anthropic's doc-coauthoring skill: a structured 3-stage workflow (Context Gathering, Refinement & Structure, Reader Testing) for co-authoring documents with AI.
- **`skill-templates/design-md/SKILL.md`** — Google Labs' design-md skill (extract-design-md): reverse-engineers a DESIGN.md design system document from frontend source code (React, Vue, Svelte, Angular, plain CSS).
- Added a 'Clarification Rule' to the Software Architect persona in system-prompt.md to ensure the AI gracefully handles fragmented, short, or unclear instructions by rephrasing and confirming with the Manager.
- Updated Software Architect persona in `system-prompt.md` to emit intermediate exploration tasks using the custom context MCP when codebase context is missing, preventing hallucinated blueprints.
- Placeholder for upcoming stack additions (see `TODO.md`).
- Updated UI/UX Designer persona in `system-prompt.md` to mandate the creation and maintenance of a `DESIGN.md` file for frontend/mobile projects.
- Added a concrete example of a perfect summary to the `<summary_phase>` in `system-prompt.md` to better guide OpenCode's final output.
- Added Phase 0: Discovery & Onboarding to the execution workflow in `system-prompt.md`. The AI will now actively prompt users for stack/design details on new projects, or analyze code to generate `AGENTS.md` and `DESIGN.md` on existing projects.
- Upgraded the `<agentic_reasoning>` block in `system-prompt.md` to strictly align with Google's official "Agentic workflows System instruction template" (Logical Dependencies, Risk Assessment, Grounding, and Inhibit Response).
- Updated Phase 0 in `system-prompt.md` to explicitly instruct the AI to ask the Manager to import pre-existing Agent Skills from the SOP repository's `skill-templates/` directory.
- Added 6 new Agent Skill templates for Python FastAPI, Go Gin, Vue/Nuxt, React Vite, iOS SwiftUI, and React Native Expo.
- Updated `TODO.md` to reflect completed framework templates and map out the next wave of frameworks (Ruby, PHP, C#, Angular, Flutter).
- **Orchestrator boundaries finalized** — `system-prompt.md` completely rewritten with explicit Brain/Hands separation: Cognitive Lead AI (Gemini 3.5 Flash in AI Studio) is a text-only orchestrator with no file/terminal/network access; OpenCode is the local execution agent. `<role>` updated to state these constraints. `<system_context>` refined to forward time-sensitive queries to OpenCode's local tools. Project Planner gains Onboarding/Discovery and Sync rules. `<constraints>` replaced with profession tone/demeanor rule. Critical tool rules (`apply_patch` pathing, `question` schema) added to `<opencode_protocol>`.
- **`AGENTS.md` Project Context Hub created** — Concise ~40-line `AGENTS.md` written at project root with project overview, setup/dev commands, SOP maintenance rules, do/don't guardrails, and documentation sync rules. Complements the SOP Trilogy as OpenCode's auto-loaded entry point.
- **Global Skills Deployment Guide added to README** — New "Global Skills Deployment" section with step-by-step instructions for installing skills globally via `~/.config/opencode/skills/`. Covers directory creation, skill folder copy, and verification using `/help`.
- **V4.5.0 Schema & Path Conformance** — Phase 0 in `<execution_workflow>` updated to mandate creation/update of `opencode.json` with `"$schema": "https://opencode.ai/config.json"`. System prompt version bumped to V4.5.

## [4.4.0] — System Prompt V4.4 Upgrade — SOP Trilogy

### Added

- **SOP Trilogy concept codified** — Three-tier documentation system for project context management:
  - **`AGENTS.md` (<150 lines)** — Auto-loaded Project Context Hub at project root. Limited to 100–150 lines max to prevent overexploration trap. Every prohibition ("don't") paired with an alternative ("do").
  - **`DESIGN.md` (YAML tokens + prose)** — Google-spec design system file. UI/UX Designer persona now manages lifecycle and validates with `npx @google/design.md lint DESIGN.md`.
  - **`.opencode/skill/<name>/SKILL.md`** — On-demand task-specific toolkits replacing the monolithic `.opencode/skills/` convention. Custom workflows isolated per-task to prevent context bloat.
- **Project Planner persona expanded** — Now owns `AGENTS.md` alongside `STATE.md` and `TODO.md`. Onboarding/Discovery Rule (Phase 0) extended to generate the full SOP Trilogy. Sync Rule now includes `AGENTS.md` and `DESIGN.md` in every task's documentation phase.
- **Software Architect persona updated** — References `.opencode/skill/<name>/SKILL.md` for custom workflow isolation instead of `.opencode/skills/`.
- **UI/UX Designer persona updated** — Gains full `DESIGN.md` lifecycle management, Google-spec compliance, and lint validation command.
- **Code Reviewer persona updated** — Audit scope includes `AGENTS.md` and `DESIGN.md` conventions.
- **State documentation** — `STATE.md` updated to V4.4 architecture with SOP Trilogy entry under Completed Features.

### Changed

- `system-prompt.md` version identifier updated from V4.3 to V4.4.
- File path convention shifted from `.opencode/skills/` to `.opencode/skill/` (singular) for task-specific toolkits.
- `STATE.md` architecture section updated to reflect V4.4 and SOP Trilogy.

## [4.4.1] — Hotfix: Reverted Agent Skills Directory to Plural

### Fixed

- **Directory path reverted** — All `.opencode/skill/` (singular) references in `system-prompt.md` corrected back to `.opencode/skills/` (plural) to restore compatibility with OpenCode's native skill discovery mechanism.
- **Persona path corrections**: Software Architect, UI/UX Designer, Project Planner, and `<opencode_protocol>` documentation phase now reference `.opencode/skills/<name>/SKILL.md` and `.opencode/skills/` respectively.
- **Execution workflow corrected** — Phase 0 Discovery & Onboarding step now directs OpenCode to write skills to `.opencode/skills/` (plural).

## [4.3.0] — Gemini 3.5 Flash Stable Upgrade

### Added

- **`docs/gemini-3.5-flash-guidelines.md`** — Comprehensive prompting guidelines for the Gemini 3.5 Flash runtime: core prompting directives, parameter updates (deprecation of `temperature`/`top_p`/`top_k`; use `thinking_level`), strict function response matching requirements, multimodal/inline instruction patterns, and tool overuse control strategies.
- **`docs/opencode-architecture-reference.md`** — Full OpenCode architecture reference covering: configuration hierarchy and merge order (Remote → Global → Custom path → Per project → `.opencode` → Inline → Managed files → macOS MDM plist), permissions engine with wildcard/negation rules and safety defaults, LSP and formatter auto-detection mapping, agent/subagent types with multi-turn session navigation keybindings, `apply_patch` path marker mechanics, and `question` tool schema.
- **`<system_context>` tag block** in `system-prompt.md` — Informs the model of its January 2025 knowledge cutoff and instructs it to use the current date (2026) for time-sensitive queries.
- **Revised `<agentic_reasoning>` block** — Restructured to align with the Gemini 3.5 Agentic Workflow system instruction template:
  - Logical dependencies and constraints
  - Risk assessment (including tool overuse evaluation)
  - Abductive reasoning and hypothesis exploration
  - Grounding (verified conclusions only)
  - Outcome evaluation
  - Information availability
  - Precision (direct, analytical, no filler)
  - Completeness
  - Inhibit response
- **Output verbosity control rules** in `<constraints>` — Mandates direct, concise, highly analytical responses. Prefers structured formats over prose. Bans conversational filler and overclaiming.
- **Gemini 3.5 Flash runtime constraint** in `<constraints>` — Declares the runtime model and instructs against setting `temperature`/`top_p`/`top_k`; recommends `thinking_level` parameter.
- **Persona `docs/` references** — Software Architect now consults `docs/opencode-architecture-reference.md` for config/permissions/tool mechanics. Senior Programmer consults both `docs/gemini-3.5-flash-guidelines.md` for prompting rules and `docs/opencode-architecture-reference.md` for apply_patch/agent navigation details.
- **State documentation** — `STATE.md` updated to include `docs/` in architecture overview and list V4.3.0 features.

### Changed

- `system-prompt.md` version identifier updated from V4.1 to V4.3.
- `STATE.md` architecture section updated to reflect `docs/` directory and V4.3 completion status.

## [1.0.0] — 2026-05-18

### Added

- Multi-agent system prompt (`system-prompt.md`) — the definitive v3 XML prompt governing all Cognitive Lead AI agents.
- Initial stack SOP directories and rule files:
  - `stacks/backend/nodejs-express.md` — 3-Layer Architecture, centralized error handling, env validation.
  - `stacks/backend/spring-boot.md` — DDD, standard packaging, MapStruct, constructor injection, global exception handlers.
  - `stacks/backend/flask-python.md` — Application Factory, Blueprints, SQLAlchemy, config separation.
  - `stacks/frontend/nextjs.md` — App Router, Server/Client Component separation, Server Actions, Tailwind, a11y.
  - `stacks/mobile/android-kotlin.md` — Jetpack Compose, MVVM, Clean Architecture, Coroutines/Flows, Hilt.
  - `stacks/mobile/android-java-xml.md` — Legacy best practices, MVC/MVP, ViewBinding, lifecycle management, RxJava.
- `README.md` — repository overview and usage guide.
- `AGENTS.md` — rules for OpenCode agents editing this repository.
- `TODO.md` — roadmap for future stack additions.
- `CHANGELOG.md` — this file.
