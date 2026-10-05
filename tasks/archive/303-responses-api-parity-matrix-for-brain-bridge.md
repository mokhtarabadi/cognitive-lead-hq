# Task 303: Responses API parity matrix for Brain bridge

**File:** `tasks/archive/303-responses-api-parity-matrix-for-brain-bridge.md`
**Source:** manager
**Type:** chore
**Status:** superseded
**Superseded-By:** `305-brain-anti-hallucination-harness`
**Superseded-At:** `2026-10-06`
**Risk-Tier:** T1 standard
**Supersedes:** none
**Meta:** false

## Goal

Prove the Brain bridge matches the latest OpenAI Responses API on file inputs, inline markdown, retrieval chunks, and error mapping with a tested parity matrix.

## Manager's Notes

Brainstorm C4 must-task from self-judgment task 299: model routing tiers plus caps have no versioned contract and risk stale provider behavior.

## Scope

In scope:
- Parity matrix tests for input_file file_data, file_id, file_url, inline markdown, chunk overlap, 400 fatal versus 429 and 5xx retry, missing key, HTTPS violation, timeouts
- Versioned contract note for routing tiers plus caps

Out of scope:
- XML gate, attach signaling, session contract (separate tasks)
- External repos untouched
- No git add/commit/push by Hands (ZAC holds)
- docs/history, tasks/archive, CHANGELOG history lines immutable

## Local TODOs

- [ ] Inventory provider call surface with grep evidence
- [ ] Implement parity matrix tests plus contract note
- [ ] Run verification gates

## Acceptance Criteria

- [ ] AC1: parity matrix covers file inputs plus errors with tests
- [ ] AC2: routing tiers plus caps carry a versioned contract
- [ ] AC3: full suite passes with evidence recorded

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pathspec pytest tests/ -q
- **Expected result:** pass exit 0
- **Actual result:** pending
- **Exit code:** pending

## Definition of Done

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** provider behavior drifts after matrix is written
- **Rollback plan:** worktree diff revert before staging

---

> **Superseded:** This task was bundled into META task `305-brain-anti-hallucination-harness` and archived on 2026-10-06. See `tasks/backlog/305-brain-anti-hallucination-harness.md` (or its Kanban successor) for the unified execution. History preserved via `git log --follow -- tasks/archive/303-responses-api-parity-matrix-for-brain-bridge.md`.

## Execution Log & Reasoning

- Origin: brainstorm C4 from task 299 self-judgment report.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
