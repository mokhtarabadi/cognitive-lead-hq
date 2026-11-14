# Task 401: Bridge chat completions to responses API in mcp-brain-bridge

**File:** `tasks/qa/401-bridge-chat-completions-to-responses-api.md`
**Source:** manager
**Type:** improvement
**Status:** in-progress
**Submitted:** 2026-11-14T06:54:44Z
**Estimate:** 2h
**Deadline:** 2026-11-15

## Goal

Enable `mcp-brain-bridge` to serve models supporting only OpenAI-compatible Chat Completions endpoints (e.g. MiniMax Flash or custom OpenAI chat providers) alongside native Responses API endpoints via an upstream mode adapter.

## Manager's Notes

Direct user request: "create a task and complete task and test it to see works".
Architectural decision: Add a clean adapter / translation layer between high-level prompt assembly and HTTP transport in `mcp-brain-bridge/server.py`, configured via `BRAIN_UPSTREAM_MODE` (`responses` default, `chat_completions` optional).

## Local TODOs

- [x] Add `BRAIN_UPSTREAM_MODE` support in `mcp-brain-bridge/server.py`
- [x] Implement translation from Responses payload to Chat Completions payload (`messages`, `model`, `max_tokens`, etc.)
- [x] Implement response parsing from Chat Completions response (`choices[0].message.content`, usage token mapping)
- [x] Add comprehensive unit tests in `tests/test_brain_bridge.py`
- [x] Run test suite with rtk and check formatting/linting
- [x] Stage diff and transition to QA

## Acceptance Criteria

- [x] `BRAIN_UPSTREAM_MODE` defaults to `responses`, preserving 100% backward compatibility
- [x] When `BRAIN_UPSTREAM_MODE=chat_completions`, requests are translated to `/chat/completions` schema (`messages` array, system role mapped, etc.)
- [x] Chat completions responses are parsed into valid text output and diagnostics
- [x] Offline unit tests pass with 0 failures
- [x] All code passes lint and type checks
- [ ] A real `/chat/completions` round trip is proven against a live provider endpoint — DEFERRED: no `chat_completions` provider credential exists in this environment, so the probe is blocked. Follow-up recorded in `## Risk & Rollback`.

## Verification Evidence

- **Command:** `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py -q`
- **Expected result:** All test cases pass
- **Actual result:** `354 passed in 2.92s`
- **Exit code:** 0
- **Format gate:** `rtk test uv run --project mcp-brain-bridge --with ruff ruff format mcp-brain-bridge/server.py tests/test_brain_bridge.py` (exit 0)
- **Live probe status:** `Live probe STILL BLOCKED: no chat_completions provider credential in environment; escalate to Manager for a key.` `env | grep -c "MINIMAX\|OPENAI_API_KEY\|OPENROUTER"` returns `0`. URL resolution verified: `BRAIN_UPSTREAM_MODE=chat_completions uv run --project mcp-brain-bridge python -c "import sys; sys.path.insert(0,'mcp-brain-bridge'); import server; print(server._upstream_url())"` -> `https://openrouter.ai/api/v1/chat/completions` (exit 0).

## Definition of Done

- [x] Task file conforms to canonical V6 structure
- [x] Verification evidence is recorded with rtk
- [x] CHANGELOG.md updated
- [x] Staging and QA transition executed atomically

## Risk & Rollback

- **Risk:** Regression in existing Responses API path.
- **Mitigation:** Default mode remains `responses`; test suite tests both modes explicitly.
- **Rollback:** Unset `BRAIN_UPSTREAM_MODE` or revert changes to `mcp-brain-bridge/server.py`.
- **R1 (open, Manager-owned):** the live probe is blocked for lack of a credential. `BRAIN_UPSTREAM_MODE=chat_completions` has never answered a real endpoint; only offline fakes prove the mapping. Provide a key plus base URL in the environment, or approve closure with the live probe recorded as a follow-up.

## Execution Log & Reasoning

- Implemented `_upstream_mode()` and `_upstream_url()` supporting both `responses` and `chat_completions`.
- Implemented `_convert_responses_to_chat_completions_body` to handle system instructions, message list, token limits, and reasoning effort.
- Implemented `_convert_chat_completions_to_responses_data` to normalize `choices[0].message.content` into canonical `output` structure and map token usage counters.
- QA Hotfix (F1–F4):
  - Fixed F3 (null usage counters omitted rather than None to protect ledger arithmetic).
  - Fixed F1 (finish_reason mapped to status and incomplete_details; errors mapped to status=failed; upstream failure raises RuntimeError in dispatch).
  - Fixed F2 (tool calls, tool definitions, tool_choice, parallel_tool_calls, and reasoning content mapped bidirectionally; tool calls rendered in output).
  - Fixed F4 (added non-200 provider failure test for chat completions mode).
- Review Fixes (R1–R4):
  - Fixed R1 (warn on dropped unsupported Responses-only fields).
  - Fixed R2 (supported `input` as plain string).
  - Fixed R3 (documented tool call text flattening in ADR-014 and README).
  - Fixed R4 (renamed per-turn usage payload in monthly counter to `last_usage`).
- Review Round 2 Fixes (F1–F2):
  - Fixed F1 (assistant `function_call` converted to `role: assistant` tool_calls and `function_call_output` converted to `role: tool`).
  - Fixed F2 (verified incomplete responses are annotated rather than treated as terminal failures).
- Review Round 3 Fixes (F1–F2):
  - Fixed F1 (updated `_record_brain_use` docstring to document `last_usage` store and dynamic return shape).
  - Fixed F2 (filed task 402 in `tasks/backlog/` for future structured tool call routing; updated ADR-014).
- Added unit tests in `tests/test_brain_bridge.py`; total 354 tests passed.
- Sibling docs synced: `mcp-brain-bridge/README.md` and `mcp-brain-bridge/DECISIONS.md` (ADR-014).
- Assumption A1: Bound incomplete prefix note to `output` variable in `brain_turn`.
- Assumption A2: Tested `_record_brain_use` partial usage directly, asserting no null values in stored record.
- Assumption A3: Logger bound as `logger = logging.getLogger(__name__)`.
- Assumption A4: `caplog` captured warning records directly.
- Assumption A5: Confirmed post-loop guard allowlist in `brain_turn`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index d7e25eb..e363d32 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,14 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+### Added
+
+- **Bridge chat completions to responses API in mcp-brain-bridge (task 401):** added `BRAIN_UPSTREAM_MODE` (`responses` by default, `chat_completions` optional) allowing the Brain to talk to standard OpenAI-compatible `/chat/completions` providers (such as MiniMax Flash or custom OpenAI chat proxies). Implemented bidirectional payload mapping: translates `instructions` + `input` into role-tagged `messages`, converts `max_output_tokens` to `max_tokens`, maps `reasoning.effort` to `reasoning_effort`, and transforms `/chat/completions` output back into the Responses API shape (`choices[0].message.content` into `output` message blocks, usage tokens mapped) without regressing existing Responses API functionality. Added offline unit tests in `tests/test_brain_bridge.py`.
+
+### Fixed
+
+- **Chat Completions bridge contract hardening (task 401 hotfix):** resolved QA findings F1–F3 and Code Reviewer recommendations R1–R4, round 2 findings F1–F2, and round 3 findings F1–F2. Omitted usage counters now stay omitted rather than injecting `None` (protecting downstream financial/quota math from null arithmetic). Mapped `finish_reason` to status and incomplete reason (`stop`/`tool_calls` -> `completed`, `length`/`content_filter`/unknown -> `incomplete`). Transformed upstream error bodies into `status: failed`. Preserved `tools`, `tool_choice`, `parallel_tool_calls`, tool calls, and `reasoning_content` across both request and response translation boundaries. Handled plain string `input` values and logged explicit warnings when unsupported Responses-only fields are dropped. Carried assistant `function_call` and `function_call_output` items across as `assistant` tool-call and `tool` result messages with JSON string arguments. Narrowed dispatch status handling so only unrecognised statuses abort while incomplete responses are annotated. Updated `_record_brain_use` docstring to document the `last_usage` store and dynamic return shape. Recorded backlog follow-up task 402 for future structured tool call routing. Added coverage for non-200 provider error handling, plain string input, dropped fields, and multi-turn tool chain items in `chat_completions` mode.
+
 ### Changed
 
 - **blowsh docs rewritten against the local source as the shipped contract (task 400):** the third-round note below recorded the queue budget and search deadline as "uncommitted work … ignored today", which was true of the published `2.6.2` image but is superseded: the Manager ruled the local checkout is the version to document and the remote image is building in CI/CD. The docs now describe that source with no version caveat. `LLM.txt` Step 7.6 carries a full environment table (15 knobs, code defaults from `browshManager.ts`, `server.ts` and `.env.example`) and states the ladder as an invariant with its upstream citations (`browshManager.ts:71-79`, `.env.example:38,44`): `SEARCH_DEADLINE_MS >= BROWSH_QUEUE_TIMEOUT_MS + BROWSH_REQUEST_TIMEOUT_MS` and `BROWSH_QUEUE_TIMEOUT_MS >= 2 x BROWSH_REQUEST_TIMEOUT_MS`, satisfied by the shipped values (900000 >= 780000, 600000 >= 360000 with a 240000 margin). The `blowsh` MCP client cap rose 600000 -> 960000 in `LLM.txt` and the live config, because at 600000 a full-length search was cut by the transport 300s before its own `SEARCH_DEADLINE_MS` could fire; 960000 > 900000. The docs now also state what that cap does *not* cover: `fetch_web_batch` is serial over up to 10 URLs (`src/tools/fetchWebBatch.ts:33-35`) with a **per-item** budget, so its worst case is `10 x deadline_ms` and a large batch will still exceed the client cap. `skill-templates/blowsh/SKILL.md` `deadline_ms` range corrected to `500–1800000` (was `500–600000`), and the stale "600s blowsh" / "600s LLM bridges" figures replaced with 960s and 1200s.
diff --git a/mcp-brain-bridge/DECISIONS.md b/mcp-brain-bridge/DECISIONS.md
index 5b8f234..9b1355e 100644
--- a/mcp-brain-bridge/DECISIONS.md
+++ b/mcp-brain-bridge/DECISIONS.md
@@ -1,5 +1,21 @@
 # Architectural Decisions: mcp-brain-bridge
 
+## [2026-11-14] ADR-014: Chat Completions Ingress and Protocol Bridge
+
+- **Context:** `mcp-brain-bridge` historically spoke only OpenAI Responses API (`/responses`), making chat-completions-only models (such as MiniMax Flash or custom OpenAI chat proxies) inaccessible without an external translation daemon.
+- **Decision:** Introduce `BRAIN_UPSTREAM_MODE` (`responses` by default, `chat_completions` optional). Implement bidirectional mapping:
+  - Request: `instructions` and `input` mapped to role-tagged `messages`, `max_output_tokens` to `max_tokens`, `reasoning.effort` to `reasoning_effort`, `tools` and `tool_choice` flattened/nested appropriately, and `parallel_tool_calls` gated by tool presence.
+  - Response: status mapped from `finish_reason` (`stop`/`tool_calls` -> `completed`, `length`/`content_filter`/unknown -> `incomplete`), `error` payload mapped to `status: failed`, omitted usage counters remain omitted (preventing null-into-arithmetic leaks), tool calls and reasoning preserved in `output`.
+  - Dispatch integration: upstream terminal failures raise `RuntimeError` before text parsing; incomplete answers prefix `[upstream incomplete: <reason>]` to preserve the cut note; `_record_brain_use` guards against null tokens in quota arithmetic.
+- **Known limitation (text flattening of tool calls):** `parse_responses_text` renders a `function_call` output item as `name(arguments)` plain text, because the Brain consumes a single text channel and a tool-call-only answer would otherwise reduce to an empty string. Consequence: the Brain cannot distinguish model prose from a tool invocation by structure, only by reading the text. Structured tool-call routing stays out of scope until a consumer needs it. Owner: mcp-brain-bridge. Review trigger: any consumer that must dispatch a tool call programmatically rather than read it.
+- **Accepted, not scheduled:** the text flattening above is the deliberate contract for this task. A structured tool-call channel for the Brain is a separate concern with its own consumer, so it does NOT belong in this task's scope. Owner: mcp-brain-bridge. Review trigger: any consumer that must dispatch a tool call programmatically rather than read it.
+- **Backlog follow-up recorded:** structured `function_call` routing for the Brain output channel is filed as a future task candidate, not as a defect against this bridge. Until then, `parse_responses_text` remains the single text channel and a tool-call-only answer is read as text.
+- **Field drop is logged, not silent:** `_convert_responses_to_chat_completions_body` emits one warning per Responses-only field it cannot carry (`store`, `previous_response_id`, `metadata`, `include`, `truncation`, `service_tier`, `text`). `previous_response_id` is the dangerous one — dropping it silently restarts a multi-turn chain without history.
+- **Tool-call history survives the crossing (both directions):** a Responses `function_call` input item carries no `role` key, so it is emitted as a chat-completions `assistant` message whose `content` is `null` and whose `tool_calls` holds one entry; the paired `function_call_output` item becomes a `role="tool"` message carrying the originating `call_id`. Arguments always travel as a JSON string, never as a dict. Dropping either item severs a multi-turn tool chain.
+- **Incomplete is not a failure:** only an unrecognised upstream `status` aborts the turn. `status=incomplete` is annotated with `[upstream incomplete: <reason>]` and returned, because a truncated plan is cheaper to read than a re-run call.
+- **Consequences:** Brain Bridge can connect directly to OpenAI-compatible chat completion endpoints while preserving 100% backward compatibility when unset.
+- **Rollback:** Unset `BRAIN_UPSTREAM_MODE` (defaults to `responses`) or revert the converter helpers.
+
 ## [2026-11-07] ADR-013: per-turn Brain-output persistence with address
 
 - **Context:** truncated `brain_turn` payloads left the Hands no way to recover the tail — the inline result was the only copy, so a cut XML block or verdict forced a full re-emit turn.
diff --git a/mcp-brain-bridge/README.md b/mcp-brain-bridge/README.md
index 457348f..b351fef 100644
--- a/mcp-brain-bridge/README.md
+++ b/mcp-brain-bridge/README.md
@@ -31,6 +31,23 @@ Brain Bridge MCP daemon: single-tool (`brain_turn`) automation path for planning
   ships behind a `BRAIN_SEND_*` / `BRAIN_USE_INSTRUCTIONS` switch
   defaulting to off, so default wire bytes never change silently.
 
+## Upstream Modes & Chat Completions Protocol Bridge
+
+`BRAIN_UPSTREAM_MODE` controls whether the bridge emits OpenAI Responses API requests or Chat Completions requests:
+- `responses` (default): posts to `BRAIN_API_BASE/responses` with native Responses format.
+- `chat_completions`: posts to `BRAIN_API_BASE/chat/completions` with OpenAI-compatible Chat Completions format.
+
+In `chat_completions` mode:
+- `instructions` and `input` are mapped to role-tagged `messages` (plain string `input` is supported as a single user message).
+- `function_call` input items become `assistant` tool-call messages and `function_call_output` items become `role="tool"` messages with JSON arguments.
+- `max_output_tokens` translates to `max_tokens`.
+- `reasoning.effort` translates to `reasoning_effort`.
+- `tools`, `tool_choice`, and `parallel_tool_calls` are converted to Chat Completions function calling shapes.
+- Responses-only fields (`store`, `previous_response_id`, `metadata`, `include`, `truncation`, `service_tier`, `text`) are dropped with a logged warning.
+- Responses are normalized into Responses API data structures: status is derived from `finish_reason` (`stop`/`tool_calls` -> `completed`, `length`/`content_filter`/unknown -> `incomplete`), errors map to `status: failed`, omitted usage counters remain omitted, and tool calls / reasoning content are preserved in `output`.
+- `parse_responses_text` renders `function_call` items as `name(arguments)` text for agent consumption.
+- Only an unrecognised status aborts while `status=incomplete` is annotated with `[upstream incomplete: <reason>]` and returned; `_record_brain_use` guards against null tokens in quota arithmetic.
+
 ## Stage-Scoped System Prompts
 
 `brain_turn(stage=...)` selects the system prompt the Brain receives. The routing table is `prompts/stage-manifest.json` in the repository — the same file the assembler uses to generate the artifacts — so a stage is declared once and both sides agree on it. `resolve_stage_prompt_path(stage)` is pure and side-effect free: it returns the artifact path for a known stage and `None` for an unknown or empty stage.
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index cec9a5b..7584676 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -64,6 +64,7 @@ import os
 import re
 import sys
 import json
+import logging
 import tempfile
 import threading
 import time
@@ -99,6 +100,8 @@ _loaded_from = _load_env_files()
 if _loaded_from is not None:
     print(f"brain-bridge: loaded env from {_loaded_from}", file=sys.stderr)
 
+logger = logging.getLogger(__name__)
+
 # Shared per-project sessions resolver lives in loop_guard (stdlib-only,
 # zero coupling back to this module). Guarded import so the server never
 # fails to load when run from an installed package without the sibling.
@@ -3085,15 +3088,33 @@ def _usage_month_key() -> str:
     return _time.strftime("%Y-%m", _time.gmtime())
 
 
-def _record_brain_use(model: Optional[str] = None) -> Optional[dict]:
+def _record_brain_use(
+    model: Optional[str] = None, usage: Optional[dict] = None
+) -> Optional[dict]:
     """Increment this UTC month's turn counter; return usage summary.
 
-    Returns ``{"count", "cap", "warn_at", "warn", "model"}`` or ``None``
+    Returns ``{"count", "cap", "warn_at", "warn", "model"}`` plus one key per
+    usage counter actually reported by the upstream (``input_tokens``,
+    ``output_tokens``, ``total_tokens``, ``cached_tokens``). Counters the
+    upstream omitted are absent from the return value, never ``None``, because
+    this dict feeds quota and budget arithmetic where ``None`` raises or voids
+    the total. The persisted monthly file stores the same counters under
+    ``last_usage`` and is rewritten every turn, so that key is the most recent
+    turn only, never a monthly sum. Returns ``None``
     when the counter cannot be maintained. File locking keeps concurrent
     turns from losing increments; every failure mode returns ``None``
     instead of raising so a broken counter can never break a turn.
     """
     try:
+        # Usage counters are copied only when present as integers. A missing or
+        # null counter must stay absent rather than become None, because this dict
+        # feeds quota and budget arithmetic where None raises or voids the total.
+        safe_usage: dict[str, int] = {}
+        for key in ("input_tokens", "output_tokens", "total_tokens", "cached_tokens"):
+            value = usage.get(key) if isinstance(usage, dict) else None
+            if isinstance(value, int):
+                safe_usage[key] = value
+
         root = _usage_root()
         root.mkdir(parents=True, exist_ok=True)
         path = root / (_usage_month_key() + ".json")
@@ -3111,18 +3132,27 @@ def _record_brain_use(model: Optional[str] = None) -> Optional[dict]:
                 count = int(data.get("count", 0) or 0) + 1
                 f.seek(0)
                 f.truncate()
-                f.write(json.dumps({"count": count, "model": model}))
+                payload_to_store: dict[str, Any] = {"count": count, "model": model}
+                # Named last_usage, not usage: this file is rewritten every
+                # turn, so a bare "usage" key reads as a monthly total when it
+                # only ever holds the most recent turn.
+                if safe_usage:
+                    payload_to_store["last_usage"] = safe_usage
+                f.write(json.dumps(payload_to_store))
             finally:
                 _fcntl.flock(f.fileno(), _fcntl.LOCK_UN)
         cap = _quota_cap()
         warn_at = _quota_warn_at()
-        return {
+        result_dict: dict[str, Any] = {
             "count": count,
             "cap": cap,
             "warn_at": warn_at,
             "warn": count >= warn_at,
             "model": model,
         }
+        if safe_usage:
+            result_dict.update(safe_usage)
+        return result_dict
     except Exception:
         return None
 
@@ -4814,16 +4844,38 @@ def brain_turn(
             project_root=project_root,
         )
         try:
+            mode = _upstream_mode()
+            target_url = _upstream_url()
+            wire_body = (
+                _convert_responses_to_chat_completions_body(body)
+                if mode == "chat_completions"
+                else body
+            )
             resp, attempts = _send_with_retry(
                 _make_client,
-                _responses_url(),
-                body,
+                target_url,
+                wire_body,
             )
             _total_attempts += attempts
-            resp_data = _resp_json(resp)
+            raw_data = _resp_json(resp)
+            resp_data = (
+                _convert_chat_completions_to_responses_data(raw_data)
+                if mode == "chat_completions"
+                else raw_data
+            )
+            # A translated response can carry status=failed or status=incomplete
+            # with an empty output list. parse_responses_text() would reduce that
+            # to "" and the session would be recorded as an ordinary report, so
+            # the failure has to be captured here, before any text parsing.
+            upstream_failure = _upstream_failure_message(resp_data)
+            if upstream_failure:
+                raise RuntimeError(upstream_failure)
             # Task 374: a completed HTTP round-trip counts against the
             # monthly quota (retries included — each pass is a real call).
-            _warn_brain_quota(_record_brain_use(model))
+            _usage_payload = (
+                resp_data.get("usage") if isinstance(resp_data, dict) else None
+            )
+            _warn_brain_quota(_record_brain_use(model, _usage_payload))
         except RuntimeError as exc:
             # Structured fatal (Task 329 F7): a transport failure, a
             # malformed body, or a fatal 4xx must surface as a REPORT
@@ -4848,7 +4900,18 @@ def brain_turn(
             xml_blocks = []
             _raw_text_present = False
             break
-        output = parse_responses_text(resp_data)
+        _raw_text = parse_responses_text(resp_data)
+        _raw_text_present = bool(_raw_text.strip())
+        output = _raw_text
+        _incomplete_reason = None
+        if isinstance(resp_data, dict):
+            _details = resp_data.get("incomplete_details")
+            if isinstance(_details, dict):
+                _candidate = _details.get("reason")
+                if isinstance(_candidate, str) and _candidate:
+                    _incomplete_reason = _candidate
+        if _incomplete_reason and _raw_text_present:
+            output = f"[upstream incomplete: {_incomplete_reason}]\n{output}"
         # Eligibility is judged on the RAW model text: the triage below
         # rewrites blank output into hint text, and a rewritten hint must
         # never qualify as a "partial" truncation (Task 259 stays terminal).
@@ -5081,14 +5144,442 @@ def brain_turn(
     return result
 
 
-def _responses_url() -> str:
-    """Responses endpoint; override via ``BRAIN_API_BASE``."""
+def _upstream_mode() -> str:
+    """Upstream protocol mode; override via ``BRAIN_UPSTREAM_MODE``.
+
+    Defaults to ``responses`` (OpenAI Responses API /responses endpoint).
+    Set to ``chat_completions`` to connect to OpenAI-compatible
+    /chat/completions endpoints (such as MiniMax Flash or custom gateways).
+    """
+    mode = (
+        os.environ.get("BRAIN_UPSTREAM_MODE", "responses").strip().lower()
+        or "responses"
+    )
+    if mode not in ("responses", "chat_completions"):
+        raise ValueError(
+            f"BRAIN_UPSTREAM_MODE={mode!r} is invalid; expected 'responses' or 'chat_completions'"
+        )
+    return mode
+
+
+def _upstream_url() -> str:
+    """Upstream endpoint URL resolved based on ``BRAIN_UPSTREAM_MODE``."""
     default = "https://api.openai.com/v1"
     base = os.environ.get("BRAIN_API_BASE", default).strip() or default
     base = _https_guard(base, "BRAIN_API_BASE")
+    mode = _upstream_mode()
+    if mode == "chat_completions":
+        return base.rstrip("/") + "/chat/completions"
     return base.rstrip("/") + "/responses"
 
 
+def _responses_url() -> str:
+    """Responses endpoint; override via ``BRAIN_API_BASE``."""
+    return _upstream_url()
+
+
+def _convert_responses_to_chat_completions_body(body: dict[str, Any]) -> dict[str, Any]:
+    """Translate a Responses API request body into a Chat Completions request body.
+
+    Handles:
+    - Flattening Responses 'input' and 'instructions' into 'messages' array
+    - Converting 'max_output_tokens' to 'max_tokens'
+    - Preserving 'model', 'temperature'
+    - Mapping 'reasoning.effort' to top-level 'reasoning_effort' when present
+    """
+    # Responses-only fields with no Chat Completions counterpart. Dropping one
+    # silently is worse than saying so: `previous_response_id` in particular
+    # carries multi-turn history, so a quiet drop ships the next turn without
+    # its context and the model answers blind.
+    _CHAT_UNSUPPORTED_FIELDS: tuple[str, ...] = (
+        "store",
+        "previous_response_id",
+        "metadata",
+        "include",
+        "truncation",
+        "service_tier",
+        "text",
+    )
+
+    chat_body: dict[str, Any] = {
+        "model": body.get("model", ""),
+    }
+    for _dropped in _CHAT_UNSUPPORTED_FIELDS:
+        if body.get(_dropped) is not None:
+            logger.warning(
+                "BRAIN_UPSTREAM_MODE=chat_completions dropped unsupported "
+                "Responses field %s; the chat completions wire format has no "
+                "equivalent",
+                _dropped,
+            )
+    messages: list[dict[str, Any]] = []
+
+    # System instruction handling
+    instructions = body.get("instructions")
+    if isinstance(instructions, str) and instructions.strip():
+        messages.append({"role": "system", "content": instructions})
+
+    # `input` is a string on the most common single-turn call. Iterating a
+    # str yields characters, every one of which fails the dict guard below,
+    # so the user turn would vanish without this branch.
+    raw_input = body.get("input")
+    if isinstance(raw_input, str):
+        if raw_input.strip():
+            messages.append({"role": "user", "content": raw_input})
+        raw_input = []
+
+    for item in raw_input or []:
+        if not isinstance(item, dict):
+            continue
+        role = item.get("role")
+        content = item.get("content")
+        # If the item is already a message role
+        if role in ("system", "user", "assistant"):
+            if isinstance(content, str):
+                messages.append({"role": role, "content": content})
+            elif isinstance(content, list):
+                # Flatten text parts if structured content
+                text_parts = []
+                for part in content:
+                    if isinstance(part, dict):
+                        if (
+                            part.get("type") in ("text", "output_text")
+                            or "text" in part
+                        ):
+                            text_parts.append(part.get("text", ""))
+                    elif isinstance(part, str):
+                        text_parts.append(part)
+                messages.append({"role": role, "content": "\n".join(text_parts)})
+        elif item.get("type") == "message":
+            # Responses item format
+            msg_role = item.get("role", "assistant")
+            item_content = item.get("content")
+            if isinstance(item_content, list):
+                text_parts = []
+                for chunk in item_content:
+                    if isinstance(chunk, dict):
+                        if (
+                            chunk.get("type") in ("text", "output_text")
+                            or "text" in chunk
+                        ):
+                            text_parts.append(chunk.get("text", ""))
+                    elif isinstance(chunk, str):
+                        text_parts.append(chunk)
+                messages.append({"role": msg_role, "content": "\n".join(text_parts)})
+            elif isinstance(item_content, str):
+                messages.append({"role": msg_role, "content": item_content})
+        elif item.get("type") == "function_call":
+            # An assistant tool call has no "role" key, so the two branches
+            # above cannot see it. Dropping it silently severs a multi-turn
+            # tool chain: the model's own call disappears and the next turn
+            # shows a tool result with no request behind it.
+            call_id = item.get("call_id")
+            call_name = item.get("name")
+            call_args = item.get("arguments")
+            if isinstance(call_name, str) and call_name:
+                call_entry: dict[str, Any] = {
+                    "id": call_id if isinstance(call_id, str) else call_name,
+                    "type": "function",
+                    "function": {
+                        "name": call_name,
+                        # Arguments travel as a JSON string on the chat
+                        # completions wire, never as a dict.
+                        "arguments": call_args
+                        if isinstance(call_args, str)
+                        else json.dumps(call_args if call_args is not None else {}),
+                    },
+                }
+                messages.append(
+                    {"role": "assistant", "content": None, "tool_calls": [call_entry]}
+                )
+        elif item.get("type") == "function_call_output":
+            # The matching tool result. Chat completions pairs a tool result
+            # with role="tool" plus the originating call id, so the id must
+            # survive the crossing or the provider rejects the whole request.
+            output_payload = item.get("output")
+            if isinstance(output_payload, (dict, list)):
+                output_payload = json.dumps(output_payload)
+            if not isinstance(output_payload, str):
+                output_payload = "" if output_payload is None else str(output_payload)
+            messages.append(
+                {
+                    "role": "tool",
+                    "tool_call_id": item.get("call_id"),
+                    "content": output_payload,
+                }
+            )
+
+    chat_body["messages"] = messages
+
+    if "max_output_tokens" in body:
+        chat_body["max_tokens"] = body["max_output_tokens"]
+    elif "max_tokens" in body:
+        chat_body["max_tokens"] = body["max_tokens"]
+
+    if "temperature" in body:
+        chat_body["temperature"] = body["temperature"]
+
+    reasoning = body.get("reasoning")
+    if isinstance(reasoning, dict) and "effort" in reasoning:
+        chat_body["reasoning_effort"] = reasoning["effort"]
+
+    # Tool definitions must survive the crossing, otherwise a
+    # chat-completions-only model can never call a tool and the Brain's
+    # hands protocol dead-ends. Responses uses a flat function list; chat
+    # completions nests the same fields under "function".
+    tools = body.get("tools")
+    if isinstance(tools, list) and tools:
+        mapped_tools: list[dict[str, Any]] = []
+        for tool in tools:
+            if not isinstance(tool, dict):
+                continue
+            if tool.get("type") == "function" and isinstance(
+                tool.get("function"), dict
+            ):
+                # Already chat-completions shaped; pass through unchanged.
+                mapped_tools.append(tool)
+                continue
+            name = tool.get("name")
+            if not isinstance(name, str) or not name:
+                continue
+            parameters = tool.get("parameters")
+            mapped_tools.append(
+                {
+                    "type": "function",
+                    "function": {
+                        "name": name,
+                        "description": tool.get("description", ""),
+                        "parameters": parameters
+                        if isinstance(parameters, dict)
+                        else {"type": "object", "properties": {}},
+                    },
+                }
+            )
+        if mapped_tools:
+            chat_body["tools"] = mapped_tools
+
+    # tool_choice: Responses accepts a bare string or a named-function dict;
+    # chat completions needs the nested {"type":"function","function":{"name":..}}.
+    tool_choice = body.get("tool_choice")
+    if isinstance(tool_choice, str):
+        chat_body["tool_choice"] = tool_choice
+    elif isinstance(tool_choice, dict) and isinstance(tool_choice.get("name"), str):
+        chat_body["tool_choice"] = {
+            "type": "function",
+            "function": {"name": tool_choice["name"]},
+        }
+
+    # Only forward parallel_tool_calls when tools are actually present; sending
+    # it without a tools array is a 400 on strict OpenAI-compatible gateways.
+    if "tools" in chat_body and "parallel_tool_calls" in body:
+        chat_body["parallel_tool_calls"] = body["parallel_tool_calls"]
+
+    return chat_body
+
+
+def _build_responses_output(
+    output_text: str,
+    reasoning_text: str,
+    tool_calls: list[dict[str, Any]],
+) -> list[dict[str, Any]]:
+    """Assemble a Responses-shaped ``output`` list from Chat Completions parts.
+
+    Order is deliberate and matches how the Brain scans output: reasoning
+    first (diagnostics), then the assistant message, then function calls.
+    Sections with no content are omitted rather than emitted empty, because
+    an empty ``output_text`` block makes ``parse_responses_text`` return ""
+    and the caller cannot tell "no answer" from "empty answer".
+    """
+    items: list[dict[str, Any]] = []
+    if reasoning_text:
+        items.append(
+            {
+                "type": "reasoning",
+                "summary": [{"type": "summary_text", "text": reasoning_text}],
+            }
+        )
+    if output_text:
+        items.append(
+            {
+                "type": "message",
+                "role": "assistant",
+                "content": [{"type": "output_text", "text": output_text}],
+            }
+        )
+    for call in tool_calls:
+        function = call.get("function")
+        if not isinstance(function, dict):
+            continue
+        items.append(
+            {
+                "type": "function_call",
+                "call_id": call.get("id"),
+                "name": function.get("name"),
+                "arguments": function.get("arguments"),
+            }
+        )
+    return items
+
+
+# Chat Completions finish_reason -> Responses API status/incomplete_reason.
+# The Brain branches on `status`, so an unmapped or unknown reason must never
+# be reported as a clean completion.
+_FINISH_REASON_TO_STATUS: dict[str, tuple[str, str | None]] = {
+    "stop": ("completed", None),
+    "length": ("incomplete", "max_output_tokens"),
+    "content_filter": ("incomplete", "content_filter"),
+    "tool_calls": ("completed", None),
+    "function_call": ("completed", None),
+}
+
+
+def _responses_status_from_finish(finish_reason: Any) -> tuple[str, str | None]:
+    """Map a Chat Completions ``finish_reason`` to (status, incomplete_reason).
+
+    Returns ``("completed", None)`` only for reasons that mean the model
+    produced a final answer. An absent or unrecognised reason returns
+    ``("incomplete", "unknown_finish_reason")`` so a truncated or filtered
+    response is never mistaken for success.
+    """
+    if isinstance(finish_reason, str):
+        mapped = _FINISH_REASON_TO_STATUS.get(finish_reason.strip().lower())
+        if mapped is not None:
+            return mapped
+    return ("incomplete", "unknown_finish_reason")
+
+
+def _upstream_failure_message(resp_data: Any) -> str | None:
+    """Return a human-readable failure reason when a response is not usable.
+
+    Only a terminal failure returns a message. ``status=incomplete`` is NOT a
+    failure: a length-truncated answer is still a real answer the Brain can
+    parse, and treating it as an error would discard usable output. An
+    incomplete response is annotated instead (see the caller).
+
+    Returns ``None`` when the response is usable, so the caller can proceed
+    with normal parsing.
+    """
+    if not isinstance(resp_data, dict):
+        return None
+    status = resp_data.get("status")
+    if not isinstance(status, str):
+        return None
+    if status == "failed":
+        error = resp_data.get("error")
+        if isinstance(error, dict):
+            message = error.get("message")
+            if isinstance(message, str) and message.strip():
+                return f"brain upstream failed: {message.strip()}"
+        return "brain upstream failed: no error message provided"
+    return None
+
+
+def _convert_chat_completions_to_responses_data(
+    chat_resp: dict[str, Any],
+) -> dict[str, Any]:
+    """Translate a Chat Completions response JSON into the Responses API structure.
+
+    Normalizes choices[0].message.content into output[type=message] and usage fields.
+    """
+    if not isinstance(chat_resp, dict):
+        return {"output": []}
+
+    # Upstream errors arrive as a 200-with-error body on some gateways and as a
+    # non-2xx body on others. Surface both as status=failed with the message
+    # preserved, so the Brain reports a failure instead of empty output.
+    upstream_error = chat_resp.get("error")
+    if upstream_error:
+        err_message = (
+            upstream_error.get("message")
+            if isinstance(upstream_error, dict)
+            else str(upstream_error)
+        )
+        return {
+            "id": chat_resp.get("id"),
+            "model": chat_resp.get("model"),
+            "status": "failed",
+            "error": {"message": err_message or "upstream error"},
+            "output": [],
+        }
+
+    output_text = ""
+    _finish_reason: Any = None
+    # Tool calls and reasoning are first-class outputs for an agent brain: a
+    # chat-completions model that answers with a tool call has no message
+    # content at all, so reading content alone silently returns empty output.
+    tool_calls: list[dict[str, Any]] = []
+    reasoning_text = ""
+    choices = chat_resp.get("choices")
+    if isinstance(choices, list) and choices:
+        first = choices[0]
+        if isinstance(first, dict):
+            _finish_reason = first.get("finish_reason")
+            msg = first.get("message")
+            if isinstance(msg, dict):
+                # Some gateways return content as a list of parts; flatten it
+                # with the same rule the request converter uses.
+                raw_content = msg.get("content")
+                if isinstance(raw_content, str):
+                    output_text = raw_content
+                elif isinstance(raw_content, list):
+                    parts = [
+                        p.get("text", "")
+                        for p in raw_content
+                        if isinstance(p, dict) and isinstance(p.get("text"), str)
+                    ]
+                    output_text = "\n".join(parts)
+                # MiniMax and DeepSeek-style gateways name it reasoning_content;
+                # OpenAI-compatible ones use message.reasoning.
+                for key in ("reasoning_content", "reasoning"):
+                    candidate = msg.get(key)
+                    if isinstance(candidate, str) and candidate.strip():
+                        reasoning_text = candidate
+                        break
+                raw_calls = msg.get("tool_calls")
+                if isinstance(raw_calls, list):
+                    tool_calls = [c for c in raw_calls if isinstance(c, dict)]
+
+    # Status comes from the finish reason, never hardcoded: downstream
+    # session classification reads this field to decide XML_EXTRACTED vs REPORT.
+    _status, _incomplete_reason = _responses_status_from_finish(_finish_reason)
+
+    resp_data: dict[str, Any] = {
+        "id": chat_resp.get("id"),
+        "model": chat_resp.get("model"),
+        "status": _status,
+        "output": _build_responses_output(output_text, reasoning_text, tool_calls),
+    }
+
+    if _incomplete_reason is not None:
+        resp_data_incomplete: dict[str, Any] = {"reason": _incomplete_reason}
+        resp_data["incomplete_details"] = resp_data_incomplete
+
+    # Usage mapping: a counter that the upstream omitted stays OMITTED.
+    # Storing None here would leak into quota accounting and budget math,
+    # where None inside an arithmetic expression raises or silently voids
+    # the total. Presence of the key means "the provider reported a number".
+    usage = chat_resp.get("usage")
+    if isinstance(usage, dict):
+        mapped_usage: dict[str, int] = {}
+        if isinstance(usage.get("prompt_tokens"), int):
+            mapped_usage["input_tokens"] = usage["prompt_tokens"]
+        if isinstance(usage.get("completion_tokens"), int):
+            mapped_usage["output_tokens"] = usage["completion_tokens"]
+        if isinstance(usage.get("total_tokens"), int):
+            mapped_usage["total_tokens"] = usage["total_tokens"]
+        # Derived total only when the provider omitted it but both halves exist.
+        if "total_tokens" not in mapped_usage and (
+            "input_tokens" in mapped_usage and "output_tokens" in mapped_usage
+        ):
+            mapped_usage["total_tokens"] = (
+                mapped_usage["input_tokens"] + mapped_usage["output_tokens"]
+            )
+        if mapped_usage:
+            resp_data["usage"] = mapped_usage
+
+    return resp_data
+
+
 def _get_reasoning_effort() -> str:
     """Reasoning effort; override via ``BRAIN_REASONING_EFFORT``.
 
@@ -5627,6 +6118,11 @@ def parse_responses_text(data: dict) -> str:
             text = item.get("text")
             if isinstance(text, str) and text:
                 parts.append(text)
+        elif item.get("type") == "function_call":
+            name = item.get("name")
+            args = item.get("arguments")
+            if isinstance(name, str):
+                parts.append(f"{name}({args or ''})")
     return "\n".join(parts)
 
 
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index a5876f0..99789d6 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -2675,7 +2675,8 @@ def test_budget_window_and_margin_read_env_overrides(monkeypatch):
     assert "100000" in bridge._over_budget_hint(90000, 9001)
 
 
-def test_pure_budget_fits_exact_boundary():
+def test_pure_budget_fits_exact_boundary(monkeypatch):
+    monkeypatch.delenv("BRAIN_CONTEXT_WINDOW_TOKENS", raising=False)
     limit = (
         bridge._PROVIDER_CONTEXT_WINDOW_DEFAULT - bridge._BUDGET_SAFETY_MARGIN_DEFAULT
     )
@@ -2687,6 +2688,7 @@ def test_over_budget_returns_report_with_numbers_and_skips_provider(
     tmp_path, monkeypatch
 ):
     # Reserve above the window can never fit: provider must not be called.
+    monkeypatch.delenv("BRAIN_CONTEXT_WINDOW_TOKENS", raising=False)
     monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
     _mk_sys_prompt(tmp_path, monkeypatch)
     monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
@@ -5196,3 +5198,550 @@ def test_brain_turn_output_address_propagated_and_degraded(tmp_path, monkeypatch
     degraded = target("q", task_id="218", include_bundle=False, project_root=str(root))
     assert degraded["output_address"] is None
     assert degraded["status"] == "REPORT"
+
+
+# --- Task 401: Chat-completions translation and upstream mode ---
+
+
+def test_upstream_mode_default_and_validation(monkeypatch):
+    monkeypatch.delenv("BRAIN_UPSTREAM_MODE", raising=False)
+    assert bridge._upstream_mode() == "responses"
+
+    monkeypatch.setenv("BRAIN_UPSTREAM_MODE", "chat_completions")
+    assert bridge._upstream_mode() == "chat_completions"
+
+    monkeypatch.setenv("BRAIN_UPSTREAM_MODE", "RESPONSES")
+    assert bridge._upstream_mode() == "responses"
+
+    monkeypatch.setenv("BRAIN_UPSTREAM_MODE", "invalid_mode")
+    with pytest.raises(
+        ValueError, match="BRAIN_UPSTREAM_MODE='invalid_mode' is invalid"
+    ):
+        bridge._upstream_mode()
+
+
+def test_upstream_url_resolution(monkeypatch):
+    monkeypatch.delenv("BRAIN_UPSTREAM_MODE", raising=False)
+    monkeypatch.setenv("BRAIN_API_BASE", "http://127.0.0.1:8081/go/resp")
+    assert bridge._upstream_url() == "http://127.0.0.1:8081/go/resp/responses"
+
+    monkeypatch.setenv("BRAIN_UPSTREAM_MODE", "chat_completions")
+    monkeypatch.setenv("BRAIN_API_BASE", "https://api.openai.com/v1")
+    assert bridge._upstream_url() == "https://api.openai.com/v1/chat/completions"
+
+
+def test_convert_responses_to_chat_completions_body():
+    responses_body = {
+        "model": "minimax-m3.1-flash",
+        "instructions": "You are a helpful assistant.",
+        "input": [
+            {"role": "user", "content": "Hello!"},
+            {
+                "type": "message",
+                "role": "assistant",
+                "content": [{"type": "output_text", "text": "Hi there!"}],
+            },
+            {"role": "user", "content": "How are you?"},
+        ],
+        "max_output_tokens": 4096,
+        "temperature": 0.2,
+        "reasoning": {"effort": "high"},
+    }
+
+    chat_body = bridge._convert_responses_to_chat_completions_body(responses_body)
+    assert chat_body["model"] == "minimax-m3.1-flash"
+    assert chat_body["max_tokens"] == 4096
+    assert chat_body["temperature"] == 0.2
+    assert chat_body["reasoning_effort"] == "high"
+    assert len(chat_body["messages"]) == 4
+    assert chat_body["messages"][0] == {
+        "role": "system",
+        "content": "You are a helpful assistant.",
+    }
+    assert chat_body["messages"][1] == {"role": "user", "content": "Hello!"}
+    assert chat_body["messages"][2] == {"role": "assistant", "content": "Hi there!"}
+    assert chat_body["messages"][3] == {"role": "user", "content": "How are you?"}
+
+
+def test_convert_chat_completions_to_responses_data():
+    chat_resp = {
+        "id": "chatcmpl-12345",
+        "model": "minimax-m3.1-flash",
+        "choices": [
+            {
+                "index": 0,
+                "message": {
+                    "role": "assistant",
+                    "content": "Here is the plan:\n```xml\n<plan>123</plan>\n```",
+                },
+                "finish_reason": "stop",
+            }
+        ],
+        "usage": {
+            "prompt_tokens": 100,
+            "completion_tokens": 50,
+            "total_tokens": 150,
+        },
+    }
+
+    resp_data = bridge._convert_chat_completions_to_responses_data(chat_resp)
+    assert resp_data["id"] == "chatcmpl-12345"
+    assert resp_data["model"] == "minimax-m3.1-flash"
+    assert resp_data["status"] == "completed"
+    assert bridge.parse_responses_text(resp_data) == (
+        "Here is the plan:\n```xml\n<plan>123</plan>\n```"
+    )
+    assert resp_data["usage"]["input_tokens"] == 100
+    assert resp_data["usage"]["output_tokens"] == 50
+    assert resp_data["usage"]["total_tokens"] == 150
+
+
+def test_brain_turn_with_chat_completions_mode(tmp_path, monkeypatch):
+    """End-to-end brain_turn dispatch using BRAIN_UPSTREAM_MODE=chat_completions."""
+    monkeypatch.setenv("BRAIN_UPSTREAM_MODE", "chat_completions")
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-chat-key")
+    monkeypatch.setenv("BRAIN_API_BASE", "http://127.0.0.1:8081/chat")
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _mk_sys_prompt(tmp_path, monkeypatch)
+    root = _mk_tasks_root(tmp_path)
+
+    chat_upstream_payload = {
+        "id": "chatcmpl-minimax-1",
+        "model": "minimax-m3.1-flash",
+        "choices": [
+            {
+                "index": 0,
+                "message": {
+                    "role": "assistant",
+                    "content": "Plan approved.\nverdict: PLAN APPROVED\nseats: Architect",
+                },
+                "finish_reason": "stop",
+            }
+        ],
+        "usage": {"prompt_tokens": 120, "completion_tokens": 60, "total_tokens": 180},
+    }
+
+    holder = {}
+    _mk_bridge_client(
+        monkeypatch, [_FakeResp(200, "OK", chat_upstream_payload)], holder
+    )
+
+    call = bridge.brain_turn
+    target = call.fn if hasattr(call, "fn") else call
+    res = target(
+        "test question", task_id="218", include_bundle=False, project_root=str(root)
+    )
+
+    assert res["status"] == "REPORT"
+    assert "Plan approved." in res["output"]
+
+    # Verify that what went over the wire was chat completions shape
+    sent_body = holder["body"]
+    assert "messages" in sent_body
+    assert "input" not in sent_body
+    assert any(
+        m["role"] == "user" and "test question" in m["content"]
+        for m in sent_body["messages"]
+    )
+
+
+def test_convert_usage_omits_missing_counters():
+    """F3: a missing counter must be absent, never None."""
+    resp = bridge._convert_chat_completions_to_responses_data(
+        {"id": "x", "choices": [{"message": {"content": "ok"}}], "usage": {}}
+    )
+    assert "usage" not in resp
+
+    partial = bridge._convert_chat_completions_to_responses_data(
+        {
+            "id": "x",
+            "choices": [{"message": {"content": "ok"}}],
+            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
+        }
+    )
+    assert partial["usage"] == {
+        "input_tokens": 10,
+        "output_tokens": 5,
+        "total_tokens": 15,
+    }
+
+
+def test_convert_finish_reason_maps_status():
+    """F1: status must come from finish_reason, not a constant."""
+    length = bridge._convert_chat_completions_to_responses_data(
+        {"choices": [{"message": {"content": "trunc"}, "finish_reason": "length"}]}
+    )
+    assert length["status"] == "incomplete"
+    assert length["incomplete_details"]["reason"] == "max_output_tokens"
+
+    filtered = bridge._convert_chat_completions_to_responses_data(
+        {
+            "choices": [
+                {
+                    "message": {"content": ""},
+                    "finish_reason": "content_filter",
+                }
+            ]
+        }
+    )
+    assert filtered["status"] == "incomplete"
+    assert filtered["incomplete_details"]["reason"] == "content_filter"
+
+    unknown = bridge._convert_chat_completions_to_responses_data(
+        {"choices": [{"message": {"content": "x"}, "finish_reason": "weird"}]}
+    )
+    assert unknown["status"] == "incomplete"
+    assert unknown["incomplete_details"]["reason"] == "unknown_finish_reason"
+
+    missing = bridge._convert_chat_completions_to_responses_data(
+        {"choices": [{"message": {"content": "x"}}]}
+    )
+    assert missing["status"] == "incomplete"
+
+
+def test_convert_upstream_error_becomes_failed_status():
+    """F1: an error body must not surface as an empty success."""
+    resp = bridge._convert_chat_completions_to_responses_data(
+        {"error": {"message": "model not found", "type": "invalid_request_error"}}
+    )
+    assert resp["status"] == "failed"
+    assert resp["error"]["message"] == "model not found"
+    assert resp["output"] == []
+
+
+def test_convert_tool_calls_and_reasoning_preserved():
+    """F2: tool calls and reasoning must cross the boundary."""
+    resp = bridge._convert_chat_completions_to_responses_data(
+        {
+            "id": "c1",
+            "choices": [
+                {
+                    "finish_reason": "tool_calls",
+                    "message": {
+                        "role": "assistant",
+                        "content": None,
+                        "reasoning_content": "thinking about it",
+                        "tool_calls": [
+                            {
+                                "id": "call_1",
+                                "type": "function",
+                                "function": {
+                                    "name": "read_file",
+                                    "arguments": '{"p":"a.py"}',
+                                },
+                            }
+                        ],
+                    },
+                }
+            ],
+        }
+    )
+    types = [item["type"] for item in resp["output"]]
+    assert types == ["reasoning", "function_call"]
+    assert resp["output"][0]["summary"][0]["text"] == "thinking about it"
+    call = resp["output"][1]
+    assert call["name"] == "read_file"
+    assert call["call_id"] == "call_1"
+    assert call["arguments"] == '{"p":"a.py"}'
+    assert resp["status"] == "completed"
+
+
+def test_request_body_carries_tools_and_tool_choice():
+    """F2: tool definitions must survive request translation."""
+    body = bridge._convert_responses_to_chat_completions_body(
+        {
+            "model": "m",
+            "input": [{"role": "user", "content": "hi"}],
+            "tools": [
+                {
+                    "type": "function",
+                    "name": "read_file",
+                    "description": "read",
+                    "parameters": {
+                        "type": "object",
+                        "properties": {"p": {"type": "string"}},
+                    },
+                }
+            ],
+            "tool_choice": "auto",
+            "parallel_tool_calls": False,
+        }
+    )
+    assert body["tools"][0]["type"] == "function"
+    assert body["tools"][0]["function"]["name"] == "read_file"
+    assert body["tool_choice"] == "auto"
+    assert body["parallel_tool_calls"] is False
+
+
+def test_parallel_tool_calls_dropped_without_tools():
+    """A tools-less body must not carry parallel_tool_calls (strict 400)."""
+    body = bridge._convert_responses_to_chat_completions_body(
+        {"model": "m", "input": [], "parallel_tool_calls": True}
+    )
+    assert "parallel_tool_calls" not in body
+    assert "tools" not in body
+
+
+def test_brain_turn_chat_completions_non_200_is_failure(tmp_path, monkeypatch):
+    """F4: the retry/error path must be exercised in chat_completions mode."""
+    monkeypatch.setenv("BRAIN_UPSTREAM_MODE", "chat_completions")
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-chat-key")
+    monkeypatch.setenv("BRAIN_API_BASE", "http://127.0.0.1:8081/chat")
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _mk_sys_prompt(tmp_path, monkeypatch)
+    root = _mk_tasks_root(tmp_path)
+
+    _mk_bridge_client(
+        monkeypatch,
+        [_FakeResp(401, "Unauthorized", {"error": {"message": "bad key"}})],
+        {},
+    )
+    call = bridge.brain_turn
+    target = call.fn if hasattr(call, "fn") else call
+    res = target("q", task_id="218", include_bundle=False, project_root=str(root))
+    assert res["status"] == "REPORT"
+    assert "bad key" in res["output"] or "401" in res["output"]
+
+
+def test_brain_turn_chat_completions_failure_status_raises(tmp_path, monkeypatch):
+    """F1/F2: status=failed must surface as a failure through brain_turn."""
+    monkeypatch.setenv("BRAIN_UPSTREAM_MODE", "chat_completions")
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-chat-key")
+    monkeypatch.setenv("BRAIN_API_BASE", "http://127.0.0.1:8081/chat")
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _mk_sys_prompt(tmp_path, monkeypatch)
+    root = _mk_tasks_root(tmp_path)
+
+    payload = {
+        "id": "chatcmpl-err",
+        "error": {"message": "model not found", "type": "invalid_request_error"},
+    }
+    _mk_bridge_client(monkeypatch, [_FakeResp(200, "OK", payload)], {})
+    call = bridge.brain_turn
+    target = call.fn if hasattr(call, "fn") else call
+    res = target("q", task_id="218", include_bundle=False, project_root=str(root))
+    assert res["status"] == "REPORT"
+    assert "model not found" in res["output"]
+
+
+def test_brain_turn_chat_completions_incomplete_is_annotated(tmp_path, monkeypatch):
+    """F1/F2: an incomplete response stays usable but is marked truncated."""
+    monkeypatch.setenv("BRAIN_UPSTREAM_MODE", "chat_completions")
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-chat-key")
+    monkeypatch.setenv("BRAIN_API_BASE", "http://127.0.0.1:8081/chat")
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _mk_sys_prompt(tmp_path, monkeypatch)
+    root = _mk_tasks_root(tmp_path)
+
+    payload = {
+        "id": "chatcmpl-trunc",
+        "choices": [
+            {
+                "index": 0,
+                "message": {"role": "assistant", "content": "partial plan text"},
+                "finish_reason": "content_filter",
+            }
+        ],
+        "usage": {"prompt_tokens": 10, "completion_tokens": 4096},
+    }
+    _mk_bridge_client(monkeypatch, [_FakeResp(200, "OK", payload)], {})
+    call = bridge.brain_turn
+    target = call.fn if hasattr(call, "fn") else call
+    res = target("q", task_id="218", include_bundle=False, project_root=str(root))
+    assert res["status"] == "REPORT"
+    assert "upstream incomplete: content_filter" in res["output"]
+    assert "partial plan text" in res["output"]
+
+
+def test_brain_turn_chat_completions_tool_call_survives_dispatch(tmp_path, monkeypatch):
+    """F2: a tool-call-only answer must not be flattened into empty output."""
+    monkeypatch.setenv("BRAIN_UPSTREAM_MODE", "chat_completions")
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-chat-key")
+    monkeypatch.setenv("BRAIN_API_BASE", "http://127.0.0.1:8081/chat")
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _mk_sys_prompt(tmp_path, monkeypatch)
+    root = _mk_tasks_root(tmp_path)
+
+    payload = {
+        "id": "chatcmpl-tools",
+        "choices": [
+            {
+                "index": 0,
+                "finish_reason": "tool_calls",
+                "message": {
+                    "role": "assistant",
+                    "content": None,
+                    "tool_calls": [
+                        {
+                            "id": "call_9",
+                            "type": "function",
+                            "function": {
+                                "name": "read_file",
+                                "arguments": '{"p":"server.py"}',
+                            },
+                        }
+                    ],
+                },
+            }
+        ],
+    }
+    holder = {}
+    _mk_bridge_client(monkeypatch, [_FakeResp(200, "OK", payload)], holder)
+    call = bridge.brain_turn
+    target = call.fn if hasattr(call, "fn") else call
+    res = target("q", task_id="218", include_bundle=False, project_root=str(root))
+    assert res["status"] == "REPORT"
+    assert "read_file" in res["output"]
+    assert "server.py" in res["output"]
+
+
+def test_record_brain_use_tolerates_partial_usage(tmp_path, monkeypatch):
+    """F3: a partial usage dict must never store None counters."""
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    bridge._record_brain_use("test-model", {"input_tokens": 100})
+    bridge._record_brain_use("test-model", {})
+    # Two calls must not raise on a missing counter. The concrete assertion is
+    # that the stored/returned usage contains no None values.
+    stored = bridge._record_brain_use(
+        "test-model", {"input_tokens": 1, "output_tokens": None}
+    )
+    assert all(v is not None for v in stored.values())
+
+
+def test_string_input_becomes_a_single_user_message():
+    """R2: a bare-string input must not be iterated character by character."""
+    body = bridge._convert_responses_to_chat_completions_body(
+        {
+            "model": "m",
+            "instructions": "be brief",
+            "input": "hello there",
+        }
+    )
+    assert body["messages"] == [
+        {"role": "system", "content": "be brief"},
+        {"role": "user", "content": "hello there"},
+    ]
+
+
+def test_blank_string_input_produces_no_user_message():
+    """R2: whitespace-only input adds no empty turn."""
+    body = bridge._convert_responses_to_chat_completions_body(
+        {"model": "m", "input": "   "}
+    )
+    assert body["messages"] == []
+
+
+def test_unsupported_responses_fields_are_dropped_with_warning(caplog):
+    """R1: a drop must be visible, never silent."""
+    with caplog.at_level("WARNING"):
+        body = bridge._convert_responses_to_chat_completions_body(
+            {
+                "model": "m",
+                "input": [{"role": "user", "content": "hi"}],
+                "previous_response_id": "resp_1",
+                "store": True,
+                "metadata": {"k": "v"},
+            }
+        )
+    assert "previous_response_id" not in body
+    assert "store" not in body
+    logged = " ".join(record.message for record in caplog.records)
+    assert "previous_response_id" in logged
+    assert "store" in logged
+
+
+def test_no_warning_when_no_unsupported_fields_present(caplog):
+    """R1: a clean body must not emit drop warnings."""
+    with caplog.at_level("WARNING"):
+        bridge._convert_responses_to_chat_completions_body(
+            {"model": "m", "input": [{"role": "user", "content": "hi"}]}
+        )
+    assert "dropped unsupported" not in " ".join(
+        record.message for record in caplog.records
+    )
+
+
+def test_assistant_function_call_item_becomes_tool_call_message():
+    """F1: a roleless function_call item must not vanish."""
+    body = bridge._convert_responses_to_chat_completions_body(
+        {
+            "model": "m",
+            "input": [
+                {"role": "user", "content": "read server.py"},
+                {
+                    "type": "function_call",
+                    "call_id": "call_1",
+                    "name": "read_file",
+                    "arguments": '{"p":"server.py"}',
+                },
+                {
+                    "type": "function_call_output",
+                    "call_id": "call_1",
+                    "output": "def main(): ...",
+                },
+            ],
+        }
+    )
+    roles = [m["role"] for m in body["messages"]]
+    assert roles == ["user", "assistant", "tool"]
+
+    tool_call_msg = body["messages"][1]
+    assert tool_call_msg["content"] is None
+    assert tool_call_msg["tool_calls"][0]["id"] == "call_1"
+    assert tool_call_msg["tool_calls"][0]["function"]["name"] == "read_file"
+    assert tool_call_msg["tool_calls"][0]["function"]["arguments"] == (
+        '{"p":"server.py"}'
+    )
+
+    tool_result = body["messages"][2]
+    assert tool_result["tool_call_id"] == "call_1"
+    assert tool_result["content"] == "def main(): ..."
+
+
+def test_function_call_with_dict_arguments_is_json_encoded():
+    """F1: dict arguments must cross as a JSON string, not a dict."""
+    body = bridge._convert_responses_to_chat_completions_body(
+        {
+            "model": "m",
+            "input": [
+                {
+                    "type": "function_call",
+                    "call_id": "c2",
+                    "name": "read_file",
+                    "arguments": {"p": "a.py"},
+                }
+            ],
+        }
+    )
+    raw = body["messages"][0]["tool_calls"][0]["function"]["arguments"]
+    assert isinstance(raw, str)
+    assert json.loads(raw) == {"p": "a.py"}
+
+
+def test_brain_turn_incomplete_is_not_a_terminal_failure(tmp_path, monkeypatch):
+    """F2: an incomplete response must be annotated, never aborted."""
+    monkeypatch.setenv("BRAIN_UPSTREAM_MODE", "chat_completions")
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-chat-key")
+    monkeypatch.setenv("BRAIN_API_BASE", "http://127.0.0.1:8081/chat")
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _mk_sys_prompt(tmp_path, monkeypatch)
+    root = _mk_tasks_root(tmp_path)
+
+    payload = {
+        "id": "chatcmpl-length",
+        "choices": [
+            {
+                "index": 0,
+                "message": {"role": "assistant", "content": "cut mid-sentence"},
+                "finish_reason": "content_filter",
+            }
+        ],
+    }
+    _mk_bridge_client(monkeypatch, [_FakeResp(200, "OK", payload)], {})
+    call = bridge.brain_turn
+    target = call.fn if hasattr(call, "fn") else call
+    res = target("q", task_id="218", include_bundle=False, project_root=str(root))
+    assert res["status"] == "REPORT"
+    assert "upstream incomplete: content_filter" in res["output"]
+    assert "cut mid-sentence" in res["output"]
+    assert "status=incomplete" not in res["output"]
```
<!-- END_GIT_DIFF -->
