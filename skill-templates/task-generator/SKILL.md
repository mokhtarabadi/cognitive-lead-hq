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

Title consistency check (unified template `# Task [NN]: [Title]`): flag any duplicate title numbers:

```bash
grep -rhn "^# Task [0-9][0-9]*:" tasks/ | sort | uniq -d
```

The title number MUST match the filename ID. Any mismatch or duplicate must be resolved with the Collision Check below before writing the file.

Duplicate ID check — flag any duplicated numeric task IDs across the ACTIVE Kanban directories only:

```bash
find tasks/backlog tasks/in-progress tasks/qa tasks/completed -type f -name "*.md" -exec basename {} \; | grep -Eo '^[0-9]+' | sort | uniq -d
```

If the output is non-empty, HALT and report duplicate task IDs. Do NOT overwrite files. Archive is a historical record and MUST NOT be included in the blocking duplicate-ID check. If archive duplicates are discovered separately, report them as a warning only, never HALT task creation.

3. **Name:** Create a kebab-case filename (e.g., `01-fix-login-bug.md`). Place it in `tasks/backlog/`.

3.5. **Collision Check:** Before writing the file, verify that `tasks/backlog/{NEXT_ID}-*.md` does NOT already exist. Run: `ls tasks/backlog/${NEXT_ID}-*.md 2>/dev/null`. If a file with that ID already exists, HALT and report: '⚠️ Task ID collision: {NEXT_ID} is already in use. Re-run ID discovery.' Do NOT overwrite existing files.

4. **Generate File:** Write the following unified canonical template to the new file. The `## Source Context` section is **polymorphic** — include ONLY the variant block matching the `**Source:**` value. `## Goal`, `## Local TODOs`, `## Acceptance Criteria`, `## Verification Evidence`, and `## Risk & Rollback` are MANDATORY and UNCONDITIONAL for ALL source types (lint contract):

   ```markdown
   # Task [NN]: [Title]

   **File:** `tasks/backlog/[filename]`
   **Source:** [orchestrator|telegram|manager]
   **Type:** [bug|improvement|feature]
   **Status:** open

   ## Source Context

   ### Variant A: Orchestrator (`**Source:** orchestrator`)

   ## Goal

   [Summary of the goal — MANDATORY]

   ## Blueprint Reference

   [Link or reference to the approved architectural blueprint]

   ## Manager's Notes

   [Any specific notes, requirements, or constraints]

   ### Variant B: Telegram (`**Source:** telegram`)

   ## Goal

   [MANDATORY — one-line goal derived from the RAW_TEXT]

   ## Original Message ([Language])

   {RAW_TEXT — verbatim, zero changes}

   ## English Translation

   {EN_TRANSLATION}

   ## Refactored Prompt

   {REFACTORED_PROMPT}

   ## Relevant Code Context

   {CODEBASE_CONTEXT}

   ## AI Analysis & Opinion

   {AI_OPINION}

   ### Variant C: Manager (`**Source:** manager`)

   ## Goal

   [Summary of the goal — MANDATORY]

   ## Manager's Notes

   [Any specific notes, requirements, or constraints]

   <!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

   ## Local TODOs

   - [ ] Initial codebase exploration
   - [ ] [Specific step 1]
   - [ ] Verify functionality

   ## Acceptance Criteria

   - [ ] [Criterion 1 — what must be true for this task to be considered done]
   - [ ] [Criterion 2]

   ## Verification Evidence

   - **Test command:** [exact command]
   - **Expected result:** [what success looks like]
   - **Actual result:** _(The Hands fill this during execution)_
   - **Exit code:** _(The Hands fill this during execution)_

   ## Definition of Done

   The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

   - [ ] Build/Test/Lint pass with exit code 0
   - [ ] `lint_task_file` passes on the active task file
   - [ ] `CHANGELOG.md` updated via Parse-Then-Append
   - [ ] `verification-before-completion` applied and evidence recorded

   ## Risk & Rollback

   - **Risk:** [what could go wrong]
   - **Rollback plan:** [how to undo if needed]

   ---

   ## Execution Log & Reasoning

   _(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

   ## Factual Git Diff

   <!-- BEGIN_GIT_DIFF -->

   _(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

   <!-- END_GIT_DIFF -->
   ```

## Multi-Phase Task Template

If the Orchestrator specifies `multi_phase: true`, generate a SINGLE task file with inline phase sections instead of separate files. Use this structure (same unified metadata header, `## Goal` mandatory):

```markdown
# Task [NN]: [Title]

**File:** `tasks/backlog/[filename]`
**Source:** [orchestrator|telegram|manager]
**Type:** [bug|improvement|feature]
**Status:** open

## Goal

[Summary of the goal]

## Acceptance Criteria

- [ ] [Criterion 1 — what must be true for this task to be considered done]
- [ ] [Criterion 2]

## Verification Evidence

- **Test command:** [exact command]
- **Expected result:** [what success looks like]
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every multi-phase task):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** [what could go wrong]
- **Rollback plan:** [how to undo if needed]

## Phase 1: [Name]

### Local TODOs

- [ ] [Phase 1 step 1]
- [ ] [Phase 1 step 2]

## Phase 2: [Name]

### Local TODOs

- [ ] [Phase 2 step 1]
- [ ] [Phase 2 step 2]

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
```

5. **Halt and Handover:** DO NOT execute the task. Print the exact message: "✅ The task file has been created at `tasks/backlog/[filename]` and is ready to be sent to the Orchestrator." and STOP.
