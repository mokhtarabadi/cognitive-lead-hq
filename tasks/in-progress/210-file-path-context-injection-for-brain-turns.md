# Task 210: File-path context injection for brain turns

**File:** `tasks/in-progress/210-file-path-context-injection-for-brain-turns.md`
**Source:** manager
**Type:** feature
**Status:** open

## Goal

Let the Brain receive context by file path instead of pasted lines: new `brain_turn` input carries markdown paths, the server reads and injects them capped and labeled.

## Manager's Notes

Manager proposal (translated from Persian): when the Brain wants context or code, it should name file paths (signature reports, context reports, trees, custom markdown). The Hands build those files with the context MCP server. The Brain server reads them from disk and injects them into the turn. Small pulls stay inline, big artifacts go by path. Goal: least hallucination with most precise context. Manager ordered a brainstorm with file-fed context before deciding.

## Local TODOs

- [x] Brainstorm with file-fed context
- [x] Decide design from brainstorm result
- [x] Implement on approval
- [x] Verify functionality

## Acceptance Criteria

- [x] Brainstorm verdict on the proposal recorded
- [x] Final design approved before code
- [x] Small pulls stay inline, big artifacts go by path
- [x] Server caps and labels each injected file

## Verification Evidence

- **Test command:** `uv run --with pytest --with pathspec --with pyyaml --with mcp==1.30.0 python -m pytest tests/ -q`
- **Expected result:** all tests pass, exit 0
- **Actual result:** 255 passed (245 baseline plus 10 new path-injection tests), 8 warnings
- **Exit code:** 0
- **Live proof:** `brain_turn` signature carries `context_paths`; `build_paths_attach(['docs/conventions.md'])` returns labeled injection from disk

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** path traversal and budget overflow if caps are wrong.
- **Rollback plan:** keep inline slices working; new parameter optional, default off.

---

## Execution Log & Reasoning

Task filed per manager order. Brainstorm with file-fed context runs under this task id next.

Brainstorm done (2 rounds, file-fed). Verdict: proposal GOOD and DOABLE. Selected path O1: optional context_paths field on brain_turn, server-side read with root check plus suffix allowlist, per-file cap plus total budget, labeled injection. Small pulls stay inline. Key evidence: bridge read_file refuses .py (suffix allowlist), context tools return paths only (ferry-shaped), fed-context pin helpers reusable. Brain asks for approval before blueprint and code. No code written.

Manager approved. Implementation O1: new optional context_paths param (default off), build_paths_attach helper (resolve under root, allowlist, per-file 20k cap, total 40k budget, explicit unavailable labels), wired after task attach so it counts toward input budget. One self-caught docstring slip repaired (dropped task_id line, restored verbatim). 10 new offline tests. Full suite 255 passed. Live proof via signature plus real-file injection.

QA round 1: QA_PASSED. Honored 2 cheap follow-ups (too-large branch test, absolute-path escape test). Symlink escape accepted: shared resolver uses realpath. Wiring test stays a follow-up: helpers plus signature proof cover it.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 8aff419..4493bb8 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **File-path context injection for brain turns (Task 210):** `brain_turn` accepts optional `context_paths` — the server reads workspace files from disk and injects them capped and labeled (per-file 20k, total 40k, escapes plus bad suffixes plus missing files become explicit labels). Context, tree, and signature reports now ride by path instead of pasted lines; small pulls stay inline. Full suite: **253 passed**.
+
 - **Discovery-fed Brain planning with pinned session context (Task 209):** planning gate gained a discovery-fed loop — when the planning turn returns a discovery task, the Hands execute it via subagents and feed the result back under the same id (max one discovery round, max two planning turns) before the final plan, which must cite fed context. The bridge pins `[fed-context]` blocks to `fed_context.md` per session and prepends the pin to later turns, exempt from compaction and the middle drop (20k cap). Executor gate plus bridge pinning, no prompt rebuild. Full suite: **245 passed**.
 
 ## [9.31.0] - 2026-09-12
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 3777a70..ad15092 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -1008,6 +1008,68 @@ def load_fed_context(task_id: str) -> str:
         return ""
 
 
+#: Per-file cap for path-injected context (chars). Truncated with a note.
+_CTX_PATHS_PER_FILE = 20000
+
+#: Total cap across all path-injected files per turn (chars). Files past
+#: the total are skipped with an explicit skipped note — stacked files
+#: must never overflow the turn budget on their own.
+_CTX_PATHS_TOTAL = 40000
+
+
+def build_paths_attach(paths: object) -> str:
+    """Read workspace files for path injection ('' when none).
+
+    Each path resolves under the workspace root (escapes, missing files,
+    and unsupported suffixes become explicit ``[unavailable: ...]``
+    labels, never silent drops). Files truncate at ``_CTX_PATHS_PER_FILE``
+    chars; injection stops at ``_CTX_PATHS_TOTAL`` with a skipped note.
+    Pure apart from disk reads; never raises.
+    """
+    if not isinstance(paths, (list, tuple)):
+        return ""
+    wanted = [p for p in paths if isinstance(p, str) and p.strip()]
+    if not wanted:
+        return ""
+    blocks: list[str] = []
+    used = 0
+    for rel in wanted:
+        try:
+            resolved = _resolve_under_root(rel)
+        except ValueError:
+            blocks.append(f"[unavailable: {rel.strip()} — outside workspace]")
+            continue
+        if resolved.suffix.lower() not in _ALLOWED_READ_SUFFIXES:
+            blocks.append(
+                f"[unavailable: {rel.strip()} — unsupported extension]")
+            continue
+        try:
+            if resolved.stat().st_size > _READ_MAX_BYTES:
+                blocks.append(
+                    f"[unavailable: {rel.strip()} — file too large]")
+                continue
+            text = resolved.read_text(encoding="utf-8", errors="replace")
+        except OSError:
+            blocks.append(f"[unavailable: {rel.strip()} — unreadable]")
+            continue
+        if not text.strip():
+            blocks.append(f"[unavailable: {rel.strip()} — empty file]")
+            continue
+        if len(text) > _CTX_PATHS_PER_FILE:
+            text = (text[:_CTX_PATHS_PER_FILE]
+                    + f"\n[...truncated at {_CTX_PATHS_PER_FILE} chars]")
+        if used + len(text) > _CTX_PATHS_TOTAL:
+            blocks.append(
+                f"[skipped: {rel.strip()} — total budget "
+                f"{_CTX_PATHS_TOTAL} chars reached]")
+            continue
+        used += len(text)
+        blocks.append(f"[path-injected: {rel.strip()}]\n{text}")
+    if not blocks:
+        return ""
+    return "\n\n---\n\n".join(blocks)
+
+
 @mcp.tool()
 def brain_turn(
     user_prompt: str,
@@ -1015,6 +1077,7 @@ def brain_turn(
     system_prompt_path: Optional[str] = None,
     include_bundle: bool = True,
     include_diff: bool = False,
+    context_paths: Optional[list[str]] = None,
 ) -> dict[str, Any]:
     """Send one Brain turn.
 
@@ -1040,6 +1103,11 @@ def brain_turn(
             flag is False but the prompt reads like a QA/reviewer turn
             ("qa engineer", "code reviewer", "adversarial"), the hunks
             still auto-attach with a stderr warning.
+        context_paths: Optional workspace file paths to inject server-side
+            (e.g. context/tree/signature reports). Each path resolves
+            under the workspace root with the read suffix allowlist;
+            per-file cap plus total budget apply, problems become explicit
+            unavailable labels. Default off. Small pulls stay inline.
 
     Returns:
         {"status": "XML_EXTRACTED"|"REPORT", "xml_blocks": [...],
@@ -1067,6 +1135,18 @@ def brain_turn(
                 effective_prompt = attach + "\n\n---\n\n" + effective_prompt
         except Exception as exc:  # never fail a turn on attach problems
             print(f"brain-bridge: task attach skipped ({exc})", file=sys.stderr)
+    if context_paths:
+        # File-path injection: the server reads big artifacts (context,
+        # tree, signature reports) from disk instead of the Hands pasting
+        # them. Counts toward the input budget below like any prompt text.
+        try:
+            paths_attach = build_paths_attach(context_paths)
+            if paths_attach:
+                effective_prompt = (
+                    effective_prompt + "\n\n---\n\n" + paths_attach)
+        except Exception as exc:  # never fail a turn on attach problems
+            print(f"brain-bridge: paths attach skipped ({exc})",
+                  file=sys.stderr)
     if include_bundle and include_diff and task_id:
         try:
             dattach = build_diff_attach(
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index 828d368..c4698a7 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -1194,3 +1194,67 @@ def test_fed_context_bad_id_raises(tmp_path, monkeypatch):
 def test_fed_context_load_bad_id_returns_empty(tmp_path, monkeypatch):
     monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path))
     assert bridge.load_fed_context("../evil") == ""
+
+
+def _ws(tmp_path, monkeypatch):
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    return tmp_path
+
+
+def test_paths_attach_off_by_default():
+    assert bridge.build_paths_attach(None) == ""
+    assert bridge.build_paths_attach([]) == ""
+    assert bridge.build_paths_attach("not-a-list") == ""
+
+
+def test_paths_attach_happy_path(tmp_path, monkeypatch):
+    _ws(tmp_path, monkeypatch)
+    (tmp_path / "ctx.md").write_text("# ctx\nbody\n", encoding="utf-8")
+    out = bridge.build_paths_attach(["ctx.md"])
+    assert "[path-injected: ctx.md]" in out
+    assert "body" in out
+
+
+def test_paths_attach_traversal_labelled(tmp_path, monkeypatch):
+    _ws(tmp_path, monkeypatch)
+    out = bridge.build_paths_attach(["../evil.md"])
+    assert "outside workspace" in out
+
+
+def test_paths_attach_bad_suffix_labelled(tmp_path, monkeypatch):
+    _ws(tmp_path, monkeypatch)
+    (tmp_path / "run.py").write_text("x = 1\n", encoding="utf-8")
+    out = bridge.build_paths_attach(["run.py"])
+    assert "unsupported extension" in out
+
+
+def test_paths_attach_missing_labelled(tmp_path, monkeypatch):
+    _ws(tmp_path, monkeypatch)
+    out = bridge.build_paths_attach(["gone.md"])
+    assert "unreadable" in out
+
+
+def test_paths_attach_empty_labelled(tmp_path, monkeypatch):
+    _ws(tmp_path, monkeypatch)
+    (tmp_path / "empty.md").write_text("   \n", encoding="utf-8")
+    out = bridge.build_paths_attach(["empty.md"])
+    assert "empty file" in out
+
+
+def test_paths_attach_per_file_cap(tmp_path, monkeypatch):
+    _ws(tmp_path, monkeypatch)
+    (tmp_path / "big.md").write_text(
+        "y" * (bridge._CTX_PATHS_PER_FILE + 10), encoding="utf-8")
+    out = bridge.build_paths_attach(["big.md"])
+    assert "truncated" in out
+
+
+def test_paths_attach_total_budget(tmp_path, monkeypatch):
+    _ws(tmp_path, monkeypatch)
+    chunk = "z" * bridge._CTX_PATHS_TOTAL
+    (tmp_path / "a.md").write_text(chunk, encoding="utf-8")
+    (tmp_path / "b.md").write_text(chunk, encoding="utf-8")
+    (tmp_path / "c.md").write_text("tiny\n", encoding="utf-8")
+    out = bridge.build_paths_attach(["a.md", "b.md", "c.md"])
+    assert "total budget" in out
+    assert "tiny" in out  # skip does not abort later files
```
<!-- END_GIT_DIFF -->
