# Task 164: owt Worktree Plugin Integration (Project + Global)

**File:** `tasks/completed/164-opencode-worktree-integration.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Integrate `@nano-step/opencode-worktree-plugin` (owt) into project workflow + global installation, following the DCP/goal-plugin pattern (Task 163/126) as closely as its distribution allows.

## Manager's Notes

- User request verbatim: "create a task, collect info about https://github.com/kdcokenny/opencode-worktree add this to project adn global installtion, like last plugin we addedd"
- Manager decision (D1): kdcokenny variant is OCX-only and OCX is NOT allowed → use `@nano-step/opencode-worktree-plugin` (owt, npm 2.0.0, 0 deps, plugin + CLI + slash commands) instead.
- Manager directive: "i like it implemment it globlally and add to our project like other plugings we have like goal plugin, create a goal and follow it until end"
- Deviation from literal DCP pattern (gatekeeper-grounded): owt is NOT added to `opencode.json`/`tui.json` `plugin` arrays — (a) its npm spec resolves per-project from `node_modules` which this docs-only repo does not have (unresolvable spec hard-fails opencode startup), (b) it is not a TUI panel plugin so `tui.json` does not apply, (c) its supported global path (`owt-setup install` → `~/.config/opencode/command/` + `~/.config/opencode/plugins/`) already covers every project session including this repo. Project side = `.gitignore` guards + `LLM.txt` § docs + `CHANGELOG.md`.
- Optional `owt hook --global` (co-author strip, sets global `core.hooksPath`) SKIPPED — unanswered Q2, documented as optional in LLM.txt.
- Alternatives evaluated: `@tmegit/opencode-worktree-session` (auto-push too aggressive), `HeberYesid/opencode-worktree` (0★ unproven), `arturosdg/opencode-worktree` (standalone TUI, not a plugin).

## Local TODOs

- [x] Collect upstream repo data (README, install spec, commands, config, license)
- [x] Discover current DCP/goal-plugin pattern in opencode.json, tui.json, LLM.txt §7
- [ ] Global install: `npm install -g @nano-step/opencode-worktree-plugin` + `owt-setup install` + verify
- [ ] Project integration: `.gitignore` worktree guards + LLM.txt § docs + CHANGELOG.md
- [ ] Verify: `owt help`, global dirs, `pytest tests/ -q` exit 0
- [ ] Lint, stage, QA transition

## Acceptance Criteria

- [x] Upstream repo data collected (install spec, purpose, commands, license)
- [x] Global installation verified (`npm i -g` exit 0, `owt help` works, `~/.config/opencode/plugins/` + `command/` populated)
- [x] Project `.gitignore` guards worktree state (`.opencode/worktrees/`, `worktree-sessions.json`)
- [x] LLM.txt § updated with owt install/commands/verification notes
- [x] CHANGELOG.md entry added
- [x] `pytest tests/ -q` exit 0 (no repo test impact)
- [x] `lint_task_file` passes on active task file

## Verification Evidence

- **Test command:** `uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q`
- **Expected result:** all tests pass, exit 0
- **Actual result:** 55 passed, 8 warnings in 4.07s; `owt help` prints v4 usage; `~/.config/opencode/plugins/worktree-plugin.js` + 7 command files present; `opencode.json`/`tui.json` JSON valid; `git status` clean except task file
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** `owt-setup install` writes into `~/.config/opencode/` (global, outside repo — no repo drift); worktrees created later live in `<repo>/.opencode/worktrees/` (gitignore-guarded).
- **Rollback plan:** `npm rm -g @nano-step/opencode-worktree-plugin`, remove `~/.config/opencode/plugins/worktree-plugin.js` + `~/.config/opencode/command/{init-worktree,list-worktrees,open-worktree}.md`, revert repo `.gitignore`/LLM.txt/CHANGELOG from git diff.

---

## Execution Log & Reasoning

- Chose `@nano-step/opencode-worktree-plugin` (owt) over kdcokenny (OCX-only, OCX forbidden), felixAnhalt (auto-push too aggressive), HeberYesid (0★ unproven), arturosdg (standalone TUI, not a plugin).
- Gatekeeper deviation: did NOT add to `opencode.json`/`tui.json` plugin arrays — npm spec resolves per-project from `node_modules` (absent in docs-only repo → hard-fail startup risk); owt is not a TUI panel plugin; global file-based install already covers all sessions. Documented in Manager's Notes.
- Global: `npm i -g @nano-step/opencode-worktree-plugin` (exit 0) + `owt-setup install` (plugin + 7 commands, v4) + `owt help` verified. Skipped optional `owt hook --global`.
- Project: `.gitignore` (+2 guards), `LLM.txt` new §7.8 + checklist bullet, `CHANGELOG.md` Unreleased entry.
- Verification: `pytest tests/ -q` → 55 passed exit 0; JSON valid; git status clean except task file.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `e39f08cc26d3c7476d7a106904dcb78ee6d7b11b`
<!-- END_GIT_DIFF -->
