#!/usr/bin/env python3
"""Validate decision records against the JSON schema (Task 168).

 dependency-free structural validator (the schema uses only `required`,
`type`, `enum`, `pattern`, `minLength`, `format: date-time`): walks
``decisions/`` and reports per-file violations. Exits non-zero when any
record is invalid so CI and the MCP `record_manager_decision` tool can gate
on it.

Usage:
    python scripts/validate_decisions.py [--repo PATH] [--strict]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(os.environ.get("DECISION_REPO_PATH", Path(__file__).resolve().parent.parent))
SCHEMA_NAME = "decision.schema.json"

CATEGORIES = {
    "architecture", "process", "scope", "quality-gate", "tooling", "release", "other",
}
ID_RE = re.compile(r"^DEC-[0-9]{8}-[0-9]{3}$")


def _is_datetime(value: object) -> bool:
    """Best-effort ISO-8601 check (accepts trailing Z)."""
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def validate_record(record: dict) -> list[str]:
    """Return a list of violation strings; empty means valid."""
    issues: list[str] = []
    for field in ("decision_id", "timestamp", "project_name", "verbatim_quote",
                  "extracted_decision", "redaction_verified"):
        if field not in record:
            issues.append(f"missing required field: {field}")
    if issues:
        return issues  # Structural checks below assume presence.
    if not isinstance(record["decision_id"], str) or not ID_RE.match(record["decision_id"]):
        issues.append(f"bad decision_id: {record['decision_id']!r} (want DEC-YYYYMMDD-NNN)")
    if not _is_datetime(record["timestamp"]):
        issues.append(f"bad timestamp: {record['timestamp']!r} (want ISO-8601)")
    if not isinstance(record["project_name"], str) or not record["project_name"].strip():
        issues.append("project_name must be a non-empty string")
    quote = record["verbatim_quote"]
    if not isinstance(quote, dict):
        issues.append("verbatim_quote must be an object")
    else:
        for sub in ("original", "english_translation"):
            if not isinstance(quote.get(sub), str) or not quote[sub].strip():
                issues.append(f"verbatim_quote.{sub} must be a non-empty string")
    decision = record["extracted_decision"]
    if not isinstance(decision, dict):
        issues.append("extracted_decision must be an object")
    else:
        for sub in ("summary", "category", "rationale"):
            if sub not in decision:
                issues.append(f"extracted_decision missing: {sub}")
        if decision.get("category") not in CATEGORIES:
            issues.append(f"bad category: {decision.get('category')!r}")
        if "summary" in decision and (
            not isinstance(decision["summary"], str) or not decision["summary"].strip()
        ):
            issues.append("extracted_decision.summary must be a non-empty string")
    if record["redaction_verified"] is not True:
        issues.append("redaction_verified must be true (run sanitize_text first)")
    return issues


def main(argv: list[str] | None = None) -> int:
    """CLI entry: validate all records; print violations; exit code."""
    parser = argparse.ArgumentParser(description="Validate decision records.")
    parser.add_argument("--repo", default=str(REPO_ROOT))
    parser.add_argument("--strict", action="store_true",
                        help="Also fail when decisions/ holds no records.")
    args = parser.parse_args(argv)
    paths = sorted((Path(args.repo) / "decisions").rglob("DEC-*.json"))
    if not paths:
        print("No decision records found.")
        return 1 if args.strict else 0
    failures = 0
    for path in paths:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"FAIL {path}: unreadable ({exc})")
            failures += 1
            continue
        problems = validate_record(record) if isinstance(record, dict) else ["top-level JSON must be an object"]
        if problems:
            failures += 1
            for problem in problems:
                print(f"FAIL {path}: {problem}")
        else:
            print(f"OK {path}")
    print(f"{len(paths) - failures}/{len(paths)} valid")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
