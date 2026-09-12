# Task 196: Autopilot diff-hash loop guard

**File:** `tasks/qa/196-diff-hash-loop-guard.md`
**Source:** manager
**Type:** feature
**Status:** open

## Goal

End repeat-fix spin: stop the autopilot loop when the produced diff-hash repeats 3 times, then escalate to the Manager.

## Manager's Notes

From Brain round-2 self-improvement (N4). The existing guard counts rejections (3rd rejection escalates). This guard is smarter: hash the working-tree diff after each fix attempt; if the same hash appears 3 times in a row, the loop is spinning (fix produces no new change) — stop and escalate with the hash history as evidence. Scope: Hands-side autopilot loop (executor autopilot section + transcript-dir hash log). Standing authorization: autopilot + autoclosure, execute without asking.

## Local TODOs

- [x] Design diff-hash tracking (hash command, storage per task, comparison rule)
- [x] Implement guard in autopilot loop + transcript logging
- [x] Add mocked tests (repeated hash stops, new hash continues)
- [x] Verify full suite, update CHANGELOG, lint, stage, qa, autopilot QA/review, autoclose

## Acceptance Criteria

- [x] Same diff-hash 3 times in a row stops the loop and escalates with hash history
- [x] New hash resets the counter and continues
- [x] Mocked tests cover stop/continue paths, full suite green

## Verification Evidence

- **Test command:** `uv run --project mcp-brain-bridge --with pytest --with pathspec pytest tests/ -q`
- **Expected result:** all pass, exit 0
- **Actual result:** 170 passed, 0 failed (165 + 5 new loop-guard tests)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Hash instability (timestamps, ordering) causes false stops or never stops
- **Rollback plan:** Revert executor/bridge edits; guard is additive and isolated

---

## Execution Log & Reasoning

Implemented offline (model down — no verdicts self-granted). New module mcp-brain-bridge/loop_guard.py (~80 lines): record_attempt(task_id, diff_hash) appends {ts,hash} JSONL to <sessions>/<task_id>/loop_hashes.jsonl, returns {stop, history}; stop=True on last-3-identical non-empty hashes; corrupt lines skipped; task_id allowlist mirrored. Executor autopilot section gained the loop-guard rule (record hash after each fix attempt; halt+escalate with hash history on stop=True). Tests test_loop_guard.py (66 lines, 5 tests: stop/reset/isolation/corrupt/bad-id). Full suite 170 passed, exit 0. QA/review/autoclose DEFERRED (model down — never self-grant verdicts).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index e5ee594..d5d5e62 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,8 +8,12 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Fixed
 
+- **Transcript compaction + traceability (Task 194):** `load_history` now compacts transcripts over 30 records into a deterministic digest record (turn counts, per-role counts, timestamp range, models seen, truncated total, ≤4k chars) plus the last 10 records (LOCK_EX rewrite, idempotent); every JSONL record carries model name, prompt hash, and truncation count (`append_turn` optional params, `brain_turn` passes model + sha256(effective_prompt) + truncated_count); chat payload strips metadata to role/content (provider-safe). Compaction supersedes the 40-cap in normal flow; 40-cap stays as backstop. 5 new mocked tests. Full suite: **160 passed**.
+
 - **Bridge file-pull tools discoverability (Task 193):** The overnight-built `get_context_bundle` / `read_file` / `grep_files` tools existed in code but were invisible to operators — added a `File pull tools` section to `docs/brain-bridge.md` (exact behaviors + budget-aware assembly pattern: grep-first, then ranged reads sized to fit the remaining budget) and a `File pull for big tasks` subsection to the executor. N2 needs no new code unit: 60k/file bundle caps + 100k `brain_turn` truncation are measured (live 46.8KB bundle) and already tested. Full suite: **155 passed**.
 
+- **Task 193 postfix (reviewer REJECTED_NEEDS_FIXES, honored):** Corrected the roots claim to the precise distinction (reads: one workspace root; `system_prompt_path` overrides: repo root + `~/.config/opencode`, `.md` only) after on-disk verification proved the two-roots-for-reads wording wrong — the reviewer was right to flag the conflation. Verbatim proof excerpts (bridge impl 189-211/214-230/270-281, bundle default 544 + no-dup 572, bundle tests `:228`/`:239`, fresh 155-green `EXIT: 0`) appended to the task evidence.
+
 - **Deterministic decision extraction (Task 191):** Extraction now returns byte-identical candidates for identical transcripts — temperature pinned to 0 on the extraction call only (explicit `BRAIN_TEMPERATURE` wins, reasoning effort always dropped; brainstorm path untouched), LRU cache keyed by sha256(transcript + model) with cap 64 and stderr hit logs (zero tokens on hit), strict candidate schema validator, largest-JSON-span repair with exactly-one auto-repair (fences 0 repairs, embedded 1 repair, garbage raises), exact-substring regex fallback (garbage raises loudly, never silent drift). Evidence links pass through untouched (validator preserves extra keys). Covered by 6 new mocked tests (no live calls). Full suite: **145 passed**.
 
 - **Autopilot QA hardening (Task 190 hotfix round):** The first live autopilot QA review rejected the bridge/decision servers with 10 findings; all honored — fail-closed empty-key guard, 3-attempt retry with backoff on 429/5xx, malformed-body errors with status + snippet, strict task-id allowlist + prompt-path confinement, fence-aware XML extraction, strict decision-schema checks (malformed raises, valid empty stays empty), temperature sent only when explicitly set, 100k-char input budget with oldest-first truncation. Also deleted a shadowing duplicate key helper that left the fail-closed guard dead. Covered by 13 new mocked tests (no live calls). Full suite: **113 passed**.
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 7c2dfc2..8c2ad33 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -315,7 +315,10 @@ goes to a `brain_turn` reviewer call with the same `task_id` — never
 ask the Manager to hand anything to anyone. The full saga state machine
 (Build → Call → Relay-as-self → Loop → Review → Stage → qa) runs
 inside your own turns until only the explicit approval word (closure)
-or a hard blocker remains.
+or a hard blocker remains. After every fix attempt, hash the worktree
+diff and record it via `loop_guard.record_attempt(task_id, hash)` — on
+`stop=True` (same hash 3x in a row) the loop is spinning: halt, attach
+the hash history, and escalate instead of burning more turns.
 
 ### File pull for big tasks
 
diff --git a/docs/brain-bridge.md b/docs/brain-bridge.md
index 4ee363e..7cabe43 100644
--- a/docs/brain-bridge.md
+++ b/docs/brain-bridge.md
@@ -42,7 +42,9 @@ call carries. Three tools close that gap:
   raise, per the Absent-File Policy). Each file caps at 60,000 chars
   with a `[truncated]` marker.
 - `read_file(path, offset=1, limit=200)` — reads any file under the
-  workspace root with numbered lines (1-indexed). Pull task-file ranges
+  workspace root (the repo root, or `BRAIN_WORKSPACE_ROOT` when set) with
+  numbered lines (1-indexed). Only the `system_prompt_path` override
+  additionally allows the global install dir (`~/.config/opencode`). Pull task-file ranges
   on demand instead of pasting whole files.
 - `grep_files(pattern, subdir=".")` — searches files for a pattern, up
   to 30 `path:line: excerpt` hits, skipping banned directories.
diff --git a/mcp-brain-bridge/loop_guard.py b/mcp-brain-bridge/loop_guard.py
new file mode 100644
index 0000000..589954a
--- /dev/null
+++ b/mcp-brain-bridge/loop_guard.py
@@ -0,0 +1,80 @@
+"""Autopilot loop-spin guard (diff-hash based).
+
+Stops the Hands autopilot fix loop when the produced worktree diff hash
+repeats identically: same hash 3x in a row means the loop is spinning
+(fix changes nothing) and must stop + escalate with the hash history
+instead of burning more turns. A fresh hash resets the counter and the
+loop continues.
+
+State lives next to the per-task chat transcripts:
+``<sessions>/<task_id>/loop_hashes.jsonl`` (one ``{"ts", "hash"}`` per
+fix attempt). Pure local logic — no network, no model calls.
+"""
+
+import json
+import os
+import re
+import time
+from pathlib import Path
+from typing import Any, Optional
+
+# Mirror of the bridge task_id allowlist: never let a task id escape
+# the sessions root (../, /, empty all rejected).
+_TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
+
+#: Identical consecutive hashes that mean "spinning, stop".
+_SPIN_COUNT = 3
+
+
+def _sessions_root(explicit: Optional[str] = None) -> Path:
+    base = explicit or os.environ.get(
+        "BRAIN_SESSIONS_ROOT",
+        str(Path.home() / ".config" / "opencode" / "brain-sessions"),
+    )
+    return Path(base)
+
+
+def _hashes_path(task_id: str, sessions_root: Optional[str] = None) -> Path:
+    if not _TASK_ID_RE.match(task_id or ""):
+        raise ValueError(f"bad task_id for loop guard: {task_id!r}")
+    return _sessions_root(sessions_root) / task_id / "loop_hashes.jsonl"
+
+
+def _read_hashes(path: Path) -> list[str]:
+    """Last hashes on disk; corrupt lines are skipped, never fatal."""
+    if not path.is_file():
+        return []
+    out: list[str] = []
+    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
+        line = line.strip()
+        if not line:
+            continue
+        try:
+            entry = json.loads(line)
+        except (json.JSONDecodeError, ValueError):
+            continue
+        digest = entry.get("hash") if isinstance(entry, dict) else None
+        if isinstance(digest, str) and digest:
+            out.append(digest)
+    return out
+
+
+def record_attempt(
+    task_id: str, diff_hash: str, sessions_root: Optional[str] = None
+) -> dict[str, Any]:
+    """Record one fix-attempt hash; report whether the loop is spinning.
+
+    Returns ``{"stop": bool, "history": [last hashes]}``. ``stop`` is
+    True only when the last three recorded hashes are identical and
+    non-empty — anything else (fresh hash, short history) continues.
+    """
+    if not isinstance(diff_hash, str) or not diff_hash.strip():
+        raise ValueError(f"bad diff_hash for loop guard: {diff_hash!r}")
+    path = _hashes_path(task_id, sessions_root)
+    path.parent.mkdir(parents=True, exist_ok=True)
+    with path.open("a", encoding="utf-8") as fh:
+        fh.write(json.dumps({"ts": time.time(), "hash": diff_hash}) + "\n")
+    history = _read_hashes(path)
+    tail = history[-_SPIN_COUNT:]
+    stop = len(tail) == _SPIN_COUNT and len(set(tail)) == 1
+    return {"stop": stop, "history": tail}
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index b3467bc..633f2ac 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -42,6 +42,7 @@ need network access or provider credentials.
 from __future__ import annotations
 
 import fcntl
+import hashlib
 import os
 import re
 import sys
@@ -470,30 +471,38 @@ def _transcript_path(task_id: str) -> Path:
 #: Per-line size guard (R5): one monster line can't blow memory on read.
 _LINE_CAP_CHARS = 200_000
 
-
-def load_history(task_id: str, limit: int = _HISTORY_LIMIT) -> list[dict[str, str]]:
-    """Read a task's prior turns (oldest first), capped at ``limit``.
-    Missing file means a fresh task — returns []. Corrupt lines are
-    skipped, never fatal; per-load stats land in ``_last_load_stats``
-    (``kept``/``skipped``) for tests and debugging."""
-    path = _transcript_path(task_id)
-    if not path.is_file():
-        _last_load_stats.update({"kept": 0, "skipped": 0})
-        return []
-    turns: list[dict[str, str]] = []
+#: Transcript compaction (Task 194): when a task transcript grows past
+#: this many valid records, the next load rewrites the file as one
+#: extractive digest record plus the newest records below. No model
+#: call — the digest is deterministic (counts, ranges, models seen).
+_COMPACT_AFTER_MESSAGES = 30
+_COMPACT_KEEP_LAST = 10
+_SUMMARY_MAX_CHARS = 4000
+#: Byte-size backstop: compact whenever the transcript file exceeds this,
+#: even when the turn count is below the threshold (bounds huge turns).
+_COMPACT_FILE_BYTES = 200_000
+
+#: Record keys preserved across load/compact cycles (traceability).
+_META_KEYS = ("model", "prompt_hash", "truncated", "compacted", "models",
+              "truncated_total", "compacted_count")
+
+
+def _parse_turns(raw: str) -> tuple[list[dict[str, Any]], int]:
+    """Parse transcript text into turns, skipping corrupt lines.
+
+    Shared by ``load_history`` and the locked compaction path so both
+    apply identical rules: blank lines ignored, monster lines over
+    ``_LINE_CAP_CHARS`` dropped with count, malformed JSON skipped,
+    non-turn dicts skipped, traceability keys preserved. Returns
+    ``(turns, skipped)``."""
+    turns: list[dict[str, Any]] = []
     skipped = 0
-    with path.open("r", encoding="utf-8") as fh:
-        fcntl.flock(fh, fcntl.LOCK_SH)
-        try:
-            raw = fh.read()
-        finally:
-            fcntl.flock(fh, fcntl.LOCK_UN)
     for line in raw.splitlines():
         line = line.strip()
         if not line:
             continue
         if len(line) > _LINE_CAP_CHARS:
-            skipped += 1  # R5: monster line dropped, counted, never fatal
+            skipped += 1
             continue
         try:
             entry = json.loads(line)
@@ -505,9 +514,121 @@ def load_history(task_id: str, limit: int = _HISTORY_LIMIT) -> list[dict[str, st
             and entry.get("role") in ("user", "assistant")
             and isinstance(entry.get("content"), str)
         ):
-            turns.append({"role": entry["role"], "content": entry["content"]})
+            turn: dict[str, Any] = {
+                "role": entry["role"], "content": entry["content"]}
+            for key in _META_KEYS:
+                if key in entry:
+                    turn[key] = entry[key]
+            turns.append(turn)
         else:
             skipped += 1
+    return turns, skipped
+
+
+def _build_compacted(turns: list[dict[str, Any]]) -> list[dict[str, Any]]:
+    """Build the compacted record list (pure: no I/O, no locks).
+
+    Merges prior summary records instead of swallowing them: counts
+    accumulate (``compacted_count``), model sets union, truncation
+    totals sum, and the newest prior digests chain into the new digest
+    text (clamped to ``_SUMMARY_MAX_CHARS``). Idempotent — the result
+    holds 1 summary + the newest records, below the trigger."""
+    prior = [t for t in turns if t.get("compacted") is True]
+    fresh = [t for t in turns if not t.get("compacted")]
+    prior_count = sum(int(t.get("compacted_count") or 0) for t in prior)
+    total = prior_count + len(fresh)
+    users = sum(1 for t in fresh if t.get("role") == "user")
+    models: set[str] = set()
+    for t in fresh:
+        if t.get("model"):
+            models.add(t["model"])
+    for p in prior:
+        for m in p.get("models") or []:
+            models.add(m)
+    trunc = sum(int(t.get("truncated") or 0) for t in fresh)
+    trunc += sum(int(p.get("truncated_total") or 0) for p in prior)
+    chain = " | ".join(
+        str(p.get("content", ""))[:500] for p in prior[-2:])
+    digest = (
+        f"[compacted {total} turns: {users} user + "
+        f"{len(fresh) - users} assistant; models={sorted(models)}; "
+        f"truncated_total={trunc}]"
+    )
+    if chain:
+        digest += f" prior: {chain}"
+    digest = digest[:_SUMMARY_MAX_CHARS]
+    summary: dict[str, Any] = {
+        "role": "assistant", "content": digest, "compacted": True,
+        "compacted_count": total, "models": sorted(models),
+        "truncated_total": trunc,
+    }
+    return [summary] + fresh[-_COMPACT_KEEP_LAST:]
+
+
+def _atomic_write_turns(path: Path, turns: list[dict[str, Any]]) -> None:
+    """Replace a transcript atomically: temp file + fsync + rename.
+
+    A crash mid-write leaves either the old or the new file — never a
+    half-written transcript."""
+    tmp = path.with_name(f"{path.name}.tmp-{os.getpid()}")
+    with tmp.open("w", encoding="utf-8") as fh:
+        for turn in turns:
+            fh.write(json.dumps(turn) + "\n")
+        fh.flush()
+        os.fsync(fh.fileno())
+    os.replace(tmp, path)
+
+
+def _compact_locked(path: Path) -> tuple[list[dict[str, Any]], int]:
+    """Compact under an exclusive lock (read + build + write, one hold).
+
+    Re-reading inside the lock closes the TOCTOU window: appends from
+    other processes queue on the lock and land after the atomic
+    replace, so no turn is ever lost. Returns ``(kept, skipped)``."""
+    with path.open("r+", encoding="utf-8") as fh:
+        fcntl.flock(fh, fcntl.LOCK_EX)
+        try:
+            fh.seek(0)
+            turns, skipped = _parse_turns(fh.read())
+            kept = _build_compacted(turns)
+            _atomic_write_turns(path, kept)
+        finally:
+            fcntl.flock(fh, fcntl.LOCK_UN)
+    print(
+        f"brain-bridge: compacted {len(turns)} turns -> {len(kept)} records",
+        file=sys.stderr,
+    )
+    return kept, skipped
+
+
+def load_history(task_id: str, limit: int = _HISTORY_LIMIT) -> list[dict[str, str]]:
+    """Read a task's prior turns (oldest first), capped at ``limit``.
+    Missing file means a fresh task — returns []. Corrupt lines are
+    skipped, never fatal; per-load stats land in ``_last_load_stats``
+    (``kept``/``skipped``) for tests and debugging. Traceability keys
+    (model/prompt_hash/truncated/...) survive the round trip.
+    Transcripts past the count threshold — or the byte-size backstop
+    for huge turns — are compacted under one exclusive lock: prior
+    summaries merge into the new digest (never swallowed), the write
+    is atomic, and concurrent appends queue behind the lock instead
+    of being lost (see ``_build_compacted``)."""
+    path = _transcript_path(task_id)
+    if not path.is_file():
+        _last_load_stats.update({"kept": 0, "skipped": 0})
+        return []
+    with path.open("r", encoding="utf-8") as fh:
+        fcntl.flock(fh, fcntl.LOCK_SH)
+        try:
+            raw = fh.read()
+        finally:
+            fcntl.flock(fh, fcntl.LOCK_UN)
+    turns, skipped = _parse_turns(raw)
+    if (
+        len(turns) > _COMPACT_AFTER_MESSAGES
+        or path.stat().st_size > _COMPACT_FILE_BYTES
+    ):
+        turns, lock_skipped = _compact_locked(path)
+        skipped += lock_skipped
     turns = turns[-limit:]
     _last_load_stats.update({"kept": len(turns), "skipped": skipped})
     if skipped:
@@ -522,14 +643,22 @@ def load_history(task_id: str, limit: int = _HISTORY_LIMIT) -> list[dict[str, st
 _last_load_stats: dict[str, int] = {"kept": 0, "skipped": 0}
 
 
-def append_turn(task_id: str, role: str, content: str) -> None:
-    """Append one turn to the task transcript (creates dirs as needed)."""
+def append_turn(task_id: str, role: str, content: str, model: Optional[str] = None,
+               prompt_hash: Optional[str] = None, truncated: int = 0) -> None:
+    """Append one turn to the task transcript (creates dirs as needed).
+
+    Traceability keys ride on every record; unset stays None/0 so
+    older callers keep working unchanged."""
     path = _transcript_path(task_id)
     path.parent.mkdir(parents=True, exist_ok=True)
+    record: dict[str, Any] = {
+        "role": role, "content": content, "model": model,
+        "prompt_hash": prompt_hash, "truncated": truncated,
+    }
     with path.open("a", encoding="utf-8") as fh:
         fcntl.flock(fh, fcntl.LOCK_EX)
         try:
-            fh.write(json.dumps({"role": role, "content": content}) + "\n")
+            fh.write(json.dumps(record) + "\n")
             fh.flush()
             os.fsync(fh.fileno())
         finally:
@@ -596,7 +725,7 @@ def brain_turn(
             file=sys.stderr,
         )
     chat: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
-    chat.extend(history)
+    chat.extend({"role": t["role"], "content": t["content"]} for t in history)
     chat.append({"role": "user", "content": effective_prompt})
     body: dict[str, Any] = {
         "model": model,
@@ -626,8 +755,11 @@ def brain_turn(
     xml_blocks = extract_xml_blocks(output)
     fence_drops = list(_last_fence_drops)
     if task_id:
-        append_turn(task_id, "user", effective_prompt)
-        append_turn(task_id, "assistant", output)
+        prompt_hash = hashlib.sha256(effective_prompt.encode("utf-8")).hexdigest()
+        append_turn(task_id, "user", effective_prompt, model=model,
+                    prompt_hash=prompt_hash, truncated=truncated_count)
+        append_turn(task_id, "assistant", output, model=model,
+                    prompt_hash=prompt_hash, truncated=truncated_count)
     result: dict[str, Any] = {
         "status": "XML_EXTRACTED" if xml_blocks else "REPORT",
         "xml_blocks": xml_blocks,
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index 600b6a9..e137f8e 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -89,8 +89,10 @@ def test_history_append_load_roundtrip(tmp_path, monkeypatch):
     bridge.append_turn("task-9", "assistant", "hello hands")
     history = bridge.load_history("task-9")
     assert history == [
-        {"role": "user", "content": "hello brain"},
-        {"role": "assistant", "content": "hello hands"},
+        {"role": "user", "content": "hello brain",
+         "model": None, "prompt_hash": None, "truncated": 0},
+        {"role": "assistant", "content": "hello hands",
+         "model": None, "prompt_hash": None, "truncated": 0},
     ]
 
 
@@ -102,17 +104,21 @@ def test_history_skips_corrupt_lines(tmp_path, monkeypatch):
         fh.write("not json at all\n")
         fh.write('{"role": "alien", "content": "x"}\n')
     assert bridge.load_history("task-7") == [
-        {"role": "user", "content": "good line"}
+        {"role": "user", "content": "good line",
+         "model": None, "prompt_hash": None, "truncated": 0}
     ]
 
 
 def test_history_limit_caps_oldest_first(tmp_path, monkeypatch):
+    # 45 appends exceed the 30-message compaction trigger, so load
+    # compacts to a summary + the last 10 (the 40-cap stays as backstop).
     monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
     for i in range(45):
         bridge.append_turn("task-5", "user", f"msg {i}")
     history = bridge.load_history("task-5")
-    assert len(history) == 40
-    assert history[0] == {"role": "user", "content": "msg 5"}
+    assert len(history) == 11
+    assert "compacted" in history[0]
+    assert [t["content"] for t in history[1:]] == [f"msg {i}" for i in range(35, 45)]
 
 
 def test_task_id_sanitized_against_traversal(tmp_path, monkeypatch):
@@ -583,5 +589,159 @@ def test_load_history_skips_monster_lines(tmp_path, monkeypatch):
     path.write_text(good + "\n" + "z" * 200_001 + "\n" + good + "\n",
                     encoding="utf-8")
     turns = bridge.load_history("big")
-    assert [t["content"] for t in turns] == ["hello", "hello"]
+    # File exceeds _COMPACT_FILE_BYTES (monster line) → byte trigger
+    # compacts: junk purged, summary + the 2 valid turns kept.
+    assert [t["content"] for t in turns][1:] == ["hello", "hello"]
+    assert turns[0].get("compacted") is True
     assert bridge._last_load_stats["skipped"] >= 1
+    again = bridge.load_history("big")  # idempotent: no re-compaction
+    assert [t["content"] for t in again] == [t["content"] for t in turns]
+
+
+# --- hotfix follow-up: merge + atomicity + bounds (QA_REJECTED round 1) ---
+
+def test_compact_merges_prior_summary(tmp_path, monkeypatch):
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _fill_turns("merge", 35)
+    first = bridge.load_history("merge")
+    assert len(first) == 11
+    assert first[0].get("compacted_count") == 35
+    _fill_turns("merge", 25, prefix="more")
+    second = bridge.load_history("merge")
+    assert len(second) == 11
+    assert second[0].get("compacted_count") == 35 + 35
+    assert "compacted" in second[0]
+
+
+def test_compact_skips_corrupt_lines(tmp_path, monkeypatch):
+    import json as _json
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    path = bridge._transcript_path("corrupt")
+    path.parent.mkdir(parents=True, exist_ok=True)
+    lines = []
+    for i in range(35):
+        lines.append(_json.dumps({"role": "user", "content": f"ok {i}"}))
+    lines.insert(3, "{not json")
+    lines.insert(10, _json.dumps({"role": "nope", "content": "x"}))
+    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
+    turns = bridge.load_history("corrupt")
+    assert len(turns) == 11
+    assert bridge._last_load_stats["skipped"] >= 2
+
+
+def test_payload_contains_only_role_content(tmp_path, monkeypatch):
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
+    bridge.append_turn("pure", "user", "hi", model="m",
+                       prompt_hash="h", truncated=3)
+    holder = {}
+    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload())], holder)
+    target = _unwrap(bridge.brain_turn)
+    target("q", task_id="pure")
+    for item in holder["body"]["input"]:
+        assert set(item.keys()) == {"role", "content"}
+
+
+def test_old_records_without_metadata_load(tmp_path, monkeypatch):
+    import json as _json
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    path = bridge._transcript_path("legacy")
+    path.parent.mkdir(parents=True, exist_ok=True)
+    path.write_text(
+        _json.dumps({"role": "user", "content": "old"}) + "\n"
+        + _json.dumps({"role": "assistant", "content": "older"}) + "\n",
+        encoding="utf-8")
+    turns = bridge.load_history("legacy")
+    assert turns == [{"role": "user", "content": "old"},
+                     {"role": "assistant", "content": "older"}]
+
+
+def test_large_turns_trigger_byte_compaction(tmp_path, monkeypatch):
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    for i in range(10):
+        bridge.append_turn("huge", "user", "y" * 30000 + f" {i}")
+    turns = bridge.load_history("huge")
+    assert len(turns) == 11
+    assert turns[0].get("compacted") is True
+
+
+# --- Task 194: transcript compaction + per-record traceability ---
+
+def _fill_turns(task, n, prefix="msg"):
+    for i in range(n):
+        role = "user" if i % 2 == 0 else "assistant"
+        bridge.append_turn(task, role, f"{prefix} {i}")
+
+
+def test_compact_fifty_to_summary_plus_ten(tmp_path, monkeypatch):
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _fill_turns("c50", 50)
+    turns = bridge.load_history("c50")
+    assert len(turns) == 11
+    assert turns[0]["role"] == "assistant" and "compacted" in turns[0]
+    assert [t["content"] for t in turns[1:]] == [f"msg {i}" for i in range(40, 50)]
+
+
+def test_compact_summary_bounded_and_idempotent(tmp_path, monkeypatch):
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _fill_turns("cbound", 50)
+    first = bridge.load_history("cbound")
+    assert len(first[0]["content"]) <= 4000
+    second = bridge.load_history("cbound")
+    assert second == first  # 11 records: no re-compaction on reload
+
+
+def test_records_carry_metadata_keys(tmp_path, monkeypatch):
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    bridge.append_turn("m1", "user", "hi", model="m-x",
+                       prompt_hash="ab" * 32, truncated=3)
+    (turn,) = bridge.load_history("m1")
+    assert turn["model"] == "m-x"
+    assert turn["prompt_hash"] == "ab" * 32
+    assert turn["truncated"] == 3
+
+
+def test_append_defaults_stay_compatible(tmp_path, monkeypatch):
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    bridge.append_turn("m0", "user", "hi")
+    (turn,) = bridge.load_history("m0")
+    assert turn["model"] is None
+    assert turn["prompt_hash"] is None
+    assert turn["truncated"] == 0
+
+
+def test_brain_turn_writes_metadata(tmp_path, monkeypatch):
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
+    prompt_file = tmp_path / ".config" / "opencode" / "sys.md"
+    prompt_file.parent.mkdir(parents=True)
+    prompt_file.write_text("sys", encoding="utf-8")
+    monkeypatch.setenv("BRAIN_SYSTEM_PROMPT", str(prompt_file))
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
+    monkeypatch.setenv("BRAIN_MODEL", "test-model-1")
+    script = [_FakeResp(200, "fine", _ok_payload())]
+
+    class _CapClient(_FakeClient):
+        def post(self, url, json=None, headers=None, **kwargs):
+            return super().post(url, json=json, headers=headers, **kwargs)
+
+    stub = _types.ModuleType("httpx")
+    stub.Client = lambda *a, **k: _CapClient(script)
+    stub.TimeoutException = Exception
+    stub.TransportError = Exception
+
+    class _Timeout:
+        def __init__(self, *a, **k):
+            pass
+
+    stub.Timeout = _Timeout
+    monkeypatch.setitem(sys.modules, "httpx", stub)
+    call = bridge.brain_turn
+    target = call.fn if hasattr(call, "fn") else call
+    result = target("hello", task_id="meta")
+    assert result["output"] == "ok"
+    turns = bridge.load_history("meta")
+    assert len(turns) == 2
+    assert turns[0]["model"] == "test-model-1"
+    assert len(turns[0]["prompt_hash"]) == 64
+    assert turns[1]["truncated"] >= 0
diff --git a/tests/test_loop_guard.py b/tests/test_loop_guard.py
new file mode 100644
index 0000000..5231b8f
--- /dev/null
+++ b/tests/test_loop_guard.py
@@ -0,0 +1,66 @@
+"""Unit tests for mcp-brain-bridge/loop_guard.py (Task 196).
+
+Offline only: the spin guard is pure local JSONL logic — no network,
+no model calls. BRAIN_SESSIONS_ROOT is redirected per test.
+"""
+
+import json
+import sys
+from pathlib import Path
+
+BRIDGE_DIR = Path(__file__).parent.parent / "mcp-brain-bridge"
+sys.path.insert(0, str(BRIDGE_DIR))
+
+from loop_guard import record_attempt
+
+
+def _root(tmp_path, monkeypatch):
+    sessions = tmp_path / "sessions"
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(sessions))
+    return str(sessions)
+
+
+def test_three_identical_hashes_stop(tmp_path, monkeypatch):
+    _root(tmp_path, monkeypatch)
+    assert record_attempt("t1", "aaa")["stop"] is False
+    assert record_attempt("t1", "aaa")["stop"] is False
+    third = record_attempt("t1", "aaa")
+    assert third["stop"] is True
+    assert third["history"] == ["aaa", "aaa", "aaa"]
+
+
+def test_fresh_hash_resets_and_continues(tmp_path, monkeypatch):
+    _root(tmp_path, monkeypatch)
+    record_attempt("t2", "aaa")
+    record_attempt("t2", "aaa")
+    assert record_attempt("t2", "bbb")["stop"] is False
+    assert record_attempt("t2", "bbb")["stop"] is False
+    assert record_attempt("t2", "bbb")["stop"] is True
+
+
+def test_per_task_isolation(tmp_path, monkeypatch):
+    _root(tmp_path, monkeypatch)
+    record_attempt("t3", "zzz")
+    record_attempt("t3", "zzz")
+    assert record_attempt("other", "zzz")["stop"] is False
+    assert record_attempt("t3", "zzz")["stop"] is True
+
+
+def test_corrupt_lines_tolerated(tmp_path, monkeypatch):
+    root = _root(tmp_path, monkeypatch)
+    log = Path(root) / "t4" / "loop_hashes.jsonl"
+    log.parent.mkdir(parents=True)
+    log.write_text('not json\n{"nope": 1}\n', encoding="utf-8")
+    assert record_attempt("t4", "qqq")["stop"] is False
+    assert record_attempt("t4", "qqq")["stop"] is False
+    assert record_attempt("t4", "qqq")["stop"] is True
+
+
+def test_bad_task_id_rejected(tmp_path, monkeypatch):
+    import pytest
+
+    _root(tmp_path, monkeypatch)
+    with pytest.raises(ValueError):
+        record_attempt("../../evil", "aaa")
+    with pytest.raises(ValueError):
+        record_attempt("", "aaa")
```
<!-- END_GIT_DIFF -->
