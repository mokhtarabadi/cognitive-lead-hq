# Task 323 — Project-local skills must be visible in AGENTS.md

**File:** tasks/backlog/323-project-skills-registry.md
**Status:** backlog
**Project:** /home/mohammad/Develop/Projects/cognitive-lead-hq
**Priority:** High

## Problem (observed live 2026-10-17)

Project-local skills (e.g. `.opencode/skills/sop-maintenance` in this repo)
are invisible: the executor's Skill Auto-Loading Matrix only lists global
stack skills, so local skills are never loaded unless the Manager names them.
The agent cannot follow a skill it cannot see.

## Rule (owner-approved 2026-10-17)

The `audit-agents` skill template gains a mandatory condition: on every audit
it scans the project's local skill directories (`.opencode/skills/*/SKILL.md`
or equivalent) and (re)builds a **Project Skills table** inside that project's
`AGENTS.md` — one row per local skill: name, trigger (when to load), one-line
duty. Same shape as the global matrix so the executor treats both uniformly.

## Deliverable

- `audit-agents` template updated with the scan-and-table condition.
- This repo's `AGENTS.md` backfilled (proves the rule on itself).
- Sync test update.

## Acceptance

- [ ] Audit without the table fails (rule enforced, not advisory).
- [ ] Executor loads project-local skills with the same confidence as global ones.
- [ ] Stale rows (deleted skill still listed) fail the audit.

## Execution Log

- Created 2026-10-17 from live miss (sop-maintenance never loaded). Owner implements.
