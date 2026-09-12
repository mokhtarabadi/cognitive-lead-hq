# Task 201: Brain QA reviewer turns always carry changed hunks plus modes doc

**File:** `tasks/completed/201-brain-qa-reviewer-turns-carry-hunks-modes-doc.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

QA and reviewer Brain turns must always include the changed hunks (Factual Git Diff content), and manual/autopilot modes must be documented in README.

## Manager's Notes

QA/reviewer turns must always carry the changed hunks or factual diff. The model must see what changed and judge from it, not guess. Implement on autopilot: run the Brain loop without asking the manager anything, notify only when approval is needed. Also teach the manager the mode switch words (manual vs autopilot, how to lock each) and record the manual mode in README.

## Local TODOs

- [x] Add include_diff path to brain_turn with tests
- [x] Mandate include_diff on QA/reviewer turns in Hands protocol (agents/cognitive-executor.md — verified NOT a system-prompt build input, so no rebuild/version bump needed)
- [x] Document manual/autopilot modes + switch words in README
- [x] Run brain QA reviewer loop, stage, move to QA

## Acceptance Criteria

- [x] brain_turn accepts include_diff and appends diff content when the task file resolves (capped, fail-safe)
- [x] QA/reviewer turns are mandated to pass include_diff through the Hands protocol
- [x] Tests cover present/absent/unresolvable/over-cap diff cases and pass
- [x] README documents manual vs autopilot modes and the exact switch words
- [x] Full suite passes with exit code 0

## Verification Evidence

- **Test command:** uv run --project mcp-decision-server python -m pytest tests/ -q
- **Expected result:** all tests pass, exit code 0
- **Actual result:** 264 passed (252 prior + 8 diff-attach + 2 fence-guard + 2 fail-safe tests)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Larger prompts on QA turns; diff content could crowd the input budget
- **Rollback plan:** Revert the bridge server hunk and the fragment line; default include_diff off keeps tiny calls unchanged

---

## Execution Log & Reasoning

**Autopilot locked** for this order (manager: run on autopilot, ask nothing, notify only on approval need). No questions asked during execution.

- **Red:** wrote `tests/test_brain_diff_attach.py` first (8 tests) — failed on missing `extract_task_diff`/`build_diff_attach`, as designed.
- **Green:** `mcp-brain-bridge/server.py`: new `_TASK_DIFF_CAP = 20000`; pure `extract_task_diff(text)` (multi-block join, unclosed-BEGIN cuts to EOF); `build_diff_attach(task_id)` (resolve → read → extract → cap with truncation note → labeled ```diff fenced block; empty/unresolvable never fail the turn); `brain_turn(..., include_diff=False)` appends the hunks block after the user prompt when `include_bundle and include_diff and task_id`. New tests 8/8, full suite **260 passed exit 0**.
- **Protocol:** `agents/cognitive-executor.md` state-machine Build step now mandates `include_diff=True` on QA/reviewer turns; new Modes section (manual default vs locked autopilot, exact switch words, one-line lock announcements, lock recorded in task file). Verified via assembler source that this file is NOT a system-prompt build input — no rebuild or version bump required.
- **README:** new Modes subsection under the manual workflow (manager-facing wording, switch words, how-you-always-know rule).
- **Assumption A1:** default `include_diff=False` keeps tiny calls unchanged; the mandate lives in the Hands protocol per the manager's "always" for QA/reviewer turns specifically.
- **QA Round (brain_turn, task_id 201, verbatim code pasted; one empty-REPORT retry): QA_PASSED.** Findings: F1/F2 verified on disk (extract multi-block join, build never-raises, mandate wording); F3 low-risk accepted and fixed — the ```diff fence in `build_diff_attach` was not escape-guarded (embedded fences in diff bodies could close the block early), mirrored the existing V1 ZWSP guard from the task attach; added 2 tests (fence break, empty-whitespace pair). Full suite now **262 passed exit 0**.
- **Verification Evidence:** `uv run --project mcp-decision-server python -m pytest tests/ -q` → 262 passed, exit 0 (run from repo root; needs `--with pytest --with pathspec --with pyyaml --with mcp==1.30.0` on bare envs — pre-existing gaps).
- **Reviewer Round (CHANGES_REQUIRED + hotfix XML, executed):** F1 (no diff arrived — my caller tool has no `include_diff` parameter; server flag proven working on disk at 7947 chars), F2 (guard line not shown — now proven: identical ZWSP line at server.py:290 V1 and server.py:350 diff attach), F3 (default-False loophole — closed by fail-safe), F4 (caller schema — server `@mcp.tool()` at server.py:911 exposes `include_diff`; the missing piece is only the Hands session harness outside this repo, covered by the fail-safe), F5 (modes doc-only — now explicit in both files). Hotfix: new pure `_failsafe_qa_attach` helper + auto-attach with stderr warning on QA-like prompts without the flag; 2 new tests. Full suite now **264 passed exit 0** (12/12 diff-attach).
- **Reviewer Round 2 (APPROVED, technically PO_REVIEW_PENDING — no autoclosure, reviewer defers to Manager):** re-review with verbatim helper (server.py:360-373) + call site (server.py:994-1008) pasted. S1-S4 strengths (non-string prompt/id safe, try/except with stderr log, normal contract intact). F1-F4 all Low: guard lines not re-pasted (proven earlier at server.py:290/350), fail-safe requires bundle True (QA mandate keeps it True), full task diff not in channel (process gap, not code defect), Modes text not re-pasted (doc-only). Verdict: fail-safe closes F3, normal-turn contract intact, code approved technically. PO (Manager) asked to reply "Approved for closure".

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `66c12bc6f2a6e1dd9a5b8320346ef0c101558dad`
<!-- END_GIT_DIFF -->
