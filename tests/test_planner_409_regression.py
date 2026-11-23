# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
"""Regression tests for the planner dashboard hardening (task 409).

Covers the defects found by browser probing across all five registered
projects: project-scoped plan writes, HTTP 500 on status failure, real
finished-today counts, canonical milestone ids and declared-milestone seeding,
UTC day anchoring, and trusted-proxy handling of forwarded protocol headers.

All tests are offline: they build the Starlette app in-process with a temporary
project directory and drive it with ``starlette.testclient.TestClient``. No
network, no running daemon, no session process required.
"""

import importlib.util
import os
import sys
from pathlib import Path

import pytest
from starlette.testclient import TestClient

PLANNER_DIR = Path(__file__).parent.parent / "mcp-planner-server"
sys.path.insert(0, str(PLANNER_DIR))


@pytest.fixture(autouse=True)
def _isolated_registry(tmp_path, monkeypatch):
    """Keep auto-registration and auth config out of the real home dir."""
    monkeypatch.setenv(
        "PLANNER_PROJECTS_REGISTRY", str(tmp_path / "planner-projects.json")
    )
    # Point at a non-existent file so _load_user_config falls back to open
    # local mode (documented no-auth behavior on missing config). Deleting
    # the env var instead falls back to the real home
    # config (~/.config/opencode/planner-users.json), which has auth_enabled:
    # true, so every request came back 401 instead of the asserted 400/404.
    monkeypatch.setenv(
        "PLANNER_USERS_CONFIG", str(tmp_path / "planner-users-none.json")
    )
    monkeypatch.delenv("PLANNER_PROJECT_ROOT", raising=False)
    monkeypatch.delenv("PLANNER_TRUSTED_PROXIES", raising=False)


_PLANNER_SPEC = importlib.util.spec_from_file_location(
    "planner_server_409", PLANNER_DIR / "server.py"
)
planner = importlib.util.module_from_spec(_PLANNER_SPEC)
_PLANNER_SPEC.loader.exec_module(planner)


def _write_task(tmp_path, lane, task_id, title, **headers):
    """Write a minimal parseable task file and return its path."""
    lane_dir = tmp_path / "tasks" / lane
    lane_dir.mkdir(parents=True, exist_ok=True)
    path = lane_dir / f"{task_id}-{title.lower().replace(' ', '-')}.md"
    lines = [
        f"# Task {task_id}: {title}",
        "",
        f"**Status:** {headers.pop('status', 'open')}",
    ]
    for key, value in headers.items():
        lines.append(f"**{key.replace('_', ' ').title()}:** {value}")
    lines.extend(["", "## Goal", "", "Offline regression fixture.", ""])
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _make_project(tmp_path, name="proj"):
    root = tmp_path / name
    (root / "tasks" / "backlog").mkdir(parents=True, exist_ok=True)
    return root


def test_plan_save_missing_project_root_returns_400(tmp_path):
    """POST /api/plan without project_root is rejected, not defaulted."""
    root = _make_project(tmp_path)
    with TestClient(planner.build_app()) as client:
        resp = client.post("/api/plan", json={"approved": False})
    assert resp.status_code == 400
    assert "project_root" in resp.json()["error"]
    assert not (root / "tasks" / ".plan").exists()


def test_plan_save_unknown_project_root_returns_404(tmp_path):
    """A non-existent absolute root is a 404, never a silent fallback."""
    with TestClient(planner.build_app()) as client:
        resp = client.post(
            "/api/plan",
            json={"project_root": str(tmp_path / "does-not-exist"), "approved": False},
        )
    assert resp.status_code == 404
    assert resp.json()["error"] == "unknown project_root"


def test_plan_save_writes_only_to_selected_project(tmp_path):
    """The write lands under the requested root, not the daemon default."""
    root_a = _make_project(tmp_path, "project-a")
    root_b = _make_project(tmp_path, "project-b")
    with TestClient(planner.build_app()) as client:
        resp = client.post(
            "/api/plan",
            json={"project_root": str(root_a), "approved": False},
        )
    assert resp.status_code == 200
    week = resp.json()["week"]
    assert (planner._plan_file(root_a, week)).is_file()
    assert not (planner._plan_file(root_b, week)).exists()


def test_api_status_internal_error_returns_500(tmp_path, monkeypatch):
    """An internal failure keeps a danger signal instead of HTTP 200."""
    root = _make_project(tmp_path)
    monkeypatch.setattr(
        planner,
        "_load_all_tasks",
        lambda _root: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    with TestClient(planner.build_app(), raise_server_exceptions=False) as client:
        resp = client.get("/api/status", params={"project_root": str(root)})
    assert resp.status_code == 500
    assert resp.json()["error"] == "internal error"


def test_today_done_counts_real_finished_tasks(tmp_path):
    """A project with zero finished tasks no longer claims target completions."""
    empty = _make_project(tmp_path, "empty")
    empty_payload = planner._api_status(str(empty))
    assert empty_payload["today"]["done"] == 0
    assert empty_payload["today"]["quota_reached"] is True

    worked = _make_project(tmp_path, "worked")
    _write_task(
        worked,
        "completed",
        "001",
        "Finished today",
        status="closed",
        finished=planner._utc_today().isoformat() + "T07:00:00Z",
    )
    payload = planner._api_status(str(worked))
    assert payload["today"]["done"] == 1


def test_normalize_milestone_unifies_leading_zeros_and_case():
    """M1, m01 and M001 are one canonical milestone key."""
    assert planner._normalize_milestone("M1") == "M01"
    assert planner._normalize_milestone("m01") == "M01"
    assert planner._normalize_milestone(" M003 ") == "M03"
    assert planner._normalize_milestone("") == ""


def test_declared_milestone_seeds_board(tmp_path):
    """A milestone document is visible even with zero tagged tasks."""
    root = _make_project(tmp_path)
    milestone_dir = root / "tasks" / "milestones"
    milestone_dir.mkdir(parents=True, exist_ok=True)
    (milestone_dir / "M02-board-hardening.md").write_text(
        "# Milestone M02 — Board hardening\n", encoding="utf-8"
    )
    assert planner._milestone_definitions(root)["M02"].startswith("Milestone M02")
    payload = planner._api_status(str(root))
    assert "M02" in payload["milestone_tree"]
    assert payload["milestone_tree"]["M02"][0]["status"] == "declared"


def test_utc_today_is_timezone_aware_source():
    """Day anchoring uses UTC, not the host local date."""
    from datetime import datetime, timezone

    assert planner._utc_today() == datetime.now(timezone.utc).date()


def test_forwarded_proto_ignored_from_untrusted_peer():
    """A spoofed X-Forwarded-Proto from a non-proxy cannot force Secure."""

    class Peer:
        def __init__(self, host):
            self.host = host

    class FakeRequest:
        def __init__(self, host, proto):
            self.client = Peer(host)
            self.headers = {"x-forwarded-proto": proto}
            self.url = type("URL", (), {"scheme": "http"})()

    assert planner._is_https(FakeRequest("203.0.113.9", "https")) is False
    assert planner._is_https(FakeRequest("127.0.0.1", "https")) is True


def test_project_tool_positional_does_not_register_bogus(tmp_path):
    """A positional goal is not mistaken for a project root (B4)."""
    root = _make_project(tmp_path, "posproj")
    planner.plan_propose("Build a feature X", project_root=str(root))
    registered = planner._read_projects_registry()
    assert "Build a feature X" not in registered
    assert str(root.resolve()) in registered


def test_month_proration_partial_week(tmp_path):
    """Partial ISO weeks in a month view get less than full capacity (B6)."""
    root = _make_project(tmp_path, "monthproj")
    payload = planner._plan_payload(str(root), "month")
    weeks = payload.get("weeks") or []
    assert weeks
    # At least one partial week at the month edge must be prorated below 20 h.
    assert any(week["capacity_hours"] < 20 for week in weeks)


def test_loopback_rejects_non_loopback_peers():
    """Only loopback IPs and known in-process labels are trusted (B9)."""
    assert planner._is_loopback_peer("127.0.0.1") is True
    assert planner._is_loopback_peer("::1") is True
    assert planner._is_loopback_peer("testclient") is True
    assert planner._is_loopback_peer("unix") is True
    assert planner._is_loopback_peer("203.0.113.9") is False
    assert planner._is_loopback_peer("evil.example") is False


def test_plan_delete_missing_project_root_returns_400(tmp_path):
    """DELETE /api/plan without project_root cannot clear the default project."""
    from starlette.testclient import TestClient as TC

    with TC(planner.build_app()) as client:
        resp = client.delete("/api/plan", params={"week": "2026-W47"})
    assert resp.status_code == 400
    assert "project_root" in resp.json()["error"]
