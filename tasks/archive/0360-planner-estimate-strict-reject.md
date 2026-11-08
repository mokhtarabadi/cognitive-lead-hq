# Task 0360: Planner estimate header strict reject

**File:** `tasks/completed/0360-planner-estimate-strict-reject.md`
**Source:** manager
**Type:** bug
**Status:** closed
**Finished:** 2026-10-28T22:55:17Z
**Started:** 2026-10-28T22:49:19Z

## Goal

Close the last silent estimate hole: a hand-written `**Estimate:** 1h 30m` must book nothing instead of a truncated prefix, with the lint gate as the loud channel.

## Manager's Notes

> One process note: the Planner only accepts estimates like 1.5h, not 1h 30m — it silently drops the malformed kind, so a task written that way vanishes from capacity.

> yes (chose "Strict reject instead" over "Parse Xh Ym properly")

## Findings (grounded)

- F1: `mcp-planner-server/server.py:243` prefix-matched `(\d+(?:\.\d+)?)\s*h` case-insensitively, so `1h 30m` booked 1.0h with no warning. `schedule_tasks` loud-rejects the same input (all-or-nothing abort), and the lint gate (`_PLANNER_ESTIMATE_RE`, `^\d+(?:\.\d+)?h$`) already fails it at stage time — the parser was the only silent path (legacy files, out-of-band edits).
- F2: the one failing suite test (`test_graph_split_oversize_fallback_names_resolve`) fails on the pristine tree too — pre-existing, unrelated.

## Local TODOs

- [x] Strict full-match in `_parse_task_file` estimate branch
- [x] Regression test: malformed books None, valid still parses
- [x] Full suite green except pre-existing graph failure (proven unrelated)
- [x] CHANGELOG entry
- [x] Run lint + stage

## Acceptance Criteria

- [x] `**Estimate:** 1h 30m` yields `estimate_hours=None`, never a truncated number
- [x] `**Estimate:** 2.5h` still yields 2.5
- [x] No other parser behavior changed (case handling now mirrors the lint contract exactly)

## Verification Evidence

- **Test command:** `rtk test uvx --with 'mcp<2' --with pathspec --with pyyaml pytest tests/ -q`
- **Expected result:** full suite green except pre-existing graph failure
- **Actual result:** `753 passed, 1 failed` (`test_graph_split_oversize_fallback_names_resolve` fails identically with changes stashed); planner file `123 passed`; new `test_parse_task_file_estimate_strict` green
- **Exit code:** 0 (planner file) / 1 (suite, pre-existing failure only)

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** legacy files with lenient values (`3 hours`, `2H`) now read as no-estimate; honest (previous number was a guess) and lint would have failed them at stage time anyway.
- **Rollback:** restore the prefix-match line; delete the test.

---

## Execution Log & Reasoning

**Seat Check.** Domains: planner estimate parsing (single regex branch) + one regression test. No whole-word trigger hit on UI/arch/perf sets — explicit miss; single-seat Senior Programmer by implementation duty. Skipped: Architect (no contract change — behavior now matches the documented lint contract), Designer (no surface), QA/Reviewer (post-stage). Brainstorm: not required — two-line change, reversible.

**Planning gate.** Manager's order is the plan ("yes" to strict-reject after the grounded options). No separate Brain round.

**Implementation.** `server.py:243`: `re.match(r"(\d+(?:\.\d+)?)\s*h", val, re.IGNORECASE)` → `re.match(r"^(\d+(?:\.\d+)?)h$", val)`. Test writes a valid task, rewrites the header to `1h 30m` in place, asserts None. Incidental: repaired a merged def line my own edit produced (line 182), verified clean.

**Assumption A1.** None beyond the lint contract as spec: `^\d+(?:\.\d+)?h$`, lowercase h, no spaces — identical regex now enforced at both layers.

**QA cycle (Brain):** `QA_PASSED`. F1: no second lenient reader (`schedule_tasks` loud-rejects, lint fails the shape at stage time, so the parser was the only silent path). F2: legacy `3 hours`/`2H` now read None — intentional honesty over a guessed number; closed files never affect capacity. F3: merged-def repair clean (`server.py:182` no residual hunk, planner 123 green proves import integrity). F4: case narrowing mirrors the lint contract. Test judged real: old prefix code returns 1.0 and fails the second assert.

**Review (Brain):** `APPROVED` → `PO_REVIEW_PENDING`, severity Low. Parity verified (`^(?:\d+(?:\.\d+)?)h$` vs lint's non-capturing form), Manager option fidelity confirmed (strict reject, not Xh-Ym parsing), test real, merged-def trace absent, CHANGELOG accurate. One non-blocking note R1: the `^` anchor is redundant under `re.match`; drop it or use `fullmatch` on the next touch.

**Closure approval (Manager, 2026-10-28):** "Approved for closure" via the question tool. Commit path is `custom_context_commit_and_clean_task` only.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `3bfdbfccc56e42149a9dcfd4de586d35d681df85`
<!-- END_GIT_DIFF -->
