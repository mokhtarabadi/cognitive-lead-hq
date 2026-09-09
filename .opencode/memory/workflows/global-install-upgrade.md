---
created_at: '2026-09-08T22:03:15.211239+00:00'
status: active
tags: []
updated_at: '2026-09-08T22:03:15.211356+00:00'
---

# Global Install Upgrade Workflow (OpenCode)

Trigger phrase: **"load upgrade workflow memory and follow it"**

Updates the machine-global installations of the Cognitive Lead AI HQ (MCP servers, Skills, custom agents) from the repo sources. The repo is the source of truth; the global dirs are machine-local copies.

## Install Locations

| Component      | OpenCode                                                                                                       |
| -------------- | -------------------------------------------------------------------------------------------------------------- |
| MCP servers    | `~/.config/opencode/mcp-{context,memory,lint}-server/` + `~/.config/opencode/mcp-persona-server/` (4 modules, Task 167) + `~/.config/opencode/mcp-decision-server/` (2 modules, Task 168) + `~/.config/opencode/mcp-common/` (shared lib, Task 170); each with `pyproject.toml` + committed `uv.lock`, launched via `uv run --project <dir> <dir>/server.py` |
| Telegram MCP   | `~/.config/opencode/mcp-telegram-server/` (upstream clone of chigwell/telegram-mcp — no fork) |
| Skills (32)    | `~/.config/opencode/skills/<name>/SKILL.md` (`manager-decision` since Task 168) |
| Custom agents  | `~/.config/opencode/agents/{cognitive-executor,cognitive-discovery}.md` |
| Shell strategy | `~/.config/opencode/opencode-shell-strategy.md` |
| System prompt  | `~/.config/opencode/system-prompt.md` |
| Credentials    | `~/.config/opencode/.env` (chmod 600 backup of project `.env`; project copy stays authoritative since opencode loads project env for servers) |

## Source Files (repo)

- `mcp-context-server/server.py`, `mcp-memory-server/server.py`, `mcp-lint-server/server.py`
- `mcp-persona-server/*.py` (server, dual_dispatch, session, telegram), `mcp-decision-server/*.py` (server, redactor)
- `mcp-common/src/mcp_common/` (shared dotenv loader) + every server dir's `pyproject.toml` + `uv.lock` (Task 170; sync all three file kinds globally)
- `skill-templates/*/` (all 32 skills — `bundle-tasks` since Task 110, `manager-decision` since Task 168)
- `agents/cognitive-executor.md`, `agents/cognitive-discovery.md`
- `docs/opencode-shell-strategy.md`, `system-prompt.md`, `.env.example` (PORTRAIT for `.env`, never copy secrets into docs)

## Upgrade Steps

1. **Audit drift** (diff repo vs installed):
   ```bash
   for f in mcp-context-server/server.py mcp-memory-server/server.py mcp-lint-server/server.py; do diff -q "$f" ~/.config/opencode/"$f" || echo "DRIFT: $f"; done
   for f in mcp-persona-server/dual_dispatch.py mcp-persona-server/session.py mcp-persona-server/telegram.py mcp-persona-server/server.py mcp-decision-server/redactor.py mcp-decision-server/server.py; do diff -q "$f" ~/.config/opencode/"$f" || echo "DRIFT: $f"; done
   for f in agents/cognitive-executor.md agents/cognitive-discovery.md; do diff -q "$f" ~/.config/opencode/"$f" || echo "DRIFT: $f"; done
   diff -q docs/opencode-shell-strategy.md ~/.config/opencode/opencode-shell-strategy.md || echo "DRIFT: shell-strategy"
   diff -q system-prompt.md ~/.config/opencode/system-prompt.md || echo "DRIFT: system-prompt"
   for d in skill-templates/*/; do n=$(basename "$d"); diff -rq "$d" ~/.config/opencode/skills/"$n" >/dev/null 2>&1 || echo "DRIFT: opencode skill $n"; done
    # opencode.json: repo uses relative mcp-*-server/server.py for 5 local while global uses absolute /home/... — they will ALWAYS differ by design.
    diff -q opencode.json ~/.config/opencode/opencode.json && echo "UNEXPECTED: opencode.json identical (should differ relative vs absolute)" || echo "EXPECTED DRIFT: opencode.json relative vs absolute (check shape separately)"
    # tui.json parity (OpenCode 1 goal plugin): both repo tui.json and global ~/.config/opencode/tui.json must contain {"plugin":["@prevalentware/opencode-goal-plugin"]} — identical by design (no relative/absolute split)
    diff -q tui.json ~/.config/opencode/tui.json && echo "tui.json in sync ✓" || echo "DRIFT: tui.json"
    # goal plugin parity: both opencode.json + tui.json (global + project) must use @prevalentware/opencode-goal-plugin (not opencode-goal-plugin)
    grep -q "@prevalentware/opencode-goal-plugin" opencode.json && echo "project opencode.json plugin ✓" || echo "DRIFT: project opencode.json plugin"
    grep -q "@prevalentware/opencode-goal-plugin" ~/.config/opencode/opencode.json && echo "global opencode.json plugin ✓" || echo "DRIFT: global opencode.json plugin"
   ```
2. **Copy drifted files** with `cp` + `chmod +x` (only those that differ). Multi-module servers copy `*.py` (never `__pycache__/`). For `opencode.json` do NOT blind copy — regenerate global with absolute paths (see `LLM.txt:7` template):
   ```bash
   cp mcp-lint-server/server.py ~/.config/opencode/mcp-lint-server/server.py && chmod +x ~/.config/opencode/mcp-lint-server/server.py
   cp mcp-persona-server/*.py ~/.config/opencode/mcp-persona-server/ && chmod +x ~/.config/opencode/mcp-persona-server/server.py
   cp mcp-decision-server/*.py ~/.config/opencode/mcp-decision-server/ && chmod +x ~/.config/opencode/mcp-decision-server/server.py
   cp system-prompt.md ~/.config/opencode/system-prompt.md
   cp skill-templates/task-generator/SKILL.md ~/.config/opencode/skills/task-generator/SKILL.md
   # global opencode.json — regenerate with absolute $HOME for 7 MCPs (custom_context, project_memory, lint, persona, manager_decisions, blowsh docker, telegram uv --directory ...), do not cp repo's relative version
   # server launch form (Task 170): ["uv", "run", "--project", "<abs-server-dir>", "<abs-server-dir>/server.py"] — locked deps; keep pyproject/uv.lock in sync per server
   # credentials: persona + manager_decisions entries carry `environment: {VAR: "{env:VAR}"}` blocks (no secrets in JSON) — but {env:} resolves from opencode's OWN process env, so export .env before launching opencode (`set -a; source ~/.config/opencode/.env; set +a`); servers also self-load .env files as fallback
   ```
3. **Re-verify** with the same diff commands — expect no DRIFT output except the expected `opencode.json` relative vs absolute.
4. **Smoke-test** servers launch and run the full test suite:
   ```bash
   opencode mcp list  # should show ✓ connected for all 7: custom_context, project_memory, lint, persona, manager_decisions (+ blowsh, telegram)
   uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
   ```

## Telegram MCP Auto-Upgrade (upstream — chigwell/telegram-mcp — no fork)

The installed copy at `~/.config/opencode/mcp-telegram-server` is a git clone of **chigwell/telegram-mcp** upstream directly (no fork) per Manager directive 2026-09-08. Remotes: `origin` = https://github.com/chigwell/telegram-mcp.git. Upgrade = shallow clone from **upstream** to `/tmp` + rsync overlay, preserving local secrets/state. Run this as an additional step of every upgrade cycle (Step 2.5). Fork `mokhtarabadi/telegram-mcp` is no longer used — its `fix/allowed-root-automkdir-and-topic-filter` (commit c83a54e + PR #201 3c37edb) was merged upstream 2026-09-03, so upstream already contains the patch.

1. **Audit drift vs upstream:**
   ```bash
   rm -rf /tmp/opencode/telegram-mcp-upstream
   GIT_TERMINAL_PROMPT=0 git clone --depth 30 https://github.com/chigwell/telegram-mcp.git /tmp/opencode/telegram-mcp-upstream
   diff -rq --exclude=.git --exclude=.env --exclude='*.session' --exclude=downloads --exclude=.venv --exclude=__pycache__ --exclude='*.egg-info' --exclude=mcp_errors.log --exclude=claude_desktop_config.json \
     /tmp/opencode/telegram-mcp-upstream ~/.config/opencode/mcp-telegram-server
   ```
   To check lag: `git -C ~/.config/opencode/mcp-telegram-server fetch origin && git log --oneline HEAD..origin/main`
2. **Backup, then upgrade (via upstream):**
   ```bash
   cp -a ~/.config/opencode/mcp-telegram-server "/tmp/opencode/telegram-backup-$(date +%Y%m%d-%H%M%S)"
   rsync -a --exclude=.git --exclude=.env --exclude='*.session' --exclude=downloads --exclude=.venv --exclude=__pycache__ --exclude='*.egg-info' --exclude=mcp_errors.log --exclude=claude_desktop_config.json \
     /tmp/opencode/telegram-mcp-upstream/ ~/.config/opencode/mcp-telegram-server/
   cd ~/.config/opencode/mcp-telegram-server && uv sync
   ```
   **Fast-forward when upstream ahead:** `git -C ~/.config/opencode/mcp-telegram-server checkout main && git merge --ff-only origin/main` (or `git pull --ff-only`) then `uv sync`. No fork rebase/push needed.
3. **Verify:**
   ```bash
   cd ~/.config/opencode/mcp-telegram-server
   uv run python -c "import telegram_mcp; print('import ok')"
   mv .env .env.hold && uv run --with pytest pytest tests/ -q 2>&1 | tail -2; mv .env.hold .env
   ```
   ⚠️ **Tests FAIL (~26 failures) if `.env` is present** — ALWAYS hold `.env` aside during the test run.
4. **Smoke:** server startup requires valid sessions. `AuthKeyDuplicatedError` on ANY account blocks the whole MCP handshake. Fix = regenerate that session or remove its `TELEGRAM_SESSION_STRING_<LABEL>` from `.env`. Never `pip install telegram-mcp` / `uvx telegram-mcp` from PyPI (credential-theft lookalike).
5. **Startup failure triage:** reproduce with `timeout 45 uv --directory ~/.config/opencode/mcp-telegram-server run main.py /tmp/telegram-mcp ~/.config/opencode/mcp-telegram-server/downloads </dev/null >/tmp/opencode/tg-test.log 2>&1; echo $?` and read the log. **Lock-held exit (code 1, `Another telegram-mcp process is already connected`) is healthy** when the live opencode server holds the session — not an auth failure. `opencode mcp list` probe will timeout on telegram while the main instance holds the lock; core 4/5 connected is still a pass.

## Key Facts

- The `lint` MCP server gains new tools when updated (e.g. `lint_system_prompt_sync`) — check `grep -c "lint_system_prompt_sync" ~/.config/opencode/mcp-lint-server/server.py` after sync (≥1).
- Skills must be synced to `~/.config/opencode/skills/`.
- Agent ports: `.md` for OpenCode (`agents/`).
- `opencode.json` permission `bundle_tasks: allow` is required for the `bundle_tasks` MCP tool (added Task 110); persona/decision tool allows (`dispatch_session_turn`, `record_manager_decision`, …) since Tasks 167/168.
- **Project vs Global `opencode.json` (Option A 2026-08-25):** Repo `opencode.json` uses **relative** `mcp-*-server/server.py` for 5 local servers — `opencode mcp list` inside clone shows `✓ connected`; literal `$HOME/...` in repo's `command` breaks. Global `~/.config/opencode/opencode.json` must use **absolute** `$HOME/.config/opencode/...` for all 7. `blowsh`/`telegram` stay `enabled:false` in repo (require global install) vs `enabled:true` in global. `diff opencode.json` will always differ — verify shape, not identity.
  - **Update 2026-08-25 (Manager-approved):** repo now OMITS the `blowsh`/`telegram` blocks entirely so they inherit the working global definitions in-project.
  - **Update 2026-09-03:** Telegram MCP used fork `mokhtarabadi/telegram-mcp` (`fork` remote) — `main` = upstream chigwell `main` (7842b91) + `fix/allowed-root-automkdir-and-topic-filter` (c83a54e). Upstream sync via `fork` rebase. Installed tracked `fork/main`.
  - **Update 2026-09-05:** Telegram MCP fast-forwarded `3c37edb` → `7623e6b` (v3.2.31). Upstream PRs #206, #207, #210. PR #201 already in upstream — `merge --ff-only` + `push fork main`. Tests: 476 passed.
  - **Update 2026-09-08:** Per Manager directive, Telegram MCP switched from fork to **upstream chigwell/telegram-mcp directly** — `fork` remote removed (`git remote remove fork`), `origin` = https://github.com/chigwell/telegram-mcp.git only. Installed `main` now tracks `origin/main` at `c9460f8` (v3.2.32, PR #213 forward-routing). Fork patch already upstreamed (3c37edb ancestor of origin/main verified). Tests: 506 passed. No fork push needed.
  - **Update 2026-09-08 (Tasks 167/168):** persona + manager_decisions MCP servers installed globally (absolute paths, 600s timeouts since the slow-LLM fix); `manager-decision` skill synced (32 total); executor agent synced; project `.env` backed up to `~/.config/opencode/.env` (chmod 600). Decision store is per-project (`<project>/.opencode/decisions`, auto-created; global templates at `~/.config/opencode/.opencode/decisions/`).
  - **Update 2026-09-09 (plugin install lesson):** config references ≠ installed — goal + DCP plugins were listed in all 4 configs but absent from `~/.cache/opencode/packages/` (that's why `/dcp-compress` didn't exist). Installing = `opencode plugin <mod> -g`, verifying = `ls -d ~/.cache/opencode/packages/<scope>/<pkg>@latest`, slash commands appear only after restart. NEVER run `opencode plugin list` — the CLI treats `list` as a package name and installs junk (`list@latest` + fake `.opencode/opencode.json`); verify via config greps + cache listing instead.

Supersedes: workflows/global-install-upgrade (prior revision: 31 skills, 5 MCPs).