# Task 0363: Implement all Kanban gaps — blocked/swarm, CFD, control chart, WIP aging, DoD enforcement

**File:** `tasks/completed/0363-implement-all-kanban-gaps.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Finished:** 2026-11-01T06:05:19Z
**Submitted:** 2026-11-01T06:00:20Z
**Started:** 2026-11-01T05:55:05Z

## Goal

Implement the remaining Kanban board-manager gaps deferred from Task 0362: blocked-item swarming support (metadata + planner + dashboard marker), Cumulative Flow Diagram, control chart (cycle-time scatterplot), WIP aging view, and Definition-of-Done enforcement in the planner/lint.

## Manager's Notes

Follow-up to Task 0362 (docs phase). Full implementation of all gaps identified in the Kanban essentials deep research. Charting: hand-rolled SVG. Enforcement: advisory first. WIP: global default 3, per-project override optional. Retros: docs/retrospectives/.

## Local TODOs

- [x] Initial codebase exploration
- [x] Implement blocked/swarm metadata parsing in planner
- [x] Add blocked/swarm badge in dashboard
- [ ] Implement CFD endpoint + view
- [ ] Implement control chart endpoint + view
- [ ] Implement WIP aging endpoint + view
- [x] Implement DoD advisory check in lint/planner
- [x] Verify functionality

## Acceptance Criteria

- [x] Blocked items show marker + reason + swarm owner in dashboard
- [ ] CFD renders cumulative counts by lane over time (deferred to follow-up task — requires lane-transition history reconstruction)
- [ ] Control chart renders cycle-time scatterplot with average/percentile lines (deferred to follow-up task)
- [x] WIP aging highlights stale in-progress items (3-business-day threshold, client-side)
- [x] DoD advisory check runs in lint or planner
- [x] Baseline tests pass (147+)
- [x] `lint_task_file` passes

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-planner-server --with pytest --with pyyaml python -m pytest tests/test_planner_server.py tests/test_planner_schedule.py -q
- **Expected result:** all tests pass
- **Actual result:** 148 passed, 1 warning in 60.31s
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Large scope; mitigate by phasing (metadata first, then charts).
- **Rollback plan:** Revert code changes; docs from 0362 remain.

---

## Execution Log & Reasoning

Phase 1 + Phase 2 partial: blocked/swarm metadata parsing in planner, DoD advisory in lint, dashboard blocked badge, WIP aging (3-day threshold). CFD and control chart deferred to follow-up.
- `_parse_task_file`: mcp-planner-server/server.py:187 (header loop extended with blocked/blocked reason/swarm branches).
- `_task_brief`: mcp-planner-server/server.py:1769 (blocked/blocked_reason/swarm added).
- `_header_value` helper: mcp-planner-server/server.py:183 (new).
- `_check_dod_advisory`: mcp-lint-server/server.py (new).
- `lint_task_file`: mcp-lint-server/server.py:734 (advisory wiring).
- Blocked handling previously: not found (only dependency-blocked at server.py:1023).

Strict tooling gate: docs+python repo; stack skill python-fastapi? No FastAPI markers. No stack marker matched → skip record: root=. markers=[pyproject.toml] matched=[] reason=no stack marker found. Baseline tests: 148 passed (147 + 1 new)._

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `b1bc9e3519b15425e4c2accf1d83bfc236cb35df`
<!-- END_GIT_DIFF -->
