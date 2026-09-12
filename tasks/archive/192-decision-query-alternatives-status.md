# Task 192: Decision query searches alternatives and status fields

**File:** `tasks/completed/192-decision-query-alternatives-status.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Extend `query_manager_decisions` so it also matches the `alternatives[]` array (and any status field), closing the documented recall gap where valid hits are missed.

## Manager's Notes

From the Brain self-improvement review (Task 190, live `brain_turn`), ranked R2. Proven live: a query for a term present only in `alternatives[]` misses, by design per the docstring. Change the design: alternatives are first-class searchable content.

## Local TODOs

- [x] Extend the query matcher to `alternatives[]` (and status field if present)
- [x] Update the tool docstring (remove the exclusion note)
- [x] Add regression test: term only in alternatives[] must hit
- [x] Verify full decision suite still green

## Acceptance Criteria

- [x] A keyword present only in `alternatives[]` returns the decision
- [x] Existing query behavior (summary/rationale/tradeoffs/quotes) unchanged
- [x] Docstring documents the full searched-field list

## Verification Evidence

- **Test command:** `uv run --project mcp-decision-server --with pytest --with pathspec pytest tests/test_decision_server.py -q`
- **Expected result:** all pass, including the new alternatives-hit test
- **Actual result:** `63 passed` (62 existing + new `test_query_hits_term_only_in_alternatives`), including honest red-green cycle (first assertion drafted against display text, corrected to match-behavior)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** More matches per query (slightly noisier results).
- **Rollback plan:** Revert the matcher diff; alternatives[] becomes invisible again.

---

## Execution Log & Reasoning

Implementation: `mcp-decision-server/server.py` `query_manager_decisions` haystack now joins `extracted.alternatives[]` (None-safe via `or []`, each item `str()`-coerced) alongside summary/rationale/tradeoffs/quotes; docstring updated to list alternatives. Schema has no status field (checked `decision.schema.json`), so the conditional "(and status field if present)" TODO is vacuous — noted, no code for a nonexistent field. Regression test `test_query_hits_term_only_in_alternatives` records a decision whose unique keyword lives only in alternatives[] and asserts the query returns that decision (red-green: first assertion targeted display text, corrected to match behavior). Full decision suite: 63 passed, exit 0. Existing query behavior unchanged (all 62 prior tests green untouched).

State-machine closure (goal: auto-close if brain APPROVED): fresh `brain_turn` QA (task_id 192, full file + complete diff pasted) returned **QA_PASSED** (F1 None-safe, F2 str-coerce, F3 wrong-type degraded-recall out-of-contract, F4 empty-query unchanged, F5 category untouched; A1–A3 non-blocking hardening notes; status handling honest). Reviewer `brain_turn` (retry once after an empty REPORT) returned **APPROVED → PO_REVIEW_PENDING** (S1–S3; I1/I2 doc/changelog hunks verified on disk: server.py:422 lists alternatives, CHANGELOG.md:16 carries the entry; I3 TODO ticks fixed at closure). Autoclosed under the goal authorization.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `ca0ddf62aed75222a963ff37c8253fed802dbed8`
<!-- END_GIT_DIFF -->
