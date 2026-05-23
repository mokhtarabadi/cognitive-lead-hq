# STATE.md — Cognitive Lead AI SOP Repository

## Current Architecture

This repository serves as the **HQ (Headquarters)** for the Cognitive Lead AI multi-agent system. It contains:
- `system-prompt.md` — V4.3 multi-agent prompt defining personas, Agentic Reasoning, and OpenCode protocol (Gemini 3.5 Flash optimized, Brain/Hands separation established)
- `docs/` — Architecture and runtime reference documentation
  - `gemini-3.5-flash-guidelines.md` — Prompting guidelines, parameter updates, function response matching, and tool overuse control for the Gemini 3.5 Flash runtime
  - `opencode-architecture-reference.md` — Configuration hierarchy, permissions engine, LSP/formatter detection, agent/subagent navigation, and tool mechanics
- `skill-templates/` — Reusable Agent Skills (SKILL.md with YAML frontmatter) for common tech stacks and workflows
  - `code-search/SKILL.md` — Custom context MCP code search strategy (importable template)
- `.opencode/skills/` — Native OpenCode skills for progressive disclosure
  - `sop-maintenance/SKILL.md` — Rules for editing this repository
  - `code-search/SKILL.md` — Custom context MCP code search strategy

## Key Integrations

- **Custom Context MCP** — Local Python FastMCP server (`mcp-context-server/server.py`) for deterministic, `.gitignore`-aware file reading and directory tree exploration. Runs via `uv run` with zero-install dependency management.
- **OpenCode Protocol** — All implementation tasks are dispatched via `<opencode_task>` XML blocks.

## Completed Features

- V4 Multi-Agent Skills architecture migration (monolithic AGENTS.md → SKILL.md)
- 6 stack templates in `skill-templates/` (Node.js, Spring Boot, Flask, Next.js, Android Kotlin, Android Java)
- V4.1 production-ready refinements (MCP support, STATE.md, test enforcement)
- Custom Context MCP server replacing Semble — deterministic `.gitignore`-aware file exploration with `get_directory_tree` and `read_source_files` tools; `read_source_files` writes reports to `context-reports/` to prevent context bloat
- `code-search` template added to `skill-templates/` for reusable import into new projects
- **V4.3.0 Gemini 3.5 Flash stable upgrade:**
  - `docs/gemini-3.5-flash-guidelines.md` — Prompting guidelines, parameter updates (no `temperature`/`top_p`/`top_k`; use `thinking_level`), strict function response matching, multimodal/inline instruction patterns, and tool overuse control
  - `docs/opencode-architecture-reference.md` — Configuration hierarchy and merge order, permissions engine with wildcard and last-matching-rule semantics, LSP/formatter auto-detection mapping, agent/subagent types and multi-turn session navigation, `apply_patch` path marker mechanics, and `question` tool schema
  - `system-prompt.md` updated to V4.3 — Added `<system_context>` tag block, revised `<agentic_reasoning>` aligned with Gemini 3.5 Agentic Workflow template (Logical dependencies, Risk assessment, Abductive reasoning, Grounding, Outcome evaluation, Information availability, Precision, Completeness, Inhibit response), output verbosity control rules, and Gemini 3.5 Flash runtime constraint
  - Persona behaviors updated — Software Architect and Senior Programmer now reference `docs/` for architectural and coding decisions
  - **Orchestrator boundaries established** — `system-prompt.md` rewritten with clear Brain/Hands separation: Cognitive Lead AI (Gemini 3.5 Flash in AI Studio) orchestrates via text blocks; OpenCode (local agent) executes. `<role>` explicitly states no file-system/terminal/network access. `<system_context>` updated. Project Planner gains Onboarding/Discovery and Sync rules. Constants block added with Tool Use and Non-Interactive rules.

## Known Items

- `opencode.json` configured with `custom_context` MCP server (replaced Semble)
- No application code in this repository — documentation/SOP only
