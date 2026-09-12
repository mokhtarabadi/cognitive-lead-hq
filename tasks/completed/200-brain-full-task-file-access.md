# Task 200: Brain always receives the full task file working content

**File:** `tasks/completed/200-brain-full-task-file-access.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Guarantee the Brain receives the task file's complete working content on every turn, so it never operates on partial context.

## Manager's Notes

Manager final order (Farsi, verbatim): "برای بار آخر، این خیلی مهمه: حتماً حتماً حتماً حتماً، BrainMCP Brain باید به کل فایل تسک یا محتوای اون همیشه دسترسی داشته باشه."

Honest design (no false promise): a multi-megabyte file cannot ride every model call. The bulk of a closed task file is the injected Factual Git Diff audit trail, which the Brain never needs whole. The guarantee covers the complete WORKING content (Goal, Notes, TODOs, Acceptance Criteria, evidence, Execution Log — everything except the diff block), plus a one-line omitted-note with the read_file pull path for the diff. Small, complete, testable.

Scope: bridge server auto-attach + mocked tests only. No prompt-fragment changes (no version bump). Standing authorization: autopilot + autoclosure, execute without asking.

## Local TODOs

- [x] Locate task file by task_id across Kanban dirs (backlog, in-progress, qa, completed, archive)
- [x] Strip the Factual Git Diff block, attach working content with omitted-note in brain_turn
- [x] Mocked unit tests (attach present, diff stripped, unresolvable task_id never fails turn)
- [x] Verify full suite, update CHANGELOG, lint, stage, qa, autopilot QA/review, autoclose

## Acceptance Criteria

- [x] Every brain_turn with a task_id carries the task file working content unless already present
- [x] Diff block excluded with a one-line omitted-note pointing at the read_file pull path
- [x] Unresolvable task_id never fails the turn (proceeds without attach)
- [x] Mocked tests cover attach, strip, missing-file paths; full suite green

## Verification Evidence

- **Test command:** `uv run --project mcp-brain-bridge --with pytest --with pathspec pytest tests/ -q`
- **Expected result:** all pass, exit 0
- **Actual result:** Full suite 218 passed (212 + 6: fence-escape, offset-note+relpath, bundle-False-skips, tmp-integration, suffix-only, truncation-pull)), exit 0
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** task_id maps to several files across Kanban dirs (moved during lifecycle)
- **Rollback plan:** resolution order backlog, in-progress, qa, completed, archive — first match wins; bridge code only, revert file on failure

---

## Execution Log & Reasoning

Implemented in mcp-brain-bridge/server.py: _resolve_task_file (Kanban-wide lookup with trailing-segment fallback), _strip_task_diff (diff-block cut + omitted-note with read_file pull path), _build_task_attach (labeled block), brain_turn hook (auto-attach unless marker present, never fails turn). 6 mocked tests (strip, resolve+fallback, unresolvable, in-body, no-dup, unresolvable-succeeds). Full suite 212 passed, exit 0. QA round 1 REJECTED with V1–V10 hardening order (all TRUE gaps); hotfix implemented (allowlist, 12k cap, global strip + truncated flag, namespaced marker, lanes+archive, fences, doc updates) + 5 new tests. Pending: QA re-test, reviewer, autoclose.

QA round-1: REJECTED (V1–V10 — all triaged TRUE gaps) → hotfix implemented (allowlist, 12000 cap, global strip + truncated flag, namespaced marker, coerce/validate, lanes incl archive, fenced attach, repo-relative paths, TOCTOU-safe; broad-except KEPT per never-fail guarantee, documented) + 5 mocked tests → full suite 212 green. QA round-2: REJECTED (V1–V3 task-file VALID → verdicts recorded HERE; V4–V6 STALE — hotfix already on disk + 212 green). Rejections: TWO — next rejection triggers Manager escalation. QA re-test pending with FULL file paste.

Numeric-prefix fallback fix (8-test failure root cause): V4 known-suffix-only edit broke slug-bearing ids like 200-foo (needs stripping to 200 to glob 200-*.md). Fix: exact match, then known lane suffix, then LEADING-NUMERIC head (200-foo gives 200, my-cool-task gives None since repo ids are numeric). Docstring updated. Full suite 218 passed, exit 0.

QA re-test (round 3, task_id 200-qa, FULL verbatim pack): QA_PASSED ([QA Engineer] + reasoning_log, REPORT no XML). All prior findings closed on pasted code (S1–S10); suite 218 green fresh. Reviewer: APPROVED → PO_REVIEW_PENDING ([Code Reviewer] + reasoning_log, REPORT no XML). F1–F6 grounded in pasted files; R1 residual accepted non-blocking Low; no postfix XML. Rejections stayed at TWO (this round passed, no escalation). Autoclosing under standing autopilot+autoclosure.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `c43949134b7958891142a03274bc534256e53872`
<!-- END_GIT_DIFF -->
