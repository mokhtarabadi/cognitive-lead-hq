"""Tests for executor.py — Goal Plugin delegation with transport retry."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from executor import TERM_COMPLETE, TERM_BLOCKED, TRANSPORT_ERROR, MAX_RETRIES, RETRY_DELAY
from models import LoopEngineConfig


def _cfg():
    return LoopEngineConfig(approval={"chat_id": 123})


def test_terminal_complete():
    assert TERM_COMPLETE.search("Done! [goal:complete]") is not None
    assert TERM_COMPLETE.search("No marker") is None


def test_terminal_blocked():
    assert TERM_BLOCKED.search("Cannot proceed [goal:blocked]") is not None
    assert TERM_BLOCKED.search("No marker") is None


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
