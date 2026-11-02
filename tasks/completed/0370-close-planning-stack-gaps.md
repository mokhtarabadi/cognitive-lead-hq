# Task 0370: Close planning-stack gaps

**File:** `tasks/completed/0370-close-planning-stack-gaps.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Finished:** 2026-11-02T19:16:29Z
**Submitted:** 2026-11-02T18:51:17Z
**Started:** 2026-11-02T18:36:11Z

## Goal

Fix the planning-stack audit gaps in code, tools, and docs so behavior matches the documented contracts.

## Manager's Notes

Manager decisions (binding): sprint scope is the calendar week Monday to Sunday, stats filter by Started/Finished stamps; precedence is Strategist capacity veto stands unless the Manager explicitly overrides. Scope: F1 milestone writer, F2 case-insensitive grouping, F5 lock enforcement, F6 week-scoped stats plus date-aware quota, F7 docs refresh, F4 QA-cap reconciliation, F9 precedence rule in prompts, F10 DoD reconciliation. Converting the 369 xfail tripwires (T2, T5, T6) to must-pass guards is part of done. Prompt fragment edits require the regenerate workflow with version bump and pin update.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Brain planning turn for the fix design
- [x] Implement server plus lint plus docs changes
- [x] Convert 369 xfails to must-pass and keep suite green
- [x] Verify functionality

## Acceptance Criteria

- [x] `schedule_tasks` writes `**Milestone:**` and the 369 T1 guard still passes
- [x] Milestone grouping is case-insensitive and T2 passes without xfail
- [x] `claim_next` refuses work while a sprint lock file exists and T5 passes without xfail
- [x] `sprint_stats` filters by calendar week and quota reports today-aware numbers, T6 passes without xfail
- [x] Guide plus policies docs refreshed (correct citations, live Missing labels, milestone/sprint flow, reconciled caps and DoD)
- [x] Precedence rule written in prompts with rebuilt prompt in sync
- [x] Full suite green with zero xfail-strict leftovers from 369

## Verification Evidence

- **Test command:** rtk test uv run --with pytest --with "mcp<2" --with pathspec --with pyyaml pytest tests/ -q (RTK wrapper cannot spawn in this shell — os error 2; ran the documented raw fallback)
- **Expected result:** all green, 369 xfails converted, exit code 0
- **Actual result:** 766 passed, 0 failed; contracts file 11 passed with zero xfail leftovers; ruff format clean on all touched Python files
- **Exit code:** 0

> Verification runner rule: the exact command above is complete. The first run MUST use the `rtk test` prefix; a raw rerun is allowed only after a failed RTK run. RTK is known-broken in this shell (os error 2) — record the fallback if used.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Medium. Touching claim gates and grouping output can break existing planner tests and the board; run the full suite before claiming done.
- **Rollback plan:** Revert server plus docs commits via git; gaps return to the documented 369-tripwire state.

---

## Execution Log & Reasoning

Autopilot locked for QA plus review (Manager order "Lock auto pilot mode").

QA verdict (autopilot, same session): QA_PASSED with two residual notes V1 (malformed week handling) and V2 (milestone newline at writer level) — both verified and closed by the Hands before review (clean blocked string, no-write rejection with new T1c test, 160-test gate green, format clean).

Review verdict (autopilot, same session): technically approved, PO_REVIEW_PENDING — writer backwards compatible, grouping converges, lock fails closed, week scope with byte-identical snapshot lines, tripwires converted, prompt rebuilt in sync. R1/R2 confirmed by the Hands (CHANGELOG entry at line 47, staged names owned-only). Manager accept quote: "Close task" — closure authorized, executing final sequence once.

Supersedes the audit tripwire state: task 369 pinned behavior plus documented gaps; this task fixes F1, F2, F4-F7, F9, F10 under the Manager's week-scope and precedence decisions. Unlock path for sprint locks: deleting the lock file (Manager-owned). Quota design detail (today-finished counting) goes to the Brain plan.

Implementation notes: milestone as trailing optional `:milestone` segment (backwards compatible, `-` untouched; writer order Estimate, Deadline, Depends on, Milestone); grouping casefold with first-seen display; claim lock gate first with unlock-by-delete message plus docstring corrections; sprint_stats optional week param plus week lines (existing snapshot lines byte-identical) plus quota Finished-today line; lint Milestone non-empty single-line; 369 T2/T5/T6 converted with strengthened asserts plus new T1b writer test (11 passed, zero xfail); precedence sentence in 06-personas plus executor roster; PATCH 9.70.2 rebuilt (111362 bytes) with pin update; docs confined to flagged lines. Adaptations to the plan XML: task already in-progress (no backlog move); ruff format is the enforced gate (ruff check shows pre-existing repo-wide patterns only). Deviation logged: slice ADR appended via shell heredoc instead of the native write tool — content verified by readback plus markdown lint; will not repeat. Stack skip: plain Python plus pytest, no framework marker — no stack skill matched, none invented.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `07b1ddc24fb43f2bb96a65d376a2c6e528396439`
<!-- END_GIT_DIFF -->
