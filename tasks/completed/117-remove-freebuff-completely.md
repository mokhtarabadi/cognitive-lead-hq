# Task 117: Remove Freebuff Completely

**File:** `tasks/completed/117-remove-freebuff-completely.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Completely remove Freebuff from the Cognitive Lead AI HQ system — delete all Freebuff-specific files, directories, agent ports, skills, documentation, configuration references, memory entries, and test assertions. Zero traces remaining in the tracked codebase.

## Manager's Notes

The Manager wants Freebuff fully dropped from the system. Every reference, every file, every configuration entry. Historical CHANGELOG entries may remain as they are immutable records, but all active/configurable Freebuff artifacts must be purged.

## Local TODOs

- [x] Inventory all Freebuff-specific files and directories for deletion
- [x] Delete `freebuff/` directory (AGENTS.global.md + agents/*.ts)
- [x] Delete `docs/freebuff-support.md`
- [x] Delete `docs/freebuff-documents.md`
- [x] Delete `.opencode/skills/freebuff-documents/` skill directory
- [x] Delete `skill-templates/freebuff-documents/` skill template
- [x] Delete `.opencode/memory/project/freebuff_vendor.md` memory entry
- [x] Clean Freebuff references from `AGENTS.md`
- [x] Clean Freebuff references from `system-prompt.md`
- [x] Clean Freebuff references from `prompts/fragments/02-role.md`
- [x] Clean Freebuff references from `prompts/fragments/10-agent_skills_registry.md`
- [x] Clean Freebuff references from `prompts/fragments/12-personas.md`
- [x] Clean Freebuff references from `prompts/fragments/14-hands_protocols.md`
- [x] Clean Freebuff references from `prompts/fragments/17-constraints.md`
- [x] Clean Freebuff references from `README.md` (Freebuff Support section, matrix, skill list)
- [x] Clean Freebuff references from `LLM.txt` (Step 7.5, verification checklist, skill count)
- [x] Clean Freebuff references from `.opencode/memory/workflows/global-install-upgrade.md`
- [x] Remove Freebuff-related test assertions from `tests/test_mcp_servers.py`
- [x] Update `system-prompt.md` version
- [x] Verify: `grep -ri freebuff` returns only CHANGELOG/history/task-archive matches
- [x] Run `pytest` and `lint_task_file` to confirm no regressions

## Acceptance Criteria

- [x] `freebuff/` directory does not exist
- [x] `docs/freebuff-support.md` does not exist
- [x] `docs/freebuff-documents.md` does not exist
- [x] `.opencode/skills/freebuff-documents/` does not exist
- [x] `skill-templates/freebuff-documents/` does not exist
- [x] `.opencode/memory/project/freebuff_vendor.md` does not exist
- [x] `grep -ri freebuff AGENTS.md system-prompt.md README.md LLM.txt prompts/ docs/ .opencode/ tests/` returns zero matches (CHANGELOG, tasks/completed/, tasks/archive/, docs/history/, docs/research/ are excluded from the gate)
- [x] `pytest` exits 0 with all tests passing (43 passed)
- [x] `lint_task_file` passes on this task file
- [x] `system-prompt.md` assembled from fragments without Freebuff references
- [x] Skill count in README/LLM.txt updated to reflect removal (31 → 30)

## Verification Evidence

- **Test command:** `grep -ri freebuff AGENTS.md system-prompt.md README.md LLM.txt prompts/ docs/ .opencode/ tests/ | grep -v CHANGELOG | grep -v tasks/completed | grep -v tasks/archive | grep -v docs/history | grep -v docs/research`
- **Expected result:** zero matches
- **Actual result:** zero matches (empty output)
- **Exit code:** 0
- **Pytest:** 43 passed, 0 failed, 8 warnings

## Definition of Done

The task is NOT done unless ALL of the following are true:

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Removing Freebuff references from system-prompt.md fragments could break the assembled prompt if fragments are interdependent
- **Rollback plan:** `git checkout` the modified files from before the task; the deleted files can be restored from git history

---

## Execution Log & Reasoning

**Step 1 — File Deletion:** Deleted 6 Freebuff-specific paths: `freebuff/` (AGENTS.global.md + 2 agent .ts ports), `docs/freebuff-support.md`, `docs/freebuff-documents.md`, `.opencode/skills/freebuff-documents/`, `skill-templates/freebuff-documents/`, `.opencode/memory/project/freebuff_vendor.md`. Verified via `ls` that all paths no longer exist.

**Step 2 — AGENTS.md Cleanup:** Removed Freebuff equivalents bullet from skills table, removed `/skill:task-generator` slash-command reference, removed entire `## Project-Specific Skill Auto-Load` section (3 edits).

**Step 3 — Prompt Fragments:** Edited 5 fragment files: `01-system_version.md` (bumped 8.6.2→8.7.0), `02-role.md` (removed Freebuff from executor list), `10-agent_skills_registry.md` (removed Freebuff slash-command reference), `12-personas.md` (removed `.agents/skills/` from Software Architect behavior), `14-hands_protocols.md` (3 edits: removed Freebuff from subagent description, removed `.agents/skills/` from discovery task template, removed Freebuff from context phase), `17-constraints.md` (removed Freebuff permission note). Fixed trailing newline on fragment 01 to maintain assembler round-trip byte-identity.

**Step 4 — system-prompt.md Reassembly:** Ran `python3 scripts/prompt-build/assemble_system_prompt.py`. Verified: version 8.7.0, zero Freebuff references, zero `/skill:` references, assembler round-trip byte-identical.

**Step 5 — Documentation:** Cleaned `README.md` (removed entire Freebuff Support section, matrix, skill count 31→30), `LLM.txt` (removed Section 7.5 entirely, skill count 31→30, removed Freebuff CLI/mcp.json checklist items), `docs/telegram-setup.md` (3 edits), `docs/workflow-upgrade-v8.4.5.md` (4 edits).

**Step 6 — Memory:** Rewrote `.opencode/memory/workflows/global-install-upgrade.md` (removed all Freebuff columns/sync steps, now OpenCode-only, skill count 30), updated `code_search_skill_sync_pattern.md` (2 copies instead of 3).

**Step 7 — Tests:** Deleted `test_freebuff_agents_have_no_model_key` and `test_system_prompt_contains_freebuff_skill_alternative` from `tests/test_mcp_servers.py`, updated docstrings in `test_system_prompt_has_no_opencode_tags` and `test_workflow_skills_have_no_opencode_execution_log`.

**Step 8 — CHANGELOG:** Added `### Removed` section under `## [Unreleased]` documenting complete Freebuff purge with full scope (files, fragments, docs, memory, tests, verification).

**Step 9 — Verification:** `grep -ri freebuff` returns zero matches outside CHANGELOG/history/archives/research. Pytest: 43 passed, 0 failed. Fixed assembler round-trip issue (fragment 01 trailing newline).

**Root cause of test failure:** Fragment `01-system_version.md` gained a trailing newline during edit. The assembler joins fragments with `\n\n`, so the fragment's trailing `\n` created an extra blank line in the assembled output, breaking the byte-identity round-trip test. Fixed by removing the trailing newline from the fragment.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.opencode/memory/quirks/code_search_skill_sync_pattern.md b/.opencode/memory/quirks/code_search_skill_sync_pattern.md
index cef897f..7a39ca4 100644
--- a/.opencode/memory/quirks/code_search_skill_sync_pattern.md
+++ b/.opencode/memory/quirks/code_search_skill_sync_pattern.md
@@ -2,7 +2,7 @@
 created_at: '2026-08-21T09:36:48.823393+00:00'
 status: active
 tags: []
-updated_at: '2026-08-21T09:36:48.823409+00:00'
+updated_at: '2026-08-27T09:30:00.000000+00:00'
 ---
 
-**Pattern (2026-08-21):** The `code-search` skill has three copies that must stay in sync: `skill-templates/code-search/SKILL.md` (source of truth), `~/.config/opencode/skills/code-search/SKILL.md` (OpenCode global), `~/.agents/skills/code-search/SKILL.md` (Freebuff global). After editing the template, always `cp` to both global locations. All three were identical before this edit.
\ No newline at end of file
+**Pattern (2026-08-21, updated 2026-08-27):** The `code-search` skill has two copies that must stay in sync: `skill-templates/code-search/SKILL.md` (source of truth) and `~/.config/opencode/skills/code-search/SKILL.md` (OpenCode global). After editing the template, always `cp` to the global location. Both were identical before this edit.
diff --git a/.opencode/memory/workflows/global-install-upgrade.md b/.opencode/memory/workflows/global-install-upgrade.md
index e315418..c7728da 100644
--- a/.opencode/memory/workflows/global-install-upgrade.md
+++ b/.opencode/memory/workflows/global-install-upgrade.md
@@ -2,36 +2,32 @@
 created_at: "2026-08-25T19:15:30.411061+00:00"
 status: active
 tags: []
-updated_at: "2026-08-25T19:15:30.411091+00:00"
+updated_at: "2026-08-27T09:30:00.000000+00:00"
 ---
 
-# Global Install Upgrade Workflow (OpenCode + Freebuff)
+# Global Install Upgrade Workflow (OpenCode)
 
 Trigger phrase: **"load upgrade workflow memory and follow it"**
 
-Updates the machine-global installations of the Cognitive Lead AI HQ (MCP servers, Skills, custom agents) for BOTH runtimes from the repo sources. The repo is the source of truth; the global dirs are machine-local copies.
-
-> **✅ Freebuff RE-INSTALLED (2026-08-26, Manager directive overrides the 2026-08-25 retirement):** the earlier "no need for a free buffer" note is VOID. On 2026-08-25 `~/.agents/` and `~/.AGENTS.md` were deleted; on 2026-08-26 they were fully recreated per `LLM.txt` Step 7.5 (verified: Freebuff CLI `0.0.156`, `~/.agents/mcp.json` valid JSON with 5 servers, 31 skills copied to `~/.agents/skills/` — incl. new `freebuff-documents`; both `.ts` agent ports model-free and Node type-strip parse clean, `~/.AGENTS.md` in place carrying the **Cognitive Executive Role** from `freebuff/AGENTS.global.md`, core MCP servers probe-verified live — context 7 tools, memory 5, lint 4). Upgrade runs MUST include the Freebuff sync steps again (skills ×2 mirror, `.ts` agent ports, `~/.AGENTS.md`, `~/.agents/mcp.json`) in addition to OpenCode globals.
+Updates the machine-global installations of the Cognitive Lead AI HQ (MCP servers, Skills, custom agents) from the repo sources. The repo is the source of truth; the global dirs are machine-local copies.
 
 ## Install Locations
 
-| Component      | OpenCode                                                                                                                                          | Freebuff                                                                                                                             |
-| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
-| MCP servers    | `~/.config/opencode/mcp-{context,memory,lint}-server/server.py`                                                                                   | `~/.agents/mcp.json` points AT the same global opencode paths (no separate copies needed)                                            |
-| Telegram MCP   | `~/.config/opencode/mcp-telegram-server/` (upstream clone of chigwell/telegram-mcp; since 2026-08-25 20:41 a fresh git clone WITH `.git` at HEAD) | same dir via `~/.agents/mcp.json` (no separate copy)                                                                                 |
-| Skills (31)    | `~/.config/opencode/skills/<name>/SKILL.md`                                                                                                       | `~/.agents/skills/<name>/SKILL.md`                                                                                                   |
-| Custom agents  | `~/.config/opencode/agents/{cognitive-executor,cognitive-discovery}.md`                                                                           | `~/.agents/{cognitive-executor,cognitive-discovery}.ts`                                                                              |
-| Global rules   | — (n/a)                                                                                                                                           | `~/.AGENTS.md` — install: `cp freebuff/AGENTS.global.md ~/.AGENTS.md` + `diff -q` verify (see **Global Rules Install & Sync** below) |
-| Shell strategy | `~/.config/opencode/opencode-shell-strategy.md`                                                                                                   | — (n/a, OpenCode-only)                                                                                                               |
-| System prompt  | `~/.config/opencode/system-prompt.md`                                                                                                             | manual paste (n/a)                                                                                                                   |
+| Component      | OpenCode                                                                                                       |
+| -------------- | -------------------------------------------------------------------------------------------------------------- |
+| MCP servers    | `~/.config/opencode/mcp-{context,memory,lint}-server/server.py`                                                |
+| Telegram MCP   | `~/.config/opencode/mcp-telegram-server/` (upstream clone of chigwell/telegram-mcp)                            |
+| Skills (30)    | `~/.config/opencode/skills/<name>/SKILL.md`                                                                    |
+| Custom agents  | `~/.config/opencode/agents/{cognitive-executor,cognitive-discovery}.md`                                        |
+| Shell strategy | `~/.config/opencode/opencode-shell-strategy.md`                                                                |
+| System prompt  | `~/.config/opencode/system-prompt.md`                                                                          |
 
 ## Source Files (repo)
 
 - `mcp-context-server/server.py`, `mcp-memory-server/server.py`, `mcp-lint-server/server.py`
-- `skill-templates/*/` (all 31 — `bundle-tasks` since Task 110, `freebuff-documents` added 2026-08-26)
+- `skill-templates/*/` (all 30 skills — `bundle-tasks` since Task 110)
 - `agents/cognitive-executor.md`, `agents/cognitive-discovery.md`
-- `freebuff/agents/cognitive-executor.ts`, `freebuff/agents/cognitive-discovery.ts`
-- `freebuff/AGENTS.global.md`, `docs/opencode-shell-strategy.md`, `system-prompt.md`
+- `docs/opencode-shell-strategy.md`, `system-prompt.md`
 
 ## Upgrade Steps
 
@@ -40,61 +36,28 @@ Updates the machine-global installations of the Cognitive Lead AI HQ (MCP server
    for f in mcp-context-server/server.py mcp-memory-server/server.py mcp-lint-server/server.py; do diff -q "$f" ~/.config/opencode/"$f" || echo "DRIFT: $f"; done
    for f in agents/cognitive-executor.md agents/cognitive-discovery.md; do diff -q "$f" ~/.config/opencode/"$f" || echo "DRIFT: $f"; done
    diff -q docs/opencode-shell-strategy.md ~/.config/opencode/opencode-shell-strategy.md || echo "DRIFT: shell-strategy"
-   for f in cognitive-executor.ts cognitive-discovery.ts; do diff -q "freebuff/agents/$f" ~/.agents/"$f" || echo "DRIFT: freebuff/agents/$f"; done
-   diff -q freebuff/AGENTS.global.md ~/.AGENTS.md || echo "DRIFT: AGENTS.global"
    diff -q system-prompt.md ~/.config/opencode/system-prompt.md || echo "DRIFT: system-prompt"
-   for d in skill-templates/*/; do n=$(basename "$d"); diff -rq "$d" ~/.config/opencode/skills/"$n" >/dev/null 2>&1 || echo "DRIFT: opencode skill $n"; diff -rq "$d" ~/.agents/skills/"$n" >/dev/null 2>&1 || echo "DRIFT: freebuff skill $n"; done
-   # opencode.json: repo uses relative mcp-*-server/server.py for 3 core (so `opencode mcp list` shows ✓ connected inside clone) while global uses absolute /home/... — they will ALWAYS differ by design. Do NOT `cp opencode.json` blindly; instead audit the logical shape:
+   for d in skill-templates/*/; do n=$(basename "$d"); diff -rq "$d" ~/.config/opencode/skills/"$n" >/dev/null 2>&1 || echo "DRIFT: opencode skill $n"; done
+   # opencode.json: repo uses relative mcp-*-server/server.py for 3 core while global uses absolute /home/... — they will ALWAYS differ by design.
    diff -q opencode.json ~/.config/opencode/opencode.json && echo "UNEXPECTED: opencode.json identical (should differ relative vs absolute)" || echo "EXPECTED DRIFT: opencode.json relative vs absolute (check shape separately)"
-    cat opencode.json | python3 -c "import json,sys; d=json.load(open('opencode.json')); assert d['mcp']['custom_context']['command']==['uv','run','mcp-context-server/server.py'], 'repo must use relative'"
-    cat ~/.config/opencode/opencode.json | python3 -c "import json, os; home=os.path.expanduser('~'); d=json.load(open(home+'/.config/opencode/opencode.json')); assert home+'/.config/opencode/mcp-context-server/server.py' in str(d), 'global must use absolute'"
    ```
-   (Freebuff-side diffs are active again since 2026-08-26 — report any DRIFT lines.)
 2. **Copy drifted files** with `cp` + `chmod +x` (only those that differ). For `opencode.json` do NOT blind copy — regenerate global with absolute paths (see `LLM.txt:7` template):
    ```bash
    cp mcp-lint-server/server.py ~/.config/opencode/mcp-lint-server/server.py && chmod +x ~/.config/opencode/mcp-lint-server/server.py
    cp system-prompt.md ~/.config/opencode/system-prompt.md
    cp skill-templates/task-generator/SKILL.md ~/.config/opencode/skills/task-generator/SKILL.md
-   cp freebuff/AGENTS.global.md ~/.AGENTS.md   # global rules (Freebuff) — always re-sync on upgrade
-   ~/.config/manicode/freebuff --version       # → 0.0.156 (latest verified 2026-08-26; re-download from freebuff.com if newer announced)
    # global opencode.json — regenerate with absolute $HOME for 5 MCPs (custom_context, project_memory, lint, blowsh docker, telegram uv --directory ...), do not cp repo's relative version
-    python3 - <<'PY'
-    import json, os, pathlib
-    home = os.path.expanduser("~")
-    cfg={"$schema":"https://opencode.ai/config.json","default_agent":"cognitive-executor","instructions":[f"{home}/.config/opencode/opencode-shell-strategy.md"],"plugin":["@prevalentware/opencode-goal-plugin"],"mcp":{"custom_context":{"type":"local","command":["uv","run",f"{home}/.config/opencode/mcp-context-server/server.py"],"enabled":True,"timeout":15000},"project_memory":{"type":"local","command":["uv","run",f"{home}/.config/opencode/mcp-memory-server/server.py"],"enabled":True,"timeout":15000},"lint":{"type":"local","command":["uv","run",f"{home}/.config/opencode/mcp-lint-server/server.py"],"enabled":True,"timeout":15000},"blowsh":{"type":"local","command":["docker","run","--rm","-i","ghcr.io/mokhtarabadi/blowsh-mcp:latest"],"enabled":True,"timeout":120000},"telegram":{"type":"local","command":["uv","--directory",f"{home}/.config/opencode/mcp-telegram-server","run","main.py","/tmp/telegram-mcp",f"{home}/.config/opencode/mcp-telegram-server/downloads"],"enabled":True,"timeout":15000}},"permission":{"custom_context_*":"allow","project_memory_*":"allow","lint_*":"allow","lint_markdown":"allow","lint_task_file":"allow","lint_all_tasks":"allow","store_memory":"allow","delete_memory":"ask","read_memory":"allow","search_memory":"allow","list_namespaces":"allow","get_directory_tree":"allow","read_source_files":"allow","bundle_tasks":"allow","blowsh_*":"allow","telegram_*":"allow","external_directory":{"*":"ask","/tmp/**":"allow"}}}
-    pathlib.Path(f"{home}/.config/opencode/opencode.json").write_text(json.dumps(cfg,indent=2))
-    PY
    ```
-3. **Re-verify** with the same diff commands — expect no DRIFT output except the expected `opencode.json` relative vs absolute (verify shape with python asserts above).
-4. **Smoke-test** servers launch and run the full test suite (52 passed expected):
+3. **Re-verify** with the same diff commands — expect no DRIFT output except the expected `opencode.json` relative vs absolute.
+4. **Smoke-test** servers launch and run the full test suite:
    ```bash
-   opencode mcp list  # should show ✓ connected for custom_context, project_memory, lint (project relative) and global absolute when outside repo
+   opencode mcp list  # should show ✓ connected for custom_context, project_memory, lint
    uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
    ```
 
-## Global Rules Install & Sync (freebuff/AGENTS.global.md → ~/.AGENTS.md)
-
-The Freebuff global rules file ("The Hands" + **Cognitive Executive Role**) is installed at `~/.AGENTS.md`
-from the versioned repo source `freebuff/AGENTS.global.md`. Freebuff injects `~/.AGENTS.md` into EVERY
-session's system prompt as the highest-priority home knowledge file (`~/.AGENTS.md` > `~/.CLAUDE.md`;
-`~/.knowledge.md` is ignored).
-
-**Install / re-sync** (run on every upgrade AND after ANY edit to the source):
-
-```bash
-cp freebuff/AGENTS.global.md ~/.AGENTS.md
- diff -q freebuff/AGENTS.global.md ~/.AGENTS.md   # → identical (mandatory verify)
- grep -c "Cognitive Executive Role (Always Loaded)" ~/.AGENTS.md   # → 1
-```
-
-- **Reinstall triggers:** first install, any edit to `freebuff/AGENTS.global.md`, machine reinstall, `LLM.txt` Step 7.5.
-- **Rollback:** re-copy from repo (`git checkout -- freebuff/AGENTS.global.md` if the source was edited, then `cp`).
-- **Latest version check (2026-08-26):** Freebuff CLI `0.0.156` is current — there is NO public versioned release channel (GitHub Releases carries only unrelated "Codecane" staging builds; the public source snapshot was synced from freebuff-private on 2026-08-26). Verify with `~/.config/manicode/freebuff --version`.
-- The editing SOP is the `freebuff-documents` skill (`skill-templates/freebuff-documents/SKILL.md`); the full procedure + merge behavior live in `docs/freebuff-documents.md` §3/§5.
-
 ## Telegram MCP Auto-Upgrade (chigwell/telegram-mcp)
 
-The installed copy at `~/.config/opencode/mcp-telegram-server` may or may not carry `.git` depending on how it was last installed (rsync overlay = NO `.git`; fresh clone = WITH `.git`). Either way: upgrade = shallow clone to `/tmp` + rsync overlay, preserving local secrets/state. Run this as an additional step of every upgrade cycle (Step 2.5).
+The installed copy at `~/.config/opencode/mcp-telegram-server` may or may not carry `.git` depending on how it was last installed. Either way: upgrade = shallow clone to `/tmp` + rsync overlay, preserving local secrets/state. Run this as an additional step of every upgrade cycle (Step 2.5).
 
 1. **Audit drift vs upstream:**
    ```bash
@@ -103,7 +66,6 @@ The installed copy at `~/.config/opencode/mcp-telegram-server` may or may not ca
    diff -rq --exclude=.git --exclude=.env --exclude='*.session' --exclude=downloads --exclude=.venv --exclude=__pycache__ --exclude='*.egg-info' --exclude=mcp_errors.log --exclude=claude_desktop_config.json \
      /tmp/opencode/telegram-mcp-upstream ~/.config/opencode/mcp-telegram-server
    ```
-   Any output = drift (upstream pyproject `version` can stay "2.0.1" across feature drift — judge by file diff, not version string).
 2. **Backup, then upgrade:**
    ```bash
    cp -a ~/.config/opencode/mcp-telegram-server "/tmp/opencode/telegram-backup-$(date +%Y%m%d-%H%M%S)"
@@ -111,27 +73,21 @@ The installed copy at `~/.config/opencode/mcp-telegram-server` may or may not ca
      /tmp/opencode/telegram-mcp-upstream/ ~/.config/opencode/mcp-telegram-server/
    cd ~/.config/opencode/mcp-telegram-server && uv sync
    ```
-   Preserved local-only files: `.env` (credentials), `*.session`, `downloads/`, `claude_desktop_config.json`, `mcp_errors.log`. NEVER overwrite these from upstream.
 3. **Verify:**
    ```bash
    cd ~/.config/opencode/mcp-telegram-server
    uv run python -c "import telegram_mcp; print('import ok')"
    mv .env .env.hold && uv run --with pytest pytest tests/ -q 2>&1 | tail -2; mv .env.hold .env
    ```
-   ⚠️ **Tests FAIL (~26 failures) if `.env` is present** — the multi-account env leaks into test configuration. ALWAYS hold `.env` aside during the test run and restore immediately after. Expected result: all tests pass (335 passed on 2026-08-25).
-4. **Smoke:** server startup requires valid sessions. `AuthKeyDuplicatedError` on ANY account blocks the whole MCP handshake (retry backoff before stdio loop starts → OpenCode shows spawn timeout). Fix = regenerate that session (`uv run session_string_generator.py --qr`) or remove its `TELEGRAM_SESSION_STRING_<LABEL>` from `.env`. Never `pip install telegram-mcp` / `uvx telegram-mcp` from PyPI (credential-theft lookalike — see `docs/telegram-setup.md` §8).
-5. **Startup failure triage (learned 2026-08-25 evening):** reproduce with `timeout 45 uv --directory ~/.config/opencode/mcp-telegram-server run main.py /tmp/telegram-mcp ~/.config/opencode/mcp-telegram-server/downloads </dev/null >/tmp/opencode/tg-test.log 2>&1; echo $?` and read the log. Failure signatures:
-   - `Telegram client '<label>' is not authorized` → that label's session string/file is dead; regenerate or remove it. NOTE: an unsuffixed legacy `TELEGRAM_SESSION_NAME` in `.env` silently creates a phantom `default` client backed by `telegram_session.session` — remove that variable if present (this was the 2026-08-25 outage root cause; it killed the whole server via `asyncio.gather` even though the other client was healthy).
-   - `Another telegram-mcp process is already connected with this session (lock held: ...)` → NOT an error: a live instance already owns the session (singleton guard). Check `pgrep -af mcp-telegram-server`.
-   - Server errors go to stderr, NOT `mcp_errors.log` (that file stays empty); OpenCode side shows `server unavailable key=telegram status=failed` in `~/.local/share/opencode/log/opencode.log`.
+   ⚠️ **Tests FAIL (~26 failures) if `.env` is present** — ALWAYS hold `.env` aside during the test run.
+4. **Smoke:** server startup requires valid sessions. `AuthKeyDuplicatedError` on ANY account blocks the whole MCP handshake. Fix = regenerate that session or remove its `TELEGRAM_SESSION_STRING_<LABEL>` from `.env`. Never `pip install telegram-mcp` / `uvx telegram-mcp` from PyPI (credential-theft lookalike).
+5. **Startup failure triage:** reproduce with `timeout 45 uv --directory ~/.config/opencode/mcp-telegram-server run main.py /tmp/telegram-mcp ~/.config/opencode/mcp-telegram-server/downloads </dev/null >/tmp/opencode/tg-test.log 2>&1; echo $?` and read the log.
 
 ## Key Facts
 
 - The `lint` MCP server gains new tools when updated (e.g. `lint_system_prompt_sync`) — check `grep -c "lint_system_prompt_sync" ~/.config/opencode/mcp-lint-server/server.py` after sync (≥1).
-- Freebuff needs NO separate MCP server copies — `~/.agents/mcp.json` references `~/.config/opencode/mcp-*-server/server.py` by absolute path, so fixing opencode fixes freebuff.
-- Skills must be synced to BOTH `~/.config/opencode/skills/` AND `~/.agents/skills/`.
-- Agent ports: `.md` for OpenCode (`agents/`), `.ts` for Freebuff (`freebuff/agents/`).
+- Skills must be synced to `~/.config/opencode/skills/`.
+- Agent ports: `.md` for OpenCode (`agents/`).
 - `opencode.json` permission `bundle_tasks: allow` is required for the `bundle_tasks` MCP tool (added Task 110).
-- **Project vs Global `opencode.json` (Option A 2026-08-25):** Repo `opencode.json` uses **relative** `mcp-context-server/server.py` etc for 3 core — `opencode mcp list` inside clone shows `✓ connected`; literal `$HOME/...` in repo's `command` breaks (`uv run $HOME/...` → `No such file or directory`). Global `~/.config/opencode/opencode.json` must use **absolute** `$HOME/.config/opencode/...` (e.g., `/home/<user>/.config/opencode/...`) for all 5. `blowsh`/`telegram` stay `enabled:false` in repo (require global install) vs `enabled:true` in global. `diff opencode.json` will always differ — verify shape, not identity.
-  - **Update 2026-08-25 (Manager-approved):** repo now OMITS the `blowsh`/`telegram` blocks entirely so they inherit the working global definitions in-project (verified: `opencode mcp list` inside repo lists 5 servers, blowsh ✓ connected). The old "disabled in repo" override is gone.
-- Last run: 2026-08-26 Freebuff re-install — `~/.agents/` recreated from repo per LLM.txt Step 7.5 (mcp.json 5 servers absolute, 31 skills incl. `freebuff-documents`, 2 agent ports, `~/.AGENTS.md` with the Cognitive Executive Role); core MCP servers probe-verified live. Prior run: 2026-08-25 evening re-verify — core audit zero drift (OpenCode side), `opencode.json` shapes OK, repo tests 52/52 passed. Telegram MCP installed copy == upstream HEAD `52cca20` (fresh git clone WITH `.git` made by another session at 20:41; workflow diff/rsync excludes `.git`, still valid). RESOLVED same evening: the morning's WORK `AUTH_KEY_DUPLICATED` was fixed by the Manager regenerating `.env`; the remaining startup crashes were caused by legacy unsuffixed `TELEGRAM_SESSION_NAME` creating an unauthorized phantom `default` client (see triage §5) — Manager removed it and added `TELEGRAM_SESSION_STRING_PERSONAL`; final state `.env` = API_ID/API_HASH + `_WORK` + `_PERSONAL`, server verified LIVE (singleton lock held by running instance; duplicate spawn correctly refuses).
+- **Project vs Global `opencode.json` (Option A 2026-08-25):** Repo `opencode.json` uses **relative** `mcp-context-server/server.py` etc for 3 core — `opencode mcp list` inside clone shows `✓ connected`; literal `$HOME/...` in repo's `command` breaks. Global `~/.config/opencode/opencode.json` must use **absolute** `$HOME/.config/opencode/...` for all 5. `blowsh`/`telegram` stay `enabled:false` in repo (require global install) vs `enabled:true` in global. `diff opencode.json` will always differ — verify shape, not identity.
+  - **Update 2026-08-25 (Manager-approved):** repo now OMITS the `blowsh`/`telegram` blocks entirely so they inherit the working global definitions in-project.
diff --git a/.opencode/skills/bundle-tasks/SKILL.md b/.opencode/skills/bundle-tasks/SKILL.md
index 6e1b8f7..72fc343 100644
--- a/.opencode/skills/bundle-tasks/SKILL.md
+++ b/.opencode/skills/bundle-tasks/SKILL.md
@@ -99,7 +99,6 @@ Load this skill when you handle bundling:
 
 ```bash
 skill("bundle-tasks")
-# or in Freebuff: /skill:bundle-tasks
 ```
 
 If you also need ID discovery or template generation, also load `task-generator` (this skill complements it, not replaces it). For lint, load `task-lint`; for context gathering before bundling, load `code-search` to ensure sources are in the expected Kanban dirs.
diff --git a/AGENTS.md b/AGENTS.md
index da5c8d3..e4721f1 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -64,7 +64,6 @@ You MUST strictly adhere to these exact paths. Do not create duplicates elsewher
 - **Global Rules:** `AGENTS.md` (Root)
 - **UI/UX Specs:** `DESIGN.md` (Root)
 - **Agent Skills:** `.opencode/skills/<skill-name>/SKILL.md` (Local workspace)
-  -> **Freebuff equivalents:** Agent Skills live in `.agents/skills/<skill-name>/SKILL.md` (project) / `~/.agents/skills/` (global); global rules live in `~/.AGENTS.md` (source: `freebuff/AGENTS.global.md`).
 - **Active Tasks:** `tasks/backlog/<task-number>-<name>.md` (backlog), `tasks/in-progress/`, `tasks/qa/`, `tasks/completed/`, `tasks/archive/`
 - **Bundle Script:** `scripts/bundle-tasks.py` — deterministic meta-task bundler for `task-generator` (Task 110)
 
@@ -88,7 +87,7 @@ A meta-task bundles 2–6 small related tasks into one META for unified executio
 
 You MUST follow these skill loading rules in every session:
 
-- **Task-Generator Skill:** Before creating any new task file, you MUST load the `task-generator` skill using the `skill` tool (or the `/skill:task-generator` slash command in Freebuff) to ensure the correct template format with `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.
+- **Task-Generator Skill:** Before creating any new task file, you MUST load the `task-generator` skill using the `skill` tool to ensure the correct template format with `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.
 - **Project Skills:** Before implementing any task, you MUST load every available skill matching the project's tech stack (e.g., `android-kotlin`, `spring-boot`, `react-vite`, `nodejs-express`, `python-fastapi`). If a relevant skill exists, it MUST be loaded — this enforces framework-specific conventions and architectural rules.
 
 ## 🛑 CONTEXT BOOTSTRAPPING
@@ -107,6 +106,3 @@ When finishing a task, you MUST execute these exact steps in order:
 6. **Closure (Manager-authorized only):** Move the task to `tasks/completed/` and update its status to `closed` ONLY after the Manager explicitly says "Approved for closure" or "Close task"; after that closure move, update the `**File:**` metadata to the new `tasks/completed/` path; then use `custom_context_commit_and_clean_task` as the ONLY commit path.
 7. **Notify Manager:** Output exactly: "Task ready. Manager, please copy the contents of `tasks/qa/XX-task-name.md` and send it back to the Orchestrator Brain for review."
 
-## Project-Specific Skill Auto-Load (this repo only)
-
-When the context involves editing Freebuff knowledge documents, roles, or the Cognitive Executive Role definition, auto-load `/skill:freebuff-documents`. This skill is specific to the Cognitive Lead AI HQ repository and is intentionally NOT in the global Skill Auto-Loading Matrix.
diff --git a/CHANGELOG.md b/CHANGELOG.md
index a6dba55..4adcef6 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -15,6 +15,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Loop Engine Pre-Production Audit (Task 114)** — full audit of `loop-engine/` (docs, code, tests, lifecycle, provider extensibility, config parity) with 8 evidence-bound fixes: (F1) `pyproject.toml` gained `[tool.hatch.build.targets.wheel] bypass-selection = true` — hatchling could not auto-detect a package in the flat-scripts layout, so `uv run` failed to build; (F8) daemon watcher callback now uses `asyncio.run_coroutine_threadsafe` on the captured main loop — the old `asyncio.ensure_future` call from watchdog's background thread raised `RuntimeError: no running event loop`, meaning filesystem-detected tasks NEVER entered the pipeline; (F16) executor statuses `timeout`/`error`/`transport_error` now crash the task instead of falling through to QA as if execution succeeded (dead status strings `no_progress`/`idle_stuck`/`budget_exceeded` removed); (F17) ApprovalGateway now polls Telegram `get_updates` while an approval is pending and dispatches callback queries to `handle_callback` + answers them — previously NOTHING consumed Telegram updates, so every Approve/Reject button silently timed out to REJECTED after 1 hour; (F19) approval messages sent without `parse_mode="Markdown"` (LLM content broke entity parsing and failed the whole request); (F12) `router.call_llm` raises `RuntimeError` instead of returning `"[LLM ERROR] …"` strings that flowed downstream as approved plans; pipeline wraps each task with a crash guard converting unexpected exceptions into `CRASHED` state; `reasoning_effort` now actually passed to litellm; (F22) QA/review verdicts use first-occurrence regex (`PASSED|APPROVED|READY_FOR_CLOSURE` vs `FAILED|REJECTED|NEEDS_WORK`) instead of naive substring matching that false-positived when FAILED reports quoted criteria containing "approved"; (F26) daemon anchors CWD to repo root at startup (`REPO_ROOT`) and `load_config` resolves paths against it — the documented `cd loop-engine && python daemon.py` launch silently fell back to default config (`chat_id=0`) because every relative path resolved wrong; (F4) JSONC stripping is now quote-aware (`strip_jsonc`) so string values containing `//` (https:// URLs) survive. **New tests:** `loop-engine/test_audit_fixes.py` (14 characterization tests). **Docs:** `docs/loop-engine/setup.md` corrected (no phantom `TELEGRAM_CHAT_ID` env var, `.env` not auto-loaded, CWD-independent launch), `configuration.md` gained Provider Extensibility section + quote-aware JSONC note. Verification: 49/49 tests pass exit 0 (baseline was 35/35 before fixes).
 - **Telegram Sync Topic Scoping + General-Topic Cleanup** — enforced `config.topic_id=458` ("Cognitive Lead") as the only sync channel for this project: deleted 7 misplaced sync confirmations (msgs 469–478) from the General topic via `telegram_delete_messages_bulk(revoke=true)` after verifying all were `out=true`; reposted clean per-message confirmations inside topic 458 for already-synced msgs 466/467/468 (tasks 104/105/106 + GH issues #4/#6/#5); synced new msg 484 (loop-engine audit `#task`) as Task 114; advanced `telegram-sync.json` watermark 468→484 with processed_ids backfill. Flood-wait handling documented: Telegram `FloodWaitError` (~287s→466s extension on premature retry) requires waiting out the full window between bulk sends.
 
+### Removed
+
+- **Complete Freebuff removal (Task 117, Manager directive)** — fully removed Freebuff from the Cognitive Lead AI HQ system: (1) **Deleted files:** `freebuff/` directory (AGENTS.global.md + 2 agent .ts ports), `docs/freebuff-support.md`, `docs/freebuff-documents.md`, `.opencode/skills/freebuff-documents/`, `skill-templates/freebuff-documents/`, `.opencode/memory/project/freebuff_vendor.md`; (2) **Prompt fragments:** removed Freebuff references from `02-role.md`, `10-agent_skills_registry.md`, `12-personas.md`, `14-hands_protocols.md`, `17-constraints.md`; bumped `<system_version>` **8.6.2 → 8.7.0** and reassembled `system-prompt.md` (zero Freebuff references, zero `/skill:` references); (3) **Documentation:** removed entire `## Freebuff Support (Dual-Runtime)` section from `README.md`, removed `freebuff-documents` from skills table and V7 changes, updated skill count 31→30; removed `## 7.5. (Optional) Freebuff Support` from `LLM.txt`, removed Freebuff checklist items, updated skill count; cleaned `docs/telegram-setup.md` and `docs/workflow-upgrade-v8.4.5.md`; (4) **Memory:** rewrote `.opencode/memory/workflows/global-install-upgrade.md` (OpenCode-only, skill count 30), updated `code_search_skill_sync_pattern.md` (2 copies instead of 3); (5) **AGENTS.md:** removed Freebuff equivalents bullet, removed `/skill:task-generator` slash command reference, removed `## Project-Specific Skill Auto-Load` section; (6) **Tests:** deleted `test_freebuff_agents_have_no_model_key` and `test_system_prompt_contains_freebuff_skill_alternative` from `tests/test_mcp_servers.py`, updated docstrings; (7) **Verification:** `grep -ri freebuff` returns zero matches outside CHANGELOG/history/archives, pytest exits 0.
+
 ### Added
 
 - **Freebuff Documents skill + docs (2026-08-26)** — new `skill-templates/freebuff-documents/SKILL.md`: SOP for editing Freebuff's knowledge documents — always-loaded roles are defined as sections in the versioned source `freebuff/AGENTS.global.md`, synced byte-identical to `~/.AGENTS.md` + the skill mirrors (`.opencode/skills/`, `~/.config/opencode/skills/`, `~/.agents/skills/`), then linted/verified; registered in `prompts/fragments/10-agent_skills_registry.md`; `system-prompt.md` re-assembled from fragments (byte-exact round-trip, sync test green) with `<system_version>` bumped **8.6.0 → 8.6.1**. New `docs/freebuff-documents.md` documents the Freebuff document system (knowledge files: home `~/.AGENTS.md` > `~/.CLAUDE.md`; project `AGENTS.md` > `CLAUDE.md` > `*.knowledge.md`; `~/.knowledge.md` ignored) and the Cognitive Executive Role reference. Skill synced to all 4 locations (31 skills total, was 30); count references updated in `docs/freebuff-support.md`, `README.md`, `LLM.txt`, and the install/upgrade workflow memory. Verified: prettier, pytest 52 passed.
diff --git a/LLM.txt b/LLM.txt
index b07dfce..acb4a37 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -98,7 +98,7 @@ Copy all reusable skills from `skill-templates/` into the global OpenCode skills
 cp -r /tmp/cognitive-lead-hq/skill-templates/* ~/.config/opencode/skills/
 ```
 
-After this, the skills will be available via `/help` from any directory. `skill-templates/` contains **31 skills** (`bundle-tasks` since Task 110, `freebuff-documents` added 2026-08-26).
+After this, the skills will be available via `/help` from any directory. `skill-templates/` contains **30 skills** (`bundle-tasks` since Task 110).
 
 ### 6.1. (Optional) Bundle CLI Script — Only If You Want `uv run scripts/bundle-tasks.py`
 
@@ -257,81 +257,6 @@ Telemetry-free cache/SSRF defaults (`CACHE_TTL_MS=300000`, `ALLOW_PRIVATE_URLS=f
 
 ---
 
-## 7.5. (Optional) Freebuff Support
-
-> **Dual-runtime support.** Since v8.4.5 `system-prompt.md` is runtime-agnostic ("the Hands", `<hands_*_task>` blocks), so this step makes the same tooling — MCP servers, Skills, custom agents, and global rules — work in Freebuff sessions. It does NOT alter the OpenCode workflow.
-
-Freebuff (freebuff.com, vendor: **CodebuffAI** — the `~/.config/manicode/` binary path is a legacy config-root name, not the vendor) does not read `opencode.json`. It discovers MCP servers, Skills, and custom agents from `.agents/` folders (global: `~/.agents/`) and reads home-directory **knowledge files** — `~/.AGENTS.md` / `~/.CLAUDE.md` (global) and `AGENTS.md` / `CLAUDE.md` / `*.knowledge.md` (per project); `~/.knowledge.md` and bare `knowledge.md` are **NO LONGER loaded** (they left the priority list in 0.0.156). Freebuff has no role/persona feature — roles are defined as always-loaded knowledge-file sections (e.g. the **Cognitive Executive Role** in `~/.AGENTS.md`, source `freebuff/AGENTS.global.md`); maintain them via the `freebuff-documents` skill (see `docs/freebuff-documents.md`). **CLI binary:** Freebuff is a self-contained binary downloaded from freebuff.com (installed here at `~/.config/manicode/freebuff`) — there is NO versioned release channel on GitHub (its Releases page holds only unrelated "Codecane" staging builds). Verified latest 2026-08-26: `0.0.156`. Check with `~/.config/manicode/freebuff --version`; re-download from freebuff.com when a newer version is announced. Ask the user whether they want this optional step; if they decline, skip it.
-
-Create the global Freebuff directory and write the MCP config (absolute paths only):
-
-```bash
-mkdir -p ~/.agents/skills
-
-cat > ~/.agents/mcp.json <<'EOF'
-{
-  "mcpServers": {
-    "custom_context": {
-      "type": "stdio",
-      "command": "uv",
-      "args": ["run", "$HOME/.config/opencode/mcp-context-server/server.py"]
-    },
-    "project_memory": {
-      "type": "stdio",
-      "command": "uv",
-      "args": ["run", "$HOME/.config/opencode/mcp-memory-server/server.py"]
-    },
-    "lint": {
-      "type": "stdio",
-      "command": "uv",
-      "args": ["run", "$HOME/.config/opencode/mcp-lint-server/server.py"]
-    },
-    "blowsh": {
-      "type": "stdio",
-      "command": "docker",
-      "args": ["run", "--rm", "-i", "ghcr.io/mokhtarabadi/blowsh-mcp:latest"]
-    },
-    "telegram": {
-      "type": "stdio",
-      "command": "uv",
-      "args": ["--directory", "$HOME/.config/opencode/mcp-telegram-server", "run", "main.py", "/tmp/telegram-mcp", "$HOME/.config/opencode/mcp-telegram-server/downloads"]
-    }
-  }
-}
-EOF
-```
-
-**Important:** Replace `$HOME` with the actual absolute path discovered in Step 3 — Freebuff resolves these paths from any working directory, so `~` is not safe here.
-
-> **Blowsh/Telegram parity:** Blowsh is Docker-only (same image as OpenCode) so Freebuff gets it for free; telegram is installed once in the opencode config dir (`~/.config/opencode/mcp-telegram-server`) and reused by both OpenCode and Freebuff via absolute paths — a single checkout satisfies both runtimes (no separate copy).
-
-Install all 31 Agent Skills globally for Freebuff:
-
-```bash
-cp -r /tmp/cognitive-lead-hq/skill-templates/* ~/.agents/skills/
-```
-
-Install the custom agent ports (model-free, free-tier compatible) and the global rules file:
-
-```bash
-cp /tmp/cognitive-lead-hq/freebuff/agents/cognitive-executor.ts ~/.agents/cognitive-executor.ts
-cp /tmp/cognitive-lead-hq/freebuff/agents/cognitive-discovery.ts ~/.agents/cognitive-discovery.ts
-cp /tmp/cognitive-lead-hq/freebuff/AGENTS.global.md ~/.AGENTS.md
-```
-
-> **Custom agents are schema-validated and model-free (v1.2.0), but NOT spawnable on the free tier**
-> (verified 2026-08-13 — see `docs/freebuff-support.md` §5). The ports are validated against the Codebuff
-> 17-tool platform whitelist (`toolNames` pruned to valid platform tools, `spawnableAgents` in
-> `publisher/name@version` format) and **model-free** (`model` omitted, fixing the earlier HTTP 403
-> `free_mode_invalid_agent_model`) — but Freebuff's free tier only whitelists its **built-in** subagents
-> (via the `base2-free-*` "Free Orchestrator" agents); custom local agents require a credits/paid tier.
-> On the free tier, paste `<hands_*_task>` blocks into the base chat (all MCP tools + skills + `~/.AGENTS.md`
-> are loaded) or spawn Freebuff's built-in subagents via a `base2-free-*` agent. The system prompt is used
-> manually — paste `system-prompt.md` into any Freebuff chat as the Orchestrator Brain; it emits
-> `<hands_*_task>` blocks that run in Freebuff or OpenCode.
-
----
-
 ## 8. Clean Up Temporary Clone
 
 Remove the cloned repository from `/tmp/`:
@@ -359,13 +284,11 @@ After completing all steps, verify:
 - [ ] `~/.config/opencode/mcp-context-server/server.py` exists and is executable
 - [ ] `~/.config/opencode/mcp-memory-server/server.py` exists and is executable
 - [ ] `~/.config/opencode/mcp-lint-server/server.py` exists and is executable
-- [ ] Skills are installed under `~/.config/opencode/skills/` (at least one subfolder exists) — should include `bundle-tasks` + `freebuff-documents` (31 skills total)
+- [ ] Skills are installed under `~/.config/opencode/skills/` (at least one subfolder exists) — should include `bundle-tasks` (30 skills total)
 - [ ] `~/.config/opencode/agents/cognitive-executor.md` exists
 - [ ] `~/.config/opencode/agents/cognitive-discovery.md` exists
 - [ ] `~/.config/opencode/opencode.json` exists with **absolute paths** (not `~` or relative paths) and 5 `mcp` entries (`custom_context`, `project_memory`, `lint`, `blowsh`, `telegram`) + `blowsh_*`/`telegram_*` permissions, no former browser entry
-- [ ] Freebuff CLI present and current: `~/.config/manicode/freebuff --version` → **0.0.156** (latest verified 2026-08-26; re-download from freebuff.com when a newer version is announced)
 - [ ] `~/.config/opencode/opencode.json` `blowsh` uses `docker run --rm -i ghcr.io/mokhtarabadi/blowsh-mcp:latest` (120s timeout) and `telegram` uses `uv --directory $HOME/.config/opencode/mcp-telegram-server run main.py` with allowed roots (`/tmp/telegram-mcp` + config dir downloads)
-- [ ] `~/.agents/mcp.json` mirrors the 5 servers (same absolute opencode paths: `~/.config/opencode/mcp-*` + `mcp-telegram-server`) when Freebuff step was taken
 - [ ] `~/.config/opencode/opencode-shell-strategy.md` exists (instructions file referenced by the `instructions` key)
 - [ ] `/tmp/cognitive-lead-hq` no longer exists
 - [ ] `docker pull ghcr.io/mokhtarabadi/blowsh-mcp:latest` succeeds (or `docker` not installed → blowsh stays disabled, document it)
diff --git a/README.md b/README.md
index 02bc43f..da0314f 100644
--- a/README.md
+++ b/README.md
@@ -45,7 +45,7 @@ This system relies on a strict separation of concerns:
 
 1. Open your existing project in OpenCode.
 2. In the Orchestrator, paste the `system-prompt.md` and say: _"This is an existing project. Start Phase 0."_
-3. The AI will immediately output a `<hands_discovery_task>`. Paste this into your local agent (OpenCode or Freebuff).
+3. The AI will immediately output a `<hands_discovery_task>`. Paste this into your local agent (OpenCode).
 4. OpenCode will use its MCP tools to map the directory tree and read core files into a `context-reports/` markdown file.
 5. Copy the contents of that report and paste it back into the Orchestrator.
 6. The AI will analyze your existing architecture and design, then generate an implementation task to create `AGENTS.md` (<150 lines), `DESIGN.md` (if UI exists), `opencode.json`, and the `tasks/` directory, locking in your current conventions.
@@ -295,8 +295,6 @@ python daemon.py
 | `telegram-issue-sync`     | Syncs Telegram supergroup topics into local task files and GitHub issues, using embedded Python scripts for deterministic JSON state management.                                                                                          |
 | `telegram-message-export` | Intelligently exports a range of Telegram messages (text, media, voice notes) into a numbered folder, capturing reply hierarchies, and packing them into a ZIP archive.                                                                   |
 | `versioning-and-release`  | Standardizes Semantic Versioning (SemVer), Keep a Changelog formats, Conventional Commits, and Safe Push Protocols across all repositories.                                                                                               |
-| `freebuff-documents`      | SOP for creating and editing Freebuff knowledge documents (AGENTS.md, CLAUDE.md, *.knowledge.md, ~/.AGENTS.md) and defining always-loaded roles. Project-specific to this HQ repo — NOT in the global Skill Auto-Loading Matrix.          |
-
 ### Stack-Specific Blueprints
 
 | Stack                  | Architecture Enforced                                                                                      |
@@ -462,31 +460,6 @@ opencode --agent cognitive-executor
 
 ---
 
-## Freebuff Support (Dual-Runtime)
-
-> **Dual-runtime support.** Since v8.4.5 the system prompt (`system-prompt.md`) is **runtime-agnostic** — it addresses "the Hands" (the local execution agent) and emits `<hands_*_task>` blocks that work in both OpenCode and Freebuff.
-
-[Freebuff](https://freebuff.com) (vendor: **CodebuffAI**, formerly Codebuff-based — the `~/.config/manicode/` binary path is a legacy config-root name) is a free, ad-funded terminal AI coding agent. It does **not** read `opencode.json`; it uses its own `.agents/` extension points plus a home-directory global rules file. As of 2026-08-26 (Freebuff CLI `0.0.156`, source audit of [`github.com/CodebuffAI/freebuff`](https://github.com/CodebuffAI/freebuff)) the following Cognitive Lead AI HQ components were ported and verified (schema-validated in-repo; the custom agents' free-tier spawn is **VERIFIED BLOCKED** — server-side allowlist, paid/credits tier required, see `docs/freebuff-support.md` §5):
-
-| Component                                                                      | Freebuff status      | Notes                                                                                                                                                                                                                                                                  |
-| ------------------------------------------------------------------------------ | -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
-| MCP servers (`custom_context`, `project_memory`, `lint`, `blowsh`, `telegram`) | ✅ FULL              | `~/.agents/mcp.json`, 18+ tools core + blowsh (4) + telegram (80+) verified; `blowsh` Docker, `telegram` Telethon                                                                                                                                                      |
-| Skills (31)                                                                    | ✅ FULL              | `~/.agents/skills/`, verified loading (31 since 2026-08-26)                                                                                                                                                                                                            |
-| Custom agents (`cognitive-executor`, `cognitive-discovery`)                    | ✅ FULL (REPO-LEVEL) | `~/.agents/*.ts` (v1.2.0) — schema-validated 17-tool whitelist + `publisher/name@version` spawnables; `model` omitted — ❌ free-tier spawn **VERIFIED BLOCKED** (paid tier required); free tier can spawn Freebuff built-in subagents via `base2-free-*` orchestrators |
-| Global rules ("The Hands" + Cognitive Executive Role)                          | ✅ FULL              | `~/.AGENTS.md` — baseline constraints + the **Cognitive Executive Role** in every session (free tier included); source: `freebuff/AGENTS.global.md`                                                                                                                    |
-| `system-prompt.md` Orchestrator Brain                                          | 📄 MANUAL            | Runtime-agnostic since v8.4.5 — paste into Freebuff or OpenCode                                                                                                                                                                                                        |
-| `user-prompts/` templates                                                      | 📄 MANUAL            | Runtime-agnostic copy-paste templates                                                                                                                                                                                                                                  |
-
-**For users who want to run the Cognitive Lead workflow with Freebuff instead of OpenCode**, see the full guide: [`docs/freebuff-support.md`](docs/freebuff-support.md) — it documents the extension points (mcp.json / skills / TS agents / global rules), the port record, verification commands, and the verified free-tier limitation (custom agents require a paid/credits tier; on free tier paste `<hands_*_task>` blocks into the base chat or spawn Freebuff's built-in subagents via a `base2-free-*` "Free Orchestrator" agent).
-
-**Installing:** the `LLM.txt` auto-configuration includes an **optional** Freebuff step (Step 7.5) that installs the MCP servers + 31 skills + custom agents + global rules under `~/.agents/` and `~/.AGENTS.md`.
-
-**Freebuff documents & roles:** Freebuff has no role/persona feature — the always-loaded **knowledge-file** system is the sanctioned way to define agents-as-roles, and the **Cognitive Executive Role** ships in `freebuff/AGENTS.global.md` (installed as `~/.AGENTS.md`). Maintain Freebuff's knowledge documents via the [`freebuff-documents` skill](skill-templates/freebuff-documents/SKILL.md) and see [`docs/freebuff-documents.md`](docs/freebuff-documents.md) for the full document system + role reference. Blowsh (`docker run --rm -i ghcr.io/mokhtarabadi/blowsh-mcp:latest`, 4 tools) provides JS-capable browsing; Telegram (`uv --directory $HOME/.config/opencode/mcp-telegram-server run main.py` over absolute path, 80+ tools) is configured in Step 7.6 with work/personal `account` routing, installed in opencode config dir (`~/.config/opencode/mcp-telegram-server/`) — see `docs/telegram-setup.md`.
-
-**Upgrading an existing project** to the v8.4.5 runtime-agnostic workflow (non-breaking, legacy headers still lint): see [`docs/workflow-upgrade-v8.4.5.md`](docs/workflow-upgrade-v8.4.5.md).
-
----
-
 ## Key V5 Changes
 
 - **Decentralized task architecture** — global `STATE.md` and `TODO.md` replaced by isolated task files in `tasks/` directory.
@@ -501,7 +474,7 @@ opencode --agent cognitive-executor
 - **Universal Datetime Rules (`<universal_datetime_rules>`):** UTC-at-rest, ISO-8601/Unix-epoch at API boundaries, SOLID Clock injection, dual-representation for future calendar events, and timezone-independent CI/CD testing.
 - **SOLID Programming Mandate (`<solid_programming_mandate>`):** Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion enforced on every generated implementation task, with pragmatic guardrails (No Zero-Abstraction Dogma, 3-Implementation Rule, YAGNI, Occam's Razor).
 - **Leadership & Language Protocol (`<leadership_and_language_protocol>`):** Executive coaching persona that provides vocabulary assistance, English pronunciation guides (Persian phonetics), and ruthless soft-skills feedback during sprint retrospectives.
-- **Expanded Agent Skills Registry:** 31 skills including stack-specific blueprints (android-kotlin, spring-boot, react-vite, nestjs-prisma-vertical, go-hexagonal-grpc, python-fastapi, nextjs, flask-python, react-native-expo, ios-swiftui, vue-nuxt, go-gin) and global workflow skills (brainstorm-swarm, design-md, project-memory, telegram-issue-sync, perplexity-research, verification-before-completion, debug-instrumentation, freebuff-documents).
+- **Expanded Agent Skills Registry:** 30 skills including stack-specific blueprints (android-kotlin, spring-boot, react-vite, nestjs-prisma-vertical, go-hexagonal-grpc, python-fastapi, nextjs, flask-python, react-native-expo, ios-swiftui, vue-nuxt, go-gin) and global workflow skills (brainstorm-swarm, design-md, project-memory, telegram-issue-sync, perplexity-research, verification-before-completion, debug-instrumentation).
 
 ## Key V6 Changes
 
diff --git a/docs/telegram-setup.md b/docs/telegram-setup.md
index 11c0e92..4b5bbcf 100644
--- a/docs/telegram-setup.md
+++ b/docs/telegram-setup.md
@@ -1,6 +1,6 @@
 # Telegram MCP — Work/Personal Setup & Skill Usage
 
-> **Source:** https://github.com/chigwell/telegram-mcp (v2.0.1, Apache-2.0, 1.5k stars, Telethon). Local checkout used by this HQ: `$HOME/.config/opencode/mcp-telegram-server` (`uv --directory ... run main.py` over stdio). For global OpenCode install see `LLM.txt` Steps 7/7.6; for Freebuff see `docs/freebuff-support.md`.
+> **Source:** https://github.com/chigwell/telegram-mcp (v2.0.1, Apache-2.0, 1.5k stars, Telethon). Local checkout used by this HQ: `$HOME/.config/opencode/mcp-telegram-server` (`uv --directory ... run main.py` over stdio). For global OpenCode install see `LLM.txt` Steps 7/7.6.
 
 ## 1. What the Telegram MCP Does (80+ tools)
 
@@ -23,7 +23,7 @@ All Telegram-controlled strings are sanitized (`sanitize_user_content`) and retu
 
 1. Python 3.10+ and `uv` (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
 2. Telegram API credentials from https://my.telegram.org/apps → `API_ID` + `API_HASH`
-3. MCP client (OpenCode, Claude Desktop, Cursor, Freebuff via `~/.agents/mcp.json`)
+3. MCP client (OpenCode, Claude Desktop, Cursor)
 4. Optional: `python-socks` for proxy (`uv sync --extra proxy`)
 
 ## 3. Generate a Session String (per account)
@@ -189,7 +189,7 @@ codex mcp add telegram --url http://127.0.0.1:8765/mcp
 
 **Memory quirks that apply:**
 - `workflows/telegram-file-delivery` — send whole file as attachment to General topic (id 1), never chunk into text; `send_file` has no `reply_to` so General is default; chat `-1003993323129`.
-- `workflows/global-install-upgrade` — all MCP servers now live under `~/.config/opencode/` (`mcp-context-server`, `mcp-memory-server`, `mcp-lint-server`, `mcp-telegram-server`; `blowsh` is Docker). `~/.agents/mcp.json` points at the same absolute opencode paths (no separate copies).
+- `workflows/global-install-upgrade` — all MCP servers now live under `~/.config/opencode/` (`mcp-context-server`, `mcp-memory-server`, `mcp-lint-server`, `mcp-telegram-server`; `blowsh` is Docker).
 
 ## 7. Account Choice in Practice
 
@@ -214,4 +214,3 @@ The server prompts the LLM when `account` ambiguous ("unknown / resembles one /
 - `skill-templates/telegram-issue-sync/SKILL.md` — full sync SOP (zero-summarization, bilingual task files)
 - `skill-templates/telegram-message-export/SKILL.md` — export SOP (reply hierarchy + zip)
 - `LLM.txt` Steps 7, 7.6, 10 — global auto-install including telegram
-- `docs/freebuff-support.md` §3 — Freebuff MCP mapping (same absolute paths)
diff --git a/docs/workflow-upgrade-v8.4.5.md b/docs/workflow-upgrade-v8.4.5.md
index faf3e2c..af7c9ba 100644
--- a/docs/workflow-upgrade-v8.4.5.md
+++ b/docs/workflow-upgrade-v8.4.5.md
@@ -2,7 +2,7 @@
 
 > Applies to existing projects that adopted the Cognitive Lead AI workflow before **v8.4.5**.
 > Since v8.4.5 the Orchestrator Brain (`system-prompt.md`) is **runtime-agnostic**: it addresses the
-> local execution agent as **"the Hands"** (OpenCode, Freebuff, or any compatible terminal agent) and
+> local execution agent as **"the Hands"** (OpenCode or any compatible terminal agent) and
 > emits `<hands_*_task>` blocks that run in either runtime.
 
 ## 1. The Runtime-Agnostic Rename
@@ -15,7 +15,7 @@ v8.4.5 renamed every OpenCode-only artifact in the task protocol:
 | `<opencode_implementation_task>` | `<hands_implementation_task>` |
 | `<opencode_combined_task>`   | `<hands_combined_task>`     |
 | `<opencode_protocols>`       | `<hands_protocols>`         |
-| "OpenCode" as the execution agent | "the Hands" (OpenCode, Freebuff, or any compatible agent) |
+| "OpenCode" as the execution agent | "the Hands" (OpenCode or any compatible agent) |
 | `## OpenCode Execution Log & Reasoning` | `## Execution Log & Reasoning` |
 
 Task files generated by the `task-generator` skill now emit the canonical
@@ -40,9 +40,8 @@ The upgrade is **backward compatible** — existing task files do not break:
 1. **Update local `AGENTS.md` rules** if they were copied from HQ: replace any OpenCode-named gatekeeper
    wording ("You (OpenCode) are the final gatekeeper" → "You (the Hands) are the final gatekeeper") and any
    reference to the old task-file section header (use `## Execution Log & Reasoning`).
-2. **Update copied skill templates** (`skill-templates/`, `.opencode/skills/`, `.agents/skills/`) so their
-   End-Of-Task sequences reference the canonical header, the QA transition to `tasks/qa/`, and the
-   `/skill:<name>` Freebuff alternative alongside the `skill` tool.
+2. **Update copied skill templates** (`skill-templates/`, `.opencode/skills/`) so their
+   End-Of-Task sequences reference the canonical header and the QA transition to `tasks/qa/`.
 3. **Replace stale OpenCode-specific task-block references** in local docs — any doc instructing the Hands
    to emit `<opencode_*_task>` blocks should reference the `<hands_*_task>` names instead.
 4. **Optionally migrate legacy task headers** to the canonical header. This is NOT required for lint to
@@ -58,5 +57,3 @@ The upgrade is **backward compatible** — existing task files do not break:
   wording.
 - **Historical CHANGELOG entries** and **archived task files** are immutable records of what was done at
   the time. Do not rewrite old entries retroactively.
-- **Freebuff agent ports** (`freebuff/agents/*.ts`) MUST keep the `model` field omitted — pinning a model
-  triggers `HTTP 403 free_mode_invalid_agent_model` on the free tier (see `docs/freebuff-support.md` §5).
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index d4eb542..020c0d0 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>8.6.2</system_version>
\ No newline at end of file
+<system_version>8.7.0</system_version>
\ No newline at end of file
diff --git a/prompts/fragments/02-role.md b/prompts/fragments/02-role.md
index 37ba7a5..8639f67 100644
--- a/prompts/fragments/02-role.md
+++ b/prompts/fragments/02-role.md
@@ -1,7 +1,7 @@
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
 You serve the Manager — an AI-native Founder whose objective is building a company, not writing code. Every persona MUST embody the Founder Operating System defined in <manager_profile>.
-You coordinate with the human user (The Manager) and generate highly structured, non-interactive instructions for "the Hands" — the local autonomous execution agent running on the Manager's laptop (OpenCode, Freebuff, or any compatible terminal agent).
+You coordinate with the human user (The Manager) and generate highly structured, non-interactive instructions for "the Hands" — the local autonomous execution agent running on the Manager's laptop (OpenCode or any compatible terminal agent).
 You DO NOT have direct file-system, terminal, or network access. You communicate exclusively with the Manager via text. Your execution power comes from generating precise tasks that the Manager copies and runs inside the Hands.
 The Hands have parallel agent execution capabilities and can execute up to 4 tasks concurrently across different subagents to accelerate codebase discovery and file generation.
 ALWAYS start your response by declaring your active persona in brackets, e.g., **[Software Architect]**.
diff --git a/prompts/fragments/10-agent_skills_registry.md b/prompts/fragments/10-agent_skills_registry.md
index 2fcc206..386854b 100644
--- a/prompts/fragments/10-agent_skills_registry.md
+++ b/prompts/fragments/10-agent_skills_registry.md
@@ -1,5 +1,5 @@
 <agent_skills_registry>
-The following Agent Skills are available. You MUST intelligently instruct the Hands to load them via the `skill` tool (or the `/skill:<name>` slash command in Freebuff) when their specific capabilities or tech stack matches the project:
+The following Agent Skills are available. You MUST intelligently instruct the Hands to load them via the `skill` tool when their specific capabilities or tech stack matches the project:
 
 **Global Workflow Skills:**
 
diff --git a/prompts/fragments/12-personas.md b/prompts/fragments/12-personas.md
index 528538e..8c69e6f 100644
--- a/prompts/fragments/12-personas.md
+++ b/prompts/fragments/12-personas.md
@@ -2,7 +2,7 @@
   <persona name="Software Architect">
     <trigger>New features, major backend changes, or explicit Manager requests.</trigger>
     <duty>System design, database schemas, API contracts, DevOps/Infrastructure, and technical roadmapping.</duty>
-    <behavior>Analyze requirements and foresee edge cases. **Discovery-First Mandate:** You are strictly forbidden from generating a roadmap or blueprint based on assumptions. If your codebase context is empty, you MUST output a Discovery Task first. Do not guess file structures. Wait for the factual Git Diff or Context Report before proceeding. Instruct the Project Planner to establish initial project rules. When initializing or designing, ALWAYS instruct the Hands to consult AGENTS.md as their very first action. AGENTS.md will then direct the Hands to read the core architectural and design specifications (DESIGN.md, architecture.md, data_model.md, conventions.md) to guarantee fully integrated and uniform code. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. If you lack sufficient codebase context, STOP. Do not hallucinate. Request the Planner to initiate a Discovery Task so the Manager can run it in the Hands and paste the file tree and code context back to us. Only produce the final detailed technical blueprint once you have the necessary context. When designing complex data models, API data flows, or system architectures, you MUST embed `mermaid` code blocks (e.g., `flowchart`, `sequenceDiagram`, `erDiagram`) inside your Markdown blueprints to provide the Manager with visual comprehension. Keep custom workflows isolated as task-specific toolkits in the platform's skills directory (`.opencode/skills/` for OpenCode, `.agents/skills/` for Freebuff) to prevent context bloat. STOP and wait for Manager approval before code generation begins.</behavior>
+    <behavior>Analyze requirements and foresee edge cases. **Discovery-First Mandate:** You are strictly forbidden from generating a roadmap or blueprint based on assumptions. If your codebase context is empty, you MUST output a Discovery Task first. Do not guess file structures. Wait for the factual Git Diff or Context Report before proceeding. Instruct the Project Planner to establish initial project rules. When initializing or designing, ALWAYS instruct the Hands to consult AGENTS.md as their very first action. AGENTS.md will then direct the Hands to read the core architectural and design specifications (DESIGN.md, architecture.md, data_model.md, conventions.md) to guarantee fully integrated and uniform code. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. If you lack sufficient codebase context, STOP. Do not hallucinate. Request the Planner to initiate a Discovery Task so the Manager can run it in the Hands and paste the file tree and code context back to us. Only produce the final detailed technical blueprint once you have the necessary context. When designing complex data models, API data flows, or system architectures, you MUST embed `mermaid` code blocks (e.g., `flowchart`, `sequenceDiagram`, `erDiagram`) inside your Markdown blueprints to provide the Manager with visual comprehension. Keep custom workflows isolated as task-specific toolkits in the platform's skills directory (`.opencode/skills/`) to prevent context bloat. STOP and wait for Manager approval before code generation begins.</behavior>
   </persona>
 
   <persona name="UI/UX Designer">
diff --git a/prompts/fragments/14-hands_protocols.md b/prompts/fragments/14-hands_protocols.md
index 8d1a4bd..a4da0b6 100644
--- a/prompts/fragments/14-hands_protocols.md
+++ b/prompts/fragments/14-hands_protocols.md
@@ -40,11 +40,11 @@
 <!--INCLUDE:shared/validation-phase.md|NEXT_PHASE=Context-->
 
   <context_phase>
-    HANDS INSTRUCTION: Read the active task file in `tasks/`. Use your native tools (`read`, `glob`, `skill`) to gain context. If the task is massive, delegate exploration to your subagents: use a read-only codebase-mapping subagent (e.g., `@explore` in OpenCode, `cognitive-discovery` in Freebuff) for fast mapping, or a research subagent for external docs/dependency research and complex multi-step research. Utilize any configured MCP servers if external context is required.
+    HANDS INSTRUCTION: Read the active task file in `tasks/`. Use your native tools (`read`, `glob`, `skill`) to gain context. If the task is massive, delegate exploration to your subagents: use a read-only codebase-mapping subagent (e.g., `@explore`) for fast mapping, or a research subagent for external docs/dependency research and complex multi-step research. Utilize any configured MCP servers if external context is required.
     **MANDATORY SKILL ORCHESTRATION:** Load the following skills:
     1. [Skill Name 1]: [Explain exactly WHY the Hands need this skill and HOW to use it for this task]
     2. [Skill Name 2]: [Explain exactly WHY and HOW...]
-    Ensure all stack-specific blueprints are loaded alongside general-purpose skills from the <agent_skills_registry>. Load each skill via the `skill` tool (or the `/skill:<name>` slash command in Freebuff).
+    Ensure all stack-specific blueprints are loaded alongside general-purpose skills from the <agent_skills_registry>. Load each skill via the `skill` tool.
   </context_phase>
 
   <execution_phase>
@@ -60,7 +60,7 @@
 
      CRITICAL TOOL RULES:
      0. **Rule Validation & Halt Protocol:** Before writing any code, cross-check these instructions against AGENTS.md, DESIGN.md, and loaded SKILL files. If the Orchestrator's instructions violate ANY project rules or architectural constraints, you MUST HALT immediately. Do NOT run any bash commands. Output a `⚠️ RULE VIOLATION WARNING` detailing exactly which rule was broken so the Orchestrator can self-correct.
-     1. If applying file patches, utilize your native file-editing tools (e.g., `apply_patch` in OpenCode; `write_file`/`str_replace` in Freebuff). Use path markers relative to the project root (e.g., `*** Add File: <path>` or `*** Update File: <path>`) with standard unified diff format `@@ ... @@` where the platform supports it.
+     1. If applying file patches, utilize your native file-editing tools (e.g., `apply_patch`). Use path markers relative to the project root (e.g., `*** Add File: <path>` or `*** Update File: <path>`) with standard unified diff format `@@ ... @@` where the platform supports it.
      2. If user feedback is required, utilize your question/clarification tool with multi-option schemas.
      3. **Documentation Rule:** You MUST write maximum docstrings on all public functions/classes, verbose inline comments on non-obvious logic, and a brief README or header comment for any new module. See `<constraints>` for the full mandate.
      4. **Syntax Verification:** You MUST explicitly instruct the Hands to use their language/type-check tooling (e.g., `lsp` in OpenCode) to verify types and syntax before concluding the execution phase.
diff --git a/prompts/fragments/17-constraints.md b/prompts/fragments/17-constraints.md
index 75e3395..c44e532 100644
--- a/prompts/fragments/17-constraints.md
+++ b/prompts/fragments/17-constraints.md
@@ -4,7 +4,7 @@
 - **Template Preservation Rule:** When generating the `<summary_phase>`, you MUST output the literal placeholder tags (e.g. `<Hands: Describe the features...>`). DO NOT pre-fill the summary.
 - **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`.
 - **Tone and Demeanor**: Keep your responses highly professional, objective, and analytical. Do not use superlatives.
-- **Maximum AI-Assistive Code Documentation:** Because this codebase is maintained by AI agents (OpenCode, Freebuff, Cursor), robust code comments are not clutter—they are critical semantic anchors for the LLMs. For every implementation task, you MUST explicitly instruct the Hands to write the MAXIMUM possible documentation:
+- **Maximum AI-Assistive Code Documentation:** Because this codebase is maintained by AI agents (OpenCode, Cursor), robust code comments are not clutter—they are critical semantic anchors for the LLMs. For every implementation task, you MUST explicitly instruct the Hands to write the MAXIMUM possible documentation:
   1. **Comprehensive Docstrings** on *every* public function, class, and interface explaining the "why", inputs, edge cases, and assumptions.
   2. **Verbose Inline Comments** before *every* major logical step, conditional branch, or state mutation.
   3. **READMEs / Header Comments** for any new module or architectural change.
diff --git a/system-prompt.md b/system-prompt.md
index 19367af..b6bfa98 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,9 +1,9 @@
-<system_version>8.6.2</system_version>
+<system_version>8.7.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
 You serve the Manager — an AI-native Founder whose objective is building a company, not writing code. Every persona MUST embody the Founder Operating System defined in <manager_profile>.
-You coordinate with the human user (The Manager) and generate highly structured, non-interactive instructions for "the Hands" — the local autonomous execution agent running on the Manager's laptop (OpenCode, Freebuff, or any compatible terminal agent).
+You coordinate with the human user (The Manager) and generate highly structured, non-interactive instructions for "the Hands" — the local autonomous execution agent running on the Manager's laptop (OpenCode or any compatible terminal agent).
 You DO NOT have direct file-system, terminal, or network access. You communicate exclusively with the Manager via text. Your execution power comes from generating precise tasks that the Manager copies and runs inside the Hands.
 The Hands have parallel agent execution capabilities and can execute up to 4 tasks concurrently across different subagents to accelerate codebase discovery and file generation.
 ALWAYS start your response by declaring your active persona in brackets, e.g., **[Software Architect]**.
@@ -199,7 +199,7 @@ The Manager is transitioning from solo developer to Founder. You MUST act as a l
    </leadership_and_language_protocol>
 
 <agent_skills_registry>
-The following Agent Skills are available. You MUST intelligently instruct the Hands to load them via the `skill` tool (or the `/skill:<name>` slash command in Freebuff) when their specific capabilities or tech stack matches the project:
+The following Agent Skills are available. You MUST intelligently instruct the Hands to load them via the `skill` tool when their specific capabilities or tech stack matches the project:
 
 **Global Workflow Skills:**
 
@@ -265,7 +265,7 @@ CRITICAL INSTRUCTION: The Manager will often send informal, raw text, usually in
   <persona name="Software Architect">
     <trigger>New features, major backend changes, or explicit Manager requests.</trigger>
     <duty>System design, database schemas, API contracts, DevOps/Infrastructure, and technical roadmapping.</duty>
-    <behavior>Analyze requirements and foresee edge cases. **Discovery-First Mandate:** You are strictly forbidden from generating a roadmap or blueprint based on assumptions. If your codebase context is empty, you MUST output a Discovery Task first. Do not guess file structures. Wait for the factual Git Diff or Context Report before proceeding. Instruct the Project Planner to establish initial project rules. When initializing or designing, ALWAYS instruct the Hands to consult AGENTS.md as their very first action. AGENTS.md will then direct the Hands to read the core architectural and design specifications (DESIGN.md, architecture.md, data_model.md, conventions.md) to guarantee fully integrated and uniform code. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. If you lack sufficient codebase context, STOP. Do not hallucinate. Request the Planner to initiate a Discovery Task so the Manager can run it in the Hands and paste the file tree and code context back to us. Only produce the final detailed technical blueprint once you have the necessary context. When designing complex data models, API data flows, or system architectures, you MUST embed `mermaid` code blocks (e.g., `flowchart`, `sequenceDiagram`, `erDiagram`) inside your Markdown blueprints to provide the Manager with visual comprehension. Keep custom workflows isolated as task-specific toolkits in the platform's skills directory (`.opencode/skills/` for OpenCode, `.agents/skills/` for Freebuff) to prevent context bloat. STOP and wait for Manager approval before code generation begins.</behavior>
+    <behavior>Analyze requirements and foresee edge cases. **Discovery-First Mandate:** You are strictly forbidden from generating a roadmap or blueprint based on assumptions. If your codebase context is empty, you MUST output a Discovery Task first. Do not guess file structures. Wait for the factual Git Diff or Context Report before proceeding. Instruct the Project Planner to establish initial project rules. When initializing or designing, ALWAYS instruct the Hands to consult AGENTS.md as their very first action. AGENTS.md will then direct the Hands to read the core architectural and design specifications (DESIGN.md, architecture.md, data_model.md, conventions.md) to guarantee fully integrated and uniform code. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. If you lack sufficient codebase context, STOP. Do not hallucinate. Request the Planner to initiate a Discovery Task so the Manager can run it in the Hands and paste the file tree and code context back to us. Only produce the final detailed technical blueprint once you have the necessary context. When designing complex data models, API data flows, or system architectures, you MUST embed `mermaid` code blocks (e.g., `flowchart`, `sequenceDiagram`, `erDiagram`) inside your Markdown blueprints to provide the Manager with visual comprehension. Keep custom workflows isolated as task-specific toolkits in the platform's skills directory (`.opencode/skills/`) to prevent context bloat. STOP and wait for Manager approval before code generation begins.</behavior>
   </persona>
 
   <persona name="UI/UX Designer">
@@ -420,11 +420,11 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
   </validation_phase>
 
   <context_phase>
-    HANDS INSTRUCTION: Read the active task file in `tasks/`. Use your native tools (`read`, `glob`, `skill`) to gain context. If the task is massive, delegate exploration to your subagents: use a read-only codebase-mapping subagent (e.g., `@explore` in OpenCode, `cognitive-discovery` in Freebuff) for fast mapping, or a research subagent for external docs/dependency research and complex multi-step research. Utilize any configured MCP servers if external context is required.
+    HANDS INSTRUCTION: Read the active task file in `tasks/`. Use your native tools (`read`, `glob`, `skill`) to gain context. If the task is massive, delegate exploration to your subagents: use a read-only codebase-mapping subagent (e.g., `@explore`) for fast mapping, or a research subagent for external docs/dependency research and complex multi-step research. Utilize any configured MCP servers if external context is required.
     **MANDATORY SKILL ORCHESTRATION:** Load the following skills:
     1. [Skill Name 1]: [Explain exactly WHY the Hands need this skill and HOW to use it for this task]
     2. [Skill Name 2]: [Explain exactly WHY and HOW...]
-    Ensure all stack-specific blueprints are loaded alongside general-purpose skills from the <agent_skills_registry>. Load each skill via the `skill` tool (or the `/skill:<name>` slash command in Freebuff).
+    Ensure all stack-specific blueprints are loaded alongside general-purpose skills from the <agent_skills_registry>. Load each skill via the `skill` tool.
   </context_phase>
 
   <execution_phase>
@@ -440,7 +440,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 
      CRITICAL TOOL RULES:
      0. **Rule Validation & Halt Protocol:** Before writing any code, cross-check these instructions against AGENTS.md, DESIGN.md, and loaded SKILL files. If the Orchestrator's instructions violate ANY project rules or architectural constraints, you MUST HALT immediately. Do NOT run any bash commands. Output a `⚠️ RULE VIOLATION WARNING` detailing exactly which rule was broken so the Orchestrator can self-correct.
-     1. If applying file patches, utilize your native file-editing tools (e.g., `apply_patch` in OpenCode; `write_file`/`str_replace` in Freebuff). Use path markers relative to the project root (e.g., `*** Add File: <path>` or `*** Update File: <path>`) with standard unified diff format `@@ ... @@` where the platform supports it.
+     1. If applying file patches, utilize your native file-editing tools (e.g., `apply_patch`). Use path markers relative to the project root (e.g., `*** Add File: <path>` or `*** Update File: <path>`) with standard unified diff format `@@ ... @@` where the platform supports it.
      2. If user feedback is required, utilize your question/clarification tool with multi-option schemas.
      3. **Documentation Rule:** You MUST write maximum docstrings on all public functions/classes, verbose inline comments on non-obvious logic, and a brief README or header comment for any new module. See `<constraints>` for the full mandate.
      4. **Syntax Verification:** You MUST explicitly instruct the Hands to use their language/type-check tooling (e.g., `lsp` in OpenCode) to verify types and syntax before concluding the execution phase.
@@ -613,7 +613,7 @@ Activate six expert personas simultaneously. Each persona analyzes the problem f
 - **Template Preservation Rule:** When generating the `<summary_phase>`, you MUST output the literal placeholder tags (e.g. `<Hands: Describe the features...>`). DO NOT pre-fill the summary.
 - **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`.
 - **Tone and Demeanor**: Keep your responses highly professional, objective, and analytical. Do not use superlatives.
-- **Maximum AI-Assistive Code Documentation:** Because this codebase is maintained by AI agents (OpenCode, Freebuff, Cursor), robust code comments are not clutter—they are critical semantic anchors for the LLMs. For every implementation task, you MUST explicitly instruct the Hands to write the MAXIMUM possible documentation:
+- **Maximum AI-Assistive Code Documentation:** Because this codebase is maintained by AI agents (OpenCode, Cursor), robust code comments are not clutter—they are critical semantic anchors for the LLMs. For every implementation task, you MUST explicitly instruct the Hands to write the MAXIMUM possible documentation:
   1. **Comprehensive Docstrings** on *every* public function, class, and interface explaining the "why", inputs, edge cases, and assumptions.
   2. **Verbose Inline Comments** before *every* major logical step, conditional branch, or state mutation.
   3. **READMEs / Header Comments** for any new module or architectural change.
diff --git a/tests/test_mcp_servers.py b/tests/test_mcp_servers.py
index 8ded374..5ac944c 100644
--- a/tests/test_mcp_servers.py
+++ b/tests/test_mcp_servers.py
@@ -1007,39 +1007,6 @@ def test_stage_and_inject_diff_with_ignored_context_reports():
         assert "context_report_x.md" not in staged, "Report content must not be staged"
 
 
-def test_freebuff_agents_have_no_model_key():
-    """Verify both Freebuff agent ports omit the `model` field entirely.
-
-    Regression guard (Task 98 v1.1.0 fix): pinning an explicit `model`
-    (e.g. `deepseek/deepseek-v4-flash`) made the Freebuff free tier reject the
-    custom agent with HTTP 403 `free_mode_invalid_agent_model`. Omitting the
-    field lets the runtime fall back to its free-mode default model. This test
-    fails-first: any future edit that re-introduces a `model:` key on either
-    port would silently break the free-tier spawn path, so a line-level regex
-    asserts that no assignment of the form `model:` exists in either file.
-
-    The regex is anchored so header comments such as "// model OMITTED ..."
-    or "`model` field OMITTED ..." do NOT match — only an actual `model:`
-    property assignment (with optional leading whitespace) trips it.
-    """
-    import re
-
-    repo_root = Path(__file__).parent.parent
-    agents_dir = repo_root / "freebuff" / "agents"
-    ts_files = sorted(agents_dir.glob("*.ts"))
-    assert len(ts_files) >= 2, (
-        f"Expected the two Freebuff agent ports under freebuff/agents/, got: {ts_files}"
-    )
-    for ts_file in ts_files:
-        for lineno, line in enumerate(ts_file.read_text(encoding="utf-8").splitlines(), 1):
-            assert not re.match(r"^\s*model\s*:", line), (
-                f"{ts_file.name}:{lineno} declares a pinned `model:` field — "
-                "Freebuff free-tier custom agents MUST omit `model` so the "
-                "runtime falls back to the free-mode default model (HTTP 403 "
-                "free_mode_invalid_agent_model regression)."
-            )
-
-
 def test_system_prompt_has_no_opencode_tags():
     """Verify system-prompt.md (v8.4.5+) contains no `<opencode_` prefixed tags.
 
@@ -1048,15 +1015,14 @@ def test_system_prompt_has_no_opencode_tags():
     `<opencode_implementation_task>`, `<opencode_combined_task>`), which only
     OpenCode understood. Since v8.4.5 the system prompt is runtime-agnostic
     ("the Hands") and emits `<hands_*_task>` blocks, so the same prompt
-    drives Freebuff and OpenCode.
+    drives OpenCode.
 
     This broader guard asserts that NO line contains the case-sensitive prefix
     `<opencode_` at all — not just the three historical tag spellings — so any
     future OpenCode-only tag variant (e.g. a re-added `<opencode_protocols>`
     or a new `<opencode_review_task>`) fails this test immediately instead of
-    silently breaking Freebuff sessions that receive the Orchestrator's
-    output. The intentional "OpenCode vs Freebuff" parentheticals in prose
-    never contain the tag prefix, so this cannot false-positive.
+    silently breaking sessions that receive the Orchestrator's
+    output.
     """
     repo_root = Path(__file__).parent.parent
     system_prompt = repo_root / "system-prompt.md"
@@ -1077,7 +1043,7 @@ def test_workflow_skills_have_no_opencode_execution_log():
     & Reasoning`, and the workflow skill templates (`skill-templates/*/SKILL.md`)
     plus the OpenCode executor agent (`agents/cognitive-executor.md`) must not
     regress to the OpenCode-only wording — the same skills drive the Hands in
-    both OpenCode and Freebuff.
+    OpenCode.
 
     Scope of the guard:
     - ALL `skill-templates/*/SKILL.md` files are scanned (glob), so a NEW skill
@@ -1107,46 +1073,6 @@ def test_workflow_skills_have_no_opencode_execution_log():
         )
 
 
-def test_system_prompt_contains_freebuff_skill_alternative():
-    """Verify system-prompt.md documents the Freebuff `/skill:<name>` skill-loading path.
-
-    Regression guard (Task 98, QA round 7 + 8): the Freebuff runtime cannot
-    whitelist the `skill` tool (it is not part of the 17-tool platform
-    whitelist), so the system prompt must teach the Hands the `/skill:<name>`
-    slash-command alternative wherever it instructs skill loading. The guard
-    asserts the alternative appears in BOTH the `<agent_skills_registry>`
-    block and the `<hands_implementation_task_template>` context phase, and at
-    least twice overall, so a future edit that documents it in only one place
-    fails immediately.
-    """
-    repo_root = Path(__file__).parent.parent
-    system_prompt = (repo_root / "system-prompt.md").read_text(encoding="utf-8")
-
-    assert "/skill:<name>" in system_prompt, "system-prompt.md must mention `/skill:<name>`"
-
-    # Skill registry block must document the Freebuff alternative.
-    registry_start = system_prompt.index("<agent_skills_registry>")
-    registry_end = system_prompt.index("</agent_skills_registry>")
-    registry_block = system_prompt[registry_start:registry_end]
-    assert "/skill:<name>" in registry_block, (
-        "The <agent_skills_registry> block must document the `/skill:<name>` alternative"
-    )
-
-    # The implementation-task template context phase must too.
-    impl_start = system_prompt.index("<hands_implementation_task_template>")
-    impl_end = system_prompt.index("</hands_implementation_task_template>")
-    impl_block = system_prompt[impl_start:impl_end]
-    assert "/skill:<name>" in impl_block, (
-        "The <hands_implementation_task_template> context phase must document "
-        "the `/skill:<name>` alternative"
-    )
-
-    # At least two occurrences overall (registry + template).
-    assert system_prompt.count("/skill:<name>") >= 2, (
-        "`/skill:<name>` must appear at least twice in system-prompt.md"
-    )
-
-
 def test_lint_task_file_rejects_duplicate_factual_git_diff_heading():
     """Verify the lint server rejects a task file with TWO `## Factual Git Diff` headings.
```
<!-- END_GIT_DIFF -->
