---
created_at: '2026-10-21T18:38:48.542510+00:00'
status: active
tags: []
updated_at: '2026-10-21T18:38:48.542540+00:00'
---

# Telegram Message Formatting Contract (Manager rule, 2026-10-21)

Every message sent through the Telegram MCP must be pretty, clean, and formatted per the
contract in `docs/telegram-message-formatting.md` and the `telegram-message-format` skill.
The rules were proven empirically against the live server on 2026-10-21.

## Binding rules

1. Always `parse_mode: "HTML"`. Markdown mode consumes triple-backtick fences and inline
   backticks without creating entities, and leaves `*bold*` as literal asterisks.
2. Escape `&` -> `&amp;`, `<` -> `&lt;`, `>` -> `&gt;` inside `<pre>` and `<code>`.
   One raw angle bracket aborts the whole message.
3. Safe elements only: `<b>`, `<i>`, `<u>`, `<code>`, `<pre>`, `<a>`.
4. No triple-backtick fences, no `*emphasis*` anywhere in a Telegram message.
5. Persian text without U+200C ZWNJ — use a normal space where the half-space belongs.
   ZWNJ is lost on the read path of every message.
6. Hard cap is 4096 characters; over it the server returns an opaque `GEN-ERR-184`
   (not a transient error — never retry). Plan on ~3800 chars and split longer payloads
   into parts, each a reply to the same parent id.
7. `send_message` has NO `topic_id` and lands in General. Post into a topic with
   `reply_to_message` anchored to a message already inside that topic. `send_file` and
   `send_album` do accept `topic_id`.
8. `get_history` resolves entities to plain text, so a read-back text diff cannot prove
   formatting was applied; use the `&lt;`/`&gt;` round-trip as the check.
9. Delete every probe message after reading it back; message ids are never reused.

## Where the rules live

- Skill (load before any send): `skill-templates/telegram-message-format/SKILL.md`
- Full evidence doc: `docs/telegram-message-formatting.md`
- Installed globally: `~/.config/opencode/skills/telegram-message-format/SKILL.md`
