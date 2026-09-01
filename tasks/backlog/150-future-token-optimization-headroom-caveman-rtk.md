# Task 150: Future R&D — Token Optimization, Context Compression & Output Trimming Layer (Headroom, Caveman, RTK)

**File:** `tasks/backlog/150-future-token-optimization-headroom-caveman-rtk.md`
**Source:** manager
**Type:** r&d / optimization
**Status:** open
**Target Milestone:** Future R&D / Token Efficiency

---

## Goal

Design and evaluate a comprehensive **Token Optimization & Context Compression Layer** for the Cognitive Lead AI system (Orchestrator, OpenCode Hands, and Loop Engine). This task synthesizes the architecture, algorithms, and integration patterns from three leading token-reduction engines discovered in 2026:

1. **Headroom (`headroom-ai`):** Context compression proxy & library (JSON SmartCrusher, AST CodeCompressor, Reversible CCR, Output Token Shaper).
2. **Caveman (`@caveman-ai/cli`):** Dual-layer compression (Caveman Proxy for input shrink + Caveman Skill for terse high-density agent replies + Pixel Mode for skills-as-images).
3. **RTK - Rust Token Killer (`rtk-ai/rtk`):** High-performance (<10ms) Rust CLI proxy cutting up to 90% of bash/command output (git, pytest, linters, docker, grep) via OpenCode `tool.execute.before` hooks.

---

## Technical Synthesis & Core Architecture (The 4 Pillars)

┌───────────────────────────────────────────────────────────────────────────────────────┐
│ Cognitive Lead AI Token Optimization Stack │
├───────────────────────────────────────────────────────────────────────────────────────┤
│ 1. CLI Output Interception (RTK) → Cuts 80–90% of Bash/Test/Git output before LLM │
│ 2. Reversible Compression (CCR) → Compresses AST/JSON; retrieves raw bytes via MCP │
│ 3. Output Token Shaper (Headroom) → Strips preambles & dials down reasoning on routine│
│ 4. Terse Response Mode (Caveman) → High-density, zero-filler communication │
│ 5. Pixel Mode (Caveman Pixel) → Converts large SKILL.md prompt bodies to images │
└───────────────────────────────────────────────────────────────────────────────────────┘

### Pillar 1: Bash & Command Output Trimming (RTK Strategy)

- **Problem:** Raw outputs of `git diff`, `git log`, `pytest`, `cargo test`, `ls`, `grep`, `docker ps` consume thousands of unnecessary input tokens.
- **Mechanism:** Intercept shell commands via OpenCode PreToolUse hooks (`tool.execute.before`) or CLI aliases:
  - `ls` / `tree` → Compact directory tree with file counts instead of verbose listings.
  - `cat` / `read` → Structural signature extraction over full file bodies.
  - `git status` / `git diff` → Stripped headers, condensed hunks, single-line confirmations.
  - `pytest` / test runners → Failures only (traceback trimmed), passing tests collapsed to a single count.
  - `tee` fallback: If a command fails, raw full output is saved locally to a log file so the agent can inspect it without re-executing.
- **Expected Reduction:** 70–90% reduction in bash output tokens with <10ms overhead.

### Pillar 2: Reversible Context Compression (CCR - Headroom & Caveman)

- **Problem:** Large JSON payloads, AST file dumps, and RAG chunks flood the context window.
- **Mechanism:**
  - **ContentRouter:** Automatically detects content type (`json`, `code`, `diff`, `log`, `text`).
  - **SmartCrusher (JSON):** Preserves keys, schema structure, error nodes, and collapses repetitive object arrays (70–90% reduction).
  - **CodeCompressor (AST):** Keeps type signatures, exports, and interfaces while eliding internal function bodies (40–70% reduction).
  - **Cache-Conscious Reversibility (CCR):** Stores the raw uncompressed bytes in local SQLite/disk cache and passes a compact handle (e.g. `handle_01`) to the LLM. If the LLM needs full details, it calls an MCP tool (`headroom_retrieve` or `caveman_retrieve`).

### Pillar 3: Output Token Reduction & Effort Routing (Headroom Strategy)

- **Problem:** Output tokens cost 3× to 5× more than input tokens. Models waste tokens on polite conversational filler ("Great, let me help you with..."), restating code, and deep thinking on trivial file reads.
- **Mechanism:**
  - **Verbosity Steering:** Appends a concise directive at the end of the system prompt to prevent context restatement without busting KV cache.
  - **Effort Routing:** When a turn is simply a routine tool result (file read, passing test), automatically clamps `reasoning_effort` to `low`/`none`. Only escalates reasoning on architectural planning or errors.
- **Expected Reduction:** 25–35% reduction in output tokens.

### Pillar 4: Terse Mode & Pixel Mode (Caveman Strategy)

- **Terse Response Skill:** Strips conversational fluff while keeping code, commands, and diffs exact ("New object ref each render. Wrap in useMemo" vs 4-line paragraph).
- **Pixel Mode (Skills as Images):** Converts large, static `SKILL.md` bodies (which load thousands of prompt tokens every turn) into PNG images. Multimodal models read the body as an image for a 60% token reduction.

---

## Benchmark Evidence from Source Repositories

| Workload / Operation                  | Baseline (Tokens) | Optimized (Tokens) | Reduction  | Tool Source        |
| ------------------------------------- | ----------------- | ------------------ | ---------- | ------------------ |
| **Code search (100 results)**         | 17,765            | 1,408              | **92%**    | Headroom           |
| **SRE / Log incident debugging**      | 65,694            | 5,118              | **92%**    | Headroom           |
| **GitHub issue triage**               | 54,174            | 14,761             | **73%**    | Headroom           |
| **Test runner output (pytest/cargo)** | 2,000+ lines      | ~20 lines          | **90%**    | RTK                |
| **Git operations (push/status/add)**  | 15–45 lines       | 1 line             | **85–95%** | RTK                |
| **JSON payload compression**          | Standard JSON     | SmartCrusher       | **70–90%** | Caveman / Headroom |
| **Codebase exploration**              | 78,502            | 41,254             | **47%**    | Headroom           |
| **Skill prompt loading (Pixel Mode)** | 1,069 (text)      | 415 (image)        | **61%**    | Caveman            |

---

## Integration Options for Cognitive Lead AI & OpenCode

When implementing this task in the future, the team can choose from three integration levels:

### Option A: OpenCode CLI Hook Integration (Fastest & Lightest — RTK)

1. Install RTK via Homebrew or Cargo (`brew install rtk` or curl binary).
2. Enable OpenCode integration via `rtk init -g --opencode`.
3. OpenCode automatically rewrites bash commands before execution (e.g. `git status` → `rtk git status`, `pytest` → `rtk pytest`), immediately reducing token spend across all tasks with zero code changes in our repo.

### Option B: Local Headroom Compression Proxy

1. Install Headroom CLI (`uv tool install "headroom-ai[all]"`).
2. Start Headroom proxy: `headroom proxy --port 8787`.
3. Point `loop-engine/loop-engine.jsonc` or OpenCode provider base URL to `http://localhost:8787/v1`.
4. Headroom compresses all inbound prompts and shapes outbound tokens automatically.

### Option C: MCP Server Integration (Native Tooling)

1. Add `headroom` or `caveman` as an MCP server in `opencode.json`.
2. Expose `headroom_compress`, `headroom_retrieve`, and `rtk` MCP tools to the agent.
3. Incorporate output trimming rules into `prompts/fragments/13-constraints.md`.

---

## Acceptance Criteria (For Future Execution)

- [ ] Evaluate RTK installation in local OpenCode environment and measure command output token reduction.
- [ ] Test Headroom / Caveman proxy integration with OpenRouter endpoints.
- [ ] Measure baseline vs optimized token consumption across a 10-task development sprint.
- [ ] Update `docs/opencode-shell-strategy.md` with recommended token-trimming practices.
- [ ] Document verified savings in `docs/loop-engine/configuration.md`.

---

## References & Documentation Links

- **Headroom AI:** [https://github.com/chopratejas/headroom](https://github.com/chopratejas/headroom) · [Documentation](https://headroom-docs.vercel.app/docs)
- **Caveman AI:** [https://github.com/JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) · [Product Hunt](https://caveman.so)
- **RTK (Rust Token Killer):** [https://github.com/rtk-ai/rtk](https://github.com/rtk-ai/rtk) · [User Guide](https://www.rtk-ai.app/guide)

---

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
