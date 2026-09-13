---
name: node-hexagonal-api
description: Hexagonal Architecture (Ports and Adapters) for TypeScript Node.js backends — strict layer boundaries, interface ports, and swappable adapters.
---

# Node.js (TypeScript) — "Max Power" Hexagonal Backend

## AI Context & Token Optimization

1. **Interfaces as Ports:** TypeScript `interface` is the port. The AI reads one interface file and knows the entire contract — no implementation archaeology.
2. **Strict Mode Always:** `strict: true` in `tsconfig.json`. `any` is banned in core and application layers; `unknown` + narrowing at adapter edges.
3. **Constructor Injection:** Explicit constructor parameters over service locators. Missing dependencies fail at composition time, not in production.

## Project Structure

```
project-root/
├── src/
│   ├── core/
│   │   ├── domain/              # Pure entities (no imports from outside core)
│   │   └── ports/
│   │       ├── inbound/         # Primary ports (e.g., UserService)
│   │       └── outbound/        # Secondary ports (e.g., UserRepository, Clock)
│   ├── application/             # Use cases implementing inbound ports
│   │   └── create-user.ts
│   ├── adapters/
│   │   ├── inbound/
│   │   │   └── http/            # Route handlers (Fastify/Express/Hono)
│   │   └── outbound/
│   │       ├── postgres/        # Prisma/TypeORM repository implementations
│   │       └── cache/           # Redis adapter
│   ├── di/
│   │   └── container.ts         # Composition root (tsyringe or manual wiring)
│   └── main.ts                  # Entry point, builds container, starts server
├── prisma/
│   └── schema.prisma            # Schema source of truth (see database-migration)
├── package.json
└── tsconfig.json                # strict: true
```

## Naming Conventions

| Artifact           | Convention              | Example                  |
| ------------------ | ----------------------- | ------------------------ |
| Port interfaces    | Nouns (`*Repository`) or role `er` nouns | `UserRepository`, `UserCreator` |
| Use cases          | Verb + entity           | `CreateUser`, `ArchiveOrder` |
| Files              | `kebab-case.ts`         | `create-user.ts`         |
| DTOs               | `*Dto` with zod/class-validator | `CreateUserDto`   |

## Architectural Patterns

**Zero-Framework Core:** `src/core` imports NOTHING from frameworks (no http lib, no ORM, no validation lib in entities). Violation fails review.
**Dependency Direction:** adapters depend on core ports; core never imports adapters. Import-lint rule or review checklist enforces it.
**DTOs at the Edge:** validate at inbound adapters (zod schemas), map to domain entities immediately. Never leak ORM models through ports.
**Clock Abstraction:** `Clock` port (`now(): Date`) in `core/ports/outbound`. Banned: `new Date()` in domain/application code — inject the clock.

## Universal DateTime Governance

- **UTC at rest:** store ISO-8601 UTC strings or epoch ms. Banned: locale-formatted date strings in storage/cache.
- **Transmit:** ISO-8601 with offset or epoch ms, matching the API contract.

## Testing Strategies

| Layer       | Test Type   | Framework / Tools              |
| ----------- | ----------- | ------------------------------ |
| Application | Unit        | `vitest` + in-memory port fakes |
| Adapters    | Integration | `vitest` + `testcontainers` (real PG/Redis) |

- Write table-driven (`it.each`) tests for all use cases against faked outbound ports.
- Inbound HTTP routes tested via supertest-style injection with the real container and faked repositories.

## Currency Baseline

- **Runtime:** Node 22 LTS. **Package manager:** `pnpm` (fallback `npm`). **Validation:** `zod`. **ORM:** `prisma` (migrations via `prisma migrate`, never `db push` on shared DBs).
