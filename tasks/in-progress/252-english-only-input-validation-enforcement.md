# Task 252: English-Only Reasoning Plus Input-Validation Enforcement

**File:** `tasks/in-progress/252-english-only-input-validation-enforcement.md`
**Source:** manager
**Type:** improvement
**Status:** open
**Mode:** autopilot-locked

## Goal

Enforce English-only thinking, reasoning, and responses plus the priority-one input-validation pipeline (validate, translate, enrich, refactor, execute with typo and voice-to-text correction) in the cognitive executor and the system prompt.

## Manager's Notes

- The agent must never respond, think, or reason in any language other than English. All thinking, reasoning, and responses stay one hundred percent English even when the Manager writes in Persian.
- The input-validation pipeline is priority one for every non-English or noisy input: validate, translate to English, enrich, refactor, then execute. Typo correction applies, especially for voice-to-text artifacts.
- Enforcement must land in both the cognitive executor and the system prompt fragments so the rule survives regeneration of the built prompt.
- Full-auto standing order applies: zero questions, Brain consulted on every step, reviewer approval counts as closure approval.

## Local TODOs

- [ ] Discovery: map existing language rules, validation-phase pipeline, prompt-refactor skill, executor input handling
- [ ] Brain plan: enforcement points in fragments plus executor plus rebuilt system prompt
- [ ] Implement with TDD where code changes apply (pure validators get unit tests)
- [ ] Rebuild system prompt, verify version bump and fragment sync
- [ ] Full suite exit 0, CHANGELOG, lint, stage, QA move

## Acceptance Criteria

- [x] No non-English prose remains in agent-facing prompt rules except explicitly quoted source material
- [x] Input-validation pipeline (validate-translate-enrich-refactor-execute with typo and voice-to-text correction) is a mandatory executor step for non-English or noisy inputs
- [x] System prompt rebuilds byte-deterministically with version bump and fragment sync check passing
- [x] Full test suite passes with exit code 0

## Verification Evidence

- **Test command:** rtk test uv run --with pytest --with mcp[cli]==1.30.0 --with pathspec --with pyyaml pytest tests/ -q
- **Expected result:** all tests pass, exit code 0
- **Actual result:** 499 passed, 10 warnings
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** prompt rebuild changes shipped prompt text; fragment drift breaks sync check
- **Rollback plan:** revert feature commit hash; system prompt rebuild is deterministic from fragments

---

## Execution Log & Reasoning

TDD red-green: wrote `tests/test_input_validation_pipeline.py` (6 tests) first — 4 failed pre-fix (manager-language wording present, validation after topic shift, prompt-refactor absent from executor), 2 passed (stage order, never-another-language line). Discovery found the rules existed as prose but contradicted each other (clarify in Manager language vs always English) with zero test gates. Fix: reordered 05 validation gate to step 0 ahead of topic shift (now 0.5), replaced all three manager-language clarification lines with simple English, hardened 13-constraints rule with quoted-source-only exception plus precedence, fixed conventions/AGENTS/executor halt lines, added prompt-refactor to executor matrix, bumped version 9.39.0, rebuilt prompt twice byte-identical with zero manager-language remnants. Extended `tests/test_prompt_sync.py` with 3 shipped gates. Suite 499 passed exit 0 via rtk (6 new pipeline + 3 new sync gates on top of 491, minus none). Standing full-auto order applies; memory `manager/english_only_reasoning_responses` stored.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
