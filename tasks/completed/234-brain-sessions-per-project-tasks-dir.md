# Task 234: Brain sessions per project under tasks sessions dir

**File:** `tasks/completed/234-brain-sessions-per-project-tasks-dir.md`
**Source:** manager
**Type:** bug
**Status:** closed

## Goal

Stop Brain task history from bleeding across projects by storing sessions inside each project under its tasks sessions dir instead of one global folder.

## Manager's Notes

Manager picked option 3 from the Brain advisory: "use this path for each project ./tasks/.session". Hands use `tasks/.sessions/` (plural) to match the existing extraction reader (`extract_session_decisions` already reads `tasks/.sessions/{task_id}/transcript.jsonl`). Root cause confirmed by Brain: the bridge builds one global path from the bare task number, so same-numbered tasks in different projects share one folder under `~/.config/opencode/brain-sessions`. Evidence: global dir mixes `230`, `231`, `232`, `233` (this HQ) with `8`, `9`, `27`, `816`-`824`, `sprintrev`, `vision`, `190-bundle-proof`, etc.

## Local TODOs

- [x] Ground the plan: read session-path code in mcp-brain-bridge/server.py (sessions root, transcript path, fed-context path, history load/save)
- [x] Brain planning turn under this task id, then implement
- [x] Move existing HQ folders (230-233 plus older HQ numbers) into tasks/.sessions/
- [x] Verify functionality

## Acceptance Criteria

- [x] Same task number in two different project roots resolves to different session paths
- [x] Same project root plus same task number resolves to the same path
- [x] A history write in one project never appears in another project
- [x] Existing HQ session folders are migrated into tasks/.sessions/ with no data loss
- [x] Full test suite passes with exit code 0

## Verification Evidence

- **Test command:** uv-pinned pytest full suite (see task-generator notes for exact pins)
- **Expected result:** all tests pass, exit code 0
- **Actual result:** 357 passed (350 prior + T1-T4 + T5-T7 hotfix), 3.53s
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Other projects still on the global path keep working (their folders stay); only this project migrates. Wrong-path writes could orphan history mid-migration.
- **Rollback plan:** Keep a manifest of moved folders; move them back to the global root if the new resolver misbehaves.

---

## Execution Log & Reasoning

PLAN APPROVED (Architect single-seat planning turn; Designer skipped — no UI triggers; Programmer executes post-plan). Grounded plan: shared `_project_root()` resolver (BRAIN_SESSIONS_ROOT → project_root param → BRAIN_PROJECT_ROOT → BRAIN_WORKSPACE_ROOT → cwd walk-up max 5 → legacy read fallback); rewrite `_sessions_root()` to `<project>/tasks/.sessions`; unify id sanitization; loop_guard reuses shared resolver; migration copies HQ folders with manifest. Lite verdict: not eligible (multi-file + migration). Proceeding under autopilot approval.

Implementation done in mcp-brain-bridge/server.py + loop_guard.py (per-project resolver, threaded project_root, legacy read-through with stderr note). 4 regression tests T1-T4 added (bridge suite 137 passed; T3 needed a test-side fix — legacy root is HOME-based, planted via fake HOME). Migrated HQ folders 230-233 (10/14/9/11 transcript lines + 233 fed_context.md) into tasks/.sessions/ — all sha256 hashes match globals, manifest at /tmp/migrate-234-manifest.json, legacy copies kept as fallback. CHANGELOG Unreleased entry appended (restored a mistakenly truncated 233 line first — verified exact).

HOTFIX (QA_REJECTED verdict, same file): S1 CHANGELOG 234 entry de-duplicated (trailing 233 fragment removed, kept 4-test sentence + 354 count). S2 sibling import tries package name first, then plain, with loud stderr note when both miss. S3 no-global-write enforced: new _write_sessions_root (explicit override honored; legacy-fallback writes rerouted to cwd/tasks/.sessions with stderr warn); append_turn + save_fed_context use _write_transcript_path/_write_fed_context_path; legacy read fallbacks unchanged. S4 loop_guard _hashes_path/record_attempt gain project_root (scoped via project_sessions_root) + legacy hash read fallback with stderr note; server has no guard call sites (verified by grep). S5 brain_turn logs resolved sessions root to stderr once per turn. S6 manifest verified (5 files, folders 230/10, 231/14, 232/9, 233/11 lines + fed_context.md present); summary below.
```json
{"date": "2026-09-15", "project_root": "tasks/.sessions", "task_ids": ["230", "231", "232", "233"], "files": 5, "sha256": {"230/transcript.jsonl": "31945f6d…c2920d21", "231/transcript.jsonl": "4b494fdb…1486de539", "232/transcript.jsonl": "4d55feb6…a11d9f5e82", "233/transcript.jsonl": "e274d8be…dba765e461", "233/fed_context.md": "0db0e433…9df33710bc"}, "verified": "all per-project copies byte-identical to global originals"}
```

HOTFIX verification: py_compile clean (server, loop_guard, tests); T3 reworked to plant the legacy fixture by hand (append_turn now refuses global writes); T5-T7 added (no-global-write with stderr proof, loop-guard isolation, sibling-missing fallback). Bridge+guard suites: 148 passed. Full suite: 357 passed, exit 0. CHANGELOG 234 entry fixed + hotfix sentence appended. Micro-tasks S1-S8 all done.

Re-QA (second QA, same id, diff attached): QA_PASSED. Reviewer confirms AC1-AC5 hold (path split, same-root stability, no-global-write for new writes, 5-file manifest with matching hashes, 357 passed exit 0). Residuals logged as low/transitional: F1 legacy read fallback may show old global history on first read before first per-project write (stops after, stderr-logged); F2 no-root write fallback shares cwd dir only when server cwd is global (normal deploy uses per-project cwd or env root); F3 spin check does not merge legacy+new hashes (self-heals after 3 new entries). No code change for residuals — follow-up candidates only.

Review (same id, diff attached): Code Reviewer approves the code technically, status PO_REVIEW_PENDING. Strengths F1-F4 (shared per-project resolver, server delegation, traversal sanitizer, loud legacy stderr notes). Two low follow-ups, not implemented here: A1 explicit paths in loop guard skip expanduser (normalize in a follow-up); A2 server keeps a duplicate walk-up only as sibling-missing fallback. Closure awaits the Manager approval word.

Completeness audit (Manager asked, Brain judged, Hands proved A1-A4): A1 manifest now persists inside the workspace at tasks/.sessions/migrate-234-manifest.json (gitignored, survives /tmp wipes) with full sha256 hashes. A2 folders proven: tasks/.sessions/230,231,232,233 exist with transcript lines 10/14/9/11 plus 233/fed_context.md (4 lines), matching the manifest. A3 all 7 tests live in tests/test_brain_bridge.py: T1 per-project-roots-differ :1524, T2 no-tasks-fallback :1535, T3 legacy-read-through :1543, T4 fresh-write :1567, T5 no-global-write :1577, T6 guard-isolation :1596, T7 sibling-missing :1610. A4 truncated diff remainder reviewed by Hands directly: write-path variants (_write_transcript_path/_write_fed_context_path/_write_sessions_root with stderr warns), per-turn sessions-root stderr line, loop-guard project_root threading — all present in the injected diff. A5 stays with the Manager: PO approval word plus accept-or-task call on residuals F1-F3 and follow-ups A1-A2.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `8fa650da311279159a14d888be0cc78eb73b567b`
<!-- END_GIT_DIFF -->
