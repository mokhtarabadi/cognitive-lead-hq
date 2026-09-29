# Task 277: MCP singleton remote services

**File:** `tasks/archive/277-mcp-singleton-remote-services.md`
**Source:** manager
**Type:** feature
**Status:** superseded
**Superseded-By:** `279-mcp-singleton-rollout`
**Superseded-At:** `2026-09-29`

## Goal

One running instance of each MCP server, shared across all sessions and projects, with a single opencode-server and a single OpenChamber instance.

## Manager's Notes

Manager request (Persian, verbatim): "در کل میخوام طوری باشه یه instance از opencode بالا باشه و همه mcp ها هم فقط یک instance داشته باشن و و یک instance از openchamber هم باشه دیگه بین همه سشن ها و پروژها مشتکر باشه mcp سرورها". English: one opencode instance up, every MCP exactly one instance, one OpenChamber instance, MCP servers shared across all sessions and projects. Current state already satisfies 2 of 3 (single `opencode serve --service` PID 1100144, single OpenChamber service). Missing piece: each session spawns its own 7 stdio MCP processes (12 observed: 2 sets x 6). Approved direction: run each Python MCP once as a supervised remote (HTTP/SSE) service on 127.0.0.1 and switch global opencode.json entries from stdio to `type: remote`. Manager approved via plan-approval gate ("Approved, build it").

## Acceptance Criteria

- [ ] Exactly one OS process per MCP server (6 Python + blowsh) regardless of open session count
- [ ] Every session/project resolves the same 7 MCP servers via `opencode mcp list`
- [ ] Single opencode-server and single OpenChamber instance unchanged and healthy
- [ ] Services supervised (auto-restart) and bound to 127.0.0.1 only
- [ ] Rollback to stdio config restores current working state

## Verification Evidence

- **Test command:** rtk test ps aux | grep -E "mcp-|telegram_mcp" | grep -v grep | wc -l
- **Expected result:** one process per server (6 Python + blowsh pathway) with 2+ concurrent sessions open, plus `opencode mcp list` showing 7/7 connected in each session
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every multi-phase task):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** stdio-to-remote migration breaks currently working MCP setup; custom servers are stdio-only and need a transport shim; shared stateful servers face concurrent access; singleton is a single point of failure
- **Rollback plan:** global config backup (`opencode.json.bak-20260929-073130` plus fresh pre-migration backup); restore stdio entries, restart sessions; document exact restore commands in Execution Log

## Phase 1: Plan

### Local TODOs

- [ ] Brain planning round (Architect seat) under this task id, discovery-fed if Brain requests repo data
- [ ] Record Brain plan verdict + seat routing in Execution Log

## Phase 2: Transport shim

### Local TODOs

- [ ] One HTTP/SSE front per Python MCP server (or chosen shared gateway), localhost-only
- [ ] Per-server stdio initialize probe equivalent over the new transport

## Phase 3: Supervision + config cutover

### Local TODOs

- [ ] systemd user units (or equivalent) with auto-restart for each singleton
- [ ] Global opencode.json cutover to `type: remote`, fresh backup first
- [ ] Multi-session verification (process count + 7/7 in each session)

> **Superseded:** This task was bundled into META task `279-mcp-singleton-rollout` and archived on 2026-09-29. See `tasks/qa/279-mcp-singleton-rollout.md` (or its Kanban successor) for the unified execution. History preserved via `git log --follow -- tasks/archive/277-mcp-singleton-remote-services.md`.

## Execution Log & Reasoning

### 2026-09-29 — Phase 1 planning (Brain-approved plan recorded)
- Seat Check: Architect (trigger word `migration`); Designer/Programmer skipped with reasons. Single-seat valid.
- `Brainstorm: not required — single-domain reversible infra change` (Brain concurred).
- Discovery: 4 parallel subagents FAILED (free-tier provider restriction); ran inline instead (shell probes + signature greps). One discovery round only, per gate bound.
- Brain planning turns: T1 returned discovery XML; T2 asked for pasted report text; T3 (fed full text inline) returned FINAL plan. Verdict: selected path D1 native HTTP per server, no gateway, no stdio sidecar.
- Plan: 7 singletons on 127.0.0.1:8101-8107 (lint, context, memory, decisions, brain via FastMCP streamable HTTP; telegram via MCP_TRANSPORT=http; blowsh via one persistent container). 7 systemd user units Restart=always. Cutover low-blast-radius-first (lint→context→memory→decisions→brain→telegram→blowsh) with fresh dated backup kept alongside opencode.json.bak-20260929-073130. Fallback SSE if type:remote rejects streamable HTTP. Explicit non-goals: do NOT repair opencode-server.service, do NOT restart OpenChamber (health-check only).
- Assumptions: A1 free ports 8101-8107 (verify with ss at implementation); A2 opencode 2.0.19 type:remote accepts streamable-http path /mcp (probe before cutover); A3 blowsh image exposes HTTP (inspect before A7).
- Manager rollout approval already granted pre-plan ("Approved, build it"); Brain-plan approval still pending at handoff.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->

### 2026-09-29 — Phase 4 blowsh DONE (native HTTP in own repo)
- blowsh-mcp (`../blowsh-mcp`, task 10): `createServer()` factory + express stateless streamable-HTTP (`MCP_TRANSPORT=http`, default 127.0.0.1:8107); `npm run build` exit 0; Docker rebuild exit 0; container smoke health/initialize/tools-list 200.
- Learning: container must bind `MCP_HOST=0.0.0.0`, host publish locked `-p 127.0.0.1:8107:8107`; recorded in blowsh README + Dockerfile EXPOSE.
- Persistent `blowsh-singleton` up (restart unless-stopped, named volume); HQ `mcp.blowsh` cut to remote (backup `opencode.json.bak-20260929-081116`).
- Verified: 7/7 connected, exactly 1 proc per MCP (6 python + 1 container), live search_web through singleton OK.
- Goal state ACHIEVED: 1 opencode-server, 1 OpenChamber, 1 instance per MCP shared across sessions.
