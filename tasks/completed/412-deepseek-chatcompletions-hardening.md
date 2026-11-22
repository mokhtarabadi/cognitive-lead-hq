# Task 412: DeepSeek Chat Completions Hardening

**File:** `tasks/qa/412-deepseek-chatcompletions-hardening.md`
**Source:** manager
**Type:** improvement
**Status:** open
**Submitted:** 2026-11-22T14:55:01Z

## Goal

Harden the brain bridge (mcp-brain-bridge) for DeepSeek V4.1 Flash running over the OpenAI-compatible chat completions API with reasoning effort `max`. Work covers: output token enhancement (BRAIN_MAX_TOKENS=131072), usage-details passthrough (cache hits + reasoning tokens) in the response converter, and a warning branch for dropped input item types. Verified against DeepSeek's official API docs.

## Manager's Notes

Switched BRAIN to DeepSeek V4.1 Flash 1017 over /go/chat (chat completions) with reasoning_effort=max. Audited converter against DeepSeek docs; only real issues were usage-details passthrough and output-token sizing. Temperature and `max` effort validated as non-issues.

## Local TODOs

- [x] Switch .env to DeepSeek chat mount + max effort
- [x] Enhance output token size (BRAIN_MAX_TOKENS=131072)
- [x] Pass through usage details (F6)
- [x] Add warning branch for dropped input items (F4)
- [x] Run lint_task_file
- [x] Stage via custom_context_stage_and_inject_diff
- [x] QA transition

## Acceptance Criteria

- [x] `uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py tests/test_brain_responses_alignment.py` exits 0
- [x] `lint_task_file` passes on this task file
- [x] Smoke brain_turn returns XML_EXTRACTED with reasoning_tokens visible in usage
- [x] CHANGELOG.md updated

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py tests/test_brain_responses_alignment.py -q
- **Expected result:** All tests pass
- **Actual result:** 390 passed in 2.88s
- **Exit code:** 0

### Post-fix verification (QA rejection round 2)

- **Syntax check:** `uv run --project mcp-brain-bridge python -c "import ast,pathlib; [ast.parse(pathlib.Path(p).read_text()) for p in ['mcp-brain-bridge/server.py','tests/test_brain_bridge.py','tests/test_brain_responses_alignment.py']]"` — exit 0.
- **Declared tooling:** `grep -n "ruff|mypy|black|isort" mcp-brain-bridge/pyproject.toml` — no match; skip (no lint tool declared).
- **V1 advisory gate:** `grep -n "usage\\[" mcp-brain-bridge/server.py` + `grep -n "sum(\\|\\.values()" mcp-brain-bridge/server.py | grep -i usage` — no numeric consumers over usage; verdict "usage type widening has no numeric consumers". Readers use `.get`.
- **Full suite (RTK):** `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py tests/test_brain_responses_alignment.py -q` — exit 0, 396 passed in 4.47s.
- **Smoke:** live brain_turn under task 412 — status REPORT, usage reasoning_tokens=6115.
- **Lint:** `lint_task_file` on `tasks/qa/412-deepseek-chatcompletions-hardening.md` — pass.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `testing-verification` applied and evidence recorded

## Risk & Rollback

- **Risk:** Output token default raised; larger bills if max effort overused. Mitigated by .env override (code default stays 32768).
- **Rollback plan:** Revert .env BRAIN_MAX_TOKENS to 32768; revert server.py usage-details edit.

---

## Execution Log & Reasoning

Implementation completed 2026-11-22. Changes:
- .env: BRAIN_API_BASE=/go/chat, BRAIN_UPSTREAM_MODE=chat_completions, BRAIN_MODEL=deepseek-v4.1-flash (all tiers), BRAIN_REASONING_EFFORT=max, BRAIN_MAX_TOKENS=131072.
- mcp-brain-bridge/server.py: _convert_chat_completions_to_responses_data now passes through input_tokens_details (cached_tokens/prompt_cache_hit_tokens) and output_tokens_details (reasoning_tokens etc.); added warning branch for dropped input item types.
- Memory updated: brain-model-routing + brain-deepseek-fixes.
- Tests: 390 passed. Smoke: XML_EXTRACTED, reasoning_tokens=9111.

### QA rejection round 1 fixes

- Added 6 regression tests: T1 OpenAI nested details passthrough, T2 DeepSeek top-level folding, T3 nested-over-top-level precedence, T4 malformed/absent details (no leak), T5 unsupported input item dropped with exactly one warning, T6 non-dict item reported without crashing.
- CHANGELOG.md: appended Fixed entry under [Unreleased] for usage-details passthrough + dropped-item warning.
- V1-V3 advisory gate: grep for sum()/.values() over usage returned no matches; readers use .get; verdict "usage type widening has no numeric consumers". V4 (bool isinstance) remains advisory, pre-existing.
- Smoke evidence: reasoning_tokens=6115 from live brain_turn under task 412.
- DECISIONS.md: appended dated ADR for chat-completions usage details passthrough.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index faf9d81..f9f1a60 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -25,6 +25,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **OpenUI render contract hardened against stringified tool arguments:** the executor and the Brain-facing hands-protocol fragment now pin the `openchamber_render` call envelope — `action: "render.page"` with `parameters` as a real object, never a JSON-encoded string, one payload inside `parameters`, and a rebuild-not-retry directive for `parameters: Expected object`. The executor's Output Contract was corrected to place `ui`/`html` inside `parameters` instead of naming them as flat fields. The tool catalog row in `docs/openchamber.md`, four living-folder docs and their ADRs were updated, `01-system_version.md` bumped 9.90.0 to 9.90.1, both `system-prompt.md` and the stage artifacts regenerated, and a regression test added. No product code, no commit.
 
+- **Brain bridge chat-completions hardening (task 412):** the chat-completions converter now passes usage details through (`input_tokens_details.cached_tokens`, `output_tokens_details.reasoning_tokens`), folding DeepSeek top-level `prompt_cache_hit_tokens`/`reasoning_tokens` into the nested shape when absent, ignoring non-dict detail payloads, and logging a warning when an unsupported Responses input item is dropped. Output token budget raised to 131072 for max-effort turns via `BRAIN_MAX_TOKENS`. Six regression tests added; 396 passed.
+
 ## [9.90.0] - 2026-11-20
 
 ### Added
diff --git a/mcp-brain-bridge/DECISIONS.md b/mcp-brain-bridge/DECISIONS.md
index 414e5fd..172901c 100644
--- a/mcp-brain-bridge/DECISIONS.md
+++ b/mcp-brain-bridge/DECISIONS.md
@@ -128,3 +128,13 @@
 - **Decision:** `_compaction_threshold` now rejects values below 1000 with a readable error, keeping the default 100000 unchanged. `_CHAT_UNSUPPORTED_FIELDS` gains `prompt_cache_key` and `context_management` so chat-completions mode logs a warning when it drops them. Both changes are additive validation and logging; the default wire bytes are unchanged.
 - **Consequences:** a misconfigured threshold now fails locally before any model call; the two cache fields can no longer vanish silently in chat-completions mode. Two tests in `tests/test_brain_responses_alignment.py` pin both behaviors (TDD red before the source change, green after).
 - **Rollback:** restore the `val <= 0` guard and the original seven-field warning tuple; remove the two tests.
+
+## 2026-11-22 — Chat-completions usage details pass through to Responses shape
+
+**Context:** DeepSeek V4.1 Flash reports cache hits as top-level `prompt_cache_hit_tokens` and can report `reasoning_tokens` at top level; OpenAI nests them under `*_tokens_details`.
+
+**Decision:** The converter folds nested details first, fills `cached_tokens` from `prompt_cache_hit_tokens` and `reasoning_tokens` from the top level only when absent, ignores non-dict detail payloads, and warns on dropped input item types.
+
+**Consequences:** Budget math can see cache hits and reasoning spend. Non-int values pass through untouched.
+
+**Rollback:** Revert the details block in `server.py`; usage reverts to prompt/completion/total only.
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index c452439..522ab56 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -5266,6 +5266,10 @@ def _convert_responses_to_chat_completions_body(body: dict[str, Any]) -> dict[st
 
     for item in raw_input or []:
         if not isinstance(item, dict):
+            logger.warning(
+                "chat converter: dropping unsupported input item type %r",
+                type(item).__name__,
+            )
             continue
         role = item.get("role")
         content = item.get("content")
@@ -5344,6 +5348,11 @@ def _convert_responses_to_chat_completions_body(body: dict[str, Any]) -> dict[st
                     "content": output_payload,
                 }
             )
+        else:
+            logger.warning(
+                "chat converter: dropping unsupported input item type %r",
+                item.get("type") if isinstance(item, dict) else type(item).__name__,
+            )
 
     chat_body["messages"] = messages
 
@@ -5663,7 +5672,7 @@ def _convert_chat_completions_to_responses_data(
     # the total. Presence of the key means "the provider reported a number".
     usage = chat_resp.get("usage")
     if isinstance(usage, dict):
-        mapped_usage: dict[str, int] = {}
+        mapped_usage: dict[str, Any] = {}
         if isinstance(usage.get("prompt_tokens"), int):
             mapped_usage["input_tokens"] = usage["prompt_tokens"]
         if isinstance(usage.get("completion_tokens"), int):
@@ -5677,6 +5686,29 @@ def _convert_chat_completions_to_responses_data(
             mapped_usage["total_tokens"] = (
                 mapped_usage["input_tokens"] + mapped_usage["output_tokens"]
             )
+        # Pass through usage details so reasoning-token spend and cache
+        # hits (DeepSeek prompt_cache_hit_tokens / OpenAI cached_tokens) are
+        # visible to the budget math instead of being silently dropped.
+        details_in: dict[str, Any] | None = None
+        prompt_details = usage.get("prompt_tokens_details")
+        if isinstance(prompt_details, dict):
+            details_in = dict(prompt_details)
+        # DeepSeek reports prompt_cache_hit_tokens at the top level rather
+        # than under prompt_tokens_details.cached_tokens.
+        if isinstance(usage.get("prompt_cache_hit_tokens"), int):
+            details_in = details_in or {}
+            details_in.setdefault("cached_tokens", usage["prompt_cache_hit_tokens"])
+        if details_in:
+            mapped_usage["input_tokens_details"] = details_in
+        details_out: dict[str, Any] = {}
+        completion_details = usage.get("completion_tokens_details")
+        if isinstance(completion_details, dict):
+            details_out.update(completion_details)
+        # DeepSeek may also surface reasoning tokens at the top level.
+        if isinstance(usage.get("reasoning_tokens"), int):
+            details_out.setdefault("reasoning_tokens", usage["reasoning_tokens"])
+        if details_out:
+            mapped_usage["output_tokens_details"] = details_out
         if mapped_usage:
             resp_data["usage"] = mapped_usage
 
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index 23a990a..b28fcd9 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -5908,3 +5908,41 @@ def test_tool_calls_wired_into_brain_turn_result(tmp_path, monkeypatch):
     ]
     # Text channel still carries the call as prose.
     assert "question" in res["output"]
+
+
+from unittest import mock
+
+
+def test_unsupported_input_items_are_dropped_with_exactly_one_warning():
+    """Unsupported Responses input items must be dropped with one warning, not
+    silently. Exactly-one also catches an over-eager branch that warns on items
+    the converter actually handles."""
+    body = {
+        "model": "deepseek-v4.1-flash",
+        "input": [
+            {"role": "user", "content": "keep me"},
+            {"type": "qa_unknown_item_type", "content": "drop me"},
+        ],
+    }
+    with mock.patch.object(bridge.logger, "warning") as warning_spy:
+        chat_body = bridge._convert_responses_to_chat_completions_body(body)
+
+    assert warning_spy.call_count == 1
+    log_args = warning_spy.call_args.args
+    assert "dropping unsupported input item type" in log_args[0]
+    assert log_args[1] == "qa_unknown_item_type"
+    serialized = [str(m) for m in chat_body["messages"]]
+    assert any("keep me" in m for m in serialized)
+    assert not any("drop me" in m for m in serialized)
+
+
+def test_non_dict_input_items_are_reported_not_crashing():
+    """A bare string item must hit the logging guard, never an AttributeError."""
+    with mock.patch.object(bridge.logger, "warning") as warning_spy:
+        chat_body = bridge._convert_responses_to_chat_completions_body({
+            "model": "deepseek-v4.1-flash",
+            "input": [{"role": "user", "content": "keep me"}, "stray-item"],
+        })
+    assert warning_spy.call_count == 1
+    assert warning_spy.call_args.args[1] == "str"
+    assert len(chat_body["messages"]) >= 1
diff --git a/tests/test_brain_responses_alignment.py b/tests/test_brain_responses_alignment.py
index 3497ffa..4a8fee3 100644
--- a/tests/test_brain_responses_alignment.py
+++ b/tests/test_brain_responses_alignment.py
@@ -521,3 +521,93 @@ def test_chat_conversion_warns_on_responses_only_cache_fields(caplog):
     assert "context_management" in logged
     assert "prompt_cache_key" not in chat
     assert "context_management" not in chat
+
+# QA regression coverage for the chat-completions usage-details passthrough.
+# Guards Task 412: cached_tokens and reasoning_tokens must reach budget math.
+
+from unittest import mock
+
+_ASSISTANT_CHOICE = {
+    "index": 0,
+    "message": {"role": "assistant", "content": "ok"},
+    "finish_reason": "stop",
+}
+
+
+def _convert(chat_resp: dict):
+    """Call the chat->responses converter with the same minimal arguments used
+    by the other alignment tests. Isolated here so a signature change touches
+    exactly one line."""
+    return bridge._convert_chat_completions_to_responses_data(chat_resp)
+
+
+def _chat_resp(usage: dict) -> dict:
+    """Build a minimal chat-completion envelope carrying the given usage block."""
+    return {
+        "id": "chatcmpl-qa",
+        "object": "chat.completion",
+        "model": "deepseek-v4.1-flash",
+        "choices": [_ASSISTANT_CHOICE],
+        "usage": usage,
+    }
+
+
+def test_usage_details_openai_style_are_passed_through():
+    """OpenAI nests cache hits and reasoning tokens under *_tokens_details."""
+    data = _convert(_chat_resp({
+        "prompt_tokens": 100,
+        "completion_tokens": 40,
+        "total_tokens": 140,
+        "prompt_tokens_details": {"cached_tokens": 80},
+        "completion_tokens_details": {"reasoning_tokens": 25},
+    }))
+    usage = data["usage"]
+    assert usage["input_tokens"] == 100
+    assert usage["output_tokens"] == 40
+    assert usage["input_tokens_details"]["cached_tokens"] == 80
+    assert usage["output_tokens_details"]["reasoning_tokens"] == 25
+
+
+def test_usage_details_deepseek_top_level_fields_are_folded_in():
+    """DeepSeek reports prompt_cache_hit_tokens and reasoning_tokens at top level."""
+    data = _convert(_chat_resp({
+        "prompt_tokens": 100,
+        "completion_tokens": 40,
+        "total_tokens": 140,
+        "prompt_cache_hit_tokens": 64,
+        "reasoning_tokens": 12,
+    }))
+    usage = data["usage"]
+    assert usage["input_tokens_details"]["cached_tokens"] == 64
+    assert usage["output_tokens_details"]["reasoning_tokens"] == 12
+
+
+def test_nested_details_win_over_top_level_deepseek_fields():
+    """Nested *_tokens_details values must take precedence over top-level aliases."""
+    data = _convert(_chat_resp({
+        "prompt_tokens": 100,
+        "completion_tokens": 40,
+        "total_tokens": 140,
+        "prompt_tokens_details": {"cached_tokens": 90},
+        "prompt_cache_hit_tokens": 64,
+        "completion_tokens_details": {"reasoning_tokens": 30},
+        "reasoning_tokens": 12,
+    }))
+    usage = data["usage"]
+    assert usage["input_tokens_details"]["cached_tokens"] == 90
+    assert usage["output_tokens_details"]["reasoning_tokens"] == 30
+
+
+def test_malformed_or_absent_details_do_not_add_detail_keys():
+    """Non-dict detail payloads are ignored and must never raise or leak keys."""
+    data = _convert(_chat_resp({
+        "prompt_tokens": 10,
+        "completion_tokens": 5,
+        "total_tokens": 15,
+        "prompt_tokens_details": "not-a-dict",
+        "completion_tokens_details": ["not", "a", "dict"],
+    }))
+    usage = data["usage"]
+    assert usage["input_tokens"] == 10
+    assert "input_tokens_details" not in usage
+    assert "output_tokens_details" not in usage
```
<!-- END_GIT_DIFF -->
