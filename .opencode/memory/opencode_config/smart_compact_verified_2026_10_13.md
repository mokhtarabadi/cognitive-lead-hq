---
created_at: '2026-10-13T05:59:55.723115+00:00'
status: active
tags: []
updated_at: '2026-10-13T05:59:55.723128+00:00'
---

# Smart Compact v0.2.1 verified live (2026-10-13, post-restart smoke test)
- Global plugin refreshed from git HEAD `8dc42f9` (v0.2.1); fresh cache `~/.cache/opencode/npm/git-opencode-smart-compact-*/1791871052256` fetched at restart, package version confirmed 0.2.1.
- No `PluginModule.LoadError` or smart-compact load errors in opencode.log after restart.
- `opencode plugin list` shows registry packages only (todolist); github-spec plugins load but are not enumerated — use the npm cache version to verify, not the list.
- Project `.opencode/smart-compact.jsonc` (`enabled: true`) parses valid; project tracks global defaults + override.
- Global system-prompt at 9.59.0, audit-agents skill synced (smart-compact ignore); AGENTS.md gained the living-docs sibling-inspection guardrail.