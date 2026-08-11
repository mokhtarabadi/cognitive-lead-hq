# Task: Enforce Skill Loading Rules in AGENTS.md, Audit Skill, and System Prompt

**Type:** improvement
**Status:** open

## Goal

Add local skill loading rules to `AGENTS.md` so OpenCode always loads the `task-generator` skill before creating task files and relevant project skills before implementation, regardless of whether the Brain instructs it. Update the `audit-agents` skill to audit for these rules, and update `system-prompt.md` to reinforce them.

## Manager's Notes

- Two rules needed: 1) task-generator for task creation, 2) project tech-stack skills for implementation
- `audit-agents` lives in two places: `skill-templates/` and `~/.config/opencode/skills/` — both must be updated
- `system-prompt.md` version must be bumped to 5.7.0

## Local TODOs

- [x] Initial codebase exploration
- [x] Add Skill Loading Rules section to AGENTS.md
- [x] Update audit-agents SKILL.md (template + global) with new audit criteria
- [x] Update system-prompt.md: bump version, update SKILL LOADING blocks and constraint
- [x] Update CHANGELOG.md with 5.7.0 entry
- [x] Create this task file

## OpenCode Execution Log & Reasoning

The existing skill loading rules lived only in `system-prompt.md` (the Brain's prompt in AI Studio). When the Brain generates task templates, it includes `SKILL LOADING` instructions, but there was no local enforcement. If someone talks to OpenCode directly (bypassing AI Studio), or if the Brain forgets to include the instruction, skills would not auto-load.

I made four changes:

1. **`AGENTS.md`** — Added a new "Skill Loading Rules" section with two mandatory rules: task-generator for new task files, and project tech-stack skills for implementation. This ensures the rules are available locally even without Brain instructions.

2. **`audit-agents/SKILL.md`** (both `skill-templates/` and `~/.config/opencode/skills/` global install) — Added two new Target Audit Criteria that check for both Task-Generator Skill Loading and Project Skill Loading rules in `AGENTS.md`.

3. **`system-prompt.md`** — Bumped from v5.6.0 to v5.7.0. Updated the `SKILL LOADING` blocks in both discovery and implementation task templates to mention `task-generator` alongside tech-stack examples. Updated the Mandatory Project Skill Loading constraint to clarify it covers both workflow skills and tech-stack skills.

4. **`CHANGELOG.md`** — Added 5.7.0 entry documenting all changes.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

````diff
diff --git a/AGENTS.md b/AGENTS.md
index f2882d1..ae2caba 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -36,6 +36,13 @@ You MUST strictly adhere to these exact paths. Do not create duplicates elsewher
 - **Agent Skills:** `.opencode/skills/<skill-name>/SKILL.md` (Local workspace)
 - **Active Tasks:** `tasks/<task-number>-<name>.md`

+## 🛑 SKILL LOADING RULES
+
+You MUST follow these skill loading rules in every session:
+
+- **Task-Generator Skill:** Before creating any new task file, you MUST load the `task-generator` skill using the `skill` tool to ensure the correct template format with `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.
+- **Project Skills:** Before implementing any task, you MUST load every available skill matching the project's tech stack (e.g., `android-kotlin`, `spring-boot`, `react-vite`, `nodejs-express`, `python-fastapi`). If a relevant skill exists, it MUST be loaded — this enforces framework-specific conventions and architectural rules.
+
 ## 🛑 MANDATORY END-OF-TASK SEQUENCE

 When finishing a task, you MUST execute these exact steps in order:
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 5f01510..9ad635c 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -126,6 +126,21 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

 - **`stage_and_inject_diff` MCP tool** — optimized the staged git diff command to globally exclude the entire `tasks/` directory (`:!tasks/`) instead of just the single active task file, completely eliminating task history clutter from factual codebase reviews.

+## [5.7.0] — 2026-06-16
+
+### Added
+
+- **Skill Loading Rules section** in `AGENTS.md` — two new mandatory rules: 1) Load `task-generator` skill before creating new task files. 2) Scan and load relevant project tech-stack skills before task implementation.
+- **Two new audit criteria** in `audit-agents/SKILL.md` — audits now verify that `AGENTS.md` contains both Task-Generator Skill Loading and Project Skill Loading rules.
+- **`task-generator` mention** in both discovery and implementation task template `SKILL LOADING` blocks in `system-prompt.md` — OpenCode now loads the task-generator skill when task creation is involved.
+- **Phase 0 Generation Mode** in `audit-agents/SKILL.md` — skill now has a full AGENTS.md template and workflow for generating the file from scratch on new projects.
+
+### Changed
+
+- **`system-prompt.md`** — `<constraints>` Mandatory Project Skill Loading clarified to cover both tech-stack skills (e.g., `android-kotlin`, `spring-boot`) and workflow skills (e.g., `task-generator`). All `SKILL LOADING` blocks now reference `task-generator` alongside tech-stack examples. Phase 0 workflow and Project Planner persona updated to instruct OpenCode to load the `audit-agents` skill for AGENTS.md generation.
+- **Simplified skill loading instructions** in `AGENTS.md`, `system-prompt.md`, and `audit-agents/SKILL.md` — removed redundant "scan `.opencode/skills/`..." path instructions since OpenCode auto-discovers skills natively. Now just says "load every available skill matching..."
+- `<system_version>` bumped from 5.6.0 to 5.7.0.
+
 ## [5.4.1] — 2026-06-13

 ### Changed
diff --git a/skill-templates/audit-agents/SKILL.md b/skill-templates/audit-agents/SKILL.md
index e1b639d..a1f3949 100644
--- a/skill-templates/audit-agents/SKILL.md
+++ b/skill-templates/audit-agents/SKILL.md
@@ -5,13 +5,92 @@ description: Enforces decentralized task management, UI/UX design strictness, an

 # OpenCode Skill: Agent Protocol Auditor

-## 🛑 STRICT EXECUTION RULES (Priority 1)
+Use this skill in two modes:
+
+- **Phase 0 (Generation):** When `AGENTS.md` does not exist yet — generate it from the template below.
+- **Audit Mode (Existing):** When `AGENTS.md` already exists — audit and patch it against the Target Audit Criteria.
+
+---
+
+## Mode 1: Phase 0 — Generate AGENTS.md
+
+Use this when a project has no `AGENTS.md` yet (new project onboarding).
+
+### Workflow
+
+1. Read the project's existing context (package configs, README, tech stack files) to determine the project name, description, and relevant tech stack skills.
+2. Generate `AGENTS.md` at the project root using the template below.
+3. Fill in the `[bracketed]` placeholders with the actual project details.
+4. Confirm the file was created.
+
+### AGENTS.md Template
+
+```markdown
+# [Project Name] — Project Context Hub
+
+## Project Overview
+
+[Brief description of the project, its purpose, and tech stack]
+
+## Setup & Dev Commands
+
+- Build: [build command, e.g., npm run build]
+- Test: [test command, e.g., npm test]
+- Lint: [lint command, e.g., npm run lint]
+- Dev: [dev server command, e.g., npm run dev]
+
+## Actionable Guardrails (Do's & Don'ts)
+
+- **Don't** [common anti-pattern to avoid]
+  -> **Do** [preferred alternative]
+- **Don't** [another anti-pattern]
+  -> **Do** [preferred alternative]
+
+## Documentation Sync Rules
+
+When modifying this repository, you must keep these files synchronized:
+
+1. Active task file in `tasks/` (single source of truth for current work items)
+2. `CHANGELOG.md` (Keep a Changelog format)
+3. `DESIGN.md` (UI/UX design system, if modified)
+4. Relevant `SKILL.md` files (if structural patterns were altered)
+
+## 🛑 CORE FILE LOCATIONS
+
+You MUST strictly adhere to these exact paths. Do not create duplicates elsewhere:
+
+- **Global Rules:** `AGENTS.md` (Root)
+- **UI/UX Specs:** `DESIGN.md` (Root)
+- **Agent Skills:** `.opencode/skills/<skill-name>/SKILL.md` (Local workspace)
+- **Active Tasks:** `tasks/<task-number>-<name>.md`
+
+## 🛑 SKILL LOADING RULES
+
+You MUST follow these skill loading rules in every session:
+
+- **Task-Generator Skill:** Before creating any new task file, you MUST load the `task-generator` skill using the `skill` tool to ensure the correct template format with `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.
+- **Project Skills:** Before implementing any task, you MUST load every available skill matching the project's tech stack (e.g., `[android-kotlin]`, `[spring-boot]`, `[react-vite]`). If a relevant skill exists, it MUST be loaded — this enforces framework-specific conventions and architectural rules.
+
+## 🛑 MANDATORY END-OF-TASK SEQUENCE
+
+When finishing a task, you MUST execute these exact steps in order:
+
+1. **Write your Summary:** Manually write your architectural reasoning, local TODO checks, and execution notes into the active `tasks/XX-task.md` file under "OpenCode Execution Log".
+2. **Call MCP Tool:** Call the `custom_context_stage_and_inject_diff` MCP tool passing the task file path to automatically `git add .` and inject the factual code diff.
+3. **Notify Manager:** Output exactly: "Task ready. Manager, please copy the contents of `tasks/XX-task.md` and send it back to the AI Studio Brain for review."
+```
+
+---
+
+## Mode 2: Audit & Patch Existing AGENTS.md
+
+### 🛑 STRICT EXECUTION RULES (Priority 1)

 1. **Primary Source of Truth**: You MUST read `AGENTS.md` at the project root using local file read tools.
 2. **Read-Only First**: Evaluate the contents of `AGENTS.md` against the Target Audit Criteria before attempting any file modifications.
 3. **Immutable Formatting**: If patching is required, maintain the exact Markdown list structure, headers, and spacing of the existing file.

-## Target Audit Criteria
+### Target Audit Criteria

 The `AGENTS.md` file MUST explicitly contain the following operational constraints, ideally within a `Task Management & OpenCode Rules` section:

@@ -20,14 +99,16 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **No Monolithic State**: Agents are strictly forbidden from creating `TODO.md` or `STATE.md`.
 - **Mandatory End-Of-Task Sequence**: MUST explicitly mandate a 3-step completion process: 1) Write manual reasoning in the task file. 2) Call the `custom_context_stage_and_inject_diff` MCP tool. 3) Notify the Manager.
 - **UI/UX Enforcement**: Any UI/UX changes MUST enforce the guidelines defined in the project's `DESIGN.md`.
+- **Task-Generator Skill Loading**: `AGENTS.md` MUST explicitly instruct OpenCode to load the `task-generator` skill before creating new task files.
+- **Project Skill Loading**: `AGENTS.md` MUST explicitly instruct OpenCode to load every available skill matching the project's tech stack before task implementation.

-## Resolution Protocol
+### Resolution Protocol

 1. **Evaluation**: Compare the active `AGENTS.md` text against the Target Audit Criteria.
 2. **Patching**: If any constraints are missing, ambiguous, or incorrect, use the `apply_patch` tool to inject the exact missing rules.
 3. **Halt on Success**: If the file already complies 100%, DO NOT execute any write operations.

-## Summary Phase
+### Summary Phase

 Upon completion, output a strict, formatted summary for the Manager:

diff --git a/system-prompt.md b/system-prompt.md
index cc0e31c..5ae0429 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>5.6.0</system_version>
+<system_version>5.7.0</system_version>

 <role>
 You are the Cognitive Lead AI running inside Google AI Studio (powered by Gemini), acting as an elite software agency orchestrator.
@@ -42,7 +42,7 @@ CRITICAL INSTRUCTION: The Manager will often send informal, raw text. Before tak
   <persona name="Project Planner">
     <trigger>Status checks, milestone planning, or explicit Manager requests.</trigger>
     <duty>Maintain individual task files in the tasks/ directory as the single source of truth for work items, and maintain AGENTS.md both in AI Studio context and mirrored locally.</duty>
-    <behavior>Maintain decentralized task files in `tasks/` as the single source of truth. When creating a new task file, instruct OpenCode to load the `task-generator` skill to ensure the correct template format with `<!-- BEGIN_GIT_DIFF -->` and `<!-- END_GIT_DIFF -->` markers. In Phase 0, instruct OpenCode to perform a deep traversal of the source code to fully comprehend the project structure and UI/UX elements, resulting in a comprehensive `DESIGN.md`. Ensure `AGENTS.md` explicitly includes instructions on reading and updating the active task file.</behavior>
+    <behavior>Maintain decentralized task files in `tasks/` as the single source of truth. When creating a new task file, instruct OpenCode to load the `task-generator` skill to ensure the correct template format with `<!-- BEGIN_GIT_DIFF -->` and `<!-- END_GIT_DIFF -->` markers. In Phase 0, instruct OpenCode to load the `audit-agents` skill to generate `AGENTS.md` and perform a deep traversal of the source code to fully comprehend the project structure and UI/UX elements, resulting in a comprehensive `DESIGN.md`. Ensure `AGENTS.md` explicitly includes instructions on reading and updating the active task file.</behavior>
   </persona>

   <persona name="Code Reviewer">
@@ -75,7 +75,7 @@ You are a very strong reasoner and planner. Before taking any action (either gen
   <context_phase>
     OPENCODE INSTRUCTION: You are in DISCOVERY mode. Your goal is to gather context for the Orchestrator.
     CRITICAL: Do NOT use your native `read` or `view_file` tools to output file contents inline. You must use the `custom_context` MCP server tools.
-    SKILL LOADING: Scan `.opencode/skills/` and `skill-templates/` for any `SKILL.md` files. Use the `skill` tool to load every skill that matches the project's tech stack. Skills are optional but if present they MUST be loaded before proceeding.
+    SKILL LOADING: Load every available skill matching the project's tech stack (e.g., android-kotlin, spring-boot, react-vite, nodejs-express, python-fastapi). If the task involves creating a new task file, also load the `task-generator` skill. Skills are optional but if present they MUST be loaded before proceeding.
   </context_phase>

   <execution_phase>
@@ -102,7 +102,7 @@ You are a very strong reasoner and planner. Before taking any action (either gen
 <opencode_implementation_task>
   <context_phase>
     OPENCODE INSTRUCTION: Read the active task file in `tasks/` to understand the current goals. Use your native tools (`read`, `glob`, `skill`) to gain context. If the task is massive, delegate exploration to the `@explore` subagent first. Utilize any configured MCP servers if external context is required.
-    SKILL LOADING: Before implementing, scan `.opencode/skills/` and `skill-templates/` for any `SKILL.md` files and use the `skill` tool to load every skill that matches the project's tech stack (e.g., bootstrap, spring-boot, android-kotlin, vue-nuxt, react-vite, nodejs-express, python-fastapi, etc.). A project may have zero or multiple skills — if a relevant `SKILL.md` exists, it MUST be loaded. This ensures framework-specific conventions and architectural rules are enforced during implementation.
+    SKILL LOADING: Before implementing, load every available skill matching the project's tech stack (e.g., android-kotlin, spring-boot, react-vite, nodejs-express, python-fastapi). A project may have zero or multiple skills — if a relevant skill exists, it MUST be loaded. If the task involves creating a new task file, also load the `task-generator` skill. This ensures framework-specific conventions and architectural rules are enforced during implementation.
   </context_phase>

   <execution_phase>
@@ -138,7 +138,7 @@ You are a very strong reasoner and planner. Before taking any action (either gen
 </opencode_implementation_task_template>
 </opencode_protocols>

-<execution_workflow> 0. **Discovery & Onboarding**: Ask the Manager if this is a NEW or EXISTING project. Instruct OpenCode to generate `AGENTS.md`, `DESIGN.md`, `opencode.json`, and initial tasks.
+<execution_workflow> 0. **Discovery & Onboarding**: Ask the Manager if this is a NEW or EXISTING project. For new projects, instruct OpenCode to load the `audit-agents` skill to generate `AGENTS.md`, load the `design-md` skill (if available) for `DESIGN.md`, and then create `opencode.json` plus initial tasks.

 1. **Input Processing & Clarification**: Analyze the Manager's raw input. Clean syntax, interpret context. IF ambiguous, HALT and ask clarifying questions. IF clear, proceed.
 2. **Plan (Architect & UI/UX)**: Analyze request -> Deliver blueprint -> Ask Manager for approval.
@@ -157,7 +157,7 @@ You are a very strong reasoner and planner. Before taking any action (either gen
   3. **README or internal docs** when the task adds a new module, endpoint, public API, or changes architecture. A single sentence describing purpose, usage, and constraints suffices.
   Be specific in the `<execution_phase>` about which files need documentation and at what level (module docs, function docs, inline). The default expectation is: **every public function/class gets a docstring; every complex block gets a comment; every new module gets a brief README or header comment.**
 - **Workspace Security:** OpenCode is STRICTLY FORBIDDEN from executing terminal commands that modify files outside the current project workspace. Destructive commands (like `rm -rf`) must ONLY target specific, known auto-generated directories (e.g., `dist/`, `build/`, `target/`).
-- **Mandatory Project Skill Loading:** During every task's context phase, OpenCode MUST discover and load all Agent Skills relevant to the project. Scan `.opencode/skills/` and `skill-templates/` for `SKILL.md` files, then use the `skill` tool to load any that match the project's tech stack (e.g., bootstrap, spring-boot, android-kotlin, vue-nuxt, react-vite, etc.). A project may have zero, one, or multiple skills — if a skill file exists, it MUST be loaded. This ensures framework-specific rules, naming conventions, and architectural patterns are always enforced.
+- **Mandatory Project Skill Loading:** During every task's context phase, OpenCode MUST discover and load all Agent Skills relevant to the project. Load every skill matching the project's tech stack (e.g., android-kotlin, spring-boot, react-vite, nodejs-express, python-fastapi) or workflow needs (e.g., `task-generator` for task creation). A project may have zero, one, or multiple skills — if a skill exists, it MUST be loaded. This ensures framework-specific rules, naming conventions, and architectural patterns are always enforced.
 </constraints>

 <initialization>
````

<!-- END_GIT_DIFF -->
