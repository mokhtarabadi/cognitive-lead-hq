# Cognitive Lead AI HQ

[![Version](https://img.shields.io/github/v/release/mokhtarabadi/cognitive-lead-hq?style=flat-square)](https://github.com/mokhtarabadi/cognitive-lead-hq/releases)
[![License](https://img.shields.io/github/license/mokhtarabadi/cognitive-lead-hq?style=flat-square)](LICENSE)
[![OpenCode](https://img.shields.io/badge/OpenCode-ready-6C47FF?style=flat-square)](https://opencode.ai)
[![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](https://github.com/mokhtarabadi/cognitive-lead-hq/pulls)

The centralized **Headquarters** for the Cognitive Lead AI multi-agent system — a collection of hallucination-resistant system prompts, MCP servers, and strict Agent Skills (SKILL.md) built for [OpenCode](https://opencode.ai).

> **Want a quick install?** Give this line to OpenCode:
>
> ```
> Hi, please read this address and, based on the instructions in this file, set up OpenCode for the user for our project.
> ```

---

## Quick Start

Give the prompt above to any AI agent (OpenCode, Cline, etc.) and it will auto-configure itself using [`LLM.txt`](LLM.txt) — the canonical auto-setup source.

To set up manually:

```bash
git clone https://github.com/mokhtarabadi/cognitive-lead-hq.git
cd cognitive-lead-hq
cp -r skill-templates/* .opencode/skills/
uv run mcp-context-server/server.py
```

Then open OpenCode in this directory. Read `system-prompt.md` to understand the multi-agent architecture, or dive into `tasks/` for active work items. For full platform-specific instructions (Windows, macOS, Linux), see [`LLM.txt`](LLM.txt).

---

## How to Operate: The Brain & The Hands

This system relies on a strict separation of concerns:

- **The Brain (Google AI Studio):** You paste the `system-prompt.md` here. It acts as the Orchestrator. It has _no_ direct access to your files or terminal. It thinks, plans, and generates XML task blocks.
- **The Hands (OpenCode):** Runs locally on your machine. You paste the XML task blocks here. It executes file changes, runs bash commands, triggers Agent Skills, and generates task summaries to feed back to the Brain.
- **The QA Loop:** After OpenCode implements a task, the Manager pastes the task file back to AI Studio. The QA Engineer persona performs adversarial testing — actively trying to break the logic. If QA fails, a fix task is generated. If QA passes, the Code Reviewer does a final architectural review before the task is committed and closed.

### Scenario A: Phase 0 for a Brand New Project

1. Initialize an empty repository on your machine and start OpenCode.
2. In AI Studio, paste the `system-prompt.md` and say: _"This is a new project. Start Phase 0."_
3. Tell the AI your desired tech stack (e.g., Next.js, Node.js).
4. The AI will generate an implementation task instructing OpenCode to:
   - Copy the relevant stack `SKILL.md` template from your global skills directory.
   - Create `opencode.json` with the required schema.
   - Set up the `tasks/` directory and use the `task-generator` skill to create your first `01-initial-setup.md` task.

### Scenario B: Phase 0 for an Existing Project (Never used this workflow)

1. Open your existing project in OpenCode.
2. In AI Studio, paste the `system-prompt.md` and say: _"This is an existing project. Start Phase 0."_
3. The AI will immediately output an `<opencode_discovery_task>`. Paste this into OpenCode.
4. OpenCode will use its MCP tools to map the directory tree and read core files into a `context-reports/` markdown file.
5. Copy the contents of that report and paste it back into AI Studio.
6. The AI will analyze your existing architecture and design, then generate an implementation task to create `AGENTS.md` (<150 lines), `DESIGN.md` (if UI exists), `opencode.json`, and the `tasks/` directory, locking in your current conventions.

### Scenario C: Migrating a V4 Project to V5

If you have an older project using global `STATE.md` and `TODO.md` files:

1. Open the project locally. Delete `STATE.md` and `TODO.md`.
2. Create a `tasks/` directory.
3. In AI Studio, paste the **new V5 `system-prompt.md`**.
4. Tell the AI: _"Migrate this project from V4 to V5. Generate a task to update `AGENTS.md` and move existing roadmap items into `tasks/01-v5-migration.md`."_
5. Ensure the `task-generator` and `audit-agents` skills are imported into `.opencode/skills/` (or installed globally).

### Inline Markdown Reviews & Strict Approval

Before any code is written, the Brain will present an Architectural Blueprint or Plan. OpenCode will **not** execute any implementation tasks without your explicit approval.

To leave feedback directly on the generated Markdown plans:

1. Copy the plan into your editor.
2. Add `> 📝 **MANAGER REVIEW:**` blockquotes immediately below the section you want to change.
3. Alternatively, use standard Markdown strikethrough (`~~text~~`) and bold (`**text**`) for direct edits.
4. Paste the annotated Markdown back to AI Studio.

The AI will process your inline feedback, generate a revised plan, and wait for your final "Approved" signal before writing code.

---

## Repository Structure

```
/
├── README.md                           # This file
├── system-prompt.md                    # V6 Multi-Agent System Prompt
├── CHANGELOG.md                        # Version history
├── tasks/
│   ├── backlog/                        # Open / unstarted tasks
│   ├── in-progress/                    # Currently being worked on
│   ├── qa/                             # Awaiting quality assurance review
│   ├── completed/                      # Finished tasks
│   └── archive/                        # Milestone-compacted historical tasks
├── docs/
│   ├── conventions.md                  # Syntax rules and automation conventions
│   ├── history/                        # Milestone compaction summaries
│   └── opencode/                       # OpenCode documentation mirror
├── mcp-context-server/
│   └── server.py                       # FastMCP server for .gitignore-aware file reading & tree
├── .opencode/
│   └── skills/
│       └── sop-maintenance/
│           └── SKILL.md                # Native OpenCode skill for repo rules
├── skill-templates/                    # Reusable stack blueprints (Agent Skills)
│   ├── archive-tasks/                  # Milestone compaction skill
│   │   └── SKILL.md
│   ├── migrate-kanban/                 # Flat-to-Kanban migration skill
│   │   └── SKILL.md
│   ├── task-generator/                 # Generates tasks in tasks/backlog/
│   │   └── SKILL.md
│   ├── go-hexagonal-grpc/
│   │   └── SKILL.md
│   ├── prompt-refactor/
│   │   └── SKILL.md
│   ├── android-kotlin/
│   │   └── SKILL.md
│   ├── nextjs/
│   │   └── SKILL.md
│   ├── spring-boot/
│   │   └── SKILL.md
│   ├── flask-python/
│   │   └── SKILL.md
│   ├── nestjs-prisma-vertical/
│   │   └── SKILL.md
│   └── code-search/
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

| Skill Name                | Purpose                                                                                                                                                                 |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `audit-agents`            | Enforces Zero-Autonomous-Commit (ZAC) workflows and generates/audits `AGENTS.md` for new and existing projects.                                                         |
| `code-search`             | Mandatory for discovery. Uses MCP tools (`get_directory_tree`, `read_source_files`, `extract_signatures`) to explore the codebase without token bloat.                  |
| `debug-instrumentation`   | Diagnoses complex runtime bugs, deadlocks, race conditions, and silent failures via strategic temporary logging and tracing.                                            |
| `design-md`               | Extracts a comprehensive design system (`DESIGN.md`) directly from frontend source code — React, Vue, Svelte, Angular, plain HTML/CSS, or any web framework.            |
| `doc-coauthoring`         | Guides users through a structured 3-stage workflow (Context Gathering, Refinement & Structure, Reader Testing) for co-authoring documentation with AI.                  |
| `prompt-refactor`         | Meta-cognitive skill that refactors basic human prompts into elite, highly constrained, XML-tagged instructions optimized for AI agent reasoning.                       |
| `task-generator`          | Automatically generates decentralized task files based on Manager instructions, with correct `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.               |
| `telegram-issue-sync`     | Syncs Telegram supergroup topics into local task files and GitHub issues, using embedded Python scripts for deterministic JSON state management.                        |
| `telegram-message-export` | Intelligently exports a range of Telegram messages (text, media, voice notes) into a numbered folder, capturing reply hierarchies, and packing them into a ZIP archive. |
| `versioning-and-release`  | Standardizes Semantic Versioning (SemVer), Keep a Changelog formats, Conventional Commits, and Safe Push Protocols across all repositories.                             |

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

_(Note: Replace `/Users/<YOUR_USER>` with your actual home directory path)._

### How It Works

1. `opencode.json` configures the custom context server as a local MCP server.
2. When OpenCode needs to explore code, it uses `get_directory_tree` and `read_source_files` tools.
3. All file reads respect `.gitignore` rules and skip binary/large files automatically.
4. The strategy is documented in `skill-templates/code-search/SKILL.md`.

### Available Tools

- `get_directory_tree` — Generates an ASCII tree of the directory structure, respecting `.gitignore`.
- `read_source_files` — Reads multiple source files or directories and saves their contents into a local Markdown report inside the `context-reports/` directory, returning the file path to prevent context bloat.

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

## Key V5 Changes

- **Decentralized task architecture** — global `STATE.md` and `TODO.md` replaced by isolated task files in `tasks/` directory.
- **Brain/Hands separation codified** — `system-prompt.md` explicitly declares AI Studio as the text-only Orchestrator and OpenCode as the local execution agent.
- **New Agent Skills** — `task-generator` for creating numbered task files and `audit-agents` for enforcing `AGENTS.md` workflows.
- **Phase 0 UI/UX traversal** — Project Planner now instructs OpenCode to perform deep source code analysis for `DESIGN.md` generation.
- **Runtime model updated** — Gemini 3.5 Flash renamed to Gemini throughout the system prompt.

## Key V6 Changes

- **Kanban lifecycle architecture** — flat `tasks/` directory replaced by state-based folders: `tasks/backlog/`, `tasks/in-progress/`, `tasks/qa/`, `tasks/completed/`, `tasks/archive/`.
- **`commit_and_clean_task` MCP tool** — new tool on the custom context server that commits staged changes, strips the raw git diff from the task file, and replaces it with a commit hash reference, keeping task files lean.
- **`migrate-kanban` skill** — automated migration of existing flat `tasks/` files into the Kanban structure by reading status metadata.
- **`archive-tasks` skill** — milestone compaction: scans `tasks/completed/`, generates dense `docs/history/milestone-X-summary.md`, and moves files to `tasks/archive/`.
- **System prompt upgraded to V6.0.0** — all personas and workflows updated for the Kanban lifecycle. Project Planner manages state-based Kanban directories. Code Reviewer now generates tasks that move files through the pipeline. Execution workflow includes `backlog → in-progress → qa → completed` transitions.

---

## Contributing

See `.opencode/skills/sop-maintenance/SKILL.md` for the rules that AI agents must follow when modifying this repository.

## Future Architectural Roadmap

1. **Automated Pull Request Integration:** Upgrade the final Code Reviewer step to automatically branch, commit, and open a PR via GitHub CLI (`gh pr create`) instead of committing locally to `main`.
2. **Epic and Milestone Tracking:** Create an `epics/` directory and update the `task-generator` skill to link individual tasks to parent epics for better macro-level project tracking.
3. **Dedicated `testing-strategy` Skill:** Create a template enforcing Test-Driven Development (TDD) or strict coverage thresholds, ensuring OpenCode writes tests before or alongside implementation code.
4. **Database Migration Management:** Create a `database-migration` skill to strictly forbid direct schema alterations, forcing the use of standard migration tools (Prisma, Alembic, Flyway) for safe, repeatable deployments.
5. ~~**Automated Prompt Refactoring Pipeline:** Integrate the new `prompt-refactor` skill into an auto-refine pre-hook so that Manager inputs are automatically expanded into elite system prompts before code execution begins.~~ ✅ **Implemented in V6.2.0**
6. **Hexagonal Architecture Expansion:** Port the strict Ports & Adapters blueprint from Go to our Python (FastAPI) and TypeScript (Node.js) templates to unify "Max Power" backend design patterns across all supported stacks.
7. **Memory Management (Smart Note-Taking MCP & Skill):** Develop a local MCP server paired with a dedicated Agent Skill to give OpenCode persistent, project-specific memory. This solves the issue of the admin needing to repeatedly explain project quirks (e.g., "for this project, tests must run with flag X").
   - **Storage:** State will be maintained in a local JSON file within the project itself (e.g., `.opencode/project-memory.json`), allowing it to be committed or git-ignored as needed.
   - **MCP Server (`memory-mcp`):** A lightweight Python/FastMCP server providing tools to `store_note`, `retrieve_notes`, and `search_memory` intelligently.
   - **Agent Skill (`project-memory`):** A `SKILL.md` that teaches OpenCode the exact interface for this memory. It will enable seamless, natural language commands from the admin, such as:
     - _"OpenCode, load the memory skill, see what the notes are, and follow them."_
     - _"OpenCode, call the memory skill; remember this thing I'm telling you about the database tests."_
   - **Goal:** Ensure complete, highly detailed context retention across isolated sessions without permanently bloating the core `AGENTS.md` file.
8. ~~**Adversarial QA Persona:** Introduce a dedicated `[QA Engineer]` persona to the `system-prompt.md`. Unlike the Code Reviewer (who checks for formatting and architectural compliance), the QA Engineer's explicit instruction is adversarial: _actively attempt to break the Senior Programmer's implementation_. It will focus on generating negative test cases, boundary tests, fuzzing scripts, and identifying race conditions, ensuring enterprise-grade stability before a task is marked complete.~~ ✅ **Implemented in V6.1.0**
9. **Lifecycle Task Architecture (Kanban & Archiving):** ~~Migrate the flat `tasks/` directory into a state-based Kanban folder structure to prevent context bloat and improve project tracking.~~ ✅ **Implemented in V6.0.0**
   ~~- **Folders:** `tasks/backlog/`, `tasks/in-progress/`, `tasks/qa/`, and `tasks/completed/`.~~
   ~~- **Workflow:** The `task-generator` skill creates tasks in `backlog/`. As the Programmer and QA personas work, the file is physically moved through the pipeline.~~
   ~~- **Compaction:** An archiving skill will periodically compress older files in the `completed/` directory into dense, single-file summaries in `docs/history/` (e.g., `milestone-1-summary.md`), keeping the active `grep` and `glob` MCP searches blazingly fast.~~
