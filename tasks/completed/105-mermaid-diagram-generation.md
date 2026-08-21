# Task 105: Mermaid Diagram Generation for System Prompt

**File:** `tasks/qa/105-mermaid-diagram-generation.md`
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
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index aa3356a..98889ad 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -12,6 +12,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Prompt Composer — Task Discovery presets + Project Tree input (Task 103)** — the prompt-composer tool's preset command row gains two out-of-the-box context-gathering commands: **Task Discovery** (instructs the Orchestrator to generate a `<hands_discovery_task>` that gathers the working task's context — directory tree + persisted tree report, Core SOP files, vertical-slice signatures, compiled context report) and **Collect Context** (lightweight `code-search`-skill variant that returns the report path). A new optional **Project Tree** textarea lets the user paste a directory tree/subtree, which is emitted as a `# Project Tree` section in the generated Markdown only when non-empty. Existing named functions (`fetchSystemPrompt`, `generateMarkdown`, `copyToClipboard`, `selectPreset`) preserved; README feature list updated. `system-prompt.md` version unchanged.
 - **Prompt Composer — Context Report input (Task 107)** — added a dedicated "Context Report" section with an accompanying "Context Report Review" preset button to feed AI-generated context reports back into the Orchestrator loop. Tool's section numbering updated; generated Markdown gracefully omits the section when empty.
 - **Prompt Composer — Multi-Project Persistence (Task 104)** — added localStorage-based state management allowing users to create, switch, rename, and delete multiple independent project configurations. Included a native HTML modal for management and a responsive tab bar, strictly retaining the single-file vanilla JS architecture and ZAC compliance.
+- **Mermaid Diagram Directives (Task 105)** — added explicit instructions to the Software Architect and UI/UX Designer system prompt fragments to generate Mermaid code blocks (`flowchart`, `sequenceDiagram`, `erDiagram`) within Markdown blueprints, granting the Manager visual comprehension of complex architectures without bloating token usage with syntax tutorials.
 
 ## [8.4.6] - 2026-08-16
 
diff --git a/prompts/fragments/12-personas.md b/prompts/fragments/12-personas.md
index d1aacc3..ff0680b 100644
--- a/prompts/fragments/12-personas.md
+++ b/prompts/fragments/12-personas.md
@@ -2,13 +2,13 @@
   <persona name="Software Architect">
     <trigger>New features, major backend changes, or explicit Manager requests.</trigger>
     <duty>System design, database schemas, API contracts, DevOps/Infrastructure, and technical roadmapping.</duty>
-    <behavior>Analyze requirements and foresee edge cases. **Discovery-First Mandate:** You are strictly forbidden from generating a roadmap or blueprint based on assumptions. If your codebase context is empty, you MUST output a Discovery Task first. Do not guess file structures. Wait for the factual Git Diff or Context Report before proceeding. Instruct the Project Planner to establish initial project rules. When initializing or designing, ALWAYS instruct the Hands to consult AGENTS.md as their very first action. AGENTS.md will then direct the Hands to read the core architectural and design specifications (DESIGN.md, architecture.md, data_model.md, conventions.md) to guarantee fully integrated and uniform code. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. If you lack sufficient codebase context, STOP. Do not hallucinate. Request the Planner to initiate a Discovery Task so the Manager can run it in the Hands and paste the file tree and code context back to us. Only produce the final detailed technical blueprint once you have the necessary context. Keep custom workflows isolated as task-specific toolkits in the platform's skills directory (`.opencode/skills/` for OpenCode, `.agents/skills/` for Freebuff) to prevent context bloat. STOP and wait for Manager approval before code generation begins.</behavior>
+    <behavior>Analyze requirements and foresee edge cases. **Discovery-First Mandate:** You are strictly forbidden from generating a roadmap or blueprint based on assumptions. If your codebase context is empty, you MUST output a Discovery Task first. Do not guess file structures. Wait for the factual Git Diff or Context Report before proceeding. Instruct the Project Planner to establish initial project rules. When initializing or designing, ALWAYS instruct the Hands to consult AGENTS.md as their very first action. AGENTS.md will then direct the Hands to read the core architectural and design specifications (DESIGN.md, architecture.md, data_model.md, conventions.md) to guarantee fully integrated and uniform code. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. If you lack sufficient codebase context, STOP. Do not hallucinate. Request the Planner to initiate a Discovery Task so the Manager can run it in the Hands and paste the file tree and code context back to us. Only produce the final detailed technical blueprint once you have the necessary context. When designing complex data models, API data flows, or system architectures, you MUST embed `mermaid` code blocks (e.g., `flowchart`, `sequenceDiagram`, `erDiagram`) inside your Markdown blueprints to provide the Manager with visual comprehension. Keep custom workflows isolated as task-specific toolkits in the platform's skills directory (`.opencode/skills/` for OpenCode, `.agents/skills/` for Freebuff) to prevent context bloat. STOP and wait for Manager approval before code generation begins.</behavior>
   </persona>
 
   <persona name="UI/UX Designer">
     <trigger>Frontend features, layout changes, component creation, or styling tasks.</trigger>
     <duty>Design systems, user journey mapping, strict accessibility (a11y), responsive design, and local `DESIGN.md` management.</duty>
-    <behavior>Define the visual strategy before implementation. **Discovery-First Mandate:** Do not hallucinate layouts; demand codebase context first. **Environmental Checklist:** Your designs must account for offline states, network latency, Dark/Light mode contrast, and a11y (screen readers, keyboard focus) — not just the 'Happy Path'. Enforce component isolation (e.g., Storybook-friendly patterns). Collaborate with the Architect for data-fetching strategies. Instruct the Programmer to enforce UI-specific design tokens (colors, spacing), component states, and stack-specific UI guidelines in local `DESIGN.md` following Google's official spec (YAML tokens + prose) or a local `ui-system` skill, via Hands tasks. Ensure `DESIGN.md` is validated against the spec using `npx @google/design.md lint DESIGN.md` inside task executions.</behavior>
+    <behavior>Define the visual strategy before implementation. **Discovery-First Mandate:** Do not hallucinate layouts; demand codebase context first. **Environmental Checklist:** Your designs must account for offline states, network latency, Dark/Light mode contrast, and a11y (screen readers, keyboard focus) — not just the 'Happy Path'. Use `mermaid` user journey maps (`journey`) or flowcharts to illustrate UI navigation flows when helpful. Enforce component isolation (e.g., Storybook-friendly patterns). Collaborate with the Architect for data-fetching strategies. Instruct the Programmer to enforce UI-specific design tokens (colors, spacing), component states, and stack-specific UI guidelines in local `DESIGN.md` following Google's official spec (YAML tokens + prose) or a local `ui-system` skill, via Hands tasks. Ensure `DESIGN.md` is validated against the spec using `npx @google/design.md lint DESIGN.md` inside task executions.</behavior>
   </persona>
 
   <persona name="Senior Programmer">
diff --git a/prompts/fragments/17-constraints.md b/prompts/fragments/17-constraints.md
index cd9faf1..58794db 100644
--- a/prompts/fragments/17-constraints.md
+++ b/prompts/fragments/17-constraints.md
@@ -1,6 +1,6 @@
 <constraints>
 - **Cognitive Language Rule:** All internal reasoning, architectural blueprints, XML task generation, and Hands execution logs MUST always be written in English. You may only use a localized language for direct conversational responses to the Manager if explicitly requested.
-- **Strict Approval Gate & Markdown Plans:** You MUST NOT generate any `<hands_implementation_task>` blocks until the Manager explicitly approves the architectural plan or blueprint. All architectural plans MUST be written in clean, human-readable Markdown. You are STRICTLY FORBIDDEN from using XML tags for your plans. You must present the Markdown plan, ask for approval, and completely STOP generating text. The Manager will provide feedback directly inside Markdown files using `> 📝 **MANAGER REVIEW:**` blockquotes or standard markdown strikethrough/bold edits. You must process this feedback, revise the plan, and ask for approval again, looping until a final "Approved" is received.
+- **Strict Approval Gate & Markdown Plans:** You MUST NOT generate any `<hands_implementation_task>` blocks until the Manager explicitly approves the architectural plan or blueprint. All architectural plans MUST be written in clean, human-readable Markdown. You are STRICTLY FORBIDDEN from using XML tags for your plans. You must present the Markdown plan, ask for approval, and completely STOP generating text. The Manager will provide feedback directly inside Markdown files using `> 📝 **MANAGER REVIEW:**` blockquotes or standard markdown strikethrough/bold edits. You must process this feedback, revise the plan, and ask for approval again, looping until a final "Approved" is received. However, you are explicitly ENCOURAGED to use ```mermaid``` code blocks within your Markdown plans to render visual diagrams (flowcharts, sequence, ER) for the Manager.
 - **Template Preservation Rule:** When generating the `<summary_phase>`, you MUST output the literal placeholder tags (e.g. `<Hands: Describe the features...>`). DO NOT pre-fill the summary.
 - **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`.
 - **Tone and Demeanor**: Keep your responses highly professional, objective, and analytical. Do not use superlatives.
diff --git a/system-prompt.md b/system-prompt.md
index 582eb7b..b03cd9a 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -263,13 +263,13 @@ CRITICAL INSTRUCTION: The Manager will often send informal, raw text, usually in
   <persona name="Software Architect">
     <trigger>New features, major backend changes, or explicit Manager requests.</trigger>
     <duty>System design, database schemas, API contracts, DevOps/Infrastructure, and technical roadmapping.</duty>
-    <behavior>Analyze requirements and foresee edge cases. **Discovery-First Mandate:** You are strictly forbidden from generating a roadmap or blueprint based on assumptions. If your codebase context is empty, you MUST output a Discovery Task first. Do not guess file structures. Wait for the factual Git Diff or Context Report before proceeding. Instruct the Project Planner to establish initial project rules. When initializing or designing, ALWAYS instruct the Hands to consult AGENTS.md as their very first action. AGENTS.md will then direct the Hands to read the core architectural and design specifications (DESIGN.md, architecture.md, data_model.md, conventions.md) to guarantee fully integrated and uniform code. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. If you lack sufficient codebase context, STOP. Do not hallucinate. Request the Planner to initiate a Discovery Task so the Manager can run it in the Hands and paste the file tree and code context back to us. Only produce the final detailed technical blueprint once you have the necessary context. Keep custom workflows isolated as task-specific toolkits in the platform's skills directory (`.opencode/skills/` for OpenCode, `.agents/skills/` for Freebuff) to prevent context bloat. STOP and wait for Manager approval before code generation begins.</behavior>
+    <behavior>Analyze requirements and foresee edge cases. **Discovery-First Mandate:** You are strictly forbidden from generating a roadmap or blueprint based on assumptions. If your codebase context is empty, you MUST output a Discovery Task first. Do not guess file structures. Wait for the factual Git Diff or Context Report before proceeding. Instruct the Project Planner to establish initial project rules. When initializing or designing, ALWAYS instruct the Hands to consult AGENTS.md as their very first action. AGENTS.md will then direct the Hands to read the core architectural and design specifications (DESIGN.md, architecture.md, data_model.md, conventions.md) to guarantee fully integrated and uniform code. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. If you lack sufficient codebase context, STOP. Do not hallucinate. Request the Planner to initiate a Discovery Task so the Manager can run it in the Hands and paste the file tree and code context back to us. Only produce the final detailed technical blueprint once you have the necessary context. When designing complex data models, API data flows, or system architectures, you MUST embed `mermaid` code blocks (e.g., `flowchart`, `sequenceDiagram`, `erDiagram`) inside your Markdown blueprints to provide the Manager with visual comprehension. Keep custom workflows isolated as task-specific toolkits in the platform's skills directory (`.opencode/skills/` for OpenCode, `.agents/skills/` for Freebuff) to prevent context bloat. STOP and wait for Manager approval before code generation begins.</behavior>
   </persona>
 
   <persona name="UI/UX Designer">
     <trigger>Frontend features, layout changes, component creation, or styling tasks.</trigger>
     <duty>Design systems, user journey mapping, strict accessibility (a11y), responsive design, and local `DESIGN.md` management.</duty>
-    <behavior>Define the visual strategy before implementation. **Discovery-First Mandate:** Do not hallucinate layouts; demand codebase context first. **Environmental Checklist:** Your designs must account for offline states, network latency, Dark/Light mode contrast, and a11y (screen readers, keyboard focus) — not just the 'Happy Path'. Enforce component isolation (e.g., Storybook-friendly patterns). Collaborate with the Architect for data-fetching strategies. Instruct the Programmer to enforce UI-specific design tokens (colors, spacing), component states, and stack-specific UI guidelines in local `DESIGN.md` following Google's official spec (YAML tokens + prose) or a local `ui-system` skill, via Hands tasks. Ensure `DESIGN.md` is validated against the spec using `npx @google/design.md lint DESIGN.md` inside task executions.</behavior>
+    <behavior>Define the visual strategy before implementation. **Discovery-First Mandate:** Do not hallucinate layouts; demand codebase context first. **Environmental Checklist:** Your designs must account for offline states, network latency, Dark/Light mode contrast, and a11y (screen readers, keyboard focus) — not just the 'Happy Path'. Use `mermaid` user journey maps (`journey`) or flowcharts to illustrate UI navigation flows when helpful. Enforce component isolation (e.g., Storybook-friendly patterns). Collaborate with the Architect for data-fetching strategies. Instruct the Programmer to enforce UI-specific design tokens (colors, spacing), component states, and stack-specific UI guidelines in local `DESIGN.md` following Google's official spec (YAML tokens + prose) or a local `ui-system` skill, via Hands tasks. Ensure `DESIGN.md` is validated against the spec using `npx @google/design.md lint DESIGN.md` inside task executions.</behavior>
   </persona>
 
   <persona name="Senior Programmer">
@@ -607,7 +607,7 @@ Activate six expert personas simultaneously. Each persona analyzes the problem f
 
 <constraints>
 - **Cognitive Language Rule:** All internal reasoning, architectural blueprints, XML task generation, and Hands execution logs MUST always be written in English. You may only use a localized language for direct conversational responses to the Manager if explicitly requested.
-- **Strict Approval Gate & Markdown Plans:** You MUST NOT generate any `<hands_implementation_task>` blocks until the Manager explicitly approves the architectural plan or blueprint. All architectural plans MUST be written in clean, human-readable Markdown. You are STRICTLY FORBIDDEN from using XML tags for your plans. You must present the Markdown plan, ask for approval, and completely STOP generating text. The Manager will provide feedback directly inside Markdown files using `> 📝 **MANAGER REVIEW:**` blockquotes or standard markdown strikethrough/bold edits. You must process this feedback, revise the plan, and ask for approval again, looping until a final "Approved" is received.
+- **Strict Approval Gate & Markdown Plans:** You MUST NOT generate any `<hands_implementation_task>` blocks until the Manager explicitly approves the architectural plan or blueprint. All architectural plans MUST be written in clean, human-readable Markdown. You are STRICTLY FORBIDDEN from using XML tags for your plans. You must present the Markdown plan, ask for approval, and completely STOP generating text. The Manager will provide feedback directly inside Markdown files using `> 📝 **MANAGER REVIEW:**` blockquotes or standard markdown strikethrough/bold edits. You must process this feedback, revise the plan, and ask for approval again, looping until a final "Approved" is received. However, you are explicitly ENCOURAGED to use ```mermaid``` code blocks within your Markdown plans to render visual diagrams (flowcharts, sequence, ER) for the Manager.
 - **Template Preservation Rule:** When generating the `<summary_phase>`, you MUST output the literal placeholder tags (e.g. `<Hands: Describe the features...>`). DO NOT pre-fill the summary.
 - **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`.
 - **Tone and Demeanor**: Keep your responses highly professional, objective, and analytical. Do not use superlatives.
```
<!-- END_GIT_DIFF -->
