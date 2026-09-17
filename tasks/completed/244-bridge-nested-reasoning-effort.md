# Task 244: Bridge nested reasoning effort fix

**File:** `tasks/qa/244-bridge-nested-reasoning-effort.md`
**Source:** manager
**Type:** bug
**Status:** open

## Goal

Task the orphaned Bridge reasoning-effort fix (nested `reasoning.effort` Responses body + tests) so it is verified, reviewed, and closable instead of riding the worktree unowned.

## Manager's Notes

Manager order (exact): "do it" — create a task for the orphaned bridge reasoning-fix files and work it. Files: `mcp-brain-bridge/server.py` + `tests/test_brain_bridge.py` (uncommitted worktree modifications; the live 400 error forced flat `reasoning_effort` → nested `reasoning:{effort}`). Sibling files `mcp-decision-server/server.py` + `.env.example` belong to open Task 243 — do NOT sweep them in. Autopilot locked for this order.

## Local TODOs

- [x] Move file to in-progress, sync header, Seat Check
- [x] Verify orphaned diff (read hunks, confirm nested-effort scope only)
- [x] Run focused + full suites, record counts
- [x] CHANGELOG bullet, lint, stage, move to qa
- [ ] Brain QA + reviewer turns, handoff (no commit/close without approval word)

## Acceptance Criteria

- [x] Orphaned bridge hunks verified as nested reasoning-effort scope only
- [x] Focused + full suites green with recorded counts
- [x] Diff staged, file in qa, no commit, no close
- [x] Brain QA + reviewer verdicts recorded

## Verification Evidence

- **Test command:** `uv tool run --with "mcp==1.4.1" --with pathspec --with pyyaml --with pytest pytest tests/ -q`
- **Expected result:** exit 0, full suite green
- **Actual result:** **400 passed**, exit 0 (full suite); focused `tests/test_brain_bridge.py`: **157 passed**, exit 0
- **Exit code:** 0 (both runs)

## Definition of Done

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** shared-worktree confusion with Task 243 files; API-shape regression against providers
- **Rollback plan:** small scoped diff, no destructive ops, revert via worktree diff

---

## Execution Log & Reasoning

Seat Check: Senior Programmer (bridge repair + tests); Software Architect (Responses API-shape call). No UI/schema/sprint/QA-seat triggers — Designer, Planner, Strategist skipped (code-only bridge fix, they judge later turns). Autopilot locked. Replayed from DEC-20260915-001 (2026-09-15): fix-all via Hands on autopilot. Replayed from DEC-20260914-003 (2026-09-14): standing zero-questions autopilot.

- QA verdict: VERDICT QA_PASSED (live gpt-5.6-luna turn, trunc 0). Nested effort + temp-branch removal confirmed (CITE server.py:1783,1797; tests :512,518); no vuln, no blocking test gaps; 157 focused + 400 full green.
- Reviewer verdict: APPROVED, state PO_REVIEW_PENDING (no issues in scope; CITE server.py:1783,1797, tests :512,518; closure only on exact phrases).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index ae5ca71..ba4e4ab 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -30,6 +30,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Context-handling gaps: utilization ledger + over-cap signatures fallback (Task 241 extension, web-research findings):** `mcp-brain-bridge/server.py` gains a per-turn context ledger (`_MODEL_WINDOW_CHARS=200000`, one JSON line per turn — task_id, budget_chars, est_tokens, util_pct, truncated — to `context_ledger.jsonl`, best-effort never-raise) and the prompt-size warn now shows `util~%`, so truncation pressure is measured instead of guessed. `mcp-context-server/server.py` `process_source_file` over-cap branch now appends tree-sitter signatures (or a narrow-paths pointer) instead of silently skipping the file, so discovery keeps structural signal past the cap. 2 new tests (ledger+util, too-large-signatures). Full suite: **389 passed**, zero failures.
 - **Decision-redactor word-edge leak (Task 242, Phase 1 B1):** `mcp-decision-server/redactor.py` assignment rule leading edge `\b` → `(?<![A-Za-z0-9])` in both sanitize and verify patterns, so ENV-style `KEY=value` names (`BRAIN_API_KEY=`, `FOO_SECRET=`) redact while prose `topsecret=` stays untouched; new short-Bearer rule (`{4,7}` chars with digit gate) catches `Bearer abc123`-shaped tokens while prose `Bearer tokens` and the `{8,}` rule stay unchanged. 4 new tests (3 failed pre-fix as required). Full decision suite: **105 passed**, zero failures. QA-hotfix regression tests added (punctuation Bearer, quoted forms — all green pre-fix; the claimed `-1` suffix leak did not reproduce: `-` is inside the token class, direct evidence recorded in Task 242). Full suite: **400 passed**, zero failures.
 - **Decision-server DECISION_* env support (Task 243):** `mcp-decision-server/server.py` now reads `DECISION_API_BASE`, `DECISION_API_KEY`, `DECISION_MODEL`, `DECISION_REASONING_EFFORT`, each with `BRAIN_*` fallback (fail-closed error names both key vars); new module-level `_get_api_base()` helper; `.env.example` DECISION section extended with the four lines + fallback docs. 3 new contract tests (precedence, blank-fallback, fail-closed); 2 old tests fixed for env hermeticity. Full suite: **396 passed**, zero failures.
+- **Bridge nested reasoning-effort fix (Task 244):** `mcp-brain-bridge/server.py` now sends `reasoning.effort` as a nested `reasoning: {effort}` object in the Responses body (the flat `reasoning_effort` key was rejected with a provider 400 on the first live OpenRouter turn); the explicit-temperature branch drops the reasoning key, mirroring the bridge contract. 2 existing tests updated to the nested shape. Full suite: **400 passed**, zero failures.
 
 ## [9.35.0] - 2026-09-14
 
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 8986096..0cac7f5 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -1777,12 +1777,15 @@ def brain_turn(
     body: dict[str, Any] = {
         "model": model,
         "input": chat,
-        "reasoning_effort": _get_reasoning_effort(),
+        # Responses API shape: effort nests under reasoning (flat
+        # reasoning_effort is rejected by strict providers, e.g.
+        # OpenAI/OpenRouter 400 unsupported_parameter).
+        "reasoning": {"effort": _get_reasoning_effort()},
         "max_output_tokens": _get_max_tokens(),
     }
     # Blank-means-unset: only send temperature when explicitly set. A
-    # non-blank temperature conflicts with reasoning_effort on Responses
-    # models, so drop the effort key when temperature is present.
+    # non-blank temperature conflicts with reasoning effort on Responses
+    # models, so drop the reasoning key when temperature is present.
     _temp_raw = os.environ.get("BRAIN_TEMPERATURE", "")
     if _temp_raw.strip():
         try:
@@ -1793,7 +1796,7 @@ def brain_turn(
                 "set a numeric value or leave it blank"
             )
         else:
-            del body["reasoning_effort"]
+            del body["reasoning"]
     with httpx.Client(
         timeout=httpx.Timeout(connect=10, read=120, write=30, pool=10)
     ) as client:
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index d30c5d2..355ae40 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -508,13 +508,13 @@ def test_brain_turn_temperature_omitted_unless_set(tmp_path, monkeypatch):
     target = call.fn if hasattr(call, "fn") else call
     target("q")
     assert "temperature" not in holder["body"]
-    assert "reasoning_effort" in holder["body"]
+    assert holder["body"].get("reasoning", {}).get("effort")
     monkeypatch.setenv("BRAIN_TEMPERATURE", "0.7")
     holder2 = {}
     _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload())], holder2)
     target("q2")
     assert holder2["body"]["temperature"] == 0.7
-    assert "reasoning_effort" not in holder2["body"]
+    assert "reasoning" not in holder2["body"]
 
 
 def test_long_task_id_error_carries_migration_hint(tmp_path, monkeypatch):
```
<!-- END_GIT_DIFF -->
