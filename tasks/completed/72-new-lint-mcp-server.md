# Task 72: New Lint MCP Server

**File:** `tasks/backlog/72-new-lint-mcp-server.md`
**Source:** orchestrator
**Type:** feature
**Status:** closed

## Source Context

### Variant A: Orchestrator (`**Source:** orchestrator`)

## Goal

Create a new `mcp-lint-server` to validate Markdown formatting and task file structure, register it in global and local configs, create a companion `task-lint` skill, and update the system prompt registry.

## Blueprint Reference

V8.0.0 Improvement Roadmap Phase 3

## Manager's Notes

This is a new MCP server that provides structural linting tools for Markdown files and the canonical task file template. It should be lightweight, regex-based, and follow the exact patterns of the existing MCP servers (`mcp-context-server`, `mcp-memory-server`).

## Local TODOs

- [x] Phase 1: Create Task File
- [x] Phase 2: Create `mcp-lint-server/server.py` with lint_markdown, lint_task_file, lint_all_tasks tools
- [x] Phase 3: Register lint server in `opencode.json` and `LLM.txt`
- [x] Phase 4: Create `task-lint` skill template
- [x] Phase 5: Update `system-prompt.md` (skill registry + version bump)
- [x] Phase 6: Verification (Python syntax, JSON syntax)

---

## OpenCode Execution Log & Reasoning

### Architectural Decisions

**Why a separate MCP server?** The `mcp-lint-server` follows the same single-responsibility pattern as `mcp-context-server` (file reading) and `mcp-memory-server` (project memory). Each MCP server owns one concern. Linting is distinct enough from context gathering and memory to warrant its own server.

**Why regex-based checks?** The existing MCP servers use only `mcp[cli]>=1.0,<2.0` as their sole dependency. Adding `markdown` or `commonmark` would introduce a heavy dependency tree. Regex covers the most critical structural rules (heading spacing, trailing whitespace, task template compliance) while keeping the server lightweight and matching the pattern of `mcp-context-server` which also uses regex for signature extraction.

**Why three tools?** The tool surface mirrors how linting is used in practice:
- `lint_markdown` — general-purpose Markdown linting (CHANGELOG, SKILL.md, README)
- `lint_task_file` — task-specific structural validation (ID match, required sections, markers)
- `lint_all_tasks` — batch validation for the archive-tasks workflow

### Files Created/Modified

| File | Action | Purpose |
|------|--------|---------|
| `mcp-lint-server/server.py` | **Created** | New MCP server with 3 lint tools |
| `opencode.json` | **Modified** | Added `lint` MCP server config + permissions |
| `LLM.txt` | **Modified** | Added lint server to global setup (mkdir, copy, JSON payload) |
| `skill-templates/task-lint/SKILL.md` | **Created** | Companion skill for the lint server |
| `system-prompt.md` | **Modified** | Added `task-lint` to agent_skills_registry; bumped version to 7.4.0 |

### Verification

- `python3 -m py_compile mcp-lint-server/server.py` — ✅ passed
- `python3 -c "import json; json.load(open('opencode.json'))"` — ✅ passed

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `354b1e3d21ac8214636237d3213ee11578f5b0ee`
<!-- END_GIT_DIFF -->
