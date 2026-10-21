---
name: telegram-message-format
description: Formats every outgoing Telegram MCP message so it renders cleanly in Telegram. Use before any send, reply, edit, or caption through the Telegram MCP - covers parse mode, HTML escaping, length splitting, forum-topic targeting, Persian text, and read-back verification.
---

# Telegram Message Formatting SOP

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
