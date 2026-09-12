# Task 184: Goal lifecycle for every task XML — create, pause, resume

**File:** `tasks/completed/184-goal-lifecycle-per-task-xml.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Make the Cognitive Executor open an OpenCode Goal for every incoming task XML, work toward it until complete, pause it to ask Admin questions when blocked, and resume when answered.

## Manager's Notes

Manager requirement: when a task XML is created and passed to the Cognitive Executor, it must create a Goal using the Goal plugin in OpenCode, define the goal, and keep working toward it until completion. If it needs to ask Admin something, it must pause the Goal, ask the question, then resume the Goal on response and continue. Encode this lifecycle (create on task receipt → execute → pause-on-question → resume-on-answer → close with evidence) into `agents/cognitive-executor.md`, integrated with the Task 181 ask-gate (pausing is only for the narrow cases where asking is allowed) and the Kanban lifecycle. Must respect the automation-paused state: design the lifecycle rules now; wire live goal-tool calls only where currently permitted.

## Local TODOs

- [x] Map goal-tool operations (create/pause/resume/close) to executor lifecycle stages
- [x] Define pause-gate: only Task-181-approved questions may pause a goal
- [x] Define resume + close-with-evidence rules
- [x] Encode into `agents/cognitive-executor.md`

## Acceptance Criteria

- [x] Every heavy task XML starts with goal creation; work continues under the goal until done (light tasks skip per manager order)
- [x] Admin questions pause the goal; answers resume it (no orphaned goals)
- [x] Goal closes only with recorded evidence, matching Kanban closure
- [x] Consistent with Task 181 ask-gate (no new question loopholes)

## Verification Evidence

- **Test command:** `grep -n -i "pause.*goal\|resume.*goal\|create.*goal" agents/cognitive-executor.md`
- **Expected result:** full lifecycle rules present (create → pause → resume → close)
- **Actual result:** all five lifecycle stages present (create on receipt, work under goal, pause on allowed questions, resume on answer, close with evidence)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Goal-tool behavior differs across OpenCode versions; lifecycle rules may need adaptation.
- **Rollback plan:** Revert `agents/cognitive-executor.md` from git history.

---

## Execution Log & Reasoning

Studied the installed opencode-goal-plugin 0.8.2 first (README + package): session-scoped `/goal`, 11 tools, active/paused/blocked statuses, evidence-gated completion, idle auto-continue. Plugin is registered in both repo and global `opencode.json`. Added a `Goal Lifecycle` section to `agents/cognitive-executor.md` right after Manual Workflow: create-on-receipt (get_goal first, create once), work under goal, pause only for allowed questions, resume on answer, close with evidence aligned to Kanban. Heavy-tasks-only per manager order — light tasks skip. No system-prompt fragments touched, so no version bump. CHANGELOG Unreleased entry added.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `92d3a2f07067a084550a6ad0bbea33a240d8c6f9`
<!-- END_GIT_DIFF -->
