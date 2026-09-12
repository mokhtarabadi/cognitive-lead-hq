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
    monkeypatch.setattr(bridge, "_resolve_task_file", lambda tid: target)
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    out = bridge.build_diff_attach("99")
    assert "+added" in out


def test_build_diff_attach_no_diff_returns_empty(monkeypatch, tmp_path):
    target = tmp_path / "99-sample.md"
    target.write_text("# Task 99: no diff\n", encoding="utf-8")
    monkeypatch.setattr(bridge, "_resolve_task_file", lambda tid: target)
    assert bridge.build_diff_attach("99") == ""


def test_build_diff_attach_unresolvable_returns_empty(monkeypatch):
    monkeypatch.setattr(bridge, "_resolve_task_file", lambda tid: None)
    assert bridge.build_diff_attach("nope") == ""


def test_build_diff_attach_over_cap_truncates(monkeypatch, tmp_path):
    target = tmp_path / "99-sample.md"
    target.write_text(_task_text("x" * 50000), encoding="utf-8")
    monkeypatch.setattr(bridge, "_resolve_task_file", lambda tid: target)
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
    monkeypatch.setattr(bridge, "_resolve_task_file", lambda tid: target)
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    out = bridge.build_diff_attach("99")
    assert "```evil" not in out
    assert "evil" in out


def test_failsafe_qa_prompt_attaches_without_flag(monkeypatch, tmp_path):
    target = tmp_path / "99-sample.md"
    target.write_text(_task_text("+added"), encoding="utf-8")
    monkeypatch.setattr(bridge, "_resolve_task_file", lambda tid: target)
    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
    out = bridge._failsafe_qa_attach(
        "QA engineer, adversarial review please", "99")
    assert "+added" in out


def test_failsafe_normal_prompt_stays_empty(monkeypatch, tmp_path):
    target = tmp_path / "99-sample.md"
    target.write_text(_task_text("+added"), encoding="utf-8")
    monkeypatch.setattr(bridge, "_resolve_task_file", lambda tid: target)
    assert bridge._failsafe_qa_attach("fix the login bug", "99") == ""
