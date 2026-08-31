"""Tests for verifier.py — Polyglot Verification & Multi-Toolchain Runner (Task 134)."""
import os
import sys
import tempfile
import asyncio
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from models import StackProfileConfig, StackToolchainConfig
from stacks import StackProfile
from verifier import CommandResult, ToolchainResult, ToolchainRunner


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_profile(lint_cmd, build_cmd, test_cmd, name="test-stack") -> StackProfile:
    cfg = StackProfileConfig(
        name=name,
        display_name=f"Test {name}",
        toolchain=StackToolchainConfig(
            lint_cmd=lint_cmd, build_cmd=build_cmd, test_cmd=test_cmd
        ),
    )
    return StackProfile(cfg)


# ---------------------------------------------------------------------------
# Dataclass contracts
# ---------------------------------------------------------------------------

def test_command_result_defaults():
    r = CommandResult(command="echo hi", cmd_type="lint", passed=True)
    assert r.command == "echo hi"
    assert r.cmd_type == "lint"
    assert r.passed is True
    assert r.skipped is False
    assert r.returncode is None
    assert r.stdout == ""
    assert r.stderr == ""
    assert r.duration_seconds == 0.0


def test_toolchain_result_defaults():
    r = ToolchainResult(passed=True)
    assert r.passed is True
    assert r.commands == []
    assert r.summary == ""
    assert r.report_md == ""


def test_toolchain_runner_init_defaults():
    runner = ToolchainRunner()
    assert runner.timeout_per_command == 120.0
    assert str(runner.evidence_base_dir) == "loop-engine/evidence"


def test_toolchain_runner_custom_init():
    runner = ToolchainRunner(timeout_per_command=30.0, evidence_base_dir="/tmp/ev")
    assert runner.timeout_per_command == 30.0
    assert runner.evidence_base_dir == Path("/tmp/ev")


# ---------------------------------------------------------------------------
# Full toolchain success
# ---------------------------------------------------------------------------

def test_toolchain_full_success():
    profile = make_profile("echo lint", "echo build", "echo test")
    runner = ToolchainRunner(timeout_per_command=5.0)
    # Use temp evidence dir to avoid polluting repo
    with tempfile.TemporaryDirectory() as tmp:
        runner.evidence_base_dir = Path(tmp)
        result = runner.run_sync(profile, task_id=999)
        assert result.passed is True
        assert len(result.commands) == 3
        # Order lint, build, test
        assert result.commands[0].cmd_type == "lint"
        assert result.commands[1].cmd_type == "build"
        assert result.commands[2].cmd_type == "test"
        for c in result.commands:
            assert c.passed is True
            assert c.skipped is False
            assert c.returncode == 0
        assert "PASSED" in result.summary
        assert "lint: PASSED" in result.summary
        assert "build: PASSED" in result.summary
        assert "test: PASSED" in result.summary
        assert "PASSED" in result.report_md
        # Evidence files
        assert (Path(tmp) / "999" / "toolchain_report.md").exists()
        assert (Path(tmp) / "999" / "toolchain_result.txt").read_text() == "PASSED"


def test_toolchain_success_no_task_id_no_evidence():
    profile = make_profile("echo lint", None, "echo test")
    with tempfile.TemporaryDirectory() as tmp:
        runner = ToolchainRunner(timeout_per_command=5.0, evidence_base_dir=tmp)
        result = runner.run_sync(profile, task_id=None)
        assert result.passed is True
        # No task_id → no evidence dir created for task
        assert not (Path(tmp) / "toolchain_report.md").exists()


# ---------------------------------------------------------------------------
# Failure cases — lint / build / test non-zero
# ---------------------------------------------------------------------------

def test_toolchain_failure_on_lint():
    profile = make_profile("false", "echo build", "echo test")
    runner = ToolchainRunner(timeout_per_command=5.0)
    with tempfile.TemporaryDirectory() as tmp:
        runner.evidence_base_dir = Path(tmp)
        result = runner.run_sync(profile, task_id=1)
        assert result.passed is False
        # lint failed
        lint_res = [c for c in result.commands if c.cmd_type == "lint"][0]
        assert lint_res.passed is False
        assert lint_res.returncode != 0
        # build and test still executed? Runner is sequential; all run even if one fails (collect all)
        assert len(result.commands) == 3
        assert "FAILED" in result.summary
        assert "lint: FAILED" in result.summary
        # Report contains failure section
        assert "Failures" in result.report_md
        assert "FAILED" in (Path(tmp) / "1" / "toolchain_result.txt").read_text()


def test_toolchain_failure_on_build():
    profile = make_profile("echo lint", "false", "echo test")
    runner = ToolchainRunner(timeout_per_command=5.0)
    with tempfile.TemporaryDirectory() as tmp:
        runner.evidence_base_dir = Path(tmp)
        result = runner.run_sync(profile)
        assert result.passed is False
        build_res = [c for c in result.commands if c.cmd_type == "build"][0]
        assert build_res.passed is False


def test_toolchain_failure_on_test():
    profile = make_profile("echo lint", "echo build", "false")
    runner = ToolchainRunner(timeout_per_command=5.0)
    result = runner.run_sync(profile)
    assert result.passed is False
    test_res = [c for c in result.commands if c.cmd_type == "test"][0]
    assert test_res.passed is False


def test_toolchain_failure_captures_stdout_stderr():
    # Use sh that writes to stderr and exits 1
    profile = make_profile("sh -c 'echo out_msg; echo err_msg >&2; exit 1'", None, None)
    runner = ToolchainRunner(timeout_per_command=5.0)
    result = runner.run_sync(profile)
    lint_res = [c for c in result.commands if c.cmd_type == "lint"][0]
    assert lint_res.passed is False
    assert "err_msg" in lint_res.stderr or "err_msg" in lint_res.stdout or "err_msg" in result.report_md
    assert "out_msg" in lint_res.stdout or "out_msg" in result.report_md


# ---------------------------------------------------------------------------
# Timeout and kill handling
# ---------------------------------------------------------------------------

def test_toolchain_timeout():
    profile = make_profile("sleep 2", None, None)
    # Very short timeout to trigger kill
    runner = ToolchainRunner(timeout_per_command=0.3)
    with tempfile.TemporaryDirectory() as tmp:
        runner.evidence_base_dir = Path(tmp)
        result = runner.run_sync(profile, task_id=2)
        assert result.passed is False
        lint_res = [c for c in result.commands if c.cmd_type == "lint"][0]
        assert lint_res.passed is False
        assert "timeout" in lint_res.stderr.lower()
        assert lint_res.duration_seconds >= 0.2
        assert "FAILED" in result.report_md


def test_toolchain_timeout_then_success_subsequent():
    # First command times out, second is skipped? Actually second is None so skipped pass, but third should still run
    profile = make_profile("sleep 2", None, "echo test")
    runner = ToolchainRunner(timeout_per_command=0.3)
    result = runner.run_sync(profile)
    assert result.passed is False
    # lint failed due timeout
    assert result.commands[0].passed is False
    # build skipped (None)
    assert result.commands[1].skipped is True
    # test should still be executed and pass
    assert result.commands[2].passed is True


# ---------------------------------------------------------------------------
# Null / empty skip (generic.yaml)
# ---------------------------------------------------------------------------

def test_generic_null_toolchain_all_skipped():
    cfg = StackProfileConfig(name="generic", display_name="Generic")
    profile = StackProfile(cfg)
    runner = ToolchainRunner(timeout_per_command=5.0)
    result = runner.run_sync(profile)
    assert result.passed is True
    assert len(result.commands) == 3
    for c in result.commands:
        assert c.skipped is True
        assert c.passed is True
        assert c.command == "none"
    assert "SKIPPED" in result.summary
    assert "PASSED" in result.summary  # overall PASSED


def test_whitespace_only_skipped():
    profile = make_profile("   ", "  \t ", None)
    runner = ToolchainRunner(timeout_per_command=5.0)
    result = runner.run_sync(profile)
    assert result.passed is True
    assert result.commands[0].skipped is True
    assert result.commands[1].skipped is True
    assert result.commands[2].skipped is True


def test_mixed_null_and_real():
    profile = make_profile(None, "echo build", None)
    runner = ToolchainRunner(timeout_per_command=5.0)
    result = runner.run_sync(profile)
    assert result.passed is True
    assert result.commands[0].skipped is True
    assert result.commands[1].passed is True and not result.commands[1].skipped
    assert result.commands[2].skipped is True


# ---------------------------------------------------------------------------
# Markdown report and evidence persistence
# ---------------------------------------------------------------------------

def test_report_contains_table_and_summary():
    profile = make_profile("echo lint", "echo build", "echo test")
    runner = ToolchainRunner(timeout_per_command=5.0)
    result = runner.run_sync(profile)
    # Table header
    assert "| Type | Command | Result | Duration | Return Code |" in result.report_md
    assert "lint" in result.report_md
    assert "build" in result.report_md
    assert "test" in result.report_md
    assert "# Toolchain Verification Report" in result.report_md
    assert "Toolchain PASSED" in result.report_md


def test_report_failure_details():
    profile = make_profile("false", None, None)
    runner = ToolchainRunner(timeout_per_command=5.0)
    result = runner.run_sync(profile)
    assert "## Failures" in result.report_md
    assert "false" in result.report_md


def test_evidence_persistence_files():
    profile = make_profile("echo lint", "echo build", "echo test")
    with tempfile.TemporaryDirectory() as tmp:
        runner = ToolchainRunner(timeout_per_command=5.0, evidence_base_dir=tmp)
        result = runner.run_sync(profile, task_id=42)
        report_path = Path(tmp) / "42" / "toolchain_report.md"
        result_path = Path(tmp) / "42" / "toolchain_result.txt"
        assert report_path.exists()
        assert result_path.exists()
        assert report_path.read_text() == result.report_md
        assert result_path.read_text() == "PASSED"
        # Failure case writes FAILED
        profile_fail = make_profile("false", None, None)
        result2 = runner.run_sync(profile_fail, task_id=43)
        assert (Path(tmp) / "43" / "toolchain_result.txt").read_text() == "FAILED"


def test_evidence_dir_created_even_if_missing():
    with tempfile.TemporaryDirectory() as tmp:
        # Use nested non-existing dir
        nested = Path(tmp) / "a" / "b" / "evidence"
        runner = ToolchainRunner(evidence_base_dir=str(nested))
        profile = make_profile("echo hi", None, None)
        result = runner.run_sync(profile, task_id=7)
        assert (nested / "7" / "toolchain_report.md").exists()


# ---------------------------------------------------------------------------
# Async run direct (not via run_sync)
# ---------------------------------------------------------------------------

def test_async_run_direct():
    async def _inner():
        profile = make_profile("echo lint", None, "echo test")
        runner = ToolchainRunner(timeout_per_command=5.0)
        result = await runner.run(profile)
        assert result.passed is True
        assert len(result.commands) == 3
    asyncio.run(_inner())


def test_profile_without_toolchain_attr():
    class FakeProfile:
        pass
    runner = ToolchainRunner(timeout_per_command=5.0)
    result = runner.run_sync(FakeProfile())  # type: ignore
    assert result.passed is True
    # Should treat as generic → all skipped
    for c in result.commands:
        assert c.skipped is True


# ---------------------------------------------------------------------------
# Daemon fail-fast integration
# ---------------------------------------------------------------------------

def test_daemon_fail_fast_bypasses_qa_on_toolchain_failure():
    # Mock state, qa, executor to test _execute_and_qa integration
    import daemon
    from unittest.mock import MagicMock, AsyncMock

    # Create a failing toolchain profile
    profile = make_profile("false", None, None)

    # Mock state
    mock_state = MagicMock()
    mock_state.set_qa_feedback = MagicMock()
    mock_state.update_state = MagicMock()

    # Mock QA that should NOT be called on failure
    mock_qa = MagicMock()
    mock_qa.config = MagicMock()
    mock_qa.config.evidence_dir = tempfile.mkdtemp()
    mock_qa.evidence_dir = Path(mock_qa.config.evidence_dir)
    mock_qa.run_qa = MagicMock(return_value={"result": "PASSED", "report": "QA_PASSED"})

    # Mock executor returning complete with dummy diff file
    mock_executor = MagicMock()
    async def fake_execute(*args, **kwargs):
        return {"status": "complete"}
    mock_executor.execute = fake_execute

    # Create temp task file with diff markers
    with tempfile.TemporaryDirectory() as tmp:
        task_file = Path(tmp) / "task.md"
        task_file.write_text("content\n<!-- BEGIN_GIT_DIFF -->\ndiff content\n<!-- END_GIT_DIFF -->", encoding="utf-8")
        # Need to monkeypatch daemon.ToolchainRunner to use our failing profile? Instead directly test via daemon._execute_and_qa with stack_profile
        async def run_test():
            result = await daemon._execute_and_qa(
                task_id=99,
                task_file=str(task_file),
                task_content="task content",
                task_path=task_file,
                state=mock_state,
                executor=mock_executor,
                qa=mock_qa,
                stack_profile=profile,
            )
            return result

        result = asyncio.run(run_test())
        # Should be FAILED due to toolchain, not PASSED
        assert result is not None
        assert result["result"] == "FAILED"
        assert "toolchain" in result["report"].lower() or "FAILED" in result["report"]
        # qa.run_qa should NOT have been called
        mock_qa.run_qa.assert_not_called()
        # state.set_qa_feedback should have been called with report_md
        mock_state.set_qa_feedback.assert_called_once()
        # evidence dir file should exist
        assert (Path(mock_qa.config.evidence_dir) / "99" / "toolchain_report.md").exists()


def test_daemon_success_forwards_to_qa():
    import daemon
    from unittest.mock import MagicMock

    profile = make_profile("echo lint", "echo build", "echo test")
    mock_state = MagicMock()
    mock_state.set_qa_feedback = MagicMock()
    mock_state.update_state = MagicMock()
    mock_qa = MagicMock()
    mock_qa.config = MagicMock()
    mock_qa.config.evidence_dir = tempfile.mkdtemp()
    mock_qa.evidence_dir = Path(mock_qa.config.evidence_dir)
    # Capture toolchain_evidence param
    captured = {}
    def fake_run_qa(task_id, task_content, diff, toolchain_evidence=""):
        captured["toolchain_evidence"] = toolchain_evidence
        return {"result": "PASSED", "report": "QA_PASSED", "evidence_dir": str(mock_qa.evidence_dir / str(task_id))}
    mock_qa.run_qa = fake_run_qa

    mock_executor = MagicMock()
    async def fake_execute(*args, **kwargs):
        return {"status": "complete"}
    mock_executor.execute = fake_execute

    with tempfile.TemporaryDirectory() as tmp:
        task_file = Path(tmp) / "task.md"
        task_file.write_text("x\n<!-- BEGIN_GIT_DIFF -->\ndiff\n<!-- END_GIT_DIFF -->", encoding="utf-8")
        async def run_test():
            return await daemon._execute_and_qa(
                task_id=100,
                task_file=str(task_file),
                task_content="task",
                task_path=task_file,
                state=mock_state,
                executor=mock_executor,
                qa=mock_qa,
                stack_profile=profile,
            )
        result = asyncio.run(run_test())
        assert result["result"] == "PASSED"
        # toolchain_evidence should have been forwarded
        assert "toolchain" in captured["toolchain_evidence"].lower() or "PASSED" in captured["toolchain_evidence"]
        # set_qa_feedback should NOT be called on success
        mock_state.set_qa_feedback.assert_not_called()


def test_daemon_generic_skips_and_passes_to_qa():
    import daemon
    from unittest.mock import MagicMock
    cfg = StackProfileConfig(name="generic", display_name="Generic")
    profile = StackProfile(cfg)
    mock_state = MagicMock()
    mock_state.set_qa_feedback = MagicMock()
    mock_state.update_state = MagicMock()
    mock_qa = MagicMock()
    mock_qa.config = MagicMock()
    mock_qa.config.evidence_dir = tempfile.mkdtemp()
    mock_qa.evidence_dir = Path(mock_qa.config.evidence_dir)
    mock_qa.run_qa = MagicMock(return_value={"result": "PASSED", "report": "QA_PASSED", "evidence_dir": "ev"})
    mock_executor = MagicMock()
    async def fake_execute(*args, **kwargs):
        return {"status": "complete"}
    mock_executor.execute = fake_execute
    with tempfile.TemporaryDirectory() as tmp:
        task_file = Path(tmp) / "t.md"
        task_file.write_text("c\n<!-- BEGIN_GIT_DIFF -->\ndiff\n<!-- END_GIT_DIFF -->")
        async def run_test():
            return await daemon._execute_and_qa(101, str(task_file), "c", task_file, mock_state, mock_executor, mock_qa, stack_profile=profile)
        result = asyncio.run(run_test())
        assert result["result"] == "PASSED"
        mock_qa.run_qa.assert_called_once()


def test_router_includes_toolchain_evidence():
    from models import LoopEngineConfig
    from router import LLMRouter
    cfg = LoopEngineConfig(approval={"chat_id": 0})
    router = LLMRouter(cfg, workspace_root=".")
    routing = router.route_qa("task content", "diff content", toolchain_evidence="Toolchain PASSED | lint: SKIPPED")
    assert "Toolchain PASSED" in routing["user"]
    assert "diff content" in routing["user"]
    # Without evidence, not included
    routing2 = router.route_qa("task", "diff")
    assert "Toolchain" not in routing2["user"]


def test_qa_engine_forwards_toolchain_evidence():
    from models import LoopEngineConfig
    from state import StateMachine
    from router import LLMRouter
    from qa_engine import QAEngine
    cfg = LoopEngineConfig(approval={"chat_id": 0}, evidence_dir=tempfile.mkdtemp())
    state = StateMachine(db_path=os.path.join(tempfile.mkdtemp(), "db"))
    router = LLMRouter(cfg, workspace_root=".")

    # Patch router.call_llm to capture routing and return PASSED
    captured = {}
    orig_call = router.call_llm
    def fake_call(routing):
        captured["user"] = routing["user"]
        return "QA_PASSED everything ok"
    router.call_llm = fake_call

    qa = QAEngine(cfg, state, router)
    result = qa.run_qa(1, "task", "diff", toolchain_evidence="Toolchain PASSED | lint: PASSED")
    assert result["result"] == "PASSED"
    assert "Toolchain PASSED" in captured["user"]
    # Also test empty evidence still works
    result2 = qa.run_qa(2, "task", "diff")
    assert result2["result"] == "PASSED"
    router.call_llm = orig_call
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
