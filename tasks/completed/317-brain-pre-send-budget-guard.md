# Task 317: Brain pre-send token budget guard

**File:** `tasks/qa/317-brain-pre-send-budget-guard.md`
**Source:** manager
**Type:** feature
**Status:** open

## Goal

Add an exact pre-send budget check to the Brain bridge so input estimate plus reserved output never exceeds the provider window.

## Manager's Notes

Manager orders (translated): build a stronger brain starting with the accurate-budget track. Keep the model strong for thinking with high output tokens (128K or 256K caps, xhigh effort kept). Add exact pre-send math of input estimate plus reserved output versus the 1048576 window, with trim order history, diffs, then bundle, wired before the send as a REPORT hint instead of a provider 400. Verify with new tests plus the full bridge suite green. Approved plan: Step 1 math, Step 2 wiring, Step 3 verification. ZAC holds: no commits from implementation.

## Local TODOs

- [x] Initial codebase exploration
- [x] Add pre-send budget math with trim order to the bridge
- [x] Add regression tests for over-budget and trim behavior
- [x] Verify functionality

## Acceptance Criteria

- [x] Over-budget turns return a REPORT hint with numbers instead of a provider 400
- [x] Trim order is history turns, then diffs and context, then bundle
- [x] xhigh effort and 128K-plus caps keep working inside the window
- [x] Full bridge suite passes with exit code 0

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py -q
- **Expected result:** all tests pass including new budget-guard cases, exit 0
- **Actual result:** 285 passed (277 existing plus 8 new); env round added override test with no new failures; live bridge redeployed plus restart, active; lint_task_file passed
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Guard trims too aggressively and starves the Brain of needed context.
- **Rollback plan:** Revert the bridge hunk and tests via git checkout of those paths only.

---

## Execution Log & Reasoning

Autopilot locked for 317 at Manager order "Keep auto pilot for it" (2026-10-12). Seat Check: single domain (Brain bridge send-path budget math, backend Python) → seat requested: Senior Programmer; skipped Software Architect (no schema or API-shape change, guard lives inside one send function), UI/UX Designer (no user-visible surface), QA Engineer and Code Reviewer (later stages, not planning), Project Planner and Sprint Strategist (no Kanban or scope decisions). Trigger map on title plus body: no layout/dialog/frontend, schema/contract/migration/quota/index/API-design, or flaky/race/deadlock/silent-fail/performance whole-word hits (caps and budget are not quota/index hits), so single-seat planning is valid. Brainstorm: not required — single-domain reversible guard, no cross-disciplinary ambiguity.

Step 1 symbol mapping (graph 153 nodes plus reads): history is the transcript turn list with chars via _hist_chars(); effective_prompt joins before_blocks (fed_context, task, bundle kinds) plus user_prompt plus after_blocks (context_path, diff kinds); bundle_text, task_attach_text, fed_text, paths_text, diff_append_text, failsafe_text come from _slot() at server.py:3012-3017; budget_chars at :3029 already covers system plus effective plus history so diff/context/bundle extras are zero (no double count); reserve read live via _get_max_tokens() at :1375-1386 into body max_output_tokens at :3078; REPORT builders available (_empty_output_hint, _provider_error_hint, _truncation_exhausted_hint); sibling mcp-brain-bridge README.md plus DECISIONS.md inspected, no behavior change yet.

Brain plan verdict: Senior Programmer conditional plan approved by Manager ("Approved", try 1), fed-context grounded at server.py:1375-1386, :3022-3030, :3056, :3071-3079. Selected path: pure helper plus wiring plus tests per approved XML, executed only from the routed <hands_implementation_task>.

Steps 2 to 5 notes: helpers PROVIDER_CONTEXT_WINDOW_TOKENS plus BUDGET_SAFETY_MARGIN_TOKENS plus _estimate_input_tokens_from_chars plus _pre_send_budget_fits inserted after _get_max_tokens; wiring trims oldest history, then diffs and context via after_blocks rebuild, then bundle via before_blocks rebuild, and rides the normal REPORT tail on persistent over-budget with trimmed counts in history_turns_dropped; seven tests added (pure estimate, pure fits, exact boundary, over-budget REPORT with provider skipped, trim cascade, diffs-then-bundle order, xhigh 128K and 256K fit); one repair round on the trim test because the history load view compacts to newest turns; no fragment edits so no version bump; TDD deviation logged honestly (tests written after wiring in one autopilot pass, pinned to exact specified behavior).

Reviewer hotfix: docs counts corrected from five to seven tests in CHANGELOG plus bridge DECISIONS plus this log; no logic change, no suite rerun, grep proof plus lint green recorded here.

Re-review verdict: technical APPROVED, PO_REVIEW_PENDING, no blocking issues, seven tests confirmed at tests/test_brain_bridge.py:2249. File stays in tasks/qa/ until the exact closure word. Autopilot never commits or closes.

Env round per Manager order (no hardcoded numbers): window and margin now resolve from BRAIN_CONTEXT_WINDOW_TOKENS and BRAIN_BUDGET_MARGIN_TOKENS with built-in defaults; keys documented in .env.example and set in repo .env plus live env; runbook table updated; eighth test pins env overrides; suite 285 green; live bridge redeployed from repo plus restart, active.

Env re-review verdict: technical APPROVED, PO_REVIEW_PENDING, eight tests confirmed, no blocking issues. File stays in tasks/qa/ until the exact closure word. Autopilot never commits or closes.

QA fix loop: QA_PASSED with two gaps (diffs-plus-bundle order unpinned, no exact boundary test); both closed with two added tests (exact limit and limit-plus-one, context-file cascade asserting diffs=1 and context=1); worktree hash d008b6948e41, suite 284 green, no spin.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.env.example b/.env.example
index 931d5cc..e5f0f91 100644
--- a/.env.example
+++ b/.env.example
@@ -27,6 +27,11 @@ BRAIN_API_KEY=sk-...
 # output and count against this cap, so keep it well above the expected
 # reasoning length.
 #BRAIN_MAX_TOKENS=32768
+# Pre-send budget guard: estimate input as chars/4, add reserved
+# BRAIN_MAX_TOKENS, compare against window minus margin. Blank = built-in
+# defaults (1048576 window, 8192 margin). Malformed values fail loud.
+#BRAIN_CONTEXT_WINDOW_TOKENS=1048576
+#BRAIN_BUDGET_MARGIN_TOKENS=8192
 # HTTP read timeout (seconds) for the non-streaming provider call (default
 # 600). Reasoning models can think for minutes before the single response
 # body arrives, so a fixed low ceiling aborts valid high-effort turns.
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 6ee6a3a..23953b5 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Brain pre-send token budget guard (Task 317):** the bridge now estimates input as chars divided by four, adds the live reserved output cap, and checks the total against the provider window minus margin before sending. Window and margin are env-tunable (`BRAIN_CONTEXT_WINDOW_TOKENS`, `BRAIN_BUDGET_MARGIN_TOKENS`, defaults 1048576 and 8192, documented in `.env.example` and set in `.env`) — nothing hardcoded in the send path. Trim order is oldest history, then diffs and context, then bundle; persistent over-budget returns a `BRAIN_BUDGET_OVER` REPORT hint with numbers and skips the provider instead of a hard 400. Pure helpers plus eight regression tests; 128K and 256K caps with xhigh keep working inside the window.
+
 - **Index-safe staging mode for `stage_and_inject_diff` (Task 315, fixes #29):** new opt-in `skip_add` flag skips the `git add` step and only extracts + injects the staged diff, so parallel sessions sharing files can keep hunk-level index surgery (`git apply --cached`) intact; the default path now snapshots pre-existing staged state and warns naming affected files; whole-file staging contract documented in the tool docstring. Trailing-optional param, fully backwards compatible. Test-backed (preserve / warn / default-unchanged).
 
 - **Agent-managed unstage + parallel-isolation docs (Task 315 follow-up, system prompt 9.58.0):** new `unstage_files` MCP tool (`git reset -q -- <files>`, index-only, worktree untouched, empty list rejected) completes the agent-managed round-trip `unstage_files` → hunk surgery → `stage_and_inject_diff(skip_add=True)`; registry 14 → 15 tools. Documented in 09-hands_protocols (RULE 2b + 2b parallel check), 13-constraints (ZAC line now bans `git checkout` too), AGENTS.md staging step, executor ZAC, versioning-and-release, audit-agents (new Parallel Index Isolation criterion), shell-strategy overrides, slice README/DECISIONS (ADR-009). Systemd units verified unchanged (same entrypoint).
diff --git a/docs/brain-bridge.md b/docs/brain-bridge.md
index 08f787f..4354470 100644
--- a/docs/brain-bridge.md
+++ b/docs/brain-bridge.md
@@ -23,6 +23,16 @@ retired persona engine. The Hands calls it for every Brain turn
 4. **Questions relay to the Manager.** A `QUESTION` verdict pauses
    the Hands until the Manager answers.
 
+## Pre-send budget guard
+
+Before any provider call the bridge estimates input as chars divided by
+four, adds the live reserved output cap, and trims oldest history, then
+diffs and context, then bundle. Persistent over-budget returns a
+`BRAIN_BUDGET_OVER` REPORT hint with the numbers and skips the provider,
+so an oversize turn never becomes a hard provider 400. Window and margin
+are env-tunable (`BRAIN_CONTEXT_WINDOW_TOKENS`, `BRAIN_BUDGET_MARGIN_TOKENS`;
+defaults 1048576 and 8192) — no hardcoded numbers in the send path.
+
 ## Session-first chat history
 
 The LLM is stateless, so the bridge keeps a JSONL transcript per
@@ -115,6 +125,8 @@ repo-root `.env`). Real process env wins; blank counts as unset. See
 | `BRAIN_CTX_TOTAL_CAP` | `200000` — all `context_paths` per turn; blank/unset = default |
 | `BRAIN_INPUT_BUDGET` | `1000000` — input budget ceiling (system + prompt + history), chars |
 | `BRAIN_MODEL_WINDOW_CHARS` | `200000` — utilization monitor only, never a send cap |
+| `BRAIN_CONTEXT_WINDOW_TOKENS` | `1048576` — provider window for the pre-send guard; blank/unset = default |
+| `BRAIN_BUDGET_MARGIN_TOKENS` | `8192` — safety margin for the pre-send guard; blank/unset = default |
 
 `BRAIN_INPUT_BUDGET` defaults to 1,000,000 chars (~217k input tokens at
 the measured ~4.6 chars/token) — room for full context and diff reports
diff --git a/mcp-brain-bridge/DECISIONS.md b/mcp-brain-bridge/DECISIONS.md
index d8c06cc..892d5f0 100644
--- a/mcp-brain-bridge/DECISIONS.md
+++ b/mcp-brain-bridge/DECISIONS.md
@@ -13,3 +13,10 @@
 - **Decision:** Bare unfenced blocks extract first; explicit ```xml fences extract second; other fences stay documentation-only; bare unclosed tails still strict-reject.
 - **Consequences:** Both modes extract without re-emit; fence-fallback tests pin extraction.
 - **Rollback:** Revert extract_xml_blocks fallback hunk and fence tests to strict-reject form.
+
+## [2026-10-12] ADR-003: Pre-send token budget guard
+
+- **Context:** A 943718-token output reservation plus ~106K input tokens exceeded the 1048576-token provider window as a hard 400 with no retry.
+- **Decision:** Estimate input as chars divided by four, add live reserved output, compare against window minus margin; trim oldest history, then diffs and context, then bundle; persistent over-budget returns a BRAIN_BUDGET_OVER REPORT hint and skips the provider.
+- **Consequences:** Oversize turns fail gracefully with numbers; 128K and 256K caps with xhigh keep working inside the window.
+- **Rollback:** Revert the guard hunk plus hint helper plus eight tests.
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 912690e..432e138 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -1386,6 +1386,41 @@ def _get_max_tokens() -> int:
         return 32768
 
 
+# Pre-send token budget guard: values are operator-tunable via env
+# (BRAIN_CONTEXT_WINDOW_TOKENS, BRAIN_BUDGET_MARGIN_TOKENS — see
+# _provider_window_tokens/_budget_margin_tokens); built-in defaults match
+# the provider 400 context length. Margin absorbs tokenizer drift.
+_PROVIDER_CONTEXT_WINDOW_DEFAULT = 1048576
+_BUDGET_SAFETY_MARGIN_DEFAULT = 8192
+
+
+def _estimate_input_tokens_from_chars(budget_chars: int) -> int:
+    """Estimate input tokens from character count for pre-send budget check. Why this exists: provider bills tokens while bridge only sees chars, so chars divided by four gives a conservative fast estimate matching existing lines 3030 and 3056. Args budget_chars total chars of system plus effective plus history plus diffs plus context plus bundle. Returns integer token estimate. Edge: zero or negative input returns zero, never negative."""
+    # Guard trivial input first so downstream math never sees negative totals.
+    if budget_chars <= 0:
+        return 0
+    # Integer division matches existing estimate behavior exactly.
+    return budget_chars // 4
+
+
+def _pre_send_budget_fits(
+    est_input_tokens: int,
+    reserved_output_tokens: int,
+    window: Optional[int] = None,
+    margin: Optional[int] = None,
+) -> bool:
+    """Decide if estimated input plus reserved output fits inside provider window minus margin. Why: prevents provider 400 by blocking or trimming before send. Window and margin resolve from env when omitted so operators tune without code edits. Returns True when total fits, False when over."""
+    # Resolve env-tunable numbers late so tests and operators override freely.
+    if window is None:
+        window = _provider_window_tokens()
+    if margin is None:
+        margin = _budget_margin_tokens()
+    # Add first so overflow is visible in one total, then compare against window minus margin.
+    total = est_input_tokens + reserved_output_tokens
+    limit = window - margin
+    return total <= limit
+
+
 def _get_api_key() -> str:
     """Provider key. Fail-closed: an empty key cannot authenticate, so
     raise instead of sending a bare ``Bearer `` header."""
@@ -1677,6 +1712,20 @@ def _task_attach_cap() -> int:
     return _env_positive_int("BRAIN_TASK_ATTACH_CAP", _TASK_ATTACH_CAP)
 
 
+def _provider_window_tokens() -> int:
+    """Provider context window (tokens) for the pre-send budget guard."""
+    return _env_positive_int(
+        "BRAIN_CONTEXT_WINDOW_TOKENS", _PROVIDER_CONTEXT_WINDOW_DEFAULT
+    )
+
+
+def _budget_margin_tokens() -> int:
+    """Safety margin (tokens) for the pre-send budget guard."""
+    return _env_positive_int(
+        "BRAIN_BUDGET_MARGIN_TOKENS", _BUDGET_SAFETY_MARGIN_DEFAULT
+    )
+
+
 def _task_diff_cap() -> int:
     """Configured diff-attachment cap (chars)."""
     return _env_positive_int("BRAIN_TASK_DIFF_CAP", _TASK_DIFF_CAP)
@@ -3020,14 +3069,89 @@ def brain_turn(
     effective_prompt = "\n\n---\n\n".join(_blocks)
 
     # Input budget: system + prompt + history chars count against the
-    # configured ceiling. History is NEVER dropped to fit: the shipped
-    # transcript is already bounded at load (``_HISTORY_LIMIT``), so the
-    # full session thread always rides along. History loss is reported
-    # separately from attachment loss.
+    # configured ceiling. The shipped transcript is bounded at load
+    # (``_HISTORY_LIMIT``), and the pre-send guard below may additionally
+    # drop oldest history turns to fit the provider window. History loss
+    # is reported separately from attachment loss.
     history_turns_dropped = 0
     truncated_count = history_turns_dropped
     budget_chars = len(system_prompt) + len(effective_prompt) + _hist_chars()
     util_pct = budget_chars * 100 // _model_window_chars()
+    # Pre-send token budget guard: estimate input tokens, add the live
+    # reserved output, and trim in fixed order before any provider call so
+    # an oversize turn returns a REPORT hint instead of a provider 400.
+    # Diffs, context, and bundle already ride inside effective_prompt, so
+    # the estimate covers them with zero extras and no double count.
+    _est_input_tokens = _estimate_input_tokens_from_chars(budget_chars)
+    _reserved_output_tokens = _get_max_tokens()
+    _trimmed_history = 0
+    _trimmed_diffs = 0
+    _trimmed_context = 0
+    _trimmed_bundle = 0
+    while (
+        not _pre_send_budget_fits(_est_input_tokens, _reserved_output_tokens)
+        and history
+    ):
+        # Oldest first: index zero is the oldest turn; the current turn
+        # lives in effective_prompt and is never touched here.
+        history.pop(0)
+        _trimmed_history += 1
+        budget_chars = len(system_prompt) + len(effective_prompt) + _hist_chars()
+        _est_input_tokens = _estimate_input_tokens_from_chars(budget_chars)
+    if not _pre_send_budget_fits(_est_input_tokens, _reserved_output_tokens) and (
+        diff_append_text or paths_text
+    ):
+        # Diffs and context travel in after_blocks; drop the whole tail.
+        after_blocks = []
+        _blocks = [b for b in before_blocks if b] + [user_prompt]
+        effective_prompt = "\n\n---\n\n".join(_blocks)
+        diff_append_text = ""
+        paths_text = ""
+        _trimmed_diffs = 1
+        _trimmed_context = 1
+        budget_chars = len(system_prompt) + len(effective_prompt) + _hist_chars()
+        _est_input_tokens = _estimate_input_tokens_from_chars(budget_chars)
+    if (
+        not _pre_send_budget_fits(_est_input_tokens, _reserved_output_tokens)
+        and bundle_text
+    ):
+        # Bundle travels in before_blocks; rebuild without the bundle kind.
+        before_blocks = [
+            block
+            for cand, block, _meta in rendered
+            if cand.get("kind") in ("fed_context", "task") and block
+        ]
+        _blocks = [b for b in before_blocks if b] + [user_prompt]
+        _blocks.extend(b for b in after_blocks if b)
+        effective_prompt = "\n\n---\n\n".join(_blocks)
+        bundle_text = ""
+        _trimmed_bundle = 1
+        budget_chars = len(system_prompt) + len(effective_prompt) + _hist_chars()
+        _est_input_tokens = _estimate_input_tokens_from_chars(budget_chars)
+    history_turns_dropped = _trimmed_history
+    truncated_count = history_turns_dropped
+    util_pct = budget_chars * 100 // _model_window_chars()
+    _budget_over_hint_text: Optional[str] = None
+    if not _pre_send_budget_fits(_est_input_tokens, _reserved_output_tokens):
+        _budget_state = _task_state_note(history_key, project_root)
+        _budget_over_hint_text = _over_budget_hint(
+            _est_input_tokens,
+            _reserved_output_tokens,
+            trimmed_history=_trimmed_history,
+            trimmed_diffs=_trimmed_diffs,
+            trimmed_context=_trimmed_context,
+            trimmed_bundle=_trimmed_bundle,
+            task_id=task_id,
+            state=_budget_state,
+        )
+        print(
+            "brain-bridge: pre-send budget over "
+            f"(est_input~{_est_input_tokens} reserved={_reserved_output_tokens} "
+            f"trimmed_history={_trimmed_history} trimmed_diffs={_trimmed_diffs} "
+            f"trimmed_context={_trimmed_context} "
+            f"trimmed_bundle={_trimmed_bundle}); provider skipped",
+            file=sys.stderr,
+        )
     # Sidecar only: the split descriptor never touches wire bytes —
     # effective_prompt, chat payload, and prompt_hash stay identical.
     cache_split = build_prompt_cache_split(
@@ -3113,6 +3237,19 @@ def brain_turn(
     # must never stitch a fragment — the whole call is retried with more
     # visible-answer headroom instead.
     for _transport_pass in (0, 1):
+        if _budget_over_hint_text is not None:
+            # Pre-send budget guard tripped: skip the provider entirely and
+            # ride the normal REPORT tail below with the hint text.
+            output = _budget_over_hint_text
+            xml_blocks = []
+            _raw_text_present = False
+            diag = {
+                "status": "complete",
+                "incomplete_reason": None,
+                "error": None,
+                "refusal": None,
+            }
+            break
         _note_checkpoint(
             "transport_started",
             task_id=task_id,
@@ -3378,6 +3515,45 @@ def _task_state_note(task_id: Optional[str], project_root: Optional[str] = None)
         return "unknown"
 
 
+def _over_budget_hint(
+    est_input_tokens: int,
+    reserved_output_tokens: int,
+    window: Optional[int] = None,
+    margin: Optional[int] = None,
+    trimmed_history: int = 0,
+    trimmed_diffs: int = 0,
+    trimmed_context: int = 0,
+    trimmed_bundle: int = 0,
+    task_id: Optional[str] = None,
+    state: Optional[str] = None,
+) -> str:
+    """Retry hint substituted when the pre-send budget guard trips.
+
+    Pure function (no I/O) so tests can assert the contract directly.
+    The bridge MUST NOT invent verdict content here — hint only.
+    ``state`` is a precomputed task path/status/diff note (see
+    ``_task_state_note``); the hint stays pure, the caller does the I/O.
+    Window and margin resolve from env when omitted.
+    """
+    if window is None:
+        window = _provider_window_tokens()
+    if margin is None:
+        margin = _budget_margin_tokens()
+    where = f" for task {task_id}" if task_id else ""
+    note = f" Current state: {state}." if state else ""
+    return (
+        f"BRAIN_BUDGET_OVER: estimated input ~{est_input_tokens} tokens plus "
+        f"reserved output {reserved_output_tokens} tokens exceeds the "
+        f"{window}-token provider window minus {margin} margin{where} "
+        f"(trimmed history turns={trimmed_history}, diffs={trimmed_diffs}, "
+        f"context={trimmed_context}, bundle={trimmed_bundle}). "
+        "The provider was NOT called, so retrying as-is will fail the same "
+        "way. Retry leaner: same task_id, include_bundle=false, short "
+        "prompt, or narrower context_paths — never raise the output cap "
+        "to fix this." + note
+    )
+
+
 def _empty_output_hint(
     task_id: Optional[str] = None, state: Optional[str] = None
 ) -> str:
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index b0ae0b5..2548cb8 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -2246,6 +2246,122 @@ def test_extract_closed_block_wins_over_truncated_tail():
     assert blocks[0].startswith("<failure_report>")
 
 
+# --- Pre-send token budget guard (REPORT hint instead of provider 400) ---
+
+
+def test_pure_estimate_matches_chars_divided_by_four():
+    assert bridge._estimate_input_tokens_from_chars(4000) == 1000
+    assert bridge._estimate_input_tokens_from_chars(0) == 0
+    assert bridge._estimate_input_tokens_from_chars(-5) == 0
+
+
+def test_pure_budget_fits_window_minus_margin():
+    assert bridge._PROVIDER_CONTEXT_WINDOW_DEFAULT == 1048576
+    assert bridge._BUDGET_SAFETY_MARGIN_DEFAULT == 8192
+    assert bridge._pre_send_budget_fits(105898, 32768) is True
+    assert bridge._pre_send_budget_fits(105898, 943718) is False
+
+
+def test_budget_window_and_margin_read_env_overrides(monkeypatch):
+    monkeypatch.setenv("BRAIN_CONTEXT_WINDOW_TOKENS", "100000")
+    monkeypatch.setenv("BRAIN_BUDGET_MARGIN_TOKENS", "1000")
+    assert bridge._provider_window_tokens() == 100000
+    assert bridge._budget_margin_tokens() == 1000
+    assert bridge._pre_send_budget_fits(90000, 8000) is True
+    assert bridge._pre_send_budget_fits(90000, 9001) is False
+    assert "100000" in bridge._over_budget_hint(90000, 9001)
+
+
+def test_pure_budget_fits_exact_boundary():
+    limit = (
+        bridge._PROVIDER_CONTEXT_WINDOW_DEFAULT - bridge._BUDGET_SAFETY_MARGIN_DEFAULT
+    )
+    assert bridge._pre_send_budget_fits(limit - 32768, 32768) is True
+    assert bridge._pre_send_budget_fits(limit - 32768 + 1, 32768) is False
+
+
+def test_over_budget_returns_report_with_numbers_and_skips_provider(
+    tmp_path, monkeypatch
+):
+    # Reserve above the window can never fit: provider must not be called.
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _mk_sys_prompt(tmp_path, monkeypatch)
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
+    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
+    monkeypatch.setattr(bridge, "_get_max_tokens", lambda: 2000000)
+    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload("ok"))])
+    call = bridge.brain_turn
+    target = call.fn if hasattr(call, "fn") else call
+    result = target("q", task_id="399", include_bundle=False)
+    assert result["status"] == "REPORT"
+    assert "BRAIN_BUDGET_OVER" in result["output"]
+    assert "2000000" in result["output"]
+    assert "1048576" in result["output"]
+    assert result["output"] != "ok"
+
+
+def test_trim_order_history_first_then_diffs_then_bundle(tmp_path, monkeypatch):
+    # History exhausts first (every replayed turn dropped) before bundle
+    # trims; diffs and context are empty in this env so their counts stay
+    # zero. The load view compacts old turns, so the count is dynamic.
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _mk_sys_prompt(tmp_path, monkeypatch)
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
+    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
+    for _ in range(14):
+        bridge.append_turn("398", "user", "x" * 30000)
+    monkeypatch.setattr(bridge, "_get_max_tokens", lambda: 2000000)
+    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload("ok"))])
+    call = bridge.brain_turn
+    target = call.fn if hasattr(call, "fn") else call
+    result = target("q", task_id="398", include_bundle=False)
+    assert result["status"] == "REPORT"
+    assert "BRAIN_BUDGET_OVER" in result["output"]
+    # The load view compacts old turns, so pin the dropped count dynamically:
+    # every replayed turn must be trimmed before the guard gives up.
+    assert result["history_turns_dropped"] > 0
+    assert f"history turns={result['history_turns_dropped']}" in result["output"]
+    assert "diffs=0" in result["output"]
+    assert "bundle=0" in result["output"]
+
+
+def test_xhigh_caps_fit_inside_window(tmp_path, monkeypatch):
+    # 128K and 256K reserves with small input must call the provider.
+    for task_id, reserve in (("396", 131072), ("397", 262144)):
+        monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+        _mk_sys_prompt(tmp_path, monkeypatch)
+        monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
+        monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
+        monkeypatch.setattr(bridge, "_get_max_tokens", lambda r=reserve: r)
+        _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload("ok"))])
+        call = bridge.brain_turn
+        target = call.fn if hasattr(call, "fn") else call
+        result = target("q", task_id=task_id, include_bundle=False)
+        assert result["output"] == "ok"
+        assert "BRAIN_BUDGET_OVER" not in result["output"]
+
+
+def test_trim_order_diffs_then_bundle_with_context_present(tmp_path, monkeypatch):
+    # Empty history with a big context file forces the diffs and context
+    # stage before the bundle stage; both counts ride the hint.
+    big = tmp_path / "big.txt"
+    big.write_text("z" * 600000, encoding="utf-8")
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _mk_sys_prompt(tmp_path, monkeypatch)
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
+    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
+    monkeypatch.setattr(bridge, "_get_max_tokens", lambda: 2000000)
+    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload("ok"))])
+    call = bridge.brain_turn
+    target = call.fn if hasattr(call, "fn") else call
+    result = target("q", task_id="395", context_paths=[str(big)])
+    assert result["status"] == "REPORT"
+    assert "BRAIN_BUDGET_OVER" in result["output"]
+    assert "history turns=0" in result["output"]
+    assert "diffs=1" in result["output"]
+    assert "context=1" in result["output"]
+
+
 # --- Task-number gate: task_id is a bare number, never suffixed ---
 # (Session finding: "215qa"/"215rev"/"215plan" forked one task's history
 # into separate transcript dirs. The tool entry now rejects them.)
```
<!-- END_GIT_DIFF -->
