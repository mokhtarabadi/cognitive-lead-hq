---
created_at: '2026-09-10T19:28:03.619203+00:00'
status: active
tags: []
updated_at: '2026-09-10T19:28:03.619220+00:00'
---

# Global Install Upgrade Workflow (OpenCode)

Trigger phrase: **"load upgrade workflow memory and follow it"**

Updates the machine-global installations of the Cognitive Lead AI HQ (MCP servers, Skills, custom agents) from the repo sources. The repo is the source of truth; the global dirs are machine-local copies.

## Install Locations

| Component      | OpenCode                                                                                                       |
| -------------- | -------------------------------------------------------------------------------------------------------------- |
| MCP servers    | `~/.config/opencode/mcp-{context,memory,lint}-server/` + `~/.config/opencode/mcp-persona-server/` (4 modules, Task 167) + `~/.config/opencode/mcp-decision-server/` (2 modules, Task 168) + `~/.config/opencode/mcp-common/` (shared lib, Task 170); each with `pyproject.toml` + committed `uv.lock`, launched via `uv run --project <dir> <dir>/server.py` |
| Telegram MCP   | `~/.config/opencode/mcp-telegram-server/` (upstream clone of chigwell/telegram-mcp — no fork) |
| Skills         | `~/.config/opencode/skills/<name>/SKILL.md` (synced 1:1 with `skill-templates/` — count varies, verify by diff not by number) |
| Custom agents  | `~/.config/opencode/agents/{cognitive-executor,cognitive-discovery}.md` |
| Shell strategy | `~/.config/opencode/opencode-shell-strategy.md` |
| System prompt  | `~/.config/opencode/system-prompt.md` |
| Credentials    | `~/.config/opencode/.env` (chmod 600 backup of project `.env`; project copy stays authoritative since opencode loads project env for servers) |

## Source Files (repo)

- `mcp-context-server/server.py`, `mcp-memory-server/server.py`, `mcp-lint-server/server.py`
- `mcp-persona-server/*.py` (server, dual_dispatch, session, telegram), `mcp-decision-server/*.py` (server, redactor)
- `mcp-common/src/mcp_common/` (shared dotenv loader) + every server dir's `pyproject.toml` + `uv.lock` (Task 170; sync all three file kinds globally)
- `skill-templates/*/` (all skills, synced 1:1 — never hardcode the count)
- `agents/cognitive-executor.md`, `agents/cognitive-discovery.md`
- `docs/opencode-shell-strategy.md`, `system-prompt.md`, `.env.example` (PORTRAIT for `.env`, never copy secrets into docs)

## Upgrade Steps

1. **Audit drift** (diff repo vs installed — same loops as originally specified over servers, agents, shell-strategy, system-prompt, skills, tui.json, goal-plugin greps).
2. **Copy drifted files** with `cp` + `chmod +x` (only those that differ). Multi-module servers copy `*.py` (never `__pycache__/`). For `opencode.json` do NOT blind copy — repo uses relative paths, global uses absolute paths; edit surgically and validate JSON after every edit.
3. **Re-verify** with the same diff commands — expect no DRIFT output except the expected `opencode.json` relative vs absolute.
4. **Smoke-test**: `opencode mcp list` (expect ONLY the currently-enabled servers connected) + repo persona test suite (`uv run --project mcp-persona-server --with pytest --with pathspec pytest tests/ -q`).
5. **Telegram MCP step 2.5** (upstream chigwell/telegram-mcp): lag check via `rev-list --count HEAD..origin/main`; run backup+rsync upgrade only when lag > 0. **Update-only — do NOT run telegram's own pytest suite** (its live-network tests hang ~300s on this machine and add nothing; `opencode mcp list` 5/5 is the sufficient smoke test). Rule set 2026-09-10 per Manager.

## Key Facts

- Project vs Global `opencode.json` (Option A 2026-08-25): repo uses **relative** paths, global uses **absolute** paths; `diff` always differs — verify shape, not identity.
- **Update 2026-09-09 (Tasks 175/176 — automation DISABLED):** persona + manager_decisions MCP servers are DISABLED (blocks removed from repo AND global `opencode.json`, `PERSONA_*`/`DECISION_*` vars commented in `.env.example`); executor/discovery automation sections commented out (manual workflow active); 9 automation commands archived to `archive/automation-paused-2026-09-09/commands/` with `RESTORE.md`; brainstorm-swarm skill restored but inert. Server code dirs, tests, skills, fragments are KEPT (not deleted). Sync scope now includes propagating the DISABLED state (neutralized agents, stripped opencode.json). Smoke-test expectation: 5 connected (custom_context, project_memory, lint, blowsh, telegram) — persona/decisions absent by design.

Supersedes: workflows/global-install-upgrade (prior revision: 31 skills, 5 MCPs).
Supersedes: workflows/global-install-upgrade (prior revision: 32 skills, 7 MCPs, automation enabled).
