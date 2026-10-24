# Task 340: System prompt integration for Planner MCP and daily pacing protocol

**File:** `tasks/backlog/0340-system-prompt-planner-protocol-integration.md`
**Source:** manager
**Type:** feature
**Status:** open
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

- [ ] Identify the appropriate prompt fragment (e.g. `prompts/fragments/09-hands_protocols.md` or a new/existing registry section) to document Planner MCP tools and Daily Pacing Protocol
- [ ] Add the planner singleton (`127.0.0.1:8108`), `sprint_daily_agenda`, `claim_next`, and `sprint_check_daily_quota` rules
- [ ] Run `python3 scripts/prompt-build/assemble_system_prompt.py`
- [ ] Bump `<system_version>`
- [ ] Run `rtk test uv run --with pytest python -m pytest tests/test_prompt_sync.py -q`
- [ ] Run `python3 scripts/check_docs_sync.py`
- [ ] Update `CHANGELOG.md` under `### Added`

## Acceptance Criteria

- [ ] Planner MCP and Daily Pacing Protocol are documented in `prompts/fragments/`
- [ ] `system-prompt.md` is reassembled and carries the bumped `<system_version>`
- [ ] `tests/test_prompt_sync.py` passes with exit code 0
- [ ] `scripts/check_docs_sync.py` exits 0 with `docs-sync: OK`
- [ ] No prompt split/assemble round-trip drift introduced

## Verification Evidence

- **Test command:** `rtk test uv run --with pytest python -m pytest tests/test_prompt_sync.py -q`
- **Expected result:** All prompt sync tests pass
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

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

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

<!-- END_GIT_DIFF -->
