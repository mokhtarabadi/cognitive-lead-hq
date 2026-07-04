---
name: mobile-architecture-ios-swiftui
description: SwiftUI, MVVM, and modern iOS app architecture
---

# iOS (SwiftUI) — Best Practices

## AI Context & Token Optimization

1. **SwiftUI Over UIKit:** Strictly ban UIKit (unless bridging is unavoidable). Declarative SwiftUI trees are vastly more token-efficient and predictable for AI generation.
2. **Modern Concurrency:** Mandate `async/await`. Avoid completion handlers and closures, which lead to "callback hell" formatting that breaks AI syntax continuity.
3. **Observable State:** Use `@Observable` (iOS 17+) to keep state management clean and localized, preventing cross-file state hallucinations.

## Project Structure

```
App/
├── App.swift            # @main struct
├── Core/                # Networking, Extensions, Utilities
├── Models/              # Data structures (Codable)
├── Views/               # SwiftUI Views
│   ├── Shared/          # Reusable components
│   └── Screens/         # Full page views
└── ViewModels/          # ObservableObjects for business logic
```

## Naming Conventions

- **Types/Structs/Classes**: `PascalCase` (e.g., `UserProfileView`)
- **Variables/Functions**: `camelCase` (e.g., `fetchUserData()`)
- **Modifiers**: Custom ViewModifiers should be `PascalCase`.

## Architectural Patterns

- **MVVM Pattern**: Separate UI (View) from business logic (ViewModel). Views should only handle layout and state binding.
- **State Management**:
  - Use `@State` for simple, local UI state.
  - Use `@StateObject` (or `@Observable` macro in iOS 17+) for ViewModels owned by the view.
  - Use `@EnvironmentObject` (or `@Environment`) for global dependency injection.
- **Networking**: Use modern `async/await` (`URLSession.shared.data(from:)`). Avoid legacy closures/completion blocks.
- **Concurrency**: Use `@MainActor` on ViewModels to ensure UI updates happen on the main thread.

## Testing Strategies

- **Framework**: `XCTest` + `XCUITest`.
- **Unit Tests**: Test ViewModels independently of Views. Inject mock network clients via protocols to verify state changes.
- **UI Tests**: Use Accessibility Identifiers (`.accessibilityIdentifier("login_btn")`) to write stable UI tests.
