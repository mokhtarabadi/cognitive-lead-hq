# Cognitive Loop Engine — Configuration Reference

All configuration lives in `loop-engine/loop-engine.jsonc`.

## Full Example

```jsonc
{
  // Default LLM provider (fallback when category has no available model)
  "default_provider": "gemini/gemini-2.5-flash",

  // Category-based model routing
  "categories": {
    "quick": {
      "models": ["kimi/kimi-k3"],
      "description": "Single-file changes, typos, quick fixes"
    },
    "deep": {
      "models": ["openai/gpt-5.6-sol", "gemini/gemini-2.5-pro"],
      "reasoning": "medium",
      "description": "Autonomous research + execution"
    },
    "visual": {
      "models": ["anthropic/claude-opus-5", "kimi/kimi-k3"],
      "reasoning": "max",
      "description": "Frontend, UI/UX, design"
    },
    "unspecified": {
      "models": ["gemini/gemini-2.5-flash", "kimi/kimi-k3"],
      "description": "Default fallback"
    }
  },

  // Max concurrent requests per provider
  "provider_concurrency": {
    "anthropic": 3,
    "openai": 3,
    "opencode": 10,
    "kimi": 5
  },

  // Max concurrent Hands sessions
  "max_parallel_tasks": 1,

  // Auto-continue settings (delegated to Goal Plugin)
  "idle": {
    "thinking_timeout_seconds": 60,
    "executing_timeout_seconds": 900,
    "max_retries": 5,
    "no_progress_threshold": 50,
    "no_progress_turns_before_pause": 2,
    "min_delay_seconds": 2.0
  },

  // Telegram approval gateway
  "approval": {
    "bot_token_env": "TELEGRAM_BOT_TOKEN",
    "chat_id": 0,
    "timeout_seconds": 3600
  },

  // QA settings
  "max_qa_retries": 3,
  "evidence_dir": "loop-engine/evidence",

  // File paths (relative to workspace root)
  "system_prompt_path": "system-prompt.md",
  "tasks_dir": "tasks",
  "agmd_path": "AGENTS.md",
  "conventions_path": "docs/conventions.md"
}
```

## Options Reference

### `default_provider`

- **Type:** `string`
- **Default:** `"gemini/gemini-2.5-flash"`
- **Description:** Fallback model when no category-specific model is available.

### `categories`

- **Type:** `object`
- **Description:** Category-based model routing. Each category has an ordered list of models (fallback chain).

| Category | Use Case | Default Models |
|---|---|---|
| `quick` | Single-file changes, typos | kimi/kimi-k3 |
| `deep` | Research, complex execution | openai/gpt-5.6-sol, gemini/gemini-2.5-pro |
| `visual` | Frontend, UI/UX | anthropic/claude-opus-5, kimi/kimi-k3 |
| `unspecified` | Everything else | gemini/gemini-2.5-flash, kimi/kimi-k3 |

Each category supports:
- `models`: Array of `provider/model` strings (ordered by preference)
- `reasoning`: Optional reasoning level (`"low"`, `"medium"`, `"high"`, `"max"`)
- `description`: Human-readable description

### `provider_concurrency`

- **Type:** `object`
- **Description:** Max concurrent requests per provider (prevents cost spiral).

### `max_parallel_tasks`

- **Type:** `integer`
- **Default:** `1`
- **Range:** `1-4`
- **Description:** Max concurrent Hands (OpenCode) sessions.

### `idle`

- **Type:** `object`
- **Description:** Auto-continue settings. Delegated to Goal Plugin.

| Option | Default | Description |
|---|---|---|
| `thinking_timeout_seconds` | `60` | Timeout when agent is thinking (no bash running) |
| `executing_timeout_seconds` | `900` | Timeout when bash command is running (15 min) |
| `max_retries` | `5` | Max auto-continue attempts before Manager alert |
| `no_progress_threshold` | `50` | Token threshold for no-progress detection |
| `no_progress_turns_before_pause` | `2` | Consecutive low-progress turns before pause |
| `min_delay_seconds` | `2.0` | Cooldown between continue attempts |

### `approval`

- **Type:** `object`
- **Description:** Telegram approval gateway settings.

| Option | Default | Description |
|---|---|---|
| `bot_token_env` | `"TELEGRAM_BOT_TOKEN"` | Env var name for bot token |
| `chat_id` | `0` | Telegram chat ID for Manager |
| `timeout_seconds` | `3600` | How long to wait for Manager response |

### `max_qa_retries`

- **Type:** `integer`
- **Default:** `3`
- **Description:** Max QA retry loops before marking task as crashed.

### `evidence_dir`

- **Type:** `string`
- **Default:** `"loop-engine/evidence"`
- **Description:** Directory for QA evidence files.

### File Paths

| Option | Default | Description |
|---|---|---|
| `system_prompt_path` | `"system-prompt.md"` | Path to system prompt |
| `tasks_dir` | `"tasks"` | Path to tasks directory |
| `agmd_path` | `"AGENTS.md"` | Path to project rules |
| `conventions_path` | `"docs/conventions.md"` | Path to conventions doc |

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram bot token from BotFather |
| `TELEGRAM_CHAT_ID` | Yes | Your Telegram chat ID |
| `GEMINI_API_KEY` | No* | Google Gemini API key |
| `KIMI_API_KEY` | No* | Kimi API key |
| `OPENAI_API_KEY` | No* | OpenAI API key |
| `ANTHROPIC_API_KEY` | No* | Anthropic API key |

*At least one LLM provider key is required.

## JSONC Format

The config file uses JSONC (JSON with Comments):
- `//` line comments
- `/* */` block comments
- Trailing commas allowed
- Environment variable references: `${VAR_NAME}`
