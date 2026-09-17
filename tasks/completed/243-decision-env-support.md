# Task 243: DECISION_* env support for decision server

**File:** `tasks/qa/243-decision-env-support.md`
**Source:** manager
**Type:** feature
**Status:** open

## Goal

Give the manager-decision server its own DECISION_API_BASE, DECISION_API_KEY, DECISION_MODEL, DECISION_REASONING_EFFORT envs (BRAIN_* fallback), and document them.

## Manager's Notes

Manager order, exact: "define and use following env too and update project docs and example and then continu your goal" with DECISION_API_BASE=https://openrouter.ai/api/v1, DECISION_API_KEY=<OpenRouter key, SECRET — never quote>, DECISION_MODEL=openai/gpt-5.6-luna, DECISION_REASONING_EFFORT=xhigh. Supersedes the earlier deepseek DECISION_MODEL value.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Wire DECISION_* reads with BRAIN_* fallback in mcp-decision-server/server.py
- [x] Set the 4 values in HQ .env (mode 600, gitignored, values never printed)
- [x] Extend .env.example DECISION section + fallback docs
- [x] Contract tests (precedence, blank-fallback, fail-closed); suite green

## Acceptance Criteria

- [x] Decision server reads all 4 DECISION_* envs, falls back to BRAIN_* when blank/unset
- [x] Missing both keys fails closed naming both env names
- [x] Docs + example updated; decision suite + full suite green

## Verification Evidence

- **Test command:** `uv tool run --with "mcp==1.4.1" --with pathspec --with pyyaml --with pytest pytest tests/ -q`
- **Expected result:** exit 0, all pass
- **Actual result:** 396 passed, zero failures (decision suite 108 incl. 3 new contract tests)
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** secret handling — key must never appear in chat, logs, diffs, or committed files
- **Rollback plan:** `git checkout -- mcp-decision-server/server.py`; unset the 4 DECISION_* lines (BRAIN_* fallback restores old behavior)

---

## Execution Log & Reasoning

Seat Check: Senior Programmer (server env wiring + contract tests). No UI/schema/sprint triggers; Designer/Planner/Strategist/QA/Reviewer skipped — small scoped wiring, judged via suites + lint. Autopilot: this task was executed under the manager's standing autopilot lock; replay lineage from stored rulings (fix-all on autopilot, zero-questions standing order).
Edits: `mcp-decision-server/server.py` — `_get_api_base()` helper (DECISION_API_BASE → BRAIN_API_BASE → default const), `_get_decision_effort()` reads DECISION_REASONING_EFFORT → BRAIN_REASONING_EFFORT, `_get_api_key()` reads DECISION_API_KEY → BRAIN_API_KEY (fail-closed names both), call site uses the helper. `DECISION_MODEL` was already read with blank-fallback (pre-existing). HQ `.env` holds all 4 values (key copied programmatically from the BRAIN key; values never printed; mode 600; gitignored). `.env.example` DECISION section extended. Tests: 3 new contract tests + 2 old tests fixed for env hermeticity. Decision suite 108 passed; full suite 396 passed, zero failures, exit 0.
- Live Brain QA verdict (gpt-5.6-luna, trunc 0): VERDICT QA_PASSED. Precedence, blank/whitespace fallback, fail-closed key, effort-only-without-temp all confirmed (CITE server.py:219,908,964; .env.example:23; tests :458). No vuln. M1/M2 = non-blocking coverage suggestions (all-four-env outbound test; whitespace BRAIN_API_BASE). Self-improvements S1 (task-scoped diff ownership) + S2 (auto env-matrix test) noted as future work.
- Reviewer verdict (gpt-5.6-luna): PO_REVIEW_PENDING — technical approval, no blocking issues; precedence, blank fallback, fail-closed key, API-base helper, reasoning config, docs all match (CITE server.py:219,908,964 + .env.example:23); no secret in diff; closure only on exact phrases.

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
```
<!-- END_GIT_DIFF -->
