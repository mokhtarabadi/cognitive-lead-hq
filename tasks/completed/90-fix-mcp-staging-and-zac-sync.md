# Task 90: Fix MCP Staging and ZAC Sync

**File:** `tasks/completed/90-fix-mcp-staging-and-zac-sync.md`
**Source:** manager
**Type:** security
**Status:** closed

## Source Context

### Variant C: Manager (`**Source:** manager`)

## Goal

Implement the F5 fix from Task 87: replace blind `git add -A .` / `git add -A tasks/` staging in `mcp-context-server/server.py` with explicit path scoping — `stage_and_inject_diff` gains a required-in-practice `modified_files` list argument and stages ONLY those files plus the task file; `commit_and_clean_task` stages ONLY the active task file. Sync `system-prompt.md` (v8.4.2, summary-phase instructions), `AGENTS.md` (end-of-task sequence), `audit-agents` skill (audit criterion), and `CHANGELOG.md` to enforce the new contract.

## Manager's Notes

- Root cause (proven live on Task 89 closure): `commit_and_clean_task`'s internal `git add -A tasks/` re-staged untracked foreign task files (86/87/88) into Task 89's closure commit even after they were explicitly unstaged beforehand.
- The new contract: the executor MUST pass every file it modified via `modified_files`; otherwise the diff table is empty and the Brain cannot review (by design — friction prevents silent contamination).
- `modified_files` is implemented with a default `[]` for backward compatibility (a missing argument yields an empty diff table rather than a hard tool error, matching the Orchestrator's reminder semantics).
- Test impact: `test_stage_and_inject_diff_with_ignored_context_reports` calls the tool with only the task file; under the new contract it must pass `modified_files=["feature.py"]` to keep its assertions meaningful (deviation from the Orchestrator's literal "pass `modified_files=[]`" — `[]` would break the test's staged-diff assertions).

## Local TODOs

- [x] Step 1: Create this task file (ID discovery → 90), move to `tasks/in-progress/` (filesystem `mv` — untracked)
- [x] Step 2: Read target files (server.py, system-prompt.md, AGENTS.md, audit-agents SKILL.md, CHANGELOG.md, tests)
- [x] Step 3: Fix `stage_and_inject_diff` — add `modified_files` param, replace `git add -A .` + reset loop with explicit `git add -- <files> + task file`
- [x] Step 4: Fix `commit_and_clean_task` — replace `git add -A tasks/` with `git add -- <task_file_path>`
- [x] Step 5: Update `system-prompt.md` — bump to 8.4.2 + update ALL summary-phase instructions that call `stage_and_inject_diff` (implementation + combined templates; note: discovery summary does NOT call it — Orchestrator said "all 3", actual = 2)
- [x] Step 6: Update `AGENTS.md` end-of-task sequence step 4 with the `modified_files` requirement
- [x] Step 7: Add the `modified_files` audit criterion to `audit-agents/SKILL.md` (top criteria list + Mode 2 list)
- [x] Step 8: Update `CHANGELOG.md` — `## [8.4.2]` with `### Fixed` entry (no duplicates)
- [x] Step 9: Syntax verification (py_compile + greps + pytest) and update the affected regression test

## Acceptance Criteria

- [x] `stage_and_inject_diff(task_file_path, modified_files)` stages ONLY `modified_files + [task_file_path]`; no `git add -A` anywhere in the function
- [x] `commit_and_clean_task` stages ONLY the active task file (no `git add -A tasks/`)
- [x] `system-prompt.md` at 8.4.2 with the new summary-phase instruction in every template that calls the tool (2 blocks)
- [x] `AGENTS.md` end-of-task sequence step 4 carries the `modified_files` requirement
- [x] `audit-agents/SKILL.md` carries the `modified_files` audit criterion
- [x] `CHANGELOG.md` has exactly one `## [8.4.2]` header with the `### Fixed` entry
- [x] `pytest` passes (updated regression test included); `py_compile` OK
- [x] Task file passes `lint_task_file`

## Verification Evidence

- **Test command:** `uv run --with pytest --with pathspec --with "mcp[cli]>=1.0,<2.0" --with pyyaml --with tree-sitter ... pytest tests/test_mcp_servers.py -q` ; `grep -n "modified_files" mcp-context-server/server.py` ; `grep -n "8.4.2" system-prompt.md` ; `lint_task_file tasks/in-progress/90-fix-mcp-staging-and-zac-sync.md`
- **Expected result:** 14+ tests pass; `modified_files` 2 matches (signature + usage); `8.4.2` 1 match; lint ✅
- **Actual result:** `14 passed, 9 warnings in 1.13s` (regression test updated to pass `modified_files=["feature.py"]`); `modified_files` at lines 472 (signature), 485 (usage) + docstring line 478; `8.4.2` exactly once (line 1 `<system_version>`); `py_compile` → ✅ Syntax OK; `grep 'git add -A'` → ✅ none left in server.py; lint → ✅ passed (run below)
- **Exit code:** 0 (pytest, py_compile, greps); 0 (lint)

## Risk & Rollback

- **Risk:** (1) Old callers that forget `modified_files` get an empty diff table — intentional friction per design, mitigated by the CRITICAL REMINDER in system-prompt and the audit criterion. (2) Regression test breakage — mitigated by updating the test to pass the modified file list. (3) CHANGELOG/version drift — mitigated by Parse-Then-Append + single grep check.
- **Rollback plan:** Restore the `git add -A .` + reset loop and `git add -A tasks/` lines from the previous commit; revert system-prompt to 8.4.1; revert AGENTS.md/audit-agents/CHANGELOG edits; re-run tests.

---

## OpenCode Execution Log & Reasoning

### What was done

1. **`mcp-context-server/server.py` — `stage_and_inject_diff`:** signature changed to `(task_file_path: str, modified_files: list[str] = [])`. The blind `git add -A .` + sensitive-file reset loop is GONE. Replacement: `files_to_stage = modified_files + [task_file_path]; git add -- <paths>`. Docstring documents the F5 rationale (cross-session contamination) and the empty-diff-table behavior when the list is omitted.
2. **`mcp-context-server/server.py` — `commit_and_clean_task`:** `git add -A tasks/` → `git add -- task_file_path` (line ~576), with a comment explaining the F5 fix. This is the exact line that re-swept tasks 86/87/88 into Task 89's closure commit.
3. **`system-prompt.md`:** `<system_version>` 8.4.1 → 8.4.2; both summary-phase instructions that invoke `stage_and_inject_diff` (implementation template line ~469, combined template line ~516) now carry the `modified_files` contract + CRITICAL REMINDER. **Deviation note:** the Orchestrator said "all 3 summary phases" — the discovery template's summary does NOT call `stage_and_inject_diff` (it only outputs the report path), so exactly 2 blocks were updated; documented in this log for the Reviewer.
4. **`AGENTS.md`:** Mandatory End-of-Task Sequence step 4 now requires the `modified_files` array (stages ONLY those files).
5. **`skill-templates/audit-agents/SKILL.md`:** new audit criterion "Explicit Staging Contract (F5)" added to BOTH Target Audit Criteria lists (top + Mode 2).
6. **`CHANGELOG.md`:** `## [8.4.2] - 2026-08-10` below `[Unreleased]` with one `### Fixed` entry (Parse-Then-Append; verified single header).
7. **`tests/test_mcp_servers.py`:** `test_stage_and_inject_diff_with_ignored_context_reports` updated to call `stage_and_inject_diff(str(task_file), modified_files=["feature.py"])`. **Deviation note:** the Orchestrator's fallback instruction said "pass `modified_files=[]` in the test mocks" — an empty list would leave `feature.py` UNSTAGED and break the test's own assertions (diff must contain feature.py). Passing the actual modified file list keeps the test meaningful under the new contract.

### Architectural reasoning

- **The staging contract shifted from "stage everything, then unstage sensitive" to "stage exactly what the agent declares".** This inverts the trust model: git-wide staging trusted the executor's environment; path-scoped staging trusts the executor's *self-reporting*, which is exactly what the Brain's review loop verifies (QA/Code Reviewer read the diff table — an empty table is a visible failure, not silent contamination).
- **Default `= []` (not required param):** a missing argument produces a tool success with an empty diff table rather than a pydantic error — this matches the Orchestrator's reminder semantics ("the diff table will be empty and your work will be lost") and keeps trivial tasks (docs-only) functioning while forcing honest reporting for code tasks.
- **Why the test passes `["feature.py"]`:** the regression test's purpose (gitignore no longer blocks staging; code change lands in the diff) is preserved by declaring the file it "modified".
- **Remaining known risk (documented, not fixed here):** `stage_and_inject_diff` still injects the diff AFTER staging the task file, so the task file itself is committed in its pre-diff state by the feature commit and re-staged by `commit_and_clean_task` step 4 — the two-commit flow is unchanged and stays reachable.
- **Global deployments:** `audit-agents` global copy at `~/.config/opencode/skills/audit-agents/SKILL.md` is NOT re-synced in this task (repo-template sync only, matching Task 85's pattern of syncing at release). Flag for the Reviewer/Manager.

### Lint & verification

- `lint_task_file tasks/in-progress/90-fix-mcp-staging-and-zac-sync.md` → ✅ (run in summary phase).
- `pytest`: 14 passed; `py_compile`: OK; greps verified (see Verification Evidence). No repair attempts needed.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `0eb5eebe90d314516e21a5c6f6da9a0fa0921c12`
<!-- END_GIT_DIFF -->