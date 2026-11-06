# Slice: mcp-brain-bridge

## Duties

Brain Bridge MCP daemon: single-tool (`brain_turn`) automation path for planning, QA, and review turns, plus session ledger, loop-spin guard, capability preflight, and request preflight.

## Files

- `server.py` — MCP daemon entrypoint exposing `brain_turn` (only automation path).
- `capability.py` — Capability preflight mapping required tools to AVAILABLE/UNAVAILABLE.
- `preflight.py` — Request validation (project_root must hold `tasks/`, memory binding).
- `loop_guard.py` — Diff-hash spin guard (same hash 3x stops autopilot fix loop).
- `session_ledger.py` — Append-only JSONL session event ledger under `tasks/.sessions/`.
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

## Plan-Turn Sufficiency Grounding

The bridge builds its plan-turn sufficiency diagnostic from the user prompt and the rendered `fed` and `paths` slots. A non-empty server-rendered `paths` slot grounds the `no fed-context block` diagnostic through the caller-provided `has_server_paths` flag; a literal `[path-injected:]` string in user text does not count as server-rendered path context. The existing `[fed-context]` and `[pinned-fed-context]` markers remain supported by the Hands-fed context contract. This change affects the sufficiency diagnostic only and does not change the request payload or context-path limits.
