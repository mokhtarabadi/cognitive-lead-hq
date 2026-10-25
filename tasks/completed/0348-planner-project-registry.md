# Task 348: Auto-register projects that use the planner MCP

**File:** `tasks/completed/0348-planner-project-registry.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Estimate:** 2h
**Sprint:** S26-W44
**Milestone:** M03

## Goal

Any project whose session calls a planner MCP tool is remembered automatically, so the dashboard's project switcher lists it without editing `PLANNER_PROJECTS` by hand.

## Design

- New registry file `~/.config/opencode/planner-projects.json` (override `PLANNER_PROJECTS_REGISTRY`), shape `{"projects": ["/abs/path", ...]}` capped at the 50 most recent, written atomically.
- `_project_tool` records the resolved `project_root` after every successful tool call; failures never surface to the caller.
- `_discover_projects` merges registry entries with `PLANNER_PROJECTS` and the current root, de-duplicates, and keeps only directories that exist and hold `tasks/`; when a session is present, grants still filter the list.
- Dashboard needs no change: it renders `projects`.

## Local TODOs

- [x] Registry helpers (`_registry_path`, `_read_projects_registry`, `_register_project`) with env override, 50-entry cap, atomic write
- [x] Record the resolved root from `_project_tool` (kwargs or first positional arg), swallowing failures
- [x] Merge registry entries into `_discover_projects` before the exists/`tasks/`/grant filters
- [x] Four tests: record + dedupe, cap, registered project listed, dead path dropped

## Acceptance Criteria

- [x] Calling a planner tool from a project adds that absolute path to the registry once (idempotent)
- [x] `GET /api/status` lists a registered project without `PLANNER_PROJECTS`
- [x] Non-existent paths and paths without `tasks/` are filtered out
- [x] A viewer still sees only granted projects despite registration
- [x] Registry writes are atomic and capped at 50 entries
- [x] Full planner suite passes with exit code 0

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/test_planner_server.py -q`
- **Expected result:** 115 existing tests plus the new registry tests pass
- **Actual result:** `119 passed, 2 warnings in 41.43s` (four new registry tests)
- **Exit code:** 0

## Definition of Done

- [x] `lint_task_file` passes; `CHANGELOG.md` updated; README documents the registry
- [x] Deployed to `~/.config/opencode/mcp-planner-server/` and `mcp-planner` restarted

## Risk & Rollback

- **Risk:** a tool call with a wrong `project_root` pollutes the list; mitigated by the `tasks/` + existence filter and the 50-entry cap.
- **Rollback:** delete the registry file; discovery falls back to `PLANNER_PROJECTS` + current root.

## Execution Log & Reasoning

Autopilot task created from the Manager's question about automatic project discovery (2026-10-25).

**Implementation:** `_register_project` writes the resolved root into `~/.config/opencode/planner-projects.json` (env override, newest first, cap 50, temp + `os.replace`, all failures swallowed); `_project_tool` records the root from kwargs or the first positional arg after every call; `_discover_projects` merges the registry with `PLANNER_PROJECTS` and the current root before the exists/`tasks/`/grant filters. Verified: 119 tests pass, deployed and `mcp-planner` restarted.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `3222a7c465881be914b8758980d9ca87f13e1c6b`
<!-- END_GIT_DIFF -->
