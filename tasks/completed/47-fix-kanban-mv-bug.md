# Task 47: Fix Kanban Git mv Bug

**File:** `tasks/in-progress/47-fix-kanban-mv-bug.md`
**Type:** bug
**Status:** closed

## Goal

Fix a critical Git tracking bug caused by standard `mv` fallbacks when Kanban directories are empty. The `commit_and_clean_task` MCP tool used `git add <single_file>` which missed the deletion of the old path. Additionally, the Code Reviewer and workflow instructions didn't mandate `mkdir -p tasks/completed/` before `git mv`, causing failures when the directory doesn't exist.

## Manager's Notes

- The root cause: `tasks/completed/` directory was deleted by `git rm` (empty dirs disappear), so subsequent `git mv` into it fails.
- Fix: `git add -A tasks/` in the MCP server catches both additions and deletions.
- Fix: Add `mkdir -p tasks/completed/` to the Code Reviewer's template and workflow Step 7.

## Local TODOs

- [x] Step 1: Scaffold task file
- [x] Step 2: Clean Git index (git rm tasks/in-progress/46-implement-qa-persona.md)
- [x] Step 3: Bulletproof MCP server (`git add -A tasks/`)
- [x] Step 4: Patch Code Reviewer persona with `mkdir -p` instruction
- [x] Step 5: Patch workflow Step 7 with `mkdir -p` instruction
- [x] Step 6: Update CHANGELOG.md
- [x] Run `npx prettier --write "**/*.md"`

## OpenCode Execution Log & Reasoning

**Architectural Reasoning:** The root cause was a classic empty-directory-in-Git problem. When `git rm` deletes all files in `tasks/completed/`, Git removes the directory from the working tree. Subsequent `git mv` into that directory fails because the path doesn't exist. The `commit_and_clean_task` MCP tool used `git add <single_file>` which only staged the moved file but missed the deletion of the old path — so Git had both the old path (deleted on disk but tracked) and the new path. Fixed by replacing with `git add -A tasks/` which catches all changes (additions + deletions) under the tasks tree. Additionally, the Code Reviewer persona and workflow Step 7 were hardened to explicitly mandate `mkdir -p tasks/completed/` before `git mv`, so the target directory is always guaranteed to exist.

**Files Modified:**

1. **`mcp-context-server/server.py`** — `commit_and_clean_task`: changed `git add <task_file_path>` to `git add -A tasks/` to catch deletions from `mv` fallbacks.
2. **`system-prompt.md`** — Code Reviewer persona final sentence now mandates `mkdir -p tasks/completed/` before `git mv`. Workflow Step 7 similarly updated.
3. **`CHANGELOG.md`** — Added Fixed entries under [6.1.0] for both the MCP server hardening and the missing `mkdir -p` instructions.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `244553b44efb9a19c02e71fe228e736cd6593cb9`
<!-- END_GIT_DIFF -->
