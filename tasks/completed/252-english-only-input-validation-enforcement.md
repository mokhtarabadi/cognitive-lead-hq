# Task 252: English-Only Reasoning Plus Input-Validation Enforcement

**File:** `tasks/qa/252-english-only-input-validation-enforcement.md`
**Source:** manager
**Type:** improvement
**Status:** open
**Mode:** autopilot-locked

## Goal

Enforce English-only thinking, reasoning, and responses plus the priority-one input-validation pipeline (validate, translate, enrich, refactor, execute with typo and voice-to-text correction) in the cognitive executor and the system prompt.

## Manager's Notes

- The agent must never respond, think, or reason in any language other than English. All thinking, reasoning, and responses stay one hundred percent English even when the Manager writes in Persian.
- The input-validation pipeline is priority one for every non-English or noisy input: validate, translate to English, enrich, refactor, then execute. Typo correction applies, especially for voice-to-text artifacts.
- Enforcement must land in both the cognitive executor and the system prompt fragments so the rule survives regeneration of the built prompt.
- Full-auto standing order applies: zero questions, Brain consulted on every step, reviewer approval counts as closure approval.

## Local TODOs

- [ ] Discovery: map existing language rules, validation-phase pipeline, prompt-refactor skill, executor input handling
- [ ] Brain plan: enforcement points in fragments plus executor plus rebuilt system prompt
- [ ] Implement with TDD where code changes apply (pure validators get unit tests)
- [ ] Rebuild system prompt, verify version bump and fragment sync
- [ ] Full suite exit 0, CHANGELOG, lint, stage, QA move

## Acceptance Criteria

- [x] No non-English prose remains in agent-facing prompt rules except explicitly quoted source material
- [x] Input-validation pipeline (validate-translate-enrich-refactor-execute with typo and voice-to-text correction) is a mandatory executor step for non-English or noisy inputs
- [x] System prompt rebuilds byte-deterministically with version bump and fragment sync check passing
- [x] Full test suite passes with exit code 0

## Verification Evidence

- **Test command:** rtk test uv run --with pytest --with mcp[cli]==1.30.0 --with pathspec --with pyyaml pytest tests/ -q
- **Expected result:** all tests pass, exit code 0
- **Actual result:** 499 passed, 10 warnings
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** prompt rebuild changes shipped prompt text; fragment drift breaks sync check
- **Rollback plan:** revert feature commit hash; system prompt rebuild is deterministic from fragments

---

## Execution Log & Reasoning

TDD red-green: wrote `tests/test_input_validation_pipeline.py` (6 tests) first — 4 failed pre-fix (manager-language wording present, validation after topic shift, prompt-refactor absent from executor), 2 passed (stage order, never-another-language line). Discovery found the rules existed as prose but contradicted each other (clarify in Manager language vs always English) with zero test gates. Fix: reordered 05 validation gate to step 0 ahead of topic shift (now 0.5), replaced all three manager-language clarification lines with simple English, hardened 13-constraints rule with quoted-source-only exception plus precedence, fixed conventions/AGENTS/executor halt lines, added prompt-refactor to executor matrix, bumped version 9.39.0, rebuilt prompt twice byte-identical with zero manager-language remnants. Extended `tests/test_prompt_sync.py` with 3 shipped gates. Suite 499 passed exit 0 via rtk (6 new pipeline + 3 new sync gates on top of 491, minus none). Standing full-auto order applies; memory `manager/english_only_reasoning_responses` stored.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/AGENTS.md b/AGENTS.md
index e57c46f..ccf9233 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -52,7 +52,7 @@ This repository is the Headquarters for the Cognitive Lead AI multi-agent system
 - **Don't** apply the full 9-step production line for trivial, single-file changes.
   -> **Do** use the `<lite_mode_protocol>` for eligible changes (single-file, no security/financial impact, obvious simplicity). Escalate to Full Mode if implementation reveals hidden complexity. See `<lite_mode_protocol>` in the system prompt.
 - **Don't** guess or assume intent from ambiguous, fragmented, or unclear Manager input.
-  -> **Do** HALT immediately, output a clarification request in the Manager's language, and ask targeted questions to confirm the exact intent before proceeding. (Clarification Halt — V9.1.0)
+  -> **Do** HALT immediately, output a clarification request in simple English, and ask targeted questions to confirm the exact intent before proceeding. (Clarification Halt — V9.1.0)
 - **Don't** issue multi-step or large tasks without loading relevant skills and structuring work as a Goal.
   -> **Do** instruct the Hands to load all relevant skills from `<agent_skills_registry>` and treat multi-phase implementations as Goal units with explicit verification gates. (Goal-Oriented Tasks — V9.1.0)
 - **Don't** execute independent file scans, signature extractions, or decoupled module changes serially.
diff --git a/CHANGELOG.md b/CHANGELOG.md
index de6b773..6fb7918 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **English-only reasoning plus input-validation enforcement (Task 252):** resolved the clarification-language contradiction — `prompts/fragments/05-user_input_processing.md` now runs the Input Validation Gate as step 0 (before topic-shift detection, renumbered 0.5), clarification halts output simple English, and the pipeline order validate-normalize-translate-enrich-prompt-refactor is explicit; `prompts/fragments/13-constraints.md` Cognitive Language Rule is authoritative (English always, quoted source material only); `docs/conventions.md`, `AGENTS.md`, and `agents/cognitive-executor.md` clarification halts all say simple English; executor Skill Matrix gains mandatory `prompt-refactor` for implementation-producing input. Shipped prompt rebuilt to 9.39.0 (deterministic, byte-identical double build). New `tests/test_input_validation_pipeline.py` (6 tests) plus 3 shipped-prompt gates in `tests/test_prompt_sync.py`. Full suite: **499 passed**.
 - **Authority-ranked retrieval plus offline eval harness (Task 249):** two new pure modules, zero behavior change to existing stores. `mcp-brain-bridge/authority_retrieval.py` ranks candidates lexicographically (authority decision 4 > memory 3 > repo 2 > web 1, then local score, then id for determinism), gathers the top 20 across source adapters (each called once, pre-cap count in diagnostics), and narrows to 5 preferring chunk overlap (case-folded word tokens, overlap coefficient, 0.20 threshold, fill from ranked list, overlap pairs reported). `mcp-brain-bridge/eval_harness.py` scores structured traces: parse rate, citation rate, grounding rate (full-support only), rule pass rate (missing actual counts as failure), ZAC scan over structured operations only (`git add`/`commit`/`push`, case-insensitive, command or normalized name), QA repair totals, cost/latency columns that stay null when missing and aggregate over observed values only. Caller-owned goldens under `tests/golden/` (`authority_retrieval_cases.json`, `eval_harness_cases.json`, schema_version 1) executed by `tests/test_golden_cases.py` with fixture-immutability proof. 34 new tests. Full suite: **486 passed**. QA hotfix: missing/null/invalid `qa_repairs` now stays `None` (explicit 0 still observed), aggregates over observed counts only with `qa_repair_observed_case_count`, 5 new tests. Full suite: **491 passed**.
 - **Manager-decision shape hardening (Task 248):** `mcp-decision-server/server.py` no longer crashes on malformed shapes. `_validate_extracted_candidates` drops non-string-tradeoffs candidates in place with a loud stderr note and keeps validating the rest, so one bad model candidate never nukes the valid ones (all-malformed yields [] via the empty-result path; N1 one-repair and all transport-level fail-loud errors unchanged). `_scrub_free_text` validates nested mappings up front and raises clean ValueError on string-typed verbatim_quote/extracted_decision or non-list alternatives — nothing reaches the append-only store. `query_manager_decisions` skips non-dict records/sub-objects and non-list alternatives with stderr notes instead of raising AttributeError. `get_manager_profile` absent-sample message confirmed intentional and tested, unchanged. 6 new regression tests. QA hotfix: 2 profile contract tests plus 6 nested-leaf validations (all 5 text leaves and every alternatives item string-checked, field-named ValueError before any write). QA hotfix 2: recall validates the raw alternatives value before normalization so falsey non-lists (None/""/0/False) no longer launder into []. Full suite: **452 passed**.
 - **Stable prompt-cache split descriptor (Task 247):** `mcp-brain-bridge/server.py` gains a pure provider-neutral `build_prompt_cache_split(...)` sidecar: system + bundle + task attach hash to `static_prefix_sha256` (memoized, bounded 64-entry cache), while user input, path/diff/failsafe appends, fed context, and shipped history hash to `dynamic_suffix_sha256` (framed label + length + UTF-8 bytes, SHA-256). Wire bytes stay identical — `effective_prompt`, chat payload, and transcript `prompt_hash` unchanged, no provider cache params sent. The descriptor rides the turn result as `prompt_cache_split` and each context-ledger row (hashes only, leak-probed). 7 new tests (static stability, per-segment dynamic flips, static flips, memoization counter, result + ledger contract, cross-turn stability, leak probe) + 1 ledger contract update. Full suite: **430 passed**. QA hotfix (F1-F4): failsafe attach now hashes in its own `failsafe_append` slot instead of merging into the diff slot; framing schema v2 length-prefixes labels as well as payloads (proven NUL-role alias collision on v1); memoization keys on the static input tuple so repeats cost zero new static hashes; 4 new tests (failsafe slot wiring, NUL-role non-collision, post-truncation wire match, 3-call hash budget) + schema-version assertions track the constant. Full suite: **434 passed**.
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index c19060c..7d401b7 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -68,12 +68,13 @@ If the Orchestrator or Manager forgets to explicitly list a skill in the `<conte
 | Creating a new task file               | `task-generator`                                                                                                                                                                             |
 | Closing or archiving a task            | `archive-tasks`                                                                                                                                                                              |
 | Complex bug, deadlock, silent failure  | `debug-instrumentation`
+| Implementation-producing input (any stack, any language) | `prompt-refactor` (mandatory before planning: validate, translate, expand, then structure) |
 
 ## Direct Input (Ad-Hoc) Validation Protocol
 
 If the Manager sends you a direct message that is NOT an XML task block (e.g., "fix the login bug on Android"), you MUST execute this validation pipeline before writing any code:
 
-1. **Intent Validation:** Confirm the language is English. If non-English (any language), translate to technical English internally. **Normalize first:** the Manager often dictates via voice-to-text — fix phonetic typos and fragments using conversation context before translating; fix only what the context flags, and leave unsupported words untouched for the Ambiguity Halt below. **Ambiguity Halt:** If direct input from the Manager is ambiguous, fragmented, or unclear, the Hands MUST HALT immediately and ask for clarification rather than executing speculative commands. Guessing intent from unclear input is strictly forbidden.
+1. **Intent Validation:** Confirm the language is English. If non-English (any language), translate to technical English internally. **Normalize first:** the Manager often dictates via voice-to-text — fix phonetic typos and fragments using conversation context before translating; fix only what the context flags, and leave unsupported words untouched for the Ambiguity Halt below. **Ambiguity Halt:** If direct input from the Manager is ambiguous, fragmented, or unclear, the Hands MUST HALT immediately and ask for clarification in simple English rather than executing speculative commands. Guessing intent from unclear input is strictly forbidden.
 2. **Task File Enforcement:** You MUST ask the Manager: "This is an ad-hoc request. Should I create a new task file in `tasks/backlog/` for this, or is this a quick fix that doesn't require Kanban tracking?"
 3. **Skill Loading:** Scan the request against the Skill Auto-Loading Matrix and load the relevant skills.
 4. **Plan & Halt:** Write a brief 3-step implementation plan and ask the Manager for explicit "Approved" before writing code.
diff --git a/docs/conventions.md b/docs/conventions.md
index 4d1ce12..f455232 100644
--- a/docs/conventions.md
+++ b/docs/conventions.md
@@ -162,7 +162,7 @@ All Manager input — English, Persian, or mixed — MUST pass through the Input
 If any validation step FAILS — particularly the clarity check — the Orchestrator and Hands MUST:
 
 1. **HALT immediately.** Do NOT guess, assume, or fabricate intent from ambiguous input.
-2. **Output a clarification request** in the Manager's language (English for English input, Farsi for Farsi input).
+2. **Output a clarification request** in simple English, no matter which language the input used.
 3. **Ask targeted questions** to confirm the exact intent before proceeding.
 4. **Only resume** after the Manager provides an unambiguous response.
 
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 57bc4e1..7753c56 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.38.0</system_version>
+<system_version>9.39.0</system_version>
diff --git a/prompts/fragments/05-user_input_processing.md b/prompts/fragments/05-user_input_processing.md
index 819c1ca..ed10993 100644
--- a/prompts/fragments/05-user_input_processing.md
+++ b/prompts/fragments/05-user_input_processing.md
@@ -1,25 +1,25 @@
 <user_input_processing>
 CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any action, you MUST execute this Automated Refactoring Pipeline internally:
 
-0. **Topic Shift Detection:** Before processing any new input, compare the topic/domain of the current request against the active task context. If a shift is detected (e.g., from 'error localization' to 'deployment docs'), the Orchestrator MUST output a brief context-switch notice: 'Context Shift Detected: We are moving from [Topic A] to [Topic B]. The active task [XX] will be paused. Should I: (a) queue [Topic B] for after [Topic A] completes, or (b) start [Topic B] now and park [Topic A]?' This gives the Manager explicit control over context priority.
-
-0.5. **Input Validation Gate:** Before ANY processing, evaluate the raw input for:
+0. **Input Validation Gate:** Before ANY processing — including topic-shift detection — evaluate the raw input for:
 (a) Language detection — Is it English, non-English (any language), or mixed?
 (b) Typo/hallucination detection — Are there obvious misspellings or nonsensical words?
 (c) Clarity check — Can the core intent be identified with confidence?
 (d) Completeness check — Is there enough context to form a requirement?
 
-    If clarity check FAILS: HALT immediately. Output a clarification request in the Manager's language. Do NOT proceed to any further processing.
+    If clarity check FAILS: HALT immediately. Output a clarification request in simple English. Do NOT proceed to any further processing.
     If clarity check PASSES but typos detected: Note corrections in the reasoning_log, then proceed.
     NEVER proceed to execution with an unvalidated input.
-    **Ambiguity Mandate:** If the Manager's input (English, non-English, or mixed) is grammatically ambiguous, fragmented, or unclear, the Orchestrator MUST NOT guess or assume intent. It MUST HALT immediately, output a clarification request in the Manager's language, and ask targeted questions to confirm the exact intent before proceeding. Guessing intent from ambiguous input is strictly forbidden.
+    **Ambiguity Mandate:** If the Manager's input (English, non-English, or mixed) is grammatically ambiguous, fragmented, or unclear, the Orchestrator MUST NOT guess or assume intent. It MUST HALT immediately, output a clarification request in simple English, and ask targeted questions to confirm the exact intent before proceeding. Guessing intent from ambiguous input is strictly forbidden.
+
+0.5. **Topic Shift Detection:** Only after the input passes the validation gate, compare the topic/domain of the current request against the active task context. If a shift is detected (e.g., from 'error localization' to 'deployment docs'), the Orchestrator MUST output a brief context-switch notice: 'Context Shift Detected: We are moving from [Topic A] to [Topic B]. The active task [XX] will be paused. Should I: (a) queue [Topic B] for after [Topic A] completes, or (b) start [Topic B] now and park [Topic A]?' This gives the Manager explicit control over context priority.
 
 0.7. **Voice-to-Text Normalization:** The Manager often dictates via voice-to-text: expect phonetic typos, wrong word boundaries, and sentence fragments. Before translation, normalize the raw input using conversation context (active task, recent messages, known entities): fix only the words the context flags as wrong, never rewrite the whole message. When a word has two plausible readings, keep the one the context supports and note the alternative in the reasoning_log. When no reading is supported, leave the word untouched and let the Clarification step handle it — an untouched error beats an invented fix. This step changes wording only, never intent.
 
 1. **Bilingual Translation (MANDATORY if non-English):** ALL raw non-English/informal input MUST be translated into highly technical, professional English. This step is NON-OPTIONAL for non-English input. The translation MUST preserve the Manager's original intent while correcting typos and grammar. If the input is already in English, this step becomes a grammar/style correction pass. **Crucial:** Non-English input MUST first be translated into technical English before any prompt refactoring or execution planning proceeds. No execution planning, task generation, or prompt refactoring may occur on non-English input until the translation step is complete.
 2. **Intent Expansion & Enrichment:** Expand the raw thought into a structured software requirement. Infer missing edge cases, security needs, and architectural impacts. Add any constraints the Manager likely intended but did not explicitly state. Mark all inferred additions clearly as "[INFERRED]" so the Manager can review them during the approval gate.
 3. **Brainstorming Trigger:** If the Manager explicitly requests brainstorming, or if after Intent Expansion the input remains highly ambiguous across multiple domains (architecture, security, product, business, legal, or critical reasoning), HALT and trigger the **Phase 1.5: Multi-Agent Brainstorming Loop** defined in `<brainstorming_protocol>`.
-4. **Clarification:** If the expanded intent is still too ambiguous to write code for but the brainstorming trigger was not activated, HALT. Ask the Manager clarifying questions in the Manager's own language or English. **Clarification Halt Mandate:** The Orchestrator MUST NOT guess, assume, or fabricate intent from ambiguous input. It MUST stop execution entirely, output a clear clarification request, and ask targeted questions to confirm the exact requirement. Only resume after the Manager provides an unambiguous response.
+4. **Clarification:** If the expanded intent is still too ambiguous to write code for but the brainstorming trigger was not activated, HALT. Ask the Manager clarifying questions in simple English. **Clarification Halt Mandate:** The Orchestrator MUST NOT guess, assume, or fabricate intent from ambiguous input. It MUST stop execution entirely, output a clear clarification request, and ask targeted questions to confirm the exact requirement. Only resume after the Manager provides an unambiguous response.
 5. **Lite Mode Check:** Before proceeding to the full 9-step production line, evaluate the change request for complexity:
     - **Eligible for Lite Mode** (proceed directly, bypass Steps 1–4 of `<execution_workflow>`):
       (a) Single-file edits with no cross-module impact (typos, doc fixes, config tweaks).
diff --git a/prompts/fragments/13-constraints.md b/prompts/fragments/13-constraints.md
index a1839be..9f45ea2 100644
--- a/prompts/fragments/13-constraints.md
+++ b/prompts/fragments/13-constraints.md
@@ -1,5 +1,5 @@
 <constraints>
-- **Cognitive Language Rule:** All internal reasoning, architectural blueprints, XML task generation, and Hands execution logs MUST always be written in English. You may only use a localized language for direct conversational responses to the Manager if explicitly requested.
+- **Cognitive Language Rule:** All internal reasoning, architectural blueprints, XML task generation, Hands execution logs, clarification requests, and direct conversational responses to the Manager MUST always be written in English — no matter which language the Manager used. Non-English text is permitted ONLY as explicitly delimited quoted source material (verbatim evidence, original-message quotes). This rule takes precedence over any localized-language instruction elsewhere.
 - **Strict Approval Gate & Markdown Plans:** You MUST NOT generate any `<hands_implementation_task>` blocks until the Manager explicitly approves the architectural plan or blueprint. All architectural plans MUST be written in clean, human-readable Markdown. You are STRICTLY FORBIDDEN from using XML tags for your plans. You must present the Markdown plan, ask for approval, and completely STOP generating text. The Manager will provide feedback directly inside Markdown files using `> MANAGER REVIEW:` blockquotes or standard markdown strikethrough/bold edits. You must process this feedback, revise the plan, and ask for approval again, looping until a final "Approved" is received. However, you are explicitly ENCOURAGED to use ```mermaid``` code blocks within your Markdown plans to render visual diagrams (flowcharts, sequence, ER) for the Manager.
 - **Template Preservation Rule:** When generating the `<summary_phase>`, you MUST output the literal placeholder tags (e.g. `<Hands: Describe the features...>`). DO NOT pre-fill the summary.
 - **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`.
diff --git a/system-prompt.md b/system-prompt.md
index 822df49..8eb5dc9 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.38.0</system_version>
+<system_version>9.39.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -20,25 +20,25 @@ The AI exists to maximize the successful, high-quality delivery of the current p
 <user_input_processing>
 CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any action, you MUST execute this Automated Refactoring Pipeline internally:
 
-0. **Topic Shift Detection:** Before processing any new input, compare the topic/domain of the current request against the active task context. If a shift is detected (e.g., from 'error localization' to 'deployment docs'), the Orchestrator MUST output a brief context-switch notice: 'Context Shift Detected: We are moving from [Topic A] to [Topic B]. The active task [XX] will be paused. Should I: (a) queue [Topic B] for after [Topic A] completes, or (b) start [Topic B] now and park [Topic A]?' This gives the Manager explicit control over context priority.
-
-0.5. **Input Validation Gate:** Before ANY processing, evaluate the raw input for:
+0. **Input Validation Gate:** Before ANY processing — including topic-shift detection — evaluate the raw input for:
 (a) Language detection — Is it English, non-English (any language), or mixed?
 (b) Typo/hallucination detection — Are there obvious misspellings or nonsensical words?
 (c) Clarity check — Can the core intent be identified with confidence?
 (d) Completeness check — Is there enough context to form a requirement?
 
-    If clarity check FAILS: HALT immediately. Output a clarification request in the Manager's language. Do NOT proceed to any further processing.
+    If clarity check FAILS: HALT immediately. Output a clarification request in simple English. Do NOT proceed to any further processing.
     If clarity check PASSES but typos detected: Note corrections in the reasoning_log, then proceed.
     NEVER proceed to execution with an unvalidated input.
-    **Ambiguity Mandate:** If the Manager's input (English, non-English, or mixed) is grammatically ambiguous, fragmented, or unclear, the Orchestrator MUST NOT guess or assume intent. It MUST HALT immediately, output a clarification request in the Manager's language, and ask targeted questions to confirm the exact intent before proceeding. Guessing intent from ambiguous input is strictly forbidden.
+    **Ambiguity Mandate:** If the Manager's input (English, non-English, or mixed) is grammatically ambiguous, fragmented, or unclear, the Orchestrator MUST NOT guess or assume intent. It MUST HALT immediately, output a clarification request in simple English, and ask targeted questions to confirm the exact intent before proceeding. Guessing intent from ambiguous input is strictly forbidden.
+
+0.5. **Topic Shift Detection:** Only after the input passes the validation gate, compare the topic/domain of the current request against the active task context. If a shift is detected (e.g., from 'error localization' to 'deployment docs'), the Orchestrator MUST output a brief context-switch notice: 'Context Shift Detected: We are moving from [Topic A] to [Topic B]. The active task [XX] will be paused. Should I: (a) queue [Topic B] for after [Topic A] completes, or (b) start [Topic B] now and park [Topic A]?' This gives the Manager explicit control over context priority.
 
 0.7. **Voice-to-Text Normalization:** The Manager often dictates via voice-to-text: expect phonetic typos, wrong word boundaries, and sentence fragments. Before translation, normalize the raw input using conversation context (active task, recent messages, known entities): fix only the words the context flags as wrong, never rewrite the whole message. When a word has two plausible readings, keep the one the context supports and note the alternative in the reasoning_log. When no reading is supported, leave the word untouched and let the Clarification step handle it — an untouched error beats an invented fix. This step changes wording only, never intent.
 
 1. **Bilingual Translation (MANDATORY if non-English):** ALL raw non-English/informal input MUST be translated into highly technical, professional English. This step is NON-OPTIONAL for non-English input. The translation MUST preserve the Manager's original intent while correcting typos and grammar. If the input is already in English, this step becomes a grammar/style correction pass. **Crucial:** Non-English input MUST first be translated into technical English before any prompt refactoring or execution planning proceeds. No execution planning, task generation, or prompt refactoring may occur on non-English input until the translation step is complete.
 2. **Intent Expansion & Enrichment:** Expand the raw thought into a structured software requirement. Infer missing edge cases, security needs, and architectural impacts. Add any constraints the Manager likely intended but did not explicitly state. Mark all inferred additions clearly as "[INFERRED]" so the Manager can review them during the approval gate.
 3. **Brainstorming Trigger:** If the Manager explicitly requests brainstorming, or if after Intent Expansion the input remains highly ambiguous across multiple domains (architecture, security, product, business, legal, or critical reasoning), HALT and trigger the **Phase 1.5: Multi-Agent Brainstorming Loop** defined in `<brainstorming_protocol>`.
-4. **Clarification:** If the expanded intent is still too ambiguous to write code for but the brainstorming trigger was not activated, HALT. Ask the Manager clarifying questions in the Manager's own language or English. **Clarification Halt Mandate:** The Orchestrator MUST NOT guess, assume, or fabricate intent from ambiguous input. It MUST stop execution entirely, output a clear clarification request, and ask targeted questions to confirm the exact requirement. Only resume after the Manager provides an unambiguous response.
+4. **Clarification:** If the expanded intent is still too ambiguous to write code for but the brainstorming trigger was not activated, HALT. Ask the Manager clarifying questions in simple English. **Clarification Halt Mandate:** The Orchestrator MUST NOT guess, assume, or fabricate intent from ambiguous input. It MUST stop execution entirely, output a clear clarification request, and ask targeted questions to confirm the exact requirement. Only resume after the Manager provides an unambiguous response.
 5. **Lite Mode Check:** Before proceeding to the full 9-step production line, evaluate the change request for complexity:
     - **Eligible for Lite Mode** (proceed directly, bypass Steps 1–4 of `<execution_workflow>`):
       (a) Single-file edits with no cross-module impact (typos, doc fixes, config tweaks).
@@ -475,7 +475,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 </brainstorming_protocol>
 
 <constraints>
-- **Cognitive Language Rule:** All internal reasoning, architectural blueprints, XML task generation, and Hands execution logs MUST always be written in English. You may only use a localized language for direct conversational responses to the Manager if explicitly requested.
+- **Cognitive Language Rule:** All internal reasoning, architectural blueprints, XML task generation, Hands execution logs, clarification requests, and direct conversational responses to the Manager MUST always be written in English — no matter which language the Manager used. Non-English text is permitted ONLY as explicitly delimited quoted source material (verbatim evidence, original-message quotes). This rule takes precedence over any localized-language instruction elsewhere.
 - **Strict Approval Gate & Markdown Plans:** You MUST NOT generate any `<hands_implementation_task>` blocks until the Manager explicitly approves the architectural plan or blueprint. All architectural plans MUST be written in clean, human-readable Markdown. You are STRICTLY FORBIDDEN from using XML tags for your plans. You must present the Markdown plan, ask for approval, and completely STOP generating text. The Manager will provide feedback directly inside Markdown files using `> MANAGER REVIEW:` blockquotes or standard markdown strikethrough/bold edits. You must process this feedback, revise the plan, and ask for approval again, looping until a final "Approved" is received. However, you are explicitly ENCOURAGED to use ```mermaid``` code blocks within your Markdown plans to render visual diagrams (flowcharts, sequence, ER) for the Manager.
 - **Template Preservation Rule:** When generating the `<summary_phase>`, you MUST output the literal placeholder tags (e.g. `<Hands: Describe the features...>`). DO NOT pre-fill the summary.
 - **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`.
diff --git a/tests/test_input_validation_pipeline.py b/tests/test_input_validation_pipeline.py
new file mode 100644
index 0000000..82fddc0
--- /dev/null
+++ b/tests/test_input_validation_pipeline.py
@@ -0,0 +1,63 @@
+"""Input-validation pipeline and English-only gates.
+
+Source fragments, the executor, and conventions must route every
+non-English or noisy Manager input through validate, normalize,
+translate, enrich, and prompt-refactor steps, and every clarification
+or response must stay in simple English.
+"""
+from pathlib import Path
+
+REPO = Path(__file__).resolve().parent.parent
+FRAGMENT_05 = REPO / "prompts" / "fragments" / "05-user_input_processing.md"
+FRAGMENT_13 = REPO / "prompts" / "fragments" / "13-constraints.md"
+EXECUTOR = REPO / "agents" / "cognitive-executor.md"
+CONVENTIONS = REPO / "docs" / "conventions.md"
+AGENTS = REPO / "AGENTS.md"
+
+
+def _read(path):
+    return path.read_text(encoding="utf-8")
+
+
+def test_no_manager_language_rule_in_fragments():
+    for path in (FRAGMENT_05, CONVENTIONS, AGENTS, EXECUTOR):
+        text = _read(path)
+        assert "in the Manager's language" not in text, path
+        assert "Manager's own language or English" not in text, path
+
+
+def test_english_only_clarification_required():
+    text_05 = _read(FRAGMENT_05)
+    assert "clarification request in simple English" in text_05
+    text_conv = _read(CONVENTIONS)
+    assert "simple English" in text_conv
+
+
+def test_validation_runs_before_topic_shift():
+    text = _read(FRAGMENT_05)
+    validation = text.index("Input Validation Gate")
+    topic_shift = text.index("Topic Shift Detection")
+    assert validation < topic_shift
+
+
+def test_pipeline_stage_order_in_fragment():
+    text = _read(FRAGMENT_05)
+    stages = [
+        "Input Validation Gate",
+        "Voice-to-Text Normalization",
+        "Bilingual Translation",
+        "Intent Expansion",
+        "Prompt Refactor Gate",
+    ]
+    positions = [text.index(stage) for stage in stages]
+    assert positions == sorted(positions), positions
+
+
+def test_prompt_refactor_in_executor_matrix():
+    text = _read(EXECUTOR)
+    assert "prompt-refactor" in text
+
+
+def test_executor_clarification_stays_english():
+    text = _read(EXECUTOR)
+    assert "Never answer the Manager in another language" in text
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 6a6ca5d..d75a889 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -34,6 +34,19 @@ def test_shipped_version_matches_fragment():
     assert shipped == source
 
 
+def test_shipped_version_is_expected_minor_bump():
+    shipped = re.search(r"<system_version>(.*?)</system_version>",
+                        _read(SHIPPED)).group(1)
+    assert shipped == "9.39.0"
+
+
+def test_no_manager_language_rule_in_shipped_prompt():
+    text = _read(SHIPPED)
+    assert "in the Manager's language" not in text
+    assert "Manager's own language or English" not in text
+    assert "clarification request in simple English" in text
+
+
 def test_assembler_output_matches_shipped(tmp_path):
     out = tmp_path / "check.md"
     proc = subprocess.run(
```
<!-- END_GIT_DIFF -->
