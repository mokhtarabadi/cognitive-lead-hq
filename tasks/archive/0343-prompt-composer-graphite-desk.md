# Task 343: Port Prompt Composer to the Graphite Desk design system

**File:** `tasks/archive/0343-prompt-composer-graphite-desk.md`
**Source:** manager
**Type:** feature
**Status:** superseded
**Superseded-By:** `344-planner-dashboard-and-prompt-composer-on-graphite-desk`
**Superseded-At:** `2026-10-24 21:19 UTC`
**Estimate:** 1.5h
**Sprint:** S26-W43
**Milestone:** M01

## Goal

Make `tools/prompt-composer/index.html` follow `DESIGN.md` (Graphite Desk) instead of raw Tailwind defaults, so both Cognitive Lead surfaces share one palette, one radius scale, one type hierarchy, and one chip language.

## Manager's Notes

- Source of truth: `DESIGN.md` at the repo root (chosen direction A, 2026-10-24). No new colors outside the palette.
- The composer currently loads `https://cdn.tailwindcss.com` and uses default slate/blue plus six rainbow preset pills; both contradict the system.
- Planner dashboard was re-skinned in task 339 to the same tokens; this task brings the composer into parity.

## Local TODOs

- [ ] Replace the Tailwind CDN with a local `<style>` block built from the DESIGN.md tokens (`--bg`, `--surface`, `--surface-raised`, `--border`, `--text`, `--muted`, `--accent`, `--accent-ink`, four state colors, `--mono`)
- [ ] Rebuild the layout classes (container 960px, 8px grid, 24px page padding) so no Tailwind utility classes remain
- [ ] Convert preset pills to neutral chips with at most four semantic tints
- [ ] Normalise radii to 4/6/8/12 and remove all box-shadows except the manage dialog
- [ ] Apply mono type to generated markdown output and system-prompt textarea
- [ ] Keep every behaviour identical: localStorage projects, fetch system prompt, copy to clipboard, dialog

## Acceptance Criteria

- [ ] Zero external network dependencies at runtime (no CDN script, no webfont link)
- [ ] Every color and radius in the file resolves to a DESIGN.md token
- [ ] Preset chips use neutral plus at most four semantic tints
- [ ] All existing composer actions still work (project CRUD, fetch, generate, copy)
- [ ] Focus states are visible on every interactive element

## Verification Evidence

- **Test command:** `node -e` parse of the inline script plus a manual pass over the composer in the browser
- **Expected result:** script parses, no console errors, every control usable by keyboard
- **Actual result:** _(pending — task not started)_
- **Exit code:** _(pending)_

## Definition of Done

- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated
- [ ] Deployed (the composer is served from the repo `tools/` directory, no service restart)

## Risk & Rollback

- **Risk:** removing Tailwind means reimplementing layout by hand; a missed utility silently changes spacing.
- **Rollback:** restore the previous `index.html` from git; the tool is standalone.

> **Superseded:** This task was bundled into META task `344-planner-dashboard-and-prompt-composer-on-graphite-desk` and archived on 2026-10-24 21:19 UTC. See `tasks/backlog/344-planner-dashboard-and-prompt-composer-on-graphite-desk.md` (or its Kanban successor) for the unified execution. History preserved via `git log --follow -- tasks/archive/0343-prompt-composer-graphite-desk.md`.

## Execution Log & Reasoning

Created from the 2026-10-24 design-direction decision (option A, Graphite Desk). Not started; `DESIGN.md` is the input contract.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

<!-- END_GIT_DIFF -->
