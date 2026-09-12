# Task 206: Systemd user unit env for opencode-server + docs

**File:** `tasks/qa/206-systemd-user-unit-env-for-opencode-server-docs.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Goal

Give the systemd-managed opencode-server our env and document it for others.

## Manager's Notes

Check our opencode and how it works, and global opencode configuration. I manage opencode by systemd (user mode) — find it, read it, and if needed add our env to it, and document it in our project and LLM.txt for other people.

## Local TODOs

- [x] Find + read opencode-server.service unit
- [x] Add EnvironmentFile if missing
- [x] daemon-reload + verify (no restart — would kill session)
- [x] Document in docs/setup.md + LLM.txt
- [x] CHANGELOG + lint + stage

## Acceptance Criteria

- [x] Unit carries our env file and shows under EnvironmentFiles
- [x] Docs explain systemd env + restart command
- [x] No service restart by Hands (session would die)

## Verification Evidence

- **Test command:** `systemctl --user show opencode-server.service -p EnvironmentFiles; rtk test "uv run --with pytest --with pathspec --with pyyaml --with mcp==1.30.0 python -m pytest tests/ -q"`
- **Expected result:** EnvironmentFiles lists HQ .env; suite green
- **Actual result:** EnvironmentFiles=`/home/mohammad/code-server/projects/cognitive-lead-hq/.env (ignore_errors=yes)`, ActiveState=active; suite 237 passed via rtk collapsed output
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Unit edit breaks daemon start; restart kills this session.
- **Rollback plan:** Remove the EnvironmentFile line + daemon-reload; unit file is not tracked by repo.

---

## Execution Log & Reasoning

**Finding:** `opencode-server.service` ran with bare `Environment` (no `EnvironmentFile`) — shell exports never reach the daemon, so `{env:}` forwarding in `opencode.json` resolved empty and keys arrived only via `.env` file fallbacks.
**Fix:** added `EnvironmentFile=-<hq>/.env` (+ comment) to the unit; `daemon-reload` applied, service still `active/running`, `EnvironmentFiles` lists the HQ file. Restart deliberately NOT run (kills this live session) — Manager restarts.
**Docs:** `docs/setup.md` §Systemd user service env + `LLM.txt` §7.10 (portable `%h` form for others).
**Rollback:** delete the EnvironmentFile line + daemon-reload; unit file lives outside the repo.
**Env cleanup (Manager order):** project `.env` held 4 dead lines (`OPENROUTER_API_KEY` — never read by our code; 3 `TELEGRAM_*` — zero code consumers). Deleted by key-name filter (values never entered context; global backup holds them). `.env` now carries only the 5 live keys; `README` quick-start line updated to the live key names. `.env` is gitignored — no staging.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index f135592..2faa908 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -19,6 +19,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Changed
 
+- **Systemd daemon env + docs (Task 206):** `opencode-server.service` (systemd user unit) gained `EnvironmentFile=-<hq>/.env` so the daemon-run OpenCode starts with keys + model pins — process env outranks every `.env` fallback and feeds `{env:}` forwarding, so all served projects share it. Verified via daemon-reload (`EnvironmentFiles` listed, service still running); restart deferred to Manager (kills live sessions). Documented in `docs/setup.md` (§Systemd user service env) and `LLM.txt` (§7.10, portable `%h` form for others).
+
 - **Cleanup sweep 9.30.0 (Task 205):** removed the dead 2026-09-09 pause narrative from live docs (executor bridge section, setup.md, README, LLM.txt) — the paused system was deleted during the bridge rebuild, never paused; deleted `archive/` (only a superseded RESTORE pointer) and its dead docs pointer; folded the loop-engine RTK evidence table into the shell strategy and removed `docs/loop-engine/`; README aligned to bridge reality; deleted the leftover `scripts/qa-rules-gate/` (zero live callers) and stripped its prose from the QA persona; shell strategy now mandates `rtk test` (binary installed) and mirrors the permission-layer git denies; LLM defaults to the latest OpenAI astra model on OpenAI-compatible transport. System version 9.29.0 → 9.30.0, prompt rebuilt (81684 bytes), sync check passed.
 
 - **Persona boundaries + mode-aware ferry (Task 204):** self-judgment follow-up — Planner vs Strategist and Architect vs Programmer gained one-line ownership boundaries (WHAT vs HOW, state vs priority); QA + Reviewer ferry language made mode-aware (manual ferry vs autopilot direct call); Architect Discovery-First triple coverage trimmed to prohibition + single directive. System version 9.28.0 → 9.29.0, prompt rebuilt, sync check passed.
diff --git a/LLM.txt b/LLM.txt
index 7cc7eb4..2d5c0b0 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -460,6 +460,30 @@ Cloudflare Tunnel (`managed-remote` with your domain + account token) is the nex
 
 ---
 
+## 7.10. Systemd User Service Env (If OpenCode Runs as a Daemon)
+
+If the user runs OpenCode via a systemd user unit (e.g. `opencode-server.service`
+for OpenChamber), the daemon starts with a bare environment — shell exports do
+not apply and `{env:VAR}` forwarding in `opencode.json` resolves empty. Add the
+env file to the unit so the bridge/decision servers start with keys:
+
+```ini
+[Service]
+# Project env (keys + model pins). '-' = unit still starts if file is missing.
+EnvironmentFile=-<project-path>/.env
+# Portable alternative: EnvironmentFile=%h/.config/opencode/.env
+```
+
+Then `systemctl --user daemon-reload` (safe anytime). The vars take effect on the
+next `systemctl --user restart opencode-server` — the restart kills live
+sessions, so the USER runs it, never the agent. Verify with
+`systemctl --user show opencode-server.service -p EnvironmentFiles`.
+As process env these vars outrank every `.env` file fallback, so all projects
+served by the daemon share them. Per-project overrides still work via that
+project's own `.env` only for keys the daemon env does NOT set.
+
+---
+
 ## 8. Clean Up Temporary Clone
 
 Remove the cloned repository from `/tmp/`:
diff --git a/docs/setup.md b/docs/setup.md
index 29819f3..fede78d 100644
--- a/docs/setup.md
+++ b/docs/setup.md
@@ -65,6 +65,26 @@ These are configured in `opencode.json` and auto-start with OpenCode.
 > (`brain_turn`).
 > Global installs additionally run `blowsh` + `telegram`.
 
+### Systemd user service env
+
+When OpenCode runs as a systemd user service (`opencode-server.service`),
+the daemon starts with a bare environment — no shell exports apply. Give
+it the project env explicitly so `{env:VAR}` forwarding in `opencode.json`
+resolves and the bridge/decision servers start with keys:
+
+```ini
+[Service]
+EnvironmentFile=-/home/mohammad/code-server/projects/cognitive-lead-hq/.env
+```
+
+Portable form for other machines: `EnvironmentFile=%h/.config/opencode/.env`.
+After editing: `systemctl --user daemon-reload` (safe anytime), then
+`systemctl --user restart opencode-server` to take effect — the restart
+kills live sessions, so the manager runs it, never the Hands. Verify with
+`systemctl --user show opencode-server.service -p EnvironmentFiles`.
+As process env, these vars outrank every `.env` file fallback, so all
+projects served by the daemon share them.
+
 ## Development Tools
 
 ```bash
```
<!-- END_GIT_DIFF -->
