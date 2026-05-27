---
name: backend-architecture-go-gin
description: Idiomatic Go, Clean Architecture, and Gin routing best practices
---

# Go (Gin) — Best Practices

## Project Structure

```
project/
├── cmd/                 # Application entry points
│   └── server/
│       └── main.go
├── internal/            # Private application code
│   ├── config/          # Environment loading (viper/godotenv)
│   ├── handlers/        # Gin HTTP handlers/controllers
│   ├── models/          # Domain structs and interfaces
│   ├── repository/      # Database access layer
│   └── service/         # Business logic
├── pkg/                 # Public utility libraries (optional)
├── go.mod
└── go.sum
```

## Naming Conventions

- **Files/Directories**: `snake_case` or `lowercase` (e.g., `user_repository.go`)
- **Structs/Interfaces**: `PascalCase` for exported, `camelCase` for unexported.
- **Functions**: `PascalCase` (e.g., `CreateUser`).
- **Interfaces**: Usually end in `-er` (e.g., `UserReader`, `DataWriter`).

## Architectural Patterns

- **Clean Architecture**: `Handler -> Service -> Repository`. Handlers parse JSON and return HTTP codes. Services hold business logic. Repositories handle SQL.
- **Dependency Injection**: Pass interfaces into constructors. e.g., `func NewUserService(repo models.UserRepository) *UserService`.
- **Error Handling**: Never panic. Always return `error` as the last return value. Wrap errors with context (`fmt.Errorf("failed to fetch user: %w", err)`).
- **Goroutines**: Use carefully for background tasks; always pass `context.Context` down the call chain to handle timeouts and cancellation.

## Testing Strategies

- **Framework**: Standard `testing` package + `testify` for assertions/mocks.
- **Mocking**: Generate mocks from interfaces using `mockery` or `gomock` for the Repository and Service layers.
- **Table-Driven Tests**: Use slice-of-structs to test multiple inputs/outputs in a single test function.
