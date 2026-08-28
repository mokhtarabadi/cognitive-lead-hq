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

def build_memory_index() -> str:
    """
    Scans MEMORY_DIR for all Markdown memories and builds a sorted, pipe-escaped
    Markdown table index at MEMORY_DIR / "index.md".

    The index is derived state: it lists every memory shard as a row with
    Namespace, Key, Summary (first non-empty content line after frontmatter,
    clamped to 120 chars, pipes escaped), and Tags (from YAML frontmatter).

    Write is atomic via tempfile.mkstemp(dir=MEMORY_DIR) + os.replace, matching
    the safety guarantees of store_memory. Failures are logged but never
    propagated to the caller — the index is best-effort derived state.

    Returns:
        Status message describing the build result (row count or empty notice).
    """
    try:
        # Ensure memory directory exists so mkstemp has a valid dir
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)

        # Collect all memory files, excluding the derived index itself and
        # any nested goals or non-Markdown artifacts.
        memory_files = []
        for md_file in MEMORY_DIR.rglob("*.md"):
            # Skip the derived index itself to avoid self-reference
            if md_file.name == "index.md":
                continue
            # MEMORY_DIR is flat namespaces; rglob is safe but we filter
            # to only files directly under a namespace directory (one level)
            # and also handle deeper nesting if present. Keep all.
            memory_files.append(md_file)

        rows = []
        for md_file in sorted(memory_files):
            try:
                # Derive namespace (parent dir name) and key (stem)
                # For .opencode/memory/<namespace>/<key>.md, parent is namespace
                # For deeper nesting, use relative parent
                rel = md_file.relative_to(MEMORY_DIR)
                # Namespace is first part of relative path (e.g., "workflows" in "workflows/foo.md")
                namespace = rel.parts[0] if len(rel.parts) >= 2 else rel.parent.name or "root"
                # Key is file stem (without .md)
                key = md_file.stem

                # Read file content safely
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Parse frontmatter tags and locate summary start
                tags = []
                summary_start_idx = 0
                if content.strip().startswith("---"):
                    try:
                        # Find closing --- (search from index 3)
                        end_idx = content.index("---", 3)
                        fm_text = content[3:end_idx].strip()
                        fm_data = yaml.safe_load(fm_text)
                        if isinstance(fm_data, dict):
                            raw_tags = fm_data.get("tags", [])
                            if isinstance(raw_tags, list):
                                tags = [str(t) for t in raw_tags]
                        # Summary starts after the closing ---
                        summary_start_idx = end_idx + 3
                    except Exception:
                        # Malformed frontmatter: treat entire file as content
                        summary_start_idx = 0

                # Extract summary: first non-empty line after frontmatter
                summary = ""
                # Slice content after frontmatter, split lines, find first non-empty
                content_after = content[summary_start_idx:].strip()
                for line in content_after.splitlines():
                    stripped = line.strip()
                    if stripped:
                        summary = stripped
                        break
                # Fallback to key if no summary line found
                if not summary:
                    summary = key

                # Clamp to 120 chars and escape pipes to preserve table columns
                if len(summary) > 120:
                    summary = summary[:117] + "..."
                summary = summary.replace("|", "\\|")
                # Also escape pipes in tags
                tags_str = ", ".join(str(t).replace("|", "\\|") for t in tags) if tags else ""

                rows.append((namespace, key, summary, tags_str))
            except Exception:
                # Skip unreadable or malformed shards; continue building index
                continue

        # Sort rows by namespace then key for deterministic output
        rows.sort(key=lambda x: (x[0].lower(), x[1].lower()))

        # Build Markdown content
        header = "# Project Memory Index\n\n> Auto-generated by `mcp-memory-server`. Do not edit directly.\n\n"
        if not rows:
            body = "*No memories recorded yet.*\n"
        else:
            body_lines = []
            body_lines.append("| Namespace | Key | Summary | Tags |")
            body_lines.append("| :--- | :--- | :--- | :--- |")
            for ns, k, s, t in rows:
                # Escape pipes already done; ensure no newlines in cells
                body_lines.append(f"| {ns} | {k} | {s} | {t} |")
            body = "\n".join(body_lines) + "\n"

        full_content = header + body

        # Atomic write to MEMORY_DIR / "index.md"
        index_path = MEMORY_DIR / "index.md"
        fd, temp_path = tempfile.mkstemp(dir=MEMORY_DIR, text=True)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(full_content)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, index_path)
        except Exception as e:
            # Clean up temp file on failure; log but don't raise
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass
            # Best-effort: log to stderr but return error status
            print(f"[build_memory_index] atomic write failed: {e}", flush=True)
            return f"Error building index: {e}"

        # Best-effort fsync parent directory for durability (ignore if not supported)
        try:
            dir_fd = os.open(MEMORY_DIR, os.O_DIRECTORY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        except Exception:
            pass

        if not rows:
            return "Memory index built: 0 memories (empty)"
        return f"Memory index built: {len(rows)} memories indexed"

    except Exception as e:
        # Catch-all: never propagate to caller, just log
        print(f"[build_memory_index] unexpected error: {e}", flush=True)
        return f"Error building index: {e}"

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

        # Best-effort: rebuild memory index after successful store (derived state, never fail parent)
        try:
            build_memory_index()
        except Exception as e:
            print(f"[store_memory] index rebuild failed: {e}", flush=True)

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

        # Best-effort: rebuild memory index after successful delete
        try:
            build_memory_index()
        except Exception as e:
            print(f"[delete_memory] index rebuild failed: {e}", flush=True)

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

@mcp.tool()
def rebuild_memory_index() -> str:
    """
    Rebuilds the project memory index at .opencode/memory/index.md.

    Scans all memory shards under MEMORY_DIR, builds a sorted Markdown
    table (Namespace | Key | Summary | Tags), and writes atomically.
    Useful for manual recovery if the index was deleted or became stale
    via out-of-band file operations (e.g., manual rm). Always
    best-effort; returns a status string with row count.

    The tool is exposed as an MCP tool so agents and managers can
    trigger a rebuild on demand without needing a store/delete cycle.
    """
    return build_memory_index()

if __name__ == "__main__":
    mcp.run(transport="stdio")
