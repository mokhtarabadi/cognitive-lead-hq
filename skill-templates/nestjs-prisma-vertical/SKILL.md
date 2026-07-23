---
name: nestjs-prisma-vertical
description: NestJS, Prisma ORM, Vertical Slice Architecture, and Strict TypeScript for zero-hallucination backend development.
---

# NestJS + Prisma (Vertical Slice) — "Max Power" AI Architecture

## AI Context & Token Optimization (Zero-Hallucination Rules)

1. **Opinionated Framework:** NestJS is mandatory. Unstructured frameworks like Express are BANNED. You must use decorators (`@Controller`, `@Injectable`) and modules.
2. **Vertical Slice Architecture:** Do NOT use traditional layered architectures (global `controllers/`, `services/`). Group all files by feature (e.g., `src/features/auth/`) to localize AI context and save memory tokens.
3. **Strict TypeScript & Compile-Time Safety:** The `any` type is strictly forbidden.
4. **Prisma ORM as Source of Truth:** Raw SQL queries are BANNED. You must modify `schema.prisma`, and rely on the compiler to catch invalid database calls.
5. **Validation:** All incoming requests MUST be validated using DTOs with `class-validator` and `class-transformer`.

## Project Structure

```text
src/
├── main.ts                     # Application entry point
├── app.module.ts               # Root module
├── core/                       # Core infrastructure (written once)
│   ├── prisma/                 # Prisma service and module
│   ├── guards/                 # Authentication/Authorization guards
│   ├── filters/                # Global exception filters
│   └── interceptors/             # Global interceptors
└── features/                   # ⬅️ Vertical Slices (Feature Modules)
    ├── auth/
    │   ├── auth.module.ts
    │   ├── auth.controller.ts
    │   ├── auth.service.ts
    │   └── dtos/
    │       ├── login.dto.ts
    │       └── register.dto.ts
    └── users/
        ├── users.module.ts
        ├── users.controller.ts
        └── users.service.ts
```

## Naming Conventions

| Artifact          | Convention              | Example              |
| ----------------- | ----------------------- | -------------------- |
| Files             | `kebab-case` with type  | `auth.controller.ts` |
| Classes           | `PascalCase`            | `AuthController`     |
| Methods/Variables | `camelCase`             | `registerUser`       |
| Prisma Models     | `PascalCase` (Singular) | `model User`         |

## Architectural Patterns

**Dependency Injection:**
Use NestJS constructor injection exclusively.

**Prisma Workflow:**

1. Modify `prisma/schema.prisma`.
2. Never write migrations manually. Use CLI commands to generate them.
3. Inject `PrismaService` into feature services to interact with the DB. The LSP will guide you with exact types.

**Global Error Handling:**
Do not use inline `try/catch` for standard HTTP errors. Throw NestJS exceptions (`ConflictException`, `NotFoundException`) and let the global filter handle the JSON formatting.

## Universal DateTime Governance

- **Prisma Schema:** Use `DateTime` fields with `@db.Timestamptz()` in the Prisma schema to enforce UTC storage. Never use `@db.Date` or `@db.Timestamp` without timezone.
- **API DTOs (class-validator):** Use `@IsString()` for ISO-8601 strings or `@IsInt()` for epoch ms. Banned: `Date` type in DTOs (serialization is unreliable cross-timezone).
- **Clock Injection:** Create a `ClockProvider` service (`@Injectable`) wrapping `new Date()` — inject it into feature services. Never call `new Date()` or `Date.now()` directly in business logic.
- **API Format:** All API responses MUST transmit datetimes as ISO-8601 UTC strings (`2026-07-23T14:30:00.000Z`) or epoch ms (number). Never transmit naive date strings.

## Testing Strategies

| Layer            | Test Type | Framework                 | File Naming               |
| ---------------- | --------- | ------------------------- | ------------------------- |
| Feature Service  | Unit      | Jest + Mock Prisma        | `auth.service.spec.ts`    |
| Controller       | Unit      | Jest                      | `auth.controller.spec.ts` |
| Feature Endpoint | E2E       | Jest + Supertest + TestDB | `auth.e2e-spec.ts`        |
