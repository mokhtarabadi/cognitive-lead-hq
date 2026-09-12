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
import json
from datetime import datetime, timezone
from pathlib import Path
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


def record(report: dict[str, Any], sessions_root=None) -> Path:
    """Append one replay-report row as JSONL; returns the file path.

    Row: {ts, prompt_hash, passed, total}. Creates parent dirs.
    sessions_root override exists for tests (default: the standard
    brain-sessions dir under ~/.config/opencode).
    """
    base = (
        Path(sessions_root)
        if sessions_root is not None
        else Path.home() / ".config" / "opencode" / "brain-sessions"
    )
    base.mkdir(parents=True, exist_ok=True)
    path = base / "golden_runs.jsonl"
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "prompt_hash": report.get("prompt_hash"),
        "passed": report.get("passed"),
        "total": report.get("passed", 0) + report.get("failed", 0),
    }
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
    return path
