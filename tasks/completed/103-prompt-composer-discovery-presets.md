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
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 96990bd..6e91e24 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -9,6 +9,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 ### Added
 
 - **Prompt Composer Web Tool** — new standalone HTML tool at `tools/prompt-composer/index.html` that automates the Brain↔Hands copy-paste workflow. Fetches the system prompt from GitHub, provides preset Manager commands, allows custom notes and task file pasting, generates structured Markdown output, and copies to clipboard. Deployed to GitHub Pages via `.github/workflows/deploy-prompt-composer.yml`. `system-prompt.md` version unchanged.
+- **Prompt Composer — Task Discovery presets + Project Tree input (Task 103)** — the prompt-composer tool's preset command row gains two out-of-the-box context-gathering commands: **Task Discovery** (instructs the Orchestrator to generate a `<hands_discovery_task>` that gathers the working task's context — directory tree + persisted tree report, Core SOP files, vertical-slice signatures, compiled context report) and **Collect Context** (lightweight `code-search`-skill variant that returns the report path). A new optional **Project Tree** textarea lets the user paste a directory tree/subtree, which is emitted as a `# Project Tree` section in the generated Markdown only when non-empty. Existing named functions (`fetchSystemPrompt`, `generateMarkdown`, `copyToClipboard`, `selectPreset`) preserved; README feature list updated. `system-prompt.md` version unchanged.
 
 ## [8.4.6] - 2026-08-16
 
diff --git a/README.md b/README.md
index 94c7a58..dca4fb5 100644
--- a/README.md
+++ b/README.md
@@ -95,7 +95,8 @@ The repository includes a standalone web tool at `tools/prompt-composer/index.ht
 
 **Features:**
 - Fetches the latest `system-prompt.md` from GitHub
-- Preset Manager commands (Phase 0, Approved, QA, Code Review, Closure)
+- Preset Manager commands (Phase 0, Task Discovery, Collect Context, Approved, QA, Code Review, Closure)
+- Optional Project Tree input — included in the generated Markdown when provided
 - Custom notes and task file pasting
 - Generates structured Markdown output
 - One-click copy to clipboard
diff --git a/tools/prompt-composer/index.html b/tools/prompt-composer/index.html
index e3100a1..1a4551a 100644
--- a/tools/prompt-composer/index.html
+++ b/tools/prompt-composer/index.html
@@ -4,8 +4,10 @@
   <!--
     Prompt Composer — Cognitive Lead AI
     Standalone web tool that automates the Brain<->Hands copy-paste workflow.
-    Fetches system-prompt.md from GitHub, provides preset Manager commands,
-    assembles a structured Markdown message, and copies it to the clipboard.
+    Fetches system-prompt.md from GitHub, provides preset Manager commands
+    (including Task Discovery / Collect Context for context gathering),
+    accepts an optional Project Tree input, assembles a structured Markdown
+    message, and copies it to the clipboard.
     Self-contained: only external dependency is the Tailwind CSS CDN.
   -->
   <meta charset="UTF-8">
@@ -67,6 +69,8 @@
         <div class="flex flex-wrap gap-2" role="group" aria-label="Preset commands">
           <button type="button" onclick="selectPreset('This is a new project. Start Phase 0.')" class="px-3 py-1.5 rounded-full bg-slate-200 hover:bg-slate-300 text-sm transition">New Project — Phase 0</button>
           <button type="button" onclick="selectPreset('This is an existing project. Start Phase 0.')" class="px-3 py-1.5 rounded-full bg-slate-200 hover:bg-slate-300 text-sm transition">Existing Project — Phase 0</button>
+          <button type="button" onclick="selectPreset('Generate a <hands_discovery_task> for the task we are working on. Instruct the Hands to gather the necessary context: get and persist the project directory tree, read all Core SOP files (AGENTS.md, DESIGN.md, docs/architecture.md, docs/data_model.md, docs/conventions.md), extract vertical slice signatures for the relevant module, and compile everything into a single context report. Use the provided Project Tree as the target context when available. Do not proceed to implementation until the discovery context has been returned and reviewed.')" class="px-3 py-1.5 rounded-full bg-sky-200 hover:bg-sky-300 text-sm transition">Task Discovery</button>
+          <button type="button" onclick="selectPreset('Load the code-search skill and collect context for the current task. Get the project directory tree, extract vertical slice signatures for the target module, and read all Core SOP files (AGENTS.md, DESIGN.md, docs/architecture.md, docs/data_model.md, docs/conventions.md). Compile everything into a single context report. Do NOT read the report yourself — return the file path to me.')" class="px-3 py-1.5 rounded-full bg-cyan-200 hover:bg-cyan-300 text-sm transition">Collect Context</button>
           <button type="button" onclick="selectPreset('Approved')" class="px-3 py-1.5 rounded-full bg-emerald-200 hover:bg-emerald-300 text-sm transition">Approved</button>
           <button type="button" onclick="selectPreset('Approved for closure')" class="px-3 py-1.5 rounded-full bg-emerald-200 hover:bg-emerald-300 text-sm transition">Approved for Closure</button>
           <button type="button" onclick="selectPreset('[QA Engineer], please perform adversarial testing.')" class="px-3 py-1.5 rounded-full bg-amber-200 hover:bg-amber-300 text-sm transition">QA — Adversarial Testing</button>
@@ -96,9 +100,23 @@
       ></textarea>
     </section>
 
+    <!-- ===================== Project Tree Section (Optional) ===================== -->
+    <section aria-labelledby="project-tree-heading">
+      <h2 id="project-tree-heading" class="text-lg font-semibold mb-2">3. Project Tree <span class="text-sm font-normal text-slate-400">(optional)</span></h2>
+      <!-- Optional codebase context: paste a directory tree or subtree here.
+           If non-empty, generateMarkdown() includes it as a "# Project Tree" section. -->
+      <textarea
+        id="project-tree"
+        rows="10"
+        class="w-full font-mono text-sm p-3 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
+        placeholder="Optional: paste the project directory tree (or a subtree) here. If provided, it is included in the generated Markdown as a # Project Tree section."
+        aria-label="Project Tree"
+      ></textarea>
+    </section>
+
     <!-- ===================== Task File Section ===================== -->
     <section aria-labelledby="task-file-heading">
-      <h2 id="task-file-heading" class="text-lg font-semibold mb-2">3. Task File</h2>
+      <h2 id="task-file-heading" class="text-lg font-semibold mb-2">4. Task File</h2>
       <textarea
         id="task-file"
         rows="10"
@@ -119,7 +137,7 @@
       </button>
 
       <div class="mt-4 flex items-center gap-3">
-        <h2 id="generate-heading" class="text-lg font-semibold">4. Output</h2>
+        <h2 id="generate-heading" class="text-lg font-semibold">5. Output</h2>
         <button
           type="button"
           onclick="copyToClipboard()"
@@ -193,14 +211,17 @@
     }
 
     /**
-     * Assembles the structured Markdown output from the three inputs:
-     * System Instructions + Manager Message (+ Custom Notes) + Task File.
+     * Assembles the structured Markdown output from the four inputs:
+     * System Instructions + Manager Message (+ Custom Notes) + optional
+     * Project Tree + Task File. The Project Tree section is only emitted
+     * when the user provides one, so the output stays clean otherwise.
      * @returns {void} Writes the assembled Markdown into the output textarea.
      */
     function generateMarkdown() {
       const systemPrompt = document.getElementById('system-prompt').value.trim();
       const managerMessage = document.getElementById('manager-message').value.trim();
       const customNotes = document.getElementById('custom-notes').value.trim();
+      const projectTree = document.getElementById('project-tree').value.trim();
       const taskFile = document.getElementById('task-file').value.trim();
 
       // Build the Manager Message block: preset/custom command plus optional notes.
@@ -217,12 +238,26 @@
         '',
         '# Manager Message',
         managerBlock || '_No manager message provided._',
+      ];
+
+      // Optional Project Tree: included only when a tree/subtree is provided.
+      if (projectTree) {
+        sections.push(
+          '',
+          '---',
+          '',
+          '# Project Tree',
+          projectTree
+        );
+      }
+
+      sections.push(
         '',
         '---',
         '',
         '# Task File',
-        taskFile || '_No task file provided._',
-      ];
+        taskFile || '_No task file provided._'
+      );
 
       document.getElementById('output').value = sections.join('\n');
     }
```
<!-- END_GIT_DIFF -->
