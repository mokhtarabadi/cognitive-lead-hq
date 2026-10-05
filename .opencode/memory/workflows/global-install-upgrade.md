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
| MCP servers    | `~/.config/opencode/mcp-{context,memory,lint,brain}-server/` (brain bridge = `mcp-brain-bridge/`) + `~/.config/opencode/mcp-common/` (shared lib); each with `pyproject.toml` + committed `uv.lock`, launched via `<dir>/.venv/bin/python <dir>/server.py` (direct venv, never `uv run` — uv startup exceeds the V2 connect timeout under multi-session spawn load, 2026-09-29) |
| Telegram MCP   | `~/.config/opencode/mcp-telegram-server/` (upstream clone of chigwell/telegram-mcp — no fork) |
| Skills         | `~/.config/opencode/skills/<name>/SKILL.md` (synced 1:1 with `skill-templates/` — count varies, verify by diff not by number) |
| Custom agents  | `~/.config/opencode/agents/{cognitive-executor,cognitive-discovery}.md` |
| Shell strategy | `~/.config/opencode/opencode-shell-strategy.md` |
| System prompt  | `~/.config/opencode/system-prompt.md` |
| Credentials    | `~/.config/opencode/.env` (chmod 600). The MCP servers self-load `.env` at import (`<server-dir>/.env` → `<server-dir>/../.env` → `<cwd>/.env`); for the global install that is this file, for repo runs the repo-root `.env`. Keep it seeded so both the CLI and the singleton services get the keys. |

## Source Files (repo)

- `mcp-context-server/server.py`, `mcp-memory-server/server.py`, `mcp-lint-server/server.py`, `mcp-brain-bridge/*.py` (server plus capability, preflight, loop_guard, session_ledger siblings)
- `mcp-common/src/mcp_common/` (shared dotenv loader) + every server dir's `pyproject.toml` + `uv.lock` (Task 170; sync all three file kinds globally)
- `skill-templates/*/` (all skills, synced 1:1 — never hardcode the count)
- `agents/cognitive-executor.md`, `agents/cognitive-discovery.md`
- `docs/opencode-shell-strategy.md`, `system-prompt.md`, `.env.example` (PORTRAIT for `.env`, never copy secrets into docs)

## Upgrade Steps

1. **Audit drift** (diff repo vs installed — same loops as originally specified over servers, agents, shell-strategy, system-prompt, skills).
2. **Copy drifted files** with `cp` + `chmod +x` (only those that differ). Multi-module servers copy `*.py` (never `__pycache__/`). For `opencode.json` do NOT blind copy — repo uses relative paths, global uses absolute paths; edit surgically and validate JSON after every edit.
2b. **Delete global orphans** (rule added 2026-09-11: `cp` never removes, so deletions need this step). Any skill dir present under `~/.config/opencode/skills/` but absent from repo `skill-templates/` MUST be removed with `rm -rf` — that is how skill drops (e.g. brainstorm-swarm, perplexity-research) propagate globally. Same for MCP server dirs and custom agents missing from the repo. Never delete in the reverse direction (repo is source of truth).
3. **Re-verify** with the same diff commands — expect no DRIFT output except the expected `opencode.json` relative vs absolute.
4. **Smoke-test**: `opencode mcp list` (expect ONLY the currently-enabled servers connected) + `rtk test uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml pytest tests/ -q`.
4b. **RTK install** (rule added 2026-09-12): the token-trimming runner from `docs/opencode-shell-strategy.md` §8. Install the musl binary when missing (`mkdir -p ~/.local/bin && curl -fsSL -o ~/.local/bin/rtk <release-url>/rtk-x86_64-unknown-linux-musl && chmod +x ~/.local/bin/rtk`), verify `rtk --version`. Never run `rtk init -g` — it rewrites the global OpenCode config.
5. **Telegram MCP step 2.5** (upstream chigwell/telegram-mcp): lag check via `rev-list --count HEAD..origin/main`; run backup+rsync upgrade only when lag > 0. **Update-only — do NOT run telegram's own pytest suite** (its live-network tests hang ~300s on this machine and add nothing; `opencode mcp list` 6/6 is the sufficient smoke test). Rule set 2026-09-10 per Manager.

## Migration Path: stdio to singleton remote (2026-09-29, Task 277/278)

Existing users on per-session stdio entries migrate without reinstalling server code:

1. **Backup global config:** `cp ~/.config/opencode/opencode.json ~/.config/opencode/opencode.json.bak-$(date +%Y%m%d-%H%M%S)`.
2. **Start the singletons:** install `services/mcp-*.service` to `~/.config/systemd/user/`, `systemctl --user daemon-reload`, enable+start all five HQ singletons (context, memory, lint, brain, telegram); start `blowsh-singleton` (`docker run -d --name blowsh-singleton --restart unless-stopped -p 127.0.0.1:8107:8107 -e MCP_TRANSPORT=http -e MCP_HOST=0.0.0.0 -e MCP_PORT=8107 -e BROWSH_PROFILE_DIR=/data/browsh-profile -v blowsh-profile:/data/browsh-profile <image>`).
3. **Cut config:** replace each stdio `mcp.<name>` block with `{type: remote, url: http://127.0.0.1:<port>/mcp, enabled: true, timeout: <ms>}` (ports docs/services.md; telegram 30000, blowsh 120000, rest 15000). Validate JSON.
4. **Verify:** `opencode mcp list` 6/6 connected in two sessions; exactly one process per server (`ps aux | grep -E 'mcp-|telegram_mcp' | grep -v grep`).
5. **Rollback:** restore the backup config, restart sessions. HQ servers default to `streamable-http` when `MCP_TRANSPORT` is unset (explicit `stdio` still works for local debugging); telegram-mcp accepts `stdio|http|sse`.

## Key Facts

- Project vs Global `opencode.json` (Option A 2026-08-25): repo uses **relative** paths, global uses **absolute** paths; `diff` always differs — verify shape, not identity.
- V1 vs V2 installers (precision rule 2026-10-06): OpenCode V1 installs from `https://opencode.ai/install`, OpenCode V2 installs from `https://opencode.ai/v2/install` — never run the V1 URL on a V2 machine or the binary downgrades (single binary at `~/.opencode/bin/opencode`, verify with `opencode --version`). OpenChamber installs as npm package `@openchamber/web` (global via mise node, `npm install -g @openchamber/web@<version>`).
- Restart handshake: Hands never restarts OpenCode, OpenChamber, or singleton units without an explicit Manager order. Hands prepares everything, then the Manager runs the OpenCode and OpenChamber restarts.
- **Update 2026-09-09 (Tasks 175/176 — automation DISABLED):** executor and discovery automation sections commented out (manual workflow active); 9 automation commands archived with a restore guide; brainstorm-swarm skill restored but inert. Sync scope now includes propagating the DISABLED state. Smoke-test expectation lists only the currently-enabled servers.

Supersedes: workflows/global-install-upgrade (prior revision: 31 skills, 5 MCPs).
Supersedes: workflows/global-install-upgrade (prior revision: 32 skills, 7 MCPs, automation enabled).
