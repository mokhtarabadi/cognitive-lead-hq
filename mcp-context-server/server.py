#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pathspec",
#     "mcp[cli]>=1.0,<2.0",
#     "tree-sitter",
#     "tree-sitter-python",
#     "tree-sitter-javascript",
#     "tree-sitter-typescript",
#     "tree-sitter-go",
#     "tree-sitter-java",
#     "tree-sitter-rust",
#     "tree-sitter-kotlin",
# ]
# ///

import importlib
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
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

TEXT_ENCODINGS = ["utf-8", "utf-8-sig", "windows-1256", "windows-1252", "latin-1"]

def is_binary(file_path: Path) -> bool:
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            return b"\0" in chunk
    except Exception:
        return True

# --- Tree-sitter AST signature extraction ---

_EXTENSION_LANG_MAP: dict[str, str] = {
    ".py": "python",
    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".ts": "typescript", ".tsx": "typescript", ".mts": "typescript", ".cts": "typescript",
    ".go": "go",
    ".java": "java", ".jsp": "java",
    ".rs": "rust",
    ".kt": "kotlin", ".kts": "kotlin",
    ".swift": "swift",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "c_sharp",
}

_TS_QUERIES: dict[str, list[str]] = {
    "python": [
        '(function_definition name: (identifier) @name parameters: (parameters) @params) @sig',
        '(class_definition name: (identifier) @name) @sig',
    ],
    "javascript": [
        '(function_declaration name: (identifier) @name parameters: (formal_parameters) @params) @sig',
        '(class_declaration name: (identifier) @name) @sig',
        '(method_definition name: (property_identifier) @name) @sig',
        '(arrow_function) @sig',
        '(generator_function_declaration name: (identifier) @name) @sig',
    ],
    "typescript": [
        '(function_declaration name: (identifier) @name parameters: (formal_parameters) @params) @sig',
        '(class_declaration name: (type_identifier) @name) @sig',
        '(interface_declaration name: (type_identifier) @name) @sig',
        '(method_definition name: (property_identifier) @name) @sig',
        '(type_alias_declaration name: (type_identifier) @name) @sig',
        '(enum_declaration name: (identifier) @name) @sig',
        '(arrow_function) @sig',
    ],
    "go": [
        '(function_declaration name: (identifier) @name parameters: (parameter_list) @params) @sig',
        '(method_declaration receiver: (parameter_list) @receiver name: (field_identifier) @name) @sig',
        '(type_declaration (type_spec name: (type_identifier) @name)) @sig',
    ],
    "java": [
        '(method_declaration name: (identifier) @name parameters: (formal_parameters) @params) @sig',
        '(class_declaration name: (identifier) @name) @sig',
        '(interface_declaration name: (identifier) @name) @sig',
        '(enum_declaration name: (identifier) @name) @sig',
        '(record_declaration name: (identifier) @name) @sig',
    ],
    "rust": [
        '(function_item name: (identifier) @name parameters: (parameters) @params) @sig',
        '(struct_item name: (type_identifier) @name) @sig',
        '(enum_item name: (type_identifier) @name) @sig',
        '(trait_item name: (type_identifier) @name) @sig',
        '(type_item name: (type_identifier) @name) @sig',
        '(impl_item trait: (type_identifier) @name) @sig',
    ],
    "kotlin": [
        '(function_declaration name: (identifier) @name) @sig',
        '(class_declaration name: (identifier) @name) @sig',
    ],
}

_ts_language_cache: dict[str, object] = {}

def _get_ts_language(lang_id: str) -> object:
    if lang_id in _ts_language_cache:
        return _ts_language_cache[lang_id]
    pkg_name = f"tree_sitter_{lang_id}"
    try:
        mod = importlib.import_module(pkg_name)
        from tree_sitter import Language as TSLanguage
        if lang_id == "typescript":
            lang = TSLanguage(mod.language_typescript())
        else:
            lang = TSLanguage(mod.language())
        _ts_language_cache[lang_id] = lang
        return lang
    except Exception:
        _ts_language_cache[lang_id] = None
        return None

def _extract_signature_line(source_lines: list[str], start_row: int) -> str:
    first = source_lines[start_row].rstrip("\n").rstrip("\r")
    if not first.rstrip().endswith(",") and first.count("(") == first.count(")"):
        return first
    parts: list[str] = [first]
    for line in source_lines[start_row + 1:]:
        stripped = line.rstrip("\n").rstrip("\r")
        parts.append(stripped)
        if ":" in stripped and not stripped.rstrip().endswith(","):
            break
        if stripped.rstrip().endswith("{"):
            break
        if stripped.rstrip().endswith("):") or stripped.rstrip().endswith(") {"):
            break
    return "\n".join(parts)

def _extract_via_tree_sitter(file_path: Path) -> Optional[str]:
    ext = file_path.suffix.lower()
    lang_id = _EXTENSION_LANG_MAP.get(ext)
    if not lang_id:
        return None
    lang = _get_ts_language(lang_id)
    if lang is None:
        return None
    queries = _TS_QUERIES.get(lang_id)
    if not queries:
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return None
    source_bytes = content.encode("utf-8")
    from tree_sitter import Parser, Query, QueryCursor
    parser = Parser(lang)
    tree = parser.parse(source_bytes)
    source_lines = content.split("\n")
    seen: set[str] = set()
    signatures: list[str] = []
    for query_str in queries:
        try:
            q = Query(lang, query_str)
            qc = QueryCursor(q)
            matches = qc.matches(tree.root_node)
            for _pattern_index, captures in matches:
                sig_nodes = captures.get("sig", [])
                for node in sig_nodes:
                    start_row = node.start_point[0]
                    sig_line = _extract_signature_line(source_lines, start_row).strip()
                    if sig_line and sig_line not in seen:
                        seen.add(sig_line)
                        signatures.append(sig_line)
        except Exception:
            continue
    if not signatures:
        return None
    return f"### Signatures in {file_path}\n" + "\n".join(signatures)

# --- End tree-sitter ---

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
    content_text = None
    for enc in TEXT_ENCODINGS:
        try:
            with open(file_path, "r", encoding=enc) as f:
                content_text = f.read()
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    if content_text is None:
        lines.append(f"> Skipped: (Could not decode file with any supported encoding)\n")
        return "\n".join(lines)
    file_lines = content_text.split("\n")
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

def _ensure_context_reports_ignored() -> None:
    """Safeguard: Append context-reports/ to .gitignore if not present.

    Both report-producing tools (read_source_files and create_tree_report)
    call this so generated reports are never accidentally committed.
    """
    gitignore = Path(".gitignore")
    if gitignore.is_file():
        try:
            with open(gitignore, "r+", encoding="utf-8") as f:
                content = f.read()
                if "context-reports/" not in content:
                    f.write("\n# Custom Context MCP reports\ncontext-reports/\n")
        except Exception as e:
            print(f"Warning: Failed to update .gitignore: {e}", file=sys.stderr)

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
    _ensure_context_reports_ignored()

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

    # Generate timestamped filename with a UUID suffix.
    # F4 Fix: UUID suffix prevents same-second TOCTOU overwrite, mirroring create_tree_report logic.
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    unique = uuid.uuid4().hex[:8]
    report_file = report_dir / f"context_report_{timestamp}_{unique}.md"

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
def create_tree_report(target_path: str = ".") -> str:
    """Creates a .gitignore-aware directory tree of a path or the entire project and saves it as a Markdown file under context-reports/ (named tree_report_<timestamp>_<uuid>.md). Use when the Manager asks to 'create a tree of the project' or 'create a tree of <path>'. Security: target_path is resolved against the workspace root and rejected if it escapes the project (path traversal prevention)."""
    # Safeguard: Append context-reports/ to .gitignore if not present
    _ensure_context_reports_ignored()

    # Security: Coerce None or invalid types back to the whole-project default
    # so a malformed tool invocation degrades gracefully instead of crashing.
    if not isinstance(target_path, str):
        target_path = "."

    # Security: Resolve the target against the workspace root and reject any
    # path that escapes it. Path traversal prevention — the tool must never
    # walk directories outside the project the server is running in.
    workspace_root = Path.cwd().resolve()
    tree_path = Path(target_path).resolve()
    try:
        tree_path.relative_to(workspace_root)
    except ValueError:
        return "Error: Path traversal detected. target_path must be within the project workspace."

    ignore_filter = GitIgnoreFilter()
    if not tree_path.is_dir():
        return f"Error: {target_path} is not a valid directory."
    if ignore_filter.is_ignored(tree_path):
        return f"Warning: Target tree path is ignored by .gitignore: {target_path}"

    tree_text = generate_tree(tree_path, ignore_filter)

    # Ensure output directory exists
    report_dir = Path("context-reports")
    report_dir.mkdir(exist_ok=True)

    # Unique filename: timestamp + random UUID suffix. The UUID guarantees
    # collision-free naming without a TOCTOU-prone exists()/open() check loop.
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    unique = uuid.uuid4().hex[:8]
    report_file = report_dir / f"tree_report_{timestamp}_{unique}.md"

    content = (
        f"# Directory Tree Report\n\n"
        f"- **Target:** `{tree_path}`\n"
        f"- **Generated:** {timestamp}\n\n"
        f"{tree_text}\n"
    )

    try:
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        return f"Error writing tree report file: {e}"

    return (
        f"✅ Success: Directory tree saved for `{tree_path}`.\n"
        f"📁 Generated Report: `{report_file}`\n\n"
        f"Manager: You can now open `{report_file}` in your local editor to view the project tree or copy/paste it directly for the AI."
    )

@mcp.tool()
def extract_signatures(file_path: str) -> str:
    """Extracts structural signatures (classes, functions, methods) from source files using tree-sitter AST. Falls back to regex when no tree-sitter grammar is available for the language. Saves the result to a Markdown file under context-reports/ and returns the report file path."""
    # Master try/except: ensure extract_signatures never crashes the MCP server
    try:
        # Safeguard: Append context-reports/ to .gitignore if not present
        _ensure_context_reports_ignored()

        path = Path(file_path)
        if not path.is_file():
            return f"Error: File not found: {file_path}"

        result_content = None

        # Try tree-sitter AST extraction first (wrapped — fall back to regex on any failure)
        try:
            ts_result = _extract_via_tree_sitter(path)
            if ts_result:
                result_content = ts_result
        except Exception as ts_err:
            # Tree-sitter failed (missing grammar, parse error, etc.) — proceed to regex
            pass

        # Fallback to regex if tree-sitter did not produce results
        if result_content is None:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Match class, function, def, interface, type — with access modifiers
            pattern = re.compile(
                r'^(?:\s*(?:export|default|public|private|protected|internal|pub|static|abstract|final|override|inline|open|suspend)\s+)*'
                r'(?:class|struct|enum|trait|impl|interface|type|def|fun|func(?:tion)?)\s+\w+.*$',
                re.MULTILINE
            )
            matches = pattern.findall(content)

            # Match const/let arrow functions
            arrow_pattern = re.compile(r'^(?:export\s+)?(?:const|let)\s+\w+\s*=\s*(?:async\s*)?(?:\([^)]*\)|[^=]*)\s*=>.*$', re.MULTILINE)
            arrow_matches = arrow_pattern.findall(content)

            all_matches = matches + arrow_matches
            if not all_matches:
                return f"No structural signatures found in {file_path}."

            result_content = f"### Signatures in {file_path}\n" + "\n".join(all_matches)

        # Ensure output directory exists
        report_dir = Path("context-reports")
        report_dir.mkdir(exist_ok=True)

        # Generate timestamped filename with UUID suffix (mirrors read_source_files / create_tree_report)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        unique = uuid.uuid4().hex[:8]
        report_file = report_dir / f"signatures_report_{timestamp}_{unique}.md"

        # Write to file
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(result_content)

        return (
            f"✅ Success: Signatures extracted from `{file_path}`.\n"
            f"📁 Generated Report: `{report_file}`\n\n"
            f"Manager: You can now open `{report_file}` in your local editor to view the extracted signatures or copy/paste it directly for the AI."
        )
    except Exception as e:
        return f"Error extracting signatures from {file_path}: {str(e)}"

@mcp.tool()
def stage_and_inject_diff(task_file_path: str, modified_files: list[str] = []) -> str:
    """Stages ONLY the explicitly listed modified files plus the task file, then intelligently injects the staged diff into the task file's Git Diff block.

    F5 fix (Task 90): explicit path scoping replaces the old blind `git add -A .`,
    which swept parallel-session/foreign files into unrelated commits and required
    fragile sensitive-file reset heuristics. The OpenCode agent MUST pass every code
    file it modified via `modified_files`; if omitted or empty, only the task file is
    staged and the diff table will be empty (by design — the Brain cannot review work
    that was never explicitly listed).
    """
    try:
        # 1. F5 Fix: Explicit path scoping. Stage ONLY the files OpenCode modified + the task file.
        #    This prevents cross-session contamination and keeps the diff table clean for the Brain.
        files_to_stage = modified_files + [task_file_path]
        subprocess.run(["git", "add", "--"] + files_to_stage, check=True, capture_output=True)
        
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

@mcp.tool()
def qa_transition(task_file_path: str, modified_files: list[str] = []) -> str:
    """
    Atomically transitions a task from tasks/in-progress/ to tasks/qa/:
    1. Validates path and ensures task resides in tasks/in-progress/
    2. Moves task file to tasks/qa/ via git mv (fallback to shutil.move + git add)
    3. Rewrites the **File:** metadata header to tasks/qa/<filename>
    4. Stages modified_files + destination task file (explicit staging)
    5. Extracts staged diff excluding tasks/ (:!tasks/)
    6. Injects diff block between <!-- BEGIN_GIT_DIFF --> and <!-- END_GIT_DIFF -->
    7. Validates header consistency and returns confirmation
    """
    try:
        workspace_root = Path.cwd().resolve()
        src = Path(task_file_path)

        # Path traversal guard: must be within workspace
        try:
            src_resolved = src.resolve()
            src_resolved.relative_to(workspace_root)
        except ValueError:
            return f"❌ Error: task path escapes workspace: {task_file_path}"
        except Exception as e:
            return f"❌ Error resolving task path: {e}"

        # Validate source is inside tasks/in-progress/
        try:
            rel_check = src_resolved.relative_to(workspace_root).as_posix()
        except ValueError:
            rel_check = task_file_path
        # Also handle relative string input that hasn't been resolved via exists check
        if not rel_check.startswith("tasks/in-progress/"):
            # Try with original string if resolved path was absolute but file missing
            if not task_file_path.startswith("tasks/in-progress/"):
                return f"❌ Error: task path must be inside tasks/in-progress/, got: {task_file_path}"

        if not src_resolved.exists():
            return f"❌ Error: task file not found: {src_resolved}"

        task_name = src_resolved.name
        if not task_name.endswith(".md"):
            return f"❌ Error: task file must be a Markdown file (*.md), got: {task_name}"

        dest = workspace_root / "tasks" / "qa" / task_name
        expected_header = f"tasks/qa/{task_name}"
        dest.parent.mkdir(parents=True, exist_ok=True)

        # 2. Move task file to tasks/qa/ via git mv (fallback to shutil.move + git add)
        try:
            result = subprocess.run(["git", "mv", str(src_resolved), str(dest)], capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "git mv failed")
        except Exception as e:
            # Fallback for untracked files or git mv failure
            if not src_resolved.exists():
                # If src was moved via git mv partially, check dest
                if dest.exists():
                    pass
                else:
                    return f"❌ Error: Source task file not found after git mv failure: {src_resolved} ({e})"
            try:
                # If src still exists, move via filesystem
                if src_resolved.exists():
                    shutil.move(str(src_resolved), str(dest))
                # Stage the moved file
                subprocess.run(["git", "add", "--", str(dest)], check=True, capture_output=True)
            except Exception as move_err:
                return f"❌ Error: Fallback move failed: {src_resolved} → {dest}: {move_err}"

        # 3. Rewrites the **File:** metadata header to tasks/qa/<filename>
        try:
            content = dest.read_text(encoding="utf-8")
        except Exception as e:
            return f"❌ Error reading moved task file {dest}: {e}"
        header_pattern = re.compile(r"\*\*File:\*\*\s*`[^`]+`")
        if not header_pattern.search(content):
            return f"❌ Error: Could not find **File:** header in {dest}"
        new_content_header = header_pattern.sub(f"**File:** `{expected_header}`", content, count=1)
        try:
            dest.write_text(new_content_header, encoding="utf-8")
        except Exception as e:
            return f"❌ Error writing header update to {dest}: {e}"

        # 4. Stages modified_files + destination task file (explicit staging)
        files_to_stage = list(modified_files) + [str(dest)]
        try:
            subprocess.run(["git", "add", "--"] + files_to_stage, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            return f"❌ Error staging files {files_to_stage}: {e.stderr.decode() if hasattr(e.stderr, 'decode') else e.stderr}"

        # 5. Extracts staged diff excluding tasks/ (:!tasks/)
        try:
            diff_proc = subprocess.run(["git", "diff", "--staged", "--", ".", ":!tasks/"], capture_output=True, text=True)
            diff_text = diff_proc.stdout.strip()
        except Exception as e:
            return f"❌ Error extracting staged diff: {e}"
        if not diff_text:
            diff_text = "No code changes detected or staged."
        diff_block = f"\n```diff\n{diff_text}\n```\n"

        # 6. Injects diff block between <!-- BEGIN_GIT_DIFF --> and <!-- END_GIT_DIFF -->
        try:
            content_after_header = dest.read_text(encoding="utf-8")
        except Exception as e:
            return f"❌ Error re-reading task file for diff injection: {e}"
        diff_pattern = re.compile(r"<!-- BEGIN_GIT_DIFF -->.*<!-- END_GIT_DIFF -->", re.DOTALL)
        if not diff_pattern.search(content_after_header):
            return f"❌ Error: Could not find <!-- BEGIN_GIT_DIFF --> markers in {dest}"
        new_content_final = diff_pattern.sub(lambda m: f"<!-- BEGIN_GIT_DIFF -->{diff_block}<!-- END_GIT_DIFF -->", content_after_header)
        try:
            dest.write_text(new_content_final, encoding="utf-8")
        except Exception as e:
            return f"❌ Error writing diff injection to {dest}: {e}"
        # Re-stage the task file after injection so final QA state is staged (header + diff)
        try:
            subprocess.run(["git", "add", "--", str(dest)], check=True, capture_output=True)
        except Exception as e:
            return f"❌ Error re-staging QA task file after injection: {e}"

        # 7. Validates header consistency and returns confirmation
        try:
            final_content = dest.read_text(encoding="utf-8")
            m = re.search(r"\*\*File:\*\*\s*`([^`]+)`", final_content)
            if not m:
                return f"❌ Error: **File:** header missing after injection in {dest}"
            actual = m.group(1).strip()
            if actual != expected_header:
                # Resolve comparison like linter
                try:
                    if Path(actual).resolve() != Path(expected_header).resolve():
                        return f"❌ Error: File header mismatch: header says '{actual}' but expected '{expected_header}'"
                except Exception:
                    return f"❌ Error: File header mismatch: header says '{actual}' but expected '{expected_header}'"
        except Exception as e:
            return f"❌ Error validating header: {e}"

        files_str = ", ".join(modified_files) if modified_files else "(no code files — diff will be sentinel)"
        return (
            f"✅ QA transition complete: {task_file_path} → {expected_header}\n"
            f"   Staged files: {files_str}\n"
            f"   Header synced and diff injected into {expected_header}"
        )

    except Exception as e:
        return f"❌ Unexpected error in qa_transition: {str(e)}"

def _derive_task_slug(task_file_path: str) -> str:
    """Derives a 'task <NN> - <slug>' label from a task file name (e.g. '78-fix-bug.md' -> 'task 78 - fix bug')."""
    name = Path(task_file_path).stem
    parts = re.split(r"[-_]", name, maxsplit=1)
    if len(parts) == 2 and parts[0].isdigit():
        return f"task {parts[0]} - {parts[1].replace('-', ' ')}"
    return f"task - {name.replace('-', ' ')}"

@mcp.tool()
def commit_and_clean_task(task_file_path: str, commit_message: str) -> str:
    """Commits staged changes, captures the feature commit hash, replaces the raw diff in the task file with the hash reference, and commits the cleaned task file as a separate closure commit. The stored hash always points to the feature commit, which stays reachable forever (no amend, no orphaned commits)."""
    try:
        # 0. Idempotency guard: skip if the task file was already cleaned.
        #    Placed first so a cleaned task file short-circuits even on a clean tree.
        #    Must match the EXACT cleaned-block structure, not a bare substring:
        #    a raw injected diff can itself mention 'Stored in Commit Hash' (e.g.
        #    the diff of this very guard or its CHANGELOG entry), causing a false
        #    positive that blocks legitimate closures.
        path = Path(task_file_path)
        if path.is_file():
            with open(path, 'r', encoding='utf-8') as f:
                existing = f.read()
            cleaned_block = re.compile(
                r'<!-- BEGIN_GIT_DIFF -->\s*\*\*Factual Git Diff:\*\* Stored in Commit Hash: `[0-9a-f]{7,40}`\s*<!-- END_GIT_DIFF -->',
                re.DOTALL
            )
            if cleaned_block.search(existing):
                return "⚠️ Task file already cleaned (Stored in Commit Hash present). Nothing to commit."

        # 0.5 Safety check before commit
        staged_check = subprocess.run(["git", "diff", "--staged", "--quiet"], capture_output=True)
        if staged_check.returncode == 0:
            return "⚠️ No staged changes to commit."

        # 1. Commit staged changes (feature commit H1)
        subprocess.run(["git", "commit", "-m", commit_message], check=True, capture_output=True, text=True)

        # 2. Capture H1 — the feature commit hash. It stays reachable forever
        #    as the parent of the closure commit (step 5). NEVER amend it.
        hash_proc = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True)
        commit_hash = hash_proc.stdout.strip()

        # 3. Read task file and replace raw diff with the hash reference
        if path.is_file():
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            pattern = re.compile(r'<!-- BEGIN_GIT_DIFF -->.*<!-- END_GIT_DIFF -->', re.DOTALL)
            if pattern.search(content):
                clean_block = f"<!-- BEGIN_GIT_DIFF -->\n**Factual Git Diff:** Stored in Commit Hash: `{commit_hash}`\n<!-- END_GIT_DIFF -->"
                new_content = pattern.sub(clean_block, content)

                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

        # 4. Stage the cleaned task file ONLY (F5 fix: never `git add -A tasks/`,
        #    which swept foreign/parallel-session task files into this commit).
        subprocess.run(["git", "add", "--", task_file_path], check=True, capture_output=True)

        # 5. Commit the cleaned task file as a separate closure commit.
        #    A plain commit (NOT --amend) keeps H1 reachable from HEAD.
        slug = _derive_task_slug(task_file_path)
        staged_after = subprocess.run(["git", "diff", "--staged", "--quiet"], capture_output=True)
        if staged_after.returncode != 0:
            subprocess.run(["git", "commit", "-m", f"chore: close {slug}"], check=True, capture_output=True, text=True)

        return f"✅ Success: Code committed (Hash: `{commit_hash}`). Task file {task_file_path} cleaned; closure commit `chore: close {slug}` created on top."
    except subprocess.CalledProcessError as e:
        return f"❌ Git Error: {e.stderr}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


@mcp.tool()
def bundle_tasks(task_ids: list[str], title: str, dry_run: bool = False, force: bool = False) -> str:
    """
    Bundle multiple small related tasks into a single META task with auto-archive (Task 110).

    Self-contained MCP implementation — does NOT require `scripts/bundle-tasks.py` to exist.
    Mirrors the CLI script logic so projects that only have the MCP server (no shell access to the
    script, e.g., other projects vendoring this HQ's MCP servers) can bundle via the Hands' MCP
    interface. When the script IS present, behavior is identical; when it is absent, this tool still
    works. The script `scripts/bundle-tasks.py` remains the CLI entry point for Managers who prefer
    `uv run scripts/bundle-tasks.py ...`; the two implementations are kept in sync (helpers are
    duplicated verbatim from the script).

    Workflow:
      1. Validates each task ID exists in tasks/backlog|in-progress|qa|completed (active only, archive excluded)
      2. Discovers NEXT_ID via max(tasks/**/*.md)+1 across ALL dirs (including archive, no collision)
      3. Slugifies title to kebab-case, writes tasks/backlog/<NEXT_ID>-<slug>.md with canonical template + **Supersedes:** [ids] + **Meta:** true + per-source verbatim appendices
      4. Unless dry_run, moves each source via `git mv <src> tasks/archive/<src>` (fallback to mv+git add) and patches header (**File:**→archive, **Status:** superseded, **Superseded-By:**, **Superseded-At:**, footer before Execution Log) — history stays via `git log --follow`
      5. Guardrails: rejects >6 without force, warns if combined LOC >400, rejects missing IDs

    Args:
        task_ids: List of task IDs to bundle (e.g., ["12","15","20"]). Must be numeric strings.
        title: Title for the META task (slugified for filename, kept verbatim for Task title).
        dry_run: If True, preview only — no files created, no archive moves. Prints what would happen.
        force: If True, allow bundling >6 tasks (bypasses cap).

    Returns:
        Success message with created META path and archive destinations, or error string.

    Security: task_ids are validated as numeric; title is slugified (no path traversal); no absolute paths.
    """
    # --- Constants (mirrors scripts/bundle-tasks.py) ---
    ACTIVE_KANBAN_DIRS = ["backlog", "in-progress", "qa", "completed"]
    MAX_BUNDLE_SIZE = 6
    DIFF_SIZE_WARNING_THRESHOLD = 400

    # --- Helpers (verbatim copies from scripts/bundle-tasks.py for self-containment) ---
    def _kebab_case(text: str) -> str:
        """Convert arbitrary title to kebab-case slug (B4: supports Unicode/Persian)."""
        import unicodedata
        normalized = unicodedata.normalize("NFKD", text)
        slug = normalized.lower().strip()
        slug = re.sub(r"[^a-z0-9\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]+", "-", slug)
        slug = re.sub(r"-{2,}", "-", slug)
        slug = slug.strip("-")
        return slug or "bundle"

    def _discover_next_id(tasks_root: Path = Path("tasks")) -> int:
        max_id = 0
        if not tasks_root.is_dir():
            return 1
        for md in tasks_root.rglob("*.md"):
            m = re.match(r"^(\d+)-", md.name)
            if m:
                try:
                    nid = int(m.group(1))
                    if nid > max_id:
                        max_id = nid
                except ValueError:
                    continue
        return max_id + 1 if max_id else 1

    def _find_task_file(task_id: str, tasks_root: Path = Path("tasks")) -> Path | None:
        norm = task_id.lstrip("0") or "0"
        candidates: list[Path] = []
        for d in ACTIVE_KANBAN_DIRS:
            dir_path = tasks_root / d
            if not dir_path.is_dir():
                continue
            for md in dir_path.glob("*.md"):
                m = re.match(r"^(\d+)-", md.name)
                if m and m.group(1).lstrip("0") == norm:
                    candidates.append(md)
        if len(candidates) == 1:
            return candidates[0]
        if len(candidates) > 1:
            return None  # B2: hard halt — duplicate active IDs
        # Check archive for better error (already archived)
        for md in (tasks_root / "archive").glob("*.md") if (tasks_root / "archive").is_dir() else []:
            m = re.match(r"^(\d+)-", md.name)
            if m and m.group(1).lstrip("0") == norm:
                return None
        return None

    def _extract_section(content: str, heading: str) -> str | None:
        pattern = re.compile(rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\n---\s*\n|\Z)", re.MULTILINE | re.DOTALL)
        m = pattern.search(content)
        return m.group(1).strip() if m else None

    def _extract_title(content: str) -> str:
        m = re.search(r"^# Task \d+:\s*(.+)$", content, re.MULTILINE)
        return m.group(1).strip() if m else "Untitled"

    def _format_task_id_list(ids: list[str]) -> str:
        return "[" + ", ".join(ids) + "]"

    def _extract_checklist_with_continuations(section_text: str) -> list[str]:
        """B1: Extract checklist items with all indented continuation lines."""
        lines = section_text.splitlines()
        result: list[str] = []
        in_checklist = False
        for line in lines:
            stripped = line.strip()
            is_root_bullet = line.startswith("- [")
            if is_root_bullet:
                in_checklist = True
                result.append(stripped)
            elif in_checklist:
                if stripped and not line.startswith("- [") and not stripped.startswith("## ") and not stripped.startswith("---"):
                    result.append(line)
                else:
                    in_checklist = False
                    if line.startswith("- ["):
                        in_checklist = True
                        result.append(stripped)
        return result

    def _detect_stack(content: str) -> str | None:
        """M1: Detect tech stack from task content."""
        lower = content.lower()
        if any(kw in lower for kw in ["jetpack compose", "kotlin", "android", "hilt", "sqldelight"]):
            return "android"
        if any(kw in lower for kw in ["react", "vite", "jsx", "tsx", "next.js", "nextjs"]):
            return "react"
        if any(kw in lower for kw in ["fastapi", "pydantic", "uvicorn"]):
            return "fastapi"
        if any(kw in lower for kw in ["spring boot", "spring-boot", "java", "mapstruct"]):
            return "spring"
        if any(kw in lower for kw in ["swiftui", "ios", "swift", "uikit"]):
            return "ios"
        if any(kw in lower for kw in ["golang", "gin", "go-gin", "hexagonal"]):
            return "go"
        return None

    def _verify_verbatim_checksums(source_data: list[tuple[str, Path, str, str]], meta_content: str) -> bool:
        """M2: Verify 100% of extracted source AC text is in the Bundled Checklist."""
        bundled_match = re.search(
            r"^## Bundled Checklist.*?\n\n(.*?)(?=^## |\Z)",
            meta_content,
            re.MULTILINE | re.DOTALL,
        )
        if not bundled_match:
            return False
        bundled_text = bundled_match.group(1)
        for sid, path, content, _title in source_data:
            ac = _extract_section(content, "Acceptance Criteria")
            if not ac:
                continue
            for line in ac.splitlines():
                stripped = line.strip()
                if stripped and stripped.startswith("- ["):
                    m = re.match(r"^- \[[ xX]\]\s*(.*)", stripped)
                    core = m.group(1) if m else stripped
                    prefixed = f"[{sid}] {core}"
                    if len(core) > 10 and prefixed not in bundled_text:
                        return False
        return True

    def _git_mv_or_fallback(src: Path, dst: Path) -> bool:
        dst.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(["git", "mv", str(src), str(dst)], capture_output=True, text=True)
        if result.returncode == 0:
            return True
        if "not under version control" in result.stderr or "not tracked" in result.stderr.lower():
            try:
                src.rename(dst)
                subprocess.run(["git", "add", "--", str(dst)], check=True, capture_output=True)
                return True
            except Exception:
                return False
        return False

    def _patch_archived_file(archive_path: Path, meta_id: str, meta_slug: str) -> None:
        try:
            content = archive_path.read_text(encoding="utf-8")
        except Exception:
            return
        new_file_header = f"**File:** `tasks/archive/{archive_path.name}`"
        content = re.sub(r"\*\*File:\*\*\s*`[^`]+`", new_file_header, content, count=1)
        if re.search(r"\*\*Status:\*\*\s*\w+", content):
            content = re.sub(r"\*\*Status:\*\*\s*\w+", "**Status:** superseded", content, count=1)
        else:
            content = re.sub(r"(\*\*Type:\*\*\s*\w+)", r"\1\n**Status:** superseded", content, count=1)
        if "**Superseded-By:**" not in content:
            content = re.sub(r"(\*\*Status:\*\*\s*superseded)", rf"\1\n**Superseded-By:** `{meta_id}-{meta_slug}`", content, count=1)
            timestamp = time.strftime("%Y-%m-%d")
            content = re.sub(r"(\*\*Superseded-By:\*\*\s*`[^`]+`)", rf"\1\n**Superseded-At:** `{timestamp}`", content, count=1)
        superseded_note = (
            f"> **Superseded:** This task was bundled into META task `{meta_id}-{meta_slug}` "
            f"and archived on {time.strftime('%Y-%m-%d')}. "
            f"See `tasks/backlog/{meta_id}-{meta_slug}.md` (or its Kanban successor) for the unified execution. "
            f"History preserved via `git log --follow -- tasks/archive/{archive_path.name}`.\n"
        )
        if superseded_note.strip() not in content:
            if "## Execution Log" in content:
                content = content.replace("## Execution Log", superseded_note + "\n## Execution Log", 1)
            elif "## Factual Git Diff" in content:
                content = content.replace("## Factual Git Diff", superseded_note + "\n## Factual Git Diff", 1)
        try:
            archive_path.write_text(content, encoding="utf-8")
        except Exception:
            pass

    def _build_meta_content(meta_id: int, meta_slug: str, meta_title: str, source_ids: list[str], source_data: list[tuple[str, Path, str, str]]) -> str:
        meta_id_str = f"{meta_id:02d}" if meta_id < 100 else str(meta_id)
        if meta_id >= 100:
            meta_id_str = str(meta_id)
        file_header = f"tasks/backlog/{meta_id_str}-{meta_slug}.md"
        title_line = f"# Task {meta_id}: {meta_title}"
        timestamp = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
        bundled_checklist_items: list[str] = []
        local_todos_aggregated: list[str] = []
        total_loc = 0
        per_source_blocks: list[str] = []
        for sid, path, content, stitle in source_data:
            goal = _extract_section(content, "Goal") or "_(No Goal section found)_"
            ac = _extract_section(content, "Acceptance Criteria") or "_(No Acceptance Criteria)_"
            todos = _extract_section(content, "Local TODOs") or "_(No Local TODOs)_"
            risk = _extract_section(content, "Risk & Rollback")
            manager_notes = _extract_section(content, "Manager's Notes")
            source_context = ""
            if "## Blueprint Reference" in content:
                br = _extract_section(content, "Blueprint Reference")
                if br:
                    source_context += f"\n**Blueprint Reference (verbatim):**\n{br}\n"
            total_loc += len(content.splitlines())
            # B1: multi-line checklist extraction
            ac_lines = _extract_checklist_with_continuations(ac)
            if not ac_lines:
                ac_lines = [f"- [ ] {line.strip()}" for line in ac.splitlines() if line.strip() and not line.strip().startswith("#")][:3]
            for line in ac_lines:
                if line.startswith("- ["):
                    m = re.match(r"^- \[[ xX]\]\s*(.*)", line)
                    inner = m.group(1) if m else line
                    bundled_checklist_items.append(f"- [ ] [{sid}] {inner}")
                else:
                    bundled_checklist_items.append(line)
            # B1: multi-line TODO extraction
            todo_lines = _extract_checklist_with_continuations(todos)
            for line in todo_lines:
                if line.startswith("- ["):
                    m = re.match(r"^- \[[ xX]\]\s*(.*)", line)
                    inner = m.group(1) if m else line
                    local_todos_aggregated.append(f"- [ ] [{sid}] {inner}")
                else:
                    local_todos_aggregated.append(line)
            block = f"### Source Task {sid}: {stitle}\n\n"
            block += f"**Original File:** `{path}` → `tasks/archive/{path.name}` (after bundling)\n\n"
            block += f"**Title:** {stitle}\n\n"
            block += "#### Goal (verbatim)\n\n"
            block += f"{goal}\n\n"
            if manager_notes:
                block += "#### Manager's Notes (verbatim)\n\n"
                block += f"{manager_notes}\n\n"
            if source_context:
                block += source_context + "\n"
            block += "#### Acceptance Criteria (verbatim)\n\n"
            block += f"{ac}\n\n"
            block += "#### Local TODOs (verbatim)\n\n"
            block += f"{todos}\n\n"
            if risk:
                block += "#### Risk & Rollback (verbatim)\n\n"
                block += f"{risk}\n\n"
            block += "---\n\n"
            per_source_blocks.append(block)
        seen_todos: set[str] = set()
        deduped_todos: list[str] = []
        for t in local_todos_aggregated:
            if t not in seen_todos:
                seen_todos.add(t)
                deduped_todos.append(t)
        meta_local_todos = (
            f"- [ ] Step 1: Validate META bundle — confirm all {len(source_data)} source requirements are captured verbatim below\n"
            f"- [ ] Step 2: Implement unified changes covering all bundled tasks (single diff, single branch)\n"
        )
        for t in deduped_todos:
            meta_local_todos += f"{t}\n"
        meta_local_todos += f"- [ ] Step {len(deduped_todos)+3}: Verify all bundled checklist items and run lint_task_file + verification-before-completion\n"
        meta_local_todos += f"- [ ] Step {len(deduped_todos)+4}: Update CHANGELOG.md and record Verification Evidence\n"
        meta_ac = "\n".join(bundled_checklist_items) if bundled_checklist_items else "- [ ] _(No aggregated criteria — check per-source blocks)_"
        meta_ac += f"\n- [ ] Traceability: All {len(source_data)} source tasks are archived with superseded-by marker and reachable via `git log --follow`"
        meta_verification = (
            f"- **Test command:** `lint_task_file` on META file; `git log --oneline --follow -- tasks/archive/<id>-*.md | head` for archived sources; project test suite if logic changed\n"
            f"- **Expected result:** META lint passes; all {len(source_data)} sources in `tasks/archive/` with `superseded` status; single Factual Git Diff covers all bundled changes\n"
            f"- **Actual result:** _(Hands fill during execution)_\n"
            f"- **Exit code:** _(Hands fill)_\n"
        )
        meta_risk = (
            "- **Risk:** Checklist omission — mitigated by verbatim copy + SHA-length comparison of source AC vs bundled checklist; script fails if mismatch >0.\n"
            "- **Risk:** Mega-diff >400 LOC unreviewable — warning emitted; Manager should split if >400.\n"
            "- **Risk:** Accidental purge — mitigation: only `git mv` to archive, never `git rm`; purge blocked until META reaches `tasks/completed/`.\n"
            f"- **Rollback plan:** `git mv tasks/archive/<id>-*.md tasks/backlog/<id>-*.md` for each superseded {_format_task_id_list(source_ids)}, remove Superseded-By footer, delete or archive `tasks/backlog/{meta_id_str}-{meta_slug}.md` as abandoned. No HQ code beyond bundler is affected.\n"
        )
        warning_note = ""
        if total_loc > DIFF_SIZE_WARNING_THRESHOLD:
            warning_note = (
                f"> ⚠️ **Guardrail Warning:** Combined source size is {total_loc} LOC (> {DIFF_SIZE_WARNING_THRESHOLD}). "
                f"Unified META diff may be large and hard to review. Consider splitting into two METAs.\n\n"
            )
        content = (
            f"{title_line}\n\n"
            f"**File:** `{file_header}`\n"
            f"**Source:** manager\n"
            f"**Type:** feature\n"
            f"**Status:** open\n"
            f"**Supersedes:** {_format_task_id_list(source_ids)}\n"
            f"**Meta:** true\n"
            f"**Created:** {timestamp}\n"
            f"**Bundled:** {len(source_data)} tasks\n\n"
            f"## Goal\n\n"
            f"Unified execution of {len(source_data)} related small tasks as a single META task to eliminate sequential overhead. This META bundles tasks {_format_task_id_list(source_ids)} — \"{meta_title}\" — into one branch, one diff, and one QA gate (all-or-nothing). Every requirement below is preserved **verbatim** from its source task; no summarization or omission is allowed.\n\n"
            f"{warning_note}**Source IDs:** {_format_task_id_list(source_ids)}\n"
            f"**Next ID:** {meta_id} (discovered via `find tasks -name \"*.md\" | sort -n | tail -1 +1`)\n"
            f"**Archive Policy:** Source files will be moved to `tasks/archive/` with `superseded-by: {meta_id}-{meta_slug}` and remain reachable via `git log --follow` (never purged until META is completed).\n\n"
            f"## Manager's Notes\n\n"
            f"**Bundle Decision (2026-08-21):** Manager requested fully automatic bundling with archive (not purge). This META was generated deterministically by `scripts/bundle-tasks.py` (and `bundle_tasks` MCP tool) to execute {len(source_data)} small related tasks together and speed up turnaround.\n\n"
            f"**Traceability:**\n"
            f"- Supersedes {_format_task_id_list(source_ids)} — see per-source verbatim blocks below\n"
            f"- Archive: each source moved via `git mv` to `tasks/archive/` with `**Superseded-By:** {meta_id_str}-{meta_slug}` header + superseded footer\n"
            f"- Rollback: `git mv tasks/archive/<id>-*.md tasks/backlog/` + delete META file\n\n"
            f"**Guardrails Applied:**\n"
            f"- Cap 6 per bundle — this bundle has {len(source_data)} ({'✅ within cap' if len(source_data) <= MAX_BUNDLE_SIZE else '❌ exceeds cap — requires --force'})\n"
            f"- Verbatim preservation — every source Goal/AC/TODO/Risk copied verbatim below (SHA comparison available in bundler dry-run)\n"
            f"- Diff-size check — combined {total_loc} LOC ({'⚠️ exceeds 400 — consider split' if total_loc > DIFF_SIZE_WARNING_THRESHOLD else '✅ within 400'})\n\n"
            f"## Source Bundles (Verbatim Preservation)\n\n"
            f"The following blocks are **verbatim copies** of each source task's critical sections. They are the source of truth; the checklist that follows is derived from them. Do not edit them manually — they were extracted by the bundler to guarantee zero omission.\n\n"
            f"{''.join(per_source_blocks)}\n"
            f"## Bundled Checklist (All-or-Nothing)\n\n"
            f"> **QA Gate (all-or-nothing):** Every line below maps to one source acceptance criterion. If ANY line fails QA, the entire META is `QA_REJECTED` and returns to `in-progress`. Do not partially close.\n\n"
            f"{meta_ac}\n\n"
            f"## Local TODOs\n\n"
            f"{meta_local_todos.strip()}\n\n"
            f"## Acceptance Criteria\n\n"
            f"{meta_ac}\n\n"
            f"## Verification Evidence\n\n"
            f"{meta_verification.strip()}\n\n"
            f"## Definition of Done\n\n"
            f"The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):\n\n"
            f"- [ ] Build/Test/Lint pass with exit code 0\n"
            f"- [ ] `lint_task_file` passes on the active task file\n"
            f"- [ ] `CHANGELOG.md` updated via Parse-Then-Append\n"
            f"- [ ] `verification-before-completion` applied and evidence recorded\n\n"
            f"## Risk & Rollback\n\n"
            f"{meta_risk.strip()}\n\n"
            f"---\n\n"
            f"## Execution Log & Reasoning\n\n"
            f"_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_\n\n"
            f"## Factual Git Diff\n\n"
            f"<!-- BEGIN_GIT_DIFF -->\n\n"
            f"_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_\n\n"
            f"<!-- END_GIT_DIFF -->\n"
        )
        return content

    try:
        # --- Validation (mirrors script) ---
        if not task_ids:
            return "❌ Error: task_ids is empty. Provide 2-6 numeric task IDs."
        cleaned_ids: list[str] = []
        for raw in task_ids:
            s = str(raw).strip()
            if not re.match(r"^\d+$", s):
                return f"❌ Invalid task ID '{raw}': must be numeric (e.g., 12, 015)."
            cleaned_ids.append(s)
        seen: set[str] = set()
        deduped: list[str] = []
        for tid in cleaned_ids:
            norm = tid.lstrip("0") or "0"
            if norm not in seen:
                seen.add(norm)
                deduped.append(tid)
        task_ids = deduped
        if not title or not title.strip():
            return "❌ Error: title is required (e.g., 'android-polish-bundle')."
        title = title.strip()
        if len(task_ids) > MAX_BUNDLE_SIZE and not force:
            return f"❌ Guardrail: Bundle size {len(task_ids)} exceeds MAX_BUNDLE_SIZE={MAX_BUNDLE_SIZE}. Use --force to override, or split into two METAs. IDs: {task_ids}"
        if len(task_ids) > MAX_BUNDLE_SIZE and force:
            # Warn but continue — caller will see warning in final output
            pass

        # --- Resolve sources (active Kanban only) ---
        tasks_root = Path("tasks")
        source_data: list[tuple[str, Path, str, str]] = []
        missing: list[str] = []
        for tid in task_ids:
            p = _find_task_file(tid, tasks_root)
            if p is None:
                missing.append(tid)
            else:
                try:
                    c = p.read_text(encoding="utf-8")
                except Exception as e:
                    return f"❌ Could not read {p} for task {tid}: {e}"
                t = _extract_title(c)
                source_data.append((tid, p, c, t))
        if missing:
            return f"❌ Missing tasks (not found in active Kanban dirs): {missing}\n   Searched: {', '.join(ACTIVE_KANBAN_DIRS)} (archive excluded).\n   Hint: Check `ls tasks/backlog/ tasks/in-progress/ tasks/qa/ tasks/completed/ | grep {missing[0]}`"
        if not source_data:
            return "❌ No source tasks resolved. Abort."

        # --- Discover NEXT_ID across ALL dirs including archive ---
        next_id = _discover_next_id(tasks_root)
        meta_id_str = f"{next_id:02d}" if next_id < 100 else str(next_id)
        if next_id >= 100:
            meta_id_str = str(next_id)
        meta_slug = _kebab_case(title)
        meta_filename = f"{meta_id_str}-{meta_slug}.md"
        output_path = tasks_root / "backlog" / meta_filename
        if output_path.exists():
            return f"❌ Task ID collision: {output_path} already exists. Re-run ID discovery."
        # Also check backlog glob for same ID prefix
        if list((tasks_root / "backlog").glob(f"{next_id}-*.md")) if (tasks_root / "backlog").is_dir() else []:
            # This would also match our not-yet-created file if we had a race, but we already checked exists
            pass

        meta_title_full = title
        meta_content = _build_meta_content(next_id, meta_slug, meta_title_full, task_ids, source_data)
        total_loc = sum(len(c.splitlines()) for _, _, c, _ in source_data)

        # M1: Stack detection
        source_stacks: list[str] = []
        for _, _, c, _ in source_data:
            stack = _detect_stack(c)
            if stack:
                source_stacks.append(stack)
        unique_stacks = set(source_stacks)
        if len(unique_stacks) > 1 and not force:
            return f"❌ Stack conflict: Tasks have different stacks {unique_stacks}. Use --force to bundle across stacks, or separate by stack."
        elif len(unique_stacks) > 1 and force:
            pass  # Warning will be in output

        # M2: Verbatim checksum validation
        if not _verify_verbatim_checksums(source_data, meta_content):
            return "❌ Verbatim checksum validation failed. Some AC text was not preserved in META."

        if dry_run:
            lines = []
            lines.append(f"🔍 Dry-run (MCP): Would create META task {next_id}-{meta_slug}")
            lines.append(f"   Output: {output_path}")
            lines.append(f"   Bundles: {task_ids} ({len(task_ids)} tasks)")
            lines.append(f"   Sources:")
            for sid, p, _, t in source_data:
                lines.append(f"     - {sid}: {t} ({p})")
            lines.append(f"   Combined LOC: {total_loc} {'⚠️ >400' if total_loc > 400 else '✅'}")
            lines.append(f"   Supersedes will be: {task_ids}")
            lines.append(f"   Archive destinations:")
            for sid, p, _, _ in source_data:
                lines.append(f"     - {p} -> tasks/archive/{p.name}")
            lines.append(f"\n   META content preview (first 40 lines):")
            for i, line in enumerate(meta_content.splitlines()[:40], 1):
                lines.append(f"   {i:3d}| {line}")
            lines.append(f"\n   ... {len(meta_content.splitlines()) - 40} more lines")
            required = ["## Goal", "## Local TODOs", "## Acceptance Criteria", "## Verification Evidence", "## Risk & Rollback", "## Factual Git Diff", "## Execution Log"]
            missing_sections = [s for s in required if s not in meta_content]
            if missing_sections:
                lines.append(f"⚠️ Missing required sections in preview: {missing_sections}")
                return "\n".join(lines)
            lines.append(f"\n✅ Dry-run lint check: All required sections present.")
            if len(task_ids) > 6 and force:
                lines.insert(0, f"⚠️ --force: Bundling {len(task_ids)} tasks (> 6). Mega-diff risk.")
            return "\n".join(lines)

        # --- B5: Atomic creation with retry loop ---
        import subprocess as _sp
        MAX_ID_RETRIES = 5
        for attempt in range(MAX_ID_RETRIES):
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "x", encoding="utf-8") as f:
                    pass  # Atomic creation
                break
            except FileExistsError:
                # Re-discover next ID
                next_id = _discover_next_id(tasks_root)
                meta_id_str = f"{next_id:02d}" if next_id < 100 else str(next_id)
                if next_id >= 100:
                    meta_id_str = str(next_id)
                meta_slug = _kebab_case(title)
                meta_filename = f"{meta_id_str}-{meta_slug}.md"
                output_path = tasks_root / "backlog" / meta_filename
                continue
        else:
            return f"❌ Failed to find unique ID after {MAX_ID_RETRIES} attempts. Another process may be bundling concurrently."

        # --- Write META content ---
        try:
            output_path.write_text(meta_content, encoding="utf-8")
        except Exception as e:
            output_path.unlink(missing_ok=True)
            return f"❌ Failed to write META file {output_path}: {e}"

        out_lines = [f"✅ Created META task (MCP): {output_path} (bundles {task_ids})"]

        # --- B3: Archive sources with transactional rollback ---
        archived: list[Path] = []
        failed: list[str] = []
        for sid, src_path, _, _ in source_data:
            dst = tasks_root / "archive" / src_path.name
            ok = _git_mv_or_fallback(src_path, dst)
            if ok:
                archived.append(dst)
                _patch_archived_file(dst, meta_id_str, meta_slug)
                out_lines.append(f"   📦 Archived {sid}: {src_path} -> {dst}")
            else:
                failed.append(sid)
                out_lines.append(f"   ❌ Failed to archive {sid}: {src_path}")

        if failed:
            # B3: Transactional rollback
            for archived_path in archived:
                original_name = archived_path.name
                for _, src_path, _, _ in source_data:
                    if src_path.name == original_name:
                        restore_dst = src_path
                        break
                else:
                    restore_dst = tasks_root / "backlog" / original_name
                try:
                    restore_dst.parent.mkdir(parents=True, exist_ok=True)
                    _sp.run(["git", "mv", str(archived_path), str(restore_dst)], check=True, capture_output=True)
                    # Remove superseded headers
                    content = restore_dst.read_text(encoding="utf-8")
                    content = re.sub(r"\n\*\*Superseded-By:\*\*.*$", "", content, flags=re.MULTILINE)
                    content = re.sub(r"\n\*\*Superseded-At:\*\*.*$", "", content, flags=re.MULTILINE)
                    superseded_pattern = re.compile(r"> \*\*Superseded:\*\*.*?History preserved.*?\n\n", re.DOTALL)
                    content = superseded_pattern.sub("", content)
                    content = re.sub(r"\*\*Status:\*\*\s*superseded", "**Status:** open", content)
                    content = re.sub(r"\*\*File:\*\*\s*`[^`]+`", f"**File:** `tasks/backlog/{restore_dst.name}`", content, count=1)
                    restore_dst.write_text(content, encoding="utf-8")
                except Exception:
                    pass
            output_path.unlink(missing_ok=True)
            return f"❌ Bundle aborted. Archive failed for {failed}. All changes rolled back. Fix and retry."
        else:
            out_lines.append(f"✅ Archived {len(archived)} source tasks to tasks/archive/ with superseded-by: {meta_id_str}-{meta_slug}")
        # Light validation
        try:
            cc = output_path.read_text(encoding="utf-8")
            for req in ["## Goal", "## Local TODOs", "## Acceptance Criteria"]:
                if req not in cc:
                    out_lines.append(f"⚠️ Lint warning: {req} missing in created META.")
        except Exception:
            pass
        out_lines.append(f"\nDone. Next: move {output_path} through Kanban (backlog → in-progress → qa → completed) as a single Hands implementation.")
        out_lines.append(f"Traceability: git log --oneline --follow -- tasks/archive/<id>-*.md | head")
        if len(task_ids) > 6 and force:
            out_lines.insert(0, f"⚠️ --force: Bundling {len(task_ids)} tasks (> 6). Mega-diff risk.")
        return "\n".join(out_lines)

    except Exception as e:
        return f"❌ Error in bundle_tasks MCP (self-contained): {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
