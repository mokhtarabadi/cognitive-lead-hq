#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mcp[cli]>=1.0,<2.0"
# ]
# ///

import os
import re
import tempfile
from pathlib import Path
from typing import Optional
from mcp.server.fastmcp import FastMCP

MEMORY_DIR = Path(".opencode/memory")

mcp = FastMCP("ProjectMemory")

def _validate_and_resolve(namespace: str, key: Optional[str] = None) -> Path:
    if not re.match(r"^[a-zA-Z0-9_-]+$", namespace):
        raise ValueError(f"Invalid namespace '{namespace}'. Only alphanumeric, hyphens, and underscores are allowed.")

    if key is not None and not re.match(r"^[a-zA-Z0-9_-]+$", key):
        raise ValueError(f"Invalid key '{key}'. Only alphanumeric, hyphens, and underscores are allowed.")

    base_dir = MEMORY_DIR.resolve()
    target_path = (base_dir / namespace).resolve()

    if not target_path.is_relative_to(base_dir):
        raise ValueError("Path traversal attempt detected.")

    return target_path

def _ensure_namespace(namespace: str) -> Path:
    ns_dir = _validate_and_resolve(namespace)
    ns_dir.mkdir(parents=True, exist_ok=True)
    return ns_dir

@mcp.tool()
def store_memory(namespace: str, key: str, content: str, overwrite: bool = True) -> str:
    """Stores a memory snippet as a markdown file. Uses atomic writes to prevent race conditions."""
    try:
        ns_dir = _ensure_namespace(namespace)
        _validate_and_resolve(namespace, key)
        file_path = ns_dir / f"{key}.md"

        if file_path.exists() and not overwrite:
            return f"Error: Memory '{key}' in namespace '{namespace}' already exists and overwrite is False."

        fd, temp_path = tempfile.mkstemp(dir=ns_dir, text=True)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(content)
            os.replace(temp_path, file_path)
        except Exception as e:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise e

        return f"Memory successfully stored at {file_path}"
    except Exception as e:
        return f"Error storing memory: {str(e)}"

@mcp.tool()
def read_memory(namespace: str, key: str) -> str:
    """Reads a specific memory snippet."""
    try:
        ns_dir = _validate_and_resolve(namespace, key)
        file_path = ns_dir / f"{key}.md"
        if not file_path.is_file():
            return f"Error: Memory '{key}' not found in namespace '{namespace}'."

        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading memory: {str(e)}"

@mcp.tool()
def delete_memory(namespace: str, key: str) -> str:
    """Deletes a specific memory snippet if it is no longer relevant."""
    try:
        ns_dir = _validate_and_resolve(namespace, key)
        file_path = ns_dir / f"{key}.md"

        if not file_path.is_file():
            return f"Error: Memory '{key}' not found in namespace '{namespace}'."

        file_path.unlink()

        if not any(ns_dir.iterdir()):
            ns_dir.rmdir()

        return f"Memory '{key}' successfully deleted from '{namespace}'."
    except Exception as e:
        return f"Error deleting memory: {str(e)}"

@mcp.tool()
def search_memory(query: str, namespace: Optional[str] = None) -> str:
    """Performs a full-text search across memories. If namespace is provided, limits search to that slice."""
    if not MEMORY_DIR.exists():
        return "No memories recorded yet."

    try:
        target_dir = _validate_and_resolve(namespace) if namespace else MEMORY_DIR
    except ValueError as e:
        return f"Error: {str(e)}"

    if not target_dir.exists():
        return f"Namespace '{namespace}' does not exist."

    results = []
    for md_file in target_dir.rglob("*.md"):
        try:
            file_rel = md_file.relative_to(MEMORY_DIR)
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if query.lower() in content.lower() or query.lower() in md_file.name.lower():
                    snippet = content[:200] + "..." if len(content) > 200 else content
                    results.append(f"- **{file_rel}**\n{snippet}\n")
        except Exception:
            continue

    if not results:
        return f"No memories found matching '{query}'."

    return "### Search Results\n\n" + "\n---\n".join(results)

@mcp.tool()
def list_namespaces() -> str:
    """Lists all active memory namespaces and their keys."""
    if not MEMORY_DIR.exists():
        return "No memory namespaces found."

    tree = []
    for ns_dir in sorted(MEMORY_DIR.iterdir()):
        if ns_dir.is_dir():
            keys = [f.stem for f in ns_dir.glob("*.md")]
            tree.append(f"- {ns_dir.name}/")
            for k in sorted(keys):
                tree.append(f"  - {k}")

    return "\n".join(tree) if tree else "Memory bank is empty."

if __name__ == "__main__":
    mcp.run(transport="stdio")
