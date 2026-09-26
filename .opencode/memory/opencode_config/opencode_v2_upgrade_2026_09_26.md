---
created_at: '2026-09-26T06:28:07.289833+00:00'
status: active
tags: []
updated_at: '2026-09-26T06:28:07.289848+00:00'
---

# OpenCode V2 Upgrade — 2026-09-26

- Global binary upgraded via https://opencode.ai/v2/install to v2.0.18 (verified with opencode --version).
- Global cli.json uses native V2 shape with $schema https://opencode.ai/v2/cli.json and plugins array (goal-plugin + dcp).
- Global and project opencode.json keep dual plugin (V1) + plugins (V2) keys, and dual permission.bash + permission.shell denies; V2 normalizes V1 in memory.
- Project cli.json removed (V2 client config is global-only); project tui.json leftover is harmless.
- MCP block still V1 shape (enabled:true, no servers wrapper) and permission object shape still V1; both accepted by V2 with warnings, native migration to mcp.servers/disabled and permissions array is optional.
- V1 to V2 DB migration key migration.v1-v2 reached phase completed after a transient SQLite database-is-locked during sessions phase caused by concurrent serve and CLI writers on 9GB db.
- OpenChamber 2.0.2 active; opencode-server systemd unit stopped per manager request while manual opencode serve --service still holds the DB.
- Supersedes: opencode_config/global_goal_plugin_upgrade_2026_08_27 (V1 plugin+tui.json note).