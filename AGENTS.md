# Cognitive Lead AI HQ — Project Context Hub

## 🛑 MANDATORY FIRST-READ RULE

The very first file the agent MUST read before performing any task is `AGENTS.md`.
This file acts as the primary router. You MUST load and read the following documents first before executing any code changes to guarantee 100% structural and stylistic alignment:

1. `DESIGN.md` — Enforces colors, typography, layout scale, component styling, and RTL Persian configurations.
2. `docs/architecture.md` — Defines project structure, layer boundaries, and key data flow policies.
3. `docs/data_model.md` — Defines database entities, schemas, pointers, and object relationships.
4. `docs/conventions.md` — Defines syntax rules, naming conventions, file boundaries, and localization paths.

## Project Overview

This repository is the Headquarters for the Cognitive Lead AI multi-agent system. It is a **documentation-only** repository containing system prompts, MCP servers, and Agent Skills (`SKILL.md`).

## Setup & Dev Commands

- Run custom context MCP: `uv run mcp-context-server/server.py`
- Format Markdown: `npx prettier --write "**/*.md"`

## Actionable Guardrails (Do's & Don'ts)

- **Don't** generate or write functional application code (Python, JS, Go, etc.) in this repository.
  -> **Do** write structured framework-specific SOPs and reusable Markdown templates only.
- **Don't** edit `system-prompt.md` without updating the version identifier.
  -> **Do** increment the version inside `<system_version>` at the very top of `system-prompt.md`, update the active task file in `tasks/`, and log a formal entry in `CHANGELOG.md`.
- **Don't** read `context-reports/` markdown files yourself.
  -> **Do** generate them using the MCP server and hand the file path to the Manager.
- **Don't** create monolithic state files like `TODO.md` or `STATE.md`.
  -> **Do** use the decentralized `tasks/` directory with individual task files as the single source of truth.
- **Don't** make UI/UX changes without consulting `DESIGN.md`.
  -> **Do** enforce the color palette, typography, spacing, and component styling defined in `DESIGN.md`.
- **Don't** execute Git commands like `git add`, `git commit`, or `git mv` autonomously or try to guess when to stage code.
  -> **Do** execute Git commands ONLY when explicitly instructed by an AI Studio task block. Otherwise, rely on the `custom_context_stage_and_inject_diff` MCP tool.

## Documentation Sync Rules

When modifying this repository, you must keep these files synchronized:

1. Active task file in `tasks/` (single source of truth for current work items)
2. `CHANGELOG.md` (Keep a Changelog format)
3. `DESIGN.md` (UI/UX design system, if modified)
4. Relevant `SKILL.md` files (if structural patterns were altered)

## 🛑 GATEKEEPER VALIDATION (HALT PROTOCOL)

You (OpenCode) are the final gatekeeper. Before executing any implementation task, you MUST evaluate the Orchestrator's instructions against this file and any referenced specs (`DESIGN.md`, `architecture.md`, etc.). If the instructions violate project rules, ignore them. HALT immediately and output a `⚠️ RULE VIOLATION WARNING` back to the Manager explaining exactly what the Orchestrator got wrong, forcing it to self-correct.

## 🛑 CORE FILE LOCATIONS

You MUST strictly adhere to these exact paths. Do not create duplicates elsewhere:

- **Global Rules:** `AGENTS.md` (Root)
- **UI/UX Specs:** `DESIGN.md` (Root)
- **Agent Skills:** `.opencode/skills/<skill-name>/SKILL.md` (Local workspace)
- **Active Tasks:** `tasks/backlog/<task-number>-<name>.md` (backlog), `tasks/in-progress/`, `tasks/qa/`, `tasks/completed/`, `tasks/archive/`

## 🛑 SKILL LOADING RULES

You MUST follow these skill loading rules in every session:

- **Task-Generator Skill:** Before creating any new task file, you MUST load the `task-generator` skill using the `skill` tool to ensure the correct template format with `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.
- **Project Skills:** Before implementing any task, you MUST load every available skill matching the project's tech stack (e.g., `android-kotlin`, `spring-boot`, `react-vite`, `nodejs-express`, `python-fastapi`). If a relevant skill exists, it MUST be loaded — this enforces framework-specific conventions and architectural rules.

## 🛑 MANDATORY END-OF-TASK SEQUENCE

When finishing a task, you MUST execute these exact steps in order:

1. **Update Changelog:** You MUST insert a formal entry into CHANGELOG.md logging your modifications.
2. **Move to Completed:** If the task is finished and approved, move the task file from its current Kanban directory to `tasks/completed/` and update its status to closed.
3. **Write your Summary:** Manually write your architectural reasoning, local TODO checks, and execution notes into the active task file under "OpenCode Execution Log".
4. **Call MCP Tool:** Call the `custom_context_stage_and_inject_diff` MCP tool passing the task file path to automatically stage the files and inject the factual code diff. DO NOT execute any `git commit` commands afterward — use `custom_context_commit_and_clean_task` instead.
5. **Notify Manager:** Output exactly: "Task ready. Manager, please copy the contents of `tasks/completed/XX-task-name.md` and send it back to the AI Studio Brain for review."
