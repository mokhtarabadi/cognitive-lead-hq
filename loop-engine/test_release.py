"""Unit tests for SemVer release engine (Task 147)."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from release import ReleaseEngine


def test_major_bump_on_breaking():
    e = ReleaseEngine()
    assert e.calculate_next_version("1.2.3", ["bug", "breaking"]) == "2.0.0"


def test_minor_bump_on_feature():
    e = ReleaseEngine()
    assert e.calculate_next_version("1.2.3", ["bug", "feature"]) == "1.3.0"


def test_patch_bump_on_fix_only():
    e = ReleaseEngine()
    assert e.calculate_next_version("1.2.3", ["bug"]) == "1.2.4"
    assert e.calculate_next_version("1.2.3", ["fix"]) == "1.2.4"
    assert e.calculate_next_version("1.2.3", ["chore"]) == "1.2.4"


def test_changelog_entry_formatting(tmp_path):
    e = ReleaseEngine()
    entry = e.format_changelog_entry("1.3.0", "2026-09-04", [
        {"id": 1, "title": "Add X", "type": "feature"},
        {"id": 2, "title": "Fix Y", "type": "bug"},
    ])
    assert "## [1.3.0] - 2026-09-04" in entry
    assert "### Added" in entry
    assert "### Fixed" in entry


def test_parse_then_append_insertion(tmp_path):
    e = ReleaseEngine()
    p = tmp_path / "CHANGELOG.md"
    p.write_text("# Changelog\n\n## [Unreleased]\n\nOld\n", encoding="utf-8")
    e.update_changelog(p, "## [1.2.4] - 2026-09-04\n\n### Fixed\n- Z\n")
    text = p.read_text(encoding="utf-8")
    assert text.index("## [Unreleased]") < text.index("## [1.2.4]")
    assert "Old" in text


def test_zac_safe_dry_run_tag():
    e = ReleaseEngine()
    out = e.create_git_tag("9.9.9", dry_run=True)
    assert out == "[dry-run] Would create git tag v9.9.9"
