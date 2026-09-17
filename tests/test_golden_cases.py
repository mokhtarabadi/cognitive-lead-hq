"""Golden-case execution for retrieval plus eval (Task 249).

Validates the caller-owned JSON fixtures under ``tests/golden/``:
schema checks first, then execution through the pure modules.
Fixtures are read-only inputs: any test that mutates a fixture fails.
"""

import hashlib
import json
import sys
from pathlib import Path

GOLDEN_DIR = Path(__file__).parent / "golden"
BRIDGE_DIR = Path(__file__).parent.parent / "mcp-brain-bridge"
sys.path.insert(0, str(BRIDGE_DIR))

from authority_retrieval import retrieve  # noqa: E402
from eval_harness import aggregate_report, score_case  # noqa: E402


def _load(name):
    path = GOLDEN_DIR / name
    return path, json.loads(path.read_text())


def _hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_retrieval_golden_schema_valid():
    _, doc = _load("authority_retrieval_cases.json")
    assert doc["schema_version"] == 1
    for case in doc["cases"]:
        assert {"case_id", "query", "candidates", "expected"} <= set(case)
        for cand in case["candidates"]:
            assert {"candidate_id", "source", "text", "local_score", "chunk_id"} <= set(cand)


def test_eval_golden_schema_valid():
    _, doc = _load("eval_harness_cases.json")
    assert doc["schema_version"] == 1
    for case in doc["cases"]:
        assert {"case_id", "trace", "expected"} <= set(case)
        assert {"citations", "grounding", "rules", "parse_ok", "qa_repairs"} <= set(case["expected"])


def test_retrieval_golden_missing_field_rejected():
    import pytest

    with pytest.raises((KeyError, TypeError)):
        retrieve("q", {"decision": [{"candidate_id": "x"}]})


def test_retrieval_golden_cases_execute():
    _, doc = _load("authority_retrieval_cases.json")
    for case in doc["cases"]:
        by_source = {}
        for cand in case["candidates"]:
            by_source.setdefault(cand["source"], []).append(cand)
        adapters = {s: (lambda items: (lambda q: items))(items) for s, items in by_source.items()}
        result = retrieve(
            case["query"],
            adapters,
            gather_limit=case["expected"].get("gather_limit", 20),
            narrow_limit=case["expected"].get("narrow_limit", 5),
        )
        ids = [c["candidate_id"] for c in result["candidates"]]
        if "top_candidate_id" in case["expected"]:
            assert ids[0] == case["expected"]["top_candidate_id"]
        if "selected_ids" in case["expected"]:
            assert ids == case["expected"]["selected_ids"]


def test_eval_golden_cases_execute():
    _, doc = _load("eval_harness_cases.json")
    rows = [score_case(case["trace"], case["expected"]) for case in doc["cases"]]
    report = aggregate_report(rows)
    assert report["case_count"] == len(doc["cases"])
    first = rows[0]
    assert first["parse_ok"] is True
    assert first["qa_repair_count"] == 1
    assert first["cost_usd"] == 0.01
    assert rows[1]["zac_violation_count"] == 2


def test_golden_fixtures_unmodified():
    paths = [GOLDEN_DIR / "authority_retrieval_cases.json", GOLDEN_DIR / "eval_harness_cases.json"]
    before = {p.name: _hash(p) for p in paths}
    test_retrieval_golden_cases_execute()
    test_eval_golden_cases_execute()
    after = {p.name: _hash(p) for p in paths}
    assert before == after
