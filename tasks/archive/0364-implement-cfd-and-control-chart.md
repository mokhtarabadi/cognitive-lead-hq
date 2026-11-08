# Task 0364: Implement CFD and control chart views in planner dashboard

**File:** `tasks/completed/0364-implement-cfd-and-control-chart.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Finished:** 2026-11-01T06:17:57Z
**Submitted:** 2026-11-01T06:11:56Z
**Started:** 2026-11-01T06:06:11Z

## Goal

Implement the two remaining Kanban flow views deferred from Task 0363: a Cumulative Flow Diagram (cumulative counts by lane over time) and a control chart (cycle-time scatterplot with average and percentile lines), reconstructing history from existing task timestamps.

## Manager's Notes

Follow-up to Task 0363. Charting: hand-rolled SVG (consistent with existing plan/hours charts). CFD data: reconstruct from Started/Submitted/Finished timestamps. Control chart cycle time: Started→Finished. Advisory enforcement only.

## Local TODOs

- [ ] Initial codebase exploration
- [ ] Design CFD data reconstruction algorithm
- [ ] Implement CFD endpoint
- [ ] Implement CFD SVG view
- [ ] Design control chart data
- [ ] Implement control chart endpoint
- [ ] Implement control chart SVG view
- [ ] Verify functionality

## Acceptance Criteria

- [x] CFD renders cumulative counts by lane over time (hand-rolled SVG)
- [x] Control chart renders cycle-time scatterplot with average and percentile lines
- [x] Both views handle empty/no-data gracefully
- [x] Baseline tests pass (148+)
- [x] `lint_task_file` passes

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-planner-server --with pytest --with pyyaml python -m pytest tests/test_planner_server.py tests/test_planner_schedule.py -q
- **Expected result:** all tests pass
- **Actual result:** 148 passed, 1 warning in 50.28s
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Historical reconstruction may be inaccurate; mitigate by labeling views as derived.
- **Rollback plan:** Revert endpoint + view changes; docs remain.

---

## Execution Log & Reasoning

Phase 1: CFD endpoint + view, control chart endpoint + view implemented. Citations:
- `_api_cfd`, `_build_cfd_series`, `_cfd_lane`: mcp-planner-server/server.py
- `_api_control_chart`: mcp-planner-server/server.py
- Routes: /api/cfd, /api/control-chart
- Dashboard: renderCFD, loadCFD, renderControlChart, loadControlChart in index.html
- Strict tooling gate: no stack marker matched → skip record: root=. markers=[pyproject.toml] matched=[] reason=no stack marker found. Baseline tests: 148 passed._

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `06bb72ca9abf5dd8f66c3302b93b0a5d18683ca6`
<!-- END_GIT_DIFF -->
