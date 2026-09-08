---
description: Run a multi-persona brainstorming swarm turn on the active topic
---

# /brainstorm — brainstorm-swarm session turn

1. Load the `brainstorm-swarm` skill (six personas: system_architect,
   security_engineer, product_manager, business_strategist, legal_advisor,
   critical_thinker).
2. Invoke `dispatch_session_turn` (persona MCP server) with:
   - `persona_name`: `"Brainstorm Facilitator"`
   - `instruction`: the text following `/brainstorm` (the ambiguous topic or
     decision to resolve), plus the active task file body as user context
   - `task_id`: the active task number (or `0` for topic-only sessions)
   - `task_file_path`: the active task file path when available
3. Classify the reply per Dual Dispatch (`XML_EXTRACTED` / `QUESTION` /
   `REPORT`). A `REPORT` here is the structured swarm session output:
   persist its decisions as task constraints, not as implementation.
