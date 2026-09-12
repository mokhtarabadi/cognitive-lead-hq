# Task 180: Self-improvement — dual-channel communication (concise manager, comprehensive machine)

**File:** `tasks/completed/180-self-improvement-dual-channel-communication.md`
**Source:** manager
**Type:** improvement
**Status:** closed

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
**Factual Git Diff:** Stored in Commit Hash: `5cdc8753971ff737cf6fb98dbfd091fbbde4c041`
<!-- END_GIT_DIFF -->
