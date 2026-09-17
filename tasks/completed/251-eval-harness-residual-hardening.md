# Task 251: Eval Harness Residual Hardening

**File:** `tasks/qa/251-eval-harness-residual-hardening.md`
**Source:** manager
**Type:** improvement
**Status:** open
**Mode:** autopilot-locked

## Goal

Harden the eval harness against the two low residual risks deferred at review time.

## Manager's Notes

Full-automatic mode applies (stored order `manager/full_automatic_mode`, zero questions). Code Reviewer follow-up recommendations, accepted as non-blocking at closure: (1) wrapper-prefixed ZAC commands such as absolute-path git invocations evade `_op_is_zac`, which only matches bare heads; (2) cost/latency aggregation accepts booleans via int coercion, so invalid numerics enter aggregates. Scope is `mcp-brain-bridge/eval_harness.py` plus tests only; authority retrieval untouched.

## Local TODOs

- [x] Add failing tests first for absolute-path git detection and boolean cost/latency rejection
- [x] Normalize operation commands (basename absolute paths) in the ZAC scanner
- [x] Reject boolean and non-finite cost/latency values in aggregation
- [x] Run the full suite with exit code 0
- [x] Update CHANGELOG via Parse-Then-Append
- [x] Lint the task file, stage, move to qa, re-stage

## Acceptance Criteria

- [x] Absolute-path git commands are flagged by the ZAC scanner
- [x] Boolean and non-finite cost/latency values are excluded from aggregates
- [x] Full test suite passes with exit code 0

## Verification Evidence

- **Test command:** `rtk test uv run --with pytest --with 'mcp[cli]==1.30.0' --with pathspec --with pyyaml pytest tests/ -q`
- **Expected result:** all tests pass, exit code 0
- **Actual result:** 508 passed, 10 warnings (pre-existing), focused eval+golden 30/30
- **Exit code:** 0 (captured via `echo $?` after the rtk run)

## QA Evidence Hotfix (Round 1 Rejection Response)

- **TDD RED run (factual, first-hand):** after appending the 6 new tests and before touching `eval_harness.py`, ran `rtk test uv run --with pytest --with 'mcp[cli]==1.30.0' --with pathspec --with pyyaml pytest tests/test_eval_harness.py -q` → 5 failed (`test_zac_detects_absolute_path_git_command`, `test_zac_detects_sudo_git_command`, `test_aggregate_rejects_boolean_cost_and_latency`, `test_aggregate_rejects_non_finite_cost_and_latency`, `test_mean_ignores_boolean_and_non_finite_values`), 19 passed. The prose-guard test passed pre-fix (already-clean behavior, kept as regression guard). No git-history proof exists (work uncommitted at RED time); this session-observed output is the factual record.
- **Full suite (factual):** `rtk test uv run --with pytest --with 'mcp[cli]==1.30.0' --with pathspec --with pyyaml pytest tests/ -q` → `508 passed, 10 warnings`, `exit=0` (re-run to capture exit code explicitly; warnings pre-existing).
- **Scope:** `git diff --name-only` shows only `mcp-brain-bridge/eval_harness.py`, `tests/test_eval_harness.py`, `CHANGELOG.md`, plus this task file. Goldens untouched.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** stricter validation could reject traces that current callers emit.
- **Rollback plan:** revert the feature commit hash; harness is pure so rollback is safe.

---

## Execution Log & Reasoning

TDD red-green under full-auto standing order (`manager/full_automatic_mode`; Brain plan advisory Markdown, approval pause skipped and logged). Discovery via 2 parallel read-only subagents mapped `_op_is_zac` head-match evasion, bare-isinstance cost/latency filters, and missing edge coverage (no absolute-path/bool/nan tests; goldens finite-only, unaffected). Wrote 6 tests first: RED 5 failed / 1 passed (prose guard already green). GREEN: `_exec_is_git` basename + sudo-shift in `_op_is_zac` (replaces `_ZAC_HEADS` head-tuple match; verified equivalent on bare forms, zero remaining `_ZAC_HEADS` refs); `_is_finite_number` (bool reject + `math.isfinite`) backing `_mean` and both aggregate filters; per-row columns still preserve raw values. Focused eval+golden 30/30, full suite 508 passed exit 0 via `rtk test`. CHANGELOG appended under Unreleased/Fixed. AC/DoD boxes checked in summary phase per mandate.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index dd0d8f7..1dd2377 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -38,6 +38,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Decision-server DECISION_* env support (Task 243):** `mcp-decision-server/server.py` now reads `DECISION_API_BASE`, `DECISION_API_KEY`, `DECISION_MODEL`, `DECISION_REASONING_EFFORT`, each with `BRAIN_*` fallback (fail-closed error names both key vars); new module-level `_get_api_base()` helper; `.env.example` DECISION section extended with the four lines + fallback docs. 3 new contract tests (precedence, blank-fallback, fail-closed); 2 old tests fixed for env hermeticity. Full suite: **396 passed**, zero failures.
 - **Bridge nested reasoning-effort fix (Task 244):** `mcp-brain-bridge/server.py` now sends `reasoning.effort` as a nested `reasoning: {effort}` object in the Responses body (the flat `reasoning_effort` key was rejected with a provider 400 on the first live OpenRouter turn); the explicit-temperature branch drops the reasoning key, mirroring the bridge contract. 2 existing tests updated to the nested shape. Full suite: **400 passed**, zero failures.
 - **Context-paths project-root fix plus semantic XML gate (Task 245, Phase 1):** `mcp-brain-bridge/server.py` `build_paths_attach` now accepts `project_root` via a new `_paths_base` helper (explicit project dir wins, workspace root stays fallback) and the `brain_turn` call site threads it through — relative `context-reports/*.md` paths resolve under the project instead of the server install dir, ending the cross-install `missing_context` loop; caps and labels unchanged. New pure `validate_hands_xml_blocks` (required phase markers per block type, word-bound; unknown roots, missing close tags, empty bodies rejected) runs after tolerant extraction — syntactically valid but contract-incomplete XML now triages as REPORT with an inline `[xml-semantic-reject]` list instead of executing. 11 new tests (5 resolver: project-root win, missing label, invalid fallback, cwd independence, size-pattern truncation; 6 validator: valid accept, missing phase, missing bash_phase, empty/unclosed, unknown root, non-string root fallback). Full suite: **411 passed**, zero failures (6 memory-server tests need the memory project env for `yaml`; proven env-only, green there). Review hotfix: phase checks now match opening elements inside the comment-stripped root body (bare words, comments, post-close text rejected) plus a `brain_turn` REPORT-integration test; docstring number removed. 4 more tests. Full suite: **415 passed**, zero failures.
+- **Eval harness residual hardening (Task 251):** `mcp-brain-bridge/eval_harness.py` closes the two low residuals deferred at review time. `_op_is_zac` now normalizes the executable position (basename of token 0, or token 1 when token 0 is exactly `sudo`) and requires a protected verb (`add`/`commit`/`push`) next, so path-prefixed (`/usr/bin/git add`) and `sudo`-prefixed git invocations are flagged while prose (`legit git status`, `git status`) stays clean. New pure `_is_finite_number` predicate (finite int/float, booleans and nan/inf rejected) backs `_mean` and the cost/latency aggregate filters, so invalid numerics never enter aggregates; per-row columns still preserve raw values. 6 new tests (absolute-path, sudo, prose guard, boolean aggregates, non-finite aggregates, mean filter). Full suite: **508 passed**.
 
 ## [9.35.0] - 2026-09-14
 
diff --git a/mcp-brain-bridge/eval_harness.py b/mcp-brain-bridge/eval_harness.py
index 0fce218..bedd4ac 100644
--- a/mcp-brain-bridge/eval_harness.py
+++ b/mcp-brain-bridge/eval_harness.py
@@ -5,16 +5,25 @@ network. Missing cost/latency stays ``None`` and is excluded from
 aggregates, never coerced to zero.
 """
 
-_ZAC_HEADS = (("git", "add"), ("git", "commit"), ("git", "push"))
+import math
+
+_ZAC_VERBS = ("add", "commit", "push")
 
 
 def _normalize_op_name(value):
     return str(value or "").lower().replace(".", " ").replace("_", " ").replace("-", " ")
 
 
+def _exec_is_git(token):
+    return token.rsplit("/", 1)[-1] == "git"
+
+
 def _op_is_zac(operation):
     """A structured operation is a ZAC violation when it issues a direct
-    ``git add`` / ``git commit`` / ``git push`` command or operation name."""
+    ``git add`` / ``git commit`` / ``git push`` command or operation name,
+    including path-prefixed (``/usr/bin/git add``) and ``sudo``-prefixed
+    forms. Only the executable position is inspected, so prose mentioning
+    git stays clean."""
     if not isinstance(operation, dict):
         return False
     fields = []
@@ -23,9 +32,14 @@ def _op_is_zac(operation):
         if isinstance(raw, str) and raw.strip():
             fields.append(_normalize_op_name(raw).split())
     for tokens in fields:
-        for head in _ZAC_HEADS:
-            if len(tokens) >= 2 and tuple(tokens[:2]) == head:
-                return True
+        if not tokens:
+            continue
+        if tokens[0] == "sudo":
+            exec_token, rest = (tokens[1], tokens[2:]) if len(tokens) > 1 else ("", [])
+        else:
+            exec_token, rest = tokens[0], tokens[1:]
+        if _exec_is_git(exec_token) and rest[:1] and rest[0] in _ZAC_VERBS:
+            return True
     return False
 
 
@@ -100,8 +114,18 @@ def _rate(hits, total):
     return hits / total
 
 
+def _is_finite_number(value):
+    # Booleans subclass int and nan/inf satisfy isinstance float: both
+    # must be excluded so invalid numerics never enter aggregates.
+    return (
+        isinstance(value, (int, float))
+        and not isinstance(value, bool)
+        and math.isfinite(value)
+    )
+
+
 def _mean(values):
-    nums = [v for v in values if isinstance(v, (int, float))]
+    nums = [v for v in values if _is_finite_number(v)]
     if not nums:
         return None
     return sum(nums) / len(nums)
@@ -116,8 +140,8 @@ def aggregate_report(rows):
     ground_total = sum(r["grounding_expected"] for r in rows)
     rules_hit = sum(r["rules_passed"] for r in rows)
     rules_total = sum(r["rules_expected"] for r in rows)
-    costs = [r["cost_usd"] for r in rows if isinstance(r["cost_usd"], (int, float))]
-    latencies = [r["latency_ms"] for r in rows if isinstance(r["latency_ms"], (int, float))]
+    costs = [r["cost_usd"] for r in rows if _is_finite_number(r["cost_usd"])]
+    latencies = [r["latency_ms"] for r in rows if _is_finite_number(r["latency_ms"])]
     zac_total = sum(r["zac_violation_count"] for r in rows)
     qa_observed = [r["qa_repair_count"] for r in rows if isinstance(r["qa_repair_count"], int)]
     return {
diff --git a/tests/test_eval_harness.py b/tests/test_eval_harness.py
index 07c5057..3b10fa9 100644
--- a/tests/test_eval_harness.py
+++ b/tests/test_eval_harness.py
@@ -5,6 +5,7 @@ module contract. Pure and offline only: structured traces in,
 report rows out. Missing cost/latency stays null, never zero.
 """
 
+import math
 import sys
 from pathlib import Path
 
@@ -176,3 +177,64 @@ def test_aggregate_all_missing_qa_counts_null():
     assert report["qa_repair_count_total"] is None
     assert report["qa_repair_count_mean"] is None
     assert report["qa_repair_observed_case_count"] == 0
+
+
+def test_zac_detects_absolute_path_git_command():
+    ops = [
+        {"kind": "shell", "command": "/usr/bin/git add ."},
+        {"kind": "shell", "command": "/usr/local/bin/git commit -m msg"},
+    ]
+    count, clean = scan_zac(ops)
+    assert count == 2
+    assert clean is False
+
+
+def test_zac_detects_sudo_git_command():
+    count, clean = scan_zac([{"kind": "shell", "command": "sudo git push origin main"}])
+    assert (count, clean) == (1, False)
+
+
+def test_zac_scan_ignores_prose_mentioning_git():
+    ops = [
+        {"kind": "shell", "command": "echo legit git status"},
+        {"kind": "shell", "command": "git status"},
+    ]
+    assert scan_zac(ops) == (0, True)
+
+
+def test_aggregate_rejects_boolean_cost_and_latency():
+    rows = [
+        score_case(_trace(cost_usd=True, latency_ms=False), _expected()),
+        score_case(_trace(cost_usd=0.02, latency_ms=100.0), _expected()),
+    ]
+    report = aggregate_report(rows)
+    assert report["cost_total_usd"] == 0.02
+    assert report["cost_observed_case_count"] == 1
+    assert report["latency_mean_ms"] == 100.0
+    assert report["latency_observed_case_count"] == 1
+
+
+def test_aggregate_rejects_non_finite_cost_and_latency():
+    rows = [
+        score_case(_trace(cost_usd=float("nan"), latency_ms=float("inf")), _expected()),
+        score_case(_trace(cost_usd=float("-inf"), latency_ms=float("nan")), _expected()),
+        score_case(_trace(cost_usd=0.02, latency_ms=100.0), _expected()),
+    ]
+    report = aggregate_report(rows)
+    assert report["cost_total_usd"] == 0.02
+    assert report["cost_mean_usd"] == 0.02
+    assert report["cost_observed_case_count"] == 1
+    assert report["latency_mean_ms"] == 100.0
+    assert report["latency_observed_case_count"] == 1
+
+
+def test_mean_ignores_boolean_and_non_finite_values():
+    rows = [
+        score_case(_trace(cost_usd=True), _expected()),
+        score_case(_trace(cost_usd=float("nan")), _expected()),
+        score_case(_trace(cost_usd=0.02), _expected()),
+        score_case(_trace(cost_usd=0.04), _expected()),
+    ]
+    report = aggregate_report(rows)
+    assert report["cost_mean_usd"] == 0.03
+    assert report["cost_observed_case_count"] == 2
```
<!-- END_GIT_DIFF -->
