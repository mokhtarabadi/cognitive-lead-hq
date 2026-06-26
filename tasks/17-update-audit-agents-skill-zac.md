# Task 17: Update Audit-Agents Skill for ZAC Workflow

**Type:** improvement
**Status:** closed

## Goal

Update the `audit-agents` skill template (`skill-templates/audit-agents/SKILL.md`) to enforce the Zero-Autonomous-Commit (ZAC) workflow rules across all three sections: Target Audit Criteria, AGENTS.md Template (Guardrails & End-Of-Task Sequence), and Mode 2 Audit Criteria.

## Manager's Notes

- Add ZAC criterion to both Target Audit Criteria blocks (Phase 0 and Mode 2).
- Update Mandatory End-Of-Task Sequence audit criterion in both blocks to say "NO COMMITS ALLOWED".
- Add Git guardrails to the AGENTS.md template's Actionable Guardrails section.
- Update the template's End-Of-Task Sequence step 3 to forbid `git commit`.
- Update CHANGELOG.md with an entry.

## Local TODOs

- [x] Create Task 17 file
- [x] Add ZAC criterion and update End-Of-Task Sequence in both Target Audit Criteria blocks
- [x] Add Git guardrails to AGENTS.md template Actionable Guardrails
- [x] Update template's End-Of-Task Sequence step 3
- [x] Update CHANGELOG.md
- [ ] Call custom_context_stage_and_inject_diff MCP tool

## OpenCode Execution Log & Reasoning

### Architectural Reasoning

This task propagates the Zero-Autonomous-Commit (ZAC) workflow into the `audit-agents` skill template, ensuring that any project scaffolded or audited by this skill will inherit the ZAC rules. Three locations required updates:

1. **Target Audit Criteria (x2):** Both the Phase 0 audit criteria and the Mode 2 audit criteria now include a `Zero-Autonomous-Commit` criterion and the End-Of-Task Sequence criterion now explicitly says "NO COMMITS ALLOWED".
2. **AGENTS.md Template Guardrails:** Added the two Git prohibition guardrails (`Don't execute Git commands...` / `Do rely on MCP tool...`) to the scaffolded template.
3. **AGENTS.md Template End-Of-Task Sequence:** Step 3 updated to match the live `AGENTS.md` — "automatically stage the files" instead of "automatically `git add .`", and "DO NOT execute any `git commit` commands afterward."

### Execution Notes

- Edited `skill-templates/audit-agents/SKILL.md` — applied patches to all three sections.
- Updated `CHANGELOG.md` with an [Unreleased] entry.
- Created `tasks/17-update-audit-agents-skill-zac.md` as the active task file.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 6b630ca..e3082d3 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -127,6 +127,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Zero-Autonomous-Commit (ZAC) Workflow:** Enforced strict separation of code staging from committing. OpenCode is now forbidden from running `git add`, `git commit`, or `git stash` during implementation (CRITICAL RULE 3). Staging is handled exclusively by the `custom_context_stage_and_inject_diff` MCP tool.
 - **Reviewer-Driven Commit Cycle:** Code Reviewer persona now generates commit tasks on `APPROVED` status and fix-loop implementation tasks on `REJECTED_NEEDS_FIXES` status, completing the review loop.
 - **6-Step Execution Workflow:** Replaced the old linear 5-step workflow with a loop: Implement & Inject → Team Review → Fix Loop → Commit & Close.
+- **Audit-Agents ZAC Propagation:** Updated `skill-templates/audit-agents/SKILL.md` to enforce the Zero-Autonomous-Commit (ZAC) workflow in newly scaffolded or audited projects — ZAC criterion added to both Target Audit Criteria blocks, Git guardrails added to the AGENTS.md template, and End-Of-Task Sequence updated.
 
 ### Changed
 
diff --git a/skill-templates/audit-agents/SKILL.md b/skill-templates/audit-agents/SKILL.md
index 1838e9d..ddf9cb9 100644
--- a/skill-templates/audit-agents/SKILL.md
+++ b/skill-templates/audit-agents/SKILL.md
@@ -13,7 +13,8 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **Core File Locations**: MUST explicitly list paths for `AGENTS.md`, `DESIGN.md`, `tasks/`, and `.opencode/skills/`.
 - **Decentralized Task Management**: Agents MUST strictly use decentralized, individual task files in the `tasks/` directory as their single source of truth.
 - **No Monolithic State**: Agents are strictly forbidden from creating `TODO.md` or `STATE.md`.
-- **Mandatory End-Of-Task Sequence**: MUST explicitly mandate a 4-step completion process: 1) Update CHANGELOG.md. 2) Write manual reasoning in the task file. 3) Call the `custom_context_stage_and_inject_diff` MCP tool. 4) Notify the Manager.
+- **Zero-Autonomous-Commit**: Agents MUST strictly be forbidden from executing `git add`, `git commit`, or `git stash` manually during implementation.
+- **Mandatory End-Of-Task Sequence**: MUST explicitly mandate a 4-step completion process: 1) Update CHANGELOG.md. 2) Write manual reasoning in the task file. 3) Call the `custom_context_stage_and_inject_diff` MCP tool (NO COMMITS ALLOWED). 4) Notify the Manager.
 - **UI/UX Enforcement**: Any UI/UX changes MUST enforce the guidelines defined in the project's `DESIGN.md`.
 - **Task-Generator Skill Loading**: `AGENTS.md` MUST explicitly instruct OpenCode to load the `task-generator` skill before creating new task files.
 - **Project Skill Loading**: `AGENTS.md` MUST explicitly instruct OpenCode to load every available skill matching the project's tech stack before task implementation.
@@ -206,6 +207,8 @@ Use this when a project has no `AGENTS.md` yet (new project onboarding).
   -> **Do** [preferred alternative]
 - **Don't** [another anti-pattern]
   -> **Do** [preferred alternative]
+- **Don't** execute Git commands like `git add`, `git commit`, or `git stash` manually during implementation.
+  -> **Do** rely exclusively on the `custom_context_stage_and_inject_diff` MCP tool to securely stage your working changes.
 
 ## Documentation Sync Rules
 
@@ -238,7 +241,7 @@ When finishing a task, you MUST execute these exact steps in order:
 
 1. **Update Changelog:** You MUST insert a formal entry into CHANGELOG.md logging your modifications.
 2. **Write your Summary:** Manually write your architectural reasoning, local TODO checks, and execution notes into the active `tasks/XX-task.md` file under "OpenCode Execution Log".
-3. **Call MCP Tool:** Call the `custom_context_stage_and_inject_diff` MCP tool passing the task file path to automatically `git add .` and inject the factual code diff.
+3. **Call MCP Tool:** Call the `custom_context_stage_and_inject_diff` MCP tool passing the task file path to automatically stage the files and inject the factual code diff. DO NOT execute any `git commit` commands afterward.
 4. **Notify Manager:** Output exactly: "Task ready. Manager, please copy the contents of `tasks/XX-task.md` and send it back to the AI Studio Brain for review."
 ```
 
@@ -259,7 +262,8 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **Core File Locations**: MUST explicitly list paths for `AGENTS.md`, `DESIGN.md`, `tasks/`, and `.opencode/skills/`.
 - **Decentralized Task Management**: Agents MUST strictly use decentralized, individual task files in the `tasks/` directory as their single source of truth.
 - **No Monolithic State**: Agents are strictly forbidden from creating `TODO.md` or `STATE.md`.
-- **Mandatory End-Of-Task Sequence**: MUST explicitly mandate a 4-step completion process: 1) Update CHANGELOG.md. 2) Write manual reasoning in the task file. 3) Call the `custom_context_stage_and_inject_diff` MCP tool. 4) Notify the Manager.
+- **Zero-Autonomous-Commit**: Agents MUST strictly be forbidden from executing `git add`, `git commit`, or `git stash` manually during implementation.
+- **Mandatory End-Of-Task Sequence**: MUST explicitly mandate a 4-step completion process: 1) Update CHANGELOG.md. 2) Write manual reasoning in the task file. 3) Call the `custom_context_stage_and_inject_diff` MCP tool (NO COMMITS ALLOWED). 4) Notify the Manager.
 - **UI/UX Enforcement**: Any UI/UX changes MUST enforce the guidelines defined in the project's `DESIGN.md`.
 - **Task-Generator Skill Loading**: `AGENTS.md` MUST explicitly instruct OpenCode to load the `task-generator` skill before creating new task files.
 - **Project Skill Loading**: `AGENTS.md` MUST explicitly instruct OpenCode to load every available skill matching the project's tech stack before task implementation.
```
<!-- END_GIT_DIFF -->
