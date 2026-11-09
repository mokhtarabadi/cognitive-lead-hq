---
name: telegram-suite
description: Unified Telegram skills — HTML message formatting, contextual export to ZIP, and issue sync to tasks/GitHub.
---

# Telegram Suite Meta Skill

Meta skill combining **telegram-message-format** (HTML formatting contract), **telegram-message-export** (contextual range export), and **telegram-issue-sync** (topic sync to tasks/GitHub). All outgoing Telegram messages in any part MUST follow Part 1. Sections are verbatim from the source skills.

---

## Part 1: Telegram Message Formatting SOP (from `telegram-message-format`)

## Purpose

Every message an agent sends through the Telegram MCP must be clean, readable, and correctly rendered. The Telegram MCP server does **not** behave like the Bot API: it silently destroys Markdown structure, rejects over-length payloads with an opaque error, drops Persian half-spaces, and has no topic parameter on `send_message`.

This skill is the agent-facing rulebook. The full evidence (probe transcripts, defect list, server-side recommendations) lives in the HQ repository at `docs/telegram-message-formatting.md`.

**Load this skill before any Telegram send.** It applies to `send_message`, `reply_to_message`, `edit_message`, `send_file` captions, and any other tool that puts text into a chat.

---

## The 9 Rules

| # | Rule                                                                                                    | Why                                                                            |
| - | ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| 1 | Always send with `parse_mode: "HTML"`.                                                                   | Markdown mode strips fence/backtick markers and creates no entities.          |
| 2 | Escape `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;` inside `<pre>` and `<code>`.                             | A raw `<` breaks the HTML parse and aborts the entire message.                |
| 3 | Use `<b>` for headings, `<code>` for inline identifiers, `<pre>` for code blocks.                          | These three are the only elements proven to survive the round-trip.           |
| 4 | Never use ` ``` ` fences or `*bold*` Markdown syntax.                                                     | Fences vanish; asterisks stay literal.                                        |
| 5 | Write Persian without U+200C ZWNJ — use a normal space where the half-space belongs.                      | ZWNJ is lost on the read path of every message, including hand-typed ones.    |
| 6 | Keep each message under ~3800 characters; split longer payloads into parts, each a reply to the same parent id. | The hard cap is 4096 chars and the failure is an opaque `GEN-ERR-184`.      |
| 7 | Post into a forum topic with `reply_to_message` anchored to a message already inside that topic.           | `send_message` has no `topic_id` and lands in General.                        |
| 8 | Verify a formatted send by reading it back and checking the `&lt;`/`&gt;` round-trip.                      | `get_history` resolves entities to plain text, so a text diff proves nothing. |
| 9 | Delete every probe message after reading it back.                                                         | Keeps the chat clean; message ids are never reused.                           |

---

## Rule Details

### 1–4. Parse mode and markup

- `parse_mode: "HTML"` is the only mode that works. `Markdown` consumes ` ``` ` fences and inline backticks without creating the matching Telegram entities, and leaves `*bold*` as literal asterisks.
- A message with **no** markup needs no parse mode at all — plain text is safe.
- The safe element set is `<b>`, `<i>`, `<u>`, `<code>`, `<pre>`, `<a>`. Everything else is unverified — do not use it.
- `<pre>` keeps its block boundaries. Put the code body inside it, escape `&`, `<`, `>`, and keep the language hint as plain text inside the block (the server does not support a language attribute).
- One unescaped `<` in the payload rejects the whole message, so escape **all** angle brackets inside `<pre>` and `<code>`, including shell redirects (`>`) and generics.

### 5. Persian text (and any non-ASCII text)

- The server drops U+200C ZERO WIDTH NON-JOINER on the read path. It is lost for every message, not only agent-authored ones.
- Author Persian with a **normal space** where the half-space belongs: `می کند`, `قابل تسویه`, `نمی فهمم`. Never paste a ZWNJ into authored text.
- Same caution for other `Cf` (format) characters: zero-width space, BOM, soft hyphen. Use plain text.

### 6. Length budget and splitting

- Hard cap: **4096 characters**. Over that, the server returns `An error occurred (code: GEN-ERR-184)` with no hint — never retry it, it is not transient.
- Plan on **~3800 characters** per message to leave headroom for the reply anchor and for entity overhead.
- Count characters, not bytes. Persian, Arabic, and emoji payloads hit the cap well before their byte length suggests.
- When a payload exceeds the budget, split it into numbered parts, each sent as a reply to the **same** parent message id, so the thread stays readable:

  ```html
  <b>Report — part 1 of 3</b>

  ... first third ...

  <i>Continued in the next reply.</i>
  ```

- Keep the part count minimal and never split inside a `<pre>` block.

### 7. Forum topics

- `send_message` accepts `chat_id`, `message`, `parse_mode`, `format_date`, `custom_emojis`, `account` — **no `topic_id`**. In a supergroup with forum topics enabled it lands in **General**.
- `send_album` and `send_file` do accept `topic_id`.
- To post into a topic, reply to a message that already lives in that topic — a reply inherits the topic of its parent:

  ```text
  reply_to_message(chat_id, message_id=<id inside the target topic>, account, parse_mode="HTML", text=...)
  ```

- Never post a topic-scoped confirmation with `send_message`.

### 8. Read-back verification

- `get_history` returns text with entities already resolved, so comparing the read-back text against the sent text **cannot** prove the formatting was applied.
- The reliable check is the entity round-trip: send `&lt;` inside a `<pre>` block, read it back, and confirm it came back as a literal `<` with the block intact. If the literal `&lt;` is still there, the HTML was not parsed.

### 9. Probe hygiene

- Every probe message must be deleted with `delete_message(chat_id, message_id, account)` after it is read back.
- Deleting does not renumber the remaining messages; later messages keep their ids. Treat a cached id as "may no longer resolve" rather than "was renumbered".

---

## Message Templates

### Short prose message

```html
<b>Short heading</b>

Plain prose with <code>identifiers</code> and no markup dependency.
```

### Report with a code block

```html
<b>Heading</b> and <code>inline_identifier</code>

<pre>curl -X POST "https://example.com/api" \
  --data 'key=value'</pre>

<b>Second heading</b>

<pre>SELECT id, state FROM trades WHERE id = 2069;</pre>

Notes with <code>snake_case_names</code> inline.
```

### Status confirmation on a task

```html
<b>Task synced</b>

<b>File:</b> <code>tasks/backlog/123-example.md</code>
<b>Issue:</b> <code>https://github.com/org/repo/issues/7</code>
<b>Type:</b> BUG
```

Keep the body plain — no emoji, no ASCII art, no horizontal rules made of dashes. One blank line between blocks, never more.

### File caption (for `send_file`)

```html
<b>Export archive</b>

<code>export-20261021-101500.zip</code> — 42 messages, 6 media files.
```

---

## Pre-Send Checklist

Run through this before every send:

1. `parse_mode` is `"HTML"`, or the message is pure plain text with no markup.
2. Every `&`, `<`, `>` inside `<pre>` / `<code>` is escaped.
3. No ` ``` ` fences and no `*asterisk*` emphasis anywhere.
4. No U+200C or other `Cf` characters in the text.
5. The message is under ~3800 characters — or it is split into numbered parts.
6. The target is a topic → the send is a `reply_to_message` to a message inside that topic.
7. The payload is not raw LLM output: it has been read once and checked for stray angle brackets and Markdown leftovers.

---

## Server Defects (known, unfixed)

The following are upstream defects in the Telegram MCP server. Work around them; do not report them as your own errors, and do not retry them.

| Defect                                                | Workaround                                                       |
| ----------------------------------------------------- | ---------------------------------------------------------------- |
| Over-length message returns opaque `GEN-ERR-184`       | Self-enforce the 3800-character budget; never retry.            |
| Markdown mode destroys code blocks                    | Use HTML.                                                         |
| Markdown `*bold*` not applied                         | Use `<b>`.                                                        |
| ZWNJ lost on the read path                            | Author Persian without U+200C.                                   |
| `send_message` cannot target a forum topic            | Use `reply_to_message` anchored inside the topic.                |
| Message `entities` not exposed on read               | Verify with the `&lt;`/`&gt;` round-trip, not a text diff.      |
| Length counted without UTF-16 semantics                | Count characters yourself, not bytes.                            |

---

## Part 2: Telegram Message Export Skill (from `telegram-message-export`)

# Telegram Message Export Skill

## Purpose

Extracts a highly contextual range of Telegram messages. It explicitly documents reply relationships to preserve conversation trees and packages text alongside downloaded media files (images, voice notes) into a ZIP file.

## Input Resolution

Determine the exact `[from_id, to_id]` range. If the Manager provided a text snippet, use `telegram_search_messages` to find the `msg_id`. If a link is provided (`t.me/c/CHAT_ID/MSG_ID`), extract the ID.

## Phase 1: Contextual Fetching

1. Call `telegram_get_history` and filter to keep messages where `id >= from_id` and `id <= to_id`.
2. Sort the filtered messages strictly by `id` in ascending order.
3. If the range spans more than 200 messages, ask for confirmation before proceeding to avoid rate limits. Use the `question` tool when the session capability manifest shows it AVAILABLE; otherwise relay the same question in prose and wait for the answer.

## Phase 2: Extraction & Sidecar Generation

1. Create directory: `mkdir -p <workspace>/telegram-exports/export-{timestamp}/`
2. Set counter `n = 1`.
3. For each message in the sorted list:

   **Text Sidecar (`{n}.txt`)**:
   Create a `.txt` file for every message. You MUST include `reply_to_message_id` to preserve thread context.

   ```text
   Message ID: {message.id}
   From: {sender_name_or_id}
   Date: {date}
   Reply To Message ID: {reply_to_message_id | 'None'}
   Message Type: {type}

   [Content]
   {message_text | caption | '[No extractable content]'}
   ```

   **Media Download**:
   If the message contains media, call `telegram_get_media_info` to get the extension. Then call `telegram_download_media(chat_id=..., message_id=..., file_path="<workspace>/telegram-exports/export-{timestamp}/{n}.{ext}")`.

4. Increment `n`.

## Phase 3: Archiving

Run the bash zip command:

```bash
cd <workspace>/telegram-exports && zip -r export-{timestamp}.zip export-{timestamp}/
rm -rf export-{timestamp}/
```

## Phase 4: Notification

Output exactly: "✅ Contextual Telegram export complete. Range: {from_id} to {to_id}. Archive path: <workspace>/telegram-exports/export-{timestamp}.zip"

## Phase 5: Optional Telegram Delivery

When the archive is delivered to a chat through the Telegram MCP, the caption and any follow-up message MUST follow the `telegram-suite` (Part 1) contract:

- `parse_mode: "HTML"`, with `<b>` for the heading and `<code>` for the archive path.
- No Markdown fences, no ZWNJ in Persian text, under ~3800 characters.
- For a forum topic, deliver with `telegram_send_file(chat_id, file_path, caption, topic_id=...)` (it accepts `topic_id`) or with `telegram_reply_to_message` anchored to a message already inside the topic. `telegram_send_message` has no `topic_id` and lands in General.

```html
<b>Export archive</b>

<code>export-{timestamp}.zip</code> — {count} messages, {media_count} media files.
```

---

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
