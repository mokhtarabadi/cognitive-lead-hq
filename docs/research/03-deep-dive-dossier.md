# Research Report 03 — Deep Dive Dossier: Best Practices in Detail

> **Purpose:** Full technical detail of the best practices extracted from top projects, for the Orchestrator Brain's design work.
> **Date:** 2026-08-18
> **Sources:** Anthropic Engineering (Jan 2026), obra/superpowers (v6.3.0), mem0 (v3 algorithm), strands-agents/agent-sop, LangGraph docs, agentskills.io spec.

---

## 1. Anthropic's Eval Framework — The Complete Blueprint

### 1.1 Vocabulary

| Term | Definition |
|---|---|
| Task | A single test with defined inputs + success criteria |
| Trial | One attempt at a task (run multiple trials — model output varies) |
| Grader | Logic scoring an aspect of performance; multiple graders per task, each with multiple assertions/checks |
| Transcript/Trace | Complete record of a trial: outputs, tool calls, reasoning, intermediate results |
| Outcome | Final state in the environment (≠ what the agent *said* — e.g., "flight booked" claim vs. actual DB reservation) |
| Evaluation harness | Infrastructure running evals end-to-end: instructions, tools, concurrent runs, recording, grading, aggregation |
| Agent harness/scaffold | The system enabling the model to act as an agent |
| Evaluation suite | Collection of tasks measuring a capability (e.g., refunds + cancellations + escalations) |

### 1.2 The Three Grader Types

**Code-based** (fast, cheap, objective, reproducible):
- String match (exact/regex/fuzzy), binary tests (fail-to-pass, pass-to-pass), static analysis (lint/type/security), outcome verification, tool-call verification, transcript analysis (turns/tokens)
- Weakness: brittle to valid variations

**Model-based (LLM-as-judge)** (flexible, scalable, captures nuance):
- Rubric-based scoring, natural-language assertions, pairwise comparison, reference-based evaluation, multi-judge consensus
- Needs calibration with human graders; give the LLM an **"Unknown" escape hatch** to avoid hallucinated grades; grade each dimension with an **isolated judge** rather than one judge for everything

**Human** (gold standard, calibrates model graders):
- SME review, crowdsourced judgment, spot-check sampling, A/B testing, inter-annotator agreement

**Scoring modes:** weighted (combined scores hit threshold), binary (all must pass), or hybrid.

### 1.3 Capability vs. Regression Evals

- **Capability evals:** "What can this agent do well?" — start at LOW pass rate, give the team a hill to climb
- **Regression evals:** "Does it still handle everything it used to?" — should be ~100% pass rate; protect against backsliding
- **Graduation:** once capability evals hit high pass rates, they become the regression suite

### 1.4 The Two Key Metrics

- **pass@k** — probability of ≥1 success in k attempts (rises with k; "shots on goal")
- **pass^k** — probability ALL k trials succeed (falls with k; consistency bar)
- At k=1 they're identical; at k=10 they tell opposite stories. Use pass@k for tools where one success matters, pass^k for customer-facing consistency.

### 1.5 The 8-Step Roadmap (zero-to-one)

1. **Start early** — 20–50 simple tasks from real failures is enough (80/20 approach; evals get harder to build the longer you wait)
2. **Start with what you already test manually** — convert bug-tracker/support-queue failures into test cases
3. **Write unambiguous tasks with reference solutions** — two domain experts must independently reach the same verdict; a 0% pass@100 usually means a broken task, not an incapable agent
4. **Build a robust harness with a stable environment** — isolated clean state per trial (shared state = correlated failures; Claude once cheated by reading git history from previous trials!)
5. **Design graders thoughtfully** — grade the *output*, not the path (agents find valid approaches you didn't anticipate); build in **partial credit**; calibrate LLM judges against humans; make graders bypass-resistant
6. **Check the transcripts** — failures should seem *fair*; reading transcripts is how you verify the eval measures what matters
7. **Monitor for saturation** — an eval at 100% tracks regressions but gives no improvement signal
8. **Maintain suites long-term** — dedicated evals team owns infrastructure; domain experts contribute tasks; **eval-driven development**: build evals to define planned capabilities *before* agents can fulfill them

### 1.6 Concrete Eval Config (Anthropic's illustrative YAML)

```yaml
task:
  id: "fix-auth-bypass_1"
  graders:
    - type: deterministic_tests
      required: [test_empty_pw_rejected.py, test_null_pw_rejected.py]
    - type: llm_rubric
      rubric: prompts/code_quality.md
    - type: static_analysis
      commands: [ruff, mypy, bandit]
    - type: state_check
      expect:
        security_logs: {event_type: "auth_blocked"}
    - type: tool_calls
      required:
        - {tool: read_file, params: {path: "src/auth/*"}}
  tracked_metrics:
    - type: transcript
      metrics: [n_turns, n_toolcalls, n_total_tokens]
    - type: latency
      metrics: [time_to_first_token, output_tokens_per_sec]
```

### 1.7 The Swiss Cheese Model (holistic understanding)

No single layer catches everything — combine: **automated evals** (pre-launch + CI/CD) → **production monitoring** (post-launch ground truth) → **A/B testing** (validated changes) → **user feedback** (triage constantly) → **manual transcript review** (weekly sampling) → **systematic human studies** (calibrate LLM graders).

---

## 2. obra/superpowers — The 273k-Star Methodology

### 2.1 The 16-Skill Library

| Category | Skills |
|---|---|
| Testing | `test-driven-development` (RED-GREEN-REFACTOR + anti-patterns doc) |
| Debugging | `systematic-debugging` (4-phase root-cause), `verification-before-completion` |
| Collaboration | `brainstorming` (Socratic refinement, saves design doc), `writing-plans` (2–5 min bite-sized tasks, exact file paths, complete code, verification steps), `executing-plans` (batch + human checkpoints), `dispatching-parallel-agents`, `requesting-code-review` (pre-review checklist), `receiving-code-review` (no-defensiveness discipline), `using-git-worktrees`, `finishing-a-development-branch` (merge/PR/keep/discard menu), `subagent-driven-development` (two-stage review: spec compliance → code quality) |
| Meta | `writing-skills` (skill-authoring best practices), `using-superpowers` (session-start bootstrap) |

### 2.2 The 7-Step Mandatory Workflow

1. **brainstorming** → 2. **using-git-worktrees** (isolated branch + clean test baseline) → 3. **writing-plans** → 4. **subagent-driven-development** (fresh subagent per task, two-stage review) → 5. **test-driven-development** (delete code written before tests!) → 6. **requesting-code-review** (severity-ranked issues; critical blocks) → 7. **finishing-a-development-branch**

> Doctrine: *"The agent checks for relevant skills before any task. Mandatory workflows, not suggestions."* — skills auto-trigger via bootstrap injected at session start.

### 2.3 The Hook System

- `hooks/hooks.json` — Claude Code **SessionStart** hook (`startup|clear|compact`, deliberately NOT `resume`), injects the bootstrap
- `hooks/hooks-cursor.json` — Cursor's camelCase format
- `run-hook.cmd` — cross-platform wrapper (Windows-safe)
- **Critical bug lesson:** Codex declares `hooks: {}` explicitly because an absent hooks field makes Codex auto-discover the Claude hooks file and re-register it (fixed in v6.1.1)
- **The one rule that makes or breaks a harness port:** *load the bootstrap at session start*

### 2.4 Two-Tier Testing

- **`tests/`** = plugin-infrastructure tests: bash suites per harness (`tests/claude-code/` plants SQLi/plaintext-password bugs to verify review skills catch them; `tests/opencode/` has 15 regression tests; `tests/shell-lint/`)
- **`evals/`** = skill-behavior tests using the **"drill" eval harness** — runs REAL Claude Code/Codex/Gemini sessions, judges with an LLM, scenarios in `evals/scenarios/*.yaml` (e.g., `code-review-catches-planted-bugs.yaml`), per-file 900s ceilings
- **Micro-testing methodology:** skill edits are pressure-tested by sampling phrasing against a no-guidance control (e.g., control 8/10 vs treatment 5/10 TDD-first behavior), including "ship-pressure"/"lukewarm-human" adversarial probes
- **Anti-pattern:** never text-assert skills (the "string-presence trap") — behavior is the observable

### 2.5 Versioning Infrastructure

- `.version-bump.json` — declares EVERY file carrying the version (8+ plugin manifests + marketplace.json)
- `scripts/bump-version.sh <X.Y.Z>` — single entry point; `--check` (drift detection), `--audit` (finds undeclared version strings)
- `RELEASE-NOTES.md` — Keep-a-Changelog style, the **single release source** (CHANGELOG.md removed in v5.1.0); `main` for releases, `dev` for PRs

### 2.6 Pre-commit & Quality Gates

- `.pre-commit-config.yaml`: ruff check + ruff format + `ty` type-check on `evals/` Python
- `scripts/lint-shell.sh` + `tests/shell-lint/` — guards all bash scripts (portable shebangs, no bare except)

### 2.7 The 14-Platform Plugin Matrix

| Platform | Manifest | Special notes |
|---|---|---|
| Claude Code | `.claude-plugin/plugin.json` + `marketplace.json` | published to Anthropic's official marketplace |
| Codex | `.codex-plugin/plugin.json` | `hooks: {}` anti-discovery; full `interface` block (brandColor, icons, screenshots); deterministic packaging script |
| Cursor | `.cursor-plugin/plugin.json` | `hooks: "./hooks/hooks-cursor.json"` |
| Devin / Kimi | `.devin-plugin/`, `.kimi-plugin/` | minimal manifests |
| Hermes | `.hermes-plugin/plugin.yaml` | YAML; no post-compaction hook → skills can stop triggering |
| OpenCode | `.opencode/` (npm package) | bootstrap injected as **prepended user message** via `experimental.chat.messages.transform`, cached at module level |
| Gemini CLI | `gemini-extension.json` | `contextFileName: "GEMINI.md"` with `@import` |

### 2.8 Governance & Culture

- **Contributor rules:** ~94% of AI PRs rejected historically; PR templates **disclose how they were made** (model, harness, version, plugins); new-harness PRs require a session transcript + acceptance test; PRs target `dev` not `main`
- **Token-cost culture:** "every session pays for the bootstrap" → constant compression passes; subagent waits are event-driven not poll-heavy; reviewer diffs move as **files** not pasted text
- **SDD workspace discipline:** per-plan scratch in `.superpowers/sdd/<plan>/` (git-ignored); five-round review circuit breaker; reviewers are read-only; controllers can't suppress findings
- **Security:** visual companion uses per-session one-time keys, tab-scoped cookies, sandboxed file server (no symlinks/dotfiles/`..` escapes)

---

## 3. mem0 — The Memory-Layer Standard

### 3.1 The New Memory Algorithm (April 2026 — v3)

- **Single-pass ADD-only extraction** — one LLM call (~7K tokens, ~0.9–1.1s p50); memories accumulate, nothing overwritten (no UPDATE/DELETE)
- **Agent-generated facts are first-class** — confirmed agent actions stored with equal weight
- **Entity linking** — entities extracted, embedded, linked across memories to boost retrieval
- **Multi-signal retrieval** — semantic + BM25 keyword + entity matching scored in parallel and **fused**
- **Temporal reasoning** — time-aware ranking: current-state vs past-event vs upcoming-plan queries get the right dated instance
- **Three memory scopes:** User, Session, Agent

### 3.2 The Chat Loop Pattern (retrieve → generate → persist)

```python
memories = memory.search(query, filters={"user_id": alice}, top_k=3)  # retrieve
response = generate(system_prompt + memories, user_msg)               # inject + generate
memory.add(messages, user_id=alice)                                   # persist full conversation
```

### 3.3 The Agent Signup Flow (self-provisioning)

`mem0 init --agent --agent-caller claude-code` — an agent mints its own API key in <5s (no email/dashboard/OTP); a human can claim it later with `mem0 init --email <their-email>` — same key, memories preserved.

### 3.4 Benchmarks (measurable memory quality)

| Benchmark | Score |
|---|---|
| LoCoMo | **92.5** (was 71.4) |
| LongMemEval | **94.4** (was 67.8; 98.2 on assistant memory recall) |
| BEAM 1M | 64.1 |
| BEAM 10M | 48.6 |

Open-sourced in `mem0ai/memory-benchmarks` so anyone can reproduce.

### 3.5 Plugin Ecosystem

`.claude-plugin`, `.codex-plugin`, `.cursor-plugin`, `.kimi-plugin` (MCP + skills + **auto-capture**), `.agents/plugins`, `skills/` catalog, root `marketplace.json`. Best-practice signal from a commit: *"use existing mem0 SDK instead of delegating to MCP, load skills properly instead of dumping them in .opencode"* — prefer SDK over MCP delegation.

---

## 4. strands-agents/agent-sop — The SOP Standard

### 4.1 The Standardized SOP Format

```
# Code Assist
## Overview          ← clear objective
## Parameters        ← parameterized inputs (required/optional + defaults)
## Steps             ← numbered, each with RFC 2119 constraints
   ### 1. Setup
   **Constraints:**
   - You MUST validate and create the documentation directory structure
   - You MUST NOT proceed if directory creation fails
## Examples / Troubleshooting
```

### 4.2 The PDD Family (5 SOPs covering the whole dev lifecycle)

`codebase-summary` → `pdd` (prompt-driven development) → `code-task-generator` → `code-assist` (TDD implementation) → `eval` (automated evaluation with Evals SDK)

### 4.3 The `.agents/` Artifact Hierarchy (what to commit)

```
.agents/
├── summary/     # always commit (docs)
├── planning/    # often commit (design decisions, rationale)
├── tasks/       # optional (or issue tracker)
└── scratchpad/  # .gitignore (transient working files)
```
Project names auto-prefixed with date: `2026-01-30-auth-system`.

### 4.4 Multi-Modal Distribution (one source, many targets)

- **MCP server:** `strands-agents-sops mcp --sop-paths ~/my-sops` — SOPs exposed as discoverable prompts; external SOPs override built-ins (first-wins)
- **Cursor commands:** `strands-agents-sops commands --type cursor` → `.cursor/commands/*.sop.md` (parameterized via prompting)
- **Agent Skills:** `strands-agents-sops skills` → `skills/<name>/SKILL.md` with frontmatter — **progressive disclosure of context** (agent loads only the relevant workflow on demand)
- **Python SDK:** `from strands_agents_sops import code_assist` — programmatic use
- **Marketplace:** auto-published to `skills-dist` branch on every GitHub Release; `claude plugin marketplace add strands-agents/agent-sop`

### 4.5 Validation & Authoring Tooling

- `skills/agent-sop-author/SKILL.md` — teaches agents to author SOPs
- `validate-sop.sh` — **SOP structure validator** (checks RFC 2119 constraint usage)
- CI: PyPI publish workflow, MCP 1.x/2.x compatibility matrix testing

---

## 5. LangGraph — Durable Execution (checkpointer vs. store)

| | Checkpointer | Store |
|---|---|---|
| Persists | Graph state snapshots | Application-defined key-value data |
| Scope | A single thread | Across threads |
| Memory type | Short-term, thread-scoped | Long-term, cross-thread |
| Use for | Conversation continuity, human-in-the-loop, time travel, fault tolerance | User preferences, facts, shared knowledge |
| Access | Pass `thread_id` in graph config | Read/write from nodes or application code |

**Troubleshooting lessons:**
- `thread_id` must stay under 255 chars (Postgres column limit) — use UUID/hash
- `MemorySaver`/`InMemorySaver` lose checkpoints on restart — use PostgresSaver/SqliteSaver for production
- Checkpoints grow unboundedly — prune with retention policy (cron deleting checkpoints older than N days)
- Subgraph state updates aren't visible to parent graph — use shared state via Store for cross-boundary data

---

## 6. agentskills.io — The Agent Skills Standard (open spec)

```
my-skill/
├── SKILL.md          # Required: metadata (name, description) + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
├── assets/           # Optional: templates, resources
└── ...               # Any additional files or directories
```

**Progressive disclosure in three stages:**
1. **Discovery** — at startup, agents load only name + description of each skill
2. **Activation** — when a task matches, the agent reads the full SKILL.md into context
3. **Execution** — the agent follows instructions, optionally executing bundled code

**Key insight:** full instructions load only when a task calls for them, so agents can keep many skills with a small context footprint. Originally developed by Anthropic, released as an open standard, adopted by a growing number of agent products (agentskills.io/clients).

---

## 7. Cross-Cutting Observations

1. **The ecosystem is converging on three standards:** Agent Skills (SKILL.md), MCP (tools/context), and AGENTS.md (rules). HQ already uses all three — the gap is in *tooling* around them (validation, distribution, evaluation).
2. **Every top project ships per-platform plugin manifests** — single source, many targets. HQ's skills are already platform-agnostic markdown; manifests are a packaging problem, not a rewrite.
3. **Evals are the 2026 bottleneck** — Anthropic, strands, and superpowers all built eval infrastructure independently. HQ's manual QA loop is the single biggest competitive gap.
4. **Memory is moving from storage to intelligence** — mem0's v3 does extraction, entity linking, and temporal reasoning in one pass. Flat markdown keyword search is a v1 pattern.
5. **Token-cost culture is a differentiator** — superpowers treats every session as paying for the bootstrap; compression passes, event-driven waits, file-based handoffs. HQ's XML task-block protocol is already token-efficient by design.