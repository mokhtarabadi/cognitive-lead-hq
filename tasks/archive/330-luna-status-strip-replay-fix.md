# Task 330: Luna 400 on Replayed Reasoning `status` — Strip at Send Time

**File:** `tasks/completed/330-luna-status-strip-replay-fix.md`
**Source:** manager
**Type:** bugfix
**Status:** closed

## Goal

Stop the fatal 400 `Unknown parameter: 'input[N].status'` on `gpt-6-luna` turns
with replayed history, by stripping volatile execution-state keys from replayed
provider items at send time — without changing capture, transcripts, or the
Brain/Hands protocol contract.

## Manager's Notes

- The Manager switched `BRAIN_MODEL` to `gpt-6-luna` and every turn with
  replayed history started failing 400; `muse-spark-1.3-contributor` never
  failed on the same transcripts.
- The Manager ordered: create a task in this project, solve it in autopilot
  mode, and check the official OpenAI docs while at it.
- Autopilot locked for task 330 on 2026-10-22: Hands chains plan → implement
  → verify → bridge-QA → bridge-review → stage → qa with no ferrying through
  the Manager. Closure still needs the explicit approval word.

## Local TODOs

- [x] Root-cause the 400 (upstream attaches `status` to reasoning output
  items; bridge replayed them verbatim; Luna validates strictly, Muse does not)
- [x] Implement `_sanitize_replay_item` + wire into `_build_request_body`
- [x] Add regression tests (strip + byte-identical fast path)
- [x] Verify against official OpenAI Responses docs (reasoning item input schema)
- [ ] Re-run full brain suite as verification evidence
- [ ] Bridge QA round (fix loop on reject, max 3)
- [ ] Bridge review round, stage diff, move to qa

## Acceptance Criteria

- [ ] A replayed reasoning item carrying `"status": "completed"` reaches the
  provider WITHOUT the `status` key, keeping `id`/`type`/`encrypted_content`
  intact (proven live: real blob + status → `completed`, not 400)
- [ ] Items without volatile keys ride the wire byte-identical (F2 verbatim
  contract preserved)
- [ ] Full brain suite green (`test_brain_bridge`, `test_brain_preflight`,
  `test_brain_capability`, `test_brain_diff_attach`,
  `test_brain_responses_alignment`)
- [ ] Official OpenAI docs confirm `status` is output-only on reasoning items
- [ ] QA verdict `QA_PASSED`, reviewer verdict `APPROVED`/`APPROVED_WITH_CHANGES`
- [ ] No secrets in repo or memory; ZAC holds (no autonomous commit)

## Verification Evidence

- `test_brain_responses_alignment.py`: 27 passed (incl. 2 new regression tests)
- Full brain files: 354 passed
- Live proof via proxy + Go gateway on `gpt-6-luna`: replay of a REAL
  provider-issued reasoning blob with `"status": "completed"` attached →
  `status: completed, T6-OK` (pre-fix shape 400d with `unknown_parameter`)
- Deployed: repo `mcp-brain-bridge/server.py` == live
  `~/.config/opencode/mcp-brain-bridge/server.py`; `mcp-brain.service`
  restarted 2026-10-22; zen-proxy audit off, healthy (200)

## Risk & Rollback

- **Risk:** Over-stripping (dropping a key a provider needs on input).
  Contained: strip list is exactly `{"status"}`; `content`/`summary`/`id`/
  `encrypted_content` pass through (live turn with `content:[]` +
  `summary:[]` returned `completed`).
- **Risk:** Old transcripts already contain `status`-carrying items.
  Covered: sanitizing happens at SEND time, so no migration is needed.
- **Rollback:** Revert the sanitizer call in `_build_request_body` plus the two
  tests and ADR-005, delete `_sanitize_replay_item` and
  `_REPLAY_DROPPED_KEYS`, and restore the F2 "replay verbatim" docstring
  line; old transcripts keep working (they replayed verbatim before — on
  lenient models).

## Execution Log & Reasoning

- QA round (2026-10-22, `gpt-6-luna` brain, autopilot): first turn asked for
  the staged diff; after `stage_and_inject_diff`, re-run returned
  `QA_PASSED` with non-blocking notes F1 (byte-level F2 exception
  documented) / F2 (strip nothing else without schema evidence) /
  F3 (send-time sanitizer covers disk transcripts) / F4 (rollback wording
  — fixed in this file before review).
- Review round (2026-10-22): Code Reviewer verdict `APPROVED` technically —
  `PO_REVIEW_PENDING`. No blocking issues; ZAC clean (no prohibited Git
  ops in hunks). PO (Manager) reply: "Approved for closure".

- Official OpenAI docs check (2026-10-22, autopilot): the Responses
  `reasoning.encrypted_content` doc states encrypted content exists to let
  reasoning items be used in multi-turn stateless conversations; the item
  shape is `{id, summary, type, +encrypted_content}`. `status` is documented
  only as *response generation* status (`completed`/`incomplete`/…), never as
  a reasoning-item input field — so stripping it at send time is
  spec-aligned, and Luna's strict `unknown_parameter` reject is correct
  server behavior, not a gateway quirk.
- Assumption A1: `status` values seen (`completed`) come from the provider,
  not the bridge — verified by capturing a raw upstream response item
  carrying both `status` and `phase` keys.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `18c33cb2bb0dccb997e3cb0d7bcfe36711c2bfa1`
<!-- END_GIT_DIFF -->
