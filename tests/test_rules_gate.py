"""Mocked unit tests for the rules-first QA gate (Task 195).

The gate runs cheap deterministic checks (verdict parse, schema, budget,
allowlist) BEFORE any LLM judge call. All tests are offline: the judge is a
Mock, and the key assertion is that it is NEVER called when rules fail.

Run: `pytest tests/test_rules_gate.py -v` (repo root).
"""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

GATE_DIR = Path(__file__).parent.parent / "scripts" / "qa-rules-gate"
sys.path.insert(0, str(GATE_DIR))

from rules_gate import (  # noqa: E402
    UnparseableVerdict,
    check_allowlist,
    check_budget,
    check_schema,
    parse_verdict,
    run_gate,
)

PASSED_REPLY = """Vulnerabilities: none found.
Missing Tests: none.
Status: QA_PASSED (prose mirror of the machine verdict below).
VERDICT: QA_PASSED
CITE: mcp-decision-server/server.py:123
CITE: tests/test_rules_gate.py:45
"""

REJECTED_REPLY = """Vulnerabilities: missing null check.
VERDICT: QA_REJECTED
CITE: mcp-decision-server/server.py:999
"""


def test_parse_valid_passed_with_cites():
    verdict, cites = parse_verdict(PASSED_REPLY)
    assert verdict == "QA_PASSED"
    assert cites == [
        ("mcp-decision-server/server.py", 123),
        ("tests/test_rules_gate.py", 45),
    ]


def test_parse_valid_rejected():
    verdict, cites = parse_verdict(REJECTED_REPLY)
    assert verdict == "QA_REJECTED"
    assert cites == [("mcp-decision-server/server.py", 999)]


def test_parse_missing_verdict_raises():
    with pytest.raises(UnparseableVerdict):
        parse_verdict("Looks fine to me, ship it.\nNo machine verdict here.")


def test_parse_verdict_found_among_prose():
    verdict, _ = parse_verdict("Some long prose...\nVERDICT: QA_PASSED\nMore prose...")
    assert verdict == "QA_PASSED"


def test_schema_missing_field():
    violations = check_schema({"a": 1}, required=["a", "b"])
    assert violations == ["missing field: b"]


def test_schema_clean():
    assert check_schema({"a": 1, "b": 2}, required=["a", "b"]) == []


def test_budget_exceeded():
    assert check_budget(used=120_000, limit=100_000) != []


def test_budget_ok():
    assert check_budget(used=50_000, limit=100_000) == []


def test_allowlist_outside():
    violations = check_allowlist(["/etc/passwd"], roots=["/repo"])
    assert violations == ["path outside allowlist: /etc/passwd"]


def test_allowlist_inside():
    assert check_allowlist(["/repo/a.py"], roots=["/repo"]) == []


def test_gate_rules_fail_never_calls_judge():
    judge = Mock(return_value="QA_PASSED")
    result = run_gate(
        {"verdict_reply": REJECTED_REPLY, "paths": ["/etc/passwd"]},
        required=[],
        budget=(0, 1_000_000),
        allowlist_roots=["/repo"],
        judge=judge,
    )
    assert result.verdict == "QA_REJECTED"
    assert result.violations != []
    judge.assert_not_called()


def test_gate_clean_calls_judge_once():
    judge = Mock(return_value="QA_PASSED")
    result = run_gate(
        {"verdict_reply": PASSED_REPLY, "paths": ["/repo/a.py"]},
        required=[],
        budget=(10, 1_000_000),
        allowlist_roots=["/repo"],
        judge=judge,
    )
    assert result.verdict == "QA_PASSED"
    assert result.violations == []
    judge.assert_called_once()


def test_gate_clean_no_judge_passes():
    result = run_gate(
        {"verdict_reply": PASSED_REPLY, "paths": []},
        required=[],
        budget=(0, 1_000_000),
        allowlist_roots=["/repo"],
    )
    assert result.verdict == "QA_PASSED"
    assert result.judge_called is False
