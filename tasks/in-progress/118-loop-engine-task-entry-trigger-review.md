# Task 118: Loop Engine Task Entry Trigger Review

**File:** `tasks/in-progress/118-loop-engine-task-entry-trigger-review.md`
**Source:** telegram
**Type:** improvement
**Status:** in-progress
**Created:** 2026-08-26

---

## Goal

Review and redesign how tasks enter the loop engine execution cycle. Currently, tasks may auto-enter the loop, but this is problematic because:

1. A task might be written and then edited afterward — auto-entry would execute an incomplete version.
2. The Telegram sync skill creates task files, but the Manager may need to refine them before execution.
3. The entry mechanism needs an explicit admin trigger (e.g., "select task N and execute it") rather than automatic pickup.

## Acceptance Criteria

- [x] Audit current loop engine task pickup mechanism — identified auto-entry in `watcher.py` `on_created` + `scan_existing` + `daemon.py` `on_task_detected` callback
- [x] Design a trigger-based entry model: `trigger_mode` config + `PENDING_TRIGGER` state + Telegram trigger cards + `/run` command
- [x] Ensure task files can be edited/refined after creation but before loop entry — `trigger_task()` does fresh file re-read from disk
- [x] Document the new trigger flow in `docs/loop-engine/` (README, configuration, setup)
- [x] Verify Telegram sync skill creates tasks in `backlog/` without triggering execution — tasks register as `PENDING_TRIGGER` in non-auto modes

## Local TODOs

- [x] Read loop engine source and identify auto-entry code paths
- [x] Propose trigger mechanism (CLI flag, admin command, or prompt directive)
- [x] Implement the trigger gate
- [x] Test: create task via Telegram sync → edit task → trigger execution manually
- [x] Update relevant docs

## Risk & Rollback

- Changing the loop entry mechanism could break existing sprint workflows if not backward-compatible.
- Need to ensure the trigger is simple enough for the Manager to use without extra friction.
- **Rollback:** Revert to `trigger_mode: "auto"` and remove `PENDING_TRIGGER` state to restore legacy auto-pickup behavior.

## Verification Evidence

- `py_compile` all 6 modified files: ✅
- `uv run --with pytest pytest -q` (loop-engine): **72 passed, 0 failed** ✅
- `uv run --with pytest ... pytest tests/ -q` (project): **50 passed, 0 failed** ✅
- `test_trigger_entry.py` standalone: **9 passed, 0 failed** ✅

## Execution Log & Reasoning

### Trigger Architecture

The trigger gate decouples task creation from execution via a new `PENDING_TRIGGER` state in the `TaskState` enum. When `trigger_mode != "auto"`, newly detected tasks register as `PENDING_TRIGGER` instead of `BACKLOG`, and the gateway sends a Telegram card with [🚀 Start Execution] / [⏸️ Hold] buttons.

**New config fields:**
- `trigger_mode`: `"telegram_button"` (default) | `"command_only"` | `"auto"`
- `auto_start_on_boot`: `false` (default) — controls boot-scan behavior

**New methods:**
- `gateway.send_task_trigger_card(task_id, title, file_path)` — sends Telegram card
- `gateway._handle_text_command(message)` — parses `/run`, `/start`, `/tasks`, `/backlog`
- `daemon.trigger_task(task_id)` — fresh file re-read, PENDING_TRIGGER→PLANNING, launches processing
- `daemon.boot_scan()` — respects `auto_start_on_boot`
- `state.get_pending_trigger_tasks()` — returns tasks awaiting trigger

**State transitions:**
- `PENDING_TRIGGER → PLANNING` (via `trigger_task()`)
- `PENDING_TRIGGER → CRASHED` (on error)
- `PENDING_TRIGGER → ABORTED` (explicit abort)

**CLI support:**
- `python daemon.py --run <task_id>` — triggers a specific staged task directly

### Files Modified

| File | Changes |
|------|---------|
| `loop-engine/models.py` | Added `PENDING_TRIGGER`, `ABORTED` to `TaskState`; added `trigger_mode`, `auto_start_on_boot` to `LoopEngineConfig` |
| `loop-engine/state.py` | Added `get_pending_trigger_tasks()` method |
| `loop-engine/gateway.py` | Added trigger card, text command parsing, daemon/state wiring |
| `loop-engine/watcher.py` | Conditional registration based on `trigger_mode` |
| `loop-engine/daemon.py` | New `LoopEngineDaemon` class, CLI `--run`, boot scan logic |
| `loop-engine/loop-engine.jsonc` | Documented new config fields |
| `loop-engine/test_trigger_entry.py` | 9 new tests |
| `loop-engine/test_models.py` | Updated enum count assertion (10→12) |
| `docs/loop-engine/README.md` | Updated architecture diagram and workflow |
| `docs/loop-engine/configuration.md` | Added trigger_mode, auto_start_on_boot docs |
| `docs/loop-engine/setup.md` | Added trigger config examples and CLI usage |
| `CHANGELOG.md` | Added Task 118 entry under [Unreleased] > Changed |

## Implementation Checklist

- [x] **Step 1:** Update `loop-engine/models.py` — add `trigger_mode` + `auto_start_on_boot` to `LoopEngineConfig`, add `PENDING_TRIGGER` + `ABORTED` to `TaskState`
- [x] **Step 2:** Update `loop-engine/loop-engine.jsonc` — add new config fields with inline docs
- [x] **Step 3:** Update `loop-engine/state.py` — add `PENDING_TRIGGER` transitions, update `get_pending_tasks()`
- [x] **Step 4:** Update `loop-engine/gateway.py` — trigger card, `/run`, `/tasks` commands, callback handling
- [x] **Step 5:** Update `loop-engine/watcher.py` — conditional auto vs manual based on `trigger_mode`
- [x] **Step 6:** Update `loop-engine/daemon.py` — boot scan, `trigger_task()`, CLI `--run`
- [x] **Step 7:** Create `loop-engine/test_trigger_entry.py` — 6 comprehensive tests
- [x] **Step 8:** Update docs (`docs/loop-engine/`)
- [x] **Step 9:** Update `CHANGELOG.md`
- [x] **Step 10:** Run all pytest verification suites

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
