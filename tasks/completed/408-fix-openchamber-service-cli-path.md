# Task 408: Fix OpenChamber service CLI path after reboot

**File:** `tasks/completed/408-fix-openchamber-service-cli-path.md`
**Source:** manager
**Type:** bug
**Status:** closed
**Finished:** 2026-11-21T06:54:28Z
**Submitted:** 2026-11-21T06:44:16Z

## Goal

Restore the `openchamber.service` systemd user unit that crash-loops after the 2026-11-21 reboot, and document the post-upgrade unit-verification rule so a future `@openchamber/web` upgrade cannot silently break the service again.

## Manager's Notes

Manager reported OpenChamber not working after a full system reboot and supplied `systemctl --user status openchamber` showing `activating (auto-restart)`, exit status 1. Direct request: find the issue and fix it, create a tracked task, update project docs including `LLM.txt`, and use the `code-search` skill to find every relevant doc.

Approved plan via question tool: correct the service `ExecStart` script path only, reload systemd, restart, and verify. No repo code is involved and ZAC holds.

## Local TODOs

- [x] Capture journal and unit evidence to identify the root cause
- [x] Locate the canonical CLI entry point in the installed npm package
- [ ] Correct the systemd unit `ExecStart` path
- [ ] Reload systemd, restart the service, and verify it stays up
- [ ] Update `LLM.txt`, `docs/openchamber.md`, and `CHANGELOG.md`
- [ ] Verify every edit and record evidence

## Acceptance Criteria

- [x] `openchamber.service` stays `active (running)` with no new auto-restarts
- [x] `ss -tlnp | grep 3005` shows a LISTEN socket owned by the service
- [x] `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3005/` returns 200
- [x] Journal shows a clean start with no `MODULE_NOT_FOUND`
- [x] `LLM.txt`, `docs/openchamber.md`, and `CHANGELOG.md` teach the post-upgrade unit-verification rule

## Verification Evidence

- **Service test command:** `XDG_RUNTIME_DIR=/run/user/1000 systemctl --user is-active openchamber` and `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3005/`
- **Expected result:** `active` and `200`
- **Actual result:** `active`; `ss -tlnp` showed `0.0.0.0:3005 LISTEN` owned by PID 18238; `curl` returned `200`; journal after the 07:35:48 restart shows `OpenChamber server listening on 0.0.0.0:3005`, managed OpenCode on `127.0.0.1:44011`, and `[PushWatcher] connected`, with no new `MODULE_NOT_FOUND`. `NRestarts=0` after the fix. Startup takes about 10 s, so the port is not bound immediately at `active`.
- **Exit code:** 0
- **Test command:** `rtk test /home/mohammad/.config/opencode/mcp-brain-bridge/.venv/bin/python -m pytest tests/ -q`
- **Expected result:** full HQ suite passes
- **Actual result:** `916 passed, 24 warnings in 93.68s`
- **Exit code:** 0
- **Stack gate skip record:** repo root `/home/mohammad/cognitive-lead-hq`; marker scan list `pyproject.toml`, `package.json`, `build.gradle.kts`, `vite.config.*`, `nuxt.config.*`, `nest-cli.json`, `prisma/schema.prisma`, `next.config.*`; matched skills list `[]` (`blowsh`, `code-search`, `debug-instrumentation`, `kanban-lifecycle` loaded for discipline only); reason phrase "documentation-only HQ repo plus one home-directory systemd unit; no application stack marker matches, so the base `rtk test` suite plus `lint_task_file` is the gate".
- **Environment prerequisite repaired:** the global brain-bridge venv lacked `pytest`, `pathspec`, and `pyyaml`; installed with `uv pip install --python ~/.config/opencode/mcp-brain-bridge/.venv/bin/python pytest pathspec pyyaml` so the repo suite could run.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `testing-verification` applied and evidence recorded

## Risk & Rollback

- **Risk:** restarting the daemon can briefly drop the active chat session.
- **Rollback plan:** restore the original unit from `/home/mohammad/.config/systemd/user/openchamber.service.bak-20261121`, run `systemctl --user daemon-reload`, then restart the service.

---

## Execution Log & Reasoning

**Gatekeeper:** no rule violation. Root cause is a stale path in a home-directory systemd unit, not repo code. ZAC holds: no `git add`, commit, checkout, or push. The only repo edits are documentation plus this task file.

**Skills loaded:** `debug-instrumentation` (silent crash-loop diagnosis), `code-search` (graph + grep over all docs), `kanban-lifecycle` (task creation), `blowsh` (upstream extension README cross-check).

**Changes:**

1. `~/.config/systemd/user/openchamber.service` — `ExecStart` CLI path changed from `@openchamber/web/bin/cli.js` to `@openchamber/web/build/bin/cli.js`. Node binary, port 3005, host 0.0.0.0, and all other arguments unchanged. A byte-for-byte backup is at `openchamber.service.bak-20261121`.
2. `docs/openchamber.md` — refreshed version table to the live OpenCode 2.3.2 / OpenChamber 2.7.3, switched the update command to `npm install -g @openchamber/web@latest`, added a §4 rule to re-run `openchamber startup enable` after every package upgrade, and added a §8 `MODULE_NOT_FOUND` troubleshooting row.
3. `LLM.txt` — corrected the stale "mise node" wording, added §7.9 "After an `@openchamber/web` upgrade — verify the boot unit" with the resolve/regen/restart/verify commands.
4. `CHANGELOG.md` — new Unreleased/Fixed entry via Parse-Then-Append (no duplicate header).

**Assumption A1:** the reboot itself did not change Node; `v26.13.1` is the only installed version and `openchamber --version` is 2.7.3, so the package layout change on 2026-11-20 is the sole cause. Logged, not guessed silently.

**Observation O1 (not changed):** the journal warns `OPENCHAMBER_UI_PASSWORD is not set` while bound to `0.0.0.0`; `startup.env` carries `OPENCHAMBER_ALLOW_UNAUTHENTICATED_LAN=true`. This is pre-existing and outside the approved plan, so it is surfaced to the Manager rather than changed.

**Verification:** `systemctl --user daemon-reload` and `restart` succeeded; first health check at ~7 s was premature (Type=simple marks active before bind), recheck at ~15 s showed the socket and HTTP 200. Full suite 916 passed with exit 0 after adding three missing test dependencies to the global brain-bridge venv.

**QA Engineer turn:** `VERDICT: QA_PASSED`. All five acceptance items had live proof. Non-blocking notes: R1 unauthenticated LAN exposure predates this fix; R2 the regenerated example uses 127.0.0.1 while the live unit binds 0.0.0.0; F1 the bin lookup returns a relative path needing manual absolute resolution; M1-M3 minor verification gaps. Cited LLM.txt:727, docs/openchamber.md:80, docs/openchamber.md:145, CHANGELOG.md:14.

**Code Reviewer turn:** `VERDICT: PO_REVIEW_PENDING` (technically APPROVED). Strengths S1-S4 covered correctness, docs, changelog hygiene, and tests/deployment. Non-blocking issues R1 (Medium, out of scope), R2 (Low), F1 (Low). "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish."

**Manager acceptance (question-tool answer, verbatim):** "Approved for closure". Recorded before any closure action. The task file was verified still in `tasks/qa/` at the time of acceptance.

**Closure authorized:** "Approved for closure" on 2026-11-21, lane verified `tasks/qa`.

## Closure Checklist

- [x] Step 1: verified lane `tasks/qa/`, all verdicts and the acceptance quote logged, staged set limited to the three docs plus this task file.
- [x] Step 2: set `Status: closed` and log the authorization line.
- [x] Step 3: lint, `git mv` to `tasks/completed/`, sync `File:` header.
- [ ] Step 4: verify staged set and run `custom_context_commit_and_clean_task`.
- [ ] Step 5: verify commits, record hashes, check documentation, output handoff.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

**Factual Git Diff:** Stored in Commit Hash: `cf2a5cc2cee8970e291b37777bdb2e1397b93d2a`
<!-- END_GIT_DIFF -->
