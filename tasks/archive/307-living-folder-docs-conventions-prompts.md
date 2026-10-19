# Task 307: Living Folder Docs — Conventions & Prompt System

**File:** `tasks/completed/307-living-folder-docs-conventions-prompts.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Implement Phase 1 of the Living Folder Docs system: add the standard to docs/conventions.md, update prompt fragments (13-constraints.md, 09-hands_protocols.md, 01-system_version.md to 9.54.0), rebuild system-prompt.md, mirror rules in agents/cognitive-executor.md, and update CHANGELOG.md.

## Manager's Notes

Phase 1 implementation from the approved Living Folder Docs roadmap (Task 306). Establishes conventions and prompt-level agent contracts before MCP tool changes in Phase 2.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Add Living Folder Docs standard to docs/conventions.md
- [x] Add mandate to prompts/fragments/13-constraints.md
- [x] Update hands protocols template in prompts/fragments/09-hands_protocols.md
- [x] Bump version to 9.54.0 in prompts/fragments/01-system_version.md and assemble system-prompt.md
- [x] Mirror rules in agents/cognitive-executor.md
- [x] Verify system-prompt.md sync and task file lint
- [x] Update skill-templates/audit-agents/SKILL.md with Living Docs criteria
- [x] Create skill-templates/init-folder-docs/SKILL.md and register in 07-agent_skills_registry.md

## Acceptance Criteria

- [x] AC1: docs/conventions.md defines the complete Living Folder Docs specification (file shapes, ADR schema, code pointer formats)
- [x] AC2: prompts/fragments/13-constraints.md and 09-hands_protocols.md mandate sibling doc reading and updates during execution
- [x] AC3: system_version incremented to 9.54.0, system-prompt.md assembled, and lint_system_prompt_sync passes cleanly
- [x] AC4: agents/cognitive-executor.md mirrors the Living Docs requirements
- [x] AC5: CHANGELOG.md records the v9.54.0 Living Docs update
- [x] AC6: skill-templates/audit-agents/SKILL.md audits Living Folder Docs conventions
- [x] AC7: skill-templates/init-folder-docs/SKILL.md created and registered in 07-agent_skills_registry.md

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-lint-server python /tmp/opencode/verify_307.py (runs `lint_system_prompt_sync()` plus `lint_task_file('tasks/in-progress/307-living-folder-docs-conventions-prompts.md')`; passes only when both report in-sync/pass)
- **Expected result:** lint_system_prompt_sync reports in sync, lint_task_file passes, exit code 0
- **Actual result:** `lint_system_prompt_sync` reports "in sync with prompts/"; `lint_task_file` reports "passed Task File linting" on the in-progress path — confirmed on the initial run and re-confirmed after the hotfix round (registry + skills changes)
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Prompt assembler drift or malformed fragment breaks prompt assembly
- **Rollback plan:** git checkout modified files to restore v9.53.0 state

---

## Execution Log & Reasoning

Phase 1 executed per the Orchestrator blueprint. Seat check: single-domain SOP/prompt change, no UI surface and no data contract change, so Designer and data-layer seats skipped with reason. Brainstorm: not required — approved plan execution, fully reversible via git checkout.

Steps performed: created the task file directly in `tasks/in-progress/` per instruction (no backlog move needed); appended the Living Folder Docs Standard to `docs/conventions.md`; added the mandate bullet before `<defensive_shell_protocol>` in `13-constraints.md`; added rule 5 (sync) to CRITICAL TOOL RULES and item 4 (sibling docs update) to the documentation phase in the implementation template of `09-hands_protocols.md`; bumped `01-system_version.md` to 9.54.0; added Core Protocol item 7 and the Boundaries bullet in `agents/cognitive-executor.md`; rebuilt `system-prompt.md` via the assembler (99489 bytes, version line confirmed, mandate content present); updated CHANGELOG `[Unreleased]` → `### Added` via Parse-Then-Append. Deviation D1 (logged, minimal): also bumped the `test_prompt_sync.py` version pin 9.53.0 → 9.54.0 — required to keep the suite green, matching prior version-bump precedent; the file is added to the staged `modified_files` so the QA diff is complete. Validation: no Orchestrator rule violations (assembler path used for the generated artifact, no git add/commit/push, task numbers only in filename/title/CHANGELOG). Absent files skipped per policy: DESIGN.md, docs/architecture.md, docs/data_model.md.

Hotfix round (Hands, 2026-10-06): moved the task back qa → in-progress via `git mv` (tracked file, exit 0) and re-synced the `**File:**` header. Added Living Folder Docs coverage to `skill-templates/audit-agents/SKILL.md` in five places: Mode 1 conventions-compliance bullet, new Sibling Inspection criterion, conventions template appendix, AGENTS.md template guardrails, and the Mode 2 audit criterion. Gatekeeper scope check: the additions reference only generic colocated docs (no HQ-only fragment paths, no task numbers in prose), so the skill stays project-agnostic and the earlier scope-leak fix holds. Created `skill-templates/init-folder-docs/SKILL.md` (slice discovery, scaffolding, pointer injection, verification summary) and registered it after `task-lint` in `07-agent_skills_registry.md`. Re-assembled `system-prompt.md` (99674 bytes, still 9.54.0, registry line present). CHANGELOG Task 307 entry extended per instruction. AC6–AC7 genuinely satisfied and checked; prior AC1–AC5 and DoD boxes remain valid.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `e2cf88080dcdcc9cf0f46b336d7de44136ae27a2`
<!-- END_GIT_DIFF -->
