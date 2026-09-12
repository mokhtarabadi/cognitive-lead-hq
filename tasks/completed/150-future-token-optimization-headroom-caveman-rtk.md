# Task 150: Future R&D — Token Optimization, Context Compression & Output Trimming Layer (Headroom, Caveman, RTK)

**File:** `tasks/completed/150-future-token-optimization-headroom-caveman-rtk.md`
**Source:** manager
**Type:** research
**Status:** closed
**Target Milestone:** Future R&D / Token Efficiency

---

## Goal

Design and evaluate a comprehensive **Token Optimization & Context Compression Layer** for the Cognitive Lead AI system (Orchestrator, OpenCode Hands, and Loop Engine). This task synthesizes the architecture, algorithms, and integration patterns from three leading token-reduction engines discovered in 2026:

1. **Headroom (`headroom-ai`):** Context compression proxy & library (JSON SmartCrusher, AST CodeCompressor, Reversible CCR, Output Token Shaper).
2. **Caveman (`@caveman-ai/cli`):** Dual-layer compression (Caveman Proxy for input shrink + Caveman Skill for terse high-density agent replies + Pixel Mode for skills-as-images).
3. **RTK - Rust Token Killer (`rtk-ai/rtk`):** High-performance (<10ms) Rust CLI proxy cutting up to 90% of bash/command output (git, pytest, linters, docker, grep) via OpenCode `tool.execute.before` hooks.

---

## Local TODOs

- [x] Evaluate RTK locally and measure raw-vs-RTK output on representative commands
- [x] Registry-verify Headroom and Caveman availability (version + description)
- [x] Write trimming practices to `docs/opencode-shell-strategy.md`
- [x] Write evidence table to `docs/loop-engine/configuration.md`
- [ ] Headroom proxy integration (follow-up, needs manager approval)
- [ ] 10-task sprint measurement (follow-up)

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

- [x] Evaluate RTK installation in local OpenCode environment and measure command output token reduction.
- [ ] Test Headroom / Caveman proxy integration with OpenRouter endpoints.
- [ ] Measure baseline vs optimized token consumption across a 10-task development sprint.
- [x] Update `docs/opencode-shell-strategy.md` with recommended token-trimming practices.
- [x] Document verified savings in `docs/loop-engine/configuration.md`.

> Spike notes 2026-09-12 (Hands): RTK 0.49.0 evaluated via local musl binary
> (`/tmp/rtk`, no `rtk init -g`). Headroom/Caveman verified present on
> registries (`headroom-ai` 0.37.0, `@caveman-ai/cli` 1.3.3) but proxy/pixel
> integration NOT executed — needs localhost proxy + provider rewiring and
> manager approval; left unchecked as follow-up. Sprint-long measurement also
> deferred; representative-command measurements stand in (see Evidence below).

---

## References & Documentation Links

- **Headroom AI:** [https://github.com/chopratejas/headroom](https://github.com/chopratejas/headroom) · [Documentation](https://headroom-docs.vercel.app/docs)
- **Caveman AI:** [https://github.com/JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) · [Product Hunt](https://caveman.so)
- **RTK (Rust Token Killer):** [https://github.com/rtk-ai/rtk](https://github.com/rtk-ai/rtk) · [User Guide](https://www.rtk-ai.app/guide)

---

## Verification Evidence

- Full decision-server suite: **232 passed**, exit 0 — verified twice (raw clean run 1801B/21 lines; `rtk test` run 44B/3 lines, same verdict).
- `lint_task_file` + `lint_markdown` (both docs) clean.
- `rtk gain` session report: 11 commands, 1.9K tokens saved, 41.0% blended.

## Risk & Rollback

- Risk: NONE to production code — spike changed zero repo code paths; only docs + task file edited. RTK binary lives in `/tmp` (eval only); no global OpenCode config touched.
- Rollback: revert docs edits (`docs/opencode-shell-strategy.md` §8, `docs/loop-engine/configuration.md`) via `git checkout -- <path>`; no data migrations involved.

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

### Spike 2026-09-12 (Hands, autopilot)

- Moved backlog→in-progress via `git mv` (file is tracked; plain `mv` first used by habit, then corrected to staged rename `R`).
- RTK 0.49.0 (x86_64 musl) downloaded from GitHub releases to `/tmp/rtk`; deliberately did NOT run `rtk init -g` (rewrites global OpenCode config — manager approval required).
- Evidence (bytes/lines measured, exit codes observed):
  - `pytest tests/ -q`, 232 passed: raw 1801B/21 lines → `rtk test` 44B/3 lines = 97.6% fewer bytes, exit 0 preserved.
  - `git status`/`git log -15`/`git diff --stat` on small outputs: RTK adds ~0–2% overhead — skip the wrapper there.
  - `rtk git diff`: condensed reformat (~2% smaller on small diffs; value grows with diff size).
  - `rtk gain`: 11 commands, 1.9K tokens saved, 41.0% blended.
- Caveats: `rtk diff` ≠ git diff (wraps `/usr/bin/diff`); `rtk test` joins args unquoted so `<` in specs (e.g. `--with "mcp<2"`) misparses as redirection → exact-pin (`mcp==1.30.0`). Env note: suite needs `pathspec` + `pyyaml` + `mcp==1.30.0` via `--with` (mcp 1.9.4 breaks brain-bridge FastMCP at collection — pre-existing, unrelated).
- Docs: `docs/opencode-shell-strategy.md` §8 (practices) + new `docs/loop-engine/configuration.md` (evidence table, recommendation, caveats).
- Deferred (AC left unchecked): Headroom/Caveman proxy integration, 10-task sprint measurement.
- Verification: full suite 232 passed exit 0 (raw clean run + rtk run both green); `lint_task_file` + `lint_markdown` clean (see QA cycle below).

### State-machine review round (this session)

- **Brain QA: QA_PASSED (spike scope).** First attempt BLOCKED on missing context (auto-attach did not resolve); retry with full file pasted succeeded. Findings: numbers internally consistent (97.6% arithmetic holds, overhead rows honest), deferrals match unchecked AC, no task-number violation in pasted view. Vulnerabilities V1–V3 + missing evidence M1–M4 passed to reviewer as follow-ups (vendor-row provenance, failure-path measurement, cross-task diff contamination — the 192/195 hunks in the diff block are shared-HEAD staging contamination, not this spike's edits).
- **Brain reviewer: CHANGES_REQUIRED (low severity, docs wording only).** Math confirmed (1757/1801 = 97.56% → 97.6%). Required before acceptance: (A1) Source column in evidence table — RTK row labeled locally-measured/passing-suites, Headroom/Caveman rows labeled vendor-claimed/registry-only; (A2) recommendation scoped to passing suites with explicit failing-suite-unmeasured warning; (A3) numeric task identifiers out of docs prose; (A4) CHANGELOG entry discipline. Hotfix XML received, scoped to the two docs files in place.
- **Per state-machine rule: not APPROVED → NO autoclosure.** Verdict recorded here, task stays in QA. Hotfix application awaits Manager authorization (rejection/change count: 1, no 3rd-round escalation).

### Autopilot hotfix applied (this session, reviewer A1–A4)

- (A1) `docs/loop-engine/configuration.md` evidence table gained a `Source` column — every row labeled `local measurement` (passing suite noted); `rtk gain` line marked tool self-report, not independently verified.
- (A2) Recommendation + `docs/opencode-shell-strategy.md` §8 test-runner bullet scoped to passing suites with explicit failing-suite-UNMEASURED warning (keep full output on failure).
- (A3) Numeric task identifier removed from docs prose (`Task 150` → neutral spike wording); residual grep `ZERO_RESIDUAL` on both docs.
- (A4) CHANGELOG entry discipline: 150 entry now states the passing-suite scope; 195 entry counts corrected (20 mocked tests, 239 passed).
- Both docs `lint_markdown` clean. Pending: fresh QA + reviewer via `brain_turn`.

### Reviewer re-run (this session, post A1–A4 hotfix)

- **Brain reviewer: PO_REVIEW_PENDING — technically APPROVED, NOT autoclosed.** Reviewer confirms A1–A4 pass on quoted disk evidence (Source column + self-report label; passing-suite scope + failing-suite warnings in both docs; docs grep ZERO task numbers; CHANGELOG scope note), no blocking issue, severity low. But status is explicitly PO_REVIEW_PENDING — "Brain has no disk access", approval is conditional on quoted proof, and it asks the Manager to reply "Approved for closure". Per goal rule (close ONLY on explicit APPROVED) this is a deferral, not an approval — task STAYS in QA awaiting Manager's approval word.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `7c51b9c284cfaf35ae40bd1d88dfc61e650ec5ba`
<!-- END_GIT_DIFF -->
