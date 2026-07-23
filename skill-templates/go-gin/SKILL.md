---
name: go-gin
description: Idiomatic Go, Clean Architecture, and Gin routing best practices
---

# Go (Gin) — Best Practices

## AI Context & Token Optimization

1. **Explicit Error Handling:** Never `panic`. Always return errors explicitly (`%w`). This creates a traceable breadcrumb trail for AI debugging tools.
2. **Interface Isolation:** Define small interfaces at the consumer level (e.g., `UserRepository`). This makes AI-driven unit testing and mocking highly reliable.
3. **Flat Handlers:** Keep Gin handlers focused strictly on JSON parsing and HTTP codes. Offload all logic to the service layer to keep files small and token-efficient.

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

## Universal DateTime Governance

- **UTC Storage:** All `time.Time` fields MUST be stored and manipulated in UTC. Use `time.Now().UTC()` or `time.Now().In(time.UTC)` exclusively. Banned: `time.Now()` without explicit `.UTC()`.
- **Clock Interface:** Define a `Clock` interface (`Now() time.Time`) and inject it into services. Never call `time.Now()` directly in business logic.
- **API Format:** Transmit datetimes as Unix epoch seconds/milliseconds (int64) or RFC3339 strings. Use `time.RFC3339Nano` for maximum precision.
- **Database Mapping:** When reading from PostgreSQL, map `TIMESTAMPTZ` columns to `time.Time`. Never use string-based timestamp columns.

## Testing Strategies

- **Framework**: Standard `testing` package + `testify` for assertions/mocks.
- **Mocking**: Generate mocks from interfaces using `mockery` or `gomock` for the Repository and Service layers.
- **Table-Driven Tests**: Use slice-of-structs to test multiple inputs/outputs in a single test function.
