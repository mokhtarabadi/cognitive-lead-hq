# Task 265: Harden Responses API transport (HTTPS guard + configurable read timeout)

**File:** `tasks/qa/265-harden-responses-transport-https-and-read-timeout.md`
**Source:** manager
**Type:** bug
**Status:** open

## Goal

Close gaps R1 and R2 from the Responses API audit in BOTH MCP servers
(`mcp-brain-bridge/server.py`, `mcp-decision-server/server.py`):

- R1: the provider base URL (`BRAIN_API_BASE` / `DECISION_API_BASE`) is read
  from the environment with no scheme check. An `http://` value sends the
  Bearer API key in cleartext. Fail closed on any non-HTTPS base, allowing
  plain HTTP only for loopback hosts (local proxy).
- R2: the httpx read timeout is a fixed 120s for a non-streaming call. A
  high-effort reasoning turn can exceed that and be aborted. Make the read
  timeout configurable (`BRAIN_HTTP_READ_TIMEOUT` /
  `DECISION_HTTP_READ_TIMEOUT`) with a higher default of 600s; leave
  connect/write/pool unchanged.

## Manager's Notes

- Findings come from the read-only Responses API audit; only R1 and R2 were
  approved. R3-R7 stay deferred until separately tasked.
- Both server files ship self-contained to the global install, so the helper
  is duplicated in each by design (same pattern as the retry constants).
- ZAC applies: no `git add`/`commit`/`push`; staging goes through the MCP tool.

## Local TODOs

- [x] Add an HTTPS-scheme guard helper to both servers
- [x] Apply it in brain `_responses_url()`
- [x] Apply it in decision `_get_api_base()`
- [x] Add a configurable read-timeout helper to both servers and wire it into the HTTP client
- [x] Document both knobs in `.env.example`
- [x] Add focused tests for the guard and the timeout parser
- [x] Run the full test suite

## Acceptance Criteria

- [x] Both servers reject an `http://` non-loopback base with a fail-closed error naming the env key.
- [x] `http://localhost` and `http://127.0.0.1` bases remain allowed (loopback only).
- [x] An `https://` base passes through unchanged.
- [x] Read timeout is configurable by env with a 600s default; a malformed or non-positive value fails loud.
- [x] connect/write/pool timeouts are unchanged.
- [x] `.env.example` documents both new knobs.
- [x] Full test suite passes with exit code 0.

## Verification Evidence

- **Test command:** rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
- **Expected result:** all tests pass
- **Actual result:** 686 passed, 10 warnings in 4.75s
- **Exit code:** 0

> Verification runner rule: the command above is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; a raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true:

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** A too-strict guard could break a legitimate local-proxy setup, or the longer timeout could make a hung request take longer to fail.
- **Rollback plan:** Revert the two server files (and `.env.example`) to the pre-change state; the edits are additive and self-contained.

---

## Execution Log & Reasoning

### Scope

Fixes gaps R1 and R2 from the read-only Responses-API audit, in both
Responses-API MCP servers. R3-R7 stay deferred (not approved).

### Changes

1. `mcp-brain-bridge/server.py`
   - Added `from urllib.parse import urlsplit`.
   - Added `_https_guard(base, env_key)` — returns `https://` bases
     unchanged; allows `http://` only for loopback hosts
     (`localhost`, `127.0.0.1`, `::1`); otherwise raises `RuntimeError`
     naming the env key.
   - Added `_get_read_timeout()` — reads `BRAIN_HTTP_READ_TIMEOUT`
     (default `600`), float-parses, raises on a non-number or `<= 0`.
   - `_make_client()` now uses `read=_get_read_timeout()`
     (connect/write/pool unchanged at 10/30/10).
   - `_responses_url()` calls `_https_guard(base, "BRAIN_API_BASE")`.
2. `mcp-decision-server/server.py`
   - Added `from urllib.parse import urlsplit`.
   - Added `_https_guard(base, env_key)` and `_get_decision_read_timeout()`
     (reads `DECISION_HTTP_READ_TIMEOUT`, default `600`).
   - `_get_api_base()` resolves the base then returns
     `_https_guard(base, "DECISION_API_BASE/BRAIN_API_BASE")`.
   - The extraction `httpx.Client(...)` uses
     `read=_get_decision_read_timeout()`.
3. `.env.example` — documents the https requirement on `BRAIN_API_BASE`
   and adds `#BRAIN_HTTP_READ_TIMEOUT=600` and
   `#DECISION_HTTP_READ_TIMEOUT=600`.

### Assumptions

- A1: The helper is duplicated in both servers by design; they ship
  self-contained to the global install (same pattern as the retry
  constants), so no shared import was introduced.
- A2: Loopback exemption covers `localhost`, `127.0.0.1`, and `::1` —
  the common local-proxy forms — and nothing else.
- A3: `600` is the new default read timeout; it is env-overridable, so a
  slower endpoint can raise it without a code change.

### Test-suite hermeticity fix

Both servers call `load_env_files()` at import, so the developer's real
gitignored `.env` leaked into assertions. Added
`monkeypatch.delenv` for `BRAIN_REASONING_EFFORT` + `BRAIN_MAX_TOKENS`
(in `_clean_routing_env`) and for `DECISION_MAX_TOKENS` (three decision
tests), and re-pointed two pre-existing tests that asserted the old
`http://` passthrough to loopback/https.

### Verification

- `rtk test uv run --with pytest ... pytest tests/ -q` -> first run
  `7 failed, 679 passed` (all 7 pre-existing env-leak / old-passthrough
  expectations, none from the new logic), second run `2 failed, 684
  passed`, final run **686 passed, exit 0**.

### ZAC

No `git add`/`commit`/`push`. Staging goes through
`custom_context_stage_and_inject_diff` only.

### QA + Review turns (Brain Bridge, autopilot)

- **QA (stage=qa, include_diff) -> `QA_PASSED`.** Confirmed the guard and
  timeout wiring in both servers. Non-blocking gaps noted: the `::1`
  allow path has no direct test; `nan`/`inf` timeout values are not
  explicitly rejected (the `<= 0` check does not catch `nan`); no mock
  assertion on the httpx Client wiring.
- **Review (stage=review, include_diff) -> technical `APPROVED`, status
  `PO_REVIEW_PENDING`.** Findings I1-I4 all Low/Info: `nan`/`inf` parser
  edge, error text names only `localhost` while code also allows
  `127.0.0.1`/`::1`, missing direct `::1` test, helper names differ
  across servers. Reviewer recommended accepting the change now and
  hardening the `nan`/`inf` and text gaps in a future task.
- Awaiting the Manager's explicit closure words; R3-R7 remain deferred.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.env.example b/.env.example
index 3cf6311..605a50a 100644
--- a/.env.example
+++ b/.env.example
@@ -1,6 +1,8 @@
 # Unified LLM Provider (Responses API: POST {BRAIN_API_BASE}/responses).
-# Key here is a placeholder — put the real key in your private `.env`
-# (git-ignored, never committed).
+# Must be https:// — plain http:// is allowed only for localhost/127.0.0.1
+# (a local proxy); any other http:// base is refused so the API key never
+# travels in cleartext. Key here is a placeholder — put the real key in
+# your private `.env` (git-ignored, never committed).
 BRAIN_API_BASE=https://api.openai.com/v1
 BRAIN_API_KEY=sk-...
 
@@ -25,6 +27,11 @@ BRAIN_API_KEY=sk-...
 # output and count against this cap, so keep it well above the expected
 # reasoning length.
 #BRAIN_MAX_TOKENS=32768
+# HTTP read timeout (seconds) for the non-streaming provider call (default
+# 600). Reasoning models can think for minutes before the single response
+# body arrives, so a fixed low ceiling aborts valid high-effort turns.
+# Malformed or non-positive values fail loud.
+#BRAIN_HTTP_READ_TIMEOUT=600
 
 # Manager decisions (mcp-decision-server) — extraction model + temperature.
 # Blank model = falls back to BRAIN_MODEL. Blank base/key = fall back to
@@ -41,6 +48,9 @@ BRAIN_API_KEY=sk-...
 # default in place). Must be a positive integer — a malformed, zero or
 # negative value fails the call with a ValueError naming the variable.
 #DECISION_MAX_TOKENS=16384
+# HTTP read timeout (seconds) for the extraction call (default 600). This
+# knob is independent of BRAIN_HTTP_READ_TIMEOUT.
+#DECISION_HTTP_READ_TIMEOUT=600
 # Extraction sampling temperature (default 1.0; blank leaves the default
 # in place). Must be a number in the inclusive range 0.0-2.0 — a malformed
 # or out-of-range value fails the call with a ValueError.
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 41e6d32..b6c7420 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -30,6 +30,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Fixed
 
+- **Responses transport hardened: HTTPS-only provider base + configurable read timeout (Task 265):** the read-only Responses-API audit found two transport gaps in BOTH MCP servers and they are now closed. (R1) The provider base (`BRAIN_API_BASE` / `DECISION_API_BASE`) was read from the environment with no scheme check, so an `http://` value sent the Bearer API key in cleartext; a new `_https_guard(base, env_key)` returns an `https://` base unchanged, allows plain `http://` only for loopback hosts (`localhost`, `127.0.0.1`, `::1` — local proxies keep working), and otherwise raises a fail-closed `RuntimeError` naming the env key. It is applied in the brain `_responses_url()` and in the decision `_get_api_base()`. (R2) The httpx read timeout was a fixed 120s for a non-streaming call that also carries reasoning tokens, so a high-effort turn could be aborted mid-flight; the read timeout is now env-configurable via `BRAIN_HTTP_READ_TIMEOUT` / `DECISION_HTTP_READ_TIMEOUT` (default `600`, parsed as a float, fail-loud on a non-number or a value `<= 0`) while connect/write/pool stay 10/30/10. Both servers ship self-contained to the global install, so the helper is duplicated in each by design (same pattern as the retry constants). `.env.example` documents the https requirement and both new knobs. 16 new offline tests (guard allow/reject, url/base application, timeout default/override/malformed/non-positive in both suites). The suite was also made honest about the gitignored `.env`: routing and max-token tests now clear `BRAIN_REASONING_EFFORT`, `BRAIN_MAX_TOKENS`, and `DECISION_MAX_TOKENS` so a developer's real env no longer leaks into assertions. Full suite: **686 passed**.
+
 - **Brain Bridge resolves the active project root for the bundle and file-pull tools (Task 264, fixes GitHub issue 24):** the auto-attached context bundle (`kind: "bundle"`) and the Hand-facing file-pull tools always read from the bridge INSTALL directory unless `BRAIN_WORKSPACE_ROOT` was exported, so real project docs (`docs/conventions.md`, `docs/architecture.md`, `docs/data_model.md`, `DESIGN.md`) were marked `[missing]` on every `brain_turn` in any other project. `_build_context_bundle()` now takes an optional `root`; `_workspace_root()` no longer defaults to the install dir — it keeps the explicit `BRAIN_WORKSPACE_ROOT` override first, then auto-resolves the ACTIVE project root via `preflight.resolve_project_root` (`BRAIN_PROJECT_ROOT`, then a cwd `tasks/` walk-up), and only falls back to the install dir as a loud stderr-noted last resort. The bundle call site in `brain_turn` now passes the turn's already-resolved project root, and because `preflight` deliberately drops an explicit root on one-off (unbound) turns, the `brain_turn` boundary re-pins it for the bundle and file-pull attaches when it is an existing directory. A new `_explicit_root` helper threads the same root through `get_context_bundle`, `read_file`, and `grep_files`, which all gained an optional `project_root` argument; the single `_workspace_root()` change also corrects `_resolve_under_root`, `_paths_base`, and the workspace fallback in `_resolve_task_file`. 5 new regression tests (explicit root beats an env decoy, tool-level root pin, cwd walk-up, read+grep root pin, end-to-end one-off `brain_turn`). Full bridge suite: **243 passed**; all bridge-adjacent suites: **411 passed**.
 
 - **Decision server bounds the transcript prompt and fails loudly on a bad config value (Task 263):** the extraction call joined the whole session transcript into its prompt with no ceiling, so a long session produced an unbounded request — the same starvation class as issue 23 — and two config readers silently papered over a bad setting instead of reporting it. `extract_session_decisions()` now caps the joined transcript at `DECISION_TRANSCRIPT_MAX_CHARS` (default 131072 characters, blank-means-unset) BEFORE the prompt is built, keeping the first N characters and appending `[...truncated at <dropped> chars]` so the caller learns exactly how much was dropped; `transcript_bytes` stays the raw file content used by the cache key. `_get_decision_max_tokens()` (default 16384) and `_get_decision_temperature()` (default 1.0, range 0.0-2.0) now raise `ValueError` naming the variable and the bad value instead of falling back to 16384 or clamping to 1.0. The Responses request shape is unchanged (`model`, `input`, `max_output_tokens`, plus either `temperature` or nested `reasoning.effort`). 5 new tests. Full suite: **665 passed**.
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index bbc9178..77d5e00 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -49,6 +49,7 @@ import sys
 import json
 from pathlib import Path
 from typing import Any, Optional
+from urllib.parse import urlsplit
 
 from mcp.server.fastmcp import FastMCP
 
@@ -1509,12 +1510,49 @@ def _resp_json(resp: Any) -> Any:
         ) from exc
 
 
+def _https_guard(base: str, env_key: str) -> str:
+    """Fail closed on a provider base that would leak the Bearer key.
+
+    HTTPS is always allowed. Plain HTTP is allowed ONLY for loopback hosts
+    (a local proxy), where the bytes never leave the machine. Anything else
+    raises instead of shipping the API key in cleartext over the network.
+    """
+    parsed = urlsplit(base)
+    if parsed.scheme == "https":
+        return base
+    host = (parsed.hostname or "").lower()
+    if parsed.scheme == "http" and host in {"localhost", "127.0.0.1", "::1"}:
+        return base
+    raise RuntimeError(
+        f"{env_key}={base!r} must use https:// (http:// is allowed only for "
+        f"localhost); refusing to send the API key in cleartext"
+    )
+
+
+def _get_read_timeout() -> float:
+    """Read timeout (seconds) for the non-streaming provider call.
+
+    Override via ``BRAIN_HTTP_READ_TIMEOUT`` (default 600). Reasoning models
+    can think for minutes before the single response body arrives, so a fixed
+    120s ceiling aborted valid high-effort turns. Malformed or non-positive
+    values fail loud rather than silently falling back.
+    """
+    raw = os.environ.get("BRAIN_HTTP_READ_TIMEOUT", "600").strip() or "600"
+    try:
+        val = float(raw)
+    except ValueError:
+        raise RuntimeError(f"BRAIN_HTTP_READ_TIMEOUT must be a number, got {raw!r}")
+    if val <= 0:
+        raise RuntimeError(f"BRAIN_HTTP_READ_TIMEOUT must be > 0, got {raw!r}")
+    return val
+
+
 def _make_client() -> Any:
     """Build the provider HTTP client (lazy httpx: imports stay offline)."""
     import httpx
 
     return httpx.Client(
-        timeout=httpx.Timeout(connect=10, read=120, write=30, pool=10)
+        timeout=httpx.Timeout(connect=10, read=_get_read_timeout(), write=30, pool=10)
     )
 
 
@@ -3317,6 +3355,7 @@ def _responses_url() -> str:
     """Responses endpoint; override via ``BRAIN_API_BASE``."""
     default = "https://api.openai.com/v1"
     base = os.environ.get("BRAIN_API_BASE", default).strip() or default
+    base = _https_guard(base, "BRAIN_API_BASE")
     return base.rstrip("/") + "/responses"
 
 
diff --git a/mcp-decision-server/server.py b/mcp-decision-server/server.py
index 1907de7..b934659 100644
--- a/mcp-decision-server/server.py
+++ b/mcp-decision-server/server.py
@@ -38,6 +38,7 @@ import unicodedata
 from datetime import datetime, timezone
 from pathlib import Path
 from typing import Any, Optional, Union
+from urllib.parse import urlsplit
 
 from mcp.server.fastmcp import FastMCP
 
@@ -370,14 +371,55 @@ def _get_api_key() -> str:
 _DECISION_API_BASE_DEFAULT = "https://api.openai.com/v1"
 
 
+def _https_guard(base: str, env_key: str) -> str:
+    """Fail closed on a provider base that would leak the Bearer key.
+
+    HTTPS is always allowed. Plain HTTP is allowed ONLY for loopback hosts
+    (a local proxy), where the bytes never leave the machine. Anything else
+    raises instead of shipping the API key in cleartext over the network.
+    """
+    parsed = urlsplit(base)
+    if parsed.scheme == "https":
+        return base
+    host = (parsed.hostname or "").lower()
+    if parsed.scheme == "http" and host in {"localhost", "127.0.0.1", "::1"}:
+        return base
+    raise RuntimeError(
+        f"{env_key}={base!r} must use https:// (http:// is allowed only for "
+        f"localhost); refusing to send the API key in cleartext"
+    )
+
+
 def _get_api_base() -> str:
     """Provider base URL: ``DECISION_API_BASE`` first, ``BRAIN_API_BASE``
-    as fallback, then the local default."""
-    return (
+    as fallback, then the local default. The resolved base must pass the
+    HTTPS guard so the Bearer key never travels in cleartext."""
+    base = (
         os.environ.get("DECISION_API_BASE", "").strip()
         or os.environ.get("BRAIN_API_BASE", _DECISION_API_BASE_DEFAULT).strip()
         or _DECISION_API_BASE_DEFAULT
     )
+    return _https_guard(base, "DECISION_API_BASE/BRAIN_API_BASE")
+
+
+def _get_decision_read_timeout() -> float:
+    """Read timeout (seconds) for the non-streaming provider call.
+
+    Override via ``DECISION_HTTP_READ_TIMEOUT`` (default 600). Reasoning
+    models can think for minutes before the single response body arrives, so
+    a fixed 120s ceiling aborted valid high-effort turns. Malformed or
+    non-positive values fail loud rather than silently falling back.
+    """
+    raw = os.environ.get("DECISION_HTTP_READ_TIMEOUT", "600").strip() or "600"
+    try:
+        val = float(raw)
+    except ValueError:
+        raise RuntimeError(
+            f"DECISION_HTTP_READ_TIMEOUT must be a number, got {raw!r}"
+        )
+    if val <= 0:
+        raise RuntimeError(f"DECISION_HTTP_READ_TIMEOUT must be > 0, got {raw!r}")
+    return val
 
 
 # Retry policy for provider calls: 3 attempts, exponential backoff.
@@ -1382,7 +1424,9 @@ def extract_session_decisions(
     else:
         body["reasoning"] = {"effort": effort}
     with httpx.Client(
-        timeout=httpx.Timeout(connect=10, read=120, write=30, pool=10)
+        timeout=httpx.Timeout(
+            connect=10, read=_get_decision_read_timeout(), write=30, pool=10
+        )
     ) as client:
         resp, _attempts = _post_with_retry(
             client, api_base.rstrip("/") + "/responses", body
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index afd43d0..d789539 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -154,8 +154,9 @@ def test_parse_responses_text_empty_and_malformed():
 def test_responses_url_default_and_override(monkeypatch):
     monkeypatch.delenv("BRAIN_API_BASE", raising=False)
     assert bridge._responses_url() == "https://api.openai.com/v1/responses"
-    monkeypatch.setenv("BRAIN_API_BASE", "http://x:1/base/")
-    assert bridge._responses_url() == "http://x:1/base/responses"
+    # Loopback http stays allowed (local proxy); trailing slash is stripped.
+    monkeypatch.setenv("BRAIN_API_BASE", "http://localhost:1/base/")
+    assert bridge._responses_url() == "http://localhost:1/base/responses"
 
 
 # --- hotfix hardening (QA_REJECTED follow-up, mocked HTTP only) ---
@@ -2374,7 +2375,8 @@ def test_sibling_missing_still_resolves_per_project(tmp_path, monkeypatch):
 
 def _clean_routing_env(monkeypatch):
     for var in ("BRAIN_RISK_ROUTING_ENABLED", "BRAIN_MODEL_LOW",
-                "BRAIN_MODEL_HIGH", "BRAIN_MODEL", "BRAIN_STAGE_TIERS"):
+                "BRAIN_MODEL_HIGH", "BRAIN_MODEL", "BRAIN_STAGE_TIERS",
+                "BRAIN_REASONING_EFFORT", "BRAIN_MAX_TOKENS"):
         monkeypatch.delenv(var, raising=False)
 
 
@@ -3189,3 +3191,55 @@ def test_nonpositive_ctx_per_file_cap_fails_the_turn(tmp_path, monkeypatch):
             stage="review", include_bundle=False, include_diff=False,
             context_paths=["report.md"], project_root=str(tmp_path))
 
+
+# --- R1: HTTPS scheme guard (Task 265) ---
+
+
+def test_https_guard_allows_https():
+    base = "https://api.openai.com/v1"
+    assert bridge._https_guard(base, "BRAIN_API_BASE") == base
+
+
+def test_https_guard_allows_loopback_http():
+    for base in ("http://localhost:8080/v1", "http://127.0.0.1:1234/v1"):
+        assert bridge._https_guard(base, "BRAIN_API_BASE") == base
+
+
+def test_https_guard_rejects_plaintext_remote():
+    with pytest.raises(RuntimeError) as exc:
+        bridge._https_guard("http://api.example.com/v1", "BRAIN_API_BASE")
+    assert "BRAIN_API_BASE" in str(exc.value)
+
+
+def test_responses_url_rejects_plaintext_remote(monkeypatch):
+    monkeypatch.setenv("BRAIN_API_BASE", "http://api.example.com/v1")
+    with pytest.raises(RuntimeError):
+        bridge._responses_url()
+
+
+def test_responses_url_accepts_https(monkeypatch):
+    monkeypatch.setenv("BRAIN_API_BASE", "https://openrouter.ai/api/v1")
+    assert bridge._responses_url() == "https://openrouter.ai/api/v1/responses"
+
+
+# --- R2: configurable read timeout (Task 265) ---
+
+
+def test_read_timeout_default_and_override(monkeypatch):
+    monkeypatch.delenv("BRAIN_HTTP_READ_TIMEOUT", raising=False)
+    assert bridge._get_read_timeout() == 600.0
+    monkeypatch.setenv("BRAIN_HTTP_READ_TIMEOUT", "900")
+    assert bridge._get_read_timeout() == 900.0
+
+
+def test_read_timeout_rejects_malformed(monkeypatch):
+    monkeypatch.setenv("BRAIN_HTTP_READ_TIMEOUT", "abc")
+    with pytest.raises(RuntimeError):
+        bridge._get_read_timeout()
+
+
+def test_read_timeout_rejects_nonpositive(monkeypatch):
+    monkeypatch.setenv("BRAIN_HTTP_READ_TIMEOUT", "0")
+    with pytest.raises(RuntimeError):
+        bridge._get_read_timeout()
+
diff --git a/tests/test_decision_server.py b/tests/test_decision_server.py
index e8f0d50..d3c427d 100644
--- a/tests/test_decision_server.py
+++ b/tests/test_decision_server.py
@@ -571,13 +571,13 @@ def test_decision_env_precedence_over_brain_fallbacks(srv, monkeypatch):
 
 
 def test_decision_env_blank_falls_back_to_brain(srv, monkeypatch):
-    monkeypatch.setenv("BRAIN_API_BASE", "http://brain-base")
+    monkeypatch.setenv("BRAIN_API_BASE", "https://brain-base")
     monkeypatch.setenv("BRAIN_API_KEY", "sk-brain")
     monkeypatch.setenv("BRAIN_REASONING_EFFORT", "low")
     monkeypatch.setenv("DECISION_API_BASE", "   ")
     monkeypatch.setenv("DECISION_API_KEY", "   ")
     monkeypatch.setenv("DECISION_REASONING_EFFORT", "   ")
-    assert srv._get_api_base() == "http://brain-base"
+    assert srv._get_api_base() == "https://brain-base"
     assert srv._get_api_key() == "sk-brain"
     assert srv._get_decision_effort() == "low"
 
@@ -945,6 +945,7 @@ def test_temperature_pinned_zero_unless_set(srv, tmp_path, monkeypatch):
         {"type": "output_text", "text": json.dumps([one])}]}]}
     monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
     monkeypatch.delenv("DECISION_TEMPERATURE", raising=False)
+    monkeypatch.delenv("DECISION_MAX_TOKENS", raising=False)
     _stub_capture(_decision_resp(200, "fine", envelope))
     _extract(srv)(7, transcript_path=str(transcript))
     assert "temperature" not in seen["body"]
@@ -1039,6 +1040,7 @@ def test_extract_repeat_determinism_five_times(srv, tmp_path, monkeypatch, capsy
     monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
     monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
     monkeypatch.delenv("DECISION_TEMPERATURE", raising=False)
+    monkeypatch.delenv("DECISION_MAX_TOKENS", raising=False)
     one = _valid_one_191()
     calls = _stub_counting_http(
         monkeypatch,
@@ -1206,6 +1208,7 @@ def test_extract_temp_wire_default_zero(srv, tmp_path, monkeypatch):
     monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
     monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
     monkeypatch.delenv("DECISION_TEMPERATURE", raising=False)
+    monkeypatch.delenv("DECISION_MAX_TOKENS", raising=False)
     seen = []
     _stub_capture(monkeypatch,
                   _decision_resp(200, "fine", _envelope_191(json.dumps(_ship_candidates()))),
@@ -2357,3 +2360,56 @@ def test_provider_failure_message_scalar_usage_still_terminal(srv):
     msg = srv._provider_failure_message(diag)
     assert msg.startswith("decision model returned no text: OUTPUT_BUDGET_EXHAUSTED")
     assert "input=None" in msg
+
+
+# --- R1: HTTPS scheme guard (Task 265) ---
+
+
+def test_decision_https_guard_allows_https(srv):
+    base = "https://api.openai.com/v1"
+    assert srv._https_guard(base, "DECISION_API_BASE") == base
+
+
+def test_decision_https_guard_allows_loopback(srv):
+    for base in ("http://localhost:8080/v1", "http://127.0.0.1:1234/v1"):
+        assert srv._https_guard(base, "DECISION_API_BASE") == base
+
+
+def test_decision_https_guard_rejects_plaintext_remote(srv):
+    with pytest.raises(RuntimeError) as exc:
+        srv._https_guard("http://api.example.com/v1", "DECISION_API_BASE")
+    assert "DECISION_API_BASE" in str(exc.value)
+
+
+def test_decision_api_base_rejects_plaintext_remote(srv, monkeypatch):
+    monkeypatch.setenv("DECISION_API_BASE", "http://api.example.com/v1")
+    monkeypatch.delenv("BRAIN_API_BASE", raising=False)
+    with pytest.raises(RuntimeError):
+        srv._get_api_base()
+
+
+def test_decision_api_base_accepts_https(srv, monkeypatch):
+    monkeypatch.setenv("DECISION_API_BASE", "https://openrouter.ai/api/v1")
+    assert srv._get_api_base() == "https://openrouter.ai/api/v1"
+
+
+# --- R2: configurable read timeout (Task 265) ---
+
+
+def test_decision_read_timeout_default_and_override(srv, monkeypatch):
+    monkeypatch.delenv("DECISION_HTTP_READ_TIMEOUT", raising=False)
+    assert srv._get_decision_read_timeout() == 600.0
+    monkeypatch.setenv("DECISION_HTTP_READ_TIMEOUT", "900")
+    assert srv._get_decision_read_timeout() == 900.0
+
+
+def test_decision_read_timeout_rejects_malformed(srv, monkeypatch):
+    monkeypatch.setenv("DECISION_HTTP_READ_TIMEOUT", "abc")
+    with pytest.raises(RuntimeError):
+        srv._get_decision_read_timeout()
+
+
+def test_decision_read_timeout_rejects_nonpositive(srv, monkeypatch):
+    monkeypatch.setenv("DECISION_HTTP_READ_TIMEOUT", "0")
+    with pytest.raises(RuntimeError):
+        srv._get_decision_read_timeout()
```
<!-- END_GIT_DIFF -->
