# Task 0361: Code Mode off for the five in-house MCP servers

**File:** `tasks/in-progress/0361-codemode-off-inhouse-servers.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Goal

Run the five in-house MCP servers in direct-tool mode (`codemode: false`) and keep the token-heavy third-party ones behind Code Mode, then teach every install/upgrade doc the new policy.

## Manager's Notes

> سرورهای کاستومی که خودمون توسعه دادیم … Project Memory، Planner، Lint، Custom Context، Brain … به نظرم Code Mode نباشه بهتره. ولی بقیه روی Code Mode قرار بگیرن … باید با Graph پروژه رو نگاه کنی … داک‌های پروژه رو که آموزش نصب این‌ها هست آپدیت کنی، بعد Globally هم آپدیت کن و بگو Restart کنم.

## Decision

| Server | codemode | Why |
| --- | --- | --- |
| `custom_context` (16 tools) | **false** | Core exploration surface; called constantly, direct calls skip the execute indirection |
| `project_memory` (6) | **false** | Small toolset, read-heavy, agents reason over results immediately |
| `lint` (4) | **false** | Tiny schema, gate calls want exact typed results |
| `brain` (1) | **false** | One conversational tool; a wrapper adds nothing |
| `planner` (11) | **false** | Lane/status calls are the daily loop |
| `telegram` (147) | true | 147 schemas would flood the system prompt |
| `blowsh` (5) | true | Heavy output, used intermittently; Code Mode keeps the wrapper |

## Local TODOs

- [x] Backup global config
- [x] Apply `codemode: false` to the five in-house servers, verify JSON + resolved values
- [x] Update `LLM.txt` install block + rationale
- [x] Update `docs/services.md` policy section
- [x] Update `docs/setup.md`
- [x] Update `README.md` Option B + upgrade note
- [x] Store the policy in project memory (`workflows/codemode-policy`)
- [x] CHANGELOG, lint, stage

## Acceptance Criteria

- [x] Global `opencode.json` sets `codemode: false` on custom_context, project_memory, lint, brain, planner and leaves telegram + blowsh on Code Mode
- [x] Config remains valid JSON with all 7 servers resolving
- [x] Every install/upgrade doc states the policy and the token trade-off
- [x] Task + CHANGELOG record the change; restarts stay with the Manager

## Verification Evidence

- **Test command:** `python3 -c "json.load(open('~/.config/opencode/opencode.json'))"` plus resolved-values dump
- **Expected result:** 5 servers `codemode=False`, 2 `True`, 7 entries, valid JSON
- **Actual result:** exactly that; live session catalog dropped custom_context/lint/memory/brain/planner out of `execute` and kept blowsh + telegram in Code Mode
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** direct mode adds ~37 tool schemas to the system prompt (16+6+4+1+11 ≈ 38 tools); far below telegram's 147, and these are the ones called every turn.
- **Risk:** a session that relied on `execute` batching for these servers now calls them directly; behaviour is equivalent, only the surface changes.
- **Rollback:** restore `~/.config/opencode/opencode.json.bak-20261029-064345` and restart.

---

## Execution Log & Reasoning

**Seat Check.** Domains: MCP host config + install docs. No whole-word trigger hit on the UI/arch/perf sets — explicit miss; single seat Senior Programmer (config + docs). Skipped Architect (no code contract change), Designer (no surface), QA/Reviewer (config-only, verified by resolution dump). Brainstorm: not required — reversible config + doc edits.

**Planning gate.** Manager's order is the plan; the server split was named explicitly.

**Why this split is token-cheap in aggregate.** Code Mode saves tokens by keeping a server's schemas out of the system prompt, but only pays off when the tools are numerous or rarely used. The five in-house servers total ~38 tools and are the ones the Hands calls every task, so the wrapper costs an extra hop per call and saves little; telegram (147) and blowsh (heavy, occasional) stay wrapped.

**Verification.** `python3 -c json.load` on the edited global config prints 5×`codemode=False`, 2×`True`, 7 servers. The running session's catalog refresh showed the five leaving `execute` immediately, which is the real proof the host honours the per-server flag.

**Assumption A1.** `codemode: false` applies at session/tool-catalog load, so the Manager's OpenCode restart makes it deterministic for every session; the singleton servers themselves are unaffected (no MCP restart needed).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
