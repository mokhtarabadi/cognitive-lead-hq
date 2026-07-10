# Task: Enhance Skill Loading Awareness

**Type:** improvement
**Status:** closed

## Goal

Inject a core workflow skills registry into the system prompt and add a comprehensive skills table to the README to enhance AI Orchestrator skill awareness.

## Manager's Notes

- Bump `<system_version>` from `5.12.0` to `5.13.0` in `system-prompt.md`.
- Insert `<core_workflow_skills>` block after `<system_context>` and before `<user_input_processing>`.
- Update `SKILL LOADING` instruction in the implementation task template `<context_phase>`.
- Add `## Available Agent Skills Library` section to `README.md` after `## Global Skills Deployment`.
- Update existing `CHANGELOG.md` `[5.13.0]` entry with new additions/changed items.

## Local TODOs

- [x] Initial codebase exploration
- [x] Create `tasks/23-enhance-skill-loading-awareness.md`
- [x] Update `system-prompt.md`: bump version, add core_workflow_skills block, update SKILL LOADING
- [x] Update `README.md`: add Available Agent Skills Library section with two tables
- [x] Update `CHANGELOG.md`: merge additions into existing 5.13.0 entry
- [x] Run prettier to format modified files
- [x] Write execution log in task file and finalize

## OpenCode Execution Log & Reasoning

_(OpenCode: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

### Architecture & Reasoning

The goal is to make the AI Studio Orchestrator (the Brain) explicitly aware of the general-purpose Agent Skills available to OpenCode (the Hands). Previously, skill loading was only reactive — OpenCode would load stack-specific skills during implementation. This change adds a proactive discovery registry (`<core_workflow_skills>`) directly in the system prompt, listing skills like `debug-instrumentation`, `versioning-and-release`, and `task-generator` so the Orchestrator can instruct OpenCode to load them based on task type (e.g., load `debug-instrumentation` for bug-fixing tasks).

Additionally, the README now has a comprehensive "Available Agent Skills Library" section cataloging all 10 general workflow skills and 13 stack-specific blueprints, making the repository's capabilities discoverable at a glance.

### Files Modified

1. **`system-prompt.md`**
   - Bumped `<system_version>` from `5.12.0` to `5.13.0`
   - Added `<core_workflow_skills>` block with 6 skill entries after `<system_context>` and before `<user_input_processing>`
   - Updated `SKILL LOADING` instruction in `<opencode_implementation_task_template>` `<context_phase>` to reference the new registry

2. **`README.md`**
   - Added `## Available Agent Skills Library` section with two markdown tables:
     - Table 1: General & Workflow Skills (10 skills with descriptions)
     - Table 2: Stack-Specific Blueprints (13 stacks with architecture summaries)

3. **`CHANGELOG.md`**
   - Merged new additions into the existing `[5.13.0] — 2026-06-30` entry under `### Added` and `### Changed`

### Verification

- Ran `npx prettier --write system-prompt.md README.md CHANGELOG.md` — all files formatted successfully.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

````diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 9e213bb..5267056 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -135,16 +135,19 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

 - **`README.md`** — Updated repository tree to feature `go-hexagonal-grpc` and `prompt-refactor` as prominent entries; appended 2 new strategic items to the Future Architectural Roadmap (Automated Prompt Refactoring Pipeline and Hexagonal Architecture Expansion).

-## [5.13.0] — 2026-06-30
+## [5.13.0] — 2026-07-01

 ### Added

 - **`skill-templates/go-hexagonal-grpc/SKILL.md`:** New Agent Skill template for Go Hexagonal Architecture (Ports & Adapters) with gRPC, Uber Fx compile-time DI, Redis caching, and PostgreSQL (pgx/ent). Designed for ultra-low-latency backends like the Caller ID system.
 - **`skill-templates/prompt-refactor/SKILL.md`:** New meta-cognitive Agent Skill template for refactoring basic human prompts into elite, XML-tagged, agent-optimized system instructions with `<role>`, `<system_context>`, `<agentic_reasoning>`, `<constraints>`, and `<output_format>` blocks.
+- **`<core_workflow_skills>` registry** — injected directly into `system-prompt.md` to grant the AI Studio Orchestrator proactive awareness of available workflow tools (like `debug-instrumentation` and `versioning-and-release`).
+- **Comprehensive Agent Skills Library tables** — added to `README.md` detailing both general workflow skills (10 skills) and stack-specific blueprints (13 stacks).

 ### Changed

 - **`skill-templates/android-kotlin/SKILL.md`:** Upgraded from MVVM to strict MVI (Model-View-Intent) with Unidirectional Data Flow. ParsePlatform references replaced with gRPC/Ktor. Offline-First Room caching mandated. Added a complete Kotlin MVI contract example with sealed Intents and reducer-style ViewModel.
+- **Updated `SKILL LOADING` instructions** in task templates to explicitly instruct the Orchestrator to route core workflow skills based on task requirements, consulting the new `<core_workflow_skills>` registry.

 ## [5.12.0] — 2026-06-29

diff --git a/README.md b/README.md
index 88e49a6..85ffdfc 100644
--- a/README.md
+++ b/README.md
@@ -195,6 +195,41 @@ To make the `code-search` skill (or any other reusable skill) available in _ever
    @explore find the main router using the code-search skill
    ```

+## Available Agent Skills Library
+
+### General & Workflow Skills
+
+| Skill Name                | Purpose                                                                                                                                                                 |
+| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
+| `audit-agents`            | Enforces Zero-Autonomous-Commit (ZAC) workflows and generates/audits `AGENTS.md` for new and existing projects.                                                         |
+| `code-search`             | Mandatory for discovery. Uses MCP tools (`get_directory_tree`, `read_source_files`, `extract_signatures`) to explore the codebase without token bloat.                  |
+| `debug-instrumentation`   | Diagnoses complex runtime bugs, deadlocks, race conditions, and silent failures via strategic temporary logging and tracing.                                            |
+| `design-md`               | Extracts a comprehensive design system (`DESIGN.md`) directly from frontend source code — React, Vue, Svelte, Angular, plain HTML/CSS, or any web framework.            |
+| `doc-coauthoring`         | Guides users through a structured 3-stage workflow (Context Gathering, Refinement & Structure, Reader Testing) for co-authoring documentation with AI.                  |
+| `prompt-refactor`         | Meta-cognitive skill that refactors basic human prompts into elite, highly constrained, XML-tagged instructions optimized for AI agent reasoning.                       |
+| `task-generator`          | Automatically generates decentralized task files based on Manager instructions, with correct `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.               |
+| `telegram-issue-sync`     | Syncs Telegram supergroup topics into local task files and GitHub issues, using embedded Python scripts for deterministic JSON state management.                        |
+| `telegram-message-export` | Intelligently exports a range of Telegram messages (text, media, voice notes) into a numbered folder, capturing reply hierarchies, and packing them into a ZIP archive. |
+| `versioning-and-release`  | Standardizes Semantic Versioning (SemVer), Keep a Changelog formats, Conventional Commits, and Safe Push Protocols across all repositories.                             |
+
+### Stack-Specific Blueprints
+
+| Stack             | Architecture Enforced                                                                                      |
+| ----------------- | ---------------------------------------------------------------------------------------------------------- |
+| Android Java      | MVC/MVP with ViewBinding, lifecycle management, and RxJava for legacy Android development.                 |
+| Android Kotlin    | Jetpack Compose, MVI (Unidirectional Data Flow), Clean Architecture, Offline-First Room, and Hilt DI.      |
+| Flask Python      | Application Factory, Blueprints, SQLAlchemy, and config separation for modular Flask applications.         |
+| Go Gin            | Idiomatic Go, Clean Architecture layers, and Gin routing best practices for RESTful services.              |
+| Go Hexagonal gRPC | Hexagonal Architecture (Ports and Adapters), gRPC, Uber Fx compile-time DI, Redis caching, and PostgreSQL. |
+| iOS SwiftUI       | SwiftUI, MVVM, and modern iOS app architecture with declarative UI patterns.                               |
+| Next.js           | App Router, Server/Client Component separation, Server Actions, and Tailwind CSS design tokens.            |
+| Node.js Express   | 3-Layer Architecture (Controller/Service/Repository), centralized error handling, and env validation.      |
+| Python FastAPI    | Pydantic schemas, dependency injection, async routing, and layered service architecture.                   |
+| React Native Expo | Expo Router, React Native components, and cross-platform UI with native module support.                    |
+| React Vite        | React 18+ SPA architecture, hooks, and Vite configuration with optimized build tooling.                    |
+| Spring Boot       | DDD, hexagonal-style packaging, MapStruct, constructor injection, and global exception handlers.           |
+| Vue Nuxt          | Vue 3 Composition API, Nuxt 3 routing, and Pinia state management.                                         |
+
 ## Key V5 Changes

 - **Decentralized task architecture** — global `STATE.md` and `TODO.md` replaced by isolated task files in `tasks/` directory.
diff --git a/system-prompt.md b/system-prompt.md
index e137c8c..db58685 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>5.12.0</system_version>
+<system_version>5.13.0</system_version>

 <role>
 You are the Cognitive Lead AI running inside Google AI Studio (powered by Gemini), acting as an elite software agency orchestrator.
@@ -13,6 +13,17 @@ Your knowledge cutoff date is January 2025. Remember it is 2026 this year.
 For time-sensitive queries that require up-to-date information, you must instruct OpenCode to use its websearch/webfetch tools locally.
 </system_context>

+<core_workflow_skills>
+The following general-purpose Agent Skills are available. You MUST instruct OpenCode to load them via the `skill` tool when their specific capabilities are required for a task:
+
+- **code-search**: Mandatory for discovery. Uses MCP tools (`get_directory_tree`, `read_source_files`, `extract_signatures`) to explore the codebase without token bloat.
+- **task-generator**: Mandatory for creating new task files in `tasks/` with correct Git Diff injection markers.
+- **audit-agents**: Enforces Zero-Autonomous-Commit (ZAC) workflows and generates/audits `AGENTS.md`.
+- **versioning-and-release**: Standardizes SemVer, Keep a Changelog updates, and Conventional Commits.
+- **debug-instrumentation**: Diagnoses complex runtime bugs, deadlocks, and race conditions via strategic temporary logging.
+- **prompt-refactor**: Meta-cognitive skill that refactors weak human prompts into elite, XML-tagged system instructions.
+  </core_workflow_skills>
+
 <user_input_processing>
 CRITICAL INSTRUCTION: The Manager will often send informal, raw text. Before taking any action or planning, you MUST execute this processing step internally:

@@ -103,7 +114,7 @@ You are a very strong reasoner and planner. Before taking any action (either gen
 <opencode_implementation_task>
   <context_phase>
     OPENCODE INSTRUCTION: Read the active task file in `tasks/` to understand the current goals. Use your native tools (`read`, `glob`, `skill`) to gain context. If the task is massive, delegate exploration to the `@explore` subagent first. Utilize any configured MCP servers if external context is required.
-    SKILL LOADING: Before implementing, load every available skill matching the project's tech stack (e.g., android-kotlin, spring-boot, react-vite, nodejs-express, python-fastapi). A project may have zero or multiple skills — if a relevant skill exists, it MUST be loaded. If the task involves creating a new task file, also load the `task-generator` skill. This ensures framework-specific conventions and architectural rules are enforced during implementation.
+    SKILL LOADING: Before implementing, load every available skill matching the project's tech stack (e.g., android-kotlin, spring-boot, react-vite, nodejs-express, python-fastapi). Additionally, consult the <core_workflow_skills> registry and load any general-purpose skills required for this specific task (e.g., debug-instrumentation for bug fixes, versioning-and-release for publishing). If the task involves creating a new task file, load the task-generator skill. A project may have zero or multiple skills — if a relevant skill exists, it MUST be loaded. This ensures framework-specific conventions and architectural rules are enforced during implementation.
   </context_phase>

   <execution_phase>
````

<!-- END_GIT_DIFF -->
