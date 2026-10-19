# Task 284: Release v9.49.0 with milestone-22 archive

**File:** `tasks/completed/284-release-v9-49-0-with-milestone-22-archive.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Cut release v9.49.0: archive completed tasks 273-283 (9 files) into `docs/history/milestone-22-summary.md`, move CHANGELOG `[Unreleased]` under `## [9.49.0] - 2026-10-01`, run all release verification gates, and generate the Manager-run push script.

## Manager's Notes

Direct Manager order: "load all memory about release workflow and do a release." Follow memory `release/release-workflow` exactly: skills versioning-and-release + project-memory + verification-before-completion + task-lint (+ task-generator, archive-tasks) loaded; archive-on-release mandatory; `system-prompt.md` already at 9.49.0 (tasks bumped it, no hand-edit); `[Unreleased]` must be empty after release; ZAC holds (stage via MCP, commit via MCP after approval, tag/push/release via the generated script run by the Manager).

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Archive completed tasks to `docs/history/milestone-22-summary.md`, `git mv` to `tasks/archive/`
- [x] Stale-memory audit report (flag only, no auto-delete)
- [x] Move CHANGELOG `[Unreleased]` entries under `## [9.49.0] - 2026-10-01`, leave `[Unreleased]` empty
- [x] Run verification gates (lint_task_file, lint_markdown, lint_system_prompt_sync, py_compile, full pytest, check_docs_sync.py)
- [x] Generate `/tmp/cognitive-lead-push-release.sh` (VERSION=v9.49.0, chmod +x)
- [x] Stage via `custom_context_stage_and_inject_diff`, verify functionality

## Acceptance Criteria

- [x] AC1: `docs/history/milestone-22-summary.md` compacts the completed tasks and all files are moved to `tasks/archive/` (archive step mandatory per release memory)
- [x] AC2: CHANGELOG has `## [9.49.0] - 2026-10-01` with all prior `[Unreleased]` entries moved; `[Unreleased]` section empty; the system-prompt.md version-unchanged statement is accurate (already built at 9.49.0)
- [x] AC3: all verification gates pass with exit code 0 and evidence recorded (pytest suite, lint_task_file, lint_markdown on edited files, lint_system_prompt_sync in sync, py_compile, check_docs_sync.py OK)
- [x] AC4: `/tmp/cognitive-lead-push-release.sh` exists, executable, starts with `set -euo pipefail`, defines `VERSION=v9.49.0`, verifies clean tree + gh auth, creates annotated tag if missing, pushes commits + tags, creates or verifies the GitHub release
- [x] AC5: stale-memory report produced and attached; no memory deleted without Manager approval

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pathspec pytest tests/ -q
- **Expected result:** full suite passes, exit code 0
- **Actual result:** 689 passed, 10 warnings in 5.57s (exit 0) after fixing 9 pre-existing failures. Gates: `lint_task_file` pass; `lint_markdown` pass (`CHANGELOG.md`, `docs/history/milestone-22-summary.md`); `lint_system_prompt_sync` "in sync" plus re-assembly byte-identical; `py_compile` OK; `check_docs_sync.py` "docs-sync: OK". Archive: 9 completed tasks moved to `tasks/archive/`, `tasks/completed/` empty. Push script `/tmp/cognitive-lead-push-release.sh` chmod +x, `bash -n` OK, `VERSION=v9.49.0`.
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
- **Rollback plan:** history stays reachable via `git log --follow` on `tasks/archive/`; the CHANGELOG edit is a single working-tree hunk revertible before staging

---

## Execution Log & Reasoning

Release v9.49.0 executed per memory `release/release-workflow`. Seat check: single-domain release ceremony → Senior Programmer; Designer/Architect/QA/Reviewer/Planner/Strategist skipped (no UI, no new contracts, planning stage only). Brainstorm: not required — deterministic standing release procedure, fully reversible via git. Planner: no Brain planning round, matching the prior release ceremony, which follows the stored SOP.

Milestone-22 draft delegated to a general subagent (9 files: 273, 274, 275, 276, 279, 280, 281, 282, 283; source split 0 orchestrator / 2 telegram / 7 manager); verified by grep (exactly 9 `### Task` sections, correct distribution) and `lint_markdown` pass. Archive via `git mv tasks/completed/*.md tasks/archive/` (tracked files, exit 0); `tasks/completed/` verified empty.

CHANGELOG: inserted `## [9.49.0] - 2026-10-01` between `[Unreleased]` and the prior entries (Parse-Then-Append, no duplicate headers) plus the release-ceremony bullet; `[Unreleased]` is now empty; `system-prompt.md` version unchanged (already built at 9.49.0).

Pre-release gate triage: the suite was RED at HEAD with 9 pre-existing failures unrelated to the release (Manager approved fixing them first). Causes and fixes: (1) `test_prompt_sync` pinned `9.47.0` while the shipped prompt is `9.49.0` — pin updated to `9.49.0`; (2) 6 `test_mcp_servers.py` tree tests broke on the Task 279 client-visible `WARNING [project-isolation]` prefix because they omit `project_root` — added a `_tree_result` helper that strips the warning while preserving each test's cwd-fallback intent; (3) `test_authority_retrieval` expected stale arg lists — added `project_root` to both (`search_memory`, `query_manager_decisions`); (4) `test_decision_server` expected `record_manager_decision` to raise on a file-path store, but the MCP tool catches the error and returns an `Error:` string (fail-closed) — the test now asserts the clear string plus an empty store. No production code changed.

Final gates (post-change): full suite **689 passed exit 0**; `lint_task_file` pass; `lint_markdown` pass (`CHANGELOG.md`, `docs/history/milestone-22-summary.md`); `lint_system_prompt_sync` in sync + re-assembly byte-identical; `py_compile` OK; `check_docs_sync.py` "docs-sync: OK".

Push script `/tmp/cognitive-lead-push-release.sh` written per memory spec (`set -euo pipefail`, `VERSION=v9.49.0`, clean-tree + `gh auth` preflight, tag-if-missing, push commits + tags, create-or-verify GitHub release), `chmod +x`, `bash -n` OK. Next: stage via MCP, then Manager closure approval, then the Manager runs the push script.
Closure 2026-10-01: Manager replied "Approved for closure" (exact accept phrase). Status set closed; file moved `tasks/qa/` → `tasks/completed/` via `git mv` (exit 0); `**File:**` header synced; committed via `custom_context_commit_and_clean_task`. Remaining Manager step: run `/tmp/cognitive-lead-push-release.sh` (tag v9.49.0, push commits + tags, create GitHub release).

## Stale Memory Report

Released-task and superseded-workflow scan (archive-tasks step 6, flag-only):
- `workflows/global-install-upgrade` — FLAGGED (re-confirmed from the earlier audit). Its 2026-09-09 note claims persona + manager_decisions servers are DISABLED and that server code dirs are KEPT; in fact `mcp-persona-server/` was deleted and manager_decisions is an enabled MCP server. Awaiting Manager approval to correct; not deleted.
- No hits for `loop-engine`, `stacks`, or V1-migration leftovers; `opencode_config/opencode_v2_upgrade_2026_09_26` is current (refreshed 2026-10-01).
No memory deleted (approval gate preserved).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `a0b83a976cd11631f4d249879249dece44b0ad0b`
<!-- END_GIT_DIFF -->
