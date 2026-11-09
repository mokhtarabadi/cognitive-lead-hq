## Part 3: Telegram Issue Sync & Discussion Crawler SOP (from `telegram-issue-sync`)

# Telegram Issue Sync & Discussion Crawler SOP

## Purpose

Syncs actionable Telegram messages into GitHub Issues and local `tasks/` files. Unlike the previous version which **summarized** raw messages (BUG: Phase 3 Step 2 had vague "inject translated context" language that allowed LLMs to paraphrase and discard the original text), this SOP enforces:

- **Zero-summarization**: raw non-English text is preserved verbatim in its original language
- **Bilingual task files**: original message + complete English translation
- **Prompt refactoring**: loads `prompt-refactor` skill to generate an enhanced prompt from the raw text
- **Codebase correlation**: autonomously searches the codebase for files relevant to the described bug/feature
- **Interactive cycle**: asks Manager for approval → generates tasks → optionally creates GitHub issues → replies to Telegram

## Root Cause of the Summarization Bug

The old Phase 3 Step 2 read:

> _"Inject the translated Telegram discussion context and codebase correlation."_

This was **ambiguously phrased** — it did not mandate verbatim preservation. LLMs interpret "inject context" as "extract the gist and summarize." The fix is:

1. Explicit `## Original Message (<Language>)` section with the **exact raw text** — no transformation allowed
2. A separate `## English Translation` section so the original is never overwritten or merged
3. Strict `execution_rules` in the system prompt forbidding any truncation or paraphrasing

## Local State Schema (`telegram-sync.json`)

```json
{
  "config": {
    "project_name": "[Name]",
    "chat_id": "[Chat ID]",
    "topic_id": null,
    "account": null,
    "target_hashtags": ["bug", "feature", "improve"]
  },
  "last_processed_message_id": 0,
  "processed_ids": [],
  "sync_registry": {}
}
```

## Detailed Workflow

### Phase 0: Load Mandatory Skills

Before any Telegram fetching, you MUST load these skills:

```markdown
1. Load `kanban-lifecycle` skill — ensures task files use the correct template with `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.
2. Load `prompt-refactor` skill — will be used in Phase 3 to generate the `## Refactored Prompt` section.
3. Load `telegram-suite` skill (Part 1) — governs every message this skill sends back to Telegram (parse mode, escaping, length splitting, Persian text, topic targeting). MANDATORY before the Phase 3 reply step.
```

Use the `skill` tool for each. If loading fails, HALT and report the error.

### Phase 1: Context Fetch & Deep Crawling

1. Read `telegram-sync.json` at the project root to get `config.chat_id`, `config.topic_id`, `config.account`, and `last_processed_message_id`.
2. Call `telegram_get_history` (with `account` if set, limit=100). This returns messages from ALL forum topics — Telegram has no server-side topic filter. **You MUST client-filter** to `reply_to == config.topic_id` OR walk the `reply_to` chain via `telegram_get_message_context` until you reach the topic root `config.topic_id`. Only messages whose `reply_to` chain terminates at `config.topic_id` belong to this project. Then additionally filter for `id > last_processed_message_id`.
3. **Candidate Selection:** Identify messages containing `target_hashtags` from the _topic-filtered_ set. Also identify messages without hashtags that strongly resemble bug reports or feature requests.
4. **Deep Context:** For every selected candidate, check `reply_to_message_id`. If it exists, call `telegram_get_message_context` to fetch the parent message. Merge the parent message (the "what") with the child message (the "intent").

**CRITICAL — Message Integrity Rule:** Store the raw message text in a variable `RAW_TEXT` immediately after fetching. You MUST NOT modify, trim, or summarize this value at any point. Use it verbatim in Phase 3.

### Forum Topic Targeting (Critical)

This MCP implementation does **NOT** expose a `topic_id` parameter. Forum topics are identified by the `reply_to` field:

- **Reading messages from a specific topic:** Call `telegram_get_history(chat_id=config.chat_id, limit=100, account=config.account)`. It returns messages from all topics. **Filter results by `reply_to`** — direct replies have `reply_to == config.topic_id` (e.g., `458` = Cognitive Lead, `455` = other project, `1` = General). For nested replies, walk the chain via `telegram_get_message_context` recursively until you hit the topic root `MessageActionTopicCreate`; discard messages whose chain terminates at `455`/`1`/`null`.
- **Sending a message to a specific topic:** You MUST use `telegram_reply_to_message` with `message_id` set to `config.topic_id`. Never post topic confirmations to General.
- **`telegram_send_message` MUST NOT be used for topic-scoped output:** it has no `topic_id` parameter, so it always lands in General.
- **MANDATORY per `.opencode/memory/telegram-sync/topic-scoped-sync-workflow.md`:** `config.topic_id` defines the ONLY channel to sync. NEVER fetch/scan group-wide history.

### Outgoing Message Formatting (Critical)

Every message this skill sends to Telegram MUST follow Part 1 (`telegram-suite` formatting contract). The short version:

- `parse_mode: "HTML"` — never `Markdown` (it destroys code blocks and leaves `*bold*` literal).
- `<b>` for headings, `<code>` for inline identifiers, `<pre>` for code blocks; escape `&`, `<`, `>` inside them.
- No ` ``` ` fences, no `*emphasis*`.
- Persian text without U+200C ZWNJ (use a normal space where the half-space belongs).
- Keep each message under ~3800 characters; split longer payloads into parts, each a reply to the same parent id.
- Anchor the reply to the **source message** (`config.topic_id` root or the candidate's own id) so the message inherits the topic.

### Phase 2: Manager Approval

1. Check the session capability manifest for the `question` tool. If AVAILABLE, use it to present the candidates and collect approval. If the required tool is UNAVAILABLE_REQUIRED, manual mode relays the returned capability block verbatim and pauses; autopilot halts with that block as the named blocker. Never make a self-selected approval decision or proceed without the required approval.
2. Phase 2 Candidate approval with brief-first options. For each candidate capture timestamp, sender, first 200 characters of the raw text, detected type (bug/feature/improve), topic, reply parent context (if any), and the numeric message ID. Present one `question`-tool option per candidate. Each option label starts with the timestamp in YYYY-MM-DD HH:MM enclosed in square brackets, followed by the sender name, a dash, the first 80 characters single-line, plus type and topic in parentheses. Each option description holds the full 200-character snippet, the type, the reply parent, and the internal ID for audit. Each option machine value is the numeric ID only and the ID is never shown as primary text. Never ask the Manager for bare message IDs: the closing prompt asks the Manager to reply with option numbers, names, or All. Manual-mode fallback when the `question` tool is unavailable renders a numbered brief list with the same label text; the Manager replies with numbers and you map numbers to IDs server-side in the same turn via a lookup table built from the listed candidates. Re-read the table before syncing to prevent a wrong anchor. All Telegram-facing text obeys the `telegram-suite` contract for HTML parse mode plus escaping plus no fences plus 4096 cap with splitting. Sync only approved IDs.
3. Also ask: _"Should GitHub issues be created for these? (yes/no)"_
4. Only proceed with the approved candidates. Log chosen IDs plus the mapping table in the task Execution Log.

Store the Manager's GitHub preference in a variable `GH_ENABLED` (true/false).

Autopilot note: the data question in step 4 (whether GitHub issues are wanted) folds into the planning turn. The Hands asks it once alongside candidate approval, records the answer in the task file, and never asks again mid-task.

### Phase 3: Task Generation & Automation (Per Approved Candidate)

For **each** approved candidate, execute the following steps **strictly in order**:

> **TASK-GENERATOR MIRROR MANDATE:** Task creation MUST mirror `kanban-lifecycle` exactly: same ID discovery command, same duplicate-title check, same duplicate-ID check, same collision check, same canonical template, and same `## Definition of Done` block. Do NOT maintain divergent logic — if the `kanban-lifecycle` skill's workflow changes, mirror those changes here.

---

**0. Mirror Checks (from kanban-lifecycle):**

Before writing the task file, run the same guards the `kanban-lifecycle` skill runs:

```bash
# Duplicate-title check
grep -rhn "^# Task [0-9][0-9]*:" tasks/ | sort | uniq -d
# Duplicate-ID check (active Kanban dirs only — archive never blocks)
find tasks/backlog tasks/in-progress tasks/qa tasks/completed -type f -name "*.md" -exec basename {} \; | grep -Eo '^[0-9]+' | sort | uniq -d
# Collision check
ls tasks/backlog/${NEXT_ID}-*.md
```

If any check returns output, HALT and report the collision. Do NOT overwrite files. Archive is a historical record and MUST NOT be included in the blocking duplicate-ID check. If archive duplicates are discovered separately, report them as a warning only, never HALT task creation. Then confirm the generated task file includes the same `## Definition of Done` block as `kanban-lifecycle` (Build/Test/Lint exit 0, `lint_task_file` passes, `CHANGELOG.md` via Parse-Then-Append, `testing-verification` evidence).

---

**1. Determine Next Task ID:**

Run this bash command (searches across all Kanban subdirectories):

```bash
NEXT_ID=$(find tasks/ -type f -name "*.md" -exec basename {} \; | grep -Eo '^[0-9]+' | sort -n | tail -1 | awk '{print $1+1}')
if [ -z "$NEXT_ID" ] || [ "$NEXT_ID" -eq 0 ]; then NEXT_ID="01"; fi
printf "%02d\n" $NEXT_ID
```

---

**2. Generate English Translation:**

Using the `RAW_TEXT` (the verbatim original message, in whatever language it was written), produce a complete English translation. Store it in a variable `EN_TRANSLATION`.

---

**3. Load & Run Prompt Refactor (The Omni-Channel Filter):**

The `prompt-refactor` skill should already be loaded (from Phase 0). Use it as the omni-channel filter: pass the `RAW_TEXT` (in its original language) to it so it translates the text to English, expands the architectural intent, and generates an enhanced "Max Power" prompt. Store the output in a variable `REFACTORED_PROMPT`.

The refactored prompt MUST include the 5 XML blocks:

- `<role>`
- `<system_context>`
- `<agentic_reasoning>`
- `<constraints>` or `<execution_rules>`
- `<output_format>`

---

**4. Search Codebase for Relevant Context:**

Use codebase exploration tools to find files related to the bug/feature described in the `RAW_TEXT`. Execute searches in this order:

```markdown
1. grep for key technical terms from the message across the codebase
2. glob for likely file patterns (e.g., if the bug mentions "sync" → `**/*sync*`)
3. Read the top 2-3 most relevant files to extract key excerpts
```

Store the results as `CODEBASE_CONTEXT` — a list of file paths with brief relevant excerpts.

---

**5. Generate Your AI Analysis & Opinion:**

Form an architectural diagnosis:

- What is the root cause of the issue described?
- What is the recommended fix?
- What files need to change?
- What are the risks?

Store as `AI_OPINION`.

---

**6. Generate Local Task File:**

Create `tasks/backlog/{NEXT_ID}-hyphenated-title.md` using the **unified canonical template** from the `kanban-lifecycle` skill, with `**Source:** telegram`. Do NOT define a separate inline template — the `kanban-lifecycle` skill is the single source of truth for the file structure.

Populate the telegram variant (`## Source Context` → Variant B) by filling these fields:

- `## Goal` — **MANDATORY.** Derive a one-line goal from the `RAW_TEXT` before writing the file.
- `## Acceptance Criteria` — **MANDATORY.** Derive 2-3 concrete, verifiable conditions from the Telegram message's intent before writing the file.
- `## Original Message ({LANGUAGE})` — `{RAW_TEXT}` — **verbatim, zero changes.**

  **RULE:** The `## Original Message` section MUST contain the exact text from Telegram. The section header names the detected language: `## Original Message (<Language>)`. If the language is unknown, use `## Original Message (Raw)`.

- `## English Translation` — `{EN_TRANSLATION}`
- `## Refactored Prompt` — `{REFACTORED_PROMPT}`
- `## Relevant Code Context` — `{CODEBASE_CONTEXT}`
- `## AI Analysis & Opinion` — `{AI_OPINION}`

`## Local TODOs` MUST be populated with at minimum:

```markdown
- [ ] Initial codebase exploration
- [ ] Verify functionality
```

---

**7. Create GitHub Issue (Optional):**

Only if `GH_ENABLED` is true, create a unique temporary Markdown body file inside the project workspace with a native file-write tool. Put the Original Message, English Translation, AI Analysis, and migration note in that file. Set `BODY_FILE` to its concrete workspace-relative path, then run:

```bash
GH_URL=$(gh issue create \
  --title "{Task Title}" \
  --body-file "$BODY_FILE" \
  --label "telegram-sync")
printf 'GH_URL=%s\n' "$GH_URL"
```

After recording the result, delete only that exact temporary file with a native file-management tool. Do not use shell redirection, scripts, or an outside-workspace path to create the body file.

If `GH_ENABLED` is false, set `GH_URL="Not created (skipped)"`.

---

**8. Update State Deterministically with native file tools:**

Edit `telegram-sync.json` using a native file-editing tool. Preserve unrelated keys. Set `last_processed_message_id` to the larger of its current value and the approved message ID. Add the message ID to `processed_ids` only if absent, then sort that list. Set `sync_registry[str(message_id)]` to an object containing the generated task-file path, the GitHub URL or recorded skip value, and the uppercase issue type. Do not create or execute a helper script and do not use shell or Python to write the JSON file. Verify the resulting JSON with `python3 -m json.tool telegram-sync.json` and inspect the native-tool diff.

---

**9. Reply in Telegram:**

Call `telegram_reply_to_message` with `parse_mode: "HTML"`, anchored to the **source message** (`config.topic_id` root, or the candidate's own message id) so the reply inherits the topic. The payload MUST follow Part 1 — no emoji, no Markdown fences, no ZWNJ in Persian text, under ~3800 characters.

```html
<b>Task synced</b>

<b>File:</b> <code>tasks/backlog/{NEXT_ID}-title.md</code> <b>Issue:</b>
<code>{GH_URL}</code> <b>Type:</b> {BUG|FEATURE|IMPROVE}
```

When the candidate is one of several in the same batch, add a leading line `<b>Task synced</b> (2 of 5)` so the Manager can match the reply to the message. If the payload would exceed ~3800 characters, split it into numbered parts, each a reply to the same parent id.

---

### Phase 4: Mark Non-Actionable Messages

Once all approved tasks are generated, edit `telegram-sync.json` with native file tools to update `last_processed_message_id` to the highest message ID observed in the batch and append the skipped IDs to `processed_ids`. Do not use a helper script.

### Phase 5: Return Control

For each generated task, invoke `brain_turn` directly under the active session thread with that task ID and task-file context. Do not ask the Manager to copy, paste, or relay task contents. Keep each task under the normal plan and approval gates. After the Brain turns return, report that the task files are ready for Orchestrator review.

## Data Integrity Guarantees

| Risk                            | Mitigation                                                                                                                                                                         |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LLM summarizes raw text         | `## Original Message` is declared as verbatim; the system prompt for the task-generation LLM MUST include "Do NOT summarize, paraphrase, or truncate the Original Message section" |
| Non-English text gets corrupted | The raw text is stored immediately on fetch and never re-encoded; the task file is written in UTF-8                                                                                |
| Codebase search misses context  | Three-pass search strategy (grep → glob → read) with fallback: if grep yields 0 results, broaden the search terms                                                                  |
| State file has concurrent edits | Single-threaded Python updater script with atomic `json.dump` write                                                                                                                |
| GitHub issue creation fails     | `GH_URL` gracefully defaults to `"Failed to create"`; the task file and Telegram reply still complete                                                                              |
| Telegram reply renders broken   | The reply is sent with `parse_mode: "HTML"` and the Part 1 rules (escaping, no fences, no ZWNJ, length budget, topic anchoring)                                 |
