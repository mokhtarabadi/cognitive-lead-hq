# Task 339: Planner dashboard UI/UX overhaul and full-screen task modal

**File:** `tasks/backlog/0339-planner-dashboard-ui-overhaul-and-task-modal.md`
**Source:** manager
**Type:** feature
**Status:** open
**Estimate:** 1.5h
**Sprint:** S26-W43
**Milestone:** M01

## Source Context

### Variant C: Manager (`**Source:** manager`)

## Goal

Revamp the Planner dashboard UI/UX to eliminate vertical clutter and enhance task visibility: cap lane heights with inner scroll and sticky headers, collapse the 320+ item Archive lane by default with a count toggle, add live search filtering, add a backend `GET /api/task` endpoint, and add a polished full-screen modal with standalone Markdown rendering so clicking any task reveals its complete content, todos, acceptance criteria, and Git diff.

## Manager's Notes

- The archive list currently stretches the page too far; it must be collapsed by default with an expand toggle showing the item count.
- Lanes need a fixed viewport height with clean internal scrolling and sticky card headers.
- A search input at the top of the board should instantly filter tasks across lanes by ID or title.
- Clicking any task card (or an inspect button) must open an aesthetic full-screen modal that renders the task file's Markdown cleanly (including `## Factual Git Diff`) without third-party build tooling.
- Zero external CDN dependencies: keep assets self-contained in `mcp-planner-server/static/`.

## Local TODOs

- [ ] Add `GET /api/task` endpoint in `mcp-planner-server/server.py` returning the raw Markdown content of a task file by path or ID (auth and project-scoping enforced)
- [ ] Update `mcp-planner-server/static/index.html` with capped lane heights (`max-height: calc(100vh - 280px); overflow-y: auto`) and sticky card headers
- [ ] Implement collapsible Archive drawer in `index.html` (collapsed by default with toggle button)
- [ ] Add live search filter bar above Kanban lanes
- [ ] Implement full-screen Task Detail Modal (`#task-modal`) with embedded lightweight Markdown rendering (pure JS / self-contained) for task body and diff
- [ ] Write unit tests for `GET /api/task` in `tests/test_planner_server.py`
- [ ] Deploy updated files to `~/.config/opencode/mcp-planner-server/` and restart `mcp-planner`
- [ ] Update `CHANGELOG.md` and verify `lint_task_file`

## Acceptance Criteria

- [ ] `GET /api/task?path=tasks/...` returns the task Markdown or 403/404 when unauthorized or missing
- [ ] Kanban lanes on the dashboard are height-capped with internal vertical scrolling and sticky headers
- [ ] Archive lane is collapsed by default and displays a toggle button with the task count
- [ ] Search input instantly filters visible cards by task ID or title without server round-trip
- [ ] Clicking a task opens a full-screen dark-mode modal displaying rendered Markdown of the task and its diff
- [ ] Zero external CDN network dependencies: markdown parser is self-contained in `static/`
- [ ] Full planner test suite passes with exit code 0

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/test_planner_server.py -q`
- **Expected result:** All planner tests pass including new `/api/task` tests
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

## Definition of Done

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Large task files or diffs might lag modal rendering.
- **Mitigation:** Use a lightweight, synchronous, pure JS markdown parser and cap max rendered lines if needed.
- **Rollback plan:** Revert `index.html` and `server.py` changes.

## Execution Log & Reasoning

Created by Project Planner / Senior Programmer per Manager directive.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

<!-- END_GIT_DIFF -->
