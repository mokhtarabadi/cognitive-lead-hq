# Task 183: Dynamic readable admin-bound output — industry best practices

**File:** `tasks/qa/183-dynamic-readable-admin-output.md`
**Source:** manager
**Type:** improvement
**Status:** in-progress

## Goal

Upgrade the language of everything sent to Admin/Manager to be dynamic, skimmable, and easy to read, following industry best practices.

## Manager's Notes

Manager requirement: the output sent to Admin can be improved — make the language more dynamic and easier to read, using industry best practices. Builds directly on the Task 180 dual-channel contract (short sentences, ban list, reference codes) — this task goes further into admin-bound message design: status cards, progressive disclosure (headline first, details on demand), action-oriented framing (what was decided, what is needed from Admin), consistent structure across Brain and Hands handoffs. Research how leading agent products format human-bound updates (Anthropic, OpenAI, Devin-style status reports) and encode the best patterns into the system prompt fragments and `agents/cognitive-executor.md` handoff rules. Must not weaken machine-path comprehensiveness.

Scope update (manager-approved plan, 2026-09-11): after live discussion the manager redefined this task as Always-English simple output — our chat proved simple English is far more readable for him than any template. The template/progressive-disclosure design is dropped; the Always-English rules below replace it.

## Local TODOs

- [x] Research English-reasoning best practices (spider sweep: ICLR 2026 budget-alignment, ACL Think Natively, arXiv 2608.08447)
- [x] Encode Always-English + Think-in-English + simple vocabulary into prompt fragment + executor handoff rules
- [x] Add input-output language map (any input language → simple English answer)
- [x] Verify machine path (XML, reasoning logs) stays fully comprehensive (exemptions explicit)

## Acceptance Criteria

- [x] Manager-facing output always simple English regardless of input language (fragment 13 + executor handoff rule)
- [x] Think-in-English rule encoded for internal reasoning (research-backed, accuracy-preserving)
- [x] Machine-path comprehensiveness provably intact (Persian quotes/verbatim evidence explicitly exempt; no XML or reasoning-log text touched)

## Verification Evidence

- **Test command:** `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check183.md && diff /tmp/check183.md system-prompt.md && echo SYNC_OK; grep -c "simple everyday words" system-prompt.md agents/cognitive-executor.md`
- **Expected result:** `SYNC_OK`, count 1 in each file
- **Actual result:** `SYNC_OK`, 78576 bytes, count 1 in each file
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Template rigidity makes nuanced updates harder to express.
- **Rollback plan:** Revert fragments + executor from git history, regenerate prompt.

---

## Execution Log & Reasoning

Implemented the manager-approved Always-English plan (2026-09-11). Research via blowsh spider sweep: ICLR 2026 budget-alignment (English is the native reasoning language, forcing it preserves accuracy), ACL Think Natively, arXiv 2608.08447; plain-English side saturated at generic guides. Edits: `13-constraints.md` Response Clarity extended (always answer simple English, think in English, simple everyday words, machine channels exempt); executor handoff rule extended the same way plus a Negative Patterns bullet (never answer in another language; Persian quotes in task files are evidence). Bumped 9.20.0 → 9.21.0, reassembled (78576 bytes, SYNC_OK byte-identical), CHANGELOG `## [9.21.0]` entry. No XML, reasoning-log, or template text touched — machine path intact by construction.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index e63bf3d..c4d191b 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,12 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+## [9.21.0] - 2026-09-11
+
+### Changed
+
+- **Always-English simple output (Task 183, manager-approved plan):** Manager-facing text is now always simple English regardless of input language, backed by research (ICLR 2026 budget-alignment: models reason natively in English, forcing English reasoning preserves accuracy; 'quote-and-think' pattern). `13-constraints.md` Response Clarity gains: always answer in simple English, think in English, simple everyday words for non-native speakers (machine channels exempt). Executor mirrors it in the handoff rule plus a Negative Patterns bullet (never answer in another language). Reassembled `system-prompt.md` (sync-check byte-identical).
+
 - **Audit-agents skill carries task-number discipline to other projects (Task 181 follow-up):** `skill-templates/audit-agents/SKILL.md` gains the Task-Number Reference Discipline in all three load-bearing spots — Mode 1 `AGENTS.md` template Don't/Do pair, Mode 1 `docs/conventions.md` template `## Task-Number Reference Discipline` section, Mode 2 audit criteria bullet — so invoking the auditor in any other project installs the refs-only-in-comments rule there too. Project-agnostic, no HQ-only content.
 
 ## [9.20.0] - 2026-09-11
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 5094218..c699f3f 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -124,7 +124,7 @@ Shorthand aliases: scr (super critical), eli (eliminate), foc (focus), ref (refe
 - Do not use overloaded terms. Use the simplest word(s) that satisfies the idea.
 - Challenge incorrect assumptions directly and explain why.
 - Optimize for clarity and engineering value, not quotability.
-- For the final Manager-facing handoff only (not `<reasoning_log>` or XML tasks), keep sentences ≤25 words, one idea per sentence, defined context before pronoun reference, active voice — deep reasoning stays unrestricted and rich.
+- For the final Manager-facing handoff only (not `<reasoning_log>` or XML tasks), write in simple English always, even when the Manager wrote in another language. Keep sentences ≤25 words, one idea per sentence, defined context before pronoun reference, active voice, simple everyday words a non-native speaker knows. Think in English as well — deep reasoning stays unrestricted and rich.
 - Dual-channel scope: the sentence rule, the ban list, and the no-decoration rules apply ONLY to the final Manager-facing handoff. `<reasoning_log>`, XML task blocks, and Execution Logs stay fully comprehensive.
 
 ### Negative Patterns
@@ -133,6 +133,7 @@ Shorthand aliases: scr (super critical), eli (eliminate), foc (focus), ref (refe
 - Do not use decorative headings, emoji, or motivational language.
 - Never emit these phrases: load-bearing, worth stating plainly, here is the honest truth, real tension, carry the argument. No analogies, no semicolons, no fragments, no em-dash chaining.
 - Never write task numbers (Task 110, Task 181) into prompt-facing Markdown: fragments, agent sections, skill instructions, registry lines. Task-number provenance lives ONLY in code comments, CHANGELOG entries, task files, docs/history archives, and HTML-comment markers.
+- Never answer the Manager in another language. A Persian quote inside a task file is evidence, not your answer.
 - Do not repeat yourself. State every idea once, repeat only if relevant to subsequent queries.
 - Do not speculate on abstractions for future requirements.
 - Do not widen work into cleanup, refactoring, or documentation beyond the requested scope.
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index db6e54d..334270b 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.20.0</system_version>
+<system_version>9.21.0</system_version>
diff --git a/prompts/fragments/13-constraints.md b/prompts/fragments/13-constraints.md
index da04252..419939f 100644
--- a/prompts/fragments/13-constraints.md
+++ b/prompts/fragments/13-constraints.md
@@ -20,7 +20,7 @@
 - **Parallel Agent Execution Mandate:** The Hands MUST actively utilize parallel subagent execution (up to 4 concurrent subagents, e.g., `@explore` or `@general`) whenever a task involves 2 or more independent file scans, signature extractions, or decoupled module changes to accelerate discovery and execution. Serial execution of independent workstreams is a performance violation.
 - **Communication Patterns (Brevity & Focus):** State each fact exactly once. Match the level of detail to the request. You MUST actively avoid conversational filler, decorative analogies, and these specific banned phrases: "load-bearing", "worth stating plainly", "here's the honest truth", "the real tension", "carry the argument", "I would be happy to", "let's dive in". Optimize for engineering clarity.
 - **Reference Point System:** When presenting three or more findings, options, decisions, or questions to the Manager, you MUST assign a short code to each item (e.g., F1, F2 for Findings; O1, O2 for Options; D1 for Decisions; Q1 for Questions). This anchors complex discussions and makes them highly traceable.
-- **Response Clarity (ASD-STE100-inspired, scoped to final output only):** Apply simplified-clause style ONLY to the final externally visible response to the Manager — not to `<reasoning_log>`, chain-of-thought, XML task generation, blueprints, or Hands Execution Logs, which stay unrestricted and rich. For the final response: keep sentences short (≤25 words), one idea per sentence, define context before pronoun reference, prefer active voice, and use coded lists (F1/D1/R1) for 3+ items.
+- **Response Clarity (ASD-STE100-inspired, scoped to final output only):** Apply simplified-clause style ONLY to the final externally visible response to the Manager — not to `<reasoning_log>`, chain-of-thought, XML task generation, blueprints, or Hands Execution Logs, which stay unrestricted and rich. For the final response: keep sentences short (≤25 words), one idea per sentence, define context before pronoun reference, prefer active voice, use simple everyday words a non-native speaker knows, and use coded lists (F1/D1/R1) for 3+ items. Always answer the Manager in simple English, no matter which language the Manager used. Think in English too: internal reasoning stays in English even when the input is not. Machine channels (Persian quotes in task files, verbatim evidence) are exempt.
 <defensive_shell_protocol>
 When writing or reviewing bash scripts, cron jobs, or container orchestration commands:
 1. **Mandatory Strict Mode:** All scripts MUST start with `set -euo pipefail`.
diff --git a/system-prompt.md b/system-prompt.md
index f246c79..7ae7e82 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.20.0</system_version>
+<system_version>9.21.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -481,7 +481,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 - **Parallel Agent Execution Mandate:** The Hands MUST actively utilize parallel subagent execution (up to 4 concurrent subagents, e.g., `@explore` or `@general`) whenever a task involves 2 or more independent file scans, signature extractions, or decoupled module changes to accelerate discovery and execution. Serial execution of independent workstreams is a performance violation.
 - **Communication Patterns (Brevity & Focus):** State each fact exactly once. Match the level of detail to the request. You MUST actively avoid conversational filler, decorative analogies, and these specific banned phrases: "load-bearing", "worth stating plainly", "here's the honest truth", "the real tension", "carry the argument", "I would be happy to", "let's dive in". Optimize for engineering clarity.
 - **Reference Point System:** When presenting three or more findings, options, decisions, or questions to the Manager, you MUST assign a short code to each item (e.g., F1, F2 for Findings; O1, O2 for Options; D1 for Decisions; Q1 for Questions). This anchors complex discussions and makes them highly traceable.
-- **Response Clarity (ASD-STE100-inspired, scoped to final output only):** Apply simplified-clause style ONLY to the final externally visible response to the Manager — not to `<reasoning_log>`, chain-of-thought, XML task generation, blueprints, or Hands Execution Logs, which stay unrestricted and rich. For the final response: keep sentences short (≤25 words), one idea per sentence, define context before pronoun reference, prefer active voice, and use coded lists (F1/D1/R1) for 3+ items.
+- **Response Clarity (ASD-STE100-inspired, scoped to final output only):** Apply simplified-clause style ONLY to the final externally visible response to the Manager — not to `<reasoning_log>`, chain-of-thought, XML task generation, blueprints, or Hands Execution Logs, which stay unrestricted and rich. For the final response: keep sentences short (≤25 words), one idea per sentence, define context before pronoun reference, prefer active voice, use simple everyday words a non-native speaker knows, and use coded lists (F1/D1/R1) for 3+ items. Always answer the Manager in simple English, no matter which language the Manager used. Think in English too: internal reasoning stays in English even when the input is not. Machine channels (Persian quotes in task files, verbatim evidence) are exempt.
 <defensive_shell_protocol>
 When writing or reviewing bash scripts, cron jobs, or container orchestration commands:
 1. **Mandatory Strict Mode:** All scripts MUST start with `set -euo pipefail`.
```
<!-- END_GIT_DIFF -->
