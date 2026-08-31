"""
Contract Propagation Engine (LE-6 / Task 138).

Detects contract file mutations in task git diffs and automatically dispatches
downstream tasks into ``tasks/backlog/`` with sequential next-task IDs and
SQLite state registration.

Pipeline:
    git diff text -> extract_modified_paths() -> match_contract_rules()
    -> ContractPropagationEngine.process_task_closure() -> task file generation.

Design notes:
- Pure helpers (extract_modified_paths, match_contract_rules,
  discover_next_task_id) are intentionally side-effect free and unit-testable.
- The engine writes canonical task files whose metadata mirrors the
  task-generator template: # Task {N}: {title}, **File:**, **Source:**
  contract-propagation, **Triggered-By:**, **Stack:**, **Type:**, **Status:**
  plus ## Goal / ## Source Context / ## Acceptance Criteria / Factual Git Diff
  markers.
- Every generated task is registered in the StateMachine as BACKLOG so the
  daemon watcher/trigger gate can pick it up.
"""

from __future__ import annotations

import fnmatch
import re
from pathlib import Path

from models import ContractRuleConfig, TaskState
from state import StateMachine

# Matches `diff --git a/<old> b/<new>` header lines. The b-side path is the
# post-change relative path we care about.
_DIFF_HEADER_RE = re.compile(r"^diff --git a/(.+?) b/(.+?)\n", re.MULTILINE)

# Slugify: drop every non-alphanumeric, collapse runs to a single dash.
_SLUG_RE = re.compile(r"[^a-z0-9]+")


def extract_modified_paths(diff_text: str) -> list[str]:
    """Return deduplicated relative paths of files touched by a git diff.

    Parses ``diff --git a/x b/y`` headers (b-side path) and preserves first
    occurrence order. Empty/malformed diffs yield ``[]``.
    """
    paths: list[str] = []
    seen: set[str] = set()
    for match in _DIFF_HEADER_RE.finditer(diff_text or ""):
        path = match.group(2)
        if path not in seen:
            seen.add(path)
            paths.append(path)
    return paths


def match_contract_rules(
    modified_paths: list[str],
    rules: list[ContractRuleConfig],
) -> list[tuple[ContractRuleConfig, list[str]]]:
    """Return ``[(rule, [matching_files])]`` for rules whose glob patterns hit.

    A path matches a rule if it matches ANY of the rule's patterns. Patterns
    are evaluated with ``fnmatch`` against the full relative path, so
    ``packages/shared-schema/**`` matches nested files and ``*.prisma``
    matches ``prisma/schema.prisma``.
    """
    matches: list[tuple[ContractRuleConfig, list[str]]] = []
    for rule in rules or []:
        matching: list[str] = []
        for path in modified_paths:
            for pattern in rule.patterns or []:
                if fnmatch.fnmatch(path, pattern):
                    matching.append(path)
                    break
        if matching:
            matches.append((rule, matching))
    return matches


def discover_next_task_id(tasks_dir: Path) -> int:
    """Return ``max(numeric task-id prefixes) + 1`` across ALL task folders.

    Scans every ``*.md`` under ``tasks_dir`` recursively (backlog,
    in-progress, qa, completed, archive) so generated IDs never collide.
    Returns ``1`` when no task files exist.
    """
    max_id = 0
    tasks_path = Path(tasks_dir)
    if tasks_path.exists():
        for md in tasks_path.rglob("*.md"):
            match = re.match(r"(\d+)", md.name)
            if match:
                max_id = max(max_id, int(match.group(1)))
    return max_id + 1


class ContractPropagationEngine:
    """Generates downstream backlog tasks when contract files mutate."""

    def __init__(
        self,
        rules: list[ContractRuleConfig] | None = None,
        tasks_dir: str | Path = "tasks",
    ):
        self.rules = list(rules) if rules else []
        self.tasks_dir = Path(tasks_dir)

    @staticmethod
    def _build_task_body(
        next_id: int,
        title: str,
        triggering_task_id: int,
        stack: str,
        goal: str,
        matching_files: list[str],
        file_header: str,
        acceptance_criteria: list[str],
    ) -> str:
        """Build the canonical Markdown body for a dispatched task."""
        ac_block = "\n".join(f"- [ ] {ac}" for ac in acceptance_criteria)
        files_block = "\n".join(f"- {f}" for f in matching_files)
        return (
            f"# Task {next_id}: {title}\n"
            f"**File:** {file_header}\n"
            f"**Source:** contract-propagation\n"
            f"**Triggered-By:** Task {triggering_task_id}\n"
            f"**Stack:** {stack}\n"
            f"**Type:** feature\n"
            f"**Status:** open\n"
            f"\n"
            f"## Goal\n"
            f"{goal}\n"
            f"\n"
            f"## Source Context\n"
            f"Generated automatically via Contract Propagation Engine following "
            f"contract mutations in Task {triggering_task_id}.\n"
            f"Modified contract files:\n"
            f"{files_block}\n"
            f"\n"
            f"## Acceptance Criteria\n"
            f"{ac_block}\n"
            f"\n"
            f"## Factual Git Diff\n"
            f"<!-- BEGIN_GIT_DIFF -->\n"
            f"<!-- END_GIT_DIFF -->\n"
        )

    def process_task_closure(
        self,
        task_id: int,
        task_file: str,
        diff_text: str,
        repo_root: str | Path,
        state: StateMachine,
    ) -> list[dict]:
        """Dispatch downstream tasks for contract mutations in a closed task.

        Args:
            task_id: ID of the closed task whose diff triggered propagation.
            task_file: Path of the closed task file (informational).
            diff_text: Raw git diff text extracted from the task file.
            repo_root: Workspace root (repo anchor for `tasks/`).
            state: StateMachine used to register generated backlog tasks.

        Returns:
            List of dispatch summaries: ``{"task_id", "title", "file"}``.
            Empty list when no contract rule matched (no-op).
        """
        repo_root_path = Path(repo_root)
        modified_paths = extract_modified_paths(diff_text)
        rule_matches = match_contract_rules(modified_paths, self.rules)
        if not rule_matches:
            return []

        tasks_root = repo_root_path / self.tasks_dir
        next_id = discover_next_task_id(tasks_root)
        backlog_dir = tasks_root / "backlog"
        backlog_dir.mkdir(parents=True, exist_ok=True)

        dispatched: list[dict] = []
        for rule, matching_files in rule_matches:
            for template in rule.downstream_tasks:
                title = template.title_template.format(
                    contract_name=rule.name,
                    triggering_task_id=task_id,
                )
                goal = template.goal_template.format(
                    contract_name=rule.name,
                    triggering_task_id=task_id,
                    files=", ".join(matching_files),
                )
                slug = re.sub(_SLUG_RE, "-", title.lower()).strip("-")[:50]
                filename = f"{next_id:02d}-{slug}.md"
                file_header = f"tasks/backlog/{filename}"
                target_path = backlog_dir / filename

                body = self._build_task_body(
                    next_id=next_id,
                    title=title,
                    triggering_task_id=task_id,
                    stack=template.stack,
                    goal=goal,
                    matching_files=matching_files,
                    file_header=file_header,
                    acceptance_criteria=template.acceptance_criteria,
                )
                target_path.write_text(body, encoding="utf-8")
                state.register_task(str(target_path), TaskState.BACKLOG)

                dispatched.append(
                    {"task_id": next_id, "title": title, "file": file_header}
                )
                next_id += 1

        return dispatched