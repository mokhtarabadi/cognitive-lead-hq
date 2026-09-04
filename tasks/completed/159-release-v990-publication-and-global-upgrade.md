# Task 159: Release v9.9.0 publication and global install upgrade

**File:** `tasks/qa/159-release-v990-publication-and-global-upgrade.md`
**Source:** manager
**Type:** feature
**Status:** open

## Goal

Publish v9.9.0 (missing tag + GitHub Release via manual push script) and upgrade global installation per memories, with zero version bump.

## Manager's Notes

Manager requested: load memory about release then make a release then load memory about system upgrade then upgrade our installation. Approved with follow memory.

Requirements:
- Follow `release/release-workflow` and `workflows/global-install-upgrade` memories (skills versioning-and-release, project-memory, verification-before-completion, task-lint already loaded; SemVer; Keep a Changelog Parse-Then-Append; system-prompt sync; verification gates; ZAC-safe staging).
- Current state at task creation: CHANGELOG [Unreleased] empty, [9.9.0] 2026-09-04 released, fragment 01-system_version.md 9.9.0, tree clean on main, tag v9.9.0 missing (latest tag v9.8.0). No new code changes to release, so this is a publication release, not a bump. system-prompt.md version unchanged (still 9.9.0).
- Generate `/tmp/cognitive-lead-push-release.sh` for VERSION v9.9.0 (set -euo pipefail, clean-tree + gh auth check, annotated tag if missing, push commits + tags, gh release create --generate-notes, verification). Manager runs manually. ZAC: Hands never execute push/tag/gh release.
- Upgrade global installation (drift audit, copy drifted, re-verify, smoke) including Telegram MCP fork overlay per memory.
- Verification gates before staging: lint_task_file, lint_markdown, lint_system_prompt_sync, py_compile, pytest.

## Local TODOs

- [x] Load and follow release + upgrade memories with required skills
- [x] Confirm SemVer decision (publication of v9.9.0, no bump) and CHANGELOG state
- [x] Run verification gates and record evidence
- [x] Generate /tmp push script for v9.9.0 and document in AC + CHANGELOG
- [x] Audit and upgrade global installation per workflow memory
- [ ] Stage via custom_context_stage_and_inject_diff and QA transition

## Acceptance Criteria

- [x] v9.9.0 publication ready: tag v9.9.0 defined in push script, CHANGELOG [Unreleased] empty, [9.9.0] documents push script, system-prompt.md version unchanged (still 9.9.0)
- [x] Push script at /tmp/cognitive-lead-push-release.sh with set -euo pipefail, VERSION v9.9.0, tag-if-missing, push commits + tags, gh release create logic, executable
- [x] Global installation upgraded and re-verified with zero unexpected drift (except expected opencode.json relative vs absolute)
- [ ] Verification gates pass (lint_task_file, lint_markdown, lint_system_prompt_sync, py_compile, pytest)
- [x] ZAC respected (no direct git add/commit/push/tag/gh release create by Hands)

## Verification Evidence

- **Test command:** lint_task_file tasks/in-progress/159-*.md; lint_markdown CHANGELOG.md; lint_system_prompt_sync; python3 -m py_compile mcp-context-server/server.py mcp-memory-server/server.py mcp-lint-server/server.py scripts/prompt-build/assemble_system_prompt.py; uv run ... pytest tests/test_mcp_servers.py -q; uv run ... pytest tests/ -q; bash -n /tmp/cognitive-lead-push-release.sh; drift diffs (repo vs ~/.config/opencode); opencode mcp list; telegram fork clone + diff + triage
- **Expected result:** all gates exit 0, sync verified, push script syntax OK, drift clean except expected opencode.json
- **Actual result:** lint_task_file PASS; lint_markdown CHANGELOG PASS; lint_system_prompt_sync IN SYNC; py_compile OK (4 files); test_mcp_servers 47 passed + 1 FAILED (test_system_prompt_split_assemble_round_trip: splitter expects retired <decision_logging_mandate> removed Task 151, pre-existing); tests/ collection ERROR (test_bundle_tasks.py imports retired scripts/bundle-tasks.py removed Task 155, pre-existing); bash -n push script OK; drift audit pre-upgrade system-prompt 9.8.0 vs repo 9.9.0 only, post-copy re-verify CLEAN except expected opencode.json relative vs absolute; tui.json in sync; goal plugins OK; lint tool present; opencode mcp list 4 connected (custom_context, project_memory, lint, blowsh), telegram timed out by design (live holder lock, diagnostic refused to avoid AuthKeyDuplicatedError); telegram fork diff vs fork CLEAN (only .pytest_cache/data artefacts), upstream origin/main ahead 4 commits (fbc4adc, ff09e6c, 1c2744f, 6936343) — fork sync needs Manager push, out of ZAC scope. AC4 left unchecked truthfully due to 2 pre-existing test drifts; no new code changed (CHANGELOG 1 line + task only) so no new regression.
- **Exit code:** mixed (0 for lint/sync/py_compile/push-script/drift; 1 for pytest full suite pre-existing + telegram diagnostic lock-refusal by design)

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Tag/push duplicates if v9.9.0 already published remotely; global copy overwrites local fixes
- **Rollback plan:** Push script is tag-if-missing + view-before-create (idempotent); global upgrade re-verified by diff, backup /tmp/opencode/telegram-backup on fork overlay; rollback via git tag -d + global re-copy from repo

---

## Execution Log & Reasoning

- SemVer decision: publication of existing v9.9.0, no bump. Rationale: [Unreleased] empty, fragment 9.9.0, tree clean, tag v9.9.0 missing. Bumping to 9.9.1 for zero changes would be empty release.
- CHANGELOG Parse-Then-Append: appended 1 bullet under existing [9.9.0] Added (no new headers), states push script path + system-prompt.md version unchanged (still 9.9.0). [Unreleased] left empty.
- Push script /tmp/cognitive-lead-push-release.sh: set -euo pipefail, repo-root detect, VERSION v9.9.0, branch detect, clean-tree + gh auth gates, tag-if-missing, push branch + tags, view-before-create release with --generate-notes, ls-remote + release view verification. chmod +x, bash -n OK. Documented in AC + CHANGELOG. Manager runs manually (ZAC).
- Global upgrade: pre-audit only system-prompt drift (global 9.8.0 75813B vs repo 9.9.0 75821B); MCP/agents/shell/skills clean; opencode.json expected relative-vs-absolute shape OK (project 3 core relative, global 5 absolute + blowsh/telegram); tui.json + goal plugins OK. Copied system-prompt.md to global, re-verify clean. opencode mcp list 4/5 connected; telegram timeout is live-holder lock (triage refused second connect to avoid AuthKeyDuplicatedError — by design). Telegram fork vs fork clean (only .pytest_cache/data); upstream ahead 4 commits needs fork push (Manager scope, not Hands/ZAC). No global opencode.json blind copy.
- Pre-existing test drift (not introduced, tree was clean at start): tests/test_bundle_tasks.py collects retired scripts/bundle-tasks.py (Task 155 removal); test_system_prompt_split_assemble_round_trip expects retired <decision_logging_mandate> (Task 151 removal). Recorded truthfully; AC4/DoD-build left unchecked. Follow-up: backlog test-repair tasks for splitter + bundle tests.
- ZAC: no git add/commit/push/tag/gh release executed. Staging only via MCP tool next.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 0d52199..0cda841 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -12,6 +12,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Deprecated-Section Purge rule in `audit-agents` skill (Task 158):** Added Deprecated-Section Purge rule to automatically strip legacy `## Manager Decisions` and `## Admin Decision` sections during audits.
 - **Standardized 1-click prompt fences + coaching upgrades (Task 158 extension):** Wrapped all 10 `user-prompts/` payloads in quad-backtick fences for 1-click copying; elevated `founder-coaching-chat.md` to an elite executive-coach persona (Campbell/Grove/Mochary lenses: Bottleneck Diagnosis, Energy & Leverage Audits, Socratic Decision Challenges) and `daily-english-coach-chat.md` to a high-impact fluency partner for high-stakes founder communication.
+- **Release publication push script (Task 159):** Added manual release push script at `/tmp/cognitive-lead-push-release.sh` for `v9.9.0` (`set -euo pipefail`, clean-tree + `gh auth status` checks, annotated tag if missing, `git push origin main` + `git push origin --tags`, `gh release create v9.9.0 --generate-notes`). system-prompt.md version unchanged (still 9.9.0).
 
 ### Changed
```
<!-- END_GIT_DIFF -->
