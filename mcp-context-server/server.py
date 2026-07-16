#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pathspec",
#     "mcp[cli]",
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
    """Extracts structural signatures (classes, functions, methods) from source files using tree-sitter AST. Falls back to regex when no tree-sitter grammar is available for the language."""
    path = Path(file_path)
    if not path.is_file():
        return f"Error: File not found: {file_path}"

    # Try tree-sitter AST extraction first
    ts_result = _extract_via_tree_sitter(path)
    if ts_result:
        return ts_result

    # Fallback to regex
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
            return f"No structural signatures found in {file_path}."

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

@mcp.tool()
def commit_and_clean_task(task_file_path: str, commit_message: str) -> str:
    """Commits staged changes, captures the commit hash, replaces the raw diff in the task file with the hash to save space, and amends the commit to include the cleaned task file."""
    try:
        # 1. Commit staged changes
        subprocess.run(["git", "commit", "-m", commit_message], check=True, capture_output=True, text=True)
        
        # 2. Get the commit hash
        hash_proc = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True)
        commit_hash = hash_proc.stdout.strip()
        
        # 3. Read task file and clean diff
        path = Path(task_file_path)
        if path.is_file():
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            pattern = re.compile(r'<!-- BEGIN_GIT_DIFF -->.*<!-- END_GIT_DIFF -->', re.DOTALL)
            if pattern.search(content):
                clean_block = f"<!-- BEGIN_GIT_DIFF -->\n**Factual Git Diff:** Stored in Commit Hash: `{commit_hash}`\n<!-- END_GIT_DIFF -->"
                new_content = pattern.sub(clean_block, content)
                
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                    
                # 4. Stage the cleaned task file and amend
                subprocess.run(["git", "add", "-A", "tasks/"], check=True, capture_output=True)
                subprocess.run(["git", "commit", "--amend", "--no-edit"], check=True, capture_output=True)
                
        return f"✅ Success: Code committed (Hash: {commit_hash}). Task file {task_file_path} cleaned and amended."
    except subprocess.CalledProcessError as e:
        return f"❌ Git Error: {e.stderr}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
