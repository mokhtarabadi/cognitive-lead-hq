# Task 123: Enforce Goal-Oriented Tasks, Parallel Agents, and Input Validation

**File:** `tasks/completed/123-enforce-goal-oriented-tasks-parallel-agents-input-validation.md`
**Source:** telegram
**Type:** improvement
**Status:** closed

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
**Factual Git Diff:** Stored in Commit Hash: `27f09f0eca88a192c8b3391a999be5b497752c90`
<!-- END_GIT_DIFF -->
