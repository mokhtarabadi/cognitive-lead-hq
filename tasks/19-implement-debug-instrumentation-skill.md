# Task 19: Implement Debug Instrumentation Skill

**Type:** feature
**Status:** closed

## Goal

Create a new `debug-instrumentation` Agent Skill template for diagnosing complex bugs, deadlocks, race conditions, and silent failures via strategic logging and tracing. Also update the `audit-agents` skill to reference it.

## Manager's Notes

- Create `skill-templates/debug-instrumentation/SKILL.md` with the full protocol workflow (Identify Choke Points → Inject Strategic Logs → Execution & Capture → Analyze Runtime Data → Implement Fix & Clean Up).
- Update `skill-templates/audit-agents/SKILL.md` in three places:
  1. Main Target Audit Criteria — add Complex Debugging bullet.
  2. AGENTS.md Template → Actionable Guardrails — add don't/do pair for debug-instrumentation.
  3. Mode 2 Target Audit Criteria — add Complex Debugging bullet.
- Update CHANGELOG.md with a new [Unreleased] Added entry.

## Local TODOs

- [x] Create task file
- [x] Create debug-instrumentation skill
- [x] Update audit-agents skill in 3 places
- [x] Run prettier for formatting
- [x] Update CHANGELOG.md
- [x] Call custom_context_stage_and_inject_diff MCP tool

## OpenCode Execution Log & Reasoning

### Architectural Reasoning

This task introduces a new **debug-instrumentation** Agent Skill that formalizes a systematic debugging protocol. The skill is designed for cases where static analysis is insufficient and runtime visibility is required. The workflow has 5 distinct phases: identifying choke points (locks, transactions, async boundaries), injecting strategic temporary logs, capturing execution output, analyzing the runtime traces, and fixing the bug with cleanup. The audit-agents skill is updated to reference this new skill so that scaffolded AGENTS.md files instruct agents not to guess blindly on complex bugs.

### Execution Notes

- Created `skill-templates/debug-instrumentation/SKILL.md` with the full debugging protocol.
- Edited `skill-templates/audit-agents/SKILL.md`:
  - Added Complex Debugging bullet to the main Target Audit Criteria section.
  - Added don't/do guardrail pair in the AGENTS.md Template's Actionable Guardrails.
  - Added Complex Debugging bullet to Mode 2's Target Audit Criteria section.
- Ran `npx prettier --write "**/*.md"` for formatting.
- Updated CHANGELOG.md under [Unreleased] Added section.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 490f488..0f0cad2 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -129,6 +129,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **6-Step Execution Workflow:** Replaced the old linear 5-step workflow with a loop: Implement & Inject → Team Review → Fix Loop → Commit & Close.
 - **Audit-Agents ZAC Propagation:** Updated `skill-templates/audit-agents/SKILL.md` to enforce the Zero-Autonomous-Commit (ZAC) workflow in newly scaffolded or audited projects — ZAC criterion added to both Target Audit Criteria blocks, Git guardrails added to the AGENTS.md template, and End-Of-Task Sequence updated.
 - **Cognitive Language Rule:** Enforced English-only cognitive reasoning and execution logging across both AI Studio (reasoning_log, blueprints, task generation) and OpenCode (execution logs). Appended future architectural TODOs to README.md.
+- **`skill-templates/debug-instrumentation/SKILL.md`:** new Agent Skill template for diagnosing complex bugs, deadlocks, race conditions, and silent failures via strategic logging and tracing.
+- **`skill-templates/audit-agents/SKILL.md`:** Added Complex Debugging audit criteria referencing the new debug-instrumentation skill to both Target Audit Criteria blocks and the AGENTS.md template guardrails.
 
 ### Changed
 
diff --git a/skill-templates/audit-agents/SKILL.md b/skill-templates/audit-agents/SKILL.md
index ddf9cb9..e7f8fbc 100644
--- a/skill-templates/audit-agents/SKILL.md
+++ b/skill-templates/audit-agents/SKILL.md
@@ -18,6 +18,7 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **UI/UX Enforcement**: Any UI/UX changes MUST enforce the guidelines defined in the project's `DESIGN.md`.
 - **Task-Generator Skill Loading**: `AGENTS.md` MUST explicitly instruct OpenCode to load the `task-generator` skill before creating new task files.
 - **Project Skill Loading**: `AGENTS.md` MUST explicitly instruct OpenCode to load every available skill matching the project's tech stack before task implementation.
+- **Complex Debugging**: Agents MUST be instructed not to guess blindly on complex bugs, but instead utilize the `debug-instrumentation` skill.
 
 ---
 
@@ -209,6 +210,8 @@ Use this when a project has no `AGENTS.md` yet (new project onboarding).
   -> **Do** [preferred alternative]
 - **Don't** execute Git commands like `git add`, `git commit`, or `git stash` manually during implementation.
   -> **Do** rely exclusively on the `custom_context_stage_and_inject_diff` MCP tool to securely stage your working changes.
+- **Don't** guess blindly when facing complex bugs, deadlocks, or silent timeouts.
+  -> **Do** utilize the `debug-instrumentation` skill to inject strategic logs and trace the runtime execution path.
 
 ## Documentation Sync Rules
 
@@ -267,6 +270,7 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **UI/UX Enforcement**: Any UI/UX changes MUST enforce the guidelines defined in the project's `DESIGN.md`.
 - **Task-Generator Skill Loading**: `AGENTS.md` MUST explicitly instruct OpenCode to load the `task-generator` skill before creating new task files.
 - **Project Skill Loading**: `AGENTS.md` MUST explicitly instruct OpenCode to load every available skill matching the project's tech stack before task implementation.
+- **Complex Debugging**: Agents MUST be instructed not to guess blindly on complex bugs, but instead utilize the `debug-instrumentation` skill.
 
 ### Resolution Protocol
 
diff --git a/skill-templates/debug-instrumentation/SKILL.md b/skill-templates/debug-instrumentation/SKILL.md
new file mode 100644
index 0000000..23a967c
--- /dev/null
+++ b/skill-templates/debug-instrumentation/SKILL.md
@@ -0,0 +1,50 @@
+---
+name: debug-instrumentation
+description: Mandatory workflow for diagnosing complex bugs, deadlocks, race conditions, and silent failures via strategic logging and tracing.
+---
+
+# Debug Instrumentation & Tracing Protocol
+
+You are debugging a complex issue (e.g., deadlock, infinite loop, race condition, or silent failure). Standard static analysis has failed or is insufficient. You MUST gain runtime visibility.
+
+**CRITICAL GUARDRAIL:** Do NOT blindly guess the solution. Do NOT attempt to refactor architectural logic without logs proving where the failure occurs.
+
+## Workflow
+
+### 1. Identify Choke Points
+
+Locate the areas of the codebase relevant to the bug. Look for:
+
+- Mutexes, Locks, or synchronized blocks.
+- Database transaction boundaries.
+- Asynchronous boundaries (Promises, Coroutines, Goroutines).
+- Deeply nested loops or recursive calls.
+
+### 2. Inject Strategic Logs (Instrumentation)
+
+Use the `apply_patch` tool to inject temporary, highly visible logging statements into the code.
+
+- Log _before_ and _after_ acquiring a lock or starting a transaction.
+- Log the current thread ID, process ID, or unique request ID.
+- Log variable states at the start and end of loops.
+- Example: `console.log('[DEBUG-TRACE] Attempting to acquire lock A...');`
+
+### 3. Execution & Capture
+
+Run the application, test suite, or specific reproduction script using your `bash` tool.
+
+- Ensure you capture `stdout` and `stderr`.
+- If testing for a deadlock, set a strict timeout on your bash command (e.g., `timeout 10s npm test`) so the agent loop does not hang indefinitely.
+
+### 4. Analyze Runtime Data
+
+Read the captured log output. Look for:
+
+- A "before lock" log that has no matching "after lock" log (Deadlock indicator).
+- Logs arriving out of expected sequential order (Race condition indicator).
+- Repeating log sequences that never terminate (Infinite loop indicator).
+
+### 5. Implement Fix & Clean Up
+
+- Once the root cause is identified from the logs, use `apply_patch` to fix the actual bug.
+- **CRITICAL:** You MUST remove all temporary `[DEBUG-TRACE]` logs you injected before finishing the task. Never commit temporary instrumentation to the codebase.
diff --git a/user-prompts/session-compactor.md b/user-prompts/session-compactor.md
index c2c9c68..27598af 100644
--- a/user-prompts/session-compactor.md
+++ b/user-prompts/session-compactor.md
@@ -32,9 +32,10 @@ Your report MUST strictly follow this exact structure:
 ## 3. Chronological Task Registry & Progress
 
 Provide a detailed table of all tasks handled in this session, matching their current local status:
-| Task Index & Filename | Msg ID (Telegram) | Type | Status (Completed/Todo/Halted) | Core Achievements & Technical Decisions |
-| :--- | :--- | :--- | :--- | :--- |
-| [e.g., tasks/05-xxx.md] | [e.g., 548] | [bug/feature] | Completed | [Brief summary of architectural changes made] |
+
+| Task Index & Filename   | Msg ID (Telegram) | Type          | Status (Completed/Todo/Halted) | Core Achievements & Technical Decisions       |
+| :---------------------- | :---------------- | :------------ | :----------------------------- | :-------------------------------------------- |
+| [e.g., tasks/05-xxx.md] | [e.g., 548]       | [bug/feature] | Completed                      | [Brief summary of architectural changes made] |
 
 ## 4. Codebase Forensic State (Critical & Modified Files)
```
<!-- END_GIT_DIFF -->
