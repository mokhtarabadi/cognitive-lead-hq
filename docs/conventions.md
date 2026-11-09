# Conventions

This document defines syntax rules, naming conventions, file boundaries, and automation patterns for the Cognitive Lead AI multi-agent system HQ.

## GitHub CLI Automation

All `gh` commands that send body content MUST use `--body-file` with a temp Markdown file, never inline `--body`.

### Rationale

Inline `--body "..."` in `gh issue create` is fragile:

| Problem             | Example                                               |
| ------------------- | ----------------------------------------------------- |
| Shell escaping      | Backticks, `$`, `"` inside the body break the command |
| Truncation          | Long bodies get silently cut off                      |
| Markdown corruption | Newlines, `#`, `---` can break shell parsing          |
| No preview          | You can't verify what will actually be sent           |

Using a body file guarantees precise, verbatim delivery of the full Markdown content. Keep it inside the project workspace.

### Standard Pattern

1. Create a unique temporary Markdown body file inside the current project workspace using a native file-write tool.
2. Pass that file's concrete workspace-relative path to `gh issue create --body-file`; never pass the body through inline `--body`.
3. After recording the command result, delete only that exact temporary file using a native file-management tool.

### Rules

- Keep the body file inside the current project workspace.
- Never create or modify it with shell redirection, Python, or another script.
- Always use `--body-file`, never inline `--body`.
- Remove only the known temporary body file after the command has been handled.

### Canonical Reference

The [`github` skill](../skill-templates/github/SKILL.md) is the canonical reference for all GitHub CLI workflows — pull request triage, issue management, CI/CD run analysis, and API queries. Load it via the `skill` tool whenever a task involves GitHub operations.

## Universal DateTime Standard

All projects in this ecosystem MUST follow these datetime rules:

1. **UTC at Rest** — All databases and caches store datetimes in UTC with `TIMESTAMP WITH TIME ZONE`. Banned: naive or local-time storage.
2. **ISO-8601 with Offset / Epoch ms at API Boundaries** — APIs transmit datetimes as Unix Epoch milliseconds (int64) or ISO-8601 with offset (e.g., `2026-07-23T14:30:00+00:00`). Banned: timezone-naive strings.
3. **Clock Injection** — All current-time access must go through an injectable `Clock` abstraction. Banned: direct `new Date()`, `datetime.now()`, `time.Now()` in business logic.
4. **Dual-Representation for Future Events** — Calendar events expose both `event_start_local` (with timezone) and `event_start_epoch_ms` (absolute).
5. **`TZ=UTC` Infrastructure** — All environments run with `TZ=UTC`. Timezone display is a client-layer responsibility only.

## SOLID Programming Guidelines

Enforce these SOLID principles and pragmatic guardrails in every implementation:

1. **SRP** — One reason to change per module. Split merged concerns.
2. **OCP** — Open for extension, closed for modification. Use composition over inheritance.
3. **LSP** — Subtypes must be substitutable. Ban `NotImplementedError` overrides.
4. **ISP** — Small role-specific interfaces. Ban monolithic god-interfaces.
5. **DIP** — Depend on abstractions, not concretions. Core layer must not import adapters.

**Pragmatic Guardrails:** No abstraction for <3 trivial operations. Only extract interfaces with 2+ implementations. Apply YAGNI strictly. Prefer simpler designs unless a measurable requirement forces complexity.

## No-Manual-DTO & Type Drift Standard

All projects in this ecosystem MUST treat source-of-truth contracts and shared schemas (`packages/shared-schema/`, OpenAPI specs, Prisma schemas, Protobuf definitions) as the **only** place a governed type may be defined:

1. **No hand-authored duplicates** — Consumer applications (`apps/**`, `services/**`, `client/**`, `frontend/**`, `mobile/**`, `src/**`) MUST NOT hand-author duplicate interface models, request/response DTOs, or data classes for types already governed by a contract.
2. **Import or generate** — When a governed type is needed, either import it directly from the shared package (`@repo/shared-schema`, `packages/shared-schema`) or execute the stack's code-generation toolchain (`pnpm generate`, `prisma generate`, `protoc`, `./gradlew generateProto`).
3. **SOLID reconciliation** — Single-source-of-truth prevents type drift (DRY/SRP) and does not conflict with YAGNI or the 3-Implementation Rule: extract or generate only when a contract or cross-service dependency already exists.
4. **Deterministic enforcement (historical — loop-engine retired):** the retired `loop-engine/sentinel.py` `TypeDriftSentinel` used to scan task diffs during toolchain verification (pre-QA). With the loop-engine daemon retired, enforcement is manual review until a replacement lands. Bypass with an explicit `drift-ignore` comment only when a justified exception exists.

The single source of truth for the full mandate is the `No-Manual-DTO Mandate` section in `agents/cognitive-executor.md` — this section is a summary only.

## Universal Financial Ledger Standard

All financial, transactional, and countable data operations MUST enforce these mandates:

1. **Snapshot-on-Write for Mutable Totals:** Whenever a financial amount, inventory count, or balance is mutated, persist a read-only snapshot of the preceding state in the same transaction (sidecar table, audit log, or WAL). Banned: mutating without preserving the prior value.
2. **Mandatory `$ifNull` Precedence:** All aggregation queries on monetary fields MUST use explicit null-handling (`COALESCE`, `ISNULL`, `$ifNull`). Banned: passing nullable columns into mathematical operators.
3. **Observability Alerting on Discrepancies:** If a computed total diverges from its line-item sum by more than 0.01, emit a high-severity alert and prevent finalization.
4. **Deep Config Merging for Financial Settings:** Financial configuration updates MUST deeply merge nested properties. Banned: shallow object spread on financial config objects.

## Defensive Shell Protocol (DSP)

When writing or reviewing bash scripts, cron jobs, or container orchestration commands:

1. **Mandatory Strict Mode:** All scripts MUST start with `set -euo pipefail`.
2. **Banned Error Masking:** `2>/dev/null` is STRICTLY FORBIDDEN on data-generation, backup, archive, or database commands.
3. **No Post-Redirect Status Checks:** Never use `command > file; if [ $? -eq 0 ]` — the shell creates the file before running the command, masking failures.
4. **Sidecar Isolation for Hostless Backups:** Never rely on host file staging for Docker volume backups. Always use ephemeral containers (`docker run --rm -v volume:/data:ro alpine tar...`) with read-only mounts.

## Risk Tiers (Autopilot-Ready Contract)

Every task runs at one tier. The tier sets how many human pauses apply.

- **T0 trivial:** no high-risk surface (no auth/authn/authz, secrets, security-surface, financial ledger or calculation, data-privacy or CLP, PII deletion, migrations, deploys, publishes, pushes, or irreversible deletes), gates green (relevant tests green plus lint clean plus risk greps clean), reversible via git. Minimal scope applies only to implementation. The full workflow and all approval gates remain mandatory, including plan approval, QA, Code Review, and PO closure approval.
- **T1 standard:** multi-file changes or new behavior. Full supervised autopilot applies with a plan-approval pause plus Relay questions.
- **T2 destructive or irreversible:** migrations, deletes, publishes, pushes, or secret handling. Each action needs explicit Manager approval. Autopilot MUST halt and never self-approve.

Max three tries per loop (plan, QA, review), then escalate to the Manager with evidence.

## Goal-Oriented Tasks & Parallel Agent Execution Standards

### Goal-Oriented Task Treatment

When the Software Architect or Senior Programmer issues a multi-step or large task (more than 2 implementation phases), they MUST:

1. **Load all relevant skills** from `<agent_skills_registry>` before generating the task.
2. **Structure the work as a Goal unit** with explicit verification gates (tests, lints, compilation checks) for each phase.
3. **List exactly WHICH skills the Hands must load**, and explain HOW and WHY to use them in the task template.

Trivial single-file changes do not require Goal treatment. The Goal treatment is mandatory for any task touching 2+ files, any new feature, or any architectural change.

### Parallel Agent Execution Mandate

The Hands MUST actively utilize parallel subagent execution (up to 4 concurrent agents) whenever a task involves 2 or more independent workstreams:

- **File scans** across different directories (e.g., reading `prompts/fragments/` and `agents/` simultaneously)
- **Signature extractions** from multiple unrelated modules
- **Decoupled module changes** where one module's edit does not depend on another's

Serial execution of independent workstreams is a performance violation. The parallel mandate applies to both the Orchestrator's planning phase (parallel discovery tasks) and the Hands' execution phase (parallel subagent spawns).

## Input Validation & Clarification Halt

### Input Validation Pipeline

All Manager input — English, non-English, or mixed — MUST pass through the Input Validation Pipeline before any execution:

1. **Language detection** (English, non-English, mixed)
2. **Typo/hallucination detection** (misspellings, nonsensical words)
3. **Clarity check** (core intent identifiable with confidence)
4. **Completeness check** (enough context to form a requirement)

### Clarification Halt

If any validation step FAILS — particularly the clarity check — the Orchestrator and Hands MUST:

1. **HALT immediately.** Do NOT guess, assume, or fabricate intent from ambiguous input.
2. **Output a clarification request** in simple English, no matter which language the input used.
3. **Ask targeted questions** to confirm the exact intent before proceeding.
4. **Only resume** after the Manager provides an unambiguous response.

Guessing intent from ambiguous, fragmented, or unclear input is strictly forbidden at every level of the system (Orchestrator, personas, and Hands).

### Non-English Translation

All non-English input MUST first pass raw-input validation and typo correction. Translate it to technical English before intent expansion, restructuring, execution planning, task generation, or any prompt-refactoring operation beyond Step 0. Step 0 raw-input validation and typo correction are the only prompt-refactor operations permitted before translation. No execution may occur before the translation step is complete.

## MCP Environment Loading & Blank-Means-Unset Convention

All MCP servers load `.env` files explicitly at import via `mcp_common.env.load_env_files` (stdlib parser, no dependency). Search order: `<server-dir>/.env` → `<server-dir>/../.env` (repo root, or the global `~/.config/opencode/.env` backup) → `<cwd>/.env`.

**Blank-means-unset (binding convention):** an empty value — whether from a bare `KEY=` line or an empty-string process variable (e.g. OpenCode `{env:…}` blocks inject `""` when the parent env lacks the var) — counts as UNSET. File values fill gaps; real non-empty process values always win. This is deliberate and load-bearing: `DECISION_MODEL=` (blank) means "fall back to `PERSONA_MODEL`". Do NOT "fix" this into standard-dotenv empty-overrides semantics without a manager-approved task — doing so silently disables the model fallback chain and reintroduces blank-auth 401s.

Parser rules (locked by tests): `#` comments and blank/malformed lines skipped; `export KEY=` prefix stripped; quotes stripped only when wrapping; inline `#` stays literal; `KEY = value` whitespace trimmed; CRLF tolerated; BOM stripped (`utf-8-sig`).

## Task-Number Reference Discipline

Task numbers are provenance for humans, not reasoning material for the model. A bare task number in visible prompt prose invites hallucination: the model treats it as load-bearing context it cannot resolve.

**Allowed homes (only):** code comments (`#`, `//`), `CHANGELOG.md` entries, task files in `tasks/`, `docs/history/` archives, and HTML-comment markers (`<!-- -->`, including frozen provenance blocks which stay verbatim).

**Forbidden homes:** visible prose in prompt fragments, agent instruction files, skill instructions, registry lines, section headings, and any Markdown the Brain or Hands reads as operating instructions.

**Authoring rule:** when writing or editing prompt-facing Markdown, strip task-number parentheticals. Record provenance in the task file and CHANGELOG instead — never in the prompt text itself.

## Edit Tool Discipline

File edits use ONLY native file-editing tools (edit for replacements, file-write tools for new files). Using python, shell, heredoc, `sed -i`, or any script to create or modify files is strictly forbidden — scripted edits fail silently (replace-all on non-unique anchors, quoting and encoding mangling) while native tools fail loudly on a non-unique anchor. Shell stays read-only for file content (e.g. grep, cat, diff, ls, git status). Verify every edit with grep/diff.

## Living Folder Docs Standard

All vertical slices and component directories across projects in this ecosystem MUST maintain colocated documentation and decision records:

1. **Folder Colocation** — Every domain component or vertical slice directory (e.g. `src/features/todos/`, `services/auth/`, `mcp-context-server/`) must contain:
   - `README.md` — Explains the component's core duties, directory layout, owned files, and critical invariants/risks.
   - `DECISIONS.md` — Chronological log of dated Architectural Decision Records (ADRs). Each entry must document Context, Decision, Consequences, and Rollback strategy.
2. **One-Line Code Pointer Standard** — Primary source files within the component directory must include a top-line comment pointing directly to the sibling docs:
   - JavaScript/TypeScript: `// Sibling Docs: <relative-path>/README.md | Decisions: <relative-path>/DECISIONS.md`
   - Python/Shell: `# Sibling Docs: <relative-path>/README.md | Decisions: <relative-path>/DECISIONS.md`
3. **Synchronization Invariant** — Whenever source code inside a component directory is added, refactored, or altered in behavior or data contract, the sibling `README.md` and `DECISIONS.md` MUST be inspected and updated within the same task. Silent overrides of existing architectural decisions are strictly forbidden.
