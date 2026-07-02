# Task: Mandatory Structural Validation Phase in Every Instruction Block

**Type:** improvement
**Status:** open

## Goal

Fix the gap where AI Studio sometimes skips the AGENTS.md-first-and-every-referenced-file validation check when generating instruction blocks for OpenCode. The existing behavioral instruction in the Senior Programmer persona ("instruct OpenCode to read AGENTS.md as its very first step") was not structurally enforced, allowing the AI to deprioritize it. The fix makes `<validation_phase>` a mandatory structural phase in both task templates.

## Manager's Notes

- Bump `<system_version>` from `5.14.0` to `5.15.0` in `system-prompt.md`.
- Insert `<validation_phase>` as the very first phase in both the discovery and implementation task templates in `system-prompt.md`.
- The validation phase forces OpenCode to: read AGENTS.md -> read every file AGENTS.md references -> cross-check instructions against project rules -> HALT with ⚠️ RULE VIOLATION WARNING if violation found -> proceed to Context Phase only if clear.
- Update CHANGELOG.md with `[5.15.0]` entry.

## Local TODOs

- [x] Bump version in system-prompt.md
- [x] Add `<validation_phase>` to discovery task template
- [x] Add `<validation_phase>` to implementation task template
- [x] Update CHANGELOG.md
- [x] Run prettier to format modified files
- [x] Write execution log and finalize

## OpenCode Execution Log & Reasoning

### Architecture & Reasoning

**Root Cause Analysis:** The system prompt had two layers of instruction:
1. **Behavioral layer** (persona descriptions): The Senior Programmer persona said "You MUST instruct OpenCode to read AGENTS.md as its very first step". The Software Architect persona said "ALWAYS instruct OpenCode to consult AGENTS.md as its very first action."
2. **Structural layer** (templates): Both `<opencode_discovery_task_template>` and `<opencode_implementation_task_template>` started with `<context_phase>` which said "Read the active task file in `tasks/`" or similar — NOT "Read AGENTS.md first."

The gap: When the AI generates task blocks, it closely follows the **structural template** (the actual XML phases). The behavioral layer instructions compete for attention with many other rules. Since the template started with `<context_phase>`, the AI would generate `<context_phase>` first, and the AGENTS.md instruction from the persona behavior was easily deprioritized or forgotten.

**Fix:** Added a new `<validation_phase>` as the **very first structural phase** in both templates. This is not a suggestion — it is a mandatory phase that appears before `<context_phase>` in every generated block. The AI cannot skip it because the template structure explicitly places it first. This is "defense in depth": even if the AI ignores the behavioral instruction, it cannot ignore the template structure.

The existing CRITICAL TOOL RULE 0 in the execution phase is kept as a redundant safety check.

### Files Modified

1. **`system-prompt.md`**
   - Bumped `<system_version>` from `5.14.0` to `5.15.0`
   - Added `<validation_phase>` as first phase in both discovery and implementation task templates

2. **`CHANGELOG.md`**
   - Added `[5.15.0] — 2026-07-02` entry with validation phase details

### Verification

- `npx prettier --write "system-prompt.md" "CHANGELOG.md"` — both files formatted successfully (no changes needed).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index e8aebb5..22f471e 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -122,6 +122,16 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+## [5.15.0] — 2026-07-02
+
+### Added
+
+- **Mandatory Structural Validation Phase:** Injected a new `<validation_phase>` as the very first phase in both the `<opencode_discovery_task>` and `<opencode_implementation_task>` templates. Every generated instruction now starts with reading `AGENTS.md`, then reading every referenced configuration file (`DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, `docs/conventions.md`), cross-checking the Orchestrator's instructions against project rules, and halting with a `⚠️ RULE VIOLATION WARNING` if a violation is found — before any context gathering or execution begins.
+
+### Changed
+
+- **`system-prompt.md`** — `<system_version>` bumped from `5.14.0` to `5.15.0`. Both task templates restructured with `<validation_phase>` as the structural first phase.
+
 ## [5.14.0] — 2026-07-02
 
 ### Added
diff --git a/system-prompt.md b/system-prompt.md
index 5514ad1..7df5777 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>5.14.0</system_version>
+<system_version>5.15.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside Google AI Studio (powered by Gemini), acting as an elite software agency orchestrator.
@@ -84,6 +84,15 @@ You are a very strong reasoner and planner. Before taking any action (either gen
 
 ```xml
 <opencode_discovery_task>
+  <validation_phase>
+    OPENCODE INSTRUCTION (MANDATORY FIRST STEP):
+    1. Read `AGENTS.md` from the project root. This is your non-negotiable entry point.
+    2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md`.
+    3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.
+    4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.
+    5. If no violations are found, proceed to the Context Phase.
+  </validation_phase>
+
   <context_phase>
     OPENCODE INSTRUCTION: You are in DISCOVERY mode. Your goal is to gather context for the Orchestrator.
     CRITICAL: Do NOT use your native `read` or `view_file` tools to output file contents inline. You must use the `custom_context` MCP server tools.
@@ -112,6 +121,15 @@ You are a very strong reasoner and planner. Before taking any action (either gen
 
 ```xml
 <opencode_implementation_task>
+  <validation_phase>
+    OPENCODE INSTRUCTION (MANDATORY FIRST STEP):
+    1. Read `AGENTS.md` from the project root. This is your non-negotiable entry point.
+    2. Read every file that `AGENTS.md` explicitly references as project configuration — `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md`.
+    3. Cross-check the Orchestrator's instructions against all rules, constraints, and architectural guidelines defined in those files.
+    4. If these instructions violate ANY project rule, HALT immediately. Do NOT proceed. Output a `⚠️ RULE VIOLATION WARNING` back to the Manager detailing exactly which rule was broken and the relevant context, so the Orchestrator can self-correct.
+    5. If no violations are found, proceed to the Context Phase.
+  </validation_phase>
+
   <context_phase>
     OPENCODE INSTRUCTION: Read the active task file in `tasks/` to understand the current goals. Use your native tools (`read`, `glob`, `skill`) to gain context. If the task is massive, delegate exploration to the `@explore` subagent first. Utilize any configured MCP servers if external context is required.
     SKILL LOADING: Before implementing, load every available skill matching the project's tech stack (e.g., android-kotlin, spring-boot, react-vite, nodejs-express, python-fastapi). Additionally, consult the <core_workflow_skills> registry and load any general-purpose skills required for this specific task (e.g., debug-instrumentation for bug fixes, versioning-and-release for publishing). If the task involves creating a new task file, load the task-generator skill. A project may have zero or multiple skills — if a relevant skill exists, it MUST be loaded. This ensures framework-specific conventions and architectural rules are enforced during implementation.
```
<!-- END_GIT_DIFF -->
