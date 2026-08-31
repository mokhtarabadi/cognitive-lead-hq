"""Tests for the Spec-First Artifact Pipeline & State Gate (LE-8 / Task 140).

Covers:
1. ``SpecGateEngine.evaluate_requirements`` — keyword matching for architectural
   tasks vs routine/bugfix tasks (empty rules, no keyword hits).
2. ``SpecGateEngine.validate_artifacts`` — workspace scan passes when an ADR /
   contract exists; diff-text staging passes; failing with a diagnostic report
   when a required artifact is absent; empty-rule immediate pass.
3. State machine migration — ``spec_artifacts`` column on new and pre-migration
   DBs, ``set_spec_artifacts``/``get_spec_artifacts`` round-trip, corrupt JSON
   fallback.
4. Daemon integration — spec gate crashes a task before ``IMPLEMENTING`` with
   ``qa_feedback``; passing gate proceeds and persists verified artifacts.
"""
import asyncio
import json
import os
import sqlite3
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.dirname(__file__))

from models import (
    LoopEngineConfig,
    SpecArtifactType,
    SpecGateConfig,
    SpecRequirementRule,
    TaskState,
)
from state import StateMachine

import daemon
from specs import SpecGateEngine, SpecValidationResult, _paths_in_diff


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _make_workspace(tmp_path):
    """Build a minimal workspace with tasks/ + spec artifact directories."""
    for sub in ("backlog", "in-progress", "qa", "completed", "archive"):
        (tmp_path / "tasks" / sub).mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "adr").mkdir(parents=True, exist_ok=True)
    (tmp_path / "contracts").mkdir(parents=True, exist_ok=True)
    (tmp_path / "migrations").mkdir(parents=True, exist_ok=True)
    return tmp_path


def _arch_rules():
    """Default spec rules (architecture-decision, api-contract, database-schema)."""
    from models import _default_spec_rules
    return _default_spec_rules()


def _engine(rules=None, enabled=True):
    return SpecGateEngine(SpecGateConfig(enabled=enabled, rules=rules))


_ARCH_TASK = (
    "# Task 99: Redesign the payment architecture\n"
    "## Goal\nRedesign the billing service architecture.\n"
)

_ROUTINE_TASK = (
    "# Task 100: Fix typo\n"
    "## Goal\nFix a typo in the README.\n"
)

_DIFF_WITH_ADR = """diff --git a/docs/adr/001-billing.md b/docs/adr/001-billing.md
new file mode 100644
index 0000000..e69de29
--- /dev/null
+++ b/docs/adr/001-billing.md
"""


# ---------------------------------------------------------------------------
# 1. evaluate_requirements
# ---------------------------------------------------------------------------

def test_evaluate_requirements_matches_architectural_keywords():
    rules = _engine(_arch_rules())
    matched = rules.evaluate_requirements(_ARCH_TASK)
    assert len(matched) == 1
    assert matched[0].name == "architecture-decision"


def test_evaluate_requirements_no_match_for_routine_task():
    rules = _engine(_arch_rules())
    assert rules.evaluate_requirements(_ROUTINE_TASK) == []


def test_evaluate_requirements_plan_text_also_triggered():
    rules = _engine(_arch_rules())
    # Keywords live in the approved plan, not the task content.
    matched = rules.evaluate_requirements("simple task", "Introduce grpc proto contract")
    assert len(matched) == 1
    assert matched[0].name == "api-contract"


def test_evaluate_requirements_empty_rules():
    rules = _engine(rules=[])
    assert rules.evaluate_requirements(_ARCH_TASK, "architecture") == []


def test_evaluate_requirements_disabled_gate_still_evaluates():
    # enabled=False only stops enforcement in the daemon; evaluation stays pure.
    rules = _engine(_arch_rules(), enabled=False)
    assert rules.evaluate_requirements(_ARCH_TASK) != []


# ---------------------------------------------------------------------------
# 2. validate_artifacts
# ---------------------------------------------------------------------------

def test_validate_artifacts_passes_when_adr_exists_in_workspace(tmp_path):
    ws = _make_workspace(tmp_path)
    (ws / "docs" / "adr" / "0001-billing.md").write_text("# ADR 1\n")
    rules = _engine(_arch_rules())
    res = rules.validate_artifacts(rules.evaluate_requirements(_ARCH_TASK), ws)
    assert res.passed is True
    assert res.errors == []
    assert "docs/adr/0001-billing.md" in res.found_artifacts
    assert "docs/adr/0001-billing.md" in res.report_md


def test_validate_artifacts_passes_when_contract_in_workspace(tmp_path):
    ws = _make_workspace(tmp_path)
    (ws / "contracts" / "billing.yaml").write_text("openapi: 3.0.0\n")
    rules = _engine(_arch_rules())
    task = "# Task: Add new endpoint\n## Goal\nAdd openapi endpoint\n"
    matched = rules.evaluate_requirements(task)
    assert matched[0].name == "api-contract"
    res = rules.validate_artifacts(matched, ws)
    assert res.passed is True
    assert "contracts/billing.yaml" in res.found_artifacts


def test_validate_artifacts_passes_when_artifact_in_diff_text(tmp_path):
    ws = _make_workspace(tmp_path)
    rules = _engine(_arch_rules())
    # No ADR on disk, but the staged diff adds one.
    res = rules.validate_artifacts(rules.evaluate_requirements(_ARCH_TASK), ws, diff_text=_DIFF_WITH_ADR)
    assert res.passed is True
    assert "docs/adr/001-billing.md" in res.found_artifacts


def test_validate_artifacts_fails_with_diagnostic_report_when_absent(tmp_path):
    ws = _make_workspace(tmp_path)
    rules = _engine(_arch_rules())
    res = rules.validate_artifacts(rules.evaluate_requirements(_ARCH_TASK), ws)
    assert res.passed is False
    assert len(res.errors) == 1
    assert "architecture-decision" in res.errors[0]
    assert "docs/adr/**" in res.errors[0]
    # Markdown report contains verified + missing sections
    assert "# Spec-First Gate Report" in res.report_md
    assert "Missing Spec Artifacts" in res.report_md
    assert "architecture-decision" in res.report_md
    assert "Verified Artifacts" not in res.report_md


def test_validate_artifacts_empty_rules_passes_immediately(tmp_path):
    ws = _make_workspace(tmp_path)
    res = _engine(rules=[]).validate_artifacts([], ws)
    assert res.passed is True
    assert res.found_artifacts == []
    assert res.errors == []


def test_validate_artifacts_data_model_rule_matches_migration(tmp_path):
    ws = _make_workspace(tmp_path)
    (ws / "migrations" / "0001_users.sql").write_text("CREATE TABLE users;")
    rules = _engine(_arch_rules())
    task = "# Task: Add a new table\n## Goal\nCreate sql migration for users\n"
    matched = rules.evaluate_requirements(task)
    assert [r.name for r in matched] == ["database-schema"]
    res = rules.validate_artifacts(matched, ws)
    assert res.passed is True
    assert "migrations/0001_users.sql" in res.found_artifacts


# --- helper: _paths_in_diff ---

def test_paths_in_diff_parses_headers():
    assert _paths_in_diff(_DIFF_WITH_ADR) == ["docs/adr/001-billing.md"]
    assert _paths_in_diff("") == []
    assert _paths_in_diff("no headers") == []


def test_paths_in_diff_deduplicates():
    diff = _DIFF_WITH_ADR + _DIFF_WITH_ADR
    assert _paths_in_diff(diff) == ["docs/adr/001-billing.md"]


# ---------------------------------------------------------------------------
# 3. State machine migration + accessors
# ---------------------------------------------------------------------------

def test_state_spec_artifacts_roundtrip(tmp_path):
    sm = StateMachine(str(tmp_path / "loop.db"))
    try:
        tid = sm.register_task("tasks/backlog/140-spec.md")
        sm.set_spec_artifacts(tid, ["docs/adr/001.md", "contracts/api.yaml"])
        assert sm.get_task(tid)["spec_artifacts"] == json.dumps(
            ["docs/adr/001.md", "contracts/api.yaml"]
        )
        assert sm.get_spec_artifacts(tid) == ["docs/adr/001.md", "contracts/api.yaml"]
    finally:
        sm.close()


def test_state_spec_artifacts_empty_and_corrupt(tmp_path):
    sm = StateMachine(str(tmp_path / "loop.db"))
    try:
        tid = sm.register_task("tasks/backlog/140b.md")
        assert sm.get_spec_artifacts(tid) == []
        sm.set_spec_artifacts(tid, [])
        assert sm.get_spec_artifacts(tid) == []
        # Corrupt persisted JSON -> [] fallback
        sm.conn.execute("UPDATE tasks SET spec_artifacts = ? WHERE task_id = ?",
                        ("{not-json", tid))
        sm.conn.commit()
        assert sm.get_spec_artifacts(tid) == []
        # Non-list JSON -> [] fallback
        sm.set_spec_artifacts(tid, ["a"])
        sm.conn.execute("UPDATE tasks SET spec_artifacts = ? WHERE task_id = ?",
                        ('"scalar"', tid))
        sm.conn.commit()
        assert sm.get_spec_artifacts(tid) == []
    finally:
        sm.close()


def test_state_migration_adds_column_to_old_db(tmp_path):
    """A DB created WITHOUT spec_artifacts gains the column via the safe ALTER."""
    db_path = tmp_path / "legacy.db"
    conn = sqlite3.connect(str(db_path))
    conn.executescript(
        """
        CREATE TABLE tasks (
            task_id INTEGER PRIMARY KEY,
            task_file TEXT NOT NULL UNIQUE,
            state TEXT NOT NULL DEFAULT 'backlog',
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL
        );
        """
    )
    conn.execute(
        "INSERT INTO tasks (task_file, created_at, updated_at) VALUES ('tasks/backlog/legacy.md', 1, 1)"
    )
    conn.commit()
    conn.close()

    sm = StateMachine(str(db_path))
    try:
        cols = [r[1] for r in sm.conn.execute("PRAGMA table_info(tasks)").fetchall()]
        assert "spec_artifacts" in cols
        row = sm.conn.execute(
            "SELECT spec_artifacts FROM tasks WHERE task_file = 'tasks/backlog/legacy.md'"
        ).fetchone()
        assert row[0] is None
    finally:
        sm.close()


def test_state_migration_idempotent_on_new_db(tmp_path):
    """New DBs already declare the column; the ALTER no-ops without error."""
    sm = StateMachine(str(tmp_path / "loop.db"))
    try:
        cols = [r[1] for r in sm.conn.execute("PRAGMA table_info(tasks)").fetchall()]
        assert "spec_artifacts" in cols
        tid = sm.register_task("tasks/backlog/140c.md")
        assert sm.get_spec_artifacts(tid) == []
    finally:
        sm.close()


# ---------------------------------------------------------------------------
# 4. Daemon integration (real _process_task)
# ---------------------------------------------------------------------------

def _make_daemon_stubs(config):
    router = MagicMock()
    router.route_plan.return_value = {"plan": "routing"}
    router.call_llm.return_value = "Approved plan text"
    gateway = MagicMock()
    gateway.request_approval = AsyncMock(return_value=True)
    executor = MagicMock()
    qa = MagicMock()
    qa.run_review.return_value = {"result": "APPROVED"}
    brainstorm = MagicMock()
    brainstorm.should_trigger.return_value = False
    return router, gateway, executor, qa, brainstorm


def _write_task(ws, text):
    task_file = ws / "tasks" / "in-progress" / "140-spec.md"
    task_file.write_text(text)
    return task_file


def _run_pipeline(ws, task_file, config, executor_cls=None):
    """Run the real _process_task with fake execute_and_qa that records the gate state."""
    router, gateway, executor, qa, brainstorm = _make_daemon_stubs(config)
    state = StateMachine(str(ws / "loop.db"))
    tid = state.register_task(str(task_file), TaskState.AWAITING_APPROVAL)

    captured = {}

    async def _fake_execute_and_qa(*args, **kwargs):
        captured["entered_executing"] = state.get_task(tid)["state"]
        return {"result": "PASSED", "report": "ok"}

    async def _run():
        await daemon._process_task(
            tid, str(task_file), config, state, router, gateway, executor, qa, brainstorm
        )

    with patch.object(daemon, "_execute_and_qa", new=_fake_execute_and_qa):
        with patch.object(daemon, "REPO_ROOT", ws):
            asyncio.run(_run())
    return tid, state, captured


def _spec_config(rules):
    return LoopEngineConfig(approval={"chat_id": 0}, trigger_mode="auto",
                            spec_gate=SpecGateConfig(enabled=True, rules=rules))


def test_daemon_spec_gate_passes_and_proceeds(tmp_path):
    ws = _make_workspace(tmp_path)
    (ws / "docs" / "adr" / "0001.md").write_text("# ADR 1\n")
    task_file = _write_task(ws, _ARCH_TASK)
    config = _spec_config(_arch_rules())

    tid, state, captured = _run_pipeline(ws, task_file, config)
    try:
        # Gate passed -> execution entered, artifacts persisted
        assert captured["entered_executing"] == "implementing"
        assert state.get_spec_artifacts(tid) == ["docs/adr/0001.md"]
    finally:
        state.close()


def test_daemon_spec_gate_failure_crashes_before_implementing(tmp_path):
    ws = _make_workspace(tmp_path)  # no ADR anywhere
    task_file = _write_task(ws, _ARCH_TASK)
    config = _spec_config(_arch_rules())

    tid, state, captured = _run_pipeline(ws, task_file, config)
    try:
        assert state.get_task(tid)["state"] == "crashed"
        assert "entered_executing" not in captured  # never reached IMPLEMENTING
        assert "architecture-decision" in (state.get_task(tid)["qa_feedback"] or "")
        assert "# Spec-First Gate Report" in (state.get_task(tid)["qa_feedback"] or "")
        assert state.get_spec_artifacts(tid) == []
    finally:
        state.close()


def test_daemon_spec_gate_disabled_proceeds_without_gate(tmp_path):
    ws = _make_workspace(tmp_path)  # no ADR
    task_file = _write_task(ws, _ARCH_TASK)
    config = LoopEngineConfig(approval={"chat_id": 0}, trigger_mode="auto",
                              spec_gate=SpecGateConfig(enabled=False, rules=_arch_rules()))

    tid, state, captured = _run_pipeline(ws, task_file, config)
    try:
        assert captured["entered_executing"] == "implementing"
        assert state.get_spec_artifacts(tid) == []
    finally:
        state.close()


def test_daemon_spec_gate_routine_task_bypasses(tmp_path):
    ws = _make_workspace(tmp_path)  # no artifacts
    task_file = _write_task(ws, _ROUTINE_TASK)
    config = _spec_config(_arch_rules())

    tid, state, captured = _run_pipeline(ws, task_file, config)
    try:
        assert captured["entered_executing"] == "implementing"
        assert state.get_spec_artifacts(tid) == []
    finally:
        state.close()


def test_loop_engine_config_default_spec_gate():
    cfg = LoopEngineConfig(approval={"chat_id": 0})
    assert cfg.spec_gate.enabled is True
    assert cfg.spec_gate.rules == []
    assert isinstance(cfg.spec_gate, SpecGateConfig)


def test_default_spec_rules_shapes():
    rules = _arch_rules()
    assert [r.name for r in rules] == [
        "architecture-decision", "api-contract", "database-schema"
    ]
    arch, api, db = rules
    assert arch.required_artifacts == [SpecArtifactType.ADR]
    assert arch.target_directories == ["docs/adr/**", "docs/architecture.md"]
    assert api.required_artifacts == [SpecArtifactType.CONTRACT]
    assert api.target_directories == ["contracts/**", "openapi/**", "proto/**"]
    assert db.required_artifacts == [SpecArtifactType.DATA_MODEL]
    assert db.target_directories == ["docs/data_model.md", "prisma/**", "migrations/**"]


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for t in tests:
        try:
            t(Path("/tmp/specs-test-ws")) if "tmp_path" in t.__code__.co_varnames else t()
            print(f"  PASS: {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)