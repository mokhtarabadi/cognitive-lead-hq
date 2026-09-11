# Task 188: Explicit voice-to-text input normalization pipeline (validate, normalize, translate, execute)

**File:** `tasks/in-progress/188-explicit-voice-text-input-normalization.md`
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

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
