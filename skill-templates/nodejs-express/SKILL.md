---
name: backend-architecture-nodejs-express
description: AI-Optimized TypeScript Express architecture with Zod validation and 3-layer pattern.
---

# Node.js + Express (TypeScript) — AI-Native Scaffolding

## AI Context & Token Optimization

1. **Strict TypeScript Only:** Pure JavaScript is banned. You MUST use strict TypeScript interfaces for all database models, API responses, and request bodies. This prevents AI hallucinations and ensures safe cross-file refactoring.
2. **Zod for Everything:** Use Zod for environment validation, request body validation, and type inference.
3. **Modular Files:** Keep files under 200 lines. The AI context window degrades when reading monolithic controllers.

## Project Structure

```
src/
├── config/              # Environment & app configuration (env.ts)
├── routes/              # Route definitions (thin — no business logic)
├── controllers/         # Request/response handling (Typed req/res)
├── services/            # Business logic (Pure functions, no Express imports)
├── middleware/          # Express middleware (errorHandler.ts, auth.ts)
├── types/               # Shared TypeScript interfaces & Zod schemas
└── server.ts            # Entry point
```

## Naming Conventions

| Artifact            | Convention                 | Example           |
| ------------------- | -------------------------- | ----------------- |
| Files               | `kebab-case`               | `user.service.ts` |
| Classes / Types     | `PascalCase`               | `UserResponse`    |
| Functions/Variables | `camelCase`                | `getUserById`     |
| Routes              | plural nouns, `kebab-case` | `/api/users/:id`  |

## Architectural Patterns

**3-Layer Architecture:**
`Route -> Controller -> Service`
Routes bind paths to Controllers. Controllers parse typed requests using Zod and pass data to Services. Services execute logic and return typed objects. No business logic in routes or controllers.

**Global Error Handling:**
Wrap all controllers in `express-async-errors`. Throw custom `AppError` classes in services; let the global error middleware format the JSON response. Never write inline `try/catch` in controllers.

**Environment Validation:**
Validate `process.env` at startup using **Zod**. Fail fast if a required variable is missing. Export a typed `config` object so the rest of the app never touches `process.env` directly.

## Testing Strategies

| Layer      | Test Type   | Framework          | File Naming               |
| ---------- | ----------- | ------------------ | ------------------------- |
| Service    | Unit        | Vitest             | `user.service.test.ts`    |
| Controller | Integration | Supertest + Vitest | `user.controller.test.ts` |
