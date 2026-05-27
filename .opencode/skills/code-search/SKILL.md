---
name: code-search
description: Mandatory workflow for exploring the codebase and gathering context for AI Studio.
---

# Code Search & Discovery Strategy

You are the Executor. Your job is to extract codebase context so the Manager can upload it to the Orchestrator (Google AI Studio).

**CRITICAL GUARDRAIL:** You MUST NOT read, analyze, or process the generated reports yourself. You are strictly a data gatherer in this phase.

## Discovery Workflow

1. **Map the Structure:** Call the `get_directory_tree` MCP tool on the target directory (e.g., `.`, `src/`, `packages/`).
2. **Target Files:** Analyze the ASCII tree to identify the exact files relevant to the Manager's request.
3. **Compile Report:** Call the `read_source_files` MCP tool, passing the list of targeted file paths. This tool will safely read the files (respecting `.gitignore`) and compile them into a single Markdown file inside the `context-reports/` directory.
4. **Halt and Handover:** Once the `read_source_files` tool returns the generated file path, **STOP**. Do NOT use your `read` tool to open the report.
5. **Output Message:** Output the following exact message to the Manager:
   > "✅ Discovery complete. I have compiled the context report here: `[INSERT_FILE_PATH]`.
   > **Manager:** Please upload this file to AI Studio for the Orchestrator's review."
