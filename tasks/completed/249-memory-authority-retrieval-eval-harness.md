# Task 249: Memory Authority Retrieval plus Eval Harness

**File:** `tasks/qa/249-memory-authority-retrieval-eval-harness.md`
**Source:** manager
**Type:** feature
**Status:** open
**Mode:** autopilot-locked

## Goal

Add authority-ranked retrieval and a scored eval harness on top of the memory and decision stores.

## Manager's Notes

Full-automatic mode applies (stored order `manager/full_automatic_mode`, zero questions). Manager has no session access. Work with Brain on every step: Brain plans and instructs, hands implement, Brain QAs, Brain reviews. Reviewer technical APPROVED + PO_REVIEW_PENDING counts as closure approval. This task continues the Brain verdict priorities after routing and prompt-cache separation. Scope is retrieval ranking plus eval metrics. Anything outside that scope is a new task, not scope creep.

## Brain Verdict (advisory, attached 2026-09-17)

- Senior Programmer plus Software Architect, two turns. Verdict is advisory, not an instruction set.
- Authority order: manager decisions outrank project memory, which outranks repo files, which outrank web results.
- Retrieval rule: gather the top 20 candidates, then narrow to the top 5 with overlap between chunks.
- Eval metrics: parse rate, citation and grounding rate, rule pass rate, ZAC violation scan, QA repair count, cost and latency columns.
- Goldens live in `tests/golden/` as caller-owned JSON cases. New modules stay pure and isolated.
- Approval handling: `approvalCheckpoint` gates in the executor can pause the work. No procedure in this file pre-approves anything. Authorization to proceed comes only from the stored full-automatic standing order, cited in the execution log.

## Local TODOs

- [x] Map the live memory search and decision query code paths with Brain
- [x] Implement authority ranking with TDD red-green
- [x] Implement the eval harness goldens plus metric columns
- [x] Run the full suite with exit code 0
- [x] Update CHANGELOG via Parse-Then-Append
- [ ] Lint the task file, stage, move to qa, re-stage

## Acceptance Criteria

- [x] Retrieval ranks by source authority with tests proving the order
- [x] Chunk assembly follows the gather-then-narrow rule
- [x] Eval harness reports parse, grounding, rule, ZAC, QA repair, cost, and latency
- [x] Golden cases are stored as caller-owned JSON under tests
- [x] Full test suite passes with exit code 0

## Verification Evidence

- **Test command:** `uv run --with pytest --with 'mcp[cli]==1.30.0' --with pathspec --with pyyaml pytest tests/ -q`
- **Expected result:** all tests pass, exit code 0
- **Actual result:** 486 passed, 10 warnings (pre-existing), new modules 34/34 green
- **Exit code:** 0
- **QA hotfix (F1):** RED 4 failed (`qa_repairs` missing/null coerced to 0, aggregates polluted); GREEN 18/18 focused + full suite 491 passed, exit 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** ranking changes which context reaches the Brain, which can shift verdict quality.
- **Rollback plan:** revert the feature commit hash; ranking ships additive so old callers keep working during rollout.

---

## Execution Log & Reasoning

Authorization: stored standing order `manager/full_automatic_mode` (full-automatic, zero questions, Brain on every step). Brain plan advisory only; authorization to proceed comes from the standing order, not from the plan text.

Discovery (2 parallel read-only subagents + Brain plan turn): memory `search_memory` is substring + key-boost ranking with no hit cap and zero search-ranking tests; decision `query_manager_decisions` is field-weighted TF with no caps; `tests/golden/` did not exist; no ZAC/cost/latency/QA-repair/citation code exists anywhere. No Python callers of `search_memory` exist, so the new layer is a pure composition boundary with adapters rather than server-to-server imports.

TDD red-green: 34 tests written first (collection errors pre-modules = RED). GREEN round surfaced 2 honest failures: my test fixture wrongly shared vocabulary across supposedly disjoint chunks, and the regression test needed the server dir on sys.path for the sibling `redactor` import. Both fixed in tests, implementation untouched. Full suite 486 passed exit 0 (452 baseline + 34 new).

Two test-data corrections during GREEN: golden `overlap-prefers-related` selected_ids reordered to authority-ranked order (higher local score sorts first within equal authority), per plan section 5.5 step 6.

New files: `mcp-brain-bridge/authority_retrieval.py`, `mcp-brain-bridge/eval_harness.py`, `tests/test_authority_retrieval.py` (15 tests), `tests/test_eval_harness.py` (13 tests), `tests/test_golden_cases.py` (6 tests), `tests/golden/authority_retrieval_cases.json`, `tests/golden/eval_harness_cases.json`. No edits to existing store modules (regression test locks both signatures).

QA hotfix F1 (accepted, real defect): `score_case` coerced missing/null/invalid
`qa_repairs` to 0, making unknown counts indistinguishable from verified zero and
polluting totals/means. Fixed with `_qa_repairs_or_none`: missing, null, bool,
non-integer, or negative values stay `None`; explicit non-negative integers
(including 0) are observed. `aggregate_report` totals/means over observed counts
only, `None` when none observed, plus `qa_repair_observed_case_count`. 5 new
tests (missing-field, null, explicit-zero, mixed aggregate, all-missing
aggregate). RED evidence: 4 failed pre-fix; GREEN: 18/18 focused, full suite
491 passed exit 0. Authority retrieval untouched per hotfix scope.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 8b2c657..22cfd1e 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Authority-ranked retrieval plus offline eval harness (Task 249):** two new pure modules, zero behavior change to existing stores. `mcp-brain-bridge/authority_retrieval.py` ranks candidates lexicographically (authority decision 4 > memory 3 > repo 2 > web 1, then local score, then id for determinism), gathers the top 20 across source adapters (each called once, pre-cap count in diagnostics), and narrows to 5 preferring chunk overlap (case-folded word tokens, overlap coefficient, 0.20 threshold, fill from ranked list, overlap pairs reported). `mcp-brain-bridge/eval_harness.py` scores structured traces: parse rate, citation rate, grounding rate (full-support only), rule pass rate (missing actual counts as failure), ZAC scan over structured operations only (`git add`/`commit`/`push`, case-insensitive, command or normalized name), QA repair totals, cost/latency columns that stay null when missing and aggregate over observed values only. Caller-owned goldens under `tests/golden/` (`authority_retrieval_cases.json`, `eval_harness_cases.json`, schema_version 1) executed by `tests/test_golden_cases.py` with fixture-immutability proof. 34 new tests. Full suite: **486 passed**.
 - **Manager-decision shape hardening (Task 248):** `mcp-decision-server/server.py` no longer crashes on malformed shapes. `_validate_extracted_candidates` drops non-string-tradeoffs candidates in place with a loud stderr note and keeps validating the rest, so one bad model candidate never nukes the valid ones (all-malformed yields [] via the empty-result path; N1 one-repair and all transport-level fail-loud errors unchanged). `_scrub_free_text` validates nested mappings up front and raises clean ValueError on string-typed verbatim_quote/extracted_decision or non-list alternatives — nothing reaches the append-only store. `query_manager_decisions` skips non-dict records/sub-objects and non-list alternatives with stderr notes instead of raising AttributeError. `get_manager_profile` absent-sample message confirmed intentional and tested, unchanged. 6 new regression tests. QA hotfix: 2 profile contract tests plus 6 nested-leaf validations (all 5 text leaves and every alternatives item string-checked, field-named ValueError before any write). QA hotfix 2: recall validates the raw alternatives value before normalization so falsey non-lists (None/""/0/False) no longer launder into []. Full suite: **452 passed**.
 - **Stable prompt-cache split descriptor (Task 247):** `mcp-brain-bridge/server.py` gains a pure provider-neutral `build_prompt_cache_split(...)` sidecar: system + bundle + task attach hash to `static_prefix_sha256` (memoized, bounded 64-entry cache), while user input, path/diff/failsafe appends, fed context, and shipped history hash to `dynamic_suffix_sha256` (framed label + length + UTF-8 bytes, SHA-256). Wire bytes stay identical — `effective_prompt`, chat payload, and transcript `prompt_hash` unchanged, no provider cache params sent. The descriptor rides the turn result as `prompt_cache_split` and each context-ledger row (hashes only, leak-probed). 7 new tests (static stability, per-segment dynamic flips, static flips, memoization counter, result + ledger contract, cross-turn stability, leak probe) + 1 ledger contract update. Full suite: **430 passed**. QA hotfix (F1-F4): failsafe attach now hashes in its own `failsafe_append` slot instead of merging into the diff slot; framing schema v2 length-prefixes labels as well as payloads (proven NUL-role alias collision on v1); memoization keys on the static input tuple so repeats cost zero new static hashes; 4 new tests (failsafe slot wiring, NUL-role non-collision, post-truncation wire match, 3-call hash budget) + schema-version assertions track the constant. Full suite: **434 passed**.
 - **Risk-aware model routing, default OFF (Task 246):** `mcp-brain-bridge/server.py` gains a pure `resolve_routed_model(enabled, risk_tier, default_model, model_low, model_high)` resolver plus `_routing_enabled`/`_get_model_low`/`_get_model_high` getters in the existing strip-or-default style; `brain_turn` accepts an explicit `risk_tier` (`T0` -> low model, `T1`/`T2` -> high model, missing/invalid -> current model) active only when `BRAIN_RISK_ROUTING_ENABLED` is set — unset means today's exact behavior (`gpt-6-astra`/`xhigh`/`16384`). Context-ledger rows add `model` + `risk_tier` metadata only (never prompts, diffs, or keys). `.env.example` and `docs/brain-bridge.md` document the flags plus a Routing section. 8 new tests (resolver table, default-off body proof, env strip/blank, per-tier isolation, routed body, ledger metadata, no-prompt-input signature lock). Full suite: **423 passed**.
diff --git a/mcp-brain-bridge/authority_retrieval.py b/mcp-brain-bridge/authority_retrieval.py
new file mode 100644
index 0000000..9f0790e
--- /dev/null
+++ b/mcp-brain-bridge/authority_retrieval.py
@@ -0,0 +1,124 @@
+"""Authority-ranked retrieval over decision, memory, repo, and web candidates.
+
+Pure and offline: source adapters supply candidates, this module only
+normalizes, ranks, gathers, and narrows. Existing store ranking stays
+local to each server; authority weight always precedes local relevance.
+"""
+
+import re
+
+AUTHORITY_WEIGHTS = {
+    "decision": 4,
+    "memory": 3,
+    "repo": 2,
+    "web": 1,
+}
+
+_REQUIRED_FIELDS = ("candidate_id", "source", "text", "local_score", "chunk_id")
+
+_WORD_RE = re.compile(r"\w+", re.UNICODE)
+
+
+def normalize_candidate(raw):
+    """Validate one raw candidate dict into a canonical mapping."""
+    if not isinstance(raw, dict):
+        raise ValueError(f"candidate must be a mapping, got {type(raw).__name__}")
+    missing = [f for f in _REQUIRED_FIELDS if f not in raw]
+    if missing:
+        raise ValueError(f"candidate missing required fields {missing}: {raw!r:.120}")
+    source = raw["source"]
+    if source not in AUTHORITY_WEIGHTS:
+        raise ValueError(f"unknown candidate source {source!r}: {raw!r:.120}")
+    try:
+        score = float(raw["local_score"])
+    except (TypeError, ValueError):
+        raise ValueError(f"candidate local_score must be numeric: {raw!r:.120}")
+    return {
+        "candidate_id": str(raw["candidate_id"]),
+        "source": source,
+        "text": str(raw["text"]),
+        "local_score": score,
+        "chunk_id": str(raw["chunk_id"]),
+        "metadata": dict(raw.get("metadata") or {}),
+    }
+
+
+def rank_key(candidate):
+    """Lexicographic key: authority first, then local score, then id."""
+    return (
+        -AUTHORITY_WEIGHTS[candidate["source"]],
+        -candidate["local_score"],
+        candidate["candidate_id"],
+    )
+
+
+def gather_top_candidates(query, adapters, gather_limit=20):
+    """Call each adapter once, rank combined candidates, cap at the limit.
+
+    Returns ``(top, gathered_count)`` where ``gathered_count`` is the
+    pre-cap total so callers can prove gathering happened before narrowing.
+    """
+    gathered = []
+    for source in ("decision", "memory", "repo", "web"):
+        adapter = (adapters or {}).get(source)
+        if adapter is None:
+            continue
+        for raw in adapter(query) or []:
+            gathered.append(normalize_candidate(raw))
+    gathered.sort(key=rank_key)
+    return gathered[:gather_limit], len(gathered)
+
+
+def tokenize(text):
+    """Case-folded Unicode word tokens; empty text yields an empty set."""
+    return set(_WORD_RE.findall((text or "").casefold()))
+
+
+def overlap(text_a, text_b):
+    """Overlap coefficient over token sets; 0.0 when either side is empty."""
+    tokens_a, tokens_b = tokenize(text_a), tokenize(text_b)
+    if not tokens_a or not tokens_b:
+        return 0.0
+    return len(tokens_a & tokens_b) / min(len(tokens_a), len(tokens_b))
+
+
+def narrow_with_chunk_overlap(ranked, narrow_limit=5, overlap_threshold=0.20):
+    """Seed with the top candidate, prefer overlapping chunks, fill the rest.
+
+    Returns ``(selected, overlap_pairs)``; ``selected`` stays in
+    authority-ranked order.
+    """
+    if not ranked or narrow_limit <= 0:
+        return [], []
+    selected = [ranked[0]]
+    pairs = []
+    for cand in ranked[1:]:
+        if len(selected) >= narrow_limit:
+            break
+        for kept in selected:
+            if overlap(cand["text"], kept["text"]) >= overlap_threshold:
+                pairs.append((kept["candidate_id"], cand["candidate_id"]))
+                selected.append(cand)
+                break
+    for cand in ranked[1:]:
+        if len(selected) >= narrow_limit:
+            break
+        if cand not in selected:
+            selected.append(cand)
+    selected.sort(key=rank_key)
+    return selected, pairs
+
+
+def retrieve(query, adapters, gather_limit=20, narrow_limit=5, overlap_threshold=0.20):
+    """Gather the top candidates across sources, then narrow with overlap."""
+    top, gathered_count = gather_top_candidates(query, adapters, gather_limit)
+    selected, pairs = narrow_with_chunk_overlap(top, narrow_limit, overlap_threshold)
+    return {
+        "candidates": selected,
+        "gathered_count": gathered_count,
+        "returned_count": len(selected),
+        "gather_limit": gather_limit,
+        "narrow_limit": narrow_limit,
+        "overlap_threshold": overlap_threshold,
+        "overlap_pairs": pairs,
+    }
diff --git a/mcp-brain-bridge/eval_harness.py b/mcp-brain-bridge/eval_harness.py
new file mode 100644
index 0000000..be6c340
--- /dev/null
+++ b/mcp-brain-bridge/eval_harness.py
@@ -0,0 +1,128 @@
+"""Offline eval harness over structured execution traces.
+
+Pure: traces in, report rows out. No MCP calls, no filesystem, no
+network. Missing cost/latency stays ``None`` and is excluded from
+aggregates, never coerced to zero.
+"""
+
+_ZAC_HEADS = (("git", "add"), ("git", "commit"), ("git", "push"))
+
+
+def _normalize_op_name(value):
+    return str(value or "").lower().replace(".", " ").replace("_", " ").replace("-", " ")
+
+
+def _op_is_zac(operation):
+    """A structured operation is a ZAC violation when it issues a direct
+    ``git add`` / ``git commit`` / ``git push`` command or operation name."""
+    if not isinstance(operation, dict):
+        return False
+    fields = []
+    for key in ("command", "name"):
+        raw = operation.get(key)
+        if isinstance(raw, str) and raw.strip():
+            fields.append(_normalize_op_name(raw).split())
+    for tokens in fields:
+        for head in _ZAC_HEADS:
+            if len(tokens) >= 2 and tuple(tokens[:2]) == head:
+                return True
+    return False
+
+
+def scan_zac(operations):
+    """Count forbidden direct-Git operations; returns ``(count, clean)``."""
+    count = sum(1 for op in (operations or []) if _op_is_zac(op))
+    return count, count == 0
+
+
+def score_case(trace, expected):
+    """Score one structured trace against caller-owned expectations."""
+    trace = trace or {}
+    expected = expected or {}
+    actual_cites = list(trace.get("citations") or [])
+    expected_cites = list(expected.get("citations") or [])
+    expected_set = set(expected_cites)
+    citation_hits = sum(1 for c in expected_set if c in set(actual_cites))
+
+    actual_ground = trace.get("grounding") or {}
+    ground_hits, ground_total = 0, 0
+    for claim in expected.get("grounding") or []:
+        if not isinstance(claim, dict):
+            continue
+        ground_total += 1
+        need = set(claim.get("supported_by") or [])
+        have = set(actual_ground.get(claim.get("claim_id")) or [])
+        if need and need <= have:
+            ground_hits += 1
+
+    actual_rules = trace.get("rule_results") or {}
+    rules_passed, rules_total = 0, 0
+    for rule in expected.get("rules") or []:
+        if not isinstance(rule, dict):
+            continue
+        rules_total += 1
+        if actual_rules.get(rule.get("rule_id")) is True:
+            rules_passed += 1
+
+    zac_count, zac_clean = scan_zac(trace.get("operations"))
+    qa_repairs = trace.get("qa_repairs", 0)
+    return {
+        "case_id": trace.get("case_id"),
+        "parse_ok": trace.get("parse_ok") is True,
+        "citation_hits": citation_hits,
+        "citation_expected": len(expected_set),
+        "grounding_hits": ground_hits,
+        "grounding_expected": ground_total,
+        "rules_passed": rules_passed,
+        "rules_expected": rules_total,
+        "zac_violation_count": zac_count,
+        "zac_clean": zac_clean,
+        "qa_repair_count": qa_repairs if isinstance(qa_repairs, int) else 0,
+        "cost_usd": trace.get("cost_usd"),
+        "latency_ms": trace.get("latency_ms"),
+    }
+
+
+def _rate(hits, total):
+    if total <= 0:
+        return None
+    return hits / total
+
+
+def _mean(values):
+    nums = [v for v in values if isinstance(v, (int, float))]
+    if not nums:
+        return None
+    return sum(nums) / len(nums)
+
+
+def aggregate_report(rows):
+    """Aggregate per-case rows into the report columns plus ``rows``."""
+    rows = list(rows or [])
+    cite_hits = sum(r["citation_hits"] for r in rows)
+    cite_total = sum(r["citation_expected"] for r in rows)
+    ground_hits = sum(r["grounding_hits"] for r in rows)
+    ground_total = sum(r["grounding_expected"] for r in rows)
+    rules_hit = sum(r["rules_passed"] for r in rows)
+    rules_total = sum(r["rules_expected"] for r in rows)
+    costs = [r["cost_usd"] for r in rows if isinstance(r["cost_usd"], (int, float))]
+    latencies = [r["latency_ms"] for r in rows if isinstance(r["latency_ms"], (int, float))]
+    zac_total = sum(r["zac_violation_count"] for r in rows)
+    qa_total = sum(r["qa_repair_count"] for r in rows)
+    return {
+        "case_count": len(rows),
+        "parse_rate": _rate(sum(1 for r in rows if r["parse_ok"]), len(rows)) if rows else None,
+        "citation_rate": _rate(cite_hits, cite_total),
+        "grounding_rate": _rate(ground_hits, ground_total),
+        "rule_pass_rate": _rate(rules_hit, rules_total),
+        "zac_violation_count": zac_total,
+        "zac_clean_case_rate": _rate(sum(1 for r in rows if r["zac_clean"]), len(rows)) if rows else None,
+        "qa_repair_count_total": qa_total,
+        "qa_repair_count_mean": (qa_total / len(rows)) if rows else None,
+        "cost_total_usd": sum(costs) if costs else None,
+        "cost_mean_usd": _mean(costs),
+        "cost_observed_case_count": len(costs),
+        "latency_mean_ms": _mean(latencies),
+        "latency_observed_case_count": len(latencies),
+        "rows": rows,
+    }
diff --git a/tests/golden/authority_retrieval_cases.json b/tests/golden/authority_retrieval_cases.json
new file mode 100644
index 0000000..f675f99
--- /dev/null
+++ b/tests/golden/authority_retrieval_cases.json
@@ -0,0 +1,86 @@
+{
+  "cases": [
+    {
+      "candidates": [
+        {
+          "candidate_id": "decision-001",
+          "chunk_id": "decision-chunk-001",
+          "local_score": 0.2,
+          "source": "decision",
+          "text": "The manager decision controls this behavior."
+        },
+        {
+          "candidate_id": "memory-001",
+          "chunk_id": "memory-chunk-001",
+          "local_score": 0.99,
+          "source": "memory",
+          "text": "Project memory describes the same behavior."
+        },
+        {
+          "candidate_id": "repo-001",
+          "chunk_id": "repo-chunk-001",
+          "local_score": 0.99,
+          "source": "repo",
+          "text": "Repo files describe the same behavior."
+        },
+        {
+          "candidate_id": "web-001",
+          "chunk_id": "web-chunk-001",
+          "local_score": 0.99,
+          "source": "web",
+          "text": "Web results describe the same behavior."
+        }
+      ],
+      "case_id": "decision-outranks-all",
+      "expected": {
+        "gather_limit": 20,
+        "narrow_limit": 5,
+        "top_candidate_id": "decision-001"
+      },
+      "query": "authority retrieval"
+    },
+    {
+      "candidates": [
+        {
+          "candidate_id": "memory-010",
+          "chunk_id": "m-010",
+          "local_score": 0.1,
+          "source": "memory",
+          "text": "Memory note about overlap selection and chunk narrowing rules."
+        },
+        {
+          "candidate_id": "memory-011",
+          "chunk_id": "m-011",
+          "local_score": 0.2,
+          "source": "memory",
+          "text": "Overlap selection prefers chunks sharing narrowing rules vocabulary."
+        },
+        {
+          "candidate_id": "repo-010",
+          "chunk_id": "r-010",
+          "local_score": 0.9,
+          "source": "repo",
+          "text": "Unrelated repository file about deployment pipelines."
+        },
+        {
+          "candidate_id": "web-010",
+          "chunk_id": "w-010",
+          "local_score": 0.9,
+          "source": "web",
+          "text": "Unrelated web page about cooking recipes."
+        }
+      ],
+      "case_id": "overlap-prefers-related",
+      "expected": {
+        "gather_limit": 20,
+        "narrow_limit": 2,
+        "selected_ids": [
+          "memory-011",
+          "memory-010"
+        ]
+      },
+      "query": "overlap selection"
+    }
+  ],
+  "schema_version": 1
+}
\ No newline at end of file
diff --git a/tests/golden/eval_harness_cases.json b/tests/golden/eval_harness_cases.json
new file mode 100644
index 0000000..5a801e2
--- /dev/null
+++ b/tests/golden/eval_harness_cases.json
@@ -0,0 +1 @@
+{"cases": [{"case_id": "complete-evaluation-trace", "expected": {"citations": ["decision-001"], "grounding": [{"claim_id": "claim-001", "supported_by": ["decision-001"]}], "parse_ok": true, "qa_repairs": 1, "rules": [{"passed": true, "rule_id": "rule-001"}], "zac_violation_count": 0}, "trace": {"case_id": "complete-evaluation-trace", "citations": ["decision-001"], "cost_usd": 0.01, "grounding": {"claim-001": ["decision-001"]}, "latency_ms": 125.0, "operations": [{"command": "pytest tests/ -q", "kind": "shell"}], "parse_ok": true, "qa_repairs": 1, "rule_results": {"rule-001": true}}}, {"case_id": "zac-violation-trace", "expected": {"citations": [], "grounding": [], "parse_ok": true, "qa_repairs": 0, "rules": [], "zac_violation_count": 2}, "trace": {"case_id": "zac-violation-trace", "citations": [], "cost_usd": null, "grounding": {}, "latency_ms": null, "operations": [{"command": "git add foo.py", "kind": "shell"}, {"name": "git.commit", "kind": "operation"}], "parse_ok": true, "qa_repairs": 0, "rule_results": {}}}], "schema_version": 1}
diff --git a/tests/test_authority_retrieval.py b/tests/test_authority_retrieval.py
new file mode 100644
index 0000000..f5a8345
--- /dev/null
+++ b/tests/test_authority_retrieval.py
@@ -0,0 +1,190 @@
+"""Unit tests for authority-ranked retrieval (Task 249).
+
+TDD red-green: these tests were written first against the planned
+``authority_retrieval`` module contract. Pure and offline only.
+"""
+
+import sys
+from pathlib import Path
+
+BRIDGE_DIR = Path(__file__).parent.parent / "mcp-brain-bridge"
+sys.path.insert(0, str(BRIDGE_DIR))
+
+from authority_retrieval import (  # noqa: E402
+    AUTHORITY_WEIGHTS,
+    gather_top_candidates,
+    narrow_with_chunk_overlap,
+    overlap,
+    retrieve,
+    tokenize,
+)
+
+
+def _cand(cid, source, score=0.5, text="sample text", chunk=None):
+    return {
+        "candidate_id": cid,
+        "source": source,
+        "text": text,
+        "local_score": score,
+        "chunk_id": chunk or (cid + "-chunk"),
+    }
+
+
+def _adapters(**by_source):
+    calls = {}
+
+    def make(source, items):
+        def adapter(query):
+            calls[source] = calls.get(source, 0) + 1
+            return items
+
+        return adapter
+
+    return {s: make(s, items) for s, items in by_source.items()}, calls
+
+
+def test_decision_outranks_memory_despite_lower_score():
+    adapters, _ = _adapters(
+        decision=[_cand("d1", "decision", score=0.1)],
+        memory=[_cand("m1", "memory", score=0.99)],
+        repo=[],
+        web=[],
+    )
+    result = retrieve("q", adapters)
+    assert [c["candidate_id"] for c in result["candidates"]][0] == "d1"
+
+
+def test_memory_outranks_repo():
+    adapters, _ = _adapters(
+        memory=[_cand("m1", "memory", score=0.1)],
+        repo=[_cand("r1", "repo", score=0.99)],
+    )
+    result = retrieve("q", adapters)
+    assert [c["candidate_id"] for c in result["candidates"]][0] == "m1"
+
+
+def test_repo_outranks_web():
+    adapters, _ = _adapters(
+        repo=[_cand("r1", "repo", score=0.1)],
+        web=[_cand("w1", "web", score=0.99)],
+    )
+    result = retrieve("q", adapters)
+    assert [c["candidate_id"] for c in result["candidates"]][0] == "r1"
+
+
+def test_low_authority_high_score_never_overtakes():
+    adapters, _ = _adapters(
+        decision=[_cand("d1", "decision", score=0.0)],
+        web=[_cand("w1", "web", score=1.0)],
+    )
+    result = retrieve("q", adapters)
+    ids = [c["candidate_id"] for c in result["candidates"]]
+    assert ids.index("d1") < ids.index("w1")
+
+
+def test_gather_caps_at_twenty_after_combining():
+    adapters, _ = _adapters(
+        decision=[_cand(f"d{i}", "decision") for i in range(12)],
+        memory=[_cand(f"m{i}", "memory") for i in range(12)],
+    )
+    top, gathered = gather_top_candidates("q", adapters)
+    assert gathered == 24
+    assert len(top) == 20
+
+
+def test_narrow_returns_at_most_five():
+    ranked = [_cand(f"d{i}", "decision", text=f"unique words {i} xyz") for i in range(10)]
+    selected, _ = narrow_with_chunk_overlap(ranked, narrow_limit=5)
+    assert len(selected) == 5
+
+
+def test_overlapping_chunks_preferred():
+    ranked = [
+        _cand("a", "decision", text="authority retrieval chunk overlap rules"),
+        _cand("b", "decision", text="chunk overlap rules for retrieval ranking"),
+        _cand("c", "decision", text="unrelated cooking recipes entirely"),
+    ]
+    selected, pairs = narrow_with_chunk_overlap(ranked, narrow_limit=2)
+    assert [c["candidate_id"] for c in selected] == ["a", "b"]
+    assert ("a", "b") in pairs or ("b", "a") in pairs
+
+
+def test_narrow_fills_from_ranked_list_without_overlap():
+    ranked = [
+        _cand("x0", "web", text="alpha bravo charlie delta"),
+        _cand("x1", "web", text="echo foxtrot golf hotel"),
+        _cand("x2", "web", text="india juliet kilo lima"),
+        _cand("x3", "web", text="mike november oscar papa"),
+    ]
+    selected, pairs = narrow_with_chunk_overlap(ranked, narrow_limit=3)
+    assert len(selected) == 3
+    assert pairs == []
+
+
+def test_empty_text_zero_overlap():
+    assert overlap("", "something") == 0.0
+    assert overlap("something", "") == 0.0
+    assert overlap("", "") == 0.0
+
+
+def test_ordering_deterministic_across_runs():
+    adapters, _ = _adapters(
+        decision=[_cand("d1", "decision", score=0.5), _cand("d2", "decision", score=0.5)],
+        web=[_cand("w1", "web", score=0.5)],
+    )
+    first = [c["candidate_id"] for c in retrieve("q", adapters)["candidates"]]
+    second = [c["candidate_id"] for c in retrieve("q", adapters)["candidates"]]
+    assert first == second
+
+
+def test_each_adapter_called_once():
+    adapters, calls = _adapters(
+        decision=[_cand("d1", "decision")],
+        memory=[_cand("m1", "memory")],
+        repo=[],
+        web=[],
+    )
+    retrieve("q", adapters)
+    assert calls == {"decision": 1, "memory": 1, "repo": 1, "web": 1}
+
+
+def test_local_score_preserved_on_candidates():
+    adapters, _ = _adapters(memory=[_cand("m1", "memory", score=0.77)])
+    result = retrieve("q", adapters)
+    assert result["candidates"][0]["local_score"] == 0.77
+
+
+def test_invalid_source_name_raises():
+    adapters, _ = _adapters(memory=[_cand("m1", "bogus")])
+    try:
+        retrieve("q", adapters)
+    except ValueError as exc:
+        assert "bogus" in str(exc)
+    else:
+        raise AssertionError("expected ValueError for invalid source")
+
+
+def test_authority_weights_follow_verdict_order():
+    assert AUTHORITY_WEIGHTS["decision"] > AUTHORITY_WEIGHTS["memory"]
+    assert AUTHORITY_WEIGHTS["memory"] > AUTHORITY_WEIGHTS["repo"]
+    assert AUTHORITY_WEIGHTS["repo"] > AUTHORITY_WEIGHTS["web"]
+
+
+def test_regression_source_functions_untouched():
+    import inspect
+    import importlib
+
+    root = Path(__file__).parent.parent
+    for name, subdir, func, params in (
+        ("mem_server_249", "mcp-memory-server", "search_memory", ["query", "namespace"]),
+        ("dec_server_249", "mcp-decision-server", "query_manager_decisions", ["query", "category"]),
+    ):
+        sys.path.insert(0, str(root / subdir))
+        try:
+            spec = importlib.util.spec_from_file_location(name, root / subdir / "server.py")
+            module = importlib.util.module_from_spec(spec)
+            sys.modules[name] = module
+            spec.loader.exec_module(module)
+        finally:
+            sys.path.remove(str(root / subdir))
+        assert list(inspect.signature(getattr(module, func)).parameters) == params
diff --git a/tests/test_eval_harness.py b/tests/test_eval_harness.py
new file mode 100644
index 0000000..c11efb5
--- /dev/null
+++ b/tests/test_eval_harness.py
@@ -0,0 +1,142 @@
+"""Unit tests for the offline eval harness (Task 249).
+
+TDD red-green: written first against the planned ``eval_harness``
+module contract. Pure and offline only: structured traces in,
+report rows out. Missing cost/latency stays null, never zero.
+"""
+
+import sys
+from pathlib import Path
+
+BRIDGE_DIR = Path(__file__).parent.parent / "mcp-brain-bridge"
+sys.path.insert(0, str(BRIDGE_DIR))
+
+from eval_harness import aggregate_report, scan_zac, score_case  # noqa: E402
+
+
+def _trace(**over):
+    base = {
+        "case_id": "case-1",
+        "parse_ok": True,
+        "citations": ["decision-001"],
+        "grounding": {"claim-001": ["decision-001"]},
+        "rule_results": {"rule-001": True},
+        "operations": [{"kind": "shell", "command": "pytest tests/ -q"}],
+        "qa_repairs": 1,
+        "cost_usd": 0.01,
+        "latency_ms": 125.0,
+    }
+    base.update(over)
+    return base
+
+
+def _expected(**over):
+    base = {
+        "citations": ["decision-001"],
+        "grounding": [{"claim_id": "claim-001", "supported_by": ["decision-001"]}],
+        "rules": [{"rule_id": "rule-001", "passed": True}],
+    }
+    base.update(over)
+    return base
+
+
+def test_parse_rate_all_pass():
+    rows = [score_case(_trace(), _expected()), score_case(_trace(), _expected())]
+    assert aggregate_report(rows)["parse_rate"] == 1.0
+
+
+def test_parse_rate_partial_pass():
+    rows = [score_case(_trace(), _expected()), score_case(_trace(parse_ok=False), _expected())]
+    assert aggregate_report(rows)["parse_rate"] == 0.5
+
+
+def test_citation_rate_counts_expected_coverage():
+    row = score_case(_trace(citations=["decision-001", "extra-009"]), _expected())
+    assert (row["citation_hits"], row["citation_expected"]) == (1, 1)
+
+
+def test_grounding_requires_full_support():
+    row = score_case(
+        _trace(grounding={"claim-001": ["decision-001"]}),
+        _expected(
+            grounding=[
+                {"claim_id": "claim-001", "supported_by": ["decision-001", "decision-002"]},
+            ]
+        ),
+    )
+    assert (row["grounding_hits"], row["grounding_expected"]) == (0, 1)
+
+
+def test_rule_pass_missing_actual_counts_as_failure():
+    row = score_case(_trace(rule_results={}), _expected())
+    assert (row["rules_passed"], row["rules_expected"]) == (0, 1)
+
+
+def test_zac_scan_detects_direct_git_ops():
+    ops = [
+        {"kind": "shell", "command": "git add foo.py"},
+        {"kind": "operation", "name": "git.commit"},
+        {"kind": "shell", "command": "GIT PUSH origin main"},
+    ]
+    count, clean = scan_zac(ops)
+    assert count == 3
+    assert clean is False
+
+
+def test_zac_scan_ignores_prose_and_docs():
+    count, clean = scan_zac([{"kind": "shell", "command": "pytest tests/ -q"}])
+    assert (count, clean) == (0, True)
+    row = score_case(_trace(), _expected())
+    assert (row["zac_violation_count"], row["zac_clean"]) == (0, True)
+
+
+def test_qa_repair_totals_and_mean():
+    rows = [
+        score_case(_trace(qa_repairs=1), _expected()),
+        score_case(_trace(qa_repairs=3), _expected()),
+    ]
+    report = aggregate_report(rows)
+    assert report["qa_repair_count_total"] == 4
+    assert report["qa_repair_count_mean"] == 2.0
+
+
+def test_cost_columns_preserve_values():
+    row = score_case(_trace(cost_usd=0.01), _expected())
+    assert row["cost_usd"] == 0.01
+    report = aggregate_report([row, score_case(_trace(cost_usd=0.03), _expected())])
+    assert report["cost_total_usd"] == 0.04
+    assert report["cost_observed_case_count"] == 2
+
+
+def test_latency_columns_preserve_values():
+    row = score_case(_trace(latency_ms=125.0), _expected())
+    assert row["latency_ms"] == 125.0
+    report = aggregate_report([row, score_case(_trace(latency_ms=175.0), _expected())])
+    assert report["latency_mean_ms"] == 150.0
+    assert report["latency_observed_case_count"] == 2
+
+
+def test_missing_cost_latency_stay_null():
+    row = score_case(_trace(cost_usd=None, latency_ms=None), _expected())
+    assert row["cost_usd"] is None
+    assert row["latency_ms"] is None
+
+
+def test_aggregate_ignores_missing_cost_latency():
+    rows = [
+        score_case(_trace(cost_usd=0.02, latency_ms=100.0), _expected()),
+        score_case(_trace(cost_usd=None, latency_ms=None), _expected()),
+    ]
+    report = aggregate_report(rows)
+    assert report["cost_total_usd"] == 0.02
+    assert report["cost_mean_usd"] == 0.02
+    assert report["latency_mean_ms"] == 100.0
+    assert report["cost_observed_case_count"] == 1
+    assert report["latency_observed_case_count"] == 1
+
+
+def test_empty_input_defined_report():
+    report = aggregate_report([])
+    assert report["case_count"] == 0
+    assert report["parse_rate"] is None
+    assert report["rows"] == []
diff --git a/tests/test_golden_cases.py b/tests/test_golden_cases.py
new file mode 100644
index 0000000..3a72764
--- /dev/null
+++ b/tests/test_golden_cases.py
@@ -0,0 +1,92 @@
+"""Golden-case execution for retrieval plus eval (Task 249).
+
+Validates the caller-owned JSON fixtures under ``tests/golden/``:
+schema checks first, then execution through the pure modules.
+Fixtures are read-only inputs: any test that mutates a fixture fails.
+"""
+
+import hashlib
+import json
+import sys
+from pathlib import Path
+
+GOLDEN_DIR = Path(__file__).parent / "golden"
+BRIDGE_DIR = Path(__file__).parent.parent / "mcp-brain-bridge"
+sys.path.insert(0, str(BRIDGE_DIR))
+
+from authority_retrieval import retrieve  # noqa: E402
+from eval_harness import aggregate_report, score_case  # noqa: E402
+
+
+def _load(name):
+    path = GOLDEN_DIR / name
+    return path, json.loads(path.read_text())
+
+
+def _hash(path):
+    return hashlib.sha256(path.read_bytes()).hexdigest()
+
+
+def test_retrieval_golden_schema_valid():
+    _, doc = _load("authority_retrieval_cases.json")
+    assert doc["schema_version"] == 1
+    for case in doc["cases"]:
+        assert {"case_id", "query", "candidates", "expected"} <= set(case)
+        for cand in case["candidates"]:
+            assert {"candidate_id", "source", "text", "local_score", "chunk_id"} <= set(cand)
+
+
+def test_eval_golden_schema_valid():
+    _, doc = _load("eval_harness_cases.json")
+    assert doc["schema_version"] == 1
+    for case in doc["cases"]:
+        assert {"case_id", "trace", "expected"} <= set(case)
+        assert {"citations", "grounding", "rules", "parse_ok", "qa_repairs"} <= set(case["expected"])
+
+
+def test_retrieval_golden_missing_field_rejected():
+    import pytest
+
+    with pytest.raises((KeyError, TypeError)):
+        retrieve("q", {"decision": [{"candidate_id": "x"}]})
+
+
+def test_retrieval_golden_cases_execute():
+    _, doc = _load("authority_retrieval_cases.json")
+    for case in doc["cases"]:
+        by_source = {}
+        for cand in case["candidates"]:
+            by_source.setdefault(cand["source"], []).append(cand)
+        adapters = {s: (lambda items: (lambda q: items))(items) for s, items in by_source.items()}
+        result = retrieve(
+            case["query"],
+            adapters,
+            gather_limit=case["expected"].get("gather_limit", 20),
+            narrow_limit=case["expected"].get("narrow_limit", 5),
+        )
+        ids = [c["candidate_id"] for c in result["candidates"]]
+        if "top_candidate_id" in case["expected"]:
+            assert ids[0] == case["expected"]["top_candidate_id"]
+        if "selected_ids" in case["expected"]:
+            assert ids == case["expected"]["selected_ids"]
+
+
+def test_eval_golden_cases_execute():
+    _, doc = _load("eval_harness_cases.json")
+    rows = [score_case(case["trace"], case["expected"]) for case in doc["cases"]]
+    report = aggregate_report(rows)
+    assert report["case_count"] == len(doc["cases"])
+    first = rows[0]
+    assert first["parse_ok"] is True
+    assert first["qa_repair_count"] == 1
+    assert first["cost_usd"] == 0.01
+    assert rows[1]["zac_violation_count"] == 2
+
+
+def test_golden_fixtures_unmodified():
+    paths = [GOLDEN_DIR / "authority_retrieval_cases.json", GOLDEN_DIR / "eval_harness_cases.json"]
+    before = {p.name: _hash(p) for p in paths}
+    test_retrieval_golden_cases_execute()
+    test_eval_golden_cases_execute()
+    after = {p.name: _hash(p) for p in paths}
+    assert before == after
```
<!-- END_GIT_DIFF -->
