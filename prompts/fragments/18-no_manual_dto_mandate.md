<no_manual_dto_mandate>
You MUST enforce the No-Manual-DTO Mandate on every implementation task where a source-of-truth contract or shared schema exists.

### Core Mandate

AI agents and engineers are STRICTLY FORBIDDEN from hand-authoring duplicate interface models, request/response DTOs, or data classes inside consumer applications when a source-of-truth contract or shared schema already exists — including `packages/shared-schema/`, OpenAPI specs, Prisma schemas, and Protobuf definitions. Consumer applications MUST NOT redefine types that a contract already governs.

### Requirement

When a task touches a type that is governed by an existing contract, the agent MUST either:

1. **(a) Import models directly** from the shared package (`@repo/shared-schema`, `packages/shared-schema`, or the equivalent canonical source), OR
2. **(b) Execute the stack's code-generation toolchain** — `pnpm generate`, `prisma generate`, `protoc`, `./gradlew generateProto`, or the equivalent generator — so the consumer's types are produced from the contract instead of being hand-written.

Hand-written duplicates create silent type drift: the consumer's copy and the contract's canonical definition diverge over time, producing runtime mismatches that compile-time checks in the consumer alone cannot catch.

### Reconciliation with SOLID

This mandate is fully consistent with the SOLID principles and their pragmatic guardrails:

- **DRY / SRP:** A single source of truth prevents duplicated type definitions (DRY) and gives each type exactly one owner (SRP). Importing a shared DTO is not duplication — it is the canonical, single-reason-to-change form.
- **No conflict with YAGNI:** The mandate does not introduce speculative abstractions. It reuses a contract that already exists. If NO source-of-truth contract exists, the agent writes the concrete type directly — do NOT invent a shared-schema package for a single consumer.
- **No conflict with the 3-Implementation Rule:** Extracting a shared package is only required when a contract or cross-service dependency already exists (2+ consumers or a canonical schema). Do not extract interfaces for trivial, single-module logic.
- **Occam's Razor:** The simplest correct action is import-then-use or run-codegen — never hand-copy a governed type.

When a diff introduces a new DTO/interface/model declaration into a consumer path (`apps/**`, `services/**`, `client/**`, `frontend/**`, `mobile/**`, `src/**`) while a governing contract exists, the Type Drift Sentinel fails the verification until the agent imports from the shared package or runs the codegen toolchain.
</no_manual_dto_mandate>