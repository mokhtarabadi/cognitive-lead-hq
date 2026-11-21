# Task 408: Fix OpenChamber service CLI path after reboot

**File:** `tasks/qa/408-fix-openchamber-service-cli-path.md`
**Source:** manager
**Type:** bug
**Status:** open
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

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 601976a..8b64e6e 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -11,6 +11,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **blowsh egress is direct; WARP and Psiphon retired:** the operator asked to move blowsh from Cloudflare WARP to a Psiphon Docker proxy with a US exit. Deployment exposed the real defect: blowsh's source had a hardcoded 800 ms health-probe timeout against Browsh's `/` endpoint, which takes 0.9–2 s here, so startup was always declared failed even though the endpoint answered HTTP 200. Fixed in the `blowsh-mcp` source with `BROWSH_HEALTH_PROBE_TIMEOUT_MS` (default 5000 ms) and no profile quarantine on a pure probe timeout. A real `fetch_web` render now succeeds in about 10 s with `PROXY_TYPE=none`. Removed `warp-socks` and `psiphon-socks`, retired the `psiphon-proxy/` build context, rewrote `docs/blowsh-warp-proxy.md` as history, added `docs/blowsh-direct-egress.md`, and updated `docs/README.md` and a dated ADR. The interim local image `blowsh-mcp:local-fix` is deployed until the source fix is pushed to the GitHub image repository. See task 269 in `blowsh-mcp` and task 407 in this repo.
 - **Both proxies restored as optional backends (supersedes the retirement above):** the operator clarified that blowsh must have two properly Dockerized, opt-in proxies. Added repo-owned build contexts `warp-proxy/` (thin wrapper over the pinned upstream image with `NET_PORT=9091` baked) and `psiphon-proxy/` (Ubuntu 22.04 with `psiphon-tunnel-core`, baked `EgressRegion=US`, HTTP `8082` / SOCKS `1081`). Direct egress remains the default; neither proxy is mandatory. Added `docs/blowsh-proxy-options.md` as the mode comparison and rewrote `docs/blowsh-warp-proxy.md` and `docs/blowsh-direct-egress.md` as live option guides, added `docs/blowsh-psiphon-proxy.md`, and updated `docs/README.md` and a dated ADR. Live Psiphon mode was verified on the fixed blowsh image: browser-side trace `ip=104.131.189.185`, `loc=US`, `warp=off`, and `fetch_web` rendered `example.com` in about 10 s. The current deployment keeps Psiphon enabled. Task 407 updated in place; no new task created.
 
+### Fixed
+
+- **OpenChamber service repaired after reboot `MODULE_NOT_FOUND` (task 408):** the `@openchamber/web` 2.7.3 upgrade on 2026-11-20 moved the npm CLI entry point from `bin/cli.js` to `build/bin/cli.js`, but the hand-written `~/.config/systemd/user/openchamber.service` still pinned the old path, so the unit crash-looped every 5 seconds after the reboot (restart counter 47+). Corrected `ExecStart` to the `build/bin/cli.js` path, kept a `.bak-20261121` copy of the unit, and verified the service stays active with port 3005 listening and HTTP 200. Added the post-upgrade unit-verification rule to `LLM.txt` §7.9 and `docs/openchamber.md` §4/§8, and refreshed the version table to the live OpenCode 2.3.2 / OpenChamber 2.7.3. ZAC holds; no commit.
+
 ## [9.90.0] - 2026-11-20
 
 ### Added
diff --git a/LLM.txt b/LLM.txt
index 6c746d5..38009ae 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -76,14 +76,14 @@ If `opencode --version` shows 1.x, back up `~/.config/opencode/opencode.json` fi
 
 ### Upgrading OpenCode / OpenChamber — the full refresh chain
 
-Upgrading a binary is NOT an upgrade of the install. The OpenCode binary lives at `~/.opencode/bin/opencode`; OpenChamber is the npm package `@openchamber/web` (global, under mise node). The **servers, skills, agents, prompts and plugins** are separate copies in `~/.config/opencode/` and do not move when either binary is replaced. A binary-only upgrade leaves the harness on the old code — that is the drift this chain exists to prevent.
+Upgrading a binary is NOT an upgrade of the install. The OpenCode binary lives at `~/.opencode/bin/opencode`; OpenChamber is the npm package `@openchamber/web` (global npm install under the active Node version). The **servers, skills, agents, prompts and plugins** are separate copies in `~/.config/opencode/` and do not move when either binary is replaced. A binary-only upgrade leaves the harness on the old code — that is the drift this chain exists to prevent.
 
 Run the whole chain, in this order:
 
 ```bash
 # 1. Upgrade the binaries.
 curl -fsSL https://opencode.ai/v2/install | bash        # OpenCode V2 only
-npm install -g @openchamber/web@latest                   # OpenChamber (mise node)
+npm install -g @openchamber/web@latest                   # OpenChamber (global npm)
 opencode --version && openchamber --version
 
 # 2. Re-sync every global install target from the fresh clone (Step 5, 6, 6.5).
@@ -724,6 +724,28 @@ sudo loginctl enable-linger $USER          # start at boot without login
 
 Re-run `openchamber startup enable` after any env/password change (it rewrites `startup.env`). Remove with `openchamber startup disable`.
 
+### After an `@openchamber/web` upgrade — verify the boot unit
+
+The npm package may move its CLI entry point between versions. In 2.7.x it
+moved from `bin/cli.js` to `build/bin/cli.js`, so any hand-written unit that
+pinned the old path crashed on the next boot with `MODULE_NOT_FOUND` and
+`activating (auto-restart)`. Regenerate the unit after every upgrade, then
+prove it is healthy:
+
+```bash
+npm install -g @openchamber/web@latest
+openchamber startup enable --port 3005 --host 127.0.0.1   # rewrites the unit
+systemctl --user show openchamber -p ExecStart --value     # inspect the resolved path
+systemctl --user daemon-reload && systemctl --user restart openchamber
+systemctl --user is-active openchamber                     # expect active
+curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3005/   # expect 200
+```
+
+If a hand-written unit must be kept, resolve the real entry point with
+`node -p "require('@openchamber/web/package.json').bin.openchamber"` and point
+`ExecStart` at that path before restarting. Always check
+`journalctl --user -u openchamber -n 50` when the status shows auto-restart.
+
 ### Remote access (optional)
 
 ```bash
diff --git a/docs/openchamber.md b/docs/openchamber.md
index bd8fb3c..7b7f37d 100644
--- a/docs/openchamber.md
+++ b/docs/openchamber.md
@@ -10,8 +10,8 @@
 
 | Component | Version | Update command | Source of truth |
 | --- | --- | --- | --- |
-| OpenCode | 2.0.21 | `curl -fsSL https://opencode.ai/v2/install \| bash` (V2) | `opencode --version`; latest via `https://opencode.ai/update/api/latest/cli/npm` |
-| OpenChamber | 2.1.0 | `openchamber update` | `openchamber --version`; latest via `npm view @openchamber/web version` |
+| OpenCode | 2.3.2 | `curl -fsSL https://opencode.ai/v2/install \| bash` (V2) | `opencode --version`; latest via `https://opencode.ai/update/api/latest/cli/npm` |
+| OpenChamber | 2.7.3 | `npm install -g @openchamber/web@latest` | `openchamber --version`; latest via `npm view @openchamber/web version` |
 
 OpenChamber and OpenCode update **separately**. OpenChamber offers OpenCode
 updates in its UI and restarts the server afterward; you can also run the V2
@@ -77,6 +77,14 @@ Notes:
   minimal environment.
 - Re-run `startup enable` after changing env vars or the UI password — it
   rewrites `~/.config/openchamber/startup.env`.
+- Re-run `openchamber startup enable` after **every** `@openchamber/web`
+  upgrade. The npm package can move its CLI entry point between versions (2.7.x
+  moved it from `bin/cli.js` to `build/bin/cli.js`), and a hand-written unit that
+  pins the old path will then crash-loop with `MODULE_NOT_FOUND`. Regenerating
+  the unit makes it track the npm-managed entry point again. If you must keep a
+  hand-written unit, verify its path after each upgrade:
+  `systemctl --user show openchamber -p ExecStart --value`, then confirm the
+  target exists before restarting.
 - Manage it with `openchamber startup {status,enable,disable}`; inspect with
   `systemctl --user status openchamber`.
 - Uninstall: `openchamber startup disable` (stops + removes the service).
@@ -134,6 +142,7 @@ Full list: https://docs.openchamber.dev/environment/
 | UI does not load | `openchamber status`; open the URL it prints; confirm the port is listening (`ss -tlnp \| grep <port>`). |
 | "OpenChamber requires OpenCode 2.0.20 or newer" | Update OpenCode: `curl -fsSL https://opencode.ai/v2/install \| bash`, then restart OpenChamber. |
 | "OpenCode is restarting" never clears | OpenChamber pauses requests while the managed server starts; if stuck, `openchamber restart` and check `openchamber logs`. |
+| `MODULE_NOT_FOUND`, status `activating (auto-restart)`, exit 1 | The unit pins a CLI path that no longer exists after an `@openchamber/web` upgrade. `journalctl --user -u openchamber -n 50` shows the missing path; confirm the real entry point from `node -p "require('@openchamber/web/package.json').bin.openchamber"`, fix the unit (or re-run `openchamber startup enable`), then `systemctl --user daemon-reload && systemctl --user restart openchamber`. |
 | Not starting at boot | `openchamber startup status`; re-run `openchamber startup enable`; verify `loginctl show-user <user> \| grep Linger` → `yes`. |
 | Sessions visible but tools missing | Reconnect/restart; MCP servers must be reachable on their loopback ports (`docs/services.md`). |
```
<!-- END_GIT_DIFF -->
