# Kanban Board Manager Guide

## Purpose

This guide onboards board managers to the HQ Kanban/planning system and maps canonical Kanban essentials to the current implementation. It is the operating reference for visualizing workflow, limiting WIP, managing flow, enforcing explicit policies, running feedback loops, and evolving the process.

## Canonical essentials

1. Visualize the workflow.
2. Limit work in progress.
3. Manage flow.
4. Make policies explicit.
5. Implement feedback loops.
6. Improve collaboratively and evolve experimentally.

## Current system map

- Planner MCP: derived index over `tasks/` Markdown; task files remain the source of truth.
- Dashboard: board lanes, task modal, 14-day load view, and measured-hours view. See `mcp-planner-server/static/index.html:215-216` (chart containers), `:674-690` (14-day load chart), `:703-732` (measured-hours chart).
- Task files: Kanban state, metadata, acceptance criteria, verification evidence, execution log, and factual diff. See `mcp-planner-server/server.py:187` (`_parse_task_file`).
- AGENTS protocol: validation, task lifecycle, WIP expectations, QA/review gates, and closure rules. See `mcp-planner-server/server.py:887-891` (WIP ceiling check), `:878-883` (QA budget check).

## Gap audit

| Canonical essential | Current implementation | Gap | Evidence |
|---|---|---|---|
| Visualize workflow | Backlog, in-progress, QA, completed, and archive lanes | Partial: lane visualization exists, but flow history is limited | `mcp-planner-server/static/index.html:215-216` |
| Limit WIP | WIP expectations and QA queue cap are documented | Partial: global default and per-project override need explicit policy and dashboard visibility | `mcp-planner-server/server.py:887-891` |
| Manage flow | Measured-hours and 14-day load views exist | Missing: CFD, control chart/cycle-time scatterplot, and WIP aging | `mcp-planner-server/static/index.html:674-732` |
| Explicit policies | AGENTS and task templates encode lifecycle rules | Partial: board-level policies are not centralized | This guide and `docs/kanban-policies.md` |
| Feedback loops | QA and review gates exist | Missing: retrospective artifact and board-manager onboarding | This guide and `docs/retrospectives/TEMPLATE.md` |
| Evolve collaboratively | Task execution logs and changelog exist | Partial: no standardized retrospective artifact | `docs/retrospectives/TEMPLATE.md` |

## Metrics

Track and review these flow metrics:

- Lead time.
- Cycle time.
- Throughput.
- WIP count.
- Blocked time.
- Cumulative flow by lane.
- Cycle-time distribution and outliers.

Prefer flow metrics over utilization metrics. High utilization is not a substitute for predictable flow.

## Ceremonies

- Daily stand-up: inspect blocked items first, then WIP aging, then flow blockers.
- Review: compare completed work against Definition of Done and flow metrics.
- Retrospective: use `docs/retrospectives/TEMPLATE.md` and convert approved actions into backlog tasks.

## Blocked items and swarming

Blocked items are first-class board state, not background noise.

Required task metadata:

```markdown
**Blocked:** no
**Blocked reason:** none
**Swarm:** none
```

When blocked:

- Set `**Blocked:** yes`.
- Record a concise `**Blocked reason:**`.
- Add `**Swarm:** <owner or task>` when swarming is active.
- Escalate after one business day without movement.
- Prefer swarming over starting new work when a blocked item threatens flow.

Dashboard and planner integration for these fields is planned for the next implementation phase. This phase establishes the metadata contract and operating rules.

## Definition of Done baseline

A task is not done unless:

- Required tests pass.
- `lint_task_file` passes.
- Verification evidence is recorded.
- `CHANGELOG.md` is updated when required.
- Living folder docs are updated for behavior or contract changes.

## Common mistakes to avoid

- Running a board without WIP limits.
- Adding too many columns.
- Ignoring blocked items.
- Never changing the process.
- Measuring utilization instead of flow.

## Onboarding checklist

- [ ] Read this guide and `docs/kanban-policies.md`.
- [ ] Confirm the active project's WIP limit.
- [ ] Identify current blocked items.
- [ ] Review WIP aging and flow metrics.
- [ ] Run or schedule the next retrospective.
