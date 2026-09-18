"""Request preflight validator for the Brain bridge (GitHub issue 18).

Local, transport-free validation of every ``brain_turn`` call: an
explicit ``project_root`` must hold a ``tasks/`` dir (raise, never
silently fall back to the workspace root); memory-bearing turns bind to
exactly one of ``task_id`` / ``session_id``; ``stage``, the boolean
flags, the Kanban path, and ``required_tools`` are shape-checked.

Stdlib only — unit tests import this module without the MCP stack.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional

#: Stages the Hands may declare for a turn. Unknown stages are rejected
#: so a typo (``qa_``) can never silently run as an unscoped turn.
ALLOWED_STAGES = ("plan", "implement", "qa", "review", "closure")

#: Bare task numbers only (digits), mirroring
#: ``server._TASK_NUMBER_RE`` — suffixed variants fork history.
_BARE_TASK_RE = re.compile(r"^\d+$")

#: Taskless saga sessions: same charset as the transcript sanitizer
#: (``server._TASK_ID_RE``), so a validated session id always resolves
#: to a safe transcript path.
_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")


class PreflightError(ValueError):
    """A ``brain_turn`` request is malformed. Raised locally, before any
    history load, file attach, or transport — a malformed request never
    consumes a model call and never surfaces as a Brain verdict."""


def require_bare_task_id(task_id: object) -> str:
    """Fail-closed gate for the ``brain_turn`` task_id input.

    Returns the stripped bare number. Raises PreflightError for anything
    else (slugs, suffixed variants, empty, non-strings) BEFORE any
    history load, file attach, or model call — a wrong id must never
    silently start a second, empty history next to the real one.
    """
    if isinstance(task_id, str) and _BARE_TASK_RE.fullmatch(task_id.strip()):
        return task_id.strip()
    raise PreflightError(
        f"bad task_id: {task_id!r} — must be the bare task number "
        "(digits only, e.g. '215'). Pass the identical number on every "
        "turn of one task (plan, implement, QA, review) so history "
        "continues; suffixes like '215qa'/'215rev' split history into "
        "separate transcripts and are rejected."
    )


def require_session_id(session_id: object) -> str:
    """Fail-closed gate for taskless saga turns. Returns the stripped
    id; raises PreflightError on traversal, separators, or overlong
    input — the id becomes a transcript path segment."""
    if isinstance(session_id, str) and _SESSION_ID_RE.fullmatch(
            session_id.strip()):
        return session_id.strip()
    raise PreflightError(
        f"bad session_id: {session_id!r} — must match "
        "[A-Za-z0-9][A-Za-z0-9_-]{0,63} (e.g. 'cando-828'). It keys the "
        "saga transcript the same way task_id keys a task transcript."
    )


def _has_tasks_dir(root: Path) -> bool:
    try:
        return (root / "tasks").is_dir()
    except OSError:
        return False


def resolve_project_root(
    explicit: object = None,
    *,
    env: Optional[Mapping[str, str]] = None,
    cwd: Optional[Path] = None,
) -> Path:
    """Resolve the project root holding ``tasks/``.

    Chain: explicit ``project_root`` → ``BRAIN_PROJECT_ROOT`` →
    ``BRAIN_WORKSPACE_ROOT`` → cwd walk-up. An EXPLICIT root is strict:
    missing, non-directory, or without ``tasks/`` raises PreflightError
    (never silently substitutes the workspace root — that substitution
    caused the Cando-828 saga to fail turns as "unavailable"). Ambient
    sources (env, walk-up) are tolerant: an env root without ``tasks/``
    falls through to the next link. Exhaustion raises PreflightError
    naming ``project_root`` as the remedy.
    """
    if explicit is not None:
        if not isinstance(explicit, (str, Path)):
            raise PreflightError(
                f"bad project_root: {explicit!r} — must be a path string "
                "to a directory holding a tasks/ dir."
            )
        root = Path(explicit).expanduser()
        if not root.is_dir():
            raise PreflightError(
                f"bad project_root: {explicit!r} — not a directory. Pass "
                "the project dir holding tasks/ (e.g. "
                "project_root='/path/to/proj')."
            )
        if not _has_tasks_dir(root):
            raise PreflightError(
                f"bad project_root: {explicit!r} — no tasks/ dir inside. "
                "Pass the project dir holding tasks/; the bridge never "
                "substitutes another root silently."
            )
        return root.resolve()
    environ = os.environ if env is None else env
    for key in ("BRAIN_PROJECT_ROOT", "BRAIN_WORKSPACE_ROOT"):
        cand = (environ.get(key) or "").strip()
        if cand and _has_tasks_dir(Path(cand).expanduser()):
            return Path(cand).expanduser().resolve()
    start = Path.cwd() if cwd is None else Path(cwd)
    for candidate in (start, *start.parents):
        if _has_tasks_dir(candidate):
            return candidate.resolve()
    raise PreflightError(
        "no project root: no tasks/ dir found via BRAIN_PROJECT_ROOT / "
        "BRAIN_WORKSPACE_ROOT / cwd walk-up. Pass "
        "project_root='<dir holding tasks/>' explicitly."
    )


def _check_stage(stage: object) -> Optional[str]:
    if stage is None:
        return None
    if isinstance(stage, str) and stage in ALLOWED_STAGES:
        return stage
    raise PreflightError(
        f"bad stage: {stage!r} — must be one of {list(ALLOWED_STAGES)} "
        "or omitted."
    )


def _check_flags(include_bundle: object, include_diff: object) -> None:
    for name, value in (("include_bundle", include_bundle),
                        ("include_diff", include_diff)):
        if not isinstance(value, bool):
            raise PreflightError(
                f"bad {name}: {value!r} — must be a bool, not "
                f"{type(value).__name__}."
            )


def _resolve_kanban_path(kanban_path: object, *, root: Path) -> Optional[Path]:
    if kanban_path is None:
        return None
    if not isinstance(kanban_path, (str, Path)):
        raise PreflightError(
            f"bad kanban_path: {kanban_path!r} — must be a path string "
            "under <project_root>/tasks/."
        )
    raw = str(kanban_path)
    base = (root / "tasks").resolve()
    candidate = (Path(raw).expanduser()
                 if Path(raw).is_absolute() else (root / raw))
    try:
        resolved = candidate.resolve()
    except OSError as exc:
        raise PreflightError(
            f"bad kanban_path: {raw!r} — unresolvable ({exc}).") from exc
    if resolved != base and base not in resolved.parents:
        raise PreflightError(
            f"bad kanban_path: {raw!r} — escapes <project_root>/tasks/. "
            "The task file must live under the project tasks/ lanes."
        )
    if resolved.suffix != ".md":
        raise PreflightError(
            f"bad kanban_path: {raw!r} — must point at a task .md file.")
    return resolved


def _check_required_tools(required_tools: object) -> tuple:
    if required_tools is None:
        return ()
    if isinstance(required_tools, str) or not isinstance(
            required_tools, (list, tuple)):
        raise PreflightError(
            f"bad required_tools: {required_tools!r} — must be a list of "
            "tool-name strings, e.g. ['question']."
        )
    for tool in required_tools:
        if not isinstance(tool, str) or not tool.strip():
            raise PreflightError(
                f"bad required_tools entry: {tool!r} — every entry must "
                "be a non-empty tool-name string."
            )
    return tuple(t.strip() for t in required_tools)


@dataclass(frozen=True)
class ValidatedRequest:
    """A ``brain_turn`` request that passed local preflight."""
    project_root: Optional[Path]
    binding: str  # "task" | "session" | "one-off"
    task_id: Optional[str] = None
    session_id: Optional[str] = None
    stage: Optional[str] = None
    kanban_path: Optional[Path] = None
    include_bundle: bool = True
    include_diff: bool = False
    required_tools: tuple = field(default_factory=tuple)

    @property
    def history_key(self) -> Optional[str]:
        """Transcript key: task turns continue the task history, saga
        turns continue the session history, one-offs persist nothing."""
        return self.task_id if self.task_id is not None else self.session_id


def validate_request(
    *,
    project_root: object = None,
    task_id: object = None,
    session_id: object = None,
    kanban_path: object = None,
    stage: object = None,
    include_bundle: object = True,
    include_diff: object = False,
    required_tools: object = None,
    env: Optional[Mapping[str, str]] = None,
    cwd: Optional[Path] = None,
) -> ValidatedRequest:
    """Validate a ``brain_turn`` request before any load, attach, or
    transport. Raises PreflightError on the first malformed field."""
    if task_id is not None and session_id is not None:
        raise PreflightError(
            f"bad binding: task_id={task_id!r} and "
            f"session_id={session_id!r} are mutually exclusive — pass "
            "exactly one so history continues under a single key."
        )
    clean_task = (require_bare_task_id(task_id)
                  if task_id is not None else None)
    clean_session = (require_session_id(session_id)
                     if session_id is not None else None)
    binding = ("task" if clean_task is not None
               else "session" if clean_session is not None else "one-off")
    _check_flags(include_bundle, include_diff)
    clean_stage = _check_stage(stage)
    clean_tools = _check_required_tools(required_tools)
    root: Optional[Path] = None
    if binding != "one-off":
        root = resolve_project_root(project_root, env=env, cwd=cwd)
    clean_kanban: Optional[Path] = None
    if kanban_path is not None:
        if root is None:
            raise PreflightError(
                "bad kanban_path: a task file path needs a project root, "
                "but this one-off turn has none. Bind task_id/session_id "
                "or pass project_root."
            )
        clean_kanban = _resolve_kanban_path(kanban_path, root=root)
    return ValidatedRequest(
        project_root=root, binding=binding, task_id=clean_task,
        session_id=clean_session, stage=clean_stage,
        kanban_path=clean_kanban, include_bundle=bool(include_bundle),
        include_diff=bool(include_diff), required_tools=clean_tools)
