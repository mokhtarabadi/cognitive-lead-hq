---
created_at: '2026-09-26T06:49:52.094220+00:00'
status: active
tags: []
updated_at: '2026-10-01T00:00:00.000000+00:00'
---

# V2 server auth — managed mode only (updated 2026-10-01)

OpenChamber now **manages its own OpenCode server** (managed mode). The old external-server setup is retired: no `opencode-server.service` unit, no `OPENCODE_HOST`, no `OPENCODE_SKIP_START`, so the V2 random-password / 401 sync problem no longer applies — OpenChamber and its managed server share one process tree and one credential automatically.

If someone reintroduces external mode (`OPENCODE_HOST` + `OPENCODE_SKIP_START=true`), then: V2 `opencode serve` mints a random Basic-auth password every boot unless `OPENCODE_SERVER_PASSWORD` is set, and the mismatch shows as `OpenCode info endpoint responded with status 401` + `PushWatcher upstream_unavailable`. The fix in that case is one stable password in `~/.config/opencode/.server-password` (chmod 600), pinned on the server unit and mirrored into the client env.

Retired with the external unit 2026-10-01 (docs cleanup).
