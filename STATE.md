# STATE.md — Cognitive Lead AI SOP Repository

## Current Architecture

This repository serves as the **HQ (Headquarters)** for the Cognitive Lead AI multi-agent system. It contains:

- `AGENTS.md` — Project Context Hub (<150 lines) with project overview, setup commands, SOP rules, and actionable do/don't guardrails; auto-loaded by OpenCode's native agent discovery
- `system-prompt.md` — V4.6 multi-agent prompt (Dual-Task Protocol, Brain/Hands separation) defining personas, Agentic Reasoning, and OpenCode protocol
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
- **V4.4.0 System Prompt V4.4 Upgrade — SOP Trilogy codified:**
  - **`AGENTS.md` (<150 lines)** — Auto-loaded Project Context Hub at project root. Concise ruleset with paired don't/do directives to prevent overexploration trap.
  - **`DESIGN.md` (YAML + prose)** — Google-spec design system file with design tokens and prose. UI/UX Designer persona now validates with `npx @google/design.md lint DESIGN.md`.
  - **`.opencode/skills/<name>/SKILL.md`** — On-demand task-specific toolkits. Keeps workflows isolated to prevent context bloat.
  - Project Planner duties updated to own `AGENTS.md` alongside `STATE.md` and `TODO.md`. Onboarding/Discovery Rule now generates the full SOP Trilogy. Sync Rule extended to cover `AGENTS.md` and `DESIGN.md`.
  - Software Architect references updated to `.opencode/skills/` path convention.
  - UI/UX Designer gains `DESIGN.md` lifecycle management and lint validation command.
- **V4.4.1 Hotfix — Reverted Agent Skills Directory to Plural:**
  - All path references in `system-prompt.md` corrected from `.opencode/skill/` (singular) back to `.opencode/skills/` (plural) to match OpenCode's native discovery mechanism.
  - Both project-local (`.opencode/skills/`) and global (`~/.config/opencode/skills/`) paths restored across all persona behaviors and protocol documentation.
- **`AGENTS.md` Project Context Hub created** — Concise ~40-line root-level `AGENTS.md` written with project overview, setup/dev commands, SOP maintenance rules, actionable do/don't guardrails, and documentation sync rules. Complements the SOP Trilogy as the auto-loaded entry point for OpenCode's native agent discovery.
- **V4.4.2 — Global Skills Deployment Guide added to README** — Added a new "Global Skills Deployment" section to `README.md` with step-by-step instructions for installing skills globally via `~/.config/opencode/skills/`. Covers directory creation, skill folder copy, and verification using `/help`.
- **V4.6.0 Dual-Task Protocol upgrade and code-search context loop fix.**
- **V4.5.0 — System Prompt V4.5 Upgrade — Schema & Path Conformance:**
  - Phase 0 Discovery & Onboarding updated to mandate creation/update of `opencode.json` at project root with `"$schema": "https://opencode.ai/config.json"`.
  - `<execution_workflow>` now enforces JSON Schema conformance for all new and existing projects.

## Known Items

- `opencode.json` configured with `custom_context` MCP server (replaced Semble)
- No application code in this repository — documentation/SOP only
