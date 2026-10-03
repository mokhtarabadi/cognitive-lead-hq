---
created_at: '2026-10-03T07:37:08.832980+00:00'
status: active
tags: []
updated_at: '2026-10-03T07:37:08.832995+00:00'
---

# OpenCode plugin policy — Smart Compact (updated 2026-10-03)
One plugin is approved and installed: `@mokhtarabadi/opencode-smart-compact` (V2-native context compaction, our own repo `mokhtarabadi/opencode-smart-compact`). It REPLACES the V1 `magic-compact` package, which fails to load on OpenCode 2 (`PluginModule.LoadError`).
- Global opencode.json: `plugins: ["github:mokhtarabadi/opencode-smart-compact"]` (Git spec, verified loading). Once published to npm, `@mokhtarabadi/opencode-smart-compact` is preferred. `opencode plugin add` rejects bare local paths.
- Native OpenCode compaction stays on: `compaction: {auto: true, keep: {tokens: 20000}}`.
- smart-compact is V2-native: per-session state in plugin storage applied to model-visible messages via `session.hook("context")`; never mutates the stored transcript. Commands `/magic-compact [N]`, `/magic-trim [N]`, `/magic-stats`; tool `read_omitted_content` (session-scoped).
- Live smoke 2026-10-03: plugin loaded from the Git spec with no load errors; `read_omitted_content` registered and executes.
- Repo gates: `npm run typecheck`, `npm test` (14 tests), `npm run verify:package`. CI publishes via npm OIDC trusted publishing once the package name exists on npm.
- Rollback: `opencode plugin remove github:mokhtarabadi/opencode-smart-compact`; native compaction continues.
- Docs: docs/compaction.md is the full guide; fragment 22 (<compaction_protocol>) and agents/cognitive-executor.md carry the contract.