---
name: backend-architecture-fastapi
description: Pydantic schemas, dependency injection, and async routing for Python FastAPI
---

# FastAPI (Python) — Best Practices

## Project Structure

```
app/
├── api/                 # API routers and endpoints
│   ├── dependencies.py  # Shared dependencies (e.g., get_db, get_current_user)
│   └── v1/
│       └── users.py     # User endpoints
├── core/                # Core configurations, security, and settings
│   ├── config.py        # Pydantic BaseSettings
│   └── security.py      # JWT, hashing
├── models/              # SQLAlchemy / Database models
│   └── user.py
├── schemas/             # Pydantic models (DTOs)
│   └── user.py
├── services/            # Business logic and CRUD operations
│   └── user.py
├── tests/               # Pytest test suite
├── main.py              # FastAPI application instance
└── requirements.txt     # Dependencies
```

## Naming Conventions

- **Files/Directories**: `snake_case` (e.g., `user_service.py`)
- **Classes**: `PascalCase` (e.g., `UserCreate`)
- **Functions/Variables**: `snake_case` (e.g., `get_user_by_id`)
- **Constants/Settings**: `UPPER_SNAKE_CASE` (e.g., `SECRET_KEY`)

## Architectural Patterns

- **Dependency Injection**: Use FastAPI's `Depends()` heavily for database sessions and auth. Never instantiate global DB sessions in routers.
- **Separation of Concerns**: Routers (`api/`) only handle HTTP requests and Pydantic validation. All business logic lives in `services/`.
- **Pydantic V2**: Use Pydantic schemas for request/response validation. Keep ORM models (`models/`) strictly separate from API schemas (`schemas/`).
- **Async First**: Use `async def` for endpoints and asynchronous database drivers (e.g., `asyncpg` for SQLAlchemy) to maximize throughput.

## Testing Strategies

- **Framework**: `pytest` and `httpx` (for `AsyncClient`).
- **Structure**: Create a `conftest.py` with fixtures for an overridden `get_db` dependency (using SQLite in-memory or a test database).
- **Coverage**: Test all API endpoints via HTTP calls. Test complex service logic via pure unit tests.
