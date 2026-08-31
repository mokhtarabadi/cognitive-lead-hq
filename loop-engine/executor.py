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
import re
import time
from pathlib import Path

from models import LoopEngineConfig
from state import StateMachine


TERM_COMPLETE = re.compile(r'\[goal:complete\]')
TERM_BLOCKED = re.compile(r'\[goal:blocked\]')
TRANSPORT_ERROR = re.compile(r'stream disconnected|ECONNRESET|ETIMEDOUT|EPIPE|timeout|connection reset', re.IGNORECASE)

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


class HandsExecutor:
    """Delegates auto-continue to Goal Plugin, monitors result."""

    def __init__(self, config: LoopEngineConfig, state: StateMachine):
        self.config = config
        self.state = state

    async def execute(self, task_id: int, task_file: str, task_content: str,
                    blueprint_context: str = "", qa_feedback: str = "") -> dict:
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
        """
        prompt_parts = [
            f"Read the task file at {task_file} and implement it.",
            "Follow AGENTS.md rules exactly.",
            "Output [goal:complete] when done, [goal:blocked] if stuck.",
        ]
        if blueprint_context and blueprint_context.strip():
            prompt_parts.append(
                f"## Approved Blueprint Context\n{blueprint_context.strip()}"
            )
        if qa_feedback and qa_feedback.strip():
            prompt_parts.append(
                f"## QA Feedback to Address\n{qa_feedback.strip()}\n\n"
                f"Address the above QA feedback explicitly. Do NOT treat this "
                f"as a new architectural plan — it is a correction request for "
                f"the previous implementation."
            )
        prompt = "\n\n".join(prompt_parts)

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
        """Run one OpenCode turn via subprocess."""
        start = time.time()
        max_duration = 7200  # 2 hours safety cap

        try:
            proc = await asyncio.create_subprocess_exec(
                "opencode", "run", "--format", "json",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=prompt.encode()),
                timeout=max_duration
            )

            output = stdout.decode(errors="replace")
            error = stderr.decode(errors="replace")
            elapsed = time.time() - start

            # Check for terminal markers in output
            if TERM_COMPLETE.search(output):
                return {"status": "complete", "output": output, "error": error, "elapsed": elapsed}

            if TERM_BLOCKED.search(output):
                return {"status": "blocked", "output": output, "error": error, "elapsed": elapsed}

            # Process exited — check return code
            if proc.returncode == 0:
                return {"status": "complete", "output": output, "error": error, "elapsed": elapsed}

            # Check for transport errors in stderr
            if TRANSPORT_ERROR.search(error):
                return {"status": "transport_error", "output": output, "error": error, "elapsed": elapsed}

            return {"status": "error", "output": output, "error": error, "returncode": proc.returncode, "elapsed": elapsed}

        except asyncio.TimeoutError:
            return {"status": "timeout", "output": "", "error": f"Exceeded {max_duration}s timeout", "elapsed": time.time() - start}

        except FileNotFoundError:
            return {"status": "error", "output": "", "error": "opencode CLI not found in PATH", "elapsed": time.time() - start}

        except Exception as e:
            if TRANSPORT_ERROR.search(str(e)):
                return {"status": "transport_error", "output": "", "error": str(e), "elapsed": time.time() - start}
            return {"status": "error", "output": "", "error": str(e), "elapsed": time.time() - start}
