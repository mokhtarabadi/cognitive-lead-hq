# Task: Add Voice-to-Text Enhancer Prompt

**File:** `tasks/41-add-voice-to-text-prompt.md`
**Type:** feature
**Status:** closed

## Goal

Create a new user-facing prompt template at `user-prompts/voice-to-text-enhancer.md` that transforms raw speech-to-text dictation into polished, actionable Markdown prompts. Also create the `user-prompts/` directory and update documentation.

## Manager's Notes

The prompt must follow the XML-tagged Markdown format with `<role>`, `<system_context>`, `<agentic_reasoning>`, `<constraints>`, and `<output_format>` sections. No conversational filler in output — only the cleaned, enhanced Markdown text.

## Local TODOs

- [x] Initial codebase exploration
- [x] Step 1: Generate task file
- [x] Step 2: Create `user-prompts/` directory
- [x] Step 3: Write `voice-to-text-enhancer.md` prompt file
- [x] Step 4: Verify file creation and content
- [x] Update CHANGELOG.md
- [x] Write execution log

## OpenCode Execution Log & Reasoning

**Architectural Reasoning:**

The `user-prompts/` directory establishes a new top-level namespace for user-facing prompt templates — distinctly separate from system prompts (`system-prompt.md`), agent skills (`.opencode/skills/`), and MCP configurations. This isolation prevents user-authored dictation templates from mixing with agent infrastructure. The voice-to-text enhancer prompt follows the same XML-tagged Markdown pattern (`<role>`, `<system_context>`, `<agentic_reasoning>`, `<constraints>`, `<output_format>`) used throughout the system prompt ecosystem, ensuring structural consistency and parsability for AI agents.

**Local TODOs verified:**

- [x] AGENTS.md checked — no violations; task creates Markdown-only prompt template (not functional code)
- [x] DESIGN.md, docs/architecture.md, docs/data_model.md — absent from repo, thus no conflict
- [x] Task-generator skill loaded — template format with `<!-- BEGIN_GIT_DIFF -->

```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 809754b..a74e48a 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

 ## [Unreleased]

+### Added
+
+- **Voice-to-Text Enhancer prompt** — New `user-prompts/voice-to-text-enhancer.md` with XML-tagged `<role>`, `<system_context>`, `<agentic_reasoning>`, `<constraints>`, and `<output_format>` sections. Transforms raw speech-to-text dictation into polished, actionable Markdown prompts. `user-prompts/` directory created as a new top-level namespace for user-facing prompt templates.
+
 ### Changed

 - **README roadmap** — Added Memory Management (Smart Note-Taking MCP & Skill) as item #7 in the Future Architectural Roadmap, describing a local `memory-mcp` server and `project-memory` agent skill for persistent context retention.
diff --git a/user-prompts/voice-to-text-enhancer.md b/user-prompts/voice-to-text-enhancer.md
new file mode 100644
index 0000000..47b418a
--- /dev/null
+++ b/user-prompts/voice-to-text-enhancer.md
@@ -0,0 +1,27 @@
+<role>
+You are an expert Voice-to-Text Processor and Prompt Architect. Your sole purpose is to take raw, messy spoken dictation and transform it into a perfectly polished, highly coherent, and actionable English prompt.
+</role>
+
+<system_context>
+The user inputs raw speech-to-text transcripts. These transcripts often contain severe phonetic misinterpretations, typos, run-on sentences, missing punctuation, and conversational filler. You act as a silent, stateless filter between the user's voice and their final destination.
+</system_context>
+
+<agentic_reasoning>
+Before generating your response, you must silently evaluate:
+1. Error Identification: What are the obvious speech-to-text errors and homophone mix-ups?
+2. Intent Extraction: What is the core objective of the user's dictation?
+3. Polish vs. Preserve: How can I elevate the grammar, structure, and clarity while strictly preserving the original meaning and scope?
+</agentic_reasoning>
+
+<constraints>
+- You MUST fix all typos, punctuation, grammatical errors, and awkward phrasing.
+- You MUST remove spoken filler words (e.g., "um", "like", "so basically").
+- You MUST NOT change the core meaning, hallucinate new ideas, or remove essential context.
+- You MUST format the output in clean Markdown to make it highly actionable for AI agents (using bolding, line breaks, or bullet points if the dictated structure implies it).
+- You are STRICTLY FORBIDDEN from outputting conversational filler, greetings, explanations, or notes (e.g., do not output "Here is the enhanced prompt:").
+- Output ONLY the final processed Markdown text.
+</constraints>
+
+<output_format>
+[Insert the cleaned, enhanced Markdown text directly. Zero conversational filler.]
+</output_format>
```

<!-- END_GIT_DIFF -->
