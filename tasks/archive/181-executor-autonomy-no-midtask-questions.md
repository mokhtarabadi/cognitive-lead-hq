# Task 181: Executor autonomy — never stall asking questions mid-task

**File:** `tasks/completed/181-executor-autonomy-no-midtask-questions.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Make the Cognitive Executor resolve ambiguities itself and keep moving instead of stalling mid-task to ask the Manager questions.

## Manager's Notes

Manager observation: the executor sometimes gets stuck and asks questions inside the Cognitive Executor instead of proceeding intelligently and automatically. Required behavior: when information is missing, the executor must pick the most reasonable interpretation, record the assumption in the Execution Log, and continue. Questions to the Manager are allowed ONLY when two or more interpretations are equally plausible AND the choice is irreversible or destructive. Everything else is decided autonomously. Research industry best practices for autonomous agent behavior (e.g. ReAct decide-act loops, assumption logging, confidence thresholds) and encode the best fitting rules into `agents/cognitive-executor.md` without disrupting the existing core protocols (ZAC, Kanban lifecycle, dual-channel communication from Task 180).

## Local TODOs

- [x] Research autonomous-agent best practices (assumption logging, decision thresholds, when-to-ask policies)
- [x] Draft autonomy rules: decide-by-default, assumption log, narrow ask-gate for irreversible choices
- [x] Encode rules into `agents/cognitive-executor.md`
- [x] Verify no conflict with existing protocols (ZAC, Kanban, dual-channel)
- [x] Trace task-number reference habit (no written rule; provenance markers + author annotations + fresh heading)
- [x] Define Task-Number Reference Discipline in `docs/conventions.md` + executor Negative Patterns bullet
- [x] Audit prompt-facing Markdown; clean hallucinating refs (fragment 07, executor heading, 2 skills, conventions line)
- [x] Bump 9.18.0 → 9.19.0, reassemble system-prompt.md, verify sync
- [x] Fix originating prompts: discipline clause in 09-hands_protocols documentation_phase + task-generator skill step 3
- [x] Bump 9.19.0 → 9.20.0, reassemble, verify sync, CHANGELOG entry
- [x] Propagate discipline to audit-agents skill (template pair + conventions template section + Mode 2 criteria) so other projects get the rule via audit

## Acceptance Criteria

- [x] Executor asks the Manager mid-task ONLY for irreversible/destructive ambiguous choices
- [x] All autonomous decisions are recorded as assumptions in the Execution Log
- [x] No existing core protocol weakened (ZAC, Kanban moves, dual-channel scope intact)
- [x] Task numbers appear ONLY in code comments, CHANGELOG, task files, history, HTML-comment markers — never in prompt prose
- [x] `system-prompt.md` regenerated from fragments and byte-identical (sync verified, v9.19.0)
- [x] Originating authoring prompts fixed (09 documentation_phase + task-generator step 3); v9.20.0 sync verified
- [x] Audit-agents skill carries the discipline (3 spots, project-agnostic); other projects inherit it on next audit

## Verification Evidence

- **Test command:** `grep -n -i "assumption\|ask the Manager" agents/cognitive-executor.md`
- **Expected result:** autonomy section present with narrow ask-gate
- **Actual result:** new `XML Task Execution Autonomy` section at lines 139-145 (assume-first, blocking-only criteria, questions ride along); Direct Input Clarification Halt untouched at lines 72-80
- **Exit code:** 0
- **Test command:** `grep -rn "(Task [0-9]" prompts/fragments/ agents/ skill-templates/ docs/conventions.md | grep -v PAUSED-2026-09-09; python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check181b.md && diff /tmp/check181b.md system-prompt.md && echo SYNC_OK`
- **Expected result:** only the two self-defining rule lines remain; SYNC_OK
- **Actual result:** only rule-definition lines (executor:135, conventions:175) + frozen pause block remain; SYNC_OK, 77915 bytes, 9.19.0
- **Exit code:** 0
- **Test command:** `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check187.md && diff /tmp/check187.md system-prompt.md && echo SYNC_OK; grep -c "Task-number discipline" system-prompt.md`
- **Expected result:** SYNC_OK + discipline clause present once
- **Actual result:** SYNC_OK, 78269 bytes, count 1, 9.20.0
- **Exit code:** 0
- **Test command:** `grep -n "Task-Number Reference Discipline" skill-templates/audit-agents/SKILL.md; grep -n "Task [0-9]\|task [0-9]" skill-templates/audit-agents/SKILL.md`
- **Expected result:** rule in 3 spots; no bare task numbers except the rule's own example
- **Actual result:** rule in 3 spots (template pair:299, conventions template section:236, Mode 2 criteria:389); only bare-number hit is the illustrative example in the Don't line
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

Extension (manager hallucination report, same task): task-number refs traced — no written rule ever mandated them; habit came from deliberate PAUSED-2026-09-09 provenance markers, skill-author origin annotations, and my own fresh heading. Defined `Task-Number Reference Discipline` in `docs/conventions.md` + mirror bullet in executor Negative Patterns (refs ONLY in code comments, CHANGELOG, task files, history, HTML-comment markers). Cleaned 10 prompt-facing hits: fragment 07 registry line, executor heading, 5 in bundle-tasks skill, 2 in task-generator skill, 1 historical line in conventions. Frozen pause block (verbatim per AGENTS.md) and YAML `#` comments untouched by design. Bumped 9.18.0 → 9.19.0 (fragment 07 changed), reassembled, SYNC_OK byte-identical. Changed skills re-synced globally.

Extension (audit-agents vehicle, manager order, same task): this repo seeds other projects via the audit-agents skill, so the discipline was propagated into `skill-templates/audit-agents/SKILL.md` in all three load-bearing spots — Mode 1 AGENTS.md template Don't/Do pair, Mode 1 conventions template `## Task-Number Reference Discipline` section, Mode 2 audit criteria bullet — mirroring the DSP/Financial pattern. Project-agnostic, no HQ-only content. Skill self-check: no bare task numbers except the rule's own illustrative example. No version bump (skills are not fragments).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `9e596fb78730cca8e8cadb7edae2ef6261e24fd8`
<!-- END_GIT_DIFF -->
