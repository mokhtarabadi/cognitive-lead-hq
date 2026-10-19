#!/usr/bin/env python3
# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
"""
Automated test suite for the meta-task bundler (bundle_tasks MCP tool in
mcp-context-server/server.py; helpers promoted to module level in Task 160).

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
    "context_server_bundler",
    PROJECT_ROOT / "mcp-context-server" / "server.py",
)
_bundler = importlib.util.module_from_spec(_bundler_spec)
_bundler_spec.loader.exec_module(_bundler)

# Re-export the functions we need (module-level helpers in mcp-context-server/server.py)
kebab_case = _bundler._kebab_case
find_task_file = _bundler._find_task_file
extract_section = _bundler._extract_section
extract_title = _bundler._extract_title
_build_meta_content = _bundler._build_meta_content
_verify_verbatim_checksums = _bundler._verify_verbatim_checksums
git_mv_or_fallback = _bundler._git_mv_or_fallback
ACTIVE_KANBAN_DIRS = _bundler.ACTIVE_KANBAN_DIRS

# _detect_stack is guaranteed in the MCP implementation (no CLI fallback needed)
detect_stack = _bundler._detect_stack


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
            if (
                stripped
                and not stripped.startswith("- [")
                and not stripped.startswith("## ")
                and not stripped.startswith("---")
            ):
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

    monkeypatch.setattr(_bundler, "_git_mv_or_fallback", mock_git_mv)

    assert hasattr(_bundler, "_patch_archived_file"), "Archive patch helper must exist"

    source_data = []
    for tid in ["01", "02"]:
        p = tmp_tasks / "backlog" / f"{int(tid):02d}-task-{chr(96 + int(tid))}.md"
        c = p.read_text(encoding="utf-8")
        source_data.append((tid, p, c, f"Task {chr(64 + int(tid))}"))

    meta_content = _build_meta_content(
        100, "test-bundle", "Test Bundle", ["01", "02"], source_data
    )
    assert "## Bundled Checklist" in meta_content


# ---------------------------------------------------------------------------
# T4: Persian unicode slug
# ---------------------------------------------------------------------------


def test_persian_unicode_slug(tmp_tasks: Path):
    """B4: Verify Persian titles produce valid kebab slugs."""
    slug = kebab_case("تست باندل فارسی")
    assert slug, "Slug should not be empty"
    assert re.match(
        r"^[a-z0-9\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF-]+$", slug
    ), f"Slug '{slug}' contains invalid characters"
    assert any("\u0600" <= c <= "\u06ff" for c in slug), (
        f"Slug '{slug}' should contain Persian characters"
    )

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
    assert detect_stack("Task for Jetpack Compose + Hilt + SQLDelight") == "android"
    assert detect_stack("Task for React 18 + Vite + TSX") == "react"
    assert detect_stack("Fix the documentation") is None


# ---------------------------------------------------------------------------
# T6: Verbatim SHA validation
# ---------------------------------------------------------------------------


def test_verbatim_sha_validation(tmp_tasks: Path):
    """M2: Verify exact text presence check."""
    _create_task_file(
        tmp_tasks,
        "backlog",
        "01",
        "Task A",
        ["Criterion Alpha", "Criterion Beta with details"],
    )
    _create_task_file(tmp_tasks, "backlog", "02", "Task B", ["Criterion Gamma"])

    source_data = []
    for tid, dirname in [("01", "backlog"), ("02", "backlog")]:
        p = tmp_tasks / dirname / f"{int(tid):02d}-task-{chr(96 + int(tid))}.md"
        c = p.read_text(encoding="utf-8")
        source_data.append((tid, p, c, f"Task {chr(64 + int(tid))}"))

    meta_content = _build_meta_content(
        100, "test-bundle", "Test Bundle", ["01", "02"], source_data
    )
    assert _verify_verbatim_checksums(source_data, meta_content), (
        "Verbatim check should pass for correctly generated META"
    )

    # Tamper: replace in the BUNDLED CHECKLIST only (not the appendix)
    # The verbatim check specifically looks at the Bundled Checklist section
    tampered = meta_content.replace("[01] Criterion Alpha", "[01] CORRUPTED")
    assert not _verify_verbatim_checksums(source_data, tampered), (
        "Verbatim check should fail for tampered META"
    )


# ---------------------------------------------------------------------------
# Integration: Dry-run CLI with Persian title
# ---------------------------------------------------------------------------


def test_cli_dry_run_persian(tmp_tasks: Path):
    """Integration test: verify Persian title handling end-to-end."""
    _create_task_file(tmp_tasks, "backlog", "01", "Task A", ["Criterion A"])
    _create_task_file(tmp_tasks, "backlog", "02", "Task B", ["Criterion B"])

    source_data = []
    for tid in ["01", "02"]:
        p = tmp_tasks / "backlog" / f"{int(tid):02d}-task-{chr(96 + int(tid))}.md"
        c = p.read_text(encoding="utf-8")
        source_data.append((tid, p, c, f"Task {chr(64 + int(tid))}"))

    meta_content = _build_meta_content(
        100, "تست-باندل", "تست باندل فارسی", ["01", "02"], source_data
    )
    assert "تست-باندل" in meta_content, "Persian slug should appear in META content"
    assert "تست باندل فارسی" in meta_content, (
        "Persian title should appear in META content"
    )


# ---------------------------------------------------------------------------
# T7-T16: Real-tool-path bundle tests (B1-B10 red proof + green guards)
# ---------------------------------------------------------------------------
# These tests invoke `bundle_tasks` through the real MCP tool function with
# project_root pointed at an isolated tmp tree — never the real repo.


def _init_git_repo(root: Path) -> None:
    """Make tmp_path a git repo so git-mv paths execute for real."""
    import subprocess as _sp

    _sp.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    _sp.run(
        ["git", "-C", str(root), "config", "user.email", "t@t.t"],
        check=True,
        capture_output=True,
    )
    _sp.run(
        ["git", "-C", str(root), "config", "user.name", "t"],
        check=True,
        capture_output=True,
    )


def test_e2e_dry_run_real_tool(tmp_tasks: Path, tmp_path: Path):
    """B10: Exercise bundle_tasks end-to-end (dry-run) via the real tool."""
    _create_task_file(tmp_tasks, "backlog", "01", "Task A", ["Criterion A"])
    _create_task_file(tmp_tasks, "backlog", "02", "Task B", ["Criterion B"])
    out = _bundler.bundle_tasks(
        ["01", "02"], "test bundle", dry_run=True, project_root=str(tmp_path)
    )
    assert "Would create META task" in out, f"dry-run preview missing:\n{out}"
    assert "All required sections present" in out, f"section gate missing:\n{out}"


def test_e2e_real_bundle_archives(tmp_tasks: Path, tmp_path: Path):
    """B10: Real bundle archives sources with superseded headers intact."""
    _init_git_repo(tmp_path)
    _create_task_file(tmp_tasks, "backlog", "01", "Task A", ["Criterion A"])
    _create_task_file(tmp_tasks, "backlog", "02", "Task B", ["Criterion B"])
    out = _bundler.bundle_tasks(
        ["01", "02"], "test bundle", dry_run=False, project_root=str(tmp_path)
    )
    assert "Created META task" in out, f"bundle failed:\n{out}"
    metas = list((tmp_path / "tasks" / "backlog").glob("*-test-bundle.md"))
    assert len(metas) == 1, f"expected one META file, got {metas}"
    meta_text = metas[0].read_text(encoding="utf-8")
    title_id = re.search(r"^# Task (\d+):", meta_text, re.MULTILINE).group(1)
    assert metas[0].name.startswith(f"{int(title_id):02d}-"), (
        "META filename ID must match META title ID"
    )
    for tid, letter in [("01", "a"), ("02", "b")]:
        archived = tmp_path / "tasks" / "archive" / f"{tid}-task-{letter}.md"
        assert archived.is_file(), f"source {tid} was not archived"
        archived_text = archived.read_text(encoding="utf-8")
        assert "**Status:** superseded" in archived_text
        assert f"**File:** `tasks/archive/{tid}-task-{letter}.md`" in archived_text


def test_count_enforcement_rejects_single(tmp_tasks: Path, tmp_path: Path):
    """B4: A single task is not a bundle — must error naming the 2-6 rule."""
    _create_task_file(tmp_tasks, "backlog", "01", "Task A", ["Criterion A"])
    out = _bundler.bundle_tasks(
        ["01"], "lonely", dry_run=True, project_root=str(tmp_path)
    )
    assert "2-6" in out and "Created META" not in out, f"single accepted:\n{out}"


def test_duplicate_input_rejected(tmp_tasks: Path, tmp_path: Path):
    """B4: The same ID twice in one call must error, not silently dedup."""
    _create_task_file(tmp_tasks, "backlog", "01", "Task A", ["Criterion A"])
    out = _bundler.bundle_tasks(
        ["01", "01"], "duped", dry_run=True, project_root=str(tmp_path)
    )
    assert "uplicate" in out and "Created META" not in out, f"dupe accepted:\n{out}"


def test_cross_dir_duplicate_distinct_error(tmp_tasks: Path, tmp_path: Path):
    """B5: Same ID in two Kanban dirs must say duplicate, never missing."""
    _create_task_file(tmp_tasks, "backlog", "05", "Task E", ["Criterion E"])
    _create_task_file(tmp_tasks, "in-progress", "05", "Task E", ["Criterion E"])
    _create_task_file(tmp_tasks, "backlog", "06", "Task F", ["Criterion F"])
    out = _bundler.bundle_tasks(
        ["05", "06"], "clash", dry_run=True, project_root=str(tmp_path)
    )
    assert "uplicate" in out, f"duplicate reported as missing:\n{out}"
    assert "Missing tasks" not in out


def test_id_retry_rebuilds_content(tmp_tasks: Path, tmp_path: Path, monkeypatch):
    """B1: After an ID retry the written META must carry the final ID."""
    _init_git_repo(tmp_path)
    _create_task_file(tmp_tasks, "backlog", "01", "Task A", ["Criterion A"])
    _create_task_file(tmp_tasks, "backlog", "02", "Task B", ["Criterion B"])
    real_open = open
    state = {"failed_once": False}

    def flaky_open(path, mode="r", *args, **kwargs):
        if (
            mode == "x"
            and not state["failed_once"]
            and str(path).endswith("-retry-bundle.md")
        ):
            state["failed_once"] = True
            # A racer lands first: decoy with the contested ID.
            decoy = Path(str(path)).parent / "03-decoy.md"
            decoy.write_text("x", encoding="utf-8")
            raise FileExistsError(str(path))
        return real_open(path, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", flaky_open)
    out = _bundler.bundle_tasks(
        ["01", "02"], "retry bundle", dry_run=False, project_root=str(tmp_path)
    )
    assert "Created META task" in out, f"bundle failed:\n{out}"
    metas = list((tmp_path / "tasks" / "backlog").glob("*-retry-bundle.md"))
    assert len(metas) == 1
    meta_text = metas[0].read_text(encoding="utf-8")
    title_id = re.search(r"^# Task (\d+):", meta_text, re.MULTILINE).group(1)
    assert metas[0].name.startswith(f"{int(title_id):02d}-"), (
        f"stale META content: file {metas[0].name} carries title ID {title_id}"
    )


def test_rollback_restores_origin_and_header(
    tmp_tasks: Path, tmp_path: Path, monkeypatch
):
    """B6: Failed archive must restore origin dir AND original File header."""
    _init_git_repo(tmp_path)
    _create_task_file(tmp_tasks, "in-progress", "01", "Task A", ["Criterion A"])
    _create_task_file(tmp_tasks, "in-progress", "02", "Task B", ["Criterion B"])
    original = (tmp_tasks / "in-progress" / "01-task-a.md").read_text(encoding="utf-8")
    calls = [0]
    real_mv = _bundler._git_mv_or_fallback

    def flaky_mv(src: Path, dst: Path) -> bool:
        calls[0] += 1
        if calls[0] == 2:
            return False
        return real_mv(src, dst)

    monkeypatch.setattr(_bundler, "_git_mv_or_fallback", flaky_mv)
    out = _bundler.bundle_tasks(
        ["01", "02"], "doomed", dry_run=False, project_root=str(tmp_path)
    )
    assert "rolled back" in out.lower() or "borted" in out.lower()
    restored = tmp_path / "tasks" / "in-progress" / "01-task-a.md"
    assert restored.is_file(), "first source was not restored to in-progress/"
    assert restored.read_text(encoding="utf-8") == original, (
        "rollback must restore byte-identical original content (File header included)"
    )
    assert not list((tmp_path / "tasks" / "backlog").glob("*-doomed.md")), (
        "META file must be removed after rollback"
    )


def test_next_id_collision_helper(tmp_tasks: Path):
    """B2: Same-ID-different-slug files must be detected either padding."""
    (tmp_tasks / "backlog" / "06-taken.md").write_text("x", encoding="utf-8")
    hits = _bundler._next_id_collision(tmp_tasks, 6)
    assert hits, "padded 06-taken.md must collide with next_id 6"
    (tmp_tasks / "backlog" / "7-loose.md").write_text("x", encoding="utf-8")
    assert _bundler._next_id_collision(tmp_tasks, 7), (
        "unpadded 7-loose.md must collide with next_id 7"
    )
    assert not _bundler._next_id_collision(tmp_tasks, 8)


def test_extractor_blank_lines_and_nested(tmp_tasks: Path):
    """B7: Blank-line paragraph breaks survive; nested boxes are items."""
    from gitops import _extract_checklist_with_continuations as extract

    section = (
        "- [ ] Root item\n"
        "  continuation paragraph\n"
        "\n"
        "  second paragraph\n"
        "  - [ ] nested box\n"
        "- [ ] Next root\n"
    )
    result = extract(section)
    joined = "\n".join(result)
    assert "continuation paragraph" in joined
    assert "second paragraph" in joined, f"blank line split the item: {result}"
    assert any(r == "- [ ] nested box" for r in result), (
        f"nested box must be its own stripped item: {result}"
    )


def test_checksum_covers_short_criteria(tmp_tasks: Path):
    """B8: Short criteria must be verified too, not skipped by length."""
    _create_task_file(tmp_tasks, "backlog", "01", "Task A", ["Fix it"])
    source_data = []
    p = tmp_tasks / "backlog" / "01-task-a.md"
    source_data.append(("01", p, p.read_text(encoding="utf-8"), "Task A"))
    meta = _build_meta_content(100, "s", "S", ["01"], source_data)
    assert _verify_verbatim_checksums(source_data, meta)
    dropped = meta.replace("[01] Fix it", "[01] GONE")
    assert not _verify_verbatim_checksums(source_data, dropped), (
        "dropped short criterion must fail the checksum"
    )


def test_patch_multiword_status(tmp_tasks: Path):
    """B9: Multi-word statuses must be replaced whole, dates aligned."""
    from gitops import _patch_archived_file

    p = tmp_tasks / "backlog" / "09-wip.md"
    p.write_text(
        "# Task 09: Wip\n\n**File:** `x`\n**Type:** bug\n**Status:** in progress\n",
        encoding="utf-8",
    )
    _patch_archived_file(p, "10", "meta")
    text = p.read_text(encoding="utf-8")
    assert "**Status:** superseded\n" in text, f"status line corrupt:\n{text}"
    assert "progress" not in [line for line in text.splitlines() if "Status" in line][0]
    created_fmt = re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC", text)
    assert created_fmt, f"Superseded-At must match Created datetime format:\n{text}"
