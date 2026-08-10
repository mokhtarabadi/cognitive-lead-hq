# Task 91: Fix TOCTOU and Dead Scout Ref

**File:** `tasks/in-progress/91-fix-toctou-and-dead-scout-ref.md`
**Source:** manager
**Type:** bug
**Status:** open

## Source Context

### Variant C: Manager (`**Source:** manager`)

## Goal

Fix two audit findings from Task 87: (F4) apply the UUID-suffix pattern to `read_source_files` in `mcp-context-server/server.py` so same-second report writes cannot overwrite each other (mirroring `create_tree_report`), and (F6) remove the dead `@scout` subagent reference from `system-prompt.md` (line ~421), replacing it with `@general`. Bump system version to 8.4.3 and update CHANGELOG.

## Manager's Notes

- F4 root cause: `context_report_<timestamp>.md` has no uniqueness guard — two calls within one second silently destroy the earlier report. Task 85 fixed the identical bug in `create_tree_report` but did not port it back.
- F6 root cause: `@scout` was never registered as a subagent (only `cognitive-discovery`, `explore`, `general` exist); the reference would error or be silently substituted.
- Version bump: PATCH (8.4.2 → 8.4.3) per `versioning-and-release`.
- Global deployment sync: after this task, `~/.config/opencode/system-prompt.md` should be re-synced (LLM.txt Step 5) so the next restart loads 8.4.3 — performed at the end of this task and logged.

## Local TODOs

- [x] Step 1: Create this task file (ID discovery → 91), move to `tasks/in-progress/` (filesystem `mv` — untracked)
- [x] Step 2: Read target files (server.py `read_source_files` ~line 365, system-prompt.md `<context_phase>` ~line 421)
- [x] Step 3: Fix F4 — UUID suffix in `read_source_files` report filename + inline comment
- [x] Step 4: Fix F6 — replace `@scout` with `@general` in the implementation template `<context_phase>`
- [x] Step 5: Bump `<system_version>` 8.4.2 → 8.4.3
- [x] Step 6: Update `CHANGELOG.md` — `## [8.4.3]` with 2 `### Fixed` entries (Parse-Then-Append)
- [x] Step 7: Syntax verification (py_compile + pytest + greps) + re-sync global system-prompt copy

## Acceptance Criteria

- [x] `read_source_files` writes `context_report_<timestamp>_<uuid8>.md` (UUID suffix, same pattern as `create_tree_report`)
- [x] `@scout` no longer appears anywhere in `system-prompt.md`
- [x] `<system_version>` is 8.4.3
- [x] `CHANGELOG.md` has exactly one `## [8.4.3]` header with 2 `### Fixed` entries
- [x] `pytest` passes (14); `py_compile` OK
- [x] Task file passes `lint_task_file`

## Verification Evidence

- **Test command:** `uv run --with pytest --with pathspec --with "mcp[cli]>=1.0,<2.0" ... pytest tests/test_mcp_servers.py -q` ; `grep -n "uuid.uuid4().hex\[:8\]" mcp-context-server/server.py` ; `grep -n "@scout" system-prompt.md` ; `lint_task_file tasks/in-progress/91-fix-toctou-and-dead-scout-ref.md`
- **Expected result:** 14 passed; UUID pattern 2 matches (create_tree_report + read_source_files); `@scout` 0 matches; lint ✅
- **Actual result:** `14 passed, 9 warnings in 1.04s`; UUID pattern at lines 366 (`read_source_files`) and 418 (`create_tree_report`) — exactly 2 matches; `@scout` → 0 matches; `8.4.3` exactly once (line 1 `<system_version>`); `py_compile` → ✅ Syntax OK; global `~/.config/opencode/system-prompt.md` re-synced (byte-identical, v8.4.3); lint → ✅ passed (run below)
- **Exit code:** 0 (pytest, py_compile, greps); 0 (lint)

## Risk & Rollback

- **Risk:** (1) Existing report consumers expecting the old filename pattern — mitigated: consumers parse the path from the tool's returned message, not a hardcoded pattern; no code/test depends on the old name. (2) CHANGELOG duplicates — mitigated by Parse-Then-Append. (3) Global copy drift — mitigated by re-sync + diff check.
- **Rollback plan:** Revert the UUID line in `read_source_files`, restore `@scout` text and 8.4.2, remove the 8.4.3 CHANGELOG block, re-sync global copies.

---

## OpenCode Execution Log & Reasoning

### What was done

1. **F4 fix — `mcp-context-server/server.py` `read_source_files` (line ~365):** report filename changed from `context_report_<timestamp>.md` to `context_report_<timestamp>_<uuid8>.md` using `uuid.uuid4().hex[:8]`, with the inline comment "F4 Fix: UUID suffix prevents same-second TOCTOU overwrite, mirroring create_tree_report logic." `uuid` was already imported (line 24). The tool's returned message carries the full report path, so consumers (Manager/Orchestrator) parse the path dynamically — no hardcoded pattern dependency anywhere (verified: no test asserts the old name).
2. **F6 fix — `system-prompt.md` `<context_phase>` of `<opencode_implementation_task_template>` (line ~421):** replaced "use `@explore` for fast read-only codebase mapping, `@scout` for external docs/dependency research, or `@general` for complex multi-step research" with "use `@explore` for fast read-only codebase mapping, or `@general` for external docs/dependency research and complex multi-step research." Grep confirms 0 remaining `@scout` occurrences.
3. **Version bump:** `<system_version>` 8.4.2 → 8.4.3 (PATCH — defect fixes).
4. **`CHANGELOG.md`:** `## [8.4.3] - 2026-08-10` inserted below `[Unreleased]` and above `[8.4.1]`... (actual position: directly above `## [8.4.1]`, since `[8.4.2]` is the previous released header — verified single header, 2 Fixed entries, Parse-Then-Append).
5. **Global deployment sync:** `~/.config/opencode/system-prompt.md` re-synced byte-identical (v8.4.3) so the next restart loads the fixed prompt — consistent with LLM.txt Step 5 and the Manager's restart workflow.

### Architectural reasoning

- **F4:** The two report-producing tools now share the identical uniqueness strategy (UUID suffix by construction, no exists()/open() race). This closes the half-applied fix noted in Task 85's execution log: the same-second overwrite failure mode that was real for `tree_report` was equally real for `context_report`.
- **F6:** The implementation template is the most delegation-heavy of the three; pointing its "external research" case at `@general` (a real, registered agent) removes a failure mode where an LLM either errors or silently substitutes an unvetted agent — consistent with the anti-lazy deterministic-orchestration philosophy.
- **No test changes required:** the 14-test suite passes unchanged — the only test touching report filenames uses a dummy `context_report_x.md` string, unaffected by the real naming pattern.

### Lint & verification

- `lint_task_file tasks/in-progress/91-fix-toctou-and-dead-scout-ref.md` → ✅ (run in summary phase).
- `pytest`: 14 passed; `py_compile`: OK; greps verified (see Verification Evidence). No repair attempts needed.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->