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

from sentinel import TypeDriftSentinel
from blast_radius import (
    calculate_affected_paths,
    extract_modified_paths,
    find_owning_package,
)

try:
    from models import BlastRadiusConfig
except Exception:
    BlastRadiusConfig = None  # type: ignore


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
        workspace_root: str | Path | None = None,
        skip_unaffected: bool = True,
        blast_radius_config: "BlastRadiusConfig | None" = None,
    ):
        self.timeout_per_command = timeout_per_command
        self.evidence_base_dir = Path(evidence_base_dir)
        # Blast-radius scoping (LE-9 / Task 141): workspace_root defaults to
        # the repo root (parent of loop-engine/). skip_unaffected is the
        # legacy rollback flag — set False to always run full toolchain verification.
        # blast_radius_config is the spec-compliant config (enabled, workspace_globs, conservative_root_fallback).
        self.workspace_root = (
            Path(workspace_root)
            if workspace_root is not None
            else Path(__file__).resolve().parent.parent
        )
        self.skip_unaffected = skip_unaffected
        if blast_radius_config is not None:
            self.blast_radius_config = blast_radius_config
        elif BlastRadiusConfig is not None:
            # Default config when not provided — enabled with standard globs
            try:
                self.blast_radius_config = BlastRadiusConfig()
            except Exception:
                self.blast_radius_config = None
        else:
            self.blast_radius_config = None
        # Sync legacy flag with spec config for backward compat
        if self.blast_radius_config is not None and not self.skip_unaffected:
            # Legacy flag disables spec config as well (rollback)
            try:
                self.blast_radius_config.enabled = False
            except Exception:
                pass

    async def run(
        self,
        profile,  # StackProfile
        task_id: int | None = None,
        cwd: str | Path | None = None,
        diff_text: str = "",
    ) -> ToolchainResult:
        """Run toolchain commands sequentially.

        Order: Type Drift Sentinel (LE-7) -> lint, build, test. Null/whitespace
        commands are skipped as passed+skipped. Non-zero exit or timeout →
        passed=False.
        """
        # --- Type Drift Sentinel (LE-7) — fail-fast before any toolchain command ---
        # A hand-authored duplicate DTO/interface/model in a consumer path is a
        # hard violation: the toolchain fails immediately and the actionable
        # report is recorded as stderr so it reaches QA feedback, preventing
        # broken duplicate types from reaching LLM QA.
        if diff_text and str(diff_text).strip():
            try:
                sentinel_result = TypeDriftSentinel().check_diff(str(diff_text))
                if not sentinel_result.passed:
                    sentinel_cmd = CommandResult(
                        command="type-drift-sentinel",
                        cmd_type="lint",
                        passed=False,
                        skipped=False,
                        returncode=None,
                        stdout="",
                        stderr=sentinel_result.report_md,
                    )
                    return self._finalize([sentinel_cmd], task_id)
            except Exception as e:
                # Sentinel infra error must not block the toolchain (mirrors the
                # daemon's toolchain-infra-error tolerance). Log to the result.
                print(f"[verifier] Type Drift Sentinel error (proceeding): {e}")

        # --- Blast-Radius Global Scoping (LE-9 / Task 141 — Spec) ---
        # Spec path: if monorepo and 0 packages affected, skip entire toolchain.
        if diff_text and str(diff_text).strip():
            try:
                cfg = getattr(self, "blast_radius_config", None)
                if cfg is not None and getattr(cfg, "enabled", False):
                    modified_paths = extract_modified_paths(str(diff_text))
                    # cwd or REPO_ROOT per spec; use workspace_root as repo root fallback
                    effective_root = Path(cwd) if cwd is not None else self.workspace_root
                    # If cwd is a file path inside workspace, use its parent? Use workspace_root for matrix
                    # Spec says: calculate_affected_paths(modified_paths, cwd or REPO_ROOT, config)
                    matrix = calculate_affected_paths(modified_paths, self.workspace_root, cfg)
                    if getattr(matrix, "is_monorepo", False) and getattr(matrix, "is_empty", False):
                        note = "Blast-Radius: 0 packages affected"
                        skipped_commands: list[CommandResult] = [
                            CommandResult(command="none", cmd_type=t, passed=True, skipped=True)
                            for t in ("lint", "build", "test")
                        ]
                        # Append note to report_md via _finalize
                        return ToolchainResult(
                            passed=True,
                            commands=skipped_commands,
                            summary="Toolchain PASSED (Blast-Radius: 0 packages affected)",
                            report_md=f"# Toolchain Verification Report\n\nToolchain PASSED (Blast-Radius: 0 packages affected)\n\n**Blast-radius scoping:** {note}\n",
                        )
            except Exception as e:
                print(f"[verifier] Blast-radius global scoping error (proceeding): {e}")

        # --- Blast-Radius Workspace Scoping (LE-9 / Task 141 — Legacy per-workspace) ---
        # When the task diff touches only a subset of monorepo workspaces, a
        # completely unaffected workspace skips its lint/build/test (all
        # commands reported SKIPPED, result passes). The analyzer is
        # deliberately conservative: it only skips when it can PROVE the
        # verified workspace is unaffected, so affected modules are never
        # silently missed (Task 141 Risk & Rollback).
        if self.skip_unaffected and diff_text and str(diff_text).strip():
            blast_note = self._blast_radius_note(diff_text, cwd)
            if blast_note:
                skipped_commands: list[CommandResult] = [
                    CommandResult(command="none", cmd_type=t, passed=True, skipped=True)
                    for t in ("lint", "build", "test")
                ]
                return self._finalize(
                    skipped_commands, task_id, blast_radius_note=blast_note
                )

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
        self,
        commands: list[CommandResult],
        task_id: int | None,
        blast_radius_note: str = "",
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
        if blast_radius_note:
            summary += f" | {blast_radius_note}"

        # Markdown report with summary table and error logs
        report_md = self._build_report_md(commands, passed, summary, blast_radius_note)

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
        self,
        commands: list[CommandResult],
        passed: bool,
        summary: str,
        blast_radius_note: str = "",
    ) -> str:
        lines: list[str] = []
        lines.append("# Toolchain Verification Report")
        lines.append("")
        lines.append(summary)
        lines.append("")
        if blast_radius_note:
            lines.append(f"**Blast-radius scoping:** {blast_radius_note}")
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

    def is_workspace_affected(
        self, diff_text: str, cwd: str | Path | None = None
    ) -> bool:
        """True when verification must run for the workspace at ``cwd``.

        Returns False only when blast-radius analysis PROVES the workspace
        (a discovered monorepo package, or the root package) is completely
        unaffected by the diff. Conservative bias: any uncertainty — no cwd,
        a non-monorepo layout, root-owned files, or a cwd outside the
        package graph — returns True so the toolchain always runs.
        """
        return self._blast_radius_note(diff_text, cwd) == ""

    def _blast_radius_note(self, diff_text: str, cwd: str | Path | None) -> str:
        """Return a skip note when ``cwd`` is provably unaffected, else "".

        The empty string means "run verification". A non-empty note is a
        human-readable explanation appended to the summary/report so skipped
        workspaces are observable in QA evidence.
        """
        if not cwd:
            return ""
        try:
            cwd_path = Path(cwd).resolve()
        except OSError:
            return ""
        try:
            root = Path(self.workspace_root).resolve()
        except OSError:
            return ""
        modified = extract_modified_paths(str(diff_text))
        if not modified:
            return ""
        try:
            matrix = calculate_affected_paths(modified, root)
        except OSError:
            return ""  # analyzer failure must never skip
        if not matrix.packages:
            return ""  # not a proven monorepo → conservative full verification
        if matrix.root_owned_files:
            return ""  # change outside the package graph → conservative
        try:
            cwd_rel = cwd_path.relative_to(root).as_posix()
        except ValueError:
            return ""  # cwd outside the workspace root → cannot scope
        owner = find_owning_package(cwd_rel, matrix.packages)
        if owner is None:
            return ""  # cwd not inside any discovered package → conservative
        if owner.name in matrix.affected_packages:
            return ""
        return (
            f"Blast-radius scoping: workspace `{owner.name}` ({owner.path}) "
            f"is unaffected by this diff — skipping unrelated toolchain verification"
        )

    def run_sync(
        self,
        profile,
        task_id: int | None = None,
        cwd: str | Path | None = None,
        diff_text: str = "",
    ) -> ToolchainResult:
        """Synchronous wrapper for tests and sync callers."""
        return asyncio.run(self.run(profile, task_id=task_id, cwd=cwd, diff_text=diff_text))
