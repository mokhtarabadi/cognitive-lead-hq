"""Planning-stack regression contracts, enforced by task 370.

Zero source edits in this file's scope. Every planner call uses tmp_path
as project_root. F1 milestone preservation, F2 merged grouping, F5 lock
gate, F3 deadline guards, F4 QA ceiling, F6 week scope, F7 sync guards,
and F8 lock-file behavior are must-pass guards.
F10 DoD mismatch is out of code-test scope and is noted only.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = REPO_ROOT / "mcp-planner-server" / "server.py"


def _load_server():
    """Load the planner server as an isolated module without real state."""
    # Unique name avoids collisions with other planner tests in one session.
    spec = importlib.util.spec_from_file_location(
        "planner_server_contracts", SERVER_PATH
    )
    assert spec is not None and spec.loader is not None, (
        f"missing planner server at {SERVER_PATH}"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["planner_server_contracts"] = module
    spec.loader.exec_module(module)
    return module


SERVER = _load_server()


@pytest.fixture(autouse=True)
def _isolate_registry(monkeypatch, tmp_path):
    """Point the planner registry at a tmp file; real lanes stay untouched."""
    # Mirrors tests/test_planner_schedule.py and test_planner_server.py.
    registry = tmp_path / "planner-projects.json"
    registry.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("PLANNER_PROJECTS_REGISTRY", str(registry))


def _write_task(project_root: Path, lane: str, filename: str, body: str) -> Path:
    """Write one task file under tmp_path and return its path."""
    # Never write outside tmp_path. Lane names mirror Kanban only here.
    task_dir = project_root / "tasks" / lane
    task_dir.mkdir(parents=True, exist_ok=True)
    path = task_dir / filename
    path.write_text(body, encoding="utf-8")
    return path


def _as_dict(payload):
    """Accept a dict, a JSON string, or plain text from planner tools."""
    if isinstance(payload, dict):
        return payload
    try:
        parsed = json.loads(payload)
        return parsed if isinstance(parsed, dict) else {"raw": parsed}
    except Exception:
        return {"raw": str(payload)}


def _minimal_task(num: int, title="Contract probe", **headers):
    """Build minimal task markdown the parser accepts (bold headers)."""
    # Parser reads `# Task N:` headings plus `**Key:** value` lines.
    lines = [f"# Task {num:04d}: {title}", "", "**Status:** open"]
    for key, value in headers.items():
        lines.append(f"**{key}:** {value}")
    lines.extend(["", "Body probes planner behavior in isolation.", ""])
    return "\n".join(lines)


def test_f1_milestone_preserved_by_schedule_tasks(tmp_path):
    """F1 must-pass guard: schedule_tasks keeps a hand-written Milestone."""
    # Targets schedule_tasks (server.py:737) and _parse_task_file (:294).
    name = "0001-milestone-guard.md"
    _write_task(tmp_path, "backlog", name, _minimal_task(1, milestone="M1"))
    result = SERVER.schedule_tasks(str(tmp_path), "0001:4h:2026-11-15")
    assert "0001" in str(result)
    record = SERVER._parse_task_file(tmp_path / "tasks" / "backlog" / name)
    assert record.get("milestone") == "M1"
    assert record.get("estimate_hours") == 4.0
    assert record.get("deadline") == "2026-11-15"


def test_f2_grouping_merges_case_variants(tmp_path):
    """F2 must-pass: M1 and m1 read as one milestone (first-seen display)."""
    # Targets _parse_task_file (:294) and milestone_status (:1257).
    _write_task(tmp_path, "backlog", "0002-upper.md", _minimal_task(2, milestone="M1"))
    _write_task(tmp_path, "backlog", "0003-lower.md", _minimal_task(3, milestone="m1"))
    text = str(SERVER.milestone_status(str(tmp_path)))
    # One canonical group: the label appears exactly once (case-insensitive).
    assert text.lower().count("m1") == 1
    assert "M1" in text  # first-seen spelling wins the display


def test_f3a_schedule_rejects_non_iso_deadline(tmp_path):
    """F3 must-pass guard: schedule_tasks rejects a non-YYYY-MM-DD deadline."""
    # Target schedule_tasks (:737). The file must stay byte-identical.
    name = "0004-deadline-trap.md"
    _write_task(tmp_path, "backlog", name, _minimal_task(4))
    path = tmp_path / "tasks" / "backlog" / name
    before = path.read_text(encoding="utf-8")
    result = str(SERVER.schedule_tasks(str(tmp_path), "0004:2h:tomorrow")).lower()
    assert "reject" in result or "error" in result or "invalid" in result
    assert path.read_text(encoding="utf-8") == before


def test_f3b_malformed_deadline_never_crashes(tmp_path):
    """F3 must-pass guard: a malformed Deadline never crashes status/quota."""
    # Targets plan_status (:1069) and sprint_check_daily_quota (:1424).
    _write_task(
        tmp_path,
        "backlog",
        "0005-malformed.md",
        _minimal_task(5, deadline="not-a-date"),
    )
    assert isinstance(_as_dict(SERVER.plan_status(str(tmp_path))), dict)
    assert isinstance(_as_dict(SERVER.sprint_check_daily_quota(str(tmp_path))), dict)


def test_f4_qa_budget_counts_single_ceiling(tmp_path):
    """F4 must-pass guard: qa_budget reports over the one-review ceiling."""
    # Target qa_budget (:1226). Two qa tasks exceed the autopilot ceiling.
    _write_task(tmp_path, "qa", "0006-first.md", _minimal_task(6))
    _write_task(tmp_path, "qa", "0007-second.md", _minimal_task(7))
    text = str(SERVER.qa_budget(str(tmp_path))).lower()
    assert "2" in text and ("1" in text or "ceiling" in text or "budget" in text)


def test_f5_lock_blocks_claim(tmp_path):
    """F5 must-pass: a sprint lock file blocks claim_next with unlock note."""
    # Targets sprint_lock (:1299) and claim_next (:954).
    _write_task(tmp_path, "backlog", "0008-locked.md", _minimal_task(8))
    SERVER.sprint_lock("sprint-1", str(tmp_path))
    outcome = str(SERVER.claim_next(str(tmp_path), "0008")).lower()
    assert "sprint-" in outcome and "unlock" in outcome
    # A blocked claim moves nothing.
    assert (tmp_path / "tasks" / "backlog" / "0008-locked.md").is_file()


def test_f6_stats_week_scoped_and_quota_date_aware(tmp_path):
    """F6 must-pass: stats carry a week scope; quota counts today-finished."""
    # Targets sprint_stats (:1164) and sprint_check_daily_quota (:1424).
    import re

    # An out-of-week stamp must not leak into the week numbers.
    out_week = _minimal_task(9, estimate="3h") + "**Started:** 2020-01-06T10:00:00Z\n"
    _write_task(tmp_path, "completed", "0009-done.md", out_week)
    stats = str(SERVER.sprint_stats(str(tmp_path)))
    assert "Week scope:" in stats
    assert re.search(r"Week scope: \d{4}-W\d{2} \(", stats), stats
    assert "Week estimated: 0h" in stats
    quota = str(SERVER.sprint_check_daily_quota(str(tmp_path)))
    assert "Finished today:" in quota


def test_f1b_milestone_written_by_schedule_tasks(tmp_path):
    """F1 must-pass: schedule_tasks writes **Milestone:** via trailing segment."""
    # Target schedule_tasks milestone segment; `-` deps skips to milestone.
    name = "0011-writer.md"
    _write_task(tmp_path, "backlog", name, _minimal_task(11))
    result = str(SERVER.schedule_tasks(str(tmp_path), "0011:2h:2026-11-20:-:M9"))
    assert "M9" in result
    text = (tmp_path / "tasks" / "backlog" / name).read_text(encoding="utf-8")
    assert "**Milestone:** M9" in text
    # Dash leaves an existing milestone untouched.
    SERVER.schedule_tasks(str(tmp_path), "0011:-:-")
    again = (tmp_path / "tasks" / "backlog" / name).read_text(encoding="utf-8")
    assert "**Milestone:** M9" in again


def test_f1c_milestone_newline_rejected(tmp_path):
    """F1 must-pass: a multiline milestone is rejected with no file write."""
    name = "0012-multiline.md"
    _write_task(tmp_path, "backlog", name, _minimal_task(12))
    path = tmp_path / "tasks" / "backlog" / name
    before = path.read_text(encoding="utf-8")
    result = str(
        SERVER.schedule_tasks(str(tmp_path), "0012:1h:2026-11-20:-:M03\nINJECTED")
    ).lower()
    assert "reject" in result or "single line" in result
    assert path.read_text(encoding="utf-8") == before


def test_f7_retrospective_template_exists():
    """F7 must-pass sync: a retrospective template exists in the repo."""
    # The guide's "Missing" label is stale; this pins the live truth.
    candidates = list(REPO_ROOT.glob("**/*retrospective*"))
    assert len(candidates) >= 1, "no retrospective template under repo root"


def test_f7_status_carries_lane_and_milestone_fields(tmp_path):
    """F7 must-pass sync: status outputs carry lane plus milestone fields."""
    # Targets plan_status (:1069) and milestone_status (:1257).
    _write_task(tmp_path, "backlog", "0010-cfd.md", _minimal_task(10, milestone="M1"))
    combined = (
        str(SERVER.plan_status(str(tmp_path)))
        + str(SERVER.milestone_status(str(tmp_path)))
    ).lower()
    assert "backlog" in combined
    assert "milestone" in combined or "m1" in combined


def test_f8_sprint_lock_writes_lock_file(tmp_path):
    """F8 must-pass behavior: sprint_lock records a lock file with metadata."""
    # sprint_lock (:1299) writes tasks/.plan/sprint-<id>.lock in the project.
    result = str(SERVER.sprint_lock("sprint-1", str(tmp_path)))
    assert "error" not in result.lower()
    lock = tmp_path / "tasks" / ".plan" / "sprint-sprint-1.lock"
    assert lock.is_file(), f"lock file missing: {lock}"
    payload = json.loads(lock.read_text(encoding="utf-8"))
    assert payload.get("sprint_id") == "sprint-1"
    assert "locked_at" in payload
