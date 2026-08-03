# Task 75: P1 Quality Improvements

**File:** `tasks/backlog/75-p1-quality-improvements.md`
**Source:** orchestrator
**Type:** improvement
**Status:** closed

## Source Context

### Variant A: Orchestrator (`**Source:** orchestrator`)

## Goal

Implement P1 quality improvements: add MCP server startup tests, enhance memory search with YAML frontmatter and ranking, create a system prompt modularization assessment, and document tree-sitter fallback languages.

## Blueprint Reference

V8.0.0 Improvement Roadmap Phase 5

## Manager's Notes

This task covers four independent quality improvements that strengthen the platform's reliability and maintainability. Each sub-task is self-contained and can be verified independently.

## Local TODOs

- [x] Add MCP server startup tests
- [x] Enhance memory search with YAML frontmatter and ranking
- [x] Create system prompt modularization assessment
- [x] Document tree-sitter fallback languages

---

## OpenCode Execution Log & Reasoning

### Phase 1: Task File Creation
- Discovered next task ID: 75 (no collision found)
- Created `tasks/backlog/75-p1-quality-improvements.md` using unified canonical template
- Moved to `tasks/in-progress/` via `git mv`

### Phase 2: MCP Server Startup Tests
- Created `tests/test_mcp_servers.py` with 5 test functions:
  - `test_context_server_import` — Verifies context server imports and exposes `mcp.name == "CustomContext"`
  - `test_memory_server_import` — Verifies memory server imports and exposes `mcp.name == "ProjectMemory"`
  - `test_lint_server_import` — Verifies lint server imports and exposes `mcp.name == "LintServer"`
  - `test_lint_task_file_logic` — Validates `_check_task_file_structure` returns 0 issues for a valid task file
  - `test_lint_task_file_missing_sections` — Validates detection of missing required sections
- Used `importlib.util.spec_from_file_location` for isolated module loading to avoid `mcp` variable conflicts between servers

### Phase 3: Memory Search Enhancement
- Added `"pyyaml"` to dependency list in `mcp-memory-server/server.py` script header
- Added `import yaml` and `from datetime import datetime, timezone` imports
- Modified `store_memory` tool: auto-prepends YAML frontmatter (`created_at`, `updated_at`, `status: active`, `tags: []`) if content doesn't start with `---`
- Rewrote `search_memory` tool with:
  - Tag filtering: `tag:xxx` in query filters by frontmatter tags
  - Ranking: exact key matches (⭐ prefix) ranked above content-only matches
  - YAML frontmatter parsing for tag extraction

### Phase 4: System Prompt Modularization Assessment
- Created `docs/system-prompt-modularization.md` — comprehensive design document covering:
  - Section mapping (14 sections, ~4,520 tokens)
  - Duplicated rules analysis (validation phase 3x, AGENTS.md overlap, persona-skill overlap)
  - Proposed directory structure (`prompts/core/`, `prompts/personas/`, etc.)
  - Token savings estimate (~52-65% reduction)
  - 5-phase migration plan

### Phase 5: Fallback Languages Documentation
- Added regex fallback note after the Languages Supported table in `skill-templates/code-search/SKILL.md`
- Documents that Swift, Ruby, PHP, and C# use regex-based extraction (no tree-sitter queries)

### Phase 6: Verification & Documentation
- Python syntax verified: `py_compile` passed for both `mcp-memory-server/server.py` and `tests/test_mcp_servers.py`
- System version bumped: `7.4.2` → `7.5.0` (MINOR bump for new features)
- CHANGELOG.md updated with formal entry under `## [Unreleased]` → `### Added`

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `aa72dc79d1aeba7133f9849083929270611bfe76`
<!-- END_GIT_DIFF -->
