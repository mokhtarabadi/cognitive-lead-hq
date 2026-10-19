# Task 323: Project-local skills visible in AGENTS.md

**File:** `tasks/completed/323-project-skills-registry.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Project:** /home/mohammad/Develop/Projects/cognitive-lead-hq
**Priority:** High

## Goal

Project-local skills (e.g. `.opencode/skills/sop-maintenance`) visible in `AGENTS.md` via an audited Project Skills table, so the executor loads them with the same confidence as global skills.

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

## Local TODOs

- [x] Grounding reads (template, AGENTS, sop-maintenance, tests)
- [x] Template scan-and-table condition with two hard fails
- [x] Backfill root AGENTS.md verbatim
- [x] Sync test update (table presence, row-count match, stale-row fail)
- [x] Verify with RTK plus lint plus grep

## Acceptance Criteria

- [x] Audit without the table fails (rule enforced, not advisory).
- [x] Executor loads project-local skills with the same confidence as global ones.
- [x] Stale rows (deleted skill still listed) fail the audit.

## Definition of Done

- [x] Tests pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append

## Risk & Rollback

- **Risk:** Brittle row-count test if local skill dirs change without AGENTS.md update (mitigated: test fails loudly by design).
- **Rollback plan:** Revert the three files via `git checkout --`.

## Execution Log & Reasoning

- Created 2026-10-17 from live miss (sop-maintenance never loaded). Owner implements.
- Seat Check: audit/template domains, no trigger words fired (explicit miss all seats), Architect minimum, single-seat plan, brainstorm not required. Brain plan approved by Manager ("Approved").
- Implemented 5 steps: read sop-maintenance SKILL.md (name plus description verbatim) plus registry test shape; template condition added in both criteria lists with two hard fails; AGENTS.md backfilled with Project Skills table (one verbatim row); sync test gained three tests (table presence, row-count match, stale-row fail) plus template-requirement test — one regex fix (blank line before table), 33 passed; no executor change per plan.
- D1: condition duplicated in both criteria lists (both enumerate required AGENTS.md contents).
- Stack-skill skip record: root=. markers=[package.json, go.mod, build.gradle.kts, pyproject.toml, vite.config] matched=[] reason="docs-only template plus registry change".

- QA: QA_PASSED (33 passed, all acceptances traced). Review: technical APPROVED, PO_REVIEW_PENDING. Awaiting Manager accept word for closure.
- Closure: Manager accept quote "Approved for closure" recorded; closure executing exactly once.

## Verification Evidence

- `rtk test /home/mohammad/v2ray-to-subs/.venv/bin/pytest tests/test_skill_registry.py tests/test_prompt_sync.py -q` — expected all pass, actual 33 passed (after one regex fix), exit 0. (Repo has no local pytest; foreign venv binary used as runner only.)
- `grep -n "Project Skills" AGENTS.md skill-templates/audit-agents/SKILL.md tests/test_skill_registry.py` — hits in all three.
- `grep -n "sop-maintenance" AGENTS.md` — one row hit, wording matches source SKILL.md verbatim.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `e909e006a2a1a8e19f81de472c87e2a055205b3e`
<!-- END_GIT_DIFF -->
