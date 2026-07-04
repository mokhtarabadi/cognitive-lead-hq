---
name: mobile-architecture-android-kotlin
description: Jetpack Compose, MVI (UDF), and Kotlin for token-efficient Android development.
---

# Android (Kotlin) — "Max Power" AI-Driven Architectural Scaffolding

## AI Context & Token Optimization

1. **XML is Strictly Banned:** Never generate `.xml` layout files. XML forces the AI to maintain cross-file context (matching IDs between Kotlin and XML), which wastes tokens and causes layout binding hallucinations.
2. **100% Jetpack Compose:** Write all UI in declarative Kotlin. Compose allows the AI to generate UI and logic in a single, predictable, token-efficient tree.
3. **Modular Composables:** Break large UIs into extremely small, pure `@Composable` functions. The AI struggles to modify 500-line Compose functions without breaking brackets.

## Modern Project Initiation Guide

When launching an Android Kotlin application (especially high-performance or offline-first apps like Caller ID) from scratch, initialize using the following strict architectural directives:

1. **Single-Activity Architecture:** Use a single `MainActivity.kt` with a Compose `NavHost`.
2. **MVI + UDF + Clean Architecture:** Group packages strictly by feature. Enforce Unidirectional Data Flow. The View sends sealed `Intents` to the ViewModel, which reduces them into a single `UiState`.
3. **Network & Protocol:** Use gRPC via Wire or Ktor for high-performance connections.
4. **Dependency Injection:** Hilt is mandatory. Annotate ViewModels with `@HiltViewModel`.

## Project Structure

```
com.company.project/
├── di/                          # Hilt DI modules
├── data/                        # Data layer (Room DAOs, gRPC DTOs, Repositories)
├── domain/                      # Domain layer (Pure Kotlin Models, Repository Interfaces, UseCases)
└── ui/                          # Presentation layer
    ├── theme/                   # Compose theming (Color, Type, Theme)
    ├── component/               # Small, reusable, modular composables
    └── screen/                  # Feature screens and ViewModels
```

## Naming Conventions

| Artifact               | Convention         | Example            |
| ---------------------- | ------------------ | ------------------ |
| Files / Composables    | `PascalCase`       | `ProfileScreen.kt` |
| Classes / Interfaces   | `PascalCase`       | `GetUserUseCase`   |
| Functions / Properties | `camelCase`        | `getUserById`      |
| Constants              | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT`  |

## Architectural Patterns

**MVI (Model-View-Intent) + UDF:**
Every screen uses a single `ViewModel`. The ViewModel exposes exactly one `StateFlow<UiState>`. The View sends sealed `Intents` to the ViewModel. This eliminates race conditions and makes the AI's reasoning traceable through a single `when(intent)` reducer block.

**Supabase / BaaS Integration:**
For rapid AI development, prefer direct integration with Supabase/Firebase SDKs in the Data layer to eliminate custom backend boilerplate, unless a dedicated backend is provided.

## Testing Strategies

| Layer           | Test Type                  | Framework                     |
| --------------- | -------------------------- | ----------------------------- |
| Use cases       | Unit                       | JUnit 5 + MockK               |
| ViewModel (MVI) | Unit (Intent injection)    | JUnit 5 + Turbine (for Flows) |
| UI / Composable | Snapshot / Compose UI Test | Compose Test                  |
