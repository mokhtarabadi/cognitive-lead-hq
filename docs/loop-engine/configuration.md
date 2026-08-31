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

### Executor Stack Context Injection & Goal Plugin Guardrails (LE-4)

`loop-engine/executor.py` (`HandsExecutor`) launches the local OpenCode agent as a subprocess and monitors its output for Goal Plugin termination tokens.

**Structured XML prompt (`_build_prompt`):** The executor builds the agent prompt from clean XML-delimited sections, emitted only when relevant:

| Section | Emitted when | Content |
|---|---|---|
| `<task_instructions>` | always | Read the task file at `<path>` and implement it; follow AGENTS.md rules exactly |
| `<stack_context name="..." display_name="...">` | `stack_profile` present | `MANDATORY: Load required skills via the native skill tool: <skills>`; preflight commands; `Run toolchain verification before completion: test='...', build='...', lint='...'` |
| `<blueprint_context>` | `blueprint_context` non-empty | Approved Architect plan (LE-0.1) |
| `<qa_feedback>` | `qa_feedback` non-empty | QA rejection feedback + `Address the above QA feedback explicitly. Do NOT treat this as a new architectural plan.` |
| `<goal_rules>` | always | `When finished and verified, output [goal:complete]. If stuck, output [goal:blocked: <reason>].` |

**Goal Plugin termination tokens:** The executor parses agent output with case-insensitive regexes:

- `TERM_COMPLETE = [goal:complete]` → `{"status": "complete", ...}`
- `TERM_BLOCKED = [goal:blocked]` or `[goal:blocked: <reason>]` → `{"status": "blocked", ..., "reason": <extracted reason or "Agent signaled blocked">}`
- `TRANSPORT_ERROR` (stream disconnected / ECONNRESET / ETIMEDOUT / EPIPE / timeout / connection reset) → retried up to `MAX_RETRIES=3` with `RETRY_DELAY=5s`

A `proc.returncode == 0` exit also maps to `complete`.

**Process group isolation:** On POSIX systems the subprocess is launched with `start_new_session=True`, placing it in its own process group. On `asyncio.TimeoutError` the executor kills the **entire process group** with `os.killpg(os.getpgid(proc.pid), signal.SIGKILL)` (suppressing `ProcessLookupError`/`AttributeError`/`PermissionError`), drains with `proc.wait(timeout=2.0)`, and returns `{"status": "timeout", "error": "Exceeded <timeout>s timeout"}`. This prevents orphaned agent processes.

**Timeout:** The subprocess timeout comes from `idle.executing_timeout_seconds` (default `900`), falling back to `900.0` if unset — the same budget as the rest of the pipeline.

**Concurrency semaphore:** `HandsExecutor.__init__` creates `asyncio.Semaphore(config.max_parallel_tasks)`; `execute()` wraps the entire run (including transport retries) in `async with self._semaphore:`, guaranteeing the daemon never exceeds the configured concurrent Hands sessions.

### End-to-End Smoke Test Gate (LE-5 / Task 137)

Phase A is certified by the canonical end-to-end smoke suite:
`loop-engine/test_polyglot_smoke.py` (16 tests, 5 happy-path stacks + 7 hard fail-fast
gates + 4 supplementary edge cases). The full suite bar is **≥ 178 passing, 0 failures**
(baseline 163 + 16 smoke).

```bash
uv run --project loop-engine --with pytest pytest loop-engine/test_polyglot_smoke.py -v
uv run --project loop-engine --with pytest pytest loop-engine/ -q   # full gate
```

**Test-harness guarantees:**

- **Hermetic workspace:** every test builds an isolated `tmp_path` workspace with
  `stacks/`, `tasks/{backlog,in-progress,qa,completed}/`, `loop-engine/{evidence,state}/`,
  and dummy `AGENTS.md`, `system-prompt.md`, `docs/conventions.md`, `loop-engine.jsonc`.
- **Real components, scripted I/O seams:** real `StateMachine`, `LLMRouter`, `QAEngine`,
  `HandsExecutor`, `ApprovalGateway`, `LoopEngineDaemon` instances are wired to the
  workspace. Only process boundaries are scripted: `call_llm` (deterministic per-stage
  responses), `executor._run_once` (simulates the Hands agent writing the diff block and
  emitting `[goal:complete]` / `[goal:blocked: <reason>]` tokens processed by the real
  TERM_* regexes), and `gateway.request_approval` (auto-approve or scripted denial).
- **REPO_ROOT anchoring:** `daemon.REPO_ROOT` is patched to the workspace for each
  pipeline run, so stack detection, preflight/toolchain `cwd`, and evidence writes never
  escape the sandbox.
- **Sandboxed commands:** workspace stack YAMLs mirror repository defaults (detection
  markers/extensions/keywords, skills, model_preferences) but preflight/toolchain commands
  are portable no-ops (`true`) or deterministic failures (`false`, fail-first marker
  files). Sandbox deviations are documented inline: bare `"go"` and `"gin"` keywords are
  dropped from the go-gin profile because they substring-match `## Goal` and the canonical
  `<!-- BEGIN_GIT_DIFF -->` markers, which would make the generic fallback unreachable.

**What the gate proves:** multi-stack ingestion/detection, preflight fail-fast before
execution, toolchain verification bypassing LLM QA on failure with evidence written, goal
blocked-reason extraction, empty-diff crash, retry recovery to `CLOSED`, max-retry crash,
header-over-marker precedence, plan/review rejection paths, QA-feedback threading, and
daemon boot-scan `PENDING_TRIGGER` registration.

### Contract Propagation & Downstream Task Dispatcher (LE-6 / Task 138)

`loop-engine/contracts.py` (`ContractPropagationEngine`) watches for **contract file
mutations** in closed task diffs and automatically dispatches downstream tasks into
`tasks/backlog/` — eliminating contract drift across multi-service monorepos.

**Pipeline:**

1. The daemon closure hooks (`_process_task`, `_reimplement_task`) run immediately after
   `state.update_state(task_id, TaskState.CLOSED)`: they extract the task's git diff via
   `extract_task_diff()` and call `ContractPropagationEngine.process_task_closure(...)`.
2. `extract_modified_paths(diff_text)` parses `diff --git a/… b/…` headers (regex
   `^diff --git a/(.+?) b/(.+?)\n`, multiline) and returns deduplicated relative paths.
3. `match_contract_rules(paths, rules)` evaluates each path against every rule pattern
   with `fnmatch` (full-relative-path globbing: `packages/shared-schema/**` matches nested
   files, `*.prisma` matches `prisma/schema.prisma`, `openapi/*.yaml` matches
   `openapi/petstore.yaml`).
4. For each matched rule × downstream template, the engine computes
   `discover_next_task_id(tasks_dir)` (max numeric prefix across
   `backlog|in-progress|qa|completed|archive` + 1), writes a canonical task file, and
   registers it in the StateMachine as `BACKLOG` via `state.register_task(...)`.
5. IDs increment per generated task so a single closure can dispatch a sequential batch.
   Non-contract diffs produce **zero** tasks (no-op).

**Generated task shape** (mirrors the canonical `task-generator` template):

```markdown
# Task {N}: {title}
**File:** tasks/backlog/{N:02d}-{slug}.md
**Source:** contract-propagation
**Triggered-By:** Task {closed_task_id}
**Stack:** {template.stack}
**Type:** feature
**Status:** open

## Goal
{goal}

## Source Context
Generated automatically via Contract Propagation Engine following contract mutations in Task {closed_task_id}.
Modified contract files:
- {file1}
- {file2}

## Acceptance Criteria
- [ ] {criteria}

## Factual Git Diff
<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
```

**`contract_rules` configuration schema** (`LoopEngineConfig`):

| Field | Type | Description |
|---|---|---|
| `name` | `string` | Canonical rule name, e.g. `openapi-spec`, `prisma-schema` |
| `patterns` | `string[]` | Glob patterns for contract files, e.g. `["openapi/**", "contracts/*.yaml"]` |
| `downstream_tasks` | `object[]` | `DownstreamTaskTemplate`s to generate upon mutation |

Each `DownstreamTaskTemplate`:

| Field | Type | Description |
|---|---|---|
| `title_template` | `string` | Title template; supports `{contract_name}`, `{triggering_task_id}` |
| `stack` | `string` | Stack profile for the downstream task (default `generic`) |
| `goal_template` | `string` | Goal template; supports `{contract_name}`, `{triggering_task_id}`, `{files}` |
| `acceptance_criteria` | `string[]` | Standard AC checkboxes for the task |

**Default rules** (applied when `contract_rules` is omitted):

| Rule | Patterns | Default downstream template |
|---|---|---|
| `openapi-spec` | `openapi/**`, `contracts/*.yaml`, `contracts/*.json` | Regenerate API client (`node-ts`) |
| `prisma-schema` | `*.prisma`, `prisma/**` | Sync Prisma schema migration (`node-ts`) |
| `protobuf` | `proto/**`, `*.proto` | Regenerate gRPC stubs (`generic`) |
| `shared-schema` | `packages/shared-schema/**`, `shared/schemas/**` | Propagate shared schema (`generic`) |

**Example override** (`loop-engine/loop-engine.jsonc`):

```jsonc
"contract_rules": [
  {
    "name": "openapi-spec",
    "patterns": ["openapi/**", "contracts/*.yaml", "contracts/*.json"],
    "downstream_tasks": [
      {
        "title_template": "Sync TypeScript SDK with updated {contract_name}",
        "stack": "node-ts",
        "goal_template": "Regenerate the TypeScript SDK to match {contract_name}. Files: {files}",
        "acceptance_criteria": ["SDK regenerated", "TypeScript types updated", "Tests pass"]
      }
    ]
  }
]
```

**Guardrails:** downstream tasks are only generated on **closure** (`CLOSED`), so rejected,
crashed, or retried tasks never spawn duplicates; `discover_next_task_id` is collision-free
across all task folders; and the engine is fully disabled if `contracts.py` cannot be
imported (`ImportError` fallback in `daemon.py`).

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
