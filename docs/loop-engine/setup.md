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
TELEGRAM_CHAT_ID=123456789
GEMINI_API_KEY=AIzaSy...
```

### 9. Configure Loop Engine

Edit `loop-engine/loop-engine.jsonc`:
```json
{
  "approval": {
    "chat_id": 123456789
  }
}
```

### 10. Start the Daemon

```bash
cd loop-engine
source .venv/bin/activate
python daemon.py
```

You should see:
```
============================================================
  Cognitive Loop Engine — Starting...
============================================================
[watcher] Watching tasks/backlog for new tasks...
[daemon] Found 0 existing tasks in backlog.
[daemon] Watching for new tasks... Press Ctrl+C to stop.
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
```

Expected output:
```
8 passed, 0 failed
10 passed, 0 failed
9 passed, 0 failed
8 passed, 0 failed
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
