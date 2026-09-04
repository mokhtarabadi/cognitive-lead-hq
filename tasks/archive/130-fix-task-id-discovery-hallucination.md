# Task 130: Fix Task ID Discovery Hallucination

**File:** `tasks/completed/130-fix-task-id-discovery-hallucination.md`
**Source:** orchestrator
**Type:** bug
**Status:** closed

## Source Context

### Variant A: Orchestrator (`**Source:** orchestrator`)

## Goal

Remove the truncated/ambiguous inline task-ID discovery command from `<execution_workflow>` Step 1.5 and replace it with a mandate to load the `task-generator` skill as the single source of truth, eliminating the Hands' occasional hallucination of a year-based task number instead of the correct next sequential ID.

## Blueprint Reference

`prompts/fragments/11-execution_workflow.md` Step 1.5 (Task Number Pre-Assignment Validation); `prompts/fragments/01-system_version.md`; `prompts/fragments/13-constraints.md`; `AGENTS.md`.

## Manager's Notes

- The truncated inline command currently contains a literal `...` placeholder (`find tasks/ -type f -name '*.md' ...`) which is ambiguous and causes hallucination.
- Preserve the existing "STRICTLY FORBIDDEN from guessing" sentence unchanged.
- This is a PATCH-level clarification (removes ambiguity, no new capability): `9.2.0` → `9.2.1`.

## Local TODOs

- [x] Initial codebase exploration
- [x] Replace truncated inline command in fragment 11 Step 1.5 with skill-loading mandate
- [x] Search AGENTS.md + fragment 13 for other truncated/duplicate occurrences
- [x] Bump `<system_version>` to 9.2.1 and regenerate system-prompt.md
- [x] Update CHANGELOG.md
- [x] Verify functionality

## Acceptance Criteria

- [x] `prompts/fragments/11-execution_workflow.md` Step 1.5 contains NO inline command text and instead mandates loading the `task-generator` skill and executing its documented next-ID discovery method exactly as written there; the "STRICTLY FORBIDDEN from guessing" sentence is preserved unchanged.
- [x] `grep -n "find tasks/" system-prompt.md prompts/fragments/11-execution_workflow.md` returns NO matches (truncated command gone).
- [x] `grep -n "task-generator" prompts/fragments/11-execution_workflow.md` returns a match (skill-load mandate present).
- [x] `<system_version>` bumped to 9.2.1 in both `prompts/fragments/01-system_version.md` and regenerated `system-prompt.md`; `CHANGELOG.md` updated under `### Fixed`.
- [x] `git diff --stat -- 'loop-engine/' '*.py'` is empty (zero out-of-scope changes).

## Verification Evidence

- **Test command:** `npx prettier --write "prompts/fragments/11-execution_workflow.md" "prompts/fragments/01-system_version.md" "AGENTS.md" "CHANGELOG.md"` then `python3 scripts/prompt-build/assemble_system_prompt.py` then `grep -n "find tasks/" system-prompt.md prompts/fragments/11-execution_workflow.md` and `grep -n "task-generator" prompts/fragments/11-execution_workflow.md` and `git diff --stat -- 'loop-engine/' '*.py'`
- **Expected result:** Prettier formats files; assembler regenerates system-prompt.md; `find tasks/` grep returns NO matches; `task-generator` grep returns a match; out-of-scope diff empty.
- **Actual result:** Prettier formatted all listed files (3 unchanged); assembler regenerated `system-prompt.md` (75364 bytes, exit 0); `grep -n "find tasks/" system-prompt.md prompts/fragments/11-execution_workflow.md` → **no matches** (exit 1, correct); `grep -n "task-generator" prompts/fragments/11-execution_workflow.md` → match at line 8 (skill-load mandate present); `grep -n "<system_version>"` → both files show `9.2.1`; `git diff --stat -- 'loop-engine/' '*.py'` → empty (zero out-of-scope changes).
- **Exit code:** 0 (all commands; grep 4 exit 1 = expected no-match)

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Manager Decisions

**[2026-08-30] [D1] [ORCHESTRATOR-DETECTED]:** Adopted Option B — mandate loading the `task-generator` skill as the single source of truth for task-ID discovery, removing the inline command from `<execution_workflow>` Step 1.5 entirely.
- **Rationale:** Single source of truth vs. duplicated/drifting logic. The truncated inline command (`find tasks/ -type f -name '*.md' ...`) was ambiguous and caused the Hands to occasionally hallucinate a year-based task number instead of the correct next sequential ID. Duplicating the full command in the system prompt would create two copies that can drift apart.
- **Alternatives considered:** Option A — inlining the exact full script directly in the system prompt (rejected: creates a second copy of the canonical command that must be manually kept in sync with the skill; any future algorithm change would need edits in two places).
- **Impact:** Any future change to the ID-discovery algorithm now only needs to happen in one place (`skill-templates/task-generator/SKILL.md`); the system prompt references the skill by name, so it never drifts. `<system_version>` bumped 9.2.0 → 9.2.1 (PATCH).

## Risk & Rollback

- **Risk:** Removing the inline command could leave the Hands without a concrete command if the skill-loading mandate is not followed; scope creep into unrelated prompt sections.
- **Rollback plan:** Revert the fragment and system-prompt edits via the injected Git diff; restore `<system_version>` 9.2.0; the task file diff is the single rollback reference.

---

## Execution Log & Reasoning

**Review-remediation + closure pass (2026-08-30):** This pass applied reviewer findings F1 and F2 to the already-approved implementation — no new implementation work.

- **F1 (checkbox confirmation):** Checked all 5 `## Acceptance Criteria` boxes and all 4 `## Definition of Done` boxes to `- [x]` — `## Verification Evidence` already confirmed each is satisfied. Checkbox count after: 15 (6 Local TODOs + 5 AC + 4 DoD).
- **F2 (closing-tag indentation):** Fixed `</execution_workflow>` from 5-space indent to column 0 in `prompts/fragments/11-execution_workflow.md` (line 44) and regenerated `system-prompt.md` (75359 bytes, exit 0) so the same fix propagated to the artifact (line 444).
  - **Before:** `grep -n "     </execution_workflow>" prompts/fragments/11-execution_workflow.md system-prompt.md` → matched both (fragment 11:44, system-prompt.md:444).
  - **After:** same grep → no matches (exit 1); `grep -n "^</execution_workflow>$"` → matches in both files at column 0.
- **Closure:** `**Status:** open` → `closed`; `**File:**` header updated to `tasks/completed/`; moved via `git mv tasks/qa/ → tasks/completed/`. Out-of-scope check `git diff --stat -- 'loop-engine/' '*.py'` → empty.

No new CHANGELOG entry (Task 130's `## [9.2.1]` entry already describes the substance; F1/F2 were review-quality fixes to the same diff). No new Manager Decision entry (F1/F2 are mechanical corrections to already-logged decisions).

**Task Number Pre-Assignment Validation (dogfooding):** Ran the task-generator skill's documented ID-discovery command verbatim → `NEXT_ID = 130` (highest existing = 129 in `tasks/completed/`; `tasks/backlog/` empty → no collision). Created the task file at `tasks/backlog/130-fix-task-id-discovery-hallucination.md`, then moved to `tasks/in-progress/` via filesystem `mv` (untracked file — `git mv` refused, per Kanban reality check memory).

**task-generator skill ID-discovery mechanism (quoted verbatim from the skill):**

```bash
NEXT_ID=$(find tasks/ -type f -name "*.md" -exec basename {} \; | grep -Eo '^[0-9]+' | sort -n | tail -1 | awk '{print $1+1}')
if [ -z "$NEXT_ID" ] || [ "$NEXT_ID" -eq 0 ] 2>/dev/null; then NEXT_ID="01"; fi
printf "%02d\n" $NEXT_ID
```

**telegram-issue-sync comparison finding:** `telegram-issue-sync` uses the **SAME** ID-discovery command verbatim (Phase 3 Step 1, lines 121–123 of `skill-templates/telegram-issue-sync/SKILL.md`) and additionally carries a **TASK-GENERATOR MIRROR MANDATE** (line 95): "Task creation MUST mirror `task-generator` exactly: same ID discovery command, same duplicate-title check, same duplicate-ID check, same collision check, same canonical template, and same `## Definition of Done` block. Do NOT maintain divergent logic — if the `task-generator` skill's workflow changes, mirror those changes here." **No divergence found** — the two skills share one canonical mechanism with an explicit mirror mandate. No follow-up flag needed.

**Step 2 search result (AGENTS.md + fragment 13):** No other truncated/ellipsis task-ID command or duplicate guardrail found. `AGENTS.md`'s only `find tasks` references (lines 91, 93) are the complete bundle-script NEXT_ID discovery in the META-TASK BUNDLE LIFECYCLE section — not truncated, not ambiguous, describing `scripts/bundle-tasks.py` behavior. `prompts/fragments/13-constraints.md` has no task-ID command; its `...` matches are unrelated template placeholders (brainstorming response tags, docker command). Explicitly recorded — the check was performed, not silently skipped.

**Files edited:**
1. `prompts/fragments/11-execution_workflow.md` — Step 1.5: replaced the truncated inline command (`find tasks/ -type f -name '*.md' ...`) with the skill-loading mandate ("load the `task-generator` skill and execute its documented next-ID discovery method exactly as written there — no command is duplicated here to prevent drift"). Preserved the "STRICTLY FORBIDDEN from guessing" sentence unchanged.
2. `prompts/fragments/01-system_version.md` — bumped `<system_version>` 9.2.0 → 9.2.1 (PATCH: removes ambiguity, no new capability).
3. `system-prompt.md` — regenerated via `python3 scripts/prompt-build/assemble_system_prompt.py` (75364 bytes, exit 0); verified `find tasks/` has zero matches and `task-generator` mandate present at line 8.
4. `CHANGELOG.md` — added Task 130 entry under `## [9.2.1]` → `### Fixed` (Parse-Then-Append).

**Anchor points:** fragment 11 line 8 (Step 1.5 bullet); fragment 01 line 1 (version string).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `a62b695be3f83b7a5adaf6ee1b5dd62197abcd8a`
<!-- END_GIT_DIFF -->