# Task 291: Brain truncated-XML server-side recovery

**File:** `tasks/completed/291-brain-truncated-xml-recovery.md`
**Source:** manager
**Type:** bugfix
**Status:** closed

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

**Closure move:** `git mv tasks/qa/291-brain-truncated-xml-recovery.md tasks/completed/291-brain-truncated-xml-recovery.md`, exit 0. `git status --porcelain` shows only the four expected paths (CHANGELOG.md, mcp-brain-bridge/server.py, tests/test_brain_bridge.py modified; task file moved). Manager accept quote 'Approved for closure' recorded 2026-10-03.

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

**Hotfix applied (same day, file stays in qa):** case-insensitive floor guard via normalized compare; terminal broadened to ANY unrecovered partial truncation (`not xml_blocks and _raw_text_present and incomplete/max_output_tokens and token not already in output`) — empty-output keeps Task 259 hints (raw empty), usable XML never converts. Floor/temperature/empty/complete-XML/uppercase-LOW/prose-floor tests added (5 new); fragment-absence asserted on recovery + exhausted paths. Full file: 283 passed. CHANGELOG untouched per hotfix scope.

**QA round 2 verdict: QA_PASSED (2026-10-03, autopilot re-QA).** F1 floor/temperature terminal, F2 uppercase LOW single-call, F3 contracts intact, F4 fragment-free recovery, F5 bounded. Notes (non-blocking): `_recovery_used` write-only, CHANGELOG wording centers second-truncation.

**Closure (2026-10-03):** QA_PASSED (round 2) + Code Reviewer APPROVED (PO_REVIEW_PENDING) + Manager accept quote 'Approved for closure'. Lane moved qa → completed, status closed.

**Autopilot locked (2026-10-03, Manager order "Lock auto pilot for task"):** full saga runs inside my own turns — re-QA, fix loop, review, stage, qa — stopping only for hard blockers and the closure gate (explicit "Approved for closure"/"Close task" required; NEVER auto-commit, NEVER auto-close).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `8438cca6b8b56030bd5f45172f08bf4493543eab`
<!-- END_GIT_DIFF -->
