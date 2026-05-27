---
name: mobile-architecture-android-java-xml
description: MVC/MVP, ViewBinding, lifecycle management, and RxJava for Android Java
---

# Android (Java + XML) — Best Practices

## Project Structure

```
com.company.project/
├── adapter/                  # RecyclerView adapters
│   └── UserAdapter.java
├── model/                    # Plain Java models (POJOs)
│   └── User.java
├── network/                  # Retrofit API / network layer
│   ├── ApiClient.java
│   └── ApiService.java
├── repository/               # Data repository
│   └── UserRepository.java
├── ui/                       # Activity / Fragment packages
│   ├── auth/
│   │   ├── LoginActivity.java
│   │   └── LoginFragment.java
│   └── profile/
│       ├── ProfileActivity.java
│       └── ProfileFragment.java
├── utils/                    # Utility classes
│   └── DateUtils.java
└── viewmodel/                # ViewModel classes (if using MVVM)
    └── ProfileViewModel.java

res/
├── layout/                   # XML layouts
│   ├── activity_login.xml
│   └── fragment_profile.xml
├── values/
│   ├── strings.xml
│   ├── colors.xml
│   └── themes.xml
├── drawable/                 # Vector drawables & shape XMLs
└── menu/
```

## Naming Conventions

| Artifact            | Convention                         | Example                                      |
| ------------------- | ---------------------------------- | -------------------------------------------- |
| Files (Java)        | `PascalCase`                       | `LoginActivity.java`                         |
| Classes             | `PascalCase`                       | `UserRepository`                             |
| Methods / Variables | `camelCase`                        | `getUserById`                                |
| Constants           | `UPPER_SNAKE_CASE`                 | `MAX_RETRY_COUNT`                            |
| Layout XML          | `snake_case` prefix with component | `activity_login.xml`, `fragment_profile.xml` |
| Resource IDs        | `snake_case`                       | `@+id/btn_submit`                            |
| String keys         | `snake_case`                       | `error_network`                              |

## Architectural Patterns

### MVC (Model-View-Controller)

- **Model**: POJOs, repositories, network layer.
- **View**: XML layouts, Activity/Fragment acting as the View (or thin Controller).
- **Controller**: For complex screens, introduce a dedicated Controller/Presenter class that handles business logic and delegates to the View via an interface.

### MVP (Model-View-Presenter) — Preferred for Complex Screens

```
View (Activity/Fragment) ←→ Presenter ←→ Model (Repository)
```

- The Presenter holds all business logic.
- The View interface is implemented by the Activity/Fragment — the Presenter calls view methods (e.g., `showUsers(List<User>)`, `showError(String)`).
- Presenters survive rotation by detaching/re-attaching the View reference.

### ViewBinding (No `findViewById`)

- Enable `viewBinding` in `build.gradle`.
- Every layout generates a `Binding` class (e.g., `ActivityLoginBinding`).
- Inflate and hold the binding in the Activity/Fragment; access views via `binding.textViewName`.
- Never use `findViewById` — it is error-prone and verbose.

### Activity / Fragment Lifecycle Management

- Initialize components in `onCreate` (Activity) or `onCreateView` (Fragment).
- Start loading data in `onStart` or `onResume`; cancel in `onPause` or `onStop`.
- Use `savedInstanceState` to preserve transient UI state across configuration changes.
- For retained data across rotation, use `ViewModel` (even with Java) or a retained fragment (`setRetainInstance(true)`).
- Avoid memory leaks: null out heavy references (Bitmap, large collections) in `onDestroy`.

### Background Threading

- Use **RxJava** (Observables/Single/Flowable) for composable async operations and thread switching (`subscribeOn`/`observeOn`).
- Alternatively, use `ExecutorService` + `Handler` for simpler cases.
- Never perform network or database operations on the main thread.
- Use `CompositeDisposable` (RxJava) to manage subscriptions and dispose in `onDestroy`.

## Testing Strategies

| Layer                 | Test Type       | Framework         | File Naming               |
| --------------------- | --------------- | ----------------- | ------------------------- |
| Repository            | Unit            | JUnit 4 + Mockito | `UserRepositoryTest.java` |
| Presenter / ViewModel | Unit            | JUnit 4 + Mockito | `LoginPresenterTest.java` |
| Utils                 | Unit            | JUnit 4           | `DateUtilsTest.java`      |
| UI / Activity         | Instrumentation | Espresso          | `LoginActivityTest.java`  |

- Use **JUnit 4** (standard for Android Java projects).
- Use **Mockito** for mocking dependencies.
- Use **Espresso** for UI interaction tests — test on the UI thread with `onView()` matchers.
- Use **Robolectric** for fast local testing of Android framework-dependent code (no emulator required).
- Keep tests in `src/test/java/` (unit) and `src/androidTest/java/` (instrumentation).
