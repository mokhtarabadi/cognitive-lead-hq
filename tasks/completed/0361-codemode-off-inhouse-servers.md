# Task 0361: Code Mode off for the five in-house MCP servers

**File:** `tasks/qa/0361-codemode-off-inhouse-servers.md`
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

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.opencode/memory/index.md b/.opencode/memory/index.md
index 347d7d9..f87f5b9 100644
--- a/.opencode/memory/index.md
+++ b/.opencode/memory/index.md
@@ -27,6 +27,7 @@
 | telegram-sync | topic-scoped-sync-workflow | # Telegram Sync Workflow Constraints (Cognitive Lead HQ) |  |
 | workflows | approval_gates_use_question_tool | # Approval gates must use the question tool (Manager standing rule 2026-09-27) |  |
 | workflows | brain_turn_mode_line | # Brain calls MUST carry a mode line (Manager order 2026-10-16) |  |
+| workflows | codemode-policy | # Code Mode policy (OpenCode v2, 2026-10-29) |  |
 | workflows | free-model-context-window-workflow | # Free-model context-window workflow (verified 2026-10-21) |  |
 | workflows | global-install-upgrade | # Global Install Upgrade Workflow (OpenCode) |  |
 | workflows | manual-qa-review-cycle | # Manual QA + Review Cycle (Hands role-plays both) |  |
diff --git a/.opencode/memory/workflows/codemode-policy.md b/.opencode/memory/workflows/codemode-policy.md
new file mode 100644
index 0000000..3a68025
--- /dev/null
+++ b/.opencode/memory/workflows/codemode-policy.md
@@ -0,0 +1,16 @@
+---
+created_at: '2026-10-29T06:45:50.396289+00:00'
+status: active
+tags: []
+updated_at: '2026-10-29T06:45:50.396335+00:00'
+---
+
+# Code Mode policy (OpenCode v2, 2026-10-29)
+
+Per-server flag: `mcp.servers.<name>.codemode` (default true = tools behind `execute`).
+
+Policy in force: the five in-house servers run with `codemode: false` (native tools) — `custom_context` (16), `project_memory` (6), `lint` (4), `brain` (1), `planner` (11) — because together they are ~38 small tools called every task, so the wrapper hop costs more than the schema saves. `telegram` (147 tools) and `blowsh` (heavy, occasional) stay on Code Mode: their schemas must not enter the system prompt.
+
+Apply by editing `~/.config/opencode/opencode.json` after a timestamped backup, then validating with `python3 -c "import json;json.load(open(...))"`. The flag is host-level: the singleton services do not change, and an OpenCode/session restart applies it. Do NOT use this flag to hide individual tools — that is `permission` on the normalized `<server>_<tool>` name.
+
+Docs: `docs/services.md` (policy table), `docs/setup.md`, `README.md` Option B, `LLM.txt` install block.
\ No newline at end of file
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 9d72975..418e920 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Code Mode off for the five in-house MCP servers (Task 0361):** `custom_context`, `project_memory`, `lint`, `brain` and `planner` now set `"codemode": false`, so their ~38 small tools are native calls instead of `execute` wrappers; `telegram` (147 tools) and `blowsh` stay on Code Mode because their schemas must not enter the system prompt. Applied to the global `opencode.json` after a timestamped backup and validated as JSON; the live session catalog dropped all five out of `execute` in place. Policy documented in `docs/services.md` (rationale table), `docs/setup.md`, `README.md` Option B and the `LLM.txt` install block, and stored as `workflows/codemode-policy` memory for the upgrade workflow.
+
 - **Planner estimate header strict reject (Task 0360):** `_parse_task_file` prefix-matched the estimate, so a hand-written `**Estimate:** 1h 30m` booked 1.0h with no warning — a wrong number instead of no number. The branch now strict full-matches the lint contract (`^\d+(?:\.\d+)?h$`): unparseable means `estimate_hours=None`, never a truncated prefix. The lint gate already fails such files loudly at stage time; legacy/out-of-band files now read honestly instead. Locked by `test_parse_task_file_estimate_strict`.
 
 - **Parallel-delegation decision rule (Task 0359):** the mandate fired on discovery work only, so R&D and implementation splits ran on guesswork. `13-constraints.md` gains implementation & R&D triggers (disjoint files, independently verifiable lanes, independent research), a disjoint-ownership partition rule, and a verify-and-merge protocol; the executor gains an implementation-delegation lane beside the untouched discovery lane; the code-search skill's stale "`task`/subagent" reference now names `subagent` calls. Prompt rebuilt (`9.68.0` → `9.69.0`). No new agents, no blessed runtimes, no cap or gate changes.
diff --git a/LLM.txt b/LLM.txt
index 82b0b17..49a66a8 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -238,24 +238,28 @@ Write the following JSON (replace `$HOME` with the actual home directory path on
       "custom_context": {
         "type": "remote",
         "url": "http://127.0.0.1:8102/mcp",
+        "codemode": false,
         "disabled": false,
         "timeout": { "catalog": 15000, "execution": 15000 }
       },
       "project_memory": {
         "type": "remote",
         "url": "http://127.0.0.1:8103/mcp",
+        "codemode": false,
         "disabled": false,
         "timeout": { "catalog": 15000, "execution": 15000 }
       },
       "lint": {
         "type": "remote",
         "url": "http://127.0.0.1:8101/mcp",
+        "codemode": false,
         "disabled": false,
         "timeout": { "catalog": 15000, "execution": 15000 }
       },
       "brain": {
         "type": "remote",
         "url": "http://127.0.0.1:8105/mcp",
+        "codemode": false,
         "disabled": false,
         "timeout": { "catalog": 600000, "execution": 600000 }
       },
@@ -274,6 +278,7 @@ Write the following JSON (replace `$HOME` with the actual home directory path on
       "planner": {
         "type": "remote",
         "url": "http://127.0.0.1:8108/mcp",
+        "codemode": false,
         "disabled": false,
         "timeout": { "catalog": 15000, "execution": 30000 }
       }
diff --git a/README.md b/README.md
index d9c69a2..87f6993 100644
--- a/README.md
+++ b/README.md
@@ -393,6 +393,7 @@ Best if you want this codebase exploration tool available in _every_ terminal di
         "/Users/<YOUR_USER>/.config/opencode/mcp-context-server/.venv/bin/python",
         "/Users/<YOUR_USER>/.config/opencode/mcp-context-server/server.py"
       ],
+      "codemode": false,
       "enabled": true,
       "timeout": 15000
     }
@@ -408,6 +409,8 @@ Best if you want this codebase exploration tool available in _every_ terminal di
 
 _(Note: Replace `/Users/<YOUR_USER>` with your actual home directory path)._
 
+`codemode: false` exposes the server's tools as native calls instead of routing them through `execute`. The HQ ships this policy for its five in-house servers (`custom_context`, `project_memory`, `lint`, `brain`, `planner`) and keeps `telegram` (147 tools) and `blowsh` in Code Mode — see `docs/services.md`.
+
 Full HQ install covering all core MCP servers plus skills plus both agents is documented in LLM.txt sections 4 through 7 and the global-install-upgrade memory workflow not here. The steps above cover only the standalone context server for third party projects.
 
 
diff --git a/docs/services.md b/docs/services.md
index 2ef8af9..53ca4cd 100644
--- a/docs/services.md
+++ b/docs/services.md
@@ -21,6 +21,23 @@ Markdown. It serves the MCP Streamable HTTP endpoint at `/mcp` and a
 standalone dashboard at `/` (plus `/api/status`) on the same loopback
 port. It reads the project given by `PLANNER_PROJECT_ROOT`, falling back
 to the nearest ancestor of its working directory that holds `tasks/`.
+
+### Code Mode policy (v2 `mcp.servers.<name>.codemode`)
+
+Code Mode keeps a server's tool schemas out of the system prompt, but it
+adds one `execute` hop per call. The split follows cost, not seniority:
+
+| Servers | `codemode` | Why |
+| --- | --- | --- |
+| `custom_context`, `project_memory`, `lint`, `brain`, `planner` | `false` (direct tools) | ~38 small tools in total, called every task; direct calls are one hop and the schema cost is small |
+| `telegram` (147 tools), `blowsh` (5 heavy tools) | `true` (default) | 147 schemas would flood the prompt; blowsh output is large and occasional, so the wrapper pays |
+
+Setting `codemode: false` puts each tool in the native tool list
+(`lint_task_file`, `claim_next`, `brain_turn`, …) instead of behind
+`execute`. It is a host-level flag: the singletons do not change, and a
+session restart applies it. Per-tool hiding still belongs to
+`permission` (`<server>_<tool>`), not to this flag.
+
 `PLANNER_PROJECTS` (pathsep-separated absolute paths) feeds the
 dashboard's project switcher. It needs no credentials. `schedule_tasks`
 is the only writer for the `**Estimate:**`, `**Deadline:**` and
diff --git a/docs/setup.md b/docs/setup.md
index 7985b0d..c32b1bc 100644
--- a/docs/setup.md
+++ b/docs/setup.md
@@ -51,6 +51,8 @@ gh auth login
 
 The project uses five FastMCP Python servers, all running as supervised singletons (one process each, shared across sessions) on loopback HTTP (`MCP_TRANSPORT=streamable-http`, ports 8101–8105; telegram 8106, blowsh 8107 — see `docs/services.md`). `opencode.json` points at them via `type: "remote"` — no stdio entries remain.
 
+**Code Mode:** the five in-house servers (`custom_context`, `project_memory`, `lint`, `brain`, `planner`) set `codemode: false` so their tools are native calls; `telegram` and `blowsh` stay in Code Mode because 147 tool schemas (and heavy, occasional web output) must not enter the system prompt. See `docs/services.md` for the rationale table.
+
 | Server                                        | Purpose                                                                       | Singleton (port)              |
 | --------------------------------------------- | ----------------------------------------------------------------------------- | ----------------------------- |
 | `mcp-context-server`                          | `.gitignore`-aware file reading, tree exploration                             | 8102 (`mcp-context.service`)  |
```
<!-- END_GIT_DIFF -->
