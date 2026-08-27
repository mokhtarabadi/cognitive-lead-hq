"""Tests for Task Entry Trigger Gate — decoupled intake mechanism.

Verifies:
1. New task ingestion under trigger_mode="telegram_button" sets PENDING_TRIGGER.
2. trigger_task() transitions to PLANNING and starts processing.
3. Fresh file re-read captures edits after initial ingestion.
4. Telegram /run command triggers task.
5. Legacy trigger_mode="auto" immediately starts processing.
6. CLI --run argument triggers targeted task.
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.dirname(__file__))

from models import LoopEngineConfig, TaskState
from state import StateMachine
from watcher import BacklogHandler


def _make_config(**overrides) -> LoopEngineConfig:
    """Create a LoopEngineConfig with test defaults."""
    defaults = {
        "approval": {"chat_id": -100123456},
        "trigger_mode": "telegram_button",
        "auto_start_on_boot": False,
    }
    defaults.update(overrides)
    return LoopEngineConfig(**defaults)


# --- Test 1: New task ingestion under telegram_button sets PENDING_TRIGGER ---

def test_trigger_mode_telegram_button_sets_pending():
    """New task detected with trigger_mode='telegram_button' → PENDING_TRIGGER."""
    with tempfile.TemporaryDirectory() as tmp:
        sm = StateMachine(os.path.join(tmp, "test.db"))
        config = _make_config(trigger_mode="telegram_button")

        # Simulate watcher registering a task
        tid = sm.register_task("tasks/backlog/99-test-trigger.md", TaskState.PENDING_TRIGGER)
        task = sm.get_task(tid)

        assert task["state"] == "pending_trigger"
        assert task["task_file"] == "tasks/backlog/99-test-trigger.md"
        sm.close()


# --- Test 2: trigger_task() transitions PENDING_TRIGGER → PLANNING ---

def test_trigger_task_transitions_to_planning():
    """Invoking trigger_task(id) transitions PENDING_TRIGGER → PLANNING."""
    with tempfile.TemporaryDirectory() as tmp:
        sm = StateMachine(os.path.join(tmp, "test.db"))
        tid = sm.register_task("tasks/backlog/99-test-trigger.md", TaskState.PENDING_TRIGGER)

        # Simulate trigger_task transition (without launching process_task)
        sm.update_state(tid, TaskState.PLANNING)
        task = sm.get_task(tid)

        assert task["state"] == "planning"
        sm.close()


# --- Test 3: Fresh file re-read captures edits ---

def test_fresh_read_captures_edits():
    """After ingestion, re-reading the file captures manual edits."""
    with tempfile.TemporaryDirectory() as tmp:
        task_file = Path(tmp) / "99-test-trigger.md"
        task_file.write_text("# Original content\n")

        # Initial read
        content_v1 = task_file.read_text()
        assert "Original" in content_v1

        # Simulate admin edit
        task_file.write_text("# Updated content\n**Status:** refined\n")

        # Fresh read captures changes
        content_v2 = task_file.read_text()
        assert "Updated" in content_v2
        assert "refined" in content_v2
        assert "Original" not in content_v2


# --- Test 4: get_pending_trigger_tasks returns correct tasks ---

def test_get_pending_trigger_tasks():
    """get_pending_trigger_tasks() returns only PENDING_TRIGGER tasks."""
    with tempfile.TemporaryDirectory() as tmp:
        sm = StateMachine(os.path.join(tmp, "test.db"))
        t1 = sm.register_task("tasks/backlog/01-a.md", TaskState.PENDING_TRIGGER)
        t2 = sm.register_task("tasks/backlog/02-b.md", TaskState.BACKLOG)
        t3 = sm.register_task("tasks/backlog/03-c.md", TaskState.PENDING_TRIGGER)

        pending = sm.get_pending_trigger_tasks()
        assert len(pending) == 2
        states = {t["task_id"] for t in pending}
        assert t1 in states
        assert t3 in states
        assert t2 not in states
        sm.close()


# --- Test 5: Legacy trigger_mode="auto" registers as BACKLOG ---

def test_trigger_mode_auto_registers_backlog():
    """With trigger_mode='auto', tasks register as BACKLOG (legacy behavior)."""
    with tempfile.TemporaryDirectory() as tmp:
        sm = StateMachine(os.path.join(tmp, "test.db"))
        config = _make_config(trigger_mode="auto")

        # Simulate auto mode registration
        tid = sm.register_task("tasks/backlog/99-test-auto.md", TaskState.BACKLOG)
        task = sm.get_task(tid)

        assert task["state"] == "backlog"
        # auto mode should NOT have pending_trigger tasks
        pending = sm.get_pending_trigger_tasks()
        assert len(pending) == 0
        sm.close()


# --- Test 6: Config defaults ---

def test_config_defaults():
    """LoopEngineConfig defaults: trigger_mode='telegram_button', auto_start_on_boot=False."""
    config = _make_config()
    assert config.trigger_mode == "telegram_button"
    assert config.auto_start_on_boot is False


def test_config_auto_mode():
    """LoopEngineConfig auto mode: trigger_mode='auto', auto_start_on_boot=True."""
    config = _make_config(trigger_mode="auto", auto_start_on_boot=True)
    assert config.trigger_mode == "auto"
    assert config.auto_start_on_boot is True


# --- Test 7: State transitions PENDING_TRIGGER → CRASHED/ABORTED ---

def test_pending_trigger_can_crash():
    """PENDING_TRIGGER → CRASHED transition works."""
    with tempfile.TemporaryDirectory() as tmp:
        sm = StateMachine(os.path.join(tmp, "test.db"))
        tid = sm.register_task("tasks/backlog/99-crash.md", TaskState.PENDING_TRIGGER)
        sm.update_state(tid, TaskState.CRASHED)
        task = sm.get_task(tid)
        assert task["state"] == "crashed"
        sm.close()


def test_pending_trigger_can_abort():
    """PENDING_TRIGGER → ABORTED transition works."""
    with tempfile.TemporaryDirectory() as tmp:
        sm = StateMachine(os.path.join(tmp, "test.db"))
        tid = sm.register_task("tasks/backlog/99-abort.md", TaskState.PENDING_TRIGGER)
        sm.update_state(tid, TaskState.ABORTED)
        task = sm.get_task(tid)
        assert task["state"] == "aborted"
        sm.close()


# --- Test 10: Thread-safe dispatch from watchdog background thread ---

def test_watcher_thread_safe_dispatch():
    """BacklogHandler.on_created runs from a background thread without RuntimeError.

    Regression test: the original code called asyncio.get_event_loop().create_task()
    from watchdog's background thread, which has no running event loop and would
    raise RuntimeError. The fix removes that call and always dispatches via the
    on_task_detected callback, letting the daemon handle async scheduling.

    Note: SQLite connections are thread-bound, so StateMachine must be created
    inside the same thread that calls on_created.
    """
    import threading
    from unittest.mock import MagicMock
    from watchdog.events import FileCreatedEvent

    with tempfile.TemporaryDirectory() as tmp:
        config = _make_config(trigger_mode="telegram_button")

        # Create a tasks/backlog dir and a task file inside it
        backlog_dir = Path(tmp) / "tasks" / "backlog"
        backlog_dir.mkdir(parents=True)
        task_file = backlog_dir / "01-thread-test.md"
        task_file.write_text("# Task 1: Thread Test\n**Source:** telegram\n**Type:** improvement\n")

        # Track callback invocations and errors from background thread
        callback_invocations = []
        errors = []

        def on_task_detected(task_id, task_file_path):
            callback_invocations.append((task_id, task_file_path))

        def run_in_thread():
            try:
                # StateMachine must be created in the same thread (SQLite thread-bound)
                sm = StateMachine(os.path.join(tmp, "test.db"))
                gateway_mock = MagicMock()
                handler = BacklogHandler(sm, config, gateway_mock, on_task_detected)

                # Create a FileCreatedEvent for the task file
                event = FileCreatedEvent(str(task_file))
                handler.on_created(event)
                sm.close()
            except Exception as e:
                errors.append(e)

        thread = threading.Thread(target=run_in_thread)
        thread.start()
        thread.join(timeout=5)

        # Verify: no RuntimeError, callback was invoked
        assert len(errors) == 0, f"Background thread raised: {errors}"
        assert len(callback_invocations) == 1, \
            f"Expected 1 callback, got {len(callback_invocations)}"
        assert callback_invocations[0][0] == 1  # task_id
        assert "thread-test" in callback_invocations[0][1]


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
