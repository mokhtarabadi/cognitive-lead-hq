"""Unit tests for Resilient Telegram Gateway + DLQ (Task 144)."""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from models import LoopEngineConfig
from gateway import ApprovalGateway
from state import StateMachine


def _gateway_with_state(tmp_path):
    cfg = LoopEngineConfig(approval={"chat_id": 1})
    gw = ApprovalGateway(cfg)
    sm = StateMachine(str(tmp_path / "loop.db"))
    gw.set_state(sm)
    return gw, sm


def _err(name, msg="boom"):
    cls = type(name, (Exception,), {})
    cls.__module__ = "telegram.error"
    return cls(msg)


def test_exponential_backoff_on_transient_errors(tmp_path):
    gw, _ = _gateway_with_state(tmp_path)
    calls = {"n": 0}

    async def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise _err("NetworkError", "net down")
        return None

    async def _run():
        # base_delay=0 to keep test fast; verifies retry-until-success
        return await gw._send_with_retry(flaky, max_retries=3, base_delay=0)

    assert asyncio.run(_run()) is True
    assert calls["n"] == 3


def test_fatal_fail_fast_on_auth_errors(tmp_path):
    gw, _ = _gateway_with_state(tmp_path)
    calls = {"n": 0}

    async def bad_token():
        calls["n"] += 1
        raise _err("InvalidToken", "unauthorized")

    async def _run():
        return await gw._send_with_retry(bad_token, max_retries=3, base_delay=0)

    assert asyncio.run(_run()) is False
    assert calls["n"] == 1


def test_dlq_enqueueing_upon_network_failure(tmp_path):
    gw, sm = _gateway_with_state(tmp_path)

    async def always_fail():
        raise _err("TimedOut", "timed out")

    async def _run():
        return await gw._send_with_retry(
            always_fail, max_retries=2, base_delay=0,
            task_id=42, stage="plan", content="hello")

    assert asyncio.run(_run()) is False
    rows = sm.get_dead_letters(42)
    assert len(rows) == 1
    assert rows[0]["stage"] == "plan"
    assert "timed out" in rows[0]["error_reason"]


def test_dlq_retrieval_from_sqlite(tmp_path):
    sm = StateMachine(str(tmp_path / "loop.db"))
    dlq_id = sm.enqueue_dead_letter(7, "review", "payload", "net err")
    assert isinstance(dlq_id, int)
    rows = sm.get_dead_letters(7)
    assert len(rows) == 1
    assert rows[0]["payload"] == "payload"
    sm.clear_dead_letter(rows[0]["id"])
    assert sm.get_dead_letters(7) == []


def test_request_approval_retries_transient_before_giveup(tmp_path):
    """request_approval must route sends via _send_with_retry (Task 144)."""
    from unittest.mock import AsyncMock, MagicMock, patch

    gw, sm = _gateway_with_state(tmp_path)
    gw.config.approval.timeout_seconds = 1
    mock_bot = MagicMock()
    calls = {"n": 0}

    async def _send_message(**kwargs):
        calls["n"] += 1
        if calls["n"] < 3:
            raise _err("NetworkError", "socket drop")
        return MagicMock(message_id=1)

    mock_bot.send_message = AsyncMock(side_effect=_send_message)
    gw._get_bot = lambda: mock_bot
    # Avoid poller side effects; approval will timeout -> False, but retries
    # must already have happened before the wait.
    gw._ensure_poller = lambda: None

    async def _run():
        return await gw.request_approval(99, "plan", "content")

    assert asyncio.run(_run()) is False
    assert calls["n"] == 3
    # Exhaustion would DLQ only after 3+ retries; success on 3rd means no DLQ.
    assert sm.get_dead_letters(99) == []


def test_request_approval_dlq_after_exhausted_retries(tmp_path):
    from unittest.mock import AsyncMock, MagicMock

    gw, sm = _gateway_with_state(tmp_path)
    gw.config.approval.timeout_seconds = 1
    mock_bot = MagicMock()
    mock_bot.send_message = AsyncMock(side_effect=_err("TimedOut", "timed out"))
    # Patch base_delay to 0 for speed
    orig_retry = gw._send_with_retry

    async def _fast_retry(fn, max_retries=3, base_delay=1.0, **kw):
        return await orig_retry(fn, max_retries=max_retries, base_delay=0, **kw)

    gw._send_with_retry = _fast_retry
    gw._get_bot = lambda: mock_bot
    gw._ensure_poller = lambda: None

    async def _run():
        return await gw.request_approval(100, "review", "content")

    assert asyncio.run(_run()) is False
    rows = sm.get_dead_letters(100)
    assert len(rows) == 1
    assert "timed out" in rows[0]["error_reason"]
