# Task 250: RTK Output-Trimming Structural Wiring

**File:** `tasks/completed/250-rtk-output-trimming-structural-wiring.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Mode:** autopilot-locked

## Goal

Make RTK output-trimming usage structural instead of advisory so agents use it on every verification run.

## Manager's Notes

Full-automatic mode applies (stored order `manager/full_automatic_mode`, zero questions). Manager found ~0% RTK usage across recent tasks and ordered: discover the reason and fix it. Discovery (read-only subagent, verified): `rtk` 0.49.0 binary live at `~/.local/bin/rtk`; mandate exists only as RULE 3b in `prompts/fragments/09-hands_protocols.md` plus `system-prompt.md`; no RTK skill exists; `agents/cognitive-executor.md` never names RTK; task files prescribe raw `uv run ... pytest` commands; no enforcement gate checks actual usage. Proven: `rtk test <suite>` collapses the 491-test verdict to 3 lines with exit code preserved. This task wires the mandate into the executor protocol, the task template, and project memory. Scope is wiring plus docs only; no behavior change to any MCP server.

## Local TODOs

- [x] Map RTK mandate points with Brain (fragment, executor matrix, template, memory)
- [x] Add RTK row to the executor Skill Auto-Loading Matrix or protocol section
- [x] Update the task-generator template Verification Evidence command to `rtk test` prefix
- [x] Store the RTK-first rule in project memory
- [x] Run the full suite via `rtk test` with exit code 0
- [x] Update CHANGELOG via Parse-Then-Append
- [x] Lint the task file, stage, move to qa, re-stage

## Acceptance Criteria

- [x] Executor protocol names RTK as the default verification runner
- [x] New task files prescribe `rtk test` prefixed verification commands
- [x] Project memory holds the RTK-first rule for cross-session stickiness
- [x] Full test suite passes with exit code 0 via `rtk test`

## Verification Evidence

- **Test command:** `rtk test uv run --with pytest --with 'mcp[cli]==1.30.0' --with pathspec --with pyyaml pytest tests/ -q`
- **Expected result:** all tests pass, exit code 0
- **Actual result:** 502 passed, 10 warnings in 4.31s
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** prompt rebuild needed if the mandate moves into the shipped system prompt.
- **Rollback plan:** revert the feature commit hash; wiring is docs-only so rollback is trivial.

---

## QA & Review Record

- Brain QA Engineer verdict: QA_PASSED (visible scope; truncation caveat noted, no visible defect).
- Code Reviewer verdict: APPROVED + PO_REVIEW_PENDING, zero blocking issues (U3 indentation note verified locally — reviewer misread, no fix needed).

## Execution Log & Reasoning

Plan approved implicitly under the full-auto standing order (zero questions; Brain Architect advisory plan, no pre-approval procedure). Discovery correction: the task-generator template carries no raw command (placeholder `[exact command]` only) — raw prescribers were individual task files, the executor example, and normative docs. TDD: 3 new tests in `tests/test_prompt_sync.py` written first (RED: 3 failed for the right reason; one self-inflicted IndentationError from a no-op edit fixed in the test file). GREEN changes: RULE 3b extended operationally (first run RTK, prefixed command recorded, raw only post-failure); executor Verification Runner policy added after the Observe rule plus RTK-prefixed evidence example (other verification sections checked — generic, no contradiction); template placeholder changed to `rtk test [exact command]` in both templates with a runner rule; memory entry overwritten canonically; 4 normative prescribers normalized (setup, brain-bridge, workflow-upgrade, upgrade-runbook memory); version 9.39.0 to 9.40.0 with byte-identical double rebuild. Focused suite 8/8, full suite 502 passed exit 0 via `rtk test` (3-line verdict). Existing executor content asserts untouched (edits additive; full suite green proves it).

Review note on U3 (template indentation): verified locally — line 118 keeps its original 4-space indent and line 179 stays at column 0; only blockquote runner-rule lines were added after each heading. The reviewer misread the diff; no fix needed.

Approved for closure (standing Manager order: Code Reviewer technical APPROVED counts as Manager approval; reviewer returned APPROVED + PO_REVIEW_PENDING with zero blocking issues).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `56e443dca14a27bb2a66d9316b7e09f0c7eb69bb`
<!-- END_GIT_DIFF -->
