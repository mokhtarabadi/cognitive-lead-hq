#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mcp[cli]>=1.0,<2.0",
#     "pyyaml",
# ]
# ///

import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml
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

        # Prepend YAML frontmatter if not present
        if not content.strip().startswith("---"):
            frontmatter = {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "status": "active",
                "tags": [],
            }
            content = f"---\n{yaml.dump(frontmatter, default_flow_style=False)}---\n\n{content}"

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
    """Performs a full-text search across memories. If namespace is provided, limits search to that slice.

    Supports tag filtering: include `tag:xxx` in the query to filter by frontmatter tag.
    Results are ranked: exact key matches rank higher than content-only matches.
    """
    if not MEMORY_DIR.exists():
        return "No memories recorded yet."

    try:
        target_dir = _validate_and_resolve(namespace) if namespace else MEMORY_DIR
    except ValueError as e:
        return f"Error: {str(e)}"

    if not target_dir.exists():
        return f"Namespace '{namespace}' does not exist."

    # Parse tag filter from query
    tag_filter = None
    search_query = query
    tag_match = re.search(r'\btag:(\S+)', query)
    if tag_match:
        tag_filter = tag_match.group(1).lower()
        search_query = query[:tag_match.start()].strip() + " " + query[tag_match.end():].strip()
        search_query = search_query.strip()

    results = []
    for md_file in target_dir.rglob("*.md"):
        try:
            file_rel = md_file.relative_to(MEMORY_DIR)
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse YAML frontmatter for tag filtering and ranking
            file_tags = []
            has_frontmatter = content.strip().startswith("---")
            if has_frontmatter:
                try:
                    end_idx = content.index("---", 3)
                    fm_text = content[3:end_idx].strip()
                    fm_data = yaml.safe_load(fm_text)
                    if isinstance(fm_data, dict):
                        file_tags = [t.lower() for t in fm_data.get("tags", [])]
                except Exception:
                    pass

            # Apply tag filter
            if tag_filter and tag_filter not in file_tags:
                continue

            key_name = md_file.stem.lower()
            content_lower = content.lower()

            # If search_query is empty and we have a tag filter, the tag match is sufficient
            if not search_query and tag_filter:
                # Tag-only query: include all files that matched the tag filter
                snippet = content[:200] + "..." if len(content) > 200 else content
                results.append((1, f"   **{file_rel}**\n{snippet}\n"))
            else:
                query_lower = search_query.lower() if search_query else query.lower()
                key_match = query_lower in key_name if query_lower else False
                content_match = query_lower in content_lower if query_lower else True

                if key_match or content_match:
                    snippet = content[:200] + "..." if len(content) > 200 else content
                    rank_marker = "⭐ " if key_match else "   "
                    results.append((0 if key_match else 1, f"{rank_marker}**{file_rel}**\n{snippet}\n"))

        except Exception:
            continue

    if not results:
        return f"No memories found matching '{query}'."

    # Sort by rank (0 = key match first, 1 = content match)
    results.sort(key=lambda x: x[0])
    ranked_results = [r[1] for r in results]

    return "### Search Results\n\n" + "\n---\n".join(ranked_results)

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
