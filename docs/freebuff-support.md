# Freebuff Support

> **Dual-runtime support.** The Cognitive Lead AI workflow now runs on **both** OpenCode and **Freebuff**
> (`freebuff.com`, vendor: manicode — formerly Codebuff-based). Since v8.4.5 the system prompt
> (`system-prompt.md`) is **runtime-agnostic**: it addresses "the Hands" (the local execution agent) and
> emits `<hands_*_task>` blocks that work in either runtime, so Freebuff is no longer a partial target.
>
> - **Last verified:** 2026-08-13 (Freebuff CLI `0.0.149`)
> - **Source of truth:** Task 96 (port audit) and Task 98 (full-support completion) — reference by ID, not path.
> - **Overall status:** ✅ FULL (REPO-LEVEL) — MCP servers, Skills, global rules, and custom agents are all
>   in place and schema-validated. **Verified 2026-08-13 (binary analysis + live session):** the free tier
>   CANNOT spawn the custom local agents (paid/credits tier required); the free tier CAN spawn Freebuff's
>   built-in subagents when running as a `base2-free-*` "Free Orchestrator" agent (see §5).

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
global rules are **verified live**; the custom agents are **✅ FULL (REPO-LEVEL, schema-validated v1.2.0)** but
**NOT spawnable on the free tier** — verified 2026-08-13 via binary analysis + a live `@Cognitive Executor`
session (see §5).

| #   | Component                                                       | Install location     | Status                                                                                                           |
| --- | --------------------------------------------------------------- | -------------------- | ---------------------------------------------------------------------------------------------------------------- |
| 1   | **MCP servers** (`custom_context`, `project_memory`, `lint`, `blowsh`, `telegram`) | `~/.agents/mcp.json` | ✅ FULL — 5 servers (core 3 + blowsh Docker + telegram Telethon) |
| 2   | **Agent Skills** (all 30 from `skill-templates/`)               | `~/.agents/skills/`  | ✅ FULL                                                                                                          |
| 3   | **Custom agents** (`cognitive-executor`, `cognitive-discovery`) | `~/.agents/*.ts`     | ✅ FULL (REPO-LEVEL) — schema-validated v1.2.0; ❌ not spawnable on the free tier (paid tier required, verified) |
| 4   | **Global rules** ("The Hands")                                  | `~/.AGENTS.md`       | ✅ FULL                                                                                                          |
| 5   | `system-prompt.md` (Orchestrator Brain)                         | — (manual)           | 📄 MANUAL — runtime-agnostic                                                                                     |
| 6   | `user-prompts/` templates                                       | — (manual)           | 📄 MANUAL                                                                                                        |
| 7   | `docs/opencode-shell-strategy.md`                               | —                    | ➖ N/A (OpenCode-specific)                                                                                       |

### 3.1 MCP servers (`~/.agents/mcp.json`) — ✅ FULL

All five MCP servers from this HQ are wired into Freebuff's global `mcp.json` with **absolute
paths** (matching the OpenCode global install under `~/.config/opencode/`; blowsh is Docker, telegram reuses the Telethon checkout):

| Server           | Command                                                                       | Tools | Notes |
| ---------------- | ----------------------------------------------------------------------------- | ----- | ----- |
| `custom_context` | `uv run $HOME/.config/opencode/mcp-context-server/server.py`                  | 6     | Core — tree + file reads + bundle_tasks (absolute path, replace `$HOME` per LLM.txt Step 3) |
| `project_memory` | `uv run $HOME/.config/opencode/mcp-memory-server/server.py`                   | 5     | Core — persistent memory (absolute path) |
| `lint`           | `uv run $HOME/.config/opencode/mcp-lint-server/server.py`                     | 3     | Core — lint (absolute path) |
| `blowsh`         | `docker run --rm -i ghcr.io/mokhtarabadi/blowsh-mcp:latest`                    | 4     | Optional — JS browsing, retired browser MCP replacement (SSRF guard, cache, timeout 120s) — Docker, no host dir |
| `telegram`       | `uv --directory $HOME/.config/opencode/mcp-telegram-server run main.py /tmp/telegram-mcp $HOME/.config/opencode/mcp-telegram-server/downloads` | 80+   | Optional — Telethon; work/personal `account` routing, allowed roots (`/tmp` + config dir), see `docs/telegram-setup.md` |

E2E verified (core 3) via an MCP stdio client (`initialize` + `tools/list` → **14 tools reachable** for core). Blowsh verified via `docker pull` + container stdin wait; telegram verified via `telegram_get_messages` when `TELEGRAM_SESSION_STRING` present (and via `uv run session_string_generator.py --help` otherwise). In-session proof: `get_directory_tree`, `list_namespaces`, `lint_all_tasks`, `read_memory`, `lint_markdown` all answered; telegram proof documented in `docs/telegram-setup.md` §6 and `workflows/telegram-file-delivery` memory.

### 3.2 Skills (`~/.agents/skills/`) — ✅ FULL

All 30 `skill-templates/*` were copied byte-identical (30 since Task 110 bundle-tasks). Validation: 30/30 kebab-case directory names,
30/30 `SKILL.md` present, 30/30 `name` + `description` frontmatter. In-session proof: `task-generator`,
`code-search`, `project-memory`, `python-fastapi`, `task-lint` all load via the `skill` tool; telegram skills `telegram-issue-sync` / `telegram-message-export` consume the `telegram` MCP when `docs/telegram-setup.md` account is set.

### 3.3 Custom agents (`~/.agents/*.ts`) — ✅ FULL (REPO-LEVEL, schema-validated v1.2.0) / ❌ free-tier spawn blocked

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

**2026-08-13 live verification (free-tier spawn BLOCKED — binary analysis + session log):** the free tier
cannot spawn the custom local agents. Evidence from the Freebuff CLI `0.0.149` binary and a live
`@Cognitive Executor say hello` session (`~/.config/manicode/projects/.../log.jsonl`):

- The **default free agent** (`base3-free-deepseek-flash`, "Buffy on DeepSeek Flash") has **NO `spawn_agents`
  tool** in its whitelist at all. The mention fell through as plain text — the run used `agentTemplateId:
base3-free-deepseek-flash` with the full prompt as literal input and no `spawn_agents` call.
- The **free-tier orchestrators** (`base2-free-*`, "Buffy the Free Orchestrator") DO ship `spawn_agents`, but
  their `spawnableAgents` whitelists contain **only built-in Codebuff subagents** (`file-picker`,
  `code-searcher`, `researcher-web`, `researcher-docs`, `basher`, `tmux-cli`, `browser-use`,
  `code-reviewer-*`, `context-pruner`). The client-side spawn validation (`qIH(I.spawnableAgents, o)`)
  rejects any target outside that list with `Agent "<id>" is not available to spawn`, so
  `cognitive-executor`/`cognitive-discovery` are rejected even though `g0()` resolves them from
  `~/.agents/` (discovery order: `{cwd}/.agents` → `{cwd}/../.agents` → `~/.agents`).
- **Bottom line:** custom `.agents/*.ts` agents require a **credits/paid tier** on Freebuff. The free tier
  can only spawn Freebuff's built-in subagents, and only when the session runs as a `base2-free-*`
  "Free Orchestrator" agent (switch via the model/agent selector — `settings.json` currently pins
  `deepseek/deepseek-v4-flash`, which maps to the non-spawning `base3-free-deepseek-flash`).

---

## 4. Freebuff Support Matrix

| Component                                                                        | Freebuff status      | Notes                                                                                                                                                                                                                                                                             |
| -------------------------------------------------------------------------------- | -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MCP servers (`custom_context`, `project_memory`, `lint`, `blowsh`, `telegram`)   | ✅ FULL              | Verified live, core 14 + blowsh (4, Docker) + telegram (80+, Telethon)                                                                                                                                                                                                           |
| Skills (30)                                                                      | ✅ FULL              | Verified loading via `skill` tool (30 since Task 110)                                                                                                                                                                                                                            |
| Custom agents (`cognitive-executor`, `cognitive-discovery`) | ✅ FULL (REPO-LEVEL) | Schema-validated v1.2.0 (11/4 tool whitelists, `publisher/name@version` spawnables); `model` omitted — ❌ NOT spawnable on the free tier (verified 2026-08-13); paid/credits tier required. Free tier can spawn Freebuff built-in subagents only via `base2-free-*` orchestrators |
| Global rules (`~/.AGENTS.md`)                               | ✅ FULL              | Baseline constraints in every Freebuff session; source: `freebuff/AGENTS.global.md`                                                                                                                                                                                               |
| `system-prompt.md` (Orchestrator Brain)                     | 📄 MANUAL            | Runtime-agnostic since v8.4.5 — emits `<hands_*_task>`; paste into Freebuff or OpenCode                                                                                                                                                                                           |
| `user-prompts/` templates                                   | 📄 MANUAL            | Copy-paste templates, work in any chat                                                                                                                                                                                                                                            |
| `opencode-shell-strategy.md`                                | ➖ N/A               | OpenCode-specific; Git/ZAC rules live in `AGENTS.md` + `~/.AGENTS.md`                                                                                                                                                                                                             |

---

## 5. Free-Tier Note (Custom Agents — VERIFIED: not spawnable on the free tier)

**History:** Task 96 observed the original ports (with a pinned `model`) return `HTTP 403
free_mode_invalid_agent_model` on the free tier. v1.1.0 removed the `model` field and v1.2.0
schema-validated the ports — but **live verification on 2026-08-13 proved the model fix was necessary but
NOT sufficient**: the free tier cannot spawn custom local agents regardless of the `model` field.

**Verified evidence (Freebuff CLI `0.0.149` binary + live session):**

1. The **default free agent** (`base3-free-deepseek-flash`, "Buffy on DeepSeek Flash") has **NO `spawn_agents`
   tool** in its whitelist. `@Cognitive Executor say hello` was recorded in the session log as a plain prompt
   run by `base3-free-deepseek-flash` — no spawn, no 403, the mention was simply treated as text.
2. The **free-tier orchestrator** (`base2-free-*`, "Buffy the Free Orchestrator") has `spawn_agents`, but its
   `spawnableAgents` list contains **only built-in Codebuff subagents**. The client-side validation
   (`qIH(I.spawnableAgents, o)`) rejects anything else with `Agent "..." is not available to spawn`, so local
   custom agents (`cognitive-executor`, `cognitive-discovery`) are rejected before any backend call.
3. Local agents ARE discovered (order: `{cwd}/.agents` → `{cwd}/../.agents` → `~/.agents`) and resolved by
   `g0()` — but the whitelist gate above blocks them on the free tier.

**Conclusion:** custom `.agents/*.ts` agents require a **credits/paid tier**. The repo-level ports remain
**✅ FULL (REPO-LEVEL)** — correct, schema-valid, and ready — but on the free tier you must either (a) run
the Cognitive Lead workflow through the base chat (paste `<hands_*_task>` blocks directly; the base agent has
all MCP tools + skills + `~/.AGENTS.md` loaded), or (b) use a paid/credits tier to spawn `@cognitive-executor`.
As a bonus, the free tier CAN spawn Freebuff's built-in subagents (researcher-web, code-searcher, basher,
browser-use, file-picker, code-reviewer, ...) if you switch the free model to a `base2-free-*`
"Free Orchestrator" agent.

---

## 6. Running the Cognitive Lead Workflow on Freebuff

Since v8.4.5 the workflow is runtime-agnostic — the same task blocks run in Freebuff or OpenCode:

1. **Orchestrator Brain (manual):** paste `system-prompt.md` into a Freebuff chat exactly as you would into
   OpenCode. The Orchestrator emits `<hands_*_task>` blocks addressed to "the Hands" — paste them into
   Freebuff (`@cognitive-executor <task>` or just paste the XML block into the base chat).
2. **Rules (automatic):** `~/.AGENTS.md` applies the baseline constraints in every session; the repo root
   `AGENTS.md` applies inside HQ clones.
3. **Tooling (automatic):** with `~/.agents/mcp.json` + `~/.agents/skills/` installed, Freebuff gains the
   context/MCP, project-memory, lint, blowsh (Docker) and telegram (Telethon) servers plus the 30 skills in any repository (30 since Task 110).
4. **Custom agents (REPO-LEVEL, paid tier):** `@cognitive-executor` and `@cognitive-discovery` are installed,
   schema-validated (v1.2.0), and model-free — but the **free tier cannot spawn them** (verified 2026-08-13,
   §5). On the free tier, either paste `<hands_*_task>` blocks into the base chat (which has all MCP tools +
   skills + `~/.AGENTS.md` loaded), or switch the free model to a `base2-free-*` "Free Orchestrator" agent to
   spawn Freebuff's built-in subagents. Use the custom agents on a credits/paid tier.
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

# 3. Skills valid (30/30 kebab-case + frontmatter)
ls ~/.agents/skills/ | wc -l                    # → 30

# 4. Custom agents are model-free (no pinned model → free-tier default)
grep -c "model:" ~/.agents/cognitive-executor.ts ~/.agents/cognitive-discovery.ts   # → 0 (comments only)

# 5. MCP servers reachable — verified via MCP stdio client:
#    `initialize` + `tools/list` → 14 tools (core 3) + blowsh (4) + telegram (80+) reachable.
#    Core probes answered: `get_directory_tree`, `list_namespaces`,
#    `lint_all_tasks`, `read_memory`, `lint_markdown`; telegram probe: `list_accounts` when creds present.

# 6. Spawn smoke test — DONE 2026-08-13 (free tier): `@Cognitive Executor say hello` ran as
#    `base3-free-deepseek-flash` with the mention as plain text (no spawn, no 403) — the free tier
#    lacks `spawn_agents` (base3-free) / whitelists only built-in subagents (base2-free). Custom
#    local agents are paid-tier only; Freebuff built-in subagents spawn via `base2-free-*`.
#    See §5 for the full verified evidence.

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
- **Free-tier custom-agent spawn is VERIFIED BLOCKED (2026-08-13)** — the earlier "manual verification item"
  status is closed: the free tier cannot spawn custom local agents (see §5). Re-verify only if Freebuff
  changes its free-tier agent policy.
- This document, the README section, and the `LLM.txt` optional step are the durable record; see
  Tasks 96 and 98 for the full audit performed 2026-08-12/13.
