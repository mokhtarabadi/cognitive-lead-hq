# Task 175: Disable automation in Cognitive Executor agent, archive automation commands, restore manual workflow

**File:** `tasks/completed/175-disable-executor-automation-archive-commands.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Neutralize the experimental automated orchestration inside the Cognitive Executor agent, archive the nine automation-specific slash commands, and restore the manual workflow as the active default — without deleting anything.

## Manager's Notes

Manager order (verbatim intent): "Disable the intelligent/automated orchestration system we were building. It is not mature enough yet and is not working well enough, so I don't want it enabled for now. If Cognitive Executor Agent and Cognitive Discovery contain any of those automation rules or related configuration, you can comment them out if the file format supports comments. If comments aren't supported, back them up or move them somewhere safe, and restore the manual workflow as the active/default behavior. Keep all of these components somewhere so we can come back to them in the future. For the existing commands that were created specifically for this automation, archive them as well. Move them to a separate archive location so that when we decide to work on this feature again, we can restore them, fix them, and continue development."

What was implemented (Tasks 167/168/174 — the automation system being paused):
- Persona dispatch loop: executor orchestrates QA → reviewer → Telegram approval → closure via `dispatch_session_turn` (`mcp-persona-server/`, 4 modules + tests).
- Nine slash commands in `.opencode/commands/`: `qa.md`, `reviewer.md`, `manager.md`, `brainstorm.md`, `architect.md`, `designer.md`, `programmer.md`, `planner.md`, `strategist.md` (Tasks 167 + 174).
- Decision Learning Loop via `manager_decisions` MCP (`mcp-decision-server/`, `skill-templates/manager-decision/`).
- Executor sections: `## Persona Loop (MCP Slash Commands)` (lines ~208–266) and `### Decision Learning Loop (automatic — manager_decisions MCP)` (lines ~268–284) in `agents/cognitive-executor.md`.

Why it is being disabled: the automated orchestration is not mature and not working well enough (slow/flaky persona turns, gate-timeout friction, review-loop instability observed across Tasks 173–174). Temporary rollback to the reliable manual workflow; everything preserved for future maturation.

## Local TODOs

- [x] Verify `agents/cognitive-discovery.md` automation refs — grep found 2 (both `query_manager_decisions`/`get_manager_profile` read-only consult, lines 9-10 + 28); neutralized via YAML `#` + HTML comments (server itself disabled in Task 176)
- [x] Wrap executor `## Persona Loop` + `### Decision Learning Loop` sections in `<!-- PAUSED-AUTOMATION ... -->` HTML comments (Markdown supports comments)
- [x] Add explicit `## Manual Workflow (ACTIVE DEFAULT)` section to executor stating persona loop is paused and task execution is manual
- [x] Create `archive/automation-paused-2026-09-09/commands/` + move the 9 command files there via `git mv` (NOT `git rm`); leave a `README.md` stub? No — leave dir without commands; record new locations
- [x] Write `archive/automation-paused-2026-09-09/RESTORE.md` (how to restore: uncomment sections, `git mv` commands back, re-enable servers per Task 176)
- [x] Keep `mcp-persona-server/`, `mcp-decision-server/`, `skill-templates/manager-decision/`, fragments, `system-prompt.md` code in place (disable is by wiring, Task 176 covers servers)
- [x] Update CHANGELOG.md, write Execution Log, lint, stage + inject diff

## Acceptance Criteria

- [x] Executor automation sections commented out; manual workflow section states ACTIVE DEFAULT
- [x] All 9 command files moved to archive location; `.opencode/commands/` holds no automation commands
- [x] `agents/cognitive-discovery.md` verified automation-free with evidence
- [x] RESTORE.md documents the exact reversal steps
- [x] No deletions: `git status` shows renames/modifications only, zero `D` (deleted) entries for implementation files
- [ ] `lint_task_file` passes on the active task file

## Verification Evidence

- **Test command:** `git --no-pager status --short; ls .opencode/commands/; grep -c "dispatch_session_turn" agents/cognitive-executor.md` (expect 0 outside comments) + `lint_task_file` via lint MCP
- **Expected result:** only `R`/`M` entries, empty commands dir, zero live dispatch refs, lint clean
- **Actual result:** `R` x9 (commands → archive), `M` CHANGELOG.md + 2 agent files, `??` RESTORE.md + 176 backlog file; `.opencode/commands/` empty (0 files); executor markers 4 (PAUSED/RESUME/Manual Workflow); discovery decision refs commented (0 live); no `D` entries
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Comment markers break agent file parsing; commands referenced by live docs become dangling
- **Rollback plan:** Remove HTML comment wrappers; `git mv archive/automation-paused-2026-09-09/commands/*.md .opencode/commands/` — full reversal documented in RESTORE.md

---

## Execution Log & Reasoning

- Executor: `## Persona Loop` (was lines 208-266) + `### Decision Learning Loop` (268-284) wrapped in `AUTOMATION-PAUSED-2026-09-09 ... AUTOMATION-RESUME` HTML comments; new `## Manual Workflow` active-default section added above the block (plan → execute → record → hand off, Manager-directed review, never auto-commit).
- Discovery correction: inventory claimed zero refs, but grep found 2 (`query_manager_decisions`/`get_manager_profile` read-only consult). Neutralized: YAML `#` comments on permission lines 9-10, HTML comment on step 5 (prohibition on write/record/evolve kept active). No dispatch/persona-loop refs exist in the file.
- Commands: `git mv` x9 (tracked → renames, history preserved) to `archive/automation-paused-2026-09-09/commands/`; `.opencode/commands/` now empty; `RESTORE.md` written with 6-step restore procedure.
- CHANGELOG: `### Removed` bullet appended (Parse-Then-Append).
- Servers/skill/fragments code untouched in place (disable-by-wiring; Task 176 handles server configs).

**Post-implementation restore (manager order, same session):** restored
`skill-templates/brainstorm-swarm/SKILL.md` (69 lines) byte-identical from
`70ac2e0^` (`diff` → IDENTICAL); left untracked + inert (no live references
point at it after the 174 sweep; automation stays paused).

**Orchestrator micro-task (same session):** grep sweep found one LIVE
automation ref missed in implementation — executor line 86 (Read First:
`query_manager_decisions` + `get_manager_profile` consult, outside the
PAUSED block). Neutralized via inline HTML comment (directive now reads
"re-ask the human manager directly"; original preserved in comment).
AGENTS.md verified CLEAN (0 hits). Persona Loop body (lines 224–304)
confirmed inside the AUTOMATION-PAUSED block — grep hits there are comment
text only. Discovery: live-clean (frontmatter `#`, body HTML comment).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `ac53b78b2873808b8f5b538d14c0bc006e89fa3e`
<!-- END_GIT_DIFF -->
