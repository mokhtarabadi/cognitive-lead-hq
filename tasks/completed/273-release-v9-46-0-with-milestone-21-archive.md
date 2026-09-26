# Task 273: Release v9.46.0 with milestone-21 archive

**File:** `tasks/completed/273-release-v9-46-0-with-milestone-21-archive.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Cut release v9.46.0: archive completed tasks 266-272 into docs/history/milestone-21-summary.md, move CHANGELOG [Unreleased] under ## [9.46.0] - 2026-09-26, run all verification gates, generate the Manager-run push script.

## Manager's Notes

Direct Manager order: "load everything from memory and skills to make a new release." Follow memory release/release-workflow exactly: versioning-and-release + project-memory + verification-before-completion + task-lint skills loaded; archive-on-release mandatory; system-prompt.md already at 9.46.0 (tasks 268-271 bumped it, no hand-edit); [Unreleased] must be empty after release; ZAC holds (stage via MCP, commit via MCP after approval, tag/push/release via generated script run by Manager).

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Archive tasks 266-272 to docs/history/milestone-21-summary.md, git mv to tasks/archive/
- [x] Stale-memory audit report (flag only, no auto-delete)
- [x] Move CHANGELOG [Unreleased] entries under ## [9.46.0] - 2026-09-26, leave [Unreleased] empty
- [x] Run verification gates (lint_task_file, lint_markdown, lint_system_prompt_sync, py_compile, full pytest, check_docs_sync.py)
- [x] Generate /tmp/cognitive-lead-push-release.sh (VERSION=v9.46.0, chmod +x)
- [x] Stage via custom_context_stage_and_inject_diff, verify functionality

## Acceptance Criteria

- [x] AC1: docs/history/milestone-21-summary.md compacts tasks 266-272 and all 7 files are moved to tasks/archive/ (archive step mandatory per release memory)
- [x] AC2: CHANGELOG has ## [9.46.0] - 2026-09-26 with all prior [Unreleased] entries moved; [Unreleased] section empty; system-prompt.md version unchanged statement accurate (already built at 9.46.0)
- [x] AC3: all verification gates pass with exit code 0 and evidence recorded (pytest suite, lint_task_file, lint_markdown on edited files, lint_system_prompt_sync in sync, check_docs_sync.py OK)
- [x] AC4: /tmp/cognitive-lead-push-release.sh exists, executable, starts with set -euo pipefail, defines VERSION=v9.46.0, verifies clean tree + gh auth, creates annotated tag if missing, pushes commits + tags, creates or verifies GitHub release
- [x] AC5: stale-memory report produced and attached; no memory deleted without Manager approval

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pathspec pytest tests/ -q
- **Expected result:** full suite passes, exit code 0
- **Actual result:** 689 passed, 10 warnings in 5.02s; lint_task_file pass (273, post-move path); lint_markdown pass (milestone-21-summary.md, CHANGELOG.md); prompt re-assembly byte-identical (system-prompt.md untouched, in sync at 9.46.0); py_compile pass; check_docs_sync.py: docs-sync OK (2 warn-only orphans)
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** archive move or CHANGELOG rewrite loses task history or misattributes entries
- **Rollback plan:** history stays reachable via git log --follow on tasks/archive/; CHANGELOG edit is a single working-tree hunk revertible with git checkout before staging

---

## Execution Log & Reasoning

Release v9.46.0 executed per memory release/release-workflow (skills: versioning-and-release, project-memory, verification-before-completion, task-lint, archive-tasks, task-generator). Seat check: single-domain release ceremony → Code Reviewer at QA, no Brain planning round (release task follows the standing memory procedure, Brainstorm: not required — mechanical ceremony, fully reversible via git).
Milestone-21 draft delegated to a general subagent (7 files, 1054 lines) to preserve context; verified its claims by grep: sources 7x manager, types 1x feature + 6x improvement, AC boxes all checked, one wart found — task 271's Local TODO section left unchecked (8 boxes) while its AC went 6/6 checked; sealed file untouched, wart recorded honestly in the milestone Criteria Met row. Archive via `git mv` (tracked files, exit 0); completed/ verified empty. CHANGELOG: inserted `## [9.46.0] - 2026-09-26` + ceremony bullet between `[Unreleased]` and `### Added` (Parse-Then-Append, no dup headers; the `### Fixed` block below belongs to released 9.41.0, untouched). `lint_system_prompt_sync` MCP resolved the wrong root (global install) so sync was proven by direct re-assembly: byte-identical, zero diff. Push script written per memory spec (strict mode, VERSION=v9.46.0, clean-tree + gh auth preflight, tag-if-missing, push commits + tags, create-or-verify release), chmod +x, `bash -n` syntax OK.
Closure (2026-09-26): Manager ordered "close it" directly. No Brain review verdict was obtained for this task (review step skipped per explicit Manager order — recorded honestly, not backfilled). File moved tasks/qa/ → tasks/completed/ via git mv, header + Status synced, re-linted, re-staged, committed via commit_and_clean_task. Next: Manager re-runs /tmp/cognitive-lead-push-release.sh (it aborted earlier on dirty-tree preflight, which was correct), then tells me to restart OpenCode.

## Stale Memory Report

Searched project memory for task-number references (266-272), V1 leftovers (1.18/tui.json), and stacks/loop-engine: zero hits on all three queries. No stale or superseded entries flagged. No memory deleted (approval gate preserved).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `d86db30b59e4daff10a5f1f567c472b10fc3437e`
<!-- END_GIT_DIFF -->
