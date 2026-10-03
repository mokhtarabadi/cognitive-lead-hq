# Task 291: Brain truncated-XML server-side recovery

**File:** `tasks/qa/291-brain-truncated-xml-recovery.md`
**Source:** manager
**Type:** bugfix
**Status:** open

## Goal

End `brain_turn` truncated-XML retry loops permanently: when a long implement turn exhausts `max_output_tokens`, the bridge recovers server-side instead of returning a fragment the caller must re-bill.

## Manager's Notes

Manager order (verbatim, translated from Persian): "Brain output always gets cut off. Fix it permanently. Issue registered, exact. Start by searching how other tools really use LLMs so this never happens to them. Find the details of the Muse model we use and configure it in the best possible way so this never happens again and Brain always returns complete comprehensive output without cutoff." Issue: https://github.com/mokhtarabadi/cognitive-lead-hq/issues/28

## Deployment Facts (verified 2026-10-03, research phase)

- Model (all tiers): `meta/muse-spark-1.3-contributor` via OpenRouter (`BRAIN_API_BASE=https://openrouter.ai/api/v1`)
- `.env`: `BRAIN_REASONING_EFFORT=xhigh`, `BRAIN_MAX_TOKENS=943718`
- Code already classifies empty-output budget exhaustion (`OUTPUT_BUDGET_EXHAUSTED`, Task 259) but partial truncation (non-empty, missing close tag) only semantic-rejects → caller-side retry loop
- `xhigh` allocates ~95% of `max_output_tokens` to reasoning (server.py:3753) — reasoning share vs visible-answer budget is the core tension

## Local TODOs

- [x] Research: exact `meta/muse-spark-1.3-contributor` output limits on OpenRouter + how OpenRouter handles oversized `max_output_tokens`
- [x] Research: how other agent tools avoid truncation (continuation turns, chunked generation, reasoning/answer budget split)
- [x] Implement F1: server-side auto-recovery for partial truncation (continue-turn or lower-effort retry, bounded, no infinite loop)
- [ ] Implement F2: cap/budget config review (default cap, reasoning share guard, document `BRAIN_MAX_TOKENS`/`BRAIN_REASONING_EFFORT`)
- [x] Regression tests + verification gate, CHANGELOG entry

## Acceptance Criteria

- [x] A truncated implement turn (incomplete/max_output_tokens with partial XML) no longer returns a bare fragment — bridge auto-recovers server-side
- [x] Recovery is bounded (max 1-2 extra attempts, no token-burn loop)
- [x] Existing contracts intact: `EMPTY_OUTPUT_RETRY`, `OUTPUT_BUDGET_EXHAUSTED`, semantic gate, retry policy for 5xx/429
- [ ] Optimal `BRAIN_MAX_TOKENS`/`BRAIN_REASONING_EFFORT` values documented for the deployed model

## Verification Evidence

- **Test command:** rtk test uv run --with-requirements /tmp/opencode/clh-test-reqs.txt pytest tests/test_brain_bridge.py -q
- **Expected result:** pass, exit code 0
- **Actual result:** `283 passed in 1.46s` after QA hotfix (272 pre-existing + 11 Task 291 tests), exit 0
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** auto-recovery adds provider spend per truncated turn; must stay bounded and cheaper than today's full caller-side retry.
- **Rollback plan:** revert server.py hunks; env-only mitigation (`BRAIN_MAX_TOKENS`/`BRAIN_REASONING_EFFORT`) reverts by restoring `.env`.

---

## Execution Log & Reasoning

**Research phase (2026-10-03):** plan approved by Manager; task created in backlog during research, moves to in-progress at implementation.

**R1 — Model identity (verified):** deployed model is `meta/muse-spark-1.3-contributor` (Meta, all tiers) via OpenRouter Responses API. Published specs: 1,048,576 context, **943,718 max output** — `.env` `BRAIN_MAX_TOKENS=943718` already sits exactly at the model ceiling. The ceiling is NOT the problem.

**R2 — Live config resolves the stale premise:** issue #28 assumed default 32768/no override, but the live bridge (systemd `mcp-brain.service`, PID 99424) prints `loaded env from /home/mohammad/.config/opencode/.env`, which carries `BRAIN_MAX_TOKENS=943718` + `BRAIN_REASONING_EFFORT=xhigh`. (`/proc` hides runtime `os.environ` writes — proven by probe test — so the journal line, not `/proc`, is the source of truth.)

**R3 — Root cause is reasoning share, not the cap (measured):** today's provider diags show e.g. `output_tokens=15024 reasoning_tokens=14683 visible_tokens=341` — ~97% of the output budget burned by reasoning, ~300 visible tokens left. `xhigh` targets ~95% reasoning share (server.py:3753). Long implement reasoning scales to fill ANY cap, so raising the ceiling cannot fix starvation — it only makes each retry loop ~30x more expensive.

**R4 — Industry playbook (dreaming.press + OpenAI/Anthropic docs):** (a) read the stop field on every call (we do); (b) branch by output type — prose continues from partial, STRUCTURED output (our XML contracts) must discard the fragment and retry whole with more headroom, never stitch; (c) budget reasoning separately from visible answer. "More headroom" at max cap means LOWERING reasoning share or shrinking input, not raising the cap.

**Fix shape:** F1 recovery = one bounded server-side re-issue with lower effort (frees visible share) on partial truncation; terminal hint if it also truncates (no caller loop). Plus config recommendation: drop implement-turn effort from `xhigh` (proposal in implementation log).

**Implementation (2026-10-03, `mcp-brain-bridge/server.py`):**
- New machine token `TRUNCATION_UNRECOVERABLE` + `_truncation_exhausted_hint` (terminal: caller must NOT retry as-is).
- New `_step_down_effort` (`max→xhigh→high→medium→low`, floor at `low`, unknown→`medium`).
- `brain_turn` transport wrapped in a max-2-pass loop: pass 0 partial truncation (RAW non-empty text + incomplete/max_output_tokens + no usable XML, reasoning key present, step-down changes effort) discards the fragment and re-issues once with lower effort; else break. Fragment never reaches the transcript. `retry_count` now sums both passes. Task 259 empty-path untouched (eligibility judged on raw text before triage rewrite).
- 6 new tests in `tests/test_brain_bridge.py` (mapping, terminal hint, recover-once with effort assertion xhigh→high, exhausted-terminal with exactly-2-calls, no-recovery-when-complete, effort-floor). Full file: 278 passed.

**Open decisions for Manager (F2/config, live `.env` NOT touched):** D1 — lower live `BRAIN_REASONING_EFFORT` from `xhigh` (today reasoning burns ~97% of output; `high`/`medium` gives visible XML a real share). D2 — keep `BRAIN_MAX_TOKENS=943718` (already at model ceiling; raising further impossible). D3 — deploy = copy repo `server.py` over installed copy + `systemctl --user restart mcp-brain` (installed copy is byte-identical today, so deploy after merge).

**QA round 1 verdict: QA_REJECTED (2026-10-03).** Brain confirmed main path (bounded, discard-not-stitch, contracts, production pattern) but found: F1/F2 floor + temperature-mode truncations returned silent fragments (final gate required `_recovery_used`); F3 case-sensitive floor compare (`LOW` vs `low`) caused one spurious billed re-issue. Required M1–M5 tests. Hotfix applied same day (see above).

**Review verdict: APPROVED / PO_REVIEW_PENDING (2026-10-03, autopilot review).** Scope tight (3 files), approach matches blueprint, all QA items closed, evidence real. C1/C2 low cosmetics, no change needed before closure. Awaiting Manager "Approved for closure".

**Hotfix applied (same day, file stays in qa):** case-insensitive floor guard via normalized compare; terminal broadened to ANY unrecovered partial truncation (`not xml_blocks and _raw_text_present and incomplete/max_output_tokens and token not already in output`) — empty-output keeps Task 259 hints (raw empty), usable XML never converts. Floor/temperature/empty/complete-XML/uppercase-LOW/prose-floor tests added (5 new); fragment-absence asserted on recovery + exhausted paths. Full file: 283 passed. CHANGELOG untouched per hotfix scope.

**QA round 2 verdict: QA_PASSED (2026-10-03, autopilot re-QA).** F1 floor/temperature terminal, F2 uppercase LOW single-call, F3 contracts intact, F4 fragment-free recovery, F5 bounded. Notes (non-blocking): `_recovery_used` write-only, CHANGELOG wording centers second-truncation.

**Review verdict: APPROVED / PO_REVIEW_PENDING (2026-10-03, autopilot review).** Scope tight (3 files), approach matches blueprint, all QA items closed, evidence real. C1/C2 low cosmetics, no change needed before closure. Awaiting Manager "Approved for closure".

**Autopilot locked (2026-10-03, Manager order "Lock auto pilot for task"):** full saga runs inside my own turns — re-QA, fix loop, review, stage, qa — stopping only for hard blockers and the closure gate (explicit "Approved for closure"/"Close task" required; NEVER auto-commit, NEVER auto-close).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 2af9bc0..98f37a1 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Brain partial-truncation server-side recovery (Task 291, fixes issue #28):** long implement `brain_turn` calls truncated by `max_output_tokens` no longer return a bare fragment into a caller-side retry loop. Research found the cap is innocent — live `BRAIN_MAX_TOKENS=943718` already sits at the `meta/muse-spark-1.3-contributor` ceiling — while `BRAIN_REASONING_EFFORT=xhigh` burns ~97% of the output budget on reasoning (measured `reasoning_tokens=14683 visible_tokens=341`), starving the visible XML at ANY cap. Following the industry playbook (structured output must be re-issued whole with more headroom, never stitched), the bridge now discards the fragment and re-issues the turn ONCE server-side with one-notch-lower reasoning effort (`max→xhigh→high→medium→low` via `_step_down_effort`); a second truncation returns terminal `TRUNCATION_UNRECOVERABLE` (caller must not retry as-is) instead of looping. Task 259 empty-output terminal, `EMPTY_OUTPUT_RETRY`, the semantic gate, and the 5xx/429 retry policy are untouched. Open decisions for the Manager: lower live effort from `xhigh`, keep the cap, deploy = copy `server.py` to the install + `systemctl --user restart mcp-brain`.
+
 - **Brain context-sufficiency pack (Task 285):** the Brain planned against a five-file documentation bundle only, with no repository structure, so it either guessed or burned a discovery round just to aim its context request. `mcp-brain-bridge/server.py` now auto-appends the newest generated `.gitignore`-aware tree report (`context-reports/tree_report_*.md`, written by the Hands via `custom_context.create_tree_report`) to that bundle under a labeled section, bounded by a new `_STRUCTURAL_FILE_CAP` (40000) and the shared `_BUNDLE_TOTAL_CAP` with honest `[truncated]`/`[skipped: bundle total cap]` markers. The section appears only when a report exists, so every workspace and test without one is byte-unchanged. New pure helpers `_latest_report_path` (newest by mtime, then name; accepts a `Path` or a `str` root) and `_build_structural_pack` (never raises) do the work, and `_build_context_bundle` appends the pack last so the stable doc files keep their prefix positions. Hardened after the QA hotfix round: a report that resolves outside the workspace root (symlink escape) is skipped rather than read, a zero-byte/whitespace report counts as no grounding, the read is capped at `_STRUCTURAL_FILE_CAP` chars so an oversized report is never slurped whole, and triple backticks are neutralized with an invisible break so report fences cannot close a surrounding fence. A second pure helper, `context_sufficiency_gaps(stage, user_prompt, bundle_text, bundle_included)`, plus a `plan`-stage-only stderr diagnostic makes a blind plan observable instead of silent — non-blocking by design (no `status`/`xml_blocks` change), so no caller behavior shifts. The diagnostic reads the FINAL rendered bundle and the combined prompt including any pinned fed-context block, and it suppresses the structural demand when the caller opted out of the bundle — closing two false-positive paths found in QA. A second QA finding (round 2) was also fixed: a pack dropped for the total cap now appends `[structural pack skipped: bundle total cap]` with NO grounding marker, so a skipped pack correctly counts as absent instead of falsely reading as grounded. 21 new regression tests cover pack selection, truncation, bundle integration, string-root normalization, symlink-escape skip, empty-report handling, fence escaping, the skip-counts-as-absent case, the pure gap checker, and the stderr wiring. Bridge suite: **272 passed** (251 pre-existing + 21 new).
 
 - **Adopted opencode-todolist plugin (Task 290):** OpenCode V2 removed the built-in `todowrite`/`todoread` session todo tools that powered the V1 sidebar, so the platform now runs `opencode-todolist` alongside `smart-compact`. Global install via `opencode plugin add opencode-todolist` (`plugins` now carries both entries) plus the TUI sidebar strip via `plugins` in `~/.config/opencode/cli.json`. HQ docs synced in every place plugins are listed: `README.md` (one plugin -> two plugins), `LLM.txt` (Step 7 JSON + description, Step 7.7 install + `cli.json` strip + restart smoke test, stale no-plugins checklist corrected). Restart OpenCode to load it, then smoke-test `todowrite`/`todoread` and the sidebar strip.
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 1e0948b..74b89db 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -3205,6 +3205,11 @@ def brain_turn(
         Questions for the admin travel inside ``output`` — relay them to
         the Manager and feed the answer back as the next ``user_prompt``
         (with the same ``task_id`` so history continues).
+        Recovery (Task 291): a partial truncation (non-empty model text,
+        status=incomplete/reason=max_output_tokens, no usable XML) is
+        re-issued ONCE server-side with stepped-down reasoning effort;
+        if that also truncates, ``output`` carries
+        TRUNCATION_UNRECOVERABLE and the caller must not retry as-is.
     """
     # Request preflight FIRST (GitHub issue 18): local validation before
     # any load, attach, import, or model call. An explicit project_root
@@ -3619,70 +3624,142 @@ def brain_turn(
         _maybe_warn_reasoning_budget(
             body["reasoning"]["effort"], body["max_output_tokens"]
         )
-    _note_checkpoint(
-        "transport_started",
-        task_id=task_id,
-        session_id=session_id,
-        project_root=project_root,
+    _total_attempts = 0
+    _recovery_used = False
+    _recovery_effort: Optional[str] = None
+    _reasoning_cfg = body.get("reasoning")
+    _first_effort: Optional[str] = (
+        _reasoning_cfg.get("effort") if isinstance(_reasoning_cfg, dict) else None
     )
-    resp, attempts = _send_with_learning(
-        _make_client,
-        _responses_url(),
-        body,
-        task_key=history_key,
-        task_id=task_id,
-        session_id=session_id,
-        project_root=project_root,
-    )
-    resp_data = _resp_json(resp)
-    output = parse_responses_text(resp_data)
-    _note_checkpoint(
-        "response_parsed",
-        task_id=task_id,
-        session_id=session_id,
-        project_root=project_root,
-    )
-    xml_blocks = extract_xml_blocks(output)
-    if xml_blocks:
-        # Semantic gate (Task 245): syntactically valid but contract-
-        # incomplete XML must triage as REPORT with explicit reasons —
-        # the Hands executes only whole contracts, never fragments.
-        sem_problems = validate_hands_xml_blocks(xml_blocks)
-        if sem_problems:
-            print(
-                "brain-bridge: xml failed semantic validation "
-                f"({len(sem_problems)} problems)",
-                file=sys.stderr,
-            )
-            output = (
-                "[xml-semantic-reject]\n"
-                + "\n".join(f"- {p}" for p in sem_problems)
-                + "\n[/xml-semantic-reject]\n"
-                + output
-            )
-            xml_blocks = []
-    diag = parse_responses_diagnostics(resp_data)
-    _log_provider_diagnostics(diag)
-    if not xml_blocks and not output.strip():
-        # Empty-output triage (Task 259): classify the provider diagnosis
-        # BEFORE falling back to the flake hint. Order is load-bearing:
-        # top-level error -> refusal -> output-budget exhaustion -> flake.
-        state = _task_state_note(history_key, project_root)
-        if diag["error"]:
-            output = _provider_error_hint(diag["error"])
-        elif diag["refusal"]:
-            output = _provider_refusal_hint(diag["refusal"])
-        elif (
-            diag["status"] == "incomplete"
+    # Transport loop (Task 291): at most TWO provider calls. Pass 0 is the
+    # normal turn. When pass 0 returns a PARTIAL truncation (non-empty
+    # output, status=incomplete/reason=max_output_tokens, no usable XML),
+    # the fragment is discarded and pass 1 re-issues the whole turn once
+    # server-side with stepped-down reasoning effort. Structured output
+    # must never stitch a fragment — the whole call is retried with more
+    # visible-answer headroom instead.
+    for _transport_pass in (0, 1):
+        _note_checkpoint(
+            "transport_started",
+            task_id=task_id,
+            session_id=session_id,
+            project_root=project_root,
+        )
+        resp, attempts = _send_with_learning(
+            _make_client,
+            _responses_url(),
+            body,
+            task_key=history_key,
+            task_id=task_id,
+            session_id=session_id,
+            project_root=project_root,
+        )
+        _total_attempts += attempts
+        resp_data = _resp_json(resp)
+        output = parse_responses_text(resp_data)
+        # Eligibility is judged on the RAW model text: the triage below
+        # rewrites blank output into hint text, and a rewritten hint must
+        # never qualify as a "partial" truncation (Task 259 stays terminal).
+        _raw_text_present = bool(output.strip())
+        _note_checkpoint(
+            "response_parsed",
+            task_id=task_id,
+            session_id=session_id,
+            project_root=project_root,
+        )
+        xml_blocks = extract_xml_blocks(output)
+        if xml_blocks:
+            # Semantic gate (Task 245): syntactically valid but contract-
+            # incomplete XML must triage as REPORT with explicit reasons —
+            # the Hands executes only whole contracts, never fragments.
+            sem_problems = validate_hands_xml_blocks(xml_blocks)
+            if sem_problems:
+                print(
+                    "brain-bridge: xml failed semantic validation "
+                    f"({len(sem_problems)} problems)",
+                    file=sys.stderr,
+                )
+                output = (
+                    "[xml-semantic-reject]\n"
+                    + "\n".join(f"- {p}" for p in sem_problems)
+                    + "\n[/xml-semantic-reject]\n"
+                    + output
+                )
+                xml_blocks = []
+        diag = parse_responses_diagnostics(resp_data)
+        _log_provider_diagnostics(diag)
+        if not xml_blocks and not output.strip():
+            # Empty-output triage (Task 259): classify the provider diagnosis
+            # BEFORE falling back to the flake hint. Order is load-bearing:
+            # top-level error -> refusal -> output-budget exhaustion -> flake.
+            state = _task_state_note(history_key, project_root)
+            if diag["error"]:
+                output = _provider_error_hint(diag["error"])
+            elif diag["refusal"]:
+                output = _provider_refusal_hint(diag["refusal"])
+            elif (
+                diag["status"] == "incomplete"
+                and diag["incomplete_reason"] == "max_output_tokens"
+            ):
+                output = _output_budget_hint(diag, task_id, state)
+            else:
+                # Transport/model flake (Task 232): never return a silent
+                # blank REPORT. Substitute the retry hint; status stays
+                # REPORT so old callers keep working. The transcript below
+                # records the hint, not a verdict.
+                output = _empty_output_hint(task_id, state)
+        if (
+            _transport_pass == 0
+            and _raw_text_present
+            and not xml_blocks
+            and diag["status"] == "incomplete"
             and diag["incomplete_reason"] == "max_output_tokens"
+            and isinstance(body.get("reasoning"), dict)
         ):
-            output = _output_budget_hint(diag, task_id, state)
-        else:
-            # Transport/model flake (Task 232): never return a silent
-            # blank REPORT. Substitute the retry hint; status stays
-            # REPORT so old callers keep working. The transcript below
-            # records the hint, not a verdict.
-            output = _empty_output_hint(task_id, state)
+            _current_effort = body["reasoning"].get("effort")
+            _next_effort = _step_down_effort(_current_effort)
+            _current_norm = (
+                _current_effort.strip().lower()
+                if isinstance(_current_effort, str) and _current_effort.strip()
+                else _current_effort
+            )
+            # Case-insensitive floor guard (Task 291 hotfix): a normalized
+            # equal means the floor is reached — re-issuing would bill a
+            # full turn for an identical shape.
+            if _next_effort != _current_norm:
+                _recovery_effort = _next_effort
+                body["reasoning"]["effort"] = _next_effort
+                _maybe_warn_reasoning_budget(_next_effort, body["max_output_tokens"])
+                print(
+                    "brain-bridge: partial truncation "
+                    "(status=incomplete, reason=max_output_tokens, no "
+                    "usable XML); discarding fragment and re-issuing once "
+                    "server-side with reasoning effort "
+                    f"{_next_effort!r} (was {_first_effort!r})",
+                    file=sys.stderr,
+                )
+                _recovery_used = True
+                continue
+        break
+    if (
+        not xml_blocks
+        and _raw_text_present
+        and diag["status"] == "incomplete"
+        and diag["incomplete_reason"] == "max_output_tokens"
+        and TRUNCATION_UNRECOVERABLE not in output
+    ):
+        # Terminal for ANY unrecovered partial truncation (Task 291
+        # hotfix): floor and temperature-mode first passes never recover,
+        # so gating on _recovery_used alone would return a silent
+        # fragment. Empty-output keeps _raw_text_present false, so the
+        # Task 259 budget/flake hints stay terminal as before; usable
+        # XML keeps xml_blocks non-empty, so complete-XML never converts.
+        # Only the transcript below records this.
+        _exhaust_state = _task_state_note(history_key, project_root)
+        output = _truncation_exhausted_hint(
+            diag, task_id, _exhaust_state, _first_effort, _recovery_effort
+        )
+        xml_blocks = []
     fence_drops = list(_last_fence_drops)
     if history_key:
         prompt_hash = hashlib.sha256(effective_prompt.encode("utf-8")).hexdigest()
@@ -3727,7 +3804,7 @@ def brain_turn(
         "attachment_chars_used": budget_info["attachment_chars_used"],
         "attachment_chars_remaining": budget_info["attachment_chars_remaining"],
         "budget_chars": budget_chars,
-        "retry_count": attempts,
+        "retry_count": _total_attempts,
         "prompt_cache_split": cache_split,
     }
     debug: dict[str, Any] = {"provider": diag}
@@ -3999,6 +4076,73 @@ def _output_budget_hint(
     )
 
 
+#: Machine token: partial truncation still unrecovered after the single
+#: server-side re-issue (Task 291). Terminal for the turn: the caller
+#: MUST NOT retry as-is — a same-shape retry re-bills the full input +
+#: reasoning budget and fails identically. Remediate via config (lower
+#: effort / smaller prompt), then re-run. NEVER rename without a task:
+#: callers and regression tests match this exact string.
+TRUNCATION_UNRECOVERABLE = "TRUNCATION_UNRECOVERABLE"
+
+#: One-notch reasoning-effort step-down for truncation recovery (Task
+#: 291). Lower effort frees visible-answer share inside the same
+#: ``max_output_tokens`` cap — the only headroom source once the cap
+#: already sits at the model ceiling. Unknown/non-string values fail
+#: safe to ``medium``; ``low`` is the floor (a second step down from
+#: ``low`` would change nothing, so the caller treats equality as
+#: no-recovery).
+_EFFORT_STEPDOWN = {
+    "max": "xhigh",
+    "xhigh": "high",
+    "high": "medium",
+    "medium": "low",
+    "low": "low",
+}
+
+
+def _step_down_effort(effort: object) -> str:
+    """Return one notch below ``effort`` (pure, offline)."""
+    if isinstance(effort, str) and effort.strip():
+        key = effort.strip().lower()
+        if key in _EFFORT_STEPDOWN:
+            return _EFFORT_STEPDOWN[key]
+    return "medium"
+
+
+def _truncation_exhausted_hint(
+    diag: dict,
+    task_id: Optional[str] = None,
+    state: Optional[str] = None,
+    first_effort: Optional[str] = None,
+    recovery_effort: Optional[str] = None,
+) -> str:
+    """Terminal hint after recovery also truncated (Task 291).
+
+    Pure function (no I/O) so tests assert the contract directly. The
+    bridge already spent its one bounded re-issue — the caller must not
+    spend more turns looping on this shape.
+    """
+    where = f" for task {task_id}" if task_id else ""
+    note = f" Current state: {state}." if state else ""
+    usage = diag.get("usage") or {}
+    return (
+        f"{TRUNCATION_UNRECOVERABLE}: the turn truncated twice{where} "
+        "(status=incomplete, reason=max_output_tokens, no usable XML even "
+        "after one server-side re-issue with stepped-down reasoning effort). "
+        "This is NOT a transport flake: do NOT retry this turn as-is and do "
+        "NOT count it as a rejection — the same shape would fail identically "
+        "while re-billing the full input + reasoning budget. Remediate by "
+        "lowering BRAIN_REASONING_EFFORT (e.g. to medium or low) or shrinking "
+        "the prompt (include_bundle=false, shorter instruction), then re-run "
+        "the turn with full context. "
+        f"First effort={first_effort} recovery effort={recovery_effort}. "
+        f"Usage: input={usage.get('input_tokens')} "
+        f"output={usage.get('output_tokens')} "
+        f"reasoning={usage.get('reasoning_tokens')} "
+        f"total={usage.get('total_tokens')}." + note
+    )
+
+
 def _maybe_warn_reasoning_budget(effort: str, max_tokens: int) -> None:
     """Warn (non-breaking) when high effort runs with a small cap (C6).
 
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index 28f7d78..35527f8 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -1774,6 +1774,223 @@ def test_brain_turn_semantic_reject_reports(tmp_path, monkeypatch):
     assert result["xml_blocks"] == []
 
 
+# --- Task 291: partial-truncation server-side recovery ---
+
+import copy as _copy
+
+
+def _incomplete_payload(text):
+    payload = _ok_payload(text)
+    payload["status"] = "incomplete"
+    payload["incomplete_details"] = {"reason": "max_output_tokens"}
+    payload["usage"] = {
+        "input_tokens": 40000,
+        "output_tokens": 900000,
+        "output_tokens_details": {"reasoning_tokens": 895000},
+        "total_tokens": 940000,
+    }
+    return payload
+
+
+class _SeqClient(_FakeClient):
+    """Capture EVERY request body in order (holder["bodies"])."""
+
+    def __init__(self, script, holder):
+        super().__init__(script)
+        # Share (don't copy) the script: sequential turns in one test
+        # consume it in order. (_FakeClient copies, which would replay
+        # item 0 for every fresh client.)
+        self._script = script
+        self._holder = holder
+
+    def post(self, url, json=None, headers=None, **kwargs):
+        # Deep-copy: brain_turn mutates the live body dict on recovery
+        # (effort step-down), so a reference would rewrite history.
+        self._holder.setdefault("bodies", []).append(_copy.deepcopy(json))
+        return super().post(url, json=json, headers=headers, **kwargs)
+
+
+def _mk_seq_client(monkeypatch, script, holder):
+    stub = _types.ModuleType("httpx")
+    stub.Client = lambda *a, **k: _SeqClient(script, holder)
+    stub.TimeoutException = type("TimeoutException", (Exception,), {})
+    stub.TransportError = type("TransportError", (Exception,), {})
+
+    class _Timeout:
+        def __init__(self, *a, **k):
+            self.args, self.kwargs = a, k
+
+    stub.Timeout = _Timeout
+    monkeypatch.setitem(sys.modules, "httpx", stub)
+    return stub
+
+
+_TRUNCATED_IMPLEMENT = (
+    "<hands_implementation_task>\n<context_phase>partial plan text, cut off"
+)
+
+_VALID_REPORT = "<failure_report>recovered and complete</failure_report>"
+
+
+def _run_recovery_turn(monkeypatch, tmp_path, script, holder, effort="xhigh"):
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _mk_sys_prompt(tmp_path, monkeypatch)
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
+    monkeypatch.delenv("BRAIN_TEMPERATURE", raising=False)
+    monkeypatch.setenv("BRAIN_REASONING_EFFORT", effort)
+    _mk_seq_client(monkeypatch, script, holder)
+    call = bridge.brain_turn
+    target = call.fn if hasattr(call, "fn") else call
+    return target("q", include_bundle=False)
+
+
+def test_step_down_effort_map():
+    assert bridge._step_down_effort("xhigh") == "high"
+    assert bridge._step_down_effort("high") == "medium"
+    assert bridge._step_down_effort("medium") == "low"
+    assert bridge._step_down_effort("max") == "xhigh"
+    assert bridge._step_down_effort("XHIGH") == "high"
+    assert bridge._step_down_effort("low") == "low"
+    assert bridge._step_down_effort("turbo") == "medium"
+    assert bridge._step_down_effort("") == "medium"
+    assert bridge._step_down_effort(None) == "medium"
+
+
+def test_truncation_exhausted_hint_is_terminal():
+    hint = bridge._truncation_exhausted_hint(
+        {
+            "usage": {
+                "input_tokens": 1,
+                "output_tokens": 2,
+                "reasoning_tokens": 3,
+                "total_tokens": 4,
+            }
+        },
+        "291",
+        "tasks/in-progress/291-x.md | status=open | diff=ab12cd34",
+        "xhigh",
+        "high",
+    )
+    assert bridge.TRUNCATION_UNRECOVERABLE in hint
+    assert "do NOT retry" in hint
+    assert "BRAIN_REASONING_EFFORT" in hint
+
+
+def test_brain_turn_recovers_partial_truncation_once(tmp_path, monkeypatch):
+    holder = {}
+    script = [
+        _FakeResp(200, "cut", _incomplete_payload(_TRUNCATED_IMPLEMENT)),
+        _FakeResp(200, "whole", _ok_payload(_VALID_REPORT)),
+    ]
+    result = _run_recovery_turn(monkeypatch, tmp_path, script, holder)
+    assert result["status"] == "XML_EXTRACTED"
+    assert result["xml_blocks"] == [_VALID_REPORT]
+    assert "partial plan text" not in result["output"]
+    assert len(holder["bodies"]) == 2
+    assert holder["bodies"][0]["reasoning"]["effort"] == "xhigh"
+    assert holder["bodies"][1]["reasoning"]["effort"] == "high"
+    assert "[xml-semantic-reject]" not in result["output"]
+
+
+def test_brain_turn_truncation_exhausted_is_terminal(tmp_path, monkeypatch):
+    holder = {}
+    script = [
+        _FakeResp(200, "cut1", _incomplete_payload(_TRUNCATED_IMPLEMENT)),
+        _FakeResp(200, "cut2", _incomplete_payload("more partial prose")),
+    ]
+    result = _run_recovery_turn(monkeypatch, tmp_path, script, holder)
+    assert result["status"] == "REPORT"
+    assert result["xml_blocks"] == []
+    assert bridge.TRUNCATION_UNRECOVERABLE in result["output"]
+    assert bridge.EMPTY_OUTPUT_RETRY not in result["output"]
+    assert "more partial prose" not in result["output"]
+    # Bounded: exactly one recovery call, never a third.
+    assert len(holder["bodies"]) == 2
+
+
+def test_brain_turn_no_recovery_when_complete(tmp_path, monkeypatch):
+    holder = {}
+    script = [_FakeResp(200, "whole", _ok_payload(_VALID_REPORT))]
+    result = _run_recovery_turn(monkeypatch, tmp_path, script, holder)
+    assert result["status"] == "XML_EXTRACTED"
+    assert len(holder["bodies"]) == 1
+
+
+def test_brain_turn_no_recovery_at_effort_floor(tmp_path, monkeypatch):
+    holder = {}
+    script = [
+        _FakeResp(200, "cut", _incomplete_payload(_TRUNCATED_IMPLEMENT)),
+    ]
+    result = _run_recovery_turn(monkeypatch, tmp_path, script, holder, effort="low")
+    assert result["status"] == "REPORT"
+    assert bridge.TRUNCATION_UNRECOVERABLE in result["output"]
+    assert "partial plan text" not in result["output"]
+    assert len(holder["bodies"]) == 1
+
+
+def test_brain_turn_empty_truncation_stays_budget_terminal(tmp_path, monkeypatch):
+    holder = {}
+    script = [_FakeResp(200, "blank", _incomplete_payload(""))]
+    result = _run_recovery_turn(monkeypatch, tmp_path, script, holder)
+    assert result["status"] == "REPORT"
+    assert bridge.OUTPUT_BUDGET_EXHAUSTED in result["output"]
+    assert bridge.TRUNCATION_UNRECOVERABLE not in result["output"]
+    assert len(holder["bodies"]) == 1
+
+
+def test_brain_turn_temperature_truncation_is_terminal(tmp_path, monkeypatch):
+    holder = {}
+    script = [
+        _FakeResp(200, "cut", _incomplete_payload("temperature prose, cut")),
+    ]
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    _mk_sys_prompt(tmp_path, monkeypatch)
+    monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
+    monkeypatch.setenv("BRAIN_TEMPERATURE", "0.7")
+    monkeypatch.setenv("BRAIN_REASONING_EFFORT", "xhigh")
+    _mk_seq_client(monkeypatch, script, holder)
+    call = bridge.brain_turn
+    target = call.fn if hasattr(call, "fn") else call
+    result = target("q", include_bundle=False)
+    assert "reasoning" not in holder["bodies"][0]
+    assert result["status"] == "REPORT"
+    assert bridge.TRUNCATION_UNRECOVERABLE in result["output"]
+    assert len(holder["bodies"]) == 1
+
+
+def test_brain_turn_complete_xml_with_incomplete_status_no_recovery(
+    tmp_path, monkeypatch
+):
+    holder = {}
+    script = [_FakeResp(200, "whole", _incomplete_payload(_VALID_REPORT))]
+    result = _run_recovery_turn(monkeypatch, tmp_path, script, holder)
+    assert result["status"] == "XML_EXTRACTED"
+    assert result["xml_blocks"] == [_VALID_REPORT]
+    assert len(holder["bodies"]) == 1
+
+
+def test_brain_turn_uppercase_low_floor_no_second_call(tmp_path, monkeypatch):
+    holder = {}
+    script = [
+        _FakeResp(200, "cut", _incomplete_payload(_TRUNCATED_IMPLEMENT)),
+    ]
+    result = _run_recovery_turn(monkeypatch, tmp_path, script, holder, effort="LOW")
+    assert result["status"] == "REPORT"
+    assert bridge.TRUNCATION_UNRECOVERABLE in result["output"]
+    assert len(holder["bodies"]) == 1
+
+
+def test_brain_turn_prose_only_floor_truncation_is_terminal(tmp_path, monkeypatch):
+    holder = {}
+    script = [
+        _FakeResp(200, "cut", _incomplete_payload("plain prose, cut mid-way")),
+    ]
+    result = _run_recovery_turn(monkeypatch, tmp_path, script, holder, effort="low")
+    assert result["status"] == "REPORT"
+    assert bridge.TRUNCATION_UNRECOVERABLE in result["output"]
+    assert len(holder["bodies"]) == 1
+
+
 # --- Task 215: reviewer hotfix XML must extract (bare + xml-fenced) ---
```
<!-- END_GIT_DIFF -->
