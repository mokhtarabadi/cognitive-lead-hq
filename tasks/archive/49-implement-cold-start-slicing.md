# Task: Implement Intelligent Cold-Start & Vertical Slicing Protocol

**File:** `tasks/in-progress/49-implement-cold-start-slicing.md`
**Type:** feature
**Status:** closed

## Goal

Upgrade the system to V6.3.0 by implementing the Intelligent Cold-Start & Vertical Slicing Protocol. This introduces a reusable cold-start prompt for the Manager, updates the discovery task template to mandate Core SOP file injection alongside vertical slice signature extraction, and documents the Vertical Slicing Strategy in the code-search skill.

## Manager's Notes

- Version bump: 6.2.0 → 6.3.0
- System prompt: update both the discovery template's `<execution_phase>` and the `<execution_workflow>` Phase 0
- code-search skill: add `### Vertical Slicing Strategy` under `## Discovery Workflow`
- Create new file: `user-prompts/cold-start-context.md`
- Update README.md directory tree and CHANGELOG.md with [6.3.0] release notes

## Local TODOs

- [x] Step 1: Scaffold task file
- [x] Step 2: Update system-prompt.md version to 6.3.0 and discovery task template
- [x] Step 3: Update system-prompt.md execution_workflow Phase 0
- [x] Step 4: Update code-search/SKILL.md with Vertical Slicing Strategy
- [x] Step 5: Create user-prompts/cold-start-context.md
- [x] Step 6: Update README.md tree and CHANGELOG.md
- [x] Run `npx prettier --write "**/*.md"` to format files

## OpenCode Execution Log & Reasoning

### Architectural Reasoning

The core motivation for V6.3.0 is to solve the "empty context" problem when starting a new AI Studio session with an existing project. Previously, the Manager had to manually paste directory trees and file contents to Bootstrap the Brain. The Vertical Slicing Protocol introduces a dedicated discovery prompt (`cold-start-context.md`) that the Manager can paste directly into OpenCode to generate a complete context report in one shot.

**Key architectural decisions:**

1. **Core SOP bundling is now mandatory in discovery tasks.** The `<opencode_discovery_task_template>` execution phase was modified so that AGENTS.md, DESIGN.md, and all docs/*.md are fetched via `read_source_files` as an explicit step (step 2), not buried in a generic list. This guarantees the Brain always receives the project's architectural ground truth.

2. **Vertical Slice Extraction is a separate step (step 3).** By placing signature extraction after Core SOP reading and before compilation, we preserve the logical flow: (a) map the tree → (b) load rules → (c) extract slice → (d) compile. This prevents OpenCode from reading the entire repo's signatures when only one module is needed.

3. **Phase 0 cold-start routing in execution_workflow.** EXISTING projects with empty context now trigger an automatic discovery task rather than leaving the Manager to manually provide details. This closes a gap where the workflow assumed either a new project (Phase 0 scaffolding) or the Manager already had context.

4. **code-search skill Vertical Slicing Strategy** is documented as a sub-section under the existing Discovery Workflow to avoid duplicating the full skill's content while adding targeted slice guidance. The mandatory "append Core SOP files to every report" rule is enforced within this section.

5. **cold-start-context.md** uses dual-language copy-paste blocks (English + Farsi) mirroring the existing `user-prompts/` convention established in V5.5.0.

### Files Modified

- `system-prompt.md` — version bump 6.2.0→6.3.0, discovery template execution_phase rewritten, Phase 0 workflow updated with cold-start routing
- `skill-templates/code-search/SKILL.md` — new `### Vertical Slicing Strategy` section under Discovery Workflow
- `CHANGELOG.md` — [6.3.0] release notes
- `README.md` — directory tree updated to include new user-prompt file
- `tasks/in-progress/49-implement-cold-start-slicing.md` — this file

### Files Created

- `user-prompts/cold-start-context.md` — reusable dual-language cold-start prompt

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

**Factual Git Diff:** Stored in Commit Hash: `f517cf91bc055e58ebb7af78cf66bf3f38104296`
<!-- END_GIT_DIFF -->
