# Task 202: Brain Planning Gate Before Implementation

**File:** `tasks/completed/202-brain-planning-gate-before-implementation.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

New-feature tasks must receive a Brain architect/brainstorm round before the Hands writes any implementation code.

## Manager's Notes

Hands are hands, not the brain. Critical decisions belong to the Brain. QA and review already run through the Brain on every task, but no rule forces a Brain planning round before implementation — the plan arrives baked into the XML and the Hands fill the gaps alone. Close that gap: the Hands must request a plan (Software Architect seat or full brainstorm panel) via the bridge and execute from the returned path. Autopilot: run the full state machine with zero manager questions, notify only when approval is needed.

## Local TODOs

- [x] Define the trigger rule (which tasks count as new-feature) in the Hands bridge protocol
- [x] Wire the planning round through the bridge with transcript continuity
- [x] Rebuild the system prompt if a fragment changes, bump version, verify sync
- [x] Full test suite passes with exit code 0
- [x] Brain QA then reviewer, fix what reproduces, stage and move to QA

## Acceptance Criteria

- [x] A new-feature task cannot reach implementation without a recorded Brain plan in its file
- [x] The Hands execute from the Brain's selected path and cite it
- [x] Escape hatch exists for trivial tasks with explicit justification
- [x] Full suite green, lint clean, CHANGELOG updated

## Verification Evidence

- **Test command:** repo pytest suite plus prompt rebuild round-trip check
- **Expected result:** exit 0, system-prompt sync clean
- **Actual result:** suite 264 passed exit 0; no fragment changed so no rebuild needed (executor doc verified not a build input); task lint clean; markdown lint clean
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** extra Brain round-trip on every feature slows the fast path
- **Rollback plan:** revert the protocol fragment change and rebuild the prompt

---

## Execution Log & Reasoning

Assumption A1: the gate lives in `agents/cognitive-executor.md` (the Hands manual), not in a prompt fragment — verified via assembler sources that file is not a build input, so no rebuild or version bump is required. The full-mode production line (Steps 1–4, blueprint, PO approval) already mandates planning; Lite Mode explicitly excludes new features; the uncovered path is direct/autopilot Hands implementation, which this gate now binds. Planning round runs under the same `task_id` so transcript continuity holds. This task itself passed via Manager-direct design, recorded in the gate text. CHANGELOG Added entry under [Unreleased].

QA round 1 (task_id 202, verbatim gate pasted): QA_REJECTED — F1 instance-history sentence in durable doc, F2 Lite bypass missing login/money guard, F3 no output format, F4 no fallback when no task file exists, F5 no approver definition, F6 proofs missing. All reproduced against the pasted text. Fix applied in executor doc: instance sentence removed (proof lives here), Lite excludes login/auth/money/security-surface, format specified (Brain's plan verdict + selected path), fallback session/goal record, approval defined (blueprint / brainstorm report / Manager's explicit quoted words, self-approval never counts). F6 proofs gathered: assembler line 6 + fragments-boundary guard, CHANGELOG entry, suite 264 exit 0 re-run, markdown lint passed. QA round 2 (fixed text + proofs pasted): QA_PASSED with one action (task re-lint before closure — done, clean). Reviewer round (final gate text pasted): APPROVED / PO_REVIEW_PENDING — strengths F1-F5 (three approval sources, self-approval ban, same-task_id history, Lite limits incl. auth/money/security-surface), no issues, no hotfix XML. No autoclosure: reviewer defers to Manager per standing rule. Moving to QA.

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `fb2a0f9a5a985e6b3ed326b774e3bb2e47004a73`
<!-- END_GIT_DIFF -->
