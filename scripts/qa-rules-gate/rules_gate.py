"""Rules-first QA gate (Task 195).

Cheap deterministic checks — verdict parse, schema, budget, allowlist — run
BEFORE any LLM judge call. If any rule fails, the gate returns QA_REJECTED
without ever invoking the judge (saves judge tokens, fails in milliseconds).

Machine verdict format (emitted by the QA persona, fragment 06-personas.md):

    VERDICT: QA_PASSED
    CITE: path/to/file.py:123

Parsed with a single regex each; an unparseable reply raises
UnparseableVerdict — the autopilot treats that as QA_REJECTED with reason
"unparseable verdict" and falls back to the prose report (escape hatch).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

_VERDICT_RE = re.compile(r"^VERDICT:\s*(QA_PASSED|QA_REJECTED)\s*$", re.MULTILINE)
_CITE_RE = re.compile(r"^CITE:\s*(\S+):(\d+)\s*$", re.MULTILINE)


class UnparseableVerdict(ValueError):
    """Raised when a QA reply carries no machine-readable VERDICT line."""


@dataclass(frozen=True)
class GateResult:
    verdict: str
    violations: list = field(default_factory=list)
    judge_called: bool = False


def parse_verdict(reply: str) -> tuple[str, list[tuple[str, int]]]:
    """Parse a QA reply into (verdict, [(file, line), ...]) with one regex each.

    Raises:
        UnparseableVerdict: if no VERDICT line is present.
    """
    match = _VERDICT_RE.search(reply)
    if not match:
        raise UnparseableVerdict(
            "No machine-readable VERDICT line (expected "
            "'VERDICT: QA_PASSED' or 'VERDICT: QA_REJECTED')."
        )
    cites = [(path, int(line)) for path, line in _CITE_RE.findall(reply)]
    return match.group(1), cites


def check_schema(record: dict, required: list[str]) -> list[str]:
    """Missing required fields → one violation string each."""
    return [f"missing field: {name}" for name in required if name not in record]


def check_budget(used: int, limit: int) -> list[str]:
    """Token/char budget overflow → a single violation string."""
    if used > limit:
        return [f"budget exceeded: used {used} > limit {limit}"]
    return []


def check_allowlist(paths: list[str], roots: list[str]) -> list[str]:
    """Paths escaping every allowed root → one violation string each."""
    violations = []
    for path in paths:
        if not any(
            Path(path) == Path(root) or Path(root) in Path(path).parents
            for root in roots
        ):
            violations.append(f"path outside allowlist: {path}")
    return violations


def run_gate(
    payload: dict,
    *,
    required: list[str],
    budget: tuple[int, int],
    allowlist_roots: list[str],
    judge: Callable[[], str] | None = None,
) -> GateResult:
    """Run rules first; call the LLM judge only if every rule passes.

    Args:
        payload: {"verdict_reply": str, "paths": [str], ...extra schema fields}.
        required: required top-level payload keys (schema check).
        budget: (used, limit) token/char budget.
        allowlist_roots: allowed path roots for payload["paths"].
        judge: optional zero-arg LLM-judge callable returning a verdict
            string; NEVER called when any rule fails.

    Returns:
        GateResult with verdict QA_PASSED / QA_REJECTED, the violation list,
        and whether the judge was called.
    """
    violations: list[str] = []
    try:
        verdict, _ = parse_verdict(payload.get("verdict_reply", ""))
    except UnparseableVerdict as exc:
        violations.append(f"unparseable verdict: {exc}")
        verdict = "QA_REJECTED"
    violations += check_schema(payload, required)
    used, limit = budget
    violations += check_budget(used, limit)
    violations += check_allowlist(payload.get("paths", []), allowlist_roots)

    if violations:
        return GateResult(verdict="QA_REJECTED", violations=violations)
    if judge is not None:
        return GateResult(
            verdict=judge(), violations=[], judge_called=True
        )
    return GateResult(verdict=verdict, violations=[])
