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
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index bf30e4b..1851269 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,8 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
-- **Token-optimization verified spike (Task 150):** Evaluated RTK 0.49.0 locally (musl binary, no global install): passing pytest suite collapses 1801 bytes / 21 lines → 44 bytes / 3 lines (**97.6% fewer bytes**, exit code preserved, 232 passed); small git outputs (±2%) not worth wrapping; `rtk diff` is a `/usr/bin/diff` wrapper (use `rtk git diff`); `rtk test` needs exact dep pins (`mcp==1.30.0` — `<` specs break as shell redirection). `headroom-ai` 0.37.0 (PyPI) and `@caveman-ai/cli` 1.3.3 (npm) registry-verified; proxy/pixel eval deferred (needs provider rewiring + manager approval). New `docs/loop-engine/configuration.md` holds the evidence table; `docs/opencode-shell-strategy.md` §8 holds the practices. Headroom/Caveman proxy integration and 10-task sprint measurement remain open follow-ups.
-- **Machine-readable QA verdicts + rules-first gate (Task 195):** QA persona (fragment 06) now ends every report with a machine verdict block (`VERDICT: QA_PASSED` / `QA_REJECTED` + `CITE: file:line` lines, single-regex parseable) with a documented escape hatch (unparseable → QA_REJECTED with reason, prose fallback, manager override). New `scripts/qa-rules-gate/rules_gate.py` runs verdict-parse, schema, budget, and allowlist checks before any LLM judge call — rule failures return QA_REJECTED without invoking the judge (Mock-asserted). 13 new mocked tests. System version 9.27.0 → 9.28.0, `system-prompt.md` rebuilt (sync-check byte-identical). Full suite: **232 passed**.
+- **Token-optimization verified spike (Task 150):** Evaluated RTK 0.49.0 locally (musl binary, no global install): passing pytest suite collapses 1801 bytes / 21 lines → 44 bytes / 3 lines (**97.6% fewer bytes**, exit code preserved, 232 passed); small git outputs (±2%) not worth wrapping; `rtk diff` is a `/usr/bin/diff` wrapper (use `rtk git diff`); `rtk test` needs exact dep pins (`mcp==1.30.0` — `<` specs break as shell redirection). `headroom-ai` 0.37.0 (PyPI) and `@caveman-ai/cli` 1.3.3 (npm) registry-verified; proxy/pixel eval deferred (needs provider rewiring + manager approval). Claim scoped to passing suites — failing-suite trimming unmeasured. New `docs/loop-engine/configuration.md` holds the evidence table (with source column: local measurement vs tool self-report); `docs/opencode-shell-strategy.md` §8 holds the practices. Headroom/Caveman proxy integration and 10-task sprint measurement remain open follow-ups.
+- **Machine-readable QA verdicts + rules-first gate (Task 195):** QA persona (fragment 06) now ends every report with a machine verdict block (`VERDICT: QA_PASSED` / `QA_REJECTED` + `CITE: file:line` lines, single-regex parseable) with a documented escape hatch (unparseable → QA_REJECTED with reason, prose fallback, manager override). New `scripts/qa-rules-gate/rules_gate.py` runs verdict-parse, schema, budget, and allowlist checks before any LLM judge call — rule failures return QA_REJECTED without invoking the judge (Mock-asserted). 20 mocked tests (relative-path allowlist, exactly-one-verdict, whitespace tolerance, judge validation, nested schema, cite punctuation). System version 9.27.0 → 9.28.0, `system-prompt.md` rebuilt (sync-check byte-identical). Full suite: **239 passed**.
 
 ### Fixed
 
diff --git a/docs/loop-engine/configuration.md b/docs/loop-engine/configuration.md
index 26b5fb7..bbde3d7 100644
--- a/docs/loop-engine/configuration.md
+++ b/docs/loop-engine/configuration.md
@@ -1,27 +1,30 @@
 # Loop Engine Configuration — Token Optimization Evidence
 
-> Verified spike measurements for Task 150 (Future R&D — Token Optimization).
+> Verified spike measurements (token-optimization R&D spike).
 > Date: 2026-09-12. Tool: RTK 0.49.0 (x86_64-unknown-linux-musl, local eval
 > binary in `/tmp`; no global install, no `rtk init -g`).
 > Byte/line counts are the hard evidence; token equivalents assume ~4 chars/token.
 
-## Verified savings (this repo, decision-server suite, 232 tests)
+## Verified savings (this repo, decision-server suite, 232 tests at measure time)
 
-| Command | Raw | Via RTK | Reduction | Exit code |
-| ------- | --- | ------- | --------- | --------- |
-| `pytest tests/ -q` (232 passed) | 1801 bytes / 21 lines | 44 bytes / 3 lines | **97.6% bytes** | preserved (0) |
-| `git status --short` (32 lines) | 1589 bytes | 1621 bytes | −2% (overhead) | n/a |
-| `git log --oneline -15` | 1218 bytes | 1696 bytes | −39% (overhead) | n/a |
-| `git diff --stat HEAD` | 1952 bytes | 1951 bytes | ~0% | n/a |
-| `rtk git diff` (2-file sample) | 5297 bytes / 48 lines | 5204 bytes / 51 lines | ~2% (reformat) | n/a |
+| Command | Raw | Via RTK | Reduction | Exit code | Source |
+| ------- | --- | ------- | --------- | --------- | ------ |
+| `pytest tests/ -q` (232 passed) | 1801 bytes / 21 lines | 44 bytes / 3 lines | **97.6% bytes** | preserved (0) | local measurement, passing suite |
+| `git status --short` (32 lines) | 1589 bytes | 1621 bytes | −2% (overhead) | n/a | local measurement |
+| `git log --oneline -15` | 1218 bytes | 1696 bytes | −39% (overhead) | n/a | local measurement |
+| `git diff --stat HEAD` | 1952 bytes | 1951 bytes | ~0% | n/a | local measurement |
+| `rtk git diff` (2-file sample) | 5297 bytes / 48 lines | 5204 bytes / 51 lines | ~2% (reformat) | n/a | local measurement |
 
 `rtk gain` self-report for the eval session: 11 commands, 1.9K tokens saved
-(41.0% blended — dominated by the test-runner wins).
+(41.0% blended — dominated by the test-runner wins; tool self-report, not
+independently verified).
 
 ## Recommendation
 
-- **Adopt Option A (RTK wrapper) for test/bash output** in agent guidance
-  (see `docs/opencode-shell-strategy.md` §8). Zero repo code changes.
+- **Adopt Option A (RTK wrapper) for passing-suite/test output** in agent
+  guidance (see `docs/opencode-shell-strategy.md` §8). Zero repo code changes.
+  Scope warning: failing-suite output is UNMEASURED — collapsing failures
+  could hide tracebacks, so keep full output on any failure.
 - **Defer Option B (Headroom proxy):** `headroom-ai` 0.37.0 verified present
   on PyPI, but proxy eval requires localhost proxy + provider URL rewiring
   in `loop-engine/loop-engine.jsonc` — follow-up task, needs manager approval.
diff --git a/docs/opencode-shell-strategy.md b/docs/opencode-shell-strategy.md
index 95adc72..9285505 100644
--- a/docs/opencode-shell-strategy.md
+++ b/docs/opencode-shell-strategy.md
@@ -152,7 +152,8 @@ manager approval). Full evidence in `docs/loop-engine/configuration.md`.
   3 lines, 97.6% fewer bytes). Exit code is preserved, so gates still
   fail the build. Prefer `rtk test <cmd>` over raw `pytest`/`cargo test`
   when only the verdict matters; use `rtk recall <id>` to pull the full
-  output on failure.
+  output on failure. Scope warning: failing-suite output is UNMEASURED —
+  keep full output on any failure, never collapse it.
 - **Small git outputs: skip the wrapper.** `git status`, short `git log`,
   and `git diff --stat` are already compact — RTK adds ~1–2% header
   overhead there. Reserve `rtk git ...` for large diffs and long logs.
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 34fc957..475f079 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -145,6 +145,12 @@ _SKIP_DIRS = frozenset(
     {".git", "__pycache__", ".venv", "node_modules", ".pytest_cache"}
 )
 
+# Guardrails for the file-pull tools (state-machine hotfix round).
+_READ_MAX_LINES = 2000        # read_file limit clamp — pulls stay pull-sized
+_READ_MAX_BYTES = 2_000_000   # read_file refuses bigger files outright
+_GREP_PATTERN_MAX = 500       # Brain-supplied regex length cap (ReDoS bound)
+_GREP_MAX_LINE_CHARS = 4000   # overlong lines are skipped, never searched
+
 
 def _workspace_root() -> Path:
     """Repo root for context reads; override via ``BRAIN_WORKSPACE_ROOT``."""
@@ -266,7 +272,11 @@ def _build_task_attach(task_id: str) -> str:
         if path is None:
             return ""
         text = path.read_text(encoding="utf-8", errors="replace")
-        rel = path.name
+        try:
+            rel = path.resolve().relative_to(
+                _workspace_root().resolve()).as_posix()
+        except (OSError, ValueError):
+            rel = path.name
         cleaned, _omitted, _truncated = _strip_task_diff(text, rel)
         if len(cleaned) > _TASK_ATTACH_CAP:
             cleaned = (
@@ -311,16 +321,29 @@ def _build_context_bundle() -> str:
 
 
 def _read_file_impl(path: str, offset: int = 1, limit: int = 200) -> dict[str, Any]:
-    """Numbered-line slice of a workspace text file (1-indexed offset)."""
+    """Numbered-line slice of a workspace text file (1-indexed offset).
+
+    The ``limit`` clamps to ``_READ_MAX_LINES`` and files over
+    ``_READ_MAX_BYTES`` are refused — pulls stay pull-sized and can
+    never drag a giant file into context.
+    """
     if not isinstance(path, str) or not path.strip():
         raise ValueError(f"bad path: {path!r}")
     if offset < 1:
         raise ValueError(f"bad offset (1-indexed): {offset!r}")
     if limit < 1:
         raise ValueError(f"bad limit: {limit!r}")
+    limit = min(limit, _READ_MAX_LINES)
     resolved = _resolve_under_root(path)
     if resolved.suffix.lower() not in _ALLOWED_READ_SUFFIXES:
         raise ValueError(f"unsupported extension: {path!r}")
+    try:
+        if resolved.stat().st_size > _READ_MAX_BYTES:
+            raise ValueError(
+                f"file too large for read_file: {path!r} "
+                f"(>{_READ_MAX_BYTES} bytes)")
+    except OSError:
+        pass  # stat failed — the read below raises the real error
     text = resolved.read_text(encoding="utf-8", errors="replace")
     lines = text.splitlines()
     total = len(lines)
@@ -336,7 +359,20 @@ def _read_file_impl(path: str, offset: int = 1, limit: int = 200) -> dict[str, A
 
 
 def _grep_files_impl(pattern: str, subdir: str = ".") -> list[str]:
-    """Python-regex search over workspace text files (max 30 hits)."""
+    """Python-regex search over workspace text files (max 30 hits).
+
+    Hardening: the Brain-supplied pattern caps at ``_GREP_PATTERN_MAX``
+    chars (``re`` has no timeout, so length is the ReDoS bound), each hit
+    line truncates at 200 chars, lines over ``_GREP_MAX_LINE_CHARS`` are
+    skipped unsearched, and every candidate resolves against the root
+    BEFORE it is read — a symlink escaping the workspace is skipped,
+    never opened.
+    """
+    if not isinstance(pattern, str) or not pattern:
+        raise ValueError(f"bad regex: {pattern!r}")
+    if len(pattern) > _GREP_PATTERN_MAX:
+        raise ValueError(
+            f"regex too long ({len(pattern)} > {_GREP_PATTERN_MAX})")
     try:
         rx = re.compile(pattern)
     except re.error as exc:
@@ -353,11 +389,18 @@ def _grep_files_impl(pattern: str, subdir: str = ".") -> list[str]:
                 continue
             fpath = Path(dirpath) / name
             try:
-                text = fpath.read_text(encoding="utf-8", errors="replace")
+                resolved = fpath.resolve()
+                resolved.relative_to(root)
+            except (OSError, ValueError):
+                continue  # symlink escape — skip before any read
+            try:
+                text = resolved.read_text(encoding="utf-8", errors="replace")
             except OSError:
                 continue
-            rel = fpath.resolve().relative_to(root).as_posix()
+            rel = resolved.relative_to(root).as_posix()
             for lineno, line in enumerate(text.splitlines(), 1):
+                if len(line) > _GREP_MAX_LINE_CHARS:
+                    continue
                 if rx.search(line):
                     hits.append(f"{rel}:{lineno}: {line.strip()[:200]}")
                     if len(hits) >= 30:
diff --git a/scripts/qa-rules-gate/rules_gate.py b/scripts/qa-rules-gate/rules_gate.py
index 7e773fc..17b63df 100644
--- a/scripts/qa-rules-gate/rules_gate.py
+++ b/scripts/qa-rules-gate/rules_gate.py
@@ -16,13 +16,17 @@ UnparseableVerdict — the autopilot treats that as QA_REJECTED with reason
 
 from __future__ import annotations
 
+import os
 import re
 from dataclasses import dataclass, field
-from pathlib import Path
 from typing import Callable
 
-_VERDICT_RE = re.compile(r"^VERDICT:\s*(QA_PASSED|QA_REJECTED)\s*$", re.MULTILINE)
-_CITE_RE = re.compile(r"^CITE:\s*(\S+):(\d+)\s*$", re.MULTILINE)
+_VERDICT_RE = re.compile(
+    r"^[ \t]*VERDICT:[ \t]*(QA_PASSED|QA_REJECTED)[ \t]*$", re.MULTILINE
+)
+_CITE_RE = re.compile(r"^[ \t]*CITE:[ \t]*(\S+):(\d+)[.,;:!?]*[ \t]*$", re.MULTILINE)
+_VALID_JUDGE_VERDICTS = ("QA_PASSED", "QA_REJECTED")
+_CITE_TRAILING_PUNCT = ".,;:!?"
 
 
 class UnparseableVerdict(ValueError):
@@ -39,22 +43,46 @@ class GateResult:
 def parse_verdict(reply: str) -> tuple[str, list[tuple[str, int]]]:
     """Parse a QA reply into (verdict, [(file, line), ...]) with one regex each.
 
+    Fail-closed: exactly ONE VERDICT line must be present — zero or
+    multiple lines raise. Leading spaces/tabs are tolerated; CRLF is
+    covered by the trailing blank match. Trailing punctuation on a cite
+    path (e.g. ``foo.py:12.``) is stripped, never accepted.
+
     Raises:
-        UnparseableVerdict: if no VERDICT line is present.
+        UnparseableVerdict: if there is not exactly one VERDICT line.
     """
-    match = _VERDICT_RE.search(reply)
-    if not match:
+    matches = _VERDICT_RE.findall(reply)
+    if len(matches) != 1:
         raise UnparseableVerdict(
-            "No machine-readable VERDICT line (expected "
-            "'VERDICT: QA_PASSED' or 'VERDICT: QA_REJECTED')."
+            f"Expected exactly one VERDICT line, found {len(matches)} "
+            "(expected 'VERDICT: QA_PASSED' or 'VERDICT: QA_REJECTED')."
         )
-    cites = [(path, int(line)) for path, line in _CITE_RE.findall(reply)]
-    return match.group(1), cites
+    cites = [
+        (path.rstrip(_CITE_TRAILING_PUNCT), int(line))
+        for path, line in _CITE_RE.findall(reply)
+    ]
+    return matches[0], cites
+
+
+def _lookup_dotted(record: dict, dotted: str) -> bool:
+    """True when a dotted path (``a.b.c``) resolves through nested dicts."""
+    current: object = record
+    for part in dotted.split("."):
+        if not isinstance(current, dict) or part not in current:
+            return False
+        current = current[part]
+    return True
 
 
 def check_schema(record: dict, required: list[str]) -> list[str]:
-    """Missing required fields → one violation string each."""
-    return [f"missing field: {name}" for name in required if name not in record]
+    """Missing required fields → one violation string each.
+
+    Entries may use dotted paths (``verdict.payload``) to require nested
+    keys, not just top-level ones.
+    """
+    return [
+        f"missing field: {name}" for name in required if not _lookup_dotted(record, name)
+    ]
 
 
 def check_budget(used: int, limit: int) -> list[str]:
@@ -65,13 +93,28 @@ def check_budget(used: int, limit: int) -> list[str]:
 
 
 def check_allowlist(paths: list[str], roots: list[str]) -> list[str]:
-    """Paths escaping every allowed root → one violation string each."""
+    """Paths escaping every allowed root → one violation string each.
+
+    Both sides are normalized with ``realpath`` (resolves ``..`` AND
+    symlinks — ``abspath`` alone leaves symlink escapes open) and
+    containment is enforced with ``commonpath``, so sibling-prefix
+    paths (``/allow-evil`` vs root ``/allow``) never match.
+    Relative payload paths (the production shape) are resolved against
+    the process CWD before comparison.
+    """
+    norm_roots = [os.path.realpath(root) for root in roots]
     violations = []
     for path in paths:
-        if not any(
-            Path(path) == Path(root) or Path(root) in Path(path).parents
-            for root in roots
-        ):
+        norm_path = os.path.realpath(path)
+        try:
+            inside = any(
+                norm_path == norm_root
+                or os.path.commonpath([norm_path, norm_root]) == norm_root
+                for norm_root in norm_roots
+            )
+        except ValueError:
+            inside = False  # e.g. different drives — fail closed
+        if not inside:
             violations.append(f"path outside allowlist: {path}")
     return violations
 
@@ -112,7 +155,14 @@ def run_gate(
     if violations:
         return GateResult(verdict="QA_REJECTED", violations=violations)
     if judge is not None:
+        judge_verdict = judge()
+        if judge_verdict not in _VALID_JUDGE_VERDICTS:
+            return GateResult(
+                verdict="QA_REJECTED",
+                violations=[f"invalid judge verdict: {judge_verdict!r}"],
+                judge_called=True,
+            )
         return GateResult(
-            verdict=judge(), violations=[], judge_called=True
+            verdict=judge_verdict, violations=[], judge_called=True
         )
     return GateResult(verdict=verdict, violations=[])
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index 1c2aba1..746a0d3 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -1088,3 +1088,61 @@ def test_task_attach_truncation_has_pull_path(tmp_path, monkeypatch):
     attach = bridge._build_task_attach("200-foo")
     assert "read_file(" in attach and "200-foo.md" in attach
     assert len(attach) < 30000
+
+
+def test_task_attach_pull_path_is_lane_relative_and_live(tmp_path, monkeypatch):
+    d = tmp_path / "tasks" / "backlog"
+    d.mkdir(parents=True, exist_ok=True)
+    (d / "200-foo.md").write_text(
+        "# T\n<!-- BEGIN_GIT_DIFF -->\nx\n<!-- END_GIT_DIFF -->\n",
+        encoding="utf-8")
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    attach = bridge._build_task_attach("200-foo")
+    assert "tasks/backlog/200-foo.md" in attach
+    pulled = bridge._read_file_impl("tasks/backlog/200-foo.md")
+    assert pulled["total_lines"] == 4
+
+
+def test_grep_skips_symlink_escape(tmp_path, monkeypatch):
+    ws = tmp_path / "ws"
+    sub = ws / "docs"
+    sub.mkdir(parents=True)
+    (sub / "real.md").write_text("hello\n", encoding="utf-8")
+    outside = tmp_path / "outside-secret.md"
+    outside.write_text("SECRET-XYZ\n", encoding="utf-8")
+    (sub / "evil.md").symlink_to(outside)
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: ws)
+    hits = bridge._grep_files_impl("SECRET-XYZ", "docs")
+    assert hits == []
+
+
+def test_read_file_limit_clamped(tmp_path, monkeypatch):
+    (tmp_path / "big.md").write_text(
+        "".join(f"line {n}\n" for n in range(2500)), encoding="utf-8")
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    result = bridge._read_file_impl("big.md", limit=10 ** 9)
+    assert result["limit"] == bridge._READ_MAX_LINES
+    assert len(result["lines"]) == bridge._READ_MAX_LINES
+
+
+def test_read_file_oversize_refused(tmp_path, monkeypatch):
+    (tmp_path / "huge.md").write_bytes(b"x" * (bridge._READ_MAX_BYTES + 1))
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    with pytest.raises(ValueError, match="too large"):
+        bridge._read_file_impl("huge.md")
+
+
+def test_grep_pattern_too_long_rejected(tmp_path, monkeypatch):
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    with pytest.raises(ValueError, match="too long"):
+        bridge._grep_files_impl("a" * (bridge._GREP_PATTERN_MAX + 1))
+
+
+def test_grep_skips_overlong_lines(tmp_path, monkeypatch):
+    sub = tmp_path / "docs"
+    sub.mkdir()
+    (sub / "mix.md").write_text(
+        "MATCH " + ("z" * 5000) + "\nplain MATCH line\n", encoding="utf-8")
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    hits = bridge._grep_files_impl("MATCH", "docs")
+    assert len(hits) == 1 and ":2:" in hits[0]
diff --git a/tests/test_rules_gate.py b/tests/test_rules_gate.py
index 2ceb3d0..fefc856 100644
--- a/tests/test_rules_gate.py
+++ b/tests/test_rules_gate.py
@@ -127,3 +127,115 @@ def test_gate_clean_no_judge_passes():
     )
     assert result.verdict == "QA_PASSED"
     assert result.judge_called is False
+
+
+def test_allowlist_relative_inside():
+    assert check_allowlist(["a/b.py"], roots=["."]) == []
+
+
+def test_allowlist_relative_escape(tmp_path, monkeypatch):
+    sub = tmp_path / "sub"
+    sub.mkdir()
+    monkeypatch.chdir(sub)
+    assert check_allowlist(["../evil.py"], roots=["."]) != []
+
+
+def test_parse_two_verdicts_raise():
+    reply = "VERDICT: QA_PASSED\nSome prose.\nVERDICT: QA_REJECTED\n"
+    with pytest.raises(UnparseableVerdict):
+        parse_verdict(reply)
+
+
+def test_parse_leading_space_verdict():
+    verdict, _ = parse_verdict("  VERDICT: QA_PASSED  \n")
+    assert verdict == "QA_PASSED"
+
+
+def test_gate_judge_garbage_rejected():
+    judge = Mock(return_value="MAYBE")
+    result = run_gate(
+        {"verdict_reply": PASSED_REPLY, "paths": []},
+        required=[],
+        budget=(0, 1_000_000),
+        allowlist_roots=["/repo"],
+        judge=judge,
+    )
+    assert result.verdict == "QA_REJECTED"
+    assert result.judge_called is True
+    assert any("invalid judge verdict" in v for v in result.violations)
+
+
+def test_schema_nested_missing():
+    assert check_schema({"a": {"b": 1}}, required=["a.b", "a.c"]) == [
+        "missing field: a.c"
+    ]
+
+
+def test_parse_cite_trailing_period():
+    verdict, cites = parse_verdict("CITE: foo.py:12.\nVERDICT: QA_PASSED\n")
+    assert verdict == "QA_PASSED"
+    assert cites == [("foo.py", 12)]
+
+
+def test_allowlist_sibling_prefix_rejected():
+    violations = check_allowlist(
+        ["/repo/allow-evil/x.py"], roots=["/repo/allow"]
+    )
+    assert violations == ["path outside allowlist: /repo/allow-evil/x.py"]
+
+
+def test_allowlist_symlink_escape_rejected(tmp_path):
+    allowed = tmp_path / "allowed"
+    allowed.mkdir()
+    secret = tmp_path / "secret.txt"
+    secret.write_text("top secret")
+    link = allowed / "link.py"
+    link.symlink_to(secret)
+    assert check_allowlist([str(link)], roots=[str(allowed)]) == [
+        f"path outside allowlist: {link}"
+    ]
+
+
+def test_allowlist_symlink_inside_passes(tmp_path):
+    allowed = tmp_path / "allowed"
+    allowed.mkdir()
+    real = allowed / "real.py"
+    real.write_text("x = 1")
+    link = allowed / "link.py"
+    link.symlink_to(real)
+    assert check_allowlist([str(link)], roots=[str(allowed)]) == []
+
+
+def test_parse_indented_second_marker_raises():
+    reply = "VERDICT: QA_PASSED\n  VERDICT: QA_REJECTED\n"
+    with pytest.raises(UnparseableVerdict):
+        parse_verdict(reply)
+
+
+def test_gate_judge_none_rejected():
+    judge = Mock(return_value=None)
+    result = run_gate(
+        {"verdict_reply": PASSED_REPLY, "paths": []},
+        required=[],
+        budget=(0, 1_000_000),
+        allowlist_roots=["/repo"],
+        judge=judge,
+    )
+    assert result.verdict == "QA_REJECTED"
+    assert result.judge_called is True
+    assert any("invalid judge verdict" in v for v in result.violations)
+
+
+def test_schema_deep_nested_and_nondict_mid():
+    assert check_schema({"a": {"b": {"c": 1}}}, required=["a.b.c"]) == []
+    assert check_schema({"a": {"b": {"c": 1}}}, required=["a.b.d"]) == [
+        "missing field: a.b.d"
+    ]
+    assert check_schema({"a": 5}, required=["a.b"]) == ["missing field: a.b"]
+
+
+def test_parse_cite_version_and_all_punct_tails():
+    reply = "CITE: pkg/v1.2:34\nCITE: foo.py:12.,;:!?\nVERDICT: QA_PASSED\n"
+    verdict, cites = parse_verdict(reply)
+    assert verdict == "QA_PASSED"
+    assert cites == [("pkg/v1.2", 34), ("foo.py", 12)]
```
<!-- END_GIT_DIFF -->
