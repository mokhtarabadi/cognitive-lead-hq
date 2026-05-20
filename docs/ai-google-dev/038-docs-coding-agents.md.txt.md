---
title: Coding Assistant Setup with Gemini MCP and Skills
url: https://ai.google.dev/gemini-api/docs/coding-agents.md.txt
source: llms
fetched_at: 2026-04-29T11:17:18.303914194-03:00
rendered_js: false
word_count: 538
summary: Enhance AI coding assistants by integrating the Gemini Docs MCP server and specialized API skills for real-time documentation and best practices.
tags:
    - ai-coding-assistant
    - gemini-api
    - mcp
    - model-context-protocol
    - agent-configuration
    - developer-tools
category: configuration
optimized: true
optimized_at: '2026-04-29T14:17:12Z'
---
AI coding assistants have training data cutoffs and may miss new API features, suggesting generic patterns instead of optimized Gemini approaches. Keep your assistant current by setting up the **Gemini Docs MCP** and **Gemini API Skills**. They are designed to work together for complete coverage but can also be used independently.

## Connect the Gemini Docs MCP

Connect your coding agent to the public MCP server at `https://gemini-api-docs-mcp.dev` to access the latest APIs, code updates, and optimal configuration examples.

Run this in your agent's terminal or project root:

```bash
npx add-mcp "https://gemini-api-docs-mcp.dev"
```

This installs a `search_documentation` function that retrieves real-time API definitions and integration patterns from official Gemini documentation.

## Add API Development Skills

Skills provide baked-in rules and best practices (correct SDK, current model versions) directly in your assistant's context. When both MCP and skills are installed, the skill uses the MCP service for documentation. Without MCP, the skill falls back to fetching `llms.txt` from `ai.google.dev`.

Install via [skills.sh](https://skills.sh) (recommended) or [Context7](https://context7.com).

### gemini-api-dev

Foundational skill for general-purpose Gemini development:

- Prompt routing to current models (e.g., Gemini 3.1 Pro/Flash), avoiding deprecated models
- Multimodal prompting, function calling, structured outputs, and common integration patterns

#### Install with skills.sh

```bash
npx skills add google-gemini/gemini-skills --skill gemini-api-dev --global
```

#### Install with Context7

```bash
npx ctx7 skills install /google-gemini/gemini-skills gemini-api-dev
```

### gemini-live-api-dev

For building real-time conversational AI applications with Gemini Live API:

- WebSocket connections for low-latency streaming
- Streaming audio, video, and text
- Voice activity detection and barge-in support

#### Install with skills.sh

```bash
npx skills add google-gemini/gemini-skills --skill gemini-live-api-dev --global
```

#### Install with Context7

```bash
npx ctx7 skills install /google-gemini/gemini-skills gemini-live-api-dev
```

### gemini-interactions-api

For building apps with the [Interactions API](https://ai.google.dev/gemini-api/docs/interactions) — a unified interface for agentic applications:

- Text generation, multi-turn chat, and streaming
- Function calling, structured output, and image generation
- Background execution and Deep Research agents
- Server-side conversation state management
- Python and TypeScript SDK patterns

#### Install with skills.sh

```bash
npx skills add google-gemini/gemini-skills --skill gemini-interactions-api --global
```

#### Install with Context7

```bash
npx ctx7 skills install /google-gemini/gemini-skills gemini-interactions-api
```

## Verify installation

Ask your agent: "How do I use context caching with the Gemini API?"

A successful setup will:

- **Provide accurate code**: Reference specific Gemini methods like `cacheContent` or `cachedContents.create` from current endpoints.
- **Use the MCP Tool**: Show connection to the **Gemini Docs MCP Server** or use of the `search_documentation` tool.
- **Invoke loaded skills**: Display "Using skill: gemini-api-dev" indicator.

### Verify manifestations & tools

| Environment | MCP Verification | Skills Verification |
|---|---|---|
| **Claude Code** | `/mcp` in terminal → active servers and `search_documentation` tools | `/skills` → list active manifests |
| **Cursor** | **Settings > Features > MCP** → server "Connected" | **Settings > Rules** → skill under "Agent Decides" |
| **Antigravity** | **Customizations > Connections** → MCP status | `/skills list` or **Customizations > Rules** |
| **Gemini CLI** | `gemini mcp list` or `/mcp list` | `gemini skills list` or `/skills` |
| **Copilot** | `@gemini /mcp` → active data connectors | `@gemini /skills` → active extensions |

## Troubleshooting

### Agent didn't discover the skill

Most agents index skills only on startup.

**Fix**: Completely restart your IDE (Cursor/VS Code) or exit and re-open your terminal-based agent (Claude Code).

### Global vs. local conflict

Installed with `--global` but the agent ignores it in favor of project-specific rules.

**Fix**: Install directly in the project root without `--global`:

```bash
npx skills add google-gemini/gemini-skills --skill gemini-api-dev
```

## Resources

- [Gemini API skills on GitHub](https://github.com/google-gemini/gemini-skills)
- [[001-docs-ai-studio-quickstart.md.txt.md|Quickstart]]
- [[014-docs-libraries.md.txt.md|Libraries]]

#gemini-api #mcp #coding-assistant #developer-tools
