"""Registry <-> skill-templates consistency (offline, Task 217).

Every skill named in prompts/fragments/07-agent_skills_registry.md must
have a matching skill-templates/<name>/SKILL.md whose frontmatter name
agrees, and the decision-migration skill must carry its workflow contract
(dry-run-first, scrub+verify, idempotent, report).
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "prompts" / "fragments" / "07-agent_skills_registry.md"


def _registry_names():
    text = REGISTRY.read_text(encoding="utf-8")
    return re.findall(r"^- \*\*([a-z0-9-]+)\*\*:", text, re.MULTILINE)


def _frontmatter_name(skill_dir: Path) -> str:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r"^name:\s*([a-z0-9-]+)\s*$", text, re.MULTILINE)
    assert m, f"{skill_dir}: no frontmatter name:"
    return m.group(1)


def test_every_registry_skill_has_matching_template():
    names = _registry_names()
    assert names, "registry lists no skills"
    for name in names:
        d = ROOT / "skill-templates" / name
        assert (d / "SKILL.md").is_file(), f"missing template for {name}"
        assert _frontmatter_name(d) == name, f"frontmatter mismatch for {name}"


def test_decision_migration_workflow_contract():
    text = (
        ROOT / "skill-templates" / "decision-migration" / "SKILL.md"
    ).read_text(encoding="utf-8")
    for required in (
        "Dry run first",
        "record_manager_decision",
        "sanitize_text",
        "verify_clean",
        "idempotent",
        "migrated / skipped",
    ):
        assert required in text, f"contract term missing: {required}"
    assert "standalone script" in text or "no standalone script" in text.lower()


def _migration_skill_text() -> str:
    """Return the decision-migration SKILL.md text under test."""
    return (
        ROOT / "skill-templates" / "decision-migration" / "SKILL.md"
    ).read_text(encoding="utf-8")


def test_migration_skill_has_explicit_approval_gate():
    """Dry run must STOP; only an explicit batch-approval phrase unlocks writes."""
    text = _migration_skill_text()
    assert "STOP" in text
    assert "explicit Manager batch-approval phrase" in text
    assert "NOT approved" in text


def test_migration_skill_has_dedup_precheck_and_provenance():
    """Idempotent reruns: pre-check migrated_from in target, skip-if-exists."""
    text = _migration_skill_text()
    assert "skip-if-exists" in text
    assert "migrated_from" in text


def test_migration_skill_forbids_invented_paths_and_source_edits():
    """Target path is never invented; source immutability must be proven."""
    text = _migration_skill_text()
    assert "Never invent, guess, or default the target path." in text
    assert "git status --porcelain" in text
