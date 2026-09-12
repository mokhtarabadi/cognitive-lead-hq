# Task 206: Systemd user unit env for opencode-server + docs

**File:** `tasks/completed/206-systemd-user-unit-env-for-opencode-server-docs.md`
**Source:** manager
**Type:** improvement
**Status:** closed

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
**Factual Git Diff:** Stored in Commit Hash: `50ea9bc86b1e9bc9738e0ea68d2be80edaba3347`
<!-- END_GIT_DIFF -->
