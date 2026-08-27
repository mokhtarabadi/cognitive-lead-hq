---
created_at: "2026-08-12T22:52:56.985682+00:00"
status: active
tags: []
updated_at: "2026-08-26T21:30:00.000000+00:00"
---

# Freebuff vendor & source of truth (REVISED 2026-08-26)

**The public source of truth is `github.com/CodebuffAI/freebuff`** (org: **CodebuffAI**, "The free coding agent" — a free-only variant of the Codebuff CLI, see `freebuff/SPEC.md` in that repo). The earlier note (Task 96, 2026-08-13) claiming "vendor is manicode, NOT CodebuffAI" is **FALSIFIED by the actual source**: the current public repo IS under the CodebuffAI org.

- `~/.config/manicode/` is just the CLI's **config-root path** (legacy name) — the binary is Bun-compiled from the `freebuff-private` workspace (build path seen in binary strings: `/home/runner/work/freebuff-private/freebuff-private`), and the repo source references `.manicodeignore` alongside `.codebuffignore`. The config dir name does NOT mean the vendor is "manicode".
- Freebuff = Codebuff CLI built with `FREEBUFF_MODE=true` (strips paid features, subscription, credits, mode switching). Free mode only.
- Free-tier agent family: `base2-free-*` (orchestrator with `spawn_agents`, built-in subagents only) and `base3-free-*` (single-loop, NO `spawn_agents` tool at all). Current CLI harness is **base3** (`CLI_HARNESS = 'base3'` in `cli/src/utils/constants.ts`).
- Free-mode agent gate is SERVER-SIDE: `FREE_MODE_AGENT_MODELS` allowlist in `common/src/constants/free-agents.ts` — "Only allowlisted agent+model combinations cost 0 credits in this mode. This prevents abuse by users trying to use arbitrary agents for free." Custom agents are NOT in it → any free-tier request on them 403s (`free_mode_invalid_agent_model`) or is metered.
- Client loader requires `model` on `.agents/*.ts`: `sdk/src/agents/load-agents.ts` (`if (!agentDefinition?.id || !agentDefinition?.model) continue`) — model-less files are SILENTLY SKIPPED on 0.0.156. Our `freebuff/agents/*.ts` omit `model` (v1.1.0 fix for 0.0.149) → they do not even load on 0.0.156.
- Always-loaded roles = the knowledge-file system (NOT a role/persona feature): home `~/.AGENTS.md` > `~/.CLAUDE.md`; project `AGENTS.md` > `CLAUDE.md` > `*.knowledge.md` per directory; `~/.knowledge.md` and bare `knowledge.md` are IGNORED (left the priority list). The Cognitive Executive Role ships in `freebuff/AGENTS.global.md` → `~/.AGENTS.md`; see `docs/freebuff-documents.md` + the `freebuff-documents` skill.
- Reference by ID (Tasks 96/98 + 2026-08-26 source audit), never by a Kanban path.
