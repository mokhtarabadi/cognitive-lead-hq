---
tags: [mcp, tool-output, agent-facing, conventions]
---

# MCP tool output and input strings address the calling agent

All Python MCP server tool return strings and tool input descriptions are read by autonomous agents (Hands, cognitive executor), never by a human who copies and pastes files. Address the calling agent, point it at the artifact plus the tool it should use, and never write a "Manager:" prefix or a copy/paste-for-the-AI instruction. Pinned by `tests/test_agent_facing_tool_outputs.py`.