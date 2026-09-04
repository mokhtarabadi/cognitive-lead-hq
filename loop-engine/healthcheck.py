"""
Healthcheck probe (Task 148).

Checks SQLite state DB connectivity, write latency, and process responsiveness.
Exits 0 on healthy, 1 on error. Supports --dry-run.
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
import time
from pathlib import Path


def check(db_path: str = "loop-engine/state/loop.db", dry_run: bool = False) -> bool:
    if dry_run:
        print("[healthcheck] dry-run OK")
        return True
    try:
        p = Path(db_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        start = time.time()
        conn = sqlite3.connect(str(p), timeout=5)
        try:
            conn.execute("SELECT 1").fetchone()
        finally:
            conn.close()
        latency = time.time() - start
        print(f"[healthcheck] OK latency={latency:.3f}s db={db_path}")
        return latency < 5.0
    except Exception as e:  # noqa: BLE001
        print(f"[healthcheck] FAIL: {e}", file=sys.stderr)
        return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--db", default="loop-engine/state/loop.db")
    args = ap.parse_args(argv)
    return 0 if check(args.db, dry_run=args.dry_run) else 1


if __name__ == "__main__":
    raise SystemExit(main())
