---
description: Dispatch the Code Reviewer persona on the active task for standards audit
---

# /reviewer — Code Reviewer persona turn

Invoke `dispatch_session_turn` (persona MCP server) with:

- `persona_name`: `"Code Reviewer"`
- `instruction`: the text following `/reviewer` (files, diff scope, standards
  in question), plus the active task file body as user context
- `task_id`: the active task number
- `task_file_path`: the active task file path

The persona audits against `AGENTS.md`, `docs/conventions.md`, and the skill
set loaded for the task's stack. Its reply is Dual-Dispatch classified:

- `XML_EXTRACTED` — a structured `<hands_*_task>` block: execute it
- `QUESTION` — the persona needs missing context: answer and re-dispatch
- `REPORT` — findings list: apply the ones that reproduce under the repo's
  linters/tests, dispute the rest with evidence in the Execution Log

A `REPORT` with zero blocking findings is the review pass. Wait for the turn
result before opening the admin approval gate.
