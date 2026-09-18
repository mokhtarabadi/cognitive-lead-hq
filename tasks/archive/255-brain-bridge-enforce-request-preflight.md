# Task 255: Brain Bridge - enforce request preflight before transport

**File:** `tasks/archive/255-brain-bridge-enforce-request-preflight.md`
**Source:** manager
**Type:** bug
**Status:** superseded
**Superseded-By:** `257-github-open-issues-bundle`
**Superseded-At:** `2026-09-18`

## Goal

Validate structured bridge requests locally before any transport call so incomplete requests are rejected early.

## Manager's Notes

Direct manager order (English, verbatim): "load all issues (status: open) from github https://github.com/mokhtarabadi/cognitive-lead-hq/issues create a metatask of all"

GitHub source: `https://github.com/mokhtarabadi/cognitive-lead-hq/issues/18` (state at capture: OPEN, 2026-09-18).

Synced from GitHub issue 18 verbatim body plus title. Implementation must resolve the issue and keep the task file in sync with the GitHub issue.

## Local TODOs

- [ ] Fetch full issue 18 body and comments via gh api
- [ ] Implement mandatory preflight validation with no silent working-directory default
- [ ] Verify functionality

## Acceptance Criteria

- [ ] Bridge validates project_root, task_id or session_id, Kanban path, stage, include_bundle, include_diff when required
- [ ] Incomplete requests rejected before any transport call
- [ ] No silent working-directory default

## Verification Evidence

- **Test command:** rtk test pytest tests/ -q
- **Expected result:** all tests pass with exit code 0
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

> Verification runner rule: `pytest tests/ -q` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** strict preflight could reject valid edge-case requests
- **Rollback plan:** relax validation to warning-only mode

---

> **Superseded:** This task was bundled into META task `257-github-open-issues-bundle` and archived on 2026-09-18. See `tasks/backlog/257-github-open-issues-bundle.md` (or its Kanban successor) for the unified execution. History preserved via `git log --follow -- tasks/archive/255-brain-bridge-enforce-request-preflight.md`.

## Execution Log & Reasoning

Created from GitHub issue 18 (OPEN) on 2026-09-18. Standing order cited: FULL AUTOMATIC MODE (manager/full_automatic_mode, 2026-09-17) — zero questions, decide from stored rulings and continue. Assumption A1: Source manager is correct for GitHub-synced direct order. Assumption A2: Type bug matches avoidable transport failures.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
