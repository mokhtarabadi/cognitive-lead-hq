# Task 182: Self-driving QA and Reviewer loops — auto re-run on rejection

**File:** `tasks/qa/182-self-driving-qa-reviewer-loops.md`
**Source:** manager
**Type:** improvement
**Status:** in-progress

## Goal

Make rejections self-healing on the Brain side: when QA or the Reviewer rejects an implementation, the persona itself emits the fix XML so the Manager only copies it to the Hands — no manual nudge needed.

## Manager's Notes

Manager clarification (Farsi, translated): the Brain/Orchestrator has no code access — the Manager ferries completed task files between Hands and Brain by hand ("QA engineer please make the adversarial testing"). On QA reject, the Brain must automatically emit a hotfix/postfix implementation XML covering the rejection reasons; the Manager copies it to the Hands, brings the fix back, and re-runs QA until pass. Same for the Reviewer: on reject (or approved-with-changes) it auto-emits the postfix XML; the Manager copies it to the Hands and re-runs the Reviewer until approval, then PO review. This state machine matters. Manager approved both open questions: APPROVED_WITH_CHANGES also auto-emits the postfix XML, and the auto XML carries a 3-line Manager-facing summary on top.

## Local TODOs

- [x] Study current QA/Reviewer persona behaviors in `prompts/fragments/06-personas.md`
- [x] Rewrite QA_REJECTED path: verdict + 3-line summary + auto hotfix XML (existing task file)
- [x] Rewrite Reviewer reject/approved-with-changes path: verdict + 3-line summary + auto postfix XML
- [x] Add 3rd-rejection escalation guard (no infinite loops)
- [x] Bump 9.16.0 → 9.17.0, reassemble, verify sync, CHANGELOG, lint, stage, move to qa

## Acceptance Criteria

- [x] QA rejection auto-emits hotfix implementation XML with findings as fix spec
- [x] Reviewer rejection AND approved-with-changes auto-emit postfix XML
- [x] Auto XML carries 3-line Manager summary (what failed, what fix covers, where to paste)
- [x] Fix targets the EXISTING task file, never a new task number
- [x] Bounded retries: 3rd rejection escalates to Manager instead of another XML
- [x] Machine-complete XML: every emitted step names exact path + operation, zero questions to Manager, no code pastes (Task 182 extension)

## Verification Evidence

- **Test command:** `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check182.md && diff /tmp/check182.md system-prompt.md && grep -c "hotfix\|postfix" system-prompt.md`
- **Expected result:** `SYNC_OK`, count 2
- **Actual result:** `SYNC_OK`, count 2; generated file 77358 bytes, contains `9.17.0`
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Brain emits fix XML against a stale task version the Manager pasted.
- **Rollback plan:** Revert `prompts/fragments/06-personas.md` + `01-system_version.md` from git history, reassemble.

---

## Execution Log & Reasoning

Implemented per manager clarification: the fix belongs on the Brain side (`06-personas.md`), not the Hands executor loop. QA_REJECTED now yields verdict + 3-line summary + hotfix XML; Reviewer REJECTED/APPROVED_WITH_CHANGES yields verdict + summary + postfix XML; both target the existing task file; 3rd rejection escalates. Version 9.17.0, sync byte-identical (77358 bytes).

Extension (manager order, same task): the Hands asked the Manager mid-task questions the approved plan already answered. Added an ORCHESTRATOR AUTHORING RULE to `09-hands_protocols.md` `<execution_phase>` — every emitted checklist step is machine-complete (exact path + exact operation, all plan decisions pre-made, zero questions back), no pasted code blocks, Hands questions allowed ONLY for info existing nowhere in plan or repo. Version 9.18.0, sync byte-identical (77926 bytes).

---

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 1540598..96f3f47 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,12 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+## [9.17.0] - 2026-09-11
+
+### Changed
+
+- **Self-driving QA/Reviewer reject loops (Task 182, manager clarification):** the Brain has no code access and the Manager ferries task files by hand, so the QA Engineer and Code Reviewer personas in `prompts/fragments/06-personas.md` no longer stop at a rejection verdict. On QA_REJECTED they now emit a 3-line Manager summary plus a hotfix `<hands_implementation_task>` XML scoped to the failing points; on REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES the Reviewer emits the same pattern as a postfix XML. Both fix the EXISTING task file (never a new task number). Retry guard: after the 3rd rejection of the same task, stop emitting XML and escalate to the Manager with options. Reassembled `system-prompt.md` (sync-check byte-identical).
+
 ### Added
 
 - **Goal lifecycle for heavy implementation tasks (Task 184):** `agents/cognitive-executor.md` gains a `Goal Lifecycle` section — create a session goal on receipt of heavy work (AC as success criteria), work under it, pause only for allowed questions, resume on answer, close with evidence aligned to Kanban closure. Light tasks skip the goal. Grounded in the installed opencode-goal-plugin 0.8.2 (`/goal` + 11 tools, active/paused/blocked, evidence-gated completion).
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index d99b07f..d52dc40 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.16.0</system_version>
+<system_version>9.17.0</system_version>
diff --git a/prompts/fragments/06-personas.md b/prompts/fragments/06-personas.md
index e6c972f..0814e20 100644
--- a/prompts/fragments/06-personas.md
+++ b/prompts/fragments/06-personas.md
@@ -47,12 +47,12 @@
   <persona name="QA Engineer">
     <trigger>Implementation phase is complete, or explicit Manager request for testing.</trigger>
     <duty>Adversarial testing, boundary analysis, fuzzing, and stability enforcement.</duty>
-    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, Status (QA_PASSED or QA_REJECTED). If QA_REJECTED, instruct the Hands to UPDATE the EXISTING task file in `tasks/qa/` with specific failing boundary tests and fixes — do NOT create a new task. The Hands must implement fixes directly in the existing task file and re-stage. If QA_PASSED, instruct the Manager to hand over to the Code Reviewer.</behavior>
+    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, Status (QA_PASSED or QA_REJECTED). If QA_REJECTED, do NOT stop at the verdict. The Manager ferries task files between the Hands and the Brain by hand, so always emit the next step yourself: first a 3-line Manager summary (what failed, what the fix covers, where to paste it), then a hotfix `<hands_implementation_task>` XML scoped ONLY to the failing points, instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs QA. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If QA_PASSED, instruct the Manager to hand over to the Code Reviewer.</behavior>
 </persona>
 
   <persona name="Code Reviewer">
     <trigger>Manager pastes the Hands' completed Task Summary, PRs are submitted, or Manager requests.</trigger>
     <duty>Audit the Hands' completed work against the Architect's blueprint, the Designer's UI specs, and the project's conventions.</duty>
-    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. If rejected, explicitly state what the Hands must fix in the next iteration and instruct the Hands to UPDATE the EXISTING task file — do NOT create a new task. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." ONLY when the Manager explicitly uses the keyword "Approved for closure" or "Close task", generate the final closure task to `mkdir -p tasks/completed/`, use `git mv` to move the task file to `tasks/completed/`, and strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options.</behavior>
+    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. The Manager ferries task files by hand, so always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where to paste it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes, instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs the Reviewer. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." ONLY when the Manager explicitly uses the keyword "Approved for closure" or "Close task", generate the final closure task to `mkdir -p tasks/completed/`, use `git mv` to move the task file to `tasks/completed/`, and strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options.</behavior>
 </persona>
 </personas>
\ No newline at end of file
diff --git a/system-prompt.md b/system-prompt.md
index 5fd7d05..9c6e08a 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.16.0</system_version>
+<system_version>9.17.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -97,13 +97,13 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
   <persona name="QA Engineer">
     <trigger>Implementation phase is complete, or explicit Manager request for testing.</trigger>
     <duty>Adversarial testing, boundary analysis, fuzzing, and stability enforcement.</duty>
-    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, Status (QA_PASSED or QA_REJECTED). If QA_REJECTED, instruct the Hands to UPDATE the EXISTING task file in `tasks/qa/` with specific failing boundary tests and fixes — do NOT create a new task. The Hands must implement fixes directly in the existing task file and re-stage. If QA_PASSED, instruct the Manager to hand over to the Code Reviewer.</behavior>
+    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, Status (QA_PASSED or QA_REJECTED). If QA_REJECTED, do NOT stop at the verdict. The Manager ferries task files between the Hands and the Brain by hand, so always emit the next step yourself: first a 3-line Manager summary (what failed, what the fix covers, where to paste it), then a hotfix `<hands_implementation_task>` XML scoped ONLY to the failing points, instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs QA. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If QA_PASSED, instruct the Manager to hand over to the Code Reviewer.</behavior>
 </persona>
 
   <persona name="Code Reviewer">
     <trigger>Manager pastes the Hands' completed Task Summary, PRs are submitted, or Manager requests.</trigger>
     <duty>Audit the Hands' completed work against the Architect's blueprint, the Designer's UI specs, and the project's conventions.</duty>
-    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. If rejected, explicitly state what the Hands must fix in the next iteration and instruct the Hands to UPDATE the EXISTING task file — do NOT create a new task. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." ONLY when the Manager explicitly uses the keyword "Approved for closure" or "Close task", generate the final closure task to `mkdir -p tasks/completed/`, use `git mv` to move the task file to `tasks/completed/`, and strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options.</behavior>
+    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. The Manager ferries task files by hand, so always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where to paste it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes, instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs the Reviewer. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." ONLY when the Manager explicitly uses the keyword "Approved for closure" or "Close task", generate the final closure task to `mkdir -p tasks/completed/`, use `git mv` to move the task file to `tasks/completed/`, and strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options.</behavior>
 </persona>
 </personas>
```
<!-- END_GIT_DIFF -->
