<decision_logging_mandate>
## Purpose

Every non-trivial decision made during task execution MUST be logged in the active task file under `## Manager Decisions`. This creates an auditable trail of architectural, design, and strategic choices — preventing repeated debates and enabling future agents to understand WHY something was built a certain way.

## When to Log

Log a decision whenever any of the following occurs:
- An architectural choice is made (framework, pattern, data store, API design).
- A design trade-off is accepted (e.g., performance vs. readability, consistency vs. availability).
- The Manager explicitly approves a plan that involves trade-offs.
- A constraint or requirement drives a specific implementation approach.
- Lite Mode is applied (log the justification).

## Log Format

Each entry MUST follow this exact format:

```
**[YYYY-MM-DD] [DECISION_ID]:** <one-line decision summary>
- **Rationale:** <why this decision was made>
- **Alternatives considered:** <what else was evaluated>
- **Impact:** <what this affects or constrains>
```

- **DECISION_ID** is a sequential identifier scoped to the task (e.g., D1, D2, D3).
- Decisions are appended in chronological order. Never reorder or delete entries.

## Scope

- **Log:** Architectural patterns, technology choices, API contracts, data model decisions, security trade-offs, performance vs. readability trade-offs, scope changes, and Lite Mode justifications.
- **Do NOT log:** Formatting changes, typo fixes, trivial config tweaks, or any change where the "why" is self-evident from the code itself.
</decision_logging_mandate>