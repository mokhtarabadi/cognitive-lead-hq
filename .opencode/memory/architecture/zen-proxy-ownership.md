---
created_at: '2026-10-23T00:00:00+00:00'
status: active
tags: [zen-proxy, gateway, brain-provider, systemd, global-install]
---

# zen-proxy is owned by this repo (2026-10-23)

The loopback gateway sidecar on `127.0.0.1:8081` lives in `zen-proxy/` and is
provisioned from `services/zen-proxy.service`. It was moved here from the
`code-server` homelab repo, which now keeps only a historical pointer.

**Why:** its original consumer (Open-WebUI) was retired 2026-09-19, and the
only live consumer is this repo's Brain Bridge
(`BRAIN_API_BASE=http://127.0.0.1:8081/go/resp`). Every behavioural change
since then — route allowlists, `reasoning.effort` translation, per-model
windows, the 64-char input-id rule, the 900s upstream timeout — was driven by
Brain/Hands needs but landed in the other repo.

**Contract (unchanged by the move):**

- Port `127.0.0.1:8081`; mounts `/zen/chat`, `/zen/resp`, `/go/chat`,
  `/go/resp`; `GET /health` → 200.
- Both `GET /models` and `POST` are allowlist-gated; a wrong-mount post
  returns `404 ModelNotServedHere` naming the correct mount.
- The proxy holds **no API key**: the caller's `Authorization` header passes
  through. It reads the single global `~/.config/opencode/.env`.
- Installed at `~/.config/opencode/zen-proxy/`, venv built with `uv`, unit
  launches the venv interpreter directly (never `uv run` at runtime).

**Timeout ordering (binding):** `ZEN_PROXY_UPSTREAM_TIMEOUT` (900) ≤
`BRAIN_OVERALL_DEADLINE_S` (900) ≤ MCP client execution timeout (1200s).
A proxy timeout below a real turn's duration surfaces as
`RemoteProtocolError: Server disconnected without sending a response`
followed by `provider overall deadline hit`.

**Do not** re-add a proxy copy to `code-server`; fix it here.
Docs: `docs/zen-proxy.md`, `zen-proxy/DECISIONS.md`.
