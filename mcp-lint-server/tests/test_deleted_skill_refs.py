"""Regression coverage for deleted-skill references in live instructions."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from server import _check_deleted_skill_refs


def test_deleted_skill_reference_is_reported_on_line_mentioning_readme() -> None:
    """A history-file mention must not hide a deleted skill in live text."""
    issues = _check_deleted_skill_refs(
        "Read README.md before using task-generator.",
        "agents/cognitive-executor.md",
    )

    assert any("task-generator" in issue for issue in issues)


def test_deleted_skill_reference_is_reported_on_skill_attribution_line() -> None:
    """Attribution wording must not exempt a deleted skill reference."""
    issues = _check_deleted_skill_refs(
        "Use task-generator skill from `task-generator` skill.",
        "agents/cognitive-executor.md",
    )

    assert any("task-generator" in issue for issue in issues)


def test_archive_path_excluded_for_deleted_skill(tmp_path) -> None:
    """Archived prompts are outside live scan scope (via lint_markdown filter)."""
    from server import lint_markdown

    text = "Load the task-generator skill here."
    live_dir = tmp_path / "agents"
    live_dir.mkdir(parents=True)
    live = live_dir / "live.md"
    live.write_text(text, encoding="utf-8")

    archive_dir = tmp_path / "prompts" / "archive"
    archive_dir.mkdir(parents=True)
    archived = archive_dir / "old.md"
    archived.write_text(text, encoding="utf-8")

    live_result = lint_markdown(str(live), project_root=str(tmp_path))
    assert "Deleted skill reference" in live_result

    archive_result = lint_markdown(str(archived), project_root=str(tmp_path))
    assert "Deleted skill reference" not in archive_result
