# Slice: mcp-memory-server

## Duties

Project-memory MCP daemon: namespaced persistent notes (`store_memory`, `search_memory`, `read_memory`), memory index rebuild, and cross-task constraint recall.

## Files

- `server.py` — Daemon entrypoint (memory CRUD and index tools).
- `pyproject.toml` / `uv.lock` — Runtime deps and lockfile.

## Key Risks & Invariants

- Save only durable rules/quirks; never task progress or code snippets (task file owns those).
- Index (`.opencode/memory/index.md`) is generated; search falls back to namespaces when missing.
- Memory never overrides explicit Manager orders; flag conflicts instead of silently applying.
