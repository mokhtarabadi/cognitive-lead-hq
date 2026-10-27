# Slice: mcp-lint-server

## Duties

Lint MCP daemon: task-file validation (`lint_task_file`, incl. META-shape and planner-metadata gates), system-prompt sync checks (incl. unactionable-skill-verb gate), and Markdown/format gates run before staging and closure.

## Files

- `server.py` — Daemon entrypoint (lint and sync-check tools).
- `pyproject.toml` / `uv.lock` — Runtime deps and lockfile.

## Key Risks & Invariants

- Lint is a pre-stage gate; staging with a stale `**File:**` header must fail.
- The path-drift comparison resolves both the `**File:**` header and the actual file against the caller's `project_root`, never the server process CWD. The server is a singleton started elsewhere, so CWD anchoring flags every relative header (it made `lint_all_tasks` report one false mismatch per file).
- Prompt-sync checks must compare assembled output against committed `system-prompt.md`.
- Keep checks offline and deterministic; no network in lint path.
- Planner metadata (`**Estimate:**`, `**Deadline:**`, `**Depends on:**`) is validated only when present: the Planner silently drops a value it cannot parse, so a malformed line must fail here instead. Absence is always valid — legacy task files carry none.
