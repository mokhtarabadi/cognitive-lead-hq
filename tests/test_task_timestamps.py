# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
"""Measured task timing: claim stamp, QA stamp, closure stamp, duration, lint gate.

Why: the planner used to report "hours spent" by summing the estimate, so the panel
could never show what a task actually cost. These tests pin the three stamps and the
arithmetic that turns them into a duration, including the write-once rule.
"""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "mcp-planner-server"))
sys.path.insert(0, str(REPO / "mcp-context-server"))


@pytest.fixture(autouse=True)
def _isolated_project_registry(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "PLANNER_PROJECTS_REGISTRY", str(tmp_path / "planner-projects.json")
    )


_PLANNER_SPEC = importlib.util.spec_from_file_location(
    "planner_server_timestamps", REPO / "mcp-planner-server" / "server.py"
)
planner = importlib.util.module_from_spec(_PLANNER_SPEC)
_PLANNER_SPEC.loader.exec_module(planner)

_LINT_SPEC = importlib.util.spec_from_file_location(
    "lint_server_timestamps", REPO / "mcp-lint-server" / "server.py"
)
lint = importlib.util.module_from_spec(_LINT_SPEC)
_LINT_SPEC.loader.exec_module(lint)

_GITOPS_SPEC = importlib.util.spec_from_file_location(
    "gitops_timestamps", REPO / "mcp-context-server" / "gitops.py"
)
gitops = importlib.util.module_from_spec(_GITOPS_SPEC)
_GITOPS_SPEC.loader.exec_module(gitops)

_SERVER_SPEC = importlib.util.spec_from_file_location(
    "context_server_timestamps", REPO / "mcp-context-server" / "server.py"
)
server = importlib.util.module_from_spec(_SERVER_SPEC)
_SERVER_SPEC.loader.exec_module(server)


TASK_BODY = (
    "# Task 9001: timing sample\n\n"
    "**File:** `tasks/backlog/9001-timing-sample.md`\n"
    "**Source:** manager\n"
    "**Type:** bug\n"
    "**Status:** open\n"
    "\n"
    "## Goal\n\nDo the thing.\n"
)


def _task(tmp_path, body=TASK_BODY):
    path = tmp_path / "tasks" / "backlog" / "9001-timing-sample.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def test_stamp_is_written_after_status(tmp_path):
    path = _task(tmp_path)

    wrote = gitops.stamp_task_header(path, "Started")

    assert wrote is True
    lines = path.read_text(encoding="utf-8").splitlines()
    idx = next(i for i, l in enumerate(lines) if l.startswith("**Status:**"))
    assert lines[idx + 1].startswith("**Started:** 20")
    assert lines[idx + 1].endswith("Z")


def test_stamp_is_write_once(tmp_path):
    path = _task(tmp_path)
    gitops.stamp_task_header(path, "Started")
    first = path.read_text(encoding="utf-8")

    wrote_again = gitops.stamp_task_header(path, "Started")

    assert wrote_again is False
    assert path.read_text(encoding="utf-8") == first


def test_planner_stamp_helper_matches_the_contract(tmp_path):
    path = _task(tmp_path)

    stamped = planner._stamp_header_once(path.read_text(encoding="utf-8"), "Finished")

    assert "**Finished:**" in stamped
    assert planner._stamp_header_once(stamped, "Finished") == stamped


def test_task_brief_computes_durations_and_never_zero_fills():
    record = {
        "name": "9001-timing-sample.md",
        "path": "tasks/completed/9001-timing-sample.md",
        "title": "timing sample",
        "lane": "completed",
        "status": "closed",
        "estimate_hours": 3.0,
        "started_at": "2026-10-25T10:00:00Z",
        "submitted_at": "2026-10-25T11:30:00Z",
        "finished_at": "2026-10-25T12:00:00Z",
    }

    brief = planner._task_brief(record)

    assert brief["elapsed_seconds"] == 7200
    assert brief["qa_wait_seconds"] == 5400

    # A missing finish is "not measured", not instant.
    partial = dict(record)
    partial["finished_at"] = None
    assert planner._task_brief(partial)["elapsed_seconds"] is None


@pytest.mark.parametrize(
    "stamp",
    [
        "2026-10-25T14:20:31Z",
    ],
)
def test_lint_accepts_iso_utc_stamps(stamp):
    content = f"# Task 1: x\n\n**Started:** {stamp}\n"
    assert lint._check_planner_metadata(content, "x.md") == []


@pytest.mark.parametrize(
    "stamp",
    [
        "2026-10-25 14:20:31",
        "25/10/2026",
        "2026-10-25T14:20:31+02:00",
        "now",
    ],
)
def test_lint_rejects_non_utc_or_free_text_stamps(stamp):
    content = f"# Task 1: x\n\n**Started:** {stamp}\n"
    issues = lint._check_planner_metadata(content, "x.md")
    assert issues, f"lint accepted a stamp that cannot be compared: {stamp}"


def test_lint_rejects_a_finish_before_the_start():
    content = (
        "# Task 1: x\n\n"
        "**Started:** 2026-10-25T12:00:00Z\n"
        "**Finished:** 2026-10-25T11:00:00Z\n"
    )
    issues = lint._check_planner_metadata(content, "x.md")
    assert any("earlier than" in i for i in issues), issues


def test_start_is_recovered_from_git_when_the_header_has_none(tmp_path):
    """A hand-moved task still gets a measured duration, not a silent gap."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    task = repo / "tasks" / "in-progress" / "9002-hand-moved.md"
    task.parent.mkdir(parents=True)
    task.write_text(
        "# Task 9002: hand moved\n\n**File:** `tasks/in-progress/9002-hand-moved.md`\n"
        "**Status:** in-progress\n",
        encoding="utf-8",
    )
    env = {
        "GIT_AUTHOR_DATE": "2026-10-24T08:30:00+00:00",
        "GIT_COMMITTER_DATE": "2026-10-24T08:30:00+00:00",
    }
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.email=t@t",
            "-c",
            "user.name=t",
            "commit",
            "-qm",
            "add task",
        ],
        cwd=repo,
        check=True,
        env={**os.environ, **env},
    )

    recovered = gitops.backfill_started_from_git(repo, task)

    assert recovered == "2026-10-24T08:30:00Z"
    assert gitops.stamp_task_header(task, "Started", recovered) is True
    assert "**Started:** 2026-10-24T08:30:00Z" in task.read_text(encoding="utf-8")


def test_start_stamp_falls_back_to_mtime_and_never_invents_now(tmp_path):
    """No git history: the file's own mtime is the next honest source."""
    repo = tmp_path / "repo2"
    repo.mkdir()
    task = repo / "tasks" / "in-progress" / "9003-untracked.md"
    task.parent.mkdir(parents=True)
    task.write_text("# Task 9003\n\n**Status:** in-progress\n", encoding="utf-8")
    os.utime(task, (1700000000, 1700000000))

    stamp = gitops.task_start_stamp(repo, task)

    assert stamp == "2023-11-14T22:13:20Z"


def test_sync_task_times_is_idempotent(tmp_path):
    repo = tmp_path / "repo3"
    task = repo / "tasks" / "in-progress" / "9004-timing.md"
    task.parent.mkdir(parents=True)
    task.write_text(
        "# Task 9004\n\n**File:** `tasks/in-progress/9004-timing.md`\n"
        "**Status:** in-progress\n",
        encoding="utf-8",
    )
    os.utime(task, (1700000000, 1700000000))

    first = server.sync_task_times(str(repo), "in-progress")
    content = task.read_text(encoding="utf-8")
    second = server.sync_task_times(str(repo), "in-progress")

    assert "**Started:**" in content
    assert "Stamped 1 task" in first
    assert "Nothing to stamp" in second
    assert task.read_text(encoding="utf-8") == content


def test_naive_stamp_is_not_interpreted_as_utc():
    """A hand-edited local time must not be silently read as UTC."""
    record = {
        "name": "9001.md",
        "started_at": "2026-10-25 14:20:31",
        "finished_at": "2026-10-25T15:00:00Z",
    }
    brief = planner._task_brief(record)
    assert brief["elapsed_seconds"] is None


def test_negative_duration_reports_not_measured():
    record = {
        "name": "9001.md",
        "started_at": "2026-10-25T12:00:00Z",
        "finished_at": "2026-10-25T11:00:00Z",
    }
    assert planner._task_brief(record)["elapsed_seconds"] is None


def test_sync_refuses_the_completed_lane(tmp_path):
    repo = tmp_path / "repo4"
    (repo / "tasks" / "completed").mkdir(parents=True)
    out = server.sync_task_times(str(repo), "completed")
    assert "in-progress or qa" in out


def test_sprint_stats_separates_measured_from_estimated(tmp_path):
    repo = tmp_path / "repo5"
    lane = repo / "tasks" / "completed"
    lane.mkdir(parents=True)
    (lane / "9010-done.md").write_text(
        "# Task 9010: done\n\n**File:** `tasks/completed/9010-done.md`\n"
        "**Status:** closed\n**Estimate:** 5h\n"
        "**Started:** 2026-10-25T10:00:00Z\n"
        "**Finished:** 2026-10-25T12:00:00Z\n",
        encoding="utf-8",
    )
    out = planner.sprint_stats(str(repo))
    assert "Completed estimated: 5.0h" in out
    assert "Completed measured: 2.00h" in out


def test_duplicate_start_stamp_is_rejected():
    content = (
        "# Task 1: x\n\n"
        "**Started:** 2026-10-25T10:00:00Z\n"
        "**Started:** 2026-10-25T11:00:00Z\n"
    )
    issues = lint._check_planner_metadata(content, "x.md")
    assert any("appears 2 times" in i for i in issues), issues


def test_claim_next_stamps_started_once(tmp_path):
    repo = tmp_path / "repo6"
    backlog = repo / "tasks" / "backlog"
    backlog.mkdir(parents=True)
    task = backlog / "0002-claim-me.md"
    task.write_text(
        "# Task 0002: claim me\n\n**File:** `tasks/backlog/0002-claim-me.md`\n"
        "**Status:** open\n**Estimate:** 1h\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "seed"],
        cwd=repo,
        check=True,
    )

    assert "claim_next succeeded" in planner.claim_next(str(repo), "2")
    moved = repo / "tasks" / "in-progress" / "0002-claim-me.md"
    first = moved.read_text(encoding="utf-8")
    assert "**Started:**" in first

    # Re-claim path: put it back and claim again; the original start must survive.
    moved.rename(task)
    task.write_text(
        first.replace("**Status:** in-progress", "**Status:** open"), encoding="utf-8"
    )
    assert "claim_next succeeded" in planner.claim_next(str(repo), "2")
    assert moved.read_text(encoding="utf-8").count("**Started:**") == 1
