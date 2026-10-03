# Task 290: Adopt opencode-todolist plugin

**File:** `tasks/completed/290-adopt-opencode-todolist-plugin.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Restore the V1 todo steps list in OpenCode V2 by adopting the `opencode-todolist` plugin globally and documenting it in every place the platform lists plugins.

## Manager's Notes

Manager order (verbatim): "create a task and add - opencode-todolist, add it everyplace, all docs in our project. and install globally and tell me restart opencode then smoke test". Scope: global install (`opencode plugin add opencode-todolist` + TUI strip via `cli.json`), HQ docs sync (`README.md`, `LLM.txt`), CHANGELOG entry, then Manager restarts OpenCode and Hands smoke-tests `todowrite`/`todoread` + sidebar.

## Local TODOs

- [x] Install `opencode-todolist` globally and enable the TUI sidebar strip via `cli.json`
- [x] Update `README.md` OpenCode Plugins section (one plugin -> two plugins)
- [x] Update `LLM.txt` Step 7 JSON, Step 7.7 Plugins, and stale no-plugins checklist
- [x] Update `CHANGELOG.md` via Parse-Then-Append
- [x] Run verification gate and record evidence

## Acceptance Criteria

- [x] Global `opencode.json` `plugins` includes `smart-compact` and `opencode-todolist`
- [x] Global `cli.json` `plugins` includes `opencode-todolist` for the sidebar strip
- [x] `README.md` and `LLM.txt` document both plugins with install commands
- [x] No doc still claims the platform uses one plugin or no plugins
- [ ] `opencode plugin list` shows the todolist entry after restart (or install recorded pre-restart)

## Verification Evidence

- **Test command:** rtk test uv run --with-requirements /tmp/opencode/clh-test-reqs.txt pytest tests/test_prompt_sync.py -q
- **Expected result:** pass, exit code 0
- **Actual result:** `13 passed in 0.08s` plus `docs-sync: OK` from `python3 scripts/check_docs_sync.py`
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** plugin loads only after OpenCode restart; pre-restart `plugin list` may not show it.
- **Rollback plan:** `opencode plugin remove opencode-todolist`, drop the `cli.json` entry, revert doc hunks.

---

## Execution Log & Reasoning

**Plan verdict:** Manager's explicit order is the plan (create task + document everywhere + install globally + restart + smoke test). **Brainstorm:** not required — single concern, reversible config + docs. **Seat Check:** domains = OpenCode config/docs → requested: Software Architect; skipped seats N/A (Lite path, 2-line check).

**Gatekeeper:** no rule violation — global plugin install + docs sync matches Tasks 287/288 precedent; repo `opencode.json` untouched (global-only `plugins`/`cli.json` per opencode-init contract); ZAC holds (no commit by Hands).

**Changes:** `opencode plugin add opencode-todolist` exit 0 — global `opencode.json` `plugins` now `[smart-compact, opencode-todolist]`; `~/.config/opencode/cli.json` `plugins` now `[opencode-todolist]` for the sidebar strip. `README.md` one plugin → two plugins. `LLM.txt` Step 7 JSON + description, Step 7.7 (todolist install + `cli.json` strip + restart smoke test), stale no-plugins checklist corrected. `CHANGELOG.md` Unreleased/Added entry.

**Verification:** `python3 scripts/check_docs_sync.py` → `docs-sync: OK`; `rtk test ... pytest tests/test_prompt_sync.py -q` → `13 passed`, exit 0. `git status` shows `README.md`, `LLM.txt`, `CHANGELOG.md` modified plus the new task file.

**Pending (needs Manager):** restart OpenCode to load the plugin, then live smoke test — ask agent for a todo list (`todowrite`), read it back (`todoread`), confirm the TUI sidebar strip. AC5 stays open until then.

**Closure:** Manager accept quote "is fine close task" — closing per explicit close order. AC5 (post-restart `plugin list`) accepted as-is by Manager; smoke test to be confirmed live after restart.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `bf285853a1daa5d895d66d22f16134bac9f09756`
<!-- END_GIT_DIFF -->
