# Task 317: Brain pre-send token budget guard

**File:** `tasks/completed/317-brain-pre-send-budget-guard.md`
**Source:** manager
**Type:** feature
**Status:** closed

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

Manager accept quote for closure: Approved for closure. Closure executed via single-issuance Senior Programmer XML, file moved to completed, status closed.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `c00be0136395be6f54f6c8dea5fb0bde725b62da`
<!-- END_GIT_DIFF -->
