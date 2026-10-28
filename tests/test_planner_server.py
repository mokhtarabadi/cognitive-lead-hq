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
import json
import os
import sys
from pathlib import Path

import pytest

PLANNER_DIR = Path(__file__).parent.parent / "mcp-planner-server"
sys.path.insert(0, str(PLANNER_DIR))


@pytest.fixture(autouse=True)
def _isolated_project_registry(tmp_path, monkeypatch):
    """Keep the auto-registry out of the real home during tests.

    Planner tools register the project root they were called with, and the
    suite calls them with pytest tmp dirs; without this the machine-local
    ``~/.config/opencode/planner-projects.json`` fills with /tmp entries.
    """
    monkeypatch.setenv(
        "PLANNER_PROJECTS_REGISTRY", str(tmp_path / "planner-projects.json")
    )


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


def test_parse_task_file_estimate_strict(tmp_path):
    p = _write_task(tmp_path, "backlog", 12, "Strict estimate", estimate=2.5)
    assert planner._parse_task_file(p)["estimate_hours"] == 2.5
    # A malformed value must book nothing — never a truncated prefix.
    p.write_text(
        p.read_text(encoding="utf-8").replace(
            "**Estimate:** 2.5h", "**Estimate:** 1h 30m"
        ),
        encoding="utf-8",
    )
    assert planner._parse_task_file(p)["estimate_hours"] is None


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
    issues = lint._check_markdown_basics(
        content, rel
    ) + lint._check_task_file_structure(content, rel)
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
        tmp_path,
        "backlog",
        1,
        "Milestone task",
        milestone="M1",
        deadline="2026-12-01",
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


def _write_mixed_width_task(tmp_path, lane, filename, title, **headers):
    """Write a task file with an exact filename (mixed widths allowed)."""
    lane_dir = tmp_path / "tasks" / lane
    lane_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Task {title}",
        "",
        f"**File:** `tasks/{lane}/{filename}`",
        "**Source:** manager",
        "**Type:** feature",
        "**Status:** open",
    ]
    for key, value in headers.items():
        lines.append(f"**{key}:** {value}")
    lines += [
        "",
        "## Goal",
        "",
        "Fixture.",
        "",
        "## Local TODOs",
        "",
        "- [x] Done",
        "",
        "## Acceptance Criteria",
        "",
        "- [x] Done",
        "",
        "## Verification Evidence",
        "",
        "Done.",
        "",
        "## Risk & Rollback",
        "",
        "None.",
        "",
        "## Execution Log & Reasoning",
        "",
        "Done.",
        "",
        "## Factual Git Diff",
        "",
        "<!-- BEGIN_GIT_DIFF -->",
        "<!-- END_GIT_DIFF -->",
        "",
    ]
    (lane_dir / filename).write_text("\n".join(lines), encoding="utf-8")


def test_lane_lists_sort_numerically_despite_mixed_widths(tmp_path):
    """Lexical glob order puts 0356 before 283; the board must not."""
    _write_mixed_width_task(tmp_path, "backlog", "0356-new.md", "New task")
    _write_mixed_width_task(tmp_path, "backlog", "283-old.md", "Old task")
    payload = planner._api_status(str(tmp_path))
    ids = [b["id"] for b in payload["lanes"]["backlog"]]
    assert ids == ["283", "0356"], ids


def test_milestone_tree_sorts_numerically(tmp_path):
    _write_mixed_width_task(
        tmp_path, "backlog", "0356-new.md", "New task", Milestone="M1"
    )
    _write_mixed_width_task(
        tmp_path, "backlog", "283-old.md", "Old task", Milestone="M1"
    )
    payload = planner._api_status(str(tmp_path))
    ids = [b["id"] for b in payload["milestone_tree"]["M1"]]
    assert ids == ["283", "0356"], ids


def test_api_hours_aggregates_measured_only(tmp_path):
    """Finished+stamped tasks count by finish date; unstamped never count."""
    from datetime import date, timedelta

    today = date.today()
    three_days_ago = today - timedelta(days=3)
    stamp = lambda d, h, m: f"{d.isoformat()}T{h:02d}:{m:02d}:00Z"
    _write_mixed_width_task(
        tmp_path,
        "completed",
        "283-old.md",
        "Old done",
        Started=stamp(today, 10, 0),
        Finished=stamp(today, 12, 30),
    )
    _write_mixed_width_task(
        tmp_path,
        "completed",
        "0356-new.md",
        "New done",
        Started=stamp(today, 14, 0),
        Finished=stamp(today, 15, 0),
    )
    _write_mixed_width_task(
        tmp_path,
        "completed",
        "100-earlier.md",
        "Earlier done",
        Started=stamp(three_days_ago, 9, 0),
        Finished=stamp(three_days_ago, 10, 0),
    )
    _write_mixed_width_task(tmp_path, "completed", "101-unstamped.md", "No stamps")
    payload = planner._api_hours(str(tmp_path))
    assert "error" not in payload
    by_date = {d["date"]: d for d in payload["days"]}
    assert by_date[today.isoformat()]["measured_hours"] == 3.5
    assert by_date[today.isoformat()]["done"] == 2
    assert by_date[three_days_ago.isoformat()]["measured_hours"] == 1.0
    assert by_date[three_days_ago.isoformat()]["done"] == 1
    assert sum(d["done"] for d in payload["days"]) == 3
    current_week = today - timedelta(days=today.weekday())
    by_week = {w["week"]: w for w in payload["weeks"]}
    assert by_week[current_week.isoformat()]["done"] >= 2
    assert len(payload["days"]) == 14
    assert len(payload["weeks"]) == 8


def test_resolve_dashboard_root_uses_env(tmp_path, monkeypatch):
    (tmp_path / "tasks").mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("PLANNER_PROJECT_ROOT", str(tmp_path))
    assert planner._resolve_dashboard_root(None) == tmp_path.resolve()


def test_build_app_serves_dashboard_and_mcp_routes(tmp_path):
    """The combined app must expose dashboard, API, and the MCP mount."""
    from starlette.routing import Mount

    (tmp_path / "tasks").mkdir(parents=True, exist_ok=True)
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("PLANNER_PROJECT_ROOT", str(tmp_path))
    monkeypatch.setenv("PLANNER_USERS_CONFIG", str(tmp_path / "nonexistent.json"))
    app = planner.build_app()
    try:
        paths = [getattr(r, "path", None) for r in app.routes]
        assert "/" in paths
        assert "/api/status" in paths
        assert "/api/task" in paths
        assert "/api/login" in paths
        assert "/api/logout" in paths
        assert "/static" in paths
    finally:
        monkeypatch.undo()
    assert "/api/me" in paths
    # The MCP transport routes itself at settings.streamable_http_path
    # ("/mcp") inside a root Mount, so the mount is the route to assert on.
    assert any(isinstance(route, Mount) for route in app.routes)
    assert planner.mcp.settings.streamable_http_path == "/mcp"
    assert app.router.lifespan_context is not None


# ---------------------------------------------------------------------------
# Dashboard API contract (/api/task) — task detail modal payload
# ---------------------------------------------------------------------------


def test_api_task_by_id_returns_markdown(tmp_path):
    """A numeric id resolves across lanes and returns the raw Markdown body."""
    _write_task(tmp_path, "backlog", 7, "Modal target")
    payload = planner._api_task(str(tmp_path), "7")

    assert "error" not in payload
    assert payload["id"] == "007"
    assert payload["lane"] == "backlog"
    assert payload["title"] == "Modal target"
    assert "## Goal" in payload["markdown"]
    assert payload["path"].endswith("007-task.md")


def test_api_task_by_path_returns_markdown(tmp_path):
    """A lane-relative path deep-links the same payload as the id form."""
    _write_task(tmp_path, "qa", 8, "Path lookup")
    payload = planner._api_task(str(tmp_path), None, "tasks/qa/008-task.md")

    assert "error" not in payload
    assert payload["id"] == "008"
    assert payload["lane"] == "qa"
    assert payload["title"] == "Path lookup"
    assert "## Local TODOs" in payload["markdown"]


def test_api_task_id_is_int_normalized(tmp_path):
    """Zero-padded ids match the same file (020 == 20), like _find_task_by_id."""
    _write_task(tmp_path, "backlog", 9, "Normalized")
    payload = planner._api_task(str(tmp_path), "009")
    assert payload["id"] == "009"


def test_api_task_unknown_id_is_not_found(tmp_path):
    (tmp_path / "tasks" / "backlog").mkdir(parents=True, exist_ok=True)
    assert planner._api_task(str(tmp_path), "424242") == {"error": "not found"}


def test_api_task_missing_params_is_client_error(tmp_path):
    payload = planner._api_task(str(tmp_path))
    assert payload["error"].startswith("missing param")


@pytest.mark.parametrize(
    "rel_path",
    [
        "../server.py",
        "tasks/backlog/../../server.py",
        "/etc/passwd",
        "tasks/backlog/sub/001-task.md",
        "tasks/nope/001-task.md",
        "tasks/backlog/001-task.txt",
        "C:/tasks/backlog/001-task.md",
        "tasks\\backlog\\001-task.md",
    ],
)
def test_api_task_path_traversal_is_forbidden(tmp_path, rel_path):
    """Anything outside tasks/<known lane>/<file>.md is 403, never a file read."""
    _write_task(tmp_path, "backlog", 1, "Guard")
    assert planner._api_task(str(tmp_path), None, rel_path) == {"error": "forbidden"}


def test_api_task_route_exists_in_auth_mode(auth_app):
    paths = [getattr(r, "path", None) for r in auth_app.routes]
    assert "/api/task" in paths


def test_api_task_401_when_unauthenticated(auth_client):
    resp = auth_client.get("/api/task", params={"id": "1"})
    assert resp.status_code == 401
    assert resp.json().get("error") == "unauthenticated"


def test_api_task_400_when_no_param(auth_client):
    auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
    resp = auth_client.get("/api/task")
    assert resp.status_code == 400
    assert resp.json().get("error", "").startswith("missing param")


def test_api_task_404_for_unknown_id(auth_client):
    auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
    resp = auth_client.get("/api/task", params={"id": "987654"})
    assert resp.status_code == 404


def test_api_task_serves_task_for_authenticated_admin(auth_client, tmp_path):
    _write_task(tmp_path, "backlog", 11, "Admin visible")
    auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
    resp = auth_client.get(
        "/api/task", params={"id": "11", "project_root": str(tmp_path)}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Admin visible"
    assert "## Goal" in data["markdown"]


def test_api_task_403_when_project_root_not_allowed(auth_client, tmp_path):
    """A viewer cannot read a task from a project outside its grants."""
    (tmp_path / "project-a").mkdir(parents=True, exist_ok=True)
    (tmp_path / "project-b").mkdir(parents=True, exist_ok=True)
    (tmp_path / "project-b" / "tasks").mkdir(parents=True, exist_ok=True)
    _write_task(tmp_path / "project-b", "backlog", 12, "Not yours")
    auth_client.post(
        "/api/login", json={"username": "viewer", "password": "viewer-pass"}
    )
    resp = auth_client.get(
        "/api/task",
        params={"id": "12", "project_root": str(tmp_path / "project-b")},
    )
    assert resp.status_code == 403
    assert resp.json().get("error") == "forbidden"


def test_api_task_403_for_traversal_over_http(auth_client, tmp_path):
    _write_task(tmp_path, "backlog", 13, "Guard http")
    auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
    resp = auth_client.get(
        "/api/task",
        params={
            "path": "tasks/backlog/../../server.py",
            "project_root": str(tmp_path),
        },
    )
    assert resp.status_code == 403


def test_api_task_works_in_open_mode(open_client, tmp_path):
    _write_task(tmp_path, "backlog", 14, "Open mode")
    resp = open_client.get(
        "/api/task", params={"id": "14", "project_root": str(tmp_path)}
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Open mode"


# ---------------------------------------------------------------------------
# Auth: password hashing, user config, and session management
# ---------------------------------------------------------------------------


def test_hash_password_produces_salt_and_hash():
    salt, hash_hex = planner._hash_password("test-password")
    assert len(salt) == 32  # 16 bytes hex
    assert len(hash_hex) == 64  # 32 bytes hex
    # Same password, different salt each call.
    salt2, hash2 = planner._hash_password("test-password")
    assert salt != salt2
    assert hash_hex != hash2


def test_verify_password_accepts_valid():
    salt, hash_hex = planner._hash_password("secret")
    assert planner._verify_password("secret", salt, hash_hex) is True


def test_verify_password_rejects_wrong():
    salt, hash_hex = planner._hash_password("secret")
    assert planner._verify_password("wrong", salt, hash_hex) is False


def test_verify_password_rejects_tampered_hash():
    salt, hash_hex = planner._hash_password("secret")
    assert planner._verify_password("secret", salt, hash_hex[:-4] + "0000") is False


def test_load_user_config_missing_file_returns_open_mode(tmp_path, monkeypatch):
    # When the file does not exist, auth is disabled.
    monkeypatch.setenv("PLANNER_USERS_CONFIG", str(tmp_path / "nonexistent.json"))
    cfg = planner._load_user_config()
    assert cfg == {"auth_enabled": False}


def test_load_user_config_invalid_json_returns_open_mode(tmp_path, monkeypatch):
    cfg_path = tmp_path / "planner-users.json"
    cfg_path.write_text("{not json", encoding="utf-8")
    monkeypatch.setenv("PLANNER_USERS_CONFIG", str(cfg_path))
    cfg = planner._load_user_config()
    assert cfg == {"auth_enabled": False}


def test_load_user_config_auth_disabled_by_default(tmp_path, monkeypatch):
    cfg_path = tmp_path / "planner-users.json"
    cfg_path.write_text('{"users": []}', encoding="utf-8")
    monkeypatch.setenv("PLANNER_USERS_CONFIG", str(cfg_path))
    cfg = planner._load_user_config()
    assert cfg["auth_enabled"] is False
    assert cfg["users"] == []


def test_load_user_config_with_users(monkeypatch, tmp_path):
    # When no env var is set, falls back to ~/.config/opencode/planner-users.json.
    monkeypatch.delenv("PLANNER_USERS_CONFIG", raising=False)
    fallback = tmp_path / "home" / ".config" / "opencode"
    fallback.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path / "home")
    (fallback / "planner-users.json").write_text(
        json.dumps(
            {
                "auth_enabled": True,
                "users": [
                    {"username": "a", "password_hash": "x", "allowed_projects": ["/p"]}
                ],
            }
        )
    )
    cfg = planner._load_user_config()
    assert isinstance(cfg, dict)
    assert "auth_enabled" in cfg
    assert isinstance(cfg.get("users"), list)


def test_find_user_by_username():
    cfg = {
        "auth_enabled": True,
        "users": [
            {"username": "alice", "role": "admin"},
            {"username": "bob", "role": "viewer"},
        ],
    }
    assert planner._find_user(cfg, "alice") is not None
    assert planner._find_user(cfg, "alice").get("role") == "admin"
    assert planner._find_user(cfg, "bob").get("role") == "viewer"
    assert planner._find_user(cfg, "carol") is None


def test_auth_state_properties_no_user():
    state = planner.AuthState({}, None, {})
    assert state.authenticated is False
    assert state.is_admin is False
    assert state.role == ""
    assert state.allowed_projects == []
    assert state.project_allowed(Path("/any")) is False


def test_auth_state_properties_with_user():
    user = {
        "username": "admin",
        "role": "admin",
        "allowed_projects": ["/"],
    }
    state = planner.AuthState({"users": [user]}, user, {})
    assert state.authenticated is True
    assert state.is_admin is True
    assert state.role == "admin"
    assert "/" in state.allowed_projects


def test_auth_state_allowed_projects_star():
    user = {"username": "admin", "role": "admin", "allowed_projects": ["*"]}
    state = planner.AuthState({}, user, {})
    assert state.project_allowed(Path("/anything")) is True
    assert state.project_allowed(Path("/deep/nested/project")) is True


def test_auth_state_project_allowed_exact_match():
    user = {"username": "viewer", "role": "viewer", "allowed_projects": ["/shared"]}
    state = planner.AuthState({}, user, {})
    assert state.project_allowed(Path("/shared")) is True
    assert state.project_allowed(Path("/shared/child")) is True
    assert state.project_allowed(Path("/other")) is False


def test_auth_state_project_allowed_subpath():
    user = {"username": "viewer", "role": "viewer", "allowed_projects": ["/home/dev"]}
    state = planner.AuthState({}, user, {})
    assert state.project_allowed(Path("/home/dev/project-a")) is True
    assert state.project_allowed(Path("/home/other/project-b")) is False


def test_auth_state_project_allowed_empty_when_not_authenticated():
    state = planner.AuthState({}, None, {})
    # Even if allowed_projects contained "*", an unauthenticated user is blocked.
    assert state.project_allowed(Path("/anything")) is False


def test_auth_state_dedup_allowed_projects():
    user = {"username": "u", "role": "viewer", "allowed_projects": ["/", "/", "*"]}
    state = planner.AuthState({}, user, {})
    assert state.allowed_projects == ["/", "*"]


def test_auth_state_allowed_projects_string_coerced_to_list():
    user = {"username": "u", "role": "viewer", "allowed_projects": "/"}
    state = planner.AuthState({}, user, {})
    assert state.allowed_projects == ["/"]


def test_auth_token_store_roundtrip():
    planner._build_auth_url_map().clear()
    store = planner._build_auth_url_map()
    store["tok1"] = {"user": {"username": "admin"}, "created": 0.0}
    assert planner._session_from_token("tok1") is not None
    assert planner._session_from_token("tok1").get("user").get("username") == "admin"
    assert planner._session_from_token("tok2") is None
    planner._invalidate_token("tok1")
    assert planner._session_from_token("tok1") is None


# ---------------------------------------------------------------------------
# Auth: login / logout / me handlers (tested through Starlette TestClient)
# ---------------------------------------------------------------------------


@pytest.fixture
def auth_app(tmp_path, monkeypatch):
    """Build the app with auth enabled and a test user config."""
    cfg_path = tmp_path / "planner-users.json"
    salt, hash_hex = planner._hash_password("admin-pass")
    salt2, hash2 = planner._hash_password("viewer-pass")
    cfg_path.write_text(
        json.dumps(
            {
                "auth_enabled": True,
                "users": [
                    {
                        "username": "admin",
                        "role": "admin",
                        "password_salt": salt,
                        "password_hash": hash_hex,
                        "allowed_projects": ["*"],
                    },
                    {
                        "username": "viewer",
                        "role": "viewer",
                        "password_salt": salt2,
                        "password_hash": hash2,
                        "allowed_projects": [str(tmp_path / "project-a")],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("PLANNER_USERS_CONFIG", str(cfg_path))
    # Both fixture projects feed the dashboard switcher; per-test creation of
    # their tasks/ dirs happens before the first request, so discovery sees
    # them and the RBAC filter is what decides who may list them.
    monkeypatch.setenv(
        "PLANNER_PROJECTS",
        os.pathsep.join([str(tmp_path / "project-a"), str(tmp_path / "project-b")]),
    )
    # Reset the module-level auth flag and config so the app picks up the
    # test config. The module was already imported, so we patch the globals.
    planner._USER_CONFIG = planner._load_user_config()
    planner._AUTH_ENABLED = bool(planner._USER_CONFIG.get("auth_enabled", False))
    planner._build_auth_url_map().clear()
    app = planner.build_app()
    # Build the app with auth enabled and a test user config — the auth middleware
    # is mounted inside build_app(), so every fresh app instance already reads the
    # patched module globals; no custom reset helper is required.
    # Prevent the build_app() call from signaling _CHANGED during fixture setup —
    # the signal is only meaningful between test cases, and we rely on the
    # auth_app fixture being rebuilt per test (pytest caches fixtures by params).
    return app


@pytest.fixture
def auth_client(auth_app):
    from starlette.testclient import TestClient

    # A context-managed client runs the app lifespan, which is what starts the
    # MCP session manager behind the /mcp guard.
    with TestClient(auth_app) as client:
        yield client


def test_security_headers_present(open_client):
    """Baseline headers ride every response; HSTS only when the hop is HTTPS."""
    resp = open_client.get("/api/me")
    assert resp.headers["x-content-type-options"] == "nosniff"
    assert resp.headers["referrer-policy"] == "same-origin"
    assert resp.headers["x-frame-options"] == "DENY"
    assert "strict-transport-security" not in resp.headers
    resp_https = open_client.get("/api/me", headers={"x-forwarded-proto": "https"})
    assert resp_https.headers["strict-transport-security"].startswith("max-age=")


def test_relative_project_root_rejected(auth_client):
    """A relative root must 400 instead of resolving against the daemon cwd."""
    auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
    for path in ("/api/status", "/api/task"):
        resp = auth_client.get(
            path, params={"project_root": "relative/path", "id": "1"}
        )
        assert resp.status_code == 400, path
        assert resp.json()["error"] == "project_root must be absolute", path


def test_session_cookie_is_secure_behind_https_proxy(auth_client):
    """X-Forwarded-Proto: https makes the session cookie Secure."""
    resp = auth_client.post(
        "/api/login",
        json={"username": "admin", "password": "admin-pass"},
        headers={"x-forwarded-proto": "https"},
    )
    assert resp.status_code == 200
    cookie = resp.headers["set-cookie"]
    assert "HttpOnly" in cookie
    assert "Secure" in cookie


def test_plan_payload_day_week_month(tmp_path):
    from datetime import date

    today = date.today().isoformat()
    _write_task(tmp_path, "backlog", 21, "Undated work", estimate=2)
    _write_task(tmp_path, "in-progress", 22, "Today work", estimate=1, deadline=today)
    _write_task(tmp_path, "completed", 23, "Done today", deadline=today)

    day = planner._plan_payload(str(tmp_path), "day")
    assert day["window"] == "day"
    assert len(day["days"]) == 1
    assert len(day["trend"]) == 14
    assert day["totals"]["in_progress"] >= 1
    assert any(t["id"] == "022" for t in day["days"][0]["tasks"])

    week = planner._plan_payload(str(tmp_path), "week")
    assert len(week["days"]) == 7
    assert len(week["weeks"]) == 1
    assert week["weeks"][0]["capacity_hours"] > 0

    month = planner._plan_payload(str(tmp_path), "month")
    assert len(month["weeks"]) >= 4


def test_plan_alerts_overdue_and_soon(tmp_path):
    from datetime import date, timedelta

    today = date.today()
    _write_task(
        tmp_path, "qa", 31, "Late", deadline=(today - timedelta(days=2)).isoformat()
    )
    _write_task(
        tmp_path,
        "backlog",
        32,
        "Soon",
        deadline=(today + timedelta(days=2)).isoformat(),
    )
    payload = planner._plan_payload(str(tmp_path), "week")
    assert [t["id"] for t in payload["alerts"]["overdue"]] == ["031"]
    assert [t["id"] for t in payload["alerts"]["soon"]] == ["032"]


def test_plan_week_sums_all_days(tmp_path):
    from datetime import date, timedelta

    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    _write_task(tmp_path, "backlog", 41, "Mon", deadline=week_start.isoformat())
    _write_task(
        tmp_path, "qa", 42, "Thu", deadline=(week_start + timedelta(days=3)).isoformat()
    )
    week = planner._plan_payload(str(tmp_path), "week")
    assert week["weeks"][0]["open"] == 2
    assert week["weeks"][0]["estimate_hours"] == week["totals"]["estimate_hours"]


def test_plan_month_includes_mid_month_dates(tmp_path):
    from datetime import date

    today = date.today()
    mid = today.replace(day=min(15, 28))
    _write_task(
        tmp_path, "backlog", 43, "Mid month", estimate=3, deadline=mid.isoformat()
    )
    month = planner._plan_payload(str(tmp_path), "month")
    assert month["totals"]["open"] >= 1
    assert month["totals"]["estimate_hours"] >= 3
    assert sum(w["open"] for w in month["weeks"]) == month["totals"]["open"]


def test_week_plan_roundtrip_and_approval(tmp_path):
    _write_task(tmp_path, "backlog", 51, "Plan me", estimate=2)
    plan, err = planner._validate_plan_edits(
        tmp_path,
        {
            "week": "2026-W43",
            "deadline_edits": {"051": "2026-10-26"},
            "capacity_by_day": {"2026-10-26": 4},
            "approved": True,
        },
    )
    assert err is None
    planner._write_week_plan(tmp_path, plan)
    saved = planner._read_week_plan(tmp_path, "2026-W43")
    assert saved["deadline_edits"]["051"] == "2026-10-26"
    assert saved["approved_at"]


def test_week_plan_validation_errors(tmp_path):
    _write_task(tmp_path, "backlog", 52, "Small", estimate=1)
    _, err = planner._validate_plan_edits(
        tmp_path, {"deadline_edits": {"999": "2026-10-26"}}
    )
    assert "unknown task" in err
    _, err = planner._validate_plan_edits(
        tmp_path,
        {
            "deadline_edits": {"052": "2026-10-26"},
            "capacity_by_day": {"2026-10-26": 0.5},
        },
    )
    assert "over capacity" in err


def test_plan_api_admin_only_and_persists(open_client, tmp_path, monkeypatch):
    monkeypatch.setenv("PLANNER_PROJECT_ROOT", str(tmp_path))
    _write_task(tmp_path, "backlog", 53, "Saved", estimate=1)
    week_dt = __import__("datetime").date.today().isocalendar()
    week = f"{week_dt[0]}-W{week_dt[1]:02d}"
    resp = open_client.post(
        "/api/plan",
        json={"week": week, "deadline_edits": {"053": "2026-10-26"}},
    )
    assert resp.status_code == 200
    assert resp.json()["deadline_edits"]["053"] == "2026-10-26"
    status = open_client.get("/api/plan", params={"window": "week"}).json()
    assert status["plan"]["week"] == week


def test_plan_api_viewer_cannot_save(auth_client):
    auth_client.post(
        "/api/login", json={"username": "viewer", "password": "viewer-pass"}
    )
    resp = auth_client.post("/api/plan", json={"deadline_edits": {}})
    assert resp.status_code == 403


def test_sprint_daily_agenda_reads_saved_plan(tmp_path, monkeypatch):
    monkeypatch.setenv("PLANNER_PROJECT_ROOT", str(tmp_path))
    _write_task(tmp_path, "backlog", 54, "Committed", estimate=1)
    plan, _ = planner._validate_plan_edits(
        tmp_path,
        {"deadline_edits": {"054": __import__("datetime").date.today().isoformat()}},
    )
    planner._write_week_plan(tmp_path, plan)
    agenda = planner.sprint_daily_agenda(str(tmp_path))
    assert "Today's commitment" in agenda
    assert "054" in agenda


def test_owner_field_parsed_and_briefed(tmp_path):
    _write_task(tmp_path, "backlog", 61, "Owned work")
    path = next((tmp_path / "tasks" / "backlog").glob("061-*.md"))
    path.write_text(
        path.read_text().replace(
            "**Status:** open", "**Status:** open\n**Owner:** ehsan"
        ),
        encoding="utf-8",
    )
    brief = planner._task_brief(planner._parse_task_file(path))
    assert brief["owner"] == "ehsan"


def test_agenda_nudges_when_backlog_waiting(tmp_path, monkeypatch):
    monkeypatch.setenv("PLANNER_PROJECT_ROOT", str(tmp_path))
    _write_task(tmp_path, "backlog", 62, "Waiting")
    agenda = planner.sprint_daily_agenda(str(tmp_path))
    assert "NUDGE" in agenda


def test_claim_next_reports_overdue(tmp_path):
    _write_task(tmp_path, "backlog", 63, "Late", deadline="2020-01-01")
    _write_task(tmp_path, "backlog", 64, "Next")
    result = planner.claim_next(str(tmp_path), "64")
    assert "claim_next succeeded" in result
    assert "OVERDUE" in result and "063" in result


def test_project_registry_records_and_dedupes(tmp_path, monkeypatch):
    reg = tmp_path / "reg.json"
    monkeypatch.setenv("PLANNER_PROJECTS_REGISTRY", str(reg))
    target = tmp_path / "proj"
    (target / "tasks").mkdir(parents=True)
    planner._register_project(target)
    planner._register_project(target)
    assert planner._read_projects_registry() == [str(target.resolve())]


def test_project_registry_is_capped(tmp_path, monkeypatch):
    reg = tmp_path / "reg.json"
    monkeypatch.setenv("PLANNER_PROJECTS_REGISTRY", str(reg))
    for i in range(55):
        planner._register_project(tmp_path / f"p{i}")
    assert len(planner._read_projects_registry()) == 50


def test_discover_projects_includes_registered(tmp_path, monkeypatch):
    reg = tmp_path / "reg.json"
    monkeypatch.setenv("PLANNER_PROJECTS_REGISTRY", str(reg))
    monkeypatch.delenv("PLANNER_PROJECTS", raising=False)
    project = tmp_path / "registered"
    (project / "tasks").mkdir(parents=True)
    planner._register_project(project)
    names = [p["path"] for p in planner._discover_projects(tmp_path)]
    assert str(project.resolve()) in names


def test_discover_projects_drops_dead_registered_paths(tmp_path, monkeypatch):
    reg = tmp_path / "reg.json"
    monkeypatch.setenv("PLANNER_PROJECTS_REGISTRY", str(reg))
    monkeypatch.delenv("PLANNER_PROJECTS", raising=False)
    dead = tmp_path / "no-tasks"
    dead.mkdir()
    planner._register_project(dead)
    names = [p["path"] for p in planner._discover_projects(tmp_path)]
    assert str(dead.resolve()) not in names


def test_api_plan_http_contract(auth_client):
    assert auth_client.get("/api/plan").status_code == 401
    auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
    assert auth_client.get("/api/plan", params={"window": "year"}).status_code == 400


def test_api_plan_relative_root_rejected(open_client):
    resp = open_client.get("/api/plan", params={"project_root": "relative/path"})
    assert resp.status_code == 400


def test_plan_missing_dir_returns_empty_buckets(tmp_path):
    payload = planner._plan_payload(str(tmp_path), "week")
    assert payload["totals"]["estimate_hours"] == 0
    assert len(payload["days"]) == 7


def test_login_valid_credentials_returns_token(auth_client):
    resp = auth_client.post(
        "/api/login", json={"username": "admin", "password": "admin-pass"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["token"]
    assert data["username"] == "admin"
    assert data["role"] == "admin"
    assert data["allowed_projects"] == ["*"]
    assert "planner_session" in resp.cookies


def test_login_invalid_password_returns_401(auth_client):
    resp = auth_client.post(
        "/api/login", json={"username": "admin", "password": "wrong"}
    )
    assert resp.status_code == 401


def test_login_nonexistent_user_returns_401(auth_client):
    resp = auth_client.post("/api/login", json={"username": "nobody", "password": "x"})
    assert resp.status_code == 401


def test_login_missing_fields_returns_400(auth_client):
    resp = auth_client.post("/api/login", json={"username": "admin"})
    assert resp.status_code == 400


def test_login_invalid_json_returns_400(auth_client):
    resp = auth_client.post("/api/login", content="not json")
    assert resp.status_code == 400


def test_me_returns_user_when_authenticated(auth_client, auth_app):
    auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
    resp = auth_client.get("/api/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["authenticated"] is True
    assert data["username"] == "admin"
    assert data["role"] == "admin"
    assert data["allowed_projects"] == ["*"]


def test_me_returns_401_when_unauthenticated(auth_client):
    resp = auth_client.get("/api/me")
    assert resp.status_code == 401


def test_logout_clears_session(auth_client, auth_app):
    auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
    assert auth_client.get("/api/me").status_code == 200
    resp = auth_client.post("/api/logout")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
    assert auth_client.get("/api/me").status_code == 401


def test_me_after_logout_is_401(auth_client, auth_app):
    auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
    auth_client.post("/api/logout")
    resp = auth_client.get("/api/me")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Auth: RBAC — admin sees all, viewer only sees authorized projects
# ---------------------------------------------------------------------------


def test_api_status_401_when_unauthenticated_and_auth_enabled(auth_client):
    # Without logging in, status is 401.
    resp = auth_client.get("/api/status")
    assert resp.status_code == 401


def test_api_status_admin_sees_all_projects(auth_client, auth_app, tmp_path):
    auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
    (tmp_path / "project-a").mkdir(parents=True, exist_ok=True)
    (tmp_path / "project-b").mkdir(parents=True, exist_ok=True)
    (tmp_path / "project-a" / "tasks").mkdir(parents=True, exist_ok=True)
    (tmp_path / "project-b" / "tasks").mkdir(parents=True, exist_ok=True)
    resp = auth_client.get("/api/status")
    assert resp.status_code == 200
    data = resp.json()
    project_paths = [p["path"] for p in data["projects"]]
    assert str(tmp_path / "project-a") in project_paths
    assert str(tmp_path / "project-b") in project_paths


def test_api_status_viewer_sees_only_authorized_project(
    auth_client, auth_app, tmp_path
):
    # Viewer is only allowed into project-a.
    auth_client.post(
        "/api/login", json={"username": "viewer", "password": "viewer-pass"}
    )
    (tmp_path / "project-a").mkdir(parents=True, exist_ok=True)
    (tmp_path / "project-b").mkdir(parents=True, exist_ok=True)
    (tmp_path / "project-a" / "tasks").mkdir(parents=True, exist_ok=True)
    (tmp_path / "project-b" / "tasks").mkdir(parents=True, exist_ok=True)
    resp = auth_client.get("/api/status")
    assert resp.status_code == 200
    data = resp.json()
    project_paths = [p["path"] for p in data["projects"]]
    assert str(tmp_path / "project-a") in project_paths
    assert str(tmp_path / "project-b") not in project_paths


def test_api_status_403_when_project_root_not_allowed(auth_client, auth_app, tmp_path):
    # Viewer logs in; requesting project-b (not allowed) returns 403.
    auth_client.post(
        "/api/login", json={"username": "viewer", "password": "viewer-pass"}
    )
    (tmp_path / "project-a").mkdir(parents=True, exist_ok=True)
    (tmp_path / "project-b").mkdir(parents=True, exist_ok=True)
    (tmp_path / "project-a" / "tasks").mkdir(parents=True, exist_ok=True)
    (tmp_path / "project-b" / "tasks").mkdir(parents=True, exist_ok=True)
    resp = auth_client.get(
        "/api/status", params={"project_root": str(tmp_path / "project-b")}
    )
    assert resp.status_code == 403
    data = resp.json()
    assert data.get("error") == "forbidden"


def test_api_status_allowed_project_root_ok_for_viewer(auth_client, auth_app, tmp_path):
    auth_client.post(
        "/api/login", json={"username": "viewer", "password": "viewer-pass"}
    )
    (tmp_path / "project-a").mkdir(parents=True, exist_ok=True)
    (tmp_path / "project-a" / "tasks").mkdir(parents=True, exist_ok=True)
    resp = auth_client.get(
        "/api/status", params={"project_root": str(tmp_path / "project-a")}
    )
    assert resp.status_code == 200
    data = resp.json()
    project_paths = [p["path"] for p in data["projects"]]
    assert str(tmp_path / "project-a") in project_paths
    assert str(tmp_path / "project-b") not in project_paths


# ---------------------------------------------------------------------------
# Auth: /mcp transport stays open to loopback clients; /api/* stays guarded
# ---------------------------------------------------------------------------


def test_mcp_open_without_session_when_auth_enabled(auth_client):
    # Local OpenCode clients send no cookie and must still reach the transport.
    resp = auth_client.post(
        "/mcp", content='{"jsonrpc":"2.0","method":"tools/list","id":1}'
    )
    assert resp.status_code not in (401, 403)


def test_mcp_open_for_viewer_session(auth_client):
    auth_client.post(
        "/api/login", json={"username": "viewer", "password": "viewer-pass"}
    )
    resp = auth_client.post(
        "/mcp", content='{"jsonrpc":"2.0","method":"tools/list","id":1}'
    )
    assert resp.status_code not in (401, 403)


def test_api_status_stays_guarded_while_mcp_is_open(auth_client):
    # Same client, same auth-enabled app: /mcp passes, /api/status still 401.
    mcp_resp = auth_client.post(
        "/mcp", content='{"jsonrpc":"2.0","method":"tools/list","id":1}'
    )
    assert mcp_resp.status_code not in (401, 403)
    assert auth_client.get("/api/status").status_code == 401
    assert auth_client.get("/api/me").status_code == 401


# ---------------------------------------------------------------------------
# Auth: backward compatibility when auth is disabled
# ---------------------------------------------------------------------------


@pytest.fixture
def open_app(tmp_path, monkeypatch):
    """Build the app with auth disabled (no config file)."""
    monkeypatch.setenv("PLANNER_USERS_CONFIG", str(tmp_path / "nonexistent.json"))
    planner._USER_CONFIG = planner._load_user_config()
    planner._AUTH_ENABLED = bool(planner._USER_CONFIG.get("auth_enabled", False))
    planner._build_auth_url_map().clear()
    return planner.build_app()


@pytest.fixture
def open_client(open_app):
    from starlette.testclient import TestClient

    # Context-managed so the app lifespan starts the MCP session manager.
    with TestClient(open_app) as client:
        yield client


def test_login_when_auth_disabled_returns_note(open_client):
    resp = open_client.post("/api/login", json={"username": "x", "password": "y"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["note"] == "auth disabled"
    assert data["token"] == ""
    assert data["username"] == ""


def test_me_when_auth_disabled_returns_unauthenticated_note(open_client):
    resp = open_client.get("/api/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["authenticated"] is False
    assert data["note"] == "auth disabled"


def test_status_works_without_auth(open_client, tmp_path):
    (tmp_path / "tasks").mkdir(parents=True, exist_ok=True)
    resp = open_client.get("/api/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "error" not in data or data.get("error") is None


def test_dashboard_frontend_serves_when_auth_disabled(open_client, tmp_path):
    # The dashboard static files should still serve when auth is disabled.
    (tmp_path / "tasks").mkdir(parents=True, exist_ok=True)
    resp = open_client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")


def test_dashboard_static_assets_serve_when_auth_disabled(open_client, tmp_path):
    (tmp_path / "tasks").mkdir(parents=True, exist_ok=True)
    resp = open_client.get("/static/index.html")
    assert resp.status_code == 200


def test_mcp_route_exists_when_auth_disabled(open_client):
    # The /mcp route is present regardless of auth mode.
    resp = open_client.post(
        "/mcp", content='{"jsonrpc":"2.0","method":"tools/list","id":1}'
    )
    # The MCP endpoint returns its own status; we just assert the route is reachable.
    assert resp.status_code in (
        200,
        400,
        405,
    )  # 400/405 expected for malformed MCP body


def test_login_when_auth_disabled_and_blob_body_returns_200(open_client):
    resp = open_client.post("/api/login", content="not json")
    # Auth disabled: the handler still parses JSON and falls through to the note.
    assert resp.status_code == 200
    assert resp.json()["note"] == "auth disabled"


# ---------------------------------------------------------------------------
# User management CLI (stdlib only, same hashing scheme as the server)
# ---------------------------------------------------------------------------


def _load_manage_users():
    spec = importlib.util.spec_from_file_location(
        "planner_manage_users", PLANNER_DIR / "manage_users.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_manage_users_cli_add_writes_server_verifiable_hash(tmp_path, capsys):
    manage_users = _load_manage_users()
    cfg = tmp_path / "planner-users.json"

    code = manage_users.main(
        [
            "--config",
            str(cfg),
            "add",
            "--username",
            "friend",
            "--role",
            "viewer",
            "--projects",
            str(tmp_path / "shared"),
            "--password",
            "friend-pass",
        ]
    )
    assert code == 0

    data = json.loads(cfg.read_text(encoding="utf-8"))
    assert data["auth_enabled"] is True
    user = data["users"][0]
    assert user["username"] == "friend"
    assert user["role"] == "viewer"
    assert user["allowed_projects"] == [str(tmp_path / "shared")]
    # The server verifies with its own PBKDF2 helper — the schemes must agree.
    assert planner._verify_password(
        "friend-pass", user["password_salt"], user["password_hash"]
    )

    out = capsys.readouterr().out
    assert "Added user 'friend'" in out


def test_manage_users_cli_rejects_duplicate_user(tmp_path):
    manage_users = _load_manage_users()
    cfg = tmp_path / "planner-users.json"
    base = [
        "--config",
        str(cfg),
        "add",
        "--username",
        "admin",
        "--role",
        "admin",
        "--projects",
        "*",
        "--password",
        "pw",
    ]
    assert manage_users.main(base) == 0
    assert manage_users.main(base) == 1


def test_manage_users_cli_disable_keeps_server_open(tmp_path):
    manage_users = _load_manage_users()
    cfg = tmp_path / "planner-users.json"
    manage_users.main(
        [
            "--config",
            str(cfg),
            "add",
            "--username",
            "admin",
            "--role",
            "admin",
            "--projects",
            "*",
            "--password",
            "pw",
        ]
    )
    assert manage_users.main(["--config", str(cfg), "disable"]) == 0
    data = json.loads(cfg.read_text(encoding="utf-8"))
    assert data["auth_enabled"] is False
