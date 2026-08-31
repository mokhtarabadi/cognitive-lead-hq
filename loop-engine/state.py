"""
State Machine v2 — SQLite-backed task state tracking.

Inspired by OMO's Boulder/Goal state system but minimal:
- tasks table: tracks each task's pipeline position
- todos table: Todo Enforcer pattern (idle detection)
- Single source of truth: SQLite file at loop-engine/state/loop.db

Zero external dependencies — uses Python's built-in sqlite3.
"""

import json
import sqlite3
import time
from pathlib import Path
from typing import Optional

from models import TaskState


# --- Schema ---

_SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    task_id INTEGER PRIMARY KEY,
    task_file TEXT NOT NULL UNIQUE,
    state TEXT NOT NULL DEFAULT 'backlog',
    plan TEXT DEFAULT NULL,
    qa_feedback TEXT DEFAULT NULL,
    qa_retry_count INTEGER DEFAULT 0,
    evidence_dir TEXT DEFAULT NULL,
    spec_artifacts TEXT DEFAULT NULL,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL,
    closed_at REAL DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at REAL NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
);

CREATE INDEX IF NOT EXISTS idx_tasks_state ON tasks(state);
CREATE INDEX IF NOT EXISTS idx_tasks_file ON tasks(task_file);
CREATE INDEX IF NOT EXISTS idx_todos_task ON todos(task_id);
"""


class StateMachine:
    """SQLite-backed state machine for the Cognitive Loop Engine."""

    def __init__(self, db_path: str = "loop-engine/state/loop.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_SCHEMA)
        self.conn.commit()
        # Safe column migration for databases created before the spec-first gate
        # (LE-8): newer schemas already declare spec_artifacts, so the ALTER is a
        # no-op that raises sqlite3.OperationalError("duplicate column name") and
        # is deliberately swallowed. Additive + non-destructive.
        try:
            self.conn.execute("ALTER TABLE tasks ADD COLUMN spec_artifacts TEXT DEFAULT NULL")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass

    def close(self):
        self.conn.close()

    # --- Task State Operations ---

    def register_task(self, task_file: str, state: TaskState = TaskState.BACKLOG) -> int:
        """Register a new task file in the state machine."""
        now = time.time()
        cursor = self.conn.execute(
            "INSERT OR IGNORE INTO tasks (task_file, state, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (task_file, state.value, now, now)
        )
        self.conn.commit()
        return cursor.lastrowid or self.get_task_by_file(task_file)["task_id"]

    def get_task(self, task_id: int) -> Optional[dict]:
        row = self.conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
        return dict(row) if row else None

    def get_task_by_file(self, task_file: str) -> Optional[dict]:
        row = self.conn.execute("SELECT * FROM tasks WHERE task_file = ?", (task_file,)).fetchone()
        return dict(row) if row else None

    def update_state(self, task_id: int, new_state: TaskState):
        """Transition a task to a new state."""
        now = time.time()
        updates = {"state": new_state.value, "updated_at": now}
        if new_state == TaskState.CLOSED:
            updates["closed_at"] = now

        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [task_id]
        self.conn.execute(f"UPDATE tasks SET {set_clause} WHERE task_id = ?", values)
        self.conn.commit()

    def set_plan(self, task_id: int, plan: str):
        self.conn.execute("UPDATE tasks SET plan = ?, updated_at = ? WHERE task_id = ?",
                          (plan, time.time(), task_id))
        self.conn.commit()

    def set_qa_feedback(self, task_id: int, feedback: str):
        self.conn.execute(
            "UPDATE tasks SET qa_feedback = ?, qa_retry_count = qa_retry_count + 1, updated_at = ? WHERE task_id = ?",
            (feedback, time.time(), task_id))
        self.conn.commit()

    def increment_qa_retry(self, task_id: int) -> int:
        """Increment QA retry count and return new count."""
        cursor = self.conn.execute(
            "UPDATE tasks SET qa_retry_count = qa_retry_count + 1, updated_at = ? WHERE task_id = ? RETURNING qa_retry_count",
            (time.time(), task_id))
        row = cursor.fetchone()
        self.conn.commit()
        return row[0] if row else 0

    def get_qa_retry_count(self, task_id: int) -> int:
        row = self.conn.execute("SELECT qa_retry_count FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
        return row[0] if row else 0

    def set_evidence_dir(self, task_id: int, evidence_dir: str):
        self.conn.execute("UPDATE tasks SET evidence_dir = ?, updated_at = ? WHERE task_id = ?",
                          (evidence_dir, time.time(), task_id))
        self.conn.commit()

    # --- Spec-First Artifact Tracking (LE-8) ---

    def set_spec_artifacts(self, task_id: int, artifacts: list[str]):
        """Persist the verified spec artifact paths for a task as a JSON array."""
        self.conn.execute(
            "UPDATE tasks SET spec_artifacts = ?, updated_at = ? WHERE task_id = ?",
            (json.dumps(artifacts), time.time(), task_id))
        self.conn.commit()

    def get_spec_artifacts(self, task_id: int) -> list[str]:
        """Return the verified spec artifact paths for a task, or ``[]`` when unset/corrupt."""
        row = self.conn.execute(
            "SELECT spec_artifacts FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
        if not row or not row[0]:
            return []
        try:
            parsed = json.loads(str(row[0]))
        except (ValueError, TypeError):
            return []
        return parsed if isinstance(parsed, list) else []

    def get_active_tasks(self) -> list[dict]:
        """Get all tasks not in terminal states."""
        rows = self.conn.execute(
            "SELECT * FROM tasks WHERE state NOT IN ('closed', 'backlog') ORDER BY updated_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_tasks_in_state(self, state: TaskState) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM tasks WHERE state = ? ORDER BY updated_at DESC", (state.value,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_pending_trigger_tasks(self) -> list[dict]:
        """Get all tasks waiting for admin trigger (PENDING_TRIGGER status)."""
        return self.get_tasks_in_state(TaskState.PENDING_TRIGGER)

    # --- Todo Operations (Todo Enforcer) ---

    def add_todo(self, task_id: int, description: str) -> int:
        cursor = self.conn.execute(
            "INSERT INTO todos (task_id, description, created_at) VALUES (?, ?, ?)",
            (task_id, description, time.time()))
        self.conn.commit()
        return cursor.lastrowid

    def update_todo_status(self, todo_id: int, status: str):
        self.conn.execute("UPDATE todos SET status = ? WHERE id = ?", (status, todo_id))
        self.conn.commit()

    def get_pending_todos(self, task_id: int) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM todos WHERE task_id = ? AND status = 'pending' ORDER BY created_at",
            (task_id,)).fetchall()
        return [dict(r) for r in rows]
