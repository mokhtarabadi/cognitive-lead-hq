# Reusable User Prompt: Session Context Compactor & Restoration Generator

**How to use:** When your AI Studio context window becomes heavily loaded (e.g., approaching 1M tokens), copy the entire text below this block, paste it into the active chat, and let the AI generate your compact restoration report. Then, copy that generated report, open a brand-new blank AI Studio session, and paste it to resume work with 0% context loss and a 99% reduction in active token load.

--- COPY BELOW THIS LINE TO COMPACT SESSIONS ---

## Context Compaction Protocol Request

Our current AI Studio development session is reaching its context limit (or becoming too heavy). To preserve the complete operational context, technical decisions, and status of our codebase without carrying forward millions of redundant discussion tokens, I need you to perform a **Semantic Context Compaction**.

Analyze our entire conversation history, the active codebase state, the files we modified, the active skills we used, and generate a highly detailed, consolidated **Context Restoration Report** in Markdown.

Your report MUST strictly follow this exact structure:

```markdown
# Session Restoration Checkpoint: [PROJECT_NAME]

**Generated on:** [Current Date, e.g., June 2026]
**Original System Prompt Version:** [e.g., V5.3.0 Ultimate]
**Token Compression Ratio:** [Estimate of compacted size vs. original session window, e.g., 98%]

## 1. Project Overview & Scope

[Provide a concise 1-2 paragraph description of the project, its core technology stack, primary goals, and the active technical boundaries.]

## 2. Global Agent & MCP Configuration

- **Active MCP Servers:** [List all configured MCP servers, e.g., custom_context, telegram, and their command setup from opencode.json]
- **Active Agent Skills:** [List all custom skills installed globally or locally, and what they do, e.g., telegram-issue-sync, versioning-and-release]
- **Core File Anchors:** [Specify exact paths of AGENTS.md, DESIGN.md, tasks/ and where they reside]

## 3. Chronological Task Registry & Progress

Provide a detailed table of all tasks handled in this session, matching their current local status:

| Task Index & Filename   | Msg ID (Telegram) | Type          | Status (Completed/Todo/Halted) | Core Achievements & Technical Decisions       |
| :---------------------- | :---------------- | :------------ | :----------------------------- | :-------------------------------------------- |
| [e.g., tasks/05-xxx.md] | [e.g., 548]       | [bug/feature] | Completed                      | [Brief summary of architectural changes made] |

## 4. Codebase Forensic State (Critical & Modified Files)

- **Files Modified/Created:** [Bullet list of files modified during this session and their final roles]
- **Critical System Anchors:** [Specify which files are the 'heart' of the system that must not be altered carelessly, e.g., server.py, system-prompt.md]
- **Last Verified Test/LSP Command:** [The exact bash commands ran to verify syntax/compilation before compacting]

## 5. Architectural Map & Key Technical Decisions (The "Why")

[Detail the architectural decisions made during this session. Explain why certain patterns were chosen, why regex-based symbol extraction was selected over pure python AST, why Git Diff is injected via HTML markers, etc. Keep this highly descriptive and technical.]

## 6. Next Milestones & Open TODOs

- **Immediate Next Task:** [What is the next task file to be generated or executed?]
- **Active Bugs/Unresolved Caveats:** [List any outstanding issues, skipped errors, or environment-specific bugs]
- **Remaining Roadmap:** [What features or stack integrations are planned next?]

## 7. Restoration Protocol (Cold-Start Restoration Instruction)

[Provide a clear, directive prompt instructing the AI in the new blank session on how to digest this report, load the listed files, and seamlessly take over the Software Architect/Senior Programmer personas without asking redundant onboarding questions.]
```

Ensure this report contains **no missing context**. Every technical choice, file path, and active configuration must be written explicitly so that our next session is a 100% smooth transition. Proceed to generate the report now.
