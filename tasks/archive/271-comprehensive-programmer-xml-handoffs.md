# Task 271: Generate Comprehensive Programmer XML Handoffs

**File:** `tasks/completed/271-comprehensive-programmer-xml-handoffs.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Source Context

## Goal

Make the Senior Programmer seat generate complete, executable `<hands_implementation_task>` XML handoffs that preserve exact code, repository-specific instructions, verification commands, acceptance criteria, and edge cases without placeholder collapse.

## Manager's Notes

The Programmer currently emits generic placeholders and omits code samples or exact instructions. Improve the task-generation contract and its tests. External agent-handoff guidance supports explicit context, state, contracts, and observable acceptance criteria. Execute the approved improvement through the Brain in locked autopilot and reuse manager decisions directly.

## Local TODOs

- [ ] Obtain a Brain-approved implementation plan under the same task history
- [ ] Replace the generic implementation template with an exact, comprehensive XML contract
- [ ] Require complete code samples and repository-specific instructions in generated handoffs
- [ ] Add regression coverage for completeness, exactness, and absence of placeholder collapse
- [ ] Run targeted tests, prompt synchronization checks, task lint, and Markdown lint
- [ ] Update verification evidence and execution reasoning
- [ ] Update `CHANGELOG.md`
- [ ] Stage the factual diff and transition the task to QA

## Acceptance Criteria

- [x] The Senior Programmer contract requires a complete `<hands_implementation_task>` payload with exact file paths, code samples, instructions, acceptance criteria, verification commands, and edge cases
- [x] The generated handoff contract forbids placeholder-only instructions, omitted code, vague file references, and contradictory guidance
- [x] Regression tests prove that comprehensive XML content and concrete code samples survive task generation
- [x] The generated system prompt remains synchronized with its source fragments
- [x] Targeted tests, task lint, and Markdown lint pass with exit code 0
- [x] `CHANGELOG.md` records the structural prompt change

## Verification Evidence

- **Test command:** rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml pytest tests/test_prompt_sync.py tests/test_brain_bridge.py tests/test_golden_cases.py -q
- **Expected result:** All targeted tests pass with exit code 0
- **Actual result:** 268 passed in 1.59s (3 new regression gates green; assembler round-trip gate confirms shipped prompt matches fragments)
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; a raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true:

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence`; do not defer box-checking to a closure task.

## Risk & Rollback

- **Risk:** A stricter template may inflate routine handoffs or conflict with existing golden snapshots.
- **Rollback plan:** Revert only the prompt/template and regression-test changes, regenerate the system prompt, and rerun the targeted suite before restoring the previous handoff format.

---

## Execution Log & Reasoning

- Initial investigation identified the root cause in the generic Senior Programmer implementation template and its explicit instruction to omit full code blocks.
- External research favored explicit handoff context, state, contracts, and observable acceptance criteria.
- Brain plan verdict (planning-gate `brain_turn`, same task history): replace the code-block ban with an exact comprehensive-handoff contract in the implementation template, add regression tests, regenerate the prompt, bump the version pin, verify, update the changelog, stage, and move to QA. Seat routing: Software Architect owns the contract, Senior Programmer owns checklists and verification; Designer skipped (no interface change). Brainstorm: not required — single-domain, reversible prompt fix. Manager replied "Approved".
- Implementation: replaced the `ORCHESTRATOR AUTHORING RULE` in `prompts/fragments/09-hands_protocols.md` with a comprehensive executable-handoff contract (exact paths, complete code samples or unified diffs, full commands, named skills with reasons, per-step verification, explicit acceptance criteria and edge cases, placeholder ban); bumped `<system_version>` to 9.46.0; regenerated `system-prompt.md`; updated the version pin and added regression gates in `tests/test_prompt_sync.py`.
- Verification: targeted `rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml pytest tests/test_prompt_sync.py tests/test_brain_bridge.py tests/test_golden_cases.py -q` → 268 passed, exit 0; full suite → 689 passed, 10 warnings, exit 0; `check_docs_sync.py` → docs-sync OK; `lint_task_file`, `lint_markdown CHANGELOG.md`, `lint_system_prompt_sync` all pass.
- QA verdict (Brain QA turn, same task history, diff attached): VERDICT: QA_PASSED — cites confirm the contract, regenerated prompt, tests, version pin, and changelog entry.
- Review verdict (Brain review turn): PO_REVIEW_PENDING — technical approval, no blocking defects; one low wording note and two later recommendations recorded.
- Manager accept quote (2026-09-23): "Approved for closure, resume goal". Closure: file moved to `tasks/completed/`, status set to closed, header synced.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `219c1ebff4876ceb06a3599cb74f037aecbb93c1`
<!-- END_GIT_DIFF -->
