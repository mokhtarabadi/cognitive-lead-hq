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
from stacks import StackRegistry, StackDetector, PreflightRunner

try:
    from verifier import ToolchainRunner
except ImportError:
    ToolchainRunner = None  # type: ignore

try:
    from contracts import ContractPropagationEngine
except ImportError:
    ContractPropagationEngine = None  # type: ignore

try:
    from specs import SpecGateEngine
except ImportError:
    SpecGateEngine = None  # type: ignore

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


def extract_task_diff(task_file: Path) -> str | None:
    """Extract ONLY the content between <!-- BEGIN_GIT_DIFF --> and <!-- END_GIT_DIFF -->.

    Reads the updated task file post-execution. Returns stripped diff content,
    or None if markers are missing/malformed. Empty stripped content is treated
    as missing evidence by the caller.
    """
    try:
        text = task_file.read_text(encoding="utf-8")
    except Exception:
        return None
    begin = "<!-- BEGIN_GIT_DIFF -->"
    end = "<!-- END_GIT_DIFF -->"
    if begin not in text or end not in text:
        return None
    start = text.index(begin) + len(begin)
    stop = text.index(end, start)
    if stop < start:
        return None
    diff = text[start:stop].strip()
    return diff


async def _execute_and_qa(
    task_id: int,
    task_file: str,
    task_content: str,
    task_path: Path,
    state: StateMachine,
    executor: HandsExecutor,
    qa: QAEngine,
    *,
    blueprint_context: str = "",
    qa_feedback: str = "",
    log_prefix: str = "pipeline",
    stack_profile=None,
) -> dict | None:
    """Shared helper for execute → status check → diff extract → QA.

    DRY extraction of the sequence duplicated in _process_task and _reimplement_task.
    Uses existing retry counter, no parallel counter. Returns qa_result dict on
    success (whether PASSED or FAILED), or None if the task was transitioned to
    CRASHED (executor blocked/error or empty diff). Caller decides FAILED retry vs
    PASSED progression. No behavior change, pure deduplication.
    """
    kwargs = {}
    if stack_profile is not None:
        kwargs["stack_profile"] = stack_profile
    try:
        result = await executor.execute(
            task_id, task_file, task_content,
            blueprint_context=blueprint_context, qa_feedback=qa_feedback,
            **kwargs,
        )
    except TypeError as e:
        if "stack_profile" in str(e) and kwargs:
            # Fallback for legacy executors / stubs that don't yet accept stack_profile
            result = await executor.execute(
                task_id, task_file, task_content,
                blueprint_context=blueprint_context, qa_feedback=qa_feedback,
            )
        else:
            raise
    print(f"[{log_prefix}] Execution result: {result['status']}")

    if result["status"] == EXEC_BLOCKED:
        state.update_state(task_id, TaskState.CRASHED)
        print(f"[{log_prefix}] Task #{task_id} crashed: {result['status']}")
        return None

    if result["status"] != EXEC_OK:
        state.update_state(task_id, TaskState.CRASHED)
        print(
            f"[{log_prefix}] Task #{task_id} crashed: executor status "
            f"'{result['status']}': {result.get('error', '')[:200]}"
        )
        return None

    diff = extract_task_diff(task_path)
    if not diff or not diff.strip():
        state.update_state(task_id, TaskState.CRASHED)
        print(
            f"[{log_prefix}] Empty or missing diff for task #{task_id} "
            f"(markers missing/malformed or diff empty) — crashing, no evidence"
        )
        return None

    # --- Toolchain verification (LE-2) — deterministic lint/build/test before LLM QA ---
    if ToolchainRunner is not None:
        # Resolve evidence base from QA engine config if available
        try:
            evidence_base_dir = qa.config.evidence_dir if hasattr(qa, "config") and hasattr(qa.config, "evidence_dir") else str(qa.evidence_dir) if hasattr(qa, "evidence_dir") else "loop-engine/evidence"
        except Exception:
            evidence_base_dir = "loop-engine/evidence"
        # Determine profile: use provided stack_profile or fallback to generic no-op
        effective_profile = stack_profile
        if effective_profile is None:
            # Try to create a synthetic generic profile (all toolchain null) to avoid None errors
            try:
                from models import StackProfileConfig
                from stacks import StackProfile as _SP
                effective_profile = _SP(StackProfileConfig(name="generic", display_name="Generic"))
            except Exception:
                effective_profile = stack_profile
        try:
            runner = ToolchainRunner(timeout_per_command=120.0, evidence_base_dir=evidence_base_dir)
            toolchain_result = await runner.run(
                effective_profile, task_id=task_id, cwd=REPO_ROOT, diff_text=diff
            )
            if not toolchain_result.passed:
                # Fail-fast: record feedback, bypass LLM QA, return FAILED for retry logic
                try:
                    state.set_qa_feedback(task_id, toolchain_result.report_md)
                except Exception:
                    pass
                print(f"[{log_prefix}] Toolchain verification FAILED for task #{task_id}")
                print(toolchain_result.summary)
                return {
                    "result": "FAILED",
                    "report": toolchain_result.report_md,
                    "evidence_dir": str(Path(evidence_base_dir) / str(task_id)),
                }
            # Success: forward summary as evidence to QA
            toolchain_evidence = toolchain_result.summary
        except Exception as e:
            # Toolchain infra error — treat as CRASHED? For now, log and proceed to QA to avoid blocking
            print(f"[{log_prefix}] Toolchain runner error (proceeding to QA): {e}")
            toolchain_evidence = ""
    else:
        toolchain_evidence = ""

    state.update_state(task_id, TaskState.QA)
    print(f"[{log_prefix}] Running QA for task #{task_id}...")
    # Forward toolchain evidence if available (LE-2 enrichment)
    try:
        qa_result = qa.run_qa(task_id, task_content, diff, toolchain_evidence=toolchain_evidence)
    except TypeError:
        # Fallback for legacy QA stubs without toolchain_evidence param
        qa_result = qa.run_qa(task_id, task_content, diff)
    print(f"[{log_prefix}] QA result: {qa_result['result']}")
    return qa_result


async def _reimplement_task(
    task_id: int,
    task_file: str,
    initial_qa_feedback: str,
    config: LoopEngineConfig,
    state: StateMachine,
    router: LLMRouter,
    gateway: ApprovalGateway,
    executor: HandsExecutor,
    qa: QAEngine,
) -> None:
    """Scoped retry loop — implementation-only, no brainstorm or plan re-approval.

    Called after an initial QA FAILED. Loops up to config.max_qa_retries,
    using state.get_qa_retry_count() as the single source of truth (no parallel
    counter). Each iteration:
      1. executor.execute() with qa_feedback as DISTINCT param (never blueprint_context)
      2. extract_task_diff() per LE-0.2 logic
      3. qa.run_qa()
    On QA PASSED, proceeds to REVIEW → AWAITING_CLOSURE (same as main pipeline).
    On QA FAILED, loops again or CRASHED when limit hit. Never sends a new
    Telegram plan-approval message.
    """
    current_feedback = initial_qa_feedback
    while True:
        retries = state.get_qa_retry_count(task_id)
        if retries >= config.max_qa_retries:
            state.update_state(task_id, TaskState.CRASHED)
            print(
                f"[reimplement] Max QA retries ({config.max_qa_retries}) "
                f"reached for task #{task_id} — crashing"
            )
            return

        # Fresh read — captures prior Hands edits and QA feedback appended to file
        try:
            task_content = Path(task_file).read_text(encoding="utf-8")
        except Exception as e:
            state.update_state(task_id, TaskState.CRASHED)
            print(f"[reimplement] Failed to re-read task file for #{task_id}: {e}")
            return

        task_path = Path(task_file)
        state.update_state(task_id, TaskState.IMPLEMENTING)
        print(
            f"[reimplement] Retrying implementation for task #{task_id} "
            f"(retry {retries + 1}/{config.max_qa_retries})..."
        )

        # Stack detection + preflight (LE-1)
        registry = StackRegistry(config.stacks_dir, repo_root=REPO_ROOT)
        profile = StackDetector.detect(task_content, REPO_ROOT, registry, default_stack=config.default_stack)
        print(f"[reimplement] Detected stack: {profile.name} ({profile.display_name})")
        runner = PreflightRunner(timeout_seconds=30.0)
        preflight = await runner.run(profile, cwd=REPO_ROOT)
        if not preflight.passed:
            state.update_state(task_id, TaskState.CRASHED)
            diag = "; ".join(preflight.errors)
            print(f"[reimplement] Preflight failed for stack {profile.name}: {diag} — crashing")
            try:
                state.set_qa_feedback(task_id, f"Preflight failed for stack {profile.name}: {diag}")
            except Exception:
                pass
            return

        qa_result = await _execute_and_qa(
            task_id, task_file, task_content, task_path, state, executor, qa,
            qa_feedback=current_feedback, log_prefix="reimplement", stack_profile=profile
        )
        if qa_result is None:
            return

        if qa_result["result"] == "FAILED":
            # qa.run_qa already incremented retry count via set_qa_feedback
            current_feedback = (
                qa_result.get("report", "") or qa_result.get("feedback", "") or current_feedback
            )
            continue

        # QA PASSED — proceed to REVIEW and CLOSURE (mirrors main pipeline steps 5-6)
        state.update_state(task_id, TaskState.REVIEW)
        review = qa.run_review(task_id, task_content, qa_result.get("report", ""),
                               stack_profile=profile)
        print(f"[reimplement] Review result: {review['result']}")

        if review["result"] == "REJECTED":
            state.update_state(task_id, TaskState.CRASHED)
            return

        state.update_state(task_id, TaskState.AWAITING_CLOSURE)
        approved = await gateway.request_approval(
            task_id, "Closure Approval", f"Task #{task_id} complete. Approve closure?"
        )
        if approved:
            state.update_state(task_id, TaskState.CLOSED)
            print(f"[reimplement] Task #{task_id} CLOSED after retry.")

            # --- Contract Propagation (LE-6) — dispatch downstream tasks ---
            diff = extract_task_diff(task_path) or ""
            if ContractPropagationEngine is not None:
                propagation_engine = ContractPropagationEngine(
                    config.contract_rules, tasks_dir=config.tasks_dir
                )
                dispatched = propagation_engine.process_task_closure(
                    task_id, task_file, diff, REPO_ROOT, state
                )
                if dispatched:
                    print(f"[pipeline] Contract propagation dispatched {len(dispatched)} downstream task(s):")
                    for d in dispatched:
                        print(f"  - Task #{d['task_id']}: {d['title']} ({d['file']})")
        else:
            print(
                f"[reimplement] Closure rejected for task #{task_id} after retry. Stays in review."
            )
        return


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
        self.stack_registry = StackRegistry(config.stacks_dir, repo_root=REPO_ROOT)
        self.propagation_engine = (
            ContractPropagationEngine(config.contract_rules, tasks_dir=config.tasks_dir)
            if ContractPropagationEngine is not None
            else None
        )

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

    # Stack detection (LE-1) — detect once at the start so planning, QA, and
    # review all share the same profile for stack-aware model routing (LE-3).
    registry = StackRegistry(config.stacks_dir, repo_root=REPO_ROOT)
    profile = StackDetector.detect(task_content, REPO_ROOT, registry, default_stack=config.default_stack)
    print(f"[pipeline] Detected stack: {profile.name} ({profile.display_name})")

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
    try:
        routing = router.route_plan(task_content, extra_context=extra_context,
                                    stack_profile=profile)
    except TypeError:
        # Fallback for legacy routers/stubs without stack_profile param
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

    # 2.5 SPEC-FIRST GATE (LE-8) — after Plan Approval, before IMPLEMENTING.
    # Architectural / contract / schema tasks must have verified spec artifacts
    # (ADR, PRD, Contract, Data Model) in the workspace or staged diff, otherwise
    # the task crashes BEFORE any code is generated.
    if SpecGateEngine is not None and config.spec_gate.enabled:
        spec_engine = SpecGateEngine(config.spec_gate)
        rules = spec_engine.evaluate_requirements(task_content, plan)
        if rules:
            spec_res = spec_engine.validate_artifacts(rules, REPO_ROOT, diff_text="")
            if not spec_res.passed:
                state.update_state(task_id, TaskState.CRASHED)
                try:
                    state.set_qa_feedback(task_id, spec_res.report_md)
                except Exception:
                    pass
                print(
                    f"[pipeline] Spec Gate FAILED for task #{task_id}: "
                    f"{'; '.join(spec_res.errors)} — crashing"
                )
                return
            state.set_spec_artifacts(task_id, spec_res.found_artifacts)
            print(
                f"[pipeline] Spec Gate PASSED for task #{task_id}: verified "
                f"{len(spec_res.found_artifacts)} artifact(s)"
            )

    # 3. IMPLEMENTING — preflight (profile already detected at pipeline start)
    state.update_state(task_id, TaskState.IMPLEMENTING)
    print(f"[pipeline] Implementing task #{task_id}...")
    runner = PreflightRunner(timeout_seconds=30.0)
    preflight = await runner.run(profile, cwd=REPO_ROOT)
    if not preflight.passed:
        state.update_state(task_id, TaskState.CRASHED)
        diag = "; ".join(preflight.errors)
        print(f"[pipeline] Preflight failed for stack {profile.name}: {diag} — crashing")
        try:
            state.set_qa_feedback(task_id, f"Preflight failed for stack {profile.name}: {diag}")
        except Exception:
            pass
        return
    qa_result = await _execute_and_qa(
        task_id, task_file, task_content, task_path, state, executor, qa,
        blueprint_context=plan, log_prefix="pipeline", stack_profile=profile
    )
    if qa_result is None:
        return

    if qa_result["result"] == "FAILED":
        qa_feedback = qa_result.get("report", "") or ""
        return await _reimplement_task(
            task_id, task_file, qa_feedback, config, state, router, gateway, executor, qa
        )

    # 5. REVIEW
    state.update_state(task_id, TaskState.REVIEW)
    review = qa.run_review(task_id, task_content, qa_result.get("report", ""),
                           stack_profile=profile)
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

        # --- Contract Propagation (LE-6) — dispatch downstream tasks ---
        diff = extract_task_diff(task_path) or ""
        if ContractPropagationEngine is not None:
            propagation_engine = ContractPropagationEngine(
                config.contract_rules, tasks_dir=config.tasks_dir
            )
            dispatched = propagation_engine.process_task_closure(
                task_id, task_file, diff, REPO_ROOT, state
            )
            if dispatched:
                print(f"[pipeline] Contract propagation dispatched {len(dispatched)} downstream task(s):")
                for d in dispatched:
                    print(f"  - Task #{d['task_id']}: {d['title']} ({d['file']})")
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
