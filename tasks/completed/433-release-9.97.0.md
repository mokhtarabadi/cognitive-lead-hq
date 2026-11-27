# Task 433: Release 9.97.0 — Brain on LiteLLM, zen-bridge, and stage-scoped seven-seat prompts

**File:** `tasks/completed/433-release-9.97.0.md`
**Source:** manager
**Type:** chore
**Status:** closed
**Finished:** 2026-11-27T10:31:29Z
**Submitted:** 2026-11-27T10:24:13Z
**Started:** 2026-11-27T10:22:57Z

## Goal

Cut release `9.97.0` from the current `main` state: bump the system version, move every
`[Unreleased]` entry under a `9.97.0` header, verify the release gate, and stage the
release for Manager closure. No application code changes; metadata and prompt artifacts only.

## Manager's Notes (verbatim intent)

"we need to make a release.. follow workflows load them, create task and follow the workflows to make a release, auto pilot lock on"

Binding context:

- Current version is `9.96.0` (`<system_version>` at the top of `system-prompt.md` and the `## [9.96.0] - 2026-11-24` header in `CHANGELOG.md`).
- `9.97.0` is a MINOR bump: non-breaking architectural upgrade (new transport, rename, removal, prompt rework). The `system-prompt.md` version is bumped.
- `[Unreleased]` must be empty after the release; all entries move under the new header.
- `system-prompt.md` and all eight stage artifacts must be regenerated and pass `assemble_system_prompt.py --check` before the release is considered complete.
- Push is owner-gated; the agent stages and commits only through the approved MCP path.

## Local TODOs

- [x] Bump `<system_version>` to `9.97.0` in `system-prompt.md` and every stage artifact
- [x] Move all `[Unreleased]` entries under `## [9.97.0] - 2026-11-27`
- [x] Run `assemble_system_prompt.py --check` and the full test suite
- [x] Verify no retired keys remain in live docs
- [x] Record final reasoning and stage via the approved mechanism
- [x] QA and review via `brain_turn`

## Acceptance Criteria

- [x] `<system_version>` reads `9.97.0` in `system-prompt.md` and all eight stage artifacts
- [x] `[Unreleased]` is empty and `## [9.97.0] - 2026-11-27` carries every entry
- [x] `assemble_system_prompt.py --check` exits 0
- [x] Full test suite passes with exit code 0
- [x] No retired names in live docs outside history
- [x] `lint_task_file` passes on the active task file

## Verification Evidence

- **Test command:** `rtk test uv run --with pytest --with mcp==1.30.0 --with litellm --with pathspec --with pyyaml python -m pytest tests/ -q`
- **Expected result:** 940 passed (or higher), exit code 0
- **Actual result:** `assemble_system_prompt.py --check` → current, exit 0; `pytest tests/ -q` → 940 passed, exit 0; `<system_version>` reads 9.97.0 in `system-prompt.md` and all 8 artifacts; `[Unreleased]` empty; retired keys have no live reader; lint passes.
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `testing-verification` applied and evidence recorded

## Risk & Rollback

- **Risk:** a stale stage artifact or a mis-numbered header ships; the release is incomplete.
- **Rollback plan:** revert the version bump and the CHANGELOG move in one commit; the underlying code is unchanged by this task.

---

## Execution Log & Reasoning

### Assumptions

- **A1** — `9.97.0` is a MINOR bump: non-breaking architectural upgrade (transport, rename, removal, prompt rework). The `system-prompt.md` version is bumped.
- **A2** — `[Unreleased]` must be empty after the release; all three entries moved under the new header.

### Step 1 — Pre-commit gate

- `assemble_system_prompt.py --check` → current, exit 0.
- `rtk test ... pytest tests/ -q` → 940 passed, exit 0 (see Verification Evidence).

### Step 2 — Metadata

- `<system_version>` bumped `9.96.0` → `9.97.0` in `prompts/fragments/01-system_version.md`; all eight artifacts and `system-prompt.md` regenerated (104,341 bytes each).
- `[Unreleased]` emptied; `## [9.97.0] - 2026-11-27` carries all three entries.
- Reasoning recorded here; no code changes beyond metadata and artifacts.

### Step 3 — Staging & review

- `lint_task_file` passes.
- QA and review chained via `brain_turn` under the same task id.

### Deviations

- **D1** — `build/stage-prompts/` is gitignored, so the regenerated artifacts are local build outputs and are not part of the release commit; the freshness gate (`--check`) is what keeps them reproducible. Only `system-prompt.md` is committed.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `a4587c0eacf25cc117006a2cb221a34cd7e18dc9`
<!-- END_GIT_DIFF -->
