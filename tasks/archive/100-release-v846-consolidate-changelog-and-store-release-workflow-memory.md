# Task 100: Release v8.4.6 — Consolidate CHANGELOG and Store Release Workflow Memory

**File:** `tasks/archive/100-release-v846-consolidate-changelog-and-store-release-workflow-memory.md`
**Source:** orchestrator
**Type:** chore
**Status:** closed

## Goal

Prepare release v8.4.6: consolidate the pending `[Unreleased]` CHANGELOG entry into the existing `[8.4.6]` section, store the future release workflow as persistent project memory (`release/release-workflow`), verify all release gates (lint, prompt sync, compile, tests), and leave `[Unreleased]` present but empty. Release publication (tag/push/GitHub release) is a separate manual Manager step after closure — the Hands perform NO tag/push/release commands. Note: the Orchestrator suggested `Type: release/maintenance`; the lint contract only accepts `bug|improvement|feature|chore|docs|refactor|security|research|infra`, so `Type: chore` is used instead (documented substitution).

## Local TODOs

- [x] **Step 1:** Discover the next task ID via the task-generator ID discovery rule and create this task file in `tasks/backlog/` using the canonical template.
- [x] **Step 2:** Move the task file to `tasks/in-progress/` via the authorized `git mv` (filesystem `mv` if untracked); update the `**File:**` header to the new path.
- [x] **Step 3:** Store the future release workflow memory — search memory for release/versioning/changelog/semver keywords, then `store_memory` namespace `release`, key `release-workflow`, `overwrite: true` with the canonical memory content.
- [x] **Step 4:** Verify the stored memory via `read_memory` (namespace `release`, key `release-workflow`); record the actual memory file path in the Execution Log.
- [x] **Step 5:** Consolidate `CHANGELOG.md` for release v8.4.6 — move the `[Unreleased]` Fixed entry (Freebuff free-tier spawn status docs hotfix) into `[8.4.6]` `### Fixed` via Parse-Then-Append (no duplicate, no wording deletion); leave `[Unreleased]` header present but empty.
- [x] **Step 6:** Add the release-preparation entry under `[8.4.6]` `### Changed` (create the category in canonical order if absent) with the specified wording.
- [x] **Step 7:** Verify CHANGELOG formatting via `lint_markdown`; fix Markdown structure and re-run if lint fails.
- [x] **Step 8:** Update the active task file with release decisions, memory storage result, CHANGELOG consolidation result, and all verification evidence (English).

## Acceptance Criteria

- [x] (a) Task file created with canonical template, correct ID 100, valid lint metadata (`Type: chore`), BEGIN/END_GIT_DIFF markers.
- [x] (b) Release workflow memory stored at namespace `release` / key `release-workflow` (file `.opencode/memory/release/release-workflow.md` or actual server path) with the exact canonical content; verified via `read_memory`.
- [x] (c) CHANGELOG `[Unreleased]` Fixed entry moved (not duplicated) into `[8.4.6]` `### Fixed`; `[Unreleased]` header present but empty; no historical wording deleted.
- [x] (d) Release-preparation entry added under `[8.4.6]` `### Changed` with the exact specified wording.
- [x] (e) `lint_markdown` passes on CHANGELOG.md; `lint_system_prompt_sync` reports in sync; py_compile exit 0; full pytest suite passes.
- [x] (f) No tag/push/GitHub release performed by the Hands (ZAC); release publication left as a separate manual Manager step.

## Verification Evidence

- **Test command:** `python3 -m py_compile scripts/prompt-build/split_system_prompt.py scripts/prompt-build/assemble_system_prompt.py mcp-lint-server/server.py` then `uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q`
- **Expected result:** py_compile exit 0; pytest all pass (exit 0); `lint_system_prompt_sync` reports `✅ system-prompt.md is in sync with prompts/`; `lint_markdown` passes on CHANGELOG.md.
- **Actual result:**
  - Task ID discovery: `find tasks/ -type f -name '*.md'` → highest ID 99 (completed/), next ID **100**; no collision in backlog/.
  - Memory storage: `store_memory(namespace=release, key=release-workflow, overwrite=true)` → stored at `.opencode/memory/release/release-workflow.md`; verified via `read_memory` (content matches canonical text exactly).
  - CHANGELOG consolidation: Freebuff free-tier spawn status docs hotfix moved from `[Unreleased]` `### Fixed` into `[8.4.6]` `### Fixed` — `grep -c "Freebuff free-tier spawn status verified and corrected"` = **1** (moved, not duplicated); `[Unreleased]` header present but empty.
  - Release-preparation entry added under `[8.4.6]` `### Changed` with the exact specified wording.
  - `lint_markdown` on CHANGELOG.md: ✅ passed.
  - `python3 -m py_compile scripts/prompt-build/split_system_prompt.py scripts/prompt-build/assemble_system_prompt.py mcp-lint-server/server.py` → exit code **0**.
  - Full pytest suite: **45 passed, 9 warnings**, exit code **0**.
  - `lint_system_prompt_sync`: `✅ system-prompt.md is in sync with prompts/`.
  - ZAC-safe release note: NO `git tag`, `git push`, or `gh release create` performed by the Hands — release publication is a separate manual Manager step after closure.
- **Exit code:** 0 (pytest)

## Risk & Rollback

- **Risk:** CHANGELOG consolidation could accidentally duplicate or delete historical wording, or leave `[Unreleased]` non-empty (release-gate violation). Mitigation: Parse-Then-Append with explicit no-duplicate check; `lint_markdown` gate on CHANGELOG.md; the `[Unreleased]` header is left present but empty per Keep a Changelog. Rollback: revert the CHANGELOG edits (working tree is uncommitted until Manager closure approval); memory file can be overwritten/deleted via the memory MCP server if needed.

---

## Execution Log & Reasoning

### Release v8.4.6 Preparation (Task 100)

**Discovered task ID:** 100 (highest existing ID was 99 in `tasks/completed/`; no collision in `tasks/backlog/` — verified via the task-generator ID discovery rule).

**Type metadata substitution (documented):** the Orchestrator suggested `Type: release/maintenance`, but the lint contract (`_check_task_file_structure` in `mcp-lint-server/server.py`) only accepts `bug|improvement|feature|chore|docs|refactor|security|research|infra`. Used `Type: chore` instead (consistent with the CHANGELOG's own `chore: close task N` convention) so the task file passes `lint_task_file`. No other metadata changed.

**Release workflow memory stored:** namespace `release`, key `release-workflow`, `overwrite=true`. Actual memory file path: `.opencode/memory/release/release-workflow.md` (confirmed by the project_memory MCP server on store and verified via `read_memory` — content matches the canonical text byte-for-byte, including frontmatter `status: active`). No prior release-workflow memory existed (search returned no matches), so no supersession was required. The memory captures: SemVer decision rules, Keep a Changelog / Parse-Then-Append rules, the empty-`[Unreleased]` rule, prompt-source rules (generated `system-prompt.md`, never hand-edit, sync verification), verification gates, ZAC-safe commit rules (no tag/push by Hands; publication is a separate manual Manager step), and the memory-rule pointer (`release/release-workflow`).

**CHANGELOG consolidation actions:**
1. Moved the `[Unreleased]` `### Fixed` bullet (Freebuff free-tier spawn status docs hotfix, 2026-08-13) into the existing `[8.4.6] - 2026-08-16` section under `### Fixed`, appending it after the QA Fix Round 4 bullet. Verified via `grep -c` that the entry appears exactly once (moved, NOT duplicated) and no historical wording was deleted.
2. Left `## [Unreleased]` header present but empty (Keep a Changelog rule: `[Unreleased]` MUST be empty after a release — this is now satisfied).
3. Added the release-preparation entry under `[8.4.6]` `### Changed` (category already existed — appended, no duplicate category header): "Release v8.4.6 preparation — consolidated the [Unreleased] docs hotfix under [8.4.6], stored persistent release workflow memory at release/release-workflow, and verified release gates. system-prompt.md version unchanged." (The `system-prompt.md version unchanged` statement is correct: this task edited no prompt source, and `lint_system_prompt_sync` confirms the generated file is in sync at 8.4.6.)

**Release verification results:**
- `lint_markdown` on CHANGELOG.md: ✅ passed.
- `python3 -m py_compile` (splitter, assembler, lint server): exit 0.
- Full pytest suite: 45 passed, exit 0.
- `lint_system_prompt_sync`: `✅ system-prompt.md is in sync with prompts/`.

**ZAC-safe release publication note:** the Hands performed NO `git tag`, `git push`, or `gh release create` in this task. Public tag/release publication (e.g. `git tag v8.4.6` + push + GitHub release) is a separate manual Manager step after task closure, per the stored release workflow memory and the Orchestrator's explicit instruction.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `44a4610db87514f11430bff958eb875f14f69c3c`
<!-- END_GIT_DIFF -->
