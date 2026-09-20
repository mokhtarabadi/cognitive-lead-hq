# Task 261: Enable the risk-aware Brain model routing baseline

**File:** `tasks/completed/261-enable-risk-aware-brain-model-routing.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Turn on the existing risk-aware model routing in the Brain bridge as a working baseline: hard turns (plan, review) run on the strong model, light turns (implement, QA) run on a cheaper model, the flag is enabled with concrete per-tier models, and the selected tier is derived deterministically instead of relying on a caller that never passes one.

## Manager's Notes

Verbatim order: "I like d1 too / Task it / Enable auto pilot baseline for it". D1 is the decision from the model-suitability review: keep the current models and enable risk-aware routing rather than switch models. Run this task through the standard autopilot cycle (Brain plan, implement, QA, Code Reviewer) and report the verdicts.

## Local TODOs

- [x] Initial codebase exploration (routing symbols already mapped)
- [x] Brain plan: settle the stage-to-tier mapping and the per-tier model values
- [x] Implement the tier selection and the config baseline
- [x] Update `docs/brain-bridge.md` (Routing section plus the stale defaults table) and `.env.example`
- [x] Verify with the RTK-prefixed suite and record evidence
- [ ] Stage the diff, run the QA-review cycle, and close

## Acceptance Criteria

- [x] With routing enabled, a hard stage (`plan`, `review`) selects the high model and a light stage (`implement`, `qa`, `closure`) selects the low model; a missing stage falls back to `BRAIN_MODEL`, while an unknown stage is rejected by the request preflight (allowed values: `plan`, `implement`, `qa`, `review`, `closure`).
- [x] An explicit `risk_tier` passed by the caller still wins over the stage-derived tier.
- [x] Routing stays fully backward compatible when the flag is off: one model for every turn, no behavior change.
- [x] Each context-ledger row records the selected model and the effective tier for the turn.
- [x] `docs/brain-bridge.md` and `.env.example` describe the enabled baseline, the stage mapping, and the current effort and token defaults.
- [x] Tests cover the stage mapping, the explicit-override precedence, and the routing-off state.
- [x] The updated `mcp-brain-bridge/server.py` is synced to the global install.

## Verification Evidence

- **Test command:** rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
- **Expected result:** all tests pass, exit code 0
- **Actual result:** 632 passed, 10 warnings in 4.63s
- **Exit code:** 0

> Verification runner rule: the command above is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task.

## Risk & Rollback

- **Risk:** a wrong tier mapping sends an easy turn to the expensive model (cost) or a hard turn to a weaker model (quality); a per-tier model id could be mistyped and fail provider-side.
- **Rollback plan:** set `BRAIN_RISK_ROUTING_ENABLED=false` in both `.env` files (instant, no code change) or `git checkout -- mcp-brain-bridge/server.py` and re-run the suite.

---

## Execution Log & Reasoning

### Authorization

Autopilot is locked for this task on the Manager's words: "I like d1 too / Task it / Enable auto pilot baseline for it". The stored standing order `manager/full_automatic_mode` is the authorization basis (zero clarification halts, consult the Brain personas, RTK-first verification, reviewer technical approval plus `PO_REVIEW_PENDING` counts as closure approval). D1 came from the model-suitability review: keep the current models and turn routing on rather than switch models.

### Design decision (Brain plan, Software Architect seat)

Routing already existed (Task 246) but was inert: `BRAIN_RISK_ROUTING_ENABLED` was unset and no caller ever passed `risk_tier`, so every turn used `BRAIN_MODEL`. The approved plan supplies the missing input by deriving the tier from the `stage` the caller already sends.

| Stage | Tier | Model |
| --- | --- | --- |
| `plan`, `review` | `T2` | `openai/gpt-5.6-luna` |
| `implement`, `qa`, `closure` | `T0` | `deepseek/deepseek-v4.1-flash` |
| missing | none | `BRAIN_MODEL` |
| unknown | rejected by preflight | n/a |

An explicit `risk_tier` stays authoritative over the derived tier.

### Implementation

`mcp-brain-bridge/server.py`:

- `_routing_enabled()` now defaults ON: blank or unset means enabled, a falsy value (`0`/`false`/`no`/`off`) disables it, and `1`/`true`/`yes`/`on` keeps it on.
- `_get_model_low()` and `_get_model_high()` gained real code defaults (`deepseek/deepseek-v4.1-flash`, `openai/gpt-5.6-luna`) instead of `""`, so the baseline works with no `.env` entries; both stay overridable.
- Added `_ROUTED_LOW_TIERS`, `_ROUTED_HIGH_TIERS`, `_DEFAULT_STAGE_TIERS`, `_get_stage_tiers()` (merges `BRAIN_STAGE_TIERS` overrides, ignoring unusable pairs) and the pure `resolve_stage_tier()`.
- `brain_turn` computes `effective_tier = risk_tier or resolve_stage_tier(stage, _get_stage_tiers())` and feeds it to `resolve_routed_model`, whose 5-parameter signature is unchanged.
- The context-ledger row now records the effective tier rather than the raw argument.

The Manager added a condition to the plan ("هر کدوم توی .env قابل تغییر باشه / و دیفالت هم باشه"): every routing value must be `.env`-overridable and must also be the built-in default. That is why the model getters carry the chosen values as code defaults and why `BRAIN_STAGE_TIERS` exists as an override for the mapping.

### Documentation and configuration

`docs/brain-bridge.md` — the routing rows and the `## Routing` section were rewritten for the enabled baseline, the stage mapping, `risk_tier` precedence, the `BRAIN_STAGE_TIERS` override and the disabled path; two stale defaults were corrected (`BRAIN_REASONING_EFFORT` `xhigh` to `medium`, `BRAIN_MAX_TOKENS` `16384` to `32768`). `.env.example` documents the same knobs with the new values.

Both live `.env` files (project and `~/.config/opencode/.env`) carry `BRAIN_RISK_ROUTING_ENABLED=true`, `BRAIN_MODEL_LOW=deepseek/deepseek-v4.1-flash` and `BRAIN_MODEL_HIGH=openai/gpt-5.6-luna`; backups were written as `*.env.bak-20260919c`.

### Verification

Bridge suite: 210 passed, exit 0. Full suite (RTK-first): 630 passed, 10 warnings in 4.41s, exit 0 — four new routing tests, and no regression in the previously green 626. `mcp-brain-bridge/server.py` was copied to `~/.config/opencode/mcp-brain-bridge/server.py`, verified IN-SYNC and `py_compile` clean.

### Incidents

The first full bridge run failed one test because it passed `stage="nonsense"` and expected the router to fall through. Copied behaviour was wrong: `mcp-brain-bridge/preflight.py` rejects any stage outside `plan|implement|qa|review|closure` before routing runs, so the unknown-stage branch is unreachable through `brain_turn`. The test now asserts the pure resolver directly (`resolve_stage_tier("nonsense", ...) is None` and `resolve_stage_tier(None, ...) is None`), which is where that rule actually lives. No production change was needed.

### QA round 1 rejection and repair

QA rejected the first submission on one reproducible defect (V1): a blank `BRAIN_MODEL_LOW`/`BRAIN_MODEL_HIGH` silently selected the built-in routed model, while `docs/brain-bridge.md` promised that blank per-tier overrides fall back to `BRAIN_MODEL`. An operator clearing an override would have been routed to an unintended model.

Repair — a three-state contract in `mcp-brain-bridge/server.py`, chosen so the QA contract and the Manager's condition both hold (every value is `.env`-changeable *and* carries that value as its built-in default):

- key **unset** → the built-in default (`_MODEL_LOW_DEFAULT` = `deepseek/deepseek-v4.1-flash`, `_MODEL_HIGH_DEFAULT` = `openai/gpt-5.6-luna`), so the baseline works with no `.env` entry;
- key **set but blank** → `""`, which the unchanged pure resolver `resolve_routed_model()` maps back to `BRAIN_MODEL`;
- key **set with a value** → the stripped value.

Tests updated accordingly: `test_routing_env_overrides_stripped_and_blank` now asserts `""` for a set-but-blank key and the built-in default for a deleted key, and a new `test_ledger_carries_stage_derived_tier_and_model` proves the context-ledger row records both the selected model and the effective tier for a stage-derived tier (QA's missing-test item). The two `docs/brain-bridge.md` rows and the Routing paragraph now state the unset-versus-blank distinction explicitly. `resolve_routed_model()` itself is unchanged, so its signature lock test still passes.

Post-repair verification: `py_compile` clean; bridge suite green; full suite (RTK-first) 631 passed, 10 warnings in 4.65s, exit 0; `mcp-brain-bridge/server.py` re-copied to `~/.config/opencode/mcp-brain-bridge/server.py`, IN-SYNC and `py_compile` clean.

### QA round 2 rejection and repair

QA rejected a second time on contract wording, not on behaviour.

- **V1 / M1 / M2 (unknown-stage contract):** the docs, `.env.example` and this task's acceptance criteria claimed an unknown stage falls back to `BRAIN_MODEL`. That path is not reachable: `mcp-brain-bridge/preflight.py:22` allows only `plan`, `implement`, `qa`, `review`, `closure`, and `_check_stage` (lines 133-141) raises `PreflightError("bad stage: …")` before routing runs. The honest contract is now stated in all three places: a **missing** stage maps to no tier and falls back to `BRAIN_MODEL`, while an **unknown** stage is rejected by the request preflight. `resolve_stage_tier()` still returns `None` for an unknown stage as defence in depth, and the new end-to-end test `test_unknown_stage_is_rejected_by_preflight` proves the rejection travels through `brain_turn` itself.
- **V2 (stale count):** the `CHANGELOG.md` entry reported `630 passed` while this task recorded `631`. Both now read `632 passed`, the post-repair figure.

Repair evidence: `py_compile` clean; full suite RTK-first `632 passed, 10 warnings in 4.63s`, exit 0; `mcp-brain-bridge/server.py` re-synced to `~/.config/opencode/mcp-brain-bridge/server.py` (IN-SYNC, `py_compile` clean).

### QA round 3 rejection and repair

The third QA round rejected on the stale-count class again: `CHANGELOG.md` still read `Full suite: 631 passed`, while the verified suite — after the round-2 preflight-contract test was added — produced **632 passed**. Corrected to `632 passed`. No code, test, contract, or documentation-behaviour change was required; only the reported count. All other items were explicitly cleared by the QA round, including the stage mapping, explicit override precedence, routing-disabled behavior, ledger metadata, blank environment values, and the unknown-stage preflight rejection.

### Closure authorization

The Manager answered the closure question through the native `question` tool with the exact required phrase **"Approved for closure"**. The task was moved to `tasks/completed/`, its status set to `closed`, and the staged change set committed through `custom_context_commit_and_clean_task`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `58e70a490fa83daeedae9d3080d3faf31f8e015f`
<!-- END_GIT_DIFF -->
