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
from pathlib import Path
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

    in_code_block = False
    for i, line in enumerate(lines, 1):
        # Track fenced code blocks
        if line.strip().startswith("```"):
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
    - Required sections exist (## Goal, ## Local TODOs, etc.)
    - BEGIN/END_GIT_DIFF markers are present
    - Source and Type metadata fields are valid

    Args:
        content: The raw Markdown text of the task file.
        file_path: The file path (used for filename-based ID checks).

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

    # 2. Required sections exist
    required_sections = [
        "## Goal",
        "## Local TODOs",
        "## OpenCode Execution Log & Reasoning",
        "## Factual Git Diff",
    ]
    for section in required_sections:
        if section not in content:
            issues.append(f"Missing required section: `{section}`")

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
def lint_all_tasks() -> str:
    """
    Run lint_task_file on ALL task files across all Kanban subdirectories.

    Scans tasks/backlog/, tasks/in-progress/, tasks/qa/, tasks/completed/,
    and tasks/archive/ for .md files. Outputs a summary report with total
    files scanned, total issues found, and a per-file breakdown.

    Returns:
        A summary report of the linting results.
    """
    tasks_dir = Path("tasks")
    if not tasks_dir.is_dir():
        return "Error: `tasks/` directory not found."

    kanban_dirs = ["backlog", "in-progress", "qa", "completed", "archive"]
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


# --- Entry Point ---

if __name__ == "__main__":
    mcp.run(transport="stdio")
