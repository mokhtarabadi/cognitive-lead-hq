---
created_at: '2026-10-15T05:38:49.927703+00:00'
status: active
tags: []
updated_at: '2026-11-13T00:00:00.000000+00:00'
---

# Upstream Upgrade Dependency Sync (Manager standing rule 2026-10-15, extended 2026-11-13)

After EVERY upstream git-pull upgrade of a deployed server (telegram-mcp, HQ MCP singletons), sync the venv dependencies BEFORE restarting the service. Upstream code often adds imports (incident: telegram-mcp pull added `from pypdf import PdfReader`; venv lacked pypdf and the service crash-looped 9000+ times).

Procedure: 1) `systemctl --user stop <service>` to halt the crash loop. 2) Diff new imports against the venv (`python -c import check` per top-level module, using correct import names: PIL not pillow, pythonjsonlogger not python-json-logger). 3) Install with `uv pip install --python <venv>/bin/python <pkgs>` covering pyproject `dependencies`. 4) Verify every declared import resolves. 5) Start the service and confirm NRestarts=0 plus a clean port response. Never run telegram's own pytest suite (live-network tests hang; memory rule).

## The full refresh chain (2026-11-13)

A server dependency sync is ONE step of an upgrade. The global install holds several independent copies, and refreshing only the servers leaves the rest stale — that drift was found twice in a row (2026-11-13 twice: skills/agents stale, then system-prompt stale). Upgrade order:

1. **Binaries** — `curl -fsSL https://opencode.ai/v2/install | bash` (OpenCode V2) and `npm install -g @openchamber/web@latest` (OpenChamber).
2. **Server sources + venv deps** — copy `mcp-*/` sources, then run the dependency sync above for each service.
3. **Skills** — `cp -r skill-templates/* ~/.config/opencode/skills/` then `rm -f ~/.config/opencode/skills/{DECISIONS.md,README.md}`; expect exactly 24 skill directories and no stray `.md` at the skills root.
4. **Agents** — copy `agents/cognitive-{executor,discovery}.md` to `~/.config/opencode/agents/`; expect exactly 2 files (no `DECISIONS.md` / `README.md`).
5. **Prompts** — `python3 scripts/prompt-build/assemble_system_prompt.py` then `--stages`, and copy `system-prompt.md` + `build/stage-prompts/system-prompt.*.md` to `~/.config/opencode/`. The full prompt is the fallback and must stay byte-identical to the assembler output.
6. **Plugins** — purge `~/.cache/opencode/npm/git-opencode-*-plugin-*` so the next start re-fetches from GitHub; `opencode plugin update` does NOT work for git specs (use remove+add).
7. **Restart** — the MCP singletons, then the Manager restarts OpenCode and OpenChamber (the Hands never restarts the editor or the app).
8. **Drift audit** — diff every copied target against its repo source; a non-empty diff means a step was skipped.

**One global skill root.** The legacy `~/.agents/skills` root (Freebuff-era) was removed 2026-11-13. If it reappears, delete it rather than syncing it — see `opencode_config/skill-sources-multiple-roots.md`.

**Freebuff is gone from this machine** (removed 2026-11-13: npm global `freebuff`, `~/.config/manicode/`, `~/warp-fr/.freebuff/`, and the Freebuff-era `~/.AGENTS.md`). The canonical agent definition lives in `~/.config/opencode/agents/cognitive-executor.md`; `~/.AGENTS.md` was a V1-format Freebuff artifact that OpenCode V2 never read.
