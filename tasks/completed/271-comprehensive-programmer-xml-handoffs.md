# Task 271: Generate Comprehensive Programmer XML Handoffs

**File:** `tasks/qa/271-comprehensive-programmer-xml-handoffs.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Source Context

## Goal

Make the Senior Programmer seat generate complete, executable `<hands_implementation_task>` XML handoffs that preserve exact code, repository-specific instructions, verification commands, acceptance criteria, and edge cases without placeholder collapse.

## Manager's Notes

The Programmer currently emits generic placeholders and omits code samples or exact instructions. Improve the task-generation contract and its tests. External agent-handoff guidance supports explicit context, state, contracts, and observable acceptance criteria. Execute the approved improvement through the Brain in locked autopilot and reuse manager decisions directly.

## Local TODOs

- [ ] Obtain a Brain-approved implementation plan under the same task history
- [ ] Replace the generic implementation template with an exact, comprehensive XML contract
- [ ] Require complete code samples and repository-specific instructions in generated handoffs
- [ ] Add regression coverage for completeness, exactness, and absence of placeholder collapse
- [ ] Run targeted tests, prompt synchronization checks, task lint, and Markdown lint
- [ ] Update verification evidence and execution reasoning
- [ ] Update `CHANGELOG.md`
- [ ] Stage the factual diff and transition the task to QA

## Acceptance Criteria

- [x] The Senior Programmer contract requires a complete `<hands_implementation_task>` payload with exact file paths, code samples, instructions, acceptance criteria, verification commands, and edge cases
- [x] The generated handoff contract forbids placeholder-only instructions, omitted code, vague file references, and contradictory guidance
- [x] Regression tests prove that comprehensive XML content and concrete code samples survive task generation
- [x] The generated system prompt remains synchronized with its source fragments
- [x] Targeted tests, task lint, and Markdown lint pass with exit code 0
- [x] `CHANGELOG.md` records the structural prompt change

## Verification Evidence

- **Test command:** rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml pytest tests/test_prompt_sync.py tests/test_brain_bridge.py tests/test_golden_cases.py -q
- **Expected result:** All targeted tests pass with exit code 0
- **Actual result:** 268 passed in 1.59s (3 new regression gates green; assembler round-trip gate confirms shipped prompt matches fragments)
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; a raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true:

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence`; do not defer box-checking to a closure task.

## Risk & Rollback

- **Risk:** A stricter template may inflate routine handoffs or conflict with existing golden snapshots.
- **Rollback plan:** Revert only the prompt/template and regression-test changes, regenerate the system prompt, and rerun the targeted suite before restoring the previous handoff format.

---

## Execution Log & Reasoning

- Initial investigation identified the root cause in the generic Senior Programmer implementation template and its explicit instruction to omit full code blocks.
- External research favored explicit handoff context, state, contracts, and observable acceptance criteria.
- Brain plan verdict (planning-gate `brain_turn`, same task history): replace the code-block ban with an exact comprehensive-handoff contract in the implementation template, add regression tests, regenerate the prompt, bump the version pin, verify, update the changelog, stage, and move to QA. Seat routing: Software Architect owns the contract, Senior Programmer owns checklists and verification; Designer skipped (no interface change). Brainstorm: not required — single-domain, reversible prompt fix. Manager replied "Approved".
- Implementation: replaced the `ORCHESTRATOR AUTHORING RULE` in `prompts/fragments/09-hands_protocols.md` with a comprehensive executable-handoff contract (exact paths, complete code samples or unified diffs, full commands, named skills with reasons, per-step verification, explicit acceptance criteria and edge cases, placeholder ban); bumped `<system_version>` to 9.46.0; regenerated `system-prompt.md`; updated the version pin and added regression gates in `tests/test_prompt_sync.py`.
- Verification: targeted `rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml pytest tests/test_prompt_sync.py tests/test_brain_bridge.py tests/test_golden_cases.py -q` → 268 passed, exit 0; full suite → 689 passed, 10 warnings, exit 0; `check_docs_sync.py` → docs-sync OK; `lint_task_file`, `lint_markdown CHANGELOG.md`, `lint_system_prompt_sync` all pass.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 4a194aa..0778a6f 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -14,6 +14,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Auditable brainstorm trigger and fragment 11 repair (Task 268):** `prompts/fragments/12-brainstorming_protocol.md` gains an `<auditability>` rule requiring every plan to state one line — `Brainstorm: required | not required — reason` — with cross-disciplinary plus hard-to-reverse work requiring the full seven-seat report; the matching instruction was added to the Planning Gate in `agents/cognitive-executor.md`. `prompts/fragments/11-execution_workflow.md` step 2 is no longer an automatic swarm invocation naming the removed out-of-band panel (`Architect, Security, PM, Strategist, Critical Thinker`) — it is now a conditional check that names exactly the seven `<personas>` seats, and its dead `user-prompts/` Perplexity pointer now points at the `blowsh` skill. Root cause of the earlier miss: Task 180's verification grep searched snake_case identifiers only, so the display name `Critical Thinker` survived. `system-prompt.md` regenerated and `<system_version>` bumped to 9.42.0. No brainstorm skill was created, and brainstorming is not always-on.
 - **Human-readable output style contract (Task 269):** the Manager reported that Manager-facing output reads machine-like rather than human. A four-track deep search — OpenAI Model Spec and the GPT-5.1 guide, Anthropic prompt-engineering and Claude Code output styles, Google Gemini guidance, the published ChatGPT/Claude/Cursor/Copilot/Perplexity/Manus prompts, and readability research from Nielsen Norman Group, GOV.UK, Google and Microsoft style — found that our style contract was prohibitions only, with no positive model of good prose. `prompts/fragments/13-constraints.md` now carries a positive **Manager-Facing Output Style** contract: answer first, an explicit length budget (short 2–5 sentences with no heading; normal 80–180 words or at most 5 bullets), flowing prose with 25 words as a ceiling rather than a target, a structure rule (prose for 1–2 items, flat bullets for 3–7, table only for repeated attributes, never nested), a clean open and close with no preamble and no recap, direct address with a plain word for each specialist term on first use, and pipeline mechanics kept out of the answer body. The **Tone and Demeanor** rule now targets a knowledgeable colleague instead of an impersonal analyst, and **Communication Patterns** grew from five banned phrases to a principle-based tell list covering hedging openers, significance inflation, negative parallelism, rote triples, collaborative preambles and trailing recaps. `prompts/fragments/02-role.md` requires the answer immediately after the persona bracket, `prompts/fragments/20-communication_examples.md` adds good-versus-bad prose pairs, and `agents/cognitive-executor.md` mirrors the contract. No behavior, tool, reasoning-log or XML change, and every evidence and verdict rule is untouched. `system-prompt.md` regenerated and `<system_version>` bumped to 9.43.0. Conflict C1 (the stored English-only rule versus answering in the user's language) was raised for a Manager decision, not auto-resolved.
 - **Stack skill strict tooling gates and the stacks/ folder decision (Task 270):** every stack skill was missing a machine-enforced lint, type-check, format, and static-analysis gate — the framework's only enforced gate checked task-file structure. Thirteen subagents researched the newest strict tooling per stack against live 2026 sources and each skill now carries a uniform **Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)** section with the same five-part shape: required toolchain table with pinned minimum versions, strict baseline config filenames and exact flags, mandatory gate order (format → lint → typecheck → static analysis → security → test → build), stack-specific hallucination traps and the evidence to record. The `stacks/` folder (five YAML profiles) had no live runtime consumer after the `loop-engine` daemon was deleted in Task 167 — its only references were one test assertion and one doc pointer — so it was removed per the Manager's rule, after carrying its toolchain commands into the skills. `prompts/fragments/09-hands_protocols.md` and `skill-templates/verification-before-completion/SKILL.md` now require the active stack skill's gate to run before any completion claim, and the registry in `prompts/fragments/07-agent_skills_registry.md` marks each stack blueprint as gate-included. `system-prompt.md` regenerated and `<system_version>` bumped to 9.45.0 (9.44.0 intermediate; QA hotfix unified the JS Node floor to 24.20.0, made the Spring actuator gate start the app before curling readiness, recorded the jsx-a11y override owner plus expiry, defined the four-field skip-record schema with the highest-Node-floor rule, and verified the Gradle 9.7.1 SHA `acd53f1e` via curl).
+- **Comprehensive Programmer XML handoffs (Task 271):** the Senior Programmer seat emitted generic placeholder-heavy `<hands_implementation_task>` XML and explicitly forbade full code blocks, contradicting its own comprehensive-handoff mandate. `prompts/fragments/09-hands_protocols.md` now carries a comprehensive executable-handoff contract: every step names the exact file path and operation, every file change ships the complete code sample or unified diff, every command is written in full with flags and working directory, every skill is named with its reason, every step states its verification command and expected result, and acceptance criteria plus edge cases are explicit — with a PLACEHOLDER BAN (no `[bracketed placeholder]` survives; halt and ask instead of emitting one). `system-prompt.md` regenerated and `<system_version>` bumped to 9.46.0. `tests/test_prompt_sync.py` gains three regression gates (complete-code-sample contract present, placeholder-only instructions forbidden, code-block ban absent) and the version pin moves to 9.46.0. Targeted suites: **268 passed** (exit 0).
 
 ## [9.41.0] - 2026-09-20
 
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 36c8f9b..f208856 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.45.0</system_version>
+<system_version>9.46.0</system_version>
diff --git a/prompts/fragments/09-hands_protocols.md b/prompts/fragments/09-hands_protocols.md
index 6d8df83..d6fbf02 100644
--- a/prompts/fragments/09-hands_protocols.md
+++ b/prompts/fragments/09-hands_protocols.md
@@ -50,7 +50,7 @@
   <execution_phase>
     HANDS INSTRUCTION: Implement the following logic step-by-step.
 
-    **ORCHESTRATOR AUTHORING RULE (machine-complete XML):** Write every checklist step so a smart machine executes it with zero questions back to the Manager. Name the exact file path and the exact operation in each step. Pre-make every decision the approved plan already contains. Leave no step ambiguous. Do NOT paste full code blocks for the Hands to copy — it is intelligent, so give precise machine directives instead. The Hands may question the Manager ONLY for information that exists nowhere in the plan or repo — never for a decision the Brain already made.
+    **ORCHESTRATOR AUTHORING RULE (comprehensive, executable XML):** Every `<hands_implementation_task>` MUST be a complete executable handoff. Each checklist step names the exact file path and the exact operation. Every file change carries the complete code sample or unified diff the Hands must apply — placeholder-only instructions, vague file references, and omitted code are forbidden. Every command is written out in full with exact flags and working directory. Every skill is named with one line saying why the Hands need it for this step. Every step states its verification command and expected result, and acceptance criteria plus edge cases are explicit. Pre-make every decision the approved plan already contains and leave no step ambiguous. **PLACEHOLDER BAN:** No `[bracketed placeholder]` may survive in the emitted XML — every skill name, file path, command, and step MUST be filled with concrete values from the approved plan. If a value is genuinely unknown, halt and ask instead of emitting a placeholder. The Hands may question the Manager ONLY for information that exists nowhere in the plan or repo — never for a decision the Brain already made.
 
     **MICRO-TASK CHECKLIST:**
     You MUST execute these steps in exact order. After completing EACH step, you MUST physically change `- [ ]` to `- [x]` in the active task file, then notify the user of your progress before moving to the next step.
diff --git a/system-prompt.md b/system-prompt.md
index e63f0db..4555e43 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.45.0</system_version>
+<system_version>9.46.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -277,7 +277,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
   <execution_phase>
     HANDS INSTRUCTION: Implement the following logic step-by-step.
 
-    **ORCHESTRATOR AUTHORING RULE (machine-complete XML):** Write every checklist step so a smart machine executes it with zero questions back to the Manager. Name the exact file path and the exact operation in each step. Pre-make every decision the approved plan already contains. Leave no step ambiguous. Do NOT paste full code blocks for the Hands to copy — it is intelligent, so give precise machine directives instead. The Hands may question the Manager ONLY for information that exists nowhere in the plan or repo — never for a decision the Brain already made.
+    **ORCHESTRATOR AUTHORING RULE (comprehensive, executable XML):** Every `<hands_implementation_task>` MUST be a complete executable handoff. Each checklist step names the exact file path and the exact operation. Every file change carries the complete code sample or unified diff the Hands must apply — placeholder-only instructions, vague file references, and omitted code are forbidden. Every command is written out in full with exact flags and working directory. Every skill is named with one line saying why the Hands need it for this step. Every step states its verification command and expected result, and acceptance criteria plus edge cases are explicit. Pre-make every decision the approved plan already contains and leave no step ambiguous. **PLACEHOLDER BAN:** No `[bracketed placeholder]` may survive in the emitted XML — every skill name, file path, command, and step MUST be filled with concrete values from the approved plan. If a value is genuinely unknown, halt and ask instead of emitting a placeholder. The Hands may question the Manager ONLY for information that exists nowhere in the plan or repo — never for a decision the Brain already made.
 
     **MICRO-TASK CHECKLIST:**
     You MUST execute these steps in exact order. After completing EACH step, you MUST physically change `- [ ]` to `- [x]` in the active task file, then notify the user of your progress before moving to the next step.
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index d1517fd..12c07fc 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -39,7 +39,7 @@ def test_shipped_version_matches_fragment():
 def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(r"<system_version>(.*?)</system_version>",
                         _read(SHIPPED)).group(1)
-    assert shipped == "9.45.0"
+    assert shipped == "9.46.0"
 
 
 def test_no_manager_language_rule_in_shipped_prompt():
@@ -74,3 +74,20 @@ def test_executor_evidence_records_rtk_command():
 def test_task_generator_template_prescribes_rtk():
     text = _read(TASKGEN_SKILL)
     assert "rtk test [exact command]" in text
+
+
+def test_handoff_contract_requires_complete_code_samples():
+    text = _read(SHIPPED)
+    assert "complete code sample or unified diff" in text
+    assert "PLACEHOLDER BAN" in text
+
+
+def test_handoff_contract_forbids_placeholder_only_instructions():
+    text = _read(SHIPPED)
+    assert "placeholder-only instructions" in text
+    assert "omitted code are forbidden" in text
+
+
+def test_code_block_ban_removed_from_shipped_prompt():
+    text = _read(SHIPPED)
+    assert "Do NOT paste full code blocks for the Hands to copy" not in text
```
<!-- END_GIT_DIFF -->
