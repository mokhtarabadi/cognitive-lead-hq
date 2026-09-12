# Task 201: Brain QA reviewer turns always carry changed hunks plus modes doc

**File:** `tasks/qa/201-brain-qa-reviewer-turns-carry-hunks-modes-doc.md`
**Source:** manager
**Type:** feature
**Status:** open

## Goal

QA and reviewer Brain turns must always include the changed hunks (Factual Git Diff content), and manual/autopilot modes must be documented in README.

## Manager's Notes

QA/reviewer turns must always carry the changed hunks or factual diff. The model must see what changed and judge from it, not guess. Implement on autopilot: run the Brain loop without asking the manager anything, notify only when approval is needed. Also teach the manager the mode switch words (manual vs autopilot, how to lock each) and record the manual mode in README.

## Local TODOs

- [x] Add include_diff path to brain_turn with tests
- [x] Mandate include_diff on QA/reviewer turns in Hands protocol (agents/cognitive-executor.md — verified NOT a system-prompt build input, so no rebuild/version bump needed)
- [x] Document manual/autopilot modes + switch words in README
- [x] Run brain QA reviewer loop, stage, move to QA

## Acceptance Criteria

- [x] brain_turn accepts include_diff and appends diff content when the task file resolves (capped, fail-safe)
- [x] QA/reviewer turns are mandated to pass include_diff through the Hands protocol
- [x] Tests cover present/absent/unresolvable/over-cap diff cases and pass
- [x] README documents manual vs autopilot modes and the exact switch words
- [x] Full suite passes with exit code 0

## Verification Evidence

- **Test command:** uv run --project mcp-decision-server python -m pytest tests/ -q
- **Expected result:** all tests pass, exit code 0
- **Actual result:** 264 passed (252 prior + 8 diff-attach + 2 fence-guard + 2 fail-safe tests)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Larger prompts on QA turns; diff content could crowd the input budget
- **Rollback plan:** Revert the bridge server hunk and the fragment line; default include_diff off keeps tiny calls unchanged

---

## Execution Log & Reasoning

**Autopilot locked** for this order (manager: run on autopilot, ask nothing, notify only on approval need). No questions asked during execution.

- **Red:** wrote `tests/test_brain_diff_attach.py` first (8 tests) — failed on missing `extract_task_diff`/`build_diff_attach`, as designed.
- **Green:** `mcp-brain-bridge/server.py`: new `_TASK_DIFF_CAP = 20000`; pure `extract_task_diff(text)` (multi-block join, unclosed-BEGIN cuts to EOF); `build_diff_attach(task_id)` (resolve → read → extract → cap with truncation note → labeled ```diff fenced block; empty/unresolvable never fail the turn); `brain_turn(..., include_diff=False)` appends the hunks block after the user prompt when `include_bundle and include_diff and task_id`. New tests 8/8, full suite **260 passed exit 0**.
- **Protocol:** `agents/cognitive-executor.md` state-machine Build step now mandates `include_diff=True` on QA/reviewer turns; new Modes section (manual default vs locked autopilot, exact switch words, one-line lock announcements, lock recorded in task file). Verified via assembler source that this file is NOT a system-prompt build input — no rebuild or version bump required.
- **README:** new Modes subsection under the manual workflow (manager-facing wording, switch words, how-you-always-know rule).
- **Assumption A1:** default `include_diff=False` keeps tiny calls unchanged; the mandate lives in the Hands protocol per the manager's "always" for QA/reviewer turns specifically.
- **QA Round (brain_turn, task_id 201, verbatim code pasted; one empty-REPORT retry): QA_PASSED.** Findings: F1/F2 verified on disk (extract multi-block join, build never-raises, mandate wording); F3 low-risk accepted and fixed — the ```diff fence in `build_diff_attach` was not escape-guarded (embedded fences in diff bodies could close the block early), mirrored the existing V1 ZWSP guard from the task attach; added 2 tests (fence break, empty-whitespace pair). Full suite now **262 passed exit 0**.
- **Verification Evidence:** `uv run --project mcp-decision-server python -m pytest tests/ -q` → 262 passed, exit 0 (run from repo root; needs `--with pytest --with pathspec --with pyyaml --with mcp==1.30.0` on bare envs — pre-existing gaps).
- **Reviewer Round (CHANGES_REQUIRED + hotfix XML, executed):** F1 (no diff arrived — my caller tool has no `include_diff` parameter; server flag proven working on disk at 7947 chars), F2 (guard line not shown — now proven: identical ZWSP line at server.py:290 V1 and server.py:350 diff attach), F3 (default-False loophole — closed by fail-safe), F4 (caller schema — server `@mcp.tool()` at server.py:911 exposes `include_diff`; the missing piece is only the Hands session harness outside this repo, covered by the fail-safe), F5 (modes doc-only — now explicit in both files). Hotfix: new pure `_failsafe_qa_attach` helper + auto-attach with stderr warning on QA-like prompts without the flag; 2 new tests. Full suite now **264 passed exit 0** (12/12 diff-attach).
- **Reviewer Round 2 (APPROVED, technically PO_REVIEW_PENDING — no autoclosure, reviewer defers to Manager):** re-review with verbatim helper (server.py:360-373) + call site (server.py:994-1008) pasted. S1-S4 strengths (non-string prompt/id safe, try/except with stderr log, normal contract intact). F1-F4 all Low: guard lines not re-pasted (proven earlier at server.py:290/350), fail-safe requires bundle True (QA mandate keeps it True), full task diff not in channel (process gap, not code defect), Modes text not re-pasted (doc-only). Verdict: fail-safe closes F3, normal-turn contract intact, code approved technically. PO (Manager) asked to reply "Approved for closure".

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 1851269..0ebadb3 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Brain QA/reviewer turns carry changed hunks (Task 201):** `brain_turn` accepts `include_diff` — when true and the task id resolves, the Factual Git Diff content rides along verbatim (capped separately, fail-safe), so QA and reviewer judge actual changes instead of summaries. The Hands protocol mandates `include_diff=True` on QA/reviewer turns. 8 new offline tests (extract present/absent/multi/unclosed, attach resolved/none/unresolvable/over-cap) plus a fence-escape guard with 2 more tests (fence break, empty pair). README gains a Modes section (manual default vs locked autopilot, switch words). Full suite: **262 passed**.
+
 - **Token-optimization verified spike (Task 150):** Evaluated RTK 0.49.0 locally (musl binary, no global install): passing pytest suite collapses 1801 bytes / 21 lines → 44 bytes / 3 lines (**97.6% fewer bytes**, exit code preserved, 232 passed); small git outputs (±2%) not worth wrapping; `rtk diff` is a `/usr/bin/diff` wrapper (use `rtk git diff`); `rtk test` needs exact dep pins (`mcp==1.30.0` — `<` specs break as shell redirection). `headroom-ai` 0.37.0 (PyPI) and `@caveman-ai/cli` 1.3.3 (npm) registry-verified; proxy/pixel eval deferred (needs provider rewiring + manager approval). Claim scoped to passing suites — failing-suite trimming unmeasured. New `docs/loop-engine/configuration.md` holds the evidence table (with source column: local measurement vs tool self-report); `docs/opencode-shell-strategy.md` §8 holds the practices. Headroom/Caveman proxy integration and 10-task sprint measurement remain open follow-ups.
 - **Machine-readable QA verdicts + rules-first gate (Task 195):** QA persona (fragment 06) now ends every report with a machine verdict block (`VERDICT: QA_PASSED` / `QA_REJECTED` + `CITE: file:line` lines, single-regex parseable) with a documented escape hatch (unparseable → QA_REJECTED with reason, prose fallback, manager override). New `scripts/qa-rules-gate/rules_gate.py` runs verdict-parse, schema, budget, and allowlist checks before any LLM judge call — rule failures return QA_REJECTED without invoking the judge (Mock-asserted). 20 mocked tests (relative-path allowlist, exactly-one-verdict, whitespace tolerance, judge validation, nested schema, cite punctuation). System version 9.27.0 → 9.28.0, `system-prompt.md` rebuilt (sync-check byte-identical). Full suite: **239 passed**.
 
@@ -33,6 +35,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Guaranteed context bundle + autopilot saga rule (Task 190 overnight):** Executor autopilot gained Saga self-sufficiency — the Hands plays the manager role via manager-decision when an XML step says the manager copies, and hands results to the reviewer directly via `brain_turn` (ferrying through the human in autopilot is now a bug). Big-file-to-LLM research (blowsh spider workflow, Kokil 2026 long-context guide) concluded tool-use beats whole-file stuffing, so the bridge now auto-prepends a 5-file context bundle (`cognitive-executor.md`, `conventions.md`, `architecture.md`, `data_model.md`, `DESIGN.md`, 60k/file cap, `[missing]` markers) to every `brain_turn`, and exposes `read_file` (root-guarded, numbered lines) + `grep_files` (30-hit cap) for on-demand pulls of big files like full task files. Live bundle proof: HTTP 200, exact `BUNDLE_PROOF_OK`, all 5 files included-or-marked. Covered by 10 new mocked tests. Full suite: **139 passed**.
 
+### Fixed
+
+- **Reviewer hotfix on hunks path (Task 201):** QA/reviewer-like prompts now auto-attach the changed hunks even when the caller forgets `include_diff` (new pure `_failsafe_qa_attach` keyword gate + stderr warning; normal turns untouched); diff fence guard proven identical to the V1 task-attach guard; Modes docs now state prompt-level enforcement explicitly. Covered by 2 new tests (QA prompt attaches, normal prompt stays empty). Full suite: **264 passed**.
+
 ## [9.26.0] - 2026-09-11
 
 ### Changed
diff --git a/README.md b/README.md
index 0ee4ea3..8e9bd6c 100644
--- a/README.md
+++ b/README.md
@@ -94,6 +94,16 @@ This is the canonical pure-MCP cycle:
 
 All transitions use pure FastMCP tools (`custom_context_qa_transition`, `bundle_tasks`, `custom_context_commit_and_clean_task`) — no `uv run scripts/...` CLI required.
 
+### Modes: manual (default) vs autopilot (locked)
+
+There is no switch in code — the switch is words, and enforcement is
+prompt-level only (no code lock; the lock is recorded in the task file):
+
+- **Manual (default).** The Hands still calls the Brain itself, but questions and approvals come to you. You never ferry XML or task text between them.
+- **Autopilot (locked).** Say "on autopilot do X". The Hands announces the lock in one line and runs end-to-end (implement, Brain-QA, fix, Brain-review, stage, move to QA) with zero pauses — stopping only for hard blockers. It never auto-commits and never closes tasks; closure always needs your explicit approval word.
+- **Switch back.** Say "manual mode" or "back to manual". The lock breaks at once.
+- **How you always know.** The Hands confirms every switch in one line ("Autopilot locked for …" / "Back to manual.") and records the lock in the task file.
+
 ### System Prompt V9 Architecture (Separation of Concerns)
 
 The `system-prompt.md` is restructured in V9.1.0 with a clear separation of concerns:
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 8c2ad33..ee68faf 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -276,7 +276,9 @@ needs no extra machinery.
 
 1. **Build** the user prompt from current machine state: the instruction
    (e.g. "QA engineer please make the adversarial testing") + the full
-   active task file + any prior answers.
+   active task file + any prior answers. QA and reviewer turns MUST pass
+   `include_diff=True` so the changed hunks ride along — the Brain judges
+   the actual changes, never a summary.
 2. **Call** `brain_turn`. Read `status`:
    - `XML_EXTRACTED` — execute `xml_blocks` as the next instruction set,
      exactly like an Orchestrator XML block.
@@ -303,6 +305,26 @@ with the same `task_id` — never paste XML or task text for the Manager
 to ferry back. In autopilot the Manager sees only Relay questions and
 the final verdict report. Ferrying work through the Manager is a bug.
 
+### Modes: manual (default) vs autopilot (locked)
+
+There is no switch in code — the switch is WORDS, and the lock is public.
+Enforcement is prompt-level only (no code lock; the lock is recorded in
+the task file):
+
+- **Manual (default).** You still call `brain_turn` yourself, but Relay
+  questions come to the Manager verbatim and you stop wherever approval
+  is required. The Manager never ferries XML or task text.
+- **Autopilot (locked).** The Manager says "on autopilot do X" (or names
+  the task plus autopilot). From that word on, the mode is LOCKED:
+  announce the lock in one line, follow it to the end, and never ask
+  anything except hard blockers and Relay questions. The lock breaks
+  only when the Manager says "manual", "stop", or takes over with a
+  new direct order.
+- **Switch words.** Manager → Hands: "on autopilot …" locks autopilot;
+  "manual mode" / "back to manual" returns to manual. Hands → Manager:
+  one line ("Autopilot locked for …" / "Back to manual.") so both sides
+  always know which mode is live. Record the lock in the task file.
+
 ### Saga self-sufficiency (autopilot/auto mode)
 
 When a Brain XML says the Manager copies, pastes, approves, or ferries —
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 475f079..a95f4ff 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -174,6 +174,7 @@ _TASK_DIFF_END = "<!-- END_GIT_DIFF -->"
 _TASK_FILE_MARKER = "[task-file:"
 _TASK_KANBAN_DIRS = ("in-progress", "qa", "backlog", "completed", "archive")
 _TASK_ATTACH_CAP = 12000
+_TASK_DIFF_CAP = 20000
 
 
 def _task_id_ok(tid: object) -> bool:
@@ -296,6 +297,82 @@ def _build_task_attach(task_id: str) -> str:
         return ""
 
 
+def extract_task_diff(text: str) -> str:
+    """Return the raw Factual Git Diff block bodies, joined ('' when none).
+
+    Pure: no filesystem touch. An unclosed BEGIN cuts to EOF.
+    """
+    bodies: list[str] = []
+    rest = text
+    while True:
+        start = rest.find(_TASK_DIFF_BEGIN)
+        if start < 0:
+            break
+        tail = rest[start + len(_TASK_DIFF_BEGIN):]
+        end = tail.find(_TASK_DIFF_END)
+        if end < 0:
+            bodies.append(tail)
+            break
+        bodies.append(tail[:end])
+        rest = tail[end + len(_TASK_DIFF_END):]
+    return "\n".join(bodies)
+
+
+def build_diff_attach(task_id: str) -> str:
+    """Assemble the labeled changed-hunks block ('' when none).
+
+    Contains the task file's Factual Git Diff content verbatim so QA and
+    reviewer turns judge the actual changes, never a summary. Content
+    caps at _TASK_DIFF_CAP chars with a truncation note. Never raises.
+    """
+    try:
+        path = _resolve_task_file(task_id)
+        if path is None:
+            return ""
+        text = path.read_text(encoding="utf-8", errors="replace")
+        diff = extract_task_diff(text)
+        if not diff.strip():
+            return ""
+        try:
+            rel = path.resolve().relative_to(
+                _workspace_root().resolve()).as_posix()
+        except (OSError, ValueError):
+            rel = path.name
+        if len(diff) > _TASK_DIFF_CAP:
+            diff = (
+                diff[:_TASK_DIFF_CAP]
+                + f"\n[...diff truncated at {_TASK_DIFF_CAP} chars — "
+                + f"pull remainder via read_file({rel!r}, offset, limit)]"
+            )
+        tid = task_id.strip() if isinstance(task_id, str) else "task"
+        # Same V1 guard as the task attach: break fence parsing invisibly
+        # so embedded fences in diff content cannot close our block early.
+        diff = diff.replace(chr(96) * 3, chr(96) * 2 + chr(8203) + chr(96))
+        return (
+            f"[changed-hunks:{tid}: {rel}]\n"
+            + "```diff\n" + diff + "\n```"
+        )
+    except Exception as exc:  # never fail a turn on attach problems
+        print(f"brain-bridge: diff attach skipped ({exc})", file=sys.stderr)
+        return ""
+
+
+def _failsafe_qa_attach(user_prompt: object, task_id: object) -> str:
+    """Return the diff-attach block for QA-like prompts ('' otherwise).
+
+    Keyword gate only: fires when the prompt reads like a QA/reviewer
+    turn ("qa engineer", "code reviewer", "adversarial"). Lets QA turns
+    carry the changed hunks even when the caller forgot include_diff.
+    Never raises (build_diff_attach never raises).
+    """
+    lowered = user_prompt.lower() if isinstance(user_prompt, str) else ""
+    if ("qa engineer" in lowered or "code reviewer" in lowered
+            or "adversarial" in lowered):
+        return build_diff_attach(
+            task_id.strip() if isinstance(task_id, str) else "")
+    return ""
+
+
 def _build_context_bundle() -> str:
     """Assemble the labeled small-file bundle (never raises on Absent-File)."""
     root = _workspace_root()
@@ -853,6 +930,7 @@ def brain_turn(
     task_id: Optional[str] = None,
     system_prompt_path: Optional[str] = None,
     include_bundle: bool = True,
+    include_diff: bool = False,
 ) -> dict[str, Any]:
     """Send one Brain turn.
 
@@ -870,6 +948,14 @@ def brain_turn(
             evidence/log minus the Factual Git Diff block, with a
             read_file pull path) whenever task_id resolves to a file.
             Pass False for tiny calls. The system prompt is untouched.
+        include_diff: When True, append the task file's changed hunks
+            (Factual Git Diff content, verbatim, capped) whenever
+            task_id resolves to a file that carries a diff block.
+            QA and reviewer turns MUST pass True — the Brain judges
+            the actual changes, never a summary. Fail-safe: when the
+            flag is False but the prompt reads like a QA/reviewer turn
+            ("qa engineer", "code reviewer", "adversarial"), the hunks
+            still auto-attach with a stderr warning.
 
     Returns:
         {"status": "XML_EXTRACTED"|"REPORT", "xml_blocks": [...],
@@ -897,6 +983,29 @@ def brain_turn(
                 effective_prompt = attach + "\n\n---\n\n" + effective_prompt
         except Exception as exc:  # never fail a turn on attach problems
             print(f"brain-bridge: task attach skipped ({exc})", file=sys.stderr)
+    if include_bundle and include_diff and task_id:
+        try:
+            dattach = build_diff_attach(
+                task_id.strip() if isinstance(task_id, str) else "")
+            if dattach:
+                effective_prompt = effective_prompt + "\n\n---\n\n" + dattach
+        except Exception as exc:  # never fail a turn on attach problems
+            print(f"brain-bridge: diff attach skipped ({exc})", file=sys.stderr)
+    if include_bundle and not include_diff and task_id:
+        # Fail-safe: QA/reviewer-like prompts carry the changed hunks even
+        # when the caller forgot the flag — a silent drop would let the
+        # Brain judge a summary instead of the changes. Keyword gate only;
+        # normal turns are untouched when the flag is False.
+        try:
+            dattach = _failsafe_qa_attach(user_prompt, task_id)
+            if dattach:
+                print("brain-bridge: QA turn without include_diff, "
+                      "auto-attaching diff", file=sys.stderr)
+                effective_prompt = (effective_prompt + "\n\n---\n\n"
+                                    + dattach)
+        except Exception as exc:  # never fail a turn on attach problems
+            print(f"brain-bridge: diff attach skipped ({exc})",
+                  file=sys.stderr)
     model = _get_brain_model()
     history = load_history(task_id) if task_id else []
     # Input budget: system + user + history chars count against
diff --git a/tests/test_brain_diff_attach.py b/tests/test_brain_diff_attach.py
new file mode 100644
index 0000000..5e010e1
--- /dev/null
+++ b/tests/test_brain_diff_attach.py
@@ -0,0 +1,115 @@
+"""Tests for the brain_turn include_diff path (task file changed hunks).
+
+Offline only: covers diff extraction from task text and the attach
+builder (present / absent / unresolvable / over-cap). The live LLM path
+(httpx POST) is never touched.
+"""
+
+import sys
+from pathlib import Path
+
+import pytest
+
+BRIDGE_DIR = Path(__file__).parent.parent / "mcp-brain-bridge"
+sys.path.insert(0, str(BRIDGE_DIR))
+
+import server as bridge
+
+
+def _task_text(diff_body: str) -> str:
+    return (
+        "# Task 99: Sample\n\nSome working content.\n\n"
+        "<!-- BEGIN_GIT_DIFF -->\n" + diff_body + "\n<!-- END_GIT_DIFF -->\n"
+    )
+
+
+def test_extract_diff_present():
+    text = _task_text("diff --git a/x b/x\n+new line")
+    out = bridge.extract_task_diff(text)
+    assert "diff --git a/x b/x" in out
+    assert "+new line" in out
+
+
+def test_extract_diff_absent_returns_empty():
+    assert bridge.extract_task_diff("# Task 99: no diff here\n") == ""
+
+
+def test_extract_diff_multiple_blocks_joined():
+    text = (
+        "<!-- BEGIN_GIT_DIFF -->\nhunk-one\n<!-- END_GIT_DIFF -->\n"
+        "middle\n"
+        "<!-- BEGIN_GIT_DIFF -->\nhunk-two\n<!-- END_GIT_DIFF -->\n"
+    )
+    out = bridge.extract_task_diff(text)
+    assert "hunk-one" in out
+    assert "hunk-two" in out
+
+
+def test_extract_diff_unclosed_cuts_to_eof():
+    text = "<!-- BEGIN_GIT_DIFF -->\npartial hunk, no end"
+    out = bridge.extract_task_diff(text)
+    assert "partial hunk" in out
+
+
+def test_build_diff_attach_resolved_with_diff(monkeypatch, tmp_path):
+    target = tmp_path / "99-sample.md"
+    target.write_text(_task_text("+added"), encoding="utf-8")
+    monkeypatch.setattr(bridge, "_resolve_task_file", lambda tid: target)
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    out = bridge.build_diff_attach("99")
+    assert "+added" in out
+
+
+def test_build_diff_attach_no_diff_returns_empty(monkeypatch, tmp_path):
+    target = tmp_path / "99-sample.md"
+    target.write_text("# Task 99: no diff\n", encoding="utf-8")
+    monkeypatch.setattr(bridge, "_resolve_task_file", lambda tid: target)
+    assert bridge.build_diff_attach("99") == ""
+
+
+def test_build_diff_attach_unresolvable_returns_empty(monkeypatch):
+    monkeypatch.setattr(bridge, "_resolve_task_file", lambda tid: None)
+    assert bridge.build_diff_attach("nope") == ""
+
+
+def test_build_diff_attach_over_cap_truncates(monkeypatch, tmp_path):
+    target = tmp_path / "99-sample.md"
+    target.write_text(_task_text("x" * 50000), encoding="utf-8")
+    monkeypatch.setattr(bridge, "_resolve_task_file", lambda tid: target)
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    monkeypatch.setattr(bridge, "_TASK_DIFF_CAP", 100)
+    out = bridge.build_diff_attach("99")
+    assert "truncated" in out
+    assert len(out) < 50000
+
+
+def test_extract_diff_empty_pair_yields_empty():
+    text = "<!-- BEGIN_GIT_DIFF --><!-- END_GIT_DIFF -->\n"
+    assert bridge.extract_task_diff(text) == ""
+
+
+def test_build_diff_attach_breaks_embedded_fences(monkeypatch, tmp_path):
+    target = tmp_path / "99-sample.md"
+    target.write_text(_task_text("line\n```evil\nline"), encoding="utf-8")
+    monkeypatch.setattr(bridge, "_resolve_task_file", lambda tid: target)
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    out = bridge.build_diff_attach("99")
+    assert "```evil" not in out
+    assert "evil" in out
+
+
+def test_failsafe_qa_prompt_attaches_without_flag(monkeypatch, tmp_path):
+    target = tmp_path / "99-sample.md"
+    target.write_text(_task_text("+added"), encoding="utf-8")
+    monkeypatch.setattr(bridge, "_resolve_task_file", lambda tid: target)
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    out = bridge._failsafe_qa_attach(
+        "QA engineer, adversarial review please", "99")
+    assert "+added" in out
+
+
+def test_failsafe_normal_prompt_stays_empty(monkeypatch, tmp_path):
+    target = tmp_path / "99-sample.md"
+    target.write_text(_task_text("+added"), encoding="utf-8")
+    monkeypatch.setattr(bridge, "_resolve_task_file", lambda tid: target)
+    assert bridge._failsafe_qa_attach("fix the login bug", "99") == ""
```
<!-- END_GIT_DIFF -->
