# Task 179: Release v9.13.0 + archive completed tasks (milestone-17)

**File:** `tasks/completed/179-release-v9-13-0-archive-milestone-17.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Cut release **v9.13.0** (matches `system-prompt.md` 9.13.0): move all `[Unreleased]` CHANGELOG entries under a `## [9.13.0] - 2026-09-10` header, compact the 15 completed tasks (162–178, minus gaps) into `docs/history/milestone-17-summary.md` and move them to `tasks/archive/`, run all verification gates, and prepare the manual push script for Manager execution.

## Manager's Notes

Direct request (2026-09-10): "load skills about workflow about new release and make a release archive tasks. create a task for it. and create needed script for me too." Skills loaded: `versioning-and-release`, `archive-tasks`, `task-generator`; memory `release/release-workflow` retrieved and followed.

**Version rationale (Manager to confirm):** `system-prompt.md` is at 9.13.0 (Task 178); Unreleased holds Tasks 163–178 + external-opencode-server + goal-restore + OpenChamber changes — new capabilities, non-breaking → MINOR → **v9.13.0**. **Tag gap noted:** latest git tag is `v9.8.0`, but CHANGELOG already contains `9.9.0` and `9.10.0` sections (never tagged). Manager confirms whether to tag only v9.13.0 or backfill.

**Push script:** pre-created this turn at `/tmp/cognitive-lead-push-release.sh` (`VERSION="v9.13.0"`, `set -euo pipefail`, clean-tree + `gh auth status` checks, annotated tag if missing, push commits + tags, `gh release create`, verification printout). ZAC: Hands never execute it — Manager runs it manually after closure.

**Completed tasks to archive (15):** 162, 163, 164, 165, 166, 167, 168, 171, 172, 173, 174, 175, 176, 177, 178 (169/170 do not exist — no gaps to explain, IDs were never issued).

## Local TODOs

- [x] Confirm release version with Manager (proposed v9.13.0; resolve v9.9.0/v9.10.0 tag gap)
- [x] Move `[Unreleased]` entries under `## [9.13.0] - 2026-09-10` via Parse-Then-Append; leave `[Unreleased]` empty
- [x] Generate `docs/history/milestone-17-summary.md` (source distribution, architectural changes, files modified, criteria, per-task summaries)
- [x] Move 15 completed task files to `tasks/archive/` via `git mv`
- [x] Run verification gates: `lint_task_file`, `lint_markdown`, `lint_system_prompt_sync`, `py_compile`, full pytest suite
- [x] Stage via `custom_context_stage_and_inject_diff`, move task to `tasks/qa/`
- [x] Stale-memory audit report (no auto-delete without Manager approval)

## Acceptance Criteria

- [x] `CHANGELOG.md` has `## [9.13.0]` with all Unreleased entries moved; `[Unreleased]` section empty
- [x] `docs/history/milestone-17-summary.md` exists covering all 15 tasks
- [x] `tasks/completed/` is empty; all 15 files in `tasks/archive/` with history preserved
- [x] All verification gates pass (lint ×3, py_compile, pytest)
- [x] `/tmp/cognitive-lead-push-release.sh` exists, executable, `bash -n` clean, references v9.13.0
- [x] `lint_task_file` passes on the release task file

## Verification Evidence

- **Test command:** `grep -n "^\#\# \[" CHANGELOG.md | head -n 5` + `ls tasks/completed/ | wc -l` + `ls docs/history/milestone-17-summary.md` + `lint_system_prompt_sync` + `python3 -m pytest tests/ -q` + `bash -n /tmp/cognitive-lead-push-release.sh`
- **Expected result:** `## [9.13.0]` header present, `[Unreleased]` empty; `tasks/completed/` empty (0 files); milestone-17 summary exists; sync clean; pytest all pass; push script syntax ok
- **Actual result:** `## [9.13.0] - 2026-09-10` at CHANGELOG line 9, `[Unreleased]` empty (line 7); `tasks/completed/` 0 files, 15 files in `tasks/archive/`; `docs/history/milestone-17-summary.md` 158 lines (manager 13 / telegram 2 / orchestrator 0; 7 feature / 7 improvement / 1 bug); `lint_task_file` ✅, `lint_markdown` ✅ ×2 (CHANGELOG + summary), `lint_system_prompt_sync` ✅, `py_compile` OK, pytest **145 passed** (`uv run --project mcp-context-server --with pytest --with pyyaml pytest tests/ -q`; note: bare `pytest` and context-only env fail on missing `yaml` — env union required); `bash -n` on push script clean, `VERSION="v9.13.0"`, chmod +x
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Wrong version header or duplicate categories corrupt Keep-a-Changelog structure; archiving the wrong files loses Kanban history; tagging over the v9.8.0→v9.13.0 gap confuses release lineage.
- **Rollback plan:** `git restore CHANGELOG.md docs/history/` before staging; archived tasks recoverable via `git mv tasks/archive/<id>-*.md tasks/completed/`; never delete tags — if a wrong tag is pushed, Manager deletes it manually via `gh release delete` + `git push --delete origin <tag>`.

---

## Execution Log & Reasoning

**Version decision:** Manager approved v9.13.0, tag-only (no backfill of never-tagged 9.9.0/9.10.0). Matches `system-prompt.md` 9.13.0; Unreleased held new capabilities (persona/decision servers, OpenChamber, blowsh skill) → MINOR.

**Edits:**
- `CHANGELOG.md` — inserted `## [9.13.0] - 2026-09-10` directly below `## [Unreleased]` (single-line move, all Added/Changed/Removed entries now under release header; Unreleased left empty). No duplicate headers.
- `docs/history/milestone-17-summary.md` — new 158-line summary drafted via delegated subagent (matched milestone-16 structure): 15 tasks (162-168, 171-178; 169/170 never issued), source 13 manager / 2 telegram / 0 orchestrator, 7 feature / 7 improvement / 1 bug.
- 15 files `tasks/completed/` → `tasks/archive/` via `git mv` (single command, history preserved; `tasks/completed/` now empty).
- `/tmp/cognitive-lead-push-release.sh` — pre-created per `release/release-workflow` memory (`set -euo pipefail`, clean-tree + `gh auth status` gates, annotated tag if missing, push branch + tags, create-or-verify `gh release`, ls-remote + release URL verification). Manager runs it manually post-closure (ZAC).

**Stale-memory audit:** searched memory for archived-task topics — no stale or superseded entries found; all indexed memories are active workflow docs. No deletions proposed.

**Verification:** `lint_task_file` ✅, `lint_markdown` ✅ ×2, `lint_system_prompt_sync` ✅, `py_compile` OK, pytest **145 passed** (env note: suite needs `mcp` + `yaml` + `pathspec` union — `uv run --project mcp-context-server --with pytest --with pyyaml`).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `ee93b99deff934b273f709d86bb3725e9c166d6f`
<!-- END_GIT_DIFF -->
