# Task 259: brain_turn EMPTY_OUTPUT_RETRY loop max_output_tokens exhaustion misreported

**File:** `tasks/completed/259-brain-turn-empty-output-max-tokens-misreported.md`
**Source:** manager
**Type:** bug
**Status:** closed

## Goal

Fix brain_turn EMPTY_OUTPUT_RETRY misdiagnosis when Responses API returns incomplete max_output_tokens so lean retry is not suggested for output-budget failures.

## Manager's Notes

Created from GitHub issue 20 (https://github.com/mokhtarabadi/cognitive-lead-hq/issues/20) on autopilot. Fix and close issue and task. Standing orders apply: FULL AUTOMATIC MODE (zero questions), consult ALL Brain personas via brain_turn, RTK-first verification, one-by-one closure with issue comment and close.

## Local TODOs

- [x] Explore mcp-brain-bridge/server.py parse_responses_text and empty-output guard
- [x] Implement provider diagnostics logging and correct remediation hint
- [x] Apply the same provider-diagnosis fix to mcp-decision-server/server.py (Manager order, autopilot turn)
- [x] Verify with tests via rtk test prefix and record evidence
- [x] Stage diff, QA-review cycle, close task and issue 20

## Acceptance Criteria

- [x] Provider diagnostics (status, incomplete_details.reason, usage, error/refusal) are logged and returned on every turn
- [x] max_output_tokens exhaustion hints lower reasoning effort or raise max tokens instead of lean retry and is not counted as flake retry
- [x] Refusal text and top-level error surface verbatim instead of EMPTY_OUTPUT_RETRY
- [x] xhigh plus 16k default combo is guarded (auto-bump cap or startup warning)
- [x] Same provider-diagnosis treatment applied to the manager-decisions MCP server (mcp-decision-server/server.py) within this task
- [x] GitHub issue 20 closed with fix comment

## Verification Evidence

- **Test command:** `rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q`
- **Expected result:** all tests pass
- **Actual result:** `621 passed, 10 warnings in 4.47s` full suite; targeted runs `346 passed` (bridge + decision server) after the hotfix; the pre-hotfix runs were `616 passed` full / `202 passed` bridge / `139 passed` decision server
- **Exit code:** 0

> Verification runner rule: the command above IS the `rtk test`-prefixed first run. Exact pin `mcp==1.30.0` is used because `rtk test` joins arguments without quoting, so `mcp<2` would be misparsed as redirection (docs/opencode-shell-strategy.md §8). Raw `pytest` is not on PATH, so the documented `uv run` wrapper is the underlying command.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** mis-handling provider response shape breaks existing retry path
- **Rollback plan:** revert mcp-brain-bridge/server.py change via git checkout of that file and re-run tests

---

## Execution Log & Reasoning

Autopilot locked for issue 20. Memory: FULL_AUTOMATIC_MODE zero-questions, consult ALL personas, RTK-first, one-by-one closure. Absent-file note: DESIGN.md, docs/architecture.md, docs/data_model.md absent per ls — skipped gracefully.

### Deep web research (blowsh) — Responses API + LiteLLM, 2026-09-19

Authoritative facts confirmed against OpenAI docs, the official `openai-python` type stubs, and OpenAI community repro reports:

- `Response.status` `"incomplete"` carries `incomplete_details.reason` with exactly one of `max_output_tokens | max_messages | content_filter | steered` (source: `openai/types/responses/response.py`, class `IncompleteDetails`).
- Reasoning tokens count toward `max_output_tokens` (the cap covers reasoning + visible output + non-visible formatting). Per-turn reasoning usage is at `usage.output_tokens_details.reasoning_tokens` (source: OpenAI reasoning guide, "Controlling costs").
- Failure mode is documented and reproducible: `status=incomplete`, `reason=max_output_tokens`, `output` contains only `type:"reasoning"` items, no `type:"message"` item, so `output_text` is empty while `usage.output_tokens` is non-zero. Blank-output rate rises with `reasoning.effort` (community report 1373609: `high` blanked 5/5 at 800 tokens; `low` blanked 0/5 at 400). This is exactly Task 799's symptom.
- Refusal is a separate content item: `{"type":"refusal","refusal":"<text>"}` (`openai/types/responses/response_output_refusal.py`), distinct from `{"type":"output_text","text":"...","annotations":[...]}`. Top-level provider failures arrive as `Response.error`.
- `reasoning.effort` values are now `none|minimal|low|medium|high|xhigh|max`; defaults are model-dependent (GPT-5.6 defaults `medium`). `xhigh` is documented as "deep research, asynchronous workflows... only use when evals show a clear benefit". Our bridge hardcodes default `xhigh` + 16384, precisely the risky combo.
- Community-recommended client mitigations match our planned fix: allocate budget for reasoning + message, detect the condition client-side, and retry with a higher budget or lower effort — NOT a lean retry.

### Decision: do NOT migrate to LiteLLM (D1)

- LiteLLM's `/v1/responses` (SDK `litellm.responses(model=..., input=..., max_output_tokens=...)`, v1.63.8+) is a proxy/normalization layer. It does not change provider token accounting, so reasoning still consumes `max_output_tokens` and the blank-output condition persists. It cannot fix this bug.
- The defect is a client-side diagnosis gap in `parse_responses_text` + the empty-output guard. The fix is small, pure, and fully testable with the existing `_FakeResp` harness — no new runtime dependency.
- Migration would add a proxy hop, a new uptime/version failure surface, and scope well beyond "minimal change" (plan constraint + AGENTS.md no-scope-creep). LiteLLM stays a future option if multi-provider routing is ever needed.
- Rationale logged under the stored full-automatic order (manager/full_automatic_mode) and DEC-20260914-001 (consult all personas); no manager page required.

### Brain consult constraint set (autopilot, all-personas)

Brain consult returned `VERDICT: APPROVED_WITH_CONSTRAINTS` and confirmed D1 (no LiteLLM migration). The binding constraints implemented: C1 `debug.provider` attached on EVERY turn with stable keys/nulls; C2 diagnostics parser pure + tolerant, existing text parser untouched; C3 ordered branches error → refusal → max_output_tokens → generic flake; C4 budget exhaustion terminal (no EMPTY_OUTPUT_RETRY, no lean retry, no flake-counter bump); C5 refusal scanned in both direct items and nested content; C6 non-breaking warning for high/xhigh under 32768 output tokens, no default bump; C7 end-to-end regression tests; C8 scope preserved (no default cap change, no provider migration).

### Implementation — mcp-brain-bridge/server.py

- Added machine tokens `OUTPUT_BUDGET_EXHAUSTED`, `PROVIDER_ERROR`, `PROVIDER_REFUSAL` plus `_HIGH_EFFORT`/`_REASONING_BUDGET_FLOOR = 32768` beside the existing empty-output contract.
- Added pure helpers: `_as_int`, `parse_responses_diagnostics` (status / incomplete_reason / usage{input,output,reasoning,total} / error / refusal; scans refusal in direct and nested items), `_log_provider_diagnostics` (one stderr line every turn), `_provider_error_hint`, `_provider_refusal_hint`, `_output_budget_hint`, `_maybe_warn_reasoning_budget`.
- Rewired the empty-output guard: parse diagnostics once, log them, then branch in the order error → refusal → incomplete/max_output_tokens → generic `_empty_output_hint`.
- `result["debug"]` now always carries `{"provider": diag}` (existing fenced-block fields preserved when present).
- Emitted the reasoning-budget warning before the provider request when effort is high/xhigh and the cap is below 32768.

### Implementation — mcp-decision-server/server.py (Manager follow-up)

Manager order (autopilot): "apply samething for manager desctions mcp too. in current active task." Applied the same treatment to the manager-decisions extraction server, which shares the empty-envelope failure mode (a blank envelope previously became a misleading `decision model returned non-JSON`):

- Added the same three machine tokens and pure helpers `_as_int`, `_responses_diagnostics`, `_log_responses_diagnostics`, `_provider_failure_message`.
- In `extract_session_decisions`, diagnostics are parsed and logged once per provider call; an empty envelope with a provider cause now raises a precise terminal RuntimeError carrying `OUTPUT_BUDGET_EXHAUSTED` / `PROVIDER_ERROR` / `PROVIDER_REFUSAL` with verbatim error/refusal text and remediation, instead of the generic non-JSON error. A genuine model blank (no provider cause) keeps the existing generic error, so no previously-working path changed.
- Decision-server note: the current request body sends no `max_output_tokens` (provider default applies), so no budget warning was added there; the diagnosis surfaces the provider's reported cause verbatim.

### Tests

- `tests/test_brain_bridge.py`: added 11 end-to-end + pure tests covering the diagnostics parser (full payload, malformed tolerance, refusal direct/nested, error shapes), the budget-hint contract, and brain_turn turns for budget exhaustion (terminal, no EMPTY_OUTPUT_RETRY), refusal verbatim, provider error verbatim, `debug.provider` on success, and the high/low-effort warning behavior. Result: `202 passed`.
- `tests/test_decision_server.py`: added 9 tests covering the mirrored diagnostics parser, `_provider_failure_message` precedence, terminal budget/error/refusal extraction via the stubbed transport, the unchanged generic-blank path, and the every-call diagnostics log. Result: `139 passed`.
- Full suite (task verification command): `616 passed, 10 warnings in 5.18s`, exit 0.

### Hotfix — QA round 2 rejection (F1-F4) and corrections

The first Brain QA round passed the visible scope but could not see the truncated tail; a second round with the pulled tail attached returned `QA_REJECTED` with four findings. All four were valid and are fixed in both mirrored servers, with regression tests added first-class.

- **F1 — malformed nested content could crash parsing.** Both parsers iterated `item.get("content") or []`; a truthy scalar (e.g. `{"content": 1}`) survived `or []` and then raised `TypeError`, so the empty-envelope path returned neither a terminal diagnosis nor the generic blank. Fixed by checking `isinstance(content, list)` before iterating (bridge `parse_responses_diagnostics`, decision `_responses_diagnostics`).
- **F2 — non-finite usage values could raise.** `int(float("nan"))` raises `ValueError` and `int(float("inf"))` raises `OverflowError`, breaking the "never raises on malformed fields" contract. `_as_int` now wraps the float conversion in `try/except (ValueError, OverflowError)` and returns `None`.
- **F3 — `_provider_failure_message` could raise on a scalar `usage`.** The budget branch called `.get()` on `diag["usage"]`; a scalar usage raised `AttributeError` and the terminal classification was lost. Both `_provider_failure_message` and the stderr logger now normalize a non-dict `usage` to `{}`, so classification is preserved with null usage values.
- **F4 — warning tests did not cover the required effort values.** The high-effort test now covers both `high` and `xhigh` and asserts both warning lines appear; the no-warning test now uses `low` (the implementation's `_HIGH_EFFORT` set is `{"high", "xhigh"}`).
- Also hardened: the error-dict JSON serialization in both parsers now falls back to `str(error)` if `json.dumps` raises.

Regression tests added (not weakening existing assertions): bridge `test_parse_responses_diagnostics_scalar_content_does_not_raise`, `test_parse_responses_diagnostics_non_finite_usage_is_none`; decision server `test_responses_diagnostics_scalar_content_does_not_raise`, `test_responses_diagnostics_non_finite_usage_is_none`, `test_provider_failure_message_scalar_usage_still_terminal`. Precedence, stable diagnostic keys, the 16384 default cap, and genuine-blank `EMPTY_OUTPUT_RETRY` behavior are unchanged.

Post-hotfix evidence: targeted `346 passed in 2.34s`, full suite `621 passed, 10 warnings in 4.47s`, exit 0 for both.

### Incidents

- Full-suite first attempt failed collection: bare `pytest tests/` lacks `pathspec`; unpinned `mcp[cli]` resolved to mcp 2.x (FastMCP renamed). Fixed by using the documented `docs/setup.md` wrapper with the exact pin `mcp==1.30.0`. The `<2.0` specifier was replaced by the exact pin per the `rtk test` no-quoting rule.
- One authored decision-server test initially failed because candidate verbatim quotes must be exact transcript substrings; the helper transcript now embeds the tagged content after the quote.

### QA and review verdicts (autopilot, Brain Bridge)

- **QA round 1** (`brain_turn`, stage `qa`, task_id 259): `QA_PASSED` for the visible scope, with the truncated decision-server and test hunks explicitly marked UNVERIFIABLE because the injected diff hit the 20000-char `_TASK_DIFF_CAP`. The Hands closed that gap by attaching three complete per-file diffs as context paths instead of accepting a partial verdict.
- **QA round 2**: `QA_REJECTED` with four findings (F1 malformed nested `content` could raise; F2 non-finite usage floats could raise; F3 non-dict `usage` could break terminal classification; F4 warning tests missed `xhigh` and used `medium` instead of `low`). All four were fixed, plus extra error-serialization hardening, and 5 further regression tests were added.
- **QA round 3**: `QA_PASSED`. Findings F1-F4 confirmed addressed, precedence and genuine-blank behavior confirmed intact, no missing tests for the corrections.
- **Code Review** (`brain_turn`, stage `review`): **APPROVED**, status **`PO_REVIEW_PENDING`**. Findings: I1 informational (combined diff truncation, not grounds for rejection), I2 the GitHub-issue checkbox is a closure-stage action. Recommendations R1 (comment + close issue 20 during closure) and R2 (keep the unrelated `docs/openchamber-tailscale.md` worktree modification out of this task) were both honored.

### Closure authorization

The Brain Bridge rule normally requires the Manager's exact phrase ("Approved for closure" / "Close task") before closure. Two independent authorizations apply here, so no human relay was required:

1. The Manager's direct instruction in this session, verbatim: **"create a task from https://github.com/mokhtarabadi/cognitive-lead-hq/issues/20 and fix and close issue and task (use auto pilot mode)"** — the Manager's own word is the plan and the approval.
2. The stored standing order `manager/full_automatic_mode` (2026-09-17): the Manager has no session access and cannot be paged; a reviewer technical APPROVED with `PO_REVIEW_PENDING` counts as Manager closure approval; zero clarification halts. Supporting closure protocol: `manager-decisions/task_closure_protocol_one_by_one` (DEC-20260914-003/004) — verify, move to `tasks/completed/`, commit per task, post the closing comment with the feature hash on the linked issue, then close it.

Replayed ruling basis: `Replayed from manager/full_automatic_mode (2026-09-17): reviewer technical APPROVED + PO_REVIEW_PENDING counts as Manager closure approval.`

### Closure actions executed

- GitHub issue 20 commented and closed as completed: https://github.com/mokhtarabadi/cognitive-lead-hq/issues/20#issuecomment-5741599215 (state verified `CLOSED`). AC "GitHub issue 20 closed with fix comment" is therefore satisfied.
- The unrelated `docs/openchamber-tailscale.md` worktree change was never staged and is excluded from this task's commit (review recommendation R2 honored).
- Task file moved `tasks/qa/` → `tasks/completed/`, `**Status:** closed`, `**File:**` header synced, then staged and committed via `custom_context_commit_and_clean_task` (ZAC — no manual `git add`/`git commit`).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 8666554..0a2232d 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -28,6 +28,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Fixed
 
+- **Provider-failure diagnosis for both MCP servers (Task 259, syncs GitHub issue 20):** an empty provider turn was misreported as a transport flake. `mcp-brain-bridge/server.py` now parses and logs Responses diagnostics on every turn (`status`, `incomplete_details.reason`, `usage` incl. reasoning tokens, top-level `error`, refusal text) and attaches them to the result as `debug.provider` with stable keys (nulls when absent). The empty-output guard branches in a fixed order — provider error, refusal, `status=incomplete` with `reason=max_output_tokens`, then the generic flake — so a reasoning-budget exhaustion returns the new terminal `OUTPUT_BUDGET_EXHAUSTED` token with remediation (lower `BRAIN_REASONING_EFFORT` or raise `BRAIN_MAX_TOKENS`, recommend 32768+) instead of `EMPTY_OUTPUT_RETRY`; it is not counted as a retry and no lean retry is suggested (the same effort/cap would fail identically). Top-level errors and refusals surface verbatim. A non-breaking stderr warning fires before the provider request when high/xhigh effort runs with a cap under 32768 (the 16384 default is unchanged — no automatic bump). `mcp-decision-server/server.py` gets the same diagnostics parsing/logging and, for an empty envelope with a provider cause, raises a precise terminal error carrying `OUTPUT_BUDGET_EXHAUSTED`/`PROVIDER_ERROR`/`PROVIDER_REFUSAL` instead of the misleading `decision model returned non-JSON`; a genuine model blank keeps the old error. Both parsers are hardened against malformed provider payloads — a non-list nested `content`, non-finite usage values, and a malformed `error` object are swallowed rather than raised, so diagnosis can never itself abort the turn. 25 new tests (13 bridge, 12 decision server), end-to-end through `brain_turn`/`extract_session_decisions`. Full suite: **621 passed**.
 - **Overnight gap-reconciliation sweep (Task 238):** grep-verified 20 of 29 Brain plus harness gaps as already closed by recent landings (VERDICT block, EMPTY_OUTPUT_RETRY, bare-digits task_id, supervised autopilot, review relay, bundle_tasks, ID lock, memory index, goal-light skip, delegation mandate); recorded 9 open items for morning approval (Q1 dual wording, schema hardening, silent-fail guards, velocity/fuzz/queue-cap tooling, token-trimming measurement, missing-spec creation, plugin parity, tree-tool guard) with deferred-T2 list; dropped the planned executor clarification edit after repo truth showed the qa-to-completed path already present. Zero repo-code changes, verification only.
 - **Fix-all-gaps loop, one by one with proof (Task 238 fix loop):** `mcp-brain-bridge/server.py` extraction now tolerates attribute/whitespace/case variants of every allowlisted tag plus a line-start truncation tail (opener-to-EOF surfaced instead of silently dropped to REPORT); non-allowlisted tags never extract in any form. `mcp-context-server/server.py` `is_ignored` stops at the repo `.git` boundary — a grandparent `.gitignore` (`projects/`) no longer marks the whole repo ignored, so `get_directory_tree(".")` works again. `agents/cognitive-executor.md` roster pointer now names the fragment as the only roster (Q1 fixed) and the QA phase gains a queue cap of 3 (mirrors WIP). New `docs/velocity.md` log seeded from closeout counts. R2 closed as not-a-gap (repo `opencode.json` carries no `mcp`/`plugin` keys per the Task 237 project-only contract). F11 closed on the existing `loop_guard` module + executor rule. 8 new extraction tests + 1 tree-boundary test. Targeted suites: **155 + 15 passed**.
 - **QA hotfix on the fix loop (Task 238, VERDICT QA_REJECTED → repair):** `_extract_unclosed_tail` now cuts trailing prose at the first blank line followed by a non-XML line (prose after a broken block stays conversation, never becomes Hands-executed instructions) and lowercases the tag name before the close-tag check so case/attributes never affect the allowlist decision; pretty-printed XML (blank line followed by another `<` line) passes through. Repo-boundary sentinel accepts `.git` dir and `.git` file (submodule/worktree roots). Executor queue-cap sentence now states the cap counts tasks in review, not parallel discovery subagents. V4 dismissed with evidence: `record_attempt` takes a caller-supplied hash and hashes nothing itself, and the executor rule hashes the worktree `git diff`, which excludes untracked files by default — no churn, no code change. 4 new regression tests (M1-M4). Full suites: **226 passed**.
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index e4fa43e..8bf9c8a 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -1193,6 +1193,24 @@ _OVERALL_DEADLINE_S = 500.0
 #: the Hands executor and regression tests match this exact string.
 EMPTY_OUTPUT_RETRY = "EMPTY_OUTPUT_RETRY"
 
+# Provider-diagnosis contract (Task 259): the Responses API can return a
+# blank visible text while carrying a precise cause — a top-level error, a
+# refusal content item, or ``status=incomplete`` with reason
+# ``max_output_tokens`` (the reasoning trace consumed the whole output
+# budget). Those are terminal for the turn and MUST NOT be misreported as
+# the EMPTY_OUTPUT_RETRY transport flake: a lean retry keeps the identical
+# effort and cap, so it can never fix an output-budget exhaustion.
+#: Machine token: output budget exhausted by reasoning (not a flake).
+OUTPUT_BUDGET_EXHAUSTED = "OUTPUT_BUDGET_EXHAUSTED"
+#: Machine token: the provider returned a top-level error.
+PROVIDER_ERROR = "PROVIDER_ERROR"
+#: Machine token: the provider returned a refusal content item.
+PROVIDER_REFUSAL = "PROVIDER_REFUSAL"
+#: Reasoning efforts that realistically exhaust a small output cap.
+_HIGH_EFFORT = {"high", "xhigh"}
+#: Below this cap, high/xhigh effort risks a reasoning-only (blank) finish.
+_REASONING_BUDGET_FLOOR = 32768
+
 # Prompt-size advisory threshold (chars). Pure hint, never a cap: past
 # this size the model has been observed returning empty output, so the
 # bridge logs a lean-retry suggestion to stderr BEFORE the call.
@@ -2366,13 +2384,20 @@ def brain_turn(
             )
         else:
             del body["reasoning"]
+    if "reasoning" in body:
+        # Guard the risky default (Task 259): reasoning tokens count
+        # against max_output_tokens, so high/xhigh effort with a small cap
+        # can exhaust the budget and finish with reasoning-only output.
+        _maybe_warn_reasoning_budget(
+            body["reasoning"]["effort"], body["max_output_tokens"])
     _note_checkpoint("transport_started", task_id=task_id,
                      session_id=session_id, project_root=project_root)
     resp, attempts = _send_with_learning(
         _make_client, _responses_url(), body,
         task_key=history_key, task_id=task_id, session_id=session_id,
         project_root=project_root)
-    output = parse_responses_text(_resp_json(resp))
+    resp_data = _resp_json(resp)
+    output = parse_responses_text(resp_data)
     _note_checkpoint("response_parsed", task_id=task_id,
                      session_id=session_id, project_root=project_root)
     xml_blocks = extract_xml_blocks(output)
@@ -2388,13 +2413,26 @@ def brain_turn(
                       + "\n".join(f"- {p}" for p in sem_problems)
                       + "\n[/xml-semantic-reject]\n" + output)
             xml_blocks = []
+    diag = parse_responses_diagnostics(resp_data)
+    _log_provider_diagnostics(diag)
     if not xml_blocks and not output.strip():
-        # Empty-output guard (Task 232): never return a silent blank
-        # REPORT. Substitute the retry hint; status stays REPORT so old
-        # callers keep working. The transcript below records the hint,
-        # not a verdict.
-        output = _empty_output_hint(
-            task_id, _task_state_note(history_key, project_root))
+        # Empty-output triage (Task 259): classify the provider diagnosis
+        # BEFORE falling back to the flake hint. Order is load-bearing:
+        # top-level error -> refusal -> output-budget exhaustion -> flake.
+        state = _task_state_note(history_key, project_root)
+        if diag["error"]:
+            output = _provider_error_hint(diag["error"])
+        elif diag["refusal"]:
+            output = _provider_refusal_hint(diag["refusal"])
+        elif (diag["status"] == "incomplete"
+              and diag["incomplete_reason"] == "max_output_tokens"):
+            output = _output_budget_hint(diag, task_id, state)
+        else:
+            # Transport/model flake (Task 232): never return a silent
+            # blank REPORT. Substitute the retry hint; status stays
+            # REPORT so old callers keep working. The transcript below
+            # records the hint, not a verdict.
+            output = _empty_output_hint(task_id, state)
     fence_drops = list(_last_fence_drops)
     if history_key:
         prompt_hash = hashlib.sha256(effective_prompt.encode("utf-8")).hexdigest()
@@ -2414,11 +2452,11 @@ def brain_turn(
         "retry_count": attempts,
         "prompt_cache_split": cache_split,
     }
+    debug: dict[str, Any] = {"provider": diag}
     if fence_drops:
-        result["debug"] = {
-            "fenced_blocks": len(fence_drops),
-            "snippets": fence_drops,
-        }
+        debug["fenced_blocks"] = len(fence_drops)
+        debug["snippets"] = fence_drops
+    result["debug"] = debug
     return result
 
 
@@ -2495,6 +2533,192 @@ def _empty_output_hint(task_id: Optional[str] = None,
     )
 
 
+def _as_int(value: Any) -> Optional[int]:
+    """Coerce a usage counter to int; ``None`` when absent/unparseable.
+
+    Non-finite floats (``nan``/``inf``) raise inside ``int()`` — they are
+    swallowed here so malformed provider usage can never abort diagnosis
+    (Task 259 hotfix, QA F2).
+    """
+    if isinstance(value, bool):
+        return None
+    if isinstance(value, int):
+        return value
+    if isinstance(value, float):
+        try:
+            return int(value)
+        except (ValueError, OverflowError):
+            return None
+    return None
+
+
+def parse_responses_diagnostics(data: Any) -> dict:
+    """Extract provider diagnostics from a Responses payload (pure).
+
+    Never raises on missing or malformed fields: every key is present with
+    a ``None`` or zeroed value so the caller can return a stable shape on
+    every turn (Task 259 contract). ``refusal`` collects refusal text from
+    both direct ``type=="refusal"`` output items and nested content chunks,
+    so it does not depend on a ``type=="message"`` item existing.
+    """
+    diag: dict[str, Any] = {
+        "status": None,
+        "incomplete_reason": None,
+        "usage": {
+            "input_tokens": None,
+            "output_tokens": None,
+            "reasoning_tokens": None,
+            "total_tokens": None,
+        },
+        "error": None,
+        "refusal": None,
+    }
+    if not isinstance(data, dict):
+        return diag
+
+    status = data.get("status")
+    if isinstance(status, str) and status:
+        diag["status"] = status
+
+    incomplete = data.get("incomplete_details")
+    if isinstance(incomplete, dict):
+        reason = incomplete.get("reason")
+        if isinstance(reason, str) and reason:
+            diag["incomplete_reason"] = reason
+
+    usage = data.get("usage")
+    if isinstance(usage, dict):
+        diag["usage"]["input_tokens"] = _as_int(usage.get("input_tokens"))
+        diag["usage"]["output_tokens"] = _as_int(usage.get("output_tokens"))
+        diag["usage"]["total_tokens"] = _as_int(usage.get("total_tokens"))
+        details = usage.get("output_tokens_details")
+        if isinstance(details, dict):
+            diag["usage"]["reasoning_tokens"] = _as_int(
+                details.get("reasoning_tokens"))
+
+    error = data.get("error")
+    if isinstance(error, str) and error.strip():
+        diag["error"] = error.strip()
+    elif isinstance(error, dict):
+        message = error.get("message")
+        if isinstance(message, str) and message.strip():
+            diag["error"] = message.strip()
+        elif error:
+            # Serialization must never raise on exotic scalar types inside the
+            # error object (Task 259 hotfix) — fall back to repr.
+            try:
+                diag["error"] = json.dumps(error, ensure_ascii=False)
+            except (TypeError, ValueError):
+                diag["error"] = str(error)
+    elif error is not None and not isinstance(error, list):
+        diag["error"] = str(error)
+
+    output = data.get("output")
+    if isinstance(output, list):
+        for item in output:
+            if not isinstance(item, dict):
+                continue
+            if item.get("type") == "refusal":
+                text = item.get("refusal")
+                if isinstance(text, str) and text.strip():
+                    diag["refusal"] = text.strip()
+                    break
+            if item.get("type") == "message":
+                # "content" may be absent, null, or a malformed scalar; only a
+                # real list is iterable (Task 259 hotfix, QA F1).
+                content = item.get("content")
+                if not isinstance(content, list):
+                    continue
+                for chunk in content:
+                    if (isinstance(chunk, dict)
+                            and chunk.get("type") == "refusal"):
+                        text = chunk.get("refusal")
+                        if isinstance(text, str) and text.strip():
+                            diag["refusal"] = text.strip()
+                            break
+                if diag["refusal"]:
+                    break
+    return diag
+
+
+def _log_provider_diagnostics(diag: dict) -> None:
+    """Emit one compact diagnostics line to stderr on every turn (AC1)."""
+    usage = diag.get("usage")
+    if not isinstance(usage, dict):
+        usage = {}
+    print(
+        "brain-bridge: provider diag "
+        f"status={diag.get('status')} "
+        f"incomplete_reason={diag.get('incomplete_reason')} "
+        f"input_tokens={usage.get('input_tokens')} "
+        f"output_tokens={usage.get('output_tokens')} "
+        f"reasoning_tokens={usage.get('reasoning_tokens')} "
+        f"total_tokens={usage.get('total_tokens')} "
+        f"error={diag.get('error')!r} refusal={diag.get('refusal')!r}",
+        file=sys.stderr)
+
+
+def _provider_error_hint(error: str) -> str:
+    """Surface a top-level provider error verbatim (Task 259, terminal)."""
+    return (
+        f"{PROVIDER_ERROR}: the provider returned an error "
+        "(terminal for this turn, never a verdict):\n"
+        f"{error}"
+    )
+
+
+def _provider_refusal_hint(refusal: str) -> str:
+    """Surface a refusal content item verbatim (Task 259, terminal)."""
+    return (
+        f"{PROVIDER_REFUSAL}: the model refused this request "
+        "(terminal for this turn, never a verdict):\n"
+        f"{refusal}"
+    )
+
+
+def _output_budget_hint(diag: dict, task_id: Optional[str] = None,
+                        state: Optional[str] = None) -> str:
+    """Terminal hint for a reasoning-exhausted output budget (Task 259).
+
+    Deliberately NOT ``EMPTY_OUTPUT_RETRY``: a lean retry reuses the same
+    effort and cap, so it can never recover a ``max_output_tokens``
+    finish. Pure function (no I/O), so tests assert the contract directly.
+    """
+    where = f" for task {task_id}" if task_id else ""
+    note = f" Current state: {state}." if state else ""
+    usage = diag.get("usage") or {}
+    return (
+        f"{OUTPUT_BUDGET_EXHAUSTED}: the model produced no visible text{where} "
+        "because its reasoning trace exhausted the output-token budget "
+        "(status=incomplete, reason=max_output_tokens). "
+        "This is NOT a transport flake: do NOT lean-retry and do NOT count "
+        "it as a rejection — the same effort/cap would fail identically. "
+        "Remediate by lowering BRAIN_REASONING_EFFORT (e.g. to medium or low) "
+        "or raising BRAIN_MAX_TOKENS (recommend 32768 or higher when the "
+        "model supports it), then re-run the turn with full context. "
+        f"Usage: input={usage.get('input_tokens')} "
+        f"output={usage.get('output_tokens')} "
+        f"reasoning={usage.get('reasoning_tokens')} "
+        f"total={usage.get('total_tokens')}." + note
+    )
+
+
+def _maybe_warn_reasoning_budget(effort: str, max_tokens: int) -> None:
+    """Warn (non-breaking) when high effort runs with a small cap (C6).
+
+    Reasoning tokens count against ``max_output_tokens``; the bridge keeps
+    its 16384 default in this task, so the risky combination is surfaced
+    to stderr before the provider request instead of silently failing.
+    """
+    if effort in _HIGH_EFFORT and max_tokens < _REASONING_BUDGET_FLOOR:
+        print(
+            f"brain-bridge: warning: reasoning effort {effort!r} with "
+            f"max_output_tokens={max_tokens} (< {_REASONING_BUDGET_FLOOR}) "
+            "can exhaust the output budget and return blank text; raise "
+            "BRAIN_MAX_TOKENS or lower BRAIN_REASONING_EFFORT.",
+            file=sys.stderr)
+
+
 def parse_responses_text(data: dict) -> str:
     """Pull plain text out of a Responses-API payload (pure, offline)."""
     parts: list[str] = []
diff --git a/mcp-decision-server/server.py b/mcp-decision-server/server.py
index ff13817..43bdf0c 100644
--- a/mcp-decision-server/server.py
+++ b/mcp-decision-server/server.py
@@ -194,6 +194,13 @@ _SCRUB_FIELDS = ("original", "english_translation", "summary", "rationale", "tra
 #: Built-in extraction model when DECISION_MODEL is not set.
 DEFAULT_DECISION_MODEL = "gpt-6-astra"
 
+# Provider-failure machine tokens (Task 259) — deliberately distinct from a
+# generic blank: the turn is terminal for the caller's retry logic, so the
+# extraction surface never blames the transcript when the provider failed.
+OUTPUT_BUDGET_EXHAUSTED = "OUTPUT_BUDGET_EXHAUSTED"
+PROVIDER_ERROR = "PROVIDER_ERROR"
+PROVIDER_REFUSAL = "PROVIDER_REFUSAL"
+
 
 def _get_decision_temperature() -> float:
     """Extraction sampling temperature; override via ``DECISION_TEMPERATURE``.
@@ -404,6 +411,176 @@ def _responses_text(data: dict) -> str:
     return "\n".join(parts)
 
 
+def _as_int(value: Any) -> Optional[int]:
+    """Coerce a usage counter to int; ``None`` when absent/unparseable.
+
+    Non-finite floats (``nan``/``inf``) raise inside ``int()`` — they are
+    swallowed here so malformed provider usage can never abort diagnosis
+    (Task 259 hotfix, QA F2).
+    """
+    if isinstance(value, bool):
+        return None
+    if isinstance(value, int):
+        return value
+    if isinstance(value, float):
+        try:
+            return int(value)
+        except (ValueError, OverflowError):
+            return None
+    return None
+
+
+def _responses_diagnostics(data: Any) -> dict:
+    """Extract provider diagnostics from a Responses payload (pure).
+
+    Mirrors ``mcp-brain-bridge`` (Task 259): never raises on missing or
+    malformed fields — every key is present with a ``None`` value so the
+    caller sees a stable shape on every call. ``refusal`` collects refusal
+    text from both direct ``type=="refusal"`` output items and nested
+    content chunks, so it does not depend on a ``type=="message"`` item.
+    """
+    diag: dict[str, Any] = {
+        "status": None,
+        "incomplete_reason": None,
+        "usage": {
+            "input_tokens": None,
+            "output_tokens": None,
+            "reasoning_tokens": None,
+            "total_tokens": None,
+        },
+        "error": None,
+        "refusal": None,
+    }
+    if not isinstance(data, dict):
+        return diag
+
+    status = data.get("status")
+    if isinstance(status, str) and status:
+        diag["status"] = status
+
+    incomplete = data.get("incomplete_details")
+    if isinstance(incomplete, dict):
+        reason = incomplete.get("reason")
+        if isinstance(reason, str) and reason:
+            diag["incomplete_reason"] = reason
+
+    usage = data.get("usage")
+    if isinstance(usage, dict):
+        diag["usage"]["input_tokens"] = _as_int(usage.get("input_tokens"))
+        diag["usage"]["output_tokens"] = _as_int(usage.get("output_tokens"))
+        diag["usage"]["total_tokens"] = _as_int(usage.get("total_tokens"))
+        details = usage.get("output_tokens_details")
+        if isinstance(details, dict):
+            diag["usage"]["reasoning_tokens"] = _as_int(
+                details.get("reasoning_tokens"))
+
+    error = data.get("error")
+    if isinstance(error, str) and error.strip():
+        diag["error"] = error.strip()
+    elif isinstance(error, dict):
+        message = error.get("message")
+        if isinstance(message, str) and message.strip():
+            diag["error"] = message.strip()
+        elif error:
+            # Serialization must never raise on exotic scalar types inside the
+            # error object (Task 259 hotfix) — fall back to repr.
+            try:
+                diag["error"] = json.dumps(error, ensure_ascii=False)
+            except (TypeError, ValueError):
+                diag["error"] = str(error)
+    elif error is not None and not isinstance(error, list):
+        diag["error"] = str(error)
+
+    output = data.get("output")
+    if isinstance(output, list):
+        for item in output:
+            if not isinstance(item, dict):
+                continue
+            if item.get("type") == "refusal":
+                text = item.get("refusal")
+                if isinstance(text, str) and text.strip():
+                    diag["refusal"] = text.strip()
+                    break
+            if item.get("type") == "message":
+                # "content" may be absent, null, or a malformed scalar; only a
+                # real list is iterable (Task 259 hotfix, QA F1).
+                content = item.get("content")
+                if not isinstance(content, list):
+                    continue
+                for chunk in content:
+                    if (isinstance(chunk, dict)
+                            and chunk.get("type") == "refusal"):
+                        text = chunk.get("refusal")
+                        if isinstance(text, str) and text.strip():
+                            diag["refusal"] = text.strip()
+                            break
+                if diag["refusal"]:
+                    break
+    return diag
+
+
+def _log_responses_diagnostics(diag: dict) -> None:
+    """Emit one compact diagnostics line to stderr on every provider call."""
+    usage = diag.get("usage")
+    if not isinstance(usage, dict):
+        usage = {}
+    print(
+        "decision-server: provider diag "
+        f"status={diag.get('status')} "
+        f"incomplete_reason={diag.get('incomplete_reason')} "
+        f"input_tokens={usage.get('input_tokens')} "
+        f"output_tokens={usage.get('output_tokens')} "
+        f"reasoning_tokens={usage.get('reasoning_tokens')} "
+        f"total_tokens={usage.get('total_tokens')} "
+        f"error={diag.get('error')!r} refusal={diag.get('refusal')!r}",
+        file=sys.stderr)
+
+
+def _provider_failure_message(diag: dict) -> Optional[str]:
+    """Precise terminal error for an empty envelope with a known cause.
+
+    Returns ``None`` when the empty text has no provider cause (a genuine
+    model blank), letting the caller fall through to the existing generic
+    non-JSON error. Otherwise returns a message carrying the machine token
+    and the verbatim cause, in the same precedence the bridge uses:
+    error, then refusal, then max_output_tokens exhaustion.
+    """
+    # Normalize before reading so a malformed scalar ``usage`` cannot raise
+    # inside the budget branch; terminal classification is preserved with
+    # null usage values (Task 259 hotfix, QA F3).
+    usage = diag.get("usage")
+    if not isinstance(usage, dict):
+        usage = {}
+    if diag.get("error"):
+        return (
+            f"decision model returned no text: {PROVIDER_ERROR} — the "
+            "provider returned an error (terminal, not a model blank):\n"
+            f"{diag['error']}"
+        )
+    if diag.get("refusal"):
+        return (
+            f"decision model returned no text: {PROVIDER_REFUSAL} — the model "
+            "refused this request (terminal, not a model blank):\n"
+            f"{diag['refusal']}"
+        )
+    if (diag.get("status") == "incomplete"
+            and diag.get("incomplete_reason") == "max_output_tokens"):
+        return (
+            f"decision model returned no text: {OUTPUT_BUDGET_EXHAUSTED} — the "
+            "reasoning trace exhausted the output-token budget "
+            "(status=incomplete, reason=max_output_tokens). This is NOT a "
+            "model blank and NOT a transport flake; retrying with the same "
+            "effort/cap fails identically. Lower DECISION_REASONING_EFFORT "
+            "(or BRAIN_REASONING_EFFORT, e.g. to medium or low) or raise the "
+            "provider output cap, then re-run. "
+            f"Usage: input={usage.get('input_tokens')} "
+            f"output={usage.get('output_tokens')} "
+            f"reasoning={usage.get('reasoning_tokens')} "
+            f"total={usage.get('total_tokens')}."
+        )
+    return None
+
+
 def _utc_today() -> str:
     """UTC date as YYYYMMDD for decision ids."""
     return datetime.now(timezone.utc).strftime("%Y%m%d")
@@ -1073,6 +1250,10 @@ def extract_session_decisions(
             client, api_base.rstrip("/") + "/responses", body
         )
         data = _resp_json(resp)
+    # Task 259: diagnose the provider turn once, log it, and reuse it to
+    # avoid misreporting a provider failure as a model-transcript blank.
+    diag = _responses_diagnostics(data)
+    _log_responses_diagnostics(diag)
     candidates: Any = None
     snippet = ""
     snippet_is_model_text = False
@@ -1101,6 +1282,13 @@ def extract_session_decisions(
         # (Task 191).
         snippet = _responses_text(data).strip()
         snippet_is_model_text = True
+        if not snippet:
+            # Task 259: an empty envelope is only a model blank when the
+            # provider reports no cause. Surface error/refusal/budget
+            # exhaustion verbatim instead of a misleading non-JSON error.
+            provider_failure = _provider_failure_message(diag)
+            if provider_failure:
+                raise RuntimeError(provider_failure)
         candidates = _parse_model_text(snippet, transcript_text, _note_repair)
         if isinstance(candidates, dict):
             if "candidates" in candidates:
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index 22f7740..4b53dd8 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -1793,6 +1793,176 @@ def test_brain_turn_normal_output_has_no_retry_hint(tmp_path, monkeypatch):
     assert bridge.EMPTY_OUTPUT_RETRY not in result["output"]
 
 
+# --- Task 259: provider-diagnosis triage (budget exhaustion != flake) ------
+
+
+def test_parse_responses_diagnostics_full_payload():
+    data = {
+        "status": "incomplete",
+        "incomplete_details": {"reason": "max_output_tokens"},
+        "usage": {
+            "input_tokens": 100,
+            "output_tokens": 16384,
+            "total_tokens": 16484,
+            "output_tokens_details": {"reasoning_tokens": 16384},
+        },
+        "output": [{"type": "reasoning", "summary": []}],
+    }
+    diag = bridge.parse_responses_diagnostics(data)
+    assert diag["status"] == "incomplete"
+    assert diag["incomplete_reason"] == "max_output_tokens"
+    assert diag["usage"] == {
+        "input_tokens": 100,
+        "output_tokens": 16384,
+        "reasoning_tokens": 16384,
+        "total_tokens": 16484,
+    }
+    assert diag["error"] is None
+    assert diag["refusal"] is None
+
+
+def test_parse_responses_diagnostics_tolerates_malformed():
+    for bad in ({}, {"output": None}, {"usage": "nope"}, {"error": {}}, []):
+        diag = bridge.parse_responses_diagnostics(bad)
+        assert set(diag) == {
+            "status", "incomplete_reason", "usage", "error", "refusal"}
+        assert set(diag["usage"]) == {
+            "input_tokens", "output_tokens", "reasoning_tokens",
+            "total_tokens"}
+    assert bridge.parse_responses_diagnostics(None)["status"] is None
+
+
+def test_parse_responses_diagnostics_refusal_direct_and_nested():
+    direct = bridge.parse_responses_diagnostics(
+        {"output": [{"type": "refusal", "refusal": "I cannot help."}]})
+    assert direct["refusal"] == "I cannot help."
+    nested = bridge.parse_responses_diagnostics(
+        {"output": [{"type": "message", "content": [
+            {"type": "refusal", "refusal": "Nested refusal text"}]}]})
+    assert nested["refusal"] == "Nested refusal text"
+
+
+def test_parse_responses_diagnostics_error_shapes():
+    assert bridge.parse_responses_diagnostics(
+        {"error": "boom"})["error"] == "boom"
+    assert bridge.parse_responses_diagnostics(
+        {"error": {"message": "boom2", "type": "x"}})["error"] == "boom2"
+
+
+def test_output_budget_hint_contract():
+    diag = bridge.parse_responses_diagnostics({
+        "status": "incomplete",
+        "incomplete_details": {"reason": "max_output_tokens"},
+        "usage": {"input_tokens": 10, "output_tokens": 20,
+                  "total_tokens": 30,
+                  "output_tokens_details": {"reasoning_tokens": 18}},
+    })
+    hint = bridge._output_budget_hint(
+        diag, "259", "tasks/qa/x.md | status=open")
+    assert bridge.OUTPUT_BUDGET_EXHAUSTED in hint
+    assert bridge.EMPTY_OUTPUT_RETRY not in hint
+    assert "include_bundle=false" not in hint
+    assert "lean-retry" in hint
+    assert "BRAIN_MAX_TOKENS" in hint
+    assert "BRAIN_REASONING_EFFORT" in hint
+    assert "259" in hint
+    assert "reasoning=18" in hint
+
+
+def test_brain_turn_budget_exhaustion_is_terminal(tmp_path, monkeypatch, capsys):
+    payload = {
+        "status": "incomplete",
+        "incomplete_details": {"reason": "max_output_tokens"},
+        "usage": {"input_tokens": 500, "output_tokens": 16384,
+                  "total_tokens": 16884,
+                  "output_tokens_details": {"reasoning_tokens": 16000}},
+        "output": [{"type": "reasoning", "summary": []}],
+    }
+    result = _run_turn(monkeypatch, tmp_path, payload)
+    assert result["status"] == "REPORT"
+    assert bridge.OUTPUT_BUDGET_EXHAUSTED in result["output"]
+    assert bridge.EMPTY_OUTPUT_RETRY not in result["output"]
+    assert "include_bundle=false" not in result["output"]
+    provider = result["debug"]["provider"]
+    assert provider["incomplete_reason"] == "max_output_tokens"
+    assert provider["usage"]["reasoning_tokens"] == 16000
+    err = capsys.readouterr().err
+    assert "provider diag" in err
+    assert "reasoning_tokens=16000" in err
+
+
+def test_brain_turn_refusal_surfaced_verbatim(tmp_path, monkeypatch):
+    payload = {"output": [{"type": "refusal", "refusal": "I must decline."}]}
+    result = _run_turn(monkeypatch, tmp_path, payload)
+    assert bridge.PROVIDER_REFUSAL in result["output"]
+    assert "I must decline." in result["output"]
+    assert bridge.EMPTY_OUTPUT_RETRY not in result["output"]
+    assert result["debug"]["provider"]["refusal"] == "I must decline."
+
+
+def test_brain_turn_provider_error_surfaced_verbatim(tmp_path, monkeypatch):
+    payload = {"error": "upstream exploded", "output": []}
+    result = _run_turn(monkeypatch, tmp_path, payload)
+    assert bridge.PROVIDER_ERROR in result["output"]
+    assert "upstream exploded" in result["output"]
+    assert bridge.EMPTY_OUTPUT_RETRY not in result["output"]
+    assert result["debug"]["provider"]["error"] == "upstream exploded"
+
+
+def test_brain_turn_debug_provider_on_success(tmp_path, monkeypatch):
+    result = _run_turn(monkeypatch, tmp_path, _ok_payload("a real verdict"))
+    assert result["output"] == "a real verdict"
+    assert set(result["debug"]["provider"]) == {
+        "status", "incomplete_reason", "usage", "error", "refusal"}
+
+
+def test_brain_turn_high_effort_budget_warning(tmp_path, monkeypatch, capsys):
+    monkeypatch.setenv("BRAIN_MAX_TOKENS", "16384")
+    for effort in ("high", "xhigh"):
+        monkeypatch.setenv("BRAIN_REASONING_EFFORT", effort)
+        result = _run_turn(monkeypatch, tmp_path, _ok_payload("ok"))
+        assert result["output"] == "ok"
+    err = capsys.readouterr().err
+    # Both high-effort values must warn at the small cap (QA F4).
+    assert "'high'" in err
+    assert "'xhigh'" in err
+    assert "BRAIN_MAX_TOKENS" in err
+
+
+def test_brain_turn_low_effort_skips_budget_warning(tmp_path, monkeypatch,
+                                                    capsys):
+    monkeypatch.setenv("BRAIN_REASONING_EFFORT", "low")
+    monkeypatch.setenv("BRAIN_MAX_TOKENS", "16384")
+    result = _run_turn(monkeypatch, tmp_path, _ok_payload("ok"))
+    assert result["output"] == "ok"
+    assert "reasoning effort" not in capsys.readouterr().err
+
+
+def test_parse_responses_diagnostics_scalar_content_does_not_raise():
+    # A malformed nested "content" scalar must not abort diagnosis (QA F1).
+    for bad_content in (1, "text", {"type": "refusal"}, True):
+        diag = bridge.parse_responses_diagnostics(
+            {"output": [{"type": "message", "content": bad_content}]})
+        assert set(diag) == {
+            "status", "incomplete_reason", "usage", "error", "refusal"}
+        assert diag["refusal"] is None
+
+
+def test_parse_responses_diagnostics_non_finite_usage_is_none():
+    # nan/inf raise inside int(); the parser must swallow them (QA F2).
+    diag = bridge.parse_responses_diagnostics({
+        "usage": {
+            "input_tokens": float("nan"),
+            "output_tokens": float("inf"),
+            "total_tokens": float("-inf"),
+            "output_tokens_details": {"reasoning_tokens": float("nan")},
+        },
+    })
+    assert diag["usage"] == {
+        "input_tokens": None, "output_tokens": None,
+        "reasoning_tokens": None, "total_tokens": None}
+
+
 def test_brain_turn_large_prompt_warns_on_stderr(tmp_path, monkeypatch, capsys):
     big = "x" * (bridge._PROMPT_WARN_CHARS + 1)
     result = _run_turn(monkeypatch, tmp_path, _ok_payload("ok"), prompt=big)
diff --git a/tests/test_decision_server.py b/tests/test_decision_server.py
index 800bce2..b397525 100644
--- a/tests/test_decision_server.py
+++ b/tests/test_decision_server.py
@@ -2032,3 +2032,180 @@ def test_query_skips_falsey_nonlist_alternatives(srv, repo, falsey):
     out = srv.query_manager_decisions("composition")
     assert isinstance(out, str)  # Never raises.
     assert tampered_id not in out  # Falsey non-list must not validate as [].
+
+
+# --- Task 259: provider diagnostics + terminal failure surfacing ----------
+
+
+def _write_transcript_text(path, text):
+    """Write a one-turn transcript whose content varies per test.
+
+    The extraction cache keys on transcript bytes, so tests must use
+    distinct content to avoid cross-test cache hits. The quote ``ship it``
+    is kept so candidate verbatim checks (exact-substring rule) pass.
+    """
+    path.write_text(
+        json.dumps({"role": "user", "content": f"ship it {text}", "name": "m",
+                    "timestamp": "2026-09-19T00:00:00+00:00"}) + "\n",
+        encoding="utf-8",
+    )
+
+
+def _stub_and_extract(srv, monkeypatch, tmp_path, payload, tag):
+    transcript = tmp_path / f"{tag}.jsonl"
+    _write_transcript_text(transcript, tag)
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
+    _stub_decision_http(monkeypatch, _decision_resp(200, "fine", payload))
+    return _extract(srv)(tag, transcript_path=str(transcript))
+
+
+def test_responses_diagnostics_full_payload(srv):
+    payload = {
+        "status": "incomplete",
+        "incomplete_details": {"reason": "max_output_tokens"},
+        "usage": {
+            "input_tokens": 10, "output_tokens": 16384, "total_tokens": 16394,
+            "output_tokens_details": {"reasoning_tokens": 16380},
+        },
+    }
+    diag = srv._responses_diagnostics(payload)
+    assert diag["status"] == "incomplete"
+    assert diag["incomplete_reason"] == "max_output_tokens"
+    assert diag["usage"] == {
+        "input_tokens": 10, "output_tokens": 16384,
+        "reasoning_tokens": 16380, "total_tokens": 16394,
+    }
+    assert diag["error"] is None and diag["refusal"] is None
+
+
+def test_responses_diagnostics_tolerates_malformed(srv):
+    for bad in (None, [], "text", 7, {"usage": "nope", "output": "nope",
+                                      "incomplete_details": 5}):
+        diag = srv._responses_diagnostics(bad)
+        assert set(diag) == {
+            "status", "incomplete_reason", "usage", "error", "refusal"}
+        assert set(diag["usage"]) == {
+            "input_tokens", "output_tokens", "reasoning_tokens", "total_tokens"}
+        assert diag["error"] is None and diag["refusal"] is None
+
+
+def test_responses_diagnostics_refusal_direct_and_nested(srv):
+    direct = {"output": [{"type": "refusal", "refusal": "I cannot do that"}]}
+    assert srv._responses_diagnostics(direct)["refusal"] == "I cannot do that"
+    nested = {"output": [{"type": "message", "content": [
+        {"type": "refusal", "refusal": "no thanks"}]}]}
+    assert srv._responses_diagnostics(nested)["refusal"] == "no thanks"
+
+
+def test_provider_failure_message_precedence(srv):
+    err = {"error": "boom", "output": []}
+    msg = srv._provider_failure_message(srv._responses_diagnostics(err))
+    assert msg.startswith("decision model returned no text: PROVIDER_ERROR")
+    assert "boom" in msg
+
+    refusal = {"output": [{"type": "refusal", "refusal": "nope"}]}
+    msg = srv._provider_failure_message(srv._responses_diagnostics(refusal))
+    assert "PROVIDER_REFUSAL" in msg and "nope" in msg
+
+    budget = {"status": "incomplete",
+              "incomplete_details": {"reason": "max_output_tokens"},
+              "usage": {"output_tokens": 5}, "output": []}
+    msg = srv._provider_failure_message(srv._responses_diagnostics(budget))
+    assert msg.startswith("decision model returned no text: OUTPUT_BUDGET_EXHAUSTED")
+    assert "NOT a model blank" in msg
+
+    # No cause => None so the caller keeps the generic non-JSON error.
+    assert srv._provider_failure_message(
+        srv._responses_diagnostics({"output": []})) is None
+
+
+def test_extract_budget_exhaustion_terminal(srv, tmp_path, monkeypatch):
+    payload = {
+        "status": "incomplete",
+        "incomplete_details": {"reason": "max_output_tokens"},
+        "usage": {"output_tokens": 16384,
+                  "output_tokens_details": {"reasoning_tokens": 16380}},
+        "output": [{"type": "reasoning"}],
+    }
+    with pytest.raises(RuntimeError, match="OUTPUT_BUDGET_EXHAUSTED") as exc:
+        _stub_and_extract(srv, monkeypatch, tmp_path, payload, "budget")
+    # Terminal diagnosis must not masquerade as a transcript/model blank.
+    assert "non-JSON" not in str(exc.value)
+    assert "max_output_tokens" in str(exc.value)
+
+
+def test_extract_provider_error_terminal(srv, tmp_path, monkeypatch):
+    payload = {"error": {"message": "upstream exploded"}, "output": []}
+    with pytest.raises(RuntimeError, match="PROVIDER_ERROR") as exc:
+        _stub_and_extract(srv, monkeypatch, tmp_path, payload, "perr")
+    assert "upstream exploded" in str(exc.value)
+
+
+def test_extract_refusal_terminal(srv, tmp_path, monkeypatch):
+    payload = {"output": [{"type": "refusal", "refusal": "I will not"}]}
+    with pytest.raises(RuntimeError, match="PROVIDER_REFUSAL") as exc:
+        _stub_and_extract(srv, monkeypatch, tmp_path, payload, "pref")
+    assert "I will not" in str(exc.value)
+
+
+def test_extract_genuine_blank_stays_generic(srv, tmp_path, monkeypatch):
+    # No provider cause: the ordinary empty envelope keeps its old error.
+    with pytest.raises(RuntimeError, match="non-JSON"):
+        _stub_and_extract(srv, monkeypatch, tmp_path, {"output": []}, "blank")
+
+
+def test_extract_logs_provider_diag_on_success(srv, tmp_path, monkeypatch, capsys):
+    one = {
+        "verbatim_quote": {"original": "ship it", "english_translation": "y"},
+        "extracted_decision": {"summary": "s", "category": "architecture",
+                               "rationale": "r", "alternatives": [],
+                               "tradeoffs": "t"},
+    }
+    payload = {"status": "completed", "usage": {"output_tokens": 3},
+               "output": [{"type": "message", "content": [
+                   {"type": "output_text", "text": json.dumps(one)}]}]}
+    assert _stub_and_extract(
+        srv, monkeypatch, tmp_path, payload, "diagnostics") == [one]
+    err = capsys.readouterr().err
+    assert "provider diag" in err
+    assert "status=completed" in err
+
+
+def test_responses_diagnostics_scalar_content_does_not_raise(srv):
+    # A malformed nested "content" scalar must not abort diagnosis (QA F1).
+    for bad_content in (1, "text", {"type": "refusal"}, True):
+        diag = srv._responses_diagnostics(
+            {"output": [{"type": "message", "content": bad_content}]})
+        assert set(diag) == {
+            "status", "incomplete_reason", "usage", "error", "refusal"}
+        assert diag["refusal"] is None
+
+
+def test_responses_diagnostics_non_finite_usage_is_none(srv):
+    # nan/inf raise inside int(); the parser must swallow them (QA F2).
+    diag = srv._responses_diagnostics({
+        "usage": {
+            "input_tokens": float("nan"),
+            "output_tokens": float("inf"),
+            "total_tokens": float("-inf"),
+            "output_tokens_details": {"reasoning_tokens": float("nan")},
+        },
+    })
+    assert diag["usage"] == {
+        "input_tokens": None, "output_tokens": None,
+        "reasoning_tokens": None, "total_tokens": None}
+
+
+def test_provider_failure_message_scalar_usage_still_terminal(srv):
+    # A hand-built diagnostic with a scalar usage must not raise in the
+    # budget branch; terminal classification survives with null usage (QA F3).
+    diag = {
+        "status": "incomplete",
+        "incomplete_reason": "max_output_tokens",
+        "usage": 5,
+        "error": None,
+        "refusal": None,
+    }
+    msg = srv._provider_failure_message(diag)
+    assert msg.startswith("decision model returned no text: OUTPUT_BUDGET_EXHAUSTED")
+    assert "input=None" in msg
```
<!-- END_GIT_DIFF -->
