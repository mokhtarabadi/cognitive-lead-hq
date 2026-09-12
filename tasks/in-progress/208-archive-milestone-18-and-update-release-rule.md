# Task 208: Archive milestone 18 and update release rule

**File:** `tasks/in-progress/208-archive-milestone-18-and-update-release-rule.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Goal

Archive completed tasks into a milestone summary and make archive-on-release a permanent rule.

## Manager's Notes

Manager order (translated from Persian): archive current tasks, no new release needed, current release is fine. Re-stage if needed and fix the push script if needed. Script must create the GitHub release and keep changelogs clean. From now on every release must archive tasks. Update both memory and manager decisions.

## Local TODOs

- [x] Scan completed tasks and write milestone summary
- [x] Move completed files to archive
- [x] Update release memory with archive-on-release rule
- [x] Record manager decision for archive-on-release
- [x] Verify push script and CHANGELOG, fix if needed

## Acceptance Criteria

- [x] `docs/history/milestone-18-summary.md` exists with all completed tasks covered
- [x] `tasks/completed/` is empty, files moved to `tasks/archive/`
- [x] Release memory holds the archive-on-release rule
- [x] Manager decision recorded for archive-on-release
- [x] Push script creates tag, pushes, creates or verifies GitHub release
- [x] `lint_task_file` passes, diff staged via stage tool

## Verification Evidence

- **Test command:** `ls tasks/completed/; ls tasks/archive/ | wc -l; ls docs/history/milestone-18-summary.md`
- **Expected result:** completed empty, archive grew, summary exists
- **Actual result:** completed empty, archive 183 → 213, milestone-18 summary exists, memory stored, DEC-20260912-013 recorded, script SYNTAX_OK
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `verification-before-completion` applied and evidence recorded
- [ ] `CHANGELOG.md` updated via Parse-Then-Append (N/A: 9.31.0 section already clean, no new release cut)
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** moving 30 files at once, history reachable only via git log after move.
- **Rollback plan:** `git mv tasks/archive/<file> tasks/completed/` per file before any commit; no commit happens without approval.

---

## Execution Log & Reasoning

Scanned 30 completed files via a read-only subagent (all manager source: 16 feature, 13 improvement, 1 research). Wrote milestone-18 summary covering every task. Moved all 30 files to archive with git mv (completed now empty, archive 183 → 213). Stored the archive-on-release rule in release memory (overwrite). Recorded the manager ruling as DEC-20260912-013 with verbatim Persian quote plus English translation. Script fixes: added `git fetch --tags`, replaced `--web` view (browser opener, unsafe headless) with plain view, verify step now fails loudly when remote tag or release is missing. CHANGELOG verified clean (Unreleased empty, single Added/Changed/Fixed under 9.31.0) so no edit needed. No commit: closure approval not given for this task.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
