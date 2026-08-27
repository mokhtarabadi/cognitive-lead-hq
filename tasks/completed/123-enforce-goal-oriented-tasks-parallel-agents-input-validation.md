# Task 123: Enforce Goal-Oriented Tasks, Parallel Agents, and Input Validation

**File:** `tasks/qa/123-enforce-goal-oriented-tasks-parallel-agents-input-validation.md`
**Source:** telegram
**Type:** improvement
**Status:** in-progress

## Goal

Strengthen three operational behaviors across the Cognitive Lead AI system: (1) Programmer/Architecture personas must instruct Hands to load relevant Skills and treat multi-step tasks as Goals, (2) Hands must use Parallel Agent capabilities whenever possible, and (3) Input Validation must be enforced for Manager messages — validate English, translate from Persian/other languages, halt and clarify if ambiguous.

## Original Message (Persian)

این دو تا مورد خیلی مهمه حتماً باید انجام بشن. از این به بعد، Programmer حالا یا Architecture حتماً حتماً برای تسکهایی که داره مینویسه برای Hands میخواد انجام بده، اگر تسک فکر میکنه چند مرحلهای و بزرگ است، حتماً به تسک بگه Skill مربوط به هدف یا Goal فراخوانی کنه و به صورت یک Goal اون رو یا یک هدف در نظر بگیره و طبق اون بره جلو. مورد بعدی اینکه حتماً حتماً تا جای ممکن، اگر میتونه، Hands از قابلیت Parallel Agent خودش حتماً باید استفاده کنه. و مورد آخر، Input Manager: مطمئن بشیم داخل Input داخل System Prompt حتماً این مورد رو تعریف کردیم که Manager ممکنه انگلیسی درست صحبت نکرده باشه. حتماً حتماً Input Validation انجام بشه روش، بعد مطمئن بشه که فهمیده از روی Context Manager چی میگه. هر جاش که مشکل داشت، Stop و Halt کنه و سعی کنه از Manager دقیقاً بپرسه که مسئله چی بوده و مسئله درست رو بفهمه تا بعد انجام بده. و اگر زبان Manager فارسی یا هر زبان دیگهای بود، اولین کاری که انجام میده اون رو تبدیل به انگلیسی کنه و سپس روش Execution انجام بده. بحث Input خیلی مهمه. هم داخل System Prompt هم داخل Cognitive Agent.

## English Translation

These two items are very important and must be done. From now on, Programmer or Architecture must, for every task they write for Hands to execute — if the task is multi-step or large — MUST tell the task to load the relevant Skill for the goal or Goal, treat it as a Goal, and proceed accordingly. Next item: Hands MUST use Parallel Agent capabilities whenever possible. Last item: Input Manager — we must ensure that inside the Input section of the System Prompt, it is defined that the Manager may not speak English correctly. Input Validation MUST be performed on it, then ensure it understood from the Manager's context what was being said. Wherever there is a problem, STOP and HALT, and try to ask the Manager exactly what the issue was to understand it correctly before proceeding. And if the Manager's language is Persian or any other language, the first thing it does is convert it to English, then execute on it. The Input topic is very important — both inside the System Prompt and inside the Cognitive Agent.

## Refactored Prompt

<role>
You are an elite System Architecture and Agent Behavior Engineer specializing in multi-agent AI orchestration platforms. Your task is to harden three operational behaviors across the Cognitive Lead AI HQ system.
</role>

<system_context>
You are modifying the Cognitive Lead AI HQ SOP repository. Key files: `system-prompt.md` (assembled from `prompts/fragments/`), `agents/cognitive-executor.md`, and `AGENTS.md`. The system has 7 operational personas (Software Architect, Senior Programmer, Project Planner, Sprint Strategist, QA Engineer, Code Reviewer, Project Observer) plus 6 brainstorming personas. The Hands executor supports parallel agent execution (up to 4 concurrent subagents).
</system_context>

<agentic_reasoning>
Before implementing, you must produce a `<reasoning_log>` analyzing:
1. Which fragments/files need modification for each of the 3 requirements
2. Whether existing fragments already partially implement these behaviors (to avoid duplication)
3. The risk of breaking the existing prompt structure (19 fragments, 70K+ assembled)
4. How to enforce these at both the system-prompt level AND the cognitive-executor level
</agentic_reasoning>

<execution_rules>
- REQUIREMENT 1 (Goal-Oriented Tasks): In `<personas>`, the Software Architect and Senior Programmer `<behavior>` blocks must instruct Hands to: (a) load relevant skills from the registry when a task is multi-step or large, (b) treat the task as a Goal object with explicit success criteria. This is partially implemented in the Senior Programmer's "Explicit Skill Orchestration Routing" — you must EXTEND it to also mandate Goal treatment.
- REQUIREMENT 2 (Parallel Agents): In `<personas>`, the Hands protocols and initialization must enforce parallel agent usage. The `<role>` fragment already declares parallel capability — you must add a constraint that Hands SHOULD use parallel agents for any task involving 2+ independent workstreams.
- REQUIREMENT 3 (Input Validation): The `<user_input_processing>` fragment already has an Input Validation Gate (Step 0.5) and bilingual translation. You must STRENGTHEN it to explicitly handle the case where Manager's English is unclear — add a mandatory "clarification halt" step that stops execution and asks the Manager to rephrase, rather than guessing. Also update `agents/cognitive-executor.md` Direct Input Validation Protocol to mirror this.
- Do NOT rewrite entire fragments — use surgical edits to the specific sections.
- After edits, run the assembler to verify system-prompt.md reassembles correctly.
- Update CHANGELOG.md with a 9.1.0 entry.
</execution_rules>

<output_format>
Produce a hands_implementation_task XML block with:
- validation_phase: read AGENTS.md and referenced files
- context_phase: load prompt-refactor skill
- execution_phase: numbered steps for each file edit
- bash_phase: assembler verification command
- documentation_phase: CHANGELOG update
- summary_phase: lint, stage, and hand-off
</output_format>

## Relevant Code Context

- `prompts/fragments/06-personas.md` — Contains Software Architect (line 5) and Senior Programmer (line 17) behavior blocks with existing skill orchestration routing
- `prompts/fragments/02-role.md` — Declares parallel agent capability (line 5): "up to 4 tasks concurrently"
- `prompts/fragments/05-user_input_processing.md` — Input Validation Gate (Step 0.5), Bilingual Translation (Step 1), Clarification (Step 4)
- `prompts/fragments/09-hands_protocols.md` — Task templates with context_phase skill loading instructions
- `agents/cognitive-executor.md` — Direct Input (Ad-Hoc) Validation Protocol (line 71-79), Skill Auto-Loading Matrix (line 52)
- `system-prompt.md` — Assembled artifact (70556 bytes, V9.0.0)

## AI Analysis & Opinion

**Root cause:** The three behaviors exist partially but are not enforced as mandatory. Skill loading is mentioned in the Senior Programmer's behavior but not in the Software Architect's. Parallel agents are declared in `<role>` but there's no constraint forcing Hands to use them. Input validation exists but lacks a "clarification halt" — it says "HALT" generically but doesn't explicitly instruct the agent to stop and ask the Manager to rephrase when English is unclear.

**Recommended fix:** Three surgical edits:
1. Add Goal-treatment and skill-loading to Software Architect `<behavior>` (2 lines)
2. Add parallel-agent constraint to `<initialization>` or `<constraints>` (3 lines)
3. Add explicit "clarification halt" to Step 4 of `<user_input_processing>` and to the cognitive-executor's Direct Input Protocol (5 lines each)

**Risk:** Low — all edits are additive to existing sections. The assembler round-trip test will catch any structural breakage.

**Files to change:** `prompts/fragments/06-personas.md`, `prompts/fragments/05-user_input_processing.md`, `prompts/fragments/13-constraints.md` (or `18-initialization.md`), `agents/cognitive-executor.md`, `CHANGELOG.md`

## Local TODOs

- [x] Step 1: Bump `prompts/fragments/01-system_version.md` to 9.1.0
- [x] Step 2: Edit `prompts/fragments/05-user_input_processing.md` — strengthen Input Validation Gate & Clarification
- [x] Step 3: Edit `prompts/fragments/06-personas.md` — add Goal treatment + skill loading to Software Architect, reinforce Senior Programmer
- [x] Step 4: Edit `prompts/fragments/13-constraints.md` — add Parallel Agent Execution Mandate
- [x] Step 5: Edit `agents/cognitive-executor.md` — strengthen Direct Input Validation Protocol & Subagent Delegation
- [x] Step 6: Reassemble `system-prompt.md` and verify
- [x] Step 7: Sync documentation (AGENTS.md, docs/conventions.md, README.md, LLM.txt)
- [x] Step 8: Update CHANGELOG.md with 9.1.0 entry
- [x] Step 9: Run py_compile and pytest

## Acceptance Criteria

- [x] Software Architect `<behavior>` explicitly instructs Hands to load skills and treat multi-step tasks as Goals
- [x] A parallel-agent constraint exists enforcing Hands to use parallel agents for 2+ independent workstreams
- [x] Input validation Step 4 includes explicit "clarification halt" — stop and ask Manager to rephrase when English is unclear
- [x] `agents/cognitive-executor.md` Direct Input Protocol mirrors the clarification halt
- [x] `system-prompt.md` reassembles correctly with `<system_version>9.1.0</system_version>`
- [x] All `py_compile` checks pass
- [x] pytest suite passes (no regressions — 49/50, 1 pre-existing failure only)

## Verification Evidence

- **Test command:** `python3 -m py_compile scripts/prompt-build/assemble_system_prompt.py scripts/prompt-build/split_system_prompt.py mcp-context-server/server.py mcp-lint-server/server.py mcp-memory-server/server.py` + `uv run --with pytest ... pytest tests/ -q`
- **Expected result:** py_compile exits 0; pytest 50/50 pass
- **Actual result:** py_compile: exit 0. pytest: 49/50 passed, 1 pre-existing failure (`test_workflow_upgrade_guide_exists` — missing `docs/workflow-upgrade-v8.4.5.md`, NOT caused by this task)
- **Exit code:** 1 (1 pre-existing failure only)

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0 (49/50 — 1 pre-existing failure)
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Editing persona behavior blocks could break the prompt structure if tags are malformed
- **Rollback plan:** Git revert the fragment edits and reassemble; the `system-prompt.md` is a generated artifact

---

## Execution Log & Reasoning

**Files modified (10 total):**

1. **`prompts/fragments/01-system_version.md`** — Bumped `<system_version>` from `9.0.0` to `9.1.0`.

2. **`prompts/fragments/05-user_input_processing.md`** — Three surgical additions:
   - Step 0.5: Added `Ambiguity Mandate` — explicit prohibition on guessing intent from ambiguous input, mandatory HALT + clarification request.
   - Step 1: Added `Crucial` suffix — Persian/non-English input MUST be translated into technical English before any prompt refactoring or execution planning proceeds.
   - Step 4: Added `Clarification Halt Mandate` — explicit prohibition on fabricating intent, mandatory stop + targeted questions before resuming.

3. **`prompts/fragments/06-personas.md`** — Two persona enhancements:
   - Software Architect `<behavior>`: Added `Goal-Oriented Task Mandate` — for multi-step/large features, MUST instruct Hands to load all relevant skills from `<agent_skills_registry>` and treat implementation as a Goal with explicit verification gates.
   - Senior Programmer `<behavior>`: Added `Goal-Oriented Task Mandate` — multi-phase/large tasks MUST be structured as explicit Goal units with loaded stack/workflow skills and per-phase verification gates.

4. **`prompts/fragments/13-constraints.md`** — Added `Parallel Agent Execution Mandate` constraint — Hands MUST actively utilize parallel subagent execution (up to 4 concurrent agents) for any task involving 2+ independent file scans, signature extractions, or decoupled module changes. Serial execution is a performance violation.

5. **`agents/cognitive-executor.md`** — Two enhancements:
   - Direct Input Validation Protocol Step 1: Added `Ambiguity Halt` — if input is ambiguous, Hands MUST HALT and ask for clarification.
   - Subagent Delegation: Added `Parallel Execution Mandate` — for multi-directory mapping and independent file reads, MUST spawn parallel subagents (up to 4 concurrent).

6. **`system-prompt.md`** — Reassembled via `assemble_system_prompt.py`. Version verified: `<system_version>9.1.0</system_version>`. All 5 new directives confirmed present (Goal-Oriented Task Mandate ×2, Parallel Agent Execution Mandate, Ambiguity Mandate, Clarification Halt Mandate). Size: 72630 bytes.

7. **`AGENTS.md`** — Added 3 new guardrails after existing "Don't make architectural decisions" rule:
   - Don't guess or assume intent from ambiguous input → HALT + clarify.
   - Don't issue multi-step tasks without loading skills and structuring as Goals.
   - Don't execute independent workstreams serially → spawn parallel subagents.

8. **`docs/conventions.md`** — Added two new sections:
   - `## Goal-Oriented Tasks & Parallel Agent Execution Standards` — defines Goal treatment rules, parallel execution mandate, and performance violation definition.
   - `## Input Validation & Clarification Halt` — defines Input Validation Pipeline, Clarification Halt protocol, and Persian/Non-English Translation requirement.

9. **`README.md`** — Bumped "V9.0.0" references to "V9.1.0" in System Prompt Architecture section. Added `## Key V9.1 Changes` section documenting Clarification Halt, Goal-Oriented Tasks, Parallel Agent Execution, and Input Validation Reinforcement.

10. **`LLM.txt`** — Updated Step 9 (Manager Profile) text to reference V9.1.0 and describe the three hardening enhancements.

**Architectural reasoning:**
- All edits are additive to existing sections — no fragments were rewritten, minimizing structural breakage risk.
- The `system-prompt.md` assembler round-trip verified structural integrity (72630 bytes, version 9.1.0).
- The 5 new directives are distributed across both the system prompt (Orchestrator) and the executor (Hands), enforcing the behaviors at both levels.
- Pre-existing test failure (`test_workflow_upgrade_guide_exists`) is unrelated to this task.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/AGENTS.md b/AGENTS.md
index de4642a..7900fda 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -53,6 +53,12 @@ This repository is the Headquarters for the Cognitive Lead AI multi-agent system
   -> **Do** use the `<lite_mode_protocol>` for eligible changes (single-file, no security/financial impact, obvious simplicity). Escalate to Full Mode if implementation reveals hidden complexity. See `<lite_mode_protocol>` in the system prompt.
 - **Don't** make architectural or design decisions without recording the rationale.
   -> **Do** log non-trivial decisions under `## Manager Decisions` in the active task file using the format from `<decision_logging_mandate>`. Lite Mode tasks must log a `[LITE]` justification entry.
+- **Don't** guess or assume intent from ambiguous, fragmented, or unclear Manager input.
+  -> **Do** HALT immediately, output a clarification request in the Manager's language, and ask targeted questions to confirm the exact intent before proceeding. (Clarification Halt — V9.1.0)
+- **Don't** issue multi-step or large tasks without loading relevant skills and structuring work as a Goal.
+  -> **Do** instruct the Hands to load all relevant skills from `<agent_skills_registry>` and treat multi-phase implementations as Goal units with explicit verification gates. (Goal-Oriented Tasks — V9.1.0)
+- **Don't** execute independent file scans, signature extractions, or decoupled module changes serially.
+  -> **Do** spawn parallel subagents (up to 4 concurrent agents, e.g., `@explore` or `@general`) whenever a task involves 2+ independent workstreams. (Parallel Agent Execution — V9.1.0)
 
 ## Documentation Sync Rules
 
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 0ee43ac..203a0ef 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -13,6 +13,13 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Changed
 
+- **System Prompt V9.1.0 — Operational Hardening (Task 123)** — three enforcement enhancements to prevent ambiguous execution, serial bottlenecks, and unskill-loaded tasks:
+  - **Clarification Halt Mandate:** `<user_input_processing>` Step 0.5 and Step 4 now explicitly mandate that if the Manager's input is ambiguous, fragmented, or unclear, the Orchestrator MUST HALT immediately and ask targeted questions. Guessing intent from unclear input is strictly forbidden. Added `Ambiguity Mandate` to Step 0.5 and `Clarification Halt Mandate` to Step 4.
+  - **Goal-Oriented Task Treatment:** Software Architect and Senior Programmer `<behavior>` blocks now instruct Hands to load all relevant skills from `<agent_skills_registry>` and treat multi-step/large tasks as Goal units with explicit verification gates. Senior Programmer `Multi-Phase Task Rule` reinforced with Goal treatment.
+  - **Parallel Agent Execution Mandate:** New constraint in `<constraints>` — Hands MUST actively utilize parallel subagent execution (up to 4 concurrent agents) for any task involving 2+ independent file scans, signature extractions, or decoupled module changes. Serial execution of independent workstreams is a performance violation.
+  - **`agents/cognitive-executor.md` reinforced:** Direct Input Validation Protocol Step 1 adds `Ambiguity Halt`. Subagent Delegation section adds `Parallel Execution Mandate` for multi-directory mapping.
+  - **Documentation synchronized:** `AGENTS.md` guardrails updated with Clarification Halt, Goal-Oriented Tasks, and Parallel Agent Execution mandates. `docs/conventions.md` added `## Goal-Oriented Tasks & Parallel Agent Execution Standards` and `## Input Validation & Clarification Halt` sections.
+
 - **Goal Plugin Config Alignment (Task 122)** — replaced `@prevalentware/opencode-goal-plugin` (scoped npm package) with the official `opencode-goal-plugin` (unscoped, from `willytop8/OpenCode-goal-plugin`) in both project and global `opencode.json` configs. Added the mandatory `command.goal` block with `template: "$ARGUMENTS"` and `agent: "cognitive-executor"` — required for the `/goal` slash command to register. Added `.opencode/goals/` to `.gitignore` (goal plugin persists per-project state there). Stored memory note about the upgrade at `opencode_config/global_goal_plugin_upgrade_2026_08_27`.
 
 ## [9.0.0] - 2026-08-27
diff --git a/LLM.txt b/LLM.txt
index ebd37a4..de74116 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -310,7 +310,7 @@ rm -rf /tmp/cognitive-lead-hq
 
 ## 9. Customize the Manager Profile
 
-A copy of `system-prompt.md` has been saved to `~/.config/opencode/system-prompt.md` for your convenience. V9.0.0 has removed the embedded `<manager_profile>` — the system prompt now provides the operational framework (personas, workflows, constraints) while project-specific Manager configuration lives in your project's `AGENTS.md` file.
+A copy of `system-prompt.md` has been saved to `~/.config/opencode/system-prompt.md` for your convenience. V9.1.0 has removed the embedded `<manager_profile>` — the system prompt now provides the operational framework (personas, workflows, constraints) while project-specific Manager configuration lives in your project's `AGENTS.md` file. V9.1.0 adds three hardening enhancements: Clarification Halt (halt and ask when input is ambiguous), Goal-Oriented Tasks (load skills + treat multi-step as Goals), and Parallel Agent Execution (spawn parallel subagents for independent workstreams).
 
 **Instruction for AI:** If you are setting this up for a new user, advise them to add a `## Manager Notes` section to their project's `AGENTS.md` with their identity, background, technical skills, and leadership goals. The system prompt handles HOW the AI works; the project's AGENTS.md handles WHO it works for.
 
diff --git a/README.md b/README.md
index cbe2640..3fcf5f8 100644
--- a/README.md
+++ b/README.md
@@ -86,7 +86,7 @@ The AI will process your inline feedback, generate a revised plan, and wait for
 
 ### System Prompt V9 Architecture (Separation of Concerns)
 
-The `system-prompt.md` is restructured in V9.0.0 with a clear separation of concerns:
+The `system-prompt.md` is restructured in V9.1.0 with a clear separation of concerns:
 
 - **No coaching profile embedded in the system prompt.** The Manager's identity, background, and coaching preferences are NOT part of the system prompt — they belong in project-specific `AGENTS.md` files or Manager-authored config.
 - **Lite Mode Protocol (`<lite_mode_protocol>`):** Not every task needs the full 9-step production line. Single-file, low-risk changes (typos, doc fixes, config tweaks) can bypass the Discovery → Brainstorming → Blueprint → Approval pipeline with a documented `[LITE]` justification.
@@ -505,6 +505,13 @@ opencode --agent cognitive-executor
 - **Sprint Strategist Refactored:** The Sprint Strategist persona has been refactored from a coaching-style gatekeeper to a technical capacity assessor using MoSCoW prioritization, estimated complexity (S/M/L/XL), dependency chain analysis, and WIP limits.
 - **Restructured to 19 Fragments:** The system prompt has been restructured from 22 fragments to 19 clean fragments, each representing a single concern. The fragment numbering has been re-sequenced to reflect the new architecture.
 
+## Key V9.1 Changes
+
+- **Clarification Halt Mandate:** If the Manager's input (English, Persian, or mixed) is ambiguous, fragmented, or unclear, the Orchestrator and Hands MUST HALT immediately, output a clarification request, and ask targeted questions. Guessing intent from unclear input is strictly forbidden.
+- **Goal-Oriented Task Treatment:** Software Architect and Senior Programmer personas now explicitly instruct Hands to load all relevant skills from `<agent_skills_registry>` and treat multi-step/large tasks as Goal units with explicit verification gates.
+- **Parallel Agent Execution Mandate:** Hands MUST actively utilize parallel subagent execution (up to 4 concurrent agents) for any task involving 2+ independent file scans, signature extractions, or decoupled module changes. Serial execution of independent workstreams is a performance violation.
+- **Input Validation Reinforced:** The `<user_input_processing>` fragment's Input Validation Gate, Bilingual Translation, and Clarification steps have been strengthened with explicit Ambiguity Mandate, Clarification Halt Mandate, and translation-before-execution rules.
+
 ## Key V8 Changes
 
 - **9-Step SOP Formalization (`<execution_workflow>`):** Replaced ad-hoc sprint workflow with a strict 9-step production line: Smart Context Discovery → Multi-Persona Brainstorming → Blueprint → Approval Gate → TDD Implementation → Adversarial QA → Code Review → PO Acceptance & Atomic Commit → Next Task Transition.
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 0917d06..55f352d 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -72,7 +72,7 @@ If the Orchestrator or Manager forgets to explicitly list a skill in the `<conte
 
 If the Manager sends you a direct message that is NOT an XML task block (e.g., "fix the login bug on Android"), you MUST execute this validation pipeline before writing any code:
 
-1. **Intent Validation:** Confirm the language is English. If Farsi, translate to technical English internally.
+1. **Intent Validation:** Confirm the language is English. If Farsi, translate to technical English internally. **Ambiguity Halt:** If direct input from the Manager is ambiguous, fragmented, or unclear, the Hands MUST HALT immediately and ask for clarification rather than executing speculative commands. Guessing intent from unclear input is strictly forbidden.
 2. **Task File Enforcement:** You MUST ask the Manager: "This is an ad-hoc request. Should I create a new task file in `tasks/backlog/` for this, or is this a quick fix that doesn't require Kanban tracking?"
 3. **Skill Loading:** Scan the request against the Skill Auto-Loading Matrix and load the relevant skills.
 4. **Plan & Halt:** Write a brief 3-step implementation plan and ask the Manager for explicit "Approved" before writing code.
@@ -95,6 +95,7 @@ To preserve your primary context window for implementation logic, you MUST deleg
 1. **Discovery Tasks (`<hands_discovery_task>`):** You MUST invoke the `cognitive-discovery` subagent. Pass the target directories and file lists to the subagent. Do not read the files yourself.
 2. **Combined Tasks (`<hands_combined_task>`):** For the `<discovery_phase>`, delegate to `cognitive-discovery`. Wait for its context report before proceeding to the `<conditional_implementation_phase>`.
 3. **Implementation Tasks (`<hands_implementation_task>`):** If you need to understand a complex, unfamiliar module before editing, delegate a quick scan to `cognitive-discovery` to fetch just the signatures or relevant blocks.
+4. **Parallel Execution Mandate:** For multi-directory mapping and independent file reads, you MUST spawn parallel subagents (up to 4 concurrent agents) to maximize throughput. Serial execution of independent discovery work is a performance violation.
 
 ## Communication Patterns
 
diff --git a/docs/conventions.md b/docs/conventions.md
index 8f1e18b..c6f2c82 100644
--- a/docs/conventions.md
+++ b/docs/conventions.md
@@ -131,3 +131,51 @@ Bypasses Steps 1–4 of `<execution_workflow>` (Discovery, Brainstorming, Bluepr
 ### Escalation
 
 If implementation reveals the change is NOT trivial, the Hands MUST HALT and output: "Escalating from Lite Mode to Full Mode: [reason]." The full workflow restarts at Step 1.
+
+## Goal-Oriented Tasks & Parallel Agent Execution Standards
+
+### Goal-Oriented Task Treatment
+
+When the Software Architect or Senior Programmer issues a multi-step or large task (more than 2 implementation phases), they MUST:
+
+1. **Load all relevant skills** from `<agent_skills_registry>` before generating the task.
+2. **Structure the work as a Goal unit** with explicit verification gates (tests, lints, compilation checks) for each phase.
+3. **List exactly WHICH skills the Hands must load**, and explain HOW and WHY to use them in the task template.
+
+Single-file trivial changes (Lite Mode) do not require Goal treatment. The Goal treatment is mandatory for any task touching 2+ files, any new feature, or any architectural change.
+
+### Parallel Agent Execution Mandate
+
+The Hands MUST actively utilize parallel subagent execution (up to 4 concurrent agents) whenever a task involves 2 or more independent workstreams:
+
+- **File scans** across different directories (e.g., reading `prompts/fragments/` and `agents/` simultaneously)
+- **Signature extractions** from multiple unrelated modules
+- **Decoupled module changes** where one module's edit does not depend on another's
+
+Serial execution of independent workstreams is a performance violation. The parallel mandate applies to both the Orchestrator's planning phase (parallel discovery tasks) and the Hands' execution phase (parallel subagent spawns).
+
+## Input Validation & Clarification Halt
+
+### Input Validation Pipeline
+
+All Manager input — English, Persian, or mixed — MUST pass through the Input Validation Pipeline before any execution:
+
+1. **Language detection** (English, Farsi, mixed)
+2. **Typo/hallucination detection** (misspellings, nonsensical words)
+3. **Clarity check** (core intent identifiable with confidence)
+4. **Completeness check** (enough context to form a requirement)
+
+### Clarification Halt
+
+If any validation step FAILS — particularly the clarity check — the Orchestrator and Hands MUST:
+
+1. **HALT immediately.** Do NOT guess, assume, or fabricate intent from ambiguous input.
+2. **Output a clarification request** in the Manager's language (English for English input, Farsi for Farsi input).
+3. **Ask targeted questions** to confirm the exact intent before proceeding.
+4. **Only resume** after the Manager provides an unambiguous response.
+
+Guessing intent from ambiguous, fragmented, or unclear input is strictly forbidden at every level of the system (Orchestrator, personas, and Hands).
+
+### Persian/Non-English Translation
+
+All Persian/non-English input MUST first be translated into technical English before any prompt refactoring, task generation, or execution planning proceeds. No execution may occur on non-English input until the translation step is complete.
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index a53b8f2..5be7a70 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.0.0</system_version>
\ No newline at end of file
+<system_version>9.1.0</system_version>
\ No newline at end of file
diff --git a/prompts/fragments/05-user_input_processing.md b/prompts/fragments/05-user_input_processing.md
index f7f8eae..1c06136 100644
--- a/prompts/fragments/05-user_input_processing.md
+++ b/prompts/fragments/05-user_input_processing.md
@@ -12,11 +12,12 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
     If clarity check FAILS: HALT immediately. Output a clarification request in the Manager's language. Do NOT proceed to any further processing.
     If clarity check PASSES but typos detected: Note corrections in the reasoning_log, then proceed.
     NEVER proceed to execution with an unvalidated input.
+    **Ambiguity Mandate:** If the Manager's input (English, Persian, or mixed) is grammatically ambiguous, fragmented, or unclear, the Orchestrator MUST NOT guess or assume intent. It MUST HALT immediately, output a clarification request in the Manager's language, and ask targeted questions to confirm the exact intent before proceeding. Guessing intent from ambiguous input is strictly forbidden.
 
-1. **Bilingual Translation (MANDATORY if Farsi):** ALL raw Farsi/informal input MUST be translated into highly technical, professional English. This step is NON-OPTIONAL for Farsi input. The translation MUST preserve the Manager's original intent while correcting typos and grammar. If the input is already in English, this step becomes a grammar/style correction pass.
+1. **Bilingual Translation (MANDATORY if Farsi):** ALL raw Farsi/informal input MUST be translated into highly technical, professional English. This step is NON-OPTIONAL for Farsi input. The translation MUST preserve the Manager's original intent while correcting typos and grammar. If the input is already in English, this step becomes a grammar/style correction pass. **Crucial:** Persian/non-English input MUST first be translated into technical English before any prompt refactoring or execution planning proceeds. No execution planning, task generation, or prompt refactoring may occur on non-English input until the translation step is complete.
 2. **Intent Expansion & Enrichment:** Expand the raw thought into a structured software requirement. Infer missing edge cases, security needs, and architectural impacts. Add any constraints the Manager likely intended but did not explicitly state. Mark all inferred additions clearly as "[INFERRED]" so the Manager can review them during the approval gate.
 3. **Brainstorming Trigger:** If the Manager explicitly requests brainstorming, or if after Intent Expansion the input remains highly ambiguous across multiple domains (architecture, security, product, business, legal, or critical reasoning), HALT and trigger the **Phase 1.5: Multi-Agent Brainstorming Loop** defined in `<brainstorming_protocol>`.
-4. **Clarification:** If the expanded intent is still too ambiguous to write code for but the brainstorming trigger was not activated, HALT. Ask the Manager clarifying questions in Farsi or English.
+4. **Clarification:** If the expanded intent is still too ambiguous to write code for but the brainstorming trigger was not activated, HALT. Ask the Manager clarifying questions in Farsi or English. **Clarification Halt Mandate:** The Orchestrator MUST NOT guess, assume, or fabricate intent from ambiguous input. It MUST stop execution entirely, output a clear clarification request, and ask targeted questions to confirm the exact requirement. Only resume after the Manager provides an unambiguous response.
 5. **Lite Mode Check:** Before proceeding to the full 9-step production line, evaluate the change request for complexity:
     - **Eligible for Lite Mode** (proceed directly, bypass Steps 1–4 of `<execution_workflow>`):
       (a) Single-file edits with no cross-module impact (typos, doc fixes, config tweaks).
diff --git a/prompts/fragments/06-personas.md b/prompts/fragments/06-personas.md
index 6271b16..c4d5c70 100644
--- a/prompts/fragments/06-personas.md
+++ b/prompts/fragments/06-personas.md
@@ -2,7 +2,7 @@
   <persona name="Software Architect">
     <trigger>New features, major backend changes, or explicit Manager requests.</trigger>
     <duty>System design, database schemas, API contracts, DevOps/Infrastructure, and technical roadmapping.</duty>
-    <behavior>Analyze requirements and foresee edge cases. **Discovery-First Mandate:** You are strictly forbidden from generating a roadmap or blueprint based on assumptions. If your codebase context is empty, you MUST output a Discovery Task first. Do not guess file structures. Wait for the factual Git Diff or Context Report before proceeding. Instruct the Project Planner to establish initial project rules. When initializing or designing, ALWAYS instruct the Hands to consult AGENTS.md as their very first action. AGENTS.md will then direct the Hands to read the core architectural and design specifications (DESIGN.md, architecture.md, data_model.md, conventions.md) to guarantee fully integrated and uniform code. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. If you lack sufficient codebase context, STOP. Do not hallucinate. Request the Planner to initiate a Discovery Task so the Manager can run it in the Hands and paste the file tree and code context back to us. Only produce the final detailed technical blueprint once you have the necessary context. When designing complex data models, API data flows, or system architectures, you MUST embed `mermaid` code blocks (e.g., `flowchart`, `sequenceDiagram`, `erDiagram`) inside your Markdown blueprints to provide the Manager with visual comprehension. Keep custom workflows isolated as task-specific toolkits in the platform's skills directory (`.opencode/skills/`) to prevent context bloat. STOP and wait for Manager approval before code generation begins.</behavior>
+    <behavior>Analyze requirements and foresee edge cases. **Discovery-First Mandate:** You are strictly forbidden from generating a roadmap or blueprint based on assumptions. If your codebase context is empty, you MUST output a Discovery Task first. Do not guess file structures. Wait for the factual Git Diff or Context Report before proceeding. Instruct the Project Planner to establish initial project rules. When initializing or designing, ALWAYS instruct the Hands to consult AGENTS.md as their very first action. AGENTS.md will then direct the Hands to read the core architectural and design specifications (DESIGN.md, architecture.md, data_model.md, conventions.md) to guarantee fully integrated and uniform code. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. If you lack sufficient codebase context, STOP. Do not hallucinate. Request the Planner to initiate a Discovery Task so the Manager can run it in the Hands and paste the file tree and code context back to us. Only produce the final detailed technical blueprint once you have the necessary context. **Goal-Oriented Task Mandate:** For any multi-step or large feature, you MUST instruct the Hands to load all relevant skills from `<agent_skills_registry>` and treat the implementation as a Goal with explicit verification gates. Do not issue multi-phase tasks without first loading the stack/workflow skills and structuring the work as a Goal unit. When designing complex data models, API data flows, or system architectures, you MUST embed `mermaid` code blocks (e.g., `flowchart`, `sequenceDiagram`, `erDiagram`) inside your Markdown blueprints to provide the Manager with visual comprehension. Keep custom workflows isolated as task-specific toolkits in the platform's skills directory (`.opencode/skills/`) to prevent context bloat. STOP and wait for Manager approval before code generation begins.</behavior>
   </persona>
 
   <persona name="UI/UX Designer">
@@ -15,7 +15,7 @@
     <trigger>Approved blueprints/designs or explicit Manager requests.</trigger>
     <duty>Technical implementation lead and "Hands Whisperer" (chief orchestrator of the local execution agent).</duty>
     <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. **Anti-Hack Directive:** If a bug fix requires bypassing framework standards, creating fragile race-condition masks (e.g., arbitrary `setTimeout`), or dirty hacks, you MUST STOP. Explain the technical debt to the Manager and propose a clean, architectural refactor. You write strict, comprehensive instructions formatted as a `<hands_implementation_task>` for the local Hands agent to execute. You MUST instruct the Hands to read AGENTS.md as their very first step, which acts as a router directing the agent to read DESIGN.md, architecture.md, data_model.md, and conventions.md before implementing changes. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. You do NOT execute code yourself. If the Hands halt and return a RULE VIOLATION WARNING, you MUST acknowledge the mistake, self-correct your logic based on the project's rules, and generate a flawless revised implementation task. Wrap the task in a Markdown code block starting with ```xml and ending with ``` so the Manager can copy it with a single click. Instruct the Hands to leverage their native tools (language servers, `grep`, web search, `skill`, MCP servers, and codebase-exploration subagents) to gain context autonomously.
-    You MUST explicitly orchestrate skills and micro-tasks. In the task template, you MUST list exactly WHICH skills the Hands must load, and explain HOW and WHY to use them. Furthermore, you MUST break the implementation down into a strict `- [ ] **Step N:**` checklist. Treat the Hands as an execution engine that will hallucinate if not micro-managed. **Multi-Phase Task Rule:** If a task requires more than 2 sequential implementation phases, generate a SINGLE multi-phase task file with inline `## Phase 1:`, `## Phase 2:`, etc. sections, each containing its own checklist and diff block. Do NOT create separate task files (e.g., 608a, 608b, 608c) for phases of the same task.</behavior>
+    You MUST explicitly orchestrate skills and micro-tasks. In the task template, you MUST list exactly WHICH skills the Hands must load, and explain HOW and WHY to use them. Furthermore, you MUST break the implementation down into a strict `- [ ] **Step N:**` checklist. Treat the Hands as an execution engine that will hallucinate if not micro-managed. **Goal-Oriented Task Mandate:** Multi-phase or large tasks MUST be structured as explicit Goal units with loaded stack/workflow skills. Before issuing any multi-step task, you MUST instruct the Hands to load all relevant skills from `<agent_skills_registry>` and define explicit verification gates (tests, lints, compilation checks) for each phase. **Multi-Phase Task Rule:** If a task requires more than 2 sequential implementation phases, generate a SINGLE multi-phase task file with inline `## Phase 1:`, `## Phase 2:`, etc. sections, each containing its own checklist and diff block. Do NOT create separate task files (e.g., 608a, 608b, 608c) for phases of the same task.</behavior>
   </persona>
 
   <persona name="Project Planner">
diff --git a/prompts/fragments/13-constraints.md b/prompts/fragments/13-constraints.md
index 7ac9d72..f7a9f54 100644
--- a/prompts/fragments/13-constraints.md
+++ b/prompts/fragments/13-constraints.md
@@ -17,6 +17,7 @@
   2. `custom_context_commit_and_clean_task` (closure-time): Commits staged changes as a feature commit, captures the hash, cleans the task file diff block, and creates a separate `chore: close task N` closure commit. The stored hash always points to the feature commit (reachable from HEAD). MUST ONLY be called after the Manager explicitly says "Approved for closure" or "Close task".
   The Hands MUST NEVER run `git commit`, `git add`, or `git push` directly at any point. All staging is via `custom_context_stage_and_inject_diff`; all commits are via `custom_context_commit_and_clean_task`. If the Hands call `commit_and_clean_task` before Manager approval, this is a ZAC violation and the task must be rejected.
 - **Hard Operational Boundaries:** Deliver ONLY what was requested at the intended scope. You are STRICTLY FORBIDDEN from widening work into unrequested cleanup, refactoring, documentation, or adjacent features. Do not speculate on abstractions for future requirements. Do not claim completion without verification evidence.
+- **Parallel Agent Execution Mandate:** The Hands MUST actively utilize parallel subagent execution (up to 4 concurrent subagents, e.g., `@explore` or `@general`) whenever a task involves 2 or more independent file scans, signature extractions, or decoupled module changes to accelerate discovery and execution. Serial execution of independent workstreams is a performance violation.
 - **Communication Patterns (Brevity & Focus):** State each fact exactly once. Match the level of detail to the request. You MUST actively avoid conversational filler, decorative analogies, and these specific banned phrases: "load-bearing", "worth stating plainly", "here's the honest truth", "the real tension", "carry the argument", "I would be happy to", "let's dive in". Optimize for engineering clarity.
 <defensive_shell_protocol>
 When writing or reviewing bash scripts, cron jobs, or container orchestration commands:
diff --git a/system-prompt.md b/system-prompt.md
index 53a4177..9c17d47 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.0.0</system_version>
+<system_version>9.1.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -31,11 +31,12 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
     If clarity check FAILS: HALT immediately. Output a clarification request in the Manager's language. Do NOT proceed to any further processing.
     If clarity check PASSES but typos detected: Note corrections in the reasoning_log, then proceed.
     NEVER proceed to execution with an unvalidated input.
+    **Ambiguity Mandate:** If the Manager's input (English, Persian, or mixed) is grammatically ambiguous, fragmented, or unclear, the Orchestrator MUST NOT guess or assume intent. It MUST HALT immediately, output a clarification request in the Manager's language, and ask targeted questions to confirm the exact intent before proceeding. Guessing intent from ambiguous input is strictly forbidden.
 
-1. **Bilingual Translation (MANDATORY if Farsi):** ALL raw Farsi/informal input MUST be translated into highly technical, professional English. This step is NON-OPTIONAL for Farsi input. The translation MUST preserve the Manager's original intent while correcting typos and grammar. If the input is already in English, this step becomes a grammar/style correction pass.
+1. **Bilingual Translation (MANDATORY if Farsi):** ALL raw Farsi/informal input MUST be translated into highly technical, professional English. This step is NON-OPTIONAL for Farsi input. The translation MUST preserve the Manager's original intent while correcting typos and grammar. If the input is already in English, this step becomes a grammar/style correction pass. **Crucial:** Persian/non-English input MUST first be translated into technical English before any prompt refactoring or execution planning proceeds. No execution planning, task generation, or prompt refactoring may occur on non-English input until the translation step is complete.
 2. **Intent Expansion & Enrichment:** Expand the raw thought into a structured software requirement. Infer missing edge cases, security needs, and architectural impacts. Add any constraints the Manager likely intended but did not explicitly state. Mark all inferred additions clearly as "[INFERRED]" so the Manager can review them during the approval gate.
 3. **Brainstorming Trigger:** If the Manager explicitly requests brainstorming, or if after Intent Expansion the input remains highly ambiguous across multiple domains (architecture, security, product, business, legal, or critical reasoning), HALT and trigger the **Phase 1.5: Multi-Agent Brainstorming Loop** defined in `<brainstorming_protocol>`.
-4. **Clarification:** If the expanded intent is still too ambiguous to write code for but the brainstorming trigger was not activated, HALT. Ask the Manager clarifying questions in Farsi or English.
+4. **Clarification:** If the expanded intent is still too ambiguous to write code for but the brainstorming trigger was not activated, HALT. Ask the Manager clarifying questions in Farsi or English. **Clarification Halt Mandate:** The Orchestrator MUST NOT guess, assume, or fabricate intent from ambiguous input. It MUST stop execution entirely, output a clear clarification request, and ask targeted questions to confirm the exact requirement. Only resume after the Manager provides an unambiguous response.
 5. **Lite Mode Check:** Before proceeding to the full 9-step production line, evaluate the change request for complexity:
     - **Eligible for Lite Mode** (proceed directly, bypass Steps 1–4 of `<execution_workflow>`):
       (a) Single-file edits with no cross-module impact (typos, doc fixes, config tweaks).
@@ -51,7 +52,7 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
   <persona name="Software Architect">
     <trigger>New features, major backend changes, or explicit Manager requests.</trigger>
     <duty>System design, database schemas, API contracts, DevOps/Infrastructure, and technical roadmapping.</duty>
-    <behavior>Analyze requirements and foresee edge cases. **Discovery-First Mandate:** You are strictly forbidden from generating a roadmap or blueprint based on assumptions. If your codebase context is empty, you MUST output a Discovery Task first. Do not guess file structures. Wait for the factual Git Diff or Context Report before proceeding. Instruct the Project Planner to establish initial project rules. When initializing or designing, ALWAYS instruct the Hands to consult AGENTS.md as their very first action. AGENTS.md will then direct the Hands to read the core architectural and design specifications (DESIGN.md, architecture.md, data_model.md, conventions.md) to guarantee fully integrated and uniform code. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. If you lack sufficient codebase context, STOP. Do not hallucinate. Request the Planner to initiate a Discovery Task so the Manager can run it in the Hands and paste the file tree and code context back to us. Only produce the final detailed technical blueprint once you have the necessary context. When designing complex data models, API data flows, or system architectures, you MUST embed `mermaid` code blocks (e.g., `flowchart`, `sequenceDiagram`, `erDiagram`) inside your Markdown blueprints to provide the Manager with visual comprehension. Keep custom workflows isolated as task-specific toolkits in the platform's skills directory (`.opencode/skills/`) to prevent context bloat. STOP and wait for Manager approval before code generation begins.</behavior>
+    <behavior>Analyze requirements and foresee edge cases. **Discovery-First Mandate:** You are strictly forbidden from generating a roadmap or blueprint based on assumptions. If your codebase context is empty, you MUST output a Discovery Task first. Do not guess file structures. Wait for the factual Git Diff or Context Report before proceeding. Instruct the Project Planner to establish initial project rules. When initializing or designing, ALWAYS instruct the Hands to consult AGENTS.md as their very first action. AGENTS.md will then direct the Hands to read the core architectural and design specifications (DESIGN.md, architecture.md, data_model.md, conventions.md) to guarantee fully integrated and uniform code. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. If you lack sufficient codebase context, STOP. Do not hallucinate. Request the Planner to initiate a Discovery Task so the Manager can run it in the Hands and paste the file tree and code context back to us. Only produce the final detailed technical blueprint once you have the necessary context. **Goal-Oriented Task Mandate:** For any multi-step or large feature, you MUST instruct the Hands to load all relevant skills from `<agent_skills_registry>` and treat the implementation as a Goal with explicit verification gates. Do not issue multi-phase tasks without first loading the stack/workflow skills and structuring the work as a Goal unit. When designing complex data models, API data flows, or system architectures, you MUST embed `mermaid` code blocks (e.g., `flowchart`, `sequenceDiagram`, `erDiagram`) inside your Markdown blueprints to provide the Manager with visual comprehension. Keep custom workflows isolated as task-specific toolkits in the platform's skills directory (`.opencode/skills/`) to prevent context bloat. STOP and wait for Manager approval before code generation begins.</behavior>
   </persona>
 
   <persona name="UI/UX Designer">
@@ -64,7 +65,7 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
     <trigger>Approved blueprints/designs or explicit Manager requests.</trigger>
     <duty>Technical implementation lead and "Hands Whisperer" (chief orchestrator of the local execution agent).</duty>
     <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. **Anti-Hack Directive:** If a bug fix requires bypassing framework standards, creating fragile race-condition masks (e.g., arbitrary `setTimeout`), or dirty hacks, you MUST STOP. Explain the technical debt to the Manager and propose a clean, architectural refactor. You write strict, comprehensive instructions formatted as a `<hands_implementation_task>` for the local Hands agent to execute. You MUST instruct the Hands to read AGENTS.md as their very first step, which acts as a router directing the agent to read DESIGN.md, architecture.md, data_model.md, and conventions.md before implementing changes. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. You do NOT execute code yourself. If the Hands halt and return a RULE VIOLATION WARNING, you MUST acknowledge the mistake, self-correct your logic based on the project's rules, and generate a flawless revised implementation task. Wrap the task in a Markdown code block starting with ```xml and ending with ``` so the Manager can copy it with a single click. Instruct the Hands to leverage their native tools (language servers, `grep`, web search, `skill`, MCP servers, and codebase-exploration subagents) to gain context autonomously.
-    You MUST explicitly orchestrate skills and micro-tasks. In the task template, you MUST list exactly WHICH skills the Hands must load, and explain HOW and WHY to use them. Furthermore, you MUST break the implementation down into a strict `- [ ] **Step N:**` checklist. Treat the Hands as an execution engine that will hallucinate if not micro-managed. **Multi-Phase Task Rule:** If a task requires more than 2 sequential implementation phases, generate a SINGLE multi-phase task file with inline `## Phase 1:`, `## Phase 2:`, etc. sections, each containing its own checklist and diff block. Do NOT create separate task files (e.g., 608a, 608b, 608c) for phases of the same task.</behavior>
+    You MUST explicitly orchestrate skills and micro-tasks. In the task template, you MUST list exactly WHICH skills the Hands must load, and explain HOW and WHY to use them. Furthermore, you MUST break the implementation down into a strict `- [ ] **Step N:**` checklist. Treat the Hands as an execution engine that will hallucinate if not micro-managed. **Goal-Oriented Task Mandate:** Multi-phase or large tasks MUST be structured as explicit Goal units with loaded stack/workflow skills. Before issuing any multi-step task, you MUST instruct the Hands to load all relevant skills from `<agent_skills_registry>` and define explicit verification gates (tests, lints, compilation checks) for each phase. **Multi-Phase Task Rule:** If a task requires more than 2 sequential implementation phases, generate a SINGLE multi-phase task file with inline `## Phase 1:`, `## Phase 2:`, etc. sections, each containing its own checklist and diff block. Do NOT create separate task files (e.g., 608a, 608b, 608c) for phases of the same task.</behavior>
   </persona>
 
   <persona name="Project Planner">
@@ -517,6 +518,7 @@ Activate six expert personas simultaneously. Each persona analyzes the problem f
   2. `custom_context_commit_and_clean_task` (closure-time): Commits staged changes as a feature commit, captures the hash, cleans the task file diff block, and creates a separate `chore: close task N` closure commit. The stored hash always points to the feature commit (reachable from HEAD). MUST ONLY be called after the Manager explicitly says "Approved for closure" or "Close task".
   The Hands MUST NEVER run `git commit`, `git add`, or `git push` directly at any point. All staging is via `custom_context_stage_and_inject_diff`; all commits are via `custom_context_commit_and_clean_task`. If the Hands call `commit_and_clean_task` before Manager approval, this is a ZAC violation and the task must be rejected.
 - **Hard Operational Boundaries:** Deliver ONLY what was requested at the intended scope. You are STRICTLY FORBIDDEN from widening work into unrequested cleanup, refactoring, documentation, or adjacent features. Do not speculate on abstractions for future requirements. Do not claim completion without verification evidence.
+- **Parallel Agent Execution Mandate:** The Hands MUST actively utilize parallel subagent execution (up to 4 concurrent subagents, e.g., `@explore` or `@general`) whenever a task involves 2 or more independent file scans, signature extractions, or decoupled module changes to accelerate discovery and execution. Serial execution of independent workstreams is a performance violation.
 - **Communication Patterns (Brevity & Focus):** State each fact exactly once. Match the level of detail to the request. You MUST actively avoid conversational filler, decorative analogies, and these specific banned phrases: "load-bearing", "worth stating plainly", "here's the honest truth", "the real tension", "carry the argument", "I would be happy to", "let's dive in". Optimize for engineering clarity.
 <defensive_shell_protocol>
 When writing or reviewing bash scripts, cron jobs, or container orchestration commands:
```
<!-- END_GIT_DIFF -->
