# Task 45: Implement V6 Kanban Lifecycle

**File:** `tasks/in-progress/45-implement-v6-kanban-lifecycle.md`
**Type:** improvement
**Status:** closed

## Goal

Upgrade the repository to V6 Kanban Task Architecture: scaffold Kanban directories, add the `commit_and_clean_task` MCP tool, create `migrate-kanban` and `archive-tasks` skills, update existing skills and system prompt to reference the Kanban lifecycle.

## Manager's Notes

- Implement the V6 lifecycle exactly as specified in the orchestration task.
- All Kanban directories: `tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`.

## Local TODOs

- [x] **Step 1:** Scaffold Kanban directories
- [x] **Step 2:** Update MCP server — add `commit_and_clean_task` tool
- [x] **Step 3:** Create `skill-templates/migrate-kanban/SKILL.md`
- [x] **Step 4:** Create `skill-templates/archive-tasks/SKILL.md`
- [x] **Step 5:** Update `skill-templates/task-generator/SKILL.md`
- [x] **Step 6:** Update `skill-templates/telegram-issue-sync/SKILL.md`
- [x] **Step 7:** Update `skill-templates/audit-agents/SKILL.md`
- [x] **Step 8:** Update `system-prompt.md` to V6.0.0
- [x] **Step 9:** Update `README.md` for V6 Kanban
- [x] **Step 10:** Update `CHANGELOG.md` for V6.0.0
- [x] **Step 11:** Verify Python syntax and format markdown

## OpenCode Execution Log & Reasoning

### Architectural Summary

Successfully deployed V6 Kanban Task Architecture across the entire repo:

**Kanban Directories Created:**
- `tasks/backlog/` — for open/unstarted tasks
- `tasks/in-progress/` — for active work
- `tasks/qa/` — for review
- `tasks/completed/` — for finished tasks
- `tasks/archive/` — for milestone-compacted history

**MCP Server (`mcp-context-server/server.py`):**
- Added `commit_and_clean_task` tool — commits staged changes, extracts hash, replaces raw diff in task file with hash reference, amends commit. This keeps task files lean and commits compact.

**New Skills Created:**
- `skill-templates/migrate-kanban/SKILL.md` — scans flat tasks/ directory, classifies by Status metadata, uses `git mv` to migrate into Kanban folders
- `skill-templates/archive-tasks/SKILL.md` — milestone compaction: reads completed/ tasks, generates dense `docs/history/milestone-X-summary.md`, moves to archive/

**Skills Updated:**
- `task-generator` — directory refs changed from `tasks/` to `tasks/backlog/`; ID calc uses `find` across all Kanban subdirs
- `telegram-issue-sync` — NEXT_ID command uses `find`; all file creation paths now `tasks/backlog/`
- `audit-agents` — both Target Audit Criteria blocks and AGENTS.md template updated to list 5 Kanban directories

**System Prompt V6.0.0:**
- Version bumped from 5.19.0 to 6.0.0
- Project Planner manages state-based Kanban directories
- Code Reviewer APPROVED action uses `custom_context_commit_and_clean_task`
- Execution workflow includes backlog → in-progress → qa → completed transitions
- Summary phase path updated to `tasks/in-progress/`

**AGENTS.md Updated:**
- Core File Locations now list all 5 Kanban directories
- End-of-Task sequence expanded to include move-to-completed step and `custom_context_commit_and_clean_task` alternative

### Quick-Fix: `git mv` Exception (ZAC Guardrail)

Added `git mv` exception to the Zero-Autonomous-Commit rules across `system-prompt.md`, `AGENTS.md`, and `audit-agents/SKILL.md` to prevent Kanban transition deadlocks. Without this exception, OpenCode would halt with a Rule Violation when trying to move task files between Kanban directories via `git mv`.

### Final Refinement: ZAC Refactored + Migrate-Kanban Fix

Refactored the Zero-Autonomous-Commit rule across all three files (`system-prompt.md`, `AGENTS.md`, `audit-agents/SKILL.md`) to be command-agnostic — agents may NOW run Git commands when explicitly instructed by the Orchestrator, rather than being hard-blocked with specific exceptions. This prevents the ZAC rule itself from being a maintenance burden as new Git operations are needed.

Also fixed an edge case in `skill-templates/migrate-kanban/SKILL.md`: added `[ -e "$f" ] || continue` inside the bash glob loop to prevent errors when `tasks/*.md` expands to the literal string on an empty directory.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `d5a77d8`
<!-- END_GIT_DIFF -->
