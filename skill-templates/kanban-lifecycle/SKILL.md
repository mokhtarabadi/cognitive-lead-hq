---
name: kanban-lifecycle
description: Unified Kanban lifecycle — task generation, lint validation, META bundling, completion archiving, and flat-to-V6 migration in one meta skill.
---

# Kanban Lifecycle Meta Skill (slim index)

Meta skill combining **task-generator** + **task-lint** + **bundle-tasks** + **archive-tasks** + **migrate-kanban**. Full bodies are verbatim in `templates/` — read only the part you need.

---

## Critical Rules (no read needed)

- **ZAC:** Staging via `custom_context_stage_and_inject_diff` only; closure on exact “Approved for closure” / “Close task”.
- **Task template:** unified canonical with `## Goal`, `## Local TODOs`, `## Acceptance Criteria`, `## Verification Evidence` (rtk test), `## Definition of Done`, `## Risk & Rollback`, `<!-- BEGIN_GIT_DIFF -->` markers. `**Source:**`/`**Type:**` required; `Meta: true` + `Supersedes` for METAs.
- **IDs:** `NEXT_ID` via `find tasks/ -type f -name "*.md" | grep -Eo '^[0-9]+' | sort -n | tail -1 +1` across ALL lanes (archive reuses consumed IDs → active duplicates fail). Collision check (`ls tasks/backlog/${NEXT_ID}-*.md`) is a hard stop.
- **Bundle:** cap 6, LOC >400 warn, verbatim preservation, `git mv` to `tasks/archive/` only — never purge until META is `completed`.
- **Archive:** `tasks/completed/` → dense `docs/history/milestone-X-summary.md`; stale-memory audit (flag only, never delete without Manager approval).
- **QA:** all-or-nothing funnel; any failed bundled item rejects the META.

## When to Read Templates

- **Create/edit a task file** → `templates/01-generate.md` (Workflow + Bundle Workflow).
- **Validate a task file** → `templates/02-lint.md`.
- **Bundle 2–6 tasks into META** → `templates/03-bundle.md`.
- **Archive a milestone** → `templates/04-archive.md`.
- **Migrate flat `tasks/` → V6 lanes** → `templates/05-migrate.md`.

Templates are authoritative; this index only summarizes. Registry: `prompts/fragments/07-agent_skills_registry.md`.
