"""Autopilot loop-spin guard (diff-hash based).

Stops the Hands autopilot fix loop when the produced worktree diff hash
repeats identically: same hash 3x in a row means the loop is spinning
(fix changes nothing) and must stop + escalate with the hash history
instead of burning more turns. A fresh hash resets the counter and the
loop continues.

State lives next to the per-task chat transcripts:
``<sessions>/<task_id>/loop_hashes.jsonl`` (one ``{"ts", "hash"}`` per
fix attempt). Pure local logic — no network, no model calls.
"""

import json
import os
import re
import time
from pathlib import Path
from typing import Any, Optional

# Mirror of the bridge task_id allowlist: never let a task id escape
# the sessions root (../, /, empty all rejected).
_TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")

#: Identical consecutive hashes that mean "spinning, stop".
_SPIN_COUNT = 3


def _sessions_root(explicit: Optional[str] = None) -> Path:
    base = explicit or os.environ.get(
        "BRAIN_SESSIONS_ROOT",
        str(Path.home() / ".config" / "opencode" / "brain-sessions"),
    )
    return Path(base)


def _hashes_path(task_id: str, sessions_root: Optional[str] = None) -> Path:
    if not _TASK_ID_RE.match(task_id or ""):
        raise ValueError(f"bad task_id for loop guard: {task_id!r}")
    return _sessions_root(sessions_root) / task_id / "loop_hashes.jsonl"


def _read_hashes(path: Path) -> list[str]:
    """Last hashes on disk; corrupt lines are skipped, never fatal."""
    if not path.is_file():
        return []
    out: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        digest = entry.get("hash") if isinstance(entry, dict) else None
        if isinstance(digest, str) and digest:
            out.append(digest)
    return out


def record_attempt(
    task_id: str, diff_hash: str, sessions_root: Optional[str] = None
) -> dict[str, Any]:
    """Record one fix-attempt hash; report whether the loop is spinning.

    The hash is stripped and stored stripped. Comparison is exact and
    case-sensitive (hashes such as base64 are case-sensitive, so no
    lowercasing is applied).

    Returns ``{"stop": bool, "history": [last hashes]}``. ``stop`` is
    True only when the last three recorded hashes are identical and
    non-empty — anything else (fresh hash, short history) continues.
    Lines with a missing/non-string/blank hash are skipped on read,
    so corrupt entries can never fake a stop.

    Raises:
        ValueError: task_id illegal, or diff_hash not a non-empty
            string after stripping.
    """
    if not isinstance(diff_hash, str) or not diff_hash.strip():
        raise ValueError(f"bad diff_hash for loop guard: {diff_hash!r}")
    clean = diff_hash.strip()
    path = _hashes_path(task_id, sessions_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": time.time(), "hash": clean}) + "\n")
    history = _read_hashes(path)
    tail = history[-_SPIN_COUNT:]
    stop = len(tail) == _SPIN_COUNT and len(set(tail)) == 1
    return {"stop": stop, "history": tail}
