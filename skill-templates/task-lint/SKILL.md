---
name: task-lint
description: Validates task files and Markdown documents using the lint MCP server. Run after task creation and before task closure.
---

# Task Lint Skill

## When to Run

1. **After task-generator creates a new task file** — validate structure before handing to Orchestrator.
2. **Before closing a task** — validate the task file is complete and well-formed.
3. **During archive-tasks** — validate all tasks before compacting.

## Workflow

1. Call `lint_task_file` with the active task file path.
2. If issues found, report them and HALT.
3. If clean, proceed.

## For Markdown files (non-task)

1. Call `lint_markdown` with the file path.
2. Report issues.
