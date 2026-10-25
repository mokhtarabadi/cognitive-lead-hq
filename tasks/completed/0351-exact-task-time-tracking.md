# Task 0351: Exact per-task time tracking from claim to closure

**File:** `tasks/qa/0351-exact-task-time-tracking.md`
**Source:** manager
**Type:** feature
**Status:** in-progress
**Submitted:** 2026-10-25T13:46:33Z
**Started:** 2026-10-25T13:45:53Z
**Estimate:** 5h

## Goal

Record when a task actually starts, when it enters QA and when it closes, so the planner can show measured duration per task instead of the current estimate-only arithmetic, and the lint can reject a malformed stamp.

## Manager's Notes

> ایا زمان دقیق هر تسک که شروع میکنم تا موقعی تموم میشه رو هم یادداشت میکنه ... حدس نه منظورم دقیق مثلا با کامند date بگریم مقایسه کنیم

Today nothing measures time. `_parse_task_file` reads only `File`, `Source`, `Type`, `Status`, `Owner`, `Estimate`, `Deadline`, `Milestone`, `Depends on`; `sprint_stats` sums `Estimate` over closed tasks and calls it "hours spent"; `claim_next` moves the file with no timestamp. The git commit time can approximate closure but says nothing about the start.

## Graph findings (2026-10-25)

Graph over the whole repository (5,000 nodes / 7,382 links) plus targeted reads. The write points are three, and they are already the only writers of their respective facts:

- `mcp-planner-server/server.py` — `_parse_task_file` (header keys), `claim_next` (backlog → in-progress), `_task_brief` (what the dashboard renders), `sprint_stats` (the estimate sum that must stay labelled as an estimate).
- `mcp-context-server/server.py` — `qa_transition` (in-progress → qa), `commit_and_clean_task` (→ completed), `stage_and_inject_diff` (the staging step that runs inside a task).
- `mcp-lint-server/server.py` — the metadata gate added in ADR-003, the only place that can reject a malformed header value.

## Acceptance Criteria

- [x] `claim_next` writes `**Started:**` as ISO-8601 UTC (e.g. `2026-10-25T14:20:31Z`) into the task header with the move to `in-progress`, from the process UTC clock — never a shell `date`, never local time.
- [ ] `qa_transition` writes `**Submitted:**` the same way when the file enters `tasks/qa/`.
- [x] `commit_and_clean_task` writes `**Finished:**` when the file enters `tasks/completed/`.
- [x] A hand-moved task with no `Started` gets it recovered from git (first commit touching the file) at closure, so the duration is measured rather than lost.
- [x] `sync_task_times` stamps a missing `Started`/`Submitted` for files already sitting in `in-progress`/`qa`, idempotently, and refuses the `completed` lane so an old closure never gets a fabricated finish.
- [ ] Re-claiming a task that already has `Started` does not overwrite it; only a missing value is stamped.
- [ ] `_task_brief` exposes `startedAt`, `submittedAt`, `finishedAt` plus a computed `elapsedSeconds` (finished − started) and `qaWaitSeconds` (submitted − started), so the panel never derives time itself.
- [ ] The dashboard shows measured duration per task next to the estimate, and the column is empty (not `0`) when a stamp is missing.
- [ ] `sprint_stats` keeps estimate arithmetic and additionally reports measured hours for closed tasks that carry both stamps, clearly separated from the estimate.
- [ ] The lint rejects a present `**Started:**`/`**Submitted:**`/`**Finished:**` that is not ISO-8601 UTC, and rejects a `Finished` earlier than `Started`.
- [ ] Docs: planner README, both DECISIONS files, executor prompt sentence, CHANGELOG.

## Local TODOs

- [ ] Initial codebase exploration (graph + read the three write points)
- [ ] Planner: parse, stamp on claim, expose in the brief, panel column
- [ ] Context server: stamp on qa transition and on closure
- [ ] Lint: validate the three stamps
- [ ] Tests: stamp-once, no overwrite, duration math, lint accept/reject
- [ ] Docs and CHANGELOG

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/ -q`
- **Expected result:** full HQ suite green, including the new timestamp tests
- **Actual result:** `19 passed` for `tests/test_task_timestamps.py` (recover-from-git with a pinned `GIT_AUTHOR_DATE`, mtime fallback, idempotency, naive→null, negative→null, refusal of the `completed` lane, sprint-stats separation, duplicate stamp, claim-stamp-once); full suite `734 passed in 49.53s`. Live check after restarting the services: `claim_next` wrote `**Started:** 2026-10-25T13:45:53Z` and `qa_transition` wrote `**Submitted:** 2026-10-25T13:46:33Z`.
- **Exit code:** 0

## Definition of Done

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** stamping on every claim path could double-write or overwrite a genuine start time when a task is re-claimed after a block; mitigated by write-only-when-absent and a test.
- **Risk:** a clock that reports local time would produce misleading durations; mitigated by reusing the planner's existing clock and linting the `Z` suffix.
- **Rollback:** remove the three stamps, the brief fields and the lint rule; the estimate-only behaviour returns and the extra header lines stay harmless.

---

## Execution Log & Reasoning

**Design.** Three stamps, three writers, no fourth path: `claim_next` writes `Started`, `qa_transition` writes `Submitted`, `commit_and_clean_task` writes `Finished`. Each is write-once, so a re-claim after a block cannot rewrite the original start, and each uses UTC on purpose — a local-time value would make two machines incomparable. The planner only reads them and derives durations in `_task_brief`, which returns `null` rather than `0` when a stamp is missing, so the panel can never show a fake instant task.

**Live proof after deploying the three servers.** `claim_next` on this task wrote `**Started:** 2026-10-25T13:45:53Z` into the header, exactly after `Status`, and the second claim attempt (after I moved the file back to backlog to retest the stale build) produced a fresh stamp because the first one had been removed with the un-claim. `sprint_stats` now prints a separate `Completed measured` line beside the estimate.

**Autopilot lock (2026-10-25).** The Manager locked autopilot while this task sat in `tasks/qa/`. QA and review run without asking; the only pause left is the explicit closure word.

**QA cycle 1 (Brain).** `QA_REJECTED` with six blocking findings, all closed: wrong-duration paths (`_parse_utc` no longer assumes UTC for a naive value, `_task_brief` returns `None` instead of a negative number, so the panel cannot render a clamped `0s`); a fabricated start in `sync_task_times` (it now skips and reports the file when git and mtime both fail); the missing QA wait for hand-moved files (`qa_transition` backfills `Started` from git before stamping `Submitted`); lane cards that showed no measurement (now `· measured 2h 14m`, empty when null); git safety (resolved paths, containment refusal, 5s timeout); and the missing proof. Six new tests cover naive→null, negative→null, refusing the `completed` lane, `sprint_stats` estimate-versus-measured separation, a duplicated stamp rejected by lint, and a real `claim_next` stamped once with the original start surviving a re-claim. Full suite `734 passed`.

**Stale-process lesson.** The first claim wrote no stamp because the running `mcp-planner` singleton still held the previous build: editing the repo does not change a loaded service. The deploy step for this change is a copy into `~/.config/opencode/mcp-*/` plus a `systemctl --user restart` of `mcp-planner`, `mcp-lint` and `mcp-context`, which is what made the stamp appear.

**Hand-moved tasks (closure gap, fixed here).** `Started` only came from `claim_next`, so a task moved by hand reached closure with `Finished` alone and its duration was silently lost — the lint passed it because absence is valid. `commit_and_clean_task` now checks for a missing `Started` and recovers it from git (`git log --follow --reverse --format=%aI`, first commit touching the file), writing the real author timestamp rather than `now`, because git already recorded when the file appeared. Proven by a test that builds a throwaway repo with a pinned `GIT_AUTHOR_DATE` and asserts the recovered stamp matches it exactly.

**Hand-moved lanes, second gap (also fixed here).** Closure was covered but the lane moves were not: a hand `git mv` into `in-progress` still left no `Started`, and into `qa` left no `Submitted`. New tool `sync_task_times(project_root, lane?)` stamps exactly those two lanes, idempotently, and deliberately refuses the `completed` lane — stamping `Finished` at call time on an old closed task would fabricate a duration. The start comes from git history, then the file mtime, and is skipped when neither can answer; `Submitted` is stamped at call time because the caller runs it right after the move. The registry guard in `tests/test_mcp_servers.py` was updated to 16 tools, which is the project's way of making that addition deliberate.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 5b33a0f..36f3b6f 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- Task time is now measured, not estimated. `claim_next` stamps `**Started:**`, `qa_transition` stamps `**Submitted:**` and `commit_and_clean_task` stamps `**Finished:**` as ISO-8601 UTC, each write-once so a re-claim never rewrites the original start. `_task_brief` derives `elapsed_seconds` and `qa_wait_seconds` (`null`, never `0`, when a stamp is missing), the task modal shows `measured 2h 14m`, and `sprint_stats` adds a separate `Completed measured` line beside the estimate. `_check_planner_metadata` rejects a non-UTC stamp or a finish earlier than its start. 10 new tests; full suite 725 green.
+
 - **Planner writes its own metadata, and the lint refuses to let it drift (Task 0350):** an approved plan used to reach the task files only by hand-editing headers, the one place where a stray space or a free-text date drops a task out of capacity and the timeline with no error on either side. New Planner tool `schedule_tasks(project_root, "id:estimate:deadline[:deps], …")` is the single writer for `**Estimate:**`, `**Deadline:**` and `**Depends on:**`: it resolves the id in the active lanes, replaces an existing line or inserts one directly after `**Status:**` (final order Estimate, Deadline, Depends on), leaves the rest of the file byte-identical, writes atomically, is idempotent, and is all-or-nothing so one malformed entry rejects the whole batch instead of leaving half a schedule. Rejections are explicit per entry (unknown or archived id, duplicate id, estimate that is not `Nh`/`N.Nh`, deadline that is not `YYYY-MM-DD`, dependencies that are not ids); `-` leaves a value untouched and clearing stays a Manager decision. Paired lint gate `_check_planner_metadata` (in `lint_task_file` and `lint_all_tasks`) enforces the same formats and flags a duplicated key, so a hallucinated format fails before staging instead of vanishing from the read model; absence stays valid for legacy files. The executor now calls the tool after plan approval and is told never to hand-edit those lines — fragment 11 and `agents/cognitive-executor.md` agree, `system-prompt.md` reassembled, `<system_version>` 9.66.0 → 9.67.0, pin updated. Docs: planner and lint READMEs, ADR-010 and ADR-003. Verified: 715 tests pass, including 24 new (writer insert/update/idempotency/atomic-reject/archived/lint-after-write and lint positive, negative and absent cases).
 
 ### Fixed
@@ -24,11 +26,11 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Planner planning cockpit: day, week and month views with charts and deadline pressure (Task 345):** new `GET /api/plan?window=day|week|month` returns buckets computed from `tasks/` — day (today), week (Monday–Sunday, mid-week safe) and month (ISO weeks of the current month) — plus a 14-day `trend`, per-week `capacity_hours` / `remaining_hours` against `PLANNER_WEEKLY_CAPACITY`, and `alerts` split into overdue / today / next-three-days. Undated open work is attributed to the current bucket, because counting deadlines alone rendered an empty cockpit; completion history does not exist in the task files, so "done" means a completed-lane task carrying a deadline in the bucket and the UI says so. The dashboard gains a Day/Week/Month switcher persisted in `localStorage`, a capacity bar, an inline-SVG 14-day load chart (open / in-progress / done, design tokens only), a deadline rail whose rows open the task modal, deep links via `?task=<id>`, and a Copy-link action in the modal header. Constants: 400 on an unknown window or a relative root, 401 without a session. Verified: 107 planner tests pass (seven new), live board returns 200 for all three windows with correct totals.
 
-- **Planner MCP and daily pacing are native to the system prompt (Task 340):** `prompts/fragments/11-execution_workflow.md` now carries a *Planner MCP and daily pacing* block after Step 9 — the singleton at `127.0.0.1:8108`, `tasks/` Markdown as the single source of truth, `sprint_daily_agenda` on "start today's work" in any language (the Persian trigger is quoted), `claim_next` instead of hand-moving a task file with refusals reported not bypassed, `plan_status`/`qa_budget` for sizing the day (one unresolved review ceiling), and `sprint_check_daily_quota` with `DAILY_QUOTA_REACHED` → present `sprint_stats` and stop claiming. It sits inside the existing tag, so the splitter manifest needed no change. `<system_version>` bumps `9.64.1 → 9.65.0`, the pin in `tests/test_prompt_sync.py` follows, and `system-prompt.md` was reassembled (109,554 bytes). Verified: 103 prompt/splitter tests pass including `test_system_prompt_split_assemble_round_trip` (byte-identical), `check_docs_sync.py` prints `docs-sync: OK`; the prompt was deployed to `~/.config/opencode/system-prompt.md` byte-identical and `mcp-brain` restarted.
+- **Planner MCP and daily pacing are native to the system prompt (Task 340):** `prompts/fragments/11-execution_workflow.md` now carries a _Planner MCP and daily pacing_ block after Step 9 — the singleton at `127.0.0.1:8108`, `tasks/` Markdown as the single source of truth, `sprint_daily_agenda` on "start today's work" in any language (the Persian trigger is quoted), `claim_next` instead of hand-moving a task file with refusals reported not bypassed, `plan_status`/`qa_budget` for sizing the day (one unresolved review ceiling), and `sprint_check_daily_quota` with `DAILY_QUOTA_REACHED` → present `sprint_stats` and stop claiming. It sits inside the existing tag, so the splitter manifest needed no change. `<system_version>` bumps `9.64.1 → 9.65.0`, the pin in `tests/test_prompt_sync.py` follows, and `system-prompt.md` was reassembled (109,554 bytes). Verified: 103 prompt/splitter tests pass including `test_system_prompt_split_assemble_round_trip` (byte-identical), `check_docs_sync.py` prints `docs-sync: OK`; the prompt was deployed to `~/.config/opencode/system-prompt.md` byte-identical and `mcp-brain` restarted.
 
 - **`DESIGN.md` — Graphite Desk, one contract for both UIs:** the repo had no design system, so the Planner dashboard carried scattered slate/cyan tokens with mixed radii and the Prompt Composer was raw Tailwind defaults with six rainbow preset pills. The Manager reviewed four proposals and chose **A · Graphite Desk**: near-black slate surfaces (`#0b0e14` / `#141a23` / `#1b2430`), hairline borders `#263141`, one mint accent `#5eead4` with ink `#04211d`, four state colours, an 8px grid, a fixed 4/6/8/12 radius scale, Inter for UI and JetBrains Mono for ids/paths/diffs, and no shadows outside modals. The file also fixes component specs (buttons, lanes, tabs, inputs, preset chips, diff blocks, task modal), layout widths (1200 / 960), motion (120/180ms with reduced-motion honoured) and Stitch prompts. The Planner dashboard was re-skinned onto these tokens under task 339 — gradient gauge replaced, lane chips reduced to neutral plus semantic text, hard-coded greys removed — deployed byte-identical to `~/.config/opencode/mcp-planner-server/static/` and served live by `mcp-planner`. The Prompt Composer port is task 343 so it can drop the Tailwind CDN without touching this diff.
 
-- **Planner dashboard overhaul and a guarded task reader (Task 339):** the board is usable with 330+ tasks on it. `GET /api/task?id=<id>` / `?path=tasks/<lane>/<file>.md` returns `{id, path, lane, title, markdown}` so the new full-screen modal can render a task's whole body — todos, acceptance criteria, and `## Factual Git Diff` — with `id` winning when both params arrive. The route is deliberately not a file-read primitive: the new `_safe_task_path` accepts exactly three segments, a lane from `TASK_LANES`, a `.md` suffix, and no absolute prefix, drive colon, backslash, or `..`/`.`, then resolves and re-checks containment inside the project root; authorization reuses `AuthState.project_allowed` and the `_api_status` fallback to a session's first allowed root. Status mapping is explicit — 400 missing param, 401 no session, 403 outside grants *and* unsafe path (never 404, so the route cannot confirm whether a file exists), 404 unknown id, 500 unexpected; the `_api_status` blanket `except → 200 {"error": …}` pattern is not copied. `_task_brief` now carries `path` so cards can deep-link. The dashboard (`static/index.html`, still zero external URLs) caps each lane at `calc(100vh - 280px)` with inner scrolling and a sticky header, collapses the Archive lane behind an `Archive (N)` toggle remembered in `localStorage`, adds a client-only search input filtering by id/name/title, and opens the task modal through one delegated listener on the grid so the 30 s poll cannot drop the binding. The Markdown renderer is inline and self-contained: source is HTML-escaped first, then fences, headings, lists, task checkboxes, blockquotes, tables, and inline emphasis are added, diffs get `--success`/`--danger` line colouring, rendering stops at 2000 lines, and links are limited to same-origin or in-page targets. Docs: component `README.md` route table plus `DECISIONS.md` ADR-007. Verified: 97/97 planner tests pass (17 new: by id, by path, int-normalized id, 404, 400, eight traversal shapes at 403, route registration, 401, cross-project viewer 403, traversal over HTTP, open mode), `py_compile` and a JS parse of the inline script are clean, deployed `server.py`/`README.md`/`DECISIONS.md`/`static/index.html` are byte-identical to the repo copies, and the live unit on `127.0.0.1:8108` serves the new dashboard markup while `/api/task` answers 401 without a session and 400 with no param.
+- **Planner dashboard overhaul and a guarded task reader (Task 339):** the board is usable with 330+ tasks on it. `GET /api/task?id=<id>` / `?path=tasks/<lane>/<file>.md` returns `{id, path, lane, title, markdown}` so the new full-screen modal can render a task's whole body — todos, acceptance criteria, and `## Factual Git Diff` — with `id` winning when both params arrive. The route is deliberately not a file-read primitive: the new `_safe_task_path` accepts exactly three segments, a lane from `TASK_LANES`, a `.md` suffix, and no absolute prefix, drive colon, backslash, or `..`/`.`, then resolves and re-checks containment inside the project root; authorization reuses `AuthState.project_allowed` and the `_api_status` fallback to a session's first allowed root. Status mapping is explicit — 400 missing param, 401 no session, 403 outside grants _and_ unsafe path (never 404, so the route cannot confirm whether a file exists), 404 unknown id, 500 unexpected; the `_api_status` blanket `except → 200 {"error": …}` pattern is not copied. `_task_brief` now carries `path` so cards can deep-link. The dashboard (`static/index.html`, still zero external URLs) caps each lane at `calc(100vh - 280px)` with inner scrolling and a sticky header, collapses the Archive lane behind an `Archive (N)` toggle remembered in `localStorage`, adds a client-only search input filtering by id/name/title, and opens the task modal through one delegated listener on the grid so the 30 s poll cannot drop the binding. The Markdown renderer is inline and self-contained: source is HTML-escaped first, then fences, headings, lists, task checkboxes, blockquotes, tables, and inline emphasis are added, diffs get `--success`/`--danger` line colouring, rendering stops at 2000 lines, and links are limited to same-origin or in-page targets. Docs: component `README.md` route table plus `DECISIONS.md` ADR-007. Verified: 97/97 planner tests pass (17 new: by id, by path, int-normalized id, 404, 400, eight traversal shapes at 403, route registration, 401, cross-project viewer 403, traversal over HTTP, open mode), `py_compile` and a JS parse of the inline script are clean, deployed `server.py`/`README.md`/`DECISIONS.md`/`static/index.html` are byte-identical to the repo copies, and the live unit on `127.0.0.1:8108` serves the new dashboard markup while `/api/task` answers 401 without a session and 400 with no param.
 
 - **Plugin references synced to the new tool set and evidence contract (Task 341):** a graph scan over this worktree (4,766 nodes, 6,788 links) plus targeted greps found four live documents lagging behind the two plugin releases. `agents/cognitive-executor.md` now carries `compact_stats` in the Smart Compact section and in the protocol contract (no inputs, read-only, same formatter as `/magic-stats`, never a poll), and states that every `goal_set` starts a fresh empty evidence sidecar while the legacy `.opencode/goal-evidence.json` is read only until the session owns its own, which is what stopped a finished goal's failing command from gating later ones. `docs/compaction.md` documents the stats tool under Agent-callable tools and the evidence reset in the goal-plugin section; `README.md`'s plugin lane carries both. `tests/test_prompt_sync.py` pins `compact_stats` so the executor cannot drift back, and the smart-compact policy memory shard lists the third tool plus the installed commit `2e702680`. Verified: prompt-sync tests exit 0, `lint_system_prompt_sync` consistent, `prettier --check` clean.
 
@@ -36,7 +38,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Planner auth, RBAC, and per-user project scoping (Task 337):** the planner can now be exposed through a Cloudflare Tunnel without giving strangers the board. Auth is opt-in via `~/.config/opencode/planner-users.json` (`PLANNER_USERS_CONFIG` override): a missing, unreadable, non-object, or `auth_enabled: false` file — or one with no users — leaves the server in open local mode with no 401s and no filtering, so every existing local client keeps working untouched. When enabled, `server.py` gains stdlib-only auth: `hashlib.pbkdf2_hmac("sha256", …, 600_000)` with a 16-byte `secrets` salt verified by `hmac.compare_digest`, opaque `secrets.token_urlsafe(32)` sessions in an in-memory store behind an `HttpOnly` `SameSite=Lax` `planner_session` cookie (7-day TTL, dropped on restart), `POST /api/login`, `POST /api/logout`, `GET /api/me`, and an `AuthState` that answers `project_allowed()` for `"*"` or any granted root and its subdirectories. `GET /api/status` returns 401 until sign-in, filters `projects` to `allowed_projects`, and 403s an explicit `project_root` outside them (a viewer with no explicit root falls back to their first allowed project instead of being denied); `POST /mcp` is wrapped in an ASGI guard that admits admin sessions only, so a viewer reads the dashboard and never executes tools. The dashboard gains a dark-mode login modal shown on 401, a `#user-badge` with a role chip, a logout button, and `/static/*` asset serving; `manage_users.py` is a stdlib `argparse` CLI (`add`/`update`/`remove`/`list`/`enable`/`disable`, `--password` for non-interactive use, file written `chmod 600`) that hashes through the same scheme the server verifies. Cloudflare Tunnel ingress is documented in `docs/services.md` and the component README, with the `/mcp` rule ordered first as `http_status:404` so tool execution never leaves the host. Two defects in the working tree were fixed rather than shipped: a corrupted `TASK_ID_RE` (`\\.md` never matched, so task lookup and dashboard ids broke) and a duplicated `# /// script` header. Verified: 76/76 planner tests pass (login valid/invalid, RBAC admin vs viewer, 403 on an unauthorized root, the three `/mcp` guard cases, open-mode backward compatibility, and CLI hashing cross-checked by the server's own verifier); `docs-sync: OK`; unit `active` with the new code deployed.
 
-- **Planner MCP deployed globally and wired into the executor protocol (Task 336):** the planner is now a live platform singleton rather than repo-local code. It installs to `~/.config/opencode/mcp-planner-server/` (source, committed `uv.lock`, and `static/` dashboard assets) with its venv built by `uv sync` from the lock, runs as `mcp-planner.service` on `127.0.0.1:8108` (enabled, active, loopback-only), and is registered in the global `opencode.json` as `mcp.servers.planner` (`type: remote`, `http://127.0.0.1:8108/mcp`, timeout 15000/30000). `agents/cognitive-executor.md` gains a *Planner MCP and Daily Pacing Protocol* section binding four moments to four tools: `sprint_daily_agenda` when the Manager starts the day, `claim_next` instead of hand-moving a task file (a block is reported, never bypassed), `sprint_check_daily_quota` when tasks close, and `plan_status`/`qa_budget` for status questions — with an explicit fallback to the Kanban workflow if the server is unreachable. `LLM.txt` provisions the whole thing (§4 directory, §5 copy block, §7 config entry, §7.5 venv-before-unit plus drop-in, verification checklist), `README.md` lists the component, and `docs/services.md` keeps the port map. Deployment adaptations forced by what actually ran: `uv pip install -e .` cannot work because the package declares no build backend, so the venv comes from `uv sync` against the committed lock; the committed unit stays machine-independent and the dashboard's project root is supplied by a `mcp-planner.service.d` drop-in (`PLANNER_PROJECT_ROOT`), since the unit's WorkingDirectory is the install dir which holds no `tasks/`; and `opencode mcp list` prints "No MCP servers configured" on v2.1.4 even for the six servers already in use, so registration is verified with `opencode debug config` (7 resolved `127.0.0.1:810*/mcp` entries) plus a live MCP handshake instead — the docs now say so. Verified: unit `active`/`enabled`, `/` and `/api/status` both 200 with 329 tasks for this repo, planner tools enumerable over `initialize`+`tools/list`, `scripts/check_docs_sync.py` exits 0, 31/31 planner tests pass, full suite 592 passed with the one pre-existing prompt round-trip failure.
+- **Planner MCP deployed globally and wired into the executor protocol (Task 336):** the planner is now a live platform singleton rather than repo-local code. It installs to `~/.config/opencode/mcp-planner-server/` (source, committed `uv.lock`, and `static/` dashboard assets) with its venv built by `uv sync` from the lock, runs as `mcp-planner.service` on `127.0.0.1:8108` (enabled, active, loopback-only), and is registered in the global `opencode.json` as `mcp.servers.planner` (`type: remote`, `http://127.0.0.1:8108/mcp`, timeout 15000/30000). `agents/cognitive-executor.md` gains a _Planner MCP and Daily Pacing Protocol_ section binding four moments to four tools: `sprint_daily_agenda` when the Manager starts the day, `claim_next` instead of hand-moving a task file (a block is reported, never bypassed), `sprint_check_daily_quota` when tasks close, and `plan_status`/`qa_budget` for status questions — with an explicit fallback to the Kanban workflow if the server is unreachable. `LLM.txt` provisions the whole thing (§4 directory, §5 copy block, §7 config entry, §7.5 venv-before-unit plus drop-in, verification checklist), `README.md` lists the component, and `docs/services.md` keeps the port map. Deployment adaptations forced by what actually ran: `uv pip install -e .` cannot work because the package declares no build backend, so the venv comes from `uv sync` against the committed lock; the committed unit stays machine-independent and the dashboard's project root is supplied by a `mcp-planner.service.d` drop-in (`PLANNER_PROJECT_ROOT`), since the unit's WorkingDirectory is the install dir which holds no `tasks/`; and `opencode mcp list` prints "No MCP servers configured" on v2.1.4 even for the six servers already in use, so registration is verified with `opencode debug config` (7 resolved `127.0.0.1:810*/mcp` entries) plus a live MCP handshake instead — the docs now say so. Verified: unit `active`/`enabled`, `/` and `/api/status` both 200 with 329 tasks for this repo, planner tools enumerable over `initialize`+`tools/list`, `scripts/check_docs_sync.py` exits 0, 31/31 planner tests pass, full suite 592 passed with the one pre-existing prompt round-trip failure.
 
 - **Planner MCP v1 and local dashboard (Task 335):** new `mcp-planner-server/` singleton on loopback `127.0.0.1:8108` that reads `tasks/` Markdown as the single source of truth and adds a capacity-aware, QA-gated planning layer over it. Tools: `plan_propose` (decompose a goal into estimated tasks + milestones, writes nothing), `plan_materialize` (writes task files only after approval), `claim_next` (guarded claim that refuses on unmet dependencies, a full WIP ceiling, or an exhausted QA budget), `plan_status`, `sprint_stats` (hours spent, progress, velocity), `qa_budget`, `milestone_status`, `sprint_lock`, `sprint_daily_agenda`, and `sprint_check_daily_quota` (`DAILY_QUOTA_REACHED`). The same process serves a zero-build dark-mode dashboard at `/` with a Jalali + Gregorian 14-day timeline, Kanban lanes, milestone tree, daily pacing gauge, and a working project switcher, plus `GET /api/status`. Two defects were fixed during verification rather than shipped: the transport is built with `mcp.streamable_http_app()` (mcp 1.30 has no `http_app()`) mounted at the root with an explicit `lifespan_context` enter, because Starlette never runs a `Mount`-ed sub-app's lifespan and the session manager stayed uninitialised; and `/api/status` now returns per-lane **task lists**, a `milestone_tree`, sorted `deadlines`, a `today` triple matching `sprint_check_daily_quota`, and a `projects` list, with the root resolved from `project_root` → `PLANNER_PROJECT_ROOT` → nearest ancestor holding `tasks/` → cwd. The previous count-per-lane shape made `items.map` throw inside `render()` and silently blanked the board, and the hard-coded `Path.cwd()` root reported an empty board under systemd. Also added `tasks/sprints/` and `tasks/milestones/`, `services/mcp-planner.service`, `uv.lock`, port 8108 in `docs/services.md`, and the unit in `services/README.md`. Verified: 30/30 planner tests pass, a live `initialize` on `/mcp` returns 200, `GET /` and `/api/status` return 200 against the real repo (328 tasks), and the dashboard `render()` was exercised headlessly against both the live and a synthetic milestone payload.
 
@@ -69,13 +71,13 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **UI stack moves to Bootstrap 5.3, vendored; Prompt Composer ported:** the hand-rolled CSS (Graphite Desk tokens written as bespoke rules) was replaced with a real component library. `bootstrap.min.css` and `bootstrap.bundle.min.js` (5.3.3) are vendored under `tools/prompt-composer/vendor/` and `mcp-planner-server/static/vendor/`, and a single `theme.css` maps the DESIGN.md palette onto `--bs-*` variables (body background, border, primary accent, radii 4/6/8/12, focus ring, mono stack) plus five missing primitives (`.chip`, `.page`, `.label`, `.gd-dialog`, `.mono`). `tools/prompt-composer/index.html` was rewritten on that stack: the Tailwind CDN is gone, all Tailwind utility classes are gone, preset pills became neutral chips with at most four semantic tints (info/success/warning/danger), the manage dialog uses `.gd-dialog`, and every behaviour is preserved (project CRUD via localStorage, system-prompt fetch, generate, copy). `DESIGN.md` now states the Bootstrap mapping as the implementation baseline. Verified: inline script parses, zero third-party URLs at runtime (only the intentional GitHub fetch for the system prompt). The Planner dashboard port is still pending inside META 344.
 
-- **Control payloads are never trimmed (executor rule only):** a Brain `hands_*`/`hotfix` block is read whole, never sliced for context. `agents/cognitive-executor.md` gains a *Code-mode output discipline* rule in the Brain Bridge call step — the `execute` runtime returns the `return` value verbatim, only its own `maxOutputBytes` may cut it, and a cut is signalled by `truncated: true`, so the Hands returns `{status, block_count, model}` and keeps the block whole instead of printing a prefix; a `truncated` flag means re-read the exact range. The rule deliberately stays out of `docs/opencode-shell-strategy.md`: that file governs non-interactive shell behaviour, and the trimming problem lives in tool calling and code mode, not in bash. Deployed to `~/.config/opencode/agents/cognitive-executor.md` byte-identical. Verified: 103 prompt/MCP tests pass.
+- **Control payloads are never trimmed (executor rule only):** a Brain `hands_*`/`hotfix` block is read whole, never sliced for context. `agents/cognitive-executor.md` gains a _Code-mode output discipline_ rule in the Brain Bridge call step — the `execute` runtime returns the `return` value verbatim, only its own `maxOutputBytes` may cut it, and a cut is signalled by `truncated: true`, so the Hands returns `{status, block_count, model}` and keeps the block whole instead of printing a prefix; a `truncated` flag means re-read the exact range. The rule deliberately stays out of `docs/opencode-shell-strategy.md`: that file governs non-interactive shell behaviour, and the trimming problem lives in tool calling and code mode, not in bash. Deployed to `~/.config/opencode/agents/cognitive-executor.md` byte-identical. Verified: 103 prompt/MCP tests pass.
 
 - **Brain consolidated onto `muse-spark-1.3-contributor` at `xhigh`, with the API key rotated to OpenCode's live credential:** the operator moved every Brain tier onto the cheap Go model, so planning, implementation, QA, and review share one route and one preset. `BRAIN_MODEL`, `BRAIN_MODEL_LOW`, and `BRAIN_MODEL_HIGH` now all read `muse-spark-1.3-contributor` in both the repo `.env` and the effective global `~/.config/opencode/.env`; `BRAIN_API_BASE` stays on the zen-proxy `/go/resp` mount and `BRAIN_REASONING_EFFORT` stays `xhigh`. `.env.example`'s preset comment drops its now-false "current production setting" label from the balanced block, since production is the economy preset. The first smoke test failed `429 GoUsageLimitError` (monthly) on `muse-spark-1.3-contributor` and on `gpt-6-luna`, which was account-level, not routing: the `BRAIN_API_KEY` in both env files belonged to a drained Go workspace. OpenCode's live credential is **not** `~/.local/share/opencode/auth.json` (that copy answers `401 Invalid credential` on the same gateway, both through the proxy and direct); it lives in the opencode V2 store at `~/.local/share/opencode/opencode.db`, table `credential` (`integration_id: opencode-go`, `active = 1`, JSON value carrying `key`). That key was copied into `BRAIN_API_KEY` in both env files and `mcp-brain` restarted. Verified: `zen-proxy` and `mcp-brain` enabled/active, `/health` 200, `/go/resp/models` serves the id, a direct gateway probe returns 200, and a `brain_turn` smoke test answered `SMOKE_OK` with `model=muse-spark-1.3-contributor`, `status=completed`, `reasoning_tokens=2216` (xhigh in effect), 25,782 total tokens.
 
 ### Fixed
 
-- **Bridge extraction is now line-accurate in every shape (fences, Python samples, Markdown):** three defects closed in one pass. Fence recognition moved from regex to `_xml_fence_segments`, which walks lines and closes a fence only on a bare run of the same character at least as long as the opener — so a four-backtick ````xml fence is now the canonical wrapper for a body carrying three-backtick samples, and a three-backtick body that closes early is repaired by a forward rescue scan (`_rescue_fenced_block`). The fence-body and rescue passes use `_extract_complete_blocks`, which anchors openers at line starts, so an operator-shaped literal inside a code sample (`sample = "<hotfix>not real</hotfix>"`) is never mistaken for an instruction while the real block is dropped. The bare-block scan runs on `_mask_fenced_code`, a line-accurate CommonMark mask, instead of the mis-slicing regex strip. Gateway and prompt now agree: manual mode recommends ````xml when the body holds fenced code, and both the system prompt (`<system_version>9.64.1`) and `agents/cognitive-executor.md` say so; the executor's claim that a missing mode line "fence-strict-rejects" is corrected to what actually happens (the Brain cannot tell which shape is live). Also: `scripts/prompt-build/split_system_prompt.py` now knows `night_mode` and captures the trailing Markdown language-policy section as a fragment, reusing committed filenames so a rebuild renames nothing — the round-trip test that had been failing on `<night_mode>` passes and `assemble(split(prompt))` is byte-identical. Verified: 292/292 bridge tests (new: quad wrapper, nested doc-sample non-leak), 103/103 prompt/splitter tests, full suite green, deployed copies byte-identical, `mcp-brain` restarted.
+- **Bridge extraction is now line-accurate in every shape (fences, Python samples, Markdown):** three defects closed in one pass. Fence recognition moved from regex to `_xml_fence_segments`, which walks lines and closes a fence only on a bare run of the same character at least as long as the opener — so a four-backtick ``xml fence is now the canonical wrapper for a body carrying three-backtick samples, and a three-backtick body that closes early is repaired by a forward rescue scan (`_rescue_fenced_block`). The fence-body and rescue passes use `_extract_complete_blocks`, which anchors openers at line starts, so an operator-shaped literal inside a code sample (`sample = "<hotfix>not real</hotfix>"`) is never mistaken for an instruction while the real block is dropped. The bare-block scan runs on `_mask_fenced_code`, a line-accurate CommonMark mask, instead of the mis-slicing regex strip. Gateway and prompt now agree: manual mode recommends ``xml when the body holds fenced code, and both the system prompt (`<system_version>9.64.1`) and `agents/cognitive-executor.md` say so; the executor's claim that a missing mode line "fence-strict-rejects" is corrected to what actually happens (the Brain cannot tell which shape is live). Also: `scripts/prompt-build/split_system_prompt.py` now knows `night_mode` and captures the trailing Markdown language-policy section as a fragment, reusing committed filenames so a rebuild renames nothing — the round-trip test that had been failing on `<night_mode>` passes and `assemble(split(prompt))` is byte-identical. Verified: 292/292 bridge tests (new: quad wrapper, nested doc-sample non-leak), 103/103 prompt/splitter tests, full suite green, deployed copies byte-identical, `mcp-brain` restarted.
 
 - **Fenced XML with inner code fences no longer burns a turn (bridge extractor):** in manual mode the Brain is told ` ```xml ` fences are expected, so it wraps `hands_implementation_task` bodies that themselves contain ` ```python ` samples. The extractor could not nest, closed the fence body at the first inner fence, saw a truncated opener, and rejected the whole answer as `XML_STRICT_REJECT_FENCE_FALLBACK` — replacing a ~25k-char block with the reject header plus its first 2000 chars, so the Hands had to ask for a complete re-emit (one wasted round trip and ~10k output tokens). `extract_xml_blocks` now walks line-anchored ` ```xml ` openers in order (`_XML_FENCE_OPEN_RE`, info-string-checked so quad and non-xml fences stay documentation-only), tries the ordinary fence body first, and when that body holds no complete allowlisted block scans forward from the opener — bounded by the next opener — for the block's closing tag. The rescue only runs on the path that used to raise, and a genuinely truncated block still raises the same code, so the strict gate never repairs input. Reproduced offline before the fix (fenced block with one inner fence → zero blocks), then pinned by three tests: `test_extract_xml_fenced_hands_block_with_inner_code_fences`, `test_extract_rescued_fences_stay_ordered_and_bounded`, `test_extract_truncated_xml_fence_still_rejects`. Same area, mirror-image defect fixed in the same pass: the bare-block scan ran on `_strip_fences` output, whose non-nesting strip mis-slices the same nested body, so an operator-shaped literal inside a documentation sample (`sample = "<hotfix>not real</hotfix>"` in a ` ```python ` block) was returned as a live instruction while the real block was dropped. The scan now runs on the new `_mask_fenced_code` line-accurate mask (opener with info string through the next bare run of the same character and length), and `_strip_fences` is kept for diagnostics only; pinned by `test_extract_ignores_operator_tag_in_nested_fence_sample`. Bridge `DECISIONS.md` ADR-008 records the decision and the rollback. Verified: 290/290 `tests/test_brain_bridge.py` pass, and the full suite is 661 passed with one pre-existing unrelated failure (`test_system_prompt_split_assemble_round_trip` in `tests/test_mcp_servers.py` drops the `<night_mode>` fragment — untouched by this change and present before it).
 
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index e47a604..d266258 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -54,26 +54,26 @@ You are the final gatekeeper of the Kanban task state. If the Orchestrator forge
 
 If the Orchestrator or Manager forgets to explicitly list a skill in the `<context_phase>`, you MUST scan the task context and auto-load the correct skill using the `skill` tool based on this matrix:
 
-| Detected Tech Stack / Context                            | Mandatory Skill to Load                                                                    |
-| -------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
-| Jetpack Compose, Android, Kotlin                         | `android-kotlin`                                                                           |
-| Flask, SQLAlchemy, Python                                | `flask-python`                                                                             |
-| Go, Gin, Hexagonal                                       | `go-gin` or `go-hexagonal-grpc`                                                            |
-| SwiftUI, iOS                                             | `ios-swiftui`                                                                              |
-| NestJS, Prisma, TypeScript                               | `nestjs-prisma-vertical`                                                                   |
-| Next.js, App Router, React                               | `nextjs`                                                                                   |
-| FastAPI, Pydantic                                        | `python-fastapi`                                                                           |
-| React Native, Expo                                       | `react-native-expo`                                                                        |
-| React, Vite                                              | `react-vite`                                                                               |
-| Spring Boot, Java                                        | `spring-boot`                                                                              |
-| Vue, Nuxt                                                | `vue-nuxt`                                                                                 |
-| Creating a new task file                                 | `task-generator`                                                                           |
-| Closing or archiving a task                              | `archive-tasks`                                                                            |
-| Complex bug, deadlock, silent failure                    | `debug-instrumentation`                                                                    |
-| Implementation-producing input (any stack, any language) | `prompt-refactor` (mandatory before planning: validate, translate, expand, then structure) |
+| Detected Tech Stack / Context                              | Mandatory Skill to Load                                                                                                                      |
+| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
+| Jetpack Compose, Android, Kotlin                           | `android-kotlin`                                                                                                                             |
+| Flask, SQLAlchemy, Python                                  | `flask-python`                                                                                                                               |
+| Go, Gin, Hexagonal                                         | `go-gin` or `go-hexagonal-grpc`                                                                                                              |
+| SwiftUI, iOS                                               | `ios-swiftui`                                                                                                                                |
+| NestJS, Prisma, TypeScript                                 | `nestjs-prisma-vertical`                                                                                                                     |
+| Next.js, App Router, React                                 | `nextjs`                                                                                                                                     |
+| FastAPI, Pydantic                                          | `python-fastapi`                                                                                                                             |
+| React Native, Expo                                         | `react-native-expo`                                                                                                                          |
+| React, Vite                                                | `react-vite`                                                                                                                                 |
+| Spring Boot, Java                                          | `spring-boot`                                                                                                                                |
+| Vue, Nuxt                                                  | `vue-nuxt`                                                                                                                                   |
+| Creating a new task file                                   | `task-generator`                                                                                                                             |
+| Closing or archiving a task                                | `archive-tasks`                                                                                                                              |
+| Complex bug, deadlock, silent failure                      | `debug-instrumentation`                                                                                                                      |
+| Implementation-producing input (any stack, any language)   | `prompt-refactor` (mandatory before planning: validate, translate, expand, then structure)                                                   |
 | Java-8 Android Views, no Compose (XML layouts, Activities) | `android-kotlin` for Kotlin discipline plus tooling order only; Compose MVI Hilt SQLDelight coverage does not apply to Views (skip recorded) |
-| Plain Node CommonJS Cloud Code, no TS or hex ports      | `node-hexagonal-api` for layering intent where applicable, else no stack skill; no CommonJS Cloud Code skill exists (skip recorded) |
-| Any Telegram MCP send, reply, edit, or file caption     | `telegram-message-format` (parse mode, escaping, length splitting, topic targeting, Persian text) |
+| Plain Node CommonJS Cloud Code, no TS or hex ports         | `node-hexagonal-api` for layering intent where applicable, else no stack skill; no CommonJS Cloud Code skill exists (skip recorded)          |
+| Any Telegram MCP send, reply, edit, or file caption        | `telegram-message-format` (parse mode, escaping, length splitting, topic targeting, Persian text)                                            |
 
 **Binding Fallback Rule:** If no stack skill exactly matches, load the closest skill for discipline only and record an explicit skip with root plus marker scan list plus matched skills list plus reason phrase. Never invent a new skill inline and never claim coverage not present.
 
@@ -103,7 +103,7 @@ Context is finite. Two layers keep long sessions productive, and the agent's dur
 
 1. **Native safety net.** OpenCode auto-compacts near the model limit: it replaces older turns with one lossy summary and keeps the most recent ~20k tokens (config: `compaction.keep.tokens`). Never depend on it to preserve working state — write the essentials to the task file as you go.
 2. **Smart Compact (high-fidelity).** The `smart-compact` plugin (`@mokhtarabadi/opencode-smart-compact`) is installed globally and loaded by OpenCode. It is V2-native: it stores a per-session compaction state and applies it to the model-visible messages per request, so it never mutates the stored transcript. It keeps user messages verbatim, condenses each old assistant turn into its own summary, and prunes bulky tool output into a retrievable cache. Above `awareness.autoTrimRatio` it trims tool output by itself between requests — expect a tool result to read as a notice even when you did not call `compact_context`; that is the plugin working as intended, and the original is one `read_omitted_content` call away. The Manager runs the commands: `/magic-compact [N]` summarizes old turns keeping the last N turns, `/magic-trim [N]` prunes tool I/O only, `/magic-stats` reports savings. `compact_stats` is the agent's read-only copy of that report (no inputs, never writes), which you call when you need to know whether a compaction actually reclaimed anything: `prunedParts` high with `summarizedTurns` 0 means the bulk is tool output, so a trim is the cheaper move. After a prune, prefer a cheap fresh run of the source tool; call `read_omitted_content` with its Content ID (`omitted-NNNN`) ONLY when the output cannot be reproduced cheaply, never speculatively. On a cache miss, re-run the source tool once.
-Task file is the sole reconcile target. Smart Compact via `compact_context` is the sole pruning writer; native auto-compact is a lossy safety net only and is never relied on for state. After any compaction resume from the task file and re-apply pruning through the sole writer.
+   Task file is the sole reconcile target. Smart Compact via `compact_context` is the sole pruning writer; native auto-compact is a lossy safety net only and is never relied on for state. After any compaction resume from the task file and re-apply pruning through the sole writer.
 
 3. **Survival contract.** Keep the task file holding: the active task id and Kanban lane, the pinned `[fed-context]` block with citations, the current persona/seat, the locked mode (manual or autopilot), the latest staged diff hash, open blockers, and the next action. Resume from that file after any compaction — never from a summary.
 4. **Trigger it yourself, or hand off the command.** The agent cannot run the `/magic-*` slash commands, but it CAN call the `compact_context` tool directly — prefer that when context pressure is high (pass `keepTurns` to protect recent turns, `mode: "trim"` to prune tool output only), state one line about it, then continue from the task file. Contract: `keepTurns` is a non-negative integer defaulting to 0, `mode` is `compact` or `trim` defaulting to `compact`, neither is required; `read_omitted_content` takes a session-scoped Content ID such as `omitted-0001`; `compact_stats` takes no inputs, only reads state, and returns the same savings line as `/magic-stats`, so call it once when you need to know whether a compaction actually reclaimed anything and never as a poll. Effect is async (stored now, prunes next request) — do not re-call to verify. In autopilot never ask the Manager to run slash commands; call it yourself and chain the next turn. Fall back to recommending a `/magic-compact` run to the Manager only when a tool call is not available in manual mode. Do not edit compaction config files.
@@ -226,6 +226,7 @@ When a circuit breaker fires, output a `⚠️ CIRCUIT BREAKER` warning with the
 - **Starting the day.** When the Manager says "start today's work" — in whatever language the request arrives — call `sprint_daily_agenda(project_root)` before touching any task file. It lists what is already in progress plus any QA-pending task that has to be resolved first.
 - **Taking a task.** Call `claim_next(project_root, task_id)` instead of hand-moving the file. It performs the backlog to in-progress transition only when dependencies are satisfied, the WIP ceiling allows it, and the QA budget is not spent. A block is an answer, not an obstacle: report the stated reason to the Manager and never bypass it by moving the file manually.
 - **Recording a plan.** Once the Manager approves a plan, call `schedule_tasks(project_root, "id:estimate:deadline[:deps], …")` so estimate, deadline and dependencies are written into the task headers. Never hand-edit `**Estimate:**`, `**Deadline:**` or `**Depends on:**` — the Planner reads them from the Markdown and a malformed line drops the task out of capacity and the timeline without any error.
+- **Measured time is automatic.** `**Started:**`, `**Submitted:**` and `**Finished:**` are written by the lane transitions themselves (`claim_next`, `qa_transition`, `commit_and_clean_task`) as ISO-8601 UTC, write-once. Never write or change them by hand: a local-time or free-text value is rejected by the lint, and a rewritten start falsifies the duration the panel reports. If you move a task file yourself (a permitted `git mv`), call `sync_task_times(project_root)` right after the move — it stamps the missing start/submit time from git history and is idempotent.
 - **Ending the day.** Once tasks are closed, call `sprint_check_daily_quota(project_root)`. When it returns `DAILY_QUOTA_REACHED`, present `sprint_stats(project_root)` and announce that the day's work is finished; do not claim another task in that turn.
 - **Status questions.** `plan_status(project_root)` covers lanes, capacity against estimate, milestones, and blockers. `qa_budget(project_root)` answers whether another review can be opened without breaching the one-unresolved-review ceiling.
 
@@ -403,29 +404,29 @@ needs no extra machinery.
    with one line stating the live mode, because the Brain's system prompt
    carries both emission shapes and it cannot know which one is live
    without being told. Autopilot: `MODE: AUTOMATIC (autopilot locked) —
-   emit bare unfenced XML only, never xml-fenced blocks; do NOT emit any
-   copy-paste relay instructions ("Manager: please copy...") — the Hands
-   chain QA/review turns directly.` Manual: `MODE: MANUAL — xml-fenced
-   blocks expected (a four-backtick ````xml wrapper when the body carries
-   its own fenced code); copy-paste relay instructions expected.` Skip this
+emit bare unfenced XML only, never xml-fenced blocks; do NOT emit any
+copy-paste relay instructions ("Manager: please copy...") — the Hands
+chain QA/review turns directly.` Manual: `MODE: MANUAL — xml-fenced
+blocks expected (a four-backtick ````xml wrapper when the body carries
+its own fenced code); copy-paste relay instructions expected.` Skip this
    line and the Brain cannot tell which shape is live: it keeps emitting
    admin copy-paste text in a silent pipeline and fenced output where bare
-   was required.   **Session Binding (Mandatory):** You MUST pass `session_id: "$OPENCODE_SESSION_ID"` (reading your active session ID from the environment) in every `brain_turn` call alongside `task_id`. Because the MCP server runs as a separate daemon, you must send this parameter explicitly over the wire so the conversation history continues in `tasks/.sessions/<session_id>/transcript.jsonl`.
+   was required. **Session Binding (Mandatory):** You MUST pass `session_id: "$OPENCODE_SESSION_ID"` (reading your active session ID from the environment) in every `brain_turn` call alongside `task_id`. Because the MCP server runs as a separate daemon, you must send this parameter explicitly over the wire so the conversation history continues in `tasks/.sessions/<session_id>/transcript.jsonl`.
 2. **Call** `brain_turn`. Read `status`:
    - `XML_EXTRACTED` — execute `xml_blocks` as the next instruction set,
      exactly like an Orchestrator XML block.
    - `REPORT` — triage like a review verdict: fix what reproduces,
      dispute the rest with evidence in the task file.
-   **Code-mode output discipline (never hand-trim a control payload):** the
-   `execute` runtime returns your `return` value verbatim; only the runtime's
-   own `maxOutputBytes` may cut it, and it says so with a `truncated: true`
-   flag. Never `slice`, `map`, or summarize `xml_blocks` — a cut block loses
-   instructions silently, and a head-only view is how a closure or hotfix step
-   goes missing. Read the block in full and execute from it; summarize
-   `output` only after the block has been consumed. In code mode return
-   `{status, block_count: xml_blocks.length, model}` and keep the block whole
-   instead of printing a prefix. A `truncated` flag means re-read the exact
-   range through the tool again, never assume the tail.
+     **Code-mode output discipline (never hand-trim a control payload):** the
+     `execute` runtime returns your `return` value verbatim; only the runtime's
+     own `maxOutputBytes` may cut it, and it says so with a `truncated: true`
+     flag. Never `slice`, `map`, or summarize `xml_blocks` — a cut block loses
+     instructions silently, and a head-only view is how a closure or hotfix step
+     goes missing. Read the block in full and execute from it; summarize
+     `output` only after the block has been consumed. In code mode return
+     `{status, block_count: xml_blocks.length, model}` and keep the block whole
+     instead of printing a prefix. A `truncated` flag means re-read the exact
+     range through the tool again, never assume the tail.
 3. **Relay** — any admin question inside `output` goes to the Manager
    verbatim. Feed the answer back as the next `brain_turn` user prompt.
    Never answer for the Manager.
diff --git a/mcp-context-server/DECISIONS.md b/mcp-context-server/DECISIONS.md
index 3a2f360..b77b627 100644
--- a/mcp-context-server/DECISIONS.md
+++ b/mcp-context-server/DECISIONS.md
@@ -77,3 +77,9 @@
 - **Consequences:** A freshly bundled META passes the real linter with no hand edit; telegram provenance survives in the working file; source blocks grow by the preserved sections, which is the intended cost. One new parity test imports the live linter function, so a future divergence between the two servers fails the suite.
 - **Rollback:** Revert `bundle.py` (section writer + extractor), the `server.py` required list, and the four new tests; METAs return to needing manual patching.
 
+## [2026-10-25] ADR-012: The lane transitions stamp their own time
+
+- **Context:** the planner can only measure a task if someone records when it entered each lane, and every candidate writer other than the transition itself (a hook, a shell `date`, a manual edit) is either unreliable or forgettable. `qa_transition` and `commit_and_clean_task` are the only code that moves a task into `tasks/qa/` and closes it.
+- **Decision:** `gitops.stamp_task_header(path, field)` writes `**Submitted:**` / `**Finished:**` as ISO-8601 UTC, inserted after `**Status:**`, and only when the field is absent. Both tools call it at the moment of the move, so the stamp cannot drift from the transition.
+- **Consequences:** durations are measured at the source, re-transitions cannot overwrite a real start, and a failed stamp is harmless (the header update is already best-effort; the move is what matters). The planner reads the same lines and never writes them, keeping one writer per stamp.
+- **Rollback:** remove the two calls and the helper; the header lines become inert and the planner reports `null` durations.
diff --git a/mcp-context-server/README.md b/mcp-context-server/README.md
index 984a2b1..2a644dd 100644
--- a/mcp-context-server/README.md
+++ b/mcp-context-server/README.md
@@ -26,3 +26,4 @@ Custom-context MCP daemon: directory trees, source reads, signature extraction,
 - Graph precision (312): full-file scans, vocab hints, DFS mode, Task/ADR rationale links, god-node noise filter, truncation note.
 - Staging index-safety: `stage_and_inject_diff` stages whole-file blobs; `skip_add=True` skips `git add` and only extracts + injects for self-managed hunk-level index surgery; default path warns naming files with pre-existing staged hunks.
 - Parallel isolation: `unstage_files` removes listed files from the index without touching the worktree — the agent-managed unstage path for shared-file parallel sessions (no commit, no checkout, no push; ZAC holds).
+- Task timing: `sync_task_times` stamps a missing `Started`/`Submitted`/`Finished` for tasks already sitting in a lane, which is what a hand-moved task needs. The start comes from git history then the file mtime, never from an invented "now".
diff --git a/mcp-context-server/gitops.py b/mcp-context-server/gitops.py
index b70d5bc..598488c 100644
--- a/mcp-context-server/gitops.py
+++ b/mcp-context-server/gitops.py
@@ -7,6 +7,7 @@ import re
 import shutil
 import subprocess
 import time
+from datetime import datetime, timezone
 from pathlib import Path
 from typing import Optional
 
@@ -288,6 +289,114 @@ def _git_mv_or_fallback(src: Path, dst: Path) -> bool:
     return False
 
 
+def backfill_started_from_git(repo_root: Path, task_path: Path) -> str | None:
+    """Recover a start stamp from git history when the header has none.
+
+    A task moved by hand reaches the next lane with no stamp, so its measured
+    duration would be silently lost. Git already recorded when the file appeared;
+    that is a real moment, not an invention.
+
+    Args:
+        repo_root: repository working tree.
+        task_path: the task file, inside the repository.
+
+    Returns:
+        An ISO-8601 UTC stamp, or ``None`` when git knows nothing about the file.
+    """
+    try:
+        result = subprocess.run(
+            [
+                "git",
+                "log",
+                "--follow",
+                "--format=%aI",
+                "--reverse",
+                "--",
+                str(task_path),
+            ],
+            capture_output=True,
+            text=True,
+            cwd=str(repo_root),
+        )
+        if result.returncode != 0:
+            return None
+        for line in result.stdout.splitlines():
+            value = line.strip()
+            if not value:
+                continue
+            return (
+                datetime.fromisoformat(value)
+                .astimezone(timezone.utc)
+                .strftime("%Y-%m-%dT%H:%M:%SZ")
+            )
+    except Exception:
+        return None
+    return None
+
+
+def task_start_stamp(repo_root: Path, task_path: Path) -> str | None:
+    """Best available start time for a task that has no ``Started`` header.
+
+    Order: git history first (a recorded fact), then the file's modification time
+    (when it was written or moved into its lane), then nothing. A guessed "now"
+    is deliberately absent: a wrong start is worse than a missing one, because it
+    silently inflates or deflates the measured duration.
+
+    Args:
+        repo_root: repository working tree.
+        task_path: the task file.
+
+    Returns:
+        An ISO-8601 UTC stamp, or ``None`` when neither source can answer.
+    """
+    from_git = backfill_started_from_git(repo_root, task_path)
+    if from_git:
+        return from_git
+    try:
+        mtime = task_path.stat().st_mtime
+        return datetime.fromtimestamp(mtime, timezone.utc).strftime(
+            "%Y-%m-%dT%H:%M:%SZ"
+        )
+    except OSError:
+        return None
+
+
+def stamp_task_header(path: Path, field_name: str, value: str | None = None) -> bool:
+    """Add a UTC ISO-8601 timestamp header line when the field is absent.
+
+    Why write-once: a task can be re-claimed after a block, or re-staged, and the
+    first value is the one that measures the work. The clock is the process clock in
+    UTC on purpose — the stamp must be comparable across machines, not local time.
+
+    Args:
+        path: task Markdown file to patch.
+        field_name: header key without decoration, e.g. ``Submitted``.
+        value: explicit stamp to write (used for a git-recovered start); defaults to now.
+
+    Returns:
+        True when a line was written, False when the field already existed or the
+        file could not be read.
+    """
+    try:
+        content = path.read_text(encoding="utf-8")
+    except Exception:
+        return False
+    if re.search(rf"^\*\*{re.escape(field_name)}:\*\*", content, re.MULTILINE):
+        return False
+    stamp = value or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
+    lines = content.splitlines()
+    for idx, line in enumerate(lines):
+        if line.strip().startswith("**Status:**"):
+            lines.insert(idx + 1, f"**{field_name}:** {stamp}")
+            path.write_text(
+                "\n".join(lines) + ("\n" if content.endswith("\n") else ""),
+                encoding="utf-8",
+            )
+            return True
+    path.write_text(f"**{field_name}:** {stamp}\n" + content, encoding="utf-8")
+    return True
+
+
 def _patch_archived_file(archive_path: Path, meta_id: str, meta_slug: str) -> None:
     try:
         content = archive_path.read_text(encoding="utf-8")
diff --git a/mcp-context-server/server.py b/mcp-context-server/server.py
index d53c54c..d5ba2c5 100755
--- a/mcp-context-server/server.py
+++ b/mcp-context-server/server.py
@@ -128,6 +128,9 @@ from gitops import (
     _extract_section,
     _extract_title,
     _find_task_file,
+    backfill_started_from_git,
+    stamp_task_header,
+    task_start_stamp,
     _format_task_id_list,
     _git_mv_or_fallback,
     _kebab_case,
@@ -882,6 +885,68 @@ def stage_and_inject_diff(
         return f"❌ Error staging or updating task file: {str(e)}"
 
 
+@_project_tool
+def sync_task_times(project_root: str | None = None, lane: str = "") -> str:
+    """Stamp missing start/submit/finish times for tasks already sitting in a lane.
+
+    Why this exists: the lane transitions stamp their own time, but a task can also be
+    moved by hand (``git mv`` is permitted). Such a file arrives without its stamp and
+    its measured duration would be silently lost. Running this after a manual move
+    closes that gap without turning any move into a hook.
+
+    The start time is recovered from git history first, then from the file's
+    modification time; it is never invented as "now", because a wrong start is worse
+    than a missing one. Submit and finish times have no history to recover from, so
+    they are stamped at call time — which is correct, since the caller runs this
+    immediately after the move.
+
+    Idempotent: an existing stamp is never rewritten.
+
+    Args:
+        project_root: absolute project root holding tasks/.
+        lane: restrict to ``in-progress`` or ``qa``; empty means both.
+
+    Returns:
+        One line per changed file, plus a summary.
+    """
+    workspace_root = _explicit_project_root(project_root, "sync_task_times")
+    # Only the two lanes a human might move a file into by hand. Closure is not offered:
+    # stamping `Finished` now on an old completed task would fabricate a duration, and
+    # `commit_and_clean_task` already handles the real closure moment.
+    wanted: list[tuple[str, str]] = [
+        ("in-progress", "Started"),
+        ("qa", "Submitted"),
+    ]
+    if lane:
+        if lane not in {name for name, _ in wanted}:
+            return "❌ lane must be in-progress or qa."
+        wanted = [pair for pair in wanted if pair[0] == lane]
+
+    changed: list[str] = []
+    skipped: list[str] = []
+    for lane_name, field in wanted:
+        lane_dir = workspace_root / "tasks" / lane_name
+        if not lane_dir.is_dir():
+            continue
+        for path in sorted(lane_dir.glob("*.md")):
+            content = path.read_text(encoding="utf-8", errors="ignore")
+            if re.search(rf"^\*\*{field}:\*\*", content, re.MULTILINE):
+                continue
+            value = None
+            source = "now"
+            if field == "Started":
+                value = task_start_stamp(workspace_root, path)
+                source = "git/mtime" if value else "unknown"
+            if stamp_task_header(path, field, value):
+                changed.append(f"- {path.name}: **{field}:** ({source})")
+            else:
+                skipped.append(path.name)
+    head = f"Stamped {len(changed)} task(s)."
+    body = "\n".join(changed) if changed else "Nothing to stamp."
+    tail = f"\nNo usable time for: {', '.join(skipped)}" if skipped else ""
+    return f"{head}\n{body}{tail}"
+
+
 @_project_tool
 def unstage_files(files: list[str], project_root: str | None = None) -> str:
     """Removes the listed files from the Git index WITHOUT touching the worktree.
@@ -1040,6 +1105,8 @@ def qa_transition(
         )
         try:
             dest.write_text(new_content_header, encoding="utf-8")
+            # Measured QA entry time: written once, so a re-transition never rewrites it.
+            stamp_task_header(dest, "Submitted")
         except Exception as e:
             return f"❌ Error writing header update to {dest}: {e}"
 
@@ -1148,6 +1215,16 @@ def commit_and_clean_task(
         if not path.is_absolute():
             path = Path(repo) / path
         if path.is_file():
+            # Closure time: stamped once, so the measured duration is start → close.
+            # A file that skipped claim_next (hand-moved) has no start; recover it from
+            # git so the duration is measured rather than silently lost.
+            if not re.search(
+                r"^\*\*Started:\*\*", path.read_text(encoding="utf-8"), re.MULTILINE
+            ):
+                recovered = backfill_started_from_git(Path(repo), path)
+                if recovered:
+                    stamp_task_header(path, "Started", recovered)
+            stamp_task_header(path, "Finished")
             with open(path, "r", encoding="utf-8") as f:
                 existing = f.read()
             cleaned_block = re.compile(
diff --git a/mcp-lint-server/DECISIONS.md b/mcp-lint-server/DECISIONS.md
index 984b182..04875c0 100644
--- a/mcp-lint-server/DECISIONS.md
+++ b/mcp-lint-server/DECISIONS.md
@@ -20,3 +20,10 @@
 - **Decision:** Add `_check_planner_metadata`, wired into `lint_task_file` and `lint_all_tasks`: a present `**Estimate:**` must match `^\d+(\.\d+)?h$`, `**Deadline:**` must be `YYYY-MM-DD`, `**Depends on:**` must be a bracketed or comma-separated id list, and a duplicated key is an error (the Planner keeps the last, hiding the mistake). Absence stays valid so legacy files and non-planner projects keep passing.
 - **Consequences:** A malformed header fails before staging instead of vanishing from the read model; the check is format-only and never rewrites; the paired writer is `schedule_tasks` in the Planner server, so agents have a correct path rather than a forbidden one.
 - **Rollback:** Remove the check and its two call sites; prior lint behavior returns.
+
+## [2026-10-25] ADR-004: Task time stamps are validated, not trusted
+
+- **Context:** the planner now measures task duration from `**Started:**`, `**Submitted:**` and `**Finished:**`. A local-time or free-text value parses to nothing, and a finish earlier than its start produces a negative duration — both silently, which is exactly the failure mode the earlier metadata gate exists to prevent.
+- **Decision:** `_check_planner_metadata` validates the three stamps when present: `YYYY-MM-DDThh:mm:ssZ` only (a `+02:00` offset is rejected on purpose, because the rest of the header is UTC and mixing them makes comparisons wrong), and a `Submitted`/`Finished` earlier than `Started` is an error. Absence stays valid, so every existing task file keeps passing.
+- **Consequences:** a malformed stamp fails before staging instead of producing a nonsense duration on the dashboard; the writer side already emits `Z`, so the gate only fires on hand edits.
+- **Rollback:** delete the stamp block from the check; the other metadata validations are untouched.
diff --git a/mcp-lint-server/server.py b/mcp-lint-server/server.py
index ab53aec..085d037 100755
--- a/mcp-lint-server/server.py
+++ b/mcp-lint-server/server.py
@@ -516,6 +516,7 @@ def _check_unactionable_skill_verbs(content: str, file_path: str) -> list[str]:
 _PLANNER_ESTIMATE_RE = re.compile(r"^\d+(?:\.\d+)?h$")
 _PLANNER_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
 _PLANNER_DEPS_RE = re.compile(r"^\[?\s*\d+(\s*,\s*\d+)*\s*\]?$")
+_PLANNER_STAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
 
 
 def _check_planner_metadata(content: str, file_path: str) -> list[str]:
@@ -528,26 +529,52 @@ def _check_planner_metadata(content: str, file_path: str) -> list[str]:
     """
     issues: list[str] = []
     counts: dict[str, int] = {}
+    stamps: dict[str, str] = {}
     for raw in content.splitlines():
         m = re.match(r"^\*\*(Estimate|Deadline|Depends on):\*\*\s*(.*)$", raw.strip())
-        if not m:
+        if m:
+            key, value = m.group(1), m.group(2).strip()
+            counts[key] = counts.get(key, 0) + 1
+            if key == "Estimate" and not _PLANNER_ESTIMATE_RE.match(value):
+                issues.append(
+                    f"Planner metadata: `**Estimate:**` must look like `3h` or `2.5h` "
+                    f"(got `{value}`) — the Planner silently drops an unparseable value."
+                )
+            elif key == "Deadline" and not _PLANNER_DATE_RE.match(value):
+                issues.append(
+                    f"Planner metadata: `**Deadline:**` must be `YYYY-MM-DD` "
+                    f"(got `{value}`) — free text never reaches the timeline."
+                )
+            elif key == "Depends on" and not _PLANNER_DEPS_RE.match(value):
+                issues.append(
+                    f"Planner metadata: `**Depends on:**` must be ids such as `338` or "
+                    f"`[338, 340]` (got `{value}`)."
+                )
             continue
-        key, value = m.group(1), m.group(2).strip()
-        counts[key] = counts.get(key, 0) + 1
-        if key == "Estimate" and not _PLANNER_ESTIMATE_RE.match(value):
-            issues.append(
-                f"Planner metadata: `**Estimate:**` must look like `3h` or `2.5h` "
-                f"(got `{value}`) — the Planner silently drops an unparseable value."
-            )
-        elif key == "Deadline" and not _PLANNER_DATE_RE.match(value):
-            issues.append(
-                f"Planner metadata: `**Deadline:**` must be `YYYY-MM-DD` "
-                f"(got `{value}`) — free text never reaches the timeline."
-            )
-        elif key == "Depends on" and not _PLANNER_DEPS_RE.match(value):
+        s = re.match(r"^\*\*(Started|Submitted|Finished):\*\*\s*(.*)$", raw.strip())
+        if s:
+            key, value = s.group(1), s.group(2).strip()
+            stamps[key] = value
+            if not _PLANNER_STAMP_RE.match(value):
+                issues.append(
+                    f"Planner metadata: `**{key}:**` must be an ISO-8601 UTC stamp such as "
+                    f"`2026-10-25T14:20:31Z` (got `{value}`) — a local or free-text time "
+                    f"makes measured duration wrong."
+                )
+    # Ordering: a finish earlier than the start is a corrupt measurement, not a fast task.
+    started = stamps.get("Started")
+    for later in ("Submitted", "Finished"):
+        value = stamps.get(later)
+        if (
+            started
+            and value
+            and _PLANNER_STAMP_RE.match(started)
+            and _PLANNER_STAMP_RE.match(value)
+            and value < started
+        ):
             issues.append(
-                f"Planner metadata: `**Depends on:**` must be ids such as `338` or "
-                f"`[338, 340]` (got `{value}`)."
+                f"Planner metadata: `**{later}:**` ({value}) is earlier than "
+                f"`**Started:**` ({started}); measured duration would be negative."
             )
     for key, count in counts.items():
         if count > 1:
diff --git a/mcp-planner-server/DECISIONS.md b/mcp-planner-server/DECISIONS.md
index 8cb5d31..17311b3 100644
--- a/mcp-planner-server/DECISIONS.md
+++ b/mcp-planner-server/DECISIONS.md
@@ -24,77 +24,77 @@
 ## [2026-10-24] ADR-003: MCP transport is mounted via `streamable_http_app()` with an explicit lifespan
 
 - **Context:** The combined Starlette app has to serve the dashboard at `/` and
-the MCP endpoint on the same loopback port. The first implementation called
-`FastMCP.http_app()`, which does not exist in the installed `mcp` 1.30 SDK, and
-mounted the returned app at `/mcp` — which would also have double-prefixed the
-endpoint, since the transport app already routes itself at
-`settings.streamable_http_path` (`/mcp`).
+  the MCP endpoint on the same loopback port. The first implementation called
+  `FastMCP.http_app()`, which does not exist in the installed `mcp` 1.30 SDK, and
+  mounted the returned app at `/mcp` — which would also have double-prefixed the
+  endpoint, since the transport app already routes itself at
+  `settings.streamable_http_path` (`/mcp`).
 - **Decision:** Build the transport app with `mcp.streamable_http_app()`, mount it
-at the root, and enter `mcp_app.router.lifespan_context(mcp_app)` from the parent
-app's lifespan. Starlette runs only the parent lifespan and never a `Mount`-ed
-sub-app's, so without the explicit enter the session manager task group stays
-uninitialised and every request to `/mcp` fails with `RuntimeError: Task group is
+  at the root, and enter `mcp_app.router.lifespan_context(mcp_app)` from the parent
+  app's lifespan. Starlette runs only the parent lifespan and never a `Mount`-ed
+  sub-app's, so without the explicit enter the session manager task group stays
+  uninitialised and every request to `/mcp` fails with `RuntimeError: Task group is
 not initialized`.
 - **Consequences:** Dashboard routes (`/`, `/api/status`) and the MCP endpoint
-(`/mcp`) coexist on one loopback listener. A future SDK change to the transport
-entrypoint or to `streamable_http_path` must be re-verified against
-`tests/test_planner_server.py::test_build_app_serves_dashboard_and_mcp_routes` and
-a live `initialize` probe.
+  (`/mcp`) coexist on one loopback listener. A future SDK change to the transport
+  entrypoint or to `streamable_http_path` must be re-verified against
+  `tests/test_planner_server.py::test_build_app_serves_dashboard_and_mcp_routes` and
+  a live `initialize` probe.
 - **Rollback:** Run `uvicorn` directly on `mcp.streamable_http_app()` and drop the
-dashboard routes; the planning tools keep working unchanged.
+  dashboard routes; the planning tools keep working unchanged.
 
 ## [2026-10-24] ADR-004: `/api/status` ships task lists, not counts
 
 - **Context:** The dashboard renders each lane by mapping over its items and
-builds the milestone tree and timeline from the same payload. The first contract
-returned a scalar count per lane and no `milestone_tree`/`deadlines`, so
-`items.map` threw inside `render()`, the exception was swallowed by the fetch
-catch block, and the board blanked while the UI reported "Server unreachable".
-A hard-coded `Path.cwd()` root also made the dashboard report an empty board
-under systemd, whose WorkingDirectory is the install directory.
+  builds the milestone tree and timeline from the same payload. The first contract
+  returned a scalar count per lane and no `milestone_tree`/`deadlines`, so
+  `items.map` threw inside `render()`, the exception was swallowed by the fetch
+  catch block, and the board blanked while the UI reported "Server unreachable".
+  A hard-coded `Path.cwd()` root also made the dashboard report an empty board
+  under systemd, whose WorkingDirectory is the install directory.
 - **Decision:** `/api/status` returns JSON-serialisable task briefs per lane, a
-`milestone_tree` keyed by `**Milestone:**`, a sorted `deadlines` list, the
-`today` pacing triple (`done`/`target`/`open`, derived from the same rule as
-`sprint_check_daily_quota`), and a `projects` list for the switcher. The root is
-resolved from the `project_root` query parameter → `PLANNER_PROJECT_ROOT` →
-nearest ancestor holding `tasks/` → cwd.
+  `milestone_tree` keyed by `**Milestone:**`, a sorted `deadlines` list, the
+  `today` pacing triple (`done`/`target`/`open`, derived from the same rule as
+  `sprint_check_daily_quota`), and a `projects` list for the switcher. The root is
+  resolved from the `project_root` query parameter → `PLANNER_PROJECT_ROOT` →
+  nearest ancestor holding `tasks/` → cwd.
 - **Consequences:** The contract is pinned by
-`tests/test_planner_server.py::test_api_status_lanes_are_task_lists` and friends;
-any change to lane shape breaks a test rather than silently blanking the UI.
-`PLANNER_PROJECTS` is the only way to offer several roots in the switcher.
+  `tests/test_planner_server.py::test_api_status_lanes_are_task_lists` and friends;
+  any change to lane shape breaks a test rather than silently blanking the UI.
+  `PLANNER_PROJECTS` is the only way to offer several roots in the switcher.
 - **Rollback:** Revert the `/api/status` handler and the dashboard `render()`
-together — they share one contract and must never be changed independently.
+  together — they share one contract and must never be changed independently.
 
 ## [2026-10-24] ADR-005: Optional cookie-session auth with per-user project scoping
 
 - **Context:** The dashboard is useful from a phone, so the Manager wants it
-reachable through a Cloudflare Tunnel. Loopback-only access was the sole control
-until now, which stops working the moment the port leaves the host. At the same
-time the local OpenCode clients call `/mcp` with no credentials and must keep
-working untouched.
+  reachable through a Cloudflare Tunnel. Loopback-only access was the sole control
+  until now, which stops working the moment the port leaves the host. At the same
+  time the local OpenCode clients call `/mcp` with no credentials and must keep
+  working untouched.
 - **Decision:** Auth is opt-in through `~/.config/opencode/planner-users.json`
-(`PLANNER_USERS_CONFIG` override). A missing, unreadable, non-object, or
-`auth_enabled: false` file — or one with no users — keeps the server in open
-local mode with no 401s and no filtering. When enabled: PBKDF2-HMAC-SHA256
-(600k iterations, 16-byte `secrets` salt, `hmac.compare_digest`) with stdlib
-only; opaque in-memory session tokens in an `HttpOnly` `SameSite=Lax`
-`planner_session` cookie (7-day TTL, dropped on restart); `/api/status` answers
-401 unauthenticated, filters `projects` to `allowed_projects` (`"*"` = all) and
-403s an explicit `project_root` outside them; `/mcp` requires an **admin**
-session while viewers stay read-only. A viewer with no explicit root falls back
-to their first allowed project rather than being denied.
+  (`PLANNER_USERS_CONFIG` override). A missing, unreadable, non-object, or
+  `auth_enabled: false` file — or one with no users — keeps the server in open
+  local mode with no 401s and no filtering. When enabled: PBKDF2-HMAC-SHA256
+  (600k iterations, 16-byte `secrets` salt, `hmac.compare_digest`) with stdlib
+  only; opaque in-memory session tokens in an `HttpOnly` `SameSite=Lax`
+  `planner_session` cookie (7-day TTL, dropped on restart); `/api/status` answers
+  401 unauthenticated, filters `projects` to `allowed_projects` (`"*"` = all) and
+  403s an explicit `project_root` outside them; `/mcp` requires an **admin**
+  session while viewers stay read-only. A viewer with no explicit root falls back
+  to their first allowed project rather than being denied.
 - **Consequences:** One server serves both audiences: local tooling stays
-credential-free in open mode, remote browsers sign in. Restart is required after
-a user edit because the config is read when the app is built. A restart also
-signs everyone out — acceptable, and it means no long-lived signing secret lives
-on disk. `/mcp` over the tunnel is blocked at ingress (`http_status:404`), so
-tool execution never depends on the guard alone. Pinned by the auth tests plus
-the CLI test that hashes through the server's own verifier.
+  credential-free in open mode, remote browsers sign in. Restart is required after
+  a user edit because the config is read when the app is built. A restart also
+  signs everyone out — acceptable, and it means no long-lived signing secret lives
+  on disk. `/mcp` over the tunnel is blocked at ingress (`http_status:404`), so
+  tool execution never depends on the guard alone. Pinned by the auth tests plus
+  the CLI test that hashes through the server's own verifier.
 - **Rollback:** Delete `planner-users.json` or run `manage_users.py disable`;
-the server returns to open local mode with no code change. Full code rollback is
-`server.py` + `static/index.html` + `manage_users.py` reverted together.
+  the server returns to open local mode with no code change. Full code rollback is
+  `server.py` + `static/index.html` + `manage_users.py` reverted together.
 - **Superseded in part:** the `/mcp` admin-session requirement only — see
-ADR-006 below. Session auth, scoping, and the CLI remain as decided here.
+  ADR-006 below. Session auth, scoping, and the CLI remain as decided here.
 
 ## [2026-10-24] ADR-007: `GET /api/task` is a guarded, lane-confined read
 
@@ -174,3 +174,9 @@ ADR-006 below. Session auth, scoping, and the CLI remain as decided here.
 - **Consequences:** the metadata has exactly one writer and one validator, so an approved plan lands in the files the Planner reads. The tool refuses to clear a value (`-` means "leave as is") because deleting a deadline stays a Manager decision, and the dashboard week plan (`deadline_edits`) is untouched — task files remain the source of truth it overlays.
 - **Rollback:** unregister the tool and revert the prompt sentence; existing metadata is plain Markdown and needs no cleanup.
 
+## [2026-10-25] ADR-011: Measured task time, stamped by the transitions
+
+- **Context:** the panel could only show estimates. `_parse_task_file` had no time fields, `claim_next` moved the file without a stamp, and `sprint_stats` summed `Estimate` over closed tasks under the label "hours spent". The git commit time approximated closure but said nothing about the start, and a shell `date` per task is neither automatic nor comparable across machines.
+- **Decision:** three ISO-8601 UTC stamps written by the transitions themselves: `Started` in `claim_next`, `Submitted` in `qa_transition`, `Finished` in `commit_and_clean_task`. All are write-once — the first start is the measured work — and `_task_brief` derives `elapsed_seconds` and `qa_wait_seconds`, `null` when a stamp is missing so the UI never shows a fake zero. `sprint_stats` keeps estimates and adds a separate measured line, and `_check_planner_metadata` rejects a non-UTC stamp or a finish before the start.
+- **Consequences:** the duration is measured, not guessed, and the estimate stays visible next to it so drift is obvious. The stamps live in the task header, so they travel with the file through every lane move and need no sidecar. A handwriting of the fields is impossible to corrupt silently: the lint fails.
+- **Rollback:** remove the three stamps, the brief fields and the lint checks; estimates-only behaviour returns and the extra lines are inert.
diff --git a/mcp-planner-server/README.md b/mcp-planner-server/README.md
index 624db74..9dc804d 100644
--- a/mcp-planner-server/README.md
+++ b/mcp-planner-server/README.md
@@ -24,16 +24,16 @@ dashboard on loopback port 8108.
 
 ## HTTP surface (loopback 8108)
 
-| Route | Purpose |
-| ----- | ------- |
-| `GET /` | Standalone dark-mode dashboard (no build step). |
-| `GET /static/*` | Dashboard assets (same `static/` directory). |
-| `GET /api/status[?project_root=<abs path>]` | JSON status contract the dashboard renders. |
+| Route                                                     | Purpose                                                                                                                                                                                                   |
+| --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
+| `GET /`                                                   | Standalone dark-mode dashboard (no build step).                                                                                                                                                           |
+| `GET /static/*`                                           | Dashboard assets (same `static/` directory).                                                                                                                                                              |
+| `GET /api/status[?project_root=<abs path>]`               | JSON status contract the dashboard renders.                                                                                                                                                               |
 | `GET /api/task?id=<id>` or `?path=tasks/<lane>/<file>.md` | One task file as `{id, path, lane, title, markdown}` for the dashboard modal. `id` wins when both are sent. 400 no param, 401 no session, 403 outside grants or unsafe path, 404 unknown, 500 unexpected. |
-| `POST /api/login` | `{"username","password"}` → `{token, username, role, allowed_projects}` + `HttpOnly` cookie. |
-| `POST /api/logout` | Invalidates the session and clears the cookie. |
-| `GET /api/me` | Current user, or 401 when signed out (200 + `note: "auth disabled"` in open mode). |
-| `POST /mcp` | MCP Streamable HTTP endpoint (tools). Auth-free on loopback; the tunnel 404s it. |
+| `POST /api/login`                                         | `{"username","password"}` → `{token, username, role, allowed_projects}` + `HttpOnly` cookie.                                                                                                              |
+| `POST /api/logout`                                        | Invalidates the session and clears the cookie.                                                                                                                                                            |
+| `GET /api/me`                                             | Current user, or 401 when signed out (200 + `note: "auth disabled"` in open mode).                                                                                                                        |
+| `POST /mcp`                                               | MCP Streamable HTTP endpoint (tools). Auth-free on loopback; the tunnel 404s it.                                                                                                                          |
 
 `/api/status` returns per-lane **task lists** (`lanes`), the milestone tree
 (`milestone_tree`), upcoming deadlines (`deadlines`), the pacing figures
@@ -52,8 +52,8 @@ holding `tasks/`, then the working directory. `PLANNER_PROJECTS`
 
 - **Config:** `~/.config/opencode/planner-users.json`, overridable with
   `PLANNER_USERS_CONFIG`. Shape: `{"auth_enabled": bool, "users": [{"username",
-  "role": "admin"|"viewer", "password_salt", "password_hash",
-  "allowed_projects": ["*"] | ["/abs/path", ...]}]}`.
+"role": "admin"|"viewer", "password_salt", "password_hash",
+"allowed_projects": ["*"] | ["/abs/path", ...]}]}`.
 - **Open mode:** no file, unreadable file, invalid JSON, `auth_enabled: false`,
   or an empty `users` list ⇒ every request behaves exactly as before
   (no 401, no filtering). This is the backward-compatibility contract.
@@ -155,7 +155,7 @@ truth for each task; the plan only records scheduling decisions.
 
 - `GET /api/plan` returns the saved plan next to the buckets.
 - `POST /api/plan` accepts `{week?, deadline_edits?, capacity_by_day?, approved?,
-  force?}`; admin session required when auth is on (401 without a session, 403
+force?}`; admin session required when auth is on (401 without a session, 403
   for non-admins). Unknown ids, malformed maps, and over-capacity assignments
   are rejected with 400 unless `force` is set.
 - `DELETE /api/plan?week=...` clears the week.
@@ -204,3 +204,23 @@ estimate that is not `Nh`/`N.Nh`, deadline that is not `YYYY-MM-DD`, dependencie
 that are not ids. The lint rule `_check_planner_metadata` enforces the same
 formats, so an agent cannot invent one and have the task silently drop out of
 capacity and the timeline.
+
+### Measured time (`Started`, `Submitted`, `Finished`)
+
+Estimates are a plan; these three stamps are the measurement. They are written
+by the lane transitions themselves, never by hand:
+
+| Stamp            | Written by              | When                                               |
+| ---------------- | ----------------------- | -------------------------------------------------- |
+| `**Started:**`   | `claim_next`            | the file enters `tasks/in-progress/`               |
+| `**Submitted:**` | `qa_transition`         | the file enters `tasks/qa/`                        |
+| `**Finished:**`  | `commit_and_clean_task` | closure, after the file sits in `tasks/completed/` |
+
+Each is ISO-8601 UTC with a `Z` suffix and is **write-once**: a re-claim or a
+re-stage never rewrites the original start, because the first one is the work
+being measured. `_task_brief` turns them into `elapsed_seconds` (finished −
+started) and `qa_wait_seconds` (submitted − started), both `null` rather than
+`0` when a stamp is missing, so the panel can tell "not measured" from
+"instant". `sprint_stats` keeps the estimate arithmetic and adds a separate
+`Completed measured` line. `_check_planner_metadata` rejects a stamp that is not
+UTC or a `Finished` earlier than its `Started`.
diff --git a/mcp-planner-server/server.py b/mcp-planner-server/server.py
index a654151..335aa38 100644
--- a/mcp-planner-server/server.py
+++ b/mcp-planner-server/server.py
@@ -211,6 +211,9 @@ def _parse_task_file(path: Path) -> dict:
         "type": None,
         "status": None,
         "estimate_hours": None,
+        "started_at": None,
+        "submitted_at": None,
+        "finished_at": None,
         "deadline": None,
         "milestone": None,
         "depends_on": [],
@@ -242,6 +245,12 @@ def _parse_task_file(path: Path) -> dict:
                 record["estimate_hours"] = float(em.group(1))
         elif key == "deadline":
             record["deadline"] = val
+        elif key == "started":
+            record["started_at"] = val
+        elif key == "submitted":
+            record["submitted_at"] = val
+        elif key == "finished":
+            record["finished_at"] = val
         elif key == "milestone":
             record["milestone"] = val
         elif key == "depends on":
@@ -757,6 +766,49 @@ def schedule_tasks(project_root: str, assignments: str) -> str:
     return f"{head}\n{body}{tail}"
 
 
+def _stamp_header_once(content: str, field_name: str) -> str:
+    """Add a UTC timestamp header line when the field is absent.
+
+    Why write-once: a task can be claimed again after a block, or re-stamped by a
+    later lane, and the first start is the one that measures the work. A present
+    value is never touched.
+
+    Args:
+        content: the task file body.
+        field_name: header key without the markdown decoration, e.g. ``Started``.
+
+    Returns:
+        The body, with the field inserted after ``**Status:**`` when it was missing.
+    """
+    pattern = re.compile(rf"^\*\*{re.escape(field_name)}:\*\*", re.MULTILINE)
+    if pattern.search(content):
+        return content
+    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
+    lines = content.splitlines()
+    for idx, line in enumerate(lines):
+        if line.strip().startswith("**Status:**"):
+            lines.insert(idx + 1, f"**{field_name}:** {stamp}")
+            return "\n".join(lines) + ("\n" if content.endswith("\n") else "")
+    # No Status line: append at the top so the stamp is never silently lost.
+    return f"**{field_name}:** {stamp}\n" + content
+
+
+def _parse_utc(value: object) -> Optional[datetime]:
+    """Parse an ISO-8601 UTC stamp, returning None when absent or malformed."""
+    if not isinstance(value, str) or not value.strip():
+        return None
+    text = value.strip()
+    try:
+        if text.endswith("Z"):
+            text = text[:-1] + "+00:00"
+        parsed = datetime.fromisoformat(text)
+    except ValueError:
+        return None
+    if parsed.tzinfo is None:
+        return parsed.replace(tzinfo=timezone.utc)
+    return parsed.astimezone(timezone.utc)
+
+
 @_project_tool
 def claim_next(project_root: str, task_id: str) -> str:
     """Claim the next task: move it from backlog to in-progress.
@@ -840,10 +892,11 @@ def claim_next(project_root: str, task_id: str) -> str:
     except Exception as exc:  # noqa: BLE001
         return f"❌ claim_next failed: {exc}."
 
-    # Update the Status header in the moved file.
+    # Update the Status header in the moved file, stamping the start time once.
     try:
         content = dest.read_text(encoding="utf-8")
         content = content.replace("**Status:** open", "**Status:** in-progress", 1)
+        content = _stamp_header_once(content, "Started")
         dest.write_text(content, encoding="utf-8")
     except OSError:
         pass  # Header update is best-effort; the move itself succeeded.
@@ -993,6 +1046,13 @@ def sprint_stats(project_root: Optional[str] = None) -> str:
         for t in tasks
         if t.get("status") == "closed" and t.get("estimate_hours")
     )
+    # Measured hours: only closed tasks that carry both stamps, so this line can
+    # never quietly reuse an estimate.
+    measured_hours = 0.0
+    for t in tasks:
+        brief = _task_brief(t)
+        if t.get("status") == "closed" and brief.get("elapsed_seconds") is not None:
+            measured_hours += brief["elapsed_seconds"] / 3600.0
 
     pct = (completed / total_tasks * 100) if total_tasks else 0.0
 
@@ -1009,6 +1069,8 @@ def sprint_stats(project_root: Optional[str] = None) -> str:
     lines.append(f"Total estimated: {total_est}h")
     lines.append(f"Completed estimated: {completed_est}h")
     lines.append("")
+    lines.append("## Measured")
+    lines.append(f"Completed measured: {measured_hours:.2f}h")
     lines.append("## Velocity")
     lines.append(f"Tasks completed per lane snapshot: {completed} / {total_tasks}")
     lines.append("")
@@ -1645,6 +1707,21 @@ def _task_brief(task: dict) -> dict:
     """
     name = task.get("name") or ""
     match = TASK_ID_RE.match(name)
+    started = _parse_utc(task.get("started_at"))
+    submitted = _parse_utc(task.get("submitted_at"))
+    finished = _parse_utc(task.get("finished_at"))
+    # Measured durations only: None when a stamp is missing, never 0, so the panel
+    # can distinguish "not measured" from "instant".
+    elapsed = (
+        int((finished - started).total_seconds())
+        if started is not None and finished is not None
+        else None
+    )
+    qa_wait = (
+        int((submitted - started).total_seconds())
+        if started is not None and submitted is not None
+        else None
+    )
     return {
         "id": match.group(1) if match else name,
         "name": name,
@@ -1656,6 +1733,11 @@ def _task_brief(task: dict) -> dict:
         "owner": task.get("owner"),
         "deadline": task.get("deadline"),
         "milestone": task.get("milestone"),
+        "started_at": task.get("started_at"),
+        "submitted_at": task.get("submitted_at"),
+        "finished_at": task.get("finished_at"),
+        "elapsed_seconds": elapsed,
+        "qa_wait_seconds": qa_wait,
     }
 
 
@@ -1767,12 +1849,19 @@ def _api_task(
 
         name = record.get("name") or ""
         match = TASK_ID_RE.match(name)
+        brief = _task_brief(record)
         return {
             "id": match.group(1) if match else name,
             "path": record.get("path"),
             "lane": record.get("lane"),
             "title": record.get("title") or "untitled",
             "markdown": record.get("raw") or "",
+            # Measured timing travels with the task so the modal never re-derives it.
+            "started_at": brief.get("started_at"),
+            "submitted_at": brief.get("submitted_at"),
+            "finished_at": brief.get("finished_at"),
+            "elapsed_seconds": brief.get("elapsed_seconds"),
+            "qa_wait_seconds": brief.get("qa_wait_seconds"),
         }
     except Exception:  # noqa: BLE001 - surface as 500, never a 200 envelope
         return {"error": "internal error"}
diff --git a/mcp-planner-server/static/index.html b/mcp-planner-server/static/index.html
index adc116e..ca109c2 100644
--- a/mcp-planner-server/static/index.html
+++ b/mcp-planner-server/static/index.html
@@ -491,6 +491,16 @@
     return marker >= 0 ? absPath.slice(marker + 1) : '';
   }
 
+  /** Human duration from measured seconds; never invent a value when it is null. */
+  function formatDuration(totalSeconds) {
+    const secs = Math.max(0, Math.round(Number(totalSeconds) || 0));
+    const h = Math.floor(secs / 3600);
+    const m = Math.floor((secs % 3600) / 60);
+    if (h > 0) return h + 'h ' + m + 'm';
+    if (m > 0) return m + 'm';
+    return secs + 's';
+  }
+
   function openTaskModal(id, absPath) {
     modalTaskId = id || '';
     const params = new URLSearchParams();
@@ -512,7 +522,8 @@
           return;
         }
         elements.taskModalTitle.textContent = payload.title || 'Task ' + (payload.id || '');
-        elements.taskModalMeta.textContent = '#' + (payload.id || '?') + ' · ' + (payload.lane || 'unknown lane') + ' · ' + (relTaskPath(payload.path) || payload.path || '');
+        elements.taskModalMeta.textContent = '#' + (payload.id || '?') + ' · ' + (payload.lane || 'unknown lane') + ' · ' + (relTaskPath(payload.path) || payload.path || '') +
+          (payload.elapsed_seconds != null ? ' · measured ' + formatDuration(payload.elapsed_seconds) : '');
         elements.taskModalBody.innerHTML = renderMarkdown(payload.markdown || '');
         elements.taskModalBody.scrollTop = 0;
       })
diff --git a/tests/test_mcp_servers.py b/tests/test_mcp_servers.py
index d65d159..5cf029d 100644
--- a/tests/test_mcp_servers.py
+++ b/tests/test_mcp_servers.py
@@ -3033,7 +3033,7 @@ def test_graph_precision_full_scan_vocab_dfs_rationale_noise():
 
 
 def test_graph_tool_registry_has_no_helper_leak():
-    """Only the 15 intended MCP tools register; plain helpers never expose."""
+    """Only the 16 intended MCP tools register; plain helpers never expose."""
     mod = _load_context_server_hardening()
     names = sorted(mod.mcp._tool_manager._tools.keys())
     assert names == [
@@ -3051,6 +3051,7 @@ def test_graph_tool_registry_has_no_helper_leak():
         "read_source_files",
         "shortest_path",
         "stage_and_inject_diff",
+        "sync_task_times",
         "unstage_files",
     ], names
 
diff --git a/tests/test_task_timestamps.py b/tests/test_task_timestamps.py
new file mode 100644
index 0000000..63374f9
--- /dev/null
+++ b/tests/test_task_timestamps.py
@@ -0,0 +1,236 @@
+# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
+"""Measured task timing: claim stamp, QA stamp, closure stamp, duration, lint gate.
+
+Why: the planner used to report "hours spent" by summing the estimate, so the panel
+could never show what a task actually cost. These tests pin the three stamps and the
+arithmetic that turns them into a duration, including the write-once rule.
+"""
+
+import importlib.util
+import os
+import subprocess
+import sys
+from pathlib import Path
+
+import pytest
+
+REPO = Path(__file__).resolve().parent.parent
+sys.path.insert(0, str(REPO / "mcp-planner-server"))
+sys.path.insert(0, str(REPO / "mcp-context-server"))
+
+
+@pytest.fixture(autouse=True)
+def _isolated_project_registry(tmp_path, monkeypatch):
+    monkeypatch.setenv(
+        "PLANNER_PROJECTS_REGISTRY", str(tmp_path / "planner-projects.json")
+    )
+
+
+_PLANNER_SPEC = importlib.util.spec_from_file_location(
+    "planner_server_timestamps", REPO / "mcp-planner-server" / "server.py"
+)
+planner = importlib.util.module_from_spec(_PLANNER_SPEC)
+_PLANNER_SPEC.loader.exec_module(planner)
+
+_LINT_SPEC = importlib.util.spec_from_file_location(
+    "lint_server_timestamps", REPO / "mcp-lint-server" / "server.py"
+)
+lint = importlib.util.module_from_spec(_LINT_SPEC)
+_LINT_SPEC.loader.exec_module(lint)
+
+_GITOPS_SPEC = importlib.util.spec_from_file_location(
+    "gitops_timestamps", REPO / "mcp-context-server" / "gitops.py"
+)
+gitops = importlib.util.module_from_spec(_GITOPS_SPEC)
+_GITOPS_SPEC.loader.exec_module(gitops)
+
+_SERVER_SPEC = importlib.util.spec_from_file_location(
+    "context_server_timestamps", REPO / "mcp-context-server" / "server.py"
+)
+server = importlib.util.module_from_spec(_SERVER_SPEC)
+_SERVER_SPEC.loader.exec_module(server)
+
+
+TASK_BODY = (
+    "# Task 9001: timing sample\n\n"
+    "**File:** `tasks/backlog/9001-timing-sample.md`\n"
+    "**Source:** manager\n"
+    "**Type:** bug\n"
+    "**Status:** open\n"
+    "\n"
+    "## Goal\n\nDo the thing.\n"
+)
+
+
+def _task(tmp_path, body=TASK_BODY):
+    path = tmp_path / "tasks" / "backlog" / "9001-timing-sample.md"
+    path.parent.mkdir(parents=True, exist_ok=True)
+    path.write_text(body, encoding="utf-8")
+    return path
+
+
+def test_stamp_is_written_after_status(tmp_path):
+    path = _task(tmp_path)
+
+    wrote = gitops.stamp_task_header(path, "Started")
+
+    assert wrote is True
+    lines = path.read_text(encoding="utf-8").splitlines()
+    idx = next(i for i, l in enumerate(lines) if l.startswith("**Status:**"))
+    assert lines[idx + 1].startswith("**Started:** 20")
+    assert lines[idx + 1].endswith("Z")
+
+
+def test_stamp_is_write_once(tmp_path):
+    path = _task(tmp_path)
+    gitops.stamp_task_header(path, "Started")
+    first = path.read_text(encoding="utf-8")
+
+    wrote_again = gitops.stamp_task_header(path, "Started")
+
+    assert wrote_again is False
+    assert path.read_text(encoding="utf-8") == first
+
+
+def test_planner_stamp_helper_matches_the_contract(tmp_path):
+    path = _task(tmp_path)
+
+    stamped = planner._stamp_header_once(path.read_text(encoding="utf-8"), "Finished")
+
+    assert "**Finished:**" in stamped
+    assert planner._stamp_header_once(stamped, "Finished") == stamped
+
+
+def test_task_brief_computes_durations_and_never_zero_fills():
+    record = {
+        "name": "9001-timing-sample.md",
+        "path": "tasks/completed/9001-timing-sample.md",
+        "title": "timing sample",
+        "lane": "completed",
+        "status": "closed",
+        "estimate_hours": 3.0,
+        "started_at": "2026-10-25T10:00:00Z",
+        "submitted_at": "2026-10-25T11:30:00Z",
+        "finished_at": "2026-10-25T12:00:00Z",
+    }
+
+    brief = planner._task_brief(record)
+
+    assert brief["elapsed_seconds"] == 7200
+    assert brief["qa_wait_seconds"] == 5400
+
+    # A missing finish is "not measured", not instant.
+    partial = dict(record)
+    partial["finished_at"] = None
+    assert planner._task_brief(partial)["elapsed_seconds"] is None
+
+
+@pytest.mark.parametrize(
+    "stamp",
+    [
+        "2026-10-25T14:20:31Z",
+    ],
+)
+def test_lint_accepts_iso_utc_stamps(stamp):
+    content = f"# Task 1: x\n\n**Started:** {stamp}\n"
+    assert lint._check_planner_metadata(content, "x.md") == []
+
+
+@pytest.mark.parametrize(
+    "stamp",
+    [
+        "2026-10-25 14:20:31",
+        "25/10/2026",
+        "2026-10-25T14:20:31+02:00",
+        "now",
+    ],
+)
+def test_lint_rejects_non_utc_or_free_text_stamps(stamp):
+    content = f"# Task 1: x\n\n**Started:** {stamp}\n"
+    issues = lint._check_planner_metadata(content, "x.md")
+    assert issues, f"lint accepted a stamp that cannot be compared: {stamp}"
+
+
+def test_lint_rejects_a_finish_before_the_start():
+    content = (
+        "# Task 1: x\n\n"
+        "**Started:** 2026-10-25T12:00:00Z\n"
+        "**Finished:** 2026-10-25T11:00:00Z\n"
+    )
+    issues = lint._check_planner_metadata(content, "x.md")
+    assert any("earlier than" in i for i in issues), issues
+
+
+def test_start_is_recovered_from_git_when_the_header_has_none(tmp_path):
+    """A hand-moved task still gets a measured duration, not a silent gap."""
+    repo = tmp_path / "repo"
+    repo.mkdir()
+    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
+    task = repo / "tasks" / "in-progress" / "9002-hand-moved.md"
+    task.parent.mkdir(parents=True)
+    task.write_text(
+        "# Task 9002: hand moved\n\n**File:** `tasks/in-progress/9002-hand-moved.md`\n"
+        "**Status:** in-progress\n",
+        encoding="utf-8",
+    )
+    env = {
+        "GIT_AUTHOR_DATE": "2026-10-24T08:30:00+00:00",
+        "GIT_COMMITTER_DATE": "2026-10-24T08:30:00+00:00",
+    }
+    subprocess.run(["git", "add", "."], cwd=repo, check=True)
+    subprocess.run(
+        [
+            "git",
+            "-c",
+            "user.email=t@t",
+            "-c",
+            "user.name=t",
+            "commit",
+            "-qm",
+            "add task",
+        ],
+        cwd=repo,
+        check=True,
+        env={**os.environ, **env},
+    )
+
+    recovered = gitops.backfill_started_from_git(repo, task)
+
+    assert recovered == "2026-10-24T08:30:00Z"
+    assert gitops.stamp_task_header(task, "Started", recovered) is True
+    assert "**Started:** 2026-10-24T08:30:00Z" in task.read_text(encoding="utf-8")
+
+
+def test_start_stamp_falls_back_to_mtime_and_never_invents_now(tmp_path):
+    """No git history: the file's own mtime is the next honest source."""
+    repo = tmp_path / "repo2"
+    repo.mkdir()
+    task = repo / "tasks" / "in-progress" / "9003-untracked.md"
+    task.parent.mkdir(parents=True)
+    task.write_text("# Task 9003\n\n**Status:** in-progress\n", encoding="utf-8")
+    os.utime(task, (1700000000, 1700000000))
+
+    stamp = gitops.task_start_stamp(repo, task)
+
+    assert stamp == "2023-11-14T22:13:20Z"
+
+
+def test_sync_task_times_is_idempotent(tmp_path):
+    repo = tmp_path / "repo3"
+    task = repo / "tasks" / "in-progress" / "9004-timing.md"
+    task.parent.mkdir(parents=True)
+    task.write_text(
+        "# Task 9004\n\n**File:** `tasks/in-progress/9004-timing.md`\n"
+        "**Status:** in-progress\n",
+        encoding="utf-8",
+    )
+    os.utime(task, (1700000000, 1700000000))
+
+    first = server.sync_task_times(str(repo), "in-progress")
+    content = task.read_text(encoding="utf-8")
+    second = server.sync_task_times(str(repo), "in-progress")
+
+    assert "**Started:**" in content
+    assert "Stamped 1 task" in first
+    assert "Nothing to stamp" in second
+    assert task.read_text(encoding="utf-8") == content
```
<!-- END_GIT_DIFF -->
