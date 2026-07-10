# Task: Enforce Strict Approval Loop & Inline Reviews

**Type:** improvement
**Status:** closed

## Goal

Codify the `> 📝 **MANAGER REVIEW:**` inline markdown review convention and strictly enforce the manager approval gate before generating any OpenCode implementation tasks.

## Manager's Notes

- Update `system-prompt.md` version to 5.16.0.
- Update execution workflow steps 2 and 3 to include the review loop.
- Add a strict approval constraint to the system prompt.
- Document the review convention in `README.md`.
- Update `CHANGELOG.md`.

## Local TODOs

- [x] Initial codebase exploration
- [x] Apply patches to system-prompt.md
- [x] Apply patches to README.md
- [x] Apply patches to CHANGELOG.md
- [x] Create this task file
- [x] Run formatting check (Prettier)

## OpenCode Execution Log & Reasoning

**Architectural Reasoning:** This task formalizes the Manager feedback loop within the AI Studio orchestration workflow. Previously, step 2 ("Plan") was a one-shot deliver-and-wait — if the Manager wanted changes, the only option was to restart the entire workflow. The inline `> 📝 **MANAGER REVIEW:**` convention introduces a structured, loopable feedback mechanism directly inside Markdown plans, enabling the Manager to annotate sections without leaving the AI Studio interface. The Strict Approval Gate constraint (newly added to `<constraints>`) prevents OpenCode from executing any implementation task before explicit Manager approval, codifying the Brain/Hands separation principle.

**Changes Made:**

1. **system-prompt.md:** Bumped `<system_version>` to 5.16.0. Reworked execution workflow step 2 from "Plan" to "Plan & Review Loop" with inline Markdown feedback handling. Updated step 3 to wait for the explicit "Approved" signal. Added a new `- **Strict Approval Gate & Inline Review Pattern:**` constraint in `<constraints>`.
2. **README.md:** Added a new "Inline Markdown Reviews & Strict Approval" section explaining the feedback workflow to Managers.
3. **CHANGELOG.md:** Added version 5.16.0 entry with "Added" items for the strict approval gate and markdown review convention. Cleaned up stale Unreleased content that was erroneously left from the 5.13.2 release.
4. **tasks/26-enforce-strict-approval-loop.md:** Created the decentralized task file tracking this improvement.

**Verification:** Prettier formatting check passed — all files remain valid Markdown.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 15071f1..078814e 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -122,9 +122,12 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

 ## [Unreleased]

-### Changed
+## [5.16.0] — 2026-07-03
+
+### Added

-- **`skill-templates/telegram-issue-sync/SKILL.md`** — Overhauled to fix the summarization bug (root cause: ambiguous "inject context" language allowed LLMs to paraphrase raw text). Now enforces verbatim `## Original Message ({LANGUAGE})` section, separate `## English Translation` section, `## Refactored Prompt` from prompt-refactor skill, `## Relevant Code Context` from autonomous codebase search, and `## AI Analysis & Opinion`. Added Phase 0 mandatory skill loading (prompt-refactor, task-generator). Added interactive GitHub issue toggle via Manager approval. Added 9-step per-candidate generation pipeline with data integrity guarantees table.
+- **Strict Approval Gate & Inline Review Pattern:** Formalized the requirement that the AI Studio Orchestrator must receive explicit Manager approval before generating OpenCode implementation tasks.
+- **Markdown Review Convention:** Documented the `> 📝 **MANAGER REVIEW:**` blockquote syntax in both `system-prompt.md` and `README.md` to establish a standard method for Managers to leave inline feedback on architectural blueprints.

 ## [5.15.0] — 2026-07-02

diff --git a/README.md b/README.md
index 85ffdfc..7b33485 100644
--- a/README.md
+++ b/README.md
@@ -54,6 +54,19 @@ If you have an older project using global `STATE.md` and `TODO.md` files:
 4. Tell the AI: _"Migrate this project from V4 to V5. Generate a task to update `AGENTS.md` and move existing roadmap items into `tasks/01-v5-migration.md`."_
 5. Ensure the `task-generator` and `audit-agents` skills are imported into `.opencode/skills/` (or installed globally).

+### Inline Markdown Reviews & Strict Approval
+
+Before any code is written, the Brain will present an Architectural Blueprint or Plan. OpenCode will **not** execute any implementation tasks without your explicit approval.
+
+To leave feedback directly on the generated Markdown plans:
+
+1. Copy the plan into your editor.
+2. Add `> 📝 **MANAGER REVIEW:**` blockquotes immediately below the section you want to change.
+3. Alternatively, use standard Markdown strikethrough (`~~text~~`) and bold (`**text**`) for direct edits.
+4. Paste the annotated Markdown back to AI Studio.
+
+The AI will process your inline feedback, generate a revised plan, and wait for your final "Approved" signal before writing code.
+
 ## Repository Structure

```

diff --git a/system-prompt.md b/system-prompt.md
index 7df5777..740038f 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>5.15.0</system_version>
+<system_version>5.16.0</system_version>

 <role>
 You are the Cognitive Lead AI running inside Google AI Studio (powered by Gemini), acting as an elite software agency orchestrator.
@@ -174,8 +174,8 @@ You are a very strong reasoner and planner. Before taking any action (either gen
 During Phase 0, the Planner will launch up to 4 parallel subagent tasks to deeply scan files and concurrently generate `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` to avoid style and structure misalignment.

1.  **Input Processing & Clarification**: Analyze the Manager's raw input. Clean syntax, interpret context. IF ambiguous, HALT and ask clarifying questions. IF clear, proceed.
    -2. **Plan (Architect & UI/UX)**: Analyze request -> Deliver blueprint -> Ask Manager for approval.
    -3. **Implement & Inject (Programmer)**: Wait for "Approved" -> generate the `<opencode_implementation_task>` block. OpenCode executes, stages via MCP tool (NO COMMITS), and outputs Task Summary.
    +2. **Plan & Review Loop (Architect & UI/UX)**: Analyze request -> Deliver blueprint -> Ask Manager for approval. If the Manager provides inline feedback using the `> 📝 **MANAGER REVIEW:**` syntax or direct text edits, resolve the feedback and output a revised blueprint. Loop this step until explicit approval is received.
    +3. **Implement & Inject (Programmer)**: Wait for the explicit "Approved" signal -> generate the `<opencode_implementation_task>` block. OpenCode executes, stages via MCP tool (NO COMMITS), and outputs Task Summary.
2.  **Team Review (Reviewer)**: Manager passes OpenCode's completed task file back. Review against the factual Git Diff.
3.  **Fix Loop (Programmer)**: If rejected, generate a subsequent task to fix the implementation. Loop back to step 3.
4.  **Commit & Close (Programmer)**: If approved by the Reviewer, generate a short task for OpenCode to run `git commit` and update the task file status to closed. In the commit task, do NOT include the `custom_context_stage_and_inject_diff` MCP tool call — calling it after a commit clears the diff section since there are no unstaged changes. Use a simple summary phase that just instructs OpenCode to output a completion message.
    @@ -183,6 +183,7 @@ During Phase 0, the Planner will launch up to 4 parallel subagent tasks to deepl

 <constraints>
 - **Cognitive Language Rule:** All internal reasoning, architectural blueprints, XML task generation, and OpenCode execution logs MUST always be written in English. You may only use a localized language for direct conversational responses to the Manager if explicitly requested.
+- **Strict Approval Gate & Inline Review Pattern:** You MUST NOT generate any `<opencode_implementation_task>` blocks until the Manager explicitly approves the architectural plan or blueprint. The Manager will provide feedback directly inside Markdown files using `> 📝 **MANAGER REVIEW:**` blockquotes or standard markdown strikethrough/bold edits. You must process this feedback, revise the plan, and ask for approval again, looping until a final "Approved" is received.
 - **Template Preservation Rule:** When generating the `<summary_phase>`, you MUST output the literal placeholder tags (e.g. `<OpenCode: Describe the features...>`). DO NOT pre-fill the summary.
 - **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`.
 - **Tone and Demeanor**: Keep your responses highly professional, objective, and analytical. Do not use superlatives.
```
<!-- END_GIT_DIFF -->
