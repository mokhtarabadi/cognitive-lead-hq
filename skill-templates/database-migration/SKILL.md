---
name: database-migration
description: Forbid direct schema alterations and force standard migration tools (Alembic, Prisma, Flyway) for safe, repeatable deployments.
---

# Database-Migration Skill — No Direct DDL

## Purpose

Schema changes ship as reviewed migration files, never as ad-hoc DDL. Direct `CREATE/ALTER/DROP TABLE` against any database — and any ORM "push/sync schema" shortcut against a shared database — is forbidden. Data loss from unreviewed schema edits is the failure this skill exists to prevent.

## Hard Bans

- **No raw DDL outside migration files.** `ALTER TABLE`, `DROP COLUMN`, manual constraint edits run ONLY inside a migration file's up/down (or equivalent) path.
- **No `prisma db push` against shared databases.** `db push` is prototyping-only on a local throwaway DB. Shared, staging, and production databases accept `prisma migrate deploy` from committed migration files only.
- **No `Base.metadata.create_all()` as a deploy strategy.** It is a local-dev convenience, never a migration. Production schema state must equal the migration history end state.

## Per-Stack Tool Map

- **Python / SQLAlchemy → Alembic:** `alembic revision --autogenerate -m "<what>"`, hand-review the generated script (autogenerate misses data migrations), `alembic upgrade head`. Transactional where the DB supports it.
- **Node / TypeScript → Prisma Migrate:** edit `schema.prisma`, `prisma migrate dev --create-only` for review, then `migrate dev` locally and `migrate deploy` in CI/production. Never edit an applied migration — add a new one.
- **Java → Flyway:** versioned `V<nn>__<what>.sql` files, forward-only. A failed migration is repaired with a new version, never by editing history.

## Migration-File Anatomy (Every Migration)

1. **Up path** (apply) + **down path** (rollback) — both required unless the tool proves irreversibility, which is then logged.
2. **Data safety note:** destructive steps (drop column/table, type narrowing) state where the data goes or why loss is accepted. Silent data loss fails review.
3. **Human review before apply:** the Hands pastes the migration diff to the Manager (or the review seat) and proceeds only on approval for shared databases.

## Drift Check

Before applying, verify the database matches migration history end state (Alembic `check`, Prisma shadow-DB drift detection, Flyway `validate`). On drift: HALT, report the diff, never force-apply. Production deploys run `migrate deploy`/`upgrade` from CI, never from a laptop.

## Greenfield Baseline

A brand-new database gets exactly ONE `init` baseline migration capturing the full initial schema. Everything after follows the standard path.
