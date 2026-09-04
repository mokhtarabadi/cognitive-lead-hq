"""Unit tests for Multi-Project Topic Routing (Task 143)."""
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, os.path.dirname(__file__))

from models import LoopEngineConfig, ProjectTopicConfig
from multi_project import MultiProjectRouter


def _cfg():
    return [
        ProjectTopicConfig(topic_id=10, project_name="alpha", workspace_root="/tmp/alpha"),
        ProjectTopicConfig(topic_id=20, project_name="beta", workspace_root="/tmp/beta"),
    ]


def test_topic_to_workspace_lookup():
    r = MultiProjectRouter(_cfg())
    assert r.get_workspace_for_topic(10) == Path("/tmp/alpha")
    assert r.get_workspace_for_topic(20) == Path("/tmp/beta")


def test_workspace_to_topic_lookup():
    r = MultiProjectRouter(_cfg())
    assert r.get_topic_for_workspace("/tmp/alpha") == 10
    assert r.get_topic_for_workspace(Path("/tmp/beta")) == 20


def test_task_path_to_topic_resolution():
    r = MultiProjectRouter(_cfg())
    assert r.get_topic_for_task("/tmp/alpha/tasks/backlog/01-x.md") == 10
    assert r.get_topic_for_task("/tmp/beta/tasks/qa/02-y.md") == 20


def test_unknown_topic_fallback_none():
    r = MultiProjectRouter(_cfg())
    assert r.get_workspace_for_topic(999) is None
    assert r.get_topic_for_workspace("/tmp/unknown") is None
    assert r.get_topic_for_task("/tmp/unknown/file.md") is None
    assert r.get_project_name(999) is None


def test_project_name_lookup():
    r = MultiProjectRouter(_cfg())
    assert r.get_project_name(10) == "alpha"
    assert r.get_project_name(20) == "beta"


def test_models_multi_project_field_defaults():
    cfg = LoopEngineConfig(approval={"chat_id": 1})
    assert cfg.multi_project == []
    cfg2 = LoopEngineConfig(
        approval={"chat_id": 1},
        multi_project=[
            {"topic_id": 1, "project_name": "p", "workspace_root": "/tmp/p"}
        ],
    )
    assert cfg2.multi_project[0].topic_id == 1
    assert cfg2.multi_project[0].target_hashtags == ["bug", "feature"]


def test_gateway_message_thread_id_propagation():
    import asyncio
    from gateway import ApprovalGateway

    cfg = LoopEngineConfig(approval={"chat_id": 123})
    gw = ApprovalGateway(cfg)
    mock_bot = MagicMock()
    mock_bot.send_message = AsyncMock(return_value=MagicMock())
    gw._get_bot = lambda: mock_bot

    async def _run():
        await gw.send_progress(5, "hello", message_thread_id=77)
        await gw.send_task_trigger_card(6, "title", "file.md", message_thread_id=88)
        await gw.send_boot_scan_summary([{"task_id": 1, "title": "t"}], message_thread_id=99)

    asyncio.run(_run())
    for call in mock_bot.send_message.call_args_list:
        kwargs = call.kwargs
        assert "message_thread_id" in kwargs
    assert mock_bot.send_message.call_args_list[0].kwargs["message_thread_id"] == 77
    assert mock_bot.send_message.call_args_list[1].kwargs["message_thread_id"] == 88
    assert mock_bot.send_message.call_args_list[2].kwargs["message_thread_id"] == 99
