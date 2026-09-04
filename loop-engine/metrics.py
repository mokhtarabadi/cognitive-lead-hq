"""
Structured Metrics, Token Cost Tracking & Error Logging (Task 146).
"""

from __future__ import annotations

import json
import logging
import time
from typing import Optional


PROMPT_COST_PER_1K = 0.0015
COMPLETION_COST_PER_1K = 0.002


class MetricsCollector:
    """In-memory per-task metrics with global summary."""

    def __init__(self) -> None:
        self._tasks: dict[int, dict] = {}

    def _ensure(self, task_id: int) -> dict:
        entry = self._tasks.get(int(task_id))
        if entry is None:
            entry = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "estimated_cost": 0.0,
                "stages": {},
                "errors": [],
                "llm_calls": 0,
            }
            self._tasks[int(task_id)] = entry
        return entry

    def record_llm_call(self, task_id: int, model: str, prompt_tokens: int,
                        completion_tokens: int, duration_seconds: float) -> None:
        entry = self._ensure(task_id)
        entry["prompt_tokens"] += int(prompt_tokens)
        entry["completion_tokens"] += int(completion_tokens)
        entry["llm_calls"] += 1
        cost = (int(prompt_tokens) / 1000.0) * PROMPT_COST_PER_1K + \
               (int(completion_tokens) / 1000.0) * COMPLETION_COST_PER_1K
        entry["estimated_cost"] += cost
        entry.setdefault("models", {})
        entry["models"][model] = entry["models"].get(model, 0) + 1
        entry["last_duration_seconds"] = float(duration_seconds)

    def record_stage_duration(self, task_id: int, stage: str, duration_seconds: float) -> None:
        entry = self._ensure(task_id)
        entry["stages"][str(stage)] = float(duration_seconds)

    def record_error(self, task_id: int, stage: str, error: str) -> None:
        entry = self._ensure(task_id)
        entry["errors"].append({"stage": str(stage), "error": str(error)})

    def get_task_metrics(self, task_id: int) -> dict:
        entry = self._ensure(task_id)
        return dict(entry)

    def get_summary(self) -> dict:
        total_tasks = len(self._tasks)
        total_prompt = sum(v["prompt_tokens"] for v in self._tasks.values())
        total_completion = sum(v["completion_tokens"] for v in self._tasks.values())
        total_cost = sum(v["estimated_cost"] for v in self._tasks.values())
        total_errors = sum(len(v["errors"]) for v in self._tasks.values())
        return {
            "total_tasks": total_tasks,
            "total_prompt_tokens": total_prompt,
            "total_completion_tokens": total_completion,
            "total_estimated_cost": total_cost,
            "total_errors": total_errors,
        }


class JSONLogFormatter(logging.Formatter):
    """Emits structured JSON log lines."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
            "task_id": getattr(record, "task_id", None),
            "duration_ms": getattr(record, "duration_ms", None),
        }
        return json.dumps(payload)


def init_sentry(sentry_dsn: Optional[str]) -> bool:
    """Gracefully init Sentry if installed and DSN provided."""
    if not sentry_dsn:
        return False
    try:
        import sentry_sdk  # type: ignore
    except ImportError:
        return False
    try:
        sentry_sdk.init(dsn=sentry_dsn)
        return True
    except Exception:
        return False
