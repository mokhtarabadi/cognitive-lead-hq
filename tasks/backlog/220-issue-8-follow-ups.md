# Task 220: Issue 8 follow-ups — maturity, consult-first, ranked retrieval, first promotion

**File:** `tasks/backlog/220-issue-8-follow-ups.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Goal

Track the deferred follow-ups of GitHub issue 8 (manager-decision skill remainder) from the team brainstorm. No implementation yet — do these in the future, in order.

## Manager's Notes

Vision (Manager, 2026-09-13): daily macro decisions (system design, architecture) across projects are stored smartly in one place; once enough accumulate and the digital identity matures, it is extracted as a working AI; then for simple to medium-hard questions the AI stops asking the Manager and follows similar past rulings instead. Current system stores well but does not reuse yet (27 records, substring search, profile never compiled, no consult gate).

Follow-ups (from brainstorm, also posted on issue 8):

1. Maturity levels L0–L3 with counts, coverage, override rate; human review gates promotion.
2. Consult-first rule: agent queries decisions and logs top-3 hits before asking the Manager; auto-follow above threshold, else escalate with search proof.
3. Ranked retrieval replacing substring search (filtered full-text first, embeddings later, with tests).
4. First reviewed promotion from the 27 live records: ruling clusters + dissent notes + expiry dates.
5. Deferred: full doppelganger runtime (unsafe at 27 records).

Risks tracked: stale auto-apply, false matches, redaction leaks, promotion drift.

## Local TODOs

- [ ] Define maturity levels L0–L3
- [ ] Enforce consult-first with logging
- [ ] Ship ranked retrieval with tests
- [ ] Run first reviewed promotion
- [ ] Verify functionality

## Acceptance Criteria

- [ ] Each follow-up has done criteria before implementation starts
- [ ] Issue 8 closes after the first reviewed promotion lands

## Verification Evidence

- **Test command:** _(fill during execution)_
- **Expected result:** _(fill during execution)_
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

## Definition of Done

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** premature auto-follow on sparse data
- **Rollback plan:** keep human gate until maturity threshold passes; promotion is append-only

---

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
