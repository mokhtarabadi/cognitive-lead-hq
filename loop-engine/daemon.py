"""
Cognitive Loop Engine — Main Daemon Entry Point.

Orchestrates: Watcher -> Router -> Gateway -> Executor -> QA -> State
Runs as: uv run loop-engine/daemon.py

Task Entry Trigger Gate:
- trigger_mode="auto": legacy auto-pickup (no admin gate).
- trigger_mode="telegram_button"|"command_only": tasks register as PENDING_TRIGGER.
- auto_start_on_boot: if True, existing backlog tasks run immediately on boot.
- CLI: python daemon.py --run <task_id> to trigger a specific staged task.
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
from brainstorm import BrainstormStage

# Repo root = parent of loop-engine/. All relative paths in the config
# (state db, evidence dir, tasks/, system-prompt.md) are anchored here so the
# daemon behaves identically no matter which directory it is launched from.
REPO_ROOT = Path(__file__).resolve().parent.parent


def strip_jsonc(raw: str) -> str:
    """Strip JSONC comments (quote-aware), trailing commas, and resolve ${VAR} refs.

    Quote-aware comment stripping prevents corruption of string values that
    contain '//' (e.g. https:// URLs).
    """
    import re

    # 1. Remove /* */ block comments (quote-aware scan)
    out = []
    i, n = 0, len(raw)
    in_string = False
    while i < n:
        c = raw[i]
        if in_string:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(raw[i + 1])
                i += 2
                continue
            if c == '"':
                in_string = False
            i += 1
            continue
        if c == '"':
            in_string = True
            out.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < n and raw[i + 1] == "*":
            end = raw.find("*/", i + 2)
            i = n if end == -1 else end + 2
            continue
        if c == "/" and i + 1 < n and raw[i + 1] == "/":
            end = raw.find("\n", i)
            i = n if end == -1 else end
            continue
        out.append(c)
        i += 1
    stripped = "".join(out)

    # 2. Strip trailing commas
    stripped = re.sub(r',\s*([}\]])', r'\1', stripped)
    # 3. Resolve env var refs: ${VAR_NAME} -> os.environ
    stripped = re.sub(r'\$\{(\w+)\}', lambda m: os.environ.get(m.group(1), ''), stripped)
    return stripped


def load_config(config_path: str = "loop-engine/loop-engine.jsonc") -> LoopEngineConfig:
    """Load config from JSONC file (strip comments)."""
    p = Path(config_path)
    if not p.is_absolute():
        p = REPO_ROOT / config_path
    if not p.exists():
        # Use defaults
        return LoopEngineConfig(approval={"chat_id": 0})

    data = json.loads(strip_jsonc(p.read_text(encoding="utf-8")))
    return LoopEngineConfig(**data)


# Executor statuses that mean the Hands session did NOT produce work.
# Anything outside EXEC_OK / EXEC_BLOCKED must crash the task, never reach QA.
EXEC_OK = "complete"
EXEC_BLOCKED = "blocked"


async def process_task(task_id: int, task_file: str, config: LoopEngineConfig,
                       state: StateMachine, router: LLMRouter,
                       gateway: ApprovalGateway, executor: HandsExecutor,
                       qa: QAEngine, brainstorm: BrainstormStage):
    """Full pipeline for one task."""
    print(f"\n[pipeline] Processing task #{task_id}: {task_file}")

    try:
        await _process_task(task_id, task_file, config, state, router,
                            gateway, executor, qa, brainstorm)
    except Exception as e:
        state.update_state(task_id, TaskState.CRASHED)
        print(f"[pipeline] Task #{task_id} crashed with unexpected error: {e}")


class LoopEngineDaemon:
    """Encapsulates daemon state and provides trigger_task() for the gateway."""

    def __init__(self, config, state, router, gateway, executor, qa, brainstorm):
        self.config = config
        self.state = state
        self.router = router
        self.gateway = gateway
        self.executor = executor
        self.qa = qa
        self.brainstorm = brainstorm

    async def trigger_task(self, task_id: int) -> None:
        """Trigger execution of a PENDING_TRIGGER task.

        Fresh Read Guarantee: re-reads the task file from disk so any
        manual edits/refinements are captured before processing.
        """
        task_record = self.state.get_task(task_id)
        if not task_record:
            print(f"[daemon] Task #{task_id} not found in state machine.")
            return

        task_file = task_record["task_file"]

        # Fresh read from disk
        from pathlib import Path
        task_path = Path(task_file)
        if not task_path.exists():
            print(f"[daemon] Task file not found: {task_file}")
            self.state.update_state(task_id, TaskState.CRASHED)
            return

        # Transition PENDING_TRIGGER -> PLANNING
        self.state.update_state(task_id, TaskState.PLANNING)
        print(f"[daemon] Task #{task_id} triggered, transitioning to PLANNING...")

        # Launch processing
        asyncio.create_task(
            process_task(task_id, task_file, self.config, self.state,
                         self.router, self.gateway, self.executor,
                         self.qa, self.brainstorm))

    async def boot_scan(self) -> list[dict]:
        """Scan existing backlog tasks on boot.

        If auto_start_on_boot=True: register as BACKLOG and auto-process.
        If auto_start_on_boot=False: register as PENDING_TRIGGER.
        """
        from watcher import KanbanWatcher
        watcher = KanbanWatcher(self.state, self.config, self.gateway)

        if self.config.auto_start_on_boot:
            # Legacy: auto-process existing tasks
            existing = watcher.scan_existing()
            for t in existing:
                asyncio.create_task(
                    process_task(t["task_id"], t["file"], self.config,
                                 self.state, self.router, self.gateway,
                                 self.executor, self.qa, self.brainstorm))
            return existing
        else:
            # Trigger gate: register as PENDING_TRIGGER, send trigger cards
            existing = watcher.scan_existing()
            for t in existing:
                from pathlib import Path
                title = Path(t["file"]).stem
                await self.gateway.send_task_trigger_card(
                    t["task_id"], title, t["file"])
            return existing


async def _process_task(task_id: int, task_file: str, config: LoopEngineConfig,
                        state: StateMachine, router: LLMRouter,
                        gateway: ApprovalGateway, executor: HandsExecutor,
                        qa: QAEngine, brainstorm: BrainstormStage):
    """Inner pipeline — exceptions propagate to process_task's guard."""
    task_path = Path(task_file)
    task_content = task_path.read_text(encoding="utf-8")

    # 0. BRAINSTORMING (Phase 1.5) — optional pre-planning stage
    extra_context = ""
    if brainstorm.should_trigger(task_content):
        state.update_state(task_id, TaskState.PLANNING)
        print(f"[pipeline] Brainstorming triggered for task #{task_id} "
              f"(six-persona swarm)...")
        session = await brainstorm.run(task_content)
        approved = await gateway.request_approval(
            task_id, "Brainstorm Review", session["session"])
        if not approved:
            state.update_state(task_id, TaskState.BACKLOG)
            print(f"[pipeline] Brainstorm rejected for task #{task_id}. "
                  f"Back to backlog.")
            return
        extra_context = session["session"]

    # 1. PLANNING
    state.update_state(task_id, TaskState.PLANNING)
    print(f"[pipeline] Planning task #{task_id}...")
    routing = router.route_plan(task_content, extra_context=extra_context)
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

    if result["status"] == EXEC_BLOCKED:
        state.update_state(task_id, TaskState.CRASHED)
        print(f"[pipeline] Task #{task_id} crashed: {result['status']}")
        return

    if result["status"] != EXEC_OK:
        # timeout / error / transport_error — no usable output, never send to QA
        state.update_state(task_id, TaskState.CRASHED)
        print(f"[pipeline] Task #{task_id} crashed: executor status "
              f"'{result['status']}': {result.get('error', '')[:200]}")
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
                                  gateway, executor, qa, brainstorm)

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
    import argparse

    # CLI argument parsing
    parser = argparse.ArgumentParser(description="Cognitive Loop Engine Daemon")
    parser.add_argument("--run", type=int, metavar="TASK_ID",
                        help="Trigger and run a specific staged task by ID")
    args = parser.parse_args()

    # Anchor all relative paths (config, state db, tasks/, evidence) to repo root
    os.chdir(REPO_ROOT)

    print("=" * 60)
    print("  Cognitive Loop Engine — Starting...")
    print("=" * 60)

    config = load_config()
    state = StateMachine()
    router = LLMRouter(config)
    gateway = ApprovalGateway(config)
    executor = HandsExecutor(config, state)
    qa = QAEngine(config, state, router)
    brainstorm = BrainstormStage(config, router, workspace_root=str(REPO_ROOT))

    # Create daemon instance
    daemon = LoopEngineDaemon(config, state, router, gateway, executor, qa, brainstorm)

    # Wire up gateway <-> daemon and gateway <-> state
    gateway.set_daemon(daemon)
    gateway.set_state(state)

    # CLI --run mode: trigger a specific task and exit
    if args.run is not None:
        print(f"[daemon] CLI trigger: task #{args.run}")
        await daemon.trigger_task(args.run)
        # Keep alive briefly for the task to start
        await asyncio.sleep(2)
        return

    # Normal daemon mode: boot scan + watch
    existing = await daemon.boot_scan()
    print(f"[daemon] Found {len(existing)} existing tasks in backlog "
          f"(trigger_mode={config.trigger_mode}, "
          f"auto_start_on_boot={config.auto_start_on_boot}).")

    # Start filesystem watcher
    loop = asyncio.get_running_loop()

    def on_task_detected(task_id: int, task_file: str):
        if config.trigger_mode == "auto":
            asyncio.run_coroutine_threadsafe(
                process_task(task_id, task_file, config, state, router,
                             gateway, executor, qa, brainstorm), loop)
        else:
            # Register as PENDING_TRIGGER and send card
            state.update_state(task_id, TaskState.PENDING_TRIGGER)
            asyncio.run_coroutine_threadsafe(
                gateway.send_task_trigger_card(task_id, task_file.split("/")[-1], task_file),
                loop)

    watcher = KanbanWatcher(state, config, gateway, on_task_detected=on_task_detected)
    watcher.start()

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
