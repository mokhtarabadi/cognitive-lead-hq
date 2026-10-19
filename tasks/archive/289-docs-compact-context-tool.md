# Task 289: Document the agent-callable compact_context tool

**File:** `tasks/completed/289-docs-compact-context-tool.md`
**Source:** manager
**Type:** docs
**Status:** closed

## Goal

Update the HQ system prompt, executor agent, and compaction guide to reflect that the agent can now trigger compaction itself via the `compact_context` tool (added to the smart-compact plugin, pushed and smoke-tested live). The old text said the agent cannot run the plugin command, which the new tool makes false.

## Manager's Notes

Manager pushed the plugin and restarted; the live smoke test passed (`compact_context` returned the correct trim and compact messages; plugin loaded 25 times, 0 failures). This task only updates the HQ side so the prompt and docs match the shipped tool.

## Local TODOs

- [x] Update fragment 22 (`<compaction_protocol>`) with the `compact_context` tool and the corrected rule
- [x] Update the executor compaction section
- [x] Add the tool to `docs/compaction.md`
- [x] Bump `<system_version>` 9.51.0 → 9.52.0, regenerate, update the prompt-sync test
- [x] Sync the prompt + agent globally and update the `opencode_config` memory
- [x] Run the gate and record evidence

## Acceptance Criteria

- [ ] Fragment 22 and the executor no longer claim the agent cannot trigger compaction; both name `compact_context`
- [ ] `docs/compaction.md` documents the tool and its inputs
- [ ] `system-prompt.md` is 9.52.0 with `compact_context`, byte-identical on re-assemble
- [ ] `tests/test_prompt_sync.py` pins 9.52.0 and asserts `compact_context`
- [ ] Targeted gate passes with exit code 0

## Verification Evidence

- **Test command:** rtk test uv run --with-requirements /tmp/opencode/clh-test-reqs.txt pytest tests/test_prompt_sync.py tests/test_mcp_servers.py -q
- **Expected result:** pass, exit code 0
- **Actual result:** `83 passed`
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** none material — docs/prompt text only; the tool already ships.
- **Rollback plan:** revert the fragment/agent/docs hunks and the version bump.

---

## Execution Log & Reasoning

**Plan verdict:** continuation of the Manager-approved "Add it" work — the tool is live, so the docs must match. **Brainstorm:** not required (docs-only). **Seat Check:** domain = prompt/docs (Architect) → requested: Software Architect; skipped: UI/UX Designer (no surface), Planner/Strategist (no scope change).

**Changes:** fragment 22 now states the agent CAN call `compact_context` (with `keepTurns` and `mode`), and the "Rule" was corrected; the executor item 4 mirrors it; `docs/compaction.md` gains an "Agent-callable tool" section; `<system_version>` 9.51.0 → 9.52.0 with a regenerated, byte-identical prompt; the prompt-sync test pins 9.52.0 and asserts `compact_context`.

**Live evidence (plugin side):** `compact_context({mode:"trim"})` → "[smart-compact] tool output will be trimmed on the next request."; `compact_context({keepTurns:9999})` → "[smart-compact] summarized 0 turn(s); …". Plugin loaded 25 times, 0 failures.

**Verification:** targeted gate `83 passed`, exit 0.

**Gate (autopilot):** Code Reviewer `PO_REVIEW_PENDING` — technically approved, Low only. Applied R2 (executor item 2 no longer says "manual", matching fragment 22) and R3 (prompt-sync test also asserts `keepTurns`). Left R1 (changelog ordering) as-is — newest-first is intentional. Re-synced the prompt + agent globally and re-ran the gate: `83 passed`, exit 0. Closure awaits the Manager's exact word.

**Closure executed** on Manager quote "Approved for closure": moved to `tasks/completed/`, Status `closed`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `ae321f9ebe8b412a649c84dd43a8abb1640333b4`
<!-- END_GIT_DIFF -->
