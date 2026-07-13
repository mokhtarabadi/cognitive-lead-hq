# Task: Micro-Task Checklists & Explicit Skill Orchestration

**File:** `tasks/33-micro-task-checklists-skill-orchestration.md`
**Type:** improvement
**Status:** open

## Goal

Upgrade the system prompt to enforce Micro-Task Checklists (`- [ ]` step tracking) and Explicit Skill Orchestration Routing in the Senior Programmer persona and implementation task templates.

## Manager's Notes

- Add `verification-before-completion` to `<agent_skills_registry>` Global Workflow Skills.
- Add strict skill orchestration and micro-task checklist directive to Senior Programmer persona `<behavior>`.
- Replace `<context_phase>` in implementation template with MANDATORY SKILL ORCHESTRATION block.
- Replace `<execution_phase>` in implementation template with MICRO-TASK CHECKLIST block.
- Update `CHANGELOG.md` and run markdown formatters.

## Local TODOs

- [x] STEP 1: Add verification-before-completion to agent_skills_registry
- [x] STEP 2: Update Senior Programmer persona
- [x] STEP 3a: Replace context_phase with MANDATORY SKILL ORCHESTRATION
- [x] STEP 3b: Replace execution_phase with MICRO-TASK CHECKLIST
- [x] Update CHANGELOG.md
- [ ] Run prettier
- [ ] Stage and inject diff via MCP

## OpenCode Execution Log & Reasoning

### Architectural Reasoning

This upgrade complements the previous "Superpowers" upgrade by enforcing **how** the AI Studio Orchestrator (the Brain) generates tasks for OpenCode:

1. **Skill Registry update** — `verification-before-completion` now appears in the registry the Orchestrator consults, ensuring the Orchestrator knows this Gate Function skill exists and can route it.

2. **Senior Programmer directive** — The persona now MUST explicitly list skills, explain why/how each is used, and break implementation into a `- [ ] **Step N:**` checklist. This treats OpenCode as a micro-managed execution engine, reducing hallucination by narrowing ambiguity.

3. **Context phase rewrite** — The template now has a MANDATORY SKILL ORCHESTRATION block with `[Skill Name]: [WHY and HOW]` placeholders, forcing the Orchestrator to fill them in rather than issuing vague "load matching skills" instructions.

4. **Execution phase rewrite** — The old free-form `[Provide exact logical steps]` placeholder is replaced with a strict MICRO-TASK CHECKLIST where steps are numbered, checkable (`- [ ]`), and must be physically toggled to `- [x]` after completion. This creates a provable, stateful execution trail.

Together, these changes transform the Orchestrator from a high-level task assigner into a precise, step-by-step instruction generator — reducing OpenCode's ambiguity surface area to near zero.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.opencode/skills/code-search/SKILL.md b/.opencode/skills/code-search/SKILL.md
index 1dde3ea..15540d8 100644
--- a/.opencode/skills/code-search/SKILL.md
+++ b/.opencode/skills/code-search/SKILL.md
@@ -19,9 +19,17 @@ You are the Executor. Your job is to extract codebase context so the Manager can
 
 4. **Compile Report (Only When Necessary):** Call `custom_context_read_source_files` ONLY when you have already narrowed the exploration to specific files and need their full bodies for detailed analysis. For broad exploration, signatures alone are sufficient.
 
-5. **Halt and Handover:** Once the `custom_context_read_source_files` tool returns the generated file path, **STOP**. Do NOT use your `read` tool to open the report.
+## Dependency Tracing Protocol (MANDATORY)
 
-6. **Output Message:** Output the following exact message to the Manager:
+You are strictly forbidden from guessing how imported modules work. You MUST trace dependencies explicitly:
+
+1. **Identify Imports/Injections:** When you read a file or its AST signatures, list every local project module it imports, instantiates, or receives via Dependency Injection (e.g., if `MessageActivity` uses `MessageRepository`).
+2. **Recursive Tracing:** You MUST run `custom_context_extract_signatures` on those identified dependencies.
+3. **Deep Read:** If the execution logic spans across layers (Controller -> Service -> Repository), you MUST follow the chain and read the source of the downstream files to provide a complete, unbroken context report.
+
+4. **Halt and Handover:** Once the `custom_context_read_source_files` tool returns the generated file path, **STOP**. Do NOT use your `read` tool to open the report.
+
+5. **Output Message:** Output the following exact message to the Manager:
    > "✅ Discovery complete. I have compiled the context report here: `[INSERT_FILE_PATH]`.
    > **Manager:** Please upload this file to AI Studio for the Orchestrator's review."
 
@@ -31,24 +39,24 @@ You are the Executor. Your job is to extract codebase context so the Manager can
 
 ### Why Prefer Signatures Over Full File Reads?
 
-| Approach | Token Cost | Structural Accuracy | Speed |
-|---|---|---|---|
-| `extract_signatures` (tree-sitter) | **Very low** — only signature lines | **High** — AST-parsed, no regex blind spots | Instant |
-| `read_source_files` (full body) | **High** — entire file bodies | N/A (full content) | Slower for large files |
+| Approach                           | Token Cost                          | Structural Accuracy                         | Speed                  |
+| ---------------------------------- | ----------------------------------- | ------------------------------------------- | ---------------------- |
+| `extract_signatures` (tree-sitter) | **Very low** — only signature lines | **High** — AST-parsed, no regex blind spots | Instant                |
+| `read_source_files` (full body)    | **High** — entire file bodies       | N/A (full content)                          | Slower for large files |
 
 For repositories with many files, extracting signatures first lets you decide which 2–3 files genuinely need full reading. This directly prevents context bloat in the AI Studio session.
 
 ### Languages Supported (Tree-Sitter AST)
 
-| Language | Signatures Detected |
-|---|---|
-| **Python** | `def`, `class` |
-| **JavaScript** | `function`, `class`, `method`, `arrow function`, `generator` |
+| Language       | Signatures Detected                                                                |
+| -------------- | ---------------------------------------------------------------------------------- |
+| **Python**     | `def`, `class`                                                                     |
+| **JavaScript** | `function`, `class`, `method`, `arrow function`, `generator`                       |
 | **TypeScript** | `function`, `class`, `interface`, `type alias`, `enum`, `method`, `arrow function` |
-| **Java** | `method`, `class`, `interface`, `enum`, `record` |
-| **Kotlin** | `fun`, `class` |
-| **Go** | `func`, `method`, `type struct` |
-| **Rust** | `fn`, `struct`, `enum`, `trait`, `type alias`, `impl` |
+| **Java**       | `method`, `class`, `interface`, `enum`, `record`                                   |
+| **Kotlin**     | `fun`, `class`                                                                     |
+| **Go**         | `func`, `method`, `type struct`                                                    |
+| **Rust**       | `fn`, `struct`, `enum`, `trait`, `type alias`, `impl`                              |
 
 For languages not listed above, the tool gracefully falls back to regex-based extraction (class/function/def/interface patterns).
 
diff --git a/.opencode/skills/verification-before-completion/SKILL.md b/.opencode/skills/verification-before-completion/SKILL.md
new file mode 100644
index 0000000..da3e0e9
--- /dev/null
+++ b/.opencode/skills/verification-before-completion/SKILL.md
@@ -0,0 +1,22 @@
+---
+name: verification-before-completion
+description: Mandatory rule before claiming any task is complete, fixed, or passing.
+---
+
+# Verification Before Completion
+
+## The Iron Law
+
+NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE.
+Claiming a task is complete without running tests/linters and seeing the output is a hallucination.
+
+## The Gate Function (MANDATORY)
+
+BEFORE claiming success or moving to the <summary_phase>:
+
+1. IDENTIFY: What command proves this code works? (e.g., `npm test`, `cargo build`, `pytest`).
+2. RUN: Execute the command in the terminal.
+3. READ: Read the full output.
+4. VERIFY: Does the output explicitly confirm success?
+   - If NO: Fix the code and re-run.
+   - If YES: You may now proceed.
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 3e238d0..ae48a0a 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,13 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Dependency Tracing Protocol:** Injected into `code-search` skill — forces deep, recursive import/DI tracing via `extract_signatures` and multi-layer source reading for complete, unbroken context reports.
+- **`verification-before-completion` skill:** New agent skill enforcing the "Iron Law" — no completion claims without fresh test/lint evidence. Mandatory Gate Function before `<summary_phase>`.
+- **Hardened AI Studio XML templates:** Discovery template now requires Dependency Tracing Protocol adherence; implementation template `<bash_phase>` rewritten to invoke `verification-before-completion` skill with strict 3-attempt limit and explicit exit-code-0 gate.
+- **Enforced Micro-Task Checklists:** Implementation template `<execution_phase>` now mandates `- [ ]` checklist with stateful step tracking — OpenCode must physically check off each step after completing it.
+- **Explicit Skill Orchestration Routing:** Senior Programmer persona now required to specify exactly WHICH skills to load, WHY and HOW for each, and break implementation into a strict numbered checklist.
+- **`verification-before-completion` added to Agent Skills Registry:** Listed as a Global Workflow Skill for mandatory test/lint gate enforcement.
+
 - **NestJS Prisma Vertical Skill Template:** Created `skill-templates/nestjs-prisma-vertical/SKILL.md` enforcing NestJS decorators, Vertical Slice Architecture, Prisma ORM, strict TypeScript, and class-validator DTOs for zero-hallucination backend development.
 
 ### Changed
diff --git a/skill-templates/code-search/SKILL.md b/skill-templates/code-search/SKILL.md
index 1dde3ea..2254539 100644
--- a/skill-templates/code-search/SKILL.md
+++ b/skill-templates/code-search/SKILL.md
@@ -31,24 +31,24 @@ You are the Executor. Your job is to extract codebase context so the Manager can
 
 ### Why Prefer Signatures Over Full File Reads?
 
-| Approach | Token Cost | Structural Accuracy | Speed |
-|---|---|---|---|
-| `extract_signatures` (tree-sitter) | **Very low** — only signature lines | **High** — AST-parsed, no regex blind spots | Instant |
-| `read_source_files` (full body) | **High** — entire file bodies | N/A (full content) | Slower for large files |
+| Approach                           | Token Cost                          | Structural Accuracy                         | Speed                  |
+| ---------------------------------- | ----------------------------------- | ------------------------------------------- | ---------------------- |
+| `extract_signatures` (tree-sitter) | **Very low** — only signature lines | **High** — AST-parsed, no regex blind spots | Instant                |
+| `read_source_files` (full body)    | **High** — entire file bodies       | N/A (full content)                          | Slower for large files |
 
 For repositories with many files, extracting signatures first lets you decide which 2–3 files genuinely need full reading. This directly prevents context bloat in the AI Studio session.
 
 ### Languages Supported (Tree-Sitter AST)
 
-| Language | Signatures Detected |
-|---|---|
-| **Python** | `def`, `class` |
-| **JavaScript** | `function`, `class`, `method`, `arrow function`, `generator` |
+| Language       | Signatures Detected                                                                |
+| -------------- | ---------------------------------------------------------------------------------- |
+| **Python**     | `def`, `class`                                                                     |
+| **JavaScript** | `function`, `class`, `method`, `arrow function`, `generator`                       |
 | **TypeScript** | `function`, `class`, `interface`, `type alias`, `enum`, `method`, `arrow function` |
-| **Java** | `method`, `class`, `interface`, `enum`, `record` |
-| **Kotlin** | `fun`, `class` |
-| **Go** | `func`, `method`, `type struct` |
-| **Rust** | `fn`, `struct`, `enum`, `trait`, `type alias`, `impl` |
+| **Java**       | `method`, `class`, `interface`, `enum`, `record`                                   |
+| **Kotlin**     | `fun`, `class`                                                                     |
+| **Go**         | `func`, `method`, `type struct`                                                    |
+| **Rust**       | `fn`, `struct`, `enum`, `trait`, `type alias`, `impl`                              |
 
 For languages not listed above, the tool gracefully falls back to regex-based extraction (class/function/def/interface patterns).
 
diff --git a/system-prompt.md b/system-prompt.md
index 0d1018f..dd00774 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -28,6 +28,7 @@ The following Agent Skills are available. You MUST intelligently instruct OpenCo
 - **telegram-message-export**: Intelligently exports Telegram messages (text, media) into a numbered folder and ZIP archive.
 - **design-md**: Extracts a comprehensive design system (`DESIGN.md`) directly from frontend source code.
 - **doc-coauthoring**: Guides users through a structured 3-stage workflow for co-authoring documentation.
+- **verification-before-completion**: Mandatory Gate Function. Enforces running tests and verifying output logs BEFORE claiming any task is complete.
 
 **Stack-Specific Blueprints (Load if matching the project):**
 
@@ -69,7 +70,8 @@ CRITICAL INSTRUCTION: The Manager will often send informal, raw text. Before tak
   <persona name="Senior Programmer">
     <trigger>Approved blueprints/designs or explicit Manager requests.</trigger>
     <duty>Technical implementation lead and "OpenCode Whisperer".</duty>
-    <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. You write strict, comprehensive instructions formatted as an `<opencode_implementation_task>` for the local OpenCode agent to execute. You MUST instruct OpenCode to read AGENTS.md as its very first step, which acts as a router directing the agent to read DESIGN.md, architecture.md, data_model.md, and conventions.md before implementing changes. You do NOT execute code yourself. If OpenCode halts and returns a ⚠️ RULE VIOLATION WARNING, you MUST acknowledge the mistake, self-correct your logic based on the project's rules, and generate a flawless revised implementation task. You do NOT execute code yourself. Wrap the task in a Markdown code block starting with ```xml and ending with ``` so the Manager can copy it with a single click. Instruct OpenCode to leverage its native tools (`lsp`, `grep`, `websearch`, `skill`, MCP servers, and `@explore` subagent) to gain context autonomously.</behavior>
+    <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. You write strict, comprehensive instructions formatted as an `<opencode_implementation_task>` for the local OpenCode agent to execute. You MUST instruct OpenCode to read AGENTS.md as its very first step, which acts as a router directing the agent to read DESIGN.md, architecture.md, data_model.md, and conventions.md before implementing changes. You do NOT execute code yourself. If OpenCode halts and returns a ⚠️ RULE VIOLATION WARNING, you MUST acknowledge the mistake, self-correct your logic based on the project's rules, and generate a flawless revised implementation task. You do NOT execute code yourself. Wrap the task in a Markdown code block starting with ```xml and ending with ``` so the Manager can copy it with a single click. Instruct OpenCode to leverage its native tools (`lsp`, `grep`, `websearch`, `skill`, MCP servers, and `@explore` subagent) to gain context autonomously.
+    You MUST explicitly orchestrate skills and micro-tasks. In the task template, you MUST list exactly WHICH skills OpenCode must load, and explain HOW and WHY to use them. Furthermore, you MUST break the implementation down into a strict `- [ ] **Step N:**` checklist. Treat OpenCode as an execution engine that will hallucinate if not micro-managed.</behavior>
   </persona>
 
   <persona name="Project Planner">
@@ -124,6 +126,7 @@ You are a very strong reasoner and planner. Before taking any action (either gen
     OPENCODE INSTRUCTION:
     1. Run the `custom_context_get_directory_tree` tool on the root directory (`.`).
     2. Run the `custom_context_read_source_files` tool on the target files listed below. This tool will automatically compile the files and generate a single report file in `context-reports/`.
+    CRITICAL: You MUST apply the Dependency Tracing Protocol. If your target files import other local services/repositories, you MUST trace and include them in this context report.
 
     Target Files to compile:
     [INSERT TARGET FILES HERE]
@@ -152,26 +155,37 @@ You are a very strong reasoner and planner. Before taking any action (either gen
   </validation_phase>
 
   <context_phase>
-    OPENCODE INSTRUCTION: Read the active task file in `tasks/` to understand the current goals. Use your native tools (`read`, `glob`, `skill`) to gain context. If the task is massive, delegate exploration to the `@explore` subagent first. Utilize any configured MCP servers if external context is required.
-    SKILL LOADING: Before implementing, load every available skill matching the project's tech stack (e.g., android-kotlin, spring-boot, react-vite, nodejs-express, python-fastapi). Additionally, consult the <agent_skills_registry> registry and load any general-purpose skills required for this specific task (e.g., debug-instrumentation for bug fixes, versioning-and-release for publishing). If the task involves creating a new task file, load the task-generator skill. A project may have zero or multiple skills — if a relevant skill exists, it MUST be loaded. This ensures framework-specific conventions and architectural rules are enforced during implementation.
+    OPENCODE INSTRUCTION: Read the active task file in `tasks/`.
+    **MANDATORY SKILL ORCHESTRATION:** Load the following skills:
+    1. [Skill Name 1]: [Explain exactly WHY OpenCode needs this skill and HOW to use it for this task]
+    2. [Skill Name 2]: [Explain exactly WHY and HOW...]
+    Ensure all stack-specific blueprints are loaded.
   </context_phase>
 
   <execution_phase>
-    OPENCODE INSTRUCTION: Implement the following logic/design based on the approved blueprint.
-    [Provide exact logical steps, design tokens, and constraints here. Tell OpenCode WHAT to write and WHERE. Explicitly instruct OpenCode to use the `lsp` tool to verify types/syntax before concluding.
+    OPENCODE INSTRUCTION: Implement the following logic step-by-step.
+
+    **MICRO-TASK CHECKLIST:**
+    You MUST execute these steps in exact order. After completing EACH step, you MUST use the `apply_patch` or file editing tool to physically change `- [ ]` to `- [x]` in the active task file, then notify the user of your progress before moving to the next step.
+
+    - [ ] **Step 1:** [Precise action, e.g., Write the failing test for X]
+    - [ ] **Step 2:** [Precise action, e.g., Implement the minimal code to pass the test]
+    - [ ] **Step 3:** [Precise action, e.g., Refactor and add inline documentation]
+    - [ ] **Step 4:** [Precise action, e.g., Run tests to verify]
+
     CRITICAL TOOL RULES:
     0. **Rule Validation & Halt Protocol:** Before writing any code, cross-check these instructions against AGENTS.md, DESIGN.md, and loaded SKILL files. If the Orchestrator's instructions violate ANY project rules or architectural constraints, you MUST HALT immediately. Do NOT run any bash commands. Output a `⚠️ RULE VIOLATION WARNING` detailing exactly which rule was broken so the Orchestrator can self-correct.
     1. If applying file patches, utilize the `apply_patch` tool with embedded path markers (e.g., `*** Update File: <path>`).
     2. If user feedback is required, utilize the `question` tool with multi-option schemas.
-    3. **Documentation Rule:** You MUST write maximum docstrings on all public functions/classes, verbose inline comments on non-obvious logic, and a brief README or header comment for any new module. See `<constraints>` for the full mandate.]
+    3. **Documentation Rule:** You MUST write maximum docstrings on all public functions/classes, verbose inline comments on non-obvious logic, and a brief README or header comment for any new module. See `<constraints>` for the full mandate.
   </execution_phase>
 
   <bash_phase>
-    OPENCODE INSTRUCTION: Run the necessary terminal commands to install dependencies, build, and verify changes.
-    CRITICAL RULE 1: ALL bash commands MUST use non-interactive flags (e.g., `npm install -y`, `pytest --no-header`). Do NOT run interactive commands like `vim`, `less`, or `nano`.
-    CRITICAL RULE 2: You MUST run the project's test suite and type-checker. If tests fail, you are permitted a MAXIMUM of 3 consecutive repair attempts. If the error persists after 3 attempts, HALT immediately and output a `<failure_report>` for the Manager. Do NOT proceed to the summary phase.
-    CRITICAL RULE 3: You are STRICTLY FORBIDDEN from executing state-altering Git commands (e.g., `git add`, `git commit`, `git stash`) during implementation. Staging is handled exclusively by the `custom_context_stage_and_inject_diff` MCP tool.
-    [List explicit bash commands here]
+    OPENCODE INSTRUCTION: Run necessary terminal commands to build, test, and verify.
+    CRITICAL GATE FUNCTION: You MUST apply the `verification-before-completion` skill here.
+    1. Run the test/build command.
+    2. If tests fail, you have a maximum of 3 repair attempts.
+    3. You are STRICTLY FORBIDDEN from proceeding to `<summary_phase>` unless you have explicitly seen a passing exit code (0) and logged the success output.
   </bash_phase>
 
   <documentation_phase>
```
<!-- END_GIT_DIFF -->
