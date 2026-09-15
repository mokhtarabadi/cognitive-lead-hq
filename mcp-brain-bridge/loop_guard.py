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
import sys
import time
from pathlib import Path
from typing import Any, Optional

# Mirror of the bridge task_id allowlist: never let a task id escape
# the sessions root (../, /, empty all rejected).
_TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")

#: Identical consecutive hashes that mean "spinning, stop".
_SPIN_COUNT = 3


#: Project layout marker: a project root holds a ``tasks/`` dir; its Brain
#: sessions live under ``<root>/tasks/.sessions/`` (gitignored) instead of
#: one global folder shared by every project.
_PROJECT_TASKS_DIR = "tasks"
_SESSIONS_DIR = ".sessions"

#: How far up from cwd to look for a project root (bounds the walk).
_WALK_UP_LIMIT = 5


def _legacy_sessions_root() -> Path:
    """Pre-per-project global sessions dir (read fallback only)."""
    return Path.home() / ".config" / "opencode" / "brain-sessions"


def legacy_sessions_root() -> Path:
    """Public alias for the legacy global root (server read-fallback)."""
    return _legacy_sessions_root()


def _has_tasks_dir(candidate: Path) -> bool:
    """True when ``candidate`` looks like a project root (has ``tasks/``)."""
    try:
        return (candidate / _PROJECT_TASKS_DIR).is_dir()
    except OSError:
        return False


def project_sessions_root(
    explicit: Optional[str] = None,
    project_root: Optional[str] = None,
) -> Path:
    """Resolve the sessions root for one project (never raises).

    Order: explicit ``BRAIN_SESSIONS_ROOT`` (or ``explicit`` arg) wins so
    tests keep control; then a ``project_root`` holding ``tasks/``
    (param, then ``BRAIN_PROJECT_ROOT``, then ``BRAIN_WORKSPACE_ROOT``
    env); then a walk up from cwd (max 5 levels) for a dir holding
    ``tasks/``; finally the legacy global root. New writes always land
    under ``<project>/tasks/.sessions/``; callers add legacy read
    fallback so old projects keep working.
    """
    override = explicit or os.environ.get("BRAIN_SESSIONS_ROOT", "").strip()
    if override:
        return Path(override).expanduser()
    candidates: list[Path] = []
    if project_root:
        candidates.append(Path(project_root).expanduser())
    for env_key in ("BRAIN_PROJECT_ROOT", "BRAIN_WORKSPACE_ROOT"):
        env_val = os.environ.get(env_key, "").strip()
        if env_val:
            candidates.append(Path(env_val).expanduser())
    for cand in candidates:
        try:
            resolved = cand.resolve()
        except OSError:
            continue
        if _has_tasks_dir(resolved):
            return resolved / _PROJECT_TASKS_DIR / _SESSIONS_DIR
    try:
        cwd = Path.cwd().resolve()
    except OSError:
        cwd = None
    if cwd is not None:
        node: Optional[Path] = cwd
        for _ in range(_WALK_UP_LIMIT + 1):
            if node is None:
                break
            if _has_tasks_dir(node):
                return node / _PROJECT_TASKS_DIR / _SESSIONS_DIR
            node = node.parent if node.parent != node else None
    return _legacy_sessions_root()


def _sessions_root(explicit: Optional[str] = None) -> Path:
    if explicit:
        return Path(explicit)
    if os.environ.get("BRAIN_SESSIONS_ROOT", "").strip():
        return Path(os.environ["BRAIN_SESSIONS_ROOT"].strip()).expanduser()
    return project_sessions_root()


def _hashes_path(task_id: str, sessions_root: Optional[str] = None,
                 project_root: Optional[str] = None) -> Path:
    if not _TASK_ID_RE.match(task_id or ""):
        raise ValueError(f"bad task_id for loop guard: {task_id!r}")
    if project_root and not sessions_root:
        root = project_sessions_root(project_root=project_root)
    else:
        root = _sessions_root(sessions_root)
    return root / task_id / "loop_hashes.jsonl"


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
    task_id: str, diff_hash: str, sessions_root: Optional[str] = None,
    project_root: Optional[str] = None,
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
    path = _hashes_path(task_id, sessions_root, project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": time.time(), "hash": clean}) + "\n")
    history = _read_hashes(path)
    if not history:
        # Legacy read fallback: old hashes written before per-project
        # scoping keep counting until the new path has its own history.
        legacy = _legacy_sessions_root() / task_id / "loop_hashes.jsonl"
        if legacy != path:
            legacy_history = _read_hashes(legacy)
            if legacy_history:
                print(
                    "loop-guard: using legacy global hashes for "
                    f"{task_id} (unmigrated)",
                    file=sys.stderr,
                )
                history = legacy_history
    tail = history[-_SPIN_COUNT:]
    stop = len(tail) == _SPIN_COUNT and len(set(tail)) == 1
    return {"stop": stop, "history": tail}
