"""Tests for models.py — Pydantic config validation."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from models import (
    LoopEngineConfig, TaskState, CategoryConfig,
    ProviderConcurrency, IdleConfig, ApprovalConfig
)


def test_task_state_values():
    assert TaskState.BACKLOG.value == "backlog"
    assert TaskState.IMPLEMENTING.value == "implementing"
    assert TaskState.CLOSED.value == "closed"
    assert TaskState.CRASHED.value == "crashed"
    assert len(TaskState) == 10


def test_category_config():
    c = CategoryConfig(models=["kimi/kimi-k3"], description="test")
    assert c.models == ["kimi/kimi-k3"]
    assert c.reasoning is None


def test_category_config_requires_models():
    try:
        CategoryConfig(models=[])
        assert False, "Should have failed"
    except Exception:
        pass


def test_provider_concurrency_defaults():
    pc = ProviderConcurrency()
    assert pc.anthropic == 3
    assert pc.openai == 3


def test_idle_config_defaults():
    ic = IdleConfig()
    assert ic.thinking_timeout_seconds == 60
    assert ic.executing_timeout_seconds == 900
    assert ic.max_retries == 5


def test_approval_config():
    ac = ApprovalConfig(chat_id=12345)
    assert ac.bot_token_env == "TELEGRAM_BOT_TOKEN"
    assert ac.chat_id == 12345


def test_loop_engine_config_defaults():
    cfg = LoopEngineConfig(approval={"chat_id": 123})
    assert cfg.max_parallel_tasks == 1
    assert "quick" in cfg.categories
    assert "deep" in cfg.categories
    assert cfg.max_qa_retries == 3


def test_loop_engine_config_max_parallel_bounds():
    try:
        LoopEngineConfig(approval={"chat_id": 1}, max_parallel_tasks=5)
        assert False, "Should fail: max is 4"
    except Exception:
        pass

    cfg = LoopEngineConfig(approval={"chat_id": 1}, max_parallel_tasks=4)
    assert cfg.max_parallel_tasks == 4


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS: {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
