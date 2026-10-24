---
created_at: '2026-10-24T16:29:23.842054+00:00'
status: active
tags: []
updated_at: '2026-10-24T16:29:23.842072+00:00'
---

# OpenCode plugin policy — Smart Compact (updated 2026-10-24)

One plugin is approved and installed: `@mokhtarabadi/opencode-smart-compact` (V2-native context compaction, our own repo `mokhtarabadi/opencode-smart-compact`). It REPLACES the V1 `magic-compact` package, which fails to load on OpenCode 2 (`PluginModule.LoadError`).
- Global opencode.json: `plugins: ["github:mokhtarabadi/opencode-smart-compact"]` (Git spec, tracks main). Once published to npm, `@mokhtarabadi/opencode-smart-compact` is preferred. `opencode plugin add` rejects bare local paths.
- 2026-10-13 refresh: upstream HEAD `8dc42f9` = v0.2.1 (closes budget-guard deadlock); global npm cache still held v0.2.0, so `plugin remove` + `plugin add` re-registered the spec and the stale `~/.cache/opencode/npm/git-opencode-smart-compact-*/` dir was deleted to force a fresh git fetch on next session start. `opencode plugin list` / `check` / `update <github-spec>` do NOT see github-spec plugins (registry packages only; `update` errors `Plugin is not configured`) — remove+add is the refresh path. Restart required for new code to load.
- Project reference: `.opencode/smart-compact.jsonc` (`enabled: true`, validated vs v0.2.1) overrides global defaults per-project; the audit-agents skill ignores it (never flag/patch/delete/gitignore).
- Native OpenCode compaction stays on: `compaction: {auto: true, keep: {tokens: 20000}}`.
- smart-compact is V2-native: per-session state in plugin storage applied to model-visible messages; never mutates the stored transcript.
- Agent tools are three: `compact_context` (compress now; `keepTurns`, `mode`), `read_omitted_content` (retrieve one cached omission by session-scoped Content ID), and `compact_stats` (read-only, no inputs, returns the same savings line as `/magic-stats` through one shared `formatStats`). Manager commands stay `/magic-compact`, `/magic-trim`, `/magic-stats`.
- Repo gates: `npm run typecheck`, `npm test`, `npm run verify:package`. CI publishes via npm OIDC trusted publishing once the package name exists on npm.
- Rollback: `opencode plugin remove github:mokhtarabadi/opencode-smart-compact`; native compaction continues.
- Docs: `docs/compaction.md` is the full guide. The live contract is `agents/cognitive-executor.md` (`<compaction_protocol>` section); `prompts/archive/22-compaction_protocol.md` is archived and no longer assembled.
- 2026-10-22: upstream moved to `fa02c759` (v0.2.1). Platform thresholds are now `warnRatio 0.5` / `emergencyRatio 0.8` in the global `smart-compact.jsonc`, plus the incoming `autoTrimRatio 0.5` key that schedules a lossless tool-output trim without an agent call. Refresh path is unchanged: remove + add the github spec, restart.
- 2026-10-24: `compact_stats` landed upstream in `2e702680` (closure `dd9e98a7`); installed cache dir `1792858905411` serves it. Smoke test on the live session returned `pruned ~130226 tokens across 213 tool results; summarized 0 turns; 13 cached omissions`, matching the plugin storage exactly. Auto-trim keeps doing the work in practice: a session can run to 365 messages with zero summarized turns and still be trimmed losslessly.