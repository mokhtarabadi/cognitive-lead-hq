# Task 147: Automated SemVer Bump & Keep-a-Changelog Engine

**File:** `tasks/archive/147-automated-semver-and-changelog.md`
**Source:** orchestrator
**Type:** feature
**Status:** superseded
**Superseded-By:** `161-production-readiness-bundle`
**Superseded-At:** `2026-09-04`

## Goal

Implement automated release management in `loop-engine/release.py` that parses closed task types (feature, fix, breaking), calculates the next SemVer version, automatically writes release entries to `CHANGELOG.md`, and creates annotated Git tags upon milestone closure.

## Local TODOs

- [ ] Initial codebase exploration (daemon.py closure lifecycle, CHANGELOG.md format)
- [ ] Implement ReleaseEngine in loop-engine/release.py with SemVer calculation
- [ ] Implement Keep-a-Changelog parsing and release entry generation
- [ ] Wire annotated Git tag creation on milestone closure
- [ ] Add unit tests in loop-engine/test_release.py
- [ ] Verify full test suite passes

## Acceptance Criteria

- [ ] `ReleaseEngine` in `loop-engine/release.py` with SemVer calculation and Keep-a-Changelog parsing.
- [ ] Unit tests in `loop-engine/test_release.py` pass.
- [ ] Full test suite passes with 0 failures.

## Verification Evidence

- **Test command:** `python -m pytest loop-engine/ -q`
- **Expected result:** all tests pass, 0 failures
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Automated Git tag creation conflicts with the repo's Zero-Autonomous-Commit policy.
- **Rollback plan:** Keep tag creation opt-in behind a config flag and log the intended tag instead.

---

> **Superseded:** This task was bundled into META task `161-production-readiness-bundle` and archived on 2026-09-04. See `tasks/backlog/161-production-readiness-bundle.md` (or its Kanban successor) for the unified execution. History preserved via `git log --follow -- tasks/archive/147-automated-semver-and-changelog.md`.

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->