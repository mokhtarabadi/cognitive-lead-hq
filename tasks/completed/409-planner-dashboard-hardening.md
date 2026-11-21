# Task 409: Planner MCP dashboard hardening across all projects

**File:** `tasks/qa/409-planner-dashboard-hardening.md`
**Source:** manager
**Type:** bug
**Status:** backlog
**Submitted:** 2026-11-21T08:13:59Z
**Mode:** AUTOMATIC (autopilot locked 2026-11-21)
**Seat routing:** UI/UX Designer + Software Architect + Senior Programmer (plan); QA Engineer + Code Reviewer (post-implementation)

## Goal

Review the live planner MCP dashboard with browser tooling across every registered project, then fix all confirmed correctness, reliability, accessibility, and documentation defects in one consolidated task so the board reports truthful state and saves to the selected project.

## Manager's Notes

Normalized from voice dictation: "Use browser tools to review our planner MCP dashboard, find all its bugs and gaps, fix all of them, make it better. Within one task in autopilot mode. Review all projects inside it. Probe it using the browser, and ask Brain seats to enhance it each time. All in one task."

Typos corrected-and-logged: "it bugs" -> "its bugs"; "enahnce" -> "enhance"; "auto pilot" -> "autopilot".

Plan approved via question tool with the answer "Approved" on 2026-11-21. The Brain blueprint is the executing plan. Brainstorm: required - the work spans API data correctness, frontend accessibility, and docs governance, and no single seat can resolve all three.

## Fed Context

[fed-context]
- Live probe: `http://127.0.0.1:8108/` returns HTTP 200; systemd `mcp-planner` active. Projects: cognitive-lead-hq, apex, blowsh-mcp, hesab-ketab, dumble. All render; project switch is asynchronous so an immediate snapshot after select can be blank.
- Browser-confirmed: hesab-ketab week plan shows `-8h left` with a full bar; board shows M01 and M03 only while `tasks/milestones/M02-planner-cockpit-and-design-system.md` exists; daily pacing is fabricated across projects.
- `GET /api/status?project_root=<abs>` returns live lane data. `today.done` derives from `target - open_work`, not from finished tasks (`mcp-planner-server/server.py:2685-2686`, `:2722`).
- `POST`/`DELETE /api/plan` resolve `_resolve_dashboard_root(None)` (`server.py:2908`, `:2934`); client sends no `project_root` (`static/index.html:935-938`) while GET does (`:663-667`).
- `/api/status` converts all exceptions to HTTP 200 with an error body (`server.py:2730-2731`, `:2769-2782`); client overwrites the danger badge with a success badge (`static/index.html:307-333`).
- Milestone grouping is case-sensitive in status (`server.py:2702-2704`) but casefolded in `plan_status`/`milestone_status` (`:1179`, `:1388`).
- `_project_tool` infers `project_root` from `args[0]` (`server.py:137-141`), breaking positional `plan_propose`/`sprint_lock`.
- Local `date.today()` anchors (`server.py:2178`, `:2505`, `:2356`, `:1467`, `:1078`, `:718`) conflict with UTC stamps (`:946-964`, `:1205`); contract is UTC (`mcp-planner-server/DECISIONS.md:194`).
- Frontend gaps: login refresh (`:1024-1035`), stale board on project switch (`:955-961`), UTC tooltip (`:461-462`), Mine only and logout state (`:128`, `:277`, `:369`, `:998-1002`), full re-render (`:645-648`), dialog a11y (`:146-184`, `:698`, `:421`), XSS escape (`:386`).
- Docs drift: `tasks/.plan/index.json` claimed but absent (`docs/planner-mcp-plan.md:54`); SSE and light theme claimed but absent (`:59`, `index.html:1077-1081`); stale ADR references (`DECISIONS.md:195`); README calls `/mcp` admin-guarded against ADR-006 (`README.md:15-17`).
- Living folder docs `mcp-planner-server/README.md` and `mcp-planner-server/DECISIONS.md` were read before analysis and must be updated for contract or decision changes with a dated ADR.
[/fec-context]

## Execution Steps

- [x] Step 1: move task to in-progress and establish live baseline (filesystem `mv` fallback: source file was untracked, so `git mv` refused; dashboard and status API both HTTP 200)
- [x] Step 2: critical backend contract fixes B1, B2, B4 plus client `project_root` (py_compile OK; grep confirms validation, 500 mapping, signature binding, and client body)
- [x] Step 3: backend data correctness B3, B5, B8, B6, B7 (py_compile OK; `_normalize_milestone` M1->M01, m02->M02; `_milestone_definitions` resolves M02; all 8 `date.today()` anchors now UTC)
- [ ] Step 4: low-risk security hardening B9, B10
- [x] Step 5: frontend UI and a11y fixes F1-F8 (`node --check` on the extracted inline script exited 0; browser pass deferred to Step 7 because the live service serves a separate installed copy at `~/.config/opencode/mcp-planner-server/`, deployed via the documented `LLM.txt` procedure)
- [x] Step 6: docs and governance D1-D4 (CHANGELOG Unreleased/Fixed entry, README contract refresh, DECISIONS ADR-015 dated 2026-11-21, plan document marked historical)
- [x] Step 7: regression tests, RTK-first gates, browser re-probe (9 new tests, planner slice 170 passed, live deploy verified, five-project browser probe clean)

## Local TODOs

- [x] Slice A: backend API and data fixes B1-B8 plus B9-B10 security hardening
- [x] Slice B: frontend UI and a11y fixes F1-F8
- [x] Slice C: docs and governance D1-D4 with dated ADRs
- [x] Slice D: regression tests, RTK-first verification gates, browser re-probe
- [ ] QA Engineer turn and Code Reviewer turn chained via `brain_turn`
- [ ] Stage via `custom_context_stage_and_inject_diff`, move to `tasks/qa/`, hand off

## Acceptance Criteria

- [x] `POST`/`DELETE /api/plan` require and honor `project_root`; a save in a non-default project lands in that project
- [x] `/api/status` internal errors return HTTP 500 and the dashboard keeps the danger badge
- [x] `today.done` reflects real finished-task count or an explicit unknown flag, never `target - open_work`
- [x] Milestone grouping is casefolded and M02 appears on the board with unified naming
- [x] All day/week anchoring is UTC consistent with the documented contract
- [x] Month view prorates capacity for partial weeks; negative capacity renders as overrun
- [x] `_project_tool` requires explicit `project_root` and never registers a bogus project
- [x] Login refreshes Plan, CFD, and Control; project switch clears stale board state
- [x] Tooltip uses the local calendar day; Mine only works and clears on logout
- [x] Dialogs have roles, focus trap, Escape, labeled controls, and aria-live status
- [x] `estimate_hours` is escaped in lane rows
- [x] Loopback guard performs a real check; forwarded-proto and token handling hardened
- [x] Docs match shipped behavior; README and DECISIONS updated with a dated ADR
- [x] New regression tests pass under `rtk test`, and browser re-probe across all 5 projects passes

## Verification Evidence

All commands run from `/home/mohammad/cognitive-lead-hq` on 2026-11-21.

- **Command:** `python3 -m py_compile mcp-planner-server/server.py tests/test_planner_409_regression.py`
- **Expected:** no output, exit 0
- **Actual:** no output; `py_compile=0`
- **Exit code:** 0

- **Command:** `awk '/<script>/{f=1;next}/<\/script>/{if(f){f=0}}f' mcp-planner-server/static/index.html > /tmp/planner409-dashboard.js && node --check /tmp/planner409-dashboard.js`
- **Expected:** JS syntax valid
- **Actual:** `js_check=0` (Node v26.13.1)
- **Exit code:** 0

- **Command:** `~/.config/opencode/mcp-brain-bridge/.venv/bin/python -m pytest tests/test_planner_409_regression.py -q`
- **Expected:** 9 new regression tests pass
- **Actual:** `9 passed, 2 warnings in 1.80s`
- **Exit code:** 0

- **Command (RTK-first planner gate):** `rtk test /home/mohammad/.config/opencode/mcp-brain-bridge/.venv/bin/python -m pytest -q tests/test_planner_server.py tests/test_planner_schedule.py tests/test_planning_contracts.py tests/test_planner_409_regression.py`
- **Expected:** planner slice green with fresh evidence
- **Actual:** `170 passed, 2 warnings in 63.12s`
- **Exit code:** 0

- **Command (RTK-first full suite, attempted first):** `rtk test /home/mohammad/.config/opencode/mcp-brain-bridge/.venv/bin/python -m pytest -q`
- **Expected:** full HQ suite green
- **Actual:** `430 failed, 490 passed, 24 warnings, 10 errors` caused by a pre-existing `sys.modules["server"]` collision from `mcp-lint-server/server.py` (`AttributeError: module 'server' has no attribute '_bridge_root'`). Diagnostic `rtk` recall confirmed 430 failures include brain-bridge and stage-prompt tests unrelated to this task. Baseline rerun without the new test file, `python -m pytest -q --ignore=tests/test_planner_409_regression.py`, produced the same `430 failed, 481 passed, 10 errors` with exit 1, proving the failure predates and is independent of this change. Five contract assertions in `tests/test_planner_server.py` were updated to ADR-015 (canonical `M01`, real `today.done`, required `project_root`, `ok` without token body); no test was deleted or weakened.
- **Exit code:** 1 (pre-existing environmental blocker; scoped planner gate above is green)

- **Command:** `cp mcp-planner-server/{server.py,pyproject.toml,uv.lock,README.md,DECISIONS.md} ~/.config/opencode/mcp-planner-server/ && cp -r mcp-planner-server/static/. ~/.config/opencode/mcp-planner-server/static/ && chmod +x ... && systemctl --user restart mcp-planner`
- **Expected:** installed copy matches repo, service active, dashboard 200
- **Actual:** `service=active`, `http=200`, `server synced=OK`, `dashboard synced=OK`. This is the documented `LLM.txt` deploy path; the live service does not read the repo copy directly.
- **Exit code:** 0

- **Command:** `curl -s 'http://127.0.0.1:8108/api/status?project_root=/home/mohammad/cognitive-lead-hq' | python3 -c ...`
- **Expected:** M02 visible, real pacing
- **Actual:** `milestones: ['M01', 'M02', 'M03']`; `today: {'done': 1, 'target': 3, 'open': 1, 'quota_reached': False}`
- **Exit code:** 0

- **Command:** `curl -s -o /dev/null -w '%{http_code}' -X POST -d '{"approved":false}' http://127.0.0.1:8108/api/plan`
- **Expected:** 400 when project_root omitted
- **Actual:** `post_no_root=400`
- **Exit code:** 0

- **Browser re-probe (openchamber_web):** dashboard at `127.0.0.1:8108` reopened after deploy. All five projects switched with no logged JS errors and no stale-board state. Live DOM shows M01, M03 and a seeded `M02 0/1 [declared]` node with `aria-label="Toggle milestone M0n"` buttons. `dumble` displays `28h of 20h · 0h left · 8h over` with a red capacity bar. `hesab-ketab` shows real `0/3` pacing. 390px mobile viewport stays single-column with no horizontal trap. Clicking Save on the non-default `dumble` project created `/home/mohammad/dumble/tasks/.plan/week-2026-W47.json` and no file under the HQ project, proving project-scoped writes. Screenshots: `.openchamber/screenshots/planner409-*.png`.

### QA hotfix round (QA_REJECTED findings F1-F6)

- **QA verdict:** `QA_REJECTED` on six reproducing findings: fail-open loopback peer check for hostnames, incomplete project-switch refresh, stale panels in `clearBoard`, lane badge using filtered count, zero-capacity bar forced to 100%, and missing regression cover for positional tool binding, month proration, loopback denial and DELETE validation. All six were verified against the diff and fixed in this task; none were disputed.
- **Command:** `python3 -m py_compile mcp-planner-server/server.py tests/test_planner_409_regression.py` — exit 0, no output.
- **Command:** `awk '/<script>/{f=1;next}/<\/script>/{if(f){f=0}}f' mcp-planner-server/static/index.html > /tmp/planner409-hotfix.js && node --check /tmp/planner409-hotfix.js` — exit 0, `js_check=0`.
- **Command:** `~/.config/opencode/mcp-brain-bridge/.venv/bin/python -m pytest tests/test_planner_409_regression.py -q` — `13 passed, 2 warnings in 1.49s`, exit 0.
- **Command (RTK-first):** `rtk test /home/mohammad/.config/opencode/mcp-brain-bridge/.venv/bin/python -m pytest -q tests/test_planner_server.py tests/test_planner_schedule.py tests/test_planning_contracts.py tests/test_planner_409_regression.py` — `174 passed, 2 warnings in 62.78s`, exit 0.
- **Deploy:** repo source copied to `~/.config/opencode/mcp-planner-server/` and `systemctl --user restart mcp-planner`; `service=active`, `http=200`, `post_no_root=400`, milestones `['M01', 'M02', 'M03']`, `today` real count.
- **Browser re-probe after hotfix:** fresh tab, switched dumble -> apex; apex showed its own 12h/20h capacity, own deadlines and own charts with no stale dumble panels and no logged JS errors. Screenshot `.openchamber/screenshots/planner409-hotfix-apex-2026-11-21T08-25-30-312.png`.

- **Stack gate skip record:** repo root `/home/mohammad/cognitive-lead-hq`; marker scan list `pyproject.toml`, `requirements.txt`, `package.json`, `vite.config.*`, `next.config.*`, `nest-cli.json`, `prisma/schema.prisma`, `build.gradle.kts`; matched skills list `[]` for an exact stack (stdlib Python HTTP plus vanilla JS dashboard); reason phrase "no exact stack skill matches stdlib Python plus vanilla JS, so `python-fastapi` supplies Python discipline only and the HQ pytest suite plus `lint_task_file` is the gate".
- **Debug instrumentation:** runtime visibility was obtained from browser probes and live API responses, so no temporary `[DEBUG-TRACE]` logs were injected.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0 (py_compile, JS syntax, 9 new tests, RTK-first planner slice 170 passed; full-suite failure proven pre-existing and unrelated in Verification Evidence)
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `testing-verification` applied with fresh evidence
- [x] Browser re-probe evidence recorded
- [ ] QA and Code Reviewer verdicts recorded with no unresolved finding

## Risk & Rollback

- **Risk:** editing the live planner daemon source requires a service restart; a malformed edit could take the dashboard down.
- **Rollback plan:** restore the touched files from the pre-edit `git diff`, restart `mcp-planner`, and re-run the API and browser probe. No `git checkout` is permitted; use native file edits from the captured original content.
- **Risk:** B1 changes the write path for saved plans; verify against a throwaway week plan before touching a real one.
- **Deferred:** OAuth auth redesign, SSE push and light theme, business-day calendar with holidays.

---

## Execution Log & Reasoning

**Gatekeeper:** no rule violation. The work is permitted tooling in a documentation-only HQ repo. ZAC holds: no `git add`, commit, checkout, or push; staging only via `custom_context_stage_and_inject_diff`.

**Skills loaded:** `prompt-refactor` (voice-dictation normalization), `project-memory` (context bootstrapping), `kanban-lifecycle` (task creation), `debug-instrumentation` (silent-failure discipline), `python-fastapi` (Python discipline only, explicit stack skip above), `testing-verification` (verification gate).

**Seat check:** domains UI/UX plus backend contracts plus security; requested UI/UX Designer, Software Architect, Senior Programmer; skipped Project Planner and Sprint Strategist because no priority or sprint-scope decision is being made. Triggers `dashboard`, `a11y`, `API design`, `schema`, `silent-fail` fired.

**Plan verdict:** approved by Manager with "Approved" on 2026-11-21 after full plan presentation. Plan source: Brain REPORT under task 409, selected seats as above. Three deferred items recorded in Risk.

**Assumption A1:** the Brain-proposed commands `black`, `ruff`, `mypy`, and a `tests/test_planner_status.py` file may not exist in this repo; available equivalents will be substituted at gate time and the substitution recorded here. Reason: the plan was authored without a repo bundle.

**Assumption A2:** the dashboard is a localhost tool, so B9 loopback enforcement must fail closed only for non-loopback peers and must not break the existing loopbound binding. Reason: ADR-006 makes bind plus edge the intended security boundary.

**Assumption A3:** B10 keeps the HttpOnly cookie as the transport and removes the raw token from the login JSON body. Reason: the documented design is cookie-based.

**Assumption A4:** the live service runs a separate installed copy under `~/.config/opencode/mcp-planner-server/`, so repo edits alone would not change the dashboard. Reason: `LLM.txt` §7 documents the `cp` deploy path; verified by `cmp` showing the copies differed before deployment and match after.

**Assumption A5:** the full-suite `sys.modules["server"]` collision is pre-existing. Reason: the same 430 failures reproduced with the new test file excluded; the planner-only RTK gate is green and five existing assertions were legitimately updated to the ADR-015 contract rather than removed.

**Finding Q1 (non-blocking):** the full HQ suite needs a separate test-isolation fix so every module loads MCP servers under unique names. Out of scope here; recorded for the Manager.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 8b64e6e..a0d8b31 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -13,6 +13,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Fixed
 
+- **Planner MCP dashboard hardened across all five registered projects (task 409):** browser probing plus three seat-routed source analyses found 22 defects and gaps, all fixed in one task. `POST`/`DELETE /api/plan` now require an absolute `project_root` and the dashboard sends the selected project, so a save can no longer silently write into the daemon's default project. `/api/status` returns HTTP 500 for internal failures and the board keeps its danger badge instead of claiming "Server reachable" over stale data. The fabricated `today.done = target - open` was replaced with a real finished-today count plus an explicit `quota_reached` flag. All day/week anchors now use UTC, matching the documented contract. Milestone grouping is canonical across the API and both MCP tools, and `tasks/milestones/*.md` declarations now seed the board so M02 is visible alongside M01 and M03. Month views prorate partial weeks. `_project_tool` binds arguments through the real signature, so positional `plan_propose`/`sprint_lock` calls no longer register bogus projects. The `/mcp` wrapper now performs a real loopback check, `X-Forwarded-Proto` is honoured only from configured trusted proxies, and the session token is no longer returned in the login body. The frontend gained a single login refresh path, stale-board clearing on project change and auth failure, local-calendar tooltips, a working Mine only filter, lane-only search updates, overrun-aware capacity rendering, dialog roles with focus traps and Escape, and escaped estimate values. Regenerated `mcp-planner-server/README.md` and `DECISIONS.md` (dated ADR) record the new contracts; the live installed copy is deployed through the documented `LLM.txt` path. See task 409.
+
 - **OpenChamber service repaired after reboot `MODULE_NOT_FOUND` (task 408):** the `@openchamber/web` 2.7.3 upgrade on 2026-11-20 moved the npm CLI entry point from `bin/cli.js` to `build/bin/cli.js`, but the hand-written `~/.config/systemd/user/openchamber.service` still pinned the old path, so the unit crash-looped every 5 seconds after the reboot (restart counter 47+). Corrected `ExecStart` to the `build/bin/cli.js` path, kept a `.bak-20261121` copy of the unit, and verified the service stays active with port 3005 listening and HTTP 200. Added the post-upgrade unit-verification rule to `LLM.txt` §7.9 and `docs/openchamber.md` §4/§8, and refreshed the version table to the live OpenCode 2.3.2 / OpenChamber 2.7.3. ZAC holds; no commit.
 
 ## [9.90.0] - 2026-11-20
diff --git a/docs/planner-mcp-plan.md b/docs/planner-mcp-plan.md
index 8a82e2b..f292712 100644
--- a/docs/planner-mcp-plan.md
+++ b/docs/planner-mcp-plan.md
@@ -1,5 +1,16 @@
 # Planner MCP v1 — Design & Implementation Plan
 
+> **Historical document — superseded by `mcp-planner-server/README.md` and
+> `mcp-planner-server/DECISIONS.md`.** This was the Phase A design plan, not the
+> shipped contract. It still names task ID 331, a `tasks/.plan/index.json` read
+> model that was never implemented, SSE refresh and a light theme that were
+> never built, and milestone file names `M24-*`. The live server derives its
+> read model per request from Markdown, polls at 30/60 s, ships a dark-only
+> dashboard, uses canonical `Mnn` milestone ids, and requires an explicit
+> `project_root` on plan writes. See ADR-015 in `mcp-planner-server/DECISIONS.md`
+> dated 2026-11-21. Where this document and those two living files disagree,
+> the living files win.
+
 ## 1. Problem & scope
 
 The Manager reports entering autopilot unintentionally, running many tasks back-to-back, and then finding QA/testing of accumulated changes hard — work becomes complex and scattered. The brainstorming session (7 seats: Architect, UI/UX Designer, Senior Programmer, Project Planner, Sprint Strategist, QA Engineer, Code Reviewer) ranked **O1** as the winning option:
@@ -34,7 +45,7 @@ This plan records that decision and the v1 execution path so planning can contin
 
 ## 4. Out of scope for v1 (explicit)
 
-- Asana or Plane synchronization, Telegram task mutation, multi-user permissions.
+- Asana or Plane synchronization, Telegram task mutation. Multi-user permissions were originally out of scope but were later added under ADR-005/006/007 in `mcp-planner-server/DECISIONS.md`.
 - Automatic task creation without Manager approval.
 - General-purpose Gantt, webhooks/inbound events, git commit/push by agents.
 
@@ -43,20 +54,20 @@ This plan records that decision and the v1 execution path so planning can contin
 Existing task header stays. New optional header fields:
 
 ```
-**Estimate:** <hours>          # work estimate, used for capacity sums
-**Milestone:** <id>            # links to tasks/milestones/<id>.md
-**Deadline:** YYYY-MM-DD       # sortable
-**Depends on:** <id>, <id>     # prerequisite task IDs
+**Estimate:** 3h               # work estimate, used for capacity sums
+**Milestone:** M02             # links to tasks/milestones/M02-*.md
+**Deadline:** 2026-12-01       # sortable
+**Depends on:** 338, 340       # prerequisite task IDs, numeric
 ```
 
-Milestones get their own file: `tasks/milestones/M24-<name>.md` (context, target date, owning task IDs).
+Milestones get their own file: `tasks/milestones/Mnn-<name>.md` (context, target date, owning task IDs). Canonical ids are `M01`, `M02`, …; `M1` and `m01` normalize to `M01`, and declared files seed the board even with zero tagged tasks.
 
-A planner **read model** lives in `tasks/.plan/index.json` (gitignored, regenerated from Markdown on every planner invocation — never hand-edited). It contains task ID, source path, status, lane, estimate, milestone, deadline, depends_on, QA status, and derived fields (`blocked`, `due_soon`, `qa_pending`).
+A planner read model was **planned** at `tasks/.plan/index.json`, but no writer was ever shipped. The live server derives the same fields per request from the Markdown files instead, so there is no persisted index to hand-edit. (Superseded by `mcp-planner-server/README.md`.)
 
 ## 6. Architecture
 
 - **`mcp-planner-server/`** (new singleton, port 8108, same pattern as other MCP servers): tools only — `plan_status`, `plan_propose` (decompose a goal into tasks + estimates, **writes nothing**), `plan_materialize` (writes task files after Manager approval), `claim_next` (guarded claim: checks dependencies, WIP, QA budget), `qa_budget` (count of QA-pending tasks), `milestone_status`.
-- **Local dashboard**: served by the MCP on 8108, static HTML+JS, Kanban lanes, QA queue bar, capacity meter (default 20 h/week), milestone timeline, blocker list (`blocked_by`). SSE refresh. Accessible states (loading, empty, disconnected, stale-data), keyboard nav, light/dark.
+- **Local dashboard**: served by the MCP on 8108, static HTML+JS, Kanban lanes, QA queue bar, capacity meter (default 20 h/week), milestone timeline, blocker list (`blocked_by`). Shipped with 30 s status polling and 60 s plan/chart polling, dark-only theme, dialog focus traps, keyboard navigation, and aria-live status. SSE and a light theme were planned but not built.
 - **Rollback**: disable planner, return to `tasks/` Markdown workflow. No destructive migration — planner reads only.
 
 ## 7. Risks & rollback
diff --git a/mcp-planner-server/DECISIONS.md b/mcp-planner-server/DECISIONS.md
index ff70797..788c6b9 100644
--- a/mcp-planner-server/DECISIONS.md
+++ b/mcp-planner-server/DECISIONS.md
@@ -201,3 +201,10 @@ not initialized`.
 - **Decision:** the arithmetic stays, the claim changes. Every user-visible label now reads **lead time** and says it counts nights and weekends. The cockpit keeps two numbers: `remaining_hours = capacity − open_estimate` and `committed_hours = open_estimate + done_estimate`. Payload keys are deliberately unchanged (`elapsed_seconds`, `measured_hours`, `cycle_hours`) so the dashboard and consumers are not broken for a rename that buys no accuracy. Effort is **not** measured and this ADR says so plainly: no pause event exists, so any accumulator would reproduce the overnight inflation under a new field name.
 - **Consequences:** the board can no longer be read as claiming effort; lead time stays useful for staleness and flow. Measuring real effort would require explicit pause/resume stamps at every lane transition plus a lint rule, and is deliberately not funded.
 - **Rollback:** revert the label strings and the bucket split; the previous (misleading) wording returns and `remaining_hours` shrinks as work completes.
+
+## [2026-11-21] ADR-015: Truthful board data, project-scoped writes, and canonical milestones
+
+- **Context:** browser probing across all five registered projects plus three seat-routed source analyses found three classes of silent wrong data. `POST /api/plan` resolved the daemon default root, so a save made while viewing another project either failed validation or wrote into the wrong `week-*.json`. `/api/status` converted every internal exception into HTTP 200 and the client then painted "Server reachable" over a stale board. `today.done` was derived as `target - open`, so every empty project claimed three finished tasks. Milestone groups were case-sensitive in status but casefolded in the tools, and `tasks/milestones/*.md` declarations were never read, so M02 was invisible. Day/week anchoring used host-local dates while stamps were UTC. The `/mcp` "loopback guard" performed no check, `X-Forwarded-Proto` was trusted from any peer, and the login token was returned in the JSON body.
+- **Decision:** plan writes require an absolute `project_root` in the body (or query for DELETE) and validate it before resolution. Internal status failures return HTTP 500 with a stable `internal error` sentinel and the client keeps the danger badge. `today` carries a real finished-today count plus `quota_reached`; the no-open-work rule stays the quota verdict, matching `sprint_check_daily_quota`. All day/week anchoring uses `datetime.now(timezone.utc)`. Milestone keys are canonical `Mnn` ids shared by the API and both tools, and declared milestone files seed the tree. `/mcp` rejects non-loopback peers with 403. Forwarded proto headers are honoured only from `PLANNER_TRUSTED_PROXIES` (default loopback). The session token travels only in the HttpOnly cookie; login signals success with `ok`. The dashboard uses one login refresh path, clears stale boards, uses local calendar dates for tooltips, and renders overrun capacity explicitly.
+- **Consequences:** saves are project-scoped and auditable, failures are visible, pacing and milestones reflect disk truth, and the transport boundary fails closed without an auth redesign. The quarterly plan document and SSE/light-theme claims were corrected to shipped behaviour. Scripted positional tool calls that relied on `args[0]` as a project root must pass `project_root` explicitly.
+- **Rollback:** revert `server.py` and `static/index.html` to the pre-2026-11-21 versions; the silent wrong-project write, fabricated pacing, and stale-board badge return. Keep the documented `LLM.txt` deploy step in mind: the installed copy under `~/.config/opencode/mcp-planner-server/` must be synced too.
diff --git a/mcp-planner-server/README.md b/mcp-planner-server/README.md
index 16856ef..f6c9494 100644
--- a/mcp-planner-server/README.md
+++ b/mcp-planner-server/README.md
@@ -14,11 +14,13 @@ dashboard on loopback port 8108.
   `milestone_status`, `plan_status`, `sprint_daily_agenda`,
   `sprint_check_daily_quota`, `sprint_lock`) plus an embedded HTTP route
   serving the static dashboard on `GET /` and `GET /api/status`, the auth
-  routes, and the admin-guarded MCP endpoint.
+  routes, and the auth-free MCP endpoint guarded by a real loopback peer check
+  plus the tunnel's `/mcp` 404.
 - `manage_users.py` — stdlib-only user CLI (`add`, `update`, `remove`,
   `list`, `enable`, `disable`) writing `~/.config/opencode/planner-users.json`.
-- `static/index.html` — standalone dark-mode dashboard (no build step),
-  including the login modal and the user badge.
+- `static/index.html` — standalone dark-only dashboard (no build step, no SSE;
+  30 s status polling and 60 s plan/chart polling), including the login modal
+  and the user badge.
 - `pyproject.toml` / `uv.lock` — runtime deps and lockfile.
 - `README.md` / `DECISIONS.md` — Living Folder Docs for this slice.
 
@@ -26,21 +28,29 @@ dashboard on loopback port 8108.
 
 | Route                                                     | Purpose                                                                                                                                                                                                                                                                |
 | --------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
-| `GET /`                                                   | Standalone dark-mode dashboard (no build step).                                                                                                                                                                                                                        |
+| `GET /`                                                   | Standalone dark-only dashboard (no build step).                                                                                                                                                                                                                         |
 | `GET /static/*`                                           | Dashboard assets (same `static/` directory).                                                                                                                                                                                                                           |
 | `GET /api/status[?project_root=<abs path>]`               | JSON status contract the dashboard renders.                                                                                                                                                                                                                            |
 | `GET /api/task?id=<id>` or `?path=tasks/<lane>/<file>.md` | One task file as `{id, path, lane, title, markdown}` for the dashboard modal. `id` wins when both are sent. 400 no param, 401 no session, 403 outside grants or unsafe path, 404 unknown, 500 unexpected.                                                              |
 | `GET /api/hours[?project_root=<abs path>]`                | Lead time from task stamps: per-day rows for the last 14 days plus per-week rows for the last 8 ISO weeks (`{date/week, measured_hours, done}`). The key is historical; the value is `finished − started` wall clock, which counts nights and weekends and is **not** effort. Tasks without `Finished` + `elapsed_seconds` never count, and hours are attributed to the finish day. Same 401/403 contract as `/api/status`. |
-| `POST /api/login`                                         | `{"username","password"}` → `{token, username, role, allowed_projects}` + `HttpOnly` cookie.                                                                                                                                                                           |
+| `POST /api/login`                                         | `{"username","password"}` → `{ok, username, role, allowed_projects}` + `HttpOnly` cookie. The session token is never returned in the body.                                                                                                                          |
 | `POST /api/logout`                                        | Invalidates the session and clears the cookie.                                                                                                                                                                                                                         |
 | `GET /api/me`                                             | Current user, or 401 when signed out (200 + `note: "auth disabled"` in open mode).                                                                                                                                                                                     |
-| `POST /mcp`                                               | MCP Streamable HTTP endpoint (tools). Auth-free on loopback; the tunnel 404s it.                                                                                                                                                                                       |
+| `GET /api/plan[?project_root=<abs path>&window=day\|week\|month]` | Saved week plan plus derived capacity and deadline alerts. `window=month` prorates capacity for partial ISO weeks.                                                                                                                                            |
+| `POST /api/plan`                                          | `{project_root, deadline_edits, capacity_by_day, approved}`. `project_root` is required and absolute: 400 when missing or relative, 404 when the directory does not exist. Writes only to that root.                                                                |
+| `DELETE /api/plan[?project_root=<abs path>&week=YYYY-Www]` | Clears the saved plan for the given project; `project_root` is required and validated like POST.                                                                                                                                                                     |
+| `POST /mcp`                                               | MCP Streamable HTTP endpoint (tools). Auth-free on loopback; the wrapper rejects non-loopback peers with 403 and the tunnel 404s it.                                                                                                                                |
 
 `/api/status` returns per-lane **task lists** (`lanes`), the milestone tree
-(`milestone_tree`), upcoming deadlines (`deadlines`), the pacing figures
-(`today` = `done`/`target`/`open`, mirroring `sprint_check_daily_quota`), the
-selectable project roots (`projects`), and the root actually reported on
-(`project_root`). Lane values are lists, never counts — the dashboard calls
+(`milestone_tree`), deadlines (`deadlines`), the pacing figures
+(`today` = real finished-today `done`, `target`, open working set, and an
+explicit `quota_reached` boolean), the selectable project roots (`projects`),
+and the root actually reported on (`project_root`). Milestone keys are
+canonical `Mnn` ids: `M1`, `m01` and `M001` merge into `M01`, and every
+`tasks/milestones/*.md` declaration seeds the tree at zero tasks so a closed
+milestone such as M02 stays visible. Internal status failures return HTTP 500
+with `{error: "internal error", detail}`, never HTTP 200. Lane values are
+lists, never counts — the dashboard calls
 `.map()` on them. Every rendered list (lanes, milestone groups, plan buckets,
 alert rails) is ordered lowest task number first by the leading filename
 integer, so mixed widths (`283-*.md` vs `0356-*.md`) still sort numerically;
@@ -51,6 +61,13 @@ Project resolution order: the `project_root` query parameter, then
 holding `tasks/`, then the working directory. `PLANNER_PROJECTS`
 (pathsep-separated absolute paths) adds entries to the dashboard switcher;
 `PLANNER_DAILY_TARGET` overrides the daily batch size (default 3).
+`PLANNER_TRUSTED_PROXIES` is a comma-separated IP allowlist whose members may
+set `X-Forwarded-Proto` for cookie `Secure` and HSTS decisions; it defaults to
+loopback so the local tunnel keeps working. All day/week bucketing, plan week
+keys, quota checks, and overdue tests use UTC, matching the timestamp contract
+below. The installed service is a copy of this directory, deployed with the
+`cp` commands in `LLM.txt` §7 and then restarted; editing this repo alone does
+not change the live dashboard.
 
 ## Authentication and RBAC (optional, off by default)
 
diff --git a/mcp-planner-server/server.py b/mcp-planner-server/server.py
index 9bac3e8..c3ea867 100644
--- a/mcp-planner-server/server.py
+++ b/mcp-planner-server/server.py
@@ -48,6 +48,8 @@ Design rules:
 import contextvars
 import functools
 import hashlib
+import inspect
+import ipaddress
 import hmac
 import json
 import os
@@ -85,6 +87,65 @@ _PROJECTS_REGISTRY_ENV = "PLANNER_PROJECTS_REGISTRY"
 _PROJECTS_REGISTRY_LIMIT = 50
 
 
+# Canonical milestone ids are M followed by digits; leading zeros vary across
+# task headers (M1) and milestone files (M02), so both map to one key.
+_MILESTONE_ID_RE = re.compile(r"^m0*(\d+)$", re.IGNORECASE)
+
+
+def _normalize_milestone(value: object) -> str:
+    """Return the canonical, casefolded key for a milestone label.
+
+    ``M1``, ``m01`` and ``M001`` all become ``M01``. Non-numeric labels are
+    trimmed and casefolded only, preserving the first-seen display spelling at
+    the call site. Empty labels return an empty string so callers can skip them.
+    """
+    text = str(value or "").strip().casefold()
+    if not text:
+        return ""
+    match = _MILESTONE_ID_RE.match(text)
+    if match:
+        return f"M{int(match.group(1)):02d}"
+    return text
+
+
+def _milestone_definitions(workspace_root: Path) -> dict[str, str]:
+    """Read ``tasks/milestones/*.md`` and map canonical id to display title.
+
+    A declared milestone must appear on the board even when no task carries
+    its header, otherwise a closed milestone document is invisible and users
+    read a false "no milestones" state.
+    """
+    result: dict[str, str] = {}
+    folder = workspace_root / "tasks" / "milestones"
+    if not folder.is_dir():
+        return result
+    for path in sorted(folder.glob("*.md")):
+        key = _normalize_milestone(path.stem.split("-", 1)[0])
+        if not key:
+            continue
+        title = path.stem.replace("-", " ")
+        try:
+            with path.open("r", encoding="utf-8") as handle:
+                first_line = handle.readline().strip()
+            if first_line.startswith("#"):
+                title = first_line.lstrip("#").strip()
+        except OSError:
+            pass
+        result[key] = title
+    return result
+
+
+def _utc_today() -> date:
+    """Return today's calendar date in UTC, the project's stored-time basis.
+
+    Task stamps are parsed as UTC (``_parse_utc``) and the documented contract
+    (DECISIONS.md) is UTC-at-rest. Anchoring day/week buckets on the host's
+    local date split a task's finish date from the bucket that displays it on
+    any non-UTC host, so every day/week decision goes through this helper.
+    """
+    return datetime.now(timezone.utc).date()
+
+
 def _registry_path() -> Path:
     """Machine-local registry of projects that have used the planner."""
     override = os.environ.get(_PROJECTS_REGISTRY_ENV, "").strip()
@@ -132,11 +193,15 @@ def _project_tool(fn):
 
     @functools.wraps(fn)
     def wrapper(*args, **kwargs):
+        # Bind against the real signature before reading project_root. The old
+        # args[0] heuristic misread the first positional argument of tools whose
+        # first parameter is not a root (plan_propose's goal, sprint_lock's id),
+        # which registered a bogus project path in the shared registry.
+        bound = inspect.signature(fn).bind(*args, **kwargs)
+        bound.apply_defaults()
         _FALLBACK_FIRED.set(False)
         out = fn(*args, **kwargs)
-        requested = kwargs.get("project_root")
-        if requested is None and args and isinstance(args[0], str):
-            requested = args[0]
+        requested = bound.arguments.get("project_root")
         if requested and str(requested).strip():
             _register_project(Path(str(requested)).expanduser())
         if not _FALLBACK_FIRED.get():
@@ -622,12 +687,13 @@ def plan_materialize(
     Args:
         project_root: Absolute path to the project holding tasks/.
         task_ids: Comma-separated list of task IDs to materialize.
-        Returns:
+
+    Returns:
         Summary of created files and any validation results.
 
-        Notes:
-        Planner metadata (**Estimate:**, **Milestone:**, **Deadline:**,
-        **Depends on:**) is deliberately left out: only the Manager knows
+    Notes:
+        Planner metadata (Estimate, Milestone, Deadline and Depends on
+        headers) is deliberately left out: only the Manager knows
         those values, and a fabricated placeholder would pollute the derived
         read model (an `Estimate: TBD` never parses and a `Deadline: TBD`
         would appear on the dashboard timeline).
@@ -715,7 +781,7 @@ Materialized from planner proposal. Review and refine before execution.
 
 ## Execution Log & Reasoning
 
-Materialized by planner on {date.today().isoformat()}.
+Materialized by planner on {_utc_today().isoformat()}.
 
 ## Factual Git Diff
 
@@ -1075,7 +1141,7 @@ def claim_next(project_root: str, task_id: str) -> str:
         if not raw:
             continue
         try:
-            if date.fromisoformat(str(raw)) < date.today():
+            if date.fromisoformat(str(raw)) < _utc_today():
                 overdue.append(str(_task_brief(candidate).get("id")))
         except ValueError:
             continue
@@ -1174,9 +1240,9 @@ def plan_status(project_root: Optional[str] = None) -> str:
     for t in tasks:
         m = t.get("milestone")
         if m:
-            # Group case-insensitively so M03 and m03 read as one
-            # milestone; display keeps the first-seen spelling.
-            key = str(m).casefold()
+            # Unified with the dashboard and ADR-013: M1 and M01 are one
+            # milestone, and M03/m03 merge. First-seen spelling is displayed.
+            key = _normalize_milestone(m)
             display.setdefault(key, str(m))
             milestones.setdefault(key, []).append(t)
     if not milestones:
@@ -1219,7 +1285,7 @@ def _week_range(week: Optional[str] = None):
 
 def _finished_today_count(tasks) -> int:
     """Count tasks whose Finished stamp falls on today's UTC date."""
-    today = datetime.now(timezone.utc).date()
+    today = _utc_today()
     count = 0
     for t in tasks:
         finished = _parse_task_timestamp(t.get("finished_at"))
@@ -1383,9 +1449,8 @@ def milestone_status(project_root: Optional[str] = None) -> str:
     for t in tasks:
         m = t.get("milestone")
         if m:
-            # Same casefold grouping as plan_status: one milestone
-            # regardless of spelling case, first-seen display.
-            key = str(m).casefold()
+            # Same canonical grouping as plan_status and /api/status.
+            key = _normalize_milestone(m)
             display.setdefault(key, str(m))
             milestones.setdefault(key, []).append(t)
 
@@ -1430,7 +1495,7 @@ def sprint_lock(sprint_id: str, project_root: Optional[str] = None) -> str:
     plan_dir.mkdir(parents=True, exist_ok=True)
     lock_file = plan_dir / f"sprint-{sprint_id}.lock"
     lock_file.write_text(
-        json.dumps({"sprint_id": sprint_id, "locked_at": date.today().isoformat()}),
+        json.dumps({"sprint_id": sprint_id, "locked_at": _utc_today().isoformat()}),
         encoding="utf-8",
     )
     return (
@@ -1464,7 +1529,7 @@ def sprint_daily_agenda(project_root: Optional[str] = None) -> str:
     lines: list[str] = ["# Daily Agenda", ""]
     week_plan = _read_week_plan(workspace_root, _plan_week_key())
     if week_plan:
-        today_key = date.today().isoformat()
+        today_key = _utc_today().isoformat()
         committed_today = [
             task_id
             for task_id, day_key in (week_plan.get("deadline_edits") or {}).items()
@@ -1521,7 +1586,7 @@ def sprint_daily_agenda(project_root: Optional[str] = None) -> str:
             if not raw or task.get("lane") not in ("backlog", "in-progress", "qa"):
                 continue
             try:
-                if date.fromisoformat(str(raw)) < date.today():
+                if date.fromisoformat(str(raw)) < _utc_today():
                     overdue_ids.append(str(_task_brief(task).get("id")))
             except ValueError:
                 continue
@@ -1848,15 +1913,56 @@ def _relative_root(project_root: Optional[str]) -> bool:
         return True
 
 
+_TRUSTED_PROXY_ENV = "PLANNER_TRUSTED_PROXIES"
+_LOOPBACK_IPS = frozenset({"127.0.0.1", "::1", "::ffff:127.0.0.1"})
+# In-process ASGI clients report a synthetic label instead of a socket IP.
+# Only these exact labels are trusted; an arbitrary hostname fails closed.
+_IN_PROCESS_PEERS = frozenset({"testclient", "unix", "localhost"})
+
+
+def _is_loopback_peer(peer: str) -> bool:
+    """True only for a loopback IP or a known in-process transport label.
+
+    Any peer that is neither a parseable loopback IP nor one of the explicit
+    in-process labels is rejected. A bare ``ValueError`` fallback used to trust
+    every non-IP peer, so a hostname such as ``evil.example`` bypassed the
+    ``/mcp`` loopback guard. Fail closed instead.
+    """
+    if not peer:
+        return False
+    try:
+        return ipaddress.ip_address(peer).is_loopback
+    except ValueError:
+        return peer in _IN_PROCESS_PEERS
+
+
+def _trusted_proxy_ips() -> frozenset[str]:
+    """IPs allowed to set ``X-Forwarded-Proto`` for cookie/HSTS decisions.
+
+    Defaults to loopback so the existing Cloudflare Tunnel setup keeps working:
+    cloudflared connects from 127.0.0.1. A deployment with a remote reverse
+    proxy should set ``PLANNER_TRUSTED_PROXIES`` explicitly rather than trusting
+    a header from any peer.
+    """
+    raw = os.environ.get(_TRUSTED_PROXY_ENV, "").strip()
+    if not raw:
+        return _LOOPBACK_IPS
+    return frozenset({part.strip() for part in raw.split(",") if part.strip()})
+
+
 def _is_https(request) -> bool:
     """True when the request reached the app over HTTPS.
 
-    The dashboard sits behind a Cloudflare Tunnel, so the origin sees plain
-    HTTP and must trust ``X-Forwarded-Proto``. Used to decide the session
-    cookie's ``Secure`` flag and whether HSTS may be sent.
+    A forwarded protocol header is honoured only from a configured trusted
+    proxy. An arbitrary direct client can no longer force ``Secure`` cookies
+    and HSTS by sending ``X-Forwarded-Proto: https`` over plain HTTP.
     """
     proto = (request.headers.get("x-forwarded-proto") or "").split(",")[0].strip()
-    if proto:
+    client = getattr(request, "client", None)
+    peer = str(getattr(client, "host", "") or "")
+    configured = os.environ.get(_TRUSTED_PROXY_ENV, "").strip()
+    trusted = peer in _trusted_proxy_ips() if configured else _is_loopback_peer(peer)
+    if proto and trusted:
         return proto.lower() == "https"
     return request.url.scheme == "https"
 
@@ -2175,7 +2281,7 @@ def _api_hours(
         workspace_root = fallback
 
     try:
-        today = date.today()
+        today = _utc_today()
         day_keys = [
             (today - timedelta(days=offset)).isoformat() for offset in range(14)
         ]
@@ -2353,7 +2459,7 @@ _PLAN_DIR_NAME = ".plan"
 
 def _plan_week_key(day: Optional[date] = None) -> str:
     """ISO week key for a date, e.g. ``2026-W43``."""
-    target = day or date.today()
+    target = day or _utc_today()
     iso = target.isocalendar()
     return f"{iso[0]}-W{iso[1]:02d}"
 
@@ -2502,7 +2608,7 @@ def _plan_payload(
             return {"error": "forbidden"}
         root = fallback
 
-    today = date.today()
+    today = _utc_today()
     week_start = today - timedelta(days=today.weekday())
     capacity = float(_WEEKLY_CAPACITY_HOURS or 0)
 
@@ -2562,6 +2668,17 @@ def _plan_payload(
 
     day_rows = [bucket_for(day) for day in days]
 
+    def _week_capacity(row_count: int) -> float:
+        """Scale weekly capacity to the days actually present in a bucket.
+
+        Month views start and end on partial ISO weeks. Charging a full week
+        to a one-day bucket inflated remaining hours, so a short week looked
+        like spare capacity that did not exist.
+        """
+        if window != "month":
+            return capacity
+        return round(capacity * row_count / 7, 2)
+
     # Undated open work is what "still to do" means in practice: most task
     # files carry no deadline, so counting deadlines alone would render an
     # empty cockpit. Attribute it to the current bucket (today, this week, or
@@ -2609,8 +2726,8 @@ def _plan_payload(
                     "estimate_hours": estimate,
                     # everything with a deadline in the window, so finished work stays visible
                     "committed_hours": committed,
-                    "capacity_hours": capacity,
-                    "remaining_hours": round(capacity - estimate, 2),
+                    "capacity_hours": _week_capacity(len(rows)),
+                    "remaining_hours": round(_week_capacity(len(rows)) - estimate, 2),
                 }
             )
 
@@ -2633,7 +2750,7 @@ def _plan_payload(
         "in_progress": sum(b["in_progress"] for b in day_rows),
         "done": sum(b["done"] for b in day_rows),
         "estimate_hours": round(sum(b["estimate_hours"] for b in day_rows), 2),
-        "capacity_hours": capacity,
+        "capacity_hours": _week_capacity(len(day_rows)),
     }
 
     return {
@@ -2658,9 +2775,11 @@ def _api_status(
     counts — the UI renders each lane as a list), the milestone tree, the
     upcoming deadlines plotted on the timeline, and today's pacing figures.
 
-    Pacing mirrors :func:`sprint_check_daily_quota`: a day is complete when no
-    task sits in ``in-progress`` and none waits in ``qa``, so ``done`` is the
-    batch target minus the open working set.
+    ``today.done`` is the real number of tasks whose Finished stamp falls on
+    today's UTC date. ``today.open`` is the in-progress plus QA working set,
+    and ``quota_reached`` uses the same no-open-work rule as
+    :func:`sprint_check_daily_quota`. Deriving ``done`` from ``target - open``
+    used to report three finished tasks on every project with an empty board.
 
     Args:
         project_root: Optional absolute project root from the query string.
@@ -2701,12 +2820,19 @@ def _api_status(
                 lanes[lane].append(brief)
             milestone = task.get("milestone")
             if milestone:
-                milestone_tree.setdefault(milestone, []).append(brief)
+                key = _normalize_milestone(milestone)
+                if key:
+                    milestone_tree.setdefault(key, []).append(brief)
             if task.get("deadline"):
                 deadlines.append(brief)
 
         for items in milestone_tree.values():
             items.sort(key=lambda b: _task_sort_key(b.get("name") or ""))
+        # A milestone document is a declaration even with zero tagged tasks.
+        # Seed it at the top so M02 is visible alongside M01 and M03.
+        for key, title in _milestone_definitions(workspace_root).items():
+            items = milestone_tree.setdefault(key, [])
+            items.insert(0, {"name": "0", "title": title, "status": "declared"})
         deadlines.sort(key=lambda t: t.get("deadline") or "")
         open_work = len(lanes["in-progress"]) + len(lanes["qa"])
 
@@ -2719,16 +2845,20 @@ def _api_status(
             "backlog": len(lanes["backlog"]),
             "completed": len(lanes["completed"]),
             "today": {
-                "done": max(0, _DAILY_TARGET - open_work),
+                "done": _finished_today_count(tasks),
                 "target": _DAILY_TARGET,
                 "open": open_work,
+                "quota_reached": open_work == 0,
             },
             "lanes": lanes,
             "milestone_tree": milestone_tree,
             "deadlines": deadlines,
         }
     except Exception as exc:  # noqa: BLE001
-        return {"error": str(exc)}
+        # Internal failures must not travel as HTTP 200: the dashboard used to
+        # paint a green "Server reachable" badge over a stale board. A stable
+        # sentinel lets the route answer 500 while the detail stays in JSON.
+        return {"error": "internal error", "detail": str(exc)}
 
 
 def _guarded_mcp_app(mcp_app):
@@ -2743,6 +2873,18 @@ def _guarded_mcp_app(mcp_app):
     """
 
     async def loopback_only(scope, receive, send):
+        # ADR-006 keeps /mcp auth-free and expects the network edge to block
+        # remote callers. Enforce that boundary here too: a bind misconfiguration
+        # or a misordered tunnel rule must fail closed instead of exposing all
+        # writing tools to an off-host caller.
+        from starlette.responses import JSONResponse
+
+        client = scope.get("client") or ()
+        peer = str(client[0]) if client else ""
+        if not _is_loopback_peer(peer):
+            response = JSONResponse({"error": "forbidden"}, status_code=403)
+            await response(scope, receive, send)
+            return
         await mcp_app(scope, receive, send)
 
     return loopback_only
@@ -2779,6 +2921,8 @@ def build_app():
             return JSONResponse(payload, status_code=401)
         if error == "forbidden":
             return JSONResponse(payload, status_code=403)
+        if error == "internal error":
+            return JSONResponse(payload, status_code=500)
         return JSONResponse(payload)
 
     async def api_task(request):
@@ -2905,7 +3049,23 @@ def build_app():
             return JSONResponse({"error": "invalid JSON body"}, status_code=400)
         if not isinstance(body, dict):
             return JSONResponse({"error": "invalid JSON body"}, status_code=400)
-        root = _resolve_dashboard_root(None)
+        # The selected project travels with every save. Resolving None here
+        # silently wrote edits into the daemon's default project when the board
+        # was showing a different one.
+        requested_root = body.get("project_root") or request.query_params.get(
+            "project_root"
+        )
+        if (
+            not isinstance(requested_root, str)
+            or not requested_root.strip()
+            or _relative_root(requested_root)
+        ):
+            return JSONResponse(
+                {"error": "project_root must be an absolute path"}, status_code=400
+            )
+        if not Path(requested_root).expanduser().is_dir():
+            return JSONResponse({"error": "unknown project_root"}, status_code=404)
+        root = _resolve_dashboard_root(requested_root)
         if auth is not None and not auth.project_allowed(root):
             fallback = _first_allowed_root(auth)
             if fallback is None:
@@ -2931,7 +3091,18 @@ def build_app():
             return JSONResponse(
                 {"error": "week must look like 2026-W43"}, status_code=400
             )
-        root = _resolve_dashboard_root(None)
+        requested_root = request.query_params.get("project_root")
+        if (
+            not isinstance(requested_root, str)
+            or not requested_root.strip()
+            or _relative_root(requested_root)
+        ):
+            return JSONResponse(
+                {"error": "project_root must be an absolute path"}, status_code=400
+            )
+        if not Path(requested_root).expanduser().is_dir():
+            return JSONResponse({"error": "unknown project_root"}, status_code=404)
+        root = _resolve_dashboard_root(requested_root)
         if auth is not None and not auth.project_allowed(root):
             fallback = _first_allowed_root(auth)
             if fallback is None:
@@ -2978,9 +3149,12 @@ def build_app():
         token = secrets.token_urlsafe(32)
         _SESSIONS[token] = {"user": user, "created": time.time()}
         state = AuthState(_USER_CONFIG, user, _SESSIONS)
+        # The token travels only in the HttpOnly cookie. Returning it in the
+        # response body widened exposure to any script that can read the login
+        # response; ``ok`` lets the client detect success without the secret.
         response = JSONResponse(
             {
-                "token": token,
+                "ok": True,
                 "username": state.username,
                 "role": state.role,
                 "allowed_projects": state.allowed_projects,
diff --git a/mcp-planner-server/static/index.html b/mcp-planner-server/static/index.html
index 5f881a1..9226bfb 100644
--- a/mcp-planner-server/static/index.html
+++ b/mcp-planner-server/static/index.html
@@ -23,7 +23,7 @@
         <span class="badge text-bg-secondary" id="user-role">—</span>
       </div>
       <button type="button" class="btn btn-sm btn-outline-secondary d-none" id="logout-btn">Logout</button>
-      <span class="badge text-bg-secondary" id="status-chip"><span class="mono" id="status-dot">•</span> <span id="status-text">Loading…</span></span>
+      <span class="badge text-bg-secondary" id="status-chip"><span class="mono" id="status-dot">•</span> <span id="status-text" aria-live="polite" role="status">Loading…</span></span>
     </div>
   </header>
 
@@ -125,7 +125,7 @@
       <span class="label mb-0">Kanban lanes</span>
     </div>
     <input type="search" id="board-search" class="form-control form-control-sm mb-3" placeholder="Filter tasks by ID or title…" autocomplete="off" aria-label="Filter tasks">
-    <div class="d-flex justify-content-end mb-2"><button type="button" class="btn btn-sm btn-outline-secondary" id="mine-toggle" aria-pressed="false">Mine only</button></div>
+    <div class="d-flex justify-content-end mb-2"><button type="button" class="btn btn-sm btn-outline-secondary d-none" id="mine-toggle" aria-pressed="false">Mine only</button></div>
     <div class="row g-3" id="lanes-grid"></div>
   </section>
 
@@ -144,12 +144,12 @@
 </div>
 
 <!-- Login overlay -->
-<div class="gd-overlay hidden" id="login-modal">
-  <div class="gd-panel gd-panel-md p-4">
-    <h2 class="h6 mb-1">Sign in to Planner</h2>
+<div class="gd-overlay hidden" id="login-modal" role="dialog" aria-modal="true" aria-labelledby="login-title">
+  <div class="gd-panel gd-panel-md p-4" role="document">
+    <h2 class="h6 mb-1" id="login-title">Sign in to Planner</h2>
     <p class="small text-muted mb-3">Authentication is enabled on this server.</p>
     <form id="login-form" method="post" action="#" novalidate>
-      <div class="small mb-2" id="login-err" style="color:var(--gd-danger);min-height:1.2em"></div>
+      <div class="small mb-2" id="login-err" role="alert" style="color:var(--gd-danger);min-height:1.2em"></div>
       <div class="mb-2">
         <label class="form-label" for="login-username">Username</label>
         <input type="text" id="login-username" name="username" class="form-control form-control-sm"
@@ -169,8 +169,8 @@
 </div>
 
 <!-- Task overlay -->
-<div class="gd-overlay hidden" id="task-modal">
-  <div class="gd-panel gd-panel-lg">
+<div class="gd-overlay hidden" id="task-modal" role="dialog" aria-modal="true" aria-labelledby="task-modal-title">
+  <div class="gd-panel gd-panel-lg" role="document">
     <div class="d-flex align-items-start justify-content-between gap-3 p-3 border-bottom">
       <h2 class="h6 mb-0" id="task-modal-title">Task</h2>
       <div class="d-flex gap-2">
@@ -192,6 +192,9 @@
   // "board served a page" failure on deep links.
   const BASE_STATUS_URL = window.location.origin + '/api/status';
   let currentProject = '';
+  // Rebuilding the project selector on every 30 s poll closed an open dropdown
+  // and lost keyboard focus, so only a real project-list change rebuilds it.
+  let lastProjectSignature = '';
   let query = '';
   let lastData = null;
   let archiveOpen = false;
@@ -253,9 +256,18 @@
     return window.jalaali.toJalaali(date.getFullYear(), date.getMonth() + 1, date.getDate());
   }
 
+  // The Gregorian day shown beside a Jalali date must come from the same
+  // local calendar components. toISOString() shifts to UTC, so in UTC+ zones
+  // the tooltip showed the previous day for the first hours after midnight.
+  function localISO(d) {
+    const month = String(d.getMonth() + 1).padStart(2, '0');
+    const day = String(d.getDate()).padStart(2, '0');
+    return d.getFullYear() + '-' + month + '-' + day;
+  }
+
   function formatJalali(d) {
     const j = jalaliOf(d);
-    if (!j) return d.toISOString().slice(0, 10);
+    if (!j) return localISO(d);
     return j.jd + ' ' + JALALI_MONTHS[j.jm - 1] + ' ' + j.jy;
   }
 
@@ -270,10 +282,30 @@
     return url + (url.indexOf('?') >= 0 ? '&' : '?') + '_t=' + Date.now();
   }
 
+  // Never leave the previous project's cards on screen while a new project
+  // loads, and never keep them after a 401/403. A stale board with a new
+  // dropdown value is misleading and was the source of "wrong project" reports.
+  function clearBoard() {
+    lastData = null;
+    elements.lanesGrid.innerHTML = '<div class="text-muted small p-3">Loading…</div>';
+    elements.milestoneTree.innerHTML = '<div class="text-muted small">Loading…</div>';
+    elements.planView.innerHTML = '<div class="text-muted small">Loading…</div>';
+    // Clear every derived panel: a project switch used to keep the previous
+    // project's timeline and charts visible behind the new dropdown value.
+    elements.timeline.innerHTML = '';
+    elements.hoursChart.innerHTML = '<div class="small text-muted">Loading…</div>';
+    elements.cfdChart.innerHTML = '<div class="small text-muted">Loading…</div>';
+    elements.controlChart.innerHTML = '<div class="small text-muted">Loading…</div>';
+    elements.deadlineRail.innerHTML = '<div class="small text-muted">Loading…</div>';
+    elements.statusChip.className = 'badge text-bg-secondary';
+    elements.statusText.textContent = 'Loading…';
+  }
+
   async function fetchStatus(retry) {
     try {
       const resp = await fetch(bust(statusUrl()), { cache: 'no-cache' });
       if (resp.status === 401) {
+        clearBoard();
         hideUserBadge();
         showLoginModal();
         elements.statusChip.className = 'badge text-bg-danger';
@@ -281,6 +313,7 @@
         return;
       }
       if (resp.status === 403) {
+        clearBoard();
         elements.statusChip.className = 'badge text-bg-danger';
         elements.statusText.textContent = 'Access denied for this project';
         return;
@@ -304,7 +337,10 @@
           ? 'board served a page (' + contentType + ') instead of data (edge login expired or /api/* misrouted)'
           : 'board served invalid data (' + contentType + ')');
       }
-      render(data);
+      // render() reports whether the payload was usable. A 200 response can
+      // still carry {"error": "..."}; in that case keep the danger badge
+      // instead of claiming the board is healthy.
+      if (!render(data)) return;
       elements.statusChip.className = 'badge text-bg-success';
       elements.statusText.textContent = 'Server reachable';
       if (pendingDeepTask) {
@@ -327,8 +363,8 @@
   function render(data) {
     if (data.error) {
       elements.statusChip.className = 'badge text-bg-danger';
-      elements.statusText.textContent = 'Error: ' + data.error;
-      return;
+      elements.statusText.textContent = 'Error: ' + (data.detail || data.error);
+      return false;
     }
     lastData = data;
 
@@ -352,61 +388,28 @@
 
     const projects = data.projects || [];
     if (projects.length) {
-      elements.projectSelect.innerHTML = projects.map(p =>
-        '<option value="' + escapeHtml(p.path) + '"' + (p.path === data.project_root ? ' selected' : '') + '>' + escapeHtml(p.label) + '</option>'
-      ).join('');
+      const signature = projects.map(function (p) { return p.path + '|' + p.label; }).join('||');
+      if (signature !== lastProjectSignature) {
+        lastProjectSignature = signature;
+        elements.projectSelect.innerHTML = projects.map(p =>
+          '<option value="' + escapeHtml(p.path) + '"' + (p.path === data.project_root ? ' selected' : '') + '>' + escapeHtml(p.label) + '</option>'
+        ).join('');
+      }
       currentProject = data.project_root || projects[0].path;
     }
 
-    // Lanes
-    const lanes = data.lanes || {};
-    elements.lanesGrid.innerHTML = '';
-    const laneOrder = ['backlog', 'in-progress', 'qa', 'completed', 'archive'];
-    const laneLabels = { backlog: 'Backlog', 'in-progress': 'In Progress', qa: 'QA / Review', completed: 'Completed', archive: 'Archive' };
-    const needle = query.trim().toLowerCase();
-    laneOrder.forEach(function (lane) {
-      const all = lanes[lane] || [];
-      const scoped = mineOnly && currentUser ? all.filter(function (t) { return t.owner === currentUser; }) : all;
-      const items = needle ? scoped.filter(function (t) { return taskMatches(t, needle); }) : scoped;
-      const isArchive = lane === 'archive';
-      const collapsed = isArchive && !archiveOpen;
-      const chipClass = { backlog: 'text-bg-secondary', 'in-progress': 'text-bg-info', qa: 'text-bg-warning', completed: 'text-bg-success', archive: 'text-bg-secondary' }[lane];
-      const header = '<span>' + laneLabels[lane] + ' <span class="badge ' + chipClass + '">' + all.length + '</span></span>' +
-        (isArchive ? '<button type="button" class="btn btn-sm btn-outline-secondary" id="archive-toggle" aria-expanded="' + (archiveOpen ? 'true' : 'false') + '">' + (archiveOpen ? 'Collapse' : 'Expand') + '</button>' : '');
-      const rows = items.length === 0
-        ? '<div class="text-muted small p-2">' + (needle ? 'No matches' : '—') + '</div>'
-        : items.map(function (t) {
-          return '<div class="task-row" role="button" tabindex="0" data-id="' + escapeHtml(t.id || t.name || '') + '" data-path="' + escapeHtml(t.path || '') + '">' +
-            '<span class="id">' + escapeHtml(t.id || t.name || 'task') + '</span> — ' + escapeHtml(t.title || 'untitled') +
-            (t.owner ? ' <span class="badge text-bg-secondary">' + escapeHtml(t.owner) + '</span>' : '') +
-            (t.blocked ? ' <span class="badge text-bg-danger">BLOCKED</span>' : '') +
-            (t.blocked && t.blocked_reason && t.blocked_reason !== 'none' ? ' <span class="text-muted small">' + escapeHtml(t.blocked_reason) + '</span>' : '') +
-            (t.swarm && t.swarm !== 'none' ? ' <span class="badge text-bg-warning">swarm: ' + escapeHtml(t.swarm) + '</span>' : '') +
-            (t.lane === 'in-progress' && t.started_at && isStale(t.started_at) ? ' <span class="badge text-bg-danger">STALE</span>' : '') +
-            (t.estimate_hours != null ? ' <span class="text-muted">' + t.estimate_hours + 'h</span>' : '') +
-            (t.elapsed_seconds != null ? ' <span class="text-muted mono">· lead time ' + formatDuration(t.elapsed_seconds) + '</span>' : '') +
-            '</div>';
-        }).join('');
-      const hint = isArchive && needle && items.length
-        ? '<div class="lane-hint mb-1">' + items.length + ' match(es) in Archive' + (collapsed ? ' — expand to view' : '') + '</div>'
-        : '';
-      const col = document.createElement('div');
-      col.className = 'col-12 col-md-6 col-xl';
-      col.innerHTML = '<div class="card lane-card h-100"><div class="card-header">' + header + '</div>' +
-        '<div class="card-body py-2">' + hint + '<div class="lane-list' + (collapsed ? ' hidden' : '') + '">' + rows + '</div></div></div>';
-      elements.lanesGrid.appendChild(col);
-    });
-    const toggle = document.getElementById('archive-toggle');
-    if (toggle) {
-      toggle.addEventListener('click', function () {
-        archiveOpen = !archiveOpen;
-        try { window.localStorage.setItem('planner-archive-open', archiveOpen ? '1' : '0'); } catch (e) { /* storage may be blocked */ }
-        if (lastData) render(lastData);
-      });
-    }
+    // Lanes are updated separately so typing in the search box does not
+    // rebuild milestones, the timeline, or the project selector.
+    renderLanes(data);
 
     // Milestones
     const tree = data.milestone_tree || {};
+    // Remember which milestone nodes the user collapsed. A full status poll
+    // used to reset every node to expanded, losing their reading position.
+    const collapsedMilestones = new Set();
+    elements.milestoneTree.querySelectorAll('.ms-node.collapsed').forEach(function (node) {
+      if (node.dataset.ms) collapsedMilestones.add(node.dataset.ms);
+    });
     elements.milestoneTree.innerHTML = '';
     if (!tree || Object.keys(tree).length === 0) {
       elements.milestoneTree.innerHTML = '<div class="text-muted small">No milestones defined.</div>';
@@ -416,16 +419,20 @@
         const items = entry[1];
         const node = document.createElement('div');
         node.className = 'ms-node';
+        node.dataset.ms = ms;
+        if (collapsedMilestones.has(ms)) node.classList.add('collapsed');
         const done = items.filter(function (i) { return i.status === 'closed'; }).length;
         node.innerHTML = '<div class="d-flex align-items-center gap-2">' +
-          '<button type="button" class="btn btn-sm btn-outline-secondary py-0 px-1" data-arrow>▾</button>' +
+          '<button type="button" class="btn btn-sm btn-outline-secondary py-0 px-1" data-arrow aria-label="Toggle milestone ' + escapeHtml(ms) + '" aria-expanded="' + (collapsedMilestones.has(ms) ? 'false' : 'true') + '">▾</button>' +
           '<strong class="small">' + escapeHtml(ms) + '</strong>' +
           '<span class="text-muted small mono">' + done + '/' + items.length + '</span></div>' +
           '<div class="children mt-1">' + items.map(function (i) {
             return '<div class="small text-muted">• ' + escapeHtml(i.title || i.name || 'untitled') + ' [' + escapeHtml(i.status || 'open') + ']</div>';
           }).join('') + '</div>';
         node.querySelector('[data-arrow]').addEventListener('click', function () {
-          node.classList.toggle('collapsed');
+          const isCollapsed = node.classList.toggle('collapsed');
+          this.setAttribute('aria-expanded', isCollapsed ? 'false' : 'true');
+          this.textContent = isCollapsed ? '▸' : '▾';
         });
         elements.milestoneTree.appendChild(node);
       });
@@ -458,10 +465,61 @@
         '<div class="cal-secondary">' + d.getDate() + (j ? '' : ' (G)') + '</div>' +
         (monthLabel ? '<div class="cal-secondary">' + monthLabel + '</div>' : '') +
         (due.length ? '<div class="cal-secondary">•' + due.length + '</div>' : '');
-      div.title = (j ? formatJalali(d) + ' · ' : '') + d.toISOString().slice(0, 10) + ' — ' +
+      div.title = (j ? formatJalali(d) + ' · ' : '') + localISO(d) + ' — ' +
         (due.length ? due.map(function (t) { return t.title; }).join(', ') : 'no deadlines');
       elements.timeline.appendChild(div);
     }
+    return true;
+  }
+
+  function renderLanes(data) {
+    const lanes = data.lanes || {};
+    elements.lanesGrid.innerHTML = '';
+    const laneOrder = ['backlog', 'in-progress', 'qa', 'completed', 'archive'];
+    const laneLabels = { backlog: 'Backlog', 'in-progress': 'In Progress', qa: 'QA / Review', completed: 'Completed', archive: 'Archive' };
+    const needle = query.trim().toLowerCase();
+    laneOrder.forEach(function (lane) {
+      const all = lanes[lane] || [];
+      const scoped = mineOnly && currentUser ? all.filter(function (t) { return t.owner === currentUser; }) : all;
+      const items = needle ? scoped.filter(function (t) { return taskMatches(t, needle); }) : scoped;
+      const isArchive = lane === 'archive';
+      const collapsed = isArchive && !archiveOpen;
+      const chipClass = { backlog: 'text-bg-secondary', 'in-progress': 'text-bg-info', qa: 'text-bg-warning', completed: 'text-bg-success', archive: 'text-bg-secondary' }[lane];
+      // Badge is the lane total, independent of the search/Mine filter;
+      // only the rendered rows are filtered.
+      const header = '<span>' + laneLabels[lane] + ' <span class="badge ' + chipClass + '">' + all.length + '</span></span>' +
+        (isArchive ? '<button type="button" class="btn btn-sm btn-outline-secondary" id="archive-toggle" aria-expanded="' + (archiveOpen ? 'true' : 'false') + '">' + (archiveOpen ? 'Collapse' : 'Expand') + '</button>' : '');
+      const rows = items.length === 0
+        ? '<div class="text-muted small p-2">' + (needle ? 'No matches' : '—') + '</div>'
+        : items.map(function (t) {
+          return '<div class="task-row" role="button" tabindex="0" data-id="' + escapeHtml(t.id || t.name || '') + '" data-path="' + escapeHtml(t.path || '') + '">' +
+            '<span class="id">' + escapeHtml(t.id || t.name || 'task') + '</span> — ' + escapeHtml(t.title || 'untitled') +
+            (t.owner ? ' <span class="badge text-bg-secondary">' + escapeHtml(t.owner) + '</span>' : '') +
+            (t.blocked ? ' <span class="badge text-bg-danger">BLOCKED</span>' : '') +
+            (t.blocked && t.blocked_reason && t.blocked_reason !== 'none' ? ' <span class="text-muted small">' + escapeHtml(t.blocked_reason) + '</span>' : '') +
+            (t.swarm && t.swarm !== 'none' ? ' <span class="badge text-bg-warning">swarm: ' + escapeHtml(t.swarm) + '</span>' : '') +
+            (t.lane === 'in-progress' && t.started_at && isStale(t.started_at) ? ' <span class="badge text-bg-danger">STALE</span>' : '') +
+            (t.estimate_hours != null ? ' <span class="text-muted">' + escapeHtml(t.estimate_hours) + 'h</span>' : '') +
+            (t.elapsed_seconds != null ? ' <span class="text-muted mono">· lead time ' + formatDuration(t.elapsed_seconds) + '</span>' : '') +
+            '</div>';
+        }).join('');
+      const hint = isArchive && needle && items.length
+        ? '<div class="lane-hint mb-1">' + items.length + ' match(es) in Archive' + (collapsed ? ' — expand to view' : '') + '</div>'
+        : '';
+      const col = document.createElement('div');
+      col.className = 'col-12 col-md-6 col-xl';
+      col.innerHTML = '<div class="card lane-card h-100"><div class="card-header">' + header + '</div>' +
+        '<div class="card-body py-2">' + hint + '<div class="lane-list' + (collapsed ? ' hidden' : '') + '">' + rows + '</div></div></div>';
+      elements.lanesGrid.appendChild(col);
+    });
+    const toggle = document.getElementById('archive-toggle');
+    if (toggle) {
+      toggle.addEventListener('click', function () {
+        archiveOpen = !archiveOpen;
+        try { window.localStorage.setItem('planner-archive-open', archiveOpen ? '1' : '0'); } catch (e) { /* storage may be blocked */ }
+        if (lastData) renderLanes(lastData);
+      });
+    }
   }
 
   function taskMatches(task, needle) {
@@ -583,7 +641,7 @@
     elements.taskModalTitle.textContent = id ? 'Task ' + id : 'Task';
     elements.taskModalMeta.textContent = 'Loading…';
     elements.taskModalBody.innerHTML = '<p class="text-muted small">Loading…</p>';
-    elements.taskModal.classList.remove('hidden');
+    openDialog(elements.taskModal);
     elements.taskModalClose.focus();
     fetch(bust('/api/task?' + params.toString()), { cache: 'no-cache' })
       .then(async function (resp) {
@@ -614,7 +672,39 @@
       });
   }
 
-  function closeTaskModal() { elements.taskModal.classList.add('hidden'); }
+  // Dialog focus management: keep Tab inside the open dialog and return focus
+  // to the control that opened it, so keyboard users are not stranded on the
+  // board behind the overlay.
+  let modalReturnFocus = null;
+
+  function trapDialogFocus(event, dialog) {
+    const focusable = dialog.querySelectorAll(
+      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
+    );
+    if (!focusable.length) return;
+    const first = focusable[0];
+    const last = focusable[focusable.length - 1];
+    if (event.shiftKey && document.activeElement === first) {
+      event.preventDefault();
+      last.focus();
+    } else if (!event.shiftKey && document.activeElement === last) {
+      event.preventDefault();
+      first.focus();
+    }
+  }
+
+  function openDialog(dialog) {
+    modalReturnFocus = document.activeElement;
+    dialog.classList.remove('hidden');
+  }
+
+  function closeDialog(dialog) {
+    dialog.classList.add('hidden');
+    if (modalReturnFocus && typeof modalReturnFocus.focus === 'function') modalReturnFocus.focus();
+    modalReturnFocus = null;
+  }
+
+  function closeTaskModal() { closeDialog(elements.taskModal); }
 
   elements.lanesGrid.addEventListener('click', function (event) {
     const row = event.target.closest('.task-row');
@@ -640,11 +730,22 @@
     if (event.target === elements.taskModal) closeTaskModal();
   });
   document.addEventListener('keydown', function (event) {
-    if (event.key === 'Escape' && !elements.taskModal.classList.contains('hidden')) closeTaskModal();
+    const openDialog = !elements.taskModal.classList.contains('hidden')
+      ? elements.taskModal
+      : (!auth.modal.classList.contains('hidden') ? auth.modal : null);
+    if (!openDialog) return;
+    if (event.key === 'Escape') {
+      if (openDialog === elements.taskModal) closeTaskModal();
+      else hideLoginModal();
+      return;
+    }
+    if (event.key === 'Tab') trapDialogFocus(event, openDialog);
   });
   elements.search.addEventListener('input', function () {
     query = elements.search.value;
-    if (lastData) render(lastData);
+    // Only the lanes change; rebuilding the whole board here used to collapse
+    // milestones and close an open project selector on every keystroke.
+    if (lastData) renderLanes(lastData);
   });
 
   const mineToggle = document.getElementById('mine-toggle');
@@ -653,7 +754,7 @@
       mineOnly = !mineOnly;
       mineToggle.setAttribute('aria-pressed', mineOnly ? 'true' : 'false');
       mineToggle.className = 'btn btn-sm ' + (mineOnly ? 'btn-primary' : 'btn-outline-secondary');
-      if (lastData) render(lastData);
+      if (lastData) renderLanes(lastData);
     });
   }
 
@@ -695,7 +796,7 @@
       laneChip(t.lane) + ' <span class="id">' + escapeHtml(t.id || '') + '</span> — ' + escapeHtml(t.title || '') +
       (t.estimate_hours != null ? ' <span class="text-muted">' + escapeHtml(t.estimate_hours) + 'h</span>' : '') +
       (committed ? ' <span class="badge text-bg-success">committed</span>' : '') + '</div>' +
-      '<select class="form-select form-select-sm" style="width:8.5rem" data-assign="' + escapeHtml(t.id || '') + '">' + options + '</select>' +
+      '<select class="form-select form-select-sm" style="width:8.5rem" data-assign="' + escapeHtml(t.id || '') + '" aria-label="Set deadline for task ' + escapeHtml(t.id || '') + '">' + options + '</select>' +
       '</div>';
   }
 
@@ -884,15 +985,25 @@
         '<div class="small text-muted">Nothing scheduled for today.</div>';
     } else if (data.window === 'week') {
       const w = (data.weeks || [])[0] || { remaining_hours: 0, estimate_hours: 0, capacity_hours: 0 };
+      const cap = w.capacity_hours || 0;
+      const estimate = w.estimate_hours || 0;
+      const remaining = w.remaining_hours == null ? cap - estimate : w.remaining_hours;
+      const over = Math.max(0, -remaining);
+      // A negative "left" value read as a bug rather than an overrun. Show
+      // zero remaining plus an explicit overrun and colour the bar as an alert.
+      const capLabel = over > 0
+        ? estimate + 'h of ' + cap + 'h · 0h left · ' + over + 'h over'
+        : estimate + 'h of ' + cap + 'h · ' + Math.max(0, remaining) + 'h left';
+      const barColor = over > 0 ? 'var(--gd-danger)' : 'var(--gd-accent)';
       html = '<div class="d-flex justify-content-between small mb-2"><span class="text-muted">Capacity</span><span class="mono">' +
-        (w.estimate_hours || 0) + 'h of ' + (w.capacity_hours || 0) + 'h · ' + (w.remaining_hours || 0) + 'h left</span></div>' +
+        capLabel + '</span></div>' +
         '<div class="progress mb-2" style="height:6px;background:var(--gd-raised)"><div class="progress-bar" style="width:' +
-        Math.min(100, Math.round(((w.estimate_hours || 0) / Math.max(1, w.capacity_hours || 1)) * 100)) + '%;background:var(--gd-accent)"></div></div>' +
+        (cap > 0 ? Math.min(100, Math.round(estimate / cap * 100)) : (estimate > 0 ? 100 : 0)) + '%;background:' + barColor + '"></div></div>' +
         days.map(function (d) {
           return '<div class="d-flex justify-content-between align-items-center border-bottom py-1 small gap-2"><span>' + d.date.slice(5) + '</span>' +
             '<span class="mono text-muted">' + d.open + ' open · ' + d.in_progress + ' wip · ' + d.done + ' done · ' + (d.estimate_hours || 0) + 'h</span>' +
             '<input type="number" min="0" step="0.5" class="form-control form-control-sm" style="width:5.5rem" data-cap="' + d.date + '" value="' +
-            (((data.plan || {}).capacity_by_day || {})[d.date] || '') + '" aria-label="Capacity ' + d.date + '"></div>';
+            (((data.plan || {}).capacity_by_day || {})[d.date] ?? '') + '" aria-label="Capacity ' + d.date + '"></div>';
         }).join('');
     } else {
       html = (data.weeks || []).map(function (w) {
@@ -935,7 +1046,9 @@
     fetch('/api/plan', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
-      body: JSON.stringify({ deadline_edits: deadline_edits, capacity_by_day: capacity_by_day, approved: !!approved }),
+      // Carry the selected project so the server never falls back to its
+      // default root and silently writes this edit into another project.
+      body: JSON.stringify({ project_root: currentProject, deadline_edits: deadline_edits, capacity_by_day: capacity_by_day, approved: !!approved }),
     }).then(function (resp) { return resp.json().then(function (body) { return { ok: resp.ok, body: body }; }); })
       .then(function (res) {
         elements.planTotals.textContent = res.ok ? (approved ? 'Plan approved' : 'Plan saved') : 'Save failed: ' + (res.body.error || 'error');
@@ -954,8 +1067,11 @@
 
   elements.projectSelect.addEventListener('change', function () {
     currentProject = elements.projectSelect.value;
+    clearBoard();
+    // Match refreshAll so no panel is left showing the previous project.
     fetchStatus();
     fetchPlan();
+    fetchHours();
     loadCFD();
     loadControlChart();
   });
@@ -976,13 +1092,13 @@
   };
 
   function showLoginModal() {
-    auth.modal.classList.remove('hidden');
+    openDialog(auth.modal);
     auth.err.textContent = '';
     auth.username.value = '';
     auth.password.value = '';
     auth.username.focus();
   }
-  function hideLoginModal() { auth.modal.classList.add('hidden'); }
+  function hideLoginModal() { closeDialog(auth.modal); }
 
   function showUserBadge(username, role) {
     currentUser = username || '';
@@ -993,12 +1109,26 @@
     auth.userRole.textContent = role;
     auth.userRole.className = 'badge ' + (role === 'admin' ? 'text-bg-info' : 'text-bg-secondary');
     auth.userAvatar.textContent = (username || '?').charAt(0).toUpperCase();
+    // "Mine only" has no meaning without a signed-in user.
+    const toggle = document.getElementById('mine-toggle');
+    if (toggle) toggle.classList.remove('d-none');
   }
 
   function hideUserBadge() {
     auth.userBadge.classList.add('d-none');
     auth.userBadge.classList.remove('d-flex');
     auth.logoutBtn.classList.add('d-none');
+    // Session expiry previously left currentUser set, so Mine only kept
+    // filtering by a user who was no longer signed in.
+    currentUser = '';
+    mineOnly = false;
+    const toggle = document.getElementById('mine-toggle');
+    if (toggle) {
+      toggle.classList.add('d-none');
+      toggle.setAttribute('aria-pressed', 'false');
+      toggle.className = 'btn btn-sm btn-outline-secondary d-none';
+    }
+    if (lastData) renderLanes(lastData);
   }
 
   async function login() {
@@ -1021,18 +1151,19 @@
         return;
       }
       const data = await resp.json();
-      if (data.token) {
+      // Success is signalled by ``ok``; the session token stays in the
+      // HttpOnly cookie and is never exposed to page JavaScript.
+      if (data.ok) {
         hideLoginModal();
         showUserBadge(data.username, data.role);
         currentProject = '';
-        fetchStatus().then(function () {
+        refreshAll().then(function () {
           if (pendingTaskModalId) {
             const retryId = pendingTaskModalId;
             pendingTaskModalId = '';
             openTaskModal(retryId);
           }
         });
-        fetchHours();
       } else if (data.note === 'auth disabled') {
         hideLoginModal();
         fetchStatus();
@@ -1068,12 +1199,18 @@
     } catch (e) { /* server unreachable: leave the board as is */ }
   })();
 
-  fetchStatus().then(function () {
-    fetchPlan();
-    fetchHours();
-    loadCFD();
-    loadControlChart();
-  });
+  // One refresh path for cold load and login. Previously login only fetched
+  // status and hours, leaving Plan, CFD and Control stuck at "unavailable"
+  // until the 60 s interval fired.
+  function refreshAll() {
+    return fetchStatus().then(function () {
+      fetchPlan();
+      fetchHours();
+      loadCFD();
+      loadControlChart();
+    });
+  }
+  refreshAll();
   setInterval(fetchStatus, 30000);
   setInterval(fetchPlan, 60000);
   setInterval(fetchHours, 60000);
diff --git a/tests/test_planner_409_regression.py b/tests/test_planner_409_regression.py
new file mode 100644
index 0000000..048a5a5
--- /dev/null
+++ b/tests/test_planner_409_regression.py
@@ -0,0 +1,219 @@
+# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
+"""Regression tests for the planner dashboard hardening (task 409).
+
+Covers the defects found by browser probing across all five registered
+projects: project-scoped plan writes, HTTP 500 on status failure, real
+finished-today counts, canonical milestone ids and declared-milestone seeding,
+UTC day anchoring, and trusted-proxy handling of forwarded protocol headers.
+
+All tests are offline: they build the Starlette app in-process with a temporary
+project directory and drive it with ``starlette.testclient.TestClient``. No
+network, no running daemon, no session process required.
+"""
+
+import importlib.util
+import os
+import sys
+from pathlib import Path
+
+import pytest
+from starlette.testclient import TestClient
+
+PLANNER_DIR = Path(__file__).parent.parent / "mcp-planner-server"
+sys.path.insert(0, str(PLANNER_DIR))
+
+
+@pytest.fixture(autouse=True)
+def _isolated_registry(tmp_path, monkeypatch):
+    """Keep auto-registration and auth config out of the real home dir."""
+    monkeypatch.setenv(
+        "PLANNER_PROJECTS_REGISTRY", str(tmp_path / "planner-projects.json")
+    )
+    monkeypatch.delenv("PLANNER_USERS_CONFIG", raising=False)
+    monkeypatch.delenv("PLANNER_PROJECT_ROOT", raising=False)
+    monkeypatch.delenv("PLANNER_TRUSTED_PROXIES", raising=False)
+
+
+_PLANNER_SPEC = importlib.util.spec_from_file_location(
+    "planner_server_409", PLANNER_DIR / "server.py"
+)
+planner = importlib.util.module_from_spec(_PLANNER_SPEC)
+_PLANNER_SPEC.loader.exec_module(planner)
+
+
+def _write_task(tmp_path, lane, task_id, title, **headers):
+    """Write a minimal parseable task file and return its path."""
+    lane_dir = tmp_path / "tasks" / lane
+    lane_dir.mkdir(parents=True, exist_ok=True)
+    path = lane_dir / f"{task_id}-{title.lower().replace(' ', '-')}.md"
+    lines = [
+        f"# Task {task_id}: {title}",
+        "",
+        f"**Status:** {headers.pop('status', 'open')}",
+    ]
+    for key, value in headers.items():
+        lines.append(f"**{key.replace('_', ' ').title()}:** {value}")
+    lines.extend(["", "## Goal", "", "Offline regression fixture.", ""])
+    path.write_text("\n".join(lines), encoding="utf-8")
+    return path
+
+
+def _make_project(tmp_path, name="proj"):
+    root = tmp_path / name
+    (root / "tasks" / "backlog").mkdir(parents=True, exist_ok=True)
+    return root
+
+
+def test_plan_save_missing_project_root_returns_400(tmp_path):
+    """POST /api/plan without project_root is rejected, not defaulted."""
+    root = _make_project(tmp_path)
+    with TestClient(planner.build_app()) as client:
+        resp = client.post("/api/plan", json={"approved": False})
+    assert resp.status_code == 400
+    assert "project_root" in resp.json()["error"]
+    assert not (root / "tasks" / ".plan").exists()
+
+
+def test_plan_save_unknown_project_root_returns_404(tmp_path):
+    """A non-existent absolute root is a 404, never a silent fallback."""
+    with TestClient(planner.build_app()) as client:
+        resp = client.post(
+            "/api/plan",
+            json={"project_root": str(tmp_path / "does-not-exist"), "approved": False},
+        )
+    assert resp.status_code == 404
+    assert resp.json()["error"] == "unknown project_root"
+
+
+def test_plan_save_writes_only_to_selected_project(tmp_path):
+    """The write lands under the requested root, not the daemon default."""
+    root_a = _make_project(tmp_path, "project-a")
+    root_b = _make_project(tmp_path, "project-b")
+    with TestClient(planner.build_app()) as client:
+        resp = client.post(
+            "/api/plan",
+            json={"project_root": str(root_a), "approved": False},
+        )
+    assert resp.status_code == 200
+    week = resp.json()["week"]
+    assert (planner._plan_file(root_a, week)).is_file()
+    assert not (planner._plan_file(root_b, week)).exists()
+
+
+def test_api_status_internal_error_returns_500(tmp_path, monkeypatch):
+    """An internal failure keeps a danger signal instead of HTTP 200."""
+    root = _make_project(tmp_path)
+    monkeypatch.setattr(
+        planner,
+        "_load_all_tasks",
+        lambda _root: (_ for _ in ()).throw(RuntimeError("boom")),
+    )
+    with TestClient(planner.build_app(), raise_server_exceptions=False) as client:
+        resp = client.get("/api/status", params={"project_root": str(root)})
+    assert resp.status_code == 500
+    assert resp.json()["error"] == "internal error"
+
+
+def test_today_done_counts_real_finished_tasks(tmp_path):
+    """A project with zero finished tasks no longer claims target completions."""
+    empty = _make_project(tmp_path, "empty")
+    empty_payload = planner._api_status(str(empty))
+    assert empty_payload["today"]["done"] == 0
+    assert empty_payload["today"]["quota_reached"] is True
+
+    worked = _make_project(tmp_path, "worked")
+    _write_task(
+        worked,
+        "completed",
+        "001",
+        "Finished today",
+        status="closed",
+        finished=planner._utc_today().isoformat() + "T07:00:00Z",
+    )
+    payload = planner._api_status(str(worked))
+    assert payload["today"]["done"] == 1
+
+
+def test_normalize_milestone_unifies_leading_zeros_and_case():
+    """M1, m01 and M001 are one canonical milestone key."""
+    assert planner._normalize_milestone("M1") == "M01"
+    assert planner._normalize_milestone("m01") == "M01"
+    assert planner._normalize_milestone(" M003 ") == "M03"
+    assert planner._normalize_milestone("") == ""
+
+
+def test_declared_milestone_seeds_board(tmp_path):
+    """A milestone document is visible even with zero tagged tasks."""
+    root = _make_project(tmp_path)
+    milestone_dir = root / "tasks" / "milestones"
+    milestone_dir.mkdir(parents=True, exist_ok=True)
+    (milestone_dir / "M02-board-hardening.md").write_text(
+        "# Milestone M02 — Board hardening\n", encoding="utf-8"
+    )
+    assert planner._milestone_definitions(root)["M02"].startswith("Milestone M02")
+    payload = planner._api_status(str(root))
+    assert "M02" in payload["milestone_tree"]
+    assert payload["milestone_tree"]["M02"][0]["status"] == "declared"
+
+
+def test_utc_today_is_timezone_aware_source():
+    """Day anchoring uses UTC, not the host local date."""
+    from datetime import datetime, timezone
+
+    assert planner._utc_today() == datetime.now(timezone.utc).date()
+
+
+def test_forwarded_proto_ignored_from_untrusted_peer():
+    """A spoofed X-Forwarded-Proto from a non-proxy cannot force Secure."""
+
+    class Peer:
+        def __init__(self, host):
+            self.host = host
+
+    class FakeRequest:
+        def __init__(self, host, proto):
+            self.client = Peer(host)
+            self.headers = {"x-forwarded-proto": proto}
+            self.url = type("URL", (), {"scheme": "http"})()
+
+    assert planner._is_https(FakeRequest("203.0.113.9", "https")) is False
+    assert planner._is_https(FakeRequest("127.0.0.1", "https")) is True
+
+
+def test_project_tool_positional_does_not_register_bogus(tmp_path):
+    """A positional goal is not mistaken for a project root (B4)."""
+    root = _make_project(tmp_path, "posproj")
+    planner.plan_propose("Build a feature X", project_root=str(root))
+    registered = planner._read_projects_registry()
+    assert "Build a feature X" not in registered
+    assert str(root.resolve()) in registered
+
+
+def test_month_proration_partial_week(tmp_path):
+    """Partial ISO weeks in a month view get less than full capacity (B6)."""
+    root = _make_project(tmp_path, "monthproj")
+    payload = planner._plan_payload(str(root), "month")
+    weeks = payload.get("weeks") or []
+    assert weeks
+    # At least one partial week at the month edge must be prorated below 20 h.
+    assert any(week["capacity_hours"] < 20 for week in weeks)
+
+
+def test_loopback_rejects_non_loopback_peers():
+    """Only loopback IPs and known in-process labels are trusted (B9)."""
+    assert planner._is_loopback_peer("127.0.0.1") is True
+    assert planner._is_loopback_peer("::1") is True
+    assert planner._is_loopback_peer("testclient") is True
+    assert planner._is_loopback_peer("unix") is True
+    assert planner._is_loopback_peer("203.0.113.9") is False
+    assert planner._is_loopback_peer("evil.example") is False
+
+
+def test_plan_delete_missing_project_root_returns_400(tmp_path):
+    """DELETE /api/plan without project_root cannot clear the default project."""
+    from starlette.testclient import TestClient as TC
+
+    with TC(planner.build_app()) as client:
+        resp = client.delete("/api/plan", params={"week": "2026-W47"})
+    assert resp.status_code == 400
+    assert "project_root" in resp.json()["error"]
diff --git a/tests/test_planner_server.py b/tests/test_planner_server.py
index 180738e..347e34d 100644
--- a/tests/test_planner_server.py
+++ b/tests/test_planner_server.py
@@ -529,8 +529,9 @@ def test_api_status_milestone_tree_and_deadlines(tmp_path):
     )
     payload = planner._api_status(str(tmp_path))
 
-    assert list(payload["milestone_tree"]) == ["M1"]
-    assert payload["milestone_tree"]["M1"][0]["title"] == "Milestone task"
+    # ADR-015: M1 is canonicalised to M01 so M1/m01/M001 merge on the board.
+    assert list(payload["milestone_tree"]) == ["M01"]
+    assert payload["milestone_tree"]["M01"][0]["title"] == "Milestone task"
     assert payload["deadlines"][0]["deadline"] == "2026-12-01"
 
 
@@ -540,7 +541,9 @@ def test_api_status_pacing_mirrors_quota(tmp_path):
     today = payload["today"]
 
     assert today["open"] == 1
-    assert today["done"] == today["target"] - 1
+    # ADR-015: done is the real finished-today count, not target minus open.
+    assert today["done"] == 0
+    assert today["quota_reached"] is False
     # Matches sprint_check_daily_quota: open work means quota not reached.
     assert "DAILY_QUOTA_REACHED" not in planner.sprint_check_daily_quota(str(tmp_path))
 
@@ -617,7 +620,7 @@ def test_milestone_tree_sorts_numerically(tmp_path):
         tmp_path, "backlog", "283-old.md", "Old task", Milestone="M1"
     )
     payload = planner._api_status(str(tmp_path))
-    ids = [b["id"] for b in payload["milestone_tree"]["M1"]]
+    ids = [b["id"] for b in payload["milestone_tree"]["M01"]]
     assert ids == ["283", "0356"], ids
 
 
@@ -1249,13 +1252,20 @@ def test_plan_api_admin_only_and_persists(open_client, tmp_path, monkeypatch):
     _write_task(tmp_path, "backlog", 53, "Saved", estimate=1)
     week_dt = __import__("datetime").date.today().isocalendar()
     week = f"{week_dt[0]}-W{week_dt[1]:02d}"
+    # ADR-015: a save must name the project it writes to.
     resp = open_client.post(
         "/api/plan",
-        json={"week": week, "deadline_edits": {"053": "2026-10-26"}},
+        json={
+            "project_root": str(tmp_path),
+            "week": week,
+            "deadline_edits": {"053": "2026-10-26"},
+        },
     )
     assert resp.status_code == 200
     assert resp.json()["deadline_edits"]["053"] == "2026-10-26"
-    status = open_client.get("/api/plan", params={"window": "week"}).json()
+    status = open_client.get(
+        "/api/plan", params={"window": "week", "project_root": str(tmp_path)}
+    ).json()
     assert status["plan"]["week"] == week
 
 
@@ -1371,7 +1381,10 @@ def test_login_valid_credentials_returns_token(auth_client):
     )
     assert resp.status_code == 200
     data = resp.json()
-    assert data["token"]
+    # ADR-015: the token lives only in the HttpOnly cookie, not the body.
+    assert data["ok"] is True
+    assert "token" not in data
+    assert resp.cookies.get("planner_session")
     assert data["username"] == "admin"
     assert data["role"] == "admin"
     assert data["allowed_projects"] == ["*"]
```
<!-- END_GIT_DIFF -->
