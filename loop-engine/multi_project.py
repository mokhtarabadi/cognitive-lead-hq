"""
Multi-Project Router (Task 143).

Maps Telegram forum topic IDs to isolated project workspaces.
Single supergroup manages multiple distinct repositories via topic threads.
"""

from __future__ import annotations

from pathlib import Path


class MultiProjectRouter:
    """Routes topic IDs <-> workspace roots <-> task paths."""

    def __init__(self, mappings) -> None:
        self._mappings = list(mappings or [])
        self._by_topic: dict[int, object] = {m.topic_id: m for m in self._mappings}

    def get_workspace_for_topic(self, topic_id: int) -> Path | None:
        m = self._by_topic.get(int(topic_id))
        if m is None:
            return None
        return Path(m.workspace_root)

    def get_topic_for_workspace(self, workspace_path: str | Path) -> int | None:
        target = str(workspace_path)
        for m in self._mappings:
            if str(m.workspace_root) == target:
                return int(m.topic_id)
            # Allow relative/absolute equivalence via normalized suffix match
            try:
                if Path(target).resolve() == Path(m.workspace_root).resolve():
                    return int(m.topic_id)
            except Exception:
                continue
        return None

    def get_topic_for_task(self, task_file: str | Path) -> int | None:
        task_str = str(task_file)
        best: tuple[int, int] | None = None  # (match_len, topic_id)
        for m in self._mappings:
            root = str(m.workspace_root)
            if root and root in task_str:
                cand = (len(root), int(m.topic_id))
                if best is None or cand[0] > best[0]:
                    best = cand
        if best is not None:
            return best[1]
        return None

    def get_project_name(self, topic_id: int) -> str | None:
        m = self._by_topic.get(int(topic_id))
        return m.project_name if m is not None else None
