# Task 234: Brain sessions per project under tasks sessions dir

**File:** `tasks/qa/234-brain-sessions-per-project-tasks-dir.md`
**Source:** manager
**Type:** bug
**Status:** open

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
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 56a716a..1892e25 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -12,6 +12,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Decision follow-up hardening H1/H2/H3 + B2 live proof (Task 231):** fingerprint path now tolerates a stray string `verbatim_quote`/`extracted_decision` (H1), skips tampered non-dict store files in both the duplicate scan and the index rewrite instead of crashing (H2), and treats explicit `None` optionals as unset so safe defaults still apply (H3). B2 live evidence: `extract_session_decisions(231)` fired at close handling and returned `[]` loudly (no session transcript in headless run — nothing queued, nothing written). 3 new regression tests. Full decision suite: **101 passed**.
 - **Brain empty-output retry hint + prompt-size warn (Task 232):** `mcp-brain-bridge/server.py` no longer returns a silent blank REPORT — root cause confirmed in code: `parse_responses_text` yields `""` on missing/non-list output and `brain_turn` forwarded it with no guard. A single choke-point guard now substitutes the machine-readable `EMPTY_OUTPUT_RETRY` hint (fixed token, lean-retry shape: same task_id, `include_bundle=false`, escalate if still empty; verdict content never invented, status stays REPORT so old callers keep working), plus a stderr advisory when the prompt exceeds 60k chars (oversized prompts correlated with both observed flakes). `agents/cognitive-executor.md` Empty-output clause now names the token. 6 new offline tests (hint contract, missing/None/whitespace payloads, normal passthrough, stderr warn). Full suite: **345 passed**.
 - **Supervised autopilot with plan approval and seat routing (Task 233):** `agents/cognitive-executor.md` gains a supervised plan-approval section (discovery feed → Brain plan → one approval pause → seat-routed implementation; Relay questions and hard blockers are the only other interrupts), a Seat Check trigger-citation line, a goal-pause carve-out for plan approval, and generous lock-word recognition. `mcp-brain-bridge/server.py` gains a 150 KB total bundle cap (truncate/skip with notes) and a text `validate_plan_verdict` checker (5 fields; cites need path:line shape). `docs/conventions.md` gains risk tiers T0/T1/T2 plus a 3-tries-then-escalate contract. `skill-templates/telegram-issue-sync/SKILL.md` folds the GitHub-preference data question into the planning turn (repo + global copies). Shipped prompt rebuilt to 9.36.0 with a Supervised Autopilot Contract bullet (authority stays in the executor file). 5 new offline bridge tests. Full suite: **350 passed**. Postfix: verdict checker uses word-bound field matching (stub text inside longer words no longer validates), bundle truncation reserves suffix length so the total never exceeds the cap, contract bullet reworded to a single plan-approval pause.
+- **Brain sessions per project, legacy global read-through (Task 234):** `mcp-brain-bridge/loop_guard.py` gains `project_sessions_root()` (explicit override → param/`BRAIN_PROJECT_ROOT`/`BRAIN_WORKSPACE_ROOT` → cwd walk-up to a `tasks/` dir → legacy global fallback) plus `legacy_sessions_root()`; `server.py` threads an optional `project_root` through `_sessions_root`, `_transcript_path`, `_fed_context_path`, `load_history`, `append_turn`, `save/load_fed_context`, and `brain_turn` — writes always land per project under `tasks/.sessions/<id>/`, while reads fall back to the legacy global dir with a loud stderr note when the per-project file is missing. HQ folders 230-233 migrated from the global store into `tasks/.sessions/` with a sha256 manifest (`/tmp/migrate-234-manifest.json`), globals kept as fallback. 4 new offline regression tests. Full suite: **354 passed**. Hotfix: no-global-write (fallback writes reroute to `cwd/tasks/.sessions` with stderr warn), package-then-plain sibling import, per-project loop-guard hashes with legacy read fallback, per-turn sessions-root stderr line, 3 more tests (T5-T7). Full suite: **357 passed**.
 
 ## [9.35.0] - 2026-09-14
 
diff --git a/mcp-brain-bridge/loop_guard.py b/mcp-brain-bridge/loop_guard.py
index 3d298bb..ae0647e 100644
--- a/mcp-brain-bridge/loop_guard.py
+++ b/mcp-brain-bridge/loop_guard.py
@@ -14,6 +14,7 @@ fix attempt). Pure local logic — no network, no model calls.
 import json
 import os
 import re
+import sys
 import time
 from pathlib import Path
 from typing import Any, Optional
@@ -26,18 +27,97 @@ _TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
 _SPIN_COUNT = 3
 
 
+#: Project layout marker: a project root holds a ``tasks/`` dir; its Brain
+#: sessions live under ``<root>/tasks/.sessions/`` (gitignored) instead of
+#: one global folder shared by every project.
+_PROJECT_TASKS_DIR = "tasks"
+_SESSIONS_DIR = ".sessions"
+
+#: How far up from cwd to look for a project root (bounds the walk).
+_WALK_UP_LIMIT = 5
+
+
+def _legacy_sessions_root() -> Path:
+    """Pre-per-project global sessions dir (read fallback only)."""
+    return Path.home() / ".config" / "opencode" / "brain-sessions"
+
+
+def legacy_sessions_root() -> Path:
+    """Public alias for the legacy global root (server read-fallback)."""
+    return _legacy_sessions_root()
+
+
+def _has_tasks_dir(candidate: Path) -> bool:
+    """True when ``candidate`` looks like a project root (has ``tasks/``)."""
+    try:
+        return (candidate / _PROJECT_TASKS_DIR).is_dir()
+    except OSError:
+        return False
+
+
+def project_sessions_root(
+    explicit: Optional[str] = None,
+    project_root: Optional[str] = None,
+) -> Path:
+    """Resolve the sessions root for one project (never raises).
+
+    Order: explicit ``BRAIN_SESSIONS_ROOT`` (or ``explicit`` arg) wins so
+    tests keep control; then a ``project_root`` holding ``tasks/``
+    (param, then ``BRAIN_PROJECT_ROOT``, then ``BRAIN_WORKSPACE_ROOT``
+    env); then a walk up from cwd (max 5 levels) for a dir holding
+    ``tasks/``; finally the legacy global root. New writes always land
+    under ``<project>/tasks/.sessions/``; callers add legacy read
+    fallback so old projects keep working.
+    """
+    override = explicit or os.environ.get("BRAIN_SESSIONS_ROOT", "").strip()
+    if override:
+        return Path(override).expanduser()
+    candidates: list[Path] = []
+    if project_root:
+        candidates.append(Path(project_root).expanduser())
+    for env_key in ("BRAIN_PROJECT_ROOT", "BRAIN_WORKSPACE_ROOT"):
+        env_val = os.environ.get(env_key, "").strip()
+        if env_val:
+            candidates.append(Path(env_val).expanduser())
+    for cand in candidates:
+        try:
+            resolved = cand.resolve()
+        except OSError:
+            continue
+        if _has_tasks_dir(resolved):
+            return resolved / _PROJECT_TASKS_DIR / _SESSIONS_DIR
+    try:
+        cwd = Path.cwd().resolve()
+    except OSError:
+        cwd = None
+    if cwd is not None:
+        node: Optional[Path] = cwd
+        for _ in range(_WALK_UP_LIMIT + 1):
+            if node is None:
+                break
+            if _has_tasks_dir(node):
+                return node / _PROJECT_TASKS_DIR / _SESSIONS_DIR
+            node = node.parent if node.parent != node else None
+    return _legacy_sessions_root()
+
+
 def _sessions_root(explicit: Optional[str] = None) -> Path:
-    base = explicit or os.environ.get(
-        "BRAIN_SESSIONS_ROOT",
-        str(Path.home() / ".config" / "opencode" / "brain-sessions"),
-    )
-    return Path(base)
+    if explicit:
+        return Path(explicit)
+    if os.environ.get("BRAIN_SESSIONS_ROOT", "").strip():
+        return Path(os.environ["BRAIN_SESSIONS_ROOT"].strip()).expanduser()
+    return project_sessions_root()
 
 
-def _hashes_path(task_id: str, sessions_root: Optional[str] = None) -> Path:
+def _hashes_path(task_id: str, sessions_root: Optional[str] = None,
+                 project_root: Optional[str] = None) -> Path:
     if not _TASK_ID_RE.match(task_id or ""):
         raise ValueError(f"bad task_id for loop guard: {task_id!r}")
-    return _sessions_root(sessions_root) / task_id / "loop_hashes.jsonl"
+    if project_root and not sessions_root:
+        root = project_sessions_root(project_root=project_root)
+    else:
+        root = _sessions_root(sessions_root)
+    return root / task_id / "loop_hashes.jsonl"
 
 
 def _read_hashes(path: Path) -> list[str]:
@@ -60,7 +140,8 @@ def _read_hashes(path: Path) -> list[str]:
 
 
 def record_attempt(
-    task_id: str, diff_hash: str, sessions_root: Optional[str] = None
+    task_id: str, diff_hash: str, sessions_root: Optional[str] = None,
+    project_root: Optional[str] = None,
 ) -> dict[str, Any]:
     """Record one fix-attempt hash; report whether the loop is spinning.
 
@@ -81,11 +162,24 @@ def record_attempt(
     if not isinstance(diff_hash, str) or not diff_hash.strip():
         raise ValueError(f"bad diff_hash for loop guard: {diff_hash!r}")
     clean = diff_hash.strip()
-    path = _hashes_path(task_id, sessions_root)
+    path = _hashes_path(task_id, sessions_root, project_root)
     path.parent.mkdir(parents=True, exist_ok=True)
     with path.open("a", encoding="utf-8") as fh:
         fh.write(json.dumps({"ts": time.time(), "hash": clean}) + "\n")
     history = _read_hashes(path)
+    if not history:
+        # Legacy read fallback: old hashes written before per-project
+        # scoping keep counting until the new path has its own history.
+        legacy = _legacy_sessions_root() / task_id / "loop_hashes.jsonl"
+        if legacy != path:
+            legacy_history = _read_hashes(legacy)
+            if legacy_history:
+                print(
+                    "loop-guard: using legacy global hashes for "
+                    f"{task_id} (unmigrated)",
+                    file=sys.stderr,
+                )
+                history = legacy_history
     tail = history[-_SPIN_COUNT:]
     stop = len(tail) == _SPIN_COUNT and len(set(tail)) == 1
     return {"stop": stop, "history": tail}
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 47c0a05..b414bba 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -76,6 +76,29 @@ _loaded_from = _load_env_files()
 if _loaded_from is not None:
     print(f"brain-bridge: loaded env from {_loaded_from}", file=sys.stderr)
 
+# Shared per-project sessions resolver lives in loop_guard (stdlib-only,
+# zero coupling back to this module). Guarded import so the server never
+# fails to load when run from an installed package without the sibling.
+try:
+    from mcp_brain_bridge.loop_guard import (  # type: ignore[import-not-found]
+        legacy_sessions_root as _shared_legacy_root,
+        project_sessions_root as _shared_project_root,
+    )
+except ImportError:
+    try:
+        from loop_guard import (  # type: ignore[import-not-found]
+            legacy_sessions_root as _shared_legacy_root,
+            project_sessions_root as _shared_project_root,
+        )
+    except ImportError:  # pragma: no cover - sibling missing
+        print(
+            "brain-bridge: loop_guard sibling missing under both import names; "
+            "per-project sessions disabled, legacy global applies",
+            file=sys.stderr,
+        )
+        _shared_project_root = None  # type: ignore[assignment]
+        _shared_legacy_root = None  # type: ignore[assignment]
+
 mcp = FastMCP("BrainBridge")
 
 # XML blocks the Brain may emit. Hands executes these; everything else
@@ -821,14 +844,89 @@ _HISTORY_LIMIT = 40
 _INPUT_BUDGET = 100000
 
 
-def _sessions_root() -> Path:
-    """Sessions root; override via ``BRAIN_SESSIONS_ROOT``."""
+def _sessions_root(project_root: Optional[str] = None) -> Path:
+    """Per-project sessions root: ``<project>/tasks/.sessions``.
+
+    Resolution lives in ``loop_guard.project_sessions_root`` (single
+    resolver, no duplicated logic): explicit ``BRAIN_SESSIONS_ROOT``
+    wins, then project-root candidates holding ``tasks/``, then a cwd
+    walk-up, then the legacy global dir. When the sibling is
+    unavailable, fall back to the legacy global path so old projects
+    keep working.
+    """
+    if _shared_project_root is not None:
+        return _shared_project_root(project_root=project_root)
     override = os.environ.get("BRAIN_SESSIONS_ROOT", "").strip()
     if override:
         return Path(override).expanduser()
+    # Sibling missing: best-effort per-project walk-up mirroring the
+    # resolver order (param, env roots, cwd walk-up), else legacy global.
+    cands: list[Path] = []
+    if project_root:
+        cands.append(Path(project_root).expanduser())
+    for _key in ("BRAIN_PROJECT_ROOT", "BRAIN_WORKSPACE_ROOT"):
+        _val = os.environ.get(_key, "").strip()
+        if _val:
+            cands.append(Path(_val).expanduser())
+    try:
+        cands.append(Path.cwd())
+    except OSError:
+        pass
+    for _cand in cands:
+        try:
+            _node = _cand.resolve()
+        except OSError:
+            continue
+        for _ in range(6):
+            try:
+                if (_node / "tasks").is_dir():
+                    return _node / "tasks" / ".sessions"
+            except OSError:
+                break
+            if _node.parent == _node:
+                break
+            _node = _node.parent
+    return Path.home() / ".config" / "opencode" / "brain-sessions"
+
+
+def _legacy_sessions_root() -> Path:
+    """Pre-per-project global root (read fallback for unmigrated history)."""
+    if _shared_legacy_root is not None:
+        return _shared_legacy_root()
     return Path.home() / ".config" / "opencode" / "brain-sessions"
 
 
+def _write_sessions_root(project_root: Optional[str] = None) -> Path:
+    """Sessions root for WRITES: per-project, never the legacy global.
+
+    An explicit ``BRAIN_SESSIONS_ROOT`` override is honored as-is (the
+    operator chose it). Otherwise, when the resolver can only offer the
+    legacy global fallback, writes go to ``cwd/tasks/.sessions`` with a
+    loud stderr warn instead — a new write must never reintroduce
+    cross-project bleed into the global dir. Reads keep the legacy
+    fallback (see ``load_history``/``load_fed_context``).
+    """
+    override = os.environ.get("BRAIN_SESSIONS_ROOT", "").strip()
+    if override:
+        return Path(override).expanduser()
+    root = _sessions_root(project_root)
+    if root != _legacy_sessions_root():
+        return root
+    print(
+        "brain-bridge: no project root found; writing to "
+        "cwd/tasks/.sessions instead of legacy global",
+        file=sys.stderr,
+    )
+    try:
+        return Path.cwd() / "tasks" / ".sessions"
+    except OSError:
+        print(
+            "brain-bridge: cwd unavailable; keeping legacy global write",
+            file=sys.stderr,
+        )
+        return root
+
+
 def _sanitize_task_id(task_id: str) -> str:
     """Strict allowlist — task ids become directory names, so anything
     outside ``^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$`` (``..``, separators,
@@ -841,8 +939,31 @@ def _sanitize_task_id(task_id: str) -> str:
     return task_id
 
 
-def _transcript_path(task_id: str) -> Path:
-    return _sessions_root() / _sanitize_task_id(task_id) / "transcript.jsonl"
+def _transcript_path(task_id: str, project_root: Optional[str] = None) -> Path:
+    return (
+        _sessions_root(project_root)
+        / _sanitize_task_id(task_id)
+        / "transcript.jsonl"
+    )
+
+
+def _write_transcript_path(task_id: str,
+                           project_root: Optional[str] = None) -> Path:
+    """Transcript path for WRITES (per-project; never legacy global)."""
+    return (
+        _write_sessions_root(project_root)
+        / _sanitize_task_id(task_id)
+        / "transcript.jsonl"
+    )
+
+
+def _legacy_transcript_path(task_id: str) -> Path:
+    """Legacy global transcript (read fallback until migration copies it)."""
+    return (
+        _legacy_sessions_root()
+        / _sanitize_task_id(task_id)
+        / "transcript.jsonl"
+    )
 
 
 #: Per-line size guard (R5): one monster line can't blow memory on read.
@@ -978,7 +1099,8 @@ def _compact_locked(path: Path) -> tuple[list[dict[str, Any]], int]:
     return kept, skipped
 
 
-def load_history(task_id: str, limit: int = _HISTORY_LIMIT) -> list[dict[str, str]]:
+def load_history(task_id: str, limit: int = _HISTORY_LIMIT,
+                  project_root: Optional[str] = None) -> list[dict[str, str]]:
     """Read a task's prior turns (oldest first), capped at ``limit``.
     Missing file means a fresh task — returns []. Corrupt lines are
     skipped, never fatal; per-load stats land in ``_last_load_stats``
@@ -989,7 +1111,14 @@ def load_history(task_id: str, limit: int = _HISTORY_LIMIT) -> list[dict[str, st
     summaries merge into the new digest (never swallowed), the write
     is atomic, and concurrent appends queue behind the lock instead
     of being lost (see ``_build_compacted``)."""
-    path = _transcript_path(task_id)
+    path = _transcript_path(task_id, project_root)
+    if not path.is_file():
+        legacy = _legacy_transcript_path(task_id)
+        if legacy.is_file():
+            print("brain-bridge: reading legacy global session "
+                  f"({task_id}); migrate it under tasks/.sessions/",
+                  file=sys.stderr)
+            path = legacy
     if not path.is_file():
         _last_load_stats.update({"kept": 0, "skipped": 0})
         return []
@@ -1021,12 +1150,14 @@ _last_load_stats: dict[str, int] = {"kept": 0, "skipped": 0}
 
 
 def append_turn(task_id: str, role: str, content: str, model: Optional[str] = None,
-               prompt_hash: Optional[str] = None, truncated: int = 0) -> None:
+                prompt_hash: Optional[str] = None, truncated: int = 0,
+                project_root: Optional[str] = None) -> None:
     """Append one turn to the task transcript (creates dirs as needed).
 
     Traceability keys ride on every record; unset stays None/0 so
-    older callers keep working unchanged."""
-    path = _transcript_path(task_id)
+    older callers keep working unchanged. Writes always go to the
+    per-project path, never to the legacy global dir."""
+    path = _write_transcript_path(task_id, project_root)
     path.parent.mkdir(parents=True, exist_ok=True)
     record: dict[str, Any] = {
         "role": role, "content": content, "model": model,
@@ -1056,9 +1187,33 @@ _FED_CONTEXT_FILE = "fed_context.md"
 _FED_CONTEXT_CAP = 20000
 
 
-def _fed_context_path(task_id: str) -> Path:
+def _fed_context_path(task_id: str,
+                        project_root: Optional[str] = None) -> Path:
     """Pinned fed-context file for a task (raises ValueError on bad id)."""
-    return _sessions_root() / _sanitize_task_id(task_id) / _FED_CONTEXT_FILE
+    return (
+        _sessions_root(project_root)
+        / _sanitize_task_id(task_id)
+        / _FED_CONTEXT_FILE
+    )
+
+
+def _legacy_fed_context_path(task_id: str) -> Path:
+    """Legacy global fed-context file (read fallback until migrated)."""
+    return (
+        _legacy_sessions_root()
+        / _sanitize_task_id(task_id)
+        / _FED_CONTEXT_FILE
+    )
+
+
+def _write_fed_context_path(task_id: str,
+                              project_root: Optional[str] = None) -> Path:
+    """Fed-context path for WRITES (per-project; never legacy global)."""
+    return (
+        _write_sessions_root(project_root)
+        / _sanitize_task_id(task_id)
+        / _FED_CONTEXT_FILE
+    )
 
 
 def extract_fed_context(prompt: object) -> str:
@@ -1085,14 +1240,15 @@ def extract_fed_context(prompt: object) -> str:
     return "\n".join(lines[start:end]).strip()
 
 
-def save_fed_context(task_id: str, content: str) -> None:
+def save_fed_context(task_id: str, content: str,
+                     project_root: Optional[str] = None) -> None:
     """Pin fed discovery context (atomic write, capped).
 
     Raises ValueError on invalid task id; IO problems are logged and
     skipped, never raised. Empty content deletes the pin. Oversize
-    content truncates with a note.
+    content truncates with a note. Writes always go per-project.
     """
-    path = _fed_context_path(task_id)
+    path = _write_fed_context_path(task_id, project_root)
     if not content.strip():
         try:
             path.unlink(missing_ok=True)
@@ -1117,10 +1273,19 @@ def save_fed_context(task_id: str, content: str) -> None:
               file=sys.stderr)
 
 
-def load_fed_context(task_id: str) -> str:
-    """Read pinned fed context ('' when none; never raises)."""
+def load_fed_context(task_id: str,
+                     project_root: Optional[str] = None) -> str:
+    """Read pinned fed context ('' when none; never raises).
+
+    Falls back to the legacy global file so unmigrated pins keep
+    working; new pins are always written per-project."""
     try:
-        return _fed_context_path(task_id).read_text(
+        return _fed_context_path(task_id, project_root).read_text(
+            encoding="utf-8", errors="replace").strip()
+    except (OSError, ValueError):
+        pass
+    try:
+        return _legacy_fed_context_path(task_id).read_text(
             encoding="utf-8", errors="replace").strip()
     except (OSError, ValueError):
         return ""
@@ -1196,6 +1361,7 @@ def brain_turn(
     include_bundle: bool = True,
     include_diff: bool = False,
     context_paths: Optional[list[str]] = None,
+    project_root: Optional[str] = None,
 ) -> dict[str, Any]:
     """Send one Brain turn.
 
@@ -1233,6 +1399,11 @@ def brain_turn(
             under the workspace root with the read suffix allowlist;
             per-file cap plus total budget apply, problems become explicit
             unavailable labels. Default off. Small pulls stay inline.
+        project_root: Optional project dir holding ``tasks/``. Its
+            ``tasks/.sessions/`` stores this turn's history (per-project
+            sessions). When omitted the resolver tries
+            ``BRAIN_PROJECT_ROOT`` / ``BRAIN_WORKSPACE_ROOT`` / cwd
+            walk-up, then falls back to legacy reads.
 
     Returns:
         {"status": "XML_EXTRACTED"|"REPORT", "xml_blocks": [...],
@@ -1303,7 +1474,12 @@ def brain_turn(
             print(f"brain-bridge: diff attach skipped ({exc})",
                   file=sys.stderr)
     model = _get_brain_model()
-    history = load_history(task_id) if task_id else []
+    if task_id:
+        # Sessions-root visibility: one debug line per turn so a
+        # misrouted project is observable in stderr, never silent.
+        print(f"brain-bridge: sessions root {_sessions_root(project_root)} "
+              f"(task {task_id})", file=sys.stderr)
+    history = load_history(task_id, project_root=project_root) if task_id else []
     if task_id:
         # Discovery-fed planning: a [fed-context] block in this prompt is
         # pinned to the session, then the pin (not just this turn's copy)
@@ -1313,8 +1489,8 @@ def brain_turn(
         try:
             fed = extract_fed_context(effective_prompt)
             if fed:
-                save_fed_context(task_id, fed)
-            pinned = load_fed_context(task_id)
+                save_fed_context(task_id, fed, project_root=project_root)
+            pinned = load_fed_context(task_id, project_root=project_root)
             if pinned and "[pinned-fed-context]" not in effective_prompt:
                 effective_prompt = (
                     "[pinned-fed-context]\n" + pinned
@@ -1392,9 +1568,11 @@ def brain_turn(
     if task_id:
         prompt_hash = hashlib.sha256(effective_prompt.encode("utf-8")).hexdigest()
         append_turn(task_id, "user", effective_prompt, model=model,
-                    prompt_hash=prompt_hash, truncated=truncated_count)
+                    prompt_hash=prompt_hash, truncated=truncated_count,
+                    project_root=project_root)
         append_turn(task_id, "assistant", output, model=model,
-                    prompt_hash=prompt_hash, truncated=truncated_count)
+                    prompt_hash=prompt_hash, truncated=truncated_count,
+                    project_root=project_root)
     result: dict[str, Any] = {
         "status": "XML_EXTRACTED" if xml_blocks else "REPORT",
         "xml_blocks": xml_blocks,
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index edc7e9c..796fdb0 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -1507,3 +1507,114 @@ def test_plan_verdict_cites_without_lines():
     plan = "verdict: ok\nseats: A\npath: p\nsteps: s\ncites: some files somewhere"
     problems = bridge.validate_plan_verdict(plan)
     assert any("file path with lines" in p for p in problems)
+
+
+def _mk_project(tmp_path, name):
+    proj = tmp_path / name
+    (proj / "tasks").mkdir(parents=True)
+    return proj
+
+
+def _clean_session_env(monkeypatch):
+    for key in ("BRAIN_SESSIONS_ROOT", "BRAIN_PROJECT_ROOT",
+                "BRAIN_WORKSPACE_ROOT"):
+        monkeypatch.delenv(key, raising=False)
+
+
+def test_per_project_roots_differ_by_project(tmp_path, monkeypatch):
+    _clean_session_env(monkeypatch)
+    proj_a = _mk_project(tmp_path, "proj_a")
+    proj_b = _mk_project(tmp_path, "proj_b")
+    root_a = bridge._sessions_root(project_root=str(proj_a))
+    root_b = bridge._sessions_root(project_root=str(proj_b))
+    assert root_a == proj_a / "tasks" / ".sessions"
+    assert root_b == proj_b / "tasks" / ".sessions"
+    assert root_a != root_b
+
+
+def test_no_tasks_dir_falls_back_to_legacy(tmp_path, monkeypatch):
+    _clean_session_env(monkeypatch)
+    bare = tmp_path / "bare"
+    bare.mkdir()
+    monkeypatch.chdir(bare)
+    assert bridge._sessions_root() == bridge._legacy_sessions_root()
+
+
+def test_legacy_global_transcript_read_through(tmp_path, monkeypatch):
+    fake_home = tmp_path / "home"
+    fake_home.mkdir()
+    monkeypatch.setenv("HOME", str(fake_home))
+    _clean_session_env(monkeypatch)
+    bare = tmp_path / "bare"
+    bare.mkdir()
+    monkeypatch.chdir(bare)
+    # Plant a pre-migration global file directly: append_turn now refuses
+    # to write to the legacy global dir (no-global-write rule), so the
+    # legacy fixture must be written by hand.
+    planted = (fake_home / ".config" / "opencode" / "brain-sessions"
+               / "t3legacy" / "transcript.jsonl")
+    planted.parent.mkdir(parents=True, exist_ok=True)
+    planted.write_text(
+        '{"role": "user", "content": "legacy hello", "model": null, '
+        '"prompt_hash": null, "truncated": 0}\n', encoding="utf-8")
+    assert planted.is_file()
+    proj = _mk_project(tmp_path, "proj_read")
+    monkeypatch.chdir(proj)
+    turns = bridge.load_history("t3legacy")
+    assert any(t.get("content") == "legacy hello" for t in turns)
+
+
+def test_fresh_write_goes_per_project(tmp_path, monkeypatch):
+    _clean_session_env(monkeypatch)
+    proj = _mk_project(tmp_path, "proj_write")
+    monkeypatch.chdir(proj)
+    bridge.append_turn("t4fresh", "user", "fresh hello")
+    fresh = (proj / "tasks" / ".sessions" / "t4fresh" / "transcript.jsonl")
+    assert fresh.is_file()
+    assert "fresh hello" in fresh.read_text(encoding="utf-8")
+
+
+def test_writes_avoid_legacy_global_when_no_root(tmp_path, monkeypatch, capsys):
+    # T5: bare cwd (no tasks/ anywhere up except tmp freshness) + fake
+    # HOME: append_turn must land in cwd/tasks/.sessions, never global.
+    fake_home = tmp_path / "home5"
+    fake_home.mkdir()
+    monkeypatch.setenv("HOME", str(fake_home))
+    _clean_session_env(monkeypatch)
+    bare = tmp_path / "bare5"
+    bare.mkdir()
+    monkeypatch.chdir(bare)
+    bridge.append_turn("t5noglobal", "user", "no bleed")
+    local = bare / "tasks" / ".sessions" / "t5noglobal" / "transcript.jsonl"
+    assert local.is_file()
+    legacy = (fake_home / ".config" / "opencode" / "brain-sessions"
+              / "t5noglobal" / "transcript.jsonl")
+    assert not legacy.exists()
+    assert "instead of legacy global" in capsys.readouterr().err
+
+
+def test_loop_guard_isolation_by_project(tmp_path, monkeypatch):
+    # T6: same task id in two projects keeps separate spin state.
+    from loop_guard import record_attempt
+    _clean_session_env(monkeypatch)
+    proj_a = _mk_project(tmp_path, "proj_ga")
+    proj_b = _mk_project(tmp_path, "proj_gb")
+    ra = record_attempt("t6spin", "aaa", project_root=str(proj_a))
+    rb = record_attempt("t6spin", "bbb", project_root=str(proj_b))
+    assert ra == {"stop": False, "history": ["aaa"]}
+    assert rb == {"stop": False, "history": ["bbb"]}
+    assert (proj_a / "tasks" / ".sessions" / "t6spin" / "loop_hashes.jsonl").is_file()
+    assert (proj_b / "tasks" / ".sessions" / "t6spin" / "loop_hashes.jsonl").is_file()
+
+
+def test_sibling_missing_still_resolves_per_project(tmp_path, monkeypatch):
+    # T7: even when the loop_guard sibling import fails, the local
+    # walk-up fallback resolves a project holding tasks/.
+    _clean_session_env(monkeypatch)
+    proj = _mk_project(tmp_path, "proj_pkg")
+    monkeypatch.chdir(proj)
+    monkeypatch.setattr(bridge, "_shared_project_root", None)
+    monkeypatch.setattr(bridge, "_shared_legacy_root", None)
+    assert bridge._sessions_root() == proj / "tasks" / ".sessions"
+    assert bridge._sessions_root(project_root=str(proj)) == (
+        proj / "tasks" / ".sessions")
```
<!-- END_GIT_DIFF -->
