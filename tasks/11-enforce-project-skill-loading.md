# Task: Enforce Project Skill Loading in System Prompt

**Type:** improvement
**Status:** open

## Goal

Add a general rule to `system-prompt.md` that instructs OpenCode to always discover and load any relevant local Agent Skills (e.g., bootstrap, spring-boot, android-kotlin, vue-nuxt, react-vite) before executing tasks. Skills are optional per project, but if they exist they MUST be loaded.

## Manager's Notes

- A project may have zero, one, or multiple skills (e.g., one for backend + one for frontend)
- Skills live in `.opencode/skills/<name>/SKILL.md` or `skill-templates/<name>/SKILL.md`
- The rule must apply across all task types (discovery + implementation)

## Local TODOs

- [x] Initial codebase exploration
- [x] Increment `<system_version>` from 5.4.1 to 5.6.0
- [x] Add Mandatory Project Skill Loading constraint to `<constraints>`
- [x] Update discovery task `<context_phase>` with SKILL LOADING instruction
- [x] Update implementation task `<context_phase>` with SKILL LOADING instruction
- [x] Create this task file
- [x] Update CHANGELOG.md
- [x] Verify formatting

## OpenCode Execution Log & Reasoning

The system prompt had no explicit instruction telling OpenCode to discover and load project-specific Agent Skills during task execution. This meant that even when a project ships a `SKILL.md` for bootstrap, spring-boot, or android-kotlin, OpenCode would not automatically load it unless the Orchestrator happened to remember to mention it.

I added three things:

1. A new constraint under `<constraints>` — mandatory rule that OpenCode must scan `.opencode/skills/` and `skill-templates/` for matching skills on every task.
2. A `SKILL LOADING` block in the discovery task template's `<context_phase>` — ensures skills are loaded during exploration.
3. A `SKILL LOADING` block in the implementation task template's `<context_phase>` — ensures skills are loaded before code generation.

Version bumped 5.4.1 → 5.6.0 (minor - new workflow rule).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/AGENTS.md b/AGENTS.md
index d5181cc..f2882d1 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -28,14 +28,18 @@ When modifying this repository, you must keep these files synchronized:
 4. Relevant `SKILL.md` files (if structural patterns were altered)
 
 ## 🛑 CORE FILE LOCATIONS
+
 You MUST strictly adhere to these exact paths. Do not create duplicates elsewhere:
+
 - **Global Rules:** `AGENTS.md` (Root)
 - **UI/UX Specs:** `DESIGN.md` (Root)
 - **Agent Skills:** `.opencode/skills/<skill-name>/SKILL.md` (Local workspace)
 - **Active Tasks:** `tasks/<task-number>-<name>.md`
 
 ## 🛑 MANDATORY END-OF-TASK SEQUENCE
+
 When finishing a task, you MUST execute these exact steps in order:
+
 1. **Write your Summary:** Manually write your architectural reasoning, local TODO checks, and execution notes into the active `tasks/XX-task.md` file under "OpenCode Execution Log".
 2. **Call MCP Tool:** Call the `custom_context_stage_and_inject_diff` MCP tool passing the task file path to automatically `git add .` and inject the factual code diff.
 3. **Notify Manager:** Output exactly: "Task ready. Manager, please copy the contents of `tasks/XX-task.md` and send it back to the AI Studio Brain for review."
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 1024154..5f01510 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -132,6 +132,17 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Project Planner persona** in `system-prompt.md` — added explicit instruction to load the `task-generator` skill when creating new task files, ensuring the template includes the correct `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers for MCP diff injection.
 
+## [5.6.0] — 2026-06-14
+
+### Added
+
+- **Mandatory Project Skill Loading constraint** in `system-prompt.md` — OpenCode must now discover and load all relevant local Agent Skills (e.g., bootstrap, spring-boot, android-kotlin, vue-nuxt) during every task's context phase. Skills are optional per project but if they exist, they MUST be loaded.
+- **`SKILL LOADING` instruction** in both the discovery task template and implementation task template `<context_phase>` blocks — ensures framework-specific rules are enforced before exploration and code generation.
+
+### Changed
+
+- `<system_version>` bumped from 5.4.1 to 5.6.0.
+
 ## [5.5.0] — 2026-06-08
 
 ### Added
diff --git a/skill-templates/audit-agents/SKILL.md b/skill-templates/audit-agents/SKILL.md
index 999ca30..e1b639d 100644
--- a/skill-templates/audit-agents/SKILL.md
+++ b/skill-templates/audit-agents/SKILL.md
@@ -6,12 +6,15 @@ description: Enforces decentralized task management, UI/UX design strictness, an
 # OpenCode Skill: Agent Protocol Auditor
 
 ## 🛑 STRICT EXECUTION RULES (Priority 1)
+
 1. **Primary Source of Truth**: You MUST read `AGENTS.md` at the project root using local file read tools.
 2. **Read-Only First**: Evaluate the contents of `AGENTS.md` against the Target Audit Criteria before attempting any file modifications.
 3. **Immutable Formatting**: If patching is required, maintain the exact Markdown list structure, headers, and spacing of the existing file.
 
 ## Target Audit Criteria
+
 The `AGENTS.md` file MUST explicitly contain the following operational constraints, ideally within a `Task Management & OpenCode Rules` section:
+
 - **Core File Locations**: MUST explicitly list paths for `AGENTS.md`, `DESIGN.md`, `tasks/`, and `.opencode/skills/`.
 - **Decentralized Task Management**: Agents MUST strictly use decentralized, individual task files in the `tasks/` directory as their single source of truth.
 - **No Monolithic State**: Agents are strictly forbidden from creating `TODO.md` or `STATE.md`.
@@ -19,14 +22,17 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **UI/UX Enforcement**: Any UI/UX changes MUST enforce the guidelines defined in the project's `DESIGN.md`.
 
 ## Resolution Protocol
+
 1. **Evaluation**: Compare the active `AGENTS.md` text against the Target Audit Criteria.
 2. **Patching**: If any constraints are missing, ambiguous, or incorrect, use the `apply_patch` tool to inject the exact missing rules.
 3. **Halt on Success**: If the file already complies 100%, DO NOT execute any write operations.
 
 ## Summary Phase
+
 Upon completion, output a strict, formatted summary for the Manager:
 
 ### Agent Audit Summary
+
 **Audit Status:** [PASSED | FIXED]
 **Violations Found:** [List of missing/incorrect rules, or "None"]
-**Actions Taken:** [Description of the patch applied, or "File already compliant"]
\ No newline at end of file
+**Actions Taken:** [Description of the patch applied, or "File already compliant"]
diff --git a/skill-templates/task-generator/SKILL.md b/skill-templates/task-generator/SKILL.md
index 5b1fe7d..0e2fbe3 100644
--- a/skill-templates/task-generator/SKILL.md
+++ b/skill-templates/task-generator/SKILL.md
@@ -35,11 +35,15 @@ You are the Task Generator. Your job is to create structured task files for the
    - [ ] Verify functionality
 
    ## OpenCode Execution Log & Reasoning
+
    _(OpenCode: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_
 
    ## Factual Git Diff
+
    <!-- BEGIN_GIT_DIFF -->
-   *(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)*
+
+   _(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_
+
    <!-- END_GIT_DIFF -->
    ```
 
diff --git a/skill-templates/telegram-issue-sync/SKILL.md b/skill-templates/telegram-issue-sync/SKILL.md
index dd54051..d947df5 100644
--- a/skill-templates/telegram-issue-sync/SKILL.md
+++ b/skill-templates/telegram-issue-sync/SKILL.md
@@ -22,6 +22,7 @@ This MCP implementation does **NOT** expose a `topic_id` parameter. All messages
 - **Discovering topics:** Call `telegram_list_topics` with `chat_id`. Returns all forum topics with their `id` and `title`.
 
 - **Sending a message to a specific topic:** You MUST use `telegram_reply_to_message` with `message_id` set to the Topic ID (not `telegram_send_message` — that always lands in the General topic). Example:
+
   ```
   telegram_reply_to_message(chat_id="-1003517558062", message_id=2, text="Hello Apex!")
   ```
@@ -129,6 +130,7 @@ Before processing new candidates, run a backfill audit:
      `gh issue create --title "[Sync] Generated Title" --label "bug|enhancement|improvement" --body "Detailed Body with Crawled Discussion"`
      Extract the GitHub issue number from the output URL.
    - **State Save:** Update `telegram-sync.json` (append to `processed_ids`, update `last_processed_message_id`, add/update `sync_registry` entry with `gh_issue` number).
+
 3. **Non-actionable messages:** All seen messages with IDs between `last_processed_message_id` and max candidate ID that do NOT have target hashtags must also be added to `processed_ids` to prevent re-fetching.
 
 ### Phase 4: Closing the Loop (Completion Telegram Reply)
diff --git a/system-prompt.md b/system-prompt.md
index 9b08db1..cc0e31c 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>5.4.1</system_version>
+<system_version>5.6.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside Google AI Studio (powered by Gemini), acting as an elite software agency orchestrator.
@@ -75,6 +75,7 @@ You are a very strong reasoner and planner. Before taking any action (either gen
   <context_phase>
     OPENCODE INSTRUCTION: You are in DISCOVERY mode. Your goal is to gather context for the Orchestrator.
     CRITICAL: Do NOT use your native `read` or `view_file` tools to output file contents inline. You must use the `custom_context` MCP server tools.
+    SKILL LOADING: Scan `.opencode/skills/` and `skill-templates/` for any `SKILL.md` files. Use the `skill` tool to load every skill that matches the project's tech stack. Skills are optional but if present they MUST be loaded before proceeding.
   </context_phase>
 
   <execution_phase>
@@ -101,6 +102,7 @@ You are a very strong reasoner and planner. Before taking any action (either gen
 <opencode_implementation_task>
   <context_phase>
     OPENCODE INSTRUCTION: Read the active task file in `tasks/` to understand the current goals. Use your native tools (`read`, `glob`, `skill`) to gain context. If the task is massive, delegate exploration to the `@explore` subagent first. Utilize any configured MCP servers if external context is required.
+    SKILL LOADING: Before implementing, scan `.opencode/skills/` and `skill-templates/` for any `SKILL.md` files and use the `skill` tool to load every skill that matches the project's tech stack (e.g., bootstrap, spring-boot, android-kotlin, vue-nuxt, react-vite, nodejs-express, python-fastapi, etc.). A project may have zero or multiple skills — if a relevant `SKILL.md` exists, it MUST be loaded. This ensures framework-specific conventions and architectural rules are enforced during implementation.
   </context_phase>
 
   <execution_phase>
@@ -155,6 +157,7 @@ You are a very strong reasoner and planner. Before taking any action (either gen
   3. **README or internal docs** when the task adds a new module, endpoint, public API, or changes architecture. A single sentence describing purpose, usage, and constraints suffices.
   Be specific in the `<execution_phase>` about which files need documentation and at what level (module docs, function docs, inline). The default expectation is: **every public function/class gets a docstring; every complex block gets a comment; every new module gets a brief README or header comment.**
 - **Workspace Security:** OpenCode is STRICTLY FORBIDDEN from executing terminal commands that modify files outside the current project workspace. Destructive commands (like `rm -rf`) must ONLY target specific, known auto-generated directories (e.g., `dist/`, `build/`, `target/`).
+- **Mandatory Project Skill Loading:** During every task's context phase, OpenCode MUST discover and load all Agent Skills relevant to the project. Scan `.opencode/skills/` and `skill-templates/` for `SKILL.md` files, then use the `skill` tool to load any that match the project's tech stack (e.g., bootstrap, spring-boot, android-kotlin, vue-nuxt, react-vite, etc.). A project may have zero, one, or multiple skills — if a skill file exists, it MUST be loaded. This ensures framework-specific rules, naming conventions, and architectural patterns are always enforced.
 </constraints>
 
 <initialization>
```
<!-- END_GIT_DIFF -->
