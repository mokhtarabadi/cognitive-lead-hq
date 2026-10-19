# Task 326: Release v9.62.0 with milestone-23 archive

**File:** `tasks/completed/326-release-v9-62-0-with-milestone-23-archive.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Cut release v9.62.0 (MINOR: new lint gates, Technical-Terms behavior, bundle hardening) with milestone-23 archive of all completed tasks, per release/release-workflow memory.

## Manager's Notes

Direct order: "make a release, load everything from memory about new release, step by step follow them". Release memory retrieved and followed: skills loaded (versioning-and-release, project-memory, verification-before-completion, task-lint, archive-tasks, task-generator), SemVer confirmed MINOR (new workflow capabilities, non-breaking), archive-on-release enforced, CHANGELOG Parse-Then-Append with empty Unreleased after release, system-prompt bump plus reassemble, full verification gates, ZAC-safe push script at /tmp/cognitive-lead-push-release.sh for manual Manager execution.

Scope: bump `prompts/fragments/01-system_version.md` 9.61.1 to 9.62.0, update `tests/test_prompt_sync.py` version pin, reassemble `system-prompt.md`, move Unreleased entries under `## [9.62.0]`, archive 31 completed tasks (284-325) with `docs/history/milestone-23-summary.md` via archive-tasks skill, generate push script, run all gates.

## Local TODOs

- [x] Archive completed tasks with milestone-23 summary (archive-tasks skill)
- [x] Bump system version fragment and reassemble prompt
- [x] Move CHANGELOG Unreleased entries under 9.62.0 header
- [x] Update version pin in tests and run full verification gates
- [x] Generate push script at /tmp/cognitive-lead-push-release.sh
- [x] Verify functionality

## Acceptance Criteria

- [x] `tasks/completed/` empty after archive; `docs/history/milestone-23-summary.md` exists; sources in `tasks/archive/`
- [x] `system-prompt.md` carries 9.62.0, sync green, byte-identical rebuild
- [x] `CHANGELOG.md` has `## [9.62.0]` with all entries; `## [Unreleased]` empty
- [x] Push script exists at /tmp/cognitive-lead-push-release.sh, executable, starts with `set -euo pipefail`, never executed by Hands
- [x] All verification gates green (lint_task_file, lint_markdown, lint_system_prompt_sync, py_compile, full pytest, check_docs_sync.py)

## Verification Evidence

- **Test command:** rtk test uv run tests/test_prompt_sync.py -q
- **Expected result:** all prompt sync checks pass with version 9.62.0
- **Actual result:** exit 0, 14 checks pass, byte-identical rebuild confirmed
- **Exit code:** 0
- **Test command:** cd mcp-context-server && uv run --with pytest python -m pytest ../tests/test_bundle_tasks.py -q
- **Expected result:** 18 passed
- **Actual result:** exit 0, 18 passed
- **Exit code:** 0
- **Test command:** ls tasks/completed/ | wc -l; ls tasks/archive/ | wc -l; ls -l docs/history/milestone-23-summary.md
- **Expected result:** completed 0, archive grown by 31, summary exists
- **Actual result:** completed 0, archive 318 files, milestone-23-summary.md present (4763 bytes)
- **Exit code:** 0
- **Test command:** lint_task_file (task) + lint_markdown (01-system_version, CHANGELOG, milestone-23-summary) + lint_system_prompt_sync
- **Expected result:** all lint tools pass
- **Actual result:** all five lint calls pass
- **Exit code:** 0
- **Test command:** ls -l + head -2 + bash -n /tmp/cognitive-lead-push-release.sh (never executed)
- **Expected result:** executable, strict-mode header, syntax valid
- **Actual result:** -rwxrwxr-x, #!/usr/bin/env bash + set -euo pipefail, bash -n exit 0
- **Exit code:** 0
- **Test command:** python3 -m py_compile (6 files) + python3 scripts/check_docs_sync.py
- **Expected result:** both exit 0
- **Actual result:** PY_OK, docs-sync OK
- **Exit code:** 0
- **Test command:** full suite minus test_mcp_servers via context-server locked env
- **Expected result:** all green; test_mcp_servers excluded (53 environmental + 1 pre-existing split failure, also failing on pristine HEAD)
- **Actual result:** exit 0, 440 passed
- **Exit code:** 0
- **Stack-skill binding:** root=. markers=[package.json, go.mod, pyproject.toml server, build.gradle.kts] matched=[] reason=no app stack skill matches release plus MCP verification

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Archiving 31 tasks in one move; a missed file breaks traceability.
- **Rollback plan:** Revert via git (no commits until closure approval); re-run ID discovery if needed. Never purge archive until META/release reaches completed.

---

## Execution Log & Reasoning

Seat Check: release procedure, single domain, requested Software Architect; skipped Designer (no user-visible surface) and Senior Programmer (mechanical file ops spelled out in XML). Brainstorm: not required — procedure fully specified by release-workflow memory plus Manager order, reversible until closure.
Fed-context: `prompts/fragments/01-system_version.md:1` (9.61.1 → 9.62.0), `tests/test_prompt_sync.py:47` (pin updated), `system-prompt.md:1` (assembled 9.62.0), `CHANGELOG.md:7-9` (Unreleased empty, 9.62.0 header 2026-10-19), `docs/history/milestone-23-summary.md` (new, 31 tasks), `/tmp/cognitive-lead-push-release.sh` (executable, syntax valid, never executed).
Archive: 31 files git-moved tasks/completed/ → tasks/archive/, completed/ verified empty. Sibling docs inspected: prompts/fragments, tests, scripts, docs READMEs/DECISIONS carry no contract change for a version bump — logged no-change. test_mcp_servers excluded from blocking gates: 53 environmental failures (missing pathspec/yaml in lint env) plus 1 split round-trip failure, all reproduced on pristine HEAD worktree. Assumption A1: MINOR (not PATCH) because new lint gates plus Technical-Terms behavior plus bundle hardening are new workflow capabilities, non-breaking.
Manager accept 2026-10-19: 'Approved For closure' — PO_REVIEW_PENDING cleared, closing per protocol.
Hotfix (QA_REJECTED evidence gap): recorded archive counts (completed 0, archive 318), lint triple green via MCP tools, push script checks (executable, strict header, syntax valid, never executed), py_compile plus docs-sync green, full suite 440 green; DoD boxes checked against this evidence. No release logic redone.
Re-QA: QA_PASSED — archive proven, pins consistent, CHANGELOG correct, lint triple green, script plus docs gates green, 440 suite green with justified exclusion, DoD closed. Re-review: APPROVED with PO_REVIEW_PENDING, no blocking issues, no follow-ups.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `f6d0c64977811bfe0110e0a369c656808a5c39c5`
<!-- END_GIT_DIFF -->
