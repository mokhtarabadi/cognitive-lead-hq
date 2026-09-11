# Task 184: Goal lifecycle for every task XML — create, pause, resume

**File:** `tasks/qa/184-goal-lifecycle-per-task-xml.md`
**Source:** manager
**Type:** feature
**Status:** in-progress

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
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 43a00e8..1540598 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Goal lifecycle for heavy implementation tasks (Task 184):** `agents/cognitive-executor.md` gains a `Goal Lifecycle` section — create a session goal on receipt of heavy work (AC as success criteria), work under it, pause only for allowed questions, resume on answer, close with evidence aligned to Kanban closure. Light tasks skip the goal. Grounded in the installed opencode-goal-plugin 0.8.2 (`/goal` + 11 tools, active/paused/blocked, evidence-gated completion).
+
 - **Spider-search workflow for blowsh skill (Task 186):** `skill-templates/blowsh/SKILL.md` gains a `Spider-Search Workflow` deep-research mode — plan (4–6 sub-questions mapped to queries) → sweep wide (`query_variants` + `intent`) → probe cheap (`must_contain`/`toc`/`map`) → read deep (`fetch_web_batch` + `focus`) → follow chains (`extract_links`, default 2 iterations) → cite everything. Loop rules: visited-URL set, budgets on every call, stop signals as results, `respect_robots`/`same_host` defaults. Grounded in researched best practices (deep-research survey pipeline, Firecrawl search→scrape→analyze→repeat, DeepWideSearch breadth-depth balance, NVIDIA planner/researcher phases, classic best-first focused crawling). Synced to global skills.
 - **Dogfood round (Task 186, same task):** Ran the new workflow on its own topic — plan (4 sub-questions) → parallel sweeps → probe → focused fetch of the LangChain deep-research doc → iteration-2 chain fetch. Folded 5 genuine deltas back into the skill: parallel sub-question sweeps (step 2), assess-after-each-search question (step 5), one citation number per unique URL + Sources list + sub-question coverage check (step 6), search budget 2–3 simple / 5 per branch complex + scale-matching rule (loop rules). Synced to global skills.
 - **Synthesis + saturation upgrade (Task 185):** Extended the spider workflow with step 7 (ranked-options synthesis: evidence with citation numbers, trade-offs, strong/medium/weak confidence grades, exactly one recommended winner) and explicit saturation stop-conditions in the loop rules (under ~10% novel facts per round, semantically repeated queries, or all sub-questions answered — budget caps demoted to backstop). Corroboration rules added to step 6 (2+ independent sources to establish a claim, primary-over-secondary weighting, explicit contradiction flagging). Grounded in tianpan.co deep-research convergence analysis (information-gain thresholds, query saturation, coverage checklists, budget backstops, multi-source corroboration). Synced to global skills.
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 53d89a7..539c866 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -226,6 +226,36 @@ Claim: "Task complete. The code looks correct."
    NEVER auto-commit. QA/review happen as Manager-directed direct review,
    not as persona loops.
 
+## Goal Lifecycle (heavy implementation tasks only)
+
+The Hands run inside OpenCode, which provides session-scoped goal tools
+(`get_goal`, `create_goal`, `update_goal`, plus pause/resume status).
+The system prompt also carries the goal mode policy. Use them as follows.
+Light tasks (single-file edits, docs-only changes, quick fixes) skip the
+goal entirely — goal overhead must never exceed the task itself.
+
+1. **Create on receipt.** When a heavy implementation task arrives
+   (multi-file, multi-phase, or explicitly ordered as a Goal), call
+   `get_goal` first. If a matching non-closed goal exists, continue under
+   it. Otherwise `create_goal` once, with the task objective and its
+   Acceptance Criteria as success criteria.
+2. **Work under the goal.** Every implementation step serves the goal
+   objective. If new instructions arrive mid-task, capture them against
+   the goal before acting.
+3. **Pause on allowed questions only.** If the task truly cannot proceed
+   without the Manager, pause the goal, ask exactly one precise question,
+   and stop. Pausing is permitted ONLY for the narrow cases where asking
+   is allowed — never as a substitute for permitted autonomous action.
+   No orphaned pauses: every pause names the blocker.
+4. **Resume on answer.** When the Manager answers, resume the goal and
+   continue from the recorded state. Do not restart completed steps.
+5. **Close with evidence.** Close the goal only when the task's
+   Acceptance Criteria are verified against real artifacts (tests,
+   diffs, command output). The closure evidence mirrors the task's
+   Verification Evidence. Goal closure and Kanban closure stay aligned:
+   no goal left open behind a closed task, no task closed with its goal
+   unmet.
+
 <!-- AUTOMATION-PAUSED-2026-09-09 (Task 175 — automation not mature enough, disabled by Manager order; preserved verbatim for future restoration, see archive/automation-paused-2026-09-09/RESTORE.md). Do NOT follow anything until AUTOMATION-RESUME while paused.
 
 ## Persona Loop (MCP Slash Commands)
```
<!-- END_GIT_DIFF -->
