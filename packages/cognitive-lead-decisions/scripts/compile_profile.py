#!/usr/bin/env python3
"""Aggregate stored decisions into manager-profile drafts (Task 168).

Reads every ``DEC-*.json`` under ``decisions/`` (repo root = this script's
grandparent, or ``DECISION_REPO_PATH``), groups them by category, and prints
a profile-draft section to stdout. The draft is a PROPOSAL: a human must
review and approve it (via the MCP ``propose_profile_evolution`` tool) before
anything lands in ``samples/manager_profile.md``. This script never writes to
the sample itself — the review gate is structural, not conventional.

Usage:
    python scripts/compile_profile.py [--repo PATH] [--since YYYY-MM-DD]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(os.environ.get("DECISION_REPO_PATH", Path(__file__).resolve().parent.parent))


def load_decisions(repo: Path, since: str | None = None) -> list[dict]:
    """Load all decision records, optionally filtered by record date."""
    records = []
    for path in sorted((repo / "decisions").rglob("DEC-*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"warning: skipping unreadable {path}: {exc}", file=sys.stderr)
            continue
        if since and record.get("decision_id", "")[4:12] < since.replace("-", ""):
            continue
        records.append(record)
    return records


def compile_draft(records: list[dict]) -> str:
    """Render a review-ready profile draft from decision records."""
    categories = Counter(
        r.get("extracted_decision", {}).get("category", "other") for r in records
    )
    lines = [
        f"## Profile draft — {datetime.now(timezone.utc).date().isoformat()}",
        f"({len(records)} decisions aggregated; HUMAN REVIEW REQUIRED before merge)",
        "",
        "### Category distribution",
        "",
    ]
    for category, count in categories.most_common():
        lines.append(f"- {category}: {count}")
    lines += ["", "### Recurring rationales", ""]
    seen: set[str] = set()
    for record in records:
        rationale = record.get("extracted_decision", {}).get("rationale", "").strip()
        quote = record.get("verbatim_quote", {}).get("english_translation", "").strip()
        key = (rationale or quote)[:160]
        if key and key not in seen:
            seen.add(key)
            lines.append(f"- [{record.get('decision_id')}] {key}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    """CLI entry: parse args, print draft to stdout, exit 0 (never mutates)."""
    parser = argparse.ArgumentParser(description="Draft a manager-profile update.")
    parser.add_argument("--repo", default=str(REPO_ROOT))
    parser.add_argument("--since", default=None, help="Only decisions on/after YYYY-MM-DD")
    args = parser.parse_args(argv)
    records = load_decisions(Path(args.repo), args.since)
    if not records:
        print("No decisions found — nothing to draft.")
        return 0
    print(compile_draft(records))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
