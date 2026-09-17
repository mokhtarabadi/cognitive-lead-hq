# Task 247: Stable prompt-cache separation for Brain turns

**File:** `tasks/qa/247-brain-prompt-cache-separation.md`
**Source:** manager
**Type:** feature
**Status:** open
**Mode:** autopilot-locked

## Goal

Split every Brain turn prompt into a stable static prefix and a dynamic suffix so repeated turns share maximal prefix bytes, and expose the split for provider-side prompt caching.

## Manager's Notes

Standing orders apply: zero-questions task-by-task autopilot with Brain on every step; consult stored manager decisions instead of asking; reviewer approval counts as closure approval. Brain-verdict priority A2 (follows closed routing work). Discovery fed: assembly order is user_prompt baseline -> bundle prepend -> task-attach prepend -> paths append -> diff/failsafe append -> fed-context prepend; final wire order is system + history + user=effective_prompt; no breakpoint/cache-key construct exists; prompt_hash is transcript-only; body carries no cache params; provider cache support unverifiable in-repo. Design must stay provider-neutral (no unverifiable cache_control/previous_response_id params), offline-testable, and additive.

## Local TODOs

- [x] Brain planning turn under task id 247 (Architect + Programmer consult)
- [x] TDD: failing tests for static/dynamic split + stability contract
- [x] Implement split + static-prefix hash exposure (provider-neutral)
- [x] Full suite green, lint_task_file, CHANGELOG, docs
- [x] stage_and_inject_diff, move to qa, Brain QA + Reviewer review

## Acceptance Criteria

- [x] Static prefix (system prompt + bundle + task attach) is byte-stable across turns for the same task/project and computed once per identical input
- [x] Dynamic suffix (paths attach + diff + user prompt + history-sensitive parts) carries all per-turn variation
- [x] Split point is observable (returned or logged) without leaking prompt text, keys, or diffs
- [x] No change to wire semantics when the feature is inert; existing tests keep passing
- [x] Full suite exit 0, lint_task_file passes, CHANGELOG updated

## Verification Evidence

- **Test command:** uv run pytest tests/ -q
- **Expected result:** all pass, exit 0
- **Actual result:** 434 passed (11 new split tests GREEN after RED: 7 original + 4 hotfix M1-M4; 1 existing ledger exact-set test updated; 2 schema-version assertions track the constant)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** split changes effective_prompt bytes and breaks golden prompt_hash attribution; dynamic/stable misclassification leaks per-turn bytes into cache key
- **Rollback plan:** revert feature commit; static/dynamic split is additive so removal restores byte-identical prompts

---

## Execution Log & Reasoning

- Autopilot locked (standing zero-questions order). Discovery via 1 subagent (fed above).
- Seat Check: contract/split design -> Architect; implementation plan -> Programmer; skipped Designer/Strategist/Planner/QA-Review (no UI, single task, gates later).
- Brain plan (Architect-led, 2 turns — first truncated mid-table, second compact re-issue complete): logical segment split, additive sidecar descriptor, byte-identical wire, hash-only exposure via result + ledger.
- Assumption A1: plan-approval pause skipped under standing zero-questions order (same as prior closed task); plan executed verbatim from Brain, deviations will be logged.
- Implementation (TDD, Brain plan executed verbatim): `server.py` += `_frame_segment` (label+NUL+len+NUL+bytes), `_static_prefix_hash` (memoized, 64-entry cap, `_STATIC_SPLIT_COMPUTES` hook), pure `build_prompt_cache_split` (static: system/bundle/task-attach; dynamic: user/paths/diff/failsafe/fed/history-turns); `brain_turn` captures the 5 segment strings inline, computes the descriptor post-truncation, exposes it as `result["prompt_cache_split"]` + ledger `prompt_cache_split` (ledger param optional, never raises). Diff and failsafe share one dynamic slot (mutually exclusive branches) while the pure function keeps both params per the plan's order list. Wire untouched: body keys unchanged, `prompt_hash` unchanged, no provider cache params.
- Design note: split is logical, not a prefix rewrite — fed context still prepends on the wire; adapters must not assume contiguity (per Brain §4).
- RED: 7 new tests failed (missing function/key). GREEN: 7 pass. Full suite 430 passed exit 0 (1 existing ledger exact-set test updated for additive key + renamed). CHANGELOG Added entry + docs/brain-bridge.md Prompt-cache split section.
- QA_REJECTED (Brain QA Engineer, real defects, no dispute): F1 failsafe branch never populates `failsafe_text` (merged into diff slot — dynamic still varied, but contract deviation from the approved plan); F2 `_frame_segment` length-prefixes payload but not label, NUL-bearing history roles can collide; F3 descriptor must provably derive from post-truncation segments; F4 cache hashes before lookup (counter proves misses, not skipped hashes). Hotfix scope: F1-F4 + M1-M4 regression tests, no new task file, no commit/close/move.
- Hotfix RED: all 4 new tests failed pre-fix (M1 dynamic-slot mismatch, M2 NUL-role alias, M3 guard, M4 4 sha256 calls vs 3 budget). Test correction: M3 budget 50 never triggered the middle drop (turn-1 assembly ~34 chars) — lowered to 20 so truncation provably fires; M2 guard fixed 6->5 (honest length of the collision pivot). F3 premise did NOT reproduce: the split computes after the in-place middle-drop loop, so the descriptor was already post-truncation — M3 stays as a regression guard locking the invariant. F2 verified real: old framing hashed both M2 histories to identical bytes (script proof `old framing collides: True`), v2 distinguishes.
- Hotfix GREEN: F1 failsafe branch captures `failsafe_text` separately and passes it through (diff slot stays empty on failsafe turns); F2 `_frame_segment` length-prefixes labels too + schema v2 (honest lengths make left-to-right parse unique); F4 cache keyed by the static input tuple (refs, no copies; 64-cap + eviction kept). Full suite 434 passed exit 0. CHANGELOG hotfix note + docs/brain-bridge.md framing/slot sentences updated. Ready for re-QA.
- Re-QA QA_PASSED (Brain QA Engineer, project_root passed explicitly after one blocked round where the diff attach missed its root): F1-F5 all PASS on visible scope; suite evidence 434 accepted, QA did not re-execute. Debug note: an earlier re-QA without project_root returned diff-UNAVAILABLE even though the hunks were injected — local probe proved `_resolve_task_file` + `build_diff_attach` healthy, so the miss was a server-side root mismatch; always pass project_root on QA/review turns.
- Review APPROVED + PO_REVIEW_PENDING (Brain Code Reviewer, zero blocking issues): S1-S6 strengths (blueprint fidelity, wire preservation, hotfix coverage, privacy boundary, docs sync, test quality). I1 low non-blocking residual: `_STATIC_SPLIT_CACHE` lookup-then-compute unsynchronized — concurrent identical turns could double-compute; no concurrent requirement established (single-threaded MCP server), deferred as follow-up, not a fix in this task. I2/I3 coverage limits only (truncated test diff, absent core spec files per Absent-File Policy).
- Closure acceptance: standing Manager order rules this close — reviewer approval counts as Manager approval. Manager accept quote (standing, pre-authorized): reviewer approval = his approval. Closing via Senior Programmer closure XML, single issuance.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 56c65d2..b9c5230 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Stable prompt-cache split descriptor (Task 247):** `mcp-brain-bridge/server.py` gains a pure provider-neutral `build_prompt_cache_split(...)` sidecar: system + bundle + task attach hash to `static_prefix_sha256` (memoized, bounded 64-entry cache), while user input, path/diff/failsafe appends, fed context, and shipped history hash to `dynamic_suffix_sha256` (framed label + length + UTF-8 bytes, SHA-256). Wire bytes stay identical — `effective_prompt`, chat payload, and transcript `prompt_hash` unchanged, no provider cache params sent. The descriptor rides the turn result as `prompt_cache_split` and each context-ledger row (hashes only, leak-probed). 7 new tests (static stability, per-segment dynamic flips, static flips, memoization counter, result + ledger contract, cross-turn stability, leak probe) + 1 ledger contract update. Full suite: **430 passed**. QA hotfix (F1-F4): failsafe attach now hashes in its own `failsafe_append` slot instead of merging into the diff slot; framing schema v2 length-prefixes labels as well as payloads (proven NUL-role alias collision on v1); memoization keys on the static input tuple so repeats cost zero new static hashes; 4 new tests (failsafe slot wiring, NUL-role non-collision, post-truncation wire match, 3-call hash budget) + schema-version assertions track the constant. Full suite: **434 passed**.
 - **Risk-aware model routing, default OFF (Task 246):** `mcp-brain-bridge/server.py` gains a pure `resolve_routed_model(enabled, risk_tier, default_model, model_low, model_high)` resolver plus `_routing_enabled`/`_get_model_low`/`_get_model_high` getters in the existing strip-or-default style; `brain_turn` accepts an explicit `risk_tier` (`T0` -> low model, `T1`/`T2` -> high model, missing/invalid -> current model) active only when `BRAIN_RISK_ROUTING_ENABLED` is set — unset means today's exact behavior (`gpt-6-astra`/`xhigh`/`16384`). Context-ledger rows add `model` + `risk_tier` metadata only (never prompts, diffs, or keys). `.env.example` and `docs/brain-bridge.md` document the flags plus a Routing section. 8 new tests (resolver table, default-off body proof, env strip/blank, per-tier isolation, routed body, ledger metadata, no-prompt-input signature lock). Full suite: **423 passed**.
 - **Manager-decision hardening B1/B2/F1-F5/M3 (Task 230, syncs GitHub issue 8):** `mcp-decision-server/server.py` — install-once path config (B1: `DECISION_REPO_PATH` set once via shell/`.env`, never asked per call; `.env.example` documents it), optional record fields with safe defaults (`fidelity` verbatim/reconstructed, `mode` manual/autopilot, `goal_ref` lineage, `scope` standing/episode, auto sha256 `fingerprint` with non-blocking duplicate warning), new `autopilot-cycle` category, ranked consultation retrieval (field-weighted TF scoring, best first), and new `get_sync_status` tool surfacing push debt at session start (M3). Skill gains install-once + auto-capture-on-close sections (B2: executor runs `extract_session_decisions` on every close; persistence stays confirm-gated per Task 213 — extraction automatic, writes never automatic) plus consult-first top-3 logging. `agents/cognitive-executor.md` close rule wires auto-extract + gated record. 5 new offline tests. Full decision suite: **98 passed**;decision-adjacent suites: **90 passed**.
 - **Decision follow-up hardening H1/H2/H3 + B2 live proof (Task 231):** fingerprint path now tolerates a stray string `verbatim_quote`/`extracted_decision` (H1), skips tampered non-dict store files in both the duplicate scan and the index rewrite instead of crashing (H2), and treats explicit `None` optionals as unset so safe defaults still apply (H3). B2 live evidence: `extract_session_decisions(231)` fired at close handling and returned `[]` loudly (no session transcript in headless run — nothing queued, nothing written). 3 new regression tests. Full decision suite: **101 passed**.
diff --git a/docs/brain-bridge.md b/docs/brain-bridge.md
index a159c97..5d3f56b 100644
--- a/docs/brain-bridge.md
+++ b/docs/brain-bridge.md
@@ -89,6 +89,25 @@ behavior never change under routing. Each context-ledger row records
 the selected `model` and the `risk_tier` (metadata only — never prompt
 text, diffs, or keys).
 
+## Prompt-cache split
+
+Every turn computes a provider-neutral split descriptor alongside the
+unchanged wire payload: the stable prefix (system prompt + bundle +
+task attach) hashes to `static_prefix_sha256` (memoized per identical
+static inputs — a repeat costs zero new static hashes), and everything
+per-turn (user input, path/diff/failsafe appends,
+fed context, shipped history) hashes to `dynamic_suffix_sha256`.
+Only hashes and fixed labels travel — never prompt text, diffs, keys,
+or history content. The descriptor is returned as `prompt_cache_split`
+on the turn result and recorded on each context-ledger row, so repeated
+turns with an identical static hash share maximal prefix bytes for any
+provider-side caching. The split is logical, not a rewrite: fed context
+still prepends on the wire exactly as before. Framing schema v2
+length-prefixes labels as well as payloads, so NUL-bearing history
+roles (caller-controlled transcript text) can never alias another
+segment list's bytes; the failsafe attach hashes in its own slot,
+never merged into the diff slot.
+
 ## Autopilot + manager-decision
 
 Autopilot mode (default OFF) runs the full state machine with zero
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 62d52ba..c5e5c48 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -998,6 +998,103 @@ def resolve_routed_model(enabled: bool, risk_tier: Optional[str],
     return default_model
 
 
+#: Prompt-cache split descriptor version. Bump only when the segment
+#: framing below changes; consumers key stability on this number.
+_CACHE_SPLIT_SCHEMA_VERSION = 2
+
+#: Logical split boundary: everything up to and including the task
+#: attach is the stable prefix; user input, injected paths, diffs,
+#: fed context, and history form the dynamic suffix (Task 247).
+_CACHE_SPLIT_BOUNDARY = "after_system_bundle_task_attach"
+
+#: Memoized static-prefix hashes, keyed by the static INPUTS (the
+#: three texts, held by reference — no copies). A hit means identical
+#: static bytes, so the stored hash is the answer without re-hashing.
+#: Bounded: oldest entry evicted past the cap.
+_STATIC_SPLIT_CACHE: dict[tuple[str, str, str], str] = {}
+_STATIC_SPLIT_CACHE_MAX = 64
+
+#: Test hook: counts static-hash computations (cache misses). Never
+#: read on the hot path for logic — informational only.
+_STATIC_SPLIT_COMPUTES = 0
+
+
+def _frame_segment(label: str, text: str) -> bytes:
+    """Deterministic framing: len + NUL + label + NUL + len + NUL + bytes.
+
+    Both halves are length-prefixed so concatenation stays injective:
+    labels are caller-controlled (history roles come from transcripts
+    and may carry NULs), and an unprefixed label lets one segment
+    list alias another's bytes. Lengths are always honest (computed
+    here, never caller-supplied), so parsing left-to-right is unique
+    and two different segment lists can never frame identically."""
+    lab = label.encode("utf-8")
+    data = text.encode("utf-8")
+    return (str(len(lab)).encode() + b"\x00" + lab + b"\x00"
+            + str(len(data)).encode() + b"\x00" + data)
+
+
+def _static_prefix_hash(system_prompt: str, bundle_text: str,
+                        task_attach_text: str) -> str:
+    """SHA-256 over the framed static segments, memoized (Task 247).
+
+    The lookup key is the static input tuple itself, so a repeat
+    input costs zero new static hashes — the digest is computed only
+    on a miss."""
+    global _STATIC_SPLIT_COMPUTES
+    key = (system_prompt, bundle_text, task_attach_text)
+    cached = _STATIC_SPLIT_CACHE.get(key)
+    if cached is not None:
+        return cached
+    framed = (b"".join((
+        _frame_segment("system_prompt", system_prompt),
+        _frame_segment("bundle_prepend", bundle_text),
+        _frame_segment("task_attach_prepend", task_attach_text),
+    )))
+    digest = hashlib.sha256(framed).hexdigest()
+    _STATIC_SPLIT_COMPUTES += 1
+    if len(_STATIC_SPLIT_CACHE) >= _STATIC_SPLIT_CACHE_MAX:
+        _STATIC_SPLIT_CACHE.pop(next(iter(_STATIC_SPLIT_CACHE)))
+    _STATIC_SPLIT_CACHE[key] = digest
+    return digest
+
+
+def build_prompt_cache_split(
+        system_prompt: str, bundle_text: str, task_attach_text: str,
+        user_prompt: str, paths_text: str = "", diff_text: str = "",
+        failsafe_text: str = "", fed_text: str = "",
+        history: Optional[list] = None) -> dict[str, str]:
+    """Pure static/dynamic split descriptor (Task 247).
+
+    Provider-neutral sidecar metadata: hashes and fixed labels only —
+    never prompt text, keys, diffs, paths, or history content. The
+    static half covers the stable prefix (system + bundle + task
+    attach); the dynamic half covers everything that may vary per
+    turn (user input, path/diff/failsafe/fed-context appends, and
+    the shipped history). Takes values only — no environment reads,
+    no network, no mutation of the prompt."""
+    static_hash = _static_prefix_hash(
+        system_prompt, bundle_text, task_attach_text)
+    frames = [
+        _frame_segment("user_prompt", user_prompt),
+        _frame_segment("paths_attach", paths_text),
+        _frame_segment("diff_append", diff_text),
+        _frame_segment("failsafe_append", failsafe_text),
+        _frame_segment("fed_context", fed_text),
+    ]
+    for idx, turn in enumerate(history or []):
+        role = turn.get("role", "") if isinstance(turn, dict) else ""
+        content = turn.get("content", "") if isinstance(turn, dict) else ""
+        frames.append(_frame_segment(f"history[{idx}].{role}", content))
+    dynamic_hash = hashlib.sha256(b"".join(frames)).hexdigest()
+    return {
+        "schema_version": _CACHE_SPLIT_SCHEMA_VERSION,
+        "split_boundary": _CACHE_SPLIT_BOUNDARY,
+        "static_prefix_sha256": static_hash,
+        "dynamic_suffix_sha256": dynamic_hash,
+    }
+
+
 def _get_max_tokens() -> int:
     """Cap for Brain turns; override via ``BRAIN_MAX_TOKENS``."""
     try:
@@ -1166,12 +1263,14 @@ def _append_context_ledger(
     truncated_count: int,
     model: Optional[str] = None,
     risk_tier: Optional[str] = None,
+    prompt_cache_split: Optional[dict] = None,
 ) -> None:
     """Best-effort utilization ledger: one JSON line per turn under the
     sessions root (Task 241 context-gap fix). Never raises — a ledger
     failure must not break the Brain turn it measures. Additive
-    ``model``/``risk_tier`` metadata only (Task 246) — never prompt
-    text, diffs, or keys."""
+    ``model``/``risk_tier`` (Task 246) and ``prompt_cache_split``
+    (Task 247, hashes only) metadata — never prompt text, diffs,
+    or keys."""
     try:
         row = {
             "task_id": task_id or "noid",
@@ -1181,6 +1280,7 @@ def _append_context_ledger(
             "truncated": truncated_count,
             "model": model,
             "risk_tier": (risk_tier or "").strip() or None,
+            "prompt_cache_split": prompt_cache_split,
         }
         ledger = _sessions_root(project_root) / _CONTEXT_LEDGER_NAME
         ledger.parent.mkdir(parents=True, exist_ok=True)
@@ -1822,8 +1922,17 @@ def brain_turn(
 
     system_prompt = load_system_prompt(system_prompt_path)
     effective_prompt = user_prompt
+    # Segment captures for the prompt-cache split descriptor (Task 247):
+    # static pieces are hashed for stability, dynamic pieces per turn.
+    bundle_text = ""
+    task_attach_text = ""
+    paths_text = ""
+    diff_append_text = ""
+    failsafe_text = ""
+    fed_text = ""
     if include_bundle and _BUNDLE_MARKER not in user_prompt:
-        effective_prompt = _build_context_bundle() + "\n\n---\n\n" + user_prompt
+        bundle_text = _build_context_bundle()
+        effective_prompt = bundle_text + "\n\n---\n\n" + user_prompt
     if include_bundle and task_id:
         try:
             attach = _build_task_attach(task_id, project_root=project_root)
@@ -1833,6 +1942,7 @@ def brain_turn(
                 else _TASK_FILE_MARKER
             )
             if attach and _ns not in user_prompt:
+                task_attach_text = attach
                 effective_prompt = attach + "\n\n---\n\n" + effective_prompt
         except Exception as exc:  # never fail a turn on attach problems
             print(f"brain-bridge: task attach skipped ({exc})", file=sys.stderr)
@@ -1844,6 +1954,7 @@ def brain_turn(
             paths_attach = build_paths_attach(
                 context_paths, project_root=project_root)
             if paths_attach:
+                paths_text = paths_attach
                 effective_prompt = (
                     effective_prompt + "\n\n---\n\n" + paths_attach)
         except Exception as exc:  # never fail a turn on attach problems
@@ -1859,6 +1970,7 @@ def brain_turn(
                 task_id.strip() if isinstance(task_id, str) else "",
                 project_root=project_root)
             if dattach:
+                diff_append_text = dattach
                 effective_prompt = effective_prompt + "\n\n---\n\n" + dattach
             else:
                 print("brain-bridge: include_diff=True but no hunks "
@@ -1876,6 +1988,7 @@ def brain_turn(
             if dattach:
                 print("brain-bridge: QA turn without include_diff, "
                       "auto-attaching diff", file=sys.stderr)
+                failsafe_text = dattach
                 effective_prompt = (effective_prompt + "\n\n---\n\n"
                                     + dattach)
         except Exception as exc:  # never fail a turn on attach problems
@@ -1902,6 +2015,7 @@ def brain_turn(
                 save_fed_context(task_id, fed, project_root=project_root)
             pinned = load_fed_context(task_id, project_root=project_root)
             if pinned and "[pinned-fed-context]" not in effective_prompt:
+                fed_text = pinned
                 effective_prompt = (
                     "[pinned-fed-context]\n" + pinned
                     + "\n[/pinned-fed-context]\n\n---\n\n"
@@ -1926,9 +2040,17 @@ def brain_turn(
         truncated_count += 1
     budget_chars = len(system_prompt) + len(effective_prompt) + _hist_chars()
     util_pct = budget_chars * 100 // _MODEL_WINDOW_CHARS
+    # Sidecar only: the split descriptor never touches wire bytes —
+    # effective_prompt, chat payload, and prompt_hash stay identical.
+    cache_split = build_prompt_cache_split(
+        system_prompt, bundle_text, task_attach_text, user_prompt,
+        paths_text=paths_text, diff_text=diff_append_text,
+        failsafe_text=failsafe_text, fed_text=fed_text,
+        history=history)
     _append_context_ledger(task_id, project_root, budget_chars,
                            truncated_count, model=model,
-                           risk_tier=risk_tier)
+                           risk_tier=risk_tier,
+                           prompt_cache_split=cache_split)
     if budget_chars > _PROMPT_WARN_CHARS:
         print(
             f"brain-bridge: prompt is large (budget_chars={budget_chars} "
@@ -2012,6 +2134,7 @@ def brain_turn(
         "truncated_count": truncated_count,
         "budget_chars": budget_chars,
         "retry_count": attempts,
+        "prompt_cache_split": cache_split,
     }
     if fence_drops:
         result["debug"] = {
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index 502d592..d49ad7f 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -2120,23 +2120,28 @@ def test_routed_body_uses_selected_model(tmp_path, monkeypatch):
     assert holder["body"]["model"] == "high-m"
 
 
-def test_ledger_carries_model_and_tier_only(tmp_path, monkeypatch):
+def test_ledger_carries_model_tier_and_cache_split(tmp_path, monkeypatch):
     import json
     _clean_routing_env(monkeypatch)
     monkeypatch.setenv("BRAIN_RISK_ROUTING_ENABLED", "true")
     monkeypatch.setenv("BRAIN_MODEL_LOW", "low-m")
     secret_prompt = "ledger-leak-probe-zz9"
-    _run_turn_capture(monkeypatch, tmp_path, _ok_payload("ok"),
-                      prompt=secret_prompt, risk_tier="T0")
+    result, _ = _run_turn_capture(monkeypatch, tmp_path, _ok_payload("ok"),
+                                  prompt=secret_prompt, risk_tier="T0")
     ledger = tmp_path / "sessions" / bridge._CONTEXT_LEDGER_NAME
     blob = ledger.read_text(encoding="utf-8").strip().split("\n")[-1]
     row = json.loads(blob)
     assert row["model"] == "low-m"
     assert row["risk_tier"] == "T0"
+    assert row["prompt_cache_split"] == result["prompt_cache_split"]
+    assert set(row["prompt_cache_split"]) == {
+        "schema_version", "split_boundary", "static_prefix_sha256",
+        "dynamic_suffix_sha256"}
     assert secret_prompt not in blob
     assert "sk-test-key" not in blob
     assert set(row) == {"task_id", "budget_chars", "est_tokens",
-                        "util_pct", "truncated", "model", "risk_tier"}
+                        "util_pct", "truncated", "model", "risk_tier",
+                        "prompt_cache_split"}
 
 
 def test_resolver_takes_no_prompt_diff_or_key():
@@ -2144,3 +2149,225 @@ def test_resolver_takes_no_prompt_diff_or_key():
     params = set(inspect.signature(bridge.resolve_routed_model).parameters)
     assert params == {"enabled", "risk_tier", "default_model",
                       "model_low", "model_high"}
+
+
+def _split_kwargs(**over):
+    base = dict(system_prompt="sys", bundle_text="bundle",
+                task_attach_text="attach", user_prompt="q",
+                paths_text="", diff_text="", failsafe_text="",
+                fed_text="", history=[])
+    base.update(over)
+    return base
+
+
+def test_cache_split_static_stable_dynamic_varies():
+    a = bridge.build_prompt_cache_split(**_split_kwargs())
+    b = bridge.build_prompt_cache_split(**_split_kwargs(
+        user_prompt="q2", paths_text="p", diff_text="d",
+        failsafe_text="f", fed_text="fed",
+        history=[{"role": "user", "content": "h"}]))
+    assert a["schema_version"] == bridge._CACHE_SPLIT_SCHEMA_VERSION
+    assert (a["split_boundary"]
+            == "after_system_bundle_task_attach")
+    assert a["static_prefix_sha256"] == b["static_prefix_sha256"]
+    assert a["dynamic_suffix_sha256"] != b["dynamic_suffix_sha256"]
+    assert len(a["static_prefix_sha256"]) == 64
+    assert len(a["dynamic_suffix_sha256"]) == 64
+
+
+def test_cache_split_each_dynamic_segment_flips_dynamic():
+    base = bridge.build_prompt_cache_split(**_split_kwargs())
+    for field, val in (("user_prompt", "x"), ("paths_text", "x"),
+                       ("diff_text", "x"), ("failsafe_text", "x"),
+                       ("fed_text", "x")):
+        other = bridge.build_prompt_cache_split(
+            **_split_kwargs(**{field: val}))
+        assert (other["dynamic_suffix_sha256"]
+                != base["dynamic_suffix_sha256"])
+        assert (other["static_prefix_sha256"]
+                == base["static_prefix_sha256"])
+    hist = bridge.build_prompt_cache_split(**_split_kwargs(
+        history=[{"role": "assistant", "content": "x"}]))
+    assert hist["dynamic_suffix_sha256"] != base["dynamic_suffix_sha256"]
+    assert hist["static_prefix_sha256"] == base["static_prefix_sha256"]
+
+
+def test_cache_split_static_change_flips_static_only():
+    base = bridge.build_prompt_cache_split(**_split_kwargs())
+    for field in ("system_prompt", "bundle_text", "task_attach_text"):
+        other = bridge.build_prompt_cache_split(
+            **_split_kwargs(**{field: "changed"}))
+        assert (other["static_prefix_sha256"]
+                != base["static_prefix_sha256"])
+
+
+def test_cache_split_memoizes_static_computation(monkeypatch):
+    bridge._STATIC_SPLIT_CACHE.clear()
+    monkeypatch.setattr(bridge, "_STATIC_SPLIT_COMPUTES", 0)
+    kw = _split_kwargs()
+    bridge.build_prompt_cache_split(**kw)
+    bridge.build_prompt_cache_split(**kw)
+    assert bridge._STATIC_SPLIT_COMPUTES == 1
+    kw["bundle_text"] = "other-bundle"
+    bridge.build_prompt_cache_split(**kw)
+    assert bridge._STATIC_SPLIT_COMPUTES == 2
+
+
+def test_cache_split_result_and_ledger(tmp_path, monkeypatch):
+    import json
+    _clean_routing_env(monkeypatch)
+    result, holder = _run_turn_capture(
+        monkeypatch, tmp_path, _ok_payload("ok"), prompt="cache-q")
+    split = result["prompt_cache_split"]
+    assert split["schema_version"] == bridge._CACHE_SPLIT_SCHEMA_VERSION
+    assert split["split_boundary"] == "after_system_bundle_task_attach"
+    assert len(split["static_prefix_sha256"]) == 64
+    assert len(split["dynamic_suffix_sha256"]) == 64
+    assert set(split) == {"schema_version", "split_boundary",
+                          "static_prefix_sha256",
+                          "dynamic_suffix_sha256"}
+    # Wire untouched: no cache params on the provider body.
+    assert set(holder["body"]) == {"model", "input", "reasoning",
+                                   "max_output_tokens"}
+    ledger = tmp_path / "sessions" / bridge._CONTEXT_LEDGER_NAME
+    row = json.loads(ledger.read_text(encoding="utf-8").strip()
+                     .split("\n")[-1])
+    assert row["prompt_cache_split"] == split
+    assert set(row) == {"task_id", "budget_chars", "est_tokens",
+                        "util_pct", "truncated", "model", "risk_tier",
+                        "prompt_cache_split"}
+
+
+def test_cache_split_stable_across_turns(tmp_path, monkeypatch):
+    _clean_routing_env(monkeypatch)
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT",
+                       str(tmp_path / "sessions"))
+    _mk_sys_prompt(tmp_path, monkeypatch)
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
+    holder = {}
+    _mk_bridge_client(monkeypatch, [_FakeResp(200, "a", _ok_payload("a")),
+                                    _FakeResp(200, "b", _ok_payload("b"))],
+                      holder=holder)
+    target = (bridge.brain_turn.fn if hasattr(bridge.brain_turn, "fn")
+              else bridge.brain_turn)
+    first = target("first-question", task_id="234")
+    second = target("second-question", task_id="234")
+    assert (first["prompt_cache_split"]["static_prefix_sha256"]
+            == second["prompt_cache_split"]["static_prefix_sha256"])
+    assert (first["prompt_cache_split"]["dynamic_suffix_sha256"]
+            != second["prompt_cache_split"]["dynamic_suffix_sha256"])
+
+
+def test_cache_split_leaks_nothing(tmp_path, monkeypatch):
+    import json
+    _clean_routing_env(monkeypatch)
+    sentinel = "cache-leak-sentinel-zz7"
+    result, _ = _run_turn_capture(
+        monkeypatch, tmp_path, _ok_payload("ok"), prompt=sentinel)
+    assert sentinel not in json.dumps(result["prompt_cache_split"])
+    ledger = tmp_path / "sessions" / bridge._CONTEXT_LEDGER_NAME
+    blob = ledger.read_text(encoding="utf-8")
+    assert sentinel not in blob
+    assert "sk-test-key" not in blob
+
+
+# --- Prompt-cache split hotfix (QA_REJECTED F1-F4 -> M1-M4, Task 247) ---
+
+def _failsafe_turn_setup(monkeypatch, tmp_path):
+    _clean_routing_env(monkeypatch)
+    _mk_tasks_root(tmp_path)
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _mk_sys_prompt(tmp_path, monkeypatch)
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
+    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
+
+
+def test_cache_split_failsafe_wires_own_slot(tmp_path, monkeypatch):
+    # M1: the failsafe branch must hash its attach in the failsafe
+    # slot, never merged into the diff slot (F1).
+    _failsafe_turn_setup(monkeypatch, tmp_path)
+    holder = {}
+    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload("ok"))],
+                      holder=holder)
+    target = (bridge.brain_turn.fn if hasattr(bridge.brain_turn, "fn")
+              else bridge.brain_turn)
+    prompt = "qa engineer, adversarial review please"
+    result = target(prompt, task_id="200", include_bundle=False)
+    hunks = bridge._failsafe_qa_attach(prompt, "200")
+    assert hunks  # guard: the failsafe really fired for this prompt
+    expected = bridge.build_prompt_cache_split(
+        "sys", "", "", prompt, diff_text="", failsafe_text=hunks,
+        history=[])
+    assert (result["prompt_cache_split"]["dynamic_suffix_sha256"]
+            == expected["dynamic_suffix_sha256"])
+    swapped = bridge.build_prompt_cache_split(
+        "sys", "", "", prompt, diff_text=hunks, failsafe_text="",
+        history=[])
+    assert (swapped["dynamic_suffix_sha256"]
+            != expected["dynamic_suffix_sha256"])
+
+
+def test_cache_split_nul_role_cannot_collide():
+    # M2: NUL-bearing history roles must not alias another segment
+    # list (F2). Old framing hashed both histories below to the same
+    # dynamic bytes: label "history[0].r" + content "q\x001\x00Y"
+    # framed identically to role "r\x005\x00q" + content "Y".
+    assert len("q\x001\x00Y") == 5  # honest length the collision pivots on
+    a = bridge.build_prompt_cache_split(**_split_kwargs(
+        history=[{"role": "r", "content": "q\x001\x00Y"}]))
+    b = bridge.build_prompt_cache_split(**_split_kwargs(
+        history=[{"role": "r\x005\x00q", "content": "Y"}]))
+    assert (a["dynamic_suffix_sha256"]
+            != b["dynamic_suffix_sha256"])
+
+
+def test_cache_split_descriptor_matches_post_truncation_wire(
+        tmp_path, monkeypatch):
+    # M3: the descriptor must describe the SHIPPED (post-truncation)
+    # wire, never the pre-truncation assembly (F3).
+    _clean_routing_env(monkeypatch)
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _mk_sys_prompt(tmp_path, monkeypatch)
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
+    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
+    monkeypatch.setattr(bridge, "_INPUT_BUDGET", 20)
+    holder = {}
+    _mk_bridge_client(monkeypatch, [_FakeResp(200, "a", _ok_payload("a")),
+                                    _FakeResp(200, "b", _ok_payload("b"))],
+                      holder=holder)
+    target = (bridge.brain_turn.fn if hasattr(bridge.brain_turn, "fn")
+              else bridge.brain_turn)
+    target("first-question", task_id="234", include_bundle=False)
+    second = target("second-question", task_id="234", include_bundle=False)
+    shipped = holder["body"]["input"]
+    shipped_history = [t for t in shipped[1:-1]]
+    assert len(shipped_history) < 2  # the middle drop really fired
+    expected = bridge.build_prompt_cache_split(
+        "sys", "", "", "second-question", history=shipped_history)
+    assert (second["prompt_cache_split"]["dynamic_suffix_sha256"]
+            == expected["dynamic_suffix_sha256"])
+    assert (second["prompt_cache_split"]["static_prefix_sha256"]
+            == expected["static_prefix_sha256"])
+
+
+def test_cache_split_static_lookup_skips_hash(monkeypatch):
+    # M4: memoization must key on the static INPUTS, not hash-then-
+    # lookup — a repeat static input must cost zero new static hashes
+    # (F4). Two identical builds: miss (static + dynamic) then hit
+    # (dynamic only) = exactly 3 sha256 calls.
+    bridge._STATIC_SPLIT_CACHE.clear()
+    real_sha256 = bridge.hashlib.sha256
+    calls = []
+
+    def counting(data=b""):
+        calls.append(1)
+        return real_sha256(data)
+
+    monkeypatch.setattr(bridge.hashlib, "sha256", counting)
+    kw = _split_kwargs()
+    first = bridge.build_prompt_cache_split(**kw)
+    second = bridge.build_prompt_cache_split(**kw)
+    assert (first["static_prefix_sha256"]
+            == second["static_prefix_sha256"])
+    assert len(calls) == 3
```
<!-- END_GIT_DIFF -->
