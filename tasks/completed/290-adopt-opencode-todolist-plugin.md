# Task 290: Adopt opencode-todolist plugin

**File:** `tasks/qa/290-adopt-opencode-todolist-plugin.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Goal

Restore the V1 todo steps list in OpenCode V2 by adopting the `opencode-todolist` plugin globally and documenting it in every place the platform lists plugins.

## Manager's Notes

Manager order (verbatim): "create a task and add - opencode-todolist, add it everyplace, all docs in our project. and install globally and tell me restart opencode then smoke test". Scope: global install (`opencode plugin add opencode-todolist` + TUI strip via `cli.json`), HQ docs sync (`README.md`, `LLM.txt`), CHANGELOG entry, then Manager restarts OpenCode and Hands smoke-tests `todowrite`/`todoread` + sidebar.

## Local TODOs

- [x] Install `opencode-todolist` globally and enable the TUI sidebar strip via `cli.json`
- [x] Update `README.md` OpenCode Plugins section (one plugin -> two plugins)
- [x] Update `LLM.txt` Step 7 JSON, Step 7.7 Plugins, and stale no-plugins checklist
- [x] Update `CHANGELOG.md` via Parse-Then-Append
- [x] Run verification gate and record evidence

## Acceptance Criteria

- [x] Global `opencode.json` `plugins` includes `smart-compact` and `opencode-todolist`
- [x] Global `cli.json` `plugins` includes `opencode-todolist` for the sidebar strip
- [x] `README.md` and `LLM.txt` document both plugins with install commands
- [x] No doc still claims the platform uses one plugin or no plugins
- [ ] `opencode plugin list` shows the todolist entry after restart (or install recorded pre-restart)

## Verification Evidence

- **Test command:** rtk test uv run --with-requirements /tmp/opencode/clh-test-reqs.txt pytest tests/test_prompt_sync.py -q
- **Expected result:** pass, exit code 0
- **Actual result:** `13 passed in 0.08s` plus `docs-sync: OK` from `python3 scripts/check_docs_sync.py`
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** plugin loads only after OpenCode restart; pre-restart `plugin list` may not show it.
- **Rollback plan:** `opencode plugin remove opencode-todolist`, drop the `cli.json` entry, revert doc hunks.

---

## Execution Log & Reasoning

**Plan verdict:** Manager's explicit order is the plan (create task + document everywhere + install globally + restart + smoke test). **Brainstorm:** not required — single concern, reversible config + docs. **Seat Check:** domains = OpenCode config/docs → requested: Software Architect; skipped seats N/A (Lite path, 2-line check).

**Gatekeeper:** no rule violation — global plugin install + docs sync matches Tasks 287/288 precedent; repo `opencode.json` untouched (global-only `plugins`/`cli.json` per opencode-init contract); ZAC holds (no commit by Hands).

**Changes:** `opencode plugin add opencode-todolist` exit 0 — global `opencode.json` `plugins` now `[smart-compact, opencode-todolist]`; `~/.config/opencode/cli.json` `plugins` now `[opencode-todolist]` for the sidebar strip. `README.md` one plugin → two plugins. `LLM.txt` Step 7 JSON + description, Step 7.7 (todolist install + `cli.json` strip + restart smoke test), stale no-plugins checklist corrected. `CHANGELOG.md` Unreleased/Added entry.

**Verification:** `python3 scripts/check_docs_sync.py` → `docs-sync: OK`; `rtk test ... pytest tests/test_prompt_sync.py -q` → `13 passed`, exit 0. `git status` shows `README.md`, `LLM.txt`, `CHANGELOG.md` modified plus the new task file.

**Pending (needs Manager):** restart OpenCode to load the plugin, then live smoke test — ask agent for a todo list (`todowrite`), read it back (`todoread`), confirm the TUI sidebar strip. AC5 stays open until then.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 966808f..2af9bc0 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -10,6 +10,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Brain context-sufficiency pack (Task 285):** the Brain planned against a five-file documentation bundle only, with no repository structure, so it either guessed or burned a discovery round just to aim its context request. `mcp-brain-bridge/server.py` now auto-appends the newest generated `.gitignore`-aware tree report (`context-reports/tree_report_*.md`, written by the Hands via `custom_context.create_tree_report`) to that bundle under a labeled section, bounded by a new `_STRUCTURAL_FILE_CAP` (40000) and the shared `_BUNDLE_TOTAL_CAP` with honest `[truncated]`/`[skipped: bundle total cap]` markers. The section appears only when a report exists, so every workspace and test without one is byte-unchanged. New pure helpers `_latest_report_path` (newest by mtime, then name; accepts a `Path` or a `str` root) and `_build_structural_pack` (never raises) do the work, and `_build_context_bundle` appends the pack last so the stable doc files keep their prefix positions. Hardened after the QA hotfix round: a report that resolves outside the workspace root (symlink escape) is skipped rather than read, a zero-byte/whitespace report counts as no grounding, the read is capped at `_STRUCTURAL_FILE_CAP` chars so an oversized report is never slurped whole, and triple backticks are neutralized with an invisible break so report fences cannot close a surrounding fence. A second pure helper, `context_sufficiency_gaps(stage, user_prompt, bundle_text, bundle_included)`, plus a `plan`-stage-only stderr diagnostic makes a blind plan observable instead of silent — non-blocking by design (no `status`/`xml_blocks` change), so no caller behavior shifts. The diagnostic reads the FINAL rendered bundle and the combined prompt including any pinned fed-context block, and it suppresses the structural demand when the caller opted out of the bundle — closing two false-positive paths found in QA. A second QA finding (round 2) was also fixed: a pack dropped for the total cap now appends `[structural pack skipped: bundle total cap]` with NO grounding marker, so a skipped pack correctly counts as absent instead of falsely reading as grounded. 21 new regression tests cover pack selection, truncation, bundle integration, string-root normalization, symlink-escape skip, empty-report handling, fence escaping, the skip-counts-as-absent case, the pure gap checker, and the stderr wiring. Bridge suite: **272 passed** (251 pre-existing + 21 new).
 
+- **Adopted opencode-todolist plugin (Task 290):** OpenCode V2 removed the built-in `todowrite`/`todoread` session todo tools that powered the V1 sidebar, so the platform now runs `opencode-todolist` alongside `smart-compact`. Global install via `opencode plugin add opencode-todolist` (`plugins` now carries both entries) plus the TUI sidebar strip via `plugins` in `~/.config/opencode/cli.json`. HQ docs synced in every place plugins are listed: `README.md` (one plugin -> two plugins), `LLM.txt` (Step 7 JSON + description, Step 7.7 install + `cli.json` strip + restart smoke test, stale no-plugins checklist corrected). Restart OpenCode to load it, then smoke-test `todowrite`/`todoread` and the sidebar strip.
+
 ### Fixed
 
 - **Context MCP singleton report write path (Task 286):** after the singleton migration the context server runs from `~/.config/opencode/mcp-context-server`, but `create_tree_report`, `read_source_files`, and `extract_signatures` wrote their reports to `Path("context-reports")` — the process cwd — so generated maps landed in the global install dir and the project's `context-reports/` went stale (the newest repo tree report stayed at 2026-09-18, still listing the removed `stacks/` directory; found by the task 285 smoke test). All three writers now resolve `report_dir = workspace_root / "context-reports"` from the per-call `project_root` argument the caller supplies, and the `.gitignore` safeguard writes to `<project_root>/.gitignore` via a new `_ensure_context_reports_ignored(workspace_root)` parameter. `extract_signatures`'s regex fallback also reads the resolved `path` instead of the cwd-relative `file_path`. The project_root-omitted path is unchanged (cwd fallback, still surfaced client-visibly), and a new regression test proves a foreign cwd writes nothing outside `<project_root>/context-reports/`. Context-server suite: **70 passed** (69 pre-existing + 1 new).
diff --git a/LLM.txt b/LLM.txt
index e3fa2d9..66356ff 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -284,7 +284,8 @@ Write the following JSON (replace `$HOME` with the actual home directory path on
     }
   },
   "plugins": [
-    "github:mokhtarabadi/opencode-smart-compact"
+    "github:mokhtarabadi/opencode-smart-compact",
+    "opencode-todolist"
   ],
   "compaction": {
     "auto": true,
@@ -295,14 +296,19 @@ Write the following JSON (replace `$HOME` with the actual home directory path on
 }
 ```
 
-The `plugins` entry loads **`smart-compact`** (install it with `opencode plugin add github:mokhtarabadi/opencode-smart-compact` — Step 7.7). The `compaction` block keeps OpenCode's native auto-compaction on as the safety net while retaining a larger recent tail; Smart Compact then provides the manual high-fidelity layer. The terminal client config `~/.config/opencode/cli.json` is V2-native (no project `cli.json`, no `tui.json`):
+The `plugins` entry loads **`smart-compact`** (install it with `opencode plugin add github:mokhtarabadi/opencode-smart-compact` — Step 7.7) plus **`opencode-todolist`** (install it with `opencode plugin add opencode-todolist` — Step 7.7, restores V1 `todowrite`/`todoread` plus the TUI sidebar strip). The `compaction` block keeps OpenCode's native auto-compaction on as the safety net while retaining a larger recent tail; Smart Compact then provides the manual high-fidelity layer. The terminal client config `~/.config/opencode/cli.json` is V2-native (no project `cli.json`, no `tui.json`):
 
 ```json
 {
-  "$schema": "https://opencode.ai/v2/cli.json"
+  "$schema": "https://opencode.ai/v2/cli.json",
+  "plugins": [
+    "opencode-todolist"
+  ]
 }
 ```
 
+The `cli.json` `plugins` entry enables the todolist TUI sidebar strip.
+
 **Important:** Replace `$HOME` with the actual absolute path resolved in Step 3 (e.g., `/home/alice` or `/Users/alice`). This is critical — MCP servers will NOT work with relative paths or `~` in the global config because OpenCode may be invoked from any working directory.
 
 **Launch form + credentials:** no session spawns servers anymore — the 7 singletons run as supervised services on `127.0.0.1:8101-8107` (started in Step 7.5, full map in `docs/services.md`), and the config above only points at them via `type: "remote"`. The old per-session stdio storm (and its `mcp connect failed: Request timed out` failures, ~200/day before the 2026-09-29 singleton fix) is gone by construction. The brain/decision timeouts stay 600000ms (10 min) — LLM turns need it. Credentials (`BRAIN_*`, `DECISION_*`, `TELEGRAM_*`) are **not** in the OpenCode config: each server self-loads `.env` at import, in order `<server-dir>/.env` → `<server-dir>/../.env` → `<cwd>/.env`, never overriding real process env. For the global install that effective file is **`~/.config/opencode/.env`** (seeded in Step 5, `chmod 600`); for servers run straight from the repo it is the repo-root `.env`. The systemd/launchd/Windows units therefore need **no** `EnvironmentFile=` for these keys. Telegram prerequisites (clone + `uv sync` + `.env` + allowed-root dirs) are still installed per §7.6 — only the launch moved into the `mcp-telegram` service.
@@ -400,17 +406,32 @@ Telemetry-free cache/SSRF defaults (`CACHE_TTL_MS=300000`, `ALLOW_PRIVATE_URLS=f
 
 ## 7.7. Plugins
 
-Install the one platform plugin — **`smart-compact`** (`@mokhtarabadi/opencode-smart-compact`, lossless V2-native context compaction, maintained in its own repo):
+Install the two platform plugins — **`smart-compact`** (`@mokhtarabadi/opencode-smart-compact`, lossless V2-native context compaction, maintained in its own repo) plus **`todolist`** (`opencode-todolist`, restores V1 `todowrite`/`todoread` plus the TUI sidebar strip removed in V2):
 
 ```bash
 # Interim (works now, installs from the pushed repo):
 opencode plugin add github:mokhtarabadi/opencode-smart-compact
 # Once published to npm:
 opencode plugin add @mokhtarabadi/opencode-smart-compact
+# Todo list (npm):
+opencode plugin add opencode-todolist
 ```
 
 This writes the spec into `plugins` in `~/.config/opencode/opencode.json`; OpenCode loads it at startup. `opencode plugin add` accepts npm registry packages or Git specs only — a bare local directory path is rejected, so use the Git spec (or list the directory in `plugins` and restart) while developing. It needs registry access: if the machine's `~/.npmrc` points at a dead proxy, remove the `proxy`/`https-proxy` lines first — direct registry access works and the install otherwise fails with `NPMInstallFailedError`.
 
+Enable the todolist sidebar strip via `~/.config/opencode/cli.json`:
+
+```json
+{
+  "$schema": "https://opencode.ai/v2/cli.json",
+  "plugins": ["opencode-todolist"]
+}
+```
+
+Restart OpenCode after install, then smoke-test: ask the agent to make a todo list (`todowrite`) and read it back (`todoread`); the TUI sidebar shows the live strip.
+
+This writes the spec into `plugins` in `~/.config/opencode/opencode.json`; OpenCode loads it at startup. `opencode plugin add` accepts npm registry packages or Git specs only — a bare local directory path is rejected, so use the Git spec (or list the directory in `plugins` and restart) while developing. It needs registry access: if the machine's `~/.npmrc` points at a dead proxy, remove the `proxy`/`https-proxy` lines first — direct registry access works and the install otherwise fails with `NPMInstallFailedError`.
+
 The V1-era `magic-compact` package does not load on OpenCode V2 (it exports the V1 plugin shape); `smart-compact` is the V2-native replacement, so do not add `magic-compact` to `plugins`.
 
 Native OpenCode compaction stays enabled as the automatic safety net (the `compaction` block in Step 7). Goal tracking still comes from OpenChamber's built-in **Session Goals**. Full guide: [`docs/compaction.md`](docs/compaction.md).
@@ -548,8 +569,8 @@ After completing all steps, verify:
 - [ ] `~/.config/opencode/agents/cognitive-executor.md` exists
 - [ ] `~/.config/opencode/agents/cognitive-discovery.md` exists
 - [ ] `~/.config/opencode/opencode.json` exists with **absolute paths** (not `~` or relative paths) and 6 `mcp` entries (`custom_context`, `project_memory`, `lint`, `brain`, `blowsh`, `telegram`) + `blowsh_*`/`telegram_*`/`brain_turn` permissions, no former browser entry
-- [ ] repo `opencode.json`, global `opencode.json`, and global `cli.json` carry **no `plugins` entries** (this platform uses no OpenCode plugins)
-- [ ] `opencode plugin list` shows no goal/dcp entries
+- [ ] `~/.config/opencode/opencode.json` `plugins` carries `smart-compact` plus `opencode-todolist`, and `~/.config/opencode/cli.json` `plugins` carries `opencode-todolist` for the sidebar strip
+- [ ] `opencode plugin list` shows smart-compact and todolist entries (after restart)
 - [ ] worktrees: OpenChamber native via sidebar/dialog (`https://docs.openchamber.dev/worktrees/`) — no plugin required
 - [ ] (optional) OpenChamber: if installed, `npm list -g @openchamber/web` shows 2.x, `openchamber status` password:yes, `openchamber startup status` shows enabled+active+lingering, `docs/openchamber.md` present; if not requested, this check is N/A
 - [ ] `~/.config/opencode/opencode.json` all 7 `mcp` entries are `type: "remote"` loopback URLs (8101 lint, 8102 context, 8103 memory, 8104 decisions, 8105 brain, 8106 telegram timeout 30000, 8107 blowsh timeout 120000) served by the supervised singletons — no stdio/`uv run` entries remain
diff --git a/README.md b/README.md
index 16d8f9f..fc48839 100644
--- a/README.md
+++ b/README.md
@@ -481,7 +481,7 @@ opencode --agent cognitive-executor
 
 ### OpenCode Plugins
 
-One plugin: **`smart-compact`** (`@mokhtarabadi/opencode-smart-compact`) — lossless, V2-native context compaction, maintained in its own repo. Native OpenCode V2 compaction stays on as the automatic safety net (`compaction.auto` + `keep.tokens: 20000`); Smart Compact adds the high-fidelity layer: user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool I/O is pruned into a retrievable cache. It never mutates the stored transcript — it stores a per-session compaction state and applies it to the model-visible messages per request. Commands: `/magic-compact [N]`, `/magic-trim [N]`, `/magic-stats`. Install with `opencode plugin add github:mokhtarabadi/opencode-smart-compact` (the Git spec, until it is published to npm); full guide in [`docs/compaction.md`](docs/compaction.md). Goal tracking still comes from OpenChamber's built-in Session Goals.
+Two plugins: **`smart-compact`** (`@mokhtarabadi/opencode-smart-compact`) — lossless, V2-native context compaction, maintained in its own repo. Native OpenCode V2 compaction stays on as the automatic safety net (`compaction.auto` + `keep.tokens: 20000`); Smart Compact adds the high-fidelity layer: user messages stay verbatim, each old assistant turn becomes its own summary, and bulky tool I/O is pruned into a retrievable cache. It never mutates the stored transcript — it stores a per-session compaction state and applies it to the model-visible messages per request. Commands: `/magic-compact [N]`, `/magic-trim [N]`, `/magic-stats`. Install with `opencode plugin add github:mokhtarabadi/opencode-smart-compact` (the Git spec, until it is published to npm); full guide in [`docs/compaction.md`](docs/compaction.md). Plus **`todolist`** (`opencode-todolist`) — restores the V1 session todo tools (`todowrite`/`todoread`) removed in V2, with a live TUI sidebar strip. Install with `opencode plugin add opencode-todolist` and enable the strip via `plugins` in `~/.config/opencode/cli.json`. Goal tracking still comes from OpenChamber's built-in Session Goals.
 
 ---
```
<!-- END_GIT_DIFF -->
