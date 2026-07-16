# Task 46: Implement Adversarial QA Persona

**File:** `tasks/in-progress/46-implement-qa-persona.md`
**Type:** improvement
**Status:** closed

## Goal

Upgrade the repository to V6.1.0 by introducing the Adversarial QA Engineer persona into `system-prompt.md`, updating the execution workflow to a 7-step process, and improving the handover instructions to prevent human workflow errors.

## Manager's Notes

- QA Engineer persona goes after Project Planner and before Code Reviewer in `<personas>`.
- Execution workflow expands from 6 steps to 7, inserting Adversarial QA before Team Review.
- Summary phase handover instructions must differentiate between logic tasks (send to QA) and docs/CSS tasks (send directly to Code Reviewer).

## Local TODOs

- [x] Step 1: Scaffold task file
- [x] Step 2: Update `system-prompt.md` — bump version to 6.1.0 + add QA Engineer persona
- [x] Step 3: Update `system-prompt.md` — 7-step workflow & summary phase handover
- [x] Step 4: Update `README.md` — operation steps + strike roadmap item #8
- [x] Step 5: Update `CHANGELOG.md` for [6.1.0]
- [x] Run `npx prettier --write "**/*.md"`

## OpenCode Execution Log & Reasoning

**Architectural Reasoning:** This upgrade introduces the Adversarial QA Engineer persona as a dedicated gate between implementation and code review. The key architectural insight is that the Code Reviewer traditionally checked for formatting/architectural compliance but not adversarial edge cases. By inserting a QA Engineer persona with an explicit "try to break it" mindset, the workflow catches null-pointer bugs, race conditions, and missing negative tests before the architectural review. The 6-step workflow was expanded to 7 steps, with the QA step (Step 4) sitting between implementation and team review. The summary phase handover instructions now differentiate between logic tasks (which require QA) and documentation/CSS tasks (which can skip directly to Code Reviewer), preventing workflow friction for trivial changes. The README was updated with a QA Loop description in the How to Operate section, and roadmap item #8 was struck through as implemented.

**Files Modified:**

1. **`system-prompt.md`** — `<system_version>` bumped from 6.0.0 to 6.1.0. QA Engineer persona block inserted after Project Planner and before Code Reviewer. Execution workflow expanded to 7 steps with adversarial QA insertion. Summary phase handover instructions split into logic-task (send to QA) and docs-task (send to Code Reviewer) paths.
2. **`README.md`** — Added QA Loop paragraph to How to Operate section. Struck through roadmap item #8 with ✅ **Implemented in V6.1.0**.
3. **`CHANGELOG.md`** — Added [6.1.0] release notes documenting QA Engineer persona, 7-step workflow, summary phase changes, and README updates.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

**Factual Git Diff:** Stored in Commit Hash: `2d2a9c5b567b7f3382ad4f0bf2f55f83974ce57f`
<!-- END_GIT_DIFF -->
