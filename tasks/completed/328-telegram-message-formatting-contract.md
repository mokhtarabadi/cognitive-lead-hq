# Task 328: Telegram Message Formatting Contract

**File:** `tasks/completed/328-telegram-message-formatting-contract.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Source Context

### Variant C: Manager (`**Source:** manager`)

## Goal

Make every message sent to Telegram by the Telegram skills and by direct Telegram MCP use render cleanly, following the empirically proven formatting contract handed over by the Manager on 2026-10-21.

## Manager's Notes

- Store the handed-over contract document somewhere sensible in the project.
- Edit the Telegram-related skills so their outgoing messages follow that contract.
- From now on, any message sent into Telegram by the Telegram skills or the Telegram MCP must be pretty, clean, formatted, and compliant with the document.
- The contract's load-bearing facts: `parse_mode: "HTML"` is the only mode that survives (Markdown strips ` ``` ` fences and leaves `*bold*` literal); escape `&` `<` `>` inside `<pre>`/`<code>`; the hard cap is 4096 characters and over-length fails with an opaque `GEN-ERR-184`; U+200C ZWNJ is lost on the read path so Persian must be authored without it; `send_message` has no `topic_id` and lands in General, so topics are reached through `reply_to_message`.

## Local TODOs

- [x] Store the contract as `docs/telegram-message-formatting.md` and index it in `docs/README.md`
- [x] Create the `telegram-message-format` skill with the nine binding authoring rules, templates, and pre-send checklist
- [x] Register the skill in the agent skills registry, bump the system version, regenerate `system-prompt.md`
- [x] Make `telegram-issue-sync` load the skill and send its reply as HTML, topic-anchored, under budget
- [x] Make `telegram-message-export` format its caption and follow-up delivery per the contract
- [x] Add the Telegram rule to the executor skill auto-loading matrix and to `docs/telegram-setup.md`
- [x] Save the contract to project memory and sync the three skills to the global install
- [x] Add contract tests and run the suite

## Acceptance Criteria

- [x] The handed-over contract is stored in the project as a first-class document with the evidence, the defect list, and a binding authoring-rules table
- [x] A `telegram-message-format` skill exists in `skill-templates/` and is registered in the agent skills registry, so the Hands can load it before any Telegram send
- [x] `telegram-issue-sync` sends its confirmation with `parse_mode: "HTML"`, escaped markup, no fences, no ZWNJ, a ~3800-character budget, and a topic-anchored reply
- [x] `telegram-message-export` formats its caption and states the topic rule for delivery
- [x] `agents/cognitive-executor.md` auto-loads the skill for any Telegram MCP send, reply, edit, or caption
- [x] `docs/telegram-setup.md` points to the contract and lists the format skill in the skill-to-tool table
- [x] The contract is saved to project memory and the three skills are byte-identical in the global install
- [x] Contract tests cover the skill, the two Telegram skills, and the document; the suite shows no new failure

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest --with pyyaml python -m pytest tests/ -q`
- **Expected result:** 531 passed, and the only failure is the pre-existing `test_system_prompt_split_assemble_round_trip`
- **Actual result:** 531 passed, 1 failed (`test_system_prompt_split_assemble_round_trip`)
- **Exit code:** 1

> Pre-existing failure, proven unrelated: the round-trip test splits `system-prompt.md` back into fragments and re-assembles it, and the splitter drops the `<night_mode>` block. Running the same split/assemble round trip against the committed `HEAD` version of `system-prompt.md` (`git show HEAD:system-prompt.md`) produces the identical 85 missing lines and 0 added lines, so the defect predates this change. The direct fragment-to-prompt check passes: `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/opencode/system-prompt-check.md` output is byte-identical to the committed `system-prompt.md`.

- **Focused test command:** `rtk test uv run --with pytest python -m pytest tests/test_skill_registry.py tests/test_prompt_sync.py -q`
- **Expected result:** all tests pass, including the three new contract tests
- **Actual result:** 38 passed
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0 (the one failing test is proven pre-existing on `HEAD`; see the evidence note)
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** A skill that every Telegram send must follow adds a load step; if the registry, the shipped prompt, and the global install drift apart, agents keep sending Markdown that the server destroys. The three surfaces (registry fragment, `system-prompt.md`, `~/.config/opencode/skills/`) are covered by the byte-identity round-trip check and the new contract tests.
- **Rollback plan:** Delete `skill-templates/telegram-message-format/`, drop the registry line from `prompts/fragments/07-agent_skills_registry.md`, remove the skill-matrix row from `agents/cognitive-executor.md`, remove the skill references from the two Telegram skills, delete `docs/telegram-message-formatting.md`, then regenerate `system-prompt.md` with `scripts/prompt-build/assemble_system_prompt.py`.

---

## Execution Log & Reasoning

### Mode

- **Autopilot locked for this task** (Manager order, 2026-10-21: "lock auto pilot mode for task 328"). From that word the mode is LOCKED: the Hands chain the QA and review turns directly through the Brain Bridge, no Manager relay for anything except a hard blocker or the closure approval gate. The lock breaks only on "manual", "stop", or a new direct order from the Manager.

### Autopilot QA + Review (2026-10-21, same session)

- **QA verdict: QA_PASSED.** Adversarial pass over the diff: AC/DoD honest (531 passed / 1 failed proven pre-existing via HEAD round-trip with identical 85 missing lines; focused run 38 passed); new skill carries all 9 rules matching doc section 10; both Telegram skills obey (HTML, no emoji, 3800 budget, topic-anchored); version 9.64.0 consistent; tests assert real strings; docs sync complete; no forbidden ops. Two advisories only: no literal U+200C byte scan, no logged global diff hash.
- **Review verdict: APPROVED (PO_REVIEW_PENDING).** Technical approval; 4 non-blocking nits (extra memory index row from rebuild pickup, LLM.txt 31 to 36 count correcting stale 35, numeric example `123-example.md` in skill, QA advisories carried forward). No scope creep, no forbidden ops, no prompt leak beyond version and registry line. File stays in `tasks/qa/`; closure needs the exact phrase "Approved for closure" or "Close task".

### Assumptions

- **A1** — The Manager's request is tracked as a Kanban task (it is a multi-file change touching the shipped prompt, the skill catalog, and the docs). The task file was created directly in `tasks/in-progress/` because the implementation was already under way when the Kanban file was generated; it moves to `tasks/qa/` after staging.
- **A2** — "MCP تلگرام" covers direct ad-hoc sends as well as skill-driven ones. The contract is therefore enforced through the executor skill auto-loading matrix (every send, not only skill runs) and not only inside the two Telegram skills.
- **A3** — The contract document is stored under `docs/` next to `telegram-setup.md` rather than inside the skill, because it is server behavior evidence (probe transcripts, defect list) that the skill points at but does not duplicate.

### What changed

- **`docs/telegram-message-formatting.md` (new)** — the handed-over contract, kept as the reference: executive summary, length findings, parse-mode findings, the ZWNJ analysis, the topic-targeting gap, read-path notes, safe patterns, reproduction probes, the upstream defect list, and a binding authoring-rules table (§10) distilled for agents.
- **`skill-templates/telegram-message-format/SKILL.md` (new)** — the agent-facing rulebook: the nine rules, the rule details (parse mode, Persian text, length splitting, forum topics, read-back verification, probe hygiene), four message templates, a pre-send checklist, and the upstream defect table. Deliberately project-agnostic: no chat ids, no HQ paths, no task numbers.
- **`skill-templates/telegram-issue-sync/SKILL.md`** — Phase 0 now loads `telegram-message-format`; a new "Outgoing Message Formatting (Critical)" section; `telegram_send_message` explicitly banned for topic-scoped output; the Phase 3 reply is now an HTML block (`<b>Task synced</b>` + `<code>` fields, no emoji) anchored to the source message, with the batch position and the length-splitting rule; a new row in the data-integrity table.
- **`skill-templates/telegram-message-export/SKILL.md`** — new Phase 5 for Telegram delivery: the caption follows the contract, and the topic rule is stated (`send_file` accepts `topic_id`; `reply_to_message` for topics; `send_message` lands in General).
- **`prompts/fragments/07-agent_skills_registry.md`** — registry line for the new skill, so the Brain/Hands discover it.
- **`prompts/fragments/01-system_version.md`** + **`system-prompt.md`** — 9.63.0 → 9.64.0, and the shipped prompt regenerated from the fragments (assembler output verified byte-identical).
- **`agents/cognitive-executor.md`** — skill auto-loading matrix gains "Any Telegram MCP send, reply, edit, or file caption → `telegram-message-format`", which is what makes the contract bind direct MCP use, not only skill runs.
- **`docs/telegram-setup.md`** — new skill row in the §6 table, a new §6.1 "Message Formatting Contract" summary, and the related-docs list.
- **`README.md`** — the skill-templates tree gains the new skill directory, the skills table gains its row, and the Telegram MCP section points at the format skill and the contract doc.
- **`docs/README.md`**, **`docs/DECISIONS.md`**, **`skill-templates/README.md`**, **`skill-templates/DECISIONS.md`** — living-folder docs updated: file index, template count 35 → 36, and an ADR per slice recording the decision and its rollback.
- **`.opencode/memory/telegram-sync/message-formatting-contract.md` (new)** + `topic-scoped-sync-workflow.md` — the contract saved as project memory (Manager rule), with the existing sync shard pointing at it; memory index rebuilt (27 shards).
- **`tests/test_skill_registry.py`** — three new tests: the format skill's contract terms, both Telegram skills referencing it, and the contract document existing with its key facts.
- **`tests/test_prompt_sync.py`** — expected shipped version moved to 9.64.0.
- **`LLM.txt`** — skill count 31 → 36 in the global-install section and its checklist (the count was already stale at 35).
- **Global install** — `telegram-message-format` (new), `telegram-issue-sync`, `telegram-message-export` copied to `~/.config/opencode/skills/`; all three verified byte-identical to the repo templates.

### Reasoning

- The contract lives in two places on purpose: the document carries the evidence and the upstream defect list (so a future reader can challenge a rule), while the skill carries the action list (so an agent can comply without reading 300 lines of probes). The skill points at the document; the document does not duplicate the templates.
- The rules were written as "use X, never Y" rather than as prose, because the failure mode being fixed is a silent one: a Markdown-fenced message arrives looking almost right, with the code block destroyed. A checklist format catches that at send time.
- The Persian rule is stated as "write without ZWNJ" because the document proves the loss but cannot tell us whether it happens on the write path, the read path, or both; authoring around it is correct under every hypothesis.
- The topic rule is stated for `reply_to_message` rather than `send_message` because `send_message` has no `topic_id` parameter at all — the only way to reach a topic today is to inherit one from a parent message.
- The executor matrix row was added instead of only patching the two skills, because the Manager asked for the Telegram MCP itself to be covered, and matrix rows are the only place the Hands consult for skills the Orchestrator did not name.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `c47900036dba8c5ad29e0b2af938753bc8975dea`
<!-- END_GIT_DIFF -->
