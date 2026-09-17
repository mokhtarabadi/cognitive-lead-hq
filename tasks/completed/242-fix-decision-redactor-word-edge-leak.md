# Task 242: Fix decision-redactor word-edge credential leak (B1)

**File:** `tasks/completed/242-fix-decision-redactor-word-edge-leak.md`
**Source:** manager
**Type:** bug
**Status:** closed

## Goal

Close the credential-leak path in `mcp-decision-server/redactor.py`: `BRAIN_API_KEY=...`-style names and short `Bearer` tokens pass `verify_clean` today, and the store is append-only with no delete path.

## Manager's Notes

Repair guide order: start B1; no Bridge changes until B1 is green. Reproduce first, then fix, then extend tests to KEY=value / colon / quoted forms. Acceptance: no secret string passes `verify_clean`. Per-task checklist: offline unit green, 40-message bound, no global writes, Handoff Note at close.

## Local TODOs

- [x] Read `mcp-decision-server/redactor.py` + existing redactor tests
- [x] Reproduce: `BRAIN_API_KEY=sk-...` and short `Bearer abc123` through `verify_clean`
- [x] Fix word-boundary regex + Bearer minimum length
- [x] Extend tests to KEY=value / colon / quoted forms
- [x] Full suite green + lint + stage + qa + Brain QA/review

## Acceptance Criteria

- [x] No secret string (`KEY=value`, colon, quoted, short Bearer) passes `verify_clean`
- [x] Full test suite passes with exit code 0
- [x] QA and reviewer verdicts recorded

## Verification Evidence

- **Test command:** `uv tool run --with "mcp==1.4.1" --with pathspec --with pyyaml --with pytest pytest tests/ -q`
- **Expected result:** all pass, exit 0
- **Actual result:** decision suite **105 passed** (101 baseline + 4 new B1 tests), exit 0. Reproduce-first proof via inline old-vs-new regex check: old `\b` edge misses `BRAIN_API_KEY=sk-test-...` and `FOO_SECRET=hunter2` (both False = leak), new `(?<![A-Za-z0-9])` edge catches both (True), `topsecret=x` stays untouched (False = no over-redact).
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** regex change over-redacts legit text; append-only store means a bad record cannot be deleted
- **Rollback plan:** revert `redactor.py` via worktree diff; no store writes during this task (offline tests only)

---

## Execution Log & Reasoning

Seat Check: Senior Programmer (credential-scrub regex + offline tests). Skipped Designer, Planner, Strategist (no UI/schema/sprint triggers); QA/Reviewer judge later bridge turns.
Replay lineage: Replayed from DEC-20260914-003 (2026-09-14): standing full-autopilot zero questions. Repair-guide order: start B1; no Bridge changes until B1 green.
Worktree truth on entry: B1 code fix + 4 tests + CHANGELOG bullet already present as uncommitted changes (parallel session); this run verified rather than re-implemented. Verified: (1) reproduce via old-vs-new pattern check — old edge leaks both ENV-style strings, new edge catches them, `topsecret=x` untouched; (2) `redactor.py:41,50` new edge in sanitize + verify patterns; `redactor.py:31-32` short-Bearer `{4,7}` digit-gated rule, `{8,}` rule unchanged; (3) 4 new tests in `tests/test_decision_server.py` (env-style names, short digit Bearer, prose no-FP guard, raw-detect); (4) decision suite 105 passed exit 0; (5) CHANGELOG B1 bullet present. No store writes (offline tests only) per rollback plan.
QA-hotfix dispute (live Brain VERDICT QA_REJECTED, F1/F2): F1 does NOT reproduce — direct evidence `sanitize_text('Authorization: Bearer abcd-1')` → `'Authorization: Bearer [REDACTED]'`, `verify_clean` True, because `-` is inside the token class `[A-Za-z0-9\-._~+/=]` so greedy `{4,7}` consumes `abcd-1` fully (no `\b`-before-`-` partial match exists). The 4 ordered regression tests were added first per TDD and ALL PASS pre-fix (incl. the punctuation test) — no RED possible, no behavior change warranted; Step 4 rule rewrite correctly NOT applied (editing correct code on a false premise would risk real regressions). Tests kept as behavior locks. Residual noted for Brain re-QA (no code change): tokens containing out-of-class chars (e.g. `Bearer abcd!1`) evade both sanitize and verify symmetrically — future hardening scope, not this hotfix. F2 quoted/topsecret tests added and green. Full suite: 400 passed exit 0. Skill deviation logged: loaded `testing-strategy` only; `project-memory`/`manager-decision`/`versioning-and-release` contents already live this session, `code-search` unneeded (files known), `verification-before-completion`/`task-lint` enforced via tools.
Re-QA verdict (live Brain, full context): VERDICT QA_PASSED. F1 REFUTED by the Brain itself (`-` inside token class, `abcd-1` consumed whole; CITE redactor.py:31). F2 CONFIRMED (quoted = and : tests; CITE test_decision_server.py:149,155). F3 CONFIRMED (topsecret=x; CITE :161). F4 no remaining B1 defect (`abcd!1` out-of-alphabet = future scope). 400 passed exit 0, no store writes. Review note R1 (resolve before closure): attached diff also holds Task 243 files (.env.example:26, decision server.py:219, tests :487) — 242 closure commit must be scoped to 242 files only; 243 files stay for 243's own closure. QA self-improvements: H1 per-task manifests; H2 executable repro before hotfix; H3 boundary lengths 3/4/7/8.
Reviewer verdict (live Brain, full context): APPROVED, PO_REVIEW_PENDING (CITE redactor.py:31/41/50, tests :149/155/161; R1 Medium repeats closure scoping — 242 feature commit = redactor + 242 tests + 242 CHANGELOG entry only, via selective unstage at closure).
Closure accept (exact Manager quote): Approved for closure, chose the option you are think is better. Choice B executed: close 242 now (fully approved, waiting) rather than hold it for 243's QA cycle; shared tests/test_decision_server.py + CHANGELOG.md hunks ride with the 242 commit (both suites green, bullets labeled per task) and are logged here for 243's closure record; 243-only files (decision-server/server.py, .env.example, 243 task file) unstaged before the commit.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `84ce325025fb9cf3722b3f95fcf36a3685d6b1c6`
<!-- END_GIT_DIFF -->
