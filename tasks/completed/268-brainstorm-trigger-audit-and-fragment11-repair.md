# Task 268: Make the brainstorm trigger auditable and repair fragment 11

**File:** `tasks/qa/268-brainstorm-trigger-audit-and-fragment11-repair.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Goal

Stop the Brain's brainstorming trigger from being automatic, and repair the stale
fragment that says it is. Two deliverables, both prompt-level:

- **A1** — every plan states one auditable line naming whether a brainstorm was
  required, with a reason. The rule: a task that is cross-disciplinary and hard
  to reverse requires the full seven-seat report.
- **A2** — repair `prompts/fragments/11-execution_workflow.md`: replace the old
  out-of-band panel names with the seven seats declared in `<personas>`, make
  step 2 conditional and consistent with fragment 12, and repair the dead
  `user-prompts/` research pointer.

## Manager's Notes

- Authorization: "Task A1 and A2 and plan and implement then full automatically".
- The current system prompt contradicts itself. Fragment 11 says the
  Orchestrator *automatically* invokes the brainstorming loop as step 2.
  Fragment 12 says the loop fires on a trigger. These are opposite policies.
- Fragment 11 also names a panel that no longer exists: `Architect, Security,
  PM, Strategist, Critical Thinker`. Fragment 12 declares the panel to be
  exactly the seven `<personas>` seats.
- The earlier audit missed this. Task 180's verification grep searched
  snake_case identifiers only, so the display name `Critical Thinker` survived.
- Do **not** create a brainstorm skill. Fragment 12 states this protocol is the
  only brainstorming path in the system. A skill would contradict it.
- Do **not** force the brainstorm always on. Cost and signal dilution are the
  reasons recorded in the analysis; the auditable line is the middle path.
- Historical records that legitimately quote the old scheme must not be
  touched: `CHANGELOG.md` entries, `docs/history/`, `tasks/archive/`.

## Local TODOs

- [x] Read `prompts/fragments/12-brainstorming_protocol.md` and `11-execution_workflow.md` at the current revision
- [x] A1: add the auditable brainstorm-decision rule to the protocol fragment
- [x] A1: add the matching sentence to the Hands planning gate in `agents/cognitive-executor.md`
- [x] A2: rewrite fragment 11 step 2 (seven seats, conditional trigger)
- [x] A2: repair the dead `user-prompts/` research pointer in fragment 11
- [x] Regenerate `system-prompt.md` and bump `<system_version>`
- [x] Verify: prompt-sync, RTK suite, markdown lint, task-file lint

## Acceptance Criteria

- [x] `prompts/fragments/11-execution_workflow.md` names the seven `<personas>` seats and states the trigger as conditional, matching fragment 12.
- [x] No live prompt fragment or generated `system-prompt.md` text still names the removed panel (`Architect, Security, PM, Strategist, Critical Thinker`).
- [x] The dead `user-prompts/` reference in fragment 11 is replaced by the current research path (`blowsh` skill).
- [x] A1: the protocol fragment requires the plan to state one line naming whether a brainstorm was required and why.
- [x] A1: the executor planning gate carries the matching instruction.
- [x] `system-prompt.md` is regenerated, `<system_version>` is bumped to 9.42.0, and the assembler output is byte-identical to the shipped file (proven by `tests/test_prompt_sync.py::test_assembler_output_matches_shipped`).
- [x] `CHANGELOG.md` carries an `[Unreleased]` entry.
- [x] RTK suite exits 0 and `lint_task_file` passes.

## Verification Evidence

- **Test command:** rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
- **Expected result:** all tests pass, plus `lint_system_prompt_sync` reports in sync and `lint_markdown`/`lint_task_file` pass
- **Actual result:** RTK suite green — `686 passed, 10 warnings in 4.72s` (one earlier run failed only on `test_shipped_version_is_expected_minor_bump`; the pinned expectation was updated to 9.42.0). `tests/test_prompt_sync.py::test_assembler_output_matches_shipped` proves the shipped prompt is byte-identical to a fresh assembly — the `lint_system_prompt_sync` MCP tool cannot run here because it resolves the assembler under the global install root. `lint_markdown` passed on both edited fragments; `lint_task_file` passed; a grep for `Critical Thinker` and `user-prompts/` across `system-prompt.md`, `prompts/` and `agents/` returned zero hits.
- **Exit code:** `0`

> Verification runner rule: `uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** editing a prompt fragment without regenerating `system-prompt.md` leaves committed drift; a wording change could also weaken the hard-gate language that keeps brainstorming available for genuinely ambiguous work.
- **Rollback plan:** revert this single commit. Only `prompts/fragments/11-execution_workflow.md`, `prompts/fragments/12-brainstorming_protocol.md`, `system-prompt.md`, `agents/cognitive-executor.md` and `CHANGELOG.md` are touched.

---

## Execution Log & Reasoning

### Pipeline authorization

Standing order `manager/full_automatic_mode` (2026-09-17) plus the Manager's order m0153 — "Task A1 and A2 and plan and implement then full automatically" — authorize plan-then-implement with no separate plan-approval pause (DEC-20260920-001). The Brain plan turn ran under `task_id=268`, `stage=plan`; its verdict and selected path are recorded here. The plan closed by asking for "Reply Approved"; that ask was already satisfied by the Manager's own order, which names the implement step.

### What changed

1. `prompts/fragments/12-brainstorming_protocol.md` — new `<auditability>` element immediately after `<trigger>`: every plan must state one line, `Brainstorm: required | not required — reason`; cross-disciplinary AND hard-to-reverse work requires the full seven-seat report; the line is recorded in the execution log.
2. `prompts/fragments/11-execution_workflow.md` — step 2 becomes "Conditional Brainstorming Check". It names the seven `<personas>` seats and the protocol's trigger, and records `Brainstorm: not required — <reason>` when the trigger does not fire. Sub-step 2.5's dead `user-prompts/` Perplexity pointer now uses the `blowsh` skill.
3. `prompts/fragments/01-system_version.md` — 9.41.0 → 9.42.0.
4. `system-prompt.md` — regenerated by `uv run python scripts/prompt-build/assemble_system_prompt.py` (88199 bytes); version at line 1, new step 2 at line 432, `blowsh` line at 435, `<auditability>` at 471.
5. `agents/cognitive-executor.md` — the Planning Gate now requires the same auditable line, recorded in the Execution Log beside the plan verdict.
6. `tests/test_prompt_sync.py` — the pinned expectation moved from `9.41.0` to `9.42.0`. That test exists to make every version bump explicit, so it is updated deliberately, not bypassed.
7. `CHANGELOG.md` — `[Unreleased]` entry.

### Root cause of the original drift

Task 180 round 2 replaced the six out-of-band brainstorm personas with the seven `<personas>` seats in fragment 12. Its verification grep — archived at `tasks/archive/180-self-improvement-dual-channel-communication.md:61` — searched snake_case identifiers only (`system_architect|ui-system|/reflect|critical_thinker`). Fragment 11 named the same personas in display form ("Critical Thinker"), so it escaped both the fix and the check.

### Decisions taken

- **A1** shipped as an auditability rule in the protocol plus a matching executor instruction, not as a bridge flag or a `stage` value. Reason: it binds the Brain through its own prompt, needs no code change, and needs no global rebuild.
- **A2** kept the hard gate. The step is conditional, never weakened: an explicit Manager request still always fires the full report.
- No brainstorm skill was created and brainstorming was not made always-on. Both were explicit exclusions in the Manager's analysis.

### Assumptions logged

- **AS1** The pinned-version test is a deliberate gate, not a stray assertion. Reason: its name (`test_shipped_version_is_expected_minor_bump`) and its sibling (`test_shipped_version_matches_fragment`) show the pin exists to force explicit bumps.
- **AS2** `lint_system_prompt_sync` cannot run in this workspace: the MCP server resolves the assembler under the global install root, not the repo. Substituted the in-repo byte-identity test, which invokes the same assembler and compares the output to the shipped file.

### Verification

- `rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q` → **686 passed, 10 warnings, exit 0**.
- `tests/test_prompt_sync.py::test_assembler_output_matches_shipped` proves the shipped prompt is byte-identical to a fresh assembly.
- `lint_markdown` passed on both edited fragments; `lint_task_file` passed.
- Grep for `Critical Thinker` and `user-prompts/` across `system-prompt.md`, `prompts/` and `agents/` → zero hits. Remaining hits are immutable history only.

### Not done (by exclusion)

No brainstorm skill. No always-on brainstorming. No edits to `CHANGELOG.md` history, `docs/history/`, or `tasks/archive/`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index c96ccce..a519823 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -11,6 +11,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Manager-decisions MCP contract doc (Task 267, fixes GitHub issue 25):** new `docs/manager-decisions.md` is the source-verified agent usage contract for the six `manager_decisions` tools. It documents server identity and stdio transport, the `_repo_root()` store resolution order including the fail-closed explicit-path behavior, a six-tool quick-reference table, per-tool sections (signature, arguments, return shape, side effects, failure modes) for `extract_session_decisions`, `record_manager_decision`, `query_manager_decisions`, `get_sync_status`, `get_manager_profile` and `propose_profile_evolution`, the shared decision-record field contract (six required fields, the closed eight-value `category` enum, the `fidelity`/`mode`/`scope` enums, fingerprint and id shapes, server-stamped `active_root`/`store_mode`), an agent pitfalls table, a recommended workflow, a doc-drift table and a could-not-verify list. Every factual claim carries a `mcp-decision-server/*.py:line` citation pinned to commit `0183433`. The issue's claim that the extraction model resolves as `DECISION_MODEL` else `BRAIN_MODEL` is corrected: `BRAIN_MODEL` is never read by this server, `_get_decision_model()` returns `DEFAULT_DECISION_MODEL` (`gpt-6-astra`) unless `DECISION_MODEL` is set, and the deliberate non-fallback target is `PERSONA_MODEL`. Six drift items are reported, not fixed: the seven-of-eight category list in the extraction prompt, the undocumented required `project_name`, the uncapped `query_manager_decisions` result set, the dead `_SCRUB_FIELDS` constant, the push-command mismatch with the skill text, and the stale `detector.py` docstring line numbers. No server source and no skill file was modified. `README.md` and `docs/setup.md` link to the new page, and the README repository tree gains the previously missing `mcp-decision-server/` entry. Full suite: **686 passed** (exit 0); `scripts/check_docs_sync.py` reports `docs-sync: OK`.
 - **manager-decisions write-tool contract fixes (direct Manager request, no task file):** `record_manager_decision`'s `Args` block now documents the full record contract it enforces — the six required fields (`decision_id`, `timestamp`, `project_name`, `verbatim_quote`, `extracted_decision`, `redaction_verified`), the fact that `project_name` is required and never defaulted, the nested `verbatim_quote` and `extracted_decision` shapes, and the closed eight-value `category` enum. The extraction prompt now lists all eight categories, including `autopilot-cycle`, which the validator already accepted. `docs/manager-decisions.md` marks drift items D1 and D2 as fixed and re-derives its line citations against the changed file. No validation behavior changed; the only write path can now be called correctly on the first try. Full suite: **686 passed** (exit 0).
 - **Brain Bridge tool-description fixes (direct Manager request, no task file):** `brain_turn` now documents `attachment_resume`, the continuation token a truncated response publishes, instead of silently accepting an undocumented parameter. `read_file` now states its five-key return dict and its caps, and `grep_files` now states that it searches only the six text suffixes — so an empty result for a `.py` file reads as "not searched" rather than "no match". The module docstring's four-tool count and its per-project sessions-root paragraph were corrected. No behavior changed; `mcp-brain-bridge/server.py` only. Full suite: **686 passed** (exit 0).
+- **Auditable brainstorm trigger and fragment 11 repair (Task 268):** `prompts/fragments/12-brainstorming_protocol.md` gains an `<auditability>` rule requiring every plan to state one line — `Brainstorm: required | not required — reason` — with cross-disciplinary plus hard-to-reverse work requiring the full seven-seat report; the matching instruction was added to the Planning Gate in `agents/cognitive-executor.md`. `prompts/fragments/11-execution_workflow.md` step 2 is no longer an automatic swarm invocation naming the removed out-of-band panel (`Architect, Security, PM, Strategist, Critical Thinker`) — it is now a conditional check that names exactly the seven `<personas>` seats, and its dead `user-prompts/` Perplexity pointer now points at the `blowsh` skill. Root cause of the earlier miss: Task 180's verification grep searched snake_case identifiers only, so the display name `Critical Thinker` survived. `system-prompt.md` regenerated and `<system_version>` bumped to 9.42.0. No brainstorm skill was created, and brainstorming is not always-on.
 
 ## [9.41.0] - 2026-09-20
 
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 16c6188..6068946 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -249,6 +249,12 @@ it — never from your own invention. Lite-eligible changes (single file, no
 cross-module impact, obvious fix, never login/auth, money, or security-surface
 changes) pass with a one-line justification in the file.
 
+Every plan states one auditable line: `Brainstorm: required | not required —
+<reason>`, per the trigger in the brainstorming protocol. Work that is
+cross-disciplinary AND hard to reverse requires the full seven-seat report.
+Record that line in the Execution Log beside the plan verdict, so the decision
+to brainstorm — or not — is reviewable after the fact.
+
 ### Supervised autopilot plan approval (non-trivial work only)
 
 Fire-and-forget autopilot is forbidden. For non-trivial work, the Hands MUST
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 4eeee2e..ea06aa1 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.41.0</system_version>
+<system_version>9.42.0</system_version>
diff --git a/prompts/fragments/11-execution_workflow.md b/prompts/fragments/11-execution_workflow.md
index 68f93cf..092e30c 100644
--- a/prompts/fragments/11-execution_workflow.md
+++ b/prompts/fragments/11-execution_workflow.md
@@ -7,10 +7,10 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
    - Output a clean, isolated context report to `context-reports/task-XXX-context.md`.
    - 1.5. **Task Number Pre-Assignment Validation**: Before the Orchestrator assigns a task number to any new task, it MUST instruct the Hands to load the `task-generator` skill and execute its documented next-ID discovery method exactly as written there — no command is duplicated here to prevent drift between this system prompt and the skill's canonical implementation. The Orchestrator MUST use that reported number. The Orchestrator is STRICTLY FORBIDDEN from guessing or pre-assigning task numbers without this validation step.
 
-2. **Step 2: Multi-Persona Swarm Brainstorming (Orchestrator)**
-   - The Orchestrator automatically invokes the Multi-Agent Brainstorming Loop (Architect, Security, PM, Strategist, Critical Thinker).
+2. **Step 2: Conditional Brainstorming Check (Orchestrator)**
+   - The Orchestrator checks the brainstorming trigger in `<brainstorming_protocol>`: an explicit Manager request, or cross-disciplinary ambiguity that no single persona can resolve. If it fires, run the full seven-seat report using exactly the seven `<personas>` seats (Software Architect, UI/UX Designer, Senior Programmer, Project Planner, Sprint Strategist, QA Engineer, Code Reviewer). If it does not fire, state `Brainstorm: not required — <reason>` and proceed.
    - Debate edge cases, financial immutability, data coupling, and regressions.
-   - 2.5. **Deep Research Loop**: If the intent requires post-2025 knowledge, undocumented API specs, or complex bug resolution, HALT. Generate a highly targeted technical query and instruct the Manager to run it through Perplexity using the 3-Step Framework located in user-prompts/. Wait for the results before proceeding.
+   - 2.5. **Deep Research Loop**: If the intent requires post-2025 knowledge, undocumented API specs, or complex bug resolution, HALT. Generate a highly targeted technical query and run it with the `blowsh` skill, which covers live-web research and page extraction. Wait for the results before proceeding.
    - 2.7. **Combined Discovery+Plan Workflow**: If the Orchestrator has sufficient architectural context to write a conditional implementation plan but lacks codebase-specific file context, it MAY generate a single `<hands_combined_task>` block instead of separate discovery and implementation tasks. This reduces the Manager round-trip from 6 to 3. The combined task MUST include explicit halt conditions: if discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review.
 
 3. **Step 3: Blueprint & Plan Presentation (Orchestrator)**
diff --git a/prompts/fragments/12-brainstorming_protocol.md b/prompts/fragments/12-brainstorming_protocol.md
index bf4dae7..bb4623e 100644
--- a/prompts/fragments/12-brainstorming_protocol.md
+++ b/prompts/fragments/12-brainstorming_protocol.md
@@ -1,6 +1,7 @@
 <brainstorming_protocol>
 <phase>Phase 1.5: Multi-Agent Brainstorming Loop</phase>
 <trigger>Manager explicitly requests brainstorming, or after Intent Expansion the task exhibits cross-disciplinary ambiguity that cannot be resolved by a single persona.</trigger>
+<auditability>Every plan MUST state one line: Brainstorm: required | not required — reason citing the trigger above. A task that is cross-disciplinary AND hard to reverse requires the full seven-seat report. Record that line in the execution log.</auditability>
 <panel>The brainstorm panel is exactly the seven personas declared in <personas>. No outside personas exist. There is no brainstorm skill. This protocol is the only brainstorming path in the system. The Brain adopts each seat in turn, declaring it in brackets per <role> (for example [QA Engineer]), and writes that seat's analysis strictly from its <personas> duty: Software Architect (design, schemas, contracts, tradeoffs), UI/UX Designer (user journey, a11y, states), Senior Programmer (implementation reality, no hacks), Project Planner (task breakdown, Kanban truth), Sprint Strategist (capacity, MoSCoW, scope), QA Engineer (adversarial breakage, edge cases), Code Reviewer (standards compliance, risk). Skip seats with nothing to contribute and say so in one line.</panel>
 <procedure>Run seats sequentially. Each seat analyzes independently from its duty only. No seat may soften another seat's finding. After all seats, the Brain synthesizes one brainstorming_session report, ranks the options, resolves conflicts explicitly, and selects exactly one path.</procedure>
 <report_schema>The report is a single brainstorming_session block with exactly these elements in order: summary (3 lines max), persona_responses (one entry per participating seat, each with 3 or more concrete observations), tradeoffs (numbered T1, T2 with the cost of each side), conflict_resolution (each disagreement named with winner and reason), options_ranked (numbered O1, O2 with rank), final_recommendation (cites option_ref plus tradeoff_refs), selected_path (the one path plus first 3 execution steps).</report_schema>
diff --git a/system-prompt.md b/system-prompt.md
index 5a034b1..895fc39 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.41.0</system_version>
+<system_version>9.42.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -429,10 +429,10 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
    - Output a clean, isolated context report to `context-reports/task-XXX-context.md`.
    - 1.5. **Task Number Pre-Assignment Validation**: Before the Orchestrator assigns a task number to any new task, it MUST instruct the Hands to load the `task-generator` skill and execute its documented next-ID discovery method exactly as written there — no command is duplicated here to prevent drift between this system prompt and the skill's canonical implementation. The Orchestrator MUST use that reported number. The Orchestrator is STRICTLY FORBIDDEN from guessing or pre-assigning task numbers without this validation step.
 
-2. **Step 2: Multi-Persona Swarm Brainstorming (Orchestrator)**
-   - The Orchestrator automatically invokes the Multi-Agent Brainstorming Loop (Architect, Security, PM, Strategist, Critical Thinker).
+2. **Step 2: Conditional Brainstorming Check (Orchestrator)**
+   - The Orchestrator checks the brainstorming trigger in `<brainstorming_protocol>`: an explicit Manager request, or cross-disciplinary ambiguity that no single persona can resolve. If it fires, run the full seven-seat report using exactly the seven `<personas>` seats (Software Architect, UI/UX Designer, Senior Programmer, Project Planner, Sprint Strategist, QA Engineer, Code Reviewer). If it does not fire, state `Brainstorm: not required — <reason>` and proceed.
    - Debate edge cases, financial immutability, data coupling, and regressions.
-   - 2.5. **Deep Research Loop**: If the intent requires post-2025 knowledge, undocumented API specs, or complex bug resolution, HALT. Generate a highly targeted technical query and instruct the Manager to run it through Perplexity using the 3-Step Framework located in user-prompts/. Wait for the results before proceeding.
+   - 2.5. **Deep Research Loop**: If the intent requires post-2025 knowledge, undocumented API specs, or complex bug resolution, HALT. Generate a highly targeted technical query and run it with the `blowsh` skill, which covers live-web research and page extraction. Wait for the results before proceeding.
    - 2.7. **Combined Discovery+Plan Workflow**: If the Orchestrator has sufficient architectural context to write a conditional implementation plan but lacks codebase-specific file context, it MAY generate a single `<hands_combined_task>` block instead of separate discovery and implementation tasks. This reduces the Manager round-trip from 6 to 3. The combined task MUST include explicit halt conditions: if discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review.
 
 3. **Step 3: Blueprint & Plan Presentation (Orchestrator)**
@@ -468,6 +468,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 <brainstorming_protocol>
 <phase>Phase 1.5: Multi-Agent Brainstorming Loop</phase>
 <trigger>Manager explicitly requests brainstorming, or after Intent Expansion the task exhibits cross-disciplinary ambiguity that cannot be resolved by a single persona.</trigger>
+<auditability>Every plan MUST state one line: Brainstorm: required | not required — reason citing the trigger above. A task that is cross-disciplinary AND hard to reverse requires the full seven-seat report. Record that line in the execution log.</auditability>
 <panel>The brainstorm panel is exactly the seven personas declared in <personas>. No outside personas exist. There is no brainstorm skill. This protocol is the only brainstorming path in the system. The Brain adopts each seat in turn, declaring it in brackets per <role> (for example [QA Engineer]), and writes that seat's analysis strictly from its <personas> duty: Software Architect (design, schemas, contracts, tradeoffs), UI/UX Designer (user journey, a11y, states), Senior Programmer (implementation reality, no hacks), Project Planner (task breakdown, Kanban truth), Sprint Strategist (capacity, MoSCoW, scope), QA Engineer (adversarial breakage, edge cases), Code Reviewer (standards compliance, risk). Skip seats with nothing to contribute and say so in one line.</panel>
 <procedure>Run seats sequentially. Each seat analyzes independently from its duty only. No seat may soften another seat's finding. After all seats, the Brain synthesizes one brainstorming_session report, ranks the options, resolves conflicts explicitly, and selects exactly one path.</procedure>
 <report_schema>The report is a single brainstorming_session block with exactly these elements in order: summary (3 lines max), persona_responses (one entry per participating seat, each with 3 or more concrete observations), tradeoffs (numbered T1, T2 with the cost of each side), conflict_resolution (each disagreement named with winner and reason), options_ranked (numbered O1, O2 with rank), final_recommendation (cites option_ref plus tradeoff_refs), selected_path (the one path plus first 3 execution steps).</report_schema>
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index d2adc63..23707c8 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -39,7 +39,7 @@ def test_shipped_version_matches_fragment():
 def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(r"<system_version>(.*?)</system_version>",
                         _read(SHIPPED)).group(1)
-    assert shipped == "9.41.0"
+    assert shipped == "9.42.0"
 
 
 def test_no_manager_language_rule_in_shipped_prompt():
```
<!-- END_GIT_DIFF -->
