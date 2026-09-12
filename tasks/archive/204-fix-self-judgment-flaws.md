# Task 204: Fix Self-Judgment Flaws (Persona Overlap, Positive Directives, ZAC Lock Design)

**File:** `tasks/completed/204-fix-self-judgment-flaws.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Fix the actionable flaws found in the self-judgment run: overlapping persona seats, negative-constraint style, and a mechanical ZAC lock design.

## Manager's Notes

Follow-up of the self-judgment task. Manager order (translated): run the flaws task after the judgment task, then write the manager decisions. Self-found flaws live in the side note; W1 already fixed in the parent task. Autopilot locked for this task.

## Local TODOs

- [x] W3: audit persona seats for overlap, merge or clarify
- [x] W4: rewrite key negative constraints as positive directives
- [x] W2: draft mechanical ZAC lock design for Manager approval (cannot enforce alone)
- [x] Verify functionality (suite green, lints clean)

## Acceptance Criteria

- [x] Persona overlap reduced or explicitly justified per seat
- [x] Top negative constraints converted without losing prohibitions
- [x] ZAC lock proposal written for Manager decision (no unilateral enforcement change)
- [x] Suite 264+ green, task lint clean, CHANGELOG updated

## Verification Evidence

- **Test command:** `uv run --with "pytest" --with "pathspec" --with "pyyaml" --with "mcp==1.30.0" python -m pytest tests/ -q`
- **Expected result:** all pass, exit 0
- **Actual result:** 264 passed, 8 warnings
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** prompt-fragment edits change Brain behavior globally; persona merges lose coverage
- **Rollback plan:** `git diff` review per hunk; fragments rebuild from source; revert single commit

---

## Execution Log & Reasoning

Planning Gate: Manager's explicit order (flaws task after judgment task) is the approved plan — Manager-direct path, executed on locked autopilot.

W3 (persona overlap), fixed in `prompts/fragments/06-personas.md`:
- Planner vs Strategist: added ownership boundaries (Planner owns file state + milestones, never priority; Strategist owns priority + scope, never file moves).
- Architect vs Programmer: added WHAT-vs-HOW boundary on both sides (Architect: design + skill list; Programmer: task XML + orchestration).
- QA vs Reviewer: already separated (QA hunts bugs, never format/architecture; Reviewer audits blueprint/conventions) — justified, no edit.
- Ferry staleness (real contradiction with no-ferry rule): QA + Reviewer behaviors said the Manager ferries by hand unconditionally — rewrote mode-aware (manual ferry vs autopilot direct call).

W4 (positive-directive noise), same file: Architect Discovery-First triple coverage (forbidden + MUST + do-not) trimmed to prohibition + single directive. Bounded: no meaning change, MUST count reduced where a prohibition already covers the ground.

W2 (ZAC mechanical lock) — PROPOSAL ONLY, needs Manager approval:
- Finding: history records permission-layer denies for git add/commit/push, but both repo and global `opencode.json` carry MCP-tool allows only — no bash deny entries exist now. ZAC is prompt-words-only.
- Proposal: restore command deny entries for the commit path in global config, then dry-verify (read-only git commands still work, commit path prompts/denies). I did NOT touch global config — enforcement semantics are a Manager decision.
 - Prompt bumped to 9.29.0, prompt rebuilt, sync check passed.

 QA round (same task_id, verbatim changed lines pasted, truncation 0): QA_PASSED with machine block (VERDICT + 6 CITE lines to 06-personas.md:5/18/24/41/50/56). Findings F1-F6 confirm ownership splits + mode-aware ferry; W2 excluded by design; no extra tests needed for wording change.
 Reviewer round (same evidence): PO_REVIEW_PENDING — technically approved, S1-S6 strengths, no defects, W4 trim + W2 proposal-only confirmed. No autoclosure per standing rule — Manager closes.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `4e7e2d63bf5451ec5ab652c16e724ee670cc9897`
<!-- END_GIT_DIFF -->
