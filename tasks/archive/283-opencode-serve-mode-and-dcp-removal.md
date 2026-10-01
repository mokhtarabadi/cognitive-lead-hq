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
**Factual Git Diff:** Stored in Commit Hash: `47868bb9a800bb691191393a5850502b10d5906d`
<!-- END_GIT_DIFF -->
