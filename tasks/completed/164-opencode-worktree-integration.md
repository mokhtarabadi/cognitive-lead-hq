# Task 164: owt Worktree Plugin Integration (Project + Global)

**File:** `tasks/qa/164-opencode-worktree-integration.md`
**Source:** manager
**Type:** feature
**Status:** open

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
```diff
diff --git a/.gitignore b/.gitignore
index 929ad0c..af0c0a1 100644
--- a/.gitignore
+++ b/.gitignore
@@ -40,4 +40,8 @@ context-reports/
 downloads/
 
 # Goal plugin state (per-project)
-.opencode/goals/
\ No newline at end of file
+.opencode/goals/
+
+# owt worktree plugin state (per-project, Task 164)
+.opencode/worktrees/
+.opencode/worktree-sessions.json
\ No newline at end of file
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 510a983..3ee6eaf 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -9,6 +9,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 ### Added
 
 - **DCP dynamic context pruning like goal plugin (Task 163):** Added `@tarquinen/opencode-dcp` to `plugin` arrays in project `opencode.json` + `tui.json` (parity with global, mirrors `@prevalentware/opencode-goal-plugin` pattern from Task 126); extended `LLM.txt` §7 JSON example + TUI parity block + Option A note, new §7.7 DCP install/config/commands (`opencode plugin @tarquinen/opencode-dcp@latest --global`, `dcp.jsonc` global + `.opencode/dcp.jsonc` override, `/dcp` + `/dcp-compress`), verification checklist DCP checks. Installed globally + verified 4-way parity.
+- **owt worktree plugin (Task 164):** Installed `@nano-step/opencode-worktree-plugin` globally (`npm i -g` + `owt-setup install` → `~/.config/opencode/plugins/worktree-plugin.js` + 7 slash commands incl. `/init-worktree`, `/list-worktrees`, `/open-worktree`; file-based loading kept, `opencode.json`/`tui.json` untouched by design — npm spec resolves from project `node_modules` which this docs-only repo has none of, and owt is not a TUI panel plugin). Chose owt over `kdcokenny/opencode-worktree` (OCX-only, OCX not allowed) and `arturosdg/opencode-worktree` (standalone TUI). Project side: `.gitignore` guards (`.opencode/worktrees/`, `worktree-sessions.json`), new `LLM.txt` §7.8 install/commands/verify docs. Optional `owt hook --global` left disabled.
 
 ## [9.10.0] - 2026-09-04
 
diff --git a/LLM.txt b/LLM.txt
index e0b2cf1..99cba3e 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -326,6 +326,29 @@ Defaults are applied automatically (enabled, autoUpdate, pruneNotification detai
 
 ---
 
+## 7.8. Install owt Worktree Plugin
+
+owt (`@nano-step/opencode-worktree-plugin`, npm, MIT) manages git worktrees across parallel OpenCode sessions: plugin tools (`createworktree`/`deleteworktree`/`listworktrees` + system-prompt injection) + slash commands (`/init-worktree`, `/list-worktrees`, `/open-worktree`) + `owt` shell CLI (`status`/`diff`/`log`/`merge`/`commit`, terminal auto-detect, `node_modules` symlink). Chosen over `kdcokenny/opencode-worktree` (OCX-registry only — OCX is not allowed here) and `arturosdg/opencode-worktree` (standalone TUI, not a plugin).
+
+```bash
+npm install -g @nano-step/opencode-worktree-plugin
+owt-setup install
+```
+
+`owt-setup install` copies the plugin to `~/.config/opencode/plugins/worktree-plugin.js` and slash commands to `~/.config/opencode/command/` (file-based loading — kept deliberately). The installer's config-based Option B (`"plugin": ["opencode-worktree-plugin"]` in `opencode.json`) is NOT adopted: it resolves from project `node_modules`, which this docs-only repo has none of, and the global file copy already covers every project session. `tui.json` is unchanged (owt is not a TUI panel plugin). Restart OpenCode after install (plugins + commands load at startup). Optional, not enabled: `owt hook --global` strips AI `Co-authored-by:` via a global `commit-msg` hook.
+
+Verify (project + global):
+
+```bash
+owt help && echo "owt CLI ✓"
+ls ~/.config/opencode/plugins/worktree-plugin.js && echo "global plugin ✓"
+ls ~/.config/opencode/command/init-worktree.md && echo "global commands ✓"
+```
+
+Worktree state lives in the project (gitignored): worktrees under `.opencode/worktrees/`, session names in `.opencode/worktree-sessions.json`.
+
+---
+
 ## 8. Clean Up Temporary Clone
 
 Remove the cloned repository from `/tmp/`:
@@ -363,6 +386,7 @@ After completing all steps, verify:
 - [ ] `~/.config/opencode/opencode.json` exists with **absolute paths** (not `~` or relative paths) and 5 `mcp` entries (`custom_context`, `project_memory`, `lint`, `blowsh`, `telegram`) + `blowsh_*`/`telegram_*` permissions, no former browser entry
 - [ ] `~/.config/opencode/opencode.json` + `tui.json` `plugin` arrays contain both `@prevalentware/opencode-goal-plugin` and `@tarquinen/opencode-dcp` (`grep -q "@tarquinen/opencode-dcp" ~/.config/opencode/opencode.json && grep -q "@tarquinen/opencode-dcp" ~/.config/opencode/tui.json`); project `opencode.json` + `tui.json` match (`diff -q tui.json ~/.config/opencode/tui.json`)
 - [ ] DCP loads: `opencode plugin list` shows `@tarquinen/opencode-dcp`, `/dcp` panel opens, `~/.config/opencode/dcp.jsonc` created on first run (project `.opencode/dcp.jsonc` overrides if present)
+- [ ] owt loads: `owt help` prints usage, `~/.config/opencode/plugins/worktree-plugin.js` + `~/.config/opencode/command/init-worktree.md` exist, `/init-worktree` recognised after restart
 - [ ] `~/.config/opencode/opencode.json` `blowsh` uses `docker run --rm -i ghcr.io/mokhtarabadi/blowsh-mcp:latest` (120s timeout) and `telegram` uses `uv --directory $HOME/.config/opencode/mcp-telegram-server run main.py` with allowed roots (`/tmp/telegram-mcp` + config dir downloads)
 - [ ] `~/.config/opencode/opencode-shell-strategy.md` exists (instructions file referenced by the `instructions` key)
 - [ ] `/tmp/cognitive-lead-hq` no longer exists
```
<!-- END_GIT_DIFF -->
