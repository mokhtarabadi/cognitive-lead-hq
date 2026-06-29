# Task 16: Zero-Autonomous-Commit Workflow

**Type:** improvement
**Status:** closed

## Goal

Enforce a strict Zero-Autonomous-Commit workflow across the system prompt and AGENTS.md, isolating code staging to the MCP tool and deferring all `git commit` commands to the AI Studio Reviewer's approval step.

## Manager's Notes

- Bump system version to 5.10.0 in system-prompt.md.
- Update Code Reviewer persona to generate commit tasks on approval and fix-loop tasks on rejection.
- Remove `git commit -m "msg"` from bash phase non-interactive examples.
- Add CRITICAL RULE 3 forbidding Git commands during implementation.
- Rewrite execution workflow to split step 3 into "Implement & Inject" (no commits), add a "Fix Loop" step, and add a separate "Commit & Close" step.
- Update AGENTS.md guardrails and End-Of-Task Sequence to reflect the new policy.
- Add CHANGELOG.md entry.

## Local TODOs

- [x] Create Task 16 file
- [x] Bump system-prompt.md version to 5.10.0
- [x] Update Code Reviewer persona with commit task generation and fix-loop logic
- [x] Remove `git commit -m "msg"` from bash CRITICAL RULE 1 and add CRITICAL RULE 3
- [x] Rewrite execution workflow with 6-step loop (Implement & Inject → Team Review → Fix Loop → Commit & Close)
- [x] Add Git guardrails to AGENTS.md Actionable Guardrails
- [x] Update AGENTS.md End-Of-Task Sequence step 3 to forbid git commit
- [x] Update CHANGELOG.md with entry
- [ ] Call custom_context_stage_and_inject_diff MCP tool

## OpenCode Execution Log & Reasoning

### Architectural Reasoning

This upgrade introduces the **Zero-Autonomous-Commit (ZAC)** workflow — a critical policy shift that separates code staging from committing. Previously, OpenCode could run `git commit` during its bash phase, bypassing the AI Studio Reviewer. The ZAC workflow enforces:

1. **MCP-only staging** — OpenCode must never run `git add`, `git commit`, or `git stash`. Staging is handled exclusively by the `custom_context_stage_and_inject_diff` MCP tool at the end of a task.
2. **Reviewer-driven commits** — Commits only happen after the Reviewer approves the factual diff. The Reviewer generates a brief commit task if approved, or a fix-loop task if rejected.
3. **6-step execution flow** — The old 5-step linear workflow is replaced with a loop: Implement & Inject → Team Review → Fix Loop (if rejected) → Commit & Close (if approved).

### Execution Notes

- Edited `system-prompt.md` — bumped to 5.10.0, updated Code Reviewer, bash rules, and execution workflow.
- Edited `AGENTS.md` — added Git guardrails under Actionable Guardrails and updated End-Of-Task Sequence step 3.
- Updated `CHANGELOG.md` with a new [Unreleased] entry describing the ZAC workflow.
- Created `tasks/16-zero-autonomous-commit-workflow.md` as the active task file.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

```diff
diff --git a/AGENTS.md b/AGENTS.md
index 84db3a2..38f8848 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -31,6 +31,8 @@ This repository is the Headquarters for the Cognitive Lead AI multi-agent system
   -> **Do** use the decentralized `tasks/` directory with individual task files as the single source of truth.
 - **Don't** make UI/UX changes without consulting `DESIGN.md`.
   -> **Do** enforce the color palette, typography, spacing, and component styling defined in `DESIGN.md`.
+- **Don't** execute Git commands like `git add`, `git commit`, or `git stash` manually during implementation.
+  -> **Do** rely exclusively on the `custom_context_stage_and_inject_diff` MCP tool to securely stage your working changes.

 ## Documentation Sync Rules

@@ -63,5 +65,5 @@ When finishing a task, you MUST execute these exact steps in order:

 1. **Update Changelog:** You MUST insert a formal entry into CHANGELOG.md logging your modifications.
 2. **Write your Summary:** Manually write your architectural reasoning, local TODO checks, and execution notes into the active `tasks/XX-task.md` file under "OpenCode Execution Log".
-3. **Call MCP Tool:** Call the `custom_context_stage_and_inject_diff` MCP tool passing the task file path to automatically `git add .` and inject the factual code diff.
+3. **Call MCP Tool:** Call the `custom_context_stage_and_inject_diff` MCP tool passing the task file path to automatically stage the files and inject the factual code diff. DO NOT execute any `git commit` commands afterward.
 4. **Notify Manager:** Output exactly: "Task ready. Manager, please copy the contents of `tasks/XX-task.md` and send it back to the AI Studio Brain for review."
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 8247a1d..6b630ca 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -122,8 +122,16 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

 ## [Unreleased]

+### Added
+
+- **Zero-Autonomous-Commit (ZAC) Workflow:** Enforced strict separation of code staging from committing. OpenCode is now forbidden from running `git add`, `git commit`, or `git stash` during implementation (CRITICAL RULE 3). Staging is handled exclusively by the `custom_context_stage_and_inject_diff` MCP tool.
+- **Reviewer-Driven Commit Cycle:** Code Reviewer persona now generates commit tasks on `APPROVED` status and fix-loop implementation tasks on `REJECTED_NEEDS_FIXES` status, completing the review loop.
+- **6-Step Execution Workflow:** Replaced the old linear 5-step workflow with a loop: Implement & Inject → Team Review → Fix Loop → Commit & Close.
+
 ### Changed

+- **`system-prompt.md`** — `<system_version>` bumped to 5.10.0. Code Reviewer behavior updated. CRITICAL RULE 1 in bash phase no longer lists `git commit` as a non-interactive example. CRITICAL RULE 3 added forbidding Git commands. `<execution_workflow>` rewritten with implement/inject, review, fix-loop, and commit steps.
+- **`AGENTS.md`** — Added Git guardrail under Actionable Guardrails. Mandatory End-Of-Task Sequence step 3 updated to forbid `git commit` commands.
 - **`stage_and_inject_diff` MCP tool** — optimized the staged git diff command to globally exclude the entire `tasks/` directory (`:!tasks/`) instead of just the single active task file, completely eliminating task history clutter from factual codebase reviews.

 ## [5.9.0] — 2026-06-21
diff --git a/system-prompt.md b/system-prompt.md
index 677f589..42a68a8 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>5.9.0</system_version>
+<system_version>5.10.0</system_version>

 <role>
 You are the Cognitive Lead AI running inside Google AI Studio (powered by Gemini), acting as an elite software agency orchestrator.
@@ -49,7 +49,7 @@ CRITICAL INSTRUCTION: The Manager will often send informal, raw text. Before tak
   <persona name="Code Reviewer">
     <trigger>Manager pastes OpenCode's completed Task Summary, PRs are submitted, or Manager requests.</trigger>
     <duty>Audit OpenCode's completed work against the Architect's blueprint, the Designer's UI specs, and the project's conventions.</duty>
-    <behavior>Read the "OpenCode Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. If rejected, explicitly state what OpenCode must fix in the next iteration.</behavior>
+    <behavior>Read the "OpenCode Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. If rejected, explicitly state what OpenCode must fix in the next iteration and generate a subsequent implementation task to fix the implementation. If APPROVED, generate a brief OpenCode task to execute `git commit` and mark the task file as `closed`.</behavior>
   </persona>
 </personas>

@@ -117,8 +117,9 @@ You are a very strong reasoner and planner. Before taking any action (either gen

   <bash_phase>
     OPENCODE INSTRUCTION: Run the necessary terminal commands to install dependencies, build, and verify changes.
-    CRITICAL RULE 1: ALL bash commands MUST use non-interactive flags (e.g., `npm install -y`, `git commit -m "msg"`, `pytest --no-header`). Do NOT run interactive commands like `vim`, `less`, or `nano`.
+    CRITICAL RULE 1: ALL bash commands MUST use non-interactive flags (e.g., `npm install -y`, `pytest --no-header`). Do NOT run interactive commands like `vim`, `less`, or `nano`.
     CRITICAL RULE 2: You MUST run the project's test suite and type-checker. If tests fail, you are permitted a MAXIMUM of 3 consecutive repair attempts. If the error persists after 3 attempts, HALT immediately and output a `<failure_report>` for the Manager. Do NOT proceed to the summary phase.
+    CRITICAL RULE 3: You are STRICTLY FORBIDDEN from executing state-altering Git commands (e.g., `git add`, `git commit`, `git stash`) during implementation. Staging is handled exclusively by the `custom_context_stage_and_inject_diff` MCP tool.
     [List explicit bash commands here]
   </bash_phase>

@@ -144,9 +145,10 @@ During Phase 0, the Planner will launch up to 4 parallel subagent tasks to deepl

 1. **Input Processing & Clarification**: Analyze the Manager's raw input. Clean syntax, interpret context. IF ambiguous, HALT and ask clarifying questions. IF clear, proceed.
 2. **Plan (Architect & UI/UX)**: Analyze request -> Deliver blueprint -> Ask Manager for approval.
-3. **Implement (Programmer)**: Wait for "Approved" -> generate the strict, markdown-wrapped `<opencode_implementation_task>` block.
-4. **Execute (OpenCode)**: Manager copies and runs inside OpenCode. OpenCode executes, passes tests, and outputs the Task Summary.
-5. **Review (Reviewer)**: Manager passes OpenCode's Task Summary back to you. Review against the blueprint.
+3. **Implement & Inject (Programmer)**: Wait for "Approved" -> generate the `<opencode_implementation_task>` block. OpenCode executes, stages via MCP tool (NO COMMITS), and outputs Task Summary.
+4. **Team Review (Reviewer)**: Manager passes OpenCode's completed task file back. Review against the factual Git Diff.
+5. **Fix Loop (Programmer)**: If rejected, generate a subsequent task to fix the implementation. Loop back to step 3.
+6. **Commit & Close (Programmer)**: If approved by the Reviewer, generate a short task for OpenCode to finally run `git commit` and update the task file status to closed.
    </execution_workflow>

 <constraints>
```

<!-- END_GIT_DIFF -->
