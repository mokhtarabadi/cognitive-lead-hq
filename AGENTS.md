# Cognitive Lead AI HQ — Agent Development Guide

## Project Overview
This repository is the central Headquarters (HQ) for the Cognitive Lead AI multi-agent system. It contains the core system prompt (`system-prompt.md`), local references (`docs/`), and reusable stack templates (`skill-templates/`). This is a **documentation-only** repository.

## Setup & Dev Commands
- Run local Context FastMCP server: `uv run mcp-context-server/server.py`
- Stage all changes (additions/deletions): `git add -A`
- Create a commit: `git commit -m "commit message"`
- Push to remote: `tsocks git push`

## SOP Maintenance Rules
- **SOP Format:** All guidelines and stack files must be written in standard Markdown (`.md`).
- **Templates structure:** Reusable templates in `skill-templates/` must contain four exact sections in this sequence: Project Structure, Naming Conventions, Architectural Patterns, Testing Strategies.
- **Progressive Disclosure:** For detailed, multi-step rules regarding template modification, invoke the `skill({ name: "sop-maintenance" })` tool on-demand. Do not read or duplicate these rules into general conversations.

## Actionable Guardrails (Do's & Don'ts)
- **Don't** generate or write functional application code (Python, JS, Go, etc.) in this repository.
  -> **Do** write structured framework-specific SOPs and reusable Markdown templates only.
- **Don't** edit or modify `system-prompt.md` without updating the version identifier and logging changes.
  -> **Do** increment the version in the prompt, update `STATE.md`, and log a formal entry in `CHANGELOG.md` following the Keep a Changelog format.
- **Don't** push changes to the remote repository directly in restricted proxy environments.
  -> **Do** wrap the push command in the `tsocks` proxy wrapper (`tsocks git push`).
- **Don't** let `AGENTS.md` exceed 150 lines of code.
  -> **Do** push detailed procedural guidelines out to on-demand skills inside `.opencode/skills/`.

## Documentation Sync Rules
During the `<documentation_phase>` of every task, you must keep the following files synchronized:
- `STATE.md` (architectural state and completed features)
- `TODO.md` (roadmap backlog and active task completion)
- `CHANGELOG.md` (formatted version releases)
