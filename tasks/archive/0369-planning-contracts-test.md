# Task 0369: Planning contracts consolidated test

**File:** `tasks/completed/0369-planning-contracts-test.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Finished:** 2026-11-02T18:33:33Z
**Submitted:** 2026-11-02T18:11:57Z
**Started:** 2026-11-02T18:10:32Z

## Goal

One consolidated regression test file pinning the planning-stack audit findings with minimal change and zero source edits.

## Manager's Notes

Manager order (Persian): build one complete test covering all audit findings together, with Brain planning context, minimal change. Scope confirmed via question: all findings. New test file only; no source, fragment, or docs edits. Tmp-dir isolation for any planner-tool calls (never touch the real tasks/ lanes).

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Brain planning turn for the test list
- [x] Write the consolidated test file
- [x] Run it green plus run related gates
- [x] Verify functionality

## Acceptance Criteria

- [x] Single new test file covers the confirmed finding set (planner contracts plus docs-vs-reality sync)
- [x] Genuine gaps are marked xfail-strict (documented, non-breaking) rather than pinned as good behavior
- [x] No source file modified; full related gates stay green

## Verification Evidence

- **Test command:** rtk test uv run --with pytest --with "mcp<2" --with pathspec --with pyyaml pytest tests/test_planning_contracts.py -q (RTK wrapper cannot spawn in this shell — os error 2, same as prior sessions; ran the documented raw fallback)
- **Expected result:** 7 passed plus 3 xfailed, exit code 0
- **Actual result:** 7 passed, 3 xfailed in 1.28s; existing planner gates (schedule, server, prompt-sync) 170 passed
- **Exit code:** 0

> Verification runner rule: the exact command above is complete. The first run MUST use the `rtk test` prefix; a raw rerun is allowed only after a failed RTK run. RTK is known-broken in this shell (os error 2) — record the fallback if used.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Low. New test file only; worst case a brittle assertion fails on unrelated text — mitigate with behavior-level asserts and xfail for gaps.
- **Rollback plan:** Delete the new test file; nothing else changes.

---

## Execution Log & Reasoning

Autopilot locked for QA plus review (Manager order "Lock auto pilot mode brain").

QA verdict (autopilot, same session): QA_PASSED — 7 passed plus 3 xfailed, 170-test regression green, no real-lane writes, xfail reasons verified as genuine gaps. Non-blocking note: tighten F4 substring asserts when gaps close.

Review verdict (autopilot, same session): technically approved, PO_REVIEW_PENDING — single new test file, fixture mirrors existing tests, must-pass plus xfail-strict discipline, gates green. No blocking issues. Manager accept quote: "Approved for closure" — closure authorized, executing final sequence once.

Fed-context (audit, all with file:line evidence in session): F1 no Milestone writer (server.py:737-744); F2 free-text grouping; F3 deadline dual-format trap (server.py:1052-1056); F4 QA cap 1-vs-3; F5 unenforced sprint_lock; F6 unscoped sprint_stats/date-blind quota; F7 stale guide citations plus wrong Missing labels; F8 empty .plan/sprints plus dashboard-only week plan; F9 triple-owned schedule plus night WIP; F10 DoD mismatch. Reality sample: 21/21 active files in completed, 8 Estimate, 5 Deadline, 1 Milestone (M03), 0 Depends on, zero malformed headers.

Implementation notes: Brain plan verified then corrected at 5 points — C1 helper emits `# Task N:` plus `**Status:** open` plus bold headers (parser reads `**Label:**` only, server.py:286-289); C2 fixture uses monkeypatch.setenv per existing tests; C3 T8 rewritten to behavioral sprint_lock file assert (tasks/sprints/ is empty, .plan/sprints absent); C4 T2 simplified; C5 record keys are lowercase (`milestone`, server.py:367). Stack skip: plain Python planner plus pytest, no framework marker — no stack skill matched, none invented. No source file touched. Assumption A1: xfail-strict gap tests will XPASS loudly if a gap is ever fixed, which is the intended tripwire.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `5c66ad5a5b14a9ba8db97613aaaea7d63fd1c0ba`
<!-- END_GIT_DIFF -->
