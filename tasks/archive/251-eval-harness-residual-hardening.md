# Task 251: Eval Harness Residual Hardening

**File:** `tasks/completed/251-eval-harness-residual-hardening.md`
**Source:** manager
**Type:** improvement
**Status:** open
**Mode:** autopilot-locked

## Goal

Harden the eval harness against the two low residual risks deferred at review time.

## Manager's Notes

Full-automatic mode applies (stored order `manager/full_automatic_mode`, zero questions). Code Reviewer follow-up recommendations, accepted as non-blocking at closure: (1) wrapper-prefixed ZAC commands such as absolute-path git invocations evade `_op_is_zac`, which only matches bare heads; (2) cost/latency aggregation accepts booleans via int coercion, so invalid numerics enter aggregates. Scope is `mcp-brain-bridge/eval_harness.py` plus tests only; authority retrieval untouched.

## Local TODOs

- [x] Add failing tests first for absolute-path git detection and boolean cost/latency rejection
- [x] Normalize operation commands (basename absolute paths) in the ZAC scanner
- [x] Reject boolean and non-finite cost/latency values in aggregation
- [x] Run the full suite with exit code 0
- [x] Update CHANGELOG via Parse-Then-Append
- [x] Lint the task file, stage, move to qa, re-stage

## Acceptance Criteria

- [x] Absolute-path git commands are flagged by the ZAC scanner
- [x] Boolean and non-finite cost/latency values are excluded from aggregates
- [x] Full test suite passes with exit code 0

## Verification Evidence

- **Test command:** `rtk test uv run --with pytest --with 'mcp[cli]==1.30.0' --with pathspec --with pyyaml pytest tests/ -q`
- **Expected result:** all tests pass, exit code 0
- **Actual result:** 508 passed, 10 warnings (pre-existing), focused eval+golden 30/30
- **Exit code:** 0 (captured via `echo $?` after the rtk run)

## QA Evidence Hotfix (Round 1 Rejection Response)

- **TDD RED run (factual, first-hand):** after appending the 6 new tests and before touching `eval_harness.py`, ran `rtk test uv run --with pytest --with 'mcp[cli]==1.30.0' --with pathspec --with pyyaml pytest tests/test_eval_harness.py -q` → 5 failed (`test_zac_detects_absolute_path_git_command`, `test_zac_detects_sudo_git_command`, `test_aggregate_rejects_boolean_cost_and_latency`, `test_aggregate_rejects_non_finite_cost_and_latency`, `test_mean_ignores_boolean_and_non_finite_values`), 19 passed. The prose-guard test passed pre-fix (already-clean behavior, kept as regression guard). No git-history proof exists (work uncommitted at RED time); this session-observed output is the factual record.
- **Full suite (factual):** `rtk test uv run --with pytest --with 'mcp[cli]==1.30.0' --with pathspec --with pyyaml pytest tests/ -q` → `508 passed, 10 warnings`, `exit=0` (re-run to capture exit code explicitly; warnings pre-existing).
- **Scope:** `git diff --name-only` shows only `mcp-brain-bridge/eval_harness.py`, `tests/test_eval_harness.py`, `CHANGELOG.md`, plus this task file. Goldens untouched.

## QA & Review Record

- **QA round 1:** QA_REJECTED (evidence-only: F1/F2 PASS; F4/F5 failed on missing RED record and exit-code capture in the evidence supplied to the Brain).
- **Evidence hotfix:** RED run + exit=0 recorded factually above; re-staged.
- **QA round 2:** QA_PASSED (F1-F5 all PASS).
- **Review:** APPROVED + PO_REVIEW_PENDING, zero blocking issues. One non-blocking note: `math.isfinite()` can raise `OverflowError` on arbitrarily large Python ints — normal cost/latency values unaffected; future guard (ints direct, isfinite floats-only) if huge-int inputs ever become supported.
- **Closure authorization:** Approved for closure (standing Manager order `manager/full_automatic_mode`: reviewer technical APPROVED + PO_REVIEW_PENDING counts as closure approval).

**Status:** closed

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** stricter validation could reject traces that current callers emit.
- **Rollback plan:** revert the feature commit hash; harness is pure so rollback is safe.

---

## Execution Log & Reasoning

TDD red-green under full-auto standing order (`manager/full_automatic_mode`; Brain plan advisory Markdown, approval pause skipped and logged). Discovery via 2 parallel read-only subagents mapped `_op_is_zac` head-match evasion, bare-isinstance cost/latency filters, and missing edge coverage (no absolute-path/bool/nan tests; goldens finite-only, unaffected). Wrote 6 tests first: RED 5 failed / 1 passed (prose guard already green). GREEN: `_exec_is_git` basename + sudo-shift in `_op_is_zac` (replaces `_ZAC_HEADS` head-tuple match; verified equivalent on bare forms, zero remaining `_ZAC_HEADS` refs); `_is_finite_number` (bool reject + `math.isfinite`) backing `_mean` and both aggregate filters; per-row columns still preserve raw values. Focused eval+golden 30/30, full suite 508 passed exit 0 via `rtk test`. CHANGELOG appended under Unreleased/Fixed. AC/DoD boxes checked in summary phase per mandate.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `07a7f1baf01ba8e2cbf059e0f0864e8187ebb351`
<!-- END_GIT_DIFF -->
