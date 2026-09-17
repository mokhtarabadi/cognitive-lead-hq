"""Unit tests for authority-ranked retrieval (Task 249).

TDD red-green: these tests were written first against the planned
``authority_retrieval`` module contract. Pure and offline only.
"""

import sys
from pathlib import Path

BRIDGE_DIR = Path(__file__).parent.parent / "mcp-brain-bridge"
sys.path.insert(0, str(BRIDGE_DIR))

from authority_retrieval import (  # noqa: E402
    AUTHORITY_WEIGHTS,
    gather_top_candidates,
    narrow_with_chunk_overlap,
    overlap,
    retrieve,
    tokenize,
)


def _cand(cid, source, score=0.5, text="sample text", chunk=None):
    return {
        "candidate_id": cid,
        "source": source,
        "text": text,
        "local_score": score,
        "chunk_id": chunk or (cid + "-chunk"),
    }


def _adapters(**by_source):
    calls = {}

    def make(source, items):
        def adapter(query):
            calls[source] = calls.get(source, 0) + 1
            return items

        return adapter

    return {s: make(s, items) for s, items in by_source.items()}, calls


def test_decision_outranks_memory_despite_lower_score():
    adapters, _ = _adapters(
        decision=[_cand("d1", "decision", score=0.1)],
        memory=[_cand("m1", "memory", score=0.99)],
        repo=[],
        web=[],
    )
    result = retrieve("q", adapters)
    assert [c["candidate_id"] for c in result["candidates"]][0] == "d1"


def test_memory_outranks_repo():
    adapters, _ = _adapters(
        memory=[_cand("m1", "memory", score=0.1)],
        repo=[_cand("r1", "repo", score=0.99)],
    )
    result = retrieve("q", adapters)
    assert [c["candidate_id"] for c in result["candidates"]][0] == "m1"


def test_repo_outranks_web():
    adapters, _ = _adapters(
        repo=[_cand("r1", "repo", score=0.1)],
        web=[_cand("w1", "web", score=0.99)],
    )
    result = retrieve("q", adapters)
    assert [c["candidate_id"] for c in result["candidates"]][0] == "r1"


def test_low_authority_high_score_never_overtakes():
    adapters, _ = _adapters(
        decision=[_cand("d1", "decision", score=0.0)],
        web=[_cand("w1", "web", score=1.0)],
    )
    result = retrieve("q", adapters)
    ids = [c["candidate_id"] for c in result["candidates"]]
    assert ids.index("d1") < ids.index("w1")


def test_gather_caps_at_twenty_after_combining():
    adapters, _ = _adapters(
        decision=[_cand(f"d{i}", "decision") for i in range(12)],
        memory=[_cand(f"m{i}", "memory") for i in range(12)],
    )
    top, gathered = gather_top_candidates("q", adapters)
    assert gathered == 24
    assert len(top) == 20


def test_narrow_returns_at_most_five():
    ranked = [_cand(f"d{i}", "decision", text=f"unique words {i} xyz") for i in range(10)]
    selected, _ = narrow_with_chunk_overlap(ranked, narrow_limit=5)
    assert len(selected) == 5


def test_overlapping_chunks_preferred():
    ranked = [
        _cand("a", "decision", text="authority retrieval chunk overlap rules"),
        _cand("b", "decision", text="chunk overlap rules for retrieval ranking"),
        _cand("c", "decision", text="unrelated cooking recipes entirely"),
    ]
    selected, pairs = narrow_with_chunk_overlap(ranked, narrow_limit=2)
    assert [c["candidate_id"] for c in selected] == ["a", "b"]
    assert ("a", "b") in pairs or ("b", "a") in pairs


def test_narrow_fills_from_ranked_list_without_overlap():
    ranked = [
        _cand("x0", "web", text="alpha bravo charlie delta"),
        _cand("x1", "web", text="echo foxtrot golf hotel"),
        _cand("x2", "web", text="india juliet kilo lima"),
        _cand("x3", "web", text="mike november oscar papa"),
    ]
    selected, pairs = narrow_with_chunk_overlap(ranked, narrow_limit=3)
    assert len(selected) == 3
    assert pairs == []


def test_empty_text_zero_overlap():
    assert overlap("", "something") == 0.0
    assert overlap("something", "") == 0.0
    assert overlap("", "") == 0.0


def test_ordering_deterministic_across_runs():
    adapters, _ = _adapters(
        decision=[_cand("d1", "decision", score=0.5), _cand("d2", "decision", score=0.5)],
        web=[_cand("w1", "web", score=0.5)],
    )
    first = [c["candidate_id"] for c in retrieve("q", adapters)["candidates"]]
    second = [c["candidate_id"] for c in retrieve("q", adapters)["candidates"]]
    assert first == second


def test_each_adapter_called_once():
    adapters, calls = _adapters(
        decision=[_cand("d1", "decision")],
        memory=[_cand("m1", "memory")],
        repo=[],
        web=[],
    )
    retrieve("q", adapters)
    assert calls == {"decision": 1, "memory": 1, "repo": 1, "web": 1}


def test_local_score_preserved_on_candidates():
    adapters, _ = _adapters(memory=[_cand("m1", "memory", score=0.77)])
    result = retrieve("q", adapters)
    assert result["candidates"][0]["local_score"] == 0.77


def test_invalid_source_name_raises():
    adapters, _ = _adapters(memory=[_cand("m1", "bogus")])
    try:
        retrieve("q", adapters)
    except ValueError as exc:
        assert "bogus" in str(exc)
    else:
        raise AssertionError("expected ValueError for invalid source")


def test_authority_weights_follow_verdict_order():
    assert AUTHORITY_WEIGHTS["decision"] > AUTHORITY_WEIGHTS["memory"]
    assert AUTHORITY_WEIGHTS["memory"] > AUTHORITY_WEIGHTS["repo"]
    assert AUTHORITY_WEIGHTS["repo"] > AUTHORITY_WEIGHTS["web"]


def test_regression_source_functions_untouched():
    import inspect
    import importlib

    root = Path(__file__).parent.parent
    for name, subdir, func, params in (
        ("mem_server_249", "mcp-memory-server", "search_memory", ["query", "namespace"]),
        ("dec_server_249", "mcp-decision-server", "query_manager_decisions", ["query", "category"]),
    ):
        sys.path.insert(0, str(root / subdir))
        try:
            spec = importlib.util.spec_from_file_location(name, root / subdir / "server.py")
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
        finally:
            sys.path.remove(str(root / subdir))
        assert list(inspect.signature(getattr(module, func)).parameters) == params
