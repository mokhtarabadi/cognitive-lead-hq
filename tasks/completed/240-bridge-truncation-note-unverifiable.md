# Task 240: Bridge truncation note orders Brain to read_file it cannot call

**File:** `tasks/completed/240-bridge-truncation-note-unverifiable.md`
**Source:** manager
**Type:** bug
**Status:** closed

> Manager accept (exact): "Approved for closure" — closure gate verified (file in tasks/qa + PO_REVIEW_PENDING logged).

## Goal

Fix the `[changed-hunks]` truncation note so a QA/reviewer Brain never rejects on unseen evidence.

## Manager's Notes

Manager order (exact): "fix; https://github.com/mokhtarabadi/cognitive-lead-hq/issues/14". Zero-guess evidence in the issue: the note orders the Brain to `pull remainder via read_file`, the Brain has zero tool calls in QA turns (its own admission), round-1 QA_REJECTED on unseen scope should have been UNVERIFIABLE. Minimal prompt-side fix: (1) reword note — mark unseen scope UNVERIFIABLE, never REJECTED past truncation; (2) drop the read_file instruction to the Brain, address pulls to the Hands (verdict quotes needed paths, Hands pulls via brain_read_file/grep before re-QA). No commit, no close without the exact approval word.

## Local TODOs

- [x] Reword truncation note in `_build_changed_hunks`
- [x] Update/extend tests for new wording
- [x] Full suite green + CHANGELOG entry
- [ ] Lint + stage + qa + Brain QA/review

## Acceptance Criteria

- [x] Note no longer instructs the Brain to call read_file
- [x] Note orders UNVERIFIABLE-not-REJECTED for unseen scope
- [x] Pull path addressed to the Hands (quote paths, Hands pulls)
- [ ] Tests cover new wording; suite green; Brain QA passes

## Verification Evidence

- **Test command:** `uv tool run --with mcp==1.4.1 --with pathspec --with pyyaml --with pytest pytest tests/ -q` (+ focused `-k "truncation or unclosed"`)
- **Expected result:** focused + full suites exit 0
- **Actual result:** focused 171 passed; full **381 passed**, zero failures; new test `test_build_diff_attach_truncation_note_is_unverifiable` asserts UNVERIFIABLE wording, no REJECTED order, no Brain read_file instruction, Hands pull path
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** prompt-wording change alters Brain verdict behavior beyond the truncation case
- **Rollback plan:** revert the note string; wording-only change, no logic touched

---

## Execution Log & Reasoning

Seat Check: Senior Programmer (bridge prompt wording + regression test; no UI/schema/sprint triggers — Designer/Architect/Planner/Strategist skipped with reason). Replayed from DEC-20260914-003 (standing autopilot) + DEC-20260915-001 (fix-all). Edit: `_build_changed_hunks` truncation note + docstring — wording only, no logic touched (`rel` still used in the return block). CITE: mcp-brain-bridge/server.py truncation note; tests/test_brain_diff_attach.py new test.
- Full-context QA turn flaked EMPTY (transport, not counted as rejection); lean retry: VERDICT QA_PASSED (F1-F4 wording/pull-path/test/suite, minor note: no negative check for old phrase — non-blocking).
- Reviewer: PO_REVIEW_PENDING (technical approval, no blocking issue; R1 low: clearer visible-scope phrase in a future edit). Closure needs exact words "Approved for closure" or "Close task". File stays in tasks/qa. No commit.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `4264c4ad24ed22f71a360ea8d929b7879245bcdb`
<!-- END_GIT_DIFF -->
