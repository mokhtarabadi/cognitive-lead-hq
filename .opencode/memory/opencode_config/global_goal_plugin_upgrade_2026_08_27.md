---
created_at: '2026-08-27T14:30:55.763872+00:00'
status: active
tags: []
updated_at: '2026-08-27T14:30:55.763893+00:00'
---

# Global Goal Plugin Upgrade — 2026-08-27

## What Changed
- Replaced `@prevalentware/opencode-goal-plugin` (scoped npm package) with the official `opencode-goal-plugin` (unscoped) in both global and project `opencode.json` configs.
- Added `command.goal` block with `template: "$ARGUMENTS"` and `agent: "cognitive-executor"` — required for the `/goal` slash command to register.
- Added `.opencode/goals/` to `.gitignore` (goal plugin persists state there).
- Updated `audit-agents` skill with Goal Plugin Gitignore criterion.

## Why
The official plugin from `willytop8/OpenCode-goal-plugin` publishes as `opencode-goal-plugin` on npm. The scoped package was either a fork or outdated. The `command.goal` block was missing entirely, which means the `/goal` command never registered. Agent must be `cognitive-executor` (not `build`) to match our default_agent.

## Reference
- Official repo: https://github.com/willytop8/OpenCode-goal-plugin
- OpenCode version: 1.18.23 (compatible)
- Config locations: `opencode.json` (project), `~/.config/opencode/opencode.json` (global)