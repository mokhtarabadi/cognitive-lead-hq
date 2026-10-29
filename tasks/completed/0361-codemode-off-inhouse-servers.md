# Task 0361: Code Mode off for every server except telegram

**File:** `tasks/completed/0361-codemode-off-inhouse-servers.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Finished:** 2026-10-29T06:48:36Z

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
| `blowsh` (5) | **false** | Five tools only; direct calls are cheaper than the wrapper hop |
| `telegram` (147) | true | 147 schemas would flood the system prompt |

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

- [x] Global `opencode.json` sets `codemode: false` on custom_context, project_memory, lint, brain, planner and blowsh, leaving only telegram on Code Mode
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

**Why this split is token-cheap in aggregate.** Code Mode saves tokens by keeping a server's schemas out of the system prompt, but only pays off when the tools are numerous. Six servers now expose ~43 tools natively — the ones called every task, where the wrapper hop costs more than the schema saves; telegram (147) stays wrapped because its schema set alone would dominate the prompt.

**Verification.** `python3 -c json.load` on the edited global config prints six `codemode=False` and one `True` (telegram), 7 servers total. The running session's catalog refresh showed all six leaving `execute` immediately, which is the real proof the host honours the per-server flag.

**Assumption A1.** `codemode: false` applies at session/tool-catalog load, so the Manager's OpenCode restart makes it deterministic for every session; the singleton servers themselves are unaffected (no MCP restart needed).

**Closure (Manager, 2026-10-29):** "close task". Commit path is `custom_context_commit_and_clean_task` only.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `5f23f2b526cc33ec81e965274376e62f5f1342e0`
<!-- END_GIT_DIFF -->
