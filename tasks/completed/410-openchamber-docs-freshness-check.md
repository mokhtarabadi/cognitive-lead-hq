# Task 410: OpenChamber docs freshness check against upstream

**File:** `tasks/completed/410-openchamber-docs-freshness-check.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Finished:** 2026-11-22T12:16:02Z

## Source Context

### Variant C: Manager (`**Source:** manager`)

## Goal

Verify that this repository's OpenChamber documentation matches the latest official upstream docs, using the `blowsh` skill for all live-web research. Report concrete drift with `file:line` citations on our side and source URLs on the upstream side, plus recommended doc patches. No product code, no commit.

## Manager's Notes

- Manager asked to create a task and run it under autopilot, and to use `blowsh` so we know the latest docs.
- Scope is documentation only: `docs/openchamber.md`, `LLM.txt` §7.9, `docs/setup.md`, and the `openchamber_render` call-envelope contract just added to `agents/cognitive-executor.md` and `prompts/fragments/09-hands_protocols.md`.
- Focus areas: current version table, environment variables (especially `OPENCHAMBER_ALLOW_UNAUTHENTICATED_LAN`), UI password and `startup enable` behavior, default host/port, and the `openchamber_render` tool call shape.
- Live-web reads must go through `blowsh` tools, never `curl`/`wget`. Cite every claim with an upstream URL.

## Local TODOs

- [ ] Probe official OpenChamber docs site with `blowsh_search_web` and `blowsh_crawl_web` map mode
- [ ] Fetch the pages that matter with `blowsh_fetch_web` and extract version, env var, auth, and startup facts
- [ ] Compare against our three doc surfaces plus the render-envelope contract, citing `file:line`
- [ ] Record a drift report with recommended patches in this task file

## Acceptance Criteria

- [x] Every factual claim about upstream OpenChamber behavior carries a source URL from `blowsh`
- [x] Every claim about this repository carries a `file:line` citation
- [x] The report lists each drift item with a concrete recommended doc patch
- [x] The report states explicitly when our docs match upstream, and when upstream is unreachable or unverifiable

## Verification Evidence

- **Test command:** rtk test python3 -m pytest tests/test_prompt_sync.py -q
- **Expected result:** the prompt-sync suite passes with the render-envelope contract intact
- **Actual result:** `44 passed in 0.38s`
- **Exit code:** `0`
- **Exact command run:** `rtk test /home/mohammad/hesab-ketab/.venv/bin/python -m pytest tests/test_prompt_sync.py -q`
- **Task lint:** `lint_task_file` passed on this file
- **Prompt sync:** `lint_system_prompt_sync` reports system-prompt.md in sync; it also flags a pre-existing unactionable skill reference in `prompts/fragments/DECISIONS.md:73` (outside this task's scope)

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `testing-verification` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** upstream docs may be unreachable, JS-guarded, or version-skewed against the installed 2.7.3; findings could be stale or misattributed.
- **Rollback plan:** this task produces a report only, not edits. If a recommended patch is wrong, discard it; no files change without a separate approved implementation plan.

---

## Execution Log & Reasoning

### Approach

Discovery task under autopilot. All live-web reads went through `blowsh` MCP tools under explicit deadlines, never `curl`/`wget`. Sources are official OpenChamber docs (`docs.openchamber.dev`) and the npm registry. Local claims cite `file:line`; installed-binary claims cite the installed package path.

### Findings

F1 — **Node floor understated in our docs (drift).** Upstream install page requires "Node.js 24.14 or newer" for the web app [https://docs.openchamber.dev/install/]; npm registry `@openchamber/web@2.8.0` declares `engines.node = ">=24.14.0"` [https://registry.npmjs.org/@openchamber/web/latest]. Our `docs/setup.md:7` says Node v18+ and `LLM.txt:16` says v20+ LTS. Local runtime is Node v26.13.1, so the install works today, but the documented floor is wrong. Recommended patch: set both to `24.14+`.

F2 — **Version table is one minor behind upstream (drift).** `docs/openchamber.md:13-14` pins OpenChamber 2.7.3 (installed) and OpenCode 2.3.2. Latest published `@openchamber/web` is 2.8.0 with `@opencode/client` 2.3.2 and `engines.opencode = ">=2.2.4"` [https://registry.npmjs.org/@openchamber/web/latest]. This is a pinned-version table, not a claim of latest; recommended patch is a "checked against latest 2.8.0 on 2026-11-22" note, not an automatic upgrade.

F3 — **`OPENCHAMBER_ALLOW_UNAUTHENTICATED_LAN` is real in the installed binary but absent from upstream public docs (caveat).** Upstream environment page full listing has no such variable, and a `must_contain: "ALLOW_UNAUTHENTICATED_LAN"` probe returned NO-MATCH [https://docs.openchamber.dev/environment/]. The installed 2.7.3 build does read it: `isUnsafeUnauthenticatedLanAllowed = (env) => env?.OPENCHAMBER_ALLOW_UNAUTHENTICATED_LAN === 'true'` and the bind-guard error says to set it `true` "to accept the risk" [`/home/mohammad/.nvm/versions/node/v26.13.1/lib/node_modules/@openchamber/web/build`]. Our `docs/openchamber.md:131,138`, `LLM.txt:704,716,725,744`, and `docs/setup.md:94,100` document it as a normal setting. Recommended patch: keep the rule (`false` with a UI password is correct and safe) but label it as an observed, version-specific escape hatch that upstream does not list publicly and that may change on upgrade.

F4 — **Our exposure guidance omits upstream's first-choice path (gap).** Upstream security page says default bind is `127.0.0.1`, to set a password before exposing, and to prefer device pairing over opening a port; Private Relay needs no exposed port at all [https://docs.openchamber.dev/security/, https://docs.openchamber.dev/private-relay/]. Our docs mention `connect-url` pairing at `docs/openchamber.md:101,121-122` and `LLM.txt:761` but never state the preference or the no-port rationale. Recommended patch: one line in `docs/openchamber.md` §6 noting pairing + Private Relay is preferred over the `0.0.0.0` bind used here.

F5 — **`OPENCHAMBER_ALLOW_NETWORK_ACCESS=1` is enterprise-mode only (no defect).** Upstream uses it only alongside `OPENCHAMBER_ENTERPRISE_MODE=1` or a policy file [https://docs.openchamber.dev/security/]. Our instance is not enterprise-managed, so it is not required. Worth a clarifying note only if readers encounter the variable.

F6 — **Port 3000 vs 3005 is a deliberate local override, not drift.** Upstream default is `localhost:3000` [https://docs.openchamber.dev/quickstart/]; `LLM.txt:690` records why HQ uses 3005 (3000 is the Next.js app, 8080 is code-server). No change.

F7 — **`openchamber_render` / openui-lang is platform-specific and not verifiable from upstream product docs.** Upstream docs cover the `@openchamber/sdk/ui` extension kit, not the chat render tool [https://docs.openchamber.dev/sdk/ui/]. The call-envelope contract just shipped is grounded in the local tool schema and the reproduced `parameters: Expected object` error, not upstream docs. No change; stated here explicitly so the absence is not mistaken for an unverified claim.

### Matches

Upstream and our docs agree on: managed OpenCode server by default with an allocated port that can change on restart [https://docs.openchamber.dev/opencode-server/]; `--ui-password` / `OPENCHAMBER_UI_PASSWORD` as the browser UI auth; `openchamber startup enable` snapshotting environment and needing a rerun after env changes [https://docs.openchamber.dev/environment/]; tunnel providers including Cloudflare managed-remote with `--token-file` and `--hostname` [https://docs.openchamber.dev/tunnels/].

### Scope note

This task produced a report only. No doc files were edited under it; the recommended patches require a separate approved implementation plan.

### Review chain (autopilot)

- QA Engineer: `VERDICT: QA_PASSED` — report meets all four acceptance checks, citation discipline holds, no product code changed, no blocking tests missing.
- Code Reviewer: technically approved, `Status: PO_REVIEW_PENDING` — awaiting final Manager sign-off. Low-severity recommendations only: add local `file:line` citations to the four Match bullets when a follow-up patch task edits docs; replace the absolute host path in F3 with package name plus version plus build-relative path. Neither point changes a finding or requires a fix.
- The 13-file working-tree diff belongs to the prior render-envelope task and was explicitly excluded from this review.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
