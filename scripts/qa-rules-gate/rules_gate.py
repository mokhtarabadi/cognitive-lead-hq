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

import os
import re
from dataclasses import dataclass, field
from typing import Callable

_VERDICT_RE = re.compile(
    r"^[ \t]*VERDICT:[ \t]*(QA_PASSED|QA_REJECTED)[ \t]*$", re.MULTILINE
)
_CITE_RE = re.compile(r"^[ \t]*CITE:[ \t]*(\S+):(\d+)[.,;:!?]*[ \t]*$", re.MULTILINE)
_VALID_JUDGE_VERDICTS = ("QA_PASSED", "QA_REJECTED")
_CITE_TRAILING_PUNCT = ".,;:!?"


class UnparseableVerdict(ValueError):
    """Raised when a QA reply carries no machine-readable VERDICT line."""


@dataclass(frozen=True)
class GateResult:
    verdict: str
    violations: list = field(default_factory=list)
    judge_called: bool = False


def parse_verdict(reply: str) -> tuple[str, list[tuple[str, int]]]:
    """Parse a QA reply into (verdict, [(file, line), ...]) with one regex each.

    Fail-closed: exactly ONE VERDICT line must be present — zero or
    multiple lines raise. Leading spaces/tabs are tolerated; CRLF is
    covered by the trailing blank match. Trailing punctuation on a cite
    path (e.g. ``foo.py:12.``) is stripped, never accepted.

    Raises:
        UnparseableVerdict: if there is not exactly one VERDICT line.
    """
    matches = _VERDICT_RE.findall(reply)
    if len(matches) != 1:
        raise UnparseableVerdict(
            f"Expected exactly one VERDICT line, found {len(matches)} "
            "(expected 'VERDICT: QA_PASSED' or 'VERDICT: QA_REJECTED')."
        )
    cites = [
        (path.rstrip(_CITE_TRAILING_PUNCT), int(line))
        for path, line in _CITE_RE.findall(reply)
    ]
    return matches[0], cites


def _lookup_dotted(record: dict, dotted: str) -> bool:
    """True when a dotted path (``a.b.c``) resolves through nested dicts."""
    current: object = record
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    return True


def check_schema(record: dict, required: list[str]) -> list[str]:
    """Missing required fields → one violation string each.

    Entries may use dotted paths (``verdict.payload``) to require nested
    keys, not just top-level ones.
    """
    return [
        f"missing field: {name}" for name in required if not _lookup_dotted(record, name)
    ]


def check_budget(used: int, limit: int) -> list[str]:
    """Token/char budget overflow → a single violation string."""
    if used > limit:
        return [f"budget exceeded: used {used} > limit {limit}"]
    return []


def check_allowlist(paths: list[str], roots: list[str]) -> list[str]:
    """Paths escaping every allowed root → one violation string each.

    Both sides are normalized with ``realpath`` (resolves ``..`` AND
    symlinks — ``abspath`` alone leaves symlink escapes open) and
    containment is enforced with ``commonpath``, so sibling-prefix
    paths (``/allow-evil`` vs root ``/allow``) never match.
    Relative payload paths (the production shape) are resolved against
    the process CWD before comparison.
    """
    norm_roots = [os.path.realpath(root) for root in roots]
    violations = []
    for path in paths:
        norm_path = os.path.realpath(path)
        try:
            inside = any(
                norm_path == norm_root
                or os.path.commonpath([norm_path, norm_root]) == norm_root
                for norm_root in norm_roots
            )
        except ValueError:
            inside = False  # e.g. different drives — fail closed
        if not inside:
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
        judge_verdict = judge()
        if judge_verdict not in _VALID_JUDGE_VERDICTS:
            return GateResult(
                verdict="QA_REJECTED",
                violations=[f"invalid judge verdict: {judge_verdict!r}"],
                judge_called=True,
            )
        return GateResult(
            verdict=judge_verdict, violations=[], judge_called=True
        )
    return GateResult(verdict=verdict, violations=[])
