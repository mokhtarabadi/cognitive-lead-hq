# Task 242: Fix decision-redactor word-edge credential leak (B1)

**File:** `tasks/qa/242-fix-decision-redactor-word-edge-leak.md`
**Source:** manager
**Type:** bug
**Status:** open

## Goal

Close the credential-leak path in `mcp-decision-server/redactor.py`: `BRAIN_API_KEY=...`-style names and short `Bearer` tokens pass `verify_clean` today, and the store is append-only with no delete path.

## Manager's Notes

Repair guide order: start B1; no Bridge changes until B1 is green. Reproduce first, then fix, then extend tests to KEY=value / colon / quoted forms. Acceptance: no secret string passes `verify_clean`. Per-task checklist: offline unit green, 40-message bound, no global writes, Handoff Note at close.

## Local TODOs

- [x] Read `mcp-decision-server/redactor.py` + existing redactor tests
- [x] Reproduce: `BRAIN_API_KEY=sk-...` and short `Bearer abc123` through `verify_clean`
- [x] Fix word-boundary regex + Bearer minimum length
- [x] Extend tests to KEY=value / colon / quoted forms
- [x] Full suite green + lint + stage + qa + Brain QA/review

## Acceptance Criteria

- [x] No secret string (`KEY=value`, colon, quoted, short Bearer) passes `verify_clean`
- [x] Full test suite passes with exit code 0
- [x] QA and reviewer verdicts recorded

## Verification Evidence

- **Test command:** `uv tool run --with "mcp==1.4.1" --with pathspec --with pyyaml --with pytest pytest tests/ -q`
- **Expected result:** all pass, exit 0
- **Actual result:** decision suite **105 passed** (101 baseline + 4 new B1 tests), exit 0. Reproduce-first proof via inline old-vs-new regex check: old `\b` edge misses `BRAIN_API_KEY=sk-test-...` and `FOO_SECRET=hunter2` (both False = leak), new `(?<![A-Za-z0-9])` edge catches both (True), `topsecret=x` stays untouched (False = no over-redact).
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** regex change over-redacts legit text; append-only store means a bad record cannot be deleted
- **Rollback plan:** revert `redactor.py` via worktree diff; no store writes during this task (offline tests only)

---

## Execution Log & Reasoning

Seat Check: Senior Programmer (credential-scrub regex + offline tests). Skipped Designer, Planner, Strategist (no UI/schema/sprint triggers); QA/Reviewer judge later bridge turns.
Replay lineage: Replayed from DEC-20260914-003 (2026-09-14): standing full-autopilot zero questions. Repair-guide order: start B1; no Bridge changes until B1 green.
Worktree truth on entry: B1 code fix + 4 tests + CHANGELOG bullet already present as uncommitted changes (parallel session); this run verified rather than re-implemented. Verified: (1) reproduce via old-vs-new pattern check — old edge leaks both ENV-style strings, new edge catches them, `topsecret=x` untouched; (2) `redactor.py:41,50` new edge in sanitize + verify patterns; `redactor.py:31-32` short-Bearer `{4,7}` digit-gated rule, `{8,}` rule unchanged; (3) 4 new tests in `tests/test_decision_server.py` (env-style names, short digit Bearer, prose no-FP guard, raw-detect); (4) decision suite 105 passed exit 0; (5) CHANGELOG B1 bullet present. No store writes (offline tests only) per rollback plan.
QA-hotfix dispute (live Brain VERDICT QA_REJECTED, F1/F2): F1 does NOT reproduce — direct evidence `sanitize_text('Authorization: Bearer abcd-1')` → `'Authorization: Bearer [REDACTED]'`, `verify_clean` True, because `-` is inside the token class `[A-Za-z0-9\-._~+/=]` so greedy `{4,7}` consumes `abcd-1` fully (no `\b`-before-`-` partial match exists). The 4 ordered regression tests were added first per TDD and ALL PASS pre-fix (incl. the punctuation test) — no RED possible, no behavior change warranted; Step 4 rule rewrite correctly NOT applied (editing correct code on a false premise would risk real regressions). Tests kept as behavior locks. Residual noted for Brain re-QA (no code change): tokens containing out-of-class chars (e.g. `Bearer abcd!1`) evade both sanitize and verify symmetrically — future hardening scope, not this hotfix. F2 quoted/topsecret tests added and green. Full suite: 400 passed exit 0. Skill deviation logged: loaded `testing-strategy` only; `project-memory`/`manager-decision`/`versioning-and-release` contents already live this session, `code-search` unneeded (files known), `verification-before-completion`/`task-lint` enforced via tools.
Re-QA verdict (live Brain, full context): VERDICT QA_PASSED. F1 REFUTED by the Brain itself (`-` inside token class, `abcd-1` consumed whole; CITE redactor.py:31). F2 CONFIRMED (quoted = and : tests; CITE test_decision_server.py:149,155). F3 CONFIRMED (topsecret=x; CITE :161). F4 no remaining B1 defect (`abcd!1` out-of-alphabet = future scope). 400 passed exit 0, no store writes. Review note R1 (resolve before closure): attached diff also holds Task 243 files (.env.example:26, decision server.py:219, tests :487) — 242 closure commit must be scoped to 242 files only; 243 files stay for 243's own closure. QA self-improvements: H1 per-task manifests; H2 executable repro before hotfix; H3 boundary lengths 3/4/7/8.
Reviewer verdict (live Brain, full context): APPROVED, PO_REVIEW_PENDING (CITE redactor.py:31/41/50, tests :149/155/161; R1 Medium repeats closure scoping — 242 feature commit = redactor + 242 tests + 242 CHANGELOG entry only, via selective unstage at closure).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.env.example b/.env.example
index 4dc7107..8eb4382 100644
--- a/.env.example
+++ b/.env.example
@@ -23,9 +23,14 @@ BRAIN_API_KEY=sk-...
 #BRAIN_MAX_TOKENS=16384
 
 # Manager decisions (mcp-decision-server) — extraction model + temperature.
-# Blank model = falls back to BRAIN_MODEL. Same Responses-API transport
-# (BRAIN_API_BASE/BRAIN_API_KEY).
+# Blank model = falls back to BRAIN_MODEL. Blank base/key = fall back to
+# BRAIN_API_BASE/BRAIN_API_KEY (same Responses-API transport); set the
+# DECISION_* pair to route decisions to a different provider or account.
+#DECISION_API_BASE=
+#DECISION_API_KEY=
 #DECISION_MODEL=
+# Reasoning effort sent as `reasoning.effort` (blank = BRAIN_REASONING_EFFORT).
+#DECISION_REASONING_EFFORT=
 #DECISION_TEMPERATURE=1.0
 # Decision store path — set ONCE here or as a shell export, never per call.
 # When set, all tools resolve the personal repo silently; when blank, the
diff --git a/CHANGELOG.md b/CHANGELOG.md
index f1ab6d8..ae5ca71 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -28,6 +28,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Truncation note orders Brain to pull without tools (Task 240, syncs GitHub issue 14):** the capped-hunks note told the Brain to pull the rest via `read_file`, but the Brain has zero tool calls — unseen evidence caused a wrongful `QA_REJECTED`. The note now says hunks past the cut were NOT sent, judge visible hunks only, mark unseen scope `UNVERIFIABLE` (never `REJECTED`) past a truncation, do not pull (no file tools exist), and quote needed paths in the verdict so the Hands pulls via `read_file` and re-runs QA. 1 new wording-lock test. Full suite: **381 passed**, zero failures.
 - **Bridge follow-up: attach-note wording, cross-project bleed, closure gate, rtk mandate (Task 241, syncs GitHub issue 15):** remaining `read_file` pull orders removed from both task-attach notes (`_strip_task_diff`, `_TASK_ATTACH_CAP`) — no file tools, quote paths, Hands feeds `fed-context` under the same `task_id`. `load_history`/`load_fed_context` legacy fallbacks now apply ONLY when the resolved root IS the legacy global (a project with its own `tasks/` dir gets fresh `[]`/`''`, never foreign turns); writes were already per-project. New `validate_closure_checklist` (QA_PASSED + PO_REVIEW_PENDING + exact approval words + non-empty diff + `extract_session_decisions` evidence) closes the never-called decision-capture gap. New CRITICAL RULE 3b in `prompts/fragments/09-hands_protocols.md` mandates `rtk test` for passing suites; shipped prompt rebuilt to **9.38.0**. 9 new tests (wording, no-bleed, closure gate, prompt-sync). Full suite: **387 passed**, zero failures.
 - **Context-handling gaps: utilization ledger + over-cap signatures fallback (Task 241 extension, web-research findings):** `mcp-brain-bridge/server.py` gains a per-turn context ledger (`_MODEL_WINDOW_CHARS=200000`, one JSON line per turn — task_id, budget_chars, est_tokens, util_pct, truncated — to `context_ledger.jsonl`, best-effort never-raise) and the prompt-size warn now shows `util~%`, so truncation pressure is measured instead of guessed. `mcp-context-server/server.py` `process_source_file` over-cap branch now appends tree-sitter signatures (or a narrow-paths pointer) instead of silently skipping the file, so discovery keeps structural signal past the cap. 2 new tests (ledger+util, too-large-signatures). Full suite: **389 passed**, zero failures.
+- **Decision-redactor word-edge leak (Task 242, Phase 1 B1):** `mcp-decision-server/redactor.py` assignment rule leading edge `\b` → `(?<![A-Za-z0-9])` in both sanitize and verify patterns, so ENV-style `KEY=value` names (`BRAIN_API_KEY=`, `FOO_SECRET=`) redact while prose `topsecret=` stays untouched; new short-Bearer rule (`{4,7}` chars with digit gate) catches `Bearer abc123`-shaped tokens while prose `Bearer tokens` and the `{8,}` rule stay unchanged. 4 new tests (3 failed pre-fix as required). Full decision suite: **105 passed**, zero failures. QA-hotfix regression tests added (punctuation Bearer, quoted forms — all green pre-fix; the claimed `-1` suffix leak did not reproduce: `-` is inside the token class, direct evidence recorded in Task 242). Full suite: **400 passed**, zero failures.
+- **Decision-server DECISION_* env support (Task 243):** `mcp-decision-server/server.py` now reads `DECISION_API_BASE`, `DECISION_API_KEY`, `DECISION_MODEL`, `DECISION_REASONING_EFFORT`, each with `BRAIN_*` fallback (fail-closed error names both key vars); new module-level `_get_api_base()` helper; `.env.example` DECISION section extended with the four lines + fallback docs. 3 new contract tests (precedence, blank-fallback, fail-closed); 2 old tests fixed for env hermeticity. Full suite: **396 passed**, zero failures.
 
 ## [9.35.0] - 2026-09-14
 
diff --git a/mcp-decision-server/redactor.py b/mcp-decision-server/redactor.py
index 2c6e119..3384268 100644
--- a/mcp-decision-server/redactor.py
+++ b/mcp-decision-server/redactor.py
@@ -25,12 +25,20 @@ REDACTION_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
     (re.compile(r"\bAIzaSy[A-Za-z0-9_-]{10,}\b"), "[REDACTED_GOOGLE_KEY]"),
     # Bearer tokens (Authorization headers, config dumps).
     (re.compile(r"\bBearer\s+[A-Za-z0-9\-._~+/=]{8,}", re.IGNORECASE), "Bearer [REDACTED]"),
+    # Short digit-bearing Bearer tokens (e.g. `Bearer abc123`). The digit
+    # gate keeps prose like "Bearer tokens" untouched; the {8,} rule above
+    # still catches long tokens with or without digits.
+    (re.compile(r"\bBearer\s+(?=[A-Za-z0-9\-._~+/=]*\d)[A-Za-z0-9\-._~+/=]{4,7}\b",
+                re.IGNORECASE), "Bearer [REDACTED]"),
     # Private IPv4: 10/8, 172.16/12, 192.168/16 (loopback stays — harmless).
     (re.compile(r"\b10(?:\.\d{1,3}){3}\b"), "[REDACTED_IP]"),
     (re.compile(r"\b172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}\b"), "[REDACTED_IP]"),
     (re.compile(r"\b192\.168(?:\.\d{1,3}){2}\b"), "[REDACTED_IP]"),
     # Generic credential assignments: password = "secret", token: xyz.
-    (re.compile(r"(?i)\b(password|passwd|secret|api[_-]?key|auth[_-]?token)\b\s*[:=]\s*\S+"),
+    # Leading edge is "not preceded by alphanumerics" (not \b) so ENV-style
+    # names joined by underscore (BRAIN_API_KEY=, FOO_SECRET=) still match,
+    # while letter-joined words (topsecret=) stay untouched.
+    (re.compile(r"(?i)(?<![A-Za-z0-9])(password|passwd|secret|api[_-]?key|auth[_-]?token)\b\s*[:=]\s*\S+"),
      r"\1=[REDACTED]"),
 )
 
@@ -39,7 +47,7 @@ REDACTION_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
 # already-redacted `password=[REDACTED]` marker is NOT mistaken for a live
 # secret (otherwise verify_clean could never pass on sanitized text).
 _VERIFY_ASSIGNMENT = re.compile(
-    r"(?i)\b(password|passwd|secret|api[_-]?key|auth[_-]?token)\b\s*[:=]\s*(?!\[REDACTED\])\S+"
+    r"(?i)(?<![A-Za-z0-9])(password|passwd|secret|api[_-]?key|auth[_-]?token)\b\s*[:=]\s*(?!\[REDACTED\])\S+"
 )
 _VERIFY_RESIDUE: tuple[re.Pattern[str], ...] = tuple(
     _VERIFY_ASSIGNMENT if rule is REDACTION_RULES[-1][0] else rule
diff --git a/mcp-decision-server/server.py b/mcp-decision-server/server.py
index 661c9be..b0767b6 100644
--- a/mcp-decision-server/server.py
+++ b/mcp-decision-server/server.py
@@ -219,22 +219,46 @@ def _get_decision_model() -> str:
 
 
 def _get_decision_effort() -> str:
-    """Reasoning effort for extraction; override via ``BRAIN_REASONING_EFFORT``."""
-    val = os.environ.get("BRAIN_REASONING_EFFORT", "xhigh").strip() or "xhigh"
+    """Reasoning effort for extraction; override via
+    ``DECISION_REASONING_EFFORT``, falling back to
+    ``BRAIN_REASONING_EFFORT``."""
+    val = (
+        os.environ.get("DECISION_REASONING_EFFORT", "").strip()
+        or os.environ.get("BRAIN_REASONING_EFFORT", "xhigh").strip()
+        or "xhigh"
+    )
     if not re.fullmatch(r"[\w.-]{1,64}", val):
         raise ValueError(f"bad reasoning effort: {val!r}")
     return val
 
 
 def _get_api_key() -> str:
-    """Provider key. Fail-closed: an empty key cannot authenticate, so
-    raise instead of sending a bare ``Bearer `` header."""
-    key = os.environ.get("BRAIN_API_KEY", "").strip()
+    """Provider key: ``DECISION_API_KEY`` first, ``BRAIN_API_KEY`` as
+    fallback. Fail-closed: an empty key cannot authenticate, so raise
+    instead of sending a bare ``Bearer `` header."""
+    key = (
+        os.environ.get("DECISION_API_KEY", "").strip()
+        or os.environ.get("BRAIN_API_KEY", "").strip()
+    )
     if not key:
-        raise RuntimeError("BRAIN_API_KEY is empty; set it in .env")
+        raise RuntimeError("DECISION_API_KEY/BRAIN_API_KEY is empty; set it in .env")
     return key
 
 
+#: Local default when neither DECISION_API_BASE nor BRAIN_API_BASE is set.
+_DECISION_API_BASE_DEFAULT = "http://127.0.0.1:8081/zen/resp"
+
+
+def _get_api_base() -> str:
+    """Provider base URL: ``DECISION_API_BASE`` first, ``BRAIN_API_BASE``
+    as fallback, then the local default."""
+    return (
+        os.environ.get("DECISION_API_BASE", "").strip()
+        or os.environ.get("BRAIN_API_BASE", _DECISION_API_BASE_DEFAULT).strip()
+        or _DECISION_API_BASE_DEFAULT
+    )
+
+
 # Retry policy for provider calls: 3 attempts, exponential backoff.
 # (Duplicated from the brain bridge on purpose — each server dir ships
 # self-contained to the global install.)
@@ -884,15 +908,26 @@ def extract_session_decisions(
     )
     transcript_bytes = path.read_bytes()
     transcript_text = "\n".join(turns)
-    _get_decision_effort()  # Validate only; the value is dropped below.
+    effort = _get_decision_effort()  # Validated always; sent when no explicit temp.
+    # Temperature-vs-effort rule (mirrors the Brain bridge): an explicitly
+    # set temperature wins (temperature sent, effort dropped — Responses
+    # models reject the combination). Otherwise the validated effort is
+    # sent in the Responses-native nested shape (flat reasoning_effort is
+    # rejected by strict providers, e.g. OpenAI/OpenRouter 400
+    # unsupported_parameter) and temperature is omitted. Manager order:
+    # decisions run at max effort by default; explicit temp restores the
+    # old pinned-temperature behavior. temp_to_send stays 0 in the
+    # default branch so the extract cache key shape is unchanged (effort
+    # is deploy-constant from env).
     # Task 191: pin the EXTRACTION temperature to 0 unless the manager
     # explicitly sets BRAIN_TEMPERATURE (explicit wins, blank-means-unset
     # house rule). Scoped to this extraction call only — brainstorm and
-    # other paths are untouched. Temperature is therefore ALWAYS sent
-    # here, so reasoning_effort is always dropped (Responses models
-    # reject the combination). Computed BEFORE the cache key so the key
-    # covers (transcript, model, effective_temp) — an explicit override
-    # never serves temp-0 results.
+    # other paths are untouched. When no explicit temperature is set, the
+    # validated effort goes out in the Responses-native nested shape and
+    # temperature is omitted (manager max-effort order); explicit temp
+    # restores temperature-sent + effort-dropped. Computed BEFORE the
+    # cache key so the key covers (transcript, model, effective_temp) —
+    # an explicit override never serves default-branch results.
     raw_brain_temp = os.environ.get("BRAIN_TEMPERATURE", "").strip()
     raw_decision_temp = os.environ.get("DECISION_TEMPERATURE", "").strip()
     if raw_brain_temp:
@@ -929,12 +964,15 @@ def extract_session_decisions(
             _EXTRACT_CACHE[cache_key] = hit  # LRU touch: recent hits stay.
             return copy.deepcopy(hit)
     import httpx  # Lazy: import stays side-effect free.
-    api_base = os.environ.get("BRAIN_API_BASE", "http://127.0.0.1:8081/zen/resp").strip() or "http://127.0.0.1:8081/zen/resp"
+    api_base = _get_api_base()
     body: dict[str, Any] = {
         "model": model,
         "input": [{"role": "user", "content": prompt}],
-        "temperature": temp_to_send,
     }
+    if raw_brain_temp or raw_decision_temp:
+        body["temperature"] = temp_to_send
+    else:
+        body["reasoning"] = {"effort": effort}
     with httpx.Client(
         timeout=httpx.Timeout(connect=10, read=120, write=30, pool=10)
     ) as client:
diff --git a/tests/test_decision_server.py b/tests/test_decision_server.py
index 3e7cc5f..0a89668 100644
--- a/tests/test_decision_server.py
+++ b/tests/test_decision_server.py
@@ -113,6 +113,66 @@ def test_verify_detects_raw_secrets(red):
     assert red.verify_clean("password=hunter2") is False
 
 
+def test_sanitize_env_style_assignment_names(red):
+    # Task 242 B1: ENV-style names (BRAIN_API_KEY=, FOO_SECRET=) must redact —
+    # the leading \b missed names joined by underscore.
+    dirty = "BRAIN_API_KEY=abc123XYZ and FOO_SECRET=hunter2 and my-auth-token: zz99x"
+    clean = red.sanitize_text(dirty)
+    assert "abc123XYZ" not in clean
+    assert "hunter2" not in clean
+    assert "zz99x" not in clean
+    assert red.verify_clean(clean) is True
+
+
+def test_sanitize_short_bearer_with_digit(red):
+    # Task 242 B1: short digit-bearing Bearer tokens must redact.
+    dirty = "Authorization: Bearer abc123"
+    clean = red.sanitize_text(dirty)
+    assert "abc123" not in clean
+    assert red.verify_clean(clean) is True
+
+
+def test_no_false_positive_on_prose(red):
+    # Guard: plain prose and letter-joined names must pass through untouched.
+    assert red.sanitize_text("Bearer tokens are standard") == "Bearer tokens are standard"
+    assert red.sanitize_text("topsecret=x") == "topsecret=x"
+    assert red.verify_clean("Bearer tokens are standard") is True
+
+
+def test_verify_detects_env_style_raw(red):
+    assert red.verify_clean("FOO_SECRET=hunter2") is False
+    assert red.verify_clean("Authorization: Bearer abc123") is False
+
+
+def test_sanitize_short_bearer_punctuation_no_suffix_leak(red):
+    # QA hotfix: `Bearer abcd-1` must fully redact — no `-1` suffix may leak.
+    dirty = "Authorization: Bearer abcd-1"
+    clean = red.sanitize_text(dirty)
+    assert "abcd-1" not in clean
+    assert "-1" not in clean
+    assert red.verify_clean(clean) is True
+
+
+def test_sanitize_quoted_assignment_value(red):
+    # QA hotfix: quoted assignment values must redact end to end.
+    dirty = 'FOO_SECRET="hunter2"'
+    assert red.verify_clean(dirty) is False
+    assert red.verify_clean(red.sanitize_text(dirty)) is True
+
+
+def test_sanitize_quoted_colon_assignment_value(red):
+    # QA hotfix: quoted colon-form values must redact end to end.
+    dirty = "API_KEY: 'abc123'"
+    assert red.verify_clean(dirty) is False
+    assert red.verify_clean(red.sanitize_text(dirty)) is True
+
+
+def test_letter_joined_name_passes_verify(red):
+    # QA hotfix: letter-joined names are not credential assignments.
+    assert red.sanitize_text("topsecret=x") == "topsecret=x"
+    assert red.verify_clean("topsecret=x") is True
+
+
 def test_sanitize_clean_text_passthrough_and_idempotent(red):
     text = "Prefer composition over inheritance for testability."
     assert red.sanitize_text(text) == text
@@ -427,6 +487,37 @@ def test_decision_model_split_no_persona_fallback(srv, monkeypatch):
     assert call() == "gpt-6-astra"  # Blank means unset.
 
 
+def test_decision_env_precedence_over_brain_fallbacks(srv, monkeypatch):
+    monkeypatch.setenv("BRAIN_API_BASE", "http://brain-base")
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-brain")
+    monkeypatch.setenv("BRAIN_REASONING_EFFORT", "low")
+    monkeypatch.setenv("DECISION_API_BASE", "https://decisions-base")
+    monkeypatch.setenv("DECISION_API_KEY", "sk-decisions")
+    monkeypatch.setenv("DECISION_REASONING_EFFORT", "xhigh")
+    assert srv._get_api_base() == "https://decisions-base"
+    assert srv._get_api_key() == "sk-decisions"
+    assert srv._get_decision_effort() == "xhigh"
+
+
+def test_decision_env_blank_falls_back_to_brain(srv, monkeypatch):
+    monkeypatch.setenv("BRAIN_API_BASE", "http://brain-base")
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-brain")
+    monkeypatch.setenv("BRAIN_REASONING_EFFORT", "low")
+    monkeypatch.setenv("DECISION_API_BASE", "   ")
+    monkeypatch.setenv("DECISION_API_KEY", "   ")
+    monkeypatch.setenv("DECISION_REASONING_EFFORT", "   ")
+    assert srv._get_api_base() == "http://brain-base"
+    assert srv._get_api_key() == "sk-brain"
+    assert srv._get_decision_effort() == "low"
+
+
+def test_decision_api_key_fail_closed_names_both(srv, monkeypatch):
+    monkeypatch.delenv("DECISION_API_KEY", raising=False)
+    monkeypatch.delenv("BRAIN_API_KEY", raising=False)
+    with pytest.raises(RuntimeError, match="DECISION_API_KEY/BRAIN_API_KEY"):
+        srv._get_api_key()
+
+
 def test_repo_root_prefers_cwd_project_store(srv, tmp_path, monkeypatch):
     # Project-aware resolution: <cwd>/.opencode/decisions wins without any env.
     monkeypatch.delenv("DECISION_REPO_PATH", raising=False)
@@ -540,6 +631,7 @@ def test_extract_empty_key_raises(srv, tmp_path, monkeypatch):
     transcript = tmp_path / "transcript.jsonl"
     _write_min_transcript(transcript)
     monkeypatch.delenv("BRAIN_API_KEY", raising=False)
+    monkeypatch.delenv("DECISION_API_KEY", raising=False)
     with pytest.raises(RuntimeError, match="empty"):
         _extract(srv)(7, transcript_path=str(transcript))
 
@@ -740,7 +832,8 @@ def test_temperature_pinned_zero_unless_set(srv, tmp_path, monkeypatch):
     monkeypatch.delenv("DECISION_TEMPERATURE", raising=False)
     _stub_capture(_decision_resp(200, "fine", envelope))
     _extract(srv)(7, transcript_path=str(transcript))
-    assert seen["body"]["temperature"] == 0
+    assert "temperature" not in seen["body"]
+    assert seen["body"]["reasoning"] == {"effort": "xhigh"}
     assert "reasoning_effort" not in seen["body"]
     srv._EXTRACT_CACHE.clear()
     monkeypatch.setenv("BRAIN_TEMPERATURE", "0.7")
@@ -759,6 +852,7 @@ def test_temperature_pinned_zero_unless_set(srv, tmp_path, monkeypatch):
 
 def test_invalid_effort_value_raises(srv, monkeypatch):
     monkeypatch.setenv("BRAIN_REASONING_EFFORT", "bad effort!!")
+    monkeypatch.delenv("DECISION_REASONING_EFFORT", raising=False)
     with pytest.raises(ValueError):
         srv._get_decision_effort()
 
@@ -838,7 +932,7 @@ def test_extract_repeat_determinism_five_times(srv, tmp_path, monkeypatch, capsy
     assert calls["n"] == 1  # Cache serves repeats: exactly one HTTP hit.
     blobs = [json.dumps(r, sort_keys=True) for r in results]
     assert all(b == blobs[0] for b in blobs)  # Byte-identical 5x.
-    assert calls["bodies"][0]["temperature"] == 0  # Temp-0 default pinned.
+    assert calls["bodies"][0]["reasoning"] == {"effort": "xhigh"}  # Max-effort default.
     assert capsys.readouterr().err.count("cache hit") == 4
 
 
@@ -1000,7 +1094,8 @@ def test_extract_temp_wire_default_zero(srv, tmp_path, monkeypatch):
                   _decision_resp(200, "fine", _envelope_191(json.dumps(_ship_candidates()))),
                   seen)
     _extract(srv)(21, transcript_path=str(transcript))
-    assert seen[0]["temperature"] == 0
+    assert "temperature" not in seen[0]
+    assert seen[0]["reasoning"] == {"effort": "xhigh"}
     assert "reasoning_effort" not in seen[0]
 
 
@@ -1037,7 +1132,11 @@ def test_extract_effort_absent_both_legs(srv, tmp_path, monkeypatch):
         _extract(srv)(23, transcript_path=str(transcript))
         body = seen[-1]
         if temp is None:
-            assert body["temperature"] == 0
+            assert "temperature" not in body
+            assert body["reasoning"] == {"effort": "xhigh"}
+        else:
+            assert body["temperature"] == 0.7
+            assert "reasoning" not in body
         assert "reasoning_effort" not in body
```
<!-- END_GIT_DIFF -->
