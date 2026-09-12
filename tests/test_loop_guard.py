"""Unit tests for mcp-brain-bridge/loop_guard.py (Task 196).

Offline only: the spin guard is pure local JSONL logic — no network,
no model calls. BRAIN_SESSIONS_ROOT is redirected per test.
"""

import json
import sys
from pathlib import Path

BRIDGE_DIR = Path(__file__).parent.parent / "mcp-brain-bridge"
sys.path.insert(0, str(BRIDGE_DIR))

from loop_guard import record_attempt


def _root(tmp_path, monkeypatch):
    sessions = tmp_path / "sessions"
    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(sessions))
    return str(sessions)


def test_three_identical_hashes_stop(tmp_path, monkeypatch):
    _root(tmp_path, monkeypatch)
    assert record_attempt("t1", "aaa")["stop"] is False
    assert record_attempt("t1", "aaa")["stop"] is False
    third = record_attempt("t1", "aaa")
    assert third["stop"] is True
    assert third["history"] == ["aaa", "aaa", "aaa"]


def test_fresh_hash_resets_and_continues(tmp_path, monkeypatch):
    _root(tmp_path, monkeypatch)
    record_attempt("t2", "aaa")
    record_attempt("t2", "aaa")
    assert record_attempt("t2", "bbb")["stop"] is False
    assert record_attempt("t2", "bbb")["stop"] is False
    assert record_attempt("t2", "bbb")["stop"] is True


def test_per_task_isolation(tmp_path, monkeypatch):
    _root(tmp_path, monkeypatch)
    record_attempt("t3", "zzz")
    record_attempt("t3", "zzz")
    assert record_attempt("other", "zzz")["stop"] is False
    assert record_attempt("t3", "zzz")["stop"] is True


def test_corrupt_lines_tolerated(tmp_path, monkeypatch):
    root = _root(tmp_path, monkeypatch)
    log = Path(root) / "t4" / "loop_hashes.jsonl"
    log.parent.mkdir(parents=True)
    log.write_text('not json\n{"nope": 1}\n', encoding="utf-8")
    assert record_attempt("t4", "qqq")["stop"] is False
    assert record_attempt("t4", "qqq")["stop"] is False
    assert record_attempt("t4", "qqq")["stop"] is True


def test_bad_task_id_rejected(tmp_path, monkeypatch):
    import pytest

    _root(tmp_path, monkeypatch)
    with pytest.raises(ValueError):
        record_attempt("../../evil", "aaa")
    with pytest.raises(ValueError):
        record_attempt("", "aaa")


def test_bad_diff_hash_rejected(tmp_path, monkeypatch):
    import pytest

    _root(tmp_path, monkeypatch)
    for bad in (None, 123, "", "   "):
        with pytest.raises(ValueError):
            record_attempt("t5", bad)


def test_missing_hash_lines_skipped_amid_valid(tmp_path, monkeypatch):
    root = _root(tmp_path, monkeypatch)
    log = Path(root) / "t6" / "loop_hashes.jsonl"
    log.parent.mkdir(parents=True)
    log.write_text(
        '{"ts": 1, "hash": "kkk"}\n'
        '{"ts": 2}\n'
        '{"ts": 3, "hash": 42}\n'
        '{"ts": 4, "hash": ""}\n'
        '{"ts": 5, "hash": "kkk"}\n',
        encoding="utf-8",
    )
    assert record_attempt("t6", "kkk")["stop"] is True


def test_whitespace_stripped_equality_stops(tmp_path, monkeypatch):
    _root(tmp_path, monkeypatch)
    assert record_attempt("t7", "  aaa")["stop"] is False
    assert record_attempt("t7", "aaa")["stop"] is False
    third = record_attempt("t7", "aaa  ")
    assert third["stop"] is True
    assert third["history"] == ["aaa", "aaa", "aaa"]
