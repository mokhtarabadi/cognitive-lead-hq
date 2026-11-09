# Task 392: Remove skill from smart-compact discardTools default

**File:** `tasks/completed/392-smart-compact-skill-discard-default.md`
**Source:** manager
**Type:** bug
**Status:** closed
**Submitted:** 2026-11-09T08:05:11Z
**Finished:** 2026-11-09T08:33:02Z
**Estimate:** 1h
**Milestone:** M01

## Goal

Stop the smart-compact plugin from discarding every `skill` tool result by default, so `Load Skill` returns its body to the agent (not the placeholder notice).

## Manager's Notes

Found via blind subagent tests: every `skill` call returned the exact placeholder `Skill contents omitted after compaction; recall the skill if needed.` Removing the key in `~/.config/opencode/smart-compact.jsonc` changed nothing. Root cause is in the plugin source at `../opencode-smart-compact/src/config.ts`: `DEFAULT_CONFIG.pruning.discardTools` hardcodes the `skill` entry, and config merging spreads defaults under user config (`{...base.pruning.discardTools, ...user}`), so an absent key in user config cannot remove it. Also, the discard check in `prune.ts` runs before `protectedTools`, so protecting `skill` cannot prevent the discard either. Audit `../opencode-smart-compact` README + defaults and fix at the source with an explicit opt-out.

## Local TODOs

- [x] Audit `../opencode-smart-compact` README + `src/config.ts` defaults
- [x] Remove `skill` from `discardTools` default (keep `todowrite`); make the user override able to remove a default key (explicit `null`/empty opt-out, not just spread)
- [x] Add `question` + `skill` to `protectedTools` defaults; document why `skill` must never be discarded
- [x] Add regression test: loading a skill returns full content, not the placeholder
- [x] Bump package version, run typecheck + tests, update CHANGELOG
- [x] Point the OpenCode install at the local plugin path (or republish) and restart; re-run the blind skill-load test

## Acceptance Criteria

- [x] `DEFAULT_CONFIG.pruning.discardTools` no longer contains `skill`, and user config can now remove a default discard key
- [x] A fresh session loading any skill receives its body verbatim (no placeholder); `discardTools` safely returns `todowrite` only by default
- [x] `npm run typecheck` and `npm test` pass in `../opencode-smart-compact`; version bumped in `package.json` + `CHANGELOG.md`
- [x] Global reinstall is verified with a blind `Load Skill` (e.g. `kanban-lifecycle`) returning real content

## Verification Evidence

- **Test command:** `rtk test npm test` (in `../opencode-smart-compact`)
- **Expected result:** all vitest suites pass
- **Actual result:** tests 141, pass 141, fail 0 (incl new `skill-discard.test.ts`); `npm run typecheck` clean
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `testing-verification` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by that evidence.

## Risk & Rollback

- **Risk:** `discardTools` semantics change — users who depended on skill discarding (unlikely; it breaks the tool) would see larger context.
- **Rollback plan:** revert the config default; re-pin the previous published version in `~/.config/opencode/opencode.json`.

## Execution Log & Reasoning

**Created:** plugin source located at `../opencode-smart-compact` (sibling repo, alongside `../opencode-goal-plugin`). `src/config.ts:96-100` hardcodes `discardTools.skill`; `src/config.ts:297-299` spreads defaults, so user deletion is a no-op; `src/prune.ts:152` discards before the `protectedTools` guard. Going forward, audit `README.md` + `DECISIONS.md` and the `DEFAULT_CONFIG` first before touching anything else.

**Fixed:** removed `skill` from `DEFAULT_CONFIG.pruning.discardTools` (only `todowrite` remains); `protectedTools` now defaults to `["question", "skill"]`; user `null` value in `discardTools` now deletes the default key (explicit opt-out). New regression test `tests/skill-discard.test.ts` asserts `skill` is not discarded and is protected. Version bumped 0.2.1 → 0.2.2; `CHANGELOG.md` Unreleased → Fixed. Typecheck clean, 141/141 tests pass.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `1331a73e1eb8f0a25727c1e70a3c03d96cd63059`
<!-- END_GIT_DIFF -->
