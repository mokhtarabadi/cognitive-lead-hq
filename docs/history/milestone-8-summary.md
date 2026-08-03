# Milestone 8 Summary

**Date:** 2026-08-04
**Tasks Compacted:** 4

## Source Distribution

| Source       | Count |
| ------------ | ----- |
| manager      | 3     |
| orchestrator | 1     |

## Architectural Changes

### 1. MCP Server Core Fixes (Task 78)

**Fixed orphaned commit hash bug in `commit_and_clean_task`:**

- **Root cause:** The tool captured `git rev-parse HEAD` *before* `git commit --amend`, so the hash stored in the task file pointed to a commit that became unreachable after the amend replaced it. Reflog evidence: `df48833` (referenced by Task 77) and `aa72dc7` (Task 75) are orphaned.
- **Solution:** Eliminated the amend entirely. Replaced with a **two-commit flow**:
  1. Feature commit: `git commit -m <message>` → captures hash H1
  2. Clean task file diff block with `**Factual Git Diff:** Stored in Commit Hash: H1`
  3. Closure commit: `git commit -m "chore: close task NN - <slug>"` (plain commit, no amend)
  - H1 stays permanently reachable as parent of closure commit
  - `git show <H1>` returns real code diff; no orphaned commits produced
- **Added:** `_derive_task_slug()` helper for closure commit messages; retained empty-staged safety check from Task 71.

**Fixed `stage_and_inject_diff` crash on ignored `context-reports/` directory:**

- **Root cause:** `git add . :!*.env ... :!context-reports/` negative pathspecs make git exit 1 with "paths are ignored" whenever the excluded path actually exists on disk (accumulated reports), blocking every closure.
- **Solution:** Plain `git add -A .` (respects .gitignore) + defense-in-depth `git reset -q -- <pattern>` for sensitive paths (`*.env`, `*.key`, `*.pem`, `credentials*`, `secrets*`, `context-reports/`, `.opencode/cache/`).

**Hardened idempotency guard (regex, not substring):**

- **Root cause:** Naive substring check (`if "Stored in Commit Hash:" in existing`) matched the guard's own source line in the injected diff, false-positiving and blocking legitimate closures.
- **Solution:** Regex matches exact cleaned-block structure (`<!-- BEGIN_GIT_DIFF -->` + `**Factual Git Diff:** Stored in Commit Hash: \`<hex>\`` + `<!-- END_GIT_DIFF -->`), immune to raw-diff mentions.

### 2. System Prompt Enhancement (Task 79)

**Added `<commit_lifecycle_rule>` to `<constraints>` in `system-prompt.md`:**

- Documents the two commit-producing MCP tools with distinct lifecycle semantics:
  - `custom_context_stage_and_inject_diff` (development-time): stages + injects diff, no commit
  - `custom_context_commit_and_clean_task` (closure-time): two-commit flow, stores feature hash, creates `chore: close task N` closure commit
- ZAC enforcement: OpenCode must never run `git add`/`git commit`/`git push` directly
- Enforcement hook: calling `commit_and_clean_task` before Manager approval = ZAC violation
- Previously ZAC was only in `<bash_phase>` CRITICAL RULE 2 (implementation-specific), invisible to non-implementation agents — caused Zen Router incident (Task 13) where OpenCode invoked `commit_and_clean_task` during iteration 1.

### 3. Project License (Task 69)

**Added MIT License to project root:**

- Selected MIT as the most widely adopted permissive license for documentation/framework repositories
- Allows unrestricted reuse, modification, distribution — aligns with PR-welcome community ethos
- Copyright holder: `mokhtarabadi` (matching GitHub owner), year 2026

### 4. Milestone 7 Archive & V8 Release (Task 77)

- Archived Tasks 70–76 into `docs/history/milestone-7-summary.md`
- Bumped system version to 8.0.0
- Executed Git push, tag `v8.0.0`, and GitHub release

## Files Modified

| File | Change |
| ---- | ------ |
| `mcp-context-server/server.py` | Three fixes: two-commit flow, staging defense-in-depth, regex guard; new `_derive_task_slug()` helper |
| `tests/test_mcp_servers.py` | Three regression tests: hash reachability, staging with ignored dirs, guard false-positive prevention (8/8 tests pass) |
| `system-prompt.md` | Added `<commit_lifecycle_rule>` to `<constraints>`; version bumped 8.0.0 → 8.0.1 (PATCH) |
| `CHANGELOG.md` | `[Unreleased]`: Added `### Changed` (commit lifecycle rule) and detailed `### Fixed` entries |
| `LICENSE` | New MIT license file (Task 69) |

## Criteria Met

| Task | Acceptance Criteria | Status |
| ---- | ------------------- | ------ |
| 69 | LICENSE file created with MIT text; README badge resolves | ✅ Met |
| 77 | Milestone 7 archived; version 8.0.0; GitHub release v8.0.0 created | ✅ Met |
| 78 | Stored hash reachable from HEAD; `git show <hash>` returns code diff; no amend commits; idempotency works | ✅ Met |
| 79 | `<commit_lifecycle_rule>` in `<constraints>`; version 8.0.1; CHANGELOG updated; lint passes | ✅ Met |

## Individual Task Summaries

### Task 69: Add Project License
- **Type:** feature
- **Source:** manager
- **Reasoning:** MIT License selected for documentation-only repo — permissive, community-friendly, no patent grant needed. Copyright holder matches GitHub owner. README badge now resolves.

### Task 77: Milestone 7 Archive & V8 Release
- **Type:** chore
- **Source:** orchestrator
- **Reasoning:** Archived Tasks 70–76 into milestone-7-summary.md with source distribution, architectural changes, files modified, and criteria met. Version bumped to 8.0.0. Full release sequence executed: push → tag v8.0.0 → GitHub release.

### Task 78: Fix commit_and_clean_task orphaned hash bug
- **Type:** bug
- **Source:** manager
- **Reasoning:** Amend-based flow fundamentally cannot satisfy both "stored hash == HEAD" and "no orphans." Two-commit flow is the only clean design: feature commit H1 stores hash; closure commit keeps H1 reachable. Also fixed staging crash on ignored dirs (negative pathspecs → `git add -A .` + `git reset`), and hardened idempotency guard with regex matching exact cleaned-block structure to avoid self-referential false positives.

### Task 79: Add commit_lifecycle_rule to system prompt constraints
- **Type:** improvement
- **Source:** manager
- **Reasoning:** ZAC rule was only in `<bash_phase>` (implementation-specific). Added to top-level `<constraints>` as `<commit_lifecycle_rule>` bullet documenting both MCP tools, their lifecycle semantics, two-commit flow, and enforcement hook. Version bumped 8.0.0 → 8.0.1 (PATCH).