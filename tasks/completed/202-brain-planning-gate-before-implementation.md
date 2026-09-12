# Task 202: Brain Planning Gate Before Implementation

**File:** `tasks/qa/202-brain-planning-gate-before-implementation.md`
**Source:** manager
**Type:** feature
**Status:** open

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
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 0ebadb3..0516e37 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Planning gate: no implementation without a Brain plan (Task 202):** new `Planning Gate` section in `agents/cognitive-executor.md` binds the Hands where full-mode Steps 1–4 and Lite Mode do not — before writing implementation code the Hands must confirm the task carries an approved plan (blueprint, brainstorm report, or Manager-direct design) and otherwise run one `brain_turn` planning round under the same `task_id`, record the selected path in the Execution Log, and execute from it. Lite-eligible changes pass with a one-line justification; explicit Manager "just do it" is the plan. Executor doc is not a prompt-build input, so no rebuild or version bump. Full suite: **264 passed**.
+
 - **Brain QA/reviewer turns carry changed hunks (Task 201):** `brain_turn` accepts `include_diff` — when true and the task id resolves, the Factual Git Diff content rides along verbatim (capped separately, fail-safe), so QA and reviewer judge actual changes instead of summaries. The Hands protocol mandates `include_diff=True` on QA/reviewer turns. 8 new offline tests (extract present/absent/multi/unclosed, attach resolved/none/unresolvable/over-cap) plus a fence-escape guard with 2 more tests (fence break, empty pair). README gains a Modes section (manual default vs locked autopilot, switch words). Full suite: **262 passed**.
 
 - **Token-optimization verified spike (Task 150):** Evaluated RTK 0.49.0 locally (musl binary, no global install): passing pytest suite collapses 1801 bytes / 21 lines → 44 bytes / 3 lines (**97.6% fewer bytes**, exit code preserved, 232 passed); small git outputs (±2%) not worth wrapping; `rtk diff` is a `/usr/bin/diff` wrapper (use `rtk git diff`); `rtk test` needs exact dep pins (`mcp==1.30.0` — `<` specs break as shell redirection). `headroom-ai` 0.37.0 (PyPI) and `@caveman-ai/cli` 1.3.3 (npm) registry-verified; proxy/pixel eval deferred (needs provider rewiring + manager approval). Claim scoped to passing suites — failing-suite trimming unmeasured. New `docs/loop-engine/configuration.md` holds the evidence table (with source column: local measurement vs tool self-report); `docs/opencode-shell-strategy.md` §8 holds the practices. Headroom/Caveman proxy integration and 10-task sprint measurement remain open follow-ups.
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index ee68faf..0af7a41 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -220,6 +220,23 @@ Claim: "Task complete. The code looks correct."
 - Do not claim completion without evidence.
 - For completed work, concisely restate it but do not overload with response detail.
 
+## Planning Gate (no implementation without a Brain plan)
+
+Full mode plans in Steps 1–4 and Lite Mode skips them — but neither binds
+the Hands when implementation arrives direct or on autopilot. This gate
+binds the Hands. Before writing implementation code, check one question:
+does this task carry an approved plan? Approved means one of: an
+Orchestrator blueprint, a brainstorm report, or the Manager's explicit
+quoted words (his word is the plan). Self-approval never counts. If yes,
+execute from it. If no, STOP and run one `brain_turn` planning round first
+(Architect seat minimum, full panel when cross-disciplinary), under the
+same `task_id` so history continues. Record the Brain's plan verdict plus
+the selected path in the task Execution Log (or the session/goal record
+when no task file exists) and execute from it — never from your own
+invention. Lite-eligible changes (single file, no cross-module impact,
+obvious fix, never login/auth, money, or security-surface changes) pass
+with a one-line justification in the file.
+
 ## Manual Workflow (Active Default)
 
 > Automation runs through ONE path: the Brain Bridge (`brain_turn` — see
```
<!-- END_GIT_DIFF -->
