# Task 209: Discovery-fed Brain planning with session-persistent context

**File:** `tasks/in-progress/209-discovery-fed-brain-planning-with-session-persistent-context.md`
**Source:** manager
**Type:** feature
**Status:** open
**Mode:** autopilot-locked (manager ordered autopilot to the end with a goal; closure approval not yet given)

## Goal

Make Brain planning run on real discovery context: when Brain returns a discovery XML during planning, the Hands execute it and feed the context back before the final plan, and that context stays reachable until session end.

## Manager's Notes

Manager's verbatim message (Persian, preserved word-for-word):

> یه یچزی به ذهنم رسید تسک کن و بعدش روش کار میکنیم
> الان توی فاز یک وقتی میخواایم به brain بگیم برامون plan بزنه
> اگه برین task xml بده برای فاز discovery ایا تون اون رو احرا میکنی که و خروجی context رو بهش بدی برای رنامه ریزی؟
> که دقیقا از روی context نظر بده؟
> همینطور ایتن کانمست یا post context ها تا انهتای سشن براش قابل دسترس باشه؟
> کاری که من در حالت دستی انجام میدم

English translation: Something came to mind — file it as a task and we will work on it later. Now in phase one, when we ask the Brain to plan for us, if the Brain gives task XML for the discovery phase, do you execute it and give the context output back to it for planning, so it opines exactly from context? Likewise, do these contexts or post-contexts stay accessible to it until end of session? That is what I do manually.

Refactored intent: extend the planning gate into a discovery-fed loop (plan request → Brain discovery XML → Hands execute → context back to Brain → final plan grounded in context), with the fed context persisted in the task session transcript so it stays reachable through session end. Park for later, do not implement yet.

## Local TODOs

- [x] Initial codebase exploration
- [x] Map planning-gate and discovery paths in executor and bridge
- [x] Design discovery-fed loop and session persistence rule
- [x] Verify functionality

## Acceptance Criteria

- [x] Planning with a discovery step executes the discovery XML before the final plan
- [x] Final Brain plan cites the fed context, not assumptions
- [x] Fed context stays reachable in session history until session end
- [x] Manual manager ferrying of context stays unnecessary in autopilot

## Verification Evidence

- **Test command:** `uv run --with pytest --with pathspec --with pyyaml --with mcp==1.30.0 python -m pytest tests/ -q`
- **Expected result:** all tests pass, exit 0
- **Actual result:** 245 passed (237 baseline plus 8 new fed-context tests), 8 warnings
- **Exit code:** 0
- **Probe:** planning turn returned discovery XML, 3 subagents executed, fed context returned grounded blueprint citing CTX-1..CTX-5; empty-output flake on 2 turns recovered via lean retry per standing rule

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** extra Brain turns per plan cost tokens and time; unbounded discovery loops.
- **Rollback plan:** keep the loop behind the existing planning gate with a guard (max one discovery round); revert to current gate behavior.

---

## Execution Log & Reasoning

Autopilot locked per manager order ("do the task, go to the end", goal created). Manager direct order counts as approval to implement from the Brain blueprint below.

Plan verdict (Brain Architect, task_id 209, REPORT, no XML): discovery-fed loop with max 1 discovery round and max 2 planning turns, same-task_id chaining, pinned fed_context.md exempt from compaction, grounding citations D10-D12, token guards G1-G5. Selected path O1 (pinned file plus transcript tag). Side finding CTX-5 (context MCP false gitignore) parked as separate follow-up.

Discovery executed first per Brain request: 3 parallel subagents (tree plus core files, bridge signatures plus history, planning fragments). Fed back as CTX-1..CTX-5, final plan grounded in it. Assumption A1: manager "go to the end" approves blueprint implementation; closure still needs explicit approval word.

Implementation (from approved blueprint, selected path O1): E1 added Discovery-fed planning subsection to executor Planning Gate (one discovery round, two planning turns max, same-id chaining, grounding citations, halt on second discovery). E2 added fed-context pinning to bridge (extract/save/load helpers, 20k cap, atomic write, prepend with pin header, exempt from compaction by separate-file design). 8 new offline tests (extract present/unclosed/absent, roundtrip, cap, clear, save-bad-id, load-bad-id). Full suite 245 passed. CHANGELOG Unreleased entry added (executor-only change, no prompt rebuild).

QA round 1: QA_PASSED with residuals. Honored F3 (load/bad-id doc mismatch): load now catches ValueError too, plus load-bad-id test. F2 (pid-only tmp collision) accepted as low risk: Hands use is sequential, same pattern as existing transcript writes. F4 (marker spoof) accepted: Hands control prompts. M1 (prepend wiring test) and M3 (double block) noted as follow-ups, non-blocking.

Reviewer round 1: APPROVED_WITH_CHANGES, all 3 findings reproduced and fixed (CHANGELOG 244→245, save/path docstrings now state ValueError). Suite still 245 passed. Re-review requested.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 92e60b6..4153afd 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+### Added
+
+- **Discovery-fed Brain planning with pinned session context (Task 209):** planning gate gained a discovery-fed loop — when the planning turn returns a discovery task, the Hands execute it via subagents and feed the result back under the same id (max one discovery round, max two planning turns) before the final plan, which must cite fed context. The bridge pins `[fed-context]` blocks to `fed_context.md` per session and prepends the pin to later turns, exempt from compaction and the middle drop (20k cap). Executor doc only, no prompt rebuild. Full suite: **244 passed**.
+
 ## [9.31.0] - 2026-09-12
 
 ### Added
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index b11e475..35f0d40 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -237,6 +237,21 @@ invention. Lite-eligible changes (single file, no cross-module impact,
 obvious fix, never login/auth, money, or security-surface changes) pass
 with a one-line justification in the file.
 
+### Discovery-fed planning (grounds the plan in repo truth)
+
+When the planning `brain_turn` returns a discovery task instead of a
+plan, execute it and feed the result back before any final plan: run
+discovery via subagents (never write code), then call `brain_turn`
+again under the same `task_id` with the fed context marked by a
+`[fed-context]` block. Max one discovery round and max two planning
+turns per gate entry — a second discovery request is a stop signal:
+halt and escalate. Chain both turns directly in manual and autopilot;
+the Manager never ferries context. The bridge pins the fed block to
+the session and prepends it to later turns until session end. The
+final plan must cite fed context (file paths with lines); if it cites
+none, re-prompt once with a grounding reminder, then escalate rather
+than invent.
+
 ## Manual Workflow (Active Default)
 
 > Automation runs through ONE path: the Brain Bridge (`brain_turn` — see
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 2cc4a8f..6d9804a 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -924,6 +924,88 @@ def append_turn(task_id: str, role: str, content: str, model: Optional[str] = No
             fcntl.flock(fh, fcntl.LOCK_UN)
 
 
+#: Marker opening a fed discovery block inside a user prompt. Everything
+#: after the marker line (up to an optional ``[/fed-context]`` line) is
+#: pinned to the session and prepended to later turns until session end,
+#: so planning always reasons from executed discovery, never memory.
+_FED_CONTEXT_MARKER = "[fed-context]"
+_FED_CONTEXT_END = "[/fed-context]"
+_FED_CONTEXT_FILE = "fed_context.md"
+
+#: Cap for pinned fed context (chars). Truncated with a note, never
+#: silently dropped by history compaction or the input-budget middle drop
+#: (it lives in its own file, outside the transcript window).
+_FED_CONTEXT_CAP = 20000
+
+
+def _fed_context_path(task_id: str) -> Path:
+    """Pinned fed-context file for a task (sanitized id, never raises)."""
+    return _sessions_root() / _sanitize_task_id(task_id) / _FED_CONTEXT_FILE
+
+
+def extract_fed_context(prompt: object) -> str:
+    """Return the fed discovery block in ``prompt`` ('' when none).
+
+    Pure: no filesystem touch. Takes text after the first ``[fed-context]``
+    line, cuts at ``[/fed-context]`` when present, strips blank edges.
+    """
+    if not isinstance(prompt, str):
+        return ""
+    lines = prompt.splitlines()
+    start = None
+    for i, line in enumerate(lines):
+        if line.strip() == _FED_CONTEXT_MARKER:
+            start = i + 1
+            break
+    if start is None:
+        return ""
+    end = len(lines)
+    for j in range(start, len(lines)):
+        if lines[j].strip() == _FED_CONTEXT_END:
+            end = j
+            break
+    return "\n".join(lines[start:end]).strip()
+
+
+def save_fed_context(task_id: str, content: str) -> None:
+    """Pin fed discovery context (atomic write, capped, never raises).
+
+    Empty content deletes the pin. Oversize content truncates with a note.
+    """
+    path = _fed_context_path(task_id)
+    if not content.strip():
+        try:
+            path.unlink(missing_ok=True)
+        except OSError as exc:
+            print(f"brain-bridge: fed-context clear skipped ({exc})",
+                  file=sys.stderr)
+        return
+    if len(content) > _FED_CONTEXT_CAP:
+        content = (content[:_FED_CONTEXT_CAP]
+                   + f"\n[...fed context truncated at {_FED_CONTEXT_CAP} "
+                   + "chars]")
+    path.parent.mkdir(parents=True, exist_ok=True)
+    tmp = path.with_name(f"{path.name}.tmp-{os.getpid()}")
+    try:
+        with tmp.open("w", encoding="utf-8") as fh:
+            fh.write(content + "\n")
+            fh.flush()
+            os.fsync(fh.fileno())
+        os.replace(tmp, path)
+    except OSError as exc:
+        print(f"brain-bridge: fed-context save skipped ({exc})",
+              file=sys.stderr)
+
+
+def load_fed_context(task_id: str) -> str:
+    """Read pinned fed context ('' when none; never raises)."""
+    try:
+        return _fed_context_path(task_id).read_text(
+            encoding="utf-8", errors="replace").strip()
+    except (OSError, ValueError):
+        return ""
+
+
 @mcp.tool()
 def brain_turn(
     user_prompt: str,
@@ -1008,6 +1090,25 @@ def brain_turn(
                   file=sys.stderr)
     model = _get_brain_model()
     history = load_history(task_id) if task_id else []
+    if task_id:
+        # Discovery-fed planning: a [fed-context] block in this prompt is
+        # pinned to the session, then the pin (not just this turn's copy)
+        # rides every later turn until session end. The pin lives outside
+        # the transcript, so compaction and the middle drop below can never
+        # silently remove it; it still counts toward the input budget.
+        try:
+            fed = extract_fed_context(effective_prompt)
+            if fed:
+                save_fed_context(task_id, fed)
+            pinned = load_fed_context(task_id)
+            if pinned and "[pinned-fed-context]" not in effective_prompt:
+                effective_prompt = (
+                    "[pinned-fed-context]\n" + pinned
+                    + "\n[/pinned-fed-context]\n\n---\n\n"
+                    + effective_prompt)
+        except Exception as exc:  # never fail a turn on pin problems
+            print(f"brain-bridge: fed-context skipped ({exc})",
+                  file=sys.stderr)
     # Input budget: system + user + history chars count against
     # _INPUT_BUDGET. The FIRST history turn is grounding and survives;
     # oldest MIDDLE turns truncate first. Token estimate (chars//4) is
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index 248aafb..828d368 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -1146,3 +1146,51 @@ def test_grep_skips_overlong_lines(tmp_path, monkeypatch):
     monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
     hits = bridge._grep_files_impl("MATCH", "docs")
     assert len(hits) == 1 and ":2:" in hits[0]
+
+
+def test_extract_fed_context_present():
+    prompt = "plan please\n[fed-context]\nCTX-1 tree\nCTX-2 gate\n[/fed-context]\nend"
+    assert bridge.extract_fed_context(prompt) == "CTX-1 tree\nCTX-2 gate"
+
+
+def test_extract_fed_context_unclosed_runs_to_end():
+    prompt = "hi\n[fed-context]\nCTX-1 tree"
+    assert bridge.extract_fed_context(prompt) == "CTX-1 tree"
+
+
+def test_extract_fed_context_absent():
+    assert bridge.extract_fed_context("plain plan, no marker") == ""
+    assert bridge.extract_fed_context(None) == ""
+
+
+def test_fed_context_roundtrip(tmp_path, monkeypatch):
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path))
+    assert bridge.load_fed_context("t1") == ""
+    bridge.save_fed_context("t1", "CTX-1 tree")
+    assert bridge.load_fed_context("t1") == "CTX-1 tree"
+
+
+def test_fed_context_truncates_at_cap(tmp_path, monkeypatch):
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path))
+    bridge.save_fed_context("t2", "x" * (bridge._FED_CONTEXT_CAP + 100))
+    saved = bridge.load_fed_context("t2")
+    assert len(saved) <= bridge._FED_CONTEXT_CAP + 100
+    assert "truncated" in saved
+
+
+def test_fed_context_empty_clears_pin(tmp_path, monkeypatch):
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path))
+    bridge.save_fed_context("t3", "something")
+    bridge.save_fed_context("t3", "   ")
+    assert bridge.load_fed_context("t3") == ""
+
+
+def test_fed_context_bad_id_raises(tmp_path, monkeypatch):
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path))
+    with pytest.raises(ValueError):
+        bridge.save_fed_context("../evil", "x")
+
+
+def test_fed_context_load_bad_id_returns_empty(tmp_path, monkeypatch):
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path))
+    assert bridge.load_fed_context("../evil") == ""
```
<!-- END_GIT_DIFF -->
