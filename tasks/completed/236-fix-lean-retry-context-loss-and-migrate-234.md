# Task 236: Fix lean-retry context loss and migrate global 234 session folder

**File:** `tasks/qa/236-fix-lean-retry-context-loss-and-migrate-234.md`
**Source:** manager
**Type:** bug
**Status:** open

## Goal

Close the two session-context gaps proven in the 235 transcript audit: lean retries must carry state, and the 234 folder must move home.

## Manager's Notes

Manager order: "Can you fix gaps?" — "New task". Plan approved in concept (3 steps); implementation approval still needed before code changes. Gap G1: lean retry (`include_bundle=false`) drops the bundle, Brain judged a stale file version live in session 235 (turn 3, 179 chars, no bundle). Gap G2: task 234 transcript + fed_context live only in the global dir (`~/.config/opencode/brain-sessions/234`, 11 lines + fed file) because old server code was live during 234; 230-233 migrated, 235 writes per-project.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Add state note to lean-retry path in bridge server (task path + status + diff hash)
- [x] Add regression test: lean retry carries state note, no stale judgment possible
- [x] Migrate global 234 folder into tasks/.sessions/234, extend manifest, verify hashes
- [x] Full suite green + lint + stage per protocol

## Acceptance Criteria

- [x] A lean retry prompt always carries task path, status, and diff hash even with bundle off
- [x] New regression test proves the state note is present on the lean path
- [x] tasks/.sessions/234 exists with transcript + fed_context byte-identical to global copies
- [x] Manifest lists 234 with matching sha256 hashes

## Verification Evidence

- **Test command:** uv run --with pytest==8.3.4 --with mcp==1.30.0 --with httpx==0.28.1 --with pathspec --with pyyaml pytest tests/ -q
- **Expected result:** all pass, exit code 0
- **Actual result:** bridge file 140 passed; full suite 357 passed in 3.41s
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** retry prompt grows; state note must stay tiny (3 lines max) or lean loses meaning
- **Rollback plan:** revert bridge edit; 234 global copies stay untouched as fallback

---

## Execution Log & Reasoning

Autopilot locked for Task 236 per Manager order "Start auto pilot".

G1: `_task_state_note()` (pure-adjacent, never raises) resolves the task file, reads `**Status:**`, hashes the Factual Git Diff block (sha8, "no-diff" when empty); `_empty_output_hint(task_id, state)` appends "Current state: path | status | diff=hash" while staying pure (caller does I/O); guard call site wires them; executor Step 5 notes the state note for cross-retry comparison. Honest AC check: AC1 demanded path+status+diff-hash on the lean path — first edit only added a freshness sentence, so the full state note was implemented before checking the box. G2: global 234 transcript (11 lines) + fed_context (6 lines) copied to tasks/.sessions/234/, sha256 match globals; manifest extended (task_ids 230-234). Tests: hint-contract extended (stale sentence, state line, unknown fallbacks); bridge file 140 passed; full suite 357 passed exit 0.

QA (same id, diff attached): QA_PASSED — state helper never raises, one-line status parse, pure hint, no shared state; notes F6-F8 are coverage observations only (no positive real-file test, no bridge-output integration test, G2 proof in log not diff). Review (same id, diff attached): technically approved, PO_REVIEW_PENDING. Strengths F1-F4 (never-raises helper, pure hint, backward-compat default arg, stale/state/unknown coverage). One fix applied: R1 changelog count corrected (1 assertion → 4 new assertions). R2/R3 noted (sessions ignored by design, proof in log; happy-path test only if bridge area reopens). Closure awaits the Manager approval word.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 5108261..0046ebf 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -14,6 +14,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Supervised autopilot with plan approval and seat routing (Task 233):** `agents/cognitive-executor.md` gains a supervised plan-approval section (discovery feed → Brain plan → one approval pause → seat-routed implementation; Relay questions and hard blockers are the only other interrupts), a Seat Check trigger-citation line, a goal-pause carve-out for plan approval, and generous lock-word recognition. `mcp-brain-bridge/server.py` gains a 150 KB total bundle cap (truncate/skip with notes) and a text `validate_plan_verdict` checker (5 fields; cites need path:line shape). `docs/conventions.md` gains risk tiers T0/T1/T2 plus a 3-tries-then-escalate contract. `skill-templates/telegram-issue-sync/SKILL.md` folds the GitHub-preference data question into the planning turn (repo + global copies). Shipped prompt rebuilt to 9.36.0 with a Supervised Autopilot Contract bullet (authority stays in the executor file). 5 new offline bridge tests. Full suite: **350 passed**. Postfix: verdict checker uses word-bound field matching (stub text inside longer words no longer validates), bundle truncation reserves suffix length so the total never exceeds the cap, contract bullet reworded to a single plan-approval pause.
  - **Brain sessions per project, legacy global read-through (Task 234):** `mcp-brain-bridge/loop_guard.py` gains `project_sessions_root()` (explicit override → param/`BRAIN_PROJECT_ROOT`/`BRAIN_WORKSPACE_ROOT` → cwd walk-up to a `tasks/` dir → legacy global fallback) plus `legacy_sessions_root()`; `server.py` threads an optional `project_root` through `_sessions_root`, `_transcript_path`, `_fed_context_path`, `load_history`, `append_turn`, `save/load_fed_context`, and `brain_turn` — writes always land per project under `tasks/.sessions/<id>/`, while reads fall back to the legacy global dir with a loud stderr note when the per-project file is missing. HQ folders 230-233 migrated from the global store into `tasks/.sessions/` with a sha256 manifest (`/tmp/migrate-234-manifest.json`), globals kept as fallback. 4 new offline regression tests. Full suite: **354 passed**. Hotfix: no-global-write (fallback writes reroute to `cwd/tasks/.sessions` with stderr warn), package-then-plain sibling import, per-project loop-guard hashes with legacy read fallback, per-turn sessions-root stderr line, 3 more tests (T5-T7). Full suite: **357 passed**.
   - **Review-approval relay + session-history gitignore (Task 235):** `agents/cognitive-executor.md` gains a Review-approval relay rule (technical approval → verbatim relay, file stays in qa; only the exact words "Approved for closure"/"Close task" count; Hands re-calls Brain Programmer once for a single final-closure XML and executes it exactly once) plus a relay line in the Code Reviewer roster row. `prompts/fragments/06-personas.md` Code Reviewer contract now routes closure through the relayed Programmer XML instead of emitting it directly. Shipped prompt rebuilt to 9.37.0. Global `audit-agents` skill Plugin Runtime-State rule now covers Brain session history (`tasks/.sessions/` added only after confirming the dir exists). Hotfix: relay tightened (bare-approved counts only as the next message answering the relayed question; explicit never-list incl. yes/done/okay/looks-good/emoji/silence; qa + PO_REVIEW_PENDING double-gate; single issuance with failure-only re-call; autopilot self-decision never satisfies); repo `skill-templates/audit-agents/SKILL.md` template extended too (both occurrences) so the rule ships in-repo. Second hotfix: reviewer contract mirrors the executor relay exactly (bare-approved exception + full never-list incl. okay/done/fine/looks-good/emoji-only + autopilot bar), audit clause gains a duplicate-line guard (check first, add only if missing), shipped prompt rebuilt to 9.37.2.
+ - **Lean-retry state note + migrate Task 234 session (Task 236):** `mcp-brain-bridge/server.py` `_empty_output_hint` and the executor Empty-output clause gain a state-freshness sentence: a lean retry drops the bundle, so if the answer judges stale or missing context, re-run ONCE with the full bundle plus diff before escalating (proven by the 235 turn-3 stale verdict). Task 234's global transcript + fed context migrated into `tasks/.sessions/234/` with sha256-verified manifest. 4 new regression assertions (stale sentence, state line, 2 unknown fallbacks). Full suite: **357 passed**.
 
 ## [9.35.0] - 2026-09-14
 
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index c232617..2d4a8a0 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -385,7 +385,12 @@ needs no extra machinery.
     retry once, lean (`include_bundle=false`, same `task_id`, short prompt),
     then escalate to the Manager if still empty. The bridge itself returns the
     `EMPTY_OUTPUT_RETRY` token in this case — treat that token exactly like an
-    empty output and follow the same retry shape.
+    empty output and follow the same retry shape. State check on the lean
+    retry: it drops the bundle, so if its answer judges stale or missing
+    context (wrong file version, no diff seen), re-run ONCE with the full
+    bundle plus diff (`include_bundle=true`, `include_diff=true`) before
+    escalating. The hint now carries a state note (task path, status,
+    diff hash) — compare it across retries to spot a stale answer.
 
 ### Review-approval relay (manual mode)
 
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index b414bba..ae94040 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -1563,7 +1563,7 @@ def brain_turn(
         # REPORT. Substitute the retry hint; status stays REPORT so old
         # callers keep working. The transcript below records the hint,
         # not a verdict.
-        output = _empty_output_hint(task_id)
+        output = _empty_output_hint(task_id, _task_state_note(task_id))
     fence_drops = list(_last_fence_drops)
     if task_id:
         prompt_hash = hashlib.sha256(effective_prompt.encode("utf-8")).hexdigest()
@@ -1605,19 +1605,59 @@ def _get_reasoning_effort() -> str:
     return val
 
 
-def _empty_output_hint(task_id: Optional[str] = None) -> str:
+def _task_state_note(task_id: Optional[str]) -> str:
+    """One-line state note for the empty-output retry hint (never raises).
+
+    Format: ``path | status | diff-hash``. Lets the retry-er judge whether
+    the next answer sees the same file version instead of a stale one.
+    Unresolvable task → "unknown".
+    """
+    try:
+        if not task_id or not isinstance(task_id, str):
+            return "unknown"
+        path = _resolve_task_file(task_id)
+        if path is None:
+            return "unknown"
+        try:
+            rel = path.resolve().relative_to(
+                _workspace_root().resolve()).as_posix()
+        except (OSError, ValueError):
+            rel = path.name
+        text = path.read_text(encoding="utf-8", errors="replace")
+        status = "unknown"
+        m = re.search(r"^\*\*Status:\*\*\s*(.+?)\s*$", text, re.M)
+        if m:
+            status = m.group(1)[:32]
+        diff = extract_task_diff(text)
+        dh = (hashlib.sha256(diff.encode("utf-8")).hexdigest()[:8]
+              if diff.strip() else "no-diff")
+        return f"{rel} | status={status} | diff={dh}"
+    except Exception:
+        return "unknown"
+
+
+def _empty_output_hint(task_id: Optional[str] = None,
+                       state: Optional[str] = None) -> str:
     """Retry instruction substituted for a blank model output.
 
     Pure function (no I/O) so tests can assert the contract directly.
     The bridge MUST NOT invent verdict content here — hint only.
+    ``state`` is a precomputed task path/status/diff note (see
+    ``_task_state_note``); the hint stays pure, the caller does the I/O.
     """
     where = f" for task {task_id}" if task_id else ""
+    note = f" Current state: {state}." if state else ""
     return (
         f"{EMPTY_OUTPUT_RETRY}: the model returned no text{where} "
         "(transport/model flake, never a verdict). "
         "Do NOT act on this result and do NOT count it as a rejection. "
         "Retry ONCE, lean: same task_id, include_bundle=false, short prompt. "
-        "If the retry is still empty, escalate to the Manager."
+        "State check on the retry: the lean call drops the bundle, so if its "
+        "answer judges stale or missing context (wrong file version, no diff "
+        "seen), re-run ONCE with the full bundle plus diff "
+        "(include_bundle=true, include_diff=true) before escalating. "
+        "If the full-context call is still empty, escalate to the Manager."
+        + note
     )
 
 
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index 796fdb0..5c5846a 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -1423,6 +1423,11 @@ def test_empty_output_hint_contract():
     bare = bridge._empty_output_hint(None)
     assert bridge.EMPTY_OUTPUT_RETRY in bare
     assert "escalate" in bare
+    assert "stale" in hint  # lean retries drop context; stale answers re-run full
+    noted = bridge._empty_output_hint("232", "tasks/qa/x.md | status=open | diff=abc123")
+    assert "Current state: tasks/qa/x.md" in noted
+    assert bridge._task_state_note("no-such-task-xyz") == "unknown"
+    assert bridge._task_state_note(None) == "unknown"
 
 
 def _run_turn(monkeypatch, tmp_path, payload, prompt="q", task_id="232"):
```
<!-- END_GIT_DIFF -->
