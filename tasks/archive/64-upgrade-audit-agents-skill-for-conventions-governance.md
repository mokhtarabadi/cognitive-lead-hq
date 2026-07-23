# Task: Upgrade audit-agents Skill for conventions.md Governance

**File:** `tasks/completed/64-upgrade-audit-agents-skill-for-conventions-governance.md`
**Type:** improvement
**Status:** closed

## Goal

Upgrade `skill-templates/audit-agents/SKILL.md` to auto-generate and audit `docs/conventions.md` with Universal DateTime Standard and SOLID Programming Guidelines.

## Manager's Notes

- Add `docs/conventions.md` validation to Target Audit Criteria checklist.
- Update Mode 1 (Phase 0 Generation) template to include a complete `docs/conventions.md` with DateTime and SOLID sections.
- Update Mode 2 (Audit Mode) to also audit `docs/conventions.md` and patch if missing.
- Update Agent Audit Summary output to include `conventions.md` compliance status.

## Local TODOs

- [x] **Step 1:** Create `tasks/backlog/64-upgrade-audit-agents-skill-for-conventions-governance.md` with goal, notes, local TODOs, execution log placeholder, and git diff markers.
- [x] **Step 2:** Refactor `skill-templates/audit-agents/SKILL.md` — add conventions.md to criteria, templates, audit mode, and summary.
- [x] **Step 3:** Update `CHANGELOG.md` under `[Unreleased]`.
- [x] **Step 4:** Move task to `tasks/in-progress/`, write execution log, stage and inject diff.

## OpenCode Execution Log & Reasoning

### Architectural Reasoning

The `audit-agents` skill is the central enforcement mechanism for project conventions. Now that `docs/conventions.md` contains the Universal DateTime Standard and SOLID Programming Guidelines (added in task 63), the `audit-agents` skill must be upgraded to generate, audit, and patch this file automatically.

Key changes:
1. **Target Audit Criteria** — Added `docs/conventions.md` path requirement and conventions content compliance checklist (DateTime rules + SOLID guidelines) to both Mode 1 and Mode 2 criteria blocks.
2. **Mode 1 (Phase 0 Generation)** — Added a complete `docs/conventions.md` template as the 3rd core document template. The workflow now generates both `AGENTS.md` and `docs/conventions.md` on new project onboarding.
3. **Mode 2 (Audit Mode)** — Extended to check `docs/conventions.md` alongside `AGENTS.md`. The Resolution Protocol now patches conventions.md if missing or incomplete using the template.
4. **Agent Audit Summary** — Expanded with dedicated `conventions.md Status` and `conventions.md Actions` fields.

### Files Modified

- `skill-templates/audit-agents/SKILL.md` — Added conventions.md criteria, template, audit logic, and summary
- `CHANGELOG.md` — Added [Unreleased] entry

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `aec83323c9b092e72fc1ee125476e6f60adfb26a`
<!-- END_GIT_DIFF -->
