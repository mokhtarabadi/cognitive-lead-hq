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
├── mcp-context-server/
│   └── server.py                       # FastMCP server for .gitignore-aware file reading & tree
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

## Custom Code Context MCP

This system uses a local **FastMCP** Python server (`mcp-context-server/server.py`) that runs via `uv run` with zero-install dependency management. It provides deterministic, `.gitignore`-aware file reading and directory tree exploration, using far fewer tokens than raw `grep`/`glob` operations.

### Setup Instructions

This server can be installed locally per-project, or globally for all OpenCode sessions on your machine.

#### Option A: Project-Level Setup (New or Existing Projects)
Best for keeping project dependencies isolated.
1. Copy `mcp-context-server/server.py` into your project root.
2. Ensure it is executable: `chmod +x mcp-context-server/server.py`.
3. Add the following to your project's `./opencode.json`:
```json
{
  "mcp": {
    "custom_context": {
      "type": "local",
      "command": ["uv", "run", "mcp-context-server/server.py"],
      "enabled": true
    }
  },
  "permission": {
    "custom_context_*": "allow",
    "get_directory_tree": "allow",
    "read_source_files": "allow"
  }
}
```

#### Option B: Global Setup (System-wide)
Best if you want this codebase exploration tool available in *every* terminal directory automatically.
1. Create a global directory for the server: `mkdir -p ~/.config/opencode/mcp-context-server`
2. Copy the `server.py` script into that directory.
3. Make it executable: `chmod +x ~/.config/opencode/mcp-context-server/server.py`.
4. Open your global config at `~/.config/opencode/opencode.json` and add the absolute path:
```json
{
  "mcp": {
    "custom_context": {
      "type": "local",
      "command": ["uv", "run", "/Users/<YOUR_USER>/.config/opencode/mcp-context-server/server.py"],
      "enabled": true
    }
  },
  "permission": {
    "custom_context_*": "allow",
    "get_directory_tree": "allow",
    "read_source_files": "allow"
  }
}
```
*(Note: Replace `/Users/<YOUR_USER>` with your actual home directory path).*

### How It Works

1. `opencode.json` configures the custom context server as a local MCP server.
2. When OpenCode needs to explore code, it uses `get_directory_tree` and `read_source_files` tools.
3. All file reads respect `.gitignore` rules and skip binary/large files automatically.
4. The strategy is documented in `skill-templates/code-search/SKILL.md`.

### Available Tools

- `get_directory_tree` — Generates an ASCII tree of the directory structure, respecting `.gitignore`.
- `read_source_files` — Reads multiple source files or directories and saves their contents into a local Markdown report inside the `context-reports/` directory, returning the file path to prevent context bloat.

## Global Skills Deployment

To make the `code-search` skill (or any other reusable skill) available in *every* terminal directory on your machine automatically, copy the skill folder into your global OpenCode configuration path.

### Step-by-Step Global Installation:

1. **Create the global skills directory** (if it does not exist yet):
   ```bash
   mkdir -p ~/.config/opencode/skills
   ```

2. **Copy the desired skill folder** into the global skills directory:
   For example, to install our custom `code-search` skill globally:
   ```bash
   cp -r skill-templates/code-search ~/.config/opencode/skills/
   ```

3. **Verify the installation:**
   In any folder on your machine, start OpenCode and run:
   ```bash
   /help
   ```
   Under the available skills list, you will see `code-search` listed. You can now use it in any project by asking:
   ```plaintext
   @explore find the main router using the code-search skill
   ```

## Key V4 Changes

- **Shifted from monolithic `AGENTS.md`** to OpenCode's native **Agent Skills** (`SKILL.md`) framework for progressive disclosure and optimized context usage.
- **Integrated Google's official Agentic Reasoning System Instruction** for superior logic, risk assessment, and abductive reasoning.
- **Upgraded `<opencode_task>`** to leverage OpenCode's native tools (`lsp`, `@explore`, `websearch`) instead of relying solely on bash commands.
- **Added `opencode.json` auto-configuration** to Phase 0 for enforcing formatters and tool permissions.
- **Restructured the repository**: migrated `stacks/` to `skill-templates/` and converted the repo's own rules into `.opencode/skills/sop-maintenance/SKILL.md`.

## Contributing

See `.opencode/skills/sop-maintenance/SKILL.md` for the rules that AI agents must follow when modifying this repository.
