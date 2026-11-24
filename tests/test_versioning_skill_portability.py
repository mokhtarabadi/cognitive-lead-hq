# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
"""Portable-core regression gate for the versioning skill (Task 423, code comment provenance only).

The skill template must stay project-agnostic: harness-specific names live
only in the clearly labeled Harness Profile section at the file end.
"""

import re
from pathlib import Path

SKILL = (
    Path(__file__).resolve().parent.parent
    / "skill-templates"
    / "versioning-and-release"
    / "SKILL.md"
)
FORBIDDEN_IN_CORE = [
    "AGENTS.md",
    "DESIGN.md",
    "tasks/",
    "system-prompt.md",
    "custom_context_",
]


def _split(text: str):
    m = re.search(r"^## Harness Profile", text, re.MULTILINE)
    assert m, "missing clearly labeled Harness Profile section"
    return text[: m.start()], text[m.start() :]


def _skill_text():
    return SKILL.read_text(encoding="utf-8")


def test_portable_core_has_no_harness_literals():
    core, _ = _split(_skill_text())
    offenders = [token for token in FORBIDDEN_IN_CORE if token in core]
    assert offenders == [], f"harness literals leaked into portable core: {offenders}"


def test_harness_profile_preserves_all_safeguards():
    _, profile = _split(_skill_text())
    for required in (
        "AGENTS.md",
        "DESIGN.md",
        "system-prompt.md",
        "tasks/",
        "custom_context_stage_and_inject_diff",
        "custom_context_unstage_files",
        "custom_context_commit_and_clean_task",
        "skip_add=True",
        "owner-gated",
    ):
        assert required in profile, (
            f"release safeguard missing from Harness Profile: {required}"
        )


def test_core_keeps_universal_release_rules():
    core, _ = _split(_skill_text())
    for required in (
        "MAJOR.MINOR.PATCH",
        "Parse-Then-Append",
        "Conventional Commits",
        "feat:",
        "fix:",
        "docs:",
        "refactor:",
        "chore:",
        "72 characters",
        "[Unreleased]",
    ):
        assert required in core, f"portable rule missing from core: {required}"


def test_core_commit_and_push_are_mechanism_gated():
    core, _ = _split(_skill_text())
    assert (
        "Never run raw `git add`, `git commit`, `git checkout`, or `git push`" in core
    )
    assert "Pushing to a remote is owner-gated" in core
