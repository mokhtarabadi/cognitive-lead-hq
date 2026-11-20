# Task 407: Optional WARP and Psiphon Docker proxies for blowsh

**File:** `tasks/completed/407-psiphon-proxy-for-blowsh.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Finished:** 2026-11-20T11:04:40Z
**Submitted:** 2026-11-20T10:28:07Z
**Started:** 2026-11-20T09:41:35Z

## Goal

Provide two properly Dockerized, optional proxy backends for blowsh, WARP and Psiphon, so the user can pick either one or run direct. Neither is mandatory. The proxy is selected only by `PROXY_*` variables on `blowsh-singleton`.

## Final outcome (updated 2026-11-20)

The task went through three operator decisions. First, move from WARP to Psiphon. Second, remove all proxies after the Psiphon deployment exposed the real blowsh source bug. Third, and final, keep **both** proxies as Dockerized optional backends, because the user needs a choice. The underlying source fix is tracked in the `blowsh-mcp` repository as task 269; this HQ task now owns both proxy build contexts and the mode documentation.

Current live state: `psiphon-socks` is running on `warp-net` with `EgressRegion=US`, and `blowsh-singleton` uses `PROXY_TYPE=http`, `PROXY_HOST=psiphon-socks`, `PROXY_PORT=8082`. Direct and WARP remain available as opt-in alternatives.

**Assumption A5:** direct egress stays the documented default because it works everywhere; WARP and Psiphon are opt-in. Reason: the operator said the proxies are optional and user-selected, not mandatory.
**Assumption A6:** no new task is created for this change. Reason: the operator explicitly asked to change the recent task in place.

## Manager's Notes

Manager input was Persian. Translated intent: "Study the codebase; find everything about blowsh and WARP set up as proxy together. Move completely off WARP. Go to Psiphon, bring up a Docker image with Psiphon inside, get a clean US proxy, connect and use it. To learn the configuration and build the Dockerfile, use a Mihemo-exit project in the home folder; if that is missing, find the config of the Psiphon already running on the system. Move fully from WARP to this."

Corrections applied: سایفون → Psiphon; میهمو → mihomo; بلوش → blowsh; وارپ → WARP. No Mihemo-exit project exists under `/home/mohammad`, so the Manager-approved fallback applies: use the live system Psiphon config and the vendored apex reference.

Manager decisions collected through the approval gate:
- Kanban: create this task file in `tasks/backlog/`.
- Egress: bake `EgressRegion=US` into the new image and prove the exit country with a live trace.
- Plan: approved as stated, under ZAC and the QA/review gates.
- Final instruction (Persian): "We need to have a proxy, and we have two types of proxy: WARP and Psiphon. Each should be properly Dockerized and optional; if the user wants, they can use it for blowsh. Change the recent task; do not create a new one." Translated and applied as the final scope above.

Relevant reference pattern: `apex/tasks/archive/285-add-psiphon-egress-sidecar-for-tonnel.md` (ubuntu:20.04 + `psiphon-tunnel-core` + baked config, SOCKS 1081 / HTTP 8082, internal-only, no published ports) and `/home/mohammad/apex/psiphon/psiphon.config`.

ZAC holds: no `git add`, `git commit`, `git checkout`, or `git push`.

## Relevant Code Context

- `docs/blowsh-warp-proxy.md` — current WARP source of truth; `warp-socks` on `warp-net` serves HTTP + SOCKS5 on `9091`; blowsh wired with `PROXY_TYPE=http`, `PROXY_HOST=warp-socks`, `PROXY_PORT=9091`, `PROXY_BYPASS=localhost,127.0.0.1`.
- `docs/services.md` — service/port table that lists blowsh on 8107.
- `docs/README.md` — doc index that links the proxy guide.
- `docs/DECISIONS.md` — ADR log; needs a dated ADR for the egress change.
- `.opencode/memory/opencode_config/blowsh_image_policy.md` — states the WARP proxy "remains mandatory at deployment"; must be superseded.
- `tasks/qa/406-warp-proxy-for-blowsh.md` — predecessor that introduced WARP.
- `CHANGELOG.md` — Keep a Changelog; Parse-Then-Append required.

## Local TODOs

- [x] Move task to `tasks/in-progress/` before editing
- [x] Create the `psiphon-proxy/` build context with a Dockerfile and baked `psiphon.config` (`EgressRegion=US`, HTTP 8082, SOCKS 1081)
- [x] Create the `warp-proxy/` build context wrapping the pinned upstream image with `NET_PORT=9091` baked
- [x] Rebuild and run `psiphon-socks` on `warp-net` with no published ports; prove US egress via a trace
- [x] Recreate `blowsh-singleton` on the fixed image with the Psiphon `PROXY_*` variables; verify render and browser-side trace
- [x] Add `docs/blowsh-proxy-options.md`, rewrite the mode guides, update living docs and CHANGELOG via Parse-Then-Append
- [x] Run verification, lint the task, re-stage via MCP in `tasks/qa/`

## Acceptance Criteria

- [x] Root cause proven and fixed in blowsh source (task 269); the old 800 ms probe failed with or without a proxy.
- [x] Two repo-owned Docker build contexts exist: `warp-proxy/` (pinned upstream wrapper, `NET_PORT=9091`) and `psiphon-proxy/` (`psiphon-tunnel-core`, `EgressRegion=US`, HTTP 8082 / SOCKS 1081).
- [x] Both proxies are optional: neither is mandatory; `docs/blowsh-proxy-options.md` documents direct, WARP, and Psiphon modes and the `PROXY_*` variables for each.
- [x] `psiphon-socks` runs on `warp-net` with no published ports and a healthy US egress; `blowsh-singleton` is wired to it on the fixed image.
- [x] A real `fetch_web` render on `https://example.com` returns page text with `isError:false`, and a browser-side trace shows `loc=US`, `warp=off`, `ip=104.131.189.185`.
- [x] `docs/blowsh-warp-proxy.md`, `docs/blowsh-direct-egress.md`, `docs/blowsh-psiphon-proxy.md`, `docs/README.md`, `docs/DECISIONS.md`, and `CHANGELOG.md` are updated; memory policy no longer marks any proxy mandatory.
- [x] `lint_task_file` passes and the final diff is staged via MCP; no new task was created.

## Verification Evidence

- **Test command:** `rtk test uv run --with pytest==8.3.5 --with mcp==1.30.0 --with httpx==0.28.1 --with pathspec==0.12.1 --with pyyaml==6.0.2 python -m pytest tests/ -q`
- **Expected result:** full suite passes with exit code 0.
- **Actual result:** `916 passed, 1 warning in 81.05s (0:01:21)`.
- **Exit code:** `0`.
- **Strict tooling gate:** docs-only HQ repo; no code stack changed here. The code fix and its strict `tsc` + three offline suites are recorded in `blowsh-mcp` task 269.
- **Memory evidence:** `opencode_config/blowsh_image_policy` overwritten via `store_memory` — WARP mandate removed, direct egress recorded, temporary local-image exception documented.

> Verification runner rule: the command above is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

**Deployment evidence (pivot outcome):**
- Psiphon image `psiphon-proxy:us` built (exit 0), container healthy, trace through `psiphon-socks:8082` returned `ip=159.65.246.226`, `loc=US`, `warp=off`.
- blowsh recreated with `PROXY_HOST=psiphon-socks`, `PROXY_PORT=8082`; generated `user.js` showed host `psiphon-socks`, port `8082`, loopback bypass intact.
- `fetch_web` still failed with the 800 ms probe timeout; raising `BROWSH_STARTUP_TIMEOUT_MS` to 300 s and changing the startup page made no difference. Direct HTTP probe on `127.0.0.1:4333` returned 200 while axios with 800 ms timed out. Root cause located in blowsh source `src/browshManager.ts:549`.
- Fixed source built with strict `tsc` (exit 0); offline suites passed 45/45, 17/17, 29/29; local image `blowsh-mcp:local-fix` built (exit 0).
- Final live run with `PROXY_TYPE=none`: health `{"status":"ok","transport":"streamable-http"}`, `fetch_web` on `https://example.com` returned real page text with `isError:false` in 10 s; logs show `acquire`/`release`. `docker rm -f warp-socks psiphon-socks` succeeded.
- **Final optional-proxy verification (after the operator rebuilt blowsh):** fresh `blowsh-mcp:latest` contains the `healthProbeTimeoutMs` fix. `psiphon-socks` rebuilt from `psiphon-proxy/` and started on `warp-net`; logs show `ConnectedServerRegion: US` and health `healthy`; trace through `psiphon-socks:8082` returned `ip=104.131.189.185`, `loc=US`, `warp=off`. `blowsh-singleton` recreated on the fixed image with `PROXY_TYPE=http`, `PROXY_HOST=psiphon-socks`, `PROXY_PORT=8082`, `PROXY_BYPASS=localhost,127.0.0.1`; generated `user.js` has `network.proxy.type=1` and `network.proxy.http=psiphon-socks`. `fetch_web` on `example.com` succeeded in 10 s; `fetch_web` on the Cloudflare trace URL returned the same US IP. Psiphon mode left enabled as requested.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `testing-verification` applied and evidence recorded
- [x] No autonomous commit; staged via `custom_context_stage_and_inject_diff`

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Psiphon exit IPs are shared and rotating, may still be flagged by some sites, and `EgressRegion` is a preference rather than a guarantee. A fresh tunnel may take time to register or may fail from this VPS.
- **Rollback plan:** recreate `blowsh-singleton` with `PROXY_TYPE=none`, remove `psiphon-socks` and its image, and restore the previous guide from git history. No migration and no data change.

---

## Execution Log & Reasoning

**Seat Check:** domains = Docker egress infrastructure plus HQ documentation → Software Architect requested (new infrastructure design and an ADR). UI/UX Designer skipped (no layout, styling, or user-visible screen). Senior Programmer skipped (no race, deadlock, flaky, or silent-failure trigger). No trigger word map hit on the title or body; duty-selected. Brainstorm: not required — the change is reversible, has a documented rollback, and follows an already verified sidecar pattern.

**Plan verdict:** Manager-approved three-step plan from the approval gate: build and run the US Psiphon image on `warp-net`; rewire blowsh and remove WARP; sync docs, memory, CHANGELOG, and stage.

**Mode:** AUTOMATIC (autopilot locked 2026-11-20). The Hands chains QA and review turns directly; only the closure approval word remains a human gate. ZAC holds: no `git add`, `git commit`, `git checkout`, or `git push`.

**Assumption A1:** the host firewall still drops container-to-host TCP, so the Psiphon proxy must live inside Docker on `warp-net`, matching the WARP finding. Reason: unchanged host firewall and the predecessor's verified `BRIDGE_OK` result.

**Assumption A2:** `PROXY_TYPE=http` stays, using the HTTP port `8082`, because blowsh's Node-side axios has no SOCKS agent. Reason: documented in `docs/blowsh-warp-proxy.md` line 71.

**Assumption A3:** sponsor, propagation, and server-list IDs from the vendored apex config are public client identifiers and can be reused in the baked config. Reason: recorded in apex task 285 execution log. Superseded by the pivot; the build context was removed.

**Pivot reasoning (2026-11-20):** the Psiphon container worked and produced a verified US exit, but blowsh could not start through it. Diagnosis proved the failure was independent of the proxy: with proxying fully off, Browsh's control endpoint answered HTTP 200 in 0.9–2 s while the hardcoded 800 ms axios probe in `src/browshManager.ts:549` always timed out. The operator then ordered the proxy stack removed and the source fixed. Both decisions are recorded here and in the `blowsh-mcp` fix task.

**Deployment caveat:** the running container uses the locally built `blowsh-mcp:local-fix`. The HQ memory rule requiring the remote auto-built `:latest` image is superseded only until the source fix is pushed to the GitHub image repository; that push is Manager-owned under ZAC.

**Final scope change (2026-11-20):** the operator rebuilt the fixed blowsh image, asked to restore Psiphon with a US exit, and confirmed the render works. The last instruction requires both WARP and Psiphon as properly Dockerized optional backends and an in-place change to this task with no new task. Recorded as assumptions A5 and A6. The two build contexts were recreated and verified; mode documentation and the memory policy were updated. The live Psiphon setup was left enabled because the operator said to keep a working proxy.

**Audit clearance:** the earlier proxy removal did not cause the startup failure, so restoring a proxy carries no regression risk with the fixed image. Verified live by rendering through Psiphon and checking the browser-side exit IP.

**Autopilot review chain (2026-11-20):** QA turn → `QA_PASSED`. Code Reviewer turn → technically approved, `PO_REVIEW_PENDING`. Reviewer notes R1 (pin the Psiphon binary digest), R2 (run both proxy images as non-root), and R3 (narrow the "all modes verified" claim). R1 and R2 are hardening follow-ups outside this scope and are recorded as non-blocking. R3 was applied immediately: `docs/blowsh-proxy-options.md` now states that Psiphon and direct were verified live, the WARP image builds, and WARP needs a fresh `warp=on` trace when next enabled. No blocking findings; no fix loop. Awaiting only the closure approval word.

**Closure approval (2026-11-20):** Manager answered the relayed closure question with the exact phrase "Approved for closure". Verified the file is still in `tasks/qa/` and the log still records `PO_REVIEW_PENDING` before closing. Closure XML issued once by the Senior Programmer and executed exactly once.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `cded157a2f2d3ee43123c643095f81ea672c7d75`
<!-- END_GIT_DIFF -->
