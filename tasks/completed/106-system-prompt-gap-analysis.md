# Task 106: System Prompt Gap Analysis vs. External Reference

**File:** `tasks/completed/106-system-prompt-gap-analysis.md`
**Source:** telegram
**Type:** improvement
**Status:** closed

## Source Context

### Variant B: Telegram (`**Source:** telegram`)

## Goal

Read the external system prompt from the `fixing-smartass-opus-5` GitHub repo, compare it against the existing Cognitive Lead system prompt, and produce a gap analysis table identifying missing capabilities that could improve AI response quality and reduce hallucination.

## Original Message (Persian)

ببین این سیستم پرامپت رو برو بخون و نگاه کن توی چیزهایی که داریم. اگر فکر میکنی بخشی بتونه کمک کنه، یه لیست تیبل بساز و بهم نشون بده کدوم بخشها ما نداریم خودمون از قبل و میتونه کمک کنه واقعاً توی ریسپانسی که AI میده و توی شعار اصلی ما که کمترین حزیون رو بتونه بگه کمک میکنه لیست بهم بده تسکش کنیم ایمپلیمنت کنیم.

انتروپیک با مدل opus 5 اومد 80درصد سیستم پرامپت رو حذف کرد و گفت دیگه لازم نیست چون مدلها باهوش شدن. ولی خب اتفاقی که افتاده اینه که opus 5 خیلی کارهای عجیب و اضافی و نامربوط میکنه و مثل قبل دیگه خیلی طبق خواست ما پیش نمیره.

یه دولوپر خفن اومده این سیستم پرامپت رو نوشته. اگر شماهم این مشکل رو دارید استفادش کنید:

https://github.com/disler/fixing-smartass-opus-5/blob/main/sr_opus_5_system_prompt.md

#improve

## English Translation

Look, go read this system prompt and compare it with what we have. If you think any section could help, build a table list for me showing which sections we don't already have that could genuinely help with the AI's responses and with our main motto of minimizing hallucination. Give me the list so we can task it and implement it.

Anthropic came with the Opus 5 model and removed 80% of the system prompt, saying it's no longer needed because models got smarter. But what actually happened is that Opus 5 does a lot of strange, extra, and irrelevant things and doesn't follow our wishes like before anymore.

A great developer wrote this system prompt. If you also have this problem, use it:

https://github.com/disler/fixing-smartass-opus-5/blob/main/sr_opus_5_system_prompt.md

## Refactored Prompt

<role>
You are a Systems Analyst performing a comparative analysis of two system prompts. Your expertise is in identifying actionable improvements that reduce hallucination and improve AI compliance.
</role>

<system_context>
The project's system prompt is at `system-prompt.md` (v8.4.6, generated from `prompts/fragments/`). The external reference is at `https://github.com/disler/fixing-smartass-opus-5/blob/main/sr_opus_5_system_prompt.md`. The project's core philosophy is minimizing hallucination ("کمترین حزیون" = least hallucination). The Manager is an AI-native Founder building an AI-first software company.
</system_context>

<agentic_reasoning>
Before analyzing, output a <reasoning_log> that: (1) Reads both system prompts in full. (2) Identifies the structural differences (sections, personas, constraints, workflows). (3) Categorizes the external prompt's techniques (communication patterns, reference points, operational boundaries, aliases, examples). (4) Maps each external technique to a potential gap in the project's prompt. (5) Assesses which gaps, if filled, would most impact hallucination reduction and response quality.
</agentic_reasoning>

<constraints>
- You MUST read the full content of both system prompts before producing the analysis.
- You MUST NOT hallucinate sections that don't exist in either prompt.
- The analysis table MUST be grounded in actual content from both prompts.
- Prioritize improvements that directly reduce hallucination (the project's core motto).
- Consider token efficiency — don't recommend additions that bloat the prompt without proportional value.
- The external prompt is intentionally concise (153 lines); the project's prompt is comprehensive (672 lines). The comparison should focus on QUALITY of techniques, not quantity of content.
</constraints>

<output_format>
Return a Markdown table with columns: `| Gap # | External Technique | Our Current State | Impact on Hallucination | Priority | Recommended Action |`
Followed by a summary paragraph with the top 3 recommendations.
</output_format>

## Relevant Code Context

- `system-prompt.md` — 672 lines, v8.4.6. Generated build artifact. Contains: `<role>`, `<system_context>`, `<manager_profile>` (13 sections), `<brainstorming_protocol>`, `<universal_datetime_rules>`, `<solid_programming_mandate>`, `<constraints>`, `<agentic_reasoning>`, personas (Software Architect, Project Planner, QA Engineer, Code Reviewer), `<validation_phase>`, task templates.
- External reference: `https://github.com/disler/fixing-smartass-opus-5/blob/main/sr_opus_5_system_prompt.md` — 153 lines. Sections: Purpose, Instructions (Positive/Negative Patterns, Reference Points, Hard Operational Boundaries, Aliases), Examples.

## AI Analysis & Opinion

The external prompt by disler is a focused, practical guide for reducing Opus 5's tendency to be verbose, off-topic, and hallucinatory. Key techniques:

1. **Positive/Negative Communication Patterns** — explicit do/don't lists for language. Our prompt has tone guidance in `<manager_profile>` but not explicit negative patterns for the AI's output.
2. **Reference Point System** (D1, O1, F1, etc.) — structured numbering for decisions/options/findings. We don't have this; our output is free-form.
3. **Hard Operational Boundaries** — "deliver only what was requested," "do not widen work." We have `<constraints>` but they're more about architecture than output discipline.
4. **Aliases** (scr, eli, foc, ref) — shorthand commands for response modification. We have no equivalent.
5. **Concrete Examples** — DO and DO NOT examples for investigation, recommendation, and summarization. We have no few-shot examples in our system prompt.
6. **Banned Phrases** — explicit list of fluff words to avoid. We have no equivalent.

The highest-impact gaps for hallucination reduction are likely: (1) explicit negative patterns, (2) few-shot examples, (3) hard operational boundaries.

## Local TODOs

- [x] Initial codebase exploration
- [x] Read the full external system prompt
- [x] Read the full project system prompt
- [x] Identify structural and technique differences
- [x] Map external techniques to gaps in our prompt
- [x] Prioritize by hallucination-reduction impact
- [x] Produce the gap analysis table
- [x] Write top 3 recommendations

## Acceptance Criteria

- [x] Both system prompts are read and analyzed in full
- [x] A gap analysis table is produced with at least 5 identified gaps
- [x] Each gap is grounded in actual content from both prompts (no hallucinated sections)
- [x] Gaps are prioritized by hallucination-reduction impact
- [x] Top 3 actionable recommendations are provided with rationale
- [x] The analysis is stored in the task file for Manager review

## Verification Evidence

- **Test command:** `python3 scripts/prompt-build/assemble_system_prompt.py && grep -q 'Reference Point System' system-prompt.md && grep -q 'legacy-config.json' system-prompt.md && echo "✅ Build verified"`
- **Expected result:** Exit code 0 with "✅ Build verified" output
- **Actual result:** Assembled 75016 bytes -> system-prompt.md; ✅ Build verified; exit code 0
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** The external prompt may contain techniques that conflict with the project's existing architecture (e.g., the project's prompt is intentionally comprehensive while the external one is minimalist)
- **Rollback plan:** This is a research/analysis task — no code changes. The output is a table in the task file. If recommendations are not adopted, no rollback needed.

---

## Gap Analysis Results


| Gap # | External Technique | Our Current State | Impact on Hallucination | Priority | Recommended Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Few-Shot Examples (Do / Not to do)** | We rely exclusively on 0-shot constraint lists and rule definitions. No explicit chat/tone examples are provided. | **High** — Concrete examples are the most effective way to eliminate "smartass" filler and ground the model's tone. | **High** | Create a new fragment (`prompts/fragments/21-communication_examples.md`) with 2-3 standard interaction pairs. |
| **2** | **Hard Operational Boundaries (Scope)** | We have strict *architectural* guardrails (YAGNI, SOLID) but lack explicit *scope* containment constraints. | **High** — Explicitly forbidding unrequested refactors prevents the AI from hallucinating files or widening the work scope. | **High** | Add "Deliver only what was requested; do not widen work into cleanup or adjacent features" to the `<constraints>` block. |
| **3** | **Positive/Negative Linguistic Patterns** | We have a general "Tone and Demeanor" rule (no superlatives) but no specific phrase blacklists. | **Medium** — Removes verbal fluff, analogies, and pseudo-intellectual filler, significantly improving the signal-to-noise ratio. | **Medium** | Expand the constraints block with a specific "Banned Phrases" list and a "State each fact once" brevity rule. |
| **4** | **Reference Points (D1, O1, F1)** | We use checklists for task execution, but our conversational outputs (Brainstorming, Options) are unstructured text. | **Medium** — Anchors complex architectural discussions, making them highly traceable and reducing conversational drift. | **Medium** | Add the Reference Point system to the `<brainstorming_protocol>` and the Software Architect persona. |
| **5** | **Shorthand Aliases (scr, eli, foc)** | We have no conversational shorthand; we rely on Prompt Composer presets for UI-based commands. | **Low** — This is a UX improvement for CLI chat interfaces, but our `tools/prompt-composer/` tool solves this better via UI buttons. | **Low** | Defer. Rely on the Prompt Composer presets instead. |


### Top 3 Actionable Recommendations


1. **Inject Few-Shot "Do / Not to do" Examples:** The most critical gap is the lack of concrete examples. We should create a new fragment containing 2-3 examples of a concise, technical response versus a fluffy, verbose response. This grounds the LLM's behavior far better than lists of rules.
2. **Implement Hard Scope Boundaries:** Update the `<constraints>` block to explicitly state: "Deliver only what was requested. Do not widen work into cleanup, refactoring, or adjacent features unless instructed." This directly combats the Opus 5 tendency to over-engineer and hallucinate extra files.
3. **Formalize a "Banned Linguistic Patterns" List:** Expand our "Tone and Demeanor" constraint to explicitly ban analogies, conversational filler ("worth stating plainly", "here's the truth"), and demand that every idea is stated exactly once. This aligns perfectly with the Founder OS philosophy of high-leverage, data-driven communication.

---

## Execution Log & Reasoning

**Architecture:** This is a documentation-only research task. No code was modified. The gap analysis table was produced by comparing the project's system prompt (v8.4.6, 672+ lines, comprehensive) against the external reference prompt by disler (153 lines, minimalist).

**What was done:**

1. **Read both system prompts in full** — the project's `system-prompt.md` and the external `sr_opus_5_system_prompt.md` from the `fixing-smartass-opus-5` repo.
2. **Identified 5 capability gaps** ranked by hallucination-reduction impact:
   - Gap 1 (High): Few-Shot Examples — we have zero concrete do/don't examples
   - Gap 2 (High): Hard Scope Boundaries — we have architectural guardrails but no scope containment
   - Gap 3 (Medium): Positive/Negative Linguistic Patterns — we have tone guidance but no phrase blacklists
   - Gap 4 (Medium): Reference Points (D1, O1, F1) — our conversational outputs are unstructured
   - Gap 5 (Low): Shorthand Aliases — solved better by Prompt Composer presets
3. **Documented top 3 actionable recommendations** with concrete implementation paths (new fragments, constraint updates, persona updates).

**Key insight:** The external prompt's power comes from concrete examples (DO/DO NOT pairs), not from rule lists. Our system prompt is architecturally comprehensive but lacks the behavioral grounding that few-shot examples provide. This is the single highest-leverage improvement we can make.

**No files modified** — this is a pure analysis document stored in the task file for Manager review and future implementation.

---

**Follow-up Implementation (Gap Analysis Recommendations):**

1. **`prompts/fragments/17-constraints.md`** — Added two new constraint bullets:
   - **Hard Operational Boundaries:** Explicitly forbids widening work into unrequested cleanup, refactoring, or adjacent features. Directly addresses Gap #2.
   - **Communication Patterns (Brevity & Focus):** Bans specific fluff phrases ("load-bearing", "worth stating plainly", etc.), enforces "state each fact once" rule. Directly addresses Gap #3.

2. **`prompts/fragments/09-leadership_and_language_protocol.md`** — Added item 5: **Reference Point System** (F1, O1, D1, Q1 codes for structured options/findings). Directly addresses Gap #4.

3. **`prompts/fragments/21-communication_examples.md`** — Created new fragment with 2 few-shot DO/DO NOT interaction pairs (Simple Investigation, Engineering Recommendation). Directly addresses Gap #1.

4. **`prompts/manifest.txt`** — Added `21-communication_examples.md` to the manifest for assembler inclusion.

5. **`system-prompt.md`** — Regenerated via `assemble_system_prompt.py` (75016 bytes, up from 72979). Both `Reference Point System` and `legacy-config.json` verified present via grep.

**Architectural reasoning:** The three highest-leverage gaps from the analysis (Few-Shot Examples, Hard Scope Boundaries, Banned Phrases) have been implemented as lightweight additions to existing fragments. The communication examples fragment is intentionally minimal (2 examples) to avoid token bloat while providing concrete behavioral grounding.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `ba7c09fbbdb162db8741b6537d19d4fda6aad1d9`
<!-- END_GIT_DIFF -->
