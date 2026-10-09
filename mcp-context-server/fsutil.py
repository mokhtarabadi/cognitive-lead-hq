# Sibling Docs: README.md | Decisions: DECISIONS.md


"""Filesystem scanning: gitignore filtering, trees, source reads, report writes. Stdlib-pure: no MCP imports, no registration, no import back to server."""

import os
import sys
from pathlib import Path
from typing import Optional

import pathspec


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
        # Repo boundary (Task 238 fix loop): git only applies .gitignore
        # files INSIDE the repo. The old walk-to-/ let a grandparent
        # .gitignore (e.g. `projects/` two levels up) mark every in-repo
        # path ignored, which broke get_directory_tree("."). Stop at the
        # nearest self-or-ancestor dir containing .git (its spec still
        # applies); with no repo found, floor at cwd when the path lives
        # under it, else keep the legacy walk-to-/ behavior.
        boundary: Path | None = None
        probe = abs_path if abs_path.is_dir() else abs_path.parent
        cwd = Path.cwd().resolve()
        # Both .git forms stop the walk: a directory in normal repos, a
        # FILE in submodule/worktree roots (gitdir pointer). Either way
        # this dir is a repo root and .gitignore files above it never
        # apply inside.
        while True:
            dot_git = probe / ".git"
            if dot_git.is_dir() or dot_git.is_file():
                boundary = probe
                break
            if probe == probe.parent:
                break
            probe = probe.parent
        if boundary is None:
            try:
                abs_path.relative_to(cwd)
                boundary = cwd
            except ValueError:
                boundary = None
        current = abs_path if abs_path.is_dir() else abs_path.parent
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
            if boundary is not None and current == boundary:
                break
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


TREE_MAX_DEPTH = 8


TREE_MAX_ENTRIES = 2000


COLLECT_MAX_FILES = 1000
# Directory names never descended into, at any level. Supplements .gitignore
# (which cannot cover absolute-path walks outside any repo).


BANNED_DIRS = frozenset(
    {
        ".git",
        ".cache",
        "__pycache__",
        "node_modules",
        ".venv",
        "venv",
        "proc",
        "sys",
        "dev",
    }
)


def _is_banned_dir(entry: Path) -> bool:
    """True when a directory entry must never be descended into."""
    try:
        return entry.is_dir() and entry.name in BANNED_DIRS
    except OSError:
        return True  # Unstatable entries are treated as unsafe to descend.


def generate_tree(
    dir_path: Path,
    ignore_filter: GitIgnoreFilter,
    max_depth: int = TREE_MAX_DEPTH,
    max_entries: int = TREE_MAX_ENTRIES,
) -> str:
    lines = ["```text", dir_path.name or str(dir_path)]
    state = {"count": 0, "truncated": False}

    def _walk(current_path: Path, prefix: str, depth: int) -> None:
        if state["truncated"]:
            return
        if depth > max_depth:
            lines.append(f"{prefix}└── [Max depth reached ({max_depth})]")
            return
        try:
            entries = list(current_path.iterdir())
        except (PermissionError, OSError):
            lines.append(f"{prefix}└── [Unreadable directory]")
            return
        valid_entries = [
            e
            for e in entries
            if not _is_banned_dir(e) and not ignore_filter.is_ignored(e)
        ]
        sorted_entries = sorted(
            valid_entries, key=lambda e: (not e.is_dir(), e.name.lower())
        )
        for i, entry in enumerate(sorted_entries):
            if state["count"] >= max_entries:
                lines.append(
                    f"{prefix}└── [Truncated: entry limit reached ({max_entries})]"
                )
                state["truncated"] = True
                return
            state["count"] += 1
            is_last = i == (len(sorted_entries) - 1)
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{entry.name}")
            if entry.is_dir():
                extension = "    " if is_last else "│   "
                _walk(entry, prefix + extension, depth + 1)

    _walk(dir_path, "", 0)
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
            lines.append(
                f"> Skipped: (File too large: {size} bytes > max_size={max_size})\n"
            )
            # Discovery gap fix (Task 241): a skipped body must not mean
            # zero evidence — attach structural signatures when extractable
            # so the Brain still sees the file's shape. Never raises.
            try:
                # Lazy import: keeps this module free of sibling edges at import
                # time (QA catch: the split stranded this call without it).
                from signatures import _extract_via_tree_sitter

                sig = _extract_via_tree_sitter(file_path)
                if sig:
                    lines.append(
                        "> Body omitted by size cap; structural signatures follow:\n"
                    )
                    lines.append(sig)
                else:
                    lines.append(
                        "> No signatures extracted — narrow `paths`, raise "
                        "`max_size`, or call `extract_signatures` on this file.\n"
                    )
            except Exception as sig_err:
                lines.append(f"> Signature fallback failed: ({sig_err})\n")
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
        lines.append(
            f"> Skipped: (Could not decode file with any supported encoding)\n"
        )
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


def collect_files(
    target: str,
    ignore_filter: GitIgnoreFilter,
    max_files: int = COLLECT_MAX_FILES,
) -> list[Path]:
    p = Path(target)
    if not p.exists() or ignore_filter.is_ignored(p):
        return []
    if p.is_file():
        return [p]
    collected = []
    for root, dirs, files in os.walk(p):
        root_path = Path(root)
        dirs[:] = [
            d
            for d in dirs
            if (root_path / d).name not in BANNED_DIRS
            and not ignore_filter.is_ignored(root_path / d)
        ]
        for f in files:
            if len(collected) >= max_files:
                return collected
            file_path = root_path / f
            if not ignore_filter.is_ignored(file_path):
                collected.append(file_path)
    return collected


def _ensure_context_reports_ignored(workspace_root: Path | None = None) -> None:
    """Safeguard: Append context-reports/ to <workspace_root>/.gitignore.

    Every report-producing tool calls this so generated reports are never
    accidentally committed. The target is the caller's project root, not the
    process cwd: under the singleton the server runs from the global install
    dir, so a bare ``Path(".gitignore")`` edited the wrong file. A ``None``
    root keeps the old cwd behavior for project_root-omitted calls.
    """
    base = workspace_root if workspace_root is not None else Path.cwd()
    gitignore = base / ".gitignore"
    if gitignore.is_file():
        try:
            with open(gitignore, "r+", encoding="utf-8") as f:
                content = f.read()
                if "context-reports/" not in content:
                    f.write("\n# Custom Context MCP reports\ncontext-reports/\n")
        except Exception as e:
            print(f"Warning: Failed to update .gitignore: {e}", file=sys.stderr)
