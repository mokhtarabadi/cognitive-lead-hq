---
created_at: '2026-09-26T06:49:52.094220+00:00'
status: active
tags: []
updated_at: '2026-09-26T06:49:52.095684+00:00'
---

# V2 Server-Password Sync (OpenChamber external mode) — 2026-09-26

V2 `opencode serve` mints a random Basic-auth password EVERY boot unless OPENCODE_PASSWORD/OPENCODE_SERVER_PASSWORD is set. External OpenChamber (OPENCODE_HOST + OPENCODE_SKIP_START) authenticates with OPENCODE_SERVER_PASSWORD from its own env. Any mismatch = `OpenCode info endpoint responded with status 401` + PushWatcher upstream_unavailable floods.

Fix: one stable password in `~/.config/opencode/.server-password` (chmod 600), pinned on the server via `opencode-server.service.d/10-password.conf`, and as the OPENCODE_SERVER_PASSWORD line in `~/.config/openchamber/startup.env` (EnvironmentFile wins over drop-ins — the startup.env edit is load-bearing). After ANY `openchamber startup enable` (rewrites startup.env), re-apply the line, daemon-reload, restart both (USER action). Verify: zero `status: 401` in openchamber journal + `[PushWatcher] connected`.

Supersedes: workflows/global-install-upgrade (extends it for V2 external-server auth).