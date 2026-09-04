"""
Automated SemVer Bump & Keep-a-Changelog Engine (Task 147).
ZAC-safe: git tag creation defaults to dry-run.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


class ReleaseEngine:
    """Calculates versions, formats changelog entries, tags releases."""

    def calculate_next_version(self, current_version: str, task_types: list[str]) -> str:
        cur = current_version.strip().lstrip("v")
        parts = cur.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid SemVer: {current_version!r}")
        try:
            major, minor, patch = (int(p) for p in parts)
        except ValueError as e:
            raise ValueError(f"Invalid SemVer: {current_version!r}") from e
        lowered = [str(t).lower() for t in (task_types or [])]
        if any(t == "breaking" for t in lowered):
            return f"{major + 1}.0.0"
        if any(t == "feature" for t in lowered):
            return f"{major}.{minor + 1}.0"
        return f"{major}.{minor}.{patch + 1}"

    def format_changelog_entry(self, version: str, date_str: str, tasks: list[dict]) -> str:
        added: list[str] = []
        changed: list[str] = []
        fixed: list[str] = []
        for t in tasks or []:
            title = str(t.get("title", "") or "").strip()
            ttype = str(t.get("type", "") or "").lower()
            tid = t.get("id", "")
            line = f"- {title} (Task {tid})" if tid != "" else f"- {title}"
            if ttype == "feature":
                added.append(line)
            elif ttype in ("bug", "fix"):
                fixed.append(line)
            else:
                changed.append(line)
        lines = [f"## [{version}] - {date_str}", ""]
        if added:
            lines.append("### Added")
            lines.extend(added)
            lines.append("")
        if changed:
            lines.append("### Changed")
            lines.extend(changed)
            lines.append("")
        if fixed:
            lines.append("### Fixed")
            lines.extend(fixed)
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def update_changelog(self, changelog_path: Path, new_entry: str) -> None:
        p = Path(changelog_path)
        text = p.read_text(encoding="utf-8") if p.exists() else "# Changelog\n\n## [Unreleased]\n"
        marker = "## [Unreleased]"
        if marker in text:
            text = text.replace(marker, marker + "\n\n" + new_entry.rstrip(), 1)
        else:
            text = text + "\n" + new_entry
        p.write_text(text, encoding="utf-8")

    def create_git_tag(self, version: str, dry_run: bool = True) -> str:
        if dry_run:
            return f"[dry-run] Would create git tag v{version}"
        subprocess.run(
            ["git", "tag", "-a", f"v{version}", "-m", f"Release v{version}"],
            check=True,
        )
        return f"v{version}"
