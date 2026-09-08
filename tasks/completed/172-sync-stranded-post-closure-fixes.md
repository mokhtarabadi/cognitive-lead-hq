# Task 172: Sync Stranded Post-Closure Fixes

**File:** `tasks/qa/172-sync-stranded-post-closure-fixes.md`
**Source:** manager
**Type:** bug
**Status:** in-progress

## Source Context

## Goal

Commit three files whose working-tree fixes missed the Task 171 closure commit (stale index content was committed): persona server transcript fix, archived 169/170 header sync.

## Manager's Notes

- Root cause: the transcript-blowup fix to `mcp-persona-server/server.py` landed after the last staging; the closure commit captured the pre-fix index version. Archived 169/170 likewise committed with pre-patch headers (bundler glitch fixes stayed unstaged).
- HEAD is internally inconsistent (committed tests expect no body-append; committed server still appends). This task re-syncs index to the tested working tree. No code changes — staging only.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Identify stranded files (diff HEAD vs worktree)
- [x] Stage via `custom_context_stage_and_inject_diff`, move to QA

## Acceptance Criteria

- [x] `mcp-persona-server/server.py` at HEAD matches tested working tree (no `_read_task_file`)
- [x] Archived 169/170 carry `Status: superseded` headers
- [x] Full suite green on the exact committed content

## Verification Evidence

- **Test command:** same locked pytest invocation (suite green on identical working tree)
- **Expected result:** 120 passed, exit 0
- **Actual result:** `120 passed, 8 warnings in 1.28s` (recorded pre-closure on this exact tree)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append (N/A — sync-only, fixes already logged under Task 171)
- [ ] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** None-code change; staging-only sync. Rollback: `git reset HEAD -- <paths>`.
- **Rollback plan:** Unstage; HEAD remains as-is.

---

## Execution Log & Reasoning

Sync-only task: no source edits. `git show HEAD:...` vs worktree comparison proved the closure commit `a37c3cb` captured pre-fix index content for exactly 3 files (persona server + 2 archived headers). Re-staging the tested tree restores consistency. CHANGELOG already covers the fixes (Task 171 entries); DoD lint box checks at QA gate.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/mcp-persona-server/server.py b/mcp-persona-server/server.py
index 5ff2373..baf7493 100644
--- a/mcp-persona-server/server.py
+++ b/mcp-persona-server/server.py
@@ -132,19 +132,6 @@ def _call_llm(model: str, messages: list[dict[str, str]]) -> str:
     return str(response.choices[0].message.content or "")
 
 
-def _read_task_file(task_file_path: Optional[str]) -> Optional[str]:
-    """Read the task file body for lineage injection; None when absent."""
-    if not task_file_path:
-        return None
-    candidate = Path(task_file_path)
-    if not candidate.is_absolute():
-        candidate = REPO_ROOT / task_file_path
-    try:
-        return candidate.read_text(encoding="utf-8")
-    except (OSError, UnicodeError):
-        return None
-
-
 @mcp.tool()
 def dispatch_session_turn(
     task_id: int,
@@ -184,15 +171,17 @@ def dispatch_session_turn(
         ``xml_content`` (XML_EXTRACTED), ``question`` (QUESTION),
         ``report`` (REPORT), or ``hint`` (RETRY_NEEDED).
     """
-    task_body = _read_task_file(task_file_path)
-    if task_body is not None:
-        append_turn(task_id, "user", f"Task file `{task_file_path}` injected.\n\n{task_body}")
+    # NOTE: the task file body is injected into the LLM messages by
+    # build_persona_messages below — it is deliberately NOT appended to the
+    # transcript. Appending full file bodies per turn made transcripts grow
+    # without bound (each replay re-sent every prior dump: 6MB → 1.5M-token
+    # requests → endpoint 400s). The transcript keeps turns only.
     append_turn(task_id, "user", instruction, name="executor")
 
     # Transcript replay already carries the injected task body + instruction,
     # so build messages without re-injecting the file (avoids triple context).
     messages = build_persona_messages(
-        task_id, persona_name, instruction, None, repo_root=REPO_ROOT
+        task_id, persona_name, instruction, task_file_path, repo_root=REPO_ROOT
     )
     output = _call_llm(_get_persona_model(), messages)
     append_turn(task_id, "assistant", output, name=persona_name)
```
<!-- END_GIT_DIFF -->
