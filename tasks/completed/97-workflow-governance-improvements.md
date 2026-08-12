# Task 97: Workflow Governance Improvements

**File:** `tasks/completed/97-workflow-governance-improvements.md`
**Source:** orchestrator
**Type:** improvement
**Status:** closed

## Goal

Implement the approved workflow-governance improvements: explicit Definition of Done in task templates, duplicate-ID/path-drift lint guards, a non-blocking distribution/growth signal in the Orchestrator system prompt, and telegram-issue-sync task-creation alignment with task-generator.

## Acceptance Criteria

- [x] `skill-templates/task-generator/SKILL.md` uses the integer-safe ID discovery command, has a Duplicate ID Check, and a `## Definition of Done` block in both single-phase and multi-phase templates.
- [x] `mcp-lint-server/server.py` `_check_task_file_structure` detects `**File:**` header vs actual path mismatches.
- [x] `tests/test_mcp_servers.py` has a fail-first `test_lint_task_file_path_mismatch` and the existing logic test matches header paths.
- [x] `system-prompt.md` gains the non-blocking distribution/growth rule (verbatim) and the `<system_version>` is incremented per AGENTS.md.
- [x] `skill-templates/telegram-issue-sync/SKILL.md` mandates mirroring task-generator exactly for task creation.
- [x] Full test suite passes (14+ tests, exit 0); lint + prettier pass.

## Verification Evidence

- **Test command:** `uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q` ; `npx prettier --write "skill-templates/task-generator/SKILL.md" "skill-templates/telegram-issue-sync/SKILL.md" "system-prompt.md" "tasks/in-progress/97-workflow-governance-improvements.md" "CHANGELOG.md"`
- **Expected result:** 15 tests pass (14 existing + new `test_lint_task_file_path_mismatch`), exit code 0; prettier clean.
- **Actual result:** **17 passed, exit 0** after QA round 3 (14 original + `test_lint_task_file_path_mismatch` + `test_lint_task_file_missing_file_header` + `test_lint_task_file_absolute_path_matches_relative_header`); prettier exit 0; `python3 -m py_compile` OK on both Python files.
- **Exit code:** 0 for all commands

## Definition of Done

The task is NOT done unless ALL of the following are true:

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** (1) Path-mismatch guard false-positives on legitimately moved task files — mitigated by normalizing whitespace/backticks and comparing only after the move. (2) The pre-existing duplicate task ID `56` in `tasks/archive/` would trip the new duplicate-ID check — archived tasks are historical records and are NOT renamed (noted, not fixed). (3) `system-prompt.md` version drift — mitigated by incrementing `<system_version>` in the same edit.
- **Rollback plan:** revert the four SKILL/system-prompt edits from the feature commit; revert `mcp-lint-server/server.py` + `tests/test_mcp_servers.py`; remove the task file.

---

## Phase 1: Task-Generator Definition of Done + ID Robustness

### Local TODOs

- [x] Replace ID discovery command with integer-safe `sort -n | tail -1` version (fallback `01`).
- [x] Add Duplicate ID Check after the duplicate-title check.
- [x] Add `## Definition of Done` section to both single-phase and multi-phase templates.

## Phase 2: Lint Server Path/ID Guards

### Local TODOs

- [x] Add path-consistency check to `_check_task_file_structure` in `mcp-lint-server/server.py`.
- [x] Keep existing ID-match logic unchanged.
- [x] Update `test_lint_task_file_logic` to match header paths.
- [x] Add fail-first `test_lint_task_file_path_mismatch`.

## Phase 3: Non-Blocking Distribution/Growth Signal

### Local TODOs

- [x] Add the distribution/growth rule verbatim to the Orchestrator behavior section of `system-prompt.md`.
- [x] Increment `<system_version>` at the top of `system-prompt.md`.
- [x] Do NOT add the rule to OpenCode agent files.

## Phase 4: Telegram Sync Alignment with Task Generator

### Local TODOs

- [x] Add the mirror-mandate to the task-creation workflow of `skill-templates/telegram-issue-sync/SKILL.md`.
- [x] Replace any divergent ID strategy/template with references to task-generator.

## OpenCode Execution Log & Reasoning

**Phase 0 — Task file creation:** ID discovery returned **97** (highest existing = 96). Note: the pre-existing archive contains a duplicate numeric ID `56` (two historical task files, IDs 56-integrate-multi-agent-brainstorming-protocol and 56-v6-9-0-system-prompt-refinement). This is exactly the drift the new duplicate-ID guard targets; archived records are historical and were NOT renamed. Task file created with canonical multi-phase template (`Source: orchestrator`, `Type: improvement`).

**Phase 1 — task-generator (SKILL.md):** (1) Confirmed the integer-safe ID discovery (`sort -n | tail -1` + `awk` fallback `01`) was already present — verified, no change needed. (2) Added the **Duplicate ID Check** (`find ... | grep -Eo '^[0-9]+' | sort | uniq -d`) after the existing duplicate-title check, with HALT semantics and an explicit note that archive duplicates are never auto-renamed. (3) Added a **`## Definition of Done`** block (4 unconditional checks: Build/Test/Lint exit 0, `lint_task_file` passes, CHANGELOG Parse-Then-Append, verification-before-completion evidence) to BOTH the single-phase and multi-phase templates.

**Phase 2 — lint server path guard + tests:** Added a path-drift check to `_check_task_file_structure` in `mcp-lint-server/server.py` (step 1.5, after the title-number check): parses the `**File:**` header value, normalizes whitespace/backticks, compares against the actual `file_path`, and appends `"File path mismatch: header says '<header>' but actual path is '<actual>'."` on mismatch. Existing ID-match logic untouched; duplicate-ID detection intentionally stays in task-generator. Tests: updated `test_lint_task_file_logic` and `test_lint_task_file_missing_sections` to pass `tasks/backlog/99-test.md` (matching the header path), and added the fail-first `test_lint_task_file_path_mismatch` (header `tasks/backlog/99-test.md` vs actual `tasks/in-progress/99-test.md` → flags `File path mismatch`; matching path → no flag).

**Phase 3 — system-prompt distribution/growth signal:** Added rule as workflow step 10 in `<execution_workflow>` verbatim ("If the last 5 closed tasks contain none classified as business, marketing, growth, or analytics, the Orchestrator MUST emit a short non-blocking reminder plus 2-3 distribution/growth suggestions. The Orchestrator is FORBIDDEN from auto-creating tasks from these suggestions."). Per AGENTS.md's mandatory rule for `system-prompt.md` edits, `<system_version>` was incremented **8.4.3 → 8.4.4**, the active task file is updated, and the CHANGELOG entry below logs the change. The rule stays in the Orchestrator layer only — no OpenCode agent files were touched.

**Phase 4 — telegram-issue-sync alignment:** Added the **TASK-GENERATOR MIRROR MANDATE** at the top of the Phase 3 task-creation workflow: task creation MUST mirror task-generator exactly (same ID discovery, duplicate-title check, duplicate-ID check, collision check, canonical template, `## Definition of Done`). Added a new step 0 running those mirror checks (duplicate-title, duplicate-ID, collision `ls tasks/backlog/${NEXT_ID}-*.md`) with HALT semantics. The workflow already used the integer-safe ID command and referenced task-generator as the single template source — confirmed, no divergent logic to replace.

**Bash verification:** prettier exit 0; `uv run` pytest with full deps → **15 passed, exit 0** (the new `test_lint_task_file_path_mismatch` included). `git mv` for the new untracked task file was not applicable (file not yet in the index), so a plain `mv` was used and the `**File:**` header updated to `tasks/in-progress/` — the new path-drift guard catches stale headers exactly as designed.

**QA fix loop entry (2026-08-13):** the QA Engineer identified that the newly added duplicate-ID check scanned ALL of `tasks/` (including `tasks/archive/`), which would HALT task creation forever on the pre-existing historical archive duplicate ID `56`. Four fixes applied:

1. **task-generator duplicate-ID check corrected** — now scans only the ACTIVE Kanban directories (`tasks/backlog tasks/in-progress tasks/qa tasks/completed`), and the note was replaced with the exact archive policy: "Archive is a historical record and MUST NOT be included in the blocking duplicate-ID check. If archive duplicates are discovered separately, report them as a warning only, never HALT task creation."
2. **telegram-issue-sync mirror updated** — the same corrected active-Kanban command and archive note applied in the step-0 mirror checks; the mirror mandate now references the corrected command.
3. **Task file gained the mandatory `## Definition of Done` block** (4 unconditional checks, exact single-phase template wording); all four marked `[x]` after bash verification (tests exit 0, `lint_task_file` passing, CHANGELOG Parse-Then-Append done, verification evidence recorded).
4. **Lint server missing-header guard** — `_check_task_file_structure` now appends `"Missing `**File:**` metadata field."` when the header regex finds nothing, preserving the existing path-mismatch behavior for present-but-mismatched headers; existing ID-match logic untouched. Added fail-first `test_lint_task_file_missing_file_header` (all sections present, no `**File:**` line → flags missing header, no spurious path mismatch).

**QA verification:** `grep -n "find tasks/"` on both skills → the two remaining occurrences are the ID-discovery commands (intentionally repo-wide for highest-ID lookup); the duplicate-ID checks both scan active Kanban dirs only. Prettier exit 0; pytest → **16 passed, exit 0** (14 original + path-mismatch + missing-header). No new CHANGELOG bullet was created; the existing Task 97 entry remains accurate.

**Second QA fix loop entry (2026-08-13):** the QA Engineer identified an absolute-vs-relative path comparison defect in the path-drift guard: `lint_task_file` explicitly accepts absolute OR relative paths, so an absolute actual path (`/repo/tasks/in-progress/97-x.md`) was falsely flagged against a relative header (`tasks/in-progress/97-x.md`) even though both resolve to the same file. One fix applied:

1. **`mcp-lint-server/server.py`** — the exact-string comparison `if header_path != actual_path:` was replaced with a resolved-absolute comparison `if Path(header_path).resolve() != Path(file_path).resolve():`. This collapses relative components, `..`, and symlinks so equivalent spellings of the same file match, while genuinely stale headers (different file → different resolved path) are still caught. The missing-header branch and the existing ID-match logic were left exactly as-is.
2. **`tests/test_mcp_servers.py`** — added fail-first `test_lint_task_file_absolute_path_matches_relative_header`: relative header `tasks/backlog/99-test.md` + computed `Path(...).resolve()` absolute path → no `File path mismatch`; sanity check that a genuinely different resolved path is still flagged.

**QA verification (round 3):** `grep` confirms `Path(header_path).resolve()` / `Path(file_path).resolve()` in the guard; `python3 -m py_compile` OK; prettier exit 0; pytest → **17 passed, exit 0**. The `## Definition of Done` block remains present with all four items marked `[x]` per final evidence. No new CHANGELOG bullet; the existing Task 97 entry remains accurate._

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `c9e29dfc427609310a9ca09204ace7d7ff1463ad`
<!-- END_GIT_DIFF -->
