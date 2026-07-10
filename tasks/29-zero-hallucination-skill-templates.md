# Task: Zero-Hallucination Skill Templates Restructure

**File:** `tasks/29-zero-hallucination-skill-templates.md`
**Type:** improvement
**Status:** closed

## Goal

Restructure `skill-templates/` to enforce "Zero-Hallucination" AI stacks: rewrite Android Kotlin and React Native Expo with strict opinionated rules, add NestJS Prisma Vertical template, and delete legacy unstructured skills (Node.js Express, Android Java XML).

## Manager's Notes

- Android Kotlin must enforce 100% Compose, ban XML, mandate Hilt, enforce null-safety, and require compile-time safe DB (SQLDelight/Room).
- React Native Expo must enforce Expo Managed Workflow only, ban native folder edits, mandate NativeWind, require strict TypeScript.
- NestJS Prisma Vertical must enforce Vertical Slice Architecture, NestJS decorators, Prisma ORM, and class-validator DTOs.
- Delete `skill-templates/nodejs-express` and `skill-templates/android-java-xml`.
- Update README.md stack table and CHANGELOG.md.

## Local TODOs

- [x] Initial codebase exploration
- [x] Rewrite `skill-templates/android-kotlin/SKILL.md` with zero-hallucination rules
- [x] Rewrite `skill-templates/react-native-expo/SKILL.md` with strict Expo Managed rules
- [x] Create `skill-templates/nestjs-prisma-vertical/SKILL.md`
- [x] Delete `skill-templates/nodejs-express` and `skill-templates/android-java-xml`
- [x] Update README.md stack table and repo tree
- [x] Update CHANGELOG.md
- [x] Write execution log in task file
- [x] Finalize: stage_and_inject_diff + notify

## OpenCode Execution Log & Reasoning

**Architectural Reasoning:** This task targets "zero-hallucination" by enforcing strictly opinionated, compile-time-safe frameworks. Android Kotlin now bans XML entirely (the #1 source of UI hallucinations), mandates Hilt DI, and requires SQLDelight/Room for type-safe DB access. React Native Expo bans native folder modification (the #1 source of RN hallucinations), mandates Expo Managed Workflow only, and enforces strict TypeScript. The new NestJS Prisma Vertical template introduces Vertical Slice Architecture (grouping by feature) to localize AI context, combined with Prisma's compile-time ORM guarantees. Legacy Node.js Express (unstructured) and Android Java XML (hallucination-prone) are deleted as they conflict with the "Max Power" zero-hallucination methodology.

**Changes Made:**

1. **skill-templates/android-kotlin/SKILL.md:** Complete rewrite. Description updated to "100% Jetpack Compose, MVI, Hilt, SQLDelight". Added strict XML ban, null-safety rule, compile-time DB mandate. Restructured to 4 required sections with Hilt-specific DI pattern.
2. **skill-templates/react-native-expo/SKILL.md:** Complete rewrite. Description updated to "Expo Managed Workflow, Expo Router, NativeWind, Strict TypeScript". Added banner against modifying ios/android native folders. Mandated NativeWind over StyleSheet.create.
3. **skill-templates/nestjs-prisma-vertical/SKILL.md:** Created new. Enforces NestJS decorators, Vertical Slice Architecture with `features/` grouping, Prisma ORM as source of truth, class-validator DTOs, and ban on `any` type.
4. **skill-templates/nodejs-express/SKILL.md:** Deleted (deprecated — unstructured Express causes AI hallucinations).
5. **skill-templates/android-java-xml/SKILL.md:** Deleted (deprecated — XML layouts cause AI hallucinations).
6. **README.md:** Updated stack table: removed Android Java and Node.js Express rows; added NestJS Prisma Vertical row; updated Android Kotlin and React Native Expo descriptions to emphasize strict zero-hallucination rules; updated repo structure tree.
7. **tasks/29-zero-hallucination-skill-templates.md:** Created this task file.

**Verification:** Pending manual review via stage_and_inject_diff.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

````diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 4c58b1c..216eff0 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,21 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

 ## [Unreleased]

+### Added
+
+- **NestJS Prisma Vertical Skill Template:** Created `skill-templates/nestjs-prisma-vertical/SKILL.md` enforcing NestJS decorators, Vertical Slice Architecture, Prisma ORM, strict TypeScript, and class-validator DTOs for zero-hallucination backend development.
+
+### Changed
+
+- **Android Kotlin Template Overhaul:** `skill-templates/android-kotlin/SKILL.md` completely rewritten with strict XML ban, Hilt DI mandate, compile-time safe DB (SQLDelight/Room), and enhanced null-safety rules.
+- **React Native Expo Template Overhaul:** `skill-templates/react-native-expo/SKILL.md` rewritten with Expo Managed Workflow enforcement, ban on native folder edits, mandatory NativeWind, and strict TypeScript requirement.
+- **README.md:** Updated Stack-Specific Blueprints table to reflect removed and added templates; strengthened Android Kotlin and React Native Expo descriptions with zero-hallucination rules.
+
+### Removed
+
+- **`skill-templates/nodejs-express/`:** Deleted — unstructured Express patterns cause AI hallucinations. Superseded by opinionated frameworks (NestJS).
+- **`skill-templates/android-java-xml/`:** Deleted — XML layout files cause severe UI hallucinations. Superseded by 100% Jetpack Compose Android Kotlin template.
+
 ## [5.17.0] — 2026-07-04

 ### Added
diff --git a/README.md b/README.md
index 7b33485..50cf217 100644
--- a/README.md
+++ b/README.md
@@ -14,7 +14,7 @@ This repository is the **V5 evolution** of the Cognitive Lead AI multi-agent sys
 | ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
 | `system-prompt.md`                          | At the start of every session; this is the V5 multi-agent prompt defining all 5 personas and the Agentic Reasoning matrix. |
 | `.opencode/skills/sop-maintenance/SKILL.md` | When an AI agent needs to modify this repository itself.                                                                   |
-| `skill-templates/*/SKILL.md`                | Before writing code in a specific stack (Node.js, Spring Boot, Flask, Next.js, Android Kotlin/Java).                       |
+| `skill-templates/*/SKILL.md`                | Before writing code in a specific stack (Spring Boot, Flask, Next.js, NestJS, Android Kotlin).                            |
 | `CHANGELOG.md`                              | To review what has changed between versions.                                                                               |
 | `tasks/`                                    | To see the active task files and current work items.                                                                       |

@@ -90,13 +90,11 @@ The AI will process your inline feedback, generate a revised plan, and wait for
         │   └── SKILL.md
         ├── nextjs/
         │   └── SKILL.md
-        ├── nodejs-express/
-        │   └── SKILL.md
         ├── spring-boot/
         │   └── SKILL.md
         ├── flask-python/
         │   └── SKILL.md
-        ├── android-java-xml/
+        ├── nestjs-prisma-vertical/
         │   └── SKILL.md
         └── code-search/
             └── SKILL.md
@@ -227,21 +225,20 @@ To make the `code-search` skill (or any other reusable skill) available in _ever

 ### Stack-Specific Blueprints

-| Stack             | Architecture Enforced                                                                                      |
-| ----------------- | ---------------------------------------------------------------------------------------------------------- |
-| Android Java      | MVC/MVP with ViewBinding, lifecycle management, and RxJava for legacy Android development.                 |
-| Android Kotlin    | Jetpack Compose, MVI (Unidirectional Data Flow), Clean Architecture, Offline-First Room, and Hilt DI.      |
-| Flask Python      | Application Factory, Blueprints, SQLAlchemy, and config separation for modular Flask applications.         |
-| Go Gin            | Idiomatic Go, Clean Architecture layers, and Gin routing best practices for RESTful services.              |
-| Go Hexagonal gRPC | Hexagonal Architecture (Ports and Adapters), gRPC, Uber Fx compile-time DI, Redis caching, and PostgreSQL. |
-| iOS SwiftUI       | SwiftUI, MVVM, and modern iOS app architecture with declarative UI patterns.                               |
-| Next.js           | App Router, Server/Client Component separation, Server Actions, and Tailwind CSS design tokens.            |
-| Node.js Express   | 3-Layer Architecture (Controller/Service/Repository), centralized error handling, and env validation.      |
-| Python FastAPI    | Pydantic schemas, dependency injection, async routing, and layered service architecture.                   |
-| React Native Expo | Expo Router, React Native components, and cross-platform UI with native module support.                    |
-| React Vite        | React 18+ SPA architecture, hooks, and Vite configuration with optimized build tooling.                    |
-| Spring Boot       | DDD, hexagonal-style packaging, MapStruct, constructor injection, and global exception handlers.           |
-| Vue Nuxt          | Vue 3 Composition API, Nuxt 3 routing, and Pinia state management.                                         |
+| Stack                   | Architecture Enforced                                                                                      |
+| ----------------------- | ---------------------------------------------------------------------------------------------------------- |
+| Android Kotlin          | **100% Jetpack Compose — XML Strictly Banned.** MVI (UDF), Hilt, SQLDelight/Room.                           |
+| Flask Python            | Application Factory, Blueprints, SQLAlchemy, and config separation for modular Flask applications.         |
+| Go Gin                  | Idiomatic Go, Clean Architecture layers, and Gin routing best practices for RESTful services.              |
+| Go Hexagonal gRPC       | Hexagonal Architecture (Ports and Adapters), gRPC, Uber Fx compile-time DI, Redis caching, and PostgreSQL. |
+| iOS SwiftUI             | SwiftUI, MVVM, and modern iOS app architecture with declarative UI patterns.                               |
+| NestJS Prisma Vertical  | NestJS, Prisma ORM, Vertical Slice Architecture, strict TypeScript, and class-validator DTOs.              |
+| Next.js                 | App Router, Server/Client Component separation, Server Actions, and Tailwind CSS design tokens.            |
+| Python FastAPI          | Pydantic schemas, dependency injection, async routing, and layered service architecture.                    |
+| React Native Expo       | **Expo Managed Workflow ONLY — no native folders.** Expo Router, NativeWind, Zustand, strict TypeScript.   |
+| React Vite              | React 18+ SPA architecture, hooks, and Vite configuration with optimized build tooling.                    |
+| Spring Boot             | DDD, hexagonal-style packaging, MapStruct, constructor injection, and global exception handlers.           |
+| Vue Nuxt                | Vue 3 Composition API, Nuxt 3 routing, and Pinia state management.                                         |

 ## Key V5 Changes

diff --git a/skill-templates/android-java-xml/SKILL.md b/skill-templates/android-java-xml/SKILL.md
deleted file mode 100644
index 5438729..0000000
--- a/skill-templates/android-java-xml/SKILL.md
+++ /dev/null
@@ -1,110 +0,0 @@
----
-name: mobile-architecture-android-java-xml
-description: MVC/MVP, ViewBinding, lifecycle management, and RxJava for Android Java
----
-
-# Android (Java + XML) — Best Practices
-
-## Project Structure
-
-```
-com.company.project/
-├── adapter/                  # RecyclerView adapters
-│   └── UserAdapter.java
-├── model/                    # Plain Java models (POJOs)
-│   └── User.java
-├── network/                  # Retrofit API / network layer
-│   ├── ApiClient.java
-│   └── ApiService.java
-├── repository/               # Data repository
-│   └── UserRepository.java
-├── ui/                       # Activity / Fragment packages
-│   ├── auth/
-│   │   ├── LoginActivity.java
-│   │   └── LoginFragment.java
-│   └── profile/
-│       ├── ProfileActivity.java
-│       └── ProfileFragment.java
-├── utils/                    # Utility classes
-│   └── DateUtils.java
-└── viewmodel/                # ViewModel classes (if using MVVM)
-    └── ProfileViewModel.java
-
-res/
-├── layout/                   # XML layouts
-│   ├── activity_login.xml
-│   └── fragment_profile.xml
-├── values/
-│   ├── strings.xml
-│   ├── colors.xml
-│   └── themes.xml
-├── drawable/                 # Vector drawables & shape XMLs
-└── menu/
-```
-
-## Naming Conventions
-
-| Artifact            | Convention                         | Example                                      |
-| ------------------- | ---------------------------------- | -------------------------------------------- |
-| Files (Java)        | `PascalCase`                       | `LoginActivity.java`                         |
-| Classes             | `PascalCase`                       | `UserRepository`                             |
-| Methods / Variables | `camelCase`                        | `getUserById`                                |
-| Constants           | `UPPER_SNAKE_CASE`                 | `MAX_RETRY_COUNT`                            |
-| Layout XML          | `snake_case` prefix with component | `activity_login.xml`, `fragment_profile.xml` |
-| Resource IDs        | `snake_case`                       | `@+id/btn_submit`                            |
-| String keys         | `snake_case`                       | `error_network`                              |
-
-## Architectural Patterns
-
-### MVC (Model-View-Controller)
-
-- **Model**: POJOs, repositories, network layer.
-- **View**: XML layouts, Activity/Fragment acting as the View (or thin Controller).
-- **Controller**: For complex screens, introduce a dedicated Controller/Presenter class that handles business logic and delegates to the View via an interface.
-
-### MVP (Model-View-Presenter) — Preferred for Complex Screens
-
-```
-View (Activity/Fragment) ←→ Presenter ←→ Model (Repository)
-```
-
-- The Presenter holds all business logic.
-- The View interface is implemented by the Activity/Fragment — the Presenter calls view methods (e.g., `showUsers(List<User>)`, `showError(String)`).
-- Presenters survive rotation by detaching/re-attaching the View reference.
-
-### ViewBinding (No `findViewById`)
-
-- Enable `viewBinding` in `build.gradle`.
-- Every layout generates a `Binding` class (e.g., `ActivityLoginBinding`).
-- Inflate and hold the binding in the Activity/Fragment; access views via `binding.textViewName`.
-- Never use `findViewById` — it is error-prone and verbose.
-
-### Activity / Fragment Lifecycle Management
-
-- Initialize components in `onCreate` (Activity) or `onCreateView` (Fragment).
-- Start loading data in `onStart` or `onResume`; cancel in `onPause` or `onStop`.
-- Use `savedInstanceState` to preserve transient UI state across configuration changes.
-- For retained data across rotation, use `ViewModel` (even with Java) or a retained fragment (`setRetainInstance(true)`).
-- Avoid memory leaks: null out heavy references (Bitmap, large collections) in `onDestroy`.
-
-### Background Threading
-
-- Use **RxJava** (Observables/Single/Flowable) for composable async operations and thread switching (`subscribeOn`/`observeOn`).
-- Alternatively, use `ExecutorService` + `Handler` for simpler cases.
-- Never perform network or database operations on the main thread.
-- Use `CompositeDisposable` (RxJava) to manage subscriptions and dispose in `onDestroy`.
-
-## Testing Strategies
-
-| Layer                 | Test Type       | Framework         | File Naming               |
-| --------------------- | --------------- | ----------------- | ------------------------- |
-| Repository            | Unit            | JUnit 4 + Mockito | `UserRepositoryTest.java` |
-| Presenter / ViewModel | Unit            | JUnit 4 + Mockito | `LoginPresenterTest.java` |
-| Utils                 | Unit            | JUnit 4           | `DateUtilsTest.java`      |
-| UI / Activity         | Instrumentation | Espresso          | `LoginActivityTest.java`  |
-
-- Use **JUnit 4** (standard for Android Java projects).
-- Use **Mockito** for mocking dependencies.
-- Use **Espresso** for UI interaction tests — test on the UI thread with `onView()` matchers.
-- Use **Robolectric** for fast local testing of Android framework-dependent code (no emulator required).
-- Keep tests in `src/test/java/` (unit) and `src/androidTest/java/` (instrumentation).
diff --git a/skill-templates/android-kotlin/SKILL.md b/skill-templates/android-kotlin/SKILL.md
index f84eb24..2011776 100644
--- a/skill-templates/android-kotlin/SKILL.md
+++ b/skill-templates/android-kotlin/SKILL.md
@@ -1,32 +1,24 @@
 ---
 name: mobile-architecture-android-kotlin
-description: Jetpack Compose, MVI (UDF), and Kotlin for token-efficient Android development.
+description: 100% Jetpack Compose, MVI (UDF), Hilt, and SQLDelight for token-efficient, zero-hallucination Android development.
 ---

-# Android (Kotlin) — "Max Power" AI-Driven Architectural Scaffolding
+# Android (Kotlin) — "Max Power" AI-Driven Architecture

-## AI Context & Token Optimization
+## AI Context & Token Optimization (Zero-Hallucination Rules)

-1. **XML is Strictly Banned:** Never generate `.xml` layout files. XML forces the AI to maintain cross-file context (matching IDs between Kotlin and XML), which wastes tokens and causes layout binding hallucinations.
-2. **100% Jetpack Compose:** Write all UI in declarative Kotlin. Compose allows the AI to generate UI and logic in a single, predictable, token-efficient tree.
-3. **Modular Composables:** Break large UIs into extremely small, pure `@Composable` functions. The AI struggles to modify 500-line Compose functions without breaking brackets.
-
-## Modern Project Initiation Guide
-
-When launching an Android Kotlin application (especially high-performance or offline-first apps like Caller ID) from scratch, initialize using the following strict architectural directives:
-
-1. **Single-Activity Architecture:** Use a single `MainActivity.kt` with a Compose `NavHost`.
-2. **MVI + UDF + Clean Architecture:** Group packages strictly by feature. Enforce Unidirectional Data Flow. The View sends sealed `Intents` to the ViewModel, which reduces them into a single `UiState`.
-3. **Network & Protocol:** Use gRPC via Wire or Ktor for high-performance connections.
-4. **Dependency Injection:** Hilt is mandatory. Annotate ViewModels with `@HiltViewModel`.
+1. **XML IS STRICTLY BANNED:** Never generate `.xml` layout files. XML forces cross-file context mapping which causes severe UI hallucinations.
+2. **100% Jetpack Compose:** Write all UI in declarative Kotlin. Break large UIs into extremely small, pure `@Composable` functions.
+3. **Strict Null-Safety:** Rely entirely on Kotlin's null-safety. Do not use `!!` unless absolutely necessary.
+4. **Compile-Time Safety for DB:** Use SQLDelight or Room. Do NOT use raw string SQL queries in repositories.

 ## Project Structure

-```
+```text
 com.company.project/
 ├── di/                          # Hilt DI modules
-├── data/                        # Data layer (Room DAOs, gRPC DTOs, Repositories)
-├── domain/                      # Domain layer (Pure Kotlin Models, Repository Interfaces, UseCases)
+├── data/                        # Data layer (SQLDelight/Room DAOs, DTOs, Repositories)
+├── domain/                      # Domain layer (Pure Kotlin Models, UseCases)
 └── ui/                          # Presentation layer
     ├── theme/                   # Compose theming (Color, Type, Theme)
     ├── component/               # Small, reusable, modular composables
@@ -45,10 +37,10 @@ com.company.project/
 ## Architectural Patterns

 **MVI (Model-View-Intent) + UDF:**
-Every screen uses a single `ViewModel`. The ViewModel exposes exactly one `StateFlow<UiState>`. The View sends sealed `Intents` to the ViewModel. This eliminates race conditions and makes the AI's reasoning traceable through a single `when(intent)` reducer block.
+Every screen uses a single `ViewModel` annotated with `@HiltViewModel`. The ViewModel exposes exactly one `StateFlow<UiState>`. The View sends sealed `Intents` to the ViewModel. This eliminates race conditions and makes the reasoning traceable through a single `when(intent)` reducer block.

-**Supabase / BaaS Integration:**
-For rapid AI development, prefer direct integration with Supabase/Firebase SDKs in the Data layer to eliminate custom backend boilerplate, unless a dedicated backend is provided.
+**Dependency Injection:**
+Hilt is mandatory. Do not write manual dependency factories.

 ## Testing Strategies

@@ -56,4 +48,4 @@ For rapid AI development, prefer direct integration with Supabase/Firebase SDKs
 | --------------- | -------------------------- | ----------------------------- |
 | Use cases       | Unit                       | JUnit 5 + MockK               |
 | ViewModel (MVI) | Unit (Intent injection)    | JUnit 5 + Turbine (for Flows) |
-| UI / Composable | Snapshot / Compose UI Test | Compose Test                  |
+| UI / Composable | Snapshot / Compose UI Test | Compose Test                  |
\ No newline at end of file
diff --git a/skill-templates/nestjs-prisma-vertical/SKILL.md b/skill-templates/nestjs-prisma-vertical/SKILL.md
new file mode 100644
index 0000000..860318a
--- /dev/null
+++ b/skill-templates/nestjs-prisma-vertical/SKILL.md
@@ -0,0 +1,69 @@
+---
+name: backend-architecture-nestjs-prisma-vertical
+description: NestJS, Prisma ORM, Vertical Slice Architecture, and Strict TypeScript for zero-hallucination backend development.
+---
+
+# NestJS + Prisma (Vertical Slice) — "Max Power" AI Architecture
+
+## AI Context & Token Optimization (Zero-Hallucination Rules)
+
+1. **Opinionated Framework:** NestJS is mandatory. Unstructured frameworks like Express are BANNED. You must use decorators (`@Controller`, `@Injectable`) and modules.
+2. **Vertical Slice Architecture:** Do NOT use traditional layered architectures (global `controllers/`, `services/`). Group all files by feature (e.g., `src/features/auth/`) to localize AI context and save memory tokens.
+3. **Strict TypeScript & Compile-Time Safety:** The `any` type is strictly forbidden.
+4. **Prisma ORM as Source of Truth:** Raw SQL queries are BANNED. You must modify `schema.prisma`, and rely on the compiler to catch invalid database calls.
+5. **Validation:** All incoming requests MUST be validated using DTOs with `class-validator` and `class-transformer`.
+
+## Project Structure
+
+```text
+src/
+├── main.ts                     # Application entry point
+├── app.module.ts               # Root module
+├── core/                       # Core infrastructure (written once)
+│   ├── prisma/                 # Prisma service and module
+│   ├── guards/                 # Authentication/Authorization guards
+│   ├── filters/                # Global exception filters
+│   └── interceptors/             # Global interceptors
+└── features/                   # ⬅️ Vertical Slices (Feature Modules)
+    ├── auth/
+    │   ├── auth.module.ts
+    │   ├── auth.controller.ts
+    │   ├── auth.service.ts
+    │   └── dtos/
+    │       ├── login.dto.ts
+    │       └── register.dto.ts
+    └── users/
+        ├── users.module.ts
+        ├── users.controller.ts
+        └── users.service.ts
+```
+
+## Naming Conventions
+
+| Artifact          | Convention                 | Example               |
+| ----------------- | -------------------------- | --------------------- |
+| Files             | `kebab-case` with type     | `auth.controller.ts`  |
+| Classes           | `PascalCase`               | `AuthController`      |
+| Methods/Variables | `camelCase`                | `registerUser`        |
+| Prisma Models     | `PascalCase` (Singular)    | `model User`          |
+
+## Architectural Patterns
+
+**Dependency Injection:**
+Use NestJS constructor injection exclusively.
+
+**Prisma Workflow:**
+1. Modify `prisma/schema.prisma`.
+2. Never write migrations manually. Use CLI commands to generate them.
+3. Inject `PrismaService` into feature services to interact with the DB. The LSP will guide you with exact types.
+
+**Global Error Handling:**
+Do not use inline `try/catch` for standard HTTP errors. Throw NestJS exceptions (`ConflictException`, `NotFoundException`) and let the global filter handle the JSON formatting.
+
+## Testing Strategies
+
+| Layer            | Test Type   | Framework                 | File Naming                 |
+| ---------------- | ----------- | ------------------------- | --------------------------- |
+| Feature Service  | Unit        | Jest + Mock Prisma      | `auth.service.spec.ts`      |
+| Controller       | Unit        | Jest                      | `auth.controller.spec.ts`   |
+| Feature Endpoint | E2E         | Jest + Supertest + TestDB | `auth.e2e-spec.ts`          |
\ No newline at end of file
diff --git a/skill-templates/nodejs-express/SKILL.md b/skill-templates/nodejs-express/SKILL.md
deleted file mode 100644
index f919191..0000000
--- a/skill-templates/nodejs-express/SKILL.md
+++ /dev/null
@@ -1,53 +0,0 @@
----
-name: backend-architecture-nodejs-express
-description: AI-Optimized TypeScript Express architecture with Zod validation and 3-layer pattern.
----
-
-# Node.js + Express (TypeScript) — AI-Native Scaffolding
-
-## AI Context & Token Optimization
-
-1. **Strict TypeScript Only:** Pure JavaScript is banned. You MUST use strict TypeScript interfaces for all database models, API responses, and request bodies. This prevents AI hallucinations and ensures safe cross-file refactoring.
-2. **Zod for Everything:** Use Zod for environment validation, request body validation, and type inference.
-3. **Modular Files:** Keep files under 200 lines. The AI context window degrades when reading monolithic controllers.
-
-## Project Structure
-
-```
-src/
-├── config/              # Environment & app configuration (env.ts)
-├── routes/              # Route definitions (thin — no business logic)
-├── controllers/         # Request/response handling (Typed req/res)
-├── services/            # Business logic (Pure functions, no Express imports)
-├── middleware/          # Express middleware (errorHandler.ts, auth.ts)
-├── types/               # Shared TypeScript interfaces & Zod schemas
-└── server.ts            # Entry point
-```
-
-## Naming Conventions
-
-| Artifact            | Convention                 | Example           |
-| ------------------- | -------------------------- | ----------------- |
-| Files               | `kebab-case`               | `user.service.ts` |
-| Classes / Types     | `PascalCase`               | `UserResponse`    |
-| Functions/Variables | `camelCase`                | `getUserById`     |
-| Routes              | plural nouns, `kebab-case` | `/api/users/:id`  |
-
-## Architectural Patterns
-
-**3-Layer Architecture:**
-`Route -> Controller -> Service`
-Routes bind paths to Controllers. Controllers parse typed requests using Zod and pass data to Services. Services execute logic and return typed objects. No business logic in routes or controllers.
-
-**Global Error Handling:**
-Wrap all controllers in `express-async-errors`. Throw custom `AppError` classes in services; let the global error middleware format the JSON response. Never write inline `try/catch` in controllers.
-
-**Environment Validation:**
-Validate `process.env` at startup using **Zod**. Fail fast if a required variable is missing. Export a typed `config` object so the rest of the app never touches `process.env` directly.
-
-## Testing Strategies
-
-| Layer      | Test Type   | Framework          | File Naming               |
-| ---------- | ----------- | ------------------ | ------------------------- |
-| Service    | Unit        | Vitest             | `user.service.test.ts`    |
-| Controller | Integration | Supertest + Vitest | `user.controller.test.ts` |
diff --git a/skill-templates/react-native-expo/SKILL.md b/skill-templates/react-native-expo/SKILL.md
index b4bba6d..46c74b6 100644
--- a/skill-templates/react-native-expo/SKILL.md
+++ b/skill-templates/react-native-expo/SKILL.md
@@ -1,19 +1,20 @@
 ---
 name: mobile-architecture-react-native-expo
-description: Expo Router, React Native components, and cross-platform UI
+description: Expo Managed Workflow, Expo Router, NativeWind, and Strict TypeScript for zero-hallucination cross-platform apps.
 ---

-# React Native (Expo) — Best Practices
+# React Native (Expo) — AI-Native Scaffolding

-## AI Context & Token Optimization
+## AI Context & Token Optimization (Zero-Hallucination Rules)

-1. **Expo Router:** Use file-based routing (`app/`). It drastically reduces navigation boilerplate, keeping the AI's context focused on the component UI rather than navigation prop-drilling.
-2. **NativeWind:** Prefer NativeWind (Tailwind for RN) over `StyleSheet.create`. It reduces line count by 40%, saving massive amounts of tokens per file.
-3. **Zustand State:** Avoid Redux. Zustand provides the simplest API footprint for AI-managed global state.
+1. **Expo Managed Workflow ONLY:** You are strictly BANNED from modifying `ios/` or `android/` native folders, `Podfile`, or `build.gradle`. Native configuration causes massive AI hallucinations. Use Expo Config plugins instead.
+2. **Strict TypeScript:** Pure JavaScript is banned. All components, props, and API responses must be strongly typed.
+3. **Expo Router:** Use file-based routing (`app/`). It drastically reduces navigation boilerplate.
+4. **NativeWind:** Use NativeWind (Tailwind for RN) over `StyleSheet.create`. It reduces line count and token usage significantly.

 ## Project Structure

-```
+```text
 project/
 ├── app/                 # Expo Router file-based routing
 │   ├── (auth)/          # Authentication flow
@@ -35,12 +36,12 @@ project/

 ## Architectural Patterns

-- **Expo Router**: Use the `app/` directory for file-based routing. Use `Link` from `expo-router` for navigation.
-- **Styling**: Use `StyleSheet.create` for static styles, or NativeWind for Tailwind CSS support in React Native.
-- **Safe Areas**: Always wrap top-level screen views in `SafeAreaView` from `react-native-safe-area-context` to prevent UI clipping by notches/status bars.
-- **Performance**: Use `FlashList` or `FlatList` for long lists. Never use `ScrollView` for rendering massive amounts of data.
+- **Expo Router**: Use the `app/` directory for routing. Use `<Link>` from `expo-router`.
+- **Styling**: NativeWind is mandatory. Keep styles inline as utility classes.
+- **State**: Use `Zustand`. Avoid Redux.
+- **Safe Areas**: Wrap top-level screen views in `SafeAreaView` from `react-native-safe-area-context`.

 ## Testing Strategies

 - **Framework**: `Jest` + `@testing-library/react-native`.
-- **Component Testing**: Test component rendering and user interactions natively. Mock platform-specific native modules (like `expo-camera` or `expo-location`).
+- **Approach**: Test component rendering and user interactions natively.
\ No newline at end of file
````

<!-- END_GIT_DIFF -->
