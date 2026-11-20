# Task 0386: Unify 100% Brain Turn and Permanently Eliminate Manual Mode

**File:** `tasks/completed/0386-unify-100-percent-brain-turn.md`
**Source:** orchestrator
**Type:** feature
**Status:** closed
**Finished:** 2026-11-08T15:18:11Z
**Submitted:** 2026-11-08T14:57:02Z

## Goal

Permanently eliminate manual mode and unify on 100% `brain_turn`. The platform operates exclusively via `mcp-brain-bridge` (`brain_turn`). The Manager is supervisor and approval gatekeeper, never a manual copy-paste courier. All fenced prompt emission for Manager ferrying is removed from all fragments and agent definitions.

## Manager's Notes

Direct order: "unify 100% brain turn and permanently eliminate manual mode". Re-audit system prompt to ensure no lost content. Brain QA to verify manual/auto mode separation is correct. Run tests at end only.

## Local TODOs

- [x] Step 1: Bump system version to 9.78.0
- [x] Step 2: Unify 02-role.md
- [x] Step 3: Unify 19-initialization.md
- [x] Step 4: Purge manual courier instructions from 06-personas.md
- [x] Step 5: Purge manual mode blocks from 09-hands_protocols.md
- [x] Step 6: Update cognitive-executor.md & AGENTS.md
- [x] Step 7: Update docs/architecture.md, docs/data_model.md, and README.md
- [x] Step 8: Reassemble system prompt
- [x] Step 9: Update test suite
- [x] Step 10: Run full test suite
- [x] Step 11: Document ADRs & Changelog
- [x] Step 12: Finalize task metadata and atomic QA transition

## Acceptance Criteria

- [x] All manual courier instructions purged from system prompt and agent definitions
- [x] All fragments reference `cognitive-executor` agent by name, not file path
- [x] Manual and automatic modes fully defined and separated
- [x] Seats pipeline is correct and verified
- [x] System prompt reassembled at 9.78.0
- [x] All tests pass with exit code 0
- [x] CHANGELOG.md updated via Parse-Then-Append
- [x] ADRs appended to DECISIONS.md files

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/ -q`
- **Expected result:** All tests pass with exit code 0
- **Actual result:** 826 passed, 24 warnings
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Removing manual mode could break external Brain workflows
- **Rollback plan:** Revert to 9.77.0 prompt fragments

---

## Execution Log & Reasoning

### 2026-11-08: Unify 100% Brain Turn

- Permanently eliminated manual mode across the entire platform.
- Updated `prompts/fragments/02-role.md` — single autonomous topology via brain_turn.
- Updated `prompts/fragments/19-initialization.md` — single 100% unified autonomous topology.
- Updated `prompts/fragments/06-personas.md` — removed all manual mode courier instructions from Senior Programmer, QA Engineer, Code Reviewer.
- Updated `prompts/fragments/09-hands_protocols.md` — removed all manual mode blocks from discovery, implementation, and combined task templates.
- Updated `agents/cognitive-executor.md` — removed True Manual Mode courier protocol, manual mode line, manual vs autopilot section.
- Updated `AGENTS.md` — clarified no-ferrying applies to all modes.
- Updated `README.md` — single topology documented.
- Updated `docs/architecture.md` — removed True Manual Mode section.
- Bumped version to 9.78.0 and rebuilt system-prompt.md.
- Updated `tests/test_prompt_sync.py` — replaced test_dual_mode_topology_separation with test_unified_brain_turn_topology.
- Added ADRs to agents/DECISIONS.md and prompts/fragments/DECISIONS.md.
- Updated CHANGELOG.md with 9.78.0 entry.
- Full test suite: 826 passed, 24 warnings. Docs-sync OK. Diff-check clean.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `494f2a39a6f6723f71e27c7919b152365b131102`
<!-- END_GIT_DIFF -->
