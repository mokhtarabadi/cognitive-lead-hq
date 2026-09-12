# Task 195: Machine-readable QA verdicts plus rules-first checks

**File:** `tasks/qa/195-machine-verdicts-rules-first.md`
**Source:** manager
**Type:** feature
**Status:** open

## Goal

Make autopilot fully hands-free: QA verdicts return a strict machine-readable `QA_PASSED` / `QA_REJECTED` with file-and-line cites the autopilot parses without copy-paste, and cheap deterministic rule checks (schema, budget, allowlist) run before the LLM judge.

## Manager's Notes

From the Brain self-improvement review (Task 190, live `brain_turn`), ranked R5 (strict verdicts with cites) and R7 (rules before judge). Fixed rules catch clear faults in milliseconds and spare judge tokens; strict verdicts let the hotfix step start automatically.

## Local TODOs

- [x] Define the strict verdict format (`QA_PASSED` / `QA_REJECTED` + `file:line` cites) in the QA persona behavior (fragment 06)
- [x] Add a rules-first gate: schema, budget, and allowlist checks run before any LLM judge call
- [x] Mocked unit tests for the rules gate
- [x] Rebuild system prompt from fragments if 06 changes; verify sync byte-identical

## Acceptance Criteria

- [x] A QA reply parses to a verdict + cites with a single regex
- [x] Schema/budget/allowlist violations are caught without any LLM call
- [x] Prompt sync verified byte-identical after any fragment edit

## Verification Evidence

- **Test command:** `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check195.md && diff /tmp/check195.md system-prompt.md && echo SYNC_OK`
- **Expected result:** `SYNC_OK`, zero diff lines
- **Actual result:** `SYNC_OK`, zero diff lines (assembled 81285 bytes → `system-prompt.md`, re-assembled to `/tmp/check195.md`, `diff` empty)
- **Exit code:** `0` (exit codes: assemble 0, pytest 0)

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Over-strict verdict regex rejects valid human-worded verdicts — keep a documented escape hatch.
- **Rollback plan:** Revert the persona-behavior diff; verdicts return to prose.

---

## Execution Log & Reasoning

- Red-green: wrote `tests/test_rules_gate.py` first (13 tests), confirmed collection ERROR (`No module named 'rules_gate'`), then implemented `scripts/qa-rules-gate/rules_gate.py` → 13/13 green.
- Gate design: `parse_verdict` uses one compiled regex each for `VERDICT:` and `CITE:` lines; `run_gate` runs parse → schema → budget → allowlist and returns QA_REJECTED without touching `judge` on any violation (Mock asserted `assert_not_called`); clean payload calls judge exactly once, or returns the parsed verdict when no judge is given. Unparseable replies become QA_REJECTED with reason "unparseable verdict" (documented escape hatch: autopilot falls back to prose, manager may override).
- Fragment 06 QA persona gained the Machine-Readable Verdict Mandate + rules-first pointer + escape hatch; version bumped 9.27.0 → 9.28.0 per AGENTS.md (system-prompt.md is generated, so the version source is `01-system_version.md`).
- Rebuilt `system-prompt.md` via the assembler (81285 bytes), round-trip check `SYNC_OK` zero diff.
- Full suite `uv run --with pytest --with "mcp<2" --with pathspec --with pyyaml python -m pytest tests/` → **232 passed** (env note: system python has no pytest; `mcp` v2 removed FastMCP so suites need `mcp<2`; memory-server tests need pyyaml — all pre-existing env gaps, unrelated to this change).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index f918a5d..2c377d6 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,8 +6,14 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+### Added
+
+- **Machine-readable QA verdicts + rules-first gate (Task 195):** QA persona (fragment 06) now ends every report with a machine verdict block (`VERDICT: QA_PASSED` / `QA_REJECTED` + `CITE: file:line` lines, single-regex parseable) with a documented escape hatch (unparseable → QA_REJECTED with reason, prose fallback, manager override). New `scripts/qa-rules-gate/rules_gate.py` runs verdict-parse, schema, budget, and allowlist checks before any LLM judge call — rule failures return QA_REJECTED without invoking the judge (Mock-asserted). 13 new mocked tests. System version 9.27.0 → 9.28.0, `system-prompt.md` rebuilt (sync-check byte-identical). Full suite: **232 passed**.
+
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
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 1c77c89..2ff9e08 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.27.0</system_version>
+<system_version>9.28.0</system_version>
diff --git a/prompts/fragments/06-personas.md b/prompts/fragments/06-personas.md
index 737a0b4..6a92078 100644
--- a/prompts/fragments/06-personas.md
+++ b/prompts/fragments/06-personas.md
@@ -47,7 +47,7 @@
   <persona name="QA Engineer">
     <trigger>Implementation phase is complete, or explicit Manager request for testing.</trigger>
     <duty>Adversarial testing, boundary analysis, fuzzing, and stability enforcement.</duty>
-    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, Status (QA_PASSED or QA_REJECTED). If QA_REJECTED, do NOT stop at the verdict. The Manager ferries task files between the Hands and the Brain by hand, so always emit the next step yourself: first a 3-line Manager summary (what failed, what the fix covers, where to paste it), then a hotfix `<hands_implementation_task>` XML scoped ONLY to the failing points, instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs QA. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If QA_PASSED, instruct the Manager to hand over to the Code Reviewer.</behavior>
+    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, Status (QA_PASSED or QA_REJECTED). If QA_REJECTED, do NOT stop at the verdict. The Manager ferries task files between the Hands and the Brain by hand, so always emit the next step yourself: first a 3-line Manager summary (what failed, what the fix covers, where to paste it), then a hotfix `<hands_implementation_task>` XML scoped ONLY to the failing points, instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs QA. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If QA_PASSED, instruct the Manager to hand over to the Code Reviewer. **Machine-Readable Verdict Mandate:** End EVERY QA report with a machine verdict block the autopilot parses with a single regex — first line exactly `VERDICT: QA_PASSED` or `VERDICT: QA_REJECTED`, then one `CITE: file:line` line per cited location (e.g. `CITE: mcp-decision-server/server.py:123`). The prose report stays for humans; the verdict block drives automation. **Rules-First Gate:** Before any LLM judge call, the autopilot runs the deterministic rules gate (`scripts/qa-rules-gate/rules_gate.py`: verdict parse, schema, budget, allowlist) — any rule failure is QA_REJECTED without spending judge tokens. **Escape hatch:** If a reply carries no parseable VERDICT line, the autopilot treats it as QA_REJECTED with reason "unparseable verdict" and falls back to the prose report; the Manager may override any machine verdict by explicit order.</behavior>
 </persona>
 
   <persona name="Code Reviewer">
diff --git a/scripts/qa-rules-gate/rules_gate.py b/scripts/qa-rules-gate/rules_gate.py
new file mode 100644
index 0000000..7e773fc
--- /dev/null
+++ b/scripts/qa-rules-gate/rules_gate.py
@@ -0,0 +1,118 @@
+"""Rules-first QA gate (Task 195).
+
+Cheap deterministic checks — verdict parse, schema, budget, allowlist — run
+BEFORE any LLM judge call. If any rule fails, the gate returns QA_REJECTED
+without ever invoking the judge (saves judge tokens, fails in milliseconds).
+
+Machine verdict format (emitted by the QA persona, fragment 06-personas.md):
+
+    VERDICT: QA_PASSED
+    CITE: path/to/file.py:123
+
+Parsed with a single regex each; an unparseable reply raises
+UnparseableVerdict — the autopilot treats that as QA_REJECTED with reason
+"unparseable verdict" and falls back to the prose report (escape hatch).
+"""
+
+from __future__ import annotations
+
+import re
+from dataclasses import dataclass, field
+from pathlib import Path
+from typing import Callable
+
+_VERDICT_RE = re.compile(r"^VERDICT:\s*(QA_PASSED|QA_REJECTED)\s*$", re.MULTILINE)
+_CITE_RE = re.compile(r"^CITE:\s*(\S+):(\d+)\s*$", re.MULTILINE)
+
+
+class UnparseableVerdict(ValueError):
+    """Raised when a QA reply carries no machine-readable VERDICT line."""
+
+
+@dataclass(frozen=True)
+class GateResult:
+    verdict: str
+    violations: list = field(default_factory=list)
+    judge_called: bool = False
+
+
+def parse_verdict(reply: str) -> tuple[str, list[tuple[str, int]]]:
+    """Parse a QA reply into (verdict, [(file, line), ...]) with one regex each.
+
+    Raises:
+        UnparseableVerdict: if no VERDICT line is present.
+    """
+    match = _VERDICT_RE.search(reply)
+    if not match:
+        raise UnparseableVerdict(
+            "No machine-readable VERDICT line (expected "
+            "'VERDICT: QA_PASSED' or 'VERDICT: QA_REJECTED')."
+        )
+    cites = [(path, int(line)) for path, line in _CITE_RE.findall(reply)]
+    return match.group(1), cites
+
+
+def check_schema(record: dict, required: list[str]) -> list[str]:
+    """Missing required fields → one violation string each."""
+    return [f"missing field: {name}" for name in required if name not in record]
+
+
+def check_budget(used: int, limit: int) -> list[str]:
+    """Token/char budget overflow → a single violation string."""
+    if used > limit:
+        return [f"budget exceeded: used {used} > limit {limit}"]
+    return []
+
+
+def check_allowlist(paths: list[str], roots: list[str]) -> list[str]:
+    """Paths escaping every allowed root → one violation string each."""
+    violations = []
+    for path in paths:
+        if not any(
+            Path(path) == Path(root) or Path(root) in Path(path).parents
+            for root in roots
+        ):
+            violations.append(f"path outside allowlist: {path}")
+    return violations
+
+
+def run_gate(
+    payload: dict,
+    *,
+    required: list[str],
+    budget: tuple[int, int],
+    allowlist_roots: list[str],
+    judge: Callable[[], str] | None = None,
+) -> GateResult:
+    """Run rules first; call the LLM judge only if every rule passes.
+
+    Args:
+        payload: {"verdict_reply": str, "paths": [str], ...extra schema fields}.
+        required: required top-level payload keys (schema check).
+        budget: (used, limit) token/char budget.
+        allowlist_roots: allowed path roots for payload["paths"].
+        judge: optional zero-arg LLM-judge callable returning a verdict
+            string; NEVER called when any rule fails.
+
+    Returns:
+        GateResult with verdict QA_PASSED / QA_REJECTED, the violation list,
+        and whether the judge was called.
+    """
+    violations: list[str] = []
+    try:
+        verdict, _ = parse_verdict(payload.get("verdict_reply", ""))
+    except UnparseableVerdict as exc:
+        violations.append(f"unparseable verdict: {exc}")
+        verdict = "QA_REJECTED"
+    violations += check_schema(payload, required)
+    used, limit = budget
+    violations += check_budget(used, limit)
+    violations += check_allowlist(payload.get("paths", []), allowlist_roots)
+
+    if violations:
+        return GateResult(verdict="QA_REJECTED", violations=violations)
+    if judge is not None:
+        return GateResult(
+            verdict=judge(), violations=[], judge_called=True
+        )
+    return GateResult(verdict=verdict, violations=[])
diff --git a/system-prompt.md b/system-prompt.md
index e415e6a..46a7f42 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.27.0</system_version>
+<system_version>9.28.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -99,7 +99,7 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
   <persona name="QA Engineer">
     <trigger>Implementation phase is complete, or explicit Manager request for testing.</trigger>
     <duty>Adversarial testing, boundary analysis, fuzzing, and stability enforcement.</duty>
-    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, Status (QA_PASSED or QA_REJECTED). If QA_REJECTED, do NOT stop at the verdict. The Manager ferries task files between the Hands and the Brain by hand, so always emit the next step yourself: first a 3-line Manager summary (what failed, what the fix covers, where to paste it), then a hotfix `<hands_implementation_task>` XML scoped ONLY to the failing points, instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs QA. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If QA_PASSED, instruct the Manager to hand over to the Code Reviewer.</behavior>
+    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, Status (QA_PASSED or QA_REJECTED). If QA_REJECTED, do NOT stop at the verdict. The Manager ferries task files between the Hands and the Brain by hand, so always emit the next step yourself: first a 3-line Manager summary (what failed, what the fix covers, where to paste it), then a hotfix `<hands_implementation_task>` XML scoped ONLY to the failing points, instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs QA. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If QA_PASSED, instruct the Manager to hand over to the Code Reviewer. **Machine-Readable Verdict Mandate:** End EVERY QA report with a machine verdict block the autopilot parses with a single regex — first line exactly `VERDICT: QA_PASSED` or `VERDICT: QA_REJECTED`, then one `CITE: file:line` line per cited location (e.g. `CITE: mcp-decision-server/server.py:123`). The prose report stays for humans; the verdict block drives automation. **Rules-First Gate:** Before any LLM judge call, the autopilot runs the deterministic rules gate (`scripts/qa-rules-gate/rules_gate.py`: verdict parse, schema, budget, allowlist) — any rule failure is QA_REJECTED without spending judge tokens. **Escape hatch:** If a reply carries no parseable VERDICT line, the autopilot treats it as QA_REJECTED with reason "unparseable verdict" and falls back to the prose report; the Manager may override any machine verdict by explicit order.</behavior>
 </persona>
 
   <persona name="Code Reviewer">
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
diff --git a/tests/test_rules_gate.py b/tests/test_rules_gate.py
new file mode 100644
index 0000000..2ceb3d0
--- /dev/null
+++ b/tests/test_rules_gate.py
@@ -0,0 +1,129 @@
+"""Mocked unit tests for the rules-first QA gate (Task 195).
+
+The gate runs cheap deterministic checks (verdict parse, schema, budget,
+allowlist) BEFORE any LLM judge call. All tests are offline: the judge is a
+Mock, and the key assertion is that it is NEVER called when rules fail.
+
+Run: `pytest tests/test_rules_gate.py -v` (repo root).
+"""
+
+import sys
+from pathlib import Path
+from unittest.mock import Mock
+
+import pytest
+
+GATE_DIR = Path(__file__).parent.parent / "scripts" / "qa-rules-gate"
+sys.path.insert(0, str(GATE_DIR))
+
+from rules_gate import (  # noqa: E402
+    UnparseableVerdict,
+    check_allowlist,
+    check_budget,
+    check_schema,
+    parse_verdict,
+    run_gate,
+)
+
+PASSED_REPLY = """Vulnerabilities: none found.
+Missing Tests: none.
+Status: QA_PASSED (prose mirror of the machine verdict below).
+VERDICT: QA_PASSED
+CITE: mcp-decision-server/server.py:123
+CITE: tests/test_rules_gate.py:45
+"""
+
+REJECTED_REPLY = """Vulnerabilities: missing null check.
+VERDICT: QA_REJECTED
+CITE: mcp-decision-server/server.py:999
+"""
+
+
+def test_parse_valid_passed_with_cites():
+    verdict, cites = parse_verdict(PASSED_REPLY)
+    assert verdict == "QA_PASSED"
+    assert cites == [
+        ("mcp-decision-server/server.py", 123),
+        ("tests/test_rules_gate.py", 45),
+    ]
+
+
+def test_parse_valid_rejected():
+    verdict, cites = parse_verdict(REJECTED_REPLY)
+    assert verdict == "QA_REJECTED"
+    assert cites == [("mcp-decision-server/server.py", 999)]
+
+
+def test_parse_missing_verdict_raises():
+    with pytest.raises(UnparseableVerdict):
+        parse_verdict("Looks fine to me, ship it.\nNo machine verdict here.")
+
+
+def test_parse_verdict_found_among_prose():
+    verdict, _ = parse_verdict("Some long prose...\nVERDICT: QA_PASSED\nMore prose...")
+    assert verdict == "QA_PASSED"
+
+
+def test_schema_missing_field():
+    violations = check_schema({"a": 1}, required=["a", "b"])
+    assert violations == ["missing field: b"]
+
+
+def test_schema_clean():
+    assert check_schema({"a": 1, "b": 2}, required=["a", "b"]) == []
+
+
+def test_budget_exceeded():
+    assert check_budget(used=120_000, limit=100_000) != []
+
+
+def test_budget_ok():
+    assert check_budget(used=50_000, limit=100_000) == []
+
+
+def test_allowlist_outside():
+    violations = check_allowlist(["/etc/passwd"], roots=["/repo"])
+    assert violations == ["path outside allowlist: /etc/passwd"]
+
+
+def test_allowlist_inside():
+    assert check_allowlist(["/repo/a.py"], roots=["/repo"]) == []
+
+
+def test_gate_rules_fail_never_calls_judge():
+    judge = Mock(return_value="QA_PASSED")
+    result = run_gate(
+        {"verdict_reply": REJECTED_REPLY, "paths": ["/etc/passwd"]},
+        required=[],
+        budget=(0, 1_000_000),
+        allowlist_roots=["/repo"],
+        judge=judge,
+    )
+    assert result.verdict == "QA_REJECTED"
+    assert result.violations != []
+    judge.assert_not_called()
+
+
+def test_gate_clean_calls_judge_once():
+    judge = Mock(return_value="QA_PASSED")
+    result = run_gate(
+        {"verdict_reply": PASSED_REPLY, "paths": ["/repo/a.py"]},
+        required=[],
+        budget=(10, 1_000_000),
+        allowlist_roots=["/repo"],
+        judge=judge,
+    )
+    assert result.verdict == "QA_PASSED"
+    assert result.violations == []
+    judge.assert_called_once()
+
+
+def test_gate_clean_no_judge_passes():
+    result = run_gate(
+        {"verdict_reply": PASSED_REPLY, "paths": []},
+        required=[],
+        budget=(0, 1_000_000),
+        allowlist_roots=["/repo"],
+    )
+    assert result.verdict == "QA_PASSED"
+    assert result.judge_called is False
```
<!-- END_GIT_DIFF -->
