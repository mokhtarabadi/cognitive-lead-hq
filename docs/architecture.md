# Cognitive Lead AI HQ — Architecture

## Overview

The Cognitive Lead AI HQ is the headquarters repository for a multi-agent AI orchestration platform. It contains system prompts, MCP servers, agent definitions, and reusable skill templates. It is a **documentation-only** repository — no target application code is generated here.

## Topology

Two operating modes:

### True Manual Mode (External Brain)
- The Brain runs in an external chat interface (Claude Web, ChatGPT, etc.) with NO access to the local filesystem or terminal.
- The Manager acts as the human courier: the Hands emits fenced prompts and task paths; the Manager copies them to the external Brain; the Brain emits fenced XML blocks; the Manager copies them to the Hands.
- No `mcp-brain-bridge` communication.

### Automatic Mode (MCP Brain Bridge)
- OpenCode runs with `mcp-brain-bridge` active.
- The Hands calls `brain_turn` directly via the MCP server.
- The Manager supervises and approves gates, never ferrying task text.
- 100% headless MCP cycle.

## System Architecture

### MCP Servers (Singletons on 127.0.0.1)
| Port | Server | Purpose |
|------|--------|---------|
| 8101 | mcp-lint-server | Task file linting and validation |
| 8102 | mcp-context-server | Context gathering, graph building, signature extraction |
| 8103 | mcp-memory-server | Persistent project memory |
| 8105 | mcp-brain-bridge | Brain turn orchestration (the ONLY automation path) |
| 8106 | mcp-telegram-server | Telegram integration |
| 8107 | blowsh-singleton | Web search, fetch, crawl |
| 8108 | mcp-planner-server | Daily workload and queue circuit-breaking |

### Agent Architecture
- **Brain (Cognitive Lead AI):** Receives system prompt + task context. Produces XML task blocks. Runs in external chat (manual) or via MCP (automatic).
- **Hands (Cognitive Executor):** Local execution agent. Reads task files, executes XML instructions, runs tests, stages diffs, manages Kanban state.
- **Cognitive Discovery:** Read-only subagent for context gathering.

### 9-Step Production Line
1. Discovery (context gathering)
2. Brainstorming (if cross-disciplinary)
3. Blueprint (architectural design)
4. Approval Gate (Manager approves plan)
5. Implementation (Hands executes)
6. QA (adversarial testing)
7. Code Review (audit vs blueprint)
8. Staging (diff injection)
9. Closure (Manager approves, commit)

### Key Data Flows
- Brain → Hands: XML task blocks via `brain_turn` (automatic) or fenced blocks (manual)
- Hands → Brain: context reports, execution logs, verification evidence
- Hands → Manager: approval requests, QA/review verdicts, closure requests
- Manager → Hands: approval words, relay answers

## Layer Boundaries
- `prompts/` — Brain-facing instructions (system prompt fragments)
- `agents/` — Hands-facing agent definitions
- `mcp-*/` — MCP server implementations (Python, stdlib-only where specified)
- `skill-templates/` — Reusable skill definitions
- `tasks/` — Kanban task files (single source of truth for work items)
- `docs/` — Project documentation and conventions
- `scripts/` — Build and maintenance scripts
