# Task 246: Risk-aware model routing for the Brain bridge

**File:** `tasks/completed/246-brain-risk-aware-routing.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Mode:** autopilot-locked

## Goal

Add risk-aware model routing to the Brain bridge so cheap low-risk turns use a light model and high-risk turns keep the strong model, cutting token cost per the deep-research cost findings, behind config flags with zero behavior change by default.

## Manager's Notes

- Standing autopilot order 2026-09-17 (FA): work task-by-task on autopilot, consult Brain personas on every step, never work solo, consult stored manager decisions instead of asking questions, zero questions to the Manager.
- Standing closure rule 2026-09-17 (FA, verbatim): "من اگر کد ریویوئر تایید کنه، منم تایید می‌کنم" — a Code Reviewer technical approval counts as Manager approval for closure. (Note: `record_manager_decision` MCP errored 3x with `'str' object has no attribute 'get'` on well-formed objects, so the ruling is preserved here instead; retry the record on a later task.)
- Research grounding: `context-reports/llm-harness-research-20260917.md` (routing saves 40-70% of LLM spend; precision stack: domain RAG + router/cache first).
- Brain joint verdict (Senior Programmer + Software Architect, session 2026-09-17): implement A1 (routing) first; A2 prompt cache, A4 ranked retrieval, eval harness follow as later tasks. Defer fine-tune/quantize/NLI/LangGraph-migration.
- Discovery map (Subagent C, Task 245): no router exists — single model via `_get_brain_model` (`mcp-brain-bridge/server.py`); risk tiers T0/T1/T2 exist only as process policy in `docs/conventions.md`; retry is narrow, not risk-tiered. Extension point: `RISK_MODEL_MAP` + `_get_model_for_tier()` beside `_get_brain_model`, env `BRAIN_MODEL_LOW/HIGH`, tier wired from `docs/conventions.md` T0/T1/T2.

## Local TODOs

- [x] Discovery: map model getters, env contract, risk-tier policy, retry paths (delegate to subagents)
- [x] Planning: `brain_turn` planning round under this task id, Brain-approved plan, Seat Check
- [x] RED: failing tests for tier-to-model resolution + default-off behavior + env override
- [x] GREEN: minimal router implementation behind flags (default: current single-model behavior)
- [x] Docs: `.env.example` + `docs/brain-bridge.md` router contract (flag names, tier mapping, cost note)
- [x] Verify: full suite exit 0, `lint_task_file` passes, CHANGELOG Parse-Then-Append
- [x] Stage via `custom_context_stage_and_inject_diff`, move to `tasks/qa/`, re-stage

## Acceptance Criteria

- [x] Risk tier (T0/T1/T2 per `docs/conventions.md`) resolves to a model/effort selection through one pure function, unit-tested
- [x] Default configuration reproduces current behavior exactly (no flag set = today's model, effort, tokens)
- [x] Env overrides (`BRAIN_MODEL_LOW`, `BRAIN_MODEL_HIGH` or Brain-approved names) select models per tier
- [x] No secrets or task diffs flow into any cache/key computation
- [x] Full test suite passes with exit code 0; new tests cover tier mapping, default-off, and invalid-tier fallback

## Verification Evidence

- **Test command:** `uv run --with pytest --with "mcp[cli]==1.30.0" --with pathspec --with pyyaml pytest tests/ -q`
- **Expected result:** all tests pass, exit 0
- **Actual result:** 423 passed, 0 failed (8 new routing tests; pre-existing memory tests need pyyaml — proven env-only via ModuleNotFoundError, green with it)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** routing changes which model answers a turn; a wrong tier mapping could silently downgrade hard turns or leak cost. Cache/key confusion could mix task diffs into shared keys.
- **Rollback plan:** flags default off; revert the feature commit hash recorded in the Execution Log; behavior returns to single-model exactly.

---

## Execution Log & Reasoning

- Autopilot locked 2026-09-17 per Manager standing order (task-by-task improvement, Brain on every step, decisions consulted not asked, reviewer approval = closure approval).
- Consulted stored decisions before acting (consult-first): DEC-20260914-003 (standing full-autopilot, zero questions), DEC-20260913-003 (no-ferry rule — call `brain_turn` directly), DEC-20260913-001 (approval promised on pass), DEC-20260914-001 (consult ALL Brain personas, never solo — will use multi-seat planning), DEC-20260914-003/004 memory (close one-by-one via MCP commit path).
- Memory loaded: `autopilot_consult_all_personas`, `task_closure_protocol_one_by_one`; index re-read at session start.
- Discovery (3 parallel subagents): no router exists anywhere (single `_get_brain_model`, sole call-site `server.py:1823`); tiers T0/T1/T2 process-policy only (`docs/conventions.md:117-125`); env/docs/ledger/golden shapes mapped; open R1 (decision-model fallback doc contradiction — Brain says leave, out of scope).
- Brain plan verdict (Architect + Senior Programmer, same task id): `PLAN_READY_FOR_MANAGER_APPROVAL` — explicit `risk_tier` param on `brain_turn`, `BRAIN_RISK_ROUTING_ENABLED` default false, `BRAIN_MODEL_LOW/HIGH` blank-means-fallback, pure resolver (no env/network/prompt/diff/key inputs), bridge-only scope, additive ledger `model` + `risk_tier` fields, effort/tokens getters untouched.
- Assumption A1: plan-approval pause skipped under the standing zero-questions autopilot order (verbatim Manager FA: reviewer approval = his approval; "واقعاً دیگه نیاز نیست از من سؤال کنی"). Risk: plan proceeds without human edit round; mitigated by Brain QA + Code Reviewer gates before any closure.
- Implementation (GREEN): `server.py` — `_routing_enabled` (1/true/yes/on, default false), `_get_model_low/high` (strip, blank-means-fallback), `resolve_routed_model` pure (case-sensitive tiers, fail-safe default), `brain_turn(..., risk_tier=None)` wired at model resolution, ledger gains `model` + `risk_tier` (None-safe); effort/tokens getters untouched; decision server untouched per Brain D3. Tests: 8 new (RED 6 failed on missing attr + 2 deselected-shape, GREEN all pass). Docs: `.env.example` routing block, `docs/brain-bridge.md` env rows + Routing section, CHANGELOG Added entry (423 passed). Full suite (`mcp[cli]==1.30.0` pin — v2 removed FastMCP; pyyaml for pre-existing memory env gap): 423 passed, exit 0.
- Brain QA: `QA_PASSED` (no reproducible defects; 2 test-strengthening notes M1/M2 adopted: disabled-routing turn now passes explicit `risk_tier="T0"`; ledger test asserts exact key set + distinctive prompt/key absence from serialized row). Re-run after strengthening: 423 passed, exit 0. (Note: bare-digits task gate rejected a `232b` probe id mid-test — used `233`; gate works as designed.)
- Code Reviewer: technical APPROVED + `PO_REVIEW_PENDING`, zero issues against the plan ("The diff matches the approved bridge-only, default-off routing plan"), relay asks for "Approved for closure".
- Replay line (standing Manager order 2026-09-17, verbatim: "من اگر کد ریویوئر تایید کنه، منم تایید می‌کنم" — reviewer approval counts as Manager closure approval; zero-questions autopilot, no separate approval round): closing via sanctioned MCP path after the recorded technical approval. `record_manager_decision` retried 3x and errored (`'str' object has no attribute 'get'`), ruling preserved here instead.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `6cfe351adc57012060fdc4fbafe4e8d1f0970019`
<!-- END_GIT_DIFF -->
