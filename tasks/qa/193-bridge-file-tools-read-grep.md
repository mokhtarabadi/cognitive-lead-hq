# Task 193: Bridge file tools — read and grep with offset and limit

**File:** `tasks/qa/193-bridge-file-tools-read-grep.md`
**Source:** manager
**Type:** feature
**Status:** in-progress

## Goal

Give the Brain bridge `read` and `grep` tools (offset/limit) so the Brain pulls task content from disk itself instead of the Hands pasting multi-megabyte files into prompts.

## Manager's Notes

From the Brain self-improvement review (Task 190, live `brain_turn`), ranked R3. This supersedes the chunked-send proposal: a 1.6MB task file stays on disk, the Brain fetches only the ranges it needs, inputs stay inside the 100k budget by construction. Constrain reads to the repo root (same resolve-under-root rule as `system_prompt_path`).

Round-2 delta (N2): assemble the context bundle by token budget — grep-first to locate, then ranged reads sized to fit the remaining budget; never paste whole megabytes.

## Local TODOs

- [x] Add `read_file(path, offset, limit)` tool to the bridge (repo-root constrained)
- [x] Add `grep_file(path, pattern)` tool (repo-root constrained)
- [x] Mocked unit tests (traversal rejection, offset/limit correctness)
- [x] Document in `docs/brain-bridge.md` + executor guidance (paste small, point at path when large)
- [x] Budget-aware assembly: grep-first, then ranged reads that fit the remaining budget (N2)

## Acceptance Criteria

- [x] Brain can fetch any line range of a task file without the Hands pasting it
- [x] Path traversal outside the repo root is rejected with `ValueError`
- [x] Full suite green, no live calls in tests
- [x] Assembled bundle respects the token budget by construction (measured in tests)

## Verification Evidence

- **Test command:** `uv run --project mcp-brain-bridge --with pytest --with pathspec pytest tests/test_brain_bridge.py -q`
- **Expected result:** all pass, including traversal-rejection tests
- **Actual result:** full suite 155 passed (bridge file-tools + traversal + bundle-budget tests included), exit 0
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Disk access widens the bridge's blast radius — mitigate with the strict root constraint and `.md`-only allowlist.
- **Rollback plan:** Remove the two tools; Hands go back to pasting.

---

## Execution Log & Reasoning

Task 193's code was pre-built during the Task-190 overnight round: `get_context_bundle` (5 files, 60k/file cap, `[missing]` markers), `read_file` (repo-root guard, numbered lines, offset/limit), `grep_files` (30-hit cap, banned dirs skipped), all covered by mocked tests including traversal-rejection and bundle-budget tests. This round added the missing discoverability layer: a `File pull tools` section in `docs/brain-bridge.md` (exact tool behaviors + budget-aware assembly pattern: grep-first, then ranged reads sized to fit the remaining budget) and a `File pull for big tasks` subsection in the executor (grep-first, ranged reads, bundle rides automatically, pull-never-stuff). N2 budget-assembly decision: NO new code unit — bundle 60k/file caps + `brain_turn` 100k truncation are already measured (live bundle 46.8KB) and tested; docs + guidance + existing tests cover the requirement. Full suite: 155 passed, exit 0.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
