# Cognitive Lead AI HQ

[![Version](https://img.shields.io/github/v/release/mokhtarabadi/cognitive-lead-hq?style=flat-square)](https://github.com/mokhtarabadi/cognitive-lead-hq/releases)
[![License](https://img.shields.io/github/license/mokhtarabadi/cognitive-lead-hq?style=flat-square)](LICENSE)
[![OpenCode](https://img.shields.io/badge/OpenCode-ready-6C47FF?style=flat-square)](https://opencode.ai)
[![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](https://github.com/mokhtarabadi/cognitive-lead-hq/pulls)

The centralized **Headquarters** for the Cognitive Lead AI multi-agent system — a collection of hallucination-resistant system prompts, MCP servers, and strict Agent Skills (SKILL.md) built for [OpenCode](https://opencode.ai).

> **Quick Install:** Copy this line and give it to OpenCode:
>
> ```
> Use webfetch on https://raw.githubusercontent.com/mokhtarabadi/cognitive-lead-hq/main/LLM.txt and follow its instructions to auto-configure everything for me.
> ```

---

## Quick Start

Give the prompt above to OpenCode and it will auto-configure itself globally using [`LLM.txt`](LLM.txt) — the canonical auto-setup source. No manual steps required.

For full platform-specific instructions (Windows, macOS, Linux), see [`LLM.txt`](LLM.txt).

---

## How to Operate: The Brain & The Hands

This system relies on a strict separation of concerns:

- **The Brain (The Orchestrator):** You paste the `system-prompt.md` here. It acts as the Orchestrator. It has _no_ direct access to your files or terminal. It thinks, plans, and generates XML task blocks.
- **The Hands (OpenCode):** Runs locally on your machine. You paste the XML task blocks here. It executes file changes, runs bash commands, triggers Agent Skills, and generates task summaries to feed back to the Brain.
- **The QA Loop:** After OpenCode implements a task, the Manager pastes the task file back to the Orchestrator. The QA Engineer persona performs adversarial testing — actively trying to break the logic. If QA fails, a fix task is generated. If QA passes, the Code Reviewer does a final architectural review before the task is committed and closed.

### Scenario A: Phase 0 for a Brand New Project

1. Initialize an empty repository on your machine and start OpenCode.
2. In the Orchestrator, paste the `system-prompt.md` and say: _"This is a new project. Start Phase 0."_
3. Tell the AI your desired tech stack (e.g., Next.js, Node.js).
4. The AI will generate an implementation task instructing OpenCode to:
   - Copy the relevant stack `SKILL.md` template from your global skills directory.
   - Create `opencode.json` with the required schema.
   - Set up the `tasks/` directory and use the `task-generator` skill to create your first `01-initial-setup.md` task.

### Scenario B: Phase 0 for an Existing Project (Never used this workflow)

1. Open your existing project in OpenCode.
2. In the Orchestrator, paste the `system-prompt.md` and say: _"This is an existing project. Start Phase 0."_
3. The AI will immediately output a `<hands_discovery_task>`. Paste this into your local agent (OpenCode or Freebuff).
4. OpenCode will use its MCP tools to map the directory tree and read core files into a `context-reports/` markdown file.
5. Copy the contents of that report and paste it back into the Orchestrator.
6. The AI will analyze your existing architecture and design, then generate an implementation task to create `AGENTS.md` (<150 lines), `DESIGN.md` (if UI exists), `opencode.json`, and the `tasks/` directory, locking in your current conventions.

### Scenario C: Migrating a V4 Project to V5

If you have an older project using global `STATE.md` and `TODO.md` files:

1. Open the project locally. Delete `STATE.md` and `TODO.md`.
2. Create a `tasks/` directory.
3. In the Orchestrator, paste the **new V5 `system-prompt.md`**.
4. Tell the AI: _"Migrate this project from V4 to V5. Generate a task to update `AGENTS.md` and move existing roadmap items into `tasks/01-v5-migration.md`."_
5. Ensure the `task-generator` and `audit-agents` skills are imported into `.opencode/skills/` (or installed globally).

### Inline Markdown Reviews & Strict Approval

Before any code is written, the Brain will present an Architectural Blueprint or Plan. OpenCode will **not** execute any implementation tasks without your explicit approval.

To leave feedback directly on the generated Markdown plans:

1. Copy the plan into your editor.
2. Add `> 📝 **MANAGER REVIEW:**` blockquotes immediately below the section you want to change.
3. Alternatively, use standard Markdown strikethrough (`~~text~~`) and bold (`**text**`) for direct edits.
4. Paste the annotated Markdown back to the Orchestrator.

The AI will process your inline feedback, generate a revised plan, and wait for your final "Approved" signal before writing code.

### Manager Profile & AI Coaching

The `system-prompt.md` includes a `<manager_profile>` (a **Founder Operating System**) and `<leadership_and_language_protocol>`. By default, this is configured for the original author: an **AI-native Founder** whose objective is building an AI-first software company. The profile models his identity, long-term mission, growth model (Solo Builder → Founder → Product Leader → Engineering Leader → CEO → Executive), entrepreneurial history, behavioral patterns, cognitive biases, and an implicit decision framework. System-level rules — `<ai_objective>`, `<operating_principles>`, `<delegation_strategy>`, and `<challenge_policy>` — make every persona act as his long-term **co-founder, executive advisor, product strategist, systems architect, and leadership coach** — not a coding assistant.

- **Founder-First Coaching:** Before any recommendation, personas evaluate the request against the AI objective, mission, operating principles, and decision framework (recurring revenue, leverage, evidence over excitement, optimization before exploration, compounding advantage) and actively defend against the Manager's documented cognitive biases.
- **Delegation Strategy:** The default solution is never "the Manager writes more code" — personas improve systems, AI, workflows, delegation, documentation, and hiring first.
- **Language & Vocabulary Corrections:** If the AI notices grammatical errors or forgotten industry keywords in your prompts, it will append a small `> 💡 **Coach's Note:**` at the end of its response to teach you the correct term or pronunciation.
- **Ruthless Soft-Skills Feedback:** When you close a sprint or ask for feedback (e.g., _"Give me your ruthless feedback about me so I can improve"_), the AI personas will critique your tone and management style as a founder, telling you how a real human would have reacted to your instructions.

**Customizing for Yourself:**
Open `prompts/fragments/04-manager_profile.md` and edit the `<manager_profile>` block there, then regenerate via `python3 scripts/prompt-build/assemble_system_prompt.py` (see `prompts/README.md` for the full authoring workflow).

---

### Prompt Composer Tool

The repository includes a standalone web tool at `tools/prompt-composer/index.html` that automates the Brain↔Hands copy-paste workflow. The tool fetches the latest `system-prompt.md` from GitHub, provides preset Manager commands, and generates structured Markdown output ready to paste into the Orchestrator chat interface.

**Access the tool:** [https://mokhtarabadi.github.io/cognitive-lead-hq/](https://mokhtarabadi.github.io/cognitive-lead-hq/) (deployed via GitHub Pages)

**Features:**

- Fetches the latest `system-prompt.md` from GitHub
- Preset Manager commands (Phase 0, Task Discovery, Collect Context, Approved, QA, Code Review, Closure)
- Optional Project Tree input — included in the generated Markdown when provided
- Custom notes and task file pasting
- Generates structured Markdown output
- One-click copy to clipboard

---

## Cognitive Loop Engine

The **Cognitive Loop Engine** is a local orchestration daemon that eliminates the manual copy-paste workflow between the Orchestrator (Brain) and OpenCode (Hands). It routes tasks to LLM APIs, invokes execution programmatically, and maintains Manager approval gates via Telegram.

### What It Does

```
Manager creates task → Daemon detects → AI plans → Telegram approval →
OpenCode executes → QA reviews → Telegram closure → Done
```

### Quick Start

```bash
# 1. Install dependencies
cd loop-engine
uv venv .venv
source .venv/bin/activate
uv pip install pydantic litellm watchdog python-telegram-bot

# 2. Configure
cp ../.env.example ../.env
# Edit .env with your API keys

# 3. Start
python daemon.py
```

### Features

- **Category-based model routing** — quick→kimi, deep→gpt-5.6, visual→opus-5
- **Telegram approval gateway** — Inline keyboard Approve/Reject
- **Auto-continue** — Goal Plugin handles idle detection and continuation
- **Evidence-bound QA** — No evidence = no commit
- **SQLite state machine** — Crash recovery, task tracking
- **Multi-project support** — One bot, Topics per project

### Documentation

- [Architecture Overview](docs/loop-engine/README.md)
- [Setup Guide](docs/loop-engine/setup.md)
- [Configuration Reference](docs/loop-engine/configuration.md)
- [Multi-Project Guide](docs/loop-engine/multi-project.md)

---

## Repository Structure

```
/
├── README.md                           # This file
├── system-prompt.md                    # Generated Orchestrator system prompt (assembled from prompts/)
├── CHANGELOG.md                        # Version history
├── tasks/
│   ├── backlog/                        # Open / unstarted tasks
│   ├── in-progress/                    # Currently being worked on
│   ├── qa/                             # Awaiting quality assurance review
│   ├── completed/                      # Finished tasks
│   └── archive/                        # Milestone-compacted historical tasks
├── agents/                             # Custom OpenCode agents (cognitive-executor, etc.)
│   ├── cognitive-executor.md           # Primary execution engine (ZAC, Kanban lifecycle)
│   └── cognitive-discovery.md          # Read-only context gathering subagent
├── docs/
│   ├── conventions.md                  # Syntax rules and automation conventions
│   ├── history/                        # Milestone compaction summaries
│   └── opencode/                       # OpenCode documentation mirror
├── mcp-context-server/
│   └── server.py                       # FastMCP server for .gitignore-aware file reading & tree
├── mcp-lint-server/
│   └── server.py                       # FastMCP server for task file linting
├── mcp-memory-server/
│   └── server.py                       # FastMCP server for persistent project memory
├── loop-engine/                         # Cognitive Loop Engine daemon
│   ├── daemon.py                        # Main entry point
│   ├── models.py                        # Pydantic config validation
│   ├── state.py                         # SQLite state machine
│   ├── watcher.py                       # Kanban filesystem observer
│   ├── router.py                        # LLM category routing
│   ├── executor.py                      # Goal Plugin delegation
│   ├── gateway.py                       # Telegram approval gateway
│   ├── qa_engine.py                     # Evidence-bound QA
│   ├── loop-engine.jsonc                # Configuration file
│   └── pyproject.toml                   # Python dependencies
├── prompts/                            # System prompt source tree (fragments + shared partials)
│   ├── README.md                       # Authoring workflow guide
│   ├── manifest.txt                    # Ordered fragment list (assembly order)
│   ├── fragments/                      # One file per top-level XML tag (01-20)
│   └── shared/                         # Shared partials (e.g. validation-phase.md)
├── tests/
│   └── test_mcp_servers.py             # Pytest suite for MCP servers
├── .opencode/
│   └── skills/
│       └── sop-maintenance/
│           └── SKILL.md                # Native OpenCode skill for repo rules
├── scripts/
│   ├── bundle-tasks.py                # Deterministic meta-task bundler (Task 110) — CLI for `bundle_tasks` MCP
│   └── prompt-build/
│       ├── split_system_prompt.py     # Disassembler: system-prompt.md → fragments/
│       └── assemble_system_prompt.py  # Assembler: fragments/ → system-prompt.md
├── skill-templates/                    # Reusable stack blueprints (Agent Skills)
│
│   **General & Workflow:**
│
│   ├── archive-tasks/                  # Milestone compaction skill
│   │   └── SKILL.md
│   ├── audit-agents/                   # AGENTS.md generation & ZAC audits
│   │   └── SKILL.md
│   ├── brainstorm-swarm/               # Multi-persona brainstorming sessions
│   │   └── SKILL.md
│   ├── code-search/                    # MCP-based codebase discovery
│   │   └── SKILL.md
│   ├── debug-instrumentation/          # Strategic logging for complex bug diagnosis
│   │   └── SKILL.md
│   ├── design-md/                      # Design system extraction (DESIGN.md)
│   │   └── SKILL.md
│   ├── doc-coauthoring/                # Structured documentation co-authoring
│   │   └── SKILL.md
│   ├── migrate-kanban/                 # Flat-to-Kanban migration skill
│   │   └── SKILL.md
│   ├── perplexity-research/            # Human-in-the-loop deep research
│   │   └── SKILL.md
│   ├── project-memory/                 # Persistent project memory bank
│   │   └── SKILL.md
│   ├── prompt-refactor/                # Refactors raw prompts into elite XML specs
│   │   └── SKILL.md
│   ├── bundle-tasks/                   # Meta-task bundling — 2–6 tasks → one META (CLI + MCP)
│   │   └── SKILL.md
│   ├── task-generator/                 # Generates tasks in tasks/backlog/
│   │   └── SKILL.md
│   ├── telegram-issue-sync/            # Telegram topics → tasks/GitHub sync
│   │   └── SKILL.md
│   ├── telegram-message-export/        # Export Telegram messages to ZIP
│   │   └── SKILL.md
│   ├── verification-before-completion/ # Mandatory verification gate
│   │   └── SKILL.md
│   ├── versioning-and-release/         # SemVer, Changelog, Commit standards
│   │   └── SKILL.md
│
│   **Stack-Specific Blueprints:**
│
│   ├── android-kotlin/                 # 100% Jetpack Compose + MVI + Hilt
│   │   └── SKILL.md
│   ├── flask-python/                   # Application Factory + SQLAlchemy
│   │   └── SKILL.md
│   ├── go-gin/                         # Idiomatic Go + Clean Architecture
│   │   └── SKILL.md
│   ├── go-hexagonal-grpc/              # Ports & Adapters + gRPC + Uber Fx
│   │   └── SKILL.md
│   ├── ios-swiftui/                    # SwiftUI + MVVM
│   │   └── SKILL.md
│   ├── nestjs-prisma-vertical/         # NestJS + Prisma + Vertical Slices
│   │   └── SKILL.md
│   ├── nextjs/                         # App Router + Server Actions + Tailwind
│   │   └── SKILL.md
│   ├── python-fastapi/                 # Pydantic V2 + modular routing
│   │   └── SKILL.md
│   ├── react-native-expo/              # Expo Managed + NativeWind
│   │   └── SKILL.md
│   ├── react-vite/                     # React 18+ SPA + hooks
│   │   └── SKILL.md
│   ├── spring-boot/                    # DDD + hexagonal-style packaging
│   │   └── SKILL.md
│   └── vue-nuxt/                       # Vue 3 Composition API + Nuxt 3
│       └── SKILL.md
└── user-prompts/                       # Reusable copy-paste prompt templates
    ├── cold-start-context.md
    ├── session-compactor.md
    ├── voice-to-text-enhancer.md
    ├── persian-to-english-dictation.md
    └── agile-pm-state-manager.md
```

---

## Agent Skills Registry

### General & Workflow Skills

| Skill Name                | Purpose                                                                                                                                                                                                                                   |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `audit-agents`            | Enforces Zero-Autonomous-Commit (ZAC) workflows and generates/audits `AGENTS.md` for new and existing projects.                                                                                                                           |
| `code-search`             | Mandatory for discovery. Uses MCP tools (`get_directory_tree`, `read_source_files`, `extract_signatures`) to explore the codebase without token bloat.                                                                                    |
| `debug-instrumentation`   | Diagnoses complex runtime bugs, deadlocks, race conditions, and silent failures via strategic temporary logging and tracing.                                                                                                              |
| `design-md`               | Extracts a comprehensive design system (`DESIGN.md`) directly from frontend source code — React, Vue, Svelte, Angular, plain HTML/CSS, or any web framework.                                                                              |
| `doc-coauthoring`         | Guides users through a structured 3-stage workflow (Context Gathering, Refinement & Structure, Reader Testing) for co-authoring documentation with AI.                                                                                    |
| `prompt-refactor`         | Meta-cognitive skill that refactors basic human prompts into elite, highly constrained, XML-tagged instructions optimized for AI agent reasoning.                                                                                         |
| `bundle-tasks`            | Deterministic meta-task bundling — bundles 2–6 small related tasks into one META for unified execution with verbatim preservation and auto-archive. Exposed as both `scripts/bundle-tasks.py` CLI and `bundle_tasks` MCP tool (Task 110). |
| `task-generator`          | Automatically generates decentralized task files based on Manager instructions, with correct `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.                                                                                 |
| `telegram-issue-sync`     | Syncs Telegram supergroup topics into local task files and GitHub issues, using embedded Python scripts for deterministic JSON state management.                                                                                          |
| `telegram-message-export` | Intelligently exports a range of Telegram messages (text, media, voice notes) into a numbered folder, capturing reply hierarchies, and packing them into a ZIP archive.                                                                   |
| `versioning-and-release`  | Standardizes Semantic Versioning (SemVer), Keep a Changelog formats, Conventional Commits, and Safe Push Protocols across all repositories.                                                                                               |
| `freebuff-documents`      | SOP for creating and editing Freebuff knowledge documents (AGENTS.md, CLAUDE.md, *.knowledge.md, ~/.AGENTS.md) and defining always-loaded roles. Project-specific to this HQ repo — NOT in the global Skill Auto-Loading Matrix.          |

### Stack-Specific Blueprints

| Stack                  | Architecture Enforced                                                                                      |
| ---------------------- | ---------------------------------------------------------------------------------------------------------- |
| Android Kotlin         | **100% Jetpack Compose — XML Strictly Banned.** MVI (UDF), Hilt, SQLDelight/Room.                          |
| Flask Python           | Application Factory, Blueprints, SQLAlchemy, and config separation for modular Flask applications.         |
| Go Gin                 | Idiomatic Go, Clean Architecture layers, and Gin routing best practices for RESTful services.              |
| Go Hexagonal gRPC      | Hexagonal Architecture (Ports and Adapters), gRPC, Uber Fx compile-time DI, Redis caching, and PostgreSQL. |
| iOS SwiftUI            | SwiftUI, MVVM, and modern iOS app architecture with declarative UI patterns.                               |
| NestJS Prisma Vertical | NestJS, Prisma ORM, Vertical Slice Architecture, strict TypeScript, and class-validator DTOs.              |
| Next.js                | App Router, Server/Client Component separation, Server Actions, and Tailwind CSS design tokens.            |
| Python FastAPI         | Pydantic schemas, dependency injection, async routing, and layered service architecture.                   |
| React Native Expo      | **Expo Managed Workflow ONLY — no native folders.** Expo Router, NativeWind, Zustand, strict TypeScript.   |
| React Vite             | React 18+ SPA architecture, hooks, and Vite configuration with optimized build tooling.                    |
| Spring Boot            | DDD, hexagonal-style packaging, MapStruct, constructor injection, and global exception handlers.           |
| Vue Nuxt               | Vue 3 Composition API, Nuxt 3 routing, and Pinia state management.                                         |

---

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
      "enabled": true,
      "timeout": 15000
    }
  },
  "permission": {
    "custom_context_*": "allow",
    "get_directory_tree": "allow",
    "read_source_files": "allow",
    "bundle_tasks": "allow"
  }
}
```

#### Option B: Global Setup (System-wide)

Best if you want this codebase exploration tool available in _every_ terminal directory automatically.

1. Create a global directory for the server: `mkdir -p ~/.config/opencode/mcp-context-server`
2. Copy the `server.py` script into that directory.
3. Make it executable: `chmod +x ~/.config/opencode/mcp-context-server/server.py`.
4. Open your global config at `~/.config/opencode/opencode.json` and add the absolute path:

```json
{
  "mcp": {
    "custom_context": {
      "type": "local",
      "command": [
        "uv",
        "run",
        "/Users/<YOUR_USER>/.config/opencode/mcp-context-server/server.py"
      ],
      "enabled": true,
      "timeout": 15000
    }
  },
  "permission": {
    "custom_context_*": "allow",
    "get_directory_tree": "allow",
    "read_source_files": "allow",
    "bundle_tasks": "allow"
  }
}
```

_(Note: Replace `/Users/<YOUR_USER>` with your actual home directory path)._

### How It Works

1. `opencode.json` configures the custom context server as a local MCP server.
2. When OpenCode needs to explore code, it uses `get_directory_tree` (inline tree), `create_tree_report` (persistent tree file), and `read_source_files` (compiled context report) tools.
3. All file reads respect `.gitignore` rules and skip binary/large files automatically.
4. The strategy is documented in `skill-templates/code-search/SKILL.md`.

### Available Tools (Core 3 + 2 Optional)

**Core — always installed:**

- `get_directory_tree` — Generates an ASCII tree of the directory structure, respecting `.gitignore`.
- `create_tree_report` — Saves a persistent `.gitignore`-aware directory tree of any path (default: the entire project) as `context-reports/tree_report_<timestamp>_<uuid>.md`, mirroring the context report convention. Trigger phrase: "create a tree of the project".
- `read_source_files` — Reads multiple source files or directories and saves their contents into a local Markdown report inside the `context-reports/` directory, returning the file path to prevent context bloat.
- `extract_signatures` — Extracts structural signatures (classes, functions, methods) via tree-sitter (fallback to regex) and saves to `context-reports/signatures_report_<timestamp>_<uuid>.md`.
- `bundle_tasks` — **Meta-task bundler (Task 110, self-contained).** Bundles 2–6 small related tasks into one META for unified execution (`tasks/backlog/<NEXT_ID>-<slug>.md` + `**Supersedes:** [ids]` + verbatim appendices, `git mv` to `tasks/archive/` with `superseded` patch). CLI `uv run scripts/bundle-tasks.py <id> ... --title "<title>" [--dry-run] [--force]` and MCP `bundle_tasks(task_ids, title, dry_run, force)` are identical and self-contained — other projects that only have this MCP server (no `scripts/` copy) can still bundle via the Hands. Guardrails: cap 6, LOC >400 warning, missing-ID and collision checks. See `skill-templates/bundle-tasks/SKILL.md` and `AGENTS.md` `## 🛑 META-TASK BUNDLE LIFECYCLE`.

**Optional — auto-installed via `LLM.txt` Step 7.6:**

- `blowsh` (Docker `ghcr.io/mokhtarabadi/blowsh-mcp:latest`, 4 tools) — **JS-capable browsing (retired browser MCP replacement).** `fetch_web` (plain/html/markdown/pdf + selector/max_chars/wait_ms), `search_web` (DuckDuckGo+Bing), `extract_links`, `fetch_web_batch` (10 URLs). SSRF guard, TTL cache. Timeout 120s. See https://github.com/mokhtarabadi/blowsh-mcp and `docs/telegram-setup.md` (setup maps to same global install).
- `telegram` (Telethon, 80+ tools, `uv --directory $HOME/.config/opencode/mcp-telegram-server run main.py` over absolute path in opencode config dir) — Accounts (`list_accounts`, multi-account `account` param), chats/groups, messages (`send_message`/`reply_to_message` with `account="personal"`/`"work"`), contacts/aliases, media (`send_file`/`download_media`), events (`wait_for_settled_message`, `enable_incoming_feed`). File roots required for media tools (`/tmp/telegram-mcp` + `$HOME/.config/opencode/mcp-telegram-server/downloads`). Used by `skill-templates/telegram-issue-sync/SKILL.md` (supergroup → tasks) and `telegram-message-export/SKILL.md` (range → ZIP) — see `docs/telegram-setup.md` §6 for the full skill→tool→config table. Single vs work/personal setup documented there plus `LLM.txt` 7.6 (absolute paths, installed in `~/.config/opencode/`).

### Meta-Task Bundling — CLI vs MCP (When to Copy the Script)

| Scenario                                                             | What to copy                                                                                                                                             | How to bundle                                                                                        |
| -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **You have shell (Manager runs `uv run`)**                           | Copy `scripts/bundle-tasks.py` to your project's `scripts/` (or keep it from the HQ template)                                                            | `uv run scripts/bundle-tasks.py 12 15 20 --title "android-polish" [--dry-run]`                       |
| **You only have the MCP server (Hands in other projects, no shell)** | **No script copy needed** — `mcp-context-server/server.py:bundle_tasks` is self-contained (helpers duplicated from the script, no `scripts/` dependency) | Hands calls MCP tool `bundle_tasks(task_ids=["12","15","20"], title="android-polish", dry_run=true)` |
| **Both**                                                             | Keep both — they are kept in sync and produce identical `tasks/backlog/<NEXT_ID>-<slug>.md` + archive patching                                           | Use CLI for Manager one-offs, MCP for AI-driven bundling                                             |

> **Is the script redundant?** No — CLI is for the Manager (`uv run`), MCP is for the Hands (AI). For cross-project reuse, **MCP is sufficient**: other projects that vendor this HQ's MCP servers (`~/.config/opencode/mcp-context-server/server.py`) can bundle without copying `scripts/`. If those projects also want CLI, copy `scripts/bundle-tasks.py` to `scripts/` (one file, `chmod +x`).

---

## Global Skills Deployment

To make the `code-search` skill (or any other reusable skill) available in _every_ terminal directory on your machine automatically, copy the skill folder into your global OpenCode configuration path.

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

---

## Custom OpenCode Agents

This workflow relies on a dedicated primary agent (`cognitive-executor`) and a read-only subagent (`cognitive-discovery`) to hard-enforce Zero-Autonomous-Commits (ZAC), MCP-first context gathering, and the strict finalization sequence at the platform permission layer.

To install them globally, run the `LLM.txt` auto-configuration script. Once installed, you can start OpenCode with the executor agent using:

```bash
opencode --agent cognitive-executor
```

---

## Freebuff Support (Dual-Runtime)

> **Dual-runtime support.** Since v8.4.5 the system prompt (`system-prompt.md`) is **runtime-agnostic** — it addresses "the Hands" (the local execution agent) and emits `<hands_*_task>` blocks that work in both OpenCode and Freebuff.

[Freebuff](https://freebuff.com) (vendor: **CodebuffAI**, formerly Codebuff-based — the `~/.config/manicode/` binary path is a legacy config-root name) is a free, ad-funded terminal AI coding agent. It does **not** read `opencode.json`; it uses its own `.agents/` extension points plus a home-directory global rules file. As of 2026-08-26 (Freebuff CLI `0.0.156`, source audit of [`github.com/CodebuffAI/freebuff`](https://github.com/CodebuffAI/freebuff)) the following Cognitive Lead AI HQ components were ported and verified (schema-validated in-repo; the custom agents' free-tier spawn is **VERIFIED BLOCKED** — server-side allowlist, paid/credits tier required, see `docs/freebuff-support.md` §5):

| Component                                                                      | Freebuff status      | Notes                                                                                                                                                                                                                                                                  |
| ------------------------------------------------------------------------------ | -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MCP servers (`custom_context`, `project_memory`, `lint`, `blowsh`, `telegram`) | ✅ FULL              | `~/.agents/mcp.json`, 18+ tools core + blowsh (4) + telegram (80+) verified; `blowsh` Docker, `telegram` Telethon                                                                                                                                                      |
| Skills (31)                                                                    | ✅ FULL              | `~/.agents/skills/`, verified loading (31 since 2026-08-26)                                                                                                                                                                                                            |
| Custom agents (`cognitive-executor`, `cognitive-discovery`)                    | ✅ FULL (REPO-LEVEL) | `~/.agents/*.ts` (v1.2.0) — schema-validated 17-tool whitelist + `publisher/name@version` spawnables; `model` omitted — ❌ free-tier spawn **VERIFIED BLOCKED** (paid tier required); free tier can spawn Freebuff built-in subagents via `base2-free-*` orchestrators |
| Global rules ("The Hands" + Cognitive Executive Role)                          | ✅ FULL              | `~/.AGENTS.md` — baseline constraints + the **Cognitive Executive Role** in every session (free tier included); source: `freebuff/AGENTS.global.md`                                                                                                                    |
| `system-prompt.md` Orchestrator Brain                                          | 📄 MANUAL            | Runtime-agnostic since v8.4.5 — paste into Freebuff or OpenCode                                                                                                                                                                                                        |
| `user-prompts/` templates                                                      | 📄 MANUAL            | Runtime-agnostic copy-paste templates                                                                                                                                                                                                                                  |

**For users who want to run the Cognitive Lead workflow with Freebuff instead of OpenCode**, see the full guide: [`docs/freebuff-support.md`](docs/freebuff-support.md) — it documents the extension points (mcp.json / skills / TS agents / global rules), the port record, verification commands, and the verified free-tier limitation (custom agents require a paid/credits tier; on free tier paste `<hands_*_task>` blocks into the base chat or spawn Freebuff's built-in subagents via a `base2-free-*` "Free Orchestrator" agent).

**Installing:** the `LLM.txt` auto-configuration includes an **optional** Freebuff step (Step 7.5) that installs the MCP servers + 31 skills + custom agents + global rules under `~/.agents/` and `~/.AGENTS.md`.

**Freebuff documents & roles:** Freebuff has no role/persona feature — the always-loaded **knowledge-file** system is the sanctioned way to define agents-as-roles, and the **Cognitive Executive Role** ships in `freebuff/AGENTS.global.md` (installed as `~/.AGENTS.md`). Maintain Freebuff's knowledge documents via the [`freebuff-documents` skill](skill-templates/freebuff-documents/SKILL.md) and see [`docs/freebuff-documents.md`](docs/freebuff-documents.md) for the full document system + role reference. Blowsh (`docker run --rm -i ghcr.io/mokhtarabadi/blowsh-mcp:latest`, 4 tools) provides JS-capable browsing; Telegram (`uv --directory $HOME/.config/opencode/mcp-telegram-server run main.py` over absolute path, 80+ tools) is configured in Step 7.6 with work/personal `account` routing, installed in opencode config dir (`~/.config/opencode/mcp-telegram-server/`) — see `docs/telegram-setup.md`.

**Upgrading an existing project** to the v8.4.5 runtime-agnostic workflow (non-breaking, legacy headers still lint): see [`docs/workflow-upgrade-v8.4.5.md`](docs/workflow-upgrade-v8.4.5.md).

---

## Key V5 Changes

- **Decentralized task architecture** — global `STATE.md` and `TODO.md` replaced by isolated task files in `tasks/` directory.
- **Brain/Hands separation codified** — `system-prompt.md` explicitly declares the Orchestrator as the text-only Brain and OpenCode as the local execution agent.
- **New Agent Skills** — `task-generator` for creating numbered task files and `audit-agents` for enforcing `AGENTS.md` workflows.
- **Phase 0 UI/UX traversal** — Project Planner now instructs OpenCode to perform deep source code analysis for `DESIGN.md` generation.
- **Runtime model updated** — Model identifier cleaned up for platform-agnostic use.

## Key V7 Changes

- **Brainstorming Protocol (`<brainstorming_protocol>`):** Multi-agent brainstorming with six specialized personas (system_architect, security_engineer, product_manager, business_strategist, legal_advisor, critical_thinker) for cross-disciplinary ambiguity resolution.
- **Universal Datetime Rules (`<universal_datetime_rules>`):** UTC-at-rest, ISO-8601/Unix-epoch at API boundaries, SOLID Clock injection, dual-representation for future calendar events, and timezone-independent CI/CD testing.
- **SOLID Programming Mandate (`<solid_programming_mandate>`):** Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion enforced on every generated implementation task, with pragmatic guardrails (No Zero-Abstraction Dogma, 3-Implementation Rule, YAGNI, Occam's Razor).
- **Leadership & Language Protocol (`<leadership_and_language_protocol>`):** Executive coaching persona that provides vocabulary assistance, English pronunciation guides (Persian phonetics), and ruthless soft-skills feedback during sprint retrospectives.
- **Expanded Agent Skills Registry:** 31 skills including stack-specific blueprints (android-kotlin, spring-boot, react-vite, nestjs-prisma-vertical, go-hexagonal-grpc, python-fastapi, nextjs, flask-python, react-native-expo, ios-swiftui, vue-nuxt, go-gin) and global workflow skills (brainstorm-swarm, design-md, project-memory, telegram-issue-sync, perplexity-research, verification-before-completion, debug-instrumentation, freebuff-documents).

## Key V6 Changes

- **Kanban lifecycle architecture** — flat `tasks/` directory replaced by state-based folders: `tasks/backlog/`, `tasks/in-progress/`, `tasks/qa/`, `tasks/completed/`, `tasks/archive/`.
- **`commit_and_clean_task` MCP tool** — new tool on the custom context server that commits staged changes, strips the raw git diff from the task file, and replaces it with a commit hash reference, keeping task files lean.
- **`migrate-kanban` skill** — automated migration of existing flat `tasks/` files into the Kanban structure by reading status metadata.
- **`archive-tasks` skill** — milestone compaction: scans `tasks/completed/`, generates dense `docs/history/milestone-X-summary.md`, and moves files to `tasks/archive/`.
- **System prompt upgraded to V6.0.0** — all personas and workflows updated for the Kanban lifecycle. Project Planner manages state-based Kanban directories. Code Reviewer now generates tasks that move files through the pipeline. Execution workflow includes `backlog → in-progress → qa → completed` transitions.

## Key V6.7 Changes

- **Manager Profile & Coaching Protocol** — Added a dedicated `<manager_profile>` to the system prompt, giving the AI deep context about the Manager's technical background, work style, and career trajectory.
- **Leadership & Language Feedback** — Introduced the `<leadership_and_language_protocol>`. The AI now acts as an Executive Coach, teaching forgotten industry keywords, correcting English grammar/pronunciation (using Persian phonetic text), and providing ruthless soft-skills feedback during sprint retrospectives to prepare the Manager for leading real human teams.

---

## Contributing

See `.opencode/skills/sop-maintenance/SKILL.md` for the rules that AI agents must follow when modifying this repository.

## Future Architectural Roadmap

1. **Automated Pull Request Integration:** Upgrade the final Code Reviewer step to automatically branch, commit, and open a PR via GitHub CLI (`gh pr create`) instead of committing locally to `main`.
2. **Epic and Milestone Tracking:** Create an `epics/` directory and update the `task-generator` skill to link individual tasks to parent epics for better macro-level project tracking.
3. **Dedicated `testing-strategy` Skill:** Create a template enforcing Test-Driven Development (TDD) or strict coverage thresholds, ensuring OpenCode writes tests before or alongside implementation code.
4. **Database Migration Management:** Create a `database-migration` skill to strictly forbid direct schema alterations, forcing the use of standard migration tools (Prisma, Alembic, Flyway) for safe, repeatable deployments.
5. **Hexagonal Architecture Expansion:** Port the strict Ports & Adapters blueprint from Go to our Python (FastAPI) and TypeScript (Node.js) templates to unify "Max Power" backend design patterns across all supported stacks.
