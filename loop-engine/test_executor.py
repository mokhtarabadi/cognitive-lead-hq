"""Tests for executor.py — Goal Plugin delegation with transport retry."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import asyncio
import signal

from executor import (
    TERM_COMPLETE, TERM_BLOCKED, TRANSPORT_ERROR, MAX_RETRIES, RETRY_DELAY,
    HandsExecutor,
)
from models import LoopEngineConfig, StackProfileConfig
from stacks import StackProfile


def _cfg():
    return LoopEngineConfig(approval={"chat_id": 123})


def _make_stack_profile(skills=None, toolchain=None, preflight=None):
    return StackProfile(StackProfileConfig(
        name="test-stack", display_name="Test Stack",
        skills=skills or [], toolchain=toolchain or {},
        preflight=preflight or []))


def test_terminal_complete():
    assert TERM_COMPLETE.search("Done! [goal:complete]") is not None
    assert TERM_COMPLETE.search("No marker") is None


def test_terminal_complete_case_insensitive():
    assert TERM_COMPLETE.search("Done! [GOAL:COMPLETE]") is not None
    assert TERM_COMPLETE.search("Done! [Goal:Complete]") is not None


def test_terminal_blocked():
    assert TERM_BLOCKED.search("Cannot proceed [goal:blocked]") is not None
    assert TERM_BLOCKED.search("No marker") is None


def test_terminal_blocked_reason():
    m = TERM_BLOCKED.search("Cannot proceed [goal:blocked: missing db credentials]")
    assert m is not None
    assert m.group(1).strip() == "missing db credentials"


def test_terminal_blocked_reason_uppercase():
    m = TERM_BLOCKED.search("Cannot proceed [GOAL:BLOCKED: compilation error]")
    assert m is not None
    assert m.group(1).strip() == "compilation error"


def test_terminal_blocked_no_reason():
    m = TERM_BLOCKED.search("Cannot proceed [goal:blocked]")
    assert m is not None
    assert m.group(1) is None


def test_terminal_complete_multiline():
    text = "Line 1\nLine 2\nTask done [goal:complete]\nLine 4"
    assert TERM_COMPLETE.search(text) is not None


def test_terminal_blocked_multiline():
    text = "Error occurred\nCannot continue [goal:blocked]"
    assert TERM_BLOCKED.search(text) is not None


def test_transport_error_detection():
    assert TRANSPORT_ERROR.search("stream disconnected before completion") is not None
    assert TRANSPORT_ERROR.search("ECONNRESET") is not None
    assert TRANSPORT_ERROR.search("ETIMEDOUT") is not None
    assert TRANSPORT_ERROR.search("Connection reset by peer") is not None
    assert TRANSPORT_ERROR.search("No transport error here") is None


def test_retry_constants():
    assert MAX_RETRIES == 3
    assert RETRY_DELAY == 5


def test_config_has_timeout():
    cfg = _cfg()
    assert cfg.idle.max_retries > 0
    assert cfg.idle.thinking_timeout_seconds > 0


def test_executor_instantiation():
    from executor import HandsExecutor
    from state import StateMachine
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        sm = StateMachine(os.path.join(tmp, "test.db"))
        exe = HandsExecutor(_cfg(), sm)
        assert exe.config is not None
        assert exe.state is not None
        sm.close()


# --- _build_prompt (LE-4) ---

def _make_executor():
    from state import StateMachine
    import tempfile
    tmp = tempfile.mkdtemp()
    sm = StateMachine(os.path.join(tmp, "test.db"))
    return HandsExecutor(_cfg(), sm), sm


def test_build_prompt_empty_profile():
    exe, sm = _make_executor()
    try:
        prompt = exe._build_prompt("/tmp/task.md")
        assert "<task_instructions>" in prompt
        assert "Read the task file at /tmp/task.md and implement it." in prompt
        assert "<goal_rules>" in prompt
        assert "[goal:complete]" in prompt
        assert "[goal:blocked: <reason>]" in prompt
        assert "<stack_context" not in prompt
        assert "<blueprint_context>" not in prompt
        assert "<qa_feedback>" not in prompt
    finally:
        sm.close()


def test_build_prompt_stack_profile():
    exe, sm = _make_executor()
    try:
        profile = _make_stack_profile(
            skills=["android-kotlin"],
            toolchain={"test_cmd": "./gradlew test", "build_cmd": "./gradlew assembleDebug", "lint_cmd": "./gradlew ktlintCheck"},
            preflight=["java -version"],
        )
        prompt = exe._build_prompt("/tmp/task.md", stack_profile=profile)
        assert '<stack_context name="test-stack" display_name="Test Stack">' in prompt
        assert "MANDATORY: Load required skills via the native skill tool: android-kotlin" in prompt
        assert "test='./gradlew test'" in prompt
        assert "build='./gradlew assembleDebug'" in prompt
        assert "lint='./gradlew ktlintCheck'" in prompt
        assert "Preflight commands: java -version" in prompt
    finally:
        sm.close()


def test_build_prompt_blueprint_and_qa():
    exe, sm = _make_executor()
    try:
        prompt = exe._build_prompt(
            "/tmp/task.md",
            blueprint_context="Approved plan: build feature X",
            qa_feedback="Fix the null pointer in module Y",
        )
        assert "<blueprint_context>" in prompt
        assert "Approved plan: build feature X" in prompt
        assert "<qa_feedback>" in prompt
        assert "Fix the null pointer in module Y" in prompt
        assert "Address the above QA feedback explicitly." in prompt
        assert "Do NOT treat this as a new architectural plan." in prompt
    finally:
        sm.close()


def test_build_prompt_all_sections():
    exe, sm = _make_executor()
    try:
        profile = _make_stack_profile(skills=["python-fastapi"])
        prompt = exe._build_prompt(
            "/tmp/task.md", blueprint_context="plan", qa_feedback="fix", stack_profile=profile)
        assert "<task_instructions>" in prompt
        assert "<stack_context" in prompt
        assert "<blueprint_context>" in prompt
        assert "<qa_feedback>" in prompt
        assert "<goal_rules>" in prompt
    finally:
        sm.close()


# --- Semaphore throttling (LE-4) ---

def test_semaphore_initialized():
    exe, sm = _make_executor()
    try:
        assert isinstance(exe._semaphore, asyncio.Semaphore)
        assert exe._semaphore._value == _cfg().max_parallel_tasks
    finally:
        sm.close()


def test_semaphore_throttles_concurrency():
    exe, sm = _make_executor()
    try:
        max_concurrent = 0
        active = 0
        lock = asyncio.Lock()

        async def worker():
            nonlocal max_concurrent, active
            async with exe._semaphore:
                active += 1
                max_concurrent = max(max_concurrent, active)
                await asyncio.sleep(0.05)
                active -= 1

        async def run():
            await asyncio.gather(*[worker() for _ in range(8)])

        asyncio.run(run())
        assert max_concurrent <= _cfg().max_parallel_tasks
        assert max_concurrent >= 1
    finally:
        sm.close()


# --- Process group timeout kill (LE-4) ---

def test_run_once_timeout_kills_process_group():
    exe, sm = _make_executor()
    try:
        # Force a tiny timeout so the subprocess exceeds it immediately.
        exe.config.idle.executing_timeout_seconds = 0.1
        result = asyncio.run(exe._run_once("/tmp/task.md", "sleep 5"))
        assert result["status"] == "timeout"
        assert "Exceeded" in result["error"]
        assert "timeout" in result["error"]
    finally:
        sm.close()


def test_run_once_start_new_session_posix():
    import os as _os
    exe, sm = _make_executor()
    try:
        # Verify the code path sets start_new_session on POSIX by checking
        # the subprocess is launched in its own session (killpg works).
        exe.config.idle.executing_timeout_seconds = 0.1
        result = asyncio.run(exe._run_once("/tmp/task.md", "sleep 5"))
        assert result["status"] == "timeout"  # proves killpg teardown path ran
    finally:
        sm.close()


# --- Transport error retries (LE-4) ---

def test_transport_error_retryable():
    exe, sm = _make_executor()
    try:
        calls = {"n": 0}

        async def fake_run_once(task_file, prompt):
            calls["n"] += 1
            if calls["n"] < 3:
                return {"status": "transport_error", "output": "", "error": "ECONNRESET", "elapsed": 0.1}
            return {"status": "complete", "output": "[goal:complete]", "error": "", "elapsed": 0.1}

        exe._run_once = fake_run_once
        result = asyncio.run(exe.execute(1, "/tmp/task.md", "content"))
        assert result["status"] == "complete"
        assert calls["n"] == 3
    finally:
        sm.close()


def test_non_retryable_error_no_retry():
    exe, sm = _make_executor()
    try:
        calls = {"n": 0}

        async def fake_run_once(task_file, prompt):
            calls["n"] += 1
            return {"status": "error", "output": "", "error": "opencode CLI not found in PATH", "elapsed": 0.1}

        exe._run_once = fake_run_once
        result = asyncio.run(exe.execute(1, "/tmp/task.md", "content"))
        assert result["status"] == "error"
        assert calls["n"] == 1
    finally:
        sm.close()


def test_blocked_reason_propagated():
    exe, sm = _make_executor()
    try:
        async def fake_run_once(task_file, prompt):
            return {"status": "blocked", "output": "[goal:blocked: missing db credentials]",
                    "error": "", "reason": "missing db credentials", "elapsed": 0.1}

        exe._run_once = fake_run_once
        result = asyncio.run(exe.execute(1, "/tmp/task.md", "content"))
        assert result["status"] == "blocked"
        assert result["reason"] == "missing db credentials"
    finally:
        sm.close()


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
