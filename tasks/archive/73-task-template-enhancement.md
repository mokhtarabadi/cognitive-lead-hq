# Task 73: Task Template Enhancement

**File:** `tasks/backlog/73-task-template-enhancement.md`
**Source:** orchestrator
**Type:** improvement
**Status:** closed

## Source Context

### Variant A: Orchestrator (`**Source:** orchestrator`)

## Goal

Enhance the task-generator template with Acceptance Criteria, Verification Evidence, and Risk & Rollback sections. Integrate the lint MCP server into the task closure workflow.

## Blueprint Reference

V8.0.0 Improvement Roadmap Phase 4

## Manager's Notes

This task enhances the task-generator skill template by adding structured sections for acceptance criteria, verification evidence, and risk/rollback planning. It also integrates the `lint_task_file` MCP tool into the `<summary_phase>` of both the `<opencode_implementation_task_template>` and `<opencode_combined_task_template>` in `system-prompt.md` to enforce structural validation before diff injection.

## Local TODOs

- [x] Enhance task-generator skill template (unified + multi-phase) with Acceptance Criteria, Verification Evidence, and Risk & Rollback sections
- [x] Integrate lint MCP tool into summary_phase of system-prompt.md task templates

---

## OpenCode Execution Log & Reasoning

### Architectural Changes

**1. Task Generator Template Enhancement (`skill-templates/task-generator/SKILL.md`)**

Added three new mandatory sections to both the unified canonical template and the multi-phase task template:

- **`## Acceptance Criteria`** — Forces explicit definition of "done" before execution begins. Prevents scope creep and ambiguity by requiring concrete, checkbox-verifiable criteria.
- **`## Verification Evidence`** — Mandates a specific test command, expected result, actual result, and exit code. This creates a machine-readable audit trail and ensures OpenCode cannot claim completion without running the verification command.
- **`## Risk & Rollback`** — Requires upfront risk assessment and rollback plan documentation. This prevents silent failures from becoming unrecoverable and gives the Code Reviewer a pre-written remediation path.

**Rationale:** These sections were placed after `## Local TODOs` (unified) and after `## Goal` (multi-phase) to maintain the logical flow: Goal → Criteria → Execution → Evidence → Risk.

**2. Lint Integration in `system-prompt.md`**

Modified the `<summary_phase>` of both `<opencode_implementation_task_template>` and `<opencode_combined_task_template>`:

- Added `lint_task_file` MCP tool call as the **first** step in the finalization sequence (before `custom_context_stage_and_inject_diff`).
- This enforces structural validation before any diff injection, catching template violations (missing sections, ID mismatches, broken markers) before they propagate to the Code Reviewer.
- Version bumped from `7.4.0` to `7.4.1` (PATCH bump for template/workflow enhancements per SemVer).

### Verification

- `grep -q "## Acceptance Criteria"` — ✅ passed
- `grep -q "## Verification Evidence"` — ✅ passed
- `grep -q "## Risk & Rollback"` — ✅ passed

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `8e71fae253fd795b94a4269f0164f8592c17e24b`
<!-- END_GIT_DIFF -->
