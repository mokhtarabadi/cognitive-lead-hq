# Task 325: English Technical Terms in Handoffs

**File:** `tasks/completed/325-english-technical-terms-in-handoffs.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Enforce that non-English Manager-facing handoffs keep technical and programming keywords in English to avoid translation mistakes, in both the cognitive executor guidance and the assembled system prompt. No operating instruction may pin a specific language; all wording uses non-English and requested language only. META extension: fix unactionable skill references in the system prompt (Brain has no skill tool; only Hands does), strengthen the lint tool to catch these bug classes, and fix bundle_tasks bugs — all in this same task.

## META Scope (all in task 325, single QA gate, all-or-nothing)

### M1: Language generalization (done, QA_PASSED, review APPROVED twice)

### M2: Unactionable skill references (blueprint approved in principle, O3 reword-only direction pending final sign-off)

Brain has no skill tool, no file access, no web; only Hands (OpenCode) has the skill tool. Five instances: 05:31 Prompt Refactor Gate, 24:11 complexity gating, 11:13 Deep Research Loop with blowsh, 05:22 parenthetical, 21:45 passive task-generator. Direction: reword with explicit Hands actor, no skill-content injection (O3 beats O1 paraphrase and O2 port on cost vs unproven benefit; measurement gate before any prompt growth).

### M3: Lint strengthening (new)

Extend `mcp-lint-server` with checks that catch these bug classes mechanically: unactionable skill-verb check for prompt-facing prose (Brain-actor skill invocation without a Hands actor), plus bundle-task structural checks. Exact check list per final blueprint.

### M4: bundle_tasks bug fixes (new, audit of record)

Subagent audit plus baseline (7 passed via `uv run --project mcp-context-server --with pytest`): B1 stale META content on ID retry (`server.py` rebuild missing), B2 dead collision check (unpadded glob plus no-op pass), B3 non-atomic create (x-open then write), B4 silent dedup plus single-task accept vs 2-6 message, B5 duplicate-vs-missing conflated in `_find_task_file`, B6 lossy rollback (no cwd, no untracked fallback, swallowed errors, hardcoded backlog origin), B7 checklist extractor dead branch plus blank-line splits, B8 checksum gaps, B9 status regex single-word plus date-format drift, B10 test drift (T1 re-implements logic, T3 never invokes bundle_tasks). Fix per final blueprint priority; extend tests to cover fixed paths.

## Manager's Notes

Original request (Persian, verbatim evidence only): "یه تسک بساز برای زبان به cogntive و هم system prompot بکو کلمات تخصصی و فنی رو همیشه سعی کنه انگلیسی بشگه که مشکل در ترجمه باعث اشتباه نشه یعنی الان داری فارسی حرف میزنی با من کلمات تخصصی و کلید واژه های برنامه نویسی رو مثلا سعی کن انگلیسی بگی."

English translation: Create a task for language: tell cognitive and also system prompt to always keep specialized and technical words in English so translation issues do not cause mistakes; i.e. when speaking Persian with me, say specialized words and programming keywords in English.

Follow-up (verbatim evidence only): "دنبال کلمه فارسی یا farsi یا persian بگرد توی پروژه نباید روی زبان خاصی باشه باید بنویسه non english همه رو تغییر بده توی همین تسک و دوباره بفرست برای pipeline brain"

Follow-up translation: search the project for the words Persian, Farsi, and persian; nothing may target a specific language, everything must say non-English; change all of it under this same task and resend through the Brain pipeline.

Scope: update `prompts/fragments/24-language_policy.md` (and `20-communication_examples.md` if it shows handoff style) plus `agents/cognitive-executor.md` communication section, then rebuild `system-prompt.md` via `scripts/prompt-build/assemble_system_prompt.py` and verify sync. Keep reasoning and task file in English; only the final handoff may use the requested language with English technical terms preserved. Follow-up scope: generalize every Persian and Farsi mention in operating instructions (fragments 05, 13, 20, 24, `agents/cognitive-executor.md`, `docs/conventions.md`, `AGENTS.md`) to non-English and requested language; history archives and verbatim evidence quotes stay untouched. Second sweep: repo-wide grep found remaining operating-prose mentions in `skill-templates/telegram-issue-sync/SKILL.md`, `skill-templates/bundle-tasks/SKILL.md`, `README.md`, and a `Unicode/Persian` docstring in `mcp-context-server/gitops.py` — all generalized; `tests/test_bundle_tasks.py` and `test_session_lifecycle.py` keep Persian strings as Unicode test data (not language pinning); `docs/history`, `tasks/completed`, `tasks/.sessions`, `prompts/archive`, and `.opencode/memory` are records and stay untouched.

## Local TODOs

- [x] Inspect `prompts/fragments/24-language_policy.md` and communication examples
- [x] Inspect `agents/cognitive-executor.md` handoff wording rules
- [x] Add English-technical-terms rule with examples (task file, Brain turn, code, Git Diff stay English)
- [x] Generalize all Persian and Farsi mentions in operating instructions to non-English and requested language
- [x] Second sweep: generalize remaining mentions in skill templates, README, and gitops docstring
- [x] Rebuild system prompt and verify sync
- [x] Verify functionality
- [x] META audit: unactionable skill mentions plus lint gaps plus bundle_tasks bugs (done, findings in scope)
- [x] META blueprint: Brain plan plus critique loop until final
- [x] M2: reword 5 unactionable skill references with explicit actors
- [x] M3: strengthen mcp-lint-server with new mechanical checks
- [x] M4: fix bundle_tasks bugs plus extend tests
- [ ] Full verify (prompt sync plus bundle suite plus lint self-check), stage, qa_transition, Brain QA plus review

## Acceptance Criteria

- [x] Non-English handoffs keep technical terms (file paths, tool names, XML tags, code identifiers, Kanban terms) in English with no transliteration into the requested language
- [x] Zero Persian or Farsi mentions remain in operating instructions (`prompts/fragments`, `agents/cognitive-executor.md`, `docs/conventions.md`, `AGENTS.md`, `skill-templates/telegram-issue-sync`, `skill-templates/bundle-tasks`, `README.md`, `mcp-context-server/gitops.py`, assembled `system-prompt.md`); history archives, session transcripts, test data, and verbatim evidence quotes untouched
- [x] Zero unactionable skill references in Brain-owned fragments (every skill verb names Hands or states the no-tool boundary)
- [x] Lint catches the new bug classes mechanically (residual grep plus new lint checks green)
- [x] bundle_tasks fixes verified by extended tests (no pre-existing failures introduced)
- [x] Rule present in both fragment source and executor guidance, and assembled `system-prompt.md` contains it
- [x] `lint_system_prompt_sync` passes (no drift between fragments and assembled prompt)

## Verification Evidence

- **Test command:** rtk test uv run tests/test_prompt_sync.py -q
- **Expected result:** all prompt sync checks pass, assembled prompt matches fragments
- **Actual result:** exit 0, assembled 112600 bytes, Technical-Terms rule intact, all 14 checks pass; byte-identity rebuild confirmed (assemble twice, empty diff)
- **Exit code:** 0
- **Test command:** cd mcp-context-server && uv run --with pytest python -m pytest ../tests/test_bundle_tasks.py -q
- **Expected result:** 7 baseline green plus 11 new red-proof tests green after fixes
- **Actual result:** exit 0, 18 passed; red proof recorded first (9 failed on old code: count, duplicate, retry-stale, rollback-header, collision-helper, extractor, checksum, status, plus e2e-dry-run assertion fixed to section-gate line)
- **Exit code:** 0
- **Test command:** mcp-lint-server self-check (new gates on reworded fragments plus /tmp negative fixture, fixture removed)
- **Expected result:** reworded files pass, old wording fails with file-plus-line citation
- **Actual result:** 4 reworded fragments pass with zero issues via lint_markdown; a negative fixture carrying the old blowsh wording fires Unactionable skill reference (line 1) via both lint_markdown and lint_system_prompt_sync; META gate passes non-META files and flags broken META; fixture deleted after run. Note: the live MCP singleton still serves pre-change lint code until redeployed — direct function runs above use the edited file.
- **Exit code:** 0
- **Stack-skill binding:** root=. markers=[package.json, go.mod, pyproject.toml server, build.gradle.kts] matched=[] reason=prompt prose plus Python MCP change, no app stack skill matches

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Overly broad wording could force English into places where the requested language is required by the Manager.
- **Risk (META):** Lint false positives on quoted Hands examples — mitigated by Hands-window, fence, marker, and registry exemptions; bundle behavior changes are covered by 18 tests.
- **Rollback plan:** Revert fragment and executor edits via git, rebuild system prompt, re-run sync check. META: revert `mcp-lint-server/server.py` + `mcp-context-server/{server,bundle,gitops}.py` + tests; prior behavior returns; never commit.

---

## Execution Log & Reasoning

Seat Check: docs-only prompt language policy change, single domain, requested Software Architect, skipped Designer and Senior Programmer (no trigger words in title plus body). Brainstorm: not required, single domain and reversible via git.
Fed-context: `prompts/fragments/24-language_policy.md:1` (policy file exists), `prompts/manifest.txt:23` (manifest already lists 24), `agents/cognitive-executor.md:161` (handoff bullet updated), `prompts/fragments/20-communication_examples.md:34` (handoff line governs examples), `scripts/prompt-build/assemble_system_prompt.py:372` (assemble entrypoint).
Changes: added Technical-Terms rule section to 24-language_policy.md, added Technical-Terms bullet to executor Communication Patterns, appended Example 4 to 20-communication_examples.md, rebuilt system-prompt.md (112374 bytes, rule at line 830). Manifest needed no change. Assumption A1: existing 20 file governs handoffs so one example is appropriate. Sibling docs inspected: prompts/fragments README/DECISIONS and agents README/DECISIONS carry no contract change for this wording rule, logged no-change.
QA: QA_PASSED with two non-blocking notes (sync test pins no drift only, Example 4 descriptive). Review: APPROVED with PO_REVIEW_PENDING, no blocking issues.
Follow-up: generalized every Persian and Farsi mention in operating instructions to non-English and requested language across fragments 05, 13, 20, 24, `agents/cognitive-executor.md`, `docs/conventions.md`, and `AGENTS.md`; rebuilt `system-prompt.md` (112269 bytes); grep confirms zero remaining matches in all six surfaces; history archives and verbatim evidence quotes intentionally untouched. Assumption A2: deployment default fallback needs no named language; per-message detection governs. Resending through Brain QA and review pipeline.
Re-QA: QA_PASSED, zero specific-language pinning in operating instructions, Technical-Terms rule intact, sync green. Re-review: APPROVED with PO_REVIEW_PENDING, no blocking issues; follow-up suggestions are deployment-default definition and pinning asserts.
Second sweep: repo-wide grep surfaced remaining operating-prose mentions in `skill-templates/telegram-issue-sync/SKILL.md` (verbatim section headers, translation steps, integrity table), `skill-templates/bundle-tasks/SKILL.md` (Unicode slug line), `README.md` (clarification-halt mandate), and `mcp-context-server/gitops.py` (`_kebab_case` docstring) — all generalized to non-English and requested language. Deliberately untouched: `tests/test_bundle_tasks.py` and `tests/test_session_lifecycle.py` Persian strings (Unicode test data, not language pinning), `docs/history`, `tasks/completed`, `tasks/.sessions`, `prompts/archive`, `.opencode/memory`, `.pytest_cache` (records, transcripts, caches). Sibling docs inspected: `mcp-context-server/README.md` and `DECISIONS.md` carry no contract change for a docstring edit, logged no-change. Assumption A3: example slug `تست-باندل` stays as functional sample data. Resending through Brain QA and review pipeline.
Second-sweep QA: QA_PASSED, no residual pinning in operating prose, test data and archives correctly untouched. Second-sweep review: APPROVED with PO_REVIEW_PENDING, no blocking issues; follow-ups are deployment-default definition and pinning asserts.
META: Brain plan (Architect plus Senior Programmer) plus critique loop reached FINAL with 7 resolved debatables. M2 applied 5 O3 rewords with Orchestrator-scoped no-tool boundary (fragments 05, 11, 21, 24). M3 added `_check_unactionable_skill_verbs` (fragment-scoped, registry-exempt, Hands-window plus fence plus marker exemptions) wired into `lint_markdown` and `lint_system_prompt_sync`, plus `_check_bundle_meta_structure` (META-only) wired into `lint_task_file`; backtick-blindness in the verb regex caught and fixed during self-test; ADRs recorded in both slice DECISIONS. M4 fixed B1 (rebuild after final ID, atomic create-plus-write), B5 (distinct locate states), B6 (byte-identical restore to recorded origin, surfaced errors), B2 (padded plus bare collision helper), B3 (atomic write), B4 (2-6 floor plus duplicate-input error), B7 (blank-line paragraphs, stripped nested boxes, dead branch removed), B8 (no length gate), B9 (full-line status, aligned datetime); red proof recorded with 9 failing tests on old code, then 18 passed. Locked runner used throughout (`cd mcp-context-server && uv run --with pytest`); `test_mcp_servers.py` failures are environmental (missing pathspec/yaml) plus one pre-existing split round-trip failure also failing on pristine HEAD. Assumption A4: hand-created same-ID files are ambiguous by definition, so collision is an error, not a warning.
META QA: QA_PASSED — zero unactionable verbs and zero language pinning in operating prose, lint gates fire on old wording and pass on rewords with non-META unaffected, 18 bundle tests green with red proof, sync green with byte-identity rebuild. META review: APPROVED with PO_REVIEW_PENDING, no blocking issues; QA notes ride as follow-ups (file-level boundary masking, fragments README/DECISIONS future false-positive, META gate non-empty vs verbatim).
Manager accept 2026-10-19: 'Approved for closure' — PO_REVIEW_PENDING cleared, closing per protocol.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/AGENTS.md b/AGENTS.md
index 62c6f87..abd2036 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -5,7 +5,7 @@
 The very first file the agent MUST read before performing any task is `AGENTS.md`.
 This file acts as the primary router. You MUST load and read the following documents first before executing any code changes to guarantee 100% structural and stylistic alignment:
 
-1. `DESIGN.md` — Enforces colors, typography, layout scale, component styling, and RTL Persian configurations.
+1. `DESIGN.md` — Enforces colors, typography, layout scale, component styling, and RTL language configurations.
 2. `docs/architecture.md` — Defines project structure, layer boundaries, and key data flow policies.
 3. `docs/data_model.md` — Defines database entities, schemas, pointers, and object relationships.
 4. `docs/conventions.md` — Defines syntax rules, naming conventions, file boundaries, and localization paths.
@@ -47,7 +47,7 @@ This repository is the Headquarters for the Cognitive Lead AI multi-agent system
   -> **Do** follow the Universal Financial Ledger Standard: snapshot-on-write, `$ifNull` precedence, discrepancy alerting, deep config merging. See `docs/conventions.md`.
 - **Don't** carry over assumptions, partial results, or architectural hypotheses from a previous task.
   -> **Do** flush context and treat every task as contextually independent (Buffer Isolation directive in validation-phase). Flushing covers working execution assumptions only — the Brain session thread persists across tasks under the active session ID (`brain_turn(session_id=...)`), so conversational context survives task boundaries while each task is still judged on its own evidence.
-- **Don't** execute raw, informal, or non-English (Farsi) prompts directly.
+- **Don't** execute raw, informal, or non-English prompts directly.
   -> **Do** ALWAYS process through the Input Validation Pipeline first: Validate → Translate → Enrich → Refactor → Execute. If the input is unclear, HALT and request clarification. NEVER proceed to task generation with unvalidated input. (Note: If you receive a standard XML task block, skip this and execute normally).
 - **Don't** attempt to resolve cross-disciplinary ambiguity within a single persona.
   -> **Do** trigger the Multi-Agent Brainstorming Loop if the Manager explicitly requests brainstorming or a task exhibits cross-disciplinary ambiguity. Interpret the `<brainstorming_session>` results in backlog tasks as non-functional guidelines that govern execution.
diff --git a/CHANGELOG.md b/CHANGELOG.md
index f491ebe..4f68a96 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -7,6 +7,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 ## [Unreleased]
 
 ### Added
+- **English technical terms in non-English handoffs:** `prompts/fragments/24-language_policy.md` gains a Technical-Terms rule (file paths, tool names, XML tags, identifiers, Kanban lanes, verdict literals stay English in backticks, approval literals matched English-only); `agents/cognitive-executor.md` and `prompts/fragments/20-communication_examples.md` carry the same rule with a correct versus transliterated example; all Persian and Farsi mentions in operating instructions (fragments 05, 13, 20, 24, executor, `docs/conventions.md`, `AGENTS.md`, both Telegram and bundle skill templates, `README.md`, `mcp-context-server/gitops.py` docstring) generalized to non-English and requested language; `system-prompt.md` rebuilt.
+- **Unactionable skill references fixed (same task):** five Brain-owned fragment lines reworded with explicit Hands actors and Orchestrator no-tool boundaries (05 gate plus parenthetical, 24 gating, 11 Deep Research Loop routed to Hands, 21 task-generator actor); zero prompt growth.
+- **Lint mechanically catches the new bug classes (same task):** `_check_unactionable_skill_verbs` in `lint_markdown` (fragment-scoped) and `lint_system_prompt_sync`, plus `_check_bundle_meta_structure` (META-only) in `lint_task_file`.
+- **Bundle hardening (same task, B1-B10):** ID-retry rebuild with atomic create-plus-write, byte-identical rollback to recorded origins, distinct duplicate-vs-missing-vs-archived states, padded plus bare collision detection, 2-6 floor with duplicate-input errors, extractor paragraph preservation, full-coverage checksums, full-line status replacement with aligned dates; 11 new red-proof tests, 18 passed total.
 - **Project Skills table in AGENTS.md (Task 323):** the `audit-agents` template now mandates a scan-and-table condition on every audit (scan `.opencode/skills/*/SKILL.md`, rebuild the table with name plus trigger plus duty; missing table and stale rows fail the audit); root `AGENTS.md` backfilled with the `sop-maintenance` row; `tests/test_skill_registry.py` enforces table presence, row-count match, and stale-row failure.
 
 - **Language policy: English inside, requested language outside (Task 322):** new `prompts/fragments/24-language_policy.md` (translate-first with complexity gating, per-message detection with Persian default, English-only internals plus Brain turns, approval literals English-only) wired via `prompts/manifest.txt`; fragments 05 (clarification in requested language), 13 (Cognitive Rule plus Output Style item 6 plus Approval Literals Guard), and 20 (handoff-language line) updated; `agents/cognitive-executor.md` Direct Input plus handoff plus Negative Patterns updated with approval gates untouched; `docs/conventions.md` clarification halt aligned; both sync tests updated (pin 9.61.0, new wording asserts, approval-English test). Bumped `<system_version>` 9.60.1 to 9.61.0 with byte-identical re-assemble. Note: `split_system_prompt.py` rewrites fragments from the prompt and drops unassembled files, so round-trip verification uses assemble-twice diff, never split.
diff --git a/README.md b/README.md
index 06ab0f2..bedddb7 100644
--- a/README.md
+++ b/README.md
@@ -491,7 +491,7 @@ Three plugins: **`smart-compact`** (`@mokhtarabadi/opencode-smart-compact`) —
 
 ## Key V9.1 Changes
 
-- **Clarification Halt Mandate:** If the Manager's input (English, Persian, or mixed) is ambiguous, fragmented, or unclear, the Orchestrator and Hands MUST HALT immediately, output a clarification request, and ask targeted questions. Guessing intent from unclear input is strictly forbidden.
+- **Clarification Halt Mandate:** If the Manager's input (English, non-English, or mixed) is ambiguous, fragmented, or unclear, the Orchestrator and Hands MUST HALT immediately, output a clarification request, and ask targeted questions. Guessing intent from unclear input is strictly forbidden.
 - **Goal-Oriented Task Treatment:** Software Architect and Senior Programmer personas now explicitly instruct Hands to load all relevant skills from `<agent_skills_registry>` and treat multi-step/large tasks as Goal units with explicit verification gates.
 - **Parallel Agent Execution Mandate:** Hands MUST actively utilize parallel subagent execution (up to 4 concurrent agents) for any task involving 2+ independent file scans, signature extractions, or decoupled module changes. Serial execution of independent workstreams is a performance violation.
 - **Input Validation Reinforced:** The `<user_input_processing>` fragment's Input Validation Gate, Bilingual Translation, and Clarification steps have been strengthened with explicit Ambiguity Mandate, Clarification Halt Mandate, and translation-before-execution rules.
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 40d02bf..ca3f2b3 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -80,7 +80,7 @@ If the Orchestrator or Manager forgets to explicitly list a skill in the `<conte
 
 If the Manager sends you a direct message that is NOT an XML task block (e.g., "fix the login bug on Android"), you MUST execute this validation pipeline before writing any code:
 
-1. **Intent Validation:** Confirm the language is English. If non-English (any language), translate to technical English internally. **Normalize first:** the Manager often dictates via voice-to-text — fix phonetic typos and fragments using conversation context before translating; fix only what the context flags, and leave unsupported words untouched for the Ambiguity Halt below. **Ambiguity Halt:** If direct input from the Manager is ambiguous, fragmented, or unclear, the Hands MUST HALT immediately and ask for clarification in the per-message requested language (Persian default) rather than executing speculative commands. Guessing intent from unclear input is strictly forbidden.
+1. **Intent Validation:** Confirm the language is English. If non-English (any language), translate to technical English internally. **Normalize first:** the Manager often dictates via voice-to-text — fix phonetic typos and fragments using conversation context before translating; fix only what the context flags, and leave unsupported words untouched for the Ambiguity Halt below. **Ambiguity Halt:** If direct input from the Manager is ambiguous, fragmented, or unclear, the Hands MUST HALT immediately and ask for clarification in the per-message requested language rather than executing speculative commands. Guessing intent from unclear input is strictly forbidden.
 2. **Task File Enforcement:** You MUST ask the Manager: "This is an ad-hoc request. Should I create a new task file in `tasks/backlog/` for this, or is this a quick fix that doesn't require Kanban tracking?"
 3. **Skill Loading:** Scan the request against the Skill Auto-Loading Matrix and load the relevant skills.
 4. **Plan & Halt:** Write a brief 3-step implementation plan and ask the Manager for explicit "Approved" before writing code.
@@ -158,8 +158,9 @@ Shorthand aliases: scr (super critical), eli (eliminate), foc (focus), ref (refe
 - Challenge incorrect assumptions directly and explain why.
 - Optimize for clarity and engineering value, not quotability.
 - Lead with the answer. Open the reply with the result or the direct answer, then the reasoning. A short answer stays prose: no heading, no process narration, no recap.
-- For the final Manager-facing handoff only (not `<reasoning_log>` or XML tasks), write in the per-message requested language (Persian default for this Manager), even when the Manager wrote in another language. Answer first, then the reason, then the next action. Budget the length: a short reply is 2–5 sentences with no heading, a normal reply is 80–180 words or at most 5 bullets. Treat 25 words as a ceiling for any single sentence, never a target. Prefer prose; use flat bullets only for 3–7 parallel items and a table only for repeated attributes. Never nest lists. Think in English as well — deep reasoning stays unrestricted and rich.
+- For the final Manager-facing handoff only (not `<reasoning_log>` or XML tasks), write in the per-message requested language, even when the Manager wrote in another language. Answer first, then the reason, then the next action. Budget the length: a short reply is 2–5 sentences with no heading, a normal reply is 80–180 words or at most 5 bullets. Treat 25 words as a ceiling for any single sentence, never a target. Prefer prose; use flat bullets only for 3–7 parallel items and a table only for repeated attributes. Never nest lists. Think in English as well — deep reasoning stays unrestricted and rich.
 - Dual-channel scope: the sentence rule, the ban list, and the no-decoration rules apply ONLY to the final Manager-facing handoff. `<reasoning_log>`, XML task blocks, and Execution Logs stay fully comprehensive.
+- Technical terms stay English in non-English handoffs (Technical-Terms rule). Keep file paths, tool names, XML tag names, code identifiers, Kanban lane names, and verdict literals in English with no transliteration into the requested language. Reasoning stays English. A non-English sentence keeps each English term intact in backticks, for example a status line naming `tasks/qa/example.md` and `lint_task_file` without translating either term.
 
 ### Negative Patterns
 
diff --git a/docs/conventions.md b/docs/conventions.md
index f3084c7..210ee91 100644
--- a/docs/conventions.md
+++ b/docs/conventions.md
@@ -150,9 +150,9 @@ Serial execution of independent workstreams is a performance violation. The para
 
 ### Input Validation Pipeline
 
-All Manager input — English, Persian, or mixed — MUST pass through the Input Validation Pipeline before any execution:
+All Manager input — English, non-English, or mixed — MUST pass through the Input Validation Pipeline before any execution:
 
-1. **Language detection** (English, Farsi, mixed)
+1. **Language detection** (English, non-English, mixed)
 2. **Typo/hallucination detection** (misspellings, nonsensical words)
 3. **Clarity check** (core intent identifiable with confidence)
 4. **Completeness check** (enough context to form a requirement)
@@ -162,15 +162,15 @@ All Manager input — English, Persian, or mixed — MUST pass through the Input
 If any validation step FAILS — particularly the clarity check — the Orchestrator and Hands MUST:
 
 1. **HALT immediately.** Do NOT guess, assume, or fabricate intent from ambiguous input.
-2. **Output a clarification request** in the per-message requested language (Persian default), no matter which language the input used.
+2. **Output a clarification request** in the per-message requested language, no matter which language the input used.
 3. **Ask targeted questions** to confirm the exact intent before proceeding.
 4. **Only resume** after the Manager provides an unambiguous response.
 
 Guessing intent from ambiguous, fragmented, or unclear input is strictly forbidden at every level of the system (Orchestrator, personas, and Hands).
 
-### Persian/Non-English Translation
+### Non-English Translation
 
-All Persian/non-English input MUST first be translated into technical English before any prompt refactoring, task generation, or execution planning proceeds. No execution may occur on non-English input until the translation step is complete.
+All non-English input MUST first be translated into technical English before any prompt refactoring, task generation, or execution planning proceeds. No execution may occur on non-English input until the translation step is complete.
 
 ## MCP Environment Loading & Blank-Means-Unset Convention
 
diff --git a/mcp-context-server/DECISIONS.md b/mcp-context-server/DECISIONS.md
index 529bfc1..e2ae8f4 100644
--- a/mcp-context-server/DECISIONS.md
+++ b/mcp-context-server/DECISIONS.md
@@ -62,3 +62,10 @@
 - **Decision:** Add opt-in `skip_add: bool = False` to `stage_and_inject_diff`: when true, skip the `git add` step entirely and only extract + inject (caller owns the whole index, task file included). On the default path, snapshot `git diff --cached --name-only` for the listed files before adding and append a warning naming files with pre-existing staged state. Document the whole-file contract in the tool docstring. `qa_transition` shares the pattern but its `git mv` interplay is out of scope (follow-up).
 - **Consequences:** Index-safe flows sequence hunk surgery before the call with `skip_add=True`; default callers get a loud warning instead of silent overwrite. Signature change is trailing-optional, fully backwards compatible.
 - **Rollback:** Revert `server.py` + tests; redeploy singleton.
+
+## [2026-10-19] ADR-010: Bundle Hardening (ID Retry, Rollback, Validation)
+
+- **Context:** Audit of `bundle_tasks` found data-loss defects: stale META body after ID retry, lossy rollback (hardcoded backlog origin, guessed headers, swallowed errors), duplicate-vs-missing conflation, non-atomic create, dead collision check, silent input dedup, extractor dead branch, checksum length gate, single-word status regex.
+- **Decision:** Rebuild META body after final ID allocation with atomic exclusive-create-plus-write; rollback restores byte-identical originals to recorded origins via `_git_mv_or_fallback` with surfaced errors; `_locate_task_file` returns distinct ok/duplicate/archived/missing states; `_next_id_collision` checks padded and bare spellings; requests enforce 2-6 tasks with explicit duplicate-input errors; extractor preserves blank-line paragraphs and strips nested boxes; checksum covers all non-empty criteria; status replacement spans the full line with Created-aligned datetime.
+- **Consequences:** Same tool surface, stricter errors, 11 new tests (red-proof first) green alongside the 7 baseline tests.
+- **Rollback:** Revert `server.py`, `gitops.py`, `bundle.py` touchpoints + tests; prior behavior returns.
diff --git a/mcp-context-server/gitops.py b/mcp-context-server/gitops.py
index ea7c712..b70d5bc 100644
--- a/mcp-context-server/gitops.py
+++ b/mcp-context-server/gitops.py
@@ -80,7 +80,7 @@ DIFF_SIZE_WARNING_THRESHOLD = 400
 
 
 def _kebab_case(text: str) -> str:
-    """Convert arbitrary title to kebab-case slug (B4: supports Unicode/Persian)."""
+    """Convert arbitrary title to kebab-case slug (B4: supports Unicode)."""
     import unicodedata
 
     normalized = unicodedata.normalize("NFKD", text)
@@ -109,7 +109,14 @@ def _discover_next_id(tasks_root: Path = Path("tasks")) -> int:
     return max_id + 1 if max_id else 1
 
 
-def _find_task_file(task_id: str, tasks_root: Path = Path("tasks")) -> Path | None:
+def _locate_task_file(task_id: str, tasks_root: Path = Path("tasks")):
+    """Locate a task ID across active Kanban dirs with distinct states.
+
+    Returns (state, payload): ("ok", Path) for exactly one active match,
+    ("duplicate", [Path, ...]) for >1 active match, ("archived", Path)
+    when only the archive holds it, ("missing", None) otherwise.
+    Distinct states keep duplicate IDs from being misreported as missing.
+    """
     norm = task_id.lstrip("0") or "0"
     candidates: list[Path] = []
     for d in ACTIVE_KANBAN_DIRS:
@@ -121,18 +128,26 @@ def _find_task_file(task_id: str, tasks_root: Path = Path("tasks")) -> Path | No
             if m and m.group(1).lstrip("0") == norm:
                 candidates.append(md)
     if len(candidates) == 1:
-        return candidates[0]
+        return ("ok", candidates[0])
     if len(candidates) > 1:
+        return ("duplicate", candidates)
+    # Check archive for a better error (already archived)
+    if (tasks_root / "archive").is_dir():
+        for md in (tasks_root / "archive").glob("*.md"):
+            m = re.match(r"^(\d+)-", md.name)
+            if m and m.group(1).lstrip("0") == norm:
+                return ("archived", md)
+    return ("missing", None)
+
+
+def _find_task_file(task_id: str, tasks_root: Path = Path("tasks")) -> Path | None:
+    state, payload = _locate_task_file(task_id, tasks_root)
+    if state == "ok":
+        return payload
+    if state == "duplicate":
         return None  # B2: hard halt — duplicate active IDs
-    # Check archive for better error (already archived)
-    for md in (
-        (tasks_root / "archive").glob("*.md")
-        if (tasks_root / "archive").is_dir()
-        else []
-    ):
-        m = re.match(r"^(\d+)-", md.name)
-        if m and m.group(1).lstrip("0") == norm:
-            return None
+    if state == "archived":
+        return None
     return None
 
 
@@ -155,29 +170,29 @@ def _format_task_id_list(ids: list[str]) -> str:
 
 
 def _extract_checklist_with_continuations(section_text: str) -> list[str]:
-    """B1: Extract checklist items with all indented continuation lines."""
+    """B1: Extract checklist items with all indented continuation lines.
+
+    A root or nested `- [ ]` line (column 0 or indented, stripped) starts a
+    new item. Plain indented lines continue the open item. Blank lines are
+    preserved as paragraph separators without closing the block — only a
+    `## ` heading or `---` rule ends it. The old dead branch (an unreachable
+    inner `- [` check) is removed.
+    """
     lines = section_text.splitlines()
     result: list[str] = []
     in_checklist = False
     for line in lines:
         stripped = line.strip()
-        is_root_bullet = line.startswith("- [")
-        if is_root_bullet:
+        if stripped.startswith("- ["):
             in_checklist = True
             result.append(stripped)
         elif in_checklist:
-            if (
-                stripped
-                and not line.startswith("- [")
-                and not stripped.startswith("## ")
-                and not stripped.startswith("---")
-            ):
-                result.append(line)
-            else:
+            if not stripped:
+                result.append("")
+            elif stripped.startswith("## ") or stripped.startswith("---"):
                 in_checklist = False
-                if line.startswith("- ["):
-                    in_checklist = True
-                    result.append(stripped)
+            else:
+                result.append(line)
     return result
 
 
@@ -224,11 +239,29 @@ def _verify_verbatim_checksums(
                 m = re.match(r"^- \[[ xX]\]\s*(.*)", stripped)
                 core = m.group(1) if m else stripped
                 prefixed = f"[{sid}] {core}"
-                if len(core) > 10 and prefixed not in bundled_text:
+                # No length gate: short criteria must be verified too.
+                if prefixed not in bundled_text:
                     return False
     return True
 
 
+def _next_id_collision(tasks_root: Path, next_id: int) -> list[Path]:
+    """Detect same-ID-different-slug files for a candidate NEXT_ID.
+
+    Checks both zero-padded (`06-*.md`) and bare (`6-*.md`) spellings,
+    since hand-created files are not always padded. A hit means the ID
+    allocation is ambiguous and the caller must abort or re-discover.
+    """
+    backlog = tasks_root / "backlog"
+    if not backlog.is_dir():
+        return []
+    padded = f"{next_id:02d}" if next_id < 100 else str(next_id)
+    hits: list[Path] = []
+    for prefix in {padded, str(next_id)}:
+        hits.extend(sorted(backlog.glob(f"{prefix}-*.md")))
+    return hits
+
+
 def _git_mv_or_fallback(src: Path, dst: Path) -> bool:
     dst.parent.mkdir(parents=True, exist_ok=True)
     repo = str(_repo_root(str(src)))
@@ -262,9 +295,11 @@ def _patch_archived_file(archive_path: Path, meta_id: str, meta_slug: str) -> No
         return
     new_file_header = f"**File:** `tasks/archive/{archive_path.name}`"
     content = re.sub(r"\*\*File:\*\*\s*`[^`]+`", new_file_header, content, count=1)
-    if re.search(r"\*\*Status:\*\*\s*\w+", content):
+    if re.search(r"\*\*Status:\*\*", content):
+        # Replace the whole status line: multi-word statuses
+        # (e.g. "in progress") must not leave remnants behind.
         content = re.sub(
-            r"\*\*Status:\*\*\s*\w+", "**Status:** superseded", content, count=1
+            r"\*\*Status:\*\*[^\n]*", "**Status:** superseded", content, count=1
         )
     else:
         content = re.sub(
@@ -277,7 +312,7 @@ def _patch_archived_file(archive_path: Path, meta_id: str, meta_slug: str) -> No
             content,
             count=1,
         )
-        timestamp = time.strftime("%Y-%m-%d")
+        timestamp = time.strftime("%Y-%m-%d %H:%M UTC")
         content = re.sub(
             r"(\*\*Superseded-By:\*\*\s*`[^`]+`)",
             rf"\1\n**Superseded-At:** `{timestamp}`",
@@ -286,7 +321,7 @@ def _patch_archived_file(archive_path: Path, meta_id: str, meta_slug: str) -> No
         )
     superseded_note = (
         f"> **Superseded:** This task was bundled into META task `{meta_id}-{meta_slug}` "
-        f"and archived on {time.strftime('%Y-%m-%d')}. "
+        f"and archived on {time.strftime('%Y-%m-%d %H:%M UTC')}. "
         f"See `tasks/backlog/{meta_id}-{meta_slug}.md` (or its Kanban successor) for the unified execution. "
         f"History preserved via `git log --follow -- tasks/archive/{archive_path.name}`.\n"
     )
diff --git a/mcp-context-server/server.py b/mcp-context-server/server.py
index f7813bf..b2513ef 100755
--- a/mcp-context-server/server.py
+++ b/mcp-context-server/server.py
@@ -131,6 +131,8 @@ from gitops import (
     _format_task_id_list,
     _git_mv_or_fallback,
     _kebab_case,
+    _locate_task_file,
+    _next_id_collision,
     _patch_archived_file,
     _repo_root,
     _verify_verbatim_checksums,
@@ -1295,7 +1297,15 @@ def bundle_tasks(
             if norm not in seen:
                 seen.add(norm)
                 deduped.append(tid)
+        if len(deduped) != len(cleaned_ids):
+            dupes = sorted(
+                {t for t in cleaned_ids if cleaned_ids.count(t) > 1},
+                key=lambda t: int(t),
+            )
+            return f"❌ Duplicate task IDs in request: {dupes}. Each ID may appear only once."
         task_ids = deduped
+        if len(task_ids) < 2:
+            return f"❌ Bundle needs 2-6 tasks, got {len(task_ids)}. Provide 2-6 numeric task IDs."
         if not title or not title.strip():
             return "❌ Error: title is required (e.g., 'android-polish-bundle')."
         title = title.strip()
@@ -1312,16 +1322,22 @@ def bundle_tasks(
         source_data: list[tuple[str, Path, str, str]] = []
         missing: list[str] = []
         for tid in task_ids:
-            p = _find_task_file(tid, tasks_root)
-            if p is None:
-                missing.append(tid)
-            else:
+            state, payload = _locate_task_file(tid, tasks_root)
+            if state == "ok":
+                p = payload
                 try:
                     c = p.read_text(encoding="utf-8")
                 except Exception as e:
                     return f"❌ Could not read {p} for task {tid}: {e}"
                 t = _extract_title(c)
                 source_data.append((tid, p, c, t))
+            elif state == "duplicate":
+                names = sorted(x.name for x in payload)
+                return f"❌ Duplicate task ID {tid} in active Kanban dirs: {names}. Resolve the duplication first — refusing to guess."
+            elif state == "archived":
+                missing.append(f"{tid} (already archived — see tasks/archive/)")
+            else:
+                missing.append(tid)
         if missing:
             return f"❌ Missing tasks (not found in active Kanban dirs): {missing}\n   Searched: {', '.join(ACTIVE_KANBAN_DIRS)} (archive excluded).\n   Hint: Check `ls tasks/backlog/ tasks/in-progress/ tasks/qa/ tasks/completed/ | grep {missing[0]}`"
         if not source_data:
@@ -1337,14 +1353,10 @@ def bundle_tasks(
         output_path = tasks_root / "backlog" / meta_filename
         if output_path.exists():
             return f"❌ Task ID collision: {output_path} already exists. Re-run ID discovery."
-        # Also check backlog glob for same ID prefix
-        if (
-            list((tasks_root / "backlog").glob(f"{next_id}-*.md"))
-            if (tasks_root / "backlog").is_dir()
-            else []
-        ):
-            # This would also match our not-yet-created file if we had a race, but we already checked exists
-            pass
+        clashes = _next_id_collision(tasks_root, next_id)
+        if clashes:
+            names = sorted(p.name for p in clashes)
+            return f"❌ Task ID collision: same-ID file(s) exist for next ID {next_id}: {names}. Re-run ID discovery."
 
         meta_title_full = title
         meta_content = _build_meta_content(
@@ -1412,36 +1424,38 @@ def bundle_tasks(
                 )
             return "\n".join(lines)
 
-        # --- B5: Atomic creation with retry loop ---
-        import subprocess as _sp
-
+        # --- B1+B3: Atomic create with retry; content rebuilt after final ID ---
+        # The META body embeds its own ID (title, headers, rollback note), so
+        # a retry that allocates a NEW id must rebuild the body — writing the
+        # pre-race body would leave a stale-ID file. Create + write happen in
+        # one exclusive open so a crash cannot leave an empty META file.
         MAX_ID_RETRIES = 5
+        meta_live = meta_content
         for attempt in range(MAX_ID_RETRIES):
             try:
                 output_path.parent.mkdir(parents=True, exist_ok=True)
                 with open(output_path, "x", encoding="utf-8") as f:
-                    pass  # Atomic creation
+                    f.write(meta_live)
                 break
             except FileExistsError:
-                # Re-discover next ID
+                # Re-discover next ID (a racer may have landed first)
                 next_id = _discover_next_id(tasks_root)
                 meta_id_str = f"{next_id:02d}" if next_id < 100 else str(next_id)
-                if next_id >= 100:
-                    meta_id_str = str(next_id)
                 meta_slug = _kebab_case(title)
                 meta_filename = f"{meta_id_str}-{meta_slug}.md"
                 output_path = tasks_root / "backlog" / meta_filename
+                if _next_id_collision(tasks_root, next_id):
+                    continue
+                meta_live = _build_meta_content(
+                    next_id, meta_slug, meta_title_full, task_ids, source_data
+                )
                 continue
+            except OSError as e:
+                output_path.unlink(missing_ok=True)
+                return f"❌ Failed to write META file {output_path}: {e}"
         else:
             return f"❌ Failed to find unique ID after {MAX_ID_RETRIES} attempts. Another process may be bundling concurrently."
 
-        # --- Write META content ---
-        try:
-            output_path.write_text(meta_content, encoding="utf-8")
-        except Exception as e:
-            output_path.unlink(missing_ok=True)
-            return f"❌ Failed to write META file {output_path}: {e}"
-
         out_lines = [f"✅ Created META task (MCP): {output_path} (bundles {task_ids})"]
 
         # --- B3: Archive sources with transactional rollback ---
@@ -1459,48 +1473,43 @@ def bundle_tasks(
                 out_lines.append(f"   ❌ Failed to archive {sid}: {src_path}")
 
         if failed:
-            # B3: Transactional rollback
+            # B6: Transactional rollback — restore byte-identical originals.
+            # source_data already carries each source's original bytes, so the
+            # restore rewrites them verbatim (File header + status included):
+            # no header guessing, no hardcoded backlog origin. Moves go through
+            # _git_mv_or_fallback (repo-rooted cwd + untracked fallback);
+            # every restore failure is surfaced, never swallowed.
+            restore_errors: list[str] = []
             for archived_path in archived:
                 original_name = archived_path.name
-                for _, src_path, _, _ in source_data:
-                    if src_path.name == original_name:
-                        restore_dst = src_path
-                        break
-                else:
-                    restore_dst = tasks_root / "backlog" / original_name
-                try:
-                    restore_dst.parent.mkdir(parents=True, exist_ok=True)
-                    _sp.run(
-                        ["git", "mv", str(archived_path), str(restore_dst)],
-                        check=True,
-                        capture_output=True,
-                    )
-                    # Remove superseded headers
-                    content = restore_dst.read_text(encoding="utf-8")
-                    content = re.sub(
-                        r"\n\*\*Superseded-By:\*\*.*$", "", content, flags=re.MULTILINE
-                    )
-                    content = re.sub(
-                        r"\n\*\*Superseded-At:\*\*.*$", "", content, flags=re.MULTILINE
-                    )
-                    superseded_pattern = re.compile(
-                        r"> \*\*Superseded:\*\*.*?History preserved.*?\n\n", re.DOTALL
+                match = next(
+                    (
+                        (src, text)
+                        for _, src, text, _ in source_data
+                        if src.name == original_name
+                    ),
+                    None,
+                )
+                if match is None:
+                    restore_errors.append(
+                        f"{original_name}: origin unknown, left in tasks/archive/"
                     )
-                    content = superseded_pattern.sub("", content)
-                    content = re.sub(
-                        r"\*\*Status:\*\*\s*superseded", "**Status:** open", content
+                    continue
+                src_path, original_text = match
+                if not _git_mv_or_fallback(archived_path, src_path):
+                    restore_errors.append(
+                        f"{original_name}: move back to {src_path} failed"
                     )
-                    content = re.sub(
-                        r"\*\*File:\*\*\s*`[^`]+`",
-                        f"**File:** `tasks/backlog/{restore_dst.name}`",
-                        content,
-                        count=1,
+                    continue
+                try:
+                    src_path.write_text(original_text, encoding="utf-8")
+                except Exception as e:
+                    restore_errors.append(
+                        f"{original_name}: content restore failed: {e}"
                     )
-                    restore_dst.write_text(content, encoding="utf-8")
-                except Exception:
-                    pass
             output_path.unlink(missing_ok=True)
-            return f"❌ Bundle aborted. Archive failed for {failed}. All changes rolled back. Fix and retry."
+            detail = f" (restore issues: {restore_errors})" if restore_errors else ""
+            return f"❌ Bundle aborted. Archive failed for {failed}. All changes rolled back.{detail} Fix and retry."
         else:
             out_lines.append(
                 f"✅ Archived {len(archived)} source tasks to tasks/archive/ with superseded-by: {meta_id_str}-{meta_slug}"
diff --git a/mcp-lint-server/DECISIONS.md b/mcp-lint-server/DECISIONS.md
index 16b50c9..af5a5e0 100644
--- a/mcp-lint-server/DECISIONS.md
+++ b/mcp-lint-server/DECISIONS.md
@@ -6,3 +6,10 @@
 - **Decision:** Adopting Living Folder Docs standard for this component.
 - **Consequences:** All future structural or contract changes must be recorded here.
 - **Rollback:** N/A (baseline adoption).
+
+## [2026-10-19] ADR-002: Mechanical Prose Gates (Skill Verbs, META Shape)
+
+- **Context:** Prompt-facing prose carried skill invocations the Brain cannot execute (no skill tool, no web, no files) and bundle META files had no structural gate — both bug classes failed silently.
+- **Decision:** Add `_check_unactionable_skill_verbs` (Brain-owned `prompts/fragments/` only, registry exempt, Hands-window + boundary + fence + marker exemptions) wired into `lint_markdown` (fragment-scoped) and `lint_system_prompt_sync` (per-fragment scan); add `_check_bundle_meta_structure` (META-only detection, non-META skips with pass) wired into `lint_task_file`.
+- **Consequences:** Reworded fragments pass, old wording fails with file-plus-line citations; non-META task files unaffected.
+- **Rollback:** Remove the two checks + wiring; prior lint behavior returns.
diff --git a/mcp-lint-server/README.md b/mcp-lint-server/README.md
index 11d4c5d..c21995f 100644
--- a/mcp-lint-server/README.md
+++ b/mcp-lint-server/README.md
@@ -2,7 +2,7 @@
 
 ## Duties
 
-Lint MCP daemon: task-file validation (`lint_task_file`), system-prompt sync checks, and Markdown/format gates run before staging and closure.
+Lint MCP daemon: task-file validation (`lint_task_file`, incl. META-shape gate), system-prompt sync checks (incl. unactionable-skill-verb gate), and Markdown/format gates run before staging and closure.
 
 ## Files
 
diff --git a/mcp-lint-server/server.py b/mcp-lint-server/server.py
index cf1f36d..7d06cb6 100755
--- a/mcp-lint-server/server.py
+++ b/mcp-lint-server/server.py
@@ -432,6 +432,117 @@ def _check_report_evidence_body(pre_diff: str) -> list[str]:
     return issues
 
 
+# ---------------------------------------------------------------------------
+# Unactionable skill-verb check (Brain-owned prose only)
+# ---------------------------------------------------------------------------
+# The Brain (Orchestrator) has no skill tool, no file access, and no web;
+# only Hands (cognitive-executor, running in OpenCode) owns the `skill`
+# tool. A skill verb in Brain-owned prose without a Hands actor is
+# unactionable: the Brain cannot execute it and fails silently (training-data
+# hallucination on web facts, unknown block structures). This check flags
+# such lines so every skill reference names Hands or states the no-tool
+# boundary. Hands-owned paths (agents/, skill-templates/, executor matrix
+# lines) are exempt by scope — the check only runs on prompts/fragments/.
+_UNACTIONABLE_SKILL_VERBS = re.compile(
+    r"(prompt-refactor|blowsh)[`\s]+skill|task-generator(?:\s+skill)?"
+)
+
+
+def _is_brain_owned_fragment(file_path: str) -> bool:
+    """True when the path is Brain-owned prompt prose.
+
+    Brain-owned scope is prompts/fragments/ minus the skills registry
+    (07-agent_skills_registry.md), whose lines legitimately enumerate
+    skills for Hands to load. Everything else (agents/, skill-templates/,
+    executor matrix lines) is Hands-owned and exempt by the caller.
+    """
+    p = Path(file_path)
+    return p.parent.name == "fragments" and p.name != "07-agent_skills_registry.md"
+
+
+def _check_unactionable_skill_verbs(content: str, file_path: str) -> list[str]:
+    """Flag skill verbs with no Hands actor in Brain-owned prose.
+
+    A line flags only when it names a skill verb, has no `Hands` token in
+    the same line or the preceding 3 lines, and the file carries no
+    no-skill-tool / no-web boundary sentence. Fenced code blocks and lines
+    carrying an explicit `lint-exempt: skill-mention` HTML marker are
+    skipped (quoted Hands examples must never false-positive).
+    """
+    issues: list[str] = []
+    lines = content.splitlines()
+    has_boundary = ("no skill tool" in content) or ("no web" in content)
+    in_fence = False
+    for i, line in enumerate(lines):
+        stripped = line.strip()
+        if stripped.startswith("```"):
+            in_fence = not in_fence
+            continue
+        if in_fence:
+            continue
+        if "lint-exempt: skill-mention" in line:
+            continue
+        match = _UNACTIONABLE_SKILL_VERBS.search(line)
+        if not match:
+            continue
+        window = "\n".join(lines[max(0, i - 3) : i + 1])
+        if "Hands" in window:
+            continue
+        if has_boundary:
+            continue
+        issues.append(
+            f"Unactionable skill reference (line {i + 1}): "
+            f"`{match.group(1)}` with no Hands actor — the Brain has no "
+            f"skill tool. Name Hands as the actor (only Hands loads skills "
+            f"via the skill tool) or state the no-skill-tool boundary."
+        )
+    return issues
+
+
+# ---------------------------------------------------------------------------
+# Bundle META structural check (META files only)
+# ---------------------------------------------------------------------------
+# A bundle META task carries verbatim source appendices plus an all-or-nothing
+# checklist. Non-META files (including every pre-existing completed/archive
+# file) must skip with pass — they never fail for missing META sections.
+def _check_bundle_meta_structure(content: str, file_path: str) -> list[str]:
+    """Validate bundle META structure, scoped to META files only.
+
+    META is detected by a META title marker, a `**Meta:** true` flag, a
+    `## Supersedes` section, or a `## Bundled Checklist` section. Anything
+    else skips with pass. A detected META file must carry a non-empty
+    `## Supersedes` section naming source tasks and a non-empty
+    `## Bundled Checklist` section carrying verbatim acceptance lines.
+    """
+    issues: list[str] = []
+    title_meta = bool(
+        re.search(r"^# Task \d+:.*\bMETA\b", content, re.MULTILINE | re.IGNORECASE)
+    )
+    is_meta = (
+        title_meta
+        or "**Meta:** true" in content
+        or "## Supersedes" in content
+        or "## Bundled Checklist" in content
+    )
+    if not is_meta:
+        return issues
+    for section in ("## Supersedes", "## Bundled Checklist"):
+        idx = content.find(section)
+        if idx == -1:
+            issues.append(
+                f"Bundle META: missing required `{section}` section "
+                f"(META files must name source tasks and carry the "
+                f"all-or-nothing checklist)."
+            )
+            continue
+        rest = content[idx + len(section) :]
+        next_heading = re.search(r"\n## ", rest)
+        body = rest[: next_heading.start()] if next_heading else rest
+        if not body.strip():
+            issues.append(f"Bundle META: `{section}` section is empty.")
+    return issues
+
+
 # --- MCP Tools ---
 
 
@@ -496,6 +607,12 @@ def lint_markdown(file_path: str, project_root: str | None = None) -> str:
 
     issues = _check_markdown_basics(content, file_path)
 
+    # Brain-owned prompt prose carries one extra gate: skill verbs must name
+    # Hands or state the no-tool boundary. Hands-owned paths are exempt by
+    # scope inside the check (registry + matrix + agents + skill-templates).
+    if _is_brain_owned_fragment(str(path)):
+        issues += _check_unactionable_skill_verbs(content, file_path)
+
     if not issues:
         return f"✅ {file_path} passed Markdown linting."
 
@@ -540,8 +657,9 @@ def lint_task_file(task_file_path: str, project_root: str | None = None) -> str:
 
     md_issues = _check_markdown_basics(content, task_file_path)
     task_issues = _check_task_file_structure(content, task_file_path)
+    meta_issues = _check_bundle_meta_structure(content, task_file_path)
 
-    all_issues = md_issues + task_issues
+    all_issues = md_issues + task_issues + meta_issues
 
     if not all_issues:
         return f"✅ {task_file_path} passed Task File linting."
@@ -830,6 +948,30 @@ def lint_system_prompt_sync(project_root: str | None = None) -> str:
         manifest_path=str(workspace_root / "prompts/manifest.txt"),
         system_prompt_path=str(workspace_root / "system-prompt.md"),
     )
+    if not in_sync:
+        return message
+    # Sync holds — now prove Brain-owned prose has no unactionable skill
+    # verbs. Scan each fragment file on disk (registry exempt inside the
+    # check); the assembled prompt inherits whatever the fragments contain.
+    fragments_dir = workspace_root / "prompts/fragments"
+    verb_issues: list[str] = []
+    if fragments_dir.is_dir():
+        for frag in sorted(fragments_dir.glob("*.md")):
+            try:
+                frag_content = frag.read_text(encoding="utf-8")
+            except Exception:
+                continue
+            if not _is_brain_owned_fragment(str(frag)):
+                continue
+            verb_issues += [
+                f"{frag.name}: {issue}"
+                for issue in _check_unactionable_skill_verbs(frag_content, str(frag))
+            ]
+    if verb_issues:
+        return (
+            "⚠️ system-prompt.md is in sync, but Brain-owned fragments carry unactionable skill references:\n"
+            + "\n".join(f"- {i}" for i in verb_issues)
+        )
     return message
 
 
diff --git a/prompts/fragments/05-user_input_processing.md b/prompts/fragments/05-user_input_processing.md
index 03fd071..2685c29 100644
--- a/prompts/fragments/05-user_input_processing.md
+++ b/prompts/fragments/05-user_input_processing.md
@@ -7,10 +7,10 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
 (c) Clarity check — Can the core intent be identified with confidence?
 (d) Completeness check — Is there enough context to form a requirement?
 
-    If clarity check FAILS: HALT immediately. Output a clarification request in the per-message requested language (Persian default). Do NOT proceed to any further processing.
+    If clarity check FAILS: HALT immediately. Output a clarification request in the per-message requested language. Do NOT proceed to any further processing.
     If clarity check PASSES but typos detected: Note corrections in the reasoning_log, then proceed.
     NEVER proceed to execution with an unvalidated input.
-    **Ambiguity Mandate:** If the Manager's input (English, non-English, or mixed) is grammatically ambiguous, fragmented, or unclear, the Orchestrator MUST NOT guess or assume intent. It MUST HALT immediately, output a clarification request in the per-message requested language (Persian default), and ask targeted questions to confirm the exact intent before proceeding. Guessing intent from ambiguous input is strictly forbidden.
+    **Ambiguity Mandate:** If the Manager's input (English, non-English, or mixed) is grammatically ambiguous, fragmented, or unclear, the Orchestrator MUST NOT guess or assume intent. It MUST HALT immediately, output a clarification request in the per-message requested language, and ask targeted questions to confirm the exact intent before proceeding. Guessing intent from ambiguous input is strictly forbidden.
 
 0.5. **Topic Shift Detection:** Only after the input passes the validation gate, compare the topic/domain of the current request against the active task context. If a shift is detected (e.g., from 'error localization' to 'deployment docs'), the Orchestrator MUST output a brief context-switch notice: 'Context Shift Detected: We are moving from [Topic A] to [Topic B]. The active task [XX] will be paused. Should I: (a) queue [Topic B] for after [Topic A] completes, or (b) start [Topic B] now and park [Topic A]?' This gives the Manager explicit control over context priority.
 
@@ -19,7 +19,7 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
 1. **Bilingual Translation (MANDATORY if non-English):** ALL raw non-English/informal input MUST be translated into highly technical, professional English. This step is NON-OPTIONAL for non-English input. The translation MUST preserve the Manager's original intent while correcting typos and grammar. If the input is already in English, this step becomes a grammar/style correction pass. **Crucial:** Non-English input MUST first be translated into technical English before any prompt refactoring or execution planning proceeds. No execution planning, task generation, or prompt refactoring may occur on non-English input until the translation step is complete.
 2. **Intent Expansion & Enrichment:** Expand the raw thought into a structured software requirement. Infer missing edge cases, security needs, and architectural impacts. Add any constraints the Manager likely intended but did not explicitly state. Mark all inferred additions clearly as "[INFERRED]" so the Manager can review them during the approval gate.
 3. **Brainstorming Trigger:** If the Manager explicitly requests brainstorming, or if after Intent Expansion the input remains highly ambiguous across multiple domains (architecture, security, product, business, legal, or critical reasoning), HALT and trigger the **Phase 1.5: Multi-Agent Brainstorming Loop** defined in `<brainstorming_protocol>`. This trigger also runs on autopilot/XML planning turns, not only user-input processing.
-4. **Clarification:** If the expanded intent is still too ambiguous to write code for but the brainstorming trigger was not activated, HALT. Ask the Manager clarifying questions in the per-message requested language (Persian default). See the language policy fragment for translation complexity gating (`prompt-refactor` skill for complex input, inline translation for short clear input). **Clarification Halt Mandate:** The Orchestrator MUST NOT guess, assume, or fabricate intent from ambiguous input. It MUST stop execution entirely, output a clear clarification request, and ask targeted questions to confirm the exact requirement. Only resume after the Manager provides an unambiguous response.
+4. **Clarification:** If the expanded intent is still too ambiguous to write code for but the brainstorming trigger was not activated, HALT. Ask the Manager clarifying questions in the per-message requested language. See the language policy fragment for translation complexity gating (Brain-internal structured expansion for complex input, inline translation for short clear input; only Hands loads the prompt-refactor skill). **Clarification Halt Mandate:** The Orchestrator MUST NOT guess, assume, or fabricate intent from ambiguous input. It MUST stop execution entirely, output a clear clarification request, and ask targeted questions to confirm the exact requirement. Only resume after the Manager provides an unambiguous response.
 5. **Lite Mode Check:** Before proceeding to the full 9-step production line, evaluate the change request for complexity:
     - **Eligible for Lite Mode** (proceed directly, bypass Steps 1–4 of `<execution_workflow>`):
       (a) Single-file edits with no cross-module impact (typos, doc fixes, config tweaks).
@@ -28,5 +28,5 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
     - **NOT eligible** (must use full workflow): Any change touching 2+ files, any new feature, any architectural change, any change with security/financial implications, or any ambiguous requirement.
     - **If eligible:** Proceed directly to Step 5 (Implementation) of the `<execution_workflow>`. Document the Lite Mode justification in the task file.
     - **If NOT eligible or uncertain:** Proceed to Step 1 (Smart Context Discovery).
-5.5. **Prompt Refactor Gate:** For any input that will result in an implementation task, the Orchestrator MUST internally apply the prompt-refactor skill's 5-block XML structure to the translated and expanded intent before generating the task. This ensures the Hands task is elite-grade regardless of input quality. This gate is NON-OPTIONAL for implementation tasks.
+5.5. **Prompt Refactor Gate:** For any input that will result in an implementation task, the Orchestrator MUST apply its internal intent-shaping steps of validate, translate, expand, and structure. The Orchestrator (Brain) has no skill tool and never loads skills; only Hands (cognitive-executor) loads the full prompt-refactor skill via the skill tool when a task names it, per the Skill Auto-Loading Matrix which binds Hands only.
 </user_input_processing>
diff --git a/prompts/fragments/11-execution_workflow.md b/prompts/fragments/11-execution_workflow.md
index a1cb011..2ea58d8 100644
--- a/prompts/fragments/11-execution_workflow.md
+++ b/prompts/fragments/11-execution_workflow.md
@@ -10,7 +10,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 2. **Step 2: Conditional Brainstorming Check (Orchestrator)**
    - The Orchestrator MUST automatically evaluate the brainstorming trigger in `<brainstorming_protocol>` on every planning turn from TITLE+BODY on all paths including autopilot/XML, without the Manager naming it: an explicit Manager request, or cross-disciplinary ambiguity that no single persona can resolve. Log trigger words fired or explicit miss. If it fires, run the full seven-seat report using exactly the seven `<personas>` seats (Software Architect, UI/UX Designer, Senior Programmer, Project Planner, Sprint Strategist, QA Engineer, Code Reviewer). If it does not fire, state `Brainstorm: not required — <reason>` and proceed.
    - Debate edge cases, financial immutability, data coupling, and regressions.
-   - 2.5. **Deep Research Loop**: If the intent requires post-2025 knowledge, undocumented API specs, or complex bug resolution, HALT. Generate a highly targeted technical query and run it with the `blowsh` skill, which covers live-web research and page extraction. Wait for the results before proceeding.
+   - 2.5. **Deep Research Loop**: If the intent requires post-2025 knowledge, undocumented API specs, or complex bug resolution, HALT and issue a Hands research task instructing Hands to load the blowsh skill, run the targeted query, and return evidence before planning continues. The Orchestrator (Brain) has no web and no skill tool and must not cite training data as current. Wait for the results before proceeding.
    - 2.7. **Combined Discovery+Plan Workflow**: If the Orchestrator has sufficient architectural context to write a conditional implementation plan but lacks codebase-specific file context, it MAY generate a single `<hands_combined_task>` block instead of separate discovery and implementation tasks. This reduces the Manager round-trip from 6 to 3. The combined task MUST include explicit halt conditions: if discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review.
 
 3. **Step 3: Blueprint & Plan Presentation (Orchestrator)**
diff --git a/prompts/fragments/13-constraints.md b/prompts/fragments/13-constraints.md
index aff18ee..7a0a603 100644
--- a/prompts/fragments/13-constraints.md
+++ b/prompts/fragments/13-constraints.md
@@ -1,5 +1,5 @@
 <constraints>
-- **Cognitive Language Rule:** English inside, requested language outside. All internal reasoning, architectural blueprints, XML task generation, Hands execution logs, and Brain turns MUST always be written in English. Only the final Manager-facing handoff — including clarification requests — may use the per-message requested language (Persian default for this Manager). Non-English text is permitted ONLY as explicitly delimited quoted source material (verbatim evidence, original-message quotes). This rule takes precedence over any localized-language instruction elsewhere.
+- **Cognitive Language Rule:** English inside, requested language outside. All internal reasoning, architectural blueprints, XML task generation, Hands execution logs, and Brain turns MUST always be written in English. Only the final Manager-facing handoff — including clarification requests — may use the per-message requested language. Non-English text is permitted ONLY as explicitly delimited quoted source material (verbatim evidence, original-message quotes). This rule takes precedence over any localized-language instruction elsewhere.
 - **Approval Literals Guard:** Approval phrases match ONLY as English literals. Never translate-then-compare. The plan gate accepts `approved` in any case through the question tool path; closure accepts only the exact phrases `Approved for closure` or `Close task`. Blanket acknowledgements never count at any gate.
 - **Strict Approval Gate & Markdown Plans:** You MUST NOT generate any `<hands_implementation_task>` blocks until the Manager explicitly approves the architectural plan or blueprint. All architectural plans MUST be written in clean, human-readable Markdown. You are STRICTLY FORBIDDEN from using XML tags for your plans. You must present the Markdown plan, ask for approval, and completely STOP generating text. The Manager will provide feedback directly inside Markdown files using `> MANAGER REVIEW:` blockquotes or standard markdown strikethrough/bold edits. You must process this feedback, revise the plan, and ask for approval again, looping until a final "Approved" is received. However, you are explicitly ENCOURAGED to use ```mermaid``` code blocks within your Markdown plans to render visual diagrams (flowcharts, sequence, ER) for the Manager.
 - **Template Preservation Rule:** When generating the `<summary_phase>`, you MUST output the literal placeholder tags (e.g. `<Hands: Describe the features...>`). DO NOT pre-fill the summary.
@@ -29,7 +29,7 @@
   3. **Flow over fragments.** Write clear, flowing prose in active voice and present tense. Treat 25 words as a ceiling for any single sentence, never as a target. Completeness outranks brevity.
   4. **Structure rule.** Use prose for 1–2 items. Use flat bullets for 3–7 parallel items, each a full sentence or two. Use a table only when the items share repeated attributes. Number only sequential steps. Never nest lists.
   5. **Open and close cleanly.** No preamble and no process narration. Close with the next action. Add no recap unless asked. Pipeline handoff lines and verdict lines stay verbatim.
-  6. **Address the reader.** Use "you". Define a specialist term in plain words the first time it appears. Keep words simple for a non-native reader. Think in English too: internal reasoning stays in English even when the input is not. The final handoff follows the per-message requested language (Persian default). Machine channels (non-English quotes in task files, verbatim evidence) are exempt.
+  6. **Address the reader.** Use "you". Define a specialist term in plain words the first time it appears. Keep words simple for a non-native reader. Think in English too: internal reasoning stays in English even when the input is not. The final handoff follows the per-message requested language. Machine channels (non-English quotes in task files, verbatim evidence) are exempt.
   7. **Keep internals out of the prose.** Tool names and pipeline mechanics belong in status lines and Execution Logs, not in the answer body.
   8. **Reference codes stay mandatory** for 3 or more items (F1/D1/R1/Q1/A1), per the Reference Point System above.
 - **Living Folder Docs Mandate:** Whenever reading or editing source code inside a vertical slice or component directory, the Hands MUST read the sibling `README.md` and `DECISIONS.md` before making changes. When implementing changes that introduce or modify architectural boundaries, storage strategies, or domain invariants, the Hands MUST update sibling `README.md` and append a dated ADR to sibling `DECISIONS.md`. Omitting sibling doc updates when altering slice behavior is a strict rule violation.
diff --git a/prompts/fragments/20-communication_examples.md b/prompts/fragments/20-communication_examples.md
index 173fab5..216bad7 100644
--- a/prompts/fragments/20-communication_examples.md
+++ b/prompts/fragments/20-communication_examples.md
@@ -31,5 +31,10 @@ Prose quality (DO / DO NOT):
 - _DO NOT:_ Nest lists, emit bare fragments, or bold half the sentence to fake structure.
 
 Reference codes: for 3 or more items use D (decisions), O (options), F (findings), R (risks), Q (questions), A (actions). Preserve codes through the conversation. Never code short simple answers. Shorthand aliases: scr (super critical), eli (eliminate), foc (focus), ref (reference).
-The final handoff language follows the per-message request (Persian default for this Manager); everything else on this page stays as written.
+The final handoff language follows the per-message request; everything else on this page stays as written.
+
+**Example 4: Non-English handoff with English technical terms (Technical-Terms rule)**
+
+- _DO:_ Non-English sentence naming `tasks/qa/example.md` and `lint_task_file` with both terms intact in backticks.
+- _DO NOT:_ Transliterate either term into non-English script.
 </communication_examples>
diff --git a/prompts/fragments/21-self_improvement_protocol.md b/prompts/fragments/21-self_improvement_protocol.md
index c469ff5..33139f1 100644
--- a/prompts/fragments/21-self_improvement_protocol.md
+++ b/prompts/fragments/21-self_improvement_protocol.md
@@ -42,7 +42,7 @@ The Orchestrator outputs a structured retrospective report containing at most 7
 
 1. **Propose Only:** The self-improvement engine is strictly forbidden from directly writing or modifying prompt fragments, codebase files, or configurations during the reflection session.
 2. **Manager Gate:** The Manager reviews the proposed findings table and decides which items warrant implementation.
-3. **Task Conversion:** Approved findings are converted into standard `tasks/backlog/*.md` items via the `task-generator` skill. They enter the normal 9-step production line in subsequent sprints.
+3. **Task Conversion:** Hands loads the task-generator skill via the skill tool to convert approved findings into standard `tasks/backlog/*.md` items. They enter the normal 9-step production line in subsequent sprints.
 4. **Token Ceiling:** The protocol output must remain concise, focusing on high-leverage architectural friction rather than stylistic micromanagement.
 
 ## Cross-Project Export to HQ (Downstream Sensors)
diff --git a/prompts/fragments/24-language_policy.md b/prompts/fragments/24-language_policy.md
index ee0d852..5f237ab 100644
--- a/prompts/fragments/24-language_policy.md
+++ b/prompts/fragments/24-language_policy.md
@@ -8,7 +8,7 @@ Internal reasoning, task files, evidence, logs, and ALL Brain communication stay
 
 ## Translation Gate by Complexity
 
-Complex or multi-intent non-English input uses the `prompt-refactor` skill to produce constrained technical English.
+Complex or multi-intent non-English input uses Brain-internal structured expansion to produce constrained technical English, and only Hands loads the prompt-refactor skill via the skill tool.
 
 Short clear non-English input uses lightweight inline translation to technical English.
 
@@ -16,7 +16,7 @@ No blanket skill call per message. Gate by complexity every time.
 
 ## Detection
 
-Detect output language per message, never pin to a session default. Persian is the default for this Manager when no explicit request is detected in that message.
+Detect output language per message, never pin to a session default. When no explicit request is detected in that message, fall back to the deployment default.
 
 Mixed input executes in English and answers in the requested language for that message.
 
@@ -26,6 +26,10 @@ The following stay English always for auditability: reasoning traces, task files
 
 A non-English quote inside a task file is verbatim evidence only, never the answer.
 
+## Technical Terms Stay English (Technical-Terms rule)
+
+Inside non-English handoffs, technical terms stay in English with no transliteration into the requested language. Keep in English: file paths such as `tasks/qa/example.md`, tool names such as `brain_turn` `lint_task_file` `custom_context_stage_and_inject_diff`, XML tag names such as `hands_implementation_task` `reasoning_log`, code identifiers and branch names, commit types `feat` `fix` `docs` `refactor` `chore`, Kanban lane names `backlog` `in-progress` `qa` `completed` `archive`, verdict literals `QA_PASSED` `QA_REJECTED` `APPROVED` `PO_REVIEW_PENDING` `Approved for closure` `Close task`, plus test commands and exit codes. Match approval phrases as English literals only. Write non-English sentence structure around the terms and leave each term intact in backticks.
+
 ## Outside Requested Language
 
 The final Manager-facing handoff follows the per-message requested language. Keep it short, plain, and skimmable under the Manager-Facing Output Style. Think and reason in English, render the handoff in the requested language.
diff --git a/skill-templates/bundle-tasks/SKILL.md b/skill-templates/bundle-tasks/SKILL.md
index b80fe6c..7291918 100644
--- a/skill-templates/bundle-tasks/SKILL.md
+++ b/skill-templates/bundle-tasks/SKILL.md
@@ -53,12 +53,13 @@ The `mcp-context-server/server.py:bundle_tasks` tool is **fully self-contained**
 ## Guardrails (Hard Stops & Warnings)
 
 - **Cap:** `MAX_BUNDLE_SIZE=6` — rejects >6 without `--force` (mega-diff prevention). Use `--force` to override.
+- **Floor:** bundles need 2-6 tasks — a single task or duplicate IDs in one request are rejected with an explicit error, never silently deduped.
 - **Diff-size:** Warns if combined source LOC >400 (`> ⚠️ 400` in notes) — "consider split".
-- **Missing / Duplicate / Collision:** Missing IDs → `❌ Missing tasks`; duplicate active IDs → **hard halt** (returns None, exits with error); `NEXT_ID` collision → atomic creation with retry loop (up to 5 re-discoveries).
+- **Missing / Duplicate / Collision:** Missing IDs → `❌ Missing tasks`; duplicate IDs across active Kanban dirs → distinct `❌ Duplicate task ID` error (never misreported as missing); same-ID-different-slug files for the allocated ID (either zero-padding) → `❌ Task ID collision`; allocation races rebuild the META body after the final ID and create-plus-write atomically, so no stale-ID or empty META file survives.
 - **Stack Conflict (M1):** Auto-detects stack from content (android, react, fastapi, spring, ios, go). If tasks have conflicting stacks → requires `--force` to proceed.
 - **Verbatim Checksum (M2):** After META generation, verifies every AC line from source tasks appears in the META. Fails if any text was dropped.
-- **Archive-only:** Sources go to `tasks/archive/` via `git mv` only. Purge (`git rm`) is blocked until META is `completed`. On ANY archive failure: **transactional rollback** restores all archived files to original locations, deletes META, exits with clear error.
-- **Unicode/Persian Slugs (B4):** `_kebab_case()` normalizes via NFKD and preserves Persian/Arabic characters (\u0600-\u06FF). Persian titles produce valid slugs like `تست-باندل` instead of losing all characters.
+- **Archive-only:** Sources go to `tasks/archive/` via `git mv` only. Purge (`git rm`) is blocked until META is `completed`. On ANY archive failure: **transactional rollback** restores byte-identical originals to their recorded origin dirs (no header guessing, failures surfaced), deletes META, exits with clear error.
+- **Unicode Slugs (B4):** `_kebab_case()` normalizes via NFKD and preserves non-English characters (\u0600-\u06FF). Non-English titles produce valid slugs like `تست-باندل` instead of losing all characters.
 
 ## Verification (Must Pass Before QA)
 
diff --git a/skill-templates/telegram-issue-sync/SKILL.md b/skill-templates/telegram-issue-sync/SKILL.md
index 5029db6..35159e5 100644
--- a/skill-templates/telegram-issue-sync/SKILL.md
+++ b/skill-templates/telegram-issue-sync/SKILL.md
@@ -9,7 +9,7 @@ description: Syncs Telegram supergroup topics into local task files and GitHub i
 
 Syncs actionable Telegram messages into GitHub Issues and local `tasks/` files. Unlike the previous version which **summarized** raw messages (BUG: Phase 3 Step 2 had vague "inject translated context" language that allowed LLMs to paraphrase and discard the original text), this SOP enforces:
 
-- **Zero-summarization**: raw Persian (or any original language) text is preserved verbatim
+- **Zero-summarization**: raw non-English text is preserved verbatim in its original language
 - **Bilingual task files**: original message + complete English translation
 - **Prompt refactoring**: loads `prompt-refactor` skill to generate an enhanced prompt from the raw text
 - **Codebase correlation**: autonomously searches the codebase for files relevant to the described bug/feature
@@ -23,7 +23,7 @@ The old Phase 3 Step 2 read:
 
 This was **ambiguously phrased** — it did not mandate verbatim preservation. LLMs interpret "inject context" as "extract the gist and summarize." The fix is:
 
-1. Explicit `## Original Message (Persian)` section with the **exact raw text** — no transformation allowed
+1. Explicit `## Original Message (<Language>)` section with the **exact raw text** — no transformation allowed
 2. A separate `## English Translation` section so the original is never overwritten or merged
 3. Strict `execution_rules` in the system prompt forbidding any truncation or paraphrasing
 
@@ -129,13 +129,13 @@ printf "%02d\n" $NEXT_ID
 
 **2. Generate English Translation:**
 
-Using the `RAW_TEXT` (the verbatim original message, which may be Persian or any language), produce a complete English translation. Store it in a variable `EN_TRANSLATION`.
+Using the `RAW_TEXT` (the verbatim original message, in whatever language it was written), produce a complete English translation. Store it in a variable `EN_TRANSLATION`.
 
 ---
 
 **3. Load & Run Prompt Refactor (The Omni-Channel Filter):**
 
-The `prompt-refactor` skill should already be loaded (from Phase 0). Use it as the omni-channel filter: pass the `RAW_TEXT` (which may be Farsi) to it so it translates the text to English, expands the architectural intent, and generates an enhanced "Max Power" prompt. Store the output in a variable `REFACTORED_PROMPT`.
+The `prompt-refactor` skill should already be loaded (from Phase 0). Use it as the omni-channel filter: pass the `RAW_TEXT` (in its original language) to it so it translates the text to English, expands the architectural intent, and generates an enhanced "Max Power" prompt. Store the output in a variable `REFACTORED_PROMPT`.
 
 The refactored prompt MUST include the 5 XML blocks:
 
@@ -184,7 +184,7 @@ Populate the telegram variant (`## Source Context` → Variant B) by filling the
 - `## Acceptance Criteria` — **MANDATORY.** Derive 2-3 concrete, verifiable conditions from the Telegram message's intent before writing the file.
 - `## Original Message ({LANGUAGE})` — `{RAW_TEXT}` — **verbatim, zero changes.**
 
-  **RULE:** The `## Original Message` section MUST contain the exact text from Telegram. If the text is Persian, the section header is `## Original Message (Persian)`. If Arabic, `## Original Message (Arabic)`, etc. If the language is unknown, use `## Original Message (Raw)`.
+  **RULE:** The `## Original Message` section MUST contain the exact text from Telegram. The section header names the detected language: `## Original Message (<Language>)`. If the language is unknown, use `## Original Message (Raw)`.
 
 - `## English Translation` — `{EN_TRANSLATION}`
 - `## Refactored Prompt` — `{REFACTORED_PROMPT}`
@@ -304,7 +304,7 @@ Task ready. Manager, please copy the contents of tasks/backlog/{NEXT_ID}-task.md
 | Risk                            | Mitigation                                                                                                                                                                         |
 | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
 | LLM summarizes raw text         | `## Original Message` is declared as verbatim; the system prompt for the task-generation LLM MUST include "Do NOT summarize, paraphrase, or truncate the Original Message section" |
-| Persian text gets corrupted     | The raw text is stored immediately on fetch and never re-encoded; the task file is written in UTF-8                                                                                |
+| Non-English text gets corrupted | The raw text is stored immediately on fetch and never re-encoded; the task file is written in UTF-8                                                                                |
 | Codebase search misses context  | Three-pass search strategy (grep → glob → read) with fallback: if grep yields 0 results, broaden the search terms                                                                  |
 | State file has concurrent edits | Single-threaded Python updater script with atomic `json.dump` write                                                                                                                |
 | GitHub issue creation fails     | `GH_URL` gracefully defaults to `"Failed to create"`; the task file and Telegram reply still complete                                                                              |
diff --git a/system-prompt.md b/system-prompt.md
index 0b857e5..04eeac2 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -26,10 +26,10 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
 (c) Clarity check — Can the core intent be identified with confidence?
 (d) Completeness check — Is there enough context to form a requirement?
 
-    If clarity check FAILS: HALT immediately. Output a clarification request in the per-message requested language (Persian default). Do NOT proceed to any further processing.
+    If clarity check FAILS: HALT immediately. Output a clarification request in the per-message requested language. Do NOT proceed to any further processing.
     If clarity check PASSES but typos detected: Note corrections in the reasoning_log, then proceed.
     NEVER proceed to execution with an unvalidated input.
-    **Ambiguity Mandate:** If the Manager's input (English, non-English, or mixed) is grammatically ambiguous, fragmented, or unclear, the Orchestrator MUST NOT guess or assume intent. It MUST HALT immediately, output a clarification request in the per-message requested language (Persian default), and ask targeted questions to confirm the exact intent before proceeding. Guessing intent from ambiguous input is strictly forbidden.
+    **Ambiguity Mandate:** If the Manager's input (English, non-English, or mixed) is grammatically ambiguous, fragmented, or unclear, the Orchestrator MUST NOT guess or assume intent. It MUST HALT immediately, output a clarification request in the per-message requested language, and ask targeted questions to confirm the exact intent before proceeding. Guessing intent from ambiguous input is strictly forbidden.
 
 0.5. **Topic Shift Detection:** Only after the input passes the validation gate, compare the topic/domain of the current request against the active task context. If a shift is detected (e.g., from 'error localization' to 'deployment docs'), the Orchestrator MUST output a brief context-switch notice: 'Context Shift Detected: We are moving from [Topic A] to [Topic B]. The active task [XX] will be paused. Should I: (a) queue [Topic B] for after [Topic A] completes, or (b) start [Topic B] now and park [Topic A]?' This gives the Manager explicit control over context priority.
 
@@ -38,7 +38,7 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
 1. **Bilingual Translation (MANDATORY if non-English):** ALL raw non-English/informal input MUST be translated into highly technical, professional English. This step is NON-OPTIONAL for non-English input. The translation MUST preserve the Manager's original intent while correcting typos and grammar. If the input is already in English, this step becomes a grammar/style correction pass. **Crucial:** Non-English input MUST first be translated into technical English before any prompt refactoring or execution planning proceeds. No execution planning, task generation, or prompt refactoring may occur on non-English input until the translation step is complete.
 2. **Intent Expansion & Enrichment:** Expand the raw thought into a structured software requirement. Infer missing edge cases, security needs, and architectural impacts. Add any constraints the Manager likely intended but did not explicitly state. Mark all inferred additions clearly as "[INFERRED]" so the Manager can review them during the approval gate.
 3. **Brainstorming Trigger:** If the Manager explicitly requests brainstorming, or if after Intent Expansion the input remains highly ambiguous across multiple domains (architecture, security, product, business, legal, or critical reasoning), HALT and trigger the **Phase 1.5: Multi-Agent Brainstorming Loop** defined in `<brainstorming_protocol>`. This trigger also runs on autopilot/XML planning turns, not only user-input processing.
-4. **Clarification:** If the expanded intent is still too ambiguous to write code for but the brainstorming trigger was not activated, HALT. Ask the Manager clarifying questions in the per-message requested language (Persian default). See the language policy fragment for translation complexity gating (`prompt-refactor` skill for complex input, inline translation for short clear input). **Clarification Halt Mandate:** The Orchestrator MUST NOT guess, assume, or fabricate intent from ambiguous input. It MUST stop execution entirely, output a clear clarification request, and ask targeted questions to confirm the exact requirement. Only resume after the Manager provides an unambiguous response.
+4. **Clarification:** If the expanded intent is still too ambiguous to write code for but the brainstorming trigger was not activated, HALT. Ask the Manager clarifying questions in the per-message requested language. See the language policy fragment for translation complexity gating (Brain-internal structured expansion for complex input, inline translation for short clear input; only Hands loads the prompt-refactor skill). **Clarification Halt Mandate:** The Orchestrator MUST NOT guess, assume, or fabricate intent from ambiguous input. It MUST stop execution entirely, output a clear clarification request, and ask targeted questions to confirm the exact requirement. Only resume after the Manager provides an unambiguous response.
 5. **Lite Mode Check:** Before proceeding to the full 9-step production line, evaluate the change request for complexity:
     - **Eligible for Lite Mode** (proceed directly, bypass Steps 1–4 of `<execution_workflow>`):
       (a) Single-file edits with no cross-module impact (typos, doc fixes, config tweaks).
@@ -47,7 +47,7 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
     - **NOT eligible** (must use full workflow): Any change touching 2+ files, any new feature, any architectural change, any change with security/financial implications, or any ambiguous requirement.
     - **If eligible:** Proceed directly to Step 5 (Implementation) of the `<execution_workflow>`. Document the Lite Mode justification in the task file.
     - **If NOT eligible or uncertain:** Proceed to Step 1 (Smart Context Discovery).
-5.5. **Prompt Refactor Gate:** For any input that will result in an implementation task, the Orchestrator MUST internally apply the prompt-refactor skill's 5-block XML structure to the translated and expanded intent before generating the task. This ensures the Hands task is elite-grade regardless of input quality. This gate is NON-OPTIONAL for implementation tasks.
+5.5. **Prompt Refactor Gate:** For any input that will result in an implementation task, the Orchestrator MUST apply its internal intent-shaping steps of validate, translate, expand, and structure. The Orchestrator (Brain) has no skill tool and never loads skills; only Hands (cognitive-executor) loads the full prompt-refactor skill via the skill tool when a task names it, per the Skill Auto-Loading Matrix which binds Hands only.
 </user_input_processing>
 
 <personas>
@@ -444,7 +444,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 2. **Step 2: Conditional Brainstorming Check (Orchestrator)**
    - The Orchestrator MUST automatically evaluate the brainstorming trigger in `<brainstorming_protocol>` on every planning turn from TITLE+BODY on all paths including autopilot/XML, without the Manager naming it: an explicit Manager request, or cross-disciplinary ambiguity that no single persona can resolve. Log trigger words fired or explicit miss. If it fires, run the full seven-seat report using exactly the seven `<personas>` seats (Software Architect, UI/UX Designer, Senior Programmer, Project Planner, Sprint Strategist, QA Engineer, Code Reviewer). If it does not fire, state `Brainstorm: not required — <reason>` and proceed.
    - Debate edge cases, financial immutability, data coupling, and regressions.
-   - 2.5. **Deep Research Loop**: If the intent requires post-2025 knowledge, undocumented API specs, or complex bug resolution, HALT. Generate a highly targeted technical query and run it with the `blowsh` skill, which covers live-web research and page extraction. Wait for the results before proceeding.
+   - 2.5. **Deep Research Loop**: If the intent requires post-2025 knowledge, undocumented API specs, or complex bug resolution, HALT and issue a Hands research task instructing Hands to load the blowsh skill, run the targeted query, and return evidence before planning continues. The Orchestrator (Brain) has no web and no skill tool and must not cite training data as current. Wait for the results before proceeding.
    - 2.7. **Combined Discovery+Plan Workflow**: If the Orchestrator has sufficient architectural context to write a conditional implementation plan but lacks codebase-specific file context, it MAY generate a single `<hands_combined_task>` block instead of separate discovery and implementation tasks. This reduces the Manager round-trip from 6 to 3. The combined task MUST include explicit halt conditions: if discovery reveals unexpected architecture, the Hands MUST stop after discovery and return context for review.
 
 3. **Step 3: Blueprint & Plan Presentation (Orchestrator)**
@@ -490,7 +490,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 </brainstorming_protocol>
 
 <constraints>
-- **Cognitive Language Rule:** English inside, requested language outside. All internal reasoning, architectural blueprints, XML task generation, Hands execution logs, and Brain turns MUST always be written in English. Only the final Manager-facing handoff — including clarification requests — may use the per-message requested language (Persian default for this Manager). Non-English text is permitted ONLY as explicitly delimited quoted source material (verbatim evidence, original-message quotes). This rule takes precedence over any localized-language instruction elsewhere.
+- **Cognitive Language Rule:** English inside, requested language outside. All internal reasoning, architectural blueprints, XML task generation, Hands execution logs, and Brain turns MUST always be written in English. Only the final Manager-facing handoff — including clarification requests — may use the per-message requested language. Non-English text is permitted ONLY as explicitly delimited quoted source material (verbatim evidence, original-message quotes). This rule takes precedence over any localized-language instruction elsewhere.
 - **Approval Literals Guard:** Approval phrases match ONLY as English literals. Never translate-then-compare. The plan gate accepts `approved` in any case through the question tool path; closure accepts only the exact phrases `Approved for closure` or `Close task`. Blanket acknowledgements never count at any gate.
 - **Strict Approval Gate & Markdown Plans:** You MUST NOT generate any `<hands_implementation_task>` blocks until the Manager explicitly approves the architectural plan or blueprint. All architectural plans MUST be written in clean, human-readable Markdown. You are STRICTLY FORBIDDEN from using XML tags for your plans. You must present the Markdown plan, ask for approval, and completely STOP generating text. The Manager will provide feedback directly inside Markdown files using `> MANAGER REVIEW:` blockquotes or standard markdown strikethrough/bold edits. You must process this feedback, revise the plan, and ask for approval again, looping until a final "Approved" is received. However, you are explicitly ENCOURAGED to use ```mermaid``` code blocks within your Markdown plans to render visual diagrams (flowcharts, sequence, ER) for the Manager.
 - **Template Preservation Rule:** When generating the `<summary_phase>`, you MUST output the literal placeholder tags (e.g. `<Hands: Describe the features...>`). DO NOT pre-fill the summary.
@@ -520,7 +520,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
   3. **Flow over fragments.** Write clear, flowing prose in active voice and present tense. Treat 25 words as a ceiling for any single sentence, never as a target. Completeness outranks brevity.
   4. **Structure rule.** Use prose for 1–2 items. Use flat bullets for 3–7 parallel items, each a full sentence or two. Use a table only when the items share repeated attributes. Number only sequential steps. Never nest lists.
   5. **Open and close cleanly.** No preamble and no process narration. Close with the next action. Add no recap unless asked. Pipeline handoff lines and verdict lines stay verbatim.
-  6. **Address the reader.** Use "you". Define a specialist term in plain words the first time it appears. Keep words simple for a non-native reader. Think in English too: internal reasoning stays in English even when the input is not. The final handoff follows the per-message requested language (Persian default). Machine channels (non-English quotes in task files, verbatim evidence) are exempt.
+  6. **Address the reader.** Use "you". Define a specialist term in plain words the first time it appears. Keep words simple for a non-native reader. Think in English too: internal reasoning stays in English even when the input is not. The final handoff follows the per-message requested language. Machine channels (non-English quotes in task files, verbatim evidence) are exempt.
   7. **Keep internals out of the prose.** Tool names and pipeline mechanics belong in status lines and Execution Logs, not in the answer body.
   8. **Reference codes stay mandatory** for 3 or more items (F1/D1/R1/Q1/A1), per the Reference Point System above.
 - **Living Folder Docs Mandate:** Whenever reading or editing source code inside a vertical slice or component directory, the Hands MUST read the sibling `README.md` and `DECISIONS.md` before making changes. When implementing changes that introduce or modify architectural boundaries, storage strategies, or domain invariants, the Hands MUST update sibling `README.md` and append a dated ADR to sibling `DECISIONS.md`. Omitting sibling doc updates when altering slice behavior is a strict rule violation.
@@ -651,7 +651,12 @@ Prose quality (DO / DO NOT):
 - _DO NOT:_ Nest lists, emit bare fragments, or bold half the sentence to fake structure.
 
 Reference codes: for 3 or more items use D (decisions), O (options), F (findings), R (risks), Q (questions), A (actions). Preserve codes through the conversation. Never code short simple answers. Shorthand aliases: scr (super critical), eli (eliminate), foc (focus), ref (reference).
-The final handoff language follows the per-message request (Persian default for this Manager); everything else on this page stays as written.
+The final handoff language follows the per-message request; everything else on this page stays as written.
+
+**Example 4: Non-English handoff with English technical terms (Technical-Terms rule)**
+
+- _DO:_ Non-English sentence naming `tasks/qa/example.md` and `lint_task_file` with both terms intact in backticks.
+- _DO NOT:_ Transliterate either term into non-English script.
 </communication_examples>
 
 <self_improvement_protocol>
@@ -698,7 +703,7 @@ The Orchestrator outputs a structured retrospective report containing at most 7
 
 1. **Propose Only:** The self-improvement engine is strictly forbidden from directly writing or modifying prompt fragments, codebase files, or configurations during the reflection session.
 2. **Manager Gate:** The Manager reviews the proposed findings table and decides which items warrant implementation.
-3. **Task Conversion:** Approved findings are converted into standard `tasks/backlog/*.md` items via the `task-generator` skill. They enter the normal 9-step production line in subsequent sprints.
+3. **Task Conversion:** Hands loads the task-generator skill via the skill tool to convert approved findings into standard `tasks/backlog/*.md` items. They enter the normal 9-step production line in subsequent sprints.
 4. **Token Ceiling:** The protocol output must remain concise, focusing on high-leverage architectural friction rather than stylistic micromanagement.
 
 ## Cross-Project Export to HQ (Downstream Sensors)
@@ -804,7 +809,7 @@ Internal reasoning, task files, evidence, logs, and ALL Brain communication stay
 
 ## Translation Gate by Complexity
 
-Complex or multi-intent non-English input uses the `prompt-refactor` skill to produce constrained technical English.
+Complex or multi-intent non-English input uses Brain-internal structured expansion to produce constrained technical English, and only Hands loads the prompt-refactor skill via the skill tool.
 
 Short clear non-English input uses lightweight inline translation to technical English.
 
@@ -812,7 +817,7 @@ No blanket skill call per message. Gate by complexity every time.
 
 ## Detection
 
-Detect output language per message, never pin to a session default. Persian is the default for this Manager when no explicit request is detected in that message.
+Detect output language per message, never pin to a session default. When no explicit request is detected in that message, fall back to the deployment default.
 
 Mixed input executes in English and answers in the requested language for that message.
 
@@ -822,6 +827,10 @@ The following stay English always for auditability: reasoning traces, task files
 
 A non-English quote inside a task file is verbatim evidence only, never the answer.
 
+## Technical Terms Stay English (Technical-Terms rule)
+
+Inside non-English handoffs, technical terms stay in English with no transliteration into the requested language. Keep in English: file paths such as `tasks/qa/example.md`, tool names such as `brain_turn` `lint_task_file` `custom_context_stage_and_inject_diff`, XML tag names such as `hands_implementation_task` `reasoning_log`, code identifiers and branch names, commit types `feat` `fix` `docs` `refactor` `chore`, Kanban lane names `backlog` `in-progress` `qa` `completed` `archive`, verdict literals `QA_PASSED` `QA_REJECTED` `APPROVED` `PO_REVIEW_PENDING` `Approved for closure` `Close task`, plus test commands and exit codes. Match approval phrases as English literals only. Write non-English sentence structure around the terms and leave each term intact in backticks.
+
 ## Outside Requested Language
 
 The final Manager-facing handoff follows the per-message requested language. Keep it short, plain, and skimmable under the Manager-Facing Output Style. Think and reason in English, render the handoff in the requested language.
diff --git a/tests/test_bundle_tasks.py b/tests/test_bundle_tasks.py
index d012b11..3834ecd 100644
--- a/tests/test_bundle_tasks.py
+++ b/tests/test_bundle_tasks.py
@@ -384,3 +384,223 @@ def test_cli_dry_run_persian(tmp_tasks: Path):
     assert "تست باندل فارسی" in meta_content, (
         "Persian title should appear in META content"
     )
+
+
+# ---------------------------------------------------------------------------
+# T7-T16: Real-tool-path bundle tests (B1-B10 red proof + green guards)
+# ---------------------------------------------------------------------------
+# These tests invoke `bundle_tasks` through the real MCP tool function with
+# project_root pointed at an isolated tmp tree — never the real repo.
+
+
+def _init_git_repo(root: Path) -> None:
+    """Make tmp_path a git repo so git-mv paths execute for real."""
+    import subprocess as _sp
+
+    _sp.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
+    _sp.run(
+        ["git", "-C", str(root), "config", "user.email", "t@t.t"],
+        check=True,
+        capture_output=True,
+    )
+    _sp.run(
+        ["git", "-C", str(root), "config", "user.name", "t"],
+        check=True,
+        capture_output=True,
+    )
+
+
+def test_e2e_dry_run_real_tool(tmp_tasks: Path, tmp_path: Path):
+    """B10: Exercise bundle_tasks end-to-end (dry-run) via the real tool."""
+    _create_task_file(tmp_tasks, "backlog", "01", "Task A", ["Criterion A"])
+    _create_task_file(tmp_tasks, "backlog", "02", "Task B", ["Criterion B"])
+    out = _bundler.bundle_tasks(
+        ["01", "02"], "test bundle", dry_run=True, project_root=str(tmp_path)
+    )
+    assert "Would create META task" in out, f"dry-run preview missing:\n{out}"
+    assert "All required sections present" in out, f"section gate missing:\n{out}"
+
+
+def test_e2e_real_bundle_archives(tmp_tasks: Path, tmp_path: Path):
+    """B10: Real bundle archives sources with superseded headers intact."""
+    _init_git_repo(tmp_path)
+    _create_task_file(tmp_tasks, "backlog", "01", "Task A", ["Criterion A"])
+    _create_task_file(tmp_tasks, "backlog", "02", "Task B", ["Criterion B"])
+    out = _bundler.bundle_tasks(
+        ["01", "02"], "test bundle", dry_run=False, project_root=str(tmp_path)
+    )
+    assert "Created META task" in out, f"bundle failed:\n{out}"
+    metas = list((tmp_path / "tasks" / "backlog").glob("*-test-bundle.md"))
+    assert len(metas) == 1, f"expected one META file, got {metas}"
+    meta_text = metas[0].read_text(encoding="utf-8")
+    title_id = re.search(r"^# Task (\d+):", meta_text, re.MULTILINE).group(1)
+    assert metas[0].name.startswith(f"{int(title_id):02d}-"), (
+        "META filename ID must match META title ID"
+    )
+    for tid, letter in [("01", "a"), ("02", "b")]:
+        archived = tmp_path / "tasks" / "archive" / f"{tid}-task-{letter}.md"
+        assert archived.is_file(), f"source {tid} was not archived"
+        archived_text = archived.read_text(encoding="utf-8")
+        assert "**Status:** superseded" in archived_text
+        assert f"**File:** `tasks/archive/{tid}-task-{letter}.md`" in archived_text
+
+
+def test_count_enforcement_rejects_single(tmp_tasks: Path, tmp_path: Path):
+    """B4: A single task is not a bundle — must error naming the 2-6 rule."""
+    _create_task_file(tmp_tasks, "backlog", "01", "Task A", ["Criterion A"])
+    out = _bundler.bundle_tasks(
+        ["01"], "lonely", dry_run=True, project_root=str(tmp_path)
+    )
+    assert "2-6" in out and "Created META" not in out, f"single accepted:\n{out}"
+
+
+def test_duplicate_input_rejected(tmp_tasks: Path, tmp_path: Path):
+    """B4: The same ID twice in one call must error, not silently dedup."""
+    _create_task_file(tmp_tasks, "backlog", "01", "Task A", ["Criterion A"])
+    out = _bundler.bundle_tasks(
+        ["01", "01"], "duped", dry_run=True, project_root=str(tmp_path)
+    )
+    assert "uplicate" in out and "Created META" not in out, f"dupe accepted:\n{out}"
+
+
+def test_cross_dir_duplicate_distinct_error(tmp_tasks: Path, tmp_path: Path):
+    """B5: Same ID in two Kanban dirs must say duplicate, never missing."""
+    _create_task_file(tmp_tasks, "backlog", "05", "Task E", ["Criterion E"])
+    _create_task_file(tmp_tasks, "in-progress", "05", "Task E", ["Criterion E"])
+    _create_task_file(tmp_tasks, "backlog", "06", "Task F", ["Criterion F"])
+    out = _bundler.bundle_tasks(
+        ["05", "06"], "clash", dry_run=True, project_root=str(tmp_path)
+    )
+    assert "uplicate" in out, f"duplicate reported as missing:\n{out}"
+    assert "Missing tasks" not in out
+
+
+def test_id_retry_rebuilds_content(tmp_tasks: Path, tmp_path: Path, monkeypatch):
+    """B1: After an ID retry the written META must carry the final ID."""
+    _init_git_repo(tmp_path)
+    _create_task_file(tmp_tasks, "backlog", "01", "Task A", ["Criterion A"])
+    _create_task_file(tmp_tasks, "backlog", "02", "Task B", ["Criterion B"])
+    real_open = open
+    state = {"failed_once": False}
+
+    def flaky_open(path, mode="r", *args, **kwargs):
+        if (
+            mode == "x"
+            and not state["failed_once"]
+            and str(path).endswith("-retry-bundle.md")
+        ):
+            state["failed_once"] = True
+            # A racer lands first: decoy with the contested ID.
+            decoy = Path(str(path)).parent / "03-decoy.md"
+            decoy.write_text("x", encoding="utf-8")
+            raise FileExistsError(str(path))
+        return real_open(path, mode, *args, **kwargs)
+
+    monkeypatch.setattr("builtins.open", flaky_open)
+    out = _bundler.bundle_tasks(
+        ["01", "02"], "retry bundle", dry_run=False, project_root=str(tmp_path)
+    )
+    assert "Created META task" in out, f"bundle failed:\n{out}"
+    metas = list((tmp_path / "tasks" / "backlog").glob("*-retry-bundle.md"))
+    assert len(metas) == 1
+    meta_text = metas[0].read_text(encoding="utf-8")
+    title_id = re.search(r"^# Task (\d+):", meta_text, re.MULTILINE).group(1)
+    assert metas[0].name.startswith(f"{int(title_id):02d}-"), (
+        f"stale META content: file {metas[0].name} carries title ID {title_id}"
+    )
+
+
+def test_rollback_restores_origin_and_header(
+    tmp_tasks: Path, tmp_path: Path, monkeypatch
+):
+    """B6: Failed archive must restore origin dir AND original File header."""
+    _init_git_repo(tmp_path)
+    _create_task_file(tmp_tasks, "in-progress", "01", "Task A", ["Criterion A"])
+    _create_task_file(tmp_tasks, "in-progress", "02", "Task B", ["Criterion B"])
+    original = (tmp_tasks / "in-progress" / "01-task-a.md").read_text(encoding="utf-8")
+    calls = [0]
+    real_mv = _bundler._git_mv_or_fallback
+
+    def flaky_mv(src: Path, dst: Path) -> bool:
+        calls[0] += 1
+        if calls[0] == 2:
+            return False
+        return real_mv(src, dst)
+
+    monkeypatch.setattr(_bundler, "_git_mv_or_fallback", flaky_mv)
+    out = _bundler.bundle_tasks(
+        ["01", "02"], "doomed", dry_run=False, project_root=str(tmp_path)
+    )
+    assert "rolled back" in out.lower() or "borted" in out.lower()
+    restored = tmp_path / "tasks" / "in-progress" / "01-task-a.md"
+    assert restored.is_file(), "first source was not restored to in-progress/"
+    assert restored.read_text(encoding="utf-8") == original, (
+        "rollback must restore byte-identical original content (File header included)"
+    )
+    assert not list((tmp_path / "tasks" / "backlog").glob("*-doomed.md")), (
+        "META file must be removed after rollback"
+    )
+
+
+def test_next_id_collision_helper(tmp_tasks: Path):
+    """B2: Same-ID-different-slug files must be detected either padding."""
+    (tmp_tasks / "backlog" / "06-taken.md").write_text("x", encoding="utf-8")
+    hits = _bundler._next_id_collision(tmp_tasks, 6)
+    assert hits, "padded 06-taken.md must collide with next_id 6"
+    (tmp_tasks / "backlog" / "7-loose.md").write_text("x", encoding="utf-8")
+    assert _bundler._next_id_collision(tmp_tasks, 7), (
+        "unpadded 7-loose.md must collide with next_id 7"
+    )
+    assert not _bundler._next_id_collision(tmp_tasks, 8)
+
+
+def test_extractor_blank_lines_and_nested(tmp_tasks: Path):
+    """B7: Blank-line paragraph breaks survive; nested boxes are items."""
+    from gitops import _extract_checklist_with_continuations as extract
+
+    section = (
+        "- [ ] Root item\n"
+        "  continuation paragraph\n"
+        "\n"
+        "  second paragraph\n"
+        "  - [ ] nested box\n"
+        "- [ ] Next root\n"
+    )
+    result = extract(section)
+    joined = "\n".join(result)
+    assert "continuation paragraph" in joined
+    assert "second paragraph" in joined, f"blank line split the item: {result}"
+    assert any(r == "- [ ] nested box" for r in result), (
+        f"nested box must be its own stripped item: {result}"
+    )
+
+
+def test_checksum_covers_short_criteria(tmp_tasks: Path):
+    """B8: Short criteria must be verified too, not skipped by length."""
+    _create_task_file(tmp_tasks, "backlog", "01", "Task A", ["Fix it"])
+    source_data = []
+    p = tmp_tasks / "backlog" / "01-task-a.md"
+    source_data.append(("01", p, p.read_text(encoding="utf-8"), "Task A"))
+    meta = _build_meta_content(100, "s", "S", ["01"], source_data)
+    assert _verify_verbatim_checksums(source_data, meta)
+    dropped = meta.replace("[01] Fix it", "[01] GONE")
+    assert not _verify_verbatim_checksums(source_data, dropped), (
+        "dropped short criterion must fail the checksum"
+    )
+
+
+def test_patch_multiword_status(tmp_tasks: Path):
+    """B9: Multi-word statuses must be replaced whole, dates aligned."""
+    from gitops import _patch_archived_file
+
+    p = tmp_tasks / "backlog" / "09-wip.md"
+    p.write_text(
+        "# Task 09: Wip\n\n**File:** `x`\n**Type:** bug\n**Status:** in progress\n",
+        encoding="utf-8",
+    )
+    _patch_archived_file(p, "10", "meta")
+    text = p.read_text(encoding="utf-8")
+    assert "**Status:** superseded\n" in text, f"status line corrupt:\n{text}"
+    assert "progress" not in [line for line in text.splitlines() if "Status" in line][0]
+    created_fmt = re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC", text)
+    assert created_fmt, f"Superseded-At must match Created datetime format:\n{text}"
```
<!-- END_GIT_DIFF -->
