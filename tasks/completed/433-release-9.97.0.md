# Task 433: Release 9.97.0 — Brain on LiteLLM, zen-bridge, and stage-scoped seven-seat prompts

**File:** `tasks/qa/433-release-9.97.0.md`
**Source:** manager
**Type:** chore
**Status:** qa
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
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index adee5eb..6c1dd71 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+## [9.97.0] - 2026-11-27
+
 ### Changed
 
 - **META 432 follow-up — retry policy removed from the Brain; every stage now ships all seven seats:** pinned `num_retries=0` on the LiteLLM call and deleted the retry ladder residue — `_litellm_retries`/`BRAIN_LITELLM_RETRIES`, the `_TERMINAL_429_CODES` classifier with `_terminal_429_code` and the quota-retry advice in `_provider_error_hint`, `_error_payload`, and `_overall_deadline_s`/`BRAIN_OVERALL_DEADLINE_S`. A failed turn now surfaces a `PROVIDER_ERROR` report and retrying is the caller's decision. Removed the matching tests and every doc/env reference, including the timeout ladder in `LLM.txt`, `docs/brain-bridge.md`, `.env.example`, and the zen-bridge ownership memory. Separately, the stage prompt design was settled on one lead persona per stage plus the full seven-seat roster and a new `auto_load` Layer 3 adoption rule, instead of duplicating seven persona blocks into every artifact: the all-blocks variant was reverted because multiple full personas in one system message conflict and burn context. All eight artifacts were regenerated (lead block only: qa 90 KB, full prompt 104 KB) and the stale installed copies under `~/.config/opencode/` were re-synced from 9.93.0. Stage and prompt-sync tests assert lead-roster match, seven nameable seats, and the adoption rule. A project-wide leftover audit also refreshed `mcp-brain-bridge/README.md`, added ADR-015, and removed stale caches. Full suite `940 passed`.
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 7014e4f..20739a2 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.96.0</system_version>
+<system_version>9.97.0</system_version>
diff --git a/system-prompt.md b/system-prompt.md
index 0b014f8..ad96e57 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.96.0</system_version>
+<system_version>9.97.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
```
<!-- END_GIT_DIFF -->
