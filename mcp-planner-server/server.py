#!/usr/bin/env -S uv run
# Sibling Docs: mcp-planner-server/README.md | Decisions: mcp-planner-server/DECISIONS.md
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.3.0,<2.0", "pyyaml", "starlette", "uvicorn"]
# ///
"""Planner MCP Server — capacity-aware, QA-gated planning layer over tasks/ Markdown.

Reads task files from tasks/{backlog,in-progress,qa,completed,archive} as the
single source of truth, builds a derived index (tasks/.plan/index.json,
gitignored), and exposes planning tools:

- plan_propose(goal, deadline, capacity_hours) — decompose a goal into tasks +
  milestones with estimates (propose only, writes nothing).
- plan_materialize(project_root, task_ids) — write new task files only after
  Manager approval; every written file passes lint_task_file.
- claim_next(project_root, task_id) — guarded claim: checks dependencies,
  WIP limits, QA budget before moving a task from backlog to in-progress.
- plan_status(project_root) — Kanban lanes, active sprint, milestone status.
- sprint_stats(project_root) — hours spent, progress %, velocity.
- qa_budget(project_root) — count of QA-pending tasks (autopilot budget).
- milestone_status(project_root) — milestone summary.
- sprint_lock(sprint_id) — mark a sprint as locked.
- sprint_daily_agenda(project_root) — locked tasks for today's quota.
- sprint_check_daily_quota(project_root) — check if today's planned tasks
  are complete; signal DAILY_QUOTA_REACHED.

An embedded Starlette app serves the static dashboard on GET / and GET /api/status
alongside the FastMCP StreamableHTTP endpoint on port 8108.

Authentication (optional, off by default) lives in
`~/.config/opencode/planner-users.json` (override with `PLANNER_USERS_CONFIG`).
When `auth_enabled` is true the dashboard requires a session cookie from
`POST /api/login` and `/api/status` filters the project list to the caller's
`allowed_projects` (403 outside them). The `/mcp` transport stays auth-free:
loopback MCP clients connect without credentials, and the Cloudflare Tunnel
ingress 404s `/mcp` before any remote request reaches it.
With no config file — or `auth_enabled: false` — the server stays in open
local mode, byte-identical to the pre-auth behaviour.

Design rules:
- tasks/ Markdown is canonical; the planner is a derived index only.
- Autopilot QA budget: max 1 unresolved QA/review task.
- Only planner tooling may change task state; every transition passes lint_task_file.
- Zero-Autonomous-Commit: no git commit/push/add/checkout from this server.
"""

import contextvars
import functools
import hashlib
import hmac
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
import uuid
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Planner", host="127.0.0.1", port=8108)

# Client-visible project-isolation warning (mirrors mcp-context-server pattern).
_FALLBACK_FIRED: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "planner_fallback_fired", default=False
)

_ROOT_FALLBACK_WARNING = (
    "WARNING [project-isolation]: project_root was omitted, so this call "
    "was scoped to the singleton server's own directory instead of the "
    "calling project. Pass an absolute project_root on every call."
)


def _project_tool(fn):
    """Register an MCP tool that surfaces root-fallback client-visibly."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        _FALLBACK_FIRED.set(False)
        out = fn(*args, **kwargs)
        if not _FALLBACK_FIRED.get():
            return out
        if isinstance(out, str):
            return _ROOT_FALLBACK_WARNING + "\n" + out
        return out

    return mcp.tool()(wrapper)


def _explicit_project_root(project_root: Optional[str], tool_name: str) -> Path:
    """Validate a per-call project root.

    Returns the resolved absolute directory. When omitted, falls back to
    the server working directory with a stderr warning. Raises ValueError
    naming the field for relative, missing, or non-directory input.
    """
    if project_root is None:
        root = Path.cwd().resolve()
        _FALLBACK_FIRED.set(True)
        print(
            f"Warning: {tool_name}: project_root omitted, "
            f"falling back to server cwd {root}",
            file=sys.stderr,
        )
        return root
    if not isinstance(project_root, str) or not project_root.strip():
        raise ValueError("project_root must be a non-empty absolute path string.")
    if not Path(project_root).is_absolute():
        raise ValueError(f"project_root must be absolute, got: {project_root!r}.")
    root = Path(project_root).resolve()
    if not root.is_dir():
        raise ValueError(
            f"project_root must be an existing directory, got: {project_root!r}."
        )
    return root


# ---------------------------------------------------------------------------
# Task parsing helpers
# ---------------------------------------------------------------------------

TASK_LANES = ("backlog", "in-progress", "qa", "completed", "archive")
TASK_ID_RE = re.compile(r"^(\d+)-(.+)\.md$")


def _parse_task_file(path: Path) -> dict:
    """Parse a task Markdown file into structured fields.

    Reads the canonical task header (**File:**, **Source:**, **Type:**,
    **Status:**) plus any additive planner metadata fields
    (**Estimate:**, **Deadline:**, **Milestone:**, **Depends on:**), the
    ## Acceptance Criteria checkboxes, and ## Local TODOs checkboxes.
    Returns a dict with lanes, status, estimates, and parsed sections.
    Never raises on malformed input — missing fields are None/empty.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {"path": str(path), "error": "unreadable"}

    lines = text.splitlines()

    record: dict = {
        "path": str(path),
        "name": path.name,
        "lane": None,
        "title": None,
        "file_header": None,
        "source": None,
        "type": None,
        "status": None,
        "estimate_hours": None,
        "deadline": None,
        "milestone": None,
        "depends_on": [],
        "acceptance_criteria": [],
        "todos": [],
        "raw": text,
    }

    header_pattern = re.compile(r"^\*\*(.+?):\*\*\s*(.+)$")
    for line in lines:
        m = header_pattern.match(line.strip())
        if not m:
            continue
        key = m.group(1).strip().lower()
        val = m.group(2).strip().strip("`")
        if key == "file":
            record["file_header"] = val
        elif key == "source":
            record["source"] = val
        elif key == "type":
            record["type"] = val
        elif key == "status":
            record["status"] = val
        elif key == "owner":
            record["owner"] = val
        elif key == "estimate":
            em = re.match(r"(\d+(?:\.\d+)?)\s*h", val, re.IGNORECASE)
            if em:
                record["estimate_hours"] = float(em.group(1))
        elif key == "deadline":
            record["deadline"] = val
        elif key == "milestone":
            record["milestone"] = val
        elif key == "depends on":
            # Parse depends_on which may be ["a", "b"] or "a, b" format
            dep_str = val.strip()
            if dep_str.startswith("[") and dep_str.endswith("]"):
                dep_str = dep_str[1:-1]
            record["depends_on"] = [
                d.strip().strip('"').strip("'") for d in dep_str.split(",") if d.strip()
            ]

    # Determine lane from path parts.
    parts = path.parts
    for idx, part in enumerate(parts):
        if part == "tasks" and idx + 1 < len(parts):
            lane = parts[idx + 1]
            if lane in TASK_LANES:
                record["lane"] = lane
            break

    # Title from first "# Task N: ..." heading.
    for line in lines:
        m = re.match(r"^# Task\s+\d+:\s*(.+)$", line.strip())
        if m:
            record["title"] = m.group(1).strip()
            break

    # Parse AC checkboxes.
    in_ac = False
    for line in lines:
        stripped = line.strip()
        if stripped == "## Acceptance Criteria":
            in_ac = True
            continue
        if in_ac:
            if stripped.startswith("## "):
                in_ac = False
                continue
            m = re.match(r"-\s*\[(x|\s)\]\s*(.+)$", stripped)
            if m:
                record["acceptance_criteria"].append(
                    {"text": m.group(2).strip(), "done": m.group(1) == "x"}
                )

    # Parse TODO checkboxes.
    in_todos = False
    for line in lines:
        stripped = line.strip()
        if stripped == "## Local TODOs":
            in_todos = True
            continue
        if in_todos:
            if stripped.startswith("## "):
                in_todos = False
                continue
            m = re.match(r"-\s*\[(x|\s)\]\s*(.+)$", stripped)
            if m:
                record["todos"].append(
                    {"text": m.group(2).strip(), "done": m.group(1) == "x"}
                )

    return record


def _load_all_tasks(workspace_root: Path) -> list[dict]:
    """Load every task file across all Kanban lanes.

    Returns a list of parsed task dicts, each augmented with its lane.
    Files in tasks/archive/ are included (historical record) but marked
    with lane "archive".
    """
    tasks_dir = workspace_root / "tasks"
    all_tasks: list[dict] = []
    if not tasks_dir.is_dir():
        return all_tasks
    for lane in TASK_LANES:
        lane_dir = tasks_dir / lane
        if not lane_dir.is_dir():
            continue
        for f in sorted(lane_dir.glob("*.md")):
            rec = _parse_task_file(f)
            rec["lane"] = lane
            all_tasks.append(rec)
    return all_tasks


def _find_task_by_id(tasks: list[dict], task_id: str) -> Optional[dict]:
    """Find a task by its numeric ID (filename prefix).

    Compares as integers so "020" matches "20".
    """
    try:
        target_id = int(task_id)
    except (ValueError, TypeError):
        return None
    for rec in tasks:
        m = TASK_ID_RE.match(rec["name"])
        if m and int(m.group(1)) == target_id:
            return rec
    return None


def _deps_met(task: dict, all_tasks: list[dict]) -> tuple[bool, list[str]]:
    """Check whether all dependencies of a task are satisfied.

    A dependency is satisfied if its task exists and is in the completed lane.
    Returns (met, unmet_dependency_ids).
    """
    unmet: list[str] = []
    for dep_id in task.get("depends_on", []):
        dep = _find_task_by_id(all_tasks, dep_id)
        if dep is None or dep.get("lane") != "completed":
            unmet.append(dep_id)
    return (len(unmet) == 0, unmet)


def _count_qa_pending(tasks: list[dict]) -> int:
    """Count tasks whose lane is 'qa' (awaiting review)."""
    return sum(1 for t in tasks if t.get("lane") == "qa")


def _count_in_progress(tasks: list[dict]) -> int:
    """Count tasks whose lane is 'in-progress'."""
    return sum(1 for t in tasks if t.get("lane") == "in-progress")


# ---------------------------------------------------------------------------
# Planning tools
# ---------------------------------------------------------------------------


@_project_tool
def plan_propose(
    goal: str,
    deadline: Optional[str] = None,
    capacity_hours: Optional[float] = None,
    project_root: Optional[str] = None,
) -> str:
    """Decompose a goal into tasks and milestones with estimates (propose only).

    This is the conversational planning tool. It analyzes the goal text,
    derives a suggested breakdown into tasks with estimates, dependencies,
    and a milestone, and returns a text proposal. It writes NOTHING to disk.
    The Manager reviews the proposal and then calls plan_materialize to
    create the actual task files.

    Args:
        goal: Natural-language description of what should be done.
        deadline: Optional target date (ISO YYYY-MM-DD or free text).
        capacity_hours: Optional weekly capacity in hours (default 20).
        project_root: Absolute path to the project holding tasks/.

    Returns:
        A markdown-formatted proposal with suggested tasks, estimates,
        dependencies, milestone, and the command to materialize it.
    """
    workspace_root = _explicit_project_root(project_root, "plan_propose")
    existing = _load_all_tasks(workspace_root)

    # Determine the next task ID.
    existing_ids: list[int] = []
    for rec in existing:
        m = TASK_ID_RE.match(rec["name"])
        if m:
            existing_ids.append(int(m.group(1)))
    next_id = (max(existing_ids) + 1) if existing_ids else 1

    cap = capacity_hours if capacity_hours is not None else 20.0

    lines: list[str] = []
    lines.append(f"# Plan Proposal: {goal}")
    lines.append("")
    lines.append(f"- **Deadline:** {deadline or 'not set'}")
    lines.append(f"- **Capacity:** {cap} hours/week")
    lines.append(f"- **Next task ID:** {next_id:03d}")
    lines.append("")
    lines.append("## Suggested Tasks")
    lines.append("")
    lines.append("| ID | Title | Estimate (h) | Depends on | Milestone | Lane |")
    lines.append("| --- | --- | --- | --- | --- | --- |")

    # Lightweight heuristic decomposition: split the goal into atomic tasks.
    parts = re.split(r"[.!?]|\band\b|\bthen\b|\bplus\b", goal, flags=re.IGNORECASE)
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        parts = [goal]

    suggested: list[dict] = []
    for i, part in enumerate(parts[:8]):  # cap at 8 tasks for v1
        task_id = next_id + i
        est = max(1.0, round(cap / max(len(parts), 1), 1))
        suggested.append(
            {
                "id": task_id,
                "title": part,
                "estimate": est,
                "depends_on": [str(task_id - 1)] if i > 0 else [],
                "milestone": "M1",
            }
        )

    for s in suggested:
        lines.append(
            f"| {s['id']:03d} | {s['title']} | {s['estimate']} | "
            f"{', '.join(s['depends_on']) or '—'} | {s['milestone']} | backlog |"
        )

    lines.append("")
    lines.append("## Milestone")
    lines.append(f"- **M1:** {goal} — deadline {deadline or 'TBD'}")
    lines.append("")
    lines.append("## Next Step")
    lines.append(
        "Review the proposal, then call `plan_materialize` with the task IDs "
        "you want to create (comma-separated) to write them to tasks/backlog/. "
        "No files are written by this call."
    )

    return "\n".join(lines)


@_project_tool
def plan_materialize(
    project_root: str,
    task_ids: str,
) -> str:
    """Materialize one or more proposed tasks into task files.

    Writes new task Markdown files to tasks/backlog/ for the given task IDs
    (comma-separated). Each file passes lint_task_file structure rules.
    The Manager must have approved the proposal first.

    Args:
        project_root: Absolute path to the project holding tasks/.
        task_ids: Comma-separated list of task IDs to materialize.
        Returns:
        Summary of created files and any validation results.

        Notes:
        Planner metadata (**Estimate:**, **Milestone:**, **Deadline:**,
        **Depends on:**) is deliberately left out: only the Manager knows
        those values, and a fabricated placeholder would pollute the derived
        read model (an `Estimate: TBD` never parses and a `Deadline: TBD`
        would appear on the dashboard timeline).
    """
    workspace_root = _explicit_project_root(project_root, "plan_materialize")
    tasks_dir = workspace_root / "tasks"
    backlog_dir = tasks_dir / "backlog"
    backlog_dir.mkdir(parents=True, exist_ok=True)

    existing = _load_all_tasks(workspace_root)
    existing_ids: set[str] = set()
    for rec in existing:
        m = TASK_ID_RE.match(rec["name"])
        if m:
            existing_ids.add(
                str(int(m.group(1)))
            )  # Normalize to int then back to string

    created: list[str] = []
    skipped: list[str] = []

    for tid in [t.strip() for t in task_ids.split(",") if t.strip()]:
        # Normalize tid to integer for comparison
        try:
            tid_norm = str(int(tid))
        except (ValueError, TypeError):
            skipped.append(f"{tid} (invalid ID)")
            continue
        if tid_norm in existing_ids:
            skipped.append(f"{tid} (already exists)")
            continue
        title = f"task-{tid_norm}"
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        filename = f"{int(tid_norm):03d}-{slug}.md"
        target = backlog_dir / filename

        content = f"""# Task {int(tid):03d}: {title}

**File:** `tasks/backlog/{filename}`
**Source:** planner
**Type:** feature
**Status:** open

## Source Context

### Variant C: Manager (`**Source:** manager`)

## Goal

{title}

## Manager's Notes

Materialized from planner proposal. Review and refine before execution.

## Local TODOs

- [ ] Clarify requirements
- [ ] Implement
- [ ] Verify functionality

## Acceptance Criteria

- [ ] Task file lint passes
- [ ] Implementation complete
- [ ] Verification evidence recorded

## Verification Evidence

- **Test command:** _(fill in during execution)_
- **Expected result:** _(fill in during execution)_
- **Actual result:** _(fill in during execution)_
- **Exit code:** _(fill in during execution)_

## Definition of Done

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Scope creep or unclear requirements.
- **Rollback plan:** Delete the task file and re-scope.

## Execution Log & Reasoning

Materialized by planner on {date.today().isoformat()}.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

<!-- END_GIT_DIFF -->
"""
        target.write_text(content, encoding="utf-8")
        created.append(str(target))

    return (
        f"Materialized {len(created)} task file(s):\n"
        + "\n".join(f"- {c}" for c in created)
        + (f"\nSkipped (already exist): {', '.join(skipped)}" if skipped else "")
    )


@_project_tool
def claim_next(project_root: str, task_id: str) -> str:
    """Claim the next task: move it from backlog to in-progress.

    Circuit breaker: refuses the claim if any of these gate conditions fail:
    - The task does not exist or is not in tasks/backlog/.
    - Any dependency is not in tasks/completed/.
    - tasks/qa/ already has an unresolved task (QA budget exhausted).
    - tasks/in-progress/ already has 3 tasks (general WIP ceiling).

    On success, updates the task's **Status:** header to in-progress and
    moves the file via `git mv` (the only permitted autonomous git op).

    Args:
        project_root: Absolute path to the project holding tasks/.
        task_id: Numeric task ID to claim.

    Returns:
        Confirmation message or a block reason.
    """
    workspace_root = _explicit_project_root(project_root, "claim_next")
    tasks = _load_all_tasks(workspace_root)

    task = _find_task_by_id(tasks, task_id)
    if task is None:
        return f"❌ claim_next blocked: task {task_id} not found."
    if task.get("lane") != "backlog":
        return (
            f"❌ claim_next blocked: task {task_id} is in "
            f"{task.get('lane') or 'unknown'}, not backlog."
        )

    # Dependency check.
    deps_met, unmet = _deps_met(task, tasks)
    if not deps_met:
        return (
            f"❌ claim_next blocked: task {task_id} has unmet dependencies: "
            f"{', '.join(unmet)}."
        )

    # QA budget check: at most 1 unresolved QA/review task.
    qa_pending = _count_qa_pending(tasks)
    if qa_pending >= 1:
        qa_task = next((t for t in tasks if t.get("lane") == "qa"), None)
        return (
            f"❌ claim_next blocked: QA budget exhausted — task "
            f"{qa_task['name']} is already in tasks/qa/. Resolve it before "
            f"claiming another task."
        )

    # WIP ceiling: at most 3 in-progress tasks.
    wip = _count_in_progress(tasks)
    if wip >= 3:
        return (
            f"❌ claim_next blocked: WIP ceiling reached — {wip} tasks "
            f"already in tasks/in-progress/. Complete one before claiming."
        )

    # Perform the move.
    src = Path(task["path"])
    dest_dir = workspace_root / "tasks" / "in-progress"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / task["name"]

    try:
        result = subprocess.run(
            ["git", "mv", str(src), str(dest)],
            capture_output=True,
            text=True,
            cwd=str(workspace_root),
        )
        if result.returncode != 0:
            # Fallback: filesystem mv for untracked files.
            if src.exists():
                shutil.move(str(src), str(dest))
            else:
                return (
                    f"❌ claim_next failed: could not move {task['name']}: "
                    f"{result.stderr.strip() or result.stdout.strip()}"
                )
    except Exception as exc:  # noqa: BLE001
        return f"❌ claim_next failed: {exc}."

    # Update the Status header in the moved file.
    try:
        content = dest.read_text(encoding="utf-8")
        content = content.replace("**Status:** open", "**Status:** in-progress", 1)
        dest.write_text(content, encoding="utf-8")
    except OSError:
        pass  # Header update is best-effort; the move itself succeeded.

    overdue = []
    for candidate in _load_all_tasks(workspace_root):
        if candidate.get("lane") not in ("backlog", "in-progress", "qa"):
            continue
        raw = candidate.get("deadline")
        if not raw:
            continue
        try:
            if date.fromisoformat(str(raw)) < date.today():
                overdue.append(str(_task_brief(candidate).get("id")))
        except ValueError:
            continue
    warning = (
        f" ⚠️ OVERDUE: {', '.join(overdue[:3])}" + (" …" if len(overdue) > 3 else "")
        if overdue
        else ""
    )
    return (
        f"✅ claim_next succeeded: task {task_id} ('{task.get('title')}') "
        f"moved to tasks/in-progress/. Status: in-progress.{warning}"
    )


@_project_tool
def plan_status(project_root: Optional[str] = None) -> str:
    """Report Kanban lanes, QA queue, capacity vs. estimate, milestones,
    and blocker list from Markdown tasks.

    Args:
        project_root: Absolute path to the project holding tasks/.

    Returns:
        A markdown-formatted status report.
    """
    workspace_root = _explicit_project_root(project_root, "plan_status")
    tasks = _load_all_tasks(workspace_root)

    lanes: dict[str, list[dict]] = {lane: [] for lane in TASK_LANES}
    for t in tasks:
        lane = t.get("lane") or "unknown"
        lanes.setdefault(lane, []).append(t)

    # Remaining work = everything not yet closed and not archived.
    open_tasks = [
        t for lane in ("backlog", "in-progress", "qa") for t in lanes.get(lane, [])
    ]
    remaining_est = sum(
        (t.get("estimate_hours") or 0) for t in open_tasks if t.get("estimate_hours")
    )

    lines: list[str] = []
    lines.append("# Planner Status")
    lines.append("")
    lines.append("## Kanban Lanes")
    lane_labels = {
        "backlog": "Backlog",
        "in-progress": "In Progress",
        "qa": "QA / Review",
        "completed": "Completed",
        "archive": "Archive",
    }
    for lane in TASK_LANES:
        items = lanes.get(lane, [])
        lines.append(f"### {lane_labels.get(lane, lane)} ({len(items)})")
        for t in items:
            est = f"{t.get('estimate_hours')}h" if t.get("estimate_hours") else "—"
            lines.append(f"- {t['name']} — {t.get('title') or 'untitled'} [{est}]")
        lines.append("")

    lines.append("## Capacity")
    lines.append(f"Total tasks: {len(tasks)}")
    lines.append(f"In-progress: {_count_in_progress(tasks)}")
    lines.append(f"QA pending: {_count_qa_pending(tasks)}")
    lines.append(f"Open tasks: {len(open_tasks)}")
    lines.append(
        f"Estimated remaining: {remaining_est:.1f}h of "
        f"{_WEEKLY_CAPACITY_HOURS:.0f}h weekly capacity"
    )
    if remaining_est > _WEEKLY_CAPACITY_HOURS:
        lines.append(
            f"⚠️ Over capacity by {remaining_est - _WEEKLY_CAPACITY_HOURS:.1f}h "
            "— trim the backlog before claiming new work."
        )
    lines.append("")

    lines.append("## Blockers")
    blocker_count = 0
    for t in tasks:
        if t.get("lane") == "qa":
            lines.append(f"- {t['name']} — awaiting QA/review in tasks/qa/.")
            blocker_count += 1
        deps_met, unmet = _deps_met(t, tasks)
        if not deps_met and t.get("lane") != "completed":
            lines.append(
                f"- {t['name']} — blocked on unmet dependencies: {', '.join(unmet)}."
            )
            blocker_count += 1
    if blocker_count == 0:
        lines.append("- None.")
    lines.append("")

    lines.append("## Milestones")
    milestones: dict[str, list[dict]] = {}
    for t in tasks:
        m = t.get("milestone")
        if m:
            milestones.setdefault(m, []).append(t)
    if not milestones:
        lines.append("- None defined.")
    else:
        for ms, items in sorted(milestones.items()):
            done = sum(1 for i in items if i.get("status") == "closed")
            lines.append(f"- {ms}: {len(items)} task(s), {done} completed.")
    lines.append("")

    return "\n".join(lines)


@_project_tool
def sprint_stats(project_root: Optional[str] = None) -> str:
    """Compute hours spent, progress percentage, and velocity.

    Args:
        project_root: Absolute path to the project holding tasks/.

    Returns:
        A markdown-formatted stats report.
    """
    workspace_root = _explicit_project_root(project_root, "sprint_stats")
    tasks = _load_all_tasks(workspace_root)

    total_tasks = len(tasks)
    completed = sum(1 for t in tasks if t.get("status") == "closed")
    in_progress = _count_in_progress(tasks)
    qa_pending = _count_qa_pending(tasks)
    backlog_count = sum(1 for t in tasks if t.get("lane") == "backlog")

    total_est = sum(
        (t.get("estimate_hours") or 0) for t in tasks if t.get("estimate_hours")
    )
    completed_est = sum(
        (t.get("estimate_hours") or 0)
        for t in tasks
        if t.get("status") == "closed" and t.get("estimate_hours")
    )

    pct = (completed / total_tasks * 100) if total_tasks else 0.0

    lines: list[str] = []
    lines.append("# Sprint Stats")
    lines.append("")
    lines.append(f"Total tasks: {total_tasks}")
    lines.append(f"Completed: {completed} ({pct:.0f}%)")
    lines.append(f"In-progress: {in_progress}")
    lines.append(f"Backlog: {backlog_count}")
    lines.append(f"QA pending: {qa_pending}")
    lines.append("")
    lines.append("## Estimates")
    lines.append(f"Total estimated: {total_est}h")
    lines.append(f"Completed estimated: {completed_est}h")
    lines.append("")
    lines.append("## Velocity")
    lines.append(f"Tasks completed per lane snapshot: {completed} / {total_tasks}")
    lines.append("")
    lines.append(
        "Note: velocity is derived from task status transitions in "
        "tasks/ Markdown; no external time-tracking is integrated in v1."
    )
    return "\n".join(lines)


@_project_tool
def qa_budget(project_root: Optional[str] = None) -> str:
    """Return the QA budget status: count of QA-pending tasks.

    The autopilot QA budget allows at most 1 unresolved QA/review task.
    Returns the count and whether the budget is exhausted.

    Args:
        project_root: Absolute path to the project holding tasks/.

    Returns:
        Budget status message.
    """
    workspace_root = _explicit_project_root(project_root, "qa_budget")
    tasks = _load_all_tasks(workspace_root)
    pending = _count_qa_pending(tasks)
    budget = 1
    if pending >= budget:
        qa_task = next((t for t in tasks if t.get("lane") == "qa"), None)
        name = qa_task["name"] if qa_task else "unknown"
        return (
            f"❌ QA budget exhausted: {pending} task(s) in tasks/qa/ "
            f"(budget: {budget}). Oldest pending: {name}. "
            f"Resolve before claiming new work."
        )
    return (
        f"✅ QA budget OK: {pending}/{budget} task(s) in tasks/qa/. "
        f"Room for {budget - pending} more."
    )


@_project_tool
def milestone_status(project_root: Optional[str] = None) -> str:
    """Summarize milestone status across all tasks.

    Groups tasks by their **Milestone:** field and reports completion
    percentage per milestone.

    Args:
        project_root: Absolute path to the project holding tasks/.

    Returns:
        Milestone status report.
    """
    workspace_root = _explicit_project_root(project_root, "milestone_status")
    tasks = _load_all_tasks(workspace_root)

    milestones: dict[str, list[dict]] = {}
    for t in tasks:
        m = t.get("milestone")
        if m:
            milestones.setdefault(m, []).append(t)

    if not milestones:
        return "## Milestone Status\n\nNo milestones defined."

    lines: list[str] = ["# Milestone Status", ""]
    for name, items in sorted(milestones.items()):
        total = len(items)
        done = sum(1 for i in items if i.get("status") == "closed")
        pct = (done / total * 100) if total else 0.0
        lines.append(f"## {name}")
        lines.append(f"- Tasks: {total}, completed: {done} ({pct:.0f}%)")
        for it in items:
            status = it.get("status") or "open"
            lines.append(
                f"  - {it['name']} — {it.get('title') or 'untitled'} [{status}]"
            )
        lines.append("")

    return "\n".join(lines)


@_project_tool
def sprint_lock(sprint_id: str, project_root: Optional[str] = None) -> str:
    """Mark a sprint as locked (no further changes allowed).

    In v1 this is a declarative operation: it records the lock in the
    planner index and prevents `claim_next` from starting new work until
    the lock is cleared. The actual lock state is tracked in
    tasks/.plan/index.json.

    Args:
        sprint_id: Identifier of the sprint to lock.
        project_root: Absolute path to the project holding tasks/.

    Returns:
        Confirmation message.
    """
    workspace_root = _explicit_project_root(project_root, "sprint_lock")
    plan_dir = workspace_root / "tasks" / ".plan"
    plan_dir.mkdir(parents=True, exist_ok=True)
    lock_file = plan_dir / f"sprint-{sprint_id}.lock"
    lock_file.write_text(
        json.dumps({"sprint_id": sprint_id, "locked_at": date.today().isoformat()}),
        encoding="utf-8",
    )
    return (
        f"✅ Sprint '{sprint_id}' locked. No new tasks can be claimed until unlocked."
    )


@_project_tool
def sprint_daily_agenda(project_root: Optional[str] = None) -> str:
    """Return locked task(s) for today's quota.

    Reads the saved week plan first: today's committed tasks and any deviation
    (committed but not claimed, or claimed but not committed) lead the answer.
    Without a saved plan it falls back to the derived lanes and says so.

    Lists in-progress tasks and any QA-pending tasks that must be resolved
    before new work can be claimed.

    Args:
        project_root: Absolute path to the project holding tasks/.

    Returns:
        Daily agenda report.
    """
    workspace_root = _explicit_project_root(project_root, "sprint_daily_agenda")
    tasks = _load_all_tasks(workspace_root)

    in_progress = [t for t in tasks if t.get("lane") == "in-progress"]
    qa_pending = [t for t in tasks if t.get("lane") == "qa"]

    lines: list[str] = ["# Daily Agenda", ""]
    week_plan = _read_week_plan(workspace_root, _plan_week_key())
    if week_plan:
        today_key = date.today().isoformat()
        committed_today = [
            task_id
            for task_id, day_key in (week_plan.get("deadline_edits") or {}).items()
            if str(day_key) == today_key
        ]
        by_id = {str(_task_brief(t).get("id")): t for t in tasks}
        lines.append(f"## Today's commitment ({week_plan.get('week')})")
        if committed_today:
            for task_id in committed_today:
                task = by_id.get(str(task_id))
                lane = task.get("lane") if task else "missing"
                lines.append(
                    f"- {task_id} — {(task.get('title') if task else 'unknown task') or 'untitled'} [{lane}]"
                )
        else:
            lines.append("- No task is committed to today in the saved plan.")
        committed_ids = {str(i) for i in (week_plan.get("deadline_edits") or {})}
        deviations = [
            f"- {t['name']}: claimed but not in the committed plan"
            for t in in_progress
            if str(_task_brief(t).get("id")) not in committed_ids
        ]
        if deviations:
            lines.append("")
            lines.append("## Deviations")
            lines.extend(deviations)
        if not week_plan.get("approved_at"):
            lines.append("")
            lines.append("- Plan is saved but not approved yet.")
        lines.append("")
    else:
        lines.append("- No saved week plan; using the derived lanes.")
        lines.append("")
    if in_progress:
        lines.append("## In Progress")
        for t in in_progress:
            lines.append(f"- {t['name']} — {t.get('title') or 'untitled'}")
        lines.append("")
    if qa_pending:
        lines.append("## QA Pending (resolve before claiming new work)")
        for t in qa_pending:
            lines.append(f"- {t['name']} — {t.get('title') or 'untitled'}")
        lines.append("")
    if not in_progress and not qa_pending:
        backlog = [t for t in tasks if t.get("lane") == "backlog"]
        if backlog:
            lines.append(
                f"- NUDGE: nothing is claimed and {len(backlog)} task(s) wait in backlog. "
                f"Top: {backlog[0]['name']} — {backlog[0].get('title') or 'untitled'}."
            )
        overdue_ids = []
        for task in tasks:
            raw = task.get("deadline")
            if not raw or task.get("lane") not in ("backlog", "in-progress", "qa"):
                continue
            try:
                if date.fromisoformat(str(raw)) < date.today():
                    overdue_ids.append(str(_task_brief(task).get("id")))
            except ValueError:
                continue
        if overdue_ids:
            lines.append(f"- OVERDUE: {', '.join(overdue_ids[:5])}")
        if not backlog and not overdue_ids:
            lines.append(
                "- Nothing in progress or awaiting QA. Ready to claim next task."
            )
    return "\n".join(lines)


@_project_tool
def sprint_check_daily_quota(project_root: Optional[str] = None) -> str:
    """Check if today's planned tasks are complete.

    Signals DAILY_QUOTA_REACHED when all in-progress tasks are closed and
    no QA-pending tasks remain.

    Args:
        project_root: Absolute path to the project holding tasks/.

    Returns:
        Quota status message.
    """
    workspace_root = _explicit_project_root(project_root, "sprint_check_daily_quota")
    tasks = _load_all_tasks(workspace_root)

    in_progress = [t for t in tasks if t.get("lane") == "in-progress"]
    qa_pending = [t for t in tasks if t.get("lane") == "qa"]

    if not in_progress and not qa_pending:
        return "✅ DAILY_QUOTA_REACHED: no in-progress or QA-pending tasks."
    parts: list[str] = []
    if in_progress:
        parts.append(
            f"{len(in_progress)} in-progress: "
            + ", ".join(t.get("title") or t["name"] for t in in_progress)
        )
    if qa_pending:
        parts.append(
            f"{len(qa_pending)} QA-pending: "
            + ", ".join(t.get("title") or t["name"] for t in qa_pending)
        )
    return f"⏳ Quota not reached — still open: {'; '.join(parts)}."


# ---------------------------------------------------------------------------
# Authentication, RBAC, and per-user project scoping (optional, off by default)
# ---------------------------------------------------------------------------

_USERS_CONFIG_ENV = "PLANNER_USERS_CONFIG"
_DEFAULT_USERS_RELATIVE = Path(".config") / "opencode" / "planner-users.json"

SESSION_COOKIE = "planner_session"
SESSION_TTL_SECONDS = 7 * 24 * 3600

_PBKDF2_ALGORITHM = "sha256"
_PBKDF2_ITERATIONS = 600_000

# In-memory token -> session store. Sessions deliberately do not survive a
# restart: a restart is an operator action and re-login is cheap.
_SESSIONS: dict = {}

_USER_CONFIG: dict = {"auth_enabled": False}
_AUTH_ENABLED: bool = False


def _users_config_path() -> Path:
    """Return the users config path: ``PLANNER_USERS_CONFIG`` or the home default.

    Resolved per call (never cached at import) so tests and operators can
    redirect it without reimporting the module.
    """
    env = os.environ.get(_USERS_CONFIG_ENV, "").strip()
    if env:
        return Path(env).expanduser()
    return Path.home() / _DEFAULT_USERS_RELATIVE


def _hash_password(password: str) -> tuple[str, str]:
    """Hash a password with PBKDF2-HMAC-SHA256 and a fresh 16-byte salt.

    Returns ``(salt_hex, hash_hex)``. Stdlib only — no third-party crypto.
    """
    salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac(
        _PBKDF2_ALGORITHM,
        password.encode("utf-8"),
        salt,
        _PBKDF2_ITERATIONS,
    )
    return salt.hex(), derived.hex()


def _verify_password(password: str, salt_hex: str, hash_hex: str) -> bool:
    """Constant-time verification of a password against a stored salt + hash.

    Returns False on any malformed stored value instead of raising, so a
    corrupt config entry denies access rather than crashing the handler.
    """
    if not password or not salt_hex or not hash_hex:
        return False
    try:
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
    except (ValueError, TypeError):
        return False
    derived = hashlib.pbkdf2_hmac(
        _PBKDF2_ALGORITHM, password.encode("utf-8"), salt, _PBKDF2_ITERATIONS
    )
    return hmac.compare_digest(derived, expected)


def _load_user_config() -> dict:
    """Load the users config, failing closed to open local mode.

    A missing file, unreadable file, invalid JSON, or non-object payload all
    mean "no auth configured": the server keeps behaving exactly as it did
    before auth existed.
    """
    path = _users_config_path()
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return {"auth_enabled": False}
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return {"auth_enabled": False}
    if not isinstance(data, dict):
        return {"auth_enabled": False}
    users = data.get("users")
    if not isinstance(users, list):
        users = []
    return {
        "auth_enabled": bool(data.get("auth_enabled", False)),
        "users": users,
    }


def _find_user(config: dict, username: str) -> Optional[dict]:
    """Return the user record matching ``username``, or None."""
    if not isinstance(config, dict) or not username:
        return None
    for user in config.get("users") or []:
        if isinstance(user, dict) and user.get("username") == username:
            return user
    return None


class AuthState:
    """Per-request authentication and authorization view.

    ``user`` is None for an unauthenticated request. Project authorization
    follows the user's ``allowed_projects``: ``"*"`` grants every project,
    any other entry grants that directory and everything beneath it.
    """

    def __init__(self, config: dict, user: Optional[dict], sessions: dict):
        self.config = config or {}
        self.user = user or None
        self.sessions = sessions

    @property
    def authenticated(self) -> bool:
        return self.user is not None

    @property
    def username(self) -> str:
        return str((self.user or {}).get("username") or "")

    @property
    def role(self) -> str:
        return str((self.user or {}).get("role") or "")

    @property
    def is_admin(self) -> bool:
        return self.authenticated and self.role == "admin"

    @property
    def allowed_projects(self) -> list[str]:
        raw = (self.user or {}).get("allowed_projects") or []
        if isinstance(raw, str):
            raw = [raw]
        if not isinstance(raw, (list, tuple)):
            return []
        out: list[str] = []
        for entry in raw:
            value = str(entry).strip()
            if value and value not in out:
                out.append(value)
        return out

    def project_allowed(self, path) -> bool:
        """True when this session may read ``path`` (itself or a subdirectory)."""
        if not self.authenticated:
            return False
        allowed = self.allowed_projects
        if "*" in allowed:
            return True
        try:
            target = Path(path).expanduser().resolve()
        except OSError:
            return False
        for entry in allowed:
            if entry == "*":
                continue
            try:
                base = Path(entry).expanduser().resolve()
            except OSError:
                continue
            if target == base or base in target.parents:
                return True
        return False


def _build_auth_url_map() -> dict:
    """Return the live token -> session map (the module-level session store)."""
    return _SESSIONS


def _session_from_token(token: str) -> Optional[dict]:
    """Return a live session for ``token``, dropping it when expired."""
    if not token:
        return None
    session = _SESSIONS.get(token)
    if session is None:
        return None
    created = float(session.get("created") or 0.0)
    if created and (time.time() - created) > SESSION_TTL_SECONDS:
        _SESSIONS.pop(token, None)
        return None
    return session


def _invalidate_token(token: str) -> None:
    """Remove ``token`` from the session store (logout)."""
    if token:
        _SESSIONS.pop(token, None)


def _refresh_auth_config() -> None:
    """Reload the users config into the module globals.

    Auth is enabled only when the file says so *and* at least one user is
    defined — ``auth_enabled: true`` with an empty user list would lock every
    caller out with no way back in except editing the file.
    """
    global _USER_CONFIG, _AUTH_ENABLED
    _USER_CONFIG = _load_user_config()
    _AUTH_ENABLED = bool(_USER_CONFIG.get("auth_enabled")) and bool(
        _USER_CONFIG.get("users")
    )


def _cookie_from_header(header: str, name: str) -> str:
    """Extract one cookie value from a raw ``Cookie`` header."""
    for chunk in (header or "").split(";"):
        key, _, value = chunk.strip().partition("=")
        if key == name:
            return value.strip()
    return ""


def _auth_from_request(request) -> Optional[AuthState]:
    """Build the request's AuthState, or None when auth is disabled.

    None means "open local mode": no session, no filtering, no 401/403.
    """
    if not _AUTH_ENABLED:
        return None
    token = request.cookies.get(SESSION_COOKIE, "")
    session = _session_from_token(token)
    return AuthState(_USER_CONFIG, (session or {}).get("user"), _SESSIONS)


# ---------------------------------------------------------------------------
# Embedded Starlette app: static dashboard + FastMCP HTTP endpoint
# ---------------------------------------------------------------------------

_STATIC_DIR = Path(__file__).resolve().parent / "static"


def _dashboard_html() -> str:
    """Serve the standalone dashboard HTML (GET /)."""
    index_path = _STATIC_DIR / "index.html"
    if index_path.is_file():
        return index_path.read_text(encoding="utf-8")
    return (
        "<html><body><h1>Planner Dashboard</h1>"
        "<p>static/index.html not found.</p></body></html>"
    )


_PROJECTS_ENV = "PLANNER_PROJECTS"
_PROJECT_ROOT_ENV = "PLANNER_PROJECT_ROOT"

# Daily batch size used by the pacing gauge (autopilot cycle default).
_DAILY_TARGET = int(os.environ.get("PLANNER_DAILY_TARGET", "3") or 3)

# Weekly capacity in hours; the planner's default from the approved plan.
_WEEKLY_CAPACITY_HOURS = float(os.environ.get("PLANNER_WEEKLY_CAPACITY", "20") or 20)


def _relative_root(project_root: Optional[str]) -> bool:
    """True when an explicit ``?project_root=`` is present but not absolute.

    ``_resolve_dashboard_root`` runs ``Path(...).resolve()`` on whatever it is
    given, so a relative value silently resolved against the daemon's working
    directory and reported an empty project. The routes reject it as a 400
    before resolution instead of answering with the wrong board.
    """
    if not project_root or not project_root.strip():
        return False
    try:
        return not Path(project_root).expanduser().is_absolute()
    except OSError:
        return True


def _is_https(request) -> bool:
    """True when the request reached the app over HTTPS.

    The dashboard sits behind a Cloudflare Tunnel, so the origin sees plain
    HTTP and must trust ``X-Forwarded-Proto``. Used to decide the session
    cookie's ``Secure`` flag and whether HSTS may be sent.
    """
    proto = (request.headers.get("x-forwarded-proto") or "").split(",")[0].strip()
    if proto:
        return proto.lower() == "https"
    return request.url.scheme == "https"


def _resolve_dashboard_root(project_root: Optional[str] = None) -> Path:
    """Resolve the project root the dashboard reports on.

    Resolution order:

    1. an explicit ``project_root`` (the ``?project_root=`` query parameter),
    2. the ``PLANNER_PROJECT_ROOT`` environment variable,
    3. the nearest ancestor of the current working directory that holds a
       ``tasks/`` directory,
    4. the current working directory.

    The walk-up step matters because the supervised singleton runs with its
    WorkingDirectory set to the install directory, which holds no ``tasks/``;
    without it the dashboard would always report an empty board.

    Args:
        project_root: Optional absolute path supplied by the dashboard.

    Returns:
        The resolved project root as an absolute Path.
    """
    if project_root and project_root.strip():
        return Path(project_root).expanduser().resolve()

    env_root = os.environ.get(_PROJECT_ROOT_ENV, "").strip()
    if env_root:
        return Path(env_root).expanduser().resolve()

    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / "tasks").is_dir():
            return candidate
    return cwd


def _discover_projects(current: Path, auth: Optional[AuthState] = None) -> list[dict]:
    """List the project roots selectable in the dashboard switcher.

    Sources the ``PLANNER_PROJECTS`` environment variable (absolute paths
    separated by ``os.pathsep``) plus the currently resolved root. Entries are
    de-duplicated, and paths that do not exist or hold no ``tasks/`` directory
    are dropped, so the selector never offers a dead target. When ``auth`` is
    given, entries outside the session's ``allowed_projects`` are dropped too.

    Args:
        current: The project root currently being reported on.
        auth: Optional session view used to filter the list.

    Returns:
        A list of ``{"path": ..., "label": ...}`` dicts, current first.
    """
    roots: list[Path] = [current]
    raw = os.environ.get(_PROJECTS_ENV, "")
    for chunk in raw.split(os.pathsep):
        chunk = chunk.strip()
        if not chunk:
            continue
        roots.append(Path(chunk).expanduser().resolve())

    seen: set[Path] = set()
    projects: list[dict] = []
    for root in roots:
        if root in seen:
            continue
        seen.add(root)
        if not (root / "tasks").is_dir():
            continue
        if auth is not None and not auth.project_allowed(root):
            continue
        projects.append({"path": str(root), "label": root.name})
    return projects


def _first_allowed_root(auth: AuthState) -> Optional[Path]:
    """Return the first existing directory in the session's allowed projects."""
    for entry in auth.allowed_projects:
        if entry == "*":
            continue
        try:
            candidate = Path(entry).expanduser().resolve()
        except OSError:
            continue
        if candidate.is_dir():
            return candidate
    return None


def _task_brief(task: dict) -> dict:
    """Project a parsed task record onto the fields the dashboard renders.

    Args:
        task: A record returned by :func:`_parse_task_file`.

    Returns:
        A JSON-serialisable summary carrying the task id, title, lane,
        status, estimate, deadline, and milestone.
    """
    name = task.get("name") or ""
    match = TASK_ID_RE.match(name)
    return {
        "id": match.group(1) if match else name,
        "name": name,
        "path": task.get("path"),
        "title": task.get("title") or "untitled",
        "lane": task.get("lane"),
        "status": task.get("status") or "open",
        "estimate_hours": task.get("estimate_hours"),
        "owner": task.get("owner"),
        "deadline": task.get("deadline"),
        "milestone": task.get("milestone"),
    }


def _safe_task_path(root: Path, rel_path: str) -> Optional[Path]:
    """Resolve a lane-relative task Markdown path, or ``None`` when unsafe.

    The dashboard may deep-link a task by path, so the value arrives from the
    query string and must never become a file-read primitive. Only three
    shapes are accepted: ``tasks/<lane>/<file>.md`` where ``<lane>`` is one of
    :data:`TASK_LANES` and the file name carries no path separators. Absolute
    paths, Windows drive paths, backslashes, ``..`` segments, extra nesting,
    and non-Markdown suffixes are all rejected. The final candidate is resolved
    and must still sit inside ``root``.

    Args:
        root: The resolved project root the request is scoped to.
        rel_path: The ``?path=`` query value, e.g. ``tasks/qa/0339-x.md``.

    Returns:
        The resolved :class:`Path` when it is a safe in-tree task file, else
        ``None`` (the caller maps that to 403 to avoid an existence oracle).
    """
    if not rel_path or not isinstance(rel_path, str):
        return None
    rel = rel_path.strip()
    if not rel or rel.startswith("/") or rel.startswith("\\") or ":" in rel:
        return None
    if "\\" in rel:
        return None
    parts = [part for part in rel.split("/") if part]
    if ".." in parts or "." in parts:
        return None
    if len(parts) != 3 or parts[0] != "tasks" or parts[1] not in TASK_LANES:
        return None
    if not parts[2].endswith(".md"):
        return None
    try:
        base = root.resolve()
        candidate = (base / parts[0] / parts[1] / parts[2]).resolve()
    except OSError:
        return None
    if candidate != base and base not in candidate.parents:
        return None
    return candidate


def _api_task(
    project_root: Optional[str] = None,
    task_id: Optional[str] = None,
    rel_path: Optional[str] = None,
    auth: Optional[AuthState] = None,
) -> dict:
    """Return one task file as JSON (GET /api/task).

    The dashboard's task modal needs the raw Markdown of a task, including the
    ``## Factual Git Diff`` section, so this route returns the parsed record's
    ``raw`` text verbatim alongside its identity fields. ``id`` wins over
    ``path`` when both are present.

    Error contract (mapped to status codes by the route):

    * ``missing param`` -> 400 when neither ``id`` nor ``path`` is given,
    * ``unauthenticated`` -> 401 when auth is enabled and no session cookie,
    * ``forbidden`` -> 403 when the root is outside the session's grants or
      the requested path fails the containment guard (never 404, so the route
      cannot be used to probe for file existence),
    * ``not found`` -> 404 for an unknown id or a safe path that does not exist,
    * ``internal error`` -> 500, never a 200 envelope.

    Args:
        project_root: Optional absolute root from ``?project_root=``.
        task_id: Optional numeric-ish task id from ``?id=``.
        rel_path: Optional ``tasks/<lane>/<file>.md`` from ``?path=``.
        auth: Optional session view; ``None`` means open local mode.

    Returns:
        A JSON-serialisable dict; on failure a dict with an ``error`` key.
    """
    if not task_id and not rel_path:
        return {"error": "missing param: id or path required"}
    if auth is not None and not auth.authenticated:
        return {"error": "unauthenticated"}

    workspace_root = _resolve_dashboard_root(project_root)
    if auth is not None and not auth.project_allowed(workspace_root):
        if project_root and project_root.strip():
            return {"error": "forbidden"}
        fallback = _first_allowed_root(auth)
        if fallback is None:
            return {"error": "forbidden"}
        workspace_root = fallback

    try:
        if task_id:
            record = _find_task_by_id(
                _load_all_tasks(workspace_root), str(task_id).strip()
            )
            if record is None:
                return {"error": "not found"}
        else:
            safe_path = _safe_task_path(workspace_root, str(rel_path))
            if safe_path is None:
                return {"error": "forbidden"}
            if not safe_path.is_file():
                return {"error": "not found"}
            record = _parse_task_file(safe_path)
            if record.get("error"):
                return {"error": "not found"}

        name = record.get("name") or ""
        match = TASK_ID_RE.match(name)
        return {
            "id": match.group(1) if match else name,
            "path": record.get("path"),
            "lane": record.get("lane"),
            "title": record.get("title") or "untitled",
            "markdown": record.get("raw") or "",
        }
    except Exception:  # noqa: BLE001 - surface as 500, never a 200 envelope
        return {"error": "internal error"}


_PLAN_WINDOWS = ("day", "week", "month")


def _empty_bucket(day: date) -> dict:
    """One planning bucket; ``jalali`` is filled by the client."""
    return {
        "date": day.isoformat(),
        "jalali": None,
        "open": 0,
        "in_progress": 0,
        "done": 0,
        "estimate_hours": 0.0,
        "tasks": [],
    }


def _hours(value) -> float:
    """Best-effort hours; malformed values count as zero, never crash."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


_PLAN_DIR_NAME = ".plan"


def _plan_week_key(day: Optional[date] = None) -> str:
    """ISO week key for a date, e.g. ``2026-W43``."""
    target = day or date.today()
    iso = target.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def _plan_file(root: Path, week: str) -> Path:
    return root / "tasks" / _PLAN_DIR_NAME / f"week-{week}.json"


def _read_week_plan(root: Path, week: Optional[str] = None) -> Optional[dict]:
    """Return the saved commitment for ``week`` (default: current week)."""
    key = week or _plan_week_key()
    path = _plan_file(root, key)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _write_week_plan(root: Path, plan: dict) -> Path:
    """Atomically persist a week plan (temp file + rename)."""
    key = str(plan.get("week") or _plan_week_key())
    plan["week"] = key
    path = _plan_file(root, key)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(plan, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)
    return path


def _validate_plan_edits(root: Path, body: dict) -> tuple[dict, Optional[str]]:
    """Validate and normalise a plan save request.

    Accepts ``{week?, deadline_edits?, capacity_by_day?, approved?, force?}``
    where ``deadline_edits`` maps a task id to ``YYYY-MM-DD`` and
    ``capacity_by_day`` maps a date to hours. Returns ``(plan, error)``.
    """
    week = str(body.get("week") or _plan_week_key())
    if not re.fullmatch(r"\d{4}-W\d{2}", week):
        return {}, "week must look like 2026-W43"
    tasks = {str(_task_brief(t).get("id")): t for t in _load_all_tasks(root)}
    deadline_edits = body.get("deadline_edits") or {}
    capacity_by_day = body.get("capacity_by_day") or {}
    if not isinstance(deadline_edits, dict) or not isinstance(capacity_by_day, dict):
        return {}, "deadline_edits and capacity_by_day must be objects"
    for task_id, deadline in deadline_edits.items():
        if str(task_id) not in tasks:
            return {}, f"unknown task id {task_id}"
        try:
            date.fromisoformat(str(deadline))
        except ValueError:
            return {}, f"invalid deadline for {task_id}: {deadline}"
    for day_key, hours in capacity_by_day.items():
        try:
            date.fromisoformat(str(day_key))
            _hours(hours)
        except (ValueError, TypeError):
            return {}, f"invalid capacity entry {day_key}"
    total_estimate = 0.0
    for task_id in deadline_edits:
        total_estimate += _hours(tasks[str(task_id)].get("estimate_hours"))
    capacity_total = sum(_hours(v) for v in capacity_by_day.values())
    if capacity_total and total_estimate > capacity_total and not body.get("force"):
        return {}, (
            f"over capacity: {total_estimate:.1f}h assigned vs "
            f"{capacity_total:.1f}h capacity (pass force to override)"
        )
    previous = _read_week_plan(root, week) or {}
    merged_edits = (
        {str(k): str(v) for k, v in deadline_edits.items()}
        if body.get("replace")
        else {
            **(previous.get("deadline_edits") or {}),
            **{str(k): str(v) for k, v in deadline_edits.items()},
        }
    )
    merged_capacity = (
        {str(k): _hours(v) for k, v in capacity_by_day.items()}
        if body.get("replace")
        else {
            **(previous.get("capacity_by_day") or {}),
            **{str(k): _hours(v) for k, v in capacity_by_day.items()},
        }
    )
    merged_estimate = sum(
        _hours(tasks[str(task_id)].get("estimate_hours"))
        for task_id in merged_edits
        if str(task_id) in tasks
    )
    merged_capacity_total = sum(merged_capacity.values())
    if (
        merged_capacity_total
        and merged_estimate > merged_capacity_total
        and not body.get("force")
    ):
        return {}, (
            f"over capacity: {merged_estimate:.1f}h assigned vs "
            f"{merged_capacity_total:.1f}h capacity (pass force to override)"
        )
    plan = {
        "week": week,
        "deadline_edits": merged_edits,
        "capacity_by_day": merged_capacity,
        "notes": body.get("notes", previous.get("notes", "")),
        "approved_at": previous.get("approved_at"),
        "approved_by": previous.get("approved_by"),
    }
    if body.get("approved"):
        plan["approved_at"] = datetime.now(timezone.utc).isoformat()
        plan["approved_by"] = str(body.get("approved_by") or "manager")
    return plan, None


def _plan_payload(
    project_root: Optional[str] = None,
    window: str = "week",
    auth=None,
    plan_week: Optional[str] = None,
) -> dict:
    """Return day/week/month planning buckets (``GET /api/plan``).

    Completion history is not stored in the task files, so "done" means a task
    that sits in the ``completed`` lane and carries a deadline inside the
    bucket. That limitation is part of the contract and is stated in the README
    and in the dashboard, rather than being papered over with a fake timestamp.

    Args:
        project_root: Optional absolute root from ``?project_root=``.
        window: ``day``, ``week`` or ``month`` (validated by the route).
        auth: Optional session view; ``None`` is open local mode.

    Returns:
        ``{project_root, window, generated_at, days, weeks, totals, alerts,
        trend}`` or ``{"error": ...}``.
    """
    if auth is not None and not auth.authenticated:
        return {"error": "unauthenticated"}
    root = _resolve_dashboard_root(project_root)
    if auth is not None and not auth.project_allowed(root):
        if project_root and project_root.strip():
            return {"error": "forbidden"}
        fallback = _first_allowed_root(auth)
        if fallback is None:
            return {"error": "forbidden"}
        root = fallback

    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    capacity = float(_WEEKLY_CAPACITY_HOURS or 0)

    buckets: dict[str, dict] = {}
    open_lanes = ("backlog", "in-progress", "qa")

    def bucket_for(day: date) -> dict:
        key = day.isoformat()
        if key not in buckets:
            buckets[key] = _empty_bucket(day)
        return buckets[key]

    alerts = {"overdue": [], "today": [], "soon": []}
    undated: list[tuple[dict, str]] = []
    for task in _load_all_tasks(root):
        lane = task.get("lane")
        brief = _task_brief(task)
        deadline_raw = task.get("deadline")
        try:
            deadline = date.fromisoformat(str(deadline_raw)) if deadline_raw else None
        except ValueError:
            deadline = None
        if deadline is not None:
            bucket = bucket_for(deadline)
            bucket["tasks"].append(brief)
            bucket["estimate_hours"] += _hours(task.get("estimate_hours"))
            if lane == "completed":
                bucket["done"] += 1
            elif lane == "in-progress":
                bucket["in_progress"] += 1
            elif lane in open_lanes:
                bucket["open"] += 1
        if lane in open_lanes and deadline is not None:
            delta = (deadline - today).days
            if delta < 0:
                alerts["overdue"].append(brief)
            elif delta == 0:
                alerts["today"].append(brief)
            elif delta <= 3:
                alerts["soon"].append(brief)
        elif lane in open_lanes:
            undated.append((task, brief))

    if window == "day":
        days = [today]
    elif window == "week":
        days = [week_start + timedelta(days=offset) for offset in range(7)]
    else:
        first = today.replace(day=1)
        next_month = (first + timedelta(days=32)).replace(day=1)
        days = [first + timedelta(days=i) for i in range((next_month - first).days)]

    day_rows = [bucket_for(day) for day in days]

    # Undated open work is what "still to do" means in practice: most task
    # files carry no deadline, so counting deadlines alone would render an
    # empty cockpit. Attribute it to the current bucket (today, this week, or
    # the month's first day) and keep the count honest in ``totals``.
    anchor = today if window == "day" else (week_start if window == "week" else days[0])
    anchor_bucket = bucket_for(anchor)
    for task, brief in undated:
        anchor_bucket["tasks"].append(brief)
        anchor_bucket["estimate_hours"] += _hours(task.get("estimate_hours"))
        if task.get("lane") == "in-progress":
            anchor_bucket["in_progress"] += 1
        else:
            anchor_bucket["open"] += 1

    weeks: list[dict] = []
    if window in ("week", "month"):
        grouped: dict[str, list[dict]] = {}
        for row in day_rows:
            day = date.fromisoformat(row["date"])
            key = (day - timedelta(days=day.weekday())).isoformat()
            grouped.setdefault(key, []).append(row)
        for start_key in sorted(grouped):
            rows = grouped[start_key]
            start = date.fromisoformat(start_key)
            estimate = round(sum(r["estimate_hours"] for r in rows), 2)
            weeks.append(
                {
                    "start": start_key,
                    "end": (start + timedelta(days=6)).isoformat(),
                    "label": f"{start.isocalendar()[0]}-W{start.isocalendar()[1]:02d}",
                    "open": sum(r["open"] for r in rows),
                    "in_progress": sum(r["in_progress"] for r in rows),
                    "done": sum(r["done"] for r in rows),
                    "estimate_hours": estimate,
                    "capacity_hours": capacity,
                    "remaining_hours": round(capacity - estimate, 2),
                }
            )

    trend = []
    for offset in range(13, -1, -1):
        day = today - timedelta(days=offset)
        row = bucket_for(day)
        trend.append(
            {
                "date": day.isoformat(),
                "open": row["open"],
                "in_progress": row["in_progress"],
                "done": row["done"],
                "estimate_hours": round(row["estimate_hours"], 2),
            }
        )

    totals = {
        "open": sum(b["open"] for b in day_rows),
        "in_progress": sum(b["in_progress"] for b in day_rows),
        "done": sum(b["done"] for b in day_rows),
        "estimate_hours": round(sum(b["estimate_hours"] for b in day_rows), 2),
        "capacity_hours": capacity,
    }

    return {
        "project_root": str(root),
        "window": window,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "days": day_rows,
        "weeks": weeks,
        "trend": trend,
        "totals": totals,
        "alerts": alerts,
        "plan": _read_week_plan(root, plan_week or _plan_week_key()),
    }


def _api_status(
    project_root: Optional[str] = None, auth: Optional[AuthState] = None
) -> dict:
    """Return planner status as JSON (GET /api/status).

    The payload is the dashboard's data contract: per-lane task lists (not
    counts — the UI renders each lane as a list), the milestone tree, the
    upcoming deadlines plotted on the timeline, and today's pacing figures.

    Pacing mirrors :func:`sprint_check_daily_quota`: a day is complete when no
    task sits in ``in-progress`` and none waits in ``qa``, so ``done`` is the
    batch target minus the open working set.

    Args:
        project_root: Optional absolute project root from the query string.
        auth: Optional session view. When given, an unauthenticated session
            yields ``{"error": "unauthenticated"}``, an explicitly requested
            root outside the session's allowed projects yields
            ``{"error": "forbidden"}``, and the ``projects`` list is filtered
            to the allowed roots. ``None`` means open local mode.

    Returns:
        A JSON-serialisable dict; on failure a dict with an ``error`` key.
    """
    try:
        if auth is not None and not auth.authenticated:
            return {"error": "unauthenticated"}

        workspace_root = _resolve_dashboard_root(project_root)
        if auth is not None and not auth.project_allowed(workspace_root):
            if project_root and project_root.strip():
                return {"error": "forbidden"}
            # No explicit root: fall back to the first allowed project rather
            # than denying a viewer whose cwd is outside their grants.
            fallback = _first_allowed_root(auth)
            if fallback is None:
                return {"error": "forbidden"}
            workspace_root = fallback

        tasks = _load_all_tasks(workspace_root)

        lanes: dict[str, list[dict]] = {lane: [] for lane in TASK_LANES}
        milestone_tree: dict[str, list[dict]] = {}
        deadlines: list[dict] = []

        for task in tasks:
            brief = _task_brief(task)
            lane = task.get("lane")
            if lane in lanes:
                lanes[lane].append(brief)
            milestone = task.get("milestone")
            if milestone:
                milestone_tree.setdefault(milestone, []).append(brief)
            if task.get("deadline"):
                deadlines.append(brief)

        deadlines.sort(key=lambda t: t.get("deadline") or "")
        open_work = len(lanes["in-progress"]) + len(lanes["qa"])

        return {
            "project_root": str(workspace_root),
            "projects": _discover_projects(workspace_root, auth),
            "total_tasks": len(tasks),
            "in_progress": len(lanes["in-progress"]),
            "qa_pending": len(lanes["qa"]),
            "backlog": len(lanes["backlog"]),
            "completed": len(lanes["completed"]),
            "today": {
                "done": max(0, _DAILY_TARGET - open_work),
                "target": _DAILY_TARGET,
                "open": open_work,
            },
            "lanes": lanes,
            "milestone_tree": milestone_tree,
            "deadlines": deadlines,
        }
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


def _guarded_mcp_app(mcp_app):
    """Wrap the MCP transport app at its trust boundary.

    The transport is deliberately auth-free, in open mode and with auth
    enabled alike: local OpenCode clients call ``/mcp`` on loopback with no
    credentials and must connect. Remote exposure is closed at the network
    edge instead — the Cloudflare Tunnel ingress answers 404 for ``/mcp``
    before the catch-all rule, so the endpoint is never reachable off-host.
    The dashboard and every ``/api/*`` route keep their session checks.
    """

    async def loopback_only(scope, receive, send):
        await mcp_app(scope, receive, send)

    return loopback_only


def build_app():
    """Build the combined Starlette app: dashboard + FastMCP HTTP endpoint."""
    from starlette.applications import Starlette
    from starlette.routing import Mount, Route
    from starlette.responses import HTMLResponse, JSONResponse
    from starlette.staticfiles import StaticFiles
    import uvicorn  # noqa: F401  (ensured available via pyproject)

    # Pick up users-config edits on every (re)build; requests then read the
    # module globals, so the hot path stays a dict lookup.
    _refresh_auth_config()

    async def dashboard(request):
        return HTMLResponse(_dashboard_html())

    async def api_status(request):
        root = request.query_params.get("project_root")
        if _relative_root(root):
            return JSONResponse(
                {"error": "project_root must be absolute"}, status_code=400
            )
        auth = _auth_from_request(request)
        payload = _api_status(root, auth)
        error = payload.get("error")
        if error == "unauthenticated":
            return JSONResponse(payload, status_code=401)
        if error == "forbidden":
            return JSONResponse(payload, status_code=403)
        return JSONResponse(payload)

    async def api_task(request):
        root = request.query_params.get("project_root")
        if _relative_root(root):
            return JSONResponse(
                {"error": "project_root must be absolute"}, status_code=400
            )
        auth = _auth_from_request(request)
        payload = _api_task(
            root,
            request.query_params.get("id"),
            request.query_params.get("path"),
            auth,
        )
        error = payload.get("error")
        if error == "unauthenticated":
            return JSONResponse(payload, status_code=401)
        if error == "forbidden":
            return JSONResponse(payload, status_code=403)
        if error == "not found":
            return JSONResponse(payload, status_code=404)
        if isinstance(error, str) and error.startswith("missing param"):
            return JSONResponse(payload, status_code=400)
        if error == "internal error":
            return JSONResponse(payload, status_code=500)
        return JSONResponse(payload)

    async def api_plan(request):
        root = request.query_params.get("project_root")
        if _relative_root(root):
            return JSONResponse(
                {"error": "project_root must be absolute"}, status_code=400
            )
        window = (request.query_params.get("window") or "week").strip().lower()
        if window not in _PLAN_WINDOWS:
            return JSONResponse({"error": "invalid window"}, status_code=400)
        plan_week = request.query_params.get("week")
        if plan_week and not re.fullmatch(r"\d{4}-W\d{2}", plan_week):
            return JSONResponse(
                {"error": "week must look like 2026-W43"}, status_code=400
            )
        auth = _auth_from_request(request)
        payload = _plan_payload(root, window, auth, plan_week)
        error = payload.get("error")
        if error == "unauthenticated":
            return JSONResponse(payload, status_code=401)
        if error == "forbidden":
            return JSONResponse(payload, status_code=403)
        if error == "internal error":
            return JSONResponse(payload, status_code=500)
        return JSONResponse(payload)

    async def api_plan_save(request):
        if _AUTH_ENABLED:
            auth = _auth_from_request(request)
            if not auth.authenticated:
                return JSONResponse({"error": "unauthenticated"}, status_code=401)
            if not auth.is_admin:
                return JSONResponse({"error": "forbidden"}, status_code=403)
        else:
            auth = None
        try:
            body = await request.json()
        except Exception:  # noqa: BLE001 - any parse failure is a 400
            return JSONResponse({"error": "invalid JSON body"}, status_code=400)
        if not isinstance(body, dict):
            return JSONResponse({"error": "invalid JSON body"}, status_code=400)
        root = _resolve_dashboard_root(None)
        if auth is not None and not auth.project_allowed(root):
            fallback = _first_allowed_root(auth)
            if fallback is None:
                return JSONResponse({"error": "forbidden"}, status_code=403)
            root = fallback
        plan, error = _validate_plan_edits(root, body)
        if error:
            return JSONResponse({"error": error}, status_code=400)
        _write_week_plan(root, plan)
        return JSONResponse(plan)

    async def api_plan_clear(request):
        if _AUTH_ENABLED:
            auth = _auth_from_request(request)
            if not auth.authenticated:
                return JSONResponse({"error": "unauthenticated"}, status_code=401)
            if not auth.is_admin:
                return JSONResponse({"error": "forbidden"}, status_code=403)
        else:
            auth = None
        week = (request.query_params.get("week") or _plan_week_key()).strip()
        if not re.fullmatch(r"\d{4}-W\d{2}", week):
            return JSONResponse(
                {"error": "week must look like 2026-W43"}, status_code=400
            )
        root = _resolve_dashboard_root(None)
        if auth is not None and not auth.project_allowed(root):
            fallback = _first_allowed_root(auth)
            if fallback is None:
                return JSONResponse({"error": "forbidden"}, status_code=403)
            root = fallback
        path = _plan_file(root, week)
        if path.is_file():
            path.unlink()
        return JSONResponse({"cleared": week})

    async def api_login(request):
        if not _AUTH_ENABLED:
            return JSONResponse(
                {
                    "note": "auth disabled",
                    "token": "",
                    "username": "",
                    "role": "",
                    "allowed_projects": [],
                }
            )
        try:
            body = await request.json()
        except Exception:  # noqa: BLE001 - any parse failure is a 400
            return JSONResponse({"error": "invalid JSON body"}, status_code=400)
        if not isinstance(body, dict):
            return JSONResponse({"error": "invalid JSON body"}, status_code=400)

        username = str(body.get("username") or "").strip()
        password = str(body.get("password") or "")
        if not username or not password:
            return JSONResponse(
                {"error": "username and password are required"}, status_code=400
            )

        user = _find_user(_USER_CONFIG, username)
        if user is None or not _verify_password(
            password,
            str(user.get("password_salt") or ""),
            str(user.get("password_hash") or ""),
        ):
            return JSONResponse({"error": "invalid credentials"}, status_code=401)

        token = secrets.token_urlsafe(32)
        _SESSIONS[token] = {"user": user, "created": time.time()}
        state = AuthState(_USER_CONFIG, user, _SESSIONS)
        response = JSONResponse(
            {
                "token": token,
                "username": state.username,
                "role": state.role,
                "allowed_projects": state.allowed_projects,
            }
        )
        response.set_cookie(
            SESSION_COOKIE,
            token,
            max_age=SESSION_TTL_SECONDS,
            httponly=True,
            samesite="lax",
            secure=_is_https(request),
            path="/",
        )
        return response

    async def api_logout(request):
        _invalidate_token(request.cookies.get(SESSION_COOKIE, ""))
        response = JSONResponse({"ok": True})
        response.delete_cookie(SESSION_COOKIE, path="/")
        return response

    async def api_me(request):
        if not _AUTH_ENABLED:
            return JSONResponse(
                {
                    "authenticated": False,
                    "note": "auth disabled",
                    "username": "",
                    "role": "",
                    "allowed_projects": [],
                }
            )
        auth = _auth_from_request(request)
        if not auth.authenticated:
            return JSONResponse({"error": "unauthenticated"}, status_code=401)
        return JSONResponse(
            {
                "authenticated": True,
                "username": auth.username,
                "role": auth.role,
                "is_admin": auth.is_admin,
                "allowed_projects": auth.allowed_projects,
            }
        )

    # The transport app routes itself at settings.streamable_http_path
    # (default "/mcp"), so it is mounted at the root and must not be
    # re-prefixed; the guard inspects the path instead.
    #
    # FastMCP caches its session manager on the instance, and a manager can be
    # run() only once. build_app() runs again on every test app and on a real
    # restart, so drop the cached manager to get a fresh transport app.
    mcp._session_manager = None
    mcp_app = mcp.streamable_http_app()

    # Starlette runs the lifespan of the parent app only; a Mount-ed sub-app
    # never gets its own. Enter the MCP app's lifespan explicitly, otherwise
    # its session manager task group stays uninitialised and every request to
    # the /mcp endpoint fails with "Task group is not initialized".
    @asynccontextmanager
    async def lifespan(app):
        async with mcp_app.router.lifespan_context(mcp_app):
            yield

    routes = [
        Route("/", dashboard),
        Route("/api/status", api_status),
        Route("/api/task", api_task),
        Route("/api/plan", api_plan, methods=["GET"]),
        Route("/api/plan", api_plan_save, methods=["POST"]),
        Route("/api/plan", api_plan_clear, methods=["DELETE"]),
        Route("/api/login", api_login, methods=["POST"]),
        Route("/api/logout", api_logout, methods=["POST"]),
        Route("/api/me", api_me),
    ]
    if _STATIC_DIR.is_dir():
        routes.append(
            Mount("/static", app=StaticFiles(directory=str(_STATIC_DIR)), name="static")
        )
    routes.append(Mount("/", app=_guarded_mcp_app(mcp_app)))

    from starlette.middleware import Middleware
    from starlette.middleware.base import BaseHTTPMiddleware

    class _SecurityHeaders(BaseHTTPMiddleware):
        """Baseline response headers for a page served through the tunnel."""

        async def dispatch(self, request, call_next):
            response = await call_next(request)
            response.headers.setdefault("X-Content-Type-Options", "nosniff")
            response.headers.setdefault("Referrer-Policy", "same-origin")
            response.headers.setdefault("X-Frame-Options", "DENY")
            if _is_https(request):
                response.headers.setdefault(
                    "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
                )
            return response

    app = Starlette(
        routes=routes,
        lifespan=lifespan,
        middleware=[Middleware(_SecurityHeaders)],
    )
    return app


if __name__ == "__main__":
    import uvicorn

    app = build_app()
    uvicorn.run(app, host="127.0.0.1", port=8108, log_level="info")
