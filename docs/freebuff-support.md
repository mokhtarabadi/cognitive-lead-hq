# Partial Freebuff Support

> **Primary runtime is OpenCode.** This document is a supplementary guide for users who want to run the
> Cognitive Lead AI workflow with **Freebuff** (`freebuff.com`, vendor: manicode — formerly Codebuff-based)
> instead of — or alongside — OpenCode. The system prompt (`system-prompt.md`) still generates tasks for
> **OpenCode**: this is deliberately **partial support** and does not change the primary workflow.
>
> - **Last verified:** 2026-08-12 (Freebuff CLI `0.0.146`, binary analysis)
> - **Source of truth:** Task 96 — the task file moves between Kanban directories; reference it by ID, not by path.
> - **Overall status:** ⚠️ PARTIAL — MCP servers and Skills work in Freebuff; custom agents are installed but
>   blocked on the free tier (HTTP 403 `free_mode_invalid_agent_model`); the Orchestrator Brain and task
>   lifecycle remain OpenCode-oriented.

---

## 1. What Freebuff Is

Freebuff (`freebuff.com`, vendor: **manicode** — formerly Codebuff-based) is a **terminal AI coding agent**:

| Fact            | Value                         |
| --------------- | ----------------------------- |
| **Binary**      | `~/.config/manicode/freebuff` |
| **Version**     | `0.0.146`                     |
| **Platform**    | Linux x64                     |
| **Config root** | `~/.config/manicode/`         |

**Key fact for this guide:** Freebuff does **not** read `opencode.json`, `AGENTS.md` agent definitions, or the
OpenCode skill registry. It has its own extension points (see §2) rooted at `.agents/` folders.

---

## 2. Freebuff Extension Points (Discovered via Binary Analysis)

Extension points were discovered via binary analysis on 2026-08-12 and confirmed in-session for MCP servers and Skills.

### 2.1 MCP Servers — `.agents/mcp.json`

Standard MCP config in the `{ "mcpServers": { ... } }` shape. Available automatically to all base agents.

**Search order** (later overrides earlier):

1. `{cwd}/.agents/mcp.json` — project-specific
2. `{cwd}/../.agents/mcp.json` — parent directory (monorepos)
3. `~/.agents/mcp.json` — **global** (`~/.agents/`)

**Supported shapes** (per [MCP docs](https://www.codebuff.com/docs/tips/mcp-servers)):

```json
{
  "mcpServers": {
    "myServer": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "/absolute/path/to/server.py"],
      "env": { "MY_VAR": "$MY_VAR" }
    }
  }
}
```

- `type` defaults to `stdio`; `http` and `sse` types are supported for remote servers (`url`, `headers`, `params`).
- Environment variables use `$VAR_NAME` syntax and resolve from the shell or a project `.env`.

### 2.2 Skills — `.agents/skills/<name>/SKILL.md`

Skills are reusable instruction sets loaded via the `skill` tool or `/skill:<name>` slash commands.

**Discovery locations** (later overrides earlier):

1. `~/.claude/skills/` — global (Claude Code compatibility)
2. `~/.agents/skills/` — **global**
3. `.claude/skills/` — project
4. `.agents/skills/` — project (highest priority)

**Frontmatter requirements** (per [Skills docs](https://www.codebuff.com/docs/tips/skills)):

```markdown
---
name: my-skill # required: 1-64 chars, lowercase alphanumeric + hyphens, MUST equal the directory name
description: What it does and when to use it # required
license: MIT # optional
metadata: # optional
  category: development
---
```

### 2.3 Custom Agents — `.agents/*.ts`

TypeScript modules in `.agents/` exporting a default `AgentDefinition` (see official
[Agent Reference](https://www.codebuff.com/docs/agents/agent-reference) and
[Creating New Agents](https://www.codebuff.com/docs/agents/creating-new-agents)).

**Key fields:**

- `id` (required, lowercase/numbers/hyphens), `displayName` (required), `spawnerPrompt`
- `model` (required — OpenRouter-style id, e.g. `anthropic/claude-sonnet-4.5`)
- `toolNames` — whitelist of the [17 platform tools](#platform-tools) (default `["end_turn"]`)
- `spawnableAgents` — other agents this agent can spawn. Built-ins **must** use `publisher/name@version`
  (e.g. `codebuff/researcher@0.0.1`); local `.agents/` agents use bare ids
- `systemPrompt` / `instructionsPrompt` / `stepPrompt` — string **or** `{ "path": "./file.md" }`
- `outputMode` (`last_message` | `all_messages` | `structured_output`), `includeMessageHistory`, `outputSchema`
- `handleSteps` — optional programmatic generator (`yield 'STEP'` / `'STEP_ALL'` / tool calls)
- `inputSchema` — JSON Schema for spawn prompt/params
- `mcpServers` — optional per-agent MCP servers

**Invocation:** `@My Agent Display Name <prompt>` in the CLI, or via `spawn_agents`.

**Platform tools** (toolNames whitelist): `add_subgoal`, `browser_logs`, `code_search`, `create_plan`,
`end_turn`, `find_files`, `read_docs`, `read_files`, `run_file_change_hooks`, `run_terminal_command`,
`spawn_agents`, `str_replace`, `think_deeply`, `update_subgoal`, `web_search`, `write_file`, `set_output`.

**Built-in agents:** `codebuff/base`, `codebuff/reviewer`, `codebuff/thinker`, `codebuff/researcher`,
`codebuff/planner`, `codebuff/file-picker` (reference with `@version`, e.g. `codebuff/reviewer@0.0.1`).

### 2.4 Project Rules — `AGENTS.md` / `CLAUDE.md`

Freebuff reads project rules files natively (like OpenCode's `AGENTS.md` instructions contract). The
Cognitive Lead AI HQ `AGENTS.md` at the repo root is therefore honored automatically by Freebuff in projects
that clone this repository. OpenCode-specific shell policy (`docs/opencode-shell-strategy.md`) is **N/A**
for Freebuff; the equivalent Git/ZAC rules live in `AGENTS.md`.

---

## 3. What Was Ported (2026-08-12)

All ported components were installed globally under `~/.agents/` and verified live.

| #   | Component                                                       | Install location     | Status                     |
| --- | --------------------------------------------------------------- | -------------------- | -------------------------- |
| 1   | **MCP servers** (`custom_context`, `project_memory`, `lint`)    | `~/.agents/mcp.json` | ✅ FULL                    |
| 2   | **Agent Skills** (all 29 from `skill-templates/`)               | `~/.agents/skills/`  | ✅ FULL                    |
| 3   | **Custom agents** (`cognitive-executor`, `cognitive-discovery`) | `~/.agents/*.ts`     | ⚠️ INSTALLED-ONLY          |
| 4   | `system-prompt.md` (Orchestrator Brain)                         | — (manual)           | 📄 MANUAL                  |
| 5   | `user-prompts/` templates                                       | — (manual)           | 📄 MANUAL                  |
| 6   | `docs/opencode-shell-strategy.md`                               | —                    | ➖ N/A (OpenCode-specific) |

### 3.1 MCP servers (`~/.agents/mcp.json`) — ✅ FULL

All three Python MCP servers from this repo were wired into Freebuff's global `mcp.json` with **absolute
paths** (matching the OpenCode global install under `~/.config/opencode/`):

| Server           | Command                                                               | Tools |
| ---------------- | --------------------------------------------------------------------- | ----- |
| `custom_context` | `uv run /home/mohammad/.config/opencode/mcp-context-server/server.py` | 6     |
| `project_memory` | `uv run /home/mohammad/.config/opencode/mcp-memory-server/server.py`  | 5     |
| `lint`           | `uv run /home/mohammad/.config/opencode/mcp-lint-server/server.py`    | 3     |

E2E verified via an MCP stdio client (`initialize` + `tools/list` → **14 tools reachable**). In-session
proof: `get_directory_tree`, `list_namespaces`, `lint_all_tasks`, `read_memory`, `lint_markdown` all answered.

### 3.2 Skills (`~/.agents/skills/`) — ✅ FULL

All 29 `skill-templates/*` were copied byte-identical. Validation: 29/29 kebab-case directory names,
29/29 `SKILL.md` present, 29/29 `name` + `description` frontmatter. In-session proof: `task-generator`,
`code-search`, `project-memory`, `python-fastapi`, `task-lint` all load via the `skill` tool.

### 3.3 Custom agents (`~/.agents/*.ts`) — ⚠️ INSTALLED-ONLY

Two TypeScript ports of the OpenCode agents were authored:

- `~/.agents/cognitive-executor.ts` — the primary executor (20-tool whitelist, 10 spawnable agents incl.
  `cognitive-discovery`, file-picker, code-searcher, basher, researchers, reviewer). OpenCode
  `mode/permission/temperature` frontmatter → Freebuff `toolNames` whitelist; OpenCode `task`-tool
  subagents → Freebuff `spawn_agents`; **ZAC + Kanban + skill matrix + memory protocol preserved in
  `systemPrompt`**.
- `~/.agents/cognitive-discovery.ts` — read-only subagent (8 tools: read-only discovery + `set_output`;
  no bash/write/git).

Both parse and import cleanly (Node 24 type-stripping) and the platform **recognizes** them, but execution
is blocked by the **free tier**: see §5.

---

## 4. Freebuff Support Matrix (Partial)

| Component                                                   | Freebuff status   | Notes                                                                                                       |
| ----------------------------------------------------------- | ----------------- | ----------------------------------------------------------------------------------------------------------- |
| MCP servers (`custom_context`, `project_memory`, `lint`)    | ✅ FULL           | Verified live, 14 tools                                                                                     |
| Skills (29)                                                 | ✅ FULL           | Verified loading via `skill` tool                                                                           |
| Custom agents (`cognitive-executor`, `cognitive-discovery`) | ⚠️ INSTALLED-ONLY | Recognized; blocked on free tier (HTTP 403)                                                                 |
| `system-prompt.md` (Orchestrator Brain)                     | 📄 MANUAL         | Chat document — paste into Freebuff like any Orchestrator session                                           |
| `user-prompts/` templates                                   | 📄 MANUAL         | Copy-paste templates, work in any chat                                                                      |
| `opencode-shell-strategy.md`                                | ➖ N/A            | OpenCode-specific; Git/ZAC rules live in `AGENTS.md` (Freebuff reads `AGENTS.md`/`CLAUDE.md` automatically) |

---

## 5. Free-Tier Limitation (Custom Agents)

Custom agents are **recognized but not executable on the free tier**. A spawn attempt resolves the agent
(downloaded/parsed) and then the runtime returns:

```text
HTTP 403  free_mode_invalid_agent_model
"Free mode is only available for specific agent and model combinations"
```

**What this means:** Free mode permits only the built-in `base-*` agents with specific model combinations.
Custom `.agents/*.ts` agents (including the `cognitive-executor` / `cognitive-discovery` ports) require a
credits/paid mode. If you run Freebuff on a paid/credits tier, the custom agents should become spawnable;
the `.ts` ports in `~/.agents/` are already in place.

---

## 6. Running the Cognitive Lead Workflow on Freebuff

Freebuff gives you the **tooling layer** (MCP + Skills) but not the **orchestrated agent layer** on the free
tier. Here is how to get the most from it while keeping OpenCode as the primary runtime:

1. **Orchestrator Brain (manual):** paste `system-prompt.md` into a Freebuff chat exactly as you would into
   OpenCode. The Orchestrator still emits `<opencode_*>_task>` blocks **targeting OpenCode** — execute those
   in OpenCode. This is by design: the task pipeline is OpenCode-first.
2. **Tooling (automatic):** with `~/.agents/mcp.json` + `~/.agents/skills/` installed, Freebuff gains the
   context/MCP, project-memory, and lint servers plus the 29 skills in any repository.
3. **User prompts (manual):** `user-prompts/*.md` are runtime-agnostic copy-paste templates; use them in any
   Freebuff chat.
4. **Custom agents (paid tier only):** on a credits plan, `@cognitive-executor` and `@cognitive-discovery`
   should become spawnable per §5.

---

## 7. Verifying the Port

Run these to confirm the components are live:

```bash
# 1. Freebuff CLI present
~/.config/manicode/freebuff --version          # → 0.0.146 (2026-08-12)

# 2. Global install exists
ls ~/.agents/mcp.json ~/.agents/skills ~/.agents/*.ts

# 3. Skills valid (29/29 kebab-case + frontmatter)
ls ~/.agents/skills/ | wc -l                    # → 29

# 4. MCP servers reachable — verified via MCP stdio client:
#    `initialize` + `tools/list` → 14 tools reachable across the 3 servers.
#    In-session probes answered: `get_directory_tree`, `list_namespaces`,
#    `lint_all_tasks`, `read_memory`, `lint_markdown`.

# 5. Repo test suite (OpenCode side, servers healthy)
uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q   # → 14 passed
```

Reference links (for staying current as Freebuff/Codebuff evolves):

- [freebuff.com](https://freebuff.com)
- [Agent Reference](https://www.codebuff.com/docs/agents/agent-reference)
- [Creating New Agents](https://www.codebuff.com/docs/agents/creating-new-agents)
- [MCP Servers](https://www.codebuff.com/docs/tips/mcp-servers)
- [Skills](https://www.codebuff.com/docs/tips/skills)

---

## 8. Stability & Drift Notes

- Version pinned to **Freebuff CLI 0.0.146** and **Codebuff docs as of 2026-08-12** — re-verify against the
  official docs above when Freebuff/Codebuff evolves.
- The global `~/.agents/` install is **machine-local** and not tracked by this repo; treat it as an
  install artifact derived from the repo (`skill-templates/`, `mcp-*-server/`, `agents/`).
- This document, the README section, and the `LLM.txt` optional step are the durable record; see
  Task 96 for the full audit performed 2026-08-12.
