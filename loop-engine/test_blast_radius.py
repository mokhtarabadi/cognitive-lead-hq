"""Tests for blast_radius.py — Monorepo Blast-Radius Analyzer (Task 141).

Covers the public API (``extract_modified_paths``, ``discover_packages``,
``find_owning_package``, ``build_dependency_map``, ``calculate_affected_paths``)
and the ``ToolchainRunner`` workspace-scoping gate in verifier.py that consumes
the matrix (including the conservative fallback and the ``skip_unaffected``
rollback flag).
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from blast_radius import (
    _PSEUDO_MANIFEST,
    BlastRadiusMatrix,
    build_dependency_map,
    calculate_affected_paths,
    discover_packages,
    extract_modified_paths,
    find_owning_package,
)
from models import StackProfileConfig, StackToolchainConfig
from stacks import StackProfile
from verifier import ToolchainRunner

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


def write(path: Path, content: str = "") -> Path:
    """Write ``content`` to ``path`` (creating parents). Returns the path.

    Callers pass the FULL target path as the first argument (e.g.
    ``write(root / "package.json", body)``); the previous split-signature
    (root, rel, content) mis-parsed the content as a relative path and
    created a directory named after the file instead of the file itself.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def node_manifest(name: str, deps: dict | None = None, extra: dict | None = None) -> str:
    """Build a package.json body with optional dependency section + extra keys."""
    data: dict = {"name": name, "version": "1.0.0"}
    if deps:
        data["dependencies"] = deps
    if extra:
        data.update(extra)
    return json.dumps(data)


def py_manifest(name: str, deps: list | None = None,
                extra_text: str = "") -> str:
    """Build a pyproject.toml body with optional dependencies + extra TOML."""
    lines = ["[project]", f'name = "{name}"', 'version = "1.0.0"']
    if deps:
        lines.append("dependencies = [")
        for dep in deps:
            lines.append(f'    "{dep}",')
        lines.append("]")
    if extra_text:
        lines.append(extra_text)
    return "\n".join(lines)


def go_manifest(module: str, requires: list | None = None,
                replaces: list | None = None) -> str:
    """Build a go.mod body with optional require/replace blocks."""
    lines = [f"module {module}", "", "go 1.22"]
    if requires:
        lines.append("require (")
        for req in requires:
            lines.append(f"    {req} v1.0.0")
        lines.append(")")
    if replaces:
        lines.append("replace (")
        for rep in replaces:
            lines.append(f"    {rep}")
        lines.append(")")
    return "\n".join(lines)


def make_monorepo(root: Path) -> None:
    """Create a small polyglot monorepo fixture.

    Layout:
      package.json                 (root, name "hq-root", workspaces globs)
      packages/shared-schema/      (pyproject, named "shared-schema")
      services/service-a/          (package.json, depends on "shared-schema")
      services/service-b/          (pyproject, independent)
      apps/gateway/                (go.mod, module "hq/gateway", requires "shared-schema")
    """
    write(root / "package.json",
          node_manifest("hq-root", extra={"private": True,
                                          "workspaces": ["packages/*", "services/*"]}))
    write(root / "packages/shared-schema/pyproject.toml", py_manifest("shared-schema"))
    write(root / "packages/shared-schema/README.md", "shared schema docs")
    write(root / "services/service-a/package.json",
          node_manifest("service-a", {"shared-schema": "workspace:*"}))
    write(root / "services/service-a/index.ts", "import { x } from 'shared-schema'\n")
    write(root / "services/service-b/pyproject.toml", py_manifest("service-b"))
    write(root / "services/service-b/app.py", "print('b')\n")
    write(root / "apps/gateway/go.mod",
          go_manifest("hq/gateway", requires=["shared-schema"]))
    write(root / "apps/gateway/main.go", "package main\n")


# ---------------------------------------------------------------------------
# extract_modified_paths
# ---------------------------------------------------------------------------


def test_extract_modified_paths_returns_bside_deduped():
    diff = (
        "diff --git a/packages/shared-schema/types.py b/packages/shared-schema/types.py\n"
        "index 111..222 100644\n"
        "--- a/packages/shared-schema/types.py\n"
        "+++ b/packages/shared-schema/types.py\n"
        "@@ -1,7 +1,7 @@\n"
        "diff --git a/services/a/x.ts b/services/a/x.ts\n"
        "diff --git a/services/a/x.ts b/services/a/x.ts\n"  # duplicate b-side
    )
    paths = extract_modified_paths(diff)
    assert paths == ["packages/shared-schema/types.py", "services/a/x.ts"]


def test_extract_modified_paths_empty_or_malformed():
    assert extract_modified_paths("") == []
    assert extract_modified_paths(None) == []  # type: ignore[arg-type]
    assert extract_modified_paths("plain text without headers") == []


def test_extract_modified_paths_rename_uses_bside():
    diff = "diff --git a/old.py b/new.py\n"
    assert extract_modified_paths(diff) == ["new.py"]


# ---------------------------------------------------------------------------
# discover_packages
# ---------------------------------------------------------------------------


def test_discover_packages_polyglot_monorepo(tmp_path):
    root = tmp_path / "monorepo"
    make_monorepo(root)

    packages = discover_packages(root)

    # Root package first (path "."), then deterministic path order.
    assert [p.path for p in packages] == [
        ".", "apps/gateway", "packages/shared-schema",
        "services/service-a", "services/service-b",
    ]
    assert packages[0].name == "hq-root"
    assert packages[0].manifest == "package.json"
    by_path = {p.path: p for p in packages}
    assert by_path["packages/shared-schema"].name == "shared-schema"
    assert by_path["packages/shared-schema"].manifest == "pyproject.toml"
    assert by_path["apps/gateway"].name == "hq/gateway"
    assert by_path["apps/gateway"].manifest == "go.mod"
    assert by_path["services/service-a"].name == "service-a"
    assert by_path["services/service-b"].name == "service-b"


def test_discover_packages_prunes_noise_dirs(tmp_path):
    root = tmp_path / "monorepo"
    write(root / "package.json", node_manifest("root"))
    write(root / "packages/real/package.json", node_manifest("real"))
    # Noise dirs that must never become package boundaries.
    write(root / "node_modules/dep/package.json", node_manifest("dep"))
    write(root / ".venv/lib/py/site-packages/x/pyproject.toml", py_manifest("venv-x"))
    write(root / ".hidden/pkg/package.json", node_manifest("hidden"))

    paths = [p.path for p in discover_packages(root)]
    assert paths == [".", "packages/real"]
    assert "node_modules/dep" not in paths
    assert ".venv" not in paths
    assert ".hidden/pkg" not in paths


def test_discover_packages_workspaces_glob_pseudo_manifest(tmp_path):
    root = tmp_path / "monorepo"
    write(root / "package.json",
          node_manifest("root", extra={"workspaces": ["packages/*"]}))
    # A workspace dir WITHOUT any manifest file gains a pseudo-manifest entry.
    write(root / "packages/empty/README.md", "no manifest here")

    packages = discover_packages(root)
    by_path = {p.path: p for p in packages}
    assert "packages/empty" in by_path
    assert by_path["packages/empty"].name == "empty"
    assert by_path["packages/empty"].manifest == _PSEUDO_MANIFEST


def test_discover_packages_missing_root_returns_empty(tmp_path):
    assert discover_packages(tmp_path / "does-not-exist") == []


# ---------------------------------------------------------------------------
# find_owning_package
# ---------------------------------------------------------------------------


def test_find_owning_package_deepest_owner_wins(tmp_path):
    root = tmp_path / "monorepo"
    make_monorepo(root)
    packages = discover_packages(root)

    assert find_owning_package("packages/shared-schema/types.py", packages).name == "shared-schema"
    assert find_owning_package("packages/shared-schema/sub/deep.py", packages).name == "shared-schema"
    assert find_owning_package("apps/gateway/main.go", packages).name == "hq/gateway"


def test_find_owning_package_root_fallback(tmp_path):
    root = tmp_path / "monorepo"
    make_monorepo(root)
    packages = discover_packages(root)

    # A repo-root file is owned by the root package (".").
    assert find_owning_package("README.md", packages).name == "hq-root"


def test_find_owning_package_none_without_root_package(tmp_path):
    root = tmp_path / "monorepo"
    # No root manifest: only a nested package exists.
    write(root / "packages/a/package.json", node_manifest("a"))

    packages = discover_packages(root)
    assert find_owning_package("unowned.txt", packages) is None
    assert find_owning_package("packages/a/src.py", packages).name == "a"


# ---------------------------------------------------------------------------
# build_dependency_map
# ---------------------------------------------------------------------------


def test_build_dependency_map_polyglot_edges(tmp_path):
    root = tmp_path / "monorepo"
    make_monorepo(root)
    packages = discover_packages(root)

    dep_map = build_dependency_map(packages, root)
    by_pkg = {d.package: d for d in dep_map}

    # service-a depends on shared-schema via workspace:* protocol
    assert by_pkg["service-a"].depends_on == ["shared-schema"]
    # hq/gateway (go.mod) requires shared-schema — name-edge via require block
    assert by_pkg["hq/gateway"].depends_on == ["shared-schema"]
    # shared-schema itself has no local deps
    assert by_pkg["shared-schema"].depends_on == []
    # independent service-b
    assert by_pkg["service-b"].depends_on == []
    # root package has no local deps
    assert by_pkg["hq-root"].depends_on == []


def test_build_dependency_map_deterministic_order(tmp_path):
    root = tmp_path / "monorepo"
    make_monorepo(root)
    packages = discover_packages(root)

    dep_map = build_dependency_map(packages, root)
    # One entry per discovered package, in the same deterministic order as
    # discover_packages (root first, then path-sorted).
    assert [d.package for d in dep_map] == [p.name for p in packages]
    # Every entry has a sorted depends_on list.
    for d in dep_map:
        assert d.depends_on == sorted(d.depends_on)


def test_build_dependency_map_file_reference_resolves_local(tmp_path):
    root = tmp_path / "monorepo"
    write(root / "package.json", node_manifest("root"))
    write(root / "packages/lib-a/package.json", node_manifest("lib-a"))
    # lib-b depends on lib-a via a relative file: reference
    write(root / "packages/lib-b/package.json",
          node_manifest("lib-b", {"lib-a": "file:../lib-a"}))

    packages = discover_packages(root)
    dep_map = build_dependency_map(packages, root)
    by_pkg = {d.package: d for d in dep_map}

    assert by_pkg["lib-b"].depends_on == ["lib-a"]
    assert by_pkg["lib-a"].depends_on == []


# ---------------------------------------------------------------------------
# calculate_affected_paths
# ---------------------------------------------------------------------------


def test_calculate_affected_paths_shared_schema_closure(tmp_path):
    root = tmp_path / "monorepo"
    make_monorepo(root)

    matrix = calculate_affected_paths(
        ["packages/shared-schema/types.py"], root
    )

    assert matrix.modified_files == ["packages/shared-schema/types.py"]
    # Directly modified package PLUS transitive dependents (service-a,
    # hq/gateway both depend on shared-schema).
    assert matrix.affected_packages == [
        "hq/gateway", "service-a", "shared-schema",
    ]
    assert matrix.affected_paths == [
        "apps/gateway", "packages/shared-schema", "services/service-a",
    ]
    # service-b and the root are outside the reverse-dependency closure.
    assert matrix.unaffected_packages == ["hq-root", "service-b"]
    assert matrix.root_owned_files == []


def test_calculate_affected_paths_independent_package_only(tmp_path):
    root = tmp_path / "monorepo"
    make_monorepo(root)

    matrix = calculate_affected_paths(["services/service-b/app.py"], root)

    assert matrix.affected_packages == ["service-b"]
    assert matrix.affected_paths == ["services/service-b"]
    assert matrix.unaffected_packages == [
        "hq-root", "hq/gateway", "service-a", "shared-schema",
    ]
    assert matrix.root_owned_files == []


def test_calculate_affected_paths_root_owned_files(tmp_path):
    root = tmp_path / "monorepo"
    # Only a nested package exists — no root manifest.
    write(root / "packages/a/package.json", node_manifest("a"))
    write(root / "README.md", "# Docs\n")

    matrix = calculate_affected_paths(
        ["README.md", "packages/a/src.py"], root
    )

    # README.md belongs to no package → root_owned_files.
    assert matrix.root_owned_files == ["README.md"]
    assert matrix.affected_packages == ["a"]
    assert matrix.modified_files == ["README.md", "packages/a/src.py"]


def test_calculate_affected_paths_empty_modified_files(tmp_path):
    root = tmp_path / "monorepo"
    make_monorepo(root)

    matrix = calculate_affected_paths([], root)

    assert matrix.modified_files == []
    assert matrix.affected_packages == []
    assert matrix.affected_paths == []
    assert matrix.unaffected_packages == sorted([
        "hq-root", "hq/gateway", "shared-schema", "service-a", "service-b",
    ])
    assert matrix.root_owned_files == []


def test_calculate_affected_paths_result_is_matrix_model():
    matrix = calculate_affected_paths([], Path("."))
    # Type-level contract: always returns a BlastRadiusMatrix model instance.
    assert isinstance(matrix, BlastRadiusMatrix)


# ---------------------------------------------------------------------------
# ToolchainRunner blast-radius workspace scoping (LE-9)
# ---------------------------------------------------------------------------


def make_profile(lint_cmd, build_cmd, test_cmd, name="test-stack") -> StackProfile:
    cfg = StackProfileConfig(
        name=name,
        display_name=f"Test {name}",
        toolchain=StackToolchainConfig(
            lint_cmd=lint_cmd, build_cmd=build_cmd, test_cmd=test_cmd
        ),
    )
    return StackProfile(cfg)


def diff_for(*paths: str) -> str:
    """Build a minimal diff touching the given files."""
    return "".join(
        f"diff --git a/{p} b/{p}\n"
        f"index 111..222 100644\n"
        f"--- a/{p}\n"
        f"+++ b/{p}\n"
        f"@@ -1 +1 @@\n"
        f"-old\n"
        f"+new\n"
        for p in paths
    )


def test_runner_skips_unaffected_workspace(tmp_path):
    root = tmp_path / "monorepo"
    make_monorepo(root)
    profile = make_profile("echo lint", "echo build", "echo test")

    runner = ToolchainRunner(
        timeout_per_command=5.0,
        evidence_base_dir=tmp_path / "evidence",
        workspace_root=root,
        skip_unaffected=True,
    )
    # Diff touches service-b only; cwd is service-a → unaffected.
    result = runner.run_sync(
        profile, task_id=None, cwd=root / "services/service-a",
        diff_text=diff_for("services/service-b/app.py"),
    )

    assert result.passed is True
    assert all(c.skipped for c in result.commands)
    assert "Blast-radius scoping" in result.summary
    assert "unaffected" in result.summary
    # No actual toolchain command ran.
    assert all(c.command == "none" for c in result.commands)


def test_runner_runs_affected_workspace(tmp_path):
    root = tmp_path / "monorepo"
    make_monorepo(root)
    profile = make_profile("echo lint", "echo build", "echo test")

    runner = ToolchainRunner(
        timeout_per_command=5.0,
        evidence_base_dir=tmp_path / "evidence",
        workspace_root=root,
        skip_unaffected=True,
    )
    # Diff touches shared-schema; cwd is service-a → service-a is a
    # transitive dependent → verification MUST run.
    result = runner.run_sync(
        profile, task_id=None, cwd=root / "services/service-a",
        diff_text=diff_for("packages/shared-schema/types.py"),
    )

    assert result.passed is True
    assert all(not c.skipped for c in result.commands)
    assert "Blast-radius scoping" not in result.summary


def test_runner_skip_unaffected_flag_disable_runs_full(tmp_path):
    """Rollback flag: skip_unaffected=False always runs full toolchain."""
    root = tmp_path / "monorepo"
    make_monorepo(root)
    profile = make_profile("echo lint", "echo build", "echo test")

    runner = ToolchainRunner(
        timeout_per_command=5.0,
        evidence_base_dir=tmp_path / "evidence",
        workspace_root=root,
        skip_unaffected=False,
    )
    result = runner.run_sync(
        profile, task_id=None, cwd=root / "services/service-a",
        diff_text=diff_for("services/service-b/app.py"),
    )

    assert result.passed is True
    assert all(not c.skipped for c in result.commands)
    assert all(c.command == "echo lint" or c.command == "echo build"
               or c.command == "echo test" for c in result.commands)


def test_runner_no_cwd_is_conservative(tmp_path):
    root = tmp_path / "monorepo"
    make_monorepo(root)
    profile = make_profile("echo lint", "echo build", "echo test")

    runner = ToolchainRunner(
        timeout_per_command=5.0,
        evidence_base_dir=tmp_path / "evidence",
        workspace_root=root,
        skip_unaffected=True,
    )
    # No cwd → cannot prove the workspace → verification runs.
    result = runner.run_sync(
        profile, task_id=None, cwd=None,
        diff_text=diff_for("services/service-b/app.py"),
    )
    assert all(not c.skipped for c in result.commands)


def test_runner_non_monorepo_is_conservative(tmp_path):
    root = tmp_path / "plain"  # no manifests → not a proven monorepo
    root.mkdir(parents=True, exist_ok=True)
    profile = make_profile("echo lint", "echo build", "echo test")

    runner = ToolchainRunner(
        timeout_per_command=5.0,
        evidence_base_dir=tmp_path / "evidence",
        workspace_root=root,
        skip_unaffected=True,
    )
    result = runner.run_sync(
        profile, task_id=None, cwd=root,
        diff_text=diff_for("src/main.py"),
    )
    assert all(not c.skipped for c in result.commands)


def test_runner_root_owned_file_is_conservative(tmp_path):
    root = tmp_path / "monorepo"
    # Only a nested package — a root file belongs to no package.
    write(root / "packages/a/package.json", node_manifest("a"))
    write(root / "README.md", "# Docs\n")
    profile = make_profile("echo lint", "echo build", "echo test")

    runner = ToolchainRunner(
        timeout_per_command=5.0,
        evidence_base_dir=tmp_path / "evidence",
        workspace_root=root,
        skip_unaffected=True,
    )
    result = runner.run_sync(
        profile, task_id=None, cwd=root / "packages/a",
        diff_text=diff_for("README.md"),
    )
    assert all(not c.skipped for c in result.commands)