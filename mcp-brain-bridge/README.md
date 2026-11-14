# Slice: mcp-brain-bridge

## Duties

Brain Bridge MCP daemon: single-tool (`brain_turn`) automation path for planning, QA, and review turns, plus session ledger, loop-spin guard, capability preflight, and request preflight.

## Files

- `server.py` — MCP daemon entrypoint exposing `brain_turn` (only automation path).
- `capability.py` — Capability preflight mapping required tools to AVAILABLE/UNAVAILABLE.
- `preflight.py` — Request validation (project_root must hold `tasks/`, memory binding).
- `loop_guard.py` — Diff-hash spin guard (same hash 3x stops autopilot fix loop).
- `session_ledger.py` — Append-only JSONL session event ledger under `tasks/.sessions/`.
- Per-turn artifacts: each `brain_turn` attempts to write `tasks/.sessions/<session>/brain_outputs/<resp>_<uuid>.json` (`xml_blocks` + full raw output); the result's `output_address` points at it for truncated-tail recovery. An artifact whose serialized JSON exceeds the 5 MB session byte cap is skipped before temp-file creation and yields `output_address = None` while the turn continues. Retention is capped at 50 files / 5 MB per session, oldest-first. Artifact writes and retention pruning are serialized within the bridge process (RLock); abandoned `.tmp-` files are removed before each new write.
- `pyproject.toml` / `uv.lock` — Runtime deps and lockfile (`mcp[cli]`, stdlib-first helpers).
- `context-reports/` — Generated context output (do not hand-read; feed via MCP).
- `context_paths` line slices: `brain_turn(context_paths=[...])` accepts
  a trailing `#Lstart-end` (inclusive 1-based lines) or `#Lstart-` (tail
  to EOF); out-of-range ends clamp, empty selections and malformed
  `#L` fragments on supported paths render as explicit `[unavailable: …]`
  labels. Unlisted-suffix files sniff as text only when valid UTF-8
  without NUL or disallowed Unicode control characters (tab, LF, CR,
  form feed allowed); anything else renders `[unavailable: …]`.

## Key Risks & Invariants

- Single-tool invariant: no second tool or slash-command path may bypass `brain_turn`.
- Helpers (`capability`, `loop_guard`, `preflight`) stay stdlib-only and importable without MCP runtime so tests stay offline.
- Session ledger is append-only; never rewrite history lines.
- Request-shape evolution stays opt-in: every new Responses parameter
  ships behind a `BRAIN_SEND_*` / `BRAIN_USE_INSTRUCTIONS` switch
  defaulting to off, so default wire bytes never change silently.

## Upstream Modes & Chat Completions Protocol Bridge

`BRAIN_UPSTREAM_MODE` controls whether the bridge emits OpenAI Responses API requests or Chat Completions requests:
- `responses` (default): posts to `BRAIN_API_BASE/responses` with native Responses format.
- `chat_completions`: posts to `BRAIN_API_BASE/chat/completions` with OpenAI-compatible Chat Completions format.

In `chat_completions` mode:
- `instructions` and `input` are mapped to role-tagged `messages` (plain string `input` is supported as a single user message).
- `function_call` input items become `assistant` tool-call messages and `function_call_output` items become `role="tool"` messages with JSON arguments.
- `max_output_tokens` translates to `max_tokens`.
- `reasoning.effort` translates to `reasoning_effort`.
- `tools`, `tool_choice`, and `parallel_tool_calls` are converted to Chat Completions function calling shapes.
- Responses-only fields (`store`, `previous_response_id`, `metadata`, `include`, `truncation`, `service_tier`, `text`) are dropped with a logged warning.
- Responses are normalized into Responses API data structures: status is derived from `finish_reason` (`stop`/`tool_calls` -> `completed`, `length`/`content_filter`/unknown -> `incomplete`), errors map to `status: failed`, omitted usage counters remain omitted, and tool calls / reasoning content are preserved in `output`.
- `parse_responses_text` renders `function_call` items as `name(arguments)` text for agent consumption.
- Only an unrecognised status aborts while `status=incomplete` is annotated with `[upstream incomplete: <reason>]` and returned; `_record_brain_use` guards against null tokens in quota arithmetic.

## Stage-Scoped System Prompts

`brain_turn(stage=...)` selects the system prompt the Brain receives. The routing table is `prompts/stage-manifest.json` in the repository — the same file the assembler uses to generate the artifacts — so a stage is declared once and both sides agree on it. `resolve_stage_prompt_path(stage)` is pure and side-effect free: it returns the artifact path for a known stage and `None` for an unknown or empty stage.

Resolution order in `load_system_prompt`: explicit `system_prompt_path` → the stage artifact (repo copy first, then the `~/.config/opencode/` install) → `BRAIN_SYSTEM_PROMPT` → the full committed prompt. A known stage whose artifact is missing on disk falls through to the full prompt with one stderr note; it never returns an empty prompt and never raises because of a stage. An unknown stage string is rejected loudly by the preflight gate (`PreflightError`) rather than silently downgraded, so a typo fails visible instead of quietly running unscoped. `preflight.ALLOWED_STAGES` accepts `plan`, `implement`, `qa`, `review`, `closure`, and `brainstorm`.

Measured artifact sizes: full 95428 bytes; plan 89690; implement 80991; qa 80140; review 80850; closure 80991; brainstorm 95428.

## Plan-Turn Sufficiency Grounding

The bridge builds its plan-turn sufficiency diagnostic from the user prompt and the rendered `fed` and `paths` slots. A non-empty server-rendered `paths` slot grounds the `no fed-context block` diagnostic through the caller-provided `has_server_paths` flag; a literal `[path-injected:]` string in user text does not count as server-rendered path context. The existing `[fed-context]` and `[pinned-fed-context]` markers remain supported by the Hands-fed context contract. This change affects the sufficiency diagnostic only and does not change the request payload or context-path limits.
