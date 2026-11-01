# Kanban Board Policies

## Scope

These policies apply to the HQ Kanban/planning system. Task files in `tasks/` remain the source of truth; the Planner MCP is a derived index and dashboard.

## Columns and WIP

- Default global WIP limit: 3 concurrent in-progress tasks.
- Per-project override is optional and must be documented in the project's board notes or task metadata.
- Do not start new work when the WIP limit is reached unless a blocked item is being swarmed.
- QA holds at most 3 tasks awaiting review.

## Entry and exit criteria

- Backlog: approved or accepted work not yet started.
- In progress: actively worked and within WIP.
- QA: implementation complete with staged diff and injected verification evidence.
- Completed: Manager-approved closure and commit completed.
- Archive: compacted historical record.

## Blocked items

- Blocked state must be explicit in task metadata.
- Every blocked item needs a reason and an owner.
- Blocked items older than one business day require escalation.
- Swarming takes priority over starting unrelated work.

## Blocked/swarm metadata contract

```markdown
**Blocked:** no | yes
**Blocked reason:** none | <concise reason>
**Swarm:** none | <owner or task>
```

These fields are advisory in this phase. Planner and dashboard enforcement will be added in a later phase.

## Definition of Done

- Build, test, and lint pass with exit code 0.
- `lint_task_file` passes on the active task file.
- Verification evidence is recorded.
- Required documentation is updated.
- No unresolved rule violations remain.

## Feedback loops

- Daily stand-up reviews blocked items, WIP aging, and flow blockers.
- Review compares outcomes against Definition of Done and flow metrics.
- Retrospective uses `docs/retrospectives/TEMPLATE.md`.
- Approved retrospective actions become backlog tasks.

## Change control

- Process changes must be documented in this file or the board-manager guide.
- Experimental changes should be time-boxed and reviewed at the next retrospective.
- Revert process changes that do not improve flow or predictability.
