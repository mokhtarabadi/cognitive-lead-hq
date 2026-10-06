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

## Key Risks & Invariants

- Single-tool invariant: no second tool or slash-command path may bypass `brain_turn`.
- Helpers (`capability`, `loop_guard`, `preflight`) stay stdlib-only and importable without MCP runtime so tests stay offline.
- Session ledger is append-only; never rewrite history lines.
