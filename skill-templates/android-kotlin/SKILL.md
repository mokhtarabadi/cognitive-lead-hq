---
name: mobile-architecture-android-kotlin
description: Jetpack Compose, MVVM, Clean Architecture, Coroutines, and Hilt for Android Kotlin
---

# Android (Kotlin) — Best Practices

## Project Structure

```
com.company.project/
├── di/                          # Hilt DI modules
│   ├── AppModule.kt
│   └── NetworkModule.kt
├── data/                        # Data layer
│   ├── local/                   # Room DAOs, entities
│   │   ├── dao/
│   │   │   └── UserDao.kt
│   │   └── entity/
│   │       └── UserEntity.kt
│   ├── remote/                  # Retrofit API services
│   │   ├── api/
│   │   │   └── UserApi.kt
│   │   └── dto/
│   │       └── UserResponse.kt
│   └── repository/              # Repository implementations
│       └── UserRepositoryImpl.kt
├── domain/                      # Domain layer (pure Kotlin — no Android deps)
│   ├── model/                   # Domain models
│   │   └── User.kt
│   ├── repository/              # Repository interfaces (ports)
│   │   └── UserRepository.kt
│   └── usecase/                 # Use cases
│       └── GetUserUseCase.kt
└── ui/                          # Presentation layer
    ├── theme/                   # Compose theming
    │   ├── Theme.kt
    │   ├── Color.kt
    │   └── Type.kt
    ├── component/               # Reusable composables
    │   └── LoadingIndicator.kt
    └── screen/                  # Screens (one package per feature)
        └── profile/
            ├── ProfileScreen.kt
            └── ProfileViewModel.kt
```

## Naming Conventions

| Artifact               | Convention         | Example                 |
| ---------------------- | ------------------ | ----------------------- |
| Files                  | `PascalCase`       | `UserRepositoryImpl.kt` |
| Classes / Interfaces   | `PascalCase`       | `GetUserUseCase`        |
| Functions / Properties | `camelCase`        | `getUserById`           |
| Constants / Companions | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT`       |
| Composable functions   | `PascalCase`       | `ProfileScreen`         |
| XML resources          | `snake_case`       | `activity_main.xml`     |
| Navigation routes      | `camelCase`        | `profile/{userId}`      |

## Architectural Patterns

### Clean Architecture (3-Layer)

```
UI (Compose + ViewModel) → Domain (UseCases + Models) → Data (Repositories + DataSources)
```

- **UI Layer**: Composable screens observe `StateFlow` from ViewModels. No business logic.
- **Domain Layer**: Pure Kotlin module. Contains use cases and repository interfaces. No Android framework imports.
- **Data Layer**: Implements repository interfaces. Coordinates local (Room) and remote (Retrofit) data sources.

### MVVM (Model-View-ViewModel)

Every screen gets a `ViewModel` that exposes `StateFlow<UiState>` and functions for user interactions. The Composable observes state and calls ViewModel methods. ViewModels survive configuration changes and are scoped to the navigation entry.

```
UserEvent → ViewModel → UseCase → Repository → DataSource
                              ↓
                         StateFlow<UiState>
                              ↓
                        Composable Screen
```

### Jetpack Compose

- Prefer `StateFlow` over `LiveData` in ViewModels.
- Use `remember`, `LaunchedEffect`, and `derivedStateOf` for local state management.
- Keep composables stateless where possible — hoist state to the ViewModel.
- Use `Modifier` parameters for all reusable composables to allow parent customization.
- Follow Material 3 design with custom theme (Color, Typography, Shapes).

### Kotlin Coroutines & Flows

- Use `viewModelScope.launch` for ViewModel coroutines.
- Prefer `StateFlow` or `SharedFlow` for one-shot event emission (snackbars, navigation).
- Use `Flow.combine`, `flatMapLatest`, and `catch` operators for reactive data streams.
- Never use `GlobalScope`.

### Dependency Injection via Hilt

- Annotate constructors with `@Inject` for simple cases.
- Create `@Module` classes for interfaces and third-party objects (`Retrofit`, `Room`).
- Scope singletons properly (`@Singleton`, `@ViewModelScoped`, `@ActivityScoped`).

## Testing Strategies

| Layer           | Test Type                  | Framework                     | File Naming                 |
| --------------- | -------------------------- | ----------------------------- | --------------------------- |
| Use cases       | Unit                       | JUnit 5 + Mockito / MockK     | `GetUserUseCaseTest.kt`     |
| ViewModel       | Unit                       | JUnit 5 + Turbine (for Flows) | `ProfileViewModelTest.kt`   |
| Repository      | Unit                       | JUnit 5 + MockK               | `UserRepositoryImplTest.kt` |
| UI / Composable | Snapshot / Compose UI Test | Compose Test                  | `ProfileScreenTest.kt`      |

- Use `MockK` (preferred) or `Mockito` for mocking in Kotlin.
- Use **Turbine** library to test `StateFlow` and `SharedFlow` emissions.
- Use Compose UI Test (`createComposeRule`) to verify composable rendering and interactions.
- Run unit tests locally without an emulator — they should be pure JVM tests.
