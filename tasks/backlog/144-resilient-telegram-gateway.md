# Task 144: Resilient Telegram Gateway with Auto-Reconnect & Dead-Letter Queue

**File:** `tasks/backlog/144-resilient-telegram-gateway.md`
**Source:** orchestrator
**Type:** feature
**Status:** open

## Goal

Harden `loop-engine/gateway.py` with automatic exponential backoff reconnection, network error recovery, dead-letter queue for unacknowledged approval requests, and graceful timeout handling to ensure the daemon never crashes due to Telegram API disconnects.

## Local TODOs

- [ ] Initial codebase exploration (gateway.py, state.py, daemon.py)
- [ ] Implement exponential backoff + auto-reconnect retry loop for polling/sending
- [ ] Add SQLite dead-letter queue table for unsent approval requests
- [ ] Implement graceful timeout handling
- [ ] Add unit tests in loop-engine/test_gateway_resilience.py
- [ ] Verify full test suite passes

## Acceptance Criteria

- [ ] Exponential backoff and auto-reconnect retry loop in Telegram polling and sending.
- [ ] Unsent approval requests queued in SQLite dead-letter table upon network failure.
- [ ] Unit tests in `loop-engine/test_gateway_resilience.py` pass.
- [ ] Full test suite passes with 0 failures.

## Verification Evidence

- **Test command:** `python -m pytest loop-engine/ -q`
- **Expected result:** all tests pass, 0 failures
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Repeated reconnect loops may mask Telegram API auth failures (dead token).
- **Rollback plan:** Fail fast after N consecutive errors and surface the daemon as CRASHED with diagnostics.

---

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->