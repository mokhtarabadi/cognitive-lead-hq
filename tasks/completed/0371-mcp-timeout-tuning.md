# Task 0371: MCP timeout tuning — stop the 30s client cap from faking upload failures

**File:** `tasks/completed/0371-mcp-timeout-tuning.md`
**Source:** manager (2026-11-03 — a 14 MB APK upload reported `Request timed out` while Telegram actually received the file; raise the timeout everywhere it is documented)
**Type:** improvement
**Status:** closed
**Finished:** 2026-11-03T18:49:24Z

## Goal

Remove the client-side 30-second execution cap on the Telegram MCP so a large file upload reports its real outcome instead of a false timeout, and keep every place that documents that number in sync with the running configuration.

## Scope

1. **Live configuration (outside the repo):** `~/.config/opencode/opencode.json` → `mcp.telegram.timeout` raised from `30000` to `300000` for both `catalog` and `execution`.
2. **Repo documentation:** `docs/telegram-setup.md` (two `"timeout": 30000` occurrences, one in the V1 local example and one in the §5.1 OpenCode example) raised to `300000`.
3. **Repo memory workflow:** `.opencode/memory/workflows/global-install-upgrade.md` — the cut-config line names `telegram 30000`; update the number so a future reinstall does not reintroduce the cap.
4. **Backup before touching the live config**, and JSON-validate it afterwards.

## Non-goals

- No change to `blowsh` (120s), `brain` (600s+), `planner` (15s/30s) or `lint` (15s) timeouts — those are sized for their own workloads and were not the defect.
- No change to the MCP server itself (`mcp-telegram-server`): the server transfers fine; only the client gives up early.
- No change to upload size limits or allowed roots.
- No code change in this repository — it is documentation plus one live config file.

## Local TODOs

- [x] Back up `~/.config/opencode/opencode.json`.
- [x] Raise `mcp.telegram.timeout` (catalog + execution) to 300000 and validate JSON.
- [x] Update both occurrences in `docs/telegram-setup.md` (lines 129, 161 → 300000).
- [x] Update the number in `.opencode/memory/workflows/global-install-upgrade.md` (line 52 → telegram 300000).
- [x] Verify: grep finds no stale `30000` telegram timeout, JSON parses exit 0, docs lint clean.

## Acceptance Criteria

- [x] `jq . ~/.config/opencode/opencode.json` exits 0 and `mcp.servers.telegram.timeout` reads `{catalog: 300000, execution: 300000}`.
- [x] `grep -rn "30000" docs/telegram-setup.md` returns nothing for the timeout key.
- [x] `.opencode/memory/workflows/global-install-upgrade.md` names the telegram timeout as 300000.
- [x] A backup of the original global config exists at a named path and is cited in the evidence table.
- [x] No other MCP server's timeout value changed (diff proves telegram only).

## Verification Evidence

| Gate | Result |
|------|--------|
| Global config backup | `~/.config/opencode/opencode.json.bak-20261103-194528` (3056 B) |
| `jq . ~/.config/opencode/opencode.json` | exit 0 — JSON valid; `mcp.servers.telegram.timeout = {catalog: 300000, execution: 300000}` |
| Stale-number grep (`30000` minus `300000`) | NONE |
| Markdown lint (`docs/telegram-setup.md`) | ✅ passed |
| Structural diff vs backup | only 2 numbers differ; all other servers unchanged |
| Subagent scope check | `git diff --stat` = 2 files, 3 insertions, 3 deletions, numeric-only hunks |

## Risk & Rollback

- **Risk:** a malformed global `opencode.json` breaks the agent environment at next start. Mitigation: backup first, validate with `jq` before finishing, and change only two numeric fields.
- **Risk:** the change needs an OpenCode restart to take effect; a running session keeps the old 30s cap until then. Stated plainly rather than assumed away.
- **Rollback:** restore the backup (`cp opencode.json.bak-<date> opencode.json`) and revert the two doc hunks.

## Definition of Done

- All five acceptance criteria evidenced, JSON validated, docs lint clean, no unrelated timeout changed.

## Execution Log & Reasoning

- **Live config done (2026-11-03).** The real path is `mcp.servers.telegram` (V2 shape), not `mcp.telegram` as the older docs show — a first read threw `KeyError: 'telegram'`, which is itself evidence that the documentation lags the running shape. Backup written to `~/.config/opencode/opencode.json.bak-20261103-194528`; the structured diff against it proves exactly two numbers changed and every other server keeps its own timeout.
- **Restart requirement (assumption A3):** OpenCode loads `opencode.json` once at startup, so this session still holds the old 30 s cap until the client restarts. The next large upload is the real proof; a timeout before a restart proves nothing about the fix.
- 2026-11-03: created from the observed defect — three `send_file` attempts on a 14.2 MB APK returned `MCP tool "send_file" ... Request timed out`, yet Telegram history showed exactly one delivered document (message 731). The transfer completes; the 30s client timeout merely reports it as failure, which is worse than a real error because it invites duplicate sends.
- **Parallel execution note:** the two documentation files were edited by one delegated subagent with a disjoint file list while the Hands handled the live global config; the Hands re-ran every grep and the lint independently rather than trusting the report. The subagent's scope check (`2 files, 3 insertions, 3 deletions`) matched.
- **Lane note (deviation, logged):** the task was created and executed in a single pass, so the backlog → in-progress hop was skipped before the edits. The file is moved straight to `tasks/qa/` with this note rather than pretending the lane was used.
- **Autopilot locked (2026-11-03, Manager: "lock auto pilot").** Mode is LOCKED for this task: edits and verification run end to end without further pauses, except hard blockers and the closure approval phrase. ZAC holds — no `git add`/`commit`/`checkout`/`push`.
- Scope decision (assumption A1): only the Telegram timeout is raised. The 15s lint/planner and 120s blowsh values were examined and left alone because no defect was observed on them; changing them without evidence would be tuning by intuition.
- Scope decision (assumption A2): the live global config is part of the task. Editing only the docs would leave the running environment still capped at 30s, which is the actual bug.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.opencode/memory/workflows/global-install-upgrade.md b/.opencode/memory/workflows/global-install-upgrade.md
index 1c66985..a50c16f 100644
--- a/.opencode/memory/workflows/global-install-upgrade.md
+++ b/.opencode/memory/workflows/global-install-upgrade.md
@@ -49,7 +49,7 @@ Existing users on per-session stdio entries migrate without reinstalling server
 
 1. **Backup global config:** `cp ~/.config/opencode/opencode.json ~/.config/opencode/opencode.json.bak-$(date +%Y%m%d-%H%M%S)`.
 2. **Start the singletons:** install `services/mcp-*.service` to `~/.config/systemd/user/`, `systemctl --user daemon-reload`. For the planner, build its venv (`cd ~/.config/opencode/mcp-planner-server && uv sync`) and write the `PLANNER_PROJECT_ROOT` drop-in **before** starting the unit, because `ExecStart` needs `.venv/bin/python`. Then enable+start every HQ singleton (`for s in lint context memory brain telegram planner`), and start `blowsh-singleton` (`docker run -d --name blowsh-singleton --restart unless-stopped -p 127.0.0.1:8107:8107 -e MCP_TRANSPORT=http -e MCP_HOST=0.0.0.0 -e MCP_PORT=8107 -e BROWSH_PROFILE_DIR=/data/browsh-profile -v blowsh-profile:/data/browsh-profile <image>`).
-3. **Cut config:** replace each stdio `mcp.<name>` block under `mcp.servers` with `{type: remote, url: http://127.0.0.1:<port>/mcp, disabled: false, timeout: {catalog, execution}}` (ports docs/services.md; telegram 30000, blowsh 120000, brain 600000+, planner 15000/30000, rest 15000). Validate JSON after the edit.
+3. **Cut config:** replace each stdio `mcp.<name>` block under `mcp.servers` with `{type: remote, url: http://127.0.0.1:<port>/mcp, disabled: false, timeout: {catalog, execution}}` (ports docs/services.md; telegram 300000, blowsh 120000, brain 600000+, planner 15000/30000, rest 15000). Validate JSON after the edit.
 4. **Verify:** `opencode debug config` resolves 7 entries; exactly one process per server (`ps aux | grep -E 'mcp-|telegram_mcp' | grep -v grep`); each port answers.
 5. **Rollback:** restore the backup config, restart sessions. HQ servers default to `streamable-http` when `MCP_TRANSPORT` is unset (explicit `stdio` still works for local debugging); telegram-mcp accepts `stdio|http|sse`.
 
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 77e50e3..0be33a6 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+### Changed
+
+- **Telegram MCP timeout raised to 300 s (Task 0371):** `mcp.servers.telegram.timeout` in the global `opencode.json` moves from `30000` to `300000` for both `catalog` and `execution`. A 14.2 MB APK upload completed on Telegram's side while three client calls reported `Request timed out` — the 30 s cap reported a success as a failure, which invites duplicate sends. Every other server keeps its own timeout (`custom_context`/`project_memory`/`lint` 15 s, `blowsh` 120 s, `brain` 1200 s, `planner` 15 s/30 s). The two documented occurrences in `docs/telegram-setup.md` and the reinstall workflow's value list were updated in step; a timestamped backup of the global config was written first and the file validated as JSON. Takes effect after an OpenCode restart.
+
 ### Added
 
 - **Code Mode off for every server except telegram (Task 0361):** `custom_context`, `project_memory`, `lint`, `brain`, `planner` and `blowsh` now set `"codemode": false`, so their ~43 tools are native calls instead of `execute` wrappers; `telegram` (147 tools) stays on Code Mode because its schemas must not enter the system prompt. Applied to the global `opencode.json` after a timestamped backup and validated as JSON; the live session catalog dropped all six out of `execute` in place. Policy documented in `docs/services.md` (rationale table), `docs/setup.md`, `README.md` Option B and the `LLM.txt` install block, and stored as `workflows/codemode-policy` memory for the upgrade workflow.
diff --git a/docs/telegram-setup.md b/docs/telegram-setup.md
index 4e9edfc..aa72c32 100644
--- a/docs/telegram-setup.md
+++ b/docs/telegram-setup.md
@@ -126,7 +126,7 @@ $HOME/.config/opencode/mcp-telegram-server/.venv/bin/python $HOME/.config/openco
       "type": "local",
       "command": ["$HOME/.config/opencode/mcp-telegram-server/.venv/bin/python", "$HOME/.config/opencode/mcp-telegram-server/main.py", "/tmp/telegram-mcp", "$HOME/.config/opencode/mcp-telegram-server/downloads"],
       "enabled": true,
-      "timeout": 30000
+      "timeout": 300000
     }
   }
 }
@@ -158,7 +158,7 @@ $HOME/.config/opencode/mcp-telegram-server/.venv/bin/python $HOME/.config/openco
       "type": "local",
       "command": ["$HOME/.config/opencode/mcp-telegram-server/.venv/bin/python", "$HOME/.config/opencode/mcp-telegram-server/main.py", "/tmp/telegram-mcp", "$HOME/.config/opencode/mcp-telegram-server/downloads"],
       "enabled": true,
-      "timeout": 30000
+      "timeout": 300000
     }
   },
   "permission": { "telegram_*": "allow" }
```
<!-- END_GIT_DIFF -->
