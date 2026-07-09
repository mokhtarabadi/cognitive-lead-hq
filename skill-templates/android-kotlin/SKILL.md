---
name: mobile-architecture-android-kotlin
description: 100% Jetpack Compose, MVI (UDF), Hilt, and SQLDelight for token-efficient, zero-hallucination Android development.
---

# Android (Kotlin) — "Max Power" AI-Driven Architecture

## AI Context & Token Optimization (Zero-Hallucination Rules)

1. **XML IS STRICTLY BANNED:** Never generate `.xml` layout files. XML forces cross-file context mapping which causes severe UI hallucinations.
2. **100% Jetpack Compose:** Write all UI in declarative Kotlin. Break large UIs into extremely small, pure `@Composable` functions.
3. **Strict Null-Safety:** Rely entirely on Kotlin's null-safety. Do not use `!!` unless absolutely necessary.
4. **Compile-Time Safety for DB:** Use SQLDelight or Room. Do NOT use raw string SQL queries in repositories.

## Project Structure

```text
com.company.project/
├── di/                          # Hilt DI modules
├── data/                        # Data layer (SQLDelight/Room DAOs, DTOs, Repositories)
├── domain/                      # Domain layer (Pure Kotlin Models, UseCases)
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
Every screen uses a single `ViewModel` annotated with `@HiltViewModel`. The ViewModel exposes exactly one `StateFlow<UiState>`. The View sends sealed `Intents` to the ViewModel. This eliminates race conditions and makes the reasoning traceable through a single `when(intent)` reducer block.

**Dependency Injection:**
Hilt is mandatory. Do not write manual dependency factories.

## Testing Strategies

| Layer           | Test Type                  | Framework                     |
| --------------- | -------------------------- | ----------------------------- |
| Use cases       | Unit                       | JUnit 5 + MockK               |
| ViewModel (MVI) | Unit (Intent injection)    | JUnit 5 + Turbine (for Flows) |
| UI / Composable | Snapshot / Compose UI Test | Compose Test                  |