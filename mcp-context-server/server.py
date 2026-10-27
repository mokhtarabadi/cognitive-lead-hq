#!/usr/bin/env -S uv run
# Sibling Docs: mcp-context-server/README.md | Decisions: mcp-context-server/DECISIONS.md
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

import contextvars
import functools
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mcp.server.fastmcp import FastMCP

from fsutil import (
    BANNED_DIRS,
    COLLECT_MAX_FILES,
    GitIgnoreFilter,
    TEXT_ENCODINGS,
    TREE_MAX_DEPTH,
    TREE_MAX_ENTRIES,
    _ensure_context_reports_ignored,
    _is_banned_dir,
    collect_files,
    generate_tree,
    is_binary,
    process_source_file,
)
from signatures import (
    _EXTENSION_LANG_MAP,
    _TS_QUERIES,
    _extract_signature_line,
    _extract_via_tree_sitter,
    _get_ts_language,
    _ts_language_cache,
)
from graph import (
    GRAPH_DOC_LINES,
    GRAPH_DOC_SECTIONS,
    GRAPH_MAX_DOCS,
    GRAPH_MAX_FILES,
    GRAPH_MAX_NODES,
    GRAPH_SCHEMA_VERSION,
    _GRAPH_ADR_REF_RE,
    _GRAPH_ANDROID_ID_RE,
    _GRAPH_ARROW_RE,
    _GRAPH_CALL_RE,
    _GRAPH_CODE_EXTS,
    _GRAPH_CSS_RE,
    _GRAPH_DART_KEYWORDS,
    _GRAPH_DART_RE,
    _GRAPH_DOM_ID_RE,
    _GRAPH_GET_ID_RE,
    _GRAPH_GOD_NOISE,
    _GRAPH_JAVA_CTOR_RE,
    _GRAPH_JAVA_METHOD_RE,
    _GRAPH_KT_FUN_RE,
    _GRAPH_MAX_SCAN_BYTES,
    _GRAPH_MD_HEADING_RE,
    _GRAPH_MD_LINK_RE,
    _GRAPH_OBJC_IMPL_RE,
    _GRAPH_OBJC_METHOD_RE,
    _GRAPH_PRISMA_RE,
    _GRAPH_PROP_RE,
    _GRAPH_R_ID_RE,
    _GRAPH_SCRIPT_BLOCK_RE,
    _GRAPH_SQL_REF_RE,
    _GRAPH_SQL_TABLE_RE,
    _GRAPH_SWIFT_RE,
    _GRAPH_SYMBOL_RE,
    _GRAPH_TASK_REF_RE,
    _GRAPH_TOKEN_SPLIT_RE,
    _GRAPH_TYPE_RE,
    _GRAPH_WIKILINK_RE,
    _build_graph_data,
    _extract_graph_symbols,
    _extract_md_link_targets,
    _extract_md_sections,
    _extract_sql_symbols,
    _find_graph_nodes,
    _graph_bfs_path,
    _graph_degrees,
    _graph_neighbors,
    _graph_tokens,
    _graph_vocab,
    _load_graph_data,
    _parse_graph_imports,
    _push_graph_symbol,
    _read_text_capped,
    _resolve_doc_link,
    _resolve_graph_file,
    _resolve_import_to_rel,
    _save_graph,
    _scan_js_like_symbols,
    _slugify_section,
    _suggest_vocab_tokens,
)
from gitops import (
    ACTIVE_KANBAN_DIRS,
    DIFF_SIZE_WARNING_THRESHOLD,
    MAX_BUNDLE_SIZE,
    _CONVENTIONAL_RE,
    _check_conventional_commit,
    _derive_task_slug,
    _detect_stack,
    _discover_next_id,
    _extract_checklist_with_continuations,
    _extract_section,
    _extract_title,
    _find_task_file,
    backfill_started_from_git,
    stamp_task_header,
    task_start_stamp,
    _format_task_id_list,
    _git_mv_or_fallback,
    _kebab_case,
    _locate_task_file,
    _next_id_collision,
    _patch_archived_file,
    _repo_root,
    _verify_verbatim_checksums,
)
from bundle import (
    _build_meta_content,
)


mcp = FastMCP("CustomContext", host="127.0.0.1", port=8102)

# Client-visible project-isolation warning (Task 279 F6/V1). When a caller
# omits project_root the helper below falls back to the server cwd; stderr
# never reaches MCP clients, so the fallback is recorded here and surfaced
# by @_project_tool in the tool result. No absolute paths are echoed
# (layout privacy, cf. decision-server _active_root_info).


_FALLBACK_FIRED: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "custom_context_fallback_fired", default=False
)


ROOT_FALLBACK_WARNING = (
    "WARNING [project-isolation]: project_root was omitted, so this call "
    "was scoped to the singleton server's own directory instead of the "
    "calling project. Pass an absolute project_root on every call."
)


def _project_tool(fn):
    """Register an MCP tool that surfaces root-fallback client-visibly."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        _FALLBACK_FIRED.set(False)
        out = fn(*args, **kwargs)
        if not _FALLBACK_FIRED.get():
            return out
        if isinstance(out, str):
            return ROOT_FALLBACK_WARNING + "\n" + out
        return out

    return mcp.tool()(wrapper)


def _safe_depth(value: object) -> int:
    """Clamp a caller-supplied tree depth to the supported range."""
    try:
        return max(1, min(int(value), TREE_MAX_DEPTH))
    except (TypeError, ValueError):
        return 3


def _safe_entries(value: object) -> int:
    """Clamp a caller-supplied tree entry cap to the supported range."""
    try:
        return max(1, min(int(value), TREE_MAX_ENTRIES))
    except (TypeError, ValueError):
        return TREE_MAX_ENTRIES


@_project_tool
def get_directory_tree(
    target_path: str = ".",
    project_root: str | None = None,
    max_depth: int = 3,
    max_entries: int = TREE_MAX_ENTRIES,
) -> str:
    """Generates an ASCII tree representation of the directory, respecting .gitignore. Use this to discover codebase structure with immediate inline output. Use create_tree_report instead when a persistent saved report file is required. project_root: absolute path to the calling project's repository root. Used to scope file resolution to that project. If omitted, falls back to the server working directory for backward compatibility."""
    # Security: mirror create_tree_report — coerce bad types, resolve against
    # the workspace root, reject escapes. Previously a bare "/" walked the
    # whole filesystem and wedged the single-threaded server (Task 177).
    if not isinstance(target_path, str):
        target_path = "."
    try:
        workspace_root = _explicit_project_root(project_root, "get_directory_tree")
    except ValueError as e:
        return f"Error: {e}"
    if Path(target_path).is_absolute():
        tree_path = Path(target_path).resolve()
    else:
        tree_path = (workspace_root / target_path).resolve()
    try:
        tree_path.relative_to(workspace_root)
    except ValueError:
        return "Error: Path traversal detected. target_path must be within the project workspace."
    ignore_filter = GitIgnoreFilter()
    if not tree_path.is_dir():
        return f"Error: {target_path} is not a valid directory."
    if ignore_filter.is_ignored(tree_path):
        return f"Warning: Target tree path is ignored by .gitignore: {target_path}"
    depth = _safe_depth(max_depth)
    entries = _safe_entries(max_entries)
    return (
        f"## Directory Tree: `{tree_path}`\n\n"
        f"(depth {depth}, entry cap {entries}; pass max_depth/max_entries for more)\n\n"
        + generate_tree(tree_path, ignore_filter, max_depth=depth, max_entries=entries)
    )


# --- Lite knowledge-graph (Graphify-inspired, stdlib-only) ---
# Design: deterministic local graph, no LLM, no vector store. Nodes are files
# + symbols (def/class). Edges carry confidence tags EXTRACTED (explicit in
# source: contains/imports) or INFERRED (resolved: references across files).
# Persisted as versioned graph.json + markdown report under context-reports/.


@_project_tool
def build_graph(
    target_path: str = ".",
    project_root: str | None = None,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    max_files: int | None = None,
    max_docs: int | None = None,
    max_nodes: int | None = None,
) -> str:
    """Builds a unified deterministic knowledge-graph (code incl. SQL plus Markdown docs: files + symbols + sections, contains/imports/references with EXTRACTED/INFERRED tags) and saves versioned graph.json plus a markdown report under context-reports/. Use before query_graph/explain_node/shortest_path/god_nodes. project_root scopes the scan; target_path scopes the subgraph."""
    if not isinstance(target_path, str):
        target_path = "."
    try:
        workspace_root = _explicit_project_root(project_root, "build_graph")
    except ValueError as e:
        return f"Error: {e}"
    _ensure_context_reports_ignored(workspace_root)
    tgt = (
        Path(target_path)
        if Path(target_path).is_absolute()
        else workspace_root / target_path
    )
    try:
        tgt = tgt.resolve()
        tgt.relative_to(workspace_root)
    except ValueError:
        return "Error: Path traversal detected. target_path must be within the project workspace."
    if not tgt.exists():
        return f"Error: {target_path} not found."
    started = time.monotonic()
    data = _build_graph_data(
        workspace_root,
        tgt if tgt.is_dir() else tgt.parent,
        include=include if isinstance(include, list) else None,
        exclude=exclude if isinstance(exclude, list) else None,
        max_files=max_files if isinstance(max_files, int) else None,
        max_docs=max_docs if isinstance(max_docs, int) else None,
        max_nodes=max_nodes if isinstance(max_nodes, int) else None,
    )
    json_path, md_path = _save_graph(workspace_root, data, str(tgt))
    dur = time.monotonic() - started
    meta = data.get("meta", {})
    caps = meta.get("caps", {})
    scanned = meta.get("scanned", {})
    indexed = meta.get("indexed", {})
    reasons = [name for name, hit in (meta.get("truncated") or {}).items() if hit]
    coverage = (
        f"📈 Coverage: {indexed.get('files', 0)}/{scanned.get('files', 0)} files, "
        f"{indexed.get('docs', 0)}/{scanned.get('docs', 0)} docs"
        + (f" (truncated: {', '.join(reasons)})" if reasons else " (complete)")
    )
    return (
        f"✅ Success: Graph built for `{tgt}`.\n"
        f"📊 {len(data['nodes'])} nodes, {len(data['links'])} links in {dur:.2f}s "
        f"(schema {GRAPH_SCHEMA_VERSION}, caps files {caps.get('files')}/docs "
        f"{caps.get('docs')}/nodes {caps.get('nodes')}).\n"
        f"{coverage}\n"
        f"📁 Graph: `{json_path}`\n📁 Report: `{md_path}`"
    )


@_project_tool
def query_graph(
    question: str,
    graph_path: str | None = None,
    top_n: int = 10,
    mode: str = "bfs",
    project_root: str | None = None,
) -> str:
    """Queries the lite graph with plain words: scores nodes by token overlap, then traverses (bfs: 2-hop fan-out for 'what connects to X'; dfs: depth-6 chains for 'how does X reach Y') and returns a scoped subgraph. Zero hits suggest closest vocabulary tokens. Run build_graph first. Pass graph_path to pin a graph file, else the latest in context-reports/ is used."""
    try:
        workspace_root = _explicit_project_root(project_root, "query_graph")
    except ValueError as e:
        return f"Error: {e}"
    if not isinstance(question, str) or not question.strip():
        return "Error: question must be a non-empty string."
    if mode not in ("bfs", "dfs"):
        return "Error: mode must be 'bfs' or 'dfs'."
    data, gp, err = _load_graph_data(workspace_root, graph_path)
    if err or data is None:
        return f"Error: {err}"
    toks = _graph_tokens(question)
    exact_needle = question.strip().lower()
    scored: list[tuple[int, dict]] = []
    for n in data.get("nodes", []):
        nt = _graph_tokens(f"{n.get('label', '')} {n.get('source_file', '')}")
        overlap = len(toks & nt)
        if overlap == 0 and n.get("label", "").lower() != exact_needle:
            continue
        nid = n.get("id", "")
        weight = 3 if nid.startswith("sym:") else 2 if nid.startswith("file:") else 1
        score = overlap * weight
        if n.get("label", "").lower() == exact_needle or nid.lower() == exact_needle:
            score += 50
        scored.append((score, n))
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
    seeds = [n for _, n in scored[:3]]
    if not seeds:
        hints = _suggest_vocab_tokens(_graph_vocab(data), toks)
        hint_txt = f" Closest vocabulary: {', '.join(hints)}." if hints else ""
        return f"No nodes matched '{question}' in `{gp}`.{hint_txt} Try build_graph on a wider target."
    keep: dict[str, dict] = {}
    keep_links: list[dict] = []
    seen_link_keys: set[tuple[str, str, str]] = set()

    def _add_link(e: dict) -> None:
        key = (e["source"], e["target"], e["relation"])
        if key not in seen_link_keys:
            seen_link_keys.add(key)
            keep_links.append(e)

    if mode == "dfs":
        adj: dict[str, list[tuple[str, dict]]] = {}
        for e in data.get("links", []):
            adj.setdefault(e["source"], []).append((e["target"], e))
            adj.setdefault(e["target"], []).append((e["source"], e))
        visited: set[str] = set()
        stack: list[tuple[str, int]] = [(s["id"], 0) for s in reversed(seeds)]
        id2n = {n["id"]: n for n in data.get("nodes", [])}
        while stack and len(keep) < max(10, top_n * 3):
            nid, depth = stack.pop()
            if nid in visited or depth > 6 or nid not in id2n:
                continue
            visited.add(nid)
            keep[nid] = id2n[nid]
            if depth < 6:
                for nxt, e in sorted(adj.get(nid, []), key=lambda x: x[0]):
                    if nxt not in visited:
                        _add_link(e)
                        stack.append((nxt, depth + 1))
    else:
        for s in seeds:
            keep[s["id"]] = s
            out, inc = _graph_neighbors(data, s["id"])
            for e, o in (out + inc)[:20]:
                keep[o["id"]] = o
                _add_link(e)
                out2, inc2 = _graph_neighbors(data, o["id"])
                for e2, o2 in (out2 + inc2)[:5]:
                    if len(keep) >= max(10, top_n * 3):
                        break
                    keep[o2["id"]] = o2
                    _add_link(e2)
    lines = [
        f"Query ({mode}): {question}",
        f"Graph: `{gp}`",
        _graph_coverage_line(data, workspace_root),
        f"Seeds: {', '.join(s.get('label', '?') for s in seeds)}",
        "",
        f"Nodes ({len(keep)}):",
    ]
    for nid in sorted(keep)[: max(10, top_n * 3)]:
        n = keep[nid]
        lines.append(
            f"- {n.get('label')} [{n.get('file_type', '?')}] {n.get('source_file', '')} {n.get('source_location', '')}"
        )
    lines.append("")
    lines.append(f"Edges ({len(keep_links)}):")
    for e in keep_links[:50]:
        lines.append(
            f"- {e['source']} --{e['relation']}[{e['confidence']}]--> {e['target']}"
        )
    text = "\n".join(lines)
    if len(text) > 8000:
        text = (
            text[:8000] + "\n... (truncated at output cap — narrow top_n or question)"
        )
    return text


@_project_tool
def explain_node(
    label: str, graph_path: str | None = None, project_root: str | None = None
) -> str:
    """Explains one graph concept: source location, type, degree, and top connections with [relation][confidence]. Use after build_graph."""
    try:
        workspace_root = _explicit_project_root(project_root, "explain_node")
    except ValueError as e:
        return f"Error: {e}"
    if not isinstance(label, str) or not label.strip():
        return "Error: label must be a non-empty string."
    data, gp, err = _load_graph_data(workspace_root, graph_path)
    if err or data is None:
        return f"Error: {err}"
    matches = _find_graph_nodes(data.get("nodes", []), label)
    if not matches:
        return f"No node matching '{label}' in `{gp}`."
    if len(matches) > 1:
        opts = ", ".join(m.get("label", "?") for m in matches[:5])
        return (
            f"Ambiguous '{label}' ({len(matches)} matches: {opts}). Be more specific."
        )
    n = matches[0]
    deg = _graph_degrees(data).get(n["id"], 0)
    out, inc = _graph_neighbors(data, n["id"])
    lines = [
        f"Node: {n.get('label')}",
        f"  ID: {n['id']}",
        f"  Source: {n.get('source_file', '?')} {n.get('source_location', '')}",
        f"  Type: {n.get('file_type', '?')}",
        f"  Degree: {deg}",
        "",
        f"Connections ({len(out) + len(inc)}):",
    ]
    for e, o in (out + inc)[:20]:
        arrow = "-->" if e["source"] == n["id"] else "<--"
        lines.append(
            f"  {arrow} {o.get('label')} [{e['relation']}] [{e['confidence']}] {o.get('source_file', '')}"
        )
    return "\n".join(lines)


@_project_tool
def shortest_path(
    source: str,
    target: str,
    graph_path: str | None = None,
    undirected: bool = False,
    project_root: str | None = None,
) -> str:
    """Traces the shortest path between two graph concepts. Directed by default; pass undirected=True to ignore edge direction. Use after build_graph."""
    try:
        workspace_root = _explicit_project_root(project_root, "shortest_path")
    except ValueError as e:
        return f"Error: {e}"
    data, gp, err = _load_graph_data(workspace_root, graph_path)
    if err or data is None:
        return f"Error: {err}"
    sm = _find_graph_nodes(data.get("nodes", []), source)
    tm = _find_graph_nodes(data.get("nodes", []), target)
    if not sm:
        return f"No node matching source '{source}'."
    if not tm:
        return f"No node matching target '{target}'."
    if len(sm) > 1 or len(tm) > 1:
        return f"Ambiguous endpoints (source {len(sm)}, target {len(tm)}). Be more specific."
    path = _graph_bfs_path(data, sm[0]["id"], tm[0]["id"], directed=not undirected)
    if not path:
        return f"No path between '{source}' and '{target}' in `{gp}`."
    id2n = {n["id"]: n for n in data.get("nodes", [])}
    lines = [f"Shortest path ({len(path)} hops):"]
    for a, e, b in path:
        al = id2n.get(a, {}).get("label", a)
        bl = id2n.get(b, {}).get("label", b)
        rel = e.get("relation", "?")
        conf = e.get("confidence", "?")
        if e.get("source") == a:
            lines.append(f"  {al} --{rel}[{conf}]--> {bl}")
        else:
            lines.append(f"  {al} <--{rel}[{conf}]-- {bl}")
    return "\n".join(lines)


@_project_tool
def god_nodes(
    top_n: int = 10, graph_path: str | None = None, project_root: str | None = None
) -> str:
    """Lists the most-connected symbol concepts (degree ranking, file hubs and trivial-helper noise excluded). Use after build_graph to find what everything flows through."""
    try:
        workspace_root = _explicit_project_root(project_root, "god_nodes")
    except ValueError as e:
        return f"Error: {e}"
    try:
        top_n = max(1, min(int(top_n), 50))
    except Exception:
        top_n = 10
    data, gp, err = _load_graph_data(workspace_root, graph_path)
    if err or data is None:
        return f"Error: {err}"
    weights = {"EXTRACTED": 2, "INFERRED": 1}
    deg: dict[str, int] = {n["id"]: 0 for n in data.get("nodes", [])}
    for e in data.get("links", []):
        w = weights.get(e.get("confidence"), 1)
        deg[e["source"]] = deg.get(e["source"], 0) + w
        deg[e["target"]] = deg.get(e["target"], 0) + w
    id2n = {n["id"]: n for n in data.get("nodes", [])}

    def _noisy(label: str) -> bool:
        ll = label.lower()
        return (ll.startswith("__") and ll.endswith("__")) or ll in _GRAPH_GOD_NOISE

    ranked = sorted(
        (
            (d, nid)
            for nid, d in deg.items()
            if nid.startswith("sym:") and not _noisy(id2n.get(nid, {}).get("label", ""))
        ),
        reverse=True,
    )[:top_n]
    if not ranked:
        return f"No symbol nodes in `{gp}`."
    lines = [f"God nodes (top {len(ranked)}) in `{gp}`:"]
    for d, nid in ranked:
        n = id2n.get(nid, {})
        lines.append(
            f"- {n.get('label', '?')} — {n.get('source_file', '?')}"
            f"{(' ' + n.get('source_location')) if n.get('source_location') else ''}"
            f" (weighted degree {d})"
        )
    return "\n".join(lines)


def _graph_stale_source(data: dict, workspace_root: Path) -> str | None:
    """Name the first indexed source modified after the build, if any."""
    meta = data.get("graph", {}) or {}
    built_at = meta.get("built_at")
    sources = meta.get("sources") or []
    if not built_at or not sources:
        return None
    newest_mtime = 0.0
    newest_path: str | None = None
    for rel in sources:
        try:
            mtime = (workspace_root / rel).stat().st_mtime
        except OSError:
            continue
        if mtime > newest_mtime:
            newest_mtime, newest_path = mtime, rel
    return newest_path if newest_mtime > built_at else None


def _graph_coverage_line(data: dict, workspace_root: Path) -> str:
    """One line that makes partial coverage and staleness impossible to miss."""
    meta = data.get("graph", {}) or {}
    scanned = meta.get("scanned") or {}
    indexed = meta.get("indexed") or {}
    caps = meta.get("caps") or {}
    truncated = meta.get("truncated") or {}
    if not scanned:
        return "Coverage: unknown (graph built before coverage metadata; rebuild)."
    flags = [name for name, hit in truncated.items() if hit]
    line = (
        f"Coverage: {indexed.get('files', 0)}/{scanned.get('files', 0)} files, "
        f"{indexed.get('docs', 0)}/{scanned.get('docs', 0)} docs; caps "
        f"files {caps.get('files', '?')}/docs {caps.get('docs', '?')}/"
        f"nodes {caps.get('nodes', '?')}"
    )
    if flags:
        line += (
            f"; truncated: {', '.join(flags)} — absence here is not proof of "
            "absence, rebuild or narrow with include"
        )
    else:
        line += "; complete"
    stale = _graph_stale_source(data, workspace_root)
    if stale:
        line += f"; STALE: `{stale}` changed after the build (rebuild)"
    return line


@_project_tool
def graph_stats(graph_path: str | None = None, project_root: str | None = None) -> str:
    """Reports node/edge counts plus EXTRACTED/INFERRED/AMBIGUOUS split and schema version for a built graph."""
    try:
        workspace_root = _explicit_project_root(project_root, "graph_stats")
    except ValueError as e:
        return f"Error: {e}"
    data, gp, err = _load_graph_data(workspace_root, graph_path)
    if err or data is None:
        return f"Error: {err}"
    ext = sum(1 for e in data.get("links", []) if e.get("confidence") == "EXTRACTED")
    inf = sum(1 for e in data.get("links", []) if e.get("confidence") == "INFERRED")
    tot = len(data.get("links", []))
    schema = (data.get("graph", {}) or {}).get("schema_version", "?")
    return (
        f"Graph: `{gp}`\n"
        f"Nodes: {len(data.get('nodes', []))} Edges: {tot} "
        f"(EXTRACTED {ext} / INFERRED {inf} / AMBIGUOUS {tot - ext - inf})\n"
        f"{_graph_coverage_line(data, workspace_root)}\n"
        f"Schema: {schema}"
    )


@_project_tool
def read_source_files(
    paths: list[str],
    max_size: int = 1048576,
    no_line_numbers: bool = False,
    project_root: str | None = None,
) -> str:
    """Reads multiple source files/directories, compiles their contents into a Markdown file under context-reports/, and returns the report file path. Use when exact source content from named files is required. Returns a path, not inline content. Use extract_signatures instead for a structural outline without file bodies. project_root: absolute path to the calling project's repository root. Used to scope file resolution to that project. If omitted, falls back to the server working directory for backward compatibility."""
    try:
        workspace_root = _explicit_project_root(project_root, "read_source_files")
    except ValueError as e:
        return f"Error: {e}"

    # Safeguard: Append context-reports/ to the PROJECT's .gitignore.
    _ensure_context_reports_ignored(workspace_root)

    ignore_filter = GitIgnoreFilter()
    files_to_process: dict[Path, Path] = {}
    for src in paths:
        # Safeguard: Do not recursively scan our own reports directory
        if "context-reports" in Path(src).parts:
            continue
        src_path = src if Path(src).is_absolute() else str(workspace_root / src)
        for p in collect_files(src_path, ignore_filter):
            if "context-reports" in p.parts:
                continue
            resolved = p.resolve()
            try:
                resolved.relative_to(workspace_root)
            except ValueError:
                continue  # symlink/traversal escape: never read outside the project
            files_to_process[resolved] = p

    if not files_to_process:
        return "No files found or all files were ignored."

    started = time.monotonic()
    output_lines = ["## Source Files\n"]
    include_line_numbers = not no_line_numbers
    skipped = 0
    total_bytes = 0
    for _, f in sorted(files_to_process.items(), key=lambda item: str(item[1]).lower()):
        try:
            total_bytes += f.stat().st_size
        except OSError:
            pass
        rendered = process_source_file(f, max_size, include_line_numbers)
        if "> Skipped:" in rendered:
            skipped += 1
        output_lines.append(rendered)
    duration_s = time.monotonic() - started

    result_content = "\n".join(output_lines)

    # Ensure the PROJECT's output directory exists (never the server cwd).
    report_dir = workspace_root / "context-reports"
    report_dir.mkdir(parents=True, exist_ok=True)

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
        f"📊 Report metrics: {len(files_to_process) - skipped} processed, "
        f"{skipped} skipped, {total_bytes} bytes read in {duration_s:.2f}s "
        f"(tree depth cap {TREE_MAX_DEPTH}, collect cap {COLLECT_MAX_FILES}).\n"
        f"📁 Generated Report: `{report_file}`\n\n"
        f"Manager: You can now open `{report_file}` in your local editor to view the codebase context or copy/paste it directly for the AI."
    )


@_project_tool
def create_tree_report(
    target_path: str = ".",
    project_root: str | None = None,
    max_depth: int = 3,
    max_entries: int = TREE_MAX_ENTRIES,
) -> str:
    """Creates a .gitignore-aware directory tree of a path or the entire project and saves it as a Markdown file under context-reports/ (named tree_report_<timestamp>_<uuid>.md). Use when the Manager asks to 'create a tree of the project' or 'create a tree of <path>'. Security: target_path is resolved against the workspace root and rejected if it escapes the project (path traversal prevention). project_root: absolute path to the calling project's repository root. Used to scope file resolution to that project. If omitted, falls back to the server working directory for backward compatibility."""
    # Security: Coerce None or invalid types back to the whole-project default
    # so a malformed tool invocation degrades gracefully instead of crashing.
    if not isinstance(target_path, str):
        target_path = "."

    # Security: Resolve the target against the workspace root and reject any
    # path that escapes it. Path traversal prevention — the tool must never
    # walk directories outside the project the server is running in.
    try:
        workspace_root = _explicit_project_root(project_root, "create_tree_report")
    except ValueError as e:
        return f"Error: {e}"

    # Safeguard: Append context-reports/ to the PROJECT's .gitignore.
    _ensure_context_reports_ignored(workspace_root)
    if Path(target_path).is_absolute():
        tree_path = Path(target_path).resolve()
    else:
        tree_path = (workspace_root / target_path).resolve()
    try:
        tree_path.relative_to(workspace_root)
    except ValueError:
        return "Error: Path traversal detected. target_path must be within the project workspace."

    ignore_filter = GitIgnoreFilter()
    if not tree_path.is_dir():
        return f"Error: {target_path} is not a valid directory."
    if ignore_filter.is_ignored(tree_path):
        return f"Warning: Target tree path is ignored by .gitignore: {target_path}"

    tree_text = generate_tree(
        tree_path,
        ignore_filter,
        max_depth=_safe_depth(max_depth),
        max_entries=_safe_entries(max_entries),
    )

    # Ensure the PROJECT's output directory exists (never the server cwd).
    report_dir = workspace_root / "context-reports"
    report_dir.mkdir(parents=True, exist_ok=True)

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


_SIGNATURE_EXTS = {
    ".py",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".ts",
    ".tsx",
    ".mts",
    ".cts",
    ".go",
    ".java",
    ".jsp",
    ".rs",
    ".kt",
    ".kts",
    ".swift",
    ".rb",
    ".php",
    ".cs",
}


def _signature_block(path: Path, label: str) -> str | None:
    """Tree-sitter first, regex fallback. None when the file has no signature."""
    try:
        ts_result = _extract_via_tree_sitter(path)
    except Exception:
        ts_result = None
    if ts_result:
        return ts_result
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return None
    pattern = re.compile(
        r"^(?:\s*(?:export|default|public|private|protected|internal|pub|static|abstract|final|override|inline|open|suspend)\s+)*"
        r"(?:class|struct|enum|trait|impl|interface|type|def|fun|func(?:tion)?)\s+\w+.*$",
        re.MULTILINE,
    )
    arrow_pattern = re.compile(
        r"^(?:export\s+)?(?:const|let)\s+\w+\s*=\s*(?:async\s*)?(?:\([^)]*\)|[^=]*)\s*=>.*$",
        re.MULTILINE,
    )
    all_matches = pattern.findall(content) + arrow_pattern.findall(content)
    if not all_matches:
        return None
    return f"### Signatures in {label}\n" + "\n".join(all_matches)


@_project_tool
def extract_signatures(
    file_path: str, project_root: str | None = None, max_chars: int = 12000
) -> str:
    """Extracts structural signatures (classes, functions, methods, interfaces) with tree-sitter AST and a regex fallback. Accepts one file OR a directory (up to 200 matching files), writes a Markdown report under context-reports/, and returns the signatures inline (capped by max_chars) so the caller never has to open the report. Markdown/HTML/JSON report that no signatures exist instead of failing silently. project_root scopes resolution; max_chars caps the inline text."""
    # Master try/except: ensure extract_signatures never crashes the MCP server
    try:
        try:
            workspace_root = _explicit_project_root(project_root, "extract_signatures")
        except ValueError as e:
            return f"Error: {e}"

        # Safeguard: Append context-reports/ to the PROJECT's .gitignore.
        _ensure_context_reports_ignored(workspace_root)

        path = Path(file_path)
        if not path.is_absolute():
            path = workspace_root / file_path
        try:
            path.resolve().relative_to(workspace_root)
        except ValueError:
            return f"Error: path escapes project: {file_path}"
        if not path.exists():
            return f"Error: File not found: {file_path}"
        if path.is_dir():
            ignore = GitIgnoreFilter()
            targets = sorted(
                p
                for p in collect_files(str(path), ignore)
                if p.is_file() and p.suffix.lower() in _SIGNATURE_EXTS
            )[:200]
        else:
            targets = [path]
        if not targets:
            return (
                f"No structural signatures found in {file_path}. "
                f"Supported extensions: {', '.join(sorted(_SIGNATURE_EXTS))}."
            )

        blocks: list[str] = []
        without_signatures = 0
        for target in targets:
            try:
                label = target.resolve().relative_to(workspace_root).as_posix()
            except ValueError:
                continue
            block = _signature_block(target, label)
            if block:
                blocks.append(block)
            else:
                without_signatures += 1
        if not blocks:
            return (
                f"No structural signatures found in {file_path} "
                f"({len(targets)} file(s) scanned). Supported extensions: "
                f"{', '.join(sorted(_SIGNATURE_EXTS))}."
            )

        result_content = "\n\n".join(blocks)

        # Ensure the PROJECT's output directory exists (never the server cwd).
        report_dir = workspace_root / "context-reports"
        report_dir.mkdir(parents=True, exist_ok=True)

        # Generate timestamped filename with UUID suffix (mirrors read_source_files / create_tree_report)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        unique = uuid.uuid4().hex[:8]
        report_file = report_dir / f"signatures_report_{timestamp}_{unique}.md"

        # Write to file
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(result_content)

        try:
            cap = max(2000, min(int(max_chars), 60000))
        except (TypeError, ValueError):
            cap = 12000
        inline = result_content
        if len(inline) > cap:
            inline = (
                inline[:cap]
                + f"\n... (inline cap {cap} chars; full text in the report)"
            )
        scope = (
            f"{len(targets)} file(s), {without_signatures} without signatures"
            if path.is_dir()
            else "1 file"
        )
        return (
            f"✅ Success: Signatures extracted from `{file_path}` ({scope}).\n"
            f"📁 Generated Report: `{report_file}`\n\n"
            f"{inline}"
        )
    except Exception as e:
        return f"Error extracting signatures from {file_path}: {str(e)}"


def _explicit_project_root(project_root: str | None, tool_name: str) -> Path:
    """Validate a per-call project root (Task 279 project_path).

    Returns the resolved absolute directory. When omitted, falls back to
    the server working directory with a stderr warning (backward
    compatible single-project behavior). Raises ValueError naming the
    field for relative, missing, or non-directory input.
    """
    if project_root is None:
        root = Path.cwd().resolve()
        _FALLBACK_FIRED.set(True)
        print(
            f"Warning: {tool_name}: project_root omitted, falling back to server cwd {root}",
            file=sys.stderr,
        )
        return root
    if not isinstance(project_root, str) or not project_root:
        raise ValueError("project_root must be a non-empty absolute path string.")
    if not Path(project_root).is_absolute():
        raise ValueError(f"project_root must be absolute, got: {project_root!r}.")
    root = Path(project_root).resolve()
    if not root.is_dir():
        raise ValueError(
            f"project_root must be an existing directory, got: {project_root!r}."
        )
    return root


@_project_tool
def stage_and_inject_diff(
    task_file_path: str,
    modified_files: list[str] = [],
    project_root: str | None = None,
    skip_add: bool = False,
) -> str:
    """Stages ONLY the explicitly listed modified files plus the task file, then intelligently injects the staged diff into the task file's Git Diff block.

    F5 fix (Task 90): explicit path scoping replaces the old blind `git add -A .`,
    which swept parallel-session/foreign files into unrelated commits and required
    fragile sensitive-file reset heuristics. The OpenCode agent MUST pass every code
    file it modified via `modified_files`; if omitted or empty, only the task file is
    staged and the diff table will be empty (by design — the Brain cannot review work
    that was never explicitly listed).
    To remove foreign files from the index without touching the worktree, use
    `unstage_files` first, then re-run with `skip_add=True`.
    Whole-file staging contract: staging is ALWAYS whole-file blobs (`git add -- <files>`).
    Any pre-existing hunk-level index surgery on the listed files (e.g. `git apply
    --cached` to scope a shared file to one task) is overwritten by the worktree blob.
    When two parallel sessions share files, the session that did hunk surgery MUST pass
    `skip_add=True` and manage the index itself: the tool then skips the `git add` step
    entirely and only extracts + injects (the caller also owns staging the task file).
    On the default path the tool reports pre-existing staged state as a warning.
    """
    try:
        # 1. F5 Fix: Explicit path scoping. Stage ONLY the files OpenCode modified + the task file.
        #    This prevents cross-session contamination and keeps the diff table clean for the Brain.
        files_to_stage = modified_files + [task_file_path]
        repo = str(_repo_root(task_file_path, project_root))
        warning = ""
        if skip_add:
            # Index-safe mode (issue #29): the caller owns the index entirely
            # (including hunk-level surgery and the task file itself). Extract +
            # inject only; never touch the index.
            pass
        else:
            # Snapshot pre-existing staged state for the listed files: `git add`
            # below stages whole-file blobs and would silently overwrite any
            # hunk-level surgery a parallel session performed on shared files.
            try:
                pre_proc = subprocess.run(
                    ["git", "diff", "--cached", "--name-only", "--"] + files_to_stage,
                    capture_output=True,
                    text=True,
                    cwd=repo,
                )
                # The task file is managed by this tool itself (re-written and
                # staged on every call), so its own staged state is noise —
                # warn only about real code files.
                task_ids = {task_file_path, Path(task_file_path).name}
                try:
                    task_ids.add(
                        str(
                            Path(task_file_path)
                            .resolve()
                            .relative_to(Path(repo).resolve())
                            .as_posix()
                        )
                    )
                except ValueError:
                    pass
                pre_staged = sorted(
                    line
                    for line in pre_proc.stdout.splitlines()
                    if line.strip() and line.strip() not in task_ids
                )
            except Exception:
                pre_staged = []
            subprocess.run(
                ["git", "add", "--"] + files_to_stage,
                check=True,
                capture_output=True,
                cwd=repo,
            )
            if pre_staged:
                warning = (
                    " ⚠️ Warning: "
                    + str(len(pre_staged))
                    + " file(s) already had staged changes before this call "
                    + "(whole-file staging overwrites hunk-level index surgery): "
                    + ", ".join(pre_staged)
                    + ". If those hunks belong to another task, unstage them and "
                    + "re-run with skip_add=True after doing your own hunk staging."
                )

        # 2. Extract the diff (EXCLUDING the entire tasks/ directory to prevent recursive diff bloat)
        # Using git pathspec magic ':!tasks/' to ignore the entire task folder
        diff_cmd = ["git", "diff", "--staged", "--", ".", ":!tasks/"]
        diff_process = subprocess.run(
            diff_cmd, capture_output=True, text=True, cwd=repo
        )
        diff_text = diff_process.stdout.strip()

        if not diff_text:
            diff_text = "No code changes detected or staged."

        diff_block = f"\n```diff\n{diff_text}\n```\n"

        # 3. Read the task file
        with open(task_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 4. Smart Replacement using Regex (greedy match from first BEGIN to last END)
        # Using greedy .* to consume everything between the first BEGIN and the LAST END marker,
        # preventing corruption when injected diff content itself contains 'END_GIT_DIFF'
        pattern = re.compile(
            r"<!-- BEGIN_GIT_DIFF -->.*<!-- END_GIT_DIFF -->", re.DOTALL
        )

        if not pattern.search(content):
            return f"Error: Could not find the <!-- BEGIN_GIT_DIFF --> markers in {task_file_path}. Did you alter the template?"

        new_content = pattern.sub(
            lambda m: f"<!-- BEGIN_GIT_DIFF -->{diff_block}<!-- END_GIT_DIFF -->",
            content,
        )

        # 5. Write back to the task file
        with open(task_file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        suffix = (
            " (staging skipped: skip_add=True — index left untouched)"
            if skip_add
            else ""
        )
        return (
            f"✅ Success: Changes staged and factual diff intelligently injected into {task_file_path}.{suffix}"
            + warning
        )

    except Exception as e:
        return f"❌ Error staging or updating task file: {str(e)}"


@_project_tool
def sync_task_times(project_root: str | None = None, lane: str = "") -> str:
    """Stamp missing start/submit/finish times for tasks already sitting in a lane.

    Why this exists: the lane transitions stamp their own time, but a task can also be
    moved by hand (``git mv`` is permitted). Such a file arrives without its stamp and
    its measured duration would be silently lost. Running this after a manual move
    closes that gap without turning any move into a hook.

    The start time is recovered from git history first, then from the file's
    modification time; it is never invented as "now", because a wrong start is worse
    than a missing one. Submit and finish times have no history to recover from, so
    they are stamped at call time — which is correct, since the caller runs this
    immediately after the move.

    Idempotent: an existing stamp is never rewritten.

    Args:
        project_root: absolute project root holding tasks/.
        lane: restrict to ``in-progress`` or ``qa``; empty means both.

    Returns:
        One line per changed file, plus a summary.
    """
    workspace_root = _explicit_project_root(project_root, "sync_task_times")
    # Only the two lanes a human might move a file into by hand. Closure is not offered:
    # stamping `Finished` now on an old completed task would fabricate a duration, and
    # `commit_and_clean_task` already handles the real closure moment.
    wanted: list[tuple[str, str]] = [
        ("in-progress", "Started"),
        ("qa", "Submitted"),
    ]
    if lane:
        if lane not in {name for name, _ in wanted}:
            return "❌ lane must be in-progress or qa."
        wanted = [pair for pair in wanted if pair[0] == lane]

    changed: list[str] = []
    skipped: list[str] = []
    for lane_name, field in wanted:
        lane_dir = workspace_root / "tasks" / lane_name
        if not lane_dir.is_dir():
            continue
        for path in sorted(lane_dir.glob("*.md")):
            content = path.read_text(encoding="utf-8", errors="ignore")
            if re.search(rf"^\*\*{field}:\*\*", content, re.MULTILINE):
                continue
            value = None
            source = "now"
            if field == "Started":
                value = task_start_stamp(workspace_root, path)
                source = "git/mtime"
                if value is None:
                    # Never invent a start: a fabricated "now" would report an
                    # instant task for work that may have taken days.
                    skipped.append(f"{path.name} (no git history or mtime)")
                    continue
            if stamp_task_header(path, field, value):
                changed.append(f"- {path.name}: **{field}:** ({source})")
            else:
                skipped.append(path.name)
    head = f"Stamped {len(changed)} task(s)."
    body = "\n".join(changed) if changed else "Nothing to stamp."
    tail = f"\nNo usable time for: {', '.join(skipped)}" if skipped else ""
    return f"{head}\n{body}{tail}"


@_project_tool
def unstage_files(files: list[str], project_root: str | None = None) -> str:
    """Removes the listed files from the Git index WITHOUT touching the worktree.

    Parallel-session isolation primitive: when a staged diff contains foreign
    hunks (another task's work in a shared file), call this with exactly those
    files, redo hunk-level surgery (`git apply --cached`), then call
    `stage_and_inject_diff` with `skip_add=True` so the index is never
    overwritten again. Uses `git reset -q -- <files>` (mixed reset of the
    listed paths only — worktree bytes are never modified, nothing is
    committed, nothing is pushed; works with or without a HEAD commit).
    ZAC holds:
    this tool cannot commit, check out, or push by construction.
    An empty file list is rejected (nothing to do is a caller bug, not success).
    """
    try:
        if not files:
            return "❌ Error: files must be a non-empty list of repo-relative or absolute paths."
        # Defense in depth: reject flag-looking arguments outright. The `--`
        # separator below already neutralizes them, but a hallucinating caller
        # must get a loud error instead of relying on git's parsing.
        flagged = [f for f in files if f.startswith("-")]
        if flagged:
            return (
                "❌ Error: refusing flag-like paths (possible flag injection): "
                + ", ".join(flagged)
                + ". Pass plain file paths only."
            )
        repo = str(_repo_root(files[0], project_root))
        proc = subprocess.run(
            ["git", "reset", "-q", "--"] + files,
            capture_output=True,
            text=True,
            cwd=repo,
        )
        if proc.returncode != 0:
            return f"❌ Error unstaging {files}: {proc.stderr.strip() or proc.stdout.strip()}"
        remaining_proc = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            cwd=repo,
        )
        remaining = sorted(
            line for line in remaining_proc.stdout.splitlines() if line.strip()
        )
        remaining_txt = (
            " Still staged: " + ", ".join(remaining) + "."
            if remaining
            else " Index is now clean."
        )
        return (
            f"✅ Success: unstaged {len(files)} file(s) (worktree untouched)."
            + remaining_txt
        )
    except Exception as e:
        return f"❌ Error unstaging files: {str(e)}"


@_project_tool
def qa_transition(
    task_file_path: str, modified_files: list[str] = [], project_root: str | None = None
) -> str:
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
        workspace_root = _repo_root(task_file_path, project_root)
        src = Path(task_file_path)
        src = src if src.is_absolute() else workspace_root / src

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
            return (
                f"❌ Error: task file must be a Markdown file (*.md), got: {task_name}"
            )

        dest = workspace_root / "tasks" / "qa" / task_name
        expected_header = f"tasks/qa/{task_name}"
        dest.parent.mkdir(parents=True, exist_ok=True)

        # 2. Move task file to tasks/qa/ via git mv (fallback to shutil.move + git add)
        try:
            result = subprocess.run(
                ["git", "mv", str(src_resolved), str(dest)],
                capture_output=True,
                text=True,
                cwd=str(workspace_root),
            )
            if result.returncode != 0:
                raise RuntimeError(
                    result.stderr.strip() or result.stdout.strip() or "git mv failed"
                )
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
                subprocess.run(
                    ["git", "add", "--", str(dest)],
                    check=True,
                    capture_output=True,
                    cwd=str(workspace_root),
                )
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
        new_content_header = header_pattern.sub(
            f"**File:** `{expected_header}`", content, count=1
        )
        try:
            dest.write_text(new_content_header, encoding="utf-8")
            # Measured QA entry time: written once, so a re-transition never rewrites it.
            # A hand-moved file may arrive without a start; recover it first so the
            # QA wait is measured rather than null.
            if not re.search(r"^\s*\*\*Started:\*\*", new_content_header, re.MULTILINE):
                recovered = backfill_started_from_git(workspace_root, dest)
                if recovered:
                    stamp_task_header(dest, "Started", recovered)
            stamp_task_header(dest, "Submitted")
        except Exception as e:
            return f"❌ Error writing header update to {dest}: {e}"

        # 4. Stages modified_files + destination task file (explicit staging)
        files_to_stage = list(modified_files) + [str(dest)]
        try:
            subprocess.run(
                ["git", "add", "--"] + files_to_stage,
                check=True,
                capture_output=True,
                cwd=str(workspace_root),
            )
        except subprocess.CalledProcessError as e:
            return f"❌ Error staging files {files_to_stage}: {e.stderr.decode() if hasattr(e.stderr, 'decode') else e.stderr}"

        # 5. Extracts staged diff excluding tasks/ (:!tasks/)
        try:
            diff_proc = subprocess.run(
                ["git", "diff", "--staged", "--", ".", ":!tasks/"],
                capture_output=True,
                text=True,
                cwd=str(workspace_root),
            )
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
        diff_pattern = re.compile(
            r"<!-- BEGIN_GIT_DIFF -->.*<!-- END_GIT_DIFF -->", re.DOTALL
        )
        if not diff_pattern.search(content_after_header):
            return f"❌ Error: Could not find <!-- BEGIN_GIT_DIFF --> markers in {dest}"
        new_content_final = diff_pattern.sub(
            lambda m: f"<!-- BEGIN_GIT_DIFF -->{diff_block}<!-- END_GIT_DIFF -->",
            content_after_header,
        )
        try:
            dest.write_text(new_content_final, encoding="utf-8")
        except Exception as e:
            return f"❌ Error writing diff injection to {dest}: {e}"
        # Re-stage the task file after injection so final QA state is staged (header + diff)
        try:
            subprocess.run(
                ["git", "add", "--", str(dest)],
                check=True,
                capture_output=True,
                cwd=str(workspace_root),
            )
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

        files_str = (
            ", ".join(modified_files)
            if modified_files
            else "(no code files — diff will be sentinel)"
        )
        return (
            f"✅ QA transition complete: {task_file_path} → {expected_header}\n"
            f"   Staged files: {files_str}\n"
            f"   Header synced and diff injected into {expected_header}"
        )

    except Exception as e:
        return f"❌ Unexpected error in qa_transition: {str(e)}"


@_project_tool
def commit_and_clean_task(
    task_file_path: str, commit_message: str, project_root: str | None = None
) -> str:
    """Commits staged changes, captures the feature commit hash, replaces the raw diff in the task file with the hash reference, and commits the cleaned task file as a separate closure commit. The stored hash always points to the feature commit, which stays reachable forever (no amend, no orphaned commits)."""
    try:
        # 0. Idempotency guard: skip if the task file was already cleaned.
        #    Placed first so a cleaned task file short-circuits even on a clean tree.
        #    Must match the EXACT cleaned-block structure, not a bare substring:
        #    a raw injected diff can itself mention 'Stored in Commit Hash' (e.g.
        #    the diff of this very guard or its CHANGELOG entry), causing a false
        #    positive that blocks legitimate closures.
        path = Path(task_file_path)
        repo = str(_repo_root(task_file_path, project_root))
        if not path.is_absolute():
            path = Path(repo) / path
        if path.is_file():
            # Closure time: stamped once, so the measured duration is start → close.
            # A file that skipped claim_next (hand-moved) has no start; recover it from
            # git so the duration is measured rather than silently lost.
            if not re.search(
                r"^\s*\*\*Started:\*\*", path.read_text(encoding="utf-8"), re.MULTILINE
            ):
                recovered = backfill_started_from_git(Path(repo), path)
                if recovered:
                    stamp_task_header(path, "Started", recovered)
            stamp_task_header(path, "Finished")
            with open(path, "r", encoding="utf-8") as f:
                existing = f.read()
            cleaned_block = re.compile(
                r"<!-- BEGIN_GIT_DIFF -->\s*\*\*Factual Git Diff:\*\* Stored in Commit Hash: `[0-9a-f]{7,40}`\s*<!-- END_GIT_DIFF -->",
                re.DOTALL,
            )
            if cleaned_block.search(existing):
                return "⚠️ Task file already cleaned (Stored in Commit Hash present). Nothing to commit."

        # 0.25 Conventional Commits gate (Task 211): reject free-form feature
        # messages before touching git. The closure commit below is templated
        # and always conforms, so only the caller-supplied message is checked.
        conventional_error = _check_conventional_commit(commit_message)
        if conventional_error:
            return conventional_error

        # 0.5 Safety check before commit
        staged_check = subprocess.run(
            ["git", "diff", "--staged", "--quiet"], capture_output=True, cwd=repo
        )
        if staged_check.returncode == 0:
            return "⚠️ No staged changes to commit."

        # 1. Commit staged changes (feature commit H1)
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            check=True,
            capture_output=True,
            text=True,
            cwd=repo,
        )

        # 2. Capture H1 — the feature commit hash. It stays reachable forever
        #    as the parent of the closure commit (step 5). NEVER amend it.
        hash_proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            cwd=repo,
        )
        commit_hash = hash_proc.stdout.strip()

        # 3. Read task file and replace raw diff with the hash reference
        if path.is_file():
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            pattern = re.compile(
                r"<!-- BEGIN_GIT_DIFF -->.*<!-- END_GIT_DIFF -->", re.DOTALL
            )
            if pattern.search(content):
                clean_block = f"<!-- BEGIN_GIT_DIFF -->\n**Factual Git Diff:** Stored in Commit Hash: `{commit_hash}`\n<!-- END_GIT_DIFF -->"
                new_content = pattern.sub(clean_block, content)

                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)

        # 4. Stage the cleaned task file ONLY (F5 fix: never `git add -A tasks/`,
        #    which swept foreign/parallel-session task files into this commit).
        subprocess.run(
            ["git", "add", "--", task_file_path],
            check=True,
            capture_output=True,
            cwd=repo,
        )

        # 5. Commit the cleaned task file as a separate closure commit.
        #    A plain commit (NOT --amend) keeps H1 reachable from HEAD.
        slug = _derive_task_slug(task_file_path)
        staged_after = subprocess.run(
            ["git", "diff", "--staged", "--quiet"], capture_output=True
        )
        if staged_after.returncode != 0:
            subprocess.run(
                ["git", "commit", "-m", f"chore: close {slug}"],
                check=True,
                capture_output=True,
                text=True,
                cwd=repo,
            )

        return f"✅ Success: Code committed (Hash: `{commit_hash}`). Task file {task_file_path} cleaned; closure commit `chore: close {slug}` created on top."
    except subprocess.CalledProcessError as e:
        return f"❌ Git Error: {e.stderr}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


# --- bundle_tasks helpers (module-level so tests can import them directly;
# the bundle_tasks MCP tool below calls these globals; logic is verbatim from
# the retired scripts/bundle-tasks.py, self-contained since Task 110/155) ---


@_project_tool
def bundle_tasks(
    task_ids: list[str],
    title: str,
    dry_run: bool = False,
    force: bool = False,
    project_root: str | None = None,
) -> str:
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
    # Bundle helpers/constants live at module level (importable by tests).
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
        if len(deduped) != len(cleaned_ids):
            dupes = sorted(
                {t for t in cleaned_ids if cleaned_ids.count(t) > 1},
                key=lambda t: int(t),
            )
            return f"❌ Duplicate task IDs in request: {dupes}. Each ID may appear only once."
        task_ids = deduped
        if len(task_ids) < 2:
            return f"❌ Bundle needs 2-6 tasks, got {len(task_ids)}. Provide 2-6 numeric task IDs."
        if not title or not title.strip():
            return "❌ Error: title is required (e.g., 'android-polish-bundle')."
        title = title.strip()
        if len(task_ids) > MAX_BUNDLE_SIZE and not force:
            return f"❌ Guardrail: Bundle size {len(task_ids)} exceeds MAX_BUNDLE_SIZE={MAX_BUNDLE_SIZE}. Use --force to override, or split into two METAs. IDs: {task_ids}"
        if len(task_ids) > MAX_BUNDLE_SIZE and force:
            # Warn but continue — caller will see warning in final output
            pass

        # --- Resolve sources (active Kanban only) ---
        # CWD fix: tasks_root anchors at explicit project_root, else CWD.
        base = Path(project_root).resolve() if project_root else Path.cwd()
        tasks_root = base / "tasks"
        source_data: list[tuple[str, Path, str, str]] = []
        missing: list[str] = []
        for tid in task_ids:
            state, payload = _locate_task_file(tid, tasks_root)
            if state == "ok":
                p = payload
                try:
                    c = p.read_text(encoding="utf-8")
                except Exception as e:
                    return f"❌ Could not read {p} for task {tid}: {e}"
                t = _extract_title(c)
                source_data.append((tid, p, c, t))
            elif state == "duplicate":
                names = sorted(x.name for x in payload)
                return f"❌ Duplicate task ID {tid} in active Kanban dirs: {names}. Resolve the duplication first — refusing to guess."
            elif state == "archived":
                missing.append(f"{tid} (already archived — see tasks/archive/)")
            else:
                missing.append(tid)
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
        clashes = _next_id_collision(tasks_root, next_id)
        if clashes:
            names = sorted(p.name for p in clashes)
            return f"❌ Task ID collision: same-ID file(s) exist for next ID {next_id}: {names}. Re-run ID discovery."

        meta_title_full = title
        meta_content = _build_meta_content(
            next_id, meta_slug, meta_title_full, task_ids, source_data
        )
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
            lines.append(
                f"🔍 Dry-run (MCP): Would create META task {next_id}-{meta_slug}"
            )
            lines.append(f"   Output: {output_path}")
            lines.append(f"   Bundles: {task_ids} ({len(task_ids)} tasks)")
            lines.append(f"   Sources:")
            for sid, p, _, t in source_data:
                lines.append(f"     - {sid}: {t} ({p})")
            lines.append(
                f"   Combined LOC: {total_loc} {'⚠️ >400' if total_loc > 400 else '✅'}"
            )
            lines.append(f"   Supersedes will be: {task_ids}")
            lines.append(f"   Archive destinations:")
            for sid, p, _, _ in source_data:
                lines.append(f"     - {p} -> tasks/archive/{p.name}")
            lines.append(f"\n   META content preview (first 40 lines):")
            for i, line in enumerate(meta_content.splitlines()[:40], 1):
                lines.append(f"   {i:3d}| {line}")
            lines.append(f"\n   ... {len(meta_content.splitlines()) - 40} more lines")
            required = [
                "## Goal",
                "## Supersedes",
                "## Bundled Checklist",
                "## Local TODOs",
                "## Acceptance Criteria",
                "## Verification Evidence",
                "## Risk & Rollback",
                "## Factual Git Diff",
                "## Execution Log",
            ]
            missing_sections = [s for s in required if s not in meta_content]
            if missing_sections:
                lines.append(
                    f"⚠️ Missing required sections in preview: {missing_sections}"
                )
                return "\n".join(lines)
            lines.append(f"\n✅ Dry-run lint check: All required sections present.")
            if len(task_ids) > 6 and force:
                lines.insert(
                    0,
                    f"⚠️ --force: Bundling {len(task_ids)} tasks (> 6). Mega-diff risk.",
                )
            return "\n".join(lines)

        # --- B1+B3: Atomic create with retry; content rebuilt after final ID ---
        # The META body embeds its own ID (title, headers, rollback note), so
        # a retry that allocates a NEW id must rebuild the body — writing the
        # pre-race body would leave a stale-ID file. Create + write happen in
        # one exclusive open so a crash cannot leave an empty META file.
        MAX_ID_RETRIES = 5
        meta_live = meta_content
        for attempt in range(MAX_ID_RETRIES):
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "x", encoding="utf-8") as f:
                    f.write(meta_live)
                break
            except FileExistsError:
                # Re-discover next ID (a racer may have landed first)
                next_id = _discover_next_id(tasks_root)
                meta_id_str = f"{next_id:02d}" if next_id < 100 else str(next_id)
                meta_slug = _kebab_case(title)
                meta_filename = f"{meta_id_str}-{meta_slug}.md"
                output_path = tasks_root / "backlog" / meta_filename
                if _next_id_collision(tasks_root, next_id):
                    continue
                meta_live = _build_meta_content(
                    next_id, meta_slug, meta_title_full, task_ids, source_data
                )
                continue
            except OSError as e:
                output_path.unlink(missing_ok=True)
                return f"❌ Failed to write META file {output_path}: {e}"
        else:
            return f"❌ Failed to find unique ID after {MAX_ID_RETRIES} attempts. Another process may be bundling concurrently."

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
            # B6: Transactional rollback — restore byte-identical originals.
            # source_data already carries each source's original bytes, so the
            # restore rewrites them verbatim (File header + status included):
            # no header guessing, no hardcoded backlog origin. Moves go through
            # _git_mv_or_fallback (repo-rooted cwd + untracked fallback);
            # every restore failure is surfaced, never swallowed.
            restore_errors: list[str] = []
            for archived_path in archived:
                original_name = archived_path.name
                match = next(
                    (
                        (src, text)
                        for _, src, text, _ in source_data
                        if src.name == original_name
                    ),
                    None,
                )
                if match is None:
                    restore_errors.append(
                        f"{original_name}: origin unknown, left in tasks/archive/"
                    )
                    continue
                src_path, original_text = match
                if not _git_mv_or_fallback(archived_path, src_path):
                    restore_errors.append(
                        f"{original_name}: move back to {src_path} failed"
                    )
                    continue
                try:
                    src_path.write_text(original_text, encoding="utf-8")
                except Exception as e:
                    restore_errors.append(
                        f"{original_name}: content restore failed: {e}"
                    )
            output_path.unlink(missing_ok=True)
            detail = f" (restore issues: {restore_errors})" if restore_errors else ""
            return f"❌ Bundle aborted. Archive failed for {failed}. All changes rolled back.{detail} Fix and retry."
        else:
            out_lines.append(
                f"✅ Archived {len(archived)} source tasks to tasks/archive/ with superseded-by: {meta_id_str}-{meta_slug}"
            )
        # Light validation
        try:
            cc = output_path.read_text(encoding="utf-8")
            for req in ["## Goal", "## Local TODOs", "## Acceptance Criteria"]:
                if req not in cc:
                    out_lines.append(f"⚠️ Lint warning: {req} missing in created META.")
        except Exception:
            pass
        out_lines.append(
            f"\nDone. Next: move {output_path} through Kanban (backlog → in-progress → qa → completed) as a single Hands implementation."
        )
        out_lines.append(
            f"Traceability: git log --oneline --follow -- tasks/archive/<id>-*.md | head"
        )
        if len(task_ids) > 6 and force:
            out_lines.insert(
                0, f"⚠️ --force: Bundling {len(task_ids)} tasks (> 6). Mega-diff risk."
            )
        return "\n".join(out_lines)

    except Exception as e:
        return f"❌ Error in bundle_tasks MCP (self-contained): {str(e)}"


if __name__ == "__main__":
    _transport = os.environ.get("MCP_TRANSPORT", "streamable-http")
    # Singleton default (Task 279 V3): all callers consume these servers as
    # remote http singletons, so an unset MCP_TRANSPORT must not silently
    # drop into stdio while the unit reports active. Explicit "stdio"
    # still works for local debugging.
    mcp.run(transport=_transport)
