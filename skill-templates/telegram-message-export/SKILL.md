---
name: telegram-message-export
description: Intelligently exports a range of Telegram messages (text, media, voice notes) into a numbered folder, capturing reply hierarchies, and packing them into a ZIP archive.
---

# Telegram Message Export Skill

## Purpose

Extracts a highly contextual range of Telegram messages. It explicitly documents reply relationships to preserve conversation trees and packages text alongside downloaded media files (images, voice notes) into a ZIP file.

## Input Resolution

Determine the exact `[from_id, to_id]` range. If the Manager provided a text snippet, use `telegram_search_messages` to find the `msg_id`. If a link is provided (`t.me/c/CHAT_ID/MSG_ID`), extract the ID.

## Phase 1: Contextual Fetching

1. Call `telegram_get_history` and filter to keep messages where `id >= from_id` and `id <= to_id`.
2. Sort the filtered messages strictly by `id` in ascending order.
3. If the range spans more than 200 messages, use the `question` tool to ask for confirmation before proceeding to avoid rate limits.

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
