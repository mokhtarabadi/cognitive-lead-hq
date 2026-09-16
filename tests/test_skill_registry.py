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
    """Target path resolves from ordered known sources only; source immutability must be proven."""
    text = _migration_skill_text()
    assert "lookup, never invent" in text
    assert "ONLY if that directory already exists" in text
    assert "HALT and ask the Manager for the target path" in text
    assert "git status --porcelain" in text


def _template_text(name: str) -> str:
    return (ROOT / "skill-templates" / name / "SKILL.md").read_text(encoding="utf-8")


def test_testing_strategy_skill_contract():
    text = _template_text("testing-strategy")
    for required in (
        "RED",
        "GREEN",
        "REFACTOR",
        "Diff coverage",
        "Error paths",
        "Test-Placement Map",
        "Lite-Mode Exemption",
    ):
        assert required in text, f"contract term missing: {required}"


def test_database_migration_skill_contract():
    text = _template_text("database-migration")
    for required in (
        "No raw DDL",
        "db push",
        "Alembic",
        "Prisma",
        "Flyway",
        "Drift Check",
    ):
        assert required in text, f"contract term missing: {required}"


def test_hexagonal_expansion_contract():
    py = _template_text("python-fastapi")
    assert "Zero-Framework Core" in py
    assert "Protocol" in py
    node = _template_text("node-hexagonal-api")
    for required in (
        "Zero-Framework Core",
        "strict",
        "container.ts",
        "vitest",
    ):
        assert required in node, f"contract term missing: {required}"
    reg = REGISTRY.read_text(encoding="utf-8")
    assert "node-hexagonal-api" in reg
    stacks = (ROOT / "stacks" / "node-ts.yaml").read_text(encoding="utf-8")
    assert "node-hexagonal-api" in stacks


def test_opencode_init_skill_contract():
    text = _template_text("opencode-init")
    for required in (
        "validate-opencode.py",
        "flat map",
        "named map",
        "default_agent",
        "{env:",
        "git commit",
        "deny",
        "Never edit global config",
    ):
        assert required in text, f"contract term missing: {required}"
    reg = REGISTRY.read_text(encoding="utf-8")
    assert "opencode-init" in reg
    refs = ROOT / "skill-templates" / "opencode-init" / "references"
    assert (refs / "runtime-matrix.md").is_file()
    assert (refs / "examples" / "golden-opencode.json").is_file()


def test_validate_opencode_script():
    import json
    import subprocess

    script = (
        ROOT / "skill-templates" / "opencode-init" / "scripts" / "validate-opencode.py"
    )
    golden = (
        ROOT
        / "skill-templates"
        / "opencode-init"
        / "references"
        / "examples"
        / "golden-opencode.json"
    )

    def run(cfg):
        p = ROOT / ".tmp-validate-check.json"
        p.write_text(json.dumps(cfg), encoding="utf-8")
        try:
            r = subprocess.run(
                ["python3", str(script), str(p)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return r.returncode, r.stdout
        finally:
            p.unlink(missing_ok=True)

    base = json.loads(golden.read_text(encoding="utf-8"))
    assert run(base) == (0, ""), "golden file must validate clean"
    v2 = dict(base)
    v2["permissions"] = [{"permission": "bash", "pattern": "*", "decision": "deny"}]
    code, out = run(v2)
    assert code == 1 and "permissions[]" in out
    no_zac = json.loads(json.dumps(base))
    del no_zac["permission"]["bash"]["git push *"]
    code, out = run(no_zac)
    assert code == 1 and "git push *" in out
    secret = json.loads(json.dumps(base))
    secret["lsp"] = {"pyright": {"command": ["pyright"],
                                 "env": {"KEY": "sk-live-abc123"}}}
    code, out = run(secret)
    assert code == 1 and "placeholder" in out


def _run_validator(cfg=None, raw=None):
    import json
    import subprocess

    script = (
        ROOT / "skill-templates" / "opencode-init" / "scripts" / "validate-opencode.py"
    )
    p = ROOT / ".tmp-validate-check.json"
    p.write_text(raw if raw is not None else json.dumps(cfg), encoding="utf-8")
    try:
        r = subprocess.run(
            ["python3", str(script), str(p)],
            capture_output=True, text=True, timeout=30,
        )
        return r.returncode, r.stdout
    finally:
        p.unlink(missing_ok=True)


def _fresh_golden():
    import json

    golden = (
        ROOT
        / "skill-templates"
        / "opencode-init"
        / "references"
        / "examples"
        / "golden-opencode.json"
    )
    return json.loads(golden.read_text(encoding="utf-8"))


def test_validate_lsp_v2_keys_rejected():
    for bad_lsp in ({"enabled": True}, {"extensions": ["py"]}, {"python": True}):
        cfg = _fresh_golden()
        cfg["lsp"] = bad_lsp
        code, out = _run_validator(cfg)
        assert code == 1 and "lsp" in out.lower()


def test_validate_lsp_wrapper_rejected():
    cfg = _fresh_golden()
    cfg["lsp"] = {"language-server": {"typescript": {"command": ["typescript-language-server", "--stdio"]}}}
    code, out = _run_validator(cfg)
    assert code == 1 and "language-server" in out
    cfg = _fresh_golden()
    cfg["lsp"] = {"pyright": {"command": ["pyright"], "environment": {"K": "{env:K}"}}}
    code, out = _run_validator(cfg)
    assert code == 1 and "env" in out


def test_validate_lsp_null_empty_and_valid():
    cfg = _fresh_golden()
    cfg["lsp"] = {"py": None}
    assert _run_validator(cfg)[0] == 1
    cfg = _fresh_golden()
    cfg["lsp"] = {"py": {"command": []}}
    code, out = _run_validator(cfg)
    assert code == 1 and "command" in out.lower()
    cfg = _fresh_golden()
    cfg["lsp"] = {"py": {}}
    assert _run_validator(cfg)[0] == 1
    cfg = _fresh_golden()
    cfg["lsp"] = {"pyright": {"command": ["pyright"]}}
    assert _run_validator(cfg) == (0, "")
    cfg = _fresh_golden()
    cfg["lsp"] = {"pyright": {"command": ["pyright"],
                              "extensions": [".py"],
                              "env": {"KEY": "{env:KEY}"}}}
    assert _run_validator(cfg) == (0, "")
    cfg = _fresh_golden()
    cfg["lsp"] = {"pyright": {"disabled": True}}
    assert _run_validator(cfg) == (0, "")
    cfg = _fresh_golden()
    cfg["lsp"] = True
    assert _run_validator(cfg) == (0, "")
    cfg = _fresh_golden()
    cfg["lsp"] = None
    assert _run_validator(cfg) == (0, "")
    cfg = _fresh_golden()
    cfg["lsp"] = {}
    assert _run_validator(cfg) == (0, "")


def test_validate_formatter_named_map():
    cfg = _fresh_golden()
    cfg["formatter"] = {"command": ["mvn"], "extensions": [".java"]}
    code, out = _run_validator(cfg)
    assert code == 1 and "named map" in out
    cfg = _fresh_golden()
    cfg["formatter"] = {"spotless-java": {"command": ["mvn", "spotless:apply"],
                                          "extensions": [".java"]}}
    assert _run_validator(cfg) == (0, "")
    cfg = _fresh_golden()
    cfg["formatter"] = False
    assert _run_validator(cfg) == (0, "")


def test_validate_plugin_env_secret_rules():
    cfg = _fresh_golden()
    cfg["plugin"] = ["my-plugin"]
    code, out = _run_validator(cfg)
    assert code == 1 and "plugin" in out and "global-only" in out
    cfg = _fresh_golden()
    cfg["plugin"] = [{"source": "my-plugin", "environment": {"KEY": "{env:KEY}"}}]
    code, out = _run_validator(cfg)
    assert code == 1 and "plugin" in out


def test_validate_invented_values_expanded():
    for bad in (
        "foo-srv", "dummy", "placeholder-x", "sample agent",
        "TODO", "changeme", "xxx", "your-value-here", "example-plugin",
    ):
        cfg = _fresh_golden()
        cfg["default_agent"] = bad
        assert _run_validator(cfg)[0] == 1, bad
    cfg = _fresh_golden()
    cfg["default_agent"] = "general"
    assert _run_validator(cfg) == (0, "")
    for field in ("instructions", "formatter", "theme", "agents_dir"):
        cfg = _fresh_golden()
        cfg[field] = "dummy-value"
        code, out = _run_validator(cfg)
        assert code == 1 and field in out, field
    cfg = _fresh_golden()
    cfg["instructions"] = ["AGENTS.md", "docs/samples.md"]
    assert _run_validator(cfg) == (0, "")


def test_validate_mcp_rejected_global_only():
    cfg = _fresh_golden()
    cfg["mcp"] = {"srv": {"type": "local", "command": ["node", "server.js"],
                          "environment": {"KEY": "{env:KEY}"}}}
    code, out = _run_validator(cfg)
    assert code == 1 and "global-only" in out


def test_validate_partial_zac_rejected():
    cfg = _fresh_golden()
    del cfg["permission"]["bash"]["git commit"]
    code, out = _run_validator(cfg)
    assert code == 1 and "git commit" in out


def test_validate_malformed_inputs_fail_closed():
    import subprocess

    script = (
        ROOT / "skill-templates" / "opencode-init" / "scripts" / "validate-opencode.py"
    )
    r = subprocess.run(
        ["python3", str(script), str(ROOT / ".tmp-does-not-exist.json")],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 1
    assert _run_validator(raw="")[0] == 1
    assert _run_validator(raw="[]")[0] == 1
    cfg = _fresh_golden()
    cfg["default_agent"] = ""
    code, out = _run_validator(cfg)
    assert code == 1 and "default_agent" in out


def test_validate_opencode_positives():
    cfg = _fresh_golden()
    assert _run_validator(cfg) == (0, "")
    cfg = _fresh_golden()
    del cfg["$schema"]
    assert _run_validator(cfg) == (0, "")
    cfg = _fresh_golden()
    cfg["lsp"] = {"pyright": {"command": ["pyright"]}}
    assert _run_validator(cfg) == (0, "")
    cfg = _fresh_golden()
    cfg["formatter"] = {"spotless-java": {"command": ["mvn", "spotless:apply"],
                                          "extensions": [".java"]}}
    assert _run_validator(cfg) == (0, "")
