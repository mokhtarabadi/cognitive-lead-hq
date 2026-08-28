---
created_at: "2026-08-25T19:15:30.411061+00:00"
status: active
tags: []
updated_at: "2026-08-27T09:30:00.000000+00:00"
---

# Global Install Upgrade Workflow (OpenCode)

Trigger phrase: **"load upgrade workflow memory and follow it"**

Updates the machine-global installations of the Cognitive Lead AI HQ (MCP servers, Skills, custom agents) from the repo sources. The repo is the source of truth; the global dirs are machine-local copies.

## Install Locations

| Component      | OpenCode                                                                                                       |
| -------------- | -------------------------------------------------------------------------------------------------------------- |
| MCP servers    | `~/.config/opencode/mcp-{context,memory,lint}-server/server.py`                                                |
| Telegram MCP   | `~/.config/opencode/mcp-telegram-server/` (upstream clone of chigwell/telegram-mcp)                            |
| Skills (30)    | `~/.config/opencode/skills/<name>/SKILL.md`                                                                    |
| Custom agents  | `~/.config/opencode/agents/{cognitive-executor,cognitive-discovery}.md`                                        |
| Shell strategy | `~/.config/opencode/opencode-shell-strategy.md`                                                                |
| System prompt  | `~/.config/opencode/system-prompt.md`                                                                          |

## Source Files (repo)

- `mcp-context-server/server.py`, `mcp-memory-server/server.py`, `mcp-lint-server/server.py`
- `skill-templates/*/` (all 30 skills — `bundle-tasks` since Task 110)
- `agents/cognitive-executor.md`, `agents/cognitive-discovery.md`
- `docs/opencode-shell-strategy.md`, `system-prompt.md`

## Upgrade Steps

1. **Audit drift** (diff repo vs installed):
   ```bash
   for f in mcp-context-server/server.py mcp-memory-server/server.py mcp-lint-server/server.py; do diff -q "$f" ~/.config/opencode/"$f" || echo "DRIFT: $f"; done
   for f in agents/cognitive-executor.md agents/cognitive-discovery.md; do diff -q "$f" ~/.config/opencode/"$f" || echo "DRIFT: $f"; done
   diff -q docs/opencode-shell-strategy.md ~/.config/opencode/opencode-shell-strategy.md || echo "DRIFT: shell-strategy"
   diff -q system-prompt.md ~/.config/opencode/system-prompt.md || echo "DRIFT: system-prompt"
   for d in skill-templates/*/; do n=$(basename "$d"); diff -rq "$d" ~/.config/opencode/skills/"$n" >/dev/null 2>&1 || echo "DRIFT: opencode skill $n"; done
    # opencode.json: repo uses relative mcp-*-server/server.py for 3 core while global uses absolute /home/... — they will ALWAYS differ by design.
    diff -q opencode.json ~/.config/opencode/opencode.json && echo "UNEXPECTED: opencode.json identical (should differ relative vs absolute)" || echo "EXPECTED DRIFT: opencode.json relative vs absolute (check shape separately)"
    # tui.json parity (OpenCode 1 goal plugin): both repo tui.json and global ~/.config/opencode/tui.json must contain {"plugin":["@prevalentware/opencode-goal-plugin"]} — identical by design (no relative/absolute split)
    diff -q tui.json ~/.config/opencode/tui.json && echo "tui.json in sync ✓" || echo "DRIFT: tui.json"
    # goal plugin parity: both opencode.json + tui.json (global + project) must use @prevalentware/opencode-goal-plugin (not opencode-goal-plugin)
    grep -q "@prevalentware/opencode-goal-plugin" opencode.json && echo "project opencode.json plugin ✓" || echo "DRIFT: project opencode.json plugin"
    grep -q "@prevalentware/opencode-goal-plugin" ~/.config/opencode/opencode.json && echo "global opencode.json plugin ✓" || echo "DRIFT: global opencode.json plugin"
    ```
2. **Copy drifted files** with `cp` + `chmod +x` (only those that differ). For `opencode.json` do NOT blind copy — regenerate global with absolute paths (see `LLM.txt:7` template):
   ```bash
   cp mcp-lint-server/server.py ~/.config/opencode/mcp-lint-server/server.py && chmod +x ~/.config/opencode/mcp-lint-server/server.py
   cp system-prompt.md ~/.config/opencode/system-prompt.md
   cp skill-templates/task-generator/SKILL.md ~/.config/opencode/skills/task-generator/SKILL.md
   # global opencode.json — regenerate with absolute $HOME for 5 MCPs (custom_context, project_memory, lint, blowsh docker, telegram uv --directory ...), do not cp repo's relative version
   ```
3. **Re-verify** with the same diff commands — expect no DRIFT output except the expected `opencode.json` relative vs absolute.
4. **Smoke-test** servers launch and run the full test suite:
   ```bash
   opencode mcp list  # should show ✓ connected for custom_context, project_memory, lint
   uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
   ```

## Telegram MCP Auto-Upgrade (chigwell/telegram-mcp)

The installed copy at `~/.config/opencode/mcp-telegram-server` may or may not carry `.git` depending on how it was last installed. Either way: upgrade = shallow clone to `/tmp` + rsync overlay, preserving local secrets/state. Run this as an additional step of every upgrade cycle (Step 2.5).

1. **Audit drift vs upstream:**
   ```bash
   rm -rf /tmp/opencode/telegram-mcp-upstream
   GIT_TERMINAL_PROMPT=0 git clone --depth 30 https://github.com/chigwell/telegram-mcp.git /tmp/opencode/telegram-mcp-upstream
   diff -rq --exclude=.git --exclude=.env --exclude='*.session' --exclude=downloads --exclude=.venv --exclude=__pycache__ --exclude='*.egg-info' --exclude=mcp_errors.log --exclude=claude_desktop_config.json \
     /tmp/opencode/telegram-mcp-upstream ~/.config/opencode/mcp-telegram-server
   ```
2. **Backup, then upgrade:**
   ```bash
   cp -a ~/.config/opencode/mcp-telegram-server "/tmp/opencode/telegram-backup-$(date +%Y%m%d-%H%M%S)"
   rsync -a --exclude=.git --exclude=.env --exclude='*.session' --exclude=downloads --exclude=.venv --exclude=__pycache__ --exclude='*.egg-info' --exclude=mcp_errors.log --exclude=claude_desktop_config.json \
     /tmp/opencode/telegram-mcp-upstream/ ~/.config/opencode/mcp-telegram-server/
   cd ~/.config/opencode/mcp-telegram-server && uv sync
   ```
3. **Verify:**
   ```bash
   cd ~/.config/opencode/mcp-telegram-server
   uv run python -c "import telegram_mcp; print('import ok')"
   mv .env .env.hold && uv run --with pytest pytest tests/ -q 2>&1 | tail -2; mv .env.hold .env
   ```
   ⚠️ **Tests FAIL (~26 failures) if `.env` is present** — ALWAYS hold `.env` aside during the test run.
4. **Smoke:** server startup requires valid sessions. `AuthKeyDuplicatedError` on ANY account blocks the whole MCP handshake. Fix = regenerate that session or remove its `TELEGRAM_SESSION_STRING_<LABEL>` from `.env`. Never `pip install telegram-mcp` / `uvx telegram-mcp` from PyPI (credential-theft lookalike).
5. **Startup failure triage:** reproduce with `timeout 45 uv --directory ~/.config/opencode/mcp-telegram-server run main.py /tmp/telegram-mcp ~/.config/opencode/mcp-telegram-server/downloads </dev/null >/tmp/opencode/tg-test.log 2>&1; echo $?` and read the log.

## Key Facts

- The `lint` MCP server gains new tools when updated (e.g. `lint_system_prompt_sync`) — check `grep -c "lint_system_prompt_sync" ~/.config/opencode/mcp-lint-server/server.py` after sync (≥1).
- Skills must be synced to `~/.config/opencode/skills/`.
- Agent ports: `.md` for OpenCode (`agents/`).
- `opencode.json` permission `bundle_tasks: allow` is required for the `bundle_tasks` MCP tool (added Task 110).
- **Project vs Global `opencode.json` (Option A 2026-08-25):** Repo `opencode.json` uses **relative** `mcp-context-server/server.py` etc for 3 core — `opencode mcp list` inside clone shows `✓ connected`; literal `$HOME/...` in repo's `command` breaks. Global `~/.config/opencode/opencode.json` must use **absolute** `$HOME/.config/opencode/...` for all 5. `blowsh`/`telegram` stay `enabled:false` in repo (require global install) vs `enabled:true` in global. `diff opencode.json` will always differ — verify shape, not identity.
  - **Update 2026-08-25 (Manager-approved):** repo now OMITS the `blowsh`/`telegram` blocks entirely so they inherit the working global definitions in-project.
