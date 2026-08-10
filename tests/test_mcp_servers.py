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


def test_commit_and_clean_task_stores_reachable_hash():
    """Verify commit_and_clean_task stores a reachable commit hash (no orphaned pre-amend hash).

    Regression test: the tool previously captured HEAD before `git commit --amend`,
    so the hash written into the task file pointed to a commit that became
    unreachable after the amend replaced it.
    """
    import importlib
    import os
    import subprocess
    import tempfile

    server_path = Path(__file__).parent.parent / "mcp-context-server" / "server.py"
    spec = importlib.util.spec_from_file_location("context_server_cc", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    with tempfile.TemporaryDirectory() as repo_dir:
        repo = Path(repo_dir)

        # Set up a git repo with a known identity
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)

        # Code change + task file with diff markers
        (repo / "feature.py").write_text("x = 1\n")
        task_file = repo / "tasks" / "completed" / "78-fix-bug.md"
        task_file.parent.mkdir(parents=True)
        task_file.write_text(
            "# Task 78: Fix bug\n\n## Factual Git Diff\n\n"
            "<!-- BEGIN_GIT_DIFF -->\n```diff\n+feature\n```\n<!-- END_GIT_DIFF -->\n"
        )
        subprocess.run(["git", "add", "-A"], cwd=repo, check=True)

        old_cwd = os.getcwd()
        os.chdir(repo)
        try:
            result = mod.commit_and_clean_task(str(task_file), "fix: repair bug")
        finally:
            os.chdir(old_cwd)
        assert "✅ Success" in result, result

        # Task file must reference a commit hash
        cleaned = task_file.read_text()
        assert "Stored in Commit Hash:" in cleaned, "Task file should reference the commit hash"
        stored_hash = None
        for line in cleaned.splitlines():
            if "Stored in Commit Hash:" in line and "`" in line:
                stored_hash = line.split("`")[1]
        assert stored_hash, "Could not parse stored commit hash"

        # Closure commit sits on top; stored hash must still be reachable
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True
        ).stdout.strip()
        assert stored_hash != head, "Closure commit should sit on top of the feature commit"
        ancestry = subprocess.run(
            ["git", "merge-base", "--is-ancestor", stored_hash, "HEAD"],
            cwd=repo, capture_output=True,
        )
        assert ancestry.returncode == 0, f"Stored hash {stored_hash} is orphaned/unreachable"

        # No amend commits in history
        log = subprocess.run(
            ["git", "log", "--oneline", "-3"], cwd=repo, capture_output=True, text=True
        ).stdout
        assert "amend" not in log, f"History must not contain amend commits:\n{log}"

        # git show <stored_hash> still returns the feature diff
        shown = subprocess.run(
            ["git", "show", stored_hash, "--stat"], cwd=repo, capture_output=True, text=True
        ).stdout
        assert "feature.py" in shown, "git show <stored_hash> should return the code diff"

        # Idempotency: second call must not create more commits
        before = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True
        ).stdout.strip()
        old_cwd = os.getcwd()
        os.chdir(repo)
        try:
            second = mod.commit_and_clean_task(str(task_file), "fix: repair bug")
        finally:
            os.chdir(old_cwd)
        assert "already cleaned" in second, second
        after = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True
        ).stdout.strip()
        assert before == after, "Idempotency guard should prevent double commits"


def test_commit_and_clean_task_guard_no_false_positive_on_diff_mention():
    """The idempotency guard must NOT trigger when the raw diff merely mentions 'Stored in Commit Hash:'.

    Regression test: a naive substring check matched the guard's own source line
    (`if "Stored in Commit Hash:" in existing:`) once that diff was injected into
    the task file, blocking the closure. The guard must only match the exact
    cleaned-block structure between the BEGIN/END markers.
    """
    import importlib
    import os
    import subprocess
    import tempfile

    server_path = Path(__file__).parent.parent / "mcp-context-server" / "server.py"
    spec = importlib.util.spec_from_file_location("context_server_fp", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    with tempfile.TemporaryDirectory() as repo_dir:
        repo = Path(repo_dir)
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)

        (repo / "feature.py").write_text("x = 1\n")
        # Raw diff that itself contains the guard's phrase AND the exact
        # clean-block f-string literal (but with {commit_hash}, not a real hash)
        raw_diff = (
            "```diff\n"
            "+            if \"Stored in Commit Hash:\" in existing:\n"
            "+**Factual Git Diff:** Stored in Commit Hash: `{commit_hash}`\n"
            "```\n"
        )
        task_file = repo / "tasks" / "79-fp-guard.md"
        task_file.parent.mkdir()
        task_file.write_text(
            "# Task 79: Guard FP\n\n## Factual Git Diff\n\n"
            "<!-- BEGIN_GIT_DIFF -->\n" + raw_diff + "<!-- END_GIT_DIFF -->\n"
        )
        subprocess.run(["git", "add", "-A"], cwd=repo, check=True)

        old_cwd = os.getcwd()
        os.chdir(repo)
        try:
            result = mod.commit_and_clean_task(str(task_file), "fix: guard fp")
        finally:
            os.chdir(old_cwd)
        assert "✅ Success" in result, result
        assert "already cleaned" not in result, "Guard must not false-positive on raw diff mentions"

        # The stored hash must reference the committed code (reachable, not orphaned)
        cleaned = task_file.read_text()
        stored_hash = None
        for line in cleaned.splitlines():
            if "Stored in Commit Hash:" in line and "`" in line:
                stored_hash = line.split("`")[1]
        assert stored_hash, "Could not parse stored commit hash"
        ancestry = subprocess.run(
            ["git", "merge-base", "--is-ancestor", stored_hash, "HEAD"],
            cwd=repo, capture_output=True,
        )
        assert ancestry.returncode == 0, f"Stored hash {stored_hash} is orphaned/unreachable"


def test_create_tree_report_saves_md_in_context_reports():
    """Verify create_tree_report saves a tree_report_*.md file that respects .gitignore."""
    import importlib
    import os
    import tempfile

    server_path = Path(__file__).parent.parent / "mcp-context-server" / "server.py"
    spec = importlib.util.spec_from_file_location("context_server_tree", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    with tempfile.TemporaryDirectory() as repo_dir:
        repo = Path(repo_dir)
        (repo / "src").mkdir()
        (repo / "src" / "app.py").write_text("x = 1\n")
        (repo / "README.md").write_text("# README\n")
        (repo / "node_modules").mkdir()
        (repo / "node_modules" / "dep.js").write_text("y = 2\n")
        (repo / ".gitignore").write_text("node_modules/\n")

        old_cwd = os.getcwd()
        os.chdir(repo)
        try:
            result = mod.create_tree_report(str(repo))
            # Assertions run while cwd still points at the temp repo so the
            # relative report path returned by the tool resolves correctly.
            assert "✅ Success" in result, result
            report_file = None
            for line in result.splitlines():
                if "Generated Report:" in line and "`" in line:
                    report_file = line.split("`")[1]
            assert report_file, "Could not parse report path"
            assert "tree_report_" in Path(report_file).name, report_file
            assert Path(report_file).is_file(), report_file

            content = Path(report_file).read_text()
            assert "app.py" in content, "Tracked file should appear in the tree"
            assert "README.md" in content, "Tracked file should appear in the tree"
            assert "node_modules" not in content, "Ignored entries must be excluded"

            # .gitignore safeguard: context-reports/ appended by the tool
            gitignore_text = (repo / ".gitignore").read_text()
            assert "context-reports/" in gitignore_text, "Tool must safeguard context-reports/ in .gitignore"
        finally:
            os.chdir(old_cwd)


def test_create_tree_report_default_target_is_cwd():
    """Verify create_tree_report with no arguments trees the entire project (cwd)."""
    import importlib
    import os
    import tempfile

    server_path = Path(__file__).parent.parent / "mcp-context-server" / "server.py"
    spec = importlib.util.spec_from_file_location("context_server_tree_default", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    with tempfile.TemporaryDirectory() as repo_dir:
        repo = Path(repo_dir)
        (repo / "package").mkdir()
        (repo / "package" / "main.py").write_text("print('hi')\n")

        old_cwd = os.getcwd()
        os.chdir(repo)
        try:
            result = mod.create_tree_report()  # no target_path -> whole project
            assert "✅ Success" in result, result
            report_file = None
            for line in result.splitlines():
                if "Generated Report:" in line and "`" in line:
                    report_file = line.split("`")[1]
            assert report_file, "Could not parse report path"
            assert "tree_report_" in Path(report_file).name, report_file
            content = Path(report_file).read_text()
            assert "main.py" in content, "Project files should appear in the default whole-project tree"
        finally:
            os.chdir(old_cwd)


def test_create_tree_report_rapid_calls_do_not_overwrite():
    """Verify two quick calls in the same second produce distinct report files.

    Regression test: both calls previously wrote to tree_report_<same-ts>.md,
    silently overwriting the first tree with the second.
    """
    import importlib
    import os
    import tempfile

    server_path = Path(__file__).parent.parent / "mcp-context-server" / "server.py"
    spec = importlib.util.spec_from_file_location("context_server_tree_rapid", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    with tempfile.TemporaryDirectory() as repo_dir:
        repo = Path(repo_dir)
        (repo / "a.txt").write_text("a\n")
        (repo / "b.txt").write_text("b\n")

        old_cwd = os.getcwd()
        os.chdir(repo)
        try:
            first = mod.create_tree_report(str(repo))
            second = mod.create_tree_report(str(repo))
            assert "✅ Success" in first and "✅ Success" in second

            reports = sorted((repo / "context-reports").glob("tree_report_*.md"))
            assert len(reports) >= 2, f"Expected 2 distinct reports, got {len(reports)}: {reports}"
            assert reports[0].is_file() and reports[1].is_file()
        finally:
            os.chdir(old_cwd)


def test_create_tree_report_invalid_path():
    """Verify create_tree_report rejects non-directory targets gracefully."""
    import importlib
    import os
    import tempfile

    server_path = Path(__file__).parent.parent / "mcp-context-server" / "server.py"
    spec = importlib.util.spec_from_file_location("context_server_tree_invalid", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    with tempfile.TemporaryDirectory() as repo_dir:
        repo = Path(repo_dir)
        (repo / "somefile.txt").write_text("x\n")

        old_cwd = os.getcwd()
        os.chdir(repo)
        try:
            result = mod.create_tree_report(str(repo / "somefile.txt"))
            assert "Error" in result and "not a valid directory" in result, result
        finally:
            os.chdir(old_cwd)


def test_create_tree_report_rejects_path_traversal():
    """Verify create_tree_report rejects absolute paths outside the workspace.

    Regression test: the tool previously accepted any directory (e.g. /tmp),
    walking filesystem paths outside the project the server runs in.
    """
    import importlib
    import os
    import tempfile

    server_path = Path(__file__).parent.parent / "mcp-context-server" / "server.py"
    spec = importlib.util.spec_from_file_location("context_server_tree_traversal", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    with tempfile.TemporaryDirectory() as repo_dir:
        repo = Path(repo_dir)

        old_cwd = os.getcwd()
        os.chdir(repo)
        try:
            # The temp repo's parent (system temp dir) is outside the workspace.
            outside_path = str(repo.parent)
            result = mod.create_tree_report(outside_path)
            assert "Path traversal detected" in result, result
            assert "within the project workspace" in result, result
        finally:
            os.chdir(old_cwd)


def test_create_tree_report_handles_none_input():
    """Verify create_tree_report(None) degrades gracefully to the whole project.

    Regression test: a malformed tool invocation must not raise; it falls back
    to the default '.' (workspace root) target.
    """
    import importlib
    import os
    import tempfile

    server_path = Path(__file__).parent.parent / "mcp-context-server" / "server.py"
    spec = importlib.util.spec_from_file_location("context_server_tree_none", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    with tempfile.TemporaryDirectory() as repo_dir:
        repo = Path(repo_dir)
        (repo / "src").mkdir()
        (repo / "src" / "main.py").write_text("x = 1\n")

        old_cwd = os.getcwd()
        os.chdir(repo)
        try:
            # Must not raise; defaults to "." (whole project from cwd).
            result = mod.create_tree_report(None)
            assert "✅ Success" in result, result
            report_file = None
            for line in result.splitlines():
                if "Generated Report:" in line and "`" in line:
                    report_file = line.split("`")[1]
            assert report_file, "Could not parse report path"
            content = Path(report_file).read_text()
            assert "main.py" in content, "None input should default to the whole-project tree"
        finally:
            os.chdir(old_cwd)


def test_stage_and_inject_diff_with_ignored_context_reports():
    """Verify stage_and_inject_diff succeeds even when an ignored context-reports/ dir exists.

    Regression test: the old `git add . :!context-reports/` pathspec made git
    fail with "The following paths are ignored..." whenever the ignored
    directory existed on disk, blocking the entire closure flow.
    """
    import importlib
    import os
    import subprocess
    import tempfile

    server_path = Path(__file__).parent.parent / "mcp-context-server" / "server.py"
    spec = importlib.util.spec_from_file_location("context_server_stage", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    with tempfile.TemporaryDirectory() as repo_dir:
        repo = Path(repo_dir)
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)

        # Ignored context-reports/ directory exists on disk
        (repo / ".gitignore").write_text("context-reports/\n")
        report_dir = repo / "context-reports"
        report_dir.mkdir()
        (report_dir / "context_report_x.md").write_text("ignored content\n")

        # Code change + task file with diff markers
        (repo / "feature.py").write_text("x = 1\n")
        task_file = repo / "tasks" / "78-fix-bug.md"
        task_file.parent.mkdir()
        task_file.write_text(
            "# Task 78: Fix bug\n\n## Factual Git Diff\n\n"
            "<!-- BEGIN_GIT_DIFF -->\n<!-- END_GIT_DIFF -->\n"
        )

        old_cwd = os.getcwd()
        os.chdir(repo)
        try:
            # F5 contract (Task 90): stage_and_inject_diff stages ONLY the explicitly
            # listed modified files + the task file — pass the modified file list.
            result = mod.stage_and_inject_diff(str(task_file), modified_files=["feature.py"])
        finally:
            os.chdir(old_cwd)
        assert "✅ Success" in result, result

        # Task file now contains the injected diff
        assert "feature.py" in task_file.read_text(), "Diff should be injected into the task file"

        # The ignored report must not be staged; the code change must be
        staged = subprocess.run(
            ["git", "diff", "--cached", "--name-only"], cwd=repo, capture_output=True, text=True
        ).stdout
        assert "feature.py" in staged, "Code change should be staged"
        assert "context-reports" not in staged, "Ignored reports must not be staged"
        assert "context_report_x.md" not in staged, "Report content must not be staged"
