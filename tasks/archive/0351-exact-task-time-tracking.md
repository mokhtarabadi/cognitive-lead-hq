# Task 0351: Exact per-task time tracking from claim to closure

**File:** `tasks/completed/0351-exact-task-time-tracking.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Finished:** 2026-10-25T14:26:21Z
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
**Factual Git Diff:** Stored in Commit Hash: `962bb357d85f10bc062c0a46e23552b7f444ff97`
<!-- END_GIT_DIFF -->
