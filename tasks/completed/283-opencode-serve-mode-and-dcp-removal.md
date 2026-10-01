# Task 283: OpenCode V2 + OpenChamber 2 migration, plugin removal, docs audit, global install

**File:** `tasks/completed/283-opencode-serve-mode-and-dcp-removal.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Make the repo and machine follow OpenCode 2 + OpenChamber 2 only: no OpenCode plugins (goal/compress/retry), OpenChamber is the single manager of a single OpenCode instance, docs are correct and orphan-free, and the repo is installed globally per `LLM.txt`.

## Manager's Notes

Manager orders (verbatim, chronological):

1. "we need opencde in serve mode not in service mode. update repo and globally and restart. opnechmaber always yse exisiting opencode never run any instance. remove compress plugin locally and globaly. create a task for them and all other exitiing working changes."
2. "read latest opencoe 2 docs makesure we use everyting correctly. even audit entire project and system prompt for opencode 2"
3. "now read opencode v2 docs and read openchamber 2 docs and upgrade them to latest version globally and in repo. after that cleanup our repo docs. remoe tailscale and goal plugin everything refrneed to goal plugin must be removed then arhcive our retry plugin and remove it from entire project. make sure every picse of project only follow opencode and openchamber version 2 docs and no goal plugin and compress plugin and the retry plugin archived. use tools to make sure see all things in repo. then clean old and wrong docs. then we need only manage openchamber and openchamber itself manage opencode for us."
4. "audit project find docs orphaned , wrong, lefover and clean all, now we don't use pluigs at all so remove everything from about them entire project. cleanup md files. lefovers."
5. "now follow llm.txt and install and setup our repo globally."
6. "i called you from openchamber, verify everything, make sure all things handled by openchamber one instance of opencode and it started via openchamber"
7. "did you remeber old tlegrm mcp .env can you find it?" / "enable it mean telegram"

Scope delivered: (1) single OpenChamber-managed OpenCode instance (background service disabled, no custom `opencode-server.service`); (2) zero OpenCode plugins (goal, DCP/compress, retry) — retry plugin archived; (3) OpenCode 2 / OpenChamber 2 docs audit + rewrite (`docs/openchamber.md`, no Tailscale, no plugin content); (4) orphan/leftover cleanup; (5) global install per `LLM.txt` including Telegram credential recovery from the 2026-09-29 backup.

## Local TODOs

- [x] Brain planning round under this task_id
- [x] Fetch latest OpenCode 2 + OpenChamber 2 docs as ground truth
- [x] Audit entire project + system prompt for OpenCode 2 conformance; fix deviations
- [x] Remove all OpenCode plugins (goal, DCP/compress); archive the retry plugin
- [x] Remove Tailscale content; rewrite `docs/openchamber-tailscale.md` → `docs/openchamber.md`
- [x] Clean orphaned/wrong docs + leftovers (scripts, plugin-SDK dirs, caches, backups)
- [x] Make OpenChamber the single manager: one OpenCode instance, started by `openchamber.service`
- [x] Follow `LLM.txt`: install repo globally (servers, skills, agents, prompt, `.env`, units, blowsh)
- [x] Recover + enable Telegram MCP from the old `.env` backup; verify both accounts
- [x] Restart all units, verify versions/plugins/MCP list

## Acceptance Criteria

- [x] Exactly one OpenCode instance running, started by `openchamber.service` (no background shared service, no custom `opencode-server.service`)
- [x] Zero OpenCode plugins in repo/global/cli configs; `opencode plugin list` shows none; goal + DCP/compress references absent from live files
- [x] Retry plugin archived at `archive/rate-limit-rescue/` and referenced by no config
- [x] Docs aligned to V2: `docs/openchamber.md` present (Tailscale removed), plugin content removed, `.env` self-load contract documented
- [x] Orphans/leftovers removed (`scripts/fetch-opencode-docs.py`, `scripts/repomd`, `docs/velocity.md`, plugin-SDK dirs, caches, backups)
- [x] Global install done per `LLM.txt`; 7 MCP servers connected (context, memory, lint, decision, brain, blowsh, telegram)
- [x] Telegram enabled and verified end-to-end (both work + personal accounts)

## Verification Evidence

- **Test command:** rtk test uv run --no-project --with pytest python -m pytest tests/test_skill_registry.py -q
- **Expected result:** docs-sync OK; registry tests pass; versions/reporting green; single OpenChamber-managed OpenCode instance; 7 MCP connected
- **Actual result:**
  - `python3 scripts/check_docs_sync.py` → `docs-sync: OK` (exit 0)
  - `rtk test ... pytest tests/test_skill_registry.py -q` → 20 passed (exit 0)
  - `opencode --version` → v2.0.21 ; `openchamber --version` → 2.1.0 ; `opencode plugin list` → "No plugins found"
  - `ps` opencode count = 1 (`serve --hostname 127.0.0.1 --port 35649`, parent = openchamber node, ownerPid in `managed-opencode/*.json`)
  - `opencode service status` → stopped; `~/.config/opencode/service.json` → `disabled: true`
  - `opencode mcp list` → blowsh/brain/custom_context/lint/manager_decisions/project_memory/telegram all connected
  - `telegram_get_me` → work (@m_mokhtari_developer) + personal (@mokhtarabadi1997)
  - full suite has 2 pre-existing failures (proven on stashed clean tree; not regressions)
  - orphan/leftover reference proof: `grep -rn "fetch-opencode-docs|repomd|velocity.md"` in live files → no importers; `git ls-files` no longer lists them
  - plugin-absence proof: `grep -rn "goal-plugin|opencode-dcp|prevalentware|tarquinen|rate-limit-rescue"` over live files → no hits (only intentional "no plugins" statements)
  - single-instance proof: `ps -eo pid,args | grep -c 'opencode serve'` = 1; parent chain → openchamber node; `managed-opencode/*.json` ownerPid match
  - restart survival: `systemctl --user restart openchamber` → managed OpenCode respawned automatically, UI 200, MCP reconnected
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** disabling the background service could drop a session hosted on it; global config edits could break CLI; Telegram credentials are sensitive; two OpenCode servers on one DB can lock.
- **Rollback plan:** restore `*.bak-*` backups (repo configs, global `opencode.json`/`cli.json`/`.env`); `opencode service unset disabled` to re-enable the shared service; remove `archive/rate-limit-rescue/` restore path; `openchamber startup disable` to remove the OpenChamber service; delete `/tmp/opencode/telegram-backup-*` if unintended.

---

## Execution Log & Reasoning

**Turn 1 — V2 config migration + rate-limit change.**
- `plugins/rate-limit-rescue`: `RETRY_DELAY_MS` 30_000 → 2_000 (+ tests/README/package description). Verified `node --test` 11/11.
- Repo/global configs moved to V2-native: `plugins`, `permission.shell`, `mcp.servers` (disabled + `timeout{catalog,execution}`); deleted repo + global `tui.json`; verified JSON + `opencode mcp list` 7/7.

**Turn 2 — serve-mode vs service-mode attempt (superseded).**
- Investigated `opencode service`/`serve`; set `~/.config/opencode/service.json` `disabled:true`. The background service (`:49374`) could not be stopped while this session was hosted on it — each stop dropped the transport. Later superseded by the OpenChamber-managed approach.

**Turn 3 — state divergence (external actor).**
- At 11:41-11:42 both `openchamber.service` and `opencode-server.service` were stopped, their `.d/` drop-ins deleted, and units masked to `/dev/null` by an external actor. Recorded; later rebuilt.

**Turn 4 — V2 docs audit + full plugin removal + docs rewrite.**
- Fetched current OpenCode V2 + OpenChamber 2 docs (config, MCP, plugins, agent/CLI, service/serve, migrate-v1, OpenChamber install/environment/opencode-server/updates).
- Removed every goal-plugin + DCP reference from repo/global configs, README, `LLM.txt`, docs, agents, memory. Archived retry plugin: `plugins/rate-limit-rescue/` → `archive/rate-limit-rescue/` (node_modules dropped).
- Rewrote `docs/openchamber-tailscale.md` → `docs/openchamber.md` (managed OpenCode, `openchamber startup enable` boot, remote access, env vars). Removed Tailscale everywhere.
- Deleted 3 stale memory shards; refreshed V2/password memories + `index.md`.
- Pruned repo `.bak-*`, `.opencode/goals/`, `.gitignore` goal guard.

**Turn 5 — docs/leftover audit + env-contract fixes.**
- Removed orphaned `scripts/fetch-opencode-docs.py`, `scripts/repomd`, `docs/velocity.md`; deleted plugin-SDK leftovers (`.opencode/{package.json,package-lock.json,node_modules,commands}`) and `.pytest_cache/`.
- **Real install bugs fixed in `LLM.txt` §4–§5:** the global install now copies **all** server modules (brain-bridge siblings + `mcp-decision-server` — previously 4 single `server.py` files, decision-server never installed) and creates the repo `.env` then `install -m 600` seeds `~/.config/opencode/.env`.
- Documented the `.env` self-load contract (`<server-dir>/.env` → `<server-dir>/../.env` → `<cwd>/.env`; global = `~/.config/opencode/.env`) across `LLM.txt`, `docs/services.md` (new Credentials section + launchd/Windows notes), `docs/setup.md`, `docs/telegram-setup.md`, `docs/brain-bridge.md`; fixed `DECISION_REPO_PATH` guidance (self-loaded, no `{env:}` block). Proven live with a temp-dir loader probe.
- Slimmed `audit-agents` runtime-state rule (no plugin wording).
- Installed the **OpenChamber-managed service** (`openchamber startup enable --port 3005 --host 127.0.0.1`).

**Turn 6 — OpenChamber data cleanup.**
- Removed stale provider leftovers from `~/.config/openchamber/settings.json` + `preferences.json`: 385 `hiddenModels` + `favoriteModels`/`recentModels`/`recentEfforts` OpenRouter entries and the retired `zen-proxy` provider (404 → 0 refs each); removed `startup.env.bak-20260926`; restarted + verified.

**Turn 7 — global install per `LLM.txt`.**
- Copied all server modules + `mcp-common` + `system-prompt.md` + `opencode-shell-strategy.md` + 36 skills + 2 agents to `~/.config/opencode/`; `uv sync` per server; seeded `~/.config/opencode/.env` (chmod 600); wrote global `opencode.json` (default_agent + instructions + `mcp.servers` ×7 + permissions) and schema-only `cli.json`.
- Installed `services/mcp-*.service` → `~/.config/systemd/user/`; enabled + started lint/context/memory/decision/brain; pulled + ran `blowsh-singleton` (Docker `:8107`).
- Telegram: cloned upstream + `uv sync`; upstream now hard-requires `TELEGRAM_API_ID` at import → disabled pending credentials.

**Turn 8 — single OpenChamber-managed instance.**
- Confirmed this session's shell ancestry → `opencode serve --port 35649` → `openchamber.service` (ownerPid match in `managed-opencode/*.json`).
- Stopped the duplicate background service (`serve --service`, `:49374`) and set `service.json` `disabled:true`. Verified `ps` opencode count = 1.

**Turn 9 — Telegram credential recovery + enable.**
- Found the old Telegram MCP `.env` at `/tmp/opencode/telegram-backup-20260929-070816/.env` (API_ID/HASH + work/personal session strings + session lock).
- Appended the 5 `TELEGRAM_*` keys to `~/.config/opencode/.env` (chmod 600); re-enabled + started `mcp-telegram`; flipped `telegram` to `disabled:false` in global `opencode.json`; the managed instance hot-reloaded it.
- Verified: unit enabled+active, `:8106` listening, `telegram_get_me` returns both accounts.
- Security: deleted 6 leftover shell-output logs under `~/.local/share/opencode/shell/` that contained the session strings in plaintext.

**Intentional residuals (recorded, not defects):**
- `docs/workflow-upgrade-v8.4.5.md` kept — a regression test (`tests/test_mcp_servers.py`) requires it.
- `CHANGELOG.md` historical entries still name the archived retry plugin (history is immutable per repo convention).
- `mcp-common/env.py` docstring updated (persona-server mention removed).
- Telegram upstream requires API credentials; without them the unit cannot start (documented).

## QA Response (round 1 → hotfix)

QA round 1 returned `QA_REJECTED` on a **truncated diff (part 1/2, 102130/157568 chars)** — the reviewer explicitly could not see part 2. Triage per the bridge protocol (fix what reproduces, dispute the rest with evidence):

- **F1 (V2, real → FIXED):** blowsh timeout had been reduced 120000 → 30000. Restored to **120000** in the `LLM.txt` §7 example + prose and in the live global `~/.config/opencode/opencode.json` (managed instance reloaded). The TODO/checklist already said 120000, so this removes the inconsistency.
- **F2 (V1, disputed with evidence):** the `30_000 → 2_000` retry-delay change in `archive/rate-limit-rescue/index.js` was an explicit Manager order ("set 30 to 2 in repo and globally"). The plugin is **archived** (`archive/rate-limit-rescue/`) and referenced by no config, so it cannot cause a retry storm — it is not loaded.
- **F3 (V3, resolved):** the Goal, Scope, TODOs, AC and this Execution Log were rewritten to the actual delivered state (single OpenChamber-managed instance, zero plugins, docs audit, global install). The "fixed :4096 external unit" wording no longer exists.
- **F4 (V4/V5, evidence added):** grep proofs and live proofs added to Verification Evidence (orphan importers, plugin absence, single-instance, restart survival).
- **F5 (M4, transport):** the diff exceeded the bridge attachment budget and was auto-split; re-QA should carry the full diff or judge part 2 explicitly.

Re-QA requested with the complete diff.

## QA Response (round 2 → hotfix)

QA round 2 (`QA_REJECTED`) confirmed F1/F2 from round 1 and raised install-block findings. All addressed:

- **V1 (real → FIXED):** `LLM.txt` §5 `cp -r …/mcp-common ~/.config/opencode/mcp-common` could nest into `mcp-common/mcp-common` because the mkdir loop pre-creates the dir. Changed to `cp -a …/mcp-common/. ~/.config/opencode/mcp-common/`. **Proven** in a temp simulation: destination contains `src/` + `pyproject.toml`, no nested `mcp-common/`.
- **V2 (real → FIXED):** §5 seeded the global `.env` with `install -m 600` unconditionally, clobbering a live file. Now: abort when the source still equals `.env.example` (placeholders), and back up an existing `~/.config/opencode/.env` to `.env.bak-<ts>` before writing. **Proven** in the same simulation: placeholder source → seed skipped, live `.env` intact.
- **V3 (→ FIXED):** `CHANGELOG.md` now carries an entry for the archive move + the Manager-ordered `30_000 → 2_000` retry change (archived, inert).
- **V4 (→ FIXED):** restored the `.opencode/goals/`, `.opencode/worktrees/`, `.opencode/worktree-sessions.json` `.gitignore` guards so any recreated runtime state stays uncommittable.
- **V5 (→ evidenced):** `docs/openchamber.md` exists and is the replacement for the deleted `docs/openchamber-tailscale.md`; `docs/openchamber.md` §3 uses the documented `openchamber --ui-password`/`openchamber startup enable` flow.
- **M1/M3 (→ evidenced):** negative greps recorded (zero goal-plugin/DCP/tui.json/SKIP_START refs in live files); `check_docs_sync.py` → OK after the doc rename.
- **M2 (→ evidenced):** the §5 copy/seed block dry-run above.
- **M4 (transport):** the diff exceeds the bridge attachment budget and is auto-split; round 3 should judge the full diff.

## Code Review Response (round 1 → hotfix)

Reviewer returned `APPROVED_WITH_CHANGES` (F1–F4). Triage:

- **F1 (disputed — stale):** the AC no longer references a fixed `:4096` unit. Live task lines 41–47 state "Exactly one OpenCode instance running, started by `openchamber.service`". The reviewer read the pre-rewrite AC from an older diff hunk; the live file is managed-mode correct.
- **F2 (real → FIXED):** `CHANGELOG.md` [Unreleased] had duplicate `### Added` / `### Fixed` headers. Merged into single `### Added` / `### Changed` / `### Fixed` sections (4 / 2 / 4 items), Parse-Then-Append satisfied.
- **F3 (real → FIXED):** `.opencode/memory/workflows/global-install-upgrade.md` decision-server list now reads `server, redactor, detector` (matches `LLM.txt` §5).
- **F4 (transport):** part 2 of the diff is unverified by the reviewer only because the bridge auto-splits large diffs; the same full diff is what QA round 3 judged.

## Code Review Response (round 2 → hotfix)

Reviewer round 2 returned `REJECTED_NEEDS_FIXES` with one **real, High** blocker it caught from the diff (`@@ -9,1381 +9,20 @@`):

- **F2 (real → FIXED):** the CHANGELOG merge script truncated history (kept head + a fragment). Restored `CHANGELOG.md` from the pre-merge backup (1396 lines) and redid the merge **correctly** (regex tail now preserves everything from the next `## [` header to EOF). Result: 1388 lines, 96 `## [` release sections intact, `## [9.46.0]` present, `[Unreleased]` = single `Added` (4) / `Changed` (2) / `Fixed` (4). `git diff HEAD -- CHANGELOG.md` = 8+/9- (clean merge, no history loss).
- **F1/F3/F4 (no action):** reviewer agreed F1 was unverifiable/stale, F3 verified, F4 truncation-only.

## Review Verdict

- QA round 3: `VERDICT: QA_PASSED`.
- Code Review round 3: **APPROVED** → `PO_REVIEW_PENDING` (`CHANGELOG.md` hunk now `@@ -8,22 +8,23 @@`, no truncation; no blocker remains).
- Awaiting the Manager's closure word ("Approved for closure" / "Close task"). File stays in `tasks/qa/`.
- **Manager closure approval (verbatim): "Approved for closure".** Moved to `tasks/completed/`, status `closed`, committed via `custom_context_commit_and_clean_task`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.gitignore b/.gitignore
index 06927e3..2b9d975 100644
--- a/.gitignore
+++ b/.gitignore
@@ -42,14 +42,12 @@ context-reports/
 # Telegram Downloads
 downloads/
 
-# Goal plugin state (per-project)
+# OpenCode runtime state (goal/session/worktree dirs if a tool recreates them)
 .opencode/goals/
-
-# worktree state (owt removed 2026-09-08 — keep guards if owt reinstalled; OpenChamber worktrees are SDK-managed)
-.opencode/worktrees/
 .opencode/worktree-sessions.json
+.opencode/worktrees/
 
-# Persona session transcripts (runtime audit trail, never committed)
+# Tracked task transcripts (runtime audit trail for Brain sessions)
 tasks/.sessions/
 
 # Python/pytest runtime caches (never committed)
diff --git a/.opencode/memory/index.md b/.opencode/memory/index.md
index 25816bc..83ea10f 100644
--- a/.opencode/memory/index.md
+++ b/.opencode/memory/index.md
@@ -10,11 +10,8 @@
 | manager | full_automatic_mode | STANDING ORDER — FULL AUTOMATIC MODE. Manager has no session access and cannot be paged. Zero questions, zero clarifi... |  |
 | manager-decisions | autopilot_consult_all_personas | Session 2026-09-14 (tasks 230+231 closure): the Manager ordered that in autopilot the Hands must consult ALL Brain pe... |  |
 | manager-decisions | task_closure_protocol_one_by_one | Session 2026-09-14: task closure protocol ordered by the Manager — close tasks ONE BY ONE (verify, git mv to tasks/co... |  |
-| opencode_config | global_goal_plugin_upgrade_2026_08_27 | # Global Goal Plugin Upgrade — 2026-08-27 |  |
-| opencode_config | opencode_v2_upgrade_2026_09_26 | # OpenCode V2 Upgrade — 2026-09-26 |  |
-| opencode_config | plugin_policy_dcp_only_2026_09_08 | 2026-09-08 (Task 165): goal plugin (@prevalentware/opencode-goal-plugin) removed from all 4 opencode configs (global ... |  |
-| opencode_config | plugins_full_v2_status_2026_09_26 | # Plugins full-V2 status — verified 2026-09-26 (Task 274, opencode 2.0.18) |  |
-| opencode_config | v2_server_password_sync_2026_09_26 | # V2 Server-Password Sync (OpenChamber external mode) — 2026-09-26 |  |
+| opencode_config | opencode_v2_upgrade_2026_09_26 | # OpenCode V2 Upgrade — 2026-09-26 (state refreshed 2026-10-01) |  |
+| opencode_config | v2_server_password_sync_2026_09_26 | # V2 server auth — managed mode only (updated 2026-10-01) |  |
 | project | absent-file-policy | Absent-File Policy: If a referenced core file does not exist (e.g., DESIGN.md, docs/architecture.md, docs/data_model.... |  |
 | project | fragment-edit-regenerate-workflow | # Fragment-Edit → Regenerate Workflow (Task 129, 2026-08-30) |  |
 | project | mcp_tool_audit_2026_09_18 | MCP tool audit 2026-09-18: 28 tools across 5 servers. Strong: decision-server (WHEN TO CALL on all 6), lint-server (4... |  |
diff --git a/.opencode/memory/opencode_config/global_goal_plugin_upgrade_2026_08_27.md b/.opencode/memory/opencode_config/global_goal_plugin_upgrade_2026_08_27.md
deleted file mode 100644
index f4e8db2..0000000
--- a/.opencode/memory/opencode_config/global_goal_plugin_upgrade_2026_08_27.md
+++ /dev/null
@@ -1,24 +0,0 @@
----
-created_at: '2026-08-27T14:30:55.763872+00:00'
-status: active
-tags: []
-updated_at: '2026-08-27T14:30:55.763893+00:00'
----
-
-# Global Goal Plugin Upgrade — 2026-08-27
-
-## What Changed (2026-08-28 — Re-migrated to @prevalentware/opencode-goal-plugin per Manager directive, supersedes 2026-08-27 willytop8 alignment)
-- **2026-08-28:** Migrated FROM `opencode-goal-plugin` (willytop8, v0.8.2) TO `@prevalentware/opencode-goal-plugin` (v0.1.39) in both global `~/.config/opencode/opencode.json` and project `opencode.json` — `plugin: ["@prevalentware/opencode-goal-plugin"]`.
-- Created `tui.json` parity for OpenCode 1 stable (required by prevalentware docs): `~/.config/opencode/tui.json` and `tui.json` (project root) both `{"plugin":["@prevalentware/opencode-goal-plugin"]}`. OpenCode 1 reads both `opencode.json` + `tui.json`; without `tui.json` the sidebar/palette goal UI does not appear.
-- Deleted corrupted local `.opencode/opencode.json` (`{"plugin":["list"]}`) — stray file created by erroneous `opencode plugin list` run (untracked, `git status` clean after removal). Correct project config is root `opencode.json`.
-- Preserved `command.goal` block (`template: "$ARGUMENTS"`, `agent: "cognitive-executor"`) — still required for `/goal` registration.
-- `.opencode/goals/` remains in `.gitignore`; `audit-agents` skill criterion unchanged.
-
-## Why (2026-08-28)
-Manager explicitly requested full migration to `@prevalentware/opencode-goal-plugin` (https://github.com/prevalentWare/opencode-goal-plugin, npm `https://www.npmjs.com/package/@prevalentware/opencode-goal-plugin`) which follows Codex native goal-mode semantics and includes `@opencode-ai/plugin`, `@opentui/solid`, `effect`, `solid-js`, `zod` (vs willytop8 single-dep). The 2026-08-27 note aligned to willytop8 as “official” — that decision is now superseded. OpenCode 1.18.25 is stable and uses `plugin` + `tui.json` (not `plugins` + `cli.json` which is OpenCode 2 beta). The `tui.json` addition ensures the TUI sidebar/palette integration loads.
-
-## Reference
-- New repo: https://github.com/prevalentWare/opencode-goal-plugin (npm `@prevalentware/opencode-goal-plugin` v0.1.39, 40 versions, 5 deps)
-- Previous repo: https://github.com/willytop8/OpenCode-goal-plugin (npm `opencode-goal-plugin` v0.8.2) — preserved in history `tasks/archive/122`, `docs/history/milestone-15-summary.md`
-- OpenCode version: 1.18.25 stable (uses `plugin` + `tui.json`); OpenCode 2 beta would use `plugins` + `cli.json`
-- Config locations: `opencode.json` + `tui.json` (both project root and `~/.config/opencode/` global)
\ No newline at end of file
diff --git a/.opencode/memory/opencode_config/opencode_v2_upgrade_2026_09_26.md b/.opencode/memory/opencode_config/opencode_v2_upgrade_2026_09_26.md
index 9a88928..c711586 100644
--- a/.opencode/memory/opencode_config/opencode_v2_upgrade_2026_09_26.md
+++ b/.opencode/memory/opencode_config/opencode_v2_upgrade_2026_09_26.md
@@ -2,16 +2,17 @@
 created_at: '2026-09-26T06:28:07.289833+00:00'
 status: active
 tags: []
-updated_at: '2026-09-26T06:28:07.289848+00:00'
+updated_at: '2026-10-01T00:00:00.000000+00:00'
 ---
 
-# OpenCode V2 Upgrade — 2026-09-26
+# OpenCode V2 Upgrade — 2026-09-26 (state refreshed 2026-10-01)
 
-- Global binary upgraded via https://opencode.ai/v2/install to v2.0.18 (verified with opencode --version).
-- Global cli.json uses native V2 shape with $schema https://opencode.ai/v2/cli.json and plugins array (goal-plugin + dcp).
-- Global and project opencode.json keep dual plugin (V1) + plugins (V2) keys, and dual permission.bash + permission.shell denies; V2 normalizes V1 in memory.
-- Project cli.json removed (V2 client config is global-only); project tui.json leftover is harmless.
-- MCP block still V1 shape (enabled:true, no servers wrapper) and permission object shape still V1; both accepted by V2 with warnings, native migration to mcp.servers/disabled and permissions array is optional.
-- V1 to V2 DB migration key migration.v1-v2 reached phase completed after a transient SQLite database-is-locked during sessions phase caused by concurrent serve and CLI writers on 9GB db.
-- OpenChamber 2.0.2 active; opencode-server systemd unit stopped per manager request while manual opencode serve --service still holds the DB.
-- Supersedes: opencode_config/global_goal_plugin_upgrade_2026_08_27 (V1 plugin+tui.json note).
\ No newline at end of file
+- Binary upgraded via https://opencode.ai/v2/install; currently **v2.0.21** (verified with `opencode --version`; the official update endpoint `https://opencode.ai/update/api/latest/cli/npm` reports 2.0.21 as latest — already current).
+- Global `cli.json` uses the native V2 shape: `$schema` https://opencode.ai/v2/cli.json (no plugin entries — the project uses no OpenCode plugins).
+- Global and project `opencode.json` use V2 keys only (`plugins` plural if any, `permission.shell`). No V1 dual keys remain.
+- Project `cli.json` removed (V2 client config is global-only); project `tui.json` deleted.
+- MCP block uses native V2 `mcp.servers` with `disabled:false` + `timeout:{catalog,execution}`.
+- V1→V2 DB migration key `migration.v1-v2` reached phase `completed`.
+- OpenChamber **2.1.0** active (latest on npm).
+- Plugin policy: **no OpenCode plugins** — the goal plugin and DCP/compress plugin were removed 2026-10-01 per Manager order. OpenChamber's built-in Session Goals replace the goal plugin.
+- Supersedes: opencode_config/global_goal_plugin_upgrade_2026_08_27 (deleted), plugin_policy_dcp_only_2026_09_08 (deleted), plugins_full_v2_status_2026_09_26 (deleted).
diff --git a/.opencode/memory/opencode_config/plugin_policy_dcp_only_2026_09_08.md b/.opencode/memory/opencode_config/plugin_policy_dcp_only_2026_09_08.md
deleted file mode 100644
index 559257d..0000000
--- a/.opencode/memory/opencode_config/plugin_policy_dcp_only_2026_09_08.md
+++ /dev/null
@@ -1,8 +0,0 @@
----
-created_at: '2026-09-08T08:42:52.334419+00:00'
-status: active
-tags: []
-updated_at: '2026-09-08T11:15:00+00:00'
----
-
-2026-09-08 (Task 165): goal plugin (@prevalentware/opencode-goal-plugin) removed from all 4 opencode configs (global + repo opencode.json/tui.json → dcp-only) and worktree loader disabled (~/.config/opencode/plugins/worktree-plugin.js → .disabled). 2026-09-08 follow-up: owt fully removed (npm uninstall -g @nano-step/opencode-worktree-plugin + rm plugin + 7 command MDs) — verified OpenChamber 1.22.2 provides native worktrees (docs.openchamber.dev/worktrees + multi-run, UI dialog, isolate runs ≤5, Fusion). Reason: OpenChamber Session Goals + native worktrees replace both plugins; reduce proc/RAM. Re-enable owt only for CLI/headless without OpenChamber: npm install -g @nano-step/opencode-worktree-plugin && owt-setup install (see LLM.txt §7.8). Supersedes Task 126 + Task 164 until Manager says otherwise.
\ No newline at end of file
diff --git a/.opencode/memory/opencode_config/plugins_full_v2_status_2026_09_26.md b/.opencode/memory/opencode_config/plugins_full_v2_status_2026_09_26.md
deleted file mode 100644
index 9858c43..0000000
--- a/.opencode/memory/opencode_config/plugins_full_v2_status_2026_09_26.md
+++ /dev/null
@@ -1,16 +0,0 @@
----
-created_at: '2026-09-26T17:45:00.423109+00:00'
-status: active
-tags: []
-updated_at: '2026-09-26T17:45:00.423238+00:00'
----
-
-# Plugins full-V2 status — verified 2026-09-26 (Task 274, opencode 2.0.18)
-
-Both plugins at latest stable AND both V2-capable upstream. No upgrade work remains.
-
-- goal `@prevalentware/opencode-goal-plugin@0.1.52` (released 2026-09-26; 0.1.50 Sep 21, 0.1.51 Sep 22). V2 port: PR #49 merged 2026-09-14 (beta-19425 contract, compaction context, restart transcript recovery, dual [id,server,setup] shape, V2 lifecycle smoke PASS) + PR #58 merged+released 2026-09-26 (V2 task-recovery scoping). Open issue #54 is a V1-host registration bug whose body confirms setupV2 targets V2 hosts.
-- DCP `@tarquinen/opencode-dcp@3.2.0` (stable 2026-09-20). V2 setup() via session hooks (context, compaction). Betas 3.2.1-3.2.8-beta0 are stale Mar/Apr experiments — stable 3.2.0 is newest. Known gap by design: compress.permission ask throws in V2; keep default allow.
-- Source of truth: `opencode plugin list` (shows 0.1.52 + 3.2.0, zero errors). `~/.cache/opencode/packages/*` is metadata-only (no dist/); V2 host resolves npm at runtime.
-- Upstream-issue policy: search before filing, never duplicate. DCP repo Opencode-DCP/opencode-dynamic-context-pruning has active V2 threads #627/#628/#631/#632 — file nothing there. Goal repo prevalentWare/opencode-goal-plugin.
-- Corrects the earlier (wrong) claim that the goal-plugin server is V1-only — that reading came from a stale cache copy.
\ No newline at end of file
diff --git a/.opencode/memory/opencode_config/v2_server_password_sync_2026_09_26.md b/.opencode/memory/opencode_config/v2_server_password_sync_2026_09_26.md
index 30845ff..04ae2c1 100644
--- a/.opencode/memory/opencode_config/v2_server_password_sync_2026_09_26.md
+++ b/.opencode/memory/opencode_config/v2_server_password_sync_2026_09_26.md
@@ -2,13 +2,13 @@
 created_at: '2026-09-26T06:49:52.094220+00:00'
 status: active
 tags: []
-updated_at: '2026-09-26T06:49:52.095684+00:00'
+updated_at: '2026-10-01T00:00:00.000000+00:00'
 ---
 
-# V2 Server-Password Sync (OpenChamber external mode) — 2026-09-26
+# V2 server auth — managed mode only (updated 2026-10-01)
 
-V2 `opencode serve` mints a random Basic-auth password EVERY boot unless OPENCODE_PASSWORD/OPENCODE_SERVER_PASSWORD is set. External OpenChamber (OPENCODE_HOST + OPENCODE_SKIP_START) authenticates with OPENCODE_SERVER_PASSWORD from its own env. Any mismatch = `OpenCode info endpoint responded with status 401` + PushWatcher upstream_unavailable floods.
+OpenChamber now **manages its own OpenCode server** (managed mode). The old external-server setup is retired: no `opencode-server.service` unit, no `OPENCODE_HOST`, no `OPENCODE_SKIP_START`, so the V2 random-password / 401 sync problem no longer applies — OpenChamber and its managed server share one process tree and one credential automatically.
 
-Fix: one stable password in `~/.config/opencode/.server-password` (chmod 600), pinned on the server via `opencode-server.service.d/10-password.conf`, and as the OPENCODE_SERVER_PASSWORD line in `~/.config/openchamber/startup.env` (EnvironmentFile wins over drop-ins — the startup.env edit is load-bearing). After ANY `openchamber startup enable` (rewrites startup.env), re-apply the line, daemon-reload, restart both (USER action). Verify: zero `status: 401` in openchamber journal + `[PushWatcher] connected`.
+If someone reintroduces external mode (`OPENCODE_HOST` + `OPENCODE_SKIP_START=true`), then: V2 `opencode serve` mints a random Basic-auth password every boot unless `OPENCODE_SERVER_PASSWORD` is set, and the mismatch shows as `OpenCode info endpoint responded with status 401` + `PushWatcher upstream_unavailable`. The fix in that case is one stable password in `~/.config/opencode/.server-password` (chmod 600), pinned on the server unit and mirrored into the client env.
 
-Supersedes: workflows/global-install-upgrade (extends it for V2 external-server auth).
\ No newline at end of file
+Retired with the external unit 2026-10-01 (docs cleanup).
diff --git a/.opencode/memory/project/fragment-edit-regenerate-workflow.md b/.opencode/memory/project/fragment-edit-regenerate-workflow.md
index e08853d..6e3a735 100644
--- a/.opencode/memory/project/fragment-edit-regenerate-workflow.md
+++ b/.opencode/memory/project/fragment-edit-regenerate-workflow.md
@@ -16,7 +16,7 @@ Verified end-to-end workflow for editing `prompts/fragments/` and keeping `syste
 5. **Verify**:
    - `grep -n "<system_version>" prompts/fragments/01-system_version.md system-prompt.md` — both MUST show the SAME bumped version.
    - `grep -n "<new-section-name>" system-prompt.md` — the new content MUST be present in the assembled artifact.
-   - `git diff --stat -- 'loop-engine/' '*.py'` — MUST be empty (zero out-of-scope changes).
+   - `git status --porcelain` — only the intended files (fragment(s) + `system-prompt.md` + docs) should appear (zero out-of-scope changes).
    - Optionally `lint_system_prompt_sync()` (lint MCP server) or `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check.md && diff /tmp/check.md system-prompt.md` before commit.
 6. **Sync docs**: update `CHANGELOG.md` (Parse-Then-Append under the new version header), the active task file, and any affected skill templates/audit checks.
 
diff --git a/.opencode/memory/workflows/approval_gates_use_question_tool.md b/.opencode/memory/workflows/approval_gates_use_question_tool.md
index 9ecdd0c..c046fe3 100644
--- a/.opencode/memory/workflows/approval_gates_use_question_tool.md
+++ b/.opencode/memory/workflows/approval_gates_use_question_tool.md
@@ -7,4 +7,4 @@ updated_at: '2026-09-27T05:57:38.148311+00:00'
 
 # Approval gates must use the question tool (Manager standing rule 2026-09-27)
 
-Whenever the cognitive executor needs Manager approval — after presenting a plan, after the Code Reviewer accepts code (PO_REVIEW_PENDING relay), or at any other approval gate — it MUST ask through the `question` tool (blocking options), never through plain prose. Reason: the goal plugin keeps the auto-continue loop running, so a prose question gets rolled past instead of answered. This holds in manual and autopilot modes; only hard blockers (missing credentials, Clarification Halt) may use prose. Blanket acknowledgements (ok/yes/looks good/emoji) never count as approval at any gate.
\ No newline at end of file
+Whenever the cognitive executor needs Manager approval — after presenting a plan, after the Code Reviewer accepts code (PO_REVIEW_PENDING relay), or at any other approval gate — it MUST ask through the `question` tool (blocking options), never through plain prose. Reason: a prose question can be rolled past by an auto-continue loop instead of answered. This holds in manual and autopilot modes; only hard blockers (missing credentials, Clarification Halt) may use prose. Blanket acknowledgements (ok/yes/looks good/emoji) never count as approval at any gate.
\ No newline at end of file
diff --git a/.opencode/memory/workflows/global-install-upgrade.md b/.opencode/memory/workflows/global-install-upgrade.md
index 2c83a70..6f99047 100644
--- a/.opencode/memory/workflows/global-install-upgrade.md
+++ b/.opencode/memory/workflows/global-install-upgrade.md
@@ -15,18 +15,18 @@ Updates the machine-global installations of the Cognitive Lead AI HQ (MCP server
 
 | Component      | OpenCode                                                                                                       |
 | -------------- | -------------------------------------------------------------------------------------------------------------- |
-| MCP servers    | `~/.config/opencode/mcp-{context,memory,lint}-server/` + `~/.config/opencode/mcp-persona-server/` (4 modules, Task 167) + `~/.config/opencode/mcp-decision-server/` (2 modules, Task 168) + `~/.config/opencode/mcp-common/` (shared lib, Task 170); each with `pyproject.toml` + committed `uv.lock`, launched via `<dir>/.venv/bin/python <dir>/server.py` (direct venv, never `uv run` — uv startup exceeds the V2 connect timeout under multi-session spawn load, 2026-09-29) |
+| MCP servers    | `~/.config/opencode/mcp-{context,memory,lint,brain}-server/` (brain bridge = `mcp-brain-bridge/`) + `~/.config/opencode/mcp-decision-server/` + `~/.config/opencode/mcp-common/` (shared lib); each with `pyproject.toml` + committed `uv.lock`, launched via `<dir>/.venv/bin/python <dir>/server.py` (direct venv, never `uv run` — uv startup exceeds the V2 connect timeout under multi-session spawn load, 2026-09-29) |
 | Telegram MCP   | `~/.config/opencode/mcp-telegram-server/` (upstream clone of chigwell/telegram-mcp — no fork) |
 | Skills         | `~/.config/opencode/skills/<name>/SKILL.md` (synced 1:1 with `skill-templates/` — count varies, verify by diff not by number) |
 | Custom agents  | `~/.config/opencode/agents/{cognitive-executor,cognitive-discovery}.md` |
 | Shell strategy | `~/.config/opencode/opencode-shell-strategy.md` |
 | System prompt  | `~/.config/opencode/system-prompt.md` |
-| Credentials    | `~/.config/opencode/.env` (chmod 600 backup of project `.env`; project copy stays authoritative since opencode loads project env for servers) |
+| Credentials    | `~/.config/opencode/.env` (chmod 600). The MCP servers self-load `.env` at import (`<server-dir>/.env` → `<server-dir>/../.env` → `<cwd>/.env`); for the global install that is this file, for repo runs the repo-root `.env`. Keep it seeded so both the CLI and the singleton services get the keys. |
 
 ## Source Files (repo)
 
 - `mcp-context-server/server.py`, `mcp-memory-server/server.py`, `mcp-lint-server/server.py`
-- `mcp-persona-server/*.py` (server, dual_dispatch, session, telegram), `mcp-decision-server/*.py` (server, redactor)
+- `mcp-brain-bridge/*.py` (server + capability/preflight/loop_guard/session_ledger/transport_learning/authority_retrieval), `mcp-decision-server/*.py` (server, redactor, detector)
 - `mcp-common/src/mcp_common/` (shared dotenv loader) + every server dir's `pyproject.toml` + `uv.lock` (Task 170; sync all three file kinds globally)
 - `skill-templates/*/` (all skills, synced 1:1 — never hardcode the count)
 - `agents/cognitive-executor.md`, `agents/cognitive-discovery.md`
@@ -34,11 +34,11 @@ Updates the machine-global installations of the Cognitive Lead AI HQ (MCP server
 
 ## Upgrade Steps
 
-1. **Audit drift** (diff repo vs installed — same loops as originally specified over servers, agents, shell-strategy, system-prompt, skills, tui.json, goal-plugin greps).
+1. **Audit drift** (diff repo vs installed — same loops as originally specified over servers, agents, shell-strategy, system-prompt, skills).
 2. **Copy drifted files** with `cp` + `chmod +x` (only those that differ). Multi-module servers copy `*.py` (never `__pycache__/`). For `opencode.json` do NOT blind copy — repo uses relative paths, global uses absolute paths; edit surgically and validate JSON after every edit.
 2b. **Delete global orphans** (rule added 2026-09-11: `cp` never removes, so deletions need this step). Any skill dir present under `~/.config/opencode/skills/` but absent from repo `skill-templates/` MUST be removed with `rm -rf` — that is how skill drops (e.g. brainstorm-swarm, perplexity-research) propagate globally. Same for MCP server dirs and custom agents missing from the repo. Never delete in the reverse direction (repo is source of truth).
 3. **Re-verify** with the same diff commands — expect no DRIFT output except the expected `opencode.json` relative vs absolute.
-4. **Smoke-test**: `opencode mcp list` (expect ONLY the currently-enabled servers connected) + repo persona test suite (`rtk test uv run --project mcp-persona-server --with pytest --with pathspec pytest tests/ -q`).
+4. **Smoke-test**: `opencode mcp list` (expect ONLY the currently-enabled servers connected) + `rtk test uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml pytest tests/ -q`.
 4b. **RTK install** (rule added 2026-09-12): the token-trimming runner from `docs/opencode-shell-strategy.md` §8. Install the musl binary when missing (`mkdir -p ~/.local/bin && curl -fsSL -o ~/.local/bin/rtk <release-url>/rtk-x86_64-unknown-linux-musl && chmod +x ~/.local/bin/rtk`), verify `rtk --version`. Never run `rtk init -g` — it rewrites the global OpenCode config.
 5. **Telegram MCP step 2.5** (upstream chigwell/telegram-mcp): lag check via `rev-list --count HEAD..origin/main`; run backup+rsync upgrade only when lag > 0. **Update-only — do NOT run telegram's own pytest suite** (its live-network tests hang ~300s on this machine and add nothing; `opencode mcp list` 5/5 is the sufficient smoke test). Rule set 2026-09-10 per Manager.
 
diff --git a/CHANGELOG.md b/CHANGELOG.md
index ff4d833..2b06ea4 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,22 +8,23 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
-- **Rate-limit rescue plugin (Task 282):** new `plugins/rate-limit-rescue/` (repo source of truth) — a global OpenCode plugin whose `retry` hook fires ONLY on free-tier 429s, runs the env-configured command (default `~/.local/bin/rr`, via `RATE_LIMIT_COMMAND`), appends a JSONL metrics line (`RATE_LIMIT_METRICS`, default under `~/.local/share/opencode/`), and overrides the wait to 30s. Gate grounded in opencode.log truth (`AI.Error.QuotaExceeded`, no status/words: rate-ish AND free-ish-model). Hook never throws; metrics carry error shape + proposed delay for Go comparison. README included. Verified: `node --check` exit 0 plus stub harness (exact-log-shape=rescued/30000, e500=pass, paid429=pass).
-
-### Fixed
-
-- **Mode-aware single prompt O1 (Task 281):** session now declares `MODE: manual|automatic` at start (`prompts/fragments/19-initialization.md`); QA/Reviewer behaviors (`06-personas.md`) and both Hands summary blocks (`09-hands_protocols.md`) carry automatic-mode overrides that chain `brain_turn` instead of asking the Manager to ferry files. Manual courier wording untouched. `<system_version>` 9.48.0 → 9.49.0, `system-prompt.md` rebuilt (96522 bytes, byte-identical re-assemble verified).
-
-- **Autopilot plan-approval chain + cutoff honesty (Task 280):** `agents/cognitive-executor.md` supervised-autopilot gate no longer implements directly on approval — the approval answer routes back via `brain_turn` (same `task_id`) for a Senior Programmer `<hands_implementation_task>` XML, and Hands execute only from that XML. Cutoff line (fragment `03-system_context.md:2`) no longer claims January 2025: web verification 2026-09-29 found Meta publishes no Muse Spark cutoff (official model page silent, corroborated secondary), so the line now states unverified status explicitly. `<system_version>` 9.47.0 → 9.48.0, `system-prompt.md` rebuilt via assembler (95266 bytes, byte-identical re-assemble verified).
-
-### Added
+- **Task 283 — OpenCode V2 + OpenChamber 2 migration and global install:** single OpenChamber-managed OpenCode instance (background shared service disabled via `service.json` `disabled:true`); no custom `opencode-server.service`; all OpenCode plugins removed and the retry plugin archived; docs rewritten to V2 (`docs/openchamber.md`, no Tailscale, no plugin content); orphan/leftover cleanup; and the `LLM.txt` global install corrected + executed (all server modules, `mcp-common` contents-copy, `.env` seed with placeholder-guard + backup), with Telegram credentials recovered from the 2026-09-29 backup and both accounts verified.
 
+- **Rate-limit rescue plugin (Task 282):** new `plugins/rate-limit-rescue/` (repo source of truth) — a global OpenCode plugin whose `retry` hook fires ONLY on free-tier 429s, runs the env-configured command (default `~/.local/bin/rr`, via `RATE_LIMIT_COMMAND`), appends a JSONL metrics line (`RATE_LIMIT_METRICS`, default under `~/.local/share/opencode/`), and overrides the wait to 30s. Gate grounded in opencode.log truth (`AI.Error.QuotaExceeded`, no status/words: rate-ish AND free-ish-model). Hook never throws; metrics carry error shape + proposed delay for Go comparison. README included. Verified: `node --check` exit 0 plus stub harness (exact-log-shape=rescued/30000, e500=pass, paid429=pass).
 - **Plugin full-V2 status verification + docs (Task 274):** verified both plugins are at their latest stable V2-capable versions — `@prevalentware/opencode-goal-plugin@0.1.52` (released 2026-09-26; upstream V2 port PR #49 + PR #58) and `@tarquinen/opencode-dcp@3.2.0` (stable 2026-09-20 is newest; 3.2.1–3.2.8 betas are stale experiments; V2 `setup()` via `session` hooks; `compress.permission: ask` unsupported in V2 by DCP design, default `allow` stands). `opencode plugin list` is documented as the source of truth (`~/.cache/opencode/packages/` is metadata-only). Upstream-issue policy recorded in `README.md` and `LLM.txt` §7.7: search open threads first, never duplicate (DCP V2 threads #627/#628/#631/#632 already active) — no issues were filed.
 - **Five-Python-MCP-server audit vs current web data (Task 275):** report-only audit, zero source modified. All five servers (`mcp-context-server` 8 tools, `mcp-memory-server` 6, `mcp-lint-server` 4, `mcp-decision-server` 6, `mcp-brain-bridge` 4; 8,427 LOC) use `FastMCP` + stdio transport, pin `mcp[cli]>=1.0,<2.0`, lock resolves to 1.30.0 which PyPI confirms is the latest v1.x (latest overall is SDK v2.2.0 for spec 2026-07-28). Verdict KEEP: stdio-loopback is the correct shape per every 2026 hardening guide, the v1 pin matches upstream's own `<2` advice, zero hits for shell/eval/pickle/os.system, subprocess uses are list-form git/python only, and 7/7 servers connect live under opencode 2.0.18. Flagged one stale memory sentence (`workflows/global-install-upgrade` claims persona code dirs KEPT; `mcp-persona-server/` was deleted in Task 191 and global is already clean) — awaiting Manager approval to correct. Full suite: **689 passed** (exit 0).
 - **Question-tool approval gates + brainstorming auto-eval (Task 276):** approval gates now mandate the `question` tool instead of prose-only asks (the goal-plugin loop rolls past prose) — `agents/cognitive-executor.md` Capability Preflight plus its plan-approval, PO_REVIEW_PENDING relay and goal-pause sections, and `prompts/fragments/11-execution_workflow.md` Steps 3/4/8. Brainstorming no longer needs a Manager mention: fragment 11 Step 2, the fragment 12 trigger and the input-processing trigger evaluate automatically on every planning turn including autopilot/XML, bound to the executor Seat Check. `<system_version>` bumped 9.46.0 → 9.47.0; `system-prompt.md` regen (94855 bytes, 8+/8-) plus sync test plus full suite green (689 passed, exit 0). Postfix restores Clarification fabricate and section 2.7 it plus fallback qualifier.
 
+### Changed
+
+- **Retry-rescue plugin archived + Manager-ordered delay:** moved `plugins/rate-limit-rescue/` → `archive/rate-limit-rescue/` (node_modules dropped) so the repo ships no plugins. The plugin's `RETRY_DELAY_MS` was changed 30_000 → 2_000 per explicit Manager order ("set 30 to 2 in repo and globally"); it is archived and referenced by no config, so the value has no runtime effect unless re-enabled.
+- **Docs/leftover audit + OpenChamber-managed service:** removed orphaned `scripts/fetch-opencode-docs.py`, `scripts/repomd`, and orphaned `docs/velocity.md`; deleted plugin-SDK leftovers (`.opencode/{package.json,package-lock.json,node_modules,commands}`) and `.pytest_cache/`. Slimmed the `audit-agents` runtime-state rule (no OpenCode-plugin wording). Fixed real install bugs in `LLM.txt` §4–§5: the global install now copies **all** server modules (brain-bridge siblings + `mcp-decision-server` — previously only 4 single `server.py` files were copied and decision-server was never installed) and explicitly creates the repo `.env` then `install -m 600` seeds `~/.config/opencode/.env`. Clarified the `.env` self-load contract across `LLM.txt`, `docs/services.md` (new Credentials section + launchd/Windows notes), `docs/setup.md`, `docs/telegram-setup.md`, `docs/brain-bridge.md`; fixed the `DECISION_REPO_PATH` guidance (self-loaded from `.env`, no `{env:}` block). Stale memory refs (persona-server, loop-engine) refreshed. Installed the **OpenChamber-managed service** via `openchamber startup enable --port 3005 --host 127.0.0.1` (systemd user unit, OpenChamber runs and manages its own OpenCode server — no separate OpenCode unit).
+
 ### Fixed
 
+- **Mode-aware single prompt O1 (Task 281):** session now declares `MODE: manual|automatic` at start (`prompts/fragments/19-initialization.md`); QA/Reviewer behaviors (`06-personas.md`) and both Hands summary blocks (`09-hands_protocols.md`) carry automatic-mode overrides that chain `brain_turn` instead of asking the Manager to ferry files. Manual courier wording untouched. `<system_version>` 9.48.0 → 9.49.0, `system-prompt.md` rebuilt (96522 bytes, byte-identical re-assemble verified).
+- **Autopilot plan-approval chain + cutoff honesty (Task 280):** `agents/cognitive-executor.md` supervised-autopilot gate no longer implements directly on approval — the approval answer routes back via `brain_turn` (same `task_id`) for a Senior Programmer `<hands_implementation_task>` XML, and Hands execute only from that XML. Cutoff line (fragment `03-system_context.md:2`) no longer claims January 2025: web verification 2026-09-29 found Meta publishes no Muse Spark cutoff (official model page silent, corroborated secondary), so the line now states unverified status explicitly. `<system_version>` 9.47.0 → 9.48.0, `system-prompt.md` rebuilt via assembler (95266 bytes, byte-identical re-assemble verified).
+- **Full V2-native migration, V1 remnants removed (direct Manager request, no task file):** completes the Task 272 groundwork — `plugin`→`plugins`, `permission.bash`→`permission.shell`, layered `tui.json`→single global `cli.json`, flat `mcp`→`mcp.servers` with `disabled:false` + `timeout:{catalog,execution}` (values preserved: 15s standard, 30s telegram/blowsh, 600s bridges). Deleted repo `tui.json` and global `~/.config/opencode/tui.json` (backups `.bak-272` both sides + `/tmp` global backup). Live docs converted: `README.md`, `LLM.txt` (example JSON + parity/verify/checklist sections), `docs/openchamber-tailscale.md`, `docs/opencode-shell-strategy.md`, `skill-templates/audit-agents/SKILL.md`, opencode-init validator + golden config + runtime matrix. `scripts/check_docs_sync.py` now reads `permission.shell`. Intentional residuals: `agents/*.md` frontmatter keeps `bash:` (agent-level tool-group name, still accepted), `capability.py` toolset note stays as historical grounding, `docs/history/` + archives keep V1 refs as provenance, `LLM.txt` keeps the V1→V2 field map as teaching text. `opencode --version` 2.0.19.
 - **MCP connect-timeout storm after V2 upgrade (direct Manager request, no task file):** since 2026-09-26 every session spawned its own copy of all 7 local MCP servers via `uv run`, and under that spawn storm (~126 concurrent server processes) startup routinely exceeded the 15s connect timeout — 721 `mcp connect failed: Request timed out` log lines (~200/day), each showing as a disabled server needing manual re-enable. Same symptom class as upstream `sst/opencode` #8478 / #11584. Fix: global `~/.config/opencode/opencode.json` now launches all 6 Python servers via their persistent venv interpreters (`<server-dir>/.venv/bin/python`, absolute script paths — telegram's relative `main.py` broke its first reconnect and was corrected), cutting startup to under a second; legacy `mcp.<name>` shape kept (this build ignores the native `mcp.servers` wrapper). Docs updated to the venv-direct rule: `LLM.txt` launch form + checklist + manual-launch block, `docs/telegram-setup.md`, `README.md`, memory `workflows/global-install-upgrade`. Verification: 7/7 `connected` via `opencode mcp list --print-logs`, stdio `initialize` handshake probed per server.
 
 ## [9.46.0] - 2026-09-26
diff --git a/LLM.txt b/LLM.txt
index 1aa56f3..0653ccd 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -70,9 +70,9 @@ curl -fsSL https://opencode.ai/v2/install | bash
 opencode --version   # expect 2.x
 ```
 
-If `opencode --version` shows 1.x, back up `~/.config/opencode/opencode.json` + `tui.json` first, then run the installer above (it replaces the V1 binary; both versions share the same config locations, so never point V1 at converted V2-only files). OpenChamber upgrades via `openchamber update` (expect 2.x). Full V1→V2 field map: `plugin`→`plugins`, `permission.bash`→`permission.shell`, layered `tui.json`→single global `cli.json` — see https://opencode.ai/v2/docs/migrate-v1/.
+If `opencode --version` shows 1.x, back up `~/.config/opencode/opencode.json` first, then run the installer above (it replaces the V1 binary). OpenChamber upgrades via `openchamber update` (expect 2.x). Full V1→V2 field map: `plugin`→`plugins`, `permission.bash`→`permission.shell`, layered `tui.json`→single global `cli.json`, flat `mcp`→`mcp.servers` — see https://opencode.ai/v2/docs/migrate-v1/.
 
-> V2 keeps dual keys during transition: `opencode.json` carries both `plugin` (V1) and `plugins` (V2); permission blocks carry both `bash` and `shell` denies. When both forms set the same value, native V2 wins.
+> V2 native only: `opencode.json` carries `plugins` (not `plugin`); permission blocks carry `shell` denies (not `bash`); `tui.json` is deleted — the terminal client reads the single global `~/.config/opencode/cli.json`.
 
 ---
 
@@ -106,11 +106,9 @@ Store this value — you will use it to construct absolute paths in the global c
 Create the global OpenCode directories:
 
 ```bash
-mkdir -p ~/.config/opencode/mcp-context-server
-mkdir -p ~/.config/opencode/mcp-memory-server
-mkdir -p ~/.config/opencode/mcp-lint-server
-mkdir -p ~/.config/opencode/mcp-brain-bridge
-mkdir -p ~/.config/opencode/mcp-common
+for d in mcp-context-server mcp-memory-server mcp-lint-server mcp-brain-bridge mcp-decision-server mcp-common; do
+  mkdir -p ~/.config/opencode/$d
+done
 mkdir -p ~/.config/opencode/skills
 ```
 
@@ -118,28 +116,49 @@ mkdir -p ~/.config/opencode/skills
 
 ## 5. Copy MCP Servers and Make Them Executable
 
-Copy the MCP server scripts from the cloned repo (brain bridge is a single module). Every server dir also carries `pyproject.toml` + committed `uv.lock` — copy those too so launches resolve locked deps:
+Copy the MCP server modules from the cloned repo. Every server is multi-module (`brain-bridge` = `server.py` + `capability.py`/`preflight.py`/`loop_guard.py`/`session_ledger.py`/`transport_learning.py`/`authority_retrieval.py`/`eval_harness.py`/`golden_replay.py`; `decision-server` = `server.py` + `redactor.py` + `detector.py`), so copy **all `*.py`**. Each dir also carries `pyproject.toml` + committed `uv.lock` — copy those too so launches resolve locked deps:
 
 ```bash
-cp /tmp/cognitive-lead-hq/mcp-context-server/server.py ~/.config/opencode/mcp-context-server/
-cp /tmp/cognitive-lead-hq/mcp-memory-server/server.py ~/.config/opencode/mcp-memory-server/
-cp /tmp/cognitive-lead-hq/mcp-lint-server/server.py ~/.config/opencode/mcp-lint-server/
-cp /tmp/cognitive-lead-hq/mcp-brain-bridge/server.py ~/.config/opencode/mcp-brain-bridge/
-cp -r /tmp/cognitive-lead-hq/mcp-common ~/.config/opencode/mcp-common
-for d in context-server memory-server lint-server; do
-  cp /tmp/cognitive-lead-hq/mcp-$d/pyproject.toml /tmp/cognitive-lead-hq/mcp-$d/uv.lock ~/.config/opencode/mcp-$d/
+for d in mcp-context-server mcp-memory-server mcp-lint-server mcp-brain-bridge mcp-decision-server; do
+  cp /tmp/cognitive-lead-hq/$d/*.py ~/.config/opencode/$d/
+  cp /tmp/cognitive-lead-hq/$d/pyproject.toml /tmp/cognitive-lead-hq/$d/uv.lock ~/.config/opencode/$d/
+  chmod +x ~/.config/opencode/$d/server.py
 done
-cp /tmp/cognitive-lead-hq/mcp-brain-bridge/pyproject.toml /tmp/cognitive-lead-hq/mcp-brain-bridge/uv.lock ~/.config/opencode/mcp-brain-bridge/
-chmod +x ~/.config/opencode/mcp-context-server/server.py
-chmod +x ~/.config/opencode/mcp-memory-server/server.py
-chmod +x ~/.config/opencode/mcp-lint-server/server.py
-chmod +x ~/.config/opencode/mcp-brain-bridge/server.py
+# mcp-common: copy CONTENTS into the pre-created dir (the trailing "/." avoids
+# nesting to mcp-common/mcp-common when the destination already exists).
+cp -a /tmp/cognitive-lead-hq/mcp-common/. ~/.config/opencode/mcp-common/
 
 # Preserve system-prompt.md globally for the user's Orchestrator
 cp /tmp/cognitive-lead-hq/system-prompt.md ~/.config/opencode/system-prompt.md
 
 # Vendor the non-interactive shell strategy globally (instructions file)
 cp /tmp/cognitive-lead-hq/docs/opencode-shell-strategy.md ~/.config/opencode/opencode-shell-strategy.md
+
+# --- credentials: create the repo .env, then seed it globally ---------------
+# 1. Create the repo .env from the template and fill the keys:
+#      cp /tmp/cognitive-lead-hq/.env.example /tmp/cognitive-lead-hq/.env
+#      # edit: BRAIN_API_BASE, BRAIN_API_KEY, (optional) BRAIN_MODEL,
+#      #       DECISION_* , TELEGRAM_*
+#    The MCP servers self-load .env at import in this order (first match wins):
+#      <server-dir>/.env  ->  <server-dir>/../.env  ->  <cwd>/.env
+#    - repo runs use /tmp/cognitive-lead-hq/.env (= <server-dir>/../.env)
+#    - global installs use ~/.config/opencode/.env (= <server-dir>/../.env)
+# 2. Seed the global copy. NEVER clobber a live file silently: back up an
+#    existing ~/.config/opencode/.env first, and abort if the source has no
+#    real keys yet (still identical to .env.example) so placeholders cannot
+#    overwrite working credentials.
+if [ ! -f /tmp/cognitive-lead-hq/.env ]; then
+  cp /tmp/cognitive-lead-hq/.env.example /tmp/cognitive-lead-hq/.env
+  echo ">> Edit /tmp/cognitive-lead-hq/.env with your keys, then re-run this block."
+fi
+if cmp -s /tmp/cognitive-lead-hq/.env /tmp/cognitive-lead-hq/.env.example; then
+  echo "!! /tmp/cognitive-lead-hq/.env still matches .env.example (placeholders). Fill it in; skipping global seed."
+else
+  if [ -f ~/.config/opencode/.env ]; then
+    cp -a ~/.config/opencode/.env ~/.config/opencode/.env.bak-$(date -u +%Y%m%d-%H%M%S)
+  fi
+  install -m 600 /tmp/cognitive-lead-hq/.env ~/.config/opencode/.env
+fi
 ```
 
 ---
@@ -188,56 +207,57 @@ After this, the `cognitive-executor` will be available as a primary agent, enfor
 
 Create or update `~/.config/opencode/opencode.json`. You MUST use **absolute paths** in the `command` array — resolve the `~` to the full home directory path discovered in Step 3. The project ships **7 MCP servers** (3 core + `manager_decisions` + `brain` bridge + `blowsh` browsing + `telegram` account routing); the persona server and the previous browser automation MCP are retired — use `blowsh` for JS-heavy browsing.
 
-Write the following JSON (replace `$HOME` with the actual home directory path only where it still appears — the `mcp` entries are loopback URLs shared by every session and project, so they contain no paths at all). V2 structure per https://opencode.ai/docs/mcp-servers/ (verified 2026-09-29): each MCP runs as **one supervised singleton** on `127.0.0.1` (see `docs/services.md` + Step 7.5), and OpenCode connects via `type: "remote"` + `url` + `enabled` + `timeout` (default 5000ms; ours are raised — 15s standard, 30s telegram, 120s blowsh, 600s LLM bridges). No session ever spawns its own server processes: with 2+ sessions open the OS process count per server stays exactly one.
+Write the following JSON (replace `$HOME` with the actual home directory path only where it still appears — the `mcp` entries are loopback URLs shared by every session and project, so they contain no paths at all). V2 structure per https://opencode.ai/v2/docs/mcp-servers/ (verified 2026-09-29): each MCP runs as **one supervised singleton** on `127.0.0.1` (see `docs/services.md` + Step 7.5), and OpenCode connects via `mcp.servers` entries with `type: "remote"` + `url` + `disabled: false` + `timeout: {catalog, execution}` (ours are raised above the 5000ms default — 15s standard, 30s telegram, 120s blowsh, 600s LLM bridges). No session ever spawns its own server processes: with 2+ sessions open the OS process count per server stays exactly one.
 
 ```json
 {
   "$schema": "https://opencode.ai/config.json",
   "default_agent": "cognitive-executor",
   "instructions": ["$HOME/.config/opencode/opencode-shell-strategy.md"],
-  "plugin": ["@prevalentware/opencode-goal-plugin", "@tarquinen/opencode-dcp@latest"],
   "mcp": {
-    "custom_context": {
-      "type": "remote",
-      "url": "http://127.0.0.1:8102/mcp",
-      "enabled": true,
-      "timeout": 15000
-    },
-    "project_memory": {
-      "type": "remote",
-      "url": "http://127.0.0.1:8103/mcp",
-      "enabled": true,
-      "timeout": 15000
-    },
-    "lint": {
-      "type": "remote",
-      "url": "http://127.0.0.1:8101/mcp",
-      "enabled": true,
-      "timeout": 15000
-    },
-    "manager_decisions": {
-      "type": "remote",
-      "url": "http://127.0.0.1:8104/mcp",
-      "enabled": true,
-      "timeout": 600000
-    },
-    "brain": {
-      "type": "remote",
-      "url": "http://127.0.0.1:8105/mcp",
-      "enabled": true,
-      "timeout": 600000
-    },
-    "blowsh": {
-      "type": "remote",
-      "url": "http://127.0.0.1:8107/mcp",
-      "enabled": true,
-      "timeout": 120000
-    },
-    "telegram": {
-      "type": "remote",
-      "url": "http://127.0.0.1:8106/mcp",
-      "enabled": true,
-      "timeout": 30000
+    "servers": {
+      "custom_context": {
+        "type": "remote",
+        "url": "http://127.0.0.1:8102/mcp",
+        "disabled": false,
+        "timeout": { "catalog": 15000, "execution": 15000 }
+      },
+      "project_memory": {
+        "type": "remote",
+        "url": "http://127.0.0.1:8103/mcp",
+        "disabled": false,
+        "timeout": { "catalog": 15000, "execution": 15000 }
+      },
+      "lint": {
+        "type": "remote",
+        "url": "http://127.0.0.1:8101/mcp",
+        "disabled": false,
+        "timeout": { "catalog": 15000, "execution": 15000 }
+      },
+      "manager_decisions": {
+        "type": "remote",
+        "url": "http://127.0.0.1:8104/mcp",
+        "disabled": false,
+        "timeout": { "catalog": 600000, "execution": 600000 }
+      },
+      "brain": {
+        "type": "remote",
+        "url": "http://127.0.0.1:8105/mcp",
+        "disabled": false,
+        "timeout": { "catalog": 600000, "execution": 600000 }
+      },
+      "blowsh": {
+        "type": "remote",
+        "url": "http://127.0.0.1:8107/mcp",
+        "disabled": false,
+        "timeout": { "catalog": 120000, "execution": 120000 }
+      },
+      "telegram": {
+        "type": "remote",
+        "url": "http://127.0.0.1:8106/mcp",
+        "disabled": false,
+        "timeout": { "catalog": 30000, "execution": 30000 }
+      }
     }
   },
   "permission": {
@@ -266,29 +286,21 @@ Write the following JSON (replace `$HOME` with the actual home directory path on
 }
 ```
 
-Also create the TUI parity file for OpenCode 1 stable (required for the goal sidebar/palette — prevalentware docs — plus DCP panel):
+No OpenCode plugins are installed. The terminal client config `~/.config/opencode/cli.json` is V2-native (no project `cli.json`, no `tui.json`):
 
-```bash
-cat > ~/.config/opencode/tui.json <<'JSON'
+```json
 {
-  "plugin": [
-    "@prevalentware/opencode-goal-plugin",
-    "@tarquinen/opencode-dcp@latest"
-  ]
+  "$schema": "https://opencode.ai/v2/cli.json"
 }
-JSON
-cat tui.json  # project root — same plugin content (formatting may differ single vs multi-line, verify with grep)
 ```
 
-OpenCode 1 reads `plugin` from **both** `opencode.json` (server/tools) and `tui.json` (sidebar/palette). Without the `tui.json` entry the `/goal` command works but the TUI goal indicator stays hidden. DCP (`/dcp`, `/dcp-compress`) likewise loads from the same `plugin` arrays.
-
 **Important:** Replace `$HOME` with the actual absolute path resolved in Step 3 (e.g., `/home/alice` or `/Users/alice`). This is critical — MCP servers will NOT work with relative paths or `~` in the global config because OpenCode may be invoked from any working directory.
 
-**Launch form + credentials:** no session spawns servers anymore — the 7 singletons run as supervised services on `127.0.0.1:8101-8107` (started in Step 7.5, full map in `docs/services.md`), and the config above only points at them via `type: "remote"`. The old per-session stdio storm (and its `mcp connect failed: Request timed out` failures, ~200/day before the 2026-09-29 singleton fix) is gone by construction. The brain/decision timeouts stay 600000ms (10 min) — LLM turns need it. Credentials (`BRAIN_*`, `DECISION_*`, telegram session) live in each singleton's own environment (systemd unit `Environment=` lines or the server dir `.env`), NOT in the OpenCode config — the servers self-load `.env` at import (`<server-dir>/.env` → install-root `.env` → `<cwd>/.env`, never overriding real env). Telegram prerequisites (clone + `uv sync` + `.env` + allowed-root dirs) are still installed per §7.6 — only the launch moved into the `mcp-telegram` service.
+**Launch form + credentials:** no session spawns servers anymore — the 7 singletons run as supervised services on `127.0.0.1:8101-8107` (started in Step 7.5, full map in `docs/services.md`), and the config above only points at them via `type: "remote"`. The old per-session stdio storm (and its `mcp connect failed: Request timed out` failures, ~200/day before the 2026-09-29 singleton fix) is gone by construction. The brain/decision timeouts stay 600000ms (10 min) — LLM turns need it. Credentials (`BRAIN_*`, `DECISION_*`, `TELEGRAM_*`) are **not** in the OpenCode config: each server self-loads `.env` at import, in order `<server-dir>/.env` → `<server-dir>/../.env` → `<cwd>/.env`, never overriding real process env. For the global install that effective file is **`~/.config/opencode/.env`** (seeded in Step 5, `chmod 600`); for servers run straight from the repo it is the repo-root `.env`. The systemd/launchd/Windows units therefore need **no** `EnvironmentFile=` for these keys. Telegram prerequisites (clone + `uv sync` + `.env` + allowed-root dirs) are still installed per §7.6 — only the launch moved into the `mcp-telegram` service.
 
 **QA/review run through the bridge:** the Hands calls `brain_turn` with the instruction + task file (see the Bridge section in `agents/cognitive-executor.md`). No per-persona commands or learning stores.
 
-> **Project vs Global `opencode.json` + `tui.json` (Option A fix 2026-08-25, updated 2026-08-28 for @prevalentware, 2026-09-05 for @tarquinen/opencode-dcp, 2026-09-29 singleton cutover):** The **repo's** `opencode.json` (committed) carries **no `mcp` section at all** — all 7 servers live in the **global** `~/.config/opencode/opencode.json` (created here) as `type: "remote"` loopback URLs (`http://127.0.0.1:8101-8107/mcp`, identical for every user — no per-machine paths). `plugin` arrays (goal + DCP) are **identical** in project and global by design. New installations and `global-install-upgrade` (Step 5 in `.opencode/memory/workflows/global-install-upgrade.md`) must keep this split — `diff -q opencode.json ~/.config/opencode/opencode.json` will always differ (repo has no `mcp`, global has 7 remote entries) by design; verify global shows 7 `127.0.0.1:810*/mcp` URLs. Verify parity with `diff -q tui.json ~/.config/opencode/tui.json && echo "tui.json in sync ✓"` and `grep -q "@tarquinen/opencode-dcp" opencode.json && grep -q "@tarquinen/opencode-dcp" ~/.config/opencode/opencode.json && echo "DCP plugin both ✓"`.
+> **Project vs Global `opencode.json` (full V2, 2026-10-01):** The **repo's** `opencode.json` (committed) carries **no `mcp` section at all** — all 7 servers live in the **global** `~/.config/opencode/opencode.json` (created here) under `mcp.servers` as `type: "remote"` loopback URLs (`http://127.0.0.1:8101-8107/mcp`, identical for every user — no per-machine paths). New installations and `global-install-upgrade` (Step 5 in `.opencode/memory/workflows/global-install-upgrade.md`) must keep this split — `diff` of repo vs global `opencode.json` will always differ (repo has no `mcp`, global has 7 remote entries) by design; verify global shows 7 `127.0.0.1:810*/mcp` URLs.
 
 **Telegram is optional but auto-configured:** the entry above points at `~/.config/opencode/mcp-telegram-server` (installed in the opencode config dir per global-install-upgrade, absolute path required) with three allowed roots (`/tmp/telegram-mcp` for temp state + `~/.config/opencode/mcp-telegram-server/downloads` for exported media + `$HOME` so home files upload). If you cloned elsewhere, update the venv-python path, the `main.py` path and the trailing roots — keep them inside `$HOME` or `/tmp` and ensure `telegram_download_media` can write there. The server is installed in Step 7.6 even before you have API credentials; it stays idle (no `TELEGRAM_SESSION_STRING`) until you finish 7.6. For Docker blowsh no host binary is needed — `docker pull ghcr.io/mokhtarabadi/blowsh-mcp:latest` on first `fetch_web` run.
 
@@ -377,208 +389,76 @@ Telemetry-free cache/SSRF defaults (`CACHE_TTL_MS=300000`, `ALLOW_PRIVATE_URLS=f
 
 ---
 
-## 7.7. Install Dynamic Context Pruning (DCP) Plugin
-
-DCP (`@tarquinen/opencode-dcp`, 4.2k stars, AGPL-3.0) reduces token usage via compress tool + automatic deduplication + purge-errors. Mirrors the goal-plugin install — same plugin entries in `opencode.json` (`plugins` on V2, `plugin` fallback on V1) + global `cli.json`, project and global identical.
-
-```bash
-opencode plugin @tarquinen/opencode-dcp@latest --global
-opencode plugin @prevalentware/opencode-goal-plugin --global
-```
-
-This adds both plugins to `~/.config/opencode/opencode.json` + `tui.json`. Ensure the project files match (already committed in this repo):
-
-```bash
-grep -q "@tarquinen/opencode-dcp" opencode.json && echo "project opencode.json DCP ✓"
-grep -q "@tarquinen/opencode-dcp" tui.json && echo "project tui.json DCP ✓"
-grep -q "@tarquinen/opencode-dcp" ~/.config/opencode/opencode.json && echo "global opencode.json DCP ✓"
-grep -q "@tarquinen/opencode-dcp" ~/.config/opencode/tui.json && echo "global tui.json DCP ✓"
-```
-
-> **References ≠ installed:** config entries alone do NOT install plugins — the packages must land in `~/.cache/opencode/packages/`, and slash commands (`/goal`, `/dcp`, `/dcp-compress`) only appear after an OpenCode **restart**. Always verify:
->
-> ```bash
-> ls -d ~/.cache/opencode/packages/@tarquinen/opencode-dcp@latest ~/.cache/opencode/packages/@prevalentware/opencode-goal-plugin@latest && echo "plugins installed ✓"
-> ```
->
-> Then restart OpenCode before testing `/goal` or `/dcp-compress`.
-
-### DCP configuration (dcp.jsonc)
-
-DCP uses its own config file, searched in order (project overrides global). Restart OpenCode after changes:
-
-1. Global: `~/.config/opencode/dcp.jsonc` (created automatically on first run)
-2. Project: `.opencode/dcp.jsonc` in your project's `.opencode` directory
-
-Defaults are applied automatically (enabled, autoUpdate, pruneNotification detailed, compress range mode with min 50k / max 100k, deduplication + purgeErrors on). If you use small-context models, lower `compress.minContextLimit` / `maxContextLimit` to match.
-
-### DCP commands
-
-- `/dcp` — opens the DCP panel with context, stats, manual-mode controls
-- `/dcp-compress [focus]` — one compression pass, optional focus text
-
-> **Upstream note:** DCP development has slowed; new context-management work moved to `sleev` (`npm i -g sleev`). DCP remains available for OpenCode plugin users. If starting fresh and Sleev fits, prefer it; otherwise DCP stays supported here.
+## 7.7. Plugins
 
-### Plugin V2 status (verified 2026-09-26, opencode 2.0.18)
-
-Both plugins are at their latest stable versions and both are V2-capable upstream — no upgrade work remains:
-
-- **goal `@prevalentware/opencode-goal-plugin@0.1.52`** (released 2026-09-26; 0.1.50 Sep 21, 0.1.51 Sep 22): upstream V2 port merged via PR #49 (2026-09-14: beta-19425 contract, compaction context, restart transcript recovery, dual `[id, server, setup]` shape, V2 lifecycle smoke PASS) and PR #58 (merged + released same day: V2 task-recovery scoping). Open issue #54 is a V1-host registration bug whose body confirms `setupV2` targets V2 hosts.
-- **DCP `@tarquinen/opencode-dcp@3.2.0`** (stable, 2026-09-20): V2 `setup()` registers `session` hooks (`context`, `compaction`) — the documented V2 equivalents of V1 `experimental.chat.messages.transform`. The 3.2.1–3.2.8 betas are stale Mar/Apr experiments; stable 3.2.0 is newest. Known V2 gap, baked into DCP source: `compress.permission: ask` throws "not supported by OpenCode V2 public plugin API yet" — keep the default `allow`.
-- **Verification:** `opencode plugin list` must show `0.1.52` + `3.2.0` with zero errors — this is the source of truth (`~/.cache/opencode/packages/` holds metadata only, no `dist/`; the V2 host resolves npm at runtime).
-- **Upstream-issue policy:** search before filing, never duplicate. Goal repo: prevalentWare/opencode-goal-plugin. DCP repo: Opencode-DCP/opencode-dynamic-context-pruning (V2 threads #627 compat, #628 `/dcp-compress` palette, #631 V2 setup, #632 compact tags all active — file nothing there).
+None. This platform runs OpenCode with **no plugins** — goal tracking comes from OpenChamber's built-in **Session Goals**, and context compaction is native to OpenCode V2. The repo and global `opencode.json`/`cli.json` carry no plugin entries.
 
 ---
 
-## 7.8. Worktree Support — OpenChamber Native (owt Removed 2026-09-08)
-
-owt (`@nano-step/opencode-worktree-plugin`, npm, MIT) was installed (`npm install -g @nano-step/opencode-worktree-plugin` + `owt-setup install` → plugin + 7 slash commands, `.gitignore` guards) and later disabled (`.disabled`). **On 2026-09-08 it was fully removed** (`npm uninstall -g @nano-step/opencode-worktree-plugin` + `rm` plugin + 7 `command/*.md`) because **OpenChamber 2.0.2 (2.x series; 1.22.2 at removal time) provides first-class worktrees natively**: [Worktree Sessions](https://docs.openchamber.dev/worktrees/) (new-worktree dialog: new/existing branch, `OpenChamber makes the branch, sets up the folder, and starts a session in it`), [Multi-run](https://docs.openchamber.dev/multi-run/) (`isolate runs` → each run its own worktree/branch, up to 5 models), Fusion, and Git view → Integrate (merge worktree commits onto main). Use OpenChamber sidebar/dialogs for worktrees — owt is redundant when OpenChamber is running (confirmed via `packages/ui/src/lib/worktreeSessionCreator.ts`, `packages/docs/content/docs/worktrees.mdx`). No `openchamber --worktree` CLI flag exists — worktrees are GUI-driven.
+## 7.8. Worktrees — OpenChamber Native
 
-If you need CLI/headless worktrees **without** OpenChamber (SSH/CI), reinstall owt:
-
-```bash
-npm install -g @nano-step/opencode-worktree-plugin
-owt-setup install  # restores plugin + 7 commands; restart OpenCode
-# optional: owt hook --global  # strips Co-authored-by via commit-msg hook (left disabled originally)
-```
-
-Worktree state (owt, now removed): was under `.opencode/worktrees/` + `.opencode/worktree-sessions.json` (gitignored). OpenChamber worktrees are SDK-managed (probed via `git worktree list`, not that path).
+Worktrees are a first-class OpenChamber feature (no plugin): [Worktree Sessions](https://docs.openchamber.dev/worktrees/) (new/existing branch, OpenChamber creates the branch, sets up the folder, and starts a session in it), [Multi-run](https://docs.openchamber.dev/multi-run/) (`isolate runs` → each run its own worktree/branch, up to 5 models), Fusion, and Git view → Integrate. Use the sidebar/dialogs — there is no `openchamber --worktree` CLI flag.
 
 ---
 
-## 7.9. (Optional) Install OpenChamber — Multi-Device Remote Access (Ask User First)
-
-OpenChamber (`@openchamber/web` 2.0.2, MIT, Node≥22) is the web/mobile/ desktop workspace that runs **on top of OpenCode** (this repo's agent harness). It gives you phone/PC remote access to the same OpenCode sessions via Tailscale, LAN, or Cloudflare Tunnel, plus native worktrees (see §7.8), Session Goals, Multi-run + Fusion, and GitHub integration. **You MUST ask the user before installing:**
-
-> "OpenChamber adds multi-device remote access (phone/PC) via Tailscale or Cloudflare Tunnel. Do you need multi-device remote access? If yes I will install it on a Tailscale-only port; if not, skip this section."
+## 7.9. Install OpenChamber (it manages OpenCode for you)
 
-Skip entirely if the user says no — the core OpenCode + MCP servers already work without it.
+OpenChamber (`@openchamber/web`, MIT, Node ≥22) is the web/mobile/desktop workspace that runs **on top of OpenCode**. OpenChamber starts and manages its own OpenCode server — you do **not** run a separate `opencode serve` unit, and you never set `OPENCODE_SKIP_START`.
 
-> **Coexistence note (2026-09-08):** installing OpenChamber does NOT remove any plugin. The goal plugin (`@prevalentware/opencode-goal-plugin`) stays enabled in all 4 configs — `/goal` and OpenChamber Session Goals complement each other. Only the `owt` worktree plugin was removed (OpenChamber worktrees replace it, see §7.8).
+Ask the user first:
 
-### When to install
+> "OpenChamber adds a web/mobile workspace for your OpenCode sessions. Do you want it? If yes I will install it and enable start-at-boot."
 
-- User wants to steer/review coding sessions from phone or a second PC (tailscale `100.x` or LAN IP).
-- User needs the OpenChamber UI (worktrees dialog, Multi-run ≤5, Fusion, walkthroughs) rather than bare `opencode` CLI.
+### Prerequisites
 
-### Prerequisites (verify, do not assume)
+- `node --version` ≥ 22, `opencode --version` prints 2.x.
+- In this HQ setup `:3000` is the Next.js app and `:8080` is code-server — use an alt port (recommended `:3005`).
 
-- `node --version` ≥22 (`lts/*`), `opencode --version` works, `tailscale status` shows peers if using Tailscale.
-- Default `:3000` is the Next.js (fa/en) app and `:8080` is code-server in this HQ setup — **do NOT use 3000** for OpenChamber; pick an alt port (recommended `:3005`).
-
-### Install + first run (Tailscale-only hardened)
+### Install + first run
 
 ```bash
-# 1. Install globally (Node≥22 required)
+# 1. Install globally (Node >= 22)
 npm install -g @openchamber/web
-openchamber --version   # expect 2.x
+openchamber --version          # expect 2.x
 
-# 2. UI password — never commit, chmod 600, pass via env to avoid ps exposure
+# 2. UI password — chmod 600, never committed
 mkdir -p ~/.secrets
 openssl rand -base64 24 > ~/.secrets/openchamber-ui-password
 chmod 600 ~/.secrets/openchamber-ui-password
 export OPENCHAMBER_UI_PASSWORD="$(cat ~/.secrets/openchamber-ui-password)"
 
-# 3. Pick Tailscale IP and start daemon — bind ONLY to the tailnet (not 0.0.0.0)
-#    ss -tlnp must later show 100.82.29.19:3005, not 0.0.0.0:3005; public IP → refused is correct
-tailscale ip -4   # e.g. 100.82.29.19 — use this as --host
-openchamber status   # check nothing on :3005
-openchamber --lan --port 3005 --host 100.82.29.19 --server http://100.82.29.19:3005
-# alternative foreground form that startup uses:
-# openchamber serve --foreground --port 3005 --host 100.82.29.19 --ui-password "$OPENCHAMBER_UI_PASSWORD"
-
-# 4. Verify: Tailscale 200, public refused, loopback refused (when tailscale-bound)
-curl -s -o /dev/null -w "%{http_code}\n" http://100.82.29.19:3005/   # 200
-curl -s -m 5 -o /dev/null -w "%{http_code}\n" http://194.76.154.73:3005/ && echo "PUBLIC OPEN" || echo "public refused (good)"
-curl -s -m 2 -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3005/ || echo "loopback refused when tailscale-bound (expected)"
-openchamber status   # mode + password: yes
-ss -tlnp | grep 3005   # 100.82.29.19:3005 LISTEN
-
-# 5. Auto-start at boot (systemd user service, survives reboot/logout/crash)
-export OPENCHAMBER_UI_PASSWORD="$(cat ~/.secrets/openchamber-ui-password)"
-openchamber startup enable --port 3005 --host 100.82.29.19
-sudo loginctl enable-linger $USER
-openchamber startup status   # startup enabled, service active, lingering enabled
-systemctl --user is-enabled openchamber   # enabled
-systemctl --user is-active openchamber    # active
-# restart test: openchamber stop --port 3005; sleep 6; systemctl --user is-active openchamber → active
-
-# 6. Pair a PC/phone (single-use expiring QR, revoke-able)
-openchamber connect-url --port 3005 --host 100.82.29.19 --qr   # or Settings → Remote Instances → Add device → Scope Anywhere/Home network only
-# PC on same tailnet: open http://100.82.29.19:3005 (Tailscale must show vm15996266)
-# Phone: Tailscale app joined to same tailnet, then open the same URL or scan QR in OpenChamber mobile/PWA
-```
+# 3. Start — managed OpenCode server, loopback bind
+openchamber --port 3005 --host 127.0.0.1 --ui-password "$OPENCHAMBER_UI_PASSWORD"
 
-Full runbook (daily commands, §2b auto-start, troubleshooting, security notes): `docs/openchamber-tailscale.md` — auto-generated after install and kept in repo.
+# 4. Verify
+openchamber status                                   # running, password: yes
+ss -tlnp | grep 3005                                 # 127.0.0.1:3005 LISTEN
+curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3005/   # 200
+```
 
-### OpenCode server password sync (external `opencode-server.service` mode, V2 only)
+### Start at boot — use OpenChamber's own integration
 
-V2 `opencode serve` requires Basic auth and mints a **random password every boot** unless `OPENCODE_PASSWORD`/`OPENCODE_SERVER_PASSWORD` is set — an external OpenChamber (`OPENCODE_HOST` + `OPENCODE_SKIP_START=true`) then fails with `401` on `/api/info` and `PushWatcher disconnected / upstream_unavailable`. Fix with one stable password shared by both units (USER runs the restarts, never the agent):
+OpenChamber writes the systemd user unit for you (it snapshots the environment and remembers port/host/password). Do **not** hand-author a unit.
 
 ```bash
-# 1. Stable password file (chmod 600, generated once, reused forever)
-[ -f ~/.config/opencode/.server-password ] || python3 -c "import secrets; print(secrets.token_urlsafe(32))" > ~/.config/opencode/.server-password
-chmod 600 ~/.config/opencode/.server-password
-
-# 2. Pin it on the OpenCode server unit (else random every boot)
-mkdir -p ~/.config/systemd/user/opencode-server.service.d
-PASS=$(cat ~/.config/opencode/.server-password)
-printf '[Service]\nEnvironment=OPENCODE_SERVER_PASSWORD=%s\n' "$PASS" > ~/.config/systemd/user/opencode-server.service.d/10-password.conf
-chmod 600 ~/.config/systemd/user/opencode-server.service.d/10-password.conf
-
-# 3. Same value is the OpenChamber client credential: it loads via
-#    EnvironmentFile=startup.env, so update that line (NOT a drop-in —
-#    the EnvironmentFile value wins over drop-in Environment):
-python3 -c "
-import re;
-stable = open('$HOME/.config/opencode/.server-password').read().strip();
-p = '$HOME/.config/openchamber/startup.env';
-s = open(p).read();
-open(p, 'w').write(re.sub(r'OPENCODE_SERVER_PASSWORD=.*', 'OPENCODE_SERVER_PASSWORD=\"' + stable + '\"', s, count=1));
-"
-
-# 4. Reload + restart (USER action), then verify zero 401s
-systemctl --user daemon-reload
-systemctl --user restart opencode-server openchamber
-journalctl --user -u openchamber -n 20 --no-pager | grep -c 'status: 401' || true   # expect 0
-journalctl --user -u openchamber --since '2 minutes ago' --no-pager | grep -m 2 'PushWatcher.*connected'
+export OPENCHAMBER_UI_PASSWORD="$(cat ~/.secrets/openchamber-ui-password)"
+openchamber startup enable --port 3005 --host 127.0.0.1
+openchamber startup status                 # startup enabled + service active
+sudo loginctl enable-linger $USER          # start at boot without login
 ```
 
-Root cause of a recurrence is always the same: the two sides hold different passwords (server re-randomized, or `startup.env` went stale). Re-run steps 2–4; never delete `~/.config/opencode/.server-password` (rotating it means re-syncing both sides).
-
-### Cloudflare Tunnel (deferred)
+Re-run `openchamber startup enable` after any env/password change (it rewrites `startup.env`). Remove with `openchamber startup disable`.
 
-Cloudflare Tunnel (`managed-remote` with your domain + account token) is the next step for public URLs without Tailscale. **Do NOT run a Quick tunnel with the real UI password for anything beyond a smoke test.** That step is intentionally deferred to a follow-up task — finish Tailscale first.
+### Remote access (optional)
 
----
-
-## 7.10. Systemd User Service Env (If OpenCode Runs as a Daemon)
-
-If the user runs OpenCode via a systemd user unit (e.g. `opencode-server.service`
-for OpenChamber), the daemon starts with a bare environment — shell exports do
-not apply and `{env:VAR}` forwarding in `opencode.json` resolves empty. Add the
-env file to the unit so the bridge/decision servers start with keys:
-
-```ini
-[Service]
-# Project env (keys + model pins). '-' = unit still starts if file is missing.
-EnvironmentFile=-<project-path>/.env
-# Portable alternative: EnvironmentFile=%h/.config/opencode/.env
+```bash
+openchamber tunnel start --port 3005        # ngrok-backed, or use your own reverse proxy
+openchamber connect-url --port 3005 --qr    # single-use pairing link
 ```
 
-Then `systemctl --user daemon-reload` (safe anytime). The vars take effect on the
-next `systemctl --user restart opencode-server` — the restart kills live
-sessions, so the USER runs it, never the agent. Verify with
-`systemctl --user show opencode-server.service -p EnvironmentFiles`.
-As process env these vars outrank every `.env` file fallback, so all projects
-served by the daemon share them. Per-project overrides still work via that
-project's own `.env` only for keys the daemon env does NOT set.
+When binding beyond loopback keep a strong UI password and prefer `--api-only` for headless clients.
 
-The same unit also pins the V2 server password (see §7.9 password-sync):
-`opencode-server.service.d/10-password.conf` sets
-`OPENCODE_SERVER_PASSWORD` from `~/.config/opencode/.server-password`
-(chmod 600). Without it every boot mints a random password and the external
-OpenChamber gets `401` on `/api/info`.
+Full runbook: `docs/openchamber.md`. Official docs: https://docs.openchamber.dev
 
 ---
 
@@ -600,12 +480,11 @@ export DECISION_REPO_PATH="$HOME/manager-decisions"   # clone/checkout path
 
 Without `DECISION_REPO_PATH` the server falls back to per-project
 `.opencode/decisions/` (write-through cache + offline fallback) and logs it —
-records still land, personality just stays local. Forward it in
-`opencode.json` as `{env:DECISION_REPO_PATH}`, the same interpolation form the
-sibling keys use (`{env:BRAIN_*}`): the daemon passes the variable through and
-the value stays per-user in the shell env or `.env`. Never hardcode a literal
-path in the shared `opencode.json` environment block — one global literal
-would break per-user resolution.
+records still land, personality just stays local. Set it in the server's own
+`.env` (`~/.config/opencode/.env` for the global install, repo-root `.env` for
+repo runs) — the decision server self-loads that file, so no `opencode.json`
+`{env:}` block is needed. Never hardcode a literal path in a shared config —
+one global literal would break per-user resolution.
 
 ---
 
@@ -640,22 +519,24 @@ After completing all steps, verify:
 - [ ] `~/.config/opencode/mcp-context-server/server.py` exists and is executable
 - [ ] `~/.config/opencode/mcp-memory-server/server.py` exists and is executable
 - [ ] `~/.config/opencode/mcp-lint-server/server.py` exists and is executable
-- [ ] `~/.config/opencode/mcp-brain-bridge/server.py` exists and is executable
+- [ ] `~/.config/opencode/mcp-brain-bridge/server.py` exists and is executable (plus its sibling modules `capability.py`, `preflight.py`, `loop_guard.py`, `session_ledger.py`, `transport_learning.py`, `authority_retrieval.py`, `eval_harness.py`, `golden_replay.py`)
+- [ ] `~/.config/opencode/mcp-decision-server/server.py` exists and is executable (plus `redactor.py`, `detector.py`)
+- [ ] `~/.config/opencode/mcp-common/src/mcp_common/env.py` exists
 - [ ] Skills are installed under `~/.config/opencode/skills/` (at least one subfolder exists) — should include `bundle-tasks` (31 skills total)
 - [ ] `~/.config/opencode/agents/cognitive-executor.md` exists
 - [ ] `~/.config/opencode/agents/cognitive-discovery.md` exists
 - [ ] `~/.config/opencode/opencode.json` exists with **absolute paths** (not `~` or relative paths) and 6 `mcp` entries (`custom_context`, `project_memory`, `lint`, `brain`, `blowsh`, `telegram`) + `blowsh_*`/`telegram_*`/`brain_turn` permissions, no former browser entry
-- [ ] `~/.config/opencode/opencode.json` + global `cli.json` `plugins` arrays contain both `@prevalentware/opencode-goal-plugin` and `@tarquinen/opencode-dcp` (V2 keys; V1 `plugin` arrays in `opencode.json` + `tui.json` kept as fallback); project `opencode.json` matches (`grep -q "@tarquinen/opencode-dcp" opencode.json && grep -q "@tarquinen/opencode-dcp" ~/.config/opencode/opencode.json`)
-- [ ] DCP loads: `opencode plugin list` shows `@tarquinen/opencode-dcp`, `/dcp` panel opens, `~/.config/opencode/dcp.jsonc` created on first run (project `.opencode/dcp.jsonc` overrides if present)
-- [ ] worktrees: OpenChamber native via sidebar/dialog (`https://docs.openchamber.dev/worktrees/`) — no `owt` required; if owt reinstalled, `owt help` + `~/.config/opencode/plugins/worktree-plugin.js` + `/init-worktree` after restart
-- [ ] (optional) OpenChamber: if user requested multi-device, `npm list -g @openchamber/web` shows 2.x, `openchamber status` password:yes, `ss -tlnp | grep 3005` shows `100.82.29.19:3005` (not 0.0.0.0), `curl http://100.82.29.19:3005/ → 200` / public `194.76.154.73:3005 → refused`, `openchamber startup status` shows enabled+active+lingering, `docs/openchamber-tailscale.md` present; if not requested, this check is N/A
+- [ ] repo `opencode.json`, global `opencode.json`, and global `cli.json` carry **no `plugins` entries** (this platform uses no OpenCode plugins)
+- [ ] `opencode plugin list` shows no goal/dcp entries
+- [ ] worktrees: OpenChamber native via sidebar/dialog (`https://docs.openchamber.dev/worktrees/`) — no plugin required
+- [ ] (optional) OpenChamber: if installed, `npm list -g @openchamber/web` shows 2.x, `openchamber status` password:yes, `openchamber startup status` shows enabled+active+lingering, `docs/openchamber.md` present; if not requested, this check is N/A
 - [ ] `~/.config/opencode/opencode.json` all 7 `mcp` entries are `type: "remote"` loopback URLs (8101 lint, 8102 context, 8103 memory, 8104 decisions, 8105 brain, 8106 telegram timeout 30000, 8107 blowsh timeout 120000) served by the supervised singletons — no stdio/`uv run` entries remain
 - [ ] `~/.config/opencode/opencode-shell-strategy.md` exists (instructions file referenced by the `instructions` key)
 - [ ] `/tmp/cognitive-lead-hq` no longer exists
 - [ ] `docker pull ghcr.io/mokhtarabadi/blowsh-mcp:latest` succeeds (or `docker` not installed → blowsh stays disabled, document it)
 - [ ] `~/.config/opencode/mcp-telegram-server/main.py` exists if telegram enabled (`ls $HOME/.config/opencode/mcp-telegram-server/main.py`); otherwise server stays `enabled:false` and no crash
 - [ ] Telegram smoke check (only if `TELEGRAM_SESSION_STRING` set): `telegram_get_messages` or `list_accounts` returns without `No Telegram session configured`
-- [ ] No former browser MCP remains in configs: `grep -R "former-browser" opencode.json LLM.txt docs/ ~/.config/opencode/opencode.json ~/.agents/mcp.json` check described here validates that removal is complete (automated check in task 111 greps for the retired browser name)
+- [ ] `.env` is seeded (repo-root `.env` for CLI runs and `~/.config/opencode/.env` for the singleton services; `chmod 600`) — verify `grep -c BRAIN_API_KEY .env ~/.config/opencode/.env`
 - [ ] `docs/telegram-setup.md` exists and is linked from `README.md` and this file
 - [ ] Start each local MCP server to verify it launches without errors (direct venv form):
   ```bash
diff --git a/README.md b/README.md
index 3bb3f01..01c6bcc 100644
--- a/README.md
+++ b/README.md
@@ -479,22 +479,9 @@ To install them globally, run the `LLM.txt` auto-configuration script. Once inst
 opencode --agent cognitive-executor
 ```
 
-### OpenCode Plugins (goal + DCP)
+### OpenCode Plugins
 
-Both the repo (`opencode.json` + `tui.json`) and global (`~/.config/opencode/`) configs load two plugins:
-
-- **`@prevalentware/opencode-goal-plugin`** — `/goal` command with sidebar indicator, persistent state, idle continuation and plan-mode safety. Restored 2026-09-08 after the OpenChamber rollout; it coexists with OpenChamber Session Goals (TUI/CLI goals + web-UI Goals complement each other).
-- **`@tarquinen/opencode-dcp@latest`** (currently 3.2.0) — token saving via compress tool, deduplication and purge-errors.
-
-Opencode V2 reads `plugins` from `opencode.json` (server/tools) and from the single global `~/.config/opencode/cli.json` (terminal client) — keep the entries identical. V1 fallbacks (`plugin` in `opencode.json` + `tui.json`) are kept alongside until V1 is fully retired. V2 prefers `permission.shell` over `permission.bash` (both kept). Both plugins are verified V2-capable at their latest stable versions: `@prevalentware/opencode-goal-plugin@0.1.52` (upstream V2 port: PR #49 dual runtime shape + PR #58 task-recovery scoping, 2026-09-26) and `@tarquinen/opencode-dcp@3.2.0` (V2 `setup()` via `session` hooks; stable 3.2.0 is newest — the 3.2.x betas are stale experiments). Verify with `opencode plugin list` (source of truth; cache dirs under `~/.cache/opencode/packages/` are metadata-only). Upstream-issue policy: search open threads first (goal: prevalentWare/opencode-goal-plugin; DCP: Opencode-DCP/opencode-dynamic-context-pruning — V2 threads #627/#628/#631/#632 already active) and never file duplicates. Full install/verify steps live in `LLM.txt` §7.
-
-> Install both plugins globally, then verify the packages actually landed (config references alone do not install them) and restart OpenCode before using `/goal` or `/dcp-compress`:
->
-> ```bash
-> opencode plugin @prevalentware/opencode-goal-plugin --global
-> opencode plugin @tarquinen/opencode-dcp@latest --global
-> ls -d ~/.cache/opencode/packages/@tarquinen/opencode-dcp@latest ~/.cache/opencode/packages/@prevalentware/opencode-goal-plugin@latest && echo "plugins installed ✓"
-> ```
+None. This platform runs OpenCode with **no plugins**; goal tracking comes from OpenChamber's built-in Session Goals and compaction is native to OpenCode V2.
 
 ---
 
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 724f71c..3e036fd 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -94,7 +94,7 @@ To prevent hallucinations and respect hidden project constraints, you MUST integ
 
 ## Capability Preflight (session start)
 
-Before approval-sensitive work (plan approval, review approval, closure), check the capability manifest: every `brain_turn` prints a `capability-manifest:` diagnostic line to stderr mapping each required tool to `AVAILABLE`, `UNAVAILABLE_REQUIRED`, or `UNAVAILABLE_OPTIONAL`. A step whose required tool is `UNAVAILABLE_REQUIRED` (for example the `question` tool) is never silently skipped. Emit the relay block the turn returned (missing tool names, stage, one narrow question, one answer slot) through the mode-appropriate channel: manual mode relays it to the Manager verbatim and pauses with the relayed question as the named blocker; autopilot replays it against stored manager decisions, and halts with the relay block as the named blocker only when no ruling covers it. Approval collection follows the single approval rule: closure accepts only the exact phrases "Approved for closure" or "Close task" (a bare "approved" never counts); the plan gate accepts "approved" in any case. Blanket acknowledgements ("ok", "yes", "looks good", emoji) never count as approval at any gate. At plan-approval, PO_REVIEW_PENDING relay, and any closure approval gate you MUST collect the decision via the question tool with one narrow question and one answer slot. Prose-only approval asks are forbidden because the goal-plugin loop rolls past prose. This holds in manual and autopilot. If question is UNAVAILABLE_REQUIRED, emit the relay block and pause with it as the named blocker; never skip. Only hard blockers may use prose.
+Before approval-sensitive work (plan approval, review approval, closure), check the capability manifest: every `brain_turn` prints a `capability-manifest:` diagnostic line to stderr mapping each required tool to `AVAILABLE`, `UNAVAILABLE_REQUIRED`, or `UNAVAILABLE_OPTIONAL`. A step whose required tool is `UNAVAILABLE_REQUIRED` (for example the `question` tool) is never silently skipped. Emit the relay block the turn returned (missing tool names, stage, one narrow question, one answer slot) through the mode-appropriate channel: manual mode relays it to the Manager verbatim and pauses with the relayed question as the named blocker; autopilot replays it against stored manager decisions, and halts with the relay block as the named blocker only when no ruling covers it. Approval collection follows the single approval rule: closure accepts only the exact phrases "Approved for closure" or "Close task" (a bare "approved" never counts); the plan gate accepts "approved" in any case. Blanket acknowledgements ("ok", "yes", "looks good", emoji) never count as approval at any gate. At plan-approval, PO_REVIEW_PENDING relay, and any closure approval gate you MUST collect the decision via the question tool with one narrow question and one answer slot. Prose-only approval asks are forbidden because an auto-continue loop can roll past prose. This holds in manual and autopilot. If question is UNAVAILABLE_REQUIRED, emit the relay block and pause with it as the named blocker; never skip. Only hard blockers may use prose.
 
 ## Subagent Delegation for Context Discovery
 
diff --git a/plugins/rate-limit-rescue/README.md b/archive/rate-limit-rescue/README.md
similarity index 96%
rename from plugins/rate-limit-rescue/README.md
rename to archive/rate-limit-rescue/README.md
index 6877605..20882f8 100644
--- a/plugins/rate-limit-rescue/README.md
+++ b/archive/rate-limit-rescue/README.md
@@ -9,7 +9,7 @@ On a free-tier 429-class failure it:
 
 1. Runs the env-configured command (default `~/.local/bin/rr` — rotates the balancer node).
 2. Appends one JSONL metrics line (default `~/.local/share/opencode/ratelimit-metrics.jsonl`), tagged `kind: "quota"` or `kind: "transport"`.
-3. Overrides the wait to 30s (`event.decision = { retry: true, delay: 30_000 }`).
+3. Overrides the wait to 2s (`event.decision = { retry: true, delay: 2_000 }`).
 
 It also rescues transient transport faults (`ECONNRESET`, socket hang-up/closed,
 `ETIMEDOUT`, `EPIPE`) the same way — these are proxy/node faults where `rr`
diff --git a/plugins/rate-limit-rescue/index.js b/archive/rate-limit-rescue/index.js
similarity index 97%
rename from plugins/rate-limit-rescue/index.js
rename to archive/rate-limit-rescue/index.js
index 10fc53a..7fb865d 100644
--- a/plugins/rate-limit-rescue/index.js
+++ b/archive/rate-limit-rescue/index.js
@@ -15,7 +15,7 @@ try {
 
 // Free-tier 429 rescue (Task 282). SCOPE: free-tier rate limits ONLY.
 // Every other error passes through untouched.
-const RETRY_DELAY_MS = 30_000
+const RETRY_DELAY_MS = 2_000
 
 export function isFreeTierLimit(error, model) {
   if (!error) return false
@@ -38,7 +38,7 @@ export function isFreeTierLimit(error, model) {
 
 // Transient transport failures (explicit Manager order 2026-09-29): e.g.
 // "ECONNRESET: The socket connection was closed unexpectedly". These are
-// proxy/node faults, not quota — rr rotation is the fix, same 30s retry.
+// proxy/node faults, not quota — rr rotation is the fix, same 2s retry.
 export function isTransportFault(error) {
   if (!error) return false
   const hay = `${error.message ?? ""} ${error.type ?? ""} ${error.code ?? ""} ${error.name ?? ""}`.toLowerCase()
@@ -75,7 +75,7 @@ export async function handleRetry(event, options) {
   if (!quota && !transport) return "pass"
   const cfg = resolveConfig(options)
   // Never let observability break the retry: command/metrics failures are
-  // recorded but the 30s decision is always set on a free-tier match.
+  // recorded but the 2s decision is always set on a free-tier match.
   let cmdResult = { ok: false, code: -1, stdout: "", stderr: "hook-guard" }
   try {
     cmdResult = await runCommand(cfg.command)
diff --git a/plugins/rate-limit-rescue/package-lock.json b/archive/rate-limit-rescue/package-lock.json
similarity index 100%
rename from plugins/rate-limit-rescue/package-lock.json
rename to archive/rate-limit-rescue/package-lock.json
diff --git a/plugins/rate-limit-rescue/package.json b/archive/rate-limit-rescue/package.json
similarity index 74%
rename from plugins/rate-limit-rescue/package.json
rename to archive/rate-limit-rescue/package.json
index ba68463..a62433b 100644
--- a/plugins/rate-limit-rescue/package.json
+++ b/archive/rate-limit-rescue/package.json
@@ -1,7 +1,7 @@
 {
   "name": "rate-limit-rescue",
   "version": "1.0.0",
-  "description": "Free-tier 429 rescue: runs the env-configured command, logs JSONL metrics, retries after 30s. All other errors untouched.",
+  "description": "Free-tier 429 rescue: runs the env-configured command, logs JSONL metrics, retries after 2s. All other errors untouched.",
   "type": "module",
   "main": "./index.js",
   "dependencies": {
diff --git a/plugins/rate-limit-rescue/test.mjs b/archive/rate-limit-rescue/test.mjs
similarity index 89%
rename from plugins/rate-limit-rescue/test.mjs
rename to archive/rate-limit-rescue/test.mjs
index f016213..0ea438c 100644
--- a/plugins/rate-limit-rescue/test.mjs
+++ b/archive/rate-limit-rescue/test.mjs
@@ -7,7 +7,7 @@ const FREE = { providerID: "opencode", id: "muse-spark-1.3-contributor-free" }
 const PAID = { providerID: "anthropic", id: "paid-model" }
 const TMP = "/tmp/rlr-test-metrics.jsonl"
 
-test("exact log shape on free model is rescued with 30s delay", async () => {
+test("exact log shape on free model is rescued with 2s delay", async () => {
   await rm(TMP, { force: true })
   const event = {
     error: { message: "Rate limit exceeded. Please try again later." },
@@ -16,10 +16,10 @@ test("exact log shape on free model is rescued with 30s delay", async () => {
     model: FREE,
   }
   assert.equal(await handleRetry(event, { command: "echo rotated", metricsPath: TMP }), "rescued")
-  assert.equal(event.decision.delay, 30_000)
+  assert.equal(event.decision.delay, 2_000)
   const line = JSON.parse(await readFile(TMP, "utf8"))
   assert.equal(line.modelID, FREE.id)
-  assert.equal(line.retryDelayMs, 30_000)
+  assert.equal(line.retryDelayMs, 2_000)
   assert.equal(line.commandOk, true)
 })
 
@@ -44,7 +44,7 @@ test("paid model 429 passes untouched", async () => {
   assert.equal(await handleRetry(event, {}), "pass")
 })
 
-test("command failure still sets the 30s decision", async () => {
+test("command failure still sets the 2s decision", async () => {
   const event = {
     error: { status: 429, message: "free tier quota hit" },
     attempt: 1,
@@ -52,10 +52,10 @@ test("command failure still sets the 30s decision", async () => {
     model: FREE,
   }
   assert.equal(await handleRetry(event, { command: "false", metricsPath: TMP }), "rescued")
-  assert.equal(event.decision.delay, 30_000)
+  assert.equal(event.decision.delay, 2_000)
 })
 
-test("unwritable metrics path still sets the 30s decision", async (t) => {
+test("unwritable metrics path still sets the 2s decision", async (t) => {
   // A regular file as parent dir fails fast (ENOTDIR). NOTE: never use /proc
   // here — recursive mkdir under /proc hangs at kernel level (found 2026-09-29).
   const parent = "/tmp/rlr-parent-file"
@@ -67,7 +67,7 @@ test("unwritable metrics path still sets the 30s decision", async (t) => {
     model: FREE,
   }
   assert.equal(await handleRetry(event, { command: "echo ok", metricsPath: `${parent}/child.jsonl` }), "rescued")
-  assert.equal(event.decision.delay, 30_000)
+  assert.equal(event.decision.delay, 2_000)
 })
 
 test("env overrides resolve", () => {
@@ -103,7 +103,7 @@ test("ECONNRESET transport fault is rescued with kind=transport", async () => {
     model: FREE,
   }
   assert.equal(await handleRetry(event, { command: "echo rotated", metricsPath: "/tmp/rlr-t.jsonl" }), "rescued")
-  assert.equal(event.decision.delay, 30_000)
+  assert.equal(event.decision.delay, 2_000)
   const line = JSON.parse(await readFile("/tmp/rlr-t.jsonl", "utf8"))
   assert.equal(line.kind, "transport")
 })
diff --git a/docs/brain-bridge.md b/docs/brain-bridge.md
index 826e03d..6ebb0d6 100644
--- a/docs/brain-bridge.md
+++ b/docs/brain-bridge.md
@@ -88,6 +88,12 @@ helper and is not a public tool.
 
 ## Environment
 
+These variables are read from the server's self-loaded `.env` (search
+order `<server-dir>/.env` → `<server-dir>/../.env` → `<cwd>/.env`; for the
+global install that is **`~/.config/opencode/.env`**, for repo runs the
+repo-root `.env`). Real process env wins; blank counts as unset. See
+`docs/services.md` §Credentials.
+
 | Variable            | Default                                              |
 | ------------------- | ---------------------------------------------------- |
 | `BRAIN_API_BASE`    | _(Manager-owned endpoint, e.g. local proxy URL)_     |
diff --git a/docs/openchamber-tailscale.md b/docs/openchamber-tailscale.md
deleted file mode 100644
index e823985..0000000
--- a/docs/openchamber-tailscale.md
+++ /dev/null
@@ -1,117 +0,0 @@
-# OpenChamber over Tailscale — Setup & Usage (this workstation)
-
-> Live since 2026-09-08. Server: `vm15996266` (loopback `127.0.0.1:3005` for Cloudflare Tunnel + Tailscale via `openchamber.surfshield.org`), port **3005**.
-> Cloudflare Tunnel active 2026-09-19: `openchamber.surfshield.org` → `http://127.0.0.1:3005` via host-native `cloudflared` (system `cloudflared.service` v2026.9.1). Tailscale direct `100.82.29.19:3005` retired 2026-09-19 in favor of loopback for tunnel — see §7.
-
-## 1. What is running
-
-- **OpenChamber 2.0.2** (global npm: `@openchamber/web`, upgraded 2026-09-26 from 1.24.2), daemon PID varies — check with `openchamber status`.
-  - Web UI: `127.0.0.1:3005` (loopback bind `--host 127.0.0.1`; Tailscale IP `100.82.29.19:3005` and public `194.76.154.73:3005` are **refused** — not `0.0.0.0`). Access locally via `http://127.0.0.1:3005`, remotely via Cloudflare `https://openchamber.surfshield.org` (tunnel → `127.0.0.1:3005`) — see §3-4. Legacy Tailscale `100.82.29.19:3005` retired 2026-09-19.
-  - External OpenCode server (stability fix 2026-09-10): `opencode-server.service` (systemd user unit, `~/.config/systemd/user/opencode-server.service`) runs `/home/mohammad/.opencode/bin/opencode serve --hostname 127.0.0.1 --port 4096` — **loopback-only**, `Restart=on-failure`, enabled at boot. OpenChamber attaches via drop-in `~/.config/systemd/user/openchamber.service.d/external-opencode.conf` (`OPENCODE_HOST=http://127.0.0.1:4096`, `OPENCODE_SKIP_START=true`, `After=opencode-server.service`). Why: the OpenChamber-supervised managed server stalled its event loop every few hours (all 5 MCPs `server unavailable` simultaneously, watchdog restarts 3×/24h — see §2c). Community-proven path (upstream issue #2258: 3 days stable). Rollback: delete the drop-in, `daemon-reload`, restart openchamber → back to managed.
-  - Managed OpenCode (OLD, pre-2026-09-10): auto-started by OpenChamber on a dynamic loopback port — replaced by the external server above.
-  - UI password: enabled. Secret lives ONLY in `~/.secrets/openchamber-ui-password` (`chmod 600`). Never committed.
-  - Auto-start at boot: `systemctl --user is-enabled openchamber` → `enabled`, `loginctl show-user mohammad | grep Linger` → `Linger=yes`, `Restart=always` (`RestartSec=5`). Survives reboot & logout; crash → restart in 5s. Check with `openchamber startup status` + `systemctl --user is-active openchamber`.
-- **Default :3000 is NOT OpenChamber** — it is the pre-existing Next.js (fa/en) app. **:8080 is code-server.** Do not move OpenChamber onto either.
-- **Plugins:** opencode plugin entries (global `~/.config/opencode/opencode.json` + global `cli.json` with V1 `tui.json` fallback, repo `opencode.json` with V1 `tui.json` fallback) are **goal + DCP** (`@prevalentware/opencode-goal-plugin` + `@tarquinen/opencode-dcp@latest`). Goal plugin **restored 2026-09-08** — it coexists with OpenChamber Session Goals (`/goal` in TUI/CLI + OpenChamber Goals in web UI complement each other, no conflict). Global `cli.json` mirrors `tui.json` for Opencode V2 compat. No project `cli.json` exists by design. (`permission.shell` mirrors `permission.bash` in `opencode.json`). **Worktree plugin `owt` (`@nano-step/opencode-worktree-plugin`) fully removed 2026-09-08** (`npm uninstall -g` + deleted `plugins/worktree-plugin.js` + 7 `command/*.md`; was `*.disabled` before removal). Reason: OpenChamber provides native worktrees (https://docs.openchamber.dev/worktrees/ + https://docs.openchamber.dev/multi-run/ — UI new-worktree dialog, isolate runs ≤5, Fusion, Git view → Integrate) — owt is redundant when OpenChamber is running. Reinstall only for CLI/headless without OpenChamber: `npm install -g @nano-step/opencode-worktree-plugin && owt-setup install` (see `LLM.txt §7.8`).
-
-## 2. Daily commands (on the server, as `mohammad`)
-
-```bash
-openchamber status                        # running runtimes (expect: port 3005, password: yes)
-curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3005/     # expect 200 (Tailscale IP; use this locally too)
-curl -s -m 5 -o /dev/null -w "%{http_code}\n" http://194.76.154.73:3005/ && echo "PUBLIC STILL OPEN" || echo "public refused (good)"
-# note: http://100.82.29.19:3005/ is now refused when bound to loopback — expected (use 127.0.0.1)
-timeout 8 openchamber logs -p 3005 | head -n 30   # recent log (logs cmd follows; always wrap in timeout)
-export OPENCHAMBER_UI_PASSWORD="$(cat ~/.secrets/openchamber-ui-password)"  # password via env, avoids ps exposure
-openchamber startup status                # startup enabled, service active, lingering enabled
-systemctl --user is-active openchamber   # should be active
-systemctl --user is-active opencode-server # external OpenCode server (see §2c)
-curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:4096/session     # expect 200 (loopback only)
-systemctl --user show-environment | tr ' ' '\n' | grep ^PATH=  # must contain mise shims, else uv MCPs can't spawn (see §2c)
-openchamber stop --port 3005              # stop this instance (systemd will restart in 5s due to Restart=always)
-openchamber update                        # update OpenChamber later
-```
-
-### 2b. Auto-start at boot (systemd user service)
-
-- Enabled via `export OPENCHAMBER_UI_PASSWORD="$(cat ~/.secrets/openchamber-ui-password)" && openchamber startup enable --port 3005 --host 127.0.0.1` (was `--host 100.82.29.19` Tailscale-only until 2026-09-19; now loopback for Cloudflare Tunnel — see §7) → writes `~/.config/systemd/user/openchamber.service` (`ExecStart=... serve --foreground --port 3005 --host 127.0.0.1` (was `100.82.29.19` until 2026-09-19), `Restart=always`, `RestartSec=5`).
-- Lingering via `sudo loginctl enable-linger mohammad` → `loginctl show-user mohammad` shows `Linger=yes`, `State=active` — user manager starts at boot even without login.
-- Verification: `openchamber startup status` → `startup enabled`, `service active`, `user lingering enabled`; `systemctl --user is-enabled openchamber` → `enabled`; `systemctl --user is-active openchamber` → `active`; `ss -tlnp | grep 3005` → `127.0.0.1:3005` LISTEN; reboot → auto-starts, crash → restarts in 5s (`NRestarts` stays 0 when stable).
-- Re-enable after password change: repeat the `startup enable` command (it rewrites `startup.env` with the new password) — do **not** hand-edit `startup.env`/`jwt-secret` (both `600`).
-
-### 2c. External OpenCode server (stability fix 2026-09-10 — replaces managed server)
-
-- **Why:** the OpenChamber-supervised managed `opencode serve` stalled its event loop every few hours of multi-session use — all 5 MCPs went `server unavailable` simultaneously (first wave `2026-09-10T00:00:25Z`, 5,550 retry lines over ~9h), no OOM/crash, watchdog (`Restarting OpenCode process...` + `TimeoutError`/WS `ECONNREFUSED`) fired 3× in 24h (Sep 9 14:01, 16:13; Sep 10 11:15). Failure is in opencode's MCP client layer, not the Python servers. Community-proven path: upstream issue [#2258](https://github.com/openchamber/openchamber/issues/2258) — external serve + `OPENCODE_SKIP_START` → 3 days stable. Related: [#3434](https://github.com/openchamber/openchamber/issues/3434) (reconnect flood, fix PR [#2783](https://github.com/openchamber/openchamber/pull/2783) unmerged) and [#1295](https://github.com/openchamber/openchamber/issues/1295) (old health-check false positives, already fixed).
-- **Unit:** `~/.config/systemd/user/opencode-server.service` → `ExecStart=/home/mohammad/.opencode/bin/opencode serve --hostname 127.0.0.1 --port 4096`, `WorkingDirectory=/home/mohammad`, `Restart=on-failure`, `RestartSec=10`, enabled at boot (`WantedBy=default.target`). **Loopback-only by design** — OpenChamber reaches it locally; remote devices go through OpenChamber :3005, never to :4096 directly.
-- **PATH (why services don't see `.bashrc`):** systemd user units never read `~/.bashrc` (non-interactive — no shell is ever spawned; upstream: https://wiki.archlinux.org/title/Systemd/User). So `~/.config/environment.d/zz-shell-path.conf` pins the full interactive-shell PATH manager-wide (mise shims, `~/.local/bin`, `~/.opencode/bin`, Android SDK, system). The `zz-` prefix is load-bearing: `/usr/lib/environment.d/99-*.conf` + `990-snapd.conf` reset PATH afterwards, so anything sorting earlier loses (verified via the `30-systemd-environment-d-generator` debug output). Rejected: `import-environment` (lost on reboot), `bash -lc` wrappers (fragile), `PAMName=login` (heavy). After PATH changes: `systemctl --user set-environment PATH=...` (running manager) + `daemon-reload`; verify with `systemctl --user show-environment | tr ' ' '\n' | grep ^PATH=`. Regenerate the pinned value with `bash -ic 'echo $PATH' 2>/dev/null`.
-- **Wiring:** drop-in `~/.config/systemd/user/openchamber.service.d/external-opencode.conf` sets `OPENCODE_HOST=http://127.0.0.1:4096` + `OPENCODE_SKIP_START=true` + `After=opencode-server.service` (ordering only). Takes effect on next openchamber restart. Rollback: delete the drop-in file, `systemctl --user daemon-reload`, restart openchamber → managed server returns.
-- **Verify:** `systemctl --user is-active opencode-server` → `active`; `ss -ltn | grep 4096` → `127.0.0.1:4096` ONLY (never `0.0.0.0`); authenticated info check → `200` (see §2c-password below — unauthenticated `/api/*` correctly returns `401` on V2); `journalctl --user -u opencode-server` shows `server listening on http://127.0.0.1:4096`.
-- **Restart order (both):** `systemctl --user restart opencode-server` first, then `systemctl --user restart openchamber` (chamber re-attaches on boot via `After=`). During the switch window two opencode processes briefly coexist — telegram MCP shared-lock mode (upstream v3.2.33) covers the overlap.
-- **Ownership note:** OpenChamber updates (`openchamber update`) no longer restart your OpenCode server; `opencode` binary updates via `~/.opencode/bin` as before, then `restart opencode-server`. OpenCode V2 itself upgrades via `curl -fsSL https://opencode.ai/v2/install | bash` (replaces the V1 binary in place).
-
-### 2c-password. V2 server-password sync (401 fix 2026-09-26 — REQUIRED in external mode)
-
-- **Why:** V2 `opencode serve` mints a random Basic-auth password every boot unless `OPENCODE_PASSWORD`/`OPENCODE_SERVER_PASSWORD` is set. OpenChamber authenticates with `OPENCODE_SERVER_PASSWORD` from its own env (`startup.env`). Any mismatch → `Startup failed / OpenCode info endpoint responded with status 401`, `PushWatcher disconnected / upstream_unavailable` floods, UI shows sessions but no OpenCode.
-- **Fix (one stable password, both sides):** `~/.config/opencode/.server-password` (`chmod 600`, generated once) → pinned on the server via drop-in `~/.config/systemd/user/opencode-server.service.d/10-password.conf` (`Environment=OPENCODE_SERVER_PASSWORD=<value>`) → same value as the `OPENCODE_SERVER_PASSWORD="..."` line in `~/.config/openchamber/startup.env` (this line wins over drop-ins, so the startup.env edit is load-bearing, not the drop-in).
-- **After ANY `openchamber startup enable`** (it rewrites `startup.env`): re-apply the password line from `~/.config/opencode/.server-password`, `daemon-reload`, restart both services (USER action). Never rotate the password file without re-syncing both sides.
-- **Verify:** `journalctl --user -u openchamber -n 20 | grep -c 'status: 401'` → `0`; fresh logs show `[PushWatcher] connected`; authenticated `curl -u opencode:<password> http://127.0.0.1:4096/api/info` → `200`. Full steps: `LLM.txt §7.9` password-sync.
-
-### 2d. Outbound proxy for opencode-server via mihomo-subs (2026-09-23)
-
-- **Why:** route all outbound LLM API traffic through the `mihomo-subs` pool (`127.0.0.1:7890`, 53 free-pool nodes, 6h refresh) instead of direct egress.
-- **How:** OpenCode respects standard proxy env vars (upstream: https://opencode.ai/docs/network). Set as `Environment=` lines in `~/.config/systemd/user/opencode-server.service` (NOT in `~/.config/opencode/.env` — that file is for secrets/keys; the proxy URL is non-secret loopback config):
-  `HTTP_PROXY=http://127.0.0.1:7890`, `HTTPS_PROXY=http://127.0.0.1:7890` (plain `http://` scheme — 7890 is a mixed HTTP+SOCKS port, TLS to providers is tunnelled via CONNECT), `NO_PROXY=localhost,127.0.0.1,::1` **required** (server/TUI loopback `:4096` must bypass the proxy or you get a routing loop), plus lowercase twins (`http_proxy`/`https_proxy`/`no_proxy`) for the Bun/Node runtime.
-- **Apply:** `systemctl --user daemon-reload && systemctl --user restart opencode-server.service`. Verify env on the live process: `tr '\0' '\n' < /proc/$(systemctl --user show -p MainPID --value opencode-server.service)/environ | grep -i proxy` (all six vars). Health: `curl http://127.0.0.1:4096/` still direct (NO_PROXY working); proxy itself: `curl -x http://127.0.0.1:7890 https://www.gstatic.com/generate_204` → `204`.
-- **Rollback:** delete the six `Environment=` lines, `daemon-reload`, restart → direct egress returns.
-
-### 2e. Free models via local zen-proxy provider (A3 result 2026-09-27)
-
-- **Setup:** `~/.local/share/zen-proxy/proxy.py` (native revival of the archived sidecar) + provider `zen-proxy` in `~/.config/opencode/opencode.json` (`npm: @ai-sdk/openai-compatible`, `baseURL: http://127.0.0.1:8081/zen/chat`, `apiKey: {env:ZEN_API_KEY}` — key added to the daemon `~/.config/opencode/.env` for substitution). Use: `opencode run --model zen-proxy/mimo-v2.5-free "..."` (free chat models: `big-pickle`, `ling-3.0-flash-fin-free`, `mimo-v2.5-free`, `nemotron-3-ultra-free`, `nemotron-3.5-lightning-free`).
-- **Proxy patches required** (live copy only — archive stays pristine): (1) forward genuine client-minted headers (`x-opencode-client/request/project`, `x-session-id/affinity`, `opencode/...` UA) instead of always stamping Chrome UA + static session; (2) map upstream `URLError` (dirty pool node, cert refused fail-closed) to `502 BadGatewayError` JSON instead of dropping the socket (the AI SDK reported it as `Transport: socket closed unexpectedly`).
-- **Gate finding (case closed):** free-tier 403 is a server-side live-session check, not headers/key/IP — proven by elimination (two valid keys, full header replays incl. UA `opencode/latest/2.0.18/cli`, direct egress, all 403) plus the decisive pair: real client through proxy → 200 `proxy-path-ok` 3/3, while curl with freshly minted real-shaped IDs (`ses_`+22alnum, 32-hex project) → 403. Only server-known live session IDs pass. Consequence: no proxy patch and no Node/Bun rewrite can ever make non-client callers (curl, Open WebUI) use free tier — the proxy cannot mint server-known sessions. Keep the provider for real-client use; use paid/Go paths for automation.
-- **RETIRED 2026-09-27:** proxy stopped + disabled, live copy and unit removed (`:8081` closed), provider block removed from `opencode.json`. Patched files + full story archived at `code-server/archive/zen-proxy-native-2026-09-27/` (proxy.py, unit, README with revive steps). `ZEN_API_KEY` stays in daemon `.env` for a future revive.
-
-## 3. Connect from a PC (mohammad-pc-1 / cando — Tailscale)
-
-1. Join the same tailnet on the PC (`tailscale status` must show `vm15996266`).
-2. Open `https://openchamber.surfshield.org/` (Cloudflare Tunnel → `127.0.0.1:3005`) in the browser, or `http://127.0.0.1:3005/` locally. Legacy `http://100.82.29.19:3005` is refused after 2026-09-19. Enter the UI password (ask the server owner; it is in `~/.secrets/` on the server only).
-3. Recommended: pair properly instead of password-every-time —
-   on the server run `openchamber connect-url --port 3005 --server https://openchamber.surfshield.org --qr` (was `http://100.82.29.19:3005` until 2026-09-19),
-   then in OpenChamber Desktop use *Settings → Remote Instances → Direct Instances → Import Link* (or scan QR from mobile). Links are **single-use and expire** — generate a fresh one per device.
-4. Desktop app can then switch between direct (Tailscale) and Relay transports; green dot = connected.
-
-## 4. Connect from Android (redmi-note-13 / xiaomi-2312fpca6g — Tailscale)
-
-1. Install Tailscale from Play Store, log in to the same tailnet, or just open `https://openchamber.surfshield.org` via Cloudflare (no Tailscale needed externally); verify `tailscale status` if using Tailscale link.
-2. Option A (native): install the OpenChamber Android APK from `https://github.com/openchamber/openchamber/releases/latest`, open it, *Scan QR* from a fresh server-side `connect-url --qr` (Home-network scope is enough on Tailscale).
-3. Option B (no install): in Chrome open `http://100.82.29.19:3005/`, log in with the UI password, then *Install app / Add to Home Screen* (PWA).
-4. For away-from-home use, re-pair with **Anywhere** scope so the E2E Relay takes over when Tailscale direct is unreachable (server holds outbound to relay infra; no ports opened).
-
-## 5. Pairing & revoke discipline
-
-- One link per device; links expire after single use (~minutes). Never paste a link into chat/docs — it contains a secret.
-- Revoke a lost device: OpenChamber *Settings → Remote Instances* → *Revoke* (then *Clear revoked*). Rotate the UI password afterwards if it may have leaked: write the new value to `~/.secrets/openchamber-ui-password` (`chmod 600`), then `openchamber restart --port 3005` (or stop + start per §2).
-- Passkeys (*Settings → OpenChamber → Passkeys*) are optional hardening; note they clear on password change.
-
-## 6. Troubleshooting
-
-| Symptom | Check |
-|---|---|
-| Browser gets 307 → `/fa` on :3000 | You hit the Next.js app, not OpenChamber — use **:3005**. |
-| `curl` to :3005 hangs/refused | `openchamber status`; `ss -tlnp \| grep 3005` should show `127.0.0.1:3005` LISTEN; `curl http://127.0.0.1:3005/` → 200; public IP → refused is expected. |
-| `curl http://100.82.29.19:3005/` refused | Expected after 2026-09-19 — bound to loopback only (`127.0.0.1:3005`). Use `http://127.0.0.1:3005/` locally or `https://openchamber.surfshield.org` remotely. |
-| Startup not starting at boot | `systemctl --user is-enabled openchamber` → `enabled`; `loginctl show-user mohammad | grep Linger` → `yes`; `systemctl --user status openchamber`; `journalctl --user -u openchamber -n 30`. Re-enable: `export OPENCHAMBER_UI_PASSWORD="$(cat ~/.secrets/openchamber-ui-password)" && openchamber startup enable --port 3005 --host 127.0.0.1` + `sudo loginctl enable-linger mohammad`. |
-| Tailscale IP unreachable from phone/PC | `tailscale status` both ends; `tailscale ping 100.82.29.19`; ensure Tailscale is up (not logged out). |
-| Chat/notifications stall | Check `timeout 8 openchamber logs -p 3005`; external OpenCode `:4096` must stay loopback (authenticated `/api/info` → 200, see §2c-password); restart order: `opencode-server` then `openchamber` (see §2c). |
-| OpenChamber "Startup failed / status 401" | Server/client password mismatch (V2 randomizes per boot) — re-sync per §2c-password, restart both, expect `[PushWatcher] connected` and zero `status: 401` lines. |
-| All MCP tools unavailable to AI at once | Known managed-server stall (pre-§2c): every session logs `server unavailable` ×5 every 30s. Check `systemctl --user is-active opencode-server` + `:4096` health; restart both per §2c. If it recurs on the external server, capture `journalctl --user -u opencode-server` + RSS trend (`ps -o pid,etime,%mem,rss -C opencode`) for an upstream issue. |
-| High RAM (7.8GB host) | `free -h`; `docker stats`; stop idle OpenChamber sessions; blowsh MCP pulls a Docker image per use. |
-| `/init-worktree` does nothing | Expected — worktree plugin `owt` was removed 2026-09-08 (OpenChamber native worktrees via UI; see §1 + `LLM.txt §7.8`). Reinstall only if you need CLI/headless without OpenChamber. |
-
-## 7. Security notes
-
-- Loopback bind `--host 127.0.0.1` (since 2026-09-19, was `--host 100.82.29.19` until 2026-09-19): `ss -tlnp` shows `127.0.0.1:3005` not `0.0.0.0:3005`; public IP `194.76.154.73:3005` → refused, Tailscale IP `100.82.29.19:3005` → refused — only loopback + Cloudflare Tunnel `openchamber.surfshield.org` can reach it (`mmokhtarabadi@gmail.com` tailnet, 5 peers) can reach it. Prior `0.0.0.0` bind was publicly reachable and has been hardened.
-- Secrets: `~/.secrets/openchamber-ui-password` (`600`), `~/.config/openchamber/jwt-secret` (`600`), `~/.config/openchamber/startup.env` (`600`, contains password for systemd — never committed). UI password stays ON, pairing links stay single-use and expire, passkeys clear on password change.
-- Auto-start: `openchamber.service` `enabled` + `Linger=yes` + `Restart=always` — survives reboot/logout/crash; verify with `openchamber startup status` and `systemctl --user is-active openchamber`.
-- Cloudflare Tunnel active 2026-09-19: host-native `cloudflared` system service (`cloudflared.service` v2026.9.1, token `/etc/cloudflared/token`) proxies `https://openchamber.surfshield.org` → `http://127.0.0.1:3005` and `https://code.surfshield.org` → `http://127.0.0.1:8080`. See `docs/cloudflared.md`. Do NOT run a Quick tunnel with the real password for anything but a smoke test.
-- External OpenCode `:4096` is loopback-only (`127.0.0.1:4096`, never `0.0.0.0`) — not reachable via Tailscale or public IP by design; remote devices always go through OpenChamber `:3005`.
diff --git a/docs/openchamber.md b/docs/openchamber.md
new file mode 100644
index 0000000..b9d87d9
--- /dev/null
+++ b/docs/openchamber.md
@@ -0,0 +1,145 @@
+# OpenChamber (web workspace for OpenCode)
+
+> OpenChamber is the visual workspace that runs **on top of OpenCode**. Install
+> OpenCode first, then OpenChamber. OpenChamber starts and manages its own
+> OpenCode server — you do **not** run a separate `opencode serve` unit.
+>
+> Docs: https://docs.openchamber.dev — OpenCode V2 docs: https://opencode.ai/v2/docs/
+
+## 1. Versions
+
+| Component | Version | Update command | Source of truth |
+| --- | --- | --- | --- |
+| OpenCode | 2.0.21 | `curl -fsSL https://opencode.ai/v2/install \| bash` (V2) | `opencode --version`; latest via `https://opencode.ai/update/api/latest/cli/npm` |
+| OpenChamber | 2.1.0 | `openchamber update` | `openchamber --version`; latest via `npm view @openchamber/web version` |
+
+OpenChamber and OpenCode update **separately**. OpenChamber offers OpenCode
+updates in its UI and restarts the server afterward; you can also run the V2
+installer directly and let OpenChamber reconnect.
+
+## 2. Install
+
+```bash
+# 1. OpenCode first
+curl -fsSL https://opencode.ai/v2/install | bash
+opencode --version            # expect 2.x
+
+# 2. OpenChamber (Node >= 22)
+npm install -g @openchamber/web
+openchamber --version         # expect 2.x
+```
+
+## 3. Run
+
+OpenChamber starts and manages its own OpenCode server (managed mode). This is
+the supported default — no external server, no `OPENCODE_SKIP_START`, no extra
+systemd unit.
+
+```bash
+openchamber --ui-password "$(cat ~/.secrets/openchamber-ui-password)"
+# prints the URL (default http://127.0.0.1:3000)
+```
+
+Set the UI password from a `chmod 600` file so it never appears in `ps`:
+
+```bash
+mkdir -p ~/.secrets
+printf '%s' 'be-creative-here' > ~/.secrets/openchamber-ui-password
+chmod 600 ~/.secrets/openchamber-ui-password
+```
+
+### Server discovery order (from the docs)
+
+1. reuse a server it already started
+2. connect to an external one if configured (`OPENCODE_HOST` + `OPENCODE_SKIP_START=true`)
+3. auto-detect a server on the default port `4096`
+4. otherwise start and manage its own
+
+In managed mode you rely on step 4; nothing else is required.
+
+## 4. Start at boot (the supported way)
+
+Use OpenChamber's own startup integration — it writes the systemd user unit,
+snapshots the environment (PATH, tokens), and remembers `--port`, `--host`,
+`--ui-password`, and `--api-only`. Do **not** hand-author a custom unit.
+
+```bash
+export OPENCHAMBER_UI_PASSWORD="$(cat ~/.secrets/openchamber-ui-password)"
+openchamber startup enable --port 3005 --host 127.0.0.1
+openchamber startup status                 # startup enabled + service active
+sudo loginctl enable-linger mohammad       # start at boot without login
+```
+
+Notes:
+
+- `openchamber startup enable` snapshots the current environment into the
+  service (provider tokens, `PATH`, SSH agent). Use `--no-env-snapshot` for a
+  minimal environment.
+- Re-run `startup enable` after changing env vars or the UI password — it
+  rewrites `~/.config/openchamber/startup.env`.
+- Manage it with `openchamber startup {status,enable,disable}`; inspect with
+  `systemctl --user status openchamber`.
+- Uninstall: `openchamber startup disable` (stops + removes the service).
+
+## 5. Daily commands
+
+```bash
+openchamber status                      # running runtimes
+openchamber restart                     # restart server
+openchamber stop                        # stop server
+openchamber update                      # update OpenChamber
+openchamber logs                        # tail logs (wrap in `timeout` if following)
+openchamber startup status              # boot integration state
+openchamber connect-url --qr            # pairing link for another device
+```
+
+## 6. Remote access (optional)
+
+OpenChamber can be reached from other devices through a tunnel. Choose one:
+
+```bash
+openchamber tunnel start --port 3005    # ngrok-backed
+openchamber tunnel stop  --port 3005
+```
+
+Or put it behind a reverse proxy / Cloudflare Tunnel yourself. When binding
+beyond localhost, keep a strong UI password and prefer `--api-only` for
+headless clients:
+
+```bash
+openchamber startup enable --port 3005 --api-only --host 0.0.0.0
+```
+
+Locally reach it at `http://127.0.0.1:3005`; generate pairing links with
+`openchamber connect-url --port 3005 --server <public-url> --qr`. Links are
+single-use and expire.
+
+## 7. Environment variables (the ones that matter here)
+
+| Var | Purpose |
+| --- | --- |
+| `OPENCHAMBER_HOST` | Bind address for the web server (`0.0.0.0` for other machines). |
+| `OPENCHAMBER_UI_PASSWORD` | Browser UI password. |
+| `OPENCHAMBER_API_ONLY` | Headless mode (`true`/`1`) — API routes only. |
+| `OPENCHAMBER_DATA_DIR` | Data dir (default `~/.config/openchamber`). |
+| `OPENCODE_BINARY` | Path to the `opencode` binary OpenChamber runs. |
+| `OPENCODE_HOST` / `OPENCODE_PORT` / `OPENCODE_SKIP_START` | External-server mode only. Not used here. |
+
+Full list: https://docs.openchamber.dev/environment/
+
+## 8. Troubleshooting
+
+| Symptom | Check |
+| --- | --- |
+| UI does not load | `openchamber status`; open the URL it prints; confirm the port is listening (`ss -tlnp \| grep <port>`). |
+| "OpenChamber requires OpenCode 2.0.20 or newer" | Update OpenCode: `curl -fsSL https://opencode.ai/v2/install \| bash`, then restart OpenChamber. |
+| "OpenCode is restarting" never clears | OpenChamber pauses requests while the managed server starts; if stuck, `openchamber restart` and check `openchamber logs`. |
+| Not starting at boot | `openchamber startup status`; re-run `openchamber startup enable`; verify `loginctl show-user <user> \| grep Linger` → `yes`. |
+| Sessions visible but tools missing | Reconnect/restart; MCP servers must be reachable on their loopback ports (`docs/services.md`). |
+
+## 9. Relationship to the MCP servers
+
+OpenChamber serves the OpenCode server; OpenCode loads MCP servers from
+`~/.config/opencode/opencode.json` (`mcp.servers`). Installing those servers is
+covered in `LLM.txt` §5–§7 and `docs/services.md`. OpenChamber itself needs no
+MCP configuration.
diff --git a/docs/opencode-shell-strategy.md b/docs/opencode-shell-strategy.md
index a2c407e..14fdf96 100644
--- a/docs/opencode-shell-strategy.md
+++ b/docs/opencode-shell-strategy.md
@@ -142,7 +142,7 @@ All Git commit/add/push operations are strictly handled by the `custom_context_s
 **ZAC (Zero-Autonomous-Commit) precedence:** the Git reference table in section 5 is overridden for this platform. `git add`, `git commit`, and `git push` MUST NOT be executed by agents under any circumstances — even with non-interactive flags such as `git commit -m "msg"` or `git add <file>`; they are denied at the permission layer. `git mv` remains permitted ONLY for moving task files between Kanban directories (`backlog`, `in-progress`, `qa`, `completed`, `archive`). All other Git commands (status, diff, log, show, ls-files, grep, reset -- <path> for unstage) remain governed by the non-interactive rules in section 5 (`git --no-pager log`, `git diff`, etc.).
 
 **Denied commands (mirrors `opencode.json` permission layer).** The
-`permission.bash` block denies these for agents — the deny fires before
+`permission.shell` block denies these for agents — the deny fires before
 execution, so the command never runs:
 
 | Denied pattern | Covers |
diff --git a/docs/services.md b/docs/services.md
index 2b6402b..20e5f65 100644
--- a/docs/services.md
+++ b/docs/services.md
@@ -24,6 +24,43 @@ already running on this machine can reach them. Do not rebind to
 container `MCP_HOST=0.0.0.0` is required, but the published port stays
 `-p 127.0.0.1:8107:8107`.)
 
+## Credentials (`.env`) — how the servers read keys
+
+The Python servers (`context`, `memory`, `lint`, `decision`, `brain`) load
+`.env` themselves at import via `mcp_common.env.load_env_files`. Search
+order, **first file holding a key wins**:
+
+1. `<server-dir>/.env`
+2. `<server-dir>/../.env`
+3. `<cwd>/.env`
+
+Real process environment always wins over the file; an empty value counts
+as **unset** (so a blank `{env:}` injection never shadows a real file
+value).
+
+Consequence for the global singleton install (`<server-dir>` =
+`~/.config/opencode/mcp-*/`): the effective file is
+**`~/.config/opencode/.env`** (`<server-dir>/../.env`). For servers run
+straight from the repo, that is the repo-root `.env`. Telegram is
+third-party and reads its own `.env` in its install dir.
+
+Therefore the unit files need **no** `EnvironmentFile=` for `BRAIN_*` /
+`DECISION_*` / `TELEGRAM_*`; just keep the keys in the right `.env`:
+
+```bash
+# global install: seed once, keep chmod 600
+install -m 600 /path/to/repo/.env ~/.config/opencode/.env
+# or start from the template:
+# install -m 600 /path/to/repo/.env.example ~/.config/opencode/.env   # then edit keys
+```
+
+After changing any key, restart the affected unit
+(`systemctl --user restart mcp-brain mcp-decision mcp-telegram`).
+
+> Note: this is separate from OpenCode's own `{env:VAR}` forwarding for a
+> managed/daemon server — that concerns variables you want the OpenCode
+> process itself to see. The MCP servers above do not need it.
+
 ## How it works
 
 Each HQ Python server (lint, context, memory, decision, brain) reads
@@ -103,7 +140,10 @@ path for `{HOME}`); the inline template below shows the shape
 ```
 
 Load with `launchctl load ~/Library/LaunchAgents/mcp-<name>.plist`.
-Repeat for ports 8102-8106 with the matching server directory.
+Repeat for ports 8102-8106 with the matching server directory. Credentials
+are self-loaded by each server from `~/.config/opencode/.env`
+(`<server-dir>/../.env`) — no `EnvironmentVariables` entry is needed for
+`BRAIN_*`/`DECISION_*` (see the Credentials section above).
 
 ## Windows
 
@@ -120,6 +160,11 @@ GUI/NSSM alternative (also untested on Windows):
   then set `MCP_TRANSPORT` under the Environment tab. NSSM gives
   `Restart=always` equivalent behavior.
 
+Credentials (`BRAIN_*`/`DECISION_*`/`TELEGRAM_*`) are self-loaded by each
+server from `%USERPROFILE%\.config\opencode\.env`
+(`<server-dir>/../.env`); you do not need to set them in the task/service
+environment (see the Credentials section above).
+
 ## Verification
 
 ```bash
diff --git a/docs/setup.md b/docs/setup.md
index 1589bbb..e19aa27 100644
--- a/docs/setup.md
+++ b/docs/setup.md
@@ -65,25 +65,39 @@ Each unit launches its server via the persistent venv interpreter (`<dir>/.venv/
 > (`brain_turn`).
 > Global installs additionally run `blowsh` + `telegram`.
 
-### Systemd user service env
+### Environment: MCP servers vs the managed OpenCode server
 
-When OpenCode runs as a systemd user service (`opencode-server.service`),
-the daemon starts with a bare environment — no shell exports apply. Give
-it the project env explicitly so `{env:VAR}` forwarding in `opencode.json`
-resolves and the bridge/decision servers start with keys:
+Two separate env paths — don't mix them:
 
-```ini
-[Service]
-EnvironmentFile=-/home/mohammad/Develop/Projects/cognitive-lead-hq/.env
+**1. MCP servers self-load `.env`.** Each Python server reads
+`<server-dir>/.env` → `<server-dir>/../.env` → `<cwd>/.env` at import
+(first match wins; real process env wins over files; blank = unset). For a
+global install that effective file is **`~/.config/opencode/.env`**; for
+repo runs it is the repo-root `.env`. So keep `BRAIN_*`/`DECISION_*`/
+`TELEGRAM_*` in that file (`chmod 600`) and no unit needs an
+`EnvironmentFile=`. Full detail: `docs/services.md` §Credentials.
+
+```bash
+# seed/refresh the global MCP credentials file
+install -m 600 .env ~/.config/opencode/.env
+systemctl --user restart mcp-brain mcp-decision mcp-telegram   # after key changes
+```
+
+**2. The OpenChamber-managed OpenCode server** inherits the environment of
+the shell that started it. `openchamber startup enable` snapshots that env
+into the service, so export anything you want the OpenCode process itself
+to see (used by `{env:VAR}` forwarding) before enabling:
+
+```bash
+export DECISION_REPO_PATH="$HOME/Develop/Projects/manager-decisions"
+export OPENCHAMBER_UI_PASSWORD="$(cat ~/.secrets/openchamber-ui-password)"
+openchamber startup enable --port 3005 --host 127.0.0.1
 ```
 
-Portable form for other machines: `EnvironmentFile=%h/.config/opencode/.env`.
-After editing: `systemctl --user daemon-reload` (safe anytime), then
-`systemctl --user restart opencode-server` to take effect — the restart
-kills live sessions, so the manager runs it, never the Hands. Verify with
-`systemctl --user show opencode-server.service -p EnvironmentFiles`.
-As process env, these vars outrank every `.env` file fallback, so all
-projects served by the daemon share them.
+Re-run `openchamber startup enable` after changing any env var. If you run
+OpenCode as your own daemon instead, give that unit an `EnvironmentFile=`
+(e.g. `EnvironmentFile=%h/.config/opencode/.env`) and restart it; the
+manager runs that restart, never the Hands.
 
 ## Development Tools
 
diff --git a/docs/telegram-setup.md b/docs/telegram-setup.md
index f248598..4b7630a 100644
--- a/docs/telegram-setup.md
+++ b/docs/telegram-setup.md
@@ -55,6 +55,14 @@ For headless/runbook use pass `--qr` or `--phone` explicitly; without a flag the
 
 ## 4. Configure Environment
 
+> **Where this `.env` lives.** The Telegram server self-loads `.env` at
+> import (search order `<server-dir>/.env` → `<server-dir>/../.env` →
+> `<cwd>/.env`). When it runs as the global singleton
+> (`~/.config/opencode/mcp-telegram-server/`), the effective file is
+> **`~/.config/opencode/.env`**; when run from the repo clone it is the
+> repo-root `.env`. Keep it `chmod 600` and never commit it. See
+> `docs/services.md` §Credentials.
+
 ### 4.1 Single-account (personal)
 
 ```bash
diff --git a/docs/velocity.md b/docs/velocity.md
deleted file mode 100644
index 87a0182..0000000
--- a/docs/velocity.md
+++ /dev/null
@@ -1,23 +0,0 @@
-# Velocity Log
-
-Throughput record for the Cognitive Lead AI HQ repo. One row per closed
-task: suite size at close proves the harness keeps working while scope
-grows. Counts come from each task's `## Verification Evidence` and its
-`CHANGELOG.md` entry.
-
-| Task | Scope | Tests passing at close |
-| ---- | ----- | ---------------------- |
-| 230 | Manager-decision hardening | 98 |
-| 231 | Decision follow-up H1/H2/H3 | 101 |
-| 232 | Brain EMPTY_OUTPUT_RETRY hint | 345 |
-| 233 | Supervised autopilot plan-approval | 350 |
-| 234 | Brain sessions per project (+hotfix) | 357 |
-| 235 | Review-approval relay | n/a (release line, no suite delta claimed) |
-| 236 | Lean-retry state note | 357 |
-| 237 | opencode-init project-only contract | validator gates |
-| 238 fix loop | XML tolerance, tree boundary, roster, queue cap | 155 + 15 (targeted suites) |
-
-## Convention
-
-On every task close, the Hands appends one row (task id, one-line scope,
-suite count + exit code). No row, no close.
diff --git a/mcp-common/src/mcp_common/env.py b/mcp-common/src/mcp_common/env.py
index 8ebe5df..f49969f 100644
--- a/mcp-common/src/mcp_common/env.py
+++ b/mcp-common/src/mcp_common/env.py
@@ -1,7 +1,7 @@
 """Explicit `.env` file loading for MCP servers (Task 170, extracted).
 
-Single home for the loader previously duplicated in mcp-persona-server and
-mcp-decision-server. Standard library only — no third-party imports.
+Single home for the loader previously duplicated inside the servers.
+Standard library only — no third-party imports.
 """
 
 from __future__ import annotations
diff --git a/opencode.json b/opencode.json
index 456f47f..f6787da 100644
--- a/opencode.json
+++ b/opencode.json
@@ -1,10 +1,6 @@
 {
   "$schema": "https://opencode.ai/config.json",
   "default_agent": "cognitive-executor",
-  "plugins": [
-    "@prevalentware/opencode-goal-plugin",
-    "@tarquinen/opencode-dcp@latest"
-  ],
   "instructions": [
     "docs/opencode-shell-strategy.md"
   ],
@@ -35,16 +31,6 @@
       "*": "ask",
       "/tmp/**": "allow"
     },
-    "bash": {
-      "git add": "deny",
-      "git add *": "deny",
-      "git checkout": "deny",
-      "git checkout *": "deny",
-      "git commit": "deny",
-      "git commit *": "deny",
-      "git push": "deny",
-      "git push *": "deny"
-    },
     "shell": {
       "git add": "deny",
       "git add *": "deny",
diff --git a/scripts/check_docs_sync.py b/scripts/check_docs_sync.py
index 14f8646..0ec1ffd 100644
--- a/scripts/check_docs_sync.py
+++ b/scripts/check_docs_sync.py
@@ -2,7 +2,7 @@
 """Docs-sync gate: permission denies vs docs table, plus orphan-script scan.
 
 Check 1 (strict, exit non-zero on drift): the repo and global
-opencode.json `permission.bash` deny sets must match, and every denied
+opencode.json `permission.shell` deny sets must match, and every denied
 verb must appear in the Denied commands table in
 docs/opencode-shell-strategy.md.
 
@@ -28,7 +28,7 @@ TEXT_SUFFIXES = {".md", ".json", ".py", ".toml", ".txt", ".js"}
 
 def _deny_set(path: Path) -> set[str]:
     data = json.loads(path.read_text(encoding="utf-8"))
-    return set(data.get("permission", {}).get("bash", {}))
+    return set(data.get("permission", {}).get("shell", {}))
 
 
 def _check_denies() -> list[str]:
@@ -37,7 +37,11 @@ def _check_denies() -> list[str]:
     global_cfg = GLOBAL / "opencode.json"
     if global_cfg.is_file():
         glob = _deny_set(global_cfg)
-        if repo != glob:
+        # Only compare when the platform is installed globally (its deny set
+        # exists). A minimal/global config without permission.shell means the
+        # cognitive platform is not installed on this machine — nothing to
+        # compare, so skip the equality check.
+        if glob and repo != glob:
             errors.append(
                 f"deny sets differ: repo-only={sorted(repo - glob)} "
                 f"global-only={sorted(glob - repo)}")
diff --git a/scripts/fetch-opencode-docs.py b/scripts/fetch-opencode-docs.py
deleted file mode 100644
index 6a0ca61..0000000
--- a/scripts/fetch-opencode-docs.py
+++ /dev/null
@@ -1,368 +0,0 @@
-#!/usr/bin/env python3
-"""Fetch all OpenCode docs pages from opencode.ai and save as markdown files."""
-
-import httpx
-import re
-import os
-import sys
-from pathlib import Path
-from html.parser import HTMLParser
-from concurrent.futures import ThreadPoolExecutor, as_completed
-
-DOCS_DIR = Path(__file__).resolve().parent.parent / "docs" / "opencode"
-BASE_URL = "https://opencode.ai"
-
-PAGES = [
-    ("intro", "/docs/"),
-    ("config", "/docs/config/"),
-    ("providers", "/docs/providers/"),
-    ("network", "/docs/network/"),
-    ("enterprise", "/docs/enterprise/"),
-    ("troubleshooting", "/docs/troubleshooting/"),
-    ("windows-wsl", "/docs/windows-wsl"),
-    ("go", "/docs/go/"),
-    ("tui", "/docs/tui/"),
-    ("cli", "/docs/cli/"),
-    ("web", "/docs/web/"),
-    ("ide", "/docs/ide/"),
-    ("zen", "/docs/zen/"),
-    ("share", "/docs/share/"),
-    ("github", "/docs/github/"),
-    ("gitlab", "/docs/gitlab/"),
-    ("tools", "/docs/tools/"),
-    ("rules", "/docs/rules/"),
-    ("agents", "/docs/agents/"),
-    ("models", "/docs/models/"),
-    ("themes", "/docs/themes/"),
-    ("keybinds", "/docs/keybinds/"),
-    ("commands", "/docs/commands/"),
-    ("formatters", "/docs/formatters/"),
-    ("permissions", "/docs/permissions/"),
-    ("policies", "/docs/policies/"),
-    ("lsp", "/docs/lsp/"),
-    ("mcp-servers", "/docs/mcp-servers/"),
-    ("acp", "/docs/acp/"),
-    ("skills", "/docs/skills/"),
-    ("references", "/docs/references/"),
-    ("custom-tools", "/docs/custom-tools/"),
-    ("sdk", "/docs/sdk/"),
-    ("server", "/docs/server/"),
-    ("plugins", "/docs/plugins/"),
-    ("ecosystem", "/docs/ecosystem/"),
-]
-
-class MarkdownExtractor(HTMLParser):
-    def __init__(self):
-        super().__init__()
-        self.in_main = False
-        self.main_depth = 0
-        self.in_code = False
-        self.in_heading = False
-        self.in_paragraph = False
-        self.in_list_item = False
-        self.in_link = False
-        self.skip_tags = 0
-        self.output = []
-        self.buffer = []
-        self.code_buffer = []
-        self.skip_tag_stack = []
-        self.heading_level = 0
-        self.list_level = 0
-        self.in_ordered_list = False
-        self.list_counter = 0
-        self.table_mode = False
-        self.in_table_row = False
-        self.in_table_cell = False
-        self.table_cells = []
-        self.cell_idx = 0
-        self.in_nav = False
-        self.in_header = False
-        self.in_footer = False
-        self.in_aside = False
-        self.in_figure = False
-        self.figure_code = False
-        self.skip_depth = 0
-        self.title = ""
-
-    def handle_starttag(self, tag, attrs):
-        attrs_dict = dict(attrs)
-        class_name = attrs_dict.get("class", "")
-        id_attr = attrs_dict.get("id", "")
-
-        skip_classes = ["sidebar", "nav", "navbar", "pagination", "edit-link", "footer", "header-wrapper"]
-        if any(c in class_name for c in skip_classes):
-            self.skip_tag_stack.append(tag)
-            self.skip_depth += 1
-            if tag in ("nav", "header", "footer", "aside"):
-                setattr(self, f"in_{tag}", True)
-            return
-
-        if tag in ("nav", "header", "footer", "aside") and self.skip_depth == 0:
-            setattr(self, f"in_{tag}", True)
-            self.skip_tag_stack.append(tag)
-            self.skip_depth += 1
-            return
-
-        if self.skip_depth > 0:
-            if not self.skip_tag_stack or self.skip_tag_stack[-1] != tag:
-                self.skip_tag_stack.append("inner")
-            return
-
-        if tag == "main":
-            self.in_main = True
-            self.main_depth = 1
-            return
-
-        if not self.in_main:
-            return
-
-        if tag in ("script", "style"):
-            self.skip_tag_stack.append(tag)
-            self.skip_depth += 1
-            return
-
-        if tag == "h1":
-            self.in_heading = True
-            self.heading_level = 1
-            self._flush_buffer()
-        elif tag == "h2":
-            self.in_heading = True
-            self.heading_level = 2
-            self._flush_buffer()
-        elif tag == "h3":
-            self.in_heading = True
-            self.heading_level = 3
-            self._flush_buffer()
-        elif tag == "h4":
-            self.in_heading = True
-            self.heading_level = 4
-            self._flush_buffer()
-        elif tag == "p":
-            self.in_paragraph = True
-        elif tag == "code":
-            parent = attrs_dict.get("class", "")
-            if "language" in parent or parent.startswith("lang-"):
-                self.in_code = True
-                self.code_buffer = []
-                lang = parent.replace("language-", "").replace("lang-", "")
-                self.code_lang = lang
-        elif tag in ("pre",):
-            self.in_code = True
-            self.code_buffer = []
-            self.code_lang = ""
-        elif tag == "a":
-            self.in_link = True
-            href = attrs_dict.get("href", "")
-            self.link_href = href
-        elif tag == "li":
-            self.in_list_item = True
-        elif tag == "ul":
-            self.output.append("\n")
-        elif tag == "ol":
-            self.output.append("\n")
-            self.list_counter = 0
-        elif tag == "hr":
-            self._flush_buffer()
-            self.output.append("\n---\n")
-        elif tag == "br":
-            self.output.append("\n")
-        elif tag == "img":
-            alt = attrs_dict.get("alt", "image")
-            src = attrs_dict.get("src", "")
-            self.output.append(f"![{alt}]({src})")
-        elif tag == "strong" or tag == "b":
-            self.buffer.append("**")
-        elif tag == "em" or tag == "i":
-            self.buffer.append("*")
-        elif tag == "table":
-            self.table_mode = True
-        elif tag == "tr":
-            self.in_table_row = True
-            self.table_cells = []
-        elif tag in ("td", "th"):
-            self.in_table_cell = True
-            self.cell_buffer = []
-        elif tag == "figure":
-            self.in_figure = True
-        elif tag == "details":
-            pass
-        elif tag == "summary":
-            pass
-
-    def handle_endtag(self, tag):
-        if self.skip_depth > 0:
-            if self.skip_tag_stack:
-                popped = self.skip_tag_stack.pop()
-                if popped == tag or popped == "inner":
-                    self.skip_depth -= 1
-                if self.skip_depth == 0:
-                    if tag in ("nav", "header", "footer", "aside"):
-                        setattr(self, f"in_{tag}", False)
-            return
-
-        if tag == "main":
-            self.in_main = False
-            return
-
-        if not self.in_main:
-            return
-
-        if tag in ("script", "style"):
-            return
-
-        if tag == "h1" or tag == "h2" or tag == "h3" or tag == "h4":
-            text = "".join(self.buffer).strip()
-            if text:
-                prefix = "#" * self.heading_level
-                self.output.append(f"\n\n{prefix} {text}\n")
-            self.buffer = []
-            self.in_heading = False
-        elif tag == "p":
-            text = "".join(self.buffer).strip()
-            if text:
-                self.output.append(f"\n\n{text}\n")
-            self.buffer = []
-            self.in_paragraph = False
-        elif tag in ("pre",):
-            if self.code_buffer:
-                code = "".join(self.code_buffer)
-                lang = getattr(self, "code_lang", "")
-                if not lang:
-                    lang = ""
-                self.output.append(f"\n\n```{lang}\n{code}\n```\n")
-                self.code_buffer = []
-            self.in_code = False
-        elif tag == "code" and self.in_code:
-            if self.code_buffer:
-                code = "".join(self.code_buffer)
-                lang = getattr(self, "code_lang", "")
-                self.output.append(f"\n\n```{lang}\n{code}\n```\n")
-                self.code_buffer = []
-            self.in_code = False
-        elif tag == "a":
-            self.in_link = False
-        elif tag == "li":
-            text = "".join(self.buffer).strip()
-            if text:
-                self.output.append(f"\n- {text}")
-            self.buffer = []
-            self.in_list_item = False
-        elif tag == "ul":
-            pass
-        elif tag == "ol":
-            pass
-        elif tag in ("strong", "b"):
-            self.buffer.append("**")
-        elif tag in ("em", "i"):
-            self.buffer.append("*")
-        elif tag == "table":
-            self.table_mode = False
-        elif tag == "tr":
-            self.in_table_row = False
-            if self.table_cells:
-                header = "| " + " | ".join(self.table_cells[0]) + " |"
-                sep = "| " + " | ".join(["---"] * len(self.table_cells[0])) + " |"
-                self.output.append(f"\n\n{header}\n{sep}\n")
-                for row in self.table_cells[1:]:
-                    self.output.append(f"| {' | '.join(row)} |\n")
-                self.table_cells = []
-        elif tag in ("td", "th"):
-            self.in_table_cell = False
-            text = "".join(self.cell_buffer).strip()
-            if self.table_cells and len(self.table_cells[-1]) <= self.cell_idx:
-                self.table_cells[-1].append(text)
-            elif not self.table_cells:
-                self.table_cells.append([text])
-            else:
-                self.table_cells[-1].append(text)
-            self.cell_buffer = []
-            self.cell_idx += 1
-        elif tag == "figure":
-            self.in_figure = False
-        elif tag == "details":
-            pass
-
-    def handle_data(self, data):
-        if self.skip_depth > 0:
-            return
-        if not self.in_main:
-            return
-        stripped = data.strip()
-        if not stripped and not self.in_code:
-            return
-
-        if self.in_code:
-            self.code_buffer.append(data)
-        elif self.in_table_cell:
-            self.cell_buffer.append(data)
-        elif self.in_heading or self.in_paragraph or self.in_list_item or self.in_link:
-            self.buffer.append(data)
-        elif self.in_figure:
-            pass
-        else:
-            self.buffer.append(data)
-
-    def handle_entityref(self, name):
-        if self.skip_depth == 0 and self.in_main:
-            char = {"amp": "&", "lt": "<", "gt": ">", "quot": '"', "apos": "'"}.get(name, f"&{name};")
-            if self.in_code:
-                self.code_buffer.append(char)
-            else:
-                self.buffer.append(char)
-
-    def _flush_buffer(self):
-        if self.buffer:
-            self.output.append("".join(self.buffer))
-            self.buffer = []
-
-    def get_markdown(self):
-        return "".join(self.output).strip()
-
-
-def fetch_page(name, path):
-    url = f"{BASE_URL}{path}"
-    try:
-        resp = httpx.get(url, follow_redirects=True, timeout=30)
-        resp.raise_for_status()
-        html = resp.text
-
-        extractor = MarkdownExtractor()
-        extractor.feed(html)
-        content = extractor.get_markdown()
-
-        title = path.rstrip("/").split("/")[-1] or "intro"
-        safe_name = name.replace("/", "-")
-
-        md = f"# {title.capitalize()}\n\n"
-        md += f"> Source: {url}\n\n"
-        md += content
-
-        filepath = DOCS_DIR / f"{safe_name}.md"
-        filepath.write_text(md, encoding="utf-8")
-        return (name, "ok", len(md))
-    except Exception as e:
-        return (name, "error", str(e))
-
-
-def main():
-    DOCS_DIR.mkdir(parents=True, exist_ok=True)
-    total = len(PAGES)
-    print(f"Fetching {total} pages into {DOCS_DIR}...")
-
-    results = []
-    with ThreadPoolExecutor(max_workers=8) as pool:
-        fut_map = {pool.submit(fetch_page, name, path): name for name, path in PAGES}
-        for fut in as_completed(fut_map):
-            name, status, detail = fut.result()
-            results.append((name, status, detail))
-            icon = "✓" if status == "ok" else "✗"
-            print(f"  {icon} {name} ({detail})")
-
-    ok_count = sum(1 for _, s, _ in results if s == "ok")
-    err_count = sum(1 for _, s, _ in results if s == "error")
-    print(f"\nDone: {ok_count} ok, {err_count} errors out of {total}")
-    return 0 if err_count == 0 else 1
-
-
-if __name__ == "__main__":
-    sys.exit(main())
diff --git a/scripts/repomd b/scripts/repomd
deleted file mode 100755
index 2117dc9..0000000
--- a/scripts/repomd
+++ /dev/null
@@ -1,363 +0,0 @@
-#!/usr/bin/env -S uv run --script
-# /// script
-# requires-python = ">=3.9"
-# dependencies = [
-#     "pathspec>=0.11.0",
-# ]
-# ///
-
-import argparse
-import os
-import signal
-import sys
-from pathlib import Path
-from typing import Dict, List, Optional, Set, Tuple
-
-import pathspec
-
-# Handle BrokenPipe errors gracefully when piping to head, grep, etc.
-try:
-    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
-except AttributeError:
-    pass  # Windows does not have SIGPIPE
-
-EXT_MAP: Dict[str, str] = {
-    ".py": "python",
-    ".js": "javascript",
-    ".mjs": "javascript",
-    ".ts": "typescript",
-    ".tsx": "typescript",
-    ".jsx": "javascript",
-    ".rs": "rust",
-    ".go": "go",
-    ".cpp": "cpp",
-    ".hpp": "cpp",
-    ".c": "c",
-    ".h": "c",
-    ".rb": "ruby",
-    ".php": "php",
-    ".cs": "csharp",
-    ".java": "java",
-    ".kt": "kotlin",
-    ".swift": "swift",
-    ".sh": "bash",
-    ".bash": "bash",
-    ".zsh": "zsh",
-    ".yml": "yaml",
-    ".yaml": "yaml",
-    ".json": "json",
-    ".toml": "toml",
-    ".sql": "sql",
-    ".html": "html",
-    ".css": "css",
-    ".scss": "scss",
-    ".md": "markdown",
-    ".dockerfile": "dockerfile",
-}
-
-
-class GitIgnoreFilter:
-    """Evaluates paths against .gitignore files dynamically and hierarchically."""
-
-    def __init__(self) -> None:
-        self._specs: Dict[Path, Optional[pathspec.PathSpec]] = {}
-
-    def _get_spec(self, dir_path: Path) -> Optional[pathspec.PathSpec]:
-        if dir_path in self._specs:
-            return self._specs[dir_path]
-
-        gitignore_file = dir_path / ".gitignore"
-        if gitignore_file.is_file():
-            try:
-                with open(gitignore_file, "r", encoding="utf-8", errors="replace") as f:
-                    spec = pathspec.PathSpec.from_lines("gitwildmatch", f)
-                    self._specs[dir_path] = spec
-                    return spec
-            except Exception as e:
-                print(f"Warning: Failed to read {gitignore_file}: {e}", file=sys.stderr)
-
-        self._specs[dir_path] = None
-        return None
-
-    def is_ignored(self, target: Path) -> bool:
-        abs_path = target.resolve()
-
-        # Always ignore .git internal files and directories
-        if ".git" in abs_path.parts:
-            return True
-
-        current = abs_path if abs_path.is_dir() else abs_path.parent
-        traversal: List[Tuple[Path, Path]] = []
-
-        # Traverse upwards collecting specs up to the git/filesystem root
-        while True:
-            traversal.append((current, abs_path))
-            if (current / ".git").exists() or current.parent == current:
-                break
-            current = current.parent
-
-        # Evaluate rules from root downwards to let child gitignores override correctly
-        for root_dir, item in reversed(traversal):
-            spec = self._get_spec(root_dir)
-            if spec:
-                try:
-                    rel_path = item.relative_to(root_dir).as_posix()
-                    if item.is_dir() and not rel_path.endswith("/"):
-                        rel_path += "/"
-                    if spec.match_file(rel_path):
-                        return True
-                except ValueError:
-                    continue
-
-        return False
-
-
-def is_binary(file_path: Path) -> bool:
-    """Check if a file appears to be binary using chunk inspection."""
-    try:
-        with open(file_path, "rb") as f:
-            chunk = f.read(4096)
-            if b"\0" in chunk:
-                return True
-            # Attempt decoding standard text
-            chunk.decode("utf-8")
-            return False
-    except UnicodeDecodeError:
-        try:
-            chunk.decode("latin-1")
-            return False
-        except Exception:
-            return True
-    except Exception:
-        return True
-
-
-def generate_tree(
-    dir_path: Path,
-    ignore_filter: GitIgnoreFilter,
-    max_depth: Optional[int] = None,
-) -> str:
-    """Generates an ASCII directory structure tree."""
-    lines = ["```text", dir_path.name or str(dir_path)]
-
-    def _walk(current: Path, prefix: str, depth: int) -> None:
-        if max_depth is not None and depth >= max_depth:
-            return
-
-        try:
-            entries = [e for e in current.iterdir() if not ignore_filter.is_ignored(e)]
-        except PermissionError:
-            lines.append(f"{prefix}└── [Permission Denied]")
-            return
-        except OSError as e:
-            lines.append(f"{prefix}└── [OS Error: {e.strerror}]")
-            return
-
-        # Sort directories first, then files alphabetically
-        sorted_entries = sorted(entries, key=lambda e: (not e.is_dir(), e.name.lower()))
-        count = len(sorted_entries)
-
-        for idx, entry in enumerate(sorted_entries):
-            is_last = idx == (count - 1)
-            connector = "└── " if is_last else "├── "
-            lines.append(f"{prefix}{connector}{entry.name}{'/' if entry.is_dir() else ''}")
-
-            if entry.is_dir():
-                sub_prefix = "    " if is_last else "│   "
-                _walk(entry, prefix + sub_prefix, depth + 1)
-
-    _walk(dir_path, "", 0)
-    lines.append("```")
-    return "\n".join(lines)
-
-
-def process_source_file(file_path: Path, max_size: int, line_numbers: bool) -> str:
-    """Wraps file contents in Markdown code fences safely."""
-    lines = [f"### `{file_path}`\n"]
-
-    if not file_path.is_file():
-        lines.append("> Skipped: (Not a file or does not exist)\n")
-        return "\n".join(lines)
-
-    try:
-        size = file_path.stat().st_size
-        if size > max_size:
-            lines.append(f"> Skipped: (File exceeds max-size limit: {size / 1024:.1f} KB)\n")
-            return "\n".join(lines)
-    except OSError as e:
-        lines.append(f"> Skipped: (Stat error: {e})\n")
-        return "\n".join(lines)
-
-    if is_binary(file_path):
-        lines.append("> Skipped: (Binary file)\n")
-        return "\n".join(lines)
-
-    # Detect language for syntax highlighting
-    ext = file_path.suffix.lower()
-    lang = EXT_MAP.get(ext, ext.lstrip("."))
-    if not lang and file_path.name.lower() == "dockerfile":
-        lang = "dockerfile"
-
-    try:
-        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
-            content = f.read()
-
-        file_lines = content.splitlines()
-
-        # Format lines
-        if line_numbers:
-            padding = len(str(len(file_lines)))
-            payload = "\n".join(
-                f"{str(i).rjust(padding)} | {line}" for i, line in enumerate(file_lines, 1)
-            )
-        else:
-            payload = "\n".join(file_lines)
-
-        # Ensure fence safety: prevent nested backtick collision
-        fence = "```"
-        while fence in payload:
-            fence += "`"
-
-        lines.append(f"{fence}{lang}")
-        if payload:
-            lines.append(payload)
-        lines.append(f"{fence}\n")
-
-    except Exception as e:
-        lines.append(f"> Skipped: (Error reading file: {e})\n")
-
-    return "\n".join(lines)
-
-
-def collect_files(target: str, ignore_filter: GitIgnoreFilter) -> List[Path]:
-    """Recursively resolves valid non-ignored files."""
-    p = Path(target)
-    if not p.exists():
-        print(f"Warning: Path not found: {target}", file=sys.stderr)
-        return []
-
-    if ignore_filter.is_ignored(p):
-        return []
-
-    if p.is_file():
-        return [p]
-
-    collected: List[Path] = []
-    for root, dirs, files in os.walk(p):
-        root_path = Path(root)
-
-        # Mutate dirs in-place to prevent os.walk from entering ignored directories
-        dirs[:] = [
-            d for d in dirs
-            if not ignore_filter.is_ignored(root_path / d)
-        ]
-
-        for f in files:
-            fpath = root_path / f
-            if not ignore_filter.is_ignored(fpath):
-                collected.append(fpath)
-
-    return collected
-
-
-def main() -> None:
-    parser = argparse.ArgumentParser(
-        prog="repomd",
-        description="Pack trees and source code into clean Markdown (optimized for LLMs and documentation).",
-    )
-    parser.add_argument(
-        "paths",
-        nargs="*",
-        default=[],
-        help="Optional positional targets to process (defaults to processing tree & sources if provided).",
-    )
-    parser.add_argument("--tree", "-t", type=str, help="Directory to generate ASCII directory tree for.")
-    parser.add_argument("--source", "-s", type=str, nargs="+", help="Files or directories to pack as source.")
-    parser.add_argument("--source-list", "-l", type=str, help="File containing list of file paths (one per line).")
-    parser.add_argument("--max-size", type=int, default=1_048_576, help="Max file size in bytes (default: 1MB).")
-    parser.add_argument("--max-depth", type=int, default=None, help="Tree directory depth limit.")
-    parser.add_argument("--output", "-o", type=str, help="Output destination file (default: stdout).")
-    parser.add_argument("--no-line-numbers", action="store_true", help="Omit line numbers from code blocks.")
-
-    args = parser.parse_args()
-
-    # Smart default fallback: `repomd .` should run both tree and source on target path
-    tree_dir = args.tree
-    source_inputs = args.source or []
-
-    if not tree_dir and not source_inputs and not args.source_list:
-        if args.paths:
-            # If positional arguments are passed, treat directories as trees & sources
-            tree_dir = args.paths[0] if Path(args.paths[0]).is_dir() else None
-            source_inputs = args.paths
-        else:
-            parser.error("No input provided. Run with `repomd .` or check `--help`.")
-
-    ignore_filter = GitIgnoreFilter()
-    output: List[str] = []
-
-    # 1. Process Directory Tree
-    if tree_dir:
-        t_path = Path(tree_dir)
-        if t_path.is_dir():
-            if not ignore_filter.is_ignored(t_path):
-                output.append(f"## Directory Tree: `{t_path}`\n")
-                output.append(generate_tree(t_path, ignore_filter, max_depth=args.max_depth))
-                output.append("")
-            else:
-                print(f"Warning: Directory is ignored by .gitignore: {t_path}", file=sys.stderr)
-        else:
-            print(f"Error: Provided tree target is not a directory: {t_path}", file=sys.stderr)
-            sys.exit(1)
-
-    # 2. Collect Source Files
-    files_to_process: Dict[Path, Path] = {}
-
-    def _register(paths: List[Path]) -> None:
-        for p in paths:
-            files_to_process[p.resolve()] = p
-
-    for src in source_inputs:
-        _register(collect_files(src, ignore_filter))
-
-    if args.source_list:
-        l_path = Path(args.source_list)
-        if l_path.is_file():
-            try:
-                with open(l_path, "r", encoding="utf-8") as f:
-                    for line in f:
-                        line_clean = line.strip()
-                        if line_clean and not line_clean.startswith("#"):
-                            _register(collect_files(line_clean, ignore_filter))
-            except Exception as e:
-                print(f"Error reading list {l_path}: {e}", file=sys.stderr)
-        else:
-            print(f"Error: Source list not found: {l_path}", file=sys.stderr)
-
-    # 3. Process Code Blocks
-    if files_to_process:
-        output.append("## Source Files\n")
-        include_lines = not args.no_line_numbers
-
-        # Sort files alphabetically for stable diffs
-        for _, file_path in sorted(files_to_process.items(), key=lambda i: str(i[1]).lower()):
-            output.append(process_source_file(file_path, args.max_size, include_lines))
-
-    # 4. Write Output
-    final_output = "\n".join(output)
-
-    if args.output:
-        try:
-            with open(args.output, "w", encoding="utf-8") as out:
-                out.write(final_output)
-            print(f"Saved repository markdown to {args.output}", file=sys.stderr)
-        except OSError as e:
-            print(f"Error writing output file: {e}", file=sys.stderr)
-            sys.exit(1)
-    else:
-        sys.stdout.write(final_output)
-
-
-if __name__ == "__main__":
-    main()
-
diff --git a/services/mcp-brain.service b/services/mcp-brain.service
index a34efe6..01be225 100644
--- a/services/mcp-brain.service
+++ b/services/mcp-brain.service
@@ -9,8 +9,8 @@ ExecStart=%h/.config/opencode/mcp-brain-bridge/.venv/bin/python %h/.config/openc
 Environment=MCP_TRANSPORT=streamable-http
 # Credentials resolve via the bridge's own .env self-load
 # (<server-dir>/.env -> install-root .env -> <cwd>/.env, never
-# overriding real environment). Export BRAIN_* before launching
-# opencode-server only if you want env to win over files.
+# overriding real environment). Export BRAIN_* in the environment
+# that launches OpenChamber only if you want env to win over files.
 Restart=always
 RestartSec=3
 
diff --git a/skill-templates/audit-agents/SKILL.md b/skill-templates/audit-agents/SKILL.md
index 6eb70b6..18c4d98 100644
--- a/skill-templates/audit-agents/SKILL.md
+++ b/skill-templates/audit-agents/SKILL.md
@@ -36,7 +36,7 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **Universal Financial Ledger Standard**: `AGENTS.md` MUST include a guardrail requiring snapshot-on-write for financial mutations and `$ifNull` precedence for monetary aggregations. `docs/conventions.md` MUST contain a `## Universal Financial Ledger Standard` section.
 - **Lite Mode Protocol**: `AGENTS.md` MUST document the `<lite_mode_protocol>` — when eligible (single-file, no security/financial impact, obvious simplicity), the full 9-step production line can be bypassed with a `[LITE]` justification in the task's `## Execution Log & Reasoning` section. Escalation to Full Mode is mandatory if hidden complexity is discovered.
 - **Deprecated-Section Purge Rule**: Scans `AGENTS.md` and all task files across `tasks/` (excluding archive and completed history) for deprecated sections: `## Manager Decisions`, `## Admin Decision`, `Manager Decision`, `Admin Decision`. When detected, the auditor MUST purge the entire deprecated section from the target file, document the purge in the audit findings/changelog, and MUST NOT flag their absence as a missing requirement or recreate them.
-- **Plugin Runtime-State gitignore**: If the project uses OpenCode plugins that write per-project state, `.gitignore` MUST cover plugin runtime-state paths (e.g. worktree checkouts, session/state JSON, goal-state dirs) while MUST NOT ignore deliberate config overrides checked in on purpose (e.g. a project-level plugin config pinning team-shared settings). Audit `.gitignore` read-only first; patch only paths belonging to plugins actually detected in the project's `opencode.json`/`tui.json` `plugin` arrays — never speculative entries. The same rule covers Brain session history: when the audited project carries `tasks/.sessions/` transcript dirs (brain-bridge per-project sessions), `.gitignore` MUST include the `tasks/.sessions/` path — check `.gitignore` first and add the line only if missing (never duplicate), and only after confirming the dir exists in that project.
+- **Runtime-State gitignore**: If the project writes per-project runtime state (plugin state, worktree checkouts, session/state JSON), `.gitignore` MUST cover those paths while MUST NOT ignore deliberate config checked in on purpose. Audit `.gitignore` read-only first; patch only paths for state actually detected in the project — never speculative entries. The same rule covers Brain session history: when the audited project carries `tasks/.sessions/` transcript dirs (brain-bridge per-project sessions), `.gitignore` MUST include the `tasks/.sessions/` path — check `.gitignore` first and add the line only if missing (never duplicate), and only after confirming the dir exists in that project.
 
 ---
 
@@ -389,7 +389,7 @@ Additionally, the `docs/conventions.md` file MUST exist and contain:
 - **Task-Number Reference Discipline**: `AGENTS.md` MUST include a guardrail restricting task-number references to code comments, CHANGELOG entries, task files, history archives, and HTML comments — never in visible prompt prose, headings, or skill instructions. `docs/conventions.md` MUST contain a `## Task-Number Reference Discipline` section.
 - **Lite Mode Protocol**: `AGENTS.md` MUST document the `<lite_mode_protocol>` — when eligible (single-file, no security/financial impact, obvious simplicity), the full 9-step production line can be bypassed with a `[LITE]` justification in the task's `## Execution Log & Reasoning` section. Escalation to Full Mode is mandatory if hidden complexity is discovered.
 - **Deprecated-Section Purge Rule**: Scans `AGENTS.md` and all task files across `tasks/` (excluding archive and completed history) for deprecated sections: `## Manager Decisions`, `## Admin Decision`, `Manager Decision`, `Admin Decision`. When detected, the auditor MUST purge the entire deprecated section from the target file, document the purge in the audit findings/changelog, and MUST NOT flag their absence as a missing requirement or recreate them.
-- **Plugin Runtime-State gitignore**: If the project uses OpenCode plugins that write per-project state, `.gitignore` MUST cover plugin runtime-state paths (e.g. worktree checkouts, session/state JSON, goal-state dirs) while MUST NOT ignore deliberate config overrides checked in on purpose (e.g. a project-level plugin config pinning team-shared settings). Audit `.gitignore` read-only first; patch only paths belonging to plugins actually detected in the project's `opencode.json`/`tui.json` `plugin` arrays — never speculative entries. The same rule covers Brain session history: when the audited project carries `tasks/.sessions/` transcript dirs (brain-bridge per-project sessions), `.gitignore` MUST include the `tasks/.sessions/` path — check `.gitignore` first and add the line only if missing (never duplicate), and only after confirming the dir exists in that project.
+- **Runtime-State gitignore**: If the project writes per-project runtime state (plugin state, worktree checkouts, session/state JSON), `.gitignore` MUST cover those paths while MUST NOT ignore deliberate config checked in on purpose. Audit `.gitignore` read-only first; patch only paths for state actually detected in the project — never speculative entries. The same rule covers Brain session history: when the audited project carries `tasks/.sessions/` transcript dirs (brain-bridge per-project sessions), `.gitignore` MUST include the `tasks/.sessions/` path — check `.gitignore` first and add the line only if missing (never duplicate), and only after confirming the dir exists in that project.
 
 ### Resolution Protocol
 
diff --git a/skill-templates/opencode-init/references/examples/golden-opencode.json b/skill-templates/opencode-init/references/examples/golden-opencode.json
index aa483de..4b88dbc 100644
--- a/skill-templates/opencode-init/references/examples/golden-opencode.json
+++ b/skill-templates/opencode-init/references/examples/golden-opencode.json
@@ -37,7 +37,7 @@
       "*": "ask",
       "/tmp/**": "allow"
     },
-    "bash": {
+    "shell": {
       "git add": "deny",
       "git add *": "deny",
       "git checkout": "deny",
diff --git a/skill-templates/opencode-init/references/runtime-matrix.md b/skill-templates/opencode-init/references/runtime-matrix.md
index f7006d7..c5974f7 100644
--- a/skill-templates/opencode-init/references/runtime-matrix.md
+++ b/skill-templates/opencode-init/references/runtime-matrix.md
@@ -4,7 +4,7 @@
 | ---- | -------------- | ----------- |
 | Top level (project) | `$schema`, `default_agent`, `instructions[]`, `formatter`, `lsp`, `permission{}` | `permissions[]` array; `mcp{}` and `plugin[]` (global-only) |
 | Permission entries | `"tool-name": "allow\|ask\|deny"` flat map | `{permission: ..., pattern: ...}` objects |
-| Bash rules | `permission.bash = {"git commit": "deny", ...}` string map | Structured rule objects |
+| Bash rules | `permission.shell = {"git commit": "deny", ...}` string map | Structured rule objects |
 | MCP | GLOBAL-ONLY — install in `~/.config/opencode/opencode.json`; banned from project output | Any `mcp{}` block in a generated project file |
 | Plugin | GLOBAL-ONLY — npm spec in global config or `.opencode/plugins/` / `~/.config/opencode/plugins/`; banned from project output | Any `plugin[]` list in a generated project file |
 | LSP (project guidance) | flat map `{name: {command, extensions?, env?, initialization?, disabled?}}` — e.g. `{"typescript": {"command": [...]}}`; `true`/`false` also valid; server install stays host/global side | `language-server` wrapper (`{language-server: {name: ...}}`), `environment` (LSP uses `env`), unknown keys |
diff --git a/skill-templates/opencode-init/scripts/validate-opencode.py b/skill-templates/opencode-init/scripts/validate-opencode.py
index 19c5847..de520b7 100644
--- a/skill-templates/opencode-init/scripts/validate-opencode.py
+++ b/skill-templates/opencode-init/scripts/validate-opencode.py
@@ -113,7 +113,7 @@ def validate(cfg: dict) -> list[str]:
                 continue
             if isinstance(decision, dict):
                 # Scoped sub-map (e.g. external_directory): leaves must be
-                # allow|ask|deny. The golden file proves this V1 shape.
+                # allow|ask|deny. The golden file proves this V2 shape.
                 for scope, leaf in decision.items():
                     if leaf not in ("allow", "ask", "deny"):
                         errors.append(
@@ -121,13 +121,13 @@ def validate(cfg: dict) -> list[str]:
                         )
             elif decision not in ("allow", "ask", "deny"):
                 errors.append(f"permission[{tool!r}] must be allow|ask|deny")
-        bash = perm.get("bash")
-        if not isinstance(bash, dict):
-            errors.append("permission.bash must be a command-pattern map")
+        shell = perm.get("shell")
+        if not isinstance(shell, dict):
+            errors.append("permission.shell must be a command-pattern map")
         else:
             for pattern in ZAC_DENIES:
-                if bash.get(pattern) != "deny":
-                    errors.append(f"permission.bash[{pattern!r}] must be 'deny'")
+                if shell.get(pattern) != "deny":
+                    errors.append(f"permission.shell[{pattern!r}] must be 'deny'")
     if "mcp" in cfg:
         errors.append(
             "mcp is global-only (install in ~/.config/opencode/opencode.json); "
diff --git a/tests/test_skill_registry.py b/tests/test_skill_registry.py
index 451726d..8f52c84 100644
--- a/tests/test_skill_registry.py
+++ b/tests/test_skill_registry.py
@@ -181,11 +181,11 @@ def test_validate_opencode_script():
     base = json.loads(golden.read_text(encoding="utf-8"))
     assert run(base) == (0, ""), "golden file must validate clean"
     v2 = dict(base)
-    v2["permissions"] = [{"permission": "bash", "pattern": "*", "decision": "deny"}]
+    v2["permissions"] = [{"permission": "shell", "pattern": "*", "decision": "deny"}]
     code, out = run(v2)
     assert code == 1 and "permissions[]" in out
     no_zac = json.loads(json.dumps(base))
-    del no_zac["permission"]["bash"]["git push *"]
+    del no_zac["permission"]["shell"]["git push *"]
     code, out = run(no_zac)
     assert code == 1 and "git push *" in out
     secret = json.loads(json.dumps(base))
@@ -336,7 +336,7 @@ def test_validate_mcp_rejected_global_only():
 
 def test_validate_partial_zac_rejected():
     cfg = _fresh_golden()
-    del cfg["permission"]["bash"]["git commit"]
+    del cfg["permission"]["shell"]["git commit"]
     code, out = _run_validator(cfg)
     assert code == 1 and "git commit" in out
 
diff --git a/tui.json b/tui.json
deleted file mode 100644
index f558fc4..0000000
--- a/tui.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "plugin": [
-    "@prevalentware/opencode-goal-plugin",
-    "@tarquinen/opencode-dcp@latest"
-  ]
-}
```
<!-- END_GIT_DIFF -->
