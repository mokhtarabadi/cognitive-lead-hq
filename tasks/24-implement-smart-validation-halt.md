# Task: Implement Smart Validation & Halt Protocol

**Type:** feature
**Status:** closed

## Goal

Implement an Agentic Self-Correction Loop where OpenCode validates tasks against project rules and halts with a warning if violations occur.

## Manager's Notes

- Bump `<system_version>` from `5.13.0` to `5.14.0` in `system-prompt.md`.
- Update Senior Programmer `<behavior>` to handle rule violation warnings.
- Insert new CRITICAL TOOL RULE 0 in the implementation task template.
- Add Gatekeeper Validation section to `AGENTS.md`.
- Update `skill-templates/audit-agents/SKILL.md` with Gatekeeper audit criteria and template block.
- Add `[5.14.0]` entry to `CHANGELOG.md`.

## Local TODOs

- [x] Create `tasks/24-implement-smart-validation-halt.md`
- [x] Update `system-prompt.md`: bump version, update Senior Programmer behavior, add CRITICAL TOOL RULE 0
- [x] Update `AGENTS.md`: add Gatekeeper Validation block before CORE FILE LOCATIONS
- [x] Update `skill-templates/audit-agents/SKILL.md`: add Gatekeeper audit criterion and template block
- [x] Update `CHANGELOG.md`: add 5.14.0 entry
- [x] Run prettier to format modified files
- [x] Write execution log in task file and finalize

## OpenCode Execution Log & Reasoning

### Architecture & Reasoning

The goal is to implement a Smart Validation & Halt Protocol — an Agentic Self-Correction Loop — across the entire system. This empowers OpenCode to act as a strict gatekeeper, cross-checking Orchestrator instructions against AGENTS.md, DESIGN.md, and loaded SKILL files before executing any code. If a violation is detected, OpenCode halts immediately and outputs a ⚠️ RULE VIOLATION WARNING, forcing the Orchestrator (AI Studio Brain) to self-correct.

This is a critical safety mechanism that prevents architectural drift and enforces compliance with project rules even when the Orchestrator hallucinates or generates non-compliant instructions.

### Files Modified

1. **`system-prompt.md`**
   - Bumped `<system_version>` from `5.13.0` to `5.14.0`
   - Updated Senior Programmer's `<behavior>` to handle ⚠️ RULE VIOLATION WARNING and self-correction
   - Inserted new CRITICAL TOOL RULE 0 (Rule Validation & Halt Protocol) at the top of the CRITICAL TOOL RULES list in the implementation task template

2. **`AGENTS.md`**
   - Added `## 🛑 GATEKEEPER VALIDATION (HALT PROTOCOL)` block right before `## 🛑 CORE FILE LOCATIONS`

3. **`skill-templates/audit-agents/SKILL.md`**
   - Added `Gatekeeper Validation (Halt Protocol)` to both Target Audit Criteria blocks
   - Inserted the Gatekeeper Validation block into the AGENTS.md Template right before CORE FILE LOCATIONS

4. **`CHANGELOG.md`**
   - Added `[5.14.0] — 2026-07-02` entry with Gatekeeper Protocol features under `### Added`

### Local TODOs

- [x] Create `tasks/24-implement-smart-validation-halt.md`
- [x] Update `system-prompt.md`: bump version, update Senior Programmer behavior, add CRITICAL TOOL RULE 0
- [x] Update `AGENTS.md`: add Gatekeeper Validation block before CORE FILE LOCATIONS
- [x] Update `skill-templates/audit-agents/SKILL.md`: add Gatekeeper audit criterion and template block
- [x] Update `CHANGELOG.md`: add 5.14.0 entry
- [x] Run prettier to format modified files
- [x] Write execution log in task file and finalize

### Verification

- Ran `npx prettier --write "system-prompt.md" "AGENTS.md" "CHANGELOG.md" "skill-templates/audit-agents/SKILL.md"` — all files formatted successfully.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/AGENTS.md b/AGENTS.md
index 38f8848..f5a4342 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -43,6 +43,10 @@ When modifying this repository, you must keep these files synchronized:
 3. `DESIGN.md` (UI/UX design system, if modified)
 4. Relevant `SKILL.md` files (if structural patterns were altered)
 
+## 🛑 GATEKEEPER VALIDATION (HALT PROTOCOL)
+
+You (OpenCode) are the final gatekeeper. Before executing any implementation task, you MUST evaluate the Orchestrator's instructions against this file and any referenced specs (`DESIGN.md`, `architecture.md`, etc.). If the instructions violate project rules, ignore them. HALT immediately and output a `⚠️ RULE VIOLATION WARNING` back to the Manager explaining exactly what the Orchestrator got wrong, forcing it to self-correct.
+
 ## 🛑 CORE FILE LOCATIONS
 
 You MUST strictly adhere to these exact paths. Do not create duplicates elsewhere:
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 5267056..e8aebb5 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -122,6 +122,13 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+## [5.14.0] — 2026-07-02
+
+### Added
+
+- **Agentic Self-Correction Loop (Gatekeeper Protocol):** Empowered OpenCode to act as a strict gatekeeper. OpenCode now cross-checks tasks against `AGENTS.md` and `DESIGN.md`, halting execution and issuing a `⚠️ RULE VIOLATION WARNING` if the AI Studio Orchestrator hallucinates or breaks architectural rules.
+- Updated `audit-agents` skill to enforce the Gatekeeper Protocol on all newly scaffolded projects.
+
 ## [5.13.2] — 2026-06-30
 
 ### Changed
diff --git a/skill-templates/audit-agents/SKILL.md b/skill-templates/audit-agents/SKILL.md
index e7f8fbc..8dbf41e 100644
--- a/skill-templates/audit-agents/SKILL.md
+++ b/skill-templates/audit-agents/SKILL.md
@@ -19,6 +19,7 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **Task-Generator Skill Loading**: `AGENTS.md` MUST explicitly instruct OpenCode to load the `task-generator` skill before creating new task files.
 - **Project Skill Loading**: `AGENTS.md` MUST explicitly instruct OpenCode to load every available skill matching the project's tech stack before task implementation.
 - **Complex Debugging**: Agents MUST be instructed not to guess blindly on complex bugs, but instead utilize the `debug-instrumentation` skill.
+- **Gatekeeper Validation (Halt Protocol)**: Agents MUST be instructed to evaluate tasks against project rules and HALT with a warning if the Orchestrator provides non-compliant instructions.
 
 ---
 
@@ -222,6 +223,10 @@ When modifying this repository, you must keep these files synchronized:
 3. `DESIGN.md` (UI/UX design system, if modified)
 4. Relevant `SKILL.md` files (if structural patterns were altered)
 
+## 🛑 GATEKEEPER VALIDATION (HALT PROTOCOL)
+
+You (OpenCode) are the final gatekeeper. Before executing any implementation task, you MUST evaluate the Orchestrator's instructions against this file and any referenced specs (`DESIGN.md`, `architecture.md`, etc.). If the instructions violate project rules, ignore them. HALT immediately and output a `⚠️ RULE VIOLATION WARNING` back to the Manager explaining exactly what the Orchestrator got wrong, forcing it to self-correct.
+
 ## 🛑 CORE FILE LOCATIONS
 
 You MUST strictly adhere to these exact paths. Do not create duplicates elsewhere:
@@ -271,6 +276,7 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **Task-Generator Skill Loading**: `AGENTS.md` MUST explicitly instruct OpenCode to load the `task-generator` skill before creating new task files.
 - **Project Skill Loading**: `AGENTS.md` MUST explicitly instruct OpenCode to load every available skill matching the project's tech stack before task implementation.
 - **Complex Debugging**: Agents MUST be instructed not to guess blindly on complex bugs, but instead utilize the `debug-instrumentation` skill.
+- **Gatekeeper Validation (Halt Protocol)**: Agents MUST be instructed to evaluate tasks against project rules and HALT with a warning if the Orchestrator provides non-compliant instructions.
 
 ### Resolution Protocol
 
diff --git a/system-prompt.md b/system-prompt.md
index a49e8fe..5514ad1 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>5.13.0</system_version>
+<system_version>5.14.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside Google AI Studio (powered by Gemini), acting as an elite software agency orchestrator.
@@ -22,7 +22,7 @@ The following general-purpose Agent Skills are available. You MUST instruct Open
 - **versioning-and-release**: Standardizes SemVer, Keep a Changelog updates, and Conventional Commits.
 - **debug-instrumentation**: Diagnoses complex runtime bugs, deadlocks, and race conditions via strategic temporary logging.
 - **prompt-refactor**: Meta-cognitive skill that refactors weak human prompts into elite, XML-tagged system instructions.
-</core_workflow_skills>
+  </core_workflow_skills>
 
 <user_input_processing>
 CRITICAL INSTRUCTION: The Manager will often send informal, raw text. Before taking any action or planning, you MUST execute this processing step internally:
@@ -48,7 +48,7 @@ CRITICAL INSTRUCTION: The Manager will often send informal, raw text. Before tak
   <persona name="Senior Programmer">
     <trigger>Approved blueprints/designs or explicit Manager requests.</trigger>
     <duty>Technical implementation lead and "OpenCode Whisperer".</duty>
-    <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. You write strict, comprehensive instructions formatted as an `<opencode_implementation_task>` for the local OpenCode agent to execute. You MUST instruct OpenCode to read AGENTS.md as its very first step, which acts as a router directing the agent to read DESIGN.md, architecture.md, data_model.md, and conventions.md before implementing changes. You do NOT execute code yourself. Wrap the task in a Markdown code block starting with ```xml and ending with ``` so the Manager can copy it with a single click. Instruct OpenCode to leverage its native tools (`lsp`, `grep`, `websearch`, `skill`, MCP servers, and `@explore` subagent) to gain context autonomously.</behavior>
+    <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. You write strict, comprehensive instructions formatted as an `<opencode_implementation_task>` for the local OpenCode agent to execute. You MUST instruct OpenCode to read AGENTS.md as its very first step, which acts as a router directing the agent to read DESIGN.md, architecture.md, data_model.md, and conventions.md before implementing changes. You do NOT execute code yourself. If OpenCode halts and returns a ⚠️ RULE VIOLATION WARNING, you MUST acknowledge the mistake, self-correct your logic based on the project's rules, and generate a flawless revised implementation task. You do NOT execute code yourself. Wrap the task in a Markdown code block starting with ```xml and ending with ``` so the Manager can copy it with a single click. Instruct OpenCode to leverage its native tools (`lsp`, `grep`, `websearch`, `skill`, MCP servers, and `@explore` subagent) to gain context autonomously.</behavior>
   </persona>
 
   <persona name="Project Planner">
@@ -121,6 +121,7 @@ You are a very strong reasoner and planner. Before taking any action (either gen
     OPENCODE INSTRUCTION: Implement the following logic/design based on the approved blueprint.
     [Provide exact logical steps, design tokens, and constraints here. Tell OpenCode WHAT to write and WHERE. Explicitly instruct OpenCode to use the `lsp` tool to verify types/syntax before concluding.
     CRITICAL TOOL RULES:
+    0. **Rule Validation & Halt Protocol:** Before writing any code, cross-check these instructions against AGENTS.md, DESIGN.md, and loaded SKILL files. If the Orchestrator's instructions violate ANY project rules or architectural constraints, you MUST HALT immediately. Do NOT run any bash commands. Output a `⚠️ RULE VIOLATION WARNING` detailing exactly which rule was broken so the Orchestrator can self-correct.
     1. If applying file patches, utilize the `apply_patch` tool with embedded path markers (e.g., `*** Update File: <path>`).
     2. If user feedback is required, utilize the `question` tool with multi-option schemas.
     3. **Documentation Rule:** You MUST write docstrings on all public functions/classes, inline comments on non-obvious logic, and a brief README or header comment for any new module. See `<constraints>` for the full mandate.]
```
<!-- END_GIT_DIFF -->
