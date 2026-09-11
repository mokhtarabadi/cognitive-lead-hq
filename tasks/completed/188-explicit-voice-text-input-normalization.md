# Task 188: Explicit voice-to-text input normalization pipeline (validate, normalize, translate, execute)

**File:** `tasks/qa/188-explicit-voice-text-input-normalization.md`
**Source:** manager
**Type:** improvement
**Status:** in-progress

## Goal

Make the Hands input pipeline explicitly handle voice-to-text typos and fragmented Farsi: normalize first from conversation context, then translate to technical English, then execute — as a written rule, not habit.

## Manager's Notes

Manager question (Farsi, verbatim):

"ببین یه چیزی برای خودم سؤاله، فقط جواب خودم رو بده به زبان انگلیسی ساده. من الان دارم به تو به زبان فارسی حرف می‌زنم و تو داری انگلیسی جواب می‌دی؛ من راضی هستم. فقط می‌خوام بفهمم توی Input Validation و Input Rule که داخل Cognitive Executor تعریف کردم و تو الان بهش دسترسی داری، آیا تو همیشه داری ورودی من رو validate می‌کنی؟ تی- تایپوهای من رو که دارم از ابزار Voice-to-Text استفاده می‌کنم، تایپو دارم، اون‌ها رو می‌گیری؟ از روی کانتکست محور می‌تونی درک کنی من چی گفتم؟ در نهایت تبدیلش می‌کنی و extendش می‌کنی به زبان انگلیسی و روی اون چیزی که درمیاد execution انجام بدی؟ اگر که فکر می‌کنی این کار رو داری انجام می‌دی، که عالی. اگر نه، ببین چرا این کار رو انجام نمی‌دی. اگر نیاز Cognitive Executor تو بخش Input Validation یا بخش Input کاربر کاری انجام بشه، هم توی System Prompt هم داخل Cognitive Executor کار رو انجام بده. این رو هم به عنوان یک task جدید تعریف کن. اگر نیاز بود کاری انجام بدی، به عنوان یک task جدید توی backlog تعریفش کن."

English translation: The manager speaks Farsi (often via voice-to-text, with typos and fragments) and is happy with English answers. He asks: does the Hands always validate his input? Does it catch voice-to-text typos? Does it understand intent from conversation context? Does it convert/extend to English and execute on that? If yes, great. If not, find out why. If the Cognitive Executor input-validation section (in the system prompt and the executor file) needs work, do it — and define it as a new backlog task.

Self-audit finding (Hands, 2026-09-11): the Direct Input Validation Protocol (executor line 72-76) covers Farsi→English translation and the Ambiguity Halt, and session evidence shows typo-fixing works in practice ("clousre"→closure, "1184"→184, "آلیس"→analysis, "Fram"→prompt, "استیل"→skill). But voice-to-text typo normalization is habit, not a written rule. This task definition IS the requested new backlog task; implementation (executor + system-prompt fragment wording) is still pending.

Scope: executor file + the system-prompt fragment that mirrors the input pipeline (if any). Minimal wording change, no behavior change for XML tasks.

## Local TODOs

- [x] Locate the system-prompt fragment mirroring the Direct Input Validation Protocol
- [x] Add explicit normalize step: voice-to-text typos and fragments resolved from conversation context before translation
- [x] Mirror the wording in agents/cognitive-executor.md Direct Input section
- [x] Reassemble system prompt if a fragment changed, verify sync
- [x] Update CHANGELOG, lint, stage, move to qa

## Acceptance Criteria

- [x] A written normalize step exists: typos/fragments fixed from conversation context before translation
- [x] Executor file and system-prompt fragment say the same thing (no N/NOT-N clash)
- [x] Ambiguity Halt unchanged (still halts on truly unclear input)
- [x] `lint_task_file` passes on the task file

## Verification Evidence

- **Test command:** `grep -n -i "voice-to-text\|normalize" agents/cognitive-executor.md prompts/fragments/*.md`
- **Expected result:** normalize step present in both executor and fragment
- **Actual result:** step 0.7 present in fragment 05, Normalize-first sentence in executor step 1; `diff /tmp/check188.md system-prompt.md` → SYNC_OK, 79237 bytes, Voice-to-Text Normalization count 1, 9.22.0 count 1
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Over-normalization — "fixing" a typo the manager intended literally.
- **Rollback plan:** Ambiguity Halt stays the guardrail; revert wording via git diff on the two files.

---

## Execution Log & Reasoning

Implemented the approved plan A1–A4. A1: step 0.7 Voice-to-Text Normalization in fragment 05 (fix only context-flagged words, note alternatives, untouched-error-beats-invented-fix, wording-only-never-intent). A2: Normalize-first sentence in executor step 1, same wording. A3: Ambiguity Halt untouched — it is the guardrail against over-normalization. A4: version 9.21.0→9.22.0, reassembled SYNC_OK byte-identical (79237 bytes). Research grounding: arXiv 2505.24347 (correct-verify pipeline), arXiv 2310.11532 (over-correction warning), COLING 2025 (context ranking +34% recall). No XML-task behavior change.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index c4d191b..a737982 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,12 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+## [9.22.0] - 2026-09-11
+
+### Added
+
+- **Explicit voice-to-text input normalization (Task 188):** New step 0.7 Voice-to-Text Normalization in `prompts/fragments/05-user_input_processing.md`, mirrored in the executor Direct Input section — fix only context-flagged words from conversation history, note alternatives in `<reasoning_log>`, untouched-error-beats-invented-fix, wording-only-never-intent. Grounded in fresh research: three-stage correct-verify pipeline (arXiv 2505.24347), over-correction danger (arXiv 2310.11532), context-augmented ranking +34% recall (COLING 2025). Ambiguity Halt unchanged.
+
 ## [9.21.0] - 2026-09-11
 
 ### Changed
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index c699f3f..dc5520c 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -73,7 +73,7 @@ If the Orchestrator or Manager forgets to explicitly list a skill in the `<conte
 
 If the Manager sends you a direct message that is NOT an XML task block (e.g., "fix the login bug on Android"), you MUST execute this validation pipeline before writing any code:
 
-1. **Intent Validation:** Confirm the language is English. If Farsi, translate to technical English internally. **Ambiguity Halt:** If direct input from the Manager is ambiguous, fragmented, or unclear, the Hands MUST HALT immediately and ask for clarification rather than executing speculative commands. Guessing intent from unclear input is strictly forbidden.
+1. **Intent Validation:** Confirm the language is English. If Farsi, translate to technical English internally. **Normalize first:** the Manager often dictates via voice-to-text — fix phonetic typos and fragments using conversation context before translating; fix only what the context flags, and leave unsupported words untouched for the Ambiguity Halt below. **Ambiguity Halt:** If direct input from the Manager is ambiguous, fragmented, or unclear, the Hands MUST HALT immediately and ask for clarification rather than executing speculative commands. Guessing intent from unclear input is strictly forbidden.
 2. **Task File Enforcement:** You MUST ask the Manager: "This is an ad-hoc request. Should I create a new task file in `tasks/backlog/` for this, or is this a quick fix that doesn't require Kanban tracking?"
 3. **Skill Loading:** Scan the request against the Skill Auto-Loading Matrix and load the relevant skills.
 4. **Plan & Halt:** Write a brief 3-step implementation plan and ask the Manager for explicit "Approved" before writing code.
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 334270b..19d04e8 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.21.0</system_version>
+<system_version>9.22.0</system_version>
diff --git a/prompts/fragments/05-user_input_processing.md b/prompts/fragments/05-user_input_processing.md
index 1c06136..4629a9c 100644
--- a/prompts/fragments/05-user_input_processing.md
+++ b/prompts/fragments/05-user_input_processing.md
@@ -14,6 +14,8 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
     NEVER proceed to execution with an unvalidated input.
     **Ambiguity Mandate:** If the Manager's input (English, Persian, or mixed) is grammatically ambiguous, fragmented, or unclear, the Orchestrator MUST NOT guess or assume intent. It MUST HALT immediately, output a clarification request in the Manager's language, and ask targeted questions to confirm the exact intent before proceeding. Guessing intent from ambiguous input is strictly forbidden.
 
+0.7. **Voice-to-Text Normalization:** The Manager often dictates via voice-to-text: expect phonetic typos, wrong word boundaries, and sentence fragments. Before translation, normalize the raw input using conversation context (active task, recent messages, known entities): fix only the words the context flags as wrong, never rewrite the whole message. When a word has two plausible readings, keep the one the context supports and note the alternative in the reasoning_log. When no reading is supported, leave the word untouched and let the Clarification step handle it — an untouched error beats an invented fix. This step changes wording only, never intent.
+
 1. **Bilingual Translation (MANDATORY if Farsi):** ALL raw Farsi/informal input MUST be translated into highly technical, professional English. This step is NON-OPTIONAL for Farsi input. The translation MUST preserve the Manager's original intent while correcting typos and grammar. If the input is already in English, this step becomes a grammar/style correction pass. **Crucial:** Persian/non-English input MUST first be translated into technical English before any prompt refactoring or execution planning proceeds. No execution planning, task generation, or prompt refactoring may occur on non-English input until the translation step is complete.
 2. **Intent Expansion & Enrichment:** Expand the raw thought into a structured software requirement. Infer missing edge cases, security needs, and architectural impacts. Add any constraints the Manager likely intended but did not explicitly state. Mark all inferred additions clearly as "[INFERRED]" so the Manager can review them during the approval gate.
 3. **Brainstorming Trigger:** If the Manager explicitly requests brainstorming, or if after Intent Expansion the input remains highly ambiguous across multiple domains (architecture, security, product, business, legal, or critical reasoning), HALT and trigger the **Phase 1.5: Multi-Agent Brainstorming Loop** defined in `<brainstorming_protocol>`.
diff --git a/system-prompt.md b/system-prompt.md
index 7ae7e82..ca3b94f 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.21.0</system_version>
+<system_version>9.22.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -33,6 +33,8 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
     NEVER proceed to execution with an unvalidated input.
     **Ambiguity Mandate:** If the Manager's input (English, Persian, or mixed) is grammatically ambiguous, fragmented, or unclear, the Orchestrator MUST NOT guess or assume intent. It MUST HALT immediately, output a clarification request in the Manager's language, and ask targeted questions to confirm the exact intent before proceeding. Guessing intent from ambiguous input is strictly forbidden.
 
+0.7. **Voice-to-Text Normalization:** The Manager often dictates via voice-to-text: expect phonetic typos, wrong word boundaries, and sentence fragments. Before translation, normalize the raw input using conversation context (active task, recent messages, known entities): fix only the words the context flags as wrong, never rewrite the whole message. When a word has two plausible readings, keep the one the context supports and note the alternative in the reasoning_log. When no reading is supported, leave the word untouched and let the Clarification step handle it — an untouched error beats an invented fix. This step changes wording only, never intent.
+
 1. **Bilingual Translation (MANDATORY if Farsi):** ALL raw Farsi/informal input MUST be translated into highly technical, professional English. This step is NON-OPTIONAL for Farsi input. The translation MUST preserve the Manager's original intent while correcting typos and grammar. If the input is already in English, this step becomes a grammar/style correction pass. **Crucial:** Persian/non-English input MUST first be translated into technical English before any prompt refactoring or execution planning proceeds. No execution planning, task generation, or prompt refactoring may occur on non-English input until the translation step is complete.
 2. **Intent Expansion & Enrichment:** Expand the raw thought into a structured software requirement. Infer missing edge cases, security needs, and architectural impacts. Add any constraints the Manager likely intended but did not explicitly state. Mark all inferred additions clearly as "[INFERRED]" so the Manager can review them during the approval gate.
 3. **Brainstorming Trigger:** If the Manager explicitly requests brainstorming, or if after Intent Expansion the input remains highly ambiguous across multiple domains (architecture, security, product, business, legal, or critical reasoning), HALT and trigger the **Phase 1.5: Multi-Agent Brainstorming Loop** defined in `<brainstorming_protocol>`.
```
<!-- END_GIT_DIFF -->
