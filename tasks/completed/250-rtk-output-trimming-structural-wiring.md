# Task 250: RTK Output-Trimming Structural Wiring

**File:** `tasks/qa/250-rtk-output-trimming-structural-wiring.md`
**Source:** manager
**Type:** improvement
**Status:** open
**Mode:** autopilot-locked

## Goal

Make RTK output-trimming usage structural instead of advisory so agents use it on every verification run.

## Manager's Notes

Full-automatic mode applies (stored order `manager/full_automatic_mode`, zero questions). Manager found ~0% RTK usage across recent tasks and ordered: discover the reason and fix it. Discovery (read-only subagent, verified): `rtk` 0.49.0 binary live at `~/.local/bin/rtk`; mandate exists only as RULE 3b in `prompts/fragments/09-hands_protocols.md` plus `system-prompt.md`; no RTK skill exists; `agents/cognitive-executor.md` never names RTK; task files prescribe raw `uv run ... pytest` commands; no enforcement gate checks actual usage. Proven: `rtk test <suite>` collapses the 491-test verdict to 3 lines with exit code preserved. This task wires the mandate into the executor protocol, the task template, and project memory. Scope is wiring plus docs only; no behavior change to any MCP server.

## Local TODOs

- [x] Map RTK mandate points with Brain (fragment, executor matrix, template, memory)
- [x] Add RTK row to the executor Skill Auto-Loading Matrix or protocol section
- [x] Update the task-generator template Verification Evidence command to `rtk test` prefix
- [x] Store the RTK-first rule in project memory
- [x] Run the full suite via `rtk test` with exit code 0
- [x] Update CHANGELOG via Parse-Then-Append
- [x] Lint the task file, stage, move to qa, re-stage

## Acceptance Criteria

- [x] Executor protocol names RTK as the default verification runner
- [x] New task files prescribe `rtk test` prefixed verification commands
- [x] Project memory holds the RTK-first rule for cross-session stickiness
- [x] Full test suite passes with exit code 0 via `rtk test`

## Verification Evidence

- **Test command:** `rtk test uv run --with pytest --with 'mcp[cli]==1.30.0' --with pathspec --with pyyaml pytest tests/ -q`
- **Expected result:** all tests pass, exit code 0
- **Actual result:** 502 passed, 10 warnings in 4.31s
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** prompt rebuild needed if the mandate moves into the shipped system prompt.
- **Rollback plan:** revert the feature commit hash; wiring is docs-only so rollback is trivial.

---

## Execution Log & Reasoning

Plan approved implicitly under the full-auto standing order (zero questions; Brain Architect advisory plan, no pre-approval procedure). Discovery correction: the task-generator template carries no raw command (placeholder `[exact command]` only) — raw prescribers were individual task files, the executor example, and normative docs. TDD: 3 new tests in `tests/test_prompt_sync.py` written first (RED: 3 failed for the right reason; one self-inflicted IndentationError from a no-op edit fixed in the test file). GREEN changes: RULE 3b extended operationally (first run RTK, prefixed command recorded, raw only post-failure); executor Verification Runner policy added after the Observe rule plus RTK-prefixed evidence example (other verification sections checked — generic, no contradiction); template placeholder changed to `rtk test [exact command]` in both templates with a runner rule; memory entry overwritten canonically; 4 normative prescribers normalized (setup, brain-bridge, workflow-upgrade, upgrade-runbook memory); version 9.39.0 to 9.40.0 with byte-identical double rebuild. Focused suite 8/8, full suite 502 passed exit 0 via `rtk test` (3-line verdict). Existing executor content asserts untouched (edits additive; full suite green proves it).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.opencode/memory/workflows/global-install-upgrade.md b/.opencode/memory/workflows/global-install-upgrade.md
index 40e6619..cad1645 100644
--- a/.opencode/memory/workflows/global-install-upgrade.md
+++ b/.opencode/memory/workflows/global-install-upgrade.md
@@ -38,7 +38,7 @@ Updates the machine-global installations of the Cognitive Lead AI HQ (MCP server
 2. **Copy drifted files** with `cp` + `chmod +x` (only those that differ). Multi-module servers copy `*.py` (never `__pycache__/`). For `opencode.json` do NOT blind copy — repo uses relative paths, global uses absolute paths; edit surgically and validate JSON after every edit.
 2b. **Delete global orphans** (rule added 2026-09-11: `cp` never removes, so deletions need this step). Any skill dir present under `~/.config/opencode/skills/` but absent from repo `skill-templates/` MUST be removed with `rm -rf` — that is how skill drops (e.g. brainstorm-swarm, perplexity-research) propagate globally. Same for MCP server dirs and custom agents missing from the repo. Never delete in the reverse direction (repo is source of truth).
 3. **Re-verify** with the same diff commands — expect no DRIFT output except the expected `opencode.json` relative vs absolute.
-4. **Smoke-test**: `opencode mcp list` (expect ONLY the currently-enabled servers connected) + repo persona test suite (`uv run --project mcp-persona-server --with pytest --with pathspec pytest tests/ -q`).
+4. **Smoke-test**: `opencode mcp list` (expect ONLY the currently-enabled servers connected) + repo persona test suite (`rtk test uv run --project mcp-persona-server --with pytest --with pathspec pytest tests/ -q`).
 4b. **RTK install** (rule added 2026-09-12): the token-trimming runner from `docs/opencode-shell-strategy.md` §8. Install the musl binary when missing (`mkdir -p ~/.local/bin && curl -fsSL -o ~/.local/bin/rtk <release-url>/rtk-x86_64-unknown-linux-musl && chmod +x ~/.local/bin/rtk`), verify `rtk --version`. Never run `rtk init -g` — it rewrites the global OpenCode config.
 5. **Telegram MCP step 2.5** (upstream chigwell/telegram-mcp): lag check via `rev-list --count HEAD..origin/main`; run backup+rsync upgrade only when lag > 0. **Update-only — do NOT run telegram's own pytest suite** (its live-network tests hang ~300s on this machine and add nothing; `opencode mcp list` 5/5 is the sufficient smoke test). Rule set 2026-09-10 per Manager.
 
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 6fb7918..dd0d8f7 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **RTK output-trimming structural wiring (Task 250):** RTK-first is now structural, not advisory. `prompts/fragments/09-hands_protocols.md` RULE 3b requires every test-suite verification to begin with `rtk test <underlying command>` and the exact prefixed command recorded in Verification Evidence (raw rerun only after failure, for diagnostics); `agents/cognitive-executor.md` gains a Verification Runner policy plus an RTK-prefixed evidence example; `skill-templates/task-generator/SKILL.md` template prescribes `rtk test [exact command]` with a runner rule; normative raw prescribers normalized (`docs/setup.md`, `docs/brain-bridge.md`, `docs/workflow-upgrade-v8.4.5.md`, upgrade-runbook memory); project memory holds one canonical RTK-first rule. Shipped prompt rebuilt to 9.40.0 (byte-identical double build). 3 new regression tests in `tests/test_prompt_sync.py` (executor default runner, evidence recording, template prescription) plus version-pin update. Full suite: **502 passed**.
 - **English-only reasoning plus input-validation enforcement (Task 252):** resolved the clarification-language contradiction — `prompts/fragments/05-user_input_processing.md` now runs the Input Validation Gate as step 0 (before topic-shift detection, renumbered 0.5), clarification halts output simple English, and the pipeline order validate-normalize-translate-enrich-prompt-refactor is explicit; `prompts/fragments/13-constraints.md` Cognitive Language Rule is authoritative (English always, quoted source material only); `docs/conventions.md`, `AGENTS.md`, and `agents/cognitive-executor.md` clarification halts all say simple English; executor Skill Matrix gains mandatory `prompt-refactor` for implementation-producing input. Shipped prompt rebuilt to 9.39.0 (deterministic, byte-identical double build). New `tests/test_input_validation_pipeline.py` (6 tests) plus 3 shipped-prompt gates in `tests/test_prompt_sync.py`. Full suite: **499 passed**.
 - **Authority-ranked retrieval plus offline eval harness (Task 249):** two new pure modules, zero behavior change to existing stores. `mcp-brain-bridge/authority_retrieval.py` ranks candidates lexicographically (authority decision 4 > memory 3 > repo 2 > web 1, then local score, then id for determinism), gathers the top 20 across source adapters (each called once, pre-cap count in diagnostics), and narrows to 5 preferring chunk overlap (case-folded word tokens, overlap coefficient, 0.20 threshold, fill from ranked list, overlap pairs reported). `mcp-brain-bridge/eval_harness.py` scores structured traces: parse rate, citation rate, grounding rate (full-support only), rule pass rate (missing actual counts as failure), ZAC scan over structured operations only (`git add`/`commit`/`push`, case-insensitive, command or normalized name), QA repair totals, cost/latency columns that stay null when missing and aggregate over observed values only. Caller-owned goldens under `tests/golden/` (`authority_retrieval_cases.json`, `eval_harness_cases.json`, schema_version 1) executed by `tests/test_golden_cases.py` with fixture-immutability proof. 34 new tests. Full suite: **486 passed**. QA hotfix: missing/null/invalid `qa_repairs` now stays `None` (explicit 0 still observed), aggregates over observed counts only with `qa_repair_observed_case_count`, 5 new tests. Full suite: **491 passed**.
 - **Manager-decision shape hardening (Task 248):** `mcp-decision-server/server.py` no longer crashes on malformed shapes. `_validate_extracted_candidates` drops non-string-tradeoffs candidates in place with a loud stderr note and keeps validating the rest, so one bad model candidate never nukes the valid ones (all-malformed yields [] via the empty-result path; N1 one-repair and all transport-level fail-loud errors unchanged). `_scrub_free_text` validates nested mappings up front and raises clean ValueError on string-typed verbatim_quote/extracted_decision or non-list alternatives — nothing reaches the append-only store. `query_manager_decisions` skips non-dict records/sub-objects and non-list alternatives with stderr notes instead of raising AttributeError. `get_manager_profile` absent-sample message confirmed intentional and tested, unchanged. 6 new regression tests. QA hotfix: 2 profile contract tests plus 6 nested-leaf validations (all 5 text leaves and every alternatives item string-checked, field-named ValueError before any write). QA hotfix 2: recall validates the raw alternatives value before normalization so falsey non-lists (None/""/0/False) no longer launder into []. Full suite: **452 passed**.
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 7d401b7..317b266 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -161,6 +161,10 @@ For every task, follow this bounded iteration loop:
 
 Do not skip the observe step. Every code change MUST be verified before claiming completion.
 
+### Verification Runner (RTK by default)
+
+Test-suite verification runs begin with `rtk test <underlying command>` by default. Inspect the active task's `## Verification Evidence` before running verification and record the exact `rtk test`-prefixed command, expected result, actual result, and exit code there. A raw test command is a diagnostic retry after a failed RTK run only — it never replaces the initial RTK verification run. Never claim completion without a successful exit code and recorded evidence.
+
 ### Circuit Breakers
 
 If you detect any of these failure modes, HALT immediately and surface to the Manager:
@@ -206,7 +210,7 @@ Result: Massive diff, unrelated changes, difficult to review.
 ### Correct: Evidence-Based Completion
 
 ```
-Claim: "Task complete. Verification: `pytest tests/` exits 0, all 47 tests pass."
+Claim: "Task complete. Verification: `rtk test pytest tests/` exits 0, all 47 tests pass."
 ```
 
 ### Incorrect: Unverified Completion
diff --git a/docs/brain-bridge.md b/docs/brain-bridge.md
index 5d3f56b..b1e9e8b 100644
--- a/docs/brain-bridge.md
+++ b/docs/brain-bridge.md
@@ -120,7 +120,7 @@ so autopilot gets smarter over time.
 ## Verify
 
 ```bash
-uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py -q
+rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py -q
 ```
 
 Live calls need a valid `BRAIN_API_KEY` for the configured
diff --git a/docs/setup.md b/docs/setup.md
index fede78d..306b9ae 100644
--- a/docs/setup.md
+++ b/docs/setup.md
@@ -91,6 +91,6 @@ projects served by the daemon share them.
 # Format all Markdown files
 npx prettier --write "**/*.md"
 
-# Run tests
-uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
+# Run tests (RTK-first: passing suites collapse to a verdict summary)
+rtk test uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
 ```
diff --git a/docs/workflow-upgrade-v8.4.5.md b/docs/workflow-upgrade-v8.4.5.md
index af7c9ba..cc2cd4a 100644
--- a/docs/workflow-upgrade-v8.4.5.md
+++ b/docs/workflow-upgrade-v8.4.5.md
@@ -48,7 +48,7 @@ The upgrade is **backward compatible** — existing task files do not break:
    pass (backward-compatible), but keeps the project uniform:
    `## OpenCode Execution Log & Reasoning` → `## Execution Log & Reasoning`.
 5. **Run `lint_task_file` after migrating** to confirm the structural checks pass clean.
-6. **Run the regression suite** (`pytest tests/ -q`) to confirm the runtime-agnostic guards pass.
+6. **Run the regression suite** (`rtk test pytest tests/ -q`) to confirm the runtime-agnostic guards pass.
 
 ## 4. What NOT to Change
 
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 7753c56..80c7af2 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.39.0</system_version>
+<system_version>9.40.0</system_version>
diff --git a/prompts/fragments/09-hands_protocols.md b/prompts/fragments/09-hands_protocols.md
index 6118f2c..b6c8cc9 100644
--- a/prompts/fragments/09-hands_protocols.md
+++ b/prompts/fragments/09-hands_protocols.md
@@ -73,7 +73,7 @@
     CRITICAL RULE 1: ALL bash commands MUST use non-interactive flags (e.g., `npm install -y`, `pytest --no-header`). Do NOT run interactive commands like `vim`, `less`, or `nano`.
     CRITICAL RULE 2: Zero-Autonomous-Commit (ZAC). You are STRICTLY FORBIDDEN from executing `git add`, `git commit`, or `git push` autonomously. The ONLY permitted autonomous Git operation is `git mv` for Kanban task-file transitions. You may ONLY run other Git commands if they are explicitly listed by the Orchestrator in this `<bash_phase>`. Do not guess or auto-commit.
     CRITICAL RULE 3: The local agent truncates terminal output over 2000 lines or 50KB. If running test suites with massive output, pipe through grep or tail to ensure the verification-before-completion gate receives the success confirmation without truncation.
-    CRITICAL RULE 3b (Token trimming): Run test suites via `rtk test <cmd>` so passing suites collapse to a verdict summary; on ANY failure re-run without the wrapper and keep the full output — never collapse failing output.
+    CRITICAL RULE 3b (Token trimming): Every test-suite verification run begins with `rtk test <underlying command>` so passing suites collapse to a verdict summary; the exact `rtk test`-prefixed command MUST be recorded in the `## Verification Evidence` section of the active task file. RTK preserves the underlying command's exit code. On ANY failure re-run without the wrapper and keep the full output — never collapse failing output. A raw rerun is allowed only after a failed RTK run for detailed diagnostics and never replaces the initial RTK verification run.
     CRITICAL RULE 4 (For Orchestrator — file staging): If the active task is currently in tasks/backlog/, you MUST explicitly include the command "git mv tasks/backlog/XX-task.md tasks/in-progress/XX-task.md" as the very first command in this bash phase. This ensures the Hands can stage the file without violating Zero-Autonomous-Commit.
     CRITICAL RULE 5 (Pre-Commit Verification Gate): For DevOps, infrastructure, or deployment tasks, the verification gate MUST include environment-specific checks (registry authentication, token scope validation, network access) BEFORE staging any files. If ANY pre-commit check fails, HALT and output a `<failure_report>`. Do NOT stage or commit partial work.
     CRITICAL RULE 6 (Evidence Capture): Before proceeding to the `<summary_phase>`, you MUST capture the exact test command, expected result, actual result, and exit code. You MUST write these into the `## Verification Evidence` section of the active task file.
diff --git a/skill-templates/task-generator/SKILL.md b/skill-templates/task-generator/SKILL.md
index 524fd79..386cca8 100644
--- a/skill-templates/task-generator/SKILL.md
+++ b/skill-templates/task-generator/SKILL.md
@@ -115,12 +115,14 @@ If the output is non-empty, HALT and report duplicate task IDs. Do NOT overwrite
    - [ ] [Criterion 1 — what must be true for this task to be considered done]
    - [ ] [Criterion 2]
 
-   ## Verification Evidence
+    ## Verification Evidence
 
-   - **Test command:** [exact command]
-   - **Expected result:** [what success looks like]
-   - **Actual result:** _(The Hands fill this during execution)_
-   - **Exit code:** _(The Hands fill this during execution)_
+    - **Test command:** rtk test [exact command]
+    - **Expected result:** [what success looks like]
+    - **Actual result:** _(The Hands fill this during execution)_
+    - **Exit code:** _(The Hands fill this during execution)_
+
+    > Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.
 
    ## Definition of Done
 
@@ -176,11 +178,13 @@ If the Orchestrator specifies `multi_phase: true`, generate a SINGLE task file w
 
 ## Verification Evidence
 
-- **Test command:** [exact command]
+- **Test command:** rtk test [exact command]
 - **Expected result:** [what success looks like]
 - **Actual result:** _(The Hands fill this during execution)_
 - **Exit code:** _(The Hands fill this during execution)_
 
+> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.
+
 ## Definition of Done
 
 The task is NOT done unless ALL of the following are true (unconditional, applies to every multi-phase task):
diff --git a/system-prompt.md b/system-prompt.md
index 8eb5dc9..9d1ca61 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.39.0</system_version>
+<system_version>9.40.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -300,7 +300,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
     CRITICAL RULE 1: ALL bash commands MUST use non-interactive flags (e.g., `npm install -y`, `pytest --no-header`). Do NOT run interactive commands like `vim`, `less`, or `nano`.
     CRITICAL RULE 2: Zero-Autonomous-Commit (ZAC). You are STRICTLY FORBIDDEN from executing `git add`, `git commit`, or `git push` autonomously. The ONLY permitted autonomous Git operation is `git mv` for Kanban task-file transitions. You may ONLY run other Git commands if they are explicitly listed by the Orchestrator in this `<bash_phase>`. Do not guess or auto-commit.
     CRITICAL RULE 3: The local agent truncates terminal output over 2000 lines or 50KB. If running test suites with massive output, pipe through grep or tail to ensure the verification-before-completion gate receives the success confirmation without truncation.
-    CRITICAL RULE 3b (Token trimming): Run test suites via `rtk test <cmd>` so passing suites collapse to a verdict summary; on ANY failure re-run without the wrapper and keep the full output — never collapse failing output.
+    CRITICAL RULE 3b (Token trimming): Every test-suite verification run begins with `rtk test <underlying command>` so passing suites collapse to a verdict summary; the exact `rtk test`-prefixed command MUST be recorded in the `## Verification Evidence` section of the active task file. RTK preserves the underlying command's exit code. On ANY failure re-run without the wrapper and keep the full output — never collapse failing output. A raw rerun is allowed only after a failed RTK run for detailed diagnostics and never replaces the initial RTK verification run.
     CRITICAL RULE 4 (For Orchestrator — file staging): If the active task is currently in tasks/backlog/, you MUST explicitly include the command "git mv tasks/backlog/XX-task.md tasks/in-progress/XX-task.md" as the very first command in this bash phase. This ensures the Hands can stage the file without violating Zero-Autonomous-Commit.
     CRITICAL RULE 5 (Pre-Commit Verification Gate): For DevOps, infrastructure, or deployment tasks, the verification gate MUST include environment-specific checks (registry authentication, token scope validation, network access) BEFORE staging any files. If ANY pre-commit check fails, HALT and output a `<failure_report>`. Do NOT stage or commit partial work.
     CRITICAL RULE 6 (Evidence Capture): Before proceeding to the `<summary_phase>`, you MUST capture the exact test command, expected result, actual result, and exit code. You MUST write these into the `## Verification Evidence` section of the active task file.
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index d75a889..61c46a8 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -13,6 +13,8 @@ REPO = Path(__file__).resolve().parent.parent
 SHIPPED = REPO / "system-prompt.md"
 FRAGMENT_01 = REPO / "prompts" / "fragments" / "01-system_version.md"
 ASSEMBLER = REPO / "scripts" / "prompt-build" / "assemble_system_prompt.py"
+EXECUTOR = REPO / "agents" / "cognitive-executor.md"
+TASKGEN_SKILL = (REPO / "skill-templates" / "task-generator" / "SKILL.md")
 
 
 def _read(path):
@@ -37,7 +39,7 @@ def test_shipped_version_matches_fragment():
 def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(r"<system_version>(.*?)</system_version>",
                         _read(SHIPPED)).group(1)
-    assert shipped == "9.39.0"
+    assert shipped == "9.40.0"
 
 
 def test_no_manager_language_rule_in_shipped_prompt():
@@ -54,3 +56,21 @@ def test_assembler_output_matches_shipped(tmp_path):
         capture_output=True, text=True, cwd=str(REPO))
     assert proc.returncode == 0, proc.stderr[-2000:]
     assert out.read_text(encoding="utf-8") == _read(SHIPPED)
+
+
+def test_executor_names_rtk_default_runner():
+    text = _read(EXECUTOR)
+    assert "rtk test" in text
+    assert "default" in text.lower()
+    assert "first" in text.lower()
+
+
+def test_executor_evidence_records_rtk_command():
+    text = _read(EXECUTOR)
+    assert "Verification Evidence" in text
+    assert "rtk test" in text
+
+
+def test_task_generator_template_prescribes_rtk():
+    text = _read(TASKGEN_SKILL)
+    assert "rtk test [exact command]" in text
```
<!-- END_GIT_DIFF -->
