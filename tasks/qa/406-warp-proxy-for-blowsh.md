# Task 406: Run Cloudflare WARP in Docker as blowsh proxy, document the setup

**File:** `tasks/qa/406-warp-proxy-for-blowsh.md`
**Source:** manager
**Type:** infrastructure + documentation
**Status:** qa
**Finished:** 2026-11-18T19:06:06Z
**Submitted:** 2026-11-18T19:00:11Z

## Goal

Give blowsh a clean outbound IP by running a Cloudflare WARP proxy container on the same Docker bridge, connecting blowsh to it, and documenting the procedure in the HQ docs for future setup.

## Manager's Notes

Manager input was English: "Is fine do It and then doc it I future setup in our docs, then use blowsh with warp as proxy." Approved the previously proposed plan to deploy Mon-ius/Docker-Warp-Socks v8 on the bridge, verify WARP, and switch blowsh to it. Then chose "Create task file" for Kanban tracking.

Established before task creation: host firewall drops every container-to-host connection (7890, 8118, 3005, 8081 all timed out), while a live container-to-container test on the bridge returned `BRIDGE_OK`. Therefore a WARP container on the bridge avoids the firewall entirely. Best candidate is `ghcr.io/mon-ius/docker-warp-socks:v8`: no privileged mode, auto-registration, HTTP and SOCKS5 on port 9091, private-network bypass. Fallback `Diniboy1123/wasque` is SOCKS5-only.

ZAC holds: no `git add`, `git commit`, `git checkout`, or `git push`.

## Local TODOs

- [x] Move task to `tasks/in-progress/` before editing
- [x] Deploy WARP v8 container on the bridge; verify `warp=on` through Cloudflare trace
- [x] Recreate blowsh with proxy env pointing at the WARP container; verify render and clean IP
- [x] Write HQ doc for future setup; update docs living files and CHANGELOG
- [x] Run verification, lint task, stage, move to `tasks/qa/`

## Acceptance Criteria

- [x] A WARP container runs on the Docker bridge and `curl` through it to `https://cloudflare.com/cdn-cgi/trace` shows `warp=on`.
- [x] blowsh is recreated with a proxy pointing at the WARP container, on the same Docker network, preserving name, port, volume, and restart settings.
- [x] A blowsh `fetch_web` render succeeds through WARP and the Cloudflare trace from inside blowsh shows the WARP IP.
- [x] `docs/blowsh-warp-proxy.md` explains prerequisites, deploy, verify, connect blowsh, rollback, and the host-firewall reason this pattern is used.
- [x] Living docs and `CHANGELOG.md` are updated via Parse-Then-Append.
- [x] Full test suite passes with `rtk test`, `lint_task_file` passes, diff staged via MCP, task moved to `tasks/qa/`.

## Verification Evidence

- **Test command:** `rtk test uv run --with pytest==8.3.5 --with mcp==1.30.0 --with httpx==0.28.1 --with pathspec==0.12.1 --with pyyaml==6.0.2 python -m pytest tests/ -q`
- **Expected result:** full suite passes with exit code 0.
- **Actual result:** `916 passed, 1 warning in 76.39s`.
- **Exit code:** `0`.
- **Deployment evidence:** `docker pull ghcr.io/mon-ius/docker-warp-socks:v8` exit 0; `docker run` for `warp-socks` exit 0; HTTP and SOCKS5 traces both returned `warp=on` with `ip=104.28.211.187`, `loc=FR`; blowsh recreated exit 0 with `PROXY_TYPE=http`, health `{"status":"ok","transport":"streamable-http"}`; generated `user.js` shows `network.proxy.type 1`, host `warp-socks`, port `9091`, loopback bypass; `fetch_web` on `https://example.com` rendered successfully; trace through blowsh showed `uag=axios/1.19.0` and `warp=on`.
- **Strict tooling gate:** docs-only HQ repo; marker scan found no stack markers; matched stack skills `[]`; base gate is the RTK suite plus `lint_task_file`.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `testing-verification` applied and evidence recorded
- [x] No autonomous commit; staged via MCP

## Risk & Rollback

- **Risk:** WARP registration may fail from this VPS, or the shared WARP exit IP may still be blocked by some sites.
- **Rollback:** recreate blowsh with `PROXY_TYPE=none` on the bridge; remove the WARP container and image. No source code changes.

---

## Execution Log & Reasoning

- **Assumption A1:** "our docs" means the HQ `docs/` slice; `docs/blowsh-warp-proxy.md` was created there and listed in `docs/README.md`. Reason: the repository is a documentation hub and the operator guide belongs beside `openchamber.md` and `zen-proxy.md`.
- **Assumption A2:** `PROXY_TYPE=http` is preferable to `socks5` because blowsh's Node-side axios has no SOCKS agent; the WARP v8 image serves HTTP and SOCKS5 on the same port. Verified by a trace with `uag=axios/1.19.0` showing `warp=on`.
- Created a dedicated `warp-net` bridge so Docker DNS resolves `warp-socks` by name. No host port was published for the proxy, so the host firewall remains untouched.
- Deployed `ghcr.io/mon-ius/docker-warp-socks:v8` without privileged mode or `NET_ADMIN`. Registration succeeded automatically, and both HTTP and SOCKS5 traces returned `warp=on` with exit IP `104.28.211.187`.
- Recreated `blowsh-singleton` on `warp-net`, preserving the name, `127.0.0.1:8107` binding, `browsh-profile` volume, `unless-stopped` policy, transport, and all `BROWSH_*` timeouts. Added `PROXY_TYPE=http`, `PROXY_HOST=warp-socks`, `PROXY_PORT=9091`, `PROXY_BYPASS=localhost,127.0.0.1`.
- Verified health, generated `user.js`, a real browser render, and a clean-IP trace from inside blowsh. No source code or tests were changed in `blowsh-mcp`.
- Wrote `docs/blowsh-warp-proxy.md`; updated `docs/README.md`, `docs/DECISIONS.md` with a dated ADR, and `CHANGELOG.md` via Parse-Then-Append. No system-prompt edit, so no version bump.
- **Review (Code Reviewer, same session):** technically approved, `PO_REVIEW_PENDING`. R1 (Status open in qa) and R2 (final TODO unchecked) fixed above. R3 (task number in guide prose) fixed by replacing the visible reference with a generic pointer; the number stays in the task file and CHANGELOG. A3 is already satisfied: no host port for the WARP proxy and loopback remains in `PROXY_BYPASS`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `f68292fdb07b828aecca3187e71f5fe21fb15eb8`
<!-- END_GIT_DIFF -->
