"""Tests for router.py — LLM routing and context building."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from router import LLMRouter, _load_file_if_exists
from models import LoopEngineConfig


def _make_config():
    return LoopEngineConfig(approval={"chat_id": 123})


def test_load_file_exists():
    p = os.path.join(os.path.dirname(__file__), "models.py")
    content = _load_file_if_exists(p)
    assert "LoopEngineConfig" in content


def test_load_file_missing():
    content = _load_file_if_exists("/nonexistent/file.md")
    assert content == ""


def test_resolve_model_with_env():
    os.environ["KIMI_API_KEY"] = "test-key"
    cfg = _make_config()
    router = LLMRouter(cfg)
    model, reasoning = router._resolve_model("quick")
    assert model == "kimi/kimi-k3"
    del os.environ["KIMI_API_KEY"]


def test_resolve_model_fallback():
    for key in ["KIMI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]:
        os.environ.pop(key, None)
    cfg = _make_config()
    router = LLMRouter(cfg)
    model, reasoning = router._resolve_model("quick")
    assert model == cfg.default_provider


def test_build_system_context():
    cfg = _make_config()
    router = LLMRouter(cfg)
    ctx = router._build_system_context("architect")
    assert "Architect" in ctx
    assert len(ctx) > 100


def test_build_system_context_qa():
    cfg = _make_config()
    router = LLMRouter(cfg)
    ctx = router._build_system_context("qa_engineer")
    assert "QA Engineer" in ctx


def test_route_plan():
    cfg = _make_config()
    router = LLMRouter(cfg)
    routing = router.route_plan("## Goal\nBuild a feature", "quick")
    assert routing["model"] is not None
    assert routing["temperature"] == 0.3
    assert "Build a feature" in routing["user"]


def test_route_qa():
    cfg = _make_config()
    router = LLMRouter(cfg)
    routing = router.route_qa("Task content", "diff here")
    assert routing["temperature"] == 0.1
    assert "diff here" in routing["user"]


def test_route_review():
    cfg = _make_config()
    router = LLMRouter(cfg)
    routing = router.route_review("Task", "QA passed")
    assert routing["temperature"] == 0.2


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = failed = 0
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
