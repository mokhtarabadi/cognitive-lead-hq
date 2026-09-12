# Task 198: Transport error taxonomy (retryable vs fatal)

**File:** `tasks/backlog/198-error-taxonomy-retryable-fatal.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Goal

Tag transport errors retryable/fatal: retry only retryable, fail fast on fatals.

## Manager's Notes

From Brain round-2 self-improvement (N6 delta). The retry wrapper already retries 429/5xx + timeouts; this task makes the taxonomy explicit: retryable (429, 500/502/503/504, timeouts, transport errors) vs fatal (400, 401, 403, 404 — fail immediately with a precise error, never burn 3 attempts). Implement in both servers' post paths + mocked tests for each class. Standing authorization: autopilot + autoclosure, execute without asking.

## Local TODOs

- [ ] Encode taxonomy (retryable set vs fatal set) in both servers
- [ ] Fail-fast path for fatals (no retry, precise error)
- [ ] Mocked tests per class, full suite green
- [ ] Update CHANGELOG, lint, stage, qa, autopilot QA/review, autoclose

## Acceptance Criteria

- [ ] 429/5xx/timeouts retry (existing behavior kept); 400/401/403/404 fail on first attempt
- [ ] Fatal errors carry status + path + snippet, never the key
- [ ] Mocked tests cover both classes in both servers, full suite green

## Verification Evidence

- **Test command:** `uv run --project mcp-brain-bridge --with pytest --with pathspec pytest tests/ -q`
- **Expected result:** all pass, exit 0
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

- **Risk:** Misclassifying a transient error as fatal (or vice versa) changes retry behavior
- **Rollback plan:** Revert to the current retry sets; taxonomy is centralized in one constant per server

---

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
