#!/usr/bin/env python3
"""Docs-sync gate: permission denies vs docs table, plus orphan-script scan.

Check 1 (strict, exit non-zero on drift): the repo and global
opencode.json `permission.bash` deny sets must match, and every denied
verb must appear in the Denied commands table in
docs/opencode-shell-strategy.md.

Check 2 (warn-only): every executable script under scripts/ should be
referenced from live docs or configs. Orphans print as ORPHAN lines but
never fail the gate — deletion needs Manager approval.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GLOBAL = Path.home() / ".config" / "opencode"
SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules",
             ".pytest_cache", "archive", "tasks", "context-reports"}
SKIP_NAMES = {"index.md"}  # generated memory index mirrors references
TEXT_SUFFIXES = {".md", ".json", ".py", ".toml", ".txt", ".js"}


def _deny_set(path: Path) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return set(data.get("permission", {}).get("bash", {}))


def _check_denies() -> list[str]:
    errors: list[str] = []
    repo = _deny_set(ROOT / "opencode.json")
    global_cfg = GLOBAL / "opencode.json"
    if global_cfg.is_file():
        glob = _deny_set(global_cfg)
        if repo != glob:
            errors.append(
                f"deny sets differ: repo-only={sorted(repo - glob)} "
                f"global-only={sorted(glob - repo)}")
    table = (ROOT / "docs" / "opencode-shell-strategy.md").read_text(
        encoding="utf-8")
    verbs = {d.split()[1] for d in repo}  # "git <verb>[ *]"
    for verb in sorted(verbs):
        if f"`git {verb}`" not in table:
            errors.append(f"docs table missing `git {verb}`")
    return errors


def _live_text_files() -> list[Path]:
    out: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        if path.name in SKIP_NAMES:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        out.append(path)
    return out


def _check_orphans() -> list[str]:
    orphans: list[str] = []
    candidates = [p for p in (ROOT / "scripts").rglob("*")
                  if p.is_file() and "__pycache__" not in p.parts]
    haystacks = {p: p.read_text(encoding="utf-8", errors="replace")
                 for p in _live_text_files()}
    for script in candidates:
        name = script.name
        stem = script.stem
        hit = any(
            (name in text or (stem and stem in text))
            for p, text in haystacks.items() if p != script)
        if not hit:
            orphans.append(str(script.relative_to(ROOT)))
    return orphans


def main() -> int:
    errors = _check_denies()
    for orphan in _check_orphans():
        print(f"ORPHAN (warn-only): {orphan}")
    for err in errors:
        print(f"DRIFT: {err}")
    print("docs-sync: " + ("FAIL" if errors else "OK"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
