# Task: Prettier Format All Markdown Files

**File:** `tasks/30-prettier-format-all-markdown.md`
**Type:** improvement
**Status:** open

## Goal

Run `npx prettier --write "**/*.md"` across the entire repository to enforce consistent markdown formatting — proper blank-line spacing around headings, consistent list indentation, correct code-fence formatting, and trailing newlines.

## Manager's Notes

Triggered by manual request to format all `.md` files. No structural or semantic content changes — only whitespace/formatting normalization.

## Local TODOs

- [x] Load relevant skills (sop-maintenance, task-generator, audit-agents)
- [x] Explore project tree
- [x] Run `npx prettier --write "**/*.md"`
- [x] Inspect `git diff` to verify changes
- [x] Create task file

## OpenCode Execution Log & Reasoning

This was a straightforward formatting pass. Prettier (v3.9.5) was installed on-the-fly via npx and applied to all 46 `.md` files. Most files were already compliant; ~10 skill-template files and a handful of task files received minor whitespace fixes (blank lines after headings, consistent list spacing, code-fence normalization). Task 29's embedded `<!-- BEGIN_GIT_DIFF -->

````diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 216eff0..2755634 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -12,6 +12,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

 ### Changed

+- **Bulk Prettier Format:** Ran `npx prettier --write "**/*.md"` across all 46 markdown files to enforce consistent formatting — blank-line spacing, list indentation, code-fence normalization, and trailing newlines.
 - **Android Kotlin Template Overhaul:** `skill-templates/android-kotlin/SKILL.md` completely rewritten with strict XML ban, Hilt DI mandate, compile-time safe DB (SQLDelight/Room), and enhanced null-safety rules.
 - **React Native Expo Template Overhaul:** `skill-templates/react-native-expo/SKILL.md` rewritten with Expo Managed Workflow enforcement, ban on native folder edits, mandatory NativeWind, and strict TypeScript requirement.
 - **README.md:** Updated Stack-Specific Blueprints table to reflect removed and added templates; strengthened Android Kotlin and React Native Expo descriptions with zero-hallucination rules.
diff --git a/README.md b/README.md
index 50cf217..fc33989 100644
--- a/README.md
+++ b/README.md
@@ -14,7 +14,7 @@ This repository is the **V5 evolution** of the Cognitive Lead AI multi-agent sys
 | ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
 | `system-prompt.md`                          | At the start of every session; this is the V5 multi-agent prompt defining all 5 personas and the Agentic Reasoning matrix. |
 | `.opencode/skills/sop-maintenance/SKILL.md` | When an AI agent needs to modify this repository itself.                                                                   |
-| `skill-templates/*/SKILL.md`                | Before writing code in a specific stack (Spring Boot, Flask, Next.js, NestJS, Android Kotlin).                            |
+| `skill-templates/*/SKILL.md`                | Before writing code in a specific stack (Spring Boot, Flask, Next.js, NestJS, Android Kotlin).                             |
 | `CHANGELOG.md`                              | To review what has changed between versions.                                                                               |
 | `tasks/`                                    | To see the active task files and current work items.                                                                       |

@@ -225,20 +225,20 @@ To make the `code-search` skill (or any other reusable skill) available in _ever

 ### Stack-Specific Blueprints

-| Stack                   | Architecture Enforced                                                                                      |
-| ----------------------- | ---------------------------------------------------------------------------------------------------------- |
-| Android Kotlin          | **100% Jetpack Compose — XML Strictly Banned.** MVI (UDF), Hilt, SQLDelight/Room.                           |
-| Flask Python            | Application Factory, Blueprints, SQLAlchemy, and config separation for modular Flask applications.         |
-| Go Gin                  | Idiomatic Go, Clean Architecture layers, and Gin routing best practices for RESTful services.              |
-| Go Hexagonal gRPC       | Hexagonal Architecture (Ports and Adapters), gRPC, Uber Fx compile-time DI, Redis caching, and PostgreSQL. |
-| iOS SwiftUI             | SwiftUI, MVVM, and modern iOS app architecture with declarative UI patterns.                               |
-| NestJS Prisma Vertical  | NestJS, Prisma ORM, Vertical Slice Architecture, strict TypeScript, and class-validator DTOs.              |
-| Next.js                 | App Router, Server/Client Component separation, Server Actions, and Tailwind CSS design tokens.            |
-| Python FastAPI          | Pydantic schemas, dependency injection, async routing, and layered service architecture.                    |
-| React Native Expo       | **Expo Managed Workflow ONLY — no native folders.** Expo Router, NativeWind, Zustand, strict TypeScript.   |
-| React Vite              | React 18+ SPA architecture, hooks, and Vite configuration with optimized build tooling.                    |
-| Spring Boot             | DDD, hexagonal-style packaging, MapStruct, constructor injection, and global exception handlers.           |
-| Vue Nuxt                | Vue 3 Composition API, Nuxt 3 routing, and Pinia state management.                                         |
+| Stack                  | Architecture Enforced                                                                                      |
+| ---------------------- | ---------------------------------------------------------------------------------------------------------- |
+| Android Kotlin         | **100% Jetpack Compose — XML Strictly Banned.** MVI (UDF), Hilt, SQLDelight/Room.                          |
+| Flask Python           | Application Factory, Blueprints, SQLAlchemy, and config separation for modular Flask applications.         |
+| Go Gin                 | Idiomatic Go, Clean Architecture layers, and Gin routing best practices for RESTful services.              |
+| Go Hexagonal gRPC      | Hexagonal Architecture (Ports and Adapters), gRPC, Uber Fx compile-time DI, Redis caching, and PostgreSQL. |
+| iOS SwiftUI            | SwiftUI, MVVM, and modern iOS app architecture with declarative UI patterns.                               |
+| NestJS Prisma Vertical | NestJS, Prisma ORM, Vertical Slice Architecture, strict TypeScript, and class-validator DTOs.              |
+| Next.js                | App Router, Server/Client Component separation, Server Actions, and Tailwind CSS design tokens.            |
+| Python FastAPI         | Pydantic schemas, dependency injection, async routing, and layered service architecture.                   |
+| React Native Expo      | **Expo Managed Workflow ONLY — no native folders.** Expo Router, NativeWind, Zustand, strict TypeScript.   |
+| React Vite             | React 18+ SPA architecture, hooks, and Vite configuration with optimized build tooling.                    |
+| Spring Boot            | DDD, hexagonal-style packaging, MapStruct, constructor injection, and global exception handlers.           |
+| Vue Nuxt               | Vue 3 Composition API, Nuxt 3 routing, and Pinia state management.                                         |

 ## Key V5 Changes

diff --git a/skill-templates/android-kotlin/SKILL.md b/skill-templates/android-kotlin/SKILL.md
index 2011776..3d4bceb 100644
--- a/skill-templates/android-kotlin/SKILL.md
+++ b/skill-templates/android-kotlin/SKILL.md
@@ -48,4 +48,4 @@ Hilt is mandatory. Do not write manual dependency factories.
 | --------------- | -------------------------- | ----------------------------- |
 | Use cases       | Unit                       | JUnit 5 + MockK               |
 | ViewModel (MVI) | Unit (Intent injection)    | JUnit 5 + Turbine (for Flows) |
-| UI / Composable | Snapshot / Compose UI Test | Compose Test                  |
\ No newline at end of file
+| UI / Composable | Snapshot / Compose UI Test | Compose Test                  |
diff --git a/skill-templates/nestjs-prisma-vertical/SKILL.md b/skill-templates/nestjs-prisma-vertical/SKILL.md
index 860318a..65db3f2 100644
--- a/skill-templates/nestjs-prisma-vertical/SKILL.md
+++ b/skill-templates/nestjs-prisma-vertical/SKILL.md
@@ -40,12 +40,12 @@ src/

 ## Naming Conventions

-| Artifact          | Convention                 | Example               |
-| ----------------- | -------------------------- | --------------------- |
-| Files             | `kebab-case` with type     | `auth.controller.ts`  |
-| Classes           | `PascalCase`               | `AuthController`      |
-| Methods/Variables | `camelCase`                | `registerUser`        |
-| Prisma Models     | `PascalCase` (Singular)    | `model User`          |
+| Artifact          | Convention              | Example              |
+| ----------------- | ----------------------- | -------------------- |
+| Files             | `kebab-case` with type  | `auth.controller.ts` |
+| Classes           | `PascalCase`            | `AuthController`     |
+| Methods/Variables | `camelCase`             | `registerUser`       |
+| Prisma Models     | `PascalCase` (Singular) | `model User`         |

 ## Architectural Patterns

@@ -53,6 +53,7 @@ src/
 Use NestJS constructor injection exclusively.

 **Prisma Workflow:**
+
 1. Modify `prisma/schema.prisma`.
 2. Never write migrations manually. Use CLI commands to generate them.
 3. Inject `PrismaService` into feature services to interact with the DB. The LSP will guide you with exact types.
@@ -62,8 +63,8 @@ Do not use inline `try/catch` for standard HTTP errors. Throw NestJS exceptions

 ## Testing Strategies

-| Layer            | Test Type   | Framework                 | File Naming                 |
-| ---------------- | ----------- | ------------------------- | --------------------------- |
-| Feature Service  | Unit        | Jest + Mock Prisma      | `auth.service.spec.ts`      |
-| Controller       | Unit        | Jest                      | `auth.controller.spec.ts`   |
-| Feature Endpoint | E2E         | Jest + Supertest + TestDB | `auth.e2e-spec.ts`          |
\ No newline at end of file
+| Layer            | Test Type | Framework                 | File Naming               |
+| ---------------- | --------- | ------------------------- | ------------------------- |
+| Feature Service  | Unit      | Jest + Mock Prisma        | `auth.service.spec.ts`    |
+| Controller       | Unit      | Jest                      | `auth.controller.spec.ts` |
+| Feature Endpoint | E2E       | Jest + Supertest + TestDB | `auth.e2e-spec.ts`        |
diff --git a/skill-templates/react-native-expo/SKILL.md b/skill-templates/react-native-expo/SKILL.md
index 46c74b6..30971bc 100644
--- a/skill-templates/react-native-expo/SKILL.md
+++ b/skill-templates/react-native-expo/SKILL.md
@@ -44,4 +44,4 @@ project/
 ## Testing Strategies

 - **Framework**: `Jest` + `@testing-library/react-native`.
-- **Approach**: Test component rendering and user interactions natively.
\ No newline at end of file
+- **Approach**: Test component rendering and user interactions natively.
diff --git a/skill-templates/task-generator/SKILL.md b/skill-templates/task-generator/SKILL.md
index 2b1a57b..98c3e4b 100644
--- a/skill-templates/task-generator/SKILL.md
+++ b/skill-templates/task-generator/SKILL.md
@@ -14,12 +14,12 @@ You are the Task Generator. Your job is to create structured task files for the
 3. **Name:** Create a kebab-case filename (e.g., `01-fix-login-bug.md`).
 4. **Generate File:** Write the following template to the new file:

-    ```markdown
-    # Task: [Task Name]
+   ```markdown
+   # Task: [Task Name]

-    **File:** `tasks/[filename]`
-    **Type:** [bug|improvement|feature]
-    **Status:** open
+   **File:** `tasks/[filename]`
+   **Type:** [bug|improvement|feature]
+   **Status:** open

    ## Goal

diff --git a/system-prompt.md b/system-prompt.md
index 740038f..0d1018f 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>5.16.0</system_version>
+<system_version>5.18.0</system_version>

 <role>
 You are the Cognitive Lead AI running inside Google AI Studio (powered by Gemini), acting as an elite software agency orchestrator.
@@ -13,8 +13,10 @@ Your knowledge cutoff date is January 2025. Remember it is 2026 this year.
 For time-sensitive queries that require up-to-date information, you must instruct OpenCode to use its websearch/webfetch tools locally.
 </system_context>

-<core_workflow_skills>
-The following general-purpose Agent Skills are available. You MUST instruct OpenCode to load them via the `skill` tool when their specific capabilities are required for a task:
+<agent_skills_registry>
+The following Agent Skills are available. You MUST intelligently instruct OpenCode to load them via the `skill` tool when their specific capabilities or tech stack matches the project:
+
+**Global Workflow Skills:**

 - **code-search**: Mandatory for discovery. Uses MCP tools (`get_directory_tree`, `read_source_files`, `extract_signatures`) to explore the codebase without token bloat.
 - **task-generator**: Mandatory for creating new task files in `tasks/` with correct Git Diff injection markers.
@@ -22,7 +24,26 @@ The following general-purpose Agent Skills are available. You MUST instruct Open
 - **versioning-and-release**: Standardizes SemVer, Keep a Changelog updates, and Conventional Commits.
 - **debug-instrumentation**: Diagnoses complex runtime bugs, deadlocks, and race conditions via strategic temporary logging.
 - **prompt-refactor**: Meta-cognitive skill that refactors weak human prompts into elite, XML-tagged system instructions.
-  </core_workflow_skills>
+- **telegram-issue-sync**: Syncs Telegram supergroup topics into local task files and GitHub issues.
+- **telegram-message-export**: Intelligently exports Telegram messages (text, media) into a numbered folder and ZIP archive.
+- **design-md**: Extracts a comprehensive design system (`DESIGN.md`) directly from frontend source code.
+- **doc-coauthoring**: Guides users through a structured 3-stage workflow for co-authoring documentation.
+
+**Stack-Specific Blueprints (Load if matching the project):**
+
+- **android-kotlin**: 100% Jetpack Compose, MVI (UDF), Hilt, SQLDelight/Room. XML Strictly Banned.
+- **flask-python**: Application Factory, Blueprints, SQLAlchemy, and config separation.
+- **go-gin**: Idiomatic Go, Clean Architecture layers, Gin routing.
+- **go-hexagonal-grpc**: Hexagonal Architecture, gRPC, Uber Fx compile-time DI, Redis, PostgreSQL.
+- **ios-swiftui**: SwiftUI, MVVM, modern iOS app architecture.
+- **nestjs-prisma-vertical**: NestJS, Prisma ORM, Vertical Slice Architecture, strict TypeScript.
+- **nextjs**: App Router, Server/Client Component separation, Server Actions, Tailwind CSS.
+- **python-fastapi**: Pydantic V2 schemas, dependency injection, async routing.
+- **react-native-expo**: Expo Managed Workflow ONLY, Expo Router, NativeWind, Zustand.
+- **react-vite**: React 18+ SPA architecture, hooks, Vite configuration.
+- **spring-boot**: DDD, hexagonal-style packaging, MapStruct, constructor injection.
+- **vue-nuxt**: Vue 3 Composition API, Nuxt 3 routing, Pinia state management.
+  </agent_skills_registry>

 <user_input_processing>
 CRITICAL INSTRUCTION: The Manager will often send informal, raw text. Before taking any action or planning, you MUST execute this processing step internally:
@@ -132,7 +153,7 @@ You are a very strong reasoner and planner. Before taking any action (either gen

   <context_phase>
     OPENCODE INSTRUCTION: Read the active task file in `tasks/` to understand the current goals. Use your native tools (`read`, `glob`, `skill`) to gain context. If the task is massive, delegate exploration to the `@explore` subagent first. Utilize any configured MCP servers if external context is required.
-    SKILL LOADING: Before implementing, load every available skill matching the project's tech stack (e.g., android-kotlin, spring-boot, react-vite, nodejs-express, python-fastapi). Additionally, consult the <core_workflow_skills> registry and load any general-purpose skills required for this specific task (e.g., debug-instrumentation for bug fixes, versioning-and-release for publishing). If the task involves creating a new task file, load the task-generator skill. A project may have zero or multiple skills — if a relevant skill exists, it MUST be loaded. This ensures framework-specific conventions and architectural rules are enforced during implementation.
+    SKILL LOADING: Before implementing, load every available skill matching the project's tech stack (e.g., android-kotlin, spring-boot, react-vite, nodejs-express, python-fastapi). Additionally, consult the <agent_skills_registry> registry and load any general-purpose skills required for this specific task (e.g., debug-instrumentation for bug fixes, versioning-and-release for publishing). If the task involves creating a new task file, load the task-generator skill. A project may have zero or multiple skills — if a relevant skill exists, it MUST be loaded. This ensures framework-specific conventions and architectural rules are enforced during implementation.
   </context_phase>

   <execution_phase>
@@ -142,7 +163,7 @@ You are a very strong reasoner and planner. Before taking any action (either gen
     0. **Rule Validation & Halt Protocol:** Before writing any code, cross-check these instructions against AGENTS.md, DESIGN.md, and loaded SKILL files. If the Orchestrator's instructions violate ANY project rules or architectural constraints, you MUST HALT immediately. Do NOT run any bash commands. Output a `⚠️ RULE VIOLATION WARNING` detailing exactly which rule was broken so the Orchestrator can self-correct.
     1. If applying file patches, utilize the `apply_patch` tool with embedded path markers (e.g., `*** Update File: <path>`).
     2. If user feedback is required, utilize the `question` tool with multi-option schemas.
-    3. **Documentation Rule:** You MUST write docstrings on all public functions/classes, inline comments on non-obvious logic, and a brief README or header comment for any new module. See `<constraints>` for the full mandate.]
+    3. **Documentation Rule:** You MUST write maximum docstrings on all public functions/classes, verbose inline comments on non-obvious logic, and a brief README or header comment for any new module. See `<constraints>` for the full mandate.]
   </execution_phase>

   <bash_phase>
@@ -174,7 +195,7 @@ You are a very strong reasoner and planner. Before taking any action (either gen
 During Phase 0, the Planner will launch up to 4 parallel subagent tasks to deeply scan files and concurrently generate `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` to avoid style and structure misalignment.

 1. **Input Processing & Clarification**: Analyze the Manager's raw input. Clean syntax, interpret context. IF ambiguous, HALT and ask clarifying questions. IF clear, proceed.
-2. **Plan & Review Loop (Architect & UI/UX)**: Analyze request -> Deliver blueprint -> Ask Manager for approval. If the Manager provides inline feedback using the `> 📝 **MANAGER REVIEW:**` syntax or direct text edits, resolve the feedback and output a revised blueprint. Loop this step until explicit approval is received.
+2. **Plan & Review Loop (Architect & UI/UX)**: Analyze request -> Deliver blueprint strictly formatted in clean Markdown (NO XML). Ask Manager for approval and COMPLETELY STOP. Do NOT generate any implementation task blocks. If the Manager provides inline feedback using the `> 📝 **MANAGER REVIEW:**` syntax or direct text edits, resolve the feedback and output a revised blueprint. Loop this step until explicit approval is received.
 3. **Implement & Inject (Programmer)**: Wait for the explicit "Approved" signal -> generate the `<opencode_implementation_task>` block. OpenCode executes, stages via MCP tool (NO COMMITS), and outputs Task Summary.
 4. **Team Review (Reviewer)**: Manager passes OpenCode's completed task file back. Review against the factual Git Diff.
 5. **Fix Loop (Programmer)**: If rejected, generate a subsequent task to fix the implementation. Loop back to step 3.
@@ -183,17 +204,16 @@ During Phase 0, the Planner will launch up to 4 parallel subagent tasks to deepl

 <constraints>
 - **Cognitive Language Rule:** All internal reasoning, architectural blueprints, XML task generation, and OpenCode execution logs MUST always be written in English. You may only use a localized language for direct conversational responses to the Manager if explicitly requested.
-- **Strict Approval Gate & Inline Review Pattern:** You MUST NOT generate any `<opencode_implementation_task>` blocks until the Manager explicitly approves the architectural plan or blueprint. The Manager will provide feedback directly inside Markdown files using `> 📝 **MANAGER REVIEW:**` blockquotes or standard markdown strikethrough/bold edits. You must process this feedback, revise the plan, and ask for approval again, looping until a final "Approved" is received.
+- **Strict Approval Gate & Markdown Plans:** You MUST NOT generate any `<opencode_implementation_task>` blocks until the Manager explicitly approves the architectural plan or blueprint. All architectural plans MUST be written in clean, human-readable Markdown. You are STRICTLY FORBIDDEN from using XML tags for your plans. You must present the Markdown plan, ask for approval, and completely STOP generating text. The Manager will provide feedback directly inside Markdown files using `> 📝 **MANAGER REVIEW:**` blockquotes or standard markdown strikethrough/bold edits. You must process this feedback, revise the plan, and ask for approval again, looping until a final "Approved" is received.
 - **Template Preservation Rule:** When generating the `<summary_phase>`, you MUST output the literal placeholder tags (e.g. `<OpenCode: Describe the features...>`). DO NOT pre-fill the summary.
 - **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`.
 - **Tone and Demeanor**: Keep your responses highly professional, objective, and analytical. Do not use superlatives.
-- **Mandatory Code Documentation:** For every implementation task that involves complex logic, non-trivial algorithms, public APIs, data transformations, configuration, or any code a teammate would need to understand to maintain or extend — you MUST instruct OpenCode to write:
-  1. **Docstrings/comments** explaining the "why" (not the "what") — intent, edge cases, assumptions, and trade-offs — following the language's idiomatic docstring format (JSDoc, Javadoc, Pydoc, etc.).
-  2. **Inline comments** on non-obvious blocks (e.g., regex patterns, state mutations, performance optimizations, error-recovery paths).
-  3. **README or internal docs** when the task adds a new module, endpoint, public API, or changes architecture. A single sentence describing purpose, usage, and constraints suffices.
-  Be specific in the `<execution_phase>` about which files need documentation and at what level (module docs, function docs, inline). The default expectation is: **every public function/class gets a docstring; every complex block gets a comment; every new module gets a brief README or header comment.**
+- **Maximum AI-Assistive Code Documentation:** Because this codebase is maintained by AI agents (OpenCode, Cursor), robust code comments are not clutter—they are critical semantic anchors for the LLMs. For every implementation task, you MUST explicitly instruct OpenCode to write the MAXIMUM possible documentation:
+  1. **Comprehensive Docstrings** on *every* public function, class, and interface explaining the "why", inputs, edge cases, and assumptions.
+  2. **Verbose Inline Comments** before *every* major logical step, conditional branch, or state mutation.
+  3. **READMEs / Header Comments** for any new module or architectural change.
 - **Workspace Security:** OpenCode is STRICTLY FORBIDDEN from executing terminal commands that modify files outside the current project workspace. Destructive commands (like `rm -rf`) must ONLY target specific, known auto-generated directories (e.g., `dist/`, `build/`, `target/`).
-- **Mandatory Project Skill Loading:** During every task's context phase, OpenCode MUST discover and load all Agent Skills relevant to the project. Load every skill matching the project's tech stack (e.g., android-kotlin, spring-boot, react-vite, nodejs-express, python-fastapi) or workflow needs (e.g., `task-generator` for task creation). A project may have zero, one, or multiple skills — if a skill exists, it MUST be loaded. This ensures framework-specific rules, naming conventions, and architectural patterns are always enforced.
+- **Mandatory Project Skill Loading:** During every task's context phase, OpenCode MUST load all Agent Skills relevant to the project from the `<agent_skills_registry>`. Load every global workflow skill needed for the task, and explicitly load the stack-specific blueprint matching the project. A project may have zero, one, or multiple skills — if a skill exists, it MUST be loaded to ensure framework-specific rules and architectural patterns are always enforced.
 </constraints>

 <initialization>
````

<!-- END_GIT_DIFF -->
