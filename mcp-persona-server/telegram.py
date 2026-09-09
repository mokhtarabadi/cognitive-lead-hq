"""Telegram manager-approval transport for the persona engine (Task 167).

Thin wrapper over the Telegram Bot HTTP API using only the standard library
(``urllib``) — no third-party client dependency. Two flows:

- **Approval gate** (``send_approval_request``): posts a stage summary with an
  inline ``[Approve]`` / ``[Reject]`` keyboard, then long-polls ``getUpdates``
  for the manager's callback query. Oversized summaries fall back to a
  document attachment so the gate never silently truncates context.
- **Open question** (``send_admin_question``): posts a question (optionally
  with an option keyboard) and awaits either a callback press or a plain
  text reply.

Credentials come from the environment (``TELEGRAM_BOT_TOKEN``,
``TELEGRAM_CHAT_ID``); when absent the functions return
``{"sent": False, ...}`` instead of raising, so the MCP server degrades
gracefully on checkouts without a bot configured. Timeouts come from
``TELEGRAM_APPROVAL_TIMEOUT_SECONDS`` (default 1800s).

All network I/O funnels through ``_api()`` so tests can stub the transport
without touching the network.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.parse
import urllib.request
from typing import Any, Callable, Optional

# Telegram caps text messages at 4096 chars; stay safely under it.
MAX_TEXT_LEN = 3500
# Long-poll window per getUpdates call (seconds).
POLL_WINDOW = 25
# Telegram caps callback_data at 64 bytes ("Bad Request: BUTTON_DATA_INVALID"
# beyond that). Stage slugs in keyboards are budgeted well under it.
MAX_CALLBACK_LEN = 64


def _env(name: str, default: str = "") -> str:
    """Read ``name`` from the environment, stripped; ``default`` when unset."""
    return os.environ.get(name, default).strip()


def _api(
    token: str,
    method: str,
    payload: dict[str, Any],
    transport: Optional[Callable[..., dict[str, Any]]] = None,
) -> dict[str, Any]:
    """POST one Bot API call and return the decoded JSON response.

    Args:
        token: Bot token (already validated non-empty by callers).
        method: Bot API method name (``sendMessage``, ``getUpdates``, ...).
        payload: JSON-serializable parameters.
        transport: Test hook — when given, called as
            ``transport(method, payload)`` instead of hitting the network.

    Raises:
        RuntimeError: On transport errors or ``ok: false`` API responses.
    """
    if transport is not None:
        return transport(method, payload)
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=POLL_WINDOW + 10) as response:
            body = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Telegram API call {method} failed: {exc}") from exc
    if not body.get("ok"):
        raise RuntimeError(f"Telegram API call {method} not ok: {body}")
    return body


def slugify_stage(stage: str) -> str:
    """Callback-safe slug for a gate stage name.

    ``callback_data`` is capped at 64 bytes by Telegram, so the full human
    stage text (which stays in the message body) can never ride on the
    buttons. The slug keeps ``approve:{task}:{slug}`` / ``reject:{task}:{slug}``
    far under the cap while remaining human-readable in update logs.

    Short stages pass through unchanged (``"QA"`` -> ``"qa"``). Long or
    degenerate stages get a content hash suffix so two DISTINCT stages can
    never share one slug (truncated siblings and double-``gate`` fallbacks
    would otherwise cross-route approvals between gates of one task).
    """
    base = re.sub(r"[^a-z0-9]+", "-", str(stage).lower()).strip("-")
    digest = hashlib.sha1(str(stage).encode("utf-8")).hexdigest()[:6]
    if not base:
        # Degenerate stage names must not all share one 'gate' slug.
        return f"gate-{digest}"
    if len(base) <= 32:
        return base
    return f"{base[:25]}-{digest}"


def _approval_keyboard(task_id: int, stage: str) -> dict[str, Any]:
    """Inline keyboard with task/stage-scoped Approve / Reject buttons.

    ``callback_data`` embeds ``{task_id}:{stage-slug}`` (e.g.
    ``approve:167:qa``) so concurrent gates on different tasks can never
    cross-accept each other's button presses — the waiter filters on the
    expected suffix. The slug (never the raw stage text) rides the buttons
    so long stage names cannot trip Telegram's 64-byte ``callback_data``
    cap; the full stage text is echoed in the gate message body instead.
    """
    slug = slugify_stage(stage)
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Approve", "callback_data": f"approve:{task_id}:{slug}"},
                {"text": "❌ Reject", "callback_data": f"reject:{task_id}:{slug}"},
            ]
        ]
    }
    # Explicit runtime guard (never bare assert: asserts vanish under
    # ``python -O``, and an oversize payload would hang the gate on a silent
    # Telegram rejection). Measured in encoded BYTES against the 64B cap.
    for row in keyboard["inline_keyboard"]:
        for button in row:
            size = len(button["callback_data"].encode("utf-8"))
            if size > MAX_CALLBACK_LEN:
                raise ValueError(
                    f"callback_data exceeds Telegram 64B cap ({size}B): "
                    f"{button['callback_data']!r}"
                )
    return keyboard


def _options_keyboard(options: list[str]) -> dict[str, Any]:
    """Inline keyboard with one button per option (callback = option text)."""
    return {"inline_keyboard": [[{"text": opt, "callback_data": opt}] for opt in options]}


def _discard_stale_updates(
    token: str,
    transport: Optional[Callable[..., dict[str, Any]]] = None,
) -> int:
    """Discard pending updates left by previous gates; return next offset.

    Queries ``getUpdates`` with ``offset=-1`` (newest update only,
    non-blocking) and converts it into a start offset past everything seen
    so far. The waiter then begins polling from there, so a button press
    from an older task/stage is never replayed into the new gate.

    Note on Bot API semantics: ``offset=-1`` alone only *peeks* at the
    latest update — the actual discard happens because the returned
    ``update_id + 1`` becomes the next poll's offset, confirming everything
    before it. Returns 0 when the queue is already empty.
    """
    body = _api(token, "getUpdates", {"offset": -1, "timeout": 0}, transport)
    results = body.get("result", [])
    if not results:
        return 0
    return max(int(update.get("update_id", 0)) for update in results) + 1


def _wait_for_update(
    token: str,
    chat_id: str,
    timeout_s: int,
    transport: Optional[Callable[..., dict[str, Any]]] = None,
    expected_action_prefix: Optional[str] = None,
    start_offset: int = 0,
) -> dict[str, Any]:
    """Long-poll ``getUpdates`` until an update for ``chat_id`` arrives.

    Accepts either a ``callback_query`` (inline button press) or a plain
    ``message`` (typed reply). Returns the raw update dict.

    Args:
        token: Bot token.
        chat_id: Target chat id (both callbacks and messages are filtered).
        timeout_s: Give up after this many seconds.
        transport: Test hook forwarded to ``_api``.
        expected_action_prefix: When set (e.g. ``":167:qa"``), ONLY the two
            exact callbacks ``"approve"+prefix`` / ``"reject"+prefix`` are
            accepted. Bare substring matching is deliberately NOT used: one
            stage's slug is often a prefix of another's (``planning`` vs
            ``planning-review``), and a substring match would let a gate
            consume a sibling stage's decision.
        start_offset: First ``update_id`` to consider — pass the value from
            ``_discard_stale_updates`` so stale history is never replayed.

    Raises:
        TimeoutError: When ``timeout_s`` elapses with no matching update.
    """
    deadline = time.monotonic() + timeout_s
    offset = start_offset
    while time.monotonic() < deadline:
        window = max(1, min(POLL_WINDOW, int(deadline - time.monotonic())))
        body = _api(
            token,
            "getUpdates",
            {"offset": offset, "timeout": window, "allowed_updates": ["message", "callback_query"]},
            transport,
        )
        for update in body.get("result", []):
            offset = max(offset, int(update.get("update_id", 0)) + 1)
            # Callback press on our keyboard?
            callback = update.get("callback_query") or {}
            callback_msg = callback.get("message") or {}
            callback_chat = callback_msg.get("chat") or {}
            if str(callback_chat.get("id", "")) == str(chat_id) and callback.get("data"):
                data = str(callback["data"])
                if expected_action_prefix is not None and data not in (
                    "approve" + expected_action_prefix,
                    "reject" + expected_action_prefix,
                ):
                    continue  # Another gate's button — skip, keep polling.
                # Acknowledge immediately: dismisses the Telegram loading
                # spinner on the manager's button press.
                if callback.get("id"):
                    _api(
                        token,
                        "answerCallbackQuery",
                        {"callback_query_id": callback["id"]},
                        transport,
                    )
                return update
            # Plain typed reply in the target chat?
            message = update.get("message") or {}
            msg_chat = message.get("chat") or {}
            if str(msg_chat.get("id", "")) == str(chat_id) and message.get("text"):
                return update
    raise TimeoutError(f"No Telegram response within {timeout_s}s")


def _extract_answer(update: dict[str, Any]) -> str:
    """Pull the manager's answer out of a raw update (callback or text).

    Scoped callback data (``approve:{task}:{stage}``) normalizes back to the
    plain ``"approve"`` / ``"reject"`` decision strings callers gate on;
    anything else (legacy unscoped data, option buttons) passes through raw.
    """
    callback = update.get("callback_query") or {}
    if callback.get("data"):
        data = str(callback["data"])
        if data.startswith("approve:"):
            return "approve"
        if data.startswith("reject:"):
            return "reject"
        return data
    message = update.get("message") or {}
    return str(message.get("text", ""))


def send_approval_request(
    task_id: int,
    stage: str,
    summary: str,
    task_file_path: str = "",
    transport: Optional[Callable[..., dict[str, Any]]] = None,
    ask_note: bool = True,
    note_timeout_s: int = 300,
) -> dict[str, Any]:
    """Post an approval gate to the manager and await Approve/Reject.

    Args:
        task_id: Owning task id (echoed in the message + callback scope).
        stage: Gate name, e.g. ``"QA"`` or ``"closure"``.
        summary: Human-readable stage summary. Oversized summaries are split
            into sequential messages (keyboard on the last) so the gate
            never silently truncates context.
        task_file_path: Optional task file reference echoed in the message.
        transport: Test hook forwarded to ``_api``/``_wait_for_update``.
        ask_note: When True (default), follow a decision with one force-reply
            prompt inviting a manager note (reject reasons, conditions).
        note_timeout_s: Window for the note reply. Expiry (or ``/skip``)
            resolves ``note`` to None — the GATE NEVER blocks on a note.

    Returns:
        Dict with ``sent`` (bool), ``decision`` (``"approve"``/``"reject"``
        or raw text), ``note`` (str or None), ``update_id``, and on failure
        ``reason`` instead of a decision. Never raises for missing
        credentials — returns ``{"sent": False, "reason": ...}``.
    """
    token = _env("TELEGRAM_BOT_TOKEN")
    chat_id = _env("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return {"sent": False, "reason": "missing Telegram credentials"}
    timeout_s = int(os.environ.get("TELEGRAM_APPROVAL_TIMEOUT_SECONDS", "1800") or 1800)

    # NOTE: pass the RAW summary — post_approval_gate prepends its own
    # header/ref. Passing pre-formatted text would duplicate the header.
    post = post_approval_gate(task_id, stage, summary, task_file_path, transport)
    if not post.get("sent"):
        return post
    return await_gate_decision(
        task_id,
        stage,
        timeout_s,
        ask_note=ask_note,
        note_timeout_s=note_timeout_s,
        transport=transport,
        start_offset=post["start_offset"],
    )


def post_approval_gate(
    task_id: int,
    stage: str,
    summary: str,
    task_file_path: str = "",
    transport: Optional[Callable[..., dict[str, Any]]] = None,
) -> dict[str, Any]:
    """Post a gate keyboard WITHOUT waiting (split-gate send half).

    Long blocking waits always outlive the MCP tool timeout, so the waiter
    gets killed and the manager's press lands unconsumed. Callers that
    cannot hold a tool call open (approval gates) post with this function
    and collect the decision with ``await_gate_decision`` in short,
    re-callable windows instead.

    Returns ``{"sent": True, "stage_slug", "start_offset"}`` (the offset to
    resume polling from) or ``{"sent": False, "reason"}``.
    """
    token = _env("TELEGRAM_BOT_TOKEN")
    chat_id = _env("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return {"sent": False, "reason": "missing Telegram credentials"}
    header = f"Task {task_id} — approval requested: {stage}\n"
    ref = f"Task file: {task_file_path}\n" if task_file_path else ""
    full_text = (header + ref + "\n" + summary).strip()
    chunks = [full_text[i : i + MAX_TEXT_LEN] for i in range(0, len(full_text), MAX_TEXT_LEN)]
    try:
        # Drain the queue first: a stale Approve from a previous gate must
        # never auto-resolve this one.
        start_offset = _discard_stale_updates(token, transport)
        for chunk in chunks[:-1]:
            _api(token, "sendMessage", {"chat_id": chat_id, "text": chunk}, transport)
        _api(
            token,
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": chunks[-1],
                "reply_markup": _approval_keyboard(int(task_id), str(stage)),
            },
            transport,
        )
        return {
            "sent": True,
            "task_id": int(task_id),
            "stage": str(stage),
            "stage_slug": slugify_stage(stage),
            "start_offset": start_offset,
        }
    except (RuntimeError, ValueError) as exc:
        return {"sent": False, "reason": str(exc)}


def await_gate_decision(
    task_id: int,
    stage: str,
    wait_s: int = 90,
    ask_note: bool = True,
    note_timeout_s: int = 300,
    transport: Optional[Callable[..., dict[str, Any]]] = None,
    start_offset: int = 0,
) -> dict[str, Any]:
    """Poll one short window for a posted gate's decision (split-gate wait half).

    Waits at most ``wait_s`` seconds (keep it under the MCP tool timeout —
    90s default). On ``"status": "timeout"`` the caller simply calls again
    with the returned ``start_offset``; the manager's eventual press is
    never lost because polling always resumes past consumed updates. On a
    decision, the optional note flow runs exactly like the blocking gate.
    """
    token = _env("TELEGRAM_BOT_TOKEN")
    chat_id = _env("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return {"sent": False, "reason": "missing Telegram credentials"}
    slug = slugify_stage(stage)
    try:
        update = _wait_for_update(
            token,
            chat_id,
            wait_s,
            transport,
            expected_action_prefix=f":{task_id}:{slug}",
            start_offset=start_offset,
        )
        decision = _extract_answer(update)
        note = _collect_note(
            token, chat_id, decision, ask_note, note_timeout_s, transport
        )
        return {
            "sent": True,
            "status": "decided",
            "decision": decision,
            "note": note,
            "update_id": update.get("update_id"),
            "start_offset": int(update.get("update_id", start_offset - 1)) + 1,
        }
    except TimeoutError:
        # Re-read the newest update id so the next window resumes cleanly
        # past anything irrelevant that arrived meanwhile.
        try:
            resume = _discard_stale_updates(token, transport)
        except RuntimeError:
            resume = start_offset
        return {"sent": True, "status": "timeout", "start_offset": resume}
    except RuntimeError as exc:
        return {"sent": False, "reason": str(exc)}


def _collect_note(
    token: str,
    chat_id: str,
    decision: str,
    ask_note: bool,
    note_timeout_s: int,
    transport: Optional[Callable[..., dict[str, Any]]] = None,
) -> Optional[str]:
    """Invite one optional manager note after a gate decision.

    Sends a force-reply prompt and waits up to ``note_timeout_s``. Silence,
    ``/skip``, or a disabled ``ask_note`` resolves to None — callers must
    treat the gate as already decided regardless of the note outcome.
    """
    if not ask_note:
        return None
    _api(
        token,
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": f"Decision recorded: {decision}. Reply with a note (why / conditions), or /skip.",
            "reply_markup": {"force_reply": True},
        },
        transport,
    )
    try:
        update = _wait_for_update(token, chat_id, note_timeout_s, transport)
    except TimeoutError:
        return None  # Silence is consent to proceed without a note.
    note = _extract_answer(update).strip()
    if not note or note.lower() == "/skip":
        return None
    return note


def send_admin_question(
    task_id: int,
    question: str,
    options: Optional[list[str]] = None,
    transport: Optional[Callable[..., dict[str, Any]]] = None,
) -> str:
    """Send an open question to the manager and await the reply text.

    Args:
        task_id: Owning task id (echoed in the message).
        question: Question text.
        options: Optional inline-button options; without them any typed
            reply is accepted.
        transport: Test hook forwarded to ``_api``/``_wait_for_update``.

    Returns:
        The manager's answer (callback data or message text), or an
        explanatory ``"ERROR: ..."`` string when credentials are missing
        or polling fails — never raises, so the MCP tool always returns.
    """
    token = _env("TELEGRAM_BOT_TOKEN")
    chat_id = _env("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return "ERROR: missing Telegram credentials"
    timeout_s = int(os.environ.get("TELEGRAM_APPROVAL_TIMEOUT_SECONDS", "1800") or 1800)
    payload: dict[str, Any] = {
        "chat_id": chat_id,
        "text": f"Task {task_id} — manager input needed:\n\n{question}".strip(),
    }
    if options:
        payload["reply_markup"] = _options_keyboard(list(options))
    try:
        start_offset = _discard_stale_updates(token, transport)
        _api(token, "sendMessage", payload, transport)
        update = _wait_for_update(token, chat_id, timeout_s, transport, start_offset=start_offset)
        return _extract_answer(update)
    except (RuntimeError, TimeoutError) as exc:
        return f"ERROR: {exc}"


# Re-export for callers that reference the query-string form explicitly.
urlencode = urllib.parse.urlencode
