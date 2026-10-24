# Task 335: Planner MCP v1 — local planning layer over task Markdown

**File:** `tasks/completed/0335-planner-mcp-v1.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Source Context

### Variant C: Manager (`**Source:** manager`)

## Goal

Build a thin Planner MCP server plus a standalone local dashboard that reads `tasks/` Markdown as the single source of truth, enforces capacity/QA/dependency queue gates, and lets the Manager hold a conversational planning loop ("next month we ship 4 features and 4 releases") without external integrations.

## Manager's Notes

- Approved direction: O1 v1 from the team brainstorming session (see `docs/planner-mcp-plan.md`).
- Keep `tasks/` Markdown canonical; the planner is a derived index, not a competing task store.
- Autopilot QA budget: max 1 unresolved QA/review task (general WIP ceiling stays 3).
- v1 is additive only — no migration of existing tasks, no external integrations (GitHub/Telegram/Asana/Plane deferred to v2/v3).
- Default weekly capacity 20 h, batch size 3 per autopilot cycle (to confirm by Manager).

## Local TODOs

- [x] Specify additive task/milestone metadata fields, capacity inputs, queue-gate rules (no migration of existing tasks)
- [x] Scaffold `mcp-planner-server/` (`pyproject.toml`, `uv.lock`, `server.py`), singleton on port 8108
- [x] Implement read model from existing Markdown tasks (`tasks/.plan/index.json`, gitignored, regenerated per turn)
- [x] Implement `plan_propose` (decompose goal into tasks + estimates, writes nothing)
- [x] Implement `plan_materialize` (writes task files only after Manager approval)
- [x] Implement `claim_next` (guarded claim: checks dependencies, WIP, QA budget)
- [x] Implement `qa_budget` and `milestone_status`
- [x] Offline unit tests: guarded transitions, dependency cycles, capacity math, stale-data handling
- [x] Standalone local dashboard on 8108: Kanban lanes, QA queue bar, capacity meter, milestone timeline, blocker list
- [x] `lint_task_file` green; full suite green (except pre-existing `test_system_prompt_split_assemble_round_trip`)
- [ ] Smoke test: `opencode mcp list` all servers connected; dashboard reachable — dashboard reachable is verified; `opencode mcp list` needs the Manager to register the remote entry in the global `opencode.json` first

## Acceptance Criteria

- [x] `mcp-planner-server/` exists as a singleton MCP server on loopback port 8108 with `pyproject.toml` + `uv.lock`
- [x] `plan_status` reports Kanban lanes, QA queue, capacity vs. estimate, milestones, blocker list from Markdown tasks
- [x] `plan_propose` decomposes a goal into task estimates without writing any task file
- [x] `claim_next` refuses when dependencies are unresolved, WIP full, or QA budget would be exceeded
- [x] `plan_materialize` writes new task files only after Manager approval; `lint_task_file` passes on each
- [x] Billing/quota-style terminal failures are hinted, not retried (mirrors brain-bridge F6/F7 patterns)
- [x] Autopilot cycle capped at 1 unresolved QA/review task + batch of 3
- [x] Full test suite passes (592 passed / 1 pre-existing failure)

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest --with pyyaml python -m pytest tests/ -q`
- **Expected result:** full suite green except pre-existing `test_system_prompt_split_assemble_round_trip` (proven on HEAD); new planner tests pass
- **Actual result:** `592 passed, 1 failed` — the only failure is `tests/test_mcp_servers.py::test_system_prompt_split_assemble_round_trip`, the documented pre-existing prompt split/assemble drift. `git status --short -- prompts/ system-prompt.md` is clean, and that test only round-trips the prompt pipeline, so this task cannot have caused it. Planner suite alone: `31 passed`.
- **Exit code:** 0 (the RTK runner reports FAILURES for the known pre-existing failure; pytest exit for `tests/test_planner_server.py` alone is 0)
- **Live smoke (dashboard + MCP):** `127.0.0.1:8108` LISTEN (loopback only); `GET /` -> 200 (15,622 bytes); `GET /api/status` -> 200 resolving the repo root with 328 tasks; `POST /mcp` `initialize` -> 200 with a session id, and `tools/list` enumerates all 10 tools (`plan_propose`, `plan_materialize`, `claim_next`, `plan_status`, `sprint_stats`, `qa_budget`, `milestone_status`, `sprint_lock`, `sprint_daily_agenda`, `sprint_check_daily_quota`).
- **Dashboard render:** `render()` exercised headlessly against the live payload (5 lane cards, 21 timeline cells, pacing 2/3) and against a synthetic milestone/deadline payload (2 milestone nodes), both exit 0.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Planner becomes a second divergent status source; overcommitment persists if gates are bypassable; direct repo edits bypass planner.
- **Rollback plan:** Task files remain readable Markdown; planner is a derived index only — disable the server and return to existing Kanban workflow. No destructive migration.

---

## Execution Log & Reasoning

### What this task is

Implementation of the Planner MCP v1 (O1) approved by the Manager following the team brainstorming session (full seven-seat report retained in `docs/planner-mcp-plan.md`). No code written yet; this task file is the specification and starting point.

### Assumptions

- **A1** — Weekly capacity default 20 h; to be confirmed by Manager before Phase B.
- **A2** — Batch size default 3 tasks per autopilot cycle; to be confirmed by Manager before Phase B.
- **A3** — No task-number prose in prompt-facing files per `docs/conventions.md`; task numbers live only in headers, code comments, CHANGELOG, and this task file.

### Decisions recorded

- **D1** — `tasks/` Markdown canonical; planner is derived index (`tasks/.plan/index.json`, gitignored).
- **D2** — v1 = Planner MCP + local dashboard; external integrations deferred.
- **D3** — Autopilot QA budget: max 1 unresolved QA/review task; general WIP ceiling stays 3.
- **D4** — Only planner tooling may change task state; every transition passes `lint_task_file`.

## Execution Progress

- [x] Step 1: Move task to `tasks/in-progress/` and sync `**File:**` header
- [x] Step 2: Scaffold `mcp-planner-server/` (`pyproject.toml`, `uv.lock`, `README.md`, `DECISIONS.md`)
- [x] Step 3: Implement `mcp-planner-server/server.py` (planning tools + static dashboard route)
- [x] Step 4: Implement `mcp-planner-server/static/index.html` (dark-mode dashboard)
- [x] Step 5: Create `tasks/sprints/`, `tasks/milestones/`, `services/mcp-planner.service`
- [x] Step 6: Offline test suite `tests/test_planner_server.py`
- [x] Step 7: Update docs (`docs/services.md`, `services/README.md`, `CHANGELOG.md`)
- [x] Step 8: Run test suite + task linter; record evidence; QA transition

### Implementation pass 2 — verification findings and fixes (2026-10-24)

Steps 1–6 existed on entry. Running the deliverable rather than trusting the
checklist surfaced five defects that the first pass could not have caught,
because it only ever called the tool functions directly:

- **F1 — the HTTP server did not start at all.** `build_app()` called
  `mcp.http_app()`, which does not exist in the installed `mcp` 1.30 SDK
  (`AttributeError`). Switched to `mcp.streamable_http_app()` and mounted it at
the root: the transport app already routes itself at
  `settings.streamable_http_path` (`/mcp`), so mounting at `/mcp` would have
  double-prefixed the endpoint.
- **F2 — the mounted app's lifespan never ran.** Starlette runs only the parent
  app's lifespan, so the session manager's task group stayed uninitialised and
  every `/mcp` request returned 500 `RuntimeError: Task group is not
  initialized`. Added an explicit
  `async with mcp_app.router.lifespan_context(mcp_app)` in the parent lifespan.
- **F3 — the dashboard crashed on every load.** `/api/status` returned a scalar
  count per lane while `render()` calls `items.map(...)`; the resulting
  `TypeError` was swallowed by the fetch `catch`, so the board blanked and the
  UI reported "Server unreachable". The payload now ships task lists per lane
  plus `milestone_tree`, `deadlines`, `today`, and `projects`.
- **F4 — the dashboard was pinned to the wrong root.** `/api/status` used
  `Path.cwd()`, which under the systemd unit is the install directory, so the
  board would always be empty. Root resolution is now `project_root` query
  parameter → `PLANNER_PROJECT_ROOT` → nearest ancestor holding `tasks/` → cwd,
  and the project switcher is wired through the same parameter instead of being
  a no-op placeholder.
- **F5 — `plan_materialize` produced lint-failing files.** The generated
  template omitted the backticks the linter requires around `**File:**`, had no
  `## Verification Evidence` section, and fabricated
  `**Estimate:** TBD` / `**Deadline:** TBD` / `**Milestone:** M1`, which polluted
  the derived read model. Materialized files now pass the real
  `_check_task_file_structure` and `_check_markdown_basics` validators, proven by
  a test rather than asserted in a docstring.

Two further defects were in the test suite itself:

- **F6 — the parser test asserted against a broken fixture.** `_write_task`
  emitted the AC and TODO blocks twice (once inline after `**Status:**`, once in
  the body), so `_parse_task_file` correctly returned 4 criteria where the test
  expected 2. The fixture was fixed; the parser is unchanged, since faithfully
  reporting duplicate sections is the correct behaviour.
- **F7 — the planner tests passed alone but failed in the full suite.**
  `import server as planner` collided with the other test modules that do
  `import server` for their own MCP server: `sys.modules["server"]` caches
  whichever loads first, so the planner tests ran against the brain bridge and
  failed with `AttributeError: module 'server' has no attribute
  '_parse_task_file'`. Now loaded via `spec_from_file_location("planner_server",
  ...)`, following the existing convention in `tests/test_mcp_servers.py`.

### Assumptions

- **A4** — The additive `sprint_*` tool surface (`sprint_lock`,
  `sprint_daily_agenda`, `sprint_check_daily_quota`, `sprint_stats`) and the
  approved `plan_*` surface are both kept. They are complementary, not
  redundant: `plan_*` covers proposal/materialisation and `sprint_*` covers the
  locked-sprint and daily-quota view. Removing either would drop functionality
  the task file or its AC list requires.
- **A5** — Weekly capacity defaults to 20 h and batch size to 3, per A1/A2, now
  overridable via `PLANNER_WEEKLY_CAPACITY` and `PLANNER_DAILY_TARGET` rather
  than hard-coded.
- **A6** — "Today's done" is derived rather than stored: `target - open`, where
  `open` is the in-progress plus QA set. The read model has no completion-date
  field, and inventing one would have been a migration, which v1 explicitly
  excludes.
- **A7** — `plan_materialize` leaves `**Estimate:**` / `**Deadline:**` /
  `**Milestone:**` / `**Depends on:**` out entirely. Only the Manager knows
  those values, and a placeholder would corrupt the read model.
- **A8** — Registering the remote entry in the global `opencode.json` is left to
  the Manager: that file lives outside this repository, so `opencode mcp list`
  cannot show the planner until they add it.

### Closure authorization

- The Orchestrator's closure block arrived with no QA verdict in this file and
  none of the required approval literals, so the Hands halted instead of
  moving/committing (gatekeeper protocol).
- The Manager was asked through the approval gate and selected **"Approved for
  closure — close now"**, explicitly accepting closure **without a QA verdict**.
  That decision is recorded here as the authorization for closure.
- QA is therefore waived for this task by Manager decision, not skipped by
  oversight. The adversarial pass the previous hand-off requested did not run.
- Status is `closed` (not `completed`) to match every existing file in
  `tasks/completed/` and the `AGENTS.md` closure rule.

### Verification notes

- Full suite `592 passed, 1 failed`; the single failure is the pre-existing
  `test_system_prompt_split_assemble_round_trip`. `prompts/` and
  `system-prompt.md` are untouched by this task (`git status` clean for both).
- Tool registration was proven over the real MCP wire (`initialize` then
  `tools/list`), not by inspecting the module: all 10 tools enumerate.
- The dashboard was proven by running `render()` against the live payload and a
  synthetic milestone/deadline payload, because a build step or a syntax check
  alone would not have caught F3.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `0fa79f0cb54441e0444d3b6021ac999f73c776a4`
<!-- END_GIT_DIFF -->
