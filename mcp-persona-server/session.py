"""Append-only session transcripts for persona dispatch turns (Task 167).

Each persona conversation lives under::

    tasks/.sessions/{task_id}/transcript.jsonl

One JSON object per line (``{"role", "content", "name", "timestamp"}``),
which is both human-inspectable and directly reusable as LiteLLM message
history (``role``/``content``). The file is append-only: turns are never
rewritten, so the transcript doubles as the audit trail for manager
approval gates.

Progressive lineage projection (``build_persona_messages``) assembles the
full LLM context for a turn: global system prompt, repo rules, persona
brief, cumulative task conversation, and the new instruction — newest,
most specific context last so the model weights it highest.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Overridable for tests: point at a tmp dir to avoid touching the real repo.
SESSIONS_ROOT = Path(os.environ.get("PERSONA_SESSIONS_DIR", "tasks/.sessions"))

# Files projected into every persona turn (repo-root relative). Missing files
# are skipped silently so sessions degrade gracefully on partial checkouts.
LINEAGE_FILES = ("system-prompt.md", "AGENTS.md")


def _utc_now() -> str:
    """Current UTC time as an ISO-8601 string (used for turn timestamps)."""
    return datetime.now(timezone.utc).isoformat()


def session_dir(task_id: int) -> Path:
    """Return (creating on demand) the session directory for ``task_id``.

    Args:
        task_id: Numeric task identifier; coerced to int so ``"167"`` and
            ``167`` resolve to the same directory.

    Raises:
        ValueError: If ``task_id`` is not integer-coercible.
    """
    try:
        tid = int(task_id)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"task_id must be an integer, got {task_id!r}") from exc
    path = SESSIONS_ROOT / str(tid)
    path.mkdir(parents=True, exist_ok=True)
    return path


def transcript_path(task_id: int) -> Path:
    """Full path of the JSONL transcript file for ``task_id``."""
    return session_dir(task_id) / "transcript.jsonl"


def append_turn(
    task_id: int,
    role: str,
    content: str,
    name: Optional[str] = None,
) -> dict[str, Any]:
    """Append one turn to the session transcript (append-only).

    Args:
        task_id: Owning task id.
        role: LiteLLM message role (``system``/``user``/``assistant``).
        content: Turn text.
        name: Optional participant label (e.g. persona name).

    Returns:
        The stored record dict (including its timestamp).
    """
    record: dict[str, Any] = {
        "role": role,
        "content": content,
        "name": name,
        "timestamp": _utc_now(),
    }
    with open(transcript_path(task_id), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def read_transcript(task_id: int) -> list[dict[str, Any]]:
    """Read all turns for ``task_id`` in order; empty list when none exist.

    Corrupt lines are skipped (never crash a live session on a bad line);
    a missing transcript simply means "no history yet".
    """
    path = session_dir(task_id) / "transcript.jsonl"
    if not path.is_file():
        return []
    turns: list[dict[str, Any]] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue  # Skip corrupt lines; keep the session usable.
            if isinstance(record, dict) and "content" in record:
                turns.append(record)
    return turns


def _read_repo_file(relative: str) -> Optional[str]:
    """Read a repo-root-relative file; None when missing/unreadable."""
    try:
        return Path(relative).read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None


def build_persona_messages(
    task_id: int,
    persona_name: str,
    instruction: str,
    task_file_path: Optional[str] = None,
    repo_root: Optional[Path] = None,
) -> list[dict[str, str]]:
    """Assemble the LiteLLM message list for one persona turn.

    Progressive lineage projection, broadest context first:

    1. ``system`` — global ``system-prompt.md`` + ``AGENTS.md`` (survives
       every turn; the persona always reasons under repo rules).
    2. ``system`` — persona brief (``prompts/fragments/06-personas.md`` when
       present, else a minimal fallback naming the persona).
    3. ``user`` — full task file body when ``task_file_path`` is given
       (cumulative task conversation / acceptance criteria).
    4. Prior transcript turns replayed verbatim (cumulative memory).
    5. ``user`` — the new instruction (most specific, last), SKIPPED when
       the replay already ends with it (dedupe: each instruction is sent
       to LiteLLM exactly once).

    Args:
        task_id: Owning task id (for transcript replay).
        persona_name: e.g. ``"QA Engineer"``, ``"Code Reviewer"``.
        instruction: The new user-side instruction for this turn.
        task_file_path: Optional task file to inject as task context.
        repo_root: Directory lineage files resolve against (defaults to the
            current working directory, i.e. the repo root under stdio).

    Returns:
        LiteLLM-compatible message list (``role``/``content`` dicts only —
        ``name``/``timestamp`` are transcript metadata, not LLM fields).
    """
    root = Path(repo_root) if repo_root is not None else Path.cwd()

    # 1. Global lineage: system prompt + repo rules.
    system_parts = []
    for relative in LINEAGE_FILES:
        body = _read_repo_file(str(root / relative))
        if body:
            system_parts.append(f"# {relative}\n\n{body}")
    system_text = (
        "You are a persona of the Cognitive Lead AI multi-persona review pipeline.\n"
        "Reason strictly under the repository rules below.\n\n" + "\n\n".join(system_parts)
        if system_parts
        else "You are a persona of the Cognitive Lead AI multi-persona review pipeline."
    )
    messages: list[dict[str, str]] = [{"role": "system", "content": system_text}]

    # 2. Persona brief.
    personas_body = _read_repo_file(str(root / "prompts" / "fragments" / "06-personas.md"))
    if personas_body:
        messages.append(
            {
                "role": "system",
                "content": f"You are acting as persona: {persona_name}.\n\n{personas_body}",
            }
        )
    else:
        messages.append(
            {"role": "system", "content": f"You are acting as persona: {persona_name}."}
        )

    # 3. Cumulative task context.
    if task_file_path:
        task_body = _read_repo_file(task_file_path)
        if task_body:
            messages.append(
                {
                    "role": "user",
                    "content": f"Task file `{task_file_path}` (full context):\n\n{task_body}",
                }
            )

    # 4. Replay prior turns (LiteLLM fields only).
    replayed: list[dict[str, str]] = []
    for turn in read_transcript(task_id):
        role = turn.get("role", "user")
        if role not in ("system", "user", "assistant"):
            role = "user"
        replayed.append({"role": role, "content": str(turn.get("content", ""))})
    messages.extend(replayed)

    # 5. The new instruction goes last (highest recency weight) — unless the
    # transcript replay already ends with it. The server appends each
    # instruction to the transcript BEFORE building messages, so without this
    # guard LiteLLM would receive every user instruction exactly twice.
    if not (
        replayed
        and replayed[-1]["role"] == "user"
        and replayed[-1]["content"] == instruction
    ):
        messages.append({"role": "user", "content": instruction})
    return messages


def summarize_session(task_id: int) -> dict[str, Any]:
    """Return a high-level milestone ledger for ``task_id``.

    Counts turns by role, reports the time span, and surfaces the latest
    assistant output as the current milestone. Pure read path — never mutates
    the transcript.
    """
    turns = read_transcript(task_id)
    by_role: dict[str, int] = {}
    for turn in turns:
        by_role[turn.get("role", "unknown")] = by_role.get(turn.get("role", "unknown"), 0) + 1
    last_assistant: Optional[str] = None
    for turn in reversed(turns):
        if turn.get("role") == "assistant":
            last_assistant = str(turn.get("content", ""))[:2000]
            break
    timestamps = [t.get("timestamp") for t in turns if t.get("timestamp")]
    return {
        "task_id": int(task_id),
        "turn_count": len(turns),
        "turns_by_role": by_role,
        "first_turn_at": timestamps[0] if timestamps else None,
        "last_turn_at": timestamps[-1] if timestamps else None,
        "latest_assistant_excerpt": last_assistant,
    }
