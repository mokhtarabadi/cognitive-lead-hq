"""Append-only session ledger (shared infra, GitHub issue 19).

WS2 shipped the minimal shape (``append_event`` → one JSON line per
call under ``<project_root>/tasks/.sessions/session_ledger.jsonl``).
WS4 extends this module with session starts, checkpoints, a tolerant
reader, and pending decision candidates — the filename and the event
envelope stay stable.

Stdlib-only, mirroring ``loop_guard``: importable without the MCP
runtime so unit tests stay offline.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Optional, Union

LEDGER_FILENAME = "session_ledger.jsonl"

# Ordered checkpoint names for one brain_turn saga (GitHub issue 19,
# P5). brain_turn wires checkpoints 1-6; 7-9 are ledger-level names
# for plan/QA/closure verdicts recorded by later stages.
CHECKPOINTS = (
    "request_accepted",
    "preflight_completed",
    "capability_completed",
    "transport_started",
    "transport_correction_or_escalation",
    "response_parsed",
    "plan_or_approval",
    "qa_or_review",
    "closure_requested_or_blocked",
)

LEDGER_FILENAME = "session_ledger.jsonl"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _resolve_dir(
    sessions_dir: Optional[Union[str, Path]] = None,
    project_root: Optional[Union[str, Path]] = None,
) -> Path:
    if sessions_dir is not None:
        ledger_dir = Path(sessions_dir).expanduser()
    elif project_root is not None:
        ledger_dir = Path(project_root).expanduser() / "tasks" / ".sessions"
    else:
        raise ValueError(
            "session ledger: pass sessions_dir or project_root")
    ledger_dir.mkdir(parents=True, exist_ok=True)
    return ledger_dir


def append_event(
    event: str,
    task_id: Optional[str] = None,
    session_id: Optional[str] = None,
    data: Optional[Mapping[str, Any]] = None,
    project_root: Optional[Union[str, Path]] = None,
    sessions_dir: Optional[Union[str, Path]] = None,
) -> dict:
    """Append one event line to the session ledger; return the record."""
    ledger_dir = _resolve_dir(sessions_dir, project_root)
    record: dict = {
        "ts": _utc_now_iso(),
        "task_id": task_id,
        "session_id": session_id,
        "event": event,
    }
    if data:
        record.update(dict(data))
    path = ledger_dir / LEDGER_FILENAME
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def start_session(
    session_id: str,
    task_id: Optional[str] = None,
    phase: Optional[str] = None,
    request_hash: Optional[str] = None,
    capability_manifest: Optional[Mapping[str, Any]] = None,
    project_root: Optional[Union[str, Path]] = None,
    sessions_dir: Optional[Union[str, Path]] = None,
    **extra: Any,
) -> dict:
    """Open one session row carrying every issue-19 ledger field."""
    ledger_dir = _resolve_dir(sessions_dir, project_root)
    record: dict = {
        "ts": _utc_now_iso(),
        "task_id": task_id,
        "session_id": session_id,
        "event": "session_started",
        "phase": phase,
        "checkpoints": [],
        "request_hash": request_hash,
        "response_hash": None,
        "retry_counts": {},
        "capability_manifest": (
            dict(capability_manifest) if capability_manifest else None),
        "approval_events": [],
        "transcript_path": str(
            ledger_dir / session_id / "transcript.jsonl"),
        "transport_corrections": [],
        "final_status": "open",
    }
    record.update(dict(extra))
    with (ledger_dir / LEDGER_FILENAME).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def checkpoint(
    session_id: str,
    name: str,
    task_id: Optional[str] = None,
    detail: Optional[Mapping[str, Any]] = None,
    project_root: Optional[Union[str, Path]] = None,
    sessions_dir: Optional[Union[str, Path]] = None,
) -> dict:
    """Append one ordered checkpoint; unknown names are rejected."""
    if name not in CHECKPOINTS:
        raise ValueError(
            f"session ledger: unknown checkpoint {name!r}; "
            f"expected one of {', '.join(CHECKPOINTS)}")
    data: dict = {"checkpoint": name}
    if detail:
        data.update(dict(detail))
    return append_event(
        "checkpoint", task_id=task_id, session_id=session_id,
        data=data, project_root=project_root, sessions_dir=sessions_dir)


def read_ledger(
    project_root: Optional[Union[str, Path]] = None,
    sessions_dir: Optional[Union[str, Path]] = None,
) -> list:
    """Read every ledger line; corrupt lines are skipped, never fatal."""
    if sessions_dir is not None:
        ledger_dir = Path(sessions_dir).expanduser()
    elif project_root is not None:
        ledger_dir = Path(project_root).expanduser() / "tasks" / ".sessions"
    else:
        raise ValueError(
            "session ledger: pass sessions_dir or project_root")
    path = ledger_dir / LEDGER_FILENAME
    if not path.is_file():
        return []
    records: list = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                parsed = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                continue
            if isinstance(parsed, dict):
                records.append(parsed)
    return records


def record_pending_candidate(
    session_id: str,
    candidate: Mapping[str, Any],
    task_id: Optional[str] = None,
    project_root: Optional[Union[str, Path]] = None,
    sessions_dir: Optional[Union[str, Path]] = None,
) -> dict:
    """Stage one extracted decision candidate as pending — never a write.

    The ledger row is the approval queue (GitHub issue 19, P7); the
    candidate reaches ``record_manager_decision`` only after the
    Manager approves, via an explicit caller handoff.
    """
    data = dict(candidate)
    data["status"] = "pending"
    return append_event(
        "decision_pending", task_id=task_id, session_id=session_id,
        data=data, project_root=project_root, sessions_dir=sessions_dir)


def _pending_for_session(
    session_id: str,
    project_root: Optional[Union[str, Path]] = None,
    sessions_dir: Optional[Union[str, Path]] = None,
) -> list[dict]:
    """Pending decision candidates staged for one session, in order."""
    return [
        e for e in read_ledger(
            project_root=project_root, sessions_dir=sessions_dir)
        if e.get("event") == "decision_pending"
        and e.get("session_id") == session_id
    ]


def resolve_pending_candidate(
    session_id: str,
    index: int,
    verdict: Union[str, bool],
    task_id: Optional[str] = None,
    note: Optional[str] = None,
    project_root: Optional[Union[str, Path]] = None,
    sessions_dir: Optional[Union[str, Path]] = None,
) -> dict:
    """Record the Manager's verdict on one pending candidate (auditable).

    ``index`` selects the session's Nth staged candidate; ``verdict`` is
    ``\"approved\"`` / ``\"rejected\"`` (a bool also works: True approves).
    Approval returns the candidate payload merged with the verdict so
    the caller can hand it to ``record_manager_decision`` explicitly —
    this function itself never writes DEC files.
    """
    pending = _pending_for_session(
        session_id, project_root=project_root, sessions_dir=sessions_dir)
    try:
        chosen = pending[index]
    except IndexError:
        raise ValueError(
            f"no pending candidate #{index} for session {session_id!r} "
            f"({len(pending)} staged)"
        ) from None
    if isinstance(verdict, str):
        decision = verdict.strip().lower()
        if decision not in ("approved", "rejected"):
            raise ValueError(
                f"bad verdict {verdict!r}; use 'approved' or 'rejected'"
            )
    else:
        decision = "approved" if verdict else "rejected"
    # The pending row stores candidate fields at the record top level
    # (append_event merges data in); carry them over minus the envelope
    # and the stale pending status.
    data = {
        key: value for key, value in chosen.items()
        if key not in ("ts", "task_id", "session_id", "event", "status")
    }
    data["decision"] = decision
    if note:
        data["note"] = note
    return append_event(
        "decision_approved" if decision == "approved"
        else "decision_rejected",
        task_id=task_id, session_id=session_id, data=data,
        project_root=project_root, sessions_dir=sessions_dir)


def promote_pending_candidate(
    session_id: str,
    index: int,
    task_id: Optional[str] = None,
    note: Optional[str] = None,
    project_root: Optional[Union[str, Path]] = None,
    sessions_dir: Optional[Union[str, Path]] = None,
) -> dict:
    """Approve one pending candidate; caller persists it explicitly."""
    return resolve_pending_candidate(
        session_id, index, "approved", task_id=task_id, note=note,
        project_root=project_root, sessions_dir=sessions_dir)
