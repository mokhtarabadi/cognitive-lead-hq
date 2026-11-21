# Task 409: Planner MCP dashboard hardening across all projects

**File:** `tasks/completed/409-planner-dashboard-hardening.md`
**Source:** manager
**Type:** bug
**Status:** closed
**Finished:** 2026-11-21T08:39:28Z
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
- [x] QA and Code Reviewer verdicts recorded with no unresolved finding (QA round 2 QA_PASSED, Code Reviewer APPROVED / PO_REVIEW_PENDING)

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

**QA round 1:** `VERDICT: QA_REJECTED` on six reproducing findings F1-F6 (fail-open loopback peer check, incomplete project-switch refresh, stale panels in `clearBoard`, lane badge using filtered count, zero-capacity bar forced to 100%, and missing regression cover). All six were fixed in the same task; none were disputed. Fresh evidence: 13 regression tests pass, planner slice 174 passed, live redeploy HTTP 200.

**QA round 2:** `VERDICT: QA_PASSED`. All six findings resolved in code with no new defect. Cited `server.py:1925`, `index.html:1070,289,488,989`, `test_planner_409_regression.py:180`.

**Code Reviewer:** `Verdict: APPROVED`, `Status: PO_REVIEW_PENDING`. Contract consistency, docs, tests, ZAC and scope all clean. Non-blocking notes N1 (declared milestone shows 0/1), N2 (month capacity proration), N3 (peer allowlist includes test labels). Relay: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish."

**Manager acceptance (question-tool answer, verbatim):** "Approved for closure". Recorded before any closure action. Lane verified `tasks/qa/` and the log still recorded `PO_REVIEW_PENDING` at the time of acceptance.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `d9669bf88911a7d259ac08c7ae0e0192ce8d00e9`
<!-- END_GIT_DIFF -->
