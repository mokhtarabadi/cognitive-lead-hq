---
description: Dispatch the Software Architect persona on the active task for system design
---

# /architect — Software Architect persona turn

Invoke `dispatch_session_turn` (persona MCP server) with:

- `persona_name`: `"Software Architect"`
- `instruction`: the text following `/architect` (design target, requirements, constraints), plus the active task file body as user context
- `task_id`: the active task number
- `task_file_path`: the active task file path

The persona holds the full system prompt, repo rules, and cumulative task
history. Its reply is Dual-Dispatch classified:

- `XML_EXTRACTED` — a structured `<hands_*_task>` block: execute it
- `CONTEXT_REQUEST` — the persona refuses to roadmap from assumptions: its
  `context_request` carries `scope` (where to look) and `focus` (what to
  find). Run the MCP discovery tools (`custom_context_get_directory_tree`,
  then `custom_context_extract_signatures`, then
  `custom_context_read_source_files` on the narrowed files), then
  re-dispatch with the generated report path as the instruction
  (Discovery-First Mandate — satisfied with evidence, not a blank request)
- `QUESTION` — the persona needs missing context: answer and re-dispatch
- `REPORT` — free-form design findings: a blueprint is only final once the
  persona has factual codebase context (Discovery-First Mandate — never let
  it roadmap from assumptions; request a Discovery Task when context is
  empty)

Wait for the turn result before continuing the pipeline. Never treat a
`QUESTION` as a pass. STOP and wait for Manager approval before code
generation begins.
