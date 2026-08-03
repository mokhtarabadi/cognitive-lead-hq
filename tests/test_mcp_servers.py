"""Basic MCP server startup and logic validation tests.

Verifies that all three MCP servers can be imported and initialized,
and that the lint server's task file structure checker works correctly.
"""

import sys
from pathlib import Path

# Add server directories to path for import testing
# Note: Each server.py defines its own `mcp` variable, so we must import
# them in isolated namespaces to avoid conflicts.
sys.path.insert(0, str(Path(__file__).parent.parent / "mcp-context-server"))
sys.path.insert(0, str(Path(__file__).parent.parent / "mcp-memory-server"))
sys.path.insert(0, str(Path(__file__).parent.parent / "mcp-lint-server"))


def test_context_server_import():
    """Verify the context server can be imported and exposes the MCP app."""
    import importlib
    import types

    server_path = Path(__file__).parent.parent / "mcp-context-server" / "server.py"
    spec = importlib.util.spec_from_file_location("context_server", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    assert hasattr(mod, "mcp"), "Context server missing 'mcp' attribute"
    assert mod.mcp.name == "CustomContext", (
        f"Expected mcp.name='CustomContext', got '{mod.mcp.name}'"
    )


def test_memory_server_import():
    """Verify the memory server can be imported and exposes the MCP app."""
    import importlib

    server_path = Path(__file__).parent.parent / "mcp-memory-server" / "server.py"
    spec = importlib.util.spec_from_file_location("memory_server", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    assert hasattr(mod, "mcp"), "Memory server missing 'mcp' attribute"
    assert mod.mcp.name == "ProjectMemory", (
        f"Expected mcp.name='ProjectMemory', got '{mod.mcp.name}'"
    )


def test_lint_server_import():
    """Verify the lint server can be imported and exposes the MCP app."""
    import importlib

    server_path = Path(__file__).parent.parent / "mcp-lint-server" / "server.py"
    spec = importlib.util.spec_from_file_location("lint_server", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    assert hasattr(mod, "mcp"), "Lint server missing 'mcp' attribute"
    assert mod.mcp.name == "LintServer", (
        f"Expected mcp.name='LintServer', got '{mod.mcp.name}'"
    )


def test_lint_task_file_logic():
    """Verify the lint server's task structure checker validates correct files."""
    import importlib

    server_path = Path(__file__).parent.parent / "mcp-lint-server" / "server.py"
    spec = importlib.util.spec_from_file_location("lint_server", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Test with a dummy valid structure
    valid_content = """# Task 99: Test

**File:** `tasks/backlog/99-test.md`
**Source:** orchestrator
**Type:** improvement
**Status:** open

## Goal

Test

## Local TODOs

- [x] Test

## Acceptance Criteria

- [x] Test

## Verification Evidence

Test

## Risk & Rollback

Test

## OpenCode Execution Log & Reasoning

Test

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
"""
    issues = mod._check_task_file_structure(valid_content, "99-test.md")
    assert len(issues) == 0, f"Expected no issues, got: {issues}"


def test_lint_task_file_missing_sections():
    """Verify the lint server catches missing required sections."""
    import importlib

    server_path = Path(__file__).parent.parent / "mcp-lint-server" / "server.py"
    spec = importlib.util.spec_from_file_location("lint_server", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Test with a file missing Acceptance Criteria
    incomplete_content = """# Task 99: Test

**File:** `tasks/backlog/99-test.md`
**Source:** orchestrator
**Type:** improvement
**Status:** open

## Goal

Test

## Local TODOs

- [x] Test

## OpenCode Execution Log & Reasoning

Test

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
"""
    issues = mod._check_task_file_structure(incomplete_content, "99-test.md")
    assert len(issues) > 0, "Expected issues for missing sections, got none"
    # Should flag missing Acceptance Criteria, Verification Evidence, Risk & Rollback
    assert any("Acceptance Criteria" in i for i in issues), (
        "Missing section detection for Acceptance Criteria"
    )
