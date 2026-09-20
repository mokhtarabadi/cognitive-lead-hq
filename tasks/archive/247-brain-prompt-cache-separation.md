# Task 247: Stable prompt-cache separation for Brain turns

**File:** `tasks/completed/247-brain-prompt-cache-separation.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Mode:** autopilot-locked

## Goal

Split every Brain turn prompt into a stable static prefix and a dynamic suffix so repeated turns share maximal prefix bytes, and expose the split for provider-side prompt caching.

## Manager's Notes

Standing orders apply: zero-questions task-by-task autopilot with Brain on every step; consult stored manager decisions instead of asking; reviewer approval counts as closure approval. Brain-verdict priority A2 (follows closed routing work). Discovery fed: assembly order is user_prompt baseline -> bundle prepend -> task-attach prepend -> paths append -> diff/failsafe append -> fed-context prepend; final wire order is system + history + user=effective_prompt; no breakpoint/cache-key construct exists; prompt_hash is transcript-only; body carries no cache params; provider cache support unverifiable in-repo. Design must stay provider-neutral (no unverifiable cache_control/previous_response_id params), offline-testable, and additive.

## Local TODOs

- [x] Brain planning turn under task id 247 (Architect + Programmer consult)
- [x] TDD: failing tests for static/dynamic split + stability contract
- [x] Implement split + static-prefix hash exposure (provider-neutral)
- [x] Full suite green, lint_task_file, CHANGELOG, docs
- [x] stage_and_inject_diff, move to qa, Brain QA + Reviewer review

## Acceptance Criteria

- [x] Static prefix (system prompt + bundle + task attach) is byte-stable across turns for the same task/project and computed once per identical input
- [x] Dynamic suffix (paths attach + diff + user prompt + history-sensitive parts) carries all per-turn variation
- [x] Split point is observable (returned or logged) without leaking prompt text, keys, or diffs
- [x] No change to wire semantics when the feature is inert; existing tests keep passing
- [x] Full suite exit 0, lint_task_file passes, CHANGELOG updated

## Verification Evidence

- **Test command:** uv run pytest tests/ -q
- **Expected result:** all pass, exit 0
- **Actual result:** 434 passed (11 new split tests GREEN after RED: 7 original + 4 hotfix M1-M4; 1 existing ledger exact-set test updated; 2 schema-version assertions track the constant)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** split changes effective_prompt bytes and breaks golden prompt_hash attribution; dynamic/stable misclassification leaks per-turn bytes into cache key
- **Rollback plan:** revert feature commit; static/dynamic split is additive so removal restores byte-identical prompts

---

## Execution Log & Reasoning

- Autopilot locked (standing zero-questions order). Discovery via 1 subagent (fed above).
- Seat Check: contract/split design -> Architect; implementation plan -> Programmer; skipped Designer/Strategist/Planner/QA-Review (no UI, single task, gates later).
- Brain plan (Architect-led, 2 turns — first truncated mid-table, second compact re-issue complete): logical segment split, additive sidecar descriptor, byte-identical wire, hash-only exposure via result + ledger.
- Assumption A1: plan-approval pause skipped under standing zero-questions order (same as prior closed task); plan executed verbatim from Brain, deviations will be logged.
- Implementation (TDD, Brain plan executed verbatim): `server.py` += `_frame_segment` (label+NUL+len+NUL+bytes), `_static_prefix_hash` (memoized, 64-entry cap, `_STATIC_SPLIT_COMPUTES` hook), pure `build_prompt_cache_split` (static: system/bundle/task-attach; dynamic: user/paths/diff/failsafe/fed/history-turns); `brain_turn` captures the 5 segment strings inline, computes the descriptor post-truncation, exposes it as `result["prompt_cache_split"]` + ledger `prompt_cache_split` (ledger param optional, never raises). Diff and failsafe share one dynamic slot (mutually exclusive branches) while the pure function keeps both params per the plan's order list. Wire untouched: body keys unchanged, `prompt_hash` unchanged, no provider cache params.
- Design note: split is logical, not a prefix rewrite — fed context still prepends on the wire; adapters must not assume contiguity (per Brain §4).
- RED: 7 new tests failed (missing function/key). GREEN: 7 pass. Full suite 430 passed exit 0 (1 existing ledger exact-set test updated for additive key + renamed). CHANGELOG Added entry + docs/brain-bridge.md Prompt-cache split section.
- QA_REJECTED (Brain QA Engineer, real defects, no dispute): F1 failsafe branch never populates `failsafe_text` (merged into diff slot — dynamic still varied, but contract deviation from the approved plan); F2 `_frame_segment` length-prefixes payload but not label, NUL-bearing history roles can collide; F3 descriptor must provably derive from post-truncation segments; F4 cache hashes before lookup (counter proves misses, not skipped hashes). Hotfix scope: F1-F4 + M1-M4 regression tests, no new task file, no commit/close/move.
- Hotfix RED: all 4 new tests failed pre-fix (M1 dynamic-slot mismatch, M2 NUL-role alias, M3 guard, M4 4 sha256 calls vs 3 budget). Test correction: M3 budget 50 never triggered the middle drop (turn-1 assembly ~34 chars) — lowered to 20 so truncation provably fires; M2 guard fixed 6->5 (honest length of the collision pivot). F3 premise did NOT reproduce: the split computes after the in-place middle-drop loop, so the descriptor was already post-truncation — M3 stays as a regression guard locking the invariant. F2 verified real: old framing hashed both M2 histories to identical bytes (script proof `old framing collides: True`), v2 distinguishes.
- Hotfix GREEN: F1 failsafe branch captures `failsafe_text` separately and passes it through (diff slot stays empty on failsafe turns); F2 `_frame_segment` length-prefixes labels too + schema v2 (honest lengths make left-to-right parse unique); F4 cache keyed by the static input tuple (refs, no copies; 64-cap + eviction kept). Full suite 434 passed exit 0. CHANGELOG hotfix note + docs/brain-bridge.md framing/slot sentences updated. Ready for re-QA.
- Re-QA QA_PASSED (Brain QA Engineer, project_root passed explicitly after one blocked round where the diff attach missed its root): F1-F5 all PASS on visible scope; suite evidence 434 accepted, QA did not re-execute. Debug note: an earlier re-QA without project_root returned diff-UNAVAILABLE even though the hunks were injected — local probe proved `_resolve_task_file` + `build_diff_attach` healthy, so the miss was a server-side root mismatch; always pass project_root on QA/review turns.
- Review APPROVED + PO_REVIEW_PENDING (Brain Code Reviewer, zero blocking issues): S1-S6 strengths (blueprint fidelity, wire preservation, hotfix coverage, privacy boundary, docs sync, test quality). I1 low non-blocking residual: `_STATIC_SPLIT_CACHE` lookup-then-compute unsynchronized — concurrent identical turns could double-compute; no concurrent requirement established (single-threaded MCP server), deferred as follow-up, not a fix in this task. I2/I3 coverage limits only (truncated test diff, absent core spec files per Absent-File Policy).
- Closure acceptance: standing Manager order rules this close — reviewer approval counts as Manager approval. Manager accept quote (standing, pre-authorized): reviewer approval = his approval. Closing via Senior Programmer closure XML, single issuance.
- Relayed Manager closure authorization (standing order fired by reviewer APPROVED + PO_REVIEW_PENDING, zero blocking issues): Approved for closure.
- Closure validation: task in tasks/qa/ with PO_REVIEW_PENDING + APPROVED + exact authorization confirmed pre-move; AC/DoD boxes all checked; verification evidence 434 passed exit 0; closure XML single issuance executed.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `60ec5b227e3c58777e20577766547a021a8d3560`
<!-- END_GIT_DIFF -->
