---
name: brain-orchestration
description: How the Cognitive Lead Brain/Hands platform works - participants, seven seats, stages, modes, approval gates, context maps, and output-recovery contracts.
---

# Brain Orchestration

## Authoritative Contract

The deployed Brain Bridge runbook and stage manifest are the authoritative contract. This skill distills them for downstream harness projects. On any conflict, the deployed contract wins.

## Participants

- Manager: human supervisor and approval gatekeeper — approves plans, answers Relay questions, issues "Approved for closure" / "Close task" verbatim; owns remote pushes and service restarts.
- Brain: the Cognitive Lead AI orchestrator persona set — produces plans and XML task blocks; no direct file, terminal, or web access.
- Hands: the local Cognitive Executor agent — executes XML tasks, runs verification, stages via approved mechanisms under Zero-Autonomous-Commit (ZAC).
- Discovery subagents: read-only context gathering, up to 4 concurrent.

## The Seven Seats

Software Architect (system design, contracts, roadmaps), UI/UX Designer (design system, a11y), Senior Programmer (implementation task authoring, orchestration), Project Planner (Kanban file state), Sprint Strategist (scope, capacity, MoSCoW), QA Engineer (adversarial verdicts: QA_PASSED / QA_REJECTED), Code Reviewer (blueprint and standards audit: APPROVED, APPROVED_WITH_CHANGES, REJECTED_NEEDS_FIXES, PO_REVIEW_PENDING). Design work uses Software Architect and UI/UX Designer; programming uses Senior Programmer; brainstorming convenes all seven as a report; verdicts and closure route through QA Engineer, Code Reviewer, and the Manager.

## Stages and Routing

brain_turn(stage=...) selects the persona-scoped system prompt from the deployed stage manifest, the single source of stage routing in harness projects. Admitted stages: plan, implement, qa, review, closure, sprint, planner, brainstorm. Manager-term aliases: "code review" maps to review, "planning" maps to plan. Unknown stages fail loud at preflight.

## Working Method

The 9-step production line: discovery, optional brainstorm (required only when cross-disciplinary AND hard to reverse), blueprint, Manager plan approval, implementation, adversarial QA, code review, PO closure approval, next-task transition. Every planning or verdict turn carries a verified Context-Map (tree report plus context_paths manifest); the Brain plans only from grounded context and returns missing_context otherwise. Seat Check names the requested and skipped seats before every planning turn.

## Modes and Approvals

Manual mode: supervised approvals, the Manager gates each handoff. Autopilot: one plan-approval pause, then chained turns; only Relay questions and hard blockers interrupt. Approval phrases match as English literals only; blanket acknowledgements never count. Approval and closure questions ride the question tool; a required tool reported unavailable pauses with the relay block.

## Output Contracts

Structured blocks (hands_implementation_task, hands_discovery_task, hands_combined_task, failure_report, hotfix) extract from bare XML first and from fenced XML in manual copy-paste mode; a body carrying its own fenced code wraps in four backticks. Oversized brain_turn results arrive as a pointer: the output begins with the [brain-output] marker and names the artifact at output_address; read the artifact and execute xml_blocks when the block count is above zero, otherwise full_output. Pruned or truncated tool output follows the executor's mandatory omitted-content recovery gate: a cache omission is one read_omitted_content call by Content ID or one cheap source re-run; a truncated code-mode return is re-read at the exact range; recovery is bounded to two attempts per payload. The deployed bridge keeps the raw provider text in a per-turn artifact and exposes one deterministic parse helper, so a rejected extraction never hides the Brain's full output; read the artifact and validate with the helper before deciding to re-emit.
