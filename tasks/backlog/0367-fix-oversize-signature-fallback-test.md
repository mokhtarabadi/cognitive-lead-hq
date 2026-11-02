# Task 0367: Fix oversize signature fallback test

**File:** `tasks/backlog/0367-fix-oversize-signature-fallback-test.md`
**Source:** manager
**Type:** bug
**Status:** open

## Goal

Make the oversize `read_source_files` fallback attach extracted signatures so the regression test passes.

## Manager's Notes

Deferred fix request: the global-sync full suite came back 754 passed with 1 unrelated failure. Task it in backlog; fix later.

Failing test: `tests/test_mcp_servers.py::test_graph_split_oversize_fallback_names_resolve` ("QA reject fix: oversize read_source_files must attach signatures, not NameError"). It writes a 20031-byte `big.py` (one `def big_symbol()` plus 5000 filler lines) into a temp repo, calls `read_source_files(["big.py"], max_size=100)`, and expects the generated report file to contain `def big_symbol():`. Actual: the report contains only `Skipped: (File too large: 20031 bytes > max_size=100)` plus `No signatures extracted — narrow paths, raise max_size, or call extract_signatures on this file.` Observed under `uvx` with exact pins (`mcp==1.30.0`, `pathspec`, `pyyaml`); full suite result 1 failed, 754 passed. Suspect area: `mcp-context-server` oversize handling / signature fallback path. No server code was touched by the synced changes, so treat as pre-existing.

## Local TODOs

- [ ] Reproduce the single failing test locally
- [ ] Fix the oversize fallback so signatures attach to the report
- [ ] Verify functionality

## Acceptance Criteria

- [ ] `tests/test_mcp_servers.py::test_graph_split_oversize_fallback_names_resolve` passes in isolation
- [ ] Full `tests/test_mcp_servers.py` module passes with no new failures
- [ ] Prompt-sync gate (`tests/test_prompt_sync.py`) still passes

## Verification Evidence

- **Test command:** rtk test uvx --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml pytest tests/test_mcp_servers.py -q
- **Expected result:** all module tests pass, exit code 0
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

> Verification runner rule: `uvx --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml pytest tests/test_mcp_servers.py -q` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics. Pin `mcp` exact (no `<`/`>` ranges — RTK joins args into a shell string and a range becomes input redirection).

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Low-medium. Touching the MCP context server fallback path could alter report output relied upon by other tests; run the full module before claiming done.
- **Rollback plan:** Revert server change via git; the failing test then returns to its current red state, which is the documented baseline.

---

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
