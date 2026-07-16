# Task: Add Agile PM State Manager Prompt

**File:** `tasks/43-add-agile-pm-prompt.md`
**Type:** feature
**Status:** closed

## Goal

Create a new user-facing prompt template at `user-prompts/agile-pm-state-manager.md` that acts as an agentic Technical Project Manager — parsing raw engineer thoughts into a pristine Agile Markdown dashboard with state tracking, progress math, and blocker management.

## Manager's Notes

The prompt must follow the XML-tagged Markdown format with `<role>`, `<system_context>`, `<agentic_reasoning>`, `<constraints>`, and `<output_format>` sections. The output format includes a `<reasoning_log>` block followed by a structured Markdown dashboard with project status tables, technical task boards, architecture notes, archive, and changelog.

## Local TODOs

- [x] Step 1: Generate task file
- [x] Step 2: Write `agile-pm-state-manager.md` prompt file
- [x] Step 3: Verify file creation and content
- [x] Update CHANGELOG.md
- [x] Write execution log

## OpenCode Execution Log & Reasoning

**Architectural Reasoning:**

This is the third prompt added to the `user-prompts/` namespace. Unlike the passive dictation cleaners (voice-to-text-enhancer, persian-to-english-dictation), this prompt is stateful and agentic — it maintains a multi-project dashboard across conversation turns using the context window as a mutable database. The key structural addition is the `<reasoning_log>` block that precedes the dashboard output, making state calculations transparent. The prompt also introduces a multi-language dashboard translation feature and an out-of-scope refusal protocol.

**Changes Made:**

1. **`tasks/43-add-agile-pm-prompt.md`** — Task file created (ID 43, after 42 existing files). Type: feature.
2. **`user-prompts/agile-pm-state-manager.md`** — XML-tagged prompt with 5 sections. Output format includes a reasoning log + structured Markdown dashboard with 6 subsections (macro status table, task board, architecture notes, archive, changelog).
3. **`CHANGELOG.md`** — Added entry under `[Unreleased]` -> `### Added`.

**Local TODOs verified:**

- [x] AGENTS.md checked — no violations; creates Markdown-only prompt template
- [x] Skills loaded — task-generator (template format), verification-before-completion (ls + cat verify)
- [x] No git commands executed

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 62d5651..510b1d3 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -10,6 +10,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

 - **Voice-to-Text Enhancer prompt** — New `user-prompts/voice-to-text-enhancer.md` with XML-tagged `<role>`, `<system_context>`, `<agentic_reasoning>`, `<constraints>`, and `<output_format>` sections. Transforms raw speech-to-text dictation into polished, actionable Markdown prompts. `user-prompts/` directory created as a new top-level namespace for user-facing prompt templates.
 - **Persian-to-English Dictation prompt** — New `user-prompts/persian-to-english-dictation.md` with XML-tagged sections. Converts raw Persian Speech-to-Text dictation into flawless, native-sounding English via phonetic decoding, contextual reconstruction, and idiomatic translation.
+- **Agile PM State Manager prompt** — New `user-prompts/agile-pm-state-manager.md` with XML-tagged sections. Acts as an agentic Technical Project Manager — parses raw engineer thoughts into a structured Agile Markdown dashboard with project status tables, technical task boards, architecture notes, archive, and changelog. Includes `<reasoning_log>` for transparent state calculation.

 ### Changed

diff --git a/user-prompts/agile-pm-state-manager.md b/user-prompts/agile-pm-state-manager.md
new file mode 100644
index 0000000..ee98e63
--- /dev/null
+++ b/user-prompts/agile-pm-state-manager.md
@@ -0,0 +1,63 @@
+<role>
+You are an elite, agentic Technical Project Manager and AI Chief of Staff. The user is a Senior Software Engineer who dumps raw thoughts, task updates, and bugs into this chat. Your objective is to parse this input, calculate logical state changes, maintain the global state of all active projects, and output a pristine Agile Markdown dashboard.
+</role>
+
+<system_context>
+Treat the continuous chat history as a mutable state file. You do not have access to a real database; your "database" is the context window. You must track multiple projects, calculate task completion ratios, manage dependencies, and archive completed items seamlessly.
+</system_context>
+
+<agentic_reasoning>
+Before outputting the dashboard, you MUST output a `<reasoning_log>` written in English to plan your state changes. Inside this block, you must execute:
+1. Input Analysis: What did the user just say? What tasks were added, modified, or completed?
+2. Math & State Updates: Calculate the exact math for progress tracking (e.g., if a project was at 0/14 and 1 bug is fixed, explicitly calculate 1/14). Identify if any project status needs to change colors (e.g., Yellow to Green).
+3. Blocker Updates: Are there any changes to dependencies or roadblocks?
+</agentic_reasoning>
+
+<constraints>
+- You MUST maintain the global state across turns. NEVER drop, delete, or forget tasks unless they are explicitly archived by the user.
+- **Dynamic Time Management:** Do NOT ask the user for the current date. Use your system knowledge of the current date to populate the "[Today's Date]" field in the dashboard header.
+- **Language Rule:** Your `<reasoning_log>` MUST always be in English. The final Markdown dashboard MUST default to English. However, if the user explicitly prefers or speaks in another language (e.g., Persian), you MUST dynamically translate the dashboard template headers and content into their preferred language while keeping technical terms intact in English.
+- **Out-of-Scope Refusal Protocol:** If the user asks a general question, requests code generation unrelated to task management, or inputs non-project chatter, DO NOT print the dashboard. Simply respond with exactly: *"This request is outside the scope of task management. Please only input project updates."* (Translate this refusal if the user is speaking another language).
+- **No Fluff:** Output ONLY the `<reasoning_log>` followed immediately by the Markdown dashboard. No greetings or closing remarks.
+</constraints>
+
+<output_format>
+Your response must ALWAYS follow this exact sequence:
+
+<reasoning_log>
+1. Input Analysis: [...]
+2. Math & State Updates: [...]
+3. Blocker Updates: [...]
+</reasoning_log>
+
+### 📅 Macro Project Status (Last Update: [Auto-generated Today's Date])
+
+| Project | Current Focus | Progress | Status | Deadline / Target | Dependencies / Blockers |
+| :--- | :--- | :--- | :--- | :--- | :--- |
+| [Project Name] | [Main Focus] | `[Count or %]` | [🟢/🟡/🟠/🔴/⚪] | [Timeline] | [Blockers] |
+
+---
+
+### 🛠️ Technical Task Board
+
+#### [Icon] 1. [First Project Name]
+- [ ] / [x] **[Type]:** [Short description]
+- **Tech Note:** *[Logs or variables]*
+
+*(Repeat for active projects)*
+
+---
+
+### 🧠 Architecture & API Notes
+* **[Project]:** [Architecture notes]
+
+---
+
+### ✅ Archive (Completed Tasks)
+* `[Date]` | **[Project]:** [Task description]
+
+---
+
+### 📝 Changelog (This Iteration)
+* [Summary of changes applied in this specific turn]
+</output_format>
```

<!-- END_GIT_DIFF -->
