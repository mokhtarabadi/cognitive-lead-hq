# Task 135: Stack-Aware LLM Router & Provider Model Mapping

**File:** `tasks/completed/135-stack-aware-llm-router-and-model-mapping.md`
**Source:** orchestrator
**Type:** feature
**Status:** closed

## Source Context

### Variant A: Orchestrator (`**Source:** orchestrator`)

## Goal

Implement a stack-aware LLM router in `loop-engine/router.py` that resolves models through a 3-tier hierarchy (Stack-Preferred Models → Global Category Models → Global Default), propagate the detected stack profile through the daemon planning/QA/review pipeline, populate `model_preferences` in the four stack YAML profiles, extend the router test suite, and document the resolution hierarchy in `docs/loop-engine/configuration.md`.

## Blueprint Reference

Phase A / Task LE-3 — Stack-Aware LLM Router & Provider Model Mapping. Blueprint decisions D1–D5 recorded under `## Manager Decisions`.

## Manager's Notes

- Tier 1 (Stack-Preferred Models): consult `stack_profile.model_preferences` (or dict `.get("model_preferences")`), match `category` then wildcard `*`, verify `{PROVIDER}_API_KEY` env presence, return `(model, category.reasoning)`.
- Tier 2 (Global Category Models): existing category iteration fallback.
- Tier 3 (Global Default): `(default_provider, None)`.
- All routing helpers (`route_plan`, `route_qa`, `route_review`, `route_with_persona`) accept `stack_profile: Optional[Any] = None` and forward it.
- Daemon detects the stack once at the start of `_process_task` and propagates the profile into planning, QA, and review.
- Test suite must grow from 136 to >= 148 passing tests with 0 failures.

## Local TODOs

- [x] Initial codebase exploration
- [x] Initialize task file with canonical template (D1–D5, AC, DoD)
- [x] Implement 3-tier `_resolve_model` + stack_profile forwarding in `router.py`
- [x] Forward stack_profile in `qa_engine.py` run_qa/run_review
- [x] Move stack detection to start of `_process_task` and propagate profile in `daemon.py`
- [x] Populate `model_preferences` in 4 stack YAML profiles
- [x] Extend `test_router.py` with stack-aware routing tests
- [x] Document stack-aware routing in `docs/loop-engine/configuration.md`
- [x] Verify functionality (baseline 136 → >= 148 passed, 0 failed)

## Acceptance Criteria

- [x] `_resolve_model(category, stack_profile=None)` implements Tier 1 (stack-preferred models with env-key check), Tier 2 (category config fallback), Tier 3 (default provider)
- [x] `route_plan`, `route_qa`, `route_review`, `route_with_persona` accept and forward `stack_profile`
- [x] `QAEngine.run_qa` and `QAEngine.run_review` forward `stack_profile` to the router
- [x] `daemon._process_task` detects the stack before planning and propagates the profile into `route_plan`, `_execute_and_qa`, and `qa.run_review`; `_reimplement_task` forwards it to `qa.run_review`
- [x] `stacks/{kotlin-android,node-ts,python-fastapi,go-gin}.yaml` declare `model_preferences` per spec
- [x] `test_router.py` covers: preferred model with key, fallback when key missing, empty preferences, wildcard `*`, object and dict profiles, backward compatibility with `stack_profile=None`
- [x] Full suite passes with >= 148 tests, 0 failures
- [x] `docs/loop-engine/configuration.md` documents the stack-aware routing hierarchy

## Verification Evidence

- **Test command:** `uv run --project loop-engine --with pytest pytest loop-engine/ -q`
- **Expected result:** >= 148 passed, 0 failed
- **Actual result:** 148 passed, 0 failed (baseline 136 → +12 new tests in `test_router.py`)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Manager Decisions

**[2026-08-31] [D1] [ORCHESTRATOR-DETECTED]:** Two-Tier Stack Model Resolution Hierarchy
- **Rationale:** Enabling stack profiles to declare preferred models per category allows specialized LLMs (e.g. Kotlin AST specialists vs TypeScript specialists) while maintaining transparent fallback to global category models when keys are absent.
- **Alternatives considered:** Hardcoding stack-to-model mappings inside `router.py`, or replacing category routing entirely with stack routing.
- **Impact:** Clean composition of stack context with cognitive categories; full backward compatibility when stack preferences are empty or unkeyed.

**[2026-08-31] [D2] [ORCHESTRATOR-DETECTED]:** Three-Tier Fallback Chain (Stack Preferences → Category Config → Default Provider)
- **Rationale:** Guarantees a model is always resolvable: stack-preferred models win when their provider key is present, otherwise the global category chain applies, and `default_provider` is the terminal fallback.
- **Alternatives considered:** Hard-failing when no stack key exists; single-tier routing that ignores stack context.
- **Impact:** Deterministic resolution in every environment state; no new failure modes for unkeyed providers.

**[2026-08-31] [D3] [ORCHESTRATOR-DETECTED]:** Single Stack Detection at Pipeline Start
- **Rationale:** Detecting the stack once at the beginning of `_process_task` (before planning) ensures planning, QA, and review all share one consistent profile for model routing, avoiding per-stage re-detection drift.
- **Alternatives considered:** Re-detecting the stack independently at each pipeline stage.
- **Impact:** One detection point, one preflight gate; profile propagates through `route_plan`, `_execute_and_qa`, and `qa.run_review`.

**[2026-08-31] [D4] [ORCHESTRATOR-DETECTED]:** Declarative `model_preferences` in Stack YAML
- **Rationale:** Stack-specific model choice is configuration, not code — new stacks declare preferred models per category without touching `router.py`.
- **Alternatives considered:** Hardcoding stack-to-model mappings inside `router.py`.
- **Impact:** Extensible stack catalog; `StackProfileConfig.model_preferences` already exists in `models.py` and is exposed via `StackProfile.model_preferences`.

**[2026-08-31] [D5] [ORCHESTRATOR-DETECTED]:** Backward-Compatible Optional `stack_profile` Parameter
- **Rationale:** All routing helpers and QA entry points accept `stack_profile: Optional[Any] = None`, so legacy routers, stubs, and existing callers keep working unchanged.
- **Alternatives considered:** Making `stack_profile` a required parameter.
- **Impact:** Zero breaking changes; TypeError fallback chains in `qa_engine.py` and `daemon.py` preserve compatibility with legacy signatures.

## Risk & Rollback

- **Risk:** Env-key collisions between stack-preferred and category models could route to an unexpected provider; daemon signature changes could break legacy callers.
- **Rollback plan:** Revert `router.py`, `qa_engine.py`, `daemon.py` to the pre-task state (git history); stack YAML `model_preferences` can be emptied back to `{}` without code changes; tests are additive and non-destructive.

---

## Execution Log & Reasoning

**Implementation (2026-08-31):**

1. **`loop-engine/router.py`** — `_resolve_model` upgraded to the 3-tier hierarchy:
   - **Tier 1 (Stack-Preferred):** accepts `stack_profile: Optional[Any] = None`; extracts `model_preferences` safely from either a `StackProfile` object (`getattr`) or a plain dict (`.get("model_preferences")`); matches exact `category` then wildcard `"*"`; iterates candidates in order, checking `os.environ["{PROVIDER}_API_KEY"]`; reasoning level sourced from the global category config (`categories[category].reasoning`, defaulting to `unspecified` then `None`).
   - **Tier 2 (Global Category):** unchanged existing fallback chain.
   - **Tier 3 (Global Default):** `(default_provider, None)`.
   - `route_plan`, `route_qa`, `route_review`, `route_with_persona` all accept `stack_profile: Optional[Any] = None` and forward it into `_resolve_model`. Added `Any` to typing imports.
2. **`loop-engine/qa_engine.py`** — `run_qa` and `run_review` accept `stack_profile: Optional[Any] = None` and forward it to `route_qa`/`route_review`; nested `TypeError` fallbacks preserve compatibility with legacy routers lacking `stack_profile` (and, for `run_qa`, lacking `toolchain_evidence`).
3. **`loop-engine/daemon.py`** — stack detection (`StackRegistry` + `StackDetector.detect`) moved to the start of `_process_task` (after reading `task_content`, before brainstorming/planning); the profile is forwarded into `route_plan(..., stack_profile=profile)` (with `TypeError` fallback for legacy routers/stubs), `_execute_and_qa(..., stack_profile=profile)` (already present), and `qa.run_review(..., stack_profile=profile)`; duplicate detection removed from the IMPLEMENTING section (preflight retained). `_reimplement_task` forwards `stack_profile=profile` into `qa.run_review`.
4. **`stacks/*.yaml`** — populated `model_preferences` for `kotlin-android`, `node-ts`, `python-fastapi`, `go-gin` per spec (deep/quick lists).
5. **`loop-engine/test_router.py`** — 12 new tests (9 → 21 collected): preferred model with env key; ordered Tier-1 fallback (first unkeyed → second keyed wins); Tier-2 category fallback when preferred key missing; empty `model_preferences`; wildcard `*`; dict-profile resolution; `route_plan`/`route_qa`/`route_review`/`route_with_persona` with stack profile objects; backward compatibility with `stack_profile=None` for `route_plan` and `route_qa`.
6. **`docs/loop-engine/configuration.md`** — new "Stack-Aware Model Routing (LE-3)" section documenting the 3-tier resolution hierarchy, daemon propagation, backward compatibility, and the default stack preferences table; schema example updated to show populated `model_preferences`.

**Verification:** baseline 136 passed → targeted `test_router.py` 21 passed → full suite **148 passed, 0 failed** (exit 0). One regression was caught and fixed during the run: `test_le0_fixes.py::test_daemon_empty_diff_crashes` failed because a legacy `StubRouter` lacks the `stack_profile` param — resolved with a `TypeError` fallback in `_process_task` (consistent with the existing `_execute_and_qa`/`qa_engine` pattern and D5). `git diff --stat` confirms changes are strictly scoped to `loop-engine/`, `stacks/`, `docs/loop-engine/`, and the task file.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `43059db71cbc4a1775f9dd703a11b3caaeb5d389`
<!-- END_GIT_DIFF -->