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
**Factual Git Diff:** Stored in Commit Hash: `d355efd760e7dccd4be3728d21ec2f2565d36116`
<!-- END_GIT_DIFF -->
