# Task 221: Dedicated testing-strategy skill (TDD enforcement)

**File:** `tasks/archive/221-testing-strategy-skill-tdd-enforcement.md`
**Source:** manager
**Type:** feature
**Status:** superseded
**Superseded-By:** 224-readme-roadmap-trio-meta
**Superseded-At:** 2026-09-13

## Source Context

## Goal

Create a `testing-strategy` skill template enforcing TDD and coverage gates so OpenCode writes tests before or alongside implementation code.

## Manager's Notes

README roadmap item 3, verbatim: "Dedicated `testing-strategy` Skill: Create a template enforcing Test-Driven Development (TDD) or strict coverage thresholds, ensuring OpenCode writes tests before or alongside implementation code." Project goal reminder (Manager, verbatim core): the project's main goal is the strictest linters/tools that stop AI hallucination — every skill must serve it. Research: TDAD paper (arXiv:2603.17973 — TDD prompting alone raised regressions 9.94%; agents need targeted test context, not procedural lectures); agentic-PR study (arXiv:2607.18057 — 50.4% of agentic code PRs ship zero tests; error-handling miss rates 81-86%); JetBrains finding-tests skill + target-coverage roadmap. No prior manager ruling found in local decision store. Skill must: tests-first order (red-green-refactor), per-PR diff-coverage threshold, mandatory error-path tests, test-placement map (no guessing), no-merge-without-tests rule. Deliverable: `skill-templates/testing-strategy/SKILL.md` + registry entry (registry-consistency test enforces both).

## Local TODOs

- [ ] Initial codebase exploration
- [ ] Write testing-strategy SKILL.md + registry entry
- [ ] Extend registry consistency tests
- [ ] Verify functionality

## Acceptance Criteria

- [ ] `skill-templates/testing-strategy/SKILL.md` exists with TDD order, coverage gates, error-path rule
- [ ] Registry lists the skill and consistency tests pass
- [ ] Full suite passes exit 0

## Verification Evidence

- **Test command:** full pytest suite + docs-sync
- **Expected result:** all pass, exit 0
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

- **Risk:** over-strict gates block trivial changes
- **Rollback plan:** Lite-Mode exemption clause inside the skill; revert template + registry line

---

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
