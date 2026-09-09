---
description: Run a multi-persona brainstorming swarm turn on the active topic
---

# /brainstorm — Brainstorm Facilitator persona turn

Invoke `dispatch_session_turn` (persona MCP server) with:

- `persona_name`: `"Brainstorm Facilitator"`
- `instruction`: the text following `/brainstorm` (the ambiguous topic or
  decision to resolve), plus the active task file body as user context
- `task_id`: the active task number (or `0` for topic-only sessions)
- `task_file_path`: the active task file path when available

The persona holds the full system prompt — including the six-expert scheme
and XML output schema in `<brainstorming_protocol>` — plus repo rules and
cumulative task history. No skill preload is needed. Classify the reply per
Dual Dispatch (`XML_EXTRACTED` / `QUESTION` / `REPORT`). A `REPORT` here is
the structured swarm session output: persist its decisions as task
constraints, not as implementation.
