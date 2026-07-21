# Task: Add CRITICAL RULE 4 (File Staging) to bash_phase

**File:** `tasks/backlog/59-add-critial-rule-4-file-staging.md`
**Type:** improvement
**Status:** closed

## Goal

Add CRITICAL RULE 4 to the `<bash_phase>` of the `<opencode_implementation_task_template>` in `system-prompt.md`, forcing the Orchestrator to explicitly include a `git mv` command when the active task is in `tasks/backlog/`. This prevents the Zero-Autonomous-Commit rule from blocking task file promotion.

## Manager's Notes

- Problem: When the Orchestrator forgot to write `git mv tasks/backlog/XX.md tasks/in-progress/XX.md` in the bash block, OpenCode's ZAC rule prevented it from moving the file autonomously.
- Fix: Added CRITICAL RULE 4 instructing the Orchestrator to always include this command as the first bash command when the task is in backlog.
- Bump `<system_version>` from `6.7.1` to `6.8.0`.
- Update `CHANGELOG.md` with `[6.8.0]` entry.

## Local TODOs

- [x] Add CRITICAL RULE 4 to `<bash_phase>` in `system-prompt.md`
- [x] Bump version from 6.7.1 to 6.8.0
- [x] Update `CHANGELOG.md`
- [x] Run prettier to format modified files

## OpenCode Execution Log & Reasoning

### Architecture & Reasoning

**Root Cause:** The `<bash_phase>` in `<opencode_implementation_task_template>` had CRITICAL RULE 2 (Zero-Autonomous-Commit) which strictly forbids OpenCode from running `git mv` autonomously — but nothing forced the Orchestrator to explicitly include the command. The Senior Programmer persona could forget to write the `git mv` line, causing task files to remain stuck in `tasks/backlog/`.

**Fix:** Added CRITICAL RULE 4 that explicitly instructs the Orchestrator (the AI Studio persona generating the task block) to include `git mv tasks/backlog/XX-task.md tasks/in-progress/XX-task.md` as the first command in the bash phase whenever the task resides in backlog. This closes the gap between "OpenCode must not guess git commands" and "the Orchestrator must not forget to specify them."

**Files modified:**
1. `system-prompt.md` — Added CRITICAL RULE 4 after CRITICAL RULE 3; bumped version to 6.8.0
2. `CHANGELOG.md` — Added 6.8.0 entry

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `cdf1401275e789480e42b97391e894d5ab5ca575`
<!-- END_GIT_DIFF -->
