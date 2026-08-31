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

  // Task Entry Trigger Gate
  // Controls how tasks enter the execution loop
  "trigger_mode": "telegram_button",  // "telegram_button" | "command_only" | "auto"
  "auto_start_on_boot": false,        // if true, existing backlog tasks run immediately

  // File paths (relative to workspace root)
  "system_prompt_path": "system-prompt.md",
  "tasks_dir": "tasks",
  "agmd_path": "AGENTS.md",
  "conventions_path": "docs/conventions.md",

  // Stack Profiles
  "stacks_dir": "stacks",
  "default_stack": "generic"
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

### `trigger_mode`

- **Type:** `string`
- **Default:** `"telegram_button"`
- **Enum:** `"telegram_button"`, `"command_only"`, `"auto"`
- **Description:** Controls how tasks enter the execution loop.

| Mode | Behavior |
|---|---|
| `telegram_button` | Tasks register as `PENDING_TRIGGER`. Gateway sends a Telegram card with [🚀 Start Execution] / [⏸️ Hold] buttons. Admin taps to trigger. |
| `command_only` | Tasks register as `PENDING_TRIGGER`. Admin uses `/run <task_id>` or `/start <task_id>` in Telegram to trigger. |
| `auto` | Legacy behavior — tasks auto-enter the pipeline immediately on file detection. No admin gate. |

### `auto_start_on_boot`

- **Type:** `boolean`
- **Default:** `false`
- **Description:** If `true`, existing backlog tasks found during daemon boot run immediately (legacy behavior). If `false`, they are registered as `PENDING_TRIGGER` and wait for admin action.

### File Paths

| Option | Default | Description |
|---|---|---|
| `system_prompt_path` | `"system-prompt.md"` | Path to system prompt |
| `tasks_dir` | `"tasks"` | Path to tasks directory |
| `agmd_path` | `"AGENTS.md"` | Path to project rules |
| `conventions_path` | `"docs/conventions.md"` | Path to conventions doc |

### `stacks_dir`

- **Type:** `string`
- **Default:** `"stacks"`
- **Description:** Directory containing stack profile YAML/JSON definitions (relative to workspace root, or absolute). Each file defines one `StackProfileConfig`.

### `default_stack`

- **Type:** `string`
- **Default:** `"generic"`
- **Description:** Fallback stack name when detection finds no match. Must correspond to a file in `stacks_dir` (e.g., `generic.yaml`).

### Stack Profile Schema

Each file in `stacks_dir` (e.g., `python-fastapi.yaml`) validates against `StackProfileConfig`:

```yaml
name: python-fastapi           # canonical name (matches filename)
display_name: Python / FastAPI
detection:
  marker_files: ["pyproject.toml", "requirements.txt"]  # presence implies this stack
  extensions: [".py"]           # file extensions implying this stack
  task_keywords: ["python", "fastapi"]  # substring match in task content
skills: ["python-fastapi"]     # skills to auto-load for this stack
preflight:                     # shell commands validated before execution (empty = pass)
  - "python3 --version"
  - "uv --version || pytest --version"
toolchain:
  test_cmd: "pytest -q"
  build_cmd: null
  lint_cmd: "ruff check . || flake8 ."
model_preferences:          # optional per-category model overrides (LE-3)
  deep: ["openai/gpt-5.6-sol", "gemini/gemini-2.5-pro"]
  quick: ["gemini/gemini-2.5-flash"]
```

**Detection precedence (StackDetector):**

1. Explicit `**Stack:** <name>` header in task file (case-insensitive)
2. `marker_files` existence or matching `extensions` scan in workspace root
3. `task_keywords` substring search in task content (case-insensitive)
4. Fallback to `default_stack` (`generic`)

**Preflight:** All `preflight` commands run sequentially via shell with 30s timeout each. Non-zero exit or timeout → `PreflightResult(passed=False)` → daemon transitions task to `CRASHED` with diagnostics (`state.set_qa_feedback`).

**Registry:** `StackRegistry` scans `stacks_dir` on first access, supports both `.yaml`/`.yml` (via PyYAML) and `.json`, caches results, exposes `get_profile(name)` and `list_profiles()`.

**Available default profiles:**

| Profile | Detection | Skills | Toolchain |
|---|---|---|---|
| `generic` | fallback only | none | none |
| `node-ts` | `package.json`, `.ts/.tsx/.js`, keywords `node/typescript` | `nextjs`, `react-vite` | `pnpm test \|\| npm test` |
| `kotlin-android` | `build.gradle.kts`, `.kt/.kts`, keywords `kotlin/android` | `android-kotlin` | `./gradlew test` |
| `python-fastapi` | `pyproject.toml`, `.py`, keywords `python/fastapi` | `python-fastapi` | `pytest -q` |
| `go-gin` | `go.mod`, `.go`, keywords `go/gin` | `go-gin`, `go-hexagonal-grpc` | `go test ./...` |

### Stack-Aware Model Routing (LE-3)

`LLMRouter._resolve_model(category, stack_profile=None)` resolves the model for a
call through a **3-tier hierarchy** — stack preferences win when their provider
key is present, otherwise the global category chain applies, and
`default_provider` is the terminal fallback:

1. **Tier 1 — Stack-Preferred Models:** If a `stack_profile` is provided, its
   `model_preferences` dict is consulted. The exact `category` key is matched
   first, then the wildcard `"*"` key. For each candidate `provider/model` in
   order, the router checks `os.environ["{PROVIDER}_API_KEY"]`; the first model
   whose key is present wins. The reasoning level comes from the global category
   config (`categories[category].reasoning`), not the stack.
2. **Tier 2 — Global Category Models:** If no stack-preferred model is keyed
   (empty preferences, no category/wildcard match, or no provider key), the
   existing `categories[category].models` fallback chain is used.
3. **Tier 3 — Global Default:** If no category model is keyed either, the router
   returns `(default_provider, None)`.

**Propagation:** The daemon detects the stack **once** at the start of
`_process_task` (before planning) and forwards the resulting `StackProfile` into
`router.route_plan(..., stack_profile=profile)`, `_execute_and_qa(...,
stack_profile=profile)`, and `qa.run_review(..., stack_profile=profile)`.
`_reimplement_task` forwards it into `qa.run_review` as well. `QAEngine.run_qa`
and `QAEngine.run_review` accept `stack_profile` and forward it to the router
(with `TypeError` fallbacks for legacy router signatures).

**Backward compatibility:** `stack_profile` is optional everywhere
(`Optional[Any] = None`). When omitted, resolution behaves exactly as before
(Tier 2 → Tier 3). Both `StackProfile` objects (`.model_preferences` attribute)
and plain dicts (`{"model_preferences": {...}}`) are accepted.

**Default stack preferences:**

| Stack | `deep` | `quick` |
|---|---|---|
| `kotlin-android` | `anthropic/claude-3-7-sonnet`, `openai/gpt-5.6-sol` | `gemini/gemini-2.5-flash` |
| `node-ts` | `openai/gpt-5.6-sol`, `anthropic/claude-3-7-sonnet` | `kimi/kimi-k3` |
| `python-fastapi` | `openai/gpt-5.6-sol`, `gemini/gemini-2.5-pro` | `gemini/gemini-2.5-flash` |
| `go-gin` | `openai/gpt-5.6-sol`, `anthropic/claude-3-7-sonnet` | `gemini/gemini-2.5-flash` |

### Toolchain Verification (LE-2)

`loop-engine/verifier.py` executes each profile's `toolchain` deterministically **after** Hands produce a git diff and **before** LLM QA, providing fail-fast short-circuiting and factual evidence.

**Runner:** `ToolchainRunner(timeout_per_command=120.0, evidence_base_dir=config.evidence_dir)` iterates sequentially `lint → build → test`. Each command runs via `asyncio.create_subprocess_shell` with `asyncio.wait_for(timeout)`. Null or whitespace-only commands are recorded as `skipped=True` and `passed=True` (e.g., `generic` with all `null` → overall `PASSED` with 3× SKIPPED).

- **Default timeout:** `120s` per command (vs `30s` preflight). Covers slow toolchains like `./gradlew test` while staying inside `idle.executing_timeout_seconds=900`. Timeout kills via `proc.kill()` (suppresses `ProcessLookupError`) and records `passed=False` with diagnostic `Toolchain timeout (120s): <cmd>`.
- **Fail-fast semantics:** In `daemon.py:_execute_and_qa`, immediately after `extract_task_diff` non-empty check, the runner is invoked with `stack_profile` and `task_id`. If `not toolchain_result.passed`: `state.set_qa_feedback(task_id, report_md)` is called (increments `qa_retry_count`), the function returns `{"result": "FAILED", "report": report_md, "evidence_dir": "<evidence_dir>/<task_id>"}` **without calling `qa.run_qa`** — saving LLM tokens and routing to `_reimplement_task` retry loop up to `max_qa_retries`. If `passed`: summary is forwarded as `qa.run_qa(..., toolchain_evidence=summary)` to enrich the LLM prompt.
- **Evidence outputs:** If `task_id` is provided, the runner writes `<evidence_base_dir>/<task_id>/toolchain_report.md` (structured Markdown with summary table `| Type | Command | Result | Duration | Return Code |` and `## Failures` logs for non-zero/timeout) and `<evidence_base_dir>/<task_id>/toolchain_result.txt` (`PASSED` or `FAILED`). `QAEngine.run_qa` also accepts `toolchain_evidence` and injects it into `router.route_qa(..., toolchain_evidence=...)` → `<## Toolchain Verification>` block in the LLM prompt.
- **Shell semantics:** Toolchain commands are shell strings (so `||` fallbacks like `pnpm test || npm test` work). `stdout`/`stderr` are captured and truncated to 2000 chars in the report.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram bot token from BotFather (name configurable via `approval.bot_token_env`) |
| `GEMINI_API_KEY` | No* | Google Gemini API key |
| `KIMI_API_KEY` | No* | Kimi API key |
| `OPENAI_API_KEY` | No* | OpenAI API key |
| `ANTHROPIC_API_KEY` | No* | Anthropic API key |

*At least one LLM provider key is required.

> **Note:** There is no `TELEGRAM_CHAT_ID` environment variable — the Manager
> chat ID is configured via `approval.chat_id` in this file. The engine reads
> `os.environ` directly and does not auto-load a `.env` file.

## Provider Extensibility

Adding a new LLM provider requires no code changes:

1. Add models to any category's `models` list as `"provider/model"` strings
   (litellm resolves the provider prefix).
2. Export the provider key as `{PROVIDER}_API_KEY` (e.g. `provider/deepseek-x`
   → `DEEPSEEK_API_KEY`) — the router auto-detects available providers per call.
3. Optionally add a concurrency cap to `provider_concurrency`
   (`zai` currently relies on its Pydantic default of 10 when omitted).

Hardcoded limits: `ProviderConcurrency` in `models.py` declares fixed fields —
a brand-new provider without a field falls back to litellm's own rate limiting
until the model is extended.

## JSONC Format

The config file uses JSONC (JSON with Comments):
- `//` line comments and `/* */` block comments are stripped quote-aware, so
  string values containing `//` (e.g. `https://` URLs) are preserved
- Trailing commas allowed
- Environment variable references: `${VAR_NAME}`
