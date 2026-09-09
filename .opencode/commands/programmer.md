---
description: Dispatch the Senior Programmer persona on the active task for implementation instructions
---

# /programmer — Senior Programmer persona turn

Invoke `dispatch_session_turn` (persona MCP server) with:

- `persona_name`: `"Senior Programmer"`
- `instruction`: the text following `/programmer` (approved blueprint
  reference, implementation target, stack skills to load), plus the active
  task file body as user context
- `task_id`: the active task number
- `task_file_path`: the active task file path

The persona holds the full system prompt, repo rules, and cumulative task
history. Its reply is Dual-Dispatch classified:

- `XML_EXTRACTED` — a structured `<hands_implementation_task>` block with an
  explicit skill list and `- [ ] **Step N:**` checklist: execute it
  (consider `force_xml=true` when a bare report is not actionable)
- `QUESTION` — the persona needs missing context: answer and re-dispatch
- `REPORT` — free-form guidance: only accept it when it names the exact
  skills to load and the verification gates per phase

Wait for the turn result before continuing the pipeline. Never treat a
`QUESTION` as a pass. If the persona proposes bypassing framework standards
or fragile hacks (Anti-Hack Directive), STOP and escalate to the Manager.
