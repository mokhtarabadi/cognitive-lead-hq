"""Unit tests for Metrics, JSON logging, Sentry (Task 146)."""
import json
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from metrics import JSONLogFormatter, MetricsCollector, init_sentry


def test_token_tracking_and_cost():
    m = MetricsCollector()
    m.record_llm_call(1, "gpt", prompt_tokens=1000, completion_tokens=1000, duration_seconds=1.0)
    got = m.get_task_metrics(1)
    assert got["prompt_tokens"] == 1000
    assert got["completion_tokens"] == 1000
    # 1k prompt @0.0015 + 1k completion @0.002 = 0.0035
    assert abs(got["estimated_cost"] - 0.0035) < 1e-9


def test_stage_latency_and_error_tracking():
    m = MetricsCollector()
    m.record_stage_duration(2, "plan", 1.5)
    m.record_error(2, "qa", "boom")
    got = m.get_task_metrics(2)
    assert got["stages"]["plan"] == 1.5
    assert got["errors"] == [{"stage": "qa", "error": "boom"}]
    summary = m.get_summary()
    assert summary["total_tasks"] == 1
    assert summary["total_errors"] == 1


def test_json_log_formatting():
    fmt = JSONLogFormatter()
    rec = logging.LogRecord("test", logging.INFO, __file__, 10, "hello", None, None)
    rec.task_id = 9
    rec.duration_ms = 12
    out = fmt.format(rec)
    data = json.loads(out)
    assert data["level"] == "INFO"
    assert data["logger"] == "test"
    assert data["event"] == "hello"
    assert data["task_id"] == 9
    assert data["duration_ms"] == 12
    assert "timestamp" in data


def test_sentry_noop_when_unconfigured():
    assert init_sentry(None) is False
    assert init_sentry("") is False
