---
name: audit-agents
description: Enforces decentralized task management, UI/UX design strictness, and global state constraints within AGENTS.md.
---

# OpenCode Skill: Agent Protocol Auditor

## 🛑 STRICT EXECUTION RULES (Priority 1)

1. **Primary Source of Truth**: You MUST read `AGENTS.md` at the project root using local file read tools.
2. **Read-Only First**: Evaluate the contents of `AGENTS.md` against the Target Audit Criteria before attempting any file modifications.
3. **Immutable Formatting**: If patching is required, maintain the exact Markdown list structure, headers, and spacing of the existing file.

## Target Audit Criteria

The `AGENTS.md` file MUST explicitly contain the following operational constraints, ideally within a `Task Management & OpenCode Rules` section:

- **Core File Locations**: MUST explicitly list paths for `AGENTS.md`, `DESIGN.md`, `tasks/`, and `.opencode/skills/`.
- **Decentralized Task Management**: Agents MUST strictly use decentralized, individual task files in the `tasks/` directory as their single source of truth.
- **No Monolithic State**: Agents are strictly forbidden from creating `TODO.md` or `STATE.md`.
- **Mandatory End-Of-Task Sequence**: MUST explicitly mandate a 3-step completion process: 1) Write manual reasoning in the task file. 2) Call the `custom_context_stage_and_inject_diff` MCP tool. 3) Notify the Manager.
- **UI/UX Enforcement**: Any UI/UX changes MUST enforce the guidelines defined in the project's `DESIGN.md`.

## Resolution Protocol

1. **Evaluation**: Compare the active `AGENTS.md` text against the Target Audit Criteria.
2. **Patching**: If any constraints are missing, ambiguous, or incorrect, use the `apply_patch` tool to inject the exact missing rules.
3. **Halt on Success**: If the file already complies 100%, DO NOT execute any write operations.

## Summary Phase

Upon completion, output a strict, formatted summary for the Manager:

### Agent Audit Summary

**Audit Status:** [PASSED | FIXED]
**Violations Found:** [List of missing/incorrect rules, or "None"]
**Actions Taken:** [Description of the patch applied, or "File already compliant"]
