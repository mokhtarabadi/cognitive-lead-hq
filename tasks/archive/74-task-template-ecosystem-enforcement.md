# Task 74: Task Template Ecosystem Enforcement

**File:** `tasks/backlog/74-task-template-ecosystem-enforcement.md`
**Source:** orchestrator
**Type:** improvement
**Status:** closed

## Source Context

### Variant A: Orchestrator (`**Source:** orchestrator`)

## Goal

Enforce the new task template sections (Acceptance Criteria, Verification Evidence, Risk & Rollback) across the entire ecosystem: update the linter to mandate them, instruct telegram-sync to populate them, instruct archive-tasks to extract them, and remind OpenCode to fill them during execution.

## Blueprint Reference

V8.0.0 Improvement Roadmap Phase 4 (Revised)

## Manager's Notes

Task 73 added Acceptance Criteria, Verification Evidence, and Risk & Rollback sections to the task-generator template. Now we need to enforce them across the entire ecosystem so they are never skipped.

## Local TODOs

- [x] Update linter (`mcp-lint-server/server.py`) to mandate the new sections in `_check_task_file_structure`
- [x] Update `telegram-issue-sync/SKILL.md` to populate Acceptance Criteria when generating task files from Telegram messages
- [x] Update `archive-tasks/SKILL.md` to extract and report criteria met in milestone summaries
- [x] Add CRITICAL RULE 6 (Evidence Capture) to `system-prompt.md` bash_phase to force verification evidence logging

---

## OpenCode Execution Log & Reasoning

### Architectural Changes

**1. Linter Enforcement (`mcp-lint-server/server.py`)**

Expanded the `required_sections` list in `_check_task_file_structure()` from 4 to 7 sections:

- **Before:** `## Goal`, `## Local TODOs`, `## OpenCode Execution Log & Reasoning`, `## Factual Git Diff`
- **After:** Added `## Acceptance Criteria`, `## Verification Evidence`, `## Risk & Rollback`

**Rationale:** The linter is the enforcement gate. Without it, the new template sections in `task-generator/SKILL.md` (added by Task 73) are merely advisory. By mandating them in the linter, any task file missing these sections will fail structural validation — catching omissions before they reach the Code Reviewer.

**2. Telegram Sync (`skill-templates/telegram-issue-sync/SKILL.md`)**

Added a mandatory field instruction after the `## Goal` instruction in Phase 3, Step 6:

```markdown
- `## Acceptance Criteria` — **MANDATORY.** Derive 2-3 concrete, verifiable conditions from the Telegram message's intent before writing the file.
```

**Rationale:** Telegram-sourced tasks bypass the Orchestrator's manual approval gate. Without explicit instruction to populate acceptance criteria, the LLM generating the task file would skip them — creating a structural lint failure downstream. This instruction forces the generating agent to derive concrete criteria from the raw message intent.

**3. Archive Tasks (`skill-templates/archive-tasks/SKILL.md`)**

Inserted a new `## Criteria Met` table in the milestone summary template, positioned between `## Files Modified` and `## Individual Task Summaries`:

```markdown
## Criteria Met

| Task | Acceptance Criteria | Status |
| ---- | ------------------- | ------ |
| XX   | [Extracted criteria from the completed task's `## Acceptance Criteria` section] | ✅ Met |
```

**Rationale:** This closes the feedback loop. Acceptance criteria are now not only defined (task-generator), validated (linter), and populated (telegram-sync), but also extracted and reported during milestone compaction. The Manager gets a concrete "what was delivered" report alongside the architectural summary.

**4. System Prompt (`system-prompt.md`)**

Added `CRITICAL RULE 6 (Evidence Capture)` to the `<bash_phase>` of `<opencode_implementation_task_template>`:

```markdown
CRITICAL RULE 6 (Evidence Capture): Before proceeding to the `<summary_phase>`, you MUST capture the exact test command, expected result, actual result, and exit code. You MUST write these into the `## Verification Evidence` section of the active task file.
```

**Rationale:** This enforces the Verification Evidence section at the agent execution level. Without this rule, OpenCode could complete implementation and skip to the summary phase without ever populating the evidence fields. The rule creates a mandatory checkpoint: evidence must be captured before the finalization sequence begins.

**5. Version Bump**

System version bumped from `7.4.1` to `7.4.2` (PATCH increment for ecosystem enforcement refinements).

### Verification

- `python3 -m py_compile mcp-lint-server/server.py` — ✅ Python syntax valid
- `grep -q "## Acceptance Criteria" mcp-lint-server/server.py` — ✅ Linter updated
- `grep -q "## Acceptance Criteria" skill-templates/telegram-issue-sync/SKILL.md` — ✅ Telegram sync updated
- `grep -q "## Criteria Met" skill-templates/archive-tasks/SKILL.md` — ✅ Archive updated
- `grep -q "CRITICAL RULE 6 (Evidence Capture)" system-prompt.md` — ✅ System prompt updated

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `1bb8fa0e6b988ca52f9afb77d59dc185ce750cce`
<!-- END_GIT_DIFF -->
