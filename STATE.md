# STATE.md — Cognitive Lead AI SOP Repository

## Current Architecture

This repository serves as the **HQ (Headquarters)** for the Cognitive Lead AI multi-agent system. It contains:
- `system-prompt.md` — V4.1 multi-agent prompt defining personas, Agentic Reasoning, and OpenCode protocol
- `skill-templates/` — Reusable Agent Skills (SKILL.md with YAML frontmatter) for common tech stacks and workflows
  - `code-search/SKILL.md` — Semble semantic code search strategy (importable template)
- `.opencode/skills/` — Native OpenCode skills for progressive disclosure
  - `sop-maintenance/SKILL.md` — Rules for editing this repository
  - `code-search/SKILL.md` — Semble semantic code search strategy

## Key Integrations

- **Semble MCP** — Semantic code search engine configured in `opencode.json`. Uses `uvx` for zero-install execution.
- **OpenCode Protocol** — All implementation tasks are dispatched via `<opencode_task>` XML blocks.

## Completed Features

- V4 Multi-Agent Skills architecture migration (monolithic AGENTS.md → SKILL.md)
- 6 stack templates in `skill-templates/` (Node.js, Spring Boot, Flask, Next.js, Android Kotlin, Android Java)
- V4.1 production-ready refinements (MCP support, STATE.md, test enforcement)
- Semble MCP integration and code-search Agent Skill
- `code-search` template added to `skill-templates/` for reusable import into new projects

## Known Items

- `opencode.json` configured with Semble MCP; no other MCP servers configured yet
- No application code in this repository — documentation/SOP only
