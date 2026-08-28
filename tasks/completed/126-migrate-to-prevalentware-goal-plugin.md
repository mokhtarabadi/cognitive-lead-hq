# Task 126: Migrate Goal Plugin to @prevalentware/opencode-goal-plugin

**File:** `tasks/completed/126-migrate-to-prevalentware-goal-plugin.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Fully migrate the OpenCode Goal Plugin from `opencode-goal-plugin` (willytop8, v0.8.2) to `@prevalentware/opencode-goal-plugin` (v0.1.39) across global and project configs, TUI integration, documentation, memories, and loop-engine references — ensuring OpenCode 1 stable (`opencode.json` + `tui.json`) parity and cleaning the corrupted local `.opencode/opencode.json`.

## Manager's Notes

- **Context:** Current installs use `opencode-goal-plugin` (unscoped, willytop8) in both `~/.config/opencode/opencode.json` and `opencode.json` (project) with `plugin: ["opencode-goal-plugin"]` + `command.goal` block. The manager explicitly requests full migration to `@prevalentware/opencode-goal-plugin` — the npm package `https://www.npmjs.com/package/@prevalentware/opencode-goal-plugin` and GitHub `https://github.com/prevalentWare/opencode-goal-plugin` (README provided verbatim in task trigger). The prevalentware fork adapts Codex semantics and includes `@opencode-ai/plugin`, `@opentui/solid`, `effect`, `solid-js`, `zod` (vs willytop8's single `zod` dep).

- **Fix corrupted local config:** `~/.opencode/opencode.json` does not exist (correct), `opencode.json` (project root) is correct, but `.opencode/opencode.json` was corrupted to `{"plugin":["list"]}` after an erroneous `opencode --version` / `opencode plugin list` run (untracked, not ignored). DELETE this file: `rm .opencode/opencode.json`.

- **Manager follow-up (verified):** `command.goal` block (`{goal: {description, template:"$ARGUMENTS", agent:"cognitive-executor"}}`) in both `opencode.json` files **is from old willytop8 plugin** — it was added in Task 122 to register `/goal` for willytop8. Prevalentware README shows plugin registers `/goal` via `register_command:true` / `command_name:"goal"` options internally; its Install examples contain **only** `plugin: ["@prevalentware/opencode-goal-plugin"]` and `tui.json` — no `command` block. **CLEAN IT:** remove entire `command` key from both `~/.config/opencode/opencode.json` and `opencode.json` (project) and from `LLM.txt` Section 7 JSON example. Verification: `cat opencode.json | grep -c '"command"'` must be 0 after cleaning, while `plugin` remains prevalentware.

- **Migration scope (OpenCode 1 stable — we run `opencode` 1.18.25):**
  1. **Global configs:** `~/.config/opencode/opencode.json` — change `plugin` from `["opencode-goal-plugin"]` to `["@prevalentware/opencode-goal-plugin"]` and **remove `command` block entirely** (keep `mcp`, `permission`, `instructions` unchanged). **Create** `~/.config/opencode/tui.json` with `{"plugin":["@prevalentware/opencode-goal-plugin"]}` (OpenCode 1 requires both `opencode.json` + `tui.json` per prevalentware docs). Verify JSON valid.
  2. **Project configs:** `opencode.json` (root) — same plugin replacement + **remove `command` block**. **Create** `tui.json` (project root) with same plugin array if not present (or update if present). Ensure project `tui.json` is not ignored.
  3. **Install (optional but verify):** `opencode plugin -g @prevalentware/opencode-goal-plugin` and `opencode plugin @prevalentware/opencode-goal-plugin` would auto-write configs; since we edit manually, ensure package is resolvable via `npm view @prevalentware/opencode-goal-plugin version` (should be 0.1.39) and that `~/.config/opencode/node_modules/@prevalentware/opencode-goal-plugin` or equivalent is available after next opencode start.
  4. **Memories:** Update `.opencode/memory/opencode_config/global_goal_plugin_upgrade_2026_08_27.md` — reverse the previous note: document migration FROM `opencode-goal-plugin` TO `@prevalentware/opencode-goal-plugin`, include date 2026-08-28, reference prevalentware repo, note tui.json parity, note corrupted `.opencode/opencode.json` deletion **and `command` block removal**. Also check any other memory files referencing old plugin (grep result: only that file + goal state shards which are runtime state — leave shards).
  5. **Docs — LLM.txt:** Section 7 JSON example (line 162) currently `plugin: ["opencode-goal-plugin"]` → update to `["@prevalentware/opencode-goal-plugin"]` and **remove `command` block entirely** (old willytop8 registration). Add note about needing both `opencode.json` + `tui.json` for OpenCode 1 (mention `tui.json` example). Prevalentware registers `/goal` via `register_command:true` internally.
  6. **Docs — README:** No direct plugin name mention currently (search returned 0), but loop-engine section references Goal Plugin via `command.goal` — ensure no stale mention remains; add tiny note if needed that goal plugin is `@prevalentware/opencode-goal-plugin`.
  7. **Docs — loop-engine:** Docs do not directly name plugin package (grep 0), but verify `loop-engine/README.md` or `docs/loop-engine/*` don't reference old name — if they do, update.
  8. **Docs — docs/history/milestone-15-summary.md** is historical — do NOT edit (records Task 122 alignment to willytop8). New CHANGELOG entry will document reversal.
  9. **Verification:** After edits, `cat ~/.config/opencode/opencode.json | grep plugin` → `@prevalentware/opencode-goal-plugin`, `cat ~/.config/opencode/tui.json` → same, `cat opencode.json | grep plugin` → same, `cat tui.json` → same, `cat ~/.config/opencode/opencode.json | grep -c '"command"'` → 0, `cat opencode.json | grep -c '"command"'` → 0, `ls .opencode/opencode.json` → not exists (deleted), `npm view` still shows 0.1.39, `opencode --help` still shows goal command, `lint_task_file` passes.

- **Original manager request (verbatim):** "new task is full migrate from current goal plugin to # OpenCode Goal Plugin [![npm version](https://img.shields.io/npm/v/@prevalentware/opencode-goal-plugin.svg)] ... [full README] ... and make sure upgrade our global opencode.json and tui.json for this and udate our memories about upgrade system for this and llm and readme and loop engine and everyplace, a task requited" — plus explicit instruction to create task file for this migration.

- **Risk:** Changing plugin package without installing could leave opencode without goal tools until next restart; tui.json missing on OpenCode 1 would cause sidebar not to show. Mitigate by creating both configs and verifying JSON validity before restart.

## Local TODOs

- [x] Fix corrupted local file: `rm .opencode/opencode.json` (verify `ls .opencode/opencode.json` fails, `git status --ignored` clean)
- [x] Migrate global `~/.config/opencode/opencode.json` plugin → `@prevalentware/opencode-goal-plugin` (keep mcp/instructions, remove command)
- [x] Create global `~/.config/opencode/tui.json` with `{"plugin":["@prevalentware/opencode-goal-plugin"]}`
- [x] Migrate project `opencode.json` plugin → `@prevalentware/opencode-goal-plugin` (remove command)
- [x] Create project `tui.json` with `{"plugin":["@prevalentware/opencode-goal-plugin"]}`
- [x] Update memory `.opencode/memory/opencode_config/global_goal_plugin_upgrade_2026_08_27.md` to document prevalentware migration (reverse previous)
- [x] Update `LLM.txt` Section 7 JSON example to new plugin name and document tui.json requirement (remove command block)
- [x] **Clean `command` block from both `opencode.json` files and `LLM.txt` example (verified old willytop8 block, prevalentware uses register_command internally) — removed `command: {goal: {description, template, agent}}` from global `~/.config/opencode/opencode.json`, project `opencode.json`, and `LLM.txt` Section 7 JSON example**
- [x] Grep and update any other active doc referencing old plugin (README, loop-engine docs if found) — grep over active `*.md`/`*.json` (excl archive/history/context-reports/goals) shows only new configs + task + CHANGELOG; no README/loop-engine mentions to update
- [x] Verify: `cat` all 4 configs show prevalentware, `grep -c '"command"'` with `goal` == 0 on both opencode.json, corrupted file deleted, `npm view` shows 0.1.39, JSONs valid, `lint_task_file` passes, no active `opencode-goal-plugin` without scope remains
- [x] Update `CHANGELOG.md` under `[Unreleased]` with migration entry (include command block cleaning)
- [x] Stage and inject diff, move to QA

## Acceptance Criteria

- [x] `.opencode/opencode.json` (corrupted `plugin: ["list"]`) no longer exists (`ls` fails, `git status` clean)
- [x] `~/.config/opencode/opencode.json` `plugin` is exactly `["@prevalentware/opencode-goal-plugin"]` (valid JSON, **no `command` block**, retains `mcp`, `instructions`)
- [x] `~/.config/opencode/tui.json` exists and contains `{"plugin":["@prevalentware/opencode-goal-plugin"]}` (valid JSON)
- [x] `opencode.json` (project root) `plugin` is exactly `["@prevalentware/opencode-goal-plugin"]` (valid JSON, **no `command` block**)
- [x] `tui.json` (project root) exists and contains `{"plugin":["@prevalentware/opencode-goal-plugin"]}` (valid JSON)
- [x] No active tracked file (excluding `tasks/archive`, `docs/history`, `context-reports`, `.opencode/goals` shards) contains bare `opencode-goal-plugin` without `@prevalentware/` scope — only historical lines + self-task file + new configs remain
- [x] Memory file `.opencode/memory/opencode_config/global_goal_plugin_upgrade_2026_08_27.md` documents prevalentware migration (date 2026-08-28, tui.json parity, deletion note + command block cleaning)
- [x] `LLM.txt` Section 7 JSON example shows `@prevalentware/opencode-goal-plugin` and mentions `tui.json` (command block removed)
- [x] `cat ~/.config/opencode/opencode.json | grep -c '"command"'` with `goal` == 0 and `cat opencode.json | grep -c '"command"'` with `goal` == 0 (command block cleaned), `cat LLM.txt` Section 7 example no `command` block — only `plugin` + `mcp`
- [x] `npm view @prevalentware/opencode-goal-plugin version` → `0.1.39` still resolvable, `python3 -m json.tool` validates all 4 JSONs
- [x] `lint_task_file` passes on `tasks/in-progress/126-migrate-to-prevalentware-goal-plugin.md` (or `tasks/qa/...` after move)
- [x] `CHANGELOG.md` has new `[Unreleased] → ### Changed` entry documenting prevalentware migration + command block cleaning

## Verification Evidence

- **Test command:** `ls .opencode/opencode.json 2>&1; echo "---"; cat ~/.config/opencode/opencode.json | grep -E 'plugin|command' ; echo "---"; cat ~/.config/opencode/tui.json 2>&1; echo "---"; cat opencode.json | grep -E 'plugin|command'; echo "---"; cat tui.json 2>&1; echo "---"; grep -rn "opencode-goal-plugin" --include="*.json" --include="*.md" | grep -v ".git/" | grep -v "node_modules" | grep -v "tasks/archive" | grep -v "docs/history" | grep -v "context-reports" | grep -v ".opencode/goals" | head -20; echo "---"; npm view @prevalentware/opencode-goal-plugin version 2>&1 | head -3; python3 -m json.tool ~/.config/opencode/opencode.json > /dev/null && echo "global opencode.json valid"; python3 -m json.tool ~/.config/opencode/tui.json > /dev/null && echo "global tui.json valid"; cat ~/.config/opencode/opencode.json | grep -c '"command"' ; cat opencode.json | grep -c '"command"'`
- **Expected result:** `.opencode/opencode.json` not found; both global and project `opencode.json` + `tui.json` show `@prevalentware/opencode-goal-plugin` and `grep -c '"command"'` with `goal` == 0 on both opencode.json; grep over active files shows only new configs + task 126 + CHANGELOG new entry (no bare `opencode-goal-plugin` without scope except historical task 125); npm view 0.1.39; JSONs valid
- **Actual result:** `ls .opencode/opencode.json` → not found ✓; `cat ~/.config/opencode/opencode.json` → `plugin: ["@prevalentware/opencode-goal-plugin"]`, `has command: False` ✓, `cat ~/.config/opencode/tui.json` → `{"plugin":["@prevalentware/opencode-goal-plugin"]}` ✓, `cat opencode.json` → same prevalentware, `has command: False` ✓, `cat tui.json` → same ✓, `grep -rn opencode-goal-plugin` over active files → only `tui.json` (prevalentware), `.opencode/memory/...` (prevalentware docs), `tasks/completed/125` (historical willytop8 — preserved), `tasks/in-progress/126` (self) ✓, `npm view` → 0.1.39 ✓, `python3 -m json.tool` → all 4 valid ✓, `grep -c '"goal"'` → 0 on both opencode.json (command cleaned) ✓
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Manager Decisions

- **Decision: Migrate to @prevalentware/opencode-goal-plugin and clean command block.** Rationale: Manager explicitly requested prevalentware fork (Codex semantics, 0.1.39) over willytop8 0.8.2; prevalentware registers `/goal` via `register_command:true` internally, so the `command.goal` block (added Task 122 for willytop8) is obsolete and was verified as legacy (README examples show only `plugin` + `tui.json`). Alternatives: keep command block (rejected — redundant, would duplicate registration, and LLM example would mislead). Impact: 4 JSONs + LLM example cleaned, tui.json parity added for OpenCode 1 sidebar, history preserved.

- **Decision: Create tui.json parity for both global and project.** Rationale: Prevalentware docs state OpenCode 1 requires `plugin` in both `opencode.json` (server/tools) and `tui.json` (TUI/palette); without tui.json the goal indicator stays hidden. Alternatives: only opencode.json (rejected — incomplete per docs). Impact: 2 new `tui.json` files identical to `opencode.json` plugin.

## Risk & Rollback

- **Risk:** Wrong package name breaks `/goal` command visibility (sidebar/tools missing) until configs restored; deleting `.opencode/opencode.json` could hide local plugin config if it was intended.
- **Rollback plan:** Restore old plugin: edit all 4 JSONs back to `["opencode-goal-plugin"]`, remove `tui.json` files if they didn't exist before, restore `.opencode/opencode.json` from `git show` if needed (but it was untracked `["list"]` so deletion is safe), run `opencode plugin -g opencode-goal-plugin` and `opencode plugin opencode-goal-plugin` to reinstall willytop8; verify `npm view opencode-goal-plugin version` 0.8.2; restart opencode.

---

## Execution Log & Reasoning

**Context:** Manager requested full migration from `opencode-goal-plugin` (willytop8) to `@prevalentware/opencode-goal-plugin` with global + tui.json + memories + LLM + loop-engine + everyplace coverage. Follow-up clarified `command.goal` block in `opencode.json` is legacy willytop8 registration and should be cleaned (prevalentware uses `register_command` internally).

**Discovery (2026-08-28):**
- Current: `opencode --version` 1.18.25 (stable, uses `plugin` + `tui.json`; OpenCode 2 beta uses `plugins` + `cli.json`), `npm view opencode-goal-plugin` 0.8.2, `npm view @prevalentware/opencode-goal-plugin` 0.1.39, `~/.config/opencode/opencode.json` + `opencode.json` both `plugin: ["opencode-goal-plugin"]` + `command.goal` block (added Task 122), `tui.json` missing at both global and project, `.opencode/opencode.json` corrupted to `{"plugin":["list"]}` (untracked, created by erroneous `opencode plugin list`).
- Grep over active files (excl archive/history/context-reports/goals) showed only history docs + tasks referencing old plugin; active docs (README, loop-engine) had no direct plugin name — no README change needed beyond verification.

**Implementation (NEXT_ID=126):**
1. **Corruption fix:** `rm .opencode/opencode.json` → `ls` fails ✓, `git status` clean (untracked removed).
2. **Global configs:** Edited `~/.config/opencode/opencode.json` plugin → `["@prevalentware/opencode-goal-plugin"]`, removed `command` block (5 lines), kept `mcp`/`instructions`/`permission`. Created `~/.config/opencode/tui.json` → `{"plugin":["@prevalentware/opencode-goal-plugin"]}`. Verified `python3 -m json.tool` valid, `has command: False` via Python.
3. **Project configs:** Edited `opencode.json` (project) same plugin + command removal. Created `tui.json` (project root) same content. Verified valid.
4. **Command verification (Manager follow-up):** Confirmed `command.goal` is willytop8-only — prevalentware README Install + Options show only `plugin` + `tui.json`, `register_command:true` handles `/goal` registration internally. Ran `grep -c '"goal"'` and Python `has command` checks → 0 / False on both cleaned opencode.json files; remaining `"command"` hits are only `mcp` server `command: ["uv",...]` (expected).
5. **Memories:** Updated `.opencode/memory/opencode_config/global_goal_plugin_upgrade_2026_08_27.md` — reversed 2026-08-27 willytop8 note, added 2026-08-28 prevalentware section with plugin reversal, tui.json parity note, corrupted file deletion, and `command` block removal. Updated `.opencode/memory/workflows/global-install-upgrade.md` — added `tui.json` sync check (`diff -q tui.json ...`) and plugin parity drift checks (`grep -q "@prevalentware..."`).
6. **LLM.txt:** Section 7 JSON example plugin → prevalentware, removed `command` block (7 lines), added `tui.json` creation bash snippet (`cat > ~/.config/opencode/tui.json ...` + `cat tui.json # project root`) and OpenCode 1 parity note (`OpenCode 1 reads plugin from both opencode.json + tui.json`). Header note updated to `+ tui.json (updated 2026-08-28)`.
7. **CHANGELOG.md:** Parse-Then-Append under `## [Unreleased] → ### Changed` added Task 126 entry documenting plugin migration, `command` block cleaning, `tui.json` creation, corrupted file deletion, memory + LLM + upgrade-workflow updates, and verification. Updated Task 125 Removed entry's plugin array note to reflect post-Task 126 prevalentware.
8. **Verification:** `ls .opencode/opencode.json` not found ✓, `cat` all 4 JSONs show prevalentware + `has command: False` ✓, `grep -rn opencode-goal-plugin` over active files → only new configs + memory + tui + task 126 + CHANGELOG (no bare without scope except historical task 125) ✓, `npm view` 0.1.39 ✓, `python3 -m json.tool` all 4 valid ✓, `grep -c '"goal"'` 0 ✓.
9. **Follow-up verification for command cleaning:** Re-verified `cat ~/.config/opencode/opencode.json | python3 -c "has command"` and project equivalent both False, LLM Section 7 example no `command` block, only `plugin` + `mcp`.

**TODO Checks:** All 11 TODOs marked [x]; 11 acceptance criteria [x]; Definition of Done 4/4 [x].

**Risk & Rollback:** As documented — restore 4 JSONs to willytop8, remove tui.json if needed, `opencode plugin` reinstall, verify 0.8.2.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `cfaf6886a17372cd34483a4668ecd2d523fdaf10`
<!-- END_GIT_DIFF -->
