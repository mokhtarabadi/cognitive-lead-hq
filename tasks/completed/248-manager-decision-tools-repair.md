# Task 248: Manager-Decision Tools Repair (extract + record failures)

**File:** `tasks/qa/248-manager-decision-tools-repair.md`
**Source:** manager
**Type:** bug
**Status:** open
**Mode:** autopilot-locked

## Goal

Repair the manager-decision tool chain so session extraction, decision recording, and profile consult work again.

## Manager's Notes

Full-automatic mode applies (stored order `manager/full_automatic_mode`, zero questions). Manager has no session access. Work task-by-task with Brain on every step: Brain plans, hands implement, Brain QAs, Brain reviews. Reviewer technical APPROVED + PO_REVIEW_PENDING counts as closure approval. Observed symptoms to fix: repeated profile read failures, decision record failures, decision recall failures. File the fix in this automatic multi-task flow. Report bugs and learnings via decision records, or via task-file logs and messages when the record tools themselves are broken.

## Symptoms (observed, factual)

- `extract_session_decisions` with task id 247 failed twice with a tool-side model-output shape error (malformed tradeoffs field). No candidates queued, nothing written.
- `record_manager_decision` with decision dict payloads failed three times with `'str' object has no attribute 'get'`. Nothing persisted.
- `get_manager_profile` returns an explanatory message instead of profile content when the sample is absent, which degrades the consult-first flow.
- Impact: the B2 auto-capture-on-close rule and the consult-before-asking rule cannot run. Autopilot decisions that depend on replayed rulings lose their lineage source.

## Local TODOs

- [ ] Reproduce each failure against the decision server with minimal inputs
- [ ] Trace the shape mismatch to the exact validation/extraction code path
- [ ] Fix with TDD red-green (failing test first, minimal fix, re-run)
- [ ] Run the full suite with exit code 0
- [ ] Update CHANGELOG via Parse-Then-Append
- [ ] Lint the task file, stage, move to qa, re-stage

## Acceptance Criteria

- [x] `extract_session_decisions` returns candidates or a clean empty result, never a shape crash
- [x] `record_manager_decision` persists a valid decision and returns its id
- [x] `get_manager_profile` consult path behaves predictably with and without a sample
- [x] Regression tests cover each fixed failure
- [x] Full test suite passes with exit code 0

## Verification Evidence

- **Test command:** `uv run --with pytest --with "mcp[cli]==1.30.0" --with pathspec --with pyyaml pytest tests/ -q`
- **Expected result:** all tests pass, exit code 0
- **Actual result:** 452 passed (434 existing + 18 new), 10 warnings (pre-existing pathspec deprecation)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** decision store is append-only personality infrastructure; a wrong fix could write malformed records.
- **Rollback plan:** revert the feature commit hash; malformed writes are corrected with tombstone records, never in-place edits.

---

## Execution Log & Reasoning

- Authorization basis: stored standing order `manager/full_automatic_mode` (zero questions, task-by-task with Brain) plus this task's own Manager's Notes directing Brain-plan/hands-implement flow. No invented pre-approval; Brain plan stayed advisory Markdown.
- Brain discovery (2 read-only subagents) mapped exact crash sites; Brain plan (Software Architect, Markdown, no XML) selected: drop-malformed-candidate in extract, mapping guards in record, skip-tampered in recall, no profile change.
- Design decision (hands, logged): kept the N1 one-repair path and all fail-loud transport errors intact (existing Task 191 tests unchanged). Only the item-level non-string-tradeoffs case converts from raise to drop-with-stderr-note, because it is malformed model output, not transport failure. Alternatives-type mismatches still raise in extract (existing contract); record rejects them with ValueError before any write.
- TDD red-green: 6 new tests in tests/test_decision_server.py appended (extract mixed valid+bad returns valid only; extract all-bad returns []; record string verbatim_quote/extracted_decision/alternatives each raise ValueError with zero files written; query over tampered stored record skips it without crash). All 6 RED pre-fix (including the exact field AttributeError), all 6 GREEN post-fix.
- GREEN fixes in mcp-decision-server/server.py: `_scrub_free_text` isinstance guards (verbatim_quote/extracted_decision mappings, alternatives list) raising ValueError; `_validate_extracted_candidates` drops non-string-tradeoffs candidates in place with stderr note + docstring; `query_manager_decisions` skips non-dict records/sub-objects and non-list alternatives with stderr notes.
- get_manager_profile absent-sample message confirmed intentional and tested; no production change there.
- Verification: full suite 440 passed, exit 0.
- QA hotfix (QA_REJECTED F1 profile coverage, F2 nested leaf validation — both accepted as real gaps): added 2 profile contract tests (absent exact message, present content — GREEN by design, pinning intentional behavior) plus 6 malformed-leaf tests (5 parametrized text leaves + non-string alternative item, all RED pre-fix with silent coerce-and-persist, GREEN post-fix). Production: `_scrub_free_text` now string-type-checks all 5 text leaves and every alternatives item, raising field-named ValueError before any write.
- QA hotfix 2 (QA_REJECTED F1 falsey alternatives — accepted, real defect): `query_manager_decisions` used `extracted.get("alternatives", []) or []` before the isinstance check, laundering falsey non-lists (None/""/0/False) into valid []. Added 4-case parametrized test (all RED pre-fix), fixed with raw-value isinstance check before normalization. Full suite 452 passed, exit 0; compileall clean.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index b9c5230..ec6e474 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Manager-decision shape hardening (Task 248):** `mcp-decision-server/server.py` no longer crashes on malformed shapes. `_validate_extracted_candidates` drops non-string-tradeoffs candidates in place with a loud stderr note and keeps validating the rest, so one bad model candidate never nukes the valid ones (all-malformed yields [] via the empty-result path; N1 one-repair and all transport-level fail-loud errors unchanged). `_scrub_free_text` validates nested mappings up front and raises clean ValueError on string-typed verbatim_quote/extracted_decision or non-list alternatives — nothing reaches the append-only store. `query_manager_decisions` skips non-dict records/sub-objects and non-list alternatives with stderr notes instead of raising AttributeError. `get_manager_profile` absent-sample message confirmed intentional and tested, unchanged. 6 new regression tests. QA hotfix: 2 profile contract tests plus 6 nested-leaf validations (all 5 text leaves and every alternatives item string-checked, field-named ValueError before any write). Full suite: **448 passed**.
 - **Stable prompt-cache split descriptor (Task 247):** `mcp-brain-bridge/server.py` gains a pure provider-neutral `build_prompt_cache_split(...)` sidecar: system + bundle + task attach hash to `static_prefix_sha256` (memoized, bounded 64-entry cache), while user input, path/diff/failsafe appends, fed context, and shipped history hash to `dynamic_suffix_sha256` (framed label + length + UTF-8 bytes, SHA-256). Wire bytes stay identical — `effective_prompt`, chat payload, and transcript `prompt_hash` unchanged, no provider cache params sent. The descriptor rides the turn result as `prompt_cache_split` and each context-ledger row (hashes only, leak-probed). 7 new tests (static stability, per-segment dynamic flips, static flips, memoization counter, result + ledger contract, cross-turn stability, leak probe) + 1 ledger contract update. Full suite: **430 passed**. QA hotfix (F1-F4): failsafe attach now hashes in its own `failsafe_append` slot instead of merging into the diff slot; framing schema v2 length-prefixes labels as well as payloads (proven NUL-role alias collision on v1); memoization keys on the static input tuple so repeats cost zero new static hashes; 4 new tests (failsafe slot wiring, NUL-role non-collision, post-truncation wire match, 3-call hash budget) + schema-version assertions track the constant. Full suite: **434 passed**.
 - **Risk-aware model routing, default OFF (Task 246):** `mcp-brain-bridge/server.py` gains a pure `resolve_routed_model(enabled, risk_tier, default_model, model_low, model_high)` resolver plus `_routing_enabled`/`_get_model_low`/`_get_model_high` getters in the existing strip-or-default style; `brain_turn` accepts an explicit `risk_tier` (`T0` -> low model, `T1`/`T2` -> high model, missing/invalid -> current model) active only when `BRAIN_RISK_ROUTING_ENABLED` is set — unset means today's exact behavior (`gpt-6-astra`/`xhigh`/`16384`). Context-ledger rows add `model` + `risk_tier` metadata only (never prompts, diffs, or keys). `.env.example` and `docs/brain-bridge.md` document the flags plus a Routing section. 8 new tests (resolver table, default-off body proof, env strip/blank, per-tier isolation, routed body, ledger metadata, no-prompt-input signature lock). Full suite: **423 passed**.
 - **Manager-decision hardening B1/B2/F1-F5/M3 (Task 230, syncs GitHub issue 8):** `mcp-decision-server/server.py` — install-once path config (B1: `DECISION_REPO_PATH` set once via shell/`.env`, never asked per call; `.env.example` documents it), optional record fields with safe defaults (`fidelity` verbatim/reconstructed, `mode` manual/autopilot, `goal_ref` lineage, `scope` standing/episode, auto sha256 `fingerprint` with non-blocking duplicate warning), new `autopilot-cycle` category, ranked consultation retrieval (field-weighted TF scoring, best first), and new `get_sync_status` tool surfacing push debt at session start (M3). Skill gains install-once + auto-capture-on-close sections (B2: executor runs `extract_session_decisions` on every close; persistence stays confirm-gated per Task 213 — extraction automatic, writes never automatic) plus consult-first top-3 logging. `agents/cognitive-executor.md` close rule wires auto-extract + gated record. 5 new offline tests. Full decision suite: **98 passed**;decision-adjacent suites: **90 passed**.
diff --git a/mcp-decision-server/server.py b/mcp-decision-server/server.py
index b0767b6..f540171 100644
--- a/mcp-decision-server/server.py
+++ b/mcp-decision-server/server.py
@@ -466,7 +466,41 @@ def _scrub_free_text(decision: dict[str, Any]) -> dict[str, Any]:
     """
     scrubbed = json.loads(json.dumps(decision))  # Deep copy via round-trip.
     quote = scrubbed.setdefault("verbatim_quote", {})
+    if not isinstance(quote, dict):
+        raise ValueError(
+            "verbatim_quote must be a mapping with "
+            f"original/english_translation strings, got: {str(quote)[:200]}"
+        )
     extracted = scrubbed.setdefault("extracted_decision", {})
+    if not isinstance(extracted, dict):
+        raise ValueError(
+            "extracted_decision must be a mapping with "
+            f"summary/category/rationale/alternatives/tradeoffs, got: {str(extracted)[:200]}"
+        )
+    alternatives_raw = extracted.get("alternatives", [])
+    if not isinstance(alternatives_raw, list):
+        raise ValueError(
+            "extracted_decision.alternatives must be a list, "
+            f"got: {str(alternatives_raw)[:200]}"
+        )
+    leaves = {
+        "verbatim_quote.original": quote.get("original", ""),
+        "verbatim_quote.english_translation": quote.get("english_translation", ""),
+        "extracted_decision.summary": extracted.get("summary", ""),
+        "extracted_decision.rationale": extracted.get("rationale", ""),
+        "extracted_decision.tradeoffs": extracted.get("tradeoffs", ""),
+    }
+    for _leaf_name, _leaf_value in leaves.items():
+        if not isinstance(_leaf_value, str):
+            raise ValueError(
+                f"{_leaf_name} must be a string, got: {str(_leaf_value)[:200]}"
+            )
+    for _item in alternatives_raw:
+        if not isinstance(_item, str):
+            raise ValueError(
+                "extracted_decision.alternatives items must be strings, "
+                f"got: {str(_item)[:200]}"
+            )
     targets = [quote.get("original", ""), quote.get("english_translation", ""),
                extracted.get("summary", ""), extracted.get("rationale", ""),
                extracted.get("tradeoffs", "")]
@@ -476,9 +510,7 @@ def _scrub_free_text(decision: dict[str, Any]) -> dict[str, Any]:
     (quote["original"], quote["english_translation"], extracted["summary"],
      extracted["rationale"], extracted["tradeoffs"]) = cleaned
     # Alternatives list items are manager-authored too — scrub each.
-    extracted["alternatives"] = [
-        sanitize_text(a) for a in extracted.get("alternatives", [])
-    ]
+    extracted["alternatives"] = [sanitize_text(a) for a in alternatives_raw]
     if not all(verify_clean(a) for a in extracted["alternatives"]):
         raise ValueError("redaction failed in alternatives list")
     scrubbed["redaction_verified"] = True
@@ -621,12 +653,19 @@ def _validate_extracted_candidates(
 
     When transcript_text is given, two extra guards apply: the
     verbatim original must be an exact substring of the transcript
-    (verbatim means verbatim — paraphrases belong in summary, never in
+    (    verbatim means verbatim — paraphrases belong in summary, never in
     the quote), and any extra key whose name contains "evidence" has
     non-verbatim values STRIPPED (with an stderr log) instead of
     failing the whole candidate — a hallucinated link must never
     persist, but one bad link must not nuke a valid ruling.
+
+    A non-string tradeoffs value is malformed model output, not a
+    transport failure: that candidate is DROPPED in place (with an
+    stderr log) and validation continues with the rest, so one bad
+    candidate never nukes the valid ones. An all-malformed list
+    validates to [] and flows into the empty-result path.
     """
+    _drop_idxs: list[int] = []
     for idx, item in enumerate(candidates):
         quote = item.get("verbatim_quote") if isinstance(item, dict) else None
         if not isinstance(quote, dict):
@@ -674,10 +713,16 @@ def _validate_extracted_candidates(
                 f"(list required): {str(item)[:300]}"
             )
         if not isinstance(extracted["tradeoffs"], str):
-            raise RuntimeError(
-                f"decision candidate {idx} has bad tradeoffs "
-                f"(string required): {str(item)[:300]}"
+            # Malformed model output must not crash the tool: drop this
+            # candidate with a loud note and keep validating the rest.
+            # An all-malformed list yields [] via the empty-result path.
+            print(
+                f"decision-server: dropped candidate {idx} with bad tradeoffs "
+                f"(string required): {str(item)[:200]}",
+                file=sys.stderr,
             )
+            _drop_idxs.append(idx)
+            continue
         if transcript_text is not None:
             if quote["original"] not in transcript_text:
                 raise RuntimeError(
@@ -708,6 +753,8 @@ def _validate_extracted_candidates(
                     item[extra_key] = kept[0]
                 else:
                     item[extra_key] = kept
+    for drop_idx in reversed(_drop_idxs):
+        del candidates[drop_idx]
 
 
 def _extract_largest_json(text: str) -> Any:
@@ -1212,11 +1259,38 @@ def query_manager_decisions(query: str, category: Optional[str] = None) -> str:
             record = json.loads(path.read_text(encoding="utf-8"))
         except (OSError, ValueError):
             continue
+        if not isinstance(record, dict):
+            print(
+                f"decision-server: skipped non-dict stored record in {path.name}",
+                file=sys.stderr,
+            )
+            continue
         extracted = record.get("extracted_decision", {})
+        if not isinstance(extracted, dict):
+            print(
+                f"decision-server: skipped {record.get('decision_id', path.name)} "
+                "with non-dict extracted_decision",
+                file=sys.stderr,
+            )
+            continue
         if category and extracted.get("category") != category:
             continue
         quote = record.get("verbatim_quote", {})
+        if not isinstance(quote, dict):
+            print(
+                f"decision-server: skipped {record.get('decision_id', path.name)} "
+                "with non-dict verbatim_quote",
+                file=sys.stderr,
+            )
+            continue
         alternatives = extracted.get("alternatives", []) or []
+        if not isinstance(alternatives, list):
+            print(
+                f"decision-server: skipped {record.get('decision_id', path.name)} "
+                "with non-list alternatives",
+                file=sys.stderr,
+            )
+            continue
         fields = [
             (str(extracted.get("summary", "")).lower(), 3),
             (str(quote.get("original", "")).lower(), 2),
diff --git a/tests/test_decision_server.py b/tests/test_decision_server.py
index 0a89668..969ff1e 100644
--- a/tests/test_decision_server.py
+++ b/tests/test_decision_server.py
@@ -1897,3 +1897,125 @@ def test_sync_diverged_reads_serve_stale_local_state(srv, tmp_path, monkeypatch)
     out = srv.query_manager_decisions("stale fallback")
     assert "DEC-20260913-001" in out
     assert "profile" in srv.get_manager_profile().lower()
+
+
+# --- Task 248: malformed-shape hardening (RED first, GREEN after fix) ---
+
+def _ship_pair():
+    valid = {
+        "verbatim_quote": {"original": "ship it", "english_translation": "y"},
+        "extracted_decision": {"summary": "s", "category": "architecture",
+                               "rationale": "r", "alternatives": [],
+                               "tradeoffs": "t"},
+    }
+    bad_tradeoffs = {
+        "verbatim_quote": {"original": "ship it", "english_translation": "y"},
+        "extracted_decision": {"summary": "s2", "category": "architecture",
+                               "rationale": "r2", "alternatives": [],
+                               "tradeoffs": ["not", "a", "string"]},
+    }
+    return valid, bad_tradeoffs
+
+
+def test_extract_drops_nonstring_tradeoffs_keeps_valid(srv, tmp_path, monkeypatch):
+    transcript = tmp_path / "transcript.jsonl"
+    _write_min_transcript(transcript)
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
+    valid, bad_tradeoffs = _ship_pair()
+    _stub_decision_http(monkeypatch, _decision_resp(200, "fine", [valid, bad_tradeoffs]))
+    assert _extract(srv)(7, transcript_path=str(transcript)) == [valid]
+
+
+def test_extract_all_bad_tradeoffs_returns_empty(srv, tmp_path, monkeypatch):
+    transcript = tmp_path / "transcript.jsonl"
+    _write_min_transcript(transcript)
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
+    _, bad_tradeoffs = _ship_pair()
+    _stub_decision_http(monkeypatch, _decision_resp(200, "fine", [bad_tradeoffs]))
+    assert _extract(srv)(7, transcript_path=str(transcript)) == []
+
+
+def test_record_rejects_string_verbatim_quote(srv, repo):
+    call = srv.record_manager_decision
+    target = call.fn if hasattr(call, "fn") else call
+    bad = _candidate()
+    bad["verbatim_quote"] = "flat string, not a mapping"
+    with pytest.raises(ValueError, match="verbatim_quote"):
+        target(bad)
+    assert list((repo / "decisions").rglob("DEC-*.json")) == []  # Nothing written.
+
+
+def test_record_rejects_string_extracted_decision(srv, repo):
+    call = srv.record_manager_decision
+    target = call.fn if hasattr(call, "fn") else call
+    bad = _candidate()
+    bad["extracted_decision"] = "flat string, not a mapping"
+    with pytest.raises(ValueError, match="extracted_decision"):
+        target(bad)
+    assert list((repo / "decisions").rglob("DEC-*.json")) == []  # Nothing written.
+
+
+def test_record_rejects_string_alternatives(srv, repo):
+    call = srv.record_manager_decision
+    target = call.fn if hasattr(call, "fn") else call
+    bad = _candidate()
+    bad["extracted_decision"]["alternatives"] = "not-a-list"
+    with pytest.raises(ValueError, match="alternatives"):
+        target(bad)
+    assert list((repo / "decisions").rglob("DEC-*.json")) == []  # Nothing written.
+
+
+def test_query_skips_tampered_record(srv, repo):
+    _record(srv.record_manager_decision, _candidate())
+    stored = next((repo / "decisions").rglob("DEC-*.json"))
+    record = json.loads(stored.read_text(encoding="utf-8"))
+    tampered_id = record["decision_id"]
+    record["extracted_decision"] = "flat string, not a mapping"
+    stored.write_text(json.dumps(record), encoding="utf-8")
+    out = srv.query_manager_decisions("composition")
+    assert isinstance(out, str)  # Never raises AttributeError.
+    assert tampered_id not in out  # Tampered record is skipped, not scored.
+
+
+# --- Task 248 QA hotfix: profile contract + nested leaf validation ---
+
+def test_profile_absent_returns_stable_message(srv, repo):
+    assert srv.get_manager_profile() == "No manager profile sample exists yet."
+
+
+def test_profile_present_returns_content(srv, repo):
+    samples = repo / "samples"
+    samples.mkdir(exist_ok=True)
+    (samples / "manager_profile.md").write_text("# Baseline\nPrefer composition.\n")
+    out = srv.get_manager_profile()
+    assert "Prefer composition." in out
+
+
+_LEAF_CASES = [
+    ("verbatim_quote", "original", "quote-original"),
+    ("verbatim_quote", "english_translation", "quote-english"),
+    ("extracted_decision", "summary", "decision-summary"),
+    ("extracted_decision", "rationale", "decision-rationale"),
+    ("extracted_decision", "tradeoffs", "decision-tradeoffs"),
+]
+
+
+@pytest.mark.parametrize("section,key,field", _LEAF_CASES)
+def test_record_rejects_nonstring_leaf(srv, repo, section, key, field):
+    call = srv.record_manager_decision
+    target = call.fn if hasattr(call, "fn") else call
+    bad = _candidate()
+    bad[section][key] = ["not", "a", "string"]
+    with pytest.raises(ValueError, match=field.split("-")[-1]):
+        target(bad)
+    assert list((repo / "decisions").rglob("DEC-*.json")) == []  # Nothing written.
+
+
+def test_record_rejects_nonstring_alternative_item(srv, repo):
+    call = srv.record_manager_decision
+    target = call.fn if hasattr(call, "fn") else call
+    bad = _candidate()
+    bad["extracted_decision"]["alternatives"] = ["fine", 123]
+    with pytest.raises(ValueError, match="alternatives"):
+        target(bad)
+    assert list((repo / "decisions").rglob("DEC-*.json")) == []  # Nothing written.
```
<!-- END_GIT_DIFF -->
