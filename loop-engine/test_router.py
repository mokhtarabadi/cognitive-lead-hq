"""Tests for router.py — LLM routing and context building."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from router import LLMRouter, _load_file_if_exists
from models import LoopEngineConfig, StackProfileConfig
from stacks import StackProfile


def _make_config():
    return LoopEngineConfig(approval={"chat_id": 123})


def _make_stack_profile(prefs):
    return StackProfile(StackProfileConfig(
        name="test-stack", display_name="Test Stack", model_preferences=prefs))


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


# --- Stack-Aware Model Routing (LE-3) ---

def test_resolve_model_stack_preferred_with_env():
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    cfg = _make_config()
    router = LLMRouter(cfg)
    profile = _make_stack_profile({"deep": ["anthropic/claude-3-7-sonnet", "openai/gpt-5.6-sol"]})
    model, reasoning = router._resolve_model("deep", stack_profile=profile)
    assert model == "anthropic/claude-3-7-sonnet"
    assert reasoning == "medium"  # deep category reasoning
    del os.environ["ANTHROPIC_API_KEY"]


def test_resolve_model_stack_preferred_second_model_when_first_unkeyed():
    for key in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "KIMI_API_KEY"]:
        os.environ.pop(key, None)
    os.environ["OPENAI_API_KEY"] = "test-key"
    cfg = _make_config()
    router = LLMRouter(cfg)
    profile = _make_stack_profile({"deep": ["anthropic/claude-3-7-sonnet", "openai/gpt-5.6-sol"]})
    model, reasoning = router._resolve_model("deep", stack_profile=profile)
    assert model == "openai/gpt-5.6-sol"  # first unkeyed, second keyed wins
    assert reasoning == "medium"
    del os.environ["OPENAI_API_KEY"]


def test_resolve_model_stack_fallback_category_when_key_missing():
    for key in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "KIMI_API_KEY"]:
        os.environ.pop(key, None)
    os.environ["OPENAI_API_KEY"] = "test-key"
    cfg = _make_config()
    router = LLMRouter(cfg)
    profile = _make_stack_profile({"deep": ["anthropic/claude-3-7-sonnet"]})
    model, reasoning = router._resolve_model("deep", stack_profile=profile)
    assert model == "openai/gpt-5.6-sol"  # Tier 2 category fallback
    assert reasoning == "medium"
    del os.environ["OPENAI_API_KEY"]


def test_resolve_model_stack_empty_preferences():
    for key in ["KIMI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]:
        os.environ.pop(key, None)
    os.environ["KIMI_API_KEY"] = "test-key"
    cfg = _make_config()
    router = LLMRouter(cfg)
    profile = _make_stack_profile({})
    model, reasoning = router._resolve_model("quick", stack_profile=profile)
    assert model == "kimi/kimi-k3"
    del os.environ["KIMI_API_KEY"]


def test_resolve_model_stack_wildcard():
    os.environ["GEMINI_API_KEY"] = "test-key"
    cfg = _make_config()
    router = LLMRouter(cfg)
    profile = _make_stack_profile({"*": ["gemini/gemini-2.5-flash"]})
    model, reasoning = router._resolve_model("quick", stack_profile=profile)
    assert model == "gemini/gemini-2.5-flash"
    del os.environ["GEMINI_API_KEY"]


def test_resolve_model_stack_dict_profile():
    os.environ["KIMI_API_KEY"] = "test-key"
    cfg = _make_config()
    router = LLMRouter(cfg)
    profile = {"model_preferences": {"quick": ["kimi/kimi-k3"]}}
    model, reasoning = router._resolve_model("quick", stack_profile=profile)
    assert model == "kimi/kimi-k3"
    del os.environ["KIMI_API_KEY"]


def test_route_plan_with_stack_profile():
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    cfg = _make_config()
    router = LLMRouter(cfg)
    profile = _make_stack_profile({"deep": ["anthropic/claude-3-7-sonnet"]})
    routing = router.route_plan("## Goal\nBuild a feature", "deep", stack_profile=profile)
    assert routing["model"] == "anthropic/claude-3-7-sonnet"
    del os.environ["ANTHROPIC_API_KEY"]


def test_route_qa_with_stack_profile():
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    cfg = _make_config()
    router = LLMRouter(cfg)
    profile = _make_stack_profile({"deep": ["anthropic/claude-3-7-sonnet"]})
    routing = router.route_qa("Task content", "diff here", stack_profile=profile)
    assert routing["model"] == "anthropic/claude-3-7-sonnet"
    del os.environ["ANTHROPIC_API_KEY"]


def test_route_review_with_stack_profile():
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    cfg = _make_config()
    router = LLMRouter(cfg)
    profile = _make_stack_profile({"deep": ["anthropic/claude-3-7-sonnet"]})
    routing = router.route_review("Task", "QA passed", stack_profile=profile)
    assert routing["model"] == "anthropic/claude-3-7-sonnet"
    del os.environ["ANTHROPIC_API_KEY"]


def test_route_with_persona_stack_profile():
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    cfg = _make_config()
    router = LLMRouter(cfg)
    profile = _make_stack_profile({"deep": ["anthropic/claude-3-7-sonnet"]})
    routing = router.route_with_persona("architect", "content", category="deep",
                                        stack_profile=profile)
    assert routing["model"] == "anthropic/claude-3-7-sonnet"
    del os.environ["ANTHROPIC_API_KEY"]


def test_route_plan_backward_compat_no_stack_profile():
    for key in ["KIMI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]:
        os.environ.pop(key, None)
    cfg = _make_config()
    router = LLMRouter(cfg)
    routing = router.route_plan("## Goal\nBuild a feature", "quick")
    assert routing["model"] == cfg.default_provider


def test_route_qa_backward_compat_no_stack_profile():
    for key in ["KIMI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]:
        os.environ.pop(key, None)
    cfg = _make_config()
    router = LLMRouter(cfg)
    routing = router.route_qa("Task content", "diff here")
    assert routing["model"] == cfg.default_provider


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
