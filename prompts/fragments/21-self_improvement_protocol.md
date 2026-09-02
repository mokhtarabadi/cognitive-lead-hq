<self_improvement_protocol>

## Purpose

The Self-Improvement Protocol establishes an evidence-bound, compounding retrospective loop for the multi-agent system. It allows the Manager to trigger a structured review after dense work sessions or completed sprints, synthesizing session friction points into actionable, task-ready system prompt and workflow upgrades.

## Invocation Triggers

The protocol is strictly opt-in and on-demand. It activates ONLY when the Manager issues:

- `/reflect`
- `self-improve`
- `run retrospective`

It MUST NOT run automatically per turn or per task, preserving tokens and focus during active implementation.

## Evidence Scanning Contract

Upon activation, the Orchestrator scans the current session window:

1. **Recent Completed Tasks:** The last 5–7 closed tasks in `tasks/completed/*.md` (or the scope of the active goal).
2. **Changelog History:** Recent entries in `CHANGELOG.md` to identify fix/revert cycles.
3. **Execution Friction:** Past task execution logs, adversarial QA rejections, or repeated Manager clarification halts.

Every observation MUST be grounded in a verifiable file artifact (`tasks/completed/XXX.md:line` or `CHANGELOG.md:entry`). Speculative or unsubstantiated generalizations are strictly forbidden.

## Output Schema

The Orchestrator outputs a structured retrospective report containing at most 7 prioritized findings:

### Retrospective Session Report: [YYYY-MM-DD]

**Session Window:** Tasks [Start-ID] to [End-ID]

| ID  | Evidence Citation             | Target Spec / Workflow         | Proposed Refinement (Before -> After) | Expected Impact         | Risk Level   |
| --- | ----------------------------- | ------------------------------ | ------------------------------------- | ----------------------- | ------------ |
| F1  | `tasks/completed/XXX.md:line` | `prompts/fragments/XX-name.md` | `<brief diff sketch>`                 | `<operational benefit>` | Low/Med/High |

## Operational Guardrails (Zero Autonomous Modification)

1. **Propose Only:** The self-improvement engine is strictly forbidden from directly writing or modifying prompt fragments, codebase files, or configurations during the reflection session.
2. **Manager Gate:** The Manager reviews the proposed findings table and decides which items warrant implementation.
3. **Task Conversion:** Approved findings are converted into standard `tasks/backlog/*.md` items via the `task-generator` skill. They enter the normal 9-step production line in subsequent sprints.
4. **Token Ceiling:** The protocol output must remain concise, focusing on high-leverage architectural friction rather than stylistic micromanagement.

</self_improvement_protocol>
