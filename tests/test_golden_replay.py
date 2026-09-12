"""Unit tests for the golden-task replay harness (Task 197).

Offline only: every test injects a stub ``ask_fn``. No model, no
network, no live calls.
"""

import hashlib
import sys
from pathlib import Path

BRIDGE_DIR = Path(__file__).parent.parent / "mcp-brain-bridge"
sys.path.insert(0, str(BRIDGE_DIR))

from golden_replay import prompt_hash, record, replay


def _echo_map(mapping):
    def ask(q):
        return mapping[q]
    return ask


def _corpus():
    return [
        {"name": "terse refusal", "ask": "q1", "expect": "no"},
        {"name": "quoted term", "ask": "q2", "expect": "cache hit"},
        {"name": "two words", "ask": "q3", "expect": "all green"},
    ]


def test_replay_three_pass():
    mapping = {"q1": "no", "q2": "cache hit", "q3": "all green"}
    report = replay(_echo_map(mapping), _corpus(), "prompt v1")
    assert report["passed"] == 3
    assert report["failed"] == 0
    assert all(r["ok"] for r in report["results"])


def test_replay_one_mismatch():
    mapping = {"q1": "no", "q2": "cache MISS", "q3": "all green"}
    report = replay(_echo_map(mapping), _corpus(), "prompt v1")
    assert report["passed"] == 2
    assert report["failed"] == 1
    bad = next(r for r in report["results"] if not r["ok"])
    assert bad["name"] == "quoted term"
    assert bad["expected"] == "cache hit"
    assert bad["got"] == "cache MISS"


def test_replay_scores_attributed_to_prompt_hash():
    mapping = {"q1": "no", "q2": "cache hit", "q3": "all green"}
    report = replay(_echo_map(mapping), _corpus(), "prompt v1")
    assert report["prompt_hash"] == hashlib.sha256(b"prompt v1").hexdigest()
    other = replay(_echo_map(mapping), _corpus(), "prompt v2")
    assert other["prompt_hash"] != report["prompt_hash"]


def test_replay_empty_corpus_scores_zero():
    report = replay(_echo_map({}), [], "prompt v1")
    assert report["passed"] == 0
    assert report["failed"] == 0
    assert report["results"] == []


def test_replay_normalizes_whitespace():
    mapping = {"q1": "  no\n", "q2": "\tcache   hit ", "q3": "all\ngreen"}
    report = replay(_echo_map(mapping), _corpus(), "prompt v1")
    assert report["passed"] == 3
    assert report["failed"] == 0


def test_record_round_trip(tmp_path):
    import json as _json

    report = replay(
        _echo_map({"q1": "a"}),
        [{"name": "n1", "ask": "q1", "expect": "a"}],
        "prompt v9",
    )
    path = record(report, sessions_root=tmp_path)
    assert path == tmp_path / "golden_runs.jsonl"
    rows = [_json.loads(line) for line in
            path.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1
    assert rows[0]["prompt_hash"] == report["prompt_hash"]
    assert rows[0]["passed"] == 1
    assert rows[0]["total"] == 1
    assert "ts" in rows[0]
