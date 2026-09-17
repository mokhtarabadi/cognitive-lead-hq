"""Offline eval harness over structured execution traces.

Pure: traces in, report rows out. No MCP calls, no filesystem, no
network. Missing cost/latency stays ``None`` and is excluded from
aggregates, never coerced to zero.
"""

_ZAC_HEADS = (("git", "add"), ("git", "commit"), ("git", "push"))


def _normalize_op_name(value):
    return str(value or "").lower().replace(".", " ").replace("_", " ").replace("-", " ")


def _op_is_zac(operation):
    """A structured operation is a ZAC violation when it issues a direct
    ``git add`` / ``git commit`` / ``git push`` command or operation name."""
    if not isinstance(operation, dict):
        return False
    fields = []
    for key in ("command", "name"):
        raw = operation.get(key)
        if isinstance(raw, str) and raw.strip():
            fields.append(_normalize_op_name(raw).split())
    for tokens in fields:
        for head in _ZAC_HEADS:
            if len(tokens) >= 2 and tuple(tokens[:2]) == head:
                return True
    return False


def scan_zac(operations):
    """Count forbidden direct-Git operations; returns ``(count, clean)``."""
    count = sum(1 for op in (operations or []) if _op_is_zac(op))
    return count, count == 0


def _qa_repairs_or_none(value):
    # Unknown counts must never masquerade as verified zero: a missing,
    # null, non-integer, boolean, or negative value means "unobserved",
    # while an explicit non-negative integer (including 0) is observed.
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value >= 0:
        return value
    return None


def score_case(trace, expected):
    """Score one structured trace against caller-owned expectations."""
    trace = trace or {}
    expected = expected or {}
    actual_cites = list(trace.get("citations") or [])
    expected_cites = list(expected.get("citations") or [])
    expected_set = set(expected_cites)
    citation_hits = sum(1 for c in expected_set if c in set(actual_cites))

    actual_ground = trace.get("grounding") or {}
    ground_hits, ground_total = 0, 0
    for claim in expected.get("grounding") or []:
        if not isinstance(claim, dict):
            continue
        ground_total += 1
        need = set(claim.get("supported_by") or [])
        have = set(actual_ground.get(claim.get("claim_id")) or [])
        if need and need <= have:
            ground_hits += 1

    actual_rules = trace.get("rule_results") or {}
    rules_passed, rules_total = 0, 0
    for rule in expected.get("rules") or []:
        if not isinstance(rule, dict):
            continue
        rules_total += 1
        if actual_rules.get(rule.get("rule_id")) is True:
            rules_passed += 1

    zac_count, zac_clean = scan_zac(trace.get("operations"))
    qa_repairs = _qa_repairs_or_none(trace.get("qa_repairs"))
    return {
        "case_id": trace.get("case_id"),
        "parse_ok": trace.get("parse_ok") is True,
        "citation_hits": citation_hits,
        "citation_expected": len(expected_set),
        "grounding_hits": ground_hits,
        "grounding_expected": ground_total,
        "rules_passed": rules_passed,
        "rules_expected": rules_total,
        "zac_violation_count": zac_count,
        "zac_clean": zac_clean,
        "qa_repair_count": qa_repairs,
        "cost_usd": trace.get("cost_usd"),
        "latency_ms": trace.get("latency_ms"),
    }


def _rate(hits, total):
    if total <= 0:
        return None
    return hits / total


def _mean(values):
    nums = [v for v in values if isinstance(v, (int, float))]
    if not nums:
        return None
    return sum(nums) / len(nums)


def aggregate_report(rows):
    """Aggregate per-case rows into the report columns plus ``rows``."""
    rows = list(rows or [])
    cite_hits = sum(r["citation_hits"] for r in rows)
    cite_total = sum(r["citation_expected"] for r in rows)
    ground_hits = sum(r["grounding_hits"] for r in rows)
    ground_total = sum(r["grounding_expected"] for r in rows)
    rules_hit = sum(r["rules_passed"] for r in rows)
    rules_total = sum(r["rules_expected"] for r in rows)
    costs = [r["cost_usd"] for r in rows if isinstance(r["cost_usd"], (int, float))]
    latencies = [r["latency_ms"] for r in rows if isinstance(r["latency_ms"], (int, float))]
    zac_total = sum(r["zac_violation_count"] for r in rows)
    qa_observed = [r["qa_repair_count"] for r in rows if isinstance(r["qa_repair_count"], int)]
    return {
        "case_count": len(rows),
        "parse_rate": _rate(sum(1 for r in rows if r["parse_ok"]), len(rows)) if rows else None,
        "citation_rate": _rate(cite_hits, cite_total),
        "grounding_rate": _rate(ground_hits, ground_total),
        "rule_pass_rate": _rate(rules_hit, rules_total),
        "zac_violation_count": zac_total,
        "zac_clean_case_rate": _rate(sum(1 for r in rows if r["zac_clean"]), len(rows)) if rows else None,
        "qa_repair_count_total": sum(qa_observed) if qa_observed else None,
        "qa_repair_count_mean": (sum(qa_observed) / len(qa_observed)) if qa_observed else None,
        "qa_repair_observed_case_count": len(qa_observed),
        "cost_total_usd": sum(costs) if costs else None,
        "cost_mean_usd": _mean(costs),
        "cost_observed_case_count": len(costs),
        "latency_mean_ms": _mean(latencies),
        "latency_observed_case_count": len(latencies),
        "rows": rows,
    }
