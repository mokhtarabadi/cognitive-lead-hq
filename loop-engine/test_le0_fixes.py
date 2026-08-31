"""Tests for LE-0.1..LE-0.4 fixes — verification-before-patch."""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

REPO_ROOT = str(Path(__file__).resolve().parent.parent)

from models import LoopEngineConfig, TaskState


def _cfg():
    return LoopEngineConfig(approval={"chat_id": 123})


# --- LE-0.1: blueprint_context threading ---

def test_executor_blueprint_context_injected():
    from executor import HandsExecutor
    from state import StateMachine
    import inspect
    sig = inspect.signature(HandsExecutor.execute)
    assert "blueprint_context" in sig.parameters, "executor.execute missing blueprint_context param"
    assert sig.parameters["blueprint_context"].default == ""
    # Check prompt injection by inspecting source
    src = Path(__file__).parent.joinpath("executor.py").read_text(encoding="utf-8")
    assert "blueprint_context" in src
    assert "<blueprint_context>" in src


def test_executor_qa_feedback_distinct():
    from executor import HandsExecutor
    import inspect
    sig = inspect.signature(HandsExecutor.execute)
    assert "qa_feedback" in sig.parameters
    assert sig.parameters["qa_feedback"].default == ""
    src = Path(__file__).parent.joinpath("executor.py").read_text(encoding="utf-8")
    assert "<qa_feedback>" in src
    # Ensure blueprint_context and qa_feedback are distinct params, not overloaded
    assert "blueprint_context" in src and "qa_feedback" in src
    # Prompt must label QA feedback distinctly from blueprint (allow line split)
    assert "Do NOT treat this" in src
    assert "as a new architectural plan" in src


def test_executor_prompt_build_with_both_contexts():
    """Directly test prompt construction via _run_once capture."""
    from executor import HandsExecutor
    from state import StateMachine

    with tempfile.TemporaryDirectory() as tmp:
        sm = StateMachine(os.path.join(tmp, "t.db"))
        cfg = _cfg()
        exe = HandsExecutor(cfg, sm)

        # We can't call _run_once without opencode, but we can test execute's prompt building
        # by checking that execute creates prompt with both sections when provided.
        # Patch _run_once to capture prompt.
        captured = {}

        async def fake_run_once(task_file, prompt):
            captured["prompt"] = prompt
            return {"status": "complete", "output": "ok", "error": "", "elapsed": 0.1}

        original = exe._run_once
        exe._run_once = fake_run_once

        async def run():
            await exe.execute(1, "tasks/backlog/01.md", "content",
                              blueprint_context="## Plan\n1. do X",
                              qa_feedback="Fix bug on line 42")
            p = captured["prompt"]
            assert "<blueprint_context>" in p
            assert "## Plan\n1. do X" in p
            assert "<qa_feedback>" in p
            assert "Fix bug on line 42" in p
            # Empty case
            captured.clear()
            await exe.execute(1, "tasks/backlog/01.md", "content",
                              blueprint_context="", qa_feedback="")
            p2 = captured["prompt"]
            assert "<blueprint_context>" not in p2
            assert "<qa_feedback>" not in p2

        asyncio.run(run())
        exe._run_once = original
        sm.close()


# --- LE-0.2: diff extraction ---

def test_extract_task_diff_clean():
    from daemon import extract_task_diff
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("header\n<!-- BEGIN_GIT_DIFF -->\n+added line\n-removed\n<!-- END_GIT_DIFF -->\nfooter")
        fname = f.name
    try:
        diff = extract_task_diff(Path(fname))
        assert diff is not None
        assert "+added line" in diff
        assert "-removed" in diff
        assert "header" not in diff
    finally:
        os.unlink(fname)


def test_extract_task_diff_missing_markers():
    from daemon import extract_task_diff
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("no markers here")
        fname = f.name
    try:
        diff = extract_task_diff(Path(fname))
        assert diff is None
    finally:
        os.unlink(fname)


def test_extract_task_diff_empty_block():
    from daemon import extract_task_diff
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("<!-- BEGIN_GIT_DIFF -->\n   \n<!-- END_GIT_DIFF -->")
        fname = f.name
    try:
        diff = extract_task_diff(Path(fname))
        assert diff == ""  # empty stripped
        assert not diff.strip()
    finally:
        os.unlink(fname)


def test_extract_task_diff_malformed_no_end():
    from daemon import extract_task_diff
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("<!-- BEGIN_GIT_DIFF -->\ncontent without end")
        fname = f.name
    try:
        diff = extract_task_diff(Path(fname))
        assert diff is None
    finally:
        os.unlink(fname)


# --- LE-0.2: empty diff hard failure in pipeline (integration) ---

def test_daemon_empty_diff_crashes():
    """Pipeline must CRASHED when diff missing, never call QA."""
    from daemon import _process_task, extract_task_diff
    from state import StateMachine
    from models import TaskState
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        # Create a task file WITHOUT diff markers
        task_file = Path(tmp) / "01-test.md"
        task_file.write_text("# Task 1\n## Goal\nTest\n<!-- BEGIN_GIT_DIFF -->\n<!-- END_GIT_DIFF -->", encoding="utf-8")
        # Actually this has empty diff -> should crash

        # Minimal stubs
        cfg = LoopEngineConfig(approval={"chat_id": 1},
                               evidence_dir=os.path.join(tmp, "evidence"),
                               max_qa_retries=2)
        sm = StateMachine(os.path.join(tmp, "t.db"))
        tid = sm.register_task(str(task_file), TaskState.BACKLOG)

        # Stub router
        class StubRouter:
            def route_plan(self, task_content, extra_context=""):
                return {}
            def call_llm(self, routing):
                return "## Plan\nDo thing"
            def route_qa(self, tc, diff=""):
                return {}
            def route_review(self, tc, qa=""):
                return {}
            def _resolve_model(self, category):
                return "stub/model", None

        stub_router = StubRouter()

        # Stub gateway: approve plan
        class StubGateway:
            async def request_approval(self, tid, title, content):
                return True

        # Stub executor: returns complete, but we want empty diff path
        class StubExecutor:
            async def execute(self, task_id, task_file, task_content, blueprint_context="", qa_feedback=""):
                # Simulate Hands writing task file with EMPTY diff block
                p = Path(task_file)
                text = p.read_text(encoding="utf-8")
                # Ensure diff block is empty
                if "<!-- BEGIN_GIT_DIFF -->" in text:
                    # Keep empty
                    pass
                else:
                    text += "\n<!-- BEGIN_GIT_DIFF -->\n<!-- END_GIT_DIFF -->\n"
                    p.write_text(text, encoding="utf-8")
                return {"status": "complete", "output": "fake output"}

        # Stub QA: should NOT be called if empty diff check works
        class StubQA:
            def __init__(self):
                self.called = False
            def run_qa(self, tid, tc, diff):
                self.called = True
                return {"result": "PASSED", "report": "PASSED"}
            def run_review(self, tid, tc, qr):
                return {"result": "APPROVED", "review": "ok"}

        stub_qa = StubQA()
        from brainstorm import BrainstormStage
        brainstorm = BrainstormStage(cfg, stub_router, workspace_root=REPO_ROOT)
        # Ensure brainstorm not triggered — avoid magic word
        task_file.write_text("# Task 1\nSimple fix no trigger word here", encoding="utf-8")

        asyncio.run(_process_task(tid, str(task_file), cfg, sm, stub_router, StubGateway(), StubExecutor(), stub_qa, brainstorm))

        task = sm.get_task(tid)
        assert task["state"] == "crashed", f"Expected crashed on empty diff, got {task['state']}"
        assert not stub_qa.called, "QA should not have been called with empty diff"
        sm.close()


# --- LE-0.3: scoped reimplement (verify function exists and uses state retry) ---

def test_reimplement_task_exists_and_uses_state_retry():
    src = Path(__file__).parent.joinpath("daemon.py").read_text(encoding="utf-8")
    assert "_reimplement_task" in src
    assert "get_qa_retry_count" in src
    assert "max_qa_retries" in src
    assert "qa_feedback" in src
    # After DRY Step 5, shared logic is in _execute_and_qa, so reimplement should call it
    assert "_execute_and_qa" in src
    reimplement_block = src.split("async def _reimplement_task")[1].split("async def ")[0]
    assert "qa_feedback" in reimplement_block
    assert "_execute_and_qa" in reimplement_block
    # Must NOT contain plan approval (except closure) or brainstorm in reimplement
    assert "Closure Approval" in reimplement_block
    assert "Plan Approval" not in reimplement_block
    assert "Brainstorm" not in reimplement_block
    assert "route_plan" not in reimplement_block
    # Ensure it doesn't recurse to full pipeline process_task
    assert "await process_task" not in reimplement_block
    # Verify DRY helper exists and is used by both sites
    assert "async def _execute_and_qa" in src
    # _process_task should also use helper
    process_block = src.split("async def _process_task")[1].split("async def ")[0] if "async def _process_task" in src else ""
    assert "_execute_and_qa" in process_block


def test_daemon_qa_failure_calls_reimplement_not_process_task():
    src = Path(__file__).parent.joinpath("daemon.py").read_text(encoding="utf-8")
    # After QA FAILED in _process_task should call _reimplement_task, not process_task
    assert "async def _process_task" in src
    process_block = src.split("async def _process_task")[1]
    assert "if qa_result[\"result\"] == \"FAILED\":" in process_block
    # Take the first FAILED block inside _process_task (before REVIEW)
    block = process_block.split("if qa_result[\"result\"] == \"FAILED\":")[1].split("# 5. REVIEW")[0]
    assert "_reimplement_task" in block
    # Old buggy recursion must be gone from this block
    assert "return await process_task" not in block


# --- LE-0.4: router memory query ---

def test_router_memory_query_present():
    src = Path(__file__).parent.joinpath("router.py").read_text(encoding="utf-8")
    assert "_load_memory_context" in src
    assert ".opencode/memory" in src
    assert "memory_context" in src
    assert "Context Bootstrapping & Memory Protocol" in src
    # Ensure _build_system_context appends memory
    assert "<memory_context>" in src


def test_router_includes_memory_in_context(tmp_path=None):
    from router import LLMRouter
    cfg = _cfg()
    # Create temp workspace with memory
    with tempfile.TemporaryDirectory() as tmp:
        mem_dir = Path(tmp) / ".opencode" / "memory" / "project"
        mem_dir.mkdir(parents=True)
        (mem_dir / "test-memory.md").write_text("# Test Memory\nThis is important project rule: always use UTC.", encoding="utf-8")
        # Also create required fragment files by symlinking from real repo
        # Router needs personas; copy or link fragments
        import shutil
        src_fragments = Path(REPO_ROOT) / "prompts" / "fragments"
        dst_fragments = Path(tmp) / "prompts" / "fragments"
        dst_fragments.mkdir(parents=True)
        for f in src_fragments.glob("*.md"):
            shutil.copy(f, dst_fragments / f.name)
        # Also copy AGENTS.md, system-prompt, conventions if needed
        for rel in ["AGENTS.md", "system-prompt.md", "docs/conventions.md"]:
            src = Path(REPO_ROOT) / rel
            dst = Path(tmp) / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.exists():
                shutil.copy(src, dst)

        router = LLMRouter(cfg, workspace_root=tmp)
        ctx = router._build_system_context("architect")
        assert "always use UTC" in ctx
        assert 'namespace="project"' in ctx
        assert 'key="test-memory"' in ctx


def test_router_without_memory_still_works():
    from router import LLMRouter
    cfg = _cfg()
    with tempfile.TemporaryDirectory() as tmp:
        # No memory dir
        import shutil
        src_fragments = Path(REPO_ROOT) / "prompts" / "fragments"
        dst_fragments = Path(tmp) / "prompts" / "fragments"
        dst_fragments.mkdir(parents=True)
        for f in src_fragments.glob("*.md"):
            shutil.copy(f, dst_fragments / f.name)
        for rel in ["AGENTS.md", "system-prompt.md", "docs/conventions.md"]:
            src = Path(REPO_ROOT) / rel
            dst = Path(tmp) / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.exists():
                shutil.copy(src, dst)
        router = LLMRouter(cfg, workspace_root=tmp)
        ctx = router._build_system_context("architect")
        assert "Software Architect" in ctx  # still works without memory


def test_reimplement_task_retry_loop_terminates():
    """Step 2: FAILED, FAILED, PASSED with max=3 → CLOSED, retry count increases, 1 Closure, 0 Plan."""
    from unittest.mock import patch
    from daemon import _reimplement_task
    from state import StateMachine
    # Mock toolchain to avoid real lint/test execution interfering with QA retry counting
    patcher = patch('daemon.ToolchainRunner', None)
    patcher.start()

    with tempfile.TemporaryDirectory() as tmp:
        task_file = Path(tmp) / "02-retry.md"
        task_file.write_text("# Task\nSimple no trigger\n<!-- BEGIN_GIT_DIFF -->\ninitial diff\n<!-- END_GIT_DIFF -->", encoding="utf-8")

        cfg = LoopEngineConfig(approval={"chat_id": 1},
                               evidence_dir=os.path.join(tmp, "evidence"),
                               max_qa_retries=3)
        sm = StateMachine(os.path.join(tmp, "t.db"))
        tid = sm.register_task(str(task_file), TaskState.BACKLOG)
        # Start at 0, _reimplement will handle FAILED->increment sequence
        assert sm.get_qa_retry_count(tid) == 0

        # Stub executor always complete + writes valid diff
        class StubExecutor:
            async def execute(self, task_id, task_file, task_content, blueprint_context="", qa_feedback=""):
                p = Path(task_file)
                text = p.read_text(encoding="utf-8")
                if "<!-- BEGIN_GIT_DIFF -->" in text and "initial diff" in text:
                    text = text.replace("initial diff", "+fix diff")
                    p.write_text(text, encoding="utf-8")
                elif "<!-- BEGIN_GIT_DIFF -->" in text:
                    if "+fix" not in text:
                        text = text.replace("<!-- BEGIN_GIT_DIFF -->", "<!-- BEGIN_GIT_DIFF -->\n+fix")
                        p.write_text(text, encoding="utf-8")
                return {"status": "complete", "output": "ok"}

        # Real QA with PreciseRouter: FAILED, FAILED, PASSED - increments via qa_engine's set_qa_feedback
        from qa_engine import QAEngine

        class PreciseRouter:
            def __init__(self):
                self.qa_calls = 0
            def route_qa(self, tc, diff):
                return {"kind": "qa"}
            def route_review(self, tc, qr):
                return {"kind": "review"}
            def call_llm(self, routing):
                kind = routing.get("kind")
                if kind == "qa":
                    self.qa_calls += 1
                    if self.qa_calls <= 2:
                        return "FAILED: still broken" if self.qa_calls == 1 else "FAILED: second fail"
                    else:
                        return "PASSED: ok"
                else:
                    return "APPROVED"

        precise_router = PreciseRouter()
        real_qa = QAEngine(cfg, sm, precise_router)

        class TrackGateway:
            def __init__(self):
                self.calls = []
            async def request_approval(self, tid, title, content):
                self.calls.append(title)
                return True

        gw = TrackGateway()

        async def run_with_timeout():
            await asyncio.wait_for(
                _reimplement_task(tid, str(task_file), "FAILED: initial", cfg, sm, precise_router, gw, StubExecutor(), real_qa),
                timeout=5.0
            )

        asyncio.run(run_with_timeout())

        # Retry count strictly increases: 0->1->2 then PASSED stays 2
        final_count = sm.get_qa_retry_count(tid)
        assert final_count == 2, f"expected final retry count 2, got {final_count}"
        assert precise_router.qa_calls == 3, f"expected 3 QA calls, got {precise_router.qa_calls}"
        assert gw.calls.count("Closure Approval") == 1, f"Closure calls: {gw.calls}"
        assert gw.calls.count("Plan Approval") == 0, f"Plan should be 0, got {gw.calls}"
        task = sm.get_task(tid)
        assert task["state"] == "closed", f"expected closed, got {task['state']}"
        sm.close()
    patcher.stop()


def test_reimplement_task_max_one_crashes_with_timeout():
    """Step 3: max=1 always FAILED → CRASHED, with hard wall-clock timeout guard."""
    from unittest.mock import patch
    from daemon import _reimplement_task
    from state import StateMachine
    # Mock toolchain to avoid real lint/test execution interfering with retry-loop test
    patcher = patch('daemon.ToolchainRunner', None)
    patcher.start()

    with tempfile.TemporaryDirectory() as tmp:
        task_file = Path(tmp) / "03-max1.md"
        task_file.write_text("# Task\nSimple no trigger\n<!-- BEGIN_GIT_DIFF -->\ninitial\n<!-- END_GIT_DIFF -->", encoding="utf-8")

        cfg = LoopEngineConfig(approval={"chat_id": 1},
                               evidence_dir=os.path.join(tmp, "evidence"),
                               max_qa_retries=1)
        sm = StateMachine(os.path.join(tmp, "t.db"))
        tid = sm.register_task(str(task_file), TaskState.BACKLOG)
        assert sm.get_qa_retry_count(tid) == 0

        class StubExecutor:
            async def execute(self, task_id, task_file, task_content, blueprint_context="", qa_feedback=""):
                return {"status": "complete", "output": "ok"}

        from qa_engine import QAEngine

        class AlwaysFailRouter:
            def route_qa(self, tc, diff):
                return {"kind": "qa"}
            def route_review(self, tc, qr):
                return {"kind": "review"}
            def call_llm(self, routing):
                return "FAILED: always"

        always_router = AlwaysFailRouter()
        real_qa = QAEngine(cfg, sm, always_router)

        class NoopGateway:
            async def request_approval(self, tid, title, content):
                assert False, "gateway should not be called on CRASHED path"

        # Hard wall-clock timeout guard: 5 seconds — infinite loop fails loudly
        async def run_guarded():
            await asyncio.wait_for(
                _reimplement_task(tid, str(task_file), "FAILED: initial", cfg, sm, always_router, NoopGateway(), StubExecutor(), real_qa),
                timeout=5.0
            )

        try:
            asyncio.run(run_guarded())
        except asyncio.TimeoutError:
            assert False, "test timed out — infinite loop not terminating (retry increment missing?)"

        task = sm.get_task(tid)
        assert task["state"] == "crashed", f"expected crashed with max=1, got {task['state']}"
        sm.close()
    patcher.stop()


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS: {t.__name__}")
            passed += 1
        except Exception as e:
            import traceback
            print(f"  FAIL: {t.__name__}: {e}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
