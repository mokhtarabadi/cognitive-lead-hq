# Cognitive Lead AI HQ — Project Context Hub

## Project Overview

This repository is the Headquarters for the Cognitive Lead AI multi-agent system. It is a **documentation-only** repository containing system prompts, MCP servers, and Agent Skills (`SKILL.md`).

## Setup & Dev Commands

- Run custom context MCP: `uv run mcp-context-server/server.py`
- Format Markdown: `npx prettier --write "**/*.md"`

## Actionable Guardrails (Do's & Don'ts)

- **Don't** generate or write functional application code (Python, JS, Go, etc.) in this repository.
  -> **Do** write structured framework-specific SOPs and reusable Markdown templates only.
- **Don't** edit `system-prompt.md` without updating the version identifier.
  -> **Do** increment the version in the prompt, update `STATE.md`, and log a formal entry in `CHANGELOG.md`.
- **Don't** read `context-reports/` markdown files yourself.
  -> **Do** generate them using the MCP server and hand the file path to the Manager.

## Documentation Sync Rules

When modifying this repository, you must keep these files synchronized:

1. `STATE.md` (architectural state and completed features)
2. `TODO.md` (roadmap backlog)
3. `CHANGELOG.md` (Keep a Changelog format)
