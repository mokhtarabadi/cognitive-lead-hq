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
- Dashboard: board lanes, task modal, 14-day load view, and measured-hours view. See `mcp-planner-server/static/index.html:221-222` (chart element refs), `:718` (14-day load label), `:767-850` (CFD/control-chart fetch with unavailable-fallback).
- Task files: Kanban state, metadata, acceptance criteria, verification evidence, execution log, and factual diff. See `mcp-planner-server/server.py:294` (`_parse_task_file`).
- AGENTS protocol: validation, task lifecycle, WIP expectations, QA/review gates, and closure rules. See `mcp-planner-server/server.py:1014` (QA budget check), `:1024` (WIP ceiling check).

## Gap audit

| Canonical essential    | Current implementation                                 | Gap                                                                                                                  | Evidence                                                 |
| ---------------------- | ------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| Visualize workflow     | Backlog, in-progress, QA, completed, and archive lanes | Partial: lane visualization exists, but flow history is limited                                                      | `mcp-planner-server/static/index.html:221-222`           |
| Limit WIP              | WIP expectations and QA queue cap are documented       | Partial: global default and per-project override need explicit policy and dashboard visibility                       | `mcp-planner-server/server.py:1024`                      |
| Manage flow            | Measured-hours and 14-day load views exist             | Partial: CFD/control-chart elements plus fetch wiring with unavailable-fallback exist; verify backend endpoints live | `mcp-planner-server/static/index.html:221-222, :767-850` |
| Explicit policies      | AGENTS and task templates encode lifecycle rules       | Partial: board-level policies are not centralized                                                                    | This guide and `docs/kanban-policies.md`                 |
| Feedback loops         | QA and review gates exist                              | Present: retrospective template plus this guide as onboarding                                                        | This guide and `docs/retrospectives/TEMPLATE.md`         |
| Evolve collaboratively | Task execution logs and changelog exist                | Present: standardized retrospective template; approved actions become backlog tasks                                  | `docs/retrospectives/TEMPLATE.md`                        |

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

## Milestone and sprint flow

Schedule with milestone via `schedule_tasks(project_root, "id:estimate:deadline[:deps[:milestone]], …")` — the single writer for all four header lines, where `-` leaves a value untouched. Claim via `claim_next`, which is blocked while any `tasks/.plan/sprint-*.lock` file exists (delete the file to unlock). Review the week via `sprint_stats` (Monday–Sunday UTC scope, optional `week="YYYY-Www"`) and `sprint_check_daily_quota` (includes the Finished-today count). Group status via `milestone_status` (case-insensitive grouping, first-seen spelling on display).

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

- Build, test, and lint pass with exit code 0.
- `lint_task_file` passes on the active task file.
- Verification evidence is recorded.
- `CHANGELOG.md` is updated when required.
- Living folder docs are updated for behavior or contract changes.
- No unresolved rule violations remain.

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
