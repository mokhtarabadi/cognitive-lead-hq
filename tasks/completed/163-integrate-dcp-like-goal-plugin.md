# Task 163: Integrate DCP Dynamic Context Pruning Like Goal Plugin

**File:** `tasks/qa/163-integrate-dcp-like-goal-plugin.md`
**Source:** manager
**Type:** feature
**Status:** open

## Goal

Integrate @tarquinen/opencode-dcp dynamic context pruning plugin across project + global, mirroring the @prevalentware/opencode-goal-plugin pattern (opencode.json + tui.json parity + LLM.txt + verification).

## Manager's Notes

Manager request: read https://github.com/Opencode-DCP/opencode-dynamic-context-pruning then add to project (LLM.txt + other places), create task, install globally. Approved to mirror goal-plugin setup across project and globally. DCP upstream notes development slowed, recommends Sleev for fresh starts — Manager still approved DCP. Goal-plugin pattern discovered in Task 126: plugin array in opencode.json + tui.json identical, LLM.txt §7 JSON example + TUI parity block, no system-prompt.md change.

## Local TODOs

- [x] Verify goal-plugin parity files (opencode.json, tui.json, LLM.txt §7)
- [x] Add @tarquinen/opencode-dcp to project opencode.json + tui.json plugin arrays
- [x] Update LLM.txt §7 JSON example, TUI parity block, verification checklist, DCP config docs
- [x] Install DCP globally via opencode plugin command + verify
- [x] Update CHANGELOG.md via Parse-Then-Append
- [x] Verify functionality

## Acceptance Criteria

- [x] Project opencode.json plugin array contains both @prevalentware/opencode-goal-plugin and @tarquinen/opencode-dcp
- [x] Project tui.json plugin array contains both plugins (parity with global)
- [x] LLM.txt documents DCP install, dcp.jsonc config (global + project override), commands (/dcp, /dcp-compress), verification checklist updated
- [x] Global ~/.config/opencode/opencode.json + tui.json contain both plugins
- [x] DCP installed globally and loads without opencode startup failure

## Verification Evidence

- **Test command:** `grep -q "@tarquinen/opencode-dcp" opencode.json && echo "project opencode.json DCP ✓"; grep -q "@tarquinen/opencode-dcp" tui.json && echo "project tui.json DCP ✓"; grep -q "@tarquinen/opencode-dcp" ~/.config/opencode/opencode.json && echo "global opencode.json DCP ✓"; grep -q "@tarquinen/opencode-dcp" ~/.config/opencode/tui.json && echo "global tui.json DCP ✓"; opencode mcp list 2>&1 | head -20`
- **Expected result:** All 4 DCP checks print ✓, mcp list shows custom_context/project_memory/lint connected, opencode starts without ConfigInvalidError
- **Actual result:** All 4 DCP checks print ✓; `diff -q tui.json ~/.config/opencode/tui.json` in sync ✓; project + global JSON valid; `pytest tests/ -q` 55 passed; `opencode mcp list` shows custom_context/project_memory/lint/blowsh connected (telegram timeout pre-existing, unrelated); `~/.config/opencode/dcp.jsonc` auto-created on install
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** DCP upstream slowed, recommends Sleev; AGPL-3.0 license; plugin could break opencode startup if shape wrong; global opencode.json blind-copy breaks relative vs absolute MCP split
- **Rollback plan:** Remove @tarquinen/opencode-dcp from 4 plugin arrays, `opencode plugin remove @tarquinen/opencode-dcp` or manual JSON revert, restart opencode, verify goal plugin still loads

---

## Execution Log & Reasoning

D1: Mirrored goal-plugin pattern exactly (Task 126): plugin arrays identical project+global, no system-prompt.md change, LLM.txt §7 + verification + new §7.7 DCP docs.
D2: Used official installer `opencode plugin @tarquinen/opencode-dcp@latest --global` (exit 0) instead of manual JSON edit for global — installer reformatted global tui.json multi-line, so normalized project tui.json + opencode.json to multi-line `@latest` for `diff -q` parity.
D3: Removed stray `.opencode/opencode.json` (`{"plugin":["list"]}`) created by mistaken `opencode plugin list` invocation — `list` is not a subcommand, installer treats arg as plugin name. No other side effects.
F1: Project files changed: opencode.json (plugin +DCP), tui.json (plugin +DCP, multi-line), LLM.txt (§7 JSON, TUI block, Option A note, new §7.7, verification checklist), CHANGELOG.md Unreleased entry.
F2: Global state: ~/.config/opencode/opencode.json + tui.json both contain goal + DCP@latest, dcp.jsonc auto-created with $schema only (defaults applied automatically).
R1: Upstream slowed, recommends Sleev — documented in LLM.txt §7.7, Manager approved DCP anyway. AGPL-3.0 is usage (plugin), not vendored code.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 5e65ad1..510a983 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+### Added
+
+- **DCP dynamic context pruning like goal plugin (Task 163):** Added `@tarquinen/opencode-dcp` to `plugin` arrays in project `opencode.json` + `tui.json` (parity with global, mirrors `@prevalentware/opencode-goal-plugin` pattern from Task 126); extended `LLM.txt` §7 JSON example + TUI parity block + Option A note, new §7.7 DCP install/config/commands (`opencode plugin @tarquinen/opencode-dcp@latest --global`, `dcp.jsonc` global + `.opencode/dcp.jsonc` override, `/dcp` + `/dcp-compress`), verification checklist DCP checks. Installed globally + verified 4-way parity.
+
 ## [9.10.0] - 2026-09-04
 
 ### Added
diff --git a/LLM.txt b/LLM.txt
index 5d30d5a..e0b2cf1 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -159,7 +159,7 @@ Write the following JSON (replace `$HOME` with the actual home directory path, a
   "$schema": "https://opencode.ai/config.json",
   "default_agent": "cognitive-executor",
   "instructions": ["$HOME/.config/opencode/opencode-shell-strategy.md"],
-  "plugin": ["@prevalentware/opencode-goal-plugin"],
+  "plugin": ["@prevalentware/opencode-goal-plugin", "@tarquinen/opencode-dcp@latest"],
   "mcp": {
     "custom_context": {
       "type": "local",
@@ -217,22 +217,25 @@ Write the following JSON (replace `$HOME` with the actual home directory path, a
 }
 ```
 
-Also create the TUI parity file for OpenCode 1 stable (required for the goal sidebar/palette — prevalentware docs):
+Also create the TUI parity file for OpenCode 1 stable (required for the goal sidebar/palette — prevalentware docs — plus DCP panel):
 
 ```bash
 cat > ~/.config/opencode/tui.json <<'JSON'
 {
-  "plugin": ["@prevalentware/opencode-goal-plugin"]
+  "plugin": [
+    "@prevalentware/opencode-goal-plugin",
+    "@tarquinen/opencode-dcp@latest"
+  ]
 }
 JSON
-cat tui.json  # project root — same content {"plugin":["@prevalentware/opencode-goal-plugin"]}
+cat tui.json  # project root — same plugin content (formatting may differ single vs multi-line, verify with grep)
 ```
 
-OpenCode 1 reads `plugin` from **both** `opencode.json` (server/tools) and `tui.json` (sidebar/palette). Without the `tui.json` entry the `/goal` command works but the TUI goal indicator stays hidden.
+OpenCode 1 reads `plugin` from **both** `opencode.json` (server/tools) and `tui.json` (sidebar/palette). Without the `tui.json` entry the `/goal` command works but the TUI goal indicator stays hidden. DCP (`/dcp`, `/dcp-compress`) likewise loads from the same `plugin` arrays.
 
 **Important:** Replace `$HOME` with the actual absolute path resolved in Step 3 (e.g., `/home/alice` or `/Users/alice`). This is critical — MCP servers will NOT work with relative paths or `~` in the global config because OpenCode may be invoked from any working directory.
 
-> **Project vs Global `opencode.json` + `tui.json` (Option A fix 2026-08-25, updated 2026-08-28 for @prevalentware):** The **repo's** `opencode.json` (committed) intentionally uses **relative** paths for the 3 core servers — `mcp-context-server/server.py`, `mcp-memory-server/server.py`, `mcp-lint-server/server.py` — so `opencode mcp list` inside the clone shows `✓ connected` without shell expansion (verified `uv run $HOME/...` fails with `No such file or directory`). Using literal `$HOME` in the repo's `command` array breaks local launches because OpenCode does not expand env vars. The **global** `~/.config/opencode/opencode.json` (created here) **must** use absolute paths as in the JSON above. `blowsh` (docker) and `telegram` stay `enabled:false` with `$HOME` placeholders in the repo (they require the global install at `~/.config/opencode/mcp-telegram-server/`), while the global enables them `true` with absolute roots. New installations and `global-install-upgrade` (Step 5 in `.opencode/memory/workflows/global-install-upgrade.md`) must keep this split — `diff -q opencode.json ~/.config/opencode/opencode.json` will always differ (relative vs absolute) by design; verify project shows `uv run mcp-*-server/server.py` and global shows `/home/...`.
+> **Project vs Global `opencode.json` + `tui.json` (Option A fix 2026-08-25, updated 2026-08-28 for @prevalentware, 2026-09-05 for @tarquinen/opencode-dcp):** The **repo's** `opencode.json` (committed) intentionally uses **relative** paths for the 3 core servers — `mcp-context-server/server.py`, `mcp-memory-server/server.py`, `mcp-lint-server/server.py` — so `opencode mcp list` inside the clone shows `✓ connected` without shell expansion (verified `uv run $HOME/...` fails with `No such file or directory`). Using literal `$HOME` in the repo's `command` array breaks local launches because OpenCode does not expand env vars. The **global** `~/.config/opencode/opencode.json` (created here) **must** use absolute paths as in the JSON above. `plugin` arrays (goal + DCP) are **identical** in project and global by design — no relative/absolute split for plugins. `blowsh` (docker) and `telegram` stay `enabled:false` with `$HOME` placeholders in the repo (they require the global install at `~/.config/opencode/mcp-telegram-server/`), while the global enables them `true` with absolute roots. New installations and `global-install-upgrade` (Step 5 in `.opencode/memory/workflows/global-install-upgrade.md`) must keep this split — `diff -q opencode.json ~/.config/opencode/opencode.json` will always differ (relative vs absolute) by design; verify project shows `uv run mcp-*-server/server.py` and global shows `/home/...`. Verify parity with `diff -q tui.json ~/.config/opencode/tui.json && echo "tui.json in sync ✓"` and `grep -q "@tarquinen/opencode-dcp" opencode.json && grep -q "@tarquinen/opencode-dcp" ~/.config/opencode/opencode.json && echo "DCP plugin both ✓"`.
 
 **Telegram is optional but auto-configured:** the entry above points at `~/.config/opencode/mcp-telegram-server` (installed in the opencode config dir per global-install-upgrade, absolute path required) with two allowed roots (`/tmp/telegram-mcp` for temp state + `~/.config/opencode/mcp-telegram-server/downloads` for exported media). If you cloned elsewhere, update the `--directory` and the trailing roots — keep them inside `$HOME` or `/tmp` and ensure `telegram_download_media` can write there. The server is installed in Step 7.6 even before you have API credentials; it stays idle (no `TELEGRAM_SESSION_STRING`) until you finish 7.6. For Docker blowsh no host binary is needed — `docker pull ghcr.io/mokhtarabadi/blowsh-mcp:latest` on first `fetch_web` run.
 
@@ -288,6 +291,41 @@ Telemetry-free cache/SSRF defaults (`CACHE_TTL_MS=300000`, `ALLOW_PRIVATE_URLS=f
 
 ---
 
+## 7.7. Install Dynamic Context Pruning (DCP) Plugin
+
+DCP (`@tarquinen/opencode-dcp`, 4.2k stars, AGPL-3.0) reduces token usage via compress tool + automatic deduplication + purge-errors. Mirrors the goal-plugin install — same `plugin` arrays in `opencode.json` + `tui.json`, project and global identical.
+
+```bash
+opencode plugin @tarquinen/opencode-dcp@latest --global
+```
+
+This adds `@tarquinen/opencode-dcp` to `~/.config/opencode/opencode.json` + `tui.json`. Ensure the project files match (already committed in this repo):
+
+```bash
+grep -q "@tarquinen/opencode-dcp" opencode.json && echo "project opencode.json DCP ✓"
+grep -q "@tarquinen/opencode-dcp" tui.json && echo "project tui.json DCP ✓"
+grep -q "@tarquinen/opencode-dcp" ~/.config/opencode/opencode.json && echo "global opencode.json DCP ✓"
+grep -q "@tarquinen/opencode-dcp" ~/.config/opencode/tui.json && echo "global tui.json DCP ✓"
+```
+
+### DCP configuration (dcp.jsonc)
+
+DCP uses its own config file, searched in order (project overrides global). Restart OpenCode after changes:
+
+1. Global: `~/.config/opencode/dcp.jsonc` (created automatically on first run)
+2. Project: `.opencode/dcp.jsonc` in your project's `.opencode` directory
+
+Defaults are applied automatically (enabled, autoUpdate, pruneNotification detailed, compress range mode with min 50k / max 100k, deduplication + purgeErrors on). If you use small-context models, lower `compress.minContextLimit` / `maxContextLimit` to match.
+
+### DCP commands
+
+- `/dcp` — opens the DCP panel with context, stats, manual-mode controls
+- `/dcp-compress [focus]` — one compression pass, optional focus text
+
+> **Upstream note:** DCP development has slowed; new context-management work moved to `sleev` (`npm i -g sleev`). DCP remains available for OpenCode plugin users. If starting fresh and Sleev fits, prefer it; otherwise DCP stays supported here.
+
+---
+
 ## 8. Clean Up Temporary Clone
 
 Remove the cloned repository from `/tmp/`:
@@ -323,6 +361,8 @@ After completing all steps, verify:
 - [ ] `~/.config/opencode/agents/cognitive-executor.md` exists
 - [ ] `~/.config/opencode/agents/cognitive-discovery.md` exists
 - [ ] `~/.config/opencode/opencode.json` exists with **absolute paths** (not `~` or relative paths) and 5 `mcp` entries (`custom_context`, `project_memory`, `lint`, `blowsh`, `telegram`) + `blowsh_*`/`telegram_*` permissions, no former browser entry
+- [ ] `~/.config/opencode/opencode.json` + `tui.json` `plugin` arrays contain both `@prevalentware/opencode-goal-plugin` and `@tarquinen/opencode-dcp` (`grep -q "@tarquinen/opencode-dcp" ~/.config/opencode/opencode.json && grep -q "@tarquinen/opencode-dcp" ~/.config/opencode/tui.json`); project `opencode.json` + `tui.json` match (`diff -q tui.json ~/.config/opencode/tui.json`)
+- [ ] DCP loads: `opencode plugin list` shows `@tarquinen/opencode-dcp`, `/dcp` panel opens, `~/.config/opencode/dcp.jsonc` created on first run (project `.opencode/dcp.jsonc` overrides if present)
 - [ ] `~/.config/opencode/opencode.json` `blowsh` uses `docker run --rm -i ghcr.io/mokhtarabadi/blowsh-mcp:latest` (120s timeout) and `telegram` uses `uv --directory $HOME/.config/opencode/mcp-telegram-server run main.py` with allowed roots (`/tmp/telegram-mcp` + config dir downloads)
 - [ ] `~/.config/opencode/opencode-shell-strategy.md` exists (instructions file referenced by the `instructions` key)
 - [ ] `/tmp/cognitive-lead-hq` no longer exists
diff --git a/opencode.json b/opencode.json
index 763ee48..8e5bab9 100644
--- a/opencode.json
+++ b/opencode.json
@@ -2,7 +2,10 @@
   "$schema": "https://opencode.ai/config.json",
   "default_agent": "cognitive-executor",
   "instructions": ["docs/opencode-shell-strategy.md"],
-  "plugin": ["@prevalentware/opencode-goal-plugin"],
+  "plugin": [
+    "@prevalentware/opencode-goal-plugin",
+    "@tarquinen/opencode-dcp@latest"
+  ],
   "mcp": {
     "custom_context": {
       "type": "local",
diff --git a/tui.json b/tui.json
index d40e200..f558fc4 100644
--- a/tui.json
+++ b/tui.json
@@ -1,3 +1,6 @@
 {
-  "plugin": ["@prevalentware/opencode-goal-plugin"]
+  "plugin": [
+    "@prevalentware/opencode-goal-plugin",
+    "@tarquinen/opencode-dcp@latest"
+  ]
 }
```
<!-- END_GIT_DIFF -->
