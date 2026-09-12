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


def test_allowlist_relative_inside():
    assert check_allowlist(["a/b.py"], roots=["."]) == []


def test_allowlist_relative_escape(tmp_path, monkeypatch):
    sub = tmp_path / "sub"
    sub.mkdir()
    monkeypatch.chdir(sub)
    assert check_allowlist(["../evil.py"], roots=["."]) != []


def test_parse_two_verdicts_raise():
    reply = "VERDICT: QA_PASSED\nSome prose.\nVERDICT: QA_REJECTED\n"
    with pytest.raises(UnparseableVerdict):
        parse_verdict(reply)


def test_parse_leading_space_verdict():
    verdict, _ = parse_verdict("  VERDICT: QA_PASSED  \n")
    assert verdict == "QA_PASSED"


def test_gate_judge_garbage_rejected():
    judge = Mock(return_value="MAYBE")
    result = run_gate(
        {"verdict_reply": PASSED_REPLY, "paths": []},
        required=[],
        budget=(0, 1_000_000),
        allowlist_roots=["/repo"],
        judge=judge,
    )
    assert result.verdict == "QA_REJECTED"
    assert result.judge_called is True
    assert any("invalid judge verdict" in v for v in result.violations)


def test_schema_nested_missing():
    assert check_schema({"a": {"b": 1}}, required=["a.b", "a.c"]) == [
        "missing field: a.c"
    ]


def test_parse_cite_trailing_period():
    verdict, cites = parse_verdict("CITE: foo.py:12.\nVERDICT: QA_PASSED\n")
    assert verdict == "QA_PASSED"
    assert cites == [("foo.py", 12)]


def test_allowlist_sibling_prefix_rejected():
    violations = check_allowlist(
        ["/repo/allow-evil/x.py"], roots=["/repo/allow"]
    )
    assert violations == ["path outside allowlist: /repo/allow-evil/x.py"]


def test_allowlist_symlink_escape_rejected(tmp_path):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    secret = tmp_path / "secret.txt"
    secret.write_text("top secret")
    link = allowed / "link.py"
    link.symlink_to(secret)
    assert check_allowlist([str(link)], roots=[str(allowed)]) == [
        f"path outside allowlist: {link}"
    ]


def test_allowlist_symlink_inside_passes(tmp_path):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    real = allowed / "real.py"
    real.write_text("x = 1")
    link = allowed / "link.py"
    link.symlink_to(real)
    assert check_allowlist([str(link)], roots=[str(allowed)]) == []


def test_parse_indented_second_marker_raises():
    reply = "VERDICT: QA_PASSED\n  VERDICT: QA_REJECTED\n"
    with pytest.raises(UnparseableVerdict):
        parse_verdict(reply)


def test_gate_judge_none_rejected():
    judge = Mock(return_value=None)
    result = run_gate(
        {"verdict_reply": PASSED_REPLY, "paths": []},
        required=[],
        budget=(0, 1_000_000),
        allowlist_roots=["/repo"],
        judge=judge,
    )
    assert result.verdict == "QA_REJECTED"
    assert result.judge_called is True
    assert any("invalid judge verdict" in v for v in result.violations)


def test_schema_deep_nested_and_nondict_mid():
    assert check_schema({"a": {"b": {"c": 1}}}, required=["a.b.c"]) == []
    assert check_schema({"a": {"b": {"c": 1}}}, required=["a.b.d"]) == [
        "missing field: a.b.d"
    ]
    assert check_schema({"a": 5}, required=["a.b"]) == ["missing field: a.b"]


def test_parse_cite_version_and_all_punct_tails():
    reply = "CITE: pkg/v1.2:34\nCITE: foo.py:12.,;:!?\nVERDICT: QA_PASSED\n"
    verdict, cites = parse_verdict(reply)
    assert verdict == "QA_PASSED"
    assert cites == [("pkg/v1.2", 34), ("foo.py", 12)]
