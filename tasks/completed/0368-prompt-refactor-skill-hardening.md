# Task 0368: Prompt-Refactor Skill Hardening

**File:** `tasks/qa/0368-prompt-refactor-skill-hardening.md`
**Source:** manager
**Type:** improvement
**Status:** in-progress
**Submitted:** 2026-11-02T17:29:24Z
**Started:** 2026-11-02T17:29:16Z

## Goal

Harden the prompt-refactor skill's Markdown files against overpromising language, contradictory instructions, and weak gates, keeping the two-pass workflow and five-block anatomy stable for existing callers.

Phase 2 (Manager order, same task): review agents plus system prompt language rules with web research (blowsh) and a 2-seat Brain brainstorm, then apply the selected wording fixes: English fallback default, executor translate-and-proceed reword, mixed-input reply sentence.

## Manager's Notes

Direct Manager order, first as a quick fix ("review yourself, make yourself more powerful, fix your bugs, md files not codes"), then converted to a tracked task with Brain review in autopilot. Scope: skill Markdown only, no application code. Template plus global copy must stay byte-identical. Autopilot locked for this task.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Audit template and global copy for bugs and weak enforcement
- [x] Rewrite the skill with stricter gates and honest capability claims
- [x] Sync global copy and verify byte-identical
- [x] Lint changed files and run related tests
- [x] Update CHANGELOG.md
- [x] Apply language-policy wording fixes plus regenerate system prompt
- [ ] Run full test suite plus re-stage plus re-QA

## Acceptance Criteria

- [x] Overguarantee ("guarantees zero hallucination") replaced with structure plus evidence gates
- [x] Correct-and-log rule, `question` tool with prose fallback, calibrated ambiguity rubric with halt below 3
- [x] Canonical `<constraints>` tag, mandatory Scope line, verification checklist in `<output_format>`
- [x] Template and global copy byte-identical; no caller, fragment, or test file touched
- [x] No-request language fallback defined as English in the language policy
- [x] Executor intent-validation reworded to translate-and-proceed
- [x] Mixed-input reply tie-break sentence added; regenerated prompt in sync

## Verification Evidence

- **Test command:** full suite `pytest tests/ -q` (throwaway env: `uv run --with pytest --with "mcp<2" --with pathspec --with pyyaml`; RTK wrapper plus repo venv unavailable in this shell)
- **Expected result:** green
- **Actual result:** 748 passed plus 7 failed on first full run (6 missing-yaml, since fixed by adding pyyaml) — final: all green except `test_graph_split_oversize_fallback_names_resolve`, which fails only because `tree_sitter` is absent from the throwaway env (fallback text differs); zero Python server files touched by this diff, so unrelated to the change
- **Exit code:** 1 (sole failure environmental, evidenced above)

## Definition of Done

- [ ] Build/Test/Lint pass with exit code 0 (Phase 2 full suite: 1 environmental failure, `tree_sitter` absent — see Verification Evidence)
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Skill consumers depend on the five-block anatomy and two-pass step names; restructuring them would break fragments and tests.
- **Rollback plan:** Worktree is unstaged — `git checkout -- skill-templates/prompt-refactor/SKILL.md CHANGELOG.md` reverts the repo; re-copy the template over the global copy to revert that.

---

## Execution Log & Reasoning

Prior-session work (quick fix, now tracked here): read the template and global copy (identical, 76 lines each), scanned HQ references (canonical callers: input-processing gate, skills registry, executor matrix — all reference the skill by name only, so internal wording changes are safe), applied eight findings (F1 overguarantee, F2 silent-vs-log contradiction, F3 capability-manifest leak, F4 uncalibrated rubric, F5 dual tag names, F6 "immediately execute", F7 missing scope, F8 no evidence rule), rewrote the file, synced the global copy (`diff` empty, SYNC_OK), lint clean on both changed files, related test files green.

Assumption A1: four-digit ID padding follows the current lane convention. Assumption A2: leaving the work under ZAC (unstaged, uncommitted) until the Manager approves closure.

QA verdict (autopilot, same session): QA_PASSED with one non-blocking note R1 (confirm no hidden `<execution_rules>` alias dependency). R1 cleared by the Hands: repo-wide grep shows no active caller depends on the old alias — the only active hits are the skill's own new sentence, telegram-issue-sync's independent output spec, and this task's diff block; remaining hits are history archives. Staged set verified as exactly the three owned files; foreign memory-dir files left unstaged and untouched.

Review verdict (autopilot, same session): technically approved, PO_REVIEW_PENDING. Strengths: five-block anatomy ordered, two-pass names stable with gates, honesty fix plus Scope/citations/checklist, contained scope with byte-identical global copy. Single low-severity note I1 (alias removal, already cleared by grep evidence). Closure awaits the Manager's explicit approval word.

Phase 2 execution log (Manager-approved plan O1): 2-seat brainstorm (Architect + Designer) over repo audit plus blowsh papers W1/W2 selected keeping anchored English reasoning with three wording fixes. Edits: fragment 24 fallback → English, Outside section mixed-input tie-break sentence, executor 84 translate-and-proceed, version 9.70.0 → 9.70.1, test pin updated. Prettier clean, regenerate OK (111267 bytes), version grep matches in fragment plus artifact, new content at system-prompt.md:804/820, old strings gone repo-wide, status shows only intended files. Prompt sync check: in-sync (one pre-existing warning on untouched DECISIONS.md:47, out of scope). Full suite: all green except the environmental tree_sitter failure evidenced above.

Phase 2 QA verdict (manual chain, same session): QA_PASSED — fallback resolves to English, executor orders proceed, version pin consistent, staged names limited, unrelated env failure carries no weight. Phase 2 review verdict (same session): technically approved, PO_REVIEW_PENDING — matches O1, tie-break confirmed to fire only with no dominant language, no blocking issues. Closure awaits the Manager's explicit approval word.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index d906d87..178ad3c 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -36,6 +36,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Brief-first Telegram candidate approval and two-pass prompt-refactor (Task 0366):** `telegram-issue-sync` Phase 2 no longer asks the Manager for bare numeric message IDs, which are invisible in official Telegram apps; each `question`-tool option now leads with a `[YYYY-MM-DD HH:MM] sender — first 80 chars (type/topic)` brief, the numeric ID stays the machine value only, and the manual fallback uses a numbered brief list with server-side number-to-ID mapping. The `prompt-refactor` skill is now an explicit two-pass workflow (Step 1 refactor, Step 2 execute the formatted prompt as the live instruction under plan approval, ZAC, QA, and closure gates), mirrored one-line in the input-processing gate, executor matrix and Direct Input protocol, skills registry, and language policy execution binding. `system-prompt.md` reassembled (`9.69.0` → `9.70.0`, test pin follows). The plan-referenced verifier `scripts/verify-templates.sh` does not exist; verification ran the adjudicated fallback (`test_prompt_sync.py` 22 green via `rtk test uvx pytest`, `check_docs_sync.py` OK). Docs: slice ADRs in `skill-templates`, `prompts/fragments`, and `agents`.
 
+- **prompt-refactor skill hardening (quick fix, no task):** the skill overpromised ("guarantees zero hallucination"), contradicted itself on typos ("correct silently" plus "log corrections"), leaked internal machinery (capability-manifest wording for the `question` tool), scored ambiguity 1-5 with no rubric, accepted two names for the rules tag, and let Step 2 read as "immediately execute" past the gates. Fixed: honest capability line plus verification gates, correct-and-log, `question` tool with prose fallback, calibrated rubric with a halt rule below 3, canonical `<constraints>` tag, a mandatory `Scope: docs-only | code | mixed` line in `<system_context>`, an evidence checklist in `<output_format>`, and Step 1/Step 2 wording that keeps intermediate passes in chat with only the final prompt in the code block. Template plus global copy rewritten in sync (verified byte-identical); no caller, fragment, or test touched.
+
+- **Language-policy wording fixes plus prompt rebuild (same task, Phase 2):** a repo-wide audit found the language rules unanimous (English inside, requested language outside) with two gaps: the no-request fallback ("deployment default") was never defined, and the executor's "Confirm the language is English" read like rejecting non-English input. A 2-seat Brain brainstorm backed by web research (Zhao et al. multilingual-CoT consistency findings; Son et al. English-anchored mixed CoT) selected keeping anchored English reasoning. Applied: fallback defined as English plus a mixed-input reply tie-break in `24-language_policy.md`, translate-and-proceed reword in `agents/cognitive-executor.md`, PATCH rebuild `9.70.0` → `9.70.1` with test pin updated. Verified: prompt sync check in-sync, full suite green except one pre-existing environmental failure (see task file).
+
 ### Fixed
 
 - **Brain results are returned whole from Code Mode (Task 0354):** the executor's Code-mode output discipline told the Hands to return `{status, block_count: xml_blocks.length, model}`, a recipe meant to stop it printing a truncated prefix of a large XML block. The recipe instead licensed dropping the payload — turns returning only `output` lost `xml_blocks`, turns returning only `blocks` lost `output` — so the transcript and the agent's next turn held less than the server returned even though the executed instructions were complete. The rule now says a `brain_turn` result is evidence, not a preview: return `status`, `output`, `xml_blocks` and any diagnostic/`truncated` field exactly as received, never slice, map, summarize or field-shape it, and manage size before the call with `compact_context`, a leaner prompt or `include_bundle=false`. The runtime's `maxOutputBytes` remains the only acceptable cut and announces itself with `truncated: true`. Locked by a prompt-sync test that fails if the rule disappears or `block_count` returns; the live agent copy is byte-identical to the repo.
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 04e1b95..a2ed1fa 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -81,7 +81,7 @@ If the Orchestrator or Manager forgets to explicitly list a skill in the `<conte
 
 If the Manager sends you a direct message that is NOT an XML task block (e.g., "fix the login bug on Android"), you MUST execute this validation pipeline before writing any code:
 
-1. **Intent Validation:** Confirm the language is English. If non-English (any language), translate to technical English internally. **Normalize first:** the Manager often dictates via voice-to-text — fix phonetic typos and fragments using conversation context before translating; fix only what the context flags, and leave unsupported words untouched for the Ambiguity Halt below. **Ambiguity Halt:** If direct input from the Manager is ambiguous, fragmented, or unclear, the Hands MUST HALT immediately and ask for clarification in the per-message requested language rather than executing speculative commands. Guessing intent from unclear input is strictly forbidden.
+1. **Intent Validation:** Confirm the internal working language is English: if the input is non-English (any language), translate to technical English internally and proceed. **Normalize first:** the Manager often dictates via voice-to-text — fix phonetic typos and fragments using conversation context before translating; fix only what the context flags, and leave unsupported words untouched for the Ambiguity Halt below. **Ambiguity Halt:** If direct input from the Manager is ambiguous, fragmented, or unclear, the Hands MUST HALT immediately and ask for clarification in the per-message requested language rather than executing speculative commands. Guessing intent from unclear input is strictly forbidden.
 2. **Task File Enforcement:** You MUST ask the Manager: "This is an ad-hoc request. Should I create a new task file in `tasks/backlog/` for this, or is this a quick fix that doesn't require Kanban tracking?"
 3. **Skill Loading:** Scan the request against the Skill Auto-Loading Matrix and load the relevant skills.
 4. **Plan & Halt:** Write a brief 3-step implementation plan and ask the Manager for explicit "Approved" before writing code.
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 1ecee0f..17ff270 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.70.0</system_version>
+<system_version>9.70.1</system_version>
diff --git a/prompts/fragments/24-language_policy.md b/prompts/fragments/24-language_policy.md
index fa47ac8..85914a3 100644
--- a/prompts/fragments/24-language_policy.md
+++ b/prompts/fragments/24-language_policy.md
@@ -16,7 +16,7 @@ No blanket skill call per message. Gate by complexity every time.
 
 ## Detection
 
-Detect output language per message, never pin to a session default. When no explicit request is detected in that message, fall back to the deployment default.
+Detect output language per message, never pin to a session default. When no explicit request is detected in that message, fall back to English.
 
 Mixed input executes in English and answers in the requested language for that message.
 
@@ -32,7 +32,7 @@ Inside non-English handoffs, technical terms stay in English with no translitera
 
 ## Outside Requested Language
 
-The final Manager-facing handoff follows the per-message requested language. Keep it short, plain, and skimmable under the Manager-Facing Output Style. Think and reason in English, render the handoff in the requested language.
+The final Manager-facing handoff follows the per-message requested language. For mixed-language input, answer in the requested language of that message; when the request itself is mixed with no dominant language, default the reply to English. Keep it short, plain, and skimmable under the Manager-Facing Output Style. Think and reason in English, render the handoff in the requested language.
 
 ## Approval Literals Guard
 
diff --git a/skill-templates/prompt-refactor/SKILL.md b/skill-templates/prompt-refactor/SKILL.md
index 5313db8..d02dcf6 100644
--- a/skill-templates/prompt-refactor/SKILL.md
+++ b/skill-templates/prompt-refactor/SKILL.md
@@ -5,11 +5,11 @@ description: Refactors basic user prompts into elite, highly constrained, XML-ta
 
 # Prompt Refactoring & Enhancement Protocol
 
-You are an expert Prompt Engineer and Cognitive Architect. Your job is to take a basic, informal, or weak instruction from the Manager and rewrite it into a "Max Power" system instruction that guarantees maximum logical reasoning and zero hallucination from an AI agent.
+You are an expert Prompt Engineer and Cognitive Architect. Your job is to take a basic, informal, or weak instruction from the Manager and rewrite it into a "Max Power" system instruction that constrains the target AI toward precise reasoning and grounded output. No prompt can guarantee zero hallucination; this protocol reduces it through structure, explicit scope, and verification gates.
 
 ## The "Max Power" Prompt Anatomy
 
-When asked to refactor a prompt, you MUST output a markdown block containing a prompt structured with these exact XML tags:
+When asked to refactor a prompt, you MUST output a markdown block containing a prompt structured with these exact XML tags (five blocks, in this order):
 
 ### 1. `<role>`
 
@@ -17,7 +17,7 @@ Define the exact persona the AI must adopt (e.g., Senior Systems Programmer, UI/
 
 ### 2. `<system_context>`
 
-Define the environment the AI is operating in. What tools does it have? What are the boundaries of its knowledge?
+Define the environment the AI is operating in. What tools does it have? What are the boundaries of its knowledge? You MUST declare the target artifact scope on one line: `Scope: docs-only | code | mixed` (default `docs-only` unless the Manager explicitly requests code changes).
 
 ### 3. `<agentic_reasoning>`
 
@@ -26,26 +26,26 @@ This is the most critical block. You must instruct the target AI to output a `<r
 1. Logical dependencies
 2. Risk assessment
 3. Abductive reasoning (why did a bug happen?)
-4. Precision and Grounding
+4. Precision and Grounding (cite file paths with lines for every factual claim)
 
-### 4. `<execution_rules>` or `<constraints>`
+### 4. `<constraints>`
 
-Provide a bulleted list of strict "DO NOT" and "MUST DO" rules.
+The canonical tag is `<constraints>`; `<execution_rules>` is not accepted. Provide a bulleted list of strict "DO NOT" and "MUST DO" rules.
 
 - Force the AI to use specific architectural patterns (e.g., "You MUST use MVI and Unidirectional Data Flow").
 - Forbid lazy behavior (e.g., "Do NOT output placeholder code. Do NOT hallucinate variables").
 
 ### 5. `<output_format>`
 
-Provide the exact XML or JSON structure the AI must use to reply, ensuring it can be parsed by automated pipelines or easily copied by the Manager.
+Provide the exact XML or JSON structure the AI must use to reply, ensuring it can be parsed by automated pipelines or easily copied by the Manager. You MUST include a verification checklist (commands run with exit codes, files changed) so results are evidenced, never asserted.
 
 ## Step 0: Input Validation & Typo Correction
 
 Before translating or refactoring, scan the raw input for:
 
-1. **Obvious typos** — Correct them silently. Log corrections in the output.
-2. **Hallucinated/nonsensical words** — If a word has no meaning in context, flag it and ask the Manager for clarification (via the `question` tool when the session capability manifest shows it AVAILABLE, otherwise in prose).
-3. **Ambiguity score** — Rate the input clarity from 1 to 5. If below 3, HALT and request clarification before proceeding.
+1. **Obvious typos** — Fix them, then log each fix in the correction note (correct-and-log, never silent).
+2. **Hallucinated/nonsensical words** — If a word has no meaning in context, flag it and ask the Manager for clarification (via the `question` tool, falling back to prose when the tool is unavailable).
+3. **Ambiguity score** — Rate the input clarity from 1 to 5 using this rubric: 5 means intent, scope, and target files are all explicit; 4 means intent is clear with one minor gap fillable from context (log it as an assumption); 3 means intent is identifiable but scope or target is ambiguous (ask exactly one narrowing question before refactoring); 2 or below means HALT and request clarification. Never guess.
 
 Output a brief correction note at the top of your response:
 
@@ -55,8 +55,8 @@ Output a brief correction note at the top of your response:
 
 ## Workflow Execution (Two-Pass Refactor-then-Execute)
 
-1. **Step 1 Refactor:** Validate the raw input, translate to technical English when needed, expand the intent, and structure the result into the constrained XML instruction using the 5 blocks above (role, system_context, agentic_reasoning, execution_rules/constraints, output_format). Keep the Step 0 correction note, the translate-then-enrich pass with [INFERRED] markings, and the draft and refine passes inside this step. Output the final prompt in a single code block, as Deliver does today.
-2. **Step 2 Execute:** Immediately execute the formatted prompt from Step 1 as the live instruction in the same session. Step 2 runs under the existing gates: plan approval via the `question` tool, Zero-Autonomous-Commit with no git add, commit, checkout, or push, QA and review loops, and closure only on the explicit approval phrase. Never bypass gates, never auto-commit, never push. If the Step 1 output is ambiguous, halt and ask one narrow question via the `question` tool before executing.
+1. **Step 1 Refactor:** Validate the raw input, translate to technical English when needed, expand the intent (marking every added detail `[INFERRED]`), and structure the result into the constrained XML instruction using the 5 blocks above (role, system_context, agentic_reasoning, constraints, output_format). Intermediate passes (correction note, translate-then-enrich, draft, refine) stay in the chat as working notes; ONLY the final prompt goes inside a single code block (Deliver).
+2. **Step 2 Execute:** Execute the formatted prompt from Step 1 as the live instruction in the same session. Step 2 runs under the existing gates: plan approval via the `question` tool, Zero-Autonomous-Commit with no git add, commit, checkout, or push, QA and review loops, and closure only on the explicit approval phrase. Executing never bypasses gates. Never auto-commit, never push. If the Step 1 output is ambiguous, halt and ask one narrow question via the `question` tool before executing.
 
 ## Example Output Format
 
@@ -65,6 +65,10 @@ Output a brief correction note at the top of your response:
 You are an elite Golang Systems Architect...
 </role>
 
+<system_context>
+Scope: code. You work in a Go service using Hexagonal Architecture...
+</system_context>
+
 <constraints>
 - You MUST use Hexagonal Architecture.
 - You are strictly forbidden from bypassing the Repository pattern.
@@ -73,4 +77,8 @@ You are an elite Golang Systems Architect...
 <agentic_reasoning>
 Before writing code, you must output a <reasoning_log> analyzing the memory safety and big-O notation of your proposed algorithm.
 </agentic_reasoning>
+
+<output_format>
+Reply with the implementation plus a verification checklist (test command with exit code, files changed). Claims without evidence are rejected.
+</output_format>
 ```
diff --git a/system-prompt.md b/system-prompt.md
index 905d215..c848bfe 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.70.0</system_version>
+<system_version>9.70.1</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -801,7 +801,7 @@ No blanket skill call per message. Gate by complexity every time.
 
 ## Detection
 
-Detect output language per message, never pin to a session default. When no explicit request is detected in that message, fall back to the deployment default.
+Detect output language per message, never pin to a session default. When no explicit request is detected in that message, fall back to English.
 
 Mixed input executes in English and answers in the requested language for that message.
 
@@ -817,7 +817,7 @@ Inside non-English handoffs, technical terms stay in English with no translitera
 
 ## Outside Requested Language
 
-The final Manager-facing handoff follows the per-message requested language. Keep it short, plain, and skimmable under the Manager-Facing Output Style. Think and reason in English, render the handoff in the requested language.
+The final Manager-facing handoff follows the per-message requested language. For mixed-language input, answer in the requested language of that message; when the request itself is mixed with no dominant language, default the reply to English. Keep it short, plain, and skimmable under the Manager-Facing Output Style. Think and reason in English, render the handoff in the requested language.
 
 ## Approval Literals Guard
 
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 309f33a..114a051 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -44,7 +44,7 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.70.0"
+    assert shipped == "9.70.1"
 
 
 def test_parallel_mandate_covers_implementation_triggers():
```
<!-- END_GIT_DIFF -->
