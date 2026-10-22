# Task 330: Luna 400 on Replayed Reasoning `status` — Strip at Send Time

**File:** `tasks/qa/330-luna-status-strip-replay-fix.md`
**Source:** manager
**Type:** bugfix
**Status:** open

## Goal

Stop the fatal 400 `Unknown parameter: 'input[N].status'` on `gpt-6-luna` turns
with replayed history, by stripping volatile execution-state keys from replayed
provider items at send time — without changing capture, transcripts, or the
Brain/Hands protocol contract.

## Manager's Notes

- The Manager switched `BRAIN_MODEL` to `gpt-6-luna` and every turn with
  replayed history started failing 400; `muse-spark-1.3-contributor` never
  failed on the same transcripts.
- The Manager ordered: create a task in this project, solve it in autopilot
  mode, and check the official OpenAI docs while at it.
- Autopilot locked for task 330 on 2026-10-22: Hands chains plan → implement
  → verify → bridge-QA → bridge-review → stage → qa with no ferrying through
  the Manager. Closure still needs the explicit approval word.

## Local TODOs

- [x] Root-cause the 400 (upstream attaches `status` to reasoning output
  items; bridge replayed them verbatim; Luna validates strictly, Muse does not)
- [x] Implement `_sanitize_replay_item` + wire into `_build_request_body`
- [x] Add regression tests (strip + byte-identical fast path)
- [x] Verify against official OpenAI Responses docs (reasoning item input schema)
- [ ] Re-run full brain suite as verification evidence
- [ ] Bridge QA round (fix loop on reject, max 3)
- [ ] Bridge review round, stage diff, move to qa

## Acceptance Criteria

- [ ] A replayed reasoning item carrying `"status": "completed"` reaches the
  provider WITHOUT the `status` key, keeping `id`/`type`/`encrypted_content`
  intact (proven live: real blob + status → `completed`, not 400)
- [ ] Items without volatile keys ride the wire byte-identical (F2 verbatim
  contract preserved)
- [ ] Full brain suite green (`test_brain_bridge`, `test_brain_preflight`,
  `test_brain_capability`, `test_brain_diff_attach`,
  `test_brain_responses_alignment`)
- [ ] Official OpenAI docs confirm `status` is output-only on reasoning items
- [ ] QA verdict `QA_PASSED`, reviewer verdict `APPROVED`/`APPROVED_WITH_CHANGES`
- [ ] No secrets in repo or memory; ZAC holds (no autonomous commit)

## Verification Evidence

- `test_brain_responses_alignment.py`: 27 passed (incl. 2 new regression tests)
- Full brain files: 354 passed
- Live proof via proxy + Go gateway on `gpt-6-luna`: replay of a REAL
  provider-issued reasoning blob with `"status": "completed"` attached →
  `status: completed, T6-OK` (pre-fix shape 400d with `unknown_parameter`)
- Deployed: repo `mcp-brain-bridge/server.py` == live
  `~/.config/opencode/mcp-brain-bridge/server.py`; `mcp-brain.service`
  restarted 2026-10-22; zen-proxy audit off, healthy (200)

## Risk & Rollback

- **Risk:** Over-stripping (dropping a key a provider needs on input).
  Contained: strip list is exactly `{"status"}`; `content`/`summary`/`id`/
  `encrypted_content` pass through (live turn with `content:[]` +
  `summary:[]` returned `completed`).
- **Risk:** Old transcripts already contain `status`-carrying items.
  Covered: sanitizing happens at SEND time, so no migration is needed.
- **Rollback:** Revert the sanitizer call in `_build_request_body` plus the two
  tests and ADR-005, delete `_sanitize_replay_item` and
  `_REPLAY_DROPPED_KEYS`, and restore the F2 "replay verbatim" docstring
  line; old transcripts keep working (they replayed verbatim before — on
  lenient models).

## Execution Log & Reasoning

- QA round (2026-10-22, `gpt-6-luna` brain, autopilot): first turn asked for
  the staged diff; after `stage_and_inject_diff`, re-run returned
  `QA_PASSED` with non-blocking notes F1 (byte-level F2 exception
  documented) / F2 (strip nothing else without schema evidence) /
  F3 (send-time sanitizer covers disk transcripts) / F4 (rollback wording
  — fixed in this file before review).
- Review round (2026-10-22): Code Reviewer verdict `APPROVED` technically —
  `PO_REVIEW_PENDING`. No blocking issues; ZAC clean (no prohibited Git
  ops in hunks). PO (Manager) reply: "Approved for closure".

- Official OpenAI docs check (2026-10-22, autopilot): the Responses
  `reasoning.encrypted_content` doc states encrypted content exists to let
  reasoning items be used in multi-turn stateless conversations; the item
  shape is `{id, summary, type, +encrypted_content}`. `status` is documented
  only as *response generation* status (`completed`/`incomplete`/…), never as
  a reasoning-item input field — so stripping it at send time is
  spec-aligned, and Luna's strict `unknown_parameter` reject is correct
  server behavior, not a gateway quirk.
- Assumption A1: `status` values seen (`completed`) come from the provider,
  not the bridge — verified by capturing a raw upstream response item
  carrying both `status` and `phase` keys.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/mcp-brain-bridge/DECISIONS.md b/mcp-brain-bridge/DECISIONS.md
index 68a0d80..e9eca88 100644
--- a/mcp-brain-bridge/DECISIONS.md
+++ b/mcp-brain-bridge/DECISIONS.md
@@ -27,3 +27,10 @@
 - **Decision:** Fix all ten behind per-parameter env switches defaulting to off (all six new wire parameters probed HTTP 200 against the live gateway first); validate effort against the official vocabulary; parse `error.code`/`error.type` with terminal billing codes; read `response.model`/`cached_tokens` into diagnostics; replay reasoning items and `phase` from version-tolerant transcripts; return structured REPORTs on fatal transport errors; fail loud on malformed numeric config.
 - **Consequences:** Default wire bytes are unchanged until operators opt in; diagnostics expose model substitution and cache hits; transcripts stay backward compatible.
 - **Rollback:** One-function revert of the request builder plus switch-off; diagnostics parser is pure and separately testable.
+
+## [2026-10-22] ADR-005: Strip volatile `status` from replayed provider items
+
+- **Context:** After switching `BRAIN_MODEL` to `gpt-6-luna`, every turn with replayed history failed 400 with `Unknown parameter: 'input[N].status'`. Upstream attaches `status` (e.g. `"completed"`) to reasoning output items; the bridge stored and replayed them verbatim (ADR-004/F2). `muse-spark-1.3-contributor` silently accepts the key, so this only surfaced on the stricter Luna endpoint.
+- **Decision:** Sanitize replayed `provider_items` at send time (`_sanitize_replay_item` drops the `status` key, keeps `id`/`type`/`encrypted_content`/`summary`/`content` intact). Send-time, not capture-time, so transcripts already on disk are fixed without migration; capture stays verbatim for audit. Proven live: a real provider-issued reasoning blob replayed with `status` attached now returns `completed` instead of 400.
+- **Consequences:** Strict providers accept history replays; lenient ones are unaffected (key was ignored anyway). Two regression tests pin the strip and the byte-identical fast path.
+- **Rollback:** Revert the sanitizer call in `_build_request_body` plus the two tests; old transcripts keep working (they replayed verbatim before).
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index ca2e0b5..f060f65 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -1466,6 +1466,33 @@ def _note_observed_ratio(chars: int, input_tokens: int) -> None:
         _calibrated_chars_per_token = ratio
 
 
+#: Volatile execution-state keys that providers attach to response output
+#: items but reject on input. Observed 2026-10-22: the Go gateway's
+#: gpt-6-luna endpoint 400s with "Unknown parameter: 'input[N].status'"
+#: when a replayed reasoning item still carries the status of the turn
+#: that produced it (e.g. "completed"). muse-spark-1.3-contributor
+#: silently accepts it, which is why this only surfaced after the model
+#: switch. Sanitized at SEND time (not capture time) so transcripts
+#: already on disk are fixed without migration; capture stays verbatim
+#: for audit value.
+_REPLAY_DROPPED_KEYS = frozenset({"status"})
+
+
+def _sanitize_replay_item(item: Any) -> Any:
+    """Strip volatile execution-state keys from a replayed provider item.
+
+    Keeps the item byte-identical (same object) when nothing needs
+    stripping, so the F2 "replay verbatim" contract holds for the common
+    case; returns a filtered copy only when a dropped key is present.
+    Non-dict items pass through untouched.
+    """
+    if not isinstance(item, dict):
+        return item
+    if not any(k in _REPLAY_DROPPED_KEYS for k in item):
+        return item
+    return {k: v for k, v in item.items() if k not in _REPLAY_DROPPED_KEYS}
+
+
 def _build_request_body(
     system_prompt: str,
     history: Optional[list],
@@ -1497,7 +1524,9 @@ def _build_request_body(
     History items may carry ``phase`` (assistant only — replayed on the
     item per the official guidance) and ``provider_items`` (non-message
     output items such as reasoning blocks with encrypted content,
-    replayed verbatim after their turn — F2). Old text-only transcripts
+    replayed after their turn — F2; volatile execution-state keys like
+    ``status`` are stripped at send time since strict providers reject
+    them on input). Old text-only transcripts
     carry neither key and replay exactly as before.
     """
     if model is None:
@@ -1524,7 +1553,7 @@ def _build_request_body(
         chat.append(item)
         for extra in turn.get("provider_items") or []:
             if isinstance(extra, dict):
-                chat.append(extra)
+                chat.append(_sanitize_replay_item(extra))
     chat.append({"role": "user", "content": effective_prompt})
     body: dict[str, Any] = {
         "model": model,
diff --git a/tests/test_brain_responses_alignment.py b/tests/test_brain_responses_alignment.py
index 52ee793..b36edeb 100644
--- a/tests/test_brain_responses_alignment.py
+++ b/tests/test_brain_responses_alignment.py
@@ -283,6 +283,47 @@ def test_new_transcript_replays_reasoning_items_and_phase():
     assert {"id": "rs_1", "type": "reasoning"} in body["input"][3:]
 
 
+def test_replay_strips_status_from_reasoning_items():
+    # 2026-10-22: upstream attaches "status" (e.g. "completed") to reasoning
+    # output items; the Go gateway's gpt-6-luna endpoint 400s with
+    # "Unknown parameter: 'input[N].status'" when it is replayed, while
+    # muse-spark-1.3-contributor silently accepts it. The replay must drop
+    # the volatile key but keep id/type/encrypted_content intact.
+    raw = (
+        '{"role": "user", "content": "q"}\n'
+        '{"role": "assistant", "content": "a", "phase": "final_answer", '
+        '"provider_items": [{"id": "rs_1", "type": "reasoning", '
+        '"status": "completed", "content": [], "summary": [], '
+        '"encrypted_content": "e30="}]}\n'
+    )
+    turns, _ = bridge._parse_turns(raw)
+    body = bridge._build_request_body("sys", turns, "next")
+    replayed = [
+        it for it in body["input"][3:]
+        if isinstance(it, dict) and it.get("type") == "reasoning"
+    ]
+    assert len(replayed) == 1
+    assert "status" not in replayed[0]
+    assert replayed[0]["id"] == "rs_1"
+    assert replayed[0]["type"] == "reasoning"
+    assert replayed[0]["encrypted_content"] == "e30="
+
+
+def test_replay_without_status_stays_byte_identical():
+    # No dropped keys present -> the exact same object rides the wire
+    # (F2 verbatim contract).
+    raw = (
+        '{"role": "user", "content": "q"}\n'
+        '{"role": "assistant", "content": "a", '
+        '"provider_items": [{"id": "rs_1", "type": "reasoning", '
+        '"encrypted_content": "e30="}]}\n'
+    )
+    turns, _ = bridge._parse_turns(raw)
+    original = turns[1]["provider_items"][0]
+    body = bridge._build_request_body("sys", turns, "next")
+    assert body["input"][3] is original
+
+
 # --- Estimator calibration (F3) -----------------------------------------------
```
<!-- END_GIT_DIFF -->
