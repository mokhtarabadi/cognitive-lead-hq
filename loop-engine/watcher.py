"""
Kanban Watcher — detects new task files in tasks/backlog/.

Uses Python watchdog filesystem observer.
Read-only: never modifies task files.
Triggers the pipeline by registering the task in StateMachine.

Respects trigger_mode from LoopEngineConfig:
- "auto": legacy behavior — immediately invokes on_task_detected (starts processing).
- "telegram_button" / "command_only": registers as PENDING_TRIGGER, sends trigger card.
"""

import re
import time
from pathlib import Path
from typing import Callable, Optional

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from models import TaskState, LoopEngineConfig
from state import StateMachine


def _parse_task_metadata(file_path: str) -> Optional[dict]:
    """Extract task ID, title, source, type, status from a task file."""
    path = Path(file_path)
    if not path.suffix == ".md":
        return None

    content = path.read_text(encoding="utf-8")

    # Extract task ID from filename: 01-feature-name.md → 01
    match = re.match(r'^(\d+)-', path.stem)
    if not match:
        return None
    task_id = int(match.group(1))

    # Extract metadata headers
    metadata = {"task_id": task_id, "file": str(path)}

    for field in ["Source", "Type", "Status"]:
        m = re.search(rf'\*\*{field}:\*\*\s*(.+)', content)
        if m:
            metadata[field.lower()] = m.group(1).strip()

    return metadata


class BacklogHandler(FileSystemEventHandler):
    """Watches for new .md files in tasks/backlog/."""

    def __init__(self, state: StateMachine, config: LoopEngineConfig,
                 gateway=None, on_task_detected: Optional[Callable] = None):
        self.state = state
        self.config = config
        self.gateway = gateway
        self.on_task_detected = on_task_detected

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path

        # Only watch .md files in tasks/backlog/
        if not file_path.endswith(".md"):
            return
        if "tasks/backlog/" not in file_path:
            return

        # Ignore archive, loop-engine, .git
        for ignore in ["archive", "loop-engine", ".git"]:
            if ignore in file_path:
                return

        # Parse metadata
        meta = _parse_task_metadata(file_path)
        if not meta:
            return

        # Register in state machine
        task_record = self.state.get_task_by_file(file_path)
        if not task_record:
            initial_state = (TaskState.BACKLOG if self.config.trigger_mode == "auto"
                             else TaskState.PENDING_TRIGGER)
            task_id = self.state.register_task(file_path, initial_state)
            print(f"[watcher] New task detected ({initial_state.value}): "
                  f"{file_path} (ID: {task_id})")

            # Always dispatch via callback — the daemon handles async scheduling
            # on the main event loop. Never call asyncio from this background thread.
            if self.on_task_detected:
                self.on_task_detected(task_id, file_path)


class KanbanWatcher:
    """Filesystem observer for tasks/backlog/."""

    def __init__(self, state: StateMachine, config: LoopEngineConfig,
                 gateway=None, tasks_dir: str = "tasks",
                 on_task_detected: Optional[Callable] = None):
        self.state = state
        self.config = config
        self.gateway = gateway
        self.tasks_dir = Path(tasks_dir)
        self.backlog_dir = self.tasks_dir / "backlog"
        self.observer = Observer()
        self.handler = BacklogHandler(state, config, gateway, on_task_detected)

    def start(self):
        """Start watching tasks/backlog/ for new files."""
        self.backlog_dir.mkdir(parents=True, exist_ok=True)
        self.observer.schedule(self.handler, str(self.backlog_dir), recursive=False)
        self.observer.start()
        print(f"[watcher] Watching {self.backlog_dir} for new tasks "
              f"(trigger_mode={self.config.trigger_mode})...")

    def stop(self):
        self.observer.stop()
        self.observer.join()

    def scan_existing(self) -> list[dict]:
        """Scan tasks/backlog/ for existing unregistered tasks.

        Respects trigger_mode: auto → BACKLOG, else → PENDING_TRIGGER.
        """
        detected = []
        if not self.backlog_dir.exists():
            return detected

        for md_file in sorted(self.backlog_dir.glob("*.md")):
            meta = _parse_task_metadata(str(md_file))
            if not meta:
                continue

            task_record = self.state.get_task_by_file(str(md_file))
            if not task_record:
                if self.config.trigger_mode == "auto":
                    task_id = self.state.register_task(str(md_file), TaskState.BACKLOG)
                else:
                    task_id = self.state.register_task(str(md_file), TaskState.PENDING_TRIGGER)
                detected.append({"task_id": task_id, "file": str(md_file)})
                print(f"[watcher] Existing task registered: {md_file.name} (ID: {task_id})")

        return detected
