# Task 344: Planner dashboard and Prompt Composer on Graphite Desk

**File:** `tasks/qa/344-planner-dashboard-and-prompt-composer-on-graphite-desk.md`
**Source:** manager
**Type:** feature
**Status:** in-progress
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

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.gitattributes b/.gitattributes
new file mode 100644
index 0000000..040a312
--- /dev/null
+++ b/.gitattributes
@@ -0,0 +1,5 @@
+# Vendored third-party assets are committed but never expanded in diffs:
+# they are minified one-liners, and a 228KB CSS blob inside a task's
+# Factual Git Diff buries the reviewable hunks.
+*.min.css -diff
+*.min.js -diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 74e779a..d53ff99 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **`DESIGN.md` — Graphite Desk, one contract for both UIs:** the repo had no design system, so the Planner dashboard carried scattered slate/cyan tokens with mixed radii and the Prompt Composer was raw Tailwind defaults with six rainbow preset pills. The Manager reviewed four proposals and chose **A · Graphite Desk**: near-black slate surfaces (`#0b0e14` / `#141a23` / `#1b2430`), hairline borders `#263141`, one mint accent `#5eead4` with ink `#04211d`, four state colours, an 8px grid, a fixed 4/6/8/12 radius scale, Inter for UI and JetBrains Mono for ids/paths/diffs, and no shadows outside modals. The file also fixes component specs (buttons, lanes, tabs, inputs, preset chips, diff blocks, task modal), layout widths (1200 / 960), motion (120/180ms with reduced-motion honoured) and Stitch prompts. The Planner dashboard was re-skinned onto these tokens under task 339 — gradient gauge replaced, lane chips reduced to neutral plus semantic text, hard-coded greys removed — deployed byte-identical to `~/.config/opencode/mcp-planner-server/static/` and served live by `mcp-planner`. The Prompt Composer port is task 343 so it can drop the Tailwind CDN without touching this diff.
+
 - **Planner dashboard overhaul and a guarded task reader (Task 339):** the board is usable with 330+ tasks on it. `GET /api/task?id=<id>` / `?path=tasks/<lane>/<file>.md` returns `{id, path, lane, title, markdown}` so the new full-screen modal can render a task's whole body — todos, acceptance criteria, and `## Factual Git Diff` — with `id` winning when both params arrive. The route is deliberately not a file-read primitive: the new `_safe_task_path` accepts exactly three segments, a lane from `TASK_LANES`, a `.md` suffix, and no absolute prefix, drive colon, backslash, or `..`/`.`, then resolves and re-checks containment inside the project root; authorization reuses `AuthState.project_allowed` and the `_api_status` fallback to a session's first allowed root. Status mapping is explicit — 400 missing param, 401 no session, 403 outside grants *and* unsafe path (never 404, so the route cannot confirm whether a file exists), 404 unknown id, 500 unexpected; the `_api_status` blanket `except → 200 {"error": …}` pattern is not copied. `_task_brief` now carries `path` so cards can deep-link. The dashboard (`static/index.html`, still zero external URLs) caps each lane at `calc(100vh - 280px)` with inner scrolling and a sticky header, collapses the Archive lane behind an `Archive (N)` toggle remembered in `localStorage`, adds a client-only search input filtering by id/name/title, and opens the task modal through one delegated listener on the grid so the 30 s poll cannot drop the binding. The Markdown renderer is inline and self-contained: source is HTML-escaped first, then fences, headings, lists, task checkboxes, blockquotes, tables, and inline emphasis are added, diffs get `--success`/`--danger` line colouring, rendering stops at 2000 lines, and links are limited to same-origin or in-page targets. Docs: component `README.md` route table plus `DECISIONS.md` ADR-007. Verified: 97/97 planner tests pass (17 new: by id, by path, int-normalized id, 404, 400, eight traversal shapes at 403, route registration, 401, cross-project viewer 403, traversal over HTTP, open mode), `py_compile` and a JS parse of the inline script are clean, deployed `server.py`/`README.md`/`DECISIONS.md`/`static/index.html` are byte-identical to the repo copies, and the live unit on `127.0.0.1:8108` serves the new dashboard markup while `/api/task` answers 401 without a session and 400 with no param.
 
 - **Plugin references synced to the new tool set and evidence contract (Task 341):** a graph scan over this worktree (4,766 nodes, 6,788 links) plus targeted greps found four live documents lagging behind the two plugin releases. `agents/cognitive-executor.md` now carries `compact_stats` in the Smart Compact section and in the protocol contract (no inputs, read-only, same formatter as `/magic-stats`, never a poll), and states that every `goal_set` starts a fresh empty evidence sidecar while the legacy `.opencode/goal-evidence.json` is read only until the session owns its own, which is what stopped a finished goal's failing command from gating later ones. `docs/compaction.md` documents the stats tool under Agent-callable tools and the evidence reset in the goal-plugin section; `README.md`'s plugin lane carries both. `tests/test_prompt_sync.py` pins `compact_stats` so the executor cannot drift back, and the smart-compact policy memory shard lists the third tool plus the installed commit `2e702680`. Verified: prompt-sync tests exit 0, `lint_system_prompt_sync` consistent, `prettier --check` clean.
@@ -41,6 +43,12 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Changed
 
+- **Public board hardening and a real Jalali library (META 344 audit):** an authorized audit of `https://board.surfshield.org/` produced four fixes. The dashboard's Jalali conversion was a hand-copied algorithm with wrong leap-year behaviour and the timeline rendered Gregorian numbers only under a "Gregorian + Jalali" heading; `jalaali-js` 1.2.6 is now vendored (`static/vendor/jalaali.min.js`, MIT, 2.9KB) and the timeline shows the Jalali day as primary, the Gregorian day beneath, the month name at each Jalali month start, and a full tooltip. The session cookie now carries `Secure` when the request arrives over HTTPS (`X-Forwarded-Proto` aware, since the daemon sits behind a tunnel), a relative `?project_root=` is rejected with `400 {"error":"project_root must be absolute"}` instead of silently resolving against the daemon cwd, and a `_SecurityHeaders` middleware adds `X-Content-Type-Options: nosniff`, `Referrer-Policy: same-origin`, `X-Frame-Options: DENY` plus HSTS on HTTPS. Verified live on the board (Secure cookie, all four headers, 400 on the relative root, 200 on the vendored script) and by 100 passing planner tests, three of them new. `/mcp` still answers `421` remotely instead of the documented `404`; no cloudflared config exists on this host, so that ingress fix is Cloudflare-side.
+
+- **UI stack moves to Bootstrap 5.3, vendored; Prompt Composer ported:** the hand-rolled CSS (Graphite Desk tokens written as bespoke rules) was replaced with a real component library. `bootstrap.min.css` and `bootstrap.bundle.min.js` (5.3.3) are vendored under `tools/prompt-composer/vendor/` and `mcp-planner-server/static/vendor/`, and a single `theme.css` maps the DESIGN.md palette onto `--bs-*` variables (body background, border, primary accent, radii 4/6/8/12, focus ring, mono stack) plus five missing primitives (`.chip`, `.page`, `.label`, `.gd-dialog`, `.mono`). `tools/prompt-composer/index.html` was rewritten on that stack: the Tailwind CDN is gone, all Tailwind utility classes are gone, preset pills became neutral chips with at most four semantic tints (info/success/warning/danger), the manage dialog uses `.gd-dialog`, and every behaviour is preserved (project CRUD via localStorage, system-prompt fetch, generate, copy). `DESIGN.md` now states the Bootstrap mapping as the implementation baseline. Verified: inline script parses, zero third-party URLs at runtime (only the intentional GitHub fetch for the system prompt). The Planner dashboard port is still pending inside META 344.
+
+- **Control payloads are never trimmed (executor rule only):** a Brain `hands_*`/`hotfix` block is read whole, never sliced for context. `agents/cognitive-executor.md` gains a *Code-mode output discipline* rule in the Brain Bridge call step — the `execute` runtime returns the `return` value verbatim, only its own `maxOutputBytes` may cut it, and a cut is signalled by `truncated: true`, so the Hands returns `{status, block_count, model}` and keeps the block whole instead of printing a prefix; a `truncated` flag means re-read the exact range. The rule deliberately stays out of `docs/opencode-shell-strategy.md`: that file governs non-interactive shell behaviour, and the trimming problem lives in tool calling and code mode, not in bash. Deployed to `~/.config/opencode/agents/cognitive-executor.md` byte-identical. Verified: 103 prompt/MCP tests pass.
+
 - **Brain consolidated onto `muse-spark-1.3-contributor` at `xhigh`, with the API key rotated to OpenCode's live credential:** the operator moved every Brain tier onto the cheap Go model, so planning, implementation, QA, and review share one route and one preset. `BRAIN_MODEL`, `BRAIN_MODEL_LOW`, and `BRAIN_MODEL_HIGH` now all read `muse-spark-1.3-contributor` in both the repo `.env` and the effective global `~/.config/opencode/.env`; `BRAIN_API_BASE` stays on the zen-proxy `/go/resp` mount and `BRAIN_REASONING_EFFORT` stays `xhigh`. `.env.example`'s preset comment drops its now-false "current production setting" label from the balanced block, since production is the economy preset. The first smoke test failed `429 GoUsageLimitError` (monthly) on `muse-spark-1.3-contributor` and on `gpt-6-luna`, which was account-level, not routing: the `BRAIN_API_KEY` in both env files belonged to a drained Go workspace. OpenCode's live credential is **not** `~/.local/share/opencode/auth.json` (that copy answers `401 Invalid credential` on the same gateway, both through the proxy and direct); it lives in the opencode V2 store at `~/.local/share/opencode/opencode.db`, table `credential` (`integration_id: opencode-go`, `active = 1`, JSON value carrying `key`). That key was copied into `BRAIN_API_KEY` in both env files and `mcp-brain` restarted. Verified: `zen-proxy` and `mcp-brain` enabled/active, `/health` 200, `/go/resp/models` serves the id, a direct gateway probe returns 200, and a `brain_turn` smoke test answered `SMOKE_OK` with `model=muse-spark-1.3-contributor`, `status=completed`, `reasoning_tokens=2216` (xhigh in effect), 25,782 total tokens.
 
 ### Fixed
diff --git a/DESIGN.md b/DESIGN.md
new file mode 100644
index 0000000..bbb9f8d
--- /dev/null
+++ b/DESIGN.md
@@ -0,0 +1,157 @@
+---
+name: Cognitive Lead Console
+colors:
+  background: "#0B0E14"
+  surface: "#141A23"
+  surfaceRaised: "#1B2430"
+  border: "#263141"
+  text: "#E6EBF2"
+  textMuted: "#8C99AB"
+  accent: "#5EEAD4"
+  accentInk: "#04211D"
+  success: "#34D399"
+  warning: "#FBBF24"
+  danger: "#F87171"
+  info: "#7DD3FC"
+---
+
+# Design System: Cognitive Lead Console
+
+## 1. Visual Theme & Atmosphere
+
+A quiet instrument panel. The interface is dark, flat, and deliberately low-chroma: near-black slate surfaces, hairline borders, and a single mint accent that only appears where action or state lives. Nothing glows, nothing floats; depth comes from one step of surface lightness, never from stacked shadows. The mood is a terminal that learned typography — precise, calm, and dense enough to show 330 tasks without the page turning into a wall.
+
+Density is a feature, not an accident. Rows are 32px, the grid is 8px, and vertical rhythm is tight because the reader is scanning status, not reading prose. Mono type carries every identifier, path, byte count, and diff line, so machine data is visually separable from human text at a glance. The result should feel like a tool built by someone who reads their own logs.
+
+## 2. Color Palette & Roles
+
+Semantic tokens only. Components never hard-code hex; they reference these names.
+
+### Primary Foundation
+
+- **Void** `#0B0E14` (`--bg`) — page background, input backgrounds, code blocks.
+- **Panel** `#141A23` (`--surface`) — cards, lanes, modal body, table headers.
+- **Panel Raised** `#1B2430` (`--surface-raised`) — hover, sticky headers over scroll, secondary buttons.
+- **Hairline** `#263141` (`--border`) — every 1px border and divider. No other border color exists.
+
+### Accent & Interactive
+
+- **Signal Mint** `#5EEAD4` (`--accent`) — primary action, focus ring, active tab underline, selected state. One accent, used sparingly.
+- **Ink on Mint** `#04211D` (`--accent-ink`) — text and icons sitting on the accent fill.
+
+### Typography & Text Hierarchy
+
+- **Chalk** `#E6EBF2` (`--text`) — primary text.
+- **Ash** `#8C99AB` (`--text-muted`) — labels, metadata, counts, placeholders.
+
+### Functional States
+
+- **Pass** `#34D399` (`--success`) — QA passed, closed, healthy.
+- **Hold** `#FBBF24` (`--warning`) — pending review, quota near, truncated output.
+- **Break** `#F87171` (`--danger`) — rejected, forbidden, destructive.
+- **Note** `#7DD3FC` (`--info`) — in-progress, neutral notice.
+
+State colors appear as text and 1px borders on a 10% tint of themselves, never as a saturated fill.
+
+## 3. Typography Rules
+
+### Hierarchy & Weights
+
+- **UI family:** `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`.
+- **Data family:** `"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace` — ids, paths, diffs, counts, timestamps, code.
+- **Display 28px / 700 / -0.02em** — page title only (`Planner`, `Prompt Composer`).
+- **Section 20px / 600 / -0.01em** — section headers.
+- **Body 14px / 400 / 1.45** — default text.
+- **Body Small 13px / 400** — table cells, lane rows.
+- **Label 11px / 600 / 0.06em uppercase** — table headers, lane headers, field labels.
+- **Mono 12.5px / 400** — identifiers, hashes, diff lines.
+
+Weights are 400, 500, 600, 700 only. No 800+, no italics except empty-state copy.
+
+### Spacing Principles
+
+Line-height is 1.2 for ≥20px headings and 1.45 for body, never both on the same element. Letter-spacing tightens with size (negative above 20px) and opens on 11px labels. Paragraphs inside task bodies get 6px above and below; list items 2px. Text never sits closer than 4px to a border.
+
+## 4. Component Stylings
+
+### Implementation baseline — Bootstrap 5.3 (vendored)
+
+Both surfaces load `vendor/bootstrap.min.css` and `theme.css` from their own directory. No CDN, no build step, no node toolchain. `theme.css` maps the palette above onto Bootstrap's variables (`--bs-body-bg`, `--bs-border-color`, `--bs-primary`, `--bs-border-radius*`, `--bs-focus-ring-color`, `--bs-font-monospace`) and adds the few primitives Bootstrap lacks: `.chip`, `.page`, `.label`, `.gd-dialog`, `.mono`. Components below therefore name the Bootstrap class where one exists; only what Bootstrap has no equivalent for is a thin custom layer on the same tokens. A screen that needs a class outside this set is a design change, not an implementation detail.
+
+### Buttons
+
+- `btn btn-primary` — accent fill, ink text, radius 6, height 32 (`btn-sm` inside cards).
+- `btn btn-outline-secondary` — hairline border, transparent fill, hover raises the surface.
+- `btn btn-outline-danger` — danger text and border, 12% danger fill on hover only.
+- Ghost actions are `btn btn-outline-secondary` without a fill; text links carry no underline until hover.
+- Transitions 120ms `ease-out` on background, border, color; `btn` never transforms.
+
+### Cards & Lanes
+
+- Radius 8px, 1px `--border`, `--surface` fill, 16px padding, no shadow.
+- Lane card header: 11px uppercase label, count in mono inside a radius-4 chip on `--surface-raised`.
+- Lane body scrolls internally: `max-height: calc(100vh - 280px)`, sticky header painted on `--surface` (opaque, never translucent) with 1px bottom border.
+- Task row: 32px, 13px, hover `--surface-raised`, focus ring 2px `--accent` offset 1px, border-bottom `--border`. Identifier in mono, weight 600.
+
+### Navigation
+
+- Top bar: `--bg`, 1px bottom border, 56px tall, title 20px/600, status chip right-aligned.
+- Tabs: 32px, 13px/500, active = `--text` with 2px `--accent` underline; inactive `--text-muted`, hover `--text`.
+- Project switcher: select styled as a secondary button; never a native-looking control.
+
+### Inputs & Forms
+
+- `form-control` / `form-select` on the page background, 1px border, radius 6px, 13px mono for long-text surfaces and 14px sans for short fields.
+- Focus: 3px accent ring at 35% (`--bs-focus-ring-color`), no layout shift.
+- Labels use `.form-label` (12px muted); placeholders are muted. Errors are 12px danger text under the field.
+- Textareas are resizable vertically only.
+
+### Domain-Specific Components
+
+- **Preset chips (Composer):** radius 6px, 1px `--border`, `--surface-raised`; each preset may carry its semantic tint at 10% background with matching text, but chips never use rainbow pastels — at most four tints (info, success, warning, danger) plus neutral.
+- **Diff block (Planner modal):** `--bg` panel, 1px `--border`, mono 12.5px, `+` lines `--success` at 12% background, `-` lines `--danger` at 12%, hunk headers `--info`. Horizontal scroll, never wrap.
+- **Status chip:** 11px/600 uppercase, 1px border, text color = state, background = 10% of state.
+- **Task modal:** radius 12px, `--surface`, max width 1000px, 92vh ceiling, overlay `rgba(4,7,12,0.72)`, sticky header with title 16px/600 and a mono id·lane meta line.
+
+## 5. Layout Principles
+
+### Grid & Structure
+
+- 8px base grid; 4px allowed only for icon-to-text gaps.
+- Planner content width 1200px, Composer 960px, both centered with 24px page padding (16px under 640px).
+- Lane grid: `repeat(auto-fit, minmax(240px, 1fr))`, gap 16px.
+- Sections separated by 24px, subsections by 12px. Dividers are 1px `--border`, never shadows.
+
+### Whitespace Strategy
+
+Dense but breathable: 16px card padding, 8px between rows, 12px between a label and its control. Page top padding 24px, bottom 32px. Empty states get 20px vertical padding and italic `--text-muted` text.
+
+### Alignment & Visual Balance
+
+Text is left-aligned; numeric columns are right-aligned with tabular figures. Labels sit above controls, never beside them on narrow widths. Icons are 16px, stroke 1.5, optically centered — no decorative illustration.
+
+### Responsive Behavior & Touch
+
+Collapse lane grid to a single column under 720px; lane max-height becomes 60vh there. Minimum touch target 44px on coarse pointers (buttons grow, row height stays 40px). Focus rings must remain visible on dark and light OS themes. Honor `prefers-reduced-motion`: transitions off, state changes instant.
+
+## 6. Design System Notes for Stitch Generation
+
+### Language to Use
+
+"Dark slate instrument panel, near-black background, flat surfaces separated by hairline borders, one mint accent used only for action and focus, mono type for identifiers and diffs, dense 32px rows, no shadows except the modal, no gradients, no rainbow chips."
+
+### Color References
+
+- Background: Void `#0B0E14`; panels: `#141A23`; raised: `#1B2430`; borders: `#263141`.
+- Text: `#E6EBF2`; muted `#8C99AB`; accent `#5EEAD4` with ink `#04211D`.
+- States: success `#34D399`, warning `#FBBF24`, danger `#F87171`, info `#7DD3FC`.
+
+### Component Prompts
+
+- "A kanban lane card on near-black slate: 8px radius, 1px #263141 border, uppercase 11px label with a mono count chip, sticky opaque header, 32px task rows with mono ids, hover lifting the surface one step, no shadow."
+- "A full-screen task modal: 12px radius, #141A23 surface, dimmed #04070C overlay, mono meta line id·lane, rendered markdown body, diff lines tinted green and red at low opacity, close button as ghost."
+- "A composer form: stacked labelled textareas with 6px radius, one mint primary button, neutral chips with at most four semantic tints, generated markdown pane in mono on the darkest surface."
+
+### Incremental Iteration
+
+Change one token at a time and re-render both surfaces. If a screen needs a color that is not in the palette, the screen is wrong, not the palette. Keep the accent for a single purpose per screen; when two actions compete, the secondary becomes ghost.
diff --git a/mcp-planner-server/DECISIONS.md b/mcp-planner-server/DECISIONS.md
index 2ead5e1..0db36be 100644
--- a/mcp-planner-server/DECISIONS.md
+++ b/mcp-planner-server/DECISIONS.md
@@ -96,6 +96,36 @@ the server returns to open local mode with no code change. Full code rollback is
 - **Superseded in part:** the `/mcp` admin-session requirement only — see
 ADR-006 below. Session auth, scoping, and the CLI remain as decided here.
 
+## [2026-10-24] ADR-007: `GET /api/task` is a guarded, lane-confined read
+
+- **Context:** The dashboard needs to open a task's full Markdown (todos,
+  acceptance criteria, `## Factual Git Diff`) in a modal, and `/api/status`
+  ships only briefs. A naive `?path=` reader would turn the loopback dashboard
+  into an arbitrary-file reader; the slice has no containment helper today
+  (`_explicit_project_root` never consults `allowed_projects`, and
+  `_resolve_dashboard_root` resolves any absolute `?project_root=`).
+- **Decision:** `/api/task` accepts `?id=` (resolved through `_find_task_by_id`
+  over `_load_all_tasks`, int-normalized) or `?path=tasks/<lane>/<file>.md`
+  (resolved through the new `_safe_task_path`). `id` wins when both arrive.
+  The path form accepts exactly three segments, a lane from `TASK_LANES`, a
+  `.md` suffix, no `..`/`.`/backslash/drive-colon/absolute prefix, and the
+  resolved candidate must remain inside the project root. Authorization reuses
+  `AuthState.project_allowed` and the `_api_status` fallback to the first
+  allowed root. Status mapping is explicit: 400 missing param, 401 no session,
+  403 outside grants **and** unsafe path (never 404, so the route is not an
+  existence oracle), 404 unknown id/missing file, 500 unexpected — the
+  `_api_status` blanket `except → 200 {"error": …}` is deliberately not copied.
+- **Consequences:** The modal can deep-link by id or path and the route remains
+  a read-only view of `tasks/` Markdown. `GET /` stays unauthenticated by
+  design (ADR-005 changed the data routes only); this route gates like
+  `/api/status`. Traversal attempts are logged as 403 by the client, which
+  cannot distinguish "outside your grants" from "not a task path". Pinned by
+  the `/api/task` tests in `tests/test_planner_server.py` (route presence, by id,
+  by path, 400, 401, 403 cross-project, 403 traversal).
+- **Rollback:** Remove the route from `build_app`, drop `_api_task` and
+  `_safe_task_path`, and remove the route from the route-existence test; the
+  dashboard falls back to the brief-only lanes.
+
 ## [2026-10-24] ADR-006: `/mcp` is auth-free on loopback; the edge is the gate
 
 - **Context:** With auth enabled, the `/mcp` guard returned 401 to every
diff --git a/mcp-planner-server/README.md b/mcp-planner-server/README.md
index 295a4e0..7ca6fa1 100644
--- a/mcp-planner-server/README.md
+++ b/mcp-planner-server/README.md
@@ -29,6 +29,7 @@ dashboard on loopback port 8108.
 | `GET /` | Standalone dark-mode dashboard (no build step). |
 | `GET /static/*` | Dashboard assets (same `static/` directory). |
 | `GET /api/status[?project_root=<abs path>]` | JSON status contract the dashboard renders. |
+| `GET /api/task?id=<id>` or `?path=tasks/<lane>/<file>.md` | One task file as `{id, path, lane, title, markdown}` for the dashboard modal. `id` wins when both are sent. 400 no param, 401 no session, 403 outside grants or unsafe path, 404 unknown, 500 unexpected. |
 | `POST /api/login` | `{"username","password"}` → `{token, username, role, allowed_projects}` + `HttpOnly` cookie. |
 | `POST /api/logout` | Invalidates the session and clears the cookie. |
 | `GET /api/me` | Current user, or 401 when signed out (200 + `note: "auth disabled"` in open mode). |
diff --git a/mcp-planner-server/server.py b/mcp-planner-server/server.py
index ffcd985..e90d23a 100644
--- a/mcp-planner-server/server.py
+++ b/mcp-planner-server/server.py
@@ -1210,6 +1210,35 @@ _DAILY_TARGET = int(os.environ.get("PLANNER_DAILY_TARGET", "3") or 3)
 _WEEKLY_CAPACITY_HOURS = float(os.environ.get("PLANNER_WEEKLY_CAPACITY", "20") or 20)
 
 
+def _relative_root(project_root: Optional[str]) -> bool:
+    """True when an explicit ``?project_root=`` is present but not absolute.
+
+    ``_resolve_dashboard_root`` runs ``Path(...).resolve()`` on whatever it is
+    given, so a relative value silently resolved against the daemon's working
+    directory and reported an empty project. The routes reject it as a 400
+    before resolution instead of answering with the wrong board.
+    """
+    if not project_root or not project_root.strip():
+        return False
+    try:
+        return not Path(project_root).expanduser().is_absolute()
+    except OSError:
+        return True
+
+
+def _is_https(request) -> bool:
+    """True when the request reached the app over HTTPS.
+
+    The dashboard sits behind a Cloudflare Tunnel, so the origin sees plain
+    HTTP and must trust ``X-Forwarded-Proto``. Used to decide the session
+    cookie's ``Secure`` flag and whether HSTS may be sent.
+    """
+    proto = (request.headers.get("x-forwarded-proto") or "").split(",")[0].strip()
+    if proto:
+        return proto.lower() == "https"
+    return request.url.scheme == "https"
+
+
 def _resolve_dashboard_root(project_root: Optional[str] = None) -> Path:
     """Resolve the project root the dashboard reports on.
 
@@ -1312,6 +1341,7 @@ def _task_brief(task: dict) -> dict:
     return {
         "id": match.group(1) if match else name,
         "name": name,
+        "path": task.get("path"),
         "title": task.get("title") or "untitled",
         "lane": task.get("lane"),
         "status": task.get("status") or "open",
@@ -1321,6 +1351,125 @@ def _task_brief(task: dict) -> dict:
     }
 
 
+def _safe_task_path(root: Path, rel_path: str) -> Optional[Path]:
+    """Resolve a lane-relative task Markdown path, or ``None`` when unsafe.
+
+    The dashboard may deep-link a task by path, so the value arrives from the
+    query string and must never become a file-read primitive. Only three
+    shapes are accepted: ``tasks/<lane>/<file>.md`` where ``<lane>`` is one of
+    :data:`TASK_LANES` and the file name carries no path separators. Absolute
+    paths, Windows drive paths, backslashes, ``..`` segments, extra nesting,
+    and non-Markdown suffixes are all rejected. The final candidate is resolved
+    and must still sit inside ``root``.
+
+    Args:
+        root: The resolved project root the request is scoped to.
+        rel_path: The ``?path=`` query value, e.g. ``tasks/qa/0339-x.md``.
+
+    Returns:
+        The resolved :class:`Path` when it is a safe in-tree task file, else
+        ``None`` (the caller maps that to 403 to avoid an existence oracle).
+    """
+    if not rel_path or not isinstance(rel_path, str):
+        return None
+    rel = rel_path.strip()
+    if not rel or rel.startswith("/") or rel.startswith("\\") or ":" in rel:
+        return None
+    if "\\" in rel:
+        return None
+    parts = [part for part in rel.split("/") if part]
+    if ".." in parts or "." in parts:
+        return None
+    if len(parts) != 3 or parts[0] != "tasks" or parts[1] not in TASK_LANES:
+        return None
+    if not parts[2].endswith(".md"):
+        return None
+    try:
+        base = root.resolve()
+        candidate = (base / parts[0] / parts[1] / parts[2]).resolve()
+    except OSError:
+        return None
+    if candidate != base and base not in candidate.parents:
+        return None
+    return candidate
+
+
+def _api_task(
+    project_root: Optional[str] = None,
+    task_id: Optional[str] = None,
+    rel_path: Optional[str] = None,
+    auth: Optional[AuthState] = None,
+) -> dict:
+    """Return one task file as JSON (GET /api/task).
+
+    The dashboard's task modal needs the raw Markdown of a task, including the
+    ``## Factual Git Diff`` section, so this route returns the parsed record's
+    ``raw`` text verbatim alongside its identity fields. ``id`` wins over
+    ``path`` when both are present.
+
+    Error contract (mapped to status codes by the route):
+
+    * ``missing param`` -> 400 when neither ``id`` nor ``path`` is given,
+    * ``unauthenticated`` -> 401 when auth is enabled and no session cookie,
+    * ``forbidden`` -> 403 when the root is outside the session's grants or
+      the requested path fails the containment guard (never 404, so the route
+      cannot be used to probe for file existence),
+    * ``not found`` -> 404 for an unknown id or a safe path that does not exist,
+    * ``internal error`` -> 500, never a 200 envelope.
+
+    Args:
+        project_root: Optional absolute root from ``?project_root=``.
+        task_id: Optional numeric-ish task id from ``?id=``.
+        rel_path: Optional ``tasks/<lane>/<file>.md`` from ``?path=``.
+        auth: Optional session view; ``None`` means open local mode.
+
+    Returns:
+        A JSON-serialisable dict; on failure a dict with an ``error`` key.
+    """
+    if not task_id and not rel_path:
+        return {"error": "missing param: id or path required"}
+    if auth is not None and not auth.authenticated:
+        return {"error": "unauthenticated"}
+
+    workspace_root = _resolve_dashboard_root(project_root)
+    if auth is not None and not auth.project_allowed(workspace_root):
+        if project_root and project_root.strip():
+            return {"error": "forbidden"}
+        fallback = _first_allowed_root(auth)
+        if fallback is None:
+            return {"error": "forbidden"}
+        workspace_root = fallback
+
+    try:
+        if task_id:
+            record = _find_task_by_id(
+                _load_all_tasks(workspace_root), str(task_id).strip()
+            )
+            if record is None:
+                return {"error": "not found"}
+        else:
+            safe_path = _safe_task_path(workspace_root, str(rel_path))
+            if safe_path is None:
+                return {"error": "forbidden"}
+            if not safe_path.is_file():
+                return {"error": "not found"}
+            record = _parse_task_file(safe_path)
+            if record.get("error"):
+                return {"error": "not found"}
+
+        name = record.get("name") or ""
+        match = TASK_ID_RE.match(name)
+        return {
+            "id": match.group(1) if match else name,
+            "path": record.get("path"),
+            "lane": record.get("lane"),
+            "title": record.get("title") or "untitled",
+            "markdown": record.get("raw") or "",
+        }
+    except Exception:  # noqa: BLE001 - surface as 500, never a 200 envelope
+        return {"error": "internal error"}
+
+
 def _api_status(
     project_root: Optional[str] = None, auth: Optional[AuthState] = None
 ) -> dict:
@@ -1434,8 +1583,13 @@ def build_app():
         return HTMLResponse(_dashboard_html())
 
     async def api_status(request):
+        root = request.query_params.get("project_root")
+        if _relative_root(root):
+            return JSONResponse(
+                {"error": "project_root must be absolute"}, status_code=400
+            )
         auth = _auth_from_request(request)
-        payload = _api_status(request.query_params.get("project_root"), auth)
+        payload = _api_status(root, auth)
         error = payload.get("error")
         if error == "unauthenticated":
             return JSONResponse(payload, status_code=401)
@@ -1443,6 +1597,32 @@ def build_app():
             return JSONResponse(payload, status_code=403)
         return JSONResponse(payload)
 
+    async def api_task(request):
+        root = request.query_params.get("project_root")
+        if _relative_root(root):
+            return JSONResponse(
+                {"error": "project_root must be absolute"}, status_code=400
+            )
+        auth = _auth_from_request(request)
+        payload = _api_task(
+            root,
+            request.query_params.get("id"),
+            request.query_params.get("path"),
+            auth,
+        )
+        error = payload.get("error")
+        if error == "unauthenticated":
+            return JSONResponse(payload, status_code=401)
+        if error == "forbidden":
+            return JSONResponse(payload, status_code=403)
+        if error == "not found":
+            return JSONResponse(payload, status_code=404)
+        if isinstance(error, str) and error.startswith("missing param"):
+            return JSONResponse(payload, status_code=400)
+        if error == "internal error":
+            return JSONResponse(payload, status_code=500)
+        return JSONResponse(payload)
+
     async def api_login(request):
         if not _AUTH_ENABLED:
             return JSONResponse(
@@ -1493,6 +1673,7 @@ def build_app():
             max_age=SESSION_TTL_SECONDS,
             httponly=True,
             samesite="lax",
+            secure=_is_https(request),
             path="/",
         )
         return response
@@ -1549,6 +1730,7 @@ def build_app():
     routes = [
         Route("/", dashboard),
         Route("/api/status", api_status),
+        Route("/api/task", api_task),
         Route("/api/login", api_login, methods=["POST"]),
         Route("/api/logout", api_logout, methods=["POST"]),
         Route("/api/me", api_me),
@@ -1559,7 +1741,28 @@ def build_app():
         )
     routes.append(Mount("/", app=_guarded_mcp_app(mcp_app)))
 
-    app = Starlette(routes=routes, lifespan=lifespan)
+    from starlette.middleware import Middleware
+    from starlette.middleware.base import BaseHTTPMiddleware
+
+    class _SecurityHeaders(BaseHTTPMiddleware):
+        """Baseline response headers for a page served through the tunnel."""
+
+        async def dispatch(self, request, call_next):
+            response = await call_next(request)
+            response.headers.setdefault("X-Content-Type-Options", "nosniff")
+            response.headers.setdefault("Referrer-Policy", "same-origin")
+            response.headers.setdefault("X-Frame-Options", "DENY")
+            if _is_https(request):
+                response.headers.setdefault(
+                    "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
+                )
+            return response
+
+    app = Starlette(
+        routes=routes,
+        lifespan=lifespan,
+        middleware=[Middleware(_SecurityHeaders)],
+    )
     return app
 
 
diff --git a/mcp-planner-server/static/index.html b/mcp-planner-server/static/index.html
index 6dc92fd..ed6dc49 100644
--- a/mcp-planner-server/static/index.html
+++ b/mcp-planner-server/static/index.html
@@ -1,194 +1,151 @@
 <!DOCTYPE html>
-<html lang="en">
+<html lang="en" data-bs-theme="dark">
 <head>
 <meta charset="UTF-8">
 <meta name="viewport" content="width=device-width, initial-scale=1.0">
 <title>Planner MCP — Local Dashboard</title>
-<style>
-  * { box-sizing: border-box; margin: 0; padding: 0; }
-  :root {
-    --bg: #0f172a;
-    --panel: #1e293b;
-    --panel-hover: #334155;
-    --text: #f8fafc;
-    --muted: #94a3b8;
-    --accent: #38bdf8;
-    --accent-hover: #7dd3fc;
-    --success: #22c55e;
-    --warning: #f59e0b;
-    --danger: #ef4444;
-    --border: #334155;
-  }
-  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; }
-  .container { max-width: 1200px; margin: 0 auto; padding: 24px; }
-  header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--border); }
-  .brand { font-size: 1.25rem; font-weight: 700; display: flex; align-items: center; gap: 10px; }
-  .brand .dot { width: 8px; height: 8px; background: var(--success); border-radius: 50%; }
-  .status-chip { display: inline-flex; align-items: center; gap: 6px; font-size: 0.875rem; background: var(--panel); border: 1px solid var(--border); padding: 4px 10px; border-radius: 20px; color: var(--muted); }
-  .status-chip.ok { color: var(--success); border-color: var(--success); }
-  .status-chip.err { color: var(--danger); border-color: var(--danger); }
-  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-bottom: 24px; }
-  .card { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 16px; }
-  .card h3 { font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); margin-bottom: 12px; }
-  .big { font-size: 2.5rem; font-weight: 700; margin-bottom: 4px; }
-  .sub { font-size: 0.875rem; color: var(--muted); }
-  .gauge { height: 10px; background: #334155; border-radius: 5px; overflow: hidden; margin-top: 8px; }
-  .gauge-bar { height: 100%; background: linear-gradient(90deg, var(--accent), #818cf8); border-radius: 5px; transition: width 0.3s ease; }
-  .section { margin-bottom: 28px; }
-  .section h2 { font-size: 1rem; color: var(--muted); margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
-  .section h2 .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); }
-  table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
-  th { text-align: left; color: var(--muted); padding: 8px 10px; border-bottom: 1px solid var(--border); font-weight: 600; }
-  td { padding: 8px 10px; border-bottom: 1px solid #334155; }
-  tr:hover { background: #1e293b; }
-  .lane-chip { display: inline-block; font-size: 0.75rem; padding: 2px 8px; border-radius: 10px; font-weight: 700; }
-  .lane-backlog { background: #1e1b4b; color: #c7d2fe; }
-  .lane-in-progress { background: #1c1917; color: #fed7aa; }
-  .lane-qa { background: #451a03; color: #fdba74; }
-  .lane-completed { background: #14532d; color: #bbf7d0; }
-  .lane-archive { background: #3f3f46; color: #a1a1aa; }
-  .tree { padding-left: 20px; border-left: 2px solid var(--border); }
-  .tree-node { margin: 6px 0; display: flex; align-items: center; gap: 8px; }
-  .tree-node .arrow { font-size: 0.75rem; color: var(--muted); cursor: pointer; user-select: none; }
-  .tree-node.collapsed .arrow { transform: rotate(-90deg); }
-  .tree-node.collapsed .children { display: none; }
-  .calendar { display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; }
-  .cal-day { text-align: center; padding: 8px 4px; font-size: 0.75rem; border-radius: 6px; background: var(--panel); }
-  .cal-day.header { font-weight: 600; color: var(--muted); background: transparent; }
-  .cal-day.today { background: var(--accent); color: #000; font-weight: 700; }
-  .cal-day.has-task { border: 1px solid var(--accent); }
-  .cal-day.has-deadline { background: rgba(239, 68, 68, 0.2); color: var(--danger); }
-  .cal-day.has-due { background: rgba(239, 68, 68, 0.2); color: var(--danger); position: relative; }
-  .due-badge { font-size: 0.6rem; line-height: 1; margin-top: 2px; }
-  .refresh-btn { background: var(--accent); color: #000; border: none; padding: 6px 14px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 0.875rem; }
-  .refresh-btn:hover { background: var(--accent-hover); }
-  .refresh-btn:loading { opacity: 0.6; cursor: not-allowed; }
-  .empty { color: var(--muted); font-style: italic; padding: 20px; text-align: center; }
-  .project-switcher { display: flex; align-items: center; gap: 10px; }
-  .project-switcher select { background: var(--panel); border: 1px solid var(--border); color: var(--text); padding: 4px 10px; border-radius: 6px; font-size: 0.875rem; }
-  .pacing { display: flex; align-items: center; gap: 12px; }
-  .pacing .label { font-size: 0.875rem; color: var(--muted); }
-  /* Auth UI */
-  .hidden { display: none !important; }
-  .user-badge { display: flex; align-items: center; gap: 8px; background: var(--panel); border: 1px solid var(--border); padding: 4px 12px 4px 8px; border-radius: 20px; font-size: 0.875rem; }
-  .user-badge .avatar { width: 22px; height: 22px; border-radius: 50%; background: var(--accent); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.75rem; color: #000; }
-  .user-badge .name { color: var(--text); font-weight: 600; }
-  .role-chip { font-size: 0.7rem; padding: 2px 8px; border-radius: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; }
-  .role-chip.admin { background: #1e1b4b; color: #c7d2fe; border: 1px solid #3730a3; }
-  .role-chip.viewer { background: #1c1917; color: #fed7aa; border: 1px solid #78350f; }
-  #logout-btn { background: transparent; border: 1px solid var(--border); color: var(--muted); padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.8rem; }
-  #logout-btn:hover { background: var(--panel-hover); color: var(--text); }
-  /* Login modal */
-  .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 100; }
-  .modal-overlay.hidden { display: none; }
-  .modal { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 24px; width: 360px; box-shadow: 0 20px 60px rgba(0,0,0,0.5); }
-  .modal h2 { font-size: 1.125rem; margin-bottom: 4px; }
-  .modal .sub { font-size: 0.875rem; color: var(--muted); margin-bottom: 20px; }
-  .modal .field { margin-bottom: 14px; }
-  .modal .field label { display: block; font-size: 0.8rem; color: var(--muted); margin-bottom: 4px; }
-  .modal .field input { width: 100%; background: var(--bg); border: 1px solid var(--border); color: var(--text); padding: 8px 12px; border-radius: 6px; font-size: 0.9rem; outline: none; }
-  .modal .field input:focus { border-color: var(--accent); }
-  .modal .err { color: var(--danger); font-size: 0.8rem; margin-bottom: 12px; min-height: 1.2em; }
-  .modal .actions { display: flex; gap: 10px; margin-top: 8px; }
-  .modal .btn-primary { flex: 1; background: var(--accent); color: #000; border: none; padding: 8px 16px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 0.9rem; }
-  .modal .btn-primary:hover { background: var(--accent-hover); }
-  .modal .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
-  .modal .btn-ghost { background: transparent; border: 1px solid var(--border); color: var(--muted); padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 0.9rem; }
-  .modal .btn-ghost:hover { background: var(--panel-hover); color: var(--text); }
-</style>
+<link rel="stylesheet" href="/static/vendor/bootstrap.min.css">
+<link rel="stylesheet" href="/static/theme.css">
 </head>
 <body>
-<div class="container">
-  <header>
-    <div class="brand"><div class="dot"></div> Planner MCP</div>
-    <div id="user-area" style="display:flex;align-items:center;gap:10px;">
-      <div class="user-badge hidden" id="user-badge">
-        <div class="avatar" id="user-avatar">?</div>
-        <span class="name" id="user-name">—</span>
-        <span class="role-chip" id="user-role">—</span>
-      </div>
-      <button id="logout-btn" class="hidden">Logout</button>
+
+<div class="page page-wide py-4">
+
+  <header class="d-flex align-items-center justify-content-between gap-3 border-bottom pb-3 mb-4">
+    <div class="d-flex align-items-center gap-2">
+      <span class="badge" style="background:var(--gd-accent);color:var(--gd-accent-ink)">&nbsp;</span>
+      <span class="h5 mb-0 fw-semibold">Planner MCP</span>
     </div>
-    <div class="status-chip" id="status-chip"><span class="dot" id="status-dot"></span><span id="status-text">Loading…</span></div>
-  </header>
-  <div class="modal-overlay hidden" id="login-modal">
-    <div class="modal">
-      <h2>Sign in to Planner</h2>
-      <div class="sub">Authentication is enabled on this server.</div>
-      <div class="err" id="login-err"></div>
-      <div class="field">
-        <label for="login-username">Username</label>
-        <input type="text" id="login-username" placeholder="e.g. admin" autocomplete="off">
-      </div>
-      <div class="field">
-        <label for="login-password">Password</label>
-        <input type="password" id="login-password" placeholder="Enter your password">
-      </div>
-      <div class="actions">
-        <button class="btn-ghost" id="login-cancel">Cancel</button>
-        <button class="btn-primary" id="login-btn">Sign in</button>
+    <div class="d-flex align-items-center gap-2" id="user-area">
+      <div class="d-none align-items-center gap-2 border rounded px-2 py-1" id="user-badge">
+        <span class="badge text-bg-dark" id="user-avatar">?</span>
+        <span class="small fw-semibold" id="user-name">—</span>
+        <span class="badge text-bg-secondary" id="user-role">—</span>
       </div>
+      <button type="button" class="btn btn-sm btn-outline-secondary d-none" id="logout-btn">Logout</button>
+      <span class="badge text-bg-secondary" id="status-chip"><span class="mono" id="status-dot">•</span> <span id="status-text">Loading…</span></span>
     </div>
-  </div>
+  </header>
 
-  <div class="grid">
-    <div class="card">
-      <h3>Total Tasks</h3>
-      <div class="big" id="stat-total">—</div>
-      <div class="sub">across all lanes</div>
+  <!-- Stats -->
+  <div class="row g-3 mb-4">
+    <div class="col-6 col-lg-3">
+      <div class="card h-100"><div class="card-body">
+        <div class="label">Total tasks</div>
+        <div class="h3 mb-0 mono" id="stat-total">—</div>
+        <div class="small text-muted">across all lanes</div>
+      </div></div>
     </div>
-    <div class="card">
-      <h3>In Progress</h3>
-      <div class="big" id="stat-inprogress">—</div>
-      <div class="sub">active work</div>
+    <div class="col-6 col-lg-3">
+      <div class="card h-100"><div class="card-body">
+        <div class="label">In progress</div>
+        <div class="h3 mb-0 mono" id="stat-inprogress">—</div>
+        <div class="small text-muted">active work</div>
+      </div></div>
     </div>
-    <div class="card">
-      <h3>QA Pending</h3>
-      <div class="big" id="stat-qa">—</div>
-      <div class="sub">awaiting review</div>
+    <div class="col-6 col-lg-3">
+      <div class="card h-100"><div class="card-body">
+        <div class="label">QA pending</div>
+        <div class="h3 mb-0 mono" id="stat-qa">—</div>
+        <div class="small text-muted">awaiting review</div>
+      </div></div>
     </div>
-    <div class="card">
-      <h3>Completed</h3>
-      <div class="big" id="stat-completed">—</div>
-      <div class="sub">closed tasks</div>
+    <div class="col-6 col-lg-3">
+      <div class="card h-100"><div class="card-body">
+        <div class="label">Completed</div>
+        <div class="h3 mb-0 mono" id="stat-completed">—</div>
+        <div class="small text-muted">closed tasks</div>
+      </div></div>
     </div>
   </div>
 
-  <div class="section pacing">
-    <h2><span class="dot"></span> Daily Pacing Gauge</h2>
-    <div class="pacing"><span class="label">Today's Work:</span> <span id="pacing-text" class="big">—</span></div>
-    <div class="gauge"><div class="gauge-bar" id="gauge-bar" style="width: 0%"></div></div>
-    <div class="sub" id="pacing-sub">Fetching status…</div>
-  </div>
+  <!-- Pacing -->
+  <div class="card mb-4"><div class="card-body">
+    <div class="d-flex align-items-center justify-content-between mb-2">
+      <span class="label mb-0">Daily pacing</span>
+      <span class="mono" id="pacing-text">—</span>
+    </div>
+    <div class="progress" style="height:6px;background:var(--gd-raised)">
+      <div class="progress-bar" id="gauge-bar" style="width:0%;background:var(--gd-accent)"></div>
+    </div>
+    <div class="small text-muted mt-2" id="pacing-sub">Fetching status…</div>
+  </div></div>
 
-  <div class="section">
-    <div class="project-switcher">
-      <label for="project-select" style="font-size:0.875rem;color:var(--muted);">Project:</label>
-      <select id="project-select"></select>
+  <!-- Project + refresh -->
+  <div class="d-flex flex-wrap align-items-end gap-2 mb-4">
+    <div>
+      <label class="form-label" for="project-select">Project</label>
+      <select id="project-select" class="form-select form-select-sm" style="min-width:20rem"></select>
     </div>
-    <button class="refresh-btn" id="refresh-btn">Refresh</button>
+    <button type="button" class="btn btn-sm btn-outline-secondary" id="refresh-btn">Refresh</button>
   </div>
 
-  <div class="section">
-    <h2><span class="dot"></span> Kanban Lanes</h2>
-    <div class="grid" id="lanes-grid" style="grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));"></div>
-  </div>
+  <!-- Lanes -->
+  <section class="mb-4">
+    <div class="d-flex align-items-center justify-content-between mb-2">
+      <span class="label mb-0">Kanban lanes</span>
+    </div>
+    <input type="search" id="board-search" class="form-control form-control-sm mb-3" placeholder="Filter tasks by ID or title…" autocomplete="off" aria-label="Filter tasks">
+    <div class="row g-3" id="lanes-grid"></div>
+  </section>
+
+  <!-- Milestones -->
+  <section class="mb-4">
+    <div class="label mb-2">Milestones</div>
+    <div id="milestone-tree"></div>
+  </section>
 
-  <div class="section">
-    <h2><span class="dot"></span> Milestone Tree</h2>
-    <div id="milestone-tree" class="tree"></div>
+  <!-- Timeline -->
+  <section class="mb-4">
+    <div class="label mb-2">Timeline (Gregorian + Jalali)</div>
+    <div id="timeline" class="cal"></div>
+  </section>
+
+</div>
+
+<!-- Login overlay -->
+<div class="gd-overlay hidden" id="login-modal">
+  <div class="gd-panel gd-panel-md p-4">
+    <h2 class="h6 mb-1">Sign in to Planner</h2>
+    <p class="small text-muted mb-3">Authentication is enabled on this server.</p>
+    <div class="small mb-2" id="login-err" style="color:var(--gd-danger);min-height:1.2em"></div>
+    <div class="mb-2">
+      <label class="form-label" for="login-username">Username</label>
+      <input type="text" id="login-username" class="form-control form-control-sm" placeholder="e.g. admin" autocomplete="off">
+    </div>
+    <div class="mb-3">
+      <label class="form-label" for="login-password">Password</label>
+      <input type="password" id="login-password" class="form-control form-control-sm" placeholder="Password">
+    </div>
+    <div class="d-flex gap-2 justify-content-end">
+      <button type="button" class="btn btn-sm btn-outline-secondary" id="login-cancel">Cancel</button>
+      <button type="button" class="btn btn-sm btn-primary" id="login-btn">Sign in</button>
+    </div>
   </div>
+</div>
 
-  <div class="section">
-    <h2><span class="dot"></span> Timeline (Gregorian + Jalali)</h2>
-    <div id="timeline" class="calendar"></div>
+<!-- Task overlay -->
+<div class="gd-overlay hidden" id="task-modal">
+  <div class="gd-panel gd-panel-lg">
+    <div class="d-flex align-items-start justify-content-between gap-3 p-3 border-bottom">
+      <h2 class="h6 mb-0" id="task-modal-title">Task</h2>
+      <button type="button" class="btn btn-sm btn-outline-secondary" id="task-modal-close">Close</button>
+    </div>
+    <div class="small text-muted px-3 pt-2 mono" id="task-modal-meta"></div>
+    <div id="task-modal-body"></div>
   </div>
 </div>
 
+<script src="/static/vendor/jalaali.min.js"></script>
 <script>
-(function() {
+(function () {
   const BASE_STATUS_URL = window.location.pathname.endsWith('/') ? window.location.href + 'api/status' : window.location.origin + '/api/status';
   let currentProject = '';
+  let query = '';
+  let lastData = null;
+  let archiveOpen = false;
+  try { archiveOpen = window.localStorage.getItem('planner-archive-open') === '1'; } catch (e) { archiveOpen = false; }
+
   const elements = {
     total: document.getElementById('stat-total'),
     inprogress: document.getElementById('stat-inprogress'),
@@ -196,7 +153,6 @@
     completed: document.getElementById('stat-completed'),
     statusChip: document.getElementById('status-chip'),
     statusText: document.getElementById('status-text'),
-    statusDot: document.getElementById('status-dot'),
     lanesGrid: document.getElementById('lanes-grid'),
     milestoneTree: document.getElementById('milestone-tree'),
     timeline: document.getElementById('timeline'),
@@ -205,101 +161,96 @@
     gaugeBar: document.getElementById('gauge-bar'),
     refreshBtn: document.getElementById('refresh-btn'),
     projectSelect: document.getElementById('project-select'),
+    search: document.getElementById('board-search'),
+    taskModal: document.getElementById('task-modal'),
+    taskModalTitle: document.getElementById('task-modal-title'),
+    taskModalMeta: document.getElementById('task-modal-meta'),
+    taskModalBody: document.getElementById('task-modal-body'),
+    taskModalClose: document.getElementById('task-modal-close'),
   };
 
-  // Jalali (Solar Hijri) calendar conversion (algorithm by M. Amin)
-  function toJalali(gy, gm, gd) {
-    const g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
-    let gy2 = (gm > 2) ? gy + 1 : gy;
-    let days = 355666 + (365 * gy2) + ((gy2 + 3) >> 2) - ((gy2 + 99) >> 2) + ((gy2 + 400) >> 2) + g_d_m[gm - 1] + gd - 1;
-    let jy = -1595 + (33 * Math.floor(days / 12053));
-    days %= 12053;
-    jy += 4 * Math.floor(days / 1461);
-    days %= 1461;
-    if (days > 365) {
-      jy += Math.floor((days - 1) / 365);
-      days = (days - 1) % 365;
-    }
-    let jm = (days < 186) ? 1 + Math.floor(days / 31) : 7 + Math.floor((days - 186) / 30);
-    let jd = 1 + ((days < 186) ? (days % 31) : ((days - 186) % 30));
-    return [jy, jm, jd];
+  const JALALI_MONTHS = ['Farvardin', 'Ordibehesht', 'Khordad', 'Tir', 'Mordad', 'Shahrivar', 'Mehr', 'Aban', 'Azar', 'Dey', 'Bahman', 'Esfand'];
+
+  // Jalali conversion comes from jalaali-js (vendored, MIT), not from a
+  // hand-rolled algorithm: the previous snippet got leap years and month
+  // boundaries wrong.
+  function jalaliOf(date) {
+    if (!window.jalaali) return null;
+    return window.jalaali.toJalaali(date.getFullYear(), date.getMonth() + 1, date.getDate());
   }
 
   function formatJalali(d) {
-    const j = toJalali(d.getFullYear(), d.getMonth() + 1, d.getDate());
-    const months = ['Farvardin','Ordibehesht','Khordad','Tir','Mordad','Shahrivar','Mehr','Aban','Azar','Dey','Bahman','Esfand'];
-    return `${j[2]} ${months[j[1]-1]} ${j[0]}`;
+    const j = jalaliOf(d);
+    if (!j) return d.toISOString().slice(0, 10);
+    return j.jd + ' ' + JALALI_MONTHS[j.jm - 1] + ' ' + j.jy;
   }
 
   function statusUrl() {
-    return currentProject
-      ? `${BASE_STATUS_URL}?project_root=${encodeURIComponent(currentProject)}`
-      : BASE_STATUS_URL;
+    return currentProject ? BASE_STATUS_URL + '?project_root=' + encodeURIComponent(currentProject) : BASE_STATUS_URL;
   }
 
   async function fetchStatus() {
     try {
       const resp = await fetch(statusUrl(), { cache: 'no-cache' });
       if (resp.status === 401) {
-        // Auth is enabled and this session is not signed in.
         hideUserBadge();
         showLoginModal();
-        elements.statusChip.className = 'status-chip err';
+        elements.statusChip.className = 'badge text-bg-danger';
         elements.statusText.textContent = 'Sign in required';
-        elements.statusDot.className = 'dot';
         return;
       }
       if (resp.status === 403) {
-        elements.statusChip.className = 'status-chip err';
+        elements.statusChip.className = 'badge text-bg-danger';
         elements.statusText.textContent = 'Access denied for this project';
-        elements.statusDot.className = 'dot';
         return;
       }
-      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
+      if (!resp.ok) throw new Error('HTTP ' + resp.status);
       const data = await resp.json();
       render(data);
-      elements.statusChip.className = 'status-chip ok';
+      elements.statusChip.className = 'badge text-bg-success';
       elements.statusText.textContent = 'Server reachable';
-      elements.statusDot.className = 'dot';
     } catch (err) {
-      elements.statusChip.className = 'status-chip err';
-      elements.statusText.textContent = `Server unreachable: ${err.message}`;
-      elements.statusDot.className = 'dot';
+      elements.statusChip.className = 'badge text-bg-danger';
+      elements.statusText.textContent = 'Server unreachable: ' + err.message;
     }
   }
 
+  function escapeHtml(value) {
+    return String(value == null ? '' : value)
+      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
+      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
+  }
+
   function render(data) {
     if (data.error) {
-      elements.statusChip.className = 'status-chip err';
-      elements.statusText.textContent = `Error: ${data.error}`;
+      elements.statusChip.className = 'badge text-bg-danger';
+      elements.statusText.textContent = 'Error: ' + data.error;
       return;
     }
+    lastData = data;
 
     const total = data.total_tasks || 0;
     const inProgress = data.in_progress || 0;
     const qaPending = data.qa_pending || 0;
     const completed = data.completed || 0;
-    const backlog = data.backlog || 0;
 
     elements.total.textContent = total;
     elements.inprogress.textContent = inProgress;
     elements.qa.textContent = qaPending;
     elements.completed.textContent = completed;
 
-    // Pacing gauge (server computes done/target from the open working set)
     const today = data.today || { done: 0, target: 3, open: 0 };
     const pct = Math.min(100, Math.round((today.done / today.target) * 100));
-    elements.pacingText.textContent = `${today.done}/${today.target}`;
-    elements.gaugeBar.style.width = `${pct}%`;
+    elements.pacingText.textContent = today.done + '/' + today.target;
+    elements.gaugeBar.style.width = pct + '%';
     elements.pacingSub.textContent = qaPending > 0
-      ? `${qaPending} task(s) awaiting QA — claim paused`
-      : (today.open > 0 ? `${today.open} task(s) still open today` : 'Quota reached');
+      ? qaPending + ' task(s) awaiting QA — claim paused'
+      : (today.open > 0 ? today.open + ' task(s) still open today' : 'Quota reached');
 
-    // Project selector
     const projects = data.projects || [];
     if (projects.length) {
       elements.projectSelect.innerHTML = projects.map(p =>
-        `<option value="${p.path}"${p.path === data.project_root ? ' selected' : ''}>${p.label}</option>`
+        '<option value="' + escapeHtml(p.path) + '"' + (p.path === data.project_root ? ' selected' : '') + '>' + escapeHtml(p.label) + '</option>'
       ).join('');
       currentProject = data.project_root || projects[0].path;
     }
@@ -309,44 +260,63 @@
     elements.lanesGrid.innerHTML = '';
     const laneOrder = ['backlog', 'in-progress', 'qa', 'completed', 'archive'];
     const laneLabels = { backlog: 'Backlog', 'in-progress': 'In Progress', qa: 'QA / Review', completed: 'Completed', archive: 'Archive' };
-    laneOrder.forEach(lane => {
-      const items = lanes[lane] || [];
-      const card = document.createElement('div');
-      card.className = 'card';
-      card.innerHTML = `
-        <h3>${laneLabels[lane] || lane} <span class="lane-chip lane-${lane}">${items.length}</span></h3>
-        ${items.length === 0 ? '<div class="empty">—</div>' : items.map(t => `
-          <div style="padding:6px 0; border-bottom:1px solid #334155; font-size:0.875rem;">
-            <strong>${t.id || t.name || 'task'}</strong> — ${t.title || 'untitled'}
-            ${t.estimate_hours != null ? `<span style="color:var(--muted); font-size:0.75rem;"> ${t.estimate_hours}h</span>` : ''}
-          </div>
-        `).join('')}
-      `;
-      elements.lanesGrid.appendChild(card);
+    const needle = query.trim().toLowerCase();
+    laneOrder.forEach(function (lane) {
+      const all = lanes[lane] || [];
+      const items = needle ? all.filter(function (t) { return taskMatches(t, needle); }) : all;
+      const isArchive = lane === 'archive';
+      const collapsed = isArchive && !archiveOpen;
+      const chipClass = { backlog: 'text-bg-secondary', 'in-progress': 'text-bg-info', qa: 'text-bg-warning', completed: 'text-bg-success', archive: 'text-bg-secondary' }[lane];
+      const header = '<span>' + laneLabels[lane] + ' <span class="badge ' + chipClass + '">' + all.length + '</span></span>' +
+        (isArchive ? '<button type="button" class="btn btn-sm btn-outline-secondary" id="archive-toggle" aria-expanded="' + (archiveOpen ? 'true' : 'false') + '">' + (archiveOpen ? 'Collapse' : 'Expand') + '</button>' : '');
+      const rows = items.length === 0
+        ? '<div class="text-muted small p-2">' + (needle ? 'No matches' : '—') + '</div>'
+        : items.map(function (t) {
+          return '<div class="task-row" role="button" tabindex="0" data-id="' + escapeHtml(t.id || t.name || '') + '" data-path="' + escapeHtml(t.path || '') + '">' +
+            '<span class="id">' + escapeHtml(t.id || t.name || 'task') + '</span> — ' + escapeHtml(t.title || 'untitled') +
+            (t.estimate_hours != null ? ' <span class="text-muted">' + t.estimate_hours + 'h</span>' : '') +
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
     });
+    const toggle = document.getElementById('archive-toggle');
+    if (toggle) {
+      toggle.addEventListener('click', function () {
+        archiveOpen = !archiveOpen;
+        try { window.localStorage.setItem('planner-archive-open', archiveOpen ? '1' : '0'); } catch (e) { /* storage may be blocked */ }
+        if (lastData) render(lastData);
+      });
+    }
 
-    // Milestone tree
+    // Milestones
     const tree = data.milestone_tree || {};
     elements.milestoneTree.innerHTML = '';
     if (!tree || Object.keys(tree).length === 0) {
-      elements.milestoneTree.innerHTML = '<div class="empty">No milestones defined.</div>';
+      elements.milestoneTree.innerHTML = '<div class="text-muted small">No milestones defined.</div>';
     } else {
-      Object.entries(tree).forEach(([ms, items]) => {
+      Object.entries(tree).forEach(function (entry) {
+        const ms = entry[0];
+        const items = entry[1];
         const node = document.createElement('div');
-        node.className = 'tree-node';
-        const done = items.filter(i => i.status === 'closed').length;
-        node.innerHTML = `
-          <span class="arrow">▾</span>
-          <strong>${ms}</strong> <span style="color:var(--muted); font-size:0.875rem;">(${done}/${items.length})</span>
-          <div class="children tree-node" style="margin-left:18px;">
-            ${items.map(i => `<div style="font-size:0.875rem; padding:2px 0;">• ${i.title || i.name || 'untitled'} [${i.status || 'open'}]</div>`).join('')}
-          </div>
-        `;
-        node.querySelector('.arrow').onclick = () => {
-          const children = node.querySelector('.children');
-          children.style.display = children.style.display === 'none' ? 'block' : 'none';
-          node.querySelector('.arrow').textContent = children.style.display === 'none' ? '▾' : '▸';
-        };
+        node.className = 'ms-node';
+        const done = items.filter(function (i) { return i.status === 'closed'; }).length;
+        node.innerHTML = '<div class="d-flex align-items-center gap-2">' +
+          '<button type="button" class="btn btn-sm btn-outline-secondary py-0 px-1" data-arrow>▾</button>' +
+          '<strong class="small">' + escapeHtml(ms) + '</strong>' +
+          '<span class="text-muted small mono">' + done + '/' + items.length + '</span></div>' +
+          '<div class="children mt-1">' + items.map(function (i) {
+            return '<div class="small text-muted">• ' + escapeHtml(i.title || i.name || 'untitled') + ' [' + escapeHtml(i.status || 'open') + ']</div>';
+          }).join('') + '</div>';
+        node.querySelector('[data-arrow]').addEventListener('click', function () {
+          node.classList.toggle('collapsed');
+        });
         elements.milestoneTree.appendChild(node);
       });
     }
@@ -354,52 +324,183 @@
     // Timeline
     const now = new Date();
     elements.timeline.innerHTML = '';
-    const dayNames = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
-    ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].forEach(dn => {
+    ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].forEach(function (dn) {
       const div = document.createElement('div');
-      div.className = 'cal-day header';
+      div.className = 'cal-day head';
       div.textContent = dn;
       elements.timeline.appendChild(div);
     });
-    // Next 14 days, with due deadlines annotated per day
     const byDay = {};
-    (data.deadlines || []).forEach(t => {
-      const key = t.deadline;
-      (byDay[key] = byDay[key] || []).push(t);
+    (data.deadlines || []).forEach(function (t) {
+      (byDay[t.deadline] = byDay[t.deadline] || []).push(t);
     });
     for (let i = 0; i < 14; i++) {
       const d = new Date();
       d.setDate(now.getDate() + i);
-      const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
+      const key = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
       const due = byDay[key] || [];
       const div = document.createElement('div');
-      div.className = 'cal-day';
-      if (i === 0) div.classList.add('today');
-      if (due.length) div.classList.add('has-due');
-      div.textContent = d.getDate();
-      div.title = `${formatJalali(d)} — ${due.length ? due.map(t => t.title).join(', ') : 'no deadlines'}`;
-      if (due.length) {
-        const badge = document.createElement('div');
-        badge.className = 'due-badge';
-        badge.textContent = `●${due.length}`;
-        div.appendChild(badge);
-      }
+      div.className = 'cal-day' + (i === 0 ? ' today' : '') + (due.length ? ' due' : '');
+      const j = jalaliOf(d);
+      const jalaliDay = j ? j.jd : '';
+      const monthLabel = j && j.jd === 1 ? JALALI_MONTHS[j.jm - 1] : '';
+      div.innerHTML = '<div class="cal-primary">' + (jalaliDay || d.getDate()) + '</div>' +
+        '<div class="cal-secondary">' + d.getDate() + (j ? '' : ' (G)') + '</div>' +
+        (monthLabel ? '<div class="cal-secondary">' + monthLabel + '</div>' : '') +
+        (due.length ? '<div class="cal-secondary">•' + due.length + '</div>' : '');
+      div.title = (j ? formatJalali(d) + ' · ' : '') + d.toISOString().slice(0, 10) + ' — ' +
+        (due.length ? due.map(function (t) { return t.title; }).join(', ') : 'no deadlines');
       elements.timeline.appendChild(div);
     }
   }
 
-  elements.refreshBtn.addEventListener('click', () => {
+  function taskMatches(task, needle) {
+    return ((task.id || '') + ' ' + (task.name || '') + ' ' + (task.title || '')).toLowerCase().indexOf(needle) !== -1;
+  }
+
+  // ---- Markdown renderer (self-contained) ----
+  const MAX_RENDER_LINES = 2000;
+
+  function inlineMarkdown(text) {
+    return text
+      .replace(/`([^`]+)`/g, '<code>$1</code>')
+      .replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>')
+      .replace(/(^|[^*])\*([^*]+)\*(?!\*)/g, '$1<i>$2</i>')
+      .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, function (m, label, href) {
+        return (href.charAt(0) === '#' || href.charAt(0) === '/')
+          ? '<a href="' + href + '" target="_blank" rel="noopener">' + label + '</a>'
+          : label;
+      });
+  }
+
+  function renderMarkdown(source) {
+    const all = escapeHtml(source).split('\n');
+    const truncated = all.length > MAX_RENDER_LINES;
+    const body = truncated ? all.slice(0, MAX_RENDER_LINES) : all;
+    const out = [];
+    let fence = null;
+    let buffer = [];
+
+    function flushFence() {
+      if (!buffer.length) return;
+      const isDiff = fence === 'diff' || buffer.some(function (line) { return /^(\+|-{3}|\+{3}|@@)/.test(line); });
+      const html = buffer.map(function (line) {
+        if (!isDiff) return line;
+        if (/^@@/.test(line)) return '<span style="color:var(--gd-info)">' + line + '</span>';
+        if (/^\+/.test(line) && !/^\+\+\+/.test(line)) return '<span class="add">' + line + '</span>';
+        if (/^-/.test(line) && !/^---/.test(line)) return '<span class="del">' + line + '</span>';
+        return line;
+      }).join('\n');
+      out.push('<pre' + (isDiff ? ' class="diff"' : '') + '><code>' + html + '</code></pre>');
+      buffer = [];
+    }
+
+    for (let i = 0; i < body.length; i++) {
+      const line = body[i];
+      const fenceMatch = line.match(/^```([\w-]*)\s*$/);
+      if (fenceMatch) {
+        if (fence === null) { fence = fenceMatch[1] || ''; buffer = []; }
+        else { flushFence(); fence = null; }
+        continue;
+      }
+      if (fence !== null) { buffer.push(line); continue; }
+      if (!line.trim()) continue;
+      let m;
+      if ((m = line.match(/^(#{1,6})\s+(.*)$/))) {
+        out.push('<h' + m[1].length + '>' + inlineMarkdown(m[2]) + '</h' + m[1].length + '>');
+        continue;
+      }
+      if ((m = line.match(/^\s*[-*]\s+\[([ xX])\]\s+(.*)$/))) {
+        out.push('<div class="todo"><input type="checkbox" disabled' + (m[1].toLowerCase() === 'x' ? ' checked' : '') + '> ' + inlineMarkdown(m[2]) + '</div>');
+        continue;
+      }
+      if ((m = line.match(/^\s*[-*]\s+(.*)$/))) { out.push('<li>' + inlineMarkdown(m[1]) + '</li>'); continue; }
+      if ((m = line.match(/^&gt;\s?(.*)$/))) { out.push('<blockquote>' + inlineMarkdown(m[1]) + '</blockquote>'); continue; }
+      if (/^\|/.test(line)) {
+        const rows = [line];
+        while (i + 1 < body.length && /^\|/.test(body[i + 1])) { i += 1; rows.push(body[i]); }
+        out.push('<pre><code>' + rows.join('\n') + '</code></pre>');
+        continue;
+      }
+      out.push('<p>' + inlineMarkdown(line) + '</p>');
+    }
+    if (fence !== null) flushFence();
+    if (truncated) out.push('<p class="truncated">truncated: showing the first ' + MAX_RENDER_LINES + ' lines</p>');
+    return out.join('\n');
+  }
+
+  function relTaskPath(absPath) {
+    if (!absPath) return '';
+    const marker = absPath.indexOf('/tasks/');
+    return marker >= 0 ? absPath.slice(marker + 1) : '';
+  }
+
+  function openTaskModal(id, absPath) {
+    const params = new URLSearchParams();
+    const rel = relTaskPath(absPath);
+    if (rel) params.set('path', rel);
+    else if (id) params.set('id', id);
+    if (currentProject) params.set('project_root', currentProject);
+    elements.taskModalTitle.textContent = id ? 'Task ' + id : 'Task';
+    elements.taskModalMeta.textContent = 'Loading…';
+    elements.taskModalBody.innerHTML = '<p class="text-muted small">Loading…</p>';
+    elements.taskModal.classList.remove('hidden');
+    elements.taskModalClose.focus();
+    fetch('/api/task?' + params.toString(), { cache: 'no-cache' })
+      .then(async function (resp) {
+        const payload = await resp.json().catch(function () { return {}; });
+        if (!resp.ok) {
+          elements.taskModalMeta.textContent = 'Error ' + resp.status;
+          elements.taskModalBody.innerHTML = '<p class="truncated">' + escapeHtml(payload.error || 'request failed') + '</p>';
+          return;
+        }
+        elements.taskModalTitle.textContent = payload.title || 'Task ' + (payload.id || '');
+        elements.taskModalMeta.textContent = '#' + (payload.id || '?') + ' · ' + (payload.lane || 'unknown lane') + ' · ' + (relTaskPath(payload.path) || payload.path || '');
+        elements.taskModalBody.innerHTML = renderMarkdown(payload.markdown || '');
+        elements.taskModalBody.scrollTop = 0;
+      })
+      .catch(function (err) {
+        elements.taskModalMeta.textContent = 'Network error';
+        elements.taskModalBody.innerHTML = '<p class="truncated">' + escapeHtml(err.message) + '</p>';
+      });
+  }
+
+  function closeTaskModal() { elements.taskModal.classList.add('hidden'); }
+
+  elements.lanesGrid.addEventListener('click', function (event) {
+    const row = event.target.closest('.task-row');
+    if (row) openTaskModal(row.dataset.id, row.dataset.path);
+  });
+  elements.lanesGrid.addEventListener('keydown', function (event) {
+    if (event.key !== 'Enter' && event.key !== ' ') return;
+    const row = event.target.closest('.task-row');
+    if (!row) return;
+    event.preventDefault();
+    openTaskModal(row.dataset.id, row.dataset.path);
+  });
+  elements.taskModalClose.addEventListener('click', closeTaskModal);
+  elements.taskModal.addEventListener('click', function (event) {
+    if (event.target === elements.taskModal) closeTaskModal();
+  });
+  document.addEventListener('keydown', function (event) {
+    if (event.key === 'Escape' && !elements.taskModal.classList.contains('hidden')) closeTaskModal();
+  });
+  elements.search.addEventListener('input', function () {
+    query = elements.search.value;
+    if (lastData) render(lastData);
+  });
+
+  elements.refreshBtn.addEventListener('click', function () {
     elements.refreshBtn.textContent = '…';
-    fetchStatus().then(() => { elements.refreshBtn.textContent = 'Refresh'; });
+    fetchStatus().then(function () { elements.refreshBtn.textContent = 'Refresh'; });
   });
 
-  // Project selector — switching re-queries the server with ?project_root=
-  elements.projectSelect.addEventListener('change', () => {
+  elements.projectSelect.addEventListener('change', function () {
     currentProject = elements.projectSelect.value;
     fetchStatus();
   });
 
-  // ---- Auth (login modal, user badge, logout) ----
+  // ---- Auth ----
   const auth = {
     modal: document.getElementById('login-modal'),
     err: document.getElementById('login-err'),
@@ -412,7 +513,6 @@
     userName: document.getElementById('user-name'),
     userRole: document.getElementById('user-role'),
     userAvatar: document.getElementById('user-avatar'),
-    userArea: document.getElementById('user-area'),
   };
 
   function showLoginModal() {
@@ -422,23 +522,22 @@
     auth.password.value = '';
     auth.username.focus();
   }
+  function hideLoginModal() { auth.modal.classList.add('hidden'); }
 
-  function hideLoginModal() {
-    auth.modal.classList.add('hidden');
-  }
-
-  function showUserBadge(username, role, allowedProjects) {
-    auth.userBadge.classList.remove('hidden');
-    auth.logoutBtn.classList.remove('hidden');
+  function showUserBadge(username, role) {
+    auth.userBadge.classList.remove('d-none');
+    auth.userBadge.classList.add('d-flex');
+    auth.logoutBtn.classList.remove('d-none');
     auth.userName.textContent = username;
     auth.userRole.textContent = role;
-    auth.userRole.className = 'role-chip ' + (role === 'admin' ? 'admin' : 'viewer');
+    auth.userRole.className = 'badge ' + (role === 'admin' ? 'text-bg-info' : 'text-bg-secondary');
     auth.userAvatar.textContent = (username || '?').charAt(0).toUpperCase();
   }
 
   function hideUserBadge() {
-    auth.userBadge.classList.add('hidden');
-    auth.logoutBtn.classList.add('hidden');
+    auth.userBadge.classList.add('d-none');
+    auth.userBadge.classList.remove('d-flex');
+    auth.logoutBtn.classList.add('d-none');
   }
 
   async function login() {
@@ -449,13 +548,10 @@
       const resp = await fetch('/api/login', {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
-        body: JSON.stringify({
-          username: auth.username.value.trim(),
-          password: auth.password.value,
-        }),
+        body: JSON.stringify({ username: auth.username.value.trim(), password: auth.password.value }),
       });
       if (!resp.ok) {
-        let message = `HTTP ${resp.status}`;
+        let message = 'HTTP ' + resp.status;
         try {
           const errBody = await resp.json();
           if (errBody && errBody.error) message = errBody.error;
@@ -466,11 +562,10 @@
       const data = await resp.json();
       if (data.token) {
         hideLoginModal();
-        showUserBadge(data.username, data.role, data.allowed_projects);
+        showUserBadge(data.username, data.role);
         currentProject = '';
         fetchStatus();
       } else if (data.note === 'auth disabled') {
-        // Auth is disabled server-side: open local mode, no badge to show.
         hideLoginModal();
         fetchStatus();
       }
@@ -483,41 +578,33 @@
   }
 
   async function logout() {
-    try {
-      await fetch('/api/logout', { method: 'POST' });
-    } catch (e) { /* best-effort: the cookie is cleared server-side */ }
+    try { await fetch('/api/logout', { method: 'POST' }); } catch (e) { /* cookie clears server-side */ }
     hideUserBadge();
-    // Reload so no stale board data from the previous session stays on screen.
     window.location.reload();
   }
 
   auth.loginBtn.addEventListener('click', login);
   auth.cancelBtn.addEventListener('click', hideLoginModal);
   auth.logoutBtn.addEventListener('click', logout);
-  auth.username.addEventListener('keydown', (e) => { if (e.key === 'Enter') auth.password.focus(); });
-  auth.password.addEventListener('keydown', (e) => { if (e.key === 'Enter') login(); });
+  auth.username.addEventListener('keydown', function (e) { if (e.key === 'Enter') auth.password.focus(); });
+  auth.password.addEventListener('keydown', function (e) { if (e.key === 'Enter') login(); });
 
-  // Check auth state on load.
   (async function checkAuth() {
     try {
       const resp = await fetch('/api/me');
       if (resp.ok) {
         const data = await resp.json();
-        if (data.authenticated) {
-          showUserBadge(data.username, data.role || 'viewer', data.allowed_projects || []);
-        }
-        // `note: "auth disabled"` is open local mode — nothing to sign in to.
+        if (data.authenticated) showUserBadge(data.username, data.role || 'viewer');
       } else if (resp.status === 401) {
         showLoginModal();
       }
-    } catch (e) {
-      // If the server is unreachable, just show the board as-is.
-    }
+    } catch (e) { /* server unreachable: leave the board as is */ }
   })();
 
   fetchStatus();
   setInterval(fetchStatus, 30000);
 })();
 </script>
+<script src="/static/vendor/bootstrap.bundle.min.js"></script>
 </body>
 </html>
diff --git a/mcp-planner-server/static/theme.css b/mcp-planner-server/static/theme.css
new file mode 100644
index 0000000..671d245
--- /dev/null
+++ b/mcp-planner-server/static/theme.css
@@ -0,0 +1,273 @@
+/* Graphite Desk theme for Bootstrap 5.3 — see DESIGN.md at the repo root.
+   Tokens are authoritative; Bootstrap variables are the adapter. */
+:root {
+  --gd-bg: #0b0e14;
+  --gd-surface: #141a23;
+  --gd-raised: #1b2430;
+  --gd-border: #263141;
+  --gd-text: #e6ebf2;
+  --gd-muted: #8c99ab;
+  --gd-accent: #5eead4;
+  --gd-accent-hover: #86f2e2;
+  --gd-accent-ink: #04211d;
+  --gd-success: #34d399;
+  --gd-warning: #fbbf24;
+  --gd-danger: #f87171;
+  --gd-info: #7dd3fc;
+  --gd-mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
+}
+
+[data-bs-theme="dark"] {
+  --bs-body-bg: var(--gd-bg);
+  --bs-body-color: var(--gd-text);
+  --bs-secondary-color: var(--gd-muted);
+  --bs-tertiary-bg: var(--gd-surface);
+  --bs-secondary-bg: var(--gd-raised);
+  --bs-emphasis-color: var(--gd-text);
+  --bs-border-color: var(--gd-border);
+  --bs-border-color-translucent: var(--gd-border);
+  --bs-primary: var(--gd-accent);
+  --bs-primary-rgb: 94, 234, 212;
+  --bs-success: var(--gd-success);
+  --bs-warning: var(--gd-warning);
+  --bs-danger: var(--gd-danger);
+  --bs-info: var(--gd-info);
+  --bs-link-color: var(--gd-accent);
+  --bs-link-hover-color: var(--gd-accent-hover);
+  --bs-body-font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
+  --bs-body-font-size: 14px;
+  --bs-font-monospace: var(--gd-mono);
+  --bs-border-radius-sm: 4px;
+  --bs-border-radius: 6px;
+  --bs-border-radius-lg: 8px;
+  --bs-border-radius-xl: 12px;
+  --bs-focus-ring-color: rgba(94, 234, 212, 0.35);
+  --bs-box-shadow: none;
+  --bs-box-shadow-sm: none;
+  --bs-box-shadow-lg: 0 24px 60px rgba(4, 7, 12, 0.55);
+}
+
+body {
+  background: var(--gd-bg);
+  font-size: 14px;
+  line-height: 1.45;
+}
+
+/* Layout */
+.page { max-width: 960px; margin: 0 auto; padding: 24px 24px 32px; }
+.page-wide { max-width: 1200px; }
+.section-gap { margin-bottom: 24px; }
+.label {
+  font-size: 11px;
+  font-weight: 600;
+  letter-spacing: 0.06em;
+  text-transform: uppercase;
+  color: var(--gd-muted);
+}
+
+/* Surfaces */
+.card {
+  --bs-card-bg: var(--gd-surface);
+  --bs-card-border-color: var(--gd-border);
+  --bs-card-border-radius: 8px;
+  --bs-card-inner-border-radius: 7px;
+  --bs-card-spacer-y: 16px;
+  --bs-card-spacer-x: 16px;
+  box-shadow: none !important;
+}
+.card-header {
+  background: var(--gd-surface);
+  border-bottom: 1px solid var(--gd-border);
+  font-size: 11px;
+  font-weight: 600;
+  letter-spacing: 0.06em;
+  text-transform: uppercase;
+  color: var(--gd-muted);
+}
+
+/* Buttons */
+.btn { border-radius: 6px; font-size: 13px; font-weight: 500; }
+.btn-sm { border-radius: 6px; font-size: 12px; }
+.btn-primary {
+  --bs-btn-bg: var(--gd-accent);
+  --bs-btn-border-color: var(--gd-accent);
+  --bs-btn-color: var(--gd-accent-ink);
+  --bs-btn-hover-bg: var(--gd-accent-hover);
+  --bs-btn-hover-border-color: var(--gd-accent-hover);
+  --bs-btn-hover-color: var(--gd-accent-ink);
+  --bs-btn-active-bg: var(--gd-accent-hover);
+  --bs-btn-active-color: var(--gd-accent-ink);
+  --bs-btn-disabled-bg: var(--gd-raised);
+  --bs-btn-disabled-color: var(--gd-muted);
+}
+.btn-outline-secondary {
+  --bs-btn-color: var(--gd-text);
+  --bs-btn-border-color: var(--gd-border);
+  --bs-btn-hover-bg: var(--gd-raised);
+  --bs-btn-hover-border-color: var(--gd-border);
+  --bs-btn-hover-color: var(--gd-text);
+}
+.btn-outline-danger {
+  --bs-btn-color: var(--gd-danger);
+  --bs-btn-border-color: var(--gd-danger);
+  --bs-btn-hover-bg: rgba(248, 113, 113, 0.12);
+  --bs-btn-hover-color: var(--gd-danger);
+}
+
+/* Chips: neutral by default, at most four semantic tints */
+.chip {
+  border: 1px solid var(--gd-border);
+  background: var(--gd-raised);
+  color: var(--gd-text);
+  border-radius: 6px;
+  font-size: 12px;
+  padding: 3px 10px;
+  line-height: 1.5;
+}
+.chip:hover { border-color: var(--gd-muted); }
+.chip[aria-pressed="true"] { border-color: var(--gd-accent); color: var(--gd-accent); }
+.chip-info { color: var(--gd-info); border-color: rgba(125, 211, 252, 0.45); }
+.chip-success { color: var(--gd-success); border-color: rgba(52, 211, 153, 0.45); }
+.chip-warning { color: var(--gd-warning); border-color: rgba(251, 191, 36, 0.45); }
+.chip-danger { color: var(--gd-danger); border-color: rgba(248, 113, 113, 0.45); }
+
+/* Forms */
+.form-control, .form-select {
+  background: var(--gd-bg);
+  border-color: var(--gd-border);
+  color: var(--gd-text);
+  border-radius: 6px;
+  font-size: 13px;
+}
+.form-control:focus, .form-select:focus {
+  background: var(--gd-bg);
+  color: var(--gd-text);
+  border-color: var(--gd-accent);
+  box-shadow: 0 0 0 3px var(--bs-focus-ring-color);
+}
+.form-control::placeholder { color: var(--gd-muted); }
+textarea.form-control { font-family: var(--gd-mono); line-height: 1.5; }
+.form-label { font-size: 12px; color: var(--gd-muted); margin-bottom: 4px; }
+
+/* Tabs */
+.nav-tabs { border-bottom: 1px solid var(--gd-border); gap: 4px; }
+.nav-tabs .nav-link {
+  border: 0;
+  border-bottom: 2px solid transparent;
+  color: var(--gd-muted);
+  font-size: 13px;
+  font-weight: 500;
+  padding: 6px 12px;
+  border-radius: 6px 6px 0 0;
+}
+.nav-tabs .nav-link:hover { color: var(--gd-text); background: var(--gd-raised); }
+.nav-tabs .nav-link.active {
+  color: var(--gd-text);
+  background: transparent;
+  border-bottom-color: var(--gd-accent);
+}
+
+/* Badges */
+.badge { font-family: var(--gd-mono); font-size: 11px; border-radius: 4px; padding: 2px 6px; }
+
+/* Dialog */
+dialog.gd-dialog {
+  background: var(--gd-surface);
+  border: 1px solid var(--gd-border);
+  border-radius: 12px;
+  color: var(--gd-text);
+  box-shadow: 0 24px 60px rgba(4, 7, 12, 0.55);
+  padding: 0;
+  width: min(480px, 92vw);
+}
+dialog.gd-dialog::backdrop { background: rgba(4, 7, 12, 0.72); }
+
+.mono { font-family: var(--gd-mono); }
+.text-muted { color: var(--gd-muted) !important; }
+a { color: var(--gd-accent); }
+
+/* ---- Planner-specific layer (Bootstrap has no equivalent) ---- */
+.gd-overlay {
+  position: fixed;
+  inset: 0;
+  background: rgba(4, 7, 12, 0.72);
+  display: flex;
+  align-items: center;
+  justify-content: center;
+  padding: 16px;
+  z-index: 1050;
+}
+.gd-overlay.hidden { display: none; }
+.gd-panel {
+  background: var(--gd-surface);
+  border: 1px solid var(--gd-border);
+  border-radius: 12px;
+  color: var(--gd-text);
+  max-height: 92vh;
+  display: flex;
+  flex-direction: column;
+  overflow: hidden;
+}
+.gd-panel-md { width: min(400px, 100%); }
+.gd-panel-lg { width: min(1000px, 100%); }
+
+.lane-card { max-height: calc(100vh - 300px); overflow-y: auto; }
+.lane-card .card-header {
+  position: sticky;
+  top: 0;
+  z-index: 2;
+  background: var(--gd-surface);
+  display: flex;
+  align-items: center;
+  justify-content: space-between;
+  gap: 8px;
+}
+.lane-list.hidden { display: none; }
+.task-row {
+  border-bottom: 1px solid var(--gd-border);
+  border-radius: 4px;
+  cursor: pointer;
+  font-size: 13px;
+  padding: 5px 4px;
+}
+.task-row:last-child { border-bottom: 0; }
+.task-row:hover { background: var(--gd-raised); }
+.task-row:focus-visible { outline: 2px solid var(--gd-accent); outline-offset: 1px; }
+.task-row .id { font-family: var(--gd-mono); font-weight: 600; }
+.lane-hint { color: var(--gd-muted); font-size: 11px; }
+
+.cal { display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; }
+.cal-day {
+  background: var(--gd-surface);
+  border: 1px solid var(--gd-border);
+  border-radius: 4px;
+  font-size: 11px;
+  padding: 6px 2px;
+  text-align: center;
+}
+.cal-day.head { background: transparent; border-color: transparent; color: var(--gd-muted); }
+.cal-day.today { background: var(--gd-accent); border-color: var(--gd-accent); color: var(--gd-accent-ink); font-weight: 600; }
+.cal-day.due { border-color: var(--gd-danger); color: var(--gd-danger); }
+.cal-day .cal-primary { font-size: 12px; font-weight: 600; line-height: 1.2; }
+.cal-day .cal-secondary { color: var(--gd-muted); font-size: 9px; line-height: 1.3; }
+.cal-day.today .cal-secondary { color: var(--gd-accent-ink); opacity: 0.75; }
+
+.ms-node { border-left: 2px solid var(--gd-border); padding-left: 12px; margin: 8px 0; }
+.ms-node .children { margin-left: 8px; }
+.ms-node.collapsed .children { display: none; }
+
+#task-modal-body { overflow-y: auto; padding: 12px 16px 16px; font-size: 13px; }
+#task-modal-body h1 { font-size: 1.1rem; margin: 14px 0 8px; }
+#task-modal-body h2 { font-size: 1rem; margin: 14px 0 8px; color: var(--gd-accent); text-transform: none; letter-spacing: 0; }
+#task-modal-body h3, #task-modal-body h4, #task-modal-body h5, #task-modal-body h6 { font-size: 0.95rem; margin: 12px 0 6px; color: var(--gd-text); text-transform: none; letter-spacing: 0; }
+#task-modal-body p { margin: 6px 0; }
+#task-modal-body li { margin: 2px 0 2px 18px; }
+#task-modal-body code { background: var(--gd-bg); border: 1px solid var(--gd-border); border-radius: 4px; font-size: 0.82rem; padding: 1px 5px; }
+#task-modal-body pre { background: var(--gd-bg); border: 1px solid var(--gd-border); border-radius: 8px; margin: 8px 0; overflow-x: auto; padding: 10px 12px; }
+#task-modal-body pre code { background: transparent; border: 0; padding: 0; white-space: pre; }
+#task-modal-body pre.diff .add { background: rgba(52, 211, 153, 0.12); color: var(--gd-success); }
+#task-modal-body pre.diff .del { background: rgba(248, 113, 113, 0.12); color: var(--gd-danger); }
+#task-modal-body .todo { margin: 3px 0; }
+#task-modal-body .truncated { color: var(--gd-warning); font-style: italic; }
+#task-modal-body blockquote { border-left: 3px solid var(--gd-border); color: var(--gd-muted); margin: 8px 0; padding: 2px 0 2px 10px; }
+
diff --git a/mcp-planner-server/static/vendor/bootstrap.bundle.min.js b/mcp-planner-server/static/vendor/bootstrap.bundle.min.js
new file mode 100644
index 0000000..04e9185
Binary files /dev/null and b/mcp-planner-server/static/vendor/bootstrap.bundle.min.js differ
diff --git a/mcp-planner-server/static/vendor/bootstrap.min.css b/mcp-planner-server/static/vendor/bootstrap.min.css
new file mode 100644
index 0000000..3993414
Binary files /dev/null and b/mcp-planner-server/static/vendor/bootstrap.min.css differ
diff --git a/mcp-planner-server/static/vendor/jalaali.min.js b/mcp-planner-server/static/vendor/jalaali.min.js
new file mode 100644
index 0000000..a0434c4
Binary files /dev/null and b/mcp-planner-server/static/vendor/jalaali.min.js differ
diff --git a/tests/test_planner_server.py b/tests/test_planner_server.py
index cc7e2dd..20c6964 100644
--- a/tests/test_planner_server.py
+++ b/tests/test_planner_server.py
@@ -518,6 +518,7 @@ def test_build_app_serves_dashboard_and_mcp_routes(tmp_path):
         paths = [getattr(r, "path", None) for r in app.routes]
         assert "/" in paths
         assert "/api/status" in paths
+        assert "/api/task" in paths
         assert "/api/login" in paths
         assert "/api/logout" in paths
         assert "/static" in paths
@@ -531,6 +532,147 @@ def test_build_app_serves_dashboard_and_mcp_routes(tmp_path):
     assert app.router.lifespan_context is not None
 
 
+# ---------------------------------------------------------------------------
+# Dashboard API contract (/api/task) — task detail modal payload
+# ---------------------------------------------------------------------------
+
+
+def test_api_task_by_id_returns_markdown(tmp_path):
+    """A numeric id resolves across lanes and returns the raw Markdown body."""
+    _write_task(tmp_path, "backlog", 7, "Modal target")
+    payload = planner._api_task(str(tmp_path), "7")
+
+    assert "error" not in payload
+    assert payload["id"] == "007"
+    assert payload["lane"] == "backlog"
+    assert payload["title"] == "Modal target"
+    assert "## Goal" in payload["markdown"]
+    assert payload["path"].endswith("007-task.md")
+
+
+def test_api_task_by_path_returns_markdown(tmp_path):
+    """A lane-relative path deep-links the same payload as the id form."""
+    _write_task(tmp_path, "qa", 8, "Path lookup")
+    payload = planner._api_task(str(tmp_path), None, "tasks/qa/008-task.md")
+
+    assert "error" not in payload
+    assert payload["id"] == "008"
+    assert payload["lane"] == "qa"
+    assert payload["title"] == "Path lookup"
+    assert "## Local TODOs" in payload["markdown"]
+
+
+def test_api_task_id_is_int_normalized(tmp_path):
+    """Zero-padded ids match the same file (020 == 20), like _find_task_by_id."""
+    _write_task(tmp_path, "backlog", 9, "Normalized")
+    payload = planner._api_task(str(tmp_path), "009")
+    assert payload["id"] == "009"
+
+
+def test_api_task_unknown_id_is_not_found(tmp_path):
+    (tmp_path / "tasks" / "backlog").mkdir(parents=True, exist_ok=True)
+    assert planner._api_task(str(tmp_path), "424242") == {"error": "not found"}
+
+
+def test_api_task_missing_params_is_client_error(tmp_path):
+    payload = planner._api_task(str(tmp_path))
+    assert payload["error"].startswith("missing param")
+
+
+@pytest.mark.parametrize(
+    "rel_path",
+    [
+        "../server.py",
+        "tasks/backlog/../../server.py",
+        "/etc/passwd",
+        "tasks/backlog/sub/001-task.md",
+        "tasks/nope/001-task.md",
+        "tasks/backlog/001-task.txt",
+        "C:/tasks/backlog/001-task.md",
+        "tasks\\backlog\\001-task.md",
+    ],
+)
+def test_api_task_path_traversal_is_forbidden(tmp_path, rel_path):
+    """Anything outside tasks/<known lane>/<file>.md is 403, never a file read."""
+    _write_task(tmp_path, "backlog", 1, "Guard")
+    assert planner._api_task(str(tmp_path), None, rel_path) == {"error": "forbidden"}
+
+
+def test_api_task_route_exists_in_auth_mode(auth_app):
+    paths = [getattr(r, "path", None) for r in auth_app.routes]
+    assert "/api/task" in paths
+
+
+def test_api_task_401_when_unauthenticated(auth_client):
+    resp = auth_client.get("/api/task", params={"id": "1"})
+    assert resp.status_code == 401
+    assert resp.json().get("error") == "unauthenticated"
+
+
+def test_api_task_400_when_no_param(auth_client):
+    auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
+    resp = auth_client.get("/api/task")
+    assert resp.status_code == 400
+    assert resp.json().get("error", "").startswith("missing param")
+
+
+def test_api_task_404_for_unknown_id(auth_client):
+    auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
+    resp = auth_client.get("/api/task", params={"id": "987654"})
+    assert resp.status_code == 404
+
+
+def test_api_task_serves_task_for_authenticated_admin(auth_client, tmp_path):
+    _write_task(tmp_path, "backlog", 11, "Admin visible")
+    auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
+    resp = auth_client.get(
+        "/api/task", params={"id": "11", "project_root": str(tmp_path)}
+    )
+    assert resp.status_code == 200
+    data = resp.json()
+    assert data["title"] == "Admin visible"
+    assert "## Goal" in data["markdown"]
+
+
+def test_api_task_403_when_project_root_not_allowed(auth_client, tmp_path):
+    """A viewer cannot read a task from a project outside its grants."""
+    (tmp_path / "project-a").mkdir(parents=True, exist_ok=True)
+    (tmp_path / "project-b").mkdir(parents=True, exist_ok=True)
+    (tmp_path / "project-b" / "tasks").mkdir(parents=True, exist_ok=True)
+    _write_task(tmp_path / "project-b", "backlog", 12, "Not yours")
+    auth_client.post(
+        "/api/login", json={"username": "viewer", "password": "viewer-pass"}
+    )
+    resp = auth_client.get(
+        "/api/task",
+        params={"id": "12", "project_root": str(tmp_path / "project-b")},
+    )
+    assert resp.status_code == 403
+    assert resp.json().get("error") == "forbidden"
+
+
+def test_api_task_403_for_traversal_over_http(auth_client, tmp_path):
+    _write_task(tmp_path, "backlog", 13, "Guard http")
+    auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
+    resp = auth_client.get(
+        "/api/task",
+        params={
+            "path": "tasks/backlog/../../server.py",
+            "project_root": str(tmp_path),
+        },
+    )
+    assert resp.status_code == 403
+
+
+def test_api_task_works_in_open_mode(open_client, tmp_path):
+    _write_task(tmp_path, "backlog", 14, "Open mode")
+    resp = open_client.get(
+        "/api/task", params={"id": "14", "project_root": str(tmp_path)}
+    )
+    assert resp.status_code == 200
+    assert resp.json()["title"] == "Open mode"
+
+
 # ---------------------------------------------------------------------------
 # Auth: password hashing, user config, and session management
 # ---------------------------------------------------------------------------
@@ -762,6 +904,41 @@ def auth_client(auth_app):
         yield client
 
 
+def test_security_headers_present(open_client):
+    """Baseline headers ride every response; HSTS only when the hop is HTTPS."""
+    resp = open_client.get("/api/me")
+    assert resp.headers["x-content-type-options"] == "nosniff"
+    assert resp.headers["referrer-policy"] == "same-origin"
+    assert resp.headers["x-frame-options"] == "DENY"
+    assert "strict-transport-security" not in resp.headers
+    resp_https = open_client.get("/api/me", headers={"x-forwarded-proto": "https"})
+    assert resp_https.headers["strict-transport-security"].startswith("max-age=")
+
+
+def test_relative_project_root_rejected(auth_client):
+    """A relative root must 400 instead of resolving against the daemon cwd."""
+    auth_client.post("/api/login", json={"username": "admin", "password": "admin-pass"})
+    for path in ("/api/status", "/api/task"):
+        resp = auth_client.get(
+            path, params={"project_root": "relative/path", "id": "1"}
+        )
+        assert resp.status_code == 400, path
+        assert resp.json()["error"] == "project_root must be absolute", path
+
+
+def test_session_cookie_is_secure_behind_https_proxy(auth_client):
+    """X-Forwarded-Proto: https makes the session cookie Secure."""
+    resp = auth_client.post(
+        "/api/login",
+        json={"username": "admin", "password": "admin-pass"},
+        headers={"x-forwarded-proto": "https"},
+    )
+    assert resp.status_code == 200
+    cookie = resp.headers["set-cookie"]
+    assert "HttpOnly" in cookie
+    assert "Secure" in cookie
+
+
 def test_login_valid_credentials_returns_token(auth_client):
     resp = auth_client.post(
         "/api/login", json={"username": "admin", "password": "admin-pass"}
diff --git a/tools/prompt-composer/index.html b/tools/prompt-composer/index.html
index b65ca14..ef38149 100644
--- a/tools/prompt-composer/index.html
+++ b/tools/prompt-composer/index.html
@@ -1,232 +1,168 @@
 <!DOCTYPE html>
-<html lang="en">
+<html lang="en" data-bs-theme="dark">
 <head>
   <!--
     Prompt Composer — Cognitive Lead AI
     Standalone web tool that automates the Brain<->Hands copy-paste workflow.
-    Fetches system-prompt.md from GitHub, provides preset Manager commands
-    (including Task Discovery / Collect Context for context gathering),
-    accepts an optional Project Tree input, assembles a structured Markdown
-    message, and copies it to the clipboard.
-    Self-contained: only external dependency is the Tailwind CSS CDN.
+    Design: Graphite Desk (DESIGN.md). Styling: Bootstrap 5.3 vendored locally
+    under vendor/ plus theme.css; no network requests at runtime.
   -->
   <meta charset="UTF-8">
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   <title>Prompt Composer — Cognitive Lead AI</title>
-  <!-- Tailwind CSS via CDN (the only external dependency) -->
-  <script src="https://cdn.tailwindcss.com"></script>
-  <style>
-    /* Minimal custom styles that Tailwind does not cover cleanly. */
-    .font-mono {
-      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
-    }
-    .scrollbar-hide::-webkit-scrollbar { display: none; }
-    .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
-  </style>
+  <link rel="stylesheet" href="vendor/bootstrap.min.css">
+  <link rel="stylesheet" href="theme.css">
 </head>
-<body class="bg-slate-100 text-slate-900 min-h-screen">
-
-  <!-- ===================== Header ===================== -->
-  <header class="bg-slate-900 text-white">
-    <div class="max-w-6xl mx-auto px-4 py-6">
-      <h1 class="text-2xl font-bold tracking-tight">Prompt Composer</h1>
-      <p class="text-slate-300 text-sm mt-1">
-        Automate the Brain ↔ Hands copy-paste workflow for Cognitive Lead AI.
-      </p>
+<body>
+
+  <header class="border-bottom">
+    <div class="page page-wide d-flex align-items-center justify-content-between py-3">
+      <div>
+        <h1 class="h5 mb-0 fw-semibold">Prompt Composer</h1>
+        <p class="text-muted small mb-0">Automate the Brain ↔ Hands copy-paste workflow.</p>
+      </div>
+      <span class="badge text-bg-secondary">Cognitive Lead AI</span>
     </div>
   </header>
 
-  <main class="max-w-6xl mx-auto px-4 py-8 space-y-8">
+  <main class="page page-wide">
 
-    <!-- ===================== Tab Navigation ===================== -->
-    <nav aria-label="Project Tabs" class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-slate-200 p-2 rounded-lg border border-slate-300">
-      <div id="tab-container" class="flex overflow-x-auto gap-1 w-full scrollbar-hide">
-        <!-- Tabs injected here via JS -->
-      </div>
-      <div class="flex gap-2 shrink-0">
-        <button type="button" onclick="createProject()" class="px-3 py-1.5 rounded-md bg-white hover:bg-slate-50 text-slate-700 text-sm font-medium border border-slate-300 shadow-sm transition">+ New</button>
-        <button type="button" onclick="openManageModal()" class="px-3 py-1.5 rounded-md bg-white hover:bg-slate-50 text-slate-700 text-sm font-medium border border-slate-300 shadow-sm transition">⚙️ Manage</button>
+    <!-- Project tabs -->
+    <nav class="d-flex flex-column flex-sm-row justify-content-between align-items-sm-center gap-2 mb-4" aria-label="Project tabs">
+      <ul class="nav nav-tabs border-0 flex-nowrap overflow-auto w-100" id="tab-container"></ul>
+      <div class="d-flex gap-2 flex-shrink-0">
+        <button type="button" class="btn btn-sm btn-outline-secondary" onclick="createProject()">New</button>
+        <button type="button" class="btn btn-sm btn-outline-secondary" onclick="openManageModal()">Manage</button>
       </div>
     </nav>
 
-    <!-- ===================== System Instructions Section ===================== -->
-    <section aria-labelledby="system-instructions-heading">
-      <h2 id="system-instructions-heading" class="text-lg font-semibold mb-2">1. System Instructions</h2>
-      <div class="flex items-center gap-3 mb-2">
-        <button
-          type="button"
-          onclick="fetchSystemPrompt()"
-          class="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition"
-        >
-          Fetch System Prompt
-        </button>
-        <span id="fetch-status" class="text-sm text-slate-500"></span>
+    <!-- 1. System instructions -->
+    <section class="card section-gap" aria-labelledby="system-instructions-heading">
+      <div class="card-header d-flex justify-content-between align-items-center">
+        <span id="system-instructions-heading">1 · System instructions</span>
+        <span id="fetch-status" class="text-muted fw-normal" style="text-transform:none;letter-spacing:0"></span>
+      </div>
+      <div class="card-body">
+        <div class="d-flex gap-2 mb-2">
+          <button type="button" class="btn btn-sm btn-primary" onclick="fetchSystemPrompt()">Fetch system prompt</button>
+        </div>
+        <textarea id="system-prompt" rows="10" class="form-control form-control-sm" aria-label="System instructions"
+          placeholder="Loads from GitHub automatically. If the fetch fails, paste system-prompt.md here."></textarea>
       </div>
-      <!-- Read-only system prompt content; user can paste manually if fetch fails -->
-      <textarea
-        id="system-prompt"
-        rows="12"
-        class="w-full font-mono text-sm p-3 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
-        placeholder="System prompt will load here automatically. If the fetch fails, paste the contents of system-prompt.md manually."
-        aria-label="System Instructions"
-      ></textarea>
     </section>
 
-    <!-- ===================== Manager Message Section ===================== -->
-    <section aria-labelledby="manager-message-heading">
-      <h2 id="manager-message-heading" class="text-lg font-semibold mb-2">2. Manager Message</h2>
-
-      <!-- Preset Command Selector -->
-      <div class="mb-3">
-        <p class="text-sm font-medium text-slate-700 mb-2">Preset Commands</p>
-        <div class="flex flex-wrap gap-2" role="group" aria-label="Preset commands">
-          <button type="button" onclick="selectPreset('This is a new project. Start Phase 0.')" class="px-3 py-1.5 rounded-full bg-slate-200 hover:bg-slate-300 text-sm transition">New Project — Phase 0</button>
-          <button type="button" onclick="selectPreset('This is an existing project. Start Phase 0.')" class="px-3 py-1.5 rounded-full bg-slate-200 hover:bg-slate-300 text-sm transition">Existing Project — Phase 0</button>
-          <button type="button" onclick="selectPreset('Generate a <hands_discovery_task> for the task we are working on. Instruct the Hands to gather the necessary context: get and persist the project directory tree, read all Core SOP files (AGENTS.md, DESIGN.md, docs/architecture.md, docs/data_model.md, docs/conventions.md), extract vertical slice signatures for the relevant module, and compile everything into a single context report. Use the provided Project Tree as the target context when available. Do not proceed to implementation until the discovery context has been returned and reviewed.')" class="px-3 py-1.5 rounded-full bg-sky-200 hover:bg-sky-300 text-sm transition">Task Discovery</button>
-          <button type="button" onclick="selectPreset('Load the code-search skill and collect context for the current task. Get the project directory tree, extract vertical slice signatures for the target module, and read all Core SOP files (AGENTS.md, DESIGN.md, docs/architecture.md, docs/data_model.md, docs/conventions.md). Compile everything into a single context report. Do NOT read the report yourself — return the file path to me.')" class="px-3 py-1.5 rounded-full bg-cyan-200 hover:bg-cyan-300 text-sm transition">Collect Context</button>
-          <button type="button" onclick="selectPreset('A context report is provided in the Context Report section below. Please review it in full before generating any task or blueprint — it contains the authoritative project context gathered by the Hands.')" class="px-3 py-1.5 rounded-full bg-teal-200 hover:bg-teal-300 text-sm transition">Context Report Review</button>
-          <button type="button" onclick="selectPreset('Approved')" class="px-3 py-1.5 rounded-full bg-emerald-200 hover:bg-emerald-300 text-sm transition">Approved</button>
-          <button type="button" onclick="selectPreset('Approved for closure')" class="px-3 py-1.5 rounded-full bg-emerald-200 hover:bg-emerald-300 text-sm transition">Approved for Closure</button>
-          <button type="button" onclick="selectPreset('[QA Engineer], please perform adversarial testing.')" class="px-3 py-1.5 rounded-full bg-amber-200 hover:bg-amber-300 text-sm transition">QA — Adversarial Testing</button>
-          <button type="button" onclick="selectPreset('[Code Reviewer], please perform the final review.')" class="px-3 py-1.5 rounded-full bg-violet-200 hover:bg-violet-300 text-sm transition">Code Review — Final Review</button>
-          <button type="button" onclick="selectPreset('Close task')" class="px-3 py-1.5 rounded-full bg-rose-200 hover:bg-rose-300 text-sm transition">Close Task</button>
-          <button type="button" onclick="selectPreset('')" class="px-3 py-1.5 rounded-full bg-slate-400 hover:bg-slate-500 text-white text-sm transition">Custom</button>
+    <!-- 2. Manager message -->
+    <section class="card section-gap" aria-labelledby="manager-message-heading">
+      <div class="card-header" id="manager-message-heading">2 · Manager message</div>
+      <div class="card-body">
+        <p class="label mb-2">Preset commands</p>
+        <div class="d-flex flex-wrap gap-2 mb-3" role="group" aria-label="Preset commands">
+          <button type="button" class="chip" onclick="selectPreset('This is a new project. Start Phase 0.')">New project · Phase 0</button>
+          <button type="button" class="chip" onclick="selectPreset('This is an existing project. Start Phase 0.')">Existing project · Phase 0</button>
+          <button type="button" class="chip chip-info" onclick="selectPreset('Generate a <hands_discovery_task> for the task we are working on. Instruct the Hands to gather the necessary context: get and persist the project directory tree, read all Core SOP files (AGENTS.md, DESIGN.md, docs/architecture.md, docs/data_model.md, docs/conventions.md), extract vertical slice signatures for the relevant module, and compile everything into a single context report. Use the provided Project Tree as the target context when available. Do not proceed to implementation until the discovery context has been returned and reviewed.')">Task discovery</button>
+          <button type="button" class="chip chip-info" onclick="selectPreset('Load the code-search skill and collect context for the current task. Get the project directory tree, extract vertical slice signatures for the target module, and read all Core SOP files (AGENTS.md, DESIGN.md, docs/architecture.md, docs/data_model.md, docs/conventions.md). Compile everything into a single context report. Do NOT read the report yourself — return the file path to me.')">Collect context</button>
+          <button type="button" class="chip" onclick="selectPreset('A context report is provided in the Context Report section below. Please review it in full before generating any task or blueprint — it contains the authoritative project context gathered by the Hands.')">Context report review</button>
+          <button type="button" class="chip chip-success" onclick="selectPreset('Approved')">Approved</button>
+          <button type="button" class="chip chip-success" onclick="selectPreset('Approved for closure')">Approved for closure</button>
+          <button type="button" class="chip chip-warning" onclick="selectPreset('[QA Engineer], please perform adversarial testing.')">QA · adversarial testing</button>
+          <button type="button" class="chip chip-info" onclick="selectPreset('[Code Reviewer], please perform the final review.')">Code review · final</button>
+          <button type="button" class="chip chip-danger" onclick="selectPreset('Close task')">Close task</button>
+          <button type="button" class="chip" onclick="selectPreset('')">Custom</button>
         </div>
-      </div>
 
-      <!-- Manager Message textarea -->
-      <textarea
-        id="manager-message"
-        rows="4"
-        class="w-full font-mono text-sm p-3 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
-        placeholder="Selected preset command appears here. For 'Custom', type your command."
-        aria-label="Manager Message"
-      ></textarea>
-
-      <!-- Custom Notes Section (separate from the preset command) -->
-      <label for="custom-notes" class="block text-sm font-medium text-slate-700 mt-4 mb-1">Custom Notes</label>
-      <textarea
-        id="custom-notes"
-        rows="3"
-        class="w-full font-mono text-sm p-3 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
-        placeholder="Optional: additional instructions or context for the Orchestrator."
-        aria-label="Custom Notes"
-      ></textarea>
-    </section>
+        <label for="manager-message" class="form-label">Command</label>
+        <textarea id="manager-message" rows="4" class="form-control form-control-sm mb-3" aria-label="Manager message"
+          placeholder="The selected preset appears here. For Custom, type your command."></textarea>
 
-    <!-- ===================== Project Tree Section (Optional) ===================== -->
-    <section aria-labelledby="project-tree-heading">
-      <h2 id="project-tree-heading" class="text-lg font-semibold mb-2">3. Project Tree <span class="text-sm font-normal text-slate-400">(optional)</span></h2>
-      <!-- Optional codebase context: paste a directory tree or subtree here.
-           If non-empty, generateMarkdown() includes it as a "# Project Tree" section. -->
-      <textarea
-        id="project-tree"
-        rows="10"
-        class="w-full font-mono text-sm p-3 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
-        placeholder="Optional: paste the project directory tree (or a subtree) here. If provided, it is included in the generated Markdown as a # Project Tree section."
-        aria-label="Project Tree"
-      ></textarea>
+        <label for="custom-notes" class="form-label">Custom notes (optional)</label>
+        <textarea id="custom-notes" rows="3" class="form-control form-control-sm" aria-label="Custom notes"
+          placeholder="Extra instructions or context for the Orchestrator."></textarea>
+      </div>
     </section>
 
-    <!-- ===================== Context Report Section (Optional) ===================== -->
-    <section aria-labelledby="context-report-heading">
-      <h2 id="context-report-heading" class="text-lg font-semibold mb-2">4. Context Report <span class="text-sm font-normal text-slate-400">(optional)</span></h2>
-      <textarea
-        id="context-report"
-        rows="10"
-        class="w-full font-mono text-sm p-3 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
-        placeholder="Optional: paste the contents of a context report (e.g., context-reports/context_report_...) here. If provided, it is included in the generated Markdown as a # Context Report section."
-        aria-label="Context Report"
-      ></textarea>
+    <!-- 3. Project tree -->
+    <section class="card section-gap" aria-labelledby="project-tree-heading">
+      <div class="card-header d-flex justify-content-between">
+        <span id="project-tree-heading">3 · Project tree</span>
+        <span class="text-muted fw-normal" style="text-transform:none;letter-spacing:0">optional</span>
+      </div>
+      <div class="card-body">
+        <textarea id="project-tree" rows="8" class="form-control form-control-sm" aria-label="Project tree"
+          placeholder="Paste a directory tree or subtree. Included as a # Project Tree section when non-empty."></textarea>
+      </div>
     </section>
 
-    <!-- ===================== Task File Section ===================== -->
-    <section aria-labelledby="task-file-heading">
-      <h2 id="task-file-heading" class="text-lg font-semibold mb-2">5. Task File</h2>
-      <textarea
-        id="task-file"
-        rows="10"
-        class="w-full font-mono text-sm p-3 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
-        placeholder="Paste the contents of a task file (e.g., tasks/qa/XX-task-name.md) here."
-        aria-label="Task File"
-      ></textarea>
+    <!-- 4. Context report -->
+    <section class="card section-gap" aria-labelledby="context-report-heading">
+      <div class="card-header d-flex justify-content-between">
+        <span id="context-report-heading">4 · Context report</span>
+        <span class="text-muted fw-normal" style="text-transform:none;letter-spacing:0">optional</span>
+      </div>
+      <div class="card-body">
+        <textarea id="context-report" rows="8" class="form-control form-control-sm" aria-label="Context report"
+          placeholder="Paste a context report. Included as a # Context Report section when non-empty."></textarea>
+      </div>
     </section>
 
-    <!-- ===================== Generate & Output Section ===================== -->
-    <section aria-labelledby="generate-heading">
-      <button
-        type="button"
-        onclick="generateMarkdown()"
-        class="px-6 py-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-sm font-semibold transition"
-      >
-        Generate Markdown
-      </button>
-
-      <div class="mt-4 flex items-center gap-3">
-        <h2 id="generate-heading" class="text-lg font-semibold">6. Output</h2>
-        <button
-          type="button"
-          onclick="copyToClipboard()"
-          class="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition"
-        >
-          Copy to Clipboard
-        </button>
-        <span id="copy-status" class="text-sm text-slate-500"></span>
+    <!-- 5. Task file -->
+    <section class="card section-gap" aria-labelledby="task-file-heading">
+      <div class="card-header" id="task-file-heading">5 · Task file</div>
+      <div class="card-body">
+        <textarea id="task-file" rows="10" class="form-control form-control-sm" aria-label="Task file"
+          placeholder="Paste a task file, e.g. tasks/qa/XX-task-name.md."></textarea>
       </div>
+    </section>
 
-      <!-- Generated Markdown output (read-only) -->
-      <textarea
-        id="output"
-        rows="16"
-        readonly
-        class="w-full font-mono text-sm p-3 rounded-lg border border-slate-300 bg-slate-50 text-slate-800 focus:outline-none"
-        placeholder="Generated Markdown will appear here."
-        aria-label="Generated Markdown Output"
-      ></textarea>
+    <!-- 6. Output -->
+    <section class="card section-gap" aria-labelledby="output-heading">
+      <div class="card-header d-flex justify-content-between align-items-center">
+        <span id="output-heading">6 · Output</span>
+        <span id="copy-status" class="text-muted fw-normal" style="text-transform:none;letter-spacing:0"></span>
+      </div>
+      <div class="card-body">
+        <div class="d-flex gap-2 mb-3">
+          <button type="button" class="btn btn-sm btn-primary" onclick="generateMarkdown()">Generate markdown</button>
+          <button type="button" class="btn btn-sm btn-outline-secondary" onclick="copyToClipboard()">Copy</button>
+        </div>
+        <textarea id="output" rows="14" readonly class="form-control form-control-sm" aria-label="Generated markdown"></textarea>
+      </div>
     </section>
 
   </main>
 
-  <!-- ===================== Manage Projects Modal ===================== -->
-  <dialog id="manage-modal" class="p-0 rounded-xl shadow-2xl border border-slate-300 backdrop:bg-slate-900/50 w-full max-w-md">
-    <div class="p-6">
-      <div class="flex justify-between items-center mb-4">
-        <h3 class="text-xl font-bold text-slate-900">Manage Projects</h3>
-        <button type="button" onclick="closeManageModal()" class="text-slate-400 hover:text-slate-600 transition text-lg">&times;</button>
+  <footer class="page page-wide text-muted small pb-4">
+    Prompt Composer — Cognitive Lead AI HQ · ZAC-compliant (this tool makes no commits)
+  </footer>
+
+  <!-- Manage projects -->
+  <dialog id="manage-modal" class="gd-dialog">
+    <div class="p-4">
+      <div class="d-flex justify-content-between align-items-center mb-3">
+        <h2 class="h6 mb-0">Manage projects</h2>
+        <button type="button" class="btn btn-sm btn-outline-secondary" onclick="closeManageModal()" aria-label="Close">Cancel</button>
       </div>
-      <ul id="modal-project-list" class="space-y-2 mb-6 max-h-64 overflow-y-auto">
-        <!-- List items injected here via JS -->
-      </ul>
-      <div class="flex justify-end">
-        <button type="button" onclick="closeManageModal()" class="px-4 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-sm font-medium transition">Done</button>
+      <ul id="modal-project-list" class="list-unstyled mb-3" style="max-height:18rem;overflow-y:auto"></ul>
+      <div class="d-flex justify-content-end">
+        <button type="button" class="btn btn-sm btn-primary" onclick="closeManageModal()">Done</button>
       </div>
     </div>
   </dialog>
 
-  <footer class="max-w-6xl mx-auto px-4 pb-8 text-sm text-slate-400">
-    Prompt Composer — Cognitive Lead AI HQ · ZAC-compliant (no commits are made by this tool)
-  </footer>
-
+  <script src="vendor/bootstrap.bundle.min.js"></script>
   <script>
     /**
      * Prompt Composer — Cognitive Lead AI
-     * Vanilla JavaScript, no external JS dependencies.
-     * All functions are defined on the global scope so inline onclick handlers can reach them.
+     * Vanilla JavaScript, no external runtime dependency.
+     * Functions stay on the global scope because inline handlers call them.
      */
 
-    // Cache the GitHub raw URL for the system prompt (canonical source).
     const SYSTEM_PROMPT_URL = 'https://raw.githubusercontent.com/mokhtarabadi/cognitive-lead-hq/main/system-prompt.md';
 
-    // ─── Multi-Project State Management ──────────────────────────────────────
     /** @type {{ activeProject: string, projects: Record<string, Record<string, string>> }} */
     let appState = { activeProject: 'Default', projects: {} };
     const STORAGE_KEY = 'promptComposerState';
     const TEXTAREA_IDS = ['system-prompt', 'manager-message', 'custom-notes', 'project-tree', 'context-report', 'task-file'];
 
-    /**
-     * Loads persisted project state from localStorage.
-     * Falls back to a fresh "Default" project if no data exists or JSON is corrupt.
-     */
     function loadState() {
       const saved = localStorage.getItem(STORAGE_KEY);
       if (saved) {
@@ -241,26 +177,15 @@
       }
     }
 
-    /**
-     * Persists the current appState to localStorage.
-     * Handles quota exceeded errors gracefully.
-     */
     function saveState() {
       try { localStorage.setItem(STORAGE_KEY, JSON.stringify(appState)); }
       catch (e) { console.error('localStorage quota exceeded', e); }
     }
 
-    /**
-     * Returns an empty project state object with all textarea keys initialized.
-     * @returns {Record<string, string>}
-     */
     function getEmptyProjectState() {
       return { 'system-prompt': '', 'manager-message': '', 'custom-notes': '', 'project-tree': '', 'context-report': '', 'task-file': '' };
     }
 
-    /**
-     * Reads all textarea values from the DOM and saves them to the active project state.
-     */
     function syncDOMToState() {
       const proj = appState.projects[appState.activeProject];
       TEXTAREA_IDS.forEach(id => {
@@ -270,9 +195,6 @@
       saveState();
     }
 
-    /**
-     * Writes the active project state values into the DOM textareas.
-     */
     function syncStateToDOM() {
       const proj = appState.projects[appState.activeProject];
       TEXTAREA_IDS.forEach(id => {
@@ -281,11 +203,6 @@
       });
     }
 
-    /**
-     * Switches the active project: saves current DOM state, updates activeProject,
-     * restores the new project's state, and re-renders tabs.
-     * @param {string} name - The project name to switch to.
-     */
     function switchProject(name) {
       syncDOMToState();
       appState.activeProject = name;
@@ -293,9 +210,6 @@
       renderTabs();
     }
 
-    /**
-     * Prompts the user for a new project name and creates it.
-     */
     function createProject() {
       const name = prompt('Enter new project name:')?.trim();
       if (!name) return;
@@ -309,10 +223,6 @@
       renderManageList();
     }
 
-    /**
-     * Prompts the user to rename an existing project.
-     * @param {string} oldName - The current project name.
-     */
     function renameProject(oldName) {
       const newName = prompt('Rename project to:', oldName)?.trim();
       if (!newName || newName === oldName) return;
@@ -325,13 +235,9 @@
       renderManageList();
     }
 
-    /**
-     * Deletes a project after confirmation. Prevents deleting the last project.
-     * @param {string} name - The project name to delete.
-     */
     function deleteProject(name) {
       if (Object.keys(appState.projects).length <= 1) { alert('Cannot delete the last project.'); return; }
-      if (!confirm(`Are you sure you want to delete "${name}"? All its data will be lost.`)) return;
+      if (!confirm(`Delete "${name}"? All its data will be lost.`)) return;
       delete appState.projects[name];
       if (appState.activeProject === name) {
         appState.activeProject = Object.keys(appState.projects)[0];
@@ -342,110 +248,83 @@
       renderManageList();
     }
 
-    /**
-     * Renders the tab buttons into the #tab-container element.
-     */
     function renderTabs() {
       const container = document.getElementById('tab-container');
       container.innerHTML = '';
       Object.keys(appState.projects).forEach(name => {
+        const li = document.createElement('li');
+        li.className = 'nav-item';
         const btn = document.createElement('button');
         btn.type = 'button';
+        btn.className = 'nav-link' + (name === appState.activeProject ? ' active' : '');
         btn.textContent = name;
-        const isActive = (name === appState.activeProject);
-        btn.className = `px-4 py-2 rounded-md text-sm font-medium transition whitespace-nowrap ${isActive ? 'bg-white text-blue-700 shadow-sm border border-slate-300' : 'text-slate-600 hover:bg-slate-300 border border-transparent'}`;
+        btn.setAttribute('aria-current', name === appState.activeProject ? 'page' : 'false');
         btn.onclick = () => switchProject(name);
-        container.appendChild(btn);
+        li.appendChild(btn);
+        container.appendChild(li);
       });
     }
 
-    /** Opens the manage projects modal. */
     function openManageModal() { renderManageList(); document.getElementById('manage-modal').showModal(); }
-    /** Closes the manage projects modal. */
     function closeManageModal() { document.getElementById('manage-modal').close(); }
 
-    /**
-     * Renders the project list inside the manage modal with Rename/Delete buttons.
-     */
     function renderManageList() {
       const list = document.getElementById('modal-project-list');
       list.innerHTML = '';
       Object.keys(appState.projects).forEach(name => {
         const li = document.createElement('li');
-        li.className = 'flex justify-between items-center bg-slate-50 p-3 rounded border border-slate-200';
+        li.className = 'd-flex justify-content-between align-items-center gap-3 py-2 border-bottom';
 
         const span = document.createElement('span');
-        span.className = 'font-medium text-slate-800 truncate mr-4';
-        span.textContent = name + (name === appState.activeProject ? ' (Active)' : '');
+        span.className = 'text-truncate';
+        span.textContent = name + (name === appState.activeProject ? ' (active)' : '');
 
-        const btnDiv = document.createElement('div');
-        btnDiv.className = 'flex gap-2 shrink-0';
+        const actions = document.createElement('div');
+        actions.className = 'd-flex gap-2 flex-shrink-0';
 
         const renameBtn = document.createElement('button');
         renameBtn.type = 'button';
         renameBtn.textContent = 'Rename';
-        renameBtn.className = 'text-xs px-2 py-1 rounded bg-slate-200 hover:bg-slate-300 text-slate-700 transition';
+        renameBtn.className = 'btn btn-sm btn-outline-secondary';
         renameBtn.onclick = () => renameProject(name);
 
         const delBtn = document.createElement('button');
         delBtn.type = 'button';
         delBtn.textContent = 'Delete';
-        delBtn.className = 'text-xs px-2 py-1 rounded bg-rose-100 hover:bg-rose-200 text-rose-700 transition disabled:opacity-50';
+        delBtn.className = 'btn btn-sm btn-outline-danger';
         delBtn.disabled = Object.keys(appState.projects).length <= 1;
         delBtn.onclick = () => deleteProject(name);
 
-        btnDiv.appendChild(renameBtn);
-        btnDiv.appendChild(delBtn);
+        actions.appendChild(renameBtn);
+        actions.appendChild(delBtn);
         li.appendChild(span);
-        li.appendChild(btnDiv);
+        li.appendChild(actions);
         list.appendChild(li);
       });
     }
 
-    /**
-     * Fetches the system prompt from GitHub and displays it in the textarea.
-     * On failure, shows an error message and lets the user paste manually.
-     * @returns {Promise<void>} Resolves when fetch completes (success or fallback).
-     */
     async function fetchSystemPrompt() {
       const textarea = document.getElementById('system-prompt');
       const status = document.getElementById('fetch-status');
       status.textContent = 'Fetching…';
       try {
         const response = await fetch(SYSTEM_PROMPT_URL);
-        if (!response.ok) {
-          throw new Error(`HTTP ${response.status}`);
-        }
+        if (!response.ok) throw new Error(`HTTP ${response.status}`);
         const text = await response.text();
         textarea.value = text;
-        status.textContent = `✅ Loaded (${(text.length / 1024).toFixed(1)} KB)`;
+        status.textContent = `Loaded · ${(text.length / 1024).toFixed(1)} KB`;
       } catch (error) {
-        // Graceful degradation: allow manual paste instead of hard-failing.
-        status.textContent = `⚠️ Fetch failed (${error.message}). Paste manually below.`;
+        status.textContent = `Fetch failed (${error.message}) — paste manually.`;
       }
     }
 
-    /**
-     * Populates the Manager Message textarea with a preset command.
-     * @param {string} command - The preset command text. Empty string = Custom.
-     * @returns {void}
-     */
     function selectPreset(command) {
       const textarea = document.getElementById('manager-message');
       textarea.value = command;
-      // Focus for immediate editing if a custom command is intended.
       textarea.focus();
       syncDOMToState();
     }
 
-    /**
-     * Assembles the structured Markdown output from the five inputs:
-     * System Instructions + Manager Message (+ Custom Notes) + optional
-     * Project Tree + optional Context Report + Task File. The Project Tree
-     * and Context Report sections are only emitted when the user provides
-     * them, so the output stays clean otherwise.
-     * @returns {void} Writes the assembled Markdown into the output textarea.
-     */
     function generateMarkdown() {
       const systemPrompt = document.getElementById('system-prompt').value.trim();
       const managerMessage = document.getElementById('manager-message').value.trim();
@@ -454,92 +333,47 @@
       const contextReport = document.getElementById('context-report').value.trim();
       const taskFile = document.getElementById('task-file').value.trim();
 
-      // Build the Manager Message block: preset/custom command plus optional notes.
       let managerBlock = managerMessage;
-      if (customNotes) {
-        managerBlock = managerBlock ? `${managerBlock}\n\n${customNotes}` : customNotes;
-      }
+      if (customNotes) managerBlock = managerBlock ? `${managerBlock}\n\n${customNotes}` : customNotes;
 
       const sections = [
         '# System Instructions',
-        systemPrompt || '_No system prompt provided. Fetch it or paste it manually._',
-        '',
-        '---',
-        '',
+        systemPrompt || '_No system prompt provided._',
+        '', '---', '',
         '# Manager Message',
         managerBlock || '_No manager message provided._',
       ];
 
-      // Optional Project Tree: included only when a tree/subtree is provided.
-      if (projectTree) {
-        sections.push(
-          '',
-          '---',
-          '',
-          '# Project Tree',
-          projectTree
-        );
-      }
-
-      // Optional Context Report: included only when a report is provided.
-      if (contextReport) {
-        sections.push(
-          '',
-          '---',
-          '',
-          '# Context Report',
-          contextReport
-        );
-      }
-
-      sections.push(
-        '',
-        '---',
-        '',
-        '# Task File',
-        taskFile || '_No task file provided._'
-      );
+      if (projectTree) sections.push('', '---', '', '# Project Tree', projectTree);
+      if (contextReport) sections.push('', '---', '', '# Context Report', contextReport);
 
+      sections.push('', '---', '', '# Task File', taskFile || '_No task file provided._');
       document.getElementById('output').value = sections.join('\n');
     }
 
-    /**
-     * Copies the generated Markdown to the clipboard using the Clipboard API.
-     * Falls back to selecting the textarea content if the API is unavailable.
-     * @returns {Promise<void>} Resolves after copy attempt (success or fallback).
-     */
     async function copyToClipboard() {
       const output = document.getElementById('output');
       const status = document.getElementById('copy-status');
       try {
         await navigator.clipboard.writeText(output.value);
-        status.textContent = '✅ Copied to clipboard';
+        status.textContent = 'Copied';
       } catch (error) {
-        // Fallback: select the text so the user can copy manually (CSP/permission denied).
         output.focus();
         output.select();
-        status.textContent = '⚠️ Clipboard API unavailable — selected, press Ctrl+C';
+        status.textContent = 'Clipboard unavailable — press Ctrl+C';
       }
-      // Clear the transient status after a few seconds.
       setTimeout(() => { status.textContent = ''; }, 3000);
     }
 
-    // Initialize on DOM ready
     document.addEventListener('DOMContentLoaded', () => {
       loadState();
       syncStateToDOM();
       renderTabs();
-
-      // Auto-save on any keystroke in the primary textareas
       TEXTAREA_IDS.forEach(id => {
         const el = document.getElementById(id);
         if (el) el.addEventListener('input', syncDOMToState);
       });
-
-      // If system prompt is completely empty on load, attempt fetch
-      if (!appState.projects[appState.activeProject]['system-prompt']) {
-        fetchSystemPrompt();
-      }
+      if (!appState.projects[appState.activeProject]['system-prompt']) fetchSystemPrompt();
     });
   </script>
 </body>
diff --git a/tools/prompt-composer/theme.css b/tools/prompt-composer/theme.css
new file mode 100644
index 0000000..9840339
--- /dev/null
+++ b/tools/prompt-composer/theme.css
@@ -0,0 +1,187 @@
+/* Graphite Desk theme for Bootstrap 5.3 — see DESIGN.md at the repo root.
+   Tokens are authoritative; Bootstrap variables are the adapter. */
+:root {
+  --gd-bg: #0b0e14;
+  --gd-surface: #141a23;
+  --gd-raised: #1b2430;
+  --gd-border: #263141;
+  --gd-text: #e6ebf2;
+  --gd-muted: #8c99ab;
+  --gd-accent: #5eead4;
+  --gd-accent-hover: #86f2e2;
+  --gd-accent-ink: #04211d;
+  --gd-success: #34d399;
+  --gd-warning: #fbbf24;
+  --gd-danger: #f87171;
+  --gd-info: #7dd3fc;
+  --gd-mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
+}
+
+[data-bs-theme="dark"] {
+  --bs-body-bg: var(--gd-bg);
+  --bs-body-color: var(--gd-text);
+  --bs-secondary-color: var(--gd-muted);
+  --bs-tertiary-bg: var(--gd-surface);
+  --bs-secondary-bg: var(--gd-raised);
+  --bs-emphasis-color: var(--gd-text);
+  --bs-border-color: var(--gd-border);
+  --bs-border-color-translucent: var(--gd-border);
+  --bs-primary: var(--gd-accent);
+  --bs-primary-rgb: 94, 234, 212;
+  --bs-success: var(--gd-success);
+  --bs-warning: var(--gd-warning);
+  --bs-danger: var(--gd-danger);
+  --bs-info: var(--gd-info);
+  --bs-link-color: var(--gd-accent);
+  --bs-link-hover-color: var(--gd-accent-hover);
+  --bs-body-font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
+  --bs-body-font-size: 14px;
+  --bs-font-monospace: var(--gd-mono);
+  --bs-border-radius-sm: 4px;
+  --bs-border-radius: 6px;
+  --bs-border-radius-lg: 8px;
+  --bs-border-radius-xl: 12px;
+  --bs-focus-ring-color: rgba(94, 234, 212, 0.35);
+  --bs-box-shadow: none;
+  --bs-box-shadow-sm: none;
+  --bs-box-shadow-lg: 0 24px 60px rgba(4, 7, 12, 0.55);
+}
+
+body {
+  background: var(--gd-bg);
+  font-size: 14px;
+  line-height: 1.45;
+}
+
+/* Layout */
+.page { max-width: 960px; margin: 0 auto; padding: 24px 24px 32px; }
+.page-wide { max-width: 1200px; }
+.section-gap { margin-bottom: 24px; }
+.label {
+  font-size: 11px;
+  font-weight: 600;
+  letter-spacing: 0.06em;
+  text-transform: uppercase;
+  color: var(--gd-muted);
+}
+
+/* Surfaces */
+.card {
+  --bs-card-bg: var(--gd-surface);
+  --bs-card-border-color: var(--gd-border);
+  --bs-card-border-radius: 8px;
+  --bs-card-inner-border-radius: 7px;
+  --bs-card-spacer-y: 16px;
+  --bs-card-spacer-x: 16px;
+  box-shadow: none !important;
+}
+.card-header {
+  background: var(--gd-surface);
+  border-bottom: 1px solid var(--gd-border);
+  font-size: 11px;
+  font-weight: 600;
+  letter-spacing: 0.06em;
+  text-transform: uppercase;
+  color: var(--gd-muted);
+}
+
+/* Buttons */
+.btn { border-radius: 6px; font-size: 13px; font-weight: 500; }
+.btn-sm { border-radius: 6px; font-size: 12px; }
+.btn-primary {
+  --bs-btn-bg: var(--gd-accent);
+  --bs-btn-border-color: var(--gd-accent);
+  --bs-btn-color: var(--gd-accent-ink);
+  --bs-btn-hover-bg: var(--gd-accent-hover);
+  --bs-btn-hover-border-color: var(--gd-accent-hover);
+  --bs-btn-hover-color: var(--gd-accent-ink);
+  --bs-btn-active-bg: var(--gd-accent-hover);
+  --bs-btn-active-color: var(--gd-accent-ink);
+  --bs-btn-disabled-bg: var(--gd-raised);
+  --bs-btn-disabled-color: var(--gd-muted);
+}
+.btn-outline-secondary {
+  --bs-btn-color: var(--gd-text);
+  --bs-btn-border-color: var(--gd-border);
+  --bs-btn-hover-bg: var(--gd-raised);
+  --bs-btn-hover-border-color: var(--gd-border);
+  --bs-btn-hover-color: var(--gd-text);
+}
+.btn-outline-danger {
+  --bs-btn-color: var(--gd-danger);
+  --bs-btn-border-color: var(--gd-danger);
+  --bs-btn-hover-bg: rgba(248, 113, 113, 0.12);
+  --bs-btn-hover-color: var(--gd-danger);
+}
+
+/* Chips: neutral by default, at most four semantic tints */
+.chip {
+  border: 1px solid var(--gd-border);
+  background: var(--gd-raised);
+  color: var(--gd-text);
+  border-radius: 6px;
+  font-size: 12px;
+  padding: 3px 10px;
+  line-height: 1.5;
+}
+.chip:hover { border-color: var(--gd-muted); }
+.chip[aria-pressed="true"] { border-color: var(--gd-accent); color: var(--gd-accent); }
+.chip-info { color: var(--gd-info); border-color: rgba(125, 211, 252, 0.45); }
+.chip-success { color: var(--gd-success); border-color: rgba(52, 211, 153, 0.45); }
+.chip-warning { color: var(--gd-warning); border-color: rgba(251, 191, 36, 0.45); }
+.chip-danger { color: var(--gd-danger); border-color: rgba(248, 113, 113, 0.45); }
+
+/* Forms */
+.form-control, .form-select {
+  background: var(--gd-bg);
+  border-color: var(--gd-border);
+  color: var(--gd-text);
+  border-radius: 6px;
+  font-size: 13px;
+}
+.form-control:focus, .form-select:focus {
+  background: var(--gd-bg);
+  color: var(--gd-text);
+  border-color: var(--gd-accent);
+  box-shadow: 0 0 0 3px var(--bs-focus-ring-color);
+}
+.form-control::placeholder { color: var(--gd-muted); }
+textarea.form-control { font-family: var(--gd-mono); line-height: 1.5; }
+.form-label { font-size: 12px; color: var(--gd-muted); margin-bottom: 4px; }
+
+/* Tabs */
+.nav-tabs { border-bottom: 1px solid var(--gd-border); gap: 4px; }
+.nav-tabs .nav-link {
+  border: 0;
+  border-bottom: 2px solid transparent;
+  color: var(--gd-muted);
+  font-size: 13px;
+  font-weight: 500;
+  padding: 6px 12px;
+  border-radius: 6px 6px 0 0;
+}
+.nav-tabs .nav-link:hover { color: var(--gd-text); background: var(--gd-raised); }
+.nav-tabs .nav-link.active {
+  color: var(--gd-text);
+  background: transparent;
+  border-bottom-color: var(--gd-accent);
+}
+
+/* Badges */
+.badge { font-family: var(--gd-mono); font-size: 11px; border-radius: 4px; padding: 2px 6px; }
+
+/* Dialog */
+dialog.gd-dialog {
+  background: var(--gd-surface);
+  border: 1px solid var(--gd-border);
+  border-radius: 12px;
+  color: var(--gd-text);
+  box-shadow: 0 24px 60px rgba(4, 7, 12, 0.55);
+  padding: 0;
+  width: min(480px, 92vw);
+}
+dialog.gd-dialog::backdrop { background: rgba(4, 7, 12, 0.72); }
+
+.mono { font-family: var(--gd-mono); }
+.text-muted { color: var(--gd-muted) !important; }
+a { color: var(--gd-accent); }
diff --git a/tools/prompt-composer/vendor/bootstrap.bundle.min.js b/tools/prompt-composer/vendor/bootstrap.bundle.min.js
new file mode 100644
index 0000000..04e9185
Binary files /dev/null and b/tools/prompt-composer/vendor/bootstrap.bundle.min.js differ
diff --git a/tools/prompt-composer/vendor/bootstrap.min.css b/tools/prompt-composer/vendor/bootstrap.min.css
new file mode 100644
index 0000000..3993414
Binary files /dev/null and b/tools/prompt-composer/vendor/bootstrap.min.css differ
```
<!-- END_GIT_DIFF -->
