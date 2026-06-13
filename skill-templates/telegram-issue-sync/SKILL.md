---
name: telegram-issue-sync
description: Optional, pure agentic sync of Telegram supergroup topics into local task files and GitHub issues, featuring non-tagged conversation crawling.
---

# Telegram Issue Sync & Discussion Crawler SOP

## Purpose

Provides an optional, highly advanced workflow for syncing actionable Telegram supergroup messages into GitHub Issues and local task files without custom Python scripts, utilizing existing Telegram MCP and `gh` CLI tools. It features "Thread Crawling" to pull in non-tagged messages for discussion context.

## Telegram MCP Tool Behavior

All Telegram MCP tool calls accept an optional `account` parameter for multi-account setups. If `account` is set in your config, it is passed to every Telegram call. If omitted, the default account is used.

### Forum Topic Targeting (Critical)

This MCP implementation does **NOT** expose a `topic_id` parameter. All messages belong to the same flat chat (`chat_id`). Forum topics in supergroups are identified by the `reply_to` field on messages. To correctly scope operations:

- **Reading messages from a specific topic:** Call `telegram_get_history` with `chat_id`. It returns messages from all topics. Filter the results by checking `reply_to` field — messages belonging to your target topic have `reply_to` matching your `topic_id`. You can also use `telegram_get_message_context` around specific messages.

- **Discovering topics:** Call `telegram_list_topics` with `chat_id`. Returns all forum topics with their `id` and `title`.

- **Sending a message to a specific topic:** You MUST use `telegram_reply_to_message` with `message_id` set to the Topic ID (not `telegram_send_message` — that always lands in the General topic). Example:
  ```
  telegram_reply_to_message(chat_id="-1003517558062", message_id=2, text="Hello Apex!")
  ```

- **Reading messages:** `telegram_get_history` returns all messages. Filter by `reply_to == topic_id` to get messages scoped to your topic.

Always use `telegram_list_topics` first to verify the target topic ID and title exist before posting.

## Activation (Strictly Optional)

- This skill is **OPTIONAL**. Do NOT execute or force setup unless:
  - A `telegram-sync.json` file already exists at the project root.
  - **OR** the Manager explicitly commands a sync (e.g., "sync telegram", "@explore search telegram issues").
  - If neither condition is met, silently skip this skill entirely during initialization or normal tasks.

## Local State Schema (`telegram-sync.json`)

Stored at project root to track local configuration and message states:

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

- `topic_id` — optional. If your MCP supports forum topic scoping (e.g., `telegram_get_history` accepts a `topic_id`), set this to an integer topic ID. Otherwise leave `null`.
- `account` — optional. If your Telegram MCP uses multiple accounts, set this to the account label string. Otherwise leave `null`. All Telegram tool calls pass this value when present.

## Detailed Workflow

### Phase 1: Verification & Optional Onboarding

1. Check for `telegram-sync.json` at project root.
2. If missing AND the command was explicitly requested:
   - Run the `question` tool to interactively ask the Manager for:
     - `project_name` (required)
     - `chat_id` (required — ID or @username)
     - `target_hashtags` (required — comma-separated hashtags like `bug,feature,improve`)
     - `topic_id` (optional — integer topic ID if the chat is a forum supergroup and your MCP supports topic scoping)
     - `account` (optional — account label if your Telegram MCP uses multiple accounts)
   - Create the `telegram-sync.json` file with the collected config. Set `topic_id` and `account` to `null` if not provided. Set `last_processed_message_id` to `0` and initialize `processed_ids` and `sync_registry`.
3. If missing and NOT explicitly requested:
   - Abort this skill immediately. Do not prompt the user.

### Phase 2: Candidate Fetch & Discussion Crawling

1. **Fetch Message History:** Call `telegram_get_history` passing `chat_id` from config and `account` if set. The result may include messages from all forum topics. Filter the returned list to keep only messages where `reply_to == config.topic_id` to scope to your target topic.
2. **Primary Filter (Actionable Items):** Filter for messages where:
   - Message ID > `last_processed_message_id`
   - Message text contains any of the target hashtags (e.g., `#bug`, `#feature`, `#improve`).
3. **Secondary Filter (Discussion & Non-tagged Replies):** For each matched candidate:
   - Retrieve all replies and subsequent discussions via `telegram_get_message_context` (pass `account` if set) or by searching for replies to the candidate.
   - Fetch neighboring messages around the candidate's timestamp (+/- 10 minutes) in the same topic. Extract the non-tagged dialogue, questions, and decisions to capture the full context.
4. **Translation & Title Generation:**
   - Translate any Persian messages (and their crawl-extracted replies) into clear English.
   - **Rule 8 Compliance:** Generate a professional, concise title (<60 chars) prefixed with 'Bug: ', 'Feature: ', or 'Improve: '.
5. **Codebase Correlation:** Scan the workspace using `custom_context_extract_signatures` with keywords from the translated discussion to identify target files.

### Phase 2b: Backfill Audit — Existing Tasks Without GitHub Issues

Before processing new candidates, run a backfill audit:

1. **Scan `telegram-sync.json` `sync_registry`:** Find all entries where `gh_issue` is `null`.
2. **Scan local `tasks/` directory:** For each task file, check if it has an associated `**Msg ID:** NNN` line. Cross-reference against the registry to identify tasks missing GH issues.
3. **Present to Manager:** Use the `question` tool to ask if GH issues should be created for these orphaned tasks.
4. **For each approved backfill:**
   - Read the corresponding task file and reconstruct the GH issue body from its Objective/Telegram Discussion Context sections.
   - Run `gh issue create --title "[Sync] {Title}" --body "{Body}"` with appropriate label (`bug`/`enhancement`/`improvement`).
   - Update the `gh_issue` field in `sync_registry` to the returned issue number.

### Phase 3: Manager Approval & Multi-Sync

1. Present the candidates and their crawled discussions to the Manager using the `question` tool.
2. For each approved candidate:
   - **Local Task:** Load the `task-generator` skill to create the base task file at `tasks/` (this ensures the correct template with `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers). After the task file is generated, open it and append the following telegram-specific sections after the `## Goal` block and before `## Local TODOs`:

     ```markdown
     **Msg ID:** {NNN}

     ## Telegram Discussion Context

     **Sender:** {sender}

     **Original Message (Persian):**
     {persian_text}

     **Translation:**
     {translated_text}

     ## Codebase Correlation

     {codebase_analysis}
     ```

   - **GitHub Issue:** Run:
     `gh issue create --title "[Sync] Generated Title" --label "bug|enhancement|improvement" --body "Detailed Body with Crawled Discussion"`
     Extract the GitHub issue number from the output URL.
   - **State Save:** Update `telegram-sync.json` (append to `processed_ids`, update `last_processed_message_id`, add/update `sync_registry` entry with `gh_issue` number).
3. **Non-actionable messages:** All seen messages with IDs between `last_processed_message_id` and max candidate ID that do NOT have target hashtags must also be added to `processed_ids` to prevent re-fetching.

### Phase 4: Closing the Loop (Completion Telegram Reply)

1. When a task file inside `tasks/` is marked as completed or successfully approved by the Code Reviewer:
2. Read `telegram-sync.json` to check if the completed task file path exists in `sync_registry`.
3. If a match is found:
   - Extract the corresponding Telegram `msg_id` from the registry map.
   - Call **`telegram_reply_to_message`** with `chat_id` from config, `message_id` = the original `msg_id` (to reply directly in the correct thread/topic), the notification text, and `account` if set. Do **NOT** use `telegram_send_message` — it sends to the General topic instead of the correct thread.
   - **Notification Template:**
     _"The bug/feature reported in this thread has been successfully resolved and committed under Local Task XX (GitHub Issue #YY). Thank you!"_
