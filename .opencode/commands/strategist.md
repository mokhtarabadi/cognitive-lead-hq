---
description: Dispatch the Sprint Strategist persona on the active task for capacity-gated planning
---

# /strategist — Sprint Strategist persona turn

Invoke `dispatch_session_turn` (persona MCP server) with:

- `persona_name`: `"Sprint Strategist"`
- `instruction`: the text following `/strategist` (backlog candidates,
  sprint goal, capacity question), plus the active task file body as user
  context
- `task_id`: the active task number
- `task_file_path`: the active task file path

The persona holds the full system prompt, repo rules, and cumulative task
history. Its reply is Dual-Dispatch classified:

- `XML_EXTRACTED` — a structured `<hands_*_task>` block: execute it
- `QUESTION` — the persona needs missing context: answer and re-dispatch
- `REPORT` — ranked sprint plan: every candidate must carry a complexity
  estimate (S/M/L/XL), a MoSCoW tier, and WIP-limit accounting (max 3
  concurrent). The persona may say NO with evidence — a pushback backed by
  capacity data is a pass, not a failure

Wait for the turn result before continuing the pipeline. Never treat a
`QUESTION` as a pass.
