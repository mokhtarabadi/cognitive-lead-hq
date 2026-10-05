# Task 299: Brain self-judgment with full brainstorm

**File:** `tasks/in-progress/299-brain-self-judgment-with-full-brainstorm.md`
**Source:** manager
**Type:** chore
**Status:** open
**Risk-Tier:** T1 standard

## Goal

Hand the Brain MCP code to the Brain itself for a full seven-seat brainstorming self-judgment. Answer whether the bridge code is sufficient and covers all parts. Find its own flaws, gaps, and system-prompt mistakes with the top goal of building the strongest anti-hallucination harness. Task the critical findings and fix them together.

## Manager's Notes

Direct Manager order (translated from Persian): "Give the Brain MCP codes to the Brain itself and ask it for brainstorming with ALL members. Are the Brain codes sufficient now, do all parts cover enough? I want it to fix itself, run self-improvement. Find its own flaws and fix them. Main goal: the strongest harness preventing hallucination, that is the most important part. Show me what it does and finds in itself: flaws, gaps, even system-prompt mistakes. Tell it to find them and report; if really critical and vital, task them and we do them together. Stay on autopilot, no need to ask everything."

## Scope

In scope:
- Full seven-seat brainstorming report over `mcp-brain-bridge/` from the Brain itself
- Self-judgment of sufficiency, gaps, flaws, prompt mistakes, anti-hallucination strength
- New task files for critical findings only, fixed together after approval
- Autopilot locked, zero questions except hard blockers and closure gate

Out of scope:
- No implementation until the brainstorm report lands and critical items are tasked
- External repos untouched
- No git add/commit/push by Hands (ZAC holds)
- docs/history, tasks/archive, CHANGELOG history lines immutable

## Local TODOs

- [x] Feed bridge code map to Brain and request full brainstorm report
- [x] Record report verdicts, flaws, gaps, prompt mistakes
- [x] Task critical findings only
- [x] Report back to Manager

## Acceptance Criteria

- [ ] AC1: seven-seat brainstorm report recorded in task file
- [ ] AC2: sufficiency verdict plus ranked flaw list recorded
- [ ] AC3: critical findings tasked, non-critical left as report
- [ ] AC4: autopilot lock recorded, zero mid-task questions asked

## Verification Evidence

- **Test command:** pending (discovery phase, no code changes)
- **Expected result:** pending
- **Actual result:** pending
- **Exit code:** pending

## Definition of Done

- [ ] Brainstorm report plus verdicts recorded
- [ ] Critical findings tasked
- [ ] `lint_task_file` passes on the active task file
- [ ] No code changed in this phase

## Risk & Rollback

- **Risk:** discovery-only phase, no code risk
- **Rollback plan:** no changes made, nothing to roll back

---

## Execution Log & Reasoning

- Seat Check: seven-seat brainstorm explicitly ordered by Manager → all seats requested, none skipped. Research plus code-map domains ride along inside the brainstorm.
- Brainstorm: required — Manager explicitly requested full brainstorm plus cross-disciplinary self-judgment.
- Prompt-refactor applied: translated Persian direct order to technical English, structured as discovery-first chore with task-only-critical rule.
- Autopilot locked per Manager order for end-to-end run with zero questions except hard blockers and closure gate.
- Brainstorm report 2026-10-06 VERDICT: BRAINSTORM_COMPLETE. All seven seats opined. Selected path O1 anti-hallucination harness first, then O2 slice split. Conflicts resolved: strictness wins for QA plus Reviewer, sliced plan wins for Planner plus Strategist, correctness wins over cache speed, verbose errors only on error paths.
- Sufficiency verdict: bridge sends correctly but does not yet guarantee anti-hallucination. Hub is a 3626-line monolith with triple session state, lenient XML repair, silent cap cuts, unverified Responses parity.
- Critical must-task list: C1 strict XML and verdict gate rejecting unmarked repair. C2 attach precedence with visible cut signals at per-file and total caps. C3 single session plus history contract with one bind source and bound markers. C4 Responses API parity matrix for file inputs, inline markdown, retrieval chunks, error mapping. C5 cache correctness with explicit eviction and collision tests, default safe-off until proven. Should-tasks: C6 hub slice split behind ports, C7 Hands-facing error rewrite with correlation IDs.
- Critical findings tasked as 300 through 304 in tasks/backlog/.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
