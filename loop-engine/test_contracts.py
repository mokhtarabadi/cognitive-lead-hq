"""Tests for Contract Propagation & Downstream Task Dispatcher (LE-6 / Task 138).

Covers:
1. ``extract_modified_paths`` — git diff path parsing (additions, updates,
   deletions, dedup, empty).
2. ``match_contract_rules`` — glob pattern matching across contract families
   (shared-schema ``**``, openapi ``*.yaml``, prisma extension).
3. ``discover_next_task_id`` — sequential, gap, multi-folder, and empty layouts.
4. ``ContractPropagationEngine.process_task_closure`` — batch generation with
   sequential IDs, canonical Markdown headers, state registration, formatting,
   and the non-contract no-op.
5. Daemon integration — task closure triggers downstream backlog tasks through
   the real ``_process_task`` closure hook.
"""
import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.dirname(__file__))

from models import ContractRuleConfig, DownstreamTaskTemplate, LoopEngineConfig, TaskState
from state import StateMachine

import daemon
from contracts import (
    ContractPropagationEngine,
    discover_next_task_id,
    extract_modified_paths,
    match_contract_rules,
)


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

_MODIFIED_DIFF = """diff --git a/openapi/contract.yaml b/openapi/contract.yaml
index 1111111..2222222 100644
--- a/openapi/contract.yaml
+++ b/openapi/contract.yaml
@@ -1,3 +1,4 @@
-old: value
+new: value
"""

_ADDED_DIFF = """diff --git a/packages/shared-schema/v1/types.ts b/packages/shared-schema/v1/types.ts
new file mode 100644
index 0000000..e69de29
--- /dev/null
+++ b/packages/shared-schema/v1/types.ts
@@ -0,0 +1 @@
+export type User = { id: string };
"""

_DELETED_DIFF = """diff --git a/contracts/legacy.yaml b/contracts/legacy.yaml
deleted file mode 100644
index 3333333..0000000
--- a/contracts/legacy.yaml
+++ /dev/null
@@ -1,2 +0,0 @@
-legacy: gone
"""


def _openapi_rule(templates=None):
    """Contract rule for OpenAPI specs with one downstream SDK sync task."""
    return ContractRuleConfig(
        name="openapi-spec",
        patterns=["openapi/**", "contracts/*.yaml", "contracts/*.json"],
        downstream_tasks=templates or [
            DownstreamTaskTemplate(
                title_template="Sync SDK with updated {contract_name}",
                stack="node-ts",
                goal_template="Update SDK for {contract_name}. Files: {files}",
                acceptance_criteria=["SDK updated", "Tests pass"],
            )
        ],
    )


def _two_template_rule():
    """OpenAPI rule with TWO downstream templates (batch generation)."""
    return ContractRuleConfig(
        name="openapi-spec",
        patterns=["openapi/**"],
        downstream_tasks=[
            DownstreamTaskTemplate(
                title_template="Regenerate API client for updated {contract_name}",
                stack="node-ts",
                goal_template="Regenerate client for {contract_name}. Files: {files}",
                acceptance_criteria=["Client regenerated"],
            ),
            DownstreamTaskTemplate(
                title_template="Update API docs for {contract_name}",
                stack="generic",
                goal_template="Update docs referencing {contract_name}. Files: {files}",
                acceptance_criteria=["Docs updated"],
            ),
        ],
    )


def _make_workspace(tmp_path):
    """Build tasks/{backlog,in-progress,qa,completed,archive} under tmp_path."""
    for sub in ("backlog", "in-progress", "qa", "completed", "archive"):
        (tmp_path / "tasks" / sub).mkdir(parents=True, exist_ok=True)
    return tmp_path


# ---------------------------------------------------------------------------
# 1. extract_modified_paths
# ---------------------------------------------------------------------------

def test_extract_modified_paths_new_file():
    paths = extract_modified_paths(_ADDED_DIFF)
    assert paths == ["packages/shared-schema/v1/types.ts"]


def test_extract_modified_paths_modified_file():
    assert extract_modified_paths(_MODIFIED_DIFF) == ["openapi/contract.yaml"]


def test_extract_modified_paths_deletion():
    assert extract_modified_paths(_DELETED_DIFF) == ["contracts/legacy.yaml"]


def test_extract_modified_paths_deduplicates():
    diff = _MODIFIED_DIFF + _MODIFIED_DIFF
    assert extract_modified_paths(diff) == ["openapi/contract.yaml"]


def test_extract_modified_paths_empty_diff():
    assert extract_modified_paths("") == []
    assert extract_modified_paths("no diff headers here") == []


# ---------------------------------------------------------------------------
# 2. match_contract_rules
# ---------------------------------------------------------------------------

def test_match_contract_rules_shared_schema_recursive():
    rule = ContractRuleConfig(name="shared-schema", patterns=["packages/shared-schema/**"])
    paths = ["packages/shared-schema/v1/types.ts", "src/app.ts"]
    matches = match_contract_rules(paths, [rule])
    assert len(matches) == 1
    matched_rule, matched_files = matches[0]
    assert matched_rule.name == "shared-schema"
    assert matched_files == ["packages/shared-schema/v1/types.ts"]


def test_match_contract_rules_openapi_yaml():
    rule = _openapi_rule()
    paths = ["openapi/petstore.yaml", "src/main.ts"]
    matches = match_contract_rules(paths, [rule])
    assert matches[0][1] == ["openapi/petstore.yaml"]


def test_match_contract_rules_prisma_extension():
    rule = ContractRuleConfig(name="prisma-schema", patterns=["*.prisma", "prisma/**"])
    paths = ["prisma/schema.prisma", "server/index.ts"]
    matches = match_contract_rules(paths, [rule])
    assert matches[0][1] == ["prisma/schema.prisma"]


def test_match_contract_rules_no_match_returns_empty():
    rule = _openapi_rule()
    matches = match_contract_rules(["src/main.ts", "docs/README.md"], [rule])
    assert matches == []


# ---------------------------------------------------------------------------
# 3. discover_next_task_id
# ---------------------------------------------------------------------------

def test_discover_next_task_id_sequential(tmp_path):
    _make_workspace(tmp_path)
    for i in (1, 2, 3):
        (tmp_path / "tasks" / "backlog" / f"{i:02d}-task.md").write_text(f"# Task {i}\n")
    assert discover_next_task_id(tmp_path / "tasks") == 4


def test_discover_next_task_id_gap(tmp_path):
    _make_workspace(tmp_path)
    (tmp_path / "tasks" / "backlog" / "01-a.md").write_text("# Task 1\n")
    (tmp_path / "tasks" / "qa" / "05-b.md").write_text("# Task 5\n")
    assert discover_next_task_id(tmp_path / "tasks") == 6


def test_discover_next_task_id_multi_folder(tmp_path):
    _make_workspace(tmp_path)
    layout = {
        "backlog": [7, 12],
        "in-progress": [8],
        "qa": [9],
        "completed": [10],
        "archive": [11, 13],
    }
    for folder, ids in layout.items():
        for i in ids:
            (tmp_path / "tasks" / folder / f"{i:02d}-t.md").write_text(f"# Task {i}\n")
    assert discover_next_task_id(tmp_path / "tasks") == 14


def test_discover_next_task_id_empty(tmp_path):
    _make_workspace(tmp_path)
    assert discover_next_task_id(tmp_path / "tasks") == 1


# ---------------------------------------------------------------------------
# 4. ContractPropagationEngine.process_task_closure
# ---------------------------------------------------------------------------

def test_process_task_closure_generates_batch_with_sequential_ids(tmp_path):
    _make_workspace(tmp_path)
    (tmp_path / "tasks" / "backlog" / "05-existing.md").write_text("# Task 5\n")
    state = StateMachine(str(tmp_path / "loop.db"))
    try:
        engine = ContractPropagationEngine(
            rules=[_two_template_rule()], tasks_dir="tasks"
        )
        dispatched = engine.process_task_closure(
            task_id=42,
            task_file="tasks/completed/05-existing.md",
            diff_text=_MODIFIED_DIFF,
            repo_root=tmp_path,
            state=state,
        )
        assert len(dispatched) == 2
        assert [d["task_id"] for d in dispatched] == [6, 7]
        assert dispatched[0]["file"] == "tasks/backlog/06-regenerate-api-client-for-updated-openapi-spec.md"
        assert dispatched[1]["file"] == "tasks/backlog/07-update-api-docs-for-openapi-spec.md"

        first = (tmp_path / "tasks" / "backlog" / "06-regenerate-api-client-for-updated-openapi-spec.md").read_text()
        second = (tmp_path / "tasks" / "backlog" / "07-update-api-docs-for-openapi-spec.md").read_text()

        # Canonical markdown headers for both generated tasks
        for body, task_id, title in (
            (first, 6, "Regenerate API client for updated openapi-spec"),
            (second, 7, "Update API docs for openapi-spec"),
        ):
            assert body.startswith(f"# Task {task_id}: {title}\n")
            assert "**Source:** contract-propagation" in body
            assert "**Triggered-By:** Task 42" in body
            assert "**Stack:**" in body
            assert "**Type:** feature" in body
            assert "**Status:** open" in body
            assert "## Goal" in body
            assert "## Source Context" in body
            assert "## Acceptance Criteria" in body
            assert "<!-- BEGIN_GIT_DIFF -->" in body
            assert "<!-- END_GIT_DIFF -->" in body
            assert "openapi/contract.yaml" in body
    finally:
        state.close()


def test_process_task_closure_formats_title_goal_and_files(tmp_path):
    _make_workspace(tmp_path)
    state = StateMachine(str(tmp_path / "loop.db"))
    try:
        rule = ContractRuleConfig(
            name="shared-schema",
            patterns=["packages/shared-schema/**"],
            downstream_tasks=[
                DownstreamTaskTemplate(
                    title_template="Propagate {contract_name} from Task {triggering_task_id}",
                    stack="generic",
                    goal_template="Sync {contract_name} consumers. Files: {files}",
                    acceptance_criteria=["Consumers updated"],
                )
            ],
        )
        dispatched = ContractPropagationEngine(rules=[rule], tasks_dir="tasks").process_task_closure(
            task_id=9,
            task_file="tasks/completed/09-x.md",
            diff_text=_ADDED_DIFF,
            repo_root=tmp_path,
            state=state,
        )
        assert len(dispatched) == 1
        body = (tmp_path / "tasks" / "backlog" / "01-propagate-shared-schema-from-task-9.md").read_text()
        assert "# Task 1: Propagate shared-schema from Task 9" in body
        assert "Sync shared-schema consumers. Files: packages/shared-schema/v1/types.ts" in body
        assert "- packages/shared-schema/v1/types.ts" in body
        assert "- [ ] Consumers updated" in body
    finally:
        state.close()


def test_process_task_closure_registers_in_state_backlog(tmp_path):
    _make_workspace(tmp_path)
    state = StateMachine(str(tmp_path / "loop.db"))
    try:
        disposed = ContractPropagationEngine(
            rules=[_openapi_rule()], tasks_dir="tasks"
        ).process_task_closure(
            task_id=1,
            task_file="tasks/completed/01-x.md",
            diff_text=_MODIFIED_DIFF,
            repo_root=tmp_path,
            state=state,
        )
        target = tmp_path / "tasks" / "backlog" / "01-sync-sdk-with-updated-openapi-spec.md"
        assert target.exists()
        record = state.get_task_by_file(str(target))
        assert record is not None
        assert record["state"] == "backlog"
        assert disposed[0]["task_id"] == record["task_id"]
    finally:
        state.close()


def test_process_task_closure_non_contract_noop(tmp_path):
    _make_workspace(tmp_path)
    state = StateMachine(str(tmp_path / "loop.db"))
    try:
        diff = """diff --git a/src/main.ts b/src/main.ts
index 1111111..2222222 100644
--- a/src/main.ts
+++ b/src/main.ts
@@ -1 +1 @@
-console.log("old");
+console.log("new");
"""
        dispatched = ContractPropagationEngine(
            rules=[_openapi_rule()], tasks_dir="tasks"
        ).process_task_closure(
            task_id=1,
            task_file="tasks/completed/01-x.md",
            diff_text=diff,
            repo_root=tmp_path,
            state=state,
        )
        assert dispatched == []
        assert list((tmp_path / "tasks" / "backlog").glob("*.md")) == []
    finally:
        state.close()


def test_loop_engine_config_default_contract_rules():
    cfg = LoopEngineConfig(approval={"chat_id": 0})
    names = [r.name for r in cfg.contract_rules]
    assert names == ["openapi-spec", "prisma-schema", "protobuf", "shared-schema"]
    openapi = cfg.contract_rules[0]
    assert openapi.patterns == ["openapi/**", "contracts/*.yaml", "contracts/*.json"]
    assert openapi.downstream_tasks[0].stack == "node-ts"


# ---------------------------------------------------------------------------
# 5. Daemon integration
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


def test_daemon_init_wires_propagation_engine():
    config = LoopEngineConfig(approval={"chat_id": 0})
    state = MagicMock()
    router = MagicMock()
    gateway = MagicMock()
    executor = MagicMock()
    qa = MagicMock()
    brainstorm = MagicMock()
    d = daemon.LoopEngineDaemon(config, state, router, gateway, executor, qa, brainstorm)
    assert isinstance(d.propagation_engine, ContractPropagationEngine)
    assert d.propagation_engine.tasks_dir == Path("tasks")


def test_daemon_task_closure_dispatches_downstream_tasks(tmp_path):
    """Real _process_task closure hook: CLOSED + contract diff -> backlog tasks."""
    ws = _make_workspace(tmp_path)
    (ws / "tasks" / "backlog" / "10-existing.md").write_text("# Task 10\n")
    config = LoopEngineConfig(approval={"chat_id": 0}, trigger_mode="auto")
    router, gateway, executor, qa, brainstorm = _make_daemon_stubs(config)

    task_file = ws / "tasks" / "completed" / "10-existing.md"
    task_file.write_text(
        "# Task 10: Contract Mutation\n"
        "**Source:** orchestrator\n"
        "**Type:** feature\n"
        "## Goal\nUpdate the OpenAPI contract.\n"
        "## Factual Git Diff\n"
        "<!-- BEGIN_GIT_DIFF -->\n"
        + _MODIFIED_DIFF +
        "<!-- END_GIT_DIFF -->\n"
    )

    state = StateMachine(str(ws / "loop.db"))
    tid = state.register_task(str(task_file), TaskState.AWAITING_CLOSURE)
    try:
        async def _run():
            await daemon._process_task(
                tid, str(task_file), config, state, router, gateway, executor, qa, brainstorm
            )

        async def _fake_execute_and_qa(*args, **kwargs):
            return {"result": "PASSED", "report": "ok"}

        with patch.object(daemon, "_execute_and_qa", new=_fake_execute_and_qa):
            with patch.object(daemon, "REPO_ROOT", ws):
                asyncio.run(_run())

        # Trigger task reached CLOSED
        assert state.get_task(tid)["state"] == "closed"

        # Downstream task generated with next sequential id (11) using the
        # config's DEFAULT openapi-spec rule template.
        backlog_files = sorted((ws / "tasks" / "backlog").glob("*.md"))
        names = [f.name for f in backlog_files]
        assert any(name.startswith("11-regenerate-api-client-for-updated-openapi-spec") for name in names)
        generated = ws / "tasks" / "backlog" / "11-regenerate-api-client-for-updated-openapi-spec.md"
        assert generated.exists()
        body = generated.read_text()
        assert f"**Triggered-By:** Task {tid}" in body
        assert "**Source:** contract-propagation" in body
        # Registered in the state machine as backlog
        assert state.get_task_by_file(str(generated))["state"] == "backlog"
    finally:
        state.close()


def test_daemon_task_closure_noop_without_contract_diff(tmp_path):
    """Real _process_task closure hook: non-contract diff -> no backlog tasks."""
    ws = _make_workspace(tmp_path)
    config = LoopEngineConfig(approval={"chat_id": 0}, trigger_mode="auto")
    router, gateway, executor, qa, brainstorm = _make_daemon_stubs(config)

    task_file = ws / "tasks" / "completed" / "20-regular.md"
    task_file.write_text(
        "# Task 20: Regular Change\n"
        "**Source:** orchestrator\n"
        "**Type:** feature\n"
        "## Goal\nRefactor a service.\n"
        "## Factual Git Diff\n"
        "<!-- BEGIN_GIT_DIFF -->\n"
        "diff --git a/src/main.ts b/src/main.ts\n"
        "index 1111111..2222222 100644\n"
        "--- a/src/main.ts\n"
        "+++ b/src/main.ts\n"
        "@@ -1 +1 @@\n"
        "-old\n"
        "+new\n"
        "<!-- END_GIT_DIFF -->\n"
    )

    state = StateMachine(str(ws / "loop.db"))
    tid = state.register_task(str(task_file), TaskState.AWAITING_CLOSURE)
    try:
        async def _run():
            await daemon._process_task(
                tid, str(task_file), config, state, router, gateway, executor, qa, brainstorm
            )

        async def _fake_execute_and_qa(*args, **kwargs):
            return {"result": "PASSED", "report": "ok"}

        with patch.object(daemon, "_execute_and_qa", new=_fake_execute_and_qa):
            with patch.object(daemon, "REPO_ROOT", ws):
                asyncio.run(_run())

        assert state.get_task(tid)["state"] == "closed"
        assert list((ws / "tasks" / "backlog").glob("*.md")) == []
    finally:
        state.close()


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for t in tests:
        try:
            t(Path("/tmp/contracts-test-ws")) if "tmp_path" in t.__code__.co_varnames else t()
            print(f"  PASS: {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)