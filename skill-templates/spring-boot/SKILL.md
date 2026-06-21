---
name: backend-architecture-spring-boot
description: DDD, hexagonal style, and naming conventions for Spring Boot
---

# Spring Boot — Best Practices & AI-Driven Scaffolding

## High-Performance Project Onboarding

Initialize any Spring Boot backend from scratch with these architectural rules:

1. **Domain-Driven Design (DDD):** Use a pure `domain` package containing entities, value objects, and repository ports (interfaces). The domain must not have adapter or framework dependencies.
2. **Hexagonal Ports & Adapters:** Inbound adapters (Controllers, DTOs) and outbound adapters (JPA Repositories, Database engines) are decoupled. Controllers depend on domain services, and domain services interact with adapters via ports.
3. **Constructor Injection:** Always use Lombok `@RequiredArgsConstructor` on classes needing dependencies. Banned: Field `@Autowired`.
4. **MapStruct Compile-Time Mapping:** Generate mappers using MapStruct `@Mapper(componentModel = "spring")`. Banned: reflection-based mapping or manually writing setter chains.
5. **Centralized Error Boundary:** Implement a single `@RestControllerAdvice` class capturing all domain-specific exceptions and mapping them to standardized HTTP responses `{ error, message, status, timestamp }`.
6. **Database Migration:** Always use Flyway or Liquibase to manage relational schemas via SQL files in `resources/db/migration`. Banned: relying on JPA `hibernate.ddl-auto=update` in production.

## Project Structure

```
src/main/java/com/company/project/
├── adapter/                   # Inbound & outbound adapters
│   ├── inbound/
│   │   ├── controller/        # REST controllers
│   │   └── dto/               # Request/response DTOs
│   └── outbound/
│       ├── repository/        # JPA / data repositories
│       └── mapper/            # MapStruct mappers
├── domain/
│   ├── entity/                # Domain entities (@Entity)
│   ├── service/               # Business logic
│   ├── exception/             # Domain exceptions
│   └── port/                  # Repository interfaces (ports)
└── common/
    ├── config/                # @Configuration classes
    ├── exception/             # Global exception handler
    └── util/                  # Utility classes

src/main/resources/
├── application.yml            # Default config
├── application-dev.yml        # Dev profile
└── application-prod.yml       # Production profile
```

## Naming Conventions

| Artifact       | Convention                 | Example                              |
| -------------- | -------------------------- | ------------------------------------ |
| Packages       | `lowercase.reverse.domain` | `com.company.project.domain.service` |
| Classes        | `PascalCase`               | `UserServiceImpl`                    |
| Methods        | `camelCase`                | `findByEmail`                        |
| REST endpoints | plural nouns, `kebab-case` | `/api/users/{id}`                    |
| Tables         | `snake_case` plural        | `user_roles`                         |
| Columns        | `snake_case`               | `created_at`                         |

## Architectural Patterns

### Domain-Driven Design (DDD)

Structure the application so that the domain is the innermost, most stable layer.

- **Domain** — Entities, value objects, domain services, repository ports. No framework annotations here (except `@Entity` where unavoidable).
- **Adapter** — Controllers, DTOs, JPA repositories, mappers. These depend on the domain, not the other way around.
- **Ports** — Interfaces in the domain layer that adapters implement. For example, a `UserRepository` interface in `domain/port/` is implemented by `JpaUserRepository` in `adapter/outbound/repository/`.

### MapStruct for Entity ↔ DTO Mapping

- Generate mapper implementations at compile time — no runtime reflection overhead.
- Keep mapping logic in dedicated `@Mapper` interfaces; never hand-write `set` calls.
- Use `@Mapping` annotations for field name differences.

### Constructor Injection Over Field Injection

Always inject dependencies via the constructor (Lombok `@RequiredArgsConstructor` or explicit constructor). Never use `@Autowired` on fields — it makes testing and immutability harder.

### Global Exception Handling

Create a single `@RestControllerAdvice` class that catches all exceptions.

- Map domain exceptions (e.g., `UserNotFoundException`) to specific HTTP status codes.
- Return a consistent error response body (`{ error, message, status, timestamp }`).
- Log the stack trace at `ERROR` level for 5xx; `WARN` for 4xx.

## Testing Strategies

| Layer            | Test Type   | Framework         | File Naming                |
| ---------------- | ----------- | ----------------- | -------------------------- |
| Domain service   | Unit        | JUnit 5 + Mockito | `UserServiceTest.java`     |
| Controller       | Slice test  | `@WebMvcTest`     | `UserControllerTest.java`  |
| Repository       | Slice test  | `@DataJpaTest`    | `UserRepositoryTest.java`  |
| Full integration | Integration | `@SpringBootTest` | `UserIntegrationTest.java` |

- Use `@WebMvcTest` and `@DataJpaTest` for focused tests — they bootstrap only the relevant context.
- Prefer `Mockito` for mocking; never use `PowerMock`.
- Use `Testcontainers` for database-dependent integration tests.
