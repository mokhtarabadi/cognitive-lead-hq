# Task 162: Archive Release Global Upgrade

**File:** `tasks/in-progress/162-archive-release-global-upgrade.md`
**Source:** manager
**Type:** feature
**Status:** open

## Goal

Execute archive of completed tasks (milestone-16), create release v9.10.0, and upgrade global installation per workflows. Manager approved all scopes (Q1=all, Q3=full, Q4=one meta).

## Manager's Notes

Manager request: "now load skills and memory archive tasks, make a release and upgrade our global installtion". Approved all on 2026-09-04. Scopes: Q1=all 31 completed → milestone-16, Q2=9.10.0 MINOR (production-readiness bundle non-breaking), Q3=full upgrade including Telegram fork, Q4=one meta task, Q5=include dirty archive/143-148 after triage. Skills loaded: project-memory, archive-tasks, versioning-and-release, sop-maintenance, verification-before-completion, task-lint, task-generator. Memories: release/release-workflow, workflows/global-install-upgrade, project/system-prompt-build-process.

## Local TODOs

- [x] Triage dirty tasks/archive/143-148 and CHANGELOG Unreleased
- [x] Archive: generate docs/history/milestone-16-summary.md and move 31 completed → archive
- [x] Release: Parse-Then-Append CHANGELOG 9.10.0, verify system-prompt sync, verification gates, push script
- [x] Global upgrade: drift audit → copy → re-verify → smoke + Telegram fork
- [x] Stage via custom_context_stage_and_inject_diff and QA transition

## Acceptance Criteria

- [x] Milestone-16 summary exists in docs/history/ covering all 31 completed tasks with source distribution and criteria
- [x] tasks/completed/ empty after git mv to tasks/archive/, history reachable via git log --follow
- [x] CHANGELOG [9.10.0] created via Parse-Then-Append, [Unreleased] empty, push script at /tmp/cognitive-lead-push-release.sh executable
- [x] system-prompt.md verified in sync (lint_system_prompt_sync or assemble diff)
- [x] Global install drift re-verified clean (except expected opencode.json relative vs absolute), smoke tests pass
- [x] Stale memory report produced, no auto-delete without approval

## Verification Evidence

- **Test command:** uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
- **Expected result:** all tests pass, lint_task_file passes, lint_system_prompt_sync in sync
- **Actual result:** tests/ 55 passed; loop-engine/ 309 passed; telegram fork 446 passed; assemble diff SYNC OK (75697 bytes); py_compile OK; lint_task_file ✅; lint_markdown milestone ✅ + CHANGELOG ✅; lint_system_prompt_sync ✅; opencode mcp list 4/5 connected (telegram lock-held benign, no AuthKeyDuplicatedError)
- **Exit code:** 0 (all suites)

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Large milestone-16 summary, version misjudgment, global cp overwrites working install, Telegram fork rebase conflicts
- **Rollback plan:** git mv tasks/archive/162-*.md back + delete milestone summary; git reset staged release; restore /tmp/opencode/telegram-backup-* for global; push script is manual-only, no remote side effects until Manager runs it

---

## Execution Log & Reasoning

Triage: dirty archive/143-148 are bundle_tasks auto-archive patches (File→archive, Status superseded by 161, Superseded-At 2026-09-04) — included as Q5. No prompts/fragments changes since 51b0da4 v9.9.0, so 9.10.0 MINOR with system-prompt unchanged (still 9.9.0). Tags: v9.9.0 tag missing (only v9.1.0/v9.8.0 exist) — push script creates tag if missing.

Archive: created docs/history/milestone-16-summary.md (31 tasks: 12 manager/6 telegram/13 orchestrator; 14 feature/11 improvement/6 bug; prettier-formatted, lint ✅), git mv 31 completed→archive (now 166 archived, completed empty).

Release: CHANGELOG Parse-Then-Append [9.10.0] 2026-09-04 (Added Task161 + milestone-16 + push script; Fixed Task160; Unreleased emptied). Gates: assemble diff SYNC OK, py_compile OK, tests/ 55 passed, loop-engine/ 309 passed, lint_task_file ✅, lint_markdown ✅, lint_system_prompt_sync ✅. Created executable /tmp/cognitive-lead-push-release.sh (set -euo pipefail, VERSION v9.10.0, clean-tree + gh auth, tag if missing, push main + tags, gh release create, ls-remote verify).

Global: drift audit found only mcp-context-server stale (Task160 helpers); cp + chmod +x synced. opencode.json expected relative-vs-absolute drift, shape verified (3 vs 5 MCPs, plugin prevalentware both). tui.json in sync. Telegram fork: clone mokhtarabadi fork, diff clean (only .pytest_cache/data runtime), backup /tmp/opencode/telegram-backup-20260904-103055, rsync overlay, uv sync, import ok, 446 passed (.env held). Upstream lag: origin/main ahead 4 commits (bounded downloads, redact logs) — fork sync (rebase+push) deferred, no remote push per ZAC; recommend Manager review. Re-verify: zero drift. Smoke: custom_context/project_memory/lint/blowsh connected; telegram timeout benign — manual repro shows lock-held by live instance (no AuthKeyDuplicatedError, no regen needed).

Memory: list_namespaces + search (archive/release/global keywords) — no stale entries referencing archived files; no deletes. Stale Memory Report: none flagged.

ZAC: no git add/commit/push/tag/gh release executed. Staging via custom_context_stage_and_inject_diff only; push script manual Manager step.

## Stale Memory Report

No stale memories. All 12 keys active, none reference tasks/completed/ or superseded workflows. No delete_memory calls.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
