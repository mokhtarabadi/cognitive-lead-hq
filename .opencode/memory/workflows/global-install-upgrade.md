---
created_at: '2026-10-24T06:46:04.780504+00:00'
status: active
tags: []
updated_at: '2026-10-24T06:46:04.780527+00:00'
---

# Global Install Upgrade Workflow (OpenCode)

Trigger phrase: **"load upgrade workflow memory and follow it"**

Updates the machine-global installations of the Cognitive Lead AI HQ (MCP servers, Skills, custom agents) from the repo sources. The repo is the source of truth; the global dirs are machine-local copies.

## Install Locations

| Component      | OpenCode                                                                                                       |
| -------------- | -------------------------------------------------------------------------------------------------------------- |
| MCP servers    | `~/.config/opencode/mcp-context-server/`, `mcp-memory-server/`, `mcp-lint-server/`, `mcp-brain-bridge/`, `mcp-planner-server/` + `~/.config/opencode/mcp-common/` (shared lib); each with `pyproject.toml` + committed `uv.lock`, launched via `<dir>/.venv/bin/python <dir>/server.py` (direct venv, never `uv run` — uv startup exceeds the V2 connect timeout under multi-session spawn load, 2026-09-29) |
| Planner        | Same dir family (`mcp-planner-server/`), with three extras: `static/` must be copied (the dashboard is served from it), the venv is built with `uv sync` (never `uv pip install -e .` — the package declares no `[build-system]`, so an editable install cannot work), and `PLANNER_PROJECT_ROOT` is supplied by a local `~/.config/systemd/user/mcp-planner.service.d/override.conf` drop-in so the committed unit stays machine-independent (its `WorkingDirectory` is the install dir, which holds no `tasks/`). |
| Telegram MCP   | `~/.config/opencode/mcp-telegram-server/` (upstream clone of chigwell/telegram-mcp — no fork) |
| Skills         | `~/.config/opencode/skills/<name>/SKILL.md` (synced 1:1 with `skill-templates/` — count varies, verify by diff not by number) |
| Custom agents  | `~/.config/opencode/agents/{cognitive-executor,cognitive-discovery}.md` (**regular files, not symlinks** — editing the repo copy alone leaves the running agent stale; diff, then copy, then `cmp`) |
| Shell strategy | `~/.config/opencode/opencode-shell-strategy.md` |
| System prompt  | `~/.config/opencode/system-prompt.md` |
| Credentials    | `~/.config/opencode/.env` (chmod 600). The MCP servers self-load `.env` at import (`<server-dir>/.env` → `<server-dir>/../.env` → `<cwd>/.env`); for the global install that is this file, for repo runs the repo-root `.env`. Keep it seeded so both the CLI and the singleton services get the keys. |

## Source Files (repo)

- `mcp-context-server/server.py`, `mcp-memory-server/server.py`, `mcp-lint-server/server.py`, `mcp-brain-bridge/*.py` (server plus capability, preflight, loop_guard, session_ledger siblings)
- `mcp-planner-server/{server.py,pyproject.toml,uv.lock,README.md,DECISIONS.md}` + `mcp-planner-server/static/`
- `mcp-common/src/mcp_common/` (shared dotenv loader) + every server dir's `pyproject.toml` + `uv.lock` (Task 170; sync all three file kinds globally)
- `skill-templates/*/` (all skills, synced 1:1 — never hardcode the count)
- `agents/cognitive-executor.md`, `agents/cognitive-discovery.md`
- `docs/opencode-shell-strategy.md`, `system-prompt.md`, `.env.example` (PORTRAIT for `.env`, never copy secrets into docs)

## Upgrade Steps

1. **Audit drift** (diff repo vs installed — same loops as originally specified over servers, agents, shell-strategy, system-prompt, skills).
2. **Copy drifted files** with `cp` + `chmod +x` (only those that differ). Multi-module servers copy `*.py` (never `__pycache__/`). For `opencode.json` do NOT blind copy — repo uses relative paths, global uses absolute paths; edit surgically and validate JSON after every edit. **Back it up first** (`opencode.json.bak-<UTC timestamp>`): a malformed or truncated edit disconnects every MCP server for every session, not just the one being changed.
2b. **Delete global orphans** (rule added 2026-09-11: `cp` never removes, so deletions need this step). Any skill dir present under `~/.config/opencode/skills/` but absent from repo `skill-templates/` MUST be removed with `rm -rf` — that is how skill drops (e.g. brainstorm-swarm, perplexity-research) propagate globally. Same for MCP server dirs and custom agents missing from the repo. Never delete in the reverse direction (repo is source of truth).
3. **Re-verify** with the same diff commands — expect no DRIFT output except the expected `opencode.json` relative vs absolute.
4. **Smoke-test**: verify the resolved config, not the CLI. On v2.1.4 `opencode mcp list` prints **"No MCP servers configured" for every entry**, including servers that are demonstrably live in a working session — it is a pre-existing CLI defect, useless as a gate. Use `opencode debug config | grep -c '127.0.0.1:810'` (expect 7 MCP entries: 8101 lint, 8102 context, 8103 memory, 8105 brain, 8106 telegram, 8107 blowsh, 8108 planner; **8104 does not exist**), `systemctl --user is-active mcp-<name>` per singleton, and `curl -s -o /dev/null -w "%{http_code}"` per port. Then the repo suite: `rtk test uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml pytest tests/ -q`.
4b. **RTK install** (rule added 2026-09-12): the token-trimming runner from `docs/opencode-shell-strategy.md` §8. Install the musl binary when missing (`mkdir -p ~/.local/bin && curl -fsSL -o ~/.local/bin/rtk <release-url>/rtk-x86_64-unknown-linux-musl && chmod +x ~/.local/bin/rtk`), verify `rtk --version`. Never run `rtk init -g` — it rewrites the global OpenCode config.
5. **Telegram MCP step 2.5** (upstream chigwell/telegram-mcp): lag check via `rev-list --count HEAD..origin/main`; run backup+rsync upgrade only when lag > 0. **Update-only — do NOT run telegram's own pytest suite** (its live-network tests hang ~300s on this machine and add nothing). Rule set 2026-09-10 per Manager.

## Migration Path: stdio to singleton remote (2026-09-29, Task 277/278)

Existing users on per-session stdio entries migrate without reinstalling server code:

1. **Backup global config:** `cp ~/.config/opencode/opencode.json ~/.config/opencode/opencode.json.bak-$(date +%Y%m%d-%H%M%S)`.
2. **Start the singletons:** install `services/mcp-*.service` to `~/.config/systemd/user/`, `systemctl --user daemon-reload`. For the planner, build its venv (`cd ~/.config/opencode/mcp-planner-server && uv sync`) and write the `PLANNER_PROJECT_ROOT` drop-in **before** starting the unit, because `ExecStart` needs `.venv/bin/python`. Then enable+start every HQ singleton (`for s in lint context memory brain telegram planner`), and start `blowsh-singleton` (`docker run -d --name blowsh-singleton --restart unless-stopped -p 127.0.0.1:8107:8107 -e MCP_TRANSPORT=http -e MCP_HOST=0.0.0.0 -e MCP_PORT=8107 -e BROWSH_PROFILE_DIR=/data/browsh-profile -v blowsh-profile:/data/browsh-profile <image>`).
3. **Cut config:** replace each stdio `mcp.<name>` block under `mcp.servers` with `{type: remote, url: http://127.0.0.1:<port>/mcp, disabled: false, timeout: {catalog, execution}}` (ports docs/services.md; telegram 30000, blowsh 120000, brain 600000+, planner 15000/30000, rest 15000). Validate JSON after the edit.
4. **Verify:** `opencode debug config` resolves 7 entries; exactly one process per server (`ps aux | grep -E 'mcp-|telegram_mcp' | grep -v grep`); each port answers.
5. **Rollback:** restore the backup config, restart sessions. HQ servers default to `streamable-http` when `MCP_TRANSPORT` is unset (explicit `stdio` still works for local debugging); telegram-mcp accepts `stdio|http|sse`.

## Retired Components (do not re-add, do not reference)

- **Manager-decisions MCP (`mcp-decision-server`, port 8104) is fully retired.** There is no server directory in the repo, no `services/mcp-decision.service`, no systemd unit, and no `opencode.json` entry. Its `manager_decisions` tools, its `DECISION_*` env vars (`DECISION_API_BASE`, `DECISION_API_KEY`, `DECISION_MODEL`, `DECISION_REASONING_EFFORT`, `DECISION_TRANSCRIPT_MAX_CHARS`), and `docs/manager-decisions.md` are all dead. `docs/services.md` and `docs/brain-bridge.md` still carry stale 8104 / `DECISION_*` rows — treat those as documentation debt, never as evidence the server exists. Historical mentions under `docs/history/` are frozen archives and must not be edited.

## Key Facts

- Project vs Global `opencode.json` (Option A 2026-08-25): repo uses **relative** paths, global uses **absolute** paths; `diff` always differs — verify shape, not identity.
- Global `opencode.json` shape is `mcp.servers.<name>` (not `mcp.<name>`); `.opencode/memory` notes that predate this are stale.
- The planner (`mcp-planner-server`, `127.0.0.1:8108`) serves three routes on one listener: `/` (dashboard), `/api/status` (JSON contract), `/mcp` (tools). It reads `tasks/` Markdown as truth and is a derived index only.
- V1 vs V2 installers (precision rule 2026-10-06): OpenCode V1 installs from `https://opencode.ai/install`, OpenCode V2 installs from `https://opencode.ai/v2/install` — never run the V1 URL on a V2 machine or the binary downgrades (single binary at `~/.opencode/bin/opencode`, verify with `opencode --version`). OpenChamber installs as npm package `@openchamber/web` (global via mise node, `npm install -g @openchamber/web@<version>`).
- Restart handshake: Hands never restarts OpenCode, OpenChamber, or singleton units without an explicit Manager order. Hands prepares everything, then the Manager runs the OpenCode and OpenChamber restarts.
- **Update 2026-09-09 (Tasks 175/176 — automation DISABLED):** executor and discovery automation sections commented out (manual workflow active); 9 automation commands archived with a restore guide; brainstorm-swarm skill restored but inert. Sync scope now includes propagating the DISABLED state. Smoke-test expectation lists only the currently-enabled servers.

Supersedes: workflows/global-install-upgrade (prior revision: 31 skills, 5 MCPs).
Supersedes: workflows/global-install-upgrade (prior revision: 32 skills, 7 MCPs, automation enabled).
