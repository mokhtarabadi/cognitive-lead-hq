# Freebuff Support

> **Dual-runtime support.** The Cognitive Lead AI workflow now runs on **both** OpenCode and **Freebuff**
> (`freebuff.com`, vendor: **CodebuffAI** — formerly Codebuff-based; the `~/.config/manicode/` binary
> path is a legacy config-root name, NOT the vendor). Since v8.4.5 the system prompt
> (`system-prompt.md`) is **runtime-agnostic**: it addresses "the Hands" (the local execution agent) and
> emits `<hands_*_task>` blocks that work in either runtime, so Freebuff is no longer a partial target.
>
> - **Last verified:** 2026-08-26 (Freebuff CLI `0.0.156` + source audit of `github.com/CodebuffAI/freebuff`)
> - **Source of truth:** Task 96 (port audit), Task 98 (full-support completion), and the 2026-08-26
>   source audit (free-tier agent policy + roles/knowledge files) — reference by ID, not path.
> - **Overall status:** ✅ FULL (REPO-LEVEL) — MCP servers, Skills, global rules, and custom agents are all
>   in place and schema-validated. **Verified 2026-08-26 against the public source:** the free tier
>   CANNOT spawn the custom local agents (server-side `FREE_MODE_AGENT_MODELS` allowlist + client gates,
>   see §5); the free tier CAN use all MCP tools, skills, and the always-loaded knowledge files
>   (`~/.AGENTS.md`), which is how the **Cognitive Executive Role** is defined (see §2.6).

---

## 1. What Freebuff Is

Freebuff (`freebuff.com`, vendor: **CodebuffAI** — formerly Codebuff-based; the `~/.config/manicode/`
binary path is a legacy config-root name, not the vendor) is a **terminal AI coding agent**:

| Fact            | Value                                                                                      |
| --------------- | ------------------------------------------------------------------------------------------ |
| **Binary**      | `~/.config/manicode/freebuff`                                                              |
| **Version**     | `0.0.156`                                                                                  |
| **Platform**    | Linux x64                                                                                  |
| **Config root** | `~/.config/manicode/`                                                                      |
| **Source**      | https://github.com/CodebuffAI/freebuff                                                     |
| **Update path** | Re-download from freebuff.com (self-contained binary; no public versioned release channel) |

**Keeping current (verified 2026-08-26):** `0.0.156` is the latest version. The public source snapshot at
`github.com/CodebuffAI/freebuff` was synced from the private build on 2026-08-26 (same day as this
install), and the GitHub Releases page carries only **"Codecane" staging builds** (a different product) —
there is no versioned Freebuff release channel to track. To check for updates:
`~/.config/manicode/freebuff --version` and compare with the newest installer at freebuff.com; re-download
when a newer version is announced.

**Key fact for this guide:** Freebuff does **not** read `opencode.json`, `AGENTS.md` agent definitions, or the
OpenCode skill registry. It has its own extension points (see §2) rooted at `.agents/` folders.

---

## 2. Freebuff Extension Points (Discovered via Binary Analysis)

Extension points were discovered via binary analysis on 2026-08-12, confirmed in-session for MCP servers,
Skills, custom agents, and rules, and **re-verified against the public source on 2026-08-26**.

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
- `model` — upstream Agent Reference marks it **required**, and the **0.0.156 loader enforces it**:
  `sdk/src/agents/load-agents.ts` silently skips any `.agents/*.ts` without a `model` field. Our ports
  omit it (the v1.1.0 fix for 0.0.149, where pinning a model 403'd on the free tier) — so on 0.0.156
  they do not even load, and on a paid tier they need `model` restored (see §5)
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

### 2.4 Project Rules — `AGENTS.md` / `CLAUDE.md` / `*.knowledge.md` (knowledge files)

Freebuff reads project rules files natively — they are **knowledge files** injected into the system
prompt of every session (see §2.6). Per directory it checks, in order: **`AGENTS.md`**, **`CLAUDE.md`**,
plus any **`*.knowledge.md`** files (case-insensitive, one `AGENTS.md`/`CLAUDE.md` per directory). The
bare `knowledge.md` name **left the priority list in 0.0.156** and is ignored (verified against the
source test suite). The Cognitive Lead AI HQ `AGENTS.md` at the repo root is therefore honored
automatically in any project that clones this repository. OpenCode-specific shell policy
(`docs/opencode-shell-strategy.md`) is **N/A** for Freebuff; the equivalent Git/ZAC rules live in
`AGENTS.md` and the global rules file below.

### 2.5 Global Rules — `~/.AGENTS.md` (The Hands)

Freebuff loads home-directory knowledge files globally, making rules apply to **every** project session:

| File           | Precedence  | Notes                                                                          |
| -------------- | ----------- | ------------------------------------------------------------------------------ |
| `~/.AGENTS.md` | 1 (highest) | **Installed by this project** — vendor-agnostic `AGENTS.md` ecosystem standard |
| `~/.CLAUDE.md` | 2           | Claude Code compatibility                                                      |

(`~/.knowledge.md` is **NOT loaded anymore** — it left the knowledge-file priority list in 0.0.156,
verified against the source test suite: _"should ignore `~/.knowledge.md` now that it left the priority
list"_.)

The Cognitive Lead HQ installs its global rules as **`~/.AGENTS.md`** (versioned source:
`freebuff/AGENTS.global.md`). It carries the baseline constraints for every session: AGENTS.md-first,
Input Validation Pipeline, English-only reasoning, ZAC, verification-before-completion, decentralized
task files, MCP/skill usage, changelog discipline — **plus the Cognitive Executive Role** (see §2.6).

### 2.6 Always-Loaded Roles (the sanctioned alternative to custom agents)

Freebuff has **no role/persona feature** (verified in source: "persona" strings are hardcoded display
metadata for built-in agents — `displayName`/`purpose`). There are no role files, no role registry, no
`/role` slash command, and no CLI flag: defining an agent-as-role is **not** a capability. The way to
make an agent always know a role is the **knowledge-file system** — files injected into **every**
agent's system prompt (via the `KNOWLEDGE_FILES_CONTENTS` placeholder), including free-tier sessions,
with no spawn and no paid tier:

| Scope       | Files (priority order)                           | Loaded                      |
| ----------- | ------------------------------------------------ | --------------------------- |
| **Home**    | `~/.AGENTS.md` > `~/.CLAUDE.md`                  | Always, in every session    |
| **Project** | `AGENTS.md` > `CLAUDE.md`, plus `*.knowledge.md` | Auto-injected per directory |

The **Cognitive Executive Role** — distilled from `freebuff/agents/cognitive-executor.ts`
`systemPrompt` (identity & mission, standing duties, hard boundaries) — ships as a `# Cognitive
Executive Role (Always Loaded)` section in `freebuff/AGENTS.global.md` (installed as `~/.AGENTS.md`),
so the base chat always knows the role on any tier. To add more roles: append a
`# <Role> Role (Always Loaded)` section to `freebuff/AGENTS.global.md`, then re-sync via the
`freebuff-documents` skill (see `docs/freebuff-documents.md`).

---

## 3. What Was Ported (2026-08-12, completed 2026-08-13)

All ported components are installed globally under `~/.agents/` (plus `~/.AGENTS.md`). MCP servers, Skills, and
global rules are **verified live**; the custom agents are **✅ FULL (REPO-LEVEL, schema-validated v1.2.0)** but
**NOT spawnable on the free tier** — verified 2026-08-13 via binary analysis + a live `@Cognitive Executor`
session, and confirmed 2026-08-26 against the public source (see §5).

| #   | Component                                                                          | Install location     | Status                                                                                                                         |
| --- | ---------------------------------------------------------------------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| 1   | **MCP servers** (`custom_context`, `project_memory`, `lint`, `blowsh`, `telegram`) | `~/.agents/mcp.json` | ✅ FULL — 5 servers (core 3 + blowsh Docker + telegram Telethon)                                                               |
| 2   | **Agent Skills** (all 31 from `skill-templates/`)                                  | `~/.agents/skills/`  | ✅ FULL                                                                                                                        |
| 3   | **Custom agents** (`cognitive-executor`, `cognitive-discovery`)                    | `~/.agents/*.ts`     | ✅ FULL (REPO-LEVEL) — schema-validated v1.2.0; ❌ not spawnable on the free tier (server-side allowlist, verified 2026-08-26) |
| 4   | **Global rules** ("The Hands" + Cognitive Executive Role)                          | `~/.AGENTS.md`       | ✅ FULL                                                                                                                        |
| 5   | `system-prompt.md` (Orchestrator Brain)                                            | — (manual)           | 📄 MANUAL — runtime-agnostic                                                                                                   |
| 6   | `user-prompts/` templates                                                          | — (manual)           | 📄 MANUAL                                                                                                                      |
| 7   | `docs/opencode-shell-strategy.md`                                                  | —                    | ➖ N/A (OpenCode-specific)                                                                                                     |

### 3.1 MCP servers (`~/.agents/mcp.json`) — ✅ FULL

All five MCP servers from this HQ are wired into Freebuff's global `mcp.json` with **absolute
paths** (matching the OpenCode global install under `~/.config/opencode/`; blowsh is Docker, telegram reuses the Telethon checkout):

| Server           | Command                                                                                                                                        | Tools | Notes                                                                                                                   |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ----- | ----------------------------------------------------------------------------------------------------------------------- |
| `custom_context` | `uv run $HOME/.config/opencode/mcp-context-server/server.py`                                                                                   | 6     | Core — tree + file reads + bundle_tasks (absolute path, replace `$HOME` per LLM.txt Step 3)                             |
| `project_memory` | `uv run $HOME/.config/opencode/mcp-memory-server/server.py`                                                                                    | 5     | Core — persistent memory (absolute path)                                                                                |
| `lint`           | `uv run $HOME/.config/opencode/mcp-lint-server/server.py`                                                                                      | 3     | Core — lint (absolute path)                                                                                             |
| `blowsh`         | `docker run --rm -i ghcr.io/mokhtarabadi/blowsh-mcp:latest`                                                                                    | 4     | Optional — JS browsing, retired browser MCP replacement (SSRF guard, cache, timeout 120s) — Docker, no host dir         |
| `telegram`       | `uv --directory $HOME/.config/opencode/mcp-telegram-server run main.py /tmp/telegram-mcp $HOME/.config/opencode/mcp-telegram-server/downloads` | 80+   | Optional — Telethon; work/personal `account` routing, allowed roots (`/tmp` + config dir), see `docs/telegram-setup.md` |

E2E verified (core 3) via an MCP stdio client (`initialize` + `tools/list` → **16 tools reachable** for
core, re-verified 2026-08-26: context 7 + memory 5 + lint 4). Blowsh verified via `docker pull` +
container stdin wait; telegram verified via `telegram_get_messages` when `TELEGRAM_SESSION_STRING`
present (and via `uv run session_string_generator.py --help` otherwise). In-session proof:
`get_directory_tree`, `list_namespaces`, `lint_all_tasks`, `read_memory`, `lint_markdown` all answered;
telegram proof documented in `docs/telegram-setup.md` §6 and `workflows/telegram-file-delivery` memory.

### 3.2 Skills (`~/.agents/skills/`) — ✅ FULL

All 31 `skill-templates/*` were copied byte-identical (30 since Task 110 bundle-tasks, 31 since
2026-08-26 freebuff-documents). Validation: 31/31 kebab-case directory names,
31/31 `SKILL.md` present, 31/31 `name` + `description` frontmatter. In-session proof: `task-generator`,
`code-search`, `project-memory`, `python-fastapi`, `task-lint` all load via the `skill` tool; telegram skills `telegram-issue-sync` / `telegram-message-export` consume the `telegram` MCP when `docs/telegram-setup.md` account is set; `freebuff-documents` maintains the Freebuff knowledge-document system (see `docs/freebuff-documents.md`).

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

**2026-08-26 source audit (three-layer block, decisive):** re-verified against the public source at
`github.com/CodebuffAI/freebuff` — the block is now **server-side**, not just client-side (see §5 for
the full evidence chain).

---

## 4. Freebuff Support Matrix

| Component                                                                      | Freebuff status      | Notes                                                                                                                                                                                                                                                                                                                                                      |
| ------------------------------------------------------------------------------ | -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MCP servers (`custom_context`, `project_memory`, `lint`, `blowsh`, `telegram`) | ✅ FULL              | Verified live, core 16 + blowsh (4, Docker) + telegram (80+, Telethon)                                                                                                                                                                                                                                                                                     |
| Skills (31)                                                                    | ✅ FULL              | Verified loading via `skill` tool (31 since 2026-08-26)                                                                                                                                                                                                                                                                                                    |
| Custom agents (`cognitive-executor`, `cognitive-discovery`)                    | ✅ FULL (REPO-LEVEL) | Schema-validated v1.2.0 (11/4 tool whitelists, `publisher/name@version` spawnables); `model` omitted — ❌ NOT spawnable on the free tier (server-side `FREE_MODE_AGENT_MODELS` allowlist, verified 2026-08-26); paid/credits tier + restored `model` field required. Free tier can spawn Freebuff built-in subagents only via `base2-free-*` orchestrators |
| Global rules (`~/.AGENTS.md`)                                                  | ✅ FULL              | Baseline constraints + **Cognitive Executive Role** in every Freebuff session; source: `freebuff/AGENTS.global.md`                                                                                                                                                                                                                                         |
| `system-prompt.md` (Orchestrator Brain)                                        | 📄 MANUAL            | Runtime-agnostic since v8.4.5 — emits `<hands_*_task>`; paste into Freebuff or OpenCode                                                                                                                                                                                                                                                                    |
| `user-prompts/` templates                                                      | 📄 MANUAL            | Copy-paste templates, work in any chat                                                                                                                                                                                                                                                                                                                     |
| `opencode-shell-strategy.md`                                                   | ➖ N/A               | OpenCode-specific; Git/ZAC rules live in `AGENTS.md` + `~/.AGENTS.md`                                                                                                                                                                                                                                                                                      |

---

## 5. Free-Tier Note (Custom Agents — VERIFIED: not spawnable on the free tier)

**History:** Task 96 observed the original ports (with a pinned `model`) return `HTTP 403
free_mode_invalid_agent_model` on the free tier. v1.1.0 removed the `model` field and v1.2.0
schema-validated the ports — but live verification on 2026-08-13 proved the model fix was necessary but
NOT sufficient: the free tier cannot spawn custom local agents regardless of the `model` field.

**Verified evidence (2026-08-26 source audit of `github.com/CodebuffAI/freebuff` — the real public
source; `~/.config/manicode/` is a legacy config-root name, the vendor is **CodebuffAI**).** The block
happens at **three independent layers**:

1. **Server-side allowlist (decisive).** `common/src/constants/free-agents.ts` —
   `FREE_MODE_AGENT_MODELS` is a hardcoded agent→model allowlist for 0-credit free mode, with the
   comment _"This prevents abuse by users trying to use arbitrary agents for free."_
   `cognitive-executor` / `cognitive-discovery` are not in it, so any free-mode request on them is
   rejected (`free_mode_invalid_agent_model` — still emitted server-side even though the string is gone
   from the client binary) or metered. `isFreeModeAllowedAgentModel()` also requires publisher =
   `codebuff`, which a user agent can never satisfy.
2. **Client loader regression (0.0.156 vs our fix).** `sdk/src/agents/load-agents.ts` now **requires a
   `model` field**: `if (!agentDefinition?.id || !agentDefinition?.model) continue`. Our ports **omit
   `model`** (the v1.1.0 fix for 0.0.149) — so on 0.0.156 they are **silently skipped at load time**
   (verified the exact string in the installed binary). Restoring `model` makes them load, but then
   layer 1 403s them. The two fixes cancel out.
3. **Client spawn gates (unchanged).** The current CLI harness is **base3**
   (`CLI_HARNESS = 'base3'` in `cli/src/utils/constants.ts` — why every session runs as
   `base3-free-deepseek-flash`), which has **no `spawn_agents` tool at all**. The `base2-free-*`
   orchestrators DO have `spawn_agents`, but whitelist only built-in subagents —
   `validateAndGetAgentTemplate` rejects anything else unless the parent is a legacy base id (`base`,
   `base-free`, `base-max`, `base-experimental`).

**Conclusion:** custom `.agents/*.ts` agents require a **credits/paid tier** — there is no way around
the server-side allowlist. On the free tier you must either (a) run the Cognitive Lead workflow through
the base chat (paste `<hands_*_task>` blocks directly; the base agent has all MCP tools + skills +
`~/.AGENTS.md` loaded, and the **Cognitive Executive Role** is always loaded via the knowledge-file
system — see §2.6), or (b) use a paid/credits tier with a `model` field restored on the ports so the
0.0.156 loader accepts them. As a bonus, the free tier CAN spawn Freebuff's built-in subagents
(researcher-web, code-searcher, basher, browser-use, file-picker, code-reviewer, ...) if you switch the
free model to a `base2-free-*` "Free Orchestrator" agent.

---

## 6. Running the Cognitive Lead Workflow on Freebuff

Since v8.4.5 the workflow is runtime-agnostic — the same task blocks run in Freebuff or OpenCode:

1. **Orchestrator Brain (manual):** paste `system-prompt.md` into a Freebuff chat exactly as you would into
   OpenCode. The Orchestrator emits `<hands_*_task>` blocks addressed to "the Hands" — paste them into
   Freebuff (`@cognitive-executor <task>` or just paste the XML block into the base chat).
2. **Rules (automatic):** `~/.AGENTS.md` applies the baseline constraints + the **Cognitive Executive
   Role** in every session (see §2.6); the repo root `AGENTS.md` applies inside HQ clones.
3. **Tooling (automatic):** with `~/.agents/mcp.json` + `~/.agents/skills/` installed, Freebuff gains the
   context/MCP, project-memory, lint, blowsh (Docker) and telegram (Telethon) servers plus the 31 skills in any repository (31 since 2026-08-26).
4. **Custom agents (REPO-LEVEL, paid tier):** `@cognitive-executor` and `@cognitive-discovery` are installed,
   schema-validated (v1.2.0), and model-free — but the **free tier cannot spawn them** (server-side
   allowlist, verified 2026-08-26, §5). On the free tier, either paste `<hands_*_task>` blocks into the base chat (which has all MCP tools +
   skills + `~/.AGENTS.md` + the Cognitive Executive Role loaded), or switch the free model to a
   `base2-free-*` "Free Orchestrator" agent to spawn Freebuff's built-in subagents. Use the custom
   agents on a credits/paid tier (with a `model` field restored).
5. **User prompts (manual):** `user-prompts/*.md` are runtime-agnostic copy-paste templates; use them in any
   Freebuff chat.

---

## 7. Verifying the Port

Run these to confirm the components are live:

```bash
# 1. Freebuff CLI present
~/.config/manicode/freebuff --version          # → 0.0.156 (2026-08-26)

# 2. Global install exists
ls ~/.agents/mcp.json ~/.agents/skills ~/.agents/*.ts ~/.AGENTS.md

# 3. Skills valid (31/31 kebab-case + frontmatter)
ls ~/.agents/skills/ | wc -l                    # → 31

# 4. Custom agents are model-free (no pinned model → free-tier default)
grep -c "model:" ~/.agents/cognitive-executor.ts ~/.agents/cognitive-discovery.ts   # → 0 (comments only)

# 5. MCP servers reachable — verified via MCP stdio client:
#    `initialize` + `tools/list` → 16 tools (core 3: context 7 + memory 5 + lint 4) + blowsh (4) + telegram (80+) reachable.
#    Core probes answered: `get_directory_tree`, `list_namespaces`,
#    `lint_all_tasks`, `read_memory`, `lint_markdown`; telegram probe: `list_accounts` when creds present.

# 6. Spawn smoke test — DONE 2026-08-13 (free tier): `@Cognitive Executor say hello` ran as
#    `base3-free-deepseek-flash` with the mention as plain text (no spawn, no 403) — the free tier
#    lacks `spawn_agents` (base3-free) / whitelists only built-in subagents (base2-free). Custom
#    local agents are paid-tier only (server-side allowlist, source-verified 2026-08-26).
#    See §5 for the full verified evidence.

# 7. Repo test suite (servers healthy)
uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q   # → 52 passed
```

Reference links (for staying current as Freebuff/Codebuff evolves):

- [freebuff.com](https://freebuff.com)
- [Freebuff source](https://github.com/CodebuffAI/freebuff)
- [Agent Reference](https://www.codebuff.com/docs/agents/agent-reference)
- [Creating New Agents](https://www.codebuff.com/docs/agents/creating-new-agents)
- [MCP Servers](https://www.codebuff.com/docs/tips/mcp-servers)
- [Skills](https://www.codebuff.com/docs/tips/skills)

---

## 8. Stability & Drift Notes

- Version pinned to **Freebuff CLI 0.0.156** and **Codebuff docs + source as of 2026-08-26** —
  re-verify against the official docs/source above when Freebuff/Codebuff evolves.
- The global `~/.agents/` install and `~/.AGENTS.md` are **machine-local** and not tracked by this repo; the
  durable sources are the repo artifacts: `freebuff/agents/*.ts`, `freebuff/AGENTS.global.md`,
  `skill-templates/`, `mcp-*-server/`, and `agents/`. Reinstall via `LLM.txt` Step 7.5.
- The system prompt (`system-prompt.md` ≥ v8.4.5) is runtime-agnostic; OpenCode-specific docs
  (`docs/opencode-architecture-reference.md`, `docs/opencode-shell-strategy.md`, `docs/opencode-schema.json`)
  remain OpenCode references and are N/A to Freebuff.
- The agent ports are at **v1.2.0** (schema-validated 2026-08-13); the installed `~/.agents/*.ts` copies
  must be re-synced from `freebuff/agents/*.ts` via `LLM.txt` Step 7.5 after any port change.
- **Free-tier custom-agent spawn is VERIFIED BLOCKED (2026-08-13 live + 2026-08-26 source)** — the
  server-side `FREE_MODE_AGENT_MODELS` allowlist cannot be bypassed from the client. Re-verify only if
  Freebuff changes its free-tier agent policy.
- **Knowledge files are the roles mechanism** — Freebuff has no role/persona feature; the Cognitive
  Executive Role lives in `freebuff/AGENTS.global.md` → `~/.AGENTS.md` and loads in every session
  (see §2.6 and `docs/freebuff-documents.md`). `~/.knowledge.md` / bare `knowledge.md` are ignored.
- **Keeping Freebuff current:** `0.0.156` is the latest verified version (2026-08-26; public source
  snapshot synced same day, GitHub releases hold only unrelated "Codecane" staging builds). Version
  checks and the global-rules install procedure (`freebuff/AGENTS.global.md` → `~/.AGENTS.md`) are
  codified in `.opencode/memory/workflows/global-install-upgrade.md` and `docs/freebuff-documents.md` §3.
- This document, the README section, and the `LLM.txt` optional step are the durable record; see
  Tasks 96 and 98 plus the 2026-08-26 source audit for the full verification.
