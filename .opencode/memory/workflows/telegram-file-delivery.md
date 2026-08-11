---
created_at: '2026-08-10T20:57:01.752264+00:00'
status: active
tags: []
updated_at: '2026-08-10T20:57:01.752284+00:00'
---

# Sending Task Files to Telegram — MANAGER PREFERENCE (updated 2026-08-10, overrides previous version)

**Trigger:** Manager says "send me the task file" / "send the file to Telegram" / "بفرست توی تلگرام".

## THE RULE (Manager's explicit preference — v2)

When the Manager asks to send a task file to Telegram, send the **WHOLE file AS A FILE** (real attachment, .md document) to the **General topic** of the Personal Projects supergroup. Do NOT chunk the content into text replies, do NOT try to target a specific forum topic. The Manager explicitly confirmed General topic is fine.

## Procedure (verified working)

1. `telegram_send_file(chat_id=-1003993323129, file_path="<abs path to task file>", caption="📄 <relative path> — <short title>", account="personal")`.
2. The file lands in the **General topic** (send_file has no reply support → General is the default for forum supergroups).
3. Verify: `telegram_get_messages(chat_id, page=1)` — the new file message should be at the top, NOT carrying reply_to 425/426.

## What was tried and REJECTED (do not repeat)

- Sending the file content as chunked text replies into the specific topic (messages 428–432, reply to topic root 425) — Manager did NOT like it ("خوشم نیومد"), messages were deleted. The topic-precise method is abandoned; never chunk a file into text messages.
- Note: topic "Cognitive Hq" (id 425) is the project's own topic; if the Manager ever asks explicitly for a topic, say the file attachment goes to General and ask for confirmation instead of chunking.

## Key IDs

- Personal Projects supergroup: `-1003993323129` (use `account="personal"`)
- General topic: id 1 (default for send_file)
- Topic "Cognitive Hq" (cognitive-lead-hq project): id 425

## Limitation

`send_file` in telegram-mcp has NO `reply_to`/topic param (verified in `/home/mohammad/telegram-mcp/telegram_mcp/tools/media.py`). File attachments can only reach the General topic. If in-topic attachments ever become required, the MCP server itself must be extended.
