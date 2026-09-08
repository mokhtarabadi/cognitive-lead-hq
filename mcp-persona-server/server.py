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
from pathlib import Path
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from dual_dispatch import extract_xml, is_clarification_question
from session import append_turn, build_persona_messages, summarize_session
from telegram import send_admin_question, send_approval_request

# Repo root resolved from this file's location so path handling works no
# matter which cwd the stdio server is launched from.
REPO_ROOT = Path(__file__).resolve().parent.parent

mcp = FastMCP("PersonaServer")


def _get_persona_model() -> str:
    """LLM model for persona turns; override via ``PERSONA_MODEL``."""
    return os.environ.get("PERSONA_MODEL", "openrouter/google/gemini-3.8-flash").strip() or (
        "openrouter/google/gemini-3.8-flash"
    )


def _get_reasoning_effort() -> str:
    """Reasoning effort for persona turns; override via ``PERSONA_REASONING_EFFORT``."""
    return (
        os.environ.get("PERSONA_REASONING_EFFORT", "high").strip() or "high"
    )


def _get_temperature() -> float:
    """Sampling temperature; override via ``PERSONA_TEMPERATURE`` (default 0.2)."""
    try:
        return float(os.environ.get("PERSONA_TEMPERATURE", "0.2") or 0.2)
    except ValueError:
        return 0.2


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

    Read-only: turn counts by role, session time span, and the latest
    assistant excerpt. Delegates to ``session.summarize_session``.
    """
    return summarize_session(task_id)


@mcp.tool()
def escalate_to_admin(
    task_id: int, question: str, options: Optional[list[str]] = None
) -> dict[str, str]:
    """Ask the human manager an open question via Telegram and await reply.

    Delegates to ``telegram.send_admin_question``. Always returns a dict —
    transport failures arrive as ``"ERROR: ..."`` answer strings, never as
    raised exceptions, so the executor loop stays alive.
    """
    answer = send_admin_question(task_id, question, options or [])
    return {"task_id": str(task_id), "answer": answer}


@mcp.tool()
def request_admin_approval(
    task_id: int, stage: str, summary: str, task_file_path: str = ""
) -> dict[str, Any]:
    """Open a Telegram Approve/Reject gate for ``stage`` and await the decision.

    Delegates to ``telegram.send_approval_request``. The manager's decision
    (``approve``/``reject``) is the hard gate: callers MUST NOT auto-continue
    on any other outcome.
    """
    result = send_approval_request(task_id, stage, summary, task_file_path)
    return {"task_id": int(task_id), "stage": stage, **result}


if __name__ == "__main__":
    mcp.run(transport="stdio")
