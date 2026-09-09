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
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Overridable for tests: point at a tmp dir to avoid touching the real repo.
SESSIONS_ROOT = Path(os.environ.get("PERSONA_SESSIONS_DIR", "tasks/.sessions"))

# Files projected into every persona turn (repo-root relative). Missing files
# are skipped silently so sessions degrade gracefully on partial checkouts.
LINEAGE_FILES = ("system-prompt.md", "AGENTS.md")

# Persona brief location (repo-root relative).
PERSONA_BRIEF_REL = Path("prompts") / "fragments" / "06-personas.md"

# Transcript replay bound: only the newest N turns are re-sent to LiteLLM so
# long-lived tasks cannot grow requests without bound. Override via
# ``PERSONA_MAX_REPLAY_TURNS``. Older turns stay in the JSONL audit trail.
DEFAULT_MAX_REPLAY_TURNS = 50


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


def _lineage_search_roots(repo_root: Path) -> list[Path]:
    """Ordered roots a lineage file is resolved against.

    1. ``repo_root`` — the checkout the turn runs against (normal path).
    2. The process working directory (MCP stdio servers may be launched
       from the project root rather than the install root).
    3. The global OpenCode config dir (``~/.config/opencode``) — fallback
       for global installs serving projects without vendored lineage files.

    Duplicates are removed, order preserved.
    """
    candidates = [repo_root, Path.cwd(), Path.home() / ".config" / "opencode"]
    roots: list[Path] = []
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if resolved not in roots:
            roots.append(resolved)
    return roots


def _read_lineage_file(
    name: str, repo_root: Path
) -> tuple[Optional[str], Optional[str], bool]:
    """Read lineage file ``name`` from the first root that holds it.

    Returns ``(body, source_path, found)``. ``found`` distinguishes "file
    exists but is empty" (no warning — nothing to project, nothing missing)
    from "absent in every root" (caller SHOULD warn: a persona running
    without its system prompt or repo rules is reasoning blind).
    """
    for root in _lineage_search_roots(repo_root):
        try:
            body = (root / name).read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        return (body if body.strip() else "", str(root / name), True)
    return None, None, False


def _warn_missing_lineage(missing: list[str]) -> None:
    """Stderr warning naming lineage files no search root provided."""
    if missing:
        print(
            "persona-server WARNING: lineage file(s) not found in any search "
            f"root (repo, cwd, ~/.config/opencode): {', '.join(missing)}. "
            "The persona turn is reasoning WITHOUT them.",
            file=sys.stderr,
        )


def _get_max_replay_turns() -> int:
    """Newest transcript turns re-sent per LiteLLM call (default 50)."""
    try:
        return max(1, int(os.environ.get("PERSONA_MAX_REPLAY_TURNS", "") or DEFAULT_MAX_REPLAY_TURNS))
    except ValueError:
        return DEFAULT_MAX_REPLAY_TURNS


def slugify_persona_name(name: str) -> str:
    """Filesystem-safe slug for a persona name (card filenames)."""
    return re.sub(r"[^a-z0-9]+", "-", str(name).lower()).strip("-") or "persona"


def persona_card_path(task_id: int, persona_name: str) -> Path:
    """JSON identity card for one persona inside one task session.

    The card is what makes a persona EXIST between LiteLLM calls: without
    it every turn rebuilds the persona from scratch (name label only). With
    it the persona carries durable identity — turn count, last outcome,
    open questions — across the whole task.
    """
    return session_dir(task_id) / f"persona_{slugify_persona_name(persona_name)}.json"


def load_persona_card(task_id: int, persona_name: str) -> dict[str, Any]:
    """Load the persona card; defaults for a first-ever turn."""
    path = persona_card_path(task_id, persona_name)
    try:
        stored = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(stored, dict):
            return stored
    except (OSError, UnicodeError, json.JSONDecodeError):
        pass
    now = _utc_now()
    return {
        "persona_name": persona_name,
        "created_at": now,
        "updated_at": now,
        "turn_count": 0,
        "last_status": None,
        "open_question": None,
    }


def save_persona_card(
    task_id: int,
    persona_name: str,
    status: str,
    open_question: Optional[str] = None,
) -> dict[str, Any]:
    """Advance the persona card after one completed turn (creates it first).

    Args:
        task_id: Owning task id.
        persona_name: Persona display name.
        status: Dispatch outcome (``XML_EXTRACTED``/``QUESTION``/``REPORT``/...).
        open_question: Carried forward only on ``QUESTION``; cleared by any
            decisive outcome so stale questions never haunt later turns.

    Returns:
        The stored card dict.
    """
    card = load_persona_card(task_id, persona_name)
    card["turn_count"] = int(card.get("turn_count", 0) or 0) + 1
    card["last_status"] = status
    card["updated_at"] = _utc_now()
    card["open_question"] = open_question if status == "QUESTION" else None
    # Atomic write (tmp + os.replace): concurrent Hands on the same
    # task+persona can still lose an increment, but a torn half-written
    # card (invalid JSON → silent default reset) is impossible.
    path = persona_card_path(task_id, persona_name)
    tmp_path = path.with_name(path.name + ".tmp")
    with open(tmp_path, "w", encoding="utf-8") as fh:
        json.dump(card, fh, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)
    return card


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
       every turn; the persona always reasons under repo rules). Files are
       resolved against ``repo_root``, then cwd, then the global OpenCode
       config dir; a stderr warning names any file missing everywhere.
    2. ``system`` — persona brief (``prompts/fragments/06-personas.md`` when
       present, else a minimal fallback naming the persona).
    2b. ``system`` — persona identity card (durable per-task state: turn
       count, last outcome, open question) so the persona EXISTS between
       LiteLLM calls instead of being rebuilt from a bare name each turn.
    3. ``user`` — full task file body when ``task_file_path`` is given
       (cumulative task conversation / acceptance criteria).
    4. Prior transcript turns replayed verbatim (cumulative memory),
       capped at ``PERSONA_MAX_REPLAY_TURNS`` newest (default 50) so
       long-lived tasks cannot grow requests without bound.
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

    # 1. Global lineage: system prompt + repo rules (fallback chain).
    # NOTE (documented, by design): the global-config root is a READ fallback
    # so installs serving projects without vendored lineage still reason
    # under a system prompt. First root holding the file wins — a repo copy
    # (even empty) always shadows the global one.
    missing: list[str] = []
    system_parts = []
    for relative in LINEAGE_FILES:
        body, _source, found = _read_lineage_file(relative, root)
        if body:
            system_parts.append(f"# {relative}\n\n{body}")
        elif not found:
            missing.append(relative)
    _warn_missing_lineage(missing)
    system_text = (
        "You are a persona of the Cognitive Lead AI multi-persona review pipeline.\n"
        "Reason strictly under the repository rules below.\n\n" + "\n\n".join(system_parts)
        if system_parts
        else "You are a persona of the Cognitive Lead AI multi-persona review pipeline."
    )
    messages: list[dict[str, str]] = [{"role": "system", "content": system_text}]

    # 2. Persona brief (fallback chain; minimal fallback names the persona).
    personas_body, _brief_source, brief_found = _read_lineage_file(str(PERSONA_BRIEF_REL), root)
    if personas_body:
        messages.append(
            {
                "role": "system",
                "content": f"You are acting as persona: {persona_name}.\n\n{personas_body}",
            }
        )
    else:
        if not brief_found:
            _warn_missing_lineage([str(PERSONA_BRIEF_REL)])
        messages.append(
            {"role": "system", "content": f"You are acting as persona: {persona_name}."}
        )

    # 2b. Persona identity card — durable self across LiteLLM calls.
    card = load_persona_card(task_id, persona_name)
    card_lines = [
        f"You are the persistent persona '{card.get('persona_name', persona_name)}' "
        f"on task {task_id} (turn #{int(card.get('turn_count', 0) or 0) + 1}).",
    ]
    if card.get("last_status"):
        card_lines.append(f"Your last turn ended as: {card['last_status']}.")
    if card.get("open_question"):
        card_lines.append(
            "Your still-open question from the previous turn: "
            f"{card['open_question']}"
        )
    card_lines.append(
        "When you lack codebase context for planning, emit a "
        "<hands_context_request> block (see your command brief) instead of "
        "guessing — the executor will gather it and re-dispatch."
        if card.get("last_status") != "CONTEXT_REQUEST"
        else "Codebase evidence was just gathered for your last context "
        "request — proceed with planning on that evidence instead of "
        "requesting again."
    )
    messages.append({"role": "system", "content": " ".join(card_lines)})

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

    # 4. Replay prior turns (LiteLLM fields only), newest-first capped.
    all_turns = read_transcript(task_id)
    max_replay = _get_max_replay_turns()
    omitted = max(0, len(all_turns) - max_replay)
    if omitted:
        messages.append(
            {
                "role": "user",
                "content": (
                    f"[{omitted} oldest transcript turn(s) omitted from this "
                    "prompt by PERSONA_MAX_REPLAY_TURNS; they remain in the "
                    "JSONL audit trail.]"
                ),
            }
        )
    replayed: list[dict[str, str]] = []
    for turn in all_turns[-max_replay:]:
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
