# Task 331: Drop Replayed Items with Over-Long IDs (Luna 64-char cap)

**File:** `tasks/completed/331-drop-overlong-replay-ids.md`
**Source:** manager
**Type:** bugfix
**Status:** closed

## Goal

Stop the fatal 400 `Invalid 'input[N].id': string too long (max 64)` on
`gpt-6-luna` turns with replayed history, by dropping replayed provider
items whose `id` exceeds the provider's 64-char input limit — at send
time, preserving everything else.

## Manager's Notes

- The Manager reported the new transport error after the task-330 fix:
  `status` gone, now the `id` itself is rejected (observed length 67).
- The Manager ordered: fix it, check the docs, auto-fix. Autopilot locked
  for task 331 on 2026-10-22.
- Docs learned: OpenAI community forum thread "input item ID exceeds 64
  characters" (Oct 2026) confirms the platform itself generates item IDs
  longer than its own 64-char input limit (`string_above_max_length`);
  recovery that preserves notes/state = do not replay the offending item.
  The Responses API reference shows input item params carrying `id`;
  `status` is response-generation state, never an input field.

## Local TODOs

- [x] Root-cause the 400 (gateway-minted `rs_` + 64 hex = 67 chars;
  Luna caps input `id` at 64; Muse ignores it)
- [ ] Extend `_sanitize_replay_item` to drop items with `len(id) > 64`
- [ ] Add regression tests (drop long-id, keep normal-id byte-identical)
- [ ] Run full brain suite as verification evidence
- [ ] Deploy live, restart singleton, prove live with a crafted long-id item
- [ ] Bridge QA round (fix loop on reject, max 3)
- [ ] Bridge review round, stage diff, move to qa

## Acceptance Criteria

- [ ] A replayed reasoning item with a 67-char `id` never reaches the wire
  (dropped at send time with a logged note)
- [ ] Items with `id` within the cap pass through unchanged (F2 verbatim
  contract preserved)
- [ ] `status`-strip from task 330 keeps working (no regression)
- [ ] Full brain suite green
- [ ] Live proof: crafted long-id replay → `completed`, not 400
- [ ] QA verdict `QA_PASSED`, reviewer verdict `APPROVED`/`APPROVED_WITH_CHANGES`
- [ ] No secrets in repo or memory; ZAC holds

## Verification Evidence

- Full brain suite: 381 passed (`test_brain_bridge`,
  `test_brain_preflight`, `test_brain_capability`, `test_brain_diff_attach`,
  `test_brain_responses_alignment` incl. 2 new id-length tests).
- Live proof (2026-10-22, via proxy + Go gateway on `gpt-6-luna`): a
  scratch transcript replaying a reasoning item with BOTH a `status` key
  AND a 67-char `id` returns `completed / POISON-OK` instead of 400; the
  singleton journal records the drop. Re-verified after the QA log-hygiene
  fix with a fresh poison turn (`V2-OK`, journal shows the static-form
  message with no item fields). NOTE: two earlier scratch runs (T6-OK,
  LONGID-OK) are discounted as proof — they wrote poison rows to
  `tasks/<id>/` instead of the real `tasks/.sessions/<id>/` path, so no
  history replayed in those turns; the POISON-OK run above used the
  correct path with row-count and journal verification.
- Docs: OpenAI community forum `input item ID exceeds 64 characters`
  (`string_above_max_length`, max 64); Responses API reference input-item
  params carry `id`; reasoning guide confirms replay uses
  id/encrypted_content-bearing items.

## Risk & Rollback

- **Risk:** Dropping a reasoning item loses encrypted-context continuity
  for that turn. Contained: continuity is an optimization, not required
  input — the turn still completes, and the drop is logged per item.
- **Risk:** A provider that accepts long ids never notices. Dropping is
  still safe: the model simply reasons without that prior block.
- **Rollback:** Revert the length check in `_sanitize_replay_item` plus
  the new tests and ADR-006; old transcripts keep working on lenient
  models.

## Execution Log & Reasoning

- Root cause (verified live 2026-10-22): the Go gateway mints reasoning
  item ids of varying length (`rs_` + 50 hex observed passing,
  `rs_` + 64 hex = 67 chars observed rejected). Luna caps input `id` at
  64 chars; Muse ignores the violation. Autopilot locked for task 331.
- Docs check: OpenAI community forum thread "input item ID exceeds 64
  characters" confirms the platform generates over-limit ids itself and
  the supported recovery is to not replay the offending item; the
  Responses reference shows input item params carrying `id`.
- Honesty note: two early scratch runs (T6-OK for task 330, LONGID-OK
  here) wrote poison rows to `tasks/<id>/` instead of the real
  `tasks/.sessions/<id>/` path, so no history replayed — discounted as
  proof. Redone correctly with row-count + journal verification
  (POISON-OK + `dropping replayed reasoning item with 67-char id`).
- Assumption A1: 64 is the right cap for all strict providers (single
  observed value: Luna 400 text). If another provider caps lower, the
  constant + tests move together.
- Review (APPROVED_WITH_CHANGES, R1 low): ADR-006 understated the
  behavior (skip applies on the send path for every provider, not just
  strict ones) and the test count (three, not two) — both corrected;
  CHANGELOG entry added under [Unreleased] per repo Documentation Sync
  Rules (Tasks 330 + 331 combined, as 330 shipped without one).
- QA round 2 (after QA-requested log-hygiene fix): QA_PASSED, zero
  findings — sentinel absent from stderr, only id length + cap logged.
- PO (Manager) reply: "Approved for closure".

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `5a18324b08360e8a4ff9b4c0ae919d79860ed29f`
<!-- END_GIT_DIFF -->
