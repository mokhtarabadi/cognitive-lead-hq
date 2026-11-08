# Task 0365: Fix dashboard CFD/control chart initial load ordering

**File:** `tasks/completed/0365-fix-dashboard-cfd-control-chart-init.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Finished:** 2026-11-01T06:22:04Z
**Submitted:** 2026-11-01T06:21:35Z

## Goal

Fix the dashboard so CFD and control chart load after project_root is resolved, avoiding "unavailable" on initial load.

## Local TODOs

- [x] Fix init ordering
- [x] Verify JS syntax

## Acceptance Criteria

- [x] loadCFD/loadControlChart called after fetchStatus resolves
- [x] JS syntax valid

## Verification Evidence

- **Test command:** node --check on extracted script
- **Expected result:** no syntax errors
- **Actual result:** JS OK
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Low.
- **Rollback plan:** Revert init change.

---

## Execution Log & Reasoning

Fixed dashboard init ordering: loadCFD/loadControlChart now run after fetchStatus resolves currentProject. Also added load calls on project change.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `71522101389c12f654f1757542a767ac31d753e9`
<!-- END_GIT_DIFF -->
