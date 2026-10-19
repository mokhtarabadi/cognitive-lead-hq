# Task 297: Remove goal-plugin wiring and enforce smart-compact usage

**File:** `tasks/completed/297-remove-goal-plugin-wiring-and-enforce-smart-compact-usage.md`
**Source:** manager
**Type:** chore
**Status:** closed
**Risk-Tier:** T1 standard

## Goal

Remove every live goal-plugin and Session Goals reference in cognitive-lead-hq since the goal plugin is no longer used. Learn the opencode-smart-compact plugin from its own repo, then strengthen the cognitive-executor guidance (and the Brain bridge only if truly needed) so the executor intelligently calls compaction and keeps a small clean context.

## Manager's Notes

Direct Manager order (translated from Persian): "Define a new task in the current open sprint and run it through planning, implementation, QA, code review, then report to me. Goal: look through the project and delete every reference to the goal plugin or goals wherever referenced. We no longer use the goal plugin. We have a plugin that compresses the session with features like magic-compact. First learn it by reading its repository, then mention it in the cognitive executor and, only if really needed, in the Brain, and force it so the cognitive executor intelligently always calls it to keep a clean small washed context. All of this lands in one task."

## Scope

In scope:
- Goal-plugin and Session Goals wiring: agents/cognitive-executor.md Goal Lifecycle section, prompts fragments mirroring it, README.md and LLM.txt Session Goals lines, .opencode/memory Session Goals lines, opencode.json goal entries if any, docs mentions
- Generic English word goal meaning objective (task Goal headings, alignment prose) stays untouched
- docs/history, tasks/archive, CHANGELOG history lines stay immutable
- opencode-smart-compact repo (../opencode-smart-compact): README, package.json, src hooks and tools (compact_context, read_omitted_content, slash commands)
- Strengthened executor compaction guidance with intelligent call triggers plus Brain mention only if proven needed
- system-prompt.md rebuilt from fragments, never hand-edited

Out of scope:
- External repos stay untouched, changes land only in cognitive-lead-hq
- No git add/commit/push by Hands (ZAC holds)

## Local TODOs

- [x] Inventory goal-plugin and Session Goals hits with grep evidence
- [x] Learn smart-compact repo (README, tools, triggers)
- [x] Remove goal-plugin wiring, keep generic goal prose
- [x] Strengthen executor compaction enforcement
- [x] Rebuild system-prompt and run verification gates

## Acceptance Criteria

- [x] AC1: targeted grep for goal-plugin, Session Goals, get_goal, create_goal, update_goal returns zero live hits outside history
- [x] AC2: generic task Goal prose still intact
- [x] AC3: executor documents smart-compact triggers and calls compact_context under pressure
- [x] AC4: system-prompt in sync with fragments, full suite passes with evidence

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pathspec pytest tests/ -q
- **Expected result:** pass exit 0
- **Actual result:** 541 passed, 22 warnings in 4.46s (exit 0) with OPENCODE_SESSION_ID unset; AC1 grep exit 1 zero hits; AC2 prose intact; json valid; index zero Session Goals
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** over-deletion removes generic goal prose or breaks goal-tool tests
- **Rollback plan:** worktree diff revert before staging, history reachable via git log --follow

---

## Execution Log & Reasoning

- Seat Check: domains are prompt contract plus docs and memory cleanup plus plugin guidance → Software Architect + Senior Programmer requested. Trigger sets all explicit miss, no user-visible surface. UI/UX Designer, QA, Reviewer, Planner, Strategist skipped at planning.
- Brainstorm: not required — single-domain reversible docs and config cleanup.
- Prompt-refactor applied: translated Persian direct order to technical English, expanded scope from targeted grep and compact repo read, structured as T1 chore with explicit keeps.
- Brain plan verdict 2026-10-06: Architect 2-seat consult APPROVED plan P0-P4. Keeps: generic goal prose untouched, history immutable, external repos untouched, ZAC. Selected path: inventory plus compact learn first, targeted goal-wiring deletes, executor trim enforcement, prompt and memory rebuild, verify plus stage. Awaiting Manager plan approval before implementation XML.
- Manager plan approval 2026-10-06: "Approved" via question tool. Routed back through Brain for Senior Programmer implementation XML. Executed XML verbatim.
- Execution: Step1 inventory found executor Goal Lifecycle 350-384, README 481, LLM 431, memory opencode_config 17-18; no prompts mirror, no opencode.json goal entries, no docs hits. Compact repo learned: compact_context tool with keepTurns and trim mode, read_omitted_content by Content ID, slash commands magic-compact, magic-trim, magic-stats. Step2 deleted Goal Lifecycle section plus three Session Goals sentences plus memory line. Step3 added trigger item 5 to executor Compaction section. Brain mention skipped: executor already holds direct compact_context access (AGENTS.md equivalent guidance in place). Step4 system-prompt rebuild verified in sync with zero fragment edits needed. Memory index rebuilt to 21 entries with zero Session Goals namespaces and no index content change required.
- Autopilot locked 2026-10-06 per Manager order for end-to-end completion of this task.
- Brain QA verdict autopilot round: QA_PASSED with zero live goal wiring and intact setup flow.
- Code Reviewer verdict autopilot round: APPROVED to PO_REVIEW_PENDING with no functional defects. R2 confirmations recorded in Verification Evidence. Awaiting Manager explicit closure words.
- Closed: 2026-10-06 Approved for closure by Manager.
- Assumption A1: OpenChamber built-in Session Goals references count as goal-plugin wiring per Manager order and were removed. Reason: Manager ordered every goal reference deleted except generic prose.
- Assumption A2: goal lifecycle tool calls (get_goal, create_goal, update_goal) have no live callers left after section delete. Reason: targeted grep returns zero hits outside history.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `83742b726f930e4dd35af0b5519f1b76974274af`
<!-- END_GIT_DIFF -->
