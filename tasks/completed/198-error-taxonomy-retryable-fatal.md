# Task 198: Transport error taxonomy (retryable vs fatal)

**File:** `tasks/completed/198-error-taxonomy-retryable-fatal.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Tag transport errors retryable/fatal: retry only retryable, fail fast on fatals.

## Manager's Notes

From Brain round-2 self-improvement (N6 delta). The retry wrapper already retries 429/5xx + timeouts; this task makes the taxonomy explicit: retryable (429, 500/502/503/504, timeouts, transport errors) vs fatal (400, 401, 403, 404 — fail immediately with a precise error, never burn 3 attempts). Implement in both servers' post paths + mocked tests for each class. Standing authorization: autopilot + autoclosure, execute without asking.

## Local TODOs

- [x] Encode taxonomy (retryable set vs fatal set) in both servers
- [x] Fail-fast path for fatals (no retry, precise error)
- [x] Mocked tests per class, full suite green
- [x] Update CHANGELOG, lint, stage, qa, autopilot QA/review, autoclose

## Acceptance Criteria

- [x] 429/5xx/timeouts retry (existing behavior kept); 400/401/403/404 fail on first attempt
- [x] Fatal errors carry status + path + snippet, never the key
- [x] Mocked tests cover both classes in both servers, full suite green

## Verification Evidence

- **Test command:** `uv run --project mcp-brain-bridge --with pytest --with pathspec pytest tests/ -q`
- **Expected result:** all pass, exit 0
- **Actual result:** 201 passed (185 + 16 new taxonomy tests: 8 bridge + 8 decision), 0 failed
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Misclassifying a transient error as fatal (or vice versa) changes retry behavior
- **Rollback plan:** Revert to the current retry sets; taxonomy is centralized in one constant per server

---

## Execution Log & Reasoning

Hotfix (live QA_REJECTED round 1, honored in full): F1 dead _FATAL_STATUS constant → DOCUMENTATION ONLY comment (branch matches 4xx range directly, set names common members kept for tests); F2 5xx-subset → documented INTENTIONALLY NARROW, no-expansion (behavior unchanged); F3–F9 per-class tests — 8 bridge + 8 decision DIRECT _post unit tests (fatal-403/404/422 calls==1 with 'no retry', retryable-429→200 attempts==2, timeout→200, message-contract status+path+snippet present + planted SECRET absent, sleep-skipped-on-fatal, non-httpx ValueError propagates unwrapped). Taxonomy-only: 22 passed (6 old + 16 new). Full suite: 201 passed, exit 0. QA re-test next (rejection #1 banked, escalation at 3rd).

QA re-test: QA_PASSED ([QA Engineer] + reasoning_log, REPORT no XML — correct on pass). F1–F8 each closed individually with tests; suite 201 green. Reviewer: APPROVED ([Code Reviewer] + reasoning_log, REPORT no XML — correct on approval). R1–R4 Low severity, no AC breach ('Accept now. Bound snippet later.'). Autoclosing under standing autopilot+autoclosure.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `dff442a6d54678153cb6b962345252dda438b82e`
<!-- END_GIT_DIFF -->
