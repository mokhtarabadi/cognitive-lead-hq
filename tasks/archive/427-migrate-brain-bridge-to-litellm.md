# Task 427: Migrate Brain Bridge to LiteLLM and Gate Debug Output by Env

**File:** `tasks/archive/427-migrate-brain-bridge-to-litellm.md`
**Source:** manager
**Type:** feature
**Status:** superseded
**Superseded-By:** `432-brain-litellm-zen-bridge-cleanup`
**Superseded-At:** `2026-11-27 09:00 UTC`

## Goal

Make LiteLLM the single upstream call path for `mcp-brain-bridge` so the bridge stops owning an
OpenAI Responses client, retry ladder, and endpoint/conversion glue. Delete the leftover custom
transport code and its tests, register the OpenCode Go models the Brain uses inside LiteLLM, and put
every per-turn debug line behind one env switch documented in `.env.example`.

## Manager's Notes

Verbatim intent:

> "we need to use litellm instead our custom openai apis endpoints in brain mcp and remove lefter
> over codes/tests make litellm handle all things. also reduce the outputs like debug when a brain
> turn called or manage it via a .env using our .env.example"

Binding context:

- The earlier evaluation in task 426 recommended keeping the hand-written transport. The Manager
  overrides that recommendation: migrate now, and fold task 426 into the meta task instead of
  following its recommendation.
- Identity headers for the Go gateway stay where they are today (the zen-bridge proxy). This task
  only replaces the Brain's own upstream client and conversion layer.
- Current transport surface to remove: `_post_with_retry`, `_make_client`, `_upstream_mode`,
  `_upstream_url`, and the responses/chat-completions conversion helpers in
  `mcp-brain-bridge/server.py`.
- Lua-free requirement: no new frontend or shell code; Python only.

## Local TODOs

- [ ] Inventory the current transport surface in `mcp-brain-bridge/server.py` (client, retry,
      conversion, endpoint selection) and record the exact line ranges to delete.
- [ ] Add LiteLLM as a bridge dependency with a pinned version in `mcp-brain-bridge/pyproject.toml`.
- [ ] Register the Go-gateway models as a custom LiteLLM `model_list` entry (openai-compatible
      base `BRAIN_API_BASE`, custom `extra_headers` passthrough, `/responses` endpoint support).
- [ ] Move retry, timeout, and 429 handling to LiteLLM `num_retries` / timeout parameters and delete
      the hand-written ladder.
- [ ] Keep `TRUNCATION_UNRECOVERABLE`, oversized-output stubbing, and XML extraction behavior
      byte-identical; cover each with a test.
- [ ] Delete dead conversion helpers and every test that only exercised removed code.
- [ ] Gate all per-turn stderr chatter behind one `BRAIN_DEBUG` switch (default off); route
      degraded-path warnings through it too.
- [ ] Document `BRAIN_DEBUG` and any new `BRAIN_LITELLM_*` keys in `.env.example` and
      `docs/brain-bridge.md`.
- [ ] Record the applied `testing-verification` evidence before lint.

## Acceptance Criteria

- [ ] `mcp-brain-bridge/server.py` performs no direct `httpx` POST to `/responses`; LiteLLM is the
      only provider call path.
- [ ] The configured Brain models (including the current Go-gateway model) are registered in code or
      config so a `brain_turn` with the production env values succeeds.
- [ ] Retry, timeout, 429-terminal, and truncation-recovery semantics match the pre-migration
      behavior, proven by tests that stay green.
- [ ] Debug output on a normal `brain_turn` is silent unless `BRAIN_DEBUG` is truthy.
- [ ] No leftover custom transport helper, dead import, or test that only covered removed code
      remains (verified by grep in the Execution Log).
- [ ] `docs/brain-bridge.md` and `.env.example` describe the new transport and the debug switch.

## Verification Evidence

- **Test command:** `rtk test uv run --with pytest --with mcp==1.30.0 python -m pytest tests/test_brain_bridge.py tests/test_brain_responses_alignment.py tests/test_raw_output_recovery.py tests/test_brain_preflight.py -q`
- **Expected result:** all collected tests pass, exit code 0; one live `brain_turn` smoke call
  through the production env returns a valid status.
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

- **Risk:** LiteLLM drops a retry or timeout behavior the bridge relies on, so a long reasoning turn
  returns a hard error instead of retrying; custom model registration for the Go gateway may not
  accept the `/responses` shape the Brain sends.
- **Rollback plan:** keep the old transport behind `BRAIN_UPSTREAM_MODE=legacy` until the LiteLLM
  path is green, then delete the legacy branch in the same task; if migration fails irrecoverably,
  revert the bridge commit and restore the pinned dependency set.

---

> **Superseded:** This task was bundled into META task `432-brain-litellm-zen-bridge-cleanup` and archived on 2026-11-27 09:00 UTC. See `tasks/backlog/432-brain-litellm-zen-bridge-cleanup.md` (or its Kanban successor) for the unified execution. History preserved via `git log --follow -- tasks/archive/427-migrate-brain-bridge-to-litellm.md`.

## Execution Log & Reasoning

_(The Hands: log technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
