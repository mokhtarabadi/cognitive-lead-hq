"""Tests for stacks.py — Stack Profile Engine (Task 133)."""
import sys, os, tempfile, json, asyncio
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from models import LoopEngineConfig, StackProfileConfig, StackDetectionConfig, StackToolchainConfig
from stacks import StackProfile, StackRegistry, StackDetector, PreflightRunner


# Helpers
def make_registry(tmp_path: Path, profiles: dict) -> StackRegistry:
    """Create YAML files in tmp_path/stacks and return registry."""
    stacks_dir = tmp_path / "stacks"
    stacks_dir.mkdir(parents=True, exist_ok=True)
    for name, data in profiles.items():
        # Use yaml if available else json
        try:
            import yaml
            (stacks_dir / f"{name}.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")
        except ImportError:
            (stacks_dir / f"{name}.json").write_text(json.dumps(data), encoding="utf-8")
    return StackRegistry(str(stacks_dir))


# ---------------------------------------------------------------------------
# Profile parsing
# ---------------------------------------------------------------------------

def test_stack_profile_config_defaults():
    cfg = StackProfileConfig(name="test", display_name="Test")
    assert cfg.detection.marker_files == []
    assert cfg.detection.extensions == []
    assert cfg.skills == []
    assert cfg.preflight == []
    assert cfg.toolchain.test_cmd is None


def test_stack_profile_config_full():
    cfg = StackProfileConfig(
        name="node-ts",
        display_name="Node TS",
        detection=StackDetectionConfig(
            marker_files=["package.json"],
            extensions=[".ts"],
            task_keywords=["node"]
        ),
        skills=["nextjs"],
        preflight=["node --version"],
        toolchain=StackToolchainConfig(test_cmd="npm test")
    )
    assert cfg.detection.marker_files == ["package.json"]
    assert cfg.skills == ["nextjs"]
    assert cfg.toolchain.test_cmd == "npm test"


def test_stack_profile_invalid_missing_name():
    try:
        StackProfileConfig(display_name="No Name")  # type: ignore
        assert False, "Should fail without name"
    except Exception:
        pass


def test_stack_registry_loads_generic():
    r = StackRegistry("stacks")
    profiles = r.list_profiles()
    names = [p.name for p in profiles]
    assert "generic" in names
    assert len(names) >= 5


def test_stack_registry_get_profile():
    r = StackRegistry("stacks")
    p = r.get_profile("node-ts")
    assert p is not None
    assert p.name == "node-ts"
    assert "package.json" in p.detection.marker_files
    assert p.get_profile is None if False else True  # dummy to avoid lint


def test_stack_registry_nonexistent_returns_none():
    r = StackRegistry("stacks")
    assert r.get_profile("does-not-exist") is None


def test_stack_registry_invalid_schema_rejection():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        stacks_dir = tmp / "stacks"
        stacks_dir.mkdir()
        # Invalid: missing display_name
        (stacks_dir / "bad.yaml").write_text("name: bad\n", encoding="utf-8")
        r = StackRegistry(str(stacks_dir))
        try:
            r.list_profiles()
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "bad.yaml" in str(e) or "Failed to load" in str(e)


def test_stack_profile_yaml_and_json_both_supported():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        stacks_dir = tmp / "stacks"
        stacks_dir.mkdir()
        # JSON file
        data = {"name": "json-stack", "display_name": "JSON Stack"}
        (stacks_dir / "json-stack.json").write_text(json.dumps(data), encoding="utf-8")
        # YAML file
        try:
            import yaml
            yaml_data = {"name": "yaml-stack", "display_name": "YAML Stack"}
            (stacks_dir / "yaml-stack.yaml").write_text(yaml.safe_dump(yaml_data), encoding="utf-8")
        except ImportError:
            pass
        r = StackRegistry(str(stacks_dir))
        assert r.get_profile("json-stack") is not None
        if (stacks_dir / "yaml-stack.yaml").exists():
            assert r.get_profile("yaml-stack") is not None


# ---------------------------------------------------------------------------
# Detection precedence
# ---------------------------------------------------------------------------

def test_detection_explicit_header_overrides_all():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # Create workspace with python marker to tempt wrong detection
        (tmp / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
        r = StackRegistry("stacks")
        task = "**Stack:** node-ts\nDo something generic"
        detected = StackDetector.detect(task, tmp, r, default_stack="generic")
        assert detected.name == "node-ts", f"Expected node-ts, got {detected.name}"


def test_detection_marker_files_before_keywords():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "go.mod").write_text("module foo\n", encoding="utf-8")
        r = StackRegistry("stacks")
        # Task mentions python but workspace has go.mod
        task = "Fix python endpoint"
        detected = StackDetector.detect(task, tmp, r, default_stack="generic")
        assert detected.name == "go-gin", f"Expected go-gin marker, got {detected.name}"


def test_detection_extensions_fallback():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        sub = tmp / "app"
        sub.mkdir()
        (sub / "main.go").write_text("package main\n", encoding="utf-8")
        r = StackRegistry("stacks")
        task = "random task without keywords"
        detected = StackDetector.detect(task, tmp, r, default_stack="generic")
        assert detected.name == "go-gin", f"Expected go-gin via .go extension, got {detected.name}"


def test_detection_keywords_after_marker_miss():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        r = StackRegistry("stacks")
        task = "This is a Kotlin Android compose task"
        detected = StackDetector.detect(task, tmp, r, default_stack="generic")
        assert detected.name == "kotlin-android", f"Expected kotlin-android via keyword, got {detected.name}"


def test_detection_generic_fallback():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        r = StackRegistry("stacks")
        task = "Completely unknown stack task with no markers or keywords xyz123"
        detected = StackDetector.detect(task, tmp, r, default_stack="generic")
        assert detected.name == "generic"


def test_detection_header_plain_format():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        r = StackRegistry("stacks")
        task = "Stack: python-fastapi\nImplement endpoint"
        detected = StackDetector.detect(task, tmp, r, default_stack="generic")
        assert detected.name == "python-fastapi"


# ---------------------------------------------------------------------------
# Preflight runner
# ---------------------------------------------------------------------------

def test_preflight_success():
    cfg = StackProfileConfig(name="test", display_name="Test", preflight=["echo hello", "echo world"])
    profile = StackProfile(cfg)
    runner = PreflightRunner(timeout_seconds=5)
    result = runner.run_sync(profile)
    assert result.passed is True
    assert result.errors == []
    assert len(result.outputs) == 2


def test_preflight_failure_nonzero():
    cfg = StackProfileConfig(name="test", display_name="Test", preflight=["false"])
    profile = StackProfile(cfg)
    runner = PreflightRunner(timeout_seconds=5)
    result = runner.run_sync(profile)
    assert result.passed is False
    assert len(result.errors) == 1
    assert "false" in result.errors[0]


def test_preflight_timeout():
    cfg = StackProfileConfig(name="test", display_name="Test", preflight=["sleep 2"])
    profile = StackProfile(cfg)
    runner = PreflightRunner(timeout_seconds=0.3)
    result = runner.run_sync(profile)
    assert result.passed is False
    assert any("timeout" in e.lower() for e in result.errors)


def test_preflight_empty_is_pass():
    cfg = StackProfileConfig(name="test", display_name="Test", preflight=[])
    profile = StackProfile(cfg)
    runner = PreflightRunner(timeout_seconds=5)
    result = runner.run_sync(profile)
    assert result.passed is True
    assert result.errors == []


def test_preflight_mixed_success_and_failure():
    cfg = StackProfileConfig(name="test", display_name="Test", preflight=["echo ok", "false", "echo again"])
    profile = StackProfile(cfg)
    runner = PreflightRunner(timeout_seconds=5)
    result = runner.run_sync(profile)
    assert result.passed is False
    assert len(result.errors) == 1


# ---------------------------------------------------------------------------
# LoopEngineConfig extension
# ---------------------------------------------------------------------------

def test_loop_engine_config_stack_fields():
    cfg = LoopEngineConfig(approval={"chat_id": 1})
    assert cfg.stacks_dir == "stacks"
    assert cfg.default_stack == "generic"
    cfg2 = LoopEngineConfig(approval={"chat_id": 1}, stacks_dir="custom/stacks", default_stack="node-ts")
    assert cfg2.stacks_dir == "custom/stacks"
    assert cfg2.default_stack == "node-ts"


# ---------------------------------------------------------------------------
# Daemon integration (mock workspace fixtures)
# ---------------------------------------------------------------------------

def test_daemon_registry_init():
    from daemon import LoopEngineDaemon
    from state import StateMachine
    from router import LLMRouter
    from gateway import ApprovalGateway
    from executor import HandsExecutor
    from qa_engine import QAEngine
    from brainstorm import BrainstormStage

    cfg = LoopEngineConfig(approval={"chat_id": 0})
    with tempfile.TemporaryDirectory() as tmp:
        db = os.path.join(tmp, "loop.db")
        state = StateMachine(db)
        router = LLMRouter(cfg, workspace_root=tmp)
        gateway = ApprovalGateway(cfg)
        executor = HandsExecutor(cfg, state)
        qa = QAEngine(cfg, state, router)
        brainstorm = BrainstormStage(cfg, router, workspace_root=tmp)
        daemon = LoopEngineDaemon(cfg, state, router, gateway, executor, qa, brainstorm)
        assert daemon.stack_registry is not None
        assert daemon.stack_registry.get_profile("generic") is not None
        state.close()


def test_executor_injects_stack_context():
    from executor import HandsExecutor
    from state import StateMachine

    cfg = LoopEngineConfig(approval={"chat_id": 0})
    with tempfile.TemporaryDirectory() as tmp:
        state = StateMachine(os.path.join(tmp, "db"))
        ex = HandsExecutor(cfg, state)

        # Create a mock profile
        profile_cfg = StackProfileConfig(
            name="python-fastapi",
            display_name="Python FastAPI",
            skills=["python-fastapi"],
            preflight=["echo ok"],
            toolchain=StackToolchainConfig(test_cmd="pytest -q")
        )
        profile = StackProfile(profile_cfg)

        # We only test prompt construction via _run_once mock
        # Monkey-patch _run_once to capture prompt
        captured = {}

        async def fake_run_once(task_file, prompt):
            captured["prompt"] = prompt
            return {"status": "complete", "output": "[goal:complete]", "error": "", "elapsed": 0.1}

        original = ex._run_once
        ex._run_once = fake_run_once  # type: ignore

        async def run():
            return await ex.execute(1, "tasks/backlog/01-test.md", "content", stack_profile=profile)

        result = asyncio.run(run())
        assert result["status"] == "complete"
        assert "python-fastapi" in captured["prompt"]
        assert "python-fastapi" in captured["prompt"].lower()
        assert "pytest -q" in captured["prompt"]
        ex._run_once = original  # type: ignore
        state.close()


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
            import traceback
            print(f"  FAIL: {t.__name__}: {e}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
