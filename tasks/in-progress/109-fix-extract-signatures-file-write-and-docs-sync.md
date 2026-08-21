# Task 109: Fix extract_signatures File-Write Bug & Sync Docs

**File:** `tasks/in-progress/109-fix-extract-signatures-file-write-and-docs-sync.md`
**Source:** manager
**Type:** bug
**Status:** open

## Goal

Fix the `extract_signatures` MCP tool to write extracted signatures to a markdown file under `context-reports/` (matching the behavior of `read_source_files` and `create_tree_report`), and sync the updated documentation across all skill copies.

## Manager's Notes

The `extract_signatures` tool was returning signature strings inline but never persisting them to disk. This is inconsistent with the other two context-producing tools. Additionally, the `code-search` SKILL.md example usage showed stale inline return values that no longer match the new behavior.

## Local TODOs

- [x] Fix `extract_signatures` in `mcp-context-server/server.py` to write to `context-reports/signatures_report_<ts>_<uuid>.md`
- [x] Update `skill-templates/code-search/SKILL.md` example usage section
- [x] Sync global skill copies (`~/.config/opencode/skills/` and `~/.agents/skills/`)
- [x] Verify Python syntax compiles

## Acceptance Criteria

- [ ] `extract_signatures` writes to `context-reports/signatures_report_<timestamp>_<uuid>.md`
- [ ] `extract_signatures` returns a success message with the file path (same pattern as `read_source_files` and `create_tree_report`)
- [ ] `code-search` SKILL.md example usage shows file-path return, not inline return
- [ ] All three SKILL.md copies (template + 2 global) are identical
- [ ] Python syntax validates (`py_compile`)

## Verification Evidence

- **Test command:** `python3 -c "import py_compile; py_compile.compile('mcp-context-server/server.py', doraise=True)"`
- **Expected result:** `✅ Syntax OK`
- **Actual result:** `✅ Syntax OK` — Python compilation passed
- **Exit code:** 0

## Definition of Done

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Agents relying on inline signature output may need to read the generated file instead.
- **Rollback plan:** Revert the `extract_signatures` function in `server.py` to its previous inline-return version.

---

## Execution Log & Reasoning

### Bug Fix: `mcp-context-server/server.py`

**Root Cause:** `extract_signatures` (line 440) returned the signature string inline but never wrote to a file under `context-reports/`. The other two context tools (`read_source_files`, `create_tree_report`) both persist to disk.

**Fix:** Modified `extract_signatures` to:
1. Call `_ensure_context_reports_ignored()` (same safeguard as sibling tools)
2. Write extracted signatures to `context-reports/signatures_report_<timestamp>_<uuid>.md`
3. Return a success message with the file path

**Files modified:**
- `mcp-context-server/server.py` — rewrote `extract_signatures` tool function (lines 440-496)

### Docs Sync: `skill-templates/code-search/SKILL.md`

**Issue:** Example usage (lines 90-99) showed inline return values (`Returns: class UserService:...`). Now the tool writes to a file and returns a path.

**Fix:** Updated example to show the actual return value (file path) and the report content.

**Files modified:**
- `skill-templates/code-search/SKILL.md` — Example Usage section (lines 90-103)
- `~/.config/opencode/skills/code-search/SKILL.md` — synced from template
- `~/.agents/skills/code-search/SKILL.md` — synced from template

### Verification

- `py_compile` passed: `✅ Syntax OK`
- All three SKILL.md copies verified identical via `diff`

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
