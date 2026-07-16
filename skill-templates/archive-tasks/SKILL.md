---
name: archive-tasks
description: Milestone compaction skill — scans completed tasks, generates dense history summaries, and moves them to the archive.
---

# Archive Tasks Skill

## Purpose

Prevents the `tasks/completed/` directory from accumulating hundreds of task files by periodically compacting completed tasks into dense, single-file milestone summaries in `docs/history/`.

## Workflow

1. **Scan completed tasks** for the current milestone:

```bash
ls tasks/completed/*.md 2>/dev/null
```

2. **Read each file** and extract:
   - Task number and title
   - Type (bug/improvement/feature)
   - OpenCode Execution Log (architectural reasoning)
   - Key files modified

3. **Generate a milestone summary** at `docs/history/milestone-X-summary.md` with the following structure:

   ```markdown
   # Milestone X Summary

   **Date:** YYYY-MM-DD
   **Tasks Compacted:** N

   ## Architectural Changes

   [Dense summary of all architectural changes across the milestone]

   ## Files Modified

   | File         | Change      |
   | ------------ | ----------- |
   | path/to/file | description |

   ## Individual Task Summaries

   ### Task XX: Title

   - **Type:** bug|improvement|feature
   - **Reasoning:** [condensed execution log]
   ```

4. **Create the `docs/history/` directory** if it does not exist:

```bash
mkdir -p docs/history
```

5. **Move completed files to archive**:

```bash
mv tasks/completed/*.md tasks/archive/
```

6. **Stage the new summary and moved files**:

```bash
git add docs/history/ tasks/archive/
```

## When to Run

Run this skill at the end of each milestone or when `tasks/completed/` contains more than 20 files. The milestone number should be determined by reading the highest existing milestone in `docs/history/` and incrementing by one.
