# Task: Max Power Skill Templates — Elite AI Architectural Upgrades

**Type:** improvement
**Status:** closed

## Goal

Upgrade the repository's skill templates to maximize AI agent reasoning performance by enforcing strict, strongly-typed, compile-time-safe architectural boundaries. This eliminates the hallucination-prone freedom of legacy patterns (MVVM, MVC, dynamic languages) and replaces them with ultra-constrained "Max Power" architectures.

## Manager's Notes

- **Android Kotlin skill (`android-kotlin/SKILL.md`):** Patched from MVVM to strict MVI/UDF. ParsePlatform references removed in favor of gRPC/Ktor. Offline-First Room caching mandated. Added a complete Kotlin code example showing the MVI contract (sealed Intent, single StateFlow, reducer-style ViewModel).
- **Go Hexagonal gRPC skill (`go-hexagonal-grpc/SKILL.md`):** Created to serve the ultra-low-latency Caller ID backend. Enforces Hexagonal Architecture with Ports & Adapters, gRPC, Uber Fx compile-time DI, and Redis caching. Explicitly forbids GORM and reflection-heavy patterns.
- **Prompt Refactor skill (`prompt-refactor/SKILL.md`):** Created as a meta-cognitive workflow skill. Takes basic human instructions and rewrites them into elite XML-tagged system prompts with `<role>`, `<system_context>`, `<agentic_reasoning>`, `<constraints>`, and `<output_format>` blocks.
- **Task 20:** This task file tracks the implementation. Task 19 was the debug-instrumentation skill.

## Local TODOs

- [x] Initial codebase exploration
- [x] Read and understand existing android-kotlin SKILL.md
- [x] Read go-gin SKILL.md for Go template reference
- [x] Update `skill-templates/android-kotlin/SKILL.md` with MVI/UDF/Offline-First architecture
- [x] Create `skill-templates/go-hexagonal-grpc/SKILL.md`
- [x] Create `skill-templates/prompt-refactor/SKILL.md`
- [x] Update `CHANGELOG.md`
- [x] Run prettier to verify markdown formatting
- [x] Call `custom_context_stage_and_inject_diff` to finalize

## OpenCode Execution Log & Reasoning

_(OpenCode: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

### Architectural Reasoning

**Why MVI over MVVM?** Standard MVVM allows the View to call arbitrary ViewModel functions, which means the AI can scatter state mutations across multiple entry points. MVI forces ALL user actions through a single `onIntent(intent:)` chokepoint, turning the ViewModel into a pure reducer. This eliminates race conditions and makes the AI's reasoning traceable through a single `when(intent)` chain.

**Why Hexagonal Architecture over Clean Architecture for Go?** Clean Architecture layers (Handler -> Service -> Repository) leak infrastructure concerns into the service layer. Pure Hexagonal (Ports & Adapters) forces the AI to define explicit interfaces in the `core/ports/` layer, which then get implemented in `adapters/outbound/`. The compiler catches missing implementations instantly. This is critical for gRPC backends where proto-generated interfaces must match adapter code exactly.

**Why a Prompt Refactor skill?** The Manager often sends short, informal instructions. Human ambiguity is the #1 cause of AI hallucination. This skill reframes any instruction into a structured XML prompt that forces the AI to reason, constrain itself, and output parsable results.

### Files Changed

1. **`skill-templates/android-kotlin/SKILL.md`** — Updated description, initiation guide, project structure (gRPC/Ktor instead of Retrofit/ParsePlatform), architectural patterns (MVI with code example), DI references, and testing table.
2. **`skill-templates/go-hexagonal-grpc/SKILL.md`** — Created new skill for Go Hexagonal Architecture with gRPC, Uber Fx, Redis, and PostgreSQL.
3. **`skill-templates/prompt-refactor/SKILL.md`** — Created new meta-cognitive skill for refactoring human prompts into elite XML-tagged system instructions.
4. **`tasks/20-max-power-skill-templates.md`** — This file.
5. **`CHANGELOG.md`** — Added v5.13.0 entry.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index e20c3eb..1f1f7ae 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -122,6 +122,17 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

 ## [Unreleased]

+## [5.13.0] — 2026-06-30
+
+### Added
+
+- **`skill-templates/go-hexagonal-grpc/SKILL.md`:** New Agent Skill template for Go Hexagonal Architecture (Ports & Adapters) with gRPC, Uber Fx compile-time DI, Redis caching, and PostgreSQL (pgx/ent). Designed for ultra-low-latency backends like the Caller ID system.
+- **`skill-templates/prompt-refactor/SKILL.md`:** New meta-cognitive Agent Skill template for refactoring basic human prompts into elite, XML-tagged, agent-optimized system instructions with `<role>`, `<system_context>`, `<agentic_reasoning>`, `<constraints>`, and `<output_format>` blocks.
+
+### Changed
+
+- **`skill-templates/android-kotlin/SKILL.md`:** Upgraded from MVVM to strict MVI (Model-View-Intent) with Unidirectional Data Flow. ParsePlatform references replaced with gRPC/Ktor. Offline-First Room caching mandated. Added a complete Kotlin MVI contract example with sealed Intents and reducer-style ViewModel.
+
 ## [5.12.0] — 2026-06-29

 ### Added
diff --git a/skill-templates/android-kotlin/SKILL.md b/skill-templates/android-kotlin/SKILL.md
index 69ec62c..83f904c 100644
--- a/skill-templates/android-kotlin/SKILL.md
+++ b/skill-templates/android-kotlin/SKILL.md
@@ -1,22 +1,22 @@
 ---
 name: mobile-architecture-android-kotlin
-description: Jetpack Compose, MVVM, Clean Architecture, Coroutines, and Hilt for Android Kotlin
+description: Jetpack Compose, MVI (UDF), Clean Architecture, Offline-First Room, and Hilt for Android Kotlin
 ---

-# Android (Kotlin) — Best Practices & AI-Driven Scaffolding
+# Android (Kotlin) — "Max Power" AI-Driven Architectural Scaffolding

 ## Modern Project Initiation Guide

-When launching an Android Kotlin application from scratch, initialize using the following strict architectural directives:
+When launching an Android Kotlin application (especially high-performance or offline-first apps like Caller ID) from scratch, initialize using the following strict architectural directives:

 1. **100% Jetpack Compose UI:** Never generate XML layout files. Use the Material 3 design system exclusively.
 2. **Single-Activity Architecture:** Use a single `MainActivity.kt` with a Compose `NavHost` configured for standard type-safe navigation routes.
-3. **MVVM + Clean Architecture:** Group packages strictly by feature:
+3. **MVI + UDF + Clean Architecture:** Group packages strictly by feature. Enforce Unidirectional Data Flow. The View sends sealed `Intents` to the ViewModel, which reduces them into a single `UiState` via a reducer function.
    - `domain/` — Contains pure Kotlin models, repository interfaces (ports), and UseCases. No Android framework dependencies.
-   - `data/` — Implements repository interfaces. Coordinates remote (ParsePlatform or API) and local (Room) data sources.
+   - `data/` — Implements repository interfaces. Prioritizes local caching (Room) for Offline-First capabilities, falling back to remote (gRPC/API).
    - `ui/` — Houses Compose screens, individual components, and ViewModels.
-4. **ParsePlatform Integration:** Always query the Parse SDK directly. Never write Retrofit wrappers or REST interfaces around Parse endpoints.
-5. **Kotlin Coroutines & Flow:** Use `StateFlow<UiState>` for rendering state, `SharedFlow` for one-time events (navigation, snackbars), and `viewModelScope` for scoping. Never use legacy LiveData or RxJava.
+4. **Network & Protocol:** Use gRPC via Wire or Ktor for high-performance, low-latency connections, especially over unstable networks.
+5. **Kotlin Coroutines & Flow:** Use `StateFlow<UiState>` for rendering state, `SharedFlow` for one-time events, and `viewModelScope` for scoping. Never use LiveData or RxJava.
 6. **Dependency Injection:** Hilt is mandatory. Annotate ViewModels with `@HiltViewModel` and inject constructor dependencies using `@Inject`.
 7. **Localization (en/fa):** All strings must be declared in `strings.xml`. Persian strings must reside inside `values-fa/strings.xml`. Ensure RTL support using `LocalLayoutDirection` on RTL screens.

@@ -33,9 +33,9 @@ com.company.project/
 │   │   │   └── UserDao.kt
 │   │   └── entity/
 │   │       └── UserEntity.kt
-│   ├── remote/                  # Retrofit API services
-│   │   ├── api/
-│   │   │   └── UserApi.kt
+│   ├── remote/                  # gRPC / Ktor API services
+│   │   ├── grpc/
+│   │   │   └── UserGrpcService.kt
 │   │   └── dto/
 │   │       └── UserResponse.kt
 │   └── repository/              # Repository implementations
@@ -82,18 +82,60 @@ UI (Compose + ViewModel) → Domain (UseCases + Models) → Data (Repositories +

 - **UI Layer**: Composable screens observe `StateFlow` from ViewModels. No business logic.
 - **Domain Layer**: Pure Kotlin module. Contains use cases and repository interfaces. No Android framework imports.
-- **Data Layer**: Implements repository interfaces. Coordinates local (Room) and remote (Retrofit) data sources.
+- **Data Layer**: Implements repository interfaces. Coordinates local (Room) and remote (gRPC/Retrofit) data sources with Offline-First priority.

-### MVVM (Model-View-ViewModel)
+### MVI (Model-View-Intent) with Unidirectional Data Flow

-Every screen gets a `ViewModel` that exposes `StateFlow<UiState>` and functions for user interactions. The Composable observes state and calls ViewModel methods. ViewModels survive configuration changes and are scoped to the navigation entry.
+Every screen gets a `ViewModel` that exposes a single `StateFlow<UiState>` and accepts a single `onIntent(intent: ViewIntent)` function. This eliminates race conditions in UI rendering. The ViewModel acts as a reducer: incoming Intents produce new UiState via aggregation over time.

```

-UserEvent → ViewModel → UseCase → Repository → DataSource

-                              ↓
-                         StateFlow<UiState>
-                              ↓
-                        Composable Screen

+User Action → sealed Intent → ViewModel (Reducer) → UseCase → Repository

-                                         ↓
-                                    StateFlow<UiState>
-                                         ↓
-                                   Composable Screen

+`
+
+`kotlin
+// Example MVI Contract
+data class CallerIdUiState(

- val phoneNumber: String = "",
- val displayName: String? = null,
- val isLoading: Boolean = false,
- val error: String? = null
  +)
-

+sealed interface CallerIdIntent {

- data class LookupNumber(val number: String) : CallerIdIntent
- data object Retry : CallerIdIntent
- data object Clear : CallerIdIntent
  +}
-

+@HiltViewModel
+class CallerIdViewModel @Inject constructor(

- private val lookupNumberUseCase: LookupNumberUseCase
  +) : ViewModel() {
-
- private val _uiState = MutableStateFlow(CallerIdUiState())
- val uiState: StateFlow<CallerIdUiState> = _uiState.asStateFlow()
-
- fun onIntent(intent: CallerIdIntent) {
-        when (intent) {
-            is CallerIdIntent.LookupNumber -> lookupNumber(intent.number)
-            CallerIdIntent.Retry -> retry()
-            CallerIdIntent.Clear -> clear()
-        }
- }
-
- private fun lookupNumber(number: String) {
-        _uiState.update { it.copy(isLoading = true, error = null) }
-        viewModelScope.launch {
-            lookupNumberUseCase(number)
-                .onSuccess { name -> _uiState.update { it.copy(displayName = name, isLoading = false) } }
-                .onFailure { e -> _uiState.update { it.copy(error = e.message, isLoading = false) } }
-        }
- }
  +}

````

### Jetpack Compose
@@ -114,7 +156,7 @@ UserEvent → ViewModel → UseCase → Repository → DataSource
### Dependency Injection via Hilt

- Annotate constructors with `@Inject` for simple cases.
-- Create `@Module` classes for interfaces and third-party objects (`Retrofit`, `Room`).
+- Create `@Module` classes for interfaces and third-party objects (`gRPC/Ktor`, `Room`).
- Scope singletons properly (`@Singleton`, `@ViewModelScoped`, `@ActivityScoped`).

## Testing Strategies
@@ -122,7 +164,7 @@ UserEvent → ViewModel → UseCase → Repository → DataSource
| Layer           | Test Type                  | Framework                     | File Naming                 |
| --------------- | -------------------------- | ----------------------------- | --------------------------- |
| Use cases       | Unit                       | JUnit 5 + Mockito / MockK     | `GetUserUseCaseTest.kt`     |
-| ViewModel       | Unit                       | JUnit 5 + Turbine (for Flows) | `ProfileViewModelTest.kt`   |
+| ViewModel (MVI) | Unit (Intent injection)    | JUnit 5 + Turbine (for Flows) | `CallerIdViewModelTest.kt`  |
| Repository      | Unit                       | JUnit 5 + MockK               | `UserRepositoryImplTest.kt` |
| UI / Composable | Snapshot / Compose UI Test | Compose Test                  | `ProfileScreenTest.kt`      |

diff --git a/skill-templates/go-hexagonal-grpc/SKILL.md b/skill-templates/go-hexagonal-grpc/SKILL.md
new file mode 100644
index 0000000..7780810
--- /dev/null
+++ b/skill-templates/go-hexagonal-grpc/SKILL.md
@@ -0,0 +1,82 @@
+---
+name: backend-architecture-go-hexagonal-grpc
+description: Hexagonal Architecture (Ports and Adapters), gRPC, Uber Fx, and Redis caching for ultra-low latency Go backends.
+---
+
+# Go (Golang) — "Max Power" Agentic Backend Architecture
+
+## Modern Project Initiation Guide
+
+When scaffolding a high-performance backend (such as a sub-50ms latency Caller ID system), enforce the following strict rules to maximize AI reasoning and eliminate runtime magic:
+
+1. **Hexagonal Architecture (Ports & Adapters):** Strictly separate the core business logic (Domain) from external concerns (gRPC, PostgreSQL, Redis). The Domain layer must have zero dependencies on external libraries.
+2. **gRPC-First:** Use protocol buffers (`.proto`) as the single source of truth for all API contracts. Generate Go interfaces from proto files.
+3. **Compile-Time DI:** Use **Uber Fx** or **Google Wire** for dependency injection. This forces the AI to explicitly declare dependencies, resulting in instant compile-time feedback if a dependency is missing.
+4. **Caching Layer:** Implement **Redis** via the `go-redis` client for all read-heavy, low-latency lookups (e.g., spam number checks).
+5. **Database:** Use **PostgreSQL** with `pgx` for raw, high-performance database interactions, or `ent` (by Facebook) if a strongly-typed ORM is required. Avoid reflection-heavy ORMs like GORM.
+
+## Project Structure
+
+```
+project-root/
+├── cmd/
+│   └── server/
+│       └── main.go              # Entry point, initializes Uber Fx application
+├── internal/
+│   ├── core/
+│   │   ├── domain/              # Pure Go structs (e.g., PhoneNumber.go)
+│   │   └── ports/               # Interfaces (e.g., CacheRepository, CallService)
+│   ├── application/             # Use cases implementing inbound ports
+│   │   └── call_service.go
+│   ├── adapters/
+│   │   ├── inbound/
+│   │   │   └── grpc/            # gRPC handlers implementing proto generated interfaces
+│   │   └── outbound/
+│   │       ├── postgres/        # PostgreSQL repository implementations
+│   │       └── redis/           # Redis cache repository implementations
+│   └── di/                      # Uber Fx module providers
+├── api/
+│   └── proto/                   # .proto definition files
+├── pkg/                         # Shared libraries (logging, metrics)
+├── go.mod
+└── Makefile                     # Protoc generation and build commands
+```
+
+## Naming Conventions
+
+| Artifact           | Convention           | Example                     |
+| ------------------ | -------------------- | --------------------------- |
+| Interfaces (Ports) | Nouns ending in `er` | `CallReader`, `CacheWriter` |
+| Structs            | `PascalCase`         | `CallScreeningRequest`      |
+| Files              | `snake_case.go`      | `call_service.go`           |
+| DI Providers       | Prefix with `New`    | `NewPostgresRepository`     |
+
+## Architectural Patterns
+
+### Functional Options Pattern
+
+Use this for configuring complex structures (like external client adapters) cleanly:
+
+```go
+type Server struct { ... }
+type Option func(*Server)
+
+func WithTimeout(t time.Duration) Option {
+    return func(s *Server) { s.timeout = t }
+}
+```
+
+### Error Handling (Self-Healing for AI)
+
+Never panic. Return errors explicitly. Wrap errors with context using `%w` so the AI agent reading the logs can trace the exact failure path:
+`return fmt.Errorf("redis cache miss for number %s: %w", number, err)`
+
+## Testing Strategies
+
+| Layer       | Test Type   | Framework / Tools                                     |
+| ----------- | ----------- | ----------------------------------------------------- |
+| Application | Unit        | `testing` + `testify/assert` + `mockery` (for ports)  |
+| Adapters    | Integration | `testcontainers-go` (spin up real Redis/PG in Docker) |
+
+- Generate mocks for all interfaces in `internal/core/ports` using `mockery`.
+- AI must write table-driven tests (`[]struct`) for all core business logic.
diff --git a/skill-templates/prompt-refactor/SKILL.md b/skill-templates/prompt-refactor/SKILL.md
new file mode 100644
index 0000000..5a72322
--- /dev/null
+++ b/skill-templates/prompt-refactor/SKILL.md
@@ -0,0 +1,64 @@
+---
+name: prompt-refactor
+description: Refactors basic user prompts into elite, highly constrained, XML-tagged instructions optimized for AI agent reasoning.
+---
+
+# Prompt Refactoring & Enhancement Protocol
+
+You are an expert Prompt Engineer and Cognitive Architect. Your job is to take a basic, informal, or weak instruction from the Manager and rewrite it into a "Max Power" system instruction that guarantees maximum logical reasoning and zero hallucination from an AI agent.
+
+## The "Max Power" Prompt Anatomy
+
+When asked to refactor a prompt, you MUST output a markdown block containing a prompt structured with these exact XML tags:
+
+### 1. `<role>`
+
+Define the exact persona the AI must adopt (e.g., Senior Systems Programmer, UI/UX Expert). Establish its domain authority.
+
+### 2. `<system_context>`
+
+Define the environment the AI is operating in. What tools does it have? What are the boundaries of its knowledge?
+
+### 3. `<agentic_reasoning>`
+
+This is the most critical block. You must instruct the target AI to output a `<reasoning_log>` BEFORE taking any action. The reasoning log must force the AI to evaluate:
+
+1. Logical dependencies
+2. Risk assessment
+3. Abductive reasoning (why did a bug happen?)
+4. Precision and Grounding
+
+### 4. `<execution_rules>` or `<constraints>`
+
+Provide a bulleted list of strict "DO NOT" and "MUST DO" rules.
+
+- Force the AI to use specific architectural patterns (e.g., "You MUST use MVI and Unidirectional Data Flow").
+- Forbid lazy behavior (e.g., "Do NOT output placeholder code. Do NOT hallucinate variables").
+
+### 5. `<output_format>`
+
+Provide the exact XML or JSON structure the AI must use to reply, ensuring it can be parsed by automated pipelines or easily copied by the Manager.
+
+## Workflow Execution
+
+1. **Analyze:** Read the Manager's raw prompt. Identify the core goal, the missing technical constraints, and the desired outcome.
+2. **Draft:** Construct the prompt using the 5 XML blocks above.
+3. **Refine:** Ensure the language is highly authoritative, objective, and precise. Remove all conversational filler.
+4. **Deliver:** Output the final prompt inside a markdown code block ` ```markdown ` so the Manager can easily copy it.
+
+## Example Output Format
+
+```markdown
+<role>
+You are an elite Golang Systems Architect...
+</role>
+
+<constraints>
+- You MUST use Hexagonal Architecture.
+- You are strictly forbidden from bypassing the Repository pattern.
+</constraints>
+
+<agentic_reasoning>
+Before writing code, you must output a <reasoning_log> analyzing the memory safety and big-O notation of your proposed algorithm.
+</agentic_reasoning>
+```
````

<!-- END_GIT_DIFF -->
