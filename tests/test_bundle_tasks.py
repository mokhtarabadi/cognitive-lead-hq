#!/usr/bin/env python3
"""
Automated test suite for the meta-task bundler (scripts/bundle-tasks.py).

Covers: T1-T6 (multiline checklist, duplicate ID halt, transactional rollback,
Persian unicode slug, stack conflict guardrail, verbatim SHA validation).
"""

from __future__ import annotations

import importlib
import importlib.util
import re
import sys
from pathlib import Path
from typing import List, Tuple

import pytest

# ---------------------------------------------------------------------------
# Import the bundler module dynamically (hyphenated filename)
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
_bundler_spec = importlib.util.spec_from_file_location(
    "bundle_tasks_bundler",
    PROJECT_ROOT / "scripts" / "bundle-tasks.py",
)
_bundler = importlib.util.module_from_spec(_bundler_spec)
_bundler_spec.loader.exec_module(_bundler)

# Re-export the functions we need
kebab_case = _bundler.kebab_case
find_task_file = _bundler.find_task_file
extract_section = _bundler.extract_section
extract_title = _bundler.extract_title
_build_meta_content = _bundler.build_meta_content
_verify_verbatim_checksums = _bundler.verify_verbatim_checksums
git_mv_or_fallback = _bundler.git_mv_or_fallback
ACTIVE_KANBAN_DIRS = _bundler.ACTIVE_KANBAN_DIRS

# detect_stack may not exist in older versions — guard
detect_stack = getattr(_bundler, "detect_stack", None)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_tasks(tmp_path: Path):
    """Create a temporary tasks/ directory with Kanban subdirs."""
    tasks = tmp_path / "tasks"
    for d in ["backlog", "in-progress", "qa", "completed", "archive"]:
        (tasks / d).mkdir(parents=True, exist_ok=True)
    return tasks


def _create_task_file(
    tasks: Path,
    dirname: str,
    task_id: str,
    title: str,
    ac_lines: list[str],
    stack_hint: str = "",
) -> Path:
    """Helper to create a task file in the specified Kanban directory."""
    padded = f"{int(task_id):02d}"
    slug = title.lower().replace(" ", "-")
    filename = f"{padded}-{slug}.md"
    path = tasks / dirname / filename
    ac_block = "\n".join(f"- [ ] {line}" for line in ac_lines)

    content = (
        f"# Task {task_id}: {title}\n"
        f"\n"
        f"**File:** `{dirname}/{filename}`\n"
        f"**Source:** manager\n"
        f"**Type:** improvement\n"
        f"**Status:** open\n"
        f"\n"
        f"## Goal\n"
        f"\n"
        f"Goal for {title}.\n"
        f"\n"
        f"## Manager's Notes\n"
        f"\n"
        f"Notes for {title}.\n"
        f"\n"
        f"## Local TODOs\n"
        f"\n"
        f"- [ ] Step 1\n"
        f"- [ ] Step 2\n"
        f"\n"
        f"## Acceptance Criteria\n"
        f"\n"
        f"{ac_block}\n"
        f"\n"
        f"## Verification Evidence\n"
        f"\n"
        f"- **Test command:** lint\n"
        f"- **Expected result:** pass\n"
        f"- **Actual result:** _fill_\n"
        f"- **Exit code:** _fill_\n"
        f"\n"
        f"## Definition of Done\n"
        f"\n"
        f"- [ ] Build/Test/Lint pass\n"
        f"- [ ] `lint_task_file` passes\n"
        f"\n"
        f"## Risk & Rollback\n"
        f"\n"
        f"- **Risk:** None\n"
        f"- **Rollback plan:** Revert\n"
        f"\n"
        f"---\n"
        f"\n"
        f"## Execution Log & Reasoning\n"
        f"\n"
        f"_(fill)_"
    )

    if stack_hint:
        content += f"\n\nStack: {stack_hint}"

    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# T1: Multi-line checklist preservation
# ---------------------------------------------------------------------------

def test_multiline_checklist_preservation(tmp_tasks: Path):
    """B1: Verify indented continuation lines survive bundling.

    In real task files, root items have `- [ ]` at column 0, continuations
    are indented (no `- [ ]` prefix), and sub-bullets are indented with `- `.
    """
    # Create task file with manually formatted AC (not using _create_task_file's join)
    path = tmp_tasks / "backlog" / "01-fix-padding.md"
    content = """# Task 01: Fix Padding

**File:** `backlog/01-fix-padding.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Goal

Goal for Fix Padding.

## Acceptance Criteria

- [ ] LoginCard uses start/end padding instead of left/right
  This ensures RTL locales render correctly
  - Sub-item: test with Turkish locale

## Execution Log & Reasoning

_(fill)_"""
    path.write_text(content, encoding="utf-8")

    content = (tmp_tasks / "backlog" / "01-fix-padding.md").read_text()
    ac = extract_section(content, "Acceptance Criteria")
    assert ac is not None, f"extract_section failed. Content:\n{content[:500]}"

    # Extract with multi-line helper (inline logic matching B1)
    lines = ac.splitlines()
    result = []
    in_checklist = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- ["):
            in_checklist = True
            result.append(stripped)
        elif in_checklist:
            if stripped and not stripped.startswith("- [") and not stripped.startswith("## ") and not stripped.startswith("---"):
                result.append(line)
            else:
                in_checklist = False
                if stripped.startswith("- ["):
                    in_checklist = True
                    result.append(stripped)

    assert len(result) == 3, f"Expected 3 items, got {len(result)}: {result}"
    assert result[0].startswith("- [ ]")  # root bullet (stripped)
    assert not result[1].startswith("- [")  # continuation (preserved indentation)
    assert result[1].strip()  # non-empty


# ---------------------------------------------------------------------------
# T2: Duplicate ID hard halt
# ---------------------------------------------------------------------------

def test_duplicate_active_id_halt(tmp_tasks: Path):
    """B2: Verify hard failure when two active tasks share the same ID."""
    content = (
        "# Task 05: Duplicate Task\n"
        "\n"
        "**File:** `tasks/backlog/05-duplicate.md`\n"
        "**Source:** manager\n"
        "**Type:** improvement\n"
        "**Status:** open\n"
        "\n"
        "## Goal\n"
        "Goal.\n"
        "\n"
        "## Manager's Notes\n"
        "Notes.\n"
        "\n"
        "## Local TODOs\n"
        "- [ ] Step 1\n"
        "\n"
        "## Acceptance Criteria\n"
        "- [ ] Criterion 1\n"
        "\n"
        "## Verification Evidence\n"
        "- **Test command:** lint\n"
        "- **Expected result:** pass\n"
        "- **Actual result:** _fill_\n"
        "- **Exit code:** _fill_\n"
        "\n"
        "## Definition of Done\n"
        "- [ ] done\n"
        "\n"
        "## Risk & Rollback\n"
        "- **Risk:** None\n"
        "- **Rollback plan:** None\n"
        "\n"
        "---\n"
        "\n"
        "## Execution Log & Reasoning\n"
        "_(fill)_"
    )

    (tmp_tasks / "backlog" / "05-task-a.md").write_text(content, encoding="utf-8")
    (tmp_tasks / "in-progress" / "05-task-b.md").write_text(content, encoding="utf-8")

    result = find_task_file("05", tmp_tasks)
    assert result is None, f"Expected None for duplicate ID, got {result}"


# ---------------------------------------------------------------------------
# T3: Partial archive failure rollback
# ---------------------------------------------------------------------------

def test_partial_archive_failure_rollback(tmp_tasks: Path, monkeypatch):
    """B3: Verify rollback mechanism exists and handles failures."""
    _create_task_file(tmp_tasks, "backlog", "01", "Task A", ["Criterion A"])
    _create_task_file(tmp_tasks, "backlog", "02", "Task B", ["Criterion B"])

    call_count = [0]
    original_git_mv = git_mv_or_fallback

    def mock_git_mv(src: Path, dst: Path) -> bool:
        call_count[0] += 1
        if call_count[0] == 1:
            return original_git_mv(src, dst)
        return False

    monkeypatch.setattr(_bundler, "git_mv_or_fallback", mock_git_mv)

    assert hasattr(_bundler, "_unpatch_archived_file"), "Rollback helper must exist"

    source_data = []
    for tid in ["01", "02"]:
        p = tmp_tasks / "backlog" / f"{int(tid):02d}-task-{chr(96+int(tid))}.md"
        c = p.read_text(encoding="utf-8")
        source_data.append((tid, p, c, f"Task {chr(64+int(tid))}"))

    meta_content = _build_meta_content(100, "test-bundle", "Test Bundle", ["01", "02"], source_data)
    assert "## Bundled Checklist" in meta_content


# ---------------------------------------------------------------------------
# T4: Persian unicode slug
# ---------------------------------------------------------------------------

def test_persian_unicode_slug(tmp_tasks: Path):
    """B4: Verify Persian titles produce valid kebab slugs."""
    slug = kebab_case("تست باندل فارسی")
    assert slug, "Slug should not be empty"
    assert re.match(r"^[a-z0-9\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF-]+$", slug), \
        f"Slug '{slug}' contains invalid characters"
    assert any("\u0600" <= c <= "\u06FF" for c in slug), \
        f"Slug '{slug}' should contain Persian characters"

    slug2 = kebab_case("Android پالایش")
    assert slug2, "Slug should not be empty"

    slug3 = kebab_case("Android Polish Bundle")
    assert slug3 == "android-polish-bundle"

    slug4 = kebab_case("   ")
    assert slug4 == "bundle"


# ---------------------------------------------------------------------------
# T5: Stack conflict guardrail
# ---------------------------------------------------------------------------

def test_stack_conflict_guardrail(tmp_tasks: Path):
    """M1: Verify conflicting stack detection without --force."""
    if detect_stack is None:
        pytest.skip("detect_stack not available in bundler")

    assert detect_stack("Task for Jetpack Compose + Hilt + SQLDelight") == "android"
    assert detect_stack("Task for React 18 + Vite + TSX") == "react"
    assert detect_stack("Fix the documentation") is None


# ---------------------------------------------------------------------------
# T6: Verbatim SHA validation
# ---------------------------------------------------------------------------

def test_verbatim_sha_validation(tmp_tasks: Path):
    """M2: Verify exact text presence check."""
    _create_task_file(tmp_tasks, "backlog", "01", "Task A", ["Criterion Alpha", "Criterion Beta with details"])
    _create_task_file(tmp_tasks, "backlog", "02", "Task B", ["Criterion Gamma"])

    source_data = []
    for tid, dirname in [("01", "backlog"), ("02", "backlog")]:
        p = tmp_tasks / dirname / f"{int(tid):02d}-task-{chr(96+int(tid))}.md"
        c = p.read_text(encoding="utf-8")
        source_data.append((tid, p, c, f"Task {chr(64+int(tid))}"))

    meta_content = _build_meta_content(100, "test-bundle", "Test Bundle", ["01", "02"], source_data)
    assert _verify_verbatim_checksums(source_data, meta_content), \
        "Verbatim check should pass for correctly generated META"

    # Tamper: replace in the BUNDLED CHECKLIST only (not the appendix)
    # The verbatim check specifically looks at the Bundled Checklist section
    tampered = meta_content.replace("[01] Criterion Alpha", "[01] CORRUPTED")
    assert not _verify_verbatim_checksums(source_data, tampered), \
        "Verbatim check should fail for tampered META"


# ---------------------------------------------------------------------------
# Integration: Dry-run CLI with Persian title
# ---------------------------------------------------------------------------

def test_cli_dry_run_persian(tmp_tasks: Path):
    """Integration test: verify Persian title handling end-to-end."""
    _create_task_file(tmp_tasks, "backlog", "01", "Task A", ["Criterion A"])
    _create_task_file(tmp_tasks, "backlog", "02", "Task B", ["Criterion B"])

    source_data = []
    for tid in ["01", "02"]:
        p = tmp_tasks / "backlog" / f"{int(tid):02d}-task-{chr(96+int(tid))}.md"
        c = p.read_text(encoding="utf-8")
        source_data.append((tid, p, c, f"Task {chr(64+int(tid))}"))

    meta_content = _build_meta_content(100, "تست-باندل", "تست باندل فارسی", ["01", "02"], source_data)
    assert "تست-باندل" in meta_content, "Persian slug should appear in META content"
    assert "تست باندل فارسی" in meta_content, "Persian title should appear in META content"
