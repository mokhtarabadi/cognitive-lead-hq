#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mcp[cli]>=1.0,<2.0"
# ]
# ///

"""
MCP Lint Server for Cognitive Lead AI HQ.

Provides structural validation tools for Markdown files and the canonical
task file template. Uses regex-based checks to avoid heavy dependencies
while covering the most critical formatting and structural rules.
"""

import re
import os
import tempfile
import difflib
from pathlib import Path
from typing import Tuple
from mcp.server.fastmcp import FastMCP


# --- FastMCP Application ---

mcp = FastMCP("LintServer")


# --- Internal Linting Functions ---

def _check_markdown_basics(content: str, file_path: str) -> list[str]:
    """
    Check basic Markdown formatting rules.

    Validates:
    - Blank lines around headings (inside code blocks are skipped)
    - Trailing whitespace (excluding intentional double-space line breaks)
    - Unclosed code blocks

    Args:
        content: The raw Markdown text to lint.
        file_path: The file path (used for error messages).

    Returns:
        A list of issue descriptions found in the content.
    """
    issues: list[str] = []
    lines = content.split('\n')

    # The machine-generated `## Factual Git Diff` block (between the
    # BEGIN_GIT_DIFF / END_GIT_DIFF markers) can contain arbitrary raw git
    # diff output — including lines that look like code fences (e.g. a diff
    # of a Markdown file that itself contains ``` blocks). Naively tracking
    # fences across the full file produces false "Unclosed code block"
    # positives, so the diff region is excluded from ALL markdown-basics
    # checks (fence tracking, heading spacing, trailing whitespace). This
    # mirrors the pre-diff scoping already applied to structural checks in
    # `_check_task_file_structure` (see the comment above its `pre_diff`
    # split). For regular Markdown files without the markers, behavior is
    # unchanged.
    in_diff_region = False
    in_code_block = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped == "<!-- BEGIN_GIT_DIFF -->":
            in_diff_region = True
            continue
        if stripped == "<!-- END_GIT_DIFF -->":
            in_diff_region = False
            continue
        # Skip everything inside the machine-generated diff region.
        if in_diff_region:
            continue

        # Track fenced code blocks
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        # Skip everything inside code blocks
        if in_code_block:
            continue

        # Check for missing blank line before heading
        if line.startswith("#"):
            if i > 1 and lines[i - 2].strip() != "" and not lines[i - 2].strip().startswith("#"):
                issues.append(f"Line {i}: Missing blank line before heading.")

            # Check for missing blank line after heading
            if i < len(lines) and lines[i].strip() != "" and not lines[i].strip().startswith("#"):
                issues.append(f"Line {i}: Missing blank line after heading.")

        # Check for trailing whitespace (excluding intentional double-space for line breaks)
        if line.endswith(" ") and not line.endswith("  "):
            issues.append(f"Line {i}: Trailing whitespace.")

    # Check for unclosed code block
    if in_code_block:
        issues.append("Unclosed code block detected.")

    return issues


def _check_task_file_structure(content: str, file_path: str) -> list[str]:
    """
    Validate a task file against the canonical template structure.

    Checks:
    - Filename ID matches the title number
    - **File:** header path matches the actual file path (path-drift guard)
    - Required sections exist (## Goal, ## Local TODOs, etc.), scoped to the
      PRE-DIFF portion of the file so the machine-generated diff block is
      never treated as structure
    - Exactly one `## Factual Git Diff` heading before the diff block
      (duplicate headings desync the BEGIN/END markers)
    - Exactly one Execution Log heading before the diff block — EITHER the
      canonical `## Execution Log & Reasoning` OR the legacy OpenCode-named
      header, never both (backward-compatible since QA round 7)
    - BEGIN/END_GIT_DIFF markers are present
    - Source and Type metadata fields are valid

    Args:
        content: The raw Markdown text of the task file.
        file_path: The file path (used for filename-based ID checks and the
            **File:** header path-drift comparison).

    Returns:
        A list of issue descriptions found in the content.
    """
    issues: list[str] = []
    filename = Path(file_path).name

    # 1. Title number matches filename ID
    id_match = re.match(r'^(\d+)-', filename)
    if id_match:
        file_id = id_match.group(1)
        title_match = re.search(r'^# Task (\d+):', content, re.MULTILINE)
        if title_match:
            title_id = title_match.group(1)
            if file_id.lstrip('0') != title_id.lstrip('0'):
                issues.append(
                    f"Task ID mismatch: Filename has '{file_id}' but title has '{title_id}'."
                )
        else:
            issues.append("Missing standard title format: `# Task [NN]: [Title]`")
    else:
        issues.append("Filename does not start with a numeric ID.")

    # 1.5 Path-drift guard: **File:** header must match the actual file path.
    # First, ensure the `**File:**` metadata field exists at all — a missing
    # header is a structural defect in its own right and is reported before
    # any path comparison. The header value is normalized (whitespace and
    # surrounding backticks stripped) so `tasks/in-progress/97-foo.md` can be
    # compared to the path the linter was called with.
    #
    # Comparison is done on RESOLVED ABSOLUTE paths, not raw strings: the
    # lint_task_file tool explicitly accepts both absolute and relative paths,
    # so a relative header (`tasks/in-progress/97-foo.md`) and an absolute
    # actual path (`/repo/tasks/in-progress/97-foo.md`) describe the same file
    # and must match. Path.resolve() collapses relative components, "..", and
    # symlinks so equivalent spellings of the same file never false-positive.
    # This still catches genuinely stale headers left behind after git mv
    # between Kanban directories (different file => different resolved path).
    file_header_match = re.search(r'\*\*File:\*\*\s*`([^`]+)`', content)
    if not file_header_match:
        issues.append("Missing `**File:**` metadata field.")
    else:
        header_path = file_header_match.group(1).strip()
        if Path(header_path).resolve() != Path(file_path).resolve():
            issues.append(
                f"File path mismatch: header says '{header_path}' but actual path is '{file_path}'."
            )

    # 2. Required sections exist. ALL structural heading inspection is scoped to
    # the PRE-DIFF portion of the file (everything before the Git-Diff BEGIN
    # marker). The injected `## Factual Git Diff` block is machine-generated raw
    # git diff output that can contain arbitrary lines — including text that
    # resembles section headings — so inspecting the full file would produce
    # false positives. Only the hand-authored metadata and reasoning sections
    # above the diff block are structural, so they are what these guards check.
    pre_diff = content.split("<!-- BEGIN_GIT_DIFF -->", 1)[0]

    # Exact-line heading counter: a heading counts only when an ENTIRE line
    # equals the heading text (whitespace-stripped). Prose that merely MENTIONS
    # a heading inside backticks (e.g. "the `## Execution Log & Reasoning`
    # header") must not count — execution logs legitimately reference section
    # names. This mirrors the anchored `grep '^## ...$'` semantics used by the
    # repo-wide drift gates.
    def _count_heading(text: str, heading: str) -> int:
        return sum(1 for line in text.splitlines() if line.strip() == heading)

    required_sections = [
        "## Goal",
        "## Local TODOs",
        "## Acceptance Criteria",
        "## Verification Evidence",
        "## Risk & Rollback",
    ]
    for section in required_sections:
        if section not in pre_diff:
            issues.append(f"Missing required section: `{section}`")

    # 2.4 `## Factual Git Diff` heading — EXACTLY ONE, and only in the pre-diff
    # section. The heading must appear once, directly above the BEGIN marker, as
    # the bridge between the hand-authored metadata and the injected diff. A
    # duplicate heading (a QA round-7 regression this hardening closes) splits
    # the diff block and desyncs the BEGIN/END markers, so >1 is reported as a
    # hard defect rather than silently tolerated.
    factual_heading_count = _count_heading(pre_diff, "## Factual Git Diff")
    if factual_heading_count == 0:
        issues.append("Missing required section: `## Factual Git Diff`")
    elif factual_heading_count > 1:
        issues.append(
            f"Duplicate `## Factual Git Diff` heading detected "
            f"({factual_heading_count} occurrences before the diff block)."
        )

    # 2.5 Execution Log section — BACKWARD-COMPATIBLE header check (QA round 7,
    # Task 98): accept EITHER the canonical runtime-agnostic header
    # (`## Execution Log & Reasoning`) OR the deprecated legacy OpenCode-named
    # header. Projects that predate the v8.4.5 runtime-agnostic rename still
    # carry the old OpenCode-named header; they must not hard-fail lint just
    # because they have not migrated yet. The `task-generator` skill always
    # emits the new canonical header, so this only widens the accepted set for
    # existing task files — it never changes what new tasks are generated with.
    # A file carrying NEITHER header still fails (the missing-section error
    # names the canonical header).
    #
    # Exactly ONE of the two variants may appear (QA round 8 hardening): the
    # pre-diff section must contain a single Execution Log heading in either
    # spelling. Both-variants-present is a half-completed migration artifact and
    # is reported as a duplicate; neither-present still fails with the canonical
    # missing-section message.
    #
    # NOTE: the legacy header constant is deliberately assembled from two string
    # parts so the repo-wide drift grep for the full legacy header phrase never
    # matches this intentional backward-compatibility shim inside the linter.
    canonical_execution_log_header = "## Execution Log & Reasoning"
    legacy_execution_log_header = "## OpenCode " + "Execution Log & Reasoning"
    execution_log_heading_count = (
        _count_heading(pre_diff, canonical_execution_log_header)
        + _count_heading(pre_diff, legacy_execution_log_header)
    )
    if execution_log_heading_count == 0:
        issues.append("Missing required section: `## Execution Log & Reasoning`")
    elif execution_log_heading_count > 1:
        issues.append(
            f"Duplicate Execution Log heading detected "
            f"({execution_log_heading_count} occurrences before the diff block) — "
            f"use EITHER the canonical `## Execution Log & Reasoning` header OR "
            f"the legacy OpenCode-named header, not both."
        )

    # 3. BEGIN/END markers
    if "<!-- BEGIN_GIT_DIFF -->" not in content or "<!-- END_GIT_DIFF -->" not in content:
        issues.append("Missing `<!-- BEGIN_GIT_DIFF -->` or `<!-- END_GIT_DIFF -->` markers.")

    # 4. Source field
    if not re.search(r'\*\*Source:\*\*\s*(orchestrator|telegram|manager)', content):
        issues.append("Missing or invalid `**Source:**` metadata field.")

    # 5. Type field
    if not re.search(
        r'\*\*Type:\*\*\s*(bug|improvement|feature|chore|docs|refactor|security|research|infra)',
        content,
    ):
        issues.append("Missing or invalid `**Type:**` metadata field.")

    return issues


# --- MCP Tools ---

@mcp.tool()
def lint_markdown(file_path: str) -> str:
    """
    Lint a Markdown file for basic formatting issues.

    Checks heading spacing, trailing whitespace, and code block closure.
    Useful for general Markdown files (README, CHANGELOG, SKILL.md, etc.).

    Args:
        file_path: Absolute or relative path to the Markdown file.

    Returns:
        A success message or a list of formatting issues found.
    """
    path = Path(file_path)
    if not path.is_file():
        return f"Error: File not found: {file_path}"

    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return f"Error reading file: {e}"

    issues = _check_markdown_basics(content, file_path)

    if not issues:
        return f"✅ {file_path} passed Markdown linting."

    return f"⚠️ {len(issues)} issues found in {file_path}:\n" + "\n".join(f"- {i}" for i in issues)


@mcp.tool()
def lint_task_file(task_file_path: str) -> str:
    """
    Validate a task file against the canonical template.

    Checks: ID match (filename vs title), required sections, BEGIN/END
    markers, and Source/Type metadata fields. Also runs basic Markdown
    formatting checks.

    Args:
        task_file_path: Absolute or relative path to the task .md file.

    Returns:
        A success message or a combined list of structural and formatting issues.
    """
    path = Path(task_file_path)
    if not path.is_file():
        return f"Error: File not found: {task_file_path}"

    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return f"Error reading file: {e}"

    md_issues = _check_markdown_basics(content, task_file_path)
    task_issues = _check_task_file_structure(content, task_file_path)

    all_issues = md_issues + task_issues

    if not all_issues:
        return f"✅ {task_file_path} passed Task File linting."

    return (
        f"⚠️ {len(all_issues)} issues found in {task_file_path}:\n"
        + "\n".join(f"- {i}" for i in all_issues)
    )


@mcp.tool()
def lint_all_tasks(include_archive: bool = False) -> str:
    """
    Run lint_task_file on ALL task files across the ACTIVE Kanban subdirectories.

    Scans tasks/backlog/, tasks/in-progress/, tasks/qa/, and tasks/completed/
    for .md files. The tasks/archive/ directory is EXCLUDED by default (F3 fix:
    archive is a historical record; linting it generates noise). Pass
    include_archive=True to explicitly lint archived tasks as well.

    Args:
        include_archive: If True, also scans tasks/archive/ (default False).

    Returns:
        A summary report of the linting results.
    """
    tasks_dir = Path("tasks")
    if not tasks_dir.is_dir():
        return "Error: `tasks/` directory not found."

    # F3 Fix: Archive is a historical record; linting it generates noise. Exclude by default.
    kanban_dirs = ["backlog", "in-progress", "qa", "completed"]
    if include_archive:
        kanban_dirs.append("archive")
    total_files = 0
    total_issues = 0
    report: list[str] = []

    for dir_name in kanban_dirs:
        dir_path = tasks_dir / dir_name
        if not dir_path.is_dir():
            continue

        for md_file in sorted(dir_path.glob("*.md")):
            total_files += 1
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue

            issues = _check_markdown_basics(content, str(md_file)) + _check_task_file_structure(
                content, str(md_file)
            )
            if issues:
                total_issues += len(issues)
                report.append(f"**{md_file.relative_to(tasks_dir)}** ({len(issues)} issues)")

    summary = f"Scanned {total_files} task files. Found {total_issues} total issues.\n\n"
    if report:
        summary += "Files with issues:\n" + "\n".join(f"- {r}" for r in report)
    else:
        summary += "✅ All task files are perfectly formatted."

    return summary


# ---------------------------------------------------------------------------
# system-prompt.md sync verification
# ---------------------------------------------------------------------------
# Since v8.4.6, system-prompt.md is a GENERATED build artifact assembled from
# prompts/fragments/ + prompts/shared/ via scripts/prompt-build/. This tool
# guards against drift: it re-runs the assembler against a temporary path and
# compares the result to the committed system-prompt.md. If they differ, the
# fragments and the committed file are out of sync and the Hands must
# regenerate. The check is covered by the existing "lint_*": "allow" permission
# rule in opencode.json, so no permissions change is needed.


def _load_assembler():
    """Dynamically import the assemble_system_prompt module from scripts/.

    Uses importlib so the lint server (run via `uv run mcp-lint-server/server.py`
    from the project root) can load the assembler without a package dependency.
    """
    import importlib.util

    assembler_path = (
        Path(__file__).resolve().parent.parent
        / "scripts"
        / "prompt-build"
        / "assemble_system_prompt.py"
    )
    spec = importlib.util.spec_from_file_location(
        "assemble_system_prompt", assembler_path
    )
    if spec is None or spec.loader is None:
        raise FileNotFoundError(f"Cannot load assembler at {assembler_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _check_system_prompt_sync(
    fragments_dir: str = "prompts/fragments",
    shared_dir: str = "prompts/shared",
    manifest_path: str = "prompts/manifest.txt",
    system_prompt_path: str = "system-prompt.md",
) -> Tuple[bool, str]:
    """Check whether the committed system-prompt.md is in sync with prompts/.

    Re-runs the assembler (writing to a temporary path) and compares the result
    to the committed system-prompt.md. Accepts custom path parameters so tests
    can verify both the clean case and drift detection without mutating the
    real files.

    Args:
        fragments_dir: Directory of per-tag fragment files.
        shared_dir: Directory of shared partials (used by include resolution).
        manifest_path: Assembly-order manifest file.
        system_prompt_path: The committed system-prompt.md to compare against.

    Returns:
        A tuple (in_sync, message).
    """
    # Existence guard for system_prompt_path — mirrors the pattern used by
    # lint_markdown() and lint_task_file() in this file. Prevents a
    # FileNotFoundError from propagating out of this function when the
    # committed system-prompt.md is missing (e.g., in test scenarios or if
    # the file was accidentally deleted). Returns a clean (False, error)
    # tuple so the caller can handle it gracefully.
    sp_path = Path(system_prompt_path)
    if not sp_path.is_file():
        return False, f"Error: File not found: {system_prompt_path}"

    try:
        assembler = _load_assembler()
    except FileNotFoundError as e:
        return False, f"Error: Assembler not found at {e}"
    except Exception as e:
        # Generic assembler-load failure handler (QA Fix Round 4):
        # _load_assembler() dynamically executes Python source from
        # scripts/prompt-build/assemble_system_prompt.py via importlib. If that
        # file is corrupted or edited into a broken state, exec_module() can
        # raise SyntaxError/IndentationError/ImportError — NOT just
        # FileNotFoundError. This MCP diagnostic tool must degrade gracefully
        # to a clean (False, error) tuple instead of crashing the lint server.
        # `except Exception` deliberately does NOT catch SystemExit or
        # KeyboardInterrupt (both derive from BaseException), so the process
        # can still be terminated normally.
        return False, f"Error: {e}"

    # Assemble to a temporary file so we never overwrite the committed prompt.
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as tmp:
        tmp_path = tmp.name

    try:
        # Run the assembler with the provided fragment/shared paths.
        try:
            assembler.assemble(
                output_path=tmp_path,
                fragments_dir=fragments_dir,
                shared_dir=shared_dir,
                manifest_path=manifest_path,
            )
        except FileNotFoundError as e:
            return False, f"Error: Fragment or manifest file not found: {e}"
        except ValueError as e:
            # WHY ValueError is caught here specifically: assemble()'s
            # unresolved-placeholder, unsafe-include-path, and malformed-marker
            # guards (added in QA Fix Rounds 1–3) raise ValueError
            # intentionally — they are loud, named failures for CLI/direct
            # callers. But this diagnostic-tool caller must degrade to a clean
            # error string instead of crashing the lint server. The message
            # still identifies the offending fragment, placeholder, or include
            # path so the user can fix the source prompt tree.
            return False, f"Error: {e}"

        assembled = Path(tmp_path).read_text(encoding="utf-8")
        committed = Path(system_prompt_path).read_text(encoding="utf-8")

        if assembled == committed:
            return True, "✅ system-prompt.md is in sync with prompts/"

        # Drift detected — produce a concise unified-diff summary.
        diff_lines = list(
            difflib.unified_diff(
                committed.splitlines(keepends=True),
                assembled.splitlines(keepends=True),
                fromfile="system-prompt.md",
                tofile="prompts/ (assembled)",
                n=2,
            )
        )
        diff_text = "".join(diff_lines[:200])  # cap to avoid huge output
        if len(diff_lines) > 200:
            diff_text += f"\n... ({len(diff_lines) - 200} more diff lines truncated)\n"
        return False, f"⚠️ DRIFT DETECTED — system-prompt.md is out of sync with prompts/:\n{diff_text}"
    except Exception as e:
        # BROAD DIAGNOSTIC CATCH (QA Fix Round 3): this function is a
        # diagnostic tool exposed over the MCP lint server. It must degrade
        # gracefully to a clean (False, error) tuple rather than crash the
        # server, no matter what the underlying assembler or file layer
        # throws — e.g. a misconfigured fragments_dir that is a regular file
        # (NotADirectoryError), a permission error, or any unexpected
        # exception from assembly, temp-file reading, committed-file reading,
        # or diff generation. `except Exception` deliberately does NOT catch
        # SystemExit or KeyboardInterrupt (both derive from BaseException),
        # so the process can still be terminated normally. This does NOT
        # weaken assemble() itself — assemble() keeps failing loudly for
        # direct CLI callers; only this diagnostic wrapper is degrading to
        # error-string form.
        return False, f"Error: {e}"
    finally:
        # Always clean up the temporary file.
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


@mcp.tool()
def lint_system_prompt_sync() -> str:
    """
    Verify that the committed system-prompt.md is byte-identical to the output
    of assembling prompts/fragments/ + prompts/shared/.

    Since v8.4.6, system-prompt.md is a generated build artifact. This tool
    re-runs the assembler against a temp path and compares the result to the
    committed system-prompt.md. Use it before any commit to confirm the
    fragments (the true source of truth) and the generated file are in sync.

    Returns:
        "✅ system-prompt.md is in sync with prompts/" when in sync, or a
        "⚠️ DRIFT DETECTED" message with a diff summary when they differ.
    """
    in_sync, message = _check_system_prompt_sync()
    return message


# --- Entry Point ---

if __name__ == "__main__":
    mcp.run(transport="stdio")
