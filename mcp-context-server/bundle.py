# Sibling Docs: README.md | Decisions: DECISIONS.md


"""Meta-task content builder (tool itself stays in server.py). Stdlib-pure: no MCP imports, no registration, no import back to server."""

import re
import time
from pathlib import Path

from gitops import (
    ACTIVE_KANBAN_DIRS,
    DIFF_SIZE_WARNING_THRESHOLD,
    MAX_BUNDLE_SIZE,
    _detect_stack,
    _extract_checklist_with_continuations,
    _extract_section,
    _extract_title,
    _format_task_id_list,
    _verify_verbatim_checksums,
)


def _build_meta_content(
    meta_id: int,
    meta_slug: str,
    meta_title: str,
    source_ids: list[str],
    source_data: list[tuple[str, Path, str, str]],
) -> str:
    meta_id_str = f"{meta_id:02d}" if meta_id < 100 else str(meta_id)
    if meta_id >= 100:
        meta_id_str = str(meta_id)
    file_header = f"tasks/backlog/{meta_id_str}-{meta_slug}.md"
    title_line = f"# Task {meta_id}: {meta_title}"
    timestamp = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    bundled_checklist_items: list[str] = []
    local_todos_aggregated: list[str] = []
    total_loc = 0
    per_source_blocks: list[str] = []
    for sid, path, content, stitle in source_data:
        goal = _extract_section(content, "Goal") or "_(No Goal section found)_"
        ac = (
            _extract_section(content, "Acceptance Criteria")
            or "_(No Acceptance Criteria)_"
        )
        todos = _extract_section(content, "Local TODOs") or "_(No Local TODOs)_"
        risk = _extract_section(content, "Risk & Rollback")
        manager_notes = _extract_section(content, "Manager's Notes")
        source_context = ""
        if "## Blueprint Reference" in content:
            br = _extract_section(content, "Blueprint Reference")
            if br:
                source_context += f"\n**Blueprint Reference (verbatim):**\n{br}\n"
        total_loc += len(content.splitlines())
        # B1: multi-line checklist extraction
        ac_lines = _extract_checklist_with_continuations(ac)
        if not ac_lines:
            ac_lines = [
                f"- [ ] {line.strip()}"
                for line in ac.splitlines()
                if line.strip() and not line.strip().startswith("#")
            ][:3]
        for line in ac_lines:
            if line.startswith("- ["):
                m = re.match(r"^- \[[ xX]\]\s*(.*)", line)
                inner = m.group(1) if m else line
                bundled_checklist_items.append(f"- [ ] [{sid}] {inner}")
            else:
                bundled_checklist_items.append(line)
        # B1: multi-line TODO extraction
        todo_lines = _extract_checklist_with_continuations(todos)
        for line in todo_lines:
            if line.startswith("- ["):
                m = re.match(r"^- \[[ xX]\]\s*(.*)", line)
                inner = m.group(1) if m else line
                local_todos_aggregated.append(f"- [ ] [{sid}] {inner}")
            else:
                local_todos_aggregated.append(line)
        block = f"### Source Task {sid}: {stitle}\n\n"
        block += f"**Original File:** `{path}` → `tasks/archive/{path.name}` (after bundling)\n\n"
        block += f"**Title:** {stitle}\n\n"
        block += "#### Goal (verbatim)\n\n"
        block += f"{goal}\n\n"
        if manager_notes:
            block += "#### Manager's Notes (verbatim)\n\n"
            block += f"{manager_notes}\n\n"
        if source_context:
            block += source_context + "\n"
        block += "#### Acceptance Criteria (verbatim)\n\n"
        block += f"{ac}\n\n"
        block += "#### Local TODOs (verbatim)\n\n"
        block += f"{todos}\n\n"
        if risk:
            block += "#### Risk & Rollback (verbatim)\n\n"
            block += f"{risk}\n\n"
        block += "---\n\n"
        per_source_blocks.append(block)
    seen_todos: set[str] = set()
    deduped_todos: list[str] = []
    for t in local_todos_aggregated:
        if t not in seen_todos:
            seen_todos.add(t)
            deduped_todos.append(t)
    meta_local_todos = (
        f"- [ ] Step 1: Validate META bundle — confirm all {len(source_data)} source requirements are captured verbatim below\n"
        f"- [ ] Step 2: Implement unified changes covering all bundled tasks (single diff, single branch)\n"
    )
    for t in deduped_todos:
        meta_local_todos += f"{t}\n"
    meta_local_todos += f"- [ ] Step {len(deduped_todos) + 3}: Verify all bundled checklist items and run lint_task_file + verification-before-completion\n"
    meta_local_todos += f"- [ ] Step {len(deduped_todos) + 4}: Update CHANGELOG.md and record Verification Evidence\n"
    meta_ac = (
        "\n".join(bundled_checklist_items)
        if bundled_checklist_items
        else "- [ ] _(No aggregated criteria — check per-source blocks)_"
    )
    meta_ac += f"\n- [ ] Traceability: All {len(source_data)} source tasks are archived with superseded-by marker and reachable via `git log --follow`"
    meta_verification = (
        f"- **Test command:** `lint_task_file` on META file; `git log --oneline --follow -- tasks/archive/<id>-*.md | head` for archived sources; project test suite if logic changed\n"
        f"- **Expected result:** META lint passes; all {len(source_data)} sources in `tasks/archive/` with `superseded` status; single Factual Git Diff covers all bundled changes\n"
        f"- **Actual result:** _(Hands fill during execution)_\n"
        f"- **Exit code:** _(Hands fill)_\n"
    )
    meta_risk = (
        "- **Risk:** Checklist omission — mitigated by verbatim copy + SHA-length comparison of source AC vs bundled checklist; script fails if mismatch >0.\n"
        "- **Risk:** Mega-diff >400 LOC unreviewable — warning emitted; Manager should split if >400.\n"
        "- **Risk:** Accidental purge — mitigation: only `git mv` to archive, never `git rm`; purge blocked until META reaches `tasks/completed/`.\n"
        f"- **Rollback plan:** `git mv tasks/archive/<id>-*.md tasks/backlog/<id>-*.md` for each superseded {_format_task_id_list(source_ids)}, remove Superseded-By footer, delete or archive `tasks/backlog/{meta_id_str}-{meta_slug}.md` as abandoned. No HQ code beyond bundler is affected.\n"
    )
    warning_note = ""
    if total_loc > DIFF_SIZE_WARNING_THRESHOLD:
        warning_note = (
            f"> ⚠️ **Guardrail Warning:** Combined source size is {total_loc} LOC (> {DIFF_SIZE_WARNING_THRESHOLD}). "
            f"Unified META diff may be large and hard to review. Consider splitting into two METAs.\n\n"
        )
    content = (
        f"{title_line}\n\n"
        f"**File:** `{file_header}`\n"
        f"**Source:** manager\n"
        f"**Type:** feature\n"
        f"**Status:** open\n"
        f"**Supersedes:** {_format_task_id_list(source_ids)}\n"
        f"**Meta:** true\n"
        f"**Created:** {timestamp}\n"
        f"**Bundled:** {len(source_data)} tasks\n\n"
        f"## Goal\n\n"
        f'Unified execution of {len(source_data)} related small tasks as a single META task to eliminate sequential overhead. This META bundles tasks {_format_task_id_list(source_ids)} — "{meta_title}" — into one branch, one diff, and one QA gate (all-or-nothing). Every requirement below is preserved **verbatim** from its source task; no summarization or omission is allowed.\n\n'
        f"{warning_note}**Source IDs:** {_format_task_id_list(source_ids)}\n"
        f'**Next ID:** {meta_id} (discovered via `find tasks -name "*.md" | sort -n | tail -1 +1`)\n'
        f"**Archive Policy:** Source files will be moved to `tasks/archive/` with `superseded-by: {meta_id}-{meta_slug}` and remain reachable via `git log --follow` (never purged until META is completed).\n\n"
        f"## Manager's Notes\n\n"
        f"**Bundle Decision (2026-08-21):** Manager requested fully automatic bundling with archive (not purge). This META was generated deterministically by the `bundle_tasks` MCP tool to execute {len(source_data)} small related tasks together and speed up turnaround.\n\n"
        f"**Traceability:**\n"
        f"- Supersedes {_format_task_id_list(source_ids)} — see per-source verbatim blocks below\n"
        f"- Archive: each source moved via `git mv` to `tasks/archive/` with `**Superseded-By:** {meta_id_str}-{meta_slug}` header + superseded footer\n"
        f"- Rollback: `git mv tasks/archive/<id>-*.md tasks/backlog/` + delete META file\n\n"
        f"**Guardrails Applied:**\n"
        f"- Cap 6 per bundle — this bundle has {len(source_data)} ({'✅ within cap' if len(source_data) <= MAX_BUNDLE_SIZE else '❌ exceeds cap — requires --force'})\n"
        f"- Verbatim preservation — every source Goal/AC/TODO/Risk copied verbatim below (SHA comparison available in bundler dry-run)\n"
        f"- Diff-size check — combined {total_loc} LOC ({'⚠️ exceeds 400 — consider split' if total_loc > DIFF_SIZE_WARNING_THRESHOLD else '✅ within 400'})\n\n"
        f"## Source Bundles (Verbatim Preservation)\n\n"
        f"The following blocks are **verbatim copies** of each source task's critical sections. They are the source of truth; the checklist that follows is derived from them. Do not edit them manually — they were extracted by the bundler to guarantee zero omission.\n\n"
        f"{''.join(per_source_blocks)}\n"
        f"## Bundled Checklist (All-or-Nothing)\n\n"
        f"> **QA Gate (all-or-nothing):** Every line below maps to one source acceptance criterion. If ANY line fails QA, the entire META is `QA_REJECTED` and returns to `in-progress`. Do not partially close.\n\n"
        f"{meta_ac}\n\n"
        f"## Local TODOs\n\n"
        f"{meta_local_todos.strip()}\n\n"
        f"## Acceptance Criteria\n\n"
        f"{meta_ac}\n\n"
        f"## Verification Evidence\n\n"
        f"{meta_verification.strip()}\n\n"
        f"## Definition of Done\n\n"
        f"The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):\n\n"
        f"- [ ] Build/Test/Lint pass with exit code 0\n"
        f"- [ ] `lint_task_file` passes on the active task file\n"
        f"- [ ] `CHANGELOG.md` updated via Parse-Then-Append\n"
        f"- [ ] `verification-before-completion` applied and evidence recorded\n\n"
        f"## Risk & Rollback\n\n"
        f"{meta_risk.strip()}\n\n"
        f"---\n\n"
        f"## Execution Log & Reasoning\n\n"
        f"_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_\n\n"
        f"## Factual Git Diff\n\n"
        f"<!-- BEGIN_GIT_DIFF -->\n\n"
        f"_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_\n\n"
        f"<!-- END_GIT_DIFF -->\n"
    )
    return content
