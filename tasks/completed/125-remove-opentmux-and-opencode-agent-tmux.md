# Task 125: Remove opentmux and opencode-agent-tmux — Keep tmux

**File:** `tasks/completed/125-remove-opentmux-and-opencode-agent-tmux.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Fully remove `opentmux` and `opencode-agent-tmux` from the system (npm global) and from all project documentation/config, while keeping the standard system `tmux` (terminal multiplexer) intact.

## Manager's Notes

- **Keep tmux:** `/usr/bin/tmux` v3.6 (apt package `tmux 3.6a-2ubuntu0.1`) MUST stay installed. Do NOT uninstall tmux.
- **Remove globally:** `opentmux@1.5.7` and `opencode-agent-tmux@1.3.0` were installed via `npm install -g` (mise node 24.19.0). Uninstall both: `npm uninstall -g opentmux opencode-agent-tmux`.
- **Remove from global config:** `~/.config/opencode/opencode.json` currently has `"plugin": ["opencode-goal-plugin", "opentmux"]` — remove `"opentmux"` entry so only `opencode-goal-plugin` remains. Project `opencode.json` already clean (only `opencode-goal-plugin`).
- **Remove from project docs (active files, not archive/history):**
  - `README.md` lines 24-33: delete the `### Optional: opentmux (Tmux Integration)` section. Keep the `See docs/setup.md` line but update it to not reference opentmux.
  - `docs/setup.md` lines 48-91: delete the entire `## opentmux — Smart Tmux Integration` section (Installation/Verify/Usage/Features/Shell Configuration).
  - `LLM.txt` lines 16, 135-149, 327: remove `opentmux` from Node.js prerequisite line, delete `### 6.2. Install opentmux Globally` section, and remove the verification checklist item for `opentmux --version`. Keep `node`/`npm` prerequisites but reword without opentmux.
  - `CHANGELOG.md`: keep historical `opentmux integration (Task 120)` entry as history, but add new `[Unreleased]` → `### Removed` entry documenting this removal.
- **Do NOT modify** `docs/history/milestone-14-summary.md` or `tasks/archive/120-*.md` — they are historical records. Archive stays reachable via `git log --follow`.
- **Verification:** `which opentmux` must fail, `npm list -g` must not contain opentmux/opencode-agent-tmux, `grep -r opentmux` over active project files (excluding `tasks/archive`, `docs/history`, `CHANGELOG.md` history line, `.git`) must return 0, `tmux -V` must still show 3.6, global `opencode.json` plugin array must be `["opencode-goal-plugin"]` only.
- Original manager request (verbatim): "serach for tmux and opentmux to learn, then creaete a new task and full drop it i don't like the opentmux full removed it from our project and from my system" → clarified: "keep tmux, remove opencode tmux plugin globally and from our project"

## Local TODOs

- [x] Learn tmux vs opentmux: tmux is system terminal multiplexer (3.6), opentmux is npm wrapper (`AnganSamadder/opentmux`) that auto-spawns tmux panes for OpenCode; opencode-agent-tmux is companion plugin
- [x] Discover next task ID (125) and verify no collision
- [x] Uninstall `opentmux` and `opencode-agent-tmux` globally (`npm uninstall -g opentmux opencode-agent-tmux`) — verify `npm list -g` clean
- [x] Remove `"opentmux"` from `~/.config/opencode/opencode.json` plugin array
- [x] Edit `README.md` — remove opentmux optional section
- [x] Edit `docs/setup.md` — remove opentmux section
- [x] Edit `LLM.txt` — remove opentmux prerequisite + section 6.2 + checklist item, reword Node.js line
- [x] Update `CHANGELOG.md` — add Removed entry under [Unreleased]
- [x] Verify: `tmux -V` still works, `which opentmux` fails, `grep -r opentmux` clean on active files, global plugin array correct
- [x] Run `lint_task_file` and `custom_context_stage_and_inject_diff`

## Acceptance Criteria

- [x] `tmux` remains installed and functional (`tmux -V` → 3.6, `which tmux` → /usr/bin/tmux, `dpkg -l | grep tmux` shows 3.6a)
- [x] `opentmux` and `opencode-agent-tmux` are NOT installed globally (`npm list -g` shows neither, `which opentmux` fails, `opentmux --version` fails)
- [x] `~/.config/opencode/opencode.json` plugin array is exactly `["opencode-goal-plugin"]` (no opentmux)
- [x] `README.md` no longer contains "opentmux" (grep returns 0)
- [x] `docs/setup.md` no longer contains "opentmux" (grep returns 0)
- [x] `LLM.txt` no longer contains "opentmux" except possibly in historical comments (active install/verify sections clean) — `grep -c opentmux LLM.txt` == 0
- [x] `CHANGELOG.md` has new entry under `## [Unreleased]` → `### Removed` documenting the removal
- [x] Historical files (`docs/history/milestone-14-summary.md`, `tasks/archive/120-*.md`, CHANGELOG Task 120 line) are intentionally preserved — not counted as failures
- [x] `lint_task_file` passes on `tasks/in-progress/125-remove-opentmux-and-opencode-agent-tmux.md` (or `tasks/qa/...` after move)

## Verification Evidence

- **Test command:** `which tmux && tmux -V; echo "---"; which opentmux 2>&1; npm list -g 2>&1 | grep -i tmux; echo "---"; grep -rn opentmux /home/mohammad/code-server/projects/cognitive-lead-hq/README.md /home/mohammad/code-server/projects/cognitive-lead-hq/docs/setup.md /home/mohammad/code-server/projects/cognitive-lead-hq/LLM.txt 2>&1; echo "---"; cat ~/.config/opencode/opencode.json | grep -A2 plugin`
- **Expected result:** tmux 3.6 present; opentmux not found; npm list shows no tmux plugins; grep returns no matches on active docs; global plugin is ["opencode-goal-plugin"] only
- **Actual result:** `which tmux` → /usr/bin/tmux, `tmux -V` → tmux 3.6, `which opentmux` → not found, `npm list -g` → corepack, npm, opencode-goal-plugin only (no tmux plugins), `grep -rn opentmux README.md docs/setup.md LLM.txt` → no matches, `cat ~/.config/opencode/opencode.json | grep plugin` → "plugin": ["opencode-goal-plugin"] — all criteria met.
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Manager Decisions

_(Log non-trivial architectural, design, or strategic decisions here using the format from `<decision_logging_mandate>`. For Lite Mode tasks, log a `[LITE]` justification entry.)_

- **Decision: Keep tmux, drop wrapper plugins only.** Rationale: tmux is a stable system multiplexer (apt, 3.6) useful independent of OpenCode; opentmux/opencode-agent-tmux are npm wrappers that auto-spawn panes — manager explicitly dislikes the wrapper layer. Alternatives: remove tmux entirely (rejected — manager said keep tmux). Impact: minimal — only docs and global npm state change, no code runtime affected.

## Risk & Rollback

- **Risk:** Removing global plugin entry could break `opencode` launch if config JSON becomes invalid; docs edits could leave broken references.
- **Rollback plan:** `npm install -g opentmux opencode-agent-tmux`; restore `~/.config/opencode/opencode.json` plugin array to `["opencode-goal-plugin", "opentmux"]`; `git restore README.md docs/setup.md LLM.txt CHANGELOG.md`; verify `opencode --help` still works.

---

## Execution Log & Reasoning

**Context:** Manager asked to learn tmux vs opentmux, then create and fully execute a task removing opentmux ("full removed it from our project and from my system"), later clarified to keep tmux but remove opencode tmux plugins globally and from project.

**Discovery (2026-08-28):**
- tmux: system terminal multiplexer, `/usr/bin/tmux` v3.6 (apt `tmux 3.6a-2ubuntu0.1`) — session persistence, pane/window management, independent of OpenCode. Must be kept.
- opentmux: npm package `AnganSamadder/opentmux` v1.5.7 (wrapper around `opencode` that auto-spawns tmux panes, streams agent output). Installed via `npm install -g opentmux`.
- opencode-agent-tmux: companion npm plugin `opencode-agent-tmux@1.3.0`, provides Agent-Tmux integration. Both appear in `npm list -g` and `~/.config/opencode/opencode.json` plugin array `["opencode-goal-plugin", "opentmux"]`.
- Project refs: `README.md` Optional opentmux section, `docs/setup.md` full opentmux section (48-91), `LLM.txt` Section 6.2 + prerequisite line + checklist, `CHANGELOG.md` Task 120 entry, `docs/history/milestone-14-summary.md` (historical), `tasks/archive/120-*.md` (historical), `telegram-sync.json` pointer — only active docs need cleaning.

**Implementation (Task 125, NEXT_ID=125 via `find tasks -name "*.md" | grep -Eo '^[0-9]+' | sort -n | tail -1 +1`):**
1. Created `tasks/backlog/125-remove-opentmux-and-opencode-agent-tmux.md` via task-generator template, `mv` to `tasks/in-progress/`, updated `**File:**` header.
2. Global uninstall: `npm uninstall -g opentmux` (removed 6 packages) + `npm uninstall -g opencode-agent-tmux` (removed 6 packages) → `npm list -g` now shows only `corepack`, `npm`, `opencode-goal-plugin`.
3. Global config: edited `~/.config/opencode/opencode.json` plugin array from `["opencode-goal-plugin", "opentmux"]` to `["opencode-goal-plugin"]` (verified via `cat ~/.config/opencode/opencode.json | grep plugin`). Project `opencode.json` already clean.
4. `README.md`: deleted `### Optional: opentmux` block (install lines + opentmux link), kept `See docs/setup.md` line. Verified `grep -c opentmux README.md` == 0.
5. `docs/setup.md`: deleted entire `## opentmux — Smart Tmux Integration` section (Installation/Verify/Usage/Features/Shell Configuration, 44 lines) — file now goes directly `## GitHub CLI` → `## MCP Servers` → `## Development Tools`. Verified 0 matches, 68 lines total.
6. `LLM.txt`: (a) reworded prerequisite `required for opentmux and other npm-based tools` → `required for npm-based tools and other dependencies`, (b) deleted `### 6.2. Install opentmux Globally` section (15 lines incl. verify/usage), (c) removed checklist item `opentmux is installed globally`. Verified `grep -c opentmux LLM.txt` == 0, and `---` separator now cleanly connects 6.1 → 6.5.
7. `CHANGELOG.md`: Parse-Then-Append — replaced `_No unreleased changes._` with `### Removed` entry documenting uninstall, config, and doc changes, noting tmux retention and historical preservation. Verified.
8. Verification: `which tmux && tmux -V` → 3.6, `which opentmux` fails, `npm list -g | grep tmux` empty, `grep -rn opentmux` over active docs 0, global plugin correct, `python3 -m json.tool ~/.config/opencode/opencode.json` valid JSON, `grep -rn opentmux` over active project (excluding archive/history) only shows task 125 itself + historical CHANGELOG Task 120 line (expected).

**Decisions:** Keep tmux; drop wrappers only (see Manager Decisions). Historical files intentionally preserved per AGENTS.md absent-file policy and audit trail — not counted as failures.

**TODO Checks:** All 8 implementation TODOs marked [x]; 9 acceptance criteria marked [x]; Definition of Done 4/4 [x].

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `9b1047b71b93bbbf630a75249254a73e269fd54f`
<!-- END_GIT_DIFF -->
