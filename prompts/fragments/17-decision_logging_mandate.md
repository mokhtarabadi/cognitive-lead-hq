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

## Decision Detection Responsibility

Logging a decision is not solely the Hands' job. Detection must happen at the layer closest to the Manager's actual words:

- **Orchestrator (chat-based conversations):** When finalizing a task for handoff to the Hands/OpenCode, the Orchestrator MUST review the conversation that produced this task and explicitly identify any Manager decisions or goals — approvals, rejections, scope changes, chosen trade-offs. These MUST be pre-seeded into the generated task file's `## Manager Decisions` section, tagged `[ORCHESTRATOR-DETECTED]`, before the task is handed to the Hands.
- **Cognitive Executor (direct Manager ↔ Hands/OpenCode conversations):** When the Manager talks directly to the Hands/OpenCode agent without going through the Orchestrator chat, the Cognitive Executor MUST perform the same detection role during its own conversation with the Manager, logging entries tagged `[EXECUTOR-DETECTED]`.
- **Hands (execution-time):** Continues to log decisions made or discovered strictly during implementation (e.g., an unforeseen technical constraint forcing a trade-off), tagged `[EXECUTION-DETECTED]`.

This produces one unified, chronologically ordered `## Manager Decisions` log per task. Each entry's `[SOURCE]` tag lets a weekly/monthly coach review distinguish stated Manager intent (Orchestrator/Executor) from technical necessity (Hands).

## Log Format

Each entry MUST follow this exact format:

```
**[YYYY-MM-DD] [DECISION_ID] [SOURCE]:** <one-line decision summary>
- **Rationale:** <why this decision was made>
- **Alternatives considered:** <what else was evaluated>
- **Impact:** <what this affects or constrains>
```

- **DECISION_ID** is a sequential identifier scoped to the task (e.g., D1, D2, D3).
- **SOURCE** MUST be one of: ORCHESTRATOR-DETECTED, EXECUTOR-DETECTED, EXECUTION-DETECTED.
- Decisions are appended in chronological order. Never reorder or delete entries.

## Scope

- **Log:** Architectural patterns, technology choices, API contracts, data model decisions, security trade-offs, performance vs. readability trade-offs, scope changes, and Lite Mode justifications.
- **Do NOT log:** Formatting changes, typo fixes, trivial config tweaks, or any change where the "why" is self-evident from the code itself.
</decision_logging_mandate>