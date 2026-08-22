"""
Cognitive Loop Engine — Main Daemon Entry Point.

Orchestrates: Watcher -> Router -> Gateway -> Executor -> QA -> State
Runs as: uv run loop-engine/daemon.py
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Add loop-engine to path for local imports
sys.path.insert(0, str(Path(__file__).parent))

from models import LoopEngineConfig, TaskState
from state import StateMachine
from watcher import KanbanWatcher
from router import LLMRouter
from gateway import ApprovalGateway
from executor import HandsExecutor
from qa_engine import QAEngine


def load_config(config_path: str = "loop-engine/loop-engine.jsonc") -> LoopEngineConfig:
    """Load config from JSONC file (strip comments)."""
    p = Path(config_path)
    if not p.exists():
        # Use defaults
        return LoopEngineConfig(approval={"chat_id": 0})

    raw = p.read_text(encoding="utf-8")
    # Strip // and /* */ comments for JSONC compatibility
    import re
    raw = re.sub(r'//.*$', '', raw, flags=re.MULTILINE)
    raw = re.sub(r'/\*.*?\*/', '', raw, flags=re.DOTALL)
    # Strip trailing commas
    raw = re.sub(r',\s*([}\]])', r'\1', raw)
    # Strip env var refs: ${VAR_NAME} -> os.environ
    raw = re.sub(r'\$\{(\w+)\}', lambda m: os.environ.get(m.group(1), ''), raw)

    data = json.loads(raw)
    return LoopEngineConfig(**data)


async def process_task(task_id: int, task_file: str, config: LoopEngineConfig,
                       state: StateMachine, router: LLMRouter,
                       gateway: ApprovalGateway, executor: HandsExecutor,
                       qa: QAEngine):
    """Full pipeline for one task."""
    print(f"\n[pipeline] Processing task #{task_id}: {task_file}")

    task_path = Path(task_file)
    task_content = task_path.read_text(encoding="utf-8")

    # 1. PLANNING
    state.update_state(task_id, TaskState.PLANNING)
    print(f"[pipeline] Planning task #{task_id}...")
    routing = router.route_plan(task_content)
    plan = router.call_llm(routing)
    state.set_plan(task_id, plan)

    # 2. AWAITING_APPROVAL (Plan)
    state.update_state(task_id, TaskState.AWAITING_APPROVAL)
    approved = await gateway.request_approval(task_id, "Plan Approval", plan)
    if not approved:
        state.update_state(task_id, TaskState.BACKLOG)
        print(f"[pipeline] Plan rejected for task #{task_id}. Back to backlog.")
        return

    # 3. IMPLEMENTING
    state.update_state(task_id, TaskState.IMPLEMENTING)
    print(f"[pipeline] Implementing task #{task_id}...")
    result = await executor.execute(task_id, task_file, task_content)
    print(f"[pipeline] Execution result: {result['status']}")

    if result["status"] in ("blocked", "no_progress", "idle_stuck", "budget_exceeded"):
        state.update_state(task_id, TaskState.CRASHED)
        print(f"[pipeline] Task #{task_id} crashed: {result['status']}")
        return

    # 4. QA
    state.update_state(task_id, TaskState.QA)
    print(f"[pipeline] Running QA for task #{task_id}...")
    qa_result = qa.run_qa(task_id, task_content, result.get("output", ""))
    print(f"[pipeline] QA result: {qa_result['result']}")

    if qa_result["result"] == "FAILED":
        retries = state.get_qa_retry_count(task_id)
        if retries >= config.max_qa_retries:
            state.update_state(task_id, TaskState.CRASHED)
            print(f"[pipeline] Max QA retries reached for task #{task_id}")
            return
        # Stay in QA — same task file, re-execute with feedback
        state.update_state(task_id, TaskState.IMPLEMENTING)
        return await process_task(task_id, task_file, config, state, router,
                                  gateway, executor, qa)

    # 5. REVIEW
    state.update_state(task_id, TaskState.REVIEW)
    review = qa.run_review(task_id, task_content, qa_result.get("report", ""))
    print(f"[pipeline] Review result: {review['result']}")

    if review["result"] == "REJECTED":
        state.update_state(task_id, TaskState.CRASHED)
        return

    # 6. AWAITING_CLOSURE
    state.update_state(task_id, TaskState.AWAITING_CLOSURE)
    approved = await gateway.request_approval(task_id, "Closure Approval",
                                               f"Task #{task_id} complete. Approve closure?")
    if approved:
        state.update_state(task_id, TaskState.CLOSED)
        print(f"[pipeline] Task #{task_id} CLOSED.")
    else:
        print(f"[pipeline] Closure rejected for task #{task_id}. Stays in review.")


async def main():
    """Main loop: watch -> process -> repeat."""
    print("=" * 60)
    print("  Cognitive Loop Engine — Starting...")
    print("=" * 60)

    config = load_config()
    state = StateMachine()
    router = LLMRouter(config)
    gateway = ApprovalGateway(config)
    executor = HandsExecutor(config, state)
    qa = QAEngine(config, state, router)

    def on_task_detected(task_id: int, task_file: str):
        asyncio.ensure_future(
            process_task(task_id, task_file, config, state, router,
                         gateway, executor, qa))

    watcher = KanbanWatcher(state, on_task_detected=on_task_detected)
    existing = watcher.scan_existing()
    watcher.start()

    print(f"[daemon] Found {len(existing)} existing tasks in backlog.")
    print("[daemon] Watching for new tasks... Press Ctrl+C to stop.")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n[daemon] Shutting down...")
        watcher.stop()
        state.close()


if __name__ == "__main__":
    asyncio.run(main())
