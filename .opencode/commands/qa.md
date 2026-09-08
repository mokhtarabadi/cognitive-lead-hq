---
description: Dispatch the QA Engineer persona on the active task for adversarial testing
---

# /qa — QA Engineer persona turn

Invoke `dispatch_session_turn` (persona MCP server) with:

- `persona_name`: `"QA Engineer"`
- `instruction`: the text following `/qa` (test target, scope, suspected weak spots), plus the active task file body as user context
- `task_id`: the active task number
- `task_file_path`: the active task file path

The persona holds the full system prompt, repo rules, and cumulative task
history. Its reply is Dual-Dispatch classified:

- `XML_EXTRACTED` — a structured `<hands_*_task>` block: execute it
- `QUESTION` — the persona needs missing context: answer and re-dispatch
- `REPORT` — free-form adversarial findings: triage each finding, fix what
  reproduces, and record evidence in the task file

Wait for the turn result before continuing the pipeline. Never treat a
`QUESTION` as a pass.
