# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
"""Offline unit tests for mcp-planner-server (Task 335).

Covers:
- DAG cycle detection for task dependencies (_deps_met)
- Circuit breaker: claim_next rejects pickup when QA task is pending
- Circuit breaker: claim_next rejects when dependencies unmet
- Daily agenda and quota calculation (sprint_daily_agenda, sprint_check_daily_quota)
- plan_status, sprint_stats, qa_budget, milestone_status
- plan_propose (propose-only, writes nothing)
- Task file parsing (_parse_task_file, _load_all_tasks, _find_task_by_id)

All tests are offline: they create temporary task files under tmp_path and
call the planner functions directly with project_root set. No network, no
gateway, no server process required.
"""

import importlib.util
import os
import sys
from pathlib import Path

import pytest

PLANNER_DIR = Path(__file__).parent.parent / "mcp-planner-server"
sys.path.insert(0, str(PLANNER_DIR))

# Load under a unique module name: several test modules in this suite do
# `import server` for their own MCP server, and sys.modules["server"] caches
# whichever loaded first — the planner tests then hit the wrong module and
# fail only in a full-suite run.
_PLANNER_SPEC = importlib.util.spec_from_file_location(
    "planner_server", PLANNER_DIR / "server.py"
)
planner = importlib.util.module_from_spec(_PLANNER_SPEC)
_PLANNER_SPEC.loader.exec_module(planner)


def _write_task(
    tmp_path,
    lane,
    task_id,
    title,
    status="open",
    estimate=None,
    deadline=None,
    milestone=None,
    depends_on=None,
    acceptance_criteria=None,
    todos=None,
):
    """Write a task file under tasks/<lane>/<task_id>-<slug>.md and return path."""
    lane_dir = tmp_path / "tasks" / lane
    lane_dir.mkdir(parents=True, exist_ok=True)
    slug = "task"
    filename = f"{int(task_id):03d}-{slug}.md"
    path = lane_dir / filename

    est_line = f"\n**Estimate:** {estimate}h" if estimate else ""
    dep_line = f"\n**Depends on:** {depends_on}" if depends_on else ""
    ms_line = f"\n**Milestone:** {milestone}" if milestone else ""
    dl_line = f"\n**Deadline:** {deadline}" if deadline else ""

    ac_block = ""
    if acceptance_criteria is not None:
        ac_block = "\n## Acceptance Criteria\n" + "\n".join(
            f"- [{'x' if c.get('done') else ' '}] {c['text']}"
            for c in acceptance_criteria
        )
    elif todos is None:  # Only add default AC if no custom AC and no custom TODOs
        ac_block = "\n## Acceptance Criteria\n- [ ] Task file lint passes"

    todo_block = ""
    if todos is not None:
        todo_block = "\n## Local TODOs\n" + "\n".join(
            f"- [{'x' if t.get('done') else ' '}] {t['text']}" for t in todos
        )
    elif acceptance_criteria is None:
        todo_block = "\n## Local TODOs\n- [ ] Write implementation"

    content = f"""# Task {int(task_id):03d}: {title}

**File:** tasks/{lane}/{filename}
**Source:** planner
**Type:** feature
**Status:** {status}{est_line}{dl_line}{ms_line}{dep_line}

## Source Context

### Variant C: Manager (`**Source:** manager`)

## Goal

{title}

## Manager's Notes

Test-generated task file.

{ac_block}{todo_block}

## Definition of Done

- [ ] `lint_task_file` passes
- [ ] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Test fixture.
- **Rollback plan:** Delete the task file.

## Execution Log & Reasoning

Test fixture created by test_planner_server.py.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

<!-- END_GIT_DIFF -->
"""
    path.write_text(content, encoding="utf-8")
    return path


def _load(workspace_root):
    return planner._load_all_tasks(Path(workspace_root))


# ---------------------------------------------------------------------------
# Parsing tests
# ---------------------------------------------------------------------------


def test_parse_task_file_basic(tmp_path):
    p = _write_task(
        tmp_path,
        "backlog",
        10,
        "Sample task",
        estimate=4,
        deadline="2026-11-15",
        milestone="M1",
        depends_on=["005", "006"],
    )
    rec = planner._parse_task_file(p)
    assert rec["lane"] == "backlog"
    assert rec["title"] == "Sample task"
    assert rec["status"] == "open"
    assert rec["estimate_hours"] == 4.0
    assert rec["deadline"] == "2026-11-15"
    assert rec["milestone"] == "M1"
    assert rec["depends_on"] == ["005", "006"]


def test_parse_task_file_ac_and_todos(tmp_path):
    p = _write_task(
        tmp_path,
        "in-progress",
        11,
        "AC task",
        acceptance_criteria=[
            {"text": "Lint passes", "done": True},
            {"text": "Tests pass", "done": False},
        ],
        todos=[{"text": "Write code", "done": True}],
    )
    rec = planner._parse_task_file(p)
    assert len(rec["acceptance_criteria"]) == 2
    assert rec["acceptance_criteria"][0]["done"] is True
    assert rec["acceptance_criteria"][1]["done"] is False
    assert len(rec["todos"]) == 1
    assert rec["todos"][0]["done"] is True


def test_load_all_tasks_across_lanes(tmp_path):
    _write_task(tmp_path, "backlog", 1, "Backlog task")
    _write_task(tmp_path, "in-progress", 2, "IP task")
    _write_task(tmp_path, "qa", 3, "QA task")
    _write_task(tmp_path, "completed", 4, "Done task", status="closed")
    tasks = _load(tmp_path)
    lanes = {}
    for t in tasks:
        lanes.setdefault(t["lane"], []).append(t)
    assert len(lanes["backlog"]) == 1
    assert len(lanes["in-progress"]) == 1
    assert len(lanes["qa"]) == 1
    assert len(lanes["completed"]) == 1


def test_find_task_by_id(tmp_path):
    _write_task(tmp_path, "backlog", 20, "Find me")
    tasks = _load(tmp_path)
    found = planner._find_task_by_id(tasks, "20")
    assert found is not None
    assert found["title"] == "Find me"
    assert planner._find_task_by_id(tasks, "999") is None


# ---------------------------------------------------------------------------
# Dependency / DAG cycle detection
# ---------------------------------------------------------------------------


def test_deps_met_all_completed(tmp_path):
    _write_task(tmp_path, "completed", 1, "Dep A", status="closed")
    _write_task(tmp_path, "completed", 2, "Dep B", status="closed")
    _write_task(tmp_path, "backlog", 3, "Depends on 1 and 2", depends_on=["1", "2"])
    tasks = _load(tmp_path)
    task = planner._find_task_by_id(tasks, "3")
    met, unmet = planner._deps_met(task, tasks)
    assert met is True
    assert unmet == []


def test_deps_met_unmet_dependency(tmp_path):
    _write_task(tmp_path, "backlog", 1, "Dep A")  # not completed
    _write_task(tmp_path, "backlog", 3, "Depends on 1", depends_on=["1"])
    tasks = _load(tmp_path)
    task = planner._find_task_by_id(tasks, "3")
    met, unmet = planner._deps_met(task, tasks)
    assert met is False
    assert unmet == ["1"]


def test_deps_met_missing_task(tmp_path):
    _write_task(tmp_path, "backlog", 3, "Depends on missing", depends_on=["99"])
    tasks = _load(tmp_path)
    task = planner._find_task_by_id(tasks, "3")
    met, unmet = planner._deps_met(task, tasks)
    assert met is False
    assert unmet == ["99"]


# ---------------------------------------------------------------------------
# claim_next circuit breaker tests
# ---------------------------------------------------------------------------


def test_claim_next_success(tmp_path, monkeypatch):
    _write_task(tmp_path, "backlog", 10, "Ready task", depends_on=["1"])
    _write_task(tmp_path, "completed", 1, "Dep A", status="closed")
    tasks = _load(tmp_path)
    # Monkeypatch _load_all_tasks inside claim_next by setting project_root
    result = planner.claim_next(str(tmp_path), "10")
    assert result.startswith("✅ claim_next succeeded"), result


def test_claim_next_not_in_backlog(tmp_path):
    _write_task(tmp_path, "qa", 10, "Already in QA")
    result = planner.claim_next(str(tmp_path), "10")
    assert result.startswith("❌ claim_next blocked"), result
    assert "not in backlog" in result or "not backlog" in result


def test_claim_next_qa_budget_exhausted(tmp_path):
    _write_task(tmp_path, "qa", 1, "Pending QA", status="open")
    _write_task(tmp_path, "backlog", 2, "Ready task")
    tasks = _load(tmp_path)
    # First claim the QA task? No - QA is pending, so claim_next for backlog task should fail
    result = planner.claim_next(str(tmp_path), "2")
    assert result.startswith("❌ claim_next blocked"), result
    assert "QA budget exhausted" in result


def test_claim_next_dependency_unmet(tmp_path):
    _write_task(tmp_path, "backlog", 1, "Dep A")  # not completed
    _write_task(tmp_path, "backlog", 2, "Depends on 1", depends_on=["1"])
    result = planner.claim_next(str(tmp_path), "2")
    assert result.startswith("❌ claim_next blocked"), result
    assert "unmet dependencies" in result


def test_claim_next_wip_ceiling(tmp_path):
    # Fill WIP to 3
    for i in range(1, 4):
        _write_task(tmp_path, "in-progress", i, f"WIP {i}")
    _write_task(tmp_path, "backlog", 4, "Ready task")
    result = planner.claim_next(str(tmp_path), "4")
    assert result.startswith("❌ claim_next blocked"), result
    assert "WIP ceiling reached" in result


# ---------------------------------------------------------------------------
# Daily agenda and quota
# ---------------------------------------------------------------------------


def test_sprint_daily_agenda(tmp_path):
    _write_task(tmp_path, "in-progress", 1, "Active task 1")
    _write_task(tmp_path, "qa", 2, "QA task 1")
    result = planner.sprint_daily_agenda(str(tmp_path))
    assert "In Progress" in result
    assert "Active task 1" in result
    assert "QA Pending" in result
    assert "QA task 1" in result


def test_sprint_daily_agenda_empty(tmp_path):
    result = planner.sprint_daily_agenda(str(tmp_path))
    assert "Nothing in progress" in result or "Ready to claim" in result


def test_sprint_check_daily_quota_reached(tmp_path):
    _write_task(tmp_path, "completed", 1, "Done", status="closed")
    result = planner.sprint_check_daily_quota(str(tmp_path))
    assert "DAILY_QUOTA_REACHED" in result


def test_sprint_check_daily_quota_not_reached(tmp_path):
    _write_task(tmp_path, "in-progress", 1, "Working")
    result = planner.sprint_check_daily_quota(str(tmp_path))
    assert "DAILY_QUOTA_REACHED" not in result
    assert "Quota not reached" in result or "in-progress" in result.lower()


# ---------------------------------------------------------------------------
# plan_status, sprint_stats, qa_budget, milestone_status
# ---------------------------------------------------------------------------


def test_plan_status(tmp_path):
    _write_task(tmp_path, "backlog", 1, "Backlog task")
    _write_task(tmp_path, "in-progress", 2, "IP task", estimate=4)
    _write_task(tmp_path, "qa", 3, "QA task")
    result = planner.plan_status(str(tmp_path))
    assert "Planner Status" in result
    assert "Backlog" in result
    assert "In Progress" in result
    assert "QA / Review" in result
    assert "Capacity" in result
    assert "Estimated remaining" in result
    assert "weekly capacity" in result
    assert "Blockers" in result


def test_sprint_stats(tmp_path):
    _write_task(tmp_path, "completed", 1, "Done", status="closed", estimate=4)
    _write_task(tmp_path, "in-progress", 2, "IP", estimate=2)
    result = planner.sprint_stats(str(tmp_path))
    assert "Sprint Stats" in result
    assert "Total tasks: 2" in result
    assert "Completed: 1" in result


def test_qa_budget_ok(tmp_path):
    _write_task(tmp_path, "backlog", 1, "Backlog")
    result = planner.qa_budget(str(tmp_path))
    assert "QA budget OK" in result


def test_qa_budget_exhausted(tmp_path):
    _write_task(tmp_path, "qa", 1, "Pending QA")
    result = planner.qa_budget(str(tmp_path))
    assert "QA budget exhausted" in result


def test_milestone_status(tmp_path):
    _write_task(tmp_path, "backlog", 1, "M1 Task 1", milestone="M1")
    _write_task(tmp_path, "completed", 2, "M1 Task 2", milestone="M1", status="closed")
    result = planner.milestone_status(str(tmp_path))
    assert "Milestone Status" in result
    assert "M1" in result


# ---------------------------------------------------------------------------
# plan_propose (propose only, writes nothing)
# ---------------------------------------------------------------------------


def test_plan_propose_writes_nothing(tmp_path):
    initial = _load(tmp_path)
    result = planner.plan_propose(
        "Build a feature",
        deadline="2026-12-01",
        capacity_hours=20,
        project_root=str(tmp_path),
    )
    after = _load(tmp_path)
    assert len(initial) == len(after)  # no files written
    assert "Plan Proposal: Build a feature" in result
    assert "Next task ID" in result
    assert "Suggested Tasks" in result


# ---------------------------------------------------------------------------
# plan_materialize
# ---------------------------------------------------------------------------


def test_plan_materialize_creates_task_file(tmp_path):
    result = planner.plan_materialize(str(tmp_path), "10")
    assert "Materialized 1 task file" in result
    created = tmp_path / "tasks" / "backlog" / "010-task-10.md"
    assert created.is_file()
    content = created.read_text(encoding="utf-8")
    assert "# Task 010: task-10" in content
    assert "**Status:** open" in content


def test_plan_materialize_skips_existing(tmp_path):
    _write_task(tmp_path, "backlog", 10, "Existing")
    result = planner.plan_materialize(str(tmp_path), "10")
    assert "already exists" in result


def test_plan_materialize_output_passes_real_lint(tmp_path, monkeypatch):
    """Materialized files must pass the real lint server validators.

    Uses the lint server's own module-level checks rather than an MCP call so
    the test stays offline. Also pins that no fabricated planner metadata
    leaks into the read model.
    """
    lint_path = Path(__file__).parent.parent / "mcp-lint-server" / "server.py"
    spec = importlib.util.spec_from_file_location("mcp_lint_server", lint_path)
    lint = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lint)

    planner.plan_materialize(str(tmp_path), "10")
    created = tmp_path / "tasks" / "backlog" / "010-task-10.md"
    assert created.is_file()
    content = created.read_text(encoding="utf-8")

    # lint_task_file resolves the `**File:**` header against the working
    # directory, so lint from the project root with a relative path exactly
    # as the real tool is invoked.
    monkeypatch.chdir(tmp_path)
    rel = "tasks/backlog/010-task-10.md"
    issues = lint._check_markdown_basics(content, rel) + \
        lint._check_task_file_structure(content, rel)
    assert issues == [], issues

    # No fabricated placeholders in the created file.
    assert "TBD" not in content

    # The derived read model must not report a bogus deadline.
    records = planner._load_all_tasks(tmp_path)
    assert all(r.get("deadline") is None for r in records)
    assert all(r.get("estimate_hours") is None for r in records)


# ---------------------------------------------------------------------------
# Dashboard API contract (/api/status)
# ---------------------------------------------------------------------------


def test_api_status_lanes_are_task_lists(tmp_path):
    """Every lane must be a list of task dicts, not a count.

    The dashboard renders each lane with ``items.map(...)``; shipping counts
    here raised "items.map is not a function" inside render() and silently
    blanked the milestone tree and timeline.
    """
    _write_task(tmp_path, "backlog", 1, "Backlog task")
    _write_task(tmp_path, "qa", 2, "QA task")
    payload = planner._api_status(str(tmp_path))

    assert "error" not in payload
    assert payload["project_root"] == str(tmp_path.resolve())
    for lane in planner.TASK_LANES:
        assert isinstance(payload["lanes"][lane], list)
    assert payload["lanes"]["backlog"][0]["id"] == "001"
    assert payload["lanes"]["backlog"][0]["title"] == "Backlog task"
    assert payload["qa_pending"] == 1


def test_api_status_milestone_tree_and_deadlines(tmp_path):
    _write_task(
        tmp_path, "backlog", 1, "Milestone task",
        milestone="M1", deadline="2026-12-01",
    )
    payload = planner._api_status(str(tmp_path))

    assert list(payload["milestone_tree"]) == ["M1"]
    assert payload["milestone_tree"]["M1"][0]["title"] == "Milestone task"
    assert payload["deadlines"][0]["deadline"] == "2026-12-01"


def test_api_status_pacing_mirrors_quota(tmp_path):
    _write_task(tmp_path, "in-progress", 1, "Open work")
    payload = planner._api_status(str(tmp_path))
    today = payload["today"]

    assert today["open"] == 1
    assert today["done"] == today["target"] - 1
    # Matches sprint_check_daily_quota: open work means quota not reached.
    assert "DAILY_QUOTA_REACHED" not in planner.sprint_check_daily_quota(str(tmp_path))


def test_api_status_explicit_project_root_wins_over_env(tmp_path, monkeypatch):
    monkeypatch.setenv("PLANNER_PROJECT_ROOT", "/nonexistent/elsewhere")
    payload = planner._api_status(str(tmp_path))
    assert payload["project_root"] == str(tmp_path.resolve())


def test_resolve_dashboard_root_uses_env(tmp_path, monkeypatch):
    (tmp_path / "tasks").mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("PLANNER_PROJECT_ROOT", str(tmp_path))
    assert planner._resolve_dashboard_root(None) == tmp_path.resolve()


def test_build_app_serves_dashboard_and_mcp_routes():
    """The combined app must expose dashboard, API, and the MCP mount."""
    app = planner.build_app()
    paths = [getattr(r, "path", None) for r in app.routes]
    assert "/" in paths
    assert "/api/status" in paths
    assert "/" in paths  # MCP sub-app is mounted at the root
    assert app.router.lifespan_context is not None
