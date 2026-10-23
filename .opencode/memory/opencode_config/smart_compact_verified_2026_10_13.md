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

## Re-verified 2026-10-22 (v0.2.1 at `fa02c759`)

- Installed cache commit `fa02c759` equals local `HEAD` and `origin/main`; package version `0.2.1`, entry `src/index.ts`.
- Global config `~/.config/opencode/smart-compact.jsonc` parses; effective values read back through the plugin's own `loadConfig`: `useTokens true`, `tokens.enabled true`, `awareness {warnRatio 0.5, emergencyRatio 0.8, rearmStep 0.05, autoTrimRatio 0.5}`.
- Suite `91/91` green, `tsc --noEmit` clean. Live `compact_context` calls applied on the following request (`prunedParts 30`, `prunedTokens 22668`, `pending` cleared).
- Machine-wide plugin storage: 25.2 MB across 25 live sessions, no per-session cap on cached omission originals. Four orphaned state rows (sessions already deleted) were backed up to `/tmp/sc-orphan-states-backup.json` and removed.
- Thresholds were lowered because a 1M-token window at the shipped `0.7` only warns around 734K tokens. `autoTrimRatio` is a new plugin key: until the repository is pushed and the plugin re-added, the installed build logs `Unknown config key: awareness.autoTrimRatio` and ignores it, while the ratio thresholds apply immediately.

## Plugin repo tasks 14 and 15 landed (2026-10-23)

- `7e88f166` + `c73dcadc` (task 14): `awareness.autoTrimRatio` with a lossless tool-output trim queued at pressure; default `0`, platform `0.5`.
- `cfd3c8e` (task 15): per-session re-arm latch (`autoTrimLastRatio` in the state whitelist) so one sustained pressure period trims once, reset via `autoTrimResetLine`; a zero or invalid `rearmStep` no longer re-queues at an unchanged fill (review finding); D8 records the in-process hook serialization guarantee of host v2.1.3 plus the cross-process caveat, with no lock added.
- Verification: 95/95 tests, `tsc --noEmit` clean, QA `QA_PASSED`, review `APPROVED`.
- Handler note: the installed build still predates both tasks until the repository is pushed and the plugin is re-added; until then the only live change on this machine is the threshold pair in the global config.