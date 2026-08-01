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
   - Source (from the `**Source:**` metadata line)
   - OpenCode Execution Log (architectural reasoning)
   - Key files modified

3. **Generate a milestone summary** at `docs/history/milestone-X-summary.md` with the following structure:

   ```markdown
   # Milestone X Summary

   **Date:** YYYY-MM-DD
   **Tasks Compacted:** N

   ## Source Distribution

   | Source       | Count |
   | ------------ | ----- |
   | orchestrator | N     |
   | telegram     | N     |
   | manager      | N     |

   ## Architectural Changes

   [Dense summary of all architectural changes across the milestone]

   ## Files Modified

   | File         | Change      |
   | ------------ | ----------- |
   | path/to/file | description |

   ## Individual Task Summaries

   ### Task XX: Title

   - **Type:** bug|improvement|feature
   - **Source:** [orchestrator|telegram|manager]
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

6. **Memory Validation:** After compacting tasks, audit the project memory bank for stale or superseded entries:
   a. Call `list_namespaces` to enumerate all memory namespaces.
   b. For each namespace, call `search_memory` using keywords from the archived tasks.
   c. Identify memories that reference archived/completed task files or superseded workflows.
   d. Detect duplicates: if two memories in the same namespace cover the same topic and one references a newer date or task, flag the older one as superseded.
   e. Output a `## Stale Memory Report` listing all flagged memories with their namespace, key, and reason for flagging.
   f. Wait for Manager approval before calling `delete_memory` on any flagged entry. NEVER auto-delete memories without explicit Manager confirmation.

7. **Stage the new summary and moved files**:

```bash
git add docs/history/ tasks/archive/
```

## When to Run

Run this skill at the end of each milestone or when `tasks/completed/` contains more than 20 files. The milestone number should be determined by reading the highest existing milestone in `docs/history/` and incrementing by one.
