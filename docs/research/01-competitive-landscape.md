# Research Report 01 — Competitive Landscape: Related Projects

> **Purpose:** Map the ecosystem of projects related to Cognitive Lead AI HQ, for the Orchestrator Brain's strategic review.
> **Date:** 2026-08-18
> **Method:** Deep web research (search + full README/doc fetches) across 6 categories.

---

## Executive Summary

No direct clone of Cognitive Lead AI HQ exists — no other repository combines *system prompt + MCP servers + skills + Kanban task lifecycle + QA loop* in one documentation-only HQ. The closest competitor is `obra/superpowers` (273k stars), which shares the skills concept but is a methodology plugin, not a full orchestration HQ. The biggest ecosystem gap: nobody else ships a **Brain/Hands XML task-block protocol with a QA persona loop** — that is this project's moat.

---

## Tier 1 — Closest Cousins (same DNA: skills + prompts + orchestration)

| Project | Stars | URL | Relevance |
|---|---|---|---|
| obra/superpowers | ~273k | https://github.com/obra/superpowers | Agentic skills framework + full dev methodology; multi-platform (Claude Code, Codex, OpenCode, Cursor, Gemini CLI, Copilot CLI, Devin, Kimi, Pi, Hermes, Grok, Factory Droid, Antigravity). The most successful version of this repo's `skill-templates/` concept |
| anthropics/skills | ~170k | https://github.com/anthropics/skills | Official Anthropic Agent Skills repo — the SKILL.md standard this project follows; includes `spec/` and `template/` |
| danielrosehill/AI-Orchestration-System-Prompts | — | https://github.com/danielrosehill/AI-Orchestration-System-Prompts | System prompts for orchestration agents in an AI assistant network — same Brain/Orchestrator concept |
| strands-agents/agent-sop | ~1.1k | https://github.com/strands-agents/agent-sop | Markdown-based SOPs (Standard Operating Procedures) with RFC 2119 constraints; multi-modal distribution (MCP, Skills, SDK) |
| obviousworks/agentic-coding-rulebook | ~11 | https://github.com/obviousworks/agentic-coding-rulebook | "Constitutional framework" (AGENTS.md-style rules) to discipline AI agents; universal AGENTS.md standard + symlink strategy |

## Tier 2 — System Prompt Engineering (vs. `system-prompt.md` + `prompts/`)

| Project | URL | Notes |
|---|---|---|
| dontriskit/awesome-ai-system-prompts | https://github.com/dontriskit/awesome-ai-system-prompts | Curated system prompts from top AI tools |
| OlehDatsyk/awesome-system-prompts | https://github.com/OlehDatsyk/awesome-system-prompts | Production-ready prompts for devs/businesses |
| System Prompt Library (Daniel Rosehill) | https://prompts.danielrosehill.com | 937+ open-source system prompts |
| System Prompts Directory | https://ainsider.beehiiv.com/p/system-prompts-directory | 20,000+ lines of open prompts/templates |
| parmsam/llm-dev-best-practices | https://github.com/parmsam/llm-dev-best-practices | Best practices incl. system prompt versioning in git — mirrors this repo's v8.4.6 build process |

## Tier 3 — MCP Servers & Context (vs. `mcp-context-server/`)

| Project | URL | Notes |
|---|---|---|
| punkpeye/awesome-mcp-servers | https://github.com/punkpeye/awesome-mcp-servers | The canonical MCP server collection |
| mcp-agents-ai/mcp-agents-hub | https://github.com/mcp-agents-ai/mcp-agents-hub | Open-source ecosystem for building/discovering MCP servers |
| mcpservers.org | https://mcpservers.org | 9,800+ MCP servers directory |

## Tier 4 — Agent Memory (vs. `mcp-memory-server/`)

| Project | Stars | URL | Notes |
|---|---|---|---|
| mem0ai/mem0 | ~63.5k | https://github.com/mem0ai/mem0 | Universal memory layer; entity linking, hybrid retrieval, temporal reasoning; memory-benchmarks |
| Zep (Graphiti) | — | https://github.com/getzep/zep | Temporal knowledge-graph memory |
| Letta (MemGPT) | — | https://github.com/letta-ai/letta | Production evolution of MemGPT |
| ipiton/agent-memory-mcp | — | https://github.com/ipiton/agent-memory-mcp | Memory + docs + repo context layer MCP — closest to our memory server |
| alphaonedev/ai-memory-mcp | — | https://github.com/alphaonedev/ai-memory-mcp | SQLite persistent memory, relevance ranking |
| OmniMem | — | https://omnimem.org | Self-hosted memory MCP with contradiction detection |

## Tier 5 — Multi-Agent Orchestration Frameworks (vs. Brain/Hands pattern)

| Project | Stars | URL | Notes |
|---|---|---|---|
| LangGraph | ~39.9k | https://github.com/langchain-ai/langgraph | Stateful graph orchestration; durable execution, human-in-the-loop, checkpointers + stores |
| CrewAI | ~57.2k | https://github.com/crewAIInc/crewAI | Role-based agent teams (Crews) + event-driven Flows; control plane |
| AutoGen / Microsoft Agent Framework | — | https://github.com/microsoft/autogen | Conversational multi-agent loops |
| OpenAI Agents SDK | — | https://github.com/openai/openai-agents-python | Official orchestration SDK |
| mcp-agent | — | https://github.com/lastmile-ai/mcp-agent | Planner/Orchestrator pattern over MCP |

## Tier 6 — Agent QA & Evaluation (vs. the QA loop)

| Project | URL | Notes |
|---|---|---|
| Anthropic "Demystifying evals for AI agents" | https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents | The definitive eval framework: task/trial/grader/transcript/outcome/harness; pass@k vs pass^k; 8-step roadmap |
| awslabs/agent-evaluation | https://github.com/awslabs/agent-evaluation | LLM evaluator orchestrating conversations with target agents |
| partarstu/agentic-qa-framework | https://github.com/partarstu/agentic-qa-framework | QuAIA — QA lifecycle automation with agents |
| agenticloops-ai/agentic-ai-engineering | https://github.com/agenticloops-ai/agentic-ai-engineering | Testing/evaluation module for non-deterministic agents |

---

## Key Takeaways

1. **Differentiated niche:** No repo combines system prompt + MCP servers + skills + Kanban + QA loop in one documentation-only HQ.
2. **Closest competitor:** `obra/superpowers` — same skills concept, but a methodology plugin, not an orchestration HQ.
3. **Biggest ecosystem gap:** the Brain/Hands XML task-block protocol with a QA persona loop is unique to this project.
4. **Fastest-moving areas:** Agent Skills standardization (agentskills.io), automated evals, and semantic memory are where the ecosystem is converging in 2026.