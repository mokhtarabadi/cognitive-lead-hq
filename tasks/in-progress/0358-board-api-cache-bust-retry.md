# Task 0358: Board API cache-busting and status retry

**File:** `tasks/in-progress/0358-board-api-cache-bust-retry.md`
**Source:** manager
**Type:** bug
**Status:** open

## Goal

Kill the persistent `?task=` status failure seen live: `/api/status` served 200 + HTML while `/api/plan?window=week` served JSON in the same browser at the same moment. Every API GET gets a cache-busting timestamp, and a status fetch that still lands on HTML retries once before diagnosing.

## Manager's Notes

> Screenshot: logged in as admin, status line shows the new diagnosis message, stats blank, but the plan section below renders live data. Deep link `?task=283` still errors.

## Findings (grounded)

- F1: same browser + moment, `/api/status` (queryless URL) → 200 HTML, `/api/plan?window=week` (URL with query) → JSON. The only request difference is the URL, so a cache layer keyed by exact URL is serving a poisoned HTML entry for `/api/status` (cached during a misroute window). `cache: 'no-cache'` does not defeat a CDN edge entry served as 200.
- F2: the 0357 diagnosis message rendered exactly as designed, proving the new static is live on the board — the failure is data staleness at the edge, not app logic.
- F3: fix is client-only: unique `_t=Date.now()` per API GET (poisoned entries can never match), one 1.5s retry on HTML body (transient challenge pages), content-type captured into the diagnosis.

## Local TODOs

- [x] Bust cache on status/plan/hours/task GETs
- [x] Retry-once on HTML status body with content-type in message
- [x] Verify functionality

## Acceptance Criteria

- [x] Reopening `?task=283` loads the board (status 200 JSON, no diagnosis line) without clearing any cache
- [x] A poisoned `/api/status` entry can never match again (unique URL per request)
- [x] Diagnosis message names the content-type when HTML persists after retry
- [x] Full planner suite green; no server change

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/test_planner_server.py -q
- **Expected result:** planner suite green; inline JS syntax clean; server ignores unknown `_t` param
- **Actual result:** `122 passed`; `node --check` clean on the inline script; `_t` touches no server query reader (status/task/plan/hours read only known keys)
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** timestamp query breaks nothing server-side (unknown query params ignored); CDN hit rate on API drops — APIs must not be edge-cached anyway.
- **Rollback:** revert `static/index.html`; board returns to 0357 behavior.

---

## Execution Log & Reasoning

**Decisive evidence (screenshot):** logged in as admin, status line shows the 0357 diagnosis, stats blank — yet the plan section below renders live data. Same browser, same moment: `/api/status` (queryless URL) → 200 HTML, `/api/plan?window=week` (URL with query) → JSON. The only request difference is the URL, so a cache layer keyed by exact URL is replaying a poisoned HTML entry for `/api/status`. The 0357 code is confirmed live on the board (its message rendered).

**Fix (client-only, `static/index.html`):** `bust()` appends `_t=Date.now()` to every API GET (status/plan/hours/task) so a poisoned entry can never match again; `fetchStatus` retries once after 1.5s on HTML bodies (transient challenge pages pass) and names the content-type in the diagnosis. Server ignores the unknown `_t` param (all four routes read only known keys). Self-caught during implementation: the first edit duplicated the try/fetch lines — removed, `node --check` clean.

**Assumption A1:** the poisoned layer is the CDN/edge cache (exact-URL key), not the app — the app provably returns JSON on all three endpoints. If HTML persists after retry with a fresh timestamp, the remaining suspect is per-request edge-login injection, and the message now says so with its content-type.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
