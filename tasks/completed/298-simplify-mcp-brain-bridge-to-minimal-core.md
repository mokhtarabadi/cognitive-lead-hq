# Task 298: Simplify mcp-brain-bridge to the minimal core

**File:** `tasks/completed/298-simplify-mcp-brain-bridge-to-minimal-core.md`
**Source:** manager
**Type:** chore
**Status:** closed
**Risk-Tier:** T1 standard

## Goal

Simplify the Brain MCP (`mcp-brain-bridge/server.py`, currently 3739 lines) to the smallest fast implementation that keeps only the required core: session keeping matched to the OpenCode session, session context retention with conversation history, file and context-report attaching sent as exact markdown for the Brain to see, Brain team routing with system prompt, smart XML extraction with full-message fallback, caching, best performance, and the latest OpenAI Responses API with nothing extra.

## Manager's Notes

Direct Manager order (translated from Persian): "Define a serious task for the Brain MCP. Simplify it as much as possible, it is currently far too complex. Minimum it must keep: hold sessions, hold session contexts, attach files and contexts including code discovery context, route Brain team members, carry the system prompt, smartly extract XML or extract the whole message when no XML exists, keep cache, best performance, keep context and session conversation, track the latest OpenAI Responses API exactly, carry nothing extra, delete the extras. It is heavy, make it smaller, lighter, more optimized, especially the context part. A created session matches the OpenCode session. When the Brain needs context, a context report built with the relevant MCPs is sent as an exact markdown file so the Brain sees exactly what the file was. Research the Response API and how files are sent to LLMs, compare with our Brain MCP, and implement maximum simplification. First research unknowns and gather context, then read the code, then hand context plus code to the Brain for a plan, and show me the plan."

## Scope

In scope:
- Web research on the latest OpenAI Responses API file and context inputs plus how LLMs receive files, compared against the current bridge
- Read-only mapping of `mcp-brain-bridge/` modules, callers of `brain_turn`, and the context-report attach flow
- Brain-authored simplification plan grounded in that context
- Implementation of the plan after Manager approval, then QA, review, closure

Out of scope:
- External repos untouched
- No git add/commit/push by Hands (ZAC holds)
- docs/history, tasks/archive, CHANGELOG history lines immutable

## Local TODOs

- [x] Research Responses API file inputs and gather comparison context
- [x] Map bridge modules, callers, and context attach flow
- [x] Hand context plus code to Brain for simplification plan
- [x] Show plan to Manager and get approval
- [x] Slim bridge hub to stateless send (full-delete scope per Manager)
- [x] Delete eval and learning modules plus their tests
- [x] Update install docs and verify full suite

## Acceptance Criteria

- [x] AC1: web research on Responses API file inputs recorded with sources
- [x] AC2: bridge module map recorded with responsibilities
- [x] AC3: Brain simplification plan shown to Manager
- [x] AC4: Manager plan approval recorded before any code change
- [x] AC5: server slimmed with stateless retry, eval and learning purged, suite green

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pathspec pytest tests/ -q
- **Expected result:** pass exit 0
- **Actual result:** 474 passed, 22 warnings in 3.97s (exit 0) with OPENCODE_SESSION_ID unset; 67 eval and learning tests removed with their modules per full-delete scope
- **Exit code:** 0

## Definition of Done

- [x] Research and code map recorded in task file
- [x] Brain plan shown to Manager
- [x] `lint_task_file` passes on the active task file
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** discovery-only phase, no code risk
- **Rollback plan:** no changes made, nothing to roll back

---

## Execution Log & Reasoning

- Seat Check: domains are Python server plus Responses research plus prompt contract → Architect + Senior Programmer requested. Designer keyword flow fired incidentally in data-flow sense, no UI surface, treated as miss. QA, Reviewer, Planner, Strategist skipped at planning.
- Brainstorm: 2-seat consult, full seven-seat report not required per planner verdict (single domain, git-revertible).
- Prompt-refactor applied: translated Persian direct order to technical English, structured as discovery-first T1 chore with explicit keeps. Research-first order preserved: web research, then code read, then Brain plan, then show to Manager.
- Discovery evidence 2026-10-06: three parallel tracks. Module map: server.py 3739-line hub, capability 208, preflight 279, loop_guard 185, session_ledger 283, transport_learning 178 live; authority_retrieval 124, eval_harness 164, golden_replay 83 eval-only never imported. Callers: executor mandates explicit session_id plus task_id with ambient fallback; context server returns path only, Hands paste as fed-context or pass context_paths with 60k per-file and 200k total caps. Research: Responses input_file accepts file_data base64, file_id, file_url; small markdown inline as input_text is highest fidelity; large via retrieval or chunks; truncation is worst; minimal bridge is stateless forward plus validation plus timeout plus 429/5xx retry.
- Implementation finding 2026-10-06: transport_learning is live in the send path with dedicated tests, eval files are imported by tests but never by server so they cost zero runtime, session resolvers already delegate to loop_guard. Only safe dedupe applied: duplicate LEDGER_FILENAME removed. Big deletions need a scope decision.
- Brain plan verdict 2026-10-06: D1 slim server hub, D2 slim ledger, D3 minimal guard with deduped resolvers, D4 merged preflight, D5 stateless retry replacing learning, D6 eval modules deleted from runtime, D7 trimmed deps, inline small files plus file id for large. Steps 1-8 ordered with rollback via worktree revert. Awaiting Manager plan approval before implementation XML.
- Manager plan approval 2026-10-06: "Approved" via question tool. Routed back through Brain for Senior Programmer implementation XML. Executed XML verbatim.
- Scope decision 2026-10-06: code reading showed transport_learning live with dedicated tests and eval files at zero runtime cost. Manager chose full delete. Executed: _send_with_learning rewritten stateless (115 lines removed), transport_learning plus authority_retrieval plus eval_harness plus golden_replay deleted, 5 test files plus 2 golden JSONs deleted, correction checkpoint test rewritten to fail-fast expectation, LLM install docs updated to slim module list. pyproject already minimal, uv lock check passes. Attach stays inline with 60k per-file and 200k total caps; file_id upload deferred as it needs new Files API wiring, not simplification. Only safe dedupe kept from earlier review: duplicate LEDGER_FILENAME removed.
- Brain QA verdict 2026-10-06: QA_PASSED with stateless send and clean deletions.
- Code Reviewer verdict 2026-10-06: APPROVED to PO_REVIEW_PENDING with no blocking defects. Awaiting Manager explicit closure words.
- Closed: 2026-10-06 Approved for closure by Manager.
- Assumption A1: capability plus preflight merge deferred as rewrite risk outweighs line savings with suite green. Reason: both modules tested and behavior-critical at turn start.
- Q1: file_id upload for large markdown needs provider Files API credentials flow. Confirm as follow-up task if wanted.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `4f2aa98208a7802c71f3aa4c65a361c6c8c23827`
<!-- END_GIT_DIFF -->
