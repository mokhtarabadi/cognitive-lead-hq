# Task 0362: Kanban board manager essentials — close gaps vs canonical Kanban practices

**File:** `tasks/qa/0362-kanban-board-manager-essentials-close-gaps.md`
**Source:** manager
**Type:** improvement
**Status:** open
**Submitted:** 2026-10-31T11:56:12Z

## Goal

Align the HQ Kanban/planning system (Planner MCP + dashboard + AGENTS protocol) with the canonical Kanban board-manager essentials identified via deep research (visualize workflow, limit WIP, manage flow, explicit policies, feedback loops, evolve collaboratively), closing the documented gaps: no Cumulative Flow Diagram, no control chart / cycle-time scatterplot, no WIP-aging view, no blocked-item swarming support, no retrospective artifact, no board-manager onboarding guide, and no Definition-of-Done enforcement in the planner.

## Manager's Notes

Deep research sources: Atlassian Kanban metrics, MethodologyWiki Kanban tutorial, Neural Project Institute Kanban guide, ProjectManagerTemplate Kanban checklist. Canonical essentials: visualize → limit WIP → manage flow (lead/cycle time, throughput, WIP, CFD) → explicit policies → feedback loops (daily stand-up, review, retrospective) → evolve. Common mistakes to avoid: board without WIP limits, too many columns, ignoring blocked items, never changing process, measuring utilization instead of flow.

## Local TODOs

- [x] Initial codebase exploration (graph over mcp-planner-server + dashboard)
- [ ] Audit current dashboard charts vs required flow views (CFD, control chart, WIP aging)
- [ ] Audit blocked-item handling and swarming support
- [ ] Audit retrospective/feedback-loop artifacts
- [x] Draft board-manager onboarding guide
- [x] Propose Definition-of-Done enforcement in planner
- [ ] Verify functionality

## Acceptance Criteria

- [x] Gap audit documented: list of missing Kanban essentials vs current implementation, with file:line citations
- [x] Dashboard plan includes CFD + control chart + WIP-aging additions (or justified deferral)
- [ ] Blocked items have a visible marker + swarming note in planner/dashboard
- [x] Retrospective artifact defined (file location + template)
- [x] Board-manager onboarding guide created under docs/
- [x] Definition of Done enforcement proposed for planner (lint or tool)
- [x] `lint_task_file` passes on this task file

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-planner-server --with pytest --with pyyaml python -m pytest tests/test_planner_server.py tests/test_planner_schedule.py -q
- **Expected result:** all tests pass (baseline preserved)
- **Actual result:** 147 passed, 1 warning in 46.36s
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Scope creep into a full dashboard rewrite; mitigation: audit + proposals first, implementation gated by Manager approval.
- **Rollback plan:** Revert any docs/dashboard changes; planner remains the derived index over tasks/ Markdown.

---

## Execution Log & Reasoning

Context gathered via graph and grep. Citations for gap audit:
- 14-day load view: `mcp-planner-server/static/index.html:674-690` (`renderPlanChart`, aria-label "14-day load").
- Measured-hours view: `mcp-planner-server/static/index.html:703-732` (`hoursChart`, aria-label "Measured hours, last 14 days").
- Planner task parsing: `mcp-planner-server/server.py:187` (`_parse_task_file`).
- WIP ceiling check: `mcp-planner-server/server.py:887-891`.
- QA budget check: `mcp-planner-server/server.py:878-883`.
- Blocked handling: not found (searched "blocked" in server.py; only dependency-blocked references at `:1023`).

Created docs: `docs/kanban-board-manager-guide.md`, `docs/kanban-policies.md`, `docs/retrospectives/TEMPLATE.md`. Strict tooling gate: docs-only repo, no stack marker matched — skip record: root=. markers=[pyproject.toml] matched=[] reason=no stack marker found (docs-only change). Baseline tests: 147 passed._

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
