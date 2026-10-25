# Task 344: Planner dashboard and Prompt Composer on Graphite Desk

**File:** `tasks/completed/344-planner-dashboard-and-prompt-composer-on-graphite-desk.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Supersedes:** [0339, 0343]
**Meta:** true
**Created:** 2026-10-24 19:19 UTC
**Bundled:** 2 tasks

## Supersedes

- `0339-planner-dashboard-ui-overhaul-and-task-modal` — planner dashboard overhaul, guarded `GET /api/task`, task modal.
- `0343-prompt-composer-graphite-desk` — Prompt Composer port to the design system.

Both sources were archived by `bundle_tasks` with `superseded-by: 344-…`; history stays reachable through `git log --follow -- tasks/archive/<id>-*.md`. The all-or-nothing gate is `## Bundled Checklist (All-or-Nothing)` below: if any line fails QA, the whole META returns to `in-progress`.

## Goal

Unified execution of 2 related small tasks as a single META task to eliminate sequential overhead. This META bundles tasks [0339, 0343] — "Planner dashboard and Prompt Composer on Graphite Desk" — into one branch, one diff, and one QA gate (all-or-nothing). Every requirement below is preserved **verbatim** from its source task; no summarization or omission is allowed.

> ⚠️ **Guardrail Warning:** Combined source size is 1146 LOC (> 400). Unified META diff may be large and hard to review. Consider splitting into two METAs.

**Source IDs:** [0339, 0343]
**Next ID:** 344 (discovered via `find tasks -name "*.md" | sort -n | tail -1 +1`)
**Archive Policy:** Source files will be moved to `tasks/archive/` with `superseded-by: 344-planner-dashboard-and-prompt-composer-on-graphite-desk` and remain reachable via `git log --follow` (never purged until META is completed).

## Manager's Notes

**Bundle Decision (2026-08-21):** Manager requested fully automatic bundling with archive (not purge). This META was generated deterministically by the `bundle_tasks` MCP tool to execute 2 small related tasks together and speed up turnaround.

**Traceability:**
- Supersedes [0339, 0343] — see per-source verbatim blocks below
- Archive: each source moved via `git mv` to `tasks/archive/` with `**Superseded-By:** 344-planner-dashboard-and-prompt-composer-on-graphite-desk` header + superseded footer
- Rollback: `git mv tasks/archive/<id>-*.md tasks/backlog/` + delete META file

**Guardrails Applied:**
- Cap 6 per bundle — this bundle has 2 (✅ within cap)
- Verbatim preservation — every source Goal/AC/TODO/Risk copied verbatim below (SHA comparison available in bundler dry-run)
- Diff-size check — combined 1146 LOC (⚠️ exceeds 400 — consider split)

## Source Bundles (Verbatim Preservation)

The following blocks are **verbatim copies** of each source task's critical sections. They are the source of truth; the checklist that follows is derived from them. Do not edit them manually — they were extracted by the bundler to guarantee zero omission.

### Source Task 0339: Planner dashboard UI/UX overhaul and full-screen task modal

**Original File:** `/home/mohammad/Develop/Projects/cognitive-lead-hq/tasks/qa/0339-planner-dashboard-ui-overhaul-and-task-modal.md` → `tasks/archive/0339-planner-dashboard-ui-overhaul-and-task-modal.md` (after bundling)

**Title:** Planner dashboard UI/UX overhaul and full-screen task modal

#### Goal (verbatim)

Revamp the Planner dashboard UI/UX to eliminate vertical clutter and enhance task visibility: cap lane heights with inner scroll and sticky headers, collapse the 320+ item Archive lane by default with a count toggle, add live search filtering, add a backend `GET /api/task` endpoint, and add a polished full-screen modal with standalone Markdown rendering so clicking any task reveals its complete content, todos, acceptance criteria, and Git diff.

#### Manager's Notes (verbatim)

- The archive list currently stretches the page too far; it must be collapsed by default with an expand toggle showing the item count.
- Lanes need a fixed viewport height with clean internal scrolling and sticky card headers.
- A search input at the top of the board should instantly filter tasks across lanes by ID or title.
- Clicking any task card (or an inspect button) must open an aesthetic full-screen modal that renders the task file's Markdown cleanly (including `## Factual Git Diff`) without third-party build tooling.
- Zero external CDN dependencies: keep assets self-contained in `mcp-planner-server/static/`.

## Audit Addendum (2026-10-24, live board)

- [x] Replace the hand-rolled Jalali converter with vendored `jalaali-js`; timeline shows Jalali primary and Gregorian secondary
- [x] Mark the session cookie `Secure` behind the tunnel, reject relative `?project_root=` with 400, emit baseline security headers

## Acceptance Criteria (verbatim)

- [x] `GET /api/task?path=tasks/...` returns the task Markdown or 403/404 when unauthorized or missing
- [x] Kanban lanes on the dashboard are height-capped with internal vertical scrolling and sticky headers
- [x] Archive lane is collapsed by default and displays a toggle button with the task count
- [x] Search input instantly filters visible cards by task ID or title without server round-trip
- [x] Clicking a task opens a full-screen dark-mode modal displaying rendered Markdown of the task and its diff
- [x] Zero external CDN network dependencies: markdown parser is self-contained in `static/`
- [x] Full planner test suite passes with exit code 0
- [x] Dashboard follows `DESIGN.md` (Graphite Desk tokens; no hex outside the palette)

#### Local TODOs (verbatim)

- [x] Add `GET /api/task` endpoint in `mcp-planner-server/server.py` returning the raw Markdown content of a task file by path or ID (auth and project-scoping enforced)
- [x] Update `mcp-planner-server/static/index.html` with capped lane heights (`max-height: calc(100vh - 280px); overflow-y: auto`) and sticky card headers
- [x] Implement collapsible Archive drawer in `index.html` (collapsed by default with toggle button)
- [x] Add live search filter bar above Kanban lanes
- [x] Implement full-screen Task Detail Modal (`#task-modal`) with embedded lightweight Markdown rendering (pure JS / self-contained) for task body and diff
- [x] Write unit tests for `GET /api/task` in `tests/test_planner_server.py`
- [x] Deploy updated files to `~/.config/opencode/mcp-planner-server/` and restart `mcp-planner`
- [x] Update `CHANGELOG.md` and verify `lint_task_file`
- [x] Re-skin the dashboard to `DESIGN.md` (Graphite Desk): one palette, radius scale 4/6/8/12, mono ids, semantic lane chips, no gradients

#### Risk & Rollback (verbatim)

- **Risk:** Large task files or diffs might lag modal rendering.
- **Mitigation:** Use a lightweight, synchronous, pure JS markdown parser and cap max rendered lines if needed.
- **Rollback plan:** Revert `index.html` and `server.py` changes.

---

### Source Task 0343: Port Prompt Composer to the Graphite Desk design system

**Original File:** `/home/mohammad/Develop/Projects/cognitive-lead-hq/tasks/backlog/0343-prompt-composer-graphite-desk.md` → `tasks/archive/0343-prompt-composer-graphite-desk.md` (after bundling)

**Title:** Port Prompt Composer to the Graphite Desk design system

#### Goal (verbatim)

Make `tools/prompt-composer/index.html` follow `DESIGN.md` (Graphite Desk) instead of raw Tailwind defaults, so both Cognitive Lead surfaces share one palette, one radius scale, one type hierarchy, and one chip language.

#### Manager's Notes (verbatim)

- Source of truth: `DESIGN.md` at the repo root (chosen direction A, 2026-10-24). No new colors outside the palette.
- The composer currently loads `https://cdn.tailwindcss.com` and uses default slate/blue plus six rainbow preset pills; both contradict the system.
- Planner dashboard was re-skinned in task 339 to the same tokens; this task brings the composer into parity.

#### Acceptance Criteria (verbatim)

- [ ] Zero external network dependencies at runtime (no CDN script, no webfont link)
- [ ] Every color and radius in the file resolves to a DESIGN.md token
- [ ] Preset chips use neutral plus at most four semantic tints
- [ ] All existing composer actions still work (project CRUD, fetch, generate, copy)
- [ ] Focus states are visible on every interactive element

#### Local TODOs (verbatim)

- [ ] Replace the Tailwind CDN with a local `<style>` block built from the DESIGN.md tokens (`--bg`, `--surface`, `--surface-raised`, `--border`, `--text`, `--muted`, `--accent`, `--accent-ink`, four state colors, `--mono`)
- [ ] Rebuild the layout classes (container 960px, 8px grid, 24px page padding) so no Tailwind utility classes remain
- [ ] Convert preset pills to neutral chips with at most four semantic tints
- [ ] Normalise radii to 4/6/8/12 and remove all box-shadows except the manage dialog
- [ ] Apply mono type to generated markdown output and system-prompt textarea
- [ ] Keep every behaviour identical: localStorage projects, fetch system prompt, copy to clipboard, dialog

#### Risk & Rollback (verbatim)

- **Risk:** removing Tailwind means reimplementing layout by hand; a missed utility silently changes spacing.
- **Rollback:** restore the previous `index.html` from git; the tool is standalone.

---


## Bundled Checklist (All-or-Nothing)

> **QA Gate (all-or-nothing):** Every line below maps to one source acceptance criterion. If ANY line fails QA, the entire META is `QA_REJECTED` and returns to `in-progress`. Do not partially close.

- [x] [0339] `GET /api/task?path=tasks/...` returns the task Markdown or 403/404 when unauthorized or missing
- [x] [0339] Kanban lanes on the dashboard are height-capped with internal vertical scrolling and sticky headers
- [x] [0339] Archive lane is collapsed by default and displays a toggle button with the task count
- [x] [0339] Search input instantly filters visible cards by task ID or title without server round-trip
- [x] [0339] Clicking a task opens a full-screen dark-mode modal displaying rendered Markdown of the task and its diff
- [x] [0339] Zero external CDN network dependencies: markdown parser is self-contained in `static/`
- [x] [0339] Full planner test suite passes with exit code 0
- [x] [0339] Dashboard follows `DESIGN.md` (Graphite Desk tokens; no hex outside the palette)
- [x] [0343] Zero external network dependencies at runtime (no CDN script, no webfont link)
- [x] [0343] Every color and radius in the file resolves to a DESIGN.md token
- [x] [0343] Preset chips use neutral plus at most four semantic tints
- [x] [0343] All existing composer actions still work (project CRUD, fetch, generate, copy)
- [x] [0343] Focus states are visible on every interactive element
- [x] Traceability: All 2 source tasks are archived with superseded-by marker and reachable via `git log --follow`

## Local TODOs

- [x] Step 1: Validate META bundle — confirm all 2 source requirements are captured verbatim below
- [x] Step 2: Implement unified changes covering all bundled tasks (single diff, single branch)
- [x] [0339] Add `GET /api/task` endpoint in `mcp-planner-server/server.py` returning the raw Markdown content of a task file by path or ID (auth and project-scoping enforced)
- [x] [0339] Update `mcp-planner-server/static/index.html` with capped lane heights (`max-height: calc(100vh - 280px); overflow-y: auto`) and sticky card headers
- [x] [0339] Implement collapsible Archive drawer in `index.html` (collapsed by default with toggle button)
- [x] [0339] Add live search filter bar above Kanban lanes
- [x] [0339] Implement full-screen Task Detail Modal (`#task-modal`) with embedded lightweight Markdown rendering (pure JS / self-contained) for task body and diff
- [x] [0339] Write unit tests for `GET /api/task` in `tests/test_planner_server.py`
- [x] [0339] Deploy updated files to `~/.config/opencode/mcp-planner-server/` and restart `mcp-planner`
- [x] [0339] Update `CHANGELOG.md` and verify `lint_task_file`
- [x] [0339] Re-skin the dashboard to `DESIGN.md` (Graphite Desk): one palette, radius scale 4/6/8/12, mono ids, semantic lane chips, no gradients
- [x] [0343] Replace the Tailwind CDN with a local `<style>` block built from the DESIGN.md tokens (`--bg`, `--surface`, `--surface-raised`, `--border`, `--text`, `--muted`, `--accent`, `--accent-ink`, four state colors, `--mono`)
- [x] [0343] Rebuild the layout classes (container 960px, 8px grid, 24px page padding) so no Tailwind utility classes remain
- [x] [0343] Convert preset pills to neutral chips with at most four semantic tints
- [x] [0343] Normalise radii to 4/6/8/12 and remove all box-shadows except the manage dialog
- [x] [0343] Apply mono type to generated markdown output and system-prompt textarea
- [x] [0343] Keep every behaviour identical: localStorage projects, fetch system prompt, copy to clipboard, dialog
- [x] Step 18: Verify all bundled checklist items and run lint_task_file + verification-before-completion
- [x] Step 19: Update CHANGELOG.md and record Verification Evidence

## Acceptance Criteria

- [x] [0339] `GET /api/task?path=tasks/...` returns the task Markdown or 403/404 when unauthorized or missing
- [x] [0339] Kanban lanes on the dashboard are height-capped with internal vertical scrolling and sticky headers
- [x] [0339] Archive lane is collapsed by default and displays a toggle button with the task count
- [x] [0339] Search input instantly filters visible cards by task ID or title without server round-trip
- [x] [0339] Clicking a task opens a full-screen dark-mode modal displaying rendered Markdown of the task and its diff
- [x] [0339] Zero external CDN network dependencies: markdown parser is self-contained in `static/`
- [x] [0339] Full planner test suite passes with exit code 0
- [x] [0339] Dashboard follows `DESIGN.md` (Graphite Desk tokens; no hex outside the palette)
- [x] [0343] Zero external network dependencies at runtime (no CDN script, no webfont link)
- [x] [0343] Every color and radius in the file resolves to a DESIGN.md token
- [x] [0343] Preset chips use neutral plus at most four semantic tints
- [x] [0343] All existing composer actions still work (project CRUD, fetch, generate, copy)
- [x] [0343] Focus states are visible on every interactive element
- [x] Traceability: All 2 source tasks are archived with superseded-by marker and reachable via `git log --follow`

- [x] [audit] Jalali dates come from `jalaali-js`; the timeline shows both calendars correctly
- [x] [audit] HTTPS login sets a `Secure` cookie; relative root returns 400; `nosniff`/`Referrer-Policy`/`X-Frame-Options`/HSTS present

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/test_planner_server.py -q`
- **Expected result:** all planner tests pass, including the three new audit tests
- **Actual result:** `100 passed, 2 warnings in 36.01s`; both inline scripts parse; live board confirms `Secure` cookie, HSTS + three headers, 400 on a relative root, and 200 on `/static/vendor/jalaali.min.js`
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Checklist omission — mitigated by verbatim copy + SHA-length comparison of source AC vs bundled checklist; script fails if mismatch >0.
- **Risk:** Mega-diff >400 LOC unreviewable — warning emitted; Manager should split if >400.
- **Risk:** Accidental purge — mitigation: only `git mv` to archive, never `git rm`; purge blocked until META reaches `tasks/completed/`.
- **Rollback plan:** `git mv tasks/archive/<id>-*.md tasks/backlog/<id>-*.md` for each superseded [0339, 0343], remove Superseded-By footer, delete or archive `tasks/backlog/344-planner-dashboard-and-prompt-composer-on-graphite-desk.md` as abandoned. No HQ code beyond bundler is affected.

---

## Execution Log & Reasoning

**Bundling (2026-10-24, Manager order "تسک ۳۳۹ و ۳۴۳ باندل کن"):** `bundle_tasks` created this META and archived both sources — `tasks/qa/0339-planner-dashboard-ui-overhaul-and-task-modal.md` and `tasks/backlog/0343-prompt-composer-graphite-desk.md` — with `superseded-by: 344-…` and the `Superseded-At` footer, so `git log --follow` keeps both histories reachable. Claimed through `claim_next`, so the META is in `tasks/in-progress/` and the QA gate is all-or-nothing across both sources.

**State carried in:** task 339's planner work is already implemented, tested (97 passed) and deployed to `~/.config/opencode/mcp-planner-server/`, and its files are staged in the index (`mcp-planner-server/server.py`, `static/index.html`, `tests/test_planner_server.py`, `README.md`, `DECISIONS.md`, plus `DESIGN.md` and `CHANGELOG.md`). Its dashboard is already re-skinned to Graphite Desk. Task 343 is **not started**: the Prompt Composer still loads the Tailwind CDN and uses rainbow preset pills.

**Remaining work for this META:** port `tools/prompt-composer/index.html` to the DESIGN.md tokens (drop the CDN, 960px container, 4/6/8/12 radii, neutral chips with at most four semantic tints, mono output pane), then run the planner suite plus the composer script parse, refresh staging — including the two archived task files, whose staged blobs predate the superseded footer — and hand the whole META to QA.

**Library pivot (2026-10-24, Manager: "بریم سراغ یه library"):** the hand-written Graphite Desk CSS is replaced by **Bootstrap 5.3.3, vendored** (no CDN, no build step). Assets live in `tools/prompt-composer/vendor/` and `mcp-planner-server/static/vendor/`; `theme.css` maps the DESIGN.md palette onto Bootstrap variables and adds `.chip`, `.page`, `.label`, `.gd-dialog`, `.mono`. The Prompt Composer was rewritten on that stack: Tailwind CDN and every utility class removed, preset pills become neutral chips with four semantic tints, manage dialog restyled, behaviour untouched (verified: inline script parses, only the intentional GitHub system-prompt fetch remains as a URL). DESIGN.md section 4 now documents the Bootstrap mapping as the implementation baseline. The Planner dashboard is the last piece of this META and still runs the pre-pivot CSS.

**Planner port completed (same session):** `mcp-planner-server/static/index.html` was rewritten on Bootstrap 5.3 with `/static/theme.css` (shared tokens plus a planner layer: `.gd-overlay`, `.gd-panel`, `.lane-card` with sticky header, `.task-row`, `.cal-day`, `.ms-node`, markdown/diff typography). All behaviour is preserved: stats, pacing bar, project switcher, lane grid with search and collapsible Archive remembered in `localStorage`, milestone collapse, 14-day Jalali timeline, auth badge/login/logout, task modal with the self-contained Markdown renderer, and the 30 s poll. `mcp-planner-server/static/vendor/` carries the same two Bootstrap files. `.gitattributes` marks `*.min.css` / `*.min.js` as `-diff` so the vendored blobs do not bury reviewable hunks in this task's Factual Git Diff.

**Verification:** `tests/test_planner_server.py` → 97 passed, exit 0 (backend untouched). Both inline scripts parse under `new Function`. No `http(s)://` or inline `<style>` remains in either page. Deployed to `~/.config/opencode/mcp-planner-server/static/` with `cmp` byte-identity for `index.html`, `theme.css` and both vendor files; `mcp-planner` restarted and serves `/` 200, `/static/theme.css` 200, `/static/vendor/bootstrap.min.css` 200.

**Live board audit (2026-10-24, admin session supplied by the Manager):** `https://board.surfshield.org/` was exercised over HTTPS. Fixes applied and verified live:

- **Jalali:** the hand-rolled converter is gone; `jalaali-js` 1.2.6 is vendored (`static/vendor/jalaali.min.js`, 2.9KB, MIT) and loaded before the app script. `formatJalali()` and the 14-day timeline now use `jalaali.toJalaali`, with the Jalali day as the primary cell value, the Gregorian day underneath, the month name on the first of each Jalali month, and a full `JD Month JY · YYYY-MM-DD` tooltip. Missing library degrades to Gregorian-only instead of throwing.
- **Cookie:** `set_cookie` now passes `secure=_is_https(request)`, which trusts `X-Forwarded-Proto` first and falls back to the request scheme. Live login returns `…; HttpOnly; Max-Age=604800; Path=/; SameSite=lax; Secure`.
- **Scoping:** new `_relative_root()` guard on `/api/status` and `/api/task` returns `400 {"error": "project_root must be absolute"}` instead of resolving a relative path against the daemon cwd.
- **Headers:** `_SecurityHeaders` middleware sets `X-Content-Type-Options: nosniff`, `Referrer-Policy: same-origin`, `X-Frame-Options: DENY`, plus HSTS on HTTPS. Confirmed on the live response.
- **Out of scope:** `/mcp` still answers `421` remotely instead of the documented `404`; no `cloudflared` config exists on this host, so the ingress fix belongs to Cloudflare.

**Verification after the audit:** 100 passed, exit 0 (three new tests: security headers incl. HSTS-on-proxy, relative-root 400 on both routes, `Secure` cookie behind `X-Forwarded-Proto: https`). Deployed `server.py`, `index.html`, `theme.css` and `vendor/jalaali.min.js`; `mcp-planner` restarted, all live checks green.

**Autopilot QA/review (2026-10-24):**

- QA turn: `VERDICT: QA_PASSED` — no dead bindings after the Bootstrap port, archive/search/modal/poll intact, Jalali fallback sound, `_relative_root` 400s before resolution, cookie and headers correct, checklist 14/14, no scope creep. Unseen tail and vendor binaries marked UNVERIFIABLE (not rejected).
- Reviewer turn: technically approved — `PO_REVIEW_PENDING`. I1 (CHANGELOG mentions the executor trimming rule whose file is not in this diff) accepted with rationale: that rule is deployed under `~/.config/opencode/agents/` and staged separately, and the CHANGELOG entry documents a real change; I2 duplicated theme tokens are deliberate so each surface runs standalone; I3 modal elevation left as is.

**Known external gap:** `/mcp` returns `421` through the tunnel instead of the documented `404`; the ingress rule lives in Cloudflare, not in this repo.

**Manager closure approval (2026-10-24), verbatim: "Approved for closure".**

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `dc31a5820ef1198ad8f2905bae55fc72a86a43e6`
<!-- END_GIT_DIFF -->
