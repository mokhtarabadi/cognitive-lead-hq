# Task: Standardize Skill Names Across Templates and System Prompt

**File:** `tasks/backlog/55-standardize-skill-names-across-templates-and-system-prompt.md`
**Type:** improvement
**Status:** closed

## Goal

Ensure three-way consistency across all 27 skills in `skill-templates/`:
1. **Folder name** matches the YAML `name:` frontmatter field in each `SKILL.md`
2. **YAML `description:`** field matches the system prompt description for each skill
3. **System prompt entry name** matches the folder name / YAML name

Also add 2 missing skills (`archive-tasks`, `migrate-kanban`) to the system prompt table.

## Manager's Notes

- The YAML frontmatter `name:` must be the canonical identifier and match the folder name exactly
- System prompt descriptions were aligned verbatim from YAML `description:` fields
- Markdown `#` headings are display titles and should remain detailed / human-readable (NOT changed)
- 13 skills had architecture-prefixed YAML names (e.g. `backend-architecture-flask-python` → `flask-python`)

## Local TODOs

- [x] Audit all 27 SKILL.md YAML `name:` fields against folder names
- [x] Fix 13 mismatched YAML `name:` fields (remove architecture prefixes)
- [x] Fix 1 `stitch::extract-design-md` YAML name → `design-md`
- [x] Restore all 27 markdown `#` headings to original detailed titles
- [x] Add `archive-tasks` and `migrate-kanban` to system prompt Global Workflow Skills
- [x] Align all 27 system prompt descriptions with YAML `description:` fields
- [x] Final three-way consistency verification (all pass)

## OpenCode Execution Log & Reasoning

_OpenCode: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool_

**Architectural Reasoning:**
The skill loading system (both the `skill` tool and `<available_skills>` list) uses the YAML `name:` field as the canonical identifier. Previously, 13 skills had prefixed names (e.g. `backend-architecture-flask-python`) while their folders and system prompt entries used short names (e.g. `flask-python`). This mismatch would cause the `skill` tool to fail when the orchestrator instructed OpenCode to load a skill by its short name. The fix standardizes all three layers (folder, YAML name, system prompt entry) on the same short kebab-case identifier.

**Files Modified:**
- `skill-templates/*/SKILL.md` — YAML `name:` field in 13 files, markdown `#` headings restored in all 27 files
- `system-prompt.md` — Added 2 missing skills, aligned all 27 descriptions with YAML counterparts

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `d6208c647d35c3baefec370c8e666d95906ce088`
<!-- END_GIT_DIFF -->
