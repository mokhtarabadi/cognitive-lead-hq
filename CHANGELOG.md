# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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

## [Unreleased]

### Added

- Placeholder for upcoming changes.

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
