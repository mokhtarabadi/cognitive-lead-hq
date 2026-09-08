#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mcp[cli]>=1.0,<2.0",
#     "litellm",
# ]
# ///

"""Persona dispatch MCP server (Task 167).

Replaces the retired ``loop-engine/`` daemon with on-demand persona turns:
the cognitive-executor calls ``dispatch_session_turn`` with a persona name
(``QA Engineer``, ``Code Reviewer``, ...) plus the instruction, and a light
LLM — holding the full system prompt, repo rules, and cumulative task
history (progressive lineage projection) — responds. Raw model output is
classified by the Dual Dispatch pattern:

- XML control block present  -> ``status="XML_EXTRACTED"`` (+ verbatim block)
- No XML but asks questions  -> ``status="QUESTION"`` (relay to the asker)
- Otherwise                  -> ``status="REPORT"`` (free-form evaluation)

Manager hard gates (Telegram inline Approve/Reject, open questions) are
exposed as ``request_admin_approval`` / ``escalate_to_admin``.

Transport: stdio FastMCP, mirroring mcp-context-server / mcp-memory-server.
``litellm`` is imported lazily inside the dispatch path so module import
(and unit tests) never need network access or provider credentials.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from dual_dispatch import extract_xml, is_clarification_question
from session import append_turn, build_persona_messages, summarize_session
from telegram import send_admin_question, send_approval_request

# Repo root resolved from this file's location so path handling works no
# matter which cwd the stdio server is launched from.
REPO_ROOT = Path(__file__).resolve().parent.parent


# Shared env loader lives in mcp-common (Task 170). Prefer the installed
# package; fall back to the sibling source tree so plain `uv run <path>`
# and direct test imports keep working without a workspace install.
try:
    from mcp_common.env import load_env_files as _shared_load_env_files
except ImportError:  # pragma: no cover - workspace/normal path first
    # Sibling source tree: <install-root>/mcp-common/src, where install-root
    # is the repo root (repo installs) or ~/.config/opencode (global installs).
    _COMMON_SRC = Path(__file__).resolve().parent.parent / "mcp-common" / "src"
    # NOTE: file.parent = server dir, so parent.parent = install root. Correct.
    if _COMMON_SRC.is_dir():
        sys.path.insert(0, str(_COMMON_SRC))
    from mcp_common.env import load_env_files as _shared_load_env_files


def _load_env_files(server_dir: Optional[Path] = None) -> Optional[str]:
    """Load `.env` files via the shared loader (kept as a thin wrapper so
    callers/tests keep one stable entry point). Empty env values count as
    unset, so blank `{env:…}` injections never shadow file values."""
    return _shared_load_env_files(
        server_dir if server_dir is not None else Path(__file__).resolve().parent
    )


_loaded_from = _load_env_files()
if _loaded_from is not None:
    print(f"persona-server: loaded env from {_loaded_from}", file=sys.stderr)

mcp = FastMCP("PersonaServer")


def _get_persona_model() -> str:
    """LLM model for persona turns; override via ``PERSONA_MODEL``."""
    return os.environ.get("PERSONA_MODEL", "openrouter/deepseek/deepseek-v4-flash-0731").strip() or (
        "openrouter/deepseek/deepseek-v4-flash-0731"
    )


def _get_reasoning_effort() -> str:
    """Reasoning effort for persona turns; override via ``PERSONA_REASONING_EFFORT``."""
    return (
        os.environ.get("PERSONA_REASONING_EFFORT", "high").strip() or "high"
    )


def _get_temperature() -> float:
    """Sampling temperature; override via ``PERSONA_TEMPERATURE`` (default 1.0).

    Gemini 3 family guidance: keep the 1.0 default; low values risk looping
    and degraded reasoning on complex tasks. Tune reasoning effort instead.
    """
    try:
        return float(os.environ.get("PERSONA_TEMPERATURE", "1.0") or 1.0)
    except ValueError:
        return 1.0


def _get_max_tokens() -> int:
    """Max completion tokens; override via ``PERSONA_MAX_TOKENS`` (default 16384)."""
    try:
        return int(os.environ.get("PERSONA_MAX_TOKENS", "16384") or 16384)
    except ValueError:
        return 16384


def _call_llm(model: str, messages: list[dict[str, str]]) -> str:
    """One LiteLLM completion; returns the assistant text (never None).

    The import is lazy so importing this server module stays side-effect
    free. ``drop_params=True`` keeps providers that reject ``reasoning_effort``
    from failing the whole turn.
    """
    import litellm  # Lazy: no network/credentials needed at import time.

    response = litellm.completion(
        model=model,
        messages=messages,
        temperature=_get_temperature(),
        max_tokens=_get_max_tokens(),
        reasoning_effort=_get_reasoning_effort(),
        drop_params=True,
    )
    return str(response.choices[0].message.content or "")


def _read_task_file(task_file_path: Optional[str]) -> Optional[str]:
    """Read the task file body for lineage injection; None when absent."""
    if not task_file_path:
        return None
    candidate = Path(task_file_path)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / task_file_path
    try:
        return candidate.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None


@mcp.tool()
def dispatch_session_turn(
    task_id: int,
    persona_name: str,
    instruction: str,
    task_file_path: Optional[str] = None,
    force_xml: bool = False,
) -> dict[str, Any]:
    """Run one persona turn and classify the raw model output.

    WHEN TO CALL (automatic): after finishing an implementation call this
    with persona "QA Engineer"; before any approval gate call it with
    "Code Reviewer"; when a task is ambiguous or cross-disciplinary call it
    with "Brainstorm Facilitator" (load the brainstorm-swarm skill first);
    when stuck waiting on missing context, let the QUESTION lane guide you.
    Do NOT call this for plain file reads or deterministic checks — use
    direct tools instead.

    1. Reads ``system-prompt.md`` + the full task file body from disk
       (progressive lineage projection via ``session.build_persona_messages``).
    2. Appends the instruction turn to ``tasks/.sessions/{task_id}/``.
    3. Calls LiteLLM (``PERSONA_MODEL``, ``PERSONA_REASONING_EFFORT``).
    4. Dual Dispatch: XML present -> ``XML_EXTRACTED``; question -> ``QUESTION``;
       otherwise -> ``REPORT``. With ``force_xml=True`` and no XML block, the
       caller gets ``RETRY_NEEDED`` (re-dispatch with a stronger instruction)
       instead of a silently unstructured answer.

    Args:
        task_id: Owning task id (session scope + audit trail).
        persona_name: e.g. ``"QA Engineer"``, ``"Code Reviewer"``.
        instruction: User-side instruction for this turn.
        task_file_path: Optional repo-relative task file for context.
        force_xml: Require a structured XML block in the reply.

    Returns:
        Dict with ``status``, ``persona_name``, ``task_id``, plus either
        ``xml_content`` (XML_EXTRACTED), ``question`` (QUESTION),
        ``report`` (REPORT), or ``hint`` (RETRY_NEEDED).
    """
    task_body = _read_task_file(task_file_path)
    if task_body is not None:
        append_turn(task_id, "user", f"Task file `{task_file_path}` injected.\n\n{task_body}")
    append_turn(task_id, "user", instruction, name="executor")

    # Transcript replay already carries the injected task body + instruction,
    # so build messages without re-injecting the file (avoids triple context).
    messages = build_persona_messages(
        task_id, persona_name, instruction, None, repo_root=REPO_ROOT
    )
    output = _call_llm(_get_persona_model(), messages)
    append_turn(task_id, "assistant", output, name=persona_name)

    has_xml, xml_content, clean_text = extract_xml(output)
    if has_xml:
        return {
            "status": "XML_EXTRACTED",
            "task_id": int(task_id),
            "persona_name": persona_name,
            "xml_content": xml_content,
            "remainder": clean_text,
        }
    if force_xml:
        return {
            "status": "RETRY_NEEDED",
            "task_id": int(task_id),
            "persona_name": persona_name,
            "hint": (
                "No XML control block found but force_xml=True. Re-dispatch with an "
                "instruction that explicitly demands a <hands_*_task> block. Raw output: "
                + output[:2000]
            ),
        }
    if is_clarification_question(output):
        return {
            "status": "QUESTION",
            "task_id": int(task_id),
            "persona_name": persona_name,
            "question": clean_text or output.strip(),
        }
    return {
        "status": "REPORT",
        "task_id": int(task_id),
        "persona_name": persona_name,
        "report": output.strip(),
    }


@mcp.tool()
def get_session_summary(task_id: int) -> dict[str, Any]:
    """Return the high-level milestone ledger for ``task_id``.

    WHEN TO CALL (automatic): when resuming a task you did not start, before
    opening an approval gate (cite the ledger in the gate summary), or when
    asked where a session stands. Read-only and cheap — prefer it over
    re-reading full transcripts.

    Read-only: turn counts by role, session time span, and the latest
    assistant excerpt. Delegates to ``session.summarize_session``.
    """
    return summarize_session(task_id)


@mcp.tool()
def escalate_to_admin(
    task_id: int, question: str, options: Optional[list[str]] = None
) -> dict[str, str]:
    """Ask the human manager an open question via Telegram and await reply.

    WHEN TO CALL (automatic): only when genuinely blocked on missing context
    that no persona turn, memory shard, or past decision can supply. Every
    call pages a human — prefer `dispatch_session_turn` (QUESTION lane),
    `query_manager_decisions`, and memory search first.

    Delegates to ``telegram.send_admin_question``. Always returns a dict —
    transport failures arrive as ``"ERROR: ..."`` answer strings, never as
    raised exceptions, so the executor loop stays alive.
    """
    answer = send_admin_question(task_id, question, options or [])
    return {"task_id": str(task_id), "answer": answer}


@mcp.tool()
def request_admin_approval(
    task_id: int, stage: str, summary: str, task_file_path: str = "", ask_note: bool = True
) -> dict[str, Any]:
    """Open a Telegram Approve/Reject gate for ``stage`` and await the decision.

    WHEN TO CALL (automatic): this is the MANDATORY hard gate — call it after
    QA + reviewer loops pass and before ANY closure/commit, and again at any
    stage whose summary the manager must sign off. Never skip it, never
    auto-continue on timeout/reject/transport failure.

    Delegates to ``telegram.send_approval_request``. The manager's decision
    (``approve``/``reject``) is the hard gate: callers MUST NOT auto-continue
    on any other outcome. With ``ask_note`` (default) the manager gets one
    follow-up prompt for an optional note (reject reasons, conditions) that
    arrives as ``note`` (None on silence/``/skip``) — record it in the task
    reasoning, especially on ``reject``.
    """
    result = send_approval_request(task_id, stage, summary, task_file_path, None, ask_note)
    return {"task_id": int(task_id), "stage": stage, **result}


if __name__ == "__main__":
    mcp.run(transport="stdio")
