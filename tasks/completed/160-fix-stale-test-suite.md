# Task 160: Fix stale test suite (bundle-test import + splitter round-trip)

**File:** `tasks/completed/160-fix-stale-test-suite.md`
**Source:** manager
**Type:** bug
**Status:** closed

## Goal

Repair the two pre-existing test drifts so the full suite passes and MCP servers are verified: stale `scripts/bundle-tasks.py` import and splitter `<decision_logging_mandate>` expectation.

## Manager's Notes

Manager requested: fix it all, must test MCP servers. Found via `/tmp/release_v9.2.2.sh` pre-flight failure and recorded in Task 159 evidence.

Requirements:
- Fix 1: `tests/test_bundle_tasks.py` imports retired `scripts/bundle-tasks.py` (removed Task 155, Pure MCP). Decide: retarget to `bundle_tasks` MCP tool in `mcp-context-server/server.py` or remove stale file.
- Fix 2: `tests/test_mcp_servers.py::test_system_prompt_split_assemble_round_trip` fails because `scripts/prompt-build/split_system_prompt.py` expects retired `<decision_logging_mandate>` block (removed Task 151). Update splitter expected-block list and/or test fixture.
- Must test MCP servers: run full `tests/` suite plus `opencode mcp list` smoke. No production behavior change beyond test/tooling repair.
- Minimal diff, no scope creep into unrelated modules.

## Local TODOs

- [x] Diagnose both failures with fresh evidence
- [x] Implement minimal fixes (bundle-test + splitter)
- [x] Run full test suite and MCP smoke, record evidence
- [ ] Update CHANGELOG via Parse-Then-Append, stage and QA transition

## Acceptance Criteria

- [x] `pytest tests/ -q` exits 0 with zero failures/errors
- [x] MCP server tests pass and `opencode mcp list` shows core servers connected
- [x] No production behavior change outside test/tooling repair scope
- [x] ZAC respected (no direct git add/commit/push by Hands)

## Verification Evidence

- **Test command:** uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
- **Expected result:** all tests pass, exit code 0
- **Actual result:** 55 passed, 0 failed (48 MCP server + 7 bundle). Pre-fix baseline: 47 passed + 1 failed (splitter round-trip) + 1 collection error (bundle import). bundle_tasks dry_run smoke in sandbox OK (META 3-smoke-bundle preview). lint_task_file PASS, lint_markdown CHANGELOG PASS, lint_system_prompt_sync IN SYNC, py_compile OK (4 files), opencode mcp list 4/5 connected (telegram lock-held by design, pre-existing).
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Test rewrite masks real bundler regression; splitter change breaks prompt-build round-trip
- **Rollback plan:** Revert test/tooling files via git checkout; re-run suite to confirm pre-existing state

---

## Execution Log & Reasoning

- D1 (bundle-test fix): promoted 12 pure helpers + 3 constants from nested closures inside `bundle_tasks()` to module level in `mcp-context-server/server.py` (same underscore names; body call sites resolve via globals, zero behavior change). Verified via AST dump comparison of all 12 defs vs HEAD nested originals (identical) plus `bundle_tasks` sandbox dry_run (META 3-smoke-bundle preview OK). Retargeted `tests/test_bundle_tasks.py` imports to the MCP module (same spec-loading pattern as `test_mcp_servers.py`); T3 now asserts `_patch_archived_file` (MCP has no separate unpatch helper — rollback is inline in the tool); T5 guard dropped (MCP always provides `_detect_stack`). Chose promotion over deletion to keep Persian-slug + verbatim regression cover, over integration rewrite to keep diff minimal.
- D2 (splitter fix): `TOP_LEVEL_TAGS` dropped `decision_logging_mandate` (archived Task 151, absent from `system-prompt.md`/`manifest.txt`) and added trailing `self_improvement_protocol` (Task 152); count stays 20; stale V9.3.0 comments refreshed. Test is data-driven, needed no change. Assembler is manifest-driven, untouched.
- Mid-course correction: first promotion attempt stacked inserts inside the function body (anchor drift + stranded `@mcp.tool()`); caught via structural grep before any commit, restored file to HEAD (`git checkout --`, worktree was clean apart from this task), redid with unique two-line anchors and AST/py_compile verification after every edit. No commit-time damage; logged transparently.
- Scope kept: `system-prompt.md`, prompts, MCP tool behavior untouched; CHANGELOG entry under `[Unreleased]` only (no release, no version bump).
- ZAC: no git add/commit/push/tag executed. Staging only via MCP tool next.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `ace57423d51ddeab38ba0e5cb32e10174b93df9f`
<!-- END_GIT_DIFF -->
