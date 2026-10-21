# Telegram MCP — Message Formatting Contract

> **Audience:** the Telegram MCP server maintainers, and every agent that sends a message through the Telegram MCP.
> **Purpose:** every rule below was proven empirically against the live server on 2026-10-21 by sending probe messages and reading them back. Nothing here is inferred from documentation.
> **Status:** the two safe patterns at the end work today on the current server; the "known defects" section is what we believe should be fixed upstream.
> **Operational twin:** [`skill-templates/telegram-message-format/SKILL.md`](../skill-templates/telegram-message-format/SKILL.md) — the agent-facing rulebook distilled from this document. Load it before any Telegram send.

---

## 0. Executive summary

| Concern                    | Verdict                                                       | Action for the server team                                  |
| -------------------------- | ------------------------------------------------------------- | ----------------------------------------------------------- |
| Message length             | Hard limit is **4096 chars**; 4097 fails with an opaque `GEN-ERR-184` | Return a descriptive error instead of a generic one   |
| Markdown ` ``` ` fences    | **Consumed** — the code block markers vanish                   | Fix the Markdown entity parser, or document HTML-only     |
| Markdown `*bold*`          | **Not applied** — asterisks survive as literal text            | Same                                                        |
| Markdown inline `` `code` `` | **Consumed** — backticks vanish                              | Same                                                        |
| HTML `<b> <code> <pre>`    | **Fully preserved**                                            | Keep as-is; recommend it as the default                     |
| HTML entities (`&lt;` `&gt;` `&amp;`) | **Decoded correctly**                              | Keep as-is                                                  |
| Persian ZWNJ (U+200C)       | **Lost on read** — affects every message, including ones the account owner typed on their own phone | Fix the read-path JSON encoding; until then, avoid ZWNJ in authored text |
| Forum topics                | `send_message` has **no `topic_id`**                           | Add `topic_id` to `send_message`                            |
| Deletion                    | `delete_message` works and is clean                            | Keep                                                        |

---

## 1. Message length

Proven by sending messages of exact known length to the Apex topic and reading back the result.

| Payload length | Result                                           |
| -------------- | ------------------------------------------------ |
| 4096 chars     | **sent successfully**                             |
| 4097 chars     | fails: `An error occurred (code: GEN-ERR-184)`    |
| 4200 chars     | fails: `An error occurred (code: GEN-ERR-184)`    |
| 4665 chars (a real report) | fails: `An error occurred (code: GEN-ERR-184)` |
| 3000 chars     | sent successfully                                 |

**Rules**

1. The limit is exactly **4096 characters**, matching Telegram's own `MESSAGE_MAX_LENGTH`. It is not a server-imposed cap.
2. `GEN-ERR-184` is returned for **any** over-length message, and it carries no indication that length was the cause. A caller that treats it as a transient/network error will retry forever. **The error should be specific**, e.g. `MESSAGE_TOO_LONG: 4665 > 4096`.
3. The counter should count **UTF-16 code units**, not bytes and not grapheme clusters — that is what Telegram counts. A message with many emoji or Persian/Arabic characters hits the limit well before its byte length suggests. (Empirically unverified here; stated because it is the Telegram-documented behavior and the difference is real for non-ASCII payloads.)
4. **Character budget for a report-style message:** plan on ~3800 characters per message and split anything longer into parts, each anchored as a reply to the same parent message id so the thread stays readable.

---

## 2. Parse mode: what actually happens

All three findings were produced by sending a probe, reading the message back, and diffing what was sent against what came out. The probes were deleted afterwards.

### 2.1 `parse_mode: "Markdown"` — fences and backticks are consumed

Probe sent:

```
PROBE-A ```bash
curl -X POST https://x/y
``` می‌کند
```

Read back:

```
PROBE-A bash
curl -X POST https://x/y
 می‌کند
```

The ` ``` ` markers are **gone**. What remains is the literal `bash` language hint followed by the code body, indistinguishable from ordinary paragraph text. A second probe confirms the same for the inline form — `INLINECODE` came back without its backticks.

A separate probe shows `*bold*` is **not** interpreted at all: `*BOLDTEST*` round-trips with its asterisks intact, so the reader sees literal asterisks rather than bold text.

**Conclusion:** in Markdown mode this server strips fence/backtick markers but does not build the corresponding Telegram entities. The code block is therefore destroyed — the content survives, its formatting does not. Do not use Markdown mode for anything containing code.

### 2.2 `parse_mode: "HTML"` — fully preserved

Probe sent:

```html
<b>BOLD</b> inline <code>IDENT</code>

<pre>curl -u '&lt;admin&gt;:&lt;pass&gt;' \
  --data 'x=1'</pre>

<pre>SELECT 1;</pre>

tail &amp; more
```

Read back (tags and entities resolved, structure intact):

```
BOLD inline IDENT

curl -u '<admin>:<pass>' \
  --data 'x=1'

SELECT 1;

tail & more
```

Every element behaved correctly:

- `<b>` → bold
- `<code>` → inline monospace
- `<pre>` → block code, with the block boundaries preserved
- `&lt;` `&gt;` `&amp;` → decoded to `<` `>` `&`

The `&lt;`/`&gt;` round-trip is the important one: it proves the HTML was genuinely parsed into Telegram entities rather than being passed through and merely displayed without tags. **This is the mode to use.**

### 2.3 Recommended defaults

- **Use `parse_mode: "HTML"` for any message containing code, identifiers, or emphasis.**
- Inside `<pre>`, escape `&` as `&amp;`, `<` as `&lt;`, `>` as `&gt;`.
- If a caller has no parse mode available, the safe fallback is to send plain text and accept that structure must be expressed with plain-text conventions (indentation, separators) rather than markup.

---

## 3. Persian text: the ZWNJ problem

**U+200C ZERO WIDTH NON-JOINER is lost.** This is not a quirk of how the text was authored — it applies to every message read back through this server, including messages the Telegram account owner typed by hand on a phone (Persian keyboards insert ZWNJ automatically).

Probe with ASCII sentinels around the ZWNJ, so nothing depends on the surrounding Persian:

```
sent:      SENTINEL_A‌SENTINEL_B
read back: SENTINEL_ASENTINEL_B
```

The ZWNJ is absent from the returned payload. The same holds for `send_message`, so it is not specific to one tool.

**Why this matters for Persian:** ZWNJ is what keeps a suffix attached to its prefix word. Without it, `می‌کند` degrades to `میکند`, and compounds like `قابل‌تسویه` or `نمی‌فهمم` lose the half-space that distinguishes one word from two. The text stays readable to a Persian reader, but it is no longer typographically correct Persian.

**Two distinct possibilities, and the server team should determine which applies:**

1. **Read-path loss (most likely).** The characters are stored correctly in Telegram and only vanish when the server serializes messages back to the client. If so, the delivered message on a phone is fine and only programmatic readers are affected — but any agent that reads a message and then re-sends it (quoting, replying, editing) will silently corrupt the Persian.
2. **Write-path loss.** The characters are stripped before the message is sent, so the delivered message itself is wrong.

Either way there is a **safe authoring rule that works under both hypotheses:** write Persian without ZWNJ, using a regular space where the half-space belongs, and never rely on a ZWNJ surviving a round-trip.

**Action for the server team:** check the JSON encoding on the message-read path. A common cause is the response being serialized with `ensure_ascii=True` plus a normalization step that drops characters in the Unicode "format" category (U+200C is `Cf`, i.e. *Format*, and many normalizers strip `Cf` characters along with the zero-width space U+200B and the BOM). The fix is to preserve `Cf` characters, or at minimum to preserve U+200C explicitly.

---

## 4. Forum topics: `send_message` cannot target a topic

`send_message` accepts `chat_id`, `message`, `parse_mode`, `format_date`, `custom_emojis` and `account` — there is **no `topic_id` parameter**. `send_album` and `send_file` do have `topic_id`.

Consequence: a message sent with `send_message` to a supergroup that has forum topics enabled lands in **General**, not in the intended topic.

The workaround that works today: use `reply_to_message` with the id of an existing message **inside** the target topic. A reply inherits the topic of its parent. Every message in the Apex topic during this investigation was posted this way.

**Action for the server team:** add `topic_id` to `send_message`, matching the signature `send_album` and `send_file` already use.

---

## 5. Deleting probe messages

`delete_message(chat_id, message_id, account)` removes a message cleanly and immediately, and the message id is not reused. This is what makes empirical probing safe: every probe in this investigation was deleted after being read back, leaving the group with only the intended messages.

`delete_messages_bulk` and `delete_chat_history` also exist. Note that deleting a message does **not** renumber the remaining ones, and later messages keep their original ids — so a client that has cached message ids must treat deletion as "this id may no longer resolve" rather than as a renumbering.

---

## 6. Reading messages back

Two read tools exist and they behave differently:

- `get_history(chat_id, limit, account, topic_id)` — returns a JSON string of `{results: [{id, sender, date, text, reply_to, ...}]}`. The `text` field is the **plain text with entities already resolved** — formatting is not visible in the response, only in the Telegram client. `topic_id` filters to one topic.
- `get_messages(chat_id, page, page_size, account)` — returns a pre-rendered human-readable listing, one line per message, with the message text inline. `page`/`page_size` pagination, **no topic filter**. Useful for a quick "what are the latest messages" check.
- `get_message_context(chat_id, message_id, context_size, account)` — returns the message plus surrounding context.

**Practical note:** because `get_history` resolves entities into plain text, **a round-trip comparison cannot confirm that formatting was applied**. Proving that `<pre>` really became a Telegram code-block entity requires reading the message's `entities` array, which none of the current read tools expose. The most reliable available check is the `&lt;`/`&gt;` round-trip described in §2.2, which proves the HTML was parsed rather than passed through — and it is the check used throughout this document.

**Suggested addition:** expose the raw `entities` array on the message payload, so a client can verify that a code block or bold span was actually applied rather than trusting that it was.

---

## 7. Safe patterns to adopt today

### 7.1 A report with a code block (recommended)

```html
<b>Heading</b> and <code>inline_identifier</code>

<pre>curl -X POST "https://example.com/api" \
  --data 'key=value'</pre>

<b>Second heading</b>

<pre>SELECT id, state FROM trades WHERE id = 2069;</pre>

Notes with <code>snake_case_names</code> inline.
```

- `parse_mode: "HTML"`
- escape `&` `<` `>` inside `<pre>`
- keep each message under ~3800 characters
- anchor every part as a reply to the same parent message id

### 7.2 A short prose message

```
<b>Short heading</b>

Plain prose with <code>identifiers</code> and no markup dependency.
```

- `parse_mode: "HTML"`
- **write Persian without ZWNJ** — use a normal space where the half-space belongs
- keep it under ~3800 characters

### 7.3 Posting into a specific forum topic

```
reply_to_message(chat_id, message_id=<an id already inside the topic>, account, parse_mode="HTML", text=...)
```

---

## 8. Reproducing every finding

Each item below is a standalone, self-verifying probe. Run them against a scratch chat, read the result back, then delete the probe.

**A. Length boundary**

```js
// 4096 -> "Replied to message N."   4097 -> "GEN-ERR-184"
await reply_to_message({chat_id, message_id, account, text: "L" + "x".repeat(4095)});
await reply_to_message({chat_id, message_id, account, text: "L" + "x".repeat(4096)});
```

**B. Markdown fences are consumed**

```js
await reply_to_message({chat_id, message_id, account, parse_mode: "Markdown",
  text: "PROBE ```bash\ncurl -X POST https://x/y\n``` end"});
// read back -> the ``` markers are gone
```

**C. HTML is preserved**

```js
await reply_to_message({chat_id, message_id, account, parse_mode: "HTML",
  text: "<b>B</b> <code>C</code> <pre>x &lt; y</pre>"});
// read back -> "B C x < y" with the block intact
```

**D. ZWNJ is lost (read-path)**

```js
await reply_to_message({chat_id, message_id, account, text: "SENTINEL_A\u200cSENTINEL_B"});
// read back -> "SENTINEL_ASENTINEL_B"
```

**E. `send_message` ignores the topic**

```js
await send_message({chat_id, message: "TOPIC_PROBE", account});
// lands in General, not in the topic
```

**F. Cleanup**

```js
await delete_message({chat_id, message_id, account});
```

---

## 9. Defect list (for the server backlog)

1. **Over-length messages return `GEN-ERR-184`** with no length hint — indistinguishable from a transient error. Return a specific, actionable error.
2. **Markdown mode destroys code blocks** — fence markers are stripped without entities being created. Either implement the entity mapping properly or reject Markdown mode with a clear message pointing at HTML.
3. **Markdown `*bold*` is not applied** — asterisks survive as literal characters. Same fix as above.
4. **Persian ZWNJ is lost** on the read path (and possibly the write path). Preserve U+200C; do not strip Unicode `Cf` characters.
5. **`send_message` cannot target a forum topic** — add `topic_id`, matching `send_album` / `send_file`.
6. **Message `entities` are not exposed** on read — a client cannot verify that formatting was applied. Add the raw entities array to the message payload.
7. **Message length should be counted in UTF-16 code units** so the check matches Telegram's own limit, and the error should report the actual count versus the cap.

---

## 10. Authoring rules for agents (binding)

These are the rules an agent must follow when it authors a Telegram message. They restate the findings above in the form of an action list, and they are the source of the [`telegram-message-format` skill](../skill-templates/telegram-message-format/SKILL.md).

| # | Rule                                                                        | Why                                                                        |
| - | --------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| 1 | Always send with `parse_mode: "HTML"`.                                     | Markdown mode strips fences and backticks without creating entities (§2.1). |
| 2 | Escape `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;` inside `<pre>` and `<code>`. | Raw `<` breaks the HTML parse and aborts the whole message (§2.2).        |
| 3 | Use `<b>` for headings, `<code>` for inline identifiers, `<pre>` for code.  | Those three are the only elements proven to survive the round-trip (§2.2). |
| 4 | Never use ` ``` ` fences or `*bold*` Markdown syntax.                       | Both are consumed or left literal (§2.1).                                 |
| 5 | Write Persian without U+200C ZWNJ — use a normal space instead.            | ZWNJ is lost on the read path for every message (§3).                      |
| 6 | Keep each message under ~3800 characters; split longer payloads into parts, each a reply to the same parent id. | The hard limit is 4096 and the failure is an opaque `GEN-ERR-184` (§1). |
| 7 | Post into a forum topic with `reply_to_message` anchored to a message inside that topic. | `send_message` has no `topic_id` and lands in General (§4).         |
| 8 | Verify a formatted send by reading it back and checking the `&lt;`/`&gt;` round-trip. | `get_history` resolves entities to plain text, so a text diff cannot prove formatting (§6). |
| 9 | Delete every probe message after reading it back.                           | Keeps the group clean; message ids are not reused (§5).                    |
