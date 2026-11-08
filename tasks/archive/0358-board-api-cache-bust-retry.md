# Task 0358: Board API cache-busting and status retry

**File:** `tasks/completed/0358-board-api-cache-bust-retry.md`
**Source:** manager
**Type:** bug
**Status:** closed
**Finished:** 2026-10-28T07:47:08Z

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

**Root cause, corrected (the above A1 was wrong):** `BASE_STATUS_URL` was built as `location.href + 'api/status'` whenever the path ended with `/`. On `?task=283` that yields `/?task=283api/status` — path `/` with garbage query — which the app routes to the dashboard, returning 200 + `text/html; charset=utf-8`. Proven live against loopback: that exact URL shape returns the dashboard with the exact content-type from the error line. Without `?task=`, href has no query, so the URL came out right — which is why plain opens always worked. No edge, no cache, no Access involved; the bust/retry/diagnosis stays as belt-and-braces. One-line fix: `origin + '/api/status'`.

**Post-review amendment (same task, still in QA):** the screenshot showed the 0357 message text without the content-type suffix while the plan section rendered data — the browser was executing a cached copy of the old shell. The dashboard shell now sends `Cache-Control: no-store`, so a stale page can never pin old client logic again. Deployed + restarted + live-verified (`cache-control: no-store` on `/`, all new-code markers in the served HTML, both API routes 401-correct). The user must hard-reload once to drop the pinned copy.

**QA cycle (Brain):** `QA_PASSED` — single `_t` per request, single retry, no server breakage; one acted-on note (`/api/me` also bust()ed).

**Review (Brain):** technically approved (`PO_REVIEW_PENDING`), severity Low. R1 applied. R2 deferred — then superseded: the screenshot proved the stale-page half of R2 is real (browser pinned the 0357 shell), so `Cache-Control: no-store` on the dashboard shell landed in this task; API `no-store` stays deferred (edge already reports DYNAMIC, and bust() covers it).

**Autopilot seats (Manager order "auto mode lock برین seats ها"):** QA re-passed on the final diff (`QA_PASSED` — origin URL consistent with all clients, retry single-fire, no-store scoped to shell) and review re-approved (`PO_REVIEW_PENDING`, Low, no blocking issues).

**Closure approval (Manager, 2026-10-28):** "Approved for closure" via the question tool after live confirmation ("حل شد"). Commit path is `custom_context_commit_and_clean_task` only.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `bde64ad670d07996c9770d971dc19e2af8a53e7c`
<!-- END_GIT_DIFF -->
