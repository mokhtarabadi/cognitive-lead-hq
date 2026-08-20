# Task 106: System Prompt Gap Analysis vs. External Reference

**File:** `tasks/backlog/106-system-prompt-gap-analysis.md`
**Source:** telegram
**Type:** improvement
**Status:** open

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

- [ ] Initial codebase exploration
- [ ] Read the full external system prompt
- [ ] Read the full project system prompt
- [ ] Identify structural and technique differences
- [ ] Map external techniques to gaps in our prompt
- [ ] Prioritize by hallucination-reduction impact
- [ ] Produce the gap analysis table
- [ ] Write top 3 recommendations

## Acceptance Criteria

- [ ] Both system prompts are read and analyzed in full
- [ ] A gap analysis table is produced with at least 5 identified gaps
- [ ] Each gap is grounded in actual content from both prompts (no hallucinated sections)
- [ ] Gaps are prioritized by hallucination-reduction impact
- [ ] Top 3 actionable recommendations are provided with rationale
- [ ] The analysis is stored in the task file for Manager review

## Verification Evidence

- **Test command:** `grep -c "## Gap\|## Recommendation\|Gap #" tasks/backlog/106-system-prompt-gap-analysis.md`
- **Expected result:** At least 5 (gaps) + 1 (recommendations) matches
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

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

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
