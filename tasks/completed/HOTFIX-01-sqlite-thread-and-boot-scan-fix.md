# Task HOTFIX-01: SQLite Thread-Affinity & Boot-Scan Pending Re-Trigger Fix

**File:** `tasks/completed/HOTFIX-01-sqlite-thread-and-boot-scan-fix.md`
**Source:** orchestrator
**Type:** improvement
**Status:** closed
**Mode:** lite

## Goal

Apply the hotfix enabling SQLite access from watchdog background threads (`check_same_thread=False`) and making `boot_scan()` re-send Telegram trigger cards for tasks already registered in `PENDING_TRIGGER` state (surviving daemon restarts), plus starting the Telegram poller before boot-scan cards are dispatched.

## Local TODOs

- [x] Read AGENTS.md, docs/conventions.md, state.py, daemon.py, gateway.py
- [x] Step 1 — state.py: `sqlite3.connect(..., check_same_thread=False)`
- [x] Step 2 — daemon.py `boot_scan()`: ensure poller + resend PENDING_TRIGGER cards (deduped)
- [x] Step 3 — daemon.py `main()`: `gateway._ensure_poller()` before `boot_scan()`
- [x] Run pytest suite — verify no regressions

## Acceptance Criteria

- [x] `StateMachine.__init__` opens SQLite with `check_same_thread=False`
- [x] `boot_scan()` (auto_start_on_boot=False) scans backlog via `watcher.scan_existing()` AND re-sends cards for `self.state.get_pending_trigger_tasks()`
- [x] `main()` calls `gateway._ensure_poller()` immediately before `boot_scan()`
- [x] Full test suite passes: `uv run --project loop-engine --with pytest pytest loop-engine/ -q` → 247 passed, 0 failed

## Verification Evidence

- **Test command:** `uv run --project loop-engine --with pytest pytest loop-engine/ -q`
- **Expected result:** all tests green, 0 failures, 0 regressions
- **Actual result:** 247 passed, 0 failed in 13.28s
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Manager Decisions

- **[2026-08-31] [D1] [LITE]:** Orchestrator tagged this task `lite_mode` (hotfix) even though it touches 2 source files (state.py, daemon.py), exceeding the strict single-file eligibility rule.
  - **Rationale:** All 3 steps were fully specified with exact code in the task block; zero architectural ambiguity; urgent hotfix; the only judgment call was dedup (D2).
  - **Alternatives considered:** Escalating to Full Mode (discovery/blueprint/approval) — unnecessary for a specified hotfix.
  - **Impact:** Expedited workflow applied; standard QA + full end-of-task sequence still enforced.
- **[2026-08-31] [D2] [EXECUTION-DETECTED]:** Deviation from the verbatim `boot_scan()` snippet: added a task_id dedup so PENDING_TRIGGER re-send skips tasks already carded by `scan_existing()` in the same boot.
  - **Rationale:** `scan_existing()` registers fresh backlog files into PENDING_TRIGGER and returns them; a blind re-query via `get_pending_trigger_tasks()` would re-send an identical card for EVERY task on EVERY fresh boot (regression confirmed by `test_smoke_boot_scan_registers_pending_trigger`, which expects exactly 1 card). Dedup preserves the hotfix's restart-survival intent without duplicate Telegram spam.
  - **Alternatives considered:** Keeping the verbatim snippet and changing the test to expect 2 cards — rejected: duplicate cards are a UX defect, and the existing test contract encodes the correct behavior.
  - **Impact:** Only affects card fan-out; ID semantics of `return existing or pending_in_db` unchanged.
- **[2026-08-31] [D3] [EXECUTION-DETECTED]:** Fixed a stale assertion in `test_audit_fixes.py::test_load_config_from_repo_root` (hard-coded `chat_id == 0` placeholder).
  - **Rationale:** `loop-engine/loop-engine.jsonc` was changed **out-of-band** (uncommitted working-tree edit applying the Manager's 2026 config with real `chat_id: 1247026399`); the placeholder assertion was pre-existing and failing before this hotfix's code changes. The test's actual purpose is repo-root anchoring, so the assertion was made type-robust.
  - **Alternatives considered:** Leaving the suite red — violates the hotfix's "all tests green" gate; reverting the out-of-band config — out of scope and would discard the Manager's intended config.
  - **Impact:** Test suite green again; the out-of-band `loop-engine.jsonc` change was deliberately NOT staged by this hotfix (F5 scoped staging).
- **[2026-08-31] [D4] [EXECUTOR-DETECTED]:** Task file was absent from all Kanban directories despite Orchestrator metadata; recreated at the exact Orchestrator-specified path (same pattern as RD-01/RD-02).
  - **Rationale:** XML block contained the full spec; halting would block the hotfix.
  - **Alternatives considered:** HALT and request clarification.
  - **Impact:** Single-source-of-truth maintained.

## Risk & Rollback

- **Risk:** `check_same_thread=False` relaxes SQLite thread affinity; concurrent writes from poller/watchdog threads may surface `database is locked` under contention (SQLite default busy timeout).
- **Rollback plan:** Revert one line in `state.py`; add `timeout=`/busy-handler if locking appears. No schema change, non-destructive.
- **Risk:** Double cards if a task transitions to PENDING_TRIGGER between `scan_existing()` and `get_pending_trigger_tasks()` (narrow race).
- **Rollback plan:** Dedup already covers the common path; the race is benign (one extra card at most).

---

## Execution Log & Reasoning

**2026-08-31 — HOTFIX-01 applied (Plan→Execute→Observe):**

1. **Verify-before-apply:** Confirmed every symbol referenced by the proposed code exists: `gateway._ensure_poller` (gateway.py:82, idempotent), `gateway.send_task_trigger_card` (gateway.py:176), `watcher.scan_existing` (watcher.py:123), `state.get_pending_trigger_tasks` (state.py:171). Loop-engine is a uv project (`loop-engine/pyproject.toml`).
2. **Step 1:** `state.py:59` → `sqlite3.connect(str(self.db_path), check_same_thread=False)`. Thread-safe DB access for the watchdog poller/update-poll background threads.
3. **Step 2:** `boot_scan()` rewritten per spec + task_id dedup (see D2). `_ensure_poller()` added at method top.
4. **Step 3:** `main()` calls `gateway._ensure_poller()` right before `boot_scan()` (comment documents why: cards must not be sent while no poller is running).
5. **Observe:** First run → 245 passed, 2 failed. Analyzed both: (a) smoke test caught the double-card defect in the verbatim snippet → added dedup; (b) `test_load_config_from_repo_root` was **pre-existing** (out-of-band `loop-engine.jsonc` now carries the real `chat_id: 1247026399`) → minimal stale-assertion fix. Re-run → **247 passed, 0 failed**.
6. **Scope guard:** The out-of-band `loop-engine/loop-engine.jsonc` modification (Manager's 2026 config) was NOT touched and NOT staged. Files staged for this hotfix: `loop-engine/state.py`, `loop-engine/daemon.py`, `loop-engine/test_audit_fixes.py`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `b4117ba87ca52dd445bc023186916e5176709434`
<!-- END_GIT_DIFF -->