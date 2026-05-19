# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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

## [Unreleased]

### Added

- Added a 'Clarification Rule' to the Software Architect persona in system-prompt.md to ensure the AI gracefully handles fragmented, short, or unclear instructions by rephrasing and confirming with the Manager.
- Placeholder for upcoming stack additions (see `TODO.md`).
- Updated UI/UX Designer persona in `system-prompt.md` to mandate the creation and maintenance of a `DESIGN.md` file for frontend/mobile projects.
- Added a concrete example of a perfect summary to the `<summary_phase>` in `system-prompt.md` to better guide OpenCode's final output.
- Added Phase 0: Discovery & Onboarding to the execution workflow in `system-prompt.md`. The AI will now actively prompt users for stack/design details on new projects, or analyze code to generate `AGENTS.md` and `DESIGN.md` on existing projects.
- Upgraded the `<agentic_reasoning>` block in `system-prompt.md` to strictly align with Google's official "Agentic workflows System instruction template" (Logical Dependencies, Risk Assessment, Grounding, and Inhibit Response).
- Updated Phase 0 in `system-prompt.md` to explicitly instruct the AI to ask the Manager to import pre-existing Agent Skills from the SOP repository's `skill-templates/` directory.
- Added 6 new Agent Skill templates for Python FastAPI, Go Gin, Vue/Nuxt, React Vite, iOS SwiftUI, and React Native Expo.
- Updated `TODO.md` to reflect completed framework templates and map out the next wave of frameworks (Ruby, PHP, C#, Angular, Flutter).

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
