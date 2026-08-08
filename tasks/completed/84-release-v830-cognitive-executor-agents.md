# Task 84: Release v8.3.0 - Cognitive Executor Agents

**File:** `tasks/in-progress/84-release-v830-cognitive-executor-agents.md`
**Source:** manager
**Type:** feature
**Status:** open

## Source Context

### Variant C: Manager (`**Source:** manager`)

## Goal

Cut release **v8.3.0** (MINOR — new feature: global `cognitive-executor`/`cognitive-discovery` OpenCode agents from Tasks 82–83). Bump `<system_version>` to 8.3.0, move `[Unreleased]` entries into `## [8.3.0] - 2026-08-08` with a `### Changed` release entry, commit via the MCP lifecycle (ZAC: `git add/commit/push` denied at the permission layer), then tag `v8.3.0` and create the GitHub release.

## Manager's Notes

- **ZAC enforcement active:** this session runs under the `cognitive-executor` agent — `git add`, `git commit`, `git push`, `git tag` are denied via bash. Commits go exclusively through `custom_context_commit_and_clean_task` (the ONLY commit path). Tag + `gh release create` must be executed by the Manager (or approved), because no MCP tool covers tags/releases.
- Pre-release evidence: `git status` clean before edits; `origin/main` in sync (0 ahead / 0 behind).
- Version rationale: MINOR per SemVer (new agent features, non-breaking) following the milestone-release precedent (8.2.0 → 8.3.0).

## Local TODOs

- [x] Bump `<system_version>` in `system-prompt.md` from 8.2.0 → 8.3.0
- [x] CHANGELOG: move `[Unreleased]` → `## [8.3.0] - 2026-08-08`, keep Added entry, add `### Changed` release entry
- [x] Prettier format `system-prompt.md` + `CHANGELOG.md` (both unchanged by prettier)
- [x] Stage via `custom_context_stage_and_inject_diff`
- [x] Commit via `custom_context_commit_and_clean_task` (release message `ee5e9d7`)
- [ ] Manager: `git tag v8.3.0` + push tag + `gh release create v8.3.0` (ZAC-denied for the agent)

## Acceptance Criteria

- [x] `<system_version>8.3.0</system_version>` in system-prompt.md
- [x] CHANGELOG `## [8.3.0] - 2026-08-08` header with Added + Changed entries; `[Unreleased]` gone
- [ ] Release commit on origin/main (local: `ee5e9d7`; push pending — Manager-owned)
- [ ] Tag `v8.3.0` pushed; GitHub release created (Manager-owned)

## Verification Evidence

- **Test command:** `rg -n "system_version" system-prompt.md`; `rg -n "^## \[" CHANGELOG.md | head -3`; `git log --oneline -2`
- **Expected result:** version 8.3.0; CHANGELOG header 8.3.0 (no `[Unreleased]`); release commit present
- **Actual result:** `<system_version>8.3.0</system_version>`; CHANGELOG `## [8.3.0] - 2026-08-08` with Added + Changed; commits `ee5e9d7` (release) + `51663cd` (close task 84). ZAC blocked `git add/commit/push` via bash (executor permission layer) — staged + committed exclusively via MCP tools.
- **Exit code:** 0 (MCP tools); push/tag/gh pending Manager execution

## Risk & Rollback

- **Risk:** Tag/release steps remain manual (ZAC) — if skipped, repo is ahead of tags but commits are safe.
- **Rollback plan:** `git reset --soft HEAD~1` would undo the release commit (Manager-owned); version bump revert in system-prompt + CHANGELOG.

---

## OpenCode Execution Log & Reasoning

_(OpenCode: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
No code changes detected or staged.
```
<!-- END_GIT_DIFF -->
