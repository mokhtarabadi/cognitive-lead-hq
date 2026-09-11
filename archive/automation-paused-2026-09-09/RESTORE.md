# Automation System — SUPERSEDED by Unified Brain Bridge (Task 190)

## Status

The 2026-09-09 paused automation (persona loops, decision-learning loop,
9 slash commands, persona + manager-decision MCP servers) was **deleted**,
not restored. Its replacement is the single unified bridge:
`mcp-brain-bridge/` (one MCP tool, `brain_turn`) + the Bridge section in
`agents/cognitive-executor.md`. See Task 190 and `CHANGELOG.md`.

## What was removed (recoverable from git history only)

- `commands/` — the 9 automation slash commands (deleted in Task 190).
- `docs-loop-engine/`, `docs-superseded/` — obsolete docs (deleted).
- `mcp-persona-server/`, `mcp-decision-server/` — old servers (deleted).
- `skill-templates/manager-decision/` — wrapper skill (deleted).
- `tests/test_persona_server.py`, `tests/test_decision_server.py` (deleted).

## What replaced the old restore procedure

Do NOT re-add `persona`/`manager_decisions` blocks to `opencode.json`.
To call the Brain from the Hands, use the `brain` MCP server's
`brain_turn` tool (system prompt loaded from the global install,
LiteLLM-backed, XML auto-extracted). Autopilot mode is documented in
the executor Bridge section (default OFF).
