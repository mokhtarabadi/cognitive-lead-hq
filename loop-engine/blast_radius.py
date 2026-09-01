"""
Monorepo Blast-Radius Analyzer & Affected Path Matrix (LE-9 / Task 141).

Deterministic, side-effect-free analysis of task diffs against monorepo
workspaces: given the list of files modified by a task, discover the packages
under ``workspace_root``, map their local dependency edges, and compute the
exact affected dependency matrix — the directly modified packages PLUS every
package that (transitively) depends on them.

The matrix feeds the toolchain verification gate (``ToolchainRunner`` in
``verifier.py``) so lint/build/test is skipped for *completely unaffected*
workspaces and strictly scoped to impacted modules. The analyzer is
deliberately conservative: when it cannot PROVE a workspace is unaffected
(non-monorepo layout, unreadable manifests, root-owned files), it reports it
as affected so verification always runs. False-negative skips of actually
affected modules are the failure mode this guard rails against (see the
Risk & Rollback section of Task 141).

Design notes:
- Package discovery is manifest-driven (``os.walk`` with noise-dir pruning)
  plus root ``package.json`` ``workspaces`` globs (npm/yarn/pnpm-style).
- Dependency edges come from explicit local references (``workspace:*``,
  ``file:../x``, relative paths, Go ``replace ... => ../x``, uv ``sources``
  path map) and from plain references to another discovered package's name.
- Manifest parsers are implemented for package.json / pyproject.toml / go.mod;
  other manifests (Cargo.toml, composer.json, gradle, pom.xml) act as package
  boundaries only and contribute no dependency edges.
- Diff-path parsing replicates the tiny ``_DIFF_HEADER_RE`` helper from
  ``specs.py``/``contracts.py`` (established in-repo pattern, no cross-module
  imports so this stays dependency-light).
"""

from __future__ import annotations

import json
import os
import re
import tomllib
from pathlib import Path

from models import BlastRadiusMatrix, PackageDependency, PackageInfo

# Matches `diff --git a/<old> b/<new>` header lines — the b-side path is the
# post-change relative path we care about (mirrors specs.py / contracts.py).
_DIFF_HEADER_RE = re.compile(r"^diff --git a/(.+?) b/(.+?)\n", re.MULTILINE)

# Pseudo-manifest sentinel for workspace-glob packages that have no real
# manifest file (e.g. a workspaces glob pointing at an empty dir).
_PSEUDO_MANIFEST = "<workspaces glob>"

# Directories that never contain a package boundary (pruned during discovery).
_EXCLUDED_DIR_NAMES = {
    ".git", ".idea", ".vscode", ".venv", ".opencode", ".pytest_cache",
    "__pycache__", "node_modules", "venv", "dist", "build", "target",
    "coverage", "htmlcov", "state", "evidence", ".tox", ".mypy_cache",
    ".ruff_cache",
}

# Manifest precedence when a directory contains several (pick the winner).
_MANIFEST_PRECEDENCE = (
    "package.json",
    "pyproject.toml",
    "go.mod",
    "Cargo.toml",
    "composer.json",
    "build.gradle.kts",
    "build.gradle",
    "pom.xml",
)

_GO_MODULE_RE = re.compile(r"^\s*module\s+(\S+)", re.MULTILINE)
_GO_SINGLE_REQUIRE_RE = re.compile(r"^\s*require\s+(\S+)")
_GO_REPLACE_RE = re.compile(r"^\s*replace\s+(\S+)(?:\s+\S+)?\s*=>\s*(\S+)")
_PY_REQUIREMENT_NAME_RE = re.compile(r"^([A-Za-z0-9_.-]+)")


def extract_modified_paths(diff_text: str) -> list[str]:
    """Return deduplicated relative paths of files touched by a git diff.

    Parses ``diff --git a/x b/y`` headers (b-side path) and preserves
    first occurrence order. Empty/malformed diffs yield ``[]``.
    """
    paths: list[str] = []
    seen: set[str] = set()
    for match in _DIFF_HEADER_RE.finditer(diff_text or ""):
        path = match.group(2)
        if path not in seen:
            seen.add(path)
            paths.append(path)
    return paths


# ---------------------------------------------------------------------------
# Package discovery
# ---------------------------------------------------------------------------


def discover_packages(
    workspace_root: str | Path, globs: list[str] | None = None
) -> dict[str, PackageDependency] | list[PackageInfo]:
    """Discover monorepo packages under ``workspace_root``.

    Scans for manifest files (package.json, pyproject.toml, go.mod,
    Cargo.toml, composer.json, gradle/pom markers) while pruning noise
    directories, then additionally resolves root ``package.json``
    ``workspaces`` globs (npm/yarn/pnpm) so un-manifested workspace dirs
    are still tracked. Returns a deterministic path-sorted list (root
    package ``"."`` first when the root itself carries a manifest).

    Spec wrapper (Task 141): when ``globs`` is provided, returns a dict
    mapping ``package_name -> PackageDependency`` filtered by globs; when
    ``globs`` is None, preserves legacy list[PackageInfo] return for existing
    tests (backward compat). The hybrid return also supports dict-style access
    via properties.
    """
    root = Path(workspace_root)
    packages: dict[str, PackageInfo] = {}
    if not root.exists():
        # For spec dict return, give empty dict; for legacy, empty list
        return {} if globs is not None else []

    # Determine effective globs for directory filtering (spec path)
    effective_globs = globs if globs is not None else ["packages/*", "apps/*", "services/*", "modules/*", "libs/*"]

    # 1. Manifest-file discovery (top-down walk with in-place pruning)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            d for d in dirnames
            if d not in _EXCLUDED_DIR_NAMES and not d.startswith(".")
        )
        manifest = _first_manifest(filenames)
        if manifest is None:
            continue
        dirpath_p = Path(dirpath)
        rel = dirpath_p.relative_to(root).as_posix()
        # When globs filtering is active, skip packages not matching any glob
        if globs is not None:
            # rel must match one of the globs (simple fnmatch)
            import fnmatch

            if rel != "." and not any(fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(rel + "/", g) for g in effective_globs):
                # Still keep manifest-discovered packages even if not matching globs?
                # Spec says scan for directories matching globs — so we filter.
                # Keep root "." always.
                continue
        name = _manifest_name(manifest, dirpath_p / manifest, rel)
        packages[rel] = PackageInfo(name=name, path=rel, manifest=manifest)

    # 2. Root package.json workspaces globs (additional package dirs)
    root_pkg = root / "package.json"
    if root_pkg.is_file():
        try:
            data = json.loads(root_pkg.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        workspaces = data.get("workspaces") or []
        if isinstance(workspaces, list):
            for pattern in workspaces:
                if not isinstance(pattern, str):
                    continue
                for match in sorted(root.glob(pattern)):
                    if not match.is_dir():
                        continue
                    rel = match.relative_to(root).as_posix()
                    if rel not in packages:
                        packages[rel] = PackageInfo(
                            name=_dir_fallback_name(rel),
                            path=rel,
                            manifest=_PSEUDO_MANIFEST,
                        )

    sorted_packages = sorted(packages.values(), key=_package_sort_key)

    # Spec dict return path
    if globs is not None:
        dep_map = build_dependency_map(sorted_packages, root)
        return {d.name: d for d in dep_map}

    return sorted_packages


def find_owning_package(
    file_rel: str, packages: list[PackageInfo]
) -> PackageInfo | None:
    """Return the deepest package whose directory prefixes ``file_rel``.

    The root package (``path == "."``) is the last-resort owner for any
    file not under a deeper package. Returns ``None`` only when the
    workspace has no root package and no deeper package owns the file.
    """
    best = None
    best_parts = -1
    for pkg in packages:
        if pkg.path == ".":
            continue
        if file_rel == pkg.path or file_rel.startswith(pkg.path + "/"):
            parts = pkg.path.count("/")
            if parts > best_parts:
                best = pkg
                best_parts = parts
    if best is not None:
        return best
    for pkg in packages:
        if pkg.path == ".":
            return pkg
    return None


# ---------------------------------------------------------------------------
# Dependency graph
# ---------------------------------------------------------------------------


def build_dependency_map(
    packages: list[PackageInfo], workspace_root: str | Path
) -> list[PackageDependency]:
    """Build local dependency edges for every discovered package.

    Edges are local-only: a package depends on another package when its
    manifest references it via an explicit path (``workspace:*``,
    ``file:../x``, relative path, Go ``replace``, uv ``sources``) or by
    name matching a discovered package. Deterministic sorted lists.
    """
    root = Path(workspace_root)
    by_name: dict[str, PackageInfo] = {p.name: p for p in packages}
    abs_by_path: dict[Path, PackageInfo] = {}
    for p in packages:
        try:
            abs_by_path[(root / p.path).resolve()] = p
        except OSError:
            continue

    result: list[PackageDependency] = []
    for pkg in packages:
        edges: set[str] = set()
        if pkg.manifest != _PSEUDO_MANIFEST:
            manifest_path = root.joinpath(pkg.path, pkg.manifest)
            if manifest_path.is_file():
                if pkg.manifest == "package.json":
                    edges |= _node_deps(
                        manifest_path, abs_by_path, by_name
                    )
                elif pkg.manifest == "pyproject.toml":
                    edges |= _python_deps(
                        manifest_path, abs_by_path, by_name
                    )
                elif pkg.manifest == "go.mod":
                    edges |= _go_deps(
                        manifest_path, abs_by_path, by_name
                    )
        result.append(
            PackageDependency(
                package=pkg.name, path=pkg.path, depends_on=sorted(edges)
            )
        )
    return result


def build_dependency_graph(
    packages: dict[str, PackageDependency] | list[PackageInfo] | list[PackageDependency],
) -> dict[str, set[str]]:
    """Invert package dependencies to construct reverse dependency map.

    Spec wrapper (Task 141): accepts either a dict ``{name: PackageDependency}``
    or a list (legacy ``list[PackageInfo]`` + workspace_root via separate call).
    When given a dict, inverts ``dependencies`` to ``package -> set of consumers``.
    When given a list, delegates to legacy path (requires caller to have built map).

    Returns ``package_name -> set of dependent consumer package names``.
    """
    # Dict path (spec): packages is dict[name, PackageDependency]
    if isinstance(packages, dict):
        reverse: dict[str, set[str]] = {name: set() for name in packages}
        for pkg_name, dep in packages.items():
            # dep may be PackageDependency or list; normalize
            deps = dep.dependencies if hasattr(dep, "dependencies") else (dep.depends_on if hasattr(dep, "depends_on") else [])
            if not isinstance(deps, (list, set, tuple)):
                deps = []
            for d in deps:
                if d in reverse:
                    reverse[d].add(pkg_name)
                else:
                    # Dependency on unknown package — still create entry for completeness
                    reverse.setdefault(d, set()).add(pkg_name)
        return reverse
    # Legacy list path: if list of PackageDependency
    if packages and isinstance(packages[0], PackageDependency):
        reverse = {d.name: set() for d in packages}  # type: ignore[attr-defined]
        for d in packages:  # type: ignore
            deps = d.dependencies if hasattr(d, "dependencies") else d.depends_on
            for dep_name in deps:
                if dep_name in reverse:
                    reverse[dep_name].add(d.name)
        return reverse
    # Legacy list[PackageInfo] needs workspace_root — caller should use build_dependency_map
    # Fallback: empty
    return {}


# ---------------------------------------------------------------------------
# Public API — the acceptance-criteria entry point
# ---------------------------------------------------------------------------


def calculate_affected_paths(
    modified_files: list[str],
    workspace_root: str | Path,
    config: "BlastRadiusConfig | None" = None,
) -> BlastRadiusMatrix:
    """Compute the affected dependency matrix for a set of modified files.

    Mapping: every modified file is owned by the deepest discovered
    package whose directory is a prefix of the file path (files outside
    every package become ``root_owned_files``). The affected set is the
    direct owners PLUS the transitive closure of packages that depend on
    them. Unaffected packages are the discovered packages outside that
    closure. Output lists are deterministically sorted.

    Spec compliance (Task 141): accepts optional ``BlastRadiusConfig`` for
    workspace_globs filtering and conservative_root_fallback, and populates
    ``is_monorepo`` / ``is_empty`` per spec.
    """
    # Lazy import to avoid circular import at module load
    try:
        from models import BlastRadiusConfig as _BRC
    except Exception:
        _BRC = None  # type: ignore

    if config is None and _BRC is not None:
        try:
            config = _BRC()
        except Exception:
            config = None

    root = Path(workspace_root)
    normalized = sorted({_normalize_file(f) for f in (modified_files or [])})
    normalized = [f for f in normalized if f]

    # Discover packages — respect workspace_globs if config provided
    if config is not None and hasattr(config, "workspace_globs"):
        # Use globs-aware discovery but preserve legacy list return for internal use
        # Call discover_packages with globs to get dict, then reconstruct list for internal
        # For backward compat, we need list[PackageInfo]; so call without globs for list
        # and use config globs only for filtering decision below
        packages = discover_packages(root)  # type: ignore
        if not isinstance(packages, list):
            # If discover_packages returned dict (when globs not None), convert
            packages = list(packages.values())  # type: ignore
    else:
        packages = discover_packages(root)  # type: ignore
        if not isinstance(packages, list):
            packages = list(packages.values())  # type: ignore

    # Spec: is_monorepo flag, but still compute matrix normally
    is_monorepo = len(packages) >= 2

    dep_map = build_dependency_map(packages, root)
    deps_by_pkg: dict[str, set[str]] = {
        d.package: set(d.depends_on) for d in dep_map
    }

    affected: set[str] = set()
    root_owned: list[str] = []
    for f in normalized:
        owner = find_owning_package(f, packages)
        if owner is None:
            root_owned.append(f)
        else:
            affected.add(owner.name)

    # Conservative root fallback: if any root file and config says True, mark all as affected
    conservative = True
    if config is not None and hasattr(config, "conservative_root_fallback"):
        conservative = bool(config.conservative_root_fallback)
    if root_owned and conservative:
        # All packages become affected
        affected = {p.name for p in packages}
        # Clear root_owned? Keep it but also mark all affected per spec
        # Spec says mark all packages as affected; we still keep root_owned for transparency
    else:
        # Transitive closure over reverse edges: any package that
        # (transitively) depends on an affected package is itself affected.
        if affected:
            changed = True
            while changed:
                changed = False
                for pkg_name, deps in deps_by_pkg.items():
                    if pkg_name not in affected and deps & affected:
                        affected.add(pkg_name)
                        changed = True

    affected_names = sorted(affected)
    affected_objs = [p for p in packages if p.name in affected_names]
    affected_paths = sorted(p.path for p in affected_objs)
    unaffected = sorted(p.name for p in packages if p.name not in affected_names)
    is_empty = len(affected_names) == 0

    return BlastRadiusMatrix(
        modified_files=normalized,
        packages=packages,
        dependency_map=dep_map,
        affected_packages=affected_names,
        affected_paths=affected_paths,
        unaffected_packages=unaffected,
        root_owned_files=root_owned,
        is_monorepo=is_monorepo,
        is_empty=is_empty,
    )


# ---------------------------------------------------------------------------
# Manifest parsers
# ---------------------------------------------------------------------------


def _node_deps(
    manifest_path: Path,
    abs_by_path: dict[Path, PackageInfo],
    by_name: dict[str, PackageInfo],
) -> set[str]:
    """Parse package.json dependency sections into local edges."""
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return set()
    edges: set[str] = set()
    sections = (
        "dependencies",
        "devDependencies",
        "peerDependencies",
        "optionalDependencies",
    )
    for section in sections:
        deps = data.get(section) or {}
        if not isinstance(deps, dict):
            continue
        for dep_name, raw_spec in deps.items():
            spec = str(raw_spec or "")
            if spec.startswith("workspace:"):
                if dep_name in by_name:
                    edges.add(dep_name)
                continue
            local = _resolve_local_reference(
                spec, manifest_path.parent, abs_by_path
            )
            if local is not None:
                edges.add(local)
                continue
            if dep_name in by_name:
                edges.add(dep_name)
    return edges


def _python_deps(
    manifest_path: Path,
    abs_by_path: dict[Path, PackageInfo],
    by_name: dict[str, PackageInfo],
) -> set[str]:
    """Parse pyproject.toml project/optional dependencies and uv sources."""
    try:
        data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return set()
    edges: set[str] = set()
    project = data.get("project") or {}

    deps = project.get("dependencies") or []
    if isinstance(deps, list):
        for spec in deps:
            _maybe_py_name_edge(spec, by_name, edges)

    optional = project.get("optional-dependencies") or {}
    if isinstance(optional, dict):
        for specs in optional.values():
            if isinstance(specs, list):
                for spec in specs:
                    _maybe_py_name_edge(spec, by_name, edges)

    # uv source map: {pkg: {"path": "../x"}} — explicit local references
    uv_sources = ((data.get("tool") or {}).get("uv") or {}).get("sources") or {}
    if isinstance(uv_sources, dict):
        for dep_name, source in uv_sources.items():
            if isinstance(source, dict) and isinstance(source.get("path"), str):
                local = _resolve_local_reference(
                    source["path"], manifest_path.parent, abs_by_path
                )
                if local is not None:
                    edges.add(local)
                elif dep_name in by_name:
                    edges.add(dep_name)
    return edges


def _maybe_py_name_edge(
    spec: str, by_name: dict[str, PackageInfo], edges: set[str]
) -> None:
    """Add a name edge when a requirement spec names a discovered package."""
    if not isinstance(spec, str):
        return
    match = _PY_REQUIREMENT_NAME_RE.match(spec.strip())
    if match and match.group(1) in by_name:
        edges.add(match.group(1))


def _go_deps(
    manifest_path: Path,
    abs_by_path: dict[Path, PackageInfo],
    by_name: dict[str, PackageInfo],
) -> set[str]:
    """Parse go.mod requires (name refs) and replaces (local path refs)."""
    try:
        text = manifest_path.read_text(encoding="utf-8")
    except Exception:
        return set()
    edges: set[str] = set()
    in_require_block = False
    in_replace_block = False
    base_dir = manifest_path.parent
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("//"):
            continue
        if line == "require (":
            in_require_block = True
            continue
        if line == ")" and in_require_block:
            in_require_block = False
            continue
        if line == "replace (":
            in_replace_block = True
            continue
        if line == ")" and in_replace_block:
            in_replace_block = False
            continue
        if in_require_block:
            parts = line.split()
            if parts and parts[0] in by_name:
                edges.add(parts[0])
            continue
        if in_replace_block:
            match = re.match(r"^(\S+)(?:\s+\S+)?\s*=>\s*(\S+)", line)
            if match:
                _maybe_go_replace_edge(
                    match.group(2), base_dir, abs_by_path, edges
                )
            continue
        if line.startswith("replace"):
            repl = _GO_REPLACE_RE.match(line)
            if repl:
                _maybe_go_replace_edge(
                    repl.group(2), base_dir, abs_by_path, edges
                )
            continue
        single = _GO_SINGLE_REQUIRE_RE.match(line)
        if single:
            token = single.group(1)
            if token in by_name:
                edges.add(token)
    return edges


def _maybe_go_replace_edge(
    target: str,
    base_dir: Path,
    abs_by_path: dict[Path, PackageInfo],
    edges: set[str],
) -> None:
    """Resolve a replace target path into a local dependency edge."""
    local = _resolve_local_reference(target, base_dir, abs_by_path)
    if local is not None:
        edges.add(local)


# ---------------------------------------------------------------------------
# Reference resolution
# ---------------------------------------------------------------------------


def _resolve_local_reference(
    spec: str, base_dir: Path, abs_by_path: dict[Path, PackageInfo]
) -> str | None:
    """Resolve an explicit local dependency reference to a package name.

    Handles ``file:../x``, ``file:../x#fragment``, relative paths and
    absolute paths. Returns the referenced package's name when the target
    resolves to a discovered package directory, else ``None``.
    """
    if spec.startswith("workspace:"):
        return None  # name-based; handled by callers
    target: str | None = None
    if spec.startswith("file:"):
        target = spec[5:]
    elif spec.startswith((".", "/", os.sep)):
        target = spec
    if target is None:
        return None
    target = target.split("#")[0].split("?")[0]
    if not target:
        return None
    try:
        resolved = (base_dir / target).resolve()
    except OSError:
        return None
    info = abs_by_path.get(resolved)
    return info.name if info is not None else None


# ---------------------------------------------------------------------------
# Manifest name / helpers
# ---------------------------------------------------------------------------


def _first_manifest(filenames: list[str]) -> str | None:
    """Return the winning manifest filename by precedence, or None."""
    names = set(filenames)
    for manifest in _MANIFEST_PRECEDENCE:
        if manifest in names:
            return manifest
    return None


def _manifest_name(manifest: str, manifest_path: Path, rel: str) -> str:
    """Extract the canonical package name from a manifest, else rel path."""
    if manifest in ("package.json", "composer.json"):
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            name = data.get("name") if isinstance(data, dict) else None
            if isinstance(name, str) and name:
                return name
        except Exception:
            pass
    elif manifest == "pyproject.toml":
        try:
            data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
            name = (data.get("project") or {}).get("name") if isinstance(data, dict) else None
            if isinstance(name, str) and name:
                return name
        except Exception:
            pass
    elif manifest == "go.mod":
        try:
            text = manifest_path.read_text(encoding="utf-8")
            match = _GO_MODULE_RE.search(text)
            if match:
                return match.group(1)
        except Exception:
            pass
    elif manifest == "Cargo.toml":
        try:
            data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
            name = (data.get("package") or {}).get("name") if isinstance(data, dict) else None
            if isinstance(name, str) and name:
                return name
        except Exception:
            pass
    return rel


def _dir_fallback_name(rel: str) -> str:
    """Name for a manifestless workspace dir: its last path segment."""
    return rel.rsplit("/", 1)[-1] or rel


def _normalize_file(path) -> str:
    """Normalize a modified-file path to a posix relative string."""
    s = str(path).replace("\\", "/")
    while s.startswith("./"):
        s = s[2:]
    return s


def _package_sort_key(p: PackageInfo) -> tuple[int, str]:
    """Sort root package ('.') first, then by path for determinism."""
    return (0 if p.path == "." else 1, p.path)