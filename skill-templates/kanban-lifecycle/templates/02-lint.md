## Part 2: Task Lint Skill (from `task-lint`)

# Task Lint Skill

## When to Run

1. **After Part 1 creates a new task file** — validate structure before handing to Orchestrator.
2. **Before closing a task** — validate the task file is complete and well-formed.
3. **During Part 4 archiving** — validate all tasks before compacting.

## Workflow

1. Call `lint_task_file` with the active task file path.
2. If issues found, report them and HALT.
3. If clean, proceed.

## For Markdown files (non-task)

1. Call `lint_markdown` with the file path.
2. Report issues.

---

