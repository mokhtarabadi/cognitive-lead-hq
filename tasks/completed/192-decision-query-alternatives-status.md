# Task 192: Decision query searches alternatives and status fields

**File:** `tasks/completed/192-decision-query-alternatives-status.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Extend `query_manager_decisions` so it also matches the `alternatives[]` array (and any status field), closing the documented recall gap where valid hits are missed.

## Manager's Notes

From the Brain self-improvement review (Task 190, live `brain_turn`), ranked R2. Proven live: a query for a term present only in `alternatives[]` misses, by design per the docstring. Change the design: alternatives are first-class searchable content.

## Local TODOs

- [x] Extend the query matcher to `alternatives[]` (and status field if present)
- [x] Update the tool docstring (remove the exclusion note)
- [x] Add regression test: term only in alternatives[] must hit
- [x] Verify full decision suite still green

## Acceptance Criteria

- [x] A keyword present only in `alternatives[]` returns the decision
- [x] Existing query behavior (summary/rationale/tradeoffs/quotes) unchanged
- [x] Docstring documents the full searched-field list

## Verification Evidence

- **Test command:** `uv run --project mcp-decision-server --with pytest --with pathspec pytest tests/test_decision_server.py -q`
- **Expected result:** all pass, including the new alternatives-hit test
- **Actual result:** `63 passed` (62 existing + new `test_query_hits_term_only_in_alternatives`), including honest red-green cycle (first assertion drafted against display text, corrected to match-behavior)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** More matches per query (slightly noisier results).
- **Rollback plan:** Revert the matcher diff; alternatives[] becomes invisible again.

---

## Execution Log & Reasoning

Implementation: `mcp-decision-server/server.py` `query_manager_decisions` haystack now joins `extracted.alternatives[]` (None-safe via `or []`, each item `str()`-coerced) alongside summary/rationale/tradeoffs/quotes; docstring updated to list alternatives. Schema has no status field (checked `decision.schema.json`), so the conditional "(and status field if present)" TODO is vacuous — noted, no code for a nonexistent field. Regression test `test_query_hits_term_only_in_alternatives` records a decision whose unique keyword lives only in alternatives[] and asserts the query returns that decision (red-green: first assertion targeted display text, corrected to match behavior). Full decision suite: 63 passed, exit 0. Existing query behavior unchanged (all 62 prior tests green untouched).

State-machine closure (goal: auto-close if brain APPROVED): fresh `brain_turn` QA (task_id 192, full file + complete diff pasted) returned **QA_PASSED** (F1 None-safe, F2 str-coerce, F3 wrong-type degraded-recall out-of-contract, F4 empty-query unchanged, F5 category untouched; A1–A3 non-blocking hardening notes; status handling honest). Reviewer `brain_turn` (retry once after an empty REPORT) returned **APPROVED → PO_REVIEW_PENDING** (S1–S3; I1/I2 doc/changelog hunks verified on disk: server.py:422 lists alternatives, CHANGELOG.md:16 carries the entry; I3 TODO ticks fixed at closure). Autoclosed under the goal authorization.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index f918a5d..d6ec760 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Fixed
 
+- **Decision query hits alternatives (Task 192):** `query_manager_decisions` haystack now includes `extracted.alternatives[]` (None-safe, str-coerced) alongside summary/rationale/tradeoffs/quotes — a keyword present only in alternatives returns the decision. Docstring lists the full searched-field list. Schema carries no status field, so no status matching was added. Regression test `test_query_hits_term_only_in_alternatives`. Decision suite: **63 passed**.
+
 - **Brain full-task-file access (Task 200):** `brain_turn` now auto-attaches the task file's working content (Goal/Notes/TODOs/AC/evidence/log minus the Factual Git Diff block, replaced by an omitted-note with line count + `read_file` pull path) on every call carrying a `task_id` — the Brain always sees the whole task file regardless of size; unresolvable ids never fail a turn. 6 new mocked tests (strip/resolve/fallback/unresolvable/attach/no-duplicate). Full suite: **207 passed**.
 
 - **Transport error taxonomy (Task 198):** Explicit retryable vs fatal sets in both servers' `_post_with_retry` (`_RETRYABLE_STATUS` 429/500/502/503/504 + timeouts/transport errors; `_FATAL_STATUS` 400/401/403/404/422 + other 4xx fail fast with a no-retry error naming status + path + snippet, never the key). 16 new per-class mocked tests (8 bridge + 8 decision: fatal-403/404/422 calls==1, retryable-429→200, timeout→200, message-contract, sleep-counter, non-httpx unwrap). Full suite: **201 passed**.
diff --git a/mcp-decision-server/server.py b/mcp-decision-server/server.py
index 2683b78..bd395ef 100644
--- a/mcp-decision-server/server.py
+++ b/mcp-decision-server/server.py
@@ -970,8 +970,9 @@ def query_manager_decisions(query: str, category: Optional[str] = None) -> str:
     process, scope, or quality gates.
 
     Case-insensitive substring match over summaries, rationales, trade-offs,
-    and both verbatim-quote languages. Returns formatted summaries with
-    verbatim quotes, or a no-match message (never an error) when empty.
+    alternatives, and both verbatim-quote languages. Returns formatted
+    summaries with verbatim quotes, or a no-match message (never an error)
+    when empty.
 
     Args:
         query: Keyword(s); blank returns everything in the category.
@@ -989,9 +990,11 @@ def query_manager_decisions(query: str, category: Optional[str] = None) -> str:
         if category and extracted.get("category") != category:
             continue
         quote = record.get("verbatim_quote", {})
+        alternatives = extracted.get("alternatives", []) or []
         haystack = " ".join([
             str(extracted.get("summary", "")), str(extracted.get("rationale", "")),
-            str(extracted.get("tradeoffs", "")), str(quote.get("original", "")),
+            str(extracted.get("tradeoffs", "")), " ".join(str(a) for a in alternatives),
+            str(quote.get("original", "")),
             str(quote.get("english_translation", "")),
         ]).lower()
         if needle and needle not in haystack:
diff --git a/tests/test_decision_server.py b/tests/test_decision_server.py
index 62187ac..c038de1 100644
--- a/tests/test_decision_server.py
+++ b/tests/test_decision_server.py
@@ -194,6 +194,24 @@ def test_query_keyword_and_category(srv, repo):
     assert "No manager decisions match" in target("zzz-no-such-thing")
 
 
+def test_query_hits_term_only_in_alternatives(srv, repo):
+    """Regression: a keyword present only in alternatives[] must hit."""
+    cand = _candidate()
+    cand["extracted_decision"] = {
+        "summary": "Adopt the new runner",
+        "category": "tooling",
+        "rationale": "Faster feedback on every push",
+        "alternatives": ["keep the legacy zebracorn runner"],
+        "tradeoffs": "Migration effort",
+    }
+    _record(srv.record_manager_decision, cand)
+    call = srv.query_manager_decisions
+    target = call.fn if hasattr(call, "fn") else call
+    found = target("zebracorn")
+    assert "No manager decisions match" not in found
+    assert "Adopt the new runner" in found
+
+
 def test_get_manager_profile_missing_and_present(srv, repo, monkeypatch):
     call = srv.get_manager_profile
     target = call.fn if hasattr(call, "fn") else call
```
<!-- END_GIT_DIFF -->
