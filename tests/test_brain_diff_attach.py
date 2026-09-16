"""Tests for the brain_turn include_diff path (task file changed hunks).

Offline only: covers diff extraction from task text and the attach
builder (present / absent / unresolvable / over-cap). The live LLM path
(httpx POST) is never touched.
"""

import sys
from pathlib import Path

import pytest

BRIDGE_DIR = Path(__file__).parent.parent / "mcp-brain-bridge"
sys.path.insert(0, str(BRIDGE_DIR))

import server as bridge


def _task_text(diff_body: str) -> str:
    return (
        "# Task 99: Sample\n\nSome working content.\n\n"
        "<!-- BEGIN_GIT_DIFF -->\n" + diff_body + "\n<!-- END_GIT_DIFF -->\n"
    )


def test_extract_diff_present():
    text = _task_text("diff --git a/x b/x\n+new line")
    out = bridge.extract_task_diff(text)
    assert "diff --git a/x b/x" in out
    assert "+new line" in out


def test_extract_diff_absent_returns_empty():
    assert bridge.extract_task_diff("# Task 99: no diff here\n") == ""


def test_extract_diff_multiple_blocks_joined():
    text = (
        "<!-- BEGIN_GIT_DIFF -->\nhunk-one\n<!-- END_GIT_DIFF -->\n"
        "middle\n"
        "<!-- BEGIN_GIT_DIFF -->\nhunk-two\n<!-- END_GIT_DIFF -->\n"
    )
    out = bridge.extract_task_diff(text)
    assert "hunk-one" in out
    assert "hunk-two" in out


def test_extract_diff_unclosed_cuts_to_eof():
    text = "<!-- BEGIN_GIT_DIFF -->\npartial hunk, no end"
    out = bridge.extract_task_diff(text)
    assert "partial hunk" in out


def test_build_diff_attach_resolved_with_diff(monkeypatch, tmp_path):
    target = tmp_path / "99-sample.md"
    target.write_text(_task_text("+added"), encoding="utf-8")
    monkeypatch.setattr(
        bridge, "_resolve_task_file",
        lambda tid, project_root=None: target)
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    out = bridge.build_diff_attach("99")
    assert "+added" in out


def test_build_diff_attach_no_diff_returns_inline_empty_note(
        monkeypatch, tmp_path):
    # Re-QA repair: stderr is invisible to the model, so an empty diff
    # returns an inline EMPTY note (never silent "") with the remedy.
    target = tmp_path / "99-sample.md"
    target.write_text("# Task 99: no diff\n", encoding="utf-8")
    monkeypatch.setattr(
        bridge, "_resolve_task_file",
        lambda tid, project_root=None: target)
    out = bridge.build_diff_attach("99")
    assert "EMPTY" in out
    assert "stage_and_inject_diff" in out


def test_build_diff_attach_unresolvable_returns_inline_note(monkeypatch):
    # Re-QA repair: unresolvable file returns an inline UNAVAILABLE
    # note (never silent "") naming project_root as the remedy.
    monkeypatch.setattr(
        bridge, "_resolve_task_file", lambda tid, project_root=None: None)
    out = bridge.build_diff_attach("nope")
    assert "UNAVAILABLE" in out
    assert "project_root" in out


def test_build_diff_attach_over_cap_truncates(monkeypatch, tmp_path):
    target = tmp_path / "99-sample.md"
    target.write_text(_task_text("x" * 50000), encoding="utf-8")
    monkeypatch.setattr(
        bridge, "_resolve_task_file",
        lambda tid, project_root=None: target)
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    monkeypatch.setattr(bridge, "_TASK_DIFF_CAP", 100)
    out = bridge.build_diff_attach("99")
    assert "truncated" in out
    assert len(out) < 50000


def test_extract_diff_empty_pair_yields_empty():
    text = "<!-- BEGIN_GIT_DIFF --><!-- END_GIT_DIFF -->\n"
    assert bridge.extract_task_diff(text) == ""


def test_build_diff_attach_breaks_embedded_fences(monkeypatch, tmp_path):
    target = tmp_path / "99-sample.md"
    target.write_text(_task_text("line\n```evil\nline"), encoding="utf-8")
    monkeypatch.setattr(
        bridge, "_resolve_task_file",
        lambda tid, project_root=None: target)
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    out = bridge.build_diff_attach("99")
    assert "```evil" not in out
    assert "evil" in out


def test_failsafe_qa_prompt_attaches_without_flag(monkeypatch, tmp_path):
    target = tmp_path / "99-sample.md"
    target.write_text(_task_text("+added"), encoding="utf-8")
    monkeypatch.setattr(
        bridge, "_resolve_task_file",
        lambda tid, project_root=None: target)
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    out = bridge._failsafe_qa_attach(
        "QA engineer, adversarial review please", "99")
    assert "+added" in out


def test_failsafe_normal_prompt_stays_empty(monkeypatch, tmp_path):
    target = tmp_path / "99-sample.md"
    target.write_text(_task_text("+added"), encoding="utf-8")
    monkeypatch.setattr(
        bridge, "_resolve_task_file",
        lambda tid, project_root=None: target)
    assert bridge._failsafe_qa_attach("fix the login bug", "99") == ""


def _mk_project(tmp_path, name="proj"):
    proj = tmp_path / name
    lane = proj / "tasks" / "qa"
    lane.mkdir(parents=True)
    (lane / "999-sample.md").write_text(
        _task_text("+via-project-root"), encoding="utf-8")
    return proj


def test_resolve_task_file_honors_project_root(monkeypatch, tmp_path):
    proj = _mk_project(tmp_path)
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setattr(bridge, "_workspace_root", lambda: empty)
    found = bridge._resolve_task_file("999", project_root=str(proj))
    assert found is not None and found.name == "999-sample.md"
    assert bridge._resolve_task_file("999") is None


def test_resolve_task_file_project_root_without_tasks_falls_back(
        monkeypatch, tmp_path):
    lane = tmp_path / "tasks" / "qa"
    lane.mkdir(parents=True)
    (lane / "999-sample.md").write_text(
        _task_text("+via-workspace"), encoding="utf-8")
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    bare = tmp_path / "bare"
    bare.mkdir()
    found = bridge._resolve_task_file("999", project_root=str(bare))
    assert found is not None and found.name == "999-sample.md"


def test_build_diff_attach_via_project_root(monkeypatch, tmp_path):
    proj = _mk_project(tmp_path)
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setattr(bridge, "_workspace_root", lambda: empty)
    out = bridge.build_diff_attach("999", project_root=str(proj))
    assert "+via-project-root" in out


def test_build_diff_attach_unresolvable_says_so(monkeypatch, capsys):
    monkeypatch.setattr(
        bridge, "_resolve_task_file",
        lambda tid, project_root=None: None)
    out = bridge.build_diff_attach("nope")
    assert "UNAVAILABLE" in out  # inline note for the model, not ""
    assert "unresolvable" in capsys.readouterr().err  # stderr kept too


def test_build_diff_attach_empty_diff_says_so(monkeypatch, tmp_path, capsys):
    target = tmp_path / "99-sample.md"
    target.write_text("# Task 99: no diff\n", encoding="utf-8")
    monkeypatch.setattr(
        bridge, "_resolve_task_file",
        lambda tid, project_root=None: target)
    out = bridge.build_diff_attach("99")
    assert "EMPTY" in out  # inline note for the model, not ""
    assert "no Factual Git Diff block" in capsys.readouterr().err
