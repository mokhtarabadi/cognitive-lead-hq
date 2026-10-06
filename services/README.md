# Slice: services

## Duties

OS service singletons for MCP daemons: systemd units plus launchd plists and Windows singleton template. Guarantees one loopback-only instance per daemon.

## Files

- `mcp-context.service` / `mcp-brain.service` / `mcp-lint.service` / `mcp-memory.service` — systemd units (streamable HTTP, loopback only).
- `mcp-telegram.service` — Telegram sync service unit.
- `launchd/ai.cognitivelead.mcp-*.plist` — macOS launchd singletons mirroring the systemd units.
- `windows/mcp-singleton-template.xml` — Windows singleton template.

## Key Risks & Invariants

- Singleton invariant: exactly one instance per daemon; duplicates cause port/state conflicts.
- Bind loopback only; never expose MCP HTTP to the network.
- Unit `ExecStart` paths must track the deployed checkout layout (`%h/.config/opencode/...`).
