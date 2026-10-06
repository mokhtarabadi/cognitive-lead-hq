# Slice: mcp-lint-server

## Duties

Lint MCP daemon: task-file validation (`lint_task_file`), system-prompt sync checks, and Markdown/format gates run before staging and closure.

## Files

- `server.py` — Daemon entrypoint (lint and sync-check tools).
- `pyproject.toml` / `uv.lock` — Runtime deps and lockfile.

## Key Risks & Invariants

- Lint is a pre-stage gate; staging with a stale `**File:**` header must fail.
- Prompt-sync checks must compare assembled output against committed `system-prompt.md`.
- Keep checks offline and deterministic; no network in lint path.
