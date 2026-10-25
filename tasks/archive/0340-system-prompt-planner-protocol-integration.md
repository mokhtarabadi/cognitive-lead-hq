# Task 340: System prompt integration for Planner MCP and daily pacing protocol

**File:** `tasks/completed/0340-system-prompt-planner-protocol-integration.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Estimate:** 1.5h
**Sprint:** S26-W43
**Milestone:** M01

## Source Context

### Variant C: Manager (`**Source:** manager`)

## Goal

Integrate the Planner MCP singleton and the Daily Pacing Protocol into the core system prompt fragments (`prompts/fragments/`), reassemble `system-prompt.md`, bump `<system_version>`, and verify full prompt synchronization so that every Cognitive Lead AI session natively recognizes the planner tools and pacing rules.

## Manager's Notes

- Currently, the planner protocol is documented in `agents/cognitive-executor.md`, but the root system prompt should also natively recognize port 8108 and the daily pacing triggers.
- Must follow the prompt assembly pipeline: edit fragments in `prompts/fragments/`, update `manifest.txt` if needed, run `assemble_system_prompt.py`, bump `<system_version>`, and keep `tests/test_prompt_sync.py` and `scripts/check_docs_sync.py` 100% green.
- Language policy must be respected: internal prompt prose stays English-only, while supporting multi-lingual Manager triggers ("کار امروز رو شروع کنیم").

## Local TODOs

- [x] Identify the target fragment: `prompts/fragments/11-execution_workflow.md` (workflow prose, no new top-level tag, so the splitter manifest stays untouched); update `manifest.txt` only if the assembly script requires it
- [x] Add the planner singleton (`127.0.0.1:8108`), `sprint_daily_agenda`, `claim_next`, and `sprint_check_daily_quota` rules, plus the Daily Pacing Protocol triggers
- [x] Run `python3 scripts/prompt-build/assemble_system_prompt.py`
- [x] Bump `<system_version>` 9.64.1 → 9.65.0 and update the pin in `tests/test_prompt_sync.py`
- [x] Run `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/test_prompt_sync.py tests/test_mcp_servers.py -q`
- [x] Run the split→assemble round-trip assertion (`test_system_prompt_split_assemble_round_trip`) and `python3 scripts/check_docs_sync.py`
- [x] Update `CHANGELOG.md` under `### Added`

## Acceptance Criteria

- [x] Planner MCP and Daily Pacing Protocol are documented in `prompts/fragments/`
- [x] `system-prompt.md` is reassembled and carries `<system_version>9.65.0</system_version>`
- [x] `tests/test_prompt_sync.py` and the prompt/splitter tests pass with exit code 0
- [x] `test_system_prompt_split_assemble_round_trip` stays green (byte-identical)
- [x] `scripts/check_docs_sync.py` exits 0 with `docs-sync: OK`
- [x] No prompt split/assemble round-trip drift introduced

## Verification Evidence

- **Test command:** `rtk test uv run --with pytest python -m pytest tests/test_prompt_sync.py -q`
- **Expected result:** All prompt sync tests pass
- **Actual result:** `103 passed` (prompt sync + MCP server suites, includes the split/assemble round trip); `docs-sync: OK`
- **Exit code:** 0
- **Round-trip:** `test_system_prompt_split_assemble_round_trip` must stay green and `scripts/check_docs_sync.py` must print `docs-sync: OK`
- **Version target:** `<system_version>9.65.0</system_version>` (pin updated in `tests/test_prompt_sync.py`)

## Definition of Done

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Editing prompt fragments can introduce assemble/split drift.
- **Mitigation:** Run `assemble_system_prompt.py` and `split_system_prompt.py` round-trip assertions to verify 100% fidelity.
- **Rollback plan:** Revert touched fragment files and `system-prompt.md`.

## Execution Log & Reasoning

Created by Project Planner / Senior Programmer per Manager directive.

**Seat consult (2026-10-24, Manager: "ask project planner and sprint strategist … handle task 340 tonight"):** [Project Planner] GO after four amendments — target fragment named, single test runner, version target pinned, CHANGELOG and round-trip added to the evidence; task is executable as written and depends only on 342, which is closed. [Sprint Strategist] GO tonight — capacity is zero in-progress plus zero QA with room for one review, the task is Must-Do for M01 because it closes the planner loop, and the only real risk is late-session prompt drift, mitigated by running assemble plus the split round-trip and halting on the first drift.

**Implementation:** the protocol landed in `prompts/fragments/11-execution_workflow.md` as a compact block after Step 9 (inside the existing `<execution_workflow>` tag, so `manifest.txt` and the splitter's tag list are untouched). It covers the singleton at `127.0.0.1:8108`, the Kanban-as-source-of-truth rule, `sprint_daily_agenda` on a start-the-day instruction in any language, `claim_next` instead of manual moves with refusals reported, `plan_status`/`qa_budget`, and `sprint_check_daily_quota` → `DAILY_QUOTA_REACHED` → `sprint_stats` then stop, plus the reachability fallback. `<system_version>` goes to 9.65.0 and the pin in `tests/test_prompt_sync.py` follows; `system-prompt.md` reassembled to 109,554 bytes and deployed byte-identical, `mcp-brain` restarted.

**Verification:** 103 passed (prompt sync + MCP servers), exit 0; `test_system_prompt_split_assemble_round_trip` green; `check_docs_sync.py` → `docs-sync: OK`; `grep -c "Planner MCP and daily pacing" system-prompt.md` = 1.

**Autopilot QA/review:** QA → `VERDICT: QA_PASSED` (placement inside the tag, version pin consistency, no protocol contradiction, language policy respected). Reviewer → APPROVED, `PO_REVIEW_PENDING`, no blocking issues.

**Manager closure approval (2026-10-24), verbatim: "Approved for closure".**

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `03549d56a771ae547fb4066c4b603dcd1a680b0d`
<!-- END_GIT_DIFF -->
