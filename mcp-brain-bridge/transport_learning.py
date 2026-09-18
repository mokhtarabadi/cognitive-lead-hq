"""Transport-failure learning for mcp-brain-bridge (GitHub issue 17).

A provider rejection caused by OUR malformed request must not fail
twice identically: classify the failure, record the missing-field
shape, retry once with the corrected body, and — scoped to the saga
(task key) — escalate on repeat instead of looping. Escalations raise
``TransportEscalationError`` (never a verdict-shaped REPORT); genuinely
non-correctable failures propagate untouched.

Stdlib-only, mirroring ``loop_guard``: importable without the MCP
runtime so unit tests stay offline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Optional, Union

try:
    from mcp_brain_bridge.session_ledger import (  # type: ignore[import-not-found]
        append_event as _ledger_append,
    )
except ImportError:
    try:
        from session_ledger import (  # type: ignore[import-not-found]
            append_event as _ledger_append,
        )
    except ImportError:
        _ledger_append = None  # type: ignore[assignment]

#: The one failure class the bridge knows how to correct: the provider
#: rejected a named request field (strict-provider 400
#: ``unsupported_parameter``). Every other class passes through.
CORRECTABLE_CLASS = "unsupported_parameter"

#: Body keys a correction must never drop: without them the request has
#: no meaning, so a rejection naming one is not correctable.
PROTECTED_KEYS = frozenset({"model", "input"})

#: Machine-readable escalation marker. NEVER a verdict string: tests
#: assert QA_/VERDICT_/XML_ tokens never appear in escalation errors.
ESCALATION_MARKER = "transport-learning-escalation"

_STATUS_RE = re.compile(r"\berror (\d{3})\b")
_UNSUPPORTED_PARAM_RE = re.compile(
    r"unsupported parameter:\s*'([^']+)'", re.IGNORECASE)


class TransportEscalationError(RuntimeError):
    """Same failure class twice in one saga: stop retrying, surface up."""


@dataclass(frozen=True)
class Correction:
    """One applicable request fix: drop the rejected top-level key."""

    param: str
    action: str = "drop"
    failure_class: str = CORRECTABLE_CLASS

    @property
    def fingerprint(self) -> str:
        return f"{self.failure_class}:{self.action}:{self.param}"

    def apply(self, body: Mapping[str, Any]) -> dict:
        fixed = dict(body)
        fixed.pop(self.param, None)
        return fixed


def classify_transport_error(
    exc: BaseException, body: Mapping[str, Any]
) -> Optional[Correction]:
    """Return the applicable correction, or None when not correctable."""
    msg = str(exc)
    status = _STATUS_RE.search(msg)
    if not status or int(status.group(1)) != 400:
        return None
    param = _UNSUPPORTED_PARAM_RE.search(msg)
    if not param:
        return None
    name = param.group(1)
    if name in PROTECTED_KEYS:
        return None
    if not isinstance(body, Mapping) or name not in body:
        return None
    return Correction(param=name)


def failure_signature(exc: BaseException) -> Optional[str]:
    """Return the ``class:param`` signature of a correctable-class
    failure, or None. Unlike ``classify_transport_error`` this does not
    need the key to still sit in the body — it identifies a REPEAT of
    an already-applied correction (provider echoing the same rejection
    after the key was dropped)."""
    msg = str(exc)
    status = _STATUS_RE.search(msg)
    if not status or int(status.group(1)) != 400:
        return None
    param = _UNSUPPORTED_PARAM_RE.search(msg)
    if not param:
        return None
    return f"{CORRECTABLE_CLASS}:{param.group(1)}"


def escalation_message(
    task_key: Optional[str], fingerprint: str, repeats: int
) -> str:
    return (
        f"[{ESCALATION_MARKER}] task={task_key or 'one-off'} "
        f"class={fingerprint} repeats={repeats}: identical request "
        "rejected twice — not retrying. Fix the request shape or the "
        "provider contract, then start a new turn."
    )


@dataclass
class CorrectionMemory:
    """Saga-scoped correction state: in-memory set plus ledger events."""

    task_key: Optional[str] = None
    seen_fingerprints: Iterable[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        self._seen: set = set(self.seen_fingerprints)
        self._corrected: set = set()
        for fp in self._seen:
            parts = fp.split(":")
            if len(parts) == 3:
                self._corrected.add(f"{parts[0]}:{parts[2]}")
            else:
                self._corrected.add(fp)

    def seen(self, fingerprint: str) -> bool:
        return fingerprint in self._seen

    def already_corrected(self, signature: str) -> bool:
        """True when this class:param already had a correction applied
        (the retry did not stick) — the saga must escalate."""
        return signature in self._corrected

    def record(
        self,
        correction: Correction,
        task_id: Optional[str] = None,
        session_id: Optional[str] = None,
        project_root: Optional[Union[str, object]] = None,
        sessions_dir: Optional[Union[str, object]] = None,
    ) -> dict:
        self._seen.add(correction.fingerprint)
        self._corrected.add(
            f"{correction.failure_class}:{correction.param}")
        record: dict = {
            "event": "transport_correction",
            "task_key": self.task_key,
            "class": correction.failure_class,
            "param": correction.param,
            "action": correction.action,
            "persisted": False,
        }
        if (_ledger_append is not None
                and (project_root is not None or sessions_dir is not None)):
            stored = _ledger_append(
                "transport_correction",
                task_id=task_id,
                session_id=session_id,
                data={"task_key": self.task_key,
                      "class": correction.failure_class,
                      "param": correction.param,
                      "action": correction.action,
                      "fingerprint": correction.fingerprint},
                project_root=project_root,  # type: ignore[arg-type]
                sessions_dir=sessions_dir,  # type: ignore[arg-type]
            )
            record["persisted"] = True
            record["stored"] = stored
        return record
