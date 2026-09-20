# Task 248: Manager-Decision Tools Repair (extract + record failures)

**File:** `tasks/completed/248-manager-decision-tools-repair.md`
**Source:** manager
**Type:** bug
**Status:** closed
**Mode:** autopilot-locked

## Goal

Repair the manager-decision tool chain so session extraction, decision recording, and profile consult work again.

## Manager's Notes

Full-automatic mode applies (stored order `manager/full_automatic_mode`, zero questions). Manager has no session access. Work task-by-task with Brain on every step: Brain plans, hands implement, Brain QAs, Brain reviews. Reviewer technical APPROVED + PO_REVIEW_PENDING counts as closure approval. Observed symptoms to fix: repeated profile read failures, decision record failures, decision recall failures. File the fix in this automatic multi-task flow. Report bugs and learnings via decision records, or via task-file logs and messages when the record tools themselves are broken.

Approved for closure.

## Symptoms (observed, factual)

- `extract_session_decisions` with task id 247 failed twice with a tool-side model-output shape error (malformed tradeoffs field). No candidates queued, nothing written.
- `record_manager_decision` with decision dict payloads failed three times with `'str' object has no attribute 'get'`. Nothing persisted.
- `get_manager_profile` returns an explanatory message instead of profile content when the sample is absent, which degrades the consult-first flow.
- Impact: the B2 auto-capture-on-close rule and the consult-before-asking rule cannot run. Autopilot decisions that depend on replayed rulings lose their lineage source.

## Local TODOs

- [ ] Reproduce each failure against the decision server with minimal inputs
- [ ] Trace the shape mismatch to the exact validation/extraction code path
- [ ] Fix with TDD red-green (failing test first, minimal fix, re-run)
- [ ] Run the full suite with exit code 0
- [ ] Update CHANGELOG via Parse-Then-Append
- [ ] Lint the task file, stage, move to qa, re-stage

## Acceptance Criteria

- [x] `extract_session_decisions` returns candidates or a clean empty result, never a shape crash
- [x] `record_manager_decision` persists a valid decision and returns its id
- [x] `get_manager_profile` consult path behaves predictably with and without a sample
- [x] Regression tests cover each fixed failure
- [x] Full test suite passes with exit code 0

## Verification Evidence

- **Test command:** `uv run --with pytest --with "mcp[cli]==1.30.0" --with pathspec --with pyyaml pytest tests/ -q`
- **Expected result:** all tests pass, exit code 0
- **Actual result:** 452 passed (434 existing + 18 new), 10 warnings (pre-existing pathspec deprecation)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** decision store is append-only personality infrastructure; a wrong fix could write malformed records.
- **Rollback plan:** revert the feature commit hash; malformed writes are corrected with tombstone records, never in-place edits.

---

## Execution Log & Reasoning

- Authorization basis: stored standing order `manager/full_automatic_mode` (zero questions, task-by-task with Brain) plus this task's own Manager's Notes directing Brain-plan/hands-implement flow. No invented pre-approval; Brain plan stayed advisory Markdown.
- Brain discovery (2 read-only subagents) mapped exact crash sites; Brain plan (Software Architect, Markdown, no XML) selected: drop-malformed-candidate in extract, mapping guards in record, skip-tampered in recall, no profile change.
- Design decision (hands, logged): kept the N1 one-repair path and all fail-loud transport errors intact (existing Task 191 tests unchanged). Only the item-level non-string-tradeoffs case converts from raise to drop-with-stderr-note, because it is malformed model output, not transport failure. Alternatives-type mismatches still raise in extract (existing contract); record rejects them with ValueError before any write.
- TDD red-green: 6 new tests in tests/test_decision_server.py appended (extract mixed valid+bad returns valid only; extract all-bad returns []; record string verbatim_quote/extracted_decision/alternatives each raise ValueError with zero files written; query over tampered stored record skips it without crash). All 6 RED pre-fix (including the exact field AttributeError), all 6 GREEN post-fix.
- GREEN fixes in mcp-decision-server/server.py: `_scrub_free_text` isinstance guards (verbatim_quote/extracted_decision mappings, alternatives list) raising ValueError; `_validate_extracted_candidates` drops non-string-tradeoffs candidates in place with stderr note + docstring; `query_manager_decisions` skips non-dict records/sub-objects and non-list alternatives with stderr notes.
- get_manager_profile absent-sample message confirmed intentional and tested; no production change there.
- Verification: full suite 440 passed, exit 0.
- QA hotfix (QA_REJECTED F1 profile coverage, F2 nested leaf validation — both accepted as real gaps): added 2 profile contract tests (absent exact message, present content — GREEN by design, pinning intentional behavior) plus 6 malformed-leaf tests (5 parametrized text leaves + non-string alternative item, all RED pre-fix with silent coerce-and-persist, GREEN post-fix). Production: `_scrub_free_text` now string-type-checks all 5 text leaves and every alternatives item, raising field-named ValueError before any write.
- QA hotfix 2 (QA_REJECTED F1 falsey alternatives — accepted, real defect): `query_manager_decisions` used `extracted.get("alternatives", []) or []` before the isinstance check, laundering falsey non-lists (None/""/0/False) into valid []. Added 4-case parametrized test (all RED pre-fix), fixed with raw-value isinstance check before normalization. Full suite 452 passed, exit 0; compileall clean.
- Reviewer: technical APPROVED + PO_REVIEW_PENDING, zero blocking issues. One non-blocking doc note (extra paren in `_validate_extracted_candidates` docstring) deferred to future cleanup — left untouched post-QA to keep the audited diff intact.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `7eeee61aec78b1a32c19fb335c53c860eb1ab099`
<!-- END_GIT_DIFF -->
