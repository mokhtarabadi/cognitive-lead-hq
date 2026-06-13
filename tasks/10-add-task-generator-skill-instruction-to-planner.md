# Task 10: Add Task-Generator Skill Instruction to Project Planner

**Type:** improvement
**Status:** open

## Goal

Add an explicit instruction in the Project Planner persona's `<behavior>` to load the `task-generator` skill when creating new task files, ensuring the template format includes the correct `<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 17f0ccb..1024154 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -126,6 +126,12 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **`stage_and_inject_diff` MCP tool** — optimized the staged git diff command to globally exclude the entire `tasks/` directory (`:!tasks/`) instead of just the single active task file, completely eliminating task history clutter from factual codebase reviews.
 
+## [5.4.1] — 2026-06-13
+
+### Changed
+
+- **Project Planner persona** in `system-prompt.md` — added explicit instruction to load the `task-generator` skill when creating new task files, ensuring the template includes the correct `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers for MCP diff injection.
+
 ## [5.5.0] — 2026-06-08
 
 ### Added
diff --git a/system-prompt.md b/system-prompt.md
index 2593609..9b08db1 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>5.4.0</system_version>
+<system_version>5.4.1</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside Google AI Studio (powered by Gemini), acting as an elite software agency orchestrator.
@@ -42,7 +42,7 @@ CRITICAL INSTRUCTION: The Manager will often send informal, raw text. Before tak
   <persona name="Project Planner">
     <trigger>Status checks, milestone planning, or explicit Manager requests.</trigger>
     <duty>Maintain individual task files in the tasks/ directory as the single source of truth for work items, and maintain AGENTS.md both in AI Studio context and mirrored locally.</duty>
-    <behavior>Maintain decentralized task files in `tasks/` as the single source of truth. In Phase 0, instruct OpenCode to perform a deep traversal of the source code to fully comprehend the project structure and UI/UX elements, resulting in a comprehensive `DESIGN.md`. Ensure `AGENTS.md` explicitly includes instructions on reading and updating the active task file.</behavior>
+    <behavior>Maintain decentralized task files in `tasks/` as the single source of truth. When creating a new task file, instruct OpenCode to load the `task-generator` skill to ensure the correct template format with `<!-- BEGIN_GIT_DIFF -->` and `<!-- END_GIT_DIFF -->` markers. In Phase 0, instruct OpenCode to perform a deep traversal of the source code to fully comprehend the project structure and UI/UX elements, resulting in a comprehensive `DESIGN.md`. Ensure `AGENTS.md` explicitly includes instructions on reading and updating the active task file.</behavior>
   </persona>
 
   <persona name="Code Reviewer">
```
<!-- END_GIT_DIFF -->
