"""Tests for state.py — SQLite state machine."""
import sys, os, tempfile
sys.path.insert(0, os.path.dirname(__file__))

from state import StateMachine
from models import TaskState


def test_register_task():
    with tempfile.TemporaryDirectory() as tmp:
        sm = StateMachine(os.path.join(tmp, "test.db"))
        tid = sm.register_task("tasks/backlog/01-test.md", TaskState.BACKLOG)
        assert tid is not None
        task = sm.get_task(tid)
        assert task["state"] == "backlog"
        assert task["task_file"] == "tasks/backlog/01-test.md"
        sm.close()


def test_get_task_by_file():
    with tempfile.TemporaryDirectory() as tmp:
        sm = StateMachine(os.path.join(tmp, "test.db"))
        sm.register_task("tasks/backlog/02-feature.md")
        task = sm.get_task_by_file("tasks/backlog/02-feature.md")
        assert task is not None
        assert task["task_id"] > 0
        sm.close()


def test_update_state():
    with tempfile.TemporaryDirectory() as tmp:
        sm = StateMachine(os.path.join(tmp, "test.db"))
        tid = sm.register_task("tasks/backlog/03-test.md")
        sm.update_state(tid, TaskState.PLANNING)
        task = sm.get_task(tid)
        assert task["state"] == "planning"
        sm.update_state(tid, TaskState.IMPLEMENTING)
        task = sm.get_task(tid)
        assert task["state"] == "implementing"
        sm.close()


def test_set_plan():
    with tempfile.TemporaryDirectory() as tmp:
        sm = StateMachine(os.path.join(tmp, "test.db"))
        tid = sm.register_task("tasks/backlog/04-test.md")
        sm.set_plan(tid, "## Plan\n1. Do stuff")
        task = sm.get_task(tid)
        assert task["plan"] == "## Plan\n1. Do stuff"
        sm.close()


def test_qa_feedback_and_retry():
    with tempfile.TemporaryDirectory() as tmp:
        sm = StateMachine(os.path.join(tmp, "test.db"))
        tid = sm.register_task("tasks/backlog/05-test.md")
        sm.set_qa_feedback(tid, "Fix the bug on line 42")
        task = sm.get_task(tid)
        assert task["qa_retry_count"] == 1
        assert task["qa_feedback"] == "Fix the bug on line 42"
        count = sm.increment_qa_retry(tid)
        assert count == 2
        sm.close()


def test_closed_at_timestamp():
    with tempfile.TemporaryDirectory() as tmp:
        sm = StateMachine(os.path.join(tmp, "test.db"))
        tid = sm.register_task("tasks/backlog/06-test.md")
        sm.update_state(tid, TaskState.CLOSED)
        task = sm.get_task(tid)
        assert task["closed_at"] is not None
        assert task["closed_at"] > 0
        sm.close()


def test_get_active_tasks():
    with tempfile.TemporaryDirectory() as tmp:
        sm = StateMachine(os.path.join(tmp, "test.db"))
        sm.register_task("tasks/backlog/07a.md")
        tid2 = sm.register_task("tasks/backlog/07b.md")
        sm.update_state(tid2, TaskState.IMPLEMENTING)
        active = sm.get_active_tasks()
        assert len(active) == 1
        assert active[0]["task_file"] == "tasks/backlog/07b.md"
        sm.close()


def test_get_tasks_in_state():
    with tempfile.TemporaryDirectory() as tmp:
        sm = StateMachine(os.path.join(tmp, "test.db"))
        t1 = sm.register_task("tasks/backlog/08a.md")
        t2 = sm.register_task("tasks/backlog/08b.md")
        sm.update_state(t1, TaskState.QA)
        sm.update_state(t2, TaskState.QA)
        qa_tasks = sm.get_tasks_in_state(TaskState.QA)
        assert len(qa_tasks) == 2
        sm.close()


def test_todos():
    with tempfile.TemporaryDirectory() as tmp:
        sm = StateMachine(os.path.join(tmp, "test.db"))
        tid = sm.register_task("tasks/backlog/09-test.md")
        todo_id = sm.add_todo(tid, "Write tests")
        assert todo_id > 0
        pending = sm.get_pending_todos(tid)
        assert len(pending) == 1
        sm.update_todo_status(todo_id, "done")
        pending = sm.get_pending_todos(tid)
        assert len(pending) == 0
        sm.close()


def test_register_task_idempotent():
    with tempfile.TemporaryDirectory() as tmp:
        sm = StateMachine(os.path.join(tmp, "test.db"))
        t1 = sm.register_task("tasks/backlog/10-test.md")
        t2 = sm.register_task("tasks/backlog/10-test.md")
        assert t1 == t2  # same file = same task
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
