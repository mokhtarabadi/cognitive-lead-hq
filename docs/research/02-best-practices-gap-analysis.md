# Research Report 02 — Best Practices Gap Analysis

> **Purpose:** Identify what top projects do that Cognitive Lead AI HQ currently does NOT support, with adoption paths.
> **Date:** 2026-08-18
> **Sources:** obra/superpowers, anthropics/skills, mem0, strands-agents/agent-sop, obviousworks/agentic-coding-rulebook, Anthropic Engineering, LangGraph, CrewAI, agentskills.io.

---

## What HQ Currently Supports (baseline)

- **Platforms:** OpenCode + Freebuff (2)
- **MCP servers:** context (trees, signatures, staging/commit), lint (markdown/task validation), memory (flat markdown files, keyword search)
- **System prompt:** modular fragments + assembly script (v8.4.6)
- **Skills:** 27 templates in `skill-templates/`
- **Task lifecycle:** V6 Kanban (backlog → in-progress → qa → completed → archive)
- **QA loop:** manual persona-based review (QA Engineer persona in the Brain)
- **Memory:** `project-memory` skill + `mcp-memory-server` (markdown + full-text search)
- **Governance:** ZAC (Zero-Autonomous-Commit), versioning skill, changelog discipline

---

## The 15 Gaps (what top projects do that we don't)

### Gap 1 — Automated Eval Harness *(Anthropic, strands)*

- **They do:** task → trial → grader → assertions → transcript → outcome → harness → suite; multi-turn evals; LLM judges with human calibration; capability vs. regression evals; pass@k / pass^k metrics; eval-driven development (define success criteria BEFORE building).
- **We do:** manual QA persona review of task files after implementation.
- **Adoption:** `evals/` directory + `scenarios/*.yaml` + MCP lint tool running task-file evals; seed with 20–50 tasks derived from the 100 archived task files.

### Gap 2 — Session-Start Hooks & Bootstrap *(superpowers)*

- **They do:** SessionStart hook injects a bootstrap so skills auto-trigger; per-platform hook formats (Claude Code `hooks.json`, Cursor camelCase, Codex `hooks: {}` anti-discovery); "load the bootstrap at session start" is the one rule that makes or breaks a harness port.
- **We do:** skills load only when explicitly named in the XML task block (Skill Auto-Loading Matrix exists but is passive).
- **Adoption:** `hooks/` directory + session-start bootstrap that activates the Skill Auto-Loading Matrix automatically.

### Gap 3 — Multi-Platform Plugin Manifests *(superpowers, mem0)*

- **They do:** `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.devin-plugin/`, `.kimi-plugin/`, `.hermes-plugin/`, `.opencode/`, `gemini-extension.json` — 14 platforms from one source; marketplace publishing (Anthropic official marketplace, `skills-dist` branch).
- **We do:** OpenCode + Freebuff only.
- **Adoption:** generate per-platform plugin manifests from the existing skill templates (they are already platform-agnostic markdown).

### Gap 4 — Semantic Memory *(mem0)*

- **They do:** single-pass ADD-only extraction (~7K tokens, ~1s p50); entity linking; multi-signal retrieval (semantic + BM25 + entity fusion); temporal reasoning; User/Session/Agent scopes; auto-capture; agent self-provisioning (`mem0 init --agent`).
- **We do:** flat markdown files with keyword search; manual `store_memory` only.
- **Adoption:** upgrade `mcp-memory-server` with embeddings + hybrid retrieval + entity extraction; add auto-capture from task execution summaries.

### Gap 5 — Standardized SOP Format *(strands)*

- **They do:** Overview → Parameters (required/optional + defaults) → Steps with RFC 2119 constraints (MUST/SHOULD/MAY) → Examples → Troubleshooting; `validate-sop.sh` structure validator; `agent-sop-author` skill.
- **We do:** free-form markdown SOPs.
- **Adoption:** convert SOPs to the standardized format; add validator to `mcp-lint-server`; add `agent-sop-author` skill.

### Gap 6 — Trace Recording *(Anthropic, LangGraph)*

- **They do:** full transcript of every trial (outputs, tool calls, reasoning, intermediate results); outcome = final environment state, not what the agent claimed.
- **We do:** no execution records; debugging is reactive.
- **Adoption:** record a transcript per task execution (tool calls + reasoning + final diff state) into the task file or a `traces/` directory.

### Gap 7 — Two-Tier Testing *(superpowers)*

- **They do:** `tests/` = infrastructure tests (bash suites per harness, planted bugs to verify review skills catch them); `evals/` = skill-behavior tests with real agent sessions judged by LLM; micro-testing methodology (sample phrasing against no-guidance control); never text-assert skills ("string-presence trap").
- **We do:** only `tests/test_mcp_servers.py`.
- **Adoption:** add per-skill behavior tests with planted-bug scenarios; add infrastructure tests for hooks/plugins.

### Gap 8 — Memory Benchmarks *(mem0)*

- **They do:** open-sourced `memory-benchmarks` repo; LoCoMo 92.5, LongMemEval 94.4, BEAM 1M 64.1; reproducible numbers.
- **We do:** no memory quality measurement.
- **Adoption:** LongMemEval-style suite for `mcp-memory-server`.

### Gap 9 — Version-Bump Manifest *(superpowers)*

- **They do:** `.version-bump.json` declares every file carrying the version; `bump-version.sh` with `--check` (drift detection) and `--audit` (undeclared version strings); `RELEASE-NOTES.md` as single release source.
- **We do:** manual versioning via skill.
- **Adoption:** `.version-bump.json` covering system-prompt version + 27 skill templates + CHANGELOG.

### Gap 10 — Capability vs. Regression Eval Split *(Anthropic)*

- **They do:** capability evals start at low pass rate (hill to climb); regression evals at ~100% (protect against backsliding); graduated suites; saturation monitoring.
- **We do:** no quality baselines at all.
- **Adoption:** two suites; graduate capability tasks into regression suite as they saturate.

### Gap 11 — Eval-Driven Development *(Anthropic)*

- **They do:** build evals to define planned capabilities BEFORE agents can fulfill them; evals force teams to specify what success means; enable fast model upgrades (days vs weeks).
- **We do:** QA is after-the-fact.
- **Adoption:** require success criteria + eval task in every implementation task template.

### Gap 12 — Durable Execution / Checkpointing *(LangGraph)*

- **They do:** checkpointers (thread-scoped graph state: conversation continuity, human-in-the-loop, time travel, fault tolerance) + stores (cross-thread durable data); resume from exactly where execution left off; retention policies for unbounded checkpoint growth.
- **We do:** no resume-from-failure; interrupted tasks restart from scratch.
- **Adoption:** checkpoint task execution state (e.g., per-step markers in task files) enabling resume.

### Gap 13 — Observability / Tracing *(LangGraph/LangSmith, CrewAI)*

- **They do:** trace execution paths, state transitions, runtime metrics (n_turns, n_toolcalls, n_total_tokens, time_to_first_token); production monitoring; A/B testing.
- **We do:** zero telemetry.
- **Adoption:** tracked_metrics block in task files; simple metrics collection in MCP servers.

### Gap 14 — SOP Multi-Modal Distribution *(strands)*

- **They do:** one SOP source → MCP server prompts (`--sop-paths`), Cursor commands, Agent Skills (progressive disclosure), Python SDK; marketplace publishing on release.
- **We do:** markdown only.
- **Adoption:** expose SOPs as MCP prompts; generate SKILL.md variants automatically.

### Gap 15 — Security Rules & Guardrails *(obviousworks)*

- **They do:** dedicated `security_rules.md`, `performance_rules.md`, `testing_rules.md`; explicit guardrails against AI-generated vulnerabilities; token-optimized rules.
- **We do:** no dedicated security rules file.
- **Adoption:** `docs/security_rules.md` + lint checks for secrets/prompt-injection patterns.

---

## Consolidated Priority Matrix

| # | Practice | Source | Effort | Value |
|---|---|---|---|---|
| 1 | Eval harness (task/trial/grader/transcript, pass^k) | Anthropic | High | 🔥🔥🔥🔥🔥 |
| 2 | Session-start hooks + bootstrap | superpowers | Low | 🔥🔥🔥🔥🔥 |
| 3 | Multi-platform plugin manifests | superpowers/mem0 | Medium | 🔥🔥🔥🔥 |
| 4 | Semantic memory (entity linking, hybrid retrieval) | mem0 | Medium | 🔥🔥🔥🔥 |
| 5 | Standardized SOP format + validator | strands | Low | 🔥🔥🔥🔥 |
| 6 | Trace recording | Anthropic/LangGraph | Medium | 🔥🔥🔥🔥 |
| 7 | Two-tier testing (infrastructure vs. behavior) | superpowers | Medium | 🔥🔥🔥 |
| 8 | Memory benchmarks | mem0 | Low | 🔥🔥🔥 |
| 9 | Version-bump manifest | superpowers | Low | 🔥🔥🔥 |
| 10 | Capability vs. regression split | Anthropic | Medium | 🔥🔥🔥 |
| 11 | Eval-driven development | Anthropic | Medium | 🔥🔥🔥 |
| 12 | Durable execution / checkpointing | LangGraph | High | 🔥🔥 |
| 13 | Observability / tracing | LangGraph/CrewAI | High | 🔥🔥 |
| 14 | SOP multi-modal distribution | strands | Medium | 🔥🔥 |
| 15 | Security rules file | obviousworks | Low | 🔥🔥 |

**Immediate wins (low effort, high value):** #2 hooks/bootstrap, #5 SOP format, #8 memory benchmarks, #9 version-bump manifest, #15 security rules.