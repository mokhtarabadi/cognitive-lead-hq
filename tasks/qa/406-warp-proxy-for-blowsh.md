# Task 406: Run Cloudflare WARP in Docker as blowsh proxy, document the setup

**File:** `tasks/qa/406-warp-proxy-for-blowsh.md`
**Source:** manager
**Type:** infrastructure + documentation
**Status:** qa
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
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 6bf568d..9129272 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Docker-side Cloudflare WARP proxy for blowsh (task 406):** added `docs/blowsh-warp-proxy.md` with the verified procedure to run `ghcr.io/mon-ius/docker-warp-socks:v8` on a `warp-net` bridge and connect `blowsh-singleton` with `PROXY_TYPE=http` to `warp-socks:9091`. Live verification showed `warp=on`, exit IP `104.28.211.187`, a successful browser render, and axios egress through WARP. The guide explains why container-to-host proxying fails here, how to verify the exit, rollback steps, and troubleshooting. Docs living files and a dated ADR were updated.
 - **OpenUI validity gate for native render (task 405):** the executor's Output Contract now carries exact positional signatures for `Stack`, `Table`, `Callout`, `Steps` and `KeyValue`, requires plain string or number `Table` cells, bans named arguments, and demands a bracket/statement self-check before every `openchamber_render` call. A render diagnostic is read from the submitted source rather than its wording, because `lang-core` reports arity when bracket recovery fails. The same contract is mirrored into `prompts/fragments/09-hands_protocols.md`, the version is bumped 9.89.0 → 9.90.0, and `system-prompt.md` plus stage artifacts are regenerated by the assembler. Regression assertions pin both surfaces; agent, fragment and tests living docs updated.
 - **Bridge chat completions to responses API in mcp-brain-bridge (task 401):** added `BRAIN_UPSTREAM_MODE` (`responses` by default, `chat_completions` optional) allowing the Brain to talk to standard OpenAI-compatible `/chat/completions` providers (such as MiniMax Flash or custom OpenAI chat proxies). Implemented bidirectional payload mapping: translates `instructions` + `input` into role-tagged `messages`, converts `max_output_tokens` to `max_tokens`, maps `reasoning.effort` to `reasoning_effort`, and transforms `/chat/completions` output back into the Responses API shape (`choices[0].message.content` into `output` message blocks, usage tokens mapped) without regressing existing Responses API functionality. Added offline unit tests in `tests/test_brain_bridge.py`.
 - **Structured tool-call channel for the Brain output (META 403, task 402):** `brain_turn` now returns an additive `tool_calls` list alongside `output` — one entry per `function_call` item in the normalized Responses-shaped output list, each with `call_id`, `name`, `arguments` (parsed dict), `arguments_raw` (original string), and `source` (`responses` or `chat_completions`). Both upstream modes share the single `extract_tool_calls` extractor, so the shape is identical by construction; `parse_responses_text` is unchanged per ADR-014. Added 6 offline unit tests (both modes, prose-empty, malformed-JSON fallback, dict scalar nonlist inputs, brain_turn wiring); full suite 360 passed.
diff --git a/docs/DECISIONS.md b/docs/DECISIONS.md
index 1e47ae4..611fc90 100644
--- a/docs/DECISIONS.md
+++ b/docs/DECISIONS.md
@@ -27,3 +27,10 @@
 - **Decision:** The complete runbook is `docs/openchamber.md` §10 (install, headless-shell over apt-chromium, `--no-sandbox` wrapper, `config.json`, daily use, troubleshooting, snap removal); `LLM.txt` carries a §7.10 pointer plus a verification-checklist line.
 - **Consequences:** Future browser setups follow one doc instead of rediscovery.
 - **Rollback:** Delete §10, §7.10, and the checklist line.
+
+## [2026-11-18] ADR-005: WARP proxy lives inside Docker, not on the host
+
+- **Context:** The host proxy on port 7890 is unreachable from every bridge container because the host firewall drops container-to-host connections on all tested ports. A live container-to-container test on the same bridge returned `BRIDGE_OK`. The VPS IP is not clean enough for the web research workload, so a clean exit is required.
+- **Decision:** Run `ghcr.io/mon-ius/docker-warp-socks:v8` on a dedicated `warp-net` bridge and connect blowsh with `PROXY_TYPE=http` to `warp-socks:9091`. HTTP mode is required because the Node-side axios has no SOCKS agent. Loopback stays in `PROXY_BYPASS` to protect the Browsh control channel. The full procedure is `docs/blowsh-warp-proxy.md`.
+- **Consequences:** Browser renders and axios egress both use the Cloudflare WARP exit IP. The shared WARP IP may still be blocked by some sites, and the no-proxy setup remains the documented rollback.
+- **Rollback:** Recreate blowsh with `PROXY_TYPE=none`, remove `warp-socks`, and delete the guide.
diff --git a/docs/README.md b/docs/README.md
index b3753ff..b556298 100644
--- a/docs/README.md
+++ b/docs/README.md
@@ -8,6 +8,7 @@ Human-readable spec hub for conventions, architecture-adjacent guides, service t
 
 - `conventions.md` — Syntax, naming, file boundaries, and automation patterns (bound spec).
 - `brain-bridge.md` — Brain Bridge protocol reference for QA/review turns.
+- `blowsh-warp-proxy.md` — Operator guide for giving blowsh a clean outbound IP via a Docker-side Cloudflare WARP proxy.
 - `compaction.md` — Context compaction and smart-compact usage.
 - `openchamber.md` — OpenChamber session linking guide.
 - `opencode-shell-strategy.md` — Shell execution strategy.
diff --git a/docs/blowsh-warp-proxy.md b/docs/blowsh-warp-proxy.md
new file mode 100644
index 0000000..761bf6a
--- /dev/null
+++ b/docs/blowsh-warp-proxy.md
@@ -0,0 +1,125 @@
+# blowsh with a Docker-side Cloudflare WARP proxy
+
+This guide gives the blowsh MCP server a clean outbound IP by running a Cloudflare WARP proxy container on the same Docker network. It was verified on 2026-11-18 with `ghcr.io/mon-ius/docker-warp-socks:v8` and `blowsh-mcp:latest`.
+
+## Why this pattern
+
+On this VPS the host firewall drops every container-to-host TCP connection. A bridge container cannot reach a proxy listening on the host, whether that proxy is on `7890`, `8118`, `3005` or `8081`. Container-to-container traffic on a Docker bridge does not traverse the host INPUT chain, so a proxy container on the same network is reachable. This was verified with a live `BRIDGE_OK` response between two containers.
+
+The WARP exit IP is shared Cloudflare infrastructure, not a dedicated residential IP. It is cleaner than the VPS IP but some sites still block it. Keep the no-proxy setup as the rollback path.
+
+## Prerequisites
+
+- Docker with permission to create networks and containers.
+- `blowsh-mcp:latest` built from `/home/mohammad/blowsh-mcp` at the current HEAD.
+- The `browsh-profile` named volume. It preserves Firefox profile state across container recreation.
+
+## Deploy the WARP proxy
+
+Create a dedicated network so container names resolve through Docker DNS:
+
+```bash
+docker network create warp-net
+```
+
+Run the proxy. This image needs no privileged mode and no `NET_ADMIN`:
+
+```bash
+docker run -d --name warp-socks --restart unless-stopped --network warp-net \
+  -e NET_PORT=9091 \
+  ghcr.io/mon-ius/docker-warp-socks:v8
+```
+
+The container registers with Cloudflare automatically and serves both HTTP and SOCKS5 on port `9091`. It keeps private-network traffic local, which protects the Browsh localhost control channel.
+
+## Verify the WARP exit
+
+Run this from another container on `warp-net`, not from the host:
+
+```bash
+docker run --rm --network warp-net --entrypoint sh ghcr.io/mon-ius/docker-warp-socks:v8 \
+  -c 'curl -x http://warp-socks:9091 -fsSL https://cloudflare.com/cdn-cgi/trace'
+```
+
+The result must contain `warp=on` and an `ip=` line. In the verified run the IP was `104.28.211.187` with `loc=FR`. Record the IP you get; it will differ on another day.
+
+## Connect blowsh
+
+Recreate the singleton on the same network. Environment variables are fixed at container creation, so `docker container update` cannot add them. Preserve the name, port binding, volume, restart policy, transport, and the existing `BROWSH_*` timeouts:
+
+```bash
+docker stop blowsh-singleton && docker rm blowsh-singleton
+
+docker run -d --name blowsh-singleton --restart unless-stopped --network warp-net \
+  -p 127.0.0.1:8107:8107 \
+  -v browsh-profile:/data/browsh-profile \
+  -e MCP_TRANSPORT=http -e MCP_HOST=0.0.0.0 -e MCP_PORT=8107 \
+  -e BROWSH_STARTUP_TIMEOUT_MS=120000 \
+  -e BROWSH_QUEUE_TIMEOUT_MS=600000 \
+  -e BROWSH_REQUEST_TIMEOUT_MS=180000 \
+  -e SEARCH_DEADLINE_MS=900000 \
+  -e BROWSH_CRASH_WINDOW_MS=60000 \
+  -e BROWSH_CRASH_THRESHOLD=3 \
+  -e BROWSH_CRASH_COOLDOWN_MS=30000 \
+  -e BROWSH_PROFILE_DIR=/data/browsh-profile \
+  -e BROWSH_COLS=160 -e BROWSH_ROWS=60 \
+  -e PROXY_TYPE=http -e PROXY_HOST=warp-socks -e PROXY_PORT=9091 \
+  -e PROXY_BYPASS=localhost,127.0.0.1 \
+  blowsh-mcp:latest
+```
+
+Use `PROXY_TYPE=http`, not `socks5`. blowsh's Firefox is fully SOCKS5-capable, but the Node-side axios calls have no SOCKS agent in this image. The HTTP mode covers both paths. Never remove `localhost,127.0.0.1` from `PROXY_BYPASS`: the Browsh control channel listens on `127.0.0.1:4333`.
+
+## Verify blowsh
+
+Health and readiness:
+
+```bash
+curl -sS http://127.0.0.1:8107/health
+docker exec blowsh-singleton cat /data/browsh-profile/.config/browsh/firefox_profile/user.js
+```
+
+The generated `user.js` must show `network.proxy.type 1`, host `warp-socks`, port `9091`, and `no_proxies_on` containing `localhost, 127.0.0.1`. The file is written on first render in HTTP mode, so trigger one fetch before judging it:
+
+```bash
+curl -sS http://127.0.0.1:8107/mcp \
+  -H 'Content-Type: application/json' \
+  -H 'Accept: application/json, text/event-stream' \
+  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"fetch_web","arguments":{"url":"https://example.com","type":"markdown"}}}'
+```
+
+Confirm the clean exit through blowsh itself:
+
+```bash
+docker exec blowsh-singleton curl -sS -x http://warp-socks:9091 \
+  https://cloudflare.com/cdn-cgi/trace | grep -E '^(ip|warp)='
+```
+
+A successful browser render of `https://example.com` plus `warp=on` in the trace is the full acceptance test.
+
+## Rollback
+
+```bash
+docker stop blowsh-singleton && docker rm blowsh-singleton
+docker run -d --name blowsh-singleton --restart unless-stopped \
+  -p 127.0.0.1:8107:8107 \
+  -v browsh-profile:/data/browsh-profile \
+  -e MCP_TRANSPORT=http -e MCP_HOST=0.0.0.0 -e MCP_PORT=8107 \
+  -e BROWSH_PROFILE_DIR=/data/browsh-profile \
+  -e PROXY_TYPE=none blowsh-mcp:latest
+docker rm -f warp-socks
+```
+
+The server rewrites `user.js` to `network.proxy.type 0` on the next boot. Removing the WARP container leaves the network in place for a future retry.
+
+## Troubleshooting
+
+- **`warp=off`** — registration failed. Check `docker logs warp-socks`. Recreate the container to register again.
+- **Blowsh renders time out** — check that both containers are on `warp-net` and that `docker exec blowsh-singleton getent hosts warp-socks` resolves.
+- **Local pages break** — `PROXY_BYPASS` lost its loopback entries. Restore `localhost,127.0.0.1`.
+- **Host proxy tried instead** — not supported here; the host firewall blocks container-to-host traffic. Keep the proxy inside Docker.
+
+## References
+
+- `ghcr.io/mon-ius/docker-warp-socks:v8` — <https://github.com/Mon-ius/Docker-Warp-Socks>
+- Host firewall finding and container-to-container verification are recorded in task 406.
```
<!-- END_GIT_DIFF -->
