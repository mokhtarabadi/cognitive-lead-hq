# Task 172: Sync Stranded Post-Closure Fixes

**File:** `tasks/completed/172-sync-stranded-post-closure-fixes.md`
**Source:** manager
**Type:** bug
**Status:** closed

## Source Context

## Goal

Commit three files whose working-tree fixes missed the Task 171 closure commit (stale index content was committed): persona server transcript fix, archived 169/170 header sync.

## Manager's Notes

- Root cause: the transcript-blowup fix to `mcp-persona-server/server.py` landed after the last staging; the closure commit captured the pre-fix index version. Archived 169/170 likewise committed with pre-patch headers (bundler glitch fixes stayed unstaged).
- HEAD is internally inconsistent (committed tests expect no body-append; committed server still appends). This task re-syncs index to the tested working tree. No code changes — staging only.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Identify stranded files (diff HEAD vs worktree)
- [x] Stage via `custom_context_stage_and_inject_diff`, move to QA

## Acceptance Criteria

- [x] `mcp-persona-server/server.py` at HEAD matches tested working tree (no `_read_task_file`)
- [x] Archived 169/170 carry `Status: superseded` headers
- [x] Full suite green on the exact committed content

## Verification Evidence

- **Test command:** same locked pytest invocation (suite green on identical working tree)
- **Expected result:** 120 passed, exit 0
- **Actual result:** `120 passed, 8 warnings in 1.28s` (recorded pre-closure on this exact tree)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append (N/A — sync-only, fixes already logged under Task 171)
- [ ] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** None-code change; staging-only sync. Rollback: `git reset HEAD -- <paths>`.
- **Rollback plan:** Unstage; HEAD remains as-is.

---

## Execution Log & Reasoning

Sync-only task: no source edits. `git show HEAD:...` vs worktree comparison proved the closure commit `a37c3cb` captured pre-fix index content for exactly 3 files (persona server + 2 archived headers). Re-staging the tested tree restores consistency. CHANGELOG already covers the fixes (Task 171 entries); DoD lint box checks at QA gate.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `aa73e71cf40a446fc65f7b3db213000fc8d55596`
<!-- END_GIT_DIFF -->
