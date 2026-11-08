# Task 0353: Lint path-drift comparison resolves against the wrong root

**File:** `tasks/completed/0353-lint-path-drift-root-resolution.md`
**Source:** manager
**Type:** bug
**Status:** closed
**Finished:** 2026-10-27T04:15:02Z
**Submitted:** 2026-10-26T19:57:46Z
**Estimate:** 1h
**Deadline:** 2026-10-26
**Started:** 2026-10-26T19:53:38Z

## Goal

Make the lint server's `**File:**` path-drift guard compare the header and the real file against the caller's project root, so an absolute path call and the batch linter stop reporting a false `File path mismatch` for every task file.

## Manager's Notes

> Q1, unrelated: `lint_task_file` reports a false "File path mismatch" when called with an absolute path, because it resolves the header against the MCP server's CWD instead of `project_root` — want a task for that?

> Task and impl it

## Root cause

`_check_task_file_structure` compares `Path(header_path).resolve()` with `Path(file_path).resolve()`. Both resolve against the lint server process CWD, not the `project_root` the tool was given. A relative header (`tasks/qa/foo.md`) and an absolute actual path (`/repo/tasks/qa/foo.md`) never meet, so the guard fires on a correct file.

Worse than the report: `lint_all_tasks` passes `str(md_file)` (absolute) for every file while headers are normally relative, so the batch linter reports one false mismatch per task. Live proof before the fix: `lint_all_tasks` on this repo returned `Scanned 5 task files. Found 5 total issues`, one per file, all path mismatches.

## Local TODOs

- [x] Fail-first test: absolute path outside the test CWD plus a relative header, resolved against an explicit root, must not flag
- [x] Fail-first test: `lint_all_tasks` on a temp project root with a relative header reports zero issues
- [x] Add a `root` parameter to `_check_task_file_structure` and resolve both sides against it
- [x] Thread `workspace_root` from `lint_task_file` and `lint_all_tasks`
- [x] Living docs (`mcp-lint-server/README.md`, `DECISIONS.md`) and CHANGELOG
- [x] Full suite + `lint_task_file`

## Acceptance Criteria

- [x] `_check_task_file_structure` resolves a relative header against the supplied root and the actual path against the same root; an absolute path under that root matches its relative header.
- [x] A genuinely stale header (different Kanban lane) is still reported as a mismatch.
- [x] `lint_task_file` and `lint_all_tasks` pass the resolved project root into the guard, so neither depends on the server process CWD.
- [x] Passing an absolute path returns the same verdict as passing the equivalent relative path.
- [x] Regression tests cover both the pure helper and `lint_all_tasks`.
- [x] README decision note + CHANGELOG entry, suite green, `lint_task_file` green.

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/ -q`
- **Expected result:** full suite green including the new lint regression tests
- **Actual result:** both new tests failed red first (`test_lint_task_file_resolves_paths_against_project_root`, `test_lint_all_tasks_accepts_relative_file_header`), then `tests/test_mcp_servers.py` went 89 passed and the full suite `737 passed in 58.47s`. Live module call after the fix: `Scanned 6 task files. Found 0 total issues` against this repo (before the fix the batch reported one false mismatch per file, proved live with `Scanned 5 task files. Found 5 total issues`). The same call against the synced global copy returns the same clean report; `cmp` confirms the global `mcp-lint-server/server.py` is byte-identical to the repo.
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** a root-relative resolution could accept a header that points at a different real file when the caller passes a root that is not the file's ancestor; mitigated by resolving the actual path against the same root and keeping the lane-mismatch test.
- **Risk:** the running `mcp-lint` singleton keeps the old code until restarted; the fix is verified by test import and the restart stays with the Manager.
- **Rollback:** drop the `root` parameter and the threading, restoring CWD-based comparison.

---

## Execution Log & Reasoning

**Assessment of the reported fragment.** Real, and bigger than the report. The guard compared `Path(header).resolve()` with `Path(file_path).resolve()`, so both sides anchored to the lint server process CWD — and that process is a singleton started from its install directory. Any absolute call path therefore never met a relative `**File:**` header. The report named the `lint_task_file` symptom; the batch tool was worse: `lint_all_tasks` hands the guard absolute paths for every file, so it flagged one file per task. Live proof before the change: `Scanned 5 task files. Found 5 total issues`, one per file, all path mismatches — a clean batch run was impossible by construction.

**Seat Check.** Domains: MCP lint server path resolution, one pure helper plus two call sites. Trigger words in TITLE+BODY: none of the mapped sets fired (`schema|contract|migration|quota|index`, `layout|dialog|sheet|…`, `flaky|race|deadlock|silent-fail|performance`), stated explicitly. Seats requested: Senior Programmer by implementation duty. Skipped: Software Architect (no schema or cross-service contract changes — one helper signature), UI/UX Designer (no user-visible surface), QA/Reviewer (later stages). Brainstorm: not required — single-function bug fix, reversible, no cross-disciplinary ambiguity.

**Planning gate.** The Manager's own words are the plan: the Q1 fragment names the cause (header resolved against the server CWD instead of `project_root`) and the order is "Task and impl it". No separate Brain planning round was needed; the fix follows those words exactly.

**Fix.** New `_resolve_task_reference(path_str, root)` resolves a path against the caller's root only when it is relative, keeping the previous CWD behaviour when no root is supplied. `_check_task_file_structure` gains a keyword `root` and compares the two resolved references. `lint_task_file` now passes the tool's `path` (absolute or root-relative) and `lint_all_tasks` passes each absolute `md_file`, both with `root=workspace_root`. The stale-lane guard is unchanged in behaviour: both sides resolve under the same root, so a header pointing at another Kanban lane still resolves to a different file.

**Why a `root` parameter and not `Path.cwd()`.** The server's CWD is an install detail, not project state. A caller passing `project_root` is the only reliable statement of which project owns the file, and `_explicit_project_root` already validates it. Keeping the parameter optional means direct callers and the existing helper-level tests keep their old behaviour instead of silently changing meaning.

**Verification shape.** Two tests were written first and both failed: the pure-helper test (absolute and relative actual paths against `tmp_path` as root, plus a real stale-lane case that must still flag) and the batch test (`lint_all_tasks` on a temp project must say `Found 0 total issues`). After the fix the helper test file went 89 passed and the full suite 737 passed. The end-to-end proof is the live module call, because the unit suite cannot see the server CWD: `Scanned 6 task files. Found 0 total issues`.

**Deployment.** The global copy under `~/.config/opencode/mcp-lint-server/server.py` was synced with the same five native edits and `cmp` reports it byte-identical; a direct import of that copy returns the same clean report. The running `mcp-lint` singleton still holds the previous build — restarting a singleton unit needs the Manager's explicit order, so the one command is left to him.

**Assumption A1.** `Estimate: 1h`, deadline today, chosen by the Hands because the Manager gave no size; written through `schedule_tasks` rather than a hand edit.

**QA cycle 1 (Brain).** `QA_PASSED` with two non-blocking gaps: the absolute-header-with-relative-actual direction was not an explicit case, and `root=None` had no new test. Both closed before review — the mixed-direction assertion was added to the helper test (the `root=None` legacy path stays covered by the untouched pre-existing test), and the full suite re-ran `737 passed`, exit 0.

**Code Reviewer (Brain).** Technically approved, `PO_REVIEW_PENDING`, severity Low. One note: `_load_lint_module` used `import importlib` and then `importlib.util`, which works only because the submodule is already loaded; changed to `import importlib.util` before staging. No blocking defect. The reviewer confirmed the resolution contract, the legacy `root=None` meaning, both call sites, and the recorded global-sync-without-restart state.

**Manager closure approval (2026-10-27):** "Approved for closure" via the question tool, answering the relayed PO_REVIEW_PENDING verdict. ZAC holds; closure runs only through `custom_context_commit_and_clean_task`.

**Closure:** preconditions verified, file moved with `git mv` to the completed lane, `**Status:** closed` and the `**File:**` header synced.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `9381a7a1d931db8019fce6e40a9dac923bd774a8`
<!-- END_GIT_DIFF -->
