# Task 146: Structured Metrics, Token Cost Tracking & Error Logging

**File:** `tasks/backlog/146-structured-metrics-and-sentry.md`
**Source:** orchestrator
**Type:** feature
**Status:** open

## Goal

Implement structured observability in `loop-engine/metrics.py` tracking token usage, latency per pipeline stage, error rates, and optional Sentry error capturing for production monitoring.

## Local TODOs

- [ ] Initial codebase exploration (daemon.py, router.py, qa.py)
- [ ] Implement MetricsCollector tracking prompt/completion tokens + estimated cost per task
- [ ] Structured JSON logging for all daemon events
- [ ] Optional Sentry error capturing
- [ ] Add unit tests in loop-engine/test_metrics.py
- [ ] Verify full test suite passes

## Acceptance Criteria

- [ ] `MetricsCollector` tracking prompt tokens, completion tokens, and estimated cost per task.
- [ ] Structured JSON logging for all daemon events.
- [ ] Unit tests in `loop-engine/test_metrics.py` pass.
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

## Manager Decisions

_(Log non-trivial architectural, design, or strategic decisions here using the format from `<decision_logging_mandate>`: `**[YYYY-MM-DD] [DECISION_ID] [SOURCE]:** <summary>`.)_

## Risk & Rollback

- **Risk:** Sentry SDK may introduce dependency bloat or network errors in air-gapped envs.
- **Rollback plan:** Make Sentry optional via config and no-op when not configured.

---

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->