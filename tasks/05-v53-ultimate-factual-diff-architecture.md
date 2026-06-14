# Task: V5.3 Ultimate Factual Diff Architecture

**Type:** improvement
**Status:** completed

## Goal

Upgrade the system to V5.3.0 Ultimate Architecture by introducing factual Git diff injection via MCP (`stage_and_inject_diff`), structural signature extraction (`extract_signatures`), strict execution guardrails (3-attempt bash failure limit, workspace security), and corresponding documentation updates across all system files.

## Manager's Notes

- Bump `<system_version>` in `system-prompt.md` from `5.2.0` to `5.3.0`.
- Add `import re` and `import subprocess` to `mcp-context-server/server.py`.
- Append two new MCP tools: `extract_signatures` and `stage_and_inject_diff`.
- Append Core File Locations and Mandatory End-Of-Task Sequence blocks to `AGENTS.md`.
- Update audit-agents, task-generator, and code-search SKILL.md templates.
- Apply 6 targeted edits to `system-prompt.md`.
- Sync `.opencode/skills/code-search/SKILL.md` with template changes.
- Add `[5.3.0]` entry to `CHANGELOG.md`.

## Local TODOs

- [x] Initial codebase exploration — read all target files
- [x] Update `mcp-context-server/server.py` — add imports + two new MCP tools
- [x] Update `AGENTS.md` — append anchor blocks
- [x] Update `skill-templates/audit-agents/SKILL.md` — replace Target Audit Criteria
- [x] Update `skill-templates/task-generator/SKILL.md` — replace Step 4 (new template)
- [x] Update `skill-templates/code-search/SKILL.md` — insert Step 2 in Discovery Workflow
- [x] Update `.opencode/skills/code-search/SKILL.md` — sync with template
- [x] Update `system-prompt.md` — 6 specific changes (version, constraint, CR2, doc_phase, summary_phase, reviewer persona)
- [x] Verify Python syntax of MCP server
- [x] Update `CHANGELOG.md` with V5.3.0 entry
- [x] Fix `re.sub` regex escape bug in `stage_and_inject_diff` (lambda instead of backreferences)
- [x] Demonstrate `stage_and_inject_diff` end-to-end on task 04, then clean up
- [x] Fix recursive diff injection — exclude task file from `git diff` via pathspec `:!`
- [x] Fix greedy regex match — use `.*` (greedy) instead of `.*?` (non-greedy) to match first BEGIN to LAST END, preventing corruption when injected diff contains `END_GIT_DIFF`

## OpenCode Execution Log & Reasoning

### Bug Fix: MCP Tool Namespacing (Post-V5.3.0)

OpenCode namespaces MCP tools using the server name as a prefix (e.g., `custom_context_`). The V5.3.0 deployment referenced bare tool names (`get_directory_tree`, `read_source_files`, `stage_and_inject_diff`, `extract_signatures`) which caused tool-calling errors at runtime.

**Fix applied across 5 files:**

- `system-prompt.md` — 3 replacements (discovery + summary templates)
- `AGENTS.md` — 1 replacement (End-Of-Task Sequence)
- `skill-templates/audit-agents/SKILL.md` — 1 replacement
- `skill-templates/code-search/SKILL.md` — 3 replacements
- `.opencode/skills/code-search/SKILL.md` — 3 replacements (synced copy)

### Architectural Reasoning

The V5.3.0 upgrade introduces two new MCP tools on the custom context server:

1. **`extract_signatures`** — Uses regex to extract structural signatures (classes, functions, methods, interfaces, arrow functions) from source files. This prevents context bloat during codebase exploration by letting agents understand file structure without loading full file bodies. Targets Python, JS/TS, Go, and similar languages.

2. **`stage_and_inject_diff`** — Automates the end-of-task finalization sequence: stages all changes via `git add .`, extracts the factual `git diff --staged`, and injects it into the task file's `<!-- BEGIN_GIT_DIFF -->

```diff
diff --git a/.opencode/skills/code-search/SKILL.md b/.opencode/skills/code-search/SKILL.md
index 5fce73b..00dcdb9 100644
--- a/.opencode/skills/code-search/SKILL.md
+++ b/.opencode/skills/code-search/SKILL.md
@@ -11,11 +11,11 @@ You are the Executor. Your job is to extract codebase context so the Manager can

 ## Discovery Workflow

-1. **Map the Structure:** Call the `get_directory_tree` MCP tool on the target directory (e.g., `.`, `src/`, `packages/`).
-2. **Extract Signatures (Prevent Context Bloat):** Before reading full files, call the `extract_signatures` MCP tool on the target files to understand their structural map (classes/functions) without loading massive file bodies.
+1. **Map the Structure:** Call the `custom_context_get_directory_tree` MCP tool on the target directory (e.g., `.`, `src/`, `packages/`).
+2. **Extract Signatures (Prevent Context Bloat):** Before reading full files, call the `custom_context_extract_signatures` MCP tool on the target files to understand their structural map (classes/functions) without loading massive file bodies.
 3. **Target Files:** Analyze the ASCII tree to identify the exact files relevant to the Manager's request.
-4. **Compile Report:** Call the `read_source_files` MCP tool, passing the list of targeted file paths. This tool will safely read the files (respecting `.gitignore`) and compile them into a single Markdown file inside the `context-reports/` directory.
-5. **Halt and Handover:** Once the `read_source_files` tool returns the generated file path, **STOP**. Do NOT use your `read` tool to open the report.
+4. **Compile Report:** Call the `custom_context_read_source_files` MCP tool, passing the list of targeted file paths. This tool will safely read the files (respecting `.gitignore`) and compile them into a single Markdown file inside the `context-reports/` directory.
+5. **Halt and Handover:** Once the `custom_context_read_source_files` tool returns the generated file path, **STOP**. Do NOT use your `read` tool to open the report.
 6. **Output Message:** Output the following exact message to the Manager:
    > "✅ Discovery complete. I have compiled the context report here: `[INSERT_FILE_PATH]`.
    > **Manager:** Please upload this file to AI Studio for the Orchestrator's review."
diff --git a/AGENTS.md b/AGENTS.md
index d037887..d5181cc 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -37,5 +37,5 @@ You MUST strictly adhere to these exact paths. Do not create duplicates elsewher
 ## 🛑 MANDATORY END-OF-TASK SEQUENCE
 When finishing a task, you MUST execute these exact steps in order:
 1. **Write your Summary:** Manually write your architectural reasoning, local TODO checks, and execution notes into the active `tasks/XX-task.md` file under "OpenCode Execution Log".
-2. **Call MCP Tool:** Call the `stage_and_inject_diff` MCP tool passing the task file path to automatically `git add .` and inject the factual code diff.
+2. **Call MCP Tool:** Call the `custom_context_stage_and_inject_diff` MCP tool passing the task file path to automatically `git add .` and inject the factual code diff.
 3. **Notify Manager:** Output exactly: "Task ready. Manager, please copy the contents of `tasks/XX-task.md` and send it back to the AI Studio Brain for review."
diff --git a/skill-templates/audit-agents/SKILL.md b/skill-templates/audit-agents/SKILL.md
index 0ca71aa..999ca30 100644
--- a/skill-templates/audit-agents/SKILL.md
+++ b/skill-templates/audit-agents/SKILL.md
@@ -15,7 +15,7 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **Core File Locations**: MUST explicitly list paths for `AGENTS.md`, `DESIGN.md`, `tasks/`, and `.opencode/skills/`.
 - **Decentralized Task Management**: Agents MUST strictly use decentralized, individual task files in the `tasks/` directory as their single source of truth.
 - **No Monolithic State**: Agents are strictly forbidden from creating `TODO.md` or `STATE.md`.
-- **Mandatory End-Of-Task Sequence**: MUST explicitly mandate a 3-step completion process: 1) Write manual reasoning in the task file. 2) Call the `stage_and_inject_diff` MCP tool. 3) Notify the Manager.
+- **Mandatory End-Of-Task Sequence**: MUST explicitly mandate a 3-step completion process: 1) Write manual reasoning in the task file. 2) Call the `custom_context_stage_and_inject_diff` MCP tool. 3) Notify the Manager.
 - **UI/UX Enforcement**: Any UI/UX changes MUST enforce the guidelines defined in the project's `DESIGN.md`.

 ## Resolution Protocol
diff --git a/skill-templates/code-search/SKILL.md b/skill-templates/code-search/SKILL.md
index 5fce73b..00dcdb9 100644
--- a/skill-templates/code-search/SKILL.md
+++ b/skill-templates/code-search/SKILL.md
@@ -11,11 +11,11 @@ You are the Executor. Your job is to extract codebase context so the Manager can

 ## Discovery Workflow

-1. **Map the Structure:** Call the `get_directory_tree` MCP tool on the target directory (e.g., `.`, `src/`, `packages/`).
-2. **Extract Signatures (Prevent Context Bloat):** Before reading full files, call the `extract_signatures` MCP tool on the target files to understand their structural map (classes/functions) without loading massive file bodies.
+1. **Map the Structure:** Call the `custom_context_get_directory_tree` MCP tool on the target directory (e.g., `.`, `src/`, `packages/`).
+2. **Extract Signatures (Prevent Context Bloat):** Before reading full files, call the `custom_context_extract_signatures` MCP tool on the target files to understand their structural map (classes/functions) without loading massive file bodies.
 3. **Target Files:** Analyze the ASCII tree to identify the exact files relevant to the Manager's request.
-4. **Compile Report:** Call the `read_source_files` MCP tool, passing the list of targeted file paths. This tool will safely read the files (respecting `.gitignore`) and compile them into a single Markdown file inside the `context-reports/` directory.
-5. **Halt and Handover:** Once the `read_source_files` tool returns the generated file path, **STOP**. Do NOT use your `read` tool to open the report.
+4. **Compile Report:** Call the `custom_context_read_source_files` MCP tool, passing the list of targeted file paths. This tool will safely read the files (respecting `.gitignore`) and compile them into a single Markdown file inside the `context-reports/` directory.
+5. **Halt and Handover:** Once the `custom_context_read_source_files` tool returns the generated file path, **STOP**. Do NOT use your `read` tool to open the report.
 6. **Output Message:** Output the following exact message to the Manager:
    > "✅ Discovery complete. I have compiled the context report here: `[INSERT_FILE_PATH]`.
    > **Manager:** Please upload this file to AI Studio for the Orchestrator's review."
diff --git a/system-prompt.md b/system-prompt.md
index b3395ba..5133680 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -79,8 +79,8 @@ You are a very strong reasoner and planner. Before taking any action (either gen

   <execution_phase>
     OPENCODE INSTRUCTION:
-    1. Run the `get_directory_tree` tool on the root directory (`.`).
-    2. Run the `read_source_files` tool on the target files listed below. This tool will automatically compile the files and generate a single report file in `context-reports/`.
+    1. Run the `custom_context_get_directory_tree` tool on the root directory (`.`).
+    2. Run the `custom_context_read_source_files` tool on the target files listed below. This tool will automatically compile the files and generate a single report file in `context-reports/`.

     Target Files to compile:
     [INSERT TARGET FILES HERE]
@@ -125,7 +125,7 @@ You are a very strong reasoner and planner. Before taking any action (either gen

   <summary_phase>
     OPENCODE INSTRUCTION: You MUST follow this exact finalization sequence:
-    1. Call the `stage_and_inject_diff` MCP tool, providing the exact path to the active task file (e.g., `tasks/XX-task-name.md`). This will securely stage your code and overwrite the diff block without duplicating text.
+    1. Call the `custom_context_stage_and_inject_diff` MCP tool, providing the exact path to the active task file (e.g., `tasks/XX-task-name.md`). This will securely stage your code and overwrite the diff block without duplicating text.
     2. Once the tool returns success, you are DONE.
     3. Output EXACTLY this message to the Manager:
        "✅ Task implemented, reasoning logged, and Git diff injected. **Manager:** Please copy the entire contents of `[path/to/task.md]` and send it back to the AI Studio Brain for the final Code Review."
```

<!-- END_GIT_DIFF -->
