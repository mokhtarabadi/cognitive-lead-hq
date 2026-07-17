# Task: Add memory deletion capability

**File:** `tasks/backlog/51-add-memory-deletion.md`
**Type:** improvement
**Status:** closed

## Goal

Add a `delete_memory` tool to the Project Memory MCP server so stale/obsolete notes can be removed, and update the `project-memory` skill to instruct agents on when to delete.

## Manager's Notes

- Adds `delete_memory` tool to `mcp-memory-server/server.py`
- Uses existing `_validate_and_resolve` for path safety
- Prunes empty namespace directories after deletion
- Updates `opencode.json` permissions and `CHANGELOG.md` release notes

## Local TODOs

- [ ] **Step 1:** Create task file and move to `tasks/in-progress/`
- [x] **Step 2:** Add `delete_memory` to `mcp-memory-server/server.py`
- [x] **Step 3:** Update `opencode.json` to allow `delete_memory`
- [x] **Step 4:** Update `skill-templates/project-memory/SKILL.md` with deletion instructions
- [x] **Step 5:** Update `CHANGELOG.md` 6.4.0 notes
- [ ] **Step 6:** Verify Python syntax and format markdown

## OpenCode Execution Log & Reasoning

### Reasoning

User requested a `delete_memory` tool since the MCP server only had store/read/search/list. Added the tool after `read_memory`, reusing the existing `_validate_and_resolve` for path safety. The function unlinks the file and cleans up empty namespace directories to prevent clutter. Updated the `project-memory` skill to instruct agents on when to delete (Manager explicitly revoking a rule). Also registered `delete_memory: allow` in `opencode.json` and updated the CHANGELOG tool count from 4 to 5.

### Files Changed

- **Modified:** `mcp-memory-server/server.py` — added `delete_memory` tool
- **Modified:** `opencode.json` — added `delete_memory: allow`
- **Modified:** `skill-templates/project-memory/SKILL.md` — added "When to DELETE" section
- **Modified:** `CHANGELOG.md` — updated tool count in 6.4.0 entry
- **Created:** `tasks/in-progress/51-add-memory-deletion.md` — this task file

### Verifications

- Python syntax: PASS (py_compile)
- Markdown formatting: PASS (prettier)

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

**Factual Git Diff:** Stored in Commit Hash: `06904f7d0bc454ec6081f4dbbede08293bb8d9a6`
<!-- END_GIT_DIFF -->
