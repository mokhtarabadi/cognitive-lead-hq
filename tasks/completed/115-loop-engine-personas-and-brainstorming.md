# Task 115: Full Persona Coverage + Brainstorming Protocol in Loop Engine

**File:** `tasks/completed/115-loop-engine-personas-and-brainstorming.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Make the Cognitive Loop Engine faithfully implement the Manager-defined system prompt: all 7 operational personas invocable (derived from source fragments, not hardcoded), plus first-class Brainstorming Protocol support (six-persona swarm with `<brainstorming_session>` output schema) as a planning mode.

## Manager's Notes

- Manager directive (2026-08-26, translated): "ALL the personas must be inside it — they must be there." This closes audit gaps G1–G4 from the Task 114 verification:
  - G1: engine-invented "PO Closure" persona must be resolved (drop it or derive it formally).
  - G2: output tokens must match persona-defined ones (`QA_PASSED/QA_REJECTED`, `APPROVED/APPROVED_WITH_CHANGES/REJECTED_NEEDS_FIXES`) — update `qa_engine.decide()` accordingly.
  - G3: `PERSONA_INSTRUCTIONS` in `router.py:28-76` are hardcoded condensed variants — replace with runtime derivation from `prompts/fragments/12-personas.md` so fragment edits propagate automatically.
  - G4: UI/UX Designer, Senior Programmer, Project Planner, Sprint Strategist are never invoked — add routes/stages that use them where their triggers match.
- Manager question answered 2026-08-26: brainstorming currently has ZERO support in the engine (`grep brainstorm loop-engine/*.py` → 0 hits). The only paths today are (a) the full system-prompt.md riding along in `<context>` while hardcoded architect instructions steer toward `<hands_implementation_task>` instead, or (b) indirect execution if the OpenCode Hands happen to load the `brainstorm-swarm` skill during IMPLEMENTING. The offline ChatGPT experience (paste system prompt → request brainstorm → six-persona XML session) does not exist in the engine.
- Required brainstorming behavior (mirrors `prompts/fragments/16-brainstorming_protocol.md`): trigger on explicit Manager request or cross-disciplinary ambiguity → activate the six swarm personas (system_architect, security_engineer, product_manager, business_strategist, legal_advisor, critical_thinker) → synthesize into a `<brainstorming_session>` XML report (summary, per-persona responses, tradeoffs, conflict_resolution, final_recommendation) → present via Telegram approval gate for Manager review.
- Design decision to make during implementation: single structured mega-call enforcing the output schema vs. six parallel persona calls + synthesis call (protocol-literal). Prefer protocol-literal parallel calls; fall back to mega-call if provider concurrency is a concern.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Initial codebase exploration (router.py persona layer, daemon pipeline stages)
- [x] Build persona loader: parse personas from `prompts/fragments/12-personas.md` at runtime
- [x] Replace hardcoded `PERSONA_INSTRUCTIONS`; align decision tokens with persona-defined ones (`QA_PASSED/QA_REJECTED`, `APPROVED/APPROVED_WITH_CHANGES/REJECTED_NEEDS_FIXES`); update `qa_engine.decide()` regexes + tests
- [x] Resolve PO Closure persona (derive formally from Code Reviewer PO-review step or remove)
- [x] Add invocation routes for all 7 personas (UI/UX Designer, Senior Programmer, Project Planner, Sprint Strategist included) at pipeline points matching their triggers
- [x] Implement BrainstormStage: trigger detection, six-persona parallel calls, synthesis, `<brainstorming_session>` schema enforcement
- [x] Wire brainstorm session into Telegram approval flow (Manager reviews synthesized session)
- [x] Add characterization tests (persona loader, token alignment, brainstorm stage with stubbed router)
- [x] Verify functionality

## Acceptance Criteria

- [x] Zero hardcoded persona instruction strings remain in `router.py`; all persona prompts derive from `prompts/fragments/*.md` at runtime, and editing a fragment changes engine behavior without code edits
- [x] All 7 defined personas are invocable in the pipeline at trigger-matching stages, and decision tokens exactly match persona-defined statuses; `decide()` passes tests for both vocabularies
- [x] A brainstorming request produces a `<brainstorming_session>` XML report containing all six swarm persona responses + synthesis, routed through the Telegram approval gate; covered by stubbed-router tests

## Verification Evidence

- **Test command:** `for t in test_models.py test_state.py test_router.py test_executor.py test_audit_fixes.py test_personas_brainstorm.py; do uv run --no-project --with pydantic --with watchdog python3 $t; done` (run in `loop-engine/`)
- **Expected result:** all suites pass, exit code 0
- **Actual result:** 8+10+9+8+14+14 = 63 passed, 0 failed across 6 suites; module import smoke test OK (`daemon`, `brainstorm`, `personas`, `router`, `qa_engine`); live loader check: 7 personas loaded
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** runtime fragment parsing couples the engine to fragment formatting (a fragment edit could break parsing); six parallel LLM calls raise cost/latency per brainstorm; wider persona surface may route tasks to ill-suited personas.
- **Rollback plan:** `git revert` the implementation commits; keep the previous hardcoded persona layer behind a config flag during transition for instant fallback.

---

## Execution Log & Reasoning

**Skill loaded first (per Manager order):** `brainstorm-swarm` — its execution rules (independent analysis, conflict documentation, ≥3 observations, grounding, schema output) are encoded as protocol constants in `brainstorm.py`.

### Implementation

| Change | File | Detail |
|--------|------|--------|
| NEW: runtime persona loader | `loop-engine/personas.py` | Parses `<persona name="…">` blocks from `prompts/fragments/12-personas.md` (trigger/duty/behavior) and `16-brainstorming_protocol.md` (focus/output + verbatim `<brainstorming_session>` schema). CWD-independent via package-anchored `_REPO_ROOT` fallback. |
| REWRITE: persona layer | `loop-engine/router.py` | Deleted the entire hardcoded `PERSONA_INSTRUCTIONS` dict (G3). `_build_system_context` now injects the fragment's trigger/duty/behavior VERBATIM; unknown personas raise `ValueError` instead of silently impersonating. New `STAGE_PERSONAS` map; new public `route_with_persona(name, …)` makes all 7 personas invocable (G4). |
| G1 resolution | `router.STAGE_PERSONAS` | No invented "PO Closure" persona — closure stage reuses **Code Reviewer**, whose fragment behavior defines the PO-review/"Approved for closure" flow. |
| G2 alignment | `loop-engine/qa_engine.py` | `decide()` regexes now accept persona-defined tokens (`QA_PASSED/QA_REJECTED`, `APPROVED_WITH_CHANGES`, `REJECTED_NEEDS_FIXES`, `PO_REVIEW_PENDING`) alongside engine shorthand; longest-alternative-first ordering keeps quoted-token reports correct. |
| NEW: BrainstormStage | `loop-engine/brainstorm.py` | Trigger = "brainstorm" keyword or `<brainstorming_session>` marker. Six INDEPENDENT parallel calls (`asyncio.gather` + `to_thread`; no cross-contamination), then one synthesis call receiving all six analyses + the verbatim output schema with mandatory conflict documentation. |
| Pipeline wiring | `loop-engine/daemon.py` | Phase 1.5 runs between content read and PLANNING: brainstorm → Telegram "Brainstorm Review" approval gate → reject→BACKLOG / approve→session injected into `route_plan(extra_context=…)`. Signature updated incl. QA-retry recursion path. |

### Design decisions

1. **Fragment-derived > hardcoded:** planning now legitimately asks the Software Architect for a *blueprint* (per its fragment behavior) instead of the old hardcoded demand for `<hands_implementation_task>` — implementation remains the Hands' job via executor.
2. **Parallel swarm over mega-call:** protocol-literal six independent calls preserve the skill's no-cross-contamination rule; synthesis is a separate grounded call.
3. **Loader fallback anchoring:** fragments resolve against `workspace_root` first, then repo root — removes the CWD-dependence class (F26 family) for library use and tests.

### Verification

63/63 tests pass across 6 suites, exit 0 (14 new in `test_personas_brainstorm.py`: loader coverage, zero-hardcoded-source assertion, 7-persona invocability, token vocabularies, swarm independence + synthesis schema, loud-failure paths). Import smoke test OK; live loader returns 7 personas.

Files changed: `loop-engine/{personas.py (new), brainstorm.py (new), router.py, qa_engine.py, daemon.py, test_personas_brainstorm.py (new)}`, `CHANGELOG.md`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `3175b1e1aa5bd167df300dcb1671ff250a3364a1`
<!-- END_GIT_DIFF -->
