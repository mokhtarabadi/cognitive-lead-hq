# Task 331: Drop Replayed Items with Over-Long IDs (Luna 64-char cap)

**File:** `tasks/qa/331-drop-overlong-replay-ids.md`
**Source:** manager
**Type:** bugfix
**Status:** open

## Goal

Stop the fatal 400 `Invalid 'input[N].id': string too long (max 64)` on
`gpt-6-luna` turns with replayed history, by dropping replayed provider
items whose `id` exceeds the provider's 64-char input limit — at send
time, preserving everything else.

## Manager's Notes

- The Manager reported the new transport error after the task-330 fix:
  `status` gone, now the `id` itself is rejected (observed length 67).
- The Manager ordered: fix it, check the docs, auto-fix. Autopilot locked
  for task 331 on 2026-10-22.
- Docs learned: OpenAI community forum thread "input item ID exceeds 64
  characters" (Oct 2026) confirms the platform itself generates item IDs
  longer than its own 64-char input limit (`string_above_max_length`);
  recovery that preserves notes/state = do not replay the offending item.
  The Responses API reference shows input item params carrying `id`;
  `status` is response-generation state, never an input field.

## Local TODOs

- [x] Root-cause the 400 (gateway-minted `rs_` + 64 hex = 67 chars;
  Luna caps input `id` at 64; Muse ignores it)
- [ ] Extend `_sanitize_replay_item` to drop items with `len(id) > 64`
- [ ] Add regression tests (drop long-id, keep normal-id byte-identical)
- [ ] Run full brain suite as verification evidence
- [ ] Deploy live, restart singleton, prove live with a crafted long-id item
- [ ] Bridge QA round (fix loop on reject, max 3)
- [ ] Bridge review round, stage diff, move to qa

## Acceptance Criteria

- [ ] A replayed reasoning item with a 67-char `id` never reaches the wire
  (dropped at send time with a logged note)
- [ ] Items with `id` within the cap pass through unchanged (F2 verbatim
  contract preserved)
- [ ] `status`-strip from task 330 keeps working (no regression)
- [ ] Full brain suite green
- [ ] Live proof: crafted long-id replay → `completed`, not 400
- [ ] QA verdict `QA_PASSED`, reviewer verdict `APPROVED`/`APPROVED_WITH_CHANGES`
- [ ] No secrets in repo or memory; ZAC holds

## Verification Evidence

- Full brain suite: 381 passed (`test_brain_bridge`,
  `test_brain_preflight`, `test_brain_capability`, `test_brain_diff_attach`,
  `test_brain_responses_alignment` incl. 2 new id-length tests).
- Live proof (2026-10-22, via proxy + Go gateway on `gpt-6-luna`): a
  scratch transcript replaying a reasoning item with BOTH a `status` key
  AND a 67-char `id` returns `completed / POISON-OK` instead of 400; the
  singleton journal records the drop. Re-verified after the QA log-hygiene
  fix with a fresh poison turn (`V2-OK`, journal shows the static-form
  message with no item fields). NOTE: two earlier scratch runs (T6-OK,
  LONGID-OK) are discounted as proof — they wrote poison rows to
  `tasks/<id>/` instead of the real `tasks/.sessions/<id>/` path, so no
  history replayed in those turns; the POISON-OK run above used the
  correct path with row-count and journal verification.
- Docs: OpenAI community forum `input item ID exceeds 64 characters`
  (`string_above_max_length`, max 64); Responses API reference input-item
  params carry `id`; reasoning guide confirms replay uses
  id/encrypted_content-bearing items.

## Risk & Rollback

- **Risk:** Dropping a reasoning item loses encrypted-context continuity
  for that turn. Contained: continuity is an optimization, not required
  input — the turn still completes, and the drop is logged per item.
- **Risk:** A provider that accepts long ids never notices. Dropping is
  still safe: the model simply reasons without that prior block.
- **Rollback:** Revert the length check in `_sanitize_replay_item` plus
  the new tests and ADR-006; old transcripts keep working on lenient
  models.

## Execution Log & Reasoning

- Root cause (verified live 2026-10-22): the Go gateway mints reasoning
  item ids of varying length (`rs_` + 50 hex observed passing,
  `rs_` + 64 hex = 67 chars observed rejected). Luna caps input `id` at
  64 chars; Muse ignores the violation. Autopilot locked for task 331.
- Docs check: OpenAI community forum thread "input item ID exceeds 64
  characters" confirms the platform generates over-limit ids itself and
  the supported recovery is to not replay the offending item; the
  Responses reference shows input item params carrying `id`.
- Honesty note: two early scratch runs (T6-OK for task 330, LONGID-OK
  here) wrote poison rows to `tasks/<id>/` instead of the real
  `tasks/.sessions/<id>/` path, so no history replayed — discounted as
  proof. Redone correctly with row-count + journal verification
  (POISON-OK + `dropping replayed reasoning item with 67-char id`).
- Assumption A1: 64 is the right cap for all strict providers (single
  observed value: Luna 400 text). If another provider caps lower, the
  constant + tests move together.
- Review (APPROVED_WITH_CHANGES, R1 low): ADR-006 understated the
  behavior (skip applies on the send path for every provider, not just
  strict ones) and the test count (three, not two) — both corrected;
  CHANGELOG entry added under [Unreleased] per repo Documentation Sync
  Rules (Tasks 330 + 331 combined, as 330 shipped without one).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index c78e848..5acca9c 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -23,6 +23,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Stale plugin citations corrected (same task):** the executor's `src/loop.ts 205-437` reference now names the real gate (`shouldContinue` at `src/loop.ts:458-492`) and handler (`handleSessionIdle` at `src/loop.ts:552-853`); the stop-file claim now states that the code reads only the projectDir `.opencode/STOP_GOAL` path (`src/index.ts:284-296`) and that the project-root path is never read; the "exact-only" slash list now covers the full parser surface (objective, block reason, resume, and evidence accept arguments; status, clear, and complete are exact-only); the missing `/goal resume` and `/goal evidence` slash inputs are documented; the goal lane's "exactly two goal writes" rule becomes three writes plus resume, matching the restored `goal_set` trigger.
 - **Compaction task-boundary gap closed (same task):** the previous task being finished and the Manager defining a new task in the same session now triggers `compact_context` with `keepTurns` 0 and `mode` `compact`, and the todo list is recovered with `todoread` rather than from a remembered transcript.
+- **Replayed reasoning items sanitized at send time (Tasks 330 + 331):** `gpt-6-luna` turns with replayed history failed 400 twice — first `Unknown parameter: 'input[N].status'` (upstream attaches execution `status` to reasoning output items; the bridge replayed them verbatim and the strict Luna endpoint rejects the key while `muse-spark-1.3-contributor` silently accepts it), then `Invalid 'input[N].id': string too long` (the gateway mints ids longer than its own 64-char input cap, e.g. `rs_` + 64 hex = 67 chars; confirmed by an OpenAI community report of platform-minted over-limit ids). `_sanitize_replay_item` in `mcp-brain-bridge/server.py` now drops the `status` key and skips whole items whose string `id` exceeds 64 chars (never truncated — the id is bound to `encrypted_content`); the skip diagnostic records only the id length and the cap, never item fields. Send-time, so existing transcripts are fixed without migration; capture stays verbatim. Proven live against the Go gateway: a real provider-issued blob replayed with both defects returns `completed`. 27 + 3 new tests in `tests/test_brain_responses_alignment.py`; ADR-005/ADR-006 in `mcp-brain-bridge/DECISIONS.md`.
 - **False-green verification command (same task):** the `uv run tests/test_prompt_sync.py` form ran the file as a script with no main block and exited 0 without executing a single assertion; the working form is `uv run --with pytest python -m pytest tests/test_prompt_sync.py -q` (16 passed).
 - **Compaction fragment retired (same task):** `prompts/fragments/22-compaction_protocol.md` moved to `prompts/archive/` with an archival header, removed from `prompts/manifest.txt`, and dropped from the splitter `TOP_LEVEL_TAGS` (21 to 20); split-to-assemble drift introduces zero new lines versus the pre-existing night-mode and language-policy gap.
 
diff --git a/mcp-brain-bridge/DECISIONS.md b/mcp-brain-bridge/DECISIONS.md
index e9eca88..933dcb6 100644
--- a/mcp-brain-bridge/DECISIONS.md
+++ b/mcp-brain-bridge/DECISIONS.md
@@ -34,3 +34,10 @@
 - **Decision:** Sanitize replayed `provider_items` at send time (`_sanitize_replay_item` drops the `status` key, keeps `id`/`type`/`encrypted_content`/`summary`/`content` intact). Send-time, not capture-time, so transcripts already on disk are fixed without migration; capture stays verbatim for audit. Proven live: a real provider-issued reasoning blob replayed with `status` attached now returns `completed` instead of 400.
 - **Consequences:** Strict providers accept history replays; lenient ones are unaffected (key was ignored anyway). Two regression tests pin the strip and the byte-identical fast path.
 - **Rollback:** Revert the sanitizer call in `_build_request_body` plus the two tests; old transcripts keep working (they replayed verbatim before).
+
+## [2026-10-22] ADR-006: Drop replayed items with over-long ids
+
+- **Context:** After ADR-005, `gpt-6-luna` turns with history failed a new way: `Invalid 'input[N].id': string too long` (length 67, cap 64). The platform itself mints reasoning ids longer than its own input cap (`rs_` + 64 hex); Muse ignores it, Luna 400s. An OpenAI community thread ("input item ID exceeds 64 characters", Oct 2026) confirms the platform generates over-limit ids and that the supported recovery is to not replay the offending item.
+- **Decision:** `_sanitize_replay_item` returns None for items whose string `id` exceeds 64 chars; the send loop skips them. The skip diagnostic records only the id length and the cap — never the id, type, or any other item field. Never truncate: the id is bound to `encrypted_content` and editing it breaks decryption. Dropping only loses encrypted-context continuity for that turn.
+- **Consequences:** Strict providers accept history replays regardless of id length. The skip applies on the send path for every provider (lenient ones simply never needed it — they ignored the over-long id instead of 400ing). Three regression tests pin the drop, the at-cap pass-through, and the redacted diagnostic. The skip diagnostic records only the id length and the cap, never item fields.
+- **Rollback:** Revert the length check plus the two tests; old transcripts keep working on lenient models.
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index f060f65..5c6c49f 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -1478,16 +1478,37 @@ def _note_observed_ratio(chars: int, input_tokens: int) -> None:
 _REPLAY_DROPPED_KEYS = frozenset({"status"})
 
 
+#: Maximum input-item id length enforced by strict Responses providers
+#: (observed 2026-10-22: gpt-6-luna 400s with "Invalid 'input[N].id':
+#: string too long", length 67 vs cap 64). The platform itself mints
+#: longer ids (e.g. rs_ + 64 hex chars), so over-long ids must be
+#: dropped whole, never truncated — the id is bound to the item's
+#: encrypted_content and editing it breaks decryption. Dropping only
+#: loses encrypted-context continuity for that turn, never the turn.
+_REPLAY_MAX_ID_LEN = 64
+
+
 def _sanitize_replay_item(item: Any) -> Any:
     """Strip volatile execution-state keys from a replayed provider item.
 
     Keeps the item byte-identical (same object) when nothing needs
     stripping, so the F2 "replay verbatim" contract holds for the common
     case; returns a filtered copy only when a dropped key is present.
+    Returns None when the whole item must be skipped: an ``id`` longer
+    than the provider's input cap (strict providers 400 the turn).
     Non-dict items pass through untouched.
     """
     if not isinstance(item, dict):
         return item
+    item_id = item.get("id")
+    if isinstance(item_id, str) and len(item_id) > _REPLAY_MAX_ID_LEN:
+        print(
+            f"brain-bridge: dropping replayed item with "
+            f"{len(item_id)}-char id (provider cap {_REPLAY_MAX_ID_LEN}); "
+            f"continuity for that block is skipped, the turn proceeds",
+            file=sys.stderr,
+        )
+        return None
     if not any(k in _REPLAY_DROPPED_KEYS for k in item):
         return item
     return {k: v for k, v in item.items() if k not in _REPLAY_DROPPED_KEYS}
@@ -1553,7 +1574,9 @@ def _build_request_body(
         chat.append(item)
         for extra in turn.get("provider_items") or []:
             if isinstance(extra, dict):
-                chat.append(_sanitize_replay_item(extra))
+                sanitized = _sanitize_replay_item(extra)
+                if sanitized is not None:
+                    chat.append(sanitized)
     chat.append({"role": "user", "content": effective_prompt})
     body: dict[str, Any] = {
         "model": model,
diff --git a/tests/test_brain_responses_alignment.py b/tests/test_brain_responses_alignment.py
index b36edeb..8c724cf 100644
--- a/tests/test_brain_responses_alignment.py
+++ b/tests/test_brain_responses_alignment.py
@@ -324,6 +324,69 @@ def test_replay_without_status_stays_byte_identical():
     assert body["input"][3] is original
 
 
+def test_replay_drops_item_with_overlong_id():
+    # 2026-10-22: the platform mints reasoning ids longer than its own
+    # 64-char input cap (observed rs_ + 64 hex = 67 chars); Luna 400s
+    # with "Invalid 'input[N].id': string too long". The item must be
+    # skipped whole — truncating the id would break the encrypted_content
+    # binding, and the turn must still go out with the remaining items.
+    long_id = "rs_" + "ab" * 32
+    assert len(long_id) == 67
+    raw = (
+        '{"role": "user", "content": "q"}\n'
+        '{"role": "assistant", "content": "a", '
+        '"provider_items": [{"id": "%s", "type": "reasoning", '
+        '"encrypted_content": "e30="}]}\n' % long_id
+    )
+    turns, _ = bridge._parse_turns(raw)
+    body = bridge._build_request_body("sys", turns, "next")
+    replayed = [
+        it for it in body["input"][3:]
+        if isinstance(it, dict) and it.get("type") == "reasoning"
+    ]
+    assert replayed == []
+
+
+def test_replay_keeps_normal_id_reasoning_item():
+    # A 64-char id is exactly at the cap and must ride through untouched.
+    ok_id = "rs_" + "ab" * 30 + "c"
+    assert len(ok_id) == 64
+    raw = (
+        '{"role": "user", "content": "q"}\n'
+        '{"role": "assistant", "content": "a", '
+        '"provider_items": [{"id": "%s", "type": "reasoning", '
+        '"encrypted_content": "e30="}]}\n' % ok_id
+    )
+    turns, _ = bridge._parse_turns(raw)
+    original = turns[1]["provider_items"][0]
+    body = bridge._build_request_body("sys", turns, "next")
+    assert body["input"][3] is original
+
+
+def test_replay_drop_logs_no_item_fields(capsys):
+    # The overlong-item diagnostic must not carry item-derived values —
+    # only the id length and the cap. A sentinel in `type` must never
+    # reach stderr, and the item must not reach the wire either.
+    long_id = "rs_" + "ab" * 32
+    assert len(long_id) == 67
+    raw = (
+        '{"role": "user", "content": "q"}\n'
+        '{"role": "assistant", "content": "a", '
+        '"provider_items": [{"id": "%s", "type": "SENTINEL_TYPE_XYZ", '
+        '"encrypted_content": "e30="}]}\n' % long_id
+    )
+    turns, _ = bridge._parse_turns(raw)
+    body = bridge._build_request_body("sys", turns, "next")
+    assert [
+        it for it in body["input"][3:]
+        if isinstance(it, dict) and it.get("id") == long_id
+    ] == []
+    captured = capsys.readouterr()
+    assert "SENTINEL_TYPE_XYZ" not in captured.err
+    assert long_id not in captured.err
+    assert "67-char id" in captured.err
+
+
 # --- Estimator calibration (F3) -----------------------------------------------
```
<!-- END_GIT_DIFF -->
