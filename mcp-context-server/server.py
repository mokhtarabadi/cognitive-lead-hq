#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pathspec",
#     "mcp[cli]"
# ]
# ///

import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import pathspec
from mcp.server.fastmcp import FastMCP

class GitIgnoreFilter:
    """Evaluates paths against .gitignore files dynamically."""
    def __init__(self) -> None:
        self._specs: dict[Path, Optional[pathspec.PathSpec]] = {}

    def _get_spec(self, dir_path: Path) -> Optional[pathspec.PathSpec]:
        if dir_path in self._specs:
            return self._specs[dir_path]
        gitignore_file = dir_path / ".gitignore"
        if gitignore_file.is_file():
            try:
                with open(gitignore_file, "r", encoding="utf-8") as f:
                    spec = pathspec.PathSpec.from_lines("gitwildmatch", f)
                    self._specs[dir_path] = spec
                    return spec
            except Exception as e:
                print(f"Warning: Failed to read {gitignore_file}: {e}", file=sys.stderr)
        self._specs[dir_path] = None
        return None

    def is_ignored(self, path: Path) -> bool:
        abs_path = path.resolve()
        if ".git" in abs_path.parts or abs_path.name == ".git":
            return True
        current = abs_path.parent
        while True:
            spec = self._get_spec(current)
            if spec:
                try:
                    rel_path = abs_path.relative_to(current)
                    match_str = rel_path.as_posix()
                    if abs_path.is_dir() and not match_str.endswith("/"):
                        match_str += "/"
                    if spec.match_file(match_str):
                        return True
                except ValueError:
                    pass
            if current == current.parent:
                break
            current = current.parent
        return False

def is_binary(file_path: Path) -> bool:
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            if b"\0" in chunk:
                return True
            chunk.decode("utf-8")
            return False
    except Exception:
        return True

def generate_tree(dir_path: Path, ignore_filter: GitIgnoreFilter) -> str:
    lines = ["```text", dir_path.name or str(dir_path)]
    def _walk(current_path: Path, prefix: str) -> None:
        try:
            entries = list(current_path.iterdir())
        except PermissionError:
            lines.append(f"{prefix}└── [Permission Denied]")
            return
        valid_entries = [e for e in entries if not ignore_filter.is_ignored(e)]
        sorted_entries = sorted(valid_entries, key=lambda e: (not e.is_dir(), e.name.lower()))
        for i, entry in enumerate(sorted_entries):
            is_last = i == (len(sorted_entries) - 1)
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{entry.name}")
            if entry.is_dir():
                extension = "    " if is_last else "│   "
                _walk(entry, prefix + extension)
    _walk(dir_path, "")
    lines.append("```")
    return "\n".join(lines)

def process_source_file(file_path: Path, max_size: int, line_numbers: bool) -> str:
    lines = [f"### `{file_path}`", ""]
    if not file_path.exists():
        lines.append("> Skipped: (File not found)\n")
        return "\n".join(lines)
    try:
        size = file_path.stat().st_size
        if size > max_size:
            lines.append(f"> Skipped: (File too large: {size} bytes)\n")
            return "\n".join(lines)
    except OSError as e:
        lines.append(f"> Skipped: (OS Error: {e})\n")
        return "\n".join(lines)
    if is_binary(file_path):
        lines.append("> Skipped: (Binary file)\n")
        return "\n".join(lines)
    ext = file_path.suffix.lstrip(".") or "text"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            file_lines = f.read().split("\n")
        if file_lines and file_lines[-1] == "":
            file_lines.pop()
        if line_numbers:
            content = "\n".join(f"{i}: {line}" for i, line in enumerate(file_lines, 1))
        else:
            content = "\n".join(file_lines)
        lines.append(f"```{ext}")
        if content:
            lines.append(content)
        lines.append("```\n")
    except Exception as e:
        lines.append(f"> Skipped: (Error reading file: {e})\n")
    return "\n".join(lines)

def collect_files(target: str, ignore_filter: GitIgnoreFilter) -> list[Path]:
    p = Path(target)
    if not p.exists() or ignore_filter.is_ignored(p):
        return []
    if p.is_file():
        return [p]
    collected = []
    for root, dirs, files in os.walk(p):
        root_path = Path(root)
        dirs[:] = [d for d in dirs if not ignore_filter.is_ignored(root_path / d)]
        for f in files:
            file_path = root_path / f
            if not ignore_filter.is_ignored(file_path):
                collected.append(file_path)
    return collected

mcp = FastMCP("CustomContext")

@mcp.tool()
def get_directory_tree(target_path: str = ".") -> str:
    """Generates an ASCII tree representation of the directory, respecting .gitignore. Use this to discover codebase structure."""
    ignore_filter = GitIgnoreFilter()
    tree_path = Path(target_path)
    if not tree_path.is_dir():
        return f"Error: {target_path} is not a valid directory."
    if ignore_filter.is_ignored(tree_path):
        return f"Warning: Target tree path is ignored by .gitignore: {target_path}"
    return f"## Directory Tree: `{tree_path}`\n\n" + generate_tree(tree_path, ignore_filter)

@mcp.tool()
def read_source_files(paths: list[str], max_size: int = 1048576, no_line_numbers: bool = False) -> str:
    """Reads multiple source files/directories, compiles their contents into a Markdown file under context-reports/, and returns the report file path."""
    # Safeguard: Append context-reports/ to .gitignore if not present
    gitignore = Path(".gitignore")
    if gitignore.is_file():
        try:
            with open(gitignore, "r+", encoding="utf-8") as f:
                content = f.read()
                if "context-reports/" not in content:
                    f.write("\n# Custom Context MCP reports\ncontext-reports/\n")
        except Exception as e:
            print(f"Warning: Failed to update .gitignore: {e}", file=sys.stderr)

    ignore_filter = GitIgnoreFilter()
    files_to_process: dict[Path, Path] = {}
    for src in paths:
        # Safeguard: Do not recursively scan our own reports directory
        if "context-reports" in Path(src).parts:
            continue
        for p in collect_files(src, ignore_filter):
            if "context-reports" in p.parts:
                continue
            files_to_process[p.resolve()] = p

    if not files_to_process:
        return "No files found or all files were ignored."

    output_lines = ["## Source Files\n"]
    include_line_numbers = not no_line_numbers
    for _, f in sorted(files_to_process.items(), key=lambda item: str(item[1]).lower()):
        output_lines.append(process_source_file(f, max_size, include_line_numbers))

    result_content = "\n".join(output_lines)

    # Ensure output directory exists
    report_dir = Path("context-reports")
    report_dir.mkdir(exist_ok=True)

    # Generate timestamped filename
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"context_report_{timestamp}.md"

    # Write to file
    try:
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(result_content)
    except Exception as e:
        return f"Error writing report file: {e}"

    return (
        f"✅ Success: Compiled context for {len(files_to_process)} files.\n"
        f"📁 Generated Report: `{report_file}`\n\n"
        f"Manager: You can now open `{report_file}` in your local editor to view the codebase context or copy/paste it directly for the AI."
    )

@mcp.tool()
def extract_signatures(file_path: str) -> str:
    """Extracts structural signatures (classes, functions, methods) from source files using regex to prevent context bloat."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Match class, function, def, interface exports
        pattern = re.compile(r'^(?:export\s+)?(?:default\s+)?(?:class|func(?:tion)?|def|interface|type)\s+\w+.*$', re.MULTILINE)
        matches = pattern.findall(content)
        
        # Match const/let arrow functions
        arrow_pattern = re.compile(r'^(?:export\s+)?(?:const|let)\s+\w+\s*=\s*(?:async\s*)?(?:\([^)]*\)|[^=]*)\s*=>.*$', re.MULTILINE)
        arrow_matches = arrow_pattern.findall(content)
        
        all_matches = matches + arrow_matches
        if not all_matches:
            return f"No standard structural signatures found in {file_path}."
            
        return f"### Signatures in {file_path}\n" + "\n".join(all_matches)
    except Exception as e:
        return f"Error extracting signatures from {file_path}: {str(e)}"

@mcp.tool()
def stage_and_inject_diff(task_file_path: str) -> str:
    """Stages current changes via Git and intelligently injects the diff into the task file's Git Diff block."""
    try:
        # 1. Stage all changes
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        
        # 2. Extract the diff (EXCLUDING the entire tasks/ directory to prevent recursive diff bloat)
        # Using git pathspec magic ':!tasks/' to ignore the entire task folder
        diff_cmd = ["git", "diff", "--staged", "--", ".", ":!tasks/"]
        diff_process = subprocess.run(diff_cmd, capture_output=True, text=True)
        diff_text = diff_process.stdout.strip()
        
        if not diff_text:
            diff_text = "No code changes detected or staged."
            
        diff_block = f"\n```diff\n{diff_text}\n```\n"

        # 3. Read the task file
        with open(task_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 4. Smart Replacement using Regex (greedy match from first BEGIN to last END)
        # Using greedy .* to consume everything between the first BEGIN and the LAST END marker,
        # preventing corruption when injected diff content itself contains 'END_GIT_DIFF'
        pattern = re.compile(r'<!-- BEGIN_GIT_DIFF -->.*<!-- END_GIT_DIFF -->', re.DOTALL)
        
        if not pattern.search(content):
            return f"Error: Could not find the <!-- BEGIN_GIT_DIFF --> markers in {task_file_path}. Did you alter the template?"

        new_content = pattern.sub(lambda m: f'<!-- BEGIN_GIT_DIFF -->{diff_block}<!-- END_GIT_DIFF -->', content)

        # 5. Write back to the task file
        with open(task_file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return f"✅ Success: Changes staged and factual diff intelligently injected into {task_file_path}."

    except Exception as e:
        return f"❌ Error staging or updating task file: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
