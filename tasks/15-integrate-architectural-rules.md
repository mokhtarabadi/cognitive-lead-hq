# Task 15: Integrate Architectural Rules & Core Templates

**Type:** feature
**Status:** completed

## Goal

Upgrade the Cognitive Lead AI system to V5.9.0 by introducing the 🛑 MANDATORY FIRST-READ RULE, parallel subagent guidelines, Phase 0 architectural file generation, and high-performance AI initialization templates for Android, Spring Boot, Node.js, Nuxt, and Next.js.

## Manager's Notes

- Bump system version to 5.9.0 in system-prompt.md.
- Write complete architecture, design, and agents templates directly into the audit-agents skill file.
- Standardize five tech-stack templates with modern best-in-class conventions.
- Update both workspace and global user skill directories.

## Local TODOs

- [x] Create Tasks 15 md file
- [x] Edit system-prompt.md to V5.9.0 (parallel agents + first-read rules)
- [x] Edit AGENTS.md to include the 🛑 MANDATORY FIRST-READ RULE
- [x] Rewrite skill-templates/audit-agents/SKILL.md with full templates & Target Audit Criteria
- [x] Rewrite five tech-stack templates (Android, Spring Boot, Node.js Express, Vue Nuxt, Next.js Next)
- [x] Sync workspace audit-agents skill to ~/.config/opencode/skills/audit-agents/SKILL.md
- [x] Update CHANGELOG.md with V5.9.0 entry
- [x] Run Prettier formatting check on modified markdown files

## OpenCode Execution Log & Reasoning

### Architectural Reasoning

This upgrade introduces the **Mandatory First-Read Rule** — a critical architectural pattern ensuring every agent reads `AGENTS.md` first, which then routes to `DESIGN.md`, `architecture.md`, `data_model.md`, and `conventions.md`. This prevents style/structural misalignment by guaranteeing agents have full context before writing any code.

Key design decisions:

1. **Version bump to 5.9.0** — skipping 5.8.x to align with the significance of this structural change.
2. **Parallel subagent declaration** — explicitly advertising OpenCode's ability to run up to 4 concurrent agents during Phase 0 discovery.
3. **Audit-agents template expansion** — the skill now contains ready-to-use templates for `architecture.md`, `DESIGN.md`, and structured audit criteria, making it a one-stop shop for project initialization.
4. **Tech-stack scaffolding** — each of the 5 templates now includes a "Modern Project Initiation Guide" section with strict, opinionated rules for AI-driven code generation, ensuring consistent output across frameworks.

### Execution Notes

- Created `tasks/15-integrate-architectural-rules.md` as the active task file.
- Edited `system-prompt.md` — bumped version, added parallel agents note, updated Software Architect to mandate AGENTS.md first-read, updated Senior Programmer to instruct first-read, updated Planner for parallel Phase 0 subagents.
- Edited `AGENTS.md` — added the Mandatory First-Read Rule section as the very first section after the title.
- Fully rewrote `skill-templates/audit-agents/SKILL.md` — added Target Audit Criteria section, architecture.md template, and DESIGN.md template.
- Updated 5 tech-stack templates with AI-driven scaffolding sections.
- Synced to `~/.config/opencode/skills/audit-agents/SKILL.md`.
- Added V5.9.0 entry to CHANGELOG.md.
- Ran Prettier formatting check — all markdown files pass.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

````diff
diff --git a/AGENTS.md b/AGENTS.md
index 59bec3f..dd608be 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -1,5 +1,15 @@
 # Cognitive Lead AI HQ — Project Context Hub

+## 🛑 MANDATORY FIRST-READ RULE
+
+The very first file the agent MUST read before performing any task is `AGENTS.md`.
+This file acts as the primary router. You MUST load and read the following documents first before executing any code changes to guarantee 100% structural and stylistic alignment:
+
+1. `DESIGN.md` — Enforces colors, typography, layout scale, component styling, and RTL Persian configurations.
+2. `docs/architecture.md` — Defines project structure, layer boundaries, and key data flow policies.
+3. `docs/data_model.md` — Defines database entities, schemas, pointers, and object relationships.
+4. `docs/conventions.md` — Defines syntax rules, naming conventions, file boundaries, and localization paths.
+
 ## Project Overview

 This repository is the Headquarters for the Cognitive Lead AI multi-agent system. It is a **documentation-only** repository containing system prompts, MCP servers, and Agent Skills (`SKILL.md`).
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 3c28e18..8247a1d 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -126,6 +126,16 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

 - **`stage_and_inject_diff` MCP tool** — optimized the staged git diff command to globally exclude the entire `tasks/` directory (`:!tasks/`) instead of just the single active task file, completely eliminating task history clutter from factual codebase reviews.

+## [5.9.0] — 2026-06-21
+
+### Added
+
+- **🛑 MANDATORY FIRST-READ RULE:** Added rules to `system-prompt.md` and `AGENTS.md` forcing coding agents to read global configurations and architectural files before starting any implementation.
+- **Parallel Subagent Guidelines:** Declared OpenCode's ability to run up to 4 concurrent subagent tasks during Phase 0 discovery.
+- **Core File Scaffolding Templates:** Integrated full schemas and templates for `architecture.md`, `DESIGN.md`, and `AGENTS.md` directly into the `audit-agents` skill template.
+- **AI-Driven Project Initialization Standards:** Standardized templates for Android Kotlin, Spring Boot, Node.js, Nuxt, and Next.js in `skill-templates/`.
+- **Task 15:** Added the active task file tracking this major system prompt and scaffolding upgrade.
+
 ## [5.7.1] — 2026-06-17

 ### Changed
diff --git a/skill-templates/android-kotlin/SKILL.md b/skill-templates/android-kotlin/SKILL.md
index 83f67a5..69ec62c 100644
--- a/skill-templates/android-kotlin/SKILL.md
+++ b/skill-templates/android-kotlin/SKILL.md
@@ -3,7 +3,22 @@ name: mobile-architecture-android-kotlin
 description: Jetpack Compose, MVVM, Clean Architecture, Coroutines, and Hilt for Android Kotlin
 ---

-# Android (Kotlin) — Best Practices
+# Android (Kotlin) — Best Practices & AI-Driven Scaffolding
+
+## Modern Project Initiation Guide
+
+When launching an Android Kotlin application from scratch, initialize using the following strict architectural directives:
+
+1. **100% Jetpack Compose UI:** Never generate XML layout files. Use the Material 3 design system exclusively.
+2. **Single-Activity Architecture:** Use a single `MainActivity.kt` with a Compose `NavHost` configured for standard type-safe navigation routes.
+3. **MVVM + Clean Architecture:** Group packages strictly by feature:
+   - `domain/` — Contains pure Kotlin models, repository interfaces (ports), and UseCases. No Android framework dependencies.
+   - `data/` — Implements repository interfaces. Coordinates remote (ParsePlatform or API) and local (Room) data sources.
+   - `ui/` — Houses Compose screens, individual components, and ViewModels.
+4. **ParsePlatform Integration:** Always query the Parse SDK directly. Never write Retrofit wrappers or REST interfaces around Parse endpoints.
+5. **Kotlin Coroutines & Flow:** Use `StateFlow<UiState>` for rendering state, `SharedFlow` for one-time events (navigation, snackbars), and `viewModelScope` for scoping. Never use legacy LiveData or RxJava.
+6. **Dependency Injection:** Hilt is mandatory. Annotate ViewModels with `@HiltViewModel` and inject constructor dependencies using `@Inject`.
+7. **Localization (en/fa):** All strings must be declared in `strings.xml`. Persian strings must reside inside `values-fa/strings.xml`. Ensure RTL support using `LocalLayoutDirection` on RTL screens.

 ## Project Structure

diff --git a/skill-templates/audit-agents/SKILL.md b/skill-templates/audit-agents/SKILL.md
index 652b8ff..1838e9d 100644
--- a/skill-templates/audit-agents/SKILL.md
+++ b/skill-templates/audit-agents/SKILL.md
@@ -5,6 +5,167 @@ description: Enforces decentralized task management, UI/UX design strictness, an

 # OpenCode Skill: Agent Protocol Auditor

+## Target Audit Criteria
+
+The `AGENTS.md` file MUST explicitly contain the following operational constraints, ideally within a `Task Management & OpenCode Rules` section:
+
+- **Mandatory First-Read Rule**: MUST explicitly command the agent to read `AGENTS.md` first before any execution. Inside it, it must route the agent to read `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` first.
+- **Core File Locations**: MUST explicitly list paths for `AGENTS.md`, `DESIGN.md`, `tasks/`, and `.opencode/skills/`.
+- **Decentralized Task Management**: Agents MUST strictly use decentralized, individual task files in the `tasks/` directory as their single source of truth.
+- **No Monolithic State**: Agents are strictly forbidden from creating `TODO.md` or `STATE.md`.
+- **Mandatory End-Of-Task Sequence**: MUST explicitly mandate a 4-step completion process: 1) Update CHANGELOG.md. 2) Write manual reasoning in the task file. 3) Call the `custom_context_stage_and_inject_diff` MCP tool. 4) Notify the Manager.
+- **UI/UX Enforcement**: Any UI/UX changes MUST enforce the guidelines defined in the project's `DESIGN.md`.
+- **Task-Generator Skill Loading**: `AGENTS.md` MUST explicitly instruct OpenCode to load the `task-generator` skill before creating new task files.
+- **Project Skill Loading**: `AGENTS.md` MUST explicitly instruct OpenCode to load every available skill matching the project's tech stack before task implementation.
+
+---
+
+## Core Document Templates
+
+### 1. `architecture.md` Template
+
+```markdown
+# Architecture Overview
+
+This document serves as a critical, living template designed to equip agents with a rapid and comprehensive understanding of the codebase's architecture, enabling efficient navigation and effective contribution from day one. Update this document as the codebase evolves.
+
+## 1. Project Structure
+
+[Project Root]/
+├── backend/ # Contains all server-side code and APIs
+│ ├── src/ # Main source code for backend services
+│ │ ├── api/ # API endpoints and controllers
+│ │ ├── client/ # Business logic and service implementations
+│ │ ├── models/ # Database models/schemas
+│ │ └── utils/ # Backend utility functions
+│ ├── config/ # Backend configuration files
+│ ├── tests/ # Backend unit and integration tests
+│ └── Dockerfile # Dockerfile for backend deployment
+├── frontend/ # Contains all client-side code for user interfaces
+│ ├── src/ # Main source code for frontend applications
+│ │ ├── components/ # Reusable UI components
+│ │ ├── pages/ # Application pages/views
+│ │ ├── assets/ # Images, fonts, and other static assets
+│ │ ├── services/ # Frontend services for API interaction
+│ │ └── store/ # State management (e.g., Redux, Vuex, Context API)
+│ ├── public/ # Publicly accessible assets (e.g., index.html)
+│ ├── tests/ # Frontend unit and E2E tests
+│ └── package.json # Frontend dependencies and scripts
+├── common/ # Shared code, types, and utilities used by both frontend and backend
+│ ├── types/ # Shared TypeScript/interface definitions
+│ └── utils/ # General utility functions
+├── docs/ # Project documentation (e.g., API docs, setup guides)
+├── scripts/ # Automation scripts (e.g., deployment, data seeding)
+├── .github/ # GitHub Actions or other CI/CD configurations
+├── .gitignore # Specifies intentionally untracked files to ignore
+├── README.md # Project overview and quick start guide
+└── ARCHITECTURE.md # This document
+
+## 2. High-Level System Diagram
+
+[User] <--> [Frontend Application] <--> [Backend Service 1] <--> [Database 1]
+|
++--> [Backend Service 2] <--> [External API]
+
+## 3. Core Components
+
+### 3.1. Frontend
+
+Name: [Web App, Mobile App]
+Description: [Purpose, core interfaces, and roles]
+Technologies: [e.g., React, Next.js, Jetpack Compose, Swift/Kotlin]
+Deployment: [e.g., Vercel, Netlify, Play Store, App Store]
+
+### 3.2. Backend Services
+
+#### 3.2.1. Service Name 1
+
+Name: [e.g., API Service]
+Description: [Core business roles]
+Technologies: [e.g., Spring Boot, Node.js Express, Go]
+Deployment: [e.g., AWS ECS, Kubernetes]
+
+## 4. Data Stores
+
+### 4.1. Data Store 1
+
+Name: [e.g., SQL Database]
+Type: [e.g., PostgreSQL, MongoDB]
+Purpose: [e.g., Account records]
+
+## 5. External Integrations / APIs
+
+- Service Name: [e.g., Stripe, SendGrid]
+- Purpose: [e.g., Payments]
+- Method: [e.g., REST, SDK]
+
+## 6. Deployment & Infrastructure
+
+- Provider: [e.g., AWS, GCP]
+- CI/CD: [e.g., GitHub Actions]
+
+## 7. Security Considerations
+
+- Authentication: OAuth2/JWT
+- Encryption: TLS + AES-256
+
+## 8. Development & Testing Environment
+
+Testing Frameworks: [e.g., Pytest, JUnit, Jest]
+
+## 9. Future Considerations / Roadmap
+
+[Planned changes or architectural debt]
+```
+
+### 2. DESIGN.md Template (Google Spec)
+
+```markdown
+# Design System Specification
+
+---
+
+name: custom-ui-system
+colors:
+primary: "#1D4ED8"
+secondary: "#4B5563"
+background: "#F3F4F6"
+surface: "#FFFFFF"
+text: "#111827"
+
+---
+
+## 1. Visual Theme & Atmosphere
+
+[Rich prose outlining overall design mood, light/dark values, and whitespace philosophy]
+
+## 2. Color Palette & Roles
+
+- Primary foundation
+- Interactive / CTAs
+- Text hierarchy
+- State colors (Success, error, warn)
+
+## 3. Typography Rules
+
+- Hierarchy (headline, body, label)
+- letterSpacing, lineHeight, fontWeights
+
+## 4. Component Stylings
+
+- Buttons
+- Cards
+- Navigation
+- Input fields
+
+## 5. Layout Principles
+
+- Spacing scales
+- Breakpoints
+```
+
+---
+
 Use this skill in two modes:

 - **Phase 0 (Generation):** When `AGENTS.md` does not exist yet — generate it from the template below.
@@ -69,7 +230,7 @@ You MUST strictly adhere to these exact paths. Do not create duplicates elsewher
 You MUST follow these skill loading rules in every session:

 - **Task-Generator Skill:** Before creating any new task file, you MUST load the `task-generator` skill using the `skill` tool to ensure the correct template format with `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.
-- **Project Skills:** Before implementing any task, you MUST load every available skill matching the project's tech stack (e.g., `[android-kotlin]`, `[spring-boot]`, `[react-vite]`). If a relevant skill exists, it MUST be loaded — this enforces framework-specific conventions and architectural rules.
+- **Project Skills:** Before implementing any task, you MUST load every available skill matching the project's tech stack (e.g., `android-kotlin`, `spring-boot`, `react-vite`). If a relevant skill exists, it MUST be loaded — this enforces framework-specific conventions and architectural rules.

 ## 🛑 MANDATORY END-OF-TASK SEQUENCE

diff --git a/skill-templates/nextjs/SKILL.md b/skill-templates/nextjs/SKILL.md
index 412418e..51abdc6 100644
--- a/skill-templates/nextjs/SKILL.md
+++ b/skill-templates/nextjs/SKILL.md
@@ -3,7 +3,19 @@ name: frontend-architecture-nextjs
 description: App Router, Server/Client Components, Server Actions, and Tailwind tokens for Next.js
 ---

-# Next.js — Best Practices
+# Next.js — Best Practices & AI-Driven Scaffolding
+
+## Modern Next.js App Router Architecture
+
+Scaffold Next.js single-page or hybrid apps using these principles:
+
+1. **App Router App Layout:** Use file-based nested routing in the `app/` directory (`layout.tsx`, `page.tsx`).
+2. **Strict Server/Client Boundaries:**
+   - Components are Server Components by default. Fetch data, access databases, and handle security here.
+   - Client Components must be annotated with `"use client"` at the top. Use them only for user interactivity (hooks, event handlers, local states). Keep them at leaf-level.
+3. **Server Actions for Mutations:** Always handle form submissions and database mutations using Server Actions with the `"use server"` directive. Banned: setting up custom API routes for simple form handling.
+4. **Tailwind Token System:** Never use arbitrary Tailwind classes (like `h-[12px]`) or inline styles. Declare custom scales inside `tailwind.config.ts` and refer to them.
+5. **A11y Semantic HTML:** Always enforce standard landmarks (`<header>`, `<main>`, `<footer/>`) and `next/image` alt tags.

 ## Project Structure

diff --git a/skill-templates/nodejs-express/SKILL.md b/skill-templates/nodejs-express/SKILL.md
index ac5eec0..5731b43 100644
--- a/skill-templates/nodejs-express/SKILL.md
+++ b/skill-templates/nodejs-express/SKILL.md
@@ -3,7 +3,19 @@ name: backend-architecture-nodejs-express
 description: Architectural rules, 3-layer pattern, and naming conventions for Node.js Express
 ---

-# Node.js + Express — Best Practices
+# Node.js + Express — Best Practices & AI-Driven Scaffolding
+
+## Strict Node.js Service Scaffolding
+
+Initialize any Express service using this high-performance layout:
+
+1. **Zod Environment Validation:** Always validate `process.env` at startup using a strict Zod schema. Export a typed `config` object. Banned: accessing `process.env` directly inside modules.
+2. **3-Layer Architecture:** Strictly enforce `Route -> Controller -> Service` boundaries:
+   - Routes define endpoints and middleware.
+   - Controllers parse request bodies/parameters and return responses. No business logic.
+   - Services implement business logic and coordinate data layers. No request/response imports.
+3. **Centralized Global Error Handler:** Use a custom `AppError` class. Wrap controllers with `express-async-errors` to capture thrown exceptions globally and format them consistently. Banned: inline `try/catch` blocks inside controllers.
+4. **Security Basics:** Always register `helmet`, `cors`, and `express-rate-limit` middlewares at startup.

 ## Project Structure

diff --git a/skill-templates/spring-boot/SKILL.md b/skill-templates/spring-boot/SKILL.md
index ef2713c..2719bb2 100644
--- a/skill-templates/spring-boot/SKILL.md
+++ b/skill-templates/spring-boot/SKILL.md
@@ -3,7 +3,18 @@ name: backend-architecture-spring-boot
 description: DDD, hexagonal style, and naming conventions for Spring Boot
 ---

-# Spring Boot — Best Practices
+# Spring Boot — Best Practices & AI-Driven Scaffolding
+
+## High-Performance Project Onboarding
+
+Initialize any Spring Boot backend from scratch with these architectural rules:
+
+1. **Domain-Driven Design (DDD):** Use a pure `domain` package containing entities, value objects, and repository ports (interfaces). The domain must not have adapter or framework dependencies.
+2. **Hexagonal Ports & Adapters:** Inbound adapters (Controllers, DTOs) and outbound adapters (JPA Repositories, Database engines) are decoupled. Controllers depend on domain services, and domain services interact with adapters via ports.
+3. **Constructor Injection:** Always use Lombok `@RequiredArgsConstructor` on classes needing dependencies. Banned: Field `@Autowired`.
+4. **MapStruct Compile-Time Mapping:** Generate mappers using MapStruct `@Mapper(componentModel = "spring")`. Banned: reflection-based mapping or manually writing setter chains.
+5. **Centralized Error Boundary:** Implement a single `@RestControllerAdvice` class capturing all domain-specific exceptions and mapping them to standardized HTTP responses `{ error, message, status, timestamp }`.
+6. **Database Migration:** Always use Flyway or Liquibase to manage relational schemas via SQL files in `resources/db/migration`. Banned: relying on JPA `hibernate.ddl-auto=update` in production.

 ## Project Structure

diff --git a/skill-templates/vue-nuxt/SKILL.md b/skill-templates/vue-nuxt/SKILL.md
index 5a229a7..0ef8328 100644
--- a/skill-templates/vue-nuxt/SKILL.md
+++ b/skill-templates/vue-nuxt/SKILL.md
@@ -3,7 +3,17 @@ name: frontend-architecture-vue-nuxt
 description: Vue 3 Composition API, Nuxt 3 routing, and state management
 ---

-# Vue 3 & Nuxt 3 — Best Practices
+# Vue 3 & Nuxt 3 — Best Practices & AI-Driven Scaffolding
+
+## Modern Nuxt 3 App Architecture
+
+Scaffold Nuxt 3 applications using these guidelines:
+
+1. **Composition API:** Always use `<script setup lang="ts">` with TypeScript. Banned: Options API.
+2. **Auto-Imports Leverage:** Rely on Nuxt's auto-imported directory structures for `composables/`, `components/`, and core Vue APIs (`ref`, `computed`, `reactive`).
+3. **State Management:** Use Pinia via `@pinia/nuxt`. Define stores using the store-factory function syntax (`defineStore('id', () => { ... })`).
+4. **SSR-Safe Data Fetching:** Always use `useFetch` or `useAsyncData` to ensure data loads on the server and hydrates safely on the client. Banned: standard `axios` or bare `fetch` inside components.
+5. **Form Validation:** Use Formkit or VeeValidate + Zod for robust client-side schemas.

 ## Project Structure

diff --git a/system-prompt.md b/system-prompt.md
index 111aa85..677f589 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,9 +1,10 @@
-<system_version>5.7.1</system_version>
+<system_version>5.9.0</system_version>

 <role>
 You are the Cognitive Lead AI running inside Google AI Studio (powered by Gemini), acting as an elite software agency orchestrator.
 You coordinate with the human user (The Manager) and generate highly structured, non-interactive instructions for "OpenCode" (the local autonomous agent running on the Manager's laptop).
 You DO NOT have direct file-system, terminal, or network access. You communicate exclusively with the Manager via text. Your execution power comes from generating precise tasks that the Manager copies and runs inside OpenCode.
+OpenCode has parallel agent execution capabilities and can execute up to 4 tasks concurrently across different subagents to accelerate codebase discovery and file generation.
 ALWAYS start your response by declaring your active persona in brackets, e.g., **[Software Architect]**.
 </role>

@@ -24,7 +25,7 @@ CRITICAL INSTRUCTION: The Manager will often send informal, raw text. Before tak
   <persona name="Software Architect">
     <trigger>New features, major backend changes, or explicit Manager requests.</trigger>
     <duty>System design, database schemas, API contracts, DevOps/Infrastructure, and technical roadmapping.</duty>
-    <behavior>Analyze requirements and foresee edge cases. Instruct the Project Planner to establish initial project rules. If you lack sufficient codebase context during onboarding or feature design, STOP. Do not hallucinate. Instead, request the Planner to initiate a Discovery Task so the Manager can run it in OpenCode and paste the file tree and code context back to us. Only produce the final detailed technical blueprint once you have the necessary context. Keep custom workflows isolated as task-specific toolkits in `.opencode/skills/<name>/SKILL.md` to prevent context bloat. STOP and wait for Manager approval before code generation begins.</behavior>
+    <behavior>Analyze requirements and foresee edge cases. Instruct the Project Planner to establish initial project rules. When initializing or designing, ALWAYS instruct OpenCode to consult AGENTS.md as its very first action. AGENTS.md will then direct OpenCode to read the core architectural and design specifications (DESIGN.md, architecture.md, data_model.md, conventions.md) to guarantee fully integrated and uniform code. If you lack sufficient codebase context, STOP. Do not hallucinate. Request the Planner to initiate a Discovery Task so the Manager can run it in OpenCode and paste the file tree and code context back to us. Only produce the final detailed technical blueprint once you have the necessary context. Keep custom workflows isolated as task-specific toolkits in `.opencode/skills/<name>/SKILL.md` to prevent context bloat. STOP and wait for Manager approval before code generation begins.</behavior>
   </persona>

   <persona name="UI/UX Designer">
@@ -36,13 +37,13 @@ CRITICAL INSTRUCTION: The Manager will often send informal, raw text. Before tak
   <persona name="Senior Programmer">
     <trigger>Approved blueprints/designs or explicit Manager requests.</trigger>
     <duty>Technical implementation lead and "OpenCode Whisperer".</duty>
-    <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. You do NOT execute code yourself and you DO NOT predict execution results. You write strict, comprehensive instructions formatted as an `<opencode_implementation_task>` for the local OpenCode agent to execute. You MUST wrap the task in a Markdown code block starting with ```xml and ending with ``` so the Manager can copy it with a single click. Instruct OpenCode to leverage its native tools (`lsp`, `grep`, `websearch`, `skill`, MCP servers, and `@explore` subagent) to gain context autonomously.</behavior>
+    <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. You write strict, comprehensive instructions formatted as an `<opencode_implementation_task>` for the local OpenCode agent to execute. You MUST instruct OpenCode to read AGENTS.md as its very first step, which acts as a router directing the agent to read DESIGN.md, architecture.md, data_model.md, and conventions.md before implementing changes. You do NOT execute code yourself. Wrap the task in a Markdown code block starting with ```xml and ending with ``` so the Manager can copy it with a single click. Instruct OpenCode to leverage its native tools (`lsp`, `grep`, `websearch`, `skill`, MCP servers, and `@explore` subagent) to gain context autonomously.</behavior>
   </persona>

   <persona name="Project Planner">
     <trigger>Status checks, milestone planning, or explicit Manager requests.</trigger>
     <duty>Maintain individual task files in the tasks/ directory as the single source of truth for work items, and maintain AGENTS.md both in AI Studio context and mirrored locally.</duty>
-    <behavior>Maintain decentralized task files in `tasks/` as the single source of truth. When creating a new task file, instruct OpenCode to load the `task-generator` skill to ensure the correct template format with `<!-- BEGIN_GIT_DIFF -->` and `<!-- END_GIT_DIFF -->` markers. In Phase 0, instruct OpenCode to load the `audit-agents` skill to generate `AGENTS.md` and perform a deep traversal of the source code to fully comprehend the project structure and UI/UX elements, resulting in a comprehensive `DESIGN.md`. Ensure `AGENTS.md` explicitly includes instructions on reading and updating the active task file.</behavior>
+    <behavior>Maintain decentralized task files in `tasks/` as the single source of truth. When creating a new task file, instruct OpenCode to load the `task-generator` skill to ensure the correct template format with `<!-- BEGIN_GIT_DIFF -->` and `<!-- END_GIT_DIFF -->` markers. In Phase 0, instruct OpenCode to load the `audit-agents` skill to generate `AGENTS.md`. During onboarding, spawn parallel subagents (up to 4 concurrent agents) to traverse the source code to fully comprehend the project layout and UI/UX design, drafting comprehensive spec files: `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md`. Ensure `AGENTS.md` explicitly includes instructions on reading and updating the active task file.</behavior>
   </persona>

   <persona name="Code Reviewer">
@@ -139,6 +140,7 @@ You are a very strong reasoner and planner. Before taking any action (either gen
 </opencode_protocols>

 <execution_workflow> 0. **Discovery & Onboarding**: Ask the Manager if this is a NEW or EXISTING project. For new projects, instruct OpenCode to load the `audit-agents` skill to generate `AGENTS.md`, load the `design-md` skill (if available) for `DESIGN.md`, and then create `opencode.json` plus initial tasks.
+During Phase 0, the Planner will launch up to 4 parallel subagent tasks to deeply scan files and concurrently generate `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` to avoid style and structure misalignment.

 1. **Input Processing & Clarification**: Analyze the Manager's raw input. Clean syntax, interpret context. IF ambiguous, HALT and ask clarifying questions. IF clear, proceed.
 2. **Plan (Architect & UI/UX)**: Analyze request -> Deliver blueprint -> Ask Manager for approval.
````

<!-- END_GIT_DIFF -->
