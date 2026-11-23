"""Regression test: MCP tool output addresses the calling agent, not a human.

Sibling Docs: mcp-context-server/README.md | Decisions: mcp-context-server/DECISIONS.md

Contract under test: the success text returned by `read_source_files` and
`create_tree_report` is consumed by autonomous agents that read files with their
own tools. The text therefore points the agent at the generated report and never
carries the retired human-facing prefix or the copy/paste-for-the-AI instruction.

Design notes:
- Source-level assertions only. Importing `server.py` would pull the FastMCP
  runtime and its dependency set, which the test environment does not install.
- The repository root is discovered by walking up from this file, so the test
  works from any working directory.
- This file lives outside `mcp-*`, so its own sentinel literals are not scanned
  by the repo-wide check below.
"""

import ast
from pathlib import Path

# Retired human-facing wording that must vanish from every MCP server source.
BANNED_SENTINELS = (
    "Manager: You can now open",
    "copy/paste it directly for the AI",
)

# Agent-addressed pointer sentence expected inside each report tool function.
EXPECTED_POINTERS = {
    "read_source_files": "Context report written to",
    "create_tree_report": "Tree report written to",
}

# Directory name that identifies the repository root.
ROOT_MARKER = "mcp-context-server"


def _repo_root():
    """Return the repository root by walking up until the marker directory exists."""
    for parent in Path(__file__).resolve().parents:
        if (parent / ROOT_MARKER).is_dir():
            return parent
    raise AssertionError("repository root not found")


def _mcp_sources(root):
    """Yield every Python file that belongs to an MCP server directory."""
    for server_dir in sorted(root.glob("mcp-*")):
        if not server_dir.is_dir():
            continue
        yield from sorted(server_dir.rglob("*.py"))


def _function_source(source, function_name):
    """Return the exact source segment of a top-level function, or fail loudly."""
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            segment = ast.get_source_segment(source, node)
            if segment is None:
                raise AssertionError(function_name + ": source segment unavailable")
            return segment
    raise AssertionError(function_name + ": definition not found")


def test_no_human_addressed_sentinels_in_mcp_sources():
    """No MCP server source may keep the retired human-facing wording."""
    root = _repo_root()
    offenders = []
    for path in _mcp_sources(root):
        text = path.read_text(encoding="utf-8")
        for sentinel in BANNED_SENTINELS:
            if sentinel in text:
                offenders.append(str(path.relative_to(root)) + " -> " + sentinel)
    if offenders:
        details = "; ".join(offenders)
        raise AssertionError("retired sentinel survived in: " + details)


def test_context_tool_outputs_are_agent_addressed():
    """Both report tools point the agent at the report and keep no human wording."""
    root = _repo_root()
    source = (root / ROOT_MARKER / "server.py").read_text(encoding="utf-8")
    for function_name, pointer in EXPECTED_POINTERS.items():
        segment = _function_source(source, function_name)
        for sentinel in BANNED_SENTINELS:
            if sentinel in segment:
                raise AssertionError(function_name + " still returns " + sentinel)
        if pointer not in segment:
            raise AssertionError(function_name + " is missing " + pointer)
