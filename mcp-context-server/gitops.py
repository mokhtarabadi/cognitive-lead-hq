# Sibling Docs: README.md | Decisions: DECISIONS.md


"""Git/kanban helpers: repo roots, commit gates, task discovery, archive patching. Stdlib-pure: no MCP imports, no registration, no import back to server."""

import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional


def _repo_root(start_path: str, project_root: str | None = None) -> Path:
    """Resolve the git repo root for git subprocess calls.

    CWD fix: this server inherits opencode-server's CWD, which is usually
    NOT the caller project, so bare `git` calls fail with exit 128.
    Resolution order: explicit project_root override first, then walk up
    from absolute task paths to the enclosing `.git`, then CWD fallback
    (git errors honestly if that is not a repo).
    """
    if project_root:
        return Path(project_root).resolve()
    p = Path(start_path)
    start = (
        (p if p.is_dir() else p.parent) if p.is_absolute() else (Path.cwd() / p).parent
    )
    for cand in [start, *start.parents]:
        if (cand / ".git").exists():
            return cand
    return start


def _derive_task_slug(task_file_path: str) -> str:
    """Derives a 'task <NN> - <slug>' label from a task file name (e.g. '78-fix-bug.md' -> 'task 78 - fix bug')."""
    name = Path(task_file_path).stem
    parts = re.split(r"[-_]", name, maxsplit=1)
    if len(parts) == 2 and parts[0].isdigit():
        return f"task {parts[0]} - {parts[1].replace('-', ' ')}"
    return f"task - {name.replace('-', ' ')}"


# Conventional Commits enforcement (Task 211): `commit_and_clean_task` is the
# ONLY commit path, so the caller-supplied feature message is validated here
# against skill-templates/versioning-and-release (`type: subject`, ≤72 chars).


_CONVENTIONAL_RE = re.compile(r"^(feat|fix|docs|refactor|chore): \S.*$")


def _check_conventional_commit(commit_message: str) -> Optional[str]:
    """Returns an error string when commit_message violates Conventional Commits, else None."""
    first_line = (
        commit_message.splitlines()[0]
        if commit_message and commit_message.strip()
        else ""
    )
    if not _CONVENTIONAL_RE.match(first_line):
        return (
            "❌ Commit message rejected: must match Conventional Commits "
            "`<type>: <subject>` with type in feat|fix|docs|refactor|chore "
            f"(see skill-templates/versioning-and-release). Got: {first_line!r}"
        )
    if len(first_line) > 72:
        return (
            "❌ Commit message rejected: first line exceeds 72 characters "
            f"({len(first_line)}). Got: {first_line!r}"
        )
    return None


ACTIVE_KANBAN_DIRS = ["backlog", "in-progress", "qa", "completed"]


MAX_BUNDLE_SIZE = 6


DIFF_SIZE_WARNING_THRESHOLD = 400


def _kebab_case(text: str) -> str:
    """Convert arbitrary title to kebab-case slug (B4: supports Unicode/Persian)."""
    import unicodedata

    normalized = unicodedata.normalize("NFKD", text)
    slug = normalized.lower().strip()
    slug = re.sub(
        r"[^a-z0-9\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]+", "-", slug
    )
    slug = re.sub(r"-{2,}", "-", slug)
    slug = slug.strip("-")
    return slug or "bundle"


def _discover_next_id(tasks_root: Path = Path("tasks")) -> int:
    max_id = 0
    if not tasks_root.is_dir():
        return 1
    for md in tasks_root.rglob("*.md"):
        m = re.match(r"^(\d+)-", md.name)
        if m:
            try:
                nid = int(m.group(1))
                if nid > max_id:
                    max_id = nid
            except ValueError:
                continue
    return max_id + 1 if max_id else 1


def _find_task_file(task_id: str, tasks_root: Path = Path("tasks")) -> Path | None:
    norm = task_id.lstrip("0") or "0"
    candidates: list[Path] = []
    for d in ACTIVE_KANBAN_DIRS:
        dir_path = tasks_root / d
        if not dir_path.is_dir():
            continue
        for md in dir_path.glob("*.md"):
            m = re.match(r"^(\d+)-", md.name)
            if m and m.group(1).lstrip("0") == norm:
                candidates.append(md)
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        return None  # B2: hard halt — duplicate active IDs
    # Check archive for better error (already archived)
    for md in (
        (tasks_root / "archive").glob("*.md")
        if (tasks_root / "archive").is_dir()
        else []
    ):
        m = re.match(r"^(\d+)-", md.name)
        if m and m.group(1).lstrip("0") == norm:
            return None
    return None


def _extract_section(content: str, heading: str) -> str | None:
    pattern = re.compile(
        rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\n---\s*\n|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(content)
    return m.group(1).strip() if m else None


def _extract_title(content: str) -> str:
    m = re.search(r"^# Task \d+:\s*(.+)$", content, re.MULTILINE)
    return m.group(1).strip() if m else "Untitled"


def _format_task_id_list(ids: list[str]) -> str:
    return "[" + ", ".join(ids) + "]"


def _extract_checklist_with_continuations(section_text: str) -> list[str]:
    """B1: Extract checklist items with all indented continuation lines."""
    lines = section_text.splitlines()
    result: list[str] = []
    in_checklist = False
    for line in lines:
        stripped = line.strip()
        is_root_bullet = line.startswith("- [")
        if is_root_bullet:
            in_checklist = True
            result.append(stripped)
        elif in_checklist:
            if (
                stripped
                and not line.startswith("- [")
                and not stripped.startswith("## ")
                and not stripped.startswith("---")
            ):
                result.append(line)
            else:
                in_checklist = False
                if line.startswith("- ["):
                    in_checklist = True
                    result.append(stripped)
    return result


def _detect_stack(content: str) -> str | None:
    """M1: Detect tech stack from task content."""
    lower = content.lower()
    if any(
        kw in lower
        for kw in ["jetpack compose", "kotlin", "android", "hilt", "sqldelight"]
    ):
        return "android"
    if any(kw in lower for kw in ["react", "vite", "jsx", "tsx", "next.js", "nextjs"]):
        return "react"
    if any(kw in lower for kw in ["fastapi", "pydantic", "uvicorn"]):
        return "fastapi"
    if any(kw in lower for kw in ["spring boot", "spring-boot", "java", "mapstruct"]):
        return "spring"
    if any(kw in lower for kw in ["swiftui", "ios", "swift", "uikit"]):
        return "ios"
    if any(kw in lower for kw in ["golang", "gin", "go-gin", "hexagonal"]):
        return "go"
    return None


def _verify_verbatim_checksums(
    source_data: list[tuple[str, Path, str, str]], meta_content: str
) -> bool:
    """M2: Verify 100% of extracted source AC text is in the Bundled Checklist."""
    bundled_match = re.search(
        r"^## Bundled Checklist.*?\n\n(.*?)(?=^## |\Z)",
        meta_content,
        re.MULTILINE | re.DOTALL,
    )
    if not bundled_match:
        return False
    bundled_text = bundled_match.group(1)
    for sid, path, content, _title in source_data:
        ac = _extract_section(content, "Acceptance Criteria")
        if not ac:
            continue
        for line in ac.splitlines():
            stripped = line.strip()
            if stripped and stripped.startswith("- ["):
                m = re.match(r"^- \[[ xX]\]\s*(.*)", stripped)
                core = m.group(1) if m else stripped
                prefixed = f"[{sid}] {core}"
                if len(core) > 10 and prefixed not in bundled_text:
                    return False
    return True


def _git_mv_or_fallback(src: Path, dst: Path) -> bool:
    dst.parent.mkdir(parents=True, exist_ok=True)
    repo = str(_repo_root(str(src)))
    result = subprocess.run(
        ["git", "mv", str(src), str(dst)], capture_output=True, text=True, cwd=repo
    )
    if result.returncode == 0:
        return True
    if (
        "not under version control" in result.stderr
        or "not tracked" in result.stderr.lower()
    ):
        try:
            src.rename(dst)
            subprocess.run(
                ["git", "add", "--", str(dst)],
                check=True,
                capture_output=True,
                cwd=repo,
            )
            return True
        except Exception:
            return False
    return False


def _patch_archived_file(archive_path: Path, meta_id: str, meta_slug: str) -> None:
    try:
        content = archive_path.read_text(encoding="utf-8")
    except Exception:
        return
    new_file_header = f"**File:** `tasks/archive/{archive_path.name}`"
    content = re.sub(r"\*\*File:\*\*\s*`[^`]+`", new_file_header, content, count=1)
    if re.search(r"\*\*Status:\*\*\s*\w+", content):
        content = re.sub(
            r"\*\*Status:\*\*\s*\w+", "**Status:** superseded", content, count=1
        )
    else:
        content = re.sub(
            r"(\*\*Type:\*\*\s*\w+)", r"\1\n**Status:** superseded", content, count=1
        )
    if "**Superseded-By:**" not in content:
        content = re.sub(
            r"(\*\*Status:\*\*\s*superseded)",
            rf"\1\n**Superseded-By:** `{meta_id}-{meta_slug}`",
            content,
            count=1,
        )
        timestamp = time.strftime("%Y-%m-%d")
        content = re.sub(
            r"(\*\*Superseded-By:\*\*\s*`[^`]+`)",
            rf"\1\n**Superseded-At:** `{timestamp}`",
            content,
            count=1,
        )
    superseded_note = (
        f"> **Superseded:** This task was bundled into META task `{meta_id}-{meta_slug}` "
        f"and archived on {time.strftime('%Y-%m-%d')}. "
        f"See `tasks/backlog/{meta_id}-{meta_slug}.md` (or its Kanban successor) for the unified execution. "
        f"History preserved via `git log --follow -- tasks/archive/{archive_path.name}`.\n"
    )
    if superseded_note.strip() not in content:
        if "## Execution Log" in content:
            content = content.replace(
                "## Execution Log", superseded_note + "\n## Execution Log", 1
            )
        elif "## Factual Git Diff" in content:
            content = content.replace(
                "## Factual Git Diff", superseded_note + "\n## Factual Git Diff", 1
            )
    try:
        archive_path.write_text(content, encoding="utf-8")
    except Exception:
        pass
