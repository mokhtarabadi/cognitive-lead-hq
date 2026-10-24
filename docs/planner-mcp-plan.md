# Planner MCP v1 — Design & Implementation Plan

## 1. Problem & scope

The Manager reports entering autopilot unintentionally, running many tasks back-to-back, and then finding QA/testing of accumulated changes hard — work becomes complex and scattered. The brainstorming session (7 seats: Architect, UI/UX Designer, Senior Programmer, Project Planner, Sprint Strategist, QA Engineer, Code Reviewer) ranked **O1** as the winning option:

> Keep `tasks/` Markdown as the single source of truth. Add a **thin Planner MCP** server plus a **local dashboard** that enforces QA/capacity gates. Defer external integrations (GitHub, Telegram, Asana, Plane) until local planning and transition rules work reliably.

This plan records that decision and the v1 execution path so planning can continue manually with full context.

## 2. Ground facts (verified, do not re-derive)

| Area | Fact |
|------|------|
| Repo type | Documentation + MCP servers only. No product code. |
| Task truth | Markdown files in `tasks/{backlog,in-progress,qa,completed,archive}`. 318 archived, 6 completed active. |
| Lifecycle enforcement | Prompt rules, not code: WIP ≤ 3, QA queue cap 3, `git mv` for transitions, `lint_task_file` for structure, ZAC (no agent commit/push). |
| MCP servers | Python stdlib-first singletons on loopback: context 8102, memory 8103, decisions 8104, brain 8105, telegram 8106, lint 8101, blowsh 8107 (Docker). Each has `pyproject.toml` + `uv.lock` + `.venv`. |
| OpenChamber | Local npm package `@openchamber/web` running as a session UI. Precedent: `tools/prompt-composer/index.html` is a static single-file UI. |
| GitHub | CLI authenticated; `gh` used for issues. Projects v2 is GraphQL-only, 5000 points/hour per user. |
| Asana | 150 req/min free, 1500 paid, `Retry-After` on 429, 50 concurrent GET / 15 concurrent write caps. |
| Plane | Self-host via docker-compose, 2 cores / 4 GB min, 12 free seats. |
| New task counter | Last used task ID: 331 (`tasks/completed/331-drop-overlong-replay-ids.md`). New planner task would be `0332`. |

## 3. Decisions (final, from brainstorming report)

| # | Decision | Reason |
|---|----------|--------|
| D1 | `tasks/` Markdown remains the single source of truth. Planner views are derived indexes. | Existing lifecycle; no-monolithic-state constraint; no competing task store. |
| D2 | v1 = Planner MCP + local dashboard over canonical Markdown. External integrations deferred to v2/v3. | Direct QA-budget enforcement; no unverified integration or lifecycle fit. |
| D3 | Autopilot QA budget: max **1 unresolved QA/review task** (general WIP ceiling stays 3). | Prevents unattended accumulation without changing general policy. |
| D4 | Only planner tooling may change task state. Every transition passes `lint_task_file`. | Prevents divergence between planner view and task files. |
| D5 | v1 builds: read model, dependency/capacity checks, guarded transitions, local dashboard. | Fixes capacity, dependency ordering, deadlines/milestones, and one dashboard. |

## 4. Out of scope for v1 (explicit)

- Asana or Plane synchronization, Telegram task mutation, multi-user permissions.
- Automatic task creation without Manager approval.
- General-purpose Gantt, webhooks/inbound events, git commit/push by agents.

## 5. Data model (additive, additive-only changes to existing task files)

Existing task header stays. New optional header fields:

```
**Estimate:** <hours>          # work estimate, used for capacity sums
**Milestone:** <id>            # links to tasks/milestones/<id>.md
**Deadline:** YYYY-MM-DD       # sortable
**Depends on:** <id>, <id>     # prerequisite task IDs
```

Milestones get their own file: `tasks/milestones/M24-<name>.md` (context, target date, owning task IDs).

A planner **read model** lives in `tasks/.plan/index.json` (gitignored, regenerated from Markdown on every planner invocation — never hand-edited). It contains task ID, source path, status, lane, estimate, milestone, deadline, depends_on, QA status, and derived fields (`blocked`, `due_soon`, `qa_pending`).

## 6. Architecture

- **`mcp-planner-server/`** (new singleton, port 8108, same pattern as other MCP servers): tools only — `plan_status`, `plan_propose` (decompose a goal into tasks + estimates, **writes nothing**), `plan_materialize` (writes task files after Manager approval), `claim_next` (guarded claim: checks dependencies, WIP, QA budget), `qa_budget` (count of QA-pending tasks), `milestone_status`.
- **Local dashboard**: served by the MCP on 8108, static HTML+JS, Kanban lanes, QA queue bar, capacity meter (default 20 h/week), milestone timeline, blocker list (`blocked_by`). SSE refresh. Accessible states (loading, empty, disconnected, stale-data), keyboard nav, light/dark.
- **Rollback**: disable planner, return to `tasks/` Markdown workflow. No destructive migration — planner reads only.

## 7. Risks & rollback

| Risk | Mitigation |
|------|------------|
| Planner becomes a second divergent status source | Task files canonical; planner is read-only index; external systems never write status independently |
| Overcommitment persists | `claim_next` blocks on QA budget + dependencies; over-capacity plans rejected/blocked before QA |
| Unattended autopilot accumulates work | Max 1 QA/review task + batch (default 3) + mandatory review packet |
| Direct repo edits bypass planner | Gate is soft by design; rollback = remove planner, Markdown still works |

## 8. Execution phases

### Phase A — Spec & plan task (current)
- Create task file `0332-planner-mcp-v1.md` in `tasks/backlog/` with this document as context.
- Specify additive task/milestone metadata fields, capacity input, queue-gate rules.
- Deposit the brainstorming report (7 seats) as the task's `## Brainstorming Result` section.

### Phase B — Planner MCP build & test
- Scaffold `mcp-planner-server/` (`pyproject.toml`, `uv.lock`, `server.py`, singleton launch).
- Implement read model from existing Markdown tasks.
- Implement `plan_propose` (no writes), `plan_materialize` (writes task files), `claim_next` (guarded), `qa_budget`, `milestone_status`.
- Offline unit tests for guarded transitions, dependency cycles, capacity math, stale-data handling.
- `lint_task_file` green; full suite green (except pre-existing `test_system_prompt_split_assemble_round_trip`).

### Phase C — Dashboard & rollout
- Standalone local dashboard on 8108 with accessible states.
- Verify autopilot blocking, rollback, unchanged operation when planner unavailable.
- Smoke test: `opencode mcp list` (all servers connected), dashboard reachable.

## 9. Parameters to confirm before Phase B

| Parameter | Suggested default | Manager decision |
|-----------|------------------|------------------|
| Weekly capacity (hours) | 20 h | ? |
| Batch size per autopilot cycle | 3 tasks | ? |

## 10. Brainstorming result (verbatim summary)

**Winner:** O1 — thin Planner MCP and standalone local dashboard over canonical task Markdown. Driven by tradeoffs T1 (Markdown-primary vs external-platform-primary) and T3 (autopilot QA budget 1 vs general 3).

**Winner path:** O1 with minimum v1 = capacity estimates + weekly capacity input, dependency validation + ordering, deadlines + milestones, single dashboard, conversational plan proposals requiring approval before task creation, transition gates. Autopilot: one active task + one unresolved QA/review task. General WIP/QA ceilings stay at 3.

**Explicitly out of v1:** Asana/Plane sync, Telegram task mutation, multi-user permissions, automatic task creation without approval, general Gantt, external primary task store.

**First three steps:**
1. Specify additive task/milestone metadata, capacity inputs, queue-gate rules (no migration).
2. Build/test Planner MCP read model, dependency/capacity checks, guarded task transitions against existing Markdown.
3. Build local dashboard, verify accessible states, autopilot blocking, rollback, and planner-unavailable operation.

## 11. Manual-mode handoff

This document is the complete context for manual planning. No subagent, no autopilot, no relay needed to continue. The next concrete action is to create `tasks/backlog/0332-planner-mcp-v1.md` using this document as the `## Source Context` and then begin Phase A execution.
