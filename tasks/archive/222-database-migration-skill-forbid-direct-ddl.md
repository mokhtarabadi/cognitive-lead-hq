# Task 222: Database-migration skill (forbid direct schema alterations)

**File:** `tasks/archive/222-database-migration-skill-forbid-direct-ddl.md`
**Source:** manager
**Type:** feature
**Status:** superseded
**Superseded-By:** 224-readme-roadmap-trio-meta
**Superseded-At:** 2026-09-13

## Source Context

## Goal

Create a `database-migration` skill that strictly forbids direct schema alterations and forces standard migration tools (Prisma, Alembic, Flyway).

## Manager's Notes

README roadmap item 4, verbatim: "Database Migration Management: Create a `database-migration` skill to strictly forbid direct schema alterations, forcing the use of standard migration tools (Prisma, Alembic, Flyway) for safe, repeatable deployments." Project goal reminder (Manager, verbatim core): the project's main goal is the strictest linters/tools that stop AI hallucination — every skill must serve it. Research: Alembic (autogenerate + transactional + offline SQL scripts, alembic.sqlalchemy.org); Prisma Migrate (shadow-DB drift detection, `migrate deploy` in CI only, prisma.io/docs/orm/prisma-migrate); Flyway (versioned SQL migrations). No prior manager ruling found in local decision store. Skill must: ban raw DDL/CREATE/ALTER outside migration files, ban `prisma db push` against prod-like DBs, per-stack tool map (Alembic→Python/SQLAlchemy, Prisma→Node/TS, Flyway→Java), migration-file anatomy (up/down, review before apply), drift-detection step. Deliverable: `skill-templates/database-migration/SKILL.md` + registry entry (registry-consistency test enforces both).

## Local TODOs

- [ ] Initial codebase exploration
- [ ] Write database-migration SKILL.md + registry entry
- [ ] Extend registry consistency tests
- [ ] Verify functionality

## Acceptance Criteria

- [ ] `skill-templates/database-migration/SKILL.md` exists with DDL ban, per-stack tool map, drift check
- [ ] Registry lists the skill and consistency tests pass
- [ ] Full suite passes exit 0

## Verification Evidence

- **Test command:** full pytest suite + docs-sync
- **Expected result:** all pass, exit 0
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** greenfield projects slowed by migration ceremony
- **Rollback plan:** skill allows single `init` baseline migration; revert template + registry line

---

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
