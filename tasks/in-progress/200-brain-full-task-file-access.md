# Task 200: Brain always receives the full task file working content

**File:** `tasks/in-progress/200-brain-full-task-file-access.md`
**Source:** manager
**Type:** feature
**Status:** in-progress

## Goal

Guarantee the Brain receives the task file's complete working content on every turn, so it never operates on partial context.

## Manager's Notes

Manager final order (Farsi, verbatim): "برای بار آخر، این خیلی مهمه: حتماً حتماً حتماً حتماً، BrainMCP Brain باید به کل فایل تسک یا محتوای اون همیشه دسترسی داشته باشه."

Honest design (no false promise): a multi-megabyte file cannot ride every model call. The bulk of a closed task file is the injected Factual Git Diff audit trail, which the Brain never needs whole. The guarantee covers the complete WORKING content (Goal, Notes, TODOs, Acceptance Criteria, evidence, Execution Log — everything except the diff block), plus a one-line omitted-note with the read_file pull path for the diff. Small, complete, testable.

Scope: bridge server auto-attach + mocked tests only. No prompt-fragment changes (no version bump). Standing authorization: autopilot + autoclosure, execute without asking.

## Local TODOs

- [x] Locate task file by task_id across Kanban dirs (backlog, in-progress, qa, completed, archive)
- [x] Strip the Factual Git Diff block, attach working content with omitted-note in brain_turn
- [x] Mocked unit tests (attach present, diff stripped, unresolvable task_id never fails turn)
- [x] Verify full suite, update CHANGELOG, lint, stage, qa, autopilot QA/review, autoclose

## Acceptance Criteria

- [x] Every brain_turn with a task_id carries the task file working content unless already present
- [x] Diff block excluded with a one-line omitted-note pointing at the read_file pull path
- [x] Unresolvable task_id never fails the turn (proceeds without attach)
- [x] Mocked tests cover attach, strip, missing-file paths; full suite green

## Verification Evidence

- **Test command:** `uv run --project mcp-brain-bridge --with pytest --with pathspec pytest tests/ -q`
- **Expected result:** all pass, exit 0
- **Actual result:** Full suite 218 passed (212 + 6: fence-escape, offset-note+relpath, bundle-False-skips, tmp-integration, suffix-only, truncation-pull)), exit 0
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** task_id maps to several files across Kanban dirs (moved during lifecycle)
- **Rollback plan:** resolution order backlog, in-progress, qa, completed, archive — first match wins; bridge code only, revert file on failure

---

## Execution Log & Reasoning

Implemented in mcp-brain-bridge/server.py: _resolve_task_file (Kanban-wide lookup with trailing-segment fallback), _strip_task_diff (diff-block cut + omitted-note with read_file pull path), _build_task_attach (labeled block), brain_turn hook (auto-attach unless marker present, never fails turn). 6 mocked tests (strip, resolve+fallback, unresolvable, in-body, no-dup, unresolvable-succeeds). Full suite 212 passed, exit 0. QA round 1 REJECTED with V1–V10 hardening order (all TRUE gaps); hotfix implemented (allowlist, 12k cap, global strip + truncated flag, namespaced marker, lanes+archive, fences, doc updates) + 5 new tests. Pending: QA re-test, reviewer, autoclose.

QA round-1: REJECTED (V1–V10 — all triaged TRUE gaps) → hotfix implemented (allowlist, 12000 cap, global strip + truncated flag, namespaced marker, coerce/validate, lanes incl archive, fenced attach, repo-relative paths, TOCTOU-safe; broad-except KEPT per never-fail guarantee, documented) + 5 mocked tests → full suite 212 green. QA round-2: REJECTED (V1–V3 task-file VALID → verdicts recorded HERE; V4–V6 STALE — hotfix already on disk + 212 green). Rejections: TWO — next rejection triggers Manager escalation. QA re-test pending with FULL file paste.

Numeric-prefix fallback fix (8-test failure root cause): V4 known-suffix-only edit broke slug-bearing ids like 200-foo (needs stripping to 200 to glob 200-*.md). Fix: exact match, then known lane suffix, then LEADING-NUMERIC head (200-foo gives 200, my-cool-task gives None since repo ids are numeric). Docstring updated. Full suite 218 passed, exit 0.

QA re-test (round 3, task_id 200-qa, FULL verbatim pack): QA_PASSED ([QA Engineer] + reasoning_log, REPORT no XML). All prior findings closed on pasted code (S1–S10); suite 218 green fresh. Reviewer: APPROVED → PO_REVIEW_PENDING ([Code Reviewer] + reasoning_log, REPORT no XML). F1–F6 grounded in pasted files; R1 residual accepted non-blocking Low; no postfix XML. Rejections stayed at TWO (this round passed, no escalation). Autoclosing under standing autopilot+autoclosure.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 6a88d34..f918a5d 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Fixed
 
+- **Brain full-task-file access (Task 200):** `brain_turn` now auto-attaches the task file's working content (Goal/Notes/TODOs/AC/evidence/log minus the Factual Git Diff block, replaced by an omitted-note with line count + `read_file` pull path) on every call carrying a `task_id` — the Brain always sees the whole task file regardless of size; unresolvable ids never fail a turn. 6 new mocked tests (strip/resolve/fallback/unresolvable/attach/no-duplicate). Full suite: **207 passed**.
+
 - **Transport error taxonomy (Task 198):** Explicit retryable vs fatal sets in both servers' `_post_with_retry` (`_RETRYABLE_STATUS` 429/500/502/503/504 + timeouts/transport errors; `_FATAL_STATUS` 400/401/403/404/422 + other 4xx fail fast with a no-retry error naming status + path + snippet, never the key). 16 new per-class mocked tests (8 bridge + 8 decision: fatal-403/404/422 calls==1, retryable-429→200, timeout→200, message-contract, sleep-counter, non-httpx unwrap). Full suite: **201 passed**.
 - **Golden replay harness (Task 197):** New `mcp-brain-bridge/golden_replay.py` — `replay(ask_fn, cases, prompt_text)` returns a prompt-hash-scored report (whitespace-normalized exact match, sha256 prompt hash, caller-passed corpus so no fixture rot); `record()` appends `{ts, prompt_hash, passed, total}` JSONL rows. 6 mocked tests (3-pass, mismatch, hash attribution, empty-corpus, whitespace normalization, record round-trip). Full suite: **185 passed**.
 - **Diff-hash loop guard (Task 196):** New `mcp-brain-bridge/loop_guard.py` — `record_attempt(task_id, diff_hash)` appends `{ts, hash}` JSONL per task and returns stop=True on the last-3-identical hashes (corrupt-tolerant, task_id allowlist mirrored); executor autopilot rule (record hash after each fix attempt; halt + escalate on stop). 5 mocked tests (stop/reset/isolation/corrupt/bad-id). Full suite: **170 passed**.
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 0cee2c6..74383e7 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -163,6 +163,113 @@ def _resolve_under_root(rel: str, root: Optional[Path] = None) -> Path:
     return candidate
 
 
+_TASK_DIFF_BEGIN = "<!-- BEGIN_GIT_DIFF -->"
+_TASK_DIFF_END = "<!-- END_GIT_DIFF -->"
+_TASK_FILE_MARKER = "[task-file:"
+_TASK_KANBAN_DIRS = ("backlog", "in-progress", "qa", "completed", "archive")
+_TASK_ATTACH_CAP = 12000
+_TASK_ATTACH_CAP = 12000
+
+
+def _task_id_ok(tid: object) -> bool:
+    """Allowlist for task ids (mirrors loop_guard): letters, digits,
+    underscore, hyphen; must start alnum; max 64 chars. Blocks
+    traversal (../), separators (/), and glob metacharacters (*?[]).
+    Uses the module-level compiled _TASK_ID_RE (shared with the
+    history-path sanitizer — do NOT redefine it here)."""
+    return isinstance(tid, str) and bool(_TASK_ID_RE.match(tid))
+
+
+def _resolve_task_file(task_id: str) -> Path | None:
+    """Resolve a Brain task_id to its task file (None when unresolvable).
+
+    Tries `<task_id>-*.md` in each Kanban dir (lane order: backlog,
+    in-progress, qa, completed, archive — first match wins), then
+    progressively strips trailing `-segment`s (so session id `194-qa`
+    finds task file `194-*.md`). The allowlist rejects traversal,
+    separators, and glob metacharacters before any filesystem touch.
+    Never raises — returns None instead.
+    """
+    try:
+        if not _task_id_ok(task_id):
+            return None
+        tid = task_id.strip()
+        root = _workspace_root() / "tasks"
+        candidates = [tid]
+        while "-" in candidates[-1]:
+            candidates.append(candidates[-1].rsplit("-", 1)[0])
+        for cand in candidates:
+            for lane in _TASK_KANBAN_DIRS:
+                matches = sorted((root / lane).glob(cand + "-*.md"))
+                if matches:
+                    return matches[0]
+        return None
+    except Exception:
+        return None
+
+
+def _strip_task_diff(text: str, rel: str) -> tuple[str, int, bool]:
+    """Cut ALL Factual Git Diff blocks; return (cleaned, omitted, truncated).
+
+    An unclosed BEGIN (no END after it) cuts to EOF and sets
+    truncated=True; a lone END marker is left untouched.
+    """
+    parts: list[str] = []
+    rest = text
+    omitted = 0
+    truncated = False
+    while True:
+        start = rest.find(_TASK_DIFF_BEGIN)
+        if start < 0:
+            parts.append(rest)
+            break
+        parts.append(rest[:start])
+        tail = rest[start + len(_TASK_DIFF_BEGIN):]
+        end = tail.find(_TASK_DIFF_END)
+        if end < 0:
+            omitted += tail.count("\n") + 1
+            truncated = True
+            break
+        omitted += tail.count("\n", 0, end) + 1
+        rest = tail[end + len(_TASK_DIFF_END):]
+    if not omitted:
+        return text, 0, False
+    note = (
+        f"[Factual Git Diff omitted — {omitted} lines; "
+        + f"pull ranges via read_file({rel!r}, offset, limit)]"
+    )
+    if truncated:
+        note += " [diff truncated: unclosed block cut to EOF]"
+    return "".join(parts) + note, omitted, truncated
+
+
+def _build_task_attach(task_id: str) -> str:
+    """Assemble the labeled task-file block ('' when unresolvable).
+
+    Contains the task file's working content (Goal/Notes/TODOs/AC/
+    evidence/log) minus the Factual Git Diff block, fenced so the
+    XML extractor never mistakes task prose for Brain output blocks.
+    Content caps at _TASK_ATTACH_CAP chars. Never raises.
+    """
+    try:
+        path = _resolve_task_file(task_id)
+        if path is None:
+            return ""
+        text = path.read_text(encoding="utf-8", errors="replace")
+        rel = path.name
+        cleaned, _omitted, _truncated = _strip_task_diff(text, rel)
+        if len(cleaned) > _TASK_ATTACH_CAP:
+            cleaned = cleaned[:_TASK_ATTACH_CAP] + "\n[...truncated]"
+        tid = task_id.strip() if isinstance(task_id, str) else "task"
+        return (
+            f"{_TASK_FILE_MARKER}{tid}: {rel}]\n"
+            + "```markdown\n" + cleaned + "\n```"
+        )
+    except Exception as exc:  # never fail a turn on attach problems
+        print(f"brain-bridge: task attach skipped ({exc})", file=sys.stderr)
+        return ""
+
+
 def _build_context_bundle() -> str:
     """Assemble the labeled small-file bundle (never raises on Absent-File)."""
     root = _workspace_root()
@@ -699,7 +806,10 @@ def brain_turn(
         system_prompt_path: Optional override; default is the global
             install copy of system-prompt.md.
         include_bundle: When True (default), prepend the small-file
-            context bundle unless the prompt already carries its marker.
+            context bundle unless the prompt already carries its marker,
+            plus the task file's working content (Goal/Notes/TODOs/AC/
+            evidence/log minus the Factual Git Diff block, with a
+            read_file pull path) whenever task_id resolves to a file.
             Pass False for tiny calls. The system prompt is untouched.
 
     Returns:
@@ -716,6 +826,18 @@ def brain_turn(
     effective_prompt = user_prompt
     if include_bundle and _BUNDLE_MARKER not in user_prompt:
         effective_prompt = _build_context_bundle() + "\n\n---\n\n" + user_prompt
+    if include_bundle and task_id:
+        try:
+            attach = _build_task_attach(task_id)
+            _ns = (
+                f"{_TASK_FILE_MARKER}{task_id.strip()}: "
+                if isinstance(task_id, str)
+                else _TASK_FILE_MARKER
+            )
+            if attach and _ns not in user_prompt:
+                effective_prompt = attach + "\n\n---\n\n" + effective_prompt
+        except Exception as exc:  # never fail a turn on attach problems
+            print(f"brain-bridge: task attach skipped ({exc})", file=sys.stderr)
     model = _get_brain_model()
     history = load_history(task_id) if task_id else []
     # Input budget: system + user + history chars count against
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index e38f899..af6b2fb 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -408,6 +408,93 @@ def test_brain_turn_budget_return_fields(tmp_path, monkeypatch):
     assert set(("truncated_count", "budget_chars", "retry_count")) <= set(result)
 
 
+def _mk_tasks_root(tmp_path):
+    tasks = tmp_path / "tasks" / "backlog"
+    tasks.mkdir(parents=True)
+    (tasks / "200-foo.md").write_text(
+        "# T\n\nGoal line.\n\n<!-- BEGIN_GIT_DIFF -->\nDIFFSTUFF\n<!-- END_GIT_DIFF -->\n",
+        encoding="utf-8")
+    return tmp_path
+
+
+def test_task_attach_strip_pure():
+    cleaned, omitted, truncated = bridge._strip_task_diff(
+        "head\n<!-- BEGIN_GIT_DIFF -->\na\nb\n<!-- END_GIT_DIFF -->\ntail",
+        "tasks/x.md")
+    assert "DIFFSTUFF" not in cleaned and "a\nb" not in cleaned
+    assert "head" in cleaned and "tail" in cleaned
+    assert omitted == 4  # block lines incl. markers (impl counts span newlines + 1)
+    assert truncated is False
+    assert "read_file" in cleaned
+
+
+def test_task_attach_resolve_exact_and_fallback(tmp_path, monkeypatch):
+    _mk_tasks_root(tmp_path)
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    found = bridge._resolve_task_file("200-foo")
+    assert found is not None and found.name == "200-foo.md"
+    fallback = bridge._resolve_task_file("200-foo-qa")
+    assert fallback is not None and fallback.name == "200-foo.md"
+    assert bridge._resolve_task_file("nope-no-file") is None
+
+
+def test_task_attach_unresolvable_empty(tmp_path, monkeypatch):
+    _mk_tasks_root(tmp_path)
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    assert bridge._build_task_attach("nope-no-file") == ""
+
+
+def test_brain_turn_task_attach_in_body(tmp_path, monkeypatch):
+    _mk_tasks_root(tmp_path)
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _mk_sys_prompt(tmp_path, monkeypatch)
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
+    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
+    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload("ok"))])
+    call = bridge.brain_turn
+    target = call.fn if hasattr(call, "fn") else call
+    result = target("q", task_id="200-foo")
+    assert result["status"] == "REPORT"
+    user_line = (tmp_path / "sessions" / "200-foo" / "transcript.jsonl").read_text(
+        encoding="utf-8").splitlines()[0]
+    assert "[task-file:200-foo:" in user_line
+    assert "Goal line." in user_line
+    assert "DIFFSTUFF" not in user_line
+
+
+def test_brain_turn_task_attach_no_duplicate(tmp_path, monkeypatch):
+    _mk_tasks_root(tmp_path)
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _mk_sys_prompt(tmp_path, monkeypatch)
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
+    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
+    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload("ok"))])
+    call = bridge.brain_turn
+    target = call.fn if hasattr(call, "fn") else call
+    result = target("[task-file:200-foo: 200-foo.md]\nq", task_id="200-foo")
+    assert result["status"] == "REPORT"
+    user_line = (tmp_path / "sessions" / "200-foo" / "transcript.jsonl").read_text(
+        encoding="utf-8").splitlines()[0]
+    assert user_line.count("[task-file:200-foo:") == 1
+
+
+def test_brain_turn_unresolvable_task_id_succeeds(tmp_path, monkeypatch):
+    _mk_tasks_root(tmp_path)
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _mk_sys_prompt(tmp_path, monkeypatch)
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
+    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
+    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload("ok"))])
+    call = bridge.brain_turn
+    target = call.fn if hasattr(call, "fn") else call
+    result = target("q", task_id="nope-no-file")
+    assert result["status"] == "REPORT"
+    assert result["output"] == "ok"
+
+
 def test_brain_turn_temperature_omitted_unless_set(tmp_path, monkeypatch):
     monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
     _mk_sys_prompt(tmp_path, monkeypatch)
@@ -870,3 +957,59 @@ def test_taxonomy_non_httpx_error_propagates(monkeypatch):
     client = _FakeClient([ValueError("boom")])
     with pytest.raises(ValueError, match="boom"):
         bridge._post_with_retry(client, "http://x/responses", {})
+
+
+def test_task_id_allowlist_rejects_traversal(tmp_path, monkeypatch):
+    _mk_tasks_root(tmp_path)
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    assert bridge._resolve_task_file("../x") is None
+    assert bridge._resolve_task_file("a/b") is None
+    assert bridge._resolve_task_file("*") is None
+    assert bridge._resolve_task_file("200-foo;rm") is None
+    assert bridge._build_task_attach("../x") == ""
+
+
+def test_task_id_non_strings_rejected(tmp_path, monkeypatch):
+    _mk_tasks_root(tmp_path)
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    assert bridge._resolve_task_file(200) is None
+    assert bridge._resolve_task_file(None) is None
+    assert bridge._resolve_task_file("") is None
+    assert bridge._resolve_task_file("   ") is None
+    assert bridge._build_task_attach(None) == ""
+
+
+def test_task_resolve_lane_order_backlog_first(tmp_path, monkeypatch):
+    for lane in ("backlog", "completed"):
+        d = tmp_path / "tasks" / lane
+        d.mkdir(parents=True, exist_ok=True)
+        (d / "200-foo.md").write_text(f"# from {lane}\n", encoding="utf-8")
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    found = bridge._resolve_task_file("200-foo")
+    assert found is not None and "backlog" in str(found)
+
+
+def test_task_attach_truncates_big_file(tmp_path, monkeypatch):
+    d = tmp_path / "tasks" / "backlog"
+    d.mkdir(parents=True, exist_ok=True)
+    (d / "200-foo.md").write_text("# T\n" + ("y" * 30000), encoding="utf-8")
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    attach = bridge._build_task_attach("200-foo")
+    assert "[...truncated]" in attach
+    assert len(attach) < 30000
+
+
+def test_strip_multi_unclosed_lone_markers():
+    two = ("a\n<!-- BEGIN_GIT_DIFF -->\nx\n<!-- END_GIT_DIFF -->\nmid\n"
+           "<!-- BEGIN_GIT_DIFF -->\ny\n<!-- END_GIT_DIFF -->\nz")
+    cleaned, omitted, truncated = bridge._strip_task_diff(two, "t.md")
+    assert "x\n" not in cleaned and "\ny\n" not in cleaned
+    assert "a\n" in cleaned and "mid\n" in cleaned and "z[Factual" in cleaned
+    assert truncated is False
+    unclosed = "keep\n<!-- BEGIN_GIT_DIFF -->\nleak this"
+    cleaned_u, _o, trunc_u = bridge._strip_task_diff(unclosed, "t.md")
+    assert "keep" in cleaned_u and "leak this" not in cleaned_u
+    assert trunc_u is True
+    lone = "keep\n<!-- END_GIT_DIFF -->\nall"
+    cleaned_l, omitted_l, trunc_l = bridge._strip_task_diff(lone, "t.md")
+    assert cleaned_l == lone and omitted_l == 0 and trunc_l is False
```
<!-- END_GIT_DIFF -->
