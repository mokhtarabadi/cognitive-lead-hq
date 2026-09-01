# Task 141: Monorepo Blast-Radius Analyzer & Affected Path Matrix

**File:** `tasks/backlog/141-monorepo-blast-radius-analyzer.md`
**Source:** orchestrator
**Type:** feature
**Status:** open

## Goal

Implement Monorepo Blast-Radius Analyzer in `loop-engine/blast_radius.py` that inspects changed files in a task diff and calculates the exact affected dependency matrix across monorepo packages, preventing execution of unrelated toolchain tests and scoping verification strictly to impacted modules.

## Local TODOs

- [ ] Initial codebase exploration (loop-engine models, verifier, toolchain runner)
- [ ] Define BlastRadiusMatrix + dependency mapping schemas in models.py
- [ ] Implement calculate_affected_paths() in loop-engine/blast_radius.py
- [ ] Wire blast-radius analysis into ToolchainRunner verification scoping
- [ ] Add unit tests in loop-engine/test_blast_radius.py
- [ ] Verify full test suite passes

## Acceptance Criteria

- [ ] `BlastRadiusMatrix(BaseModel)` and dependency mapping schemas defined in `models.py`.
- [ ] `loop-engine/blast_radius.py` implements `calculate_affected_paths(modified_files, workspace_root)` mapping package dependencies.
- [ ] `ToolchainRunner` uses blast-radius analysis to skip verification on completely unaffected monorepo workspaces.
- [ ] Comprehensive unit tests in `loop-engine/test_blast_radius.py` pass.
- [ ] Full test suite passes with 0 failures and 0 regressions.

## Verification Evidence

- **Test command:** `python -m pytest loop-engine/ -q`
- **Expected result:** all tests pass, 0 failures, 0 regressions
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Manager Decisions

_(Log non-trivial architectural, design, or strategic decisions here using the format from `<decision_logging_mandate>`: `**[YYYY-MM-DD] [DECISION_ID] [SOURCE]:** <summary>`.)_

## Risk & Rollback

- **Risk:** Incorrect dependency mapping may skip verification for actually affected modules (false negatives).
- **Rollback plan:** Disable blast-radius scoping via config flag and revert to full-toolchain verification.

---

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->