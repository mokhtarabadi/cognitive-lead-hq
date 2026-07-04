---
name: backend-architecture-go-hexagonal-grpc
description: Hexagonal Architecture (Ports and Adapters), gRPC, Uber Fx, and Redis caching for ultra-low latency Go backends.
---

# Go (Golang) — "Max Power" Agentic Backend Architecture

## AI Context & Token Optimization

1. **Compile-Time Dependency Injection:** Use Uber Fx. This forces explicit dependency declaration, giving the AI instant compiler feedback if a module is wired incorrectly, preventing runtime panics.
2. **gRPC Source of Truth:** Rely on `.proto` files as the absolute contract. The AI uses these to perfectly align client/server interactions.
3. **No Reflection ORMs:** Use `pgx` or `ent`. Reflection-heavy ORMs like GORM cause unpredictable runtime behaviors that confuse AI debugging workflows.

## Modern Project Initiation Guide

When scaffolding a high-performance backend (such as a sub-50ms latency Caller ID system), enforce the following strict rules to maximize AI reasoning and eliminate runtime magic:

1. **Hexagonal Architecture (Ports & Adapters):** Strictly separate the core business logic (Domain) from external concerns (gRPC, PostgreSQL, Redis). The Domain layer must have zero dependencies on external libraries.
2. **gRPC-First:** Use protocol buffers (`.proto`) as the single source of truth for all API contracts. Generate Go interfaces from proto files.
3. **Compile-Time DI:** Use **Uber Fx** or **Google Wire** for dependency injection. This forces the AI to explicitly declare dependencies, resulting in instant compile-time feedback if a dependency is missing.
4. **Caching Layer:** Implement **Redis** via the `go-redis` client for all read-heavy, low-latency lookups (e.g., spam number checks).
5. **Database:** Use **PostgreSQL** with `pgx` for raw, high-performance database interactions, or `ent` (by Facebook) if a strongly-typed ORM is required. Avoid reflection-heavy ORMs like GORM.

## Project Structure

```
project-root/
├── cmd/
│   └── server/
│       └── main.go              # Entry point, initializes Uber Fx application
├── internal/
│   ├── core/
│   │   ├── domain/              # Pure Go structs (e.g., PhoneNumber.go)
│   │   └── ports/               # Interfaces (e.g., CacheRepository, CallService)
│   ├── application/             # Use cases implementing inbound ports
│   │   └── call_service.go
│   ├── adapters/
│   │   ├── inbound/
│   │   │   └── grpc/            # gRPC handlers implementing proto generated interfaces
│   │   └── outbound/
│   │       ├── postgres/        # PostgreSQL repository implementations
│   │       └── redis/           # Redis cache repository implementations
│   └── di/                      # Uber Fx module providers
├── api/
│   └── proto/                   # .proto definition files
├── pkg/                         # Shared libraries (logging, metrics)
├── go.mod
└── Makefile                     # Protoc generation and build commands
```

## Naming Conventions

| Artifact           | Convention           | Example                     |
| ------------------ | -------------------- | --------------------------- |
| Interfaces (Ports) | Nouns ending in `er` | `CallReader`, `CacheWriter` |
| Structs            | `PascalCase`         | `CallScreeningRequest`      |
| Files              | `snake_case.go`      | `call_service.go`           |
| DI Providers       | Prefix with `New`    | `NewPostgresRepository`     |

## Architectural Patterns

### Functional Options Pattern

Use this for configuring complex structures (like external client adapters) cleanly:

```go
type Server struct { ... }
type Option func(*Server)

func WithTimeout(t time.Duration) Option {
    return func(s *Server) { s.timeout = t }
}
```

### Error Handling (Self-Healing for AI)

Never panic. Return errors explicitly. Wrap errors with context using `%w` so the AI agent reading the logs can trace the exact failure path:
`return fmt.Errorf("redis cache miss for number %s: %w", number, err)`

## Testing Strategies

| Layer       | Test Type   | Framework / Tools                                     |
| ----------- | ----------- | ----------------------------------------------------- |
| Application | Unit        | `testing` + `testify/assert` + `mockery` (for ports)  |
| Adapters    | Integration | `testcontainers-go` (spin up real Redis/PG in Docker) |

- Generate mocks for all interfaces in `internal/core/ports` using `mockery`.
- AI must write table-driven tests (`[]struct`) for all core business logic.
