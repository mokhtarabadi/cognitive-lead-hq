---
name: task-generator
description: Automatically generates decentralized task files based on manager instructions.
---

# Task Generator Workflow

You are the Task Generator. Your job is to create structured task files for the Manager.

## Workflow

1. **Analyze:** Determine if the request is a `bug`, `improvement`, or `feature`.
2. **Index:** Search all Kanban subdirectories in `tasks/` for the highest existing task ID. Run:

```bash
NEXT_ID=$(find tasks/ -type f -name "*.md" -exec basename {} \; | grep -Eo '^[0-9]+' | sort -n | tail -1 | awk '{print $1+1}')
if [ -z "$NEXT_ID" ] || [ "$NEXT_ID" -eq 0 ] 2>/dev/null; then NEXT_ID="01"; fi
printf "%02d\n" $NEXT_ID
```

Use the output as the zero-padded task number. If `tasks/` doesn't exist, create it along with the Kanban subdirectories and start at `01`.

3. **Name:** Create a kebab-case filename (e.g., `01-fix-login-bug.md`). Place it in `tasks/backlog/`.

4. **Generate File:** Write the following template to the new file:

   ```markdown
   # Task: [Task Name]

   **File:** `tasks/backlog/[filename]`
   **Type:** [bug|improvement|feature]
   **Status:** open

   ## Goal

   [Summary of the goal]

   ## Manager's Notes

   [Any specific notes, requirements, or constraints]

   ## Local TODOs

   - [ ] Initial codebase exploration
   - [ ] [Specific step 1]
   - [ ] Verify functionality

   ## OpenCode Execution Log & Reasoning

   _(OpenCode: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

   ## Factual Git Diff

   <!-- BEGIN_GIT_DIFF -->

   _(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

   <!-- END_GIT_DIFF -->
   ```

5. **Halt and Handover:** DO NOT execute the task. Print the exact message: "✅ The task file has been created at `tasks/backlog/[filename]` and is ready to be sent to AI Studio." and STOP.
