# Freebuff Support

> **Dual-runtime support.** The Cognitive Lead AI workflow now runs on **both** OpenCode and **Freebuff**
> (`freebuff.com`, vendor: manicode — formerly Codebuff-based). Since v8.4.5 the system prompt
> (`system-prompt.md`) is **runtime-agnostic**: it addresses "the Hands" (the local execution agent) and
> emits `<hands_*_task>` blocks that work in either runtime, so Freebuff is no longer a partial target.
>
> - **Last verified:** 2026-08-13 (Freebuff CLI `0.0.149`)
> - **Source of truth:** Task 96 (port audit) and Task 98 (full-support completion) — reference by ID, not path.
> - **Overall status:** ✅ FULL (REPO-LEVEL) — MCP servers, Skills, global rules, and custom agents are all
>   in place and schema-validated; the live free-tier spawn remains a **manual verification item** pending
>   Manager confirmation (see §5).

---

## 1. What Freebuff Is

Freebuff (`freebuff.com`, vendor: **manicode** — formerly Codebuff-based) is a **terminal AI coding agent**:

| Fact            | Value                         |
| --------------- | ----------------------------- |
| **Binary**      | `~/.config/manicode/freebuff` |
| **Version**     | `0.0.149`                     |
| **Platform**    | Linux x64                     |
| **Config root** | `~/.config/manicode/`         |

**Key fact for this guide:** Freebuff does **not** read `opencode.json`, `AGENTS.md` agent definitions, or the
OpenCode skill registry. It has its own extension points (see §2) rooted at `.agents/` folders.

---

## 2. Freebuff Extension Points (Discovered via Binary Analysis)

Extension points were discovered via binary analysis on 2026-08-12 and confirmed in-session for MCP servers,
Skills, custom agents, and rules.

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
- `model` (upstream Agent Reference marks it **required**, but it is effectively **optional** in the
  Freebuff free-tier runtime — omitting it falls back to the platform/free-mode default model, and
  pinning a model triggers `HTTP 403 free_mode_invalid_agent_model`; see §5)
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

### 2.4 Project Rules — `AGENTS.md` / `CLAUDE.md` / `knowledge.md`

Freebuff reads project rules files natively. Per directory it checks, in order: **`knowledge.md`**,
**`AGENTS.md`**, **`CLAUDE.md`** (case-insensitive, one file per directory). The Cognitive Lead AI HQ
`AGENTS.md` at the repo root is therefore honored automatically in any project that clones this repository.
OpenCode-specific shell policy (`docs/opencode-shell-strategy.md`) is **N/A** for Freebuff; the equivalent
Git/ZAC rules live in `AGENTS.md` and the global rules file below.

### 2.5 Global Rules — `~/.AGENTS.md` (The Hands)

Freebuff loads home-directory instruction files globally, making rules apply to **every** project session:

| File              | Precedence  | Notes                                                                          |
| ----------------- | ----------- | ------------------------------------------------------------------------------ |
| `~/.knowledge.md` | 1 (highest) | Freebuff/Codebuff native                                                       |
| `~/.AGENTS.md`    | 2           | **Installed by this project** — vendor-agnostic `AGENTS.md` ecosystem standard |
| `~/.CLAUDE.md`    | 3           | Claude Code compatibility                                                      |

The Cognitive Lead HQ installs its global rules as **`~/.AGENTS.md`** (versioned source:
`freebuff/AGENTS.global.md`). It carries the baseline constraints for every session: AGENTS.md-first,
Input Validation Pipeline, English-only reasoning, ZAC, verification-before-completion, decentralized
task files, MCP/skill usage, and changelog discipline.

---

## 3. What Was Ported (2026-08-12, completed 2026-08-13)

All ported components are installed globally under `~/.agents/` (plus `~/.AGENTS.md`). MCP servers, Skills, and
global rules are **verified live**; the custom agents are **✅ FULL (REPO-LEVEL)** — schema-validated in-repo
(v1.2.0) with the **live free-tier spawn still pending** Manager confirmation (see §5).

| #   | Component                                                       | Install location     | Status                       |
| --- | --------------------------------------------------------------- | -------------------- | ---------------------------- |
| 1   | **MCP servers** (`custom_context`, `project_memory`, `lint`)    | `~/.agents/mcp.json` | ✅ FULL                      |
| 2   | **Agent Skills** (all 29 from `skill-templates/`)               | `~/.agents/skills/`  | ✅ FULL                      |
| 3   | **Custom agents** (`cognitive-executor`, `cognitive-discovery`) | `~/.agents/*.ts`     | ✅ FULL (REPO-LEVEL) — schema-validated v1.2.0; free-tier spawn pending |
| 4   | **Global rules** ("The Hands")                                  | `~/.AGENTS.md`       | ✅ FULL                      |
| 5   | `system-prompt.md` (Orchestrator Brain)                         | — (manual)           | 📄 MANUAL — runtime-agnostic |
| 6   | `user-prompts/` templates                                       | — (manual)           | 📄 MANUAL                    |
| 7   | `docs/opencode-shell-strategy.md`                               | —                    | ➖ N/A (OpenCode-specific)   |

### 3.1 MCP servers (`~/.agents/mcp.json`) — ✅ FULL

All three Python MCP servers from this repo are wired into Freebuff's global `mcp.json` with **absolute
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

### 3.3 Custom agents (`~/.agents/*.ts`) — ✅ FULL (REPO-LEVEL, schema-validated v1.2.0)

Two TypeScript ports of the OpenCode agents are authored **in-repo** at `freebuff/agents/*.ts` and
installed to `~/.agents/`:

- `~/.agents/cognitive-executor.ts` — the primary executor (**11-tool whitelist**, 4 spawnable agents:
  local `cognitive-discovery` + built-ins `codebuff/file-picker@0.0.1`, `codebuff/researcher@0.0.1`,
  `codebuff/reviewer@0.0.1`). OpenCode `mode/permission/temperature` frontmatter → Freebuff `toolNames`
  whitelist; OpenCode `task`-tool subagents → Freebuff `spawn_agents`; **ZAC + Kanban + skill matrix +
  memory protocol preserved in `systemPrompt`**; handles the runtime-agnostic `<hands_*_task>` blocks.
- `~/.agents/cognitive-discovery.ts` — read-only subagent (**4 tools**: `read_files`, `code_search`,
  `find_files`, `set_output`; no bash/write/git).

**v1.1.0 free-tier fix:** the `model` field was **removed** from both definitions. Pinning
`deepseek/deepseek-v4-flash` made the free tier reject the spawn with `HTTP 403
free_mode_invalid_agent_model`; omitting `model` lets the runtime fall back to its free-mode default
model. Both parse cleanly (Node 24 type-stripping) and the platform recognizes them.

**v1.2.0 schema validation (QA pass, 2026-08-13):** `toolNames` were cross-checked against the Codebuff
Agent Reference 17-tool platform whitelist — every non-platform entry (`apply_patch`, `list_directory`,
`glob`, `read_subtree`, `read_url`, `skill`, `ask_user`, `suggest_followups`, `lookup_agent_info`) was
removed, and `spawnableAgents` now uses `publisher/name@version` for built-ins (bare ids only for local
`.agents/` agents). Directory mapping remains covered by the `custom_context` MCP tools (auto-available to
all base agents, no whitelisting needed); skills load via `/skill:<name>` slash commands.

---

## 4. Freebuff Support Matrix

| Component                                                   | Freebuff status | Notes                                                                                   |
| ----------------------------------------------------------- | --------------- | --------------------------------------------------------------------------------------- |
| MCP servers (`custom_context`, `project_memory`, `lint`)    | ✅ FULL         | Verified live, 14 tools                                                                 |
| Skills (29)                                                 | ✅ FULL         | Verified loading via `skill` tool                                                       |
| Custom agents (`cognitive-executor`, `cognitive-discovery`) | ✅ FULL (REPO-LEVEL) | Schema-validated v1.2.0 (11/4 tool whitelists, `publisher/name@version` spawnables); `model` omitted — live free-tier spawn pending (§5 caveat) |
| Global rules (`~/.AGENTS.md`)                               | ✅ FULL         | Baseline constraints in every Freebuff session; source: `freebuff/AGENTS.global.md`     |
| `system-prompt.md` (Orchestrator Brain)                     | 📄 MANUAL       | Runtime-agnostic since v8.4.5 — emits `<hands_*_task>`; paste into Freebuff or OpenCode |
| `user-prompts/` templates                                   | 📄 MANUAL       | Copy-paste templates, work in any chat                                                  |
| `opencode-shell-strategy.md`                                | ➖ N/A          | OpenCode-specific; Git/ZAC rules live in `AGENTS.md` + `~/.AGENTS.md`                   |

---

## 5. Free-Tier Note (Custom Agents — Resolved v1.1.0)

Task 96 observed that a spawn attempt resolved the agent and then the runtime returned:

```text
HTTP 403  free_mode_invalid_agent_model
"Free mode is only available for specific agent and model combinations"
```

**Root cause + fix:** the port pinned an explicit `model` (`deepseek/deepseek-v4-flash`). Free mode only
permits the platform's default free-mode model combinations, so any pinned model was rejected. Removing
the `model` field (v1.1.0) lets the runtime fall back to the free-mode default. **Caveat:** if Freebuff
additionally restricts _custom agents themselves_ (not just models) on the free tier, a credits/paid
tier may still be required — the `~/.agents/*.ts` ports are already correct either way, and `@cognitive-executor`
/ `@cognitive-discovery` should be tried on the current free tier to confirm.

**Status note (v1.2.0):** as of the QA adversarial pass the repo-level port is **✅ FULL (REPO-LEVEL)** —
the schema is verified against the live Codebuff docs and the model-free fix is in place, but the live
free-tier spawn could not be executed from the CI-like environment. It is a **manual verification item**
until the Manager starts Freebuff and confirms `@Cognitive Executor <prompt>` spawns without HTTP 403.

---

## 6. Running the Cognitive Lead Workflow on Freebuff

Since v8.4.5 the workflow is runtime-agnostic — the same task blocks run in Freebuff or OpenCode:

1. **Orchestrator Brain (manual):** paste `system-prompt.md` into a Freebuff chat exactly as you would into
   OpenCode. The Orchestrator emits `<hands_*_task>` blocks addressed to "the Hands" — paste them into
   Freebuff (`@cognitive-executor <task>` or just paste the XML block into the base chat).
2. **Rules (automatic):** `~/.AGENTS.md` applies the baseline constraints in every session; the repo root
   `AGENTS.md` applies inside HQ clones.
3. **Tooling (automatic):** with `~/.agents/mcp.json` + `~/.agents/skills/` installed, Freebuff gains the
   context/MCP, project-memory, and lint servers plus the 29 skills in any repository.
4. **Custom agents (free tier, REPO-LEVEL):** `@cognitive-executor` and `@cognitive-discovery` are
   installed, schema-validated (v1.2.0), and model-free; spawn them per §5 — the live spawn is the
   pending manual verification item.
5. **User prompts (manual):** `user-prompts/*.md` are runtime-agnostic copy-paste templates; use them in any
   Freebuff chat.

---

## 7. Verifying the Port

Run these to confirm the components are live:

```bash
# 1. Freebuff CLI present
~/.config/manicode/freebuff --version          # → 0.0.149 (2026-08-13)

# 2. Global install exists
ls ~/.agents/mcp.json ~/.agents/skills ~/.agents/*.ts ~/.AGENTS.md

# 3. Skills valid (29/29 kebab-case + frontmatter)
ls ~/.agents/skills/ | wc -l                    # → 29

# 4. Custom agents are model-free (no pinned model → free-tier default)
grep -c "model:" ~/.agents/cognitive-executor.ts ~/.agents/cognitive-discovery.ts   # → 0 (comments only)

# 5. MCP servers reachable — verified via MCP stdio client:
#    `initialize` + `tools/list` → 14 tools reachable across the 3 servers.
#    In-session probes answered: `get_directory_tree`, `list_namespaces`,
#    `lint_all_tasks`, `read_memory`, `lint_markdown`.

# 6. Spawn smoke test (MANUAL, pending): start Freebuff and run `@Cognitive Executor <any prompt>`
#    — v1.2.0 is schema-validated and model-free; confirm no HTTP 403. Until the Manager
#    confirms this, the repo-level status is ✅ FULL (REPO-LEVEL), not verified-live FULL.

# 7. Repo test suite (servers healthy)
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

- Version pinned to **Freebuff CLI 0.0.149** and **Codebuff docs as of 2026-08-13** — re-verify against the
  official docs above when Freebuff/Codebuff evolves.
- The global `~/.agents/` install and `~/.AGENTS.md` are **machine-local** and not tracked by this repo; the
  durable sources are the repo artifacts: `freebuff/agents/*.ts`, `freebuff/AGENTS.global.md`,
  `skill-templates/`, `mcp-*-server/`, and `agents/`. Reinstall via `LLM.txt` Step 7.5.
- The system prompt (`system-prompt.md` ≥ v8.4.5) is runtime-agnostic; OpenCode-specific docs
  (`docs/opencode-architecture-reference.md`, `docs/opencode-shell-strategy.md`, `docs/opencode-schema.json`)
  remain OpenCode references and are N/A to Freebuff.
- The agent ports are at **v1.2.0** (schema-validated 2026-08-13); the installed `~/.agents/*.ts` copies
  must be re-synced from `freebuff/agents/*.ts` via `LLM.txt` Step 7.5 after any port change.
- This document, the README section, and the `LLM.txt` optional step are the durable record; see
  Tasks 96 and 98 for the full audit performed 2026-08-12/13.
