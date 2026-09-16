# Task 240: Bridge truncation note orders Brain to read_file it cannot call

**File:** `tasks/qa/240-bridge-truncation-note-unverifiable.md`
**Source:** manager
**Type:** bug
**Status:** open

## Goal

Fix the `[changed-hunks]` truncation note so a QA/reviewer Brain never rejects on unseen evidence.

## Manager's Notes

Manager order (exact): "fix; https://github.com/mokhtarabadi/cognitive-lead-hq/issues/14". Zero-guess evidence in the issue: the note orders the Brain to `pull remainder via read_file`, the Brain has zero tool calls in QA turns (its own admission), round-1 QA_REJECTED on unseen scope should have been UNVERIFIABLE. Minimal prompt-side fix: (1) reword note — mark unseen scope UNVERIFIABLE, never REJECTED past truncation; (2) drop the read_file instruction to the Brain, address pulls to the Hands (verdict quotes needed paths, Hands pulls via brain_read_file/grep before re-QA). No commit, no close without the exact approval word.

## Local TODOs

- [x] Reword truncation note in `_build_changed_hunks`
- [x] Update/extend tests for new wording
- [x] Full suite green + CHANGELOG entry
- [ ] Lint + stage + qa + Brain QA/review

## Acceptance Criteria

- [x] Note no longer instructs the Brain to call read_file
- [x] Note orders UNVERIFIABLE-not-REJECTED for unseen scope
- [x] Pull path addressed to the Hands (quote paths, Hands pulls)
- [ ] Tests cover new wording; suite green; Brain QA passes

## Verification Evidence

- **Test command:** `uv tool run --with mcp==1.4.1 --with pathspec --with pyyaml --with pytest pytest tests/ -q` (+ focused `-k "truncation or unclosed"`)
- **Expected result:** focused + full suites exit 0
- **Actual result:** focused 171 passed; full **381 passed**, zero failures; new test `test_build_diff_attach_truncation_note_is_unverifiable` asserts UNVERIFIABLE wording, no REJECTED order, no Brain read_file instruction, Hands pull path
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** prompt-wording change alters Brain verdict behavior beyond the truncation case
- **Rollback plan:** revert the note string; wording-only change, no logic touched

---

## Execution Log & Reasoning

Seat Check: Senior Programmer (bridge prompt wording + regression test; no UI/schema/sprint triggers — Designer/Architect/Planner/Strategist skipped with reason). Replayed from DEC-20260914-003 (standing autopilot) + DEC-20260915-001 (fix-all). Edit: `_build_changed_hunks` truncation note + docstring — wording only, no logic touched (`rel` still used in the return block). CITE: mcp-brain-bridge/server.py truncation note; tests/test_brain_diff_attach.py new test.
- Full-context QA turn flaked EMPTY (transport, not counted as rejection); lean retry: VERDICT QA_PASSED (F1-F4 wording/pull-path/test/suite, minor note: no negative check for old phrase — non-blocking).
- Reviewer: PO_REVIEW_PENDING (technical approval, no blocking issue; R1 low: clearer visible-scope phrase in a future edit). Closure needs exact words "Approved for closure" or "Close task". File stays in tasks/qa. No commit.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index d08357a..28ac25b 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -25,6 +25,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **QA hotfix on the fix loop (Task 238, VERDICT QA_REJECTED → repair):** `_extract_unclosed_tail` now cuts trailing prose at the first blank line followed by a non-XML line (prose after a broken block stays conversation, never becomes Hands-executed instructions) and lowercases the tag name before the close-tag check so case/attributes never affect the allowlist decision; pretty-printed XML (blank line followed by another `<` line) passes through. Repo-boundary sentinel accepts `.git` dir and `.git` file (submodule/worktree roots). Executor queue-cap sentence now states the cap counts tasks in review, not parallel discovery subagents. V4 dismissed with evidence: `record_attempt` takes a caller-supplied hash and hashes nothing itself, and the executor rule hashes the worktree `git diff`, which excludes untracked files by default — no churn, no code change. 4 new regression tests (M1-M4). Full suites: **226 passed**.
 - **Why-fix: Brain diff attach never failed (Task 238, Manager order):** `mcp-brain-bridge/server.py` diff attach was gated on `include_bundle and include_diff`, so every lean retry (`include_bundle=false` — the documented `EMPTY_OUTPUT_RETRY` shape) silently carried zero hunks; gates decoupled to `include_diff and task_id` (attach) vs `not include_diff and task_id` (state note), with loud stderr reasons when the task file cannot resolve or the diff block is empty plus a no-hunks warning. `_resolve_task_file` now honors an optional `project_root` (explicit root with `tasks/` first, then workspace root) threaded through all attach helpers and the empty-output hint — a server running from another install resolves the file instead of warning. 8 new tests (5 resolver/attach, 3 turn-level lean/failsafe/unresolvable). Targeted suites: **170 passed**. Full suite: **374 passed** + 4 `test_skill_registry` failures proven pre-existing on clean HEAD via stash check.
 - **Why-fix follow-up: silent-empty diff notes go inline (Task 238, re-QA rejection → repair):** the rejection proved a second defect — every `build_diff_attach` failure path returned an empty string to the model while the loud reasons went only to stderr (server logs the Brain never reads), so even live fixed code stays silent on unresolvable files; the live QA turn runs the global server copy (started before the repo fix; global sync is manager-triggered, repo stays source of truth). `build_diff_attach` now returns inline `UNAVAILABLE`/`EMPTY` notes with remedy (retry with `project_root` or paste hunks inline, never reject blind) instead of `""`. 5 tests updated/rewritten to assert the inline notes reach the sent prompt. Targeted suites: **170 passed**.
+- **Truncation note orders Brain to pull without tools (Task 240, syncs GitHub issue 14):** the capped-hunks note told the Brain to pull the rest via `read_file`, but the Brain has zero tool calls — unseen evidence caused a wrongful `QA_REJECTED`. The note now says hunks past the cut were NOT sent, judge visible hunks only, mark unseen scope `UNVERIFIABLE` (never `REJECTED`) past a truncation, do not pull (no file tools exist), and quote needed paths in the verdict so the Hands pulls via `read_file` and re-runs QA. 1 new wording-lock test. Full suite: **381 passed**, zero failures.
 
 ## [9.35.0] - 2026-09-14
 
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index be0d73b..b02f550 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -423,7 +423,9 @@ def build_diff_attach(
 
     Contains the task file's Factual Git Diff content verbatim so QA and
     reviewer turns judge the actual changes, never a summary. Content
-    caps at _TASK_DIFF_CAP chars with a truncation note. When the hunks
+    caps at _TASK_DIFF_CAP chars with a truncation note that orders
+    UNVERIFIABLE-not-REJECTED for unseen scope (the Brain has no file
+    tools, so the note addresses pulls to the Hands, never to the Brain). When the hunks
     cannot attach, an inline UNAVAILABLE/EMPTY note is returned INSTEAD
     of "" — stderr is invisible to the model, so a silent "" made the
     Brain reject blind ("no diff present, cannot judge"); the inline
@@ -466,7 +468,14 @@ def build_diff_attach(
             diff = (
                 diff[:_TASK_DIFF_CAP]
                 + f"\n[...diff truncated at {_TASK_DIFF_CAP} chars — "
-                + f"pull remainder via read_file({rel!r}, offset, limit)]"
+                + "hunks past this point were NOT sent. Judge only what "
+                + "is visible above: pass visible scope, mark the unseen "
+                + "remainder UNVERIFIABLE, and NEVER emit REJECTED on "
+                + "evidence past the truncation point. You have no file "
+                + "tools in this turn, so do NOT attempt to pull the "
+                + "remainder yourself. If you need specific paths to "
+                + "finish, quote them in your verdict and the Hands will "
+                + "pull them via read_file and re-run QA.]"
             )
         # Same V1 guard as the task attach: break fence parsing invisibly
         # so embedded fences in diff content cannot close our block early.
diff --git a/tests/test_brain_diff_attach.py b/tests/test_brain_diff_attach.py
index b295f26..2498cbe 100644
--- a/tests/test_brain_diff_attach.py
+++ b/tests/test_brain_diff_attach.py
@@ -99,6 +99,24 @@ def test_build_diff_attach_over_cap_truncates(monkeypatch, tmp_path):
     assert len(out) < 50000
 
 
+def test_build_diff_attach_truncation_note_is_unverifiable(monkeypatch, tmp_path):
+    # Issue 14: the Brain has zero tool calls, so the truncation note must
+    # order UNVERIFIABLE-not-REJECTED and address the pull path to the
+    # Hands — never instruct the Brain to pull via read_file itself.
+    target = tmp_path / "99-sample.md"
+    target.write_text(_task_text("x" * 50000), encoding="utf-8")
+    monkeypatch.setattr(
+        bridge, "_resolve_task_file",
+        lambda tid, project_root=None: target)
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    monkeypatch.setattr(bridge, "_TASK_DIFF_CAP", 100)
+    out = bridge.build_diff_attach("99")
+    assert "UNVERIFIABLE" in out
+    assert "NEVER emit REJECTED" in out
+    assert "no file tools" in out
+    assert "Hands will" in out and "read_file" in out
+
+
 def test_extract_diff_empty_pair_yields_empty():
     text = "<!-- BEGIN_GIT_DIFF --><!-- END_GIT_DIFF -->\n"
     assert bridge.extract_task_diff(text) == ""
```
<!-- END_GIT_DIFF -->
