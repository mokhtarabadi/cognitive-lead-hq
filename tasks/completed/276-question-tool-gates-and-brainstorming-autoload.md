# Task 276: Question-tool approval gates and brainstorming auto-load

**File:** `tasks/qa/276-question-tool-gates-and-brainstorming-autoload.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Encode the question-tool-at-approval-gates rule into the cognitive agents and system prompt, and make brainstorming trigger without the Manager naming it each time.

## Manager's Notes

- After planning and after Code Reviewer acceptance the system asks the Manager for approval, but the goal plugin keeps the loop running, so at those gates the system must use the `question` tool (stored memory `workflows/approval_gates_use_question_tool`).
- Brainstorming currently does not auto-load; the Manager has to mention it every time. Fix so the trigger fires on its own.
- Both fixes in one task. Update cognitive agents and system prompt fragments where needed.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Initial codebase exploration
- [x] Encode question-tool gate rule in executor agent + prompt fragments + regen
- [x] Fix brainstorming auto-load trigger
- [x] Verify functionality

## Acceptance Criteria

- [x] Approval gates (plan approval, review acceptance/closure) call the `question` tool instead of prose-only asks
- [x] Brainstorming triggers without the Manager naming it each time
- [x] Cognitive agents and system prompt updated consistently, prompt sync passes
- [x] CHANGELOG updated, lint and full suite green

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pathspec pytest tests/ -q
- **Expected result:** all tests pass, exit code 0
- **Actual result:** Manager ran the suite pre-regen 2026-09-27: **689 passed, 10 warnings in 5.12s**, exit 0. After regen (`Assembled 94855 bytes`, head 9.47.0, 8+/8- in system-prompt.md only), suite re-run: **689 passed, 10 warnings in 5.01s**, exit 0. After review hotfix (Steps 1-5), Manager re-ran regen: `Assembled 95089 bytes -> system-prompt.md`; final suite re-run: **689 passed, 10 warnings in 10.59s**, exit 0. Lint evidence: `lint_task_file` pass on task file, `lint_markdown` pass on CHANGELOG.md (via lint MCP, exit-equivalent OK).
- **Exit code:** 0 (final post-hotfix suite run)

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** prompt regen drift; question-tool unavailable in some runtimes
- **Rollback plan:** revert fragment edits, regen prompt, re-run sync test

---

## Execution Log & Reasoning

Autopilot locked for task 276 (Manager: "auto polit it", 2026-09-27). File move to tasks/in-progress/ pending — no shell/mv tool in this runtime; Manager to run `git mv` (logged deviation, read-only work unaffected).
Seat Check: single-domain prompt engineering → Senior Programmer; Designer/Architect/QA/Reviewer/Planner/Strategist skipped with reasons; trigger map explicit miss.
Brainstorm: not required — single-domain reversible docs change.
Brain plan verdict (Senior Programmer, 2 turns, discovery-fed): E1-E7 question-tool mandate (executor Capability Preflight + 3 sections + fragment 11 Steps 3/4/8), E8-E11 brainstorming auto-eval (fragment 11 Step 2 + fragment 12 trigger/auditability + user-input-processing trigger + executor Seat Check), version bump 9.46.0→9.47.0, regen via scripts/prompt-build/assemble_system_prompt.py, verify lint + sync test + suite. history_turns_dropped 0 both turns. Plan presented for explicit approval (try 1/3).
Plan APPROVED by Manager via question tool (answer: "Approved", try 1/3 — gate passed using the very mechanism being implemented).
Implementation round (all edits applied, grep-verified): E1 Capability Preflight append; E2 plan-approval pause binding; E3 PO_REVIEW_PENDING relay binding; E4 goal-pause binding; E5/E6 fragment 11 Steps 3/4/8; E7 executor-only (Capability Preflight source fragment unpinned); E8 fragment 11 Step 2 auto-eval rewrite; E9 fragment 12 trigger append; E10 fragment 05 trigger append; E11 executor Seat Check + Planning Gate appends. Version bump: fragment 01 → 9.47.0, test pin tests/test_prompt_sync.py:42 → 9.47.0, CHANGELOG [Unreleased] bullet appended. Two edit retries needed (multi-line anchors with invisible whitespace mismatch; single-line anchors succeeded). BLOCKED: system-prompt.md regen + sync test + full suite — no shell in this runtime; Manager must run them before QA.
Verification round 2026-09-27: Manager ran the full suite pre-regen — 689 passed, 10 warnings in 5.12s, exit 0 (recorded in Verification Evidence). Task file header synced to tasks/in-progress/ after Manager's git mv. STILL PENDING: prompt regen + post-regen suite re-run (sync test must see the regenerated system-prompt.md).
Verification close-out 2026-09-27: Manager ran regen — assembled 94855 bytes, head 9.47.0, diff stat 8+/8- in system-prompt.md only. Post-regen suite re-run — 689 passed, 10 warnings in 5.01s, exit 0. All TODO/AC/DoD boxes checked. Ready for qa move (git mv needs Manager — no shell in this runtime).
Brain QA round 2026-09-27 (autopilot, same task_id): QA Engineer QA_PASSED with 2 nits (R1: Steps 3/8 lack unavailable-tool fallback; R2: fragment 05 dropped 'fabricate', 11/2.7 dropped 'it'). Code Reviewer APPROVED_WITH_CHANGES + 6-step hotfix XML. Hotfix applied Steps 1-5: fragment 05 'fabricate' restored, fragment 11 Step 2 'it' restored, Steps 3+8 got unavailable-fallback sentences, CHANGELOG bullet rewritten to done-state. Step 6 (regen + suite re-run) PENDING — needs Manager shell; version stays 9.47.0; file stays in tasks/qa/; re-review after Step 6.
Review Step 6 DONE 2026-09-27: Manager ran regen separately — `Assembled 95089 bytes -> system-prompt.md`; suite re-run — 689 passed, 10 warnings in 10.59s, exit 0. Ready for re-review.
Re-review 2026-09-27 (Code Reviewer): APPROVED, PO_REVIEW_PENDING — "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." No blocking issues. File stays in tasks/qa/ awaiting the exact PO phrase.
Closure 2026-09-27: Manager replied "Approved for closure" (exact accept phrase). PO_REVIEW_PENDING verified (glob confirms file in tasks/qa/, grep confirms verdict in log). Status set closed. Deviation from closure XML: no shell tool exists in this runtime, so the `git mv tasks/qa/ → tasks/completed/` step cannot run here — `**File:**` header stays truthful at the qa path and the Manager runs the move plus push manually (same precedent as prior tool-only closure). Closure XML otherwise executed exactly once (single issuance).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `c13aadfac38230a8e715a6c6520b02575f5a5790`
<!-- END_GIT_DIFF -->
