# Task 286: Context MCP Singleton Report Write Path

**File:** `tasks/qa/286-context-mcp-singleton-report-path.md`
**Source:** manager
**Type:** bug
**Status:** open

## Goal

Make the context MCP server write every generated report under the caller-supplied project root (`<project_root>/context-reports/`) instead of the singleton server's working directory. After the singleton migration the server cwd is `~/.config/opencode/mcp-context-server`, so `create_tree_report`, `read_source_files`, and `extract_signatures` dropped their output in the global install dir, and the Brain's bundle (which reads the project's `context-reports/`) never saw a fresh map. The fix routes the output through the already-resolved `workspace_root` argument.

## Manager's Notes

Manager order (translated): since the MCP servers are singletons now, every server must take the project path through the argument supplied by the caller (the Hands); the report path must return to the project's own `context-reports/` as before. Constraint: preserve the cwd fallback for project_root-omitted calls; change only where output is written.

Discovered during the task 285 smoke test: a regenerated tree report landed in `~/.config/opencode/mcp-context-server/context-reports/`, and the repo's newest report stayed at 2026-09-18 (still listing a removed `stacks/` directory).

## Local TODOs

- [x] Add a failing regression test that runs with cwd away from the project and asserts reports land under `<project_root>/context-reports/`
- [x] Fix `_ensure_context_reports_ignored` to accept and use the workspace root
- [x] Fix `read_source_files` report dir + gitignore call
- [x] Fix `create_tree_report` report dir + gitignore call
- [x] Fix `extract_signatures` report dir + gitignore call (and its cwd-relative fallback read)
- [x] Verify with the RTK-prefixed test command and record evidence

## Acceptance Criteria

- [x] With `project_root` set and cwd elsewhere, `create_tree_report`, `read_source_files`, and `extract_signatures` write under `<project_root>/context-reports/`
- [x] The `.gitignore` safeguard updates `<project_root>/.gitignore`, not the server cwd's
- [x] With `project_root` omitted, behavior is unchanged (cwd fallback, still warned client-visibly)
- [x] All pre-existing `tests/test_mcp_servers.py` tests still pass
- [x] A new regression test proves the project-root target with a foreign cwd

## Verification Evidence

- **Test command:** rtk test uv run --with-requirements /tmp/opencode/clh-test-reqs.txt pytest tests/test_mcp_servers.py -q
- **Expected result:** all context-server tests pass, including the new foreign-cwd target case, exit code 0
- **Actual result:** `70 passed, 22 warnings in 1.92s` (69 pre-existing + 1 new)
- **Exit code:** 0
- **Full suite (informational):** `709 passed, 2 failed`; both failures are the pre-existing unrelated `tests/test_decision_server.py` cases.

> Verification runner rule: the first verification run used the `rtk test` prefix as recorded above; exit code 0. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** changing the output path could break callers that assumed a cwd-relative return. Mitigated: with `project_root` omitted the workspace root resolves to cwd exactly as before, so the fallback path is byte-identical.
- **Risk:** absolute return paths could surprise a caller parsing the path. The returned path is still a valid filesystem path and the filename is unchanged.
- **Rollback plan:** revert the `mcp-context-server/server.py` hunk and the new test; no persisted schema or migration is involved.

---

## Execution Log & Reasoning

**Plan verdict:** Manager-authorized direct bug fix — "fix it quickly and return the path to the project's own `context-reports/`". His order is the plan.

**Seat Check:** domain = MCP server path resolution (Software Architect) + Python fix (Senior Programmer). Skipped: UI/UX Designer (no surface), Planner/Strategist (no scope/file-state change). QA/Review run after the fix per the Manager's sequence.

**Root cause:** `create_tree_report`, `read_source_files`, and `extract_signatures` each did `report_dir = Path("context-reports")`, relative to the server process cwd. Under per-session stdio the cwd was the project, so reports landed correctly; after the singleton migration the cwd is `~/.config/opencode/mcp-context-server`, so every report went to the global install dir. `_ensure_context_reports_ignored()` had the same `Path(".gitignore")` bug, and `extract_signatures`'s regex fallback read `file_path` (cwd-relative) instead of the resolved `path`.

**Fix:** all three writers now use `workspace_root / "context-reports"` (mkdir parents), `_ensure_context_reports_ignored(workspace_root)` targets `<project_root>/.gitignore`, and the fallback reads `path`. `workspace_root` already came from `_explicit_project_root(project_root, ...)`, so the project path travels through the caller's argument exactly as the Manager required; a `None` root still falls back to cwd with the client-visible warning.

**Assumption A1 (logged):** the Manager said "all our MCP servers must take the project path via argument". This fix covers the context server's report writers (the only cwd-relative writers found). A repo-wide grep showed no other server writing project-relative output paths. If a second offender surfaces, it becomes a follow-up.

**Verification:** `rtk test uv run --with-requirements /tmp/opencode/clh-test-reqs.txt pytest tests/test_mcp_servers.py -q` → `70 passed`, exit 0. The new `test_context_reports_follow_project_root_not_singleton_cwd` fails before the fix (reports written to the foreign cwd; `extract_signatures` raised `FileNotFoundError`) and passes after.

**Global sync + live smoke (Manager sequence):** copied `mcp-context-server/server.py` to `~/.config/opencode/mcp-context-server/`, confirmed byte-identical, restarted `mcp-context.service` (active, port 8102). Live smoke through the singleton: `create_tree_report`, `read_source_files`, and `extract_signatures` each returned `<repo>/context-reports/...`; the fresh tree report no longer lists the removed `stacks/`; the global install `context-reports/` count stayed at 19 (the stray report written by the old buggy code was removed); and `get_context_bundle` picked the fresh report.

**Autopilot QA + review:** QA Engineer `VERDICT: QA_PASSED` (no functional vulnerabilities; notes the pre-existing absolute-path read scope in `extract_signatures` as out-of-scope backlog). Code Reviewer `PO_REVIEW_PENDING` — technically approved, two Low process/test-depth nits (formatting churn in the diff, and preferring parametrized writer coverage next time). Closure requires the Manager's exact word.

**Formatting-churn follow-up (same task):** the first staged diff was ~600 lines in `mcp-context-server/server.py` because the auto-formatter rewrote the whole file on edit. That oversized diff also tripped `lint_task_file`: the context server's own source contains the diff-begin/end HTML-comment markers on their own lines, and when the diff carried them as context lines the linter's diff-skip region ended early. Both files were restored from HEAD and only the functional changes re-applied via a script (shell writes bypass the formatter), yielding a clean 56/48-line diff; lint then passes. The linter's marker-detection fragility is a separate, pre-existing robustness issue left as a follow-up, not fixed here. A related trap: never write the raw begin/end marker text into task prose, because the injection tool's dot-all regex will consume the span between a prose marker and the real end marker.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
