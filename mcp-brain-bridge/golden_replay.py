"""Golden-task replay harness (Task 197, Brain N5).

Offline-safe: the harness never calls a model itself. The caller injects
``ask_fn`` (a stub in unit tests; the bridge ``brain_turn`` in production
when the model endpoint is healthy). Scoring is deterministic:
whitespace-normalized exact match of the model answer against the golden
answer. Reports carry the sha256 of the prompt text so regressions are
attributed to the exact prompt version (goldens live with the caller,
so approved behavior changes cannot silently rot a fixture file).
"""

from __future__ import annotations

import hashlib
from typing import Any, Callable


def _normalize(text: str) -> str:
    """Collapse all whitespace runs to single spaces for comparison."""
    return " ".join(str(text).split())


def prompt_hash(prompt_text: str) -> str:
    """sha256 hex of the prompt text — the regression attribution key."""
    return hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()


def replay(
    ask_fn: Callable[[str], str],
    cases: list[dict[str, str]],
    prompt_text: str,
) -> dict[str, Any]:
    """Replay golden cases through ``ask_fn`` and score them.

    Each case: ``{\"name\": ..., \"ask\": ..., \"expect\": ...}``.
    Returns ``{\"prompt_hash\": ..., \"passed\": n, \"failed\": m,
    \"results\": [{\"name\", \"ok\", \"expected\", \"got\"}]}``.
    An empty corpus scores 0/0 (nothing to regress).
    """
    digest = prompt_hash(prompt_text)
    results: list[dict[str, Any]] = []
    for case in cases:
        got = ask_fn(case["ask"])
        ok = _normalize(got) == _normalize(case["expect"])
        results.append(
            {"name": case["name"], "ok": ok,
             "expected": case["expect"], "got": got}
        )
    passed = sum(1 for r in results if r["ok"])
    return {
        "prompt_hash": digest,
        "passed": passed,
        "failed": len(results) - passed,
        "results": results,
    }
