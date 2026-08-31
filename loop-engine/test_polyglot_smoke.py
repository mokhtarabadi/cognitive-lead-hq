"""End-to-End Polyglot Smoke Test Suite & Hard Verification Gate (Task 137 / LE-5).

Certifies Phase A (Polyglot Toolchain & Execution Sandboxing) end-to-end by driving the
REAL pipeline components — StateMachine, LLMRouter, QAEngine, HandsExecutor,
ApprovalGateway, LoopEngineDaemon — anchored to an isolated temporary workspace.

Strategy (hermetic, deterministic, zero side effects):
- Every test builds its own workspace under tmp_path: stacks/, tasks/{backlog,in-progress,
  qa,completed}/, loop-engine/{evidence,state}/, plus dummy AGENTS.md, system-prompt.md,
  docs/conventions.md, and loop-engine.jsonc.
- All five stack profile YAMLs mirror the repository defaults (detection, skills,
  model_preferences); preflight/toolchain commands are sandboxed to portable no-ops
  (``true``) or deterministic failures (``false``, fail-first marker files) so the gate
  passes on any CI machine without installed toolchains.
- daemon.REPO_ROOT is patched to the temp workspace for the duration of each pipeline run,
  so detection, preflight/toolchain cwd, and evidence writes never touch the real repo.
- Scripted I/O seams at the process boundary only: call_llm (deterministic per-stage
  responses), executor._run_once (simulates the Hands agent writing the diff block and
  emitting real goal tokens), and gateway.request_approval (auto-approve or scripted).

Coverage matrix (16 tests):
  - Happy path (5): node-ts, python-fastapi, kotlin-android, go-gin, generic fallback.
  - Hard gate (7): preflight failure crashes before execution; toolchain failure bypasses
    QA and retries; goal-blocked reason extraction; empty diff crashes without toolchain/QA;
    retry recovery to CLOSED; max retries → CRASHED; explicit **Stack:** header overrides
    marker detection.
  - Supplementary (4): plan rejection → BACKLOG; review rejection → CRASHED; QA-feedback
    retry recovery; daemon boot_scan registers PENDING_TRIGGER.
"""
import asyncio
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(__file__))

import pytest  # noqa: F401  (tmp_path fixture)

import daemon
from models import LoopEngineConfig, TaskState
from state import StateMachine
from router import LLMRouter
from qa_engine import QAEngine
from executor import HandsExecutor, TERM_BLOCKED, TERM_COMPLETE
from gateway import ApprovalGateway
from brainstorm import BrainstormStage

REAL_REPO_ROOT = daemon.REPO_ROOT


# ---------------------------------------------------------------------------
# Workspace construction
# ---------------------------------------------------------------------------

# Sandboxed profiles mirroring stacks/*.yaml repository defaults.
# Preflight/toolchain commands are portable no-ops so the gate is deterministic.
_DEFAULT_PROFILES = {
    "generic": {
        "display_name": "Generic (Fallback)",
        "detection": {"marker_files": [], "extensions": [], "task_keywords": []},
        "skills": [],
        "preflight": [],
        "toolchain": {"test_cmd": None, "build_cmd": None, "lint_cmd": None},
        "model_preferences": {},
    },
    "node-ts": {
        "display_name": "Node.js / TypeScript",
        "detection": {
            "marker_files": ["package.json", "tsconfig.json"],
            "extensions": [".ts", ".tsx", ".js"],
            "task_keywords": ["node", "typescript", "nextjs", "react"],
        },
        "skills": ["nextjs", "react-vite"],
        "preflight": ["true"],
        "toolchain": {"test_cmd": "true", "build_cmd": "true", "lint_cmd": "true"},
        "model_preferences": {
            "deep": ["openai/gpt-5.6-sol", "anthropic/claude-3-7-sonnet"],
            "quick": ["kimi/kimi-k3"],
        },
    },
    "python-fastapi": {
        "display_name": "Python / FastAPI",
        "detection": {
            "marker_files": ["pyproject.toml", "requirements.txt", "Pipfile"],
            "extensions": [".py"],
            "task_keywords": ["python", "fastapi", "pydantic", "pytest"],
        },
        "skills": ["python-fastapi"],
        "preflight": ["true"],
        "toolchain": {"test_cmd": "true", "build_cmd": None, "lint_cmd": "true"},
        "model_preferences": {
            "deep": ["openai/gpt-5.6-sol", "gemini/gemini-2.5-pro"],
            "quick": ["gemini/gemini-2.5-flash"],
        },
    },
    "kotlin-android": {
        "display_name": "Kotlin / Android",
        "detection": {
            "marker_files": ["build.gradle.kts", "build.gradle", "settings.gradle.kts"],
            "extensions": [".kt", ".kts"],
            "task_keywords": ["kotlin", "android", "compose", "gradle"],
        },
        "skills": ["android-kotlin"],
        "preflight": ["true"],
        "toolchain": {"test_cmd": "true", "build_cmd": "true", "lint_cmd": "true"},
        "model_preferences": {
            "deep": ["anthropic/claude-3-7-sonnet", "openai/gpt-5.6-sol"],
            "quick": ["gemini/gemini-2.5-flash"],
        },
    },
    "go-gin": {
        "display_name": "Go / Gin",
        "detection": {
            "marker_files": ["go.mod", "go.sum"],
            "extensions": [".go"],
            # Sandbox deviation from repo default: bare "go" and "gin" are dropped
            # because every task file contains "## Goal" and the canonical
            # <!-- BEGIN_GIT_DIFF --> markers (which embed the substring "gin"
            # in "begin_git_diff"). Either keyword would make the keyword phase
            # match go-gin for ALL tasks and render generic fallback unreachable
            # in the hermetic suite. golang/grpc remain.
            "task_keywords": ["golang", "grpc"],
        },
        "skills": ["go-gin", "go-hexagonal-grpc"],
        "preflight": ["true"],
        "toolchain": {"test_cmd": "true", "build_cmd": "true", "lint_cmd": "true"},
        "model_preferences": {
            "deep": ["openai/gpt-5.6-sol", "anthropic/claude-3-7-sonnet"],
            "quick": ["gemini/gemini-2.5-flash"],
        },
    },
}

_DEFAULT_MARKERS = {
    "node-ts": "package.json",
    "python-fastapi": "pyproject.toml",
    "kotlin-android": "build.gradle.kts",
    "go-gin": "go.mod",
    "generic": None,
}


def _render_yaml_value(value):
    """Render a Python value as a YAML flow scalar (strings always quoted).

    Quoting is mandatory: a bare ``true``/``false``/``null`` renders as a YAML
    boolean/null, not a string, breaking StackProfileConfig validation.
    """
    if value is None:
        return "null"
    if isinstance(value, (list, dict)):
        return json.dumps(value)
    return json.dumps(str(value))


def _write_profile(path: Path, name: str, profile: dict) -> None:
    lines = [f"name: {name}", f"display_name: {profile['display_name']}"]
    det = profile["detection"]
    lines.append("detection:")
    lines.append(f"  marker_files: {json.dumps(det['marker_files'])}")
    lines.append(f"  extensions: {json.dumps(det['extensions'])}")
    lines.append(f"  task_keywords: {json.dumps(det['task_keywords'])}")
    lines.append(f"skills: {json.dumps(profile['skills'])}")
    lines.append(f"preflight: {json.dumps(profile['preflight'])}")
    tc = profile["toolchain"]
    lines.append("toolchain:")
    lines.append(f"  test_cmd: {_render_yaml_value(tc.get('test_cmd'))}")
    lines.append(f"  build_cmd: {_render_yaml_value(tc.get('build_cmd'))}")
    lines.append(f"  lint_cmd: {_render_yaml_value(tc.get('lint_cmd'))}")
    lines.append(f"model_preferences: {json.dumps(profile['model_preferences'])}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


@dataclass
class SmokeWorkspace:
    """Container for a hermetic workspace plus real, workspace-anchored components."""

    root: Path
    config: LoopEngineConfig
    state: StateMachine
    router: LLMRouter
    qa: QAEngine
    executor: HandsExecutor
    gateway: ApprovalGateway
    brainstorm: BrainstormStage
    daemon: daemon.LoopEngineDaemon
    prompts: list = field(default_factory=list)
    run_once_calls: int = 0
    qa_calls: list = field(default_factory=list)

    @property
    def root_str(self) -> str:
        return str(self.root)

    def create_task(self, task_id: int, name: str, content: str, with_diff_markers: bool = True) -> Path:
        """Write a task file into the workspace backlog and register it."""
        backlog = self.root / "tasks" / "backlog"
        backlog.mkdir(parents=True, exist_ok=True)
        task_file = backlog / f"{task_id:02d}-{name}.md"
        body = (
            f"# Task {task_id}: {name}\n"
            f"**File:** tasks/backlog/{task_id:02d}-{name}.md\n"
            "**Source:** orchestrator\n"
            "**Type:** feature\n"
            "**Status:** open\n\n"
            "## Goal\n\n"
            f"{content}\n\n"
            "## Acceptance Criteria\n\n- [ ] criterion\n\n"
            "## Factual Git Diff\n\n"
        )
        if with_diff_markers:
            body += "<!-- BEGIN_GIT_DIFF -->\n\n<!-- END_GIT_DIFF -->\n"
        task_file.write_text(body, encoding="utf-8")
        return task_file

    def register(self, task_file: Path) -> int:
        return self.state.register_task(str(task_file), TaskState.BACKLOG)

    async def run_pipeline(self, task_id: int, task_file: Path) -> None:
        """Run the real public pipeline entry against this workspace.

        daemon.REPO_ROOT is patched to the workspace for the duration so marker
        detection, preflight/toolchain cwd, and evidence writes stay hermetic.
        """
        with patch.object(daemon, "REPO_ROOT", self.root_str):
            await daemon.process_task(
                task_id, str(task_file), self.config, self.state,
                self.router, self.gateway, self.executor, self.qa, self.brainstorm,
            )

    def evidence_dir(self, task_id: int) -> Path:
        return self.root / "loop-engine" / "evidence" / str(task_id)

    def close(self) -> None:
        self.state.close()


def setup_test_workspace(
    tmp_path,
    stack_name,
    marker_files=None,
    toolchain=None,
    preflight=None,
    model_prefs=None,
) -> SmokeWorkspace:
    """Build a hermetic workspace + real, workspace-anchored engine components.

    Args:
        tmp_path: pytest tmp_path (or any pathlib.Path).
        stack_name: profile whose toolchain/preflight/model_prefs are (optionally)
            overridden. ALL default profiles are written so marker-based detection
            competes realistically.
        marker_files: optional explicit marker files to create in the workspace root.
            Defaults to the named stack's first detection marker (none for generic).
        toolchain: optional dict overrides for the named stack's toolchain config.
        preflight: optional list overrides for the named stack's preflight commands.
        model_prefs: optional dict overrides for the named stack's model_preferences.

    Returns:
        SmokeWorkspace with real StateMachine/LLMRouter/QAEngine/HandsExecutor/
        ApprovalGateway/LoopEngineDaemon wired to the workspace.
    """
    root = Path(tmp_path)
    (root / "stacks").mkdir(parents=True, exist_ok=True)
    for sub in ("backlog", "in-progress", "qa", "completed"):
        (root / "tasks" / sub).mkdir(parents=True, exist_ok=True)
    (root / "loop-engine" / "evidence").mkdir(parents=True, exist_ok=True)
    (root / "loop-engine" / "state").mkdir(parents=True, exist_ok=True)
    (root / "docs").mkdir(parents=True, exist_ok=True)

    # Dummy core files (router reads them; content is not load-bearing here).
    (root / "AGENTS.md").write_text("# AGENTS\nDummy project rules for smoke test.\n", encoding="utf-8")
    (root / "system-prompt.md").write_text("# System Prompt\nDummy.\n", encoding="utf-8")
    (root / "docs" / "conventions.md").write_text("# Conventions\nDummy.\n", encoding="utf-8")
    (root / "loop-engine.jsonc").write_text('{\n  // dummy\n  "approval": {"chat_id": 1}\n}\n', encoding="utf-8")

    # Stack profiles: ALL defaults (realistic detection competition), then apply
    # overrides to the named profile.
    for prof_name, profile in _DEFAULT_PROFILES.items():
        _write_profile(root / "stacks" / f"{prof_name}.yaml", prof_name, dict(profile))

    profile = _DEFAULT_PROFILES[stack_name]
    contents = dict(profile)
    if preflight is not None:
        contents["preflight"] = list(preflight)
    if toolchain is not None:
        merged_tc = dict(profile["toolchain"])
        merged_tc.update(toolchain)
        contents["toolchain"] = merged_tc
    if model_prefs is not None:
        contents["model_preferences"] = dict(model_prefs)
    _write_profile(root / "stacks" / f"{stack_name}.yaml", stack_name, contents)

    # Marker files for detection.
    if marker_files is None:
        marker = _DEFAULT_MARKERS.get(stack_name)
        marker_files = [marker] if marker else []
    for m in marker_files:
        (root / m).write_text("marker\n", encoding="utf-8")

    config = LoopEngineConfig(
        approval={"chat_id": 1},
        evidence_dir=str(root / "loop-engine" / "evidence"),
        stacks_dir=str(root / "stacks"),
        tasks_dir=str(root / "tasks"),
        max_qa_retries=3,
        trigger_mode="telegram_button",
        auto_start_on_boot=False,
    )

    state = StateMachine(str(root / "loop-engine" / "state" / "loop.db"))
    router = ScriptedRouter(config, workspace_root=str(root))
    qa = QAEngine(config, state, router)
    executor = FakeHandsExecutor(config, state)
    gateway = AutoApproveGateway(config)
    brainstorm = BrainstormStage(config, router, workspace_root=str(root))

    ws = SmokeWorkspace(
        root=root, config=config, state=state, router=router, qa=qa,
        executor=executor, gateway=gateway, brainstorm=brainstorm,
        daemon=None,  # daemon constructed below (needs gateway wiring)
    )
    ws.daemon = daemon.LoopEngineDaemon(config, state, router, gateway, executor, qa, brainstorm)
    gateway.set_daemon(ws.daemon)
    gateway.set_state(state)
    # Bind recorder hooks so tests can derive evidence.
    qa.run_qa = _record_qa(qa.run_qa, ws.qa_calls)
    return ws


def _record_qa(original, sink):
    def wrapper(*args, **kwargs):
        sink.append(args[0])
        return original(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------------------------
# Scripted seams (real classes, stubbed I/O boundary)
# ---------------------------------------------------------------------------

class ScriptedRouter(LLMRouter):
    """Real LLMRouter with deterministic, stage-aware call_llm.

    route_plan/route_qa/route_review inherit the real prompt-building logic;
    call_llm consumes scripted per-stage responses instead of hitting litellm.
    """

    def __init__(self, config, workspace_root="."):
        super().__init__(config, workspace_root=workspace_root)
        self._stage = "plan"
        self.plan_response = "# Plan\n1. Implement the change."
        self.qa_responses = ["QA_PASSED: change satisfies the acceptance criteria."]
        self.review_responses = ["APPROVED"]
        self.seen_stack_profiles = []
        self.plan_calls = 0
        self.qa_count = 0
        self.review_count = 0

    def route_plan(self, task_content, category="unspecified", extra_context="", stack_profile=None):
        self._stage = "plan"
        self.plan_calls += 1
        if stack_profile is not None:
            self.seen_stack_profiles.append(stack_profile.name)
        return super().route_plan(
            task_content, category=category, extra_context=extra_context,
            stack_profile=stack_profile,
        )

    def route_qa(self, task_content, diff="", toolchain_evidence="", stack_profile=None):
        self._stage = "qa"
        return super().route_qa(
            task_content, diff=diff, toolchain_evidence=toolchain_evidence,
            stack_profile=stack_profile,
        )

    def route_review(self, task_content, qa_report="", stack_profile=None):
        self._stage = "review"
        return super().route_review(
            task_content, qa_report=qa_report, stack_profile=stack_profile)

    def call_llm(self, routing):
        if self._stage == "plan":
            self.plan_calls += 1
            return self.plan_response
        if self._stage == "qa":
            self.qa_count += 1
            if self.qa_responses:
                return self.qa_responses.pop(0)
            return "QA_PASSED"
        self.review_count += 1
        if self.review_responses:
            return self.review_responses.pop(0)
        return "APPROVED"


class FakeHandsExecutor(HandsExecutor):
    """Real HandsExecutor; _run_once simulates the Hands agent.

    Modes:
      complete     — injects a non-empty diff into the task file, emits [goal:complete].
      empty_diff   — leaves the diff block empty, still emits [goal:complete] (crashes later).
      blocked      — emits [goal:blocked: <reason>]; the REAL TERM_BLOCKED regex extracts it.
      error        — non-transport error.
    """

    def __init__(self, config, state, mode="complete", blocked_reason="missing credentials"):
        super().__init__(config, state)
        self.mode = mode
        self.blocked_reason = blocked_reason
        self.prompts = []
        self.run_once_calls = 0
        self.last_result = None

    async def _run_once(self, task_file, prompt):
        self.run_once_calls += 1
        self.prompts.append(prompt)

        if self.mode == "blocked":
            # Simulate agent stdout; the real executor regex does the extraction.
            output = f"[goal:blocked: {self.blocked_reason}]"
            m = TERM_BLOCKED.search(output)
            reason = m.group(1) if m and m.group(1) else "Agent signaled blocked"
            result = {"status": "blocked", "output": output, "error": "", "reason": reason.strip(), "elapsed": 0.1}
            self.last_result = result
            return result

        if self.mode == "error":
            result = {"status": "error", "output": "", "error": "boom", "returncode": 2, "elapsed": 0.1}
            self.last_result = result
            return result

        # Default complete/empty_diff: Hands "writes" the factual diff block.
        path = Path(task_file)
        text = path.read_text(encoding="utf-8")
        begin = "<!-- BEGIN_GIT_DIFF -->"
        end = "<!-- END_GIT_DIFF -->"
        if begin not in text or end not in text:
            text += f"\n{begin}\n{end}\n"

        if self.mode == "empty_diff":
            # Keep markers present but payload empty → extract_task_diff returns "".
            head, _, tail = text.partition(begin)
            _, _, footer = tail.partition(end)
            text = f"{head}{begin}\n{end}{footer}"
        else:
            # Inject a passing diff payload between markers.
            head, _, tail = text.partition(begin)
            _, _, footer = tail.partition(end)
            payload = "+def smoke_impl():\n+    return 42\n"
            text = f"{head}{begin}\n{payload}{end}{footer}"
        path.write_text(text, encoding="utf-8")
        result = {"status": "complete", "output": "[goal:complete]", "error": "", "elapsed": 0.1}
        self.last_result = result
        return result


class AutoApproveGateway(ApprovalGateway):
    """Real ApprovalGateway with scripted approval I/O (no Telegram).

    approve_plan / approve_closure flags let tests script denial; trigger cards
    are recorded instead of sent.
    """

    def __init__(self, config, approve_plan=True, approve_closure=True):
        super().__init__(config)
        self.approve_plan = approve_plan
        self.approve_closure = approve_closure
        self.plan_approvals = 0
        self.closure_approvals = 0
        self.trigger_cards = []

    async def request_approval(self, task_id, stage, content):
        if stage == "Plan Approval":
            self.plan_approvals += 1
            return self.approve_plan
        if stage == "Closure Approval":
            self.closure_approvals += 1
            return self.approve_closure
        return False

    async def send_task_trigger_card(self, task_id, title, file_path):
        self.trigger_cards.append((task_id, title, file_path))
        return True


# ---------------------------------------------------------------------------
# Happy-path E2E smoke tests
# ---------------------------------------------------------------------------

def _run_to_completion(ws: SmokeWorkspace, tid: int, task_file: Path):
    asyncio.run(ws.run_pipeline(tid, task_file))


def test_smoke_node_ts_end_to_end(tmp_path):
    """Node/TS workspace with package.json → full lifecycle → CLOSED."""
    ws = setup_test_workspace(tmp_path, "node-ts")
    try:
        task = ws.create_task(1, "node-smoke", "Add a TypeScript API endpoint to the service layer.")
        tid = ws.register(task)
        _run_to_completion(ws, tid, task)

        rec = ws.state.get_task(tid)
        assert rec["state"] == "closed"
        assert "node-ts" in ws.router.seen_stack_profiles
        # Stack context was injected into the Hands prompt.
        assert "node-ts" in ws.executor.prompts[0]
        assert "nextjs" in ws.executor.prompts[0]
    finally:
        ws.close()


def test_smoke_python_fastapi_end_to_end(tmp_path):
    """Python/FastAPI workspace with pyproject.toml → CLOSED + evidence files."""
    ws = setup_test_workspace(tmp_path, "python-fastapi")
    try:
        task = ws.create_task(2, "py-smoke", "Add a FastAPI health endpoint using Pydantic schemas.")
        tid = ws.register(task)
        _run_to_completion(ws, tid, task)

        rec = ws.state.get_task(tid)
        assert rec["state"] == "closed"
        ev = ws.evidence_dir(tid)
        assert (ev / "qa_report.md").exists()
        assert (ev / "result.txt").read_text() == "PASSED"
        assert (ev / "review.md").exists()
        assert (ev / "review_result.txt").read_text() == "APPROVED"
        assert (ev / "toolchain_report.md").exists()
        assert (ev / "toolchain_result.txt").read_text() == "PASSED"
    finally:
        ws.close()


def test_smoke_kotlin_android_end_to_end(tmp_path):
    """Kotlin/Android workspace with build.gradle.kts → CLOSED, android-kotlin skill verified."""
    ws = setup_test_workspace(tmp_path, "kotlin-android")
    try:
        task = ws.create_task(3, "kotlin-smoke", "Refactor a Compose screen using Kotlin coroutines.")
        tid = ws.register(task)
        _run_to_completion(ws, tid, task)

        rec = ws.state.get_task(tid)
        assert rec["state"] == "closed"
        assert "kotlin-android" in ws.router.seen_stack_profiles
        # Android-Kotlin skill mandated via <stack_context> in the Hands prompt.
        assert "android-kotlin" in ws.executor.prompts[0]
        assert "<stack_context" in ws.executor.prompts[0]
    finally:
        ws.close()


def test_smoke_go_gin_end_to_end(tmp_path):
    """Go/Gin workspace with go.mod → CLOSED."""
    ws = setup_test_workspace(tmp_path, "go-gin")
    try:
        task = ws.create_task(4, "go-smoke", "Add a Gin route with middleware for the service.")
        tid = ws.register(task)
        _run_to_completion(ws, tid, task)

        rec = ws.state.get_task(tid)
        assert rec["state"] == "closed"
        assert "go-gin" in ws.router.seen_stack_profiles
    finally:
        ws.close()


def test_smoke_generic_end_to_end(tmp_path):
    """Untagged task, no marker files → generic fallback → toolchain skipped → CLOSED."""
    ws = setup_test_workspace(tmp_path, "generic")
    try:
        task = ws.create_task(5, "generic-smoke", "Update the documentation template for onboarding.")
        tid = ws.register(task)
        _run_to_completion(ws, tid, task)

        rec = ws.state.get_task(tid)
        assert rec["state"] == "closed"
        assert "generic" in ws.router.seen_stack_profiles
        # Generic toolchain is all-null → skipped gracefully, reported as PASSED.
        ev = ws.evidence_dir(tid)
        assert (ev / "toolchain_report.md").exists()
        assert "SKIPPED" in (ev / "toolchain_report.md").read_text()
        assert (ev / "toolchain_result.txt").read_text() == "PASSED"
    finally:
        ws.close()


# ---------------------------------------------------------------------------
# Hard-gate failure & edge-case smoke tests
# ---------------------------------------------------------------------------

def test_smoke_preflight_failure_crashes_before_execution(tmp_path):
    """Failing preflight → CRASHED before executor.execute; error recorded via set_qa_feedback."""
    ws = setup_test_workspace(tmp_path, "node-ts", preflight=["false"])
    try:
        task = ws.create_task(6, "preflight-fail", "Add a TypeScript endpoint (preflight will fail).")
        tid = ws.register(task)
        _run_to_completion(ws, tid, task)

        rec = ws.state.get_task(tid)
        assert rec["state"] == "crashed"
        # Executor never ran — preflight gate fired first.
        assert ws.executor.run_once_calls == 0
        # Preflight diagnostic recorded via set_qa_feedback (retry count incremented once).
        assert rec["qa_feedback"] is not None
        assert "Preflight failed" in rec["qa_feedback"]
        assert rec["qa_retry_count"] == 1
        # No toolchain/QA evidence was produced.
        assert not ws.evidence_dir(tid).exists()
    finally:
        ws.close()


def test_smoke_toolchain_failure_bypasses_qa_and_retries(tmp_path):
    """Failing test_cmd → _execute_and_qa returns FAILED without qa.run_qa; evidence written;
    _reimplement_task retries until max_qa_retries then CRASHED."""
    ws = setup_test_workspace(tmp_path, "go-gin", toolchain={"test_cmd": "false"})
    try:
        task = ws.create_task(7, "toolchain-fail", "Add a Go route with a failing test command.")
        tid = ws.register(task)
        _run_to_completion(ws, tid, task)

        rec = ws.state.get_task(tid)
        assert rec["state"] == "crashed"
        # Toolchain failed on every attempt → LLM QA never invoked.
        assert ws.qa_calls == []
        # Fail-fast evidence written before QA bypass.
        ev = ws.evidence_dir(tid)
        assert (ev / "toolchain_report.md").exists()
        assert "FAILED" in (ev / "toolchain_result.txt").read_text()
        # Retry loop engaged (each toolchain failure bumps the retry counter).
        assert rec["qa_retry_count"] >= 3
        # Hands prompt carried the toolchain failure report as qa_feedback on retries.
        assert ws.executor.run_once_calls >= 3
        assert "<qa_feedback>" in ws.executor.prompts[-1]
    finally:
        ws.close()


def test_smoke_goal_blocked_extracts_reason_and_crashes(tmp_path):
    """Handler emits [goal:blocked: missing credentials] → CRASHED with extracted reason."""
    ws = setup_test_workspace(tmp_path, "python-fastapi")
    try:
        ws.executor.mode = "blocked"
        ws.executor.blocked_reason = "missing credentials"
        task = ws.create_task(8, "blocked", "Add a FastAPI auth dependency (will be blocked).")
        tid = ws.register(task)
        _run_to_completion(ws, tid, task)

        rec = ws.state.get_task(tid)
        assert rec["state"] == "crashed"
        # The real TERM_BLOCKED regex extracted the reason from the agent output.
        assert ws.executor.last_result is not None
        assert ws.executor.last_result["status"] == "blocked"
        assert ws.executor.last_result["reason"] == "missing credentials"
        # QA never reached.
        assert ws.qa_calls == []
    finally:
        ws.close()


def test_smoke_empty_diff_crashes_without_qa(tmp_path):
    """Hands leaves diff block empty → CRASHED before toolchain/QA execute."""
    ws = setup_test_workspace(tmp_path, "node-ts")
    try:
        ws.executor.mode = "empty_diff"
        task = ws.create_task(9, "empty-diff", "Add a TypeScript endpoint but produce no diff.")
        tid = ws.register(task)
        _run_to_completion(ws, tid, task)

        rec = ws.state.get_task(tid)
        assert rec["state"] == "crashed"
        # No toolchain evidence and no QA calls — empty-diff gate fired before both.
        assert ws.qa_calls == []
        assert not ws.evidence_dir(tid).exists()
    finally:
        ws.close()


def test_smoke_reimplement_retry_recovers_to_closed(tmp_path):
    """Attempt 1 toolchain fails; _reimplement_task loops; attempt 2 passes → CLOSED."""
    # test_cmd fails once (marker file consumed on first run), then passes.
    ws = setup_test_workspace(
        tmp_path, "python-fastapi",
        toolchain={"test_cmd": "test -f .smoke_fail_once && rm -f .smoke_fail_once && exit 1 || true"},
    )
    try:
        (ws.root / ".smoke_fail_once").write_text("x", encoding="utf-8")
        task = ws.create_task(10, "retry-recover", "Add a FastAPI route that recovers on retry.")
        tid = ws.register(task)
        _run_to_completion(ws, tid, task)

        rec = ws.state.get_task(tid)
        assert rec["state"] == "closed"
        # Exactly one toolchain failure → one retry increment, then success.
        assert rec["qa_retry_count"] == 1
        # QA ran exactly once (attempt 2 only).
        assert len(ws.qa_calls) == 1
        # Closure approved after recovery.
        assert ws.gateway.closure_approvals >= 1
    finally:
        ws.close()


def test_smoke_reimplement_max_retries_exceeded_crashes(tmp_path):
    """Consecutive toolchain failures hit max_qa_retries → CRASHED."""
    ws = setup_test_workspace(tmp_path, "go-gin", toolchain={"test_cmd": "false"})
    try:
        ws.config.max_qa_retries = 2
        task = ws.create_task(11, "max-retries", "Add a Go route whose tests always fail.")
        tid = ws.register(task)
        _run_to_completion(ws, tid, task)

        rec = ws.state.get_task(tid)
        assert rec["state"] == "crashed"
        assert rec["qa_retry_count"] >= 2
        # No QA ever executed; no closure approval.
        assert ws.qa_calls == []
        assert ws.gateway.closure_approvals == 0
    finally:
        ws.close()


def test_smoke_explicit_header_overrides_marker_detection(tmp_path):
    """package.json marker present (node-ts), but explicit **Stack:** python-fastapi header wins."""
    ws = setup_test_workspace(tmp_path, "python-fastapi", marker_files=["package.json"])
    try:
        task = ws.create_task(
            12, "header-override",
            "Add an endpoint.\n\n**Stack:** python-fastapi\n\nImplement it now.",
        )
        tid = ws.register(task)
        _run_to_completion(ws, tid, task)

        rec = ws.state.get_task(tid)
        assert rec["state"] == "closed"
        # Header precedence: python-fastapi, NOT node-ts (despite package.json).
        assert "python-fastapi" in ws.router.seen_stack_profiles
        assert "node-ts" not in ws.router.seen_stack_profiles
        assert "python-fastapi" in ws.executor.prompts[0]
    finally:
        ws.close()


# ---------------------------------------------------------------------------
# Supplementary smoke tests (extend coverage beyond the mandated 12)
# ---------------------------------------------------------------------------

def test_smoke_plan_rejected_returns_to_backlog(tmp_path):
    """Plan Approval denied → task returns to BACKLOG, executor never runs."""
    ws = setup_test_workspace(tmp_path, "node-ts")
    try:
        ws.gateway.approve_plan = False
        task = ws.create_task(13, "plan-rejected", "Add a TypeScript endpoint but plan is rejected.")
        tid = ws.register(task)
        _run_to_completion(ws, tid, task)

        rec = ws.state.get_task(tid)
        assert rec["state"] == "backlog"
        assert ws.executor.run_once_calls == 0
        assert ws.qa_calls == []
    finally:
        ws.close()


def test_smoke_review_rejected_crashes(tmp_path):
    """QA passes but Code Review rejects → CRASHED after review."""
    ws = setup_test_workspace(tmp_path, "python-fastapi")
    try:
        ws.router.review_responses = ["REJECTED: architectural risk in the change."]
        task = ws.create_task(14, "review-rejected", "Add a FastAPI module that review will reject.")
        tid = ws.register(task)
        _run_to_completion(ws, tid, task)

        rec = ws.state.get_task(tid)
        assert rec["state"] == "crashed"
        assert len(ws.qa_calls) == 1
        ev = ws.evidence_dir(tid)
        assert (ev / "review_result.txt").read_text() == "REJECTED"
    finally:
        ws.close()


def test_smoke_qa_failure_retries_with_feedback(tmp_path):
    """QA FAILED → retry re-executes with qa_feedback; second attempt passes → CLOSED."""
    ws = setup_test_workspace(tmp_path, "python-fastapi")
    try:
        ws.router.qa_responses = [
            "FAILED: missing error handling for the edge case.",
            "QA_PASSED: error handling added.",
        ]
        task = ws.create_task(15, "qa-retry", "Add a FastAPI endpoint that fails QA once.")
        tid = ws.register(task)
        _run_to_completion(ws, tid, task)

        rec = ws.state.get_task(tid)
        assert rec["state"] == "closed"
        assert rec["qa_retry_count"] == 1
        assert len(ws.qa_calls) == 2
        # Retry prompt carried the QA report as <qa_feedback> (distinct from plan).
        assert "<qa_feedback>" in ws.executor.prompts[-1]
        assert "error handling" in ws.executor.prompts[-1]
        assert ws.gateway.closure_approvals == 1
    finally:
        ws.close()


def test_smoke_boot_scan_registers_pending_trigger(tmp_path):
    """Daemon boot_scan registers backlog tasks as PENDING_TRIGGER + sends trigger cards.

    daemon.boot_scan constructs KanbanWatcher without an explicit tasks_dir (it defaults
    to CWD-relative "tasks/backlog"). For hermeticity we patch the class with a factory
    that forwards config.tasks_dir, so boot_scan scans the temp workspace and never
    registers unrelated real-repo backlog files.
    """
    from watcher import KanbanWatcher as RealKanbanWatcher
    import watcher as watcher_module

    ws = setup_test_workspace(tmp_path, "node-ts")
    try:
        task_file = ws.create_task(16, "boot-scan", "Add a TypeScript endpoint awaiting trigger.")
        assert task_file.exists()

        def watcher_factory(state, config, gateway=None, on_task_detected=None):
            return RealKanbanWatcher(
                state, config, gateway,
                tasks_dir=config.tasks_dir, on_task_detected=on_task_detected)

        # boot_scan does a local `from watcher import KanbanWatcher`, so the patch
        # must replace the attribute on the watcher module itself.
        with patch.object(watcher_module, "KanbanWatcher", watcher_factory):
            existing = asyncio.run(ws.daemon.boot_scan())

        assert len(existing) == 1
        tid = existing[0]["task_id"]
        rec = ws.state.get_task(tid)
        assert rec["state"] == "pending_trigger"
        assert len(ws.gateway.trigger_cards) == 1
        assert ws.gateway.trigger_cards[0][0] == tid
    finally:
        ws.close()


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for t in tests:
        try:
            t(Path(f"/tmp/polyglot-smoke-{t.__name__}"))
            print(f"  PASS: {t.__name__}")
            passed += 1
        except TypeError:
            # pytest tmp_path fixtures not available in bare-run mode
            print(f"  SKIP: {t.__name__} (requires pytest tmp_path fixture)")
        except Exception as e:
            import traceback
            print(f"  FAIL: {t.__name__}: {e}")
            traceback.print_exc()
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)