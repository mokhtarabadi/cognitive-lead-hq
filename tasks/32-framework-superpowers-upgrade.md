# Task: Framework Superpowers Upgrade

**File:** `tasks/32-framework-superpowers-upgrade.md`
**Type:** improvement
**Status:** open

## Goal

Upgrade the core framework with three "Superpowers": Dependency Tracing Protocol in `code-search`, a new `verification-before-completion` skill, and hardened AI Studio XML templates in `system-prompt.md`.

## Manager's Notes

- Insert Dependency Tracing Protocol before the "Halt and Handover" step in `code-search`.
- Create `.opencode/skills/verification-before-completion/SKILL.md` with the Iron Law and Gate Function.
- Add Dependency Tracing Protocol instruction to the discovery task template's `<execution_phase>`.
- Replace the implementation task template's `<bash_phase>` with the rigorous Gate Function version.
- Update `CHANGELOG.md` and run markdown formatters.

## Local TODOs

- [x] STEP 1: Insert Dependency Tracing Protocol into code-search skill
- [x] STEP 2: Create verification-before-completion skill file
- [x] STEP 3a: Add Dependency Tracing Protocol instruction to discovery template
- [x] STEP 3b: Replace bash_phase content with Gate Function version
- [ ] Run markdown formatter
- [ ] Update CHANGELOG.md
- [ ] Stage and inject diff

## OpenCode Execution Log & Reasoning

### Architectural Reasoning

The three upgrades form a cohesive "Superpowers" framework:

1. **Dependency Tracing Protocol** (`code-search`): Forces deep, recursive tracing of imports and DI injections, eliminating guesswork about how modules wire together. This prevents the common hallucination pattern where an agent assumes a module works a certain way without verifying its actual implementation.

2. **Verification Before Completion** (new skill): Hardcodes the rule that no task can be claimed complete without fresh test/lint evidence. The "Iron Law" and "Gate Function" are designed to be non-negotiable — agents MUST run the verification command, read its output, and confirm success before proceeding.

3. **Hardened XML Templates** (`system-prompt.md`): The discovery template now requires Dependency Tracing Protocol adherence, ensuring deep context reports include downstream dependencies. The implementation template's `<bash_phase>` is rewritten to invoke the `verification-before-completion` skill directly, replacing the older CRITICAL RULE 1/2/3 format with a cleaner, skill-driven Gate Function that also enforces the 3-attempt limit and strictly forbids proceeding to `<summary_phase>` without a passing exit code (0).

These three changes together ensure the agent produces more accurate, well-traced, and verified outputs — reducing hallucination risk at every stage.

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
index 3e238d0..d2128bf 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Dependency Tracing Protocol:** Injected into `code-search` skill — forces deep, recursive import/DI tracing via `extract_signatures` and multi-layer source reading for complete, unbroken context reports.
+- **`verification-before-completion` skill:** New agent skill enforcing the "Iron Law" — no completion claims without fresh test/lint evidence. Mandatory Gate Function before `<summary_phase>`.
+- **Hardened AI Studio XML templates:** Discovery template now requires Dependency Tracing Protocol adherence; implementation template `<bash_phase>` rewritten to invoke `verification-before-completion` skill with strict 3-attempt limit and explicit exit-code-0 gate.
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
index 0d1018f..6cbeb03 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -124,6 +124,7 @@ You are a very strong reasoner and planner. Before taking any action (either gen
     OPENCODE INSTRUCTION:
     1. Run the `custom_context_get_directory_tree` tool on the root directory (`.`).
     2. Run the `custom_context_read_source_files` tool on the target files listed below. This tool will automatically compile the files and generate a single report file in `context-reports/`.
+    CRITICAL: You MUST apply the Dependency Tracing Protocol. If your target files import other local services/repositories, you MUST trace and include them in this context report.
 
     Target Files to compile:
     [INSERT TARGET FILES HERE]
@@ -167,11 +168,11 @@ You are a very strong reasoner and planner. Before taking any action (either gen
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
