# Task 0386: Release v9.77.0 with milestone-24 archive

**File:** `tasks/completed/0386-release-v9-77-0-with-milestone-24-archive.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Finished:** 2026-11-15T07:49:25Z
**Submitted:** 2026-11-08T12:08:23Z

## Goal

Cut release v9.77.0 (MINOR: system-prompt audit cleanup, brain output persistence, manual/auto mode decoupling, comprehensive repo audit) with milestone-24 archive of all completed tasks, per release/release-workflow memory.

## Manager's Notes

Direct order: "load everything from memory about new release, step by step follow them". Release memory retrieved and followed: skills loaded (versioning-and-release, project-memory, verification-before-completion, task-lint, archive-tasks), SemVer confirmed MINOR (new workflow capabilities, non-breaking), archive-on-release enforced, CHANGELOG Parse-Then-Append with empty Unreleased after release, system-prompt bump plus reassemble, full verification gates, ZAC-safe push script at /tmp/cognitive-lead-push-release.sh for manual Manager execution.

Scope: bump `prompts/fragments/01-system_version.md` 9.76.0 to 9.77.0 (already done), update `tests/test_prompt_sync.py` version pin (already done), reassemble `system-prompt.md`, move Unreleased entries under `## [9.77.0]`, archive 36 completed tasks with `docs/history/milestone-24-summary.md` via archive-tasks skill, generate push script, run all gates.

## Local TODOs

- [x] Archive completed tasks with milestone-24 summary (archive-tasks skill)
- [x] Bump system version fragment and reassemble prompt
- [x] Move CHANGELOG Unreleased entries under 9.77.0 header
- [x] Update version pin in tests and run full verification gates
- [x] Generate push script at /tmp/cognitive-lead-push-release.sh
- [x] Verify functionality

## Acceptance Criteria

- [x] `tasks/completed/` empty after archive; `docs/history/milestone-24-summary.md` exists; sources in `tasks/archive/`
- [x] `system-prompt.md` carries 9.77.0, sync green, byte-identical rebuild
- [x] `CHANGELOG.md` has `## [9.77.0]` with all entries; `## [Unreleased]` empty
- [x] Push script exists at /tmp/cognitive-lead-push-release.sh, executable, starts with `set -euo pipefail`, never executed by Hands
- [x] All verification gates green (lint_task_file, lint_markdown, lint_system_prompt_sync, py_compile, full pytest, check_docs_sync.py)

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/ -q
- **Expected result:** all tests pass with exit code 0
- **Actual result:** 826 passed, 24 warnings
- **Exit code:** 0
- **Test command:** python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/sp_check.md
- **Expected result:** sync green, byte-identical rebuild
- **Actual result:** SYNC_OK
- **Exit code:** 0
- **Test command:** python3 scripts/check_docs_sync.py
- **Expected result:** docs-sync OK
- **Actual result:** docs-sync: OK
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Large archive move could conflict with other tasks
- **Rollback plan:** git mv tasks/archive/<id>-*.md tasks/completed/

---

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `b810b755cc8099da3520860104485de7cda09a7e`
<!-- END_GIT_DIFF -->
