# Task: README Roadmap Cleanup

**File:** `tasks/in-progress/52-readme-roadmap-cleanup.md`
**Type:** improvement
**Status:** closed

## Goal

Clean up the Future Architectural Roadmap section in `README.md` by removing completed/struck-through items and renumbering the remaining items.

## Manager's Notes

- Items implemented in V6.0.0 (Kanban), V6.1.0 (QA Persona), V6.2.0 (Prompt Refactoring), and V6.4.0 (Memory Management) should be removed.
- Only items 1-4 and the Hexagonal Architecture Expansion item remain.
- Renumber Hexagonal Architecture Expansion from 6 to 5.
- Update CHANGELOG.md with a [6.4.1] release entry.

## Local TODOs

- [x] Step 1: Create task file
- [ ] Step 2: Update README.md - remove completed roadmap items
- [ ] Step 3: Update CHANGELOG.md with [6.4.1] release entry
- [ ] Step 4: Run Prettier formatting
- [ ] Step 5: Finalize - update task log, stage diff, notify Manager

## OpenCode Execution Log & Reasoning

- Removed completed/struck-through roadmap items 5-9 from `README.md` (items implemented in V6.0.0 Kanban, V6.1.0 QA Persona, V6.2.0 Prompt Refactoring, V6.4.0 Memory Management).
- Renumbered Hexagonal Architecture Expansion from 6 → 5.
- No functional changes to roadmap items 1-4.
- Injected `[6.4.1]` changelog entry with a `### Changed` block documenting the README cleanup.
- Ran `npx prettier --write` on both files — already well-formatted, no changes needed.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `0e0fb2be959ad3211c8cd1f526d2d42676ae6400`
<!-- END_GIT_DIFF -->
