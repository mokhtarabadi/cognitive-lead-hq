---
name: backend-architecture-nodejs-express
description: Architectural rules, 3-layer pattern, and naming conventions for Node.js Express
---

# Node.js + Express — Best Practices

## Project Structure

```
src/
├── config/              # Environment & app configuration
│   ├── env.js           # Zod/Joi schema validation
│   └── cors.js
├── routes/              # Route definitions (thin — no business logic)
│   ├── index.js         # Router aggregator
│   └── user.routes.js
├── controllers/         # Request/response handling
│   └── user.controller.js
├── services/            # Business logic
│   └── user.service.js
├── middleware/           # Express middleware
│   ├── errorHandler.js
│   └── auth.js
├── validators/          # Request validation schemas
│   └── user.validator.js
├── utils/               # Pure helper functions
├── app.js               # Express app setup
└── server.js            # Entry point (listens on port)
```

## Naming Conventions

| Artifact              | Convention                 | Example           |
| --------------------- | -------------------------- | ----------------- |
| Files                 | `kebab-case`               | `user.service.js` |
| Classes               | `PascalCase`               | `UserService`     |
| Functions/Variables   | `camelCase`                | `getUserById`     |
| Routes                | plural nouns, `kebab-case` | `/api/users/:id`  |
| Environment variables | `UPPER_SNAKE_CASE`         | `DATABASE_URL`    |

## Architectural Patterns

### 3-Layer Architecture

```
Route  →  Controller  →  Service
  │           │              │
  │     (parse req,     (business logic,
  │      format res)     orchestration)
  │
  ├── No business logic in routes
  ├── No business logic in controllers
  └── Services are pure — no req/res objects
```

### Centralized Error Handling

Create a custom `AppError` class and a single `errorHandler` middleware. Every thrown error is caught and formatted in one place. Never use try/catch in controllers directly — wrap async route handlers with a utility like `express-async-errors` or an `asyncHandler` wrapper.

### Environment Validation

Validate `process.env` at startup using **Zod** (recommended) or **Joi**. Fail fast if a required variable is missing or has the wrong type. Export a typed `config` object so the rest of the app never touches `process.env` directly.

### Avoiding Fat Controllers

Controllers should only:

1. Parse request parameters (body, params, query).
2. Call a service method.
3. Send the response (or pass to the error handler).

Any logic beyond this belongs in a service, middleware, or utility.

## Testing Strategies

| Layer      | Test Type   | Framework          | File Naming               |
| ---------- | ----------- | ------------------ | ------------------------- |
| Service    | Unit        | Vitest / Jest      | `user.service.test.js`    |
| Controller | Integration | Supertest + Vitest | `user.controller.test.js` |
| Middleware | Unit        | Vitest             | `auth.middleware.test.js` |
| API (E2E)  | E2E         | Supertest          | `user.api.test.js`        |

- Mock external dependencies (DB, HTTP calls) at the service layer.
- Use a test database or in-memory substitute for integration tests.
- Aim for >80% coverage; 100% on shared middleware and validators.
