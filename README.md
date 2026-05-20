# Cognitive Lead AI — V4 Multi-Agent System Prompt & Agent Skills

This repository is the **V4 evolution** of the Cognitive Lead AI multi-agent system. It has been restructured to adopt the **Agent Skills** standard and Google's official Agentic Workflow constraints, maximizing OpenCode's native context management and reasoning capabilities.

## Purpose

- **Unified Agent Instruction** — `system-prompt.md` is the single source of truth for agent behavior, role definitions, Google-aligned Agentic Reasoning, and the `<opencode_task>` protocol.
- **Agent Skills (`SKILL.md`)** — Instead of a monolithic `AGENTS.md` or flat `stacks/` directory, the system now uses OpenCode's native **Agent Skills** framework for progressive disclosure: `.opencode/skills/*/SKILL.md` for repository rules and `skill-templates/*/SKILL.md` for reusable stack blueprints.
- **Progressive Disclosure** — OpenCode's `skill` tool loads only the relevant `SKILL.md` at the moment it is needed, optimizing context usage and keeping the system prompt lean.

## How to Use This Repository

| File / Directory | When to Consult |
|---|---|
| `system-prompt.md` | At the start of every session; this is the V4 multi-agent prompt defining all 5 personas and the Agentic Reasoning matrix. |
| `.opencode/skills/sop-maintenance/SKILL.md` | When an AI agent needs to modify this repository itself. |
| `skill-templates/*/SKILL.md` | Before writing code in a specific stack (Node.js, Spring Boot, Flask, Next.js, Android Kotlin/Java). |
| `CHANGELOG.md` | To review what has changed between versions. |
| `TODO.md` | To see which stacks are planned for future coverage. |

## Repository Structure

```
/
├── README.md                           # This file
├── system-prompt.md                    # V4 Multi-Agent System Prompt
├── CHANGELOG.md                        # Version history
├── TODO.md                             # Roadmap for new stacks
├── .opencode/
│   └── skills/
│       └── sop-maintenance/
│           └── SKILL.md                # Native OpenCode skill for repo rules
    └── skill-templates/                    # Reusable stack blueprints (Agent Skills)
        ├── nodejs-express/
        │   └── SKILL.md
        ├── spring-boot/
        │   └── SKILL.md
        ├── flask-python/
        │   └── SKILL.md
        ├── nextjs/
        │   └── SKILL.md
        ├── android-kotlin/
        │   └── SKILL.md
        ├── android-java-xml/
        │   └── SKILL.md
        └── code-search/
            └── SKILL.md
```

## Code Search & MCP Integration

This system uses **Semble**, a semantic code search engine that runs locally via MCP. Semble understands natural language queries (e.g., "find the authentication flow") and returns highly targeted code chunks, using ~98% fewer tokens than standard `grep`/`read` operations.

### Prerequisites

Semble runs via `uvx` (no installation required), but you need the `uv` package manager:

| Platform | Command |
|---|---|
| macOS / Linux | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Windows | `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` |

### How It Works

1. The `opencode.json` in this repo configures Semble as an MCP server.
2. When OpenCode needs to explore code, it uses natural-language `semble_search` and `semble_find_related` tools instead of raw `grep`/`glob`.
3. The strategy is documented in `skill-templates/code-search/SKILL.md`.

### Available Tools

- `semble_search` — Find code by describing it in natural language.
- `semble_find_related` — Get more context around a specific file and line.

## Key V4 Changes

- **Shifted from monolithic `AGENTS.md`** to OpenCode's native **Agent Skills** (`SKILL.md`) framework for progressive disclosure and optimized context usage.
- **Integrated Google's official Agentic Reasoning System Instruction** for superior logic, risk assessment, and abductive reasoning.
- **Upgraded `<opencode_task>`** to leverage OpenCode's native tools (`lsp`, `@explore`, `websearch`) instead of relying solely on bash commands.
- **Added `opencode.json` auto-configuration** to Phase 0 for enforcing formatters and tool permissions.
- **Restructured the repository**: migrated `stacks/` to `skill-templates/` and converted the repo's own rules into `.opencode/skills/sop-maintenance/SKILL.md`.

## Contributing

See `.opencode/skills/sop-maintenance/SKILL.md` for the rules that AI agents must follow when modifying this repository.
