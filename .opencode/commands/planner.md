---
description: Dispatch the Project Planner persona on the active task for Kanban state
---

# /planner — Project Planner persona turn

Invoke `dispatch_session_turn` (persona MCP server) with:

- `persona_name`: `"Project Planner"`
- `instruction`: the text following `/planner` (status query, milestone
  scope, task-file operation), plus the active task file body as user context
- `task_id`: the active task number
- `task_file_path`: the active task file path

The persona holds the full system prompt, repo rules, and cumulative task
history. Its reply is Dual-Dispatch classified:

- `XML_EXTRACTED` — a structured `<hands_*_task>` block (task-generator
  template with `BEGIN/END_GIT_DIFF` markers, Kanban moves): execute it
- `CONTEXT_REQUEST` — the persona is smart enough to know it lacks codebase
  evidence: its `context_request` carries `scope` (where to look) and
  `focus` (what to find). Run the MCP discovery tools
  (`custom_context_get_directory_tree`, then
  `custom_context_extract_signatures`, then `custom_context_read_source_files`
  on the narrowed files), then re-dispatch with the generated report path
  as the instruction. Never answer a plan from assumptions.
- `QUESTION` — the persona needs missing context: answer and re-dispatch
- `REPORT` — state summary: task files stay the single source of truth
  across `backlog`, `in-progress`, `qa`, `completed`, `archive`

Wait for the turn result before continuing the pipeline. Never treat a
`QUESTION` as a pass.
