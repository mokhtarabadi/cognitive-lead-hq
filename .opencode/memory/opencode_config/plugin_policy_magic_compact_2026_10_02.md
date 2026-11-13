---
created_at: '2026-11-10T11:21:24.259383+00:00'
status: active
tags: []
updated_at: '2026-11-10T11:21:24.259409+00:00'
---

# OpenCode plugin policy — Smart Compact (updated 2026-11-13)

**THREE plugins are approved and installed** (2026-11-13): `github:mokhtarabadi/opencode-smart-compact` (V2-native context compaction), `github:mokhtarabadi/opencode-goal-plugin` (one long-running objective per session, with evidence-gated completion), and `opencode-todolist` (V1 `todowrite`/`todoread` + the TUI sidebar strip, also listed in `~/.config/opencode/cli.json`). Earlier notes claiming "no OpenCode plugins" are stale.

Smart Compact REPLACES the V1 `magic-compact` package, which fails to load on OpenCode 2 (`PluginModule.LoadError`). `magic-compact` must never be added.
- Global opencode.json `plugins`: `["github:mokhtarabadi/opencode-smart-compact", "github:mokhtarabadi/opencode-goal-plugin", "opencode-todolist"]` (git specs track `main`; `opencode plugin add` rejects bare local paths).
- 2026-10-13 refresh: upstream HEAD `8dc42f9` = v0.2.1 (closes budget-guard deadlock); global npm cache still held v0.2.0, so `plugin remove` + `plugin add` re-registered the spec and the stale `~/.cache/opencode/npm/git-opencode-smart-compact-*/` dir was deleted to force a fresh git fetch on next session start. `opencode plugin list` / `check` / `update <github-spec>` do NOT see github-spec plugins (registry packages only; `update` errors `Plugin is not configured`) — remove+add is the refresh path. Restart required for new code to load.
- Project reference: `.opencode/smart-compact.jsonc` overrides global defaults per-project and now carries the HQ working budget (200k cap, warn 120k, emergency 160k — needs plugin 0.3.0+); the audit-agents skill ignores it (never flag/patch/delete/gitignore).
- Native OpenCode compaction stays on: `compaction: {auto: true, keep: {tokens: 20000}}`.
- smart-compact is V2-native: per-session state in plugin storage applied to model-visible messages; never mutates the stored transcript.
- Agent tools are three: `compact_context` (compress now; `keepTurns`, `mode`), `read_omitted_content` (retrieve one cached omission by session-scoped Content ID), and `compact_stats` (read-only, no inputs, returns the same savings line as `/magic-stats` through one shared `formatStats`). Manager commands stay `/magic-compact`, `/magic-trim`, `/magic-stats`.
- Repo gates: `npm run typecheck`, `npm test`, `npm run verify:package`. CI publishes via npm OIDC trusted publishing once the package name exists on npm.
- Rollback: `opencode plugin remove github:mokhtarabadi/opencode-smart-compact`; native compaction continues.
- Docs: `docs/compaction.md` is the full guide; the live operational contract is the Compaction section of `agents/cognitive-executor.md`. The system prompt is plugin-blind, and `prompts/archive/22-compaction_protocol.md` is archived and never assembled.
- 2026-10-22: upstream moved to `fa02c759` (v0.2.1). Ratio thresholds in the global `smart-compact.jsonc` moved to `warnRatio 0.5` / `emergencyRatio 0.8`, plus the incoming `autoTrimRatio 0.5` key that schedules a lossless tool-output trim without an agent call. Refresh path is unchanged: remove + add the github spec, restart.
- 2026-10-24: `compact_stats` landed upstream in `2e702680` (closure `dd9e98a7`); installed cache dir `1792858905411` serves it. Smoke test on the live session returned `pruned ~130226 tokens across 213 tool results; summarized 0 turns; 13 cached omissions`, matching the plugin storage exactly. Auto-trim keeps doing the work in practice: a session can run to 365 messages with zero summarized turns and still be trimmed losslessly.
- 2026-11-10 (0.3.0 semantics — supersedes the ratio-only reading above): awareness is token-threshold based. `awareness.contextWindowTokens` is a HARD CAP on the denominator (effective window = `min(registry limit, configured)`), not only a fallback for a silent registry. `awareness.warnAtTokens` and `awareness.emergencyAtTokens` are absolute token thresholds and 0 disables either, because a ratio on a 1M window only speaks at 500k/800k. The plugin logs one console line per fired reminder and per queued auto-trim, and `compact_stats` reports the effective window plus whether config capped it. Practical rule: when the plugin warns, or when a closed task's context is dead, call `compact_context` yourself.