---
created_at: '2026-08-27T14:30:55.763872+00:00'
status: active
tags: []
updated_at: '2026-08-27T14:30:55.763893+00:00'
---

# Global Goal Plugin Upgrade — 2026-08-27

## What Changed (2026-08-28 — Re-migrated to @prevalentware/opencode-goal-plugin per Manager directive, supersedes 2026-08-27 willytop8 alignment)
- **2026-08-28:** Migrated FROM `opencode-goal-plugin` (willytop8, v0.8.2) TO `@prevalentware/opencode-goal-plugin` (v0.1.39) in both global `~/.config/opencode/opencode.json` and project `opencode.json` — `plugin: ["@prevalentware/opencode-goal-plugin"]`.
- Created `tui.json` parity for OpenCode 1 stable (required by prevalentware docs): `~/.config/opencode/tui.json` and `tui.json` (project root) both `{"plugin":["@prevalentware/opencode-goal-plugin"]}`. OpenCode 1 reads both `opencode.json` + `tui.json`; without `tui.json` the sidebar/palette goal UI does not appear.
- Deleted corrupted local `.opencode/opencode.json` (`{"plugin":["list"]}`) — stray file created by erroneous `opencode plugin list` run (untracked, `git status` clean after removal). Correct project config is root `opencode.json`.
- Preserved `command.goal` block (`template: "$ARGUMENTS"`, `agent: "cognitive-executor"`) — still required for `/goal` registration.
- `.opencode/goals/` remains in `.gitignore`; `audit-agents` skill criterion unchanged.

## Why (2026-08-28)
Manager explicitly requested full migration to `@prevalentware/opencode-goal-plugin` (https://github.com/prevalentWare/opencode-goal-plugin, npm `https://www.npmjs.com/package/@prevalentware/opencode-goal-plugin`) which follows Codex native goal-mode semantics and includes `@opencode-ai/plugin`, `@opentui/solid`, `effect`, `solid-js`, `zod` (vs willytop8 single-dep). The 2026-08-27 note aligned to willytop8 as “official” — that decision is now superseded. OpenCode 1.18.25 is stable and uses `plugin` + `tui.json` (not `plugins` + `cli.json` which is OpenCode 2 beta). The `tui.json` addition ensures the TUI sidebar/palette integration loads.

## Reference
- New repo: https://github.com/prevalentWare/opencode-goal-plugin (npm `@prevalentware/opencode-goal-plugin` v0.1.39, 40 versions, 5 deps)
- Previous repo: https://github.com/willytop8/OpenCode-goal-plugin (npm `opencode-goal-plugin` v0.8.2) — preserved in history `tasks/archive/122`, `docs/history/milestone-15-summary.md`
- OpenCode version: 1.18.25 stable (uses `plugin` + `tui.json`); OpenCode 2 beta would use `plugins` + `cli.json`
- Config locations: `opencode.json` + `tui.json` (both project root and `~/.config/opencode/` global)