# Task 89: Fix Template Lint Contract and Add Absent-File Policy

**File:** `tasks/completed/89-fix-template-lint-and-absent-file-policy.md`
**Source:** manager
**Type:** bug
**Status:** closed

## Source Context

### Variant C: Manager (`**Source:** manager`)

## Goal

Fix two audit findings from Task 87 (F1 + F2): (1) move the lint-required sections (`## Local TODOs`, `## Acceptance Criteria`, `## Verification Evidence`, `## Risk & Rollback`) OUT of the source-variant switch in the `task-generator` skill template so they are unconditional for ALL source variants, and (2) add the Absent-File Policy (SKIP gracefully — DO NOT HALT, DO NOT HALLUCINATE) to `AGENTS.md` and all 3 `<validation_phase>` blocks in `system-prompt.md`, then bump system version to 8.4.1 and update CHANGELOG.

## Manager's Notes

- Implements findings F1 and F2 documented in `tasks/backlog/87-workflow-audit-findings.md`.
- F2: template variants A (orchestrator) and B (telegram) omitted 4 lint-required sections → every such task failed `lint_task_file` at creation.
- F1: `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md` are referenced as mandatory but do not exist (verified by glob) → the executor's "MUST read" instruction was unsatisfiable; agents could HALT or hallucinate compliance.
- Version bump: PATCH (8.4.0 → 8.4.1) per `versioning-and-release` skill (bug fixes / doc sync).
- Global deployment of `task-generator` lives at `~/.config/opencode/skills/task-generator/SKILL.md` — must be re-synced after editing `skill-templates/`.

## Local TODOs

- [x] Step 1: Create this task file in `tasks/backlog/` with ID from the official discovery script (expected 89), then move to `tasks/in-progress/` via `git mv`
- [x] Step 2: Read target files (task-generator template, AGENTS.md, system-prompt.md, CHANGELOG head) and map exact edit points
- [x] Step 3: Fix F2 — move the 4 lint-required sections outside the variant switch in `skill-templates/task-generator/SKILL.md` + add the "unconditional" comment marker
- [x] Step 4: Sync global deployment copy (`~/.config/opencode/skills/task-generator/SKILL.md`) with the updated template
- [x] Step 5: Fix F1 — add Absent-File Policy to `AGENTS.md` after the Mandatory First-Read Rule
- [x] Step 6: Fix F1 — add the skip instruction to all 3 `<validation_phase>` blocks in `system-prompt.md`
- [x] Step 7: Bump `<system_version>` 8.4.0 → 8.4.1 in `system-prompt.md`
- [x] Step 8: Update `CHANGELOG.md` — add `## [8.4.1]` header with `### Fixed` entries (Parse-Then-Append, no duplicates)
- [x] Step 9: Save project memory (`project/absent-file-policy`)
- [x] Step 10: Syntax verification (XML tags balanced, Markdown structure intact, formatting consistent)

## Acceptance Criteria

- [x] `skill-templates/task-generator/SKILL.md` contains all 4 lint-required sections ONCE, positioned after the variant switch, with the `<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->` comment
- [x] Global copy `~/.config/opencode/skills/task-generator/SKILL.md` is byte-identical to the template
- [x] `AGENTS.md` contains the Absent-File Policy (SKIP gracefully — DO NOT HALT, DO NOT HALLUCINATE)
- [x] `system-prompt.md` contains the skip instruction in ALL 3 `<validation_phase>` blocks
- [x] `<system_version>` in `system-prompt.md` is 8.4.1
- [x] `CHANGELOG.md` has a single `## [8.4.1]` header with the 2 `### Fixed` entries, no duplicates
- [x] Memory `project/absent-file-policy` stored
- [x] Task file passes `lint_task_file`

## Verification Evidence

- **Test command:** `lint_task_file tasks/in-progress/89-fix-template-lint-and-absent-file-policy.md` ; `grep -n "## Local TODOs\|## Acceptance Criteria\|## Verification Evidence\|## Risk & Rollback" skill-templates/task-generator/SKILL.md` ; `grep -n "Absent-File Policy\|SKIP gracefully" AGENTS.md system-prompt.md` ; `grep -n "8.4.1" system-prompt.md` ; `diff skill-templates/task-generator/SKILL.md ~/.config/opencode/skills/task-generator/SKILL.md`
- **Expected result:** lint ✅; 4 section matches OUTSIDE the variant switch; Absent-File Policy in AGENTS.md (1) + SKIP instruction in system-prompt.md (3); `8.4.1` exactly once in `<system_version>`; template ↔ global diff clean
- **Actual result:** `lint_task_file` → ✅ passed; 4 section headers in the unified template at lines 99/105/110/117 (once each, after Variant C's Manager's Notes, guarded by the comment marker at line 97); AGENTS.md 1 match (line 13, "Absent-File Policy") + system-prompt.md 3 matches (lines 373/414/489, "SKIP gracefully"); `8.4.1` exactly once (line 1, `<system_version>`); `diff` → IDENTICAL (global copy synced); CHANGELOG: exactly 1 `## [8.4.1]` header with exactly 2 `### Fixed` entries; XML balance verified: `<validation_phase>` 3/3, all 3 task templates 1/1, `<system_version>` 1/1 (line 443 `<constraints>` is an intentional textual reference)
- **Exit code:** 0 (all grep/diff checks); 0 (lint — passed)

## Risk & Rollback

- **Risk:** (1) Moving the 4 sections could break the polymorphic template shape if placed inside a variant by mistake — mitigated by the comment marker and grep verification. (2) CHANGELOG duplicate `### Fixed` under 8.4.1 — mitigated by Parse-Then-Append. (3) Global/`skill-templates/` drift — mitigated by diff check.
- **Rollback plan:** Revert the 4 sections into the variant switch (restore from git history), remove the Absent-File Policy lines, revert `<system_version>` to 8.4.0, and remove the 8.4.1 CHANGELOG block; re-sync the global task-generator copy.

---

## OpenCode Execution Log & Reasoning

### What was done

1. **Task 89 created** in `tasks/backlog/` (ID discovery: 89, collision-checked), then moved to `tasks/in-progress/` via filesystem `mv` (file was untracked — `git mv` correctly rejected it, per executor protocol "filesystem mv if untracked").
2. **F2 fix — `skill-templates/task-generator/SKILL.md`:** The 4 lint-required sections now sit AFTER the polymorphic variant switch (Variant C's `Manager's Notes`), guarded by the marker comment `<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->` (line 97). Variants now contain ONLY source-specific context: A = Source Context/Goal/Blueprint Reference/Manager's Notes; B = Goal/Original Message/English Translation/Refactored Prompt/Relevant Code Context/AI Analysis & Opinion; C = Source Context/Goal/Manager's Notes. The intro instruction (line 35) now declares the 5 mandatory+unconditional sections explicitly. The multi-phase template was already compliant (it carries its own copies of the sections).
3. **Global sync:** `cp skill-templates/task-generator/SKILL.md ~/.config/opencode/skills/task-generator/SKILL.md` → `diff` confirms byte-identical.
4. **F1 fix — `AGENTS.md`:** Absent-File Policy blockquote added after the Mandatory First-Read Rule's file list (line 13).
5. **F1 fix — `system-prompt.md`:** All 3 `<validation_phase>` blocks (lines 373/414/489 — discovery, implementation, combined templates) gained: "If any of these files do NOT exist, SKIP gracefully with an explicit note. DO NOT HALT. DO NOT HALLUCINATE their contents. Proceed to the next step."
6. **Version bump:** `<system_version>` 8.4.0 → 8.4.1 (PATCH — bug fixes per `versioning-and-release`).
7. **`CHANGELOG.md`:** `## [8.4.1] - 2026-08-10` added below `[Unreleased]` with exactly 2 `### Fixed` entries (Parse-Then-Append; verified no duplicates — grep count = 1 header, 2 entries).
8. **Memory:** `project/absent-file-policy` stored via `project_memory_store_memory`.

### Architectural reasoning

- **Placement decision for F2:** The 4 sections were left physically where Variant C ended (immediately after `Manager's Notes`) rather than duplicated per variant — this keeps the template DRY: one copy, always emitted, regardless of which variant block is selected. The marker comment is the anti-regression guard (an LLM "compacting" the template later will see why the block must stay outside the variants). This directly implements the F2 suggested fix from Task 87 and matches the lint contract (`_check_task_file_structure.required_sections`).
- **Placement decision for F1:** The policy lives in ONE place in AGENTS.md (First-Read Rule) and is mirrored verbatim in all 3 XML validation phases — the same phrase "SKIP gracefully" makes the bash-phase grep deterministic (1 + 3 matches) and keeps the executor's HALT protocol well-defined: missing files are never a halt condition, only a note.
- **Why PATCH:** Both changes are defect fixes to existing workflow artifacts (template/lint mismatch + unsatisfiable first-read mandate) — no new capability, so 8.4.1 per SemVer.
- **Cross-session note (Task 87 F5):** The staged tree at closure time must be reviewed by the Code Reviewer — this task touched `skill-templates/`, `AGENTS.md`, `system-prompt.md`, `CHANGELOG.md`, plus the global `~/.config/opencode/skills/` copy (outside the repo, not staged).

### Lint & verification

- `lint_task_file tasks/in-progress/89-fix-template-lint-and-absent-file-policy.md` → ✅ passed (twice: before and after the final doc updates).
- All bash-phase greps returned expected results (see Verification Evidence). No repair attempts needed.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `c21e45715a682a5d5ea890bdabf1f5349884c980`
<!-- END_GIT_DIFF -->