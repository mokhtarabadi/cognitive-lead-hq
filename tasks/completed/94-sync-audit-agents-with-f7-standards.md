# Task 94: Sync Audit-Agents with F7 Standards

**File:** `tasks/in-progress/94-sync-audit-agents-with-f7-standards.md`
**Source:** manager
**Type:** chore
**Status:** open

## Source Context

### Variant C: Manager (`**Source:** manager`)

## Goal

Sync `skill-templates/audit-agents/SKILL.md` with the F7 standards introduced in Task 93: (1) Mode 1's AGENTS.md template gains the autonomous `git mv` Kanban exception in the Git Guardrail and the mandatory `tasks/qa/` transition in the End-Of-Task Sequence; (2) the Target Audit Criteria (top summary + Mode 2 lists) gain the matching `git mv` exception and the QA transition wording; (3) re-sync the global deployment copy; (4) CHANGELOG entry.

## Manager's Notes

- Consistency decision: the ZAC and End-Of-Task criteria bullets have IDENTICAL text in both the top Target Audit Criteria summary (lines ~17-18) and the Mode 2 list (lines ~326-327) — both are updated via replaceAll so the skill never carries a stale fast-scan summary (same pattern as the Task 90 F5 criterion update).
- The new 4-step completion process mirrors the live executor protocol (Task 93 F7d): stage_and_inject_diff → git mv to tasks/qa/ → notify Manager.
- Global copy: `~/.config/opencode/skills/audit-agents/SKILL.md` re-synced (LLM.txt Step 6 pattern).

## Local TODOs

- [x] Step 1: Create this task file (ID discovery → 94), move to `tasks/in-progress/`
- [x] Step 2: Read target file (audit-agents SKILL.md anchors) + CHANGELOG head
- [x] Step 3: Mode 1 — append `git mv` exception to Git Guardrail; update End-Of-Task Sequence step 3 with the `tasks/qa/` transition
- [x] Step 4: Mode 2 + top summary — append `git mv` exception to ZAC criteria; update End-Of-Task criteria with `tasks/qa/` wording (replaceAll, both lists)
- [x] Step 5: Sync global deployment copy
- [x] Step 6: Update `CHANGELOG.md` — `[Unreleased]` → `### Changed`: audit-agents F7 sync bullet
- [x] Step 7: Syntax verification (greps + lint)

## Acceptance Criteria

- [x] `Exception.*git mv` appears exactly 2× in the skill (Mode 1 template + criteria) — actual: 3× (Mode 1 guardrail line 253 + criteria in BOTH the top summary line 17 and Mode 2 line 327; deliberate consistency extension, documented)
- [x] `tasks/qa/` appears exactly 2× in the skill (Mode 1 sequence + criteria) — actual: 4× (line 18 top criteria + line 328 Mode 2 criteria + line 301 Mode 1 sequence + line 282 pre-existing Core File Locations; consistent extension documented)
- [x] Global copy byte-identical to template
- [x] `CHANGELOG.md` `[Unreleased]` → `### Changed` has the bullet, no duplicates
- [x] Task file passes `lint_task_file`

## Verification Evidence

- **Test command:** `grep -n "Exception.*git mv" skill-templates/audit-agents/SKILL.md` ; `grep -n "tasks/qa/" skill-templates/audit-agents/SKILL.md` ; `diff skill-templates/audit-agents/SKILL.md ~/.config/opencode/skills/audit-agents/SKILL.md` ; `lint_task_file tasks/in-progress/94-sync-audit-agents-with-f7-standards.md`
- **Expected result:** 2 matches each; diff empty (identical); lint ✅
- **Actual result:** `Exception.*git mv` → 3 matches (lines 17, 253, 327); `tasks/qa/` → 4 matches (lines 18, 282, 301, 328); `diff` → IDENTICAL (global synced); CHANGELOG `### Changed` gained 1 bullet (no duplicates); lint → ✅ passed (run below)
- **Exit code:** 0 (all checks); 0 (lint)

## Risk & Rollback

- **Risk:** (1) replaceAll could hit unexpected duplicate anchors — verified anchors are exactly the paired criteria lines. (2) Global copy drift — diff check. (3) CHANGELOG duplicates — Parse-Then-Append.
- **Rollback plan:** revert the 4 skill edits + CHANGELOG bullet; re-sync global copy from template.

---

## OpenCode Execution Log & Reasoning

### What was done

1. **Mode 1 — AGENTS.md template Git Guardrail (line ~251):** appended `-> **Exception:** \`git mv\` is permitted autonomously for moving task files between Kanban directories.` — mirroring the AGENTS.md repo guardrail from Task 93 F7c.
2. **Mode 1 — End-Of-Task Sequence step 3 (line ~300):** replaced with "Call MCP Tool & QA Transition": `stage_and_inject_diff` → mandatory `git mv` to `tasks/qa/` → notify Manager; NO git commit — mirroring the live executor protocol from Task 93 F7d.
3. **Criteria lists (top summary + Mode 2, lines ~17/326 and ~18/327):** the ZAC bullet gained the `git mv` Kanban exception and the End-Of-Task bullet's step 3 now reads "then `git mv` the task to `tasks/qa/`" — applied via replaceAll so both identical bullets stayed in sync (same pattern as Task 90's F5 criterion).
4. **Global deployment:** `cp` to `~/.config/opencode/skills/audit-agents/SKILL.md` — diff confirms byte-identical.
5. **`CHANGELOG.md`:** bullet appended under `[Unreleased]` → `### Changed` (Parse-Then-Append; no duplicates).

### Architectural reasoning

- **Grep-count deviation (documented):** the Orchestrator expected 2 matches for `Exception.*git mv` and `tasks/qa/`; actual results are 3 and 4. The extra matches come from (a) the deliberate consistency extension to the top Target Audit Criteria summary (lines 17-18) — which was already in sync with Mode 2 for the F5 criterion and would otherwise drift again — and (b) a pre-existing `tasks/qa/` mention in the Core File Locations line (282). The REQUIRED targets (Mode 1 template + Mode 2 criteria) are all updated; the counts are supersets, not missing coverage.
- **Skill-ecosystem consistency:** with this task, `audit-agents`, `AGENTS.md`, `agents/cognitive-executor.md`, and `system-prompt.md` all enforce the SAME git-mv-exception + qa-transition semantics — the F7 standards are now propagated through the entire governance layer (AGENTS.md → executor agent → audit skill), closing the "rules in one place only" drift pattern that F7 documented.

### Verification

- greps, diff, and lint results in Verification Evidence. No repair attempts needed.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->