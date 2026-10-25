# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
"""Planner metadata writer and lint guard (Task 0350).

Covers `schedule_tasks` (insert, update, idempotency, rejections) and the
`_check_planner_metadata` lint rule that stops an unparseable header from
silently dropping a task out of the Planner read model.
"""

import importlib.util
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "mcp-planner-server"))


@pytest.fixture(autouse=True)
def _isolated_project_registry(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "PLANNER_PROJECTS_REGISTRY", str(tmp_path / "planner-projects.json")
    )


_PLANNER_SPEC = importlib.util.spec_from_file_location(
    "planner_server_schedule", REPO / "mcp-planner-server" / "server.py"
)
planner = importlib.util.module_from_spec(_PLANNER_SPEC)
_PLANNER_SPEC.loader.exec_module(planner)

_LINT_SPEC = importlib.util.spec_from_file_location(
    "lint_server_metadata", REPO / "mcp-lint-server" / "server.py"
)
lint = importlib.util.module_from_spec(_LINT_SPEC)
_LINT_SPEC.loader.exec_module(lint)


def _task(tmp_path: Path, task_id: str = "336", status: str = "open") -> Path:
    backlog = tmp_path / "tasks" / "backlog"
    backlog.mkdir(parents=True, exist_ok=True)
    path = backlog / f"{int(task_id):03d}-sample.md"
    path.write_text(
        f"# Task {int(task_id):03d}: sample\n\n"
        f"**File:** `tasks/backlog/{path.name}`\n"
        f"**Source:** manager\n"
        f"**Type:** bug\n"
        f"**Status:** {status}\n"
        f"\n"
        f"## Goal\n\nDo the thing.\n\n"
        f"## Acceptance Criteria\n\n- [ ] one\n",
        encoding="utf-8",
    )
    return path


def test_inserts_metadata_after_status(tmp_path):
    path = _task(tmp_path)
    out = planner.schedule_tasks(str(tmp_path), "336:3h:2026-10-25")

    text = path.read_text(encoding="utf-8")
    assert "**Estimate:** 3h" in text
    assert "**Deadline:** 2026-10-25" in text
    lines = text.splitlines()
    status_idx = next(i for i, l in enumerate(lines) if l.startswith("**Status:**"))
    estimate_idx = next(i for i, l in enumerate(lines) if l.startswith("**Estimate:**"))
    assert estimate_idx == status_idx + 1, "metadata must follow the Status line"
    assert "updated" in out


def test_idempotent_second_call(tmp_path):
    path = _task(tmp_path)
    planner.schedule_tasks(str(tmp_path), "336:3h:2026-10-25")
    first = path.read_text(encoding="utf-8")

    out = planner.schedule_tasks(str(tmp_path), "336:3h:2026-10-25")

    assert path.read_text(encoding="utf-8") == first, "a repeat call must not rewrite"
    assert "unchanged" in out


def test_updates_existing_value_and_reports_previous(tmp_path):
    path = _task(tmp_path)
    planner.schedule_tasks(str(tmp_path), "336:3h:2026-10-25")
    out = planner.schedule_tasks(str(tmp_path), "336:5h:2026-10-26")

    text = path.read_text(encoding="utf-8")
    assert "**Estimate:** 5h" in text
    assert "**Deadline:** 2026-10-26" in text
    assert text.count("**Estimate:**") == 1, "update must replace, never duplicate"
    assert "3h -> 5h" in out


def test_dependencies_are_formatted(tmp_path):
    path = _task(tmp_path)
    planner.schedule_tasks(str(tmp_path), "336:3h:2026-10-27:338")
    assert "**Depends on:** [338]" in path.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "assignment,reason",
    [
        ("336:3 hours:2026-10-25", "estimate must look like"),
        ("336:3h:25-10-2026", "deadline must be YYYY-MM-DD"),
        ("999:3h:2026-10-25", "no task with that id"),
        ("336:3h:2026-10-25:338,336:4h:2026-10-26", "duplicate id"),
        ("336:3h", "expected id:estimate:deadline"),
    ],
)
def test_rejections_are_explicit(tmp_path, assignment, reason):
    path = _task(tmp_path)
    before = path.read_text(encoding="utf-8")
    out = planner.schedule_tasks(str(tmp_path), assignment)

    assert reason in out, f"expected reason {reason!r} in:\n{out}"
    assert path.read_text(encoding="utf-8") == before, "a rejected call must not write"


def test_archived_task_rejected(tmp_path):
    path = _task(tmp_path)
    archive = tmp_path / "tasks" / "archive"
    archive.mkdir(parents=True, exist_ok=True)
    path.rename(archive / path.name)

    out = planner.schedule_tasks(str(tmp_path), "336:3h:2026-10-25")
    assert "archived" in out


def test_written_file_still_passes_planner_lint(tmp_path):
    path = _task(tmp_path)
    planner.schedule_tasks(str(tmp_path), "336:3h:2026-10-25:338")

    issues = lint._check_planner_metadata(path.read_text(encoding="utf-8"), str(path))
    assert issues == [], f"writer produced metadata the lint rejects: {issues}"


@pytest.mark.parametrize(
    "line",
    [
        "**Estimate:** 3 hours",
        "**Estimate:** three hours",
        "**Estimate:** 3",
        "**Deadline:** 2026/10/25",
        "**Deadline:** next tuesday",
        "**Depends on:** task 338",
    ],
)
def test_lint_rejects_malformed_metadata(line):
    issues = lint._check_planner_metadata(
        f"# Task 1: x\n\n{line}\n", "tasks/backlog/001-x.md"
    )
    assert issues, f"lint accepted a value the Planner cannot parse: {line}"


@pytest.mark.parametrize(
    "line",
    [
        "**Estimate:** 3h",
        "**Estimate:** 2.5h",
        "**Deadline:** 2026-10-25",
        "**Depends on:** 338",
        "**Depends on:** [338, 340]",
    ],
)
def test_lint_accepts_valid_metadata(line):
    issues = lint._check_planner_metadata(
        f"# Task 1: x\n\n{line}\n", "tasks/backlog/001-x.md"
    )
    assert issues == [], f"lint rejected a parseable value: {line} -> {issues}"


def test_lint_allows_absent_metadata():
    issues = lint._check_planner_metadata("# Task 1: x\n\n**Status:** open\n", "x.md")
    assert issues == [], "legacy task files without metadata must keep passing"


def test_lint_rejects_duplicate_keys():
    content = "# Task 1: x\n\n**Estimate:** 3h\n**Estimate:** 4h\n"
    issues = lint._check_planner_metadata(content, "x.md")
    assert any(re.search(r"appears 2 times", i) for i in issues)
