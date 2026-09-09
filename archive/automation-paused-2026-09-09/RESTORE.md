# Automation System — Paused 2026-09-09 (Tasks 175/176)

## Why paused

Manager order: the intelligent/automated orchestration system (persona
loops, decision-learning loop, automation slash commands, persona +
manager-decision MCP servers) is **not mature enough yet** and is not
working well enough. Disabled for now. **Nothing was deleted** — all code,
configs, and docs are preserved for future development.

## What is archived here

- `commands/` — the 9 automation slash commands, moved verbatim via
  `git mv` from `.opencode/commands/`: `qa.md`, `reviewer.md`,
  `manager.md`, `brainstorm.md`, `architect.md`, `designer.md`,
  `programmer.md`, `planner.md`, `strategist.md`.
- The automation *rules* stay in place but neutralized:
  - `agents/cognitive-executor.md` — `## Persona Loop` +
    `### Decision Learning Loop` wrapped in
    `AUTOMATION-PAUSED-2026-09-09 ... AUTOMATION-RESUME` HTML comments;
    active behavior is `## Manual Workflow`.
  - `agents/cognitive-discovery.md` — verified ZERO automation refs,
    untouched.
  - Repo + global `opencode.json` — `persona` / `manager_decisions` MCP
    blocks removed from active JSON (JSON has no comments); exact removed
    text is documented in Tasks 175/176.
  - `.env.example` — `PERSONA_*` / `DECISION_*` vars commented out
    (`# PAUSED-2026-09-09`).
- Server implementations untouched and shippable: `mcp-persona-server/`,
  `mcp-decision-server/`, `skill-templates/manager-decision/`,
  `prompts/fragments/{06-personas,07-agent_skills_registry,12-brainstorming_protocol}.md`.

## What was implemented (history)

Tasks 167 (persona engine), 168 (decision learning), 170 (hardening),
171 (META), 172 (sync), 173 (plugin docs), 174 (persona commands,
skill removal, persistence cards, context-request lane, split gates,
replay cap, lineage fallback). See `tasks/completed/` for full records.

## How to restore (when the system is mature)

1. `git mv archive/automation-paused-2026-09-09/commands/*.md .opencode/commands/`
2. In `agents/cognitive-executor.md`: delete the Manual Workflow section
   (or keep it as fallback) and remove the
   `AUTOMATION-PAUSED-2026-09-09` / `AUTOMATION-RESUME` comment markers.
3. Re-add the `persona` + `manager_decisions` blocks to repo and global
   `opencode.json` (Task 176 documents the exact removed JSON).
4. Uncomment `PERSONA_*` / `DECISION_*` in `.env.example`; ensure live
   `.env` values exist.
5. Re-run the global-install upgrade workflow, then `opencode mcp list`
   must show persona + manager_decisions connected.
6. Run the persona test suite green before re-enabling.

## Appendix A — exact removed JSON (Task 176, 2026-09-09)

Repo `opencode.json` — `mcp.persona` block (global variant identical
except absolute paths
`/home/mohammad/.config/opencode/mcp-persona-server`):

```json
    "persona": {
      "type": "local",
      "command": ["uv", "run", "--project", "mcp-persona-server", "mcp-persona-server/server.py"],
      "enabled": true,
      "timeout": 600000,
      "environment": {
        "OPENROUTER_API_KEY": "{env:OPENROUTER_API_KEY}",
        "PERSONA_MODEL": "{env:PERSONA_MODEL}",
        "PERSONA_REASONING_EFFORT": "{env:PERSONA_REASONING_EFFORT}",
        "PERSONA_TEMPERATURE": "{env:PERSONA_TEMPERATURE}",
        "PERSONA_MAX_TOKENS": "{env:PERSONA_MAX_TOKENS}",
        "TELEGRAM_BOT_TOKEN": "{env:TELEGRAM_BOT_TOKEN}",
        "TELEGRAM_CHAT_ID": "{env:TELEGRAM_CHAT_ID}",
        "TELEGRAM_APPROVAL_TIMEOUT_SECONDS": "{env:TELEGRAM_APPROVAL_TIMEOUT_SECONDS}"
      }
    },
```

Repo `opencode.json` — `mcp.manager_decisions` block (global variant:
absolute paths `/home/mohammad/.config/opencode/mcp-decision-server`):

```json
    "manager_decisions": {
      "type": "local",
      "command": ["uv", "run", "--project", "mcp-decision-server", "mcp-decision-server/server.py"],
      "enabled": true,
      "timeout": 600000,
      "environment": {
        "OPENROUTER_API_KEY": "{env:OPENROUTER_API_KEY}",
        "PERSONA_MODEL": "{env:PERSONA_MODEL}",
        "DECISION_MODEL": "{env:DECISION_MODEL}",
        "DECISION_TEMPERATURE": "{env:DECISION_TEMPERATURE}"
      }
    }
```

Removed permission lines — repo (9):
`dispatch_session_turn`, `get_session_summary`, `escalate_to_admin`,
`request_admin_approval`, `extract_session_decisions`,
`record_manager_decision`, `query_manager_decisions`,
`get_manager_profile`, `propose_profile_evolution` (all `"allow"`).
Global (same 9 plus): `open_approval_gate`, `poll_approval_gate`
(all `"allow"`). All other permission lines untouched.
