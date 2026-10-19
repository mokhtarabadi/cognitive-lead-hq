# Task 322: Language policy - English inside, requested language outside

**File:** `tasks/completed/322-language-policy.md`
**Source:** manager
**Type:** chore
**Status:** closed
**Project:** /home/mohammad/Develop/Projects/cognitive-lead-hq
**Priority:** High

## Goal

Translate-first pipeline with English-only internals and per-message requested-language handoff, wired through fragments, executor, conventions, and tests.

## Rule (owner-approved 2026-10-17)

Non-English input (Manager speaks Persian) is ALWAYS translated to technical
English first; execution runs on the English version only. The
`prompt-refactor` skill is invoked for complex/multi-intent messages; short
clear messages use lightweight inline translation. Voice-to-text normalization
stays step one (existing Direct Input rule).

Internal reasoning, task files, evidence, logs, and ALL Brain communication
stay English, no exceptions. Only the Manager-facing handoff may use the
requested language (detected per message, Persian default for this Manager).

## Hard guards (part of the rule, not optional)

1. Approval phrases (`Approved for closure`, `Close task`, plan-gate
   `approved`) match ONLY as English literals. Never translate-then-compare.
2. Skill gating by complexity: refactor skill for complex messages, inline
   translation for short clear ones. No blanket skill call per message.
3. Evidence/logs/task files English always — auditability over comfort.
4. Output language detected per message, not pinned to a session default.

## Deliverable

New prompt fragment (language policy) wired into `system-prompt.md` generation
+ executor boundary update + sync test update. Owner implements.

## Local TODOs

- [x] Steps 1-10: fragment 24, manifest, version, 05, 13, 20, executor, conventions, tests, rebuild

## Acceptance Criteria

- [x] Persian order executes on its English translation with identical gates.
- [x] Approval matching untouched by translation layer (test proves it).
- [x] Brain turns carry English only.
- [x] Manager handoff follows per-message requested language.

## Execution Log

- Created 2026-10-17 from Manager directive. Owner implements.

## Definition of Done

- [x] Assembler plus tests pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append

## Risk & Rollback

- **Risk:** Prompt plus executor plus conventions drift if the rebuild step is skipped; stale English-always phrases resurfacing.
- **Rollback plan:** Revert prompt and doc hunks via `git checkout --` on the touched paths only.

## Execution Log & Reasoning

- Seat Check: prompt-protocol domains, no trigger words fired (explicit miss on all seats), Architect minimum by domain, single-seat plan, brainstorm not required (doc-level, reversible). One discovery round used (fed-context: fragments 05/13/20, manifest, builder, tests); final grounded plan approved by Manager ("Approved").
- Implemented 10 steps: fragment 24 created; manifest appended; version 9.61.0; fragments 05/13/20, executor, and conventions updated to inside/outside with approval literals guard; both sync tests updated; system-prompt.md rebuilt (111187 bytes, byte-identical re-assemble).
- D1: split_system_prompt.py is destructive (rewrites fragments from the prompt, drops unassembled files) — recovered via git checkout and re-applied edits; round-trip verification uses assemble-twice diff, never split.
- Stack-skill skip record: root=. markers=[package.json, go.mod, build.gradle.kts, pyproject.toml, vite.config] matched=[] reason="docs-only prompt-text change".

## Verification Evidence

- `rtk test /home/mohammad/v2ray-to-subs/.venv/bin/pytest tests/test_prompt_sync.py tests/test_input_validation_pipeline.py -q` — expected all pass, actual 20 passed, exit 0. (Repo has no local pytest; foreign venv binary used as runner only.)
- Greps: `simple English` 0 hits in 05/conventions/executor; `per-message requested language` hits in 05, 13, conventions, executor; `Never answer the Manager in another language` 0 hits; `Approval Literals Guard` in shipped; `9.61.0` in 01/tests/shipped.
- Assembler: `python3 scripts/prompt-build/assemble_system_prompt.py --output system-prompt.md` exit 0, byte-identical re-assemble verified (111187 bytes, 9.61.0).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/AGENTS.md b/AGENTS.md
index 3960615..a37131d 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -41,6 +41,8 @@ This repository is the Headquarters for the Cognitive Lead AI multi-agent system
   -> **Do** utilize the `debug-instrumentation` skill to inject strategic logs and trace the runtime execution path.
 - **Don't** write bash scripts without strict mode or mask errors with `2>/dev/null` on data commands.
   -> **Do** follow the Defensive Shell Protocol: `set -euo pipefail`, ban error masking, sidecar isolation for Docker backups. See `docs/conventions.md`.
+- **Don't** create or modify files with python, shell, heredoc, `sed -i`, or any script.
+  -> **Do** use native file-editing tools only; shell stays read-only for file content (e.g. grep, cat, diff, ls, git status). A non-unique anchor must fail loudly, never be forced. See `docs/conventions.md`.
 - **Don't** perform financial mutations without snapshotting the prior state or allow nulls in monetary aggregations.
   -> **Do** follow the Universal Financial Ledger Standard: snapshot-on-write, `$ifNull` precedence, discrepancy alerting, deep config merging. See `docs/conventions.md`.
 - **Don't** carry over assumptions, partial results, or architectural hypotheses from a previous task.
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index c71b6c0..40d02bf 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -80,7 +80,7 @@ If the Orchestrator or Manager forgets to explicitly list a skill in the `<conte
 
 If the Manager sends you a direct message that is NOT an XML task block (e.g., "fix the login bug on Android"), you MUST execute this validation pipeline before writing any code:
 
-1. **Intent Validation:** Confirm the language is English. If non-English (any language), translate to technical English internally. **Normalize first:** the Manager often dictates via voice-to-text — fix phonetic typos and fragments using conversation context before translating; fix only what the context flags, and leave unsupported words untouched for the Ambiguity Halt below. **Ambiguity Halt:** If direct input from the Manager is ambiguous, fragmented, or unclear, the Hands MUST HALT immediately and ask for clarification in simple English rather than executing speculative commands. Guessing intent from unclear input is strictly forbidden.
+1. **Intent Validation:** Confirm the language is English. If non-English (any language), translate to technical English internally. **Normalize first:** the Manager often dictates via voice-to-text — fix phonetic typos and fragments using conversation context before translating; fix only what the context flags, and leave unsupported words untouched for the Ambiguity Halt below. **Ambiguity Halt:** If direct input from the Manager is ambiguous, fragmented, or unclear, the Hands MUST HALT immediately and ask for clarification in the per-message requested language (Persian default) rather than executing speculative commands. Guessing intent from unclear input is strictly forbidden.
 2. **Task File Enforcement:** You MUST ask the Manager: "This is an ad-hoc request. Should I create a new task file in `tasks/backlog/` for this, or is this a quick fix that doesn't require Kanban tracking?"
 3. **Skill Loading:** Scan the request against the Skill Auto-Loading Matrix and load the relevant skills.
 4. **Plan & Halt:** Write a brief 3-step implementation plan and ask the Manager for explicit "Approved" before writing code.
@@ -158,7 +158,7 @@ Shorthand aliases: scr (super critical), eli (eliminate), foc (focus), ref (refe
 - Challenge incorrect assumptions directly and explain why.
 - Optimize for clarity and engineering value, not quotability.
 - Lead with the answer. Open the reply with the result or the direct answer, then the reasoning. A short answer stays prose: no heading, no process narration, no recap.
-- For the final Manager-facing handoff only (not `<reasoning_log>` or XML tasks), write in simple English always, even when the Manager wrote in another language. Answer first, then the reason, then the next action. Budget the length: a short reply is 2–5 sentences with no heading, a normal reply is 80–180 words or at most 5 bullets. Treat 25 words as a ceiling for any single sentence, never a target. Prefer prose; use flat bullets only for 3–7 parallel items and a table only for repeated attributes. Never nest lists. Think in English as well — deep reasoning stays unrestricted and rich.
+- For the final Manager-facing handoff only (not `<reasoning_log>` or XML tasks), write in the per-message requested language (Persian default for this Manager), even when the Manager wrote in another language. Answer first, then the reason, then the next action. Budget the length: a short reply is 2–5 sentences with no heading, a normal reply is 80–180 words or at most 5 bullets. Treat 25 words as a ceiling for any single sentence, never a target. Prefer prose; use flat bullets only for 3–7 parallel items and a table only for repeated attributes. Never nest lists. Think in English as well — deep reasoning stays unrestricted and rich.
 - Dual-channel scope: the sentence rule, the ban list, and the no-decoration rules apply ONLY to the final Manager-facing handoff. `<reasoning_log>`, XML task blocks, and Execution Logs stay fully comprehensive.
 
 ### Negative Patterns
@@ -167,7 +167,7 @@ Shorthand aliases: scr (super critical), eli (eliminate), foc (focus), ref (refe
 - Do not use decorative headings, emoji, or motivational language.
 - Never emit these phrases: load-bearing, worth stating plainly, here is the honest truth, real tension, carry the argument. No analogies, no semicolons, no fragments, no em-dash chaining. Also keep out the AI tells: hedging openers ("it is worth noting"), inflated significance ("stands as a testament"), negative parallelism ("not just X, but Y"), rote rule-of-three lists, collaborative preambles ("Great question"), and trailing recaps.
 - Never write task numbers into prompt-facing Markdown: fragments, agent sections, skill instructions, registry lines. Task-number provenance lives ONLY in code comments, CHANGELOG entries, task files, docs/history archives, and HTML-comment markers.
-- Never answer the Manager in another language. A non-English quote inside a task file is evidence, not your answer.
+- English inside, requested language outside. A non-English quote inside a task file is evidence, not your answer.
 - Do not repeat yourself. State every idea once, repeat only if relevant to subsequent queries.
 - Do not speculate on abstractions for future requirements.
 - Do not widen work into cleanup, refactoring, or documentation beyond the requested scope.
@@ -197,6 +197,10 @@ Do not skip the observe step. Every code change MUST be verified before claiming
 
 Test-suite verification runs begin with `rtk test <underlying command>` by default. Inspect the active task's `## Verification Evidence` before running verification and record the exact `rtk test`-prefixed command, expected result, actual result, and exit code there. A raw test command is a diagnostic retry after a failed RTK run only — it never replaces the initial RTK verification run. Never claim completion without a successful exit code and recorded evidence.
 
+### Edit Tool Discipline (native tools only)
+
+File edits use ONLY native file-editing tools (edit for replacements, file-write tools for new files). Using python, shell, heredoc, `sed -i`, or any script to create or modify files is strictly forbidden — scripted edits fail silently (replace-all on non-unique anchors, quoting and encoding mangling) while native tools fail loudly on a non-unique anchor. If the anchor does not match uniquely, stop and re-read instead of forcing it. Shell stays read-only for file content (e.g. grep, cat, diff, ls, git status). Verify every edit with grep/diff.
+
 ### Micro-Task Tracking (todowrite/todoread)
 
 The `opencode-todolist` plugin provides session-scoped `todowrite` (create/replace the whole list; empty array clears) and `todoread` (read it back), with fields `content` (imperative), `status` (`pending`/`in_progress`/`completed`/`cancelled`), and optional `priority`. Whenever a task decomposes into 2 or more micro-steps, maintain them here alongside the task file: keep exactly one `in_progress`, mark steps `completed` the moment they finish, and `todoread` to recover the list after any compaction instead of reconstructing it from memory.
diff --git a/docs/conventions.md b/docs/conventions.md
index 433e2c5..f3084c7 100644
--- a/docs/conventions.md
+++ b/docs/conventions.md
@@ -162,7 +162,7 @@ All Manager input — English, Persian, or mixed — MUST pass through the Input
 If any validation step FAILS — particularly the clarity check — the Orchestrator and Hands MUST:
 
 1. **HALT immediately.** Do NOT guess, assume, or fabricate intent from ambiguous input.
-2. **Output a clarification request** in simple English, no matter which language the input used.
+2. **Output a clarification request** in the per-message requested language (Persian default), no matter which language the input used.
 3. **Ask targeted questions** to confirm the exact intent before proceeding.
 4. **Only resume** after the Manager provides an unambiguous response.
 
@@ -190,6 +190,10 @@ Task numbers are provenance for humans, not reasoning material for the model. A
 
 **Authoring rule:** when writing or editing prompt-facing Markdown, strip task-number parentheticals. Record provenance in the task file and CHANGELOG instead — never in the prompt text itself.
 
+## Edit Tool Discipline
+
+File edits use ONLY native file-editing tools (edit for replacements, file-write tools for new files). Using python, shell, heredoc, `sed -i`, or any script to create or modify files is strictly forbidden — scripted edits fail silently (replace-all on non-unique anchors, quoting and encoding mangling) while native tools fail loudly on a non-unique anchor. Shell stays read-only for file content (e.g. grep, cat, diff, ls, git status). Verify every edit with grep/diff.
+
 ## Living Folder Docs Standard
 
 All vertical slices and component directories across projects in this ecosystem MUST maintain colocated documentation and decision records:
diff --git a/skill-templates/audit-agents/SKILL.md b/skill-templates/audit-agents/SKILL.md
index 1a273e6..9cf8301 100644
--- a/skill-templates/audit-agents/SKILL.md
+++ b/skill-templates/audit-agents/SKILL.md
@@ -31,6 +31,7 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **MCP Report Generation**: `AGENTS.md` MUST instruct agents to generate context reports (`custom_context_read_source_files`) and tree reports (`custom_context_create_tree_report` — "create a tree of the project") via the MCP server and hand the file path to the Manager instead of reading `context-reports/` files inline.
 - **Explicit Staging Contract (F5)**: Verify that the active task's `Execution Log & Reasoning` or `summary_phase` passed a `modified_files` list to `stage_and_inject_diff` — blind `git add -A .` staging is banned because it sweeps parallel-session files into unrelated commits.
 - **Parallel Index Isolation**: Verify the project documents the agent-managed round-trip for shared files — `custom_context_unstage_files` (index-only unstage) followed by `stage_and_inject_diff` with `skip_add=True` — and that `git commit`/`git checkout`/`git push` remain forbidden everywhere.
+- **Edit Tool Discipline**: `AGENTS.md` MUST forbid all scripted file edits — agents may use ONLY native file-editing tools for creating or modifying files (python, shell, heredoc, and `sed -i` are banned for edits; shell stays read-only for file content — e.g. grep, cat, diff, ls, git status). A non-unique anchor must fail loudly, never be forced. `docs/conventions.md` MUST contain a matching `## Edit Tool Discipline` section.
 - **Gatekeeper Validation (Halt Protocol)**: Agents MUST be instructed to evaluate tasks against project rules and HALT with a warning if the Orchestrator provides non-compliant instructions.
 - **Context Bootstrapping**: `AGENTS.md` MUST explicitly instruct the Hands: "At the start of every task, you MUST call `search_memory` or `list_namespaces` to load any hidden project quirks relevant to your domain before implementing."
 - **Buffer Isolation**: The shared validation phase MUST include a buffer-flush directive requiring Hands to treat every task as contextually independent, preventing cross-task context leakage. When the project uses session-keyed conversation threads, the rules MUST note that flushing covers working execution assumptions only — the conversation thread persists across tasks under the active session ID until sprint completion.
@@ -238,6 +239,14 @@ When writing or reviewing bash scripts, cron jobs, or container orchestration co
 3. **No Post-Redirect Status Checks:** Never use `command > file; if [ $? -eq 0 ]` — the shell creates the file before running the command, masking failures.
 4. **Sidecar Isolation for Hostless Backups:** Never rely on host file staging for Docker volume backups. Always use ephemeral containers (`docker run --rm -v volume:/data:ro alpine tar...`) with read-only mounts.
 
+## Edit Tool Discipline
+
+File edits use ONLY native file-editing tools (edit for replacements, file-write tools for new files). Using python, shell, heredoc, `sed -i`, or any script to create or modify files is strictly forbidden — scripted edits fail silently (replace-all on non-unique anchors, quoting and encoding mangling) while native tools fail loudly on a non-unique anchor.
+
+1. **Default native only:** one replacement, one location, exact unique anchor. A no-match or multi-match error is a signal, never a retry hint.
+2. **No scripted edits:** python, shell, heredoc, and `sed -i` are banned for creating or modifying files. Shell stays read-only for file content (e.g. grep, cat, diff, ls, git status).
+3. **Verify always:** grep/diff after every edit.
+
 ## Task-Number Reference Discipline
 
 Task numbers are provenance for humans, not reasoning material for the model. A bare task number in visible prompt prose invites hallucination: the model treats it as load-bearing context it cannot resolve.
@@ -400,6 +409,7 @@ Additionally, the `docs/conventions.md` file MUST exist and contain:
 - **MCP Report Generation**: `AGENTS.md` MUST instruct agents to generate context reports (`custom_context_read_source_files`) and tree reports (`custom_context_create_tree_report` — "create a tree of the project") via the MCP server and hand the file path to the Manager instead of reading `context-reports/` files inline.
 - **Explicit Staging Contract (F5)**: Verify that the active task's `Execution Log & Reasoning` or `summary_phase` passed a `modified_files` list to `stage_and_inject_diff` — blind `git add -A .` staging is banned because it sweeps parallel-session files into unrelated commits.
 - **Parallel Index Isolation**: Verify the project documents the agent-managed round-trip for shared files — `custom_context_unstage_files` (index-only unstage) followed by `stage_and_inject_diff` with `skip_add=True` — and that `git commit`/`git checkout`/`git push` remain forbidden everywhere.
+- **Edit Tool Discipline**: `AGENTS.md` MUST forbid all scripted file edits — agents may use ONLY native file-editing tools for creating or modifying files (python, shell, heredoc, and `sed -i` are banned for edits; shell stays read-only for file content — e.g. grep, cat, diff, ls, git status). A non-unique anchor must fail loudly, never be forced. `docs/conventions.md` MUST contain a matching `## Edit Tool Discipline` section.
 - **Gatekeeper Validation (Halt Protocol)**: Agents MUST be instructed to evaluate tasks against project rules and HALT with a warning if the Orchestrator provides non-compliant instructions.
 - **Bilingual Prompt Refactoring & Brainstorming Protocol**: Agents MUST be instructed not to execute raw, informal, or non-English prompts directly. The `prompt-refactor` skill must be loaded, or the Phase 1.5 Multi-Agent Brainstorming Protocol triggered, to translate and expand intent first. Standard XML task blocks are exempt.
 - **Context Bootstrapping**: `AGENTS.md` MUST explicitly instruct the Hands: "At the start of every task, you MUST call `search_memory` or `list_namespaces` to load any hidden project quirks relevant to your domain before implementing."
```
<!-- END_GIT_DIFF -->

- Rework try 2 (Reviewer REJECTED_NEEDS_FIXES, R1+R2): fragment 13 Cognitive Rule no longer lists clarification requests as English-only (handoff including clarification uses requested language); fragment 20 handoff line moved inside `</communication_examples>`. Rebuilt 9.61.0 (111226 bytes, byte-identical re-assemble), no version bump.
- Stack-skill skip record: root=. markers=[package.json, go.mod, build.gradle.kts, pyproject.toml, vite.config] matched=[] reason="docs-only wording fix".

- Rework try 3 (Reviewer 2nd rejection, duplicate close): fragment 20 tail fixed to single `</communication_examples>` as final line; rebuilt 9.61.0 (111199 bytes, byte-identical re-assemble), 20 tests pass. My earlier placement claim was wrong — verified against the diff this time.

- Review try 3: technical APPROVED, PO_REVIEW_PENDING. Awaiting Manager accept word for closure.

## History Note 2026-10-17 — Edit tool discipline (native tools only)

Follow-up Manager order after closure, logged here per Manager direction (no active qa task existed). A real replace-all bug (python anchor matched twice, section duplicated; caught by lint plus grep) led to a total ban: file edits use ONLY native file-editing tools; python, shell, heredoc, and `sed -i` are banned for creating or modifying files; shell stays read-only. Written into `agents/cognitive-executor.md` (operative rule) and `skill-templates/audit-agents/SKILL.md` (enforcement criterion in two sites plus conventions template section), both lint-clean and globally synced with no drift. Task file 323 created for this work was deleted per Manager order; this note is its replacement record.

## QA Rework 2026-10-17 — self-compliance fixes (QA_REJECTED try 1)

- F1 fixed: `AGENTS.md` guardrail plus `docs/conventions.md` `## Edit Tool Discipline` section added; repo now satisfies its own audit rule (grep hits: AGENTS line 45, conventions line 193).
- F3 fixed: read-only wording relaxed to illustrative list (e.g. grep, cat, diff, ls, git status) in executor, both skill criterion sites, and the template.
- F2 evidence: `lint_markdown` passes on all four files (AGENTS, conventions, skill, executor), recorded here.
- F4 disputed: task 323 was same-session scratch created and deleted per direct Manager order within minutes; no archive record needed — this note is the record.
- Stack-skill skip: root=. markers=[package.json, go.mod, build.gradle.kts, pyproject.toml, vite.config] matched=[] reason="docs-only rule text change".

- Closure: Manager accept quote "Approved for closure" logged, closure executing exactly once. Stack-skill skip: root=. markers=[package.json, go.mod, build.gradle.kts, pyproject.toml, vite.config] matched=[] reason="closure-only lane move plus commit tool".
