# Task 183: Dynamic readable admin-bound output — industry best practices

**File:** `tasks/completed/183-dynamic-readable-admin-output.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Upgrade the language of everything sent to Admin/Manager to be dynamic, skimmable, and easy to read, following industry best practices.

## Manager's Notes

Manager requirement: the output sent to Admin can be improved — make the language more dynamic and easier to read, using industry best practices. Builds directly on the Task 180 dual-channel contract (short sentences, ban list, reference codes) — this task goes further into admin-bound message design: status cards, progressive disclosure (headline first, details on demand), action-oriented framing (what was decided, what is needed from Admin), consistent structure across Brain and Hands handoffs. Research how leading agent products format human-bound updates (Anthropic, OpenAI, Devin-style status reports) and encode the best patterns into the system prompt fragments and `agents/cognitive-executor.md` handoff rules. Must not weaken machine-path comprehensiveness.

Scope update (manager-approved plan, 2026-09-11): after live discussion the manager redefined this task as Always-English simple output — our chat proved simple English is far more readable for him than any template. The template/progressive-disclosure design is dropped; the Always-English rules below replace it.

## Local TODOs

- [x] Research English-reasoning best practices (spider sweep: ICLR 2026 budget-alignment, ACL Think Natively, arXiv 2608.08447)
- [x] Encode Always-English + Think-in-English + simple vocabulary into prompt fragment + executor handoff rules
- [x] Add input-output language map (any input language → simple English answer)
- [x] Verify machine path (XML, reasoning logs) stays fully comprehensive (exemptions explicit)

## Acceptance Criteria

- [x] Manager-facing output always simple English regardless of input language (fragment 13 + executor handoff rule)
- [x] Think-in-English rule encoded for internal reasoning (research-backed, accuracy-preserving)
- [x] Machine-path comprehensiveness provably intact (Persian quotes/verbatim evidence explicitly exempt; no XML or reasoning-log text touched)

## Verification Evidence

- **Test command:** `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check183.md && diff /tmp/check183.md system-prompt.md && echo SYNC_OK; grep -c "simple everyday words" system-prompt.md agents/cognitive-executor.md`
- **Expected result:** `SYNC_OK`, count 1 in each file
- **Actual result:** `SYNC_OK`, 78576 bytes, count 1 in each file
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Template rigidity makes nuanced updates harder to express.
- **Rollback plan:** Revert fragments + executor from git history, regenerate prompt.

---

## Execution Log & Reasoning

Implemented the manager-approved Always-English plan (2026-09-11). Research via blowsh spider sweep: ICLR 2026 budget-alignment (English is the native reasoning language, forcing it preserves accuracy), ACL Think Natively, arXiv 2608.08447; plain-English side saturated at generic guides. Edits: `13-constraints.md` Response Clarity extended (always answer simple English, think in English, simple everyday words, machine channels exempt); executor handoff rule extended the same way plus a Negative Patterns bullet (never answer in another language; Persian quotes in task files are evidence). Bumped 9.20.0 → 9.21.0, reassembled (78576 bytes, SYNC_OK byte-identical), CHANGELOG `## [9.21.0]` entry. No XML, reasoning-log, or template text touched — machine path intact by construction.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `c492e17955185c3a1708d8171ff771ffc1f13f0d`
<!-- END_GIT_DIFF -->
