# Task 92: Archive Zombies and Scope Lint

**File:** `tasks/completed/92-archive-zombies-and-scope-lint.md`
**Source:** manager
**Type:** chore
**Status:** closed

## Source Context

### Variant C: Manager (`**Source:** manager`)

## Goal

Implement the F3 finding from Task 87 in two parts: (1) archive the 6 zombie tasks (10, 11, 12, 13, 25, 30) — fully completed work items that were never closed and still sit in `tasks/backlog/` — moving them to `tasks/archive/`; (2) scope `lint_all_tasks` in `mcp-lint-server/server.py` to exclude `tasks/archive/` from the default scan (archive is a historical record; linting it produces noise — 388 issues across 87 files, mostly archive), with an optional `include_archive` flag.

## Manager's Notes

- Zombie verification (discovery phase): all 6 files have `## OpenCode Execution Log & Reasoning` sections documenting completed work; their changes are confirmed merged in the codebase (task-generator instruction in Project Planner persona; Project Skill Loading in system-prompt `<constraints>`; skill-loading rules in AGENTS.md + audit-agents criteria; `telegram-message-export` skill exists in skill-templates/ + global; `<validation_phase>` present in all 3 XML templates; prettier formatting pass applied repo-wide). All 6 are git-tracked, so `git mv` works.
- F3 root cause: `lint_all_tasks` scans `tasks/archive/` too, so the whole-repo health gate always reports hundreds of historical-format violations and agents learn to ignore it.
- No system-prompt version bump in this task (no system-prompt.md edit). NOTE for Reviewer: the `versioning-and-release` skill suggests a bump when MCP servers change — the Orchestrator did not instruct one here; flagged in the execution log.
- CHANGELOG entries go under existing `## [Unreleased]` → `### Changed` (Parse-Then-Append).

## Local TODOs

- [x] Step 1: Create this task file (ID discovery → 92), move to `tasks/in-progress/` (filesystem `mv` — untracked)
- [x] Step 2: Archive 6 zombie tasks (10, 11, 12, 13, 25, 30) from `tasks/backlog/` to `tasks/archive/` via `git mv`
- [x] Step 3: Fix F3 — `lint_all_tasks` excludes `tasks/archive/` by default; optional `include_archive` flag; comment added
- [x] Step 4: Update `CHANGELOG.md` — `[Unreleased]` → `### Changed`: 2 entries (zombie archive + lint scoping)
- [x] Step 5: Syntax verification (py_compile + pytest + lint + ls checks)

## Acceptance Criteria

- [x] `tasks/archive/` contains exactly 6 new files matching `10-|11-|12-|13-|25-|30-`
- [x] `tasks/backlog/` contains exactly 3 files (86, 87, 88)
- [x] `lint_all_tasks` default scan excludes `tasks/archive` (verified by code + direct module run)
- [x] `CHANGELOG.md` `[Unreleased]` → `### Changed` has both entries, no duplicates
- [x] `pytest` passes (14); `py_compile` OK
- [x] Task file passes `lint_task_file`

## Verification Evidence

- **Test command:** `uv run --with pytest ... pytest tests/test_mcp_servers.py -q` ; `ls tasks/archive/ | grep -E "10-|11-|12-|13-|25-|30-"` ; `ls tasks/backlog/ | wc -l` ; `lint_task_file tasks/in-progress/92-archive-zombies-and-scope-lint.md` ; live `lint_all_tasks` run
- **Expected result:** 14 passed; 6 archive matches; backlog count 3; lint ✅; `lint_all_tasks` reports active dirs only
- **Actual result:** `14 passed, 9 warnings in 1.10s`; archive grep → 6 matches; backlog → 3 (86/87/88); `py_compile` → ✅; task lint → ✅ passed; NEW `lint_all_tasks()` (direct module invocation, since the running MCP server still holds pre-restart code) → **"Scanned 11 task files. Found 0 total issues. ✅ All task files are perfectly formatted."** (backlog 3 + in-progress 1 + completed 7 + qa 0); `lint_all_tasks(include_archive=True)` → 93 files / 388 issues (historical noise, expected)
- **Exit code:** 0 (pytest, py_compile, greps); 0 (lint)

## Risk & Rollback

- **Risk:** (1) Archive numbering interleaving (10–13, 25, 30 fill gaps in the 01–81 sequence) — acceptable, matches existing archive naming. (2) `include_archive` flag changes MCP tool schema — backward-compatible optional param (default False). (3) CHANGELOG duplicates — Parse-Then-Append. (4) If a zombie turns out NOT to be merged, it must be un-archived — mitigated by the discovery-phase verification above.
- **Rollback plan:** `git mv` the 6 files back to `tasks/backlog/`; revert the `lint_all_tasks` scoping change; remove the 2 CHANGELOG bullets.

---

## OpenCode Execution Log & Reasoning

### What was done

1. **Discovery phase:** generated `context-reports/context_report_20260811_001057.md` (AGENTS.md + conventions.md) and `context-reports/tree_report_20260811_001057_317d84db.md`; verified all 6 zombie files are git-tracked, carry completed Execution Logs, and their changes are confirmed merged (Project Planner task-generator instruction; Mandatory Project Skill Loading constraint; AGENTS.md/audit-agents skill-loading rules; `telegram-message-export` skill in templates + global; `<validation_phase>` in all 3 XML templates; prettier formatting pass). Conditional implementation condition satisfied.
2. **Zombie archive:** `git mv` of tasks 10, 11, 12, 13, 25, 30 from `tasks/backlog/` → `tasks/archive/` (all tracked, so git history preserved). `tasks/backlog/` now holds exactly 86/87/88.
3. **F3 fix — `mcp-lint-server/server.py` `lint_all_tasks`:** signature extended to `lint_all_tasks(include_archive: bool = False)`; default scan list reduced to `["backlog", "in-progress", "qa", "completed"]` with the F3 comment; `include_archive=True` appends `archive`. Docstring updated.
4. **`CHANGELOG.md`:** 2 bullets appended under `[Unreleased]` → `### Changed` (Parse-Then-Append; no duplicates).

### Architectural reasoning

- **The archive is a historical record, not a health signal.** Linting it against today's template contract conflates "the repo is healthy" with "100+ old-format files predate the template". Scoping the default to active directories turns `lint_all_tasks` from a noise wall (388 issues) into a real gate: **11 active files, 0 issues** — exactly the anti-lazy behavior the workflow wants.
- **Optional `include_archive=True`** preserves the capability for explicit historical audits without polluting the default signal (YAGNI-compatible: the flag costs one boolean).
- **Zombie root cause (why they existed):** tasks 10–30 predate the enforced closure loop (Task 26's approval loop, Task 45's V6 lifecycle); nothing at the time forced completed-but-never-closed files out of backlog. The `archive-tasks` skill + closure protocol now prevent recurrence; the zombie detector idea from Task 87 F3 (CI gate) remains a future F8 candidate.
- **Version note (flagged for Reviewer):** this task modifies an MCP server but the Orchestrator did not instruct a system-prompt bump; per `versioning-and-release` the next release/archive milestone should consider bumping for the lint-server change. No system-prompt.md edit was made here.

### Verification notes

- The RUNNING MCP lint server still executes pre-restart code (live `lint_all_tasks` call returned the old 93-file scan). The new behavior was verified by direct module invocation under `uv run` (default → 11 files / 0 issues; include_archive=True → 93 / 388). **A restart is required for the deployed server to pick up the new behavior** — same known limitation as the context server in Task 90.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `05a4bffa4e268cb31da905d7698e8c5e4b3d2844`
<!-- END_GIT_DIFF -->