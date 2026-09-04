# Task 143: Multi-Project Topic Routing & Isolated Workspaces

**File:** `tasks/backlog/143-multi-project-topic-routing.md`
**Source:** orchestrator
**Type:** feature
**Status:** open

## Goal

Implement multi-project routing in `loop-engine/multi_project.py` and `gateway.py` allowing a single Telegram supergroup to manage multiple distinct project repositories using forum topic IDs, maintaining isolated state databases, memories, and task queues per project topic.

## Local TODOs

- [ ] Initial codebase exploration (models.py, gateway.py, state.py)
- [ ] Define topic mapping schemas in models.py linking Telegram topic_id to workspace roots
- [ ] Implement multi_project.py router
- [ ] Wire ApprovalGateway to route approvals/cards to the project topic thread
- [ ] Add unit tests in loop-engine/test_multi_project.py
- [ ] Verify full test suite passes

## Acceptance Criteria

- [ ] Topic mapping schemas in `models.py` linking Telegram `topic_id` to workspace root paths.
- [ ] `ApprovalGateway` routes approvals and cards to the specific project topic thread in Telegram.
- [ ] Unit tests in `loop-engine/test_multi_project.py` pass.
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

- **Risk:** Topic-to-workspace misrouting could leak state or approvals across projects.
- **Rollback plan:** Restrict routing to a single default project when no topic mapping is configured.

---

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->