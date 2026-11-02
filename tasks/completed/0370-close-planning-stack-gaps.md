# Task 0370: Close planning-stack gaps

**File:** `tasks/qa/0370-close-planning-stack-gaps.md`
**Source:** manager
**Type:** improvement
**Status:** in-progress
**Submitted:** 2026-11-02T18:51:17Z
**Started:** 2026-11-02T18:36:11Z

## Goal

Fix the planning-stack audit gaps in code, tools, and docs so behavior matches the documented contracts.

## Manager's Notes

Manager decisions (binding): sprint scope is the calendar week Monday to Sunday, stats filter by Started/Finished stamps; precedence is Strategist capacity veto stands unless the Manager explicitly overrides. Scope: F1 milestone writer, F2 case-insensitive grouping, F5 lock enforcement, F6 week-scoped stats plus date-aware quota, F7 docs refresh, F4 QA-cap reconciliation, F9 precedence rule in prompts, F10 DoD reconciliation. Converting the 369 xfail tripwires (T2, T5, T6) to must-pass guards is part of done. Prompt fragment edits require the regenerate workflow with version bump and pin update.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Brain planning turn for the fix design
- [x] Implement server plus lint plus docs changes
- [x] Convert 369 xfails to must-pass and keep suite green
- [x] Verify functionality

## Acceptance Criteria

- [x] `schedule_tasks` writes `**Milestone:**` and the 369 T1 guard still passes
- [x] Milestone grouping is case-insensitive and T2 passes without xfail
- [x] `claim_next` refuses work while a sprint lock file exists and T5 passes without xfail
- [x] `sprint_stats` filters by calendar week and quota reports today-aware numbers, T6 passes without xfail
- [x] Guide plus policies docs refreshed (correct citations, live Missing labels, milestone/sprint flow, reconciled caps and DoD)
- [x] Precedence rule written in prompts with rebuilt prompt in sync
- [x] Full suite green with zero xfail-strict leftovers from 369

## Verification Evidence

- **Test command:** rtk test uv run --with pytest --with "mcp<2" --with pathspec --with pyyaml pytest tests/ -q (RTK wrapper cannot spawn in this shell — os error 2; ran the documented raw fallback)
- **Expected result:** all green, 369 xfails converted, exit code 0
- **Actual result:** 766 passed, 0 failed; contracts file 11 passed with zero xfail leftovers; ruff format clean on all touched Python files
- **Exit code:** 0

> Verification runner rule: the exact command above is complete. The first run MUST use the `rtk test` prefix; a raw rerun is allowed only after a failed RTK run. RTK is known-broken in this shell (os error 2) — record the fallback if used.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Medium. Touching claim gates and grouping output can break existing planner tests and the board; run the full suite before claiming done.
- **Rollback plan:** Revert server plus docs commits via git; gaps return to the documented 369-tripwire state.

---

## Execution Log & Reasoning

Autopilot locked for QA plus review (Manager order "Lock auto pilot mode").

QA verdict (autopilot, same session): QA_PASSED with two residual notes V1 (malformed week handling) and V2 (milestone newline at writer level) — both verified and closed by the Hands before review (clean blocked string, no-write rejection with new T1c test, 160-test gate green, format clean).

Review verdict (autopilot, same session): technically approved, PO_REVIEW_PENDING — writer backwards compatible, grouping converges, lock fails closed, week scope with byte-identical snapshot lines, tripwires converted, prompt rebuilt in sync. R1/R2 confirmed by the Hands (CHANGELOG entry at line 47, staged names owned-only). No blocking issues. Closure awaits the Manager's explicit approval word.

Supersedes the audit tripwire state: task 369 pinned behavior plus documented gaps; this task fixes F1, F2, F4-F7, F9, F10 under the Manager's week-scope and precedence decisions. Unlock path for sprint locks: deleting the lock file (Manager-owned). Quota design detail (today-finished counting) goes to the Brain plan.

Implementation notes: milestone as trailing optional `:milestone` segment (backwards compatible, `-` untouched; writer order Estimate, Deadline, Depends on, Milestone); grouping casefold with first-seen display; claim lock gate first with unlock-by-delete message plus docstring corrections; sprint_stats optional week param plus week lines (existing snapshot lines byte-identical) plus quota Finished-today line; lint Milestone non-empty single-line; 369 T2/T5/T6 converted with strengthened asserts plus new T1b writer test (11 passed, zero xfail); precedence sentence in 06-personas plus executor roster; PATCH 9.70.2 rebuilt (111362 bytes) with pin update; docs confined to flagged lines. Adaptations to the plan XML: task already in-progress (no backlog move); ruff format is the enforced gate (ruff check shows pre-existing repo-wide patterns only). Deviation logged: slice ADR appended via shell heredoc instead of the native write tool — content verified by readback plus markdown lint; will not repeat. Stack skip: plain Python plus pytest, no framework marker — no stack skill matched, none invented.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 1faba23..77e50e3 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -44,6 +44,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Planning contracts consolidated test (Task 369):** one new `tests/test_planning_contracts.py` pinning the planning-stack audit — 7 must-pass guards (milestone preservation, deadline rejection, no-crash, QA ceiling, retrospective sync, status fields, lock-file behavior) plus 3 xfail-strict gap markers (case-split grouping, unenforced lock, unscoped stats). Zero source edits; planner gates 170 passed.
 
+- **Planning-stack gaps closed (Task 370):** `schedule_tasks` writes `**Milestone:**` via trailing segment (lint enforces non-empty single-line); grouping casefolded with first-seen display; `claim_next` blocked by sprint lock files (delete to unlock); `sprint_stats` week-scoped Mon-Sun with today-finished quota line; docs refreshed (live citations, milestone/sprint flow, QA cap 1-vs-3 reconciled, single DoD); precedence rule in prompts with rebuild `9.70.1` → `9.70.2`. The 369 tripwires convert to must-pass (11 passed, zero xfail). Full suite 766 green.
+
 ### Fixed
 
 - **Brain results are returned whole from Code Mode (Task 0354):** the executor's Code-mode output discipline told the Hands to return `{status, block_count: xml_blocks.length, model}`, a recipe meant to stop it printing a truncated prefix of a large XML block. The recipe instead licensed dropping the payload — turns returning only `output` lost `xml_blocks`, turns returning only `blocks` lost `output` — so the transcript and the agent's next turn held less than the server returned even though the executed instructions were complete. The rule now says a `brain_turn` result is evidence, not a preview: return `status`, `output`, `xml_blocks` and any diagnostic/`truncated` field exactly as received, never slice, map, summarize or field-shape it, and manage size before the call with `compact_context`, a leaner prompt or `include_bundle=false`. The runtime's `maxOutputBytes` remains the only acceptable cut and announces itself with `truncated: true`. Locked by a prompt-sync test that fails if the rule disappears or `block_count` returns; the live agent copy is byte-identical to the repo.
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index a2ed1fa..4f49584 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -230,7 +230,7 @@ When a circuit breaker fires, output a `⚠️ CIRCUIT BREAKER` warning with the
 
 - **Starting the day.** When the Manager says "start today's work" — in whatever language the request arrives — call `sprint_daily_agenda(project_root)` before touching any task file. It lists what is already in progress plus any QA-pending task that has to be resolved first.
 - **Taking a task.** Call `claim_next(project_root, task_id)` instead of hand-moving the file. It performs the backlog to in-progress transition only when dependencies are satisfied, the WIP ceiling allows it, and the QA budget is not spent. A block is an answer, not an obstacle: report the stated reason to the Manager and never bypass it by moving the file manually.
-- **Recording a plan.** Once the Manager approves a plan, call `schedule_tasks(project_root, "id:estimate:deadline[:deps], …")` so estimate, deadline and dependencies are written into the task headers. Never hand-edit `**Estimate:**`, `**Deadline:**` or `**Depends on:**` — the Planner reads them from the Markdown and a malformed line drops the task out of capacity and the timeline without any error.
+- **Recording a plan.** Once the Manager approves a plan, call `schedule_tasks(project_root, "id:estimate:deadline[:deps[:milestone]], …")` so estimate, deadline, dependencies and milestone are written into the task headers. Never hand-edit `**Estimate:**`, `**Deadline:**`, `**Depends on:**` or `**Milestone:**` — the Planner reads them from the Markdown and a malformed line drops the task out of capacity and the timeline without any error.
 - **Measured time is automatic.** `**Started:**`, `**Submitted:**` and `**Finished:**` are written by the lane transitions themselves (`claim_next`, `qa_transition`, `commit_and_clean_task`) as ISO-8601 UTC, write-once. Never write or change them by hand: a local-time or free-text value is rejected by the lint, and a rewritten start falsifies the duration the panel reports. If you move a task file yourself (a permitted `git mv`), call `sync_task_times(project_root)` right after the move — it stamps the missing start/submit time from git history and is idempotent.
 - **Ending the day.** Once tasks are closed, call `sprint_check_daily_quota(project_root)`. When it returns `DAILY_QUOTA_REACHED`, present `sprint_stats(project_root)` and announce that the day's work is finished; do not claim another task in that turn.
 - **Status questions.** `plan_status(project_root)` covers lanes, capacity against estimate, milestones, and blockers. `qa_budget(project_root)` answers whether another review can be opened without breaching the one-unresolved-review ceiling.
@@ -572,7 +572,7 @@ The roster table below is the only roster.
 | UI/UX Designer     | Frontend features, layout, components, styling                | Design systems, user journeys, a11y, responsive, local `DESIGN.md`                                                                                                                                                  |
 | Senior Programmer  | Approved blueprints/designs, explicit Manager request         | Implementation lead, "Hands Whisperer", writes `<hands_implementation_task>` XML                                                                                                                                    |
 | Project Planner    | Status checks, milestone planning, explicit Manager request   | Kanban file state + milestones; never backlog priority                                                                                                                                                              |
-| Sprint Strategist  | Sprint planning, backlog prioritization, sprint overfill      | Capacity, MoSCoW, WIP ≤ 3; owns priority and sprint scope                                                                                                                                                           |
+| Sprint Strategist  | Sprint planning, backlog prioritization, sprint overfill      | Capacity, MoSCoW, WIP ≤ 3; owns priority and sprint scope; veto stands unless Manager explicitly overrides                                                                                                          |
 | QA Engineer        | Implementation complete, explicit test request                | Adversarial testing; verdict `QA_PASSED` / `QA_REJECTED`                                                                                                                                                            |
 | Code Reviewer      | Task summary pasted, PR submitted, review requested           | Audit vs blueprint; verdict `APPROVED` / `APPROVED_WITH_CHANGES` / `REJECTED_NEEDS_FIXES`; technical approval → `PO_REVIEW_PENDING` + notice, closure only via relayed Programmer XML after the exact approval word |
 
diff --git a/docs/kanban-board-manager-guide.md b/docs/kanban-board-manager-guide.md
index 1284baf..feaf821 100644
--- a/docs/kanban-board-manager-guide.md
+++ b/docs/kanban-board-manager-guide.md
@@ -16,20 +16,20 @@ This guide onboards board managers to the HQ Kanban/planning system and maps can
 ## Current system map
 
 - Planner MCP: derived index over `tasks/` Markdown; task files remain the source of truth.
-- Dashboard: board lanes, task modal, 14-day load view, and measured-hours view. See `mcp-planner-server/static/index.html:215-216` (chart containers), `:674-690` (14-day load chart), `:703-732` (measured-hours chart).
-- Task files: Kanban state, metadata, acceptance criteria, verification evidence, execution log, and factual diff. See `mcp-planner-server/server.py:187` (`_parse_task_file`).
-- AGENTS protocol: validation, task lifecycle, WIP expectations, QA/review gates, and closure rules. See `mcp-planner-server/server.py:887-891` (WIP ceiling check), `:878-883` (QA budget check).
+- Dashboard: board lanes, task modal, 14-day load view, and measured-hours view. See `mcp-planner-server/static/index.html:221-222` (chart element refs), `:718` (14-day load label), `:767-850` (CFD/control-chart fetch with unavailable-fallback).
+- Task files: Kanban state, metadata, acceptance criteria, verification evidence, execution log, and factual diff. See `mcp-planner-server/server.py:294` (`_parse_task_file`).
+- AGENTS protocol: validation, task lifecycle, WIP expectations, QA/review gates, and closure rules. See `mcp-planner-server/server.py:1014` (QA budget check), `:1024` (WIP ceiling check).
 
 ## Gap audit
 
-| Canonical essential | Current implementation | Gap | Evidence |
-|---|---|---|---|
-| Visualize workflow | Backlog, in-progress, QA, completed, and archive lanes | Partial: lane visualization exists, but flow history is limited | `mcp-planner-server/static/index.html:215-216` |
-| Limit WIP | WIP expectations and QA queue cap are documented | Partial: global default and per-project override need explicit policy and dashboard visibility | `mcp-planner-server/server.py:887-891` |
-| Manage flow | Measured-hours and 14-day load views exist | Missing: CFD, control chart/cycle-time scatterplot, and WIP aging | `mcp-planner-server/static/index.html:674-732` |
-| Explicit policies | AGENTS and task templates encode lifecycle rules | Partial: board-level policies are not centralized | This guide and `docs/kanban-policies.md` |
-| Feedback loops | QA and review gates exist | Missing: retrospective artifact and board-manager onboarding | This guide and `docs/retrospectives/TEMPLATE.md` |
-| Evolve collaboratively | Task execution logs and changelog exist | Partial: no standardized retrospective artifact | `docs/retrospectives/TEMPLATE.md` |
+| Canonical essential    | Current implementation                                 | Gap                                                                                                                  | Evidence                                                 |
+| ---------------------- | ------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
+| Visualize workflow     | Backlog, in-progress, QA, completed, and archive lanes | Partial: lane visualization exists, but flow history is limited                                                      | `mcp-planner-server/static/index.html:221-222`           |
+| Limit WIP              | WIP expectations and QA queue cap are documented       | Partial: global default and per-project override need explicit policy and dashboard visibility                       | `mcp-planner-server/server.py:1024`                      |
+| Manage flow            | Measured-hours and 14-day load views exist             | Partial: CFD/control-chart elements plus fetch wiring with unavailable-fallback exist; verify backend endpoints live | `mcp-planner-server/static/index.html:221-222, :767-850` |
+| Explicit policies      | AGENTS and task templates encode lifecycle rules       | Partial: board-level policies are not centralized                                                                    | This guide and `docs/kanban-policies.md`                 |
+| Feedback loops         | QA and review gates exist                              | Present: retrospective template plus this guide as onboarding                                                        | This guide and `docs/retrospectives/TEMPLATE.md`         |
+| Evolve collaboratively | Task execution logs and changelog exist                | Present: standardized retrospective template; approved actions become backlog tasks                                  | `docs/retrospectives/TEMPLATE.md`                        |
 
 ## Metrics
 
@@ -51,6 +51,10 @@ Prefer flow metrics over utilization metrics. High utilization is not a substitu
 - Review: compare completed work against Definition of Done and flow metrics.
 - Retrospective: use `docs/retrospectives/TEMPLATE.md` and convert approved actions into backlog tasks.
 
+## Milestone and sprint flow
+
+Schedule with milestone via `schedule_tasks(project_root, "id:estimate:deadline[:deps[:milestone]], …")` — the single writer for all four header lines, where `-` leaves a value untouched. Claim via `claim_next`, which is blocked while any `tasks/.plan/sprint-*.lock` file exists (delete the file to unlock). Review the week via `sprint_stats` (Monday–Sunday UTC scope, optional `week="YYYY-Www"`) and `sprint_check_daily_quota` (includes the Finished-today count). Group status via `milestone_status` (case-insensitive grouping, first-seen spelling on display).
+
 ## Blocked items and swarming
 
 Blocked items are first-class board state, not background noise.
@@ -77,11 +81,12 @@ Dashboard and planner integration for these fields is planned for the next imple
 
 A task is not done unless:
 
-- Required tests pass.
-- `lint_task_file` passes.
+- Build, test, and lint pass with exit code 0.
+- `lint_task_file` passes on the active task file.
 - Verification evidence is recorded.
 - `CHANGELOG.md` is updated when required.
 - Living folder docs are updated for behavior or contract changes.
+- No unresolved rule violations remain.
 
 ## Common mistakes to avoid
 
diff --git a/docs/kanban-policies.md b/docs/kanban-policies.md
index 9d003f9..034880e 100644
--- a/docs/kanban-policies.md
+++ b/docs/kanban-policies.md
@@ -9,7 +9,7 @@ These policies apply to the HQ Kanban/planning system. Task files in `tasks/` re
 - Default global WIP limit: 3 concurrent in-progress tasks.
 - Per-project override is optional and must be documented in the project's board notes or task metadata.
 - Do not start new work when the WIP limit is reached unless a blocked item is being swarmed.
-- QA holds at most 3 tasks awaiting review.
+- QA holds at most 3 tasks awaiting review; automated claiming stops while 1 is unresolved (`claim_next` QA-budget gate).
 
 ## Entry and exit criteria
 
@@ -22,7 +22,7 @@ These policies apply to the HQ Kanban/planning system. Task files in `tasks/` re
 ## Blocked items
 
 - Blocked state must be explicit in task metadata.
-- Every blocked item needs a reason and an owner.
+- Every blocked item needs a reason; name an owner when swarming starts.
 - Blocked items older than one business day require escalation.
 - Swarming takes priority over starting unrelated work.
 
@@ -41,7 +41,8 @@ These fields are advisory in this phase. Planner and dashboard enforcement will
 - Build, test, and lint pass with exit code 0.
 - `lint_task_file` passes on the active task file.
 - Verification evidence is recorded.
-- Required documentation is updated.
+- `CHANGELOG.md` is updated when required.
+- Living folder docs are updated for behavior or contract changes.
 - No unresolved rule violations remain.
 
 ## Feedback loops
diff --git a/mcp-lint-server/server.py b/mcp-lint-server/server.py
index 342764e..7452e73 100755
--- a/mcp-lint-server/server.py
+++ b/mcp-lint-server/server.py
@@ -559,7 +559,9 @@ def _check_planner_metadata(content: str, file_path: str) -> list[str]:
     counts: dict[str, int] = {}
     stamps: dict[str, str] = {}
     for raw in content.splitlines():
-        m = re.match(r"^\*\*(Estimate|Deadline|Depends on):\*\*\s*(.*)$", raw.strip())
+        m = re.match(
+            r"^\*\*(Estimate|Deadline|Depends on|Milestone):\*\*\s*(.*)$", raw.strip()
+        )
         if m:
             key, value = m.group(1), m.group(2).strip()
             counts[key] = counts.get(key, 0) + 1
@@ -578,6 +580,12 @@ def _check_planner_metadata(content: str, file_path: str) -> list[str]:
                     f"Planner metadata: `**Depends on:**` must be ids such as `338` or "
                     f"`[338, 340]` (got `{value}`)."
                 )
+            elif key == "Milestone":
+                if not value or "\n" in value:
+                    issues.append(
+                        f"Planner metadata: `**Milestone:**` must be a single "
+                        f"non-empty value such as `M03` (got `{value or '(empty)'}`)."
+                    )
             continue
         s = re.match(r"^\s*\*\*(Started|Submitted|Finished):\*\*\s*(.*)$", raw)
         if s:
diff --git a/mcp-planner-server/DECISIONS.md b/mcp-planner-server/DECISIONS.md
index 36a2a3e..44870b1 100644
--- a/mcp-planner-server/DECISIONS.md
+++ b/mcp-planner-server/DECISIONS.md
@@ -187,3 +187,10 @@ not initialized`.
 - **Decision:** one numeric sort key (leading filename integer, lexical fallback) applied to lanes, milestone groups, plan buckets and alert rails; the deep-link modal waits for the first successful status, carries `project_root`, and retries once automatically after login on 401; `fetchStatus` sniffs non-JSON bodies and names the edge-login/ingress cause instead of dumping the token; new read-only `GET /api/hours` aggregates `elapsed_seconds` by finish date into 14 daily plus 8 weekly rows (measured-only, unstamped tasks skipped), rendered as an SVG block reusing the plan-chart pattern.
 - **Consequences:** board order is numeric everywhere; deep links survive a cold open; the status line diagnoses instead of dumping. Hours are derived per request like the plan buckets — no second store.
 - **Rollback:** revert `server.py` + `static/index.html`; the board returns to lexical order, immediate modal, and no hours block.
+
+## [2026-11-02] ADR-013: Milestone writer, enforced locks, week scope
+
+- **Context:** the audit found `**Milestone:**` readable but unwritable by any tool (hand-edited free text), `sprint_lock` declarative-only while its docstring claimed enforcement, milestone grouping case-sensitive, and `sprint_stats`/quota unscoped and date-blind. The week scope (calendar Mon-Sun by stamps) and precedence (Strategist veto unless Manager overrides) are Manager decisions recorded here.
+- **Decision:** `schedule_tasks` accepts a trailing optional `:milestone` segment and becomes the single writer for all four header lines (lint enforces non-empty single-line Milestone); grouping keys are casefolded with first-seen display; `claim_next` refuses work while any `tasks/.plan/sprint-*.lock` exists (delete to unlock); `sprint_stats` gains an optional `week="YYYY-Www"` param defaulting to the current week with today-finished reporting in quota.
+- **Consequences:** milestones, locks, and week numbers are managed entities with tests; the 369 xfail tripwires convert to must-pass guards.
+- **Rollback:** revert `server.py` milestone/lock/week hunks plus lint rule; hand-editing returns and tripwires go red again.
diff --git a/mcp-planner-server/README.md b/mcp-planner-server/README.md
index 324a7ca..91ae1e0 100644
--- a/mcp-planner-server/README.md
+++ b/mcp-planner-server/README.md
@@ -24,17 +24,17 @@ dashboard on loopback port 8108.
 
 ## HTTP surface (loopback 8108)
 
-| Route                                                     | Purpose                                                                                                                                                                                                   |
-| --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
-| `GET /`                                                   | Standalone dark-mode dashboard (no build step).                                                                                                                                                           |
-| `GET /static/*`                                           | Dashboard assets (same `static/` directory).                                                                                                                                                              |
-| `GET /api/status[?project_root=<abs path>]`               | JSON status contract the dashboard renders.                                                                                                                                                               |
-| `GET /api/task?id=<id>` or `?path=tasks/<lane>/<file>.md` | One task file as `{id, path, lane, title, markdown}` for the dashboard modal. `id` wins when both are sent. 400 no param, 401 no session, 403 outside grants or unsafe path, 404 unknown, 500 unexpected. |
-| `GET /api/hours[?project_root=<abs path>]` | Measured hours from task stamps: per-day rows for the last 14 days plus per-week rows for the last 8 ISO weeks (`{date/week, measured_hours, done}`). Measured-only: tasks without `Finished` + `elapsed_seconds` never count. Same 401/403 contract as `/api/status`. |
-| `POST /api/login`                                         | `{"username","password"}` → `{token, username, role, allowed_projects}` + `HttpOnly` cookie.                                                                                                              |
-| `POST /api/logout`                                        | Invalidates the session and clears the cookie.                                                                                                                                                            |
-| `GET /api/me`                                             | Current user, or 401 when signed out (200 + `note: "auth disabled"` in open mode).                                                                                                                        |
-| `POST /mcp`                                               | MCP Streamable HTTP endpoint (tools). Auth-free on loopback; the tunnel 404s it.                                                                                                                          |
+| Route                                                     | Purpose                                                                                                                                                                                                                                                                |
+| --------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
+| `GET /`                                                   | Standalone dark-mode dashboard (no build step).                                                                                                                                                                                                                        |
+| `GET /static/*`                                           | Dashboard assets (same `static/` directory).                                                                                                                                                                                                                           |
+| `GET /api/status[?project_root=<abs path>]`               | JSON status contract the dashboard renders.                                                                                                                                                                                                                            |
+| `GET /api/task?id=<id>` or `?path=tasks/<lane>/<file>.md` | One task file as `{id, path, lane, title, markdown}` for the dashboard modal. `id` wins when both are sent. 400 no param, 401 no session, 403 outside grants or unsafe path, 404 unknown, 500 unexpected.                                                              |
+| `GET /api/hours[?project_root=<abs path>]`                | Measured hours from task stamps: per-day rows for the last 14 days plus per-week rows for the last 8 ISO weeks (`{date/week, measured_hours, done}`). Measured-only: tasks without `Finished` + `elapsed_seconds` never count. Same 401/403 contract as `/api/status`. |
+| `POST /api/login`                                         | `{"username","password"}` → `{token, username, role, allowed_projects}` + `HttpOnly` cookie.                                                                                                                                                                           |
+| `POST /api/logout`                                        | Invalidates the session and clears the cookie.                                                                                                                                                                                                                         |
+| `GET /api/me`                                             | Current user, or 401 when signed out (200 + `note: "auth disabled"` in open mode).                                                                                                                                                                                     |
+| `POST /mcp`                                               | MCP Streamable HTTP endpoint (tools). Auth-free on loopback; the tunnel 404s it.                                                                                                                                                                                       |
 
 `/api/status` returns per-lane **task lists** (`lanes`), the milestone tree
 (`milestone_tree`), upcoming deadlines (`deadlines`), the pacing figures
@@ -123,6 +123,9 @@ the tunnel goes live, then verify: `https://planner.example.com/mcp` → 404,
 - `tasks/` Markdown is the canonical source of truth; the planner is a derived
   index (`tasks/.plan/index.json`, gitignored) regenerated per turn.
 - Autopilot QA budget: max 1 unresolved QA/review task (general WIP ceiling 3).
+- Sprint scope is the calendar week Monday–Sunday (UTC), filtered by Started/Finished stamps; `sprint_stats` accepts an optional `week="YYYY-Www"`.
+- Precedence: Sprint Strategist veto stands unless the Manager explicitly overrides.
+- Sprint locks are enforced: `claim_next` refuses work while any `tasks/.plan/sprint-*.lock` exists; deleting the file unlocks.
 - `/mcp` trusts the bind and the tunnel ingress, not session auth: the
   `^/mcp(/.*)?$ → 404` ingress rule must stay ahead of the catch-all, and the
   port must never leave `127.0.0.1`. Breaking either exposes tool execution.
@@ -189,24 +192,25 @@ to a successful claim without ever blocking it. Hand-moving a task file around
 
 ### Scheduling metadata (`schedule_tasks`)
 
-The Planner reads `**Estimate:**`, `**Deadline:**` and `**Depends on:**` from
-the task header, and Markdown stays the only source of truth. `schedule_tasks`
-is the single writer for those three lines:
+The Planner reads `**Estimate:**`, `**Deadline:**`, `**Depends on:**` and
+`**Milestone:**` from the task header, and Markdown stays the only source of
+truth. `schedule_tasks` is the single writer for those four lines:
 
 ```
 schedule_tasks(project_root, "336:3h:2026-10-25, 339:3h:2026-10-27:338")
 ```
 
-Each entry is `id:estimate:deadline[:deps]`; `-` leaves a value untouched.
+Each entry is `id:estimate:deadline[:deps[:milestone]]` (e.g.
+`340:2h:2026-11-01:-:M03` sets only the milestone); `-` leaves a value untouched.
 The tool resolves the id in the active lanes only, replaces an existing value
 or inserts the line directly after `**Status:**` (final order Estimate,
-Deadline, Depends on), leaves the rest of the file byte-identical, and writes
+Deadline, Depends on, Milestone), leaves the rest of the file byte-identical, and writes
 atomically. It is idempotent, and the call is **all-or-nothing**: one malformed
 entry rejects the whole batch so a partially applied schedule cannot exist.
 Rejections are explicit — unknown or archived id, duplicate id in one call,
 estimate that is not `Nh`/`N.Nh`, deadline that is not `YYYY-MM-DD`, dependencies
 that are not ids. The lint rule `_check_planner_metadata` enforces the same
-formats, so an agent cannot invent one and have the task silently drop out of
+formats (Milestone must be a single non-empty value when present), so an agent cannot invent one and have the task silently drop out of
 capacity and the timeline.
 
 ### Measured time (`Started`, `Submitted`, `Finished`)
diff --git a/mcp-planner-server/server.py b/mcp-planner-server/server.py
index 23a64bf..890d411 100644
--- a/mcp-planner-server/server.py
+++ b/mcp-planner-server/server.py
@@ -740,14 +740,16 @@ def schedule_tasks(project_root: str, assignments: str) -> str:
     The Planner derives everything from `tasks/` Markdown, but nothing wrote
     the metadata it reads, so an agent had to hand-edit headers — the exact
     place where a stray space silently drops a deadline from the read model.
-    This tool is the single writer for `**Estimate:**`, `**Deadline:**` and
-    `**Depends on:**`.
+    This tool is the single writer for `**Estimate:**`, `**Deadline:**`,
+    `**Depends on:**` and `**Milestone:**`.
 
     Args:
         project_root: Absolute path to the project holding tasks/.
         assignments: Comma-separated entries of the form
-            `id:estimate:deadline[:deps]`, e.g.
-            `336:3h:2026-10-25, 339:3h:2026-10-27:338`.
+            `id:estimate:deadline[:deps[:milestone]]`, e.g.
+            `336:3h:2026-10-25, 339:3h:2026-10-27:338` or
+            `340:2h:2026-11-01:-:M03` (use `-` for deps to set only
+            the milestone).
             `-` leaves a value unchanged (clear is not supported on purpose:
             deleting a deadline is a Manager decision, not an agent one).
 
@@ -764,18 +766,21 @@ def schedule_tasks(project_root: str, assignments: str) -> str:
 
     entries = [e.strip() for e in assignments.split(",") if e.strip()]
     if not entries:
-        return "No assignments given. Use `id:estimate:deadline[:deps]`."
+        return "No assignments given. Use `id:estimate:deadline[:deps[:milestone]]`."
 
     seen: set[str] = set()
-    parsed: list[tuple[str, str | None, str | None, str | None]] = []
+    parsed: list[tuple[str, str | None, str | None, str | None, str | None]] = []
     rejects: list[str] = []
     for entry in entries:
         parts = [p.strip() for p in entry.split(":")]
-        if len(parts) < 3 or len(parts) > 4:
-            rejects.append(f"{entry} (expected id:estimate:deadline[:deps])")
+        if len(parts) < 3 or len(parts) > 5:
+            rejects.append(
+                f"{entry} (expected id:estimate:deadline[:deps[:milestone]])"
+            )
             continue
         tid, estimate, deadline = parts[0], parts[1], parts[2]
-        deps = parts[3] if len(parts) == 4 else None
+        deps = parts[3] if len(parts) >= 4 else None
+        milestone = parts[4] if len(parts) == 5 else None
         try:
             tid_norm = str(int(tid))
         except (TypeError, ValueError):
@@ -803,6 +808,7 @@ def schedule_tasks(project_root: str, assignments: str) -> str:
                 None if estimate == "-" else estimate,
                 None if deadline == "-" else deadline,
                 None if deps in (None, "-") else deps,
+                None if milestone in (None, "-", "") else milestone,
             )
         )
 
@@ -817,7 +823,7 @@ def schedule_tasks(project_root: str, assignments: str) -> str:
             + "\n".join(f"- {r}" for r in rejects)
         )
 
-    for tid, estimate, deadline, deps in parsed:
+    for tid, estimate, deadline, deps, milestone in parsed:
         task = _find_task_by_id(all_tasks, tid)
         if task is None:
             results.append(
@@ -868,8 +874,10 @@ def schedule_tasks(project_root: str, assignments: str) -> str:
             return True
 
         # Insert deepest-first so the final order under Status is
-        # Estimate, Deadline, Depends on (each insert lands right after Status).
-        changed = set_field("Depends on", deps)
+        # Estimate, Deadline, Depends on, Milestone (each insert lands
+        # right after Status).
+        changed = set_field("Milestone", milestone)
+        changed = set_field("Depends on", deps) or changed
         changed = set_field("Deadline", deadline) or changed
         changed = set_field("Estimate", estimate) or changed
 
@@ -955,6 +963,7 @@ def claim_next(project_root: str, task_id: str) -> str:
     """Claim the next task: move it from backlog to in-progress.
 
     Circuit breaker: refuses the claim if any of these gate conditions fail:
+    - A sprint lock file exists under tasks/.plan/ (delete it to unlock).
     - The task does not exist or is not in tasks/backlog/.
     - Any dependency is not in tasks/completed/.
     - tasks/qa/ already has an unresolved task (QA budget exhausted).
@@ -973,6 +982,16 @@ def claim_next(project_root: str, task_id: str) -> str:
     workspace_root = _explicit_project_root(project_root, "claim_next")
     tasks = _load_all_tasks(workspace_root)
 
+    # Sprint lock gate: a locked sprint blocks all new claims until the
+    # lock file is deleted (Manager-owned unlock). Checked first so one
+    # message covers every task id.
+    locks = sorted((workspace_root / "tasks" / ".plan").glob("sprint-*.lock"))
+    if locks:
+        return (
+            f"❌ claim_next blocked: sprint locked ({locks[0].name}). "
+            f"Delete the lock file to unlock."
+        )
+
     task = _find_task_by_id(tasks, task_id)
     if task is None:
         return f"❌ claim_next blocked: task {task_id} not found."
@@ -1145,14 +1164,20 @@ def plan_status(project_root: Optional[str] = None) -> str:
 
     lines.append("## Milestones")
     milestones: dict[str, list[dict]] = {}
+    display: dict[str, str] = {}
     for t in tasks:
         m = t.get("milestone")
         if m:
-            milestones.setdefault(m, []).append(t)
+            # Group case-insensitively so M03 and m03 read as one
+            # milestone; display keeps the first-seen spelling.
+            key = str(m).casefold()
+            display.setdefault(key, str(m))
+            milestones.setdefault(key, []).append(t)
     if not milestones:
         lines.append("- None defined.")
     else:
-        for ms, items in sorted(milestones.items()):
+        for key, items in sorted(milestones.items(), key=lambda kv: kv[0]):
+            ms = display[key]
             done = sum(1 for i in items if i.get("status") == "closed")
             lines.append(f"- {ms}: {len(items)} task(s), {done} completed.")
     lines.append("")
@@ -1161,11 +1186,52 @@ def plan_status(project_root: Optional[str] = None) -> str:
 
 
 @_project_tool
-def sprint_stats(project_root: Optional[str] = None) -> str:
+def _week_range(week: Optional[str] = None):
+    """Resolve an ISO week label to a Mon-Sun UTC date range.
+
+    Args:
+        week: ``YYYY-Www`` (e.g. ``2026-W45``) or None for the current week.
+
+    Returns:
+        ``(monday, sunday, label)`` or ``(None, None, "")`` when malformed.
+    """
+    if week is None:
+        today = datetime.now(timezone.utc).date()
+        monday = today - timedelta(days=today.weekday())
+    else:
+        m = re.match(r"^(\d{4})-W(\d{2})$", str(week).strip())
+        if not m:
+            return None, None, ""
+        try:
+            monday = date.fromisocalendar(int(m.group(1)), int(m.group(2)), 1)
+        except ValueError:
+            return None, None, ""
+    sunday = monday + timedelta(days=6)
+    label = f"{monday.isocalendar()[0]:04d}-W{monday.isocalendar()[1]:02d}"
+    return monday, sunday, label
+
+
+def _finished_today_count(tasks) -> int:
+    """Count tasks whose Finished stamp falls on today's UTC date."""
+    today = datetime.now(timezone.utc).date()
+    count = 0
+    for t in tasks:
+        finished = _parse_task_timestamp(t.get("finished_at"))
+        if finished is not None and finished.date() == today:
+            count += 1
+    return count
+
+
+def sprint_stats(project_root: Optional[str] = None, week: Optional[str] = None) -> str:
     """Compute hours spent, progress percentage, and velocity.
 
+    Week-scoped (Manager decision): counts below the snapshot header cover
+    only tasks whose Started or Finished stamp falls in the Mon-Sun week
+    (UTC). ``week`` accepts ``YYYY-Www``; None means the current week.
+
     Args:
         project_root: Absolute path to the project holding tasks/.
+        week: ISO week label or None for the current week.
 
     Returns:
         A markdown-formatted stats report.
@@ -1173,6 +1239,19 @@ def sprint_stats(project_root: Optional[str] = None) -> str:
     workspace_root = _explicit_project_root(project_root, "sprint_stats")
     tasks = _load_all_tasks(workspace_root)
 
+    monday, sunday, week_label = _week_range(week)
+    if monday is None:
+        return f"❌ sprint_stats blocked: week must look like 2026-W45 (got `{week}`)."
+
+    def _in_week(task) -> bool:
+        for key in ("started_at", "finished_at"):
+            stamp = _parse_task_timestamp(task.get(key))
+            if stamp is not None and monday <= stamp.date() <= sunday:
+                return True
+        return False
+
+    scoped = [t for t in tasks if _in_week(t)]
+
     total_tasks = len(tasks)
     completed = sum(1 for t in tasks if t.get("status") == "closed")
     in_progress = _count_in_progress(tasks)
@@ -1187,19 +1266,34 @@ def sprint_stats(project_root: Optional[str] = None) -> str:
         for t in tasks
         if t.get("status") == "closed" and t.get("estimate_hours")
     )
+    week_est = sum(
+        (t.get("estimate_hours") or 0) for t in scoped if t.get("estimate_hours")
+    )
+    week_completed = sum(1 for t in scoped if t.get("status") == "closed")
+    week_completed_est = sum(
+        (t.get("estimate_hours") or 0)
+        for t in scoped
+        if t.get("status") == "closed" and t.get("estimate_hours")
+    )
     # Measured hours: only closed tasks that carry both stamps, so this line can
     # never quietly reuse an estimate.
     measured_hours = 0.0
+    week_measured_hours = 0.0
     for t in tasks:
         brief = _task_brief(t)
         if t.get("status") == "closed" and brief.get("elapsed_seconds") is not None:
             measured_hours += brief["elapsed_seconds"] / 3600.0
+            if _in_week(t):
+                week_measured_hours += brief["elapsed_seconds"] / 3600.0
 
     pct = (completed / total_tasks * 100) if total_tasks else 0.0
 
     lines: list[str] = []
     lines.append("# Sprint Stats")
     lines.append("")
+    lines.append(
+        f"Week scope: {week_label} ({monday.isoformat()}..{sunday.isoformat()}, UTC)"
+    )
     lines.append(f"Total tasks: {total_tasks}")
     lines.append(f"Completed: {completed} ({pct:.0f}%)")
     lines.append(f"In-progress: {in_progress}")
@@ -1209,9 +1303,14 @@ def sprint_stats(project_root: Optional[str] = None) -> str:
     lines.append("## Estimates")
     lines.append(f"Total estimated: {total_est}h")
     lines.append(f"Completed estimated: {completed_est}h")
+    lines.append(f"Week estimated: {week_est}h")
+    lines.append(
+        f"Week completed: {week_completed} task(s), {week_completed_est}h estimated"
+    )
     lines.append("")
     lines.append("## Measured")
     lines.append(f"Completed measured: {measured_hours:.2f}h")
+    lines.append(f"Week measured: {week_measured_hours:.2f}h")
     lines.append("## Velocity")
     lines.append(f"Tasks completed per lane snapshot: {completed} / {total_tasks}")
     lines.append("")
@@ -1270,16 +1369,22 @@ def milestone_status(project_root: Optional[str] = None) -> str:
     tasks = _load_all_tasks(workspace_root)
 
     milestones: dict[str, list[dict]] = {}
+    display: dict[str, str] = {}
     for t in tasks:
         m = t.get("milestone")
         if m:
-            milestones.setdefault(m, []).append(t)
+            # Same casefold grouping as plan_status: one milestone
+            # regardless of spelling case, first-seen display.
+            key = str(m).casefold()
+            display.setdefault(key, str(m))
+            milestones.setdefault(key, []).append(t)
 
     if not milestones:
         return "## Milestone Status\n\nNo milestones defined."
 
     lines: list[str] = ["# Milestone Status", ""]
-    for name, items in sorted(milestones.items()):
+    for key, items in sorted(milestones.items(), key=lambda kv: kv[0]):
+        name = display[key]
         total = len(items)
         done = sum(1 for i in items if i.get("status") == "closed")
         pct = (done / total * 100) if total else 0.0
@@ -1299,10 +1404,9 @@ def milestone_status(project_root: Optional[str] = None) -> str:
 def sprint_lock(sprint_id: str, project_root: Optional[str] = None) -> str:
     """Mark a sprint as locked (no further changes allowed).
 
-    In v1 this is a declarative operation: it records the lock in the
-    planner index and prevents `claim_next` from starting new work until
-    the lock is cleared. The actual lock state is tracked in
-    tasks/.plan/index.json.
+    The lock is enforced: `claim_next` refuses all new work while any
+    `tasks/.plan/sprint-*.lock` file exists. Delete the lock file to
+    unlock (Manager-owned).
 
     Args:
         sprint_id: Identifier of the sprint to lock.
@@ -1438,10 +1542,15 @@ def sprint_check_daily_quota(project_root: Optional[str] = None) -> str:
 
     in_progress = [t for t in tasks if t.get("lane") == "in-progress"]
     qa_pending = [t for t in tasks if t.get("lane") == "qa"]
+    finished_today = _finished_today_count(tasks)
 
     if not in_progress and not qa_pending:
-        return "✅ DAILY_QUOTA_REACHED: no in-progress or QA-pending tasks."
+        return (
+            "✅ DAILY_QUOTA_REACHED: no in-progress or QA-pending tasks. "
+            f"Finished today: {finished_today}."
+        )
     parts: list[str] = []
+    parts.append(f"Finished today: {finished_today}.")
     if in_progress:
         parts.append(
             f"{len(in_progress)} in-progress: "
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 17ff270..ee72fde 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.70.1</system_version>
+<system_version>9.70.2</system_version>
diff --git a/prompts/fragments/06-personas.md b/prompts/fragments/06-personas.md
index 42867f9..114a1e6 100644
--- a/prompts/fragments/06-personas.md
+++ b/prompts/fragments/06-personas.md
@@ -34,7 +34,7 @@
       - **MoSCoW prioritization:** Must Do (blocks other work or is a production defect), Should Do (high-value but can defer), Could Do (nice-to-have), Won't Do this sprint.
       - **WIP limits:** Maximum 3 concurrent in-progress tasks. Any task exceeding S-size requires explicit capacity justification.
 
-      You have explicit authority to say NO. When the Manager tries to pull in too many tasks — which he will — you MUST push back with specific evidence: estimated complexity, dependency risks, test coverage requirements, and which MoSCoW tier each candidate falls into.
+      You have explicit authority to say NO. When the Manager tries to pull in too many tasks — which he will — you MUST push back with specific evidence: estimated complexity, dependency risks, test coverage requirements, and which MoSCoW tier each candidate falls into. Precedence: the Strategist veto stands unless the Manager explicitly overrides it.
 
       Output a ranked sprint plan using MoSCoW prioritization with explicit WIP limits and a capacity budget (total story-points or time estimate).
 
@@ -61,4 +61,4 @@ Layer 1 — explicit mention wins. If the Manager names a persona (exact name or
 Layer 2 — threshold inference. If nobody is named, infer from the Manager's message plus conversation history and current machine state. High confidence means the message maps to exactly one persona's trigger or duty with no rival. Then load it, declare it in the existing bracket label, and proceed. The label makes the choice visible and correctable. Low confidence means two or more personas fit, or none fits clearly. Then do NOT guess. Stop and ask the Manager which persona to load. Guessing an identity is a hallucination risk. One question costs less than a wrong persona.
 No new label. The bracket declaration in 02-role stays the single speaker display. Never add a second Speaking-as line.
 </auto_load>
-</personas>
\ No newline at end of file
+</personas>
diff --git a/prompts/fragments/11-execution_workflow.md b/prompts/fragments/11-execution_workflow.md
index 246074d..75d903e 100644
--- a/prompts/fragments/11-execution_workflow.md
+++ b/prompts/fragments/11-execution_workflow.md
@@ -42,7 +42,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 9. **Step 9: Next Task Transition (Sprint Strategist)**
    - Sprint Strategist verifies backlog priority and immediately initiates Step 1 on the next sprint candidate.
 
-**Planner MCP and daily pacing.** The Planner singleton runs at `127.0.0.1:8108` and reads `tasks/` Markdown as the single source of truth; it never replaces the Kanban files. Use it at six moments: when the Manager says start today's work — in any language, including "کار امروز رو شروع کنیم" — call `sprint_daily_agenda` before touching a task file; to take work, call `claim_next(project_root, task_id)` instead of moving the file by hand, and report a refusal with its stated reason instead of bypassing it; **when the Manager approves a plan, call `schedule_tasks(project_root, "id:estimate:deadline[:deps], …")` so the estimate and deadline land in the task headers, and never hand-edit those header lines** — a stray character there silently removes the task from the Planner's capacity and timeline; to size the day, `plan_status` and `qa_budget` (one unresolved review is the ceiling); to close work, `sprint_check_daily_quota`, and when it returns `DAILY_QUOTA_REACHED`, present `sprint_stats` and stop claiming for the day. If the server is unreachable, fall back to the Kanban workflow and say so plainly — never stall waiting for it.
+**Planner MCP and daily pacing.** The Planner singleton runs at `127.0.0.1:8108` and reads `tasks/` Markdown as the single source of truth; it never replaces the Kanban files. Use it at six moments: when the Manager says start today's work — in any language, including "کار امروز رو شروع کنیم" — call `sprint_daily_agenda` before touching a task file; to take work, call `claim_next(project_root, task_id)` instead of moving the file by hand, and report a refusal with its stated reason instead of bypassing it; **when the Manager approves a plan, call `schedule_tasks(project_root, "id:estimate:deadline[:deps[:milestone]], …")` so the estimate and deadline land in the task headers, and never hand-edit those header lines** — a stray character there silently removes the task from the Planner's capacity and timeline; to size the day, `plan_status` and `qa_budget` (one unresolved review is the ceiling); to close work, `sprint_check_daily_quota`, and when it returns `DAILY_QUOTA_REACHED`, present `sprint_stats` and stop claiming for the day. If the server is unreachable, fall back to the Kanban workflow and say so plainly — never stall waiting for it.
 
 **Night mode override.** When the Manager hands over the night ("night mode", "100% autopilot until morning"), `<night_mode>` governs: the Step 6 QA gate, the Step 7 review gate, and the Step 8 closure approval are pre-authorized and played by the Hands, and the question tool is not used until he returns. Every other step in this pipeline is unchanged.
-</execution_workflow>
\ No newline at end of file
+</execution_workflow>
diff --git a/system-prompt.md b/system-prompt.md
index c848bfe..b128dfc 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.70.1</system_version>
+<system_version>9.70.2</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -87,7 +87,7 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
       - **MoSCoW prioritization:** Must Do (blocks other work or is a production defect), Should Do (high-value but can defer), Could Do (nice-to-have), Won't Do this sprint.
       - **WIP limits:** Maximum 3 concurrent in-progress tasks. Any task exceeding S-size requires explicit capacity justification.
 
-      You have explicit authority to say NO. When the Manager tries to pull in too many tasks — which he will — you MUST push back with specific evidence: estimated complexity, dependency risks, test coverage requirements, and which MoSCoW tier each candidate falls into.
+      You have explicit authority to say NO. When the Manager tries to pull in too many tasks — which he will — you MUST push back with specific evidence: estimated complexity, dependency risks, test coverage requirements, and which MoSCoW tier each candidate falls into. Precedence: the Strategist veto stands unless the Manager explicitly overrides it.
 
       Output a ranked sprint plan using MoSCoW prioritization with explicit WIP limits and a capacity budget (total story-points or time estimate).
 
@@ -479,7 +479,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 9. **Step 9: Next Task Transition (Sprint Strategist)**
    - Sprint Strategist verifies backlog priority and immediately initiates Step 1 on the next sprint candidate.
 
-**Planner MCP and daily pacing.** The Planner singleton runs at `127.0.0.1:8108` and reads `tasks/` Markdown as the single source of truth; it never replaces the Kanban files. Use it at six moments: when the Manager says start today's work — in any language, including "کار امروز رو شروع کنیم" — call `sprint_daily_agenda` before touching a task file; to take work, call `claim_next(project_root, task_id)` instead of moving the file by hand, and report a refusal with its stated reason instead of bypassing it; **when the Manager approves a plan, call `schedule_tasks(project_root, "id:estimate:deadline[:deps], …")` so the estimate and deadline land in the task headers, and never hand-edit those header lines** — a stray character there silently removes the task from the Planner's capacity and timeline; to size the day, `plan_status` and `qa_budget` (one unresolved review is the ceiling); to close work, `sprint_check_daily_quota`, and when it returns `DAILY_QUOTA_REACHED`, present `sprint_stats` and stop claiming for the day. If the server is unreachable, fall back to the Kanban workflow and say so plainly — never stall waiting for it.
+**Planner MCP and daily pacing.** The Planner singleton runs at `127.0.0.1:8108` and reads `tasks/` Markdown as the single source of truth; it never replaces the Kanban files. Use it at six moments: when the Manager says start today's work — in any language, including "کار امروز رو شروع کنیم" — call `sprint_daily_agenda` before touching a task file; to take work, call `claim_next(project_root, task_id)` instead of moving the file by hand, and report a refusal with its stated reason instead of bypassing it; **when the Manager approves a plan, call `schedule_tasks(project_root, "id:estimate:deadline[:deps[:milestone]], …")` so the estimate and deadline land in the task headers, and never hand-edit those header lines** — a stray character there silently removes the task from the Planner's capacity and timeline; to size the day, `plan_status` and `qa_budget` (one unresolved review is the ceiling); to close work, `sprint_check_daily_quota`, and when it returns `DAILY_QUOTA_REACHED`, present `sprint_stats` and stop claiming for the day. If the server is unreachable, fall back to the Kanban workflow and say so plainly — never stall waiting for it.
 
 **Night mode override.** When the Manager hands over the night ("night mode", "100% autopilot until morning"), `<night_mode>` governs: the Step 6 QA gate, the Step 7 review gate, and the Step 8 closure approval are pre-authorized and played by the Hands, and the question tool is not used until he returns. Every other step in this pipeline is unchanged.
 </execution_workflow>
diff --git a/tests/test_planning_contracts.py b/tests/test_planning_contracts.py
index e87e409..122d7e8 100644
--- a/tests/test_planning_contracts.py
+++ b/tests/test_planning_contracts.py
@@ -1,11 +1,9 @@
-"""Planning-stack regression contracts for task 369.
-
-Zero source edits. Every planner call uses tmp_path as project_root.
-F1 milestone preservation is a must-pass guard.
-F2 grouping split, F5 unlocked claim, and F6 snapshot stats are documented
-gaps marked xfail strict.
-F3 malformed deadlines, F4 QA ceiling, F7 template sync, and F8 lock-file
-behavior are must-pass guards.
+"""Planning-stack regression contracts, enforced by task 370.
+
+Zero source edits in this file's scope. Every planner call uses tmp_path
+as project_root. F1 milestone preservation, F2 merged grouping, F5 lock
+gate, F3 deadline guards, F4 QA ceiling, F6 week scope, F7 sync guards,
+and F8 lock-file behavior are must-pass guards.
 F10 DoD mismatch is out of code-test scope and is noted only.
 """
 
@@ -91,16 +89,15 @@ def test_f1_milestone_preserved_by_schedule_tasks(tmp_path):
     assert record.get("deadline") == "2026-11-15"
 
 
-@pytest.mark.xfail(strict=True, reason="F2 gap: Milestone grouping is case-sensitive")
-def test_f2_grouping_case_split_documents_gap(tmp_path):
-    """F2 gap: desired canonical grouping merges M1 and m1 into one group."""
+def test_f2_grouping_merges_case_variants(tmp_path):
+    """F2 must-pass: M1 and m1 read as one milestone (first-seen display)."""
     # Targets _parse_task_file (:294) and milestone_status (:1257).
     _write_task(tmp_path, "backlog", "0002-upper.md", _minimal_task(2, milestone="M1"))
     _write_task(tmp_path, "backlog", "0003-lower.md", _minimal_task(3, milestone="m1"))
-    status = SERVER.milestone_status(str(tmp_path))
-    text = str(status)
-    # Desired: a single canonical group, so M1/m1 appear as one entry.
-    assert text.count("M1") + text.count("m1") <= 1
+    text = str(SERVER.milestone_status(str(tmp_path)))
+    # One canonical group: the label appears exactly once (case-insensitive).
+    assert text.lower().count("m1") == 1
+    assert "M1" in text  # first-seen spelling wins the display
 
 
 def test_f3a_schedule_rejects_non_iso_deadline(tmp_path):
@@ -137,25 +134,46 @@ def test_f4_qa_budget_counts_single_ceiling(tmp_path):
     assert "2" in text and ("1" in text or "ceiling" in text or "budget" in text)
 
 
-@pytest.mark.xfail(strict=True, reason="F5 gap: sprint_lock does not block claim_next")
-def test_f5_lock_does_not_block_claim_documents_gap(tmp_path):
-    """F5 gap: desired behavior is that a locked sprint blocks claim_next."""
+def test_f5_lock_blocks_claim(tmp_path):
+    """F5 must-pass: a sprint lock file blocks claim_next with unlock note."""
     # Targets sprint_lock (:1299) and claim_next (:954).
     _write_task(tmp_path, "backlog", "0008-locked.md", _minimal_task(8))
     SERVER.sprint_lock("sprint-1", str(tmp_path))
     outcome = str(SERVER.claim_next(str(tmp_path), "0008")).lower()
-    assert "error" in outcome or "lock" in outcome or "block" in outcome
+    assert "sprint-" in outcome and "unlock" in outcome
+    # A blocked claim moves nothing.
+    assert (tmp_path / "tasks" / "backlog" / "0008-locked.md").is_file()
 
 
-@pytest.mark.xfail(strict=True, reason="F6 gap: unscoped stats and date-blind quota")
-def test_f6_stats_snapshot_and_quota_date_blind_documents_gap(tmp_path):
-    """F6 gap: desired behavior is sprint-scoped stats plus date-aware quota."""
+def test_f6_stats_week_scoped_and_quota_date_aware(tmp_path):
+    """F6 must-pass: stats carry a week scope; quota counts today-finished."""
     # Targets sprint_stats (:1164) and sprint_check_daily_quota (:1424).
-    _write_task(tmp_path, "completed", "0009-done.md", _minimal_task(9))
-    stats_text = str(SERVER.sprint_stats(str(tmp_path))).lower()
-    quota_text = str(SERVER.sprint_check_daily_quota(str(tmp_path))).lower()
-    assert "scope" in stats_text
-    assert "date" in quota_text and "remaining" in quota_text
+    import re
+
+    # An out-of-week stamp must not leak into the week numbers.
+    out_week = _minimal_task(9, estimate="3h") + "**Started:** 2020-01-06T10:00:00Z\n"
+    _write_task(tmp_path, "completed", "0009-done.md", out_week)
+    stats = str(SERVER.sprint_stats(str(tmp_path)))
+    assert "Week scope:" in stats
+    assert re.search(r"Week scope: \d{4}-W\d{2} \(", stats), stats
+    assert "Week estimated: 0h" in stats
+    quota = str(SERVER.sprint_check_daily_quota(str(tmp_path)))
+    assert "Finished today:" in quota
+
+
+def test_f1b_milestone_written_by_schedule_tasks(tmp_path):
+    """F1 must-pass: schedule_tasks writes **Milestone:** via trailing segment."""
+    # Target schedule_tasks milestone segment; `-` deps skips to milestone.
+    name = "0011-writer.md"
+    _write_task(tmp_path, "backlog", name, _minimal_task(11))
+    result = str(SERVER.schedule_tasks(str(tmp_path), "0011:2h:2026-11-20:-:M9"))
+    assert "M9" in result
+    text = (tmp_path / "tasks" / "backlog" / name).read_text(encoding="utf-8")
+    assert "**Milestone:** M9" in text
+    # Dash leaves an existing milestone untouched.
+    SERVER.schedule_tasks(str(tmp_path), "0011:-:-")
+    again = (tmp_path / "tasks" / "backlog" / name).read_text(encoding="utf-8")
+    assert "**Milestone:** M9" in again
 
 
 def test_f7_retrospective_template_exists():
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 114a051..5679f26 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -44,7 +44,7 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.70.1"
+    assert shipped == "9.70.2"
 
 
 def test_parallel_mandate_covers_implementation_triggers():
```
<!-- END_GIT_DIFF -->
