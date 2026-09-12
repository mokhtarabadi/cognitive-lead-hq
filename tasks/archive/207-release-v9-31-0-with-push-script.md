# Task 207: Release v9.31.0 with push script

**File:** `tasks/completed/207-release-v9-31-0-with-push-script.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Mode:** autopilot-locked (manager said "use auto polit mode"; auto-closure approved)

## Goal

Cut release v9.31.0, move Unreleased entries under it, keep prompt in sync, and leave a ready push script.

## Manager's Notes

Manager asked to load memory, decisions, and release workflow, follow them, make the script ready, autopilot on, auto-closure fine. Autopilot locked. No-ferry rule applies. Past rulings used: QA-review autopilot cycle, no-ferry in autopilot, ZAC push-owned-by-manager, closure typos accepted.

## Local TODOs

- [x] Verify prompt sync, decide version, run full checks
- [x] Bump fragment version, rebuild prompt, move CHANGELOG
- [x] Write and chmod push script, lint and stage, run Brain QA and reviewer, close

## Acceptance Criteria

- [x] CHANGELOG has `## [9.31.0]` with moved Unreleased entries, Unreleased empty
- [x] Fragment version and system-prompt agree at 9.31.0, sync check passes
- [x] Full pytest suite passes with evidence recorded
- [x] `/tmp/cognitive-lead-push-release.sh` exists, executable, starts with `set -euo pipefail`, holds `VERSION="v9.31.0"`
- [x] `lint_task_file` passes, diff staged via stage tool

## Verification Evidence

- **Test command:** `uv run --with pytest --with pathspec --with pyyaml --with mcp==1.30.0 python -m pytest tests/ -q`
- **Expected result:** all tests pass, exit 0
- **Actual result:** 237 passed, 8 warnings (baseline and post-release identical)
- **Exit code:** 0
- **Sync command:** `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/sysprompt-check.md && diff -q /tmp/sysprompt-check.md system-prompt.md`
- **Sync result:** SYNC_OK, 81684 bytes, fragment and system-prompt agree at 9.31.0
- **Compile:** `python3 -m py_compile scripts/prompt-build/assemble_system_prompt.py mcp-lint-server/server.py` → COMPILE_OK
- **Script check:** `bash -n /tmp/cognitive-lead-push-release.sh` → SYNTAX_OK, executable bit set
- **Lint command:** `lint_task_file tasks/in-progress/207-release-v9-31-0-with-push-script.md`

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** branch is 57 commits ahead of origin, push may need rebase; CHANGELOG move may misplace categories.
- **Rollback plan:** reset CHANGELOG, prompt, and fragment files from git before staging; delete tag only if script created one locally.

---

## Execution Log & Reasoning

Autopilot locked per manager order. Plan: MINOR 9.31.0 since Unreleased holds Added workflow capabilities. Prompt behavior changes via prior tasks were deferred, so bump owed now. No assumptions yet.

Brain plan verdict (task_id 207, REPORT, no XML): Architect proposed MINOR 9.31.0, parse-then-append move, single fragment bump plus rebuild plus sync, ZAC no push or tag by Hands. Selected path recorded: conditional discovery first, then bump, rebuild, move, script, gates. Autopilot self-approval applied per no-ferry rule. Version source confirmed single file `prompts/fragments/01-system_version.md`. CHANGELOG duplicate Fixed merged into one. Baseline 237 passed, post-release 237 passed, sync OK, compile OK, script syntax OK.

QA verdict: QA_PASSED with cites on CHANGELOG, fragment, prompt, evidence. Reviewer round 1: APPROVED_WITH_CHANGES claiming missing Fixed header. Disputed with on-disk evidence: 9.31.0 block holds exactly one `### Fixed` at line 34, reviewer bullet at line 56 sits under it with no intervening header. Applying the hotfix would create a duplicate category, violating Parse-Then-Append. Fix rejected, re-review requested.

Reviewer round 2: technically approved, no blocking issue, keep file as is, PO review pending. Manager pre-approved auto-closure. Moving to qa, then closure.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `876bbf808ad75ebc0e335da47149f40960a879c1`
<!-- END_GIT_DIFF -->
