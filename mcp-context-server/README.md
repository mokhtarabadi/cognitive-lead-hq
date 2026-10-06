# Slice: mcp-context-server

## Duties

Custom-context MCP daemon: directory trees, source reads, signature extraction, diff staging/injection (`stage_and_inject_diff`), task commit/clean, and meta-task bundling (`bundle_tasks`).

## Files

- `server.py` — Daemon entrypoint (tree reports, source reads, staging, bundling tools).
- `pyproject.toml` / `uv.lock` — Runtime deps (`pathspec`, `mcp[cli]`) and lockfile.

## Key Risks & Invariants

- ZAC enforcement point: staging goes through `stage_and_inject_diff`; never `git commit` directly.
- Path confinement: all scans stay inside project root; vendor dirs excluded.
- Bundle lifecycle (META + supersede/archive) is the only writer of `tasks/archive/` moves.
