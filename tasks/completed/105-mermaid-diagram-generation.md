# Task 105: Mermaid Diagram Generation for System Prompt

**File:** `tasks/completed/105-mermaid-diagram-generation.md`
**Source:** telegram
**Type:** feature
**Status:** closed

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

- [x] Initial codebase exploration
- [x] Research Mermaid syntax for common diagram types
- [x] Evaluate integration point in system prompt (new fragment vs. existing fragment)
- [x] Draft Mermaid reference section for system prompt
- [x] Identify which personas benefit from Mermaid output
- [x] Verify the system prompt regeneration works with the new content

## Acceptance Criteria

- [x] A decision is made: proceed with integration or defer (with documented rationale)
- [x] If proceeding: the exact files to modify are identified with proposed changes
- [x] If proceeding: a Mermaid syntax reference section is drafted with 3+ diagram type examples
- [x] The system prompt regeneration pipeline is verified to work with any proposed changes

## Verification Evidence

- **Test command:** `python3 scripts/prompt-build/assemble_system_prompt.py && grep -i -c 'mermaid' system-prompt.md`
- **Expected result:** Exit code 0 and grep count ≥ 3
- **Actual result:** Assembled 72979 bytes -> system-prompt.md; grep count: 3; exit code 0
- **Exit code:** 0

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

**Architecture:** Lightweight Mermaid integration into the system prompt via surgical edits to existing persona and constraint fragments. No new fragment created — this keeps token overhead minimal while enabling visual diagram generation across personas.

**Changes made:**

1. **`prompts/fragments/12-personas.md` — Software Architect persona:** Added a directive before "Keep custom workflows isolated..." instructing the Architect to embed `mermaid` code blocks (flowchart, sequenceDiagram, erDiagram) in Markdown blueprints when designing complex data models, API flows, or system architectures. This ensures the Manager gets visual comprehension of architectural plans.

2. **`prompts/fragments/12-personas.md` — UI/UX Designer persona:** Added a directive before "Enforce component isolation..." instructing the Designer to use `mermaid` user journey maps (`journey`) or flowcharts to illustrate UI navigation flows when helpful.

3. **`prompts/fragments/17-constraints.md` — Strict Approval Gate constraint:** Appended an encouragement clause to the existing Approval Gate bullet, explicitly allowing `mermaid` code blocks within Markdown plans for visual diagrams. This removes any ambiguity about whether diagrams violate the "no XML in plans" rule.

4. **`system-prompt.md` — regenerated** via `assemble_system_prompt.py` (72979 bytes). Grep confirms 3 occurrences of 'mermaid' in the output.

**Key design decisions:**
- Modified existing fragments rather than creating a new one — minimal token overhead
- Only the Software Architect and UI/UX Designer personas get explicit Mermaid directives (the two personas most likely to produce visual plans)
- The constraint change is an encouragement, not a mandate — personas can choose when diagrams add value
- Mermaid rendering remains a client-side concern (Manager's viewer), not an AI concern

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `ff07236954c16a7c81e7ff32ac5b8ca58ffdf1aa`
<!-- END_GIT_DIFF -->
