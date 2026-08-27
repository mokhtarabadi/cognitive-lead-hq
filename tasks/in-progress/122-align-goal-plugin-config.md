# Task 122: Align Goal Plugin Config with Official Docs

**File:** `tasks/in-progress/122-align-goal-plugin-config.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Goal

Audit and align the OpenCode goal plugin configuration across both project and global `opencode.json` files to match the official `opencode-goal-plugin` documentation from `willytop8/OpenCode-goal-plugin`. Store a memory note about the global upgrade for future reference.

## Manager's Notes

- Both `/home/mohammad/.config/opencode/opencode.json` (global) and `/home/mohammad/code-server/projects/cognitive-lead-hq/opencode.json` (project) use `@prevalentware/opencode-goal-plugin` — a scoped npm package that may not be the official package.
- The official package is `opencode-goal-plugin` (unscoped).
- The `command.goal` registration block is missing from both configs — this is required for the `/goal` slash command to work.
- `.gitignore` needs an entry for `.opencode/goals/` per the official docs.
- OpenCode version is 1.18.23 which is compatible.
- Store a memory note about the upgrade for future reference.

## Local TODOs

- [x] Update project `opencode.json` — replace plugin name and add `command.goal` block
- [x] Update global `opencode.json` — replace plugin name and add `command.goal` block
- [x] Add `.opencode/goals/` to project `.gitignore`
- [x] Store memory note about the global upgrade
- [x] Update `CHANGELOG.md`
- [ ] Verify with `lint_task_file`

## Acceptance Criteria

- [ ] Both `opencode.json` files reference `opencode-goal-plugin` (unscoped) instead of `@prevalentware/opencode-goal-plugin`
- [ ] Both configs include the `command.goal` block with `description`, `template: "$ARGUMENTS"`, and `agent: "build"`
- [ ] `.gitignore` includes `.opencode/goals/`
- [ ] Memory note stored about the upgrade
- [ ] `CHANGELOG.md` updated
- [ ] `lint_task_file` passes

## Verification Evidence

- **Test command:** `cat opencode.json | grep -A4 '"command"'` and `cat /home/mohammad/.config/opencode/opencode.json | grep -A4 '"command"'`
- **Expected result:** Both show `opencode-goal-plugin` in plugin array and `command.goal` block present
- **Actual result:** _(fill during execution)_
- **Exit code:** _(fill during execution)_

## Definition of Done

The task is NOT done unless ALL of the following are true:

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Changing the plugin package name could break the goal plugin if the old scoped package had custom behavior.
- **Rollback plan:** Revert both `opencode.json` files via `git checkout HEAD -- opencode.json /home/mohammad/.config/opencode/opencode.json` (or manually restore from diff).

---

## Execution Log & Reasoning

**Execution Date:** 2026-08-27
**Model:** xiaomi/mimo-v2.5

### Changes Made

1. **Project `opencode.json`** — replaced `"@prevalentware/opencode-goal-plugin"` with `"opencode-goal-plugin"` in the `plugin` array. Added the mandatory `command.goal` block:
   ```json
   "command": {
     "goal": {
       "description": "Set a session-scoped goal and auto-continue until complete.",
       "template": "$ARGUMENTS",
       "agent": "build"
     }
   }
   ```

2. **Global `~/.config/opencode/opencode.json`** — same plugin name replacement. Added identical `command.goal` block. Preserved existing `opentmux` and `opencode-agent-tmux` plugins.

3. **`.gitignore`** — added `.opencode/goals/` entry (goal plugin persists per-project session-shard state there).

4. **Memory** — stored `opencode_config/global_goal_plugin_upgrade_2026_08_27` documenting the upgrade rationale, config locations, and reference URL.

5. **`CHANGELOG.md`** — added entry under `[Unreleased]` with full change description.

### Architectural Reasoning

- The official plugin from `willytop8/OpenCode-goal-plugin` publishes as `opencode-goal-plugin` on npm (unscoped). The scoped `@prevalentware/opencode-goal-plugin` was either a fork or outdated reference.
- The `command.goal` block is **mandatory** for the `/goal` slash command to register in OpenCode. Without it, the plugin loads but the command never appears.
- `template: "$ARGUMENTS"` passes the user's goal text to the plugin. `agent: "build"` routes goal requests to the build agent.
- Goal state persists to `.opencode/goals/` per project — gitignored to avoid leaking session state.

### Verification

- Both `opencode.json` files now reference `opencode-goal-plugin` (unscoped)
- Both configs include `command.goal` with correct fields
- `.gitignore` includes `.opencode/goals/`
- Memory stored successfully
- CHANGELOG updated

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
