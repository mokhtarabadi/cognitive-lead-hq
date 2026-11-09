---
name: telegram-suite
description: Unified Telegram skills — HTML message formatting, contextual export to ZIP, and issue sync to tasks/GitHub.
---

# Telegram Suite Meta Skill (slim index)

Meta skill combining **telegram-message-format** (HTML formatting contract), **telegram-message-export** (contextual range export), and **telegram-issue-sync** (topic sync to tasks/GitHub). All outgoing messages follow Part 1. Full bodies are verbatim in `templates/` — read only the part you need.

---

## Critical Rules (no read needed)

- **Parse mode:** always `parse_mode: "HTML"`; `<b>`/`<code>`/`<pre>` only; no ` ``` ` or `*emphasis*`; escape `&` `<` `>` inside `<code>`/`<pre>`.
- **Persian:** no U+200C ZWNJ — use normal space. **Length:** ≤ ~3800 chars/message (hard cap 4096); split with numbered parts anchored to the same parent.
- **Topics:** `send_message` has no `topic_id` (lands in General). Post into a topic via `reply_to_message` anchored to a message already inside that topic.
- **Export:** `get_history` range → sorted sidecars with `Reply To Message ID` → `Max` (single `get_media_info` + `download_media` per media) → `zip -r export.zip` → delete dir. No media = no zip.
- **Sync:** verbatim `RAW_TEXT` (no summarize) + `## Original Message` + `## English Translation` + `## Refactored Prompt` (prompt-refactor 5 blocks) + codebase correlation + `AI_OPINION` in `kanban-lifecycle` unified template. State via native edits only; never helper scripts. Approval: `question` tool when available, else capability-block relay.

## When to Read Templates

- **Send, reply, edit, caption, or verify a message** → `templates/01-format.md` (9 Rules + checklists + defect table).
- **Export a range to ZIP** → `templates/02-export.md`.
- **Sync topics → tasks/GitHub** → `templates/03-sync.md`.

Templates are authoritative; this index only summarizes. Registry: `prompts/fragments/07-agent_skills_registry.md`.
