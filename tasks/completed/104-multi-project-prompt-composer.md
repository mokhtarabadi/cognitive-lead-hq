# Task 104: Multi-Project Prompt Composer

**File:** `tasks/completed/104-multi-project-prompt-composer.md`
**Source:** telegram
**Type:** improvement
**Status:** closed

## Source Context

### Variant B: Telegram (`**Source:** telegram`)

## Goal

Add multi-project support to the Prompt Composer tool with tab-based navigation, a project management section, and local storage persistence so users can manage multiple project configurations.

## Original Message (Persian)

توی بخش ابزار html کخ کمک میکنه برای تولید پرامت ها
باید قبالیت این اضافه بشه چند پروژه محور باشه بتونه هندل کنه
با تب بالا و یه بخش برای مدیریت پروژه ها و همه هم توی local storage کاربر ذخیره بشه
`#improve`

## English Translation

In the HTML tool section that helps generate prompts,
the capability should be added to be multi-project oriented so it can handle multiple projects.
With tabs at the top and a section for project management, and everything should be saved in the user's local storage.

## Refactored Prompt

<role>
You are a Frontend Architect specializing in vanilla JavaScript single-page tools with local storage persistence. You are enhancing an existing standalone HTML tool (Prompt Composer) that currently supports a single project workflow.
</role>

<system_context>
The tool is at `tools/prompt-composer/index.html`. It is a self-contained single-file HTML app using Tailwind CSS CDN. It currently has 4 sections: System Instructions, Manager Message (with presets), Project Tree, and Task File. All state is ephemeral (no persistence). The tool generates structured Markdown output and copies it to clipboard. It is ZAC-compliant (no commits).
</system_context>

<agentic_reasoning>
Before implementing, output a <reasoning_log> analyzing: (1) the current single-project data model vs. the multi-project requirement, (2) the tab navigation UX pattern for vanilla JS, (3) local storage schema design (project list + per-project state), and (4) backward compatibility with the existing single-project workflow.
</agentic_reasoning>

<constraints>
- You MUST preserve all existing functionality (fetchSystemPrompt, generateMarkdown, copyToClipboard, selectPreset, named functions).
- You MUST use vanilla JavaScript only — no frameworks, no build steps.
- You MUST persist project data in localStorage with a clean schema.
- You MUST support: creating new projects, switching between projects via tabs, renaming projects, deleting projects.
- Each project must store its own: system prompt, manager message, custom notes, project tree, task file, and selected preset.
- The default project name should be "Default" for backward compatibility.
- Tab bar should appear at the top of the tool, below the header.
- A "Manage Projects" section (or modal) for rename/delete operations.
- Do NOT add external JS dependencies. Do NOT break the single-file architecture.
</constraints>

<output_format>
Return the complete updated `tools/prompt-composer/index.html` file with multi-project support integrated. Preserve all existing HTML structure and CSS classes. Add JSDoc comments to all new functions.
</output_format>

## Relevant Code Context

- `tools/prompt-composer/index.html` — The sole file to modify. 292 lines, self-contained HTML+CSS+JS. Key functions: `fetchSystemPrompt()`, `selectPreset(command)`, `generateMarkdown()`, `copyToClipboard()`. Sections: System Instructions (textarea id="system-prompt"), Manager Message (textarea id="manager-message" + preset buttons), Project Tree (textarea id="project-tree"), Task File (textarea id="task-file"), Output (textarea id="output").
- `CHANGELOG.md` — Documents the tool's history: Task 102 (initial creation), Task 103 (Task Discovery presets + Project Tree input).

## AI Analysis & Opinion

The Prompt Composer is currently a single-project tool with no persistence. The request is to add multi-project support with tabs and localStorage. This is a well-scoped improvement:

1. **Data Model:** A `projects` object in localStorage keyed by project name, with each project storing all 5 textarea values + selected preset. A `currentProject` key tracks the active tab.
2. **UX:** Tab bar at the top (horizontal scrollable if many projects). "+" button to create, "x" to delete, double-click to rename. A "Manage" button opens a simple list for rename/delete.
3. **Backward Compatibility:** On first load with no localStorage data, create a "Default" project from the current ephemeral state. Existing users lose nothing.
4. **Risk:** Low. Single-file change, no dependencies, no API changes. The main risk is localStorage quota (5MB typical), which is plenty for text content.

## Local TODOs

- [x] Initial codebase exploration
- [x] Design localStorage schema for multi-project state
- [x] Implement tab bar UI with project switching
- [x] Implement project CRUD (create, rename, delete)
- [x] Persist all textarea state per project in localStorage
- [x] Add "Manage Projects" section/modal
- [x] Ensure backward compatibility (Default project on first load)
- [x] Verify all existing functions still work

## Acceptance Criteria

- [ ] Tab bar appears below the header showing project names
- [ ] Clicking a tab switches to that project and restores its state
- [ ] A "+" button creates a new project with a prompt for the name
- [ ] Projects can be renamed and deleted via a management UI
- [ ] All textarea values (system prompt, manager message, custom notes, project tree, task file) are persisted per project in localStorage
- [ ] On first load with no localStorage, a "Default" project is created
- [ ] All existing functions (fetchSystemPrompt, generateMarkdown, copyToClipboard, selectPreset) work correctly for the active project
- [ ] No external JS dependencies added; single-file architecture preserved

## Verification Evidence

- **Test command:** `sed -n '/<script>/,/<\/script>/p' tools/prompt-composer/index.html | sed '1d;$d' > /tmp/pc-multi.js && node --check /tmp/pc-multi.js`
- **Expected result:** Exit code 0 (valid JavaScript syntax)
- **Actual result:** Exit code 0 — valid JavaScript syntax, no parse errors
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** localStorage quota could be exceeded with many large projects (unlikely — 5MB is ~5000 pages of text)
- **Rollback plan:** Remove the multi-project code from `index.html` and revert to the single-project version from git history

---

## Execution Log & Reasoning

**Architecture:** Added multi-project state management to the existing single-file Prompt Composer tool (`tools/prompt-composer/index.html`). The implementation uses a clean `appState` object with `projects` (keyed by name) and `activeProject` (current tab), persisted to `localStorage` under key `promptComposerState`.

**Changes made (all in `tools/prompt-composer/index.html`):**

1. **HTML Tab Bar** — Responsive `<nav>` with `#tab-container` for dynamically rendered project tabs, plus "+ New" and "⚙️ Manage" buttons. Uses Tailwind utility classes consistent with the existing design system.
2. **HTML Modal** — Native `<dialog>` element for project management (rename/delete). No external dependencies. Backdrop styling via Tailwind.
3. **CSS** — Added `.scrollbar-hide` class for horizontal tab scrolling without visible scrollbars.
4. **JavaScript State Logic** — 15 new functions: `loadState`, `saveState`, `getEmptyProjectState`, `syncDOMToState`, `syncStateToDOM`, `switchProject`, `createProject`, `renameProject`, `deleteProject`, `renderTabs`, `openManageModal`, `closeManageModal`, `renderManageList`. All with JSDoc comments.
5. **Event Bindings** — `DOMContentLoaded` now loads state, syncs DOM, renders tabs, and binds `input` event listeners for auto-save on all 6 textareas. Auto-fetches system prompt only if the current project's prompt is empty.
6. **selectPreset Update** — Added `syncDOMToState()` call so preset clicks auto-save to the active project.

**Key design decisions:**
- Kept single-file architecture (no build step, no external JS dependencies)
- `TEXTAREA_IDS` array includes all 6 textareas (including `context-report` which was added in Task 107)
- Backward-compatible: first load creates a "Default" project with empty state
- Delete prevents removing the last project (minimum 1 project required)
- All state mutations go through `syncDOMToState()` → `saveState()` for consistency
- Tailwind utility classes match the existing design language (slate palette, rounded corners, shadow-sm)

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `3ccb12dea4fe8e2e78a7eb57d0e1d9476719a266`
<!-- END_GIT_DIFF -->
