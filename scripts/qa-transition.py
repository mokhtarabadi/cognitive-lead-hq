#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Atomic QA Transition Tool — Task 154

Unifies Kanban QA transition into a single deterministic operation:
  git mv tasks/in-progress/<task>.md → tasks/qa/<task>.md
  + **File:** header sync to tasks/qa/
  + git add -- <modified_files> <dest_task>
  + git diff --staged -- . ':!tasks/' injection into the QA task file

This eliminates the two-pass friction (stage → mv → header patch → re-stage)
that caused stale **File:** headers and desynced diffs when the second staging
was skipped.

Usage:
  uv run scripts/qa-transition.py --task tasks/in-progress/154-foo.md --files file1.py file2.md
  uv run scripts/qa-transition.py --task tasks/in-progress/154-foo.md
  # legacy positional form also accepted:
  uv run scripts/qa-transition.py tasks/in-progress/154-foo.md file1.py file2.md

Exit codes:
  0 — success
  1 — validation / git / I/O failure (message on stderr)

Security & correctness:
  - Resolves task path against repo root and rejects traversal outside workspace
  - Validates source is inside tasks/in-progress/ (Path.relative_to guard)
  - Fallback for untracked files: shutil.move + git add when git mv fails
  - Header rewrite uses the same regex the linter validates (literal `**File:**` line)
  - Final confirmation re-reads **File:** and fails if it mismatches dest
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a subprocess, capturing output; raise on failure if check=True."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        msg = result.stderr.strip() or result.stdout.strip() or f"command failed: {' '.join(cmd)}"
        raise RuntimeError(msg)
    return result


def _git_mv_or_fallback(src: Path, dst: Path) -> None:
    """Move src → dst via git mv, fallback to filesystem mv + git add for untracked files."""
    # Ensure destination directory exists
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        _run(["git", "mv", str(src), str(dst)], check=True)
    except RuntimeError as e:
        # Fallback for untracked or git-mv failure: filesystem move + git add
        # Mirrors scripts/bundle-tasks.py fallback
        if not src.exists():
            raise RuntimeError(f"Source task file not found: {src} ({e})") from e
        try:
            shutil.move(str(src), str(dst))
        except Exception as move_err:
            raise RuntimeError(f"Fallback move failed: {src} → {dst}: {move_err}") from move_err
        # Stage the moved file via git add (so diff injection sees it if needed)
        try:
            _run(["git", "add", "--", str(dst)], check=True)
        except RuntimeError as add_err:
            # Non-fatal: the file is at least moved; staging failure is surfaced later
            print(f"Warning: fallback git add failed for {dst}: {add_err}", file=sys.stderr)


def _rewrite_file_header(task_path: Path, new_file_value: str) -> None:
    """Rewrite the **File:** metadata line to new_file_value.

    Mirrors mcp-lint-server path-drift guard: header is `**File:** `tasks/...``
    """
    content = task_path.read_text(encoding="utf-8")
    # Match **File:** `...`  — capture whole line
    pattern = re.compile(r"\*\*File:\*\*\s*`[^`]+`")
    replacement = f"**File:** `{new_file_value}`"
    if not pattern.search(content):
        raise RuntimeError(f"Could not find **File:** header in {task_path}")
    new_content = pattern.sub(replacement, content, count=1)
    task_path.write_text(new_content, encoding="utf-8")


def _inject_diff(task_path: Path, modified_files: list[str]) -> None:
    """Stage files + dest task, extract staged diff (excluding tasks/), inject into task."""
    # Stage explicitly listed files + the dest task file
    files_to_stage: list[str] = []
    if modified_files:
        files_to_stage.extend(modified_files)
    files_to_stage.append(str(task_path))

    # Filter to existing paths for git add? Keep as-is so git reports missing files
    # but avoid staging non-existent entries that would error
    # We let git add handle it; if a listed file doesn't exist, git add will error
    _run(["git", "add", "--"] + files_to_stage, check=True)

    # Extract diff excluding tasks/ directory (pathspec magic)
    diff_cmd = ["git", "diff", "--staged", "--", ".", ":!tasks/"]
    diff_proc = _run(diff_cmd, check=False)
    diff_text = diff_proc.stdout.strip()
    if not diff_text:
        diff_text = "No code changes detected or staged."
    diff_block = f"\n```diff\n{diff_text}\n```\n"

    content = task_path.read_text(encoding="utf-8")
    # Greedy from first BEGIN to last END to avoid corruption when diff contains END marker
    pattern = re.compile(r"<!-- BEGIN_GIT_DIFF -->.*<!-- END_GIT_DIFF -->", re.DOTALL)
    if not pattern.search(content):
        raise RuntimeError(f"Could not find <!-- BEGIN_GIT_DIFF --> markers in {task_path}")
    new_content = pattern.sub(lambda m: f"<!-- BEGIN_GIT_DIFF -->{diff_block}<!-- END_GIT_DIFF -->", content)
    task_path.write_text(new_content, encoding="utf-8")
    # Re-stage the task file after injection so the final QA file state is staged (header + diff)
    _run(["git", "add", "--", str(task_path)], check=True)


def _confirm_header(task_path: Path, expected: str) -> None:
    content = task_path.read_text(encoding="utf-8")
    m = re.search(r"\*\*File:\*\*\s*`([^`]+)`", content)
    if not m:
        raise RuntimeError(f"**File:** header missing after injection in {task_path}")
    actual = m.group(1).strip()
    # Resolve comparison like linter does, but also allow exact string match for simplicity
    if actual != expected:
        # Also try resolved path comparison for tolerance
        try:
            if Path(actual).resolve() != Path(expected).resolve():
                raise RuntimeError(f"File header mismatch: header says '{actual}' but expected '{expected}'")
        except Exception:
            raise RuntimeError(f"File header mismatch: header says '{actual}' but expected '{expected}'")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Atomic QA transition: git mv + **File:** header sync + staged diff injection"
    )
    parser.add_argument(
        "--task",
        dest="task",
        help="Path to task file in tasks/in-progress/ (mandatory)",
    )
    parser.add_argument(
        "--files",
        dest="files",
        nargs="*",
        default=[],
        help="Modified code files to stage (optional, default empty)",
    )
    # Legacy positional fallback: allow `qa-transition.py <task> [files...]` without flags
    parser.add_argument(
        "positional",
        nargs="*",
        help="Legacy positional: <task> [files...] when --task not used",
    )
    args = parser.parse_args(argv)

    # Resolve legacy positional form
    if not args.task and args.positional:
        args.task = args.positional[0]
        # Remaining positional items are files if --files not already set
        if args.positional[1:] and not args.files:
            args.files = args.positional[1:]
    elif args.task and args.positional:
        # If --task is set, treat remaining positional as extra files
        args.files = (args.files or []) + args.positional

    if not args.task:
        parser.error("--task <path> is required (or positional <task>)")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    # Resolve workspace root
    workspace_root = Path.cwd().resolve()
    # Security: task path must be within workspace
    task_input = Path(args.task)
    # Keep original for error messages
    original_task_str = str(task_input)

    # Resolve task path: if relative, resolve against cwd; if absolute, keep
    try:
        task_src = task_input.resolve()
        task_src.relative_to(workspace_root)
    except ValueError:
        print(f"Error: task path escapes workspace: {original_task_str}", file=sys.stderr)
        return 1

    # Also need to handle case where file is not yet moved but path is tasks/in-progress/...
    # For validation, check the *logical* relative path
    try:
        rel = task_src.relative_to(workspace_root)
    except ValueError:
        rel = Path(original_task_str)

    # Validate source is inside tasks/in-progress/
    # Use the relative path string to check prefix regardless of resolved symlinks
    rel_posix = rel.as_posix() if isinstance(rel, Path) else str(rel)
    # Normalize: if absolute task_src exists, compute its relative posix
    if task_src.exists():
        try:
            rel_check = task_src.relative_to(workspace_root).as_posix()
        except ValueError:
            rel_check = original_task_str
    else:
        rel_check = original_task_str

    if not rel_check.startswith("tasks/in-progress/"):
        print(
            f"Error: task path must be inside tasks/in-progress/, got: {original_task_str}",
            file=sys.stderr,
        )
        return 1

    if not task_src.exists():
        print(f"Error: task file not found: {task_src}", file=sys.stderr)
        return 1

    # Compute target path in tasks/qa/
    task_name = task_src.name
    dest = workspace_root / "tasks" / "qa" / task_name
    # Also compute the repo-relative expected header value
    expected_header = f"tasks/qa/{task_name}"

    # Validate .md extension (guard against misuse)
    if not task_name.endswith(".md"):
        print(f"Error: task file must be a Markdown file (*.md), got: {task_name}", file=sys.stderr)
        return 1

    try:
        # 1. Move file
        _git_mv_or_fallback(task_src, dest)

        # 2. Rewrite **File:** header to tasks/qa/...
        _rewrite_file_header(dest, expected_header)

        # 3. Stage + diff injection
        _inject_diff(dest, args.files or [])

        # 4. Confirm header
        _confirm_header(dest, expected_header)

    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

    print(f"✅ QA transition complete: {original_task_str} → {expected_header}")
    if args.files:
        print(f"   Staged files: {', '.join(args.files)}")
    else:
        print("   No code files staged (only task file — diff will be empty sentinel)")
    print(f"   Header synced and diff injected into {expected_header}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
