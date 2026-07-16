---
name: migrate-kanban
description: Migrates a flat tasks/ directory into the V6 Kanban folder structure (backlog, in-progress, qa, completed, archive).
---

# Migrate Kanban Skill

## Purpose

Transforms a flat `tasks/` directory (e.g., `tasks/01-task.md`, `tasks/02-task.md`) into the state-based V6 Kanban lifecycle structure:

- `tasks/backlog/` — Open / unstarted tasks
- `tasks/in-progress/` — Currently being worked on
- `tasks/qa/` — Awaiting review / quality assurance
- `tasks/completed/` — Finished tasks
- `tasks/archive/` — Milestone-compacted historical tasks

## Workflow

1. **Create the 5 Kanban directories** if they do not already exist:

```bash
mkdir -p tasks/backlog tasks/in-progress tasks/qa tasks/completed tasks/archive
```

2. **Scan all `.md` files** in the flat `tasks/` root (excluding the Kanban subdirectories):

```bash
find tasks/ -maxdepth 1 -type f -name "*.md" | sort
```

3. **Classify each file** by reading its frontmatter or first line:

   - If the file contains `Status: open` (or `**Status:** open`), move it to `tasks/backlog/`.
   - If the file contains `Status: closed` (or `**Status:** closed`), move it to `tasks/completed/`.
   - If no status is found, default to `tasks/backlog/`.

4. **Move the files** using `git mv` to preserve history:

```bash
for f in tasks/*.md; do
  [ -e "$f" ] || continue
  [ "$f" = "tasks/README.md" ] && continue
  if grep -qi "Status: open" "$f" 2>/dev/null; then
    git mv "$f" tasks/backlog/
  elif grep -qi "Status: closed" "$f" 2>/dev/null; then
    git mv "$f" tasks/completed/
  else
    git mv "$f" tasks/backlog/
  fi
done
```

5. **Verify** the migration:

```bash
echo "=== Backlog ===" && ls tasks/backlog/
echo "=== Completed ===" && ls tasks/completed/
```

6. **Update AGENTS.md** to reference the Kanban directory structure in the "Core File Locations" and "Documentation Sync Rules" sections.

## Post-Migration

After running this skill, the flat `tasks/` directory should be empty (except for the 5 Kanban subdirectories). All existing task history is preserved via `git mv`.
