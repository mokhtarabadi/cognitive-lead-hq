# Task: Implement Project Memory System (MCP Server + Skill)

**File:** `tasks/in-progress/50-implement-project-memory-system.md`
**Type:** feature
**Status:** closed

## Goal

Implement a persistent project memory system consisting of an MCP server (`mcp-memory-server/server.py`) and a companion Agent Skill (`skill-templates/project-memory/SKILL.md`). This solves the issue of the Manager repeatedly explaining project quirks across sessions.

## Manager's Notes

- MCP server stores memory as markdown files under `.opencode/memory/` using atomic writes
- Uses `FastMCP` like the existing `custom_context` server
- Skill teaches OpenCode when to store and retrieve memory context
- Version 6.4.0

## Local TODOs

- [x] **Step 1:** Create `mcp-memory-server/server.py`
- [x] **Step 2:** Create `skill-templates/project-memory/SKILL.md`
- [x] **Step 3:** Update `opencode.json` to register the new MCP server
- [x] **Step 4:** Update `system-prompt.md` to integrate the memory system
- [x] **Step 5:** Update `skill-templates/audit-agents/SKILL.md`
- [x] **Step 6:** Update `README.md` and `CHANGELOG.md` (Version 6.4.0)
- [x] **Step 7 (QA Fix):** Update `mcp-memory-server/server.py` — add `_validate_and_resolve` with regex sanitization and `is_relative_to` path boundary checks
- [x] **Step 8 (QA Fix):** Update `mcp-memory-server/server.py` — add temp file cleanup on `os.replace` failure in `store_memory`

## OpenCode Execution Log & Reasoning

### QA Fixes (2026-07-16)

**Vulnerability 1 — Path Traversal:** `_ensure_namespace`, `read_memory`, and `search_memory` constructed file paths directly from user-supplied `namespace`/`key` strings. A malicious input like `../../etc` could escape `.opencode/memory/`. Fixed by adding `_validate_and_resolve` which applies regex alphanumeric-only validation (`^[a-zA-Z0-9_-]+$`) plus runtime `is_relative_to` boundary enforcement.

**Vulnerability 2 — Dangling Temp Files:** If `os.replace` raised between `mkstemp` and `os.replace`, the temp file leaked on disk. Fixed by wrapping the critical section in try/except with explicit `os.unlink(temp_path)` cleanup.

### Architectural Reasoning

This task implements the long-planned Memory Management system (Roadmap item #7). The architecture follows the same pattern as the existing `custom_context` MCP + `code-search` skill pairing: a FastMCP server for data operations, and a `SKILL.md` teaching OpenCode the interface protocol.

### Key Design Decisions

1. **Markdown files over JSON** — The original roadmap suggested `.opencode/project-memory.json`, but markdown files under `.opencode/memory/<namespace>/<key>.md` are more git-friendly, human-readable, and support atomic writes via `tempfile` + `os.replace` without corruption risk.
2. **Namespace slicing** — Memories are organized into namespaces (e.g., `testing`, `database`, `quirks`) to prevent context bloat and support targeted retrieval.
3. **Context Bootstrapping in audit-agents** — The new constraint forces every task's Context Phase to proactively load relevant memories, preventing the Manager from repeating project rules.

### Files Changed

- **Created:** `mcp-memory-server/server.py` (FastMCP server, 4 tools)
- **Created:** `skill-templates/project-memory/SKILL.md` (store/retrieve triggers)
- **Modified:** `opencode.json` (registered `project_memory` MCP server + permissions)
- **Modified:** `system-prompt.md` (version 6.4.0, skill registry, architect/programmer behaviors)
- **Modified:** `skill-templates/audit-agents/SKILL.md` (Context Bootstrapping in both audit blocks and template)
- **Modified:** `README.md` (roadmap item #7 struck through)
- **Modified:** `CHANGELOG.md` (6.4.0 section)

### Verifications

- Python syntax: PASS (py_compile)
- Markdown formatting: PASS (prettier — all files clean, README.md reformatted)

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

**Factual Git Diff:** Stored in Commit Hash: `54e0fcd45fd186d817a0d5a2caea5e6bd1206934`
<!-- END_GIT_DIFF -->
