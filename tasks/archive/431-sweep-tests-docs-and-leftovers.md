# Task 431: Sweep Leftover References, Slim the Tests, and Clean Docs and README

**File:** `tasks/backlog/431-sweep-tests-docs-and-leftovers.md`
**Source:** manager
**Type:** improvement
**Status:** backlog

## Goal

Close the meta task with one code-search-driven sweep: remove every reference and leftover left by
the LiteLLM migration, the zen-bridge rename, and the proxy removal; make the test suite smaller and
more focused without losing a guard; and refresh the docs and READMEs so they describe the final
state only.

## Manager's Notes

Verbatim intent:

> "use $code-search remove any refrences and lefovers realted to our cleanup and migration to litellm
> and clean them"

> "cleanup our tests make them cleaner focusable"

> "cleanup our docs and readme at end."

Binding context:

- This task runs last inside the meta task, after the migration, the rename, and the proxy removal
  have landed, so it treats their output as the ground truth.
- No test may be deleted unless the behavior it covered is gone; a guard that still matters is
  retargeted, not dropped.
- `docs/history/`, `tasks/archive/`, `tasks/completed/`, and `tasks/.sessions/` are records and stay
  out of the sweep.
- `split_system_prompt.py` counts and the prompt-sync byte-identity gate must stay green after any
  doc edit that touches a prompt fragment.

## Local TODOs

- [ ] Run the `code-search` workflow (graph build, query, `explain_node`, signatures) over the
      changed slices before editing, and record the graph coverage line.
- [ ] Grep for `litellm`, `zen-proxy`, `warp`, `psiphon`, `_post_with_retry`, `_make_client`,
      `_upstream_mode`, `_upstream_url` and classify each live hit as fixed, retargeted, or archive.
- [ ] Collapse duplicated bridge/env tests into named behavior tests; delete tests that only covered
      removed code; keep one test per surviving contract.
- [ ] Re-anchor any fixture that names a removed path or key.
- [ ] Refresh `README.md`, `docs/README.md`, `docs/brain-bridge.md`, `docs/services.md`, and each
      touched slice `README.md` / `DECISIONS.md` to the final state.
- [ ] Update `AGENTS.md` and `tests/README.md` only where a rule or slice duty actually changed.
- [ ] Verify the prompt-sync suite and the full suite after every doc edit that touches fragments.

## Acceptance Criteria

- [ ] A repo-wide grep for the retired names returns only history, archive, completed-task, and
      session-transcript paths.
- [ ] No duplicate test covers the same contract; the suite is smaller with the guard floor intact.
- [ ] Every doc and README describes the final architecture with no reference to a removed component.
- [ ] Prompt-sync byte identity still holds.
- [ ] The full suite passes with exit code 0.

## Verification Evidence

- **Test command:** `rtk test uv run --with pytest --with mcp==1.30.0 python -m pytest tests/ -q`
- **Expected result:** full suite green, exit code 0, collected count recorded before and after the
  slimming.
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

> Verification runner rule: the first verification run MUST use the `rtk test` prefix; a raw rerun is
> allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `testing-verification` applied and evidence recorded

## Risk & Rollback

- **Risk:** a test is deleted together with a guard that still protects a surviving contract, so a
  real regression can land unnoticed.
- **Rollback plan:** restore the deleted test file from git history and retarget it; no production
  code depends on test presence.

---

## Execution Log & Reasoning

_(The Hands: log technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
