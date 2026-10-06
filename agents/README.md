# Slice: agents

## Duties

Defines the two OpenCode agent personas for the Cognitive Lead HQ: primary executor and read-only discovery subagent, including permissions, execution discipline, and Kanban rules.

## Files

- `cognitive-executor.md` — Primary execution engine persona (XML task execution, ZAC, Brain Bridge).
- `cognitive-discovery.md` — Read-only context-gathering subagent (MCP-first scans, no edits).

## Key Risks & Invariants

- Permission drift: executor allows edit/question, discovery denies edit/bash; never invert.
- Persona changes must stay in sync with `system-prompt.md` fragments and `prompts/` sources.
- No runtime code here; changes are prompt-contract changes with system-wide effect.
