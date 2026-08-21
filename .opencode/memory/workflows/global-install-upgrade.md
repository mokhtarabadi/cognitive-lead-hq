---
created_at: '2026-08-19T05:09:27.234287+00:00'
status: active
tags: []
updated_at: '2026-08-21T14:45:00+00:00'
---

# Global Install Upgrade Workflow (OpenCode + Freebuff)

Trigger phrase: **"load upgrade workflow memory and follow it"**

Updates the machine-global installations of the Cognitive Lead AI HQ (MCP servers, Skills, custom agents) for BOTH runtimes from the repo sources. The repo is the source of truth; the global dirs are machine-local copies.

## Install Locations

| Component | OpenCode | Freebuff |
| --- | --- | --- |
| MCP servers | `~/.config/opencode/mcp-{context,memory,lint}-server/server.py` | `~/.agents/mcp.json` points AT the same global opencode paths (no separate copies needed) |
| Skills (30) | `~/.config/opencode/skills/<name>/SKILL.md` | `~/.agents/skills/<name>/SKILL.md` |
| Custom agents | `~/.config/opencode/agents/{cognitive-executor,cognitive-discovery}.md` | `~/.agents/{cognitive-executor,cognitive-discovery}.ts` |
| Global rules | — (n/a) | `~/.AGENTS.md` (from `freebuff/AGENTS.global.md`) |
| Shell strategy | `~/.config/opencode/opencode-shell-strategy.md` | — (n/a, OpenCode-only) |
| System prompt | `~/.config/opencode/system-prompt.md` | manual paste (n/a) |

## Source Files (repo)

- `mcp-context-server/server.py`, `mcp-memory-server/server.py`, `mcp-lint-server/server.py`
- `skill-templates/*/` (all 30 — includes `bundle-tasks` since Task 110)
- `agents/cognitive-executor.md`, `agents/cognitive-discovery.md`
- `freebuff/agents/cognitive-executor.ts`, `freebuff/agents/cognitive-discovery.ts`
- `freebuff/AGENTS.global.md`, `docs/opencode-shell-strategy.md`, `system-prompt.md`

## Upgrade Steps

1. **Audit drift** (diff repo vs installed):
   ```bash
   for f in mcp-context-server/server.py mcp-memory-server/server.py mcp-lint-server/server.py; do diff -q "$f" ~/.config/opencode/"$f" || echo "DRIFT: $f"; done
   for f in agents/cognitive-executor.md agents/cognitive-discovery.md; do diff -q "$f" ~/.config/opencode/"$f" || echo "DRIFT: $f"; done
   diff -q docs/opencode-shell-strategy.md ~/.config/opencode/opencode-shell-strategy.md || echo "DRIFT: shell-strategy"
   for f in cognitive-executor.ts cognitive-discovery.ts; do diff -q "freebuff/agents/$f" ~/.agents/"$f" || echo "DRIFT: freebuff/agents/$f"; done
   diff -q freebuff/AGENTS.global.md ~/.AGENTS.md || echo "DRIFT: AGENTS.global"
   diff -q system-prompt.md ~/.config/opencode/system-prompt.md || echo "DRIFT: system-prompt"
   for d in skill-templates/*/; do n=$(basename "$d"); diff -rq "$d" ~/.config/opencode/skills/"$n" >/dev/null 2>&1 || echo "DRIFT: opencode skill $n"; diff -rq "$d" ~/.agents/skills/"$n" >/dev/null 2>&1 || echo "DRIFT: freebuff skill $n"; done
   diff -q opencode.json ~/.config/opencode/opencode.json || echo "DRIFT: opencode.json"
   ```
2. **Copy drifted files** with `cp` + `chmod +x` (only those that differ):
   ```bash
   cp mcp-lint-server/server.py ~/.config/opencode/mcp-lint-server/server.py && chmod +x ~/.config/opencode/mcp-lint-server/server.py
   cp system-prompt.md ~/.config/opencode/system-prompt.md
   cp skill-templates/task-generator/SKILL.md ~/.config/opencode/skills/task-generator/SKILL.md
   cp skill-templates/task-generator/SKILL.md ~/.agents/skills/task-generator/SKILL.md
   cp opencode.json ~/.config/opencode/opencode.json
   ```
3. **Re-verify** with the same diff commands — expect no DRIFT output.
4. **Smoke-test** servers launch and run the full test suite (52 passed expected):
   ```bash
   uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
   ```

## Key Facts

- The `lint` MCP server gains new tools when updated (e.g. `lint_system_prompt_sync`) — check `grep -c "lint_system_prompt_sync" ~/.config/opencode/mcp-lint-server/server.py` after sync (≥1).
- Freebuff needs NO separate MCP server copies — `~/.agents/mcp.json` references `~/.config/opencode/mcp-*-server/server.py` by absolute path, so fixing opencode fixes freebuff.
- Skills must be synced to BOTH `~/.config/opencode/skills/` AND `~/.agents/skills/`.
- Agent ports: `.md` for OpenCode (`agents/`), `.ts` for Freebuff (`freebuff/agents/`).
- `opencode.json` permission `bundle_tasks: allow` is required for the `bundle_tasks` MCP tool (added Task 110).
- Last run: 2026-08-21 — drift was `mcp-lint-server/server.py`, `system-prompt.md` (8.5.0→8.6.0), `task-generator` skill (bundle workflow), `opencode.json` (bundle_tasks:allow). All 30 skills ×2, all 4 agents, context+memory servers, shell-strategy, and `~/.AGENTS.md` already identical. 52 tests passed.