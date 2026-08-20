# Task 105: Mermaid Diagram Generation for System Prompt

**File:** `tasks/backlog/105-mermaid-diagram-generation.md`
**Source:** telegram
**Type:** feature
**Status:** open

## Source Context

### Variant B: Telegram (`**Source:** telegram`)

## Goal

Explore Mermaid integration for generating diagrams and flowcharts from the system prompt, enabling planners and other roles to produce visual representations of plans and architectures.

## Original Message (Persian)

کاری که باید انجام بدم، باید ببینم آیا جالبه یا نه. یک ساختار اولیه از مامبرید پیدا کنم که سینتکس سادهاش رو داشته باشیم. بعد یک جزئیاتی داخل سیستم پرامپت اضافه کنم. پلنر وقتی میخواد پلن بریزه، یا حالا رولهای دیگه هم خواستن کاری انجام بدن. اگه واقعاً نیاز بود که من یک دیاگرام، یک فلوچارت هم ازش ببینم، میتونه با استفاده از مامبرید اون رو هم برای من بکشه. برای منیجر که وقتی میخوام ببینم، درک کنم پلان رو بهتر به صورت بصری هم خیلی بهتر بتونم این مورد رو درک کنم.
`#task`
`#memaraid`

## English Translation

The work I need to do: I should see if it's interesting or not. Find an initial structure of Mermaid that we have the simple syntax of. Then add some details inside the system prompt. When the planner wants to plan, or other roles want to do something — if I really need to see a diagram, a flowchart from it, it can draw that for me using Mermaid. For the manager, when I want to see and understand the plan, being able to understand it visually is much better.

## Refactored Prompt

<role>
You are a Systems Architect evaluating the integration of Mermaid diagram-as-code into an AI agent's system prompt ecosystem. The goal is to enable AI personas (Planner, Architect, Manager) to generate visual diagrams (flowcharts, sequence diagrams, architecture diagrams) as part of their planning output.
</role>

<system_context>
The project is the Cognitive Lead AI multi-agent system HQ. The system prompt is at `system-prompt.md` (generated from `prompts/fragments/`). The Manager is an AI-native Founder who needs to visually understand plans and architectures. The current system prompt has personas (Software Architect, Project Planner, QA Engineer, Code Reviewer) that produce text-only output. Mermaid is a JavaScript-based diagramming tool that renders markdown-like syntax into SVG/PNG diagrams.
</system_context>

<agentic_reasoning>
Before implementing, output a <reasoning_log> analyzing: (1) where Mermaid syntax would be injected in the system prompt (which persona, which section), (2) whether the Orchestrator (Brain) can render Mermaid or if it must be rendered by the Hands, (3) the simplest Mermaid diagram types most useful for planning (flowchart, sequence, architecture), (4) whether this should be a system prompt enhancement or a separate tool/script.
</agentic_reasoning>

<constraints>
- You MUST evaluate whether Mermaid integration adds genuine value before implementing.
- The system prompt is a GENERATED BUILD ARTIFACT — edits go in `prompts/fragments/` or `prompts/shared/`, then regenerate via `python3 scripts/prompt-build/assemble_system_prompt.py`.
- Keep the Mermaid syntax simple — only the most common diagram types (flowchart, sequence, class, architecture).
- The enhancement should be in the system prompt so ALL AI personas can use it, not just the Planner.
- Consider: should this be a new fragment, an addition to an existing fragment, or a shared partial?
- Mermaid rendering is a client-side concern (the Manager's viewer), not an AI concern. The AI just generates the Mermaid code block.
</constraints>

<output_format>
Return: (1) A recommendation on whether to proceed, with rationale. (2) If proceeding, the exact file(s) to modify and the proposed changes. (3) A list of Mermaid diagram types to support with examples.
</output_format>

## Relevant Code Context

- `system-prompt.md` — Generated build artifact (v8.4.6). 672 lines. Personas defined in `<persona>` blocks. No existing diagram/visual output capability.
- `prompts/fragments/` — Source fragments for system prompt. Key files: `04-manager_profile.md`, `14-hands_protocols.md`.
- `prompts/shared/` — Shared partials (e.g., `validation-phase.md`).
- `scripts/prompt-build/assemble_system_prompt.py` — Assembler that concatenates fragments into `system-prompt.md`.

## AI Analysis & Opinion

This is a research/exploration task. The core question is: does adding Mermaid to the system prompt genuinely help the Manager understand plans better?

**Pros:**
- Visual diagrams significantly improve comprehension of complex architectures and workflows
- Mermaid syntax is simple enough for AI to generate reliably
- The Manager (Founder) explicitly wants visual understanding of plans

**Cons/Risks:**
- The Orchestrator (Brain) is text-only — it generates Mermaid code blocks but cannot render them. The Manager must render them externally (Mermaid Live Editor, VS Code plugin, etc.)
- Adding Mermaid instructions to the system prompt increases token usage for every persona, even those that don't need diagrams
- The Planner persona already produces structured text output; diagrams may be redundant for simple plans

**Recommendation:** Proceed with a lightweight approach — add a shared Mermaid reference section to the system prompt that personas can optionally use, rather than mandating diagram output for every plan.

## Local TODOs

- [ ] Initial codebase exploration
- [ ] Research Mermaid syntax for common diagram types
- [ ] Evaluate integration point in system prompt (new fragment vs. existing fragment)
- [ ] Draft Mermaid reference section for system prompt
- [ ] Identify which personas benefit from Mermaid output
- [ ] Verify the system prompt regeneration works with the new content

## Acceptance Criteria

- [ ] A decision is made: proceed with integration or defer (with documented rationale)
- [ ] If proceeding: the exact files to modify are identified with proposed changes
- [ ] If proceeding: a Mermaid syntax reference section is drafted with 3+ diagram type examples
- [ ] The system prompt regeneration pipeline is verified to work with any proposed changes

## Verification Evidence

- **Test command:** `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check.md && diff /tmp/check.md system-prompt.md`
- **Expected result:** Exit code 0 if no changes to fragments; diff shows changes if fragments were modified
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Increased token usage in system prompt for personas that don't need diagrams; potential complexity creep
- **Rollback plan:** Remove the Mermaid section from the system prompt fragment and regenerate. The generated `system-prompt.md` reverts cleanly.

---

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
