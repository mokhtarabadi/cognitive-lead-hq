# Task: Add Memory Management to README roadmap

**File:** `tasks/39-add-memory-management-to-roadmap.md`
**Type:** improvement
**Status:** closed

## Goal

Add the Memory Management (Smart Note-Taking MCP & Skill) specification as item #7 in the Future Architectural Roadmap section of README.md.

## Manager's Notes

- Append a new roadmap item describing a local `memory-mcp` server and `project-memory` skill for persistent, project-specific context retention.
- Update CHANGELOG.md under `[Unreleased]` > `Changed`.

## Local TODOs

- [x] Initial codebase exploration — read README.md roadmap section
- [x] Step 1: Create tasks/39-add-memory-management-to-roadmap.md
- [x] Step 2: Append Memory Management item #7 to README roadmap
- [x] Step 3: Update CHANGELOG.md
- [x] Step 4: Verify functionality — run prettier

## OpenCode Execution Log & Reasoning

### Files Modified

| File                                           | Change                                                                     |
| ---------------------------------------------- | -------------------------------------------------------------------------- |
| `README.md`                                    | Added Memory Management (Smart Note-Taking MCP & Skill) as roadmap item #7 |
| `CHANGELOG.md`                                 | Added entry under `[Unreleased]` > `Changed`                               |
| `tasks/39-add-memory-management-to-roadmap.md` | Created as tracking task file                                              |

### Architectural Reasoning

- **Roadmap placement**: Item #7 follows the existing 6 items in the Future Architectural Roadmap section. Keeps the sequential numbering consistent.
- **Memory MCP + Skill pairing**: The specification describes both a local MCP server (`memory-mcp`) for data operations and an Agent Skill (`project-memory`) for the interface layer — following the same pattern as the `custom_context` MCP server with its `code-search` skill.
- **JSON file storage**: `.opencode/project-memory.json` keeps memory project-scoped and commit-friendly, avoiding centralized databases or external services.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 3f61ced..a88bccd 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

 ## [Unreleased]

+### Changed
+
+- **README roadmap** — Added Memory Management (Smart Note-Taking MCP & Skill) as item #7 in the Future Architectural Roadmap, describing a local `memory-mcp` server and `project-memory` agent skill for persistent context retention.
+
 ## [5.19.0] — 2026-07-15

 ### Added
diff --git a/README.md b/README.md
index d9bcb61..7f626ac 100644
--- a/README.md
+++ b/README.md
@@ -289,3 +289,10 @@ See `.opencode/skills/sop-maintenance/SKILL.md` for the rules that AI agents mus
 4. **Database Migration Management:** Create a `database-migration` skill to strictly forbid direct schema alterations, forcing the use of standard migration tools (Prisma, Alembic, Flyway) for safe, repeatable deployments.
 5. **Automated Prompt Refactoring Pipeline:** Integrate the new `prompt-refactor` skill into an auto-refine pre-hook so that Manager inputs are automatically expanded into elite system prompts before code execution begins.
 6. **Hexagonal Architecture Expansion:** Port the strict Ports & Adapters blueprint from Go to our Python (FastAPI) and TypeScript (Node.js) templates to unify "Max Power" backend design patterns across all supported stacks.
+7. **Memory Management (Smart Note-Taking MCP & Skill):** Develop a local MCP server paired with a dedicated Agent Skill to give OpenCode persistent, project-specific memory. This solves the issue of the admin needing to repeatedly explain project quirks (e.g., "for this project, tests must run with flag X").
+   - **Storage:** State will be maintained in a local JSON file within the project itself (e.g., `.opencode/project-memory.json`), allowing it to be committed or git-ignored as needed.
+   - **MCP Server (`memory-mcp`):** A lightweight Python/FastMCP server providing tools to `store_note`, `retrieve_notes`, and `search_memory` intelligently.
+   - **Agent Skill (`project-memory`):** A `SKILL.md` that teaches OpenCode the exact interface for this memory. It will enable seamless, natural language commands from the admin, such as:
+     - _"OpenCode, load the memory skill, see what the notes are, and follow them."_
+     - _"OpenCode, call the memory skill; remember this thing I'm telling you about the database tests."_
+   - **Goal:** Ensure complete, highly detailed context retention across isolated sessions without permanently bloating the core `AGENTS.md` file.
```

<!-- END_GIT_DIFF -->
