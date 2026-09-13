# Task 223: Hexagonal architecture expansion (Python FastAPI + TypeScript Node)

**File:** `tasks/archive/223-hexagonal-expansion-python-node.md`
**Source:** manager
**Type:** feature
**Status:** superseded
**Superseded-By:** 224-readme-roadmap-trio-meta
**Superseded-At:** 2026-09-13

## Source Context

## Goal

Port the strict Ports & Adapters blueprint from Go to Python (FastAPI) and TypeScript (Node.js) templates.

## Manager's Notes

README roadmap item 5, verbatim: "Hexagonal Architecture Expansion: Port the strict Ports & Adapters blueprint from Go to our Python (FastAPI) and TypeScript (Node.js) templates to unify "Max Power" backend design patterns across all supported stacks." Project goal reminder (Manager, verbatim core): the project's main goal is the strictest linters/tools that stop AI hallucination — every skill must serve it. Source blueprint: `skill-templates/go-hexagonal-grpc/SKILL.md` (core/ports/application/adapters, `er`-suffixed port interfaces, compile-time DI, UTC/clock rules, table-driven tests + testcontainers). Research consensus: core with zero framework imports (pure dataclasses/Pydantic-free domain), `core/ports/inbound|outbound` + `adapters/inbound|outbound` split, composition-root DI container (fraps93/hexagonal-fastapi; fastapi-hexagon module layout domain/application/infrastructure). No prior manager ruling found in local decision store. Scope: add Hexagonal section to `skill-templates/python-fastapi/SKILL.md` (Protocol-based ports, dependency-injector container, SQLAlchemy outbound adapter, httpx-tested inbound routes) + create `skill-templates/node-hexagonal-api/SKILL.md` (interfaces-as-ports, tsyringe/nest-like manual container, Prisma/TypeORM outbound adapter, vitest + testcontainers) + registry entry + `stacks/node-ts.yaml` skills append. stacks/ is LIVE (loop-engine profiles) — NOT leftover, do NOT delete.

## Local TODOs

- [ ] Initial codebase exploration
- [ ] Hexagonal section in python-fastapi template + new node-hexagonal-api template + registry + stacks yaml
- [ ] Extend registry consistency tests
- [ ] Verify functionality

## Acceptance Criteria

- [ ] python-fastapi template carries a Hexagonal section with zero-framework-import rule
- [ ] node-hexagonal-api template exists with ports/adapters/DI/testing rules
- [ ] Registry + stacks yaml updated and consistency tests pass
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

- **Risk:** new Node template duplicates nextjs/react-vite coverage
- **Rollback plan:** node-hexagonal-api is backend-only (no UI); revert template + registry/yaml lines

---

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
