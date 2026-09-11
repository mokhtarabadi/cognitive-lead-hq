# Task 181: Executor autonomy — never stall asking questions mid-task

**File:** `tasks/in-progress/181-executor-autonomy-no-midtask-questions.md`
**Source:** manager
**Type:** improvement
**Status:** in-progress

## Goal

Make the Cognitive Executor resolve ambiguities itself and keep moving instead of stalling mid-task to ask the Manager questions.

## Manager's Notes

Manager observation: the executor sometimes gets stuck and asks questions inside the Cognitive Executor instead of proceeding intelligently and automatically. Required behavior: when information is missing, the executor must pick the most reasonable interpretation, record the assumption in the Execution Log, and continue. Questions to the Manager are allowed ONLY when two or more interpretations are equally plausible AND the choice is irreversible or destructive. Everything else is decided autonomously. Research industry best practices for autonomous agent behavior (e.g. ReAct decide-act loops, assumption logging, confidence thresholds) and encode the best fitting rules into `agents/cognitive-executor.md` without disrupting the existing core protocols (ZAC, Kanban lifecycle, dual-channel communication from Task 180).

## Local TODOs

- [x] Research autonomous-agent best practices (assumption logging, decision thresholds, when-to-ask policies)
- [x] Draft autonomy rules: decide-by-default, assumption log, narrow ask-gate for irreversible choices
- [x] Encode rules into `agents/cognitive-executor.md`
- [x] Verify no conflict with existing protocols (ZAC, Kanban, dual-channel)

## Acceptance Criteria

- [x] Executor asks the Manager mid-task ONLY for irreversible/destructive ambiguous choices
- [x] All autonomous decisions are recorded as assumptions in the Execution Log
- [x] No existing core protocol weakened (ZAC, Kanban moves, dual-channel scope intact)

## Verification Evidence

- **Test command:** `grep -n -i "assumption\|ask the Manager" agents/cognitive-executor.md`
- **Expected result:** autonomy section present with narrow ask-gate
- **Actual result:** new `XML Task Execution Autonomy` section at lines 139-145 (assume-first, blocking-only criteria, questions ride along); Direct Input Clarification Halt untouched at lines 72-80
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Over-autonomy causes wrong irreversible actions.
- **Rollback plan:** Revert `agents/cognitive-executor.md` from git history; ask-gate restores previous behavior.

---

## Execution Log & Reasoning

Added `XML Task Execution Autonomy` section (lines 139-145) before `## Execution Discipline`: assume-first with A1/A2 assumption log, blocking-only stop criteria (destructive without rollback, missing secret, self-contradictory task), questions ride along as Q1/Q2 in the handoff. Scoped strictly to XML execution — Direct Input Clarification Halt (lines 72-80) unchanged, so raw ad-hoc input still halts on ambiguity. Verified ZAC/Kanban/dual-channel sections untouched via grep. Executor-only change: no system-prompt fragments, no version bump, no global sync needed beyond the executor file itself.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
