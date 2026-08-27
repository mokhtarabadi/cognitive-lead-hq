# Cognitive Loop Engine — Setup Guide

## Prerequisites

| Requirement | Version | Purpose |
|---|---|---|
| Python | 3.12+ | Runtime |
| uv | Latest | Package manager |
| OpenCode | Installed | CLI execution |
| Telegram Bot | BotFather | Approval gateway |
| LLM API Key | At least one | AI planning/review |

## Step-by-Step Installation

### 1. Clone and Enter

```bash
cd cognitive-lead-hq
```

### 2. Create Virtual Environment

```bash
cd loop-engine
uv venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
uv pip install pydantic litellm watchdog python-telegram-bot
```

### 4. Verify Installation

```bash
python -c "
from models import LoopEngineConfig
from state import StateMachine
from watcher import KanbanWatcher
from router import LLMRouter
from executor import HandsExecutor
from gateway import ApprovalGateway
from qa_engine import QAEngine
print('All imports OK')
"
```

### 5. Create Telegram Bot

1. Open Telegram, search for `@BotFather`
2. Send `/newbot`
3. Choose a name (e.g., "Cognitive Loop Bot")
4. Choose a username (e.g., `cognitive_loop_bot`)
5. Copy the bot token (format: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### 6. Get Your Chat ID

1. Open Telegram, search for `@userinfobot`
2. Send any message
3. Copy your Chat ID (format: `123456789`)

### 7. Get LLM API Key

Choose at least one provider:

| Provider | How to Get | Environment Variable |
|---|---|---|
| Google Gemini | [AI Studio](https://aistudio.google.com/) | `GEMINI_API_KEY` |
| Kimi | [Kimi Code](https://www.kimi.com/code) | `KIMI_API_KEY` |
| OpenAI | [Platform](https://platform.openai.com/) | `OPENAI_API_KEY` |
| Anthropic | [Console](https://console.anthropic.com/) | `ANTHROPIC_API_KEY` |

### 8. Configure Environment

```bash
cd ..  # back to cognitive-lead-hq
cp .env.example .env
```

Edit `.env`:
```bash
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
GEMINI_API_KEY=AIzaSy...
```

> **Note:** The engine reads environment variables via `os.environ` — it does
> NOT auto-load `.env`. Export the variables in your shell (`set -a; source .env; set +a`)
> or use your process manager's env file support.

### 9. Configure Loop Engine

Edit `loop-engine/loop-engine.jsonc`:
```json
{
  "approval": {
    "chat_id": 123456789
  },
  "trigger_mode": "telegram_button",
  "auto_start_on_boot": false
}
```

> The Manager chat ID comes from this config field (`approval.chat_id`) — there
> is no `TELEGRAM_CHAT_ID` environment variable.

**Trigger modes:**
- `"telegram_button"` (default): Tasks wait for admin to tap [🚀 Start Execution] in Telegram.
- `"command_only"`: Tasks wait for admin to run `/run <task_id>` in Telegram.
- `"auto"`: Legacy — tasks auto-enter the pipeline immediately.

**Boot behavior:**
- `auto_start_on_boot: false` (default): Existing backlog tasks register as `PENDING_TRIGGER` and wait for admin action.
- `auto_start_on_boot: true`: Existing backlog tasks run immediately on daemon boot.

### 10. Start the Daemon

```bash
cd loop-engine
source .venv/bin/activate
python daemon.py
```

You can launch `daemon.py` from any working directory — all relative paths
(config, state DB, `tasks/`, evidence dir) are anchored to the repository root
automatically at startup.

Expected output:
```
============================================================
  Cognitive Loop Engine — Starting...
============================================================
[watcher] Watching tasks/backlog for new tasks (trigger_mode=telegram_button)...
[daemon] Found 0 existing tasks in backlog (trigger_mode=telegram_button, auto_start_on_boot=False).
[daemon] Watching for new tasks... Press Ctrl+C to stop.
```

### CLI Options

```bash
# Trigger a specific staged task directly
python daemon.py --run <task_id>
```

## Testing

### Run All Tests

```bash
cd loop-engine
source .venv/bin/activate
python test_models.py
python test_state.py
python test_router.py
python test_executor.py
python test_trigger_entry.py
```

Expected output:
```
8 passed, 0 failed
10 passed, 0 failed
9 passed, 0 failed
8 passed, 0 failed
9 passed, 0 failed
```

### Smoke Test

```bash
python -c "
from daemon import load_config
cfg = load_config()
print(f'Default provider: {cfg.default_provider}')
print(f'Categories: {list(cfg.categories.keys())}')
print(f'Max parallel: {cfg.max_parallel_tasks}')
print('Config load OK')
"
```

## Troubleshooting

| Error | Solution |
|---|---|
| `opencode CLI not found in PATH` | Install OpenCode or add to PATH |
| `TELEGRAM_BOT_TOKEN not set` | Check `.env` file |
| `litellm not installed` | Run `uv pip install litellm` |
| `pydantic not installed` | Run `uv pip install pydantic` |
| `Telegram error: Forbidden` | Bot not added to chat, or chat_id wrong |

## Next Steps

- [Configuration Reference](configuration.md) — all options explained
- [Multi-Project Guide](multi-project.md) — managing multiple projects
- [Architecture Overview](README.md) — how it all works together
