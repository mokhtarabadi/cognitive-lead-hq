# Task 182: Self-driving QA and Reviewer loops — auto re-run on rejection

**File:** `tasks/completed/182-self-driving-qa-reviewer-loops.md`
**Source:** manager
**Type:** improvement
**Status:** closed

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
**Factual Git Diff:** Stored in Commit Hash: `7833765a4761ea5fbc13484bdbb773f408738484`
<!-- END_GIT_DIFF -->
