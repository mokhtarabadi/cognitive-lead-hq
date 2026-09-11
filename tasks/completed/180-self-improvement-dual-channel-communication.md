# Task 180: Self-improvement — dual-channel communication (concise manager, comprehensive machine)

**File:** `tasks/qa/180-self-improvement-dual-channel-communication.md`
**Source:** manager
**Type:** improvement
**Status:** in-progress

## Goal

Make Brain + Cognitive Executor manager-facing output short and human-readable while keeping machine-facing XML tasks fully comprehensive, with zero performance impact — by folding in the best patterns from disler/fixing-smartass-opus-5, obra/superpowers, and Anthropic prompting best practices.

## Manager's Notes

Manager request (Farsi, translated to technical English with typos fixed):

> "Define a task for yourself to improve yourself. First translate what I am telling you now into English, fix its spelling errors, then execute it. Start searching the internet — you are free. Search the internet for hours, find different things; using your own style is much better. I want you to improve yourself: in the system prompt you are working with, first know your own nature, then I want working with you to be easier for me as the manager. Right now your output to me is a bit complex — reading the output produced in the Brain is really a bit complex for me. I want a good output: as minimal as possible, with absolutely zero impact on performance — I want the best performance from you — but the text you write for me the manager, because I am human: a high volume of data and text is really hard for me to read. Both in the system-prompt output and in the cognitive-executor output. But in the XML tasks you write it must be 100% comprehensive, because that is machine-to-machine, it does not matter. The more context and explanation you give it, the better it can handle the job. But I as the manager really do not need that volume of explanation. Search the internet for people who set up such systems (e.g. Superpowers), the best prompts used for coding/prompt-writing, the key points inside the system prompts of famous programs/agents such as Claude itself, Claude Code, Codex — read them, learn from them, and define a task to improve yourself: much better performance, much better XML tasks, much more precise understanding when the manager talks to you, and when you talk to the manager speak like a human so it is easy to understand. Do deep searches, follow each clue into the next search in a chain, find everything needed, improve yourself. I also sent two links — look at them if you like. I deal with the system prompt in the Brain and with the cognitive-executor in the Hands (OpenCode). Write these to the best possible level for system performance; the system's nature must become truly professional, even better."
>
> Reference sent by manager: `disler/fixing-smartass-opus-5` (resolved to https://github.com/disler/fixing-smartass-opus-5).

Research already performed (chain): disler `sr_opus_5_system_prompt.md` fetched verbatim; obra/superpowers repo mapped (285k stars, skills workflow); Anthropic `claude-prompting-best-practices` fetched with focus filter (XML structuring, Opus 5 verbosity rule, output-style matching).

Key findings to encode (F1–F5):

- F1 (disler): ban list + no flattery/analogy/em-dash-chaining/semicolons; state each fact once; match detail to task; reference codes D/O/F/R/Q/A for 3+ items; hard scope boundaries; no completion claim without evidence; aliases scr/eli/foc/ref; concrete DO/DON'T pairs.
- F2 (superpowers): composable skills with mandatory invocation; design shown to human in short digestible chunks for sign-off; plans written so a context-less junior can follow (exact paths, complete code, verification); two-stage review (spec compliance then quality); TDD red-green-refactor; severity-graded review.
- F3 (Anthropic): XML tags disambiguate instructions/context/input; explicit conciseness prompt required for Opus 5 (effort levels do not control verbosity); match prompt style to desired output style; few-shot DO/DON'T examples are the most reliable steering.
- F4 (diagnosis, this repo): `<agentic_reasoning>` fragment 08 forces a full 9-step `<reasoning_log>` before EVERY Brain response — including pure manager conversation. That is the main verbosity driver the manager feels. Machine XML path needs it; human chat path does not.
- F5 (diagnosis, this repo): fragment `20-communication_examples.md` is thin (2 examples, no ban list, no codes, no dual-channel rule). Executor file already has reference codes + ≤25-word manager sentences, but lacks the ban list, aliases, and explicit dual-channel scoping.

## Local TODOs

- [x] Expand `prompts/fragments/20-communication_examples.md` with dual-channel contract + ban list + codes + aliases + DO/DON'T examples
- [x] Clarify executor `Communication Patterns` with ban list + aliases + dual-channel scope (reasoning_log/XML stay rich)
- [x] Bump `01-system_version.md` 9.13.0 → 9.14.0, reassemble system-prompt.md, verify sync
- [x] Update CHANGELOG.md, lint task file, stage + inject diff, move to qa
- [x] Round 2: contradiction audit (N vs not-N scan across fragments, skill, executor)
- [x] Round 2: realign brainstorming to seven system personas + embedded schema + selection rule
- [x] Round 2: bump 9.14.0 → 9.15.0, reassemble, verify, CHANGELOG, re-lint, re-stage
- [x] Round 3: drop `brainstorm-swarm` + `perplexity-research` skills entirely (repo + global + registry/matrix/README/LLM.txt refs); protocol is sole brainstorming path
- [x] Round 3: bump 9.15.0 → 9.16.0, reassemble, verify, CHANGELOG, re-lint, re-stage

## Acceptance Criteria

- [x] Manager-facing Brain output governed by a concise-output contract (short sentences, ban list, codes, no flattery) without weakening any machine-path instruction
- [x] XML task templates and `<reasoning_log>` explicitly exempted from conciseness (machine-to-machine stays comprehensive)
- [x] `system-prompt.md` regenerated from fragments and byte-identical to assembler output (sync verified)
- [x] Version bumped to 9.14.0 in fragment source (not hand-edited in generated file)
- [x] CHANGELOG.md entry added; `lint_task_file` passes on the task file
- [x] Round 2: no definition contradicts another (old six-persona panel, phantom `ui-system` skill, phantom `/reflect` command all eliminated; dangling schema pointer resolved by embedding it)
- [x] Round 2: brainstorming runs the seven declared system personas, builds the `brainstorming_session` block, and the final plan must cite it to select the best path
- [x] Round 2: version 9.15.0, sync verified, CHANGELOG entry added
- [x] Round 3: both skills fully dropped (dirs deleted, zero stale refs in fragments/executor/prompt/README/LLM.txt); protocol declares itself the only brainstorming path; research covered by `blowsh`
- [x] Round 3: version 9.16.0, sync verified, CHANGELOG entry added

## Verification Evidence

- **Test command:** `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check180.md && diff /tmp/check180.md system-prompt.md && echo SYNC_OK`
- **Expected result:** `SYNC_OK`, zero diff lines
- **Actual result:** `SYNC_OK`, zero diff lines; generated file 75587 bytes, contains `9.14.0`
- **Exit code:** 0
- **Round 2 test command:** same assembler check to `/tmp/check180b.md` + `grep -n "system_architect\|ui-system\|/reflect\|critical_thinker" system-prompt.md prompts/fragments/*.md skill-templates/brainstorm-swarm/SKILL.md agents/cognitive-executor.md`
- **Round 2 expected result:** `SYNC_OK`; grep prints nothing (zero stale references)
- **Round 2 actual result:** `SYNC_OK`, 76962 bytes, contains `9.15.0`, grep empty
- **Round 2 exit code:** 0
- **Round 3 test command:** same assembler check to `/tmp/check180r3.md` + `grep -rn "brainstorm-swarm\|perplexity-research" prompts/fragments/ agents/ system-prompt.md README.md LLM.txt`
- **Round 3 expected result:** `SYNC_OK`; grep prints nothing (zero stale references)
- **Round 3 actual result:** `SYNC_OK`, 76538 bytes, contains `9.16.0`, grep empty; repo holds 31 skill dirs, global clean
- **Round 3 exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a separate closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Conciseness rule bleeds into XML/reasoning path and starves the Hands of context.
- **Rollback plan:** Revert fragments + regenerate (`git diff` on `prompts/fragments/20-communication_examples.md`, `agents/cognitive-executor.md`, `system-prompt.md`); re-run assembler; previous version 9.13.0 recoverable from git history.

---

## Execution Log & Reasoning

Implemented the manager-ordered self-improvement (Task 180) after chained research (disler sr_opus_5 prompt, obra/superpowers, Anthropic best practices — see Manager's Notes F1–F5).

Diagnosis: the verbosity the manager feels comes from fragment 08 forcing a full 9-step `<reasoning_log>` before every Brain response including pure chat, plus thin communication examples (fragment 20 had only 2 examples, no ban list, no dual-channel rule).

Changes (docs-only, zero `.py` touched, zero performance impact on machine path):
1. `prompts/fragments/20-communication_examples.md` — added dual-channel contract header, banned-phrase list, style bans, D/O/F/R/Q/A codes with scr/eli/foc/ref aliases, and Example 3 (status update DO/DON'T).
2. `prompts/fragments/08-agentic_reasoning.md` — pure Manager conversation exempted from the 9-step log (3-line verdict instead); full log stays mandatory before every XML task block.
3. `agents/cognitive-executor.md` — Communication Patterns gain alias row, dual-channel scope line, and ban list. Machine channels (`<reasoning_log>`, XML, Execution Logs) explicitly stay comprehensive.
4. `prompts/fragments/01-system_version.md` 9.13.0 → 9.14.0; `system-prompt.md` reassembled (75587 bytes, sync-check `SYNC_OK` byte-identical).
5. `CHANGELOG.md` — new `## [9.14.0]` entry, Keep-a-Changelog format.

No scope creep: no template, skill, or server logic touched.

Round 2 (manager order: contradiction audit + brainstorming check, all inside this task):
F6: brainstorm panel (six outside personas) contradicted the seven declared `<personas>` and broke the 02-role declaration contract. C1/C3 retracted (skill file exists, restored Task 175 — verified on disk). C4: skill pointed at a report schema that existed nowhere. Fixed by rewriting fragment 12 (seven-seat panel, embedded report_schema, selection_rule with citation mandate) and realigning the skill + registry line. C6: phantom `ui-system` skill alternative removed from 06. C7: phantom `/reflect` command trigger corrected to chat phrase in 21. Executor references outside the paused block are clean (only the valid skill-matrix row). Self-caught typo (stray non-ASCII token in skill frontmatter) fixed and ASCII-scanned.
Files round 2: `prompts/fragments/{12-brainstorming_protocol,07-agent_skills_registry,06-personas,21-self_improvement_protocol,01-system_version}.md`, `skill-templates/brainstorm-swarm/SKILL.md`, `system-prompt.md`, `CHANGELOG.md`.

Round 3 (manager order: drop `brainstorm-swarm` + `perplexity-research` skills entirely; protocol is the sole Brain-side brainstorming path; research via `blowsh`; all inside this task):
Deleted `skill-templates/brainstorm-swarm/` + `skill-templates/perplexity-research/` (tracked, `rm` + staged deletions) and the global installs under `~/.config/opencode/skills/`. Removed both registry lines from fragment 07, the `brainstorm-swarm` auto-load row from the executor matrix, the `perplexity-research` README tree entry; synced counts to 31 skills (README, `LLM.txt` x2). Fragment 12 panel now declares itself the only brainstorming path (no new tag — inline sentence, splitter-safe; a `<sole_path>` attempt was reverted after it ate the `</selection_rule>` close, then repaired and verified). Fragment 12 otherwise untouched: seven-seat panel, schema, selection_rule intact. Out of scope, left for manager: `user-prompts/{multi-agent-brainstorming,perplexity-deep-research}.md` copy-paste templates and dated memory shards. Version 9.15.0 → 9.16.0, reassembled `SYNC_OK` (76538 bytes), zero stale refs, CHANGELOG `## [9.16.0]` entry.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index e053362..d86a3b4 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,18 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+## [9.15.0] - 2026-09-11
+
+### Fixed
+
+- **Contradiction audit + brainstorming realignment (Task 180 round 2, manager order):** Audit proved the brainstorm system contradicted the declared personas — fragment 12 and the skill ran six outside personas (`system_architect`, `security_engineer`, `product_manager`, `business_strategist`, `legal_advisor`, `critical_thinker`) that exist nowhere in `<personas>`, breaking the 02-role declaration contract, and the skill pointed at a `report_schema` that was never defined. Fixes: (1) `prompts/fragments/12-brainstorming_protocol.md` rewritten — panel is exactly the seven `<personas>` seats, Brain declares each seat in brackets, sequential independent analysis, embedded `report_schema` (summary, persona_responses, tradeoffs T1/T2, conflict_resolution, options_ranked O1/O2, final_recommendation with refs, selected_path), and a `selection_rule` forcing the final plan to cite winning option id plus deciding tradeoff ids, with the full block pasted into the backlog task as reference; (2) `skill-templates/brainstorm-swarm/SKILL.md` realigned to the same seven-seat panel (devil's advocacy folded into QA Engineer, cross-domain coverage mapped to Architect/Planner/Strategist/Reviewer duties); (3) registry line in fragment 07 updated; (4) phantom `ui-system` skill alternative removed from 06-personas; (5) phantom `/reflect` slash trigger in fragment 21 corrected to plain chat phrase (no command file exists while automation is paused). Verified: zero remaining references to old persona names, `ui-system`, or `/reflect` across fragments, generated prompt, skill, and executor. Reassembled `system-prompt.md` (sync-check byte-identical).
+
+## [9.14.0] - 2026-09-11
+
+### Changed
+
+- **Dual-channel communication — concise manager, comprehensive machine (Task 180, manager self-improvement order):** Manager-facing output is now short and human-readable while XML task blocks, `<reasoning_log>`, blueprints, and Execution Logs stay fully comprehensive — zero performance impact (fewer tokens on the chat path, identical context on the machine path). Changes: (1) `prompts/fragments/20-communication_examples.md` gains the dual-channel contract, a banned-phrase list (load-bearing, worth stating plainly, here is the honest truth, real tension, carry the argument), style bans (no analogies, flattery, emoji, em-dash chaining, semicolons, fragments), reference codes D/O/F/R/Q/A with scr/eli/foc/ref aliases, and a new Example 3 status-update DO/DON'T pair; (2) `prompts/fragments/08-agentic_reasoning.md` exempts pure Manager conversation from the 9-step `<reasoning_log>` — a 3-line verdict (decision, reason, next step) replaces it, full log stays mandatory before every XML task block; (3) `agents/cognitive-executor.md` Communication Patterns gain the alias row, the dual-channel scope line, and the ban list. Patterns learned from chained research: disler `fixing-smartass-opus-5` system prompt, obra `superpowers` agent workflow, Anthropic prompt-engineering best practices (XML structuring, explicit conciseness for Opus 5). Reassembled `system-prompt.md` (sync-check byte-identical).
+
 ## [9.13.0] - 2026-09-10
 
 ### Added
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 4305034..7d4e88e 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -115,6 +115,8 @@ When presenting three or more findings, decisions, options, risks, questions, or
 
 Preserve the same codes throughout the conversation. Do not create codes for short simple answers.
 
+Shorthand aliases: scr (super critical), eli (eliminate), foc (focus), ref (reference).
+
 ### Positive Patterns
 
 - State each fact once. Match detail level to task complexity.
@@ -124,11 +126,13 @@ Preserve the same codes throughout the conversation. Do not create codes for sho
 - Challenge incorrect assumptions directly and explain why.
 - Optimize for clarity and engineering value, not quotability.
 - For the final Manager-facing handoff only (not `<reasoning_log>` or XML tasks), keep sentences ≤25 words, one idea per sentence, defined context before pronoun reference, active voice — deep reasoning stays unrestricted and rich.
+- Dual-channel scope: the sentence rule, the ban list, and the no-decoration rules apply ONLY to the final Manager-facing handoff. `<reasoning_log>`, XML task blocks, and Execution Logs stay fully comprehensive.
 
 ### Negative Patterns
 
 - Do not flatter, praise, validate, or agree without reason.
 - Do not use decorative headings, emoji, or motivational language.
+- Never emit these phrases: load-bearing, worth stating plainly, here is the honest truth, real tension, carry the argument. No analogies, no semicolons, no fragments, no em-dash chaining.
 - Do not repeat yourself. State every idea once, repeat only if relevant to subsequent queries.
 - Do not speculate on abstractions for future requirements.
 - Do not widen work into cleanup, refactoring, or documentation beyond the requested scope.
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 7ecb219..e123cf6 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.13.0</system_version>
+<system_version>9.15.0</system_version>
diff --git a/prompts/fragments/06-personas.md b/prompts/fragments/06-personas.md
index b8184a0..e6c972f 100644
--- a/prompts/fragments/06-personas.md
+++ b/prompts/fragments/06-personas.md
@@ -8,7 +8,7 @@
   <persona name="UI/UX Designer">
     <trigger>Frontend features, layout changes, component creation, or styling tasks.</trigger>
     <duty>Design systems, user journey mapping, strict accessibility (a11y), responsive design, and local `DESIGN.md` management.</duty>
-    <behavior>Define the visual strategy before implementation. **Discovery-First Mandate:** Do not hallucinate layouts; demand codebase context first. **Environmental Checklist:** Your designs must account for offline states, network latency, Dark/Light mode contrast, and a11y (screen readers, keyboard focus) — not just the 'Happy Path'. Use `mermaid` user journey maps (`journey`) or flowcharts to illustrate UI navigation flows when helpful. Enforce component isolation (e.g., Storybook-friendly patterns). Collaborate with the Architect for data-fetching strategies. Instruct the Programmer to enforce UI-specific design tokens (colors, spacing), component states, and stack-specific UI guidelines in local `DESIGN.md` following Google's official spec (YAML tokens + prose) or a local `ui-system` skill, via Hands tasks. Ensure `DESIGN.md` is validated against the spec using `npx @google/design.md lint DESIGN.md` inside task executions.</behavior>
+    <behavior>Define the visual strategy before implementation. **Discovery-First Mandate:** Do not hallucinate layouts; demand codebase context first. **Environmental Checklist:** Your designs must account for offline states, network latency, Dark/Light mode contrast, and a11y (screen readers, keyboard focus) — not just the 'Happy Path'. Use `mermaid` user journey maps (`journey`) or flowcharts to illustrate UI navigation flows when helpful. Enforce component isolation (e.g., Storybook-friendly patterns). Collaborate with the Architect for data-fetching strategies. Instruct the Programmer to enforce UI-specific design tokens (colors, spacing), component states, and stack-specific UI guidelines in local `DESIGN.md` following Google's official spec (YAML tokens + prose), via Hands tasks. Ensure `DESIGN.md` is validated against the spec using `npx @google/design.md lint DESIGN.md` inside task executions.</behavior>
 </persona>
 
   <persona name="Senior Programmer">
diff --git a/prompts/fragments/07-agent_skills_registry.md b/prompts/fragments/07-agent_skills_registry.md
index 877d22d..bf6a54a 100644
--- a/prompts/fragments/07-agent_skills_registry.md
+++ b/prompts/fragments/07-agent_skills_registry.md
@@ -21,7 +21,7 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **verification-before-completion**: Mandatory rule before claiming any task is complete, fixed, or passing.
 - **perplexity-research**: Triggers a human-in-the-loop deep research cycle using the Perplexity 3-Step Framework. Use when encountering post-2025 dependencies, undocumented API errors, or complex hardware/system bugs.
 - **github**: GitHub CLI (gh) workflow for pull request triage, issue management, CI/CD run analysis, and API queries.
-- **brainstorm-swarm**: Orchestrates a multi-expert brainstorming session using six specialized personas (system_architect, security_engineer, product_manager, business_strategist, legal_advisor, critical_thinker) to resolve cross-disciplinary ambiguity. Outputs structured XML-tagged session reports.
+- **brainstorm-swarm**: Multi-seat brainstorming using exactly the seven system personas from `<personas>`, each arguing from its defined duty. Outputs a structured `brainstorming_session` report (schema in `<brainstorming_protocol>`) that the final plan must cite to justify the selected path.
 - **blowsh**: Web search, fetch, crawl, and link extraction via the blowsh MCP server (Docker transport) — rendered search engines, JS-rendered page fetch, sitemap-aware crawls. Use for all live-web research instead of raw curl.
 
 **Stack-Specific Blueprints (Load if matching the project):**
diff --git a/prompts/fragments/08-agentic_reasoning.md b/prompts/fragments/08-agentic_reasoning.md
index 0b93956..4e3f8b2 100644
--- a/prompts/fragments/08-agentic_reasoning.md
+++ b/prompts/fragments/08-agentic_reasoning.md
@@ -43,5 +43,5 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 
 9. Inhibit your response: only take an action after all the above reasoning is completed. Once you've taken an action, you cannot take it back.
 
-10. Visible reasoning (Critical): Since you rely on token generation to reason effectively, you MUST NOT keep these 9 steps hidden. Before outputting any template or final response, you MUST output a <reasoning_log> block where you write down your analysis for steps 1–9. This entire reasoning log MUST strictly be written in English. ONLY AFTER closing the </reasoning_log> tag are you allowed to output the task blocks or talk to the Manager.
+10. Visible reasoning (Critical): Since you rely on token generation to reason effectively, you MUST NOT keep these 9 steps hidden. Before outputting any template or final response, you MUST output a <reasoning_log> block where you write down your analysis for steps 1–9. This entire reasoning log MUST strictly be written in English. ONLY AFTER closing the </reasoning_log> tag are you allowed to output the task blocks or talk to the Manager. Exception: pure Manager conversation with no task block needs no 9-step log. Give a 3-line verdict instead (decision, reason, next step). The full log stays mandatory before every XML task block or template response.
 </agentic_reasoning>
\ No newline at end of file
diff --git a/prompts/fragments/12-brainstorming_protocol.md b/prompts/fragments/12-brainstorming_protocol.md
index 1475cdb..68f291b 100644
--- a/prompts/fragments/12-brainstorming_protocol.md
+++ b/prompts/fragments/12-brainstorming_protocol.md
@@ -1,6 +1,8 @@
 <brainstorming_protocol>
 <phase>Phase 1.5: Multi-Agent Brainstorming Loop</phase>
 <trigger>Manager explicitly requests brainstorming, or after Intent Expansion the task exhibits cross-disciplinary ambiguity that cannot be resolved by a single persona.</trigger>
-<workflow>When triggered, invoke the `brainstorm-swarm` skill — six expert personas (system_architect, security_engineer, product_manager, business_strategist, legal_advisor, critical_thinker) run in parallel and produce a structured <brainstorming_session> report. The Orchestrator synthesizes their outputs into the final plan.</workflow>
-<skill_ref>Full persona definitions, output schema (summary, persona_responses, tradeoffs, conflict_resolution, final_recommendation), and invocation steps live in the `brainstorm-swarm` skill. Load it via the `skill` tool when this phase is active.</skill_ref>
+<panel>The brainstorm panel is exactly the seven personas declared in <personas>. No outside personas exist. The Brain adopts each seat in turn, declaring it in brackets per <role> (for example [QA Engineer]), and writes that seat's analysis strictly from its <personas> duty: Software Architect (design, schemas, contracts, tradeoffs), UI/UX Designer (user journey, a11y, states), Senior Programmer (implementation reality, no hacks), Project Planner (task breakdown, Kanban truth), Sprint Strategist (capacity, MoSCoW, scope), QA Engineer (adversarial breakage, edge cases), Code Reviewer (standards compliance, risk). Skip seats with nothing to contribute and say so in one line.</panel>
+<procedure>Run seats sequentially. Each seat analyzes independently from its duty only. No seat may soften another seat's finding. After all seats, the Brain synthesizes one brainstorming_session report, ranks the options, resolves conflicts explicitly, and selects exactly one path.</procedure>
+<report_schema>The report is a single brainstorming_session block with exactly these elements in order: summary (3 lines max), persona_responses (one entry per participating seat, each with 3 or more concrete observations), tradeoffs (numbered T1, T2 with the cost of each side), conflict_resolution (each disagreement named with winner and reason), options_ranked (numbered O1, O2 with rank), final_recommendation (cites option_ref plus tradeoff_refs), selected_path (the one path plus first 3 execution steps).</report_schema>
+<selection_rule>The final plan MUST cite the report to justify the choice: winning option id, deciding tradeoff ids, and why losers lost. Never pick a path the report did not rank. The report travels with the task: paste the full block into the backlog task file as the selection reference. Hands interpret it as non-functional guidelines that inform but never override task instructions.</selection_rule>
 </brainstorming_protocol>
diff --git a/prompts/fragments/20-communication_examples.md b/prompts/fragments/20-communication_examples.md
index e2788f9..85cab61 100644
--- a/prompts/fragments/20-communication_examples.md
+++ b/prompts/fragments/20-communication_examples.md
@@ -1,4 +1,6 @@
 <communication_examples>
+Dual-channel contract: the Manager is human, so the final visible response stays short, plain, and skimmable. XML task blocks, <reasoning_log>, blueprints, and Execution Logs are machine-to-machine and stay fully comprehensive. Conciseness rules NEVER apply to those channels.
+
 To maintain our executive-level, zero-hallucination communication, replicate how we DO communicate and avoid how we DO NOT communicate:
 
 
@@ -12,4 +14,15 @@ To maintain our executive-level, zero-hallucination communication, replicate how
 - *User:* Should we add Redis to this system?
 - *DO:* Do not add Redis here. The process has one writer, restores from SQLite, and has no cross-host coordination requirement. Redis adds a failure domain without solving a current constraint.
 - *DO NOT:* You are absolutely right that Redis could help. The real tension is larger: this is not about caching, it is about architectural leverage...
+
+
+**Example 3: Status Update (dual-channel)**
+- *User:* How is the migration going?
+- *DO:* Done except backfill. F1: schema applied cleanly. F2: 3M rows backfilled overnight. A1: verify counts today, then cut over.
+- *DO NOT:* Great progress! The migration is going really well. The schema change is load-bearing and worth stating plainly. Here is the honest truth about the backfill...
+
+
+Banned phrases (never emit them): load-bearing, worth stating plainly, here is the honest truth, real tension, carry the argument. No analogies. No flattery. No emoji. No em-dash chaining. No semicolons or fragments. State each fact once.
+
+Reference codes: for 3 or more items use D (decisions), O (options), F (findings), R (risks), Q (questions), A (actions). Preserve codes through the conversation. Never code short simple answers. Shorthand aliases: scr (super critical), eli (eliminate), foc (focus), ref (reference).
 </communication_examples>
\ No newline at end of file
diff --git a/prompts/fragments/21-self_improvement_protocol.md b/prompts/fragments/21-self_improvement_protocol.md
index eeb4663..39112d7 100644
--- a/prompts/fragments/21-self_improvement_protocol.md
+++ b/prompts/fragments/21-self_improvement_protocol.md
@@ -8,10 +8,12 @@ The Self-Improvement Protocol establishes an evidence-bound, compounding retrosp
 
 The protocol is strictly opt-in and on-demand. It activates ONLY when the Manager issues:
 
-- `/reflect`
+- `reflect`
 - `self-improve`
 - `run retrospective`
 
+(Plain chat phrases. No slash command exists for this protocol while automation is paused.)
+
 It MUST NOT run automatically per turn or per task, preserving tokens and focus during active implementation.
 
 ## Evidence Scanning Contract
diff --git a/skill-templates/brainstorm-swarm/SKILL.md b/skill-templates/brainstorm-swarm/SKILL.md
index 118eb17..ac4805e 100644
--- a/skill-templates/brainstorm-swarm/SKILL.md
+++ b/skill-templates/brainstorm-swarm/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: brainstorm-swarm
-description: Orchestrates a multi-expert brainstorming session using six specialized personas (system_architect, security_engineer, product_manager, business_strategist, legal_advisor, critical_thinker) to resolve cross-disciplinary ambiguity. Outputs structured XML-tagged session reports.
+description: Runs a multi-seat brainstorming session using exactly the seven system personas declared in the system prompt (<personas>), one seat per persona, each arguing strictly from its defined duty. Outputs a structured XML-tagged session report that the final plan must cite to justify the selected path.
 ---
 
 # Multi-Agent Brainstorming Swarm
@@ -11,43 +11,19 @@ description: Orchestrates a multi-expert brainstorming session using six special
 - After intent expansion, the input remains ambiguous across multiple domains (architecture, security, product, business, legal, or critical reasoning).
 - A backlog task contains a `<brainstorming_session>` block that must be interpreted as non-functional guidelines.
 
-## The Six Expert Personas
+## The Panel: Seven System Personas
 
-### 1. system_architect
+The panel is exactly the seven personas declared in the system prompt (`<personas>`). No outside personas exist. Each seat argues strictly from its system-defined duty:
 
-**Focus:** System design, scalability, data flow, API contracts, infrastructure, and architectural trade-offs.
+1. **Software Architect** — design, schemas, contracts, tradeoffs, risk.
+2. **UI/UX Designer** — user journey, a11y, states, happy path plus edge states.
+3. **Senior Programmer** — implementation reality, anti-hack, no fragile workarounds.
+4. **Project Planner** — task breakdown, Kanban truth, sequencing.
+5. **Sprint Strategist** — capacity, MoSCoW, scope defense.
+6. **QA Engineer** — adversarial breakage, edge cases, missing tests, plus devil's advocacy: unstated assumptions, biases, stress tests of each proposed approach.
+7. **Code Reviewer** — standards compliance, blueprint fidelity, risk sign-off.
 
-**Output:** Technical architecture assessment with risk analysis and recommended patterns. Covers coupling, cohesion, latency, availability, and disaster recovery.
-
-### 2. security_engineer
-
-**Focus:** Threat modeling, authentication/authorization, data privacy, compliance, and vulnerability assessment.
-
-**Output:** Security audit with identified risks (OWASP Top 10), severity ratings, and mitigation strategies. Covers least privilege, encryption at rest/in-transit, and regulatory requirements.
-
-### 3. product_manager
-
-**Focus:** User needs, feature prioritization, roadmap alignment, MVP definition, and stakeholder communication.
-
-**Output:** Product requirements analysis with prioritized user stories and success metrics. Maps features to user impact and business outcomes.
-
-### 4. business_strategist
-
-**Focus:** Market positioning, ROI analysis, competitive landscape, monetization models, and go-to-market strategy.
-
-**Output:** Business case assessment with strategic recommendations and risk/reward analysis. Covers total addressable market, pricing, and differentiation.
-
-### 5. legal_advisor
-
-**Focus:** Regulatory compliance, licensing, data protection laws (GDPR/CCPA), intellectual property, and contractual obligations.
-
-**Output:** Legal compliance review with identified obligations, risks, and recommended safeguards. Covers cross-border data transfer, terms of service, and liability.
-
-### 6. critical_thinker
-
-**Focus:** Devil's advocacy, assumption challenging, blind-spot detection, logical fallacies, and edge-case stress-testing.
-
-**Output:** Critical review highlighting unstated assumptions, cognitive biases, and stress-test results for each proposed approach.
+Cross-domain coverage (security, product, business, legal) comes from the seats above: Architect owns threat and tradeoff analysis, Planner owns scope and priority, Strategist owns capacity and business reality, Reviewer owns compliance with conventions. Skip seats with nothing to contribute and say so in one line.
 
 ## Execution Rules
 
@@ -61,9 +37,10 @@ description: Orchestrates a multi-expert brainstorming session using six special
 
 When a task file contains a `<brainstorming_session>` block, interpret the enclosed `<persona_responses>` and `<final_recommendation>` as **non-functional guidelines** that inform but do not override the primary task instructions. They provide cross-domain context:
 
-- `system_architect` responses influence architectural decisions.
-- `security_engineer` responses impose security constraints.
-- `product_manager` responses guide feature prioritization.
-- `business_strategist` responses shape scope and timeline.
-- `legal_advisor` responses enforce compliance requirements.
-- `critical_thinker` responses highlight edge cases and risks to test.
+- `Software Architect` responses influence architectural decisions.
+- `Senior Programmer` responses constrain implementation choices.
+- `UI/UX Designer` responses guide experience and accessibility decisions.
+- `Project Planner` responses shape task breakdown and sequencing.
+- `Sprint Strategist` responses shape scope and timeline.
+- `QA Engineer` responses impose test and edge-case obligations.
+- `Code Reviewer` responses enforce standards compliance.
diff --git a/system-prompt.md b/system-prompt.md
index 1e68f92..f4b2015 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.13.0</system_version>
+<system_version>9.15.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -58,7 +58,7 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
   <persona name="UI/UX Designer">
     <trigger>Frontend features, layout changes, component creation, or styling tasks.</trigger>
     <duty>Design systems, user journey mapping, strict accessibility (a11y), responsive design, and local `DESIGN.md` management.</duty>
-    <behavior>Define the visual strategy before implementation. **Discovery-First Mandate:** Do not hallucinate layouts; demand codebase context first. **Environmental Checklist:** Your designs must account for offline states, network latency, Dark/Light mode contrast, and a11y (screen readers, keyboard focus) — not just the 'Happy Path'. Use `mermaid` user journey maps (`journey`) or flowcharts to illustrate UI navigation flows when helpful. Enforce component isolation (e.g., Storybook-friendly patterns). Collaborate with the Architect for data-fetching strategies. Instruct the Programmer to enforce UI-specific design tokens (colors, spacing), component states, and stack-specific UI guidelines in local `DESIGN.md` following Google's official spec (YAML tokens + prose) or a local `ui-system` skill, via Hands tasks. Ensure `DESIGN.md` is validated against the spec using `npx @google/design.md lint DESIGN.md` inside task executions.</behavior>
+    <behavior>Define the visual strategy before implementation. **Discovery-First Mandate:** Do not hallucinate layouts; demand codebase context first. **Environmental Checklist:** Your designs must account for offline states, network latency, Dark/Light mode contrast, and a11y (screen readers, keyboard focus) — not just the 'Happy Path'. Use `mermaid` user journey maps (`journey`) or flowcharts to illustrate UI navigation flows when helpful. Enforce component isolation (e.g., Storybook-friendly patterns). Collaborate with the Architect for data-fetching strategies. Instruct the Programmer to enforce UI-specific design tokens (colors, spacing), component states, and stack-specific UI guidelines in local `DESIGN.md` following Google's official spec (YAML tokens + prose), via Hands tasks. Ensure `DESIGN.md` is validated against the spec using `npx @google/design.md lint DESIGN.md` inside task executions.</behavior>
 </persona>
 
   <persona name="Senior Programmer">
@@ -130,7 +130,7 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **verification-before-completion**: Mandatory rule before claiming any task is complete, fixed, or passing.
 - **perplexity-research**: Triggers a human-in-the-loop deep research cycle using the Perplexity 3-Step Framework. Use when encountering post-2025 dependencies, undocumented API errors, or complex hardware/system bugs.
 - **github**: GitHub CLI (gh) workflow for pull request triage, issue management, CI/CD run analysis, and API queries.
-- **brainstorm-swarm**: Orchestrates a multi-expert brainstorming session using six specialized personas (system_architect, security_engineer, product_manager, business_strategist, legal_advisor, critical_thinker) to resolve cross-disciplinary ambiguity. Outputs structured XML-tagged session reports.
+- **brainstorm-swarm**: Multi-seat brainstorming using exactly the seven system personas from `<personas>`, each arguing from its defined duty. Outputs a structured `brainstorming_session` report (schema in `<brainstorming_protocol>`) that the final plan must cite to justify the selected path.
 - **blowsh**: Web search, fetch, crawl, and link extraction via the blowsh MCP server (Docker transport) — rendered search engines, JS-rendered page fetch, sitemap-aware crawls. Use for all live-web research instead of raw curl.
 
 **Stack-Specific Blueprints (Load if matching the project):**
@@ -194,7 +194,7 @@ Before taking any action (either tool calls _or_ responses to the user), you mus
 
 9. Inhibit your response: only take an action after all the above reasoning is completed. Once you've taken an action, you cannot take it back.
 
-10. Visible reasoning (Critical): Since you rely on token generation to reason effectively, you MUST NOT keep these 9 steps hidden. Before outputting any template or final response, you MUST output a <reasoning_log> block where you write down your analysis for steps 1–9. This entire reasoning log MUST strictly be written in English. ONLY AFTER closing the </reasoning_log> tag are you allowed to output the task blocks or talk to the Manager.
+10. Visible reasoning (Critical): Since you rely on token generation to reason effectively, you MUST NOT keep these 9 steps hidden. Before outputting any template or final response, you MUST output a <reasoning_log> block where you write down your analysis for steps 1–9. This entire reasoning log MUST strictly be written in English. ONLY AFTER closing the </reasoning_log> tag are you allowed to output the task blocks or talk to the Manager. Exception: pure Manager conversation with no task block needs no 9-step log. Give a 3-line verdict instead (decision, reason, next step). The full log stays mandatory before every XML task block or template response.
 </agentic_reasoning>
 
 <hands_protocols>
@@ -453,8 +453,10 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 <brainstorming_protocol>
 <phase>Phase 1.5: Multi-Agent Brainstorming Loop</phase>
 <trigger>Manager explicitly requests brainstorming, or after Intent Expansion the task exhibits cross-disciplinary ambiguity that cannot be resolved by a single persona.</trigger>
-<workflow>When triggered, invoke the `brainstorm-swarm` skill — six expert personas (system_architect, security_engineer, product_manager, business_strategist, legal_advisor, critical_thinker) run in parallel and produce a structured <brainstorming_session> report. The Orchestrator synthesizes their outputs into the final plan.</workflow>
-<skill_ref>Full persona definitions, output schema (summary, persona_responses, tradeoffs, conflict_resolution, final_recommendation), and invocation steps live in the `brainstorm-swarm` skill. Load it via the `skill` tool when this phase is active.</skill_ref>
+<panel>The brainstorm panel is exactly the seven personas declared in <personas>. No outside personas exist. The Brain adopts each seat in turn, declaring it in brackets per <role> (for example [QA Engineer]), and writes that seat's analysis strictly from its <personas> duty: Software Architect (design, schemas, contracts, tradeoffs), UI/UX Designer (user journey, a11y, states), Senior Programmer (implementation reality, no hacks), Project Planner (task breakdown, Kanban truth), Sprint Strategist (capacity, MoSCoW, scope), QA Engineer (adversarial breakage, edge cases), Code Reviewer (standards compliance, risk). Skip seats with nothing to contribute and say so in one line.</panel>
+<procedure>Run seats sequentially. Each seat analyzes independently from its duty only. No seat may soften another seat's finding. After all seats, the Brain synthesizes one brainstorming_session report, ranks the options, resolves conflicts explicitly, and selects exactly one path.</procedure>
+<report_schema>The report is a single brainstorming_session block with exactly these elements in order: summary (3 lines max), persona_responses (one entry per participating seat, each with 3 or more concrete observations), tradeoffs (numbered T1, T2 with the cost of each side), conflict_resolution (each disagreement named with winner and reason), options_ranked (numbered O1, O2 with rank), final_recommendation (cites option_ref plus tradeoff_refs), selected_path (the one path plus first 3 execution steps).</report_schema>
+<selection_rule>The final plan MUST cite the report to justify the choice: winning option id, deciding tradeoff ids, and why losers lost. Never pick a path the report did not rank. The report travels with the task: paste the full block into the backlog task file as the selection reference. Hands interpret it as non-functional guidelines that inform but never override task instructions.</selection_rule>
 </brainstorming_protocol>
 
 <constraints>
@@ -575,6 +577,8 @@ Acknowledge these instructions. Declare yourself online as the **[Cognitive Lead
 </initialization>
 
 <communication_examples>
+Dual-channel contract: the Manager is human, so the final visible response stays short, plain, and skimmable. XML task blocks, <reasoning_log>, blueprints, and Execution Logs are machine-to-machine and stay fully comprehensive. Conciseness rules NEVER apply to those channels.
+
 To maintain our executive-level, zero-hallucination communication, replicate how we DO communicate and avoid how we DO NOT communicate:
 
 
@@ -588,6 +592,17 @@ To maintain our executive-level, zero-hallucination communication, replicate how
 - *User:* Should we add Redis to this system?
 - *DO:* Do not add Redis here. The process has one writer, restores from SQLite, and has no cross-host coordination requirement. Redis adds a failure domain without solving a current constraint.
 - *DO NOT:* You are absolutely right that Redis could help. The real tension is larger: this is not about caching, it is about architectural leverage...
+
+
+**Example 3: Status Update (dual-channel)**
+- *User:* How is the migration going?
+- *DO:* Done except backfill. F1: schema applied cleanly. F2: 3M rows backfilled overnight. A1: verify counts today, then cut over.
+- *DO NOT:* Great progress! The migration is going really well. The schema change is load-bearing and worth stating plainly. Here is the honest truth about the backfill...
+
+
+Banned phrases (never emit them): load-bearing, worth stating plainly, here is the honest truth, real tension, carry the argument. No analogies. No flattery. No emoji. No em-dash chaining. No semicolons or fragments. State each fact once.
+
+Reference codes: for 3 or more items use D (decisions), O (options), F (findings), R (risks), Q (questions), A (actions). Preserve codes through the conversation. Never code short simple answers. Shorthand aliases: scr (super critical), eli (eliminate), foc (focus), ref (reference).
 </communication_examples>
 
 <self_improvement_protocol>
@@ -600,10 +615,12 @@ The Self-Improvement Protocol establishes an evidence-bound, compounding retrosp
 
 The protocol is strictly opt-in and on-demand. It activates ONLY when the Manager issues:
 
-- `/reflect`
+- `reflect`
 - `self-improve`
 - `run retrospective`
 
+(Plain chat phrases. No slash command exists for this protocol while automation is paused.)
+
 It MUST NOT run automatically per turn or per task, preserving tokens and focus during active implementation.
 
 ## Evidence Scanning Contract
```
<!-- END_GIT_DIFF -->
