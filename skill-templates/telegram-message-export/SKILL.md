---
name: telegram-message-export
description: Exports a range of Telegram messages (text, images, voice notes) into a numbered folder and packs them into a ZIP archive.
---

# Telegram Message Export Skill

## Purpose

Extracts a consecutive range of Telegram messages from a chat — text, images, and voice notes — saves them to disk in a numbered folder, and bundles everything into a single ZIP file.

## Input Methods (choose one)

| Method | Parameters | Description |
|---|---|---|
| **Message ID range** | `chat_id`, `from_id`, `to_id` | Export messages with IDs between `from_id` and `to_id` (inclusive) |
| **Message link** | `link` | Parse a `t.me/c/CHAT_ID/MSG_ID` or `t.me/username/MSG_ID` link, then export `MSG_ID ± context_size` messages |
| **Text search** | `chat_id`, `search_query` | Search for messages matching the query, export all results |

## Output

A ZIP file at the path: `<workspace>/telegram-exports/telegram-export-{unix_timestamp}.zip`

Inside the ZIP, files are numbered sequentially in ascending message ID order:

- `1.txt` — text message (content + sender + date header)
- `2.jpeg` / `2.png` — downloaded photo
- `3.ogg` — downloaded voice note
- `4.txt` — another text message
- etc.

## Detailed Workflow

### Phase 1: Input Parsing

**Method A — Message ID range:**
1. Accept `chat_id`, `from_id` (int), `to_id` (int).
2. Validate that `from_id <= to_id` and both are positive integers.
3. Store as the target range.

**Method B — Message link:**
1. Accept a Telegram message link:
   - `https://t.me/c/CHAT_ID/MSG_ID` — extract `chat_id` and `msg_id`. Prepend `-100` to `chat_id` if it is a pure numeric string (standard Telegram supergroup encoding).
   - `https://t.me/username/MSG_ID` — call `telegram_resolve_username(username)` to get the `chat_id`, then extract `msg_id`.
2. Ask the user for `context_size` (number of messages before and after), default 10.
3. Range = `[msg_id - context_size, msg_id + context_size]`, clamped to `>= 1`.

**Method C — Text search:**
1. Accept `chat_id` and `search_query` (string).
2. Call `telegram_search_messages(chat_id=chat_id, query=search_query, limit=100)`.
3. Use the returned message list directly as the export set (no ID range filtering needed).

### Phase 2: Message Fetching

1. Call `telegram_get_history(chat_id=chat_id, limit=200)` to retrieve recent messages. If the returned list does not cover the requested range, call it again with a larger limit or use pagination.
2. Filter the list to keep only messages where `id >= from_id` and `id <= to_id`.
3. Sort by `id` in ascending order.
4. If no messages match the range, abort with: "No messages found in the specified range."

### Phase 3: File Extraction

1. Create the export directory: `mkdir -p <workspace>/telegram-exports/telegram-export-{unix_timestamp}/`
2. Set a counter `n = 1`.
3. Iterate over each message in ascending order:

   **For text messages** (where `message` has a non-empty `text` field):
   - Write a file `{n}.txt` with the following format:
     ```
     From: {sender_name_or_id}
     Date: {date}
     Message ID: {id}

     {message_text}
     ```
   - Increment `n`.

   **For media messages** (photos, voice, video, document, sticker):
   - Call `telegram_get_media_info(chat_id=chat_id, message_id=message.id)` to determine the file extension.
   - Call `telegram_download_media(chat_id=chat_id, message_id=message.id, file_path="<export_dir>/{n}.{ext}")`.
   - If the message also has text content, also write `{n}.txt` with the text (same `n` value for companion text).
   - Increment `n`.

   **For unsupported message types** (poll, game, etc.):
   - Write `{n}.txt` with content: "Unsupported message type: {type}"
   - Increment `n`.

### Phase 4: ZIP Packaging

1. After all files are extracted, run:
   ```
   cd <workspace>/telegram-exports && zip -r telegram-export-{unix_timestamp}.zip telegram-export-{unix_timestamp}/
   ```
2. Remove the source directory:
   ```
   rm -rf <workspace>/telegram-exports/telegram-export-{unix_timestamp}/
   ```
3. Confirm the ZIP file exists at:
   `<workspace>/telegram-exports/telegram-export-{unix_timestamp}.zip`

### Phase 5: Summary

Output exactly:

```
✅ Telegram message export complete.
   Range: messages {from_id} to {to_id} in chat {chat_id}
   Total files: {n-1}
   Archive: <workspace>/telegram-exports/telegram-export-{unix_timestamp}.zip
```

## Edge Cases

- **Empty range:** Abort early with a clear message. Do not create an empty ZIP.
- **Mixed content (text + photo in one message):** The text sidecar file and the media file share the same number `{n}` (e.g., `5.txt` describes `5.jpeg`).
- **Voice notes:** Downloaded as `.ogg` via `telegram_download_media`. No special handling needed — the MCP tool saves the correct format.
- **Large ranges (>200 messages):** Instruct the user to narrow the range. The skill is designed for focused extraction, not bulk archiving.
