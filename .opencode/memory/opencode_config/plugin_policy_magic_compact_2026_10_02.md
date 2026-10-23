---
created_at: '2026-10-13T05:56:36.413817+00:00'
status: active
tags: []
updated_at: '2026-10-13T05:56:36.413829+00:00'
---

# OpenCode plugin policy — Smart Compact (updated 2026-10-13)
One plugin is approved and installed: `@mokhtarabadi/opencode-smart-compact` (V2-native context compaction, our own repo `mokhtarabadi/opencode-smart-compact`). It REPLACES the V1 `magic-compact` package, which fails to load on OpenCode 2 (`PluginModule.LoadError`).
- Global opencode.json: `plugins: ["github:mokhtarabadi/opencode-smart-compact"]` (Git spec, tracks main). Once published to npm, `@mokhtarabadi/opencode-smart-compact` is preferred. `opencode plugin add` rejects bare local paths.
- 2026-10-13 refresh: upstream HEAD `8dc42f9` = v0.2.1 (closes budget-guard deadlock); global npm cache still held v0.2.0, so `plugin remove` + `plugin add` re-registered the spec and the stale `~/.cache/opencode/npm/git-opencode-smart-compact-*/` dir was deleted to force a fresh git fetch on next session start. `opencode plugin list` / `check` / `update <github-spec>` do NOT see github-spec plugins (registry packages only; `update` errors `Plugin is not configured`) — remove+add is the refresh path. Restart required for new code to load.
- Project reference: `.opencode/smart-compact.jsonc` (`enabled: true`, validated vs v0.2.1) overrides global defaults per-project; the audit-agents skill ignores it (never flag/patch/delete/gitignore).
- Native OpenCode compaction stays on: `compaction: {auto: true, keep: {tokens: 20000}}`.
- smart-compact is V2-native: per-session state in plugin storage applied to model-visible messages; never mutates the stored transcript. Tool `read_omitted_content` (session-scoped).
- Repo gates: `npm run typecheck`, `npm test`, `npm run verify:package`. CI publishes via npm OIDC trusted publishing once the package name exists on npm.
- Rollback: `opencode plugin remove github:mokhtarabadi/opencode-smart-compact`; native compaction continues.
- Docs: docs/compaction.md is the full guide; fragment 22 (<compaction_protocol>) and agents/cognitive-executor.md carry the contract.
- 2026-10-22: upstream moved to `fa02c759` (v0.2.1). Platform thresholds are now `warnRatio 0.5` / `emergencyRatio 0.8` in the global `smart-compact.jsonc`, plus the incoming `autoTrimRatio 0.5` key that schedules a lossless tool-output trim without an agent call. Refresh path is unchanged: remove + add the github spec, restart.