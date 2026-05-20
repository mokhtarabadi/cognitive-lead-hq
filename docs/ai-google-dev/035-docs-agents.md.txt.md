---
title: Agents Overview
url: https://ai.google.dev/gemini-api/docs/agents.md.txt
source: llms
fetched_at: 2026-04-29T11:17:12.532079894-03:00
rendered_js: false
word_count: 251
summary: This document provides an overview of building autonomous agents using Gemini models, highlighting key technical components, prompting strategies, and integration with popular orchestration frameworks.
tags:
    - gemini-api
    - ai-agents
    - tool-calling
    - orchestration-frameworks
    - autonomous-agents
category: concept
optimized: true
optimized_at: '2026-04-29T14:17:12Z'
---
# Agents Overview

Agents leverage Gemini models, tools, and reasoning to perform complex multi-step tasks. Unlike single model calls, agents plan actions, interact with external systems, and synthesize information.

## Key Features

Build agents using these Gemini API features:

- **[[049-docs-models-gemini-2.5-flash|Gemini models]]** — Core intelligence for reasoning and language understanding
- **[Tools](https://ai.google.dev/gemini-api/docs/tools)** — Connect to real-world info/actions (built-in: Google Search, Maps, Code Execution; or custom)
- **[Function calling](https://ai.google.dev/gemini-api/docs/function-calling)** — Define and connect custom tools/APIs
- **[[027-docs-thinking|Thinking]]** — Enhanced reasoning and planning for complex tasks
- **[[037-docs-long-context|Long context]]** — Maintain state over extended interactions

## Available Agents

- **[Deep Research Agent](https://ai.google.dev/gemini-api/docs/deep-research)** — Autonomous agent for multi-step research: market analysis, due diligence, literature reviews

## Building Agents

Agents combine models (reasoning/"brain") and tools (execution/"hands"). Orchestration frameworks typically manage memory, plan loops, and complex tool chaining.

> [!tip]
> For reliable multi-step workflows, craft instructions that explicitly control reasoning and planning. Gemini handles general reasoning well; agents benefit from prompts enforcing persistence through issues, risk assessment, and proactive planning.

See [[023-docs-prompting-strategies#agentic-workflows|Agentic Workflows]] for prompt design strategies. A [system instruction template](https://ai.google.dev/gemini-api/docs/prompting-strategies#agentic-si-template) improved agentic benchmark performance ~5%.

## Agent Frameworks

Gemini integrates with leading open-source frameworks:

- **[[013-docs-langgraph-example|LangChain / LangGraph]]** — Stateful, complex flows and multi-agent systems via graph structures
- **[LlamaIndex](https://ai.google.dev/gemini-api/docs/llama-index)** — Connect agents to private data for RAG-enhanced workflows
- **[[008-docs-crewai-example|CrewAI]]** — Orchestrate collaborative, role-playing autonomous agents
- **[[031-docs-vercel-ai-sdk-example|Vercel AI SDK]]** — Build AI-powered UIs and agents in JavaScript/TypeScript
- **[Google ADK](https://google.github.io/adk-docs/get-started/python/)** — Open-source framework for interoperable AI agents

#gemini-api #ai-agents #tool-calling #orchestration-frameworks #autonomous-agents
