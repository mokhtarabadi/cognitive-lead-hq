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

Using `--body-file /tmp/gh-issue-body.md` guarantees precise, verbatim delivery of the full Markdown content.

### Standard Pattern

```bash
cat > /tmp/gh-issue-body.md << 'EOF'
## Title
Full Markdown content here — safe from shell escaping.
EOF

gh issue create \
  --title "Issue Title" \
  --body-file /tmp/gh-issue-body.md \
  --label "some-label"

rm -f /tmp/gh-issue-body.md
```

### Rules

- Use single-quoted `'EOF'` delimiter to prevent shell variable expansion.
- Always include `rm -f /tmp/gh-issue-body.md` cleanup after the `gh` command.
- This applies to all files: SKILL.md templates, task files, and scripts.

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

## Decision Logging Standard (`<manager_decisions>`)

Every non-trivial decision made during task execution MUST be logged in the active task file under `## Manager Decisions`. This creates an auditable trail of architectural, design, and strategic choices.

### When to Log

- Architectural choices (framework, pattern, data store, API design).
- Design trade-offs (performance vs. readability, consistency vs. availability).
- Manager explicit plan approvals involving trade-offs.
- Constraint-driven implementation approaches.
- Lite Mode justifications.

### Log Format

```
**[YYYY-MM-DD] [DECISION_ID]:** <one-line decision summary>
- **Rationale:** <why this decision was made>
- **Alternatives considered:** <what else was evaluated>
- **Impact:** <what this affects or constrains>
```

- **DECISION_ID** is sequential per-task (D1, D2, D3).
- Decisions are appended in chronological order. Never reorder or delete.

### Scope

- **Log:** Architectural patterns, technology choices, API contracts, data model decisions, security trade-offs, performance trade-offs, scope changes, Lite Mode justifications.
- **Do NOT log:** Formatting changes, typo fixes, trivial config tweaks, or self-evident code changes.

## Lite Mode Protocol

Process is scaled to risk. Not every task requires the full 9-step production line.

### Eligibility (All Three Must Be True)

1. **Single-file impact:** Change touches one file (or config-only, zero cross-module dependencies).
2. **No security/financial impact:** No authentication, authorization, data privacy, financial calculation, or payment implications.
3. **Explicit or obvious simplicity:** Manager says "just do it" / "quick fix" / "no plan needed", OR root cause and fix are both obvious and verifiable within one file.

### Workflow

Bypasses Steps 1–4 of `<execution_workflow>` (Discovery, Brainstorming, Blueprint, Approval Gate). Goes directly to Implementation. Standard QA + Code Review still applies but can be expedited for trivial changes.

### Escalation

If implementation reveals the change is NOT trivial, the Hands MUST HALT and output: "Escalating from Lite Mode to Full Mode: [reason]." The full workflow restarts at Step 1.
