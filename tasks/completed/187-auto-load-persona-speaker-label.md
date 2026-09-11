# Task 187: Auto-load persona in system prompt with speaker label

**File:** `tasks/qa/187-auto-load-persona-speaker-label.md`
**Source:** manager
**Type:** feature
**Status:** in-progress

## Goal

Make the system-prompt Brain auto-load the right persona per turn with a confidence threshold. High-confidence inference declares the persona in the existing bracket label and proceeds; low-confidence stops and asks. No new label — the `02-role.md` bracket stays the single display.

## Manager's Notes

Manager request (Farsi, translated): add an "Auto-load persona" behavior to the system prompt so it is smart enough to handle two cases. (1) Explicit invocation: if the user names a persona by hand — e.g. "QA Engineer", "Code Reviewer", "Sprint Strategist", "Software Architect" (system architect), "Programmer (Senior Programmer)", "Project Planner", or "UI/UX Designer" — that exact persona must activate, its identity loads, and it answers. (2) Auto mode: if the user mentions nobody, the system infers who should load from the user's prompt plus the current Brain machine-state plus prior messages, and loads that persona automatically. Always: every Brain response opens with a speaker label stating which persona is speaking, so the Manager can verify who said it. The seven persona names above are the full known set (see `prompts/fragments/06-personas.md` + `02-role.md` declaration contract).

Scope revisions by Manager (later messages, binding): (a) DEDUP — the bracket label in `02-role.md` (`[Software Architect]`) already exists, so NO new "Speaking as" line is added; the auto-load rule reuses the existing bracket as its declaration display. (b) THRESHOLD — approved design: high-confidence inference proceeds with the bracket declaration (visible, correctable by Manager); low-confidence stops and asks instead of guessing, because guessing identity is hallucination-prone and one question costs less than a wrong persona.

Constraints: no contradiction with the seven-seat declaration contract (Task 180 round 2 fixed outside-persona brainstorming — do not regress); explicit mention always wins over inference; inference must be deterministic and explainable (which signal picked the persona).

## Local TODOs

- [x] Read `prompts/fragments/06-personas.md` + `02-role.md` + `12-brainstorming_protocol.md` for persona definitions and contracts
- [x] Draft auto-load rule: explicit-match (all 7 names + aliases) → threshold inference (high-confidence proceed with bracket declaration, low-confidence ask) → reuse existing bracket, no new label
- [x] Encode rule into 06-personas (`<auto_load>`), bump 9.22.0 → 9.23.0, reassemble, verify sync
- [x] Update CHANGELOG.md, lint, stage, move to qa
- [x] Generalize Farsi mentions to non-English in prompt files (manager order, same task)

## Acceptance Criteria

- [x] Explicit persona mention activates exactly that persona
- [x] High-confidence inference declares the persona in the existing bracket and proceeds; low-confidence stops and asks instead of guessing
- [x] No new "Speaking as" label — existing `02-role.md` bracket is the single display, no duplication
- [x] No new persona invented outside the declared seven; no regression of seven-seat contract
- [x] `system-prompt.md` regenerated from fragments and byte-identical (sync verified)
- [x] No Farsi-specific wording left in prompt-facing files — generalized to non-English (telegram-issue-sync domain data + Unicode technical ranges exempt)

## Verification Evidence

- **Test command:** `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check187.md && diff /tmp/check187.md system-prompt.md && echo SYNC_OK`
- **Expected result:** `SYNC_OK`, zero diff lines
- **Actual result:** `SYNC_OK`, zero diff lines; generated file 80177 bytes; `auto_load` count 1; `9.23.0` count 1
- **Exit code:** 0

Round 2 (Farsi → non-English generalization):

- **Test command:** `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check187b.md && diff /tmp/check187b.md system-prompt.md && echo SYNC_OK; grep -rn "Farsi\|Persian\|فارسی" prompts/fragments/ agents/cognitive-executor.md`
- **Expected result:** `SYNC_OK`, zero diff lines; zero Farsi hits in prompt files
- **Actual result:** `SYNC_OK`, zero diff lines; generated file 80237 bytes; `9.24.0` count 1; zero Farsi hits in `prompts/fragments/` + `agents/cognitive-executor.md` (remaining hits only in telegram-issue-sync domain data + bundle-tasks Unicode ranges, both exempt by design)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Inference picks the wrong persona; label adds noise to short answers.
- **Rollback plan:** Revert fragment edit from git history; reassemble; previous version recoverable.

---

## Execution Log & Reasoning

Implemented the approved threshold auto-load design. Read the 06-personas tail (seven seats incl. QA hotfix + Reviewer postfix behaviors intact) and confirmed version 9.22.0. Appended the `<auto_load>` block directly before `</personas>`: Layer 1 explicit name/alias match always wins; Layer 2 high-confidence inference declares the persona in the existing `02-role.md` bracket and proceeds (declaration is visible, Manager can correct); low-confidence stops and asks, because guessing identity risks hallucination and one question costs less than a wrong persona. No new "Speaking as" label per Manager dedup order — the existing bracket is the single display. Bumped 9.22.0 → 9.23.0 in fragment source, reassembled (80177 bytes, SYNC_OK byte-identical). No other fragments touched; seven-seat contract untouched.

Round 2 — Farsi → non-English generalization (same task, manager order, no new task): grepped prompt files for Farsi mentions (7 hits in fragments/executor). Fixed all: fragment 05 language detection, ambiguity mandate, translation step, clarifying-question language; fragment 13 machine-channel exemption; executor intent-validation + quote-is-evidence. Also neutralized Farsi-specific wording in audit-agents and prompt-refactor skills. Kept deliberately: telegram-issue-sync Persian handling (its domain data IS Persian Telegram messages) and bundle-tasks Unicode/Persian slug ranges (technical character-range facts). Bumped 9.23.0 → 9.24.0 in fragment source, reassembled (80237 bytes, SYNC_OK byte-identical, zero Farsi hits in prompt files).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index a737982..7e6bdf6 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,12 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+## [9.23.0] - 2026-09-11
+
+### Added
+
+- **Persona auto-load with confidence threshold (Task 187):** New `<auto_load>` block in `prompts/fragments/06-personas.md` — Layer 1 explicit name/alias always wins; Layer 2 high-confidence inference declares the persona in the existing `02-role.md` bracket and proceeds (visible, correctable), low-confidence stops and asks the Manager instead of guessing (guessing identity is hallucination-prone; one question costs less than a wrong persona). No new "Speaking as" label by Manager order — the existing bracket display is the single label, no duplication. Seven-seat contract intact.
+
 ## [9.22.0] - 2026-09-11
 
 ### Added
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 19d04e8..6c9b60c 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.22.0</system_version>
+<system_version>9.23.0</system_version>
diff --git a/prompts/fragments/06-personas.md b/prompts/fragments/06-personas.md
index 0814e20..737a0b4 100644
--- a/prompts/fragments/06-personas.md
+++ b/prompts/fragments/06-personas.md
@@ -55,4 +55,10 @@
     <duty>Audit the Hands' completed work against the Architect's blueprint, the Designer's UI specs, and the project's conventions.</duty>
     <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. The Manager ferries task files by hand, so always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where to paste it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes, instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs the Reviewer. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." ONLY when the Manager explicitly uses the keyword "Approved for closure" or "Close task", generate the final closure task to `mkdir -p tasks/completed/`, use `git mv` to move the task file to `tasks/completed/`, and strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options.</behavior>
 </persona>
+
+<auto_load>
+Layer 1 — explicit mention wins. If the Manager names a persona (exact name or clear alias: QA, Reviewer, Architect, Strategist, Planner, Programmer, Designer), load that persona immediately. No inference needed.
+Layer 2 — threshold inference. If nobody is named, infer from the Manager's message plus conversation history and current machine state. High confidence means the message maps to exactly one persona's trigger or duty with no rival. Then load it, declare it in the existing bracket label, and proceed. The label makes the choice visible and correctable. Low confidence means two or more personas fit, or none fits clearly. Then do NOT guess. Stop and ask the Manager which persona to load. Guessing an identity is a hallucination risk. One question costs less than a wrong persona.
+No new label. The bracket declaration in 02-role stays the single speaker display. Never add a second Speaking-as line.
+</auto_load>
 </personas>
\ No newline at end of file
diff --git a/system-prompt.md b/system-prompt.md
index ca3b94f..942b08e 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.22.0</system_version>
+<system_version>9.23.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -107,6 +107,12 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
     <duty>Audit the Hands' completed work against the Architect's blueprint, the Designer's UI specs, and the project's conventions.</duty>
     <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. The Manager ferries task files by hand, so always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where to paste it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes, instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs the Reviewer. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." ONLY when the Manager explicitly uses the keyword "Approved for closure" or "Close task", generate the final closure task to `mkdir -p tasks/completed/`, use `git mv` to move the task file to `tasks/completed/`, and strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options.</behavior>
 </persona>
+
+<auto_load>
+Layer 1 — explicit mention wins. If the Manager names a persona (exact name or clear alias: QA, Reviewer, Architect, Strategist, Planner, Programmer, Designer), load that persona immediately. No inference needed.
+Layer 2 — threshold inference. If nobody is named, infer from the Manager's message plus conversation history and current machine state. High confidence means the message maps to exactly one persona's trigger or duty with no rival. Then load it, declare it in the existing bracket label, and proceed. The label makes the choice visible and correctable. Low confidence means two or more personas fit, or none fits clearly. Then do NOT guess. Stop and ask the Manager which persona to load. Guessing an identity is a hallucination risk. One question costs less than a wrong persona.
+No new label. The bracket declaration in 02-role stays the single speaker display. Never add a second Speaking-as line.
+</auto_load>
 </personas>
 
 <agent_skills_registry>
```
<!-- END_GIT_DIFF -->
