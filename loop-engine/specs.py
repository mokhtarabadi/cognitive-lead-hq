"""
Spec-First Artifact Pipeline & State Gate (LE-8 / Task 140).

Enforces that tasks introducing architectural changes, API contracts, or
database schema mutations must have verified spec artifacts (ADR, PRD,
Contract, Data Model) BEFORE code implementation begins.

Pipeline:
    task_content + plan_text -> evaluate_requirements() -> matched rules
    -> validate_artifacts(workspace_root, diff_text) -> SpecValidationResult

Design notes:
- ``evaluate_requirements`` is a pure keyword scan (lowercased substring
  match) and returns an empty list for routine tasks / bugfixes.
- ``validate_artifacts`` scans the workspace with ``rglob`` + ``fnmatch``
  (full-relative-path glob semantics, same as ``contracts.match_contract_rules``)
  and also parses ``diff --git`` headers from the staged task diff so artifacts
  staged in the active task satisfy the gate.
- An empty rule set passes immediately (the gate is inert until configured).
- The engine is deterministic and side-effect free; the daemon owns all state
  transitions (CRASHED / spec_artifacts persistence).
"""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from pathlib import Path

from models import SpecGateConfig, SpecRequirementRule

# Matches `diff --git a/<old> b/<new>` header lines — the b-side path is the
# post-change relative path that may stage spec artifacts (mirrors contracts.py).
_DIFF_HEADER_RE = re.compile(r"^diff --git a/(.+?) b/(.+?)\n", re.MULTILINE)


@dataclass
class SpecValidationResult:
    """Outcome of a spec artifact validation run."""
    passed: bool
    required_artifacts: list[str] = field(default_factory=list)
    found_artifacts: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    report_md: str = ""


class SpecGateEngine:
    """Keyword-driven spec requirement evaluation + artifact validation."""

    def __init__(self, config: SpecGateConfig | None = None):
        self.config = config or SpecGateConfig()

    # --- Requirement evaluation ---

    def evaluate_requirements(self, task_content: str, plan_text: str = "") -> list[SpecRequirementRule]:
        """Return the subset of configured rules triggered by task/plan keywords.

        The task content and approved plan are combined and lowercased; a rule
        fires when ANY of its ``keywords`` appears as a substring. Routine tasks
        and bugfixes (no keyword hit) yield an empty list.
        """
        if not self.config.rules:
            return []
        haystack = f"{(task_content or '')}\n{(plan_text or '')}".lower()
        matched: list[SpecRequirementRule] = []
        for rule in self.config.rules:
            if any(keyword.lower() in haystack for keyword in rule.keywords):
                matched.append(rule)
        return matched

    # --- Artifact validation ---

    def validate_artifacts(
        self,
        rules: list[SpecRequirementRule],
        workspace_root: str | Path,
        diff_text: str = "",
    ) -> SpecValidationResult:
        """Validate that required spec artifacts exist for each fired rule.

        For every rule, each ``target_directories`` pattern is checked against
        (1) files present under ``workspace_root`` (``rglob`` + ``fnmatch``) and
        (2) paths staged in ``diff_text`` (parsed from ``diff --git`` headers).
        A rule is satisfied when at least one of its patterns matches anywhere.
        Missing rules produce diagnostic errors and a structured Markdown report.

        An empty ``rules`` list passes immediately (``SpecValidationResult(passed=True)``).
        """
        if not rules:
            return SpecValidationResult(passed=True)

        root = Path(workspace_root)
        diff_text = diff_text or ""
        required: list[str] = []
        found: list[str] = []
        errors: list[str] = []

        for rule in rules:
            rule_required = [a.value for a in rule.required_artifacts]
            rule_found: list[str] = []
            for pattern in rule.target_directories or []:
                if pattern not in required:
                    required.append(pattern)
                matches = _find_matching_files(root, pattern)
                matches += _paths_in_diff_matching(diff_text, pattern)
                for m in matches:
                    if m not in rule_found:
                        rule_found.append(m)
                    if m not in found:
                        found.append(m)
            if not rule_found:
                artifact_label = ", ".join(rule_required) if rule_required else "spec artifact"
                errors.append(
                    f"Rule '{rule.name}' requires {artifact_label} "
                    f"but no matching file found under {', '.join(rule.target_directories or [])}"
                )

        report_md = _build_report(rules, required, found, errors)
        return SpecValidationResult(
            passed=len(errors) == 0,
            required_artifacts=required,
            found_artifacts=found,
            errors=errors,
            report_md=report_md,
        )


# --- Pure helpers (unit-testable, side-effect free) ---


def _find_matching_files(root: Path, pattern: str) -> list[str]:
    """Return relative paths of files under ``root`` matching a glob pattern.

    Uses ``rglob`` + ``fnmatch`` over the full relative path so patterns like
    ``docs/adr/**`` and ``docs/architecture.md`` behave consistently.
    """
    matches: list[str] = []
    try:
        for p in root.rglob("*"):
            if p.is_file():
                rel = p.relative_to(root).as_posix()
                if fnmatch.fnmatch(rel, pattern):
                    matches.append(rel)
    except OSError:
        return []
    return sorted(matches)


def _paths_in_diff(diff_text: str) -> list[str]:
    """Return deduplicated relative paths of files touched by a git diff."""
    paths: list[str] = []
    seen: set[str] = set()
    for match in _DIFF_HEADER_RE.finditer(diff_text):
        path = match.group(2).strip()
        if path and path not in seen:
            seen.add(path)
            paths.append(path)
    return paths


def _paths_in_diff_matching(diff_text: str, pattern: str) -> list[str]:
    """Return staged diff paths (b-side) matching a glob pattern."""
    return [p for p in _paths_in_diff(diff_text) if fnmatch.fnmatch(p, pattern)]


def _build_report(
    rules: list[SpecRequirementRule],
    required: list[str],
    found: list[str],
    errors: list[str],
) -> str:
    """Build a structured Markdown report: verified vs missing spec artifacts."""
    lines = ["# Spec-First Gate Report", ""]
    lines.append(f"**Rules evaluated:** {len(rules)}")
    lines.append(f"**Required artifact locations:** {len(required)}")
    lines.append(f"**Verified artifacts:** {len(found)}")
    lines.append(f"**Errors:** {len(errors)}")
    lines.append("")
    if found:
        lines.append("## Verified Artifacts")
        lines.extend(f"- {f}" for f in found)
        lines.append("")
    if errors:
        lines.append("## Missing Spec Artifacts")
        lines.extend(f"- {e}" for e in errors)
        lines.append("")
    lines.append("## Resolution")
    lines.append(
        "Add the required spec artifact (ADR / PRD / Contract / Data Model) under "
        "the configured target directories, or include it in the task's staged diff "
        "before implementation. See `docs/loop-engine/configuration.md` (LE-8)."
    )
    return "\n".join(lines)