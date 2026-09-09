---
description: Dispatch the UI/UX Designer persona on the active task for visual strategy
---

# /designer — UI/UX Designer persona turn

Invoke `dispatch_session_turn` (persona MCP server) with:

- `persona_name`: `"UI/UX Designer"`
- `instruction`: the text following `/designer` (screen or feature, layout
  goal, styling constraints), plus the active task file body as user context
- `task_id`: the active task number
- `task_file_path`: the active task file path

The persona holds the full system prompt, repo rules, and cumulative task
history. Its reply is Dual-Dispatch classified:

- `XML_EXTRACTED` — a structured `<hands_*_task>` block: execute it
- `QUESTION` — the persona needs missing context: answer and re-dispatch
- `REPORT` — visual strategy: must cover offline states, latency, Dark/Light
  contrast, and a11y (not just the happy path), enforced through local
  `DESIGN.md` tokens and component isolation

Wait for the turn result before continuing the pipeline. Never treat a
`QUESTION` as a pass. Do not let it hallucinate layouts — demand codebase
context first.
