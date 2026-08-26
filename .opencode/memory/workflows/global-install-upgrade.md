---
created_at: '2026-08-25T19:15:30.411061+00:00'
status: active
tags: []
updated_at: '2026-08-25T19:15:30.411091+00:00'
---

# Global Install Upgrade Workflow (OpenCode + Freebuff)

Trigger phrase: **"load upgrade workflow memory and follow it"**

Updates the machine-global installations of the Cognitive Lead AI HQ (MCP servers, Skills, custom agents) for BOTH runtimes from the repo sources. The repo is the source of truth; the global dirs are machine-local copies.

> **⚠️ Freebuff RETIRED on this machine (2026-08-25, Manager directive "no need for a free buffer"):** the Manager deleted `~/.agents/` and `~/.AGENTS.md`. Future upgrade runs must SKIP every Freebuff sync step (skills ×2 mirror, `.ts` agent ports, `~/.AGENTS.md`, `~/.agents/mcp.json`) and upgrade OpenCode globals ONLY. The Freebuff rows below are kept for historical reference.

## Install Locations

| Component | OpenCode | Freebuff |
| --- | --- | --- |
| MCP servers | `~/.config/opencode/mcp-{context,memory,lint}-server/server.py` | `~/.agents/mcp.json` points AT the same global opencode paths (no separate copies needed) |
| Telegram MCP | `~/.config/opencode/mcp-telegram-server/` (upstream clone of chigwell/telegram-mcp; since 2026-08-25 20:41 a fresh git clone WITH `.git` at HEAD) | same dir via `~/.agents/mcp.json` (no separate copy) |
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
   # opencode.json: repo uses relative mcp-*-server/server.py for 3 core (so `opencode mcp list` shows ✓ connected inside clone) while global uses absolute /home/... — they will ALWAYS differ by design. Do NOT `cp opencode.json` blindly; instead audit the logical shape:
   diff -q opencode.json ~/.config/opencode/opencode.json && echo "UNEXPECTED: opencode.json identical (should differ relative vs absolute)" || echo "EXPECTED DRIFT: opencode.json relative vs absolute (check shape separately)"
    cat opencode.json | python3 -c "import json,sys; d=json.load(open('opencode.json')); assert d['mcp']['custom_context']['command']==['uv','run','mcp-context-server/server.py'], 'repo must use relative'"
    cat ~/.config/opencode/opencode.json | python3 -c "import json, os; home=os.path.expanduser('~'); d=json.load(open(home+'/.config/opencode/opencode.json')); assert home+'/.config/opencode/mcp-context-server/server.py' in str(d), 'global must use absolute'"
   ```
   (Freebuff-side diffs in step 1 will fail while Freebuff is retired — expected; skip them.)
2. **Copy drifted files** with `cp` + `chmod +x` (only those that differ). For `opencode.json` do NOT blind copy — regenerate global with absolute paths (see `LLM.txt:7` template):
   ```bash
   cp mcp-lint-server/server.py ~/.config/opencode/mcp-lint-server/server.py && chmod +x ~/.config/opencode/mcp-lint-server/server.py
   cp system-prompt.md ~/.config/opencode/system-prompt.md
   cp skill-templates/task-generator/SKILL.md ~/.config/opencode/skills/task-generator/SKILL.md
   # global opencode.json — regenerate with absolute $HOME for 5 MCPs (custom_context, project_memory, lint, blowsh docker, telegram uv --directory ...), do not cp repo's relative version
    python3 - <<'PY'
    import json, os, pathlib
    home = os.path.expanduser("~")
    cfg={"$schema":"https://opencode.ai/config.json","default_agent":"cognitive-executor","instructions":[f"{home}/.config/opencode/opencode-shell-strategy.md"],"plugin":["@prevalentware/opencode-goal-plugin"],"mcp":{"custom_context":{"type":"local","command":["uv","run",f"{home}/.config/opencode/mcp-context-server/server.py"],"enabled":True,"timeout":15000},"project_memory":{"type":"local","command":["uv","run",f"{home}/.config/opencode/mcp-memory-server/server.py"],"enabled":True,"timeout":15000},"lint":{"type":"local","command":["uv","run",f"{home}/.config/opencode/mcp-lint-server/server.py"],"enabled":True,"timeout":15000},"blowsh":{"type":"local","command":["docker","run","--rm","-i","ghcr.io/mokhtarabadi/blowsh-mcp:latest"],"enabled":True,"timeout":120000},"telegram":{"type":"local","command":["uv","--directory",f"{home}/.config/opencode/mcp-telegram-server","run","main.py","/tmp/telegram-mcp",f"{home}/.config/opencode/mcp-telegram-server/downloads"],"enabled":True,"timeout":15000}},"permission":{"custom_context_*":"allow","project_memory_*":"allow","lint_*":"allow","lint_markdown":"allow","lint_task_file":"allow","lint_all_tasks":"allow","store_memory":"allow","delete_memory":"ask","read_memory":"allow","search_memory":"allow","list_namespaces":"allow","get_directory_tree":"allow","read_source_files":"allow","bundle_tasks":"allow","blowsh_*":"allow","telegram_*":"allow","external_directory":{"*":"ask","/tmp/**":"allow"}}}
    pathlib.Path(f"{home}/.config/opencode/opencode.json").write_text(json.dumps(cfg,indent=2))
    PY
   ```
3. **Re-verify** with the same diff commands — expect no DRIFT output except the expected `opencode.json` relative vs absolute (verify shape with python asserts above).
4. **Smoke-test** servers launch and run the full test suite (52 passed expected):
   ```bash
   opencode mcp list  # should show ✓ connected for custom_context, project_memory, lint (project relative) and global absolute when outside repo
   uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
   ```

## Telegram MCP Auto-Upgrade (chigwell/telegram-mcp)

The installed copy at `~/.config/opencode/mcp-telegram-server` may or may not carry `.git` depending on how it was last installed (rsync overlay = NO `.git`; fresh clone = WITH `.git`). Either way: upgrade = shallow clone to `/tmp` + rsync overlay, preserving local secrets/state. Run this as an additional step of every upgrade cycle (Step 2.5).

1. **Audit drift vs upstream:**
   ```bash
   rm -rf /tmp/opencode/telegram-mcp-upstream
   GIT_TERMINAL_PROMPT=0 git clone --depth 30 https://github.com/chigwell/telegram-mcp.git /tmp/opencode/telegram-mcp-upstream
   diff -rq --exclude=.git --exclude=.env --exclude='*.session' --exclude=downloads --exclude=.venv --exclude=__pycache__ --exclude='*.egg-info' --exclude=mcp_errors.log --exclude=claude_desktop_config.json \
     /tmp/opencode/telegram-mcp-upstream ~/.config/opencode/mcp-telegram-server
   ```
   Any output = drift (upstream pyproject `version` can stay "2.0.1" across feature drift — judge by file diff, not version string).
2. **Backup, then upgrade:**
   ```bash
   cp -a ~/.config/opencode/mcp-telegram-server "/tmp/opencode/telegram-backup-$(date +%Y%m%d-%H%M%S)"
   rsync -a --exclude=.git --exclude=.env --exclude='*.session' --exclude=downloads --exclude=.venv --exclude=__pycache__ --exclude='*.egg-info' --exclude=mcp_errors.log --exclude=claude_desktop_config.json \
     /tmp/opencode/telegram-mcp-upstream/ ~/.config/opencode/mcp-telegram-server/
   cd ~/.config/opencode/mcp-telegram-server && uv sync
   ```
   Preserved local-only files: `.env` (credentials), `*.session`, `downloads/`, `claude_desktop_config.json`, `mcp_errors.log`. NEVER overwrite these from upstream.
3. **Verify:**
   ```bash
   cd ~/.config/opencode/mcp-telegram-server
   uv run python -c "import telegram_mcp; print('import ok')"
   mv .env .env.hold && uv run --with pytest pytest tests/ -q 2>&1 | tail -2; mv .env.hold .env
   ```
   ⚠️ **Tests FAIL (~26 failures) if `.env` is present** — the multi-account env leaks into test configuration. ALWAYS hold `.env` aside during the test run and restore immediately after. Expected result: all tests pass (335 passed on 2026-08-25).
4. **Smoke:** server startup requires valid sessions. `AuthKeyDuplicatedError` on ANY account blocks the whole MCP handshake (retry backoff before stdio loop starts → OpenCode shows spawn timeout). Fix = regenerate that session (`uv run session_string_generator.py --qr`) or remove its `TELEGRAM_SESSION_STRING_<LABEL>` from `.env`. Never `pip install telegram-mcp` / `uvx telegram-mcp` from PyPI (credential-theft lookalike — see `docs/telegram-setup.md` §8).
5. **Startup failure triage (learned 2026-08-25 evening):** reproduce with `timeout 45 uv --directory ~/.config/opencode/mcp-telegram-server run main.py /tmp/telegram-mcp ~/.config/opencode/mcp-telegram-server/downloads </dev/null >/tmp/opencode/tg-test.log 2>&1; echo $?` and read the log. Failure signatures:
   - `Telegram client '<label>' is not authorized` → that label's session string/file is dead; regenerate or remove it. NOTE: an unsuffixed legacy `TELEGRAM_SESSION_NAME` in `.env` silently creates a phantom `default` client backed by `telegram_session.session` — remove that variable if present (this was the 2026-08-25 outage root cause; it killed the whole server via `asyncio.gather` even though the other client was healthy).
   - `Another telegram-mcp process is already connected with this session (lock held: ...)` → NOT an error: a live instance already owns the session (singleton guard). Check `pgrep -af mcp-telegram-server`.
   - Server errors go to stderr, NOT `mcp_errors.log` (that file stays empty); OpenCode side shows `server unavailable key=telegram status=failed` in `~/.local/share/opencode/log/opencode.log`.

## Key Facts

- The `lint` MCP server gains new tools when updated (e.g. `lint_system_prompt_sync`) — check `grep -c "lint_system_prompt_sync" ~/.config/opencode/mcp-lint-server/server.py` after sync (≥1).
- Freebuff needs NO separate MCP server copies — `~/.agents/mcp.json` references `~/.config/opencode/mcp-*-server/server.py` by absolute path, so fixing opencode fixes freebuff. (Moot while Freebuff is retired — see top note.)
- Skills must be synced to BOTH `~/.config/opencode/skills/` AND `~/.agents/skills/`. (OpenCode-only while Freebuff is retired.)
- Agent ports: `.md` for OpenCode (`agents/`), `.ts` for Freebuff (`freebuff/agents/`).
- `opencode.json` permission `bundle_tasks: allow` is required for the `bundle_tasks` MCP tool (added Task 110).
- **Project vs Global `opencode.json` (Option A 2026-08-25):** Repo `opencode.json` uses **relative** `mcp-context-server/server.py` etc for 3 core — `opencode mcp list` inside clone shows `✓ connected`; literal `$HOME/...` in repo's `command` breaks (`uv run $HOME/...` → `No such file or directory`). Global `~/.config/opencode/opencode.json` must use **absolute** `$HOME/.config/opencode/...` (e.g., `/home/<user>/.config/opencode/...`) for all 5. `blowsh`/`telegram` stay `enabled:false` in repo (require global install) vs `enabled:true` in global. `diff opencode.json` will always differ — verify shape, not identity.
  - **Update 2026-08-25 (Manager-approved):** repo now OMITS the `blowsh`/`telegram` blocks entirely so they inherit the working global definitions in-project (verified: `opencode mcp list` inside repo lists 5 servers, blowsh ✓ connected). The old "disabled in repo" override is gone.
- Last run: 2026-08-25 evening re-verify — core audit zero drift (OpenCode side; Freebuff skipped per retirement note), `opencode.json` shapes OK, repo tests 52/52 passed. Telegram MCP installed copy == upstream HEAD `52cca20` (fresh git clone WITH `.git` made by another session at 20:41; workflow diff/rsync excludes `.git`, still valid). RESOLVED same evening: the morning's WORK `AUTH_KEY_DUPLICATED` was fixed by the Manager regenerating `.env`; the remaining startup crashes were caused by legacy unsuffixed `TELEGRAM_SESSION_NAME` creating an unauthorized phantom `default` client (see triage §5) — Manager removed it and added `TELEGRAM_SESSION_STRING_PERSONAL`; final state `.env` = API_ID/API_HASH + `_WORK` + `_PERSONAL`, server verified LIVE (singleton lock held by running instance; duplicate spawn correctly refuses).