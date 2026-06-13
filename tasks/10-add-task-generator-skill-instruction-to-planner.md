# Task 10: Add Task-Generator Skill Instruction to Project Planner

**Type:** improvement
**Status:** open

## Goal

Add an explicit instruction in the Project Planner persona's `<behavior>` to load the `task-generator` skill when creating new task files, ensuring the template format includes the correct `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.

## Manager's Notes

- The system prompt had no instruction forcing OpenCode to load the `task-generator` skill for task file creation.
- Inserted into Project Planner's behavior block in `system-prompt.md`.

## Local TODOs

- [x] Add instruction to Project Planner behavior in system-prompt.md
- [x] Bump system_version to 5.4.1
- [x] Update CHANGELOG.md
- [x] Create task file

## OpenCode Execution Log & Reasoning

- Edited `system-prompt.md` line 45 (Project Planner behavior) to add: "When creating a new task file, instruct OpenCode to load the `task-generator` skill to ensure the correct template format with `<!-- BEGIN_GIT_DIFF -->` and `<!-- END_GIT_DIFF -->` markers."
- Bumped `<system_version>` from `5.4.0` to `5.4.1` (PATCH bump — minor docs/improvement change).
- Added `[5.4.1]` changelog entry under `Changed` category.
- Created this task file using the task-generator template format.

## Factual Git Diff
<!-- BEGIN_GIT_DIFF -->
*(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)*
<!-- END_GIT_DIFF -->
