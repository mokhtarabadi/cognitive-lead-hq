---
name: code-search
description: Rules for navigating the codebase and finding relevant code chunks using Semble.
---

# Code Search Strategy

When exploring the codebase or looking for specific implementations, ALWAYS prefer the `semble` MCP tools over standard `grep`, `glob`, or `read` to save context tokens.

## Workflow
1. Use the `semble_search` tool to find code by describing what it does in natural language (e.g., "authentication flow") or naming a specific symbol/function.
2. Review the highly targeted code chunks returned by Semble.
3. If a chunk looks promising but you need more context around it, use `semble_find_related` passing the `file_path` and `line` number.
4. ONLY use the native `read` tool to read a full file if the Semble chunks are insufficient to perform the required edits.
