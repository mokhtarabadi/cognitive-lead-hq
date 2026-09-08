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

import json
import os
import time
import urllib.parse
import urllib.request
from typing import Any, Callable, Optional

# Telegram caps text messages at 4096 chars; stay safely under it.
MAX_TEXT_LEN = 3500
# Long-poll window per getUpdates call (seconds).
POLL_WINDOW = 25


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


def _approval_keyboard(task_id: int, stage: str) -> dict[str, Any]:
    """Inline keyboard with task/stage-scoped Approve / Reject buttons.

    ``callback_data`` embeds ``{task_id}:{stage}`` (e.g. ``approve:167:QA``)
    so concurrent gates on different tasks can never cross-accept each
    other's button presses — the waiter filters on the expected suffix.
    """
    return {
        "inline_keyboard": [
            [
                {"text": "✅ Approve", "callback_data": f"approve:{task_id}:{stage}"},
                {"text": "❌ Reject", "callback_data": f"reject:{task_id}:{stage}"},
            ]
        ]
    }


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
        expected_action_prefix: When set (e.g. ``":167:QA"``), callbacks
            whose data does NOT contain the prefix belong to a different
            gate and are skipped (offset still advances past them).
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
                if expected_action_prefix is not None and expected_action_prefix not in data:
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

    Returns:
        Dict with ``sent`` (bool), ``decision`` (``"approve"``/``"reject"``
        or raw text), ``update_id``, and on failure ``reason`` instead of a
        decision. Never raises for missing credentials — returns
        ``{"sent": False, "reason": "missing Telegram credentials"}``.
    """
    token = _env("TELEGRAM_BOT_TOKEN")
    chat_id = _env("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return {"sent": False, "reason": "missing Telegram credentials"}
    timeout_s = int(os.environ.get("TELEGRAM_APPROVAL_TIMEOUT_SECONDS", "1800") or 1800)

    header = f"Task {task_id} — approval requested: {stage}\n"
    ref = f"Task file: {task_file_path}\n" if task_file_path else ""
    full_text = (header + ref + "\n" + summary).strip()
    # Chunk oversized bodies into sequential messages (Telegram caps single
    # messages); the inline keyboard rides on the FINAL chunk so the manager
    # decides with the complete context above. Nothing is truncated.
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
        update = _wait_for_update(
            token,
            chat_id,
            timeout_s,
            transport,
            expected_action_prefix=f":{task_id}:{stage}",
            start_offset=start_offset,
        )
        return {
            "sent": True,
            "decision": _extract_answer(update),
            "update_id": update.get("update_id"),
        }
    except (RuntimeError, TimeoutError) as exc:
        return {"sent": False, "reason": str(exc)}


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
