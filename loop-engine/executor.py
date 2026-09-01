"""
Hands Executor v2 — delegates auto-continue to Goal Plugin.

The Goal Plugin (@prevalentware/opencode-goal-plugin) runs INSIDE OpenCode
and handles: event-driven idle detection, terminal markers, no-progress,
budget enforcement, compaction survival, re-entrancy guard.

Our executor.py only needs to:
1. Send the initial prompt to OpenCode CLI
2. Wait for the Goal Plugin to finish (or timeout)
3. Read the result from the task file
4. Handle transport errors with retry

ZAC intact: executor NEVER commits.
"""

import asyncio
import os
import re
import signal
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any

from models import LoopEngineConfig
from state import StateMachine


TERM_COMPLETE = re.compile(r'\[goal:complete\]', re.IGNORECASE)
TERM_BLOCKED = re.compile(r'\[goal:blocked(?::\s*([^\]]+))?\]', re.IGNORECASE)
TRANSPORT_ERROR = re.compile(r'stream disconnected|ECONNRESET|ETIMEDOUT|EPIPE|timeout|connection reset', re.IGNORECASE)

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


class HandsExecutor:
    """Delegates auto-continue to Goal Plugin, monitors result."""

    def __init__(self, config: LoopEngineConfig, state: StateMachine):
        self.config = config
        self.state = state
        self._semaphore = asyncio.Semaphore(config.max_parallel_tasks)

    def _build_prompt(self, task_file: str, blueprint_context: str = "",
                      qa_feedback: str = "", stack_profile: Optional[Any] = None) -> str:
        """Construct the structured XML prompt for the local OpenCode agent.

        Sections (emitted only when relevant):
          1. <task_instructions> — read the task file, follow AGENTS.md.
          2. <stack_context> — when a stack profile is present: mandate skill
             loading via the native skill tool and list toolchain commands.
          3. <blueprint_context> — approved Architect plan (LE-0.1).
          4. <qa_feedback> — QA rejection feedback to address (LE-0.1).
          5. <goal_rules> — Goal Plugin termination tokens.
        """
        parts = [
            "<task_instructions>\n"
            f"Read the task file at {task_file} and implement it.\n"
            "Follow AGENTS.md rules exactly.\n"
            "</task_instructions>",
        ]

        if stack_profile is not None:
            try:
                skills = getattr(stack_profile, "skills", []) or []
                skills_str = ", ".join(skills) if skills else "none"
                toolchain = getattr(stack_profile, "toolchain", None)
                test_cmd = getattr(toolchain, "test_cmd", None) if toolchain else None
                build_cmd = getattr(toolchain, "build_cmd", None) if toolchain else None
                lint_cmd = getattr(toolchain, "lint_cmd", None) if toolchain else None
                preflight = getattr(stack_profile, "preflight", []) or []
                preflight_str = ", ".join(preflight) if preflight else "none"
                name = getattr(stack_profile, "name", "unknown")
                display_name = getattr(stack_profile, "display_name", name)
                parts.append(
                    f'<stack_context name="{name}" display_name="{display_name}">\n'
                    f"MANDATORY: Load required skills via the native skill tool: {skills_str}\n"
                    f"Preflight commands: {preflight_str}\n"
                    f"Run toolchain verification before completion: "
                    f"test='{test_cmd}', build='{build_cmd}', lint='{lint_cmd}'\n"
                    "</stack_context>"
                )
            except Exception:
                pass

        if blueprint_context and blueprint_context.strip():
            parts.append(
                f"<blueprint_context>\n{blueprint_context.strip()}\n</blueprint_context>"
            )

        if qa_feedback and qa_feedback.strip():
            parts.append(
                f"<qa_feedback>\n{qa_feedback.strip()}\n\n"
                "Address the above QA feedback explicitly. Do NOT treat this "
                "as a new architectural plan.\n"
                "</qa_feedback>"
            )

        parts.append(
            "<goal_rules>\n"
            "When finished and verified, output [goal:complete]. "
            "If stuck, output [goal:blocked: <reason>].\n"
            "</goal_rules>"
        )

        return "\n\n".join(parts)

    async def execute(self, task_id: int, task_file: str, task_content: str,
                    blueprint_context: str = "", qa_feedback: str = "",
                    stack_profile: Optional[Any] = None) -> dict:
        """Execute a task via OpenCode CLI with transport error retry.

        Args:
            task_id: Task identifier.
            task_file: Path to task file.
            task_content: Content of task file (may be stale; executor re-reads file).
            blueprint_context: Approved architectural blueprint/plan (from Architect).
                Injected as delimited section when non-empty. Named to avoid collision
                with qa_feedback.
            qa_feedback: QA rejection feedback to address (on retry). Injected as
                distinct delimited section when non-empty, never overloaded with
                blueprint_context.
            stack_profile: Optional StackProfile detected for this task — skills and
                toolchain commands are injected into the prompt.
        """
        prompt = self._build_prompt(
            task_file, blueprint_context=blueprint_context,
            qa_feedback=qa_feedback, stack_profile=stack_profile)

        async with self._semaphore:
            for attempt in range(MAX_RETRIES):
                result = await self._run_once(task_file, prompt)

                # Success or terminal failure — no retry
                if result["status"] in ("complete", "blocked", "timeout"):
                    return result

                # Transport error — retry
                if result["status"] == "transport_error" and attempt < MAX_RETRIES - 1:
                    print(f"[executor] Transport error (attempt {attempt + 1}/{MAX_RETRIES}), retrying in {RETRY_DELAY}s...")
                    await asyncio.sleep(RETRY_DELAY)
                    continue

                # Non-transport error or final attempt
                return result

            return result  # last attempt result

    async def _run_once(self, task_file: str, prompt: str) -> dict:
        """Run one OpenCode turn via subprocess, with debug telemetry (HOTFIX-03).

        Wraps the real implementation so every result path (complete, blocked,
        transport_error, timeout, error) is captured by the same debug log hook.
        """
        result = await self._run_once_impl(task_file, prompt)
        if os.environ.get("LOOP_ENGINE_DEBUG") == "1":
            self._log_executor_debug(task_file, prompt, result)
        return result

    def _log_executor_debug(self, task_file: str, prompt: str, result: dict) -> None:
        """Append the executor session to loop-engine/logs/executor_sessions.log.

        Opt-in ONLY via LOOP_ENGINE_DEBUG=1. Never raises: telemetry must not
        affect pipeline execution.
        """
        try:
            log_dir = Path(__file__).resolve().parent / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            entry = (
                f"\n===== [{datetime.now(timezone.utc).isoformat(timespec='seconds')}Z] "
                f"task_file={task_file} status={result.get('status')} "
                f"returncode={result.get('returncode')} elapsed={result.get('elapsed', 0):.1f}s =====\n"
                f"--- PROMPT ---\n{prompt}\n"
                f"--- STDOUT ---\n{result.get('output', '')}\n"
                f"--- STDERR ---\n{result.get('error', '')}\n"
                f"===== END =====\n"
            )
            with open(log_dir / "executor_sessions.log", "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception as e:
            print(f"[executor] debug telemetry log error: {e}")

    async def _run_once_impl(self, task_file: str, prompt: str) -> dict:
        """Run one OpenCode turn via subprocess."""
        start = time.time()
        timeout = float(getattr(self.config.idle, "executing_timeout_seconds", None) or 900.0)

        try:
            kwargs = {}
            if os.name == "posix":
                kwargs["start_new_session"] = True
            proc = await asyncio.create_subprocess_exec(
                "opencode", "run", "--format", "json",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                **kwargs,
            )

            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=prompt.encode()),
                timeout=timeout
            )

            output = stdout.decode(errors="replace")
            error = stderr.decode(errors="replace")
            elapsed = time.time() - start

            # Check for terminal markers in output
            if TERM_COMPLETE.search(output):
                return {"status": "complete", "output": output, "error": error, "elapsed": elapsed}

            m = TERM_BLOCKED.search(output)
            if m:
                reason = m.group(1).strip() if m.group(1) else "Agent signaled blocked"
                return {"status": "blocked", "output": output, "error": error, "reason": reason, "elapsed": elapsed}

            # Process exited — check return code
            if proc.returncode == 0:
                return {"status": "complete", "output": output, "error": error, "elapsed": elapsed}

            # Check for transport errors in stderr
            if TRANSPORT_ERROR.search(error):
                return {"status": "transport_error", "output": output, "error": error, "elapsed": elapsed}

            return {"status": "error", "output": output, "error": error, "returncode": proc.returncode, "elapsed": elapsed}

        except asyncio.TimeoutError:
            # Cleanly terminate the entire process group (start_new_session=True)
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except (ProcessLookupError, AttributeError, PermissionError):
                pass
            try:
                await asyncio.wait_for(proc.wait(), timeout=2.0)
            except (asyncio.TimeoutError, ProcessLookupError):
                pass
            return {"status": "timeout", "output": "", "error": f"Exceeded {timeout}s timeout", "elapsed": time.time() - start}

        except FileNotFoundError:
            return {"status": "error", "output": "", "error": "opencode CLI not found in PATH", "elapsed": time.time() - start}

        except Exception as e:
            if TRANSPORT_ERROR.search(str(e)):
                return {"status": "transport_error", "output": "", "error": str(e), "elapsed": time.time() - start}
            return {"status": "error", "output": "", "error": str(e), "elapsed": time.time() - start}
