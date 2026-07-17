# Milestone 3 Summary

**Date:** 2026-07-17
**Tasks Compacted:** 7

## Architectural Changes

Established persistent project memory with an MCP server and companion skill, enabling the Manager to save constraints and project quirks across sessions. Introduced the Intelligent Cold-Start & Vertical Slicing Protocol (V6.3.0) that bundles Core SOP files as mandatory discovery steps. Integrated the Perplexity Deep Research 3-Step Framework with a reusable user prompt template and a formal human-in-the-loop halt-before-hallucination workflow. Refactored the Perplexity UX to embed the full framework prompt inside the agent message block, reducing Manager friction from 3 steps to 1 click. Hardened all 27 skill templates by standardizing YAML `name:` fields, folder names, and system prompt registry entries onto a single kebab-case identifier, fixing a latent `skill` tool invocation bug. Cleaned up the README roadmap by removing completed milestone items.

## Files Modified

| File                                           | Change                                                                                                                                                 |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `system-prompt.md`                             | V6.3.0 / V6.4.0 / V6.4.1 / V6.5.0 / V6.6.0 upgrades — cold start protocol, memory system, perplexity research, UX refactor, skill name standardization |
| `skill-templates/code-search/SKILL.md`         | Added Vertical Slicing Strategy section under Discovery Workflow                                                                                       |
| `user-prompts/cold-start-context.md`           | Created — reusable cold-start discovery prompt for the Manager                                                                                         |
| `README.md`                                    | Removed completed roadmap items, renumbered Hexagonal Architecture to #5                                                                               |
| `mcp-memory-server/server.py`                  | Created — FastMCP server with store/read/search/list_namespaces/delete_memory tools                                                                    |
| `opencode.json`                                | Added memory tool permissions                                                                                                                          |
| `skill-templates/project-memory/SKILL.md`      | Created — companion skill for the memory MCP server                                                                                                    |
| `user-prompts/perplexity-deep-research.md`     | Created — 3-Step Framework user prompt template for Perplexity                                                                                         |
| `skill-templates/perplexity-research/SKILL.md` | Created — companion skill for the deep research loop                                                                                                   |
| `skill-templates/perplexity-research/SKILL.md` | Refactored — embedded full 3-Step Framework prompt inline                                                                                              |
| `skill-templates/*/SKILL.md` (13 files)        | Fixed YAML `name:` fields to match folder names                                                                                                        |
| `CHANGELOG.md`                                 | Updated with entries for V6.3.0 through V6.6.0                                                                                                         |

## Individual Task Summaries

### Task 49: Implement Intelligent Cold-Start & Vertical Slicing Protocol

- **Type:** feature
- **Reasoning:** Solved the "empty context" problem by introducing `cold-start-context.md` and making Core SOP file injection mandatory in discovery tasks. Vertical Slice Extraction was promoted to its own step (step 3) to prevent reading the entire repo's signatures when only one module is needed.

### Task 50: Implement Project Memory System

- **Type:** feature
- **Reasoning:** Built a FastMCP server (`mcp-memory-server/server.py`) with store/read/search/list_namespaces tools and a companion `project-memory` skill. The server uses atomic writes, path traversal protection via regex validation, and automatically creates `.opencode/memory/` namespaced directories.

### Task 51: Add Memory Deletion

- **Type:** improvement
- **Reasoning:** Added `delete_memory` tool to the MCP server with stale-directory cleanup. Updated `opencode.json` permissions and documented the delete-use-case in the skill.

### Task 52: README Roadmap Cleanup

- **Type:** improvement
- **Reasoning:** Removed 6 completed/struck-through roadmap items (Kanban, QA Persona, Prompt Refactoring, Memory Management). Renumbered Hexagonal Architecture from item 6 to 5.

### Task 53: Implement Perplexity Deep Research Workflow

- **Type:** improvement
- **Reasoning:** Introduced a formal human-in-the-loop bridge for post-2025 knowledge gaps. Created `user-prompts/perplexity-deep-research.md` encoding a Broad → Refined → Precise search pyramid, and a companion skill teaching OpenCode when to halt and delegate to the Manager.

### Task 54: Refactor Perplexity Research Skill UX

- **Type:** improvement
- **Reasoning:** Embedded the entire 3-Step Framework prompt inside the agent's message block with a single `[INSERT YOUR SPECIFIC QUERY HERE]` placeholder. Reduced Manager operation from 3 steps to 1 click. Preserved the standalone user prompt for manual use.

### Task 55: Standardize Skill Names Across Templates and System Prompt

- **Type:** improvement
- **Reasoning:** Audited all 27 skills and fixed 13 prefixed YAML `name:` fields (`backend-architecture-*`, `frontend-architecture-*`, `mobile-architecture-*`, `stitch::extract-design-md`) to match folder names. Added 2 missing skills to the system prompt registry. Aligned all 27 descriptions verbatim between YAML and system prompt. This fixes a latent bug where the `skill` tool could fail to find a skill by its short name.
