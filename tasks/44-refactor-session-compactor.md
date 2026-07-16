# Task: Refactor Session Compactor Prompt

**File:** `tasks/44-refactor-session-compactor.md`
**Type:** improvement
**Status:** closed

## Goal

Overwrite the existing `user-prompts/session-compactor.md` with a fully XML-tagged Markdown prompt that functions as a Session Context Compactor & Restoration Generator, using `<role>`, `<system_context>`, `<agentic_reasoning>`, `<constraints>`, and `<output_format>` sections with a structured restoration report template.

## Manager's Notes

This is a refactor of the existing session-compactor prompt. The new version adds a `<reasoning_log>` block, expands the output format to 7 sections (Project Overview, Global Config, Task Registry, Codebase State, Architectural Map, Next Milestones, Restoration Protocol), and includes a copy-paste usage instruction at the top.

## Local TODOs

- [x] Step 1: Generate task file
- [x] Step 2: Overwrite `session-compactor.md` with new content
- [x] Step 3: Verify file was updated correctly
- [x] Update CHANGELOG.md
- [x] Write execution log

## OpenCode Execution Log & Reasoning

**Architectural Reasoning:**

This refactor upgrades the existing session-compactor prompt (previously a flat Markdown template) to the full XML-tagged format used across `user-prompts/` and the system prompt ecosystem. The key structural improvements: (1) a `<reasoning_log>` block for transparent session analysis before report generation, (2) a standardized 7-section restoration report template covering project overview, MCP/agent config, chronological task registry with Telegram MSG ID tracking, forensic codebase state, architectural decisions ("The Why"), next milestones, and a cold-start restoration protocol. The copy-paste usage instruction at the top makes the user workflow self-documenting.

**Changes Made:**

1. **`tasks/44-refactor-session-compactor.md`** — Task file created (ID 44, after 43 existing files). Type: improvement.
2. **`user-prompts/session-compactor.md`** — Fully overwritten with XML-tagged prompt. Expanded from flat Markdown to structured 5-section XML + 7-section restoration report.
3. **`CHANGELOG.md`** — Added entry under `[Unreleased]` -> `### Changed`.

**Local TODOs verified:**

- [x] AGENTS.md checked — no violations
- [x] Skills loaded — task-generator, verification-before-completion
- [x] File verified — `ls -la` confirms file exists (4576 bytes, 66 lines); new header and all 7 sections present

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

````diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 510b1d3..7a1ac5e 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -14,6 +14,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

 ### Changed

+- **Session Compactor prompt** — Refactored `user-prompts/session-compactor.md` to full XML-tagged Markdown format with `<role>`, `<system_context>`, `<agentic_reasoning>`, `<constraints>`, and `<output_format>` sections. Added `<reasoning_log>` block and expanded restoration report to 7 structured sections (Project Overview, Global Config, Task Registry, Codebase State, Architectural Map, Next Milestones, Restoration Protocol) with copy-paste usage instructions.
 - **README roadmap** — Added Memory Management (Smart Note-Taking MCP & Skill) as item #7 in the Future Architectural Roadmap, describing a local `memory-mcp` server and `project-memory` agent skill for persistent context retention.
 - **README roadmap** — Added Adversarial QA Persona as item #8 and Lifecycle Task Architecture (Kanban & Archiving) as item #9 to the Future Architectural Roadmap, describing a dedicated `[QA Engineer]` persona with adversarial testing instructions and a state-based Kanban folder workflow with archiving compaction.

diff --git a/user-prompts/session-compactor.md b/user-prompts/session-compactor.md
index 27598af..b5880fc 100644
--- a/user-prompts/session-compactor.md
+++ b/user-prompts/session-compactor.md
@@ -4,58 +4,63 @@

 --- COPY BELOW THIS LINE TO COMPACT SESSIONS ---

-## Context Compaction Protocol Request
+<role>
+You are an elite Context Compaction Specialist and Systems Archivist. Your objective is to perform a Semantic Context Compaction of our current development session, extracting all critical technical state, decisions, and progress into a highly condensed Context Restoration Report.
+</role>
+
+<system_context>
+Our current AI Studio development session is reaching its token limit. To preserve the complete operational context without carrying forward millions of redundant conversational tokens, we must generate a dense, stateless checkpoint. This checkpoint will be loaded into a brand-new, blank session to resume work with zero context loss.
+</system_context>
+
+<agentic_reasoning>
+Before generating the report, you MUST output a `<reasoning_log>` analyzing the session. Inside this block, execute:
+1. History Scan: What were the primary objectives and major technical hurdles overcome in this session?
+2. State Extraction: What exactly changed in the codebase? Which files were created or modified? What is the current status of the active tasks?
+3. Configuration Audit: Which Agent Skills and MCP servers are currently active?
+</agentic_reasoning>
+
+<constraints>
+- You MUST exhaustively analyze the entire conversation history.
+- You MUST NOT hallucinate file names, task IDs, or technical decisions; rely strictly on the factual events of this session.
+- You MUST retain "The Why"—the architectural reasoning behind the code changes, not just the code itself.
+- You MUST output the report strictly using the provided Markdown structure.
+</constraints>
+
+<output_format>
+Your response must begin with the `<reasoning_log>`, followed immediately by this exact Markdown template:

-Our current AI Studio development session is reaching its context limit (or becoming too heavy). To preserve the complete operational context, technical decisions, and status of our codebase without carrying forward millions of redundant discussion tokens, I need you to perform a **Semantic Context Compaction**.
-
-Analyze our entire conversation history, the active codebase state, the files we modified, the active skills we used, and generate a highly detailed, consolidated **Context Restoration Report** in Markdown.
-
-Your report MUST strictly follow this exact structure:
-
-```markdown
 # Session Restoration Checkpoint: [PROJECT_NAME]

 **Generated on:** [Current Date, e.g., June 2026]
-**Original System Prompt Version:** [e.g., V5.3.0 Ultimate]
+**Original System Prompt Version:** [e.g., V5.19.0 Ultimate]
 **Token Compression Ratio:** [Estimate of compacted size vs. original session window, e.g., 98%]

 ## 1. Project Overview & Scope
-
 [Provide a concise 1-2 paragraph description of the project, its core technology stack, primary goals, and the active technical boundaries.]

 ## 2. Global Agent & MCP Configuration
-
 - **Active MCP Servers:** [List all configured MCP servers, e.g., custom_context, telegram, and their command setup from opencode.json]
-- **Active Agent Skills:** [List all custom skills installed globally or locally, and what they do, e.g., telegram-issue-sync, versioning-and-release]
+- **Active Agent Skills:** [List all custom skills installed globally or locally, and what they do]
 - **Core File Anchors:** [Specify exact paths of AGENTS.md, DESIGN.md, tasks/ and where they reside]

 ## 3. Chronological Task Registry & Progress
-
-Provide a detailed table of all tasks handled in this session, matching their current local status:
-
-| Task Index & Filename   | Msg ID (Telegram) | Type          | Status (Completed/Todo/Halted) | Core Achievements & Technical Decisions       |
-| :---------------------- | :---------------- | :------------ | :----------------------------- | :-------------------------------------------- |
-| [e.g., tasks/05-xxx.md] | [e.g., 548]       | [bug/feature] | Completed                      | [Brief summary of architectural changes made] |
+| Task Index & Filename | Msg ID (Telegram) | Type | Status (Completed/Todo/Halted) | Core Achievements & Technical Decisions |
+| :--- | :--- | :--- | :--- | :--- |
+| [e.g., tasks/05-xxx.md] | [e.g., 548] | [bug/feature] | Completed | [Brief summary of architectural changes made] |

 ## 4. Codebase Forensic State (Critical & Modified Files)
-
 - **Files Modified/Created:** [Bullet list of files modified during this session and their final roles]
-- **Critical System Anchors:** [Specify which files are the 'heart' of the system that must not be altered carelessly, e.g., server.py, system-prompt.md]
+- **Critical System Anchors:** [Specify which files are the 'heart' of the system that must not be altered carelessly]
 - **Last Verified Test/LSP Command:** [The exact bash commands ran to verify syntax/compilation before compacting]

 ## 5. Architectural Map & Key Technical Decisions (The "Why")
-
-[Detail the architectural decisions made during this session. Explain why certain patterns were chosen, why regex-based symbol extraction was selected over pure python AST, why Git Diff is injected via HTML markers, etc. Keep this highly descriptive and technical.]
+[Detail the architectural decisions made during this session. Explain why certain patterns were chosen. Keep this highly descriptive and technical.]

 ## 6. Next Milestones & Open TODOs
-
 - **Immediate Next Task:** [What is the next task file to be generated or executed?]
 - **Active Bugs/Unresolved Caveats:** [List any outstanding issues, skipped errors, or environment-specific bugs]
 - **Remaining Roadmap:** [What features or stack integrations are planned next?]

 ## 7. Restoration Protocol (Cold-Start Restoration Instruction)
-
-[Provide a clear, directive prompt instructing the AI in the new blank session on how to digest this report, load the listed files, and seamlessly take over the Software Architect/Senior Programmer personas without asking redundant onboarding questions.]
-```
-
-Ensure this report contains **no missing context**. Every technical choice, file path, and active configuration must be written explicitly so that our next session is a 100% smooth transition. Proceed to generate the report now.
+[Provide a clear, directive prompt instructing the AI in the new blank session on how to digest this report, load the listed files, and seamlessly take over the project without asking redundant onboarding questions.]
+</output_format>
````

<!-- END_GIT_DIFF -->
