# Task: Implement Decentralized Tasks

**Type:** feature
**Status:** completed

## Goal

Migrate from global `STATE.md` and `TODO.md` to decentralized, isolated task files.

## Manager's Notes

- Ensure task files track their own TODOs, final status, technical changes, and architectural reasoning.
- Remove global state and todo files.

## Local TODOs

- [x] Create `tasks/` directory
- [x] Add `task-generator` skill
- [x] Add `audit-agents` skill
- [x] Update `system-prompt.md` Phase 0 and personas
- [x] Clean up legacy files

## Execution Log & Technical Changes

### Files Created

- `tasks/01-implement-decentralized-tasks.md` — initial task file
- `skill-templates/task-generator/SKILL.md` — task generator skill
- `skill-templates/audit-agents/SKILL.md` — agent audit skill
- `update_prompt.py` (removed after execution) — Python script for system-prompt.md transformations

### Files Modified

- `system-prompt.md` — replaced "Gemini 3.5 Flash" with "Gemini" globally; rewrote Project Planner duty and behavior to reference decentralized task files; updated context phase to read active task file; updated documentation phase to update active task file instead of STATE.md/TODO.md; updated initialization block
- `AGENTS.md` — replaced STATE.md/TODO.md sync rules with active task file and DESIGN.md
- `.opencode/skills/sop-maintenance/SKILL.md` — added documentation sync rules for task files and DESIGN.md
- `CHANGELOG.md` — added V5.0.0 section documenting the decentralized task architecture

### Files Deleted

- `STATE.md` — replaced by decentralized task files
- `TODO.md` — replaced by per-task local TODOs

### Architectural Decisions

- Decentralized task files in `tasks/` with numbered naming convention (e.g., `01-task-name.md`) replace global state/todo files
- Each task file is self-contained with its own TODOs, status, and execution log
- Task Generator skill (`skill-templates/task-generator/`) provides a standardized workflow for creating new task files
- Audit Agents skill (`skill-templates/audit-agents/`) ensures AGENTS.md enforces task update protocols
- DESIGN.md added to documentation sync rules across all relevant files
