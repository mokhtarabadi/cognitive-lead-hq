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
```diff
diff --git a/.env.example b/.env.example
index bf2d7fc..60814e8 100644
--- a/.env.example
+++ b/.env.example
@@ -49,10 +49,17 @@ BRAIN_API_KEY=sk-...
 # global literal breaks per-user resolution.
 #DECISION_REPO_PATH=$HOME/manager-decisions
 
-# Risk-aware routing (mcp-brain-bridge) — OFF by default. When enabled,
-# `brain_turn(..., risk_tier=...)` selects the model per tier
+# Risk-aware routing (mcp-brain-bridge) — ON by default. Hard stages use the
+# high model, light stages use the low one; an explicit `risk_tier` on
+# `brain_turn(..., risk_tier=...)` overrides the stage-derived tier
 # (T0 -> LOW, T1/T2 -> HIGH, missing/invalid -> BRAIN_MODEL).
-# Blank model = fall back to BRAIN_MODEL for that tier.
-#BRAIN_RISK_ROUTING_ENABLED=false
-#BRAIN_MODEL_LOW=
-#BRAIN_MODEL_HIGH=
\ No newline at end of file
+# Stage default: plan/review -> T2 (HIGH), implement/qa/closure -> T0 (LOW);
+# missing stage -> BRAIN_MODEL; an unknown stage is rejected by preflight.
+# Both model ids below are also the built-in code defaults.
+# Set the switch to a falsy value to disable routing (single-model behavior).
+#BRAIN_RISK_ROUTING_ENABLED=true
+#BRAIN_MODEL_LOW=deepseek/deepseek-v4.1-flash
+#BRAIN_MODEL_HIGH=openai/gpt-5.6-luna
+# Stage->tier overrides: comma-separated `stage:Tier` pairs merged onto the
+# built-in default (unusable pairs are ignored).
+#BRAIN_STAGE_TIERS=plan:T2,review:T2,implement:T0,qa:T0,closure:T0
\ No newline at end of file
diff --git a/CHANGELOG.md b/CHANGELOG.md
index d61f74e..41071bb 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Risk-aware Brain model routing enabled by default (Task 261):** `brain_turn` no longer sends every turn to one model. It now derives the model from the turn `stage`: the hard stages `plan` and `review` route to the high model `openai/gpt-5.6-luna`, while the lighter `implement`, `qa` and `closure` stages route to the low model `deepseek/deepseek-v4.1-flash`; a missing stage falls back to `BRAIN_MODEL`, while an unknown stage is rejected by the request preflight. An explicit `risk_tier` on the call still wins over the stage-derived tier. `mcp-brain-bridge/server.py` gains a pure `resolve_stage_tier()` resolver and a `_get_stage_tiers()` map, and the context-ledger row now records the effective tier. Every routing value is `.env`-overridable (`BRAIN_MODEL_LOW`, `BRAIN_MODEL_HIGH`, `BRAIN_STAGE_TIERS`) while carrying that same value as its built-in code default, so the baseline works with no `.env` entries at all; routing itself defaults ON and a falsy `BRAIN_RISK_ROUTING_ENABLED` disables it so every turn falls back to `BRAIN_MODEL`. `docs/brain-bridge.md` and `.env.example` were updated, including two previously stale defaults (`BRAIN_REASONING_EFFORT` now `medium`, `BRAIN_MAX_TOKENS` now `32768`). Full suite: **632 passed**.
+
 - **Brain-bridge reliability bundle META 257 (syncs GitHub issues 16, 17, 18, 19):** four stdlib-only modules plus prompt reconciliation. `mcp-brain-bridge/preflight.py` (Issue 18, P1): local request validation before transport — explicit `project_root` must hold `tasks/` (raise, never silent workspace-root fallback — the fallback WAS the Cando-828 double failure), omitted root resolves via explicit → `BRAIN_PROJECT_ROOT` → `BRAIN_WORKSPACE_ROOT` → cwd walk-up and raises naming the remedy on exhaustion; new `session_id`/`stage` (plan/implement/qa/review/closure)/`kanban_path`/`required_tools` params; exactly-one task_id/session_id binding for memory turns, neither means one-off. `mcp-brain-bridge/capability.py` (Issue 16, P3): three-status manifest (`AVAILABLE`/`UNAVAILABLE_REQUIRED`/`UNAVAILABLE_OPTIONAL`) grounded in `opencode.json` permissions — `question` resolves to `UNAVAILABLE_REQUIRED` (internal registry `KNOWN_UNAVAILABLE`: absent from permissions, zero repo definitions — the registry name is never emitted as a public manifest status); stage-implied requirements (qa→lint_task_file, closure→commit_and_clean, plan/review→brain_turn); blocked approval-sensitive work returns a non-verdict REPORT relay block with zero transport calls, and the `question`-tool handoff contradictions are reconciled in `agents/cognitive-executor.md`, `prompts/fragments/09-hands_protocols.md`, and `skill-templates/telegram-issue-sync/SKILL.md` (manifest check first, never silent skip; single approval rule; manual→relay+pause, autopilot→replay-or-halt). `mcp-brain-bridge/transport_learning.py` (Issue 17, P2): `unsupported_parameter` 400 classifier with protected keys (model/input never dropped), one corrected retry, saga-scoped correction memory keyed by task_id persisted as ledger events, repeat same-class failures escalate via marked `TransportEscalationError` — transport raises preserved, never verdicts. `mcp-brain-bridge/session_ledger.py` + decision/lint extensions (Issue 19, P4-P7): append-only `session_ledger.jsonl` with `start_session` (10 required fields) + 9 ordered checkpoints wired into `brain_turn`; `extract_session_decisions` accepts taskless `session_id`/non-numeric ids; pending→approved/rejected ledger candidates never touch the DEC store before approval; lint exempts ```source-evidence fenced blocks from markdown-basics (unclosed block is its own error, fence contents never satisfy structure) and a new `analysis` task Type accepts Report Evidence instead of test-command evidence. Shipped prompt rebuilt to **9.41.0**. 86 new tests (`test_brain_preflight`, `test_brain_capability`, `test_brain_transport_learning`, `test_session_lifecycle`) + 4 existing tests re-seamed to explicit `project_root`. Full suite: **596 passed**, zero regressions.
 - **RTK output-trimming structural wiring (Task 250):** RTK-first is now structural, not advisory. `prompts/fragments/09-hands_protocols.md` RULE 3b requires every test-suite verification to begin with `rtk test <underlying command>` and the exact prefixed command recorded in Verification Evidence (raw rerun only after failure, for diagnostics); `agents/cognitive-executor.md` gains a Verification Runner policy plus an RTK-prefixed evidence example; `skill-templates/task-generator/SKILL.md` template prescribes `rtk test [exact command]` with a runner rule; normative raw prescribers normalized (`docs/setup.md`, `docs/brain-bridge.md`, `docs/workflow-upgrade-v8.4.5.md`, upgrade-runbook memory); project memory holds one canonical RTK-first rule. Shipped prompt rebuilt to 9.40.0 (byte-identical double build). 3 new regression tests in `tests/test_prompt_sync.py` (executor default runner, evidence recording, template prescription) plus version-pin update. Full suite: **502 passed**.
 - **English-only reasoning plus input-validation enforcement (Task 252):** resolved the clarification-language contradiction — `prompts/fragments/05-user_input_processing.md` now runs the Input Validation Gate as step 0 (before topic-shift detection, renumbered 0.5), clarification halts output simple English, and the pipeline order validate-normalize-translate-enrich-prompt-refactor is explicit; `prompts/fragments/13-constraints.md` Cognitive Language Rule is authoritative (English always, quoted source material only); `docs/conventions.md`, `AGENTS.md`, and `agents/cognitive-executor.md` clarification halts all say simple English; executor Skill Matrix gains mandatory `prompt-refactor` for implementation-producing input. Shipped prompt rebuilt to 9.39.0 (deterministic, byte-identical double build). New `tests/test_input_validation_pipeline.py` (6 tests) plus 3 shipped-prompt gates in `tests/test_prompt_sync.py`. Full suite: **499 passed**.
diff --git a/docs/brain-bridge.md b/docs/brain-bridge.md
index 0776dea..cd73398 100644
--- a/docs/brain-bridge.md
+++ b/docs/brain-bridge.md
@@ -73,29 +73,39 @@ helper and is not a public tool.
 | `BRAIN_API_BASE`    | _(Manager-owned endpoint, e.g. local proxy URL)_     |
 | `BRAIN_API_KEY`     | _(Manager-owned, never committed)_                   |
 | `BRAIN_MODEL`       | `gpt-6-astra`                   |
-| `BRAIN_REASONING_EFFORT` | `xhigh`                                         |
-| `BRAIN_MAX_TOKENS`  | `16384`                                              |
+| `BRAIN_REASONING_EFFORT` | `medium`                                         |
+| `BRAIN_MAX_TOKENS`  | `32768`                                              |
 | `BRAIN_SYSTEM_PROMPT` | `~/.config/opencode/system-prompt.md`              |
 | `BRAIN_SESSIONS_ROOT` | `~/.config/opencode/brain-sessions`                |
 | `DECISION_MODEL`    | _(falls back to `BRAIN_MODEL` default)_              |
 | `DECISION_TEMPERATURE` | `1.0`                                             |
-| `BRAIN_RISK_ROUTING_ENABLED` | `false` (routing OFF = single model)      |
-| `BRAIN_MODEL_LOW`   | _(blank = `BRAIN_MODEL`; used for `T0` turns)_       |
-| `BRAIN_MODEL_HIGH`  | _(blank = `BRAIN_MODEL`; used for `T1`/`T2` turns)_  |
+| `BRAIN_RISK_ROUTING_ENABLED` | `true` (routing ON; set a falsy value to disable) |
+| `BRAIN_MODEL_LOW`   | `deepseek/deepseek-v4.1-flash` for `T0` turns; **unset** = built-in default, **blank** = `BRAIN_MODEL` |
+| `BRAIN_MODEL_HIGH`  | `openai/gpt-5.6-luna` for `T1`/`T2` turns; **unset** = built-in default, **blank** = `BRAIN_MODEL` |
+| `BRAIN_STAGE_TIERS` | `plan:T2,review:T2,implement:T0,qa:T0,closure:T0`    |
 
 ## Routing
 
-Risk-aware model routing is OFF by default: with no flags set, every
-turn uses `BRAIN_MODEL` (default `gpt-6-astra`), effort `xhigh`, and
-`16384` max tokens — exactly today's behavior. To enable, set
-`BRAIN_RISK_ROUTING_ENABLED=true` plus `BRAIN_MODEL_LOW` and/or
-`BRAIN_MODEL_HIGH`, then pass `risk_tier` (`T0`/`T1`/`T2` per
-`docs/conventions.md`) on `brain_turn`. `T0` routes to the low model,
-`T1`/`T2` to the high model; missing or invalid tiers fail safe to
-`BRAIN_MODEL`, as do blank per-tier overrides. Effort and token
-behavior never change under routing. Each context-ledger row records
-the selected `model` and the `risk_tier` (metadata only — never prompt
-text, diffs, or keys).
+Risk-aware model routing is ON by default. The effective tier comes from
+the turn `stage` unless an explicit `risk_tier` (`T0`/`T1`/`T2` per
+`docs/conventions.md`) is passed to `brain_turn`, which always wins.
+Stage defaults: `plan` and `review` → `T2` (high model), `implement`,
+`qa` and `closure` → `T0` (low model); a missing stage maps to no tier
+and falls back to `BRAIN_MODEL`, while an unknown stage is rejected by the
+request preflight (`plan`, `implement`, `qa`, `review`, `closure` are the
+allowed values). `T1` also routes to the high
+model. Override the mapping with `BRAIN_STAGE_TIERS` (comma-separated
+`stage:Tier` pairs merged onto the built-in default; unusable pairs are
+ignored). Set `BRAIN_RISK_ROUTING_ENABLED` to a falsy value to disable
+routing entirely — every turn then uses `BRAIN_MODEL`. Missing or invalid
+tiers fail safe to `BRAIN_MODEL`. For the per-tier models the unset and
+blank cases differ on purpose: leaving `BRAIN_MODEL_LOW`/`BRAIN_MODEL_HIGH`
+unset applies their built-in defaults, while setting a key to a blank value
+falls back to `BRAIN_MODEL`, so clearing an override never silently selects
+the built-in routed model. Effort
+and token behavior never change under routing. Each context-ledger row
+records the selected `model` and the effective `risk_tier` (metadata only
+— never prompt text, diffs, or keys).
 
 ## Prompt-cache split
 
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 44f2bb2..c16bcc6 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -1006,26 +1006,49 @@ def _get_brain_model() -> str:
 
 
 def _routing_enabled() -> bool:
-    """Risk-aware routing master switch; default OFF (Task 246).
+    """Risk-aware routing master switch; default ON (Task 261).
 
-    Accepts ``1/true/yes/on`` (case-insensitive); anything else —
-    including blank — keeps today's single-model behavior exactly."""
-    return os.environ.get(
-        "BRAIN_RISK_ROUTING_ENABLED", "").strip().lower() in (
-            "1", "true", "yes", "on")
+    Blank/unset means enabled, so the routing baseline works with no
+    ``.env`` entry at all. An explicit falsy value (``0/false/no/off``
+    or anything unrecognized) turns routing off and restores the
+    single-model behavior exactly; ``1/true/yes/on`` keeps it on."""
+    raw = os.environ.get("BRAIN_RISK_ROUTING_ENABLED", "").strip().lower()
+    if not raw:
+        return True
+    return raw in ("1", "true", "yes", "on")
+
+
+#: Built-in per-tier model defaults (Task 261). They apply only when the
+#: corresponding ``.env`` key is UNSET; an explicitly BLANK value falls
+#: back to ``BRAIN_MODEL`` instead (see ``_get_model_low``).
+_MODEL_LOW_DEFAULT = "deepseek/deepseek-v4.1-flash"
+_MODEL_HIGH_DEFAULT = "openai/gpt-5.6-luna"
 
 
 def _get_model_low() -> str:
-    """Override model for T0 turns; blank means fall back to the
-    current model (``BRAIN_MODEL``). Stripped, never defaulted here —
-    the pure resolver below owns the fallback."""
-    return os.environ.get("BRAIN_MODEL_LOW", "").strip()
+    """Model for light turns; override via ``BRAIN_MODEL_LOW``.
+
+    Three-state contract (Task 261): UNSET uses the built-in default so
+    the routing baseline works with no ``.env`` entry; set-but-BLANK
+    returns an empty string, which the pure resolver below maps back to
+    ``BRAIN_MODEL``. The distinction is deliberate — an operator who
+    clears the override gets the ``BRAIN_MODEL`` fallback, never a
+    silent switch to the built-in routed model."""
+    raw = os.environ.get("BRAIN_MODEL_LOW")
+    if raw is None:
+        return _MODEL_LOW_DEFAULT
+    return raw.strip()
 
 
 def _get_model_high() -> str:
-    """Override model for T1/T2 turns; blank means fall back to the
-    current model (``BRAIN_MODEL``). Stripped, never defaulted here."""
-    return os.environ.get("BRAIN_MODEL_HIGH", "").strip()
+    """Model for hard turns; override via ``BRAIN_MODEL_HIGH``.
+
+    Same three-state contract as ``_get_model_low``: UNSET uses the
+    built-in default, set-but-BLANK falls back to ``BRAIN_MODEL``."""
+    raw = os.environ.get("BRAIN_MODEL_HIGH")
+    if raw is None:
+        return _MODEL_HIGH_DEFAULT
+    return raw.strip()
 
 
 #: Tier sets for routing. Case-sensitive on purpose: a lowercase
@@ -1033,6 +1056,51 @@ def _get_model_high() -> str:
 _ROUTED_LOW_TIERS = frozenset({"T0"})
 _ROUTED_HIGH_TIERS = frozenset({"T1", "T2"})
 
+#: Default stage-to-tier map (Task 261): the hard turns get the strong
+#: model, the light turns the cheap one. Overridable per stage through
+#: ``BRAIN_STAGE_TIERS`` so no value is hardcoded beyond its default.
+_DEFAULT_STAGE_TIERS: dict[str, str] = {
+    "plan": "T2",
+    "review": "T2",
+    "implement": "T0",
+    "qa": "T0",
+    "closure": "T0",
+}
+
+
+def _get_stage_tiers() -> dict[str, str]:
+    """Stage-to-tier map; override entries via ``BRAIN_STAGE_TIERS``.
+
+    Format: ``stage:Tier`` pairs, comma-separated, e.g.
+    ``plan:T2,qa:T0``. Overrides merge onto the built-in default, and
+    an unusable pair (bad stage or unknown tier) is ignored rather
+    than failing a turn."""
+    mapping = dict(_DEFAULT_STAGE_TIERS)
+    raw = os.environ.get("BRAIN_STAGE_TIERS", "").strip()
+    if not raw:
+        return mapping
+    valid_tiers = _ROUTED_LOW_TIERS | _ROUTED_HIGH_TIERS
+    for pair in raw.split(","):
+        stage, _, tier = pair.partition(":")
+        stage = stage.strip().lower()
+        tier = tier.strip()
+        if stage and tier in valid_tiers:
+            mapping[stage] = tier
+    return mapping
+
+
+def resolve_stage_tier(stage: Optional[str],
+                       stage_tiers: dict[str, str]) -> Optional[str]:
+    """Pure stage-to-tier resolver (Task 261).
+
+    Takes values only — no environment reads. Returns ``None`` for a
+    missing or unknown stage, which the model resolver then treats as
+    "no tier" and falls back to ``BRAIN_MODEL``."""
+    key = (stage or "").strip().lower()
+    if not key:
+        return None
+    return stage_tiers.get(key)
+
 
 def resolve_routed_model(enabled: bool, risk_tier: Optional[str],
                          default_model: str, model_low: str,
@@ -2290,8 +2358,14 @@ def brain_turn(
         except Exception as exc:  # never fail a turn on attach problems
             print(f"brain-bridge: diff attach skipped ({exc})",
                   file=sys.stderr)
+    # Tier precedence: an explicit ``risk_tier`` wins; otherwise the
+    # tier is derived from the turn stage (Task 261). A missing or
+    # unknown stage leaves the tier empty, and the resolver returns
+    # ``BRAIN_MODEL`` for it.
+    effective_tier = (risk_tier or "").strip() or resolve_stage_tier(
+        stage, _get_stage_tiers())
     model = resolve_routed_model(
-        _routing_enabled(), risk_tier, _get_brain_model(),
+        _routing_enabled(), effective_tier, _get_brain_model(),
         _get_model_low(), _get_model_high())
     if history_key:
         # Sessions-root visibility: one debug line per turn so a
@@ -2347,7 +2421,7 @@ def brain_turn(
         history=history)
     _append_context_ledger(history_key, project_root, budget_chars,
                            truncated_count, model=model,
-                           risk_tier=risk_tier,
+                           risk_tier=effective_tier,
                            prompt_cache_split=cache_split)
     if budget_chars > _PROMPT_WARN_CHARS:
         print(
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index b8d7916..75a1543 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -2233,7 +2233,7 @@ def test_sibling_missing_still_resolves_per_project(tmp_path, monkeypatch):
 
 def _clean_routing_env(monkeypatch):
     for var in ("BRAIN_RISK_ROUTING_ENABLED", "BRAIN_MODEL_LOW",
-                "BRAIN_MODEL_HIGH", "BRAIN_MODEL"):
+                "BRAIN_MODEL_HIGH", "BRAIN_MODEL", "BRAIN_STAGE_TIERS"):
         monkeypatch.delenv(var, raising=False)
 
 
@@ -2271,18 +2271,29 @@ def test_routed_model_resolution_table(monkeypatch):
     assert r(True, "T1", "gpt-6-astra", "low-m", "  ") == "gpt-6-astra"
 
 
-def test_routing_disabled_by_default_preserves_behavior(tmp_path, monkeypatch):
+def test_routing_enabled_by_default_keeps_default_model(tmp_path, monkeypatch):
     _clean_routing_env(monkeypatch)
-    assert bridge._routing_enabled() is False
+    assert bridge._routing_enabled() is True
     result, holder = _run_turn_capture(monkeypatch, tmp_path, _ok_payload("ok"))
     assert result["output"] == "ok"
+    # No stage and no explicit tier -> no derived tier -> BRAIN_MODEL.
     assert holder["body"]["model"] == "gpt-6-astra"
     assert holder["body"]["reasoning"] == {"effort": "medium"}
     assert holder["body"]["max_output_tokens"] == 32768
-    # Disabled + explicit tier: wiring must stay on the default model.
+    # An unknown stage resolves to no tier, so the default model stands.
+    # (preflight rejects an unknown stage before routing runs, so this branch
+    # is only reachable through the pure resolver.)
+    assert bridge.resolve_stage_tier("nonsense", bridge._get_stage_tiers()) is None
+    assert bridge.resolve_stage_tier(None, bridge._get_stage_tiers()) is None
+
+
+def test_routing_explicitly_disabled_preserves_behavior(tmp_path, monkeypatch):
+    _clean_routing_env(monkeypatch)
+    monkeypatch.setenv("BRAIN_RISK_ROUTING_ENABLED", "false")
+    assert bridge._routing_enabled() is False
     result, holder = _run_turn_capture(
-        monkeypatch, tmp_path, _ok_payload("ok"), task_id="233",
-        risk_tier="T0")
+        monkeypatch, tmp_path, _ok_payload("ok"), risk_tier="T0")
+    assert result["output"] == "ok"
     assert holder["body"]["model"] == "gpt-6-astra"
 
 
@@ -2292,10 +2303,85 @@ def test_routing_env_overrides_stripped_and_blank(monkeypatch):
     assert bridge._routing_enabled() is True
     monkeypatch.setenv("BRAIN_RISK_ROUTING_ENABLED", "0")
     assert bridge._routing_enabled() is False
+    monkeypatch.delenv("BRAIN_RISK_ROUTING_ENABLED")
+    # Blank means the baseline is on with no .env entry at all.
+    assert bridge._routing_enabled() is True
     monkeypatch.setenv("BRAIN_MODEL_LOW", "  low-m  ")
     monkeypatch.setenv("BRAIN_MODEL_HIGH", "   ")
     assert bridge._get_model_low() == "low-m"
+    # A set-but-blank override yields "" so the pure resolver falls back
+    # to BRAIN_MODEL; only an UNSET key uses the built-in default.
     assert bridge._get_model_high() == ""
+    monkeypatch.delenv("BRAIN_MODEL_HIGH")
+    assert bridge._get_model_high() == "openai/gpt-5.6-luna"
+
+
+def test_unknown_stage_is_rejected_by_preflight(tmp_path, monkeypatch):
+    """End-to-end contract: an unknown stage never reaches routing.
+
+    Preflight rejects any stage outside the allowed set, so the documented
+    contract is "missing stage -> BRAIN_MODEL; unknown stage -> rejected",
+    never a silent fallback to the default model.
+    """
+    import pytest as _pytest
+    import preflight as _preflight
+
+    _clean_routing_env(monkeypatch)
+    with _pytest.raises(_preflight.PreflightError, match="stage"):
+        _run_turn_capture(monkeypatch, tmp_path, _ok_payload("ok"),
+                          task_id="233", stage="nonsense")
+
+
+def test_routing_model_defaults_are_built_in_and_overridable(monkeypatch):
+    _clean_routing_env(monkeypatch)
+    assert bridge._get_model_low() == "deepseek/deepseek-v4.1-flash"
+    assert bridge._get_model_high() == "openai/gpt-5.6-luna"
+    monkeypatch.setenv("BRAIN_MODEL_LOW", "cheap-x")
+    monkeypatch.setenv("BRAIN_MODEL_HIGH", "strong-x")
+    assert bridge._get_model_low() == "cheap-x"
+    assert bridge._get_model_high() == "strong-x"
+
+
+def test_stage_tier_mapping_defaults_and_override(monkeypatch):
+    _clean_routing_env(monkeypatch)
+    r = bridge.resolve_stage_tier
+    tiers = bridge._get_stage_tiers()
+    assert r("plan", tiers) == "T2"
+    assert r("review", tiers) == "T2"
+    assert r("implement", tiers) == "T0"
+    assert r("qa", tiers) == "T0"
+    assert r("closure", tiers) == "T0"
+    # Case/whitespace-insensitive stage; unknown and missing -> no tier.
+    assert r("  PLAN  ", tiers) == "T2"
+    assert r("nonsense", tiers) is None
+    assert r(None, tiers) is None
+    assert r("", tiers) is None
+    # Env override merges onto the default; unusable pairs are ignored.
+    monkeypatch.setenv("BRAIN_STAGE_TIERS",
+                       " plan:T0 ,qa:T2,bogus:T9,:T1,review")
+    overridden = bridge._get_stage_tiers()
+    assert overridden["plan"] == "T0"
+    assert overridden["qa"] == "T2"
+    assert "bogus" not in overridden
+    assert "" not in overridden
+    assert overridden["review"] == "T2"
+
+
+def test_stage_derived_tier_routes_the_turn(tmp_path, monkeypatch):
+    _clean_routing_env(monkeypatch)
+    monkeypatch.setenv("BRAIN_MODEL_LOW", "low-m")
+    monkeypatch.setenv("BRAIN_MODEL_HIGH", "high-m")
+    _, holder = _run_turn_capture(
+        monkeypatch, tmp_path, _ok_payload("ok"), stage="plan")
+    assert holder["body"]["model"] == "high-m"
+    _, holder = _run_turn_capture(
+        monkeypatch, tmp_path, _ok_payload("ok"), task_id="233", stage="qa")
+    assert holder["body"]["model"] == "low-m"
+    # An explicit risk_tier still wins over the stage-derived tier.
+    _, holder = _run_turn_capture(
+        monkeypatch, tmp_path, _ok_payload("ok"), task_id="234",
+        stage="plan", risk_tier="T0")
+    assert holder["body"]["model"] == "low-m"
 
 
 def test_model_low_only_affects_T0(monkeypatch):
@@ -2356,6 +2442,25 @@ def test_ledger_carries_model_tier_and_cache_split(tmp_path, monkeypatch):
                         "prompt_cache_split"}
 
 
+def test_ledger_carries_stage_derived_tier_and_model(tmp_path, monkeypatch):
+    import json
+    _clean_routing_env(monkeypatch)
+    monkeypatch.setenv("BRAIN_MODEL_LOW", "low-m")
+    monkeypatch.setenv("BRAIN_MODEL_HIGH", "high-m")
+    # No explicit risk_tier: the tier comes from the turn stage.
+    _run_turn_capture(monkeypatch, tmp_path, _ok_payload("ok"), stage="plan")
+    ledger = tmp_path / "sessions" / bridge._CONTEXT_LEDGER_NAME
+    row = json.loads(ledger.read_text(encoding="utf-8").strip().split("\n")[-1])
+    assert row["model"] == "high-m"
+    assert row["risk_tier"] == "T2"
+    # A light stage derives the low tier and the cheap model.
+    _run_turn_capture(monkeypatch, tmp_path, _ok_payload("ok"),
+                      task_id="233", stage="qa")
+    row = json.loads(ledger.read_text(encoding="utf-8").strip().split("\n")[-1])
+    assert row["model"] == "low-m"
+    assert row["risk_tier"] == "T0"
+
+
 def test_resolver_takes_no_prompt_diff_or_key():
     import inspect
     params = set(inspect.signature(bridge.resolve_routed_model).parameters)
```
<!-- END_GIT_DIFF -->
