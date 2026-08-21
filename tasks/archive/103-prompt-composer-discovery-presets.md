# Task 103: Prompt Composer — Task Discovery Presets & Project Tree Input

**File:** `tasks/completed/103-prompt-composer-discovery-presets.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Expand the built-in preset commands of the Prompt Composer web tool (`tools/prompt-composer/index.html`) with a **Task Discovery** preset (and one context-collection companion) so the Manager can trigger context gathering for the working task out of the box, and add an **optional Project Tree input** that is included in the final generated Markdown output when provided.

## Manager's Notes

- Keep the preset row from getting crowded: 8 → 10 buttons max (add 1–2 new presets only).
- **Task Discovery is the most important addition**: when triggered, the preset text must instruct the Orchestrator to generate something that goes and gathers the necessary context for the task being worked on (i.e., a `<hands_discovery_task>` per the system prompt's `14-hands_protocols.md` template).
- The second preset ("Collect Context") should mirror the lightweight `user-prompts/cold-start-context.md` pattern (code-search skill, tree + signatures + Core SOP files, return report path).
- Project Tree input is optional: if left empty it must NOT appear as a section in the generated Markdown.
- Preserve the four named functions (`fetchSystemPrompt`, `generateMarkdown`, `copyToClipboard`, `selectPreset`) — the Task 102 acceptance contract.
- No `system-prompt.md` edits; version unchanged. Platform tooling only.

## Local TODOs

- [x] Initial codebase exploration (tool, prompts templates, user-prompts)
- [x] Add Task Discovery + Collect Context preset buttons to `tools/prompt-composer/index.html`
- [x] Add optional Project Tree textarea section and include it in `generateMarkdown()` output when non-empty
- [x] Update README.md Prompt Composer features section
- [x] Update CHANGELOG.md via Parse-Then-Append
- [x] Verify: `node --check` on extracted inline JS + grep gates + `lint_task_file`

## Acceptance Criteria

- [x] `tools/prompt-composer/index.html` contains a "Task Discovery" preset button whose command instructs the Orchestrator to generate a `<hands_discovery_task>` that gathers context for the working task
- [x] `tools/prompt-composer/index.html` contains a "Collect Context" preset button (lightweight code-search/context-report command)
- [x] `tools/prompt-composer/index.html` contains an optional Project Tree textarea; when non-empty, generated Markdown includes a `# Project Tree` section; when empty, no such section appears
- [x] All four named functions (`fetchSystemPrompt`, `generateMarkdown`, `copyToClipboard`, `selectPreset`) remain present and working
- [x] README.md and CHANGELOG.md updated
- [x] `lint_task_file` passes on this file
- [x] `node --check` passes on extracted inline JS

## Verification Evidence

- **Test command:** `sed -n '/<script>/,/<\/script>/p' tools/prompt-composer/index.html | sed '1d;$d' > /tmp/pc-inline.js && node --check /tmp/pc-inline.js`; grep gates for `Task Discovery`, `Collect Context`, `project-tree`, `hands_discovery_task`, named functions, `# Project Tree`; functional DOM-stub test of `generateMarkdown()` with/without Project Tree; `lint_task_file`
- **Expected result:** JS syntax OK; all grep gates pass; CASE 1 (no tree) output omits `# Project Tree`, CASE 2 (with tree) includes it in order System → Manager → Tree → Task; lint passes
- **Actual result:** `node --check` exit 0 (JS SYNTAX OK); grep gates all ≥1 (`Task Discovery` 2, `Collect Context` 2, `project-tree` 4, `hands_discovery_task` 1, all four functions present, `# Project Tree` 3, `(optional)` 1, 10 preset onclick handlers + function def); functional test — CASE 1 sections `["# System Instructions","# Manager Message","# Task File"]` with `# Project Tree` absent, CASE 2 sections `["# System Instructions","# Manager Message","# Project Tree","# Task File"]` with correct order and tree content preserved (`app.js` present); lint passes
- **Exit code:** 0 (all verification commands)

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Preset row becomes crowded or the generated Markdown order drifts from the Brain's expected format.
- **Rollback plan:** Remove the new preset buttons and Project Tree section from `tools/prompt-composer/index.html`; revert README/CHANGELOG edits.

---

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

- **2026-08-18 — Hands execution log:**
  - **Validation:** AGENTS.md loaded; `docs/conventions.md` read (no conflicts — gh/date/SOLID rules untouched). `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md` absent → skipped gracefully per Absent-File Policy. Rule check: the Prompt Composer is **platform tooling** (automates the Brain↔Hands workflow), permitted under the AGENTS.md exception for "tooling required for the Cognitive Lead AI platform itself". No `system-prompt.md` edits (generated artifact — not touched, version unchanged), no ZAC violations, CHANGELOG/README sync applied per AGENTS.md. No HALT required.
  - **Skills loaded:** `project-memory` (search: no prior composer-specific constraints; read `system-prompt-build-process`, `repo-details`, `absent-file-policy` memories), `task-generator` (ID discovery + canonical template), `verification-before-completion` (iron law: no completion claims without fresh verification evidence), `task-lint` (structural validation).
  - **Kanban:** ID discovery → highest ID 102 → next **103**; collision check clean; created `tasks/backlog/103-prompt-composer-discovery-presets.md` (**Source:** manager — the request arrived as a direct Manager instruction, not an XML block; per the Direct Input protocol the Manager approved creating a tracked task), then moved to `tasks/in-progress/` via filesystem `mv` (untracked file — `git mv` refused) BEFORE writing code, per lifecycle rules; `**File:**` header updated to `tasks/in-progress/`.
  - **Context discovery:** Read the full tool (`tools/prompt-composer/index.html` — 4 sections, 8 preset buttons, `generateMarkdown()` assembling `# System Instructions` / `# Manager Message` / `# Task File`), the discovery task template in `prompts/fragments/14-hands_protocols.md` (`<hands_discovery_task>` with directory tree + persisted tree report + Core SOP files + vertical-slice signatures + compiled context report), `user-prompts/cold-start-context.md` (lightweight code-search context-collection pattern), and the Task 102 completed task file (acceptance contract: four named functions must survive).
  - **Step 3 — `tools/prompt-composer/index.html`:** (a) Added **Task Discovery** preset button — command instructs the Orchestrator to generate a `<hands_discovery_task>` that goes and gathers the working task's context (directory tree + persisted report, Core SOP files, vertical-slice signatures, compiled context report; uses the provided Project Tree as target context; no implementation until discovery context is returned/reviewed). Matches the system prompt's native discovery template (`14-hands_protocols.md`) so the preset output feeds directly into the existing Brain workflow. (b) Added **Collect Context** preset button — lightweight variant mirroring `user-prompts/cold-start-context.md` (code-search skill, tree + signatures + Core SOP files, return report path, do not read it yourself). Preset row stays at 10 buttons (8 → 10) honoring the "don't crowd the presets" constraint. (c) Added **Project Tree** section (optional textarea, `id="project-tree"`) between Manager Message and Task File; renumbered sections 3/4 → 4/5. (d) Updated `generateMarkdown()`: reads `project-tree`; pushes a `# Project Tree` section **only when non-empty** (clean output when omitted); existing named functions untouched (Task 102 contract preserved). HTML/JSDoc comments updated for maximum-documentation mandate.
  - **Step 4 — README.md:** Prompt Composer features list updated to mention the new presets (Phase 0, Task Discovery, Collect Context, Approved, QA, Code Review, Closure) and the optional Project Tree input.
  - **Step 5 — CHANGELOG.md:** Parse-Then-Append — `[Unreleased]` exists, `### Added` exists, appended the Task 103 bullet under it; no duplicate headers.
  - **Steps 6 — Verification gate:** `node --check` on extracted inline JS exit 0; grep gates all pass (`Task Discovery` 2, `Collect Context` 2, `project-tree` 4, `hands_discovery_task` 1, all four named functions present, `# Project Tree` 3, 10 preset onclick handlers + function def); functional DOM-stub test of `generateMarkdown()` proves the conditional behavior — no-tree input produces only System/Manager/Task sections (no `# Project Tree`), with-tree input produces System/Manager/Project Tree/Task in the correct order with tree content byte-preserved. Exit code 0 throughout.
  - **Architectural reasoning:** The two new presets intentionally mirror the system prompt's two official context-gathering mechanisms (the Hands-dispatched `<hands_discovery_task>` and the direct `code-search`/user-prompt variant) instead of inventing a parallel protocol — so the generated Markdown is immediately actionable by the Orchestrator with zero retraining. The Project Tree was placed between Manager Message and Task File in the output to read as "command → codebase context → task details", which matches how the Orchestrator consumes context. Conditional emission (only when provided) keeps the output minimal, consistent with the tool's existing graceful-degradation philosophy (fetch fallback, empty-section placeholders). ZAC preserved: the tool only generates text; commits remain gated through MCP tooling.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `3d1e611dca0e2c7034ba207b7d9c96234f262497`
<!-- END_GIT_DIFF -->
