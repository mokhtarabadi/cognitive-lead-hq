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

## Execution Log & Reasoning

Test

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
"""
    issues = mod._check_task_file_structure(valid_content, "tasks/backlog/99-test.md")
    assert len(issues) == 0, f"Expected no issues, got: {issues}"


def test_lint_task_file_path_mismatch():
    """Verify the lint server flags a **File:** header that drifts from the actual path.

    Fail-first regression test for the path-drift guard: content whose
    `**File:**` header points at `tasks/backlog/99-test.md` but which is passed
    in as `tasks/in-progress/99-test.md` must be reported as a mismatch (e.g.
    after a git mv between Kanban directories leaves a stale header behind).
    """
    import importlib

    server_path = Path(__file__).parent.parent / "mcp-lint-server" / "server.py"
    spec = importlib.util.spec_from_file_location("lint_server", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

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

## Execution Log & Reasoning

Test

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
"""
    # Header says backlog, but the file is actually in in-progress.
    issues = mod._check_task_file_structure(valid_content, "tasks/in-progress/99-test.md")
    assert any("File path mismatch" in i for i in issues), (
        f"Expected 'File path mismatch' issue, got: {issues}"
    )

    # Sanity: same content with the matching path must produce no mismatch.
    issues_ok = mod._check_task_file_structure(valid_content, "tasks/backlog/99-test.md")
    assert not any("File path mismatch" in i for i in issues_ok), (
        f"Matching header/path must not be flagged: {issues_ok}"
    )


def test_lint_task_file_missing_file_header():
    """Verify the lint server flags a task file with no `**File:**` metadata field.

    Fail-first regression test for the missing-header guard: content that has
    all required sections but omits the `**File:**` line entirely must produce
    a "Missing `**File:**` metadata field." issue instead of crashing the
    regex comparison or silently passing.
    """
    import importlib

    server_path = Path(__file__).parent.parent / "mcp-lint-server" / "server.py"
    spec = importlib.util.spec_from_file_location("lint_server", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # All required sections present, but NO `**File:**` line at all.
    no_header_content = """# Task 99: Test

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

## Execution Log & Reasoning

Test

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
"""
    issues = mod._check_task_file_structure(no_header_content, "99-test.md")
    assert any("Missing `**File:**` metadata field." in i for i in issues), (
        f"Expected 'Missing **File:** metadata field' issue, got: {issues}"
    )
    # The missing header must not also produce a spurious path mismatch.
    assert not any("File path mismatch" in i for i in issues), (
        f"Missing header must not produce a path mismatch: {issues}"
    )


def test_lint_task_file_absolute_path_matches_relative_header():
    """Verify the path-drift guard compares RESOLVED absolute paths, not raw strings.

    Fail-first regression test: `lint_task_file` explicitly accepts absolute or
    relative paths, so calling `_check_task_file_structure` with an absolute
    path while the `**File:**` header holds the equivalent relative path must
    NOT be flagged as a mismatch (they resolve to the same file).
    """
    import importlib

    server_path = Path(__file__).parent.parent / "mcp-lint-server" / "server.py"
    spec = importlib.util.spec_from_file_location("lint_server", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

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

## Execution Log & Reasoning

Test

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
"""
    # Relative header + equivalent absolute actual path -> must match.
    abs_path = str(Path("tasks/backlog/99-test.md").resolve())
    issues = mod._check_task_file_structure(valid_content, abs_path)
    assert not any("File path mismatch" in i for i in issues), (
        f"Resolved absolute path must match relative header, got: {issues}"
    )

    # Sanity: a genuinely different absolute path still flags the mismatch.
    other_path = str(Path("tasks/in-progress/99-test.md").resolve())
    issues_mismatch = mod._check_task_file_structure(valid_content, other_path)
    assert any("File path mismatch" in i for i in issues_mismatch), (
        f"Different resolved path must still be flagged: {issues_mismatch}"
    )


def test_lint_task_file_rejects_file_path_mismatch():
    """Verify the lint server rejects a `**File:**` header that drifted across Kanban dirs.

    Fail-first regression test (Task 98, QA round 9): after a `git mv` between Kanban
    directories, a stale header is the classic failure mode. Content whose `**File:**`
    header still points at `tasks/backlog/99-test.md` while the file actually lives in
    `tasks/qa/99-test.md` MUST be reported as a path mismatch — the header no longer
    describes where the file is.
    """
    import importlib

    server_path = Path(__file__).parent.parent / "mcp-lint-server" / "server.py"
    spec = importlib.util.spec_from_file_location("lint_server_path_mismatch", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

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

## Execution Log & Reasoning

Test

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
"""
    # Header says backlog, but the file actually lives in qa (post-git-mv drift).
    issues = mod._check_task_file_structure(valid_content, "tasks/qa/99-test.md")
    assert any("File path mismatch" in i for i in issues), (
        f"Expected 'File path mismatch' issue for stale Kanban header, got: {issues}"
    )


def test_lint_task_file_accepts_matching_file_path():
    """Verify the lint server accepts a `**File:**` header matching the actual path.

    Regression guard (Task 98, QA round 9): after the Hands synchronize the `**File:**`
    metadata to the new Kanban path, the file must lint clean — no spurious path
    mismatch. Content whose header matches the actual `tasks/qa/99-test.md` path must
    produce no `File path mismatch` issue.
    """
    import importlib

    server_path = Path(__file__).parent.parent / "mcp-lint-server" / "server.py"
    spec = importlib.util.spec_from_file_location("lint_server_path_match", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    valid_content = """# Task 99: Test

**File:** `tasks/qa/99-test.md`
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

## Execution Log & Reasoning

Test

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
"""
    issues = mod._check_task_file_structure(valid_content, "tasks/qa/99-test.md")
    assert not any("File path mismatch" in i for i in issues), (
        f"Matching header/path must not be flagged as drift, got: {issues}"
    )


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

## Execution Log & Reasoning

Test

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
"""
    issues = mod._check_task_file_structure(incomplete_content, "tasks/backlog/99-test.md")
    assert len(issues) > 0, "Expected issues for missing sections, got none"
    # Should flag missing Acceptance Criteria, Verification Evidence, Risk & Rollback
    assert any("Acceptance Criteria" in i for i in issues), (
        "Missing section detection for Acceptance Criteria"
    )


def test_lint_task_file_accepts_old_and_new_headers():
    """Verify the lint server accepts BOTH the new and legacy Execution Log headers.

    Regression guard (Task 98, QA round 7): the task-file section header was
    renamed from `## OpenCode Execution Log & Reasoning` to `## Execution Log
    & Reasoning` in v8.4.5. QA round 7 made the linter BACKWARD COMPATIBLE:
    existing projects that predate the runtime-agnostic rename still carry the
    legacy OpenCode-named header and must lint clean (no missing-section error)
    instead of hard-failing, while files using the new canonical header keep
    passing. Both variants are asserted below on the same structurally valid
    template so neither direction regresses.
    """
    import importlib

    server_path = Path(__file__).parent.parent / "mcp-lint-server" / "server.py"
    spec = importlib.util.spec_from_file_location("lint_server_headers", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Structurally valid task file, parameterized over the Execution Log header.
    template = """# Task 99: Test

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

## {header}

Test

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
"""

    # New canonical header must pass.
    new_header_content = template.format(header="Execution Log & Reasoning")
    issues_new = mod._check_task_file_structure(new_header_content, "tasks/backlog/99-test.md")
    assert "Missing required section: `## Execution Log & Reasoning`" not in issues_new, (
        f"Canonical '## Execution Log & Reasoning' header must pass; got: {issues_new}"
    )

    # Deprecated legacy header must ALSO pass (backward compatibility).
    old_header_content = template.format(header="OpenCode Execution Log & Reasoning")
    issues_old = mod._check_task_file_structure(old_header_content, "tasks/backlog/99-test.md")
    assert "Missing required section: `## Execution Log & Reasoning`" not in issues_old, (
        f"Legacy '## OpenCode Execution Log & Reasoning' header must be accepted "
        f"(non-breaking guarantee); got: {issues_old}"
    )


def test_lint_task_file_rejects_missing_execution_log():
    """Verify the lint server rejects a file with NEITHER Execution Log header.

    Regression guard (Task 98, QA round 7): the backward-compatible header
    check must not become a no-op. A task file that omits the section entirely
    (no canonical `## Execution Log & Reasoning` AND no legacy
    `## OpenCode Execution Log & Reasoning`) must still fail with the
    missing-section message for the canonical header.
    """
    import importlib

    server_path = Path(__file__).parent.parent / "mcp-lint-server" / "server.py"
    spec = importlib.util.spec_from_file_location("lint_server_no_log", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Structurally valid task file EXCEPT the Execution Log section is absent.
    no_log_content = """# Task 99: Test

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

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
"""
    issues = mod._check_task_file_structure(no_log_content, "tasks/backlog/99-test.md")
    assert "Missing required section: `## Execution Log & Reasoning`" in issues, (
        f"File with NEITHER Execution Log header must be rejected; got: {issues}"
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


def test_system_prompt_has_no_opencode_tags():
    """Verify system-prompt.md (v8.4.5+) contains no `<opencode_` prefixed tags.

    Regression guard (Task 98): the Orchestrator Brain previously emitted
    OpenCode-only XML tags (`<opencode_discovery_task>`,
    `<opencode_implementation_task>`, `<opencode_combined_task>`), which only
    OpenCode understood. Since v8.4.5 the system prompt is runtime-agnostic
    ("the Hands") and emits `<hands_*_task>` blocks, so the same prompt
    drives OpenCode.

    This broader guard asserts that NO line contains the case-sensitive prefix
    `<opencode_` at all — not just the three historical tag spellings — so any
    future OpenCode-only tag variant (e.g. a re-added `<opencode_protocols>`
    or a new `<opencode_review_task>`) fails this test immediately instead of
    silently breaking sessions that receive the Orchestrator's
    output.
    """
    repo_root = Path(__file__).parent.parent
    system_prompt = repo_root / "system-prompt.md"
    content = system_prompt.read_text(encoding="utf-8")
    for lineno, line in enumerate(content.splitlines(), 1):
        assert "<opencode_" not in line, (
            f"system-prompt.md:{lineno} contains the OpenCode-only prefix "
            "`<opencode_` — use the runtime-agnostic `<hands_*>` equivalents "
            f"(Task 98). Offending line: {line.strip()[:120]}"
        )


def test_workflow_skills_have_no_opencode_execution_log():
    """Verify active workflow skills are runtime-agnostic (Task 98).

    Regression guard (Task 98, QA round 4): the task-file section header was
    renamed from `## OpenCode Execution Log & Reasoning` to `## Execution Log
    & Reasoning`, and the workflow skill templates (`skill-templates/*/SKILL.md`)
    plus the OpenCode executor agent (`agents/cognitive-executor.md`) must not
    regress to the OpenCode-only wording — the same skills drive the Hands in
    OpenCode.

    Scope of the guard:
    - ALL `skill-templates/*/SKILL.md` files are scanned (glob), so a NEW skill
      template reintroducing the old header or prose also fails immediately.
    - `agents/cognitive-executor.md` is the OpenCode agent definition; its prose
      must reference the canonical header name even though the file legitimately
      keeps OpenCode-specific frontmatter, paths, and tool names.

    The two assertions are intentionally separate so a failure message pinpoints
    whether the exact `## ` header or the prose wording regressed. Note this test
    does NOT flag the historical `tasks/archive/*` files or `CHANGELOG.md`
    entries — those are immutable historical records by design.
    """
    repo_root = Path(__file__).parent.parent
    target_files = list((repo_root / "skill-templates").glob("*/SKILL.md"))
    target_files.append(repo_root / "agents" / "cognitive-executor.md")
    assert len(target_files) >= 32, (
        f"Expected the 32 skill templates + executor agent, got {len(target_files)} files"
    )
    for skill_file in target_files:
        content = skill_file.read_text(encoding="utf-8")
        assert "## OpenCode Execution Log & Reasoning" not in content, (
            f"{skill_file} still contains the OpenCode-only task-file header"
        )
        assert "OpenCode Execution Log" not in content, (
            f"{skill_file} still contains OpenCode Execution Log wording"
        )


def test_lint_task_file_rejects_duplicate_factual_git_diff_heading():
    """Verify the lint server rejects a task file with TWO `## Factual Git Diff` headings.

    Regression guard (Task 98, QA round 8): a duplicate `## Factual Git Diff`
    heading before the diff block splits the injected-diff section and desyncs
    the BEGIN/END markers. The linter must report the duplicate instead of
    silently accepting it (the round-7 duplicate-heading cleanup regression).
    """
    import importlib

    server_path = Path(__file__).parent.parent / "mcp-lint-server" / "server.py"
    spec = importlib.util.spec_from_file_location("lint_server_dup_factual", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    dup_content = """# Task 99: Test

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

## Execution Log & Reasoning

Test

## Factual Git Diff

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
"""
    issues = mod._check_task_file_structure(dup_content, "tasks/backlog/99-test.md")
    assert any("Duplicate" in i and "Factual Git Diff" in i for i in issues), (
        f"Two `## Factual Git Diff` headings must be rejected; got: {issues}"
    )


def test_lint_task_file_rejects_both_execution_log_headers():
    """Verify the lint server rejects BOTH Execution Log headers present at once.

    Regression guard (Task 98, QA round 8): a task file that carries BOTH the
    canonical `## Execution Log & Reasoning` and the legacy OpenCode-named
    header is a half-completed migration artifact. The linter must report it as
    a duplicate rather than accepting the file — exactly one Execution Log
    heading (in either spelling) is required.
    """
    import importlib

    server_path = Path(__file__).parent.parent / "mcp-lint-server" / "server.py"
    spec = importlib.util.spec_from_file_location("lint_server_both_log", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    both_content = """# Task 99: Test

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

## Execution Log & Reasoning

Test

## OpenCode Execution Log & Reasoning

Test

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
"""
    issues = mod._check_task_file_structure(both_content, "tasks/backlog/99-test.md")
    assert any("Duplicate" in i and "Execution Log" in i for i in issues), (
        f"Both Execution Log headers must be rejected; got: {issues}"
    )


def test_system_prompt_summary_mentions_qa_transition():
    """Verify at least one `<summary_phase>` block in system-prompt.md mentions `tasks/qa/`.

    Regression guard (Task 98, QA round 8): the canonical QA-transition rule
    requires the Hands to move a successfully-staged implementation task from
    `tasks/in-progress/` to `tasks/qa/` before notifying the Manager. The
    system prompt's task templates must encode this, so at least one
    `<summary_phase>` block must reference the `tasks/qa/` directory.
    """
    import re

    repo_root = Path(__file__).parent.parent
    system_prompt = (repo_root / "system-prompt.md").read_text(encoding="utf-8")

    summary_blocks = re.findall(r"<summary_phase>.*?</summary_phase>", system_prompt, re.DOTALL)
    assert summary_blocks, "system-prompt.md must contain at least one <summary_phase> block"
    assert any("tasks/qa/" in block for block in summary_blocks), (
        "At least one <summary_phase> block must mention the `tasks/qa/` QA-transition "
        "destination"
    )


def test_workflow_upgrade_guide_exists():
    """Verify the v8.4.5 workflow upgrade guide exists.

    Regression guard (Task 98, QA round 8): `docs/workflow-upgrade-v8.4.5.md`
    documents the runtime-agnostic rename and the non-breaking upgrade path for
    existing projects. Its absence would strand pre-v8.4.5 projects without
    migration guidance.
    """
    repo_root = Path(__file__).parent.parent
    guide = repo_root / "docs" / "workflow-upgrade-v8.4.5.md"
    assert guide.is_file(), (
        "docs/workflow-upgrade-v8.4.5.md must exist (v8.4.5 upgrade guide)"
    )


def test_cognitive_executor_preserves_qa_and_closure_rules():
    """Verify agents/cognitive-executor.md preserves the QA git-mv Rule and closure authorization Rule.

    Regression guard (Task 98, QA round 10): QA round 9 accidentally removed
    the QA/Review Phase "Rule" bullet that instructs the Hands to move the task
    to tasks/qa/, and the Closure Sequence "Rule" bullet that requires explicit
    Manager authorization. Both bullets are mandatory ZAC/Kanban safeguards and
    must remain present in the OpenCode executor definition.
    """
    repo_root = Path(__file__).parent.parent
    executor = repo_root / "agents" / "cognitive-executor.md"
    content = executor.read_text(encoding="utf-8")

    assert "- **Rule:** When your implementation and `stage_and_inject_diff` are complete" in content, (
        "agents/cognitive-executor.md must preserve the QA/Review Phase Rule bullet "
        "authorizing the git mv from tasks/in-progress/ to tasks/qa/."
    )
    assert '- **Rule:** Only when the Manager explicitly says "Approved for closure" or "Close task"' in content, (
        "agents/cognitive-executor.md must preserve the Closure Sequence Rule bullet "
        "requiring explicit Manager closure authorization."
    )


def test_hands_implementation_summary_phase_has_unique_step_numbers():
    """Verify the Hands implementation template summary_phase steps are numbered sequentially.

    Regression guard (Task 98, QA round 10): QA round 9 introduced duplicate
    step "5." numbering in <hands_implementation_task_template> <summary_phase>.
    Duplicate or skipped step numbers can cause the Hands to skip finalization
    actions. This guard extracts the numbered lines in that summary phase and
    asserts they are exactly 1..N in order.
    """
    import re

    repo_root = Path(__file__).parent.parent
    system_prompt = (repo_root / "system-prompt.md").read_text(encoding="utf-8")

    impl_start = system_prompt.index("<hands_implementation_task_template>")
    impl_end = system_prompt.index("</hands_implementation_task_template>")
    impl_block = system_prompt[impl_start:impl_end]

    # NOTE: use rindex (last occurrence) — the literal string "<summary_phase>"
    # ALSO appears in the template's <bash_phase> CRITICAL RULE 6 prose ("Before
    # proceeding to the <summary_phase>...") BEFORE the real phase. index() would
    # slice from that prose mention and sweep the bash-phase 1-3 steps into the
    # numbering check, producing a false failure.
    summary_start = impl_block.rindex("<summary_phase>")
    summary_end = impl_block.index("</summary_phase>")
    summary_block = impl_block[summary_start:summary_end]

    numbers = re.findall(r"^\s*(\d+)\.", summary_block, flags=re.MULTILINE)
    assert numbers, "The implementation summary_phase must contain numbered steps."
    assert numbers == [str(i) for i in range(1, len(numbers) + 1)], (
        f"Implementation summary_phase steps must be numbered sequentially without "
        f"duplicates or gaps; got: {numbers}"
    )


def test_system_prompt_split_assemble_round_trip():
    """Verify assemble(split(pristine)) reproduces the source byte-for-byte.

    Regression / correctness guard (Task 99): system-prompt.md is now a
    generated build artifact assembled from prompts/fragments/ +
    prompts/shared/. This test splits a pristine copy of the committed
    system-prompt.md into temporary fragment/shared directories, assembles
    them back into a temporary output, and asserts the result is
    byte-identical to the original — proving the split/assemble pipeline is
    lossless (no text change to the final assembled file is permitted).
    """
    import importlib
    import tempfile
    import shutil

    repo_root = Path(__file__).parent.parent
    pristine_path = repo_root / "system-prompt.md"
    splitter_path = repo_root / "scripts" / "prompt-build" / "split_system_prompt.py"
    assembler_path = repo_root / "scripts" / "prompt-build" / "assemble_system_prompt.py"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Copy the committed system-prompt.md as the pristine source.
        pristine_copy = tmp / "system-prompt.pristine.md"
        shutil.copy(pristine_path, pristine_copy)

        # Temp output directories for the split.
        frag_dir = tmp / "fragments"
        shared_dir = tmp / "shared"
        manifest = tmp / "manifest.txt"

        # Import + run the splitter against the temp copy.
        spec = importlib.util.spec_from_file_location("splitter_rt", splitter_path)
        splitter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(splitter)
        splitter.split_system_prompt(
            source_path=str(pristine_copy),
            fragments_dir=str(frag_dir),
            shared_dir=str(shared_dir),
            manifest_path=str(manifest),
        )

        # Import + run the assembler reading from the temp dirs.
        spec2 = importlib.util.spec_from_file_location("assembler_rt", assembler_path)
        assembler = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(assembler)
        assembled_path = tmp / "assembled.md"
        assembler.assemble(
            output_path=str(assembled_path),
            fragments_dir=str(frag_dir),
            shared_dir=str(shared_dir),
            manifest_path=str(manifest),
        )

        assembled = assembled_path.read_text(encoding="utf-8")
        pristine = pristine_copy.read_text(encoding="utf-8")
        assert assembled == pristine, (
            "assemble(split(pristine)) must be byte-identical to the pristine "
            f"copy. First diff: ...{repr(assembled[:200])}... vs ...{repr(pristine[:200])}..."
        )


def test_lint_system_prompt_sync_clean():
    """Verify lint_system_prompt_sync reports 'in sync' on the committed state.

    Regression guard (Task 99): the lint tool must report clean when the
    committed system-prompt.md matches the fragments that assemble it.
    """
    import importlib

    repo_root = Path(__file__).parent.parent
    server_path = repo_root / "mcp-lint-server" / "server.py"
    spec = importlib.util.spec_from_file_location("lint_server_sync_clean", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    in_sync, msg = mod._check_system_prompt_sync()
    assert in_sync is True, f"Expected clean sync but got: {msg}"
    assert "in sync" in msg.lower(), f"Unexpected sync message: {msg}"


def test_lint_system_prompt_sync_detects_drift():
    """Verify lint_system_prompt_sync detects drift from a mutated fragment.

    Regression guard (Task 99): when a fragment is artificially mutated in a
    temp copy, the sync check must report DRIFT (not silently pass). The test
    copies the real fragments/shared/manifest to a temp dir, mutates one
    fragment, and asserts the check against the unchanged committed
    system-prompt.md flags the discrepancy.
    """
    import importlib
    import tempfile
    import shutil

    repo_root = Path(__file__).parent.parent
    server_path = repo_root / "mcp-lint-server" / "server.py"
    spec = importlib.util.spec_from_file_location("lint_server_drift", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Copy the real fragments/shared/manifest into a temp dir.
        frag_dir = tmp / "fragments"
        shared_dir = tmp / "shared"
        shutil.copytree(repo_root / "prompts" / "fragments", frag_dir)
        shutil.copytree(repo_root / "prompts" / "shared", shared_dir)
        manifest = tmp / "manifest.txt"
        shutil.copy(repo_root / "prompts" / "manifest.txt", manifest)

        # Mutate a fragment in the temp copy.
        fpath = frag_dir / "03-system_context.md"
        original = fpath.read_text(encoding="utf-8")
        fpath.write_text(
            original.replace("January 2025", "January 2099"), encoding="utf-8"
        )

        # The committed system-prompt.md is unchanged — drift must be detected.
        in_sync, msg = mod._check_system_prompt_sync(
            fragments_dir=str(frag_dir),
            shared_dir=str(shared_dir),
            manifest_path=str(manifest),
            system_prompt_path=str(repo_root / "system-prompt.md"),
        )
        assert in_sync is False, "Expected drift to be detected, but check reported clean."
        assert "DRIFT DETECTED" in msg, f"Expected DRIFT message, got: {msg[:200]}"


def test_lint_system_prompt_sync_missing_system_prompt_file():
    """Verify lint_system_prompt_sync handles missing system-prompt.md gracefully.

    Regression guard (QA Fix Round 1, V1): _check_system_prompt_sync() must
    return a clean (False, "Error: File not found: ...") tuple instead of
    raising FileNotFoundError when the system_prompt_path does not exist.
    This mirrors the existence-guard pattern used by lint_markdown() and
    lint_task_file() in the same server.
    """
    import importlib
    import tempfile

    repo_root = Path(__file__).parent.parent
    server_path = repo_root / "mcp-lint-server" / "server.py"
    spec = importlib.util.spec_from_file_location("lint_server_missing", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Use a non-existent path for system_prompt_path
        missing_path = Path(tmpdir) / "does_not_exist.md"
        in_sync, msg = mod._check_system_prompt_sync(
            system_prompt_path=str(missing_path)
        )
        assert in_sync is False, f"Expected False for missing file, got: {msg}"
        assert "not found" in msg.lower(), f"Expected 'not found' in message: {msg}"


def test_assemble_raises_on_unresolved_placeholder():
    """Verify assemble() raises ValueError when a placeholder remains unresolved.

    Regression guard (QA Fix Round 1, V2): assemble() must fail loudly with
    ValueError if any {{PLACEHOLDER}} remains in a fragment after include
    resolution. This prevents silent corruption where a shared partial's
    placeholder is never substituted and literal placeholder text leaks into
    the generated system-prompt.md.
    """
    import importlib
    import tempfile
    import shutil
    import pytest

    repo_root = Path(__file__).parent.parent
    assembler_path = repo_root / "scripts" / "prompt-build" / "assemble_system_prompt.py"
    spec = importlib.util.spec_from_file_location("assembler_unresolved", assembler_path)
    assembler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(assembler)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Create a minimal fragment that includes a shared partial with an
        # unresolved placeholder {{FOO}}.
        frag_dir = tmp / "fragments"
        shared_dir = tmp / "shared"
        frag_dir.mkdir()
        shared_dir.mkdir()

        # Fragment with include marker that supplies no value for FOO
        fragment_path = frag_dir / "01-test.md"
        fragment_path.write_text(
            "<test>\n<!--INCLUDE:shared/test.md|NEXT_PHASE=Context-->\n</test>\n",
            encoding="utf-8",
        )

        # Shared partial containing {{FOO}} placeholder — no include marker
        # provides a value for FOO, so it should remain unresolved.
        shared_path = shared_dir / "test.md"
        shared_path.write_text(
            "Content with {{FOO}} placeholder.\n", encoding="utf-8"
        )

        manifest = tmp / "manifest.txt"
        manifest.write_text("01-test.md\n", encoding="utf-8")

        assembled_path = tmp / "assembled.md"

        # assemble() should raise ValueError with the unresolved placeholder name.
        with pytest.raises(ValueError, match=r"Unresolved placeholder \{\{FOO\}\} in fragment 01-test.md"):
            assembler.assemble(
                output_path=str(tmp / "out.md"),
                fragments_dir=str(frag_dir),
                shared_dir=str(shared_dir),
                manifest_path=str(manifest),
            )


def test_lint_system_prompt_sync_handles_unresolved_placeholder():
    """Verify _check_system_prompt_sync() degrades cleanly on unresolved placeholder.

    Regression guard (QA Fix Round 2): assemble() raises ValueError when a
    {{PLACEHOLDER}} remains unresolved — that is intentional and correct for
    CLI/direct callers. But the lint server's _check_system_prompt_sync() is a
    diagnostic tool and must NOT crash when it drives the assembler against a
    broken fragment tree. It must catch the ValueError (added in round 2) and
    return a clean (False, <message>) tuple whose message still identifies the
    placeholder, so the user can fix the source prompt tree.
    """
    import importlib
    import tempfile

    repo_root = Path(__file__).parent.parent
    server_path = repo_root / "mcp-lint-server" / "server.py"
    spec = importlib.util.spec_from_file_location("lint_server_unresolved", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Reuse the same fixture shape as test_assemble_raises_on_unresolved_placeholder:
        # a fragment with an include marker, a shared partial containing an
        # unresolved {{FOO}} placeholder, and a manifest.
        frag_dir = tmp / "fragments"
        shared_dir = tmp / "shared"
        frag_dir.mkdir()
        shared_dir.mkdir()

        fragment_path = frag_dir / "01-test.md"
        fragment_path.write_text(
            "<test>\n<!--INCLUDE:shared/test.md|NEXT_PHASE=Context-->\n</test>\n",
            encoding="utf-8",
        )
        shared_path = shared_dir / "test.md"
        shared_path.write_text(
            "Content with {{FOO}} placeholder.\n", encoding="utf-8"
        )
        manifest = tmp / "manifest.txt"
        manifest.write_text("01-test.md\n", encoding="utf-8")

        # _check_system_prompt_sync() must return (False, message) WITHOUT raising.
        in_sync, msg = mod._check_system_prompt_sync(
            fragments_dir=str(frag_dir),
            shared_dir=str(shared_dir),
            manifest_path=str(manifest),
            system_prompt_path=str(repo_root / "system-prompt.md"),
        )
        assert in_sync is False, f"Expected False, got: {msg}"
        assert "FOO" in msg, f"Expected message to identify the placeholder {{FOO}}, got: {msg}"


def test_split_halts_on_missing_top_level_tag():
    """Verify split_system_prompt() halts when a top-level tag is missing.

    Regression guard (QA Fix Round 1, Step 5): split_system_prompt() uses
    _halt() -> sys.exit(1) when a declared top-level tag cannot be located.
    This test verifies that behavior by stripping one top-level tag from a
    pristine copy and asserting SystemExit is raised.
    """
    import importlib
    import tempfile
    import shutil
    import pytest

    repo_root = Path(__file__).parent.parent
    pristine_path = repo_root / "system-prompt.md"
    splitter_path = repo_root / "scripts" / "prompt-build" / "split_system_prompt.py"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Copy pristine and strip one top-level tag (e.g., <ai_objective>...</ai_objective>)
        pristine_copy = tmp / "system-prompt.pristine.md"
        shutil.copy(pristine_path, pristine_copy)
        content = pristine_copy.read_text(encoding="utf-8")

        # Remove the <ai_objective> block (including its opening/closing tags)
        # Find the block boundaries
        start = content.find("<ai_objective>")
        end = content.find("</ai_objective>")
        assert start != -1 and end != -1, "Test setup: ai_objective tag not found in pristine"
        end += len("</ai_objective>")
        corrupted = content[:start] + content[end:]
        corrupted_path = tmp / "system-prompt.corrupted.md"
        corrupted_path.write_text(corrupted, encoding="utf-8")

        # Import + run splitter on corrupted file — should raise SystemExit
        spec = importlib.util.spec_from_file_location("splitter_corrupt", splitter_path)
        splitter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(splitter)

        with pytest.raises(SystemExit) as exc_info:
            splitter.split_system_prompt(
                source_path=str(corrupted_path),
                fragments_dir=str(tmp / "fragments"),
                shared_dir=str(tmp / "shared"),
                manifest_path=str(tmp / "manifest.txt"),
            )
        # _halt() calls sys.exit(1)
        assert exc_info.value.code == 1


def test_assemble_rejects_path_traversal_include():
    """Verify assemble() rejects include markers that escape prompts/ via '..'.

    Regression guard (QA Fix Round 3): include paths are resolved relative to
    prompts/ and the resolved path MUST stay inside prompts/. An include
    marker like <!--INCLUDE:../outside.md--> would otherwise read an arbitrary
    file from outside the prompt source tree — a path-traversal hole. The
    assembler must raise ValueError naming the unsafe include path.
    """
    import importlib
    import tempfile
    import pytest

    repo_root = Path(__file__).parent.parent
    assembler_path = repo_root / "scripts" / "prompt-build" / "assemble_system_prompt.py"
    spec = importlib.util.spec_from_file_location("assembler_traversal", assembler_path)
    assembler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(assembler)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Build a prompt tree where prompts/fragments/ is inside a temp prompts/ dir.
        prompts_dir = tmp / "prompts"
        frag_dir = prompts_dir / "fragments"
        shared_dir = prompts_dir / "shared"
        frag_dir.mkdir(parents=True)
        shared_dir.mkdir()

        # A file OUTSIDE prompts/ that the traversal attempt should NOT be able
        # to read.
        outside_file = tmp / "outside.md"
        outside_file.write_text("SECRET OUTSIDE CONTENT\n", encoding="utf-8")

        # Fragment with an include marker attempting to read ../outside.md
        # (resolves to tmp/outside.md — outside prompts_dir).
        fragment_path = frag_dir / "01-test.md"
        fragment_path.write_text(
            "<test>\n<!--INCLUDE:../outside.md-->\n</test>\n",
            encoding="utf-8",
        )
        manifest = tmp / "manifest.txt"
        manifest.write_text("01-test.md\n", encoding="utf-8")

        # assemble() must raise ValueError naming the unsafe include path.
        with pytest.raises(ValueError) as exc_info:
            assembler.assemble(
                output_path=str(tmp / "out.md"),
                fragments_dir=str(frag_dir),
                shared_dir=str(shared_dir),
                manifest_path=str(manifest),
            )
        assert "../outside.md" in str(exc_info.value), (
            f"Error message must identify the unsafe include path, got: {exc_info.value}"
        )


def test_assemble_rejects_malformed_include_marker():
    """Verify assemble() fails loudly on a malformed include marker.

    Regression guard (QA Fix Round 3): a marker like
    <!--INCLUDE:shared/test.md|NEXT_PHASE=Context--!> is malformed — its
    closing sequence is wrong, so the regex-driven _resolve_includes() cannot
    match it and the literal marker text would silently leak into the
    generated system-prompt.md. The assembler must detect any remaining
    `<!--INCLUDE:` substring after resolution and raise ValueError identifying
    the fragment and the malformed/unresolved marker.
    """
    import importlib
    import tempfile
    import pytest

    repo_root = Path(__file__).parent.parent
    assembler_path = repo_root / "scripts" / "prompt-build" / "assemble_system_prompt.py"
    spec = importlib.util.spec_from_file_location("assembler_malformed", assembler_path)
    assembler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(assembler)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        frag_dir = tmp / "fragments"
        shared_dir = tmp / "shared"
        frag_dir.mkdir()
        shared_dir.mkdir()
        # A well-formed shared file exists, but the fragment's marker is
        # malformed so it will never be resolved.
        (shared_dir / "test.md").write_text("SHARED\n", encoding="utf-8")

        fragment_path = frag_dir / "01-test.md"
        fragment_path.write_text(
            "<test>\n<!--INCLUDE:shared/test.md|NEXT_PHASE=Context--!>\n</test>\n",
            encoding="utf-8",
        )
        manifest = tmp / "manifest.txt"
        manifest.write_text("01-test.md\n", encoding="utf-8")

        # assemble() must raise ValueError identifying the fragment and the
        # malformed/unresolved marker.
        with pytest.raises(ValueError) as exc_info:
            assembler.assemble(
                output_path=str(tmp / "out.md"),
                fragments_dir=str(frag_dir),
                shared_dir=str(shared_dir),
                manifest_path=str(manifest),
            )
        msg = str(exc_info.value)
        assert "01-test.md" in msg, f"Error message must identify the fragment, got: {msg}"
        assert "<!--INCLUDE:" in msg or "INCLUDE" in msg, (
            f"Error message must identify the malformed include marker, got: {msg}"
        )


def test_lint_system_prompt_sync_missing_include_file():
    """Verify _check_system_prompt_sync() degrades cleanly when a shared include file is missing.

    Regression guard (QA Fix Round 3): a fragment referencing a shared partial
    that does not exist raises FileNotFoundError inside the assembler. The lint
    diagnostic tool must catch it and return (False, message) — identifying the
    missing file / include failure — WITHOUT raising.
    """
    import importlib
    import tempfile

    repo_root = Path(__file__).parent.parent
    server_path = repo_root / "mcp-lint-server" / "server.py"
    spec = importlib.util.spec_from_file_location("lint_server_missing_include", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        frag_dir = tmp / "fragments"
        shared_dir = tmp / "shared"
        frag_dir.mkdir()
        shared_dir.mkdir()
        # Valid-looking include marker pointing at a shared file that does NOT exist.
        fragment_path = frag_dir / "01-test.md"
        fragment_path.write_text(
            "<test>\n<!--INCLUDE:shared/missing.md-->\n</test>\n",
            encoding="utf-8",
        )
        manifest = tmp / "manifest.txt"
        manifest.write_text("01-test.md\n", encoding="utf-8")

        in_sync, msg = mod._check_system_prompt_sync(
            fragments_dir=str(frag_dir),
            shared_dir=str(shared_dir),
            manifest_path=str(manifest),
            system_prompt_path=str(repo_root / "system-prompt.md"),
        )
        assert in_sync is False, f"Expected False, got: {msg}"
        assert "missing" in msg.lower() or "not found" in msg.lower() or "include" in msg.lower(), (
            f"Expected message to identify the missing file or include failure, got: {msg[:200]}"
        )


def test_lint_system_prompt_sync_invalid_fragments_dir_configuration():
    """Verify _check_system_prompt_sync() degrades cleanly on invalid fragments_dir.

    Regression guard (QA Fix Round 3): passing a regular FILE path (instead of
    a directory) as fragments_dir must not crash the diagnostic tool — it must
    return (False, message) WITHOUT raising.
    """
    import importlib
    import tempfile

    repo_root = Path(__file__).parent.parent
    server_path = repo_root / "mcp-lint-server" / "server.py"
    spec = importlib.util.spec_from_file_location("lint_server_invalid_cfg", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # A regular text file used as fragments_dir — a misconfiguration.
        bogus_fragments_dir = tmp / "not-a-directory.txt"
        bogus_fragments_dir.write_text("this is a file, not a directory\n", encoding="utf-8")

        shared_dir = tmp / "shared"
        shared_dir.mkdir()
        manifest = tmp / "manifest.txt"
        manifest.write_text("01-test.md\n", encoding="utf-8")

        in_sync, msg = mod._check_system_prompt_sync(
            fragments_dir=str(bogus_fragments_dir),
            shared_dir=str(shared_dir),
            manifest_path=str(manifest),
            system_prompt_path=str(repo_root / "system-prompt.md"),
        )
        assert in_sync is False, f"Expected False for invalid fragments_dir, got: {msg}"
        assert "error" in msg.lower(), f"Expected an error message, got: {msg[:200]}"


def test_assemble_rejects_path_traversal_manifest_entry():
    """Verify assemble() rejects manifest entries that escape fragments/ via '..'.

    Regression guard (QA Fix Round 4): the manifest is an untrusted input
    surface — it lists the fragment files to read. A manifest entry like
    `../outside.md` would resolve to a file OUTSIDE prompts/fragments/ (the
    assembler reads fragment files by joining fragments_dir with the manifest
    entry). Path traversal via the manifest must raise ValueError naming the
    unsafe manifest entry.
    """
    import importlib
    import tempfile
    import pytest

    repo_root = Path(__file__).parent.parent
    assembler_path = repo_root / "scripts" / "prompt-build" / "assemble_system_prompt.py"
    spec = importlib.util.spec_from_file_location("assembler_manifest_trav", assembler_path)
    assembler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(assembler)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        frag_dir = tmp / "fragments"
        shared_dir = tmp / "shared"
        frag_dir.mkdir()
        shared_dir.mkdir()

        # A file OUTSIDE prompts/fragments/ that traversal must NOT reach.
        outside_file = tmp / "outside.md"
        outside_file.write_text("SECRET OUTSIDE CONTENT\n", encoding="utf-8")

        # A legit fragment exists, but the manifest points at ../outside.md.
        (frag_dir / "01-test.md").write_text("<test>ok</test>\n", encoding="utf-8")
        manifest = tmp / "manifest.txt"
        manifest.write_text("../outside.md\n", encoding="utf-8")

        # assemble() must raise ValueError naming the unsafe manifest entry.
        with pytest.raises(ValueError) as exc_info:
            assembler.assemble(
                output_path=str(tmp / "out.md"),
                fragments_dir=str(frag_dir),
                shared_dir=str(shared_dir),
                manifest_path=str(manifest),
            )
        assert "../outside.md" in str(exc_info.value), (
            f"Error message must identify the unsafe manifest entry, got: {exc_info.value}"
        )


def test_assemble_rejects_absolute_manifest_entry():
    """Verify assemble() rejects absolute paths in the manifest.

    Regression guard (QA Fix Round 4): the manifest must only reference fragment
    files inside prompts/fragments/. An absolute manifest entry (e.g. the
    absolute path of a file outside fragments/) must raise ValueError naming the
    unsafe absolute manifest entry — the manifest is untrusted input and must
    never be able to point the assembler at an arbitrary file on the host.
    """
    import importlib
    import tempfile
    import pytest

    repo_root = Path(__file__).parent.parent
    assembler_path = repo_root / "scripts" / "prompt-build" / "assemble_system_prompt.py"
    spec = importlib.util.spec_from_file_location("assembler_manifest_abs", assembler_path)
    assembler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(assembler)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        frag_dir = tmp / "fragments"
        shared_dir = tmp / "shared"
        frag_dir.mkdir()
        shared_dir.mkdir()

        # A file OUTSIDE prompts/fragments/ whose absolute path goes in the manifest.
        outside_file = tmp / "outside.md"
        outside_file.write_text("SECRET OUTSIDE CONTENT\n", encoding="utf-8")

        (frag_dir / "01-test.md").write_text("<test>ok</test>\n", encoding="utf-8")
        manifest = tmp / "manifest.txt"
        manifest.write_text(f"{outside_file}\n", encoding="utf-8")

        # assemble() must raise ValueError naming the unsafe absolute entry.
        with pytest.raises(ValueError) as exc_info:
            assembler.assemble(
                output_path=str(tmp / "out.md"),
                fragments_dir=str(frag_dir),
                shared_dir=str(shared_dir),
                manifest_path=str(manifest),
            )
        assert str(outside_file) in str(exc_info.value), (
            f"Error message must identify the unsafe absolute manifest entry, "
            f"got: {exc_info.value}"
        )


def test_lint_system_prompt_sync_handles_assembler_load_failure(monkeypatch):
    """Verify _check_system_prompt_sync() degrades cleanly when the assembler cannot load.

    Regression guard (QA Fix Round 4): _load_assembler() dynamically executes
    Python code from scripts/prompt-build/assemble_system_prompt.py — it can
    raise SyntaxError/ImportError (not just FileNotFoundError) if the script is
    corrupted. The MCP diagnostic tool must catch ALL load failures and return
    (False, message) without raising, identifying the load failure.
    """
    import importlib

    repo_root = Path(__file__).parent.parent
    server_path = repo_root / "mcp-lint-server" / "server.py"
    spec = importlib.util.spec_from_file_location("lint_server_load_fail", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Replace _load_assembler with a synthetic failing loader.
    def _failing_loader():
        raise SyntaxError("synthetic assembler load failure")

    monkeypatch.setattr(mod, "_load_assembler", _failing_loader)

    # Use real repo paths for the prompt tree; only the loader is broken here.
    in_sync, msg = mod._check_system_prompt_sync(
        fragments_dir=str(repo_root / "prompts" / "fragments"),
        shared_dir=str(repo_root / "prompts" / "shared"),
        manifest_path=str(repo_root / "prompts" / "manifest.txt"),
        system_prompt_path=str(repo_root / "system-prompt.md"),
    )
    assert in_sync is False, f"Expected False on assembler load failure, got: {msg}"
    assert "error" in msg.lower(), f"Expected an error message, got: {msg[:200]}"
    assert "synthetic assembler load failure" in msg, (
        f"Expected message to identify the load failure, got: {msg[:200]}"
    )
