---
created_at: '2026-08-25T20:10:44.379873+00:00'
status: active
tags: []
updated_at: '2026-08-25T20:10:44.379901+00:00'
---

# Telegram Sync Workflow Constraints (Cognitive Lead HQ)

Established by Manager on 2026-08-25 after a mis-scoped sync cycle.

## Topic Scoping (MANDATORY)
- `telegram-sync.json` → `config.topic_id` (currently 458 = "Cognitive Lead" topic) defines the ONLY channel to sync for the project.
- NEVER fetch/scan group-wide history. Forum topics are reply threads: a message belongs to topic T if its `reply_to_message_id` chain terminates at T's root service message (`MessageActionTopicCreate`).
- For chat -1003993323129: root 458 = Cognitive Lead; root 455 = second topic; root 2 area = General. Messages replying directly to the root id are thread members.
- Sync confirmations MUST be posted as `telegram_reply_to_message` on the SOURCE message inside its own topic. NEVER post confirmations to General or as standalone messages.

## Flood-Wait Handling
- Bulk Telegram sends trigger `FloodWaitError` (~287s initial). Retrying before the window expires EXTENDS the penalty (observed 466s).
- Protocol: send one message → verify → wait ≥30–60s between sends; on FloodWaitError, sleep the FULL demanded duration + buffer before any retry.

## State File Semantics
- `last_processed_message_id` is a global watermark for the chat; after each cycle set it to the highest observed id and backfill `processed_ids` for the whole range so skipped messages are not refetched.
- `sync_registry[<msg_id>]` = {task_file, gh_issue, type}. Task files may later be archived — check `tasks/archive/` when the backlog path no longer exists.

## Kanban Reality Check (2026-08-25)
- `tasks/backlog|in-progress|qa` dirs can be absent after archiving sweeps — create them (`mkdir -p`) before `git mv`; `git mv` fails if destination dir does not exist.
