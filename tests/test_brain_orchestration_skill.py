# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
"""Contract gate for the brain-orchestration skill template (Task 423).

The skill must describe the platform without hard-coding HQ repository
paths: the portable-authority rule from the versioning-skill split applies
here too (skill-templates README portability invariant).
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skill-templates" / "brain-orchestration" / "SKILL.md"
REGISTRY = ROOT / "prompts" / "fragments" / "07-agent_skills_registry.md"


def test_frontmatter_name_matches_dir():
    text = SKILL.read_text(encoding="utf-8")
    assert re.search(r"^name: brain-orchestration$", text, re.MULTILINE)


def test_registry_lists_skill_without_plugin_literals():
    reg = REGISTRY.read_text(encoding="utf-8")
    line = next(
        l for l in reg.splitlines() if l.startswith("- **brain-orchestration**")
    )
    for banned in (
        "read_omitted_content",
        "compact_context",
        "goal_set",
        "smart-compact",
    ):
        assert banned not in line, f"plugin literal in registry line: {banned}"


def test_skill_covers_participants_seats_stages_gates():
    text = SKILL.read_text(encoding="utf-8")
    for token in (
        "Manager",
        "Brain",
        "Hands",
        "Software Architect",
        "UI/UX Designer",
        "Senior Programmer",
        "Project Planner",
        "Sprint Strategist",
        "QA Engineer",
        "Code Reviewer",
        "brain_turn",
        "plan",
        "implement",
        "qa",
        "review",
        "closure",
        "sprint",
        "planner",
        "brainstorm",
        "Approved for closure",
        "Zero-Autonomous-Commit",
        "[brain-output]",
        "output_address",
        "read_omitted_content",
        "Context-Map",
        "Seat Check",
    ):
        assert token in text, f"platform contract element missing from skill: {token}"


def test_skill_uses_portable_authority_wording():
    text = SKILL.read_text(encoding="utf-8")
    for token in (
        "deployed Brain Bridge runbook",
        "stage manifest",
        "authoritative contract",
        "On any conflict, the deployed contract wins",
    ):
        assert token in text, f"portable-authority wording missing: {token}"


def test_skill_hard_codes_no_hq_repository_paths():
    text = SKILL.read_text(encoding="utf-8")
    for banned in (
        "docs/brain-bridge.md",
        "mcp-brain-bridge/README.md",
        "prompts/stage-manifest.json",
    ):
        assert banned not in text, f"HQ repository path leaked into template: {banned}"
