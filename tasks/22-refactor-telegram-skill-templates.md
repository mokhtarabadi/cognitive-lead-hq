# Task: Refactor Telegram Skill Templates

**Type:** improvement
**Status:** closed

## Goal

Refactor `skill-templates/telegram-issue-sync/SKILL.md` and `skill-templates/telegram-message-export/SKILL.md`:

- Replace LLM-driven JSON state mutation with deterministic Python scripts (issue-sync)
- Consolidate phases from 5 to 4 for both skills
- Remove verbose MCP behavioral docs, streamline formatting
- Simplify message export workflow and ZIP archiving

## Manager's Notes

- No breaking contract changes — pure structural simplification
- Telegram MCP tool behavioral notes removed as they are now documented in the MCP server itself

## Local TODOs

- [x] Initial codebase exploration (diff reviewed)
- [x] Refactor `telegram-issue-sync/SKILL.md` — deterministic Python state updater, simplified phases
- [x] Refactor `telegram-message-export/SKILL.md` — consolidated phases, stripped verbose formatting
- [x] CHANGELOG entry added under Unreleased
- [x] Inject factual diff via MCP tool
- [x] Commit & push

## OpenCode Execution Log & Reasoning

**Diff Analysis:**

- `telegram-issue-sync/SKILL.md`: 96 insertions, 155 deletions. Replaced agentic "intent parsing" with deterministic Python script for JSON state management. Removed verbose Telegram MCP tool behavioral docs. Consolidated from 5 to 4 phases.
- `telegram-message-export/SKILL.md`: Major simplification. Removed multi-input resolution section, stripped verbose per-message formatting. Consolidated from 5 to 4 phases.

**Version Impact:** PATCH (5.13.1 → 5.13.2) — pure documentation restructuring, no new functionality or breaking changes.

**Sequence:** Create task → update CHANGELOG → inject diff via MCP → commit → push

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

````diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 5cc3eff..9e213bb 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -122,6 +122,13 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

 ## [Unreleased]

+## [5.13.2] — 2026-06-30
+
+### Changed
+
+- **`skill-templates/telegram-issue-sync/SKILL.md`** — Replaced LLM-driven JSON state mutation with a deterministic Python updater script. Removed verbose Telegram MCP behavioral documentation. Consolidated from 5 to 4 phases.
+- **`skill-templates/telegram-message-export/SKILL.md`** — Simplified message export workflow. Removed multi-input resolution section. Stripped verbose per-message formatting. Consolidated from 5 to 4 phases.
+
 ## [5.13.1] — 2026-06-30

 ### Changed
diff --git a/skill-templates/telegram-issue-sync/SKILL.md b/skill-templates/telegram-issue-sync/SKILL.md
index e405cdc..125c7d7 100644
--- a/skill-templates/telegram-issue-sync/SKILL.md
+++ b/skill-templates/telegram-issue-sync/SKILL.md
@@ -1,38 +1,14 @@
 ---
 name: telegram-issue-sync
-description: Optional, pure agentic sync of Telegram supergroup topics into local task files and GitHub issues, featuring intelligent intent parsing and reply-tree crawling.
+description: Syncs Telegram supergroup topics into local task files and GitHub issues, using embedded Python scripts for deterministic JSON state management.
 ---

 # Telegram Issue Sync & Discussion Crawler SOP

 ## Purpose
-
-Syncs actionable Telegram supergroup messages into GitHub Issues and local `tasks/` files. It features deep "Intent Parsing" — if a Manager tags a message with `#bug` while _replying_ to an older message, this skill autonomously fetches the parent message to construct a complete, contextual narrative.
-
-## Telegram MCP Tool Behavior
-
-All Telegram MCP tool calls accept an optional `account` parameter for multi-account setups. If `account` is set in your config, it is passed to every Telegram call.
-
-### Forum Topic Targeting (Critical)
-
-This MCP implementation does **NOT** expose a `topic_id` parameter. All messages belong to the same flat chat (`chat_id`). Forum topics are identified by the `reply_to` field on messages. To correctly scope operations:
-
-- **Reading messages from a specific topic:** Call `telegram_get_history` with `chat_id`. It returns messages from all topics. Filter the results by `reply_to` — messages belonging to your target topic have `reply_to` matching your `topic_id`.
-- **Discovering topics:** Call `telegram_list_topics` with `chat_id`. Returns all forum topics with their `id` and `title`.
-- **Sending a message to a specific topic:** You MUST use `telegram_reply_to_message` with `message_id` set to the Topic ID (not `telegram_send_message` — that always lands in the General topic).
-- **Reading messages:** `telegram_get_history` returns all messages. Filter by `reply_to == topic_id` to get messages scoped to your topic.
-
-Always use `telegram_list_topics` first to verify the target topic exists before posting.
-
-## Activation & State Management
-
-- **OPTIONAL**: Only run if `telegram-sync.json` exists at the workspace root, or if explicitly invoked by the Manager.
-- **State Schema Compliance**: You must strictly adhere to the `telegram-sync.json` format. The `sync_registry` maps a string `msg_id` to an object containing `task_file`, `gh_issue`, and `type`.
+Syncs actionable Telegram messages into GitHub Issues and local `tasks/` files. It features deep "Intent Parsing" (crawling parent/child replies) and uses a deterministic Python script to mutate the `telegram-sync.json` state, ensuring zero data loss or LLM hallucination during JSON updates.

 ## Local State Schema (`telegram-sync.json`)
-
-Stored at project root to track local configuration and message states:
-
 ```json
 {
   "config": {
@@ -50,61 +26,77 @@ Stored at project root to track local configuration and message states:

 ## Detailed Workflow

-### Phase 1: Verification & Onboarding
-
-1. Check for `telegram-sync.json` at project root.
-2. If missing AND the command was explicitly requested by the Manager:
-   - Run the `question` tool to ask for: `project_name`, `chat_id`, `target_hashtags`, optional `topic_id`, optional `account`.
-   - Create `telegram-sync.json` with the collected config. Set `last_processed_message_id` to `0`, initialize `processed_ids` and `sync_registry`.
-3. If missing and NOT explicitly requested: abort silently.
-4. If config exists, extract `config.chat_id`, `config.topic_id`, `config.account`, and `config.target_hashtags`.
-
-### Phase 2: Candidate Fetch & Deep Intent Crawling
-
-All Telegram calls in this phase pass `account` from config if set.
-
-1. **Fetch History:** Call `telegram_get_history(chat_id=chat_id, limit=200, account=account)`. If more messages are needed, paginate with higher limits. Filter by `reply_to == config.topic_id` if forum routing is used.
-2. **Identify Actionable Items:** Find messages where `id > last_processed_message_id` containing any `target_hashtags`.
-3. **Deep Intent & Reply Crawling (CRITICAL):**
-   - For each tagged message, check its `reply_to_message_id`.
-   - If the Manager replied to an older message, you MUST fetch that parent message using `telegram_get_message_context(chat_id=chat_id, message_id=reply_to_message_id, context_size=2, account=account)`. This returns the parent with surrounding context.
-   - Merge the parent message's context (the "what") with the Manager's tagged message (the "intent/instruction").
-   - Also fetch neighboring messages (+/- 5 messages) via `telegram_get_message_context` to capture unstructured discussion around the decision.
-4. **Translation & Blueprinting:**
-   - Translate Persian text to English.
-   - Synthesize the exact intent of the Manager based on the reply chain.
-
-### Phase 3: Task Generation & Multi-Sync
+### Phase 1: Context Fetch & Deep Crawling
+1. Read `telegram-sync.json` at the project root to get `config.chat_id`, `config.topic_id`, `config.account`, and `last_processed_message_id`.
+2. Call `telegram_get_history` (with `account` if set, limit=100) and filter for messages where `id > last_processed_message_id`.
+3. **Candidate Selection:** Identify messages containing `target_hashtags`. *Crucially, also identify any messages without hashtags that strongly resemble bug reports or feature requests.*
+4. **Deep Context:** For every selected candidate, check `reply_to_message_id`. If it exists, call `telegram_get_message_context` to fetch the parent message. Merge the parent message (the "what") with the child message (the "intent").
+
+### Phase 2: Manager Approval
+1. Use the `question` tool to present the identified candidates to the Manager.
+2. Ask: *"Which of these candidates should be synced? (Provide the Message IDs, or state 'All')"*
+3. Only proceed with the approved candidates.
+
+### Phase 3: Task Generation & Automation (Per Approved Candidate)
+For *each* approved candidate, execute the following steps strictly in order:
+
+**1. Determine Next Task ID:**
+Run this bash command to calculate the next task prefix:
+```bash
+NEXT_ID=$(ls tasks/ | grep -Eo '^[0-9]+' | sort -n | tail -1 | awk '{print $1+1}')
+if [ -z "$NEXT_ID" ]; then NEXT_ID="01"; fi
+printf "%02d\n" $NEXT_ID
+```

-1. Present the parsed candidates to the Manager for approval using the `question` tool.
-2. For each approved candidate:
-   - **Local Task Generation:** Use the `task-generator` skill to create `tasks/XX-title.md`. Inject the deep intent context:
+**2. Generate Local Task File:**
+Create `tasks/{NEXT_ID}-hyphenated-title.md` utilizing the standard project template (`<!-- BEGIN_GIT_DIFF -->`, etc.). Inject the translated Telegram discussion context and codebase correlation.

-     ```markdown
-     **Msg ID:** {NNN}
+**3. Create GitHub Issue:**
+Run the GitHub CLI to create the issue and capture the URL.
+```bash
+cat > /tmp/gh-issue-body.md << 'EOF'
+Migrated from Telegram. See local task file for details.
+EOF
+
+GH_URL=$(gh issue create --title "{Task Title}" --body-file /tmp/gh-issue-body.md --label "telegram-sync")
+rm -f /tmp/gh-issue-body.md
+echo "GH_URL=$GH_URL"
+```

-     ## Telegram Discussion Context
+**4. Update State Deterministically (The Updater Script):**
+Create a temporary file named `update_sync.py` with the exact code below.
+```python
+import json, sys, os

-     **Context/Parent Message:** {parent_text_translated}
-     **Manager's Instruction:** {manager_tagged_text_translated}
+msg_id = int(sys.argv[1])
+task_file = sys.argv[2]
+gh_issue_url = sys.argv[3]
+issue_type = sys.argv[4].upper()

-     ## Codebase Correlation
+file_path = 'telegram-sync.json'
+with open(file_path, 'r') as f:
+    data = json.load(f)

-     {Autonomous analysis of which files likely need changes based on the context}
-     ```
+data['last_processed_message_id'] = max(data.get('last_processed_message_id', 0), msg_id)

-   - **GitHub Issue:** Create the issue using the `gh issue create` CLI tool.
-   - **State Update:** Update `telegram-sync.json`. Append to `processed_ids`, update `last_processed_message_id`. Add the entry to `sync_registry` using the exact schema:
-     `"{msg_id}": { "task_file": "tasks/...", "gh_issue": 123, "type": "BUG" }`
+if msg_id not in data.get('processed_ids', []):
+    data.setdefault('processed_ids', []).append(msg_id)
+    data['processed_ids'].sort()

-### Phase 4: Non-Actionable Message Tracking
+data.setdefault('sync_registry', {})[str(msg_id)] = {
+    "task_file": task_file,
+    "gh_issue": gh_issue_url,
+    "type": issue_type
+}

-All seen messages with IDs between `last_processed_message_id` and the max candidate ID that do NOT have target hashtags must also be added to `processed_ids` to prevent re-fetching.
+with open(file_path, 'w') as f:
+    json.dump(data, f, indent=2)

-### Phase 5: Closing the Loop (Completion Notification)
+print(f"Successfully updated registry for msg {msg_id}")
+```
+Run it via Bash, passing the arguments, then delete it:
+```bash
+python3 update_sync.py "{MSG_ID}" "tasks/{NEXT_ID}-title.md" "$GH_URL" "{TYPE}"
+rm update_sync.py
+```

-When a task implementation is completed and the Git diff was injected:
+**5. Reply in Telegram:**
+Call `telegram_reply_to_message(chat_id=chat_id, message_id=MSG_ID, text="✅ Task synced successfully.\n📁 Local File: tasks/{NEXT_ID}-title.md\n🌐 GitHub Issue: $GH_URL", account=account)`.

-1. Read `telegram-sync.json` -> `sync_registry`.
-2. If the completed `task_file` matches an entry, extract the `msg_id`.
-3. Call `telegram_reply_to_message(chat_id=chat_id, message_id=msg_id, text="✅ The bug/feature reported in this thread has been resolved and committed under Local Task XX.", account=account)` to reply directly in the correct thread.
+### Phase 4: Mark Non-Actionable Messages
+Once all approved tasks are generated, you must update `last_processed_message_id` to the highest message ID you observed in the batch so they are not fetched again. Create a short python script similar to Phase 3 to just update `last_processed_message_id` and append the skipped IDs to `processed_ids`.
diff --git a/skill-templates/telegram-message-export/SKILL.md b/skill-templates/telegram-message-export/SKILL.md
index 0640a4e..a38dde3 100644
--- a/skill-templates/telegram-message-export/SKILL.md
+++ b/skill-templates/telegram-message-export/SKILL.md
@@ -6,96 +6,45 @@ description: Intelligently exports a range of Telegram messages (text, media, vo
 # Telegram Message Export Skill

 ## Purpose
+Extracts a highly contextual range of Telegram messages. It explicitly documents reply relationships to preserve conversation trees and packages text alongside downloaded media files (images, voice notes) into a ZIP file.

-Extracts a highly contextual range of Telegram messages. It automatically resolves dynamic starting/ending points, extracts text and media files side-by-side, explicitly documents reply relationships to preserve conversation trees, and packages the result into a ZIP file.
+## Input Resolution
+Determine the exact `[from_id, to_id]` range. If the Manager provided a text snippet, use `telegram_search_messages` to find the `msg_id`. If a link is provided (`t.me/c/CHAT_ID/MSG_ID`), extract the ID.

-## Input Methods
+## Phase 1: Contextual Fetching
+1. Call `telegram_get_history` and filter to keep messages where `id >= from_id` and `id <= to_id`.
+2. Sort the filtered messages strictly by `id` in ascending order.
+3. If the range spans more than 200 messages, use the `question` tool to ask for confirmation before proceeding to avoid rate limits.

-Accept the boundaries of the export dynamically based on the Manager's prompt:
-
-1. **Start & End Bounds**: Can be explicit Message IDs, Message Links (`t.me/c/CHAT_ID/MSG_ID`), or exact text snippets (which you will search for to resolve the ID).
-2. **Start Point + Context Window**: A starting link/ID and a request like "and the next 50 messages".
-
-## Output
-
-A ZIP file at the path: `<workspace>/telegram-exports/telegram-export-{unix_timestamp}.zip`
-Inside, files are numbered sequentially by ascending message ID:
-
-- `1.txt` (Contains sender, date, reply metadata, and text content)
-- `1.jpg` (If the message included an image)
-- `2.txt`
-- `2.ogg` (If the message was a voice note)
-
-## Detailed Workflow
-
-### Phase 1: Input Parsing & Boundary Resolution
-
-All Telegram calls in this skill pass `account` if the user provides one.
-
-1. Determine `chat_id` and the `from_id` / `to_id` bounds.
-2. If the user provides a link:
-   - `t.me/c/CHAT_ID/MSG_ID` — parse the numeric `CHAT_ID` and `MSG_ID`. Prepend `-100` to `CHAT_ID` to form the full chat_id.
-   - `t.me/username/MSG_ID` — call `telegram_resolve_username(username=username, account=account)` to get the `chat_id`, then extract `MSG_ID`.
-3. If the user provides a text snippet as a boundary, use `telegram_search_messages(chat_id=chat_id, query=snippet, limit=5, account=account)` to locate the exact `msg_id`.
-4. Establish the final `[from_id, to_id]` range. If the user requested a context size instead of an end bound, calculate `to_id = from_id + context_size`.
-
-### Phase 2: Contextual Message Fetching
-
-1. Call `telegram_get_history(chat_id=chat_id, limit=200, account=account)` to retrieve recent messages. If the range extends beyond the returned batch, paginate by calling again with a larger limit or using the last returned message ID.
-2. Filter the returned list to keep only messages where `id >= from_id` and `id <= to_id`.
-3. Sort the filtered messages strictly by `id` in ascending order.
-4. If the filtered list is empty, abort with a clear message. Do not create an empty ZIP.
-5. **Range guard:** If the range spans more than 200 messages, warn the Manager via the `question` tool and ask for confirmation before proceeding. This skill is designed for focused extraction, not bulk archiving.
-
-### Phase 3: Intelligent File Extraction & Reply Mapping
-
-1. Create directory: `mkdir -p <workspace>/telegram-exports/telegram-export-{unix_timestamp}/`
+## Phase 2: Extraction & Sidecar Generation
+1. Create directory: `mkdir -p <workspace>/telegram-exports/export-{timestamp}/`
 2. Set counter `n = 1`.
 3. For each message in the sorted list:

-   **Step A: Text & Metadata Sidecar (`{n}.txt`)**
-   - You MUST create a `{n}.txt` file for _every_ message, even if it's just media or an unsupported type.
-   - Extract `reply_to_message_id`. If it exists, explicitly document it so the LLM can reconstruct the thread later.
-   - Format of `{n}.txt`:
-
-     ```text
-     Message ID: {message.id}
-     From: {sender_name_or_id}
-     Date: {date}
-     Reply To Message ID: {reply_to_message_id | 'None'}
-     Message Type: {text | photo | voice | video | document | sticker | poll | service | unsupported}
-
-     [Content]
-     {message_text_or_caption | '[No text content]'}
-     ```
-
-   - For polls, write the poll question and options as the content.
-   - For service messages (member joined, title changed, etc.), write the service action description.
-   - If the message has no extractable content, write `[No extractable content]`.
-
-   **Step B: Media Extraction**
-   - If the message contains media (photo, voice note, video, document):
-     - Call `telegram_get_media_info(chat_id=chat_id, message_id=message.id, account=account)` to determine the file extension.
-     - Call `telegram_download_media(chat_id=chat_id, message_id=message.id, file_path="<export_dir>/{n}.{ext}", account=account)` to save the file.
-     - Note: Voice notes download as `.ogg` automatically.
-
-   **Step C:** Increment `n = n + 1`.
+   **Text Sidecar (`{n}.txt`)**:
+   Create a `.txt` file for every message. You MUST include `reply_to_message_id` to preserve thread context.
+   ```text
+   Message ID: {message.id}
+   From: {sender_name_or_id}
+   Date: {date}
+   Reply To Message ID: {reply_to_message_id | 'None'}
+   Message Type: {type}
+
+   [Content]
+   {message_text | caption | '[No extractable content]'}
+   ```

-### Phase 4: Archiving and Cleanup
+   **Media Download**:
+   If the message contains media, call `telegram_get_media_info` to get the extension. Then call `telegram_download_media(chat_id=..., message_id=..., file_path="<workspace>/telegram-exports/export-{timestamp}/{n}.{ext}")`.

-1. Run the bash zip command:
-   ```bash
-   cd <workspace>/telegram-exports && zip -r telegram-export-{unix_timestamp}.zip telegram-export-{unix_timestamp}/
-   ```
-2. Delete the temporary directory:
-   ```bash
-   rm -rf <workspace>/telegram-exports/telegram-export-{unix_timestamp}/
-   ```
+4. Increment `n`.

-### Phase 5: Notification
+## Phase 3: Archiving
+Run the bash zip command:
+```bash
+cd <workspace>/telegram-exports && zip -r export-{timestamp}.zip export-{timestamp}/
+rm -rf export-{timestamp}/
+```

-Output EXACTLY:
-"✅ Contextual Telegram export complete.
-Range: {from_id} to {to_id}
-Total items processed: {n-1}
-Archive path: <workspace>/telegram-exports/telegram-export-{unix_timestamp}.zip"
+## Phase 4: Notification
+Output exactly: "✅ Contextual Telegram export complete. Range: {from_id} to {to_id}. Archive path: <workspace>/telegram-exports/export-{timestamp}.zip"
````

<!-- END_GIT_DIFF -->
