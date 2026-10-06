# Slice: mcp-common

## Duties

Shared stdlib-only helpers for all MCP daemons (env loading, common paths). Single home for logic previously duplicated inside each server.

## Files

- `src/mcp_common/env.py` — Explicit `.env` file loader, no third-party imports.
- `src/mcp_common/__init__.py` — Package marker.
- `pyproject.toml` / `uv.lock` — Package metadata and lockfile.

## Key Risks & Invariants

- Must stay dependency-free (stdlib only) so every daemon can import it offline.
- Changes here propagate to all MCP servers; verify each server's tests after edits.
- No daemon-specific logic; per-server behavior stays in its own `server.py`.
