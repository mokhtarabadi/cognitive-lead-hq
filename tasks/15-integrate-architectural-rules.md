# Task 15: Integrate Architectural Rules & Core Templates

**Type:** feature
**Status:** completed

## Goal

Upgrade the Cognitive Lead AI system to V5.9.0 by introducing the 🛑 MANDATORY FIRST-READ RULE, parallel subagent guidelines, Phase 0 architectural file generation, and high-performance AI initialization templates for Android, Spring Boot, Node.js, Nuxt, and Next.js.

## Manager's Notes

- Bump system version to 5.9.0 in system-prompt.md.
- Write complete architecture, design, and agents templates directly into the audit-agents skill file.
- Standardize five tech-stack templates with modern best-in-class conventions.
- Update both workspace and global user skill directories.

## Local TODOs

- [x] Create Tasks 15 md file
- [x] Edit system-prompt.md to V5.9.0 (parallel agents + first-read rules)
- [x] Edit AGENTS.md to include the 🛑 MANDATORY FIRST-READ RULE
- [x] Rewrite skill-templates/audit-agents/SKILL.md with full templates & Target Audit Criteria
- [x] Rewrite five tech-stack templates (Android, Spring Boot, Node.js Express, Vue Nuxt, Next.js Next)
- [x] Sync workspace audit-agents skill to ~/.config/opencode/skills/audit-agents/SKILL.md
- [x] Update CHANGELOG.md with V5.9.0 entry
- [x] Run Prettier formatting check on modified markdown files

## OpenCode Execution Log & Reasoning

### Architectural Reasoning

This upgrade introduces the **Mandatory First-Read Rule** — a critical architectural pattern ensuring every agent reads `AGENTS.md` first, which then routes to `DESIGN.md`, `architecture.md`, `data_model.md`, and `conventions.md`. This prevents style/structural misalignment by guaranteeing agents have full context before writing any code.

Key design decisions:

1. **Version bump to 5.9.0** — skipping 5.8.x to align with the significance of this structural change.
2. **Parallel subagent declaration** — explicitly advertising OpenCode's ability to run up to 4 concurrent agents during Phase 0 discovery.
3. **Audit-agents template expansion** — the skill now contains ready-to-use templates for `architecture.md`, `DESIGN.md`, and structured audit criteria, making it a one-stop shop for project initialization.
4. **Tech-stack scaffolding** — each of the 5 templates now includes a "Modern Project Initiation Guide" section with strict, opinionated rules for AI-driven code generation, ensuring consistent output across frameworks.

### Execution Notes

- Created `tasks/15-integrate-architectural-rules.md` as the active task file.
- Edited `system-prompt.md` — bumped version, added parallel agents note, updated Software Architect to mandate AGENTS.md first-read, updated Senior Programmer to instruct first-read, updated Planner for parallel Phase 0 subagents.
- Edited `AGENTS.md` — added the Mandatory First-Read Rule section as the very first section after the title.
- Fully rewrote `skill-templates/audit-agents/SKILL.md` — added Target Audit Criteria section, architecture.md template, and DESIGN.md template.
- Updated 5 tech-stack templates with AI-driven scaffolding sections.
- Synced to `~/.config/opencode/skills/audit-agents/SKILL.md`.
- Added V5.9.0 entry to CHANGELOG.md.
- Ran Prettier formatting check — all markdown files pass.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
