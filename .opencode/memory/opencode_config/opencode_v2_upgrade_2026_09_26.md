---
created_at: '2026-09-26T06:28:07.289833+00:00'
status: active
tags: []
updated_at: '2026-10-01T00:00:00.000000+00:00'
---

# OpenCode V2 Upgrade — 2026-09-26 (state refreshed 2026-10-01)

- Binary upgraded via https://opencode.ai/v2/install; currently **v2.0.21** (verified with `opencode --version`; the official update endpoint `https://opencode.ai/update/api/latest/cli/npm` reports 2.0.21 as latest — already current).
- Global `cli.json` uses the native V2 shape: `$schema` https://opencode.ai/v2/cli.json (no plugin entries — the project uses no OpenCode plugins).
- Global and project `opencode.json` use V2 keys only (`plugins` plural if any, `permission.shell`). No V1 dual keys remain.
- Project `cli.json` removed (V2 client config is global-only); project `tui.json` deleted.
- MCP block uses native V2 `mcp.servers` with `disabled:false` + `timeout:{catalog,execution}`.
- V1→V2 DB migration key `migration.v1-v2` reached phase `completed`.
- OpenChamber **2.1.0** active (latest on npm).
- Plugin policy: **no OpenCode plugins** — the goal plugin and DCP/compress plugin were removed 2026-10-01 per Manager order. OpenChamber's built-in Session Goals replace the goal plugin.
- Supersedes: opencode_config/global_goal_plugin_upgrade_2026_08_27 (deleted), plugin_policy_dcp_only_2026_09_08 (deleted), plugins_full_v2_status_2026_09_26 (deleted).
