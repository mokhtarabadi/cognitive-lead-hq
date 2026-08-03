# Task 73: Task Template Enhancement

**File:** `tasks/backlog/73-task-template-enhancement.md`
**Source:** orchestrator
**Type:** improvement
**Status:** open

## Source Context

### Variant A: Orchestrator (`**Source:** orchestrator`)

## Goal

Enhance the task-generator template with Acceptance Criteria, Verification Evidence, and Risk & Rollback sections. Integrate the lint MCP server into the task closure workflow.

## Blueprint Reference

V8.0.0 Improvement Roadmap Phase 4

## Manager's Notes

This task enhances the task-generator skill template by adding structured sections for acceptance criteria, verification evidence, and risk/rollback planning. It also integrates the `lint_task_file` MCP tool into the `<summary_phase>` of both the `<opencode_implementation_task_template>` and `<opencode_combined_task_template>` in `system-prompt.md` to enforce structural validation before diff injection.

## Local TODOs

- [x] Enhance task-generator skill template (unified + multi-phase) with Acceptance Criteria, Verification Evidence, and Risk & Rollback sections
- [x] Integrate lint MCP tool into summary_phase of system-prompt.md task templates

---

## OpenCode Execution Log & Reasoning

### Architectural Changes

**1. Task Generator Template Enhancement (`skill-templates/task-generator/SKILL.md`)**

Added three new mandatory sections to both the unified canonical template and the multi-phase task template:

- **`## Acceptance Criteria`** — Forces explicit definition of "done" before execution begins. Prevents scope creep and ambiguity by requiring concrete, checkbox-verifiable criteria.
- **`## Verification Evidence`** — Mandates a specific test command, expected result, actual result, and exit code. This creates a machine-readable audit trail and ensures OpenCode cannot claim completion without running the verification command.
- **`## Risk & Rollback`** — Requires upfront risk assessment and rollback plan documentation. This prevents silent failures from becoming unrecoverable and gives the Code Reviewer a pre-written remediation path.

**Rationale:** These sections were placed after `## Local TODOs` (unified) and after `## Goal` (multi-phase) to maintain the logical flow: Goal → Criteria → Execution → Evidence → Risk.

**2. Lint Integration in `system-prompt.md`**

Modified the `<summary_phase>` of both `<opencode_implementation_task_template>` and `<opencode_combined_task_template>`:

- Added `lint_task_file` MCP tool call as the **first** step in the finalization sequence (before `custom_context_stage_and_inject_diff`).
- This enforces structural validation before any diff injection, catching template violations (missing sections, ID mismatches, broken markers) before they propagate to the Code Reviewer.
- Version bumped from `7.4.0` to `7.4.1` (PATCH bump for template/workflow enhancements per SemVer).

### Verification

- `grep -q "## Acceptance Criteria"` — ✅ passed
- `grep -q "## Verification Evidence"` — ✅ passed
- `grep -q "## Risk & Rollback"` — ✅ passed

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 061a8b2..6f6bb76 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -12,6 +12,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Changed
 
+- **Task Template Enhancement & Lint Integration (V8.0.0 Phase 4)** — Enhanced `task-generator` skill template with mandatory `## Acceptance Criteria`, `## Verification Evidence`, and `## Risk & Rollback` sections for both unified and multi-phase task files. Integrated `lint_task_file` MCP tool into the `<summary_phase>` of both `<opencode_implementation_task_template>` and `<opencode_combined_task_template>` to enforce structural validation before diff injection. System prompt version bumped to 7.4.1.
 - **Input Processing Pipeline Enhancement (V8.0.0 Phase 1)** — Enhanced `<user_input_processing>` in `system-prompt.md` with mandatory Input Validation Gate (Step 0.5), enriched Intent Expansion, and Prompt Refactor Gate (Step 5.5). Enhanced `prompt-refactor` skill with Step 0 validation and typo correction. Updated `AGENTS.md` guardrail to enforce Input Validation Pipeline. Created `user-prompts/input-validation-test.md`. System prompt version bumped to 7.3.0.
 
 ### Fixed
diff --git a/skill-templates/task-generator/SKILL.md b/skill-templates/task-generator/SKILL.md
index fbd5d60..d5769f0 100644
--- a/skill-templates/task-generator/SKILL.md
+++ b/skill-templates/task-generator/SKILL.md
@@ -100,6 +100,23 @@ The title number MUST match the filename ID. Any mismatch or duplicate must be r
    - [ ] [Specific step 1]
    - [ ] Verify functionality
 
+   ## Acceptance Criteria
+
+   - [ ] [Criterion 1 — what must be true for this task to be considered done]
+   - [ ] [Criterion 2]
+
+   ## Verification Evidence
+
+   - **Test command:** [exact command]
+   - **Expected result:** [what success looks like]
+   - **Actual result:** _(OpenCode fills this during execution)_
+   - **Exit code:** _(OpenCode fills this during execution)_
+
+   ## Risk & Rollback
+
+   - **Risk:** [what could go wrong]
+   - **Rollback plan:** [how to undo if needed]
+
    ---
 
    ## OpenCode Execution Log & Reasoning
@@ -131,6 +148,23 @@ If the Orchestrator specifies `multi_phase: true`, generate a SINGLE task file w
 
 [Summary of the goal]
 
+## Acceptance Criteria
+
+- [ ] [Criterion 1 — what must be true for this task to be considered done]
+- [ ] [Criterion 2]
+
+## Verification Evidence
+
+- **Test command:** [exact command]
+- **Expected result:** [what success looks like]
+- **Actual result:** _(OpenCode fills this during execution)_
+- **Exit code:** _(OpenCode fills this during execution)_
+
+## Risk & Rollback
+
+- **Risk:** [what could go wrong]
+- **Rollback plan:** [how to undo if needed]
+
 ## Phase 1: [Name]
 
 ### Local TODOs
diff --git a/system-prompt.md b/system-prompt.md
index 58b9285..ea969b1 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>7.4.0</system_version>
+<system_version>7.4.1</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -283,9 +283,10 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 
   <summary_phase>
     OPENCODE INSTRUCTION: You MUST follow this exact finalization sequence:
-    1. Call the `custom_context_stage_and_inject_diff` MCP tool, providing the exact path to the active task file (e.g., `tasks/in-progress/XX-task-name.md`). This will securely stage your code and overwrite the diff block without duplicating text.
-    2. Once the tool returns success, you are DONE.
-    3. Output EXACTLY this message to the Manager:
+    1. Call the `lint_task_file` MCP tool (from the `lint` server) on the active task file. If lint fails, fix the structural issues before proceeding.
+    2. Call the `custom_context_stage_and_inject_diff` MCP tool, providing the exact path to the active task file. This will securely stage your code and overwrite the diff block without duplicating text.
+    3. Once the tool returns success, you are DONE.
+    4. Output EXACTLY this message to the Manager:
        "✅ Task implemented, reasoning logged, and Git diff injected. **Manager:** Please copy the entire contents of `[path/to/task.md]` and send it back to the Orchestrator Brain with the following message:"
 
        "(If this task involved logic, backend, or state changes, tell the Manager to copy/paste this:) **'[QA Engineer], please perform adversarial testing.'**"
@@ -329,7 +330,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
     OPENCODE INSTRUCTION:
     1. If you HALTED after discovery (architecture mismatch): STOP. Do not implement anything. Output exactly:
        "⏸️ Discovery complete but architecture mismatch detected. Manager: I have generated the context report at [REPORT_PATH]. Please copy its contents and send them back to the Orchestrator for a revised plan."
-    2. If implementation completed successfully: Follow the standard finalization sequence — call the `custom_context_stage_and_inject_diff` MCP tool, then output exactly:
+    2. If implementation completed successfully: Follow the standard finalization sequence — call the `lint_task_file` MCP tool (from the `lint` server) on the active task file. If lint fails, fix the structural issues before proceeding. Then call the `custom_context_stage_and_inject_diff` MCP tool, then output exactly:
        "✅ Task implemented, reasoning logged, and Git diff injected. **Manager:** Please copy the entire contents of [path/to/task.md] and send it back to the Orchestrator Brain with the following message:"
 
        "(If this task involved logic, backend, or state changes, tell the Manager to copy/paste this:) **'[QA Engineer], please perform adversarial testing.'**"
```
<!-- END_GIT_DIFF -->
