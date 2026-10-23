# Architectural Decisions: services

## [2026-10-06] ADR-001: Initial Slice Baseline

- **Context:** Baseline documentation initialized via init-folder-docs.
- **Decision:** Adopting Living Folder Docs standard for this component.
- **Consequences:** All future structural or contract changes must be recorded here.
- **Rollback:** N/A (baseline adoption).

## [2026-10-23] ADR-002: zen-proxy is provisioned from this slice

- **Context:** The Brain's provider hop (`127.0.0.1:8081`) was owned by the
  `code-server` homelab repo while its only consumer lived here, so every
  behavioural change landed in a repo that did not own the need.
- **Decision:** `zen-proxy.service` ships here next to the MCP units, points
  `ExecStart` at `~/.config/opencode/zen-proxy/.venv/bin/python`, and reads
  the single global `~/.config/opencode/.env`. It stays out of the `mcp-*`
  naming because it speaks the OpenAI API, not MCP.
- **Consequences:** One provisioning pass installs every loopback service;
  the Brain's provider and its consumer share a repo and an `.env`.
- **Rollback:** Restore the unit from the `code-server` history and re-point
  the path; no other service depends on it.
