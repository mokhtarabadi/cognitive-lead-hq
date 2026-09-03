# Telegram MCP — Work/Personal Setup & Skill Usage

> **Source:** Fork https://github.com/mokhtarabadi/telegram-mcp (tracks upstream https://github.com/chigwell/telegram-mcp v2.0.1+; fork adds `fix/allowed-root-automkdir-and-topic-filter` — auto-mkdir for allowed roots + `topic_id` filter on `get_history`, merged to `main`). Local checkout used by this HQ: `$HOME/.config/opencode/mcp-telegram-server` (`uv --directory ... run main.py` over stdio; `origin` = chigwell, `fork` = mokhtarabadi, active branch `main` = fork patched). For global OpenCode install see `LLM.txt` Steps 7/7.6.

## 1. What the Telegram MCP Does (80+ tools)

| Area | Representative tools | Notes |
|------|---------------------|-------|
| **Accounts** | `list_accounts`, routing by `account` param | Multi-account via `TELEGRAM_SESSION_STRING_<LABEL>`; single-account `account` optional |
| **Chats/Groups** | `list_chats`, `get_chat`, `create_group`, `join_chat`, `invite_to_chat`, `manage_admins`, `set_slow_mode`, `manage_topics`, `get_common_chats` | Forum/supergroup topics supported |
| **Messages** | `send_message`, `reply_to_message`, `edit_message`, `delete_message`, `forward_message`, `pin_message`, `search_messages`, `send_poll`, `manage_reactions`, `press_inline_button` | Rich modes `rich`/`rich_markdown`/`rich_html` require Premium; classic `md`/`html` always works |
| **Contacts** | `set_contact_alias`, `list_contact_aliases`, `delete_contact_alias`, `add_contact`, `block_user` | Fuzzy alias file `~/.local/state/telegram-mcp/aliases.json` |
| **Media** | `send_file`, `download_media`, `send_voice`, `send_sticker` | File-path security via allowed roots |
| **Profile/Privacy** | `get_me`, `update_profile`, `set_profile_photo`, `get_user_info` | |
| **Folders/Drafts** | `list_folders`, `create_folder`, `save_draft` | |
| **Events** | `wait_for_new_message`, `wait_for_settled_message`, `enable_incoming_feed`, `incoming_feed_status` | Callback mode for Claude Code |

All Telegram-controlled strings are sanitized (`sanitize_user_content`) and returned as structured JSON.

---

## 2. Prerequisites

1. Python 3.10+ and `uv` (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
2. Telegram API credentials from https://my.telegram.org/apps → `API_ID` + `API_HASH`
3. MCP client (OpenCode, Claude Desktop, Cursor)
4. Optional: `python-socks` for proxy (`uv sync --extra proxy`)

## 3. Generate a Session String (per account)

```bash
git clone https://github.com/mokhtarabadi/telegram-mcp.git $HOME/.config/opencode/mcp-telegram-server
cd $HOME/.config/opencode/mcp-telegram-server
# remotes: origin = chigwell upstream (read-only), fork = mokhtarabadi (patched)
# fork main = upstream main + fix/allowed-root-automkdir-and-topic-filter
uv sync

# Create the two allowed roots — file tools (send_file/download_media) fail with
# "Path rejected" on first use if these do not exist:
# Note: patched server (≥ fix/allowed-root-automkdir) auto-creates missing roots
# with mkdir -p instead of SystemExit, but manual mkdir remains recommended for first install:
mkdir -p /tmp/telegram-mcp
mkdir -p $HOME/.config/opencode/mcp-telegram-server/downloads

# QR login (recommended if Telegram open on another device)
uv run session_string_generator.py --qr

# or phone-code login
uv run session_string_generator.py --phone
```

Save the printed session string securely — it grants full account access. Never commit `.env` or `*.session`.

For headless/runbook use pass `--qr` or `--phone` explicitly; without a flag the generator prompts interactively.

## 4. Configure Environment

### 4.1 Single-account (personal)

```bash
cp .env.example .env
# .env
TELEGRAM_API_ID=123456
TELEGRAM_API_HASH=abcdef123...
TELEGRAM_SESSION_STRING=1A...long string...
# optional hardening
TELEGRAM_EXPOSED_TOOLS=all               # or read-only / read-only+send_message,reply_to_message
TELEGRAM_DEVICE_MODEL=Telegram MCP
TELEGRAM_SYSTEM_VERSION=1.0
TELEGRAM_APP_VERSION=1.0
```

### 4.2 Multi-account (work + personal)

Labels are lowercased → `account` param value.

```bash
# .env — two accounts share API_ID/HASH but have distinct session strings
TELEGRAM_API_ID=123456
TELEGRAM_API_HASH=abcdef...
TELEGRAM_SESSION_STRING_WORK=1A...work session...
TELEGRAM_SESSION_STRING_PERSONAL=1B...personal session...

# per-account proxy overrides (optional)
TELEGRAM_PROXY_TYPE_WORK=http
TELEGRAM_PROXY_HOST_WORK=proxy.work.example
TELEGRAM_PROXY_PORT_WORK=3128
```

***Routing rules:***

- Single-account mode: `account` param optional.
- Multi-account mode: write tools (`send_message`, `send_file`, etc.) **require** `account="work"` or `"personal"`; read tools fan out to all accounts when `account` omitted.
- Example prompts: `"List my accounts"`, `"Send this from my work account to @example"`.

### 4.3 Session pool (one account, several concurrent clients)

If you run desktop app **and** CLI against the same account, give each client its own session to avoid `AuthKeyDuplicatedError`:

```bash
TELEGRAM_SESSION_STRINGS="sessionA sessionB sessionC"  # whitespace/comma/semicolon separated
```

Each process claims a free slot via advisory lock; if all slots claimed the server refuses to start rather than colliding. Generate extras with `uv run session_string_generator.py`.

### 4.4 Allowed roots (file tools)

`send_file`, `download_media`, `upload_file`, `send_voice`, etc. are **disabled until allowed roots exist**. Set via CLI args (fallback) or MCP Roots (client-provided, replaces CLI).

```bash
# server CLI (installed in opencode config dir, absolute paths)
uv run main.py /tmp/telegram-mcp $HOME/.config/opencode/mcp-telegram-server/downloads

# opencode.json example (global, absolute paths only — $HOME replaced with real absolute path per LLM.txt Step 3)
{
  "mcpServers": {
    "telegram": {
      "command": "uv",
      "args": ["--directory", "$HOME/.config/opencode/mcp-telegram-server", "run", "main.py", "/tmp/telegram-mcp", "$HOME/.config/opencode/mcp-telegram-server/downloads"]
    }
  }
}
```

- Empty client Roots → deny-all by default. Set `TELEGRAM_ALLOW_SERVER_ROOTS_FALLBACK=1` to fall back to CLI roots when client advertises empty Roots.
- Paths are real-path resolved, traversal/wildcard/null-byte rejected, relative paths resolve under first root, downloads default to `<first_root>/downloads/`.
- Override alias file: `TELEGRAM_ALIASES_FILE`; feed file: `TELEGRAM_EVENT_FEED_FILE` / `TELEGRAM_EVENT_FEED=1`.

### 4.5 Transport, device, proxy summary

| Variable | Default | Purpose |
|----------|---------|---------|
| `MCP_TRANSPORT` | `stdio` | `stdio` (one process/client), `http` (`MCP_HOST:8765/mcp`, shared), `sse` (legacy) |
| `MCP_HOST`/`MCP_PORT` | `127.0.0.1:8765` | For `http`/`sse`; set `MCP_ALLOWED_HOSTS` if behind domain |
| `TELEGRAM_DEVICE_MODEL`/`TELEGRAM_SYSTEM_VERSION`/`TELEGRAM_APP_VERSION` | platform default | Stable name in Settings → Devices |
| `TELEGRAM_PROXY_TYPE` | — | `socks5`/`socks4`/`http`/`mtproxy` + `HOST`/`PORT`/`USERNAME`/`PASSWORD`; per-label `_<LABEL>` overrides |
| `TELEGRAM_EXPOSED_TOOLS` | `all` | `all` / `read-only` / `read-only+tool,tool` (typo aborts startup) |

## 5. MCP Client Configuration

### 5.1 OpenCode (global, `~/.config/opencode/opencode.json`)

```json
{
  "mcp": {
    "telegram": {
      "type": "local",
      "command": ["uv", "--directory", "$HOME/.config/opencode/mcp-telegram-server", "run", "main.py", "/tmp/telegram-mcp", "$HOME/.config/opencode/mcp-telegram-server/downloads"],
      "enabled": true,
      "timeout": 15000
    }
  },
  "permission": { "telegram_*": "allow" }
}
```

Replace `$HOME` with your actual absolute home path (e.g., `/home/<user>` or `/Users/<user>`, see `LLM.txt` Step 3). Restart OpenCode after saving (`opencode.json` loaded once at startup).

### 5.2 Claude Desktop / Cursor

```json
{
  "mcpServers": {
    "telegram": {
      "command": "uv",
      "args": ["--directory", "/full/path/to/telegram-mcp", "run", "main.py"],
      "env": {
        "TELEGRAM_API_ID": "...",
        "TELEGRAM_API_HASH": "...",
        "TELEGRAM_SESSION_STRING": "..."
      }
    }
  }
}
```

### 5.3 HTTP shared server (multi-client, recommended)

```bash
MCP_TRANSPORT=http MCP_HOST=0.0.0.0 uv run main.py  # inside container/Docker
# publish only locally: docker run -p 127.0.0.1:8765:8765
claude mcp add --transport http telegram http://127.0.0.1:8765/mcp
codex mcp add telegram --url http://127.0.0.1:8765/mcp
```

## 6. Where This HQ Uses the Telegram MCP

| HQ Skill / Workflow | Telegram MCP tools it calls | Config file mapping | Typical flow |
|---------------------|----------------------------|---------------------|--------------|
| **`telegram-issue-sync`** (`skill-templates/telegram-issue-sync/SKILL.md`) | `telegram_get_history` (filter `reply_to == config.topic_id` then `id > last_processed_message_id`), `telegram_get_message_context` (parent chain walk to topic root), `telegram_reply_to_message` (topic-targeted reply), optionally GitHub issue create | `telegram-sync.json` at repo root: `config.chat_id`, `config.topic_id` (**topic-scoped — ONLY this topic syncs**), `config.account`, `target_hashtags` (`bug`, `feature`, `improve`), `last_processed_message_id`, `processed_ids`, `sync_registry` | Phase 1 fetch + client-filter by `reply_to` → Phase 2 manager approval → Phase 3 per-candidate: verbatim `RAW_TEXT` → translate → `prompt-refactor` → codebase `grep/glob` → task file + optional GH issue → topic-targeted reply |
| **`telegram-message-export`** (`skill-templates/telegram-message-export/SKILL.md`) | `telegram_get_history` (range `[from_id,to_id]`), `telegram_get_media_info`, `telegram_download_media` | No `telegram-sync.json`; takes `[from_id,to_id]` or snippet/link `t.me/c/CHAT/MSG` | Phase 1 fetch & sort → Phase 2 write `{n}.txt` sidecars + `reply_to_message_id` + media download → Phase 3 `zip -r telegram-exports/export-{ts}.zip` → Phase 4 notification |
| **Direct ad-hoc use** | `send_file` (file attachments to General topic `chat_id=-1003993323129`), `send_message`/`reply_to_message` | `account="personal"` per memory `workflows/telegram-file-delivery` | `telegram_send_file(chat_id, file_path, caption, account="personal")` → verifies via `telegram_get_messages` |

**Memory quirks that apply:**
- `workflows/telegram-file-delivery` — send whole file as attachment to General topic (id 1), never chunk into text; `send_file` has no `reply_to` so General is default; chat `-1003993323129`.
- `workflows/global-install-upgrade` — all MCP servers now live under `~/.config/opencode/` (`mcp-context-server`, `mcp-memory-server`, `mcp-lint-server`, `mcp-telegram-server`; `blowsh` is Docker).

## 7. Account Choice in Practice

| Need | Value to set / pass |
|------|---------------------|
| Personal task sync | `telegram-sync.json` `account: "personal"` + `TELEGRAM_SESSION_STRING_PERSONAL` in `.env`; tools called with `account="personal"` |
| Work announcement | `account="work"` in `send_message` + `TELEGRAM_SESSION_STRING_WORK` |
| Read across both | Omit `account` on read tools (`search_messages`, `list_chats`) → fans out |
| Pool isolation | `TELEGRAM_SESSION_STRINGS` per account label |

The server prompts the LLM when `account` ambiguous ("unknown / resembles one / matches several") → instructs LLM to ask user and retry with `set_contact_alias` — never sends to wrong contact.

## 8. Security & Troubleshooting

- Never commit `.env` / session strings / `*.session` / `aliases.json`.
- `telegram-mcp` on PyPI is **not** this repo — do not `uvx telegram-mcp` (credential theft risk); always clone `mokhtarabadi/telegram-mcp` (our patched fork) or `pip install git+https://github.com/mokhtarabadi/telegram-mcp.git@<tag>` (upstream is `chigwell/telegram-mcp`).
- Startup guard `assert_safe_distribution()` refuses an unsafe installed distribution without source checkout.
- Common failures: `No Telegram session configured` → set `TELEGRAM_SESSION_STRING[_LABEL]`; `Session is not authorized` → regenerate via `session_string_generator.py --qr`; `AuthKeyDuplicatedError` → use session pool + `TELEGRAM_LOCK_GRACE_SECONDS`; `File tools are disabled` / `Path rejected` → set allowed roots and keep path inside root; check `mcp_errors.log`.

## 9. Related Docs

- `skill-templates/telegram-issue-sync/SKILL.md` — full sync SOP (zero-summarization, bilingual task files)
- `skill-templates/telegram-message-export/SKILL.md` — export SOP (reply hierarchy + zip)
- `LLM.txt` Steps 7, 7.6, 10 — global auto-install including telegram
