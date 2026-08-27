# Task 117: Remove Freebuff Completely

**File:** `tasks/completed/117-remove-freebuff-completely.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Completely remove Freebuff from the Cognitive Lead AI HQ system — delete all Freebuff-specific files, directories, agent ports, skills, documentation, configuration references, memory entries, and test assertions. Zero traces remaining in the tracked codebase.

## Manager's Notes

The Manager wants Freebuff fully dropped from the system. Every reference, every file, every configuration entry. Historical CHANGELOG entries may remain as they are immutable records, but all active/configurable Freebuff artifacts must be purged.

## Local TODOs

- [x] Inventory all Freebuff-specific files and directories for deletion
- [x] Delete `freebuff/` directory (AGENTS.global.md + agents/*.ts)
- [x] Delete `docs/freebuff-support.md`
- [x] Delete `docs/freebuff-documents.md`
- [x] Delete `.opencode/skills/freebuff-documents/` skill directory
- [x] Delete `skill-templates/freebuff-documents/` skill template
- [x] Delete `.opencode/memory/project/freebuff_vendor.md` memory entry
- [x] Clean Freebuff references from `AGENTS.md`
- [x] Clean Freebuff references from `system-prompt.md`
- [x] Clean Freebuff references from `prompts/fragments/02-role.md`
- [x] Clean Freebuff references from `prompts/fragments/10-agent_skills_registry.md`
- [x] Clean Freebuff references from `prompts/fragments/12-personas.md`
- [x] Clean Freebuff references from `prompts/fragments/14-hands_protocols.md`
- [x] Clean Freebuff references from `prompts/fragments/17-constraints.md`
- [x] Clean Freebuff references from `README.md` (Freebuff Support section, matrix, skill list)
- [x] Clean Freebuff references from `LLM.txt` (Step 7.5, verification checklist, skill count)
- [x] Clean Freebuff references from `.opencode/memory/workflows/global-install-upgrade.md`
- [x] Remove Freebuff-related test assertions from `tests/test_mcp_servers.py`
- [x] Update `system-prompt.md` version
- [x] Verify: `grep -ri freebuff` returns only CHANGELOG/history/task-archive matches
- [x] Run `pytest` and `lint_task_file` to confirm no regressions

## Acceptance Criteria

- [x] `freebuff/` directory does not exist
- [x] `docs/freebuff-support.md` does not exist
- [x] `docs/freebuff-documents.md` does not exist
- [x] `.opencode/skills/freebuff-documents/` does not exist
- [x] `skill-templates/freebuff-documents/` does not exist
- [x] `.opencode/memory/project/freebuff_vendor.md` does not exist
- [x] `grep -ri freebuff AGENTS.md system-prompt.md README.md LLM.txt prompts/ docs/ .opencode/ tests/` returns zero matches (CHANGELOG, tasks/completed/, tasks/archive/, docs/history/, docs/research/ are excluded from the gate)
- [x] `pytest` exits 0 with all tests passing (43 passed)
- [x] `lint_task_file` passes on this task file
- [x] `system-prompt.md` assembled from fragments without Freebuff references
- [x] Skill count in README/LLM.txt updated to reflect removal (31 → 30)

## Verification Evidence

- **Test command:** `grep -ri freebuff AGENTS.md system-prompt.md README.md LLM.txt prompts/ docs/ .opencode/ tests/ | grep -v CHANGELOG | grep -v tasks/completed | grep -v tasks/archive | grep -v docs/history | grep -v docs/research`
- **Expected result:** zero matches
- **Actual result:** zero matches (empty output)
- **Exit code:** 0
- **Pytest:** 43 passed, 0 failed, 8 warnings

## Definition of Done

The task is NOT done unless ALL of the following are true:

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Removing Freebuff references from system-prompt.md fragments could break the assembled prompt if fragments are interdependent
- **Rollback plan:** `git checkout` the modified files from before the task; the deleted files can be restored from git history

---

## Execution Log & Reasoning

**Step 1 — File Deletion:** Deleted 6 Freebuff-specific paths: `freebuff/` (AGENTS.global.md + 2 agent .ts ports), `docs/freebuff-support.md`, `docs/freebuff-documents.md`, `.opencode/skills/freebuff-documents/`, `skill-templates/freebuff-documents/`, `.opencode/memory/project/freebuff_vendor.md`. Verified via `ls` that all paths no longer exist.

**Step 2 — AGENTS.md Cleanup:** Removed Freebuff equivalents bullet from skills table, removed `/skill:task-generator` slash-command reference, removed entire `## Project-Specific Skill Auto-Load` section (3 edits).

**Step 3 — Prompt Fragments:** Edited 5 fragment files: `01-system_version.md` (bumped 8.6.2→8.7.0), `02-role.md` (removed Freebuff from executor list), `10-agent_skills_registry.md` (removed Freebuff slash-command reference), `12-personas.md` (removed `.agents/skills/` from Software Architect behavior), `14-hands_protocols.md` (3 edits: removed Freebuff from subagent description, removed `.agents/skills/` from discovery task template, removed Freebuff from context phase), `17-constraints.md` (removed Freebuff permission note). Fixed trailing newline on fragment 01 to maintain assembler round-trip byte-identity.

**Step 4 — system-prompt.md Reassembly:** Ran `python3 scripts/prompt-build/assemble_system_prompt.py`. Verified: version 8.7.0, zero Freebuff references, zero `/skill:` references, assembler round-trip byte-identical.

**Step 5 — Documentation:** Cleaned `README.md` (removed entire Freebuff Support section, matrix, skill count 31→30), `LLM.txt` (removed Section 7.5 entirely, skill count 31→30, removed Freebuff CLI/mcp.json checklist items), `docs/telegram-setup.md` (3 edits), `docs/workflow-upgrade-v8.4.5.md` (4 edits).

**Step 6 — Memory:** Rewrote `.opencode/memory/workflows/global-install-upgrade.md` (removed all Freebuff columns/sync steps, now OpenCode-only, skill count 30), updated `code_search_skill_sync_pattern.md` (2 copies instead of 3).

**Step 7 — Tests:** Deleted `test_freebuff_agents_have_no_model_key` and `test_system_prompt_contains_freebuff_skill_alternative` from `tests/test_mcp_servers.py`, updated docstrings in `test_system_prompt_has_no_opencode_tags` and `test_workflow_skills_have_no_opencode_execution_log`.

**Step 8 — CHANGELOG:** Added `### Removed` section under `## [Unreleased]` documenting complete Freebuff purge with full scope (files, fragments, docs, memory, tests, verification).

**Step 9 — Verification:** `grep -ri freebuff` returns zero matches outside CHANGELOG/history/archives/research. Pytest: 43 passed, 0 failed. Fixed assembler round-trip issue (fragment 01 trailing newline).

**Root cause of test failure:** Fragment `01-system_version.md` gained a trailing newline during edit. The assembler joins fragments with `\n\n`, so the fragment's trailing `\n` created an extra blank line in the assembled output, breaking the byte-identity round-trip test. Fixed by removing the trailing newline from the fragment.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `f4acea14d891c92a7e18e9e3734ab8afdffebdae`
<!-- END_GIT_DIFF -->
