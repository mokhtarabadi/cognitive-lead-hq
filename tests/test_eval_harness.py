"""Unit tests for the offline eval harness (Task 249).

TDD red-green: written first against the planned ``eval_harness``
module contract. Pure and offline only: structured traces in,
report rows out. Missing cost/latency stays null, never zero.
"""

import sys
from pathlib import Path

BRIDGE_DIR = Path(__file__).parent.parent / "mcp-brain-bridge"
sys.path.insert(0, str(BRIDGE_DIR))

from eval_harness import aggregate_report, scan_zac, score_case  # noqa: E402


def _trace(**over):
    base = {
        "case_id": "case-1",
        "parse_ok": True,
        "citations": ["decision-001"],
        "grounding": {"claim-001": ["decision-001"]},
        "rule_results": {"rule-001": True},
        "operations": [{"kind": "shell", "command": "pytest tests/ -q"}],
        "qa_repairs": 1,
        "cost_usd": 0.01,
        "latency_ms": 125.0,
    }
    base.update(over)
    return base


def _expected(**over):
    base = {
        "citations": ["decision-001"],
        "grounding": [{"claim_id": "claim-001", "supported_by": ["decision-001"]}],
        "rules": [{"rule_id": "rule-001", "passed": True}],
    }
    base.update(over)
    return base


def test_parse_rate_all_pass():
    rows = [score_case(_trace(), _expected()), score_case(_trace(), _expected())]
    assert aggregate_report(rows)["parse_rate"] == 1.0


def test_parse_rate_partial_pass():
    rows = [score_case(_trace(), _expected()), score_case(_trace(parse_ok=False), _expected())]
    assert aggregate_report(rows)["parse_rate"] == 0.5


def test_citation_rate_counts_expected_coverage():
    row = score_case(_trace(citations=["decision-001", "extra-009"]), _expected())
    assert (row["citation_hits"], row["citation_expected"]) == (1, 1)


def test_grounding_requires_full_support():
    row = score_case(
        _trace(grounding={"claim-001": ["decision-001"]}),
        _expected(
            grounding=[
                {"claim_id": "claim-001", "supported_by": ["decision-001", "decision-002"]},
            ]
        ),
    )
    assert (row["grounding_hits"], row["grounding_expected"]) == (0, 1)


def test_rule_pass_missing_actual_counts_as_failure():
    row = score_case(_trace(rule_results={}), _expected())
    assert (row["rules_passed"], row["rules_expected"]) == (0, 1)


def test_zac_scan_detects_direct_git_ops():
    ops = [
        {"kind": "shell", "command": "git add foo.py"},
        {"kind": "operation", "name": "git.commit"},
        {"kind": "shell", "command": "GIT PUSH origin main"},
    ]
    count, clean = scan_zac(ops)
    assert count == 3
    assert clean is False


def test_zac_scan_ignores_prose_and_docs():
    count, clean = scan_zac([{"kind": "shell", "command": "pytest tests/ -q"}])
    assert (count, clean) == (0, True)
    row = score_case(_trace(), _expected())
    assert (row["zac_violation_count"], row["zac_clean"]) == (0, True)


def test_qa_repair_totals_and_mean():
    rows = [
        score_case(_trace(qa_repairs=1), _expected()),
        score_case(_trace(qa_repairs=3), _expected()),
    ]
    report = aggregate_report(rows)
    assert report["qa_repair_count_total"] == 4
    assert report["qa_repair_count_mean"] == 2.0


def test_cost_columns_preserve_values():
    row = score_case(_trace(cost_usd=0.01), _expected())
    assert row["cost_usd"] == 0.01
    report = aggregate_report([row, score_case(_trace(cost_usd=0.03), _expected())])
    assert report["cost_total_usd"] == 0.04
    assert report["cost_observed_case_count"] == 2


def test_latency_columns_preserve_values():
    row = score_case(_trace(latency_ms=125.0), _expected())
    assert row["latency_ms"] == 125.0
    report = aggregate_report([row, score_case(_trace(latency_ms=175.0), _expected())])
    assert report["latency_mean_ms"] == 150.0
    assert report["latency_observed_case_count"] == 2


def test_missing_cost_latency_stay_null():
    row = score_case(_trace(cost_usd=None, latency_ms=None), _expected())
    assert row["cost_usd"] is None
    assert row["latency_ms"] is None


def test_aggregate_ignores_missing_cost_latency():
    rows = [
        score_case(_trace(cost_usd=0.02, latency_ms=100.0), _expected()),
        score_case(_trace(cost_usd=None, latency_ms=None), _expected()),
    ]
    report = aggregate_report(rows)
    assert report["cost_total_usd"] == 0.02
    assert report["cost_mean_usd"] == 0.02
    assert report["latency_mean_ms"] == 100.0
    assert report["cost_observed_case_count"] == 1
    assert report["latency_observed_case_count"] == 1


def test_empty_input_defined_report():
    report = aggregate_report([])
    assert report["case_count"] == 0
    assert report["parse_rate"] is None
    assert report["rows"] == []


def test_missing_qa_repairs_field_stays_null():
    trace = _trace()
    del trace["qa_repairs"]
    assert score_case(trace, _expected())["qa_repair_count"] is None


def test_null_qa_repairs_stays_null():
    assert score_case(_trace(qa_repairs=None), _expected())["qa_repair_count"] is None


def test_explicit_zero_qa_repairs_preserved():
    assert score_case(_trace(qa_repairs=0), _expected())["qa_repair_count"] == 0


def test_aggregate_excludes_missing_qa_counts():
    rows = [
        score_case(_trace(qa_repairs=2), _expected()),
        score_case(_trace(qa_repairs=None), _expected()),
    ]
    report = aggregate_report(rows)
    assert report["qa_repair_count_total"] == 2
    assert report["qa_repair_count_mean"] == 2.0
    assert report["qa_repair_observed_case_count"] == 1


def test_aggregate_all_missing_qa_counts_null():
    missing = _trace(qa_repairs=None)
    absent = _trace()
    del absent["qa_repairs"]
    rows = [score_case(missing, _expected()), score_case(absent, _expected())]
    report = aggregate_report(rows)
    assert report["qa_repair_count_total"] is None
    assert report["qa_repair_count_mean"] is None
    assert report["qa_repair_observed_case_count"] == 0
