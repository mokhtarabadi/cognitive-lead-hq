# Task: Add Persian Dictation Prompt

**File:** `tasks/42-add-persian-dictation-prompt.md`
**Type:** feature
**Status:** closed

## Goal

Create a new user-facing prompt template at `user-prompts/persian-to-english-dictation.md` that converts raw Persian Speech-to-Text dictation into flawless, native-sounding English.

## Manager's Notes

The prompt must follow the XML-tagged Markdown format with `<role>`, `<system_context>`, `<agentic_reasoning>`, `<constraints>`, and `<output_format>` sections. No conversational filler in output — only the final English translation.

## Local TODOs

- [x] Step 1: Generate task file
- [x] Step 2: Write `persian-to-english-dictation.md` prompt file
- [x] Step 3: Verify file creation and content
- [x] Update CHANGELOG.md
- [x] Write execution log

## OpenCode Execution Log & Reasoning

**Architectural Reasoning:**

Extends the `user-prompts/` namespace (created in task 41) with a Persian-specific dictation pipeline. The XML-tagged structure remains consistent with `voice-to-text-enhancer.md` and the broader system prompt ecosystem. Key difference: this prompt functions as a bilingual translation API (Persian → English) with phonetic decoding for Persian VTT errors, whereas the English variant only cleans and polishes the same-language input.

**Changes Made:**

1. **`tasks/42-add-persian-dictation-prompt.md`** — Task file created (ID 42, after 41 existing files). Type: feature.
2. **`user-prompts/persian-to-english-dictation.md`** — XML-tagged prompt with 5 sections: role, system_context, agentic_reasoning (3-step phonetic→contextual→idiomatic pipeline), constraints (5 rules), output_format.
3. **`CHANGELOG.md`** — Added entry under `[Unreleased]` -> `### Added`.

**Local TODOs verified:**

- [x] AGENTS.md checked — no violations; creates Markdown-only prompt template
- [x] Skills loaded — task-generator (template format with diff markers), verification-before-completion (ls + cat verification)
- [x] No git commands executed — MCP tool will stage changes

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 809754b..62d5651 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,11 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

 ## [Unreleased]

+### Added
+
+- **Voice-to-Text Enhancer prompt** — New `user-prompts/voice-to-text-enhancer.md` with XML-tagged `<role>`, `<system_context>`, `<agentic_reasoning>`, `<constraints>`, and `<output_format>` sections. Transforms raw speech-to-text dictation into polished, actionable Markdown prompts. `user-prompts/` directory created as a new top-level namespace for user-facing prompt templates.
+- **Persian-to-English Dictation prompt** — New `user-prompts/persian-to-english-dictation.md` with XML-tagged sections. Converts raw Persian Speech-to-Text dictation into flawless, native-sounding English via phonetic decoding, contextual reconstruction, and idiomatic translation.
+
 ### Changed

 - **README roadmap** — Added Memory Management (Smart Note-Taking MCP & Skill) as item #7 in the Future Architectural Roadmap, describing a local `memory-mcp` server and `project-memory` agent skill for persistent context retention.
diff --git a/user-prompts/persian-to-english-dictation.md b/user-prompts/persian-to-english-dictation.md
new file mode 100644
index 0000000..0b0f166
--- /dev/null
+++ b/user-prompts/persian-to-english-dictation.md
@@ -0,0 +1,26 @@
+<role>
+You are an elite Bilingual Context Engine and Translation API. Your sole purpose is to convert raw, error-prone Persian Speech-to-Text (VTT) transcripts into flawless, native-sounding English.
+</role>
+
+<system_context>
+The input is a raw Persian voice dictation. Voice recognition software frequently introduces severe phonetic misinterpretations (homophone errors), ignores sentence boundaries, omits punctuation, and transcribes colloquial or slang spoken Persian literally. You act as a stateless, silent conversion pipeline bridging the gap between messy Persian speech and polished English text.
+</system_context>
+
+<agentic_reasoning>
+Before generating your response, you must silently evaluate:
+1. Phonetic Decoding: Which words did the VTT AI mishear? Identify and mentally correct phonetic mistakes based on the surrounding context.
+2. Contextual Reconstruction: Where are the true sentence boundaries? Mentally add punctuation and rebuild the sentence structure to uncover the true semantic intent.
+3. Idiomatic Translation: How do I express this reconstructed intent in highly professional, natural English? (Avoid robotic, word-for-word literal translations).
+</agentic_reasoning>
+
+<constraints>
+- You MUST function purely as a translation API endpoint.
+- You MUST output ONLY the final English translation.
+- You MUST NOT output the corrected Persian text.
+- You are STRICTLY FORBIDDEN from outputting <thinking> tags, reasoning logs, greetings, or any conversational filler (e.g., do not output "Here is your translation:").
+- If the input is heavily garbled or completely incomprehensible, you must deduce the most logical intent based on the context without complaining or leaving notes.
+</constraints>
+
+<output_format>
+[Insert the flawless English translation directly. Zero conversational filler.]
+</output_format>
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
