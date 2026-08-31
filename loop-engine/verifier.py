"""
Polyglot Verification & Multi-Toolchain Test Runner.

Deterministic lint/build/test execution per StackProfile.toolchain.
Invoked from daemon._execute_and_qa immediately after diff verification,
before LLM QA, to fail-fast on broken builds without wasting tokens.
"""

import asyncio
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CommandResult:
    command: str
    cmd_type: str
    passed: bool
    skipped: bool = False
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""
    duration_seconds: float = 0.0


@dataclass
class ToolchainResult:
    passed: bool
    commands: list[CommandResult] = field(default_factory=list)
    summary: str = ""
    report_md: str = ""


class ToolchainRunner:
    """Deterministic toolchain executor for StackProfile.toolchain.

    Executes lint → build → test sequentially via shell, with per-command
    timeout and evidence persistence. Mirrors PreflightRunner's subprocess
    pattern but validates functional correctness, not just presence.
    """

    def __init__(
        self,
        timeout_per_command: float = 120.0,
        evidence_base_dir: str | Path = "loop-engine/evidence",
    ):
        self.timeout_per_command = timeout_per_command
        self.evidence_base_dir = Path(evidence_base_dir)

    async def run(
        self,
        profile,  # StackProfile
        task_id: int | None = None,
        cwd: str | Path | None = None,
    ) -> ToolchainResult:
        """Run toolchain commands sequentially.

        Order: lint, build, test. Null/whitespace commands are skipped as
        passed+skipped. Non-zero exit or timeout → passed=False.
        """
        # Defensive: profile may lack toolchain attr in mocks
        toolchain = getattr(profile, "toolchain", None)
        if toolchain is None:
            # Treat as generic no-op
            commands: list[CommandResult] = [
                CommandResult(command="none", cmd_type=t, passed=True, skipped=True)
                for t in ("lint", "build", "test")
            ]
            return self._finalize(commands, task_id)

        # Sequential order: lint, build, test per spec
        ordered = [
            ("lint", getattr(toolchain, "lint_cmd", None)),
            ("build", getattr(toolchain, "build_cmd", None)),
            ("test", getattr(toolchain, "test_cmd", None)),
        ]

        results: list[CommandResult] = []
        cwd_path = Path(cwd) if cwd is not None else None

        for cmd_type, cmd in ordered:
            # Null or whitespace-only → skipped
            if cmd is None or (isinstance(cmd, str) and not cmd.strip()):
                results.append(
                    CommandResult(
                        command="none",
                        cmd_type=cmd_type,
                        passed=True,
                        skipped=True,
                    )
                )
                continue

            cmd_str = str(cmd)
            start = time.monotonic()
            try:
                proc = await asyncio.create_subprocess_shell(
                    cmd_str,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(cwd_path) if cwd_path else None,
                )
                try:
                    stdout_bytes, stderr_bytes = await asyncio.wait_for(
                        proc.communicate(), timeout=self.timeout_per_command
                    )
                except asyncio.TimeoutError:
                    try:
                        proc.kill()
                    except ProcessLookupError:
                        pass
                    duration = time.monotonic() - start
                    # Drain? proc already killed, attempt wait with timeout
                    try:
                        await asyncio.wait_for(proc.wait(), timeout=2.0)
                    except Exception:
                        pass
                    results.append(
                        CommandResult(
                            command=cmd_str,
                            cmd_type=cmd_type,
                            passed=False,
                            skipped=False,
                            returncode=None,
                            stdout="",
                            stderr=f"Toolchain timeout ({self.timeout_per_command}s): {cmd_str}",
                            duration_seconds=duration,
                        )
                    )
                    continue

                duration = time.monotonic() - start
                stdout = stdout_bytes.decode(errors="replace").strip()
                stderr = stderr_bytes.decode(errors="replace").strip()
                passed = proc.returncode == 0
                results.append(
                    CommandResult(
                        command=cmd_str,
                        cmd_type=cmd_type,
                        passed=passed,
                        skipped=False,
                        returncode=proc.returncode,
                        stdout=stdout,
                        stderr=stderr,
                        duration_seconds=duration,
                    )
                )

            except FileNotFoundError as e:
                duration = time.monotonic() - start
                results.append(
                    CommandResult(
                        command=cmd_str,
                        cmd_type=cmd_type,
                        passed=False,
                        skipped=False,
                        returncode=None,
                        stdout="",
                        stderr=f"Toolchain spawn failed: {cmd_str} → {e}",
                        duration_seconds=duration,
                    )
                )
            except Exception as e:
                duration = time.monotonic() - start
                results.append(
                    CommandResult(
                        command=cmd_str,
                        cmd_type=cmd_type,
                        passed=False,
                        skipped=False,
                        returncode=None,
                        stdout="",
                        stderr=f"Toolchain error: {cmd_str} → {e}",
                        duration_seconds=duration,
                    )
                )

        return self._finalize(results, task_id)

    def _finalize(
        self, commands: list[CommandResult], task_id: int | None
    ) -> ToolchainResult:
        passed = all(c.passed for c in commands)
        # Summary: single line
        summary_parts = []
        for c in commands:
            if c.skipped:
                summary_parts.append(f"{c.cmd_type}: SKIPPED")
            elif c.passed:
                summary_parts.append(f"{c.cmd_type}: PASSED")
            else:
                summary_parts.append(f"{c.cmd_type}: FAILED")
        summary = "Toolchain " + ("PASSED" if passed else "FAILED") + " | " + ", ".join(summary_parts)

        # Markdown report with summary table and error logs
        report_md = self._build_report_md(commands, passed, summary)

        result = ToolchainResult(
            passed=passed, commands=commands, summary=summary, report_md=report_md
        )

        # Evidence persistence if task_id provided
        if task_id is not None:
            try:
                # Only write if base dir's parent exists? spec says if evidence_base_dir exists: save
                # We ensure mkdir for base + task subdir
                evidence_path = self.evidence_base_dir / str(task_id)
                evidence_path.mkdir(parents=True, exist_ok=True)
                (evidence_path / "toolchain_report.md").write_text(report_md, encoding="utf-8")
                (evidence_path / "toolchain_result.txt").write_text(
                    "PASSED" if passed else "FAILED", encoding="utf-8"
                )
            except Exception:
                # Evidence write failure should not fail the toolchain result itself
                pass

        return result

    def _build_report_md(
        self, commands: list[CommandResult], passed: bool, summary: str
    ) -> str:
        lines: list[str] = []
        lines.append("# Toolchain Verification Report")
        lines.append("")
        lines.append(summary)
        lines.append("")
        lines.append(f"**Overall:** {'PASSED' if passed else 'FAILED'}")
        lines.append("")
        lines.append("| Type | Command | Result | Duration | Return Code |")
        lines.append("|---|---|---|---|---|")
        for c in commands:
            if c.skipped:
                result_str = "SKIPPED"
                cmd_display = "none"
                rc = "-"
                dur = "-"
            else:
                result_str = "PASSED" if c.passed else "FAILED"
                # Escape pipe in command for markdown table
                cmd_display = c.command.replace("|", "\\|")
                rc = str(c.returncode) if c.returncode is not None else "timeout"
                dur = f"{c.duration_seconds:.2f}s"
            lines.append(f"| {c.cmd_type} | `{cmd_display}` | {result_str} | {dur} | {rc} |")
        lines.append("")
        # Error logs for failing commands
        failing = [c for c in commands if not c.passed and not c.skipped]
        if failing:
            lines.append("## Failures")
            lines.append("")
            for c in failing:
                lines.append(f"### {c.cmd_type}: `{c.command}`")
                lines.append("")
                if c.stderr:
                    lines.append("**stderr:**")
                    lines.append("```")
                    lines.append(c.stderr[:2000])
                    lines.append("```")
                if c.stdout:
                    lines.append("**stdout:**")
                    lines.append("```")
                    lines.append(c.stdout[:2000])
                    lines.append("```")
                lines.append("")
        else:
            if passed and any(not c.skipped for c in commands):
                lines.append("All toolchain commands passed.")
                lines.append("")
        return "\n".join(lines)

    def run_sync(
        self,
        profile,
        task_id: int | None = None,
        cwd: str | Path | None = None,
    ) -> ToolchainResult:
        """Synchronous wrapper for tests and sync callers."""
        return asyncio.run(self.run(profile, task_id=task_id, cwd=cwd))
