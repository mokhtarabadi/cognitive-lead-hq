# Task 187: Auto-load persona in system prompt with speaker label

**File:** `tasks/completed/187-auto-load-persona-speaker-label.md`
**Source:** manager
**Type:** feature
**Status:** closed

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
**Factual Git Diff:** Stored in Commit Hash: `a426922a4d4018330c39da2c698d57614a22b51a`
<!-- END_GIT_DIFF -->
