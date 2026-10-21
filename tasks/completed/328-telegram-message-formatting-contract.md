# Task 328: Telegram Message Formatting Contract

**File:** `tasks/qa/328-telegram-message-formatting-contract.md`
**Source:** manager
**Type:** feature
**Status:** open

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
```diff
diff --git a/.opencode/memory/index.md b/.opencode/memory/index.md
index 194e1eb..10e3402 100644
--- a/.opencode/memory/index.md
+++ b/.opencode/memory/index.md
@@ -20,9 +20,11 @@
 | quirks | extract_signatures_file_write_fix | **Bug Fixed (2026-08-21):** `extract_signatures` MCP tool in `mcp-context-server/server.py` was returning signature s... |  |
 | quirks | full_output_verification_rule | Never trust truncated command output. Head tail cuts hide status lines and cause false alarms. Always re-run with ful... |  |
 | release | release-workflow | Release workflow for cognitive-lead-hq. |  |
+| telegram-sync | message-formatting-contract | # Telegram Message Formatting Contract (Manager rule, 2026-10-21) |  |
 | telegram-sync | topic-scoped-sync-workflow | # Telegram Sync Workflow Constraints (Cognitive Lead HQ) |  |
 | workflows | approval_gates_use_question_tool | # Approval gates must use the question tool (Manager standing rule 2026-09-27) |  |
 | workflows | brain_turn_mode_line | # Brain calls MUST carry a mode line (Manager order 2026-10-16) |  |
+| workflows | free-model-context-window-workflow | # Free-model context-window workflow (verified 2026-10-21) |  |
 | workflows | global-install-upgrade | # Global Install Upgrade Workflow (OpenCode) |  |
 | workflows | manual-qa-review-cycle | # Manual QA + Review Cycle (Hands role-plays both) |  |
 | workflows | no_task_for_global_upgrade | Global install upgrades run WITHOUT a task file: Manager order 2026-09-14 — delete any upgrade task file, execute wor... |  |
diff --git a/.opencode/memory/telegram-sync/message-formatting-contract.md b/.opencode/memory/telegram-sync/message-formatting-contract.md
new file mode 100644
index 0000000..0922890
--- /dev/null
+++ b/.opencode/memory/telegram-sync/message-formatting-contract.md
@@ -0,0 +1,38 @@
+---
+created_at: '2026-10-21T18:38:48.542510+00:00'
+status: active
+tags: []
+updated_at: '2026-10-21T18:38:48.542540+00:00'
+---
+
+# Telegram Message Formatting Contract (Manager rule, 2026-10-21)
+
+Every message sent through the Telegram MCP must be pretty, clean, and formatted per the
+contract in `docs/telegram-message-formatting.md` and the `telegram-message-format` skill.
+The rules were proven empirically against the live server on 2026-10-21.
+
+## Binding rules
+
+1. Always `parse_mode: "HTML"`. Markdown mode consumes triple-backtick fences and inline
+   backticks without creating entities, and leaves `*bold*` as literal asterisks.
+2. Escape `&` -> `&amp;`, `<` -> `&lt;`, `>` -> `&gt;` inside `<pre>` and `<code>`.
+   One raw angle bracket aborts the whole message.
+3. Safe elements only: `<b>`, `<i>`, `<u>`, `<code>`, `<pre>`, `<a>`.
+4. No triple-backtick fences, no `*emphasis*` anywhere in a Telegram message.
+5. Persian text without U+200C ZWNJ — use a normal space where the half-space belongs.
+   ZWNJ is lost on the read path of every message.
+6. Hard cap is 4096 characters; over it the server returns an opaque `GEN-ERR-184`
+   (not a transient error — never retry). Plan on ~3800 chars and split longer payloads
+   into parts, each a reply to the same parent id.
+7. `send_message` has NO `topic_id` and lands in General. Post into a topic with
+   `reply_to_message` anchored to a message already inside that topic. `send_file` and
+   `send_album` do accept `topic_id`.
+8. `get_history` resolves entities to plain text, so a read-back text diff cannot prove
+   formatting was applied; use the `&lt;`/`&gt;` round-trip as the check.
+9. Delete every probe message after reading it back; message ids are never reused.
+
+## Where the rules live
+
+- Skill (load before any send): `skill-templates/telegram-message-format/SKILL.md`
+- Full evidence doc: `docs/telegram-message-formatting.md`
+- Installed globally: `~/.config/opencode/skills/telegram-message-format/SKILL.md`
diff --git a/.opencode/memory/telegram-sync/topic-scoped-sync-workflow.md b/.opencode/memory/telegram-sync/topic-scoped-sync-workflow.md
index 830b0cb..17485e9 100644
--- a/.opencode/memory/telegram-sync/topic-scoped-sync-workflow.md
+++ b/.opencode/memory/telegram-sync/topic-scoped-sync-workflow.md
@@ -19,6 +19,9 @@ Established by Manager on 2026-08-25 after a mis-scoped sync cycle.
 - Bulk Telegram sends trigger `FloodWaitError` (~287s initial). Retrying before the window expires EXTENDS the penalty (observed 466s).
 - Protocol: send one message → verify → wait ≥30–60s between sends; on FloodWaitError, sleep the FULL demanded duration + buffer before any retry.
 
+## Outgoing Message Formatting (MANDATORY)
+- Every reply/notification sent through the Telegram MCP MUST follow `telegram-sync/message-formatting-contract` (skill `telegram-message-format`): `parse_mode: "HTML"`, escaped `&` `<` `>` inside `<pre>`/`<code>`, no triple-backtick fences, no `*emphasis*`, Persian without U+200C ZWNJ, ~3800-char budget with split parts, topic targeting through `reply_to_message` only.
+
 ## State File Semantics
 - `last_processed_message_id` is a global watermark for the chat; after each cycle set it to the highest observed id and backfill `processed_ids` for the whole range so skipped messages are not refetched.
 - `sync_registry[<msg_id>]` = {task_file, gh_issue, type}. Task files may later be archived — check `tasks/archive/` when the backlog path no longer exists.
diff --git a/CHANGELOG.md b/CHANGELOG.md
index dd4dee6..2000239 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Telegram message formatting contract (Task 328):** the Manager's contract document — proven empirically against the live Telegram MCP on 2026-10-21 — is stored as `docs/telegram-message-formatting.md` (executive summary, length findings with the 4096-char cap and the opaque `GEN-ERR-184`, parse-mode findings where HTML is fully preserved but Markdown strips ` ``` ` fences and leaves `*bold*` literal, the U+200C ZWNJ read-path loss, the missing `topic_id` on `send_message`, read-path notes, safe patterns, reproduction probes, the upstream defect list, and a binding authoring-rules table). The new `telegram-message-format` skill carries the nine rules, four message templates, the pre-send checklist, and the upstream defect table, and is registered in the agent skills registry; `telegram-issue-sync` loads it in Phase 0 and sends its confirmation as an HTML block anchored to the source message, with no emoji, no fences, no ZWNJ, and a ~3800-char budget; `telegram-message-export` formats its caption and states the topic rule for delivery; the executor skill auto-loading matrix binds any Telegram MCP send, reply, edit, or caption to the skill, so direct MCP use is covered too; `docs/telegram-setup.md` gains the skill row and a §6.1 contract summary; the contract is saved to project memory (index rebuilt, 27 shards) and the three skills are synced byte-identically to the global install; three contract tests added (skill terms, both Telegram skills referencing it, document presence). Bumped `<system_version>` 9.63.0 → 9.64.0 with byte-identical re-assemble.
 - **Plugin lane contract for Brain and Hands (Task 327):** the goal, todolist, and smart-compact lanes become executable steps instead of trailing prose. Lane G (goal) restores the missing `goal_set` create trigger and states the full lifecycle with the evidence gate and the busy-lease retry; Lane T (todolist) mirrors ANY Brain-produced plan with 2 or more steps, including the combined conditional phase, and states the replace-whole-list semantics, the 100-item and 500-char caps, the durable session storage, and the automatic re-injection; Lane C (smart-compact) adds the task-boundary trigger (previous task finished, new task in the same session) and states the async effect plus the `omitted-NNNN` retrieval rule. (Round 2 superseded the in-prompt lanes: the prompt is now plugin-blind and the executor owns every lane — see the separation entries below.)
 - **Brain-side vocabulary reduced to plan and checklist (same task, Round 2):** both persona mandates speak only of a todo list (micro-list) with verification gates, plus a single sentence stating that how the Hands tracks and executes them is defined solely in the context executor. No tool, plugin, or channel names remain in the prompt.
 - **Tracked idle-loop brake (same task):** `.opencode/STOP_GOAL` is now a tracked marker (the `.gitignore` negation lifts the ignore for that path while the root `STOP_GOAL` stays ignored), so the goal plugin's idle auto-continue is braked by a committed control instead of a prompt promise. The marker stops only the idle loop and never blocks the five agent tools.
diff --git a/LLM.txt b/LLM.txt
index 51a7205..9056b9b 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -171,7 +171,7 @@ Copy all reusable skills from `skill-templates/` into the global OpenCode skills
 cp -r /tmp/cognitive-lead-hq/skill-templates/* ~/.config/opencode/skills/
 ```
 
-After this, the skills will be available via `/help` from any directory. `skill-templates/` contains **31 skills** (`bundle-tasks`, `github`, and 29 more).
+After this, the skills will be available via `/help` from any directory. `skill-templates/` contains **36 skills** (`bundle-tasks`, `github`, `telegram-message-format`, and 33 more).
 
 ### 6.1. (Optional) Bundle CLI Script — Only If You Want `uv run scripts/bundle-tasks.py`
 
@@ -535,7 +535,7 @@ After completing all steps, verify:
 - [ ] `~/.config/opencode/mcp-lint-server/server.py` exists and is executable
 - [ ] `~/.config/opencode/mcp-brain-bridge/server.py` exists and is executable (plus its sibling modules `capability.py`, `preflight.py`, `loop_guard.py`, `session_ledger.py`)
 - [ ] `~/.config/opencode/mcp-common/src/mcp_common/env.py` exists
-- [ ] Skills are installed under `~/.config/opencode/skills/` (at least one subfolder exists) — should include `bundle-tasks` (31 skills total)
+- [ ] Skills are installed under `~/.config/opencode/skills/` (at least one subfolder exists) — should include `bundle-tasks` (36 skills total)
 - [ ] `~/.config/opencode/agents/cognitive-executor.md` exists
 - [ ] `~/.config/opencode/agents/cognitive-discovery.md` exists
 - [ ] `~/.config/opencode/opencode.json` exists with **absolute paths** (not `~` or relative paths) and 6 `mcp` entries (`custom_context`, `project_memory`, `lint`, `brain`, `blowsh`, `telegram`) + `blowsh_*`/`telegram_*`/`brain_turn` permissions, no former browser entry
diff --git a/README.md b/README.md
index ebcef32..77190e6 100644
--- a/README.md
+++ b/README.md
@@ -245,6 +245,8 @@ cp .env.example .env
 │   │   └── SKILL.md
 │   ├── telegram-message-export/        # Export Telegram messages to ZIP
 │   │   └── SKILL.md
+│   ├── telegram-message-format/        # Outgoing Telegram message formatting rules
+│   │   └── SKILL.md
 │   ├── verification-before-completion/ # Mandatory verification gate
 │   │   └── SKILL.md
 │   ├── versioning-and-release/         # SemVer, Changelog, Commit standards
@@ -299,6 +301,7 @@ cp .env.example .env
 | `task-generator`          | Automatically generates decentralized task files based on Manager instructions, with correct `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.                                                                       |
 | `telegram-issue-sync`     | Syncs Telegram supergroup topics into local task files and GitHub issues, using embedded Python scripts for deterministic JSON state management.                                                                                |
 | `telegram-message-export` | Intelligently exports a range of Telegram messages (text, media, voice notes) into a numbered folder, capturing reply hierarchies, and packing them into a ZIP archive.                                                         |
+| `telegram-message-format` | Formats every outgoing Telegram MCP message — HTML parse mode, escaping, length splitting, forum-topic targeting, Persian text without ZWNJ. Contract evidence in `docs/telegram-message-formatting.md`.                                    |
 | `versioning-and-release`  | Standardizes Semantic Versioning (SemVer), Keep a Changelog formats, Conventional Commits, and Safe Push Protocols across all repositories.                                                                                     |
 
 ### Stack-Specific Blueprints
@@ -420,7 +423,7 @@ Full HQ install covering all core MCP servers plus skills plus both agents is do
 **Optional — auto-installed via `LLM.txt` Step 7.6:**
 
 - `blowsh` (Docker `ghcr.io/mokhtarabadi/blowsh-mcp:latest`, 5 tools) — **JS-capable browsing (retired browser MCP replacement).** `fetch_web` (plain/html/markdown/pdf + selector/max_chars/wait_ms + focus/toc/must_contain/archive/stitch probes), `search_web` (DuckDuckGo+Bing+Brave+Mojeek consensus, intent verticals), `extract_links`, `fetch_web_batch` (10 URLs), `crawl_web` (sitemap-aware multi-page docs/API refs/wikis with focus/depth/char budgets). SSRF guard, TTL cache. Timeout 120s. See https://github.com/mokhtarabadi/blowsh-mcp, `skill-templates/blowsh/SKILL.md`, and `docs/telegram-setup.md` (setup maps to same global install).
-- `telegram` (Telethon, 80+ tools, `$HOME/.config/opencode/mcp-telegram-server/.venv/bin/python` + absolute `main.py` path in opencode config dir) — Accounts (`list_accounts`, multi-account `account` param), chats/groups, messages (`send_message`/`reply_to_message` with `account="personal"`/`"work"`), contacts/aliases, media (`send_file`/`download_media`), events (`wait_for_settled_message`, `enable_incoming_feed`). File roots required for media tools (`/tmp/telegram-mcp` + `$HOME/.config/opencode/mcp-telegram-server/downloads`). Used by `skill-templates/telegram-issue-sync/SKILL.md` (supergroup → tasks) and `telegram-message-export/SKILL.md` (range → ZIP) — see `docs/telegram-setup.md` §6 for the full skill→tool→config table. Single vs work/personal setup documented there plus `LLM.txt` 7.6 (absolute paths, installed in `~/.config/opencode/`).
+- `telegram` (Telethon, 80+ tools, `$HOME/.config/opencode/mcp-telegram-server/.venv/bin/python` + absolute `main.py` path in opencode config dir) — Accounts (`list_accounts`, multi-account `account` param), chats/groups, messages (`send_message`/`reply_to_message` with `account="personal"`/`"work"`), contacts/aliases, media (`send_file`/`download_media`), events (`wait_for_settled_message`, `enable_incoming_feed`). File roots required for media tools (`/tmp/telegram-mcp` + `$HOME/.config/opencode/mcp-telegram-server/downloads`). Used by `skill-templates/telegram-issue-sync/SKILL.md` (supergroup → tasks), `telegram-message-export/SKILL.md` (range → ZIP), and `telegram-message-format/SKILL.md` (HTML parse mode, escaping, length, topic targeting — contract in `docs/telegram-message-formatting.md`) — see `docs/telegram-setup.md` §6 for the full skill→tool→config table. Single vs work/personal setup documented there plus `LLM.txt` 7.6 (absolute paths, installed in `~/.config/opencode/`).
 
 ### Meta-Task Bundling — Pure MCP (No CLI Required)
 
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 344602d..e7761d7 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -73,6 +73,7 @@ If the Orchestrator or Manager forgets to explicitly list a skill in the `<conte
 | Implementation-producing input (any stack, any language) | `prompt-refactor` (mandatory before planning: validate, translate, expand, then structure) |
 | Java-8 Android Views, no Compose (XML layouts, Activities) | `android-kotlin` for Kotlin discipline plus tooling order only; Compose MVI Hilt SQLDelight coverage does not apply to Views (skip recorded) |
 | Plain Node CommonJS Cloud Code, no TS or hex ports      | `node-hexagonal-api` for layering intent where applicable, else no stack skill; no CommonJS Cloud Code skill exists (skip recorded) |
+| Any Telegram MCP send, reply, edit, or file caption     | `telegram-message-format` (parse mode, escaping, length splitting, topic targeting, Persian text) |
 
 **Binding Fallback Rule:** If no stack skill exactly matches, load the closest skill for discipline only and record an explicit skip with root plus marker scan list plus matched skills list plus reason phrase. Never invent a new skill inline and never claim coverage not present.
 
diff --git a/docs/DECISIONS.md b/docs/DECISIONS.md
index db76fd7..dfe1b84 100644
--- a/docs/DECISIONS.md
+++ b/docs/DECISIONS.md
@@ -6,3 +6,10 @@
 - **Decision:** Adopting Living Folder Docs standard for this component.
 - **Consequences:** All future structural or contract changes must be recorded here.
 - **Rollback:** N/A (baseline adoption).
+
+## [2026-10-21] ADR-002: Telegram Message Formatting Contract Lives in `docs/`
+
+- **Context:** The Telegram MCP's real formatting behavior (HTML preserved, Markdown fences consumed, 4096-char limit, lost ZWNJ, no `topic_id` on `send_message`) was proven empirically on 2026-10-21 and handed over as a document. It had no home in the repo, so every agent that sends a Telegram message re-derives it or ignores it.
+- **Decision:** The contract is stored verbatim as `docs/telegram-message-formatting.md` (server-side facts plus a binding authoring-rules table). The agent-facing rulebook is a skill, `skill-templates/telegram-message-format/SKILL.md`, so the Hands can load it on demand; the doc stays the reference the skill points at.
+- **Consequences:** Every Telegram send from a skill or a direct MCP call must load the skill and obey the 9 authoring rules. The two Telegram skills and the Hands skill matrix now name it explicitly.
+- **Rollback:** Delete the skill and the doc, and remove the registry line, the skill-matrix row, and the skill references from the two Telegram skills.
diff --git a/docs/README.md b/docs/README.md
index 282dbd3..488f856 100644
--- a/docs/README.md
+++ b/docs/README.md
@@ -15,6 +15,7 @@ Human-readable spec hub for conventions, architecture-adjacent guides, service t
 - `services.md` — Service topology for MCP daemons.
 - `setup.md` — Environment setup guide.
 - `telegram-setup.md` — Telegram sync setup.
+- `telegram-message-formatting.md` — Message formatting contract for the Telegram MCP (parse mode, length limit, ZWNJ, topic targeting).
 - `living-folder-docs-roadmap.md` — Rollout roadmap for Living Folder Docs.
 - `workflow-upgrade-v8.4.5.md` — Workflow upgrade notes.
 - `history/` — Per-milestone summaries (milestone-1 through milestone-22).
diff --git a/docs/telegram-message-formatting.md b/docs/telegram-message-formatting.md
new file mode 100644
index 0000000..5d196bb
--- /dev/null
+++ b/docs/telegram-message-formatting.md
@@ -0,0 +1,298 @@
+# Telegram MCP — Message Formatting Contract
+
+> **Audience:** the Telegram MCP server maintainers, and every agent that sends a message through the Telegram MCP.
+> **Purpose:** every rule below was proven empirically against the live server on 2026-10-21 by sending probe messages and reading them back. Nothing here is inferred from documentation.
+> **Status:** the two safe patterns at the end work today on the current server; the "known defects" section is what we believe should be fixed upstream.
+> **Operational twin:** [`skill-templates/telegram-message-format/SKILL.md`](../skill-templates/telegram-message-format/SKILL.md) — the agent-facing rulebook distilled from this document. Load it before any Telegram send.
+
+---
+
+## 0. Executive summary
+
+| Concern                    | Verdict                                                       | Action for the server team                                  |
+| -------------------------- | ------------------------------------------------------------- | ----------------------------------------------------------- |
+| Message length             | Hard limit is **4096 chars**; 4097 fails with an opaque `GEN-ERR-184` | Return a descriptive error instead of a generic one   |
+| Markdown ` ``` ` fences    | **Consumed** — the code block markers vanish                   | Fix the Markdown entity parser, or document HTML-only     |
+| Markdown `*bold*`          | **Not applied** — asterisks survive as literal text            | Same                                                        |
+| Markdown inline `` `code` `` | **Consumed** — backticks vanish                              | Same                                                        |
+| HTML `<b> <code> <pre>`    | **Fully preserved**                                            | Keep as-is; recommend it as the default                     |
+| HTML entities (`&lt;` `&gt;` `&amp;`) | **Decoded correctly**                              | Keep as-is                                                  |
+| Persian ZWNJ (U+200C)       | **Lost on read** — affects every message, including ones the account owner typed on their own phone | Fix the read-path JSON encoding; until then, avoid ZWNJ in authored text |
+| Forum topics                | `send_message` has **no `topic_id`**                           | Add `topic_id` to `send_message`                            |
+| Deletion                    | `delete_message` works and is clean                            | Keep                                                        |
+
+---
+
+## 1. Message length
+
+Proven by sending messages of exact known length to the Apex topic and reading back the result.
+
+| Payload length | Result                                           |
+| -------------- | ------------------------------------------------ |
+| 4096 chars     | **sent successfully**                             |
+| 4097 chars     | fails: `An error occurred (code: GEN-ERR-184)`    |
+| 4200 chars     | fails: `An error occurred (code: GEN-ERR-184)`    |
+| 4665 chars (a real report) | fails: `An error occurred (code: GEN-ERR-184)` |
+| 3000 chars     | sent successfully                                 |
+
+**Rules**
+
+1. The limit is exactly **4096 characters**, matching Telegram's own `MESSAGE_MAX_LENGTH`. It is not a server-imposed cap.
+2. `GEN-ERR-184` is returned for **any** over-length message, and it carries no indication that length was the cause. A caller that treats it as a transient/network error will retry forever. **The error should be specific**, e.g. `MESSAGE_TOO_LONG: 4665 > 4096`.
+3. The counter should count **UTF-16 code units**, not bytes and not grapheme clusters — that is what Telegram counts. A message with many emoji or Persian/Arabic characters hits the limit well before its byte length suggests. (Empirically unverified here; stated because it is the Telegram-documented behavior and the difference is real for non-ASCII payloads.)
+4. **Character budget for a report-style message:** plan on ~3800 characters per message and split anything longer into parts, each anchored as a reply to the same parent message id so the thread stays readable.
+
+---
+
+## 2. Parse mode: what actually happens
+
+All three findings were produced by sending a probe, reading the message back, and diffing what was sent against what came out. The probes were deleted afterwards.
+
+### 2.1 `parse_mode: "Markdown"` — fences and backticks are consumed
+
+Probe sent:
+
+```
+PROBE-A ```bash
+curl -X POST https://x/y
+``` می‌کند
+```
+
+Read back:
+
+```
+PROBE-A bash
+curl -X POST https://x/y
+ می‌کند
+```
+
+The ` ``` ` markers are **gone**. What remains is the literal `bash` language hint followed by the code body, indistinguishable from ordinary paragraph text. A second probe confirms the same for the inline form — `INLINECODE` came back without its backticks.
+
+A separate probe shows `*bold*` is **not** interpreted at all: `*BOLDTEST*` round-trips with its asterisks intact, so the reader sees literal asterisks rather than bold text.
+
+**Conclusion:** in Markdown mode this server strips fence/backtick markers but does not build the corresponding Telegram entities. The code block is therefore destroyed — the content survives, its formatting does not. Do not use Markdown mode for anything containing code.
+
+### 2.2 `parse_mode: "HTML"` — fully preserved
+
+Probe sent:
+
+```html
+<b>BOLD</b> inline <code>IDENT</code>
+
+<pre>curl -u '&lt;admin&gt;:&lt;pass&gt;' \
+  --data 'x=1'</pre>
+
+<pre>SELECT 1;</pre>
+
+tail &amp; more
+```
+
+Read back (tags and entities resolved, structure intact):
+
+```
+BOLD inline IDENT
+
+curl -u '<admin>:<pass>' \
+  --data 'x=1'
+
+SELECT 1;
+
+tail & more
+```
+
+Every element behaved correctly:
+
+- `<b>` → bold
+- `<code>` → inline monospace
+- `<pre>` → block code, with the block boundaries preserved
+- `&lt;` `&gt;` `&amp;` → decoded to `<` `>` `&`
+
+The `&lt;`/`&gt;` round-trip is the important one: it proves the HTML was genuinely parsed into Telegram entities rather than being passed through and merely displayed without tags. **This is the mode to use.**
+
+### 2.3 Recommended defaults
+
+- **Use `parse_mode: "HTML"` for any message containing code, identifiers, or emphasis.**
+- Inside `<pre>`, escape `&` as `&amp;`, `<` as `&lt;`, `>` as `&gt;`.
+- If a caller has no parse mode available, the safe fallback is to send plain text and accept that structure must be expressed with plain-text conventions (indentation, separators) rather than markup.
+
+---
+
+## 3. Persian text: the ZWNJ problem
+
+**U+200C ZERO WIDTH NON-JOINER is lost.** This is not a quirk of how the text was authored — it applies to every message read back through this server, including messages the Telegram account owner typed by hand on a phone (Persian keyboards insert ZWNJ automatically).
+
+Probe with ASCII sentinels around the ZWNJ, so nothing depends on the surrounding Persian:
+
+```
+sent:      SENTINEL_A‌SENTINEL_B
+read back: SENTINEL_ASENTINEL_B
+```
+
+The ZWNJ is absent from the returned payload. The same holds for `send_message`, so it is not specific to one tool.
+
+**Why this matters for Persian:** ZWNJ is what keeps a suffix attached to its prefix word. Without it, `می‌کند` degrades to `میکند`, and compounds like `قابل‌تسویه` or `نمی‌فهمم` lose the half-space that distinguishes one word from two. The text stays readable to a Persian reader, but it is no longer typographically correct Persian.
+
+**Two distinct possibilities, and the server team should determine which applies:**
+
+1. **Read-path loss (most likely).** The characters are stored correctly in Telegram and only vanish when the server serializes messages back to the client. If so, the delivered message on a phone is fine and only programmatic readers are affected — but any agent that reads a message and then re-sends it (quoting, replying, editing) will silently corrupt the Persian.
+2. **Write-path loss.** The characters are stripped before the message is sent, so the delivered message itself is wrong.
+
+Either way there is a **safe authoring rule that works under both hypotheses:** write Persian without ZWNJ, using a regular space where the half-space belongs, and never rely on a ZWNJ surviving a round-trip.
+
+**Action for the server team:** check the JSON encoding on the message-read path. A common cause is the response being serialized with `ensure_ascii=True` plus a normalization step that drops characters in the Unicode "format" category (U+200C is `Cf`, i.e. *Format*, and many normalizers strip `Cf` characters along with the zero-width space U+200B and the BOM). The fix is to preserve `Cf` characters, or at minimum to preserve U+200C explicitly.
+
+---
+
+## 4. Forum topics: `send_message` cannot target a topic
+
+`send_message` accepts `chat_id`, `message`, `parse_mode`, `format_date`, `custom_emojis` and `account` — there is **no `topic_id` parameter**. `send_album` and `send_file` do have `topic_id`.
+
+Consequence: a message sent with `send_message` to a supergroup that has forum topics enabled lands in **General**, not in the intended topic.
+
+The workaround that works today: use `reply_to_message` with the id of an existing message **inside** the target topic. A reply inherits the topic of its parent. Every message in the Apex topic during this investigation was posted this way.
+
+**Action for the server team:** add `topic_id` to `send_message`, matching the signature `send_album` and `send_file` already use.
+
+---
+
+## 5. Deleting probe messages
+
+`delete_message(chat_id, message_id, account)` removes a message cleanly and immediately, and the message id is not reused. This is what makes empirical probing safe: every probe in this investigation was deleted after being read back, leaving the group with only the intended messages.
+
+`delete_messages_bulk` and `delete_chat_history` also exist. Note that deleting a message does **not** renumber the remaining ones, and later messages keep their original ids — so a client that has cached message ids must treat deletion as "this id may no longer resolve" rather than as a renumbering.
+
+---
+
+## 6. Reading messages back
+
+Two read tools exist and they behave differently:
+
+- `get_history(chat_id, limit, account, topic_id)` — returns a JSON string of `{results: [{id, sender, date, text, reply_to, ...}]}`. The `text` field is the **plain text with entities already resolved** — formatting is not visible in the response, only in the Telegram client. `topic_id` filters to one topic.
+- `get_messages(chat_id, page, page_size, account)` — returns a pre-rendered human-readable listing, one line per message, with the message text inline. `page`/`page_size` pagination, **no topic filter**. Useful for a quick "what are the latest messages" check.
+- `get_message_context(chat_id, message_id, context_size, account)` — returns the message plus surrounding context.
+
+**Practical note:** because `get_history` resolves entities into plain text, **a round-trip comparison cannot confirm that formatting was applied**. Proving that `<pre>` really became a Telegram code-block entity requires reading the message's `entities` array, which none of the current read tools expose. The most reliable available check is the `&lt;`/`&gt;` round-trip described in §2.2, which proves the HTML was parsed rather than passed through — and it is the check used throughout this document.
+
+**Suggested addition:** expose the raw `entities` array on the message payload, so a client can verify that a code block or bold span was actually applied rather than trusting that it was.
+
+---
+
+## 7. Safe patterns to adopt today
+
+### 7.1 A report with a code block (recommended)
+
+```html
+<b>Heading</b> and <code>inline_identifier</code>
+
+<pre>curl -X POST "https://example.com/api" \
+  --data 'key=value'</pre>
+
+<b>Second heading</b>
+
+<pre>SELECT id, state FROM trades WHERE id = 2069;</pre>
+
+Notes with <code>snake_case_names</code> inline.
+```
+
+- `parse_mode: "HTML"`
+- escape `&` `<` `>` inside `<pre>`
+- keep each message under ~3800 characters
+- anchor every part as a reply to the same parent message id
+
+### 7.2 A short prose message
+
+```
+<b>Short heading</b>
+
+Plain prose with <code>identifiers</code> and no markup dependency.
+```
+
+- `parse_mode: "HTML"`
+- **write Persian without ZWNJ** — use a normal space where the half-space belongs
+- keep it under ~3800 characters
+
+### 7.3 Posting into a specific forum topic
+
+```
+reply_to_message(chat_id, message_id=<an id already inside the topic>, account, parse_mode="HTML", text=...)
+```
+
+---
+
+## 8. Reproducing every finding
+
+Each item below is a standalone, self-verifying probe. Run them against a scratch chat, read the result back, then delete the probe.
+
+**A. Length boundary**
+
+```js
+// 4096 -> "Replied to message N."   4097 -> "GEN-ERR-184"
+await reply_to_message({chat_id, message_id, account, text: "L" + "x".repeat(4095)});
+await reply_to_message({chat_id, message_id, account, text: "L" + "x".repeat(4096)});
+```
+
+**B. Markdown fences are consumed**
+
+```js
+await reply_to_message({chat_id, message_id, account, parse_mode: "Markdown",
+  text: "PROBE ```bash\ncurl -X POST https://x/y\n``` end"});
+// read back -> the ``` markers are gone
+```
+
+**C. HTML is preserved**
+
+```js
+await reply_to_message({chat_id, message_id, account, parse_mode: "HTML",
+  text: "<b>B</b> <code>C</code> <pre>x &lt; y</pre>"});
+// read back -> "B C x < y" with the block intact
+```
+
+**D. ZWNJ is lost (read-path)**
+
+```js
+await reply_to_message({chat_id, message_id, account, text: "SENTINEL_A\u200cSENTINEL_B"});
+// read back -> "SENTINEL_ASENTINEL_B"
+```
+
+**E. `send_message` ignores the topic**
+
+```js
+await send_message({chat_id, message: "TOPIC_PROBE", account});
+// lands in General, not in the topic
+```
+
+**F. Cleanup**
+
+```js
+await delete_message({chat_id, message_id, account});
+```
+
+---
+
+## 9. Defect list (for the server backlog)
+
+1. **Over-length messages return `GEN-ERR-184`** with no length hint — indistinguishable from a transient error. Return a specific, actionable error.
+2. **Markdown mode destroys code blocks** — fence markers are stripped without entities being created. Either implement the entity mapping properly or reject Markdown mode with a clear message pointing at HTML.
+3. **Markdown `*bold*` is not applied** — asterisks survive as literal characters. Same fix as above.
+4. **Persian ZWNJ is lost** on the read path (and possibly the write path). Preserve U+200C; do not strip Unicode `Cf` characters.
+5. **`send_message` cannot target a forum topic** — add `topic_id`, matching `send_album` / `send_file`.
+6. **Message `entities` are not exposed** on read — a client cannot verify that formatting was applied. Add the raw entities array to the message payload.
+7. **Message length should be counted in UTF-16 code units** so the check matches Telegram's own limit, and the error should report the actual count versus the cap.
+
+---
+
+## 10. Authoring rules for agents (binding)
+
+These are the rules an agent must follow when it authors a Telegram message. They restate the findings above in the form of an action list, and they are the source of the [`telegram-message-format` skill](../skill-templates/telegram-message-format/SKILL.md).
+
+| # | Rule                                                                        | Why                                                                        |
+| - | --------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
+| 1 | Always send with `parse_mode: "HTML"`.                                     | Markdown mode strips fences and backticks without creating entities (§2.1). |
+| 2 | Escape `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;` inside `<pre>` and `<code>`. | Raw `<` breaks the HTML parse and aborts the whole message (§2.2).        |
+| 3 | Use `<b>` for headings, `<code>` for inline identifiers, `<pre>` for code.  | Those three are the only elements proven to survive the round-trip (§2.2). |
+| 4 | Never use ` ``` ` fences or `*bold*` Markdown syntax.                       | Both are consumed or left literal (§2.1).                                 |
+| 5 | Write Persian without U+200C ZWNJ — use a normal space instead.            | ZWNJ is lost on the read path for every message (§3).                      |
+| 6 | Keep each message under ~3800 characters; split longer payloads into parts, each a reply to the same parent id. | The hard limit is 4096 and the failure is an opaque `GEN-ERR-184` (§1). |
+| 7 | Post into a forum topic with `reply_to_message` anchored to a message inside that topic. | `send_message` has no `topic_id` and lands in General (§4).         |
+| 8 | Verify a formatted send by reading it back and checking the `&lt;`/`&gt;` round-trip. | `get_history` resolves entities to plain text, so a text diff cannot prove formatting (§6). |
+| 9 | Delete every probe message after reading it back.                           | Keeps the group clean; message ids are not reused (§5).                    |
diff --git a/docs/telegram-setup.md b/docs/telegram-setup.md
index 4b7630a..8220fd1 100644
--- a/docs/telegram-setup.md
+++ b/docs/telegram-setup.md
@@ -201,6 +201,19 @@ codex mcp add telegram --url http://127.0.0.1:8765/mcp
 | **`telegram-issue-sync`** (`skill-templates/telegram-issue-sync/SKILL.md`) | `telegram_get_history` (filter `reply_to == config.topic_id` then `id > last_processed_message_id`), `telegram_get_message_context` (parent chain walk to topic root), `telegram_reply_to_message` (topic-targeted reply), optionally GitHub issue create | `telegram-sync.json` at repo root: `config.chat_id`, `config.topic_id` (**topic-scoped — ONLY this topic syncs**), `config.account`, `target_hashtags` (`bug`, `feature`, `improve`), `last_processed_message_id`, `processed_ids`, `sync_registry` | Phase 1 fetch + client-filter by `reply_to` → Phase 2 manager approval → Phase 3 per-candidate: verbatim `RAW_TEXT` → translate → `prompt-refactor` → codebase `grep/glob` → task file + optional GH issue → topic-targeted reply |
 | **`telegram-message-export`** (`skill-templates/telegram-message-export/SKILL.md`) | `telegram_get_history` (range `[from_id,to_id]`), `telegram_get_media_info`, `telegram_download_media` | No `telegram-sync.json`; takes `[from_id,to_id]` or snippet/link `t.me/c/CHAT/MSG` | Phase 1 fetch & sort → Phase 2 write `{n}.txt` sidecars + `reply_to_message_id` + media download → Phase 3 `zip -r telegram-exports/export-{ts}.zip` → Phase 4 notification |
 | **Direct ad-hoc use** | `send_file` (file attachments to General topic `chat_id=-1003993323129`), `send_message`/`reply_to_message` | `account="personal"` per memory `workflows/telegram-file-delivery` | `telegram_send_file(chat_id, file_path, caption, account="personal")` → verifies via `telegram_get_messages` |
+| **`telegram-message-format`** (`skill-templates/telegram-message-format/SKILL.md`) | No send of its own — it governs every send made by the rows above | n/a | Load before any send: `parse_mode: "HTML"`, escape `&` `<` `>` inside `<pre>`/`<code>`, no ` ``` ` fences, no U+200C ZWNJ, ~3800-char budget with split parts, topic targeting through `reply_to_message` |
+
+### 6.1 Message Formatting Contract
+
+Every message sent through this MCP must follow [`telegram-message-formatting.md`](telegram-message-formatting.md) — the empirical contract proven against the live server on 2026-10-21:
+
+- `parse_mode: "HTML"` only. `Markdown` strips ` ``` ` fences and inline backticks without creating entities, and leaves `*bold*` literal.
+- Escape `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;` inside `<pre>` and `<code>`; one raw `<` aborts the whole message.
+- Safe elements: `<b>`, `<i>`, `<u>`, `<code>`, `<pre>`, `<a>`.
+- Persian text without U+200C ZWNJ — use a normal space where the half-space belongs.
+- Hard cap 4096 characters; over it the server returns an opaque `GEN-ERR-184`. Plan on ~3800 and split longer payloads into parts, each a reply to the same parent id.
+- `send_message` has no `topic_id` and lands in General; post into a topic with `reply_to_message` anchored to a message inside it. `send_file` and `send_album` do accept `topic_id`.
+- `get_history` resolves entities to plain text, so a read-back text diff cannot prove formatting; use the `&lt;`/`&gt;` round-trip instead.
 
 **Memory quirks that apply:**
 - `workflows/telegram-file-delivery` — send whole file as attachment to General topic (id 1), never chunk into text; `send_file` has no `reply_to` so General is default; chat `-1003993323129`.
@@ -228,4 +241,6 @@ The server prompts the LLM when `account` ambiguous ("unknown / resembles one /
 
 - `skill-templates/telegram-issue-sync/SKILL.md` — full sync SOP (zero-summarization, bilingual task files)
 - `skill-templates/telegram-message-export/SKILL.md` — export SOP (reply hierarchy + zip)
+- `skill-templates/telegram-message-format/SKILL.md` — outgoing message formatting rules (parse mode, escaping, length, topics)
+- `telegram-message-formatting.md` — the full formatting contract with probe evidence and the upstream defect list
 - `LLM.txt` Steps 7, 7.6, 10 — global auto-install including telegram
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index b0b5d76..c0e04e4 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.63.0</system_version>
+<system_version>9.64.0</system_version>
diff --git a/prompts/fragments/07-agent_skills_registry.md b/prompts/fragments/07-agent_skills_registry.md
index 0ef04a6..9841a56 100644
--- a/prompts/fragments/07-agent_skills_registry.md
+++ b/prompts/fragments/07-agent_skills_registry.md
@@ -16,6 +16,7 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **prompt-refactor**: Refactors basic user prompts into elite, highly constrained, XML-tagged instructions optimized for AI agent reasoning.
 - **telegram-issue-sync**: Syncs Telegram supergroup topics into local task files and GitHub issues, using embedded Python scripts for deterministic JSON state management.
 - **telegram-message-export**: Intelligently exports a range of Telegram messages (text, media, voice notes) into a numbered folder, capturing reply hierarchies, and packing them into a ZIP archive.
+- **telegram-message-format**: Formats every outgoing Telegram MCP message so it renders cleanly in Telegram. Load before any send, reply, edit, or caption through the Telegram MCP — covers parse mode, HTML escaping, length splitting, forum-topic targeting, Persian text, and read-back verification.
 - **design-md**: Extract a comprehensive design system (DESIGN.md) directly from frontend source code — React, Vue, Svelte, Angular, plain HTML/CSS, or any web framework. Analyzes component files, stylesheets, Tailwind configs, theme definitions, and design tokens to produce a rich, Stitch-compatible design system document.
 - **doc-coauthoring**: Guide users through a structured workflow for co-authoring documentation. Use when user wants to write documentation, proposals, technical specs, decision docs, or similar structured content.
 - **project-memory**: Smart note-taking and persistent project memory. Automatically saves Manager constraints and proactively retrieves context to prevent hallucinations.
diff --git a/skill-templates/DECISIONS.md b/skill-templates/DECISIONS.md
index b572ed2..70d5ca3 100644
--- a/skill-templates/DECISIONS.md
+++ b/skill-templates/DECISIONS.md
@@ -6,3 +6,10 @@
 - **Decision:** Adopting Living Folder Docs standard for this component.
 - **Consequences:** All future structural or contract changes must be recorded here.
 - **Rollback:** N/A (baseline adoption).
+
+## [2026-10-21] ADR-002: Telegram Message Formatting Is a Skill, Not an Inline Rule
+
+- **Context:** The Telegram MCP server does not behave like the Bot API — `parse_mode: "Markdown"` strips code fences without creating entities, `*bold*` stays literal, payloads over 4096 characters fail with an opaque `GEN-ERR-184`, U+200C ZWNJ is dropped on the read path, and `send_message` has no `topic_id` so it lands in General. Without a shared rule, each Telegram skill re-derives (or ignores) the behavior and messages render broken.
+- **Decision:** Add a dedicated `telegram-message-format` skill holding the nine binding authoring rules, the message templates, and the pre-send checklist. The two Telegram skills load it in their mandatory-skill phase; the HQ evidence document `docs/telegram-message-formatting.md` stays the reference the skill points at.
+- **Consequences:** One place owns Telegram render correctness; the skill is discoverable through the agent skills registry and loadable on demand by any agent that sends a Telegram message. The template stays project-agnostic — no HQ paths, task numbers, or chat ids inside it.
+- **Rollback:** Delete `skill-templates/telegram-message-format/`, remove the registry line, the skill-matrix row, and the skill references from the two Telegram skills.
diff --git a/skill-templates/README.md b/skill-templates/README.md
index 85a0e21..8cea60e 100644
--- a/skill-templates/README.md
+++ b/skill-templates/README.md
@@ -6,7 +6,7 @@ Project-agnostic skill template catalog: source of truth copied into `.opencode/
 
 ## Files
 
-- `*/SKILL.md` — One directory per skill (35 templates: `android-kotlin`, `audit-agents`, `bundle-tasks`, `task-generator`, `prompt-refactor`, `verification-before-completion`, `init-folder-docs`, and others).
+- `*/SKILL.md` — One directory per skill (36 templates: `android-kotlin`, `audit-agents`, `bundle-tasks`, `task-generator`, `prompt-refactor`, `verification-before-completion`, `init-folder-docs`, `telegram-message-format`, and others).
 - `opencode-init/references/` and `opencode-init/scripts/` — Init scaffolding references and helpers.
 
 ## Key Risks & Invariants
diff --git a/skill-templates/telegram-issue-sync/SKILL.md b/skill-templates/telegram-issue-sync/SKILL.md
index 35159e5..5f90763 100644
--- a/skill-templates/telegram-issue-sync/SKILL.md
+++ b/skill-templates/telegram-issue-sync/SKILL.md
@@ -53,6 +53,7 @@ Before any Telegram fetching, you MUST load these skills:
 ```markdown
 1. Load `task-generator` skill — ensures task files use the correct template with `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.
 2. Load `prompt-refactor` skill — will be used in Phase 3 to generate the `## Refactored Prompt` section.
+3. Load `telegram-message-format` skill — governs every message this skill sends back to Telegram (parse mode, escaping, length splitting, Persian text, topic targeting). MANDATORY before the Phase 3 reply step.
 ```
 
 Use the `skill` tool for each. If loading fails, HALT and report the error.
@@ -72,8 +73,20 @@ This MCP implementation does **NOT** expose a `topic_id` parameter. Forum topics
 
 - **Reading messages from a specific topic:** Call `telegram_get_history(chat_id=config.chat_id, limit=100, account=config.account)`. It returns messages from all topics. **Filter results by `reply_to`** — direct replies have `reply_to == config.topic_id` (e.g., `458` = Cognitive Lead, `455` = other project, `1` = General). For nested replies, walk the chain via `telegram_get_message_context` recursively until you hit the topic root `MessageActionTopicCreate`; discard messages whose chain terminates at `455`/`1`/`null`.
 - **Sending a message to a specific topic:** You MUST use `telegram_reply_to_message` with `message_id` set to `config.topic_id`. Never post topic confirmations to General.
+- **`telegram_send_message` MUST NOT be used for topic-scoped output:** it has no `topic_id` parameter, so it always lands in General.
 - **MANDATORY per `.opencode/memory/telegram-sync/topic-scoped-sync-workflow.md`:** `config.topic_id` defines the ONLY channel to sync. NEVER fetch/scan group-wide history.
 
+### Outgoing Message Formatting (Critical)
+
+Every message this skill sends to Telegram MUST follow the `telegram-message-format` skill. The short version:
+
+- `parse_mode: "HTML"` — never `Markdown` (it destroys code blocks and leaves `*bold*` literal).
+- `<b>` for headings, `<code>` for inline identifiers, `<pre>` for code blocks; escape `&`, `<`, `>` inside them.
+- No ` ``` ` fences, no `*emphasis*`.
+- Persian text without U+200C ZWNJ (use a normal space where the half-space belongs).
+- Keep each message under ~3800 characters; split longer payloads into parts, each a reply to the same parent id.
+- Anchor the reply to the **source message** (`config.topic_id` root or the candidate's own id) so the message inherits the topic.
+
 ### Phase 2: Manager Approval
 
 1. Check the session capability manifest for the `question` tool first. If AVAILABLE, use it to present the identified candidates to the Manager. If UNAVAILABLE, do NOT silently skip this approval: relay the candidate list to the Manager as one message with the options inline and wait for the answer (manual mode), or record the replay-or-halt decision in the task file (autopilot mode).
@@ -276,14 +289,17 @@ rm update_sync.py
 
 **9. Reply in Telegram:**
 
-Call `telegram_reply_to_message` with:
+Call `telegram_reply_to_message` with `parse_mode: "HTML"`, anchored to the **source message** (`config.topic_id` root, or the candidate's own message id) so the reply inherits the topic. The payload MUST follow the `telegram-message-format` skill — no emoji, no Markdown fences, no ZWNJ in Persian text, under ~3800 characters.
 
+```html
+<b>Task synced</b>
+
+<b>File:</b> <code>tasks/backlog/{NEXT_ID}-title.md</code>
+<b>Issue:</b> <code>{GH_URL}</code>
+<b>Type:</b> {BUG|FEATURE|IMPROVE}
 ```
-✅ Task synced successfully.
-📁 Local File: tasks/backlog/{NEXT_ID}-title.md
-🌐 GitHub Issue: {GH_URL}
-📝 Type: {BUG|FEATURE|IMPROVE}
-```
+
+When the candidate is one of several in the same batch, add a leading line `<b>Task synced</b> (2 of 5)` so the Manager can match the reply to the message. If the payload would exceed ~3800 characters, split it into numbered parts, each a reply to the same parent id.
 
 ---
 
@@ -308,3 +324,4 @@ Task ready. Manager, please copy the contents of tasks/backlog/{NEXT_ID}-task.md
 | Codebase search misses context  | Three-pass search strategy (grep → glob → read) with fallback: if grep yields 0 results, broaden the search terms                                                                  |
 | State file has concurrent edits | Single-threaded Python updater script with atomic `json.dump` write                                                                                                                |
 | GitHub issue creation fails     | `GH_URL` gracefully defaults to `"Failed to create"`; the task file and Telegram reply still complete                                                                              |
+| Telegram reply renders broken   | The reply is sent with `parse_mode: "HTML"` and the `telegram-message-format` rules (escaping, no fences, no ZWNJ, length budget, topic anchoring)                             |
diff --git a/skill-templates/telegram-message-export/SKILL.md b/skill-templates/telegram-message-export/SKILL.md
index f598d82..3cb3716 100644
--- a/skill-templates/telegram-message-export/SKILL.md
+++ b/skill-templates/telegram-message-export/SKILL.md
@@ -56,3 +56,17 @@ rm -rf export-{timestamp}/
 ## Phase 4: Notification
 
 Output exactly: "✅ Contextual Telegram export complete. Range: {from_id} to {to_id}. Archive path: <workspace>/telegram-exports/export-{timestamp}.zip"
+
+## Phase 5: Optional Telegram Delivery
+
+When the archive is delivered to a chat through the Telegram MCP, the caption and any follow-up message MUST follow the `telegram-message-format` skill:
+
+- `parse_mode: "HTML"`, with `<b>` for the heading and `<code>` for the archive path.
+- No Markdown fences, no ZWNJ in Persian text, under ~3800 characters.
+- For a forum topic, deliver with `telegram_send_file(chat_id, file_path, caption, topic_id=...)` (it accepts `topic_id`) or with `telegram_reply_to_message` anchored to a message already inside the topic. `telegram_send_message` has no `topic_id` and lands in General.
+
+```html
+<b>Export archive</b>
+
+<code>export-{timestamp}.zip</code> — {count} messages, {media_count} media files.
+```
diff --git a/skill-templates/telegram-message-format/SKILL.md b/skill-templates/telegram-message-format/SKILL.md
new file mode 100644
index 0000000..b87bff9
--- /dev/null
+++ b/skill-templates/telegram-message-format/SKILL.md
@@ -0,0 +1,164 @@
+---
+name: telegram-message-format
+description: Formats every outgoing Telegram MCP message so it renders cleanly in Telegram. Use before any send, reply, edit, or caption through the Telegram MCP - covers parse mode, HTML escaping, length splitting, forum-topic targeting, Persian text, and read-back verification.
+---
+
+# Telegram Message Formatting SOP
+
+## Purpose
+
+Every message an agent sends through the Telegram MCP must be clean, readable, and correctly rendered. The Telegram MCP server does **not** behave like the Bot API: it silently destroys Markdown structure, rejects over-length payloads with an opaque error, drops Persian half-spaces, and has no topic parameter on `send_message`.
+
+This skill is the agent-facing rulebook. The full evidence (probe transcripts, defect list, server-side recommendations) lives in the HQ repository at `docs/telegram-message-formatting.md`.
+
+**Load this skill before any Telegram send.** It applies to `send_message`, `reply_to_message`, `edit_message`, `send_file` captions, and any other tool that puts text into a chat.
+
+---
+
+## The 9 Rules
+
+| # | Rule                                                                                                    | Why                                                                            |
+| - | ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
+| 1 | Always send with `parse_mode: "HTML"`.                                                                   | Markdown mode strips fence/backtick markers and creates no entities.          |
+| 2 | Escape `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;` inside `<pre>` and `<code>`.                             | A raw `<` breaks the HTML parse and aborts the entire message.                |
+| 3 | Use `<b>` for headings, `<code>` for inline identifiers, `<pre>` for code blocks.                          | These three are the only elements proven to survive the round-trip.           |
+| 4 | Never use ` ``` ` fences or `*bold*` Markdown syntax.                                                     | Fences vanish; asterisks stay literal.                                        |
+| 5 | Write Persian without U+200C ZWNJ — use a normal space where the half-space belongs.                      | ZWNJ is lost on the read path of every message, including hand-typed ones.    |
+| 6 | Keep each message under ~3800 characters; split longer payloads into parts, each a reply to the same parent id. | The hard cap is 4096 chars and the failure is an opaque `GEN-ERR-184`.      |
+| 7 | Post into a forum topic with `reply_to_message` anchored to a message already inside that topic.           | `send_message` has no `topic_id` and lands in General.                        |
+| 8 | Verify a formatted send by reading it back and checking the `&lt;`/`&gt;` round-trip.                      | `get_history` resolves entities to plain text, so a text diff proves nothing. |
+| 9 | Delete every probe message after reading it back.                                                         | Keeps the chat clean; message ids are never reused.                           |
+
+---
+
+## Rule Details
+
+### 1–4. Parse mode and markup
+
+- `parse_mode: "HTML"` is the only mode that works. `Markdown` consumes ` ``` ` fences and inline backticks without creating the matching Telegram entities, and leaves `*bold*` as literal asterisks.
+- A message with **no** markup needs no parse mode at all — plain text is safe.
+- The safe element set is `<b>`, `<i>`, `<u>`, `<code>`, `<pre>`, `<a>`. Everything else is unverified — do not use it.
+- `<pre>` keeps its block boundaries. Put the code body inside it, escape `&`, `<`, `>`, and keep the language hint as plain text inside the block (the server does not support a language attribute).
+- One unescaped `<` in the payload rejects the whole message, so escape **all** angle brackets inside `<pre>` and `<code>`, including shell redirects (`>`) and generics.
+
+### 5. Persian text (and any non-ASCII text)
+
+- The server drops U+200C ZERO WIDTH NON-JOINER on the read path. It is lost for every message, not only agent-authored ones.
+- Author Persian with a **normal space** where the half-space belongs: `می کند`, `قابل تسویه`, `نمی فهمم`. Never paste a ZWNJ into authored text.
+- Same caution for other `Cf` (format) characters: zero-width space, BOM, soft hyphen. Use plain text.
+
+### 6. Length budget and splitting
+
+- Hard cap: **4096 characters**. Over that, the server returns `An error occurred (code: GEN-ERR-184)` with no hint — never retry it, it is not transient.
+- Plan on **~3800 characters** per message to leave headroom for the reply anchor and for entity overhead.
+- Count characters, not bytes. Persian, Arabic, and emoji payloads hit the cap well before their byte length suggests.
+- When a payload exceeds the budget, split it into numbered parts, each sent as a reply to the **same** parent message id, so the thread stays readable:
+
+  ```html
+  <b>Report — part 1 of 3</b>
+
+  ... first third ...
+
+  <i>Continued in the next reply.</i>
+  ```
+
+- Keep the part count minimal and never split inside a `<pre>` block.
+
+### 7. Forum topics
+
+- `send_message` accepts `chat_id`, `message`, `parse_mode`, `format_date`, `custom_emojis`, `account` — **no `topic_id`**. In a supergroup with forum topics enabled it lands in **General**.
+- `send_album` and `send_file` do accept `topic_id`.
+- To post into a topic, reply to a message that already lives in that topic — a reply inherits the topic of its parent:
+
+  ```text
+  reply_to_message(chat_id, message_id=<id inside the target topic>, account, parse_mode="HTML", text=...)
+  ```
+
+- Never post a topic-scoped confirmation with `send_message`.
+
+### 8. Read-back verification
+
+- `get_history` returns text with entities already resolved, so comparing the read-back text against the sent text **cannot** prove the formatting was applied.
+- The reliable check is the entity round-trip: send `&lt;` inside a `<pre>` block, read it back, and confirm it came back as a literal `<` with the block intact. If the literal `&lt;` is still there, the HTML was not parsed.
+
+### 9. Probe hygiene
+
+- Every probe message must be deleted with `delete_message(chat_id, message_id, account)` after it is read back.
+- Deleting does not renumber the remaining messages; later messages keep their ids. Treat a cached id as "may no longer resolve" rather than "was renumbered".
+
+---
+
+## Message Templates
+
+### Short prose message
+
+```html
+<b>Short heading</b>
+
+Plain prose with <code>identifiers</code> and no markup dependency.
+```
+
+### Report with a code block
+
+```html
+<b>Heading</b> and <code>inline_identifier</code>
+
+<pre>curl -X POST "https://example.com/api" \
+  --data 'key=value'</pre>
+
+<b>Second heading</b>
+
+<pre>SELECT id, state FROM trades WHERE id = 2069;</pre>
+
+Notes with <code>snake_case_names</code> inline.
+```
+
+### Status confirmation on a task
+
+```html
+<b>Task synced</b>
+
+<b>File:</b> <code>tasks/backlog/123-example.md</code>
+<b>Issue:</b> <code>https://github.com/org/repo/issues/7</code>
+<b>Type:</b> BUG
+```
+
+Keep the body plain — no emoji, no ASCII art, no horizontal rules made of dashes. One blank line between blocks, never more.
+
+### File caption (for `send_file`)
+
+```html
+<b>Export archive</b>
+
+<code>export-20261021-101500.zip</code> — 42 messages, 6 media files.
+```
+
+---
+
+## Pre-Send Checklist
+
+Run through this before every send:
+
+1. `parse_mode` is `"HTML"`, or the message is pure plain text with no markup.
+2. Every `&`, `<`, `>` inside `<pre>` / `<code>` is escaped.
+3. No ` ``` ` fences and no `*asterisk*` emphasis anywhere.
+4. No U+200C or other `Cf` characters in the text.
+5. The message is under ~3800 characters — or it is split into numbered parts.
+6. The target is a topic → the send is a `reply_to_message` to a message inside that topic.
+7. The payload is not raw LLM output: it has been read once and checked for stray angle brackets and Markdown leftovers.
+
+---
+
+## Server Defects (known, unfixed)
+
+The following are upstream defects in the Telegram MCP server. Work around them; do not report them as your own errors, and do not retry them.
+
+| Defect                                                | Workaround                                                       |
+| ----------------------------------------------------- | ---------------------------------------------------------------- |
+| Over-length message returns opaque `GEN-ERR-184`       | Self-enforce the 3800-character budget; never retry.            |
+| Markdown mode destroys code blocks                    | Use HTML.                                                         |
+| Markdown `*bold*` not applied                         | Use `<b>`.                                                        |
+| ZWNJ lost on the read path                            | Author Persian without U+200C.                                   |
+| `send_message` cannot target a forum topic            | Use `reply_to_message` anchored inside the topic.                |
+| Message `entities` not exposed on read               | Verify with the `&lt;`/`&gt;` round-trip, not a text diff.      |
+| Length counted without UTF-16 semantics                | Count characters yourself, not bytes.                            |
diff --git a/system-prompt.md b/system-prompt.md
index 7fc1c29..029d566 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.63.0</system_version>
+<system_version>9.64.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -133,6 +133,7 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **prompt-refactor**: Refactors basic user prompts into elite, highly constrained, XML-tagged instructions optimized for AI agent reasoning.
 - **telegram-issue-sync**: Syncs Telegram supergroup topics into local task files and GitHub issues, using embedded Python scripts for deterministic JSON state management.
 - **telegram-message-export**: Intelligently exports a range of Telegram messages (text, media, voice notes) into a numbered folder, capturing reply hierarchies, and packing them into a ZIP archive.
+- **telegram-message-format**: Formats every outgoing Telegram MCP message so it renders cleanly in Telegram. Load before any send, reply, edit, or caption through the Telegram MCP — covers parse mode, HTML escaping, length splitting, forum-topic targeting, Persian text, and read-back verification.
 - **design-md**: Extract a comprehensive design system (DESIGN.md) directly from frontend source code — React, Vue, Svelte, Angular, plain HTML/CSS, or any web framework. Analyzes component files, stylesheets, Tailwind configs, theme definitions, and design tokens to produce a rich, Stitch-compatible design system document.
 - **doc-coauthoring**: Guide users through a structured workflow for co-authoring documentation. Use when user wants to write documentation, proposals, technical specs, decision docs, or similar structured content.
 - **project-memory**: Smart note-taking and persistent project memory. Automatically saves Manager constraints and proactively retrieves context to prevent hallucinations.
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index b1284f0..94dfc25 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -44,7 +44,7 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.63.0"
+    assert shipped == "9.64.0"
 
 
 def test_executor_carries_compaction_guidance():
diff --git a/tests/test_skill_registry.py b/tests/test_skill_registry.py
index ce48949..ee61cd4 100644
--- a/tests/test_skill_registry.py
+++ b/tests/test_skill_registry.py
@@ -355,6 +355,41 @@ def test_validate_opencode_positives():
     assert _run_validator(cfg) == (0, "")
 
 
+def test_telegram_message_format_skill_contract():
+    text = _template_text("telegram-message-format")
+    for required in (
+        'parse_mode: "HTML"',
+        "&amp;",
+        "&lt;",
+        "&gt;",
+        "U+200C",
+        "3800",
+        "reply_to_message",
+        "GEN-ERR-184",
+        "4096",
+    ):
+        assert required in text, f"contract term missing: {required}"
+    reg = REGISTRY.read_text(encoding="utf-8")
+    assert "telegram-message-format" in reg
+
+
+def test_telegram_skills_obey_the_format_contract():
+    for name in ("telegram-issue-sync", "telegram-message-export"):
+        assert "telegram-message-format" in _template_text(name), name
+    issue_sync = _template_text("telegram-issue-sync")
+    assert 'parse_mode: "HTML"' in issue_sync
+    assert "3800" in issue_sync
+    assert "U+200C" in issue_sync
+
+
+def test_telegram_formatting_contract_doc_exists():
+    doc = ROOT / "docs" / "telegram-message-formatting.md"
+    assert doc.is_file(), "formatting contract doc missing"
+    text = doc.read_text(encoding="utf-8")
+    for required in ("4096", "GEN-ERR-184", "U+200C", "topic_id", "parse_mode"):
+        assert required in text, f"doc term missing: {required}"
+
+
 def _project_skills_table_rows():
     text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
     m = re.search(r"## .*PROJECT SKILLS.*\n\n((?:\|.*\n)+)", text)
```
<!-- END_GIT_DIFF -->
