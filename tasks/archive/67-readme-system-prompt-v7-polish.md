# Task: README & system-prompt V7 Consistency Polish

**File:** `tasks/in-progress/67-readme-system-prompt-v7-polish.md`
**Type:** improvement
**Status:** closed

## Goal

Polish documentation for V7.1.1 consistency: fix README version drift (V6 → V7), add a `## Key V7 Changes` section, renumber the `<execution_workflow>` list in `system-prompt.md` from `0.`–`8.` to `1.`–`9.`, move the `</execution_workflow>` closing tag to its own line, and complete the README `skill-templates/` tree with all missing skill directories.

## Manager's Notes

- Self-corrected execution approved by Manager after ⚠️ RULE VIOLATION WARNING: the original Orchestrator task bundled a `system-prompt.md` edit without version bump / task file / CHANGELOG entry, and instructed a direct git commit outside the bash phase. Self-corrections: bump `<system_version>` to 7.1.1 (PATCH), create this task file, add CHANGELOG entry, no commit (stage via MCP tool).
- Renumbering is semantic-preserving: Discovery & Onboarding becomes step 1, explicitly labeled `(Phase 0)` to keep the `<initialization>` anchor; sub-steps re-parent (`0.5`→`1.5`, `1.5`→`2.5`, `1.7`→`2.7`); "Loop back to step 3" corrected to step 4.

## Local TODOs

- [x] Create task file (ID 67)
- [x] Polish 1: README `# V6 Multi-Agent System Prompt` → `# V7`, add `## Key V7 Changes` before `## Key V6 Changes`
- [x] Polish 2: renumber `<execution_workflow>` 1–9, fix sub-step parents, fix internal step reference, move tags to own lines
- [x] Polish 3: complete README `skill-templates/` tree (all 28 skills, grouped, alphabetical)
- [x] Verify: prettier check, grep gates
- [x] CHANGELOG `## [7.1.1]` entry
- [x] Move to in-progress, log, stage + inject diff

## OpenCode Execution Log & Reasoning

### Gatekeeper note (self-correction)

The original Orchestrator task was flagged with a ⚠️ RULE VIOLATION WARNING because Polish 2 edited `system-prompt.md` without the AGENTS.md-mandated version bump / task file / CHANGELOG entry, and ordered a direct git commit outside `<bash_phase>` (ZAC). The Manager approved a self-corrected execution: task file created (ID 67), `<system_version>` bumped to 7.1.1 (PATCH per SemVer), CHANGELOG entry added, no commit — staging via MCP tool only.

### Polish 1 — README V7 drift (README.md)

- Tree line `├── system-prompt.md ... # V6 Multi-Agent System Prompt` → `# V7 Multi-Agent System Prompt`.
- New `## Key V7 Changes` section inserted immediately before `## Key V6 Changes` (per literal instruction "before the V6 sections"), using the Orchestrator's provided bullet content verbatim (brainstorming protocol, universal datetime rules, SOLID mandate, leadership & language protocol, expanded skills registry).

### Polish 2 — `<execution_workflow>` renumber (system-prompt.md)

- The Orchestrator's spec ("renumber from 1. through 8.") was internally contradictory: the list had 9 numbered items (`0.`–`8.`), and item `0.` is the "Phase 0: Discovery & Onboarding" anchor referenced by `<initialization>`. Executed the semantically-safe scheme approved by the Manager:
  - `0.` → `1. **Discovery & Onboarding (Phase 0)**` (keeps the Phase 0 identity).
  - Sub-steps re-parented: `0.5` Task Number Pre-Assignment Validation → `1.5`; `1.5` Deep Research Loop → `2.5`; `1.7` Combined Discovery+Plan → `2.7`.
  - Main steps shifted: Input Processing `2.`, Plan & Review `3.`, Implement & Inject `4.`, Adversarial QA `5.`, Team Review `6.`, Fix Loop `7.`, PO Acceptance `8.`, Commit & Close `9.`.
  - Internal cross-reference "Loop back to step 3" corrected to "Loop back to step 4" (Implement & Inject is now step 4).
- Opening `<execution_workflow>` and closing `</execution_workflow>` tags moved to their own lines. Note: prettier canonically indents the closing tag with 3 spaces (verified via `npx prettier system-prompt.md` diff); the functional fix — tag no longer jammed onto item text — is satisfied. Prettier is the repo's formatting authority, so its canonical form is kept.

### Polish 3 — README skill-templates tree (README.md)

- Completed the tree with all 28 skill directories, split into two labeled groups mirroring the Agent Skills Registry tables (`# General & Workflow` = 16 dirs, `# Stack-Specific Blueprints` = 12 dirs), alphabetical within each group. Existing entries retained with their inline comments.
- Deviations beyond the Orchestrator's list: `audit-agents/` was missing from the README (before and after the Orchestrator's additions) but exists in the repo — added per the rule's own logic ("add the missing skill directories that exist in the repo but not in the README"). `versioning-and-release/` and `code-search/` were also completed/grouped correctly (code-search moved to the General group where it belongs).
- Verified 1:1 with `comm`: every `skill-templates/` repo dir appears in the tree, no extras.

### Verification

- `npx prettier --check README.md system-prompt.md` → exit 0.
- Grep gates: V7 line (1), `## Key V7 Changes` (1), `1. **Discovery & Onboarding (Phase 0)` (1), `9. **Commit & Close` (1), `Loop back to step 4` (1), `<system_version>7.1.1` (1), sub-steps 1.5/2.5/2.7 present (1 each), no orphan `0.5/1.5(Deep Research)/1.7` numbering.
- CHANGELOG `## [7.1.1] - 2026-08-01` created below `[Unreleased]` via Parse-Then-Append (header absent → created; single `### Changed` section, no duplicates).
- No commit executed (ZAC) — changes staged via the `custom_context_stage_and_inject_diff` MCP tool only.

### Post-Review Corrections (2026-08-01)

Applied three fixes from the Code Reviewer's findings on Task 67:

1. **task-generator Collision Check renumbered `2.5` → `3.5`** — the step was numbered 2.5 but physically sat between steps 3 (Name) and 4 (Generate File). Renumbered to 3.5 so the numerical order ascends. Content identical.
2. **README skill-templates tree group labels moved out of the tree** — removed the two pseudo-directory comment lines (`│   ├── # General & Workflow`, `│   ├── # Stack-Specific Blueprints`) and replaced them with standalone `**General & Workflow:**` / `**Stack-Specific Blueprints:**` lines immediately before the first entry of each group. All 28 skill directories unchanged.
3. **Memory auto-deletion policy reconciled** — `project-memory` Supersession Detection step 3 now explicitly scopes auto-`delete_memory` to store-time supersession within the same namespace and key topic ("the ONE allowed auto-deletion path"), resolving the contradiction with `archive-tasks` Memory Validation step (f) ("NEVER auto-delete memories without explicit Manager confirmation").

No version bump — corrections to documentation introduced within the same 7.1.1 release cycle. CHANGELOG `## [7.1.1]` `### Fixed` section appended via Parse-Then-Append (no duplicate headers). No commit executed; changes staged via the MCP tool only.

### Final Polish Corrections (post Code Review)

1. **README skill-tree group labels made fully standalone (Issue #1)** — the labels already lacked the `├──` connector (removed in the prior correction round), so this pass added blank `│` separator lines above and below each label, giving clean visual separation before `archive-tasks/` and `android-kotlin/`.
2. **Task 67 header path corrected (Issue #2)** — `**File:**` updated from `tasks/backlog/67-readme-system-prompt-v7-polish.md` to `tasks/in-progress/67-readme-system-prompt-v7-polish.md`.
3. **Skills count fixed (Issue #3)** — `## Key V7 Changes` now reads "**28 skills** including..." (was "30+"), matching the actual repo count (16 General & Workflow + 12 Stack-Specific).
4. **CHANGELOG dash normalized (Issue #4)** — `## [7.0.1] — 2026-07-25` (em-dash) changed to `## [7.0.1] - 2026-07-25` (hyphen), aligning with newer entries.

Verification: `npx prettier --check README.md CHANGELOG.md` exit 0; no `├── #` pseudo-directory lines remain; labels have blank-line separation (4 `│`-only lines); task header and 28-count confirmed. No version bump (same 7.1.1 cycle, no `system-prompt.md` edits). No commit executed — staged via MCP tool only.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

**Factual Git Diff:** Stored in Commit Hash: `14061d5`
<!-- END_GIT_DIFF -->

```

```
